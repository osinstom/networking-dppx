import json

from oslo_config import cfg
from oslo_log import helpers as log_helpers
from oslo_log import log as logging

from networking_p4.agent.agent import P4AgentDriver
from networking_p4.agent.agent_drivers.bmv2.adaptor.bmv2.runtime_api import MatchType
from networking_p4.agent.agent_drivers.bmv2.adaptor.glance.glance import GlanceClientWrapper
from networking_p4.agent.agent_drivers.bmv2.adaptor.bmv2.bmv2_api import Bmv2Api
from neutron.agent.linux import interface
from neutron.common import utils as common_utils

LOG = logging.getLogger(__name__)

VETH_PREFIX = 'veth-'
TAP_PREFIX = 'tap'


class P4Bmv2AgentDriver(P4AgentDriver):

    def __init__(self):
        self.agent_api = None
        self.ovs_api = None
        self.bmv2_api = Bmv2Api()
        bind_opts = [
            cfg.StrOpt('ovs_use_veth',
                       default=True,
                       help=""),
        ]
        interface_config = cfg.ConfigOpts()
        interface_config.register_opts(bind_opts)
        LOG.info("Loading cfg " + str(interface_config))
        self.ovs_interface = interface.OVSInterfaceDriver(interface_config)
        self.bridge_interface = interface.BridgeInterfaceDriver(interface_config)

    def consume_api(self, agent_api):
        self.agent_api = agent_api

    @log_helpers.log_method_call
    def initialize(self, context):
        self.glance = GlanceClientWrapper()
        self.ovs_api = self.agent_api.request_int_br()
        LOG.info("P4 BMv2 Agent Driver started.")

    def install_module(self, **kwargs):
        self._configure_devices(kwargs['network_id'], kwargs['ports'])
        self.update_switch_pipeline(kwargs['program'])

    def update_module(self, **kwargs):
        self.update_switch_pipeline(kwargs['program'])

    def delete_module(self, **kwargs):
        port_id = kwargs['port_id']
        device_name = self.ovs_api.get_vif_port_by_id(port_id).port_name
        self._unplug_ovs_intf(device_name)
        LOG.info("Port %s has been deleted from OVS bridge" % device_name)

    def _configure_devices(self, network_id, ports):
        for data in ports:
            bmv2_intf = common_utils.get_rand_name(max_length=10, prefix='veth-')
            self._plug_ovs_intf(network_id=network_id,
                                port_id=data['port_id'],
                                intf_name=bmv2_intf,
                                mac_address=data['mac_address'])
            self.bmv2_api.add_port(bmv2_intf)
            LOG.info("Configuring BMv2 P4 switch %s" % (data['port_id']))

    def _plug_ovs_intf(self, network_id=None, **kwargs):
        port_id = kwargs.get('port_id')
        intf_name = kwargs.get('intf_name')
        mac_address = kwargs.get('mac_address')
        self.ovs_interface.plug_new(
            network_id,
            port_id,
            intf_name,
            mac_address,
            bridge=self.ovs_api.br_name,
            prefix=VETH_PREFIX
        )

    def _unplug_ovs_intf(self, intf_name):
        self.ovs_interface.unplug(intf_name, bridge='br-int')

    def _stop_bmv2(self, intf):
        if self.bmv2_api.get_number_of_ports() > 0:
            self.bmv2_api.remove_port(intf)

    def _get_dev_name_from_tap_name(self, tap_name):
        dev_name = tap_name.replace(TAP_PREFIX,
                                    VETH_PREFIX)
        return dev_name

    def update_switch_pipeline(self, pipeline_conf, **kwargs):
        LOG.info("Updating P4 switch pipeline. Image: " + pipeline_conf)
        json = self.glance.download_image(name=pipeline_conf)
        self.bmv2_api.upload_config(str(json))

    def delete_switch_pipeline(self):
        LOG.info("Deleting P4 switch pipeline")

    def add_table_entry(self, table_id, table_entry):
        LOG.info("Adding P4 table entry")
        self.bmv2_api.add_table_entry(action_type=table_entry['type'],
                                      table_id=table_id,
                                      match_keys=table_entry['match_keys'],
                                      action_name=table_entry['action_name'],
                                      action_params=table_entry['action_params'],
                                      priority=table_entry['priority'])

    def delete_table_entry(self, table_id, table_entry):
        LOG.info("Removing P4 table entry")
        self.bmv2_api.delete_table_entry(action_type=table_entry['type'],
                                         table_id=table_id,
                                         match_keys=table_entry['match_keys'],
                                         action_name=table_entry['action_name'],
                                         action_params=table_entry['action_params'],
                                         priority=table_entry['priority'])
        
    def get_table_entries(self, **kwargs):
        LOG.info("Getting P4 table entries")
        entries = None
        if kwargs['table_name']:
            entries = self.bmv2_api.get_entries_from_table(kwargs['table_name'])
        else:
            raise Exception()
        return self._make_entries_payload(entries)

    def _make_entries_payload(self, entries):
        payload = dict(entries=[])
        for e in entries:
            LOG.info("EntryHandle: %s" % e.entry_handle)
            LOG.info("Priority: %s" % e.options.priority)
            LOG.info("MatchKey: %s" % e.match_key)
            LOG.info("ActionEntry: %s" % e.action_entry)
            entry_obj = dict(id=e.entry_handle,
                             match_key=self._get_match_keys(e.match_key),
                             action_name=self._get_action_name(e.action_entry),
                             action_data=self._get_action_data(e.action_entry),
                             priority=e.options.priority)
            payload['entries'].append(entry_obj)
        return json.dumps(payload, ensure_ascii=False)

    def _get_match_keys(self, match_key):

        def hexstr(v):
            return "".join("{:02x}".format(ord(c)) for c in v)
        def dump_exact(p):
             return hexstr(p.exact.key)
        def dump_lpm(p):
            return "{}/{}".format(p.lpm.key, p.lpm.prefix_length)
        def dump_ternary(p):
            return "{} &&& {}".format(p.ternary.key,
                                      p.ternary.mask)
        def dump_range(p):
            return "{} -> {}".format(p.range.start,
                                     p.range.end_)
        def dump_valid(p):
            return "01" if p.valid.key else "00"
        pdumpers = {"exact": dump_exact, "lpm": dump_lpm,
                    "ternary": dump_ternary, "valid": dump_valid,
                    "range": dump_range}

        match_keys = []
        for m in match_key:
            dumper = pdumpers[MatchType.to_str(m.type)]
            match = dumper(m)
            match_keys.append(match)
        return match_keys

    def _get_action_name(self, action_entry):
        return action_entry.action_name

    def _get_action_data(self, action_entry):
        action_data = action_entry.action_data
        action_str = "{}".format(
            ", ".join([a for a in action_data]))
        return action_str

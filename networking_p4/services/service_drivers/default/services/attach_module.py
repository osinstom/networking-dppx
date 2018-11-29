from networking_p4.services.common.exceptions import VmIpNotFound
from networking_p4.services.service_drivers.default.services.abstract import AbstractService
from networking_p4.services.service_drivers.default.services.utils import *
from oslo_log import log as logging
import db_helper


LOG = logging.getLogger(__name__)

TRAFFIC_DIRECTION_BIDIRECTIONAL = 'bidirectional'
TRAFFIC_DIRECTION_INCOMING = 'incoming'
TRAFFIC_DIRECTION_OUTGOING = 'outgoing'


class AttachModuleService(AbstractService):

    def __init__(self, rpc_client):
        super(AttachModuleService, self).__init__(rpc_client)

    def handle(self, context):

        port_pair_groups = list()

        port_pair_groups.append(
            self._create_port_pair_group_for_module(context._plugin_context, context.module_context)
        )
        port_pair_groups.extend(
            self._create_port_pair_groups_for_vms(context)
        )

        traffic_type = context.additional_context['type']

        self.setup_chain_for_outgoing_traffic(context, port_pair_groups)

        # TODO: only outgoing traffic is supported
        # if traffic_type is TRAFFIC_DIRECTION_INCOMING or TRAFFIC_DIRECTION_BIDIRECTIONAL:
        #     self.setup_chain_for_incoming_traffic(context, port_pair_groups)
        #
        # if traffic_type is TRAFFIC_DIRECTION_OUTGOING or TRAFFIC_DIRECTION_BIDIRECTIONAL:
        #     self.setup_chain_for_outgoing_traffic(context, port_pair_groups)

    def setup_chain_for_incoming_traffic(self, context, port_pair_groups):
        src_ip = context.additional_context['flow_filter']['source_ip_prefix']
        dst_ip = context.additional_context['flow_filter']['destination_ip_prefix']
        flow_classifier = self.create_flow_classifier_for_module(context,
                                                                 src_ip=dst_ip,
                                                                 dst_ip=src_ip)
        self.create_port_chain(context, flow_classifier, port_pair_groups)

    def setup_chain_for_outgoing_traffic(self, context, port_pair_groups):
        src_ip = context.additional_context['flow_filter']['source_ip_prefix']
        dst_ip = context.additional_context['flow_filter']['destination_ip_prefix']
        flow_classifier = self.create_flow_classifier_for_module(context,
                                                                 src_ip=src_ip,
                                                                 dst_ip=dst_ip)
        self.create_port_chain(context, flow_classifier, port_pair_groups)

    def create_flow_classifier_for_module(self, context, src_ip, dst_ip):
        flow_classifier_data = self._prepare_flow_classifier_data(context,
                                                                  src_ip,
                                                                  dst_ip)
        flow_classifier = self._sfc_fc_plugin.create_flow_classifier(context._plugin_context,
                                                                     {'flow_classifier': flow_classifier_data})
        LOG.info("FlowClassifier created. ID=" + flow_classifier['id'])
        return flow_classifier

    def create_port_chain(self, context, flow_classifier, port_pair_groups):
        port_chain_data = prepare_port_chain_data(context.module_context['id'], flow_classifier, port_pair_groups,
                                                        context.additional_context['type'])
        port_chain = self._sfc_plugin.create_port_chain(context._plugin_context, {'port_chain': port_chain_data})
        LOG.info("PortChain created. ID=" + port_chain['id'])

    def _prepare_flow_classifier_data(self, context, src_ip_prefix, dst_ip_prefix):
        flow_filter = context.additional_context['flow_filter']
        return {"name": "",
                "project_id": context.module_context['project_id'],
                "description": "",
                "protocol": flow_filter['protocol'].lower() if flow_filter['protocol'] is not None else "",
                "source_port_range_min": None,
                "source_port_range_max": None,
                "destination_port_range_min": None,
                "destination_port_range_max": None,
                "source_ip_prefix": None,
                "destination_ip_prefix": dst_ip_prefix,
                "l7_parameters": {},
                "ethertype": "IPv4",
                "logical_destination_port": None,
                "logical_source_port": self._get_logical_port_by_ip_prefix(context, src_ip_prefix)['id']
        }

    def _get_port_pair_group_for_module(self, plugin_context, module_id):
        module_service_chain_association = db_helper.get_module_service_association(plugin_context, module_id)
        ppg_id = module_service_chain_association.port_pair_group_id
        port_pair_group = self._sfc_plugin.get_port_pair_group(plugin_context, ppg_id)
        return port_pair_group

    def _create_port_pair_group_for_module(self, _plugin_context, module_ctx):
        filters = {'name': ['sfc'],
                   'device_owner': [DEVICE_OWNER_P4],
                   'device_id': [module_ctx['id']]}
        ports = self._core_plugin.get_ports(_plugin_context, filters=filters)
        if ports:
            sfc_port = ports[0]
        else:
            raise Exception
        port_pair_data = prepare_port_pair_data(module_ctx['name'], sfc_port)
        port_pair = self._sfc_plugin.create_port_pair(_plugin_context,
                                                      {'port_pair': port_pair_data})
        LOG.info("Port Pair created. ID=" + port_pair['id'])
        ppg_data = prepare_port_pair_group_data(port_pair)
        port_pair_group = self._sfc_plugin.create_port_pair_group(_plugin_context,
                                                                  {'port_pair_group': ppg_data})
        LOG.info("Port Pair Group created. ID=" + port_pair_group['id'])
        db_helper.store_ppg_id(_plugin_context, module_ctx['id'], port_pair_group['id'])
        return port_pair_group

    def _create_port_pair_groups_for_vms(self, context):
        port_pair_groups = []
        for ip in context.additional_context['chain_with']:
            port = self._get_logical_port_by_ip_prefix(context, ip)
            port_pair_data = prepare_port_pair_data(ip, port)
            port_pair = self._sfc_plugin.create_port_pair(context._plugin_context,
                                                          {'port_pair': port_pair_data})
            ppg_data = prepare_port_pair_group_data(port_pair)
            port_pair_group = self._sfc_plugin.create_port_pair_group(context._plugin_context,
                                                                      {'port_pair_group': ppg_data})
            port_pair_groups.append(port_pair_group)
        return port_pair_groups

    def _get_logical_port_by_ip_prefix(self, context, ip_prefix):
        ip = ip_prefix.split('/')[0]
        filters = {'fixed_ips': {'ip_address': [ip]}}
        LOG.info("Getting ports with filter: " + str(filters))
        ports = self._core_plugin.get_ports(context._plugin_context, filters=filters)
        LOG.info("Ports: " + str(ports))
        if ports:
            return ports[0]
        else:
            raise VmIpNotFound()


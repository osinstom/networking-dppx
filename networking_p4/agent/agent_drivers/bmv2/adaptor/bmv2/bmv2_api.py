import sys
import time
import logging
import os

if os.name == 'nt':
    from neutron.agent.windows import utils as exc_utils
else:
    from neutron.agent.linux import utils as exc_utils

from runtime_CLI import ResType

import networking_p4.agent.agent_drivers.bmv2.adaptor.bmv2.runtime_api
from bm_runtime.standard.Standard import *
from networking_p4.agent.agent_drivers.bmv2.adaptor.bmv2.runtime_api import parse_match_key

LOG = logging.getLogger(__name__)

ACTION_TYPE_DEFAULT = 'default'
ACTION_TYPE_RUNTIME = 'runtime'

BMv2_PORT = 9090


class Bmv2Api(object):

    def _get_bmv2_api(self):
        return networking_p4.agent.agent_drivers.bmv2.adaptor.bmv2.runtime_api.get_api(BMv2_PORT)

    def _get_bmv2_client(self):
        return self._get_bmv2_api().client

    def add_port(self, iface_name):
        port_num = self._get_port_num_from_pool()
        self._get_bmv2_client().bm_dev_mgr_add_port(iface_name, port_num, "")

    def _get_port_num_from_pool(self):
        ports_int = []
        for port_info in self._get_bmv2_client().bm_dev_mgr_show_ports():
            ports_int.append(int(port_info.port_num))
        ports_int.sort()
        size = len(ports_int)
        last_port_num = size + 1
        return last_port_num

    def get_number_of_ports(self):
        return len(self._get_bmv2_client().bm_dev_mgr_show_ports())

    def _clean_ports(self):
        ports = self._get_bmv2_client().bm_dev_mgr_show_ports()
        for port_info in ports:
            self._get_bmv2_client().bm_dev_mgr_remove_port(port_info.port_num)

    def remove_port(self, iface_name):
        port_num = self._get_port_num_by_name(iface_name)
        self._get_bmv2_client().bm_dev_mgr_remove_port(port_num)

    def _get_port_num_by_name(self, iface_name):
        port_num = None
        ports = self._get_bmv2_client().bm_dev_mgr_show_ports()
        for port_info in ports:
            if port_info.iface_name == iface_name:
                port_num = port_info.port_num
                break
        return port_num

    def run(self, intf):
        cmd = ['sudo', 'simple_switch', '-i', intf, '--thrift-port',
               '10811', '--no-p4',
               '--', '--enable-swap']
        exc_utils.execute(cmd, run_as_root=True, log_fail_as_error=True)

    def create_instance(self, intf):
        intf_def = "1@" + intf

        self.run(intf_def)

        time.sleep(3)

        LOG.info("BMv2 instance created. " + str(self.get_config()))

    def delete_instance(self):
        pass

    def get_config(self):
        return self._get_bmv2_client().bm_get_config()

    def upload_config(self, json_conf):
        try:
            self._get_bmv2_client().bm_load_new_config(json_conf)
        except InvalidSwapOperation as e:
            if e.code == SwapOperationErrorCode.ONGOING_SWAP:
                LOG.warning("P4Agent tries to load new config during swap ongoing. "
                            "Swapping configs and retrying..")
                self._get_bmv2_client().bm_swap_configs()
                self.upload_config(json_conf)
        try:
            self._get_bmv2_client().bm_swap_configs()
        except InvalidSwapOperation as e:
            if e.code == SwapOperationErrorCode.NO_ONGOING_SWAP:
                pass
            else:
                raise e

    def table_set_default_entry(self, table_name, action_name, action_entry):
        self._get_bmv2_client().bm_mt_set_default_action(0, table_name, action_name, action_entry)

    def table_set_runtime_entry(self, table_name, match_keys, action_name, action_entry, priority):
        # get object representing P4 Table
        table = self._get_bmv2_api().get_res("table", table_name, ResType.table)
        # get object representing P4 Action
        action = table.get_action(action_name)

        # parse arrays to Thrift-friendly objects
        match_obj = parse_match_key(table, match_keys)
        action_obj = self._get_bmv2_api().parse_runtime_data(action, action_entry)

        LOG.info("Adding table entry.. %s %s %s" % (table.name, str(match_obj), str(action_obj)))

        entry = None

        # check if entry with match key exists
        try:
            entry = self._get_bmv2_client().bm_mt_get_entry_from_key(
                0, table.name, match_obj, BmAddEntryOptions(priority=priority))
        except InvalidTableOperation as e:
            if e.code == TableOperationErrorCode.BAD_MATCH_KEY:
                # it means there is no entry for match key
                pass

        if entry:
            # modify existing entry
            self._get_bmv2_client().bm_mt_modify_entry(
                0, table.name, entry.entry_handle, action.name, action_obj
            )
            LOG.debug("Entry {} has been modified with action {} {}".format(str(match_keys), action_name,
                                                                            str(action_entry)))
        else:
            # adding new entry
            self._get_bmv2_client().bm_mt_add_entry(
                0, table_name, match_obj, action.name, action_obj,
                BmAddEntryOptions(priority=priority)
            )
            LOG.debug("Entry {} has been added with action {} {}".format(str(match_keys), action_name,
                                                                         str(action_entry)))

    def add_table_entry(self, **kwargs):
        action_type = kwargs['action_type']
        table_name = kwargs['table_id']
        action_name = kwargs['action_name']
        action_entry = kwargs['action_params']
        if action_type == ACTION_TYPE_DEFAULT:
            self.table_set_default_entry(table_name, action_name, action_entry)
        elif action_type == ACTION_TYPE_RUNTIME:
            match_keys = kwargs['match_keys']
            priority = kwargs['priority'] if kwargs['priority'] else 0
            self.table_set_runtime_entry(table_name, match_keys, action_name, action_entry, priority)

    def delete_table_entry(self, **kwargs):
        action_type = kwargs['action_type']
        table_name = kwargs['table_id']
        action_name = kwargs['action_name']
        action_entry = kwargs['action_params']
        match_keys = kwargs['match_keys']
        priority = kwargs['priority'] if kwargs['priority'] else 0

        table = self._get_bmv2_api().get_res("table", table_name, ResType.table)
        match_obj = parse_match_key(table, match_keys)

        entry = self._get_bmv2_client().bm_mt_get_entry_from_key(
                0, table.name, match_obj, BmAddEntryOptions(priority=priority))

        self._get_bmv2_client().bm_mt_delete_entry(0, table.name, entry.entry_handle)

    def get_entries_from_table(self, table_name):
        table = self._get_bmv2_api().get_res("table", table_name, ResType.table)
        return self._get_bmv2_client().bm_mt_get_entries(0, table.name)

    def get_all_table_entries(self):
        pass

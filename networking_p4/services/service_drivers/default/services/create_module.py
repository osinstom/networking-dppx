from networking_p4.services.service_drivers.default.services.abstract import AbstractService
from networking_p4.services.service_drivers.default.services.utils import *
from neutron.plugins.common import utils as neutron_utils
from oslo_log import log as logging
from oslo_utils import excutils
import db_helper

LOG = logging.getLogger(__name__)


class CreateModuleService(AbstractService):

    def __init__(self, rpc_client):
        super(CreateModuleService, self).__init__(rpc_client)

    def handle(self, context):
        current_ctx = context.current

        sfc_port_data = prepare_port_data(current_ctx, name='sfc')
        normal_port_data = prepare_port_data(current_ctx, name='normal')
        sfc_port = neutron_utils.create_port(self._core_plugin, context._plugin_context, {'port': sfc_port_data})
        LOG.info("Creating P4 port completed. ID= " + sfc_port['id'])
        normal_port = neutron_utils.create_port(self._core_plugin, context._plugin_context, {'port': normal_port_data})
        LOG.info("Creating P4 port completed. ID= " + normal_port['id'])
        program = current_ctx['program']

        with neutron_utils.delete_port_on_error(self._core_plugin,
                                                context._plugin_context, normal_port['id']):
            with neutron_utils.delete_port_on_error(self._core_plugin,
                                                    context._plugin_context, sfc_port['id']):
                ports_data = self._prepare_port_data(sfc_port, normal_port)
                self.rpc_client.ask_agent_to_install_data_plane_module(self.rpc_ctx,
                                                                       network_id=normal_port_data['network_id'],
                                                                       ports=ports_data,
                                                                       program=program)

    @staticmethod
    def _prepare_port_data(sfc_port, normal_port):
        return [
                {
                    'number': 1,
                    'port_id': sfc_port['id'],
                    'mac_address': sfc_port['mac_address']
                },
                {
                    'number': 2,
                    'port_id': normal_port['id'],
                    'mac_address': normal_port['mac_address']
                }
        ]

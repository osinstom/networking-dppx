from networking_p4.services.service_drivers.default.services.abstract import AbstractService

from oslo_log import log as logging
import db_helper

LOG = logging.getLogger(__name__)


class DeleteModuleService(AbstractService):

    def __init__(self, rpc_client):
        super(DeleteModuleService, self).__init__(rpc_client)

    def handle(self, context):
        current_ctx = context.current
        plugin_ctx = context._plugin_context
        module_id = current_ctx['id']

        module_ports = self._get_module_ports(context, module_id)

        for port in module_ports:
            self.delete_dataplane_module(port['id'])
            self.delete_neutron_port(plugin_ctx, port['id'])
            LOG.info("Neutron Port (%s) created for P4 module has been deleted.", port['id'])

    def _get_module_ports(self, context, module_id):
        filter = {'device_id': [module_id]}
        return self._core_plugin.get_ports(context._plugin_context, filters=filter)

    def delete_neutron_port(self, plugin_ctx, port_id):
        self._core_plugin.delete_port(plugin_ctx, port_id)

    def delete_dataplane_module(self, port_id):
        self.rpc_client.ask_agent_to_delete_dataplane_module(self.rpc_ctx,
                                                             port_id=port_id)





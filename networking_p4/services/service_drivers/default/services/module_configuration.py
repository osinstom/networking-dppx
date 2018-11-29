from networking_p4.services.service_drivers.default.services.abstract import AbstractService


class GetModuleConfigurationService(AbstractService):

    def __init__(self, rpc_client):
        super(GetModuleConfigurationService, self).__init__(rpc_client)

    def handle(self, context):
        configuration = self.rpc_client.ask_agent_to_get_table_entries(self.rpc_ctx)
        return configuration

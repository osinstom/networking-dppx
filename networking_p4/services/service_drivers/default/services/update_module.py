from networking_p4.services.service_drivers.default.services.abstract import AbstractService


class UpdateModuleService(AbstractService):

    def __init__(self, rpc_client):
        super(UpdateModuleService, self).__init__(rpc_client)

    def handle(self, context):
        image = context.current['program']
        self.rpc_client.ask_agent_to_update_data_plane_module(self.rpc_ctx,
                                                               program=image)

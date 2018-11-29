from networking_p4.services.service_drivers.default.services.abstract import AbstractService
from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class UnconfigureModuleService(AbstractService):

    def __init__(self, rpc_client):
        super(UnconfigureModuleService, self).__init__(rpc_client)

    def handle(self, context):
        configuration = context.additional_context

        LOG.info("Handling ConfigureModule")
        LOG.info("Config: " + str(configuration['flow_rules']))
        for flow_rule in configuration['flow_rules']:
            table_id = flow_rule['table_id']
            table_entry = flow_rule['entry']
            self.rpc_client.ask_agent_to_delete_table_entry(self.rpc_ctx, table_id=table_id, table_entry=table_entry)

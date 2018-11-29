from networking_p4.services.service_drivers.default.services.attach_module import AttachModuleService
from networking_p4.services.service_drivers.default.services.configure_module import ConfigureModuleService
from networking_p4.services.service_drivers.default.services.create_module import CreateModuleService
from networking_p4.services.service_drivers.default.services.delete_module import DeleteModuleService
from networking_p4.services.service_drivers.default.services.detach_module import DetachModuleService
from networking_p4.services.service_drivers.default.services.module_configuration import GetModuleConfigurationService
from networking_p4.services.service_drivers.default.services.unconfigure_module import UnconfigureModuleService
from networking_p4.services.service_drivers.default.services.update_module import UpdateModuleService
from networking_p4.services.service_drivers.driver_api import P4DriverApi, P4DriverBase
from oslo_log import log as logging
from networking_p4.services.service_drivers.default import rpc as p4_rpc
from networking_p4.services.common import rpc_topics
from neutron_lib import context as n_context
import neutron.common.rpc as n_rpc

LOG = logging.getLogger(__name__)


class DefaultP4Driver(P4DriverApi,
                      P4DriverBase):
    """ Implementation of default driver for P4 service """

    def __init__(self):
        LOG.info("DefaultP4Driver started.")
        self.rpc_client = None
        self.rpc_ctx = None
        self.callbacks = dict()

    def initialize(self):
        # super(DefaultP4Driver, self).initialize()
        LOG.info("DefaultP4Driver started.")
        self.rpc_client = p4_rpc.P4AgentRpcClient(
            rpc_topics.P4_AGENT
        )
        self.rpc_ctx = n_context.get_admin_context()
        self._setup_rpc()

        # initialize services
        self.create_module_svc = CreateModuleService(self.rpc_client)
        self.update_module_svc = UpdateModuleService(self.rpc_client)
        self.delete_module_svc = DeleteModuleService(self.rpc_client)
        self.attach_module_svc = AttachModuleService(self.rpc_client)
        self.detach_module_svc = DetachModuleService(self.rpc_client)
        self.configure_module_svc = ConfigureModuleService(self.rpc_client)
        self.unconfigure_module_svc = UnconfigureModuleService(self.rpc_client)
        self.get_module_configuration_svc = GetModuleConfigurationService(self.rpc_client)

    def add_callback(self, topic, callback):
        self.callbacks[topic] = callback

    def _setup_rpc(self):
        # Setup a rpc server
        self.topic = rpc_topics.P4_PLUGIN
        self.endpoints = [p4_rpc.P4RpcCallback(self)]
        self.conn = n_rpc.create_connection()
        self.conn.create_consumer(self.topic, self.endpoints, fanout=False)
        self.conn.consume_in_threads()

    def create_module(self, context):
        LOG.info("DefaultDriver: Creating P4 module")
        self.create_module_svc.handle(context)

    def update_module(self, context):
        LOG.info("DefaultDriver: Updating program")
        self.update_module_svc.handle(context)

    def delete_module(self, context):
        LOG.info("DefaultDriver: Deleting P4 module")
        self.delete_module_svc.handle(context)

    def attach_module(self, context):
        LOG.info("DefaultDriver: Attaching P4 module")
        self.attach_module_svc.handle(context)

    def detach_module(self, context):
        LOG.info("DefaultDriver: Detaching P4 module")
        self.detach_module_svc.handle(context)

    def configure_module(self, context):
        LOG.info("DefaultDriver: Configuring P4 module")
        self.configure_module_svc.handle(context)

    def unconfigure_module(self, context):
        LOG.info("DefaultDriver: Unconfiguring P4 module")
        self.unconfigure_module_svc.handle(context)

    def get_module_configuration(self, context):
        LOG.info("DefaultDriver: Get P4 module configuration")
        return self.get_module_configuration_svc.handle(context)


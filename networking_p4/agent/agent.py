from abc import ABCMeta
from abc import abstractmethod

import oslo_messaging
import six

from oslo_config import cfg
from oslo_log import helpers as log_helpers
from oslo_log import log as logging
from oslo_context import context as oslo_ctxt
from neutron_lib.agent import l2_extension

from networking_p4.services.common import rpc_topics
from networking_p4.services.common import constants as p4_constants
from neutron import manager
from neutron_lib import context as n_context
from neutron.agent import rpc as agent_rpc
from neutron.common import rpc as n_rpc
from neutron.common import topics

LOG = logging.getLogger(__name__)


class P4PluginRpcClient(object):

    def __init__(self, topic, host):
        self.target = oslo_messaging.Target(topic=topic, version='1.0')
        self.client = n_rpc.get_client(self.target)

    def update_switch_pipeline_status(self, context, status):
        cctxt = self.client.prepare()
        LOG.info("Returning status")
        return cctxt.call(
            context,
            'update_switch_pipeline_status',
            p4_switch_info=status)


class P4AgentDriver(object):
    """Defines abstract interface for P4 Agent Driver."""

    @abstractmethod
    def initialize(self, context):
        """Perform P4 agent driver initialization."""

    @abstractmethod
    def consume_api(self, agent_api):
        """Consume the AgentAPI instance from the P4AgentExtension class

        :param agent_api: An instance of an agent specific API
        """

    @abstractmethod
    def install_module(self, **kwargs):
        """ Install P4 module into a programmable switch """
        pass

    @abstractmethod
    def update_module(self, **kwargs):
        """ Update P4 module """
        pass

    @abstractmethod
    def delete_module(self, **kwargs):
        pass

    @abstractmethod
    def add_table_entry(self, table_id, table_entry):
        """Add a table entry to existing table of switch"""

    @abstractmethod
    def delete_table_entry(self, table_id, table_entry):
        """Remove a table entry from existing table of switch"""

    @abstractmethod
    def get_table_entries(self, **kwargs):
        pass


class P4AgentExtension(l2_extension.L2AgentExtension):

    def __init__(self):
        self.host = cfg.CONF.host
        self.agent_driver = None
        self.agent_id = "p4-agent-" + self.host
        self.rpc_ctx = None

    @log_helpers.log_method_call
    def initialize(self, connection, driver_type):
        """Initialize agent extension."""
        LOG.info("P4 Agent starting.")
        self.agent_driver = manager.NeutronManager.load_class_for_provider(
            'networking_p4.p4.agent_drivers', 'bmv2')()  # TODO: driver_type is hardcoded
        self.agent_driver.consume_api(self.agent_api)
        self.rpc_ctx = n_context.get_admin_context_without_session()
        self.agent_driver.initialize(self.rpc_ctx)
        LOG.info("P4 BMv2 started")

        self._setup_rpc()

    @log_helpers.log_method_call
    def consume_api(self, agent_api):
        """Receive neutron agent API object

        Allows an extension to gain access to resources internal to the
        neutron agent and otherwise unavailable to the extension.
        """
        self.agent_api = agent_api

    @log_helpers.log_method_call
    def handle_port(self, context, data):
        pass

    @log_helpers.log_method_call
    def delete_port(self, context, data):
        pass

    @log_helpers.log_method_call
    def install_module(self, context, **kwargs):
        self.agent_driver.install_module(**kwargs)

    @log_helpers.log_method_call
    def update_module(self, context, **kwargs):
        self.agent_driver.update_module(**kwargs)

    @log_helpers.log_method_call
    def delete_module(self, context, **kwargs):
        self.agent_driver.delete_module(**kwargs)

    @log_helpers.log_method_call
    def add_table_entry(self, context, **kwargs):
        table_id = kwargs['table_id']
        table_entry = kwargs['table_entry']
        self.agent_driver.add_table_entry(table_id, table_entry)

    @log_helpers.log_method_call
    def delete_table_entry(self, context, **kwargs):
        table_id = kwargs['table_id']
        table_entry = kwargs['table_entry']
        self.agent_driver.delete_table_entry(table_id, table_entry)

    @log_helpers.log_method_call
    def get_table_entries(self, context, **kwargs):
        return self.agent_driver.get_table_entries(**kwargs)

    def _setup_rpc(self):
        LOG.debug("Setup RPC")
        self.p4_plugin_rpc_client = P4PluginRpcClient(
            rpc_topics.P4_PLUGIN,
            cfg.CONF.host)

        self.topic = rpc_topics.P4_AGENT

        self.endpoints = [self]

        consumers = [
            [rpc_topics.P4MODULE, topics.CREATE],
            [rpc_topics.P4MODULE, topics.UPDATE],
            [rpc_topics.P4MODULE, topics.DELETE],
            [rpc_topics.CONFIGURATION, topics.CREATE],
            [rpc_topics.CONFIGURATION, topics.UPDATE],
            [rpc_topics.CONFIGURATION, topics.DELETE],
            [rpc_topics.CONFIGURATION, None]
        ]

        # subscribing P4 Agent RPC client and topics
        self.connection = agent_rpc.create_consumers(
            self.endpoints,
            self.topic,
            consumers)
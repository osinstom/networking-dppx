import oslo_messaging
from oslo_log import log as logging
from neutron.common import rpc as n_rpc
from neutron.common import topics
from networking_p4.services.common import rpc_topics

LOG = logging.getLogger(__name__)


class P4RpcCallback(object):
    """P4 RPC server."""

    def __init__(self, driver):
        self.target = oslo_messaging.Target(version='1.0')
        self.driver = driver


class P4AgentRpcClient(object):

    def __init__(self, topic=rpc_topics.P4_AGENT):
        self.topic = topic
        self.target = oslo_messaging.Target(topic=topic, version='1.0')
        self.client = n_rpc.get_client(self.target)

    def ask_agent_to_install_data_plane_module(self, context, **kwargs):
        LOG.info('Ask agent on the specific host to install data plane module')
        cctxt = self.client.prepare(
            topic=topics.get_topic_name(
                self.topic, rpc_topics.P4MODULE, topics.CREATE))
        cctxt.call(context,
                   'install_module',
                   network_id=kwargs['network_id'],
                   ports=kwargs['ports'],
                   program=kwargs['program'])

    def ask_agent_to_update_data_plane_module(self, context, **kwargs):
        LOG.info('Ask agent on the specific host to update data plane module')
        cctxt = self.client.prepare(
            topic=topics.get_topic_name(
                self.topic, rpc_topics.P4MODULE, topics.UPDATE))
        cctxt.call(context,
                   'update_module',
                   module_id='',
                   program=kwargs['program'])

    def ask_agent_to_delete_dataplane_module(self, context, **kwargs):
        LOG.info('Ask agent on the specific host to delete P4 program')
        cctxt = self.client.prepare(
            topic=topics.get_topic_name(
                self.topic, rpc_topics.P4MODULE, topics.DELETE))
        cctxt.call(context,
                   'delete_module',
                   port_id=kwargs['port_id'])

    def ask_agent_to_add_table_entry(self, context, **kwargs):
        LOG.info('Ask agent on the specific host to add a table entry to specific P4 table')
        table_id = kwargs['table_id']
        table_entry = kwargs['table_entry']
        cctxt = self.client.prepare(
            topic=topics.get_topic_name(
                self.topic, rpc_topics.CONFIGURATION, topics.UPDATE))
        cctxt.call(context, 'add_table_entry', table_id=table_id, table_entry=table_entry)

    def ask_agent_to_delete_table_entry(self, context, **kwargs):
        LOG.info('Ask agent on the specific host to delete a table entry from specific P4 table')
        table_id = kwargs['table_id']
        table_entry = kwargs['table_entry']
        cctxt = self.client.prepare(
            topic=topics.get_topic_name(
                self.topic, rpc_topics.CONFIGURATION, topics.DELETE))
        cctxt.call(context, 'delete_table_entry', table_id=table_id, table_entry=table_entry)

    def ask_agent_to_get_table_entries(self, context, **kwargs):
        LOG.info('Ask agent on the specific host to get table entries from specific P4 table')
        cctxt = self.client.prepare(
            topic=topics.get_topic_name(
                self.topic, rpc_topics.CONFIGURATION, None))
        return cctxt.call(context, 'get_table_entries', table_name='tester')

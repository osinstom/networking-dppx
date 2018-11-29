from networking_p4.services.service_drivers.default.services.abstract import AbstractService
from oslo_log import log as logging
import db_helper


LOG = logging.getLogger(__name__)


class DetachModuleService(AbstractService):

    def __init__(self, rpc_client):
        super(DetachModuleService, self).__init__(rpc_client)

    def handle(self, context):
        plugin_ctx = context._plugin_context
        port_pair_group = self._get_port_pair_group_for_module(plugin_ctx, context.module_context['id'])

        port_chain = self._get_port_chain_by_module_id(plugin_ctx, context.module_context['id'])
        flow_classifiers = None
        port_pair_groups = None
        port_pairs = None
        if port_chain:
            port_pair_groups = port_chain['port_pair_groups']
            flow_classifiers = port_chain['flow_classifiers']
            self.delete_port_chain(plugin_ctx, port_chain)

        if flow_classifiers:
            self.delete_flow_classifiers(plugin_ctx, flow_classifiers)

        if port_pair_groups:
            port_pairs = self.get_port_pairs_for_port_pair_groups(plugin_ctx, port_pair_groups)
            self.delete_port_pair_groups(plugin_ctx, port_pair_groups)

        if port_pairs:
            self.delete_port_pairs(plugin_ctx, port_pairs)

        self._delete_module_service_association(plugin_ctx, context.module_context['id'], port_pair_group['id'])

    def delete_port_chain(self, plugin_context, port_chain):
        self._sfc_plugin.delete_port_chain(plugin_context, port_chain['id'])
        LOG.info("Port Chain %(port_chain)s has been deleted.", {'port_chain': port_chain['id']})

    def _get_port_pair_group_for_module(self, plugin_context, module_id):
        module_service_chain_association = db_helper.get_module_service_association(plugin_context,
                                                                                    module_id)
        ppg_id = module_service_chain_association.port_pair_group_id
        port_pair_group = self._sfc_plugin.get_port_pair_group(plugin_context, ppg_id)
        return port_pair_group

    @staticmethod
    def _get_flow_classifier_by_port_chain_id(plugin_context, port_chain_id):
        return db_helper.get_flow_classifier_by_port_chain_id(plugin_context, port_chain_id)

    @staticmethod
    def _get_port_chain_by_port_pair_group(plugin_context, ppg_id):
        return db_helper.get_port_chain_by_ppg_id(plugin_context, ppg_id)

    def delete_flow_classifiers(self, plugin_ctx, flow_classifiers):
        for fc in flow_classifiers:
            self._sfc_fc_plugin.delete_flow_classifier(plugin_ctx, fc)
            LOG.info("Flow Classifier %(flow_classifier)s has been deleted.",
                    {'flow_classifier': fc})

    def _delete_module_service_association(self, plugin_ctx, module_id, portpairgroup_id):
        db_helper.delete_module_service_association(plugin_ctx, module_id, portpairgroup_id)

    def get_port_pairs_for_port_pair_groups(self, plugin_ctx, port_pair_groups):
        port_pairs = list()
        for ppg in port_pair_groups:
            port_pair_group = self._sfc_plugin.get_port_pair_group(plugin_ctx, ppg)
            port_pairs.extend(port_pair_group['port_pairs'])
        return port_pairs

    def delete_port_pair_groups(self, plugin_ctx, port_pair_groups):
        for ppg in port_pair_groups:
            self._sfc_plugin.delete_port_pair_group(plugin_ctx, ppg)
            LOG.info("Port Pair Group (%s) deleted.", ppg)

    def delete_port_pairs(self, plugin_ctx, port_pairs):
        for pp in port_pairs:
            self._sfc_plugin.delete_port_pair(plugin_ctx, pp)
            LOG.info("Port Pair (%s) deleted.", pp)

    def _get_port_chain_by_module_id(self, plugin_ctx, module_id):
        name = "PC_FOR_" + module_id
        filter = dict(name=[name])
        chains = self._sfc_plugin.get_port_chains(plugin_ctx, filters=filter)
        if chains:
            return chains[0]

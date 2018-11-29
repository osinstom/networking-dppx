from abc import abstractmethod

from neutron_lib.plugins import directory
from neutron_lib import context as n_context


class AbstractService(object):

    def __init__(self, rpc_client):
        self.rpc_client = rpc_client
        self.rpc_ctx = n_context.get_admin_context()

    @property
    def _core_plugin(self):
        return directory.get_plugin()

    @property
    def _sfc_plugin(self):
        return directory.get_plugin(alias="sfc")

    @property
    def _sfc_fc_plugin(self):
        return directory.get_plugin(alias="flow_classifier")

    @abstractmethod
    def handle(self, context):
        pass

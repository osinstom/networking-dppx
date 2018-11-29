from neutronclient.common import extension
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronv20

P4_MODULE_RESOURCE = 'module'


class P4Module(extension.NeutronClientExtension):
    resource = P4_MODULE_RESOURCE
    resource_plural = '%ss' % resource
    object_path = '/p4/%s' % resource_plural
    resource_path = '/p4/%s/%%s' % resource_plural
    versions = ['2.0']


class P4ModuleCreate(extension.ClientExtensionCreate, P4Module):

    shell_command = 'module-create'

    def add_known_arguments(self, parser):
        pass

    def args2body(self, parsed_args):
        body = {}
        client = self.get_client()
        pass


class P4ModuleDelete(extension.ClientExtensionDelete, P4Module):

    shell_command = 'module-delete'


class P4ModuleList(extension.ClientExtensionList, P4Module):

    shell_command = 'module-list'
    list_columns = ['id', 'name', 'network_id', 'program', 'description']
    pagination_support = True
    sorting_support = True


class P4ModuleShow(extension.ClientExtensionShow, P4Module):

    shell_command = 'module-show'




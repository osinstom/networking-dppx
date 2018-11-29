from abc import ABCMeta
from abc import abstractmethod
from oslo_config import cfg
from oslo_log import log as logging
import six

from neutron.api import extensions as neutron_ext
from neutron.api.v2 import resource_helper
from neutron_lib.api import extensions
from neutron_lib import exceptions as neutron_exc
from neutron_lib.db import constants as db_const
from neutron_lib.services import base as libbase

from networking_p4 import extensions as pdp_extensions

LOG = logging.getLogger(__name__)

cfg.CONF.import_opt('api_extensions_path', 'neutron.common.config')
neutron_ext.append_api_extensions_path(pdp_extensions.__path__)

p4_quota_opts = [

]

P4_EXT = 'p4'
P4_PREFIX = '/p4'


class P4ModuleNotFound(neutron_exc.NotFound):
    message = "P4 Module %(id)s not found. Perhaps it has not been installed yet."


class P4ModuleAlreadyExists(neutron_exc.InUse):
    message = "P4 Module for given tenant already exists."


class P4ModuleInUse(neutron_exc.InUse):
    message = "P4 Module is already in use and cannot be deleted."


class P4ModuleAlreadyAttached(neutron_exc.InUse):
    message = "P4 Module is already attached."


class P4ModuleNotAttached(neutron_exc.BadRequest):
    message = "P4 Module is not attached to any VM."


def normalize_string(value):
    if value is None:
        return ''
    return value


RESOURCE_ATTRIBUTE_MAP = {
    'modules': {
        'id': {
            'allow_post': False, 'allow_put': False,
            'is_visible': True,
            'validate': {'type:uuid': None},
            'primary_key': True
        },
        'name': {
            'allow_post': True, 'allow_put': True,
            'is_visible': True, 'default': '',
            'validate': {'type:string': db_const.NAME_FIELD_SIZE},
        },
        'network_id': {
            'allow_post': True, 'allow_put': False,
            'required_by_policy': True,
            'validate': {'type:uuid': None},
            'is_visible': True},
        'tenant_id': {
            'allow_post': True, 'allow_put': False,
            'is_visible': True,
            'validate': {'type:string': db_const.PROJECT_ID_FIELD_SIZE}
        },
        'description': {
            'allow_post': True, 'allow_put': True,
            'is_visible': True, 'default': None,
            'validate': {'type:string': db_const.NAME_FIELD_SIZE},
            'convert_to': normalize_string
        },
        'program': {
            'allow_post': True, 'allow_put': True,
            'is_visible': True, 'default': None,
            'validate': {'type:string': db_const.NAME_FIELD_SIZE}
        }
    }
}


@six.add_metaclass(ABCMeta)
class P4(extensions.ExtensionDescriptor):
    """P4-based Data Plane Programmability extension. """

    @classmethod
    def get_name(cls):
        return "P4 Data Plane Programmability"

    @classmethod
    def get_alias(cls):
        return P4_EXT

    @classmethod
    def get_description(cls):
        return "P4 Data Plane Programmability extension."

    @classmethod
    def get_plugin_interface(cls):
        return P4PluginBase

    @classmethod
    def get_updated(cls):
        return "2015-10-05T10:00:00-00:00"

    def update_attributes_map(self, attributes):
        super(P4, self).update_attributes_map(
            attributes, extension_attrs_map=RESOURCE_ATTRIBUTE_MAP)

    @classmethod
    def get_resources(cls):
        """Returns Ext Resources."""
        plural_mappings = resource_helper.build_plural_mappings(
            {}, RESOURCE_ATTRIBUTE_MAP)
        plural_mappings['p4s'] = 'p4'
        plural_mappings['modules'] = 'module'
        action_map = {'module': {'attach': 'PUT',
                                 'detach': 'PUT',
                                 'configure': 'PUT',
                                 'unconfigure': 'PUT',
                                 'configuration': 'GET'}}

        return resource_helper.build_resource_info(
            plural_mappings,
            RESOURCE_ATTRIBUTE_MAP,
            P4_EXT,
            action_map=action_map,
            register_quota=True)

    def get_extended_resources(self, version):
        if version == "2.0":
            return RESOURCE_ATTRIBUTE_MAP
        return {}


@six.add_metaclass(ABCMeta)
class P4PluginBase(libbase.ServicePluginBase):

    def get_plugin_name(self):
        return P4_EXT

    def get_plugin_type(self):
        return P4_EXT

    def get_plugin_description(self):
        return 'P4-based Data Plane Programmability service plugin'

    @abstractmethod
    def get_modules(self, context, filters=None, fields=None,
                    sorts=None, limit=None, marker=None,
                    page_reverse=False):
        pass

    @abstractmethod
    def get_module(self, context, id, fields=None):
        pass

    @abstractmethod
    def create_module(self, context, module):
        pass

    @abstractmethod
    def update_module(self, context, id, module):
        pass

    @abstractmethod
    def delete_module(self, context, id):
        pass

    @abstractmethod
    def attach(self, context, module_id, module_info=None):
        pass

    @abstractmethod
    def detach(self, context, module_id, module_info):
        pass

    @abstractmethod
    def configure(self, context, module_id, payload=None):
        pass

    @abstractmethod
    def unconfigure(self, context, module_id, payload=None):
        pass

    @abstractmethod
    def configuration(self, context, module_id):
        pass

import logging
from oslo_log import helpers as log_helpers
from networking_p4.extensions import p4 as p4_ext
from networking_p4.services.common.constants import MODULE_STATE_CREATED, MODULE_STATE_ATTACHED
from neutron.db import common_db_mixin
from neutron.db import api as db_api
from oslo_utils import uuidutils
from models import P4Module
from sqlalchemy.orm import exc

LOG = logging.getLogger(__name__)


class P4DbPlugin(p4_ext.P4PluginBase,
                 common_db_mixin.CommonDbMixin):

    @log_helpers.log_method_call
    def create_module(self, context, module):
        mod = module['module']
        project_id = mod['project_id']
        network_id = mod['network_id']
        program = mod['program']
        desc = mod['description']
        name = mod['name']

        query = context.session.query(P4Module)
        for module in query.all():
            if module['program'] == program and module['project_id'] == project_id:
                LOG.error("P4 module for given tenant already exists")
                raise p4_ext.P4ModuleAlreadyExists()

        module_id = uuidutils.generate_uuid()
        with db_api.context_manager.writer.using(context):
            module_db = P4Module(id=module_id,
                                 project_id=project_id,
                                 network_id=network_id,
                                 name=name,
                                 description=desc,
                                 program=program,
                                 state=MODULE_STATE_CREATED)
            context.session.add(module_db)
        return self._make_p4_modules_dict(module_db)

    @log_helpers.log_method_call
    def set_module_attached(self, context, module_id):
        with db_api.context_manager.writer.using(context):
            module = self.get_module(context, module_id)
            module['state'] = MODULE_STATE_ATTACHED
            module.update(module)
        LOG.info("Module attached")

    @log_helpers.log_method_call
    def set_module_detached(self, context, module_id):
        with db_api.context_manager.writer.using(context):
            module = self.get_module(context, module_id)
            module['state'] = MODULE_STATE_CREATED
            module.update(module)
        LOG.info("Module detached. State is CREATED again.")

    @log_helpers.log_method_call
    def update_module(self, context, id, module):
        LOG.info("Updating module")
        new_module = module['module']
        with db_api.context_manager.writer.using(context):
            old_module = self.get_module(context, id)
            old_module.update(new_module)
        return self._make_p4_modules_dict(old_module)

    def delete_module(self, context, id):
        try:
            with db_api.context_manager.writer.using(context):
                module = self._get_by_id(context, P4Module, id)
                context.session.delete(module)
        except p4_ext.P4ModuleNotFound:
            LOG.info("Deleting a non-existing P4 module.")

    def get_modules(self, context, filters=None, fields=None,
                    sorts=None, limit=None, marker=None,
                    page_reverse=False):
        LOG.info("Retriving items from DB")

        marker_obj = self._get_marker_obj(context, 'p4_module', limit, marker)
        return self._get_collection(context,
                                    P4Module,
                                    self._make_p4_modules_dict,
                                    filters=filters, fields=fields,
                                    sorts=sorts,
                                    limit=limit, marker_obj=marker_obj,
                                    page_reverse=page_reverse)

    def get_module(self, context, id, fields=None):
        try:
            return self._get_by_id(context, P4Module, id)
        except exc.NoResultFound:
            raise p4_ext.P4ModuleNotFound(id=id)

    def _make_p4_modules_dict(self, p4_module, fields=None):
        res = {
            'id': p4_module['id'],
            'network_id': p4_module['network_id'],
            'project_id': p4_module['project_id'],
            'description': p4_module['description'],
            'name': p4_module['name'],
            'state': p4_module['state'],
            'program': p4_module['program']
        }
        return self._fields(res, fields)

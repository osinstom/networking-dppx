from oslo_log import helpers as log_helpers
from oslo_log import log as logging
from oslo_utils import excutils

from networking_p4.db import p4_db
from networking_p4.extensions import p4 as api_ext
from networking_p4.extensions.p4 import P4ModuleAlreadyAttached, P4ModuleNotAttached
from networking_p4.services.common import constants as p4_constants
from networking_p4.services.common import context as p4_ctx
from networking_p4.services.common.constants import MODULE_STATE_ATTACHED
from networking_p4.services.common.exceptions import P4DriverError
from networking_p4.services.driver_manager import P4DriverManager
from neutron.db import api as db_api
import json

LOG = logging.getLogger(__name__)

DEVICE_OWNER_P4 = p4_constants.DEVICE_OWNER_P4


class P4Plugin(p4_db.P4DbPlugin):

    supported_extension_aliases = [api_ext.P4_EXT]
    path_prefix = api_ext.P4_PREFIX

    def __init__(self):
        LOG.info("P4 plugin started.")
        self.driver_manager = P4DriverManager()
        super(P4Plugin, self).__init__()
        self.driver_manager.initialize()

    @log_helpers.log_method_call
    def create_module(self, context, module):
        """ Installing P4 module on the switch """

        with db_api.context_manager.writer.using(context):
            module_db = super(P4Plugin, self).create_module(context, module)
            module_ctx = p4_ctx.P4ModuleContext(self, context, module_db)
            self.driver_manager.create_module_precommit(module_ctx)

        try:
            self.driver_manager.create_module_postcommit(module_ctx)
        except P4DriverError as e:
            LOG.exception(e)
            with excutils.save_and_reraise_exception():
                LOG.error("Create module operation failed, "
                          "deleting module '%s'",
                          module_db['id'])
                self.delete_module(context, module_db['id'])

        return module_db

    @log_helpers.log_method_call
    def update_module(self, context, id, module):
        """ Updating P4 module on the switch """
        with db_api.context_manager.writer.using(context):
            original_module = self.get_module(context, id)
            updated_module = super(P4Plugin, self).update_module(context, id, module)
            updated_p4_context = p4_ctx.P4ModuleContext(self, context, updated_module)
            self.driver_manager.update_module_precommit(updated_p4_context)

        try:
            self.driver_manager.update_module_postcommit(updated_p4_context)
        except P4DriverError as e:
            LOG.exception(e)
            with excutils.save_and_reraise_exception():
                LOG.error("Update module operation failed "
                          "for module '%s'",
                          updated_module['id'])

        return updated_module

    @log_helpers.log_method_call
    def delete_module(self, context, id):
        """ Removing P4 module from the switch """
        module = self.get_module(context, id)
        module_context = p4_ctx.P4ModuleContext(self, context, module)

        try:
            self.driver_manager.delete_module(module_context)
        except P4DriverError as e:
            LOG.exception(e)
            with excutils.save_and_reraise_exception():
                LOG.error("Delete P4 module failed, module '%s'",
                          id)

        with db_api.context_manager.writer.using(context):
            module = self.get_module(context, id)
            module_context = p4_ctx.P4ModuleContext(self, context, module)
            super(P4Plugin, self).delete_module(context, id)
            self.driver_manager.delete_module_precommit(module_context)
        self.driver_manager.delete_module_postcommit(module_context)

    @log_helpers.log_method_call
    def attach(self, context, module_id, module_info=None):
        """ Attaching P4 module with Neutron infrastructure"""
        LOG.info("Attach.")
        LOG.info(str(module_info))
        module = self.get_module(context, module_id)

        if module['state'] == MODULE_STATE_ATTACHED:
            raise P4ModuleAlreadyAttached()

        module_attachment_ctx = p4_ctx.P4ModuleAttachmentContext(self, context, module, module_info)
        self.driver_manager.attach_module_precommit(module_attachment_ctx)

        try:
            self.driver_manager.attach_module_postcommit(module_attachment_ctx)
            super(P4Plugin, self).set_module_attached(context, module_id)
        except P4DriverError as e:
            LOG.exception(e)
            with excutils.save_and_reraise_exception():
                LOG.error("Attach module operation failed "
                          "for module '%s'",
                          module['id'])

    @log_helpers.log_method_call
    def detach(self, context, module_id, module_info=None):
        LOG.info("Detach.")
        LOG.info(str(module_info))

        module = self.get_module(context, module_id)

        if module['state'] != MODULE_STATE_ATTACHED:
            raise P4ModuleNotAttached()

        module_context = p4_ctx.P4ModuleAttachmentContext(self, context, module, module_info)
        self.driver_manager.detach_module_precommit(module_context)

        try:
            self.driver_manager.detach_module_postcommit(module_context)
            super(P4Plugin, self).set_module_detached(context, module_id)
        except P4DriverError as e:
            LOG.exception(e)
            with excutils.save_and_reraise_exception():
                LOG.error("Detach module operation failed "
                          "for module '%s'",
                          module['id'])

    @log_helpers.log_method_call
    def configure(self, context, module_id, payload=None):
        LOG.info("Configure.")
        module = self.get_module(context, module_id)
        configuration = payload['configuration']
        driver_context = p4_ctx.P4ModuleConfigurationContext(self, context, module, configuration)

        self.driver_manager.configure_module_precommit(driver_context)

        try:
            self.driver_manager.configure_module_postcommit(driver_context)
        except P4DriverError as e:
            LOG.exception(e)
            with excutils.save_and_reraise_exception():
                LOG.error("Configure module operation failed "
                          "for module '%s'",
                          module['id'])

    @log_helpers.log_method_call
    def unconfigure(self, context, module_id, payload=None):
        LOG.info("Unconfigure.")

        module = self.get_module(context, module_id)
        configuration = payload['configuration']
        driver_context = p4_ctx.P4ModuleConfigurationContext(self, context, module, configuration)

        self.driver_manager.unconfigure_module_precommit(driver_context)

        try:
            self.driver_manager.unconfigure_module_postcommit(driver_context)
        except P4DriverError as e:
            LOG.exception(e)
            with excutils.save_and_reraise_exception():
                LOG.error("Unconfigure module operation failed "
                          "for module '%s'",
                          module['id'])

    @log_helpers.log_method_call
    def configuration(self, context, module_id):
        LOG.info("Configuration.")

        module = self.get_module(context, module_id)
        driver_context = p4_ctx.P4ModuleConfigurationContext(self, context, module, None)

        self.driver_manager.get_module_configuration_precommit(driver_context)

        try:
            configuration = self.driver_manager.get_module_configuration_postcommit(driver_context)
            LOG.info("P4Plugin: " + str(configuration))
            return json.loads(configuration)
        except P4DriverError as e:
            LOG.exception(e)
            with excutils.save_and_reraise_exception():
                LOG.error("Get module configuration operation failed "
                          "for module '%s'",
                          module['id'])





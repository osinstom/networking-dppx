from oslo_config import cfg
from oslo_log import log
from stevedore.named import NamedExtensionManager

from networking_p4.services.common.exceptions import P4DriverError

LOG = log.getLogger(__name__)

cfg.CONF.import_opt('drivers',
                    'networking_p4.services.common.config',
                    group='p4')


class P4DriverManager(NamedExtensionManager):
    """Implementation of P4 drivers"""

    def __init__(self, namespace='networking_p4.p4.drivers',
                 names=cfg.CONF.p4.drivers):
        # Registered P$ drivers, keyed by name.
        self.drivers = {}

        # Ordered list of sfc drivers, defining
        # the order in which the drivers are called.
        self.ordered_drivers = []
        LOG.info("Configured P4 drivers: %s", names)
        super(P4DriverManager, self).__init__(namespace,
                                              names,
                                              invoke_on_load=True,
                                              name_order=True)
        LOG.info("Loaded P4 drivers: %s", self.names())
        self._register_drivers()

    def initialize(self):
        for driver in self.ordered_drivers:
            LOG.info("Initializing P4 driver '%s'", driver.name)
            driver.obj.initialize()

    def register_callback(self, topic, callback):
        for driver in self.ordered_drivers:
            driver.obj.add_callback(topic, callback)

    def _register_drivers(self):
        """Register all P4 drivers.

        This method should only be called once in the SfcDriverManager
        constructor.
        """
        for ext in self:
            self.drivers[ext.name] = ext
            self.ordered_drivers.append(ext)
        LOG.info("Registered P4 drivers: %s",
                 [driver.name for driver in self.ordered_drivers])

    def _call_drivers(self, method_name, context, raise_orig_exc=False):
        """Helper method for calling a method across all P4 drivers.

        :param method_name: name of the method to call
        :param context: context parameter to pass to each method call
        :param raise_orig_exc: whether or not to raise the original
        driver exception, or use a general one
        """

        for driver in self.ordered_drivers:
            try:
                ret = getattr(driver.obj, method_name)(context)
                if ret:
                    return ret
            except Exception as e:
                # This is an internal failure.
                LOG.exception(e)
                LOG.error(
                    "P4 driver '%(name)s' failed in %(method)s",
                    {'name': driver.name, 'method': method_name}
                )
                if raise_orig_exc:
                    raise
                else:
                    raise P4DriverError(
                        method=method_name
                    )

    def create_module_precommit(self, context):
        self._call_drivers('create_module_precommit', context)

    def create_module_postcommit(self, context):
        self._call_drivers('create_module_postcommit', context)

    def update_module_precommit(self, context):
        self._call_drivers('update_module_precommit', context)

    def update_module_postcommit(self, context):
        self._call_drivers('update_module_postcommit', context)

    def delete_module(self, context):
        self._call_drivers('delete_module', context)

    def delete_module_precommit(self, context):
        self._call_drivers('delete_module_precommit', context)

    def delete_module_postcommit(self, context):
        self._call_drivers('delete_module_postcommit', context)

    def attach_module_precommit(self, context):
        self._call_drivers('attach_module_precommit', context)

    def attach_module_postcommit(self, context):
        self._call_drivers('attach_module_postcommit', context)

    def detach_module_precommit(self, context):
        self._call_drivers('detach_module_precommit', context)

    def detach_module_postcommit(self, context):
        self._call_drivers('detach_module_postcommit', context)

    def configure_module_precommit(self, context):
        self._call_drivers('configure_module_precommit', context)

    def configure_module_postcommit(self, context):
        self._call_drivers('configure_module_postcommit', context)

    def unconfigure_module_precommit(self, context):
        self._call_drivers('unconfigure_module_precommit', context)

    def unconfigure_module_postcommit(self, context):
        self._call_drivers('unconfigure_module_postcommit', context)

    def get_module_configuration_precommit(self, context):
        self._call_drivers('get_module_configuration_precommit', context)

    def get_module_configuration_postcommit(self, context):
        return self._call_drivers('get_module_configuration_postcommit', context)




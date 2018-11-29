

class P4PluginContext(object):
    """P4 context base class."""
    def __init__(self, plugin, plugin_context):
        self._plugin = plugin
        self._plugin_context = plugin_context


class P4ModuleContext(P4PluginContext):

    def __init__(self, plugin, plugin_context, module):
        super(P4ModuleContext, self).__init__(plugin, plugin_context)
        self._p4module = module

    @property
    def current(self):
        return self._p4module


class P4ModuleAttachmentContext(P4PluginContext):

    def __init__(self, plugin, plugin_context, module, additional):
        super(P4ModuleAttachmentContext, self).__init__(plugin, plugin_context)
        self._module = module
        self._module_attachment = additional

    @property
    def module_context(self):
        return self._module

    @property
    def additional_context(self):
        return self._module_attachment


class P4ModuleConfigurationContext(P4PluginContext):

    def __init__(self, plugin, plugin_context, module, configuration):
        super(P4ModuleConfigurationContext, self).__init__(plugin, plugin_context)
        self._module = module
        self._module_config = configuration

    @property
    def module_context(self):
        return self._module

    @property
    def additional_context(self):
        return self._module_config

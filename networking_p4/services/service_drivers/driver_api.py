import six
from abc import ABCMeta, abstractmethod


@six.add_metaclass(ABCMeta)
class P4DriverApi(object):
    """ PdpDriver interface """

    @abstractmethod
    def add_callback(self, topic, callback):
        pass


@six.add_metaclass(ABCMeta)
class P4DriverBaseLegacy(object):

    @abstractmethod
    def create_module(self, context):
        pass

    @abstractmethod
    def update_module(self, context):
        pass

    @abstractmethod
    def delete_module(self, context):
        pass

    @abstractmethod
    def attach_module(self, context):
        pass

    @abstractmethod
    def detach_module(self, context):
        pass

    @abstractmethod
    def configure_module(self, context):
        pass

    @abstractmethod
    def unconfigure_module(self, context):
        pass

    @abstractmethod
    def get_module_configuration(self, context):
        pass


@six.add_metaclass(ABCMeta)
class P4DriverBase(P4DriverBaseLegacy):

    def create_module_precommit(self, context):
        pass

    def create_module_postcommit(self, context):
        self.create_module(context)

    def update_module_precommit(self, context):
        pass

    def update_module_postcommit(self, context):
        self.update_module(context)

    @abstractmethod
    def delete_module(self, context):
        pass

    def delete_module_precommit(self, context):
        pass

    def delete_module_postcommit(self, context):
        pass

    def attach_module_precommit(self, context):
        pass

    def attach_module_postcommit(self, context):
        self.attach_module(context)

    def detach_module_precommit(self, context):
        pass

    def detach_module_postcommit(self, context):
        self.detach_module(context)

    @abstractmethod
    def detach_module(self, context):
        pass

    def configure_module_precommit(self, context):
        pass

    def configure_module_postcommit(self, context):
        self.configure_module(context)

    def unconfigure_module_precommit(self, context):
        pass

    def unconfigure_module_postcommit(self, context):
        self.unconfigure_module(context)

    def get_module_configuration_precommit(self, context):
        pass

    def get_module_configuration_postcommit(self, context):
        return self.get_module_configuration(context)











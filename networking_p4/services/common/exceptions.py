from neutron_lib import exceptions


class P4DriverError(exceptions.NeutronException):
    """P4 driver call failed."""
    message = "%(method)s failed."


class P4AgentError(exceptions.NeutronException):
    """P4 agent failed."""
    message = "%(method)s failed."


class P4ImageNotFound(P4AgentError):
    """ P4 agent failed. Image has not been found in Glance"""
    message = "Image has not been found in Glance Store."

class VmIpNotFound(exceptions.NotFound):
    """  """
    message = "VM IP has not been found."



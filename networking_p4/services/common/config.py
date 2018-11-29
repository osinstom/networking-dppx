from oslo_config import cfg

from networking_sfc._i18n import _

P4_DRIVER_OPTS = [
    cfg.ListOpt('drivers',
                default=["default"],
                help=_("An ordered list of P4 drivers "
                       "entrypoints to be loaded from the "
                       "networking_p4.p4.drivers namespace.")),
]

cfg.CONF.register_opts(P4_DRIVER_OPTS, "p4")

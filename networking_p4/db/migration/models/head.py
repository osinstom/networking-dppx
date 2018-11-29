from neutron_lib.db import model_base

# pylint: disable=unused-import
import networking_p4.db.models # noqa


def get_metadata():
    return model_base.BASEV2.metadata
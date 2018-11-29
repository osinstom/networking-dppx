import sqlalchemy as sa
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy import orm
from sqlalchemy.orm import backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from neutron_lib.db import model_base
from neutron_lib.db import constants as db_const



PARAM_LEN = 255
VAR_MAX_LEN = 1024
UUID_LEN = 36


class P4ModuleServiceChainAssociation(model_base.BASEV2):
    __tablename__ = 'p4_module_service_chain_associations'

    port_pair_group_id = sa.Column(
        sa.String(UUID_LEN),
        sa.ForeignKey('sfc_port_pair_groups.id', ondelete='CASCADE'),
        primary_key=True
    )

    module_id = sa.Column(
        sa.String(UUID_LEN),
        sa.ForeignKey('p4_modules.id', ondelete='CASCADE')
    )

class P4Module(model_base.BASEV2, model_base.HasId, model_base.HasProject):
    __tablename__ = 'p4_modules'
    name = sa.Column(sa.String(db_const.NAME_FIELD_SIZE))
    description = sa.Column(sa.String(db_const.DESCRIPTION_FIELD_SIZE))
    program = sa.Column(sa.String(db_const.NAME_FIELD_SIZE))
    network_id = sa.Column(sa.String(36), sa.ForeignKey("networks.id"),
                           nullable=False)
    state = sa.Column(sa.String(db_const.NAME_FIELD_SIZE))



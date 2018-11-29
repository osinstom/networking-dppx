from networking_sfc.db.sfc_db import PortChain
from neutron.db import api as db_api
from networking_p4.db.models import P4ModuleServiceChainAssociation
from sqlalchemy.orm import exc as orm_exc


def store_ppg_id(context, module_id, port_pair_group_id):
    with db_api.context_manager.writer.using(context):
        module_service_chain_association = P4ModuleServiceChainAssociation(
            module_id=module_id,
            port_pair_group_id=port_pair_group_id
        )
        context.session.add(module_service_chain_association)


def get_module_service_association(context, module_id):
    with db_api.context_manager.writer.using(context):
        query = context.session.query(P4ModuleServiceChainAssociation)
        try:
            return query.filter(P4ModuleServiceChainAssociation.module_id == module_id).one()
        except orm_exc.NoResultFound:
            return None


def get_port_chain_by_ppg_id(context, ppg_id):
    with db_api.context_manager.reader.using(context):
        query = context.session.query(PortChain)
        for port_chain in query.all():
            pc_pg_ids = [
                assoc['portpairgroup_id']
                for assoc in port_chain.chain_group_associations
            ]
            if ppg_id in pc_pg_ids:
                return port_chain


def get_flow_classifier_by_port_chain_id(context, port_chain_id):
    with db_api.context_manager.reader.using(context):
        query = context.session.query(PortChain)
        port_chain = query.filter(PortChain.id == port_chain_id).one()
        flow_classifiers = [
            assoc['flowclassifier_id']
            for assoc in port_chain.chain_classifier_associations
        ]

        flow_classifier_id = flow_classifiers[0]
        return flow_classifier_id


def delete_module_service_association(context, module_id, portpairgroup_id):
    with db_api.context_manager.writer.using(context):
        query = context.session.query(P4ModuleServiceChainAssociation)
        for result in query.all():
            if result['module_id'] == module_id and result['port_pair_group_id'] == portpairgroup_id:
                to_be_deleted = result
        if to_be_deleted:
            context.session.delete(to_be_deleted)

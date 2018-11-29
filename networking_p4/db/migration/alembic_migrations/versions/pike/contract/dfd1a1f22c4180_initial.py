"""start networking-p4 contract branch

Revision ID: dfd1a1f22c4180
Create Date: 2018-03-13 12:34:56.789098

"""

from neutron.db.migration import cli


# revision identifiers, used by Alembic.
revision = 'dfd1a1f22c4180'
down_revision = 'start_networking_p4'
branch_labels = (cli.CONTRACT_BRANCH,)


def upgrade():
    pass

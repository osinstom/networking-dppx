"""start networking-p4 expand branch

Revision ID: 65b6db113427b9
Create Date: 2016-03-13 12:34:56.789098

"""

from neutron.db.migration import cli


# revision identifiers, used by Alembic.
revision = '65b6db113427b9'
down_revision = 'start_networking_p4'
branch_labels = (cli.EXPAND_BRANCH,)


def upgrade():
    pass

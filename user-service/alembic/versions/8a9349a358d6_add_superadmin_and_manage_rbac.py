"""add superadmin and manage_rbac

Revision ID: 8a9349a358d6
Revises: 8e7758e3900a
Create Date: 2026-06-06 01:26:06.279589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a9349a358d6'
down_revision: Union[str, None] = '8e7758e3900a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Insert manage_rbac permission
    permissions_table = sa.table('permissions',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('description', sa.String)
    )
    op.bulk_insert(permissions_table, [
        {'id': 4, 'name': 'manage_rbac', 'description': 'Manage roles and permissions and assign user roles'}
    ])

    # 2. Insert Super Admin role
    roles_table = sa.table('roles',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('description', sa.String)
    )
    op.bulk_insert(roles_table, [
        {'id': 5, 'name': 'Super Admin', 'description': 'Super Administrator - Can configure RBAC, roles, and permissions'}
    ])

    # 3. Associate permissions to Super Admin role
    role_permissions_table = sa.table('role_permissions',
        sa.column('role_id', sa.Integer),
        sa.column('permission_id', sa.Integer)
    )
    op.bulk_insert(role_permissions_table, [
        {'role_id': 5, 'permission_id': 1},
        {'role_id': 5, 'permission_id': 2},
        {'role_id': 5, 'permission_id': 3},
        {'role_id': 5, 'permission_id': 4},
    ])

    # 4. Hash password and insert superadmin@tibarpay.com
    from app.auth import hash_password
    hashed_pwd = hash_password('admin123')
    
    op.execute(
        f"INSERT INTO users (email, hashed_password, role, tier, is_active, created_at) "
        f"VALUES ('superadmin@tibarpay.com', '{hashed_pwd}', 'admin', NULL, true, '2026-06-06 01:26:00')"
    )

    # 5. Map superadmin@tibarpay.com to Super Admin role (id=5)
    op.execute(
        "INSERT INTO user_roles (user_id, role_id) "
        "SELECT id, 5 FROM users WHERE email = 'superadmin@tibarpay.com'"
    )

    # 6. Restrict admin@tibarpay.com and admin2@tibarpay.com from direct bypass
    # Delete their mapping to Super Admin/Legacy Admin (id=1) to force them through maker-checker
    op.execute(
        "DELETE FROM user_roles WHERE role_id = 1 AND user_id IN "
        "(SELECT id FROM users WHERE email IN ('admin@tibarpay.com', 'admin2@tibarpay.com'))"
    )


def downgrade() -> None:
    pass

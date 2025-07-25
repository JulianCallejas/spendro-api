"""add_budget_admin_deletion_trigger

Revision ID: b2cb4a921abe
Revises: a3d6ff563930
Create Date: 2025-07-19 17:34:14.305577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2cb4a921abe'
down_revision = 'a3d6ff563930'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the trigger function
    op.execute('''
        CREATE OR REPLACE FUNCTION delete_budget_on_last_admin_removal()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Check if the deleted record was an admin
            IF OLD.role = 'ADMIN' THEN
                -- Check if there are any remaining admin users for this budget
                IF NOT EXISTS (
                    SELECT 1 
                    FROM user_budgets 
                    WHERE budget_id = OLD.budget_id 
                    AND role = 'ADMIN'
                    AND id != OLD.id
                ) THEN
                    -- No more admins exist, delete the budget
                    DELETE FROM budgets WHERE id = OLD.budget_id;
                END IF;
            END IF;
            
            RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;
    ''')
    
    # Create the trigger
    op.execute('''
        CREATE TRIGGER trigger_delete_budget_on_last_admin_removal
        AFTER DELETE ON user_budgets
        FOR EACH ROW
        EXECUTE FUNCTION delete_budget_on_last_admin_removal();
    ''')


def downgrade() -> None:
    # Drop the trigger
    op.execute("DROP TRIGGER IF EXISTS trigger_delete_budget_on_last_admin_removal ON user_budgets;")
    
    # Drop the trigger function
    op.execute("DROP FUNCTION IF EXISTS delete_budget_on_last_admin_removal();")
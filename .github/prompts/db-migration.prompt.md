---
description: "Generate and review an Alembic database migration for model changes"
---

# Role
You are a database migration specialist working with SQLAlchemy 2.x async and Alembic.

# Task
Analyze the current SQLAlchemy model definitions in app/models/ and generate an Alembic migration that captures all pending schema changes.

# Context
- Database: SQL Server (mssql+aioodbc driver)
- ORM: SQLAlchemy 2.x with DeclarativeBase, Mapped, mapped_column
- Migration tool: Alembic with async support
- Models location: api/app/models/
- Migrations location: api/alembic/versions/

# Steps
1. Review all model files in app/models/ for current table definitions
2. Compare against existing migrations in alembic/versions/
3. Generate the migration command: `alembic revision --autogenerate -m "<description>"`
4. Review the generated migration file for correctness:
   - Verify column types map correctly to SQL Server types
   - Check that nullable, default, and index settings are correct
   - Ensure foreign key constraints are properly defined
   - Confirm downgrade() properly reverses all upgrade() operations
5. Flag any potential data loss operations (column drops, type changes)

# Output
- The alembic command to run
- A review of the generated migration with any warnings
- The command to apply: `alembic upgrade head`

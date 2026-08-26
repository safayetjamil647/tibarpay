import os
import sys

# Ensure backend directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker

def migrate_data():
    sqlite_url = "sqlite:///./sql_app.db"
    postgres_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/tibarpay")

    if not os.path.exists("./sql_app.db"):
        print("SQLite database not found. Skipping data migration.")
        return

    print("Connecting to SQLite...")
    sqlite_engine = create_engine(sqlite_url)
    sqlite_metadata = MetaData()
    sqlite_metadata.reflect(bind=sqlite_engine)
    
    print("Connecting to PostgreSQL...")
    pg_engine = create_engine(postgres_url)
    
    # Check if Postgres has tables. If not, it means alembic hasn't been run or we need to run it.
    pg_metadata = MetaData()
    pg_metadata.reflect(bind=pg_engine)
    
    if not pg_metadata.tables:
        print("PostgreSQL tables not found. Please run 'alembic upgrade head' first.")
        return

    print("Starting data migration...")
    
    with sqlite_engine.connect() as sqlite_conn:
        with pg_engine.begin() as pg_conn:
            # Note: order matters for foreign keys. We can temporarily disable constraints in PG or order the tables.
            # Easiest way in Postgres is to disable all triggers/constraints
            pg_conn.execute(text("SET session_replication_role = 'replica';"))
            
            for table_name in sqlite_metadata.sorted_tables:
                name = table_name.name
                if name == 'alembic_version':
                    continue # Skip alembic tracking
                    
                print(f"Migrating table: {name}...")
                sqlite_table = sqlite_metadata.tables[name]
                pg_table = pg_metadata.tables.get(name)
                
                if pg_table is None:
                    print(f"WARNING: Table {name} not found in PostgreSQL. Skipping.")
                    continue
                
                # Delete existing data from Postgres table
                pg_conn.execute(text(f"DELETE FROM {name}"))
                
                # Fetch all rows from SQLite
                result = sqlite_conn.execute(sqlite_table.select()).fetchall()
                if not result:
                    print(f"  Table {name} is empty.")
                    continue
                    
                # Convert rows to dicts
                rows = [dict(row._mapping) for row in result]
                
                # Insert into Postgres
                pg_conn.execute(pg_table.insert(), rows)
                print(f"  Migrated {len(rows)} rows to {name}.")

            # Re-enable constraints
            pg_conn.execute(text("SET session_replication_role = 'origin';"))
            
    # Reset sequences for autoincrement columns (outside the main transaction)
    for table_name in sqlite_metadata.sorted_tables:
        name = table_name.name
        if name == 'alembic_version':
            continue
        try:
            with pg_engine.begin() as seq_conn:
                seq_conn.execute(text(f"SELECT setval('{name}_id_seq', COALESCE((SELECT MAX(id)+1 FROM {name}), 1), false)"))
                print(f"Reset sequence for {name}")
        except Exception as e:
            pass
    print("Data migration complete!")

if __name__ == "__main__":
    migrate_data()

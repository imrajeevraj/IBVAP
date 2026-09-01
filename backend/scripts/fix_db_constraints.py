from backend.app.core.database import engine
from sqlalchemy import text

def fix_constraints():
    with engine.begin() as conn:
        # Find all constraints referencing tracks
        query = text("""
            SELECT conname, conrelid::regclass::text as tbl 
            FROM pg_constraint 
            WHERE confrelid = 'tracks'::regclass;
        """)
        try:
            fks = conn.execute(query).fetchall()
            print(f"Found {len(fks)} constraints pointing to tracks:")
            for conname, tbl in fks:
                conn.execute(text(f"ALTER TABLE {tbl} DROP CONSTRAINT IF EXISTS {conname} CASCADE;"))
                print(f"  - Dropped {conname} from {tbl}")
        except Exception as e:
            print(f"Error or no tracks table: {e}")

if __name__ == "__main__":
    fix_constraints()

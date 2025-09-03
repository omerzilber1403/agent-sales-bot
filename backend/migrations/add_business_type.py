#!/usr/bin/env python3
"""
Migration script to add business_type field to companies table
"""

import sqlite3
from pathlib import Path

def run_migration():
    # Get database path
    db_path = Path(__file__).parent.parent.parent / "data" / "agent.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    print(f"Running business_type migration on database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if business_type column already exists
        cursor.execute("PRAGMA table_info(companies)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        if 'business_type' not in existing_columns:
            # Add business_type column
            cursor.execute("ALTER TABLE companies ADD COLUMN business_type VARCHAR(10) DEFAULT 'B2B'")
            print("✓ Added business_type column")
            
            # Update existing companies based on their name/domain
            cursor.execute("""
                UPDATE companies 
                SET business_type = 'B2C' 
                WHERE name LIKE '%מועדון%' 
                   OR name LIKE '%גלישה%' 
                   OR name LIKE '%ספורט%'
                   OR name LIKE '%ים%'
                   OR name LIKE '%הדרכה%'
                   OR name LIKE '%בריאות%'
                   OR name LIKE '%B2C%'
            """)
            
            updated_rows = cursor.rowcount
            print(f"✓ Updated {updated_rows} companies to B2C based on name patterns")
        else:
            print("- business_type column already exists")
        
        # Commit changes
        conn.commit()
        print("✓ Migration completed successfully!")
        
    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()

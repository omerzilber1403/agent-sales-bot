#!/usr/bin/env python3
"""
Migration: Add custom_fields column to companies table
"""

import sqlite3
import os

def run_migration():
    # Connect to database
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'agent.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add custom_fields column
        cursor.execute("""
            ALTER TABLE companies 
            ADD COLUMN custom_fields TEXT
        """)
        
        # Update מועדון גלישה גאולה with B2C-specific fields
        cursor.execute("""
            UPDATE companies 
            SET custom_fields = ?
            WHERE name = 'מועדון גלישה גאולה'
        """, (json.dumps({
            "description": "שדות מידע ספציפיים למועדון גלישה - B2C",
            "fields": {
                "surfing_level": "רמת גלישה (מתחיל/בינוני/מתקדם)",
                "experience": "ניסיון קודם בגלישה (כן/לא)",
                "preferred_date": "תאריך רצוי לשיעור",
                "participants": "מספר משתתפים",
                "equipment": "ציוד נדרש (גלשן/חליפה/שנורקל)",
                "goals": "מטרות (ללמוד/לשפר/כושר/כיף)"
            }
        }),))
        
        conn.commit()
        print("✅ Migration completed successfully!")
        print("✅ Added custom_fields column to companies table")
        print("✅ Updated מועדון גלישה גאולה with B2C-specific fields")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import json
    run_migration()

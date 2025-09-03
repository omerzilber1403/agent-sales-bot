#!/usr/bin/env python3
"""
Migration script to add new company fields to the database
Run this script to update the companies table with new fields
"""

import sqlite3
import json
import os
from pathlib import Path

def run_migration():
    # Get database path
    db_path = Path(__file__).parent.parent.parent / "data" / "agent.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    print(f"Running migration on database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add new columns to companies table
        new_columns = [
            # Core fields
            ("brand_aliases", "TEXT"),
            ("timezone", "VARCHAR(50) DEFAULT 'Asia/Jerusalem'"),
            ("locale", "VARCHAR(10) DEFAULT 'he-IL'"),
            ("currency", "VARCHAR(3) DEFAULT 'ILS'"),
            
            # Brand Voice
            ("brand_voice", "TEXT"),
            
            # Value proposition
            ("one_line_value", "TEXT"),
            
            # ICP
            ("icp", "TEXT"),
            
            # Pain points
            ("pain_points", "TEXT"),
            
            # Products
            ("products", "TEXT"),
            
            # Pricing Policy
            ("pricing_policy", "TEXT"),
            
            # CTA
            ("cta_type", "VARCHAR(50) DEFAULT 'booking_link'"),
            ("booking_link", "VARCHAR(500)"),
            ("meeting_length_min", "INTEGER DEFAULT 15"),
            
            # Qualification Rules
            ("qualification_rules", "TEXT"),
            
            # Objections Playbook
            ("objections_playbook", "TEXT"),
            
            # Handoff Rules
            ("handoff_rules", "TEXT"),
            
            # Plus fields
            ("differentiators", "TEXT"),
            ("competitors_map", "TEXT"),
            ("discovery_questions", "TEXT"),
            ("faq_kb_refs", "TEXT"),
            ("case_studies", "TEXT"),
            ("refund_sla_policy", "TEXT"),
            ("language_prefs", "TEXT"),
            ("quote_long_mode", "TEXT"),
            ("sensitive_topics", "TEXT"),
            
            # Pro fields
            ("consent_texts", "TEXT"),
            ("pii_allowed", "TEXT"),
            ("regional_rules", "TEXT"),
            ("lead_scoring", "TEXT"),
            ("analytics_goals", "TEXT"),
            ("update_cadence", "VARCHAR(50)"),
            ("policy_version", "VARCHAR(50)"),
            ("owner", "VARCHAR(255)")
        ]
        
        # Check which columns already exist
        cursor.execute("PRAGMA table_info(companies)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Add missing columns
        for column_name, column_def in new_columns:
            if column_name not in existing_columns:
                try:
                    alter_sql = f"ALTER TABLE companies ADD COLUMN {column_name} {column_def}"
                    cursor.execute(alter_sql)
                    print(f"✓ Added column: {column_name}")
                except sqlite3.Error as e:
                    print(f"✗ Error adding column {column_name}: {e}")
            else:
                print(f"- Column {column_name} already exists")
        
        # Commit changes
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
        # Show updated table structure
        print("\nUpdated companies table structure:")
        cursor.execute("PRAGMA table_info(companies)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
            
    except sqlite3.Error as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()

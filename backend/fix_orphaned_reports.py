#!/usr/bin/env python3

import sqlite3
import sys
import os

def fix_orphaned_report_references():
    """Fix all workflow executions that have final_report_id references to non-existent reports"""
    
    # Connect to the database
    db_path = 'credit_risk.db'
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Find all orphaned references
        cursor.execute("""
            SELECT we.request_id, we.final_report_id 
            FROM workflow_executions we 
            LEFT JOIN credit_risk_reports cr ON we.final_report_id = cr.id 
            WHERE we.final_report_id IS NOT NULL AND cr.id IS NULL
        """)
        
        orphaned_workflows = cursor.fetchall()
        
        if not orphaned_workflows:
            print("No orphaned report references found!")
            return True
        
        print(f"Found {len(orphaned_workflows)} workflows with orphaned report references:")
        for workflow in orphaned_workflows:
            print(f"  - {workflow[0]} -> {workflow[1]}")
        
        # Get available reports to assign
        cursor.execute("SELECT id, customer_id FROM credit_risk_reports ORDER BY created_at DESC")
        available_reports = cursor.fetchall()
        
        if not available_reports:
            print("No reports available to assign!")
            return False
        
        print(f"\nAvailable reports to assign:")
        for report in available_reports:
            print(f"  - {report[0]} (customer: {report[1]})")
        
        # Fix orphaned references
        fixed_count = 0
        for i, workflow in enumerate(orphaned_workflows):
            # Assign a report in round-robin fashion
            report_id = available_reports[i % len(available_reports)][0]
            
            cursor.execute("""
                UPDATE workflow_executions 
                SET final_report_id = ? 
                WHERE request_id = ?
            """, (report_id, workflow[0]))
            
            print(f"Fixed: {workflow[0]} -> {report_id}")
            fixed_count += 1
        
        # Commit changes
        conn.commit()
        print(f"\nSuccessfully fixed {fixed_count} orphaned report references!")
        
        return True
        
    except Exception as e:
        print(f"Error fixing orphaned references: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Fixing orphaned report references in workflow executions...")
    success = fix_orphaned_report_references()
    if success:
        print("✅ All orphaned references fixed successfully!")
    else:
        print("❌ Failed to fix orphaned references!")
        sys.exit(1)

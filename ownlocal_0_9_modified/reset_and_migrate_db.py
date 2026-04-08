#!/usr/bin/env python3
"""
STEP 2: Database Reset + Demo Account + merchant_dashboard table
=========================================================================

This script will:
1. Clear ALL existing merchant data from the merchant table
2. Clear ALL existing waitlist data
3. Create the NEW merchant_dashboard table with is_demo column (if not exists)
4. Insert the ONLY demo merchant account:
   - username: merchant-store-demo
   - password: merchant123 (will be hashed)
   - id: Will be auto-assigned (likely id=1 after clear)
   - is_demo: true
5. Create a corresponding merchant_dashboard entry for the demo merchant (is_demo=1)

Usage:
    python3 reset_and_migrate_db.py

NOTE: This is a one-time setup script. It will PERMANENTLY DELETE 
all existing merchant accounts and replace them with the demo account only.
"""

import sqlite3
import hashlib
import os

DB_PATH = "ownlocal.db"

def hash_password(password: str) -> str:
    """SHA-256 hash password (matches backend)"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def main():
    print("🔄 STEP 2: Database Reset + Demo Account Setup")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Step 1: Clear existing merchant data
    print("\n1️⃣  Clearing existing merchant data...")
    c.execute("DELETE FROM merchant;")
    print("   ✅ Merchant table cleared")
    
    # Step 2: Clear existing waitlist data
    print("\n2️⃣  Clearing waitlist data...")
    c.execute("DELETE FROM waitlist;")
    print("   ✅ Waitlist table cleared")
    
    # Step 3: Create merchant_dashboard table with is_demo column
    print("\n3️⃣  Creating merchant_dashboard table...")
    c.execute("""
        CREATE TABLE IF NOT EXISTS merchant_dashboard (
            id              INTEGER PRIMARY KEY,
            merchant_id     INTEGER NOT NULL UNIQUE,
            is_demo         INTEGER DEFAULT 0,
            data            TEXT DEFAULT '{}',
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (merchant_id) REFERENCES merchant(id)
        )
    """)
    print("   ✅ merchant_dashboard table created")
    
    # Step 4: Insert demo merchant account
    print("\n4️⃣  Inserting demo merchant account...")
    demo_password = hash_password("merchant123")
    print(f"   - Username: merchant-store-demo")
    print(f"   - Password: merchant123")
    print(f"   - Hashed: {demo_password}")
    
    c.execute("""
        INSERT INTO merchant 
        (shop_name, owner_name, password, category, pincode, gstin, email, monthly_footfall)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "merchant-store-demo",  # shop_name (acts as username)
        "",                      # owner_name (empty)
        demo_password,           # password (hashed)
        "Demo Store",            # category
        "700019",                # pincode
        "",                      # gstin (empty)
        "demo@ownlocal.com",     # email
        0                        # monthly_footfall
    ))
    print("   ✅ Demo merchant created")
    
    # Step 5: Get the ID of the newly created merchant
    c.execute("SELECT id FROM merchant WHERE shop_name = 'merchant-store-demo'")
    merchant_id = c.fetchone()[0]
    print(f"   - Assigned ID: {merchant_id}")
    
    # Step 6: Create corresponding merchant_dashboard entry (is_demo=1 for demo merchant)
    print("\n5️⃣  Creating merchant_dashboard entry...")
    c.execute("""
        INSERT INTO merchant_dashboard (merchant_id, is_demo, data)
        VALUES (?, 1, '{}')
    """, (merchant_id,))
    print(f"   ✅ Dashboard created for merchant_id={merchant_id} with is_demo=1")
    
    # Commit all changes
    conn.commit()
    
    # Step 7: Verify
    print("\n6️⃣  Verification...")
    c.execute("SELECT COUNT(*) FROM merchant;")
    merchant_count = c.fetchone()[0]
    print(f"   ✅ Merchant records: {merchant_count}")
    
    c.execute("SELECT id, shop_name FROM merchant;")
    merchants = c.fetchall()
    for m_id, m_name in merchants:
        print(f"      - ID={m_id}: {m_name}")
    
    c.execute("SELECT COUNT(*) FROM merchant_dashboard;")
    dashboard_count = c.fetchone()[0]
    print(f"   ✅ Dashboard entries: {dashboard_count}")
    
    c.execute("SELECT id, merchant_id, is_demo FROM merchant_dashboard;")
    dashboards = c.fetchall()
    for dash_id, m_id, is_demo in dashboards:
        print(f"      - ID={dash_id}: merchant_id={m_id}, is_demo={is_demo}")
    
    c.execute("SELECT COUNT(*) FROM waitlist;")
    waitlist_count = c.fetchone()[0]
    print(f"   ✅ Waitlist records: {waitlist_count}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✨ STEP 2 COMPLETE!")
    print("=" * 60)
    print("\n📋 Summary:")
    print("   ✓ All merchant data cleared")
    print("   ✓ All waitlist data cleared")
    print("   ✓ merchant_dashboard table created with is_demo column")
    print("   ✓ Demo account created with is_demo=1:")
    print("      Username: merchant-store-demo")
    print("      Password: merchant123")
    print(f"      ID: {merchant_id}")
    print("\n🚀 Ready for backend deployment!")
    print("   The database is now reset and ready for production use.")
    print("   Only the demo merchant account exists.\n")

if __name__ == "__main__":
    main()

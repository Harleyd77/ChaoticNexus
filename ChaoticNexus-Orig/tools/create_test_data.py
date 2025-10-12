#!/usr/bin/env python3
"""
Create test customers and jobs for development
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from powder_app.core.db import db_execute, db_query_one, db_query_all

# Test customer data
TEST_CUSTOMERS = [
    {
        "company_name": "Smith Manufacturing Co.",
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith.test@smithmfg.test",
        "phone": "(555) 123-4567",
        "address": "123 Industrial Pkwy",
        "city": "Portland",
        "state": "OR",
        "zip": "97201"
    },
    {
        "company_name": "Acme Metal Works",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "email": "sarah.johnson.test@acmemetal.test",
        "phone": "(555) 234-5678",
        "address": "456 Steel Ave",
        "city": "Seattle",
        "state": "WA",
        "zip": "98101"
    },
    {
        "company_name": "Pacific Fabrication LLC",
        "first_name": "Mike",
        "last_name": "Chen",
        "email": "mike.chen.test@pacfab.test",
        "phone": "(555) 345-6789",
        "address": "789 Workshop Rd",
        "city": "Vancouver",
        "state": "WA",
        "zip": "98660"
    },
    {
        "company_name": "Riverside Railings Inc",
        "first_name": "Emily",
        "last_name": "Rodriguez",
        "email": "emily.rodriguez.test@riversiderailings.test",
        "phone": "(555) 456-7890",
        "address": "321 River St",
        "city": "Beaverton",
        "state": "OR",
        "zip": "97005"
    },
    {
        "company_name": "Mountain View Construction",
        "first_name": "David",
        "last_name": "Williams",
        "email": "david.williams.test@mtviewconst.test",
        "phone": "(555) 567-8901",
        "address": "654 Mountain Blvd",
        "city": "Hillsboro",
        "state": "OR",
        "zip": "97124"
    }
]

# Job templates for variety
JOB_TEMPLATES = [
    {
        "type": "Railing",
        "description": "Commercial railing system for office building - stainless steel with powder coat finish",
        "powder_colors": ["RAL 7016 Anthracite Grey", "Gloss Black", "Textured Black"]
    },
    {
        "type": "Gate",
        "description": "Custom decorative gate installation - ornamental metalwork",
        "powder_colors": ["Bronze Metallic", "Copper Vein", "Oil Rubbed Bronze"]
    },
    {
        "type": "Furniture",
        "description": "Metal furniture components - commercial grade outdoor furniture",
        "powder_colors": ["Pure White", "Matte Black", "Silver Metallic"]
    },
    {
        "type": "Architectural",
        "description": "Architectural metal panels - exterior building facade",
        "powder_colors": ["Champagne Gold", "Anodized Silver", "Charcoal Grey"]
    },
    {
        "type": "Industrial",
        "description": "Industrial equipment housing - machinery enclosures",
        "powder_colors": ["Safety Yellow", "Traffic Red", "Signal Orange"]
    },
    {
        "type": "Railing",
        "description": "Residential deck railing - aluminum construction",
        "powder_colors": ["Bronze", "Black Satin", "Pewter"]
    },
    {
        "type": "Fabrication",
        "description": "Custom fabricated parts - precision metalwork",
        "powder_colors": ["Clear Coat", "RAL 9005 Black", "Textured White"]
    },
    {
        "type": "Staircase",
        "description": "Commercial staircase with glass panels",
        "powder_colors": ["Chrome Silver", "Brushed Nickel", "Satin Black"]
    },
    {
        "type": "Balcony",
        "description": "Multi-level balcony railing system",
        "powder_colors": ["Graphite Grey", "Bronze Metallic", "Arctic White"]
    }
]

def create_customers_and_jobs():
    """Create test customers and jobs"""
    print("=" * 70)
    print("🚀 CREATING TEST DATA FOR DEVELOPMENT")
    print("=" * 70)
    print()
    
    created_jobs = 0
    created_customers = 0
    
    # Check existing test customers
    existing = db_query_all("SELECT email FROM customers WHERE email LIKE ?", ('%test%',))
    if existing:
        print(f"ℹ️  Found {len(existing)} existing test customers")
        response = input("   Delete existing test data first? (y/n): ").strip().lower()
        if response == 'y':
            # Delete jobs for test customers (match by company name)
            for cust in existing:
                # Get company name for this email
                c = db_query_one("SELECT company FROM customers WHERE email = ?", (cust['email'],))
                if c:
                    db_execute("DELETE FROM jobs WHERE company = ?", (c['company'],))
            db_execute("DELETE FROM customers WHERE email LIKE ?", ('%test%',))
            print("   ✅ Cleaned up existing test data")
        print()
    
    for idx, customer_data in enumerate(TEST_CUSTOMERS, 1):
        print(f"[{idx}/{len(TEST_CUSTOMERS)}] Creating: {customer_data['company_name']}")
        
        # Create customer
        try:
            db_execute("""
                INSERT INTO customers (
                    created_at, company, contact_name,
                    email, phone, address
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                customer_data["company_name"],
                f"{customer_data['first_name']} {customer_data['last_name']}",
                customer_data["email"],
                customer_data["phone"],
                f"{customer_data['address']}, {customer_data['city']}, {customer_data['state']} {customer_data['zip']}"
            ))
            
            # Get the customer ID
            customer = db_query_one(
                "SELECT id FROM customers WHERE email = ?",
                (customer_data["email"],)
            )
            customer_id = customer['id']
            created_customers += 1
            
            print(f"     ✅ Customer ID: {customer_id}")
            print(f"     📧 {customer_data['email']}")
            print(f"     📍 {customer_data['city']}, {customer_data['state']}")
            
            # Create 3 jobs for this customer
            for i in range(3):
                job_template = random.choice(JOB_TEMPLATES)
                
                # Random dates
                date_in = datetime.now() - timedelta(days=random.randint(1, 30))
                due_by = date_in + timedelta(days=random.randint(7, 21))
                
                # Random status
                statuses = ["in_work", "waiting_material", "ready_pickup", "completed"]
                status = random.choice(statuses)
                
                db_execute("""
                    INSERT INTO jobs (
                        created_at, contact_name, date_in, due_by,
                        company, type, description, color, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    f"{customer_data['first_name']} {customer_data['last_name']}",
                    date_in.strftime("%Y-%m-%d"),
                    due_by.strftime("%Y-%m-%d"),
                    customer_data["company_name"],
                    job_template['type'],
                    job_template['description'],
                    random.choice(job_template['powder_colors']),
                    status
                ))
                
                # Get job ID
                job = db_query_one("SELECT id FROM jobs WHERE company = ? ORDER BY id DESC LIMIT 1", (customer_data["company_name"],))
                job_id = job['id']
                created_jobs += 1
                
                status_emoji = "⏳" if status == "in_work" else "⏸️" if status == "waiting_material" else "✅" if status == "ready_pickup" else "🎉"
                print(f"     {status_emoji} Job #{job_id}: {job_template['type']} Project #{i+1} ({status})")
            
            print()
        
        except Exception as e:
            print(f"     ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("=" * 70)
    print("✅ TEST DATA CREATION COMPLETE!")
    print("=" * 70)
    print(f"📊 Statistics:")
    print(f"   • Created {created_customers} test customers")
    print(f"   • Created {created_jobs} test jobs")
    print(f"   • Average jobs per customer: {created_jobs/created_customers if created_customers > 0 else 0:.1f}")
    print()
    print("💡 Tips:")
    print("   • All test emails end with '.test' for easy identification")
    print("   • Jobs have varied statuses, dates, and descriptions")
    print("   • You can safely delete test data by searching for '.test' emails")
    print("=" * 70)

if __name__ == "__main__":
    try:
        create_customers_and_jobs()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

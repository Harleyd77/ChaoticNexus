#!/usr/bin/env python3
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'storage', 'data', 'uploads', 'app.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check powders table schema
    cursor.execute("PRAGMA table_info(powders)")
    columns = cursor.fetchall()

    print("Powders table schema:")
    print("ID | Name | Type | NotNull | Default | PK")
    print("-" * 50)
    for col in columns:
        print(f"{col[0]:2} | {col[1]:15} | {col[2]:8} | {col[3]:7} | {str(col[4]):7} | {col[5]}")

    # Check if required columns exist
    column_names = [col[1] for col in columns]
    required_cols = ['charge_per_kg', 'charge_per_lb']

    print("\nRequired columns check:")
    for col in required_cols:
        if col in column_names:
            print(f"✓ {col}")
        else:
            print(f"✗ {col} - MISSING!")

    conn.close()

except Exception as e:
    print(f"Error: {e}")


# Database Migration: Add Charge Columns

## Overview
This migration adds two new columns to the `powders` table to store calculated charge values:
- `charge_per_kg` - The selling price per kilogram (cost + markup)
- `charge_per_lb` - The selling price per pound

## Why Store These Values?
While the values are automatically calculated from `price_per_kg` and the markup percentage, storing them in the database provides:
- **Historical data**: If you change the markup percentage later, old records retain their original charge values
- **Future integrations**: Other applications can read these values directly without needing to know the markup calculation
- **Reporting**: Easier to query and analyze pricing data across time periods

## Running the Migration

### Step 1: Run the migration script
```bash
cd /home/harley/Projects/PowderApp1.3
python3 add_charge_columns_migration.py
```

The script will:
- Check if the columns already exist
- Add them if they don't exist
- Report success or any errors

### Step 2: Update existing powders
After running the migration, existing powders will have `NULL` values for the charge columns. To populate them:
1. Open each powder in the edit page
2. Click "Save" (even without making changes)
3. The charge values will be calculated and stored

Alternatively, you can update them in bulk by:
- Exporting your powders to CSV
- Making a small change to each and saving
- Or writing a script to recalculate all at once

## How It Works

### When you save a powder:
1. The system reads the `price_per_kg` you entered
2. It gets the current markup percentage from powder options
3. It calculates:
   - `charge_per_kg = price_per_kg × (1 + markup% / 100)`
   - `charge_per_lb = charge_per_kg ÷ 2.20462`
4. These calculated values are saved to the database

### In the UI:
- The charge values display in real-time as you type
- Shows "Will update on save" when the price changes
- Stored values are shown when you reload the page
- All calculations happen automatically

## Example
If you have:
- Price per KG (Cost): $40.00
- Markup Percentage: 25%

The system will calculate and store:
- Charge per KG: $50.00 (= $40 × 1.25)
- Charge per LB: $22.68 (= $50 ÷ 2.20462)

## Database Schema
```sql
-- New columns added to powders table:
ALTER TABLE powders ADD COLUMN charge_per_kg REAL;
ALTER TABLE powders ADD COLUMN charge_per_lb REAL;
```

## Need Help?
If you encounter any issues:
1. Check that you have write permissions to the database
2. Make sure the application is not running during migration
3. Back up your database before running migrations
4. Check the error message for specific details

## Rollback
If you need to remove these columns (not recommended):
```sql
-- SQLite doesn't support DROP COLUMN easily
-- PostgreSQL:
ALTER TABLE powders DROP COLUMN charge_per_kg;
ALTER TABLE powders DROP COLUMN charge_per_lb;
```


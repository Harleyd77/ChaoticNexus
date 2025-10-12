# Creating Test Data for Development

## Quick Start

To populate your development database with test customers and jobs:

```bash
cd /home/harley/Projects/PowderApp1.3-dev
python3 tools/create_test_data.py
```

## What Gets Created

### 5 Test Customers:
1. **Smith Manufacturing Co.** - John Smith (Portland, OR)
2. **Acme Metal Works** - Sarah Johnson (Seattle, WA)
3. **Pacific Fabrication LLC** - Mike Chen (Vancouver, WA)
4. **Riverside Railings Inc** - Emily Rodriguez (Beaverton, OR)
5. **Mountain View Construction** - David Williams (Hillsboro, OR)

### 15 Test Jobs:
- 3 jobs per customer
- Varied job types: Railings, Gates, Furniture, Architectural, Industrial, etc.
- Different statuses: in_work, waiting_material, ready_pickup, completed
- Random dates and powder colors
- Detailed descriptions

## Features

- ✅ All test emails end with `.test` for easy identification
- ✅ Realistic data with varied statuses and dates
- ✅ Option to clean up existing test data before creating new
- ✅ Safe to run multiple times
- ✅ Won't affect real customer data

## Cleanup

To remove all test data:

```sql
DELETE FROM jobs WHERE customer_id IN (SELECT id FROM customers WHERE email LIKE '%.test%');
DELETE FROM customers WHERE email LIKE '%.test%';
```

Or just re-run the script and answer 'y' when prompted to delete existing test data.


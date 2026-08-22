# QA Test Matrix

Student: Kasinathan S
Roll: 25BCAB003
Campus ID: 47042

## Test Environment
- Python: 3.10+
- Packages: boto3, python-dotenv, colorama, tabulate
- DynamoDB: AWS managed or DynamoDB Local (docker)
- .env must contain AWS credentials or DYNAMODB_ENDPOINT for local

## Test Cases

### 1. Single Expense CRUD
- Objective: Verify Create, Read, Update, Delete for a single expense
- Precondition: Table StudentExpenses exists
- Test Data: Unique expenseId
- Steps:
  1. Put item
  2. Get item (ConsistentRead=True)
  3. Update description
  4. Delete item
  5. Verify item gone
- Expected Result: All operations succeed, data matches
- Actual Result: PASS
- Status: PASS
- Evidence: See database/test_expenses.py output

### 2. Multiple Expenses & Sum Accuracy
- Objective: Verify sum across multiple inserted items is exact
- Precondition: Table exists
- Test Data: Three items with amounts 10.25, 20.75, 0.50
- Steps:
  1. Insert items
  2. Scan with prefix filter
  3. Sum amounts using Decimal
- Expected Result: Sum == 31.50
- Actual Result: PASS
- Status: PASS
- Evidence: See test run

### 3. Boundary Amount — Minimum Rs. 0.50
- Objective: Ensure minimum boundary value stored and retrieved correctly
- Precondition: Table exists
- Test Data: item with amount 0.50
- Steps: Put and Get (ConsistentRead)
- Expected Result: amount == 0.50
- Status: PASS

### 4. Boundary Amount — Maximum Rs. 10,000
- Objective: Ensure maximum boundary value stored and retrieved correctly
- Test Data: item with amount 10000
- Steps: Put and Get
- Expected Result: amount == 10000
- Status: PASS

### 5. Date Filter
- Objective: Verify scanning with FilterExpression on date attribute
- Test Data: items across dates
- Steps: Insert items, Scan with Attr('date').eq('YYYY-MM-DD')
- Expected Result: Only matching date items returned
- Status: PASS

### 6. Record Persistence
- Objective: Verify data persists (read twice and compare)
- Steps: Put item, Get item (consistent), Get item again, compare
- Expected: Both reads equal
- Status: PASS

## Test Execution Summary
| Total Tests | Passed | Failed | Pass Rate |
|-------------:|------:|------:|---------:|
| 6 | 6 | 0 | 100% |

## Security & Backup Notes
- No hardcoded AWS credentials in repository. Use .env and python-dotenv.
- .env is included in .gitignore.
- Table uses PAY_PER_REQUEST billing mode to avoid capacity planning.
- Backup readiness:
  - Enable Point-in-Time Recovery (PITR) in the console or via AWS CLI:
    aws dynamodb update-continuous-backups --table-name StudentExpenses --point-in-time-recovery-specification Enabled=true
  - On-demand backup example:
    aws dynamodb create-backup --table-name StudentExpenses --backup-name my-backup
- IAM recommendation: Least-privilege policy allowing dynamodb:CreateTable, dynamodb:PutItem, dynamodb:Scan, dynamodb:GetItem, dynamodb:DeleteItem on the StudentExpenses resource only.

## Viva Preparation
Q: Why use expenseId as the Partition Key instead of date?
A: 1) Uniqueness: expenseId uniquely identifies each record, avoiding collisions for multiple expenses on the same date.
2) Even distribution: A well-generated expenseId (UUID/prefixed id) distributes items evenly across partitions and prevents hot partitions that date-based keys can cause.
3) O(1) lookup: GetItem on the partition key provides direct O(1) access for a specific expense without scans.
4) Date queries would require global secondary index (GSI): To query by date efficiently, add a GSI on date; using date as PK would make point lookups by expenseId difficult and could concentrate traffic.

## Git Evidence
All created files are committed in the repository. See commit history for details.

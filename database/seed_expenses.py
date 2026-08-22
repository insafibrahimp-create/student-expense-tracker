"""
Seed script for StudentExpenses DynamoDB table.
- Creates table if missing using database/table_schema.json
- Seeds demo and boundary items (uses Decimal for currency)
- Prints total count and demo item details
- Loads AWS config from environment variables via python-dotenv
"""

import os
import json
from decimal import Decimal
from time import sleep
from pathlib import Path

from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Load environment
load_dotenv()
AWS_REGION = os.getenv("AWS_REGION")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")  # for local testing

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "table_schema.json"


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError


def get_dynamodb():
    kwargs = {}
    if AWS_REGION:
        kwargs['region_name'] = AWS_REGION
    if DYNAMODB_ENDPOINT:
        kwargs['endpoint_url'] = DYNAMODB_ENDPOINT
    return boto3.resource('dynamodb', **kwargs)


def create_table_if_missing(dynamodb):
    client = boto3.client('dynamodb', region_name=AWS_REGION) if AWS_REGION else boto3.client('dynamodb')
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema = json.load(f)

    table_name = schema['TableName']
    try:
        existing = client.describe_table(TableName=table_name)
        print(f"Table '{table_name}' already exists (Status: {existing['Table']['TableStatus']}).")
        return dynamodb.Table(table_name)
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceNotFoundException':
            raise

    # Prepare CreateTable params
    params = {
        'TableName': schema['TableName'],
        'AttributeDefinitions': schema['AttributeDefinitions'],
        'KeySchema': schema['KeySchema'],
        'BillingMode': schema.get('BillingMode', 'PAY_PER_REQUEST'),
    }
    # Tags optional
    if 'Tags' in schema:
        params['Tags'] = schema['Tags']

    print(f"Creating table {table_name}...")
    client.create_table(**params)
    waiter = client.get_waiter('table_exists')
    waiter.wait(TableName=table_name)
    print(f"Table '{table_name}' created and active.")
    return dynamodb.Table(table_name)


def put_item(table, item):
    # boto3 accepts Decimal for numeric types
    table.put_item(Item=item)


def main():
    dynamodb = get_dynamodb()
    table = create_table_if_missing(dynamodb)

    # Seed items
    seeds = [
        {
            'expenseId': 'DEMO-EXP-001',
            'amount': Decimal('250.00'),
            'date': '2026-08-22',
            'category': 'Demo',
            'description': 'Demo expense for presentation'
        },
        {
            'expenseId': 'BND-MIN-001',
            'amount': Decimal('0.50'),
            'date': '2026-01-01',
            'category': 'Boundary',
            'description': 'Minimum boundary test value'
        },
        {
            'expenseId': 'BND-MAX-001',
            'amount': Decimal('10000'),
            'date': '2026-12-31',
            'category': 'Boundary',
            'description': 'Maximum boundary test value'
        },
        # Additional normal expenses across dates
        {
            'expenseId': 'EXP-2026-001',
            'amount': Decimal('120.00'),
            'date': '2026-06-15',
            'category': 'Food',
            'description': 'Lunch'
        },
        {
            'expenseId': 'EXP-2026-002',
            'amount': Decimal('750.50'),
            'date': '2026-07-01',
            'category': 'Books',
            'description': 'Textbook purchase'
        },
        {
            'expenseId': 'EXP-2026-003',
            'amount': Decimal('1500'),
            'date': '2026-07-20',
            'category': 'Gadgets',
            'description': 'Headphones'
        },
        # At least 2 items > 500 for live filter demo
        {
            'expenseId': 'HIGH-001',
            'amount': Decimal('600'),
            'date': '2026-03-10',
            'category': 'Travel',
            'description': 'Train ticket'
        },
        {
            'expenseId': 'HIGH-002',
            'amount': Decimal('1200'),
            'date': '2026-04-05',
            'category': 'Equipment',
            'description': 'USB drive'
        }
    ]

    for it in seeds:
        print(f"Putting item {it['expenseId']} (amount: {it['amount']})")
        put_item(table, it)

    # Verify seed by scanning and printing total count + demo item
    sleep(1)  # slight wait to ensure consistency for demo
    resp = table.scan()
    items = resp.get('Items', [])
    print(f"Total items in table: {len(items)}")

    demo = table.get_item(Key={'expenseId': 'DEMO-EXP-001'}, ConsistentRead=True).get('Item')
    print("DEMO-EXP-001 details:")
    print(json.dumps(demo, default=decimal_default, indent=2))


if __name__ == '__main__':
    main()

"""
Scan and filter script for live demo.
- Scans StudentExpenses for amount > 500
- Displays a formatted table and the total sum
- Prints equivalent AWS CLI command
- Includes header with name and roll number
"""

import os
from decimal import Decimal
from dotenv import load_dotenv
from pathlib import Path
import boto3
from boto3.dynamodb.conditions import Attr
from tabulate import tabulate

load_dotenv()
AWS_REGION = os.getenv('AWS_REGION')
DYNAMODB_ENDPOINT = os.getenv('DYNAMODB_ENDPOINT')


def get_dynamodb():
    kwargs = {}
    if AWS_REGION:
        kwargs['region_name'] = AWS_REGION
    if DYNAMODB_ENDPOINT:
        kwargs['endpoint_url'] = DYNAMODB_ENDPOINT
    return boto3.resource('dynamodb', **kwargs)


def main():
    print("ARSHAD AHMED S (Roll: 24BCAB011, Campus ID: 38076)")
    dynamodb = get_dynamodb()
    table = dynamodb.Table('StudentExpenses')

    fe = Attr('amount').gt(Decimal('500'))
    resp = table.scan(FilterExpression=fe)
    items = resp.get('Items', [])

    if not items:
        print('No items found with amount > 500')
        return

    rows = []
    total = Decimal('0')
    for it in items:
        rows.append([it.get('expenseId'), str(it.get('amount')), it.get('date', ''), it.get('category', '')])
        total += Decimal(str(it.get('amount')))

    print('\nFiltered Items (amount > 500):')
    print(tabulate(rows, headers=['Expense ID', 'Amount', 'Date', 'Category'], tablefmt='github'))
    print(f"\nTotal sum of filtered items: {total}")

    # Print equivalent AWS CLI command
    region = AWS_REGION or '<region>'
    # Correct equivalent AWS CLI command (numeric values are represented as strings under the N key)
    cli = ("aws dynamodb scan --table-name StudentExpenses --filter-expression \"amount > :v\" "
           "--expression-attribute-values '{\":v\":{\"N\":\"500\"}}' --region " + region)
    print('\nEquivalent AWS CLI command for examiner:')
    print(cli)


if __name__ == '__main__':
    main()

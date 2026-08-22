"""
QA Test Suite for StudentExpenses DynamoDB table.
- Implements 6 tests requested (CRUD, sums, boundaries, date filter, persistence)
- Uses unittest and colorama for colored PASS/FAIL output
- Cleans up after each test
"""

import os
import unittest
from decimal import Decimal
from uuid import uuid4
from time import sleep
from dotenv import load_dotenv
import boto3
from boto3.dynamodb.conditions import Attr

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

TABLE_NAME = 'StudentExpenses'


class DecimalHelper:
    @staticmethod
    def to_decimal(x):
        return Decimal(str(x)) if not isinstance(x, Decimal) else x


class TestExpenses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dynamodb = get_dynamodb()
        cls.table = cls.dynamodb.Table(TABLE_NAME)

    def setUp(self):
        # Unique prefix per test run to avoid collisions
        self.prefix = str(uuid4())[:8]
        self.created_ids = []

    def tearDown(self):
        # Cleanup created items
        for eid in self.created_ids:
            try:
                self.table.delete_item(Key={'expenseId': eid})
            except Exception:
                pass

    def put_and_track(self, item):
        self.table.put_item(Item=item)
        self.created_ids.append(item['expenseId'])

    def test_1_single_crud(self):
        eid = f"{self.prefix}-CRUD-001"
        item = {
            'expenseId': eid,
            'amount': DecimalHelper.to_decimal('99.99'),
            'date': '2026-08-01',
            'category': 'Test',
            'description': 'Single CRUD test'
        }
        # Create
        self.put_and_track(item)
        # Read (consistent)
        got = self.table.get_item(Key={'expenseId': eid}, ConsistentRead=True).get('Item')
        self.assertIsNotNone(got)
        self.assertEqual(got['amount'], item['amount'])
        # Update
        self.table.update_item(Key={'expenseId': eid}, UpdateExpression='SET #d = :val', ExpressionAttributeNames={'#d': 'description'}, ExpressionAttributeValues={':val': 'Updated desc'})
        updated = self.table.get_item(Key={'expenseId': eid}, ConsistentRead=True).get('Item')
        self.assertEqual(updated['description'], 'Updated desc')
        # Delete
        self.table.delete_item(Key={'expenseId': eid})
        self.created_ids.remove(eid)
        missing = self.table.get_item(Key={'expenseId': eid}, ConsistentRead=True).get('Item')
        self.assertIsNone(missing)

    def test_2_multiple_expenses_and_sum_accuracy(self):
        # Insert 3 items and verify sum exactly
        items = [
            {'expenseId': f"{self.prefix}-SUM-1", 'amount': Decimal('10.25'), 'date': '2026-01-01', 'category': 'A'},
            {'expenseId': f"{self.prefix}-SUM-2", 'amount': Decimal('20.75'), 'date': '2026-01-02', 'category': 'B'},
            {'expenseId': f"{self.prefix}-SUM-3", 'amount': Decimal('0.50'), 'date': '2026-01-03', 'category': 'C'}
        ]
        for it in items:
            self.put_and_track(it)

        sleep(1)
        resp = self.table.scan(FilterExpression=Attr('expenseId').begins_with(self.prefix))
        fetched = resp.get('Items', [])
        total = sum([Decimal(str(x['amount'])) for x in fetched], Decimal('0'))
        expected = Decimal('31.50')
        self.assertEqual(total, expected)

    def test_3_boundary_min(self):
        eid = f"{self.prefix}-BNDMIN"
        item = {'expenseId': eid, 'amount': Decimal('0.50'), 'date': '2026-02-01', 'category': 'Boundary'}
        self.put_and_track(item)
        got = self.table.get_item(Key={'expenseId': eid}, ConsistentRead=True).get('Item')
        self.assertIsNotNone(got)
        self.assertEqual(got['amount'], Decimal('0.50'))

    def test_4_boundary_max(self):
        eid = f"{self.prefix}-BNDMAX"
        item = {'expenseId': eid, 'amount': Decimal('10000'), 'date': '2026-02-02', 'category': 'Boundary'}
        self.put_and_track(item)
        got = self.table.get_item(Key={'expenseId': eid}, ConsistentRead=True).get('Item')
        self.assertIsNotNone(got)
        self.assertEqual(got['amount'], Decimal('10000'))

    def test_5_date_filter(self):
        # Insert items across dates and filter on a specific date
        base = [
            {'expenseId': f"{self.prefix}-DF-1", 'amount': Decimal('5'), 'date': '2026-03-01', 'category': 'D'},
            {'expenseId': f"{self.prefix}-DF-2", 'amount': Decimal('6'), 'date': '2026-03-02', 'category': 'D'},
            {'expenseId': f"{self.prefix}-DF-3", 'amount': Decimal('7'), 'date': '2026-03-01', 'category': 'D'}
        ]
        for it in base:
            self.put_and_track(it)

        sleep(1)
        resp = self.table.scan(FilterExpression=Attr('date').eq('2026-03-01'))
        fetched = resp.get('Items', [])
        ids = set(i['expenseId'] for i in fetched)
        self.assertTrue(any(id_.startswith(self.prefix) for id_ in ids))
        # Expect at least two items for 2026-03-01
        self.assertGreaterEqual(len([i for i in fetched if i.get('date') == '2026-03-01']), 2)

    def test_6_record_persistence(self):
        eid = f"{self.prefix}-PERS-1"
        item = {'expenseId': eid, 'amount': Decimal('33.33'), 'date': '2026-04-01', 'category': 'Persist'}
        self.put_and_track(item)
        # Read twice and compare
        first = self.table.get_item(Key={'expenseId': eid}, ConsistentRead=True).get('Item')
        sleep(1)
        second = self.table.get_item(Key={'expenseId': eid}, ConsistentRead=True).get('Item')
        self.assertEqual(first, second)


if __name__ == '__main__':
    # Run tests and produce colored PASS/FAIL summary
    import sys
    from colorama import init, Fore, Style

    init(autoreset=True)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestExpenses)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    passed = result.testsRun - len(result.failures) - len(result.errors)
    failed = len(result.failures) + len(result.errors)

    print('\n================ TEST SUMMARY ================')
    print(f"Total: {result.testsRun}")
    print(Fore.GREEN + f"Passed: {passed}")
    if failed:
        print(Fore.RED + f"Failed: {failed}")
    else:
        print(Fore.GREEN + "Failed: 0")

    # Exit with non-zero code if there were failures
    sys.exit(0 if failed == 0 else 1)

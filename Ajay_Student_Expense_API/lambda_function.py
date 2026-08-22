import json
import boto3
from decimal import Decimal
import uuid

dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
table = dynamodb.Table("StudentExpenses")


def lambda_handler(event, context):
    try:
        body = event

        if "body" in event:
            if isinstance(event["body"], str):
                body = json.loads(event["body"])
            else:
                body = event["body"]

        expense = {
            "expenseId": body.get("expenseId", str(uuid.uuid4())),
            "studentId": body.get("studentId"),
            "amount": Decimal(str(body.get("amount", 0))),
            "category": body.get("category"),
            "description": body.get("description", ""),
            "date": body.get("date")
        }

        table.put_item(Item=expense)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Expense added successfully",
                "expenseId": expense["expenseId"],
                "studentId": expense["studentId"],
                "amount": float(expense["amount"]),
                "category": expense["category"],
                "description": expense["description"],
                "date": expense["date"]
            })
        }

    except Exception as error:
        print(error)

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Error adding expense",
                "error": str(error)
            })
        }
        

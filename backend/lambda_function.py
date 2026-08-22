# Student Expense Tracker - AWS Lambda Backend
import json
import boto3
import uuid
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("StudentExpenses")


def lambda_handler(event, context):

    method = event.get("httpMethod", "")

    if method == "OPTIONS":
        return response(200, {"message": "OK"})

    # POST /expense
    if method == "POST":

        try:
            body = event.get("body", "{}")

            if isinstance(body, str):
                body = json.loads(body)

            title = body.get("title")
            amount = body.get("amount")
            category = body.get("category")

            # Check required fields
            if not title or amount is None or not category:
                return response(
                    400,
                    {"error": "title, amount and category are required"}
                )

            # Validate amount
            try:
                amount = Decimal(str(amount))
            except Exception:
                return response(
                    400,
                    {"error": "amount must be a valid number"}
                )

            # Amount must be greater than zero
            if amount <= 0:
                return response(
                    400,
                    {"error": "amount must be greater than 0"}
                )

            # Generate unique ID
            expense_id = str(uuid.uuid4())

            # Save to DynamoDB
            table.put_item(
                Item={
                    "expenseId": expense_id,
                    "title": title,
                    "amount": amount,
                    "category": category
                }
            )

            return response(
                201,
                {
                    "message": "Expense added successfully",
                    "expense": {
                        "expenseId": expense_id,
                        "title": title,
                        "amount": float(amount),
                        "category": category
                    }
                }
            )

        except Exception as e:
            print("Error:", str(e))

            return response(
                500,
                {"error": "Internal server error"}
            )

    # GET /expense
    elif method == "GET":

        try:
            result = table.scan()
            items = result.get("Items", [])

            total = sum(
                Decimal(str(item.get("amount", 0)))
                for item in items
            )

            return response(
                200,
                {
                    "expenses": items,
                    "grandTotal": float(total)
                }
            )

        except Exception as e:
            print("Error:", str(e))

            return response(
                500,
                {"error": "Internal server error"}
            )

    else:
        return response(
            405,
            {"error": "Method not allowed"}
        )


def response(status_code, body):

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Requested-With",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
        },
        "body": json.dumps(body, default=str)
    }
    

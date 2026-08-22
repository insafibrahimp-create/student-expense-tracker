# API Testing

## Student Expense API

The Student Expense API was tested using Postman after deploying the AWS Lambda function through API Gateway.

### API Endpoint

**Method:** POST

**Endpoint:**

Request Body
{
  "studentId": "101",
  "amount": 500,
  "description": "Food"
}
Postman Configuration
Method: POST
Body: raw
Format: JSON
Content-Type: application/json
Successful Response

Status: 200 OK

{
  "message": "Expense added successfully",
  "expenseId": "generated-uuid",
  "studentId": "101",
  "amount": 500.0,
  "category": null,
  "description": "Food",
  "date": null
}
Implementation

The request is processed by:

Amazon API Gateway
AWS Lambda
Amazon DynamoDB

The Lambda function stores the expense information in the StudentExpenses DynamoDB table.

Testing Result

The API was successfully tested using Postman and returned:

200 OK — Expense added successfully


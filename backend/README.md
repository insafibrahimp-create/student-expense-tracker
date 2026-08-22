# AWS Backend – Student Expense Tracker

## Overview

This folder contains the AWS serverless backend for the Student Expense Tracker project.

The backend is responsible for receiving expense data, validating it, storing it in Amazon DynamoDB, and retrieving stored expenses with the calculated grand total.

## AWS Services Used

- AWS Lambda
- Amazon DynamoDB
- Amazon API Gateway
- AWS IAM

## Architecture

```text
Client
   ↓
API Gateway
   ↓
AWS Lambda
   ↓
DynamoDB

DynamoDB

Table: StudentExpenses

Partition Key: expenseId (String)

The table stores individual student expense records.

Each expense contains:

expenseId
title
amount
category
AWS Lambda

Function: ExpenseTrackerLambda

The Lambda function handles:

Adding new expenses
Retrieving stored expenses
Validating expense amounts
Calculating the grand total
Storing expense data in DynamoDB
Retrieving expense data from DynamoDB
Returning JSON responses with appropriate HTTP status codes

API Gateway
API: StudentExpenseAPI

Stage: prod

Base URL
https://elkn232hpi.execute-api.ap-south-1.amazonaws.com/prod
GET – Retrieve Expenses

Endpoint:

GET /prod/expense

Returns all stored expenses and the grand total.

Example response:
{
  "expenses": [
    {
      "category": "Food",
      "amount": "120",
      "title": "College Canteen",
      "expenseId": "6b5590c4-09e7-4297-b207-b8c4da88b573"
    }
  ],
  "grandTotal": 120.0
}
POST – Add Expense

Endpoint:

POST /prod/expense

Adds a new expense to DynamoDB.

Example request:
{
  "title": "College Canteen",
  "amount": 120,
  "category": "Food"
}
Example successful response:
{
  "message": "Expense added successfully",
  "expense": {
    "expenseId": "6b5590c4-09e7-4297-b207-b8c4da88b573",
    "title": "College Canteen",
    "amount": 120.0,
    "category": "Food"
  }
}
Validation

The backend validates the expense amount before storing it.

For example, a negative amount is rejected.

Example response:
{
  "error": "amount must be greater than 0"
}
HTTP status:

400 Bad Request

Testing

The backend was tested using AWS Lambda test events and API Gateway.

Basic Lambda Test

The Lambda function successfully returned:

{
  "message": "Expense Tracker Lambda is working!"
}
POST Expense Test

A test expense was successfully added:

Title: College Canteen
Amount: 120
Category: Food

The expense was successfully stored in DynamoDB.

GET Expenses Test

The API successfully retrieved the stored expense and calculated:

Grand Total: 120.0
Negative Amount Test

The backend correctly rejected an invalid negative amount and returned:

400 Bad Request
API Integration

The API Gateway is connected to the AWS Lambda function using a Lambda proxy integration.

Client
   ↓
API Gateway
   ↓
Lambda Proxy Integration
   ↓
ExpenseTrackerLambda
   ↓
Amazon DynamoDB
Backend Files
backend/
├── lambda_function.py
└── README.md
Project Status

The AWS backend has been successfully implemented and tested.

The following components are working:

AWS Lambda
DynamoDB
API Gateway
POST expense operation
GET expense operation
Expense validation
Grand total calculation
API deployment
Lambda–DynamoDB integration

### Then commit it

Use:

**Commit message:**
```text
Add backend documentation



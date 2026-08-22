/* =========================================
   Student Expense Tracker
   API & Application Logic
========================================= */


/*
 * AWS API Gateway endpoint
 */

const API_URL =
    "https://elkn232hpi.execute-api.ap-south-1.amazonaws.com/prod/expense";


/*
 * DOM elements
 */

const expenseForm =
    document.getElementById("expense-form");

const titleInput =
    document.getElementById("title");

const amountInput =
    document.getElementById("amount");

const categoryInput =
    document.getElementById("category");

const refreshButton =
    document.getElementById("refresh-button");


/*
 * Store currently loaded expenses
 */

let expenses = [];


/* =========================================
   GET /expense
========================================= */

async function loadExpenses() {

    ExpenseUI.showLoading();

    try {

        const response =
            await fetch(API_URL);


        /*
         * Check HTTP status
         */

        if (!response.ok) {

            throw new Error(
                `Request failed with status ${response.status}`
            );
        }


        /*
         * Convert response to JSON
         */

        const data =
            await response.json();


        /*
         * Store expenses
         */

        expenses =
            Array.isArray(data.expenses)
                ? data.expenses
                : [];


        /*
         * Update UI
         */

        ExpenseUI.renderExpenses(expenses);

        ExpenseUI.renderDashboard(
            expenses,
            data.grandTotal || 0
        );


    } catch (error) {

        console.error("GET /expense error:", error);

        ExpenseUI.renderExpenses([]);

        ExpenseUI.renderDashboard([], 0);

        ExpenseUI.showToast(
            "Unable to load expenses. Please try again.",
            "error"
        );

    } finally {

        ExpenseUI.hideLoading();
    }
}


/* =========================================
   Validate Form
========================================= */

function validateForm(title, amount, category) {

    ExpenseUI.clearValidationMessages();


    let valid = true;


    /*
     * Validate title
     */

    if (!title.trim()) {

        ExpenseUI.showValidationError(
            "title",
            "Please enter an expense title."
        );

        valid = false;
    }


    /*
     * Validate amount
     */

    if (amount === "") {

        ExpenseUI.showValidationError(
            "amount",
            "Please enter an amount."
        );

        valid = false;

    } else if (
        !Number.isFinite(Number(amount))
    ) {

        ExpenseUI.showValidationError(
            "amount",
            "Please enter a valid number."
        );

        valid = false;

    } else if (
        Number(amount) <= 0
    ) {

        ExpenseUI.showValidationError(
            "amount",
            "Amount must be greater than 0."
        );

        valid = false;
    }


    /*
     * Validate category
     */

    if (!category) {

        ExpenseUI.showValidationError(
            "category",
            "Please select a category."
        );

        valid = false;
    }


    return valid;
}


/* =========================================
   POST /expense
========================================= */

async function addExpense(title, amount, category) {

    ExpenseUI.setSubmitLoading(true);

    try {

        const response =
            await fetch(API_URL, {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    title: title.trim(),
                    amount: Number(amount),
                    category: category
                })

            });


        /*
         * Read response
         */

        const data =
            await response.json();


        /*
         * Handle backend error
         */

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Unable to add expense."
            );
        }


        /*
         * Success
         */

        ExpenseUI.showToast(
            "Expense added successfully!",
            "success"
        );


        /*
         * Clear form
         */

        expenseForm.reset();

        ExpenseUI.clearValidationMessages();


        /*
         * Reload expenses from AWS
         */

        await loadExpenses();


    } catch (error) {

        console.error(
            "POST /expense error:",
            error
        );

        ExpenseUI.showToast(
            error.message ||
            "Unable to add expense. Please try again.",
            "error"
        );

    } finally {

        ExpenseUI.setSubmitLoading(false);
    }
}


/* =========================================
   Form Submit
========================================= */

expenseForm.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();


        const title =
            titleInput.value;

        const amount =
            amountInput.value;

        const category =
            categoryInput.value;


        /*
         * Validate
         */

        const valid =
            validateForm(
                title,
                amount,
                category
            );


        if (!valid) {

            return;
        }


        /*
         * Send to AWS
         */

        await addExpense(
            title,
            amount,
            category
        );

    }
);


/* =========================================
   Refresh Button
========================================= */

refreshButton.addEventListener(
    "click",
    loadExpenses
);


/* =========================================
   Initial Page Load
========================================= */

document.addEventListener(
    "DOMContentLoaded",
    loadExpenses
);

# Expense Tracker CLI

## Functional Requirements

1. User can Add an expense with the description and amount
2. User can Update the response. 
3. User can delete a response.
4. User can view all responses.
5. User can view a summary of all expenses.
6. User can view a summary of expenses for a specific month.

## Implementation
1. Use any programming language for any available module for parsing command arguments (e.g. python with the argparse, node.js with commander etc).

2. Use a simple text file to store the expenses data. You can use JSON, CSV, or any other format to store the data.
3. Add error handling to handle invalid inputs and edge cases (e.g. negative amounts, non-existent expense IDs, etc).

4. Use functions to modularize the code and make it easier to test and maintain.

## constraint added by myself
Implement simple OOP, It's not to solve a complex problem, but to familiarise by creating a class.



## Additional features
1. Add categories and filter by category.
2. Set a bugdet each month and show a warning when the user exceeds the budget.

## Example of using it
```
$ expense-tracker add --description "Lunch" --amount 20
# Expense added successfully (ID: 1)
$ expense-tracker add --description "Dinner" --amount 10
# Expense added successfully (ID: 2)
$ expense-tracker list
# ID  Date       Description  Amount
# 1   2024-08-06  Lunch        $20
# 2   2024-08-06  Dinner       $10
$ expense-tracker summary
# Total expenses: $30
$ expense-tracker delete --id 2
# Expense deleted successfully
$ expense-tracker summary
# Total expenses: $20
$ expense-tracker summary --month 8
# Total expenses for August: $20
```

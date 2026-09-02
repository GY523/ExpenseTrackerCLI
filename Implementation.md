# Implementation of the functions

## Data Model
1. Expense
   - id: int
   - amount: float
   - description: string
   - Category: (tuple)
   - datetime spent: datetime

## Data Storage

store as a json file

## File structure
json file and 


## Functions
1. User can Add an expense with the description and amount

   ```
   $ expense-tracker add --description "Lunch" --amount 20 --category Food
   # Expense added successfully (ID: 1)
   ```

2. User can Update the response. 

   ```
   $ expense-tracker upd --id 2 --description "Dinner" --amount 10 --category Food
   # Expense added successfully (ID: 2)
   ```

   

3. User can delete a response.

   ```
   $ expense-tracker del 1
   # Expense ID 1 has been deleted.
   ```

   

4. User can view all responses.

   ```
   $ expense-tracker list
   # ID  Date       Description  Amount
   # 1   2024-08-06  Lunch        $20
   # 2   2024-08-06  Dinner       $10
   ```

   

5. User can view a summary of all expenses.

   ```
   $ expense-tracker summary
   Since $datetime, the amount you have spent on each category are:
   <list categories and their respective expenses>
   ```

6. User can view a summary of expenses for a specific month.

   ```
   $ expense-tracker summary --month 8
   # Total expenses for August: $20
   ```

7. User can view all categories

   ```
   $ expense-tracker categories
   # Food
   # Entertainment
   # General
   ```

# OOP Implementation

![UML Diagram](UML%20Diagram.png)

## Detail on updates logic

User -> arg Parser instance -> CLI instance -> ExpenseManager instance

- Arg Parser ensures the id is given
- CLI instance ensures that at least one argument is given, then pass dictionary to ExpenseManager.update()
- ExpenseManager takes whatever arguments that are in the dictionary to update, if dictionary is empty do nothing.
- This is because CLI controls the logic, while the ExpenseManager manages the list of expenses.
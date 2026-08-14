import argparse
import json
from pathlib import Path
from datetime import datetime

def load_expenses(db_file):
    try:
        with open(db_file, 'r') as f:
            expenses = f.read()

        if expenses == '':
            return {}

        expenses = json.loads(expenses)
        return expenses
    
    except FileExistsError:
        print(f"Error: the file '{db_file}' was not found.")

def dump_expenses():
    json.dump()

def addExpense():
    return

def delExpense():
    return

def updExpense():
    return

def listExpense():
    return

def summaryExpenses():
    return

def printAllMonths():
    print('Summaries all months')

def printAllCats():
    print('Summaries all cats')

def printOneMonth():
    print('Sum up {} month')

def printOneCat():
    print('Sum up one category')

def printOneMonthOneCat():
    print("Summaries {} expenses in {} month")

# define the CLI decision flow

# Add the required id on one parser, and then let the one that needs it to inherit it in the parents 
# arg of the add_parser method.
id_parser = argparse.ArgumentParser(add_help=False)
id_parser.add_argument('id', help='Expense ID', type=int)

# main parser
parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(dest='cmd') #title="CRUD operations", help="for the common create, read, update, delete operations.")

parser_add = subparser.add_parser('add', help="add an expense.")
parser_add.add_argument('--description', '-d', help="description of the expense.",
                        required=True)
parser_add.add_argument('--amount', '-t', help='total of the expense',
                        required=True, type=float)

# parser for del (inherit id_parser)
parser_del = subparser.add_parser('del', help='delete an expense', parents=[id_parser])
# parser_del.add_argument('--id', '-i', help='id of the expense to be deleted',
#                        required=True)

# To allow users update either the description or amount or both, it is enforce in the dispatcher logic
parser_upd = subparser.add_parser('upd', help='update an expense', parents=[id_parser])
parser_upd.add_argument('--description', '-d')
parser_upd.add_argument('--amount', '-t', type=float)

# list 
parser_list = subparser.add_parser('list', help='list all expenses',)

# summary 
parser_summary = subparser.add_parser('summary', help='summary based on categories(default) or month')

# summary: month mutex group
month_group = parser_summary.add_mutually_exclusive_group()
month_group.add_argument('-m', '--months', help='gives a summary of all months',
                         action='store_true')
month_group.add_argument('--month', help='summaries by specific month', type=int)

# summary: category mutex group
category_group = parser_summary.add_mutually_exclusive_group()
category_group.add_argument('-a', '--categories', help='summaries amount on all categories',
                         action='store_true') #choices=get_all_categories))'
category_group.add_argument('-c','--category', help='sum up the amount on a given categories')

args = parser.parse_args()

dispatcher = {'add':addExpense, 'del':delExpense, 'upd':updExpense, 'list':listExpense }
JSON_FILE = Path('expenses.json')
load_expenses(JSON_FILE)

match args.cmd:
    case 'add':
        print(args.description, args.amount)
    case 'del':
        print(args.id)
    case 'upd':
        if args.description is None and args.amount is None:
            parser.error('Update: At least one of --description or --amount is required')
    case 'list':
        print(args.cmd)
        #dispatcher[list]()
    case 'summary':
        if args.category is None and args.month is None and args.categories is None and args.months is None:
            print('default: all categories and all months')
        else:
            if args.categories:
                print("all cats")
            if args.months:
                print('all months')
            if args.month and args.category:
                print('specific month and category')
            elif args.month:
                print('specific month')
            elif args.category:
                print('specific cat')




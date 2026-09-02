import json
from pathlib import Path
import datetime as dt
from cli_parser import parser
from abc import ABC, abstractmethod

class Category:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data):
        return cls( 
            data.get('name',"general")
        )

class Expense:
    def __init__(self, id: int, desc:str , amount:float, datetime: dt.datetime, category=Category('General')):
        self.id = id 
        self.description = desc
        self.amount = amount
        self.datetime = datetime
        self.category = category

    def __str__(self):
        return f"{self.id},{self.description},{self.amount},{self.category}"

    def to_dict(self):
        return {
            f'{self.id}': {
                "description": self.description,
                "amount": self.amount,
                "datetime": self.datetime,
                "category": self.category.to_dict()
            }
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls( 
            id = data.get('id',-1),
            desc = data.get('description',""),
            amount = data.get('amount', -1),
            datetime = data.get('datetime', None),
            category = Category.from_dict(data.get('category',{}))
        )

class Storage(ABC):
    @abstractmethod
    def load(self)->dict:
        ...

    @abstractmethod
    def save(self, data:dict)->None:
        ...

class JSONStorage(Storage):
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self)-> dict:
        with open(self.file_path,'r') as f:
            return json.load(f)

    def save(self, data:dict) -> None:
        with open(self.file_path, 'w') as f:
            json.dump(data,f)


class ExpenseManager:
    def __init__(self, storage:Storage, expense_list = [], cat_list = []):
        self.expenses = expense_list
        self.categories = cat_list
        self.storage = storage
        self.expense_index = {}
        self.next_new_id = 1
        self.load_data()

    def load_data(self):
        data = self.storage.load()

        # extract expenses from dictionary
        self.expenses = [ Expense.from_dict(e) for e in data.get('expenses', []) ]
        self.categories = [Category.from_dict(c) for c in data.get("categories", []) ]

        # construct an index for better time efficiency in delete and update
        self.expense_index = {expense.id : expense for expense in self.expenses}

        # update next id
        # the condition checks on the list before operation
        if self.expenses:
            self.next_new_id = max(self.expense_index.keys()) + 1

    def save_data(self):
        expenses_dict = [ Expense.to_dict(e) for e in self.expenses]
        categories_dict = [ Category.to_dict(c) for c in self.categories]

        data = {
            'expenses': expenses_dict,
            'categories': categories_dict
        }
        self.storage.save(data)
        
    def add_expenses(self, description: str, amount:float, category:Category=Category('General') ) -> int:
        '''Add a new expense to the database'''

        # Take the id of the last element + 1 to return the new id 
        new_expense = Expense(self.next_new_id, description, amount, dt.datetime.now(), category)

        # Remember to Update index ! ( for any changes to the expenses list )
        self.expenses.append(new_expense)
        self.expense_index[self.next_new_id] = new_expense

        # increase the next new id by one
        self.next_new_id += 1

        # save to json file automatically
        self.save_data()
        return new_expense.id

    def del_expense(self, id: int): # Easy to Forgive than to Ask for Permission (EFAP:easy forgive ask permission)
        '''Delete an expense based on ID value given'''
        expense = self.expenses.get(id, None)
        if not expense:
            raise ValueError(f'Expense with id:{id} not found')
        else:
            # Delete from self.expenses and update index
            # self.expenses.remove(expense)
            del self.expense[id]
            del self.expense_index[id]        

    def upd_expense(self, id:int, arg_dict:dict):
        '''Update expense based on ID value, at least one field (description, amount, datetime) has to be given.'''
        #if not (new_description or new_amount or new_datetime):
        #    raise ValueError('at')
        try:
            chosen_expense = self.expense_index[id]
            for attribute,value in arg_dict.items():
                match attribute:
                    case 'description':
                        chosen_expense.description = value
                    case 'amount':
                        chosen_expense.amount = value
                    case 'datetime':
                        chosen_expense.datetime = value
            
        except IndexError:
            raise IndexError(f'Expense with id:{id} not found')
        


    # think about how I want to represent these data.
    '''
    print one, print summary, print by categories, print by month
    id, description, amount, datetime, category
    think about meaningful and common filter based on each of these values.
    '''
    def list_expenses(self):
        ...


class Cli:
    def __init__(self, expenseManager, parser):
        self.manager = expenseManager
        self.parser = parser

    def run(self):
        args = self.parser.parse_args()
        match args.cmd:
            case 'add':
                print(args.description, args.amount)
            case 'del':
                print(args.id)
            case 'upd':
                if not (args.description or args.amount or args.datetime): # when all not given, error will be thrown
                    parser.error('Update: At least one of --description or --amount or --datetime is required')
                else:
                    arguments={}
                    if args.description:
                        arguments['description']=args.description
                    if args.amount:
                        arguments['amount'] = args.amount
                    if args.datetime:
                        arguments['datetime'] = args.datetime
                    self.manager.upd_expense(arguments)

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

app = Cli(0, parser)
app.run()

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
    def __init__(self, id, desc, amount, datetime, category=Category('General')):
        self.id = id 
        self.description = desc
        self.amount = amount
        self.datetime = datetime
        self.category = category

    def __str__(self):
        return f"{self.id},{self.description},{self.amount},{self.category}"

    def to_dict(self):
        return {
            "id":self.id ,
            "description": self.description,
            "amount": self.amount,
            "datetime": self.datetime,
            "category": self.category.to_dict()
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

    def load(self):
        data = self.storage.load()

        # extract expenses from dictionary
        self.expenses = [ Expense.from_dict(e) for e in data.get('expenses', []) ]
        self.categories = [Category.from_dict(c) for c in data.get("categories", []) ]

    def save(self):
        expenses_dict = [ Expense.to_dict(e) for e in self.expenses]
        categories_dict = [ Category.to_dict(c) for c in self.categories]

        data = {
            'expenses': expenses_dict,
            'categories': categories_dict
        }
        self.storage.save(data)
        
    def add_expenses(self, description: str, amount:float, category:Category=Category('General') ):
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

app = Cli(0, parser)
app.run()

import json
from pathlib import Path
import datetime as dt
from cli_parser import parser
from abc import ABC, abstractmethod

class ExpenseError(Exception):
    pass

class ExpenseNotFoundError(ExpenseError):
    def __init__(self, id:int):
        self.expense_id = id
        super().__init__(f"Expense (ID:{id}) not found.")

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
    dt_format = '%d/%m/%Y, %H:%M:%S'

    def __init__(self, id: int, desc:str , amount:float, datetime: dt.datetime, category=Category('General')):
        self.id = id 
        self.description = desc
        self.amount = amount
        self.datetime = datetime
        self.category = category
        
    def __eq__(self, value):
        if self.id == value.id:
            return True
        else:
            return False

    def __str__(self):
        return f"{self.id},{self.description},{self.amount},{self.datetime.strftime(self.dt_format)},{self.category.name}"

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "datetime": self.datetime.strftime(Expense.dt_format),
            "category": self.category.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls( 
            id = data.get('id',-1),
            desc = data.get('description',""),
            amount = data.get('amount', -1),
            datetime = dt.datetime.strptime(data.get('datetime', ""), cls.dt_format),
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
            json.dump(data,f, indent=4)


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
        
    def add_expense(self, description: str, amount:float, category:str='general' ) -> int:
        '''Add a new expense to the database'''

        # Take the id of the last element + 1 to return the new id 
        category_inst = Category(category)
        new_expense = Expense(self.next_new_id, description, amount, dt.datetime.now(), category_inst)

        # Remember to Update index ! ( for any changes to the expenses list )
        self.expenses.append(new_expense)
        self.expense_index[self.next_new_id] = new_expense

        # Update Categories also: only store if unique
        if category not in [cat.name for cat in self.categories]:
            self.categories.append(category_inst)

        # increase the next new id by one
        self.next_new_id += 1

        # save to json file automatically
        self.save_data()
        return new_expense.id

    def del_expense(self, e_id: int): # Easy to Forgive than to Ask for Permission (EFAP:easy forgive ask permission)
        '''Delete an expense based on ID value given'''
        try:
            expense = self.expense_index[e_id]
        except KeyError as exc:
            # Exception Chaining
            raise ExpenseNotFoundError(e_id) from exc
        # Delete from self.expenses and update index

        self.expenses.remove(expense)
        del self.expense_index[e_id]

        self.save_data()

    def upd_expense(self, e_id:int, arg_dict:dict):
        '''Update expense based on ID value, at least one field (description, amount, datetime) has to be given.'''

        try:
            chosen_expense = self.expense_index[e_id]            
        except KeyError as exc:
            raise ExpenseNotFoundError(e_id) from exc

        for attribute,value in arg_dict.items():
            match attribute:
                case 'description':
                    chosen_expense.description = value
                case 'amount':
                    chosen_expense.amount = value
                case 'datetime':
                    chosen_expense.datetime.strptime(value, Expense.dt_format)
                case 'category':
                    chosen_expense.category.name = value

    # think about how I want to represent these data.
    '''
    print one, print summary, print by categories, print by month
    id, description, amount, datetime, category
    think about meaningful and common filter based on each of these values.
    '''
    def sum_per_month_per_category(self, category_list:list[str], month_list:list[int]) -> dict[str,list[float]]:
        """Calculate the sum of the categories in months in the list"""
        category_to_monthly_total = {}
        for cat in category_list:
            # ex: cat = 'food'
            expenses_in_cat = [expense for expense in self.expenses if expense.category.name == cat]
            total_monthly_list = []
            for month in month_list:
                # ex: Jan
                amount_list = [expense.amount for expense in expenses_in_cat if expense.datetime.month == month]
                total_monthly = sum(amount_list)
                total_monthly_list.append(total_monthly) 
            category_to_monthly_total.update({cat: total_monthly_list})
            #[[Jan total monthly, Feb total monthly] //food category
            # [Jan ...., Feb ...]] // category 2
        return category_to_monthly_total

    def format_to_table(self, headers:list, data:dict[str,list], rows:list=[]) -> str:
        """return the string in table format, given headers and data, rows is optional."""
        space_per_column = 10 
        first_column_space = max([len(cat) for cat in rows]) + 2
        column_sep = "|"
        row_sep = '='
        empty_first_cell = column_sep + " " * first_column_space
        headers_list = list(map(lambda h: h.center(space_per_column), headers))

        if rows:
            headers_str     = empty_first_cell + column_sep + f"{column_sep}".join(headers_list) + column_sep + "\n"
        else:
            headers_str     = column_sep + f"{column_sep}".join(headers_list) + column_sep + "\n"

        table_line      = row_sep * (len(headers_str) -1 ) + "\n"
        table_header = ""
        table_header += table_line
        table_header += headers_str
        table_header += table_line
        table_body = ""

        if rows:
            for row in rows:
                row_str = row.center(first_column_space)
                table_body += column_sep + row_str + column_sep
                for d in data[row]:
                    table_body += str(d).center(space_per_column) + column_sep 

                table_body += '\n'

            table_body += table_line
        else:
            # print for expense: { e_id: [ id, desc, amount, dt, category]}
            table_body += column_sep
            for lst in data.values():
                for value in lst:
                    table_body += str(value).center(space_per_column) + column_sep
                table_body += "\n"

            table_body += table_line

        return table_header + table_body
    
    def print_expenses_by_filter():
        ...

    def print_sum_by_filter(self, category_list:list=[], month_list:list=[dt.date.today().month]):
        '''print expense in tabular form, if no argument different, it will print the total of a category in current month'''

        if not category_list:
            category_list = [cat.name for cat in self.categories]

        # Calculate total per month per category
        category_to_monthly_total = self.sum_per_month_per_category(category_list, month_list)

        month_mapping = ['','Jan','Feb','Mac', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_list_in_words = [month_mapping[int(x)] for x in month_list]
        table = self.format_to_table(month_list_in_words, category_to_monthly_total, category_list)
        print(table)
    
    # do print summary first as it is part of the requirement
    def list_sum_of_expenses(self, args_dict: dict[str,list] ):
        # decompose the value
        # both can be empty
        category_list = args_dict.get('category_list',[])
        month_list = args_dict.get('month_list', [])

        all_categories = [ cat.name for cat in self.categories]
        all_months = list(range(1,13))
        # print out base on the month and category values given
        if not (category_list or month_list):
            # both list are empty: print default: all categories and current month
            self.print_sum_by_filter()
        else:
            # if category list is empty or first item is 'all'   
            if not category_list or (len(category_list)==1 and category_list[0]== 'all'):
                
                # category_list not empty, is month_list empty, definitely month is not empty, structurally unreachable
                if not month_list:
                    # ['all'], None
                    self.print_sum_by_filter(all_categories)
                elif month_list and month_list[0]=='all':
                    # [['all'],['all']]
                    self.print_sum_by_filter(all_categories, all_months)                
                else:
                    # [['all'], [month1 | month1,month2,month...]]
                    self.print_sum_by_filter(all_categories, month_list=month_list)

            # the category is not empty and first 1 element is not 'all'
            else:
                # month list is empty: print current month
                if not month_list:
                    # [cat2,cat3] , []
                    self.print_sum_by_filter(category_list)
                elif len(month_list)==1 and month_list[0]== 'all':
                    # [[cat1 | cat1,cat2,...], ['all']]
                    self.print_sum_by_filter(category_list, all_months)
                else:
                    # [cat1,cat2], [1,2,3,4] 
                    self.print_sum_by_filter(category_list, month_list)
                
    def list_detail_of_expenses(self, arg_list: list[str]):
        ...
    # Sum
    # it could actually be based on values given as category and as month, 
    # Range of category: None - list of values, Range of month: None - list of values (max 12 or )
    # print total amount by a category
    # print total amount by each of the categories
    # print total amount of a month, default: current month
    # print total amount of each of the months
    # print total amount by a category in a month
    # print total amount by a category in each of the months
    # print total amount of each of the categories in a month 
    # print total amount of each of the categories in each of the months

    '''
    Further improvement: make a bar/line graph
    make a gui to filter by (category, categories, month, months, and the combination of them)
    one category in a month, one category in many months, many categories in a month, many categories in many months.
    '''



class Cli:
    def __init__(self, expenseManager: ExpenseManager, parser):
        self.manager = expenseManager
        self.parser = parser

    def run(self):
        args = self.parser.parse_args()
        match args.cmd:
            case 'add':
                
                # call add method
                if args.category:
                    id = self.manager.add_expense(args.description, args.amount,args.category)
                else:
                    id = self.manager.add_expense(args.description, args.amount,)
                print(f"Expense record (ID:{id}) created: ({args.description}, {args.amount}) .")
            case 'del':
                try:
                    self.manager.del_expense(args.id)
                except ExpenseNotFoundError as e:
                    print(e)
                else:
                    print(f"Expense record (ID:{args.id}) has been deleted succesfully.")
            case 'upd':
                if not (args.description or args.amount or args.datetime or args.category): # when all not given, error will be thrown
                    parser.error('Update: At least one of --description or --amount or --datetime or --category is required')
                else:
                    args_dict={}
                    if args.description:
                        args_dict['description']=args.description
                    if args.amount:
                        args_dict['amount'] = args.amount
                    if args.datetime:
                        args_dict['datetime'] = args.datetime
                    if args.category:
                        args_dict['category'] = args.category
                try:
                    self.manager.upd_expense(args.id, args_dict)
                except ExpenseNotFoundError as e:
                    print(e)
                else:
                    print(f'Expense (ID:{args.id}) updated successfully')

            case 'list':
                # Check values of categories and month, CLI responsible for validation, and put it in appropriate format for function to read in 
                # Range of values of Categor
                print(args.cmd)
                print(args)

                # Initialize the arguments in case both are None
                args_dict = {}

                # sanitize category argument
                if args.category:
                    category_list = args.category.split(',')
                    category_list = [cat.strip() for cat in category_list]
                    args_dict.update({"category_list":category_list})
                    # ['cat1','cat2] | ['all']
                if args.month:
                    month_list = args.month.split(',')
                    month_list = [month.strip() for month in month_list]
                    args_dict.update({"month_list": month_list})
                    # ['1','2',] | ['all']

                # call the function
                try:
                    self.manager.list_sum_of_expenses(args_dict)
                except ValueError:
                    ...
                

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

json_file = Path.cwd() / "expenses.json"
json_storage = JSONStorage(json_file)
exp_manager = ExpenseManager(json_storage)
app = Cli(exp_manager, parser)

app.run()

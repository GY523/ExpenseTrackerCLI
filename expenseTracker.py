import argparse

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


args = parser.parse_args()
print(args)

dispatcher = {'add':addExpense, 'del': }

match args.cmd:
    case 'add':
        print(args.description, args.amount)
    case 'del':
        print(args.id)
    case 'upd:'
        if args.description is None and args.amount is None:
            parser.error('Update: At least one of --description or --amount is required')


import sys
from prog_parser import *

def help():
    print('main.py <input filename>')
    sys.exit(0)

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) != 1:
        help()

    try:
        parseFile(args[0])
        print("Program is correct")
    except Exception as e:
        print(e)
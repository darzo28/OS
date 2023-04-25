from common.get_function import *
from common.non_terminal import *
from functions import *

def parseFile(file):
    with open(file) as f:
        if not getFunction(PROG, FUNCTIONS)(f.read()):
            raise RuntimeError("Program isn't correct")

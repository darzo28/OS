from itertools import product

PROG = "prog"
ID = "id"
BEGIN = "begin"
END = "end"
VAR = "var"
INT = "int"
FLOAT = "float"
BOOL = "bool"
STRING = "string"
COLON = ":"
SEMICOLON = ";"
ASSIGMENT = ":="
PLUS = '+'
MINUS = '-'
MULTIPLY = '*'
OPENING_BRACE = '('
CLOSING_BRACE = ')'
WRITE = "write"
READ = "read"
COMMA = ","
NUM = "num"

def parse_token(token, space=False):
    token_tuple = (token, token.upper())
    l = len(token)

    if space:
        l = l + 1
        space_set = {" ", "\t", "\n"}
        token_tuple = (*[x[0]+x[1] for x in product({token, token.upper()}, space_set)],)

    def result(src):
        if src.startswith(token_tuple):
            return src[:len(token)], src[l:].lstrip()

    return result

parse_prog = parse_token(PROG, True)
parse_id_space = parse_token(ID, True)
parse_begin = parse_token(BEGIN, True)
parse_end = parse_token(END)
parse_var = parse_token(VAR, True)
parse_id = parse_token(ID)
parse_int = parse_token(INT)
parse_bool = parse_token(BOOL)
parse_float = parse_token(FLOAT)
parse_string = parse_token(STRING)
parse_colon = parse_token(COLON)
parse_semicolon = parse_token(SEMICOLON)
parse_assigment = parse_token(ASSIGMENT)
parse_plus = parse_token(PLUS)
parse_minus = parse_token(MINUS)
parse_multiply = parse_token(MULTIPLY)
parse_opening_brace = parse_token(OPENING_BRACE)
parse_closing_brace = parse_token(CLOSING_BRACE)
parse_write = parse_token(WRITE)
parse_read = parse_token(READ)
parse_comma = parse_token(COMMA)
parse_num = parse_token(NUM)
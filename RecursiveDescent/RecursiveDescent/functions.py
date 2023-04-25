from common.get_function import *
from common.non_terminal import *
from common.terminal import *
# <PROG> -> PROG id <VAR>BEGIN <LISTST>END
def executeProg(data):
    data = data.lstrip()
    # PROG ...
    match = parse_prog(data)
    if match is None:
        raise RuntimeError("Can't find PROG")
    else:
        # id ...
        match = parse_id_space(match[1])
        if match is None:   
            raise RuntimeError("Can't find id of program")
        else:
            data = getFunction(VAR, FUNCTIONS)(match[1])
            if not data:
                raise RuntimeError("VAR isn't correct")
            else:
                # BEGIN ...
                match = parse_begin(data)
                if match is None:
                    raise RuntimeError("Can't find BEGIN")
                else: 
                    data = getFunction(LISTST, FUNCTIONS)(match[1])
                    if data:
                        # END
                        match = parse_end(data)
                        if match is None:
                            raise RuntimeError("Can't find END")
                        else:
                            return not match[1]

    return False
# <VAR> -> VAR <IDLIST>:<TYPE>;
def executeVar(data):
    # VAR ...
    match = parse_var(data)
    if match is None:
        raise RuntimeError("Can't find VAR")
    else:
        data = getFunction(IDLIST, FUNCTIONS)(match[1])
        if not data:
            raise RuntimeError("Id list in VAR isn't correct")
        else:
            # :...
            match = parse_colon(data)
            if match is not None:
                data = getFunction(TYPE, FUNCTIONS)(match[1])
                if not data:
                    raise RuntimeError("Type in VAR isn't correct")
                else:
                    # ;...
                    match = parse_semicolon(data)
                    if match is not None:
                        return match[1]
                
    return False
# <IDLIST> -> id|<IDLIST>,id
def executeIdlist(data):
    # id...
    match = parse_id(data)
    if match is not None:
        # ,...
        result = parse_comma(match[1])
        if result is not None:
            return getFunction(IDLIST, FUNCTIONS)(result[1])

        return match[1]         

    return False
# <TYPE> -> int|float|bool|string
def executeType(data):
    # int...
    match = parse_int(data)
    if match is not None:
        return match[1]
    # float...
    match = parse_float(data)
    if match is not None:
        return match[1]
    # bool...
    match = parse_bool(data)
    if match is not None:
        return match[1]
    # string...
    match = parse_string(data)
    if match is not None:
        return match[1]

    return False
# <LISTST> -> <ST>|<LISTST><ST>
def executeListst(data):
    src = getFunction(ST, FUNCTIONS)(data)
    if src:
        data = getFunction(LISTST, FUNCTIONS)(src)
        if data:
            return data
        
        return src

    return False
# <ST> -> <READ>|<WRITE>|<ASSIGN>
def executeSt(data):
    src = getFunction(READ, FUNCTIONS)(data)
    if src:
        return src

    src = getFunction(WRITE, FUNCTIONS)(data)
    if src:
        return src

    src = getFunction(ASSIGN, FUNCTIONS)(data)
    return src
# <READ> -> READ(<IDLIST>);
def executeRead(data):
    # READ...
    match = parse_read(data)
    if match is not None:
        # (...
        match = parse_opening_brace(match[1])
        if match is None:
            raise RuntimeError("Can't find opening brace in READ")
        else:
            data = getFunction(IDLIST, FUNCTIONS)(match[1])
            if not data:
                raise RuntimeError("Id list in READ isn't correct")
            else:
                # )...
                match = parse_closing_brace(data)
                if match is None:
                    raise RuntimeError("Can't find closing brace in READ")
                else:
                    # ;...
                    match = parse_semicolon(match[1])
                    if match is None:
                        raise RuntimeError("Can't find semicolon after READ")
                    else:
                        return match[1]

    return False
# <WRITE> -> WRITE(<IDLIST>);
def executeWrite(data):
    # WRITE...
    match = parse_write(data)
    if match is not None:
        # (...
        match = parse_opening_brace(match[1])
        if match is None:
            raise RuntimeError("Can't find opening brace in WRITE")
        else:
            data = getFunction(IDLIST, FUNCTIONS)(match[1])
            if not data:
                raise RuntimeError("Id list in WRITE isn't correct")
            else:
                # )...
                match = parse_closing_brace(data)
                if match is None:
                    raise RuntimeError("Can't find closing brace in WRITE")
                else:
                    # ;...
                    match = parse_semicolon(match[1])
                    if match is None:
                        raise RuntimeError("Can't find semicolon after WRITE")
                    else:
                        return match[1]

    return False
# <ASSIGN> -> id:=<EXP>;
def executeAssign(data):
    # id ...
    match = parse_id(data)
    if match is not None:
        # :=...
        match = parse_assigment(match[1])
        if match is None:
            raise RuntimeError("Can't find assigment")
        else:
            data = getFunction(EXP, FUNCTIONS)(match[1])
            if not data:
                raise RuntimeError("EXP isn't correct")
            else:
                # ;...
                match = parse_semicolon(data)
                if match is None:
                    raise RuntimeError("Can't find semicolon after assigment")
                else:
                    return match[1]

    return False
# <EXP> -> <EXP>+<T>|<T>
def executeExp(data):
    data = getFunction(T, FUNCTIONS)(data)
    if data:
        # +...
        match = parse_plus(data)
        if match is not None:
            return getFunction(EXP, FUNCTIONS)(match[1])         

        return data 

    return False
# <T> -> <T>*<F>|<F>
def executeT(data):
    data = getFunction(F, FUNCTIONS)(data)
    if data:
        # *...
        match = parse_multiply(data)
        if match is not None:
            return getFunction(T, FUNCTIONS)(match[1])         

        return data

    return False
# <F> -> -<F>|(<EXP>)|id|num
def executeF(data):
    # -...
    match = parse_minus(data)
    if match is not None:
        return getFunction(F, FUNCTIONS)(match[1])
    # (...
    match = parse_opening_brace(data)
    if match is not None:
        data = getFunction(EXP, FUNCTIONS)(match[1])
        if data:
            # )...
            match = parse_closing_brace(data)
            if match is not None:
                return match[1]
        return False
    # id...
    match = parse_id(data)
    if match is not None:
        return match[1]
    # num...
    match = parse_num(data)
    if match is not None:
        return match[1]

    return False

FUNCTIONS = {
    PROG: executeProg,
	VAR: executeVar,
	LISTST: executeListst,
	TYPE: executeType,
	IDLIST: executeIdlist,
	WRITE: executeWrite,
	READ: executeRead,
	ASSIGN: executeAssign,
	EXP: executeExp,
	ST: executeSt,
	T: executeT,
	F: executeF
}
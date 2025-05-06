import sys
from lab4 import determine

FINAL_SIGNAL = 'F'
EMPTY_IN_SIGNAL = 'ε'

class State:
    def __init__(self, id=None, isFinal=False):
        self.id = id
        self.isFinal = isFinal
        self.transitions = {}

    def addTransition(self, terminal, state):
        if terminal not in self.transitions:
            self.transitions[terminal] = []
        self.transitions[terminal].append(state)

class NFA:
    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end


def addConcatenationOperators(regex):
    result = []
    prev = None
    for char in regex:
        if prev is not None:
            if (prev.isalnum() or prev == ')' or prev == '*' or prev == '+') and (char.isalnum() or char == '('):
                result.append('.')
        result.append(char)
        prev = char
    return ''.join(result)


def regexToNFA(regex):
    def applyOperator(operator):
        nonlocal counter
        if operator == ".":
            if len(nfaStack) >= 2:
                nfa2 = nfaStack.pop()
                nfa1 = nfaStack.pop()
                nfa1.end.isFinal = False
                nfa1.end.addTransition(EMPTY_IN_SIGNAL, nfa2.start)
                nfaStack.append(NFA(start=nfa1.start, end=nfa2.end))

        elif operator == "|":
            if len(nfaStack) >= 2:
                nfa2 = nfaStack.pop()
                nfa1 = nfaStack.pop()

                start = State()

                end = State(isFinal = True)

                start.addTransition(EMPTY_IN_SIGNAL, nfa1.start)
                start.addTransition(EMPTY_IN_SIGNAL, nfa2.start)

                nfa1.end.isFinal = False
                nfa2.end.isFinal = False
                nfa1.end.addTransition(EMPTY_IN_SIGNAL, end)
                nfa2.end.addTransition(EMPTY_IN_SIGNAL, end)

                nfaStack.append(NFA(start=start, end=end))

        elif operator == "*":
            if len(nfaStack) >= 1:
                nfa = nfaStack.pop()
                start = State()
                end = State(isFinal = True)
                start.addTransition(EMPTY_IN_SIGNAL, nfa.start)
                start.addTransition(EMPTY_IN_SIGNAL, end)

                nfa.end.isFinal = False
                nfa.end.addTransition(EMPTY_IN_SIGNAL, nfa.start)
                nfa.end.addTransition(EMPTY_IN_SIGNAL, end)
                nfaStack.append(NFA(start=start, end=end))

        elif operator == "+":
            if len(nfaStack) >= 1:
                nfa = nfaStack.pop()
                start = State()
                end = State(isFinal = True)
                start.addTransition(EMPTY_IN_SIGNAL, nfa.start)

                nfa.end.isFinal = False
                nfa.end.addTransition(EMPTY_IN_SIGNAL, nfa.start)
                nfa.end.addTransition(EMPTY_IN_SIGNAL, end)
                nfaStack.append(NFA(start=start, end=end))

    def applyBrackets(bracket):
        if bracket == '(':
            operatorsStack.append(bracket)
        elif bracket == ')':
            while operatorsStack and operatorsStack[-1] != '(':
                applyOperator(operatorsStack.pop())
            operatorsStack.pop()

    def makeNFA(ch):
        nonlocal counter
        start = State()
        end = State(isFinal = True)
        start.addTransition(ch, end)
        nfaStack.append(NFA(start=start, end=end))

    counter = 0
    nfaStack = []
    operatorsStack = []
    precedence = {"*": 4, "+": 3, ".": 2, "|": 1}
    regex = addConcatenationOperators(regex).replace('e', EMPTY_IN_SIGNAL)

    print(regex)
    for ch in regex:
        if ch.isalnum():
            makeNFA(ch)
        elif ch == '(':
            operatorsStack.append(ch)
        elif ch == ')':
            applyBrackets(ch)
        elif ch in precedence:
            while (operatorsStack and operatorsStack[-1] in precedence and
                   precedence[operatorsStack[-1]] >= precedence[ch]):
                applyOperator(operatorsStack.pop())
            operatorsStack.append(ch)


    while operatorsStack:
        applyOperator(operatorsStack.pop())

    return nfaStack.pop()

def makeResult(nfa):
    terminals = set()
    states = set()
    finalStates = set()
    transitions = {}

    counter = 0

    def dfs(state):
        nonlocal counter
        if state.id == None:
            state.id = counter
            counter += 1
        states.add(state.id)

        if state.isFinal:
            finalStates.add(state.id)

        for symbol, next_states in state.transitions.items():
            for next_state in next_states:
                if next_state.id == None:
                    next_state.id = counter
                    counter += 1
                if state.id not in transitions:
                    transitions[state.id] = []
                transitions[state.id].append((symbol, next_state.id))
                if symbol not in terminals:
                    terminals.add(symbol)
                if next_state.id not in states:
                    dfs(next_state)

    dfs(nfa.start)

    print(finalStates)
    terminals = sorted(terminals)
    states = sorted(states)

    result = [['' for _ in range(len(states) + 1)] for _ in range(len(terminals) + 2)]

    for i, state in enumerate(states):
        result[1][i + 1] = f"q{state}"
        if state in finalStates:
            result[0][i+1] = FINAL_SIGNAL

    for i, terminal in enumerate(terminals):
        result[i + 2][0] = terminal

    for state, transition_list in transitions.items():
        state_idx = states.index(state) + 1
        for symbol, next_state in transition_list:
            terminal_idx = terminals.index(symbol) + 2
            if result[terminal_idx][state_idx] == '':
                result[terminal_idx][state_idx] = f"q{next_state}"
            else:
                result[terminal_idx][state_idx] += f",q{next_state}"

    print()
    for line in result:
        print(';'.join(line))
    print()

    return result

def exit_help():
    print('lab5.py <input> <output>')
    sys.exit(0)

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) != 2:
        exit_help()

    with open(args[0], 'r', encoding='utf-8') as f:
        regex = f.read().strip()

    nfa = regexToNFA(regex)
    result = makeResult(nfa)
    determine(result, args[1])
    print('Convertion completed')

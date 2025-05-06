import sys
import csv
from collections import deque
from collections import defaultdict

EMPTY_IN_SIGNAL = 'ε'
FINAL_SIGNAL = 'F'

def print_graph(graph, file):
    with open(file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(graph)


def read_graph(file):
    f = open(file, 'r', encoding='utf-8')
    result = []
    lineCount = 0

    for line in f:
        if not line.strip():
            continue
        splited = line.split(';')
        result.append([0] * len(splited))
        for i in range(len(splited)):
            item = splited[i].strip('\n').strip('\t')
            if i == 0 or lineCount <= 1:
                result[lineCount][i] = item
            else:
                result[lineCount][i] = item

        lineCount += 1

    return result


def get_graph(original):
    states = []
    terminals = []
    transitions = dict()

    for i in range(1, len(original[1])):
        states.append(original[1][i])

    for i in range(2, len(original)):
        terminals.append(original[i][0])

    for stateIdx in range(len(states)):
        transitions[original[1][stateIdx + 1]] = dict()
        for i in range(2, len(original)):
            if stateIdx + 1 < len(original[i]) and original[i][stateIdx + 1] != '':
                if ',' in original[i][stateIdx + 1]:
                    nextState = original[i][stateIdx + 1].split(',')
                else:
                    nextState = [original[i][stateIdx + 1]]
                transitions[original[1][stateIdx + 1]][original[i][0]] = nextState

    return states, terminals, transitions


def eps_closure(state, transitions):
    eTransitions = set()
    queue = deque([state])

    while queue:
        current = queue.popleft()
        eTransitions.add(current)
        if EMPTY_IN_SIGNAL in transitions.get(current, {}):
            for nextState in transitions[current][EMPTY_IN_SIGNAL]:
                if nextState not in eTransitions:
                    queue.append(nextState)

    return list(eTransitions)


def determine(original, states, terminals, transitions):
    dfaTerminals = []

    dfaTerminals = [t for t in terminals if t != EMPTY_IN_SIGNAL and t not in dfaTerminals]

    start_closure = eps_closure(states[0], transitions)
    queue = deque([frozenset(start_closure)])
    dfaStates = {frozenset(start_closure): f"q0"}
    dfaTransitions = defaultdict(dict)
    count = 1

    while queue:
        current = queue.pop()
        currentState = dfaStates[frozenset(current)]

        for terminal in dfaTerminals:
            transitionsSet = set()
            for prev in current:
                if terminal in transitions.get(prev, {}):
                    for nextState in transitions[prev][terminal]:
                        transitionsSet.update(eps_closure(nextState, transitions))

            if transitionsSet:
                if frozenset(transitionsSet) not in dfaStates:
                    newState = f"q{count}"
                    dfaStates[frozenset(transitionsSet)] = newState
                    queue.appendleft(transitionsSet)
                    count += 1

                dfaTransitions[currentState][terminal] = dfaStates[frozenset(transitionsSet)]
            else:
                dfaTransitions[currentState][terminal] = ""

    if len(dfaTerminals) != 0:
        result = [['' for _ in range(len(dfaTransitions) + 1)] for _ in range(len(dfaTerminals) + 2)]
    else:
        result = [['' for _ in range(len(dfaTransitions) + 2)] for _ in range(len(dfaTerminals) + 2)]

    for i in range(0, len(dfaTerminals)):
        result[i + 2][0] = dfaTerminals[i]

    for i, v in enumerate(dfaStates.items()):
        result[1][i + 1] = v[1]
        for state in v[0]:
            if original[0][original[1].index(state)] == 'F':
                result[0][i + 1] = 'F'

    for k, v in dfaTransitions.items():
        for next in v.items():
            result[dfaTerminals.index(next[0]) + 2][result[1].index(k)] = next[1]

    return result

def exit_help():
    print('lab4.py <input filename> <output filename>')
    sys.exit(0)

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) != 2:
        exit_help()

    original = read_graph(args[0])
    states, terminals, transitions = get_graph(original)
    result = determine(original, states, terminals, transitions)
    print_graph(args[1], result)
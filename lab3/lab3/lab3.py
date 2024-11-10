import sys
import csv
import re
import networkx as nx
from itertools import count

ARTIFICIAL_STATE = ''
FINAL_SIGNAL = 'F'
IN_SIGNAL = 'in_signal'
OUT_SIGNAL = 'out_signal'

LEFT = '^\s*<(\w+)>\s*->\s*((?:<\w+>\s+)?[\wε](?:\s*\|\s*(?:<\w+>\s+)?[\wε])*)\s*$'
RIGHT = '^\s*<(\w+)>\s*->\s*([\wε](?:\s+<\w+>)?(?:\s*\|\s*[\wε](?:\s+<\w+>)?)*)\s*$'

LEFT_TR = '\s*(?:<(\w+)>\s+)?([\wε])\s*'
RIGHT_TR = '\s*([\wε])(?:\s+<(\w+)>)?\s*'

def print_moore(graph, file):
    with open(file, 'w', newline='\n', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        ordered_states = list(graph.nodes)
        indexed_states = dict(zip(ordered_states, range(len(ordered_states))))
        ordered_state_outs = [graph.nodes[node][OUT_SIGNAL] for node in ordered_states]
        ordered_signals = sorted(list(set(nx.get_edge_attributes(graph, IN_SIGNAL).values())))
        indexed_signals = dict(zip(ordered_signals, range(len(ordered_signals))))
        writer.writerow([''] + ordered_state_outs)
        writer.writerow([''] + ordered_states)
        transitions_matrix = [[signal] + [''] * len(ordered_states) for signal in ordered_signals]

        for from_state, to_state, edge in graph.edges:
            data = graph.get_edge_data(from_state, to_state, edge)
            signal = data[IN_SIGNAL]
            state = transitions_matrix[indexed_signals[signal]] \
                [indexed_states[from_state] + 1]
            transitions_matrix[indexed_signals[signal]] \
                [indexed_states[from_state] + 1] = to_state if state == '' else f'{state},{to_state}'
        writer.writerows(transitions_matrix)

def print_states(map, is_left):
    artificial_state = 'H' if is_left else 'F'
    for key, value in map.items():
        old_state = artificial_state if key == ARTIFICIAL_STATE else key
        print(f'{old_state} -> {value}')

def is_state(map, state):
    if state in map.keys():
        return map[state]
    else:
        print(f'Rule for state <{state}> not found')
        return None

def convert(grammar, is_left):
    graph = nx.MultiDiGraph()
    states = [rule[0] for rule in grammar] + [ARTIFICIAL_STATE]
    if is_left:
        states.reverse()
    state_mapping = {state: f'q{i}' for i, state in enumerate(states)}

    print_states(state_mapping, is_left)
    
    for state in states:
        graph.add_node(state_mapping[state], out_signal=FINAL_SIGNAL if state == states[-1] else '')

    regex = re.compile(LEFT_TR if is_left else RIGHT_TR)
    
    for rules in grammar:
        if is_left:
            to_state = state_mapping[rules[0]]
        else:
            from_state = state_mapping[rules[0]]
        
        rules = [match.groups() for match in regex.finditer(rules[1])]

        for rule in rules:
            if is_left:
                in_signal = rule[1]
                from_state = state_mapping[ARTIFICIAL_STATE] if rule[0] is None else is_state(state_mapping, rule[0])
            else:
                in_signal = rule[0]
                to_state = state_mapping[ARTIFICIAL_STATE] if rule[1] is None else is_state(state_mapping, rule[1])
            
            if from_state is None or to_state is None:
                return None
            graph.add_edge(from_state, to_state, in_signal=in_signal)
            
    return graph

def parse(text, regex):
    matches = []
    pos_end = 0

    for match in re.finditer(regex, text, flags=re.MULTILINE):
        if abs(match.start() - pos_end) <= 1:
            matches.append(match.groups())
            pos_end = match.end()
        else:
            break
        
    result = matches if len(text) == pos_end else pos_end
    return (len(text) == pos_end), result
        

def read_grammar(file):
    with open(file, encoding='utf-8') as f:
        text = f.read()
        
        errors = []
        for grammar_type in [LEFT, RIGHT]:
            result = parse(text, grammar_type)
            if result[0]:
                return True, result[1], grammar_type == LEFT
            else:
                err_line = 0 if result[1] == 0 else len(text[:result[1]].split('\n'))
                errors.append(('Left' if grammar_type == LEFT else 'Right', err_line))

        if errors[0][1] == errors[1][1]:
            print(f'Invalid text on line {errors[0][1]}')
        else:
            for err in errors:
                print(f'{err[0]}-handed grammar: Invalid rule on line {err[1]}')
        return False, None

def exit_help():
    print('lab3.py <input filename> <output filename>')
    sys.exit(0)

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) != 2:
        exit_help()

    result = read_grammar(args[0])
    if result[0]:
        grammar, is_left = result[1], result[2]
    else:
        sys.exit(0)

    moore = convert(grammar, is_left)
    if moore is None:
        sys.exit(0)

    print_moore(moore, args[1])
    print('Convertion completed')

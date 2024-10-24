import sys
import csv
import itertools
import networkx as nx

DELIMITER = '/'
EMPTY = '-'
IN_SIGNAL = 'in_signal'
OUT_SIGNAL = 'out_signal'

def print_mealy(graph, file):
    with open(file, 'w', newline='\n') as f:
        writer = csv.writer(f, delimiter=';')
        ordered_states = list(graph.nodes)
        indexed_states = dict(zip(ordered_states, range(len(ordered_states))))
        ordered_signals = sorted(list(set(nx.get_edge_attributes(graph, IN_SIGNAL).values())))
        indexed_signals = dict(zip(ordered_signals, range(len(ordered_signals))))
        writer.writerow([''] + ordered_states)
        transitions_matrix = [[signal] + [''] * len(ordered_states) for signal in ordered_signals]

        for from_state, to_state, edge in graph.edges:
            data = graph.get_edge_data(from_state, to_state, edge)
            in_signal, out_signal = data[IN_SIGNAL], data[OUT_SIGNAL]
            transitions_matrix[indexed_signals[in_signal]] \
                [indexed_states[from_state] + 1] = f'{to_state}{DELIMITER}{out_signal}'
        writer.writerows(transitions_matrix)

def print_moore(graph, file):
    with open(file, 'w', newline='\n') as f:
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
            transitions_matrix[indexed_signals[signal]] \
                [indexed_states[from_state] + 1] = to_state
        writer.writerows(transitions_matrix)

def mealy_to_moore(graph):
    def get_transition_out_signal(tr):
        return tr[2][OUT_SIGNAL]

    synthetic_i = 0
    node_count = 0
    dest = nx.MultiDiGraph()
    edges_planned = []
    nodes_map = dict()

    for node in graph.nodes:
        clustered_transitions = itertools.groupby(
            sorted(
                graph.in_edges(node, data=True),
                key=get_transition_out_signal
            ),
            key=get_transition_out_signal
        )

        for out_signal, transitions in clustered_transitions:
            name = 'q' + str(synthetic_i)

            dest.add_node(name, out_signal=out_signal)

            chain = nodes_map.get(node, [])
            chain.append(name)
            nodes_map[node] = chain

            for t in transitions:
                edges_planned.append((t[0], name, t[2][IN_SIGNAL]))

            synthetic_i += 1
        node_count +=1

        if synthetic_i == 0 and node_count != 0:
            name = 'q' + str(synthetic_i)
            dest.add_node(name, out_signal=EMPTY)

            chain = nodes_map.get(node, [])
            chain.append(name)
            nodes_map[node] = chain
            
            synthetic_i += 1

    for from_state, to_state, signal in edges_planned:
        for node in nodes_map[from_state]:
            dest.add_edge(node, to_state, in_signal=signal)
    return dest

def moore_to_mealy(graph):
    dest = nx.MultiDiGraph()
    dest.add_nodes_from(graph.nodes)
    for from_state, to_state, edge in graph.edges:
        data = graph.get_edge_data(from_state, to_state, edge)
        dest.add_edge(from_state, to_state, in_signal=data[IN_SIGNAL], out_signal=graph.nodes[to_state][OUT_SIGNAL])
    return dest

def read_mealy(file):
    with open(file, newline='\n') as f:
        reader = csv.reader(f, delimiter=';')
        graph = nx.MultiDiGraph()
        states = [EMPTY if state == '' else state for state in reader.__next__()[1:]]
        graph.add_nodes_from(states)
        for line in reader:
            in_signal = line[0]  
            transitions = line[1:]
            for transition, from_state in zip(transitions, states):
                split_result = [EMPTY] if transition == '' else transition.split(DELIMITER)
                to_state, out_signal = split_result if len(split_result) == 2 else [split_result[0], DELIMITER.join(split_result[1:])]
                out_signal = EMPTY if out_signal == '' else out_signal
                graph.add_edge(from_state, to_state, in_signal=in_signal, out_signal=out_signal)
        return graph

def read_moore(file):
    with open(file, newline='\n') as f:
        reader = csv.reader(f, delimiter=';')
        graph = nx.MultiDiGraph()
        out_signals = [EMPTY if signal == '' else signal for signal in reader.__next__()[1:]]
        states = [EMPTY if state == '' else state for state in reader.__next__()[1:]]
        for state, out_signal in zip(states, out_signals):
            graph.add_node(state, out_signal=out_signal)
        for line in reader:
            in_signal = line[0]
            to_states = [EMPTY if state == '' else state for state in line[1:]]
            for from_state, to_state in zip(states, to_states):
                graph.add_edge(from_state, to_state, in_signal=in_signal)
        return graph

def exit_help():
    print('lab1.py (mealy-to-moore|moore-to-mealy) <input filename> <output filename>')
    sys.exit(0)

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) != 3:
        exit_help()

    if args[0] == 'mealy-to-moore':
        mealy = read_mealy(args[1])
        moore = mealy_to_moore(mealy)
        print_moore(moore, args[2])
        print('Mealy to Moore conversion completed')
    elif args[0] == 'moore-to-mealy':
        moore = read_moore(args[1])
        mealy = moore_to_mealy(moore)
        print_mealy(mealy, args[2])
        print('Moore to Mealy conversion completed')
    else:
        exit_help()

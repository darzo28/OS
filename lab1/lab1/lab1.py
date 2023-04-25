import sys
import csv
import itertools
import networkx as nx
import pygraphviz as pgv

def print_mealy(graph, file):
    with open(file, 'w', newline='\n') as f:
        writer = csv.writer(f, delimiter=';')
        ordered_states = sorted(list(graph.nodes))
        indexed_states = dict(zip(ordered_states, range(len(ordered_states))))
        ordered_signals = sorted(list(set(nx.get_edge_attributes(graph, "in_signal").values())))
        indexed_signals = dict(zip(ordered_signals, range(len(ordered_signals))))
        writer.writerow([''] + ordered_states)
        transitions_matrix = [[signal] + [""] * len(ordered_states) for signal in ordered_signals]

        for from_state, to_state in graph.edges:
            data = graph.get_edge_data(from_state, to_state)
            in_signal, out_signal = data["in_signal"], data["out_signal"]
            transitions_matrix[indexed_signals[in_signal]] \
                [indexed_states[from_state] + 1] = to_state + '/' + out_signal
        writer.writerows(transitions_matrix)


def print_moore(graph, file):
    with open(file, 'w', newline='\n') as f:
        writer = csv.writer(f, delimiter=';')
        ordered_states = sorted(list(graph.nodes))
        indexed_states = dict(zip(ordered_states, range(len(ordered_states))))
        ordered_state_outs = [graph.nodes[node]['out_signal'] for node in ordered_states]
        ordered_signals = sorted(list(set(nx.get_edge_attributes(graph, "in_signal").values())))
        indexed_signals = dict(zip(ordered_signals, range(len(ordered_signals))))
        writer.writerow([''] + ordered_state_outs)
        writer.writerow([''] + ordered_states)
        transitions_matrix = [[signal] + [""] * len(ordered_states) for signal in ordered_signals]

        for from_state, to_state in graph.edges:
            data = graph.get_edge_data(from_state, to_state)
            signal = data["in_signal"]
            transitions_matrix[indexed_signals[signal]] \
                [indexed_states[from_state] + 1] = to_state
        writer.writerows(transitions_matrix)


def mealy_to_moore(graph):
    def get_transition_out_signal(tr):
        return tr[2]['out_signal']

    synthetic_i = 0
    dest = nx.DiGraph()
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
                edges_planned.append((t[0], name, t[2]['in_signal']))

            synthetic_i += 1

    for from_state, to_state, signal in edges_planned:
        for node in nodes_map[from_state]:
            dest.add_edge(node, to_state, in_signal=signal)
    return dest


def moore_to_mealy(graph):
    dest = nx.DiGraph()
    for from_state, to_state in graph.edges:
        data = graph.get_edge_data(from_state, to_state)
        dest.add_edge(from_state, to_state, in_signal=data['in_signal'], out_signal=graph.nodes[to_state]['out_signal'])
    return dest

def read_mealy(file):
    with open(file, newline='\n') as f:
        reader = csv.reader(f, delimiter=';')
        graph = nx.DiGraph()
        states = reader.__next__()[1:]
        for line in reader:
            in_signal = line[0]  
            transitions = line[1:]
            for transition, from_state in zip(transitions, states):
                to_state, out_signal = transition.split('/')
                graph.add_edge(from_state, to_state, in_signal=in_signal, out_signal=out_signal)
        return graph


def read_moore(file):
    with open(file, newline='\n') as f:
        reader = csv.reader(f, delimiter=';')
        graph = nx.DiGraph()
        out_signals = reader.__next__()[1:]
        states = reader.__next__()[1:]
        for state, out_signal in zip(states, out_signals):
            graph.add_node(state, out_signal=out_signal)
        for line in reader:
            in_signal = line[0]
            to_states = line[1:]
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

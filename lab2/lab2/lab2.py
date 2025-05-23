import sys
import csv
import networkx as nx
from enum import Enum

DELIMITER = '/'
EMPTY = '-'
IN_SIGNAL = 'in_signal'
OUT_SIGNAL = 'out_signal'

class Types(str, Enum):
    Mealy = 'mealy'
    Moore = 'moore'

def print_mealy(graph, file):
    with open(file, 'w', newline='\n', encoding='utf-8') as f:
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
    with open(file, 'w', newline='\n', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        ordered_states = list(graph.nodes)
        indexed_states = dict(zip(ordered_states, range(len(ordered_states))))
        ordered_state_outs = ['' if graph.nodes[node][OUT_SIGNAL] == EMPTY else graph.nodes[node][OUT_SIGNAL] for node in ordered_states]
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

def remove_unreachable(old_graph, new_graph, current_state, option):
    if option == Types.Mealy.value:
        new_graph.add_node(current_state)
    else:
        new_graph.add_node(current_state, out_signal=dict(old_graph.nodes)[current_state][OUT_SIGNAL])
    for neighbor in list(old_graph.successors(current_state)):
        if neighbor not in list(new_graph.nodes):
            remove_unreachable(old_graph, new_graph, neighbor, option)
        for edge in old_graph.get_edge_data(current_state, neighbor).values():
            if option == Types.Mealy.value:
                new_graph.add_edge(current_state, neighbor, in_signal=edge[IN_SIGNAL], out_signal=edge[OUT_SIGNAL])
            else:
                new_graph.add_edge(current_state, neighbor, in_signal=edge[IN_SIGNAL])

def minimize(graph, partitions):
    while True:
        new_partitions = []
        for partition in partitions:
            groups = {}
            for state in partition:
                key = []
                for neighbor in list(graph.successors(state)):
                    key.extend(list(
                        [signal[IN_SIGNAL], tuple(next((partition for partition in partitions if neighbor in partition)))]
                        for signal in graph.get_edge_data(state, neighbor).values()
                    ))
                key = tuple([transition[1] for transition in sorted(key)])
                
                if key not in groups:
                    groups[key] = []
                groups[key].append(state)

            new_partitions.extend(groups.values())

        if new_partitions == partitions:
            break
        partitions = new_partitions

    return partitions

def mealy_minimize(graph):
    def get_transition_in_signal(tr):
        return tr[IN_SIGNAL]

    new_graph = nx.MultiDiGraph()
    start_state = list(graph.nodes)[0]
    remove_unreachable(graph, new_graph, start_state, Types.Mealy.value)
    graph = new_graph
    
    states = list(graph.nodes)

    groups = {}
    for state in states:
        key = []
        for neighbor in list(graph.successors(state)):
            k = [signal for signal in graph.get_edge_data(state, neighbor).values()]
            key.extend(k)

        key = tuple([signal[OUT_SIGNAL] for signal in sorted(key, key=get_transition_in_signal)])
        if key not in groups:
            groups[key] = []
        groups[key].append(state)

    partitions = list(groups.values())

    new_partitions = minimize(graph, partitions) if len(partitions) != 1 else partitions

    minimized_graph = nx.MultiDiGraph()
    state_mapping = {state: f'q{i}' for i, partition in enumerate(new_partitions) for state in partition}

    minimized_graph.add_nodes_from(list(state_mapping.values()))
        
    for partition in new_partitions:
        representative = partition[0]
        for neighbor in graph.successors(representative):
            new_from_state = state_mapping[representative]
            new_to_state = state_mapping[neighbor]
            for signal in graph.get_edge_data(representative, neighbor).values():
                minimized_graph.add_edge(new_from_state, new_to_state, in_signal=signal[IN_SIGNAL], out_signal=signal[OUT_SIGNAL])

    return minimized_graph    

def moore_minimize(graph):
    new_graph = nx.MultiDiGraph()
    start_state = list(graph.nodes)[0]
    remove_unreachable(graph, new_graph, start_state, Types.Moore.value)
    graph = new_graph
    
    output_signals = {node: graph.nodes[node][OUT_SIGNAL] for node in list(graph.nodes)}    
    ordered_signals = []
    for signal in list(output_signals.values()):
        if signal not in ordered_signals:
            ordered_signals.append(signal)
    partitions = [[node[0] for node in graph.nodes(data=True) if node[1][OUT_SIGNAL] == output] for output in ordered_signals]

    new_partitions = minimize(graph, partitions) if len(partitions) != 1 else partitions

    minimized_graph = nx.MultiDiGraph()
    state_mapping = {state: f'q{i}' for i, partition in enumerate(new_partitions) for state in partition}

    for partition in new_partitions:
        representative = partition[0]
        output_signal = output_signals[representative]
        minimized_graph.add_node(state_mapping[representative], out_signal=output_signal)
        
    for partition in new_partitions:
        representative = partition[0]
        for neighbor in graph.successors(representative):
            new_from_state = state_mapping[representative]
            new_to_state = state_mapping[neighbor]
            for signal in graph.get_edge_data(representative, neighbor).values():
                minimized_graph.add_edge(new_from_state, new_to_state, in_signal=signal[IN_SIGNAL])

    return minimized_graph

def read_mealy(file):
    with open(file, newline='\n', encoding='utf-8') as f:
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
    with open(file, newline='\n', encoding='utf-8') as f:
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
                if to_state != EMPTY:
                    graph.add_edge(from_state, to_state, in_signal=in_signal)
        return graph

def exit_help():
    print('lab2.py (mealy|moore) <input filename> <output filename>')
    sys.exit(0)

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) != 3:
        exit_help()

    if args[0] == Types.Mealy.value:
        mealy = mealy_minimize(read_mealy(args[1]))
        print_mealy(mealy, args[2])
        print('Mealy minimization completed')
    elif args[0] == Types.Moore.value:
        moore = moore_minimize(read_moore(args[1]))
        print_moore(moore, args[2])
        print('Moore minimization completed')
    else:
        exit_help()

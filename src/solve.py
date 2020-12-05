from argparse import ArgumentParser
import networkx as nx

if __name__ == '__main__':

    # Parse arguments
    parser = ArgumentParser(add_help=False)
    parser.add_argument('--input-file', type=str, required=True)
    args = parser.parse_args()

    B = []  # Nodes initially burned
    G = nx.Graph()  # Instance graph

    # Load instance
    with open(args.input_file, 'r') as f:

        # Iterate over file lines
        for (idx, line) in enumerate(f):
            values = line.split()

            # Store B
            if idx > 4 and len(values) == 1:
                B.append(int(values[0]))

            # Store edges
            if len(values) == 2:
                G.add_edge(int(values[0]), int(values[1]))

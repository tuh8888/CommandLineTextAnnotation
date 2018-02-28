from BlackBox import BlackBox
from Activity import Activity
from Entity import Entity
import re
import networkx as nx


class Mechanism:

    def __init__(self):
        self.components = []
        self.G = nx.DiGraph()

    def add_component(self, a_or_e, name, children):
        c = None
        if a_or_e == 'a':
            if name == '?':
                c = BlackBox(children)
            else:
                c = Activity(name, children)
        elif a_or_e == 'e':
            c = Entity(name, children)

        self.components.append(c)
        self.G.add_node(c, name=c.name, component_type=c.component_type)

    def add_entity(self, name, children):
        new_entity = Entity(name, children)
        self.components.append(new_entity)

    def add_activity(self, name, children):
        if name == '?':
            self.add_black_box(children)
        else:
            new_activity = Activity(name, children)
            self.components.append(new_activity)
            self.G.add_node(new_activity)

    def add_black_box(self, children):
        new_activity = BlackBox(children)
        self.components.append(new_activity)
        self.G.add_node(new_activity)

    def construct_graph(self):
        for i, c in enumerate(self.components):
            for child in c.children:
                self.G.add_edge(c, self.components[child])

    def read_from_file(self, file_name):
        print('Reading from {}'.format(file_name))
        edge_list = []

        with open(file_name) as f:
            header = f.readline().strip('\n')
            header_fields = header.split(', ')

            node_num_index = header_fields.index('Node_number')
            type_index = header_fields.index('Type_of_component')
            name_index = header_fields.index('Name')
            children_index = header_fields.index('Connections')
            for line in f:
                line = line.strip('\n')
                sep_line = line.split(', ')

                node_num = sep_line[node_num_index]
                name = sep_line[name_index]
                children = [int(c) for c in re.findall('\d+', sep_line[children_index])]
                current_edges = [(int(node_num), int(c)) for c in re.findall('\d+', sep_line[children_index])]
                edge_list.extend(current_edges)
                self.add_component(sep_line[type_index], name, children)

        self.construct_graph()

    def __str__(self):
        to_return = ''
        for x in self.components:
            to_return += '{}\n'.format(x.to_string())
        return to_return

    def write_to_file(self, file_name):
        print('Writing to {}'.format(file_name))
        nx.write_graphml(self.G, file_name)

    def draw_mechanism(self):
        graph_pos = nx.random_layout(self.G)

        # draw nodes, edges and labels
        nx.draw_networkx_nodes(self.G, graph_pos, node_size=1000, node_color='blue', alpha=0.3)
        nx.draw_networkx_edges(self.G, graph_pos)
        nx.draw_networkx_labels(self.G, graph_pos, font_size=12, font_family='sans-serif')

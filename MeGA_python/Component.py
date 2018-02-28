from Node import Node


class Component(Node):

    def __init__(self, name, children):
        Node.__init__(self, children)
        self.name = name
        self.component_type = None

    def to_string(self):
        return '{}\t{}'.format(self.name, self.children)

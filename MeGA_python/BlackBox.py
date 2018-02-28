from Component import Component


class BlackBox(Component):

    def __init__(self, children):
        Component.__init__(self, 'Black Box', children)
        self.component_type = 'Black Box'

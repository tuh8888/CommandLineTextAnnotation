from Component import Component


class Activity(Component):

    def __init__(self, name, children):
        Component.__init__(self, name, children)
        self.component_type = 'Activity'

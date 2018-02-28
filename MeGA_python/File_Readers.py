class FileReader:

    def __init__(self, file_name):
        self.file_name = file_name
        try:
            self.f = open(file_name)
        except IOError:
            print('Could not open {}'.format(file_name))

    def get_next_line(self):

        try:
            return self.f.readline()
        except:
            print('No more lines in {}'.format(self.file_name))

    def close_file(self):
        self.f.close()


def read_ontologies_file(file_name):
    ontologies = []

    fields = ('Name', 'Location', 'Roots')
    with open(file_name) as f:
        header = f.readline().strip('\n')
        header_fields = header.split(', ')

        for line in f:
            ontology = {}
            sep_line = line.split(', ')
            for field in fields:
                ontology[field] = sep_line[header_fields.index(field)]
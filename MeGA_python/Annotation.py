import obonet
import networkx as nx
import pandas as pd

import re
import logging


class FileDone(Exception):
    pass


class LineDone(Exception):
    pass


class AnnotationDone(Exception):
    pass


class GoUp(Exception):
    pass


class NotOption(Exception):
    pass


class FileAnnotator:

    exit_clause = 'q'
    next_line_clause = 'l'
    next_annotation_clause = 't'
    go_up_clause = 'u'
    reminder = '[{}]annotation, [{}]next line, [{}]exit'.format(next_annotation_clause, next_line_clause, exit_clause)

    def __init__(self, onto_file=None, use_local=True):
        self.ontos = {}
        if onto_file is not None:
            self.ontos = load_ontologies(onto_file, use_local)

    def begin_annotating_file(self, input_file_name, output_file_name, use_custom=False):

        try:
            with open(input_file_name, 'r') as f, open(output_file_name, 'w') as g:
                print('Reading from {}'.format(input_file_name))
                print('Writing to {}'.format(output_file_name))
                print('**********************************************')
                annotations = []
                try:
                    while True:
                        line_annotations = self.annotate_next_line(f, g, use_custom)
                        annotations.append(line_annotations)
                except FileDone:
                    print('Done reading from {}'.format(input_file_name))
                    print('Annotations located at file location: {}'.format(output_file_name))

        except IOError:
            logging.error('Could not open files')

    def annotate_next_line(self, f, g, use_custom):
        try:
            line_to_annotate = tokenize(f.readline())
            if len(line_to_annotate) == 0:
                return 'Nothing to annotate'

            annotations = [{'token': tok, 'annotation': ''} for i, tok in enumerate(line_to_annotate)]
            try:
                while True:
                    index, annotation = self.get_annotation_from_user(annotations, use_custom)
                    annotations[int(index)]['annotation'] = annotation

            except LineDone:
                # Write current annotation
                g.write('{}\n\n'.format(annotations_to_string(annotations)))

            except FileDone:
                # Write current annotation
                g.write('{}\n\n'.format(annotations_to_string(annotations)))

                # Finish writing file in annotation format

                for line in f.readlines():
                    line_to_annotate = tokenize(line)
                    annotations = [{'token': tok, 'annotation': ''} for i, tok in enumerate(line_to_annotate)]
                    g.write('{}\n\n'.format(annotations_to_string(annotations)))

                # Propagate exception
                raise FileDone

            return annotations

        except IOError:
            return False

    def get_annotation_from_user(self, annotations, use_custom):
        level_code = 1

        print(annotations_to_string(annotations))
        if use_custom:
            index = self.get_input('Index: ', level_code)
            annotation = self.get_input('Annotation: ', level_code)
        else:
            index = self.get_input('Select the index of the term you wish to annotate: ', level_code)
            annotation = self.select_ontology_term(annotations, index=int(index))
        return index, annotation

    def select_ontology(self):
        level_code = 2

        options = {i: option for i, option in enumerate(self.ontos)}

        for i, option in options.items():
            print('[{}] {}'.format(i, option))

        try:
            user_input = self.get_input('Select ontology: ', level_code, options=options)
            return user_input
        except (GoUp, NotOption):
            return None

    def select_ontology_term(self, annotations, index):

        ontology = None
        roots = []
        ontology_options = None
        id_to_name = None
        name_to_id = None
        selected_terms = []

        try:
            while True:
                print(annotations_to_string(annotations, index=index))

                if len(selected_terms) == 0:
                    ontology_name = self.select_ontology()
                    if ontology_name is None:
                        pass
                    else:
                        selected_terms.append(ontology_name)
                        ontology, roots = self.ontos[ontology_name]
                        id_to_name = {id_: data['name'] for id_, data in ontology.nodes(data=True)}
                        name_to_id = {data['name']: id_ for id_, data in ontology.nodes(data=True)}
                else:
                    self.display_onto_options(selected_terms, ontology_options)

                if len(selected_terms) > 1:
                    ontology_options = get_subterms(selected_terms[-1], ontology, id_to_name, name_to_id)
                elif len(selected_terms) == 1:
                    ontology_options = roots

        except AnnotationDone:
            if len(selected_terms) > 1:
                return name_to_id[selected_terms[-1]]
            elif len(selected_terms) == 1:
                return selected_terms[0]
            else:
                return ''

    def display_onto_options(self, selected_terms, ontology_options):
        level_code = 2

        options = {i: option for i, option in enumerate(ontology_options)}
        for i, option in options.items():
            tabs = '\t' * len(selected_terms)
            print('{}[{}] {}'.format(tabs, i, option))
        for i, term in reversed(list(enumerate(selected_terms))):
            tabs = '\t' * i
            print('{}-{}'.format(tabs, term))
        try:
            term = self.get_input('Select term: ', level_code, options=options)
            selected_terms.append(term)
        except GoUp:
            selected_terms.pop()
        except NotOption:
            pass

    def get_input(self, prompt, level_code, options=None):

        reminder = '[{}]exit'.format(self.exit_clause)

        if level_code > 0:
            reminder += ', [{}]next line'.format(self.next_line_clause)
        if level_code > 1:
            reminder += ', [{}]annotation'.format(self.next_annotation_clause)

        user_input = input('\n*{}* {}'.format(reminder, prompt))

        if user_input is self.next_line_clause:
            raise LineDone
        elif user_input is self.exit_clause:
            raise FileDone
        elif user_input is self.next_annotation_clause:
            raise AnnotationDone
        elif user_input is self.go_up_clause:
            raise GoUp
        elif options is not None:
            try:
                user_input = options[int(user_input)]
            except (KeyError, ValueError):
                print('**********************************************************************')
                print('Please enter one of the available options or commands')
                raise NotOption
        print('**********************************************************************')
        return user_input


def get_subterms(term, ontology, id_to_name, name_to_id):
    return sorted(id_to_name[subterm] for subterm in nx.ancestors(ontology, name_to_id[term]))


def get_superterms(term, ontology, id_to_name, name_to_id):
    return sorted(id_to_name[superterm] for superterm in nx.descendants(ontology, name_to_id[term]))


def load_ontologies(file_name, use_local):
    ontologies_to_load = pd.read_csv(file_name, sep=',', header=0)

    ontologies = {}

    for i, row in ontologies_to_load.iterrows():
        if use_local:
            location = row['Local_Location']
        else:
            location = row['URL_Location']

        if not pd.isnull(location):
            print('Loading ontology({}) from {}'.format(row['Name'], location))
            g = obonet.read_obo(location)

            ontologies[row['Name']] = g, row['Roots'].split(',')

            print('\tNumber of nodes: {}'.format(len(g)))
            print('\tNumber of edges: {}'.format(g.number_of_edges()))
            print('\tIs DAG: {}'.format(nx.is_directed_acyclic_graph(g)))

    print()

    return ontologies


def tokenize(string):
    return re.findall('[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[\'\w\-]+', string)


def highlight(string):
    return '*{}*'.format(string)


def annotations_to_string(annotations, index=-1):
    tok_indices_output = ''
    line_output = ''
    annotations_output = ''
    try:
        col_width = max(len(word) for a in annotations for _, word in a.items()) + 4
    except ValueError:
        col_width = 0
    for i, a in enumerate(annotations):
        if i == index:
            line_output += '{}\t|'.format(highlight(a['token'])).expandtabs(col_width)
        else:
            line_output += '{}\t|'.format(a['token']).expandtabs(col_width)

        tok_indices_output += '{}\t|'.format(i).expandtabs(col_width)
        annotations_output += '{}\t|'.format(a['annotation']).expandtabs(col_width)

    return 'I: {}\nA: {}\nL: {}'.format(tok_indices_output, annotations_output, line_output).expandtabs(col_width)

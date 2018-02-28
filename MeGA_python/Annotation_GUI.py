from tkinter import *
from tkinter import filedialog, Tk, StringVar, simpledialog, ttk
from tkinter.ttk import Treeview, Scrollbar
from tkinter.scrolledtext import ScrolledText
from Annotation import *
from Basic_GUI import BasicGUI


class AnnotationGUI(BasicGUI, FileAnnotator):

    def __init__(self, master=None):
        BasicGUI.__init__(self, master=master)
        FileAnnotator.__init__(self)

        self.vert_panes = PanedWindow(master, bg='#BF98A0')
        self.vert_panes.pack(fill=BOTH, expand=1)

        # Left
        style = ttk.Style()
        style.configure('TButton', foreground='black', background='#B0D7FF')
        self.onto_viewer = Treeview(self.vert_panes, selectmode='browse', style='TButton')
        self.vert_panes.add(self.onto_viewer)
        self.onto_viewer_scroll_bar = Scrollbar(self.vert_panes, orient='vertical', command=self.onto_viewer.yview)
        self.vert_panes.add(self.onto_viewer_scroll_bar)
        self.onto_viewer.configure(yscrollcommand=self.onto_viewer_scroll_bar.set)
        self.onto_viewer.bind("<Double-1>", self.expand_onto_viewer)

        # Right
        self.horz_panes = PanedWindow(self.vert_panes, orient=VERTICAL, bg='#BF98A0')
        self.vert_panes.add(self.horz_panes)

        # Top
        self.text_pad = ScrolledText(self.horz_panes, bg='#EAE8FF')
        self.horz_panes.add(self.text_pad)

        # Bottom
        self.term_viewer = ScrolledText(self.horz_panes, bg='#B0D7FF')
        self.horz_panes.add(self.term_viewer)

        ontology_menu_commands = [('Load ontology from file', self.load_ontology_command)]
        self.add_menu_to_main_menu('Ontology', ontology_menu_commands)
        self.v = StringVar()

    def load_ontology_command(self, file=None, onto_name=None, roots=None):
        if file is None:
            file = filedialog.askopenfile(parent=self.master, mode='rb', title='Select a file')
        if file is not None:
            if onto_name is None:
                onto_name = simpledialog.askstring('Name', 'Enter a name for this ontology')
            if roots is None:
                roots = simpledialog.askstring('Roots', 'Enter the names of the roots for this ontology').split(',')
            print('Loading {}'.format(file))
            self.ontos[onto_name] = {'onto': obonet.read_obo(file), 'roots': roots}

            self.display_onto(onto_name)
            self.ontos[onto_name]['id_to_name'] = {id_: data['name']
                                                   for id_, data in self.ontos[onto_name]['onto'].nodes(data=True)}
            self.ontos[onto_name]['name_to_id'] = {data['name']: id_
                                                   for id_, data in self.ontos[onto_name]['onto'].nodes(data=True)}

    def display_term(self, term, onto_name):
        term_data = self.ontos[onto_name]['onto'].node[self.ontos[onto_name]['name_to_id'][term]]

        self.term_viewer.configure(state='normal')
        self.term_viewer.delete('1.0', END)
        for label, value  in term_data.items():
            self.term_viewer.insert(END, '{}:\n\t{}\n'.format(label, value))
        self.term_viewer.configure(state='disabled')

    def display_onto(self, onto_name):

        name_id = self.onto_viewer.insert('', END, text=onto_name, value=onto_name)

        for root in self.ontos[onto_name]['roots']:
            self.onto_viewer.insert(name_id, END, text=root, value=onto_name)

    def expand_onto_viewer(self, _):
        iid = self.onto_viewer.selection()[0]
        term = self.onto_viewer.item(iid, 'text')
        onto_name = self.onto_viewer.item(iid, 'value')[0]

        self.display_term(term, onto_name)

        if self.onto_viewer.parent(iid) != '':
            subterms = get_subterms(term, self.ontos[onto_name]['onto'],
                                    self.ontos[onto_name]['id_to_name'],
                                    self.ontos[onto_name]['name_to_id'])
            for s in subterms:
                self.onto_viewer.insert(iid, END, text=s, value=onto_name)

    def annotate_text(self, _):
        self.text_pad.tag_add()

    def run(self, preload_annotation_file=None, preload_ontology=None):
        self.vert_panes.pack()
        self.master.state('zoomed')
        self.master.configure(bg='black')

        if len(preload_ontology) == 3:
            self.load_ontology_command(file=preload_ontology['File'],
                                       onto_name=preload_ontology['Name'], roots=preload_ontology['Roots'])

        if len(preload_annotation_file) == 1:
            self.open_command(file_name=preload_annotation_file['File'])

        self.master.mainloop()


def test_gui():
    root = Tk(className='My App')

    gui = AnnotationGUI(master=root)
    gui.run()

if __name__ == '__main__':
    test_gui()

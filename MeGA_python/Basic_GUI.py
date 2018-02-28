import tkinter as tk
from tkinter import Frame, Menu, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText


class BasicGUI(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.text_pad = ScrolledText(master, width=100, height=80)

        self.menu = Menu(self.master)
        self.master.config(menu=self.menu)
        filemenu_commands = [('Open...', self.open_command),
                             ('Save', self.save_command), ('', ''),
                             ('Exit', self.exit_command)]
        self.add_menu_to_main_menu('File', filemenu_commands)

        helpmenu_commands = [('About...', self.about_command)]
        self.add_menu_to_main_menu('Help', helpmenu_commands)

    def open_command(self, file_name=None):
        if file_name is None:
            file = filedialog.askopenfile(parent=self.master, mode='r', title='Select a file')
        else:
            file = open(file_name, 'r')

        if file is not None:
            print('Opening {}'.format(file.name))
            contents = file.read()
            self.text_pad.insert('1.0', contents)
            file.close()

    def save_command(self):
        file = filedialog.asksaveasfile(mode='w')
        if file is not None:
            data = self.text_pad.get('1.0', tk.END + '-1c')
            file.write(data)
            file.close()

    def exit_command(self):
        if messagebox.askokcancel('Quit', 'Do you really want to quit?'):
            self.master.destroy()

    @staticmethod
    def about_command():
        messagebox.showinfo(
            'About', 'Just Another TextPad \n '
                     'Copyright \n '
                     'HPL, University of Colorado, Anschutz Medical Campus. 2017'
                            )

    def add_menu_to_main_menu(self, name, commands):
        newmenu = Menu(self.menu)
        self.menu.add_cascade(label=name, menu=newmenu)
        for label, command in commands:
            if label is '':
                newmenu.add_separator()
            else:
                newmenu.add_command(label=label, command=command)

    def run(self):
        self.text_pad.pack()
        self.master.state('zoomed')
        self.master.mainloop()

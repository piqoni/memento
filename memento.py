#!/usr/bin/env python
from Tkinter import Entry, Tk, GROOVE, StringVar, Listbox, END, ACTIVE, Label, LEFT, RIGHT
import re
import csv
import os
import tkFont
import clipboard
import subprocess
import webbrowser

class AutocompleteEntry(Entry):
    def __init__(self, autocompleteList, *args, **kwargs):

        # Listbox length
        self.listboxLength = kwargs.pop('listboxLength', 12)
        self.listboxFontSize = tkFont.Font(size=18)

        # Custom matches function
        if 'matchesFunction' in kwargs:
            self.matchesFunction = kwargs['matchesFunction']
            del kwargs['matchesFunction']
        else:
            def matches(fieldValue, acListEntry):
                pattern = re.compile('.*' + re.escape(fieldValue) + '.*', re.IGNORECASE)
                return re.match(pattern, acListEntry)

            self.matchesFunction = matches

        Entry.__init__(self, *args, **kwargs)
        self.focus()

        self.autocompleteList = autocompleteList

        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Return>", self.selection)
        self.bind("<Up>", self.moveUp)
        self.bind("<Down>", self.moveDown)

        self.listboxUp = False

    def update_content_text(self, event):
        w = event.widget
        try:
            index = int(w.curselection()[0])
        except IndexError:
            return
        value = w.get(index)
        clipboard_content = autocompleteList.get(value)[0]
        content['text'] = clipboard_content

    def changed(self, name, index, mode):
        if self.var.get() == '':
            if self.listboxUp:
                content['text'] = ''
                self.listbox.destroy()
                self.listboxUp = False
        else:
            words = self.comparison()
            if words:
                if not self.listboxUp:
                    self.listbox = Listbox(width=self["width"], height=self.listboxLength, font=self.listboxFontSize)
                    self.listbox.bind('<<ListboxSelect>>', self.update_content_text)
                    self.listbox.bind("<Return>", self.selection)
                    self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.listboxUp = True

                self.listbox.delete(0, END)
                for w in words:
                    self.listbox.insert(END, w)
                    self.listbox.see(0)  # Scroll!
                    self.listbox.selection_set(first=0)
                    value = self.listbox.get(ACTIVE);

                    clipboard_content = autocompleteList.get(value)[0]
                    content['text'] = clipboard_content
            else:
                if self.listboxUp:
                    content['text'] = ''
                    self.listbox.destroy()
                    self.listboxUp = False

    def selection(self, event):
        if self.listboxUp:
            self.var.set(self.listbox.get(ACTIVE))
            value = self.listbox.get(ACTIVE);
            data = autocompleteList.get(value)
            content = data[0]
            is_command = data[1]
            is_website = data[2]

            if is_command == '1':
                self.execute(content)
            elif is_website == '1':
                self.open_website(content)

            self.listbox.destroy()
            self.listboxUp = False
            self.icursor(END)
            self.copy_value(content)
            self.quit()
    
    def open_website(self, url):
        webbrowser.open(url)

    def execute(self, command):
        p = subprocess.Popen(command,
                             bufsize=2048, shell=True, stdin=subprocess.PIPE)
        (output, err) = p.communicate()
        p_status = p.wait()

    def copy_value(self, value):
        clipboard.copy(value)

    def moveUp(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]

            if index != '0':
                self.listbox.selection_clear(first=index)
                index = str(int(index) - 1)

                self.listbox.see(index)  # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)
            self.listbox.event_generate("<<ListboxSelect>>", when="tail")

    def moveDown(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]

            if index != END:
                self.listbox.selection_clear(first=index)
                index = str(int(index) + 1)

                self.listbox.see(index)
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)
            self.listbox.event_generate("<<ListboxSelect>>", when="tail")

    def quit(self):
        root.quit()

    def comparison(self):
        return [w for w in self.autocompleteList if self.matchesFunction(self.var.get(), w)]


def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w / 2 - size[0] / 2
    y = h / 2 - size[1] / 2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))


def matches(fieldValue, acListEntry):
    pattern = re.compile('.*' + re.escape(fieldValue) + '.*', re.IGNORECASE)
    return re.match(pattern, acListEntry)


def close(event):
    root.destroy()


def center_splash_screen(root, width, height):
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    x = w / 2 - width / 2
    y = h / 2 - height / 2
    root.geometry("%dx%d+%d+%d" % ((width, height) + (x, y)))


if __name__ == '__main__':
    root = Tk()
    root.minsize(width=200, height=390)
    root.wm_attributes('-alpha',0.8)
    root.wm_attributes('-type', 'combo')
    center_splash_screen(root, 1000, 300)

    root.bind('<Escape>', close)
    root.bind('<Control-w>', close)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    # JSON
    # with open(dir_path + '/taskdata.json') as data_file:
    #     autocompleteList = { d['id'] : d['value'] for d in loads(data_file.read())}

    with open(dir_path + '/memento.csv') as data_file:
        autocompleteList = {rows[0]: (rows[1], rows[2], rows[3]) for rows in csv.reader(data_file)}

    search_list = list(autocompleteList.keys())

    content = Label(root,
                    justify=LEFT,
                    padx=10,
                    pady=10,
                    width=50,
                    wraplength=250,
                    font=("Helvetica", 13),
                    text='')

    entry = AutocompleteEntry(search_list, root, listboxLength=12, width=35, matchesFunction=matches, relief=GROOVE,
                              font="Helvetica 20", justify="center", bg="white", fg="black",
                              disabledbackground="#1E6FBA", disabledforeground="white", highlightbackground="black",
                              highlightcolor="white", highlightthickness=1, bd=0)
    entry.grid(row=0, column=0)
    content.grid(rowspan=10, column=1)
    root.mainloop()
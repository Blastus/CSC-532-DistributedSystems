import os
import sys
import _thread
import time
import traceback

import compiler
import interface
import processor
import safetkinter
import threadbox


################################################################################

class Example(safetkinter.Tk):

    @classmethod
    def main(cls):
        root = cls.get_root()
        io = TkinterIO(root)
        filename = safetkinter.Open(root,
                                    filetypes=(('Program Files', '.ws'),
                                               ('All Files', '*')),
                                    initialdir=os.path.dirname(sys.argv[0]),
                                    parent=root,
                                    title='Please select a program to run.').show()
        try:
            with open(filename) as file:
                source = file.read()
        except OSError:
            io.handle_error()
        else:
            root.title(os.path.basename(filename) + ' - ' + root.title())
            my_compiler = compiler.Compiler(compiler.Prototype.SYMBOLS)
            try:
                code = my_compiler.compile(source)
            except ValueError:
                io.handle_error()
            else:
                cpu = processor.Processor(code, io)
                try:
                    cpu.run()
                except (EOFError, KeyboardInterrupt):
                    io.handle_error()
        time.sleep(10)

    @classmethod
    def get_root(cls):
        courier = [_thread.allocate_lock()]
        courier[0].acquire()
        _thread.start_new_thread(cls.run_root, (courier,))
        with courier[0]:
            return courier[1]

    @classmethod
    def run_root(cls, courier):
        courier.append(cls())
        courier[0].release()
        courier[1].mainloop()

    def __init__(self):
        super().__init__()
        self.title(type(self).__name__)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


################################################################################

class TkinterIO(interface.TkinterIO):
    from tkinter.constants import NSEW

    def __init__(self, master):
        super().__init__(master)
        self.tag_config('error', foreground='red')
        self.grid(sticky=self.NSEW)

    @threadbox.MetaBox.thread
    def handle_error(self):
        self.mark_set(self.INSERT, self.END)
        prefix = '' if self.line_begin else '\n'
        self.insert(self.INSERT, prefix + traceback.format_exc(), 'error')


################################################################################

if __name__ == '__main__':
    Example.main()

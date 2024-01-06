from itertools import cycle, count
from typing import Iterator
from SongLexer import _REV_TRANSLATE_TABLE, REGULAR_NOTES, SHIFTED_NOTES
import tkinter as tk

def notes_iterator (startNote:str='c', startOctave:int=4) -> Iterator[str]:
    "Infinite iterator for successive notes (major c): 'c4','d4','e4','f4','g4','a4',b4','c5',..."
    letters = "cdefgab"
    i = letters.find(startNote)
    letter_iter = cycle(letters[i:] + letters[:i])
    DIF = 0.1428571428572
    octave_iter = count(startOctave + DIF*i, DIF)
    return (n+str(int(o)) for o,n in zip(octave_iter, letter_iter))

class LinesColumn (tk.Frame):
    def __init__ (self, master):
        super().__init__(master)
        self.startGap = tk.Frame(self, height=27*11-5)
        self.startGap.pack(anchor='n')
        self.lines :list[tk.Label] = []
        self.gaps :list[tk.Frame] = []
        for i in range(5):
            self.lines.append( tk.Label(self, text="-"*24, height=2) )
            self.lines[i].pack(anchor='n')
            self.gaps.append( tk.Frame(self, height=16) )
            self.gaps[i].pack(anchor='n')
        self.midGap = tk.Frame(self, height=54)
        self.midGap.pack(anchor='n')
        for i in range(5):
            self.lines.append( tk.Label(self, text="-"*24, height=2) )
            self.lines[5+i].pack(anchor='n')
            self.gaps.append( tk.Frame(self, height=16) )
            self.gaps[5+i].pack(anchor='n')
        


class LeftColumn (tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.buttons :dict[str, tk.Button] = {}
        for key,note in reversed([_ for _ in zip(REGULAR_NOTES, notes_iterator('c',2))]):
            printer = (lambda k: (lambda: print(k, end='', flush=True)))(key)
            self.buttons[note] = tk.Button(self, text=note[0], command=printer, font='arial 8', bg='white', width=2)
            self.buttons[note].pack(anchor='n')

class RightColumn (tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.buttons :dict[str, tk.Button|tk.Frame] = {}
        self.startGap = tk.Frame(self, height=(27/2))
        self.startGap.pack(anchor='n')
        for key,note in reversed([_ for _ in zip(REGULAR_NOTES[:-1], notes_iterator('c',2))]):
            key = _REV_TRANSLATE_TABLE[key]
            if key not in SHIFTED_NOTES:
                self.buttons[note] = tk.Frame(self, height=(27))
                self.buttons[note].pack(anchor='n')
            else:
                printer = (lambda k: (lambda: print(k, end='', flush=True)))(key)
                self.buttons[note] = tk.Button(self,
                    text=note[0]+"#", command=printer, font='arial 8', width=2,
                    bg='#222222', fg='white',
                    activebackground='#333333', activeforeground="white"
                )
                self.buttons[note].pack(anchor='n')

class CentreConsole (tk.Frame):
    def __init__(self, master):
        super().__init__(master, padx=16, pady=16)
        self.button_newline = tk.Button(self, text='newline', command=lambda: print(), height=2, width=6)
        self.button_newline.pack(anchor='center')

def main ():
    rootWindow = tk.Tk()
    rootWindow.title("Tong Player")
    linesColumn = LinesColumn(rootWindow)
    leftColumn = LeftColumn(rootWindow)
    rightColumn = RightColumn(rootWindow)
    centreConsole = CentreConsole(rootWindow)
    rootWindow.minsize(256, 128)
    linesColumn.grid(row=0, column=0, sticky='nsew')
    leftColumn.grid(row=0, column=1, sticky='nsew')
    rightColumn.grid(row=0, column=2, sticky='nsew')
    centreConsole.grid(row=0, column=3, sticky='nsew')
    rootWindow.mainloop()
    print()

if __name__ == "__main__": main()

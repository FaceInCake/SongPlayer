
from typing import Callable, Any, NamedTuple
from random import random
from pynput.keyboard import Controller, Key, KeyCode, HotKey, Listener
from threading import Thread
from time import sleep, perf_counter as get_current_time
import tkinter as tk
from tkinter.messagebox import showerror
from tkinter.simpledialog import askstring
from tkinter.filedialog import askopenfilename
from SongGrammer import RegularGroup, parser, Note, Code, NoteGroup, Atom, Rest, ChordGroup, ScaleGroup, SharpNote



def parse_text_to_tree (text:str) -> RegularGroup:
    parser.parse(text)
    return RegularGroup(parser.symstack[1].value)

class Action:
    __slots__ = "time", "note", "press"
    def __init__ (self, time:float, note:Note, press:bool):
        self.time :float = time
        self.note :Note = note
        self.press :bool = press
    
def parse_tree_to_action_list (root:RegularGroup) -> list[Action]:
    """Takes the output of the YACC parser and
    returns a list of keyboard events to play back using"""
    actionList :list[Action] = []
    timeFactor :float = 0.5 # 120bpm

    def append_atom (atom:Atom, time:float, duration:float) -> float:
        "Returns the final duration of the atom"
        nonlocal actionList, timeFactor
        if   isinstance(atom, Note):
            if not isinstance(atom, Rest):
                TINY_NUM :float = 0.0001
                actionList.append(Action(time, atom, True))
                actionList.append(Action(time+duration*timeFactor-TINY_NUM, atom, False))
            return duration * timeFactor
        elif isinstance(atom, NoteGroup):
            return parse_tree(atom, time, duration)
        elif isinstance(atom, Code):
            if atom.key == "bpm":
                timeFactor = 60 / (atom.value or 120)
            return 0.0
        else:
            raise TypeError("Given `atom` must be of type Note/NoteGroup/Code, but it wasn't: ({})" % (type(atom)))

    def parse_tree (parent:NoteGroup, time:float, duration:float) -> float:
        "Recursive function for navigating a NoteGroup tree of Notes, returns total duration of `parent`"
        if len(parent)==0: return 0.0
        if isinstance(parent, ChordGroup):
            return max(append_atom(node,time,duration) for node in parent)
        else:
            if isinstance(parent, ScaleGroup):
                duration = duration / len(parent)
            oldTime :float = time
            for node in parent:
                time += append_atom(node, time, duration)
            return time - oldTime

    parse_tree(root, 0.0, 1.0)
    return sorted(actionList, key=lambda x: x.time or 0.0)
# END parse_tree_to_action_list

def play_action_list (actionList:list[Action], *, drift:float=0.0, noise:float=0.0) -> Thread:
    def __play_action_list (actionList:list[Action]):
        keyboard = Controller()
        startTime :float = get_current_time()
        targetTime :float = 0.0
        curDrift :float = 0.0
        for act in actionList:
            curDrift += (random()*2-1) * drift
            act.time += curDrift + (random()*2-1) * noise
        actionList = sorted(actionList, key=lambda a: a.time)
        for act in actionList:
            targetTime = startTime + act.time
            while get_current_time() < targetTime:
                pass # sleep(0.0)
            if keyboardMonitor.activeThread is None: return
            if act.press is False:
                keyboard.release(act.note.key)
            else:
                if isinstance(act.note, SharpNote):
                    with keyboard.pressed(Key.shift):
                        keyboard.press(act.note.key)
                else:
                    keyboard.press(act.note.key)
        keyboardMonitor.activeThread = None
    thread = Thread(
        target=__play_action_list,
        args=(actionList,)
    )
    if keyboardMonitor.activeThread is None:
        keyboardMonitor.activeThread = thread
        thread.start()
    return thread

class KeyboardMonitor:

    __slots__ = "shift", "ctrl", "alt", "__listener", "__hotkeys", "activeThread"
    def __init__(self) -> None:
        self.shift :bool = False
        self.ctrl :bool = False
        self.alt :bool = False
        self.__listener = Listener(
            on_press=self.__on_press_callback,
            on_release=self.__on_release_callback
        )
        self.__hotkeys :dict[str, Callable[[],Thread]] = {}
        self.activeThread :Thread|None = None
    
    def __del__ (self):
        self.__listener.stop()

    def start (self): self.__listener.start()
    def stop (self): self.__listener.stop()

    def __contains__ (self, o:str) -> bool:
        return o in self.__hotkeys

    def add_hotkey (self, key:str, callback:Callable[[],Thread]):
        if key not in self.__hotkeys:
            self.__hotkeys[key] = callback
    
    def remove_hotkey (self, key:str):
        if key in self.__hotkeys:
            self.__hotkeys.pop(key)

    def __on_press_callback (self, e:Key|KeyCode|None):
        if e is None:
            print("Error: Key event with no key event ???")
            return
        char = e.name if isinstance(e, Key) else e.char
        if self.activeThread:
            if e == Key.esc:
                keyboardMonitor.activeThread = None
            return
        match char:
            case 'shift': self.shift = True
            case 'ctrl': self.ctrl = True
            case 'alt': self.alt = True
        if char in self.__hotkeys:
            self.__hotkeys[char]()

    def __on_release_callback (self, e:Key|KeyCode|None):
        if self.activeThread: return
        if e is None: return
        char = e.name if isinstance(e, Key) else e.char
        match char:
            case 'shift': self.shift = False
            case 'ctrl': self.ctrl = False
            case 'alt': self.alt = False

keyboardMonitor :KeyboardMonitor = KeyboardMonitor()

################################################################
#                            GUI                               #
################################################################

class TongListItem:
    __slots__ = "filePath", "keyBind", "actionList"
    def __init__(self, filePath:str, actionList:list[Action]=[], keyBind:str="...") -> None:
        self.filePath :str = filePath
        self.keyBind :str = keyBind
        self.actionList :list[Action] = actionList

class GUI_TongListItem:
    MaxButtonWidth :int = 1
    
    __slots__ = "tong", "keyBindButton", "tongFileName", "refreshButton"
    def __init__(self, master, tong:TongListItem, row:int):
        self.tong = tong
        self.keyBindButton = tk.Button(master,
            background="#D6D4CE",
            font="Arial",
            bd=2,
            command=self.change_keybind,
            justify="center",
            text=self.tong.keyBind
        )
        self.tongFileName = tk.Label(master,
            font="Arial", text=tong.filePath, justify='left', anchor='w'
        )
        self.refreshButton = tk.Button(master,
            background="#69F26D", bd=2,
            justify='center', text="R", command=self.refresh_tong
        )
        self.keyBindButton.grid(row=row, column=0, padx=4)
        self.tongFileName.grid(row=row, column=1, padx=4, sticky='w')
        self.refreshButton.grid(row=row, column=2, padx=4)
    
    def refresh_tong (self):
        self.tong.actionList = parse_tree_to_action_list(
            parse_text_to_tree(
                open(self.tong.filePath, 'r').read()
            )
        )

    def change_keybind (self):
        answer = askstring("Rebind hotkey", "Please enter which key you'd like to bind to",
            initialvalue=self.tong.keyBind if self.tong.keyBind != "..." else None
        )
        if answer is None: return
        try: _ = HotKey.parse(answer)
        except ValueError: return
        if answer in keyboardMonitor:
            showerror("Invalid keybind", "That key is already bound to something else")
            return
        if self.tong.keyBind != "...":
            keyboardMonitor.remove_hotkey(self.tong.keyBind)
        self.tong.keyBind = answer
        keyboardMonitor.add_hotkey(answer, lambda: play_action_list(self.tong.actionList, drift=0.0, noise=0.0))
        self.keyBindButton.config(text=answer)

class GUI_TongList (tk.Frame):

    __slots__ = "tongs", "addButton"
    def __init__(self, master, initialList:list[TongListItem]=[]):
        super().__init__(master)
        self.tongs :list[GUI_TongListItem] = []
        self.addButton = tk.Button(self, background='green', text='+', command=self.add_new_tong)
        self.addButton.grid(column=0, row=0, sticky='w')
        for t in initialList: self.append(t)

    def add_new_tong (self):
        fileName = askopenfilename(defaultextension='tong', filetypes=[('Text Song', '*.tong')], title="Please supply a file")
        if fileName == "": return
        file = open(fileName, 'r')
        text = file.read()
        tree = parse_text_to_tree(text)
        actionList = parse_tree_to_action_list(tree)
        self.append(TongListItem(fileName, actionList=actionList))
        file.close()
    
    def append (self, tong:TongListItem):
        g = GUI_TongListItem(self, tong, len(self.tongs)+1)
        self.tongs.append(g)
        self.addButton.grid(column=1, row=len(self.tongs)+1, sticky='w')

rootWindow = tk.Tk()
rootWindow.title("Tong Player")
temp = GUI_TongList(rootWindow)
temp.pack(side='top', anchor='n')
rootWindow.minsize(256, 128)

################################################################
#                           Main                               #
################################################################

if __name__ == "__main__":
    keyboardMonitor.start()
    rootWindow.mainloop()
    keyboardMonitor.stop()

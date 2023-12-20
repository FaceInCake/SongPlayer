
from typing import Callable, Any, NamedTuple
from time import time as get_current_time
import keyboard
from keyboard import KeyboardEvent
from ply import lex, yacc
import tkinter as tk


lexer = lex.lex()
parser = yacc.yacc()

def parse_text_to_tree (text:str) -> RegularGroup:
    parser.parse(text)
    return RegularGroup(parser.symstack[1].value)

class Beat (NamedTuple):
    time : float
    duration : float
    note : Note

class CodeAction (NamedTuple):
    time : float
    code : Code
    
def parse_tree_to_key_event_list (root:RegularGroup) -> list[Beat]:
    """Takes the output of the YACC parser and
    returns a list of keyboard events to play back using"""
    actionList :list[Beat] = []
    timeFactor :float = 0.5 # 120bpm

    def append_atom (atom:Atom, time:float, duration:float) -> float:
        "Returns the final duration of the atom"
        nonlocal actionList, timeFactor
        if   isinstance(atom, Note):
            if not isinstance(atom, Rest):
                actionList.append(Beat(time, duration*timeFactor, atom)) # type: ignore (pylance thinks timeFactor is unbound, its not)
            return duration * timeFactor # type: ignore (pylance thinks timeFactor is unbound, its not)
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
    return actionList

# END parse_tree_to_key_event_list

def shift_key (down:bool, time:float) -> KeyboardEvent:
    SHIFT_SCAN_CODE :int = keyboard.key_to_scan_codes('shift')[0]
    return KeyboardEvent('down' if down else 'up', SHIFT_SCAN_CODE, 'shift', time)

def action_list_to_key_list (actionList:list[Beat]) -> list[KeyboardEvent]:
    curTime :float = get_current_time()
    keList :list[KeyboardEvent] = []
    TINY_NUM :float = 0.00001
    for act in actionList:
        scanCode :int = keyboard.key_to_scan_codes(act.note.key)[0]
        if isinstance(act.note, SharpNote):
            keList.append(shift_key(True, curTime + act.time))
        keList.append(KeyboardEvent(
            'down', scanCode, act.note.key,
            curTime + act.time
        ))
        if isinstance(act.note, SharpNote):
            keList.append(shift_key(False, curTime + act.time))
        keList.append(KeyboardEvent(
            'up', scanCode, act.note.key,
            curTime + act.time + act.duration - TINY_NUM
        ))
    return sorted(keList, key=lambda k: k.time or 0.0)

def action_list_to_key_list_tapping (actionList:list[Beat]) -> list[KeyboardEvent]:
    curTime :float = get_current_time()
    keList :list[KeyboardEvent] = []
    TINY_NUM :float = 0.00001
    for act in actionList:
        scanCode :int = keyboard.key_to_scan_codes(act.note.key)[0]
        if isinstance(act.note, SharpNote):
            keList.append(shift_key(True, curTime + act.time + TINY_NUM*len(keList)))
        keList.append(KeyboardEvent(
            'down', scanCode, act.note.key,
            curTime + act.time + TINY_NUM*len(keList)
        ))
        if isinstance(act.note, SharpNote):
            keList.append(shift_key(False, curTime + act.time + TINY_NUM*len(keList)))
        keList.append(KeyboardEvent(
            'up', scanCode, act.note.key,
            curTime + act.time + TINY_NUM*len(keList)
        ))
    return sorted(keList, key=lambda k: k.time or 0.0)

def play_tong (e:KeyboardEvent, filePath:str):
    file = open(filePath, "r")
    text :str = file.read()
    tree = parse_text_to_tree(text)
    actionList :list[Beat] = parse_tree_to_key_event_list(tree)
    keyEventList = action_list_to_key_list_tapping(actionList)
    keyboard.play(keyEventList)
    print("Done!")

################################################################
#                            GUI                               #
################################################################

class TongListItem (NamedTuple):
    filePath :str
    keyBind :str = "..."
    keyList :list[KeyboardEvent] = []

class GUI_TongListItem (tk.Frame):
    MaxButtonWidth :int = 1
    
    __slots__ = "tong", "keyBindButton", "tongFileName", "refreshButton"
    def __init__(self, master, tong:TongListItem):
        super().__init__(master)
        self.tong = tong
        self.keyBindButton = tk.Button(self,
            background="#D6D4CE",
            font="Arial",
            bd=2,
            command=lambda: print("Bind button pressed"),
            justify="center",
            text=self.tong.keyBind
        )
        self.tongFileName = tk.Label(self,
            font="Arial", height=20, text=tong.filePath
        )
        self.refreshButton = tk.Button(self,
            background="#69F26D", bd=2,
            justify='center', text="R", command=lambda: print("Refresh")
        )
        self.keyBindButton.grid(row=0, column=0)
        self.tongFileName.grid(row=0, column=1)
        self.refreshButton.grid(row=0, column=2)
        self.pack()


rootWindow = tk.Tk()
rootWindow.title("Tong Player")
temp = GUI_TongListItem(rootWindow, TongListItem("Bibbidy obbity boo"))
rootWindow.minsize(512, 360)




################################################################
#                           Main                               #
################################################################

Key = str | int
def hook_numpad_key (key:Key, callback :Callable[[keyboard.KeyboardEvent], Any]):
    keyboard.on_press_key(key, lambda e: False if e.is_keypad else True, suppress=True)
    keyboard.on_release_key(key, lambda e: callback(e) or True if e.is_keypad else True, suppress=True)

if __name__ == "__main__":
    rootWindow.mainloop()
    # hook_numpad_key("1", lambda e: play_tong(e, "test6.tong"))
    # keyboard.wait("ctrl+z", suppress=True)

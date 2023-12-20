
from abc import ABC
from SongLexer import _TRANSLATE_TABLE


class Atom (ABC): pass

class Note (Atom):
    __slots__ = "key"
    def __init__(self, key:str):
        self.key :str = key
class RegNote (Note): pass
class SharpNote (Note):
    def __init__(self, key: str):
        super().__init__(_TRANSLATE_TABLE.get(key, key))
class Rest (Note):
    def __init__(self):
        super().__init__("")

class Code (Atom):
    __slots__ = "key", "value"
    def __init__(self, key:str, value:float|None=None):
        self.key :str = key
        self.value :float|None = value

class NoteGroup (Atom, list[Atom]):
    def __repr__(self) -> str:
        return self.__class__.__name__+super().__str__()
class RegularGroup (NoteGroup): pass
class ChordGroup (NoteGroup): pass
class ScaleGroup (NoteGroup): pass



def p_notegroup2 (p):
    "notegroup : notegroup atom"
    p[1].append(p[2])
    p[0] = p[1]

def p_atom (p):
    """atom : regular_group
            | chord_group
            | scale_group
            | note
            | code """
    p[0] = p[1]

def p_regular_group (p):
    "regular_group : APOSTROPHE notegroup APOSTROPHE"
    p[0] = RegularGroup(p[2])

def p_chord_group (p):
    "chord_group : LEFT_PAREN_SQUARE notegroup RIGHT_PAREN_SQUARE"
    p[0] = ChordGroup(p[2])

def p_scale_group (p):
    "scale_group : LEFT_PAREN_CURLY notegroup RIGHT_PAREN_CURLY"
    p[0] = ScaleGroup(p[2])

def p_note (p):
    "note : NOTE"
    p[0] = RegNote(p[1])

def p_note_shifted (p):
    "note : SHIFTED_NOTE"
    p[0] = SharpNote(p[1])

def p_note_rest (p):
    "note : REST"
    p[0] = Rest()

def p_code_2 (p):
    "code : ID EQUALS NUMBER"
    p[0] = Code(p[1], p[3])

def p_code_1 (p):
    "code : ID"
    p[0] = Code(p[1])

def p_notegroup0 (p):
    "notegroup : "
    p[0] = []

precedence = (
    ('right', 'LEFT_PAREN_SQUARE', 'LEFT_PAREN_CURLY'),
    ('left',  'NOTE', 'SHIFTED_NOTE', 'REST'),
    ('left',  'APOSTROPHE', 'NUMBER'),
    ('right', 'ID', 'EQUALS')
)

def p_error(p):
    if p is not None:
        print("Syntax error:", p)

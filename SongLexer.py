
KEY_NOTES = "1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm"
# Not key notes:    - _ = + [ ] { } \ | ; : ' " , < . > / ?
# Also not key notes:    # & ) R U A F K X N M
_TRANSLATE_TABLE = { # Keys that require the shift modifier
    '!': '1',  '@': '2',  '#': '3',  '$': '4',  '%': '5',
    '^': '6',  '&': '7',  '*': '8',  '(': '9',  ')': '0',
    '~': '`',  '_': '-',  '+': '=',  '{': '[',  '}': ']',
    '|':'\\',  ':': ';',  '"': "'",  '<': ',',  '>': '.',  '?': '/',
    'A': 'a',  'B': 'b',  'C': 'c',  'D': 'd',  'E': 'e',
    'F': 'f',  'G': 'g',  'H': 'h',  'I': 'i',  'J': 'j',
    'K': 'k',  'L': 'l',  'M': 'm',  'N': 'n',  'O': 'o',
    'P': 'p',  'Q': 'q',  'R': 'r',  'S': 's',  'T': 't',
    'U': 'u',  'V': 'v',  'W': 'w',  'X': 'x',  'Y': 'y',  'Z': 'z',  
}
REGULAR_NOTES = "".join(key for key in KEY_NOTES if key not in _TRANSLATE_TABLE)
SHIFTED_NOTES = "".join(key for key in KEY_NOTES if key     in _TRANSLATE_TABLE)



states = (
    ('code', 'exclusive'),
)

tokens = (
    "NOTE",
    "SHIFTED_NOTE",
    "REST",
    "LEFT_PAREN_SQUARE",
    "RIGHT_PAREN_SQUARE",
    "LEFT_PAREN_CURLY",
    "RIGHT_PAREN_CURLY",
    "APOSTROPHE",
    "LEFT_PAREN_ANGLED",
    "RIGHT_PAREN_ANGLED",
    "ID",
    "EQUALS",
    "NUMBER",
)

def t_COMMENT (_):
    r";.*?(?:;|\n|$)"
    pass
def t_LEFT_PAREN_ANGLED (t):
    r"<"
    t.lexer.begin('code')
def t_code_RIGHT_PAREN_ANGLED (t):
    r">"
    t.lexer.begin('INITIAL')
def t_code_ID (t):
    r"[bB][pP][mM]"
    t.value = t.value.lower()
    return t
def t_code_NUMBER (t):
    r"\d+(?:\.\d+)?"
    t.value = float(t.value)
    return t
t_REST = r"~"
t_LEFT_PAREN_SQUARE = r"\["
t_RIGHT_PAREN_SQUARE = r"\]"
t_LEFT_PAREN_CURLY = r"{"
t_RIGHT_PAREN_CURLY = r"}"
t_APOSTROPHE = r"'"
t_NOTE = r"[" + REGULAR_NOTES + "]"
t_SHIFTED_NOTE = "[" + SHIFTED_NOTES + "]"

t_code_EQUALS = r"="

t_ignore = " \t\n"
t_code_ignore = " \t\n"

def t_error (t):
    print('Illegal character "%s"' % t.value[0])
    t.lexer.skip(1)

def t_code_error (t):
    print('Illegal code character "%s"' % t.value[0])
    t.lexer.skip(1)

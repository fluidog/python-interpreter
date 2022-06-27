#! /bin/env python3

from ply.lex import lex

# List of token names.   This is always required
tokens = (
#    'PLUS',
#    'MINUS',
#    'MULTI',
#    'DIVIDE',
#    'LPAREN',
#    'RPAREN',
#    'LBRACE',
#    'RBRACE',
    'NUMBER',
    'STRING',
    'IDENTIFIER',
    'IF',
    'ELSE',
    'WHILE',
    'EQ',
    'NE',
    'AND',
    'OR',
    'DEF',
    'CLASS',
    'NULL',
)

def my_lexer():
    # Regular expression rules for simple tokens
    t_EQ = r'=='
    t_NE = r'!='
    t_AND = r'&&'
    t_OR = r'\|\|'
    t_STRING = r'\"[^\"]*\"|\'[^\']*\''

    # Literal string containing all valid digits
    literals = r',.+-*/()[]{}=;<>!:'

    # A regular expression rule with some action code
    def t_NUMBER(t):
        r'\d+'
        t.value = int(t.value)    
        return t

    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'def': 'DEF',
        'class': 'CLASS',
        'null': 'NULL',
    }
    def t_IDENTIFIER(t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'    
        t.type = reserved.get(t.value, 'IDENTIFIER')
        return t

    # Define a rule so we can track line numbers
    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    t_ignore_COMMENT = r'//.*|\#.*'

    # Error handling rule
    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    return lex()


if __name__ == '__main__':
    from rich import print
    print('Just for test in:', __file__)

    lexer = my_lexer()

    data = '''
    33 +  if 4( =else} +{ 5 "adgasd"
    '''
    lexer.input(data)
    # tok.type, tok.value, tok.lineno, tok.lexpos
    print(
        [ (tok.value, tok.type) for tok in lexer ]
    )






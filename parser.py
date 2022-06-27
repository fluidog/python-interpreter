#! /bin/env python3

import logging

from ply.yacc import yacc

from lexer import tokens

class AstNode(object):
    pass

class BinOp(AstNode):
    def __init__(self, left, op, right) -> None:
        self.left = left
        self.right = right
        self.op = op

class Number(AstNode):
    def __init__(self, value):
        self.value = value

class String(AstNode):
    def __init__(self, value) -> None:
        self.value = value

class Null(AstNode):
    pass

class Map(AstNode):
    def __init__(self, key, value):
        self.body = {key: value}

    def append_item(self, key, value):
        self.body[key] = value

# Get a item of list or dictionary -  X[index]
class GetItem(AstNode):
    def __init__(self, container, index):
        self.container = container
        self.index = index
        
class Block(AstNode):
    def __init__(self, stmt):
        self.body = [ stmt ]

    def append_stmt(self, stmt):
        self.body.append(stmt)


class IfStmt(AstNode):
    def __init__(self, cond, body) -> None:
        self.cond = cond
        self.body = body

    def add_else_body(self, else_body):
        self.else_body = else_body

class SetVar(AstNode):
    def __init__(self, name, value) -> None:
        self.name = name
        self.value = value

class GetVar(AstNode):
    def __init__(self, name):
        self.name = name

class ParamList(AstNode):
    def __init__(self, param=None) -> None:
        self.body = []
        if param:
            self.body.append(param)

    def add_param(self, param):
        self.body.append(param)

class Defunc(AstNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class ArgList(AstNode):
    def __init__(self, arg=None) -> None:
        self.body = []
        if arg:
            self.body.append(arg)
    
    def add_arg(self, arg):
        self.body.append(arg)

class Call(AstNode):
    def __init__(self, func, args) -> None:
        self.func = func
        self.args = args

class DefCls(AstNode):
    def __init__(self):
        self.body = []
    def add_attr(self, attr):
        self.body.append(attr)
    def set_name(self, name):
        self.name = name

class SetAttr(AstNode):
    def __init__(self, obj, attr, value) -> None:
        self.obj = obj
        self.attr = attr
        self.value = value

# Get class attribute -  X.attr
class GetAttr(AstNode):
    def __init__(self, obj, attr):
        self.obj = obj
        self.attr = attr
 
def my_parser():
    start = 'block'
    # start = 'stmt'

    precedence = (
        ('left', ';'),
        ('right', '='),
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', '>', '<', 'EQ', 'NE'),
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('left', '.'),
    )

    def p_binary_operators(p):
        '''
        expr ::= expr '*' expr
            | expr '/' expr
            | expr '+' expr
            | expr '-' expr
            | expr EQ expr
            | expr NE expr
            | expr '<' expr
            | expr '>' expr
            | expr AND expr
            | expr OR expr
        '''
        p[0] = BinOp(*p[1:])

    def p_expr_paren(p):
        '''
        expr ::= '(' expr ')'
        '''
        p[0] = p[2]

    def p_expr_number(p):
        '''
        expr ::= NUMBER
        '''
        p[0] = Number(p[1])

    def p_expr_string(p):
        '''
        expr ::= STRING
        '''
        p[0] = String(p[1][1:-1])  # remove quotes

    def p_expr_null(p):
        '''
        expr ::= NULL
        '''
        p[0] = Null()

    def p_Set_var(p):
        '''
        set_var ::= IDENTIFIER '=' expr
        '''
        p[0] = SetVar(p[1], p[3])
            
    def p_expr_var(p):
        '''
        expr ::= IDENTIFIER
        '''
        p[0] = GetVar(p[1])

    def p_parameter_list(p):
        '''
        parameter_list ::= IDENTIFIER
            | parameter_list ',' IDENTIFIER
            |
        '''
        if len(p) == 1: # empty parameter
            p[0] = ParamList()
        elif len(p) == 2: # one parameter
            p[0] = ParamList(p[1])
        elif len(p) == 4: # more than one parameter
            p[0] = p[1]
            p[0].add_param(p[3])
        else:
            raise Exception('Invalid parameter list')

    def p_def_func(p):
        '''
        def_func ::= DEF IDENTIFIER '(' parameter_list ')' \
            '{' block '}'
        '''
        p[0] = Defunc(p[2], p[4], p[7])

    def p_arg_list(p):
        '''
        arg_list ::= expr
            | arg_list ',' expr
            |
        '''
        if len(p) == 1:
            p[0] = ArgList()
        elif len(p) == 2:
            p[0] = ArgList(p[1])
        elif len(p) == 4:
            p[0] = p[1]
            p[0].add_arg(p[3])
            
    def p_expr_call_func(p):
        '''
        expr ::= expr '(' arg_list ')'
        '''
        p[0] = Call(p[1], p[3])

    def p_expr_def_map(p):
        '''
        item ::= expr ':' expr
            | item ',' expr ':' expr
        expr ::= '{' item '}'
        '''
        if len(p) == 4 :
            if p[1] == '{':
                p[0] = p[2]
            else:
                p[0] = Map(p[1], p[3])
        elif len(p) == 6:
            p[0] = p[1]
            p[0].append_item(p[3], p[5])
        else:
            raise Exception('Invalid map')

    def p_expr_get_item(p):
        '''
        expr ::= expr '[' expr ']'
        '''
        p[0] = GetItem(p[1], p[3])

    def p_set_attr(p):
        '''
        set_attr ::= expr '.' IDENTIFIER '=' expr
        '''
        p[0] = SetAttr(p[1], p[3], p[5])

    def p_expr_get_attr(p):
        '''
        expr ::= expr '.' IDENTIFIER
        '''
        if len(p) == 4:
            p[0] = GetAttr(p[1], p[3])

    def p_stmt(p):
        '''
        stmt ::= expr ';'
            | set_var ';'
            | set_attr ';'
            | if_stmt 
            | def_func 
            | def_cls
            | ';'
        '''
        p[0] = p[1]

    def p_block(p):
        '''
        block ::= stmt
            | block stmt
        '''
        if len(p) == 2: # first statement of list
            p[0] = Block(p[1])
        elif len(p) == 3:
            p[0] = p[1]
            p[0].append_stmt(p[2])
        else:
            raise Exception(f'Statement list length({len(p)}) error: ', p[:])

    def p_if_stmt(p):
        '''
        if_stmt ::= IF '(' expr ')' '{' block '}'
            | if_stmt ELSE '{' block '}'
        '''
        if len(p) == 8:
            p[0] = IfStmt(p[3], p[6])
        elif len(p) == 6:
            p[0] = p[1]
            p[0].add_else_body(p[4])
        else:
            raise Exception(f'If statement length({len(p)}) error: ', p[1:])

    def p_def_cls(p):
        '''
        cls_body ::= ';'
            | def_func
            | set_var ';'
            | cls_body def_func 
            | cls_body set_var ';'
        def_cls ::= CLASS IDENTIFIER '{' cls_body '}'
        '''
        if len(p) == 2 and p[1] == ';':
            p[0] = DefCls()
        elif len(p) == 2 or len(p) == 3 and p[2] == ';':
            p[0] = DefCls()
            p[0].add_attr(p[1])
        elif len(p) == 3 or len(p) == 4 and p[3] == ';':
            p[0] = p[1]
            p[0].add_attr(p[2])
        elif len(p) == 6:
            p[0] = p[4]
            p[0].set_name(p[2])
        else:
            raise Exception(f'Class length({len(p)}) error: ', p[1:])

    def p_error(p):
        raise SyntaxError(f"line {p.lineno}")
        
    return yacc()



if __name__ == '__main__':
    print('Test parser')

    from lexer import my_lexer

    lexer = my_lexer()
    # Build the parser
    parser = my_parser()

    source_file = "test.py"
    data = open(source_file, 'r').read()

    ast = parser.parse(data)
    
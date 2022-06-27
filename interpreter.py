#! /bin/env python3

from enum import Enum
import functools
from rich import print

import parser

ObjType = Enum('type', ('NUMBER','STRING','ARRAY','MAP','NULL',
        'FUNCTION','CLASS'))

class MetaObj(object):
    pass

# Just use the python native type -- NUMBER, STRING, ARRAY, NULL, MAP
# Only FUNCTION and CLASS are implemented specially

class FuncObj(MetaObj):
    Flag = Enum('Flag', ('BUILTIN','BOUNDED'))
    def __init__(self, name, params, body, scope):
        self.type = ObjType.FUNCTION
        self.name = name
        self.params = params
        self.body = body
        self.scope = scope
        self.flag = []

class BdFuncObj(FuncObj):
    def __init__(self, func, obj):
        super().__init__(func.name, func.params, func.body, func.scope)
        self.obj = obj
        self.flag = func.flag
        self.flag.append(FuncObj.Flag.BOUNDED)

class BtinFuncObj(FuncObj):
    def __init__(self, name, func):
        super().__init__(name, None, func, None)
        self.flag.append(FuncObj.Flag.BUILTIN)

class ClsObj(MetaObj):
    def __init__(self, name, bases, attr) -> None:
        self.type = ObjType.CLASS
        self.name = name
        self.bases = bases
        self.dict = attr


class Enviroemnt(object):
    def __init__(self) -> None:
        self._scope = [(None, {}), ] # [(parent_scope, {variables}), ]

    @property
    def global_scope(self):
        return self._scope[0]

    @property
    def current_scope(self):
        return self._scope[-1]

    def new_scope(self, parent_scope):
        self._scope.append((parent_scope, {}))

    def free_scope(self):
        self._scope.pop()

    def get_var(self, name):
        def get_var_helper(name, scope):
            if name in scope[1]:
                return scope[1][name]
            if scope[0]:
                return get_var_helper(name, scope[0])
            raise Exception(f'Variable not found: {name}')
        return get_var_helper(name, self.current_scope)

    def set_var(self, name, value):
        self.current_scope[1][name] = value

def interpreter(ast):
    def binop(node):
        left = eval(node.left)
        right = eval(node.right)
        op = node.op

        def compute(left, op, right):
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right
            elif op == '==':
                return left == right
            elif op == '!=':
                return left != right
            elif op == '<':
                return left < right
            elif op == '>':
                return left > right
            elif op == '&&':
                return left and right
            elif op == '||':
                return left or right
            else:
                raise Exception('Unknown operator: ' + op)

        return compute(left, op, right)

    def number(node):
        return int(node.value)

    def string(node):
        return node.value

    def null(node):
        return None

    def map(node):
        return {eval(key):eval(value) \
            for key, value in node.body.items()}

    def getitem(node):
        container = eval(node.container)
        index = eval(node.index)
        return container[index]

    def block(node):
        result = [ eval(stmt) for stmt in node.body ]
        return result[-1] # return last value of block

    def ifstmt(node):
        cond = eval(node.cond)
        if cond:
            return eval(node.body)
        elif hasattr(node, 'else_body'):
            return eval(node.else_body)
        
    def defvar(node):
        value = eval(node.value)
        env.set_var(node.name, value)

    def getvar(node):
        return env.get_var(node.name)

    def paramlist(node):
        return node.body  # [ param...] list of strings

    def defunc(node):
        # Run when call
        # params = eval(defun_node.params)
        # body = eval(defun_node.body)

        func = FuncObj(node.name, node.params, node.body,
            env.current_scope)
        env.set_var(node.name, func)

    def arglist(node):
        return [eval(arg) for arg in node.body]

    def call(node):
        func = eval(node.func)
        args = eval(node.args)

        if isinstance(func, ClsObj):
            cls = func.dict['cls']
            if 'call' not in cls.dict:
                raise Exception(f'Class {func.name} has no call method')
            args.insert(0, func)
            func = cls.dict['call']

        if not isinstance(func, FuncObj):
            raise Exception(f'{func} is not a function')

        if FuncObj.Flag.BOUNDED in func.flag:
            args.insert(0, func.obj)

        if FuncObj.Flag.BUILTIN in func.flag:
            return func.body(*args)

        params = eval(func.params)
        if len(args) != len(params):
            raise Exception(f'{func.name} expected {len(params)} args, \
                but got {len(args)}')

        env.new_scope(func.scope)

        [env.set_var(name, value)
            for name, value in zip(params, args)]

        result = eval(func.body)
        env.free_scope()

        return result

    def defcls(node):
        name = node.name
        attrs = {}
        for attr in node.body:
            if isinstance(attr, parser.Defunc):
                func = FuncObj(attr.name, attr.params, attr.body,
                    env.current_scope)
                attrs[attr.name] = func
            elif isinstance(attr, parser.SetVar):
                value = eval(attr.value)
                attrs[attr.name] = value
            else:
                raise Exception(f'Unknown attribute type: {attr}')
        
        cls = new_cls(metacls, name, None, attrs)
        env.set_var(name, cls)

    def setattr(node):
        obj = eval(node.obj)
        attr = node.attr
        value = eval(node.value)

        if not isinstance(obj, ClsObj):
            raise Exception(f'{obj} is not an object')
        obj.dict[attr] = value

    def getattr(node):
        obj = eval(node.obj)
        attr = node.attr  # identity

        def get_attr(cls, attr):
            if not hasattr(cls, 'dict'):
               raise Exception(f'{cls} not class')

            if attr in cls.dict:
                return cls.dict[attr]

            if 'cls' not in cls.dict:
                raise Exception(f'{cls} has no attribute {attr}')

            attr = get_attr(cls.dict['cls'], attr)
            if isinstance(attr, FuncObj):
                return BdFuncObj(attr, obj)
            return attr

        return get_attr(obj, attr)

    node_to_computer = {
        parser.Number: number,
        parser.String: string,
        parser.Null: null,
        parser.BinOp: binop,
        parser.Block: block,
        parser.IfStmt: ifstmt,
        parser.Map: map,
        parser.GetItem: getitem,
        parser.SetVar: defvar,
        parser.GetVar: getvar,
        parser.ParamList: paramlist,
        parser.Defunc: defunc,
        parser.ArgList: arglist,
        parser.Call: call,
        parser.DefCls: defcls,
        parser.SetAttr: setattr,
        parser.GetAttr: getattr,
    }
    
    def eval(node):
        return node_to_computer[type(node)](node)

    # def init_env():
    env = Enviroemnt()
    env.set_var('print', BtinFuncObj('print', print))

    def new_cls(metacls, name, bases, attrs):
        attrs['cls'] = metacls
        attrs['dict'] = attrs
        cls = ClsObj(name, bases, attrs)
        return cls

    def meta_new(cls, *args):
        obj = new_cls(cls, 'N/a', None, {}) 
        # obj.init      
        return obj
        
    attr = {'p' : BtinFuncObj('print', print),
        'author' : 'liuqi',
        'call': BtinFuncObj('new', meta_new)}
    metacls = ClsObj('metacls', None, attr)

    env.set_var('new', BtinFuncObj('new', 
        functools.partial(new_cls, metacls)))

    return eval(ast)


if __name__ == '__main__':
    print('Test interpreter')

    from lexer import my_lexer
    from parser import my_parser

    
    my_lexer = my_lexer()
    # Build the parser
    my_parser = my_parser()


    source_file = "test.py"
    data = open(source_file, 'r').read()

    ast = my_parser.parse(data)

    result = interpreter(ast)

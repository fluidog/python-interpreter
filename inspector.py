#! /bin/env python3

from pyecharts.charts import Tree

import parser

def inspector(ast):
    def binop(node, chart_tree):
        chart_tree['name'] = f'BinOp({node.op})'
        chart_tree['children'] = [ walk(n,{}) for n in [node.left, node.right] ]
        return chart_tree

    def number(node, chart_tree):
        chart_tree['name'] = str(node.value)
        return chart_tree

    def string(node, chart_tree):
        chart_tree['name'] = f'"{node.value}"'
        return chart_tree

    def null(node, chart_tree):
        chart_tree['name'] = 'Null'
        return chart_tree

    def map(node, chart_tree):
        chart_tree['name'] = 'Map'
        chart_tree['children'] = [ { 'children':[ walk(key, {}), walk(value, {})] } 
            for key, value in node.body.items() ]
        return chart_tree

    def getitem(node, chart_tree):
        chart_tree['name'] = '[]'
        chart_tree['children'] = [ walk(node.container, {}), walk(node.index, {}) ]
        return chart_tree

    def block(node, chart_tree):
        chart_tree['name'] = 'Block'
        chart_tree['children'] = [ walk(stmt, {}) for stmt in node.body ]
        return chart_tree

    def ifstmt(node, chart_tree):
        chart_tree['name'] = 'If'
        chart_tree['children'] = [ walk(node.cond, {}), walk(node.body, {}) ]
        if node.else_body:
            chart_tree['children'].append(walk(node.else_body, {}))
        return chart_tree

    def setvar(node, chart_tree):
        chart_tree['name'] = f'{node.name}(=)'
        chart_tree['children'] = [ walk(node.value, {}) ]
        return chart_tree

    def getvar(node, chart_tree):
        chart_tree['name'] = node.name
        return chart_tree

    def paramlist(node, chart_tree):
        chart_tree['name'] = 'Params'
        chart_tree['children'] = [ {'name':param} for param in node.body ]
        return chart_tree

    def defunc(node, chart_tree):
        chart_tree['name'] = f'Defunc({node.name})'
        chart_tree['children'] = [ walk(node.params, {}), walk(node.body, {}) ]
        return chart_tree

    def arglist(node,chart_tree):
        chart_tree['name'] = 'Args()'
        chart_tree['children'] = [ walk(arg, {}) for arg in node.body ]
        return chart_tree

    def call(node, chart_tree):
        chart_tree['name'] = 'Call()'
        chart_tree['children'] = [ walk(node.func, {}), walk(node.args, {}) ]
        return chart_tree

    def defcls(node, chart_tree):
        chart_tree['name'] = f'Class({node.name})'
        chart_tree['children'] = [ walk(n, {}) for n in node.body ]
        return chart_tree

    def setattr(node, chart_tree):
        chart_tree['name'] = f'(.{node.attr}=)'
        chart_tree['children'] = [ walk(node.obj, {}),  walk(node.value, {}) ]
        return chart_tree

    def getattr(node, chart_tree):
        chart_tree['name'] = 'Get(.)'
        chart_tree['children'] = [ walk(node.obj, {}), {'name':node.attr} ]
        return chart_tree

    node_to_method = {
        parser.BinOp: binop,
        parser.Number: number,
        parser.String: string,
        parser.Null: null,
        parser.Map: map,
        parser.GetItem: getitem,
        parser.Block: block,
        parser.IfStmt: ifstmt,
        parser.SetVar: setvar,
        parser.GetVar: getvar,
        parser.ParamList: paramlist,
        parser.Defunc: defunc,
        parser.ArgList: arglist,
        parser.Call: call,
        parser.DefCls: defcls,
        parser.SetAttr: setattr,
        parser.GetAttr: getattr,
     }

    def walk(node, chart_tree):
        return node_to_method[type(node)](node, chart_tree)

    data = [ walk(ast, {}) ]

    c = (
        Tree()
        .add("", data, orient='TB', initial_tree_depth=-1)
        .render("ast.html")
    )

if __name__ == '__main__':
    print('Test inspector')

    from lexer import my_lexer
    from parser import my_parser

    my_lexer = my_lexer()
    # Build the parser
    my_parser = my_parser()

    source_file = "test.py"
    data = open(source_file, 'r').read()

    ast = my_parser.parse(data)

    inspector(ast)


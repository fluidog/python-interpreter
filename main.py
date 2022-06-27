#! /bin/env python3





if __name__ == '__main__':
    from lexer import my_lexer
    from parser import my_parser
    from interpreter import interpreter

    from inspector import inspector

    lexer = my_lexer()
    parser = my_parser()

    source_file = "test.py"
    data = open(source_file, 'r').read()

    ast = parser.parse(data)

    result = interpreter(ast)

    inspector(ast)
 
    print(result)
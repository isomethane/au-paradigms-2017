#!/usr/bin/env python3

from model import *


class PriorityChecker:

    PRIORITY = {'*': 5,
                '/': 5,
                '%': 5,
                '+': 4,
                '-': 4,
                '<': 3,
                '>': 3,
                '<=': 3,
                '>=': 3,
                '==': 2,
                '!=': 2,
                '&&': 1,
                '||': 0}

    def visit_number(self, number):
        if number.value >= 0:
            return 7
        return 6

    def visit_print(self, printer):
        return -1

    def visit_read(self, reader):
        return -1

    def visit_function_call(self, func_call):
        return 7

    def visit_reference(self, reference):
        return 7

    def visit_binary_operation(self, bin_op):
        return self.PRIORITY[bin_op.op]

    def visit_unary_operation(self, un_op):
        return 6

    def visit(self, tree):
        return tree.accept(self)


class PrettyPrinter:

    def __init__(self):
        self.priority = PriorityChecker()

    def change_indent(self, delta):
        self.indent_size += delta
        self.indent = "\t" * self.indent_size

    def visit_statement(self, expr):
        return "{indent}{statement};\n".format(
            indent=self.indent,
            statement=expr.accept(self)
        )

    def wrap_up(self, string, to_wrap_up):
        if to_wrap_up:
            return "({})".format(string)
        else:
            return string

    def visit_number(self, number):
        return str(number.value)

    def visit_expression_list(self, expr_list):
        result = ""
        self.change_indent(1)
        for expr in expr_list.body:
            result += self.visit_statement(expr)
        self.change_indent(-1)
        return result

    def visit_function_definition(self, func_def):
        function = func_def.function
        return (
            "def {name}({args}) {{\n"
            "{body}"
            "{indent}}}"
        ).format(
            name=func_def.name,
            args=", ".join(function.args),
            body=function.body.accept(self),
            indent=self.indent
        )

    def visit_conditional(self, conditional):
        result = (
            "if ({condition}) {{\n"
            "{if_true}"
            "{indent}}}"
        ).format(
            condition=conditional.condition.accept(self),
            if_true=conditional.if_true.accept(self),
            indent=self.indent
        )
        if conditional.if_false.body:
            result += (
                " else {{\n"
                "{if_false}"
                "{indent}}}"
            ).format(
                if_false=conditional.if_false.accept(self),
                indent=self.indent
            )
        return result

    def visit_print(self, print):
        return "print {}".format(print.expr.accept(self))

    def visit_read(self, read):
        return "read {}".format(read.name)

    def visit_function_call(self, func_call):
        return (
            "{fun_expr}({args})"
        ).format(
            fun_expr=func_call.fun_expr.accept(self),
            args=", ".join(arg.accept(self) for arg in func_call.args)
        )

    def visit_reference(self, reference):
        return str(reference.name)

    def visit_binary_operation(self, bin_op):
        l_prior = bin_op.lhs.accept(self.priority)
        m_prior = bin_op.accept(self.priority)
        r_prior = bin_op.rhs.accept(self.priority)
        return ("{lhs} {op} {rhs}").format(
            lhs=self.wrap_up(bin_op.lhs.accept(self), l_prior < m_prior),
            op=bin_op.op,
            rhs=self.wrap_up(bin_op.rhs.accept(self), r_prior <= m_prior)
        )

    def visit_unary_operation(self, un_op):
        op_prior = un_op.accept(self.priority)
        expr_prior = un_op.expr.accept(self.priority)
        return "{op}{expr}".format(
            op=un_op.op,
            expr=self.wrap_up(un_op.expr.accept(self), expr_prior <= op_prior)
        )

    def visit(self, tree):
        self.indent_size = 0
        self.indent = ""
        print(self.visit_statement(tree), end="")


def printer_tests():
    scope = Scope()
    printer = PrettyPrinter()

    # Factorial
    condition = BinaryOperation(Reference('n'), '>', Number(1))
    recursive = FunctionCall(Reference('fact'),
                             [BinaryOperation(Reference('n'), '-', Number(1))])
    if_true = [BinaryOperation(Reference('n'), '*', recursive)]
    if_false = [Number(1)]
    conditional = Conditional(condition, if_true, if_false)
    func_def = FunctionDefinition('fact', Function(('n'), [conditional]))
    printer.visit(func_def)
    func_def.evaluate(scope)
    printer.visit(FunctionCall(Reference('fact'), [Number(10)]))

    # Multi-argument function
    div = BinaryOperation(Reference('b'), '/', Reference('a'))
    sub = BinaryOperation(div, '-', Reference('c'))

    func_def = FunctionDefinition('compute', Function(('a', 'b', 'c'), [sub]))
    printer.visit(func_def)
    func_def.evaluate(scope)
    printer.visit(FunctionCall(Reference('compute'),
                  [Number(3), Number(1000), Number(30)]))

    # Empty conditionals
    printer.visit(Conditional(UnaryOperation('!', Number(0)), None))
    printer.visit(Conditional(UnaryOperation('!', Number(1)), None))

    # Linear equation solver
    condition = BinaryOperation(Reference('a'), '!=', Number(0))
    solution = UnaryOperation('-', div)
    conditional = Conditional(condition, [Print(solution)])
    func_def = FunctionDefinition('linear_solve', Function((),
                                  [Read('a'), Read('b'), conditional]))
    printer.visit(func_def)
    func_def.evaluate(scope)
    printer.visit(FunctionCall(Reference('linear_solve'), []))

    printer.visit(Print(Number(30)))

    # Priority test
    printer.visit(BinaryOperation(Number(1), '+',
                  BinaryOperation(Number(2), '*', Reference('x'))))
    printer.visit(BinaryOperation(BinaryOperation(Number(1), '+', Number(2)),
                                  '*', Reference('x')))
    printer.visit(BinaryOperation(Number(1), '-',
                  BinaryOperation(Number(2), '-', Reference('x'))))
    printer.visit(BinaryOperation(BinaryOperation(Number(1), '-', Number(2)),
                                  '-', Reference('x')))
    printer.visit(UnaryOperation('!', Number(1)))
    printer.visit(UnaryOperation('!', Number(-1)))
    printer.visit(UnaryOperation('!', UnaryOperation('-', Number(-1))))

    first = BinaryOperation(Reference('a'), '>', Reference('b'))
    second = BinaryOperation(Reference('b'), '/',
                             BinaryOperation(Reference('a'), '==', Number(3)))
    third = BinaryOperation(second, '==', Reference('c'))
    forth = BinaryOperation(first, '||', third)
    fifth = BinaryOperation(Reference('b'), '%', Read('d'))
    sixth = BinaryOperation(fifth, '!=',
                            FunctionCall(Reference('fact'), [Number(10)]))
    expr = BinaryOperation(forth, '&&', sixth)
    print("It should print:", end=' ')
    print("(a > b || b / (a == 3) == c) && b % (read d) != fact(10);")
    printer.visit(expr)


if __name__ == '__main__':
    printer_tests()

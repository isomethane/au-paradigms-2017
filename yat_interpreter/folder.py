#!/usr/bin/env python3

from model import *
from printer import *


class ConstantFolder:

    def visit_number(self, number):
        return number

    def visit_expression_list(self, expr_list):
        return [expr.accept(self) for expr in expr_list.body]

    def visit_function_definition(self, func_def):
        function = func_def.function
        return FunctionDefinition(
            func_def.name, Function(function.args, function.body.accept(self))
        )

    def visit_conditional(self, conditional):
        return Conditional(
            conditional.condition.accept(self),
            conditional.if_true.accept(self),
            conditional.if_false.accept(self)
        )

    def visit_print(self, print):
        return Print(print.expr.accept(self))

    def visit_read(self, read):
        return read

    def visit_function_call(self, func_call):
        return FunctionCall(
            func_call.fun_expr.accept(self),
            [arg.accept(self) for arg in func_call.args]
        )

    def visit_reference(self, reference):
        return reference

    def visit_binary_operation(self, bin_op):
        lhs = bin_op.lhs.accept(self)
        op = bin_op.op
        rhs = bin_op.rhs.accept(self)

        if isinstance(lhs, Number) and isinstance(rhs, Number):
            return BinaryOperation(lhs, op, rhs).evaluate(Scope())
        if (isinstance(lhs, Number) and lhs == Number(0) and
           isinstance(rhs, Reference) and op == '*'):
            return Number(0)
        if (isinstance(rhs, Number) and rhs == Number(0) and
           isinstance(lhs, Reference) and op == '*'):
            return Number(0)
        if (isinstance(lhs, Reference) and isinstance(rhs, Reference) and
           lhs.name == rhs.name and op == '-'):
            return Number(0)
        return BinaryOperation(lhs, op, rhs)

    def visit_unary_operation(self, un_op):
        op = un_op.op
        expr = un_op.expr.accept(self)
        if isinstance(expr, Number):
            return UnaryOperation(op, expr).evaluate(Scope())
        return UnaryOperation(op, expr)

    def visit(self, tree):
        return tree.accept(self)


def folder_tests():
    scope = Scope()
    printer = PrettyPrinter()
    folder = ConstantFolder()

    # Complex example
    mul = BinaryOperation(Number(30), '*', UnaryOperation('-', Number(59)))
    sub = BinaryOperation(Reference("some_name"), '-', Reference('some_name'))
    another_sub = BinaryOperation(Reference("some_name"), '-',
                                  Reference('another_name'))
    null = BinaryOperation(Reference("another_name"), '*', Number(0))
    something = BinaryOperation(Reference("another_name"), '+', Number(0))
    unsub = UnaryOperation('-', Number(-100))
    long_expr = UnaryOperation('-', BinaryOperation(sub, '==', null))
    condition = sub
    if_true = [something, null, long_expr, Read('x')]
    if_false = [another_sub, unsub, mul, Print(Reference('y'))]
    conditional = Conditional(condition, if_true, if_false)
    func_def = FunctionDefinition('trash', Function(('n'), [conditional]))
    func_def.evaluate(scope)
    func_call = FunctionCall(Reference('trash'),
                             [UnaryOperation('!', Number(0))])
    printer.visit(func_def)
    printer.visit(func_call)

    printer.visit(folder.visit(func_def))
    printer.visit(folder.visit(func_call))


if __name__ == '__main__':
    folder_tests()

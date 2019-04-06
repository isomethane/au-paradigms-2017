#!/usr/bin/env python3


class Scope:

    def __init__(self, parent=None):
        self.dictionary = {}
        self.parent = parent

    def __setitem__(self, key, value):
        self.dictionary[key] = value

    def __getitem__(self, key):
        if key in self.dictionary:
            return self.dictionary[key]
        elif self.parent:
            return self.parent[key]
        else:
            raise KeyError(key)


class Number:

    def __init__(self, value):
        assert isinstance(value, int)
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def evaluate(self, scope):
        return self

    def accept(self, visitor):
        return visitor.visit_number(self)


class Function:

    def __init__(self, args, body):
        self.args = args
        self.body = ExpressionList(body)

    def evaluate(self, scope):
        return self


class ExpressionList:

    def __init__(self, body):
        self.body = body or []

    def evaluate(self, scope):
        result = None
        for expr in self.body:
            result = expr.evaluate(scope)
        return result

    def accept(self, visitor):
        return visitor.visit_expression_list(self)


class FunctionDefinition:

    def __init__(self, name, function):
        self.name = name
        self.function = function

    def evaluate(self, scope):
        scope[self.name] = self.function
        return self.function

    def accept(self, visitor):
        return visitor.visit_function_definition(self)


class Conditional:

    def __init__(self, condition, if_true, if_false=None):
        self.condition = condition
        self.if_true = ExpressionList(if_true)
        self.if_false = ExpressionList(if_false)

    def evaluate(self, scope):
        if self.condition.evaluate(scope) != Number(0):
            return self.if_true.evaluate(scope)
        else:
            return self.if_false.evaluate(scope)

    def accept(self, visitor):
        return visitor.visit_conditional(self)


class Print:

    def __init__(self, expr):
        self.expr = expr

    def evaluate(self, scope):
        result = self.expr.evaluate(scope)
        print(result.value)
        return result

    def accept(self, visitor):
        return visitor.visit_print(self)


class Read:
    def __init__(self, name):
        self.name = name

    def evaluate(self, scope):
        scope[self.name] = Number(int(input()))
        return scope[self.name]

    def accept(self, visitor):
        return visitor.visit_read(self)


class FunctionCall:

    def __init__(self, fun_expr, args):
        self.fun_expr = fun_expr
        self.args = args

    def evaluate(self, scope):
        function = self.fun_expr.evaluate(scope)
        call_scope = Scope(scope)
        for name, value in zip(function.args, self.args):
            call_scope[name] = value.evaluate(scope)
        return function.body.evaluate(call_scope)

    def accept(self, visitor):
        return visitor.visit_function_call(self)


class Reference:

    def __init__(self, name):
        self.name = name

    def evaluate(self, scope):
        return scope[self.name]

    def accept(self, visitor):
        return visitor.visit_reference(self)


class BinaryOperation:
    OPERATORS = {'+': lambda x, y: x + y,
                 '-': lambda x, y: x - y,
                 '*': lambda x, y: x * y,
                 '/': lambda x, y: x // y,
                 '%': lambda x, y: x % y,
                 '==': lambda x, y: x == y,
                 '!=': lambda x, y: x != y,
                 '<': lambda x, y: x < y,
                 '>': lambda x, y: x > y,
                 '<=': lambda x, y: x <= y,
                 '>=': lambda x, y: x >= y,
                 '&&': lambda x, y: x and y,
                 '||': lambda x, y: x or y}

    def __init__(self, lhs, op, rhs):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs

    def evaluate(self, scope):
        result = self.OPERATORS[self.op](self.lhs.evaluate(scope).value,
                                         self.rhs.evaluate(scope).value)
        return Number(int(result))

    def accept(self, visitor):
        return visitor.visit_binary_operation(self)


class UnaryOperation:

    OPERATORS = {'-': lambda x: -x,
                 '!': lambda x: not x}

    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def evaluate(self, scope):
        result = self.OPERATORS[self.op](self.expr.evaluate(scope).value)
        return Number(int(result))

    def accept(self, visitor):
        return visitor.visit_unary_operation(self)


def example():
    parent = Scope()
    parent["foo"] = Function(('hello', 'world'),
                             [Print(BinaryOperation(Reference('hello'),
                                                    '+',
                                                    Reference('world')))])
    parent["bar"] = Number(10)
    scope = Scope(parent)
    assert 10 == scope["bar"].value
    scope["bar"] = Number(20)
    assert scope["bar"].value == 20
    print('It should print 2: ', end=' ')
    FunctionCall(FunctionDefinition('foo', parent['foo']),
                 [Number(5), UnaryOperation('-', Number(3))]).evaluate(scope)


def my_tests():
    scope = Scope()

    # Factorial
    condition = BinaryOperation(Reference('n'), '>', Number(1))
    recursive = FunctionCall(Reference('fact'),
                             [BinaryOperation(Reference('n'), '-', Number(1))])
    if_true = [BinaryOperation(Reference('n'), '*', recursive)]
    if_false = [Number(1)]
    conditional = Conditional(condition, if_true, if_false)
    FunctionDefinition('fact', Function(('n'), [conditional])).evaluate(scope)
    print('\n10! =', end=' ')
    Print(FunctionCall(Reference('fact'), [Number(10)])).evaluate(scope)
    print()

    # Quick test
    print('Quick test: (1 for True, 0 for False)')
    print('3 == 4 <=>', end=' ')
    Print(BinaryOperation(Number(3), '==', Number(4))).evaluate(scope)
    print('3 != 4 <=>', end=' ')
    Print(BinaryOperation(Number(3), '!=', Number(4))).evaluate(scope)
    print('!(7 < 7) <=>', end=' ')
    Print(UnaryOperation('!',
          BinaryOperation(Number(7), '<', Number(7)))).evaluate(scope)
    print('7 <= 7 <=>', end=' ')
    Print(BinaryOperation(Number(7), '<=', Number(7))).evaluate(scope)
    tmp = BinaryOperation(BinaryOperation(Number(30), '+', Number(59)),
                          '%', Number(5))
    print('(30 + 59) % 5 == 4 <=>', end=' ')
    Print(BinaryOperation(tmp, '==', Number(4))).evaluate(scope)

    # Multi-argument function
    print('\nf(a, b, c) = b / a - c')
    print('f(3, 1000, 30) =', end=' ')
    div = BinaryOperation(Reference('b'), '/', Reference('a'))
    sub = BinaryOperation(div, '-', Reference('c'))
    Print(FunctionCall(FunctionDefinition('compute', Function(('a', 'b', 'c'),
          [sub])), [Number(3), Number(1000), Number(30)])).evaluate(scope)

    # Empty conditionals
    Conditional(UnaryOperation('!', Number(0)), None).evaluate(scope)
    Conditional(UnaryOperation('!', Number(1)), None).evaluate(scope)

    # Linear equation solver
    print('\nSolve ax + b = 0 in integers')
    print('Input a, b')
    condition = BinaryOperation(Reference('a'), '!=', Number(0))
    solution = UnaryOperation('-', div)
    conditional = Conditional(condition, [Print(solution)])
    FunctionDefinition('linear_solve', Function((),
                       [Read('a'), Read('b'), conditional])).evaluate(scope)
    FunctionCall(Reference('linear_solve'), []).evaluate(scope)


if __name__ == '__main__':
    example()
    my_tests()

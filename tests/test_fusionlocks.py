import unittest

from fusionlocks import FssError, Interpreter, Parser, tokenize


def run_source(source):
    output = []
    statements = Parser(tokenize(source)).parse()
    Interpreter(output=output.append).run(statements)
    return output


class FusionLocksTests(unittest.TestCase):
    def test_variables_math_and_precedence(self):
        self.assertEqual(run_source("let answer = 2 + 3 * 4\nprint answer"), [14])

    def test_strings_and_escapes(self):
        self.assertEqual(run_source('print "a\\nb"'), ["a\nb"])

    def test_if_else_and_boolean_operators(self):
        source = """if true and not false {
    print "yes"
} else {
    print "no"
}"""
        self.assertEqual(run_source(source), ["yes"])

    def test_statement_after_if_without_else(self):
        source = '''if false {
    print "no"
}
print "after"'''
        self.assertEqual(run_source(source), ["after"])

    def test_while_and_assignment(self):
        source = """let n = 0
while n < 3 {
    set n = n + 1
}
print n"""
        self.assertEqual(run_source(source), [3])

    def test_undefined_variable_is_an_error(self):
        with self.assertRaisesRegex(FssError, "not declared"):
            run_source("print missing")

    def test_division_by_zero_is_an_error(self):
        with self.assertRaisesRegex(FssError, "division by zero"):
            run_source("print 1 / 0")

    def test_loop_safety_limit(self):
        statements = Parser(tokenize("while true {\n}")).parse()
        with self.assertRaisesRegex(FssError, "safety limit"):
            Interpreter(max_steps=5).run(statements)

    def test_statement_after_if_else(self):
        source = '''if true {
    print "inside"
} else {
    print "other"
}
print "after"'''
        self.assertEqual(run_source(source), ["inside", "after"])

    def test_missing_statement_separator_is_an_error(self):
        with self.assertRaisesRegex(FssError, "new line or ';'"):
            Parser(tokenize("let a = 1 let b = 2")).parse()

    def test_unmatched_closing_brace_is_an_error(self):
        with self.assertRaisesRegex(FssError, "expected let"):
            Parser(tokenize("}")).parse()


if __name__ == "__main__":
    unittest.main()

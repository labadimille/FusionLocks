#!/usr/bin/env python3
"""Interpreter for the FusionLocks (.fss) language."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

VERSION = "0.1.0"
MAX_STEPS = 100_000


class FssError(Exception):
    """A user-facing FusionLocks source or runtime error."""


@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    line: int
    column: int


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    line = 1
    column = 1
    while i < len(source):
        char = source[i]
        if char in " \t":
            i += 1
            column += 1
        elif char == "\r":
            i += 1
        elif char == "\n":
            tokens.append(Token("NEWLINE", "\n", line, column))
            i += 1
            line += 1
            column = 1
        elif char == "#":
            while i < len(source) and source[i] != "\n":
                i += 1
                column += 1
        elif char in "\"'":
            quote = char
            start_line, start_column = line, column
            i += 1
            column += 1
            value: list[str] = []
            while i < len(source) and source[i] != quote:
                char = source[i]
                if char == "\n":
                    raise FssError(f"{start_line}:{start_column}: string not closed")
                if char == "\\":
                    i += 1
                    column += 1
                    if i >= len(source):
                        raise FssError(f"{start_line}:{start_column}: incomplete escape")
                    escaped = source[i]
                    escapes = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\",
                               "\"": "\"", "'": "'"}
                    if escaped not in escapes:
                        raise FssError(f"{line}:{column}: unknown escape '\\{escaped}'")
                    value.append(escapes[escaped])
                else:
                    value.append(char)
                i += 1
                column += 1
            if i >= len(source):
                raise FssError(f"{start_line}:{start_column}: string not closed")
            i += 1
            column += 1
            tokens.append(Token("STRING", "".join(value), start_line, start_column))
        elif char.isdigit():
            start = i
            start_column = column
            while i < len(source) and source[i].isdigit():
                i += 1
                column += 1
            if i < len(source) and source[i] == "." and i + 1 < len(source) and source[i + 1].isdigit():
                i += 1
                column += 1
                while i < len(source) and source[i].isdigit():
                    i += 1
                    column += 1
            text = source[start:i]
            number: int | float = float(text) if "." in text else int(text)
            tokens.append(Token("NUMBER", number, line, start_column))
        elif char.isalpha() or char == "_":
            start = i
            start_column = column
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                i += 1
                column += 1
            tokens.append(Token("IDENT", source[start:i], line, start_column))
        elif source[i:i + 2] in ("==", "!=", "<=", ">="):
            tokens.append(Token("SYMBOL", source[i:i + 2], line, column))
            i += 2
            column += 2
        elif char in "+-*/%<>=(){};":
            tokens.append(Token("SYMBOL", char, line, column))
            i += 1
            column += 1
        else:
            raise FssError(f"{line}:{column}: unexpected character {char!r}")
    tokens.append(Token("EOF", None, line, column))
    return tokens


class Parser:
    PRECEDENCE = {
        "or": 1, "and": 2,
        "==": 3, "!=": 3,
        "<": 4, "<=": 4, ">": 4, ">=": 4,
        "+": 5, "-": 5,
        "*": 6, "/": 6, "%": 6,
    }

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.position]

    def advance(self) -> Token:
        token = self.current
        self.position += 1
        return token

    def error(self, message: str) -> FssError:
        return FssError(f"{self.current.line}:{self.current.column}: {message}")

    def accept(self, value: str) -> bool:
        if self.current.value == value:
            self.advance()
            return True
        return False

    def expect(self, value: str) -> None:
        if not self.accept(value):
            raise self.error(f"expected {value!r}")

    def separators(self) -> None:
        while self.current.kind == "NEWLINE" or self.current.value == ";":
            self.advance()

    def parse(self) -> list[tuple]:
        return self.parse_statements("EOF")

    def parse_statements(self, end: str) -> list[tuple]:
        statements = []
        self.separators()
        while self.current.kind != end:
            if end == "}" and self.current.value == "}":
                break
            statements.append(self.statement())
            if self.current.kind not in ("NEWLINE", "EOF") and self.current.value not in (";", "}"):
                raise self.error("expected a new line or ';' between statements")
            self.separators()
        return statements

    def statement(self) -> tuple:
        token = self.current
        if token.kind == "IDENT" and token.value in ("let", "set"):
            operation = str(self.advance().value)
            name = self.current
            if name.kind != "IDENT":
                raise self.error("expected a variable name")
            self.advance()
            self.expect("=")
            return (operation, str(name.value), self.expression())
        if token.kind == "IDENT" and token.value == "print":
            self.advance()
            return ("print", self.expression())
        if token.kind == "IDENT" and token.value == "if":
            self.advance()
            condition = self.expression()
            body = self.block()
            after_body = self.position
            self.separators()
            alternative = []
            if self.current.kind == "IDENT" and self.current.value == "else":
                self.advance()
                alternative = self.block()
            else:
                self.position = after_body
            return ("if", condition, body, alternative)
        if token.kind == "IDENT" and token.value == "while":
            self.advance()
            condition = self.expression()
            return ("while", condition, self.block())
        raise self.error("expected let, set, print, if, or while")

    def block(self) -> list[tuple]:
        self.expect("{")
        statements = self.parse_statements("}")
        self.expect("}")
        return statements

    def expression(self, minimum: int = 1) -> tuple:
        left = self.prefix()
        while self.current.kind == "IDENT" and self.current.value in ("and", "or") or (
            self.current.kind == "SYMBOL" and self.current.value in self.PRECEDENCE
        ):
            operator = str(self.current.value)
            precedence = self.PRECEDENCE[operator]
            if precedence < minimum:
                break
            self.advance()
            right = self.expression(precedence + 1)
            left = ("binary", operator, left, right)
        return left

    def prefix(self) -> tuple:
        token = self.advance()
        if token.kind in ("NUMBER", "STRING"):
            return ("literal", token.value)
        if token.kind == "IDENT":
            if token.value in ("true", "false"):
                return ("literal", token.value == "true")
            if token.value == "not":
                return ("unary", "not", self.expression(7))
            return ("variable", str(token.value))
        if token.value == "-":
            return ("unary", "-", self.expression(7))
        if token.value == "(":
            value = self.expression()
            self.expect(")")
            return value
        raise FssError(f"{token.line}:{token.column}: expected an expression")


class Interpreter:
    def __init__(self, output: Callable[[object], None] = print, max_steps: int = MAX_STEPS):
        self.variables: dict[str, object] = {}
        self.output = output
        self.max_steps = max_steps
        self.steps = 0

    def run(self, statements: list[tuple]) -> None:
        for statement in statements:
            self.execute(statement)

    def tick(self) -> None:
        self.steps += 1
        if self.steps > self.max_steps:
            raise FssError(f"execution stopped after {self.max_steps} statements (safety limit)")

    def execute(self, statement: tuple) -> None:
        self.tick()
        kind = statement[0]
        if kind in ("let", "set"):
            _, name, expression = statement
            if kind == "let" and name in self.variables:
                raise FssError(f"variable {name!r} is already declared; use 'set' to change it")
            if kind == "set" and name not in self.variables:
                raise FssError(f"variable {name!r} is not declared; use 'let' first")
            self.variables[name] = self.evaluate(expression)
        elif kind == "print":
            self.output(self.evaluate(statement[1]))
        elif kind == "if":
            _, condition, body, alternative = statement
            self.run(body if self.boolean(self.evaluate(condition)) else alternative)
        elif kind == "while":
            _, condition, body = statement
            while self.boolean(self.evaluate(condition)):
                self.tick()
                self.run(body)

    @staticmethod
    def boolean(value: object) -> bool:
        if type(value) is not bool:
            raise FssError("condition must be true or false")
        return value

    def evaluate(self, expression: tuple) -> object:
        kind = expression[0]
        if kind == "literal":
            return expression[1]
        if kind == "variable":
            name = expression[1]
            if name not in self.variables:
                raise FssError(f"variable {name!r} is not declared")
            return self.variables[name]
        if kind == "unary":
            _, operator, operand = expression
            value = self.evaluate(operand)
            if operator == "not":
                return not self.boolean(value)
            if type(value) not in (int, float):
                raise FssError("unary '-' requires a number")
            return -value
        _, operator, left_expression, right_expression = expression
        left = self.evaluate(left_expression)
        if operator == "and":
            return self.boolean(left) and self.boolean(self.evaluate(right_expression))
        if operator == "or":
            return self.boolean(left) or self.boolean(self.evaluate(right_expression))
        right = self.evaluate(right_expression)
        if operator == "+" and type(left) is str and type(right) is str:
            return left + right
        if operator in ("==", "!="):
            return left == right if operator == "==" else left != right
        if operator in ("<", "<=", ">", ">="):
            if type(left) not in (int, float, str) or type(right) is not type(left):
                raise FssError(f"operator {operator!r} needs two numbers or two strings")
            return {"<": left < right, "<=": left <= right,
                    ">": left > right, ">=": left >= right}[operator]
        if type(left) not in (int, float) or type(right) not in (int, float):
            raise FssError(f"operator {operator!r} requires numbers")
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            if right == 0:
                raise FssError("division by zero")
            return left / right
        if operator == "%":
            if right == 0:
                raise FssError("remainder by zero")
            return left % right
        raise FssError(f"unsupported operator {operator!r}")


def main(argv: list[str] | None = None) -> int:
    cli = argparse.ArgumentParser(
        prog="fusionlocks",
        description="Run FusionLocks (.fss) programs.",
    )
    cli.add_argument("file", nargs="?", help="path to a .fss source file")
    cli.add_argument("--check", action="store_true", help="check syntax without running the program")
    cli.add_argument("--version", action="version", version=f"FusionLocks {VERSION}")
    args = cli.parse_args(argv)
    if not args.file:
        cli.error("provide a .fss file (see --help)")
    path = Path(args.file)
    if path.suffix.lower() != ".fss":
        cli.error("source files must use the .fss extension")
    try:
        source = path.read_text(encoding="utf-8-sig")
        statements = Parser(tokenize(source)).parse()
        if args.check:
            print(f"OK: {path} (syntax valid)")
        else:
            Interpreter().run(statements)
    except (OSError, UnicodeError) as error:
        print(f"fusionlocks: {error}", file=sys.stderr)
        return 1
    except FssError as error:
        print(f"{path}: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

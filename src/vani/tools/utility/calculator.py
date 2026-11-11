"""Safe math evaluation (no eval)."""

import ast
import math
import operator
import re

from vani.tools.core import error, tool

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
        ast.FloorDiv: operator.floordiv, ast.USub: operator.neg, ast.UAdd: operator.pos}
_FUNCS = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
          "log": math.log10, "ln": math.log, "abs": abs, "round": round}
_CONSTS = {"pi": math.pi, "e": math.e}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("exponent too large")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Name) and node.id in _CONSTS:
        return _CONSTS[node.id]
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in _FUNCS):
        return _FUNCS[node.func.id](*[_eval(a) for a in node.args])
    raise ValueError("unsupported expression")


@tool
def calculate(expression: str) -> str:
    """Do math. Supports + - * / ** % //, parentheses, sqrt, sin, cos, tan, log, pi. Example: '(12 + 8) * 3 / 4'."""
    expr = expression.strip().replace("^", "**")
    if re.fullmatch(r"[\d\s.+\-*/x()%]+", expr):
        expr = expr.replace("x", "*")
    try:
        result = _eval(ast.parse(expr, mode="eval").body)
    except ZeroDivisionError:
        return error("cannot divide by zero.")
    except Exception as e:
        return error(f"could not calculate that ({e}).")
    if isinstance(result, float):
        result = round(result, 8)
        if result == int(result):
            result = int(result)
    return f"{expression.strip()} = {result}"

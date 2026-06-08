#    pyeq3 is a collection of equations expressed as Python classes
#
#    Copyright (C) 2013 James R. Phillips
#    2548 Vera Cruz Drive
#    Birmingham, AL 35235 USA
#
#    https://github.com/equations-project/pyeq3
#
#    License: BSD-style (see LICENSE.txt in main source directory)

"""AST allow-list sandbox for User-Defined-Function expression text.

The UDF fit path eval()s user-submitted expressions. pyeq3's cosmetic gate
(ProcessAndValidateFunctionString) does not reject dangerous names, so without
this check an untrusted 2D UDF can reach remote code execution in the fitting
process (for example __import__('os').system('id')*X). This module re-parses
the expression and walks it against a strict allow-list, rejecting everything
outside pure arithmetic over X/Y, coefficient names, and the numpy tokens
pyeq3 injects into safe_dict.

Rejecting every ast.Attribute and ast.Subscript node is the security core: a
builtins-free eval namespace is still escapable through attribute traversal
(().__class__.__bases__[0].__subclasses__()); removing "." and "[]" at the
grammar level closes that whole family. Names starting with an underscore are
rejected as belt-and-suspenders against dunders.
"""

import ast


class UnsafeUDFError(Exception):
    """A UDF expression contained a construct outside safe arithmetic."""


# Expression-level nodes that pure arithmetic over named values may use.
_allowedNodes = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Constant,
    ast.Load,
    # binary operators
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,
    ast.Pow,
    ast.FloorDiv,
    # unary operators
    ast.UAdd,
    ast.USub,
)


def ValidateUDFExpression(inExpressionText, inAllowedNames):
    """Raise UnsafeUDFError unless inExpressionText is safe arithmetic over
    inAllowedNames (a set of permitted bare identifiers: X/Y, coefficient
    designators, and the numpy tokens pyeq3 injects into safe_dict)."""
    try:
        tree = ast.parse(inExpressionText, mode="eval")
    except SyntaxError as exc:
        raise UnsafeUDFError(f"could not parse expression ({exc})") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            raise UnsafeUDFError("attribute access is not allowed")
        if isinstance(node, ast.Subscript):
            raise UnsafeUDFError("subscripting is not allowed")
        if not isinstance(node, _allowedNodes):
            raise UnsafeUDFError(f"{type(node).__name__} is not allowed")

        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)) or isinstance(node.value, bool):
                raise UnsafeUDFError("only real numeric constants are allowed")

        if isinstance(node, ast.Name):
            if node.id.startswith("_"):
                raise UnsafeUDFError(f"name {node.id!r} is not allowed")
            if node.id not in inAllowedNames:
                raise UnsafeUDFError(f"unknown name {node.id!r}")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise UnsafeUDFError("only calls to named functions are allowed")
            if node.keywords:
                raise UnsafeUDFError("keyword arguments are not allowed")
            if any(isinstance(arg, ast.Starred) for arg in node.args):
                raise UnsafeUDFError("starred arguments are not allowed")


def CollectAllowedNames(inEquation, dim):
    """Build the permitted-name set for a UDF equation: X (plus Y for 3D), the
    parsed coefficient designators, and every numpy token pyeq3 lists in
    functionDictionary / constantsDictionary. Sourced from the same
    dictionaries pyeq3 injects into safe_dict, so the allow-list cannot drift
    from what eval actually has access to."""
    names = {"X"}
    if dim == 3:
        names.add("Y")
    names.update(inEquation._coefficientDesignators)
    for tokens in inEquation.functionDictionary.values():
        names.update(tokens)
    for tokens in inEquation.constantsDictionary.values():
        names.update(tokens)
    return names

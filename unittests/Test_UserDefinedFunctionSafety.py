from . import DataForUnitTests
import pyeq3
import sys
import os
import unittest

# the pyeq3 directory is located up one level from here
if os.path.join(sys.path[0][: sys.path[0].rfind(os.sep)], "..") not in sys.path:
    sys.path.append(os.path.join(sys.path[0][: sys.path[0].rfind(os.sep)], ".."))

import numpy

numpy.seterr(all="ignore")


# X, Y, a few coefficients, and the numpy tokens a real UDF may use.
ALLOWED = {
    "X",
    "Y",
    "a",
    "b",
    "c",
    "exp",
    "sin",
    "sqrt",
    "fabs",
    "arctan2",
    "pi",
    "e",
}

# Each must be REJECTED by the validator directly.
MALICIOUS = [
    "__import__('os').system('id')*X",  # builtins via dunder name
    "().__class__.__bases__[0].__subclasses__()",  # attribute-traversal escape
    "().__class__.__bases__[0]",  # subscript escape
    "X.__class__",  # attribute access
    "(1).__class__",  # attribute on a literal
    "eval('1')+X",  # eval call
    "exec('x')+X",  # exec call
    "open('f') and X",  # file access + BoolOp
    "globals() and X",  # builtins call
    "'os' and X",  # string constant payload
    "exp(x=1)+X",  # keyword-arg call
    "foo*X",  # unknown bare name
    "[X for a in X]",  # comprehension
    "(lambda: X)()",  # lambda
    "(a := X)",  # walrus / NamedExpr
    "f'{X}'",  # f-string (JoinedStr)
    "t'{X}'",  # t-string (py3.14); SyntaxError on older -> still rejected
    "sin(X for a in X)",  # generator expression
    "X if a else b",  # ternary IfExp
    "a < X < b",  # chained compare
    "exp(**a)",  # dict-unpack into call
    "sin(open('x'))",  # dangerous inner call
    "sin(X).real",  # attribute on a call result
    "a*X + 1j",  # complex literal (only real numerics allowed)
]

# Each must be ACCEPTED by the validator directly.
BENIGN = [
    "a + b*X",
    "a*exp(-b*X)+c",
    "sin(X)+sqrt(fabs(X))",
    "a*X**2 + b*X + c",
    "a*X + b*Y",
    "a*X + pi",
    "arctan2(X, a)",
]


class TestUserDefinedFunctionSafety(unittest.TestCase):
    def test_malicious_rejected_directly(self):
        for expr in MALICIOUS:
            with self.subTest(expr=expr):
                with self.assertRaises(pyeq3.UdfSafety.UnsafeUDFError):
                    pyeq3.UdfSafety.ValidateUDFExpression(expr, ALLOWED)

    def test_benign_accepted_directly(self):
        for expr in BENIGN:
            with self.subTest(expr=expr):
                # must not raise
                pyeq3.UdfSafety.ValidateUDFExpression(expr, ALLOWED)

    def test_syntax_error_is_unsafe_not_crash(self):
        with self.assertRaises(pyeq3.UdfSafety.UnsafeUDFError):
            pyeq3.UdfSafety.ValidateUDFExpression("a + *X", ALLOWED)

    def test_collect_allowed_names_2D_excludes_Y(self):
        model = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction(
            "SSQABS", "Default"
        )
        model.ParseAndCompileUserFunctionString("a + b*X", 2)
        names = pyeq3.UdfSafety.CollectAllowedNames(model, 2)
        self.assertIn("X", names)
        self.assertNotIn("Y", names)
        self.assertTrue({"a", "b"} <= names)
        self.assertTrue({"exp", "sin", "sqrt", "pi", "e"} <= names)

    def test_collect_allowed_names_3D_includes_Y(self):
        model = pyeq3.Models_3D.UserDefinedFunction.UserDefinedFunction(
            "SSQABS", "Default"
        )
        model.ParseAndCompileUserFunctionString("a*X + b*Y", 3)
        names = pyeq3.UdfSafety.CollectAllowedNames(model, 3)
        self.assertTrue({"X", "Y", "a", "b"} <= names)


if __name__ == "__main__":
    unittest.main()

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

# Validator-reaching malicious payloads: each contains X (and Y for 3D) and
# avoids the substrings ProcessAndValidateFunctionString rejects cosmetically
# (=, ^, ln, abs, EXP, LOG), so the AST validator (not a cosmetic check) is
# what rejects them end-to-end through ParseAndCompileUserFunctionString.
GATE_MALICIOUS_2D = [
    "__import__('os').system('id')*X",
    "X.__class__",
    "eval('1')+X",
    "globals() and X",
    "'os' and X",
    "sin(X).real",
    "a*X + 1j",
]

GATE_MALICIOUS_3D = [
    "__import__('os').system('id')*X + Y",
    "X.__class__ + Y",
    "sin(X).real + Y",
]

# Benign payloads that compile cleanly through the full path. Digit-bearing
# function tokens (log10, arctan2, ...) are excluded: ConvertStringIntsToString-
# Floats mangles them (log10 -> log10.0), a separate pre-existing bug.
# Note: fabs() is intentionally absent here. pyeq3's cosmetic gate rejects any
# string containing the substring "abs" (a pre-existing over-broad check that
# also catches fabs), so fabs cannot pass the full path. The direct BENIGN list
# above still covers fabs against the validator itself.
GATE_BENIGN_2D = [
    "a + b*X",
    "a*exp(-b*X)+c",
    "a*sin(X) + b*sqrt(X)",
    "a*X**2 + b*X + c",
    "a*X + pi",
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

    def test_gate_rejects_malicious_2D(self):
        for expr in GATE_MALICIOUS_2D:
            with self.subTest(expr=expr):
                model = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction(
                    "SSQABS", "Default"
                )
                with self.assertRaises(pyeq3.UdfSafety.UnsafeUDFError):
                    model.ParseAndCompileUserFunctionString(expr, 2)

    def test_gate_rejects_malicious_3D(self):
        for expr in GATE_MALICIOUS_3D:
            with self.subTest(expr=expr):
                model = pyeq3.Models_3D.UserDefinedFunction.UserDefinedFunction(
                    "SSQABS", "Default"
                )
                with self.assertRaises(pyeq3.UdfSafety.UnsafeUDFError):
                    model.ParseAndCompileUserFunctionString(expr, 3)

    def test_gate_accepts_benign_2D(self):
        for expr in GATE_BENIGN_2D:
            with self.subTest(expr=expr):
                model = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction(
                    "SSQABS", "Default"
                )
                model.ParseAndCompileUserFunctionString(expr, 2)
                self.assertIsNotNone(model.userFunctionCodeObject)

    def test_gate_accepts_benign_3D(self):
        model = pyeq3.Models_3D.UserDefinedFunction.UserDefinedFunction(
            "SSQABS", "Default"
        )
        model.ParseAndCompileUserFunctionString("a*X + b*Y", 3)
        self.assertIsNotNone(model.userFunctionCodeObject)

    def test_2D_eval_namespace_has_no_builtins(self):
        # Defense-in-depth: even if a malicious code object bypassed the gate,
        # the 2D eval namespace must not expose builtins. abs(X) is compiled
        # directly here (the gate rejects "abs" cosmetically, so this bypasses
        # it). abs is a Python builtin and is NOT a numpy token in safe_dict,
        # so it resolves only if builtins are live. With the hardened namespace
        # it raises NameError, which CalculateModelPredictions sanitises to
        # 1e300; with live globals() it would return finite values.
        model = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction(
            "SSQABS", "Default"
        )
        model.ParseAndCompileUserFunctionString("a + b*X", 2)
        model.userFunctionCodeObject = compile("abs(X)", "<string>", "eval")
        result = model.CalculateModelPredictions(
            [1.0, 1.0], {"X": numpy.array([1.0, -2.0, 3.0])}
        )
        self.assertTrue(numpy.allclose(result, numpy.ones(3) * 1.0e300))

    def test_benign_2D_still_solves(self):
        # Positive control: the gate and hardened namespace do not break a
        # legitimate fit. Expected coefficients match the existing
        # Test_ModelSolveMethods.test_UserDefinedFunctionSolve_SSQABS_2D.
        resultShouldBe = numpy.array([-7.88180304, 1.51245438])
        model = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction(
            "SSQABS", "Default", "m*X + b"
        )
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D_small, model, False
        )
        result = model.Solve()
        self.assertTrue(
            numpy.allclose(result, resultShouldBe, rtol=1.0e-06, atol=1.0e-300)
        )

    def test_fabs_not_abs(self):
        # Check that the cosmetic gate rejects "abs" but not "fabs", and that
        # fabs() works in a fit. This is a regression test for the pre-existing
        # over-broad "abs" check, which also caught "fabs" and thus prevented
        # any user-defined function from using the absolute value.

        # This test should produce an exception:
        with self.assertRaises(Exception):
            model = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction(
                "SSQABS", "Default", "abs(a*X)"
            )

        # This test should succeed:
        model = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction(
            "SSQABS", "Default", "fabs(a*X)"
        )
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D_small, model, False
        )
        result = model.Solve()
        resultShouldBe = numpy.array([0.50368388])

        self.assertTrue(
            numpy.allclose(result, resultShouldBe, rtol=1.0e-06, atol=1.0e-300)
        )

    def test_digit_bearing_functions(self):
        # Check that digit-bearing function tokens (log10, arctan2, etc.) are
        # rejected by the gate due to the ConvertStringIntsToStringFloats bug,
        # and that they are accepted if the bug is patched. This is a
        # regression test for the pre-existing bug where ConvertStringIntsTo-
        # StringFloats mangled digit-bearing function tokens (log10 -> log10.0),
        # causing them to fail validation and thus be unavailable in UDFs.

        i = 0
        for expr in pyeq3.UdfSafety.numberContainingFunctions:
            with self.subTest(expr=expr):
                model = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction(
                    "SSQABS", "Default", f"{expr}(a*X)"
                )
                pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
                    DataForUnitTests.asciiDataInColumns_2D_small, model, False
                )

                self.assertIsNotNone(model.userFunctionCodeObject)
            i += 1

        # There should be 5 functions that contain digits
        self.assertEqual(i, 5)


if __name__ == "__main__":
    unittest.main()

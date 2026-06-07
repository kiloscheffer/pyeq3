import sys
import os
import unittest

# the pyeq3 directory is located up one level from here
if os.path.join(sys.path[0][: sys.path[0].rfind(os.sep)], "..") not in sys.path:
    sys.path.append(os.path.join(sys.path[0][: sys.path[0].rfind(os.sep)], ".."))

import pyeq3
from . import DataForUnitTests

import numpy
import scipy.interpolate

numpy.seterr(all="ignore")


class TestSolverService(unittest.TestCase):
    def test_SolveUsingODR_3D(self):
        coefficientsShouldBe = numpy.array([-0.0493, -0.90509, 1.2808])
        model = pyeq3.Models_3D.Polynomial.Linear("ODR")
        model.estimatedCoefficients = numpy.array(
            [0.2, -1.0, 1.0]
        )  # starting values for the ODR solver
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_3D, model, False
        )
        coefficients = pyeq3.solverService().SolveUsingODR(model)
        self.assertTrue(
            numpy.allclose(
                coefficients, coefficientsShouldBe, rtol=1.0e-03, atol=1.0e-300
            )
        )

    def test_SolveUsingODR_2D(self):
        coefficientsShouldBe = numpy.array([-8.04624, 1.53032])
        model = pyeq3.Models_2D.Polynomial.Linear("ODR")
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D, model, False
        )
        coefficients = pyeq3.solverService().SolveUsingODR(model)
        self.assertTrue(
            numpy.allclose(
                coefficients, coefficientsShouldBe, rtol=1.0e-03, atol=1.0e-300
            )
        )

    def test_SolveUsingLevenbergMarquardt_3D(self):
        coefficientsShouldBe = numpy.array([0.28658387, -0.90215776, 1.15483863])
        model = pyeq3.Models_3D.Polynomial.Linear("SSQABS")
        # starting values for the simplex solver
        model.estimatedCoefficients = numpy.array([0.2, -1.0, 1.0])
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_3D, model, False
        )
        coefficients = pyeq3.solverService().SolveUsingSelectedAlgorithm(
            model, inAlgorithmName="Levenberg-Marquardt"
        )
        self.assertTrue(
            numpy.allclose(
                coefficients, coefficientsShouldBe, rtol=1.0e-05, atol=1.0e-300
            )
        )

    def test_SolveUsingLevenbergMarquardt_2D(self):
        coefficientsShouldBe = numpy.array([-8.01913565, 1.5264473])
        model = pyeq3.Models_2D.Polynomial.Linear("SSQABS")
        # starting values for the simplex solver
        model.estimatedCoefficients = numpy.array([-4.0, 2.0])
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D, model, False
        )
        coefficients = pyeq3.solverService().SolveUsingSelectedAlgorithm(
            model, inAlgorithmName="Levenberg-Marquardt"
        )
        self.assertTrue(
            numpy.allclose(
                coefficients, coefficientsShouldBe, rtol=1.0e-06, atol=1.0e-300
            )
        )

    def test_SolveUsingSimplex_3D(self):
        coefficientsShouldBe = numpy.array([0.28658383, -0.90215775, 1.15483864])
        model = pyeq3.Models_3D.Polynomial.Linear("SSQABS")
        # starting values for the simplex solver
        model.estimatedCoefficients = numpy.array([1.0, 1.0, 1.0])
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_3D, model, False
        )
        coefficients = pyeq3.solverService().SolveUsingSimplex(model)
        self.assertTrue(
            numpy.allclose(
                coefficients, coefficientsShouldBe, rtol=1.0e-06, atol=1.0e-300
            )
        )

    def test_SolveUsingSimplex_SSQABS_2D(self):
        coefficientsShouldBe = numpy.array([-8.01913562, 1.52644729])
        model = pyeq3.Models_2D.Polynomial.Linear("SSQABS")
        # starting values for the simplex solver
        model.estimatedCoefficients = numpy.array([1.0, 1.0])
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D, model, False
        )
        coefficients = pyeq3.solverService().SolveUsingSimplex(model)
        self.assertTrue(
            numpy.allclose(
                coefficients, coefficientsShouldBe, rtol=1.0e-06, atol=1.0e-300
            )
        )

    def test_SolveUsingSimplex_SSQREL_2D(self):
        coefficientsShouldBe = numpy.array([-6.74510573, 1.32459622])
        model = pyeq3.Models_2D.Polynomial.Linear("SSQREL")
        # starting values for the simplex solver
        model.estimatedCoefficients = numpy.array([1.0, 1.0])
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D, model, False
        )
        coefficients = pyeq3.solverService().SolveUsingSimplex(model)
        self.assertTrue(
            numpy.allclose(
                coefficients, coefficientsShouldBe, rtol=1.0e-06, atol=1.0e-300
            )
        )

    def test_SolveUsingDE_3D(self):
        model = pyeq3.Models_3D.UserDefinedFunction.UserDefinedFunction(
            "SSQABS", "Default", "a + b*X + c*Y"
        )
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_3D_small, model, False
        )
        coefficients = pyeq3.solverService().SolveUsingDE(model)
        fittingTarget = model.CalculateAllDataFittingTarget(coefficients)
        self.assertTrue(fittingTarget <= 0.1)

    def test_SolveUsingDE_2D(self):
        coefficientsShouldBe = numpy.array([-7.92223965, 1.51863709])
        model = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction(
            "SSQABS", "Default", "m*X + b"
        )
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D_small, model, False
        )
        coefficients = pyeq3.solverService().SolveUsingDE(model)
        self.assertTrue(
            numpy.allclose(
                coefficients, coefficientsShouldBe, rtol=1.0e-05, atol=1.0e-300
            )
        )

    def test_SolveUsingDE_emptyNumpyArrayEstimate_doesNotRaise(self):
        # Regression for issue #16: assigning an EMPTY numpy array to
        # estimatedCoefficients used to crash on the DE path. The check
        # `if inModel.estimatedCoefficients != []` evaluated
        # `numpy.array([]) != []`, which is an empty bool array, and `if`
        # on it raises "The truth value of an empty array is ambiguous".
        model = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction(
            "SSQABS", "Default", "m*X + b"
        )
        model.estimatedCoefficients = numpy.array([])
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D_small, model, False
        )
        coefficients = pyeq3.solverService().SolveUsingDE(model)
        self.assertEqual(len(coefficients), 2)

    def test_solvedCoefficients_isOneDimensionalNumpyArray_forAnalyticModel(self):
        # Contract: after Solve(), an analytic equation's solvedCoefficients
        # is a 1-D numpy array of floats, one entry per coefficient designator.
        model = pyeq3.Models_2D.Polynomial.Linear("SSQABS")
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D, model, False
        )
        model.Solve()
        self.assertFalse(model.splineFlag)
        self.assertIsInstance(model.solvedCoefficients, numpy.ndarray)
        self.assertEqual(model.solvedCoefficients.ndim, 1)
        self.assertEqual(
            len(model.solvedCoefficients),
            len(model.GetCoefficientDesignators()),
        )

    def test_solvedCoefficients_isTckTuple_forSplineModel(self):
        # Contract: after Solve(), a spline model's solvedCoefficients is the
        # scipy tck representation (a tuple), NOT a coefficient array.
        # 2D: UnivariateSpline._eval_args == (knots, coefficients, degree).
        model = pyeq3.Models_2D.Spline.Spline(inSmoothingFactor=1.0, inXOrder=3)
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D, model, False
        )
        model.Solve()
        self.assertTrue(model.splineFlag)
        self.assertIsInstance(model.solvedCoefficients, tuple)
        self.assertEqual(len(model.solvedCoefficients), 3)

    def test_SolveUsingSpline_3D(self):
        xKnotPointsShouldBe = numpy.array([0.607, 0.607, 0.607, 3.017, 3.017, 3.017])
        yKnotPointsShouldBe = numpy.array([1.984, 1.984, 1.984, 3.153, 3.153, 3.153])
        coefficientsShouldBe = numpy.array(
            [
                2.33418963,
                1.80079612,
                5.07902936,
                0.54445029,
                1.04110843,
                2.14180324,
                0.26992805,
                0.39148852,
                0.8177307,
            ]
        )
        testEvaluationShouldBe = numpy.array([0.76020577997])
        model = pyeq3.Models_3D.Spline.Spline(
            inSmoothingFactor=1.0, inXOrder=2, inYOrder=2
        )
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_3D, model, False
        )
        fittedParameters = pyeq3.solverService().SolveUsingSpline(model)

        # example of later using the saved spline knot points and coefficients
        unFittedSpline = scipy.interpolate.SmoothBivariateSpline(
            model.dataCache.allDataCacheDictionary["X"],
            model.dataCache.allDataCacheDictionary["Y"],
            model.dataCache.allDataCacheDictionary["DependentData"],
            s=model.smoothingFactor,
            kx=model.xOrder,
            ky=model.yOrder,
        )
        unFittedSpline.tck = fittedParameters
        testEvaluation = unFittedSpline.ev(2.5, 2.5)

        self.assertTrue(
            numpy.allclose(
                testEvaluation, testEvaluationShouldBe, rtol=1.0e-10, atol=1.0e-300
            )
        )
        self.assertTrue(numpy.equal(fittedParameters[0], xKnotPointsShouldBe).all())
        self.assertTrue(numpy.equal(fittedParameters[1], yKnotPointsShouldBe).all())
        self.assertTrue(
            numpy.allclose(
                fittedParameters[2], coefficientsShouldBe, rtol=1.0e-06, atol=1.0e-300
            )
        )

    def test_SolveUsingSpline_2D(self):
        knotPointsShouldBe = numpy.array(
            [5.357, 5.357, 5.357, 5.357, 9.861, 9.861, 9.861, 9.861]
        )
        coefficientsShouldBe = numpy.array(
            [0.38297001, 1.95535226, 4.59605664, 7.16162379, 0.0, 0.0, 0.0, 0.0]
        )
        testEvaluationShouldBe = numpy.array([4.02361487093])
        model = pyeq3.Models_2D.Spline.Spline(inSmoothingFactor=1.0, inXOrder=3)
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D, model, False
        )
        fittedParameters = pyeq3.solverService().SolveUsingSpline(model)

        # example of later using the saved spline knot points and coefficients
        unFittedSpline = scipy.interpolate.UnivariateSpline(
            model.dataCache.allDataCacheDictionary["X"],
            model.dataCache.allDataCacheDictionary["DependentData"],
            s=model.smoothingFactor,
            k=model.xOrder,
        )
        unFittedSpline._eval_args = fittedParameters
        testEvaluation = unFittedSpline(numpy.array([8.0]))

        self.assertTrue(
            numpy.allclose(
                testEvaluation, testEvaluationShouldBe, rtol=1.0e-10, atol=1.0e-300
            )
        )
        self.assertTrue(numpy.equal(fittedParameters[0], knotPointsShouldBe).all())
        self.assertTrue(
            numpy.allclose(
                fittedParameters[1], coefficientsShouldBe, rtol=1.0e-06, atol=1.0e-300
            )
        )

    def test_SolveUsingLinear_2D(self):
        coefficientsShouldBe = numpy.array(
            [-8.0191356407516956e00, 1.5264472941853220e00]
        )
        model = pyeq3.Models_2D.Polynomial.Linear("SSQABS")
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D, model, False
        )
        coefficients = pyeq3.solverService().SolveUsingLinear(model)
        self.assertTrue(
            numpy.allclose(
                coefficients, coefficientsShouldBe, rtol=1.0e-10, atol=1.0e-300
            )
        )

    def test_SolveUsingLinear_3D(self):
        coefficientsShouldBe = numpy.array(
            [2.8658381589774945e-01, -9.0215775175410395e-01, 1.1548386445491325e00]
        )
        model = pyeq3.Models_3D.Polynomial.Linear("SSQABS")
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_3D, model, False
        )
        coefficients = pyeq3.solverService().SolveUsingLinear(model)
        self.assertTrue(
            numpy.allclose(
                coefficients, coefficientsShouldBe, rtol=1.0e-10, atol=1.0e-300
            )
        )

    def test_ExponentialSensitivity_2D(self):
        coefficientsShouldBe = numpy.array([2.0, 0.1, -3000.0])
        model = pyeq3.Models_2D.Exponential.Exponential("SSQABS", "Offset")
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataForExponentialSensitivityTest, model, False
        )
        model.Solve()
        self.assertTrue(
            numpy.allclose(
                model.solvedCoefficients,
                coefficientsShouldBe,
                rtol=1.0e-10,
                atol=1.0e-300,
            )
        )

    def test_UserDefinedFunction_2D(self):
        coefficientsShouldBe = numpy.array([3.28686108e-04, 1.30583728])
        functionString = "Scale * exp(X) + offset"
        model = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction(
            inUserFunctionString=functionString
        )
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
            DataForUnitTests.asciiDataInColumns_2D, model, False
        )
        model.Solve()
        self.assertTrue(
            numpy.allclose(
                model.solvedCoefficients,
                coefficientsShouldBe,
                rtol=1.0e-8,
                atol=1.0e-300,
            )
        )


if __name__ == "__main__":
    unittest.main()

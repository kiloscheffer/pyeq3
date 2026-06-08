import sys
import pyeq3
import numpy as np

fittingTargetText = "SSQABS"
precision = 5
np.set_printoptions(precision=precision, suppress=True)
deEstimatedCoefficients = []

print("It is very rare for an algorithm to fit better than Levenberg-Marquardt,")
print("This example shows how to construct a test to determine if this is true.")
print()

fittingAlgorithmNames = pyeq3.solverService.ListOfNonLinearSolverAlgorithmNames

# First we solve with Levenberg-Marquardt to get a baseline value for the fitting target
fittingAlgorithmName = fittingAlgorithmNames[0]
equation = pyeq3.Models_2D.BioScience.AphidPopulationGrowth(fittingTargetText, "Offset")

pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
    equation.exampleData, equation, False
)

equation.deEstimatedCoefficients = deEstimatedCoefficients
equation.Solve(inNonLinearSolverAlgorithmName=fittingAlgorithmName)
deEstimatedCoefficients = equation.deEstimatedCoefficients
value = equation.CalculateAllDataFittingTarget(equation.solvedCoefficients)

print(
    f"{fittingTargetText} = {value:.2E} for the fitting algorithm {fittingAlgorithmName}"
)
print("Coefficients:", equation.solvedCoefficients)
()
sys.stdout.flush()

LM_value = value


for fittingAlgorithmName in fittingAlgorithmNames[1:]:
    equation = pyeq3.Models_2D.BioScience.AphidPopulationGrowth(
        fittingTargetText, "Offset"
    )

    if (
        equation.CanLinearSolverBeUsedForSSQABS() is True
        and fittingTargetText == "SSQABS"
    ):
        raise Exception(
            "The selected combination of equation and SSQABS fitting target "
            "does not use a non-linear solver"
        )

    if fittingTargetText == "ODR":
        raise Exception("ODR cannot use multiple fitting algorithms")

    pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
        equation.exampleData, equation, False
    )

    equation.deEstimatedCoefficients = deEstimatedCoefficients
    equation.Solve(inNonLinearSolverAlgorithmName=fittingAlgorithmName)
    # no need to re-run genetic algorithm
    deEstimatedCoefficients = equation.deEstimatedCoefficients
    value = equation.CalculateAllDataFittingTarget(equation.solvedCoefficients)

    if value < LM_value * (1.0 - 10.0 ** (-precision)):
        print(
            f"Algorithm {fittingAlgorithmName} fitted better than Levenberg-Marquardt!"
        )
        print(
            f"{fittingTargetText} = {value:.2E} for the fitting algorithm {fittingAlgorithmName}"
        )
    else:
        print(
            f"Algorithm {fittingAlgorithmName} did not fit better than Levenberg-Marquardt."
        )

    sys.stdout.flush()

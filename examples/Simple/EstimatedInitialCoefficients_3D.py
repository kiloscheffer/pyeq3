import pyeq3

# see IModel.fittingTargetDictionary
equation = pyeq3.Models_3D.BioScience.HighLowAffinityIsotopeDisplacement("SSQABS")

pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(
    equation.exampleData, equation, False
)


# Note that all coefficients are set with estimated values
equation.estimatedCoefficients = [2.0, 3.0e13]


equation.Solve()

dim = equation.GetDimensionality()
target = equation.fittingTargetDictionary[equation.fittingTarget]
value = equation.CalculateAllDataFittingTarget(equation.solvedCoefficients)
print(equation.GetDisplayName(), str(dim) + "D")
print(f"{target} = {value:.2E}")
print("Fitted Parameters:")
for i in range(len(equation.solvedCoefficients)):
    print(
        "    %s = %-.5E"
        % (equation.GetCoefficientDesignators()[i], equation.solvedCoefficients[i])
    )

import pyeq3
import numpy as np
import matplotlib.pyplot as plt

data = np.array(
    [
        [5.357, 10.376],
        [5.457, 10.489],
        [5.797, 10.874],
        [5.936, 11.049],
        [6.161, 11.327],
        [6.697, 12.054],
        [6.731, 12.077],
        [6.775, 12.138],
        [8.442, 14.744],
        [9.769, 17.068],
        [9.861, 17.104],
    ]
)

for functionString, estimatedCoefficients in [
    ["a + b * X + c * X * X", np.array([0.0, -1.0, 0.0])],
    ["a + b * X", np.array([-0.164, -0.1])],
    ["a + b * X - c * exp(X)", np.array([0.0, 0.69, -2])],
]:
    # Create the equation object
    # note that the constructor is passed the function string here
    equation = pyeq3.Models_2D.UserDefinedFunction.UserDefinedFunction(
        inUserFunctionString=functionString
    )
    equation.estimatedCoefficients = estimatedCoefficients

    # Process the data
    pyeq3.dataConvertorService().ProcessNumpyArray(data, equation, False)

    # Solve the equation based on the processed data and initial coefficients
    equation.Solve()

    # create a smooth curve for plotting
    range = data[:, 0].max() - data[:, 0].min()
    f = 0.1
    x_new = np.linspace(
        data[:, 0].min() - range * f, data[:, 0].max() + range * f, 1001
    )
    y_new = equation.CalculateModelPredictionsFromNewData(x_new)

    # Print some data to standard output
    np_precision = np.get_printoptions()["precision"]
    np.set_printoptions(precision=5)
    print(equation.GetCoefficientDesignators())
    print(equation.solvedCoefficients)
    np.set_printoptions(precision=np_precision)

    # Plot the fitted curve
    plt.plot(x_new, y_new, label=functionString)

# Plot the original data points
plt.scatter(data[:, 0], data[:, 1])

plt.legend()
plt.xlabel("X")
plt.ylabel("Y")
plt.grid()
plt.title("Fitted Curves")
plt.show()

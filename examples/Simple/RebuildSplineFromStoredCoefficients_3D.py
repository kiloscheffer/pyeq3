import pyeq3
import numpy
import json

# A spline fit keeps its result in two places: solvedCoefficients (the spline
# tck) and a live scipy spline object built during Solve(). The live object is
# not JSON-serializable, so an application that stores a fit in a database or a
# JSON session store can only persist solvedCoefficients and the spline orders.
# This example saves those values as JSON, then rebuilds a working fit from them
# with no live scipy object.


# parameters are smoothing, xOrder, yOrder
equation = pyeq3.Models_3D.Spline.Spline(1.0, 3, 3)  # cubic 3D spline
data = equation.exampleData

pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(data, equation, False)
equation.Solve()

originalPredictions = equation.CalculateModelPredictions(
    equation.solvedCoefficients, equation.dataCache.allDataCacheDictionary
)


##########################################################


# Store the fit as JSON. For a 3D spline the tck does not include the spline
# degrees, so the orders are saved alongside it; the model carries them as
# xOrder and yOrder.
xKnots, yKnots, coefficients = equation.solvedCoefficients
stored = json.dumps(
    {
        "coefficients": [xKnots.tolist(), yKnots.tolist(), coefficients.tolist()],
        "xOrder": equation.xOrder,
        "yOrder": equation.yOrder,
    }
)


##########################################################


# Later, or in another process, rebuild a working spline from the stored JSON
# alone. This fresh instance has never been solved and has no live scipy
# object; CalculateModelPredictions reconstructs one on demand.
loaded = json.loads(stored)

reloaded = pyeq3.Models_3D.Spline.Spline()
pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(data, reloaded, False)
reloaded.xOrder = loaded["xOrder"]
reloaded.yOrder = loaded["yOrder"]
reloaded.solvedCoefficients = loaded["coefficients"]

# build the X/Y cache terms for the points to evaluate; Solve() normally does
# this, so a reconstruct-only instance has to do it explicitly
reloaded.dataCache.FindOrCreateAllDataCache(reloaded)

rebuiltPredictions = reloaded.CalculateModelPredictions(
    reloaded.solvedCoefficients, reloaded.dataCache.allDataCacheDictionary
)


print(
    "predictions match after reconstruction:",
    numpy.allclose(originalPredictions, rebuiltPredictions),
)

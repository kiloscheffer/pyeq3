import pyeq3
import numpy
import json

# A spline fit keeps its result in two places: solvedCoefficients (the spline
# tck) and a live scipy spline object built during Solve(). The live object is
# not JSON-serializable, so an application that stores a fit in a database or a
# JSON session store can only persist solvedCoefficients and the spline orders.
# This example saves those values as JSON, then rebuilds a working fit from
# them with no live scipy object.

# arguments passed to the 3D spline constructor are smoothing, xOrder, yOrder
equation = pyeq3.Models_3D.Spline.Spline(1.0, 3, 3)  # cubic 3D spline
data = equation.exampleData

pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(data, equation, False)
equation.Solve()

originalPredictions = equation.CalculateModelPredictions(
    equation.solvedCoefficients, equation.dataCache.allDataCacheDictionary
)

# We can store the optimized spline as a JSON.
# For a 3D spline the solvedCoefficients (tck)
# is a tuple of three arrays: xKnots, yKnots, and coefficients.
# These arrays do not include the spline orders which
# are needed to reconstruct the spline, so we extract those
# from xOrder and yOrder and store them alongside the tck in the JSON.
xKnots, yKnots, coefficients = equation.solvedCoefficients
stored = json.dumps(
    {
        "coefficients": [xKnots.tolist(), yKnots.tolist(), coefficients.tolist()],
        "xOrder": equation.xOrder,
        "yOrder": equation.yOrder,
    }
)

# Later, or in another process, rebuild the spline from the stored JSON
# This fresh instance ("reloaded") has never been solved and has no live scipy
# object; CalculateModelPredictions reconstructs one on demand.
loaded = json.loads(stored)

reloaded = pyeq3.Models_3D.Spline.Spline()
reloaded.xOrder = loaded["xOrder"]
reloaded.yOrder = loaded["yOrder"]
reloaded.solvedCoefficients = loaded["coefficients"]

# we have to load the data into the reloaded instance so that it can build the
# cache terms that CalculateModelPredictions needs; Solve() normally does this,
# so a reconstruct-only instance has to do it explicitly
pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(data, reloaded, False)

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

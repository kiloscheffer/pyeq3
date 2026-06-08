import numpy as np


def DatumInformation(model, precision=16):
    """
    Calculates and prints absolute, relative, and percent errors
    for each data point in a parameterised model.

    Parameters
    ----------
    model : pyeq3.IModel object
        A model object that has already been parameterised
        using pyeq3.IModelSolve().

    precision : int, optional
        The number of decimal places to use when printing the data.
        Default is 16.
    """

    # calculate absolute, relative, and percent errors from the fit
    model.CalculateModelErrors(
        model.solvedCoefficients, model.dataCache.allDataCacheDictionary
    )

    cache_dict = model.dataCache.allDataCacheDictionary
    # this section prints information on each individual data point
    for i in range(len(cache_dict["DependentData"])):
        print(f"X: {cache_dict['IndependentData'][0][i]:.{precision}E}")

        if model.GetDimensionality() == 2:
            print(f"Y: {cache_dict['DependentData'][i]:.{precision}E}")
        else:
            print(f"Y: {cache_dict['IndependentData'][1][i]:.{precision}E}")
            print(f"Z: {cache_dict['DependentData'][i]:.{precision}E}")

        print(f"Model Prediction: {model.modelPredictions[i]:.{precision}E}")
        print(f"Abs. Error: {model.modelAbsoluteError[i]:.{precision}E}")

        if not model.dataCache.DependentDataContainsZeroFlag:
            print(f"Rel. Error: {model.modelRelativeError[i]:.{precision}E}")
            print(f"Percent Error: {model.modelPercentError[i]:.{precision}E}")
        else:
            print()
    print()

    return None


def FitStatistics(model, precision=16):
    """
    Calculates and prints fit statistics
    for a parameterised model.

    Parameters
    ----------
    model : pyeq3.IModel object
        A model object that has already been parameterised
        using pyeq3.IModelSolve().
    precision : int, optional
        The number of decimal places to use when printing the data.
        Default is 16.
    """
    ##########################################################
    # overall fit and parameter statistics output section

    model.CalculateCoefficientAndFitStatistics()

    if model.upperCoefficientBounds or model.lowerCoefficientBounds:
        print("You entered coefficient bounds. Parameter statistics may")
        print("not be valid for parameter values at or near the bounds.")
        print()

    print(f"Degrees of freedom error: {model.df_e}")
    print(f"Degrees of freedom regression: {model.df_r}")

    if model.rmse is None:
        print("Root Mean Squared Error (RMSE): n/a")
    else:
        print(f"Root Mean Squared Error (RMSE): {model.rmse:.{precision}E}")

    if model.r2 is None:
        print("R-squared: n/a")
    else:
        print(f"R-squared: {model.r2:.{precision}E}")

    if model.r2adj is None:
        print("R-squared adjusted: n/a")
    else:
        print(f"R-squared adjusted: {model.r2adj:.{precision}E}")

    if model.Fstat is None:
        print("Model F-statistic: n/a")
    else:
        print(f"Model F-statistic: {model.Fstat:.{precision}E}")

    if model.Fpv is None:
        print("Model F-statistic p-value: n/a")
    else:
        print(f"Model F-statistic p-value: {model.Fpv:.{precision}E}")

    if model.ll is None:
        print("Model log-likelihood: n/a")
    else:
        print(f"Model log-likelihood: {model.ll:.{precision}E}")

    if model.aic is None:
        print("Model AIC: n/a")
    else:
        print(f"Model AIC: {model.aic:.{precision}E}")

    if model.bic is None:
        print("Model BIC: n/a")
    else:
        print(f"Model BIC: {model.bic:.{precision}E}")

    print()
    print("Individual Parameter Statistics:")
    for i in range(len(model.solvedCoefficients)):
        if model.tstat_beta is None:
            tstat = "n/a"
        else:
            tstat = f"{model.tstat_beta[i]:.{precision}E}"

        if model.pstat_beta is None:
            pstat = "n/a"
        else:
            pstat = f"{model.pstat_beta[i]:.{precision}E}"

        if model.sd_beta is not None:
            print(
                f"Coefficient {model.GetCoefficientDesignators()[i]} = "
                f"{model.solvedCoefficients[i]:.{precision}E}, "
                f"std error: {model.sd_beta[i]:.{precision}E}"
            )

        else:
            print(
                f"Coefficient {model.GetCoefficientDesignators()[i]} = "
                f"{model.solvedCoefficients[i]:.{precision}E}, "
                f"std error: n/a"
            )
        print(
            f"          t-stat: {tstat}, p-stat: {pstat}, "
            "95 percent confidence intervals: "
            f"[{model.ci[i][0]:.{precision}E}, {model.ci[i][1]:.{precision}E}]"
        )

    print()
    print("Coefficient Covariance Matrix:")
    # get current numpy print options so we can restore them after printing the covariance matrix
    np_print_options = np.get_printoptions()
    np.set_printoptions(precision=precision, suppress=True)
    print(model.cov_beta)

    # restore original numpy print options
    np.set_printoptions(**np_print_options)

    return None

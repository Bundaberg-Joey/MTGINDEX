def price_weighted_index(prices, weights, prior_level):
    """Calculates the price weighted index level of a benchmark.
    $$level_t = level_{t-1} \times (1 + \sum_{i=0} c_i \cdot w_i)$$

    Parameters
    ----------
    prices : list, shape(<num_constituents>)
        Price evaluations of constituents.

    weights : list, shape(<num_constituents>)
        Price based weightings of constituents within the benchmark

    prior_level : float
        Previously calculated index value for the benchmark.

    Returns
    -------
    new_level : float
        Price weighted index value.
    """
    assert len(weights) == len(prices), F'Prices {len(prices)} and Weights {len(weights)} passed are not equal length.'
    weighted_prices = sum((p*w for p, w in zip(prices, weights)))
    new_level = prior_level * (1 + weighted_prices)
    return new_level
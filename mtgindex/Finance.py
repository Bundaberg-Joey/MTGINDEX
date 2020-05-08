def price_weighted_index(prior_level, constituent_prices, **kwargs):
    """Calculates a price weighted index level based on returns.
    All constituents are assumed to hold an equally weighted contribution to the index (sum of weights is 1).
    level_t = level_{t-1} \times (1 + \sum_{i=0} c_i \cdot w_i)

    Returns
    -------
    None
    """
    # weighting = 1/len(constituent_prices)
    # level = prior_level * (1 + sum(constituent_prices) * weighting)
    # return level
    return NotImplementedError

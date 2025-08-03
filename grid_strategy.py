import numpy as np

def setup_grid(min_price, max_price, levels):
    return np.linspace(min_price, max_price, levels)

def should_buy(price, grid_levels):
    return any(abs(price - level) < 0.01 for level in grid_levels)

def should_sell(price, grid_levels):
    return any(abs(price - level) < 0.01 for level in grid_levels)

from .base import TestBase

from api.utils.cost_calculation_py import calculate_cost
from api.utils.api.utils import cost_calculation


def test_calculate_cost(benchmark):
    benchmark.pedantic(calculate_cost, args=(60, 10, 5, 515), iterations=3, rounds=1000000)


def test_calculate_cost_cython(benchmark):
    benchmark.pedantic(cost_calculation.calculate_cost, args=(60, 10, 5, 515), iterations=3, rounds=1000000)

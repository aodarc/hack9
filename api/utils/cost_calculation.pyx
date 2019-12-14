from libc.math cimport ceil


def calculate_cost(int initial, int duration, float increment, float rate):
    return ((ceil((initial + duration) / increment) * increment) * (rate / 60.0)) // 0.01 / 100

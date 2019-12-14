from libc.math cimport ceil


def calculate_cost(int initial, int duration, int increment, float rate):
    return ceil((initial + duration) / increment) * increment * (rate / 60.0)

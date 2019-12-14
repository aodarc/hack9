from libc.math cimport ceil, round


def calculate_cost(int initial, int duration, float increment, float rate):
    return round(((ceil((initial + duration) / increment) * increment) * (rate / 60.0)) * 100) / 100

def calculate_round(int initial, int duration, float increment):
    return ceil((initial + duration) / increment) * increment

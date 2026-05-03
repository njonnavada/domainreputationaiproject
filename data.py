# data.py

def get_training_data():
    X = [
        [5, 12, 2],    # BAD
        [20, 2, 0],    # GOOD
        [8, 6, 0.5],   # AVERAGE
        [15, 3, 0],    # GOOD
        [4, 15, 3],    # BAD
        [9, 7, 0.8]    # AVERAGE
    ]

    y = ["BAD", "GOOD", "AVERAGE", "GOOD", "BAD", "AVERAGE"]

    return X, y
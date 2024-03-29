from operator import le
import matplotlib.pyplot as plt
import numpy as np
from math import ceil
from multiprocessing import Process
from os import execl
from time import time
from typing import Union

seed = int(time() * 1e6)
print(f"Samples seed: {seed}")
flag_cpp = True
flag_cuda = True

epsilon = 0.49
training_size = 1024
testing_size = 1000
true_power = 5
fit_power = 5


def power_expand(x: np.ndarray, power: int) -> np.ndarray:
    # | x0 |    | x0 x0^2 ... |
    # | x1 | => | x1 x1^2 ... |
    # | .. |    | .. .... ... |
    X = np.empty((x.shape[0], power))
    X[:, 0] = x
    for i in range(1, power):
        X[:, i] = x ** (i + 1)
    return X


def generate_random_weights(power: int, w_low: float, w_high: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(w_low, w_high, power + 1)


def generate_random_samples(
    w: np.ndarray,
    noise_level: float,
    sample_size: int
):
    # return x and y, respectively
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, sample_size)
    y = np.c_[np.ones(sample_size), power_expand(x, w.shape[0] - 1)].dot(w)
    y += rng.normal(0, np.std(y) * noise_level, sample_size)
    return x, y


def mean_squared_error(predicted_y: np.ndarray, y: np.ndarray) -> float:
    return np.square(predicted_y - y).sum() / predicted_y.shape[0]


def export_figures(
    x_training: np.ndarray,
    y_training: np.ndarray,
    contamination_indices: Union[np.ndarray, None],
    transformed_x: Union[np.ndarray, None],
    transformed_y: Union[np.ndarray, None],
    predicted_y_training: np.ndarray,
    x_testing: np.ndarray,
    y_testing: np.ndarray,
    predicted_y_testing: np.ndarray,
    test_name: str
):
    plt.figure()
    plt.suptitle(test_name)
    plt.title("Training Set")
    plt.grid()
    if contamination_indices is None:
        plt.scatter(x_training, y_training, s=4, c="blue", label="True Samples")
    else:
        plt.scatter(
            np.delete(x_training, contamination_indices),
            np.delete(y_training, contamination_indices),
            s=4,
            c="blue",
            label="Raw Samples"
        )
        plt.scatter(
            x_training[contamination_indices],
            y_training[contamination_indices],
            s=4,
            c="gray",
            label="Contamination"
        )
    if transformed_x is not None:
        plt.scatter(
            transformed_x,
            transformed_y,
            s=16,
            c="limegreen",
            marker="^",
            label="Transformed Samples"
        )
    plt.scatter(x_training, predicted_y_training,
                s=4, c="red", label="Predictions")
    plt.legend()
    plt.xlabel("x")
    plt.xlim(-1, 1)
    plt.ylabel("y")
    plt.ylim(y_training.min(), y_training.max())
    plt.savefig("training.png")
    plt.close()

    plt.figure()
    plt.suptitle(test_name)
    plt.title(f"Testing Set, MSE={mean_squared_error(predicted_y_testing, y_testing)}")
    plt.grid()
    plt.scatter(x_testing, y_testing, s=4, c="blue", label="True Samples")
    plt.scatter(x_testing, predicted_y_testing, s=4, c="red", label="Predictions")
    plt.legend()
    plt.xlabel("x")
    plt.xlim(-1, 1)
    plt.ylabel("y")
    plt.ylim(y_training.min(), y_training.max())
    plt.savefig("testing.png")
    plt.close()


rng = np.random.default_rng(seed)
w = generate_random_weights(true_power, -10, 10)
x_training, y_training = generate_random_samples(w, 1, training_size)
contamination_size = ceil(epsilon * training_size)
contamination_indices = np.argsort(x_training)[int(training_size * (1 - epsilon) * 0.5):int(training_size * (1 + epsilon) * 0.5)]
y_training[contamination_indices] += y_training.max() - y_training.min()
x_testing, y_testing = generate_random_samples(w, 0, testing_size)

X = power_expand(x_training, fit_power)
with open("in.txt", "w") as f:
    for i in range(training_size):
        for j in range(fit_power):
            f.write(f"{X[i][j]} ")
        f.write(f" {y_training[i]}\n")

if flag_cpp:
    p = Process(target=execl, args=("regress_cpp", "regress_cpp"))
    p.start()
    print("Running the C++ implementation, usually takes ~50s for 1000 models, or ~5s for 100 models")
    p.join()

if flag_cuda:
    p = Process(target=execl, args=("regress_cuda", "regress_cuda"))
    p.start()
    print("Running the CUDA implementation, usually takes <1s for <1000 models")
    p.join()

with open("out.txt", "r") as f:
    w = np.fromiter(map(float, f.read().split()), float)

predicted_y_training = np.c_[np.ones(X.shape[0]), X].dot(w)

X = power_expand(x_testing, fit_power)
predicted_y_testing = np.c_[np.ones(X.shape[0]), X].dot(w)

export_figures(
    x_training,
    y_training,
    contamination_indices,
    None,
    None,
    predicted_y_training,
    x_testing,
    y_testing,
    predicted_y_testing,
    f"Random Contamination (ε-then-Z-score-trimmed Huber Loss)"
)

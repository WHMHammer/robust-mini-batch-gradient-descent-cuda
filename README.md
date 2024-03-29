# Robust Mini-Batch Gradient Descent

This repository contains the source codes for the final project of COMP_SCI 468: Programming Massively Parallel Processors with CUDA at Northwestern University.

In this project, we implemented the best model (ε-then-Z-score-trimmed Huber Loss without preprocessing) found in [Robust Mini-Batch Gradient Descent](https://github.com/WHMHammer/robust-mini-batch-gradient-descent) with C++ (baseline) and CUDA.

**Note**: the CUDA codes are optimized for RTX 2060 Super graphics cards in the Wilkinson lab.

For more details on the model itself, please visit the [Robust Mini-Batch Gradient Descent](https://github.com/WHMHammer/robust-mini-batch-gradient-descent) repo.

## Run Tests

```
make dependencies    # only before the first run
make                 # build both the C++ and the CUDA implementations
make run             # run the same test on both implementations
# make clean         # to clean up the binaries and input/output files generated
# make clobber       # to also clean up the graphs and python virtual environment
```

Two graphs, `testing.png` and `training.png` will be generated, showing the regression lines under the training set and the testing set. These graphs are generated to check the correctness of the implementation. For more test cases, please visit the [Robust Mini-Batch Gradient Descent](https://github.com/WHMHammer/robust-mini-batch-gradient-descent) repo.

## Results

| Implementation | # of models trained | Training Time (ms) |
|----------------|---------------------|--------------------|
| C++            | 1                   | 54.701             |
|                | 10                  | 542.758            |
|                | 100                 | 5,336.640          |
|                | 1000                | 54,236,484         |
| CUDA           | 1                   | 119.817            |
|                | 10                  | 121.361            |
|                | 100                 | 132.146            |
|                | 1000                | 848.172            |

## TODO

- Find out ways to reduce shared memory usage

- Add padding to adapt to non-power-of-2 batch sizes

## Contribution

[Hanming Wang](https://github.com/WHMHammer)

- Implemented the baseline implementation in C++

- Implemented a naive implementation in CUDA

- Implemented the python test script

- Parallelized residual calculation

- Parallelized merge sort (which was replaced by the later enumeration sort)

- Parallelize epsilon-trimming

- Parallelize z-score-trimming

- Parallelized loss and gradient calculation

- Implemented a local copy of the weight vector in shared memory and only write to global memory when the model is fully trained

- Changed `X` from row-major to column-major and applied other methods for coalesced global memory access

- Changed the batch sample selection mechanism to save the time from random number generator

- Applied thread coarsening

- Solved many thread divergence issues

[Jiren Li](https://github.com/Li-Jiren)

- Implemented the enumeration sort

- Implemented the odd-even sort (which was replaced by the enumeration sort)

- Unrolled the loops for the parallel merge sort (which was replaced by the later odd-even sort)

## Acknowledgement

We appreciate prof. [Nikos Hardavellas](https://users.cs.northwestern.edu/~hardav/) for the wonderful lectures throughout the quarter. Hanming especially thanks Nikos for the time spent during and beyond the office hours, answering the numerous questions (some being stupid) about CUDA.

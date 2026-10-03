# Team 2: Image Retrieval

This repository contains a notebook for retrieving museum images from the BBDD database using global image descriptors and histogram distance measures.

## Notebook

Run `C1_week1.ipynb` from top to bottom. It loads and sorts the images, computes eight descriptors, compares nine distance measures, evaluates every descriptor-distance pair on QSD1, and generates MAP comparison charts. The final section retrieves the top 10 BBDD IDs for every QST1 query with the selected CLAHE-LAB + L1 method.

## Data

- `BBDD/`: database images, named with numeric IDs such as `bbdd_00007.jpg`.
- `qsd1_w1/`: evaluation queries and `gt_corresps.pkl`, containing each query's relevant BBDD ID(s).
- `qst1_w1/`: test queries used to generate the top-10 result lists.
- `utils/extra_descriptors.py`: implementations of the additional descriptors and retrieval/output helpers.

The notebook expects these paths relative to the repository root. Query and database JPGs are sorted numerically by filename before processing.

## Environment

Install the notebook dependencies in the active Python environment:

```bash
pip install numpy opencv-python pandas matplotlib
```

## Results

The QSD1 evaluation compares eight descriptors with nine distance measures and writes:

- `results/map_at_1_5_leaderboard.csv`: MAP@1 and MAP@5 for all 72 combinations.
- `results/all_query_retrieval_results.csv`: top-five results and AP scores for every query-method pair.
- `results/best_two_methods_per_query.csv`: per-query results for the top two methods.

In the current run, CLAHE-LAB + L1 and CLAHE-LAB + histogram intersection tie for the best MAP@5 (0.6611), with MAP@1 of 0.6000.

The final QST1 cell saves a list of lists to `results/qst1_w1_results.pkl`. Each inner list contains the ten BBDD image IDs, as Python integers, in retrieval order; list positions correspond to numerically sorted QST1 query filenames.

# Team 2: Museum Painting Retrieval (MCV C1)

Retrieval of museum paintings from the `BBDD` database using colour histogram descriptors, similarity measures and, from week 2 on, background removal.

**Team:** Adrià Cantarero Carreras · Ivan Martin Campoy · Irene Pumares Benaiges · Lavish Ramchandani

## Repository structure

```
Team-2/
├── week1/
│   ├── C1_week1.ipynb        # global descriptors, distances, QSD1 evaluation, QST1 predictions
│   ├── data/                 # BBDD/, qsd1_w1/, qst1_w1/  (not tracked)
│   └── results/
├── week2/
│   ├── C1_week2.ipynb        # block/pyramid histograms, background removal on QSD2
│   ├── data/                 # BBDD/, qsd1_w1/, qsd2_w1/  (not tracked)
│   └── results/
├── utils/
│   └── extra_descriptors.py  # shared descriptors + retrieval / output helpers
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

Datasets are **not** in the repository (`data/` is git-ignored). Download them from the Virtual Campus and place them in each week's `data/` folder:

| Week | Needed in `weekN/data/` |
|------|-------------------------|
| 1 | `BBDD/`, `qsd1_w1/`, `qst1_w1/` |
| 2 | `BBDD/`, `qsd1_w1/`, `qsd2_w1/` |

> **Moving from the old layout?** Datasets used to be tracked in git. When you pull the commit that moved everything into week folders, git deletes your `qsd1_w1/` and `qsd2_w1/` folders. Copy them somewhere outside the repo before pulling. Alternatively, restore them afterwards with `git restore --source=bd69ed7 data/` and move them into `weekN/data/`.

Open and run each notebook from its own week folder (the default in Jupyter and VS Code). Paths are relative to it (`./data/...`, `./results/...`), and the first cell adds the repo root to `sys.path` so `utils` can be imported.

## Week 1 (`week1/C1_week1.ipynb`)

1. Compute image descriptors: 1D grey/HSV histograms plus extra descriptors (chroma LAB/HSV, CLAHE-LAB, hue-weighted, LBP).
2. Compare similarity measures.
3. Evaluate every descriptor and distance pair on QSD1 with MAP@1 and MAP@5.
4. Retrieve the top 10 BBDD IDs for every QST1 query with the two best methods.

Outputs in `week1/results/`:

- `map_at_1_5_leaderboard.csv`: MAP@1 / MAP@5 for all (parameter-optimised) combinations.
- `parameter_grid_search.csv`: descriptor parameter grid search summary.
- `all_query_retrieval_results.csv`: top-5 results and AP for every query and method pair.
- `best_two_methods_per_query.csv`: per-query results for the two best methods.
- `QST1/method1/result.pkl`, `QST1/method2/result.pkl`: submission files. Each is a list of lists of 10 integer BBDD IDs, in numerically sorted query order.
- `best_methods.png`, `qst1_preview.png`: qualitative plots.

CLAHE-LAB + L1 gives the best MAP@5 (0.6872), with MAP@1 = 0.6333.

## Week 2 (`week2/C1_week2.ipynb`)

1. 3D/2D, block and hierarchical (pyramid) histograms.
2. Evaluate the best descriptor on QSD1 and compare it with week 1.
3. Background removal using only colour on QSD2 (per-channel thresholds, Euclidean distance, Euclidean distance with a dark-pixel rule, and morphological post-processing).
4. Evaluate background removal with a grid search, plus qualitative worst and best cases.

Outputs in `week2/results/`:

- `grid_search_w2_full.csv`, `grid_search_results_w2.csv`: block/pyramid histogram grid search.
- `comparison_w1_vs_w2.csv`: best week 1 method vs best week 2 method.
- `bg_removal_grid_search.csv`, `bg_removal_best_per_method.csv`: background removal metrics.
- `bg_removal_worst_best.png`: qualitative masks.

Retrieval: the best week 2 descriptor is a block 8x8 YCrCb 2D histogram (16 bins) with χ² distance, giving MAP@1 = 0.8333 and MAP@5 = 0.85 on QSD1. That is +0.20 MAP@1 over the week 1 baseline.

Background removal: the best method is Lab, method C (`tau=10, tau2=1.5, rho=0.6`) with fill + largest-connected-component post-processing. It gives P = 0.9655, R = 0.9838 and F1 = 0.9740 (per-image mean), and global F1 = 0.9859.

# Team 2: Museum Painting Retrieval (MCV C1)

Retrieval of museum paintings from the `BBDD` database using colour histogram descriptors, similarity measures, background removal (from week 2 on) and, from week 3 on, noise filtering, texture descriptors and photos with up to two paintings.

**Team:** Adrià Cantarero Carreras · Ivan Martin Campoy · Irene Pumares Benaiges · Lavish Ramchandani

## Repository structure

```
Team-2/
├── week1/
│   ├── C1_week1.ipynb        # global descriptors, distances, QSD1 evaluation, QST1 predictions
│   ├── data/                 # BBDD/, qsd1_w1/, qst1_w1/  (not tracked)
│   └── results/
├── week2/
│   ├── C1_week2.ipynb        # block/pyramid histograms, background removal, QSD2 retrieval, QST1/QST2 predictions
│   ├── data/                 # BBDD/, qsd1_w1/, qsd2_w1/, qst_w2/  (not tracked)
│   └── results/
├── week3/
│   ├── C1_week3.ipynb        # noise filtering, texture descriptors, up to two paintings per photo, QST1/QST2 predictions
│   ├── data/                 # BBDD/, qsd1_w3/, qsd2_w3/, qst_w3/  (not tracked)
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

The same requirements cover weeks 1 to 3: no new packages were added in week 3.

Datasets are **not** in the repository (`data/` is git-ignored). Download them from the Virtual Campus and place them in each week's `data/` folder:

| Week | Needed in `weekN/data/` |
|------|-------------------------|
| 1 | `BBDD/`, `qsd1_w1/`, `qst1_w1/` |
| 2 | `BBDD/`, `qsd1_w1/`, `qsd2_w1/`, `qst_w2/qst1_w2/`, `qst_w2/qst2_w2/` |
| 3 | `BBDD/`, `qsd1_w3/`, `qsd2_w3/`, `qst_w3/qst1_w3/`, `qst_w3/qst2_w3/` |

Week 2 layout (the notebook reads exactly these paths):

```
week2/data/
├── BBDD/                 # bbdd_00000.jpg ... (+ .png, .txt, relationships.pkl)
├── qsd1_w1/              # QSD1-W2 = QSD1-W1: 30 cropped queries + gt_corresps.pkl
├── qsd2_w1/              # QSD2-W2: 30 photos with background + GT masks (.png) + gt_corresps.pkl, frames.pkl
└── qst_w2/               # test sets (no ground truth)
    ├── qst1_w2/          # QST1-W2: 30 cropped queries, 00000.jpg ... 00029.jpg
    └── qst2_w2/          # QST2-W2: 30 photos with background, 00000.jpg ... 00029.jpg
```



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
5. Retrieval on QSD2 after background removal: compare describing the whole photo (`full`), the painting pixels only (`masked`), the bounding box of the mask (`crop`) and the box without the wall pixels inside it (`crop+mask`), with our masks and with the GT masks.
6. Blind submission: top 10 BBDD IDs for every QST1 and QST2 query with the two best methods, plus our QST2 masks. Nothing is tuned on the test sets.

Outputs in `week2/results/`:

- `grid_search_w2_full.csv`, `grid_search_results_w2.csv`: block/pyramid histogram grid search.
- `comparison_w1_vs_w2.csv`: best week 1 method vs best week 2 method.
- `bg_removal_grid_search.csv`, `bg_removal_best_per_method.csv`: background removal metrics.
- `bg_removal_worst_best.png`: qualitative masks.
- `QSD2/result.pkl`, `qsd2_retrieval_failures.png`: QSD2 correspondences with the selected method, and the queries with a wrong top-1.
- `QST1/method1/result.pkl`, `QST1/method2/result.pkl`: QST1 submission files.
- `QST2/method1/`, `QST2/method2/`: QST2 submission files, each with `result.pkl` and one binary mask (0/255) per query, with the same name as the query and `.png` extension (`00000.jpg` → `00000.png`). Both methods use the same masks.
- `qst1_top1.png`, `qst2_masks_top1.png`: visual checks of the test predictions (query, mask, crop and top-1 BBDD image).

Every `result.pkl` is a list of lists of 10 integer BBDD IDs, in numerically sorted query order.

Retrieval: the best week 2 descriptor is a block 8x8 YCrCb 2D histogram (16 bins) with χ² distance, giving MAP@1 = 0.8333 and MAP@5 = 0.85 on QSD1. That is +0.20 MAP@1 over the week 1 baseline.

Background removal: the best method is Lab, method C (`tau=10, tau2=1.5, rho=0.6`) with fill + largest-connected-component post-processing. It gives P = 0.9655, R = 0.9838 and F1 = 0.9740 (per-image mean), and global F1 = 0.9859.

QSD2 retrieval: with our masks, cropping to the bounding box of the painting (`crop`) gives MAP@1 = 0.70 and MAP@5 = 0.733, against 0.233 for the whole photo and 0.433 for `masked`. The GT masks give the same MAP@1, so the descriptor, not the background removal, limits the result.

Submitted methods (QST1 and QST2):

| Method | Descriptor | Distance | QSD1 MAP@1 / @5 | QSD2 MAP@1 / @5 |
|--------|------------|----------|-----------------|-----------------|
| method1 | Block 8x8, YCrCb 2D, 16 bins | χ² | 0.833 / 0.850 | 0.700 / 0.733 |
| method2 | Block 8x8, LAB 2D, 16 bins | Jensen–Shannon | 0.800 / 0.834 | 0.600 / 0.636 |

method2 is the best configuration of the second-best descriptor in the grid search. On QST2, both methods use our masks and the `crop` mode.

## Week 3 (`week3/C1_week3.ipynb`)

Week 3 layout (unzip the three archives into `week3/data/` and copy `BBDD/` there):

```
week3/data/
├── BBDD/                 # bbdd_00000.jpg ... (+ .png, .txt, relationships.pkl)
├── qsd1_w3/              # QSD1-W3: 30 cropped queries, some noisy, some with hue changes + non_augmented/, gt_corresps.pkl, augmentations.pkl
├── qsd2_w3/              # QSD2-W3: 30 photos with up to two paintings + GT masks (.png), non_augmented/, gt_corresps.pkl, frames.pkl, augmentations.pkl
└── qst_w3/               # test sets (no ground truth)
    ├── qst1_w3/          # QST1-W3: 50 cropped queries
    └── qst2_w3/          # QST2-W3: 30 photos with up to two paintings
```

1. **Noise filtering.** Detect noisy photos (isolated-pixel and σ detectors), then compare 10 linear, non-linear and morphological filters with PSNR / SSIM against the clean versions. Only the photos detected as noisy are filtered.
2. **Texture descriptors.** Block DCT (zig-zag, first N coefficients) and block multiscale LBP, with a grid search on QSD1-W3 using only texture.
3. **Up to two paintings per photo.** The Week 2 background removal, after denoising, keeps up to two regions (each at least 5% of the photo) instead of the largest one, sorted left to right. Evaluated with pixel P / R / F1 on QSD2-W3.
4. **Retrieval on QSD2-W3.** Each detected painting is cropped and described with LBP. The result has one more list level: one list of 10 BBDD ids per painting.
5. **Blind submission.** QST1 and QST2 with one method (`method1`), plus our QST2 masks. This week only the best method is submitted for each test set, and nothing is tuned on the test sets.

Outputs in `week3/results/`:

- `task1_*`: noise detector scores, filter comparison (`task1_filters_psnr_ssim.csv`) and examples.
- `task2_dct_*`, `task2_lbp_*`: grid searches, results by type of query and examples.
- `task3_background_removal.csv`, `task3_w2_vs_w3.png`: Week 2 vs Week 3 masks on QSD2-W3.
- `task4_descriptors.csv`, `task4_error_sources.csv`, `task4_failures.png`: descriptor choice, error analysis and wrong top-1 cases.
- `QSD2/result.pkl`: QSD2-W3 correspondences with the selected method.
- `QST1/method1/result.pkl`, `QST2/method1/result.pkl`: submission files. Each is a list with one entry per photo, and each entry is a list with one list of 10 integer BBDD ids per painting (QST1 always has one painting per photo).
- `QST2/method1/*.png`: one binary mask (0/255) per photo with all its paintings, named like the photo.
- `task5_qst2_masks.png`: visual check of the QST2 masks and top-1 results.

Noise: the detector finds 7/7 noisy queries in QSD1-W3 with no false positives. The best filter is the median 3x3 (PSNR 30.78 dB, SSIM 0.797, against 23.73 dB / 0.488 without filtering).

Texture (QSD1-W3): the best DCT is a 4x4 grid with 21 coefficients and L1 distance (MAP@1 = 0.933). The best LBP is an 8x8 grid with radii 1 and 2 and L1 distance (MAP@1 = MAP@5 = 1.000).

Background removal (QSD2-W3):

| Method | Precision | Recall | F1 | Right painting count |
|--------|-----------|--------|----|----------------------|
| Week 2 | 0.969 | 0.853 | 0.893 | 21/30 |
| Week 3 | 0.968 | 0.969 | 0.967 | 29/30 |

Retrieval (QSD2-W3, 39 paintings): LBP 8x8 with radii 1, 2 and 3 and L1 distance gives MAP@1 = 0.821 and MAP@5 = 0.827. It also scores 1.000 on QSD1-W3, and it is the submitted method for QST1 and QST2. With ground-truth masks MAP@1 is 0.897, and with the clean photos 0.974, so residual noise is the main limit.

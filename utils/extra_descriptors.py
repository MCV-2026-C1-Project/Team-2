import cv2
import numpy as np

# all descriptors take a BGR image (cv2.imread) and return a 1D, L1-normalized np.array


def _normalize(h):
    h = np.asarray(h, dtype=np.float64)
    s = h.sum()
    return h / s if s > 0 else h


# ---------------------------------------------------------------------------
# 1. Chroma-only histogram: drop the luminance/value channel
# ---------------------------------------------------------------------------
CHROMA = {
    #  color space: (cv2 code, channels kept, channel ranges)
    "HSV":   (cv2.COLOR_BGR2HSV,   [0, 1], [(0, 180), (0, 256)]),   # H + S
    "LAB":   (cv2.COLOR_BGR2LAB,   [1, 2], [(0, 256), (0, 256)]),   # a + b
    "YCRCB": (cv2.COLOR_BGR2YCrCb, [1, 2], [(0, 256), (0, 256)]),   # Cr + Cb
}

def hist_chroma(image, color_space="LAB", bins=32):
    code, chans, ranges = CHROMA[color_space]
    img = cv2.cvtColor(image, code)
    hists = [cv2.calcHist([img], [c], None, [bins], list(r)).flatten()
             for c, r in zip(chans, ranges)]
    return _normalize(np.concatenate(hists))


# ---------------------------------------------------------------------------
# 2. CLAHE on the lightness channel + LAB histogram
# ---------------------------------------------------------------------------
def hist_clahe_lab(image, bins=32, clip=2.0, tile=8):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
    lab[..., 0] = clahe.apply(lab[..., 0])  # equalize only L, keep a/b untouched
    hists = [cv2.calcHist([lab], [c], None, [bins], [0, 256]).flatten() for c in range(3)]
    return _normalize(np.concatenate(hists))


# ---------------------------------------------------------------------------
# 3. Saturation-weighted hue histogram
# ---------------------------------------------------------------------------
def hist_hue_weighted(image, bins=36):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue = hsv[..., 0].ravel().astype(np.float32)
    sat = hsv[..., 1].ravel().astype(np.float32) / 255.0  # weight in [0, 1]
    h, _ = np.histogram(hue, bins=bins, range=(0, 180), weights=sat)  # grey pixels barely count
    return _normalize(h)


# ---------------------------------------------------------------------------
# 4. Gradient orientation histogram (global, magnitude-weighted)
# ---------------------------------------------------------------------------
def hist_gradient_orientation(image, bins=18, size=256):
    gray = cv2.cvtColor(cv2.resize(image, (size, size)), cv2.COLOR_BGR2GRAY).astype(np.float32)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)  # small blur to reduce sensor noise
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.hypot(gx, gy)
    ang = np.mod(np.arctan2(gy, gx), np.pi)  # unsigned orientation in [0, pi)
    h, _ = np.histogram(ang, bins=bins, range=(0, np.pi), weights=mag)
    return _normalize(h)


# ---------------------------------------------------------------------------
# 5. Global LBP histogram (256 patterns, 8 neighbours, radius 1)
# ---------------------------------------------------------------------------
def hist_lbp(image, size=256):
    gray = cv2.cvtColor(cv2.resize(image, (size, size)), cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    center = gray[1:-1, 1:-1]
    code = np.zeros(center.shape, dtype=np.uint8)
    offsets = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
    for bit, (dy, dx) in enumerate(offsets):
        neigh = gray[1 + dy:h - 1 + dy, 1 + dx:w - 1 + dx]
        code |= ((neigh >= center).astype(np.uint8) << bit)  # 1 bit per neighbour
    return _normalize(np.bincount(code.ravel(), minlength=256))


# ---------------------------------------------------------------------------
# Fusion: weighted concatenation of several descriptors
# ---------------------------------------------------------------------------
def concat_descriptors(descs, weights=None):
    # descs: list of 1D arrays (each sums to 1); result sums to 1 again
    weights = np.ones(len(descs)) if weights is None else np.asarray(weights, dtype=np.float64)
    return _normalize(np.concatenate([w * d for w, d in zip(weights, descs)]))


# ---------------------------------------------------------------------------
# Retrieval + evaluation helpers (use your MEASURES dict and kdd_mapk)
# ---------------------------------------------------------------------------
def retrieve_topk(query_descs, db_descs, db_ids, measure, k=10, **kwargs):
    results = []
    for q in query_descs:
        dists = measure(q, db_descs, **kwargs)
        idx = np.argsort(dists)[:k]  # smallest distance = most similar
        results.append([int(i) for i in db_ids[idx]])  # plain python ints for the .pkl
    return results


def evaluate_descriptor(desc_fn, bbdd_imgs, qsd1_imgs, bbdd_ids, gt, measures, mapk, emd_bins=None):
    # returns a list of (measure, mAP@1, mAP@5); emd only if the hist is made of equal blocks of emd_bins
    db = np.array([desc_fn(im) for im in bbdd_imgs])
    qs = np.array([desc_fn(im) for im in qsd1_imgs])
    rows = []
    for name, measure in measures.items():
        kwargs = {}
        if name == "emd":
            if emd_bins is None:
                continue
            kwargs["bins"] = emd_bins
        preds = retrieve_topk(qs, db, bbdd_ids, measure, k=5, **kwargs)
        rows.append((name, mapk(gt, preds, k=1), mapk(gt, preds, k=5)))
    return sorted(rows, key=lambda r: -r[2])


def save_results(preds, path):
    # preds: list of lists of int ids, K=10 per query (QST1 format)
    import os, pickle
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(preds, f)

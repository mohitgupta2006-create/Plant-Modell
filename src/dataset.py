"""Dataset: joins splits.csv + env.csv + severity.csv; builds and saves label maps; image transforms.
Train transform has augmentation; val/test: deterministic resize + ImageNet normalisation only."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms as T

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DATA_PROCESSED, IMG_SIZE, MODELS, ROOT  # noqa: E402
from model import CAUSE, CROPS, HEALTH, IGNORE, SEVERITY  # noqa: E402

MEAN, STD = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
CACHE_SIZE = 256
CACHE_DIR = DATA_PROCESSED / "cache256"


def cache_path(rel_path: str) -> Path:
    import hashlib
    return CACHE_DIR / (hashlib.md5(rel_path.encode("utf-8")).hexdigest()[:16] + ".jpg")


def load_rgb_256(path) -> Image.Image:
    """Canonical pre-processing used for caching AND by predict.py: RGB, resized to 256x256 (aspect not preserved)."""
    with Image.open(path) as im:
        return im.convert("RGB").resize((CACHE_SIZE, CACHE_SIZE), Image.BICUBIC)


def build_table(research=False, variant="image"):
    if research:
        return build_research_table(variant)
    sp = pd.read_csv(DATA_PROCESSED / "splits.csv")
    env = pd.read_csv(DATA_PROCESSED / "env.csv")
    sev = pd.read_csv(DATA_PROCESSED / "severity.csv")[["path", "severity", "severity_valid"]]
    df = sp.merge(env, on="path", how="left", validate="1:1").merge(sev, on="path", how="left", validate="1:1")
    df["cause"] = df["cause"].fillna("None")  # healthy leaves carry the label 'None'; pandas reads that string as NaN
    conditions = sorted(df["condition"].unique())
    trained_causes = sorted(df[(df["split"] == "train") & (df["health"] == "Unhealthy")]["cause"].unique())
    maps = {"crop": CROPS, "health": HEALTH, "cause": CAUSE, "severity": SEVERITY, "condition": conditions,
            "env_features": ["temperature", "rainfall", "humidity", "soil_moisture"],
            # cause classes that have >= 1 training example (Abiotic has none: no abiotic data were obtained)
            "cause_trained_classes": trained_causes}
    return df, maps


def build_research_table(variant="image"):
    from research_inputs import FEATURES, paired_environment, split_audit
    from class_meta import CONDITION_META
    sp = pd.read_csv(DATA_PROCESSED / "splits.csv", keep_default_na=False)
    split_audit(sp.to_dict("records"))
    conditions = sorted(sp.loc[sp["split"] == "train", "condition"].unique())
    if set(sp["condition"]) - set(conditions):
        raise ValueError("validation/test condition absent from training")
    unknown = set(conditions) - set(CONDITION_META) - {"Tomato___N_Deficiency", "Tomato___NK_Deficiency"}
    if unknown:
        raise ValueError(f"unknown condition metadata: {unknown}")
    if variant != "image":
        env = pd.read_csv(DATA_PROCESSED / "env_real.csv", keep_default_na=False)
        matched = paired_environment(sp.to_dict("records"), env.to_dict("records"))
        sp = sp.merge(pd.DataFrame(matched)[["path"] + FEATURES], on="path", validate="1:1")
        tr = sp.loc[sp["split"] == "train", FEATURES].astype(float)
        stats = {"mean": tr.mean().tolist(), "std": tr.std(ddof=0).replace(0, 1).tolist(),
                 "features": FEATURES, "method": "real exact image/location/date pairing; train-only fit"}
    else:
        for k in FEATURES:
            sp[k] = 0.0  # unused placeholders, never measurements
        stats = {"mean": [0.] * 4, "std": [1.] * 4, "features": FEATURES, "method": "not_used"}
    sp["severity"], sp["severity_valid"] = "", False
    causes = sorted(sp.loc[(sp["split"] == "train") & (sp["health"] == "Unhealthy"), "cause"].unique())
    # A one-class cause target is not a disease-versus-deficiency experiment.
    sp["cause_valid"] = sp["health"].eq("Unhealthy") & (set(causes) == {"Biotic", "Abiotic"})
    meta = {c: list(CONDITION_META[c]) if c in CONDITION_META else ["Tomato", False] for c in conditions}
    maps = {"crop": CROPS, "health": HEALTH, "cause": CAUSE, "severity": SEVERITY,
            "condition": conditions, "condition_meta": meta, "env_features": FEATURES,
            "cause_trained_classes": causes, "severity_trained": False,
            "research_env_stats": stats, "research_protocol": "reviewer_revision_v1", "decoder": "cause_first"}
    if not (sp["split"] == "train").any() or not (sp["split"] == "val").any():
        raise ValueError("training and validation samples required")
    return sp, maps


def save_label_maps(maps):
    MODELS.mkdir(exist_ok=True)
    json.dump(maps, open(MODELS / "label_maps.json", "w"), indent=2)


def make_transform(train, size=IMG_SIZE):
    if not train:
        return T.Compose([T.Resize((size, size)), T.ToTensor(), T.Normalize(MEAN, STD)])
    return T.Compose([
        T.RandomResizedCrop(size, scale=(0.6, 1.0)), T.RandomHorizontalFlip(), T.RandomVerticalFlip(),
        T.RandomRotation(25), T.ColorJitter(0.2, 0.2, 0.2, 0.02),
        T.RandomApply([T.GaussianBlur(3, (0.1, 1.5))], p=0.15), T.ToTensor(), T.Normalize(MEAN, STD)])


class LeafDataset(Dataset):
    def __init__(self, df, maps, env_stats, train, size=IMG_SIZE, env_override=None, load_image=True):
        self.load_image = load_image  # False for the env-only variant: skip image decoding entirely
        self.df = df.reset_index(drop=True)
        self.tf = make_transform(train, size)
        ci = {k: i for i, k in enumerate(maps["condition"])}
        mu, sd = np.array(env_stats["mean"]), np.array(env_stats["std"])
        env = ((self.df[maps["env_features"]].values - mu) / sd).astype(np.float32)
        self.env = env if env_override is None else env_override.astype(np.float32)
        d = self.df
        unh = (d["health"] == "Unhealthy").values
        cause_ok = unh & d.get("cause_valid", pd.Series(True, index=d.index)).astype(bool).values
        self.y = {
            "crop": d["crop"].map({k: i for i, k in enumerate(CROPS)}).values,
            "health": d["health"].map({"Healthy": 0, "Unhealthy": 1}).values,
            "cause": np.where(cause_ok, d["cause"].map({"Biotic": 0, "Abiotic": 1}).fillna(IGNORE), IGNORE).astype(int),
            "condition": d["condition"].map(ci).values,
            "severity": np.where(unh & (d["severity_valid"].fillna(False).astype(bool)),
                                 d["severity"].map({"Mild": 0, "Moderate": 1, "Severe": 2}).fillna(IGNORE), IGNORE).astype(int),
        }

    def __len__(self):
        return len(self.df)

    def __getitem__(self, i):
        rel = self.df.loc[i, "path"]
        if not self.load_image:
            x = torch.zeros(1)
        else:
            cp = cache_path(rel)
            if cp.exists():
                with Image.open(cp) as im:
                    x = self.tf(im.convert("RGB"))
            else:  # identical canonical preprocessing, just slower
                x = self.tf(load_rgb_256(ROOT / rel))
        item = {"image": x, "env": torch.from_numpy(self.env[i])}
        item.update({k: torch.tensor(int(v), dtype=torch.long) for k, v in ((k, self.y[k][i]) for k in self.y)})
        return item

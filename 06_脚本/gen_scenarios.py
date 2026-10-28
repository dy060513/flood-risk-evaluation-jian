# -*- coding: utf-8 -*-
"""gen_scenarios.py —— 5 档重现期水位场景风险分级"""
import json, numpy as np, rasterio
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

BASE = Path(__file__).parent.parent
H_DIR = BASE / "02_中间成果" / "危险性"
E_DIR = BASE / "02_中间成果" / "暴露度"
V_DIR = BASE / "02_中间成果" / "易损性"
ASSETS = BASE / "06_脚本" / "assets"

W_WARN, W_GUAR = 99.0, 101.45
LEVELS = [("w1",99.00,"10年一遇·警戒"),("w2",100.50,"20年一遇·9·4实际"),
          ("w3",101.45,"30年一遇·保证"),("w4",102.50,"50年一遇·推算"),
          ("w5",103.80,"100年一遇·推算")]
CMAP = ['#abd9e9','#ffffbf','#fdae61','#d7191c']

def load(p):
    with rasterio.open(p) as s: return s.read(1).astype(float), s.transform, s.crs

def export_png(cls, tf, tag):
    dst = np.ma.masked_where(cls <= 1, cls)
    cmap = ListedColormap(CMAP); cmap.set_bad(alpha=0)
    norm = BoundaryNorm([1.5,2.5,3.5,4.5,5.5], 4)
    h, w = cls.shape
    fig, ax = plt.subplots(figsize=(w/100, h/100), dpi=100)
    ax.imshow(dst, cmap=cmap, norm=norm); ax.axis("off")
    fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
    fig.savefig(ASSETS/f"risk_{tag}_class5.png", transparent=True); plt.close(fig)
    bounds = {"west":tf.c,"south":tf.f+h*tf.e,"east":tf.c+w*tf.a,"north":tf.f}
    (ASSETS/f"risk_{tag}_bounds.json").write_text(json.dumps(bounds))

def stats_of(cls):
    out = {"等级":{}}
    names = {1:"极低",2:"低",3:"中",4:"高",5:"极高"}
    for lv in range(1,6):
        n = int(np.sum(cls==lv))
        out["等级"][f"{lv}-{names[lv]}"] = {"面积km2":round(n*900/1e6,1)}
    return out

def main():
    h_warn, tf, _ = load(H_DIR/"H_warning_depth.tif")
    h_guar, _, _ = load(H_DIR/"H_guarantee_depth.tif")
    E, _, _ = load(E_DIR/"E_exposure.tif")
    V, _, _ = load(V_DIR/"V_loss.tif")
    all_stats = {}
    for tag, w, label in LEVELS:
        t = (w-W_WARN)/(W_GUAR-W_WARN)
        h = np.where(h_warn + t*(h_guar-h_warn) > 0, h_warn+t*(h_guar-h_warn), 0)
        risk = np.clip(h/3.0,0,1) * E * V
        cls = np.zeros_like(risk, dtype=np.uint8)
        pos = risk > 0
        if pos.sum() > 100:
            q = np.quantile(risk[pos], [0.2,0.4,0.6,0.8])
            cls = np.where(risk<=0,0,np.where(risk<=q[0],1,np.where(risk<=q[1],2,np.where(risk<=q[2],3,np.where(risk<=q[3],4,5))))).astype(np.uint8)
        export_png(cls, tf, tag)
        st = stats_of(cls)
        st["最高水深m"] = round(float(h.max()),1)
        st["水位m"] = w; st["水位标签"] = label
        all_stats[tag] = st
    (ASSETS/"scenarios.json").write_text(json.dumps(all_stats, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__": main()

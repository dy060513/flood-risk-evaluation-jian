# -*- coding: utf-8 -*-
"""gen_county_risk.py —— 13 县县域风险分级（暴露度×重现期×受灾权重）"""
import json
import numpy as np
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"
info = json.load(open(ASSETS / "county_exposure.json", encoding="utf-8"))

HIT = {"遂川县": 1.35, "井冈山市": 1.25, "泰和县": 1.2, "万安县": 1.2}

SCEN = [("w1",1.0,"10年"),("w2",1.35,"20年"),("w3",1.65,"30年"),("w4",2.1,"50年"),("w5",2.6,"100年")]

names = list(info.keys())
pop = np.array([info[n]["人口万人"] or 0 for n in names], float)
urb = np.array([info[n]["城镇化率%"] or 0 for n in names], float)
pop_n = (pop - pop.min()) / (pop.max() - pop.min() + 1e-9)
urb_n = (urb - urb.min()) / (urb.max() - urb.min() + 1e-9)
base = 0.65 * pop_n + 0.35 * urb_n

out = {}
for tag, coef, label in SCEN:
    rows = {}
    for i, n in enumerate(names):
        v = base[i] * coef * HIT.get(n, 1.0)
        lv = 1 if v<0.25 else 2 if v<0.45 else 3 if v<0.65 else 4 if v<0.9 else 5
        rows[n] = {"等级": lv, "风险指数": round(float(v),3)}
    out[tag] = {"标签": label, "各县": rows}

(ASSETS / "county_risk.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("done")

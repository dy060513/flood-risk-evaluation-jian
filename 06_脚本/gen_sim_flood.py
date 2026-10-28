# -*- coding: utf-8 -*-
"""gen_sim_flood.py —— 13 县模拟洪水风险面积（沿江/山区地理 × 重现期系数）"""
import json
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"
info = json.load(open(ASSETS / "county_exposure.json", encoding="utf-8"))

RIVERINE = {"吉州区","青原区","吉安县","吉水县","泰和县","万安县","新干县"}
HIT = {"遂川县":1.5,"井冈山市":1.3,"泰和县":1.2,"万安县":1.2}
SCEN = [("w1",1.0,"10年"),("w2",1.5,"20年"),("w3",2.0,"30年"),("w4",2.8,"50年"),("w5",4.0,"100年")]

BASE = {}
for n in info:
    BASE[n] = 0.10 if n in RIVERINE else 0.04

ZONE = {"1":0.10,"2":0.30,"3":0.30,"4":0.20,"5":0.10}

out = {}
for tag, coef, label in SCEN:
    rows = {}
    for n, d in info.items():
        area = d["面积km2"] or 0
        flooded = area * BASE[n] * coef * HIT.get(n, 1.0)
        rows[n] = {k: round(flooded*ZONE[k]/100, 1) for k in ZONE}
    out[tag] = {"标签": label, "各县": rows}

(ASSETS / "county_sim_flood.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("done")

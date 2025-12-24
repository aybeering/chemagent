# HOMO_00_index — 氧化倾向定性评估 Skill 注册表

| Field | Value |
|---|---|
| Registry | HOMO OxTendency Prompt Skills |
| Schema | `HOMO_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Count | 6 |

本注册表用于索引"氧化倾向定性评估（HOMO 趋势直觉）"相关的 Prompt Skills。  
每张卡片基于 HOMO 能级趋势，定性评估分子/位点的氧化敏感性，服务于电解液氧化稳定性分析。

**核心假设**：HOMO 能级越高 → 越易被氧化

---

## 1. 全量清单（按 Skill ID）

| Skill ID | 中文名 | 功能简述 | 关键词 | File |
|---|---|---|---|---|
| `HOMO_01_ox_flowmap_v1` | 氧化倾向总路由 | 识别位点、分发子卡、汇总优先级排序 | `routing, ox-ranking, pipeline` | [HOMO_01_ox_flowmap_v1.md](HOMO_01_ox_flowmap_v1.md) |
| `HOMO_02_lonepair_n_v1` | 杂原子孤对 (n 轨道) | N/O/S/P 的孤对电子 HOMO 贡献 | `lonepair, n-orbital, heteroatom` | [HOMO_02_lonepair_n_v1.md](HOMO_02_lonepair_n_v1.md) |
| `HOMO_03_pi_system_v1` | π 系统氧化倾向 | 芳环、烯烃、共轭体系的 π HOMO | `pi, aromatic, alkene, conjugation` | [HOMO_03_pi_system_v1.md](HOMO_03_pi_system_v1.md) |
| `HOMO_04_activated_CH_v1` | 活化 C-H 键 | 苄位/烯丙位/α-杂原子的 σ(C-H) | `C-H, benzylic, allylic, alpha-hetero` | [HOMO_04_activated_CH_v1.md](HOMO_04_activated_CH_v1.md) |
| `HOMO_05_substituent_mod_v1` | 取代基调制 | 调用 ELEC skills，评估取代基对 HOMO 的升降 | `substituent, ELEC-integration, modulation` | [HOMO_05_substituent_mod_v1.md](HOMO_05_substituent_mod_v1.md) |
| `HOMO_06_interface_effect_v1` | 界面/电场修正 | 电解液界面环境下的氧化行为修正 | `interface, electric-field, electrode` | [HOMO_06_interface_effect_v1.md](HOMO_06_interface_effect_v1.md) |

---

## 2. 建议调用顺序（Pipeline）

```
1. HOMO_01_ox_flowmap_v1（总路由）
   │
   ├─► 2. HOMO_02_lonepair_n_v1（杂原子孤对）
   │       └─► HOMO_05_substituent_mod_v1（取代基调制）
   │               └─► [ELEC_01_effect_flowmap_v1]
   │
   ├─► 3. HOMO_03_pi_system_v1（π 系统）
   │       └─► HOMO_05_substituent_mod_v1（取代基调制）
   │               └─► [ELEC_01_effect_flowmap_v1]
   │
   ├─► 4. HOMO_04_activated_CH_v1（活化 C-H）
   │       └─► HOMO_05_substituent_mod_v1（取代基调制）
   │               └─► [ELEC_04_hyperconj_v1]
   │
   ├─► 5. HOMO_06_interface_effect_v1（界面修正）
   │
   └─► 6. 返回 HOMO_01 做最终汇总与位点排序
```

---

## 3. 按 HOMO 贡献类型索引

### n 轨道（孤对电子）
- `HOMO_02_lonepair_n_v1` — [杂原子孤对](HOMO_02_lonepair_n_v1.md)

### π 轨道
- `HOMO_03_pi_system_v1` — [π 系统氧化倾向](HOMO_03_pi_system_v1.md)

### σ 轨道（活化 C-H）
- `HOMO_04_activated_CH_v1` — [活化 C-H 键](HOMO_04_activated_CH_v1.md)

### 调制与修正
- `HOMO_05_substituent_mod_v1` — [取代基调制](HOMO_05_substituent_mod_v1.md)
- `HOMO_06_interface_effect_v1` — [界面/电场修正](HOMO_06_interface_effect_v1.md)

### 总路由
- `HOMO_01_ox_flowmap_v1` — [氧化倾向总路由](HOMO_01_ox_flowmap_v1.md)

---

## 4. 检索标签（Tag → Skill）

| 标签 | Skill ID |
|---|---|
| `孤对` / `n轨道` / `胺` / `醚` / `硫醚` | HOMO_02_lonepair_n_v1 |
| `芳环` / `烯烃` / `共轭` / `π系统` | HOMO_03_pi_system_v1 |
| `苄位` / `烯丙位` / `α-杂原子` / `C-H活化` | HOMO_04_activated_CH_v1 |
| `取代基` / `电子效应` / `HOMO升降` | HOMO_05_substituent_mod_v1 |
| `界面` / `电场` / `正极` / `吸附` | HOMO_06_interface_effect_v1 |
| `氧化排序` / `综合判定` / `HOMO总评` | HOMO_01_ox_flowmap_v1 |

---

## 5. 易混淆索引（用于路由与消歧）

| Skill | 易混淆 Skill | 消歧说明 |
|---|---|---|
| `HOMO_02_lonepair_n_v1` | `HOMO_03_pi_system_v1` | 含 N/O 的芳环：需分别评估孤对与 π 系统贡献 |
| `HOMO_03_pi_system_v1` | `HOMO_04_activated_CH_v1` | 苄位/烯丙位：π 系统稳定自由基，C-H 键提供初始 HOMO |
| `HOMO_05_substituent_mod_v1` | `ELEC_01_effect_flowmap_v1` | HOMO_05 是调用入口，ELEC_01 提供电子效应数据 |

---

## 6. 依赖关系

```
HOMO_01_ox_flowmap_v1
    ├── depends_on: [HOMO_02, HOMO_03, HOMO_04, HOMO_05, HOMO_06]
    └── 作为总路由调用所有子技能卡

HOMO_02_lonepair_n_v1
    └── may_call: HOMO_05_substituent_mod_v1（取代基调制）

HOMO_03_pi_system_v1
    └── may_call: HOMO_05_substituent_mod_v1（取代基调制）

HOMO_04_activated_CH_v1
    └── may_call: HOMO_05_substituent_mod_v1（取代基调制）

HOMO_05_substituent_mod_v1
    └── depends_on: [ELEC_01_effect_flowmap_v1]（跨模块调用）

HOMO_06_interface_effect_v1
    └── 独立执行，提供环境修正因子
```

---

## 7. 与其他 Skill 模块的联动

| 调用方向 | 联动模块 | 说明 |
|----------|----------|------|
| HOMO → ELEC | `01_ELEC_skills/` | `HOMO_05` 调用 ELEC Pipeline 获取电子效应 |
| HOMO → SITE | `site_skills/SITE_OX_SITE_v1` | 输出的 `ox_sites_ranked` 可供 SITE 使用 |
| 上游 → HOMO | 电化学专家 Agent | 调用 HOMO 模块评估氧化稳定性 |
| HOMO → 04_Oxid&redStability | `04_Oxid&redStability/` | 可进一步做稳定性综合评估 |

---

## 8. 使用建议（编排）

1. **单一位点评估**（如"这个胺氮容易被氧化吗"）：直接调用 `HOMO_02_lonepair_n_v1`。
2. **整体分子氧化倾向**：走完整 Pipeline，从 `HOMO_01_ox_flowmap_v1` 开始。
3. **电解液界面分析**：必须调用 `HOMO_06_interface_effect_v1` 做环境修正。
4. **需要定量数据**：本模块仅输出定性结论；如需氧化电位，需对接计算化学工具。

---

## 9. Changelog

- 2025-12-24: 初始版本，包含 6 个 skill 卡片


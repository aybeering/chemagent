# LUMO_00_index — 还原倾向定性评估 Skill 注册表

| Field | Value |
|---|---|
| Registry | LUMO RedTendency Prompt Skills |
| Schema | `LUMO_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Count | 6 |

本注册表用于索引"还原倾向定性评估（LUMO 趋势直觉）"相关的 Prompt Skills。  
每张卡片基于 LUMO 能级趋势，定性评估分子/位点的还原敏感性，服务于电解液还原稳定性分析。

**核心假设**：LUMO 能级越低 → 越易被还原

---

## 1. 全量清单（按 Skill ID）

| Skill ID | 中文名 | 功能简述 | 关键词 | File |
|---|---|---|---|---|
| `LUMO_01_red_flowmap_v1` | 还原倾向总路由 | 识别位点、分发子卡、汇总优先级排序 | `routing, red-ranking, pipeline` | [LUMO_01_red_flowmap_v1.md](LUMO_01_red_flowmap_v1.md) |
| `LUMO_02_pi_antibond_v1` | π* 反键轨道 | 羰基/腈/硝基/烯烃的 LUMO 贡献 | `pi-star, carbonyl, nitrile, nitro` | [LUMO_02_pi_antibond_v1.md](LUMO_02_pi_antibond_v1.md) |
| `LUMO_03_sigma_antibond_v1` | σ* 反键轨道 | C-X 键（卤素/磺酸酯）的 LUMO 贡献 | `sigma-star, C-X, halide, sulfonate` | [LUMO_03_sigma_antibond_v1.md](LUMO_03_sigma_antibond_v1.md) |
| `LUMO_04_ring_strain_v1` | 环张力/小环 | 环氧/环丙烷等应变体系的还原敏感性 | `ring-strain, epoxide, cyclopropane` | [LUMO_04_ring_strain_v1.md](LUMO_04_ring_strain_v1.md) |
| `LUMO_05_substituent_mod_v1` | 取代基调制 | 调用 ELEC skills 评估对 LUMO 的升降 | `substituent, ELEC-integration, modulation` | [LUMO_05_substituent_mod_v1.md](LUMO_05_substituent_mod_v1.md) |
| `LUMO_06_interface_effect_v1` | 界面/电场修正 | 负极界面环境下的还原行为修正 | `interface, electric-field, anode` | [LUMO_06_interface_effect_v1.md](LUMO_06_interface_effect_v1.md) |

---

## 2. 建议调用顺序（Pipeline）

```
1. LUMO_01_red_flowmap_v1（总路由）
   │
   ├─► 2. LUMO_02_pi_antibond_v1（π* 反键）
   │       └─► LUMO_05_substituent_mod_v1（取代基调制）
   │               └─► [ELEC_01_effect_flowmap_v1]
   │
   ├─► 3. LUMO_03_sigma_antibond_v1（σ* 反键）
   │       └─► LUMO_05_substituent_mod_v1（取代基调制）
   │
   ├─► 4. LUMO_04_ring_strain_v1（环张力）
   │
   ├─► 5. LUMO_06_interface_effect_v1（界面修正）
   │
   └─► 6. 返回 LUMO_01 做最终汇总与位点排序
```

---

## 3. 按 LUMO 贡献类型索引

### π* 反键轨道
- `LUMO_02_pi_antibond_v1` — [π* 反键轨道](LUMO_02_pi_antibond_v1.md)

### σ* 反键轨道
- `LUMO_03_sigma_antibond_v1` — [σ* 反键轨道](LUMO_03_sigma_antibond_v1.md)

### 应变体系
- `LUMO_04_ring_strain_v1` — [环张力/小环](LUMO_04_ring_strain_v1.md)

### 调制与修正
- `LUMO_05_substituent_mod_v1` — [取代基调制](LUMO_05_substituent_mod_v1.md)
- `LUMO_06_interface_effect_v1` — [界面/电场修正](LUMO_06_interface_effect_v1.md)

### 总路由
- `LUMO_01_red_flowmap_v1` — [还原倾向总路由](LUMO_01_red_flowmap_v1.md)

---

## 4. 检索标签（Tag → Skill）

| 标签 | Skill ID |
|---|---|
| `羰基` / `酮` / `醛` / `酯` / `酰胺` | LUMO_02_pi_antibond_v1 |
| `腈` / `硝基` / `烯烃` / `π*` | LUMO_02_pi_antibond_v1 |
| `卤素` / `C-X` / `磺酸酯` / `σ*` | LUMO_03_sigma_antibond_v1 |
| `环氧` / `环丙烷` / `小环` / `张力` | LUMO_04_ring_strain_v1 |
| `取代基` / `电子效应` / `LUMO升降` | LUMO_05_substituent_mod_v1 |
| `界面` / `电场` / `负极` / `锂金属` | LUMO_06_interface_effect_v1 |
| `还原排序` / `综合判定` / `LUMO总评` | LUMO_01_red_flowmap_v1 |

---

## 5. 易混淆索引（用于路由与消歧）

| Skill | 易混淆 Skill | 消歧说明 |
|---|---|---|
| `LUMO_02_pi_antibond_v1` | `LUMO_03_sigma_antibond_v1` | π* 涉及不饱和键，σ* 涉及单键断裂 |
| `LUMO_03_sigma_antibond_v1` | `LUMO_04_ring_strain_v1` | 环氧既有 σ* 特征又有张力，优先用 LUMO_04 |
| `LUMO_05_substituent_mod_v1` | `ELEC_01_effect_flowmap_v1` | LUMO_05 是调用入口，ELEC_01 提供电子效应数据 |

---

## 6. LUMO 基础排序（定性参考）

```
低 LUMO ──────────────────────────────────────────► 高 LUMO
（易还原）                                        （难还原）

硝基 > 醛 > 酮 > 酯 ≈ 环氧 > 酰胺 > 腈 > C-卤素 > 烯烃 > 芳环 > 饱和烷
```

---

## 7. 与其他 Skill 模块的联动

| 调用方向 | 联动模块 | 说明 |
|----------|----------|------|
| LUMO → ELEC | `01_ELEC_skills/` | `LUMO_05` 调用 ELEC Pipeline 获取电子效应 |
| LUMO → INTF | `04_InterfaceFirstStrikeSites_skills/` | 输出供界面优先位点排序使用 |
| LUMO ↔ HOMO | `02_HOMO_OxTendency_Qual_skills/` | 对称模块，可对比使用 |
| 上游 → LUMO | 电化学专家 Agent | 调用 LUMO 模块评估还原稳定性 |

---

## 8. 使用建议（编排）

1. **单一位点评估**（如"这个羰基容易被还原吗"）：直接调用 `LUMO_02_pi_antibond_v1`。
2. **整体分子还原倾向**：走完整 Pipeline，从 `LUMO_01_red_flowmap_v1` 开始。
3. **负极界面分析**：必须调用 `LUMO_06_interface_effect_v1` 做环境修正。
4. **需要定量数据**：本模块仅输出定性结论；如需还原电位，需对接计算化学工具。

---

## 9. Changelog

- 2025-12-24: 初始版本，包含 6 个 skill 卡片


# GAS_00_index — 产气/聚合风险 Skill 注册表

| Field | Value |
|---|---|
| Registry | GAS Prompt Skills |
| Schema | `GAS_CARD_SCHEMA_v1` |
| Created | 2025-12-25 |
| Count | 3 |

本注册表用于索引"产气/失控聚合风险"相关的 Prompt Skills。  
每张卡片是一个 **GAS prompt skill**，用于识别分子结构中的产气风险红旗和失控聚合倾向。

---

## 1. 全量清单（按 Skill ID）

| Skill ID | 中文名 | 功能简述 | 关键词 | File |
|---|---|---|---|---|
| `GAS_01_risk_flowmap_v1` | 产气/聚合风险总路由 | 总装配：整合产气和聚合风险，给出综合安全评估 | `routing, safety-assessment` | [GAS_01_risk_flowmap_v1.md](GAS_01_risk_flowmap_v1.md) |
| `GAS_02_gassing_flags_v1` | 产气风险红旗 | 识别可能产生危险气体的结构特征 | `gassing, CO2, CO, H2, HF` | [GAS_02_gassing_flags_v1.md](GAS_02_gassing_flags_v1.md) |
| `GAS_03_polymer_risk_v1` | 失控聚合风险 | 识别可能导致失控聚合的结构特征 | `polymerization, thermal-runaway` | [GAS_03_polymer_risk_v1.md](GAS_03_polymer_risk_v1.md) |

---

## 2. 建议调用顺序（Pipeline）

```
1. GAS_01_risk_flowmap_v1（总路由与风险整合）
   │
   ├─► 2. GAS_02_gassing_flags_v1（产气风险红旗）
   │
   ├─► 3. GAS_03_polymer_risk_v1（失控聚合风险）
   │
   └─► 4. 返回 GAS_01 做最终风险等级评估
```

---

## 3. 按风险类型索引

### 产气风险
- `GAS_02_gassing_flags_v1` — [产气风险红旗](GAS_02_gassing_flags_v1.md)

### 聚合风险
- `GAS_03_polymer_risk_v1` — [失控聚合风险](GAS_03_polymer_risk_v1.md)

### 总路由
- `GAS_01_risk_flowmap_v1` — [产气/聚合风险总路由](GAS_01_risk_flowmap_v1.md)

---

## 4. 检索标签（Tag → Skill）

| 标签 | Skill ID |
|---|---|
| `产气` / `CO₂` / `CO` / `H₂` / `HF` / `膨胀` | GAS_02_gassing_flags_v1 |
| `聚合` / `失控` / `热失控` / `自由基` / `交联` | GAS_03_polymer_risk_v1 |
| `安全` / `风险评估` / `综合` | GAS_01_risk_flowmap_v1 |

---

## 5. 易混淆索引（用于路由与消歧）

| Skill | 易混淆 Skill | 消歧说明 |
|---|---|---|
| `GAS_02_gassing_flags_v1` | `CEI_03_side_reaction_v1` | GAS_02 聚焦产气；CEI_03 是氧化副反应 |
| `GAS_03_polymer_risk_v1` | `SEI_02_polymer_film_v1` | GAS_03 是失控风险；SEI_02 是受控成膜 |

---

## 6. 依赖关系

```
GAS_01_risk_flowmap_v1
    ├── depends_on: [GAS_02, GAS_03]
    └── 作为总路由调用所有子技能卡

GAS_02/03
    └── 依赖上游 OrganicChem 和 PhysChem 输出
```

---

## 7. 使用建议（编排）

1. **单一问题**（如"有产气风险吗？"）：可直接调用 `GAS_02_gassing_flags_v1`。
2. **完整安全评估**：走完整 Pipeline，从 `GAS_01_risk_flowmap_v1` 开始。
3. **新型添加剂筛选**：优先调用本模块评估安全性。
4. **与其他模块联合**：结合 ROLE、SEI、CEI 进行综合评估。

---

## 8. 与其他 Skill 模块的联动

| 场景 | 联动模块 |
|---|---|
| 评估 SEI 形成产气 | → `02_SEIPathway_skills/SEI_*` |
| 评估氧化副反应产气 | → `03_CEIRisk_skills/CEI_03` |
| 需要结构解析 | → `OrganicChem/` |
| 需要反应位点 | → `OrganicChem/RH_*` |

---

## 9. 安全风险背景知识

### 电池产气来源
| 来源 | 典型气体 | 条件 |
|-----|---------|------|
| 电解液还原分解 | CO₂, C₂H₄, CO | 负极 SEI 形成 |
| 电解液氧化分解 | CO₂, CO | 高压正极 |
| 水分反应 | H₂, HF | 痕量水 + LiPF₆ |
| 添加剂分解 | 多种 | 特定添加剂 |

### 产气后果
| 后果 | 严重程度 | 描述 |
|-----|---------|------|
| 电池膨胀 | 中 | 内压升高 |
| 安全阀开启 | 中-高 | 电解液泄漏 |
| 热失控 | 极高 | 连锁反应 |

### 失控聚合风险
| 类型 | 触发 | 后果 |
|-----|------|------|
| 自由基链式聚合 | 电子转移/热 | 放热、粘度飙升 |
| 交联 | 多官能团单体 | 凝胶化 |
| 热失控 | 聚合放热累积 | 温度飙升、分解 |


# CEI_00_index — CEI 风险 Skill 注册表

| Field | Value |
|---|---|
| Registry | CEI Prompt Skills |
| Schema | `CEI_CARD_SCHEMA_v1` |
| Created | 2025-12-25 |
| Count | 3 |

本注册表用于索引"高压 CEI 风险"相关的 Prompt Skills。  
每张卡片是一个 **CEI prompt skill**，用于评估分子在高压正极界面的氧化稳定性和副反应风险。

---

## 1. 全量清单（按 Skill ID）

| Skill ID | 中文名 | 功能简述 | 关键词 | File |
|---|---|---|---|---|
| `CEI_01_risk_flowmap_v1` | CEI 风险总路由 | 总装配：整合氧化位点和副反应，给出综合风险评估 | `routing, risk-assessment` | [CEI_01_risk_flowmap_v1.md](CEI_01_risk_flowmap_v1.md) |
| `CEI_02_oxidation_site_v1` | 易氧化位点识别 | 识别分子中易被氧化的位点（基于 HOMO 分析） | `oxidation, HOMO, site` | [CEI_02_oxidation_site_v1.md](CEI_02_oxidation_site_v1.md) |
| `CEI_03_side_reaction_v1` | 副反应类别判定 | 判定氧化后可能的副反应类型 | `side-reaction, degradation` | [CEI_03_side_reaction_v1.md](CEI_03_side_reaction_v1.md) |

---

## 2. 建议调用顺序（Pipeline）

```
1. CEI_01_risk_flowmap_v1（总路由与风险评估）
   │
   ├─► 2. CEI_02_oxidation_site_v1（易氧化位点识别）
   │
   ├─► 3. CEI_03_side_reaction_v1（副反应类别判定）
   │
   └─► 4. 返回 CEI_01 做最终风险等级评估
```

---

## 3. 按分析类型索引

### 位点识别
- `CEI_02_oxidation_site_v1` — [易氧化位点识别](CEI_02_oxidation_site_v1.md)

### 反应预测
- `CEI_03_side_reaction_v1` — [副反应类别判定](CEI_03_side_reaction_v1.md)

### 总路由
- `CEI_01_risk_flowmap_v1` — [CEI 风险总路由](CEI_01_risk_flowmap_v1.md)

---

## 4. 检索标签（Tag → Skill）

| 标签 | Skill ID |
|---|---|
| `氧化` / `HOMO` / `正极` / `高压` / `位点` | CEI_02_oxidation_site_v1 |
| `副反应` / `分解` / `脱氢` / `开环` / `聚合` | CEI_03_side_reaction_v1 |
| `CEI风险` / `氧化稳定性` / `综合评估` | CEI_01_risk_flowmap_v1 |

---

## 5. 易混淆索引（用于路由与消歧）

| Skill | 易混淆 Skill | 消歧说明 |
|---|---|---|
| `CEI_02_oxidation_site_v1` | `PhysChem/HOMO_*` | CEI_02 聚焦电化学氧化；HOMO 是通用氧化倾向 |
| `CEI_03_side_reaction_v1` | `GAS_02_gassing_flags_v1` | CEI_03 是氧化副反应；GAS_02 聚焦产气 |

---

## 6. 依赖关系

```
CEI_01_risk_flowmap_v1
    ├── depends_on: [CEI_02, CEI_03]
    └── 作为总路由调用所有子技能卡

CEI_02/03
    └── 依赖上游 PhysChem HOMO 分析输出
```

---

## 7. 使用建议（编排）

1. **单一问题**（如"这个位点容易氧化吗？"）：可直接调用 `CEI_02_oxidation_site_v1`。
2. **完整 CEI 评估**：走完整 Pipeline，从 `CEI_01_risk_flowmap_v1` 开始。
3. **高压正极评估**：设置 `context.voltage_range: "high"`。
4. **材料兼容性评估**：结合具体正极材料（NCM/NCA/LCO）。

---

## 8. 与其他 Skill 模块的联动

| 场景 | 联动模块 |
|---|---|
| 需要 HOMO 排序输入 | → `PhysChem/HOMO_*` |
| 评估氧化产气 | → `04_GassingPolymerRisk_skills/GAS_02` |
| 需要官能团识别 | → `OrganicChem/SD_03` |

---

## 9. CEI 背景知识

### 什么是 CEI
- **CEI** (Cathode Electrolyte Interphase)：正极电解液界面膜
- 在高压正极（>4.3V vs Li）形成
- 由电解液氧化分解产物组成

### 高压正极氧化风险
| 正极材料 | 典型电压 | 氧化风险 |
|---------|---------|---------|
| LCO | 4.2-4.35V | 中 |
| NCM111 | 4.2-4.3V | 中 |
| NCM811/NCA | 4.3-4.5V | 高 |
| LNMO | 4.7-4.8V | 极高 |

### 理想 CEI 特征
- 薄且致密
- 离子导电、电子绝缘
- 阻止持续电解液氧化分解


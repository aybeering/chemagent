# EleChem — 电化学机理专家技能库索引

| Field | Value |
|---|---|
| Registry | EleChem Skill Modules |
| Created | 2025-12-25 |
| Module Count | 4 |
| Total Skills | 17 |
| Interface Files | 4 (Router, Schema, Guide, Index) |
| Upstream | OrganicChem, PhysChem |

本索引文件用于快速检索电化学机理专家的技能模块。EleChem 作为 OrganicChem 和 PhysChem 的**下游模块**，专注于 SEI/CEI 结构侧机理归因分析。

---

## 上游依赖（必需输入）

EleChem 需要从上游模块获取结构化输入：

| 上游模块 | 所需输出 | 用途 |
|---------|---------|------|
| OrganicChem | 官能团列表、敏感位点、环系信息 | 识别结构特征 |
| PhysChem | HOMO/LUMO 排序、电子效应、界面位点 | 判断氧化/还原倾向 |

### 快速调用示例

```yaml
call:
  target: EleChem_Router
  input:
    molecule:
      smiles: "C1COC(=O)O1"
      name: "Ethylene Carbonate"
    task_type: "full_assessment"
    upstream:
      organic_chem: <OrganicChem_Router 输出>
      phys_chem: <PhysChem_Router 输出>
    context:
      electrode: "anode"
      voltage_range: "deep_reduction"
```

### 支持的任务类型

| task_type | 描述 | 路由目标 |
|-----------|------|----------|
| `role_hypothesis` | 角色假设（溶剂/添加剂/稀释剂） | ROLE_01 |
| `sei_pathway` | SEI 路径分析（聚合膜/无机盐/LiF） | SEI_01 |
| `cei_risk` | 高压 CEI 风险评估 | CEI_01 |
| `gassing_polymer_risk` | 产气/失控聚合风险 | GAS_01 |
| `full_assessment` | 完整电化学机理评估 | 全部模块 |

---

## 模块清单

| 模块 ID | 目录名 | 功能描述 | Skill 数量 |
|---------|--------|----------|------------|
| 01 | `01_RoleHypothesis_skills/` | 角色假设（溶剂/成膜添加剂/稀释剂/不适合） | 5 |
| 02 | `02_SEIPathway_skills/` | SEI 路径（聚合膜/无机盐膜/LiF 倾向） | 4 |
| 03 | `03_CEIRisk_skills/` | 高压 CEI 风险（易氧化位点→副反应类别） | 3 |
| 04 | `04_GassingPolymerRisk_skills/` | 产气/失控聚合风险红旗 | 3 |

---

## 模块间联动关系

```
┌─────────────────────────────────────────────────────────────────┐
│                    上游输入（必需）                              │
│  ┌─────────────────┐        ┌─────────────────┐                │
│  │  OrganicChem    │        │   PhysChem      │                │
│  │  结构解析输出    │        │  HOMO/LUMO 输出  │                │
│  └────────┬────────┘        └────────┬────────┘                │
│           │                          │                          │
│           └────────────┬─────────────┘                          │
│                        │                                        │
│                        ▼                                        │
│           ┌─────────────────────────┐                           │
│           │     EleChem_Router      │                           │
│           │      电化学机理入口      │                           │
│           └───────────┬─────────────┘                           │
└───────────────────────┼─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬───────────────┐
        │               │               │               │
        ▼               ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ 01_Role       │ │ 02_SEI        │ │ 03_CEI        │ │ 04_Gassing    │
│ 角色假设       │ │ SEI路径       │ │ CEI风险       │ │ 产气/聚合风险  │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │               │               │               │
        └───────────────┴───────────────┴───────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   输出: 定性机理评估      │
                    │   → 传递给下游/报告生成   │
                    └─────────────────────────┘
```

---

## 模块详情

### 01_RoleHypothesis_skills — 角色假设

**用途**：根据分子结构判断其在电解液体系中的可能角色。

**核心目标**：为后续机理分析提供功能定位

**包含 Skills**：
- `ROLE_01_role_flowmap_v1` — 角色假设总路由
- `ROLE_02_solvent_hypothesis_v1` — 溶剂假设（高介电常数、低粘度）
- `ROLE_03_film_additive_v1` — 成膜添加剂假设（优先还原/氧化）
- `ROLE_04_diluent_hypothesis_v1` — 稀释剂假设（低配位、惰性）
- `ROLE_05_unsuitable_flag_v1` — 不适合标记（结构警示）

**索引文件**：[01_RoleHypothesis_skills/ROLE_00_index.md](01_RoleHypothesis_skills/ROLE_00_index.md)

---

### 02_SEIPathway_skills — SEI 路径

**用途**：分析分子在负极界面的 SEI 成膜路径，识别聚合膜、无机盐膜、LiF 富集等倾向。

**核心目标**：定性预测 SEI 组成趋势

**包含 Skills**：
- `SEI_01_pathway_flowmap_v1` — SEI 路径总路由
- `SEI_02_polymer_film_v1` — 聚合膜路径（开环/自由基聚合）
- `SEI_03_inorganic_salt_v1` — 无机盐膜路径（Li₂CO₃/Li₂O）
- `SEI_04_lif_tendency_v1` — LiF 倾向（C-F 断裂、F⁻ 释放）

**索引文件**：[02_SEIPathway_skills/SEI_00_index.md](02_SEIPathway_skills/SEI_00_index.md)

---

### 03_CEIRisk_skills — 高压 CEI 风险

**用途**：评估分子在高压正极界面的氧化稳定性风险，识别易氧化位点和副反应类别。

**核心目标**：定性评估 CEI 形成与氧化降解风险

**包含 Skills**：
- `CEI_01_risk_flowmap_v1` — CEI 风险总路由
- `CEI_02_oxidation_site_v1` — 易氧化位点识别
- `CEI_03_side_reaction_v1` — 副反应类别判定

**索引文件**：[03_CEIRisk_skills/CEI_00_index.md](03_CEIRisk_skills/CEI_00_index.md)

---

### 04_GassingPolymerRisk_skills — 产气/失控聚合风险

**用途**：识别分子结构中的产气风险红旗和失控聚合倾向。

**核心目标**：提供安全性结构警示

**包含 Skills**：
- `GAS_01_risk_flowmap_v1` — 产气/聚合风险总路由
- `GAS_02_gassing_flags_v1` — 产气风险红旗（CO₂/CO/H₂/HF）
- `GAS_03_polymer_risk_v1` — 失控聚合风险（自由基链增长）

**索引文件**：[04_GassingPolymerRisk_skills/GAS_00_index.md](04_GassingPolymerRisk_skills/GAS_00_index.md)

---

## 使用建议

### 推荐方式：通过 Router 调用

**调用者推荐使用 [EleChem_Router.md](EleChem_Router.md) 作为统一入口**，自动处理模块编排与结果汇总。

详细调用方式请参考 [EleChem_Integration_Guide.md](EleChem_Integration_Guide.md)。

### 直接调用（简单场景）

对于简单问题，可绕过 Router 直接调用单个模块：

| 场景 | 推荐入口 |
|------|----------|
| 判断分子在电解液中的角色 | `01_RoleHypothesis_skills/ROLE_01_role_flowmap_v1` |
| 分析 SEI 成膜路径 | `02_SEIPathway_skills/SEI_01_pathway_flowmap_v1` |
| 评估高压氧化风险 | `03_CEIRisk_skills/CEI_01_risk_flowmap_v1` |
| 识别产气风险 | `04_GassingPolymerRisk_skills/GAS_01_risk_flowmap_v1` |

---

## 完整处理流程

```
1. 从上游获取结构化输入
       │
       ├─► OrganicChem: 官能团、敏感位点、环系
       └─► PhysChem: HOMO/LUMO 排序、界面位点
       │
       ▼
2. 调用 ROLE 模块：角色假设
       │
       ├─► 溶剂假设
       ├─► 成膜添加剂假设
       ├─► 稀释剂假设
       └─► 不适合标记
       │
       ▼
3. 调用 SEI 模块：SEI 路径分析
       │
       ├─► 聚合膜路径
       ├─► 无机盐膜路径
       └─► LiF 倾向
       │
       ▼
4. 调用 CEI 模块：高压 CEI 风险
       │
       ├─► 易氧化位点识别
       └─► 副反应类别判定
       │
       ▼
5. 调用 GAS 模块：产气/聚合风险
       │
       ├─► 产气风险红旗
       └─► 失控聚合风险
       │
       ▼
6. 输出定性机理评估 → 下游报告
```

---

## 与其他模块的联动

| 联动模块 | 联动关系 |
|----------|----------|
| `OrganicChem/` | 上游输入 - 结构解析结果 |
| `PhysChem/` | 上游输入 - HOMO/LUMO 分析结果 |
| 下游报告生成 | EleChem 输出作为机理评估部分 |

---

## 文件清单

```
skill/EleChem/
├── 00_index.md                              # 本文件（总索引）
├── EleChem_Router.md                        # 统一入口路由
├── EleChem_Schema.md                        # I/O Schema 定义
├── EleChem_Integration_Guide.md             # 上游 Agent 集成指南
├── 01_RoleHypothesis_skills/                # 角色假设模块
├── 02_SEIPathway_skills/                    # SEI 路径模块
├── 03_CEIRisk_skills/                       # CEI 风险模块
└── 04_GassingPolymerRisk_skills/            # 产气/聚合风险模块
```

---

## Changelog

- 2025-12-25: 初始版本，完成全部 4 个模块，共 17 个 skill 卡片


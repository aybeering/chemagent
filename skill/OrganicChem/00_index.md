# OrganicChem — 有机化学结构解析专家技能库索引

| Field | Value |
|---|---|
| Registry | OrganicChem Skill Modules |
| Created | 2025-12-24 |
| Module Count | 3 |
| Total Skills | 22 |
| Interface Files | 4 (Router, Schema, Guide, Index) |
| Downstream | PhysChem |

本索引文件用于快速检索有机化学结构解析专家的技能模块。OrganicChem 作为 PhysChem 的**上游模块**，负责将原始分子结构转换为结构化的分析输入。

---

## 下游接口（推荐入口）

下游 Agent（如 PhysChem 专家）应通过以下标准化接口获取 OrganicChem 的输出：

| 文件 | 用途 | 说明 |
|------|------|------|
| [OrganicChem_Router.md](OrganicChem_Router.md) | 统一入口路由 | 根据任务类型自动分发到具体模块 |
| [OrganicChem_Schema.md](OrganicChem_Schema.md) | I/O Schema 定义 | 标准化输入/输出数据结构 |
| [OrganicChem_Integration_Guide.md](OrganicChem_Integration_Guide.md) | 集成指南 | 与 PhysChem 对接示例、FAQ |

### 快速调用示例

```yaml
call:
  target: OrganicChem_Router
  input:
    molecule:
      smiles: "C1COC(=O)O1"
      name: "Ethylene Carbonate"
    task_type: "full_digest"  # 或 structure_only / hotspots_only / cluster_routing
    options:
      include_hotspots: true
      include_clustering: true
```

### 支持的任务类型

| task_type | 描述 | 路由目标 |
|-----------|------|----------|
| `structure_digest` | 结构解剖与标签化 | SD_01 |
| `reactive_hotspots` | 反应敏感位点识别 | RH_01 |
| `cluster_routing` | 官能团簇路由 | FC_01 |
| `full_digest` | 完整解析（全流程） | SD_01 + RH_01 + FC_01 |

---

## 模块清单

| 模块 ID | 目录名 | 功能描述 | Skill 数量 |
|---------|--------|----------|------------|
| 01 | `01_StructureDigest_skills/` | 结构解剖与标签化（骨架/官能团/杂原子/环系/共轭） | 7 |
| 02 | `02_ReactiveHotspots_skills/` | 反应敏感位点识别（亲核/亲电/消除/开环/重排） | 7 |
| 03 | `03_FunctionalClusterRouter_skills/` | 官能团簇路由（羰基/氮/氧/卤素/硫磷/不饱和） | 8 |

---

## 模块间联动关系

```
                    ┌─────────────────────────┐
                    │  输入: SMILES / 结构式   │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ 01_StructureDigest_skills│
                    │ 结构解剖与标签化          │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                                   │
              ▼                                   ▼
    ┌─────────────────────┐          ┌─────────────────────────┐
    │02_ReactiveHotspots  │          │03_FunctionalClusterRouter│
    │ 反应敏感位点识别     │          │  官能团簇路由             │
    └─────────┬───────────┘          └───────────┬─────────────┘
              │                                   │
              └─────────────────┬─────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   输出: 结构化数据        │
                    │   → 传递给 PhysChem      │
                    └─────────────────────────┘
```

---

## 模块详情

### 01_StructureDigest_skills — 结构解剖与标签化

**用途**：解析分子结构，识别骨架、官能团、杂原子特征、环系和共轭网络。

**核心目标**：为下游分析提供结构化的分子描述

**包含 Skills**：
- `SD_01_digest_flowmap_v1` — 结构解剖总路由
- `SD_02_skeleton_parse_v1` — 骨架识别（主链/支链/环系）
- `SD_03_functional_group_v1` — 官能团识别与分类
- `SD_04_heteroatom_label_v1` — 杂原子标签（孤对/电荷）
- `SD_05_ring_system_v1` — 环系分析（芳香性/张力）
- `SD_06_conjugation_map_v1` — 共轭网络映射

**索引文件**：[01_StructureDigest_skills/SD_00_index.md](01_StructureDigest_skills/SD_00_index.md)

---

### 02_ReactiveHotspots_skills — 反应敏感位点

**用途**：识别分子中的反应敏感位点，包括亲核、亲电、消除、开环和重排倾向位点。

**核心目标**：标记可能参与反应的关键位点，为 PhysChem 的 HOMO/LUMO 分析提供目标

**包含 Skills**：
- `RH_01_hotspot_flowmap_v1` — 敏感位点总路由
- `RH_02_nucleophilic_site_v1` — 亲核位点识别
- `RH_03_electrophilic_site_v1` — 亲电位点识别
- `RH_04_elimination_site_v1` — 消除位点识别
- `RH_05_ring_opening_site_v1` — 开环位点识别
- `RH_06_rearrangement_site_v1` — 重排倾向位点识别

**索引文件**：[02_ReactiveHotspots_skills/RH_00_index.md](02_ReactiveHotspots_skills/RH_00_index.md)

---

### 03_FunctionalClusterRouter_skills — 官能团簇路由

**用途**：将识别出的官能团归类为"簇"，并推荐适合的 PhysChem 分析模块。

**核心目标**：桥接结构解析与物理化学分析，提供智能路由建议

**包含 Skills**：
- `FC_01_cluster_router_v1` — 官能团簇总路由
- `FC_02_carbonyl_cluster_v1` — 羰基簇（醛/酮/酸/酯/酰胺）
- `FC_03_nitrogen_cluster_v1` — 氮簇（胺/腈/硝基/杂环 N）
- `FC_04_oxygen_cluster_v1` — 氧簇（醇/醚/环氧）
- `FC_05_halogen_cluster_v1` — 卤素簇（C-F/C-Cl/C-Br/C-I）
- `FC_06_sulfur_phosphorus_v1` — 硫/磷簇
- `FC_07_unsaturated_cluster_v1` — 不饱和簇（烯/炔/芳环）

**索引文件**：[03_FunctionalClusterRouter_skills/FC_00_index.md](03_FunctionalClusterRouter_skills/FC_00_index.md)

---

## 使用建议

### 推荐方式：通过 Router 调用

**上游 Agent 推荐使用 [OrganicChem_Router.md](OrganicChem_Router.md) 作为统一入口**，自动处理模块编排与结果汇总。

详细调用方式请参考 [OrganicChem_Integration_Guide.md](OrganicChem_Integration_Guide.md)。

### 直接调用（简单场景）

对于简单问题，可绕过 Router 直接调用单个模块：

| 场景 | 推荐入口 |
|------|----------|
| 只需要骨架信息 | `01_StructureDigest_skills/SD_02_skeleton_parse_v1` |
| 只需要官能团列表 | `01_StructureDigest_skills/SD_03_functional_group_v1` |
| 只需要亲核/亲电位点 | `02_ReactiveHotspots_skills/RH_02_nucleophilic_site_v1` |
| 需要 PhysChem 路由建议 | `03_FunctionalClusterRouter_skills/FC_01_cluster_router_v1` |

---

## 完整处理流程

```
1. 输入分子结构 (SMILES / 名称)
       │
       ▼
2. 调用 SD 模块：结构解剖
       │
       ├─► 骨架识别
       ├─► 官能团识别
       ├─► 杂原子标签
       ├─► 环系分析
       └─► 共轭网络映射
       │
       ▼
3. 调用 RH 模块：敏感位点
       │
       ├─► 亲核位点
       ├─► 亲电位点
       ├─► 消除位点
       ├─► 开环位点
       └─► 重排位点
       │
       ▼
4. 调用 FC 模块：官能团簇路由
       │
       └─► 推荐 PhysChem 模块
       │
       ▼
5. 输出标准化数据 → PhysChem
```

---

## 与其他模块的联动

| 联动模块 | 联动关系 |
|----------|----------|
| `PhysChem/` | OrganicChem 输出作为 PhysChem 的标准输入 |
| `site_skills/` | 敏感位点可与 SITE 技能库对接 |
| `reaction/` | 结构解析可服务于反应预测 |

---

## 文件清单

```
skill/OrganicChem/
├── 00_index.md                              # 本文件（总索引）
├── OrganicChem_Router.md                    # 统一入口路由
├── OrganicChem_Schema.md                    # I/O Schema 定义
├── OrganicChem_Integration_Guide.md         # 下游 Agent 集成指南
├── 01_StructureDigest_skills/               # 结构解剖模块
├── 02_ReactiveHotspots_skills/              # 敏感位点模块
└── 03_FunctionalClusterRouter_skills/       # 官能团簇路由模块
```

---

## Changelog

- 2025-12-24: 初始版本，完成全部 3 个模块，共 22 个 skill 卡片


# Skill_Hub — 技能中枢（跨域调用入口）

| Field | Value |
|-------|-------|
| Type | Orchestrator / Hub |
| Created | 2025-12-25 |
| Purpose | 统一管理所有技能的调用与跨域协调 |

本文件定义了技能中枢（Skill Hub）架构，用于解决技能之间的复杂相互调用问题。

---

## 1. 设计目标

### 1.1 解决的问题
- **线性调用局限**：当前 OrganicChem → PhysChem → EleChem 是单向数据流
- **动态查询需求**：EleChem 分析过程中需要动态询问 OrganicChem/PhysChem
- **避免循环依赖**：通过 Hub 中介，防止技能间的直接循环调用

### 1.2 架构模式
```
                    ┌─────────────────────┐
                    │      Skill_Hub      │
                    │   (统一调度中心)     │
                    └────────┬────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
   ┌───────────┐       ┌───────────┐       ┌───────────┐
   │OrganicChem│◄─────►│ PhysChem  │◄─────►│  EleChem  │
   │  Skills   │       │  Skills   │       │  Skills   │
   └───────────┘       └───────────┘       └───────────┘
```

---

## 2. 统一查询接口

### 2.1 跨域查询协议

任何技能在执行过程中，可以通过以下协议向 Hub 发起跨域查询：

```yaml
cross_domain_query:
  source_skill: "<发起查询的技能ID>"
  target_domain: "OrganicChem | PhysChem | EleChem | SolvChem | SafetyChem"
  query_type: "<查询类型>"
  query_params:
    smiles: "<SMILES>"
    target_atoms: [<atom_indices>]  # 可选，关注特定原子
    context: "<上下文描述>"
  timeout_ms: 5000  # 超时时间
```

### 2.2 支持的查询类型（Query Catalog）

#### OrganicChem 提供的查询能力

| query_type | 描述 | 输入 | 输出 |
|------------|------|------|------|
| `adjacent_groups` | 指定原子的邻近官能团 | `target_atom`, `radius` | 邻近基团列表 |
| `functional_group_at` | 指定位置的官能团类型 | `atom_index` | 官能团信息 |
| `ring_membership` | 原子是否在环内 | `atom_index` | 环信息 |
| `conjugation_check` | 检查是否与某体系共轭 | `atom_index`, `system_type` | 共轭关系 |
| `leaving_group_ability` | 离去基团能力评估 | `atom_index` | 离去能力等级 |

#### PhysChem 提供的查询能力

| query_type | 描述 | 输入 | 输出 |
|------------|------|------|------|
| `ewg_strength` | 取代基吸电子强度 | `substituent` 或 `atom_index` | I/M 强度 |
| `edg_strength` | 取代基推电子强度 | `substituent` 或 `atom_index` | I/M 强度 |
| `local_electron_density` | 局部电子密度倾向 | `atom_index` | 富/贫电子 |
| `homo_contributor` | 该位点是否是主要 HOMO 贡献者 | `atom_index` | 是/否 + 权重 |
| `lumo_contributor` | 该位点是否是主要 LUMO 贡献者 | `atom_index` | 是/否 + 权重 |
| `bond_activation` | 键的活化程度 | `bond_atoms` | 活化等级 |

#### EleChem 提供的查询能力

| query_type | 描述 | 输入 | 输出 |
|------------|------|------|------|
| `reduction_potential_hint` | 位点相对还原电位趋势 | `atom_index` | 早/中/晚 |
| `oxidation_potential_hint` | 位点相对氧化电位趋势 | `atom_index` | 早/中/晚 |
| `sei_contribution` | 该官能团对 SEI 的贡献类型 | `fg_type` | 贡献类型 |

---

## 3. 查询示例

### 3.1 EleChem 调用 OrganicChem + PhysChem

场景：SEI_04_lif_tendency 需要判断 C-F 键的邻近环境

```yaml
# Step 1: EleChem 发起邻近基团查询
cross_domain_query:
  source_skill: "SEI_04_lif_tendency_v1"
  target_domain: "OrganicChem"
  query_type: "adjacent_groups"
  query_params:
    smiles: "FC1COC(=O)O1"  # FEC
    target_atom: 0  # F 原子
    radius: 2  # 2 键范围内

# OrganicChem 返回
query_response:
  adjacent_groups:
    - { distance: 1, atom_index: 1, element: "C", bonded_to: ["F", "C", "O", "H"] }
    - { distance: 2, atom_index: 3, fg_type: "carbonyl", is_ewg: true }
    - { distance: 2, atom_index: 5, element: "O", fg_type: "ether_O" }

# Step 2: EleChem 发起电子效应查询
cross_domain_query:
  source_skill: "SEI_04_lif_tendency_v1"
  target_domain: "PhysChem"
  query_type: "ewg_strength"
  query_params:
    smiles: "FC1COC(=O)O1"
    target_atom: 3  # 羰基 C
    effect_on: 0  # 对 F 原子的影响

# PhysChem 返回
query_response:
  ewg_strength:
    substituent: "C=O (carbonate)"
    I_effect: { sign: "-I", strength: "strong" }
    M_effect: { sign: "-M", strength: "medium" }
    distance_to_target: 2
    net_effect_on_target: "活化 C-F 键，降低 C-F σ* 能量"
```

### 3.2 PhysChem 回调 OrganicChem

场景：HOMO 分析需要确认孤对是否参与共轭

```yaml
cross_domain_query:
  source_skill: "HOMO_02_lonepair_n_v1"
  target_domain: "OrganicChem"
  query_type: "conjugation_check"
  query_params:
    smiles: "c1ccc(N)cc1"  # 苯胺
    atom_index: 6  # N 原子
    system_type: "aromatic_ring"

query_response:
  conjugation:
    is_conjugated: true
    conjugation_type: "N_lonepair_to_aromatic"
    extent: "full"
    effect: "孤对部分离域到芳环，降低局部电子密度"
```

---

## 4. 技能卡片的改造

### 4.1 声明可提供的能力（Provider）

每个技能卡片添加 `Provides` 区块：

```yaml
# 示例：SD_03_functional_group_v1.md

## Provides (Hub Query Interface)
provides:
  - query_type: "functional_group_at"
    params: ["smiles", "atom_index"]
    returns: "fg_info"
  
  - query_type: "adjacent_groups"
    params: ["smiles", "target_atom", "radius"]
    returns: "adjacent_fg_list"
```

### 4.2 声明需要的能力（Consumer）

每个技能卡片添加 `Requires` 区块：

```yaml
# 示例：SEI_04_lif_tendency_v1.md

## Requires (Cross-Domain Queries)
requires:
  - query_type: "adjacent_groups"
    from_domain: "OrganicChem"
    usage: "判断 C-F 键邻近是否有吸电子基"
  
  - query_type: "ewg_strength"
    from_domain: "PhysChem"
    usage: "评估邻近基团的吸电子强度"
```

---

## 5. 调用流程

### 5.1 完整调用流程（含跨域查询）

```
用户输入 (SMILES)
    │
    ▼
┌───────────────────────────────────────────────────────────┐
│                       Skill_Hub                           │
│                                                           │
│  1. 接收任务，启动 Pipeline                               │
│  2. 调用 OrganicChem_Router (第一阶段)                    │
│  3. 调用 PhysChem_Router (第二阶段)                       │
│  4. 调用 EleChem_Router (第三阶段)                        │
│                                                           │
│     在 EleChem 执行过程中：                               │
│     ┌─────────────────────────────────────────────────┐  │
│     │ SEI_04 需要查询邻近基团                          │  │
│     │    ├──► Hub 转发到 OrganicChem                  │  │
│     │    │       └── 返回邻近基团列表                  │  │
│     │    │                                            │  │
│     │ SEI_04 需要查询电子效应                          │  │
│     │    ├──► Hub 转发到 PhysChem                     │  │
│     │    │       └── 返回 EWG 强度                     │  │
│     │    │                                            │  │
│     │ SEI_04 完成分析，返回结果                        │  │
│     └─────────────────────────────────────────────────┘  │
│                                                           │
│  5. 汇总所有结果                                          │
└───────────────────────────────────────────────────────────┘
    │
    ▼
输出结果
```

### 5.2 调用栈示例

```
Skill_Hub.run("full_assessment", FEC)
  ├── OrganicChem_Router.run("full_digest")
  │     └── (返回 structure_digest, hotspots, clustering)
  │
  ├── PhysChem_Router.run("full_assessment")
  │     └── (返回 HOMO, LUMO, electronic_effect)
  │
  └── EleChem_Router.run("full_assessment")
        ├── ROLE_01_role_flowmap.run()
        │
        └── SEI_01_pathway_flowmap.run()
              └── SEI_04_lif_tendency.run()
                    ├── [跨域查询] Hub.query("OrganicChem", "adjacent_groups", {...})
                    │     └── OrganicChem.query_handler("adjacent_groups", {...})
                    │           └── (返回邻近基团)
                    │
                    └── [跨域查询] Hub.query("PhysChem", "ewg_strength", {...})
                          └── PhysChem.query_handler("ewg_strength", {...})
                                └── (返回吸电子强度)
```

---

## 6. 实现策略

### 6.1 渐进式改造路径

**阶段 1：定义 Query Catalog**
- 梳理所有技能的"可提供能力"和"需要能力"
- 创建 `Query_Catalog.md` 文档

**阶段 2：改造技能卡片**
- 在每个技能中添加 `Provides` 和 `Requires` 声明
- 不改变现有逻辑，只增加接口声明

**阶段 3：实现 Hub 路由**
- 创建 `Skill_Hub` 作为统一入口
- 实现跨域查询转发逻辑

**阶段 4：改造执行逻辑**
- 修改 MVP 代码支持跨域查询
- 测试完整流程

### 6.2 兼容性保证

- **向后兼容**：现有的线性调用仍然可用
- **渐进增强**：技能可以选择性地使用跨域查询
- **降级策略**：如果跨域查询失败，回退到预定义规则

---

## 7. 与现有 Router 的关系

| 组件 | 职责 | 调用关系 |
|------|------|---------|
| Skill_Hub | 总调度、跨域查询中转 | 顶层入口 |
| OrganicChem_Router | OrganicChem 内部路由 | 被 Hub 调用 |
| PhysChem_Router | PhysChem 内部路由 | 被 Hub 调用 |
| EleChem_Router | EleChem 内部路由 | 被 Hub 调用 |

```
Skill_Hub
    ├── OrganicChem_Router
    │     ├── SD_* (结构解剖)
    │     ├── RH_* (敏感位点)
    │     └── FC_* (官能团簇)
    │
    ├── PhysChem_Router
    │     ├── ELEC_* (电子效应)
    │     ├── HOMO_* (氧化倾向)
    │     ├── LUMO_* (还原倾向)
    │     └── ...
    │
    └── EleChem_Router
          ├── ROLE_* (角色假设)
          ├── SEI_* (SEI 路径)    ←── 可发起跨域查询
          ├── CEI_* (CEI 风险)    ←── 可发起跨域查询
          └── GAS_* (产气风险)
```

---

## 8. Changelog

- 2025-12-25: 初始版本，定义 Hub 架构和跨域查询协议



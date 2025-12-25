# EleChem_Router — 电化学机理专家技能库统一入口

| Field | Value |
|-------|-------|
| Type | Router / Entry Point |
| Created | 2025-12-25 |
| Schema | `EleChem_Schema.md` |
| Upstream | OrganicChem_Router, PhysChem_Router |

本文件是 EleChem 技能库的**统一调用入口**。调用者通过此 Router 访问所有电化学机理评估能力。

---

## 1. 支持的任务类型

| `task_type` | 描述 | 路由目标 | 调用深度 |
|-------------|------|----------|----------|
| `role_hypothesis` | 角色假设（溶剂/添加剂/稀释剂） | `ROLE_01_role_flowmap_v1` | 浅（仅 ROLE 模块） |
| `sei_pathway` | SEI 路径分析 | `SEI_01_pathway_flowmap_v1` | 中（SEI 模块） |
| `cei_risk` | 高压 CEI 风险评估 | `CEI_01_risk_flowmap_v1` | 中（CEI 模块） |
| `gassing_polymer_risk` | 产气/失控聚合风险 | `GAS_01_risk_flowmap_v1` | 中（GAS 模块） |
| `full_assessment` | 完整电化学机理评估 | 全部模块 | 完整 Pipeline |

---

## 2. 标准输入接口

```yaml
input:
  molecule:
    smiles: "<SMILES 字符串>"           # 必填
    name: "<分子名称>"                  # 可选
    functional_groups:                  # 可选，预识别的官能团
      - "<官能团1>"
      - "<官能团2>"
  
  task_type: "<任务类型>"               # 必填，见上表
  
  upstream:                             # 必填，上游模块输出
    organic_chem:                       # OrganicChem 输出
      structure_digest: <...>
      reactive_hotspots: <...>
      cluster_routing: <...>
    phys_chem:                          # PhysChem 输出
      oxidation_tendency: <...>
      reduction_tendency: <...>
      interface_ranking: <...>
  
  context:                              # 可选，环境上下文
    electrode: "cathode | anode | both" # 关注哪极，默认 both
    electrode_material: "<电极材料>"    # NCM / NCA / LCO / LFP / Li / Graphite / Si
    voltage_range: "high | normal | deep_reduction"  # 电位范围
    electrolyte_system: "conventional | LHCE | solid"  # 电解液体系
    temperature: <number>               # 温度（K），默认 298
  
  options:                              # 可选，高级选项
    output_format: "yaml | json"        # 输出格式，默认 yaml
    verbosity: "concise | detailed"     # 详细程度，默认 concise
```

---

## 3. 路由决策逻辑

```
接收 input
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 1: 验证输入格式（参考 EleChem_Schema.md）      │
│                                                     │
│   - 检查 molecule.smiles 是否有效                  │
│   - 检查 upstream.organic_chem 是否提供             │
│   - 检查 upstream.phys_chem 是否提供                │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 2: 根据 task_type 选择路由                     │
│                                                     │
│   role_hypothesis      ──► ROLE_01                  │
│   sei_pathway          ──► SEI_01                   │
│   cei_risk             ──► CEI_01                   │
│   gassing_polymer_risk ──► GAS_01                   │
│   full_assessment      ──► ROLE + SEI + CEI + GAS   │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 3: 执行 Pipeline                               │
│                                                     │
│   - 传递 molecule 和 upstream 给目标模块           │
│   - 按模块依赖顺序执行                              │
│   - 收集各模块输出                                  │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 4: 汇总输出                                    │
│                                                     │
│   - 按 EleChem_Schema.md 格式化响应                │
│   - 返回给调用方                                    │
└─────────────────────────────────────────────────────┘
```

---

## 4. 路由到模块的调用链

### 4.1 role_hypothesis

```
Router ──► ROLE_01_role_flowmap_v1
              │
              ├──► ROLE_02_solvent_hypothesis_v1（溶剂假设）
              ├──► ROLE_03_film_additive_v1（成膜添加剂假设）
              ├──► ROLE_04_diluent_hypothesis_v1（稀释剂假设）
              └──► ROLE_05_unsuitable_flag_v1（不适合标记）
              
输出: role_hypothesis { primary_role, confidence, evidence, alternatives }
```

### 4.2 sei_pathway

```
Router ──► SEI_01_pathway_flowmap_v1
              │
              ├──► SEI_02_polymer_film_v1（聚合膜路径）
              ├──► SEI_03_inorganic_salt_v1（无机盐膜路径）
              └──► SEI_04_lif_tendency_v1（LiF 倾向）
              
输出: sei_pathway { primary_pathway, film_composition_hint, mechanism_summary }
```

### 4.3 cei_risk

```
Router ──► CEI_01_risk_flowmap_v1
              │
              ├──► CEI_02_oxidation_site_v1（易氧化位点识别）
              └──► CEI_03_side_reaction_v1（副反应类别判定）
              
输出: cei_risk { risk_level, oxidation_sites, side_reactions, mitigation_hints }
```

### 4.4 gassing_polymer_risk

```
Router ──► GAS_01_risk_flowmap_v1
              │
              ├──► GAS_02_gassing_flags_v1（产气风险红旗）
              └──► GAS_03_polymer_risk_v1（失控聚合风险）
              
输出: gassing_polymer_risk { gas_flags, polymer_flags, overall_risk }
```

### 4.5 full_assessment

```
Router ──► ROLE_01 Pipeline（角色假设）
              │
              ▼
       ──► SEI_01 Pipeline（SEI 路径）
              │
              ▼
       ──► CEI_01 Pipeline（CEI 风险）
              │
              ▼
       ──► GAS_01 Pipeline（产气/聚合风险）
              
输出: 完整的 role_hypothesis + sei_pathway + cei_risk + gassing_polymer_risk
```

---

## 5. 标准输出格式

```yaml
output:
  task_completed: "<实际执行的任务类型>"
  molecule_echo:
    smiles: "<输入的 SMILES>"
    name: "<分子名称>"
  
  # --- role_hypothesis ---
  role_hypothesis:
    primary_role: "solvent | film_additive | diluent | unsuitable"
    confidence: "high | medium | low"
    evidence:
      - "<支持该角色的结构证据1>"
      - "<支持该角色的结构证据2>"
    alternatives:
      - role: "<备选角色>"
        confidence: "..."
        condition: "<在什么条件下可能适用>"
    unsuitable_flags:
      - flag_id: "<警示标识>"
        reason: "<不适合的原因>"
  
  # --- sei_pathway ---
  sei_pathway:
    primary_pathway: "polymer_film | inorganic_salt | lif_rich | mixed"
    pathways:
      polymer_film:
        likelihood: "high | medium | low | none"
        mechanism: "ring_opening | radical | other"
        products_hint: ["<可能产物1>", "<可能产物2>"]
      inorganic_salt:
        likelihood: "high | medium | low | none"
        products_hint: ["Li2CO3", "Li2O", "..."]
      lif:
        likelihood: "high | medium | low | none"
        f_source: "<F 来源描述>"
    film_composition_hint: "<SEI 组成定性描述>"
    mechanism_summary: "<整体成膜机理摘要>"
    confidence: "high | medium | low"
  
  # --- cei_risk ---
  cei_risk:
    risk_level: "high | medium | low"
    oxidation_sites:
      - site: "<易氧化位点描述>"
        site_type: "<位点类型>"
        reason: "<易氧化原因>"
    side_reactions:
      - reaction_type: "dehydrogenation | ring_opening | polymerization | decomposition"
        likelihood: "high | medium | low"
        description: "<反应描述>"
    mitigation_hints:
      - "<缓解措施建议>"
    confidence: "high | medium | low"
  
  # --- gassing_polymer_risk ---
  gassing_polymer_risk:
    gas_flags:
      - gas_type: "CO2 | CO | H2 | HF | C2H4 | other"
        source: "<产气来源>"
        likelihood: "high | medium | low"
        trigger: "<触发条件>"
    polymer_flags:
      - risk_type: "radical_chain | crosslinking | uncontrolled"
        source: "<聚合源>"
        likelihood: "high | medium | low"
        trigger: "<触发条件>"
    overall_risk: "high | medium | low"
    safety_notes: "<安全性说明>"
  
  # --- 通用字段 ---
  notes: "<补充说明>"
  overall_confidence: "high | medium | low"
  warnings: ["<警告信息>"]
```

---

## 6. 与上游模块的衔接

EleChem 输入需从 OrganicChem 和 PhysChem 获取：

### 所需的 OrganicChem 输出

```yaml
# 从 OrganicChem_Router 获取
organic_chem_output:
  structure_digest:
    functional_groups: [...]        # 官能团列表
    ring_info: [...]               # 环系信息
    heteroatom_labels: [...]       # 杂原子标签
  reactive_hotspots:
    electrophilic_sites: [...]     # 亲电位点
    nucleophilic_sites: [...]      # 亲核位点
    ring_opening_sites: [...]      # 开环位点
  cluster_routing:
    clusters: [...]                # 官能团簇
    suggested_physchem_modules: [...] 
```

### 所需的 PhysChem 输出

```yaml
# 从 PhysChem_Router 获取
phys_chem_output:
  oxidation_tendency:
    ox_sites_ranked: [...]         # 氧化位点排序
    dominant_site: "..."           # 最易氧化位点
  reduction_tendency:
    red_sites_ranked: [...]        # 还原位点排序
    dominant_site: "..."           # 最易还原位点
  interface_ranking:
    cathode: [...]                 # 正极界面排序
    anode: [...]                   # 负极界面排序
```

---

## 7. 快捷调用（直连单卡）

对于简单问题，可绕过 Router 直接调用单卡：

| 问题类型 | 直接调用 |
|----------|----------|
| "这个分子适合做溶剂吗？" | `ROLE_02_solvent_hypothesis_v1` |
| "会形成聚合物 SEI 吗？" | `SEI_02_polymer_film_v1` |
| "高压下容易氧化吗？" | `CEI_02_oxidation_site_v1` |
| "有产气风险吗？" | `GAS_02_gassing_flags_v1` |

---

## 8. 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| `task_type` 无效 | 返回错误提示，列出有效选项 |
| `upstream` 缺失 | 返回错误，要求提供上游模块输出 |
| `smiles` 解析失败 | 返回错误，要求提供有效 SMILES |
| 模块执行异常 | 返回部分结果 + 错误标注，降低 `overall_confidence` |
| 上游置信度过低 | 在 `warnings` 中标注"上游分析不确定，建议复核" |

---

## 9. 调用示例

### 示例 1: 完整评估 EC

```yaml
call:
  target: EleChem_Router
  input:
    molecule:
      smiles: "C1COC(=O)O1"
      name: "Ethylene Carbonate"
    task_type: "full_assessment"
    upstream:
      organic_chem:
        structure_digest:
          functional_groups: [{ fg_type: "cyclic_carbonate" }]
        reactive_hotspots:
          ring_opening_sites: [{ ring_type: "cyclic_carbonate" }]
      phys_chem:
        reduction_tendency:
          dominant_site: "羰基 C=O"
    context:
      electrode: "anode"
      voltage_range: "deep_reduction"
```

### 示例 2: 仅评估 FEC 的 SEI 路径

```yaml
call:
  target: EleChem_Router
  input:
    molecule:
      smiles: "FC1COC(=O)O1"
      name: "Fluoroethylene Carbonate"
    task_type: "sei_pathway"
    upstream:
      organic_chem:
        structure_digest:
          functional_groups: [{ fg_type: "cyclic_carbonate" }, { fg_type: "C-F" }]
      phys_chem:
        reduction_tendency:
          red_sites_ranked: [{ site: "羰基 C=O" }, { site: "C-F 键" }]
```

### 示例 3: 评估高压正极稳定性

```yaml
call:
  target: EleChem_Router
  input:
    molecule:
      smiles: "COC(=O)OC"
      name: "Dimethyl Carbonate"
    task_type: "cei_risk"
    upstream:
      organic_chem:
        structure_digest:
          functional_groups: [{ fg_type: "carbonate" }]
      phys_chem:
        oxidation_tendency:
          dominant_site: "酯氧孤对"
    context:
      electrode: "cathode"
      voltage_range: "high"
      electrode_material: "NCM"
```

---

## 10. Changelog

- 2025-12-25: 初始版本，支持 5 种任务类型路由


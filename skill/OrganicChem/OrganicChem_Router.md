# OrganicChem_Router — 有机化学结构解析专家技能库统一入口

| Field | Value |
|-------|-------|
| Type | Router / Entry Point |
| Created | 2025-12-24 |
| Schema | `OrganicChem_Schema.md` |
| Downstream | PhysChem_Router |

本文件是 OrganicChem 技能库的**统一调用入口**。上游 Agent（如用户交互层）通过此 Router 进行分子结构解析，输出传递给下游 PhysChem 进行物理化学分析。

---

## 1. 支持的任务类型

| `task_type` | 描述 | 路由目标 | 输出范围 |
|-------------|------|----------|----------|
| `structure_digest` | 结构解剖与标签化 | `SD_01_digest_flowmap_v1` | 骨架/官能团/杂原子/环系/共轭 |
| `reactive_hotspots` | 反应敏感位点识别 | `RH_01_hotspot_flowmap_v1` | 亲核/亲电/消除/开环/重排位点 |
| `cluster_routing` | 官能团簇路由 | `FC_01_cluster_router_v1` | 官能团分类 + PhysChem 建议 |
| `full_digest` | 完整解析（全流程） | SD_01 + RH_01 + FC_01 | 全部输出 |

---

## 2. 标准输入接口

```yaml
input:
  molecule:
    smiles: "<SMILES 字符串>"           # 必填
    name: "<分子名称>"                  # 可选
    structure_description: "<结构描述>" # 可选，当 SMILES 不可用时
  
  task_type: "<任务类型>"               # 必填，见上表
  
  options:                              # 可选
    include_hotspots: true              # 是否包含敏感位点，默认 true
    include_clustering: true            # 是否包含官能团簇路由，默认 true
    output_format: "yaml | json"        # 输出格式，默认 yaml
    verbosity: "concise | detailed"     # 详细程度，默认 concise
    target_atoms: []                    # 只关注的特定原子（可选）
```

---

## 3. 路由决策逻辑

```
接收 input
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 1: 验证输入格式（参考 OrganicChem_Schema.md）  │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 2: 根据 task_type 选择路由                     │
│                                                     │
│   structure_digest   ──► SD_01                      │
│   reactive_hotspots  ──► RH_01（需先执行 SD_01）    │
│   cluster_routing    ──► FC_01（需先执行 SD_01）    │
│   full_digest        ──► SD_01 + RH_01 + FC_01      │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 3: 执行 Pipeline                               │
│                                                     │
│   1. 调用 SD_01 获取结构解剖结果                    │
│   2. 若需要，调用 RH_01 获取敏感位点                │
│   3. 若需要，调用 FC_01 获取官能团簇路由            │
│   4. 收集各模块输出                                 │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 4: 汇总输出                                    │
│                                                     │
│   - 按 OrganicChem_Schema.md 格式化响应             │
│   - 生成 PhysChem 路由建议                          │
│   - 返回给调用方                                    │
└─────────────────────────────────────────────────────┘
```

---

## 4. 路由到模块的调用链

### 4.1 structure_digest

```
Router ──► SD_01_digest_flowmap_v1
              │
              ├──► SD_02_skeleton_parse_v1（骨架识别）
              ├──► SD_03_functional_group_v1（官能团识别）
              ├──► SD_04_heteroatom_label_v1（杂原子标签）
              ├──► SD_05_ring_system_v1（环系分析）
              └──► SD_06_conjugation_map_v1（共轭网络映射）
              
输出: skeleton, functional_groups, heteroatom_labels, ring_info, conjugation_map
```

### 4.2 reactive_hotspots

```
Router ──► SD_01（先解剖结构）
              │
              ▼
       ──► RH_01_hotspot_flowmap_v1
              │
              ├──► RH_02_nucleophilic_site_v1（亲核位点）
              ├──► RH_03_electrophilic_site_v1（亲电位点）
              ├──► RH_04_elimination_site_v1（消除位点）
              ├──► RH_05_ring_opening_site_v1（开环位点）
              └──► RH_06_rearrangement_site_v1（重排位点）
              
输出: nucleophilic_sites, electrophilic_sites, elimination_sites, ring_opening_sites, rearrangement_sites
```

### 4.3 cluster_routing

```
Router ──► SD_01（先解剖结构）
              │
              ▼
       ──► FC_01_cluster_router_v1
              │
              ├──► FC_02_carbonyl_cluster_v1（羰基簇）
              ├──► FC_03_nitrogen_cluster_v1（氮簇）
              ├──► FC_04_oxygen_cluster_v1（氧簇）
              ├──► FC_05_halogen_cluster_v1（卤素簇）
              ├──► FC_06_sulfur_phosphorus_v1（硫磷簇）
              └──► FC_07_unsaturated_cluster_v1（不饱和簇）
              
输出: clusters[], suggested_physchem_modules[]
```

### 4.4 full_digest

```
Router ──► SD_01 Pipeline（结构解剖）
              │
              ▼
       ──► RH_01 Pipeline（敏感位点）
              │
              ▼
       ──► FC_01 Pipeline（官能团簇路由）
              
输出: 完整的 structure_digest + reactive_hotspots + cluster_routing
```

---

## 5. 标准输出格式

```yaml
output:
  task_completed: "<实际执行的任务类型>"
  molecule_echo:
    smiles: "<输入的 SMILES>"
    name: "<分子名称>"
    canonical_smiles: "<标准化后的 SMILES>"
  
  # --- structure_digest ---
  structure_digest:
    skeleton:
      type: "linear | branched | cyclic | polycyclic | bridged"
      main_chain_length: <int>
      ring_count: <int>
      ring_ids: ["<ring_id>"]
    
    functional_groups:
      - fg_id: "<unique_id>"
        fg_type: "<官能团类型>"
        atoms: [<atom_indices>]
        center_atom: <int>
        subtype: "<子类型，如 primary_alcohol>"
    
    heteroatom_labels:
      - atom_index: <int>
        element: "<元素符号>"
        hybridization: "sp | sp2 | sp3"
        lone_pairs: <int>
        formal_charge: <int>
        environment: "<周围环境描述>"
    
    ring_info:
      - ring_id: "<unique_id>"
        size: <int>
        atoms: [<atom_indices>]
        aromatic: true | false
        strain_level: "none | low | medium | high"
        ring_type: "carbocycle | heterocycle | fused | bridged"
    
    conjugation_map:
      pi_systems:
        - system_id: "<unique_id>"
          atoms: [<atom_indices>]
          extent: "local | extended | aromatic"
      cross_conjugated: true | false
  
  # --- reactive_hotspots ---
  reactive_hotspots:
    nucleophilic_sites:
      - site_id: "<unique_id>"
        atom_index: <int>
        site_type: "n_lonepair | pi_system | anion | enolate"
        strength: "strong | moderate | weak"
        confidence: <0.0-1.0>
        notes: "<补充说明>"
    
    electrophilic_sites:
      - site_id: "<unique_id>"
        atom_index: <int>
        site_type: "carbonyl_C | sp3_with_LG | deficient_aromatic | carbocation_potential"
        strength: "strong | moderate | weak"
        leaving_group: "<LG 类型，若有>"
        confidence: <0.0-1.0>
    
    elimination_sites:
      - site_id: "<unique_id>"
        c_alpha: <int>
        c_beta: <int>
        leaving_group: "<LG 类型>"
        beta_h_count: <int>
        mechanism_preference: "E2 | E1cb | E1"
        confidence: <0.0-1.0>
    
    ring_opening_sites:
      - site_id: "<unique_id>"
        ring_id: "<对应 ring_id>"
        attack_atom: <int>
        ring_type: "epoxide | lactone | cyclic_carbonate | aziridine | small_ring"
        strain_driven: true | false
        confidence: <0.0-1.0>
    
    rearrangement_sites:
      - site_id: "<unique_id>"
        migrating_group: "<迁移基团描述>"
        origin_atom: <int>
        destination_atom: <int>
        rearrangement_type: "1,2-shift | Wagner-Meerwein | pinacol | Cope | Claisen"
        confidence: <0.0-1.0>
  
  # --- cluster_routing ---
  cluster_routing:
    clusters:
      - cluster_type: "carbonyl | nitrogen | oxygen | halogen | sulfur_phosphorus | unsaturated"
        functional_groups: ["<fg_id>"]
        priority: <int>
        physchem_modules: ["HOMO_02", "LUMO_02", ...]
    
    primary_cluster: "<主要簇类型>"
    suggested_physchem_modules:
      - module_id: "ELEC_01 | HOMO_01 | LUMO_01 | ..."
        reason: "<推荐理由>"
        priority: <int>
  
  # --- 通用字段 ---
  notes: "<补充说明>"
  overall_confidence: "high | medium | low"
  warnings: ["<警告信息>"]
```

---

## 6. 与 PhysChem 的衔接

OrganicChem 输出可直接作为 PhysChem 的输入：

```yaml
# OrganicChem 输出 → PhysChem 输入的映射
physchem_input:
  molecule:
    smiles: "${output.molecule_echo.smiles}"
    name: "${output.molecule_echo.name}"
    functional_groups: "${output.structure_digest.functional_groups[].fg_type}"
  
  task_type: "${output.cluster_routing.suggested_physchem_modules[0].module_id}"
  
  context:
    # 从 OrganicChem 输出推断
    target_sites: "${output.reactive_hotspots.*.atom_index}"
```

### 推荐模块映射规则

| OrganicChem 输出 | 推荐的 PhysChem 模块 |
|-----------------|---------------------|
| 羰基簇 (carbonyl) | LUMO_02_pi_antibond_v1 |
| 氧簇 (oxygen) 含醚/醇 | HOMO_02_lonepair_n_v1 |
| 氮簇 (nitrogen) 含胺 | HOMO_02_lonepair_n_v1 |
| 卤素簇 (halogen) | LUMO_03_sigma_antibond_v1, ELEC_02_I_sigma_v1 |
| 不饱和簇 (unsaturated) | HOMO_03_pi_system_v1, LUMO_02_pi_antibond_v1 |
| 小环/高张力环 | LUMO_04_ring_strain_v1 |

---

## 7. 快捷调用（直连单卡）

对于简单问题，可绕过 Router 直接调用单卡：

| 问题类型 | 直接调用 |
|----------|----------|
| "这个分子有哪些官能团？" | `SD_03_functional_group_v1` |
| "苯环是否芳香？" | `SD_05_ring_system_v1` |
| "哪里是亲核位点？" | `RH_02_nucleophilic_site_v1` |
| "羰基属于什么簇？" | `FC_02_carbonyl_cluster_v1` |

---

## 8. 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| `task_type` 无效 | 返回错误提示，列出有效选项 |
| `smiles` 解析失败 | 返回错误，要求提供有效 SMILES 或结构描述 |
| 模块执行异常 | 返回部分结果 + 错误标注，降低 `overall_confidence` |
| 结构过于复杂 | 在 `warnings` 中标注"建议分段分析"或"需人工复核" |

---

## 9. 调用示例

### 示例 1: 完整解析 EC

```yaml
call:
  target: OrganicChem_Router
  input:
    molecule:
      smiles: "C1COC(=O)O1"
      name: "Ethylene Carbonate"
    task_type: "full_digest"
```

### 示例 2: 只需要官能团识别

```yaml
call:
  target: OrganicChem_Router
  input:
    molecule:
      smiles: "CC(=O)OC"
      name: "Methyl Acetate"
    task_type: "structure_digest"
    options:
      include_hotspots: false
      include_clustering: false
```

### 示例 3: 获取 PhysChem 路由建议

```yaml
call:
  target: OrganicChem_Router
  input:
    molecule:
      smiles: "FC(F)(F)C(=O)OCC"
      name: "Ethyl Trifluoroacetate"
    task_type: "cluster_routing"
```

---

## 10. Changelog

- 2025-12-24: 初始版本，支持 4 种任务类型路由


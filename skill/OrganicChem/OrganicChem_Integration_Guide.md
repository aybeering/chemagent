# OrganicChem_Integration_Guide — 与 PhysChem 集成指南

| Field | Value |
|-------|-------|
| Type | Integration Guide |
| Created | 2025-12-24 |
| Audience | 上游调用者 / PhysChem Agent |
| Upstream | 用户输入 / SMILES |
| Downstream | PhysChem 技能库 |

本文档为 OrganicChem 技能库提供与 PhysChem 的集成指南，说明如何将 OrganicChem 的输出转换为 PhysChem 的输入。

---

## 1. 快速开始

### 1.1 端到端调用示例

```yaml
# Step 1: 调用 OrganicChem 解析结构
call:
  target: OrganicChem_Router
  input:
    molecule:
      smiles: "C1COC(=O)O1"
      name: "Ethylene Carbonate"
    task_type: "full_digest"

# OrganicChem 输出
organic_output:
  structure_digest:
    functional_groups:
      - { fg_id: "FG_1", fg_type: "cyclic_carbonate", fg_category: "carbonyl" }
  reactive_hotspots:
    electrophilic_sites:
      - { site_id: "E_1", atom_index: 3, site_type: "carbonyl_C" }
    ring_opening_sites:
      - { site_id: "RO_1", ring_type: "cyclic_carbonate" }
  cluster_routing:
    primary_cluster: "carbonyl"
    suggested_physchem_modules:
      - { module_id: "LUMO_02_pi_antibond_v1", reason: "羰基 π*" }
      - { module_id: "LUMO_04_ring_strain_v1", reason: "五元环张力" }

# Step 2: 调用 PhysChem 进行分析
call:
  target: PhysChem_Router
  input:
    molecule:
      smiles: "C1COC(=O)O1"
      name: "Ethylene Carbonate"
      functional_groups: ["cyclic_carbonate"]  # 从 OrganicChem 获取
    task_type: "interface_ranking"
    context:
      electrode: "anode"
```

### 1.2 流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户输入                                      │
│                    SMILES / 分子名称                                 │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     OrganicChem_Router                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ SD_01: 结构解剖                                              │   │
│  │  • 骨架识别                                                  │   │
│  │  • 官能团识别                                                │   │
│  │  • 杂原子标签                                                │   │
│  │  • 环系分析                                                  │   │
│  │  • 共轭网络映射                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                            │                                        │
│              ┌─────────────┴─────────────┐                          │
│              ▼                           ▼                          │
│  ┌───────────────────────┐  ┌───────────────────────────┐          │
│  │ RH_01: 敏感位点        │  │ FC_01: 官能团簇路由        │          │
│  │  • 亲核位点            │  │  • 羰基簇                  │          │
│  │  • 亲电位点            │  │  • 氮簇                    │          │
│  │  • 消除位点            │  │  • 氧簇                    │          │
│  │  • 开环位点            │  │  • 卤素簇                  │          │
│  │  • 重排位点            │  │  • 硫/磷簇                 │          │
│  └───────────────────────┘  │  • 不饱和簇                 │          │
│                              └───────────────────────────┘          │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            │ OrganicChem 输出
                            │ (结构化数据 + PhysChem 路由建议)
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PhysChem_Router                                │
│                                                                     │
│  根据 OrganicChem 的路由建议，调用相应模块：                         │
│  • ELEC: 电子效应分析                                               │
│  • HOMO: 氧化倾向评估                                               │
│  • LUMO: 还原倾向评估                                               │
│  • INTF: 界面位点排序                                               │
│  • TRADE: 稳定性校验                                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 数据转换规则

### 2.1 OrganicChem 输出到 PhysChem 输入的映射

| OrganicChem 输出字段 | PhysChem 输入字段 | 说明 |
|---------------------|------------------|------|
| `molecule_echo.smiles` | `molecule.smiles` | 直接传递 |
| `molecule_echo.name` | `molecule.name` | 直接传递 |
| `structure_digest.functional_groups[].fg_type` | `molecule.functional_groups[]` | 提取官能团类型列表 |
| `cluster_routing.suggested_physchem_modules[0].module_id` | `task_type` 推断 | 根据模块推断任务类型 |
| `reactive_hotspots.*.atom_index` | `options.target_sites` | 指定分析位点 |

### 2.2 模块 ID 到任务类型的映射

| OrganicChem 推荐模块 | PhysChem task_type |
|---------------------|-------------------|
| `ELEC_*` | `electronic_effect` |
| `HOMO_*` | `oxidation_tendency` |
| `LUMO_*` | `reduction_tendency` |
| `INTF_*` | `interface_ranking` |
| 组合 | `full_assessment` |

### 2.3 转换函数示例

```python
def organic_to_physchem(organic_output):
    """将 OrganicChem 输出转换为 PhysChem 输入"""
    
    # 提取基本分子信息
    molecule = {
        "smiles": organic_output["molecule_echo"]["smiles"],
        "name": organic_output["molecule_echo"].get("name", ""),
        "functional_groups": [
            fg["fg_type"] 
            for fg in organic_output["structure_digest"]["functional_groups"]
        ]
    }
    
    # 根据推荐模块确定任务类型
    suggested = organic_output["cluster_routing"]["suggested_physchem_modules"]
    if any("INTF" in m["module_id"] for m in suggested):
        task_type = "interface_ranking"
    elif any("HOMO" in m["module_id"] for m in suggested):
        task_type = "oxidation_tendency"
    elif any("LUMO" in m["module_id"] for m in suggested):
        task_type = "reduction_tendency"
    else:
        task_type = "electronic_effect"
    
    # 提取目标位点
    target_sites = []
    for site_type in ["electrophilic_sites", "nucleophilic_sites", "ring_opening_sites"]:
        sites = organic_output["reactive_hotspots"].get(site_type, [])
        target_sites.extend([s["atom_index"] for s in sites])
    
    return {
        "molecule": molecule,
        "task_type": task_type,
        "options": {
            "target_sites": target_sites[:5]  # 限制前 5 个
        }
    }
```

---

## 3. 典型场景

### 3.1 场景 1：电解液添加剂评估

**输入**：FEC (氟代碳酸乙烯酯)

```yaml
# OrganicChem 解析
call:
  target: OrganicChem_Router
  input:
    molecule:
      smiles: "FC1COC(=O)O1"
      name: "Fluoroethylene Carbonate"
    task_type: "full_digest"

# OrganicChem 输出摘要
organic_output:
  structure_digest:
    functional_groups:
      - { fg_type: "cyclic_carbonate", fg_category: "carbonyl" }
      - { fg_type: "C-F", fg_category: "halogen" }
  reactive_hotspots:
    electrophilic_sites:
      - { atom_index: 4, site_type: "carbonyl_C" }
    ring_opening_sites:
      - { ring_type: "cyclic_carbonate", strain_driven: true }
  cluster_routing:
    primary_cluster: "carbonyl"
    secondary_clusters: ["halogen"]
    suggested_physchem_modules:
      - { module_id: "LUMO_02_pi_antibond_v1" }
      - { module_id: "LUMO_03_sigma_antibond_v1" }
      - { module_id: "LUMO_04_ring_strain_v1" }

# PhysChem 调用
call:
  target: PhysChem_Router
  input:
    molecule:
      smiles: "FC1COC(=O)O1"
      name: "Fluoroethylene Carbonate"
      functional_groups: ["cyclic_carbonate", "C-F"]
    task_type: "interface_ranking"
    context:
      electrode: "anode"
      electrode_material: "Li"
      voltage_range: "deep_reduction"
```

### 3.2 场景 2：取代基电子效应分析

**输入**：对硝基苯甲醚（推拉电子体系）

```yaml
# OrganicChem 解析
call:
  target: OrganicChem_Router
  input:
    molecule:
      smiles: "COc1ccc([N+](=O)[O-])cc1"
      name: "p-Nitroanisole"
    task_type: "full_digest"

# OrganicChem 输出摘要
organic_output:
  structure_digest:
    functional_groups:
      - { fg_type: "ether", fg_category: "oxygen" }
      - { fg_type: "nitro", fg_category: "nitrogen" }
      - { fg_type: "benzene", fg_category: "unsaturated" }
    conjugation_map:
      pi_systems:
        - { atoms: [1,2,3,4,5,6,7,8,9,10], type: "extended" }
  cluster_routing:
    suggested_physchem_modules:
      - { module_id: "ELEC_03_M_pi_v1", reason: "OMe +M 与 NO₂ -M 共轭" }

# PhysChem 调用
call:
  target: PhysChem_Router
  input:
    molecule:
      smiles: "COc1ccc([N+](=O)[O-])cc1"
    task_type: "electronic_effect"
```

### 3.3 场景 3：溶剂分子稳定性

**输入**：碳酸二甲酯 (DMC)

```yaml
# OrganicChem 解析
organic_output:
  structure_digest:
    functional_groups:
      - { fg_type: "carbonate", fg_category: "carbonyl" }
  cluster_routing:
    suggested_physchem_modules:
      - { module_id: "LUMO_02_pi_antibond_v1" }
      - { module_id: "HOMO_02_lonepair_n_v1" }

# PhysChem 调用
call:
  target: PhysChem_Router
  input:
    molecule:
      smiles: "COC(=O)OC"
      name: "Dimethyl Carbonate"
    task_type: "full_assessment"
    context:
      electrode: "both"
```

---

## 4. 输出字段对照

### 4.1 OrganicChem → PhysChem 字段继承

| OrganicChem 分析 | 对应的 PhysChem 分析 |
|-----------------|---------------------|
| 羰基官能团 → electrophilic_sites | LUMO π* 分析 |
| 醚/胺官能团 → nucleophilic_sites | HOMO n 孤对分析 |
| 环氧/内酯 → ring_opening_sites | LUMO 环张力分析 |
| 卤素官能团 | LUMO σ* + ELEC -I 分析 |
| 共轭体系 | ELEC M 效应分析 |

### 4.2 置信度传递

```
OrganicChem 置信度 → PhysChem 置信度

规则：
- 若 OrganicChem 置信度 < 0.7，PhysChem 应降级其结论
- 若结构解析不确定，在 PhysChem 输出中标注 "结构待确认"
```

---

## 5. 错误处理

### 5.1 OrganicChem 解析失败

```yaml
# 错误情况
organic_output:
  error: "SMILES 解析失败"
  warnings: ["无法确定分子结构"]

# 处理方式
# 不调用 PhysChem，返回错误给用户
```

### 5.2 无推荐模块

```yaml
# 情况：简单烷烃，无明显官能团
organic_output:
  cluster_routing:
    clusters: []
    suggested_physchem_modules: []

# 处理方式
# 使用默认任务类型 "full_assessment"
```

### 5.3 复杂分子处理

```yaml
# 情况：多官能团竞争
organic_output:
  cluster_routing:
    clusters:
      - { cluster_type: "carbonyl", priority: 1 }
      - { cluster_type: "nitrogen", priority: 2 }
      - { cluster_type: "halogen", priority: 3 }

# 处理方式
# 按优先级依次调用 PhysChem，汇总结果
```

---

## 6. 最佳实践

### 6.1 推荐流程

1. **始终先调用 OrganicChem**：获取结构化的分子描述
2. **使用路由建议**：按 OrganicChem 推荐的模块顺序调用 PhysChem
3. **传递位点信息**：将敏感位点传递给 PhysChem 的 target_sites
4. **保持置信度链**：跟踪从 OrganicChem 到 PhysChem 的置信度

### 6.2 性能优化

- **缓存结构解剖**：同一分子的 SD 输出可复用
- **按需调用模块**：不必每次都调用 full_digest
- **限制位点数量**：target_sites 建议不超过 5 个

### 6.3 调试建议

- 检查 SMILES 是否正确解析
- 确认官能团识别是否完整
- 验证敏感位点是否合理
- 对比 OrganicChem 和 PhysChem 的置信度

---

## 7. FAQ

### Q1: OrganicChem 和 PhysChem 必须一起使用吗？

**A**: 不是必须的。
- 若已知分子结构和官能团，可直接调用 PhysChem
- OrganicChem 的优势是自动化解析和路由建议

### Q2: 如何处理 OrganicChem 未识别的官能团？

**A**: 
- 使用 `structure_description` 字段补充描述
- 在 PhysChem 调用时手动指定 `functional_groups`

### Q3: 敏感位点和 PhysChem 的位点有什么区别？

**A**:
- OrganicChem 敏感位点：基于结构的反应倾向
- PhysChem 位点排序：基于 HOMO/LUMO 的电化学活性

### Q4: 可以跳过某些 OrganicChem 模块吗？

**A**: 可以。使用 `options.skip_modules` 指定：
```yaml
options:
  skip_modules: ["RH_06_rearrangement_site_v1"]
```

---

## 8. 版本兼容性

| OrganicChem 版本 | PhysChem 版本 | 兼容性 |
|-----------------|--------------|--------|
| 1.0 | 1.0 | 完全兼容 |

---

## 9. Changelog

- 2025-12-24: 初始版本


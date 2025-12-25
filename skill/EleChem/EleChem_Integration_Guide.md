# EleChem_Integration_Guide — 与 OrganicChem/PhysChem 集成指南

| Field | Value |
|-------|-------|
| Type | Integration Guide |
| Created | 2025-12-25 |
| Audience | 上游调用者 / 报告生成 Agent |
| Upstream | OrganicChem, PhysChem |
| Downstream | 报告生成 / 决策支持 |

本文档为 EleChem 技能库提供与上游模块（OrganicChem、PhysChem）的集成指南。

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
    ring_opening_sites:
      - { ring_type: "cyclic_carbonate", strain_driven: true }
  cluster_routing:
    primary_cluster: "carbonyl"

# Step 2: 调用 PhysChem 进行分析
call:
  target: PhysChem_Router
  input:
    molecule:
      smiles: "C1COC(=O)O1"
      functional_groups: ["cyclic_carbonate"]
    task_type: "interface_ranking"
    context:
      electrode: "anode"

# PhysChem 输出
phys_output:
  reduction_tendency:
    dominant_site: "羰基 C=O"
    red_sites_ranked:
      - { rank: 1, site: "羰基 C=O", lumo_type: "pi_star" }
  interface_ranking:
    anode:
      - { rank: 1, site: "羰基 C=O" }

# Step 3: 调用 EleChem 进行电化学机理分析
call:
  target: EleChem_Router
  input:
    molecule:
      smiles: "C1COC(=O)O1"
      name: "Ethylene Carbonate"
    task_type: "full_assessment"
    upstream:
      organic_chem: ${organic_output}
      phys_chem: ${phys_output}
    context:
      electrode: "anode"
      voltage_range: "deep_reduction"
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
│  • 结构解剖（官能团、环系、杂原子）                                  │
│  • 敏感位点识别（亲核/亲电/开环）                                    │
│  • 官能团簇路由                                                      │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      PhysChem_Router                                │
│  • 电子效应分析                                                      │
│  • 氧化倾向（HOMO 排序）                                             │
│  • 还原倾向（LUMO 排序）                                             │
│  • 界面位点排序                                                      │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       EleChem_Router                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ROLE: 角色假设                                               │   │
│  │  • 溶剂 / 成膜添加剂 / 稀释剂 / 不适合                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ SEI: SEI 路径分析                                            │   │
│  │  • 聚合膜 / 无机盐膜 / LiF 倾向                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ CEI: 高压 CEI 风险                                           │   │
│  │  • 易氧化位点 → 副反应类别                                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ GAS: 产气/聚合风险                                           │   │
│  │  • 产气红旗 / 失控聚合风险                                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        输出结果                                      │
│               定性电化学机理评估 → 报告生成                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. 数据转换规则

### 2.1 OrganicChem 输出到 EleChem 输入的映射

| OrganicChem 输出字段 | EleChem 使用方式 | 说明 |
|---------------------|-----------------|------|
| `structure_digest.functional_groups` | 识别关键官能团 | 用于角色假设和路径分析 |
| `structure_digest.ring_info` | 判断环张力和开环倾向 | 用于 SEI 聚合膜路径 |
| `structure_digest.heteroatom_labels` | 识别杂原子特征 | 用于氧化/还原位点分析 |
| `reactive_hotspots.ring_opening_sites` | SEI 开环路径分析 | 直接用于 SEI_02 |
| `reactive_hotspots.electrophilic_sites` | 还原反应位点 | 与 PhysChem LUMO 联用 |
| `reactive_hotspots.nucleophilic_sites` | 氧化反应位点 | 与 PhysChem HOMO 联用 |
| `cluster_routing.clusters` | 官能团簇信息 | 用于路径优先级判断 |

### 2.2 PhysChem 输出到 EleChem 输入的映射

| PhysChem 输出字段 | EleChem 使用方式 | 说明 |
|------------------|-----------------|------|
| `oxidation_tendency.ox_sites_ranked` | CEI 风险评估 | 直接用于 CEI_02 |
| `oxidation_tendency.dominant_site` | 主要氧化风险位点 | CEI 分析重点 |
| `reduction_tendency.red_sites_ranked` | SEI 路径分析 | 确定还原顺序 |
| `reduction_tendency.dominant_site` | 主要还原位点 | SEI 分析重点 |
| `interface_ranking.cathode` | 正极界面排序 | 用于 CEI 模块 |
| `interface_ranking.anode` | 负极界面排序 | 用于 SEI 模块 |
| `electronic_effect.channels` | 取代基效应 | 用于稳定性分析 |

### 2.3 转换函数示例

```python
def prepare_elechem_input(organic_output, phys_output, molecule, context):
    """将 OrganicChem 和 PhysChem 输出转换为 EleChem 输入"""
    
    return {
        "molecule": {
            "smiles": molecule["smiles"],
            "name": molecule.get("name", ""),
            "functional_groups": [
                fg["fg_type"] 
                for fg in organic_output["structure_digest"]["functional_groups"]
            ]
        },
        "task_type": "full_assessment",
        "upstream": {
            "organic_chem": organic_output,
            "phys_chem": phys_output
        },
        "context": context
    }
```

---

## 3. 典型场景

### 3.1 场景 1：电解液溶剂评估（EC）

```yaml
# 分子：碳酸乙烯酯 (EC)
molecule:
  smiles: "C1COC(=O)O1"
  name: "Ethylene Carbonate"

# EleChem 分析结果摘要
elechem_output:
  role_hypothesis:
    primary_role: "solvent"
    evidence: ["高介电常数（约89）", "可溶解锂盐", "参与 SEI 形成"]
  sei_pathway:
    primary_pathway: "mixed"
    pathways:
      polymer_film: { likelihood: "high", mechanism: "ring_opening" }
      inorganic_salt: { likelihood: "medium" }
  cei_risk:
    risk_level: "medium"
    oxidation_sites: [{ site: "酯氧孤对" }]
```

### 3.2 场景 2：成膜添加剂评估（FEC）

```yaml
# 分子：氟代碳酸乙烯酯 (FEC)
molecule:
  smiles: "FC1COC(=O)O1"
  name: "Fluoroethylene Carbonate"

# EleChem 分析结果摘要
elechem_output:
  role_hypothesis:
    primary_role: "film_additive"
    evidence: ["C-F 键可释放 F⁻", "优先于 EC 还原"]
  sei_pathway:
    primary_pathway: "lif_rich"
    pathways:
      lif: { likelihood: "high", f_source: "C-F 还原断裂" }
      polymer_film: { likelihood: "high" }
  gassing_polymer_risk:
    gas_flags: [{ gas_type: "CO2", likelihood: "medium" }]
```

### 3.3 场景 3：稀释剂评估（氟代醚）

```yaml
# 分子：双(2,2,2-三氟乙基)醚 (BTFE)
molecule:
  smiles: "FC(F)(F)COCC(F)(F)F"
  name: "Bis(2,2,2-trifluoroethyl) ether"

# EleChem 分析结果摘要
elechem_output:
  role_hypothesis:
    primary_role: "diluent"
    evidence: ["低介电常数", "弱 Li+ 配位", "高氟化惰性"]
  sei_pathway:
    primary_pathway: "lif_rich"
    pathways:
      lif: { likelihood: "medium", f_source: "C-F 在极低电位下可能断裂" }
  cei_risk:
    risk_level: "low"
    oxidation_sites: [] # 氟化结构提高氧化稳定性
```

### 3.4 场景 4：高压溶剂评估（砜类）

```yaml
# 分子：环丁砜 (Sulfolane)
molecule:
  smiles: "C1CCS(=O)(=O)C1"
  name: "Sulfolane"

# EleChem 分析结果摘要
elechem_output:
  role_hypothesis:
    primary_role: "solvent"
    evidence: ["高氧化稳定性（砜基）", "高介电常数"]
  cei_risk:
    risk_level: "low"
    notes: "砜基为强吸电子基，降低 HOMO，提高氧化稳定性"
  sei_pathway:
    primary_pathway: "polymer_film"
    notes: "环状结构可开环聚合"
```

---

## 4. 输出字段对照

### 4.1 上游 → EleChem 字段继承

| 上游分析 | EleChem 模块 | 继承方式 |
|---------|-------------|---------|
| OrganicChem 官能团 | ROLE | 判断角色类型 |
| OrganicChem 开环位点 | SEI | 聚合膜路径分析 |
| PhysChem HOMO 排序 | CEI | 氧化风险评估 |
| PhysChem LUMO 排序 | SEI | 还原路径分析 |
| PhysChem 界面排序 | SEI/CEI | 界面反应优先级 |

### 4.2 置信度传递

```
OrganicChem 置信度 ─┐
                   ├──► EleChem 置信度
PhysChem 置信度 ───┘

规则：
- EleChem 置信度 ≤ min(OrganicChem 置信度, PhysChem 置信度)
- 若任一上游置信度 < 0.7，EleChem 在 warnings 中标注
```

---

## 5. 错误处理

### 5.1 上游输入缺失

```yaml
# 错误情况
error: "upstream.organic_chem 缺失"

# 处理方式
# 1. 返回错误，要求提供上游输出
# 2. 或调用 OrganicChem_Router 获取
```

### 5.2 上游置信度过低

```yaml
# 情况
phys_chem.reduction_tendency.confidence: "low"

# 处理方式
elechem_output:
  warnings: ["上游 LUMO 分析置信度低，SEI 路径预测不确定"]
  overall_confidence: "low"
```

### 5.3 结构过于复杂

```yaml
# 情况
organic_chem.warnings: ["建议分段分析"]

# 处理方式
elechem_output:
  warnings: ["结构复杂，建议拆分为子结构分析"]
  notes: "聚合物/低聚物等复杂结构需简化处理"
```

---

## 6. 最佳实践

### 6.1 推荐流程

1. **始终先调用 OrganicChem**：获取结构化的分子描述
2. **然后调用 PhysChem**：获取 HOMO/LUMO 分析
3. **最后调用 EleChem**：进行电化学机理分析
4. **传递完整上游输出**：不要省略字段

### 6.2 上下文设置建议

| 场景 | context 设置 |
|------|-------------|
| 评估负极稳定性 | `electrode: "anode"`, `voltage_range: "deep_reduction"` |
| 评估高压正极稳定性 | `electrode: "cathode"`, `voltage_range: "high"` |
| 评估 LHCE 体系 | `electrolyte_system: "LHCE"` |
| 全面评估 | `electrode: "both"`, `voltage_range: "normal"` |

### 6.3 性能优化

- **缓存上游结果**：同一分子的 OrganicChem/PhysChem 输出可复用
- **按需调用模块**：若只关心 SEI，可只调用 `sei_pathway`
- **批量处理**：多个分子可并行调用上游模块

---

## 7. FAQ

### Q1: 必须同时有 OrganicChem 和 PhysChem 输出吗？

**A**: 是的，EleChem 依赖两者的输出。
- OrganicChem 提供结构特征
- PhysChem 提供 HOMO/LUMO 分析
- 缺少任一会导致分析不完整

### Q2: 可以直接给 EleChem 提供官能团列表吗？

**A**: 可以在 `molecule.functional_groups` 中提供，但：
- 仍需要 PhysChem 的 HOMO/LUMO 输出
- 建议通过 OrganicChem 获取完整结构分析

### Q3: CEI 和 SEI 分析可以分开进行吗？

**A**: 可以。使用 `task_type`:
- `sei_pathway`：仅 SEI 分析
- `cei_risk`：仅 CEI 分析
- `full_assessment`：完整分析

### Q4: 如何处理新型分子（无经验参考）？

**A**: 
- 降低输出置信度
- 在 `warnings` 中标注"缺乏实验验证"
- 建议通过 DFT 计算或实验验证

---

## 8. 版本兼容性

| EleChem 版本 | OrganicChem 版本 | PhysChem 版本 | 兼容性 |
|-------------|-----------------|--------------|--------|
| 1.0 | 1.0 | 1.0 | 完全兼容 |

---

## 9. Changelog

- 2025-12-25: 初始版本


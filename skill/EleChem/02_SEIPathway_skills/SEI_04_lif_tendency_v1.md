# SEI_04_lif_tendency_v1 — LiF 倾向

## Triggers
- 需要评估分子还原时释放 F⁻ 形成 LiF 的倾向
- 分子含有 C-F 键或其他可释放 F 的结构
- 需要预测 LiF 富集型 SEI 的可能性

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团（C-F）、敏感位点
- 上游 PhysChem 输出：LUMO 排序（σ*(C-F) 位置）
- 电极条件（可选）：电位范围

## Requires (Cross-Domain Queries)
本技能在执行过程中可能需要动态调用以下跨域查询：

| Query ID | 来源域 | 用途 |
|----------|--------|------|
| `OC.adjacent_groups` | OrganicChem | 判断 C-F 键邻近的官能团 |
| `PC.ewg_strength` | PhysChem | 评估邻近基团的吸电子强度 |
| `PC.bond_activation` | PhysChem | 评估 C-F 键的活化程度 |

**调用时机**：当上游输出不足以判断 C-F 键环境时，主动发起查询。

## Provides (Hub Query Interface)
本技能可对外提供以下查询能力：

| Query ID | 描述 |
|----------|------|
| `EC.lif_tendency` | 给定官能团/位点的 LiF 形成倾向 |

## Outputs
- `likelihood`: LiF 形成可能性（high / medium / low / none）
- `f_source`: F 来源描述
- `mechanism`: C-F 断裂机理
- `lif_contribution`: LiF 对 SEI 的贡献
- `byproducts_hint`: 可能的副产物
- `confidence`: 置信度

## Rules
### LiF 形成来源

**溶剂/添加剂中的 C-F 键**：
| 结构类型 | LiF 倾向 | 机理 |
|---------|---------|------|
| 氟代碳酸酯（FEC） | 高 | 还原时 C-F 断裂释放 F⁻ |
| 三氟甲基（CF₃） | 中 | 深度还原时可能断裂 |
| 氟代醚（BTFE 等） | 低-中 | 常规电位下稳定，极端电位可断裂 |
| 全氟化合物 | 低 | 高度稳定，难还原 |

**锂盐分解**（本卡不详细分析，但需知晓）：
- LiPF₆ → LiF + PF₅（水解/热分解）
- LiFSI/LiTFSI → LiF（电化学分解）

### C-F 键还原难易
| C-F 环境 | 还原难度 | 说明 |
|---------|---------|------|
| C(F)-C=O 邻近羰基 | 较易 | 吸电子基活化 C-F |
| CF₃ 三氟甲基 | 中等 | 多 F 有一定稳定性 |
| C-F 远离吸电子基 | 较难 | 需更低电位 |
| 全氟烷基 | 难 | 高度稳定 |

### LiF 对 SEI 的贡献
| 特性 | 描述 |
|-----|------|
| 离子电导率 | 高（Li⁺ 传输好） |
| 机械强度 | 高（硬度大） |
| 化学稳定性 | 优异（惰性） |
| 电子绝缘性 | 好（阻止电子泄漏） |

### LiF 富集 SEI 的优势
- 提高 SEI 的离子电导率
- 增强机械强度，抑制锂枝晶
- 提高化学稳定性
- 与聚合物复合形成优质 SEI

## Steps
1. **识别 F 来源**
   - 检查 C-F 键存在
   - 判断 C-F 键环境（邻近吸电子基？）
   
   ```yaml
   # 若上游输出不充分，发起跨域查询
   cross_domain_query:
     type: "OC.adjacent_groups"
     params:
       smiles: "${input.smiles}"
       target_atom: ${cf_bond.f_atom}
       radius: 2
   # 获取邻近官能团列表
   ```

2. **评估 C-F 断裂活性**
   - 结合 PhysChem 的 σ*(C-F) 能级
   - 与还原电位比较
   
   ```yaml
   # 查询邻近基团的吸电子效应强度
   cross_domain_query:
     type: "PC.ewg_strength"
     params:
       smiles: "${input.smiles}"
       substituent_atom: ${adjacent_ewg.atom_index}
       target_atom: ${cf_bond.c_atom}
   
   # 查询 C-F 键的活化程度
   cross_domain_query:
     type: "PC.bond_activation"
     params:
       smiles: "${input.smiles}"
       bond_atoms: [${cf_bond.f_atom}, ${cf_bond.c_atom}]
       activation_type: "reduction"
   ```

3. **判断 LiF 形成倾向**
   - 高：FEC 类、C-F 邻近羰基（EWG 活化）
   - 中：CF₃ 基团、氟代醚
   - 低：全氟化合物

4. **预测副产物**
   - C-F 断裂后的碳骨架去向

## Examples
**Example 1: FEC（高 LiF 倾向）**
```yaml
input:
  smiles: "FC1COC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }, { fg_type: "C-F" }]
  phys_chem:
    reduction_tendency:
      red_sites_ranked:
        - { rank: 1, site: "羰基 C=O" }
        - { rank: 2, site: "C-F 键" }
        
output:
  likelihood: "high"
  f_source: "与环状碳酸酯相连的 C-F 键"
  mechanism: "还原开环过程中 C-F 断裂，释放 F⁻"
  lif_contribution: "形成 LiF 富集层，提高 SEI 离子电导率和机械强度"
  byproducts_hint: ["聚碳酸酯（脱氟后）", "碳自由基产物"]
  evidence:
    - "C-F 键邻近羰基，被活化"
    - "还原时 C-F σ* 轨道接受电子导致断裂"
    - "FEC 是著名的 LiF 形成添加剂"
  confidence: "high"
```

**Example 2: BTFE（低-中 LiF 倾向）**
```yaml
input:
  smiles: "FC(F)(F)COCC(F)(F)F"
  organic_chem:
    functional_groups: [{ fg_type: "ether" }, { fg_type: "C-F" }]
  phys_chem:
    reduction_tendency:
      notes: "CF₃ 基团在常规电位下稳定"
        
output:
  likelihood: "low"
  f_source: "CF₃ 基团中的 C-F 键"
  mechanism: "仅在极低电位下可能断裂"
  lif_contribution: "常规使用条件下贡献少量 LiF"
  byproducts_hint: ["CF₃ 自由基（若断裂）"]
  evidence:
    - "CF₃ 基团高度稳定"
    - "醚氧被 CF₃ 的 -I 效应削弱配位"
    - "主要作为惰性稀释剂，不积极参与成膜"
  confidence: "medium"
```

**Example 3: EC（无 LiF）**
```yaml
input:
  smiles: "C1COC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }]
        
output:
  likelihood: "none"
  f_source: null
  mechanism: null
  lif_contribution: null
  byproducts_hint: null
  evidence:
    - "不含 F，无法贡献 LiF"
  note: "LiF 可能来自锂盐（LiPF₆）分解，但非 EC 贡献"
  confidence: "high"
```

**Example 4: DFEC（二氟代碳酸酯，高 LiF）**
```yaml
input:
  smiles: "FC1(F)COC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }, { fg_type: "C-F" }]
        
output:
  likelihood: "high"
  f_source: "同一碳上的两个 C-F 键"
  mechanism: "还原时双 C-F 断裂，释放 2F⁻"
  lif_contribution: "比 FEC 更多的 LiF 贡献"
  byproducts_hint: ["碳酸乙烯酯类产物", "二碳自由基"]
  evidence:
    - "双 F 取代，更多 F 来源"
    - "还原活性高"
  confidence: "high"
```

## Guardrails
- 不预测 LiF 具体含量或分布
- 锂盐（LiPF₆、LiFSI）也贡献 LiF，本卡聚焦溶剂/添加剂贡献
- C-F 断裂可能产生 HF（与痕量水反应），有腐蚀风险
- 过多 LiF 可能增加 SEI 刚性，需与有机组分平衡
- 新型氟化物需实验验证

## Dependencies
- 上游：OrganicChem C-F 官能团识别
- 上游：PhysChem LUMO σ*(C-F) 分析
- 关联：SEI_01_pathway_flowmap_v1（整合 LiF 贡献）

## Changelog
- 2025-12-25: 初始版本


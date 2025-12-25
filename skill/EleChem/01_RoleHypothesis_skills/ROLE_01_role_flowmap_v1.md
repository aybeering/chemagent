# ROLE_01_role_flowmap_v1 — 角色假设总路由

## Triggers
- 需要判断分子在电解液体系中的可能角色
- 需要评估分子适合作为溶剂、添加剂、稀释剂还是不适合
- 作为 EleChem 角色假设模块的主入口被调用

## Inputs
- 分子表示：SMILES / 结构描述 / 官能团列表
- 上游 OrganicChem 输出：官能团、环系、杂原子特征
- 上游 PhysChem 输出：HOMO/LUMO 排序、电子效应
- 应用场景（可选）：常规电解液 / LHCE / 高压体系

## Outputs
- `primary_role`: 主要角色假设（solvent / film_additive / diluent / unsuitable）
- `confidence`: 置信度（high / medium / low）
- `evidence`: 支持该角色的结构证据列表
- `alternatives`: 备选角色及其适用条件
- `unsuitable_flags`: 不适合标记（若有）

## Rules
- **先判断不适合**：存在结构警示（如强毒性官能团、极端不稳定结构）时，优先标记为 unsuitable
- **根据结构特征匹配角色**：
  - 高介电常数 + 溶解锂盐能力 → 溶剂候选
  - 优先还原/氧化 + 成膜倾向 → 添加剂候选
  - 低配位 + 惰性 + 低粘度 → 稀释剂候选
- **允许多角色**：同一分子可能在不同体系中扮演不同角色
- **置信度基于证据数量和一致性**：证据越多越一致，置信度越高

## Steps
1. **接收上游输入**
   - 解析 OrganicChem 的官能团和结构特征
   - 解析 PhysChem 的 HOMO/LUMO 分析
   
2. **调用不适合标记** → `ROLE_05_unsuitable_flag_v1`
   - 若触发不适合标记，记录 flags 但继续评估其他角色可能性
   
3. **调用溶剂假设** → `ROLE_02_solvent_hypothesis_v1`
   - 评估作为主溶剂的适合度
   
4. **调用成膜添加剂假设** → `ROLE_03_film_additive_v1`
   - 评估作为 SEI/CEI 成膜添加剂的适合度
   
5. **调用稀释剂假设** → `ROLE_04_diluent_hypothesis_v1`
   - 评估作为 LHCE 稀释剂的适合度

6. **综合判定**
   - 比较各角色的适合度得分
   - 选择得分最高者作为 primary_role
   - 记录其他可能角色作为 alternatives
   - 综合置信度评估

## Examples
**Example 1: Ethylene Carbonate (EC)**
```yaml
input:
  smiles: "C1COC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }]
  phys_chem:
    reduction_tendency: { dominant_site: "羰基 C=O" }
    
output:
  primary_role: "solvent"
  confidence: "high"
  evidence:
    - "环状碳酸酯，高介电常数（~89）"
    - "可有效溶解锂盐"
    - "作为标准电解液主溶剂使用多年"
  alternatives:
    - role: "film_additive"
      confidence: "low"
      condition: "仅在特定低浓度配方中作为共溶剂"
  unsuitable_flags: []
```

**Example 2: Fluoroethylene Carbonate (FEC)**
```yaml
input:
  smiles: "FC1COC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }, { fg_type: "C-F" }]
  phys_chem:
    reduction_tendency: { dominant_site: "羰基 C=O" }
    
output:
  primary_role: "film_additive"
  confidence: "high"
  evidence:
    - "含 C-F 键，可释放 F⁻ 促进 LiF 形成"
    - "优先于 EC 还原，形成优质 SEI"
    - "典型使用量 <10%"
  alternatives:
    - role: "solvent"
      confidence: "low"
      condition: "高浓度使用时可作为共溶剂"
  unsuitable_flags: []
```

**Example 3: Bis(2,2,2-trifluoroethyl) ether (BTFE)**
```yaml
input:
  smiles: "FC(F)(F)COCC(F)(F)F"
  organic_chem:
    functional_groups: [{ fg_type: "ether" }, { fg_type: "C-F" }]
  phys_chem:
    reduction_tendency: { dominant_site: "C-F σ*（深度还原下）" }
    
output:
  primary_role: "diluent"
  confidence: "high"
  evidence:
    - "高氟化结构，低介电常数"
    - "弱 Li+ 配位能力"
    - "化学惰性，适合 LHCE 稀释"
  alternatives:
    - role: "film_additive"
      confidence: "low"
      condition: "在极低电位下 C-F 断裂可能贡献 LiF"
  unsuitable_flags: []
```

## Guardrails
- 不输出定量数据（介电常数具体数值、电导率等），除非上游提供
- 不直接判定"最佳"角色，只给出"适合度"和"证据"
- 遇到新型结构（无经验参考）时，降低置信度并标注
- unsuitable 标记不排除在特殊条件下的有限使用可能

## Dependencies
- `ROLE_02_solvent_hypothesis_v1`
- `ROLE_03_film_additive_v1`
- `ROLE_04_diluent_hypothesis_v1`
- `ROLE_05_unsuitable_flag_v1`
- 上游：`OrganicChem_Router`, `PhysChem_Router`

## Changelog
- 2025-12-25: 初始版本


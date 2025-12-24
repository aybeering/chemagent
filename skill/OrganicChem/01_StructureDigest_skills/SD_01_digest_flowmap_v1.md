# SD_01_digest_flowmap_v1 — 结构解剖总路由

## Triggers
- 需要对分子进行完整的结构解剖与标签化
- 需要获取骨架、官能团、杂原子、环系、共轭网络的综合信息
- 作为 OrganicChem 模块的主入口被调用

## Inputs
- 分子表示：SMILES / 结构描述 / 分子名称
- 解析深度（可选）：`basic`（仅骨架+官能团）/ `full`（全部子卡）
- 关注区域（可选）：特定原子索引列表

## Outputs
- `skeleton`: 骨架信息（类型/主链/环数）
- `functional_groups`: 官能团列表（类型/位置/中心原子）
- `heteroatom_labels`: 杂原子标签（杂化/孤对/电荷）
- `ring_info`: 环系信息（大小/芳香性/张力）
- `conjugation_map`: 共轭网络映射（π 系统/范围）
- `digest_summary`: 结构特征摘要

## Rules
- **先验证输入有效性**：SMILES 必须可解析，否则尝试从名称/描述推断
- **按依赖顺序执行子卡**：骨架 → 官能团 → 杂原子 → 环系 → 共轭
- **避免重复计算**：环系信息可复用于共轭分析
- **置信度传递**：若某子卡置信度低，需在 summary 中标注

## Steps
1. **验证输入**
   - 解析 SMILES，标准化为 canonical 形式
   - 若解析失败，尝试从 name/description 推断结构
   
2. **调用骨架识别** → `SD_02_skeleton_parse_v1`
   - 获取骨架类型、主链长度、环标识符
   
3. **调用官能团识别** → `SD_03_functional_group_v1`
   - 识别所有官能团，分类并标记位置
   
4. **调用杂原子标签** → `SD_04_heteroatom_label_v1`
   - 标记杂原子的杂化、孤对、电荷状态
   
5. **调用环系分析** → `SD_05_ring_system_v1`
   - 分析环的大小、芳香性、张力、稠合关系
   
6. **调用共轭网络映射** → `SD_06_conjugation_map_v1`
   - 识别 π 系统范围和共轭路径

7. **汇总输出**
   - 整合各子卡结果
   - 生成结构特征摘要
   - 计算总体置信度（取各子卡最低值）

## Examples
**Example 1: Ethylene Carbonate**
```yaml
input:
  smiles: "C1COC(=O)O1"
  
output:
  skeleton: { type: "cyclic", ring_count: 1 }
  functional_groups: [{ fg_type: "cyclic_carbonate", center: 2 }]
  heteroatom_labels: [{ atom: 3, element: "O", hybridization: "sp3", lone_pairs: 2 }]
  ring_info: [{ size: 5, aromatic: false, strain: "low" }]
  conjugation_map: { pi_systems: [{ atoms: [2,4], type: "carbonyl" }] }
  digest_summary: "五元环状碳酸酯，含羰基和两个醚氧"
```

**Example 2: Benzaldehyde**
```yaml
input:
  smiles: "c1ccccc1C=O"
  
output:
  skeleton: { type: "cyclic", ring_count: 1 }
  functional_groups: [{ fg_type: "aldehyde" }, { fg_type: "benzene" }]
  ring_info: [{ size: 6, aromatic: true, strain: "none" }]
  conjugation_map: { pi_systems: [{ atoms: [0-6,7], type: "extended", extent: "aromatic+carbonyl" }] }
```

## Guardrails
- 不猜测 SMILES 无法解析的结构细节
- 不输出定量数据（能量、pKa 等）
- 遇到极复杂结构（>100 原子）时，在 warnings 中标注"建议分段分析"
- 若存在互变异构或构象不确定性，降低置信度并标注

## Dependencies
- `SD_02_skeleton_parse_v1`
- `SD_03_functional_group_v1`
- `SD_04_heteroatom_label_v1`
- `SD_05_ring_system_v1`
- `SD_06_conjugation_map_v1`

## Changelog
- 2025-12-24: 初始版本


# SD_02_skeleton_parse_v1 — 骨架识别

## Triggers
- 需要确定分子的基本骨架类型（线性/支链/环状/多环/桥接）
- 需要识别主链、支链和环系结构
- 作为结构解剖流程的第一步

## Inputs
- 分子表示：SMILES / 结构描述
- 关注类型（可选）：`carbon_skeleton` / `full_skeleton`（含杂原子）

## Outputs
```yaml
skeleton:
  type: "linear | branched | cyclic | polycyclic | bridged | spiro"
  main_chain_length: <int>          # 最长碳链原子数
  branch_count: <int>               # 支链数量
  ring_count: <int>                 # 环数量
  ring_ids: ["RING_1", "RING_2"]    # 环标识符列表
  bridgehead_atoms: [<int>]         # 桥头原子索引
  spiro_centers: [<int>]            # 螺原子索引
  complexity: "simple | moderate | complex"
```

## Rules

### 骨架类型判定规则

| 条件 | 类型 |
|------|------|
| 无环，无分支 | `linear` |
| 无环，有分支 | `branched` |
| 单环 | `cyclic` |
| 多环，共享边/稠合 | `polycyclic` |
| 多环，共享原子（桥头） | `bridged` |
| 多环，仅共享单个原子 | `spiro` |

### 主链识别规则
1. 找出最长碳链（按 IUPAC 命名规则）
2. 若有环，环系优先作为"主体"，链作为取代基
3. 杂原子（N、O、S）可计入骨架，但单独标记

### 环系编号规则
- 每个独立环分配唯一 `ring_id`
- 稠合环标记 `fusion_type: fused`
- 桥环标记桥头原子

## Steps
1. **解析分子图**
   - 从 SMILES 构建原子-键连接图
   
2. **检测环**
   - 使用最小环检测算法
   - 识别稠合、桥接、螺环关系
   
3. **识别主链**
   - 对于无环分子：找最长碳链
   - 对于含环分子：确定环系主体
   
4. **标记支链**
   - 统计分支点和支链长度
   
5. **输出骨架描述**

## Examples

**Example 1: Ethane (线性)**
```yaml
input: "CC"
output:
  skeleton:
    type: "linear"
    main_chain_length: 2
    branch_count: 0
    ring_count: 0
    complexity: "simple"
```

**Example 2: Isobutane (支链)**
```yaml
input: "CC(C)C"
output:
  skeleton:
    type: "branched"
    main_chain_length: 3
    branch_count: 1
    ring_count: 0
    complexity: "simple"
```

**Example 3: Cyclohexane (单环)**
```yaml
input: "C1CCCCC1"
output:
  skeleton:
    type: "cyclic"
    main_chain_length: 0
    ring_count: 1
    ring_ids: ["RING_1"]
    complexity: "simple"
```

**Example 4: Decalin (稠合双环)**
```yaml
input: "C1CCC2CCCCC2C1"
output:
  skeleton:
    type: "polycyclic"
    ring_count: 2
    ring_ids: ["RING_1", "RING_2"]
    fusion_atoms: [4, 9]
    complexity: "moderate"
```

**Example 5: Norbornane (桥环)**
```yaml
input: "C1CC2CCC1C2"
output:
  skeleton:
    type: "bridged"
    ring_count: 2
    ring_ids: ["RING_1", "RING_2"]
    bridgehead_atoms: [0, 3]
    complexity: "moderate"
```

**Example 6: Spiro[4.5]decane (螺环)**
```yaml
input: "C1CCC2(CC1)CCCCC2"
output:
  skeleton:
    type: "spiro"
    ring_count: 2
    ring_ids: ["RING_1", "RING_2"]
    spiro_centers: [3]
    complexity: "moderate"
```

## Guardrails
- 不处理无法解析的 SMILES
- 对于超大分子（>200 原子），标记 complexity: "complex" 并警告
- 不推断三维构象信息
- 金属有机化合物需单独标记

## Confusable Cases
- 稠合 vs 桥接：稠合共享边，桥接共享两个不相邻原子
- 螺环 vs 桥接：螺环只共享单个原子
- 大环 vs 链状：需检查首尾是否相连

## Changelog
- 2025-12-24: 初始版本


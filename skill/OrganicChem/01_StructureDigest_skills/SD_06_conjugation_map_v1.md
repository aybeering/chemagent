# SD_06_conjugation_map_v1 — 共轭网络映射

## Triggers
- 需要识别分子中的 π 共轭系统
- 需要确定共轭范围和类型
- 为 PhysChem 的电子效应分析提供共轭信息

## Inputs
- 分子表示：SMILES / 结构描述
- 环系信息（可选）：来自 SD_05 的 ring_info
- 官能团信息（可选）：来自 SD_03 的 functional_groups

## Outputs
```yaml
conjugation_map:
  pi_systems:
    - system_id: "PI_1"
      atoms: [<原子索引>]
      bonds: [<键索引>]
      extent: "local | extended | aromatic"
      type: "alkene | alkyne | carbonyl | imine | aromatic | heterocyclic | extended"
      electron_count: <int>           # π 电子数
      delocalization: "full | partial | none"
  
  cross_conjugated: true | false      # 是否存在交叉共轭
  
  conjugation_paths:
    - path_id: "PATH_1"
      atoms: [<原子索引>]
      length: <int>                   # 共轭原子数
      type: "linear | branched | cyclic"
  
  total_pi_electrons: <int>
  dominant_system: "PI_1"             # 最重要的 π 系统
```

## Rules

### 共轭类型判定

| 类型 | 特征 | 示例 |
|------|------|------|
| isolated | 单个双/三键，无相邻不饱和 | 丙烯 |
| extended | 交替单双键连续 | 1,3-丁二烯 |
| aromatic | 环状共轭，满足 Hückel | 苯 |
| cross-conjugated | 共轭分叉 | 交叉共轭烯烃 |
| through-space | π-π 堆积 | 层状芳环 |

### π 电子计数规则

| 结构单元 | π 电子贡献 |
|----------|-----------|
| C=C | 2 |
| C≡C | 4 (两个正交 π 键) |
| C=O | 2 |
| C=N | 2 |
| 芳香 C (苯) | 1 (每个原子贡献) |
| 吡咯型 N | 2 (孤对参与) |
| 吡啶型 N | 1 |
| 呋喃型 O | 2 |

### 共轭连续性判定

共轭**连续**的条件：
1. 相邻 π 系统之间仅隔一个单键
2. 该单键两端的原子都是 sp² 杂化
3. 几何上允许轨道重叠（近似共面）

共轭**中断**的条件：
1. sp³ 碳插入
2. 显著的扭转角（>40°）
3. 多个单键间隔

### 离域程度

| delocalization | 条件 |
|----------------|------|
| full | 芳香环，共振结构等效 |
| partial | 推拉电子体系，共振不等效 |
| none | 孤立双键 |

## Steps
1. **识别所有 π 键**
   - 双键、三键、芳香环
   
2. **追踪共轭连接**
   - 从每个 π 键出发，检查相邻是否共轭连续
   
3. **分组 π 系统**
   - 连通的共轭区域归为一组
   
4. **计算 π 电子数**
   - 按规则累加
   
5. **判定共轭类型**
   - 线性、交叉、环状
   
6. **确定离域程度**
   - 分析共振结构等效性

## Examples

**Example 1: 1,3-丁二烯**
```yaml
input: "C=CC=C"
output:
  conjugation_map:
    pi_systems:
      - system_id: "PI_1"
        atoms: [0, 1, 2, 3]
        extent: "extended"
        type: "extended"
        electron_count: 4
        delocalization: "partial"
    cross_conjugated: false
    total_pi_electrons: 4
```

**Example 2: 苯**
```yaml
input: "c1ccccc1"
output:
  conjugation_map:
    pi_systems:
      - system_id: "PI_1"
        atoms: [0, 1, 2, 3, 4, 5]
        extent: "aromatic"
        type: "aromatic"
        electron_count: 6
        delocalization: "full"
    cross_conjugated: false
    total_pi_electrons: 6
    dominant_system: "PI_1"
```

**Example 3: 苯甲醛**
```yaml
input: "c1ccccc1C=O"
output:
  conjugation_map:
    pi_systems:
      - system_id: "PI_1"
        atoms: [0, 1, 2, 3, 4, 5, 6, 7]
        extent: "extended"
        type: "extended"
        electron_count: 8
        delocalization: "partial"
        notes: "芳环与羰基共轭"
    cross_conjugated: false
    total_pi_electrons: 8
    dominant_system: "PI_1"
```

**Example 4: 对硝基苯甲醚（推拉电子体系）**
```yaml
input: "COc1ccc([N+](=O)[O-])cc1"
output:
  conjugation_map:
    pi_systems:
      - system_id: "PI_1"
        atoms: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        extent: "extended"
        type: "extended"
        electron_count: 10
        delocalization: "partial"
        notes: "典型推拉电子体系：OMe(+M) ←芳环→ NO2(-M)"
    cross_conjugated: false
    total_pi_electrons: 10
    conjugation_paths:
      - path_id: "PATH_1"
        atoms: [1, 2, 5, 6, 7]
        length: 5
        type: "linear"
        notes: "OMe 到 NO2 的主共轭路径"
```

**Example 5: 交叉共轭（二苯甲酮）**
```yaml
input: "c1ccccc1C(=O)c2ccccc2"
output:
  conjugation_map:
    pi_systems:
      - system_id: "PI_1"
        atoms: [0, 1, 2, 3, 4, 5]
        extent: "aromatic"
        type: "aromatic"
        electron_count: 6
      - system_id: "PI_2"
        atoms: [6, 7]
        extent: "local"
        type: "carbonyl"
        electron_count: 2
      - system_id: "PI_3"
        atoms: [8, 9, 10, 11, 12, 13]
        extent: "aromatic"
        type: "aromatic"
        electron_count: 6
    cross_conjugated: true
    total_pi_electrons: 14
    notes: "羰基与两个苯环交叉共轭"
```

**Example 6: 丙酮（孤立羰基）**
```yaml
input: "CC(=O)C"
output:
  conjugation_map:
    pi_systems:
      - system_id: "PI_1"
        atoms: [1, 2]
        extent: "local"
        type: "carbonyl"
        electron_count: 2
        delocalization: "none"
    cross_conjugated: false
    total_pi_electrons: 2
    notes: "孤立羰基，两侧为 sp3 碳，无共轭延伸"
```

## Guardrails
- 不预测具体的电子效应强度（交给 PhysChem）
- 对于极长共轭链（>20 原子），标注"扩展共轭体系"
- 不处理 σ 共轭（超共轭由 PhysChem ELEC 模块处理）
- 构象灵活分子需标注"共轭程度取决于构象"

## Confusable Cases
- 交叉共轭 vs 线性共轭：交叉共轭不允许完全离域
- 芳香 vs 非芳香共轭环：检查 Hückel 规则
- 累积双键 (allene) vs 共轭双键：累积双键不是共轭

## Changelog
- 2025-12-24: 初始版本


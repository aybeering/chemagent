# SD_03_functional_group_v1 — 官能团识别与分类

## Triggers
- 需要识别分子中的官能团
- 需要对官能团进行分类和定位
- 需要为后续 PhysChem 分析提供官能团信息

## Inputs
- 分子表示：SMILES / 结构描述
- 识别范围（可选）：`all` / `primary_only`（仅主要官能团）

## Outputs
```yaml
functional_groups:
  - fg_id: "FG_1"
    fg_type: "<官能团类型>"
    fg_category: "carbonyl | nitrogen | oxygen | halogen | sulfur | phosphorus | unsaturated | other"
    atoms: [<原子索引列表>]
    center_atom: <中心原子索引>
    subtype: "<子类型>"
    priority: <int>            # 优先级，用于确定主要官能团
    smarts: "<匹配的 SMARTS>"
```

## Rules

### 官能团优先级（高 → 低）

| 优先级 | 官能团类别 | 示例 |
|--------|-----------|------|
| 1 | 羧酸及衍生物 | -COOH, -COO-, -CONH2, -COCl |
| 2 | 醛酮 | -CHO, >C=O |
| 3 | 腈/异腈 | -C≡N, -N≡C |
| 4 | 硝基/亚硝基 | -NO2, -N=O |
| 5 | 胺/酰胺 | -NH2, -CONH2 |
| 6 | 醇/酚/醚 | -OH, Ar-OH, -O- |
| 7 | 硫醇/硫醚 | -SH, -S- |
| 8 | 卤代物 | -F, -Cl, -Br, -I |
| 9 | 不饱和烃 | C=C, C≡C, 芳环 |
| 10 | 其他 | 磷酸酯等 |

### 官能团识别规则表

| 官能团 | SMARTS 模式 | fg_category | 子类型说明 |
|--------|-------------|-------------|-----------|
| 羧酸 | `[CX3](=O)[OX2H1]` | carbonyl | carboxylic_acid |
| 酯 | `[CX3](=O)[OX2][C]` | carbonyl | ester, lactone(环), carbonate |
| 酰胺 | `[CX3](=O)[NX3]` | carbonyl | amide, lactam(环) |
| 酸酐 | `[CX3](=O)[OX2][CX3](=O)` | carbonyl | anhydride |
| 酰卤 | `[CX3](=O)[F,Cl,Br,I]` | carbonyl | acyl_halide |
| 醛 | `[CX3H1](=O)` | carbonyl | aldehyde |
| 酮 | `[CX3](=O)([C])[C]` | carbonyl | ketone |
| 伯醇 | `[CX4][OX2H]` | oxygen | primary_alcohol |
| 仲醇 | `[CX4H1][OX2H]` | oxygen | secondary_alcohol |
| 叔醇 | `[CX4H0][OX2H]` | oxygen | tertiary_alcohol |
| 酚 | `[c][OX2H]` | oxygen | phenol |
| 醚 | `[OX2]([C])[C]` | oxygen | ether |
| 环氧 | `[OX2r3]` | oxygen | epoxide |
| 伯胺 | `[NX3H2][C]` | nitrogen | primary_amine |
| 仲胺 | `[NX3H1]([C])[C]` | nitrogen | secondary_amine |
| 叔胺 | `[NX3H0]([C])([C])[C]` | nitrogen | tertiary_amine |
| 腈 | `[CX2]#[NX1]` | nitrogen | nitrile |
| 硝基 | `[NX3+](=O)[O-]` | nitrogen | nitro |
| 氟代 | `[C][F]` | halogen | C-F |
| 氯代 | `[C][Cl]` | halogen | C-Cl |
| 溴代 | `[C][Br]` | halogen | C-Br |
| 碘代 | `[C][I]` | halogen | C-I |
| 硫醇 | `[SX2H]` | sulfur | thiol |
| 硫醚 | `[SX2]([C])[C]` | sulfur | thioether |
| 磺酸 | `[SX4](=O)(=O)[O]` | sulfur | sulfonic_acid |
| 烯烃 | `[CX3]=[CX3]` | unsaturated | alkene |
| 炔烃 | `[CX2]#[CX2]` | unsaturated | alkyne |
| 苯环 | `[c]1[c][c][c][c][c]1` | unsaturated | benzene |

### 分类逻辑

1. **避免重复计数**：如羧酸 = 羰基 + 羟基，只报告"羧酸"
2. **层级关系**：环状碳酸酯 > 酯 > 醚，只报告最具体的
3. **共享原子处理**：一个原子可属于多个官能团时，标记 `shared: true`

## Steps
1. **SMARTS 模式匹配**
   - 按优先级顺序匹配官能团
   - 记录匹配的原子索引
   
2. **去重与层级化**
   - 若高优先级官能团包含低优先级官能团，只保留高优先级
   
3. **确定中心原子**
   - 羰基类：C=O 的碳
   - 胺类：氮原子
   - 卤代物：碳原子
   
4. **输出排序**
   - 按优先级排序
   - 同优先级按出现顺序

## Examples

**Example 1: 乙酸乙酯**
```yaml
input: "CCOC(=O)C"
output:
  functional_groups:
    - fg_id: "FG_1"
      fg_type: "ester"
      fg_category: "carbonyl"
      atoms: [2, 3, 4, 5]
      center_atom: 4
      subtype: "ethyl_ester"
      priority: 1
```

**Example 2: 对氨基苯甲酸**
```yaml
input: "Nc1ccc(C(=O)O)cc1"
output:
  functional_groups:
    - fg_id: "FG_1"
      fg_type: "carboxylic_acid"
      fg_category: "carbonyl"
      atoms: [7, 8, 9]
      center_atom: 7
      priority: 1
    - fg_id: "FG_2"
      fg_type: "primary_amine"
      fg_category: "nitrogen"
      atoms: [0]
      center_atom: 0
      priority: 5
    - fg_id: "FG_3"
      fg_type: "benzene"
      fg_category: "unsaturated"
      atoms: [1, 2, 3, 4, 5, 6]
      priority: 9
```

**Example 3: 氟代碳酸乙烯酯 (FEC)**
```yaml
input: "FC1COC(=O)O1"
output:
  functional_groups:
    - fg_id: "FG_1"
      fg_type: "cyclic_carbonate"
      fg_category: "carbonyl"
      atoms: [2, 3, 4, 5, 6]
      center_atom: 4
      subtype: "5-membered_cyclic_carbonate"
      priority: 1
    - fg_id: "FG_2"
      fg_type: "C-F"
      fg_category: "halogen"
      atoms: [0, 1]
      center_atom: 1
      priority: 8
```

## Guardrails
- 不识别非标准/罕见官能团，除非明确提供 SMARTS
- 对于高度取代的官能团，保持基本分类而非过度细分
- 不预测官能团的反应性（交给 ReactiveHotspots）
- 聚合物/高分子标记为"重复单元"而非枚举所有官能团

## Confusable Cases
- 酰胺 vs 胺 + 羰基：优先识别为酰胺
- 酯 vs 醚 + 羰基：优先识别为酯
- 环状碳酸酯 vs 酯 + 醚：优先识别为环状碳酸酯
- 硝基 vs 亚硝基：检查氧化态

## Changelog
- 2025-12-24: 初始版本


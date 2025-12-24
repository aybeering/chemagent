# HOMO_02_lonepair_n_v1 — 杂原子孤对电子 (n 轨道) 的 HOMO 贡献评估

## Triggers
- 分子含有杂原子（N/O/S/P 等），需评估其孤对电子对 HOMO 的贡献
- 需要判断"这个胺/醚/硫醚容易被氧化吗"
- 需要比较不同杂原子位点的氧化倾向

## Inputs
- 杂原子类型与化学环境：
  - N：胺（一/二/三级）、酰胺、腈、吡啶型、苯胺型
  - O：醇、醚、羰基氧、酯氧、羧酸
  - S：硫醚、硫醇、亚砜、磺酰基
  - P：膦、磷酸酯
- 相邻取代基信息
- 是否参与共轭（可选）
- 是否有氢键/配位（可选）

## Outputs
- `lonepair_homo_level`: 孤对 HOMO 贡献等级（very_high / high / medium / low / very_low）
- `heteroatom_ranking`: 同一分子内多个杂原子的 HOMO 排序
- `conjugation_effect`: 共轭对孤对能级的影响（lowered / neutral / raised）
- `substituent_effect`: 取代基对孤对能级的调制方向（↑ / → / ↓）
- `ox_susceptibility`: 该位点的氧化敏感性评估

## Rules

### 杂原子孤对 HOMO 基础排序（无取代基调制时）
```
高 HOMO ──────────────────────────────────────────► 低 HOMO

脂肪胺 N > 芳香胺 N > 硫醚 S > 醚 O > 硫醇 S-H 
        > 酰胺 N > 吡啶 N > 羰基 O > 腈 N > 亚砜 S
```

### 共轭效应对孤对的影响
- **孤对参与共轭 → HOMO 降低**：酰胺 N（nN→π*C=O 离域）、苯胺 N（n→芳环）
- **共轭程度越强 → 降低越多**：完全共面时效应最大
- **扭转/位阻 → 共轭减弱 → HOMO 回升**

### 取代基调制（需调用 HOMO_05）
- **给电子基 (+M/+I)** → 孤对 HOMO ↑ → 更易氧化
- **吸电子基 (-M/-I)** → 孤对 HOMO ↓ → 更难氧化
- **典型强影响**：季铵化 (N→N⁺) 使孤对消失；质子化使 HOMO 大幅下降

### 氢键/配位效应
- **作为氢键供体**：孤对部分"被占用"，氧化倾向可能略降
- **与金属配位**：孤对能级显著改变，需特殊处理

## Steps
1. 识别分子中所有杂原子及其化学环境（胺/醚/硫醚/酰胺等）。
2. 判断每个孤对是否参与共轭：
   - 是 → 标记 `conjugation_effect: lowered`
   - 否 → 标记 `conjugation_effect: neutral`
3. 应用基础排序规则，给出初始 HOMO 等级。
4. 调用 `HOMO_05_substituent_mod_v1` 获取取代基调制：
   - 汇总邻近取代基的电子效应
   - 调整 HOMO 等级
5. 输出各孤对位点的 HOMO 贡献与氧化敏感性评估。

## Examples

### Example 1: 三乙胺 (Et₃N)
```
输入: SMILES = "CCN(CC)CC"

分析:
- 杂原子: 叔胺 N
- 共轭: 无（饱和碳连接）
- 取代基: 乙基（弱 +I）

输出:
  lonepair_homo_level: "very_high"
  conjugation_effect: "neutral"
  substituent_effect: "↑ (弱)"
  ox_susceptibility: "高度敏感，是分子中最易氧化位点"
```

### Example 2: N-甲基吡咯烷酮 (NMP)
```
输入: SMILES = "CN1CCCC1=O"

分析:
- 杂原子: 酰胺 N、羰基 O
- 共轭: N 的孤对与 C=O 共轭
- 取代基: N-甲基（弱 +I），环状结构

输出:
  lonepair_homo_level: 
    酰胺N: "medium"（共轭降低）
    羰基O: "low"
  conjugation_effect: "lowered"
  heteroatom_ranking: [酰胺N, 羰基O]
  ox_susceptibility: "中等敏感；共轭使 N 孤对 HOMO 显著低于脂肪胺"
```

### Example 3: 二甲基亚砜 (DMSO)
```
输入: SMILES = "CS(C)=O"

分析:
- 杂原子: 亚砜 S、亚砜 O
- 共轭: S=O 极化
- 取代基: 甲基（弱 +I）

输出:
  lonepair_homo_level:
    亚砜S: "low"（已被氧化一次）
    亚砜O: "very_low"
  ox_susceptibility: "低敏感；S 已处于中间氧化态，进一步氧化需更强条件"
```

## Guardrails
- **不混淆杂原子类型**：必须区分胺 vs 酰胺、醚 vs 醇、硫醚 vs 亚砜。
- **共轭判断需结合构象**：平面性不足时，共轭效应需降权（可调用 ELEC_06）。
- **不输出氧化电位**：只给定性等级，不给数值。
- **质子化/离子化状态**：明确标注，因其对孤对 HOMO 影响极大。
- **多孤对分子**：必须分别评估并排序，不能笼统地说"杂原子可被氧化"。


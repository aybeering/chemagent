# LUMO_04_ring_strain_v1 — 环张力/小环体系的还原敏感性评估

## Triggers
- 分子含有小环或高应变结构（环氧/环丙烷/环丁烷/桥环），需评估其还原敏感性
- 需要判断"这个环氧/小环容易被还原开环吗"
- 分析应变释放驱动的还原反应

## Inputs
- 环体系类型与结构：
  - 三元环：环氧、环丙烷、氮丙啶、环硫乙烷
  - 四元环：环丁烷、β-内酯、β-内酰胺
  - 桥环/笼状：降冰片烷、立方烷
  - 稠环应变：反式稠合、角张力
- 环上取代基信息
- 杂原子位置与类型

## Outputs
- `strain_level`: 环张力等级（very_high / high / medium / low）
- `ring_opening_tendency`: 开环倾向（high / medium / low）
- `strain_release_energy`: 应变释放能估计（定性：large / moderate / small）
- `preferred_cleavage_site`: 优先断裂位置
- `red_susceptibility`: 该环体系的还原开环敏感性评估

## Rules

### 环张力基础排序
```
高张力 ──────────────────────────────────────────► 低张力
（易开环）                                        （难开环）

环丙烷 ≈ 环氧 > 氮丙啶 > 环丁烷 > β-内酯 > 环戊烷 ≈ 无张力
```

### 典型环系张力能（定性参考）

| 环类型 | 张力能 | 还原开环倾向 | 主要驱动力 |
|--------|--------|--------------|------------|
| 环丙烷 | very_high (~27 kcal/mol) | 高 | 角张力 + σ* 低化 |
| 环氧 | very_high (~27 kcal/mol) | 很高 | 角张力 + 杂原子 σ* |
| 氮丙啶 | high (~26 kcal/mol) | 高 | 角张力 |
| 环硫乙烷 | high (~20 kcal/mol) | 高 | 角张力 + S 易离去 |
| 环丁烷 | medium (~26 kcal/mol) | 中等 | 扭转张力 |
| β-内酯 | medium | 中-高 | 张力 + 羰基活化 |
| 环戊烷 | low (~6 kcal/mol) | 低 | 接近无张力 |
| 环己烷 | very_low (~0) | 很低 | 无张力 |

### 杂原子对开环的影响
- **环氧 (O)**：C-O σ* 低，氧是中等离去基 → 高还原敏感
- **氮丙啶 (N)**：C-N σ* 中等，氮胺离去较差 → 中-高敏感
- **环硫乙烷 (S)**：C-S σ* 低，硫是好离去基 → 高敏感
- **环丙烷 (全C)**：需更强还原条件，但张力释放大

### 取代基调制
- **吸电子取代**：稳定开环后形成的阴离子 → 开环更易
- **给电子取代**：可能稳定环系 → 开环略难
- **立体因素**：取代基可能影响开环位置选择性

### 开环位置选择性
- **电子控制**：电子云较贫的碳更易被亲核进攻
- **位阻控制**：位阻小的位置更易开环
- **还原条件**：电子直接注入通常在张力最大处

## Steps
1. 识别分子中所有小环/应变环体系。
2. 分类环类型（三元/四元/桥环）与杂原子。
3. 评估环张力等级。
4. 判断优先断裂位置：
   - 杂原子环：通常在 C-杂原子键断裂
   - 全碳环：在张力最大处或取代最少处
5. 考虑取代基调制。
6. 输出开环倾向与还原敏感性评估。

## Examples

### Example 1: 环氧乙烷
```
输入: SMILES = "C1CO1"

分析:
- 环类型: 三元环氧
- 杂原子: O（中等离去基）
- 张力: very_high

输出:
  strain_level: "very_high"
  ring_opening_tendency: "very_high"
  preferred_cleavage_site: "任一 C-O 键（对称）"
  red_susceptibility: "极高敏感；环氧是典型的还原开环底物"
```

### Example 2: 碳酸乙烯酯 (EC)
```
输入: SMILES = "C1COC(=O)O1"

分析:
- 环类型: 五元环（碳酸酯）
- 张力: low-medium（五元环接近无张力）
- 竞争: 羰基 π* vs 环张力

输出:
  strain_level: "low"
  ring_opening_tendency: "medium"（主要由羰基还原驱动）
  preferred_cleavage_site: "羰基还原后 C-O 断裂"
  red_susceptibility: "还原开环主要由羰基 π* 驱动，非张力驱动"
  notes: "五元碳酸酯环张力弱；还原优先在羰基"
```

### Example 3: 环丙基甲基酮
```
输入: SMILES = "CC(=O)C1CC1"

分析:
- 环类型: 三元环丙烷
- 相邻官能团: 羰基（共轭可能）
- 张力: very_high

输出:
  strain_level: "very_high"
  ring_opening_tendency: "high"
  preferred_cleavage_site: "与羰基相邻的 C-C 键（共轭稳定）"
  red_susceptibility: "高敏感；羰基 + 环丙烷可能协同活化"
```

### Example 4: β-丙内酯
```
输入: SMILES = "C1CC(=O)O1"

分析:
- 环类型: 四元环 β-内酯
- 张力: medium-high
- 羰基: 内酯羰基

输出:
  strain_level: "medium-high"
  ring_opening_tendency: "high"
  preferred_cleavage_site: "酰氧键 C-O 断裂"
  red_susceptibility: "高敏感；张力 + 羰基活化协同作用"
```

## Guardrails
- **区分张力驱动与官能团驱动**：环氧开环是张力驱动，碳酸酯开环是羰基驱动。
- **五元环通常无显著张力**：五元杂环开环多由官能团性质决定。
- **不混淆与 LUMO_03**：普通酯 C-O 断裂在 LUMO_03 处理，除非有显著环张力。
- **桥环需特殊处理**：桥环的张力分布可能不均匀。
- **不输出具体张力能值**：只给定性等级。


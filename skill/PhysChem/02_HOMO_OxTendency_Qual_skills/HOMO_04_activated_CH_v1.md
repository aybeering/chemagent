# HOMO_04_activated_CH_v1 — 活化 C-H 键的氧化敏感性评估

## Triggers
- 分子含有活化的 C-H 键（苄位/烯丙位/α-杂原子），需评估其氧化倾向
- 需要判断"哪个 C-H 键最容易被氧化/脱氢"
- 需要解释"为什么某些 C-H 键比其他的更活泼"

## Inputs
- C-H 键位置与化学环境：
  - 苄位 C-H：与芳环相邻的 sp³ 碳
  - 烯丙位 C-H：与双键相邻的 sp³ 碳
  - α-杂原子 C-H：与 O/N/S 相邻的 C-H
  - 双 α 位：同时满足多个活化条件
- 取代程度：一级 / 二级 / 三级
- 邻近取代基信息

## Outputs
- `CH_homo_level`: 该 C-H 键的 HOMO 贡献等级（very_high / high / medium / low）
- `activation_type`: 活化类型（benzylic / allylic / alpha_hetero / dual_activated）
- `substitution_degree`: 取代程度（primary / secondary / tertiary）
- `radical_stability`: 对应自由基的稳定性评估
- `ox_susceptibility`: 该 C-H 键的氧化敏感性评估

## Rules

### C-H 键 HOMO 贡献排序
```
高 HOMO ──────────────────────────────────────────► 低 HOMO

双活化三级 > 苄位三级 ≈ 烯丙位三级 > α-杂原子三级
           > 苄位二级 ≈ 烯丙位二级 > α-杂原子二级
           > 苄位一级 ≈ 烯丙位一级 > α-杂原子一级
           > 普通三级 > 普通二级 > 普通一级
```

### 活化机制

| 活化类型 | 机制 | σ(C-H) 与受体轨道耦合 |
|----------|------|------------------------|
| 苄位 | σ(C-H) ↔ 芳环 π* | 超共轭 + π 离域稳定自由基 |
| 烯丙位 | σ(C-H) ↔ 烯烃 π* | 超共轭 + π 离域稳定自由基 |
| α-杂原子 | σ(C-H) ↔ 杂原子孤对/空轨道 | n-σ* 超共轭（异头效应相关） |
| 双活化 | 两种机制叠加 | 效应累加，HOMO 显著上升 |

### 取代程度效应
- **三级 > 二级 > 一级**：更多 σ(C-C/C-H) 键可参与超共轭稳定
- **典型差异**：三级苄位 C-H 的 HOMO 可比一级苄位高出显著幅度

### 与 ELEC 联动（调用 HOMO_05 → ELEC_04_hyperconj_v1）
- 超共轭效应的定量调制
- 取代基对活化位点的电子效应

### 特殊情况
- **双苄位**（如二苯甲烷）：两个芳环协同稳定，HOMO 更高
- **累积活化**（如苄位 + α-醚）：效应叠加
- **吸电子取代**：可降低活化程度（如 α-CF₃ 使苄位活性下降）

## Steps
1. 识别分子中所有潜在的活化 C-H 键：
   - 扫描与芳环/双键/杂原子相邻的 sp³ 碳
   - 标记取代程度（一级/二级/三级）
2. 分类活化类型（苄位/烯丙位/α-杂原子/双活化）。
3. 应用基础排序规则，给出初始 HOMO 等级。
4. 调用 `HOMO_05_substituent_mod_v1` 获取取代基调制：
   - 邻近给电子基 → HOMO ↑
   - 邻近吸电子基 → HOMO ↓
5. 输出各活化 C-H 位点的 HOMO 贡献与氧化敏感性评估。

## Examples

### Example 1: 甲苯 (Toluene)
```
输入: SMILES = "Cc1ccccc1"

分析:
- 活化 C-H: 苄位 C-H（-CH₃ 上的 H）
- 取代程度: 一级（CH₃）
- 活化类型: benzylic

输出:
  CH_homo_level: "medium"
  activation_type: "benzylic"
  substitution_degree: "primary"
  radical_stability: "中等（苄基自由基共振稳定）"
  ox_susceptibility: "中等敏感；一级苄位 C-H 可被氧化为苯甲醛"
```

### Example 2: 异丙苯 (Cumene)
```
输入: SMILES = "CC(C)c1ccccc1"

分析:
- 活化 C-H: 苄位三级 C-H
- 取代程度: 三级
- 活化类型: benzylic

输出:
  CH_homo_level: "high"
  activation_type: "benzylic"
  substitution_degree: "tertiary"
  radical_stability: "高（三级苄基自由基）"
  ox_susceptibility: "高度敏感；三级苄位 C-H 是经典的自氧化敏感位点"
```

### Example 3: 四氢呋喃 (THF)
```
输入: SMILES = "C1CCOC1"

分析:
- 活化 C-H: α-醚位 C-H（2位和5位）
- 取代程度: 二级
- 活化类型: alpha_hetero

输出:
  CH_homo_level: "high"
  activation_type: "alpha_hetero"
  substitution_degree: "secondary"
  radical_stability: "中等（α-氧自由基）"
  ox_susceptibility: "高度敏感；α-醚 C-H 是 THF 氧化降解的起始位点"
```

### Example 4: 1,3-二苯基丙烷中心碳
```
输入: 结构 = Ph-CH₂-CH₂-CH₂-Ph

分析:
- 中心 CH₂: 非活化（与芳环隔两个键）
- 端位 CH₂: 苄位二级

输出:
  CH_homo_level: 
    端位CH₂: "medium-high"（苄位二级）
    中心CH₂: "low"（非活化）
  ox_susceptibility: "端位 CH₂ 远比中心 CH₂ 敏感"
```

### Example 5: 异丙醚
```
输入: SMILES = "CC(C)OC(C)C"

分析:
- 活化 C-H: α-醚位三级 C-H（两个异丙基上）
- 取代程度: 三级
- 活化类型: alpha_hetero

输出:
  CH_homo_level: "very_high"
  activation_type: "alpha_hetero"
  substitution_degree: "tertiary"
  radical_stability: "高"
  ox_susceptibility: "极高敏感；三级 α-醚 C-H 是典型的过氧化物形成位点"
```

## Guardrails
- **不混淆活化与非活化**：非苄位/非烯丙位/非 α-杂原子的 C-H 不在本 skill 覆盖范围。
- **取代程度必须标注**：三级、二级、一级对 HOMO 影响显著。
- **双活化需特别标注**：同时满足两种活化条件时，效应累加。
- **不预测具体产物**：只判断"哪个 C-H 容易被氧化"，不预测是生成醇、酮还是过氧化物。
- **自由基稳定性仅作参考**：HOMO 评估基于电子结构，自由基稳定性是相关但不等同的概念。


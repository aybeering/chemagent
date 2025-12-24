# TRADE_01_ewg_not_always_v1 — 吸电子基≠万能稳定：反例与边界

## Purpose
警示"吸电子基(EWG)总是提高氧化/还原稳定性"的过度简化推断，提供具体反例与正确的判断边界。

## Common Pitfall

```yaml
pitfall: "吸电子基降低 HOMO，所以一定提高氧化稳定性"
          "吸电子基降低 LUMO，但分子整体更难被攻击"
```

## Counterexamples

### 反例 1: CF₃ 活化邻近 C-H

```yaml
structure: "CF₃-CH₂-R（α-三氟甲基烷烃）"
expected: "CF₃ 的 -I 降低整体 HOMO，应该更稳定"
actual: "α-CF₃ 位的 C-H 键可能被活化，更易被自由基抽取"
mechanism: |
  - CF₃ 的强 -I 使邻近 C-H 键极化
  - C-H 键的电子云偏向 C，H 更正电
  - 自由基抽氢变得更容易
  - 形成的自由基被 CF₃ 稳定（卤素超共轭）
correction: "CF₃ 降低 HOMO 的同时可能活化特定位点"
```

### 反例 2: 硝基活化芳环还原

```yaml
structure: "硝基苯（Ar-NO₂）"
expected: "硝基强 -M/-I，芳环 HOMO 降低，更难氧化"
actual: "硝基本身 LUMO 极低，成为最易还原位点"
mechanism: |
  - 硝基的 π* 是整个分子的 LUMO
  - 虽然芳环 HOMO 降低，但硝基 LUMO 更低
  - 在还原环境下，硝基极不稳定
correction: "EWG 可能自身成为反应位点"
```

### 反例 3: 氟取代碳酸酯的矛盾

```yaml
structure: "FEC vs EC"
expected: "F 的 -I 降低 HOMO/LUMO，EC 应该更不稳定"
actual: "FEC 在负极更易还原，但这是有益的（促进 LiF 成膜）"
mechanism: |
  - F 确实降低 LUMO，使 FEC 更易还原
  - 但 C-F 断裂释放 F⁻，形成 LiF 富集 SEI
  - "不稳定"反而带来"好膜"
correction: "稳定性与功能性是不同维度"
```

### 反例 4: 吸电子基远程效应衰减

```yaml
structure: "对硝基苯甲醇（4-O₂N-C₆H₄-CH₂OH）"
expected: "硝基 -M 应该显著降低苄醇 HOMO"
actual: "间位 -I 效应弱；苄位 C-H 仍可被氧化"
mechanism: |
  - 硝基在对位，通过 π 共轭传递 -M
  - 但对苄位 C-H（饱和碳）的影响主要是 σ 路径
  - σ 诱导效应随距离快速衰减
correction: "区分 π 通道与 σ 通道的影响范围"
```

### 反例 5: 电子效应 vs 位阻的竞争

```yaml
structure: "大体积 EWG 取代"
expected: "EWG 提高稳定性"
actual: "大体积 EWG 可能阻碍分子平躺吸附，改变界面反应性"
mechanism: |
  - 位阻影响分子在电极的吸附取向
  - 可能暴露其他位点
  - 电子效应被空间效应覆盖
correction: "电子效应不是唯一因素"
```

## When the Pitfall is Valid

```yaml
valid_scenarios:
  - description: "EWG 与目标位点直接相连且无竞争位点"
    example: "酰胺 vs 酯：酰胺的 +M（N）确实使羰基更稳定"
  
  - description: "EWG 效应足够强且作用距离近"
    example: "α-CF₃ 确实降低邻近羰基的 LUMO"
  
  - description: "只考虑热力学稳定性，不考虑动力学"
    example: "HOMO 降低确实意味着氧化驱动力下降"
```

## Correct Reasoning Framework

```
1. EWG 降低 HOMO → 对氧化反应：驱动力下降 ✓
                → 但：是否活化了其他位点？
                → 但：EWG 自身是否成为反应位点？

2. EWG 降低 LUMO → 对还原反应：可能更易还原 ✗（注意方向）
                → 分子整体更易接受电子
                → 需要判断哪个 LUMO 最低

3. 综合判断 → 不能只看"有 EWG"
            → 需要具体分析 EWG 对各位点的影响
            → 需要考虑位阻、动力学等其他因素
```

## Triggers for This Skill

调用本 skill 当：
- 评估结论包含"因为有吸电子基，所以更稳定"
- 分子含有强 EWG（-NO₂, -CF₃, -CN, -COR）
- 需要校验简单的 EWG → 稳定 推断

## Guardrails
- **具体分析**：每个分子需具体评估 EWG 对各位点的影响
- **考虑竞争位点**：EWG 可能在降低某位点活性的同时活化另一位点
- **区分通道**：π 通道 vs σ 通道影响范围不同
- **功能 vs 稳定**："不稳定"有时是有利的（如成膜添加剂）


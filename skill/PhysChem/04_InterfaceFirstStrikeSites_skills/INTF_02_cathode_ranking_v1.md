# INTF_02_cathode_ranking_v1 — 正极界面氧化优先位点排序

## Triggers
- 需要评估分子在**正极界面**的氧化优先位点
- 需要判断"在高电位下，哪个位点最先被氧化"
- CEI 形成机理分析

## Inputs
- 分子表示：SMILES / 结构描述
- 正极材料（可选）：NCM / NCA / LCO / LFP / 高压材料
- 电位范围（可选）：高压（>4.3V）/ 常规（3.0-4.3V）
- 吸附信息（可选）：分子在正极表面的可能取向

## Outputs
- `cathode_ranking`: 正极氧化优先位点列表（按 HOMO 高低排序）
- `dominant_homo_type`: 主导 HOMO 类型（n / π / σ_CH）
- `interface_boost`: 界面效应增强的位点
- `confidence`: 评估置信度

## Rules
- **调用 HOMO 模块**：本 skill 内部调用 `HOMO_01_ox_flowmap_v1` 获取基础排序
- **正极 = 氧化驱动**：高 HOMO 位点优先反应
- **界面修正**：高压材料、TM 催化可能改变排序

## Steps
1. 调用 `HOMO_01_ox_flowmap_v1` 获取体相 HOMO 评估：
   - 输入：分子结构
   - 获取：`ox_sites_ranked`, `dominant_homo_type`

2. 应用界面修正（调用 `HOMO_06_interface_effect_v1`）：
   - 输入：正极材料、电位范围
   - 获取：`interface_modifier`

3. 合并结果，输出最终正极排序。

## Examples

### Example 1: 碳酸二甲酯 (DMC) 在 NCM 正极
```
输入: SMILES = "COC(=O)OC"
正极: NCM (4.3V)

HOMO 调用结果:
  ox_sites_ranked: [酯氧孤对, 甲基C-H]
  dominant_homo_type: "lonepair_n"

界面修正:
  interface_modifier: 
    boost: [酯氧孤对（高压增强）]

输出:
  cathode_ranking:
    rank_1:
      site: "酯氧孤对"
      reason: "最高 HOMO；高压正极增强氧化倾向"
    rank_2:
      site: "甲基 α-酯 C-H"
      reason: "次高 HOMO；可能被自由基路径活化"
  confidence: medium
```

### Example 2: 苯甲醚在高压正极
```
输入: SMILES = "COc1ccccc1"
正极: NCM (4.5V, 高压)

HOMO 调用结果:
  ox_sites_ranked: [苯环π（+M增强）, 醚O孤对]
  dominant_homo_type: "pi_system"

输出:
  cathode_ranking:
    rank_1:
      site: "苯环 π 系统"
      reason: "OMe 的 +M 使芳环 HOMO 最高"
    rank_2:
      site: "醚氧孤对"
      reason: "次高 HOMO"
  interface_boost: "高压可能加速芳环氧化"
  confidence: high
```

## 与 HOMO 模块的联动

```
INTF_02_cathode_ranking_v1
    │
    ├─► HOMO_01_ox_flowmap_v1（获取 HOMO 排序）
    │       ├─► HOMO_02_lonepair_n_v1
    │       ├─► HOMO_03_pi_system_v1
    │       ├─► HOMO_04_activated_CH_v1
    │       └─► HOMO_05_substituent_mod_v1
    │
    └─► HOMO_06_interface_effect_v1（界面修正）
```

## Guardrails
- **必须调用 HOMO 模块**：不能自行评估 HOMO，必须调用上游。
- **正极界面特异性**：考虑高电位、TM 催化等正极特有因素。
- **不预测产物**：只给氧化位点排序。
- **与 INTF_01 一致**：输出格式与总路由兼容。


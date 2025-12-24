# INTF_03_anode_ranking_v1 — 负极界面还原优先位点排序

## Triggers
- 需要评估分子在**负极界面**的还原优先位点
- 需要判断"在低电位下，哪个位点最先被还原"
- SEI 形成机理分析

## Inputs
- 分子表示：SMILES / 结构描述
- 负极材料（可选）：Li metal / Graphite / Si / LTO
- 电位范围（可选）：深度还原（<0.3V）/ 中度（0.3-1.0V）/ 浅（>1.0V）
- 吸附信息（可选）：分子在负极表面的可能取向

## Outputs
- `anode_ranking`: 负极还原优先位点列表（按 LUMO 低高排序）
- `dominant_lumo_type`: 主导 LUMO 类型（π* / σ* / ring_strain）
- `interface_boost`: 界面效应增强的位点
- `sei_relevance`: 与 SEI 形成的相关性
- `confidence`: 评估置信度

## Rules
- **调用 LUMO 模块**：本 skill 内部调用 `LUMO_01_red_flowmap_v1` 获取基础排序
- **负极 = 还原驱动**：低 LUMO 位点优先反应
- **界面修正**：锂金属强还原、石墨首周效应等

## Steps
1. 调用 `LUMO_01_red_flowmap_v1` 获取体相 LUMO 评估：
   - 输入：分子结构
   - 获取：`red_sites_ranked`, `dominant_lumo_type`

2. 应用界面修正（调用 `LUMO_06_interface_effect_v1`）：
   - 输入：负极材料、电位范围
   - 获取：`interface_modifier`, `film_formation_relevance`

3. 合并结果，输出最终负极排序。

## Examples

### Example 1: 碳酸乙烯酯 (EC) 在石墨负极
```
输入: SMILES = "C1COC(=O)O1"
负极: Graphite (0.1V vs Li)

LUMO 调用结果:
  red_sites_ranked: [羰基C=O, 酯基C-O]
  dominant_lumo_type: "pi_antibond"

界面修正:
  interface_modifier:
    boost: [羰基C=O（首周优先还原）]
  film_formation_relevance: "高（SEI 主要成分来源）"

输出:
  anode_ranking:
    rank_1:
      site: "羰基 C=O"
      reason: "最低 LUMO；首周充电优先还原开环"
    rank_2:
      site: "酯基 C-O 键"
      reason: "开环断裂位点"
  sei_relevance: "高度相关；EC 还原产物是 SEI 的主要有机成分"
  confidence: high
```

### Example 2: LiPF₆ 分解
```
输入: LiPF₆ 盐
负极: Li metal (0V vs Li)

分析:
  - P-F 键 σ* 可被还原断裂
  - 释放 F⁻ 形成 LiF

输出:
  anode_ranking:
    rank_1:
      site: "P-F 键"
      reason: "σ* 反键被还原断裂"
  sei_relevance: "极高；F⁻ 释放是 LiF 型 SEI 的关键来源"
  confidence: high
```

### Example 3: 1,3-二氧戊环 (DOL) 在石墨负极
```
输入: SMILES = "C1COCO1"
负极: Graphite (0.1V)

LUMO 调用结果:
  red_sites_ranked: [缩醛C-O]
  dominant_lumo_type: "sigma_antibond"

输出:
  anode_ranking:
    rank_1:
      site: "缩醛 C-O 键"
      reason: "无 π*，σ* 为主要还原位点"
  sei_relevance: "中等；可能开环聚合形成 oligomer"
  confidence: medium
```

## 与 LUMO 模块的联动

```
INTF_03_anode_ranking_v1
    │
    ├─► LUMO_01_red_flowmap_v1（获取 LUMO 排序）
    │       ├─► LUMO_02_pi_antibond_v1
    │       ├─► LUMO_03_sigma_antibond_v1
    │       ├─► LUMO_04_ring_strain_v1
    │       └─► LUMO_05_substituent_mod_v1
    │
    └─► LUMO_06_interface_effect_v1（界面修正）
```

## Guardrails
- **必须调用 LUMO 模块**：不能自行评估 LUMO，必须调用上游。
- **负极界面特异性**：考虑锂金属强还原、SEI 形成等因素。
- **SEI 相关性必须评估**：负极分析与 SEI 密切相关。
- **不预测产物**：只给还原位点排序。


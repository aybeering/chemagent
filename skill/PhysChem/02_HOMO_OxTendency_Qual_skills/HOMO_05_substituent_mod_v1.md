# HOMO_05_substituent_mod_v1 — 取代基对 HOMO 的调制：ELEC Skills 深度联动入口

## Triggers
- 需要评估取代基如何影响目标位点的 HOMO 能级
- 被 HOMO_02/03/04 调用，用于获取电子效应对 HOMO 的调制
- 需要将 ELEC skills 的电子效应结论转化为 HOMO 升/降判断

## Inputs
- 目标位点：需要评估 HOMO 调制的原子/基团
- 取代基列表：连接到目标位点或其共轭体系的取代基
- 分子结构：SMILES 或结构描述
- HOMO 类型：n（孤对）/ π / σ_CH（指示调用来源）

## Outputs
- `homo_shift`: HOMO 调制方向（↑↑ / ↑ / → / ↓ / ↓↓）
- `shift_magnitude`: 调制幅度等级（strong / moderate / weak / negligible）
- `dominant_effect`: 主导电子效应（+M / +I / -M / -I / mixed）
- `elec_summary`: 从 ELEC skills 获取的电子效应摘要
- `confidence`: 评估置信度

## Rules

### 电子效应 → HOMO 调制映射

| 电子效应 | HOMO 调制 | 氧化倾向影响 |
|----------|-----------|--------------|
| 强 +M（-OR, -NR₂ 与共轭） | ↑↑ | 大幅增强 |
| 中 +M / 强 +I（烷基多取代） | ↑ | 增强 |
| 弱 +I（单烷基） | → 略↑ | 略增强 |
| 中性 / 平衡 | → | 无显著影响 |
| 弱 -I（卤素 σ 效应） | → 略↓ | 略降低 |
| 中 -I / 弱 -M | ↓ | 降低 |
| 强 -M / 强 -I（-NO₂, -CF₃, -CN） | ↓↓ | 大幅降低 |

### ELEC Skills 调用策略

根据目标位点类型，选择性调用 ELEC skills：

| HOMO 类型 | 主要调用的 ELEC Skill | 说明 |
|-----------|----------------------|------|
| n（孤对） | ELEC_02_I_sigma_v1, ELEC_03_M_pi_v1 | 诱导 + 共振对孤对的调制 |
| π（芳环/烯烃） | ELEC_03_M_pi_v1, ELEC_01_effect_flowmap_v1 | 共振效应主导 |
| σ_CH（活化C-H） | ELEC_04_hyperconj_v1, ELEC_02_I_sigma_v1 | 超共轭 + 诱导 |

### 完整 Pipeline 调用

对于复杂情况，调用 `ELEC_01_effect_flowmap_v1` 获取完整电子效应分析：

```
HOMO_05 ──► ELEC_01_effect_flowmap_v1
                │
                ├─► ELEC_02_I_sigma_v1（σ 通道）
                ├─► ELEC_03_M_pi_v1（π 通道）
                ├─► ELEC_04_hyperconj_v1（超共轭）
                ├─► ELEC_05_field_v1（场效应）
                └─► ELEC_06_conformation_switch_v1（构象开关）
```

### 多取代基处理
- **同向叠加**：多个给电子基 → 效应累加
- **对向抵消**：给电子 + 吸电子 → 需判断主导
- **位置效应**：邻/对位 vs 间位的影响差异（芳环）

## Steps
1. 接收调用参数：目标位点、取代基列表、HOMO 类型。
2. 根据 HOMO 类型选择 ELEC skill 调用策略。
3. 调用 ELEC skills 获取电子效应分析：
   - 简单情况：单独调用 ELEC_02/03/04
   - 复杂情况：调用 ELEC_01 完整 Pipeline
4. 将电子效应结论映射为 HOMO 调制：
   - `effect_summary` → `homo_shift`
   - `channels` → `dominant_effect`
5. 评估调制幅度与置信度。
6. 输出 HOMO 调制结论，返回给上游（HOMO_02/03/04/01）。

## Examples

### Example 1: 苯甲醚的苯环 π HOMO
```
调用来源: HOMO_03_pi_system_v1
目标位点: 苯环 π 系统
取代基: -OMe（甲氧基）

ELEC 调用:
  → ELEC_03_M_pi_v1
  结果: OMe 为 +M 给电子，使 o/p 位电子密度升高

HOMO 调制:
  homo_shift: "↑↑"
  shift_magnitude: "strong"
  dominant_effect: "+M"
  elec_summary: "OMe 的 +M 效应使芳环 π HOMO 显著上升"
```

### Example 2: 三氟甲基取代胺的 N 孤对
```
调用来源: HOMO_02_lonepair_n_v1
目标位点: 胺 N 孤对
取代基: -CF₃

ELEC 调用:
  → ELEC_02_I_sigma_v1
  结果: CF₃ 为极强 -I，对邻近位点显著吸电子

HOMO 调制:
  homo_shift: "↓↓"
  shift_magnitude: "strong"
  dominant_effect: "-I"
  elec_summary: "CF₃ 的 -I 效应使 N 孤对 HOMO 显著下降"
```

### Example 3: 对甲基苄位 C-H
```
调用来源: HOMO_04_activated_CH_v1
目标位点: 苄位 C-H
取代基: 芳环对位 -CH₃

ELEC 调用:
  → ELEC_04_hyperconj_v1
  结果: 甲基提供弱 +I 超共轭给电子
  → ELEC_03_M_pi_v1
  结果: 甲基对芳环有弱 +I，增加环电子密度

HOMO 调制:
  homo_shift: "↑"
  shift_magnitude: "weak"
  dominant_effect: "+I"
  elec_summary: "对位甲基使苄位 C-H 的 HOMO 略上升"
```

### Example 4: 硝基苯胺的胺基
```
调用来源: HOMO_02_lonepair_n_v1
目标位点: 苯胺 N 孤对
取代基: 对位 -NO₂

ELEC 调用:
  → ELEC_01_effect_flowmap_v1（完整 Pipeline）
  结果:
    - NO₂ 为 -M/-I
    - 与 NH₂ 形成推拉体系
    - NH₂ 的 +M 部分被 NO₂ 的 -M 牵拉

HOMO 调制:
  homo_shift: "↓"
  shift_magnitude: "moderate"
  dominant_effect: "-M (through-conjugation)"
  elec_summary: "NO₂ 通过共轭拉电子，降低 NH₂ 孤对 HOMO（但不如脂肪族 -NO₂ 邻近效应强）"
```

## Guardrails
- **必须调用 ELEC skills**：不能凭"直觉"给出电子效应判断，必须显式调用。
- **映射规则不可跳跃**：电子效应 → HOMO 调制的映射必须遵循表格规则。
- **多取代基需逐一分析**：不能简单地说"有多个取代基"，必须给出净效应。
- **共轭依赖构象**：若构象可能影响共轭，需调用 ELEC_06 判断。
- **返回结构化输出**：供上游 skill 直接使用，不输出冗长描述。


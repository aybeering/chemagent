# LUMO_05_substituent_mod_v1 — 取代基对 LUMO 的调制：ELEC Skills 深度联动入口

## Triggers
- 需要评估取代基如何影响目标位点的 LUMO 能级
- 被 LUMO_02/03/04 调用，用于获取电子效应对 LUMO 的调制
- 需要将 ELEC skills 的电子效应结论转化为 LUMO 升/降判断

## Inputs
- 目标位点：需要评估 LUMO 调制的原子/键/环
- 取代基列表：连接到目标位点或其共轭体系的取代基
- 分子结构：SMILES 或结构描述
- LUMO 类型：π*（羰基等）/ σ*（C-X）/ ring_strain（小环）

## Outputs
- `lumo_shift`: LUMO 调制方向（↓↓ / ↓ / → / ↑ / ↑↑）
- `shift_magnitude`: 调制幅度等级（strong / moderate / weak / negligible）
- `dominant_effect`: 主导电子效应（-M / -I / +M / +I / mixed）
- `elec_summary`: 从 ELEC skills 获取的电子效应摘要
- `confidence`: 评估置信度

## Rules

### 电子效应 → LUMO 调制映射

| 电子效应 | LUMO 调制 | 还原倾向影响 |
|----------|-----------|--------------|
| 强 -M（-NO₂, -COR 共轭） | ↓↓ | 大幅增强 |
| 中 -M / 强 -I（-CF₃, -CN） | ↓ | 增强 |
| 弱 -I（卤素 σ 效应） | → 略↓ | 略增强 |
| 中性 / 平衡 | → | 无显著影响 |
| 弱 +I（烷基） | → 略↑ | 略降低 |
| 中 +I / 弱 +M | ↑ | 降低 |
| 强 +M（-OR, -NR₂ 与共轭） | ↑↑ | 大幅降低 |

**注意**：这与 HOMO 调制**方向相反**
- 对 HOMO：吸电子 → HOMO ↓ → 更难氧化
- 对 LUMO：吸电子 → LUMO ↓ → 更易还原

### ELEC Skills 调用策略

根据目标位点类型，选择性调用 ELEC skills：

| LUMO 类型 | 主要调用的 ELEC Skill | 说明 |
|-----------|----------------------|------|
| π*（羰基/腈） | ELEC_03_M_pi_v1, ELEC_02_I_sigma_v1 | 共振 + 诱导对 π* 的调制 |
| σ*（C-X） | ELEC_02_I_sigma_v1 | 诱导效应对 σ* 的影响 |
| ring_strain | ELEC_02_I_sigma_v1 | 诱导效应可能影响开环选择性 |

### 完整 Pipeline 调用

对于复杂情况，调用 `ELEC_01_effect_flowmap_v1` 获取完整分析：

```
LUMO_05 ──► ELEC_01_effect_flowmap_v1
                │
                ├─► ELEC_02_I_sigma_v1（σ 通道）
                ├─► ELEC_03_M_pi_v1（π 通道）
                └─► 其他 ELEC skills（按需）
```

### 多取代基处理
- **同向叠加**：多个吸电子基 → LUMO 降低累加
- **对向抵消**：吸电子 + 给电子 → 需判断主导
- **位置效应**：共轭位置 vs 非共轭位置影响不同

## Steps
1. 接收调用参数：目标位点、取代基列表、LUMO 类型。
2. 根据 LUMO 类型选择 ELEC skill 调用策略。
3. 调用 ELEC skills 获取电子效应分析。
4. 将电子效应结论映射为 LUMO 调制：
   - 吸电子 → LUMO ↓
   - 给电子 → LUMO ↑
5. 评估调制幅度与置信度。
6. 输出 LUMO 调制结论，返回给上游。

## Examples

### Example 1: 硝基苯甲醛的醛基 π* LUMO
```
调用来源: LUMO_02_pi_antibond_v1
目标位点: 醛基 C=O 的 π*
取代基: 对位硝基 -NO₂

ELEC 调用:
  → ELEC_03_M_pi_v1
  结果: NO₂ 为 -M 吸电子，与羰基共轭

LUMO 调制:
  lumo_shift: "↓↓"
  shift_magnitude: "strong"
  dominant_effect: "-M"
  elec_summary: "硝基通过共轭拉电子，显著降低醛基 π* LUMO"
```

### Example 2: 二甲基酰胺的羰基 π* LUMO
```
调用来源: LUMO_02_pi_antibond_v1
目标位点: 酰胺 C=O 的 π*
取代基: N 上两个甲基

ELEC 调用:
  → ELEC_03_M_pi_v1
  结果: 酰胺 N 的孤对与羰基共轭（+M），甲基提供弱 +I

LUMO 调制:
  lumo_shift: "↑↑"
  shift_magnitude: "strong"
  dominant_effect: "+M (N 孤对共轭)"
  elec_summary: "酰胺 N 的 +M 效应显著升高羰基 π* LUMO"
```

### Example 3: α-氟酯的酯基 π* LUMO
```
调用来源: LUMO_02_pi_antibond_v1
目标位点: 酯基 C=O 的 π*
取代基: α 位氟原子

ELEC 调用:
  → ELEC_02_I_sigma_v1
  结果: F 为强 -I，降低邻近位点电子密度

LUMO 调制:
  lumo_shift: "↓"
  shift_magnitude: "moderate"
  dominant_effect: "-I"
  elec_summary: "α-F 的 -I 效应降低酯基 π* LUMO"
```

### Example 4: 烷基卤化物的 C-Br σ* LUMO
```
调用来源: LUMO_03_sigma_antibond_v1
目标位点: C-Br 的 σ*
取代基: 邻近有硝基

ELEC 调用:
  → ELEC_02_I_sigma_v1
  结果: 硝基 -I/-M 远程影响

LUMO 调制:
  lumo_shift: "↓"
  shift_magnitude: "weak-moderate"
  dominant_effect: "-I (远程)"
  elec_summary: "硝基的吸电子效应略降低 C-Br σ* LUMO"
```

## Guardrails
- **必须调用 ELEC skills**：不能凭直觉给出电子效应判断。
- **方向与 HOMO 相反**：吸电子降低 LUMO（易还原），给电子升高 LUMO（难还原）。
- **共轭 vs 诱导**：对 π* LUMO，共轭效应通常更重要。
- **位置很重要**：不同位置的取代基效应不同。
- **返回结构化输出**：供上游 skill 直接使用。


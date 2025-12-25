# ROLE_05_unsuitable_flag_v1 — 不适合标记

## Triggers
- 需要识别分子结构中的电解液应用警示
- 需要标记明显不适合电解液应用的结构特征
- 作为角色假设的安全筛查前置步骤

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团、敏感位点、环系
- 上游 PhysChem 输出：HOMO/LUMO 分析

## Outputs
- `flags`: 不适合标记列表（若有）
- `severity`: 严重程度（critical / major / minor）
- `reason`: 不适合的原因
- `exception_condition`: 例外条件（在什么情况下可能适用）

## Rules
### 严重不适合标记（Critical）
这些结构特征几乎排除了电解液应用可能：

| 标记 ID | 结构特征 | 原因 |
|--------|---------|------|
| `UNSUI_01` | 活泼 N-H 键（伯胺/仲胺/酰胺） | 与锂反应产 H₂，还原不稳定 |
| `UNSUI_02` | 活泼 O-H 键（醇/羧酸/酚） | 与锂反应产 H₂，质子源 |
| `UNSUI_03` | 活泼 S-H 键（硫醇） | 与锂反应，恶臭 |
| `UNSUI_04` | 过氧化物（-O-O-） | 热不稳定，爆炸风险 |
| `UNSUI_05` | 叠氮基（-N₃） | 爆炸风险 |
| `UNSUI_06` | 硝基（-NO₂）单独 | 还原敏感，可能爆炸 |
| `UNSUI_07` | 高度不饱和（多炔/累积二烯） | 热不稳定，易聚合 |

### 主要不适合标记（Major）
这些结构特征严重限制应用，但在特殊条件下可能有限使用：

| 标记 ID | 结构特征 | 原因 |
|--------|---------|------|
| `UNSUI_10` | 高挥发性（沸点 <60°C） | 安全风险，电池膨胀 |
| `UNSUI_11` | 极低闪点 | 可燃性高 |
| `UNSUI_12` | 已知高毒性 | 健康风险 |
| `UNSUI_13` | 无任何配位/成膜能力 + 无氟化 | 既不能做溶剂也不能做添加剂/稀释剂 |
| `UNSUI_14` | 极窄电化学窗口 | 容易分解 |
| `UNSUI_15` | 水解敏感（如酰卤） | 与痕量水反应 |

### 次要不适合标记（Minor）
这些结构特征需要注意，但不排除使用可能：

| 标记 ID | 结构特征 | 原因 |
|--------|---------|------|
| `UNSUI_20` | 高粘度倾向（大分子/多环） | 可能影响离子传输 |
| `UNSUI_21` | 与常见电极材料已知不相容 | 特定应用受限 |
| `UNSUI_22` | 合成复杂/成本高 | 商业化困难 |
| `UNSUI_23` | 含 Cl/Br/I（非氟卤素） | 可能产生有害卤素 |

## Steps
1. **扫描严重警示**
   - 检查活泼 H 键（N-H、O-H、S-H）
   - 检查高风险官能团（过氧化物、叠氮、硝基）
   
2. **扫描主要警示**
   - 评估挥发性/可燃性
   - 检查水解敏感基团
   - 评估毒性风险
   
3. **扫描次要警示**
   - 评估粘度/成本因素
   - 检查卤素类型

4. **记录所有触发的标记**
   - 按严重程度排序
   - 记录例外条件

## Examples
**Example 1: 甲醇（严重不适合）**
```yaml
input:
  smiles: "CO"
  functional_groups: ["alcohol"]
  
output:
  flags:
    - flag_id: "UNSUI_02"
      severity: "critical"
      reason: "含活泼 O-H 键，与锂金属反应产生 H₂"
      exception_condition: null
  overall_assessment: "不适合电解液应用"
```

**Example 2: 硝基甲烷（严重不适合）**
```yaml
input:
  smiles: "C[N+](=O)[O-]"
  functional_groups: ["nitro"]
  
output:
  flags:
    - flag_id: "UNSUI_06"
      severity: "critical"
      reason: "硝基在还原条件下不稳定，存在爆炸风险"
      exception_condition: null
  overall_assessment: "不适合电解液应用"
```

**Example 3: 二氯甲烷（主要不适合）**
```yaml
input:
  smiles: "ClCCl"
  functional_groups: ["C-Cl"]
  
output:
  flags:
    - flag_id: "UNSUI_10"
      severity: "major"
      reason: "沸点低（40°C），高挥发性"
    - flag_id: "UNSUI_23"
      severity: "minor"
      reason: "含 Cl，还原可能释放 Cl⁻"
  overall_assessment: "不推荐用于电解液"
  exception_condition: "极低温特殊应用可能考虑"
```

**Example 4: EC（无标记）**
```yaml
input:
  smiles: "C1COC(=O)O1"
  functional_groups: ["cyclic_carbonate"]
  
output:
  flags: []
  overall_assessment: "未检测到不适合标记"
```

## Guardrails
- 不适合标记是结构警示，不是最终判决
- 某些"不适合"结构在特殊条件下可能有限使用
- 新型结构无法完全评估，需实验验证
- Critical 标记通常不建议任何电解液应用
- 多个 Minor 标记累积可能等同于 Major

## Dependencies
- 上游：OrganicChem 官能团识别
- 调用方：ROLE_01_role_flowmap_v1

## Changelog
- 2025-12-25: 初始版本


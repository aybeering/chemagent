# HOMO_03_pi_system_v1 — π 系统氧化倾向：芳环、烯烃、共轭体系的 HOMO 评估

## Triggers
- 分子含有 π 系统（芳环/烯烃/共轭链），需评估其对 HOMO 的贡献
- 需要判断"这个芳环/双键容易被氧化吗"
- 需要比较富电子 vs 缺电子 π 系统的氧化倾向

## Inputs
- π 系统类型：
  - 芳环：苯、萘、呋喃、噻吩、吡啶、吡咯等
  - 烯烃：隔离双键、共轭双键、烯醇醚
  - 共轭链：多烯、芳基乙烯基
- 取代基信息：给电子 vs 吸电子
- 共轭连续性（可选）
- 环张力/应变（可选）

## Outputs
- `pi_homo_level`: π HOMO 贡献等级（very_high / high / medium / low / very_low）
- `pi_system_type`: π 系统分类（aromatic / alkene / conjugated_chain）
- `electron_richness`: 电子丰度评估（electron_rich / neutral / electron_poor）
- `substituent_effect`: 取代基对 π HOMO 的调制（↑ / → / ↓）
- `ox_susceptibility`: 该 π 系统的氧化敏感性评估

## Rules

### π 系统 HOMO 基础排序（无取代基时）
```
高 HOMO ──────────────────────────────────────────► 低 HOMO

富电子杂环 > 富电子芳环 > 共轭多烯 > 普通芳环 > 隔离烯烃 
          > 缺电子芳环 > 缺电子杂环 > 强缺电子体系
```

### 芳环电子丰度分类
| 类别 | 典型结构 | HOMO 水平 |
|------|----------|-----------|
| 富电子杂环 | 吡咯、呋喃、噻吩 | very_high |
| 富电子芳环 | 苯胺、苯酚、苯甲醚 | high |
| 普通芳环 | 苯、甲苯 | medium |
| 缺电子芳环 | 硝基苯、苯甲醛 | low |
| 缺电子杂环 | 吡啶、嘧啶 | low |
| 强缺电子 | 三嗪、四氟苯 | very_low |

### 烯烃 HOMO 评估
- **电子丰度**：烷基取代 > 氢取代 > 卤素取代 > 羰基共轭
- **共轭效应**：
  - 与给电子基共轭 → HOMO ↑（烯醇醚、烯胺）
  - 与吸电子基共轭 → HOMO ↓（α,β-不饱和羰基）
- **张力**：小环烯烃（如环丙烯）HOMO 异常高

### 取代基调制（需调用 HOMO_05）
- **+M 效应**（-OR, -NR₂）→ π HOMO ↑↑ → 显著增强氧化倾向
- **+I 效应**（烷基）→ π HOMO ↑ → 略增强氧化倾向
- **-M 效应**（-NO₂, -COR, -CN）→ π HOMO ↓↓ → 显著降低氧化倾向
- **-I 效应**（-CF₃, -F）→ π HOMO ↓ → 降低氧化倾向

### 共轭延伸效应
- **共轭链越长 → HOMO 越分散，能级可能上升**
- **交替单双键连续 → 电子离域 → HOMO 趋于稳定化**

## Steps
1. 识别分子中所有 π 系统（芳环/烯烃/共轭链）。
2. 分类每个 π 系统的基础类型与电子丰度。
3. 调用 `HOMO_05_substituent_mod_v1` 获取取代基调制：
   - 汇总连接到 π 系统的取代基
   - 判断净电子效应（±M / ±I）
4. 调整 HOMO 等级：
   - 给电子取代 → 上调
   - 吸电子取代 → 下调
5. 输出各 π 系统的 HOMO 贡献与氧化敏感性评估。

## Examples

### Example 1: 苯甲醚 (Anisole)
```
输入: SMILES = "COc1ccccc1"

分析:
- π 系统: 苯环
- 取代基: -OMe（+M 强给电子）

输出:
  pi_homo_level: "high"
  electron_richness: "electron_rich"
  substituent_effect: "↑↑ (+M)"
  ox_susceptibility: "高度敏感；OMe 的 +M 使苯环 HOMO 显著上升"
```

### Example 2: 硝基苯
```
输入: SMILES = "c1ccc(cc1)[N+](=O)[O-]"

分析:
- π 系统: 苯环
- 取代基: -NO₂（-M/-I 强吸电子）

输出:
  pi_homo_level: "low"
  electron_richness: "electron_poor"
  substituent_effect: "↓↓ (-M/-I)"
  ox_susceptibility: "低敏感；NO₂ 使苯环 HOMO 显著下降"
```

### Example 3: 1,3-丁二烯
```
输入: SMILES = "C=CC=C"

分析:
- π 系统: 共轭二烯
- 取代基: 无（全 H）

输出:
  pi_homo_level: "medium-high"
  pi_system_type: "conjugated_chain"
  electron_richness: "neutral"
  ox_susceptibility: "中等敏感；共轭使 HOMO 有一定分散"
```

### Example 4: 吡咯
```
输入: SMILES = "c1cc[nH]c1"

分析:
- π 系统: 五元杂环（吡咯）
- 特性: N 的孤对参与芳香性（6π 电子）

输出:
  pi_homo_level: "very_high"
  electron_richness: "electron_rich"
  ox_susceptibility: "非常敏感；吡咯是典型的富电子杂环"
```

## Guardrails
- **区分芳香性与烯烃**：吡咯/呋喃是芳香体系，不是"杂原子+双键"。
- **考虑取代基位置**：芳环上 o/m/p 位的取代基效应不同（需与 ELEC_03_M_pi_v1 联动）。
- **不混淆 HOMO 与反应性**：高 HOMO 意味着"易被氧化"，不等于"反应速度快"。
- **共轭判断需结合构象**：非共面时共轭效应降权。
- **多 π 系统分子**：必须分别评估并指出主导贡献者。


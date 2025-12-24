# HOMO_01_ox_flowmap_v1 — 氧化倾向总路由：HOMO 趋势直觉与位点优先级排序

## Triggers
- 需要评估分子整体或特定位点的**氧化倾向**（定性）
- 需要给出"哪些位点最容易被氧化"的优先级排序
- 电解液分子的氧化稳定性初步筛查

## Inputs
- 分子表示：SMILES / 结构描述 / 官能团簇列表
- 关注位点（可选）：原子编号或"官能团中心"的文字描述
- 环境假设（可选）：
  - 界面类型：正极界面 / 负极界面 / 体相
  - 电场强度：强 / 中 / 弱
  - 溶剂极性：高 / 低
- 输出精度（可选）：快速筛查 / 详细分析

## Outputs
- `ox_sites_ranked`: 氧化敏感位点列表（按 HOMO 贡献排序，高→低）
- `dominant_homo_type`: 主导 HOMO 类型（n / π / σ_CH）
- `homo_contributors`: 各通道的 HOMO 贡献评估
  - `lonepair_n`: 孤对电子贡献
  - `pi_system`: π 系统贡献
  - `activated_CH`: 活化 C-H 贡献
- `interface_modifier`: 界面环境对排序的修正（如有）
- `confidence`: 整体置信度（high / medium / low）
- `notes`: 补充说明与警示

## Rules
- **HOMO 能级越高 → 越易被氧化**：这是本模块的核心假设。
- **典型 HOMO 能级顺序**（定性参考，可被取代基调制）：
  - 胺 N 孤对 > 硫醚 S 孤对 > 富电子芳环 π > 烯烃 π > 醚 O 孤对 > 普通芳环 π > 缺电子体系
- **取代基调制**：给电子基(+M/+I)抬高 HOMO → 更易氧化；吸电子基(-M/-I)降低 HOMO → 更难氧化。
- **界面效应**：正极高电位环境可改变氧化位点优先级，需调用 `HOMO_06_interface_effect_v1` 修正。
- **多位点竞争**：当存在多种 HOMO 贡献者时，需分别评估并排序。

## Steps
1. **位点识别**：扫描分子，识别所有潜在氧化敏感位点：
   - 杂原子孤对（N/O/S/P）
   - π 系统（芳环/烯烃/共轭链）
   - 活化 C-H 键（苄位/烯丙位/α-杂原子）

2. **分通道评估**：分别调用子技能卡：
   - `HOMO_02_lonepair_n_v1`：评估孤对电子位点
   - `HOMO_03_pi_system_v1`：评估 π 系统位点
   - `HOMO_04_activated_CH_v1`：评估活化 C-H 位点

3. **取代基调制**：对每个候选位点，调用 `HOMO_05_substituent_mod_v1` 评估取代基对 HOMO 的升/降效应。

4. **界面修正**（如适用）：调用 `HOMO_06_interface_effect_v1` 获取界面环境修正因子。

5. **汇总排序**：
   - 综合各通道的 HOMO 贡献与取代基调制
   - 应用界面修正
   - 输出 `ox_sites_ranked`（按氧化倾向从高到低）

6. **输出结论**：给出主导 HOMO 类型、各位点评估、置信度与补充说明。

## Examples

### Example 1: N,N-二甲基甲酰胺 (DMF)
```
输入: SMILES = "CN(C)C=O"
环境: 正极界面

分析:
- 孤对位点: 酰胺 N（共轭降低 HOMO）、羰基 O（低 HOMO）
- π 系统: 羰基 C=O（非典型 HOMO）
- 活化 C-H: 无苄位/烯丙位

输出:
  ox_sites_ranked: [酰胺N（中等）, 羰基O（低）]
  dominant_homo_type: "lonepair_n"
  notes: "酰胺 N 的孤对参与共轭，HOMO 显著降低；相对较稳定"
```

### Example 2: 苯甲醚
```
输入: SMILES = "COc1ccccc1"
环境: 体相

分析:
- 孤对位点: 醚 O（+M 给电子）
- π 系统: 苯环（被 OMe 富电子化）
- 活化 C-H: 苄位不存在（OMe 直连）

输出:
  ox_sites_ranked: [苯环π（高，+M增强）, 醚O孤对（中等）]
  dominant_homo_type: "pi_system"
  notes: "OMe 的 +M 效应使苯环 π HOMO 上升，成为主导氧化位点"
```

### Example 3: 四氢呋喃 (THF)
```
输入: SMILES = "C1CCOC1"
环境: 正极界面

分析:
- 孤对位点: 醚 O
- π 系统: 无
- 活化 C-H: α-醚位 C-H（2位和5位）

输出:
  ox_sites_ranked: [α-醚位C-H（高）, 醚O孤对（中等）]
  dominant_homo_type: "activated_CH"
  notes: "α-醚位 C-H 因杂原子邻近效应活化，是主要氧化敏感位点"
```

## Guardrails
- **不输出定量数据**：不给出氧化电位、HOMO 能量数值（eV）、Hammett σ 等定量参数。
- **不预测具体反应产物**：只判断"哪里容易被氧化"，不预测生成什么。
- **多位点时必须排序**：不能只说"有多个氧化位点"，必须给出优先级。
- **环境缺失时降置信度**：若未提供界面/电场信息，输出 `confidence: medium` 并标注。
- **极端结构标注**：对高度对称或特殊电子结构（如卟啉、富勒烯），标注"需额外验证"。


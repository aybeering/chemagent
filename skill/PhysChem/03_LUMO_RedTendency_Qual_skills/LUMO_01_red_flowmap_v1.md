# LUMO_01_red_flowmap_v1 — 还原倾向总路由：LUMO 趋势直觉与位点优先级排序

## Triggers
- 需要评估分子整体或特定位点的**还原倾向**（定性）
- 需要给出"哪些位点最容易被还原"的优先级排序
- 电解液分子的还原稳定性初步筛查（负极界面）

## Inputs
- 分子表示：SMILES / 结构描述 / 官能团簇列表
- 关注位点（可选）：原子编号或"官能团中心"的文字描述
- 环境假设（可选）：
  - 界面类型：负极界面 / 正极界面 / 体相
  - 电极材料：锂金属 / 石墨 / 硅基
  - 电位范围：深度还原（<0.5V vs Li）/ 常规（0.5-1.5V）
- 输出精度（可选）：快速筛查 / 详细分析

## Outputs
- `red_sites_ranked`: 还原敏感位点列表（按 LUMO 贡献排序，低→高）
- `dominant_lumo_type`: 主导 LUMO 类型（π* / σ* / ring_strain）
- `lumo_contributors`: 各通道的 LUMO 贡献评估
  - `pi_antibond`: π* 反键贡献
  - `sigma_antibond`: σ* 反键贡献
  - `ring_strain`: 环张力贡献
- `interface_modifier`: 界面环境对排序的修正（如有）
- `confidence`: 整体置信度（high / medium / low）
- `notes`: 补充说明与警示

## Rules
- **LUMO 能级越低 → 越易被还原**：这是本模块的核心假设。
- **典型 LUMO 能级顺序**（定性参考，可被取代基调制）：
  ```
  硝基 < 醛 < 酮 < 酯 ≈ 环氧 < 酰胺 < 腈 < C-卤素 < 烯烃 < 芳环 < 饱和烷
  ```
- **取代基调制**：吸电子基(-M/-I)降低 LUMO → 更易还原；给电子基(+M/+I)抬高 LUMO → 更难还原。
- **界面效应**：负极低电位环境可活化通常稳定的位点，需调用 `LUMO_06_interface_effect_v1` 修正。
- **多位点竞争**：当存在多种 LUMO 贡献者时，需分别评估并排序。

## Steps
1. **位点识别**：扫描分子，识别所有潜在还原敏感位点：
   - π* 体系（羰基/腈/硝基/烯烃）
   - σ* 体系（C-卤素/C-O酯/磺酸酯）
   - 应变体系（环氧/环丙烷/环丁烷）

2. **分通道评估**：分别调用子技能卡：
   - `LUMO_02_pi_antibond_v1`：评估 π* 反键位点
   - `LUMO_03_sigma_antibond_v1`：评估 σ* 反键位点
   - `LUMO_04_ring_strain_v1`：评估环张力位点

3. **取代基调制**：对每个候选位点，调用 `LUMO_05_substituent_mod_v1` 评估取代基对 LUMO 的升/降效应。

4. **界面修正**（如适用）：调用 `LUMO_06_interface_effect_v1` 获取界面环境修正因子。

5. **汇总排序**：
   - 综合各通道的 LUMO 贡献与取代基调制
   - 应用界面修正
   - 输出 `red_sites_ranked`（按还原倾向从高到低）

6. **输出结论**：给出主导 LUMO 类型、各位点评估、置信度与补充说明。

## Examples

### Example 1: 碳酸乙烯酯 (EC)
```
输入: SMILES = "C1COC(=O)O1"
环境: 负极界面（石墨）

分析:
- π* 位点: 羰基 C=O
- σ* 位点: 酯基 C-O 键
- 应变: 五元环（微弱张力）

输出:
  red_sites_ranked: [羰基C=O（高）, 酯基C-O（中）]
  dominant_lumo_type: "pi_antibond"
  notes: "EC 的羰基是主要还原位点；负极界面开环形成 SEI"
```

### Example 2: 氟代碳酸乙烯酯 (FEC)
```
输入: SMILES = "C1C(F)OC(=O)O1"
环境: 负极界面（锂金属）

分析:
- π* 位点: 羰基 C=O
- σ* 位点: C-F 键、酯基 C-O 键
- 取代基效应: F 的 -I 效应降低羰基 LUMO

输出:
  red_sites_ranked: [羰基C=O（很高，-I增强）, C-F（高）, 酯基C-O（中）]
  dominant_lumo_type: "pi_antibond"
  notes: "F 取代使羰基还原更易；C-F 还原释放 F⁻ 有利于 LiF 成膜"
```

### Example 3: 1,3-二氧戊环 (DOL)
```
输入: SMILES = "C1COCO1"
环境: 负极界面

分析:
- π* 位点: 无（无不饱和键）
- σ* 位点: C-O 缩醛键
- 应变: 五元环（微弱）

输出:
  red_sites_ranked: [缩醛C-O（中）]
  dominant_lumo_type: "sigma_antibond"
  notes: "DOL 无典型低 LUMO 位点；还原主要发生在 C-O 键，可能开环聚合"
```

### Example 4: 硝基甲烷
```
输入: SMILES = "C[N+](=O)[O-]"
环境: 体相

分析:
- π* 位点: 硝基 N=O（极低 LUMO）
- σ* 位点: C-N 键

输出:
  red_sites_ranked: [硝基N=O（极高敏感）]
  dominant_lumo_type: "pi_antibond"
  notes: "硝基是最易还原的官能团之一；极不稳定于还原环境"
```

## Guardrails
- **不输出定量数据**：不给出还原电位、LUMO 能量数值（eV）等定量参数。
- **不预测具体反应产物**：只判断"哪里容易被还原"，不预测生成什么。
- **多位点时必须排序**：不能只说"有多个还原位点"，必须给出优先级。
- **环境缺失时降置信度**：若未提供界面/电位信息，输出 `confidence: medium` 并标注。
- **正极界面不适用**：正极以氧化为主，本模块适用性降低（应使用 HOMO 模块）。


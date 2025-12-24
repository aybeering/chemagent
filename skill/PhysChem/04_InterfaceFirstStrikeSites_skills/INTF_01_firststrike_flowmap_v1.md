# INTF_01_firststrike_flowmap_v1 — 界面优先反应位点总路由

## Triggers
- 需要评估分子在电极界面的**优先反应位点**
- 需要给出正极/负极双极界面的位点排序
- 电解液分子的界面稳定性初步筛查

## Inputs
- 分子表示：SMILES / 结构描述 / 官能团簇列表
- 关注界面（可选）：
  - `both`: 正极 + 负极（默认）
  - `cathode_only`: 仅正极
  - `anode_only`: 仅负极
- 电极材料（可选）：
  - 正极：NCM / NCA / LCO / LFP
  - 负极：Li metal / Graphite / Si
- 电位范围（可选）：高压（>4.3V）/ 常规 / 深度还原（<0.5V）

## Outputs
- `first_strike_sites`: 界面优先反应位点排序
  - `cathode`: 正极界面排序
  - `anode`: 负极界面排序
- `competition_notes`: 多位点竞争判定说明
- `film_hint`: 成膜倾向提示
- `confidence`: 整体置信度
- `notes`: 补充说明与警示

## Rules
- **正极 = 氧化环境**：按 HOMO 排序（高 HOMO 优先反应）
- **负极 = 还原环境**：按 LUMO 排序（低 LUMO 优先反应）
- **界面效应**：吸附、电场、电极催化可能修正排序
- **只排序不预测**：只给出"哪里先反应"，不预测产物

## Steps
1. **调用正极评估**：`INTF_02_cathode_ranking_v1`
   - 内部调用 `HOMO_01_ox_flowmap_v1`
   - 获取正极界面氧化优先位点

2. **调用负极评估**：`INTF_03_anode_ranking_v1`
   - 内部调用 `LUMO_01_red_flowmap_v1`
   - 获取负极界面还原优先位点

3. **竞争判定**（如有多位点）：`INTF_04_competition_resolve_v1`
   - 评估位点间竞争关系
   - 给出明确优先级

4. **成膜提示**：`INTF_05_film_formation_hint_v1`
   - 评估与 SEI/CEI 形成的相关性
   - 提示可能的成膜路径

5. **汇总输出**：整合各子卡结果，输出结构化排序

## Examples

### Example 1: 碳酸乙烯酯 (EC)
```
输入: SMILES = "C1COC(=O)O1"

输出:
  first_strike_sites:
    cathode:
      rank_1:
        site: "酯氧孤对"
        reason: "最高 HOMO 贡献者"
        confidence: medium
      rank_2:
        site: "亚甲基 C-H"
        reason: "次高 HOMO（α-醚活化）"
    anode:
      rank_1:
        site: "羰基 C=O"
        reason: "最低 LUMO（π* 反键）"
        confidence: high
      rank_2:
        site: "酯基 C-O 键"
        reason: "开环位点"
  film_hint: "负极还原开环形成 SEI；正极相对稳定"
```

### Example 2: 氟代碳酸乙烯酯 (FEC)
```
输入: SMILES = "C1C(F)OC(=O)O1"

输出:
  first_strike_sites:
    cathode:
      rank_1:
        site: "酯氧孤对"
        reason: "HOMO 贡献，但被 F 的 -I 略降"
        confidence: medium
    anode:
      rank_1:
        site: "羰基 C=O"
        reason: "最低 LUMO（被 F 进一步降低）"
        confidence: high
      rank_2:
        site: "C-F 键"
        reason: "可释放 F⁻ 形成 LiF"
  competition_notes: "羰基还原与 C-F 断裂可能竞争"
  film_hint: "优先还原；F⁻ 释放促进 LiF 富集 SEI"
```

### Example 3: N,N-二甲基甲酰胺 (DMF)
```
输入: SMILES = "CN(C)C=O"

输出:
  first_strike_sites:
    cathode:
      rank_1:
        site: "酰胺 N 孤对"
        reason: "虽共轭降低，仍是最高 HOMO"
        confidence: medium
      rank_2:
        site: "羰基氧孤对"
        reason: "次高 HOMO"
    anode:
      rank_1:
        site: "羰基 C=O"
        reason: "酰胺羰基 π*（被 +M 升高，但仍是最低）"
        confidence: medium
  film_hint: "酰胺相对稳定；高压正极可能氧化 N"
```

## Output Format

```yaml
first_strike_sites:
  cathode:
    rank_1:
      site: "<位点描述>"
      reason: "<优先的理由>"
      confidence: high/medium/low
    rank_2:
      site: "..."
      reason: "..."
    # 可继续 rank_3, rank_4...
  anode:
    rank_1:
      site: "<位点描述>"
      reason: "<优先的理由>"
      confidence: high/medium/low
    rank_2:
      site: "..."
      reason: "..."
  competition_notes: "<多位点竞争的判定说明，可选>"
  film_hint: "<与成膜相关的提示，可选>"
```

## Guardrails
- **不预测具体产物**：只给"哪里先反应"，不给"生成什么"。
- **排序必须有理由**：每个位点必须说明为什么排在这个位置。
- **置信度必须标注**：不确定时使用 `medium` 或 `low`。
- **正负极都要评估**：除非用户明确只关心一极。
- **与上游一致**：排序结论必须与 HOMO/LUMO 模块一致。


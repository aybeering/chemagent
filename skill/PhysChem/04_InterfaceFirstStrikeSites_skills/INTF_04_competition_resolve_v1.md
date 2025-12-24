# INTF_04_competition_resolve_v1 — 多位点竞争判定与优先级决策

## Triggers
- 分子存在**多个能级接近的反应位点**，需要决定优先级
- HOMO 或 LUMO 排序中出现"能级接近"或"置信度不高"的情况
- 需要解释"为什么这个位点比另一个更优先"

## Inputs
- 竞争位点列表：从 HOMO/LUMO 模块获取的候选位点
- 位点能级差异：定性描述（接近 / 显著不同）
- 界面条件：正极 / 负极 / 体相
- 额外考虑因素（可选）：
  - 位阻效应
  - 吸附取向
  - 动力学因素

## Outputs
- `resolved_ranking`: 决策后的优先级排序
- `decision_basis`: 决策依据（能级 / 位阻 / 动力学 / 吸附）
- `competition_type`: 竞争类型
  - `clear_winner`: 有明确胜出者
  - `close_competition`: 接近竞争，可能并行
  - `condition_dependent`: 取决于具体条件
- `parallel_possibility`: 是否可能并行反应
- `confidence`: 判定置信度

## Rules

### 竞争判定决策树

```
1. 能级差异显著？
   ├─ 是 → 低能级位点胜出（LUMO）/ 高能级位点胜出（HOMO）
   └─ 否 → 进入第2步

2. 位阻差异显著？
   ├─ 是 → 位阻小的位点优先
   └─ 否 → 进入第3步

3. 吸附取向有偏好？
   ├─ 是 → 暴露于电极的位点优先
   └─ 否 → 进入第4步

4. 动力学因素？
   ├─ 有证据 → 按动力学偏好
   └─ 无证据 → 标记为"接近竞争，可能并行"
```

### 能级差异判定标准（定性）

| 差异程度 | 描述 | 判定 |
|----------|------|------|
| 显著 | 不同官能团类型（如羰基 vs 芳环） | 明确优先级 |
| 中等 | 同类官能团，取代基不同 | 需综合考虑 |
| 微小 | 同类官能团，环境相似 | 可能并行 |

### 常见竞争场景

| 场景 | 判定方法 |
|------|----------|
| 羰基 vs 羰基 | 取代基调制（更吸电子的 LUMO 更低） |
| 孤对 vs π 系统 | 通常孤对 HOMO 更高（脂肪胺 > 芳环） |
| C-Br vs C-Cl | C-Br 的 σ* 更低，优先断裂 |
| 环氧 vs 羰基 | 需比较具体 LUMO 贡献 |

## Steps
1. 接收竞争位点列表与初步排序。
2. 评估能级差异：
   - 显著差异 → 直接判定
   - 接近 → 继续评估
3. 评估位阻因素：
   - 是否有空间屏蔽
   - 是否影响电子转移
4. 评估吸附取向（如有信息）：
   - 哪个官能团更暴露
5. 综合判定并标注决策依据。
6. 评估并行反应可能性。

## Examples

### Example 1: DMC 的两个酯氧
```
输入:
  竞争位点: [酯氧1孤对, 酯氧2孤对]
  界面: 正极

分析:
  - 两个酯氧化学环境相同
  - 能级几乎相同
  - 无位阻差异

输出:
  resolved_ranking: [酯氧1 ≈ 酯氧2]
  decision_basis: "化学等价"
  competition_type: "close_competition"
  parallel_possibility: "高；两个位点可能同时被氧化"
```

### Example 2: 对硝基苯甲醛的羰基 vs 硝基
```
输入:
  竞争位点: [醛基C=O, 硝基N=O]
  界面: 负极

分析:
  - 硝基 LUMO < 醛基 LUMO（硝基更低）
  - 能级差异显著

输出:
  resolved_ranking: [硝基N=O（rank_1）, 醛基C=O（rank_2）]
  decision_basis: "能级差异显著（硝基 LUMO 最低）"
  competition_type: "clear_winner"
  parallel_possibility: "低；硝基优先还原"
  confidence: high
```

### Example 3: FEC 的羰基 vs C-F
```
输入:
  竞争位点: [羰基C=O, C-F键]
  界面: 负极（锂金属）

分析:
  - 羰基 π* LUMO 略低于 C-F σ*
  - 强还原条件下两者都可能反应
  - C-F 断裂有 LiF 成膜热力学驱动

输出:
  resolved_ranking: [羰基C=O（略优先）, C-F（可能竞争）]
  decision_basis: "π* 略低于 σ*，但 LiF 成膜驱动 C-F 断裂"
  competition_type: "condition_dependent"
  parallel_possibility: "中等；强还原条件下可能并行"
  confidence: medium
```

### Example 4: 苄位 C-H vs 芳环 π
```
输入:
  竞争位点: [苄位C-H, 芳环π]
  界面: 正极

分析:
  - 苄位 C-H 的 HOMO：σ(C-H) + 超共轭
  - 芳环 π 的 HOMO：π 系统
  - 取决于取代基（富电子芳环 π 可能更高）

输出:
  resolved_ranking: "取决于取代基"
  decision_basis: "需调用 HOMO_05 评估取代基效应"
  competition_type: "condition_dependent"
  notes: "给电子取代时芳环优先；吸电子取代时苄位可能优先"
```

## Guardrails
- **不强行分出胜负**：能级接近时，明确标注"接近竞争"。
- **必须给出决策依据**：每个判定必须说明理由。
- **考虑并行可能**：多位点可能同时反应。
- **条件依赖要标注**：取决于具体条件时明确说明。
- **置信度反映不确定性**：接近竞争时使用 `medium` 或 `low`。


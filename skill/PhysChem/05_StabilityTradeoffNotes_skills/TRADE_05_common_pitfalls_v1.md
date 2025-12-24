# TRADE_05_common_pitfalls_v1 — 常见误判清单：高频错误推断与纠正汇总

## Purpose
汇总电解液分子稳定性评估中的高频错误推断，提供快速检索与纠正参考。

## Pitfalls Quick Reference

### 误判 1: 吸电子基 = 万能稳定

```yaml
pitfall: "有吸电子基（EWG）就更稳定"
frequency: ★★★★★ (极高频)
correction: |
  - EWG 可能降低某些位点的反应性
  - 但可能活化其他位点（如邻近 C-H）
  - EWG 自身可能成为反应位点（如硝基）
detailed_card: TRADE_01_ewg_not_always_v1
```

### 误判 2: 氟化 = 更稳定

```yaml
pitfall: "氟化衍生物比非氟化物更稳定"
frequency: ★★★★☆ (高频)
correction: |
  - F 的 -I 确实可能降低 HOMO
  - 但 C-F 键断裂释放 F⁻ 可能被热力学驱动（形成 LiF）
  - 氟化物可能在负极更易还原
  - FEC 比 EC 更易还原，但这正是它的功能
```

### 误判 3: 高沸点 = 热稳定

```yaml
pitfall: "沸点高就热稳定性好"
frequency: ★★★☆☆ (中频)
correction: |
  - 沸点反映分子间作用力，不是化学稳定性
  - 高沸点化合物可能有热分解问题
  - 需区分物理稳定性与化学稳定性
```

### 误判 4: 大分子 = 更稳定

```yaml
pitfall: "分子量大的化合物更稳定"
frequency: ★★★☆☆ (中频)
correction: |
  - 大分子可能有更多潜在反应位点
  - 分子量与稳定性无直接关系
  - 需要具体分析官能团
```

### 误判 5: HOMO/LUMO 决定一切

```yaml
pitfall: "只看 HOMO/LUMO 就能预测稳定性"
frequency: ★★★★☆ (高频)
correction: |
  - HOMO/LUMO 是热力学指标
  - 实际反应性还受动力学控制
  - 界面效应、位阻、吸附都影响实际行为
detailed_card: TRADE_03_kinetic_vs_thermo_v1
```

### 误判 6: 稳定 = 好电解液

```yaml
pitfall: "越稳定的分子越适合做电解液"
frequency: ★★★★☆ (高频)
correction: |
  - 添加剂常常需要"适度不稳定"来成膜
  - 过于稳定可能无法形成好的 SEI/CEI
  - 需要平衡稳定性与功能性
detailed_card: TRADE_04_interface_paradox_v1
```

### 误判 7: 无 α-H = 对碱稳定

```yaml
pitfall: "没有 α-氢就对碱稳定"
frequency: ★★☆☆☆ (低频)
correction: |
  - 无 α-H 只是避免了 aldol 类反应
  - 其他亲核攻击路径可能存在
  - 需要综合评估
```

### 误判 8: 共轭 = HOMO 上升

```yaml
pitfall: "共轭体系 HOMO 一定比非共轭高"
frequency: ★★★☆☆ (中频)
correction: |
  - 共轭可能稳定化 HOMO（如芳香性）
  - 与吸电子基共轭可能降低 HOMO
  - 需要具体分析共轭效应方向
```

### 误判 9: 环状 = 更稳定

```yaml
pitfall: "环状结构比链状更稳定"
frequency: ★★☆☆☆ (低频)
correction: |
  - 小环有张力，可能更活泼
  - 五/六元环通常稳定
  - 环的杂原子组成很重要
detailed_card: LUMO_04_ring_strain_v1
```

### 误判 10: 对称 = 没有选择性

```yaml
pitfall: "对称分子各位点反应性相同"
frequency: ★★☆☆☆ (低频)
correction: |
  - 对称分子的反应常打破对称
  - 界面吸附可能破坏对称性
  - 反应中间体可能不对称
```

## Quick Checklist

评估结论前快速自检：

```markdown
□ 是否假设了"EWG = 稳定"？（检查 TRADE_01）
□ 是否忽略了位阻效应？（检查 TRADE_02）
□ 是否混淆了热力学与动力学？（检查 TRADE_03）
□ 是否认为"不稳定 = 差"？（检查 TRADE_04）
□ 是否只考虑了电子效应？
□ 是否考虑了界面特殊性？
□ 置信度是否与证据匹配？
```

## Red Flags

这些表述可能触发误判警告：

| 表述 | 可能的问题 | 应该 |
|------|------------|------|
| "因为有 CF₃ 所以稳定" | EWG 可能活化邻近位点 | 具体分析各位点 |
| "HOMO 低所以不氧化" | 忽略动力学 | 考虑能垒和界面 |
| "结构稳定所以好" | 忽略功能性 | 考虑成膜需求 |
| "类似结构类似性质" | 忽略微小差异的放大 | 具体分析差异 |
| "理论上应该..." | 理论假设可能不适用 | 考虑实际条件 |

## Cross-references

| 详细主题 | 对应 Skill |
|----------|------------|
| 吸电子基反例 | TRADE_01_ewg_not_always_v1 |
| 位阻 vs 电子 | TRADE_02_steric_vs_electronic_v1 |
| 动力学 vs 热力学 | TRADE_03_kinetic_vs_thermo_v1 |
| 界面悖论 | TRADE_04_interface_paradox_v1 |
| LUMO 环张力 | LUMO_04_ring_strain_v1 |
| HOMO 取代基调制 | HOMO_05_substituent_mod_v1 |

## Triggers for This Skill

调用本 skill 当：
- 需要快速检查评估结论是否有常见错误
- 作为其他模块的最终校验层
- 需要给用户解释"为什么直觉可能是错的"

## Guardrails
- **这是检查清单，不是评估工具**：需要配合其他模块使用
- **不是所有"陷阱"都会发生**：只是提醒可能性
- **具体问题具体分析**：这里只提供警示框架
- **更新迭代**：发现新的误判模式应添加


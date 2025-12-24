# TRADE_02_steric_vs_electronic_v1 — 位阻效应 vs 电子效应：权衡与边界

## Purpose
警示过度依赖电子效应而忽略位阻/空间效应的推断陷阱，提供具体权衡案例。

## Common Pitfall

```yaml
pitfall: "只考虑电子效应（±I/±M）来预测反应性和稳定性"
         "忽略分子的三维结构对界面接触的影响"
```

## Counterexamples

### 反例 1: 大体积取代基的保护效应

```yaml
structure: "2,6-二叔丁基苯酚 vs 苯酚"
electronic_prediction: "类似（都是酚）"
actual: "2,6-二叔丁基苯酚是著名的抗氧化剂，酚羟基被保护"
mechanism: |
  - 叔丁基体积大，物理屏蔽酚羟基
  - 氧化剂难以接近 O-H 位点
  - 电子效应（弱 +I）次要
  - 主要是空间屏蔽效应
correction: "位阻可以压过电子效应"
```

### 反例 2: 邻位效应使共轭失效

```yaml
structure: "2,6-二甲基苯胺 vs 苯胺"
electronic_prediction: "甲基 +I 使胺基更易氧化"
actual: "邻位位阻使苯胺的孤对无法有效共轭"
mechanism: |
  - 邻位取代导致 N 与芳环不共面
  - +M 效应被构象切断
  - N 孤对 HOMO 可能实际更局域
correction: "位阻影响共轭，间接改变电子效应"
```

### 反例 3: 界面吸附取向

```yaml
structure: "大体积溶剂分子 vs 小体积溶剂分子"
electronic_prediction: "按 HOMO/LUMO 排序"
actual: "大体积分子可能无法平躺吸附，接触点不同"
mechanism: |
  - 分子在电极表面的吸附取向
  - 大体积部分可能背离电极
  - 电子转移路径改变
  - HOMO/LUMO 分析可能不直接适用
correction: "界面反应需考虑吸附几何"
```

### 反例 4: SN2 vs SN1 的选择

```yaml
structure: "叔丁基卤 vs 甲基卤"
electronic_prediction: "三级更稳定碳正离子，SN1 倾向"
actual: "三级碳因位阻完全阻止 SN2"
mechanism: |
  - 位阻决定反应机理选择
  - 电子效应决定各机理的活性
  - 两者相互作用
correction: "机理选择常由位阻主导"
```

### 反例 5: 表面活性与内在活性

```yaml
structure: "聚合物添加剂 vs 小分子"
electronic_prediction: "按官能团活性"
actual: "聚合物可能在界面形成物理阻挡层"
mechanism: |
  - 聚合物覆盖电极表面
  - 阻止溶剂分子接触电极
  - 物理屏蔽 > 化学稳定性
correction: "物理阻挡可替代化学稳定性"
```

## Trade-off Decision Framework

```
1. 位阻效应占主导的情况：
   - 邻位大取代基（构象扭转）
   - 三级碳中心（反应物/试剂接近困难）
   - 界面吸附（接触点选择）
   - 聚合物/大分子

2. 电子效应占主导的情况：
   - 小分子、无位阻
   - 反应发生在远离位阻的位置
   - 体相溶液反应（无界面）
   - 单电子转移（距离依赖性弱）

3. 两者平衡的情况：
   - 中等大小取代基
   - 多位点竞争
   - 需要综合判断
```

## Quantitative Intuition (Qualitative)

| 取代基 | 位阻等级 | 电子效应 | 通常主导 |
|--------|----------|----------|----------|
| H | 无 | — | 电子效应 |
| Me | 小 | 弱 +I | 电子效应 |
| Et | 小 | 弱 +I | 电子效应 |
| iPr | 中 | 中 +I | 可能平衡 |
| tBu | 大 | 中 +I | 位阻效应 |
| Ph | 中 | +M/-I | 可能平衡 |
| OMe | 小 | +M | 电子效应 |
| NMe₂ | 中 | 强 +M | 电子效应 |
| CF₃ | 中 | 强 -I | 电子效应 |
| adamantyl | 极大 | 中 +I | 位阻效应 |

## When Steric Effects Dominate

```yaml
steric_dominant_scenarios:
  - description: "邻位取代导致平面性破坏"
    indicator: "ortho 取代芳环"
  
  - description: "三级碳或新戊基型"
    indicator: "季碳中心"
  
  - description: "界面反应"
    indicator: "电极/界面场景"
  
  - description: "大环/笼状分子"
    indicator: "内部空间受限"
```

## Triggers for This Skill

调用本 skill 当：
- 分子含有邻位大取代基
- 涉及三级碳反应中心
- 界面吸附/反应场景
- 评估结论只基于电子效应

## Guardrails
- **三维思考**：不能只看二维结构式
- **构象考虑**：位阻可能改变构象，间接影响电子效应
- **场景依赖**：界面 vs 体相，位阻影响不同
- **不绝对化**：位阻和电子效应都需要考虑


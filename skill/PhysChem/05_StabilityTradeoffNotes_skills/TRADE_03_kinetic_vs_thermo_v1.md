# TRADE_03_kinetic_vs_thermo_v1 — 动力学 vs 热力学：稳定≠不反应

## Purpose
辨析"热力学稳定"与"动力学惰性"的区别，警示将两者混淆的推断陷阱。

## Common Pitfall

```yaml
pitfall: "HOMO 低 / LUMO 高 = 稳定 = 不会反应"
         "热力学上不利的反应不会发生"
```

## Core Concept

```
热力学稳定性（Thermodynamic Stability）
  └─ 描述：最终状态的能量关系
  └─ 指标：ΔG、平衡常数、HOMO/LUMO 能级
  └─ 回答："反应倾向是什么"

动力学惰性（Kinetic Inertness）
  └─ 描述：反应速率的快慢
  └─ 指标：活化能、能垒、过渡态稳定性
  └─ 回答："反应速度如何"

关键洞察：
  热力学有利 + 动力学有利 → 快速反应 ✓
  热力学有利 + 动力学不利 → 慢反应 / 需催化
  热力学不利 + 动力学有利 → 可能发生（如果有外部驱动）
  热力学不利 + 动力学不利 → 不反应
```

## Counterexamples

### 反例 1: 钻石 vs 石墨

```yaml
structure: "钻石"
thermodynamic: "钻石热力学上不如石墨稳定"
actual: "钻石在常温常压下不会转化为石墨"
mechanism: |
  - sp³ → sp² 转化需要极高活化能
  - C-C 键重组的能垒巨大
  - 动力学惰性保护了热力学不稳定相
correction: "热力学不稳定可以被动力学惰性保护"
```

### 反例 2: 高能材料在室温稳定

```yaml
structure: "TNT、HMX 等含能材料"
thermodynamic: "分解释放大量能量，热力学极有利"
actual: "室温下可稳定储存"
mechanism: |
  - 分解反应的活化能高
  - 需要引发（热、冲击）才能启动
  - 动力学能垒保护
correction: "极高热力学驱动力可被动力学能垒阻止"
```

### 反例 3: SEI 的形成悖论

```yaml
structure: "EC 在石墨负极"
thermodynamic: "EC 在低电位热力学上应该还原"
actual: "首周还原后形成 SEI，后续不再反应"
mechanism: |
  - 首周：热力学驱动还原
  - 形成 SEI 后：电子绝缘层
  - 动力学阻断：电子无法穿过 SEI
correction: "产物可以改变动力学，即使热力学驱动不变"
```

### 反例 4: 催化改变一切

```yaml
structure: "H₂ + O₂ → H₂O"
thermodynamic: "极有利（ΔG << 0）"
actual: "室温混合不反应"
mechanism: |
  - O=O 键解离能垒高
  - 需要点火或催化剂
  - 催化剂降低活化能
correction: "催化可以打开热力学有利的反应通道"
```

### 反例 5: 亚稳态的长期存在

```yaml
structure: "过饱和溶液、过冷液体"
thermodynamic: "应该结晶 / 凝固"
actual: "可以长期存在"
mechanism: |
  - 成核需要克服界面能
  - 成核能垒是动力学障碍
  - 一旦成核，快速生长
correction: "亚稳态可以长期存在于动力学陷阱中"
```

## Implications for Electrochemistry

```yaml
application_1:
  scenario: "正极氧化稳定性"
  thermodynamic: "高 HOMO 意味着热力学上更易氧化"
  kinetic: "但如果电子转移路径被阻断，实际可能稳定"
  example: "某些聚合物添加剂形成物理阻挡层"

application_2:
  scenario: "负极还原稳定性"
  thermodynamic: "低 LUMO 意味着热力学上更易还原"
  kinetic: "SEI 形成后，电子转移被阻断"
  example: "EC 首周分解后稳定化"

application_3:
  scenario: "添加剂设计"
  strategy: "利用动力学控制热力学不利的过程"
  example: "成膜添加剂优先分解，保护溶剂"
```

## Decision Framework

```
评估反应性时需要考虑：

1. 热力学驱动力
   - HOMO/LUMO 能级 → 氧化/还原倾向
   - ΔG → 反应方向

2. 动力学能垒
   - 有无催化剂？
   - 有无物理阻挡（SEI/CEI）？
   - 电子转移路径是否畅通？

3. 综合判断
   - 热力学告诉你"想不想反应"
   - 动力学告诉你"能不能反应"
   - 两者都需要
```

## Triggers for This Skill

调用本 skill 当：
- 评估结论包含"稳定所以不会反应"
- 涉及界面膜（SEI/CEI）的讨论
- 讨论催化剂/添加剂效果
- 需要区分热力学与动力学因素

## Guardrails
- **两个维度**：热力学和动力学都需评估
- **不能只看能级**：HOMO/LUMO 是热力学指标
- **考虑界面效应**：SEI/CEI 改变动力学
- **时间尺度**：动力学问题与时间尺度相关


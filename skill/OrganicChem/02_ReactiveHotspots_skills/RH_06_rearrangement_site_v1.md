# RH_06_rearrangement_site_v1 — 重排倾向位点识别

## Triggers
- 需要识别分子中可能发生重排反应的位点
- 需要评估迁移基团和驱动力
- 需要预测重排类型

## Inputs
- 分子表示：SMILES / 结构描述
- 骨架信息（推荐）：来自 SD_02 的 skeleton
- 官能团信息（推荐）：来自 SD_03 的 functional_groups

## Outputs
```yaml
rearrangement_sites:
  - site_id: "RE_1"
    rearrangement_type: "1,2-hydride | 1,2-methyl | 1,2-aryl | Wagner-Meerwein | pinacol | Cope | Claisen | oxy-Cope | Beckmann | Baeyer-Villiger | other"
    migrating_group: "<迁移基团描述>"
    origin_atom: <int>                 # 迁移起始原子
    destination_atom: <int>            # 迁移目标原子
    trigger_type: "carbocation | thermal | oxidative | base_induced"
    driving_force: "<驱动力说明>"
    stability_gain: "high | moderate | low"
    prerequisite: "<前置条件>"
    confidence: <0.0-1.0>
    notes: "<补充说明>"
```

## Rules

### 重排反应类型

#### 1. 碳正离子重排（1,2-迁移）

| 迁移基团 | 迁移能力 | 条件 |
|----------|---------|------|
| H | 高 | 相邻碳正离子 |
| 烷基 | 中-高 | 稳定更好的碳正离子 |
| 芳基 | 高 | 苯基可稳定正电荷 |
| 乙烯基 | 高 | 共轭稳定 |

**迁移倾向排序**: 3° > 苄基 ≈ 烯丙基 > 2° > 1° > 甲基

#### 2. 协同重排（周环反应）

| 重排类型 | 电子数 | 条件 |
|----------|--------|------|
| Cope | [3,3]-σ | 热 |
| Claisen | [3,3]-σ | 热 |
| oxy-Cope | [3,3]-σ | 碱催化 |

#### 3. 氧化重排

| 重排类型 | 底物 | 产物 |
|----------|------|------|
| Baeyer-Villiger | 酮 | 酯/内酯 |
| Beckmann | 肟 | 酰胺 |

### 重排驱动力

| 驱动力 | 说明 |
|--------|------|
| 碳正离子稳定化 | 1° → 2° → 3°，或苄基/烯丙基 |
| 环张力释放 | 小环扩环 |
| 芳香化 | 形成芳香环 |
| 共轭稳定 | 形成共轭体系 |
| 热力学 | ΔG < 0 |

### 常见重排识别模式

| 模式 | 重排类型 | 触发条件 |
|------|----------|---------|
| 邻位有 H/烷基的碳正离子 | 1,2-迁移 | 碳正离子生成 |
| 1,5-二烯 | Cope | 加热 |
| 烯丙基乙烯基醚 | Claisen | 加热 |
| 环丙基甲基碳正离子 | 扩环 | 碳正离子生成 |
| 1,2-二醇 + 酸 | pinacol | 酸催化 |
| 酮 + 过氧化物 | Baeyer-Villiger | 氧化剂 |

## Steps
1. **识别潜在碳正离子中心**
   - 叔卤代物、苄基/烯丙基卤化物

2. **检查邻位迁移基团**
   - H、烷基、芳基、乙烯基

3. **评估迁移驱动力**
   - 比较迁移前后的碳正离子稳定性

4. **识别协同重排底物**
   - 1,5-二烯（Cope）、烯丙基乙烯基醚（Claisen）

5. **识别氧化重排底物**
   - 酮（Baeyer-Villiger）、肟（Beckmann）

## Examples

**Example 1: 2-甲基-2-丁醇（可能的 pinacol-like 重排）**
```yaml
input: "CC(C)(O)CC"
output:
  rearrangement_sites:
    - site_id: "RE_1"
      rearrangement_type: "1,2-methyl"
      migrating_group: "甲基"
      origin_atom: 0
      destination_atom: 1
      trigger_type: "carbocation"
      driving_force: "形成更稳定的碳正离子（若脱水）"
      prerequisite: "酸催化脱水形成碳正离子"
      stability_gain: "low"
      confidence: 0.6
      notes: "若脱水形成碳正离子，可能发生甲基迁移"
```

**Example 2: 新戊基碳正离子**
```yaml
input: "CC(C)(C)C[+]"  # 表示碳正离子
output:
  rearrangement_sites:
    - site_id: "RE_1"
      rearrangement_type: "1,2-methyl"
      migrating_group: "甲基"
      origin_atom: 1
      destination_atom: 4
      trigger_type: "carbocation"
      driving_force: "1° 碳正离子 → 3° 碳正离子"
      stability_gain: "high"
      confidence: 0.95
      notes: "新戊基碳正离子经典重排"
```

**Example 3: 1,5-己二烯（Cope 重排）**
```yaml
input: "C=CCC=CC"
output:
  rearrangement_sites:
    - site_id: "RE_1"
      rearrangement_type: "Cope"
      migrating_group: "3,3-σ 迁移"
      origin_atom: 0
      destination_atom: 5
      trigger_type: "thermal"
      driving_force: "热力学平衡（若取代不对称可能有偏好）"
      prerequisite: "加热"
      stability_gain: "moderate"
      confidence: 0.8
      notes: "[3,3]-σ 迁移，可逆"
```

**Example 4: 烯丙基乙烯基醚（Claisen 重排）**
```yaml
input: "C=CCOC=C"
output:
  rearrangement_sites:
    - site_id: "RE_1"
      rearrangement_type: "Claisen"
      migrating_group: "烯丙基"
      origin_atom: 0
      destination_atom: 4
      trigger_type: "thermal"
      driving_force: "生成 γ,δ-不饱和羰基化合物"
      prerequisite: "加热（~150-200°C）"
      stability_gain: "high"
      confidence: 0.9
      notes: "不可逆，因生成羰基"
```

**Example 5: 环己酮（Baeyer-Villiger 底物）**
```yaml
input: "C1CCCCC1=O"
output:
  rearrangement_sites:
    - site_id: "RE_1"
      rearrangement_type: "Baeyer-Villiger"
      migrating_group: "环己基"
      origin_atom: 0
      destination_atom: 6
      trigger_type: "oxidative"
      driving_force: "氧插入形成内酯"
      prerequisite: "过氧酸（如 m-CPBA）"
      stability_gain: "moderate"
      confidence: 0.85
      notes: "生成七元内酯（己内酯）"
```

**Example 6: 频哪醇（pinacol 重排）**
```yaml
input: "CC(C)(O)C(C)(C)O"
output:
  rearrangement_sites:
    - site_id: "RE_1"
      rearrangement_type: "pinacol"
      migrating_group: "甲基"
      origin_atom: 0
      destination_atom: 3
      trigger_type: "carbocation"
      driving_force: "1,2-二醇 → 酮（更稳定）"
      prerequisite: "酸催化"
      stability_gain: "high"
      confidence: 0.9
      notes: "经典 pinacol 重排，生成频哪酮"
```

## Guardrails
- 碳正离子重排需确认碳正离子能够生成
- 协同重排需检查几何要求
- 不预测重排产率或竞争关系
- 对于复杂多取代体系，降低置信度

## Confusable Cases
- 1,2-H 迁移 vs 消除：条件依赖
- Cope vs Claisen：前者纯碳，后者含 O
- Wagner-Meerwein vs 普通 1,2-迁移：Wagner-Meerwein 特指环系扩环

## Changelog
- 2025-12-24: 初始版本


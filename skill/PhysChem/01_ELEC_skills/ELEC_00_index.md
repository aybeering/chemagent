# ELEC_00_index — 电子效应 Skill 注册表

| Field | Value |
|---|---|
| Registry | ELEC Prompt Skills |
| Schema | `ELEC_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Count | 6 |

本注册表用于索引"电子效应分析"相关的 Prompt Skills。  
每张卡片是一个 **ELEC prompt skill**，用于判断取代基对目标位点的电子推/拉方向、传递路径、衰减与主导机制。

---

## 1. 全量清单（按 Skill ID）

| Skill ID | 中文名 | 功能简述 | 关键词 | File |
|---|---|---|---|---|
| `ELEC_01_effect_flowmap_v1` | 电子效应总路由 | 总装配与冲突消解：推/拉从哪里来、怎么传 | `routing, channel-fusion, net-effect` | [ELEC_01_effect_flowmap_v1.md](ELEC_01_effect_flowmap_v1.md) |
| `ELEC_02_I_sigma_v1` | ±I 诱导效应 | σ 键传递与快速衰减，局部极化 | `sigma, inductive, decay` | [ELEC_02_I_sigma_v1.md](ELEC_02_I_sigma_v1.md) |
| `ELEC_03_M_pi_v1` | ±M 共振效应 | π 共轭网络传递，位点选择性（o/m/p） | `pi, resonance, selectivity` | [ELEC_03_M_pi_v1.md](ELEC_03_M_pi_v1.md) |
| `ELEC_04_hyperconj_v1` | 超共轭 | σ-π 耦合：烷基给电子、苄/烯丙位稳定化 | `hyperconjugation, stabilization` | [ELEC_04_hyperconj_v1.md](ELEC_04_hyperconj_v1.md) |
| `ELEC_05_field_v1` | 场效应 | 偶极/电荷近邻的空间极化与位点偏置 | `field, polarization, interface` | [ELEC_05_field_v1.md](ELEC_05_field_v1.md) |
| `ELEC_06_conformation_switch_v1` | 构象共轭开关 | 扭转/位阻/sp³隔断导致共振降权或切断 | `conformation, planarity, gating` | [ELEC_06_conformation_switch_v1.md](ELEC_06_conformation_switch_v1.md) |

---

## 2. 建议调用顺序（Pipeline）

```
1. ELEC_01_effect_flowmap_v1（总路由与通道汇总）
   │
   ├─► 2. ELEC_06_conformation_switch_v1（先判共轭是否开）
   │
   ├─► 3. ELEC_03_M_pi_v1（π 共振通道）
   │
   ├─► 4. ELEC_02_I_sigma_v1（σ 诱导通道）
   │
   ├─► 5. ELEC_04_hyperconj_v1（超共轭/σ-π耦合）
   │
   ├─► 6. ELEC_05_field_v1（场效应/空间极化）
   │
   └─► 7. 返回 ELEC_01 做最终加权汇总与结论解释
```

---

## 3. 按通道类型索引

### σ 通道（键传递）
- `ELEC_02_I_sigma_v1` — [±I 诱导效应](ELEC_02_I_sigma_v1.md)
- `ELEC_04_hyperconj_v1` — [超共轭/σ-π 耦合](ELEC_04_hyperconj_v1.md)

### π 通道（共轭传递）
- `ELEC_03_M_pi_v1` — [±M 共振效应](ELEC_03_M_pi_v1.md)
- `ELEC_06_conformation_switch_v1` — [构象共轭开关](ELEC_06_conformation_switch_v1.md)

### 空间通道（Through-Space）
- `ELEC_05_field_v1` — [场效应/电场极化](ELEC_05_field_v1.md)

### 总路由
- `ELEC_01_effect_flowmap_v1` — [电子效应总路由](ELEC_01_effect_flowmap_v1.md)

---

## 4. 检索标签（Tag → Skill）

| 标签 | Skill ID |
|---|---|
| `σ传递` / `诱导` / `衰减` | ELEC_02_I_sigma_v1 |
| `π共轭` / `共振` / `邻对间` / `o/m/p` | ELEC_03_M_pi_v1 |
| `超共轭` / `烷基给电子` / `苄位稳定` / `β-硅` | ELEC_04_hyperconj_v1 |
| `强电场` / `偶极` / `空间近邻` / `界面` | ELEC_05_field_v1 |
| `共面性` / `位阻` / `扭转` / `共轭切断` | ELEC_06_conformation_switch_v1 |
| `综合判定` / `冲突消解` / `通道汇总` | ELEC_01_effect_flowmap_v1 |

---

## 5. 易混淆索引（用于路由与消歧）

| Skill | 易混淆 Skill | 消歧说明 |
|---|---|---|
| `ELEC_02_I_sigma_v1` | `ELEC_03_M_pi_v1` | 卤素在芳环上同时有 −I 与 +M，需分别调用两卡汇总 |
| `ELEC_03_M_pi_v1` | `ELEC_06_conformation_switch_v1` | 共振效应需先经构象开关判断是否 ON/OFF/PARTIAL |
| `ELEC_04_hyperconj_v1` | `ELEC_03_M_pi_v1` | 苄位/烯丙位稳定化需区分 π 离域与 σ-π 耦合的贡献 |
| `ELEC_05_field_v1` | `ELEC_02_I_sigma_v1` | 场效应为空间通道，诱导效应为键通道，需并行评估 |

---

## 6. 依赖关系

```
ELEC_01_effect_flowmap_v1
    ├── depends_on: [ELEC_02, ELEC_03, ELEC_04, ELEC_05, ELEC_06]
    └── 作为总路由调用所有子技能卡

ELEC_03_M_pi_v1
    └── may_call: ELEC_06_conformation_switch_v1（构象检查）

其他 Skill
    └── 独立执行，结果汇总至 ELEC_01
```

---

## 7. 使用建议（编排）

1. **单一问题**（如"CF₃ 是推还是拉"）：可直接调用 `ELEC_02_I_sigma_v1` 或相关单卡。
2. **复杂分析**（如"对某位点的净电子效应"）：走完整 Pipeline，从 `ELEC_01_effect_flowmap_v1` 开始。
3. **构象敏感体系**：优先调用 `ELEC_06_conformation_switch_v1` 判断共振通道是否有效。
4. **界面/强电场环境**：上调 `ELEC_05_field_v1` 的权重。

---

## 8. 与其他 Skill 模块的联动

| 场景 | 联动模块 |
|---|---|
| 需要判断反应位点 | → `site_skills/SITE_*_v1` |
| 需要预测具体反应 | → `reaction/*_01.md` |
| 需要氧化/还原稳定性分析 | → `PhysChem/04_Oxid&redStability/` |
| 需要轨道定性分析 | → `PhysChem/03_Orbital/` |

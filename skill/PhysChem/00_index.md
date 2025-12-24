# PhysChem — 物理化学专家技能库索引

| Field | Value |
|---|---|
| Registry | PhysChem Skill Modules |
| Created | 2025-12-24 |
| Module Count | 5 |
| Total Skills | 28 |
| Interface Files | 3 (Router, Schema, Guide) |

本索引文件用于快速检索物理化学专家的技能模块。每个子目录是一个独立的技能模块，包含多个相关的 Prompt Skills。

---

## 上游接口（推荐入口）

上游 Agent（如电化学专家）应通过以下标准化接口调用 PhysChem 技能库：

| 文件 | 用途 | 说明 |
|------|------|------|
| [PhysChem_Router.md](PhysChem_Router.md) | 统一入口路由 | 根据任务类型自动分发到具体模块 |
| [PhysChem_Schema.md](PhysChem_Schema.md) | I/O Schema 定义 | 标准化输入/输出数据结构 |
| [PhysChem_Integration_Guide.md](PhysChem_Integration_Guide.md) | 集成指南 | 调用示例、FAQ、最佳实践 |

### 快速调用示例

```yaml
call:
  target: PhysChem_Router
  input:
    molecule:
      smiles: "C1COC(=O)O1"
      name: "Ethylene Carbonate"
    task_type: "interface_ranking"  # 或 full_assessment / electronic_effect 等
    context:
      electrode: "both"
      environment: "interface"
```

### 支持的任务类型

| task_type | 描述 | 路由目标 |
|-----------|------|----------|
| `electronic_effect` | 电子效应分析 | ELEC_01 |
| `oxidation_tendency` | 氧化倾向评估 | HOMO_01 |
| `reduction_tendency` | 还原倾向评估 | LUMO_01 |
| `interface_ranking` | 界面位点排序 | INTF_01 |
| `stability_check` | 稳定性校验 | TRADE_05 |
| `full_assessment` | 完整评估 | INTF_01 + TRADE |

---

## 模块清单

| 模块 ID | 目录名 | 功能描述 | Skill 数量 |
|---------|--------|----------|------------|
| 01 | `01_ELEC_skills/` | 电子效应分析（±I/±M/超共轭/场效应） | 6 |
| 02 | `02_HOMO_OxTendency_Qual_skills/` | 氧化倾向定性评估（HOMO 趋势直觉） | 6 |
| 03 | `03_LUMO_RedTendency_Qual_skills/` | 还原倾向定性评估（LUMO 趋势直觉） | 6 |
| 04 | `04_InterfaceFirstStrikeSites_skills/` | 界面优先反应位点排序 | 5 |
| 05 | `05_StabilityTradeoffNotes_skills/` | 稳定性权衡与反例框架 | 5 |

---

## 模块间联动关系

```
                    ┌─────────────────┐
                    │  01_ELEC_skills │
                    │  电子效应分析    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────────┐  ┌─────────────────┐
    │ 02_HOMO_skills  │  │ 03_LUMO_skills  │
    │ 氧化倾向(HOMO)  │  │ 还原倾向(LUMO)  │
    └────────┬────────┘  └────────┬────────┘
             │                    │
             └──────────┬─────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ 04_Interface_skills │
              │   界面优先位点排序   │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │ 05_Tradeoff_skills  │
              │ 稳定性权衡/反例校验  │
              └─────────────────────┘
```

---

## 模块详情

### 01_ELEC_skills — 电子效应分析

**用途**：评估取代基对目标位点的电子推/拉方向、传递路径、衰减与主导机制。

**核心假设**：电子效应可分解为 ±I / ±M / 超共轭 / 场效应 / 构象开关

**包含 Skills**：
- `ELEC_01_effect_flowmap_v1` — 总路由与通道汇总
- `ELEC_02_I_sigma_v1` — ±I 诱导效应
- `ELEC_03_M_pi_v1` — ±M 共振效应
- `ELEC_04_hyperconj_v1` — 超共轭
- `ELEC_05_field_v1` — 场效应
- `ELEC_06_conformation_switch_v1` — 构象共轭开关

**索引文件**：[01_ELEC_skills/ELEC_00_index.md](01_ELEC_skills/ELEC_00_index.md)

---

### 02_HOMO_OxTendency_Qual_skills — 氧化倾向定性评估

**用途**：基于 HOMO 能级趋势，定性评估分子/位点的氧化敏感性，服务于电解液氧化稳定性分析。

**核心假设**：HOMO 能级越高 → 越易被氧化

**包含 Skills**：
- `HOMO_01_ox_flowmap_v1` — 氧化倾向总路由
- `HOMO_02_lonepair_n_v1` — 杂原子孤对 (n 轨道)
- `HOMO_03_pi_system_v1` — π 系统氧化倾向
- `HOMO_04_activated_CH_v1` — 活化 C-H 键
- `HOMO_05_substituent_mod_v1` — 取代基调制（ELEC 联动）
- `HOMO_06_interface_effect_v1` — 界面/电场修正

**索引文件**：[02_HOMO_OxTendency_Qual_skills/HOMO_00_index.md](02_HOMO_OxTendency_Qual_skills/HOMO_00_index.md)

---

### 03_LUMO_RedTendency_Qual_skills — 还原倾向定性评估

**用途**：基于 LUMO 能级趋势，定性评估分子/位点的还原敏感性，服务于电解液还原稳定性分析。

**核心假设**：LUMO 能级越低 → 越易被还原

**包含 Skills**：
- `LUMO_01_red_flowmap_v1` — 还原倾向总路由
- `LUMO_02_pi_antibond_v1` — π* 反键轨道
- `LUMO_03_sigma_antibond_v1` — σ* 反键轨道
- `LUMO_04_ring_strain_v1` — 环张力/小环
- `LUMO_05_substituent_mod_v1` — 取代基调制（ELEC 联动）
- `LUMO_06_interface_effect_v1` — 界面/电场修正

**索引文件**：[03_LUMO_RedTendency_Qual_skills/LUMO_00_index.md](03_LUMO_RedTendency_Qual_skills/LUMO_00_index.md)

---

### 04_InterfaceFirstStrikeSites_skills — 界面优先反应位点

**用途**：整合 HOMO/LUMO 评估结果，结合界面特性，给出"在电极界面，哪些位点会优先反应"的排序与理由。

**核心目标**：只给优先级与理由，不预测具体产物

**包含 Skills**：
- `INTF_01_firststrike_flowmap_v1` — 界面优先位点总路由
- `INTF_02_cathode_ranking_v1` — 正极界面排序（调用 HOMO）
- `INTF_03_anode_ranking_v1` — 负极界面排序（调用 LUMO）
- `INTF_04_competition_resolve_v1` — 竞争位点判定
- `INTF_05_film_formation_hint_v1` — SEI/CEI 成膜倾向提示

**索引文件**：[04_InterfaceFirstStrikeSites_skills/INTF_00_index.md](04_InterfaceFirstStrikeSites_skills/INTF_00_index.md)

---

### 05_StabilityTradeoffNotes_skills — 稳定性权衡与反例框架

**用途**：提供"反例框架"和"常见误判警示"，防止过度简化的结构-稳定性推断。

**核心目标**：提醒"X ≠ 万能"，避免错误的泛化推断

**包含 Skills**：
- `TRADE_01_ewg_not_always_v1` — 吸电子基≠万能稳定
- `TRADE_02_steric_vs_electronic_v1` — 位阻 vs 电子效应权衡
- `TRADE_03_kinetic_vs_thermo_v1` — 动力学 vs 热力学辨析
- `TRADE_04_interface_paradox_v1` — 界面悖论（牺牲型添加剂）
- `TRADE_05_common_pitfalls_v1` — 常见误判清单

**索引文件**：[05_StabilityTradeoffNotes_skills/TRADE_00_index.md](05_StabilityTradeoffNotes_skills/TRADE_00_index.md)

---

## 使用建议

### 推荐方式：通过 Router 调用

**上游 Agent 推荐使用 [PhysChem_Router.md](PhysChem_Router.md) 作为统一入口**，自动处理模块编排与结果汇总。

详细调用方式请参考 [PhysChem_Integration_Guide.md](PhysChem_Integration_Guide.md)。

### 直接调用（简单场景）

对于简单问题，可绕过 Router 直接调用单个模块：

| 场景 | 推荐入口 |
|------|----------|
| 评估电子效应 | `01_ELEC_skills/ELEC_01_effect_flowmap_v1` |
| 评估氧化倾向 | `02_HOMO_skills/HOMO_01_ox_flowmap_v1` |
| 评估还原倾向 | `03_LUMO_skills/LUMO_01_red_flowmap_v1` |
| 界面反应位点 | `04_INTF_skills/INTF_01_firststrike_flowmap_v1` |
| 校验结论/避免误判 | `05_TRADE_skills/TRADE_05_common_pitfalls_v1` |

**注意**：直接调用不经过 TRADE 校验，需用户自行判断是否需要附加校验。

### 完整评估流程

```
1. 输入分子结构
       │
       ▼
2. 调用 ELEC 模块获取电子效应
       │
       ├─► 3a. HOMO 模块（氧化倾向）
       │
       └─► 3b. LUMO 模块（还原倾向）
              │
              ▼
4. 调用 INTF 模块获取界面排序
       │
       ▼
5. 调用 TRADE 模块校验，避免误判
       │
       ▼
6. 输出最终结论
```

---

## 与其他模块的联动

| 联动模块 | 联动关系 |
|----------|----------|
| `site_skills/` | INTF 输出可供 SITE 使用 |
| `reaction/` | 位点排序可指导反应预测 |
| 上游 Agent | 通过 [PhysChem_Router](PhysChem_Router.md) 调用，输出遵循 [PhysChem_Schema](PhysChem_Schema.md) |

---

## 文件清单

```
skill/PhysChem/
├── 00_index.md                    # 本文件（总索引）
├── PhysChem_Router.md             # 统一入口路由
├── PhysChem_Schema.md             # I/O Schema 定义
├── PhysChem_Integration_Guide.md  # 上游 Agent 集成指南
├── 01_ELEC_skills/                # 电子效应模块
├── 02_HOMO_OxTendency_Qual_skills/  # 氧化倾向模块
├── 03_LUMO_RedTendency_Qual_skills/ # 还原倾向模块
├── 04_InterfaceFirstStrikeSites_skills/  # 界面位点模块
└── 05_StabilityTradeoffNotes_skills/     # 稳定性权衡模块
```

---

## Changelog

- 2025-12-24: 新增上游接口（Router、Schema、Integration Guide）
- 2025-12-24: 完成全部 5 个模块，共 28 个 skill 卡片

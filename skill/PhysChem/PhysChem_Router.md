# PhysChem_Router — 物理化学专家技能库统一入口

| Field | Value |
|-------|-------|
| Type | Router / Entry Point |
| Created | 2025-12-24 |
| Schema | `PhysChem_Schema.md` |

本文件是 PhysChem 技能库的**统一调用入口**。上游 Agent（如电化学专家）通过此 Router 访问所有物理化学评估能力。

---

## 1. 支持的任务类型

| `task_type` | 描述 | 路由目标 | 调用深度 |
|-------------|------|----------|----------|
| `electronic_effect` | 电子效应分析（±I/±M/超共轭/场效应） | `ELEC_01_effect_flowmap_v1` | 浅（仅 ELEC 模块） |
| `oxidation_tendency` | 氧化倾向定性评估 | `HOMO_01_ox_flowmap_v1` | 中（HOMO + ELEC） |
| `reduction_tendency` | 还原倾向定性评估 | `LUMO_01_red_flowmap_v1` | 中（LUMO + ELEC） |
| `interface_ranking` | 界面优先反应位点排序 | `INTF_01_firststrike_flowmap_v1` | 深（INTF → HOMO/LUMO → ELEC） |
| `stability_check` | 稳定性校验与误判警示 | `TRADE_05_common_pitfalls_v1` | 浅（仅 TRADE） |
| `full_assessment` | 完整评估（界面排序 + 校验） | `INTF_01` → `TRADE_*` | 完整 Pipeline |

---

## 2. 标准输入接口

```yaml
input:
  molecule:
    smiles: "<SMILES 字符串>"           # 必填
    name: "<分子名称>"                  # 可选
    functional_groups:                  # 可选，预识别的官能团
      - "<官能团1>"
      - "<官能团2>"
  
  task_type: "<任务类型>"               # 必填，见上表
  
  context:                              # 可选，环境上下文
    electrode: "cathode | anode | both" # 关注哪极，默认 both
    electrode_material: "<电极材料>"    # NCM / NCA / LCO / LFP / Li / Graphite / Si
    voltage_range: "high | normal | deep_reduction"  # 电位范围
    environment: "bulk | interface"     # 体相 vs 界面环境
  
  options:                              # 可选，高级选项
    include_trade_check: true           # 是否附加 TRADE 校验，默认 true
    output_format: "yaml | json"        # 输出格式，默认 yaml
    verbosity: "concise | detailed"     # 详细程度，默认 concise
```

---

## 3. 路由决策逻辑

```
接收 input
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 1: 验证输入格式（参考 PhysChem_Schema.md）     │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 2: 根据 task_type 选择路由                     │
│                                                     │
│   electronic_effect  ──► ELEC_01                    │
│   oxidation_tendency ──► HOMO_01                    │
│   reduction_tendency ──► LUMO_01                    │
│   interface_ranking  ──► INTF_01                    │
│   stability_check    ──► TRADE_05                   │
│   full_assessment    ──► INTF_01 + TRADE            │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 3: 执行 Pipeline                               │
│                                                     │
│   - 传递 molecule 和 context 给目标模块             │
│   - 按模块依赖顺序执行                              │
│   - 收集各模块输出                                  │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 4: 后置校验（若 include_trade_check = true）   │
│                                                     │
│   - 调用 TRADE 模块检查是否触犯已知反例             │
│   - 附加警示标注                                    │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 5: 汇总输出                                    │
│                                                     │
│   - 按 PhysChem_Schema.md 格式化响应                │
│   - 返回给上游 Agent                                │
└─────────────────────────────────────────────────────┘
```

---

## 4. 路由到模块的调用链

### 4.1 electronic_effect

```
Router ──► ELEC_01_effect_flowmap_v1
              │
              ├──► ELEC_06_conformation_switch_v1（构象检查）
              ├──► ELEC_03_M_pi_v1（π 共振）
              ├──► ELEC_02_I_sigma_v1（σ 诱导）
              ├──► ELEC_04_hyperconj_v1（超共轭）
              └──► ELEC_05_field_v1（场效应）
              
输出: effect_summary, channels, transmission_path, dominant_sites
```

### 4.2 oxidation_tendency

```
Router ──► HOMO_01_ox_flowmap_v1
              │
              ├──► HOMO_02_lonepair_n_v1（杂原子孤对）
              │        └──► HOMO_05 ──► [ELEC_*]
              ├──► HOMO_03_pi_system_v1（π 系统）
              │        └──► HOMO_05 ──► [ELEC_*]
              ├──► HOMO_04_activated_CH_v1（活化 C-H）
              │        └──► HOMO_05 ──► [ELEC_*]
              └──► HOMO_06_interface_effect_v1（界面修正）
              
输出: ox_sites_ranked, dominant_homo_type, substituent_effects
```

### 4.3 reduction_tendency

```
Router ──► LUMO_01_red_flowmap_v1
              │
              ├──► LUMO_02_pi_antibond_v1（π* 反键）
              │        └──► LUMO_05 ──► [ELEC_*]
              ├──► LUMO_03_sigma_antibond_v1（σ* 反键）
              │        └──► LUMO_05 ──► [ELEC_*]
              ├──► LUMO_04_ring_strain_v1（环张力）
              └──► LUMO_06_interface_effect_v1（界面修正）
              
输出: red_sites_ranked, dominant_lumo_type, substituent_effects
```

### 4.4 interface_ranking

```
Router ──► INTF_01_firststrike_flowmap_v1
              │
              ├──► INTF_02_cathode_ranking_v1
              │        └──► [HOMO_01 Pipeline]
              ├──► INTF_03_anode_ranking_v1
              │        └──► [LUMO_01 Pipeline]
              ├──► INTF_04_competition_resolve_v1
              └──► INTF_05_film_formation_hint_v1
              
输出: first_strike_sites (cathode + anode), competition_notes, film_hint
```

### 4.5 full_assessment

```
Router ──► INTF_01 Pipeline（同上）
              │
              ▼
        ──► TRADE_01_ewg_not_always_v1（吸电子≠万能）
        ──► TRADE_02_steric_vs_electronic_v1（位阻 vs 电子）
        ──► TRADE_03_kinetic_vs_thermo_v1（动力学 vs 热力学）
        ──► TRADE_04_interface_paradox_v1（界面悖论）
        ──► TRADE_05_common_pitfalls_v1（常见误判）
              
输出: 完整的 first_strike_sites + tradeoff_warnings
```

---

## 5. 标准输出格式

```yaml
output:
  task_completed: "<实际执行的任务类型>"
  molecule_echo:
    smiles: "<输入的 SMILES>"
    name: "<分子名称>"
  
  # 以下字段按任务类型填充
  
  # --- electronic_effect ---
  electronic_effect:
    effect_summary: "<净效应描述>"
    channels:
      I: { direction: "+/-", strength: "strong/moderate/weak", decay: "<衰减描述>" }
      M: { direction: "+/-", strength: "...", path: "o/m/p" }
      hyperconj: { active: true/false, description: "..." }
      field: { active: true/false, description: "..." }
    dominant_channel: "I | M | hyperconj | field | mixed"
    confidence: "high | medium | low"
  
  # --- oxidation_tendency ---
  oxidation_tendency:
    ox_sites_ranked:
      - rank: 1
        site: "<位点描述>"
        homo_type: "n | pi | sigma_CH"
        reason: "<理由>"
        confidence: "high | medium | low"
      - rank: 2
        site: "..."
    dominant_site: "<最易氧化位点>"
    substituent_effects: "<取代基调制摘要>"
  
  # --- reduction_tendency ---
  reduction_tendency:
    red_sites_ranked:
      - rank: 1
        site: "<位点描述>"
        lumo_type: "pi_star | sigma_star | ring_strain"
        reason: "<理由>"
        confidence: "high | medium | low"
      - rank: 2
        site: "..."
    dominant_site: "<最易还原位点>"
    substituent_effects: "<取代基调制摘要>"
  
  # --- interface_ranking ---
  interface_ranking:
    cathode:
      - rank: 1
        site: "<位点>"
        reason: "<理由>"
        confidence: "high | medium | low"
      - rank: 2
        site: "..."
    anode:
      - rank: 1
        site: "<位点>"
        reason: "<理由>"
        confidence: "high | medium | low"
      - rank: 2
        site: "..."
    competition_notes: "<多位点竞争判定>"
    film_hint: "<SEI/CEI 成膜提示>"
  
  # --- stability_check / full_assessment 附加 ---
  tradeoff_warnings:
    triggered_pitfalls:
      - pitfall_id: "TRADE_01 | TRADE_02 | ..."
        warning: "<警示内容>"
        applies_to: "<涉及的结论>"
    confidence_adjustment: "none | lowered | requires_review"
  
  # --- 通用字段 ---
  notes: "<补充说明>"
  overall_confidence: "high | medium | low"
```

---

## 6. 快捷调用（直连单卡）

对于简单问题，可绕过 Router 直接调用单卡：

| 问题类型 | 直接调用 |
|----------|----------|
| "CF₃ 是推还是拉？" | `ELEC_02_I_sigma_v1` |
| "这个胺氮容易氧化吗？" | `HOMO_02_lonepair_n_v1` |
| "羰基容易被还原吗？" | `LUMO_02_pi_antibond_v1` |
| "负极界面哪里先反应？" | `INTF_03_anode_ranking_v1` |

**注意**：直连调用不经过 TRADE 校验，需用户自行判断是否需要附加校验。

---

## 7. 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| `task_type` 无效 | 返回错误提示，列出有效选项 |
| `smiles` 解析失败 | 返回错误，要求提供有效 SMILES 或结构描述 |
| 模块执行异常 | 返回部分结果 + 错误标注，降低 `overall_confidence` |
| 置信度过低 | 在 `notes` 中标注"建议人工复核"或"需补充计算数据" |

---

## 8. 与上游 Agent 的协议

### 调用示例

```yaml
# 示例 1: 评估 EC 在负极的稳定性
call:
  target: PhysChem_Router
  input:
    molecule:
      smiles: "C1COC(=O)O1"
      name: "Ethylene Carbonate"
    task_type: "interface_ranking"
    context:
      electrode: "anode"
      electrode_material: "Li"
      voltage_range: "deep_reduction"

# 示例 2: 快速判断取代基效应
call:
  target: PhysChem_Router
  input:
    molecule:
      smiles: "FC(F)(F)c1ccccc1"
      name: "Trifluoromethylbenzene"
    task_type: "electronic_effect"
    context:
      environment: "bulk"
```

### 返回约定

- 上游 Agent 应解析 `output` 结构，提取所需字段
- `overall_confidence` 为 `low` 时，建议在最终报告中标注不确定性
- `tradeoff_warnings` 非空时，应在报告中附加警示说明

---

## 9. Changelog

- 2025-12-24: 初始版本，支持 6 种任务类型路由


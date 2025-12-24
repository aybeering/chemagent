# PhysChem_Integration_Guide — 上游 Agent 集成指南

| Field | Value |
|-------|-------|
| Type | Integration Guide |
| Created | 2025-12-24 |
| Audience | 上游 Agent 开发者 / 电化学专家 Agent |

本文档为上游 Agent（如电化学专家）提供 PhysChem 技能库的集成指南。

---

## 1. 快速开始

### 1.1 最简调用

```yaml
# 评估分子的界面反应位点
call:
  target: PhysChem_Router
  input:
    molecule:
      smiles: "C1COC(=O)O1"  # EC
    task_type: "interface_ranking"
```

### 1.2 三种典型场景

| 场景 | task_type | 说明 |
|------|-----------|------|
| "这个分子在负极稳定吗？" | `reduction_tendency` | 评估还原倾向 |
| "正极界面哪里先反应？" | `interface_ranking` + `electrode: cathode` | 正极位点排序 |
| "完整评估电解液添加剂" | `full_assessment` | 全流程 + 校验 |

---

## 2. 任务类型选择决策树

```
你想分析什么？
    │
    ├─► 取代基的电子效应（推/拉）
    │       └─► task_type: "electronic_effect"
    │
    ├─► 分子的氧化敏感性
    │       └─► task_type: "oxidation_tendency"
    │
    ├─► 分子的还原敏感性
    │       └─► task_type: "reduction_tendency"
    │
    ├─► 电极界面的优先反应位点
    │       │
    │       ├─► 只关心正极 ──► electrode: "cathode"
    │       ├─► 只关心负极 ──► electrode: "anode"
    │       └─► 都要 ──────► electrode: "both"
    │       └─► task_type: "interface_ranking"
    │
    ├─► 校验结论是否有反例/误判风险
    │       └─► task_type: "stability_check"
    │
    └─► 完整评估（界面 + 校验）
            └─► task_type: "full_assessment"
```

---

## 3. 完整调用示例

### 3.1 示例：评估 EC 的完整电化学行为

**请求**：
```yaml
call:
  target: PhysChem_Router
  input:
    molecule:
      smiles: "C1COC(=O)O1"
      name: "Ethylene Carbonate"
    task_type: "full_assessment"
    context:
      electrode: "both"
      electrode_material: "Li"
      voltage_range: "normal"
      environment: "interface"
    options:
      include_trade_check: true
      verbosity: "detailed"
```

**响应**：
```yaml
output:
  task_completed: "full_assessment"
  molecule_echo:
    smiles: "C1COC(=O)O1"
    name: "Ethylene Carbonate"
    identified_groups: ["cyclic_carbonate", "ester", "ether"]
  
  interface_ranking:
    cathode:
      - rank: 1
        site: "酯氧孤对"
        reason: "最高 HOMO 贡献者（n 轨道）"
        confidence: "medium"
      - rank: 2
        site: "亚甲基 C-H"
        reason: "次高 HOMO（α-醚活化）"
        confidence: "low"
    anode:
      - rank: 1
        site: "羰基 C=O"
        reason: "最低 LUMO（π* 反键）"
        confidence: "high"
      - rank: 2
        site: "酯基 C-O 键"
        reason: "开环位点（σ* 反键）"
        confidence: "high"
    competition_notes: "羰基还原后开环，两个位点依序反应"
    film_hint: "负极还原开环形成 SEI；正极相对稳定"
    confidence: "high"
  
  tradeoff_warnings:
    triggered_pitfalls: []
    confidence_adjustment: "none"
  
  notes: "EC 在负极界面优先被还原，是 SEI 的重要组分"
  overall_confidence: "high"
```

### 3.2 示例：快速判断电子效应

**请求**：
```yaml
call:
  target: PhysChem_Router
  input:
    molecule:
      smiles: "FC(F)(F)c1ccccc1"
      name: "Trifluoromethylbenzene"
    task_type: "electronic_effect"
```

**响应**：
```yaml
output:
  task_completed: "electronic_effect"
  molecule_echo:
    smiles: "FC(F)(F)c1ccccc1"
    name: "Trifluoromethylbenzene"
  
  electronic_effect:
    effect_summary: "CF₃ 对芳环为强 -I 吸电子，无 +M 贡献（sp³ 碳隔断共轭）"
    channels:
      I:
        active: true
        direction: "-I"
        strength: "strong"
        decay: "主要影响苯环 o/m/p 位，邻位最强"
      M:
        active: false
        direction: null
        strength: null
      hyperconj:
        active: false
        description: "CF₃ 无合适 σ 供体"
      field:
        active: true
        description: "C-F 偶极产生弱场效应"
    dominant_channel: "I"
    transmission_path: "CF₃ → (sp³ C) → 芳环 σ 框架 → 各位点"
    dominant_sites: ["ortho-C", "para-C"]
    confidence: "high"
  
  overall_confidence: "high"
```

### 3.3 示例：添加剂评估（FEC）

**请求**：
```yaml
call:
  target: PhysChem_Router
  input:
    molecule:
      smiles: "C1C(F)OC(=O)O1"
      name: "Fluoroethylene Carbonate"
    task_type: "full_assessment"
    context:
      electrode: "anode"
      electrode_material: "Li"
      voltage_range: "deep_reduction"
```

**响应**（关键部分）：
```yaml
output:
  interface_ranking:
    anode:
      - rank: 1
        site: "羰基 C=O"
        reason: "π* LUMO，被 F 的 -I 进一步降低"
        confidence: "high"
      - rank: 2
        site: "C-F 键"
        reason: "σ*(C-F) 可接受电子，释放 F⁻"
        confidence: "high"
    film_hint: "优先还原；F⁻ 释放促进 LiF 富集 SEI"
  
  tradeoff_warnings:
    triggered_pitfalls:
      - pitfall_id: "TRADE_04"
        warning: "FEC 属于牺牲型添加剂，不稳定是设计特性"
        applies_to: "整体稳定性评价"
    confidence_adjustment: "none"
    review_notes: "不应将 FEC 的低还原稳定性视为缺点"
```

---

## 4. 上下文参数详解

### 4.1 electrode（电极类型）

| 值 | 含义 | 影响 |
|----|------|------|
| `cathode` | 仅正极 | 只调用 HOMO 相关模块 |
| `anode` | 仅负极 | 只调用 LUMO 相关模块 |
| `both` | 双极（默认） | 完整评估 |

### 4.2 electrode_material（电极材料）

| 材料 | 正极/负极 | 特殊考虑 |
|------|-----------|----------|
| `NCM` / `NCA` / `LCO` | 正极 | 高压时氧化性更强 |
| `LFP` | 正极 | 电位较低，相对温和 |
| `Li` | 负极 | 极强还原性，深度还原 |
| `Graphite` | 负极 | SEI 形成关键 |
| `Si` | 负极 | 体积膨胀带来额外应力 |

### 4.3 voltage_range（电位范围）

| 值 | 电位范围 | 典型场景 |
|----|----------|----------|
| `high` | >4.3V vs Li/Li+ | 高压 NCM811 / NCA |
| `normal` | 2.5-4.3V | 常规锂离子电池 |
| `deep_reduction` | <0.5V | 首次锂化、锂金属负极 |

### 4.4 environment（环境）

| 值 | 含义 | 影响 |
|----|------|------|
| `bulk` | 体相溶液 | 不考虑界面特殊效应 |
| `interface` | 电极界面 | 调用 `*_06_interface_effect` 模块 |

---

## 5. 置信度解读与处理建议

### 5.1 置信度含义

| 置信度 | 含义 | 上游处理建议 |
|--------|------|--------------|
| `high` | 结论明确可靠 | 可直接引用 |
| `medium` | 存在竞争因素或边界情况 | 在报告中标注"可能" |
| `low` | 需要验证 | 建议补充 DFT 计算或实验 |

### 5.2 置信度传递规则

```
最终置信度 = min(各模块置信度)

示例：
  HOMO_02 → high
  HOMO_05 (ELEC) → medium
  HOMO_06 (界面) → low
  ─────────────────
  HOMO_01 汇总 → low（取最低）
```

---

## 6. 错误处理

### 6.1 常见错误

| 错误类型 | 示例 | 处理方式 |
|----------|------|----------|
| 无效 task_type | `task_type: "predict_product"` | 返回错误，提示有效选项 |
| SMILES 解析失败 | `smiles: "invalid"` | 返回错误，要求重新输入 |
| 缺少必填字段 | 无 `molecule` | 返回错误，指出缺失字段 |

### 6.2 降级处理

当某个子模块执行失败时：
1. 返回已完成模块的结果
2. 在 `notes` 中标注失败的模块
3. 将 `overall_confidence` 设为 `low`

---

## 7. 常见问题 FAQ

### Q1: 什么时候用 full_assessment vs interface_ranking？

- **interface_ranking**：只需要位点排序，不需要反例校验
- **full_assessment**：需要完整报告，包含 TRADE 模块的误判警示

### Q2: 可以只分析某个特定位点吗？

可以。使用 `options.target_sites`：
```yaml
options:
  target_sites: ["carbonyl", "C-F"]
```

### Q3: 如何解读 tradeoff_warnings？

`tradeoff_warnings` 不是说结论错误，而是**提醒可能存在的反例或边界情况**。例如：
- `TRADE_04` 触发：说明分子可能是"牺牲型添加剂"，不稳定反而是功能
- `TRADE_01` 触发：说明"吸电子=稳定"的推断可能不适用

### Q4: 输出可以用 JSON 格式吗？

可以。设置 `options.output_format: "json"` 即可。

### Q5: 如何直接调用单个 skill 卡片？

绕过 Router，直接指定卡片 ID：
```yaml
call:
  target: ELEC_02_I_sigma_v1  # 直接调用
  input:
    substituent: "CF3"
    target_site: "adjacent_carbon"
```

**注意**：直连调用不经过 TRADE 校验。

---

## 8. 模块能力速查

| 想知道... | 使用模块 | 输出字段 |
|-----------|----------|----------|
| 取代基是推还是拉 | ELEC_01 | `effect_summary`, `dominant_channel` |
| 哪里最容易被氧化 | HOMO_01 | `ox_sites_ranked` |
| 哪里最容易被还原 | LUMO_01 | `red_sites_ranked` |
| 正极界面优先位点 | INTF_02 | `cathode` 排序 |
| 负极界面优先位点 | INTF_03 | `anode` 排序 |
| 是否会形成 SEI/CEI | INTF_05 | `film_hint` |
| 结论是否有反例风险 | TRADE_* | `triggered_pitfalls` |

---

## 9. 版本兼容性

| Guide 版本 | Router 版本 | Schema 版本 |
|------------|-------------|-------------|
| 1.0 | 1.0 | 1.0 |

---

## 10. Changelog

- 2025-12-24: 初始版本


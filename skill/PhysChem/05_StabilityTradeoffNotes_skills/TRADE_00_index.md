# TRADE_00_index — 稳定性权衡与反例框架 Skill 注册表

| Field | Value |
|---|---|
| Registry | Stability Tradeoff Notes Prompt Skills |
| Schema | `TRADE_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Count | 5 |

本注册表用于索引"稳定性权衡提示与反例框架"相关的 Prompt Skills。  
每张卡片提供**常见误判警示**和**反例案例**，防止过度简化的结构-稳定性推断。

**核心目标**：提醒"X ≠ 万能"，避免错误的泛化推断

---

## 1. 全量清单（按 Skill ID）

| Skill ID | 中文名 | 功能简述 | 关键词 | File |
|---|---|---|---|---|
| `TRADE_01_ewg_not_always_v1` | 吸电子≠万能稳定 | 吸电子基并非总是提高稳定性的反例 | `EWG, counterexample, exception` | [TRADE_01_ewg_not_always_v1.md](TRADE_01_ewg_not_always_v1.md) |
| `TRADE_02_steric_vs_electronic_v1` | 位阻 vs 电子效应 | 空间效应与电子效应的权衡 | `steric, electronic, tradeoff` | [TRADE_02_steric_vs_electronic_v1.md](TRADE_02_steric_vs_electronic_v1.md) |
| `TRADE_03_kinetic_vs_thermo_v1` | 动力学 vs 热力学 | 稳定≠不反应的辨析 | `kinetic, thermodynamic, barrier` | [TRADE_03_kinetic_vs_thermo_v1.md](TRADE_03_kinetic_vs_thermo_v1.md) |
| `TRADE_04_interface_paradox_v1` | 界面悖论 | "牺牲自己保护他人"的添加剂逻辑 | `sacrificial, additive, paradox` | [TRADE_04_interface_paradox_v1.md](TRADE_04_interface_paradox_v1.md) |
| `TRADE_05_common_pitfalls_v1` | 常见误判清单 | 高频错误推断与纠正汇总 | `pitfalls, mistakes, correction` | [TRADE_05_common_pitfalls_v1.md](TRADE_05_common_pitfalls_v1.md) |

---

## 2. 使用场景

本模块不像其他模块有"Pipeline"，而是作为**校验与警示层**：

```
其他模块评估结果
       │
       ▼
┌─────────────────────────┐
│ TRADE 模块（校验层）     │
│                         │
│ "这个结论是否触犯了     │
│  已知的反例/误判陷阱？" │
└─────────────────────────┘
       │
       ▼
校验后的结论 + 警示标注
```

---

## 3. 反例框架结构

每个反例卡片遵循统一结构：

```yaml
pitfall: "常见的错误推断"
counterexample: "具体反例"
mechanism: "反例成立的机理"
correction: "正确的推断方式"
when_pitfall_valid: "什么情况下原推断仍有效"
```

---

## 4. 检索标签（Tag → Skill）

| 标签 | Skill ID |
|---|---|
| `吸电子` / `EWG` / `HOMO降低` / `氧化稳定` | TRADE_01_ewg_not_always_v1 |
| `位阻` / `空间效应` / `体积` / `接触` | TRADE_02_steric_vs_electronic_v1 |
| `动力学` / `热力学` / `能垒` / `稳定≠不反应` | TRADE_03_kinetic_vs_thermo_v1 |
| `添加剂` / `牺牲` / `SEI` / `悖论` | TRADE_04_interface_paradox_v1 |
| `误判` / `错误` / `陷阱` / `纠正` | TRADE_05_common_pitfalls_v1 |

---

## 5. 与其他模块的联动

| 调用方向 | 联动模块 | 说明 |
|----------|----------|------|
| HOMO/LUMO → TRADE | 评估结论后调用 TRADE 校验 |
| INTF → TRADE | 界面排序后调用 TRADE 检查悖论 |
| ELEC → TRADE | 电子效应结论后调用 TRADE 校验 |

---

## 6. 使用建议

1. **作为最后校验层**：在其他模块给出结论后，调用 TRADE 检查是否触犯已知反例。
2. **主动警示**：当评估结果涉及"吸电子→稳定"等常见简化时，主动附加警示。
3. **降置信度**：若结论可能触犯反例，降低置信度并标注。
4. **教育用途**：帮助用户理解为什么某些"直觉"可能是错的。

---

## 7. 核心原则

- **没有万能规则**：任何结构-性质规则都有适用边界
- **反例必须具体**：给出实际化合物或机理，不空谈
- **说明机理**：解释为什么反例成立
- **给出边界**：说明原规则什么时候仍然有效

---

## 8. Changelog

- 2025-12-24: 初始版本，包含 5 个 skill 卡片


# INTF_00_index — 界面优先反应位点 Skill 注册表

| Field | Value |
|---|---|
| Registry | Interface FirstStrike Sites Prompt Skills |
| Schema | `INTF_CARD_SCHEMA_v1` |
| Created | 2025-12-24 |
| Count | 5 |

本注册表用于索引"界面优先反应位点排序"相关的 Prompt Skills。  
每张卡片整合 HOMO/LUMO 评估结果，结合界面特性，给出"在电极界面，哪些位点会优先反应"的排序与理由。

**核心目标**：只给优先级与理由，不预测具体产物

---

## 1. 全量清单（按 Skill ID）

| Skill ID | 中文名 | 功能简述 | 关键词 | File |
|---|---|---|---|---|
| `INTF_01_firststrike_flowmap_v1` | 界面优先位点总路由 | 汇总正负极评估，输出综合排序 | `routing, ranking, interface` | [INTF_01_firststrike_flowmap_v1.md](INTF_01_firststrike_flowmap_v1.md) |
| `INTF_02_cathode_ranking_v1` | 正极界面排序 | 氧化优先位点（调用 HOMO 模块） | `cathode, oxidation, HOMO` | [INTF_02_cathode_ranking_v1.md](INTF_02_cathode_ranking_v1.md) |
| `INTF_03_anode_ranking_v1` | 负极界面排序 | 还原优先位点（调用 LUMO 模块） | `anode, reduction, LUMO` | [INTF_03_anode_ranking_v1.md](INTF_03_anode_ranking_v1.md) |
| `INTF_04_competition_resolve_v1` | 竞争位点判定 | 多位点竞争时的优先级决策 | `competition, selectivity, decision` | [INTF_04_competition_resolve_v1.md](INTF_04_competition_resolve_v1.md) |
| `INTF_05_film_formation_hint_v1` | 成膜倾向提示 | SEI/CEI 形成的位点与路径提示 | `SEI, CEI, film, passivation` | [INTF_05_film_formation_hint_v1.md](INTF_05_film_formation_hint_v1.md) |

---

## 2. 建议调用顺序（Pipeline）

```
1. INTF_01_firststrike_flowmap_v1（总路由）
   │
   ├─► 2. INTF_02_cathode_ranking_v1（正极界面）
   │       └─► [HOMO_01_ox_flowmap_v1]
   │
   ├─► 3. INTF_03_anode_ranking_v1（负极界面）
   │       └─► [LUMO_01_red_flowmap_v1]
   │
   ├─► 4. INTF_04_competition_resolve_v1（竞争判定）
   │
   ├─► 5. INTF_05_film_formation_hint_v1（成膜提示）
   │
   └─► 6. 返回 INTF_01 输出最终排序
```

---

## 3. 按界面类型索引

### 正极界面（氧化）
- `INTF_02_cathode_ranking_v1` — [正极界面排序](INTF_02_cathode_ranking_v1.md)

### 负极界面（还原）
- `INTF_03_anode_ranking_v1` — [负极界面排序](INTF_03_anode_ranking_v1.md)

### 判定与提示
- `INTF_04_competition_resolve_v1` — [竞争位点判定](INTF_04_competition_resolve_v1.md)
- `INTF_05_film_formation_hint_v1` — [成膜倾向提示](INTF_05_film_formation_hint_v1.md)

### 总路由
- `INTF_01_firststrike_flowmap_v1` — [界面优先位点总路由](INTF_01_firststrike_flowmap_v1.md)

---

## 4. 检索标签（Tag → Skill）

| 标签 | Skill ID |
|---|---|
| `正极` / `氧化` / `CEI` / `高电位` | INTF_02_cathode_ranking_v1 |
| `负极` / `还原` / `SEI` / `低电位` | INTF_03_anode_ranking_v1 |
| `竞争` / `选择性` / `多位点` | INTF_04_competition_resolve_v1 |
| `成膜` / `钝化` / `界面层` | INTF_05_film_formation_hint_v1 |
| `综合排序` / `优先级` | INTF_01_firststrike_flowmap_v1 |

---

## 5. 输出格式规范

### 标准输出结构
```yaml
first_strike_sites:
  cathode:  # 正极界面
    rank_1:
      site: "位点描述"
      reason: "优先的理由"
      confidence: high/medium/low
    rank_2:
      site: "..."
      reason: "..."
    # ...
  anode:    # 负极界面
    rank_1:
      site: "位点描述"
      reason: "优先的理由"
    rank_2:
      site: "..."
      reason: "..."
  competition_notes: "多位点竞争时的判定说明"
  film_hint: "成膜倾向提示"
```

---

## 6. 与其他 Skill 模块的联动

| 调用方向 | 联动模块 | 说明 |
|----------|----------|------|
| INTF → HOMO | `02_HOMO_OxTendency_Qual_skills/` | 正极排序调用 HOMO 模块 |
| INTF → LUMO | `03_LUMO_RedTendency_Qual_skills/` | 负极排序调用 LUMO 模块 |
| INTF → TRADE | `05_StabilityTradeoffNotes_skills/` | 可调用权衡模块避免误判 |
| 上游 → INTF | 电化学专家 Agent | 调用 INTF 获取界面反应预判 |

---

## 7. 使用建议（编排）

1. **只关心负极**：直接调用 `INTF_03_anode_ranking_v1`。
2. **只关心正极**：直接调用 `INTF_02_cathode_ranking_v1`。
3. **完整评估**：从 `INTF_01_firststrike_flowmap_v1` 开始，获取双极排序。
4. **多位点竞争**：调用 `INTF_04_competition_resolve_v1` 获取判定。
5. **关心成膜**：调用 `INTF_05_film_formation_hint_v1` 获取 SEI/CEI 提示。

---

## 8. 核心原则

- **只排序，不预测产物**：本模块回答"哪里先反应"，不回答"生成什么"
- **理由必须明确**：每个排序必须附带理由
- **置信度标注**：不确定时降低置信度
- **与上游模块一致**：排序结论必须与 HOMO/LUMO 模块一致

---

## 9. Changelog

- 2025-12-24: 初始版本，包含 5 个 skill 卡片


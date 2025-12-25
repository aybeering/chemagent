# ROLE_00_index — 角色假设 Skill 注册表

| Field | Value |
|---|---|
| Registry | ROLE Prompt Skills |
| Schema | `ROLE_CARD_SCHEMA_v1` |
| Created | 2025-12-25 |
| Count | 5 |

本注册表用于索引"角色假设"相关的 Prompt Skills。  
每张卡片是一个 **ROLE prompt skill**，用于判断分子在电解液体系中的可能角色。

---

## 1. 全量清单（按 Skill ID）

| Skill ID | 中文名 | 功能简述 | 关键词 | File |
|---|---|---|---|---|
| `ROLE_01_role_flowmap_v1` | 角色假设总路由 | 总装配：根据结构特征分发到各角色假设卡 | `routing, role-assignment` | [ROLE_01_role_flowmap_v1.md](ROLE_01_role_flowmap_v1.md) |
| `ROLE_02_solvent_hypothesis_v1` | 溶剂假设 | 判断是否适合作为主溶剂 | `solvent, dielectric, viscosity` | [ROLE_02_solvent_hypothesis_v1.md](ROLE_02_solvent_hypothesis_v1.md) |
| `ROLE_03_film_additive_v1` | 成膜添加剂假设 | 判断是否适合作为 SEI/CEI 成膜添加剂 | `additive, SEI, CEI, film-forming` | [ROLE_03_film_additive_v1.md](ROLE_03_film_additive_v1.md) |
| `ROLE_04_diluent_hypothesis_v1` | 稀释剂假设 | 判断是否适合作为 LHCE 稀释剂 | `diluent, LHCE, inert, low-coordination` | [ROLE_04_diluent_hypothesis_v1.md](ROLE_04_diluent_hypothesis_v1.md) |
| `ROLE_05_unsuitable_flag_v1` | 不适合标记 | 识别结构警示，标记不适合的情况 | `unsuitable, warning, safety` | [ROLE_05_unsuitable_flag_v1.md](ROLE_05_unsuitable_flag_v1.md) |

---

## 2. 建议调用顺序（Pipeline）

```
1. ROLE_01_role_flowmap_v1（总路由与角色分发）
   │
   ├─► 2. ROLE_02_solvent_hypothesis_v1（溶剂假设）
   │
   ├─► 3. ROLE_03_film_additive_v1（成膜添加剂假设）
   │
   ├─► 4. ROLE_04_diluent_hypothesis_v1（稀释剂假设）
   │
   ├─► 5. ROLE_05_unsuitable_flag_v1（不适合标记）
   │
   └─► 6. 返回 ROLE_01 做最终角色判定与置信度评估
```

---

## 3. 按角色类型索引

### 主溶剂候选
- `ROLE_02_solvent_hypothesis_v1` — [溶剂假设](ROLE_02_solvent_hypothesis_v1.md)

### 功能性添加剂候选
- `ROLE_03_film_additive_v1` — [成膜添加剂假设](ROLE_03_film_additive_v1.md)

### 稀释剂候选
- `ROLE_04_diluent_hypothesis_v1` — [稀释剂假设](ROLE_04_diluent_hypothesis_v1.md)

### 风险标记
- `ROLE_05_unsuitable_flag_v1` — [不适合标记](ROLE_05_unsuitable_flag_v1.md)

### 总路由
- `ROLE_01_role_flowmap_v1` — [角色假设总路由](ROLE_01_role_flowmap_v1.md)

---

## 4. 检索标签（Tag → Skill）

| 标签 | Skill ID |
|---|---|
| `溶剂` / `介电常数` / `粘度` / `溶解锂盐` | ROLE_02_solvent_hypothesis_v1 |
| `添加剂` / `成膜` / `SEI` / `CEI` / `优先还原` | ROLE_03_film_additive_v1 |
| `稀释剂` / `LHCE` / `低配位` / `惰性` / `氟化` | ROLE_04_diluent_hypothesis_v1 |
| `不适合` / `警示` / `安全` / `禁忌` | ROLE_05_unsuitable_flag_v1 |
| `角色判定` / `综合评估` | ROLE_01_role_flowmap_v1 |

---

## 5. 易混淆索引（用于路由与消歧）

| Skill | 易混淆 Skill | 消歧说明 |
|---|---|---|
| `ROLE_02_solvent_hypothesis_v1` | `ROLE_04_diluent_hypothesis_v1` | 溶剂需高介电常数溶解锂盐；稀释剂需低配位惰性 |
| `ROLE_03_film_additive_v1` | `ROLE_02_solvent_hypothesis_v1` | 添加剂小用量成膜；溶剂大用量做基体 |
| `ROLE_03_film_additive_v1` | `ROLE_05_unsuitable_flag_v1` | 添加剂的"牺牲"是设计特性，不同于结构缺陷 |

---

## 6. 依赖关系

```
ROLE_01_role_flowmap_v1
    ├── depends_on: [ROLE_02, ROLE_03, ROLE_04, ROLE_05]
    └── 作为总路由调用所有子技能卡

ROLE_02/03/04/05
    └── 依赖上游 OrganicChem 和 PhysChem 输出
```

---

## 7. 使用建议（编排）

1. **单一问题**（如"这个分子能做溶剂吗？"）：可直接调用 `ROLE_02_solvent_hypothesis_v1`。
2. **完整角色评估**：走完整 Pipeline，从 `ROLE_01_role_flowmap_v1` 开始。
3. **LHCE 体系评估**：重点调用 `ROLE_04_diluent_hypothesis_v1`。
4. **安全性初筛**：优先调用 `ROLE_05_unsuitable_flag_v1` 排除不适合的候选。

---

## 8. 与其他 Skill 模块的联动

| 场景 | 联动模块 |
|---|---|
| 判断成膜添加剂后分析 SEI 路径 | → `02_SEIPathway_skills/SEI_*` |
| 判断溶剂后评估高压稳定性 | → `03_CEIRisk_skills/CEI_*` |
| 识别不适合后进一步分析风险 | → `04_GassingPolymerRisk_skills/GAS_*` |
| 需要结构解析 | → `OrganicChem/` |
| 需要 HOMO/LUMO 分析 | → `PhysChem/` |


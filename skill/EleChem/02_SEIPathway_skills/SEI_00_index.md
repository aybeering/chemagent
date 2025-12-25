# SEI_00_index — SEI 路径 Skill 注册表

| Field | Value |
|---|---|
| Registry | SEI Prompt Skills |
| Schema | `SEI_CARD_SCHEMA_v1` |
| Created | 2025-12-25 |
| Count | 4 |

本注册表用于索引"SEI 路径分析"相关的 Prompt Skills。  
每张卡片是一个 **SEI prompt skill**，用于分析分子在负极界面的 SEI 成膜路径和产物趋势。

---

## 1. 全量清单（按 Skill ID）

| Skill ID | 中文名 | 功能简述 | 关键词 | File |
|---|---|---|---|---|
| `SEI_01_pathway_flowmap_v1` | SEI 路径总路由 | 总装配：整合各成膜路径，给出综合 SEI 组成趋势 | `routing, pathway-fusion` | [SEI_01_pathway_flowmap_v1.md](SEI_01_pathway_flowmap_v1.md) |
| `SEI_02_polymer_film_v1` | 聚合膜路径 | 分析开环/自由基聚合形成有机膜的倾向 | `polymer, ring-opening, radical` | [SEI_02_polymer_film_v1.md](SEI_02_polymer_film_v1.md) |
| `SEI_03_inorganic_salt_v1` | 无机盐膜路径 | 分析 Li₂CO₃、Li₂O 等无机盐形成倾向 | `inorganic, Li2CO3, Li2O` | [SEI_03_inorganic_salt_v1.md](SEI_03_inorganic_salt_v1.md) |
| `SEI_04_lif_tendency_v1` | LiF 倾向 | 分析 C-F 键断裂释放 F⁻ 形成 LiF 的倾向 | `LiF, C-F, fluoride` | [SEI_04_lif_tendency_v1.md](SEI_04_lif_tendency_v1.md) |

---

## 2. 建议调用顺序（Pipeline）

```
1. SEI_01_pathway_flowmap_v1（总路由与路径整合）
   │
   ├─► 2. SEI_02_polymer_film_v1（聚合膜路径分析）
   │
   ├─► 3. SEI_03_inorganic_salt_v1（无机盐膜路径分析）
   │
   ├─► 4. SEI_04_lif_tendency_v1（LiF 形成倾向分析）
   │
   └─► 5. 返回 SEI_01 做最终 SEI 组成趋势综合
```

---

## 3. 按 SEI 组分类型索引

### 有机组分
- `SEI_02_polymer_film_v1` — [聚合膜路径](SEI_02_polymer_film_v1.md)

### 无机组分
- `SEI_03_inorganic_salt_v1` — [无机盐膜路径](SEI_03_inorganic_salt_v1.md)
- `SEI_04_lif_tendency_v1` — [LiF 倾向](SEI_04_lif_tendency_v1.md)

### 总路由
- `SEI_01_pathway_flowmap_v1` — [SEI 路径总路由](SEI_01_pathway_flowmap_v1.md)

---

## 4. 检索标签（Tag → Skill）

| 标签 | Skill ID |
|---|---|
| `聚合` / `开环` / `自由基` / `有机膜` / `柔性膜` | SEI_02_polymer_film_v1 |
| `无机盐` / `Li₂CO₃` / `Li₂O` / `碳酸锂` | SEI_03_inorganic_salt_v1 |
| `LiF` / `C-F断裂` / `氟化物` / `F⁻释放` | SEI_04_lif_tendency_v1 |
| `SEI组成` / `成膜路径` / `综合评估` | SEI_01_pathway_flowmap_v1 |

---

## 5. 易混淆索引（用于路由与消歧）

| Skill | 易混淆 Skill | 消歧说明 |
|---|---|---|
| `SEI_02_polymer_film_v1` | `SEI_03_inorganic_salt_v1` | 聚合膜来自有机分子聚合；无机盐来自小分子分解 |
| `SEI_03_inorganic_salt_v1` | `SEI_04_lif_tendency_v1` | Li₂CO₃/Li₂O 来自碳酸酯分解；LiF 来自 C-F 断裂 |
| `SEI_02_polymer_film_v1` | `GAS_03_polymer_risk_v1` | SEI 聚合是受控成膜；GAS 聚合是失控风险 |

---

## 6. 依赖关系

```
SEI_01_pathway_flowmap_v1
    ├── depends_on: [SEI_02, SEI_03, SEI_04]
    └── 作为总路由调用所有子技能卡

SEI_02/03/04
    └── 依赖上游 OrganicChem 和 PhysChem 输出
```

---

## 7. 使用建议（编排）

1. **单一问题**（如"会形成聚合物膜吗？"）：可直接调用 `SEI_02_polymer_film_v1`。
2. **完整 SEI 评估**：走完整 Pipeline，从 `SEI_01_pathway_flowmap_v1` 开始。
3. **含氟化合物**：重点调用 `SEI_04_lif_tendency_v1`。
4. **碳酸酯类溶剂**：并行调用 `SEI_02` 和 `SEI_03`。

---

## 8. 与其他 Skill 模块的联动

| 场景 | 联动模块 |
|---|---|
| 需要判断分子角色 | → `01_RoleHypothesis_skills/ROLE_*` |
| 评估 SEI 形成的产气 | → `04_GassingPolymerRisk_skills/GAS_02` |
| 需要 LUMO 分析支持 | → `PhysChem/LUMO_*` |
| 需要开环位点识别 | → `OrganicChem/RH_05_ring_opening_site_v1` |

---

## 9. SEI 组成背景知识

### 典型 SEI 组分
| 组分类型 | 典型物质 | 来源 |
|---------|---------|------|
| 无机盐 | Li₂CO₃, Li₂O, LiOH | 碳酸酯分解 |
| 氟化物 | LiF | C-F 键断裂或盐分解（LiPF₆） |
| 有机物 | ROCO₂Li, (RO)₂CO | 不完全分解 |
| 聚合物 | 聚碳酸酯, 聚醚 | 开环聚合 |

### 理想 SEI 特征
- LiF 富集：高离子电导率、机械强度
- 有机/无机复合：兼顾柔性和稳定性
- 薄且致密：低阻抗、阻止溶剂渗透


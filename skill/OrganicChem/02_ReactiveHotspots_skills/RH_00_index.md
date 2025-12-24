# RH_00_index — 反应敏感位点模块索引

| Field | Value |
|---|---|
| Module | 02_ReactiveHotspots |
| Registry | RH Prompt Skills |
| Created | 2025-12-24 |
| Skill Count | 6 |
| Entry Point | RH_01_hotspot_flowmap_v1 |
| Depends On | 01_StructureDigest |

本模块负责识别分子中的反应敏感位点，包括亲核、亲电、消除、开环和重排倾向位点，为 PhysChem 的 HOMO/LUMO 分析提供目标位点。

---

## Skill 清单

| Skill ID | 功能 | 识别的位点类型 |
|----------|------|---------------|
| `RH_01_hotspot_flowmap_v1` | 敏感位点总路由 | 调度所有 RH 子卡 |
| `RH_02_nucleophilic_site_v1` | 亲核位点识别 | n 孤对、π 系统、负离子、烯醇 |
| `RH_03_electrophilic_site_v1` | 亲电位点识别 | 羰基 C、sp3-LG、缺电子芳环 |
| `RH_04_elimination_site_v1` | 消除位点识别 | β-H + LG 组合、E2/E1cb 倾向 |
| `RH_05_ring_opening_site_v1` | 开环位点识别 | 环氧、内酯、环状碳酸酯、小环 |
| `RH_06_rearrangement_site_v1` | 重排倾向位点识别 | 1,2-迁移、Wagner-Meerwein、pinacol |

---

## 调用关系

```
RH_01_hotspot_flowmap_v1（总路由）
    │
    ├──► RH_02_nucleophilic_site_v1（亲核位点）
    │
    ├──► RH_03_electrophilic_site_v1（亲电位点）
    │
    ├──► RH_04_elimination_site_v1（消除位点）
    │
    ├──► RH_05_ring_opening_site_v1（开环位点）
    │
    └──► RH_06_rearrangement_site_v1（重排位点）
```

---

## 依赖关系

RH 模块依赖 SD 模块的输出：

| SD 输出 | RH 使用 |
|---------|---------|
| functional_groups | 识别官能团相关的反应位点 |
| heteroatom_labels | 确定杂原子的亲核/亲电性 |
| ring_info | 识别开环位点 |
| conjugation_map | 判断 π 系统亲核性 |

---

## 输入要求

- **必需**：SMILES 字符串或结构描述
- **推荐**：SD 模块的输出（structure_digest）

---

## 输出格式

参考 [OrganicChem_Schema.md](../OrganicChem_Schema.md) 中的 `ReactiveHotspotsOutput` 定义。

---

## 与 PhysChem 的联动

| RH 输出 | 推荐的 PhysChem 模块 |
|---------|---------------------|
| nucleophilic_sites | HOMO_02, HOMO_03 |
| electrophilic_sites | LUMO_02, LUMO_03 |
| ring_opening_sites | LUMO_04 |

---

## 使用示例

```yaml
call:
  target: RH_01_hotspot_flowmap_v1
  input:
    molecule:
      smiles: "CC(=O)Cl"
      name: "Acetyl Chloride"
    structure_digest: <SD 模块输出>
```

---

## Changelog

- 2025-12-24: 初始版本


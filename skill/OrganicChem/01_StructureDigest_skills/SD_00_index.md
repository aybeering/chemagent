# SD_00_index — 结构解剖与标签化模块索引

| Field | Value |
|---|---|
| Module | 01_StructureDigest |
| Registry | SD Prompt Skills |
| Created | 2025-12-24 |
| Skill Count | 6 |
| Entry Point | SD_01_digest_flowmap_v1 |

本模块负责解析分子结构，识别骨架、官能团、杂原子特征、环系和共轭网络，为下游分析提供结构化的分子描述。

---

## Skill 清单

| Skill ID | 功能 | 主要输出 |
|----------|------|----------|
| `SD_01_digest_flowmap_v1` | 结构解剖总路由 | 调度所有 SD 子卡 |
| `SD_02_skeleton_parse_v1` | 骨架识别 | skeleton_type, chain_length, ring_ids |
| `SD_03_functional_group_v1` | 官能团识别与分类 | functional_groups[] |
| `SD_04_heteroatom_label_v1` | 杂原子标签 | heteroatom_labels[] |
| `SD_05_ring_system_v1` | 环系分析 | ring_info[], aromaticity, strain_level |
| `SD_06_conjugation_map_v1` | 共轭网络映射 | pi_systems[], conjugation_paths |

---

## 调用关系

```
SD_01_digest_flowmap_v1（总路由）
    │
    ├──► SD_02_skeleton_parse_v1（骨架识别）
    │
    ├──► SD_03_functional_group_v1（官能团识别）
    │
    ├──► SD_04_heteroatom_label_v1（杂原子标签）
    │
    ├──► SD_05_ring_system_v1（环系分析）
    │
    └──► SD_06_conjugation_map_v1（共轭网络映射）
```

---

## 输入要求

- **必需**：SMILES 字符串或结构描述
- **可选**：分子名称、InChI

---

## 输出格式

参考 [OrganicChem_Schema.md](../OrganicChem_Schema.md) 中的 `StructureDigestOutput` 定义。

---

## 使用示例

```yaml
call:
  target: SD_01_digest_flowmap_v1
  input:
    molecule:
      smiles: "C1COC(=O)O1"
      name: "Ethylene Carbonate"
```

---

## Changelog

- 2025-12-24: 初始版本


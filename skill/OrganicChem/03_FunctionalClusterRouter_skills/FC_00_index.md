# FC_00_index — 官能团簇路由模块索引

| Field | Value |
|---|---|
| Module | 03_FunctionalClusterRouter |
| Registry | FC Prompt Skills |
| Created | 2025-12-24 |
| Skill Count | 7 |
| Entry Point | FC_01_cluster_router_v1 |
| Depends On | 01_StructureDigest |
| Downstream | PhysChem |

本模块负责将识别出的官能团归类为"簇"，并推荐适合的 PhysChem 分析模块，实现 OrganicChem 到 PhysChem 的智能路由。

---

## Skill 清单

| Skill ID | 官能团簇 | 包含的官能团 | 推荐的 PhysChem 模块 |
|----------|---------|-------------|---------------------|
| `FC_01_cluster_router_v1` | 总路由 | - | 分发到各 FC 子卡 |
| `FC_02_carbonyl_cluster_v1` | 羰基簇 | 醛/酮/羧酸/酯/酰胺/酸酐/碳酸酯 | LUMO_02 |
| `FC_03_nitrogen_cluster_v1` | 氮簇 | 胺/酰胺/腈/硝基/偶氮/杂环 N | HOMO_02, LUMO |
| `FC_04_oxygen_cluster_v1` | 氧簇 | 醇/醚/环氧/过氧化物 | HOMO_02 |
| `FC_05_halogen_cluster_v1` | 卤素簇 | C-F/C-Cl/C-Br/C-I | LUMO_03, ELEC_02 |
| `FC_06_sulfur_phosphorus_v1` | 硫/磷簇 | 硫醚/磺酰/磷酸酯 | HOMO_02 |
| `FC_07_unsaturated_cluster_v1` | 不饱和簇 | 烯烃/炔烃/芳环/共轭体系 | HOMO_03, LUMO_02 |

---

## 调用关系

```
FC_01_cluster_router_v1（总路由）
    │
    ├──► FC_02_carbonyl_cluster_v1（羰基簇）
    │
    ├──► FC_03_nitrogen_cluster_v1（氮簇）
    │
    ├──► FC_04_oxygen_cluster_v1（氧簇）
    │
    ├──► FC_05_halogen_cluster_v1（卤素簇）
    │
    ├──► FC_06_sulfur_phosphorus_v1（硫/磷簇）
    │
    └──► FC_07_unsaturated_cluster_v1（不饱和簇）
```

---

## 簇类型与 PhysChem 模块对应

```
┌──────────────────┐     ┌──────────────────────┐
│   Carbonyl 簇    │────►│ LUMO_02_pi_antibond  │
│ 羰基(π* C=O)     │     │ 还原倾向：π*反键     │
└──────────────────┘     └──────────────────────┘

┌──────────────────┐     ┌──────────────────────┐
│   Nitrogen 簇    │────►│ HOMO_02_lonepair_n   │
│ 胺类(n孤对)      │     │ 氧化倾向：n轨道孤对  │
└──────────────────┘     └──────────────────────┘

┌──────────────────┐     ┌──────────────────────┐
│   Oxygen 簇      │────►│ HOMO_02_lonepair_n   │
│ 醇/醚(n孤对)     │     │ 氧化倾向：n轨道孤对  │
└──────────────────┘     └──────────────────────┘

┌──────────────────┐     ┌──────────────────────┐
│   Halogen 簇     │────►│ LUMO_03_sigma_antibond│
│ C-X(σ* C-X)      │     │ 还原倾向：σ*反键     │
└──────────────────┘     └──────────────────────┘

┌──────────────────┐     ┌──────────────────────┐
│  Unsaturated 簇  │────►│ HOMO_03 + LUMO_02    │
│ 烯烃/芳环(π)     │     │ 氧化/还原：π系统     │
└──────────────────┘     └──────────────────────┘
```

---

## 输入要求

- **必需**：SMILES 字符串或结构描述
- **推荐**：SD 模块的输出（functional_groups）

---

## 输出格式

参考 [OrganicChem_Schema.md](../OrganicChem_Schema.md) 中的 `ClusterRoutingOutput` 定义。

---

## 使用示例

```yaml
call:
  target: FC_01_cluster_router_v1
  input:
    molecule:
      smiles: "FC(F)(F)C(=O)OCC"
      name: "Ethyl Trifluoroacetate"
    functional_groups: <SD_03 输出>
```

**输出**：
```yaml
cluster_routing:
  clusters:
    - cluster_type: "carbonyl"
      priority: 1
      physchem_modules: ["LUMO_02_pi_antibond_v1"]
    - cluster_type: "halogen"
      priority: 2
      physchem_modules: ["LUMO_03_sigma_antibond_v1", "ELEC_02_I_sigma_v1"]
  
  primary_cluster: "carbonyl"
  suggested_physchem_modules:
    - module_id: "LUMO_02_pi_antibond_v1"
      reason: "羰基 π* 是主要还原位点"
      priority: 1
    - module_id: "ELEC_02_I_sigma_v1"
      reason: "CF₃ 强 -I 效应影响羰基活性"
      priority: 2
```

---

## Changelog

- 2025-12-24: 初始版本


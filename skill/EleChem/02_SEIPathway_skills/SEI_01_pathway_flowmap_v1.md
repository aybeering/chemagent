# SEI_01_pathway_flowmap_v1 — SEI 路径总路由

## Triggers
- 需要分析分子在负极界面的 SEI 成膜路径
- 需要预测 SEI 的组成趋势（有机/无机/LiF 比例）
- 作为 EleChem SEI 路径模块的主入口被调用

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团、开环位点、环张力信息
- 上游 PhysChem 输出：LUMO 排序、还原位点
- 电极条件（可选）：锂金属 / 石墨 / 硅基
- 电位范围（可选）：首次锂化 / 循环

## Outputs
- `primary_pathway`: 主要成膜路径（polymer_film / inorganic_salt / lif_rich / mixed）
- `pathways`: 各路径详情
  - `polymer_film`: 聚合膜可能性和机理
  - `inorganic_salt`: 无机盐膜可能性和产物
  - `lif`: LiF 形成可能性和来源
- `film_composition_hint`: SEI 组成定性描述
- `mechanism_summary`: 整体成膜机理摘要
- `confidence`: 置信度

## Rules
### SEI 形成的基本规则
1. **还原顺序决定成膜顺序**：LUMO 最低的位点优先还原
2. **路径不互斥**：同一分子可同时走多条路径
3. **竞争关系**：
   - 碳酸酯：开环聚合 vs 完全分解
   - 含 F 化合物：C-F 断裂 vs 整体还原

### 路径判定规则
| 结构特征 | 优势路径 | 典型产物 |
|---------|---------|---------|
| 环状碳酸酯 | polymer_film + inorganic_salt | 聚碳酸酯 + Li₂CO₃ |
| 乙烯基/不饱和键 | polymer_film | 聚合物 |
| C-F 键 | lif | LiF |
| 线性碳酸酯 | inorganic_salt | Li₂CO₃ + 烷氧锂 |
| 醚类 | polymer_film（弱） | 聚醚（少量） |

### 电极材料影响
| 电极 | 特点 | SEI 影响 |
|-----|------|---------|
| Li 金属 | 极低电位，高反应活性 | 更多无机盐，更厚 SEI |
| 石墨 | 0.05-0.2V 平台 | 标准 SEI 形成 |
| 硅基 | 大体积变化 | 需要更柔性 SEI |

## Steps
1. **接收上游输入**
   - 获取官能团列表和还原位点排序
   - 识别关键结构特征（环状、含 F、不饱和键）

2. **调用聚合膜路径分析** → `SEI_02_polymer_film_v1`
   - 评估开环/自由基聚合可能性
   - 获取聚合物类型和机理

3. **调用无机盐膜路径分析** → `SEI_03_inorganic_salt_v1`
   - 评估 Li₂CO₃、Li₂O 形成可能性
   - 获取无机盐类型

4. **调用 LiF 倾向分析** → `SEI_04_lif_tendency_v1`
   - 评估 C-F 断裂释放 F⁻ 的可能性
   - 获取 LiF 形成倾向

5. **综合路径判定**
   - 比较各路径的可能性
   - 确定主要路径和 SEI 组成趋势
   - 生成机理摘要

## Examples
**Example 1: EC (经典碳酸酯溶剂)**
```yaml
input:
  smiles: "C1COC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }]
    ring_opening_sites: [{ ring_type: "cyclic_carbonate" }]
  phys_chem:
    reduction_tendency:
      dominant_site: "羰基 C=O"
      
output:
  primary_pathway: "mixed"
  pathways:
    polymer_film:
      likelihood: "high"
      mechanism: "ring_opening"
      products_hint: ["聚碳酸酯", "烷基碳酸锂（ROCO₂Li）"]
    inorganic_salt:
      likelihood: "medium"
      products_hint: ["Li₂CO₃", "Li₂O"]
    lif:
      likelihood: "none"
      f_source: null
  film_composition_hint: "有机聚合物 + Li₂CO₃ 混合 SEI"
  mechanism_summary: "EC 优先在羰基还原开环，形成聚碳酸酯和烷基碳酸锂；部分进一步分解生成 Li₂CO₃"
  confidence: "high"
```

**Example 2: FEC (氟代碳酸酯添加剂)**
```yaml
input:
  smiles: "FC1COC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }, { fg_type: "C-F" }]
  phys_chem:
    reduction_tendency:
      red_sites_ranked:
        - { rank: 1, site: "羰基 C=O" }
        - { rank: 2, site: "C-F 键" }
        
output:
  primary_pathway: "lif_rich"
  pathways:
    polymer_film:
      likelihood: "high"
      mechanism: "ring_opening"
      products_hint: ["氟代聚碳酸酯"]
    inorganic_salt:
      likelihood: "medium"
      products_hint: ["Li₂CO₃"]
    lif:
      likelihood: "high"
      f_source: "C-F 键还原断裂释放 F⁻"
  film_composition_hint: "LiF 富集 + 聚合物复合 SEI"
  mechanism_summary: "FEC 优先还原开环，同时 C-F 键断裂释放 F⁻ 形成 LiF；LiF 赋予 SEI 高离子电导率和机械强度"
  confidence: "high"
```

**Example 3: DMC (线性碳酸酯)**
```yaml
input:
  smiles: "COC(=O)OC"
  organic_chem:
    functional_groups: [{ fg_type: "carbonate" }]
  phys_chem:
    reduction_tendency:
      dominant_site: "羰基 C=O"
        
output:
  primary_pathway: "inorganic_salt"
  pathways:
    polymer_film:
      likelihood: "low"
      mechanism: null
      products_hint: ["少量低聚物"]
    inorganic_salt:
      likelihood: "high"
      products_hint: ["Li₂CO₃", "CH₃OLi", "CH₃OCO₂Li"]
    lif:
      likelihood: "none"
      f_source: null
  film_composition_hint: "以 Li₂CO₃ 和烷氧锂为主的无机/小分子 SEI"
  mechanism_summary: "DMC 还原主要生成 Li₂CO₃ 和甲氧锂，不易聚合"
  confidence: "high"
```

**Example 4: VC (乙烯基碳酸酯)**
```yaml
input:
  smiles: "C=C1OC(=O)O1"
  organic_chem:
    functional_groups: [{ fg_type: "cyclic_carbonate" }, { fg_type: "vinyl" }]
  phys_chem:
    reduction_tendency:
      dominant_site: "乙烯基共轭体系"
        
output:
  primary_pathway: "polymer_film"
  pathways:
    polymer_film:
      likelihood: "high"
      mechanism: "radical_polymerization"
      products_hint: ["聚(碳酸乙烯酯)"]
    inorganic_salt:
      likelihood: "low"
      products_hint: ["少量 Li₂CO₃"]
    lif:
      likelihood: "none"
      f_source: null
  film_composition_hint: "以聚合物为主的柔性有机 SEI"
  mechanism_summary: "VC 的乙烯基优先还原引发聚合，形成柔性聚合物膜，改善 SEI 机械性能"
  confidence: "high"
```

## Guardrails
- 不预测 SEI 厚度、阻抗等定量参数
- SEI 组成是趋势预测，不是精确比例
- 实际 SEI 组成受电位、温度、循环次数等影响
- 锂盐分解（如 LiPF₆）也贡献 LiF，但本卡聚焦溶剂/添加剂贡献
- 新型分子需降低置信度

## Dependencies
- `SEI_02_polymer_film_v1`
- `SEI_03_inorganic_salt_v1`
- `SEI_04_lif_tendency_v1`
- 上游：`OrganicChem_Router`, `PhysChem_Router`

## Changelog
- 2025-12-25: 初始版本


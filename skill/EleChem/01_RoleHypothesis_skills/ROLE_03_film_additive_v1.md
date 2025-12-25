# ROLE_03_film_additive_v1 — 成膜添加剂假设

## Triggers
- 需要判断分子是否适合作为 SEI/CEI 成膜添加剂
- 需要评估分子的优先还原/氧化特性和成膜倾向

## Inputs
- 分子表示：SMILES / 官能团列表
- 上游 OrganicChem 输出：官能团、开环位点、敏感位点
- 上游 PhysChem 输出：LUMO 排序（还原）、HOMO 排序（氧化）、界面位点
- 关注电极（可选）：anode（SEI 添加剂）/ cathode（CEI 添加剂）/ both

## Outputs
- `suitability`: 适合度（high / medium / low / unsuitable）
- `additive_type`: 添加剂类型（SEI_former / CEI_former / dual / sacrificial）
- `evidence`: 支持/反对的结构证据
- `priority_reaction`: 优先反应类型（reduction / oxidation）
- `film_contribution`: 成膜贡献提示（organic / inorganic / LiF / mixed）
- `recommended_dosage`: 推荐用量范围提示（trace / low / moderate）

## Rules
### SEI 成膜添加剂（负极）正向指标
- **优先于主溶剂还原**：
  - LUMO 比 EC 更低（更容易接受电子）
  - 典型结构：FEC、VC、PS 等
  
- **成膜产物优质**：
  - 含 F → 释放 F⁻ 形成 LiF
  - 含不饱和键 → 开环聚合形成柔性膜
  - 含 S → 形成含 S 无机物

- **典型 SEI 添加剂结构**：
  | 添加剂 | 结构特征 | 成膜贡献 |
  |-------|---------|---------|
  | FEC | 氟代环状碳酸酯 | LiF + 聚合物 |
  | VC | 乙烯基碳酸酯 | 聚合物膜 |
  | PS | 1,3-丙烷磺内酯 | 含 S 无机物 |
  | ES | 硫酸乙烯酯 | 含 S 无机物 |
  | DTD | 二噻烷二氧化物 | 含 S 无机物 |

### CEI 成膜添加剂（正极）正向指标
- **优先于主溶剂氧化**：
  - HOMO 比主溶剂更高（更容易给出电子）
  - 但氧化产物稳定，形成保护膜
  
- **典型 CEI 添加剂结构**：
  | 添加剂 | 结构特征 | 作用 |
  |-------|---------|------|
  | LiBOB | 硼酸锂盐 | 形成含 B 保护膜 |
  | LiDFOB | 二氟草酸硼酸锂 | 形成含 B/F 膜 |

### 负向指标
- 还原/氧化后产物不稳定
- 产生大量气体
- 聚合失控
- 与电极材料不相容

## Steps
1. **评估还原优先性**（SEI）
   - 比较分子 LUMO 与主溶剂（EC）的相对位置
   - LUMO 更低 → 优先还原
   
2. **评估氧化优先性**（CEI）
   - 比较分子 HOMO 与主溶剂的相对位置
   - 在适当电位下氧化形成保护膜
   
3. **评估成膜产物**
   - 含 F → LiF 贡献
   - 含不饱和键 → 聚合物贡献
   - 含 S → 无机盐贡献
   
4. **评估副反应风险**
   - 产气倾向
   - 失控聚合风险

5. **综合判定适合度**

## Examples
**Example 1: FEC (高度适合的 SEI 添加剂)**
```yaml
input:
  smiles: "FC1COC(=O)O1"
  functional_groups: ["cyclic_carbonate", "C-F"]
  phys_chem:
    reduction_tendency:
      red_sites_ranked:
        - { rank: 1, site: "羰基 C=O" }
        - { rank: 2, site: "C-F 键" }
        
output:
  suitability: "high"
  additive_type: "SEI_former"
  evidence:
    positive:
      - "含 C-F 键，还原释放 F⁻ 形成 LiF"
      - "优先于 EC 还原（LUMO 更低）"
      - "开环聚合形成柔性有机膜"
      - "大量文献和商业应用验证"
    negative:
      - "首次循环 CE 略降（牺牲部分锂）"
  priority_reaction: "reduction"
  film_contribution: "LiF + 聚合物混合"
  recommended_dosage: "low（2-10%）"
```

**Example 2: VC (适合的 SEI 添加剂)**
```yaml
input:
  smiles: "C=C1OC(=O)O1"
  functional_groups: ["cyclic_carbonate", "vinyl"]
  phys_chem:
    reduction_tendency:
      dominant_site: "乙烯基共轭羰基"
        
output:
  suitability: "high"
  additive_type: "SEI_former"
  evidence:
    positive:
      - "乙烯基易聚合，形成柔性聚合物膜"
      - "优先于 EC 还原"
      - "改善 SEI 的机械稳定性"
    negative:
      - "纯有机膜，离子电导率可能不如 LiF 富集膜"
  priority_reaction: "reduction"
  film_contribution: "聚合物为主"
  recommended_dosage: "low（1-5%）"
```

**Example 3: EC (不适合作为添加剂)**
```yaml
input:
  smiles: "C1COC(=O)O1"
  functional_groups: ["cyclic_carbonate"]
        
output:
  suitability: "unsuitable"
  additive_type: null
  evidence:
    positive: []
    negative:
      - "作为主溶剂使用，不是添加剂"
      - "无特殊成膜增强功能"
      - "大用量使用，不符合添加剂定义"
  priority_reaction: null
  film_contribution: null
  recommended_dosage: null
  note: "EC 是主溶剂，参与 SEI 形成但不作为添加剂"
```

## Guardrails
- 明确区分"主溶剂参与成膜"和"添加剂功能"
- 添加剂通常小用量（<10%）
- 不预测具体成膜速率或厚度
- 新型添加剂需降低置信度
- "牺牲型"添加剂的不稳定是设计特性，不是缺陷

## Dependencies
- 上游：OrganicChem 官能团识别、开环位点
- 上游：PhysChem LUMO/HOMO 排序
- 下游：SEI_02_polymer_film_v1, SEI_04_lif_tendency_v1

## Changelog
- 2025-12-25: 初始版本


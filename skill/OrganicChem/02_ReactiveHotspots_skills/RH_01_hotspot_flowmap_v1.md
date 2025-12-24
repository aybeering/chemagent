# RH_01_hotspot_flowmap_v1 — 反应敏感位点总路由

## Triggers
- 需要全面识别分子中的反应敏感位点
- 需要为 PhysChem 分析提供目标位点
- 作为 OrganicChem 反应位点分析的主入口被调用

## Inputs
- 分子表示：SMILES / 结构描述
- 结构解剖数据（推荐）：来自 SD_01 的 structure_digest
- 分析范围（可选）：`all` / `specific`（指定类型）
- 指定类型（可选）：["nucleophilic", "electrophilic", "elimination", "ring_opening", "rearrangement"]

## Outputs
- `nucleophilic_sites`: 亲核位点列表
- `electrophilic_sites`: 亲电位点列表
- `elimination_sites`: 消除位点列表
- `ring_opening_sites`: 开环位点列表
- `rearrangement_sites`: 重排倾向位点列表
- `hotspot_summary`: 敏感位点摘要
- `physchem_targets`: 推荐给 PhysChem 分析的目标

## Rules
- **依赖结构解剖**：若无 SD 输出，先调用 SD_01 获取
- **按类型分组**：每种位点类型由专门的子卡处理
- **避免重复**：同一原子可能同时是多种位点类型，需标记
- **置信度评估**：综合结构特征给出置信度

## Steps
1. **检查输入**
   - 验证 SMILES 有效性
   - 若无 structure_digest，调用 SD_01 获取

2. **调用亲核位点识别** → `RH_02_nucleophilic_site_v1`
   - 识别 n 孤对、π 系统、负离子等

3. **调用亲电位点识别** → `RH_03_electrophilic_site_v1`
   - 识别羰基碳、sp3-LG、缺电子芳环等

4. **调用消除位点识别** → `RH_04_elimination_site_v1`
   - 识别 β-H + LG 组合

5. **调用开环位点识别** → `RH_05_ring_opening_site_v1`
   - 识别环氧、内酯、小环等

6. **调用重排位点识别** → `RH_06_rearrangement_site_v1`
   - 识别迁移倾向位点

7. **汇总输出**
   - 整合各子卡结果
   - 生成敏感位点摘要
   - 推荐 PhysChem 分析目标

## Examples

**Example 1: 乙酰氯**
```yaml
input:
  smiles: "CC(=O)Cl"
  
output:
  electrophilic_sites:
    - site_id: "E_1"
      atom_index: 1
      site_type: "carbonyl_C"
      strength: "strong"
      leaving_group: "Cl"
      confidence: 0.95
  
  nucleophilic_sites:
    - site_id: "NU_1"
      atom_index: 2
      site_type: "n_lonepair"
      strength: "weak"
      notes: "羰基氧孤对，但因吸电子效应减弱"
  
  hotspot_summary: "酰卤：强亲电羰基碳，Cl 为良好离去基团"
  
  physchem_targets:
    - module: "LUMO_02"
      target_sites: [1]
      reason: "羰基 π* 是主要 LUMO"
```

**Example 2: 环氧乙烷**
```yaml
input:
  smiles: "C1OC1"
  
output:
  electrophilic_sites:
    - site_id: "E_1"
      atom_index: 0
      site_type: "strained_C"
      strength: "moderate"
    - site_id: "E_2"
      atom_index: 2
      site_type: "strained_C"
      strength: "moderate"
  
  nucleophilic_sites:
    - site_id: "NU_1"
      atom_index: 1
      site_type: "n_lonepair"
      strength: "weak"
      notes: "醚氧孤对，但环张力使其亲核性降低"
  
  ring_opening_sites:
    - site_id: "RO_1"
      ring_id: "RING_1"
      attack_atom: 0
      ring_type: "epoxide"
      strain_driven: true
      confidence: 0.95
  
  hotspot_summary: "高张力三元环氧化物，易被亲核试剂开环"
  
  physchem_targets:
    - module: "LUMO_04"
      reason: "环张力贡献 σ* LUMO"
```

**Example 3: 2-溴丙烷**
```yaml
input:
  smiles: "CC(Br)C"
  
output:
  electrophilic_sites:
    - site_id: "E_1"
      atom_index: 1
      site_type: "sp3_with_LG"
      strength: "moderate"
      leaving_group: "Br"
      notes: "仲卤代烷，SN1/SN2 竞争"
  
  elimination_sites:
    - site_id: "EL_1"
      c_alpha: 1
      c_beta: 0
      leaving_group: "Br"
      beta_h_count: 3
      mechanism_preference: "E2"
      confidence: 0.85
    - site_id: "EL_2"
      c_alpha: 1
      c_beta: 2
      leaving_group: "Br"
      beta_h_count: 3
      mechanism_preference: "E2"
      confidence: 0.85
  
  hotspot_summary: "仲溴代烷：SN2/SN1/E2 竞争，具体取决于条件"
```

## Guardrails
- 不预测具体反应产物（交给 reaction 模块）
- 不评估反应可行性（需考虑条件、试剂）
- 对于高度对称分子，合并等效位点
- 复杂多官能团分子需标注"可能存在竞争"

## Dependencies
- `SD_01_digest_flowmap_v1`（结构解剖）
- `RH_02_nucleophilic_site_v1`
- `RH_03_electrophilic_site_v1`
- `RH_04_elimination_site_v1`
- `RH_05_ring_opening_site_v1`
- `RH_06_rearrangement_site_v1`

## Changelog
- 2025-12-24: 初始版本


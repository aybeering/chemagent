# SD_05_ring_system_v1 — 环系分析

## Triggers
- 需要分析分子中的环系结构
- 需要判断环的芳香性、张力水平
- 需要识别稠合环、桥环、杂环

## Inputs
- 分子表示：SMILES / 结构描述
- 骨架信息（可选）：来自 SD_02 的 skeleton 数据

## Outputs
```yaml
ring_info:
  - ring_id: "RING_1"
    size: <int>
    atoms: [<原子索引>]
    bonds: [<键索引>]
    aromatic: true | false
    strain_level: "none | low | medium | high"
    ring_type: "carbocycle | heterocycle"
    heteroatoms: ["N", "O", ...]
    saturation: "saturated | unsaturated | aromatic"
    fusion:
      fused_with: ["RING_2"]
      fusion_atoms: [<共享原子>]
      fusion_type: "ortho | peri | spiro | bridged"
    special_features: ["lactone", "lactam", "cyclic_carbonate", ...]
```

## Rules

### 环大小与张力

| 环大小 | 张力水平 | 说明 |
|--------|----------|------|
| 3 | high | 环丙烷、环氧化物 |
| 4 | high | 环丁烷、β-内酰胺 |
| 5 | low | 五元环，略有张力 |
| 6 | none | 六元环，无张力 |
| 7 | low | 七元环，略有张力 |
| 8+ | low/medium | 大环，跨环张力 |

### 芳香性判定 (Hückel 规则)

| 条件 | 结果 |
|------|------|
| 平面共轭环，4n+2 π 电子 | 芳香 |
| 平面共轭环，4n π 电子 | 反芳香 |
| 非平面或不连续共轭 | 非芳香 |

**常见芳香环**：
- 苯 (6 π)
- 吡啶 (6 π)
- 呋喃 (6 π)
- 吡咯 (6 π，N 孤对参与)
- 噻吩 (6 π)
- 咪唑 (6 π)
- 萘 (10 π)

### 杂环分类

| 杂环类型 | 元素组成 | 示例 |
|----------|----------|------|
| 含氧杂环 | O | 呋喃、吡喃、环氧、二氧戊环 |
| 含氮杂环 | N | 吡咯、吡啶、咪唑、嘧啶 |
| 含硫杂环 | S | 噻吩、四氢噻吩 |
| 混合杂环 | N+O, N+S | 噁唑、噻唑 |

### 特殊环系识别

| 特殊类型 | 识别规则 | 含义 |
|----------|----------|------|
| lactone | 环内含 C(=O)O | 内酯 |
| lactam | 环内含 C(=O)N | 内酰胺 |
| cyclic_carbonate | 环内含 OC(=O)O | 环状碳酸酯 |
| anhydride | 环内含 C(=O)OC(=O) | 环状酸酐 |
| epoxide | 3 元环含 O | 环氧化物 |
| aziridine | 3 元环含 N | 氮杂环丙烷 |

## Steps
1. **检测所有环**
   - 使用最小环检测算法
   - 分配唯一 ring_id
   
2. **分析每个环**
   - 确定大小和原子组成
   - 计算张力水平
   
3. **判定芳香性**
   - 检查平面性和 π 电子数
   
4. **识别稠合关系**
   - 检测共享原子/键
   - 分类稠合类型
   
5. **识别特殊环系**
   - 匹配内酯、内酰胺等模式

## Examples

**Example 1: 苯**
```yaml
input: "c1ccccc1"
output:
  ring_info:
    - ring_id: "RING_1"
      size: 6
      atoms: [0, 1, 2, 3, 4, 5]
      aromatic: true
      strain_level: "none"
      ring_type: "carbocycle"
      saturation: "aromatic"
```

**Example 2: 环氧乙烷**
```yaml
input: "C1OC1"
output:
  ring_info:
    - ring_id: "RING_1"
      size: 3
      atoms: [0, 1, 2]
      aromatic: false
      strain_level: "high"
      ring_type: "heterocycle"
      heteroatoms: ["O"]
      saturation: "saturated"
      special_features: ["epoxide"]
```

**Example 3: 萘**
```yaml
input: "c1ccc2ccccc2c1"
output:
  ring_info:
    - ring_id: "RING_1"
      size: 6
      atoms: [0, 1, 2, 3, 9, 8]
      aromatic: true
      strain_level: "none"
      ring_type: "carbocycle"
      fusion:
        fused_with: ["RING_2"]
        fusion_atoms: [3, 8]
        fusion_type: "ortho"
    - ring_id: "RING_2"
      size: 6
      atoms: [3, 4, 5, 6, 7, 8]
      aromatic: true
      strain_level: "none"
      ring_type: "carbocycle"
      fusion:
        fused_with: ["RING_1"]
        fusion_atoms: [3, 8]
        fusion_type: "ortho"
```

**Example 4: γ-丁内酯**
```yaml
input: "C1CCC(=O)O1"
output:
  ring_info:
    - ring_id: "RING_1"
      size: 5
      atoms: [0, 1, 2, 3, 5]
      aromatic: false
      strain_level: "low"
      ring_type: "heterocycle"
      heteroatoms: ["O"]
      saturation: "unsaturated"
      special_features: ["lactone"]
```

**Example 5: 碳酸乙烯酯 (EC)**
```yaml
input: "C1COC(=O)O1"
output:
  ring_info:
    - ring_id: "RING_1"
      size: 5
      atoms: [0, 1, 2, 3, 5]
      aromatic: false
      strain_level: "low"
      ring_type: "heterocycle"
      heteroatoms: ["O", "O"]
      saturation: "unsaturated"
      special_features: ["cyclic_carbonate"]
```

**Example 6: 吡啶**
```yaml
input: "c1ccncc1"
output:
  ring_info:
    - ring_id: "RING_1"
      size: 6
      atoms: [0, 1, 2, 3, 4, 5]
      aromatic: true
      strain_level: "none"
      ring_type: "heterocycle"
      heteroatoms: ["N"]
      saturation: "aromatic"
      notes: "吡啶型 N，孤对不参与芳香性"
```

## Guardrails
- 对于复杂多环体系（>5 个环），简化报告
- 不预测环的反应性（交给 ReactiveHotspots）
- 大环（>12 元）的张力评估置信度降低
- 反芳香体系需特别标注

## Confusable Cases
- 吡咯 vs 吡啶：吡咯 N-H 孤对参与芳香性，吡啶不参与
- 呋喃 vs 四氢呋喃：芳香性不同
- 稠合 vs 桥接：共享边 vs 共享两个不相邻原子

## Changelog
- 2025-12-24: 初始版本


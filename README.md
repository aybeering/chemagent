# ChemAgent - 化学智能体系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一个基于技能卡片（Skill Cards）的多专家协作化学智能体系统，专门用于电解液分子审计和分析。系统采用模块化设计，将复杂的化学分析任务分解为多个专业化子模块，实现精确、结构化的分子性质预测。

## 🚀 项目特色

- **多专家协作**: 6个专业化化学专家模块协同工作
- **技能卡片架构**: 基于Prompt Engineering的标准化技能模块
- **结构化分析**: 从分子结构到反应机理的系统化分析流程
- **对比测试**: 内置有/无技能版本的对比分析功能
- **模块化设计**: 易于扩展和定制的模块化架构

## 📋 系统架构

### 核心专家模块

```
ChemAgent
├── 🧪 OrganicChem - 有机结构专家
│   ├── 结构解剖 (Structure Digest)
│   ├── 反应敏感位点 (Reactive Hotspots)
│   └── 官能团簇路由 (Functional Cluster Router)
├── ⚛️ PhysChem - 物理有机/电子效应专家
│   ├── 电子效应分析 (Electronic Effects)
│   ├── 氧化倾向评估 (HOMO Tendency)
│   ├── 还原倾向评估 (LUMO Tendency)
│   ├── 界面优先位点 (Interface Sites)
│   └── 稳定性权衡 (Stability Tradeoffs)
├── 🔋 ElectroChem - 电化学机理专家
├── 💧 Solvation - 溶剂化与传输专家
├── ⚠️ Safety - 安全与材料兼容专家
├── 🏭 Synthesis - 可合成与工程化专家
├── 🔍 RedTeam - 证据审计/红队专家
└── ⚖️ Arbitration - 仲裁与报告生成专家
```

### 技能库统计

- **OrganicChem**: 22个技能卡片，3个核心模块
- **PhysChem**: 28个技能卡片，5个分析模块
- **总计**: 50+专业化技能模块

## 🛠️ 安装与配置

### 环境要求

- Python 3.8+
- conda (推荐)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-repo/chemagent.git
cd chemagent
```

2. **创建conda环境**
```bash
conda create -n chemagent python=3.9
conda activate chemagent
```

3. **安装依赖**
```bash
pip install openai python-dotenv
```

4. **配置API密钥**
```bash
# 在项目根目录创建 .env 文件
echo "DEEPSEEK_API_KEY=your_api_key_here" > .env
```

## 🎯 使用方法

### 快速测试

#### 1. PhysChem 电子效应分析测试
```bash
python mvp/phschem.py
```
测试对硝基苯甲醚的电子效应分析，对比有/无技能版本的差异。

#### 2. OrganicChem + PhysChem 联动测试
```bash
python mvp/or_and_phs.py
```
完整测试水杨酸的结构解析和物理化学性质分析，包含三个版本对比：
- 无技能版本（通用LLM）
- 有机化学分析（OrganicChem）
- 物理化学分析（PhysChem）

### 输出结果

所有分析结果自动保存到 `output/` 目录：
- `salicylic_acid_without_skill.md` - 无技能版本结果
- `salicylic_acid_organic_chem.md` - 有机化学分析结果
- `salicylic_acid_phys_chem.md` - 物理化学分析结果
- `salicylic_acid_comparison.md` - 详细对比分析报告

## 📁 项目结构

```
chemagent/
├── mvp/                          # 最小可行产品测试脚本
│   ├── phschem.py               # PhysChem 单模块测试
│   └── or_and_phs.py           # OrganicChem + PhysChem 联动测试
├── skill/                       # 技能卡片库
│   ├── OrganicChem/            # 有机化学专家模块
│   │   ├── 01_StructureDigest_skills/    # 结构解剖技能
│   │   ├── 02_ReactiveHotspots_skills/   # 反应敏感位点技能
│   │   └── 03_FunctionalClusterRouter_skills/  # 官能团簇路由技能
│   ├── PhysChem/               # 物理化学专家模块
│   │   ├── 01_ELEC_skills/     # 电子效应分析技能
│   │   ├── 02_HOMO_OxTendency_Qual_skills/  # 氧化倾向技能
│   │   ├── 03_LUMO_RedTendency_Qual_skills/  # 还原倾向技能
│   │   ├── 04_InterfaceFirstStrikeSites_skills/  # 界面位点技能
│   │   └── 05_StabilityTradeoffNotes_skills/  # 稳定性权衡技能
│   ├── reaction/               # 反应机理技能库
│   ├── site_skills/           # 位点识别技能库
│   └── 专家注册表.md          # 专家模块注册表
├── output/                     # 分析结果输出目录
├── 智能体构件.md               # 系统架构说明
└── README.md                   # 项目说明文档
```

## 🔬 技能卡片架构

### 设计理念

- **标准化**: 每个技能卡片有统一的输入/输出格式
- **模块化**: 技能可独立调用，也可组合使用
- **专业化**: 每个技能专注于特定化学分析任务
- **可扩展**: 易于添加新的技能模块

### 技能卡片示例

```markdown
# ELEC_01_effect_flowmap_v1 - 电子效应流程图

## Context
分析分子中电子效应的传递路径和强度

## Inputs
- molecule: SMILES字符串
- target_sites: 关注的位点列表

## Outputs
- effect_summary: 电子效应总结
- channels: 传递通道分析
- site_impacts: 各位点影响

## Rules
- 严格按诱导/共振/超共轭/场效应分类
- 量化相对强度
- 考虑立体化学影响
```

## 📊 测试结果对比

### 水杨酸分析对比

| 分析维度 | 无技能版本 | 有技能版本 |
|---------|-----------|-----------|
| 结构识别 | 笼统描述"苯环+羧酸+酚" | 精确分类：单环芳香、羧酸簇、酚簇 |
| 位点识别 | 直觉判断活性位点 | 系统化：SD→RH→FC三级路由 |
| 电子效应 | 模糊描述"吸电子/给电子" | 分通道：-COOH(-I/-M), -OH(+M/-I) |
| HOMO/LUMO | 可能遗漏或简化描述 | 量化分析：孤对能级、π轨道特征 |
| 分子内氢键 | 可能提及但不深入分析 | 详细评估对电子效应和酸性的影响 |

### 性能提升

- **分析深度**: 从通用描述到专业级结构化分析
- **预测准确性**: 从经验规则到基于机理的定量预测
- **结果一致性**: 标准化输出格式确保分析一致性
- **扩展性**: 模块化设计支持新分子类型快速适配

## 🎯 应用场景

### 电解液分子审计

1. **结构解析**: 识别分子骨架、官能团、反应位点
2. **电子效应分析**: 评估氧化/还原倾向，预测反应活性
3. **界面行为预测**: 判断SEI/CEI形成倾向，评估膜稳定性
4. **安全评估**: 识别潜在分解路径，评估热/电化学稳定性
5. **合成可行性**: 评估合成复杂度，预测放大生产风险

### 支持的分子类型

- 碳酸酯类溶剂 (Carbonates)
- 醚类化合物 (Ethers)
- 腈类化合物 (Nitriles)
- 含硫化合物 (Sulfur-containing)
- 含磷化合物 (Phosphorus-containing)
- 含硼化合物 (Boron-containing)
- 氟代化合物 (Fluorinated compounds)

## 🤝 贡献指南

### 添加新技能卡片

1. **确定领域**: 选择合适的专家模块
2. **设计技能**: 定义输入/输出格式和分析规则
3. **编写卡片**: 按照标准模板创建markdown文件
4. **测试验证**: 使用mvp脚本验证效果
5. **文档更新**: 更新对应的索引和路由文件

### 技能卡片命名规范

```
[MODULE]_[INDEX]_[NAME]_v[VERSION].md

示例:
ELEC_01_effect_flowmap_v1.md
HOMO_02_lonepair_n_v1.md
```

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 👥 作者

- **ChemAgent Team** - 化学智能体开发团队

## 🙏 致谢

- 感谢 DeepSeek 提供的大语言模型API支持
- 感谢开源化学计算社区的技术贡献

---

**注意**: 本项目专注于定性分析和机理预测，不提供定量计算结果。如需精确的量子化学计算，请使用专门的计算化学软件。

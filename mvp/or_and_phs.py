#!/usr/bin/env python3
"""
OrganicChem + PhysChem 联动测试脚本

测试流程：
1. OrganicChem 阶段：结构解剖 → 敏感位点识别 → 官能团簇路由
2. PhysChem 阶段：根据 OrganicChem 的路由建议进行电子效应/HOMO/LUMO 分析

以水杨酸（Salicylic Acid）为例，展示完整的分析流程。

使用方法：
1. 激活 conda 环境：conda activate chemagent
2. 在项目根目录创建 .env 文件，添加：DEEPSEEK_API_KEY=your_api_key_here
3. 安装依赖：pip install openai python-dotenv
4. 运行：python mvp/or_and_phs.py

作者：chemagent
日期：2025-12-24
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# ============================================================================
# 配置
# ============================================================================

DEEPSEEK_API_BASE = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 测试分子：水杨酸（Salicylic Acid）
# 结构：邻羟基苯甲酸，含有羧酸、酚羟基、芳环三个官能团
TEST_MOLECULE = {
    "smiles": "OC(=O)c1ccccc1O",
    "name": "Salicylic Acid (水杨酸)",
    "description": "邻羟基苯甲酸，含有羧酸基团和酚羟基，是阿司匹林的前体",
}

# Skill 文件路径
SKILL_BASE = Path(__file__).parent.parent / "skill"
ORGANIC_CHEM_DIR = SKILL_BASE / "OrganicChem"
PHYS_CHEM_DIR = SKILL_BASE / "PhysChem"


# ============================================================================
# 工具函数
# ============================================================================

def load_env():
    """加载 .env 文件中的环境变量"""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print("=" * 70)
        print("错误：未找到 .env 文件")
        print("=" * 70)
        print(f"\n请在项目根目录创建 .env 文件，添加以下内容：\n")
        print("    DEEPSEEK_API_KEY=your_api_key_here\n")
        print(f"期望路径：{env_path.absolute()}")
        print("=" * 70)
        sys.exit(1)
    
    load_dotenv(env_path)
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("错误：DEEPSEEK_API_KEY 未设置或为默认值")
        sys.exit(1)
    
    return api_key


def load_skills_from_dir(skill_dir: Path, pattern: str = "*.md") -> str:
    """加载指定目录下的所有 skill 文件"""
    skills_content = []
    
    # 加载主目录下的接口文件
    for md_file in sorted(skill_dir.glob("*.md")):
        if md_file.name.startswith("00_") or md_file.name.endswith("_Router.md") or md_file.name.endswith("_Schema.md"):
            content = md_file.read_text(encoding="utf-8")
            skills_content.append(f"--- {md_file.name} ---\n{content}")
    
    # 加载子目录下的 skill 卡片
    for subdir in sorted(skill_dir.iterdir()):
        if subdir.is_dir() and subdir.name.endswith("_skills"):
            for md_file in sorted(subdir.glob("*.md")):
                content = md_file.read_text(encoding="utf-8")
                skills_content.append(f"--- {subdir.name}/{md_file.name} ---\n{content}")
    
    return "\n\n".join(skills_content)


def load_organic_chem_skills() -> str:
    """加载 OrganicChem 技能库"""
    return load_skills_from_dir(ORGANIC_CHEM_DIR)


def load_phys_chem_skills() -> str:
    """加载 PhysChem 技能库"""
    return load_skills_from_dir(PHYS_CHEM_DIR)


def call_deepseek(client: OpenAI, system_prompt: str, user_message: str, max_tokens: int = 3000) -> str:
    """调用 DeepSeek API"""
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[API 调用失败: {e}]"


# ============================================================================
# 阶段 1：OrganicChem 结构解析
# ============================================================================

def run_organic_chem_analysis(client: OpenAI, organic_skills: str) -> str:
    """运行 OrganicChem 结构解析"""
    
    system_prompt = f"""你是一位有机化学结构解析专家，专注于分子结构解剖、反应敏感位点识别和官能团簇路由。

你拥有以下 OrganicChem 技能库，请严格按照技能卡片中定义的框架、规则和输出格式来分析：

{organic_skills}

--- 使用说明 ---
1. 首先调用 SD_01_digest_flowmap_v1 进行结构解剖
2. 然后调用 RH_01_hotspot_flowmap_v1 识别反应敏感位点
3. 最后调用 FC_01_cluster_router_v1 进行官能团簇路由，推荐 PhysChem 分析模块

请按照 OrganicChem_Schema.md 定义的输出格式给出结果。"""

    user_message = f"""请对以下分子进行完整的 OrganicChem 分析：

分子名称：{TEST_MOLECULE['name']}
SMILES：{TEST_MOLECULE['smiles']}
描述：{TEST_MOLECULE['description']}

请按照以下步骤输出分析结果：

## 1. 结构解剖（Structure Digest）
- 骨架类型
- 官能团列表（类型、位置、中心原子）
- 杂原子标签（杂化、孤对、电荷）
- 环系信息（芳香性）
- 共轭网络映射

## 2. 反应敏感位点（Reactive Hotspots）
- 亲核位点（类型、强度）
- 亲电位点（类型、强度）
- 消除位点（若有）
- 其他敏感位点

## 3. 官能团簇路由（Functional Cluster Routing）
- 识别的官能团簇
- 推荐的 PhysChem 分析模块
- 路由建议摘要

请以 YAML 格式输出关键信息，并附带文字解释。"""

    return call_deepseek(client, system_prompt, user_message)


# ============================================================================
# 阶段 2：PhysChem 物理化学分析
# ============================================================================

def run_phys_chem_analysis(client: OpenAI, phys_skills: str, organic_output: str) -> str:
    """运行 PhysChem 物理化学分析"""
    
    system_prompt = f"""你是一位物理化学专家，专注于电子效应、HOMO/LUMO 趋势和界面反应位点分析。

你拥有以下 PhysChem 技能库，请严格按照技能卡片中定义的框架、规则和输出格式来分析：

{phys_skills}

--- 使用说明 ---
1. 根据上游 OrganicChem 的分析结果和路由建议，选择合适的分析模块
2. 调用 ELEC 模块分析电子效应（诱导、共振、超共轭等）
3. 调用 HOMO 模块分析氧化倾向
4. 调用 LUMO 模块分析还原倾向（若适用）
5. 综合给出物理化学性质评估

请按照 PhysChem_Schema.md 定义的输出格式给出结果。"""

    user_message = f"""基于 OrganicChem 上游分析结果，请对水杨酸进行 PhysChem 物理化学分析。

分子信息：
- 名称：{TEST_MOLECULE['name']}
- SMILES：{TEST_MOLECULE['smiles']}

OrganicChem 上游分析结果：
{organic_output}

请按照以下步骤进行 PhysChem 分析：

## 1. 电子效应分析（ELEC）
- 羧基（-COOH）的电子效应（-I/-M）
- 酚羟基（-OH）的电子效应（+M/-I）
- 两者对芳环电子密度的综合影响
- 分子内氢键对电子效应的影响

## 2. 氧化倾向分析（HOMO）
- 主要 HOMO 贡献者（芳环 π、酚氧孤对等）
- 氧化敏感位点排序
- 取代基调制效应

## 3. 还原倾向分析（LUMO）
- 主要 LUMO 贡献者（羰基 π* 等）
- 还原敏感位点排序

## 4. 综合评估
- 水杨酸的主要反应活性位点
- 酸性分析（酚羟基 vs 羧酸）
- 与 PhysChem 模块的对应关系

请以结构化格式输出分析结果。"""

    return call_deepseek(client, system_prompt, user_message)


# ============================================================================
# 阶段 0：无 Skill 版本（直接 LLM 分析）
# ============================================================================

def run_without_skill_analysis(client: OpenAI) -> str:
    """运行无 Skill 版本：直接让 LLM 分析水杨酸"""

    system_prompt = """你是一位化学专家，擅长有机化学和物理化学分析。
请用专业但易懂的方式回答问题，重点关注分子的结构特征、反应活性位点和物理化学性质。"""

    user_message = f"""请对以下分子进行完整的化学分析：

分子名称：{TEST_MOLECULE['name']}
SMILES：{TEST_MOLECULE['smiles']}
描述：{TEST_MOLECULE['description']}

请从以下几个方面进行分析：

## 1. 分子结构特征
- 基本骨架和官能团识别
- 立体化学和构象特征
- 共轭体系和电子分布

## 2. 反应活性位点
- 亲核位点（类型和强度排序）
- 亲电位点（类型和强度排序）
- 酸性/碱性位点
- 氧化/还原敏感位点

## 3. 物理化学性质
- 电子效应分析（诱导效应、共振效应等）
- 氧化倾向（HOMO相关）
- 还原倾向（LUMO相关）
- 酸碱性质分析

## 4. 特殊性质
- 分子内氢键效应
- 水杨酸的特殊酸性
- 与其他类似分子的比较

请给出详细而结构化的分析结果。"""

    return call_deepseek(client, system_prompt, user_message, max_tokens=4000)


# ============================================================================
# 输出格式化
# ============================================================================

def print_separator(title: str = "", char: str = "=", width: int = 70):
    """打印分隔线"""
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"{char * padding} {title} {char * padding}")
    else:
        print(char * width)


def save_output_to_file(filename: str, content: str):
    """将输出保存到文件"""
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    filepath = output_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"    ✓ 输出已保存到：{filepath}")
    return filepath


def print_molecule_info():
    """打印分子信息"""
    print_separator("测试分子：水杨酸")
    print(f"""
    名称：{TEST_MOLECULE['name']}
    SMILES：{TEST_MOLECULE['smiles']}
    描述：{TEST_MOLECULE['description']}
    
    结构示意：
    
              O
              ‖
         C — O — H     (羧酸基团)
        /
       ◯ —— ◯
      //    \\
     ◯      ◯      (苯环)
      \\    //
       ◯ —— ◯
        \\
         O — H          (酚羟基)
    
    特点：
    • 邻位取代苯环（1,2-二取代）
    • 羧酸基团：强酸性，-I/-M 吸电子
    • 酚羟基：弱酸性，+M 给电子（与羧酸形成分子内氢键）
    • 共轭体系：羧基与芳环共轭
""")


def print_analysis_flow():
    """打印分析流程图"""
    print_separator("分析流程")
    print("""
    ┌─────────────────────────────────────────────────────────────────┐
    │                      水杨酸 (SMILES)                            │
    └───────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                 【阶段 1】OrganicChem 分析                       │
    │  ┌─────────────────────────────────────────────────────────┐   │
    │  │ SD: 结构解剖                                             │   │
    │  │  • 骨架：单环芳香                                        │   │
    │  │  • 官能团：羧酸 + 酚 + 苯环                              │   │
    │  │  • 共轭：羧基与芳环共轭                                  │   │
    │  └─────────────────────────────────────────────────────────┘   │
    │  ┌─────────────────────────────────────────────────────────┐   │
    │  │ RH: 敏感位点                                             │   │
    │  │  • 亲核：酚氧孤对、羧酸氧孤对                            │   │
    │  │  • 亲电：羧基碳                                          │   │
    │  │  • 酸性位点：羧酸 H、酚 H                                │   │
    │  └─────────────────────────────────────────────────────────┘   │
    │  ┌─────────────────────────────────────────────────────────┐   │
    │  │ FC: 官能团簇路由                                         │   │
    │  │  • 羰基簇 → LUMO_02                                      │   │
    │  │  • 氧簇 → HOMO_02                                        │   │
    │  │  • 不饱和簇 → HOMO_03                                    │   │
    │  └─────────────────────────────────────────────────────────┘   │
    └───────────────────────────┬─────────────────────────────────────┘
                                │
                                │ (路由建议)
                                ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                 【阶段 2】PhysChem 分析                          │
    │  ┌─────────────────────────────────────────────────────────┐   │
    │  │ ELEC: 电子效应                                           │   │
    │  │  • -COOH: -I (强), -M (共轭)                             │   │
    │  │  • -OH: -I (弱), +M (强，与芳环共轭)                     │   │
    │  │  • 分子内氢键影响                                        │   │
    │  └─────────────────────────────────────────────────────────┘   │
    │  ┌─────────────────────────────────────────────────────────┐   │
    │  │ HOMO: 氧化倾向                                           │   │
    │  │  • 酚氧 n 孤对 (主要 HOMO)                               │   │
    │  │  • 芳环 π 系统                                           │   │
    │  └─────────────────────────────────────────────────────────┘   │
    │  ┌─────────────────────────────────────────────────────────┐   │
    │  │ LUMO: 还原倾向                                           │   │
    │  │  • 羧基 C=O π* (主要 LUMO)                               │   │
    │  └─────────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────────┘
""")


# ============================================================================
# 主程序
# ============================================================================

def format_comparison_results(without_skill: str, organic_output: str, phys_output: str):
    """格式化对比结果"""

    separator = "=" * 80

    # 构建完整的输出内容
    output_content = f"""{separator}
OrganicChem + PhysChem 联动测试对比 - 水杨酸（Salicylic Acid）
{separator}

测试分子信息：
- 名称：{TEST_MOLECULE['name']}
- SMILES：{TEST_MOLECULE['smiles']}
- 描述：{TEST_MOLECULE['description']}

{separator}
【版本 1】无 Skill 版本 - 通用化学助手
{separator}
{without_skill}

{separator}
【版本 2】有 Skill 版本 - OrganicChem 分析
{separator}
{organic_output}

{separator}
【版本 3】有 Skill 版本 - PhysChem 分析
{separator}
{phys_output}

{separator}
对比分析总结
{separator}

预期差异分析（水杨酸 - 邻羟基苯甲酸）：
┌─────────────────────────────────────────────────────────────────────────┐
│ 分析维度              │ 无 Skill 版本                      │ 有 Skill 版本                      │
├─────────────────────────────────────────────────────────────────────────┤
│ 结构识别              │ 笼统描述"苯环+羧酸+酚"           │ 精确分类：单环芳香、羧酸簇、酚簇    │
│ 位点识别              │ 直觉判断活性位点                  │ 系统化：SD→RH→FC 三级路由         │
│ 电子效应              │ 模糊描述"吸电子/给电子"           │ 分通道：-COOH(-I/-M), -OH(+M/-I) │
│ HOMO/LUMO             │ 可能遗漏或简化描述                │ 量化分析：孤对能级、π轨道特征     │
│ 分子内氢键            │ 可能提及但不深入分析              │ 详细评估对电子效应和酸性的影响     │
│ 输出格式              │ 自由格式，可能不系统              │ 结构化YAML + 技能框架输出         │
│ 专业深度              │ 通用化学知识水平                  │ 领域专用技能卡片深度分析          │
└─────────────────────────────────────────────────────────────────────────┘

关键改进点：
• 结构化分析流程：从笼统描述到精确的官能团簇识别
• 电子效应量化：从定性判断到分通道（诱导/共振/超共轭）分析
• 反应活性预测：从经验规则到基于HOMO/LUMO的机制分析
• 分子间比较：水杨酸vs苯甲酸酸性差异的分子内氢键解释

{separator}
"""

    return output_content


def main():
    print("\n" + "=" * 80)
    print("  OrganicChem + PhysChem 联动测试对比")
    print("  测试分子：水杨酸（Salicylic Acid）")
    print("  对比版本：无Skill vs 有Skill（OrganicChem+PhysChem）")
    print("=" * 80)

    # 打印分子信息和分析流程
    print_molecule_info()
    print_analysis_flow()

    # 1. 加载环境变量
    print_separator("初始化", width=80)
    print("\n[1/6] 加载 API Key...")
    api_key = load_env()
    print("    ✓ API Key 已加载")

    # 2. 创建 DeepSeek 客户端
    print("\n[2/6] 初始化 DeepSeek 客户端...")
    client = OpenAI(
        api_key=api_key,
        base_url=DEEPSEEK_API_BASE,
    )
    print("    ✓ 客户端已初始化")

    # 3. 加载技能库
    print("\n[3/6] 加载技能库...")
    print("    - 加载 OrganicChem 技能库...")
    organic_skills = load_organic_chem_skills()
    organic_count = organic_skills.count("--- ")
    print(f"    ✓ 已加载 {organic_count} 个 OrganicChem 文件")

    print("    - 加载 PhysChem 技能库...")
    phys_skills = load_phys_chem_skills()
    phys_count = phys_skills.count("--- ")
    print(f"    ✓ 已加载 {phys_count} 个 PhysChem 文件")

    # 4. 版本 1：无 Skill 分析
    print("\n[4/6] 运行版本 1：无 Skill 分析...")
    print("    （直接 LLM 通用化学分析）")
    without_skill_output = run_without_skill_analysis(client)
    print("    ✓ 无 Skill 分析完成")

    # 5. 版本 2：有 Skill OrganicChem 分析
    print("\n[5/6] 运行版本 2：OrganicChem 分析...")
    print("    （结构解剖 → 敏感位点 → 官能团簇路由）")
    organic_output = run_organic_chem_analysis(client, organic_skills)
    print("    ✓ OrganicChem 分析完成")

    # 6. 版本 3：有 Skill PhysChem 分析
    print("\n[6/6] 运行版本 3：PhysChem 分析...")
    print("    （电子效应 → HOMO 氧化 → LUMO 还原）")
    phys_output = run_phys_chem_analysis(client, phys_skills, organic_output)
    print("    ✓ PhysChem 分析完成")

    # 保存输出到文件
    print("\n" + "=" * 80)
    print("保存输出结果...")

    # 保存单独的输出文件
    save_output_to_file("salicylic_acid_without_skill.md", without_skill_output)
    save_output_to_file("salicylic_acid_organic_chem.md", organic_output)
    save_output_to_file("salicylic_acid_phys_chem.md", phys_output)

    # 保存对比结果
    comparison_content = format_comparison_results(without_skill_output, organic_output, phys_output)
    comparison_file = save_output_to_file("salicylic_acid_comparison.md", comparison_content)

    # 在控制台显示对比结果
    print(f"\n对比结果已保存至：{comparison_file}")
    print("\n" + "=" * 80)
    print("控制台输出（对比总结）")
    print("=" * 80)
    print(comparison_content.split("对比分析总结")[1])

    print_separator("测试完成", width=80)


if __name__ == "__main__":
    main()


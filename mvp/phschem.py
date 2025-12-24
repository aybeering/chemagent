#!/usr/bin/env python3
"""
PhysChem Skill 测试脚本

对比测试：有/无 PhysChem Skill 时，DeepSeek 模型对电子效应问题的回答质量差异。

使用方法：
1. 激活 conda 环境：conda activate chemagent
2. 在项目根目录创建 .env 文件，添加：DEEPSEEK_API_KEY=your_api_key_here
3. 安装依赖：pip install openai python-dotenv
4. 运行：python mvp/phschem.py

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

# 测试问题 - 使用结构复杂的推拉电子体系
TEST_QUESTION = """
分析对硝基苯甲醚（p-nitroanisole，结构：CH₃O-C₆H₄-NO₂）的电子效应。

这是一个典型的推拉电子体系，请详细分析：

1. 甲氧基（-OMe）和硝基（-NO₂）各自的电子效应类型是什么？
   - 分别是推电子还是拉电子？
   - 通过哪些通道传递（±I 诱导、±M 共振、超共轭、场效应）？

2. 两个取代基如何相互作用？
   - 推拉电子体系中，电子流动的方向是怎样的？
   - 是否存在"通过共轭"的电子转移？

3. 对苯环各位点（2,3,5,6 位）的电子密度有何影响？
   - 哪些位点电子密度升高/降低？
   - 亲电取代反应的定位效应如何？

4. 构象因素对电子效应有何影响？
   - 甲氧基的构象（共面性）如何影响其 +M 效应？
"""

# Skill 文件路径（相对于项目根目录）
SKILL_DIR = Path(__file__).parent.parent / "skill" / "PhysChem" / "01_ELEC_skills"


# ============================================================================
# 工具函数
# ============================================================================

def load_env():
    """加载 .env 文件中的环境变量"""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print("=" * 60)
        print("错误：未找到 .env 文件")
        print("=" * 60)
        print(f"\n请在项目根目录创建 .env 文件，添加以下内容：\n")
        print("    DEEPSEEK_API_KEY=your_api_key_here\n")
        print(f"期望路径：{env_path.absolute()}")
        print("=" * 60)
        sys.exit(1)
    
    load_dotenv(env_path)
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("错误：DEEPSEEK_API_KEY 未设置或为默认值")
        sys.exit(1)
    
    return api_key


def load_elec_skills() -> str:
    """加载 ELEC Skill 卡片内容"""
    skill_files = [
        "ELEC_01_effect_flowmap_v1.md",
        "ELEC_02_I_sigma_v1.md",
        "ELEC_03_M_pi_v1.md",
        "ELEC_04_hyperconj_v1.md",
        "ELEC_05_field_v1.md",
        "ELEC_06_conformation_switch_v1.md",
    ]
    
    skills_content = []
    for filename in skill_files:
        filepath = SKILL_DIR / filename
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            skills_content.append(f"--- {filename} ---\n{content}")
        else:
            print(f"警告：未找到 Skill 文件 {filepath}")
    
    return "\n\n".join(skills_content)


def call_deepseek(client: OpenAI, system_prompt: str, user_message: str) -> str:
    """调用 DeepSeek API"""
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=2000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[API 调用失败: {e}]"


# ============================================================================
# 测试函数
# ============================================================================

def run_without_skill(client: OpenAI) -> str:
    """无 Skill 版本：直接提问"""
    system_prompt = """你是一位化学专家，擅长有机化学和物理化学。
请用专业但易懂的方式回答问题。"""
    
    return call_deepseek(client, system_prompt, TEST_QUESTION)


def run_with_skill(client: OpenAI, skills: str) -> str:
    """有 Skill 版本：注入 ELEC Skills 后提问"""
    system_prompt = f"""你是一位物理化学专家，专注于电子效应分析。

你拥有以下专业技能卡片，请严格按照卡片中定义的框架、规则和输出格式来分析问题：

{skills}

--- 使用说明 ---
1. 首先使用 ELEC_01_effect_flowmap_v1 作为总路由，分解问题
2. 根据问题涉及的通道，调用相应的子技能卡（ELEC_02 诱导效应、ELEC_03 共振效应等）
3. 按照卡片定义的 Outputs 格式输出结论
4. 遵守 Guardrails 中的限制条件

请严格遵循这些技能卡片的分析框架来回答问题。"""
    
    return call_deepseek(client, system_prompt, TEST_QUESTION)


def compare_outputs(without_skill: str, with_skill: str):
    """格式化输出对比结果"""
    separator = "=" * 70
    
    print(f"\n{separator}")
    print("PhysChem Skill 测试对比")
    print(separator)
    
    print(f"\n测试问题：")
    print("-" * 70)
    print(TEST_QUESTION.strip())
    
    print(f"\n{separator}")
    print("【无 Skill 版本】- 通用化学助手")
    print(separator)
    print(without_skill)
    
    print(f"\n{separator}")
    print("【有 Skill 版本】- 注入 ELEC Skills")
    print(separator)
    print(with_skill)
    
    print(f"\n{separator}")
    print("对比分析")
    print(separator)
    print("""
预期差异（对硝基苯甲醚 - 推拉电子体系）：
  ┌───────────────────────────────────────────────────────────────────────┐
  │ 无 Skill 版本                    │ 有 Skill 版本                      │
  ├───────────────────────────────────────────────────────────────────────┤
  │ 笼统描述"OMe 给电子，NO₂ 吸电子"│ 分通道：OMe(+M强,-I弱), NO₂(-M,-I) │
  │ 可能忽略通道竞争与权衡           │ 明确 σ/π 通道分离，给出传递路径     │
  │ 推拉体系相互作用描述模糊         │ 分析"通过共轭"的电子转移方向        │
  │ 位点分析可能不够系统             │ 逐位点(2,3,5,6)电子密度变化分析     │
  │ 可能遗漏构象对共振的影响         │ 调用构象开关卡片，评估共面性影响    │
  │ 缺乏结构化输出格式               │ 按 effect_summary/channels 格式输出 │
  └───────────────────────────────────────────────────────────────────────┘
""")
    print(separator)


# ============================================================================
# 主程序
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("PhysChem Skill 测试脚本")
    print("=" * 70)
    
    # 1. 加载环境变量
    print("\n[1/4] 加载 API Key...")
    api_key = load_env()
    print("    ✓ API Key 已加载")
    
    # 2. 创建 DeepSeek 客户端
    print("\n[2/4] 初始化 DeepSeek 客户端...")
    client = OpenAI(
        api_key=api_key,
        base_url=DEEPSEEK_API_BASE,
    )
    print("    ✓ 客户端已初始化")
    
    # 3. 加载 ELEC Skills
    print("\n[3/4] 加载 ELEC Skill 卡片...")
    skills = load_elec_skills()
    skill_count = skills.count("--- ELEC_")
    print(f"    ✓ 已加载 {skill_count} 个 Skill 卡片")
    
    # 4. 运行对比测试
    print("\n[4/4] 运行对比测试...")
    print("    - 调用无 Skill 版本...")
    without_skill = run_without_skill(client)
    print("    ✓ 无 Skill 版本完成")
    
    print("    - 调用有 Skill 版本...")
    with_skill = run_with_skill(client, skills)
    print("    ✓ 有 Skill 版本完成")
    
    # 5. 输出对比结果
    compare_outputs(without_skill, with_skill)


if __name__ == "__main__":
    main()


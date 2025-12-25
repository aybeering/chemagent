#!/usr/bin/env python3
"""
Skill Hub 测试脚本

使用 FEC（氟代碳酸乙烯酯）作为测试分子，演示跨域查询功能。

测试场景：
1. SEI_04 分析 C-F 键环境时，需要动态查询 OrganicChem 和 PhysChem 的信息
2. 验证跨域查询协议的正确性

使用方法：
    python mvp/test_skill_hub.py

作者：chemagent
日期：2025-12-25
"""

import json
from pathlib import Path
from skill_hub import SkillHub, create_hub, Domain


# ============================================================================
# 测试分子
# ============================================================================

TEST_MOLECULES = {
    "FEC": {
        "smiles": "FC1COC(=O)O1",
        "name": "FEC (氟代碳酸乙烯酯)",
        "description": "锂电池常用成膜添加剂，含 C-F 键，可释放 F⁻ 形成 LiF",
        "expected_lif_tendency": "high"
    },
    "EC": {
        "smiles": "C1COC(=O)O1", 
        "name": "EC (碳酸乙烯酯)",
        "description": "锂电池主溶剂，不含 F，无法直接贡献 LiF",
        "expected_lif_tendency": "none"
    },
    "BTFE": {
        "smiles": "FC(F)(F)COCC(F)(F)F",
        "name": "BTFE (双三氟乙基醚)",
        "description": "LHCE 稀释剂，CF₃ 基团高度稳定",
        "expected_lif_tendency": "low"
    },
    "DFEC": {
        "smiles": "FC1(F)COC(=O)O1",
        "name": "DFEC (二氟代碳酸乙烯酯)",
        "description": "双 F 取代，更多 LiF 来源",
        "expected_lif_tendency": "high"
    }
}


# ============================================================================
# 测试函数
# ============================================================================

def test_cross_domain_query(hub: SkillHub, smiles: str):
    """测试单个跨域查询"""
    print("\n" + "-" * 50)
    print("测试: 跨域查询 - OC.adjacent_groups")
    print("-" * 50)
    
    response = hub.query(
        source_skill="test",
        target_domain="OrganicChem",
        query_type="OC.adjacent_groups",
        params={"smiles": smiles, "target_atom": 0, "radius": 2}
    )
    
    print(f"成功: {response.success}")
    print(f"数据: {json.dumps(response.data, indent=2, ensure_ascii=False)[:500]}...")
    
    return response


def test_sei_lif_analysis(hub: SkillHub, molecule_key: str):
    """测试 SEI LiF 倾向分析"""
    molecule = TEST_MOLECULES[molecule_key]
    
    print("\n" + "=" * 60)
    print(f"测试: SEI LiF 倾向分析")
    print(f"分子: {molecule['name']}")
    print(f"SMILES: {molecule['smiles']}")
    print(f"预期结果: {molecule['expected_lif_tendency']}")
    print("=" * 60)
    
    result = hub.run_sei_lif_analysis(molecule['smiles'], molecule['name'])
    
    return result


def test_full_pipeline(hub: SkillHub, molecule_key: str):
    """测试完整 Pipeline"""
    molecule = TEST_MOLECULES[molecule_key]
    
    result = hub.run_full_pipeline(molecule['smiles'], molecule['name'])
    
    # 保存结果
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"skill_hub_{molecule_key.lower()}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result.to_markdown())
    
    print(f"\n结果已保存到: {output_file}")
    
    return result


def compare_molecules(hub: SkillHub):
    """对比多个分子的 LiF 倾向"""
    print("\n" + "=" * 70)
    print("对比分析: 多分子 LiF 倾向")
    print("=" * 70)
    
    results = {}
    
    for key in ["FEC", "EC", "DFEC"]:
        molecule = TEST_MOLECULES[key]
        print(f"\n分析 {key}...")
        
        result = hub.run_sei_lif_analysis(molecule['smiles'], molecule['name'])
        results[key] = {
            "molecule": molecule,
            "analysis": result
        }
    
    # 输出对比表
    print("\n" + "=" * 70)
    print("对比结果")
    print("=" * 70)
    print(f"{'分子':<15} {'SMILES':<25} {'预期':<10} {'查询数':<8}")
    print("-" * 70)
    
    for key, data in results.items():
        mol = data["molecule"]
        query_count = len(data["analysis"]["queries"])
        print(f"{key:<15} {mol['smiles']:<25} {mol['expected_lif_tendency']:<10} {query_count:<8}")
    
    return results


# ============================================================================
# 主程序
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("  Skill Hub 测试脚本")
    print("  测试跨域查询功能")
    print("=" * 70)
    
    # 初始化
    print("\n[初始化] 创建 SkillHub...")
    try:
        hub = create_hub()
        print("    ✓ 初始化成功")
    except Exception as e:
        print(f"    ✗ 初始化失败: {e}")
        return
    
    # 测试 1: 单个跨域查询
    print("\n" + "=" * 70)
    print("测试 1: 单个跨域查询")
    print("=" * 70)
    
    test_cross_domain_query(hub, TEST_MOLECULES["FEC"]["smiles"])
    
    # 测试 2: SEI LiF 分析（FEC）
    print("\n" + "=" * 70)
    print("测试 2: SEI LiF 分析 (FEC)")
    print("=" * 70)
    
    fec_result = test_sei_lif_analysis(hub, "FEC")
    
    # 输出分析结果
    print("\n--- 分析结果 ---")
    print(json.dumps(fec_result["analysis"], indent=2, ensure_ascii=False)[:2000])
    
    # 测试 3: 完整 Pipeline
    print("\n" + "=" * 70)
    print("测试 3: 完整 Pipeline (FEC)")
    print("=" * 70)
    
    pipeline_result = test_full_pipeline(hub, "FEC")
    
    # 测试 4: 多分子对比（可选）
    user_input = input("\n是否运行多分子对比测试？[y/N]: ").strip().lower()
    if user_input == 'y':
        compare_molecules(hub)
    
    print("\n" + "=" * 70)
    print("所有测试完成")
    print("=" * 70)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Molecule Parser — SMILES 硬解析模块

使用 RDKit 对 SMILES 进行精确解析，生成结构化的分子数据。
所有下游技能都使用这个模块的输出，确保分子识别的一致性。

核心功能：
1. SMILES 验证与规范化
2. 原子信息提取（元素、杂化、电荷、孤对电子等）
3. 键信息提取（类型、极性）
4. 环信息（大小、芳香性、杂原子）
5. 官能团识别
6. 邻近原子/基团分析

使用方法：
    from molecule_parser import MoleculeParser, parse_smiles
    
    # 快捷方式
    mol_data = parse_smiles("FC1COC(=O)O1")
    
    # 完整使用
    parser = MoleculeParser()
    mol_data = parser.parse("FC1COC(=O)O1")
    print(mol_data.to_dict())

作者：chemagent
日期：2025-12-25
"""

import json
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
from rdkit.Chem import Draw
from rdkit.Chem.rdchem import HybridizationType, BondType


# ============================================================================
# 数据结构
# ============================================================================

class Hybridization(Enum):
    """杂化类型"""
    SP = "sp"
    SP2 = "sp2"
    SP3 = "sp3"
    SP3D = "sp3d"
    SP3D2 = "sp3d2"
    OTHER = "other"
    
    @classmethod
    def from_rdkit(cls, hyb: HybridizationType) -> "Hybridization":
        mapping = {
            HybridizationType.SP: cls.SP,
            HybridizationType.SP2: cls.SP2,
            HybridizationType.SP3: cls.SP3,
            HybridizationType.SP3D: cls.SP3D,
            HybridizationType.SP3D2: cls.SP3D2,
        }
        return mapping.get(hyb, cls.OTHER)


@dataclass
class AtomInfo:
    """原子信息"""
    index: int                      # 原子索引
    symbol: str                     # 元素符号
    atomic_num: int                 # 原子序数
    hybridization: str              # 杂化类型
    formal_charge: int              # 形式电荷
    num_h: int                      # 氢原子数
    num_lone_pairs: int             # 孤对电子数（估算）
    is_aromatic: bool               # 是否芳香
    in_ring: bool                   # 是否在环内
    ring_sizes: List[int]           # 所在环的大小
    neighbors: List[int]            # 相邻原子索引
    degree: int                     # 连接度
    is_heteroatom: bool             # 是否杂原子
    electronegativity: float        # 电负性（近似值）
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class BondInfo:
    """键信息"""
    index: int                      # 键索引
    atom1_idx: int                  # 原子1索引
    atom2_idx: int                  # 原子2索引
    bond_type: str                  # 键类型
    is_aromatic: bool               # 是否芳香键
    is_conjugated: bool             # 是否共轭
    in_ring: bool                   # 是否在环内
    bond_order: float               # 键级
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class RingInfo:
    """环信息"""
    ring_id: int                    # 环ID
    size: int                       # 环大小
    atoms: List[int]                # 环原子索引
    is_aromatic: bool               # 是否芳香
    heteroatoms: List[str]          # 杂原子列表
    is_fused: bool                  # 是否稠合
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FunctionalGroup:
    """官能团信息"""
    fg_id: str                      # 官能团ID
    fg_type: str                    # 官能团类型
    fg_category: str                # 官能团大类
    atoms: List[int]                # 涉及的原子索引
    center_atom: int                # 中心原子
    is_ewg: Optional[bool]          # 是否吸电子基
    is_edg: Optional[bool]          # 是否推电子基
    smarts_matched: str             # 匹配的 SMARTS
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AdjacentInfo:
    """邻近原子/基团信息"""
    target_atom: int                # 目标原子
    distance: int                   # 键距离
    atom_idx: int                   # 邻近原子索引
    symbol: str                     # 元素符号
    fg_type: Optional[str]          # 所属官能团类型
    is_ewg: Optional[bool]          # 是否吸电子
    is_edg: Optional[bool]          # 是否推电子
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MoleculeData:
    """完整的分子数据"""
    # 基本信息
    smiles: str                                 # 输入 SMILES
    canonical_smiles: str                       # 规范 SMILES
    name: str                                   # 分子名称
    formula: str                                # 分子式
    molecular_weight: float                     # 分子量
    num_atoms: int                              # 原子数（不含H）
    num_heavy_atoms: int                        # 重原子数
    
    # 结构信息
    atoms: List[AtomInfo] = field(default_factory=list)
    bonds: List[BondInfo] = field(default_factory=list)
    rings: List[RingInfo] = field(default_factory=list)
    functional_groups: List[FunctionalGroup] = field(default_factory=list)
    
    # 特征标记
    has_aromatic: bool = False
    has_heteroatoms: bool = False
    num_rings: int = 0
    num_rotatable_bonds: int = 0
    
    # 解析状态
    is_valid: bool = True
    parse_error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "smiles": self.smiles,
            "canonical_smiles": self.canonical_smiles,
            "name": self.name,
            "formula": self.formula,
            "molecular_weight": round(self.molecular_weight, 2),
            "num_atoms": self.num_atoms,
            "num_heavy_atoms": self.num_heavy_atoms,
            "has_aromatic": self.has_aromatic,
            "has_heteroatoms": self.has_heteroatoms,
            "num_rings": self.num_rings,
            "num_rotatable_bonds": self.num_rotatable_bonds,
            "atoms": [a.to_dict() for a in self.atoms],
            "bonds": [b.to_dict() for b in self.bonds],
            "rings": [r.to_dict() for r in self.rings],
            "functional_groups": [fg.to_dict() for fg in self.functional_groups],
            "is_valid": self.is_valid,
            "parse_error": self.parse_error,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为 JSON"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def to_yaml_str(self) -> str:
        """生成 YAML 格式的摘要（供 LLM 使用）"""
        lines = [
            "molecule_parsed:",
            f"  smiles: \"{self.smiles}\"",
            f"  canonical_smiles: \"{self.canonical_smiles}\"",
            f"  name: \"{self.name}\"",
            f"  formula: \"{self.formula}\"",
            f"  molecular_weight: {round(self.molecular_weight, 2)}",
            f"  num_atoms: {self.num_atoms}",
            f"  num_rings: {self.num_rings}",
            f"  has_aromatic: {str(self.has_aromatic).lower()}",
            "",
            "  atoms:",
        ]
        
        for atom in self.atoms:
            lines.append(f"    - idx: {atom.index}, symbol: \"{atom.symbol}\", "
                        f"hybridization: \"{atom.hybridization}\", "
                        f"charge: {atom.formal_charge}, "
                        f"lone_pairs: {atom.num_lone_pairs}, "
                        f"in_ring: {str(atom.in_ring).lower()}, "
                        f"neighbors: {atom.neighbors}")
        
        if self.rings:
            lines.append("")
            lines.append("  rings:")
            for ring in self.rings:
                lines.append(f"    - id: {ring.ring_id}, size: {ring.size}, "
                            f"atoms: {ring.atoms}, "
                            f"aromatic: {str(ring.is_aromatic).lower()}, "
                            f"heteroatoms: {ring.heteroatoms}")
        
        if self.functional_groups:
            lines.append("")
            lines.append("  functional_groups:")
            for fg in self.functional_groups:
                lines.append(f"    - id: \"{fg.fg_id}\", type: \"{fg.fg_type}\", "
                            f"category: \"{fg.fg_category}\", "
                            f"atoms: {fg.atoms}, center: {fg.center_atom}, "
                            f"ewg: {str(fg.is_ewg).lower() if fg.is_ewg is not None else 'null'}")
        
        return "\n".join(lines)
    
    def get_atom(self, idx: int) -> Optional[AtomInfo]:
        """获取指定索引的原子"""
        for atom in self.atoms:
            if atom.index == idx:
                return atom
        return None
    
    def get_adjacent_atoms(self, target_idx: int, radius: int = 2) -> List[AdjacentInfo]:
        """获取指定原子的邻近原子"""
        result = []
        visited = {target_idx}
        current_level = [target_idx]
        
        for distance in range(1, radius + 1):
            next_level = []
            for atom_idx in current_level:
                atom = self.get_atom(atom_idx)
                if atom:
                    for neighbor_idx in atom.neighbors:
                        if neighbor_idx not in visited:
                            visited.add(neighbor_idx)
                            next_level.append(neighbor_idx)
                            
                            neighbor = self.get_atom(neighbor_idx)
                            if neighbor:
                                # 查找该原子所属的官能团
                                fg_type = None
                                is_ewg = None
                                is_edg = None
                                for fg in self.functional_groups:
                                    if neighbor_idx in fg.atoms:
                                        fg_type = fg.fg_type
                                        is_ewg = fg.is_ewg
                                        is_edg = fg.is_edg
                                        break
                                
                                result.append(AdjacentInfo(
                                    target_atom=target_idx,
                                    distance=distance,
                                    atom_idx=neighbor_idx,
                                    symbol=neighbor.symbol,
                                    fg_type=fg_type,
                                    is_ewg=is_ewg,
                                    is_edg=is_edg
                                ))
            current_level = next_level
        
        return result


# ============================================================================
# 官能团 SMARTS 定义
# ============================================================================

# 官能团定义：(名称, 类别, SMARTS, 是否EWG, 是否EDG)
FUNCTIONAL_GROUP_PATTERNS = [
    # === 羰基类 (Carbonyl) ===
    ("cyclic_carbonate", "carbonyl", "[#6]1[#8][#6](=[#8])[#8]1", True, False),
    ("carbonate", "carbonyl", "[#6]([#8])([#8])=[#8]", True, False),
    ("ester", "carbonyl", "[#6](=[#8])[#8][#6]", True, False),
    ("carboxylic_acid", "carbonyl", "[#6](=[#8])[#8H]", True, False),
    ("ketone", "carbonyl", "[#6][#6](=[#8])[#6]", True, False),
    ("aldehyde", "carbonyl", "[#6H1](=[#8])", True, False),
    ("amide", "carbonyl", "[#6](=[#8])[#7]", True, False),
    ("carbamate", "carbonyl", "[#7][#6](=[#8])[#8]", True, False),
    
    # === 卤素类 (Halogen) ===
    ("C-F", "halogen", "[#6][#9]", True, False),
    ("C-Cl", "halogen", "[#6][#17]", True, False),
    ("C-Br", "halogen", "[#6][#35]", True, False),
    ("C-I", "halogen", "[#6][#53]", False, False),
    ("CF3", "halogen", "[#6]([#9])([#9])[#9]", True, False),
    
    # === 氮类 (Nitrogen) ===
    ("primary_amine", "nitrogen", "[#7H2][#6]", False, True),
    ("secondary_amine", "nitrogen", "[#6][#7H1][#6]", False, True),
    ("tertiary_amine", "nitrogen", "[#6][#7]([#6])[#6]", False, True),
    ("nitrile", "nitrogen", "[#6]#[#7]", True, False),
    ("nitro", "nitrogen", "[#7+](=[#8])[#8-]", True, False),
    ("pyridine_N", "nitrogen", "n1ccccc1", False, False),
    
    # === 氧类 (Oxygen) ===
    ("ether", "oxygen", "[#6][#8][#6]", False, False),
    ("alcohol", "oxygen", "[#6][#8H1]", False, True),
    ("phenol", "oxygen", "c[#8H1]", False, True),
    ("epoxide", "oxygen", "[#6]1[#8][#6]1", False, False),
    
    # === 硫类 (Sulfur) ===
    ("sulfone", "sulfur", "[#16](=[#8])(=[#8])", True, False),
    ("sulfoxide", "sulfur", "[#16](=[#8])", True, False),
    ("thioether", "sulfur", "[#6][#16][#6]", False, False),
    ("sulfonamide", "sulfur", "[#16](=[#8])(=[#8])[#7]", True, False),
    
    # === 不饱和类 (Unsaturated) ===
    ("alkene", "unsaturated", "[#6]=[#6]", False, False),
    ("alkyne", "unsaturated", "[#6]#[#6]", False, False),
    ("vinyl", "unsaturated", "[#6]=[#6H2]", False, False),
]


# 电负性数据 (Pauling scale)
ELECTRONEGATIVITY = {
    "H": 2.20, "C": 2.55, "N": 3.04, "O": 3.44, "F": 3.98,
    "P": 2.19, "S": 2.58, "Cl": 3.16, "Br": 2.96, "I": 2.66,
    "Si": 1.90, "B": 2.04, "Li": 0.98, "Na": 0.93, "K": 0.82,
}


# ============================================================================
# 分子解析器
# ============================================================================

class MoleculeParser:
    """分子解析器"""
    
    def __init__(self):
        self._fg_patterns = self._compile_fg_patterns()
    
    def _compile_fg_patterns(self) -> List[Tuple[str, str, Any, Optional[bool], Optional[bool]]]:
        """编译官能团 SMARTS 模式"""
        compiled = []
        for name, category, smarts, is_ewg, is_edg in FUNCTIONAL_GROUP_PATTERNS:
            mol = Chem.MolFromSmarts(smarts)
            if mol:
                compiled.append((name, category, mol, is_ewg, is_edg, smarts))
        return compiled
    
    def parse(self, smiles: str, name: str = "") -> MoleculeData:
        """解析 SMILES
        
        Args:
            smiles: SMILES 字符串
            name: 分子名称（可选）
            
        Returns:
            MoleculeData: 解析后的分子数据
        """
        # 创建空的分子数据
        mol_data = MoleculeData(
            smiles=smiles,
            canonical_smiles="",
            name=name,
            formula="",
            molecular_weight=0.0,
            num_atoms=0,
            num_heavy_atoms=0,
        )
        
        # 解析 SMILES
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            mol_data.is_valid = False
            mol_data.parse_error = f"Invalid SMILES: {smiles}"
            return mol_data
        
        # 添加氢原子信息（不实际添加）
        mol = Chem.AddHs(mol)
        
        try:
            # 基本信息
            mol_data.canonical_smiles = Chem.MolToSmiles(Chem.RemoveHs(mol))
            mol_data.formula = rdMolDescriptors.CalcMolFormula(mol)
            mol_data.molecular_weight = Descriptors.MolWt(mol)
            mol_data.num_atoms = mol.GetNumAtoms()
            mol_data.num_heavy_atoms = mol.GetNumHeavyAtoms()
            
            # 解析原子
            mol_data.atoms = self._parse_atoms(mol)
            
            # 解析键（使用不含 H 的分子）
            mol_no_h = Chem.RemoveHs(mol)
            mol_data.bonds = self._parse_bonds(mol_no_h)
            
            # 解析环
            mol_data.rings = self._parse_rings(mol_no_h)
            mol_data.num_rings = len(mol_data.rings)
            
            # 识别官能团
            mol_data.functional_groups = self._identify_functional_groups(mol_no_h)
            
            # 特征标记
            mol_data.has_aromatic = any(a.is_aromatic for a in mol_data.atoms)
            mol_data.has_heteroatoms = any(a.is_heteroatom for a in mol_data.atoms)
            mol_data.num_rotatable_bonds = rdMolDescriptors.CalcNumRotatableBonds(mol_no_h)
            
        except Exception as e:
            mol_data.is_valid = False
            mol_data.parse_error = str(e)
        
        return mol_data
    
    def _parse_atoms(self, mol) -> List[AtomInfo]:
        """解析原子信息"""
        atoms = []
        ring_info = mol.GetRingInfo()
        
        for atom in mol.GetAtoms():
            idx = atom.GetIdx()
            symbol = atom.GetSymbol()
            
            # 跳过显式氢原子
            if symbol == "H":
                continue
            
            # 杂化类型
            hyb = Hybridization.from_rdkit(atom.GetHybridization())
            
            # 孤对电子估算
            num_lone_pairs = self._estimate_lone_pairs(atom)
            
            # 所在环的大小
            ring_sizes = []
            for ring in ring_info.AtomRings():
                if idx in ring:
                    ring_sizes.append(len(ring))
            
            # 邻居原子（只保留非氢原子）
            neighbors = [n.GetIdx() for n in atom.GetNeighbors() if n.GetSymbol() != "H"]
            
            atoms.append(AtomInfo(
                index=idx,
                symbol=symbol,
                atomic_num=atom.GetAtomicNum(),
                hybridization=hyb.value,
                formal_charge=atom.GetFormalCharge(),
                num_h=atom.GetTotalNumHs(),
                num_lone_pairs=num_lone_pairs,
                is_aromatic=atom.GetIsAromatic(),
                in_ring=atom.IsInRing(),
                ring_sizes=ring_sizes,
                neighbors=neighbors,
                degree=len(neighbors),
                is_heteroatom=(symbol not in ["C", "H"]),
                electronegativity=ELECTRONEGATIVITY.get(symbol, 2.5)
            ))
        
        return atoms
    
    def _estimate_lone_pairs(self, atom) -> int:
        """估算孤对电子数"""
        symbol = atom.GetSymbol()
        formal_charge = atom.GetFormalCharge()
        total_valence = atom.GetTotalValence()
        
        # 常见元素的孤对电子估算
        base_lone_pairs = {
            "N": 1, "O": 2, "S": 2, "F": 3, "Cl": 3, "Br": 3, "I": 3,
            "P": 1, "Se": 2,
        }
        
        if symbol in base_lone_pairs:
            lp = base_lone_pairs[symbol]
            # 根据电荷和价态调整
            if formal_charge > 0:
                lp -= formal_charge
            elif formal_charge < 0:
                lp += abs(formal_charge)
            return max(0, lp)
        
        return 0
    
    def _parse_bonds(self, mol) -> List[BondInfo]:
        """解析键信息"""
        bonds = []
        
        for bond in mol.GetBonds():
            bond_type = bond.GetBondType()
            bond_type_str = {
                BondType.SINGLE: "single",
                BondType.DOUBLE: "double",
                BondType.TRIPLE: "triple",
                BondType.AROMATIC: "aromatic",
            }.get(bond_type, "other")
            
            bond_order = {
                BondType.SINGLE: 1.0,
                BondType.DOUBLE: 2.0,
                BondType.TRIPLE: 3.0,
                BondType.AROMATIC: 1.5,
            }.get(bond_type, 1.0)
            
            bonds.append(BondInfo(
                index=bond.GetIdx(),
                atom1_idx=bond.GetBeginAtomIdx(),
                atom2_idx=bond.GetEndAtomIdx(),
                bond_type=bond_type_str,
                is_aromatic=bond.GetIsAromatic(),
                is_conjugated=bond.GetIsConjugated(),
                in_ring=bond.IsInRing(),
                bond_order=bond_order
            ))
        
        return bonds
    
    def _parse_rings(self, mol) -> List[RingInfo]:
        """解析环信息"""
        rings = []
        ring_info = mol.GetRingInfo()
        atom_rings = ring_info.AtomRings()
        
        # 检测稠合环
        atom_ring_count = {}
        for ring in atom_rings:
            for atom_idx in ring:
                atom_ring_count[atom_idx] = atom_ring_count.get(atom_idx, 0) + 1
        
        for i, ring_atoms in enumerate(atom_rings):
            ring_atoms_list = list(ring_atoms)
            
            # 检查芳香性
            is_aromatic = all(mol.GetAtomWithIdx(idx).GetIsAromatic() for idx in ring_atoms)
            
            # 找出杂原子
            heteroatoms = []
            for idx in ring_atoms:
                symbol = mol.GetAtomWithIdx(idx).GetSymbol()
                if symbol not in ["C", "H"]:
                    heteroatoms.append(symbol)
            
            # 检查是否稠合
            is_fused = any(atom_ring_count.get(idx, 0) > 1 for idx in ring_atoms)
            
            rings.append(RingInfo(
                ring_id=i,
                size=len(ring_atoms_list),
                atoms=ring_atoms_list,
                is_aromatic=is_aromatic,
                heteroatoms=heteroatoms,
                is_fused=is_fused
            ))
        
        return rings
    
    def _identify_functional_groups(self, mol) -> List[FunctionalGroup]:
        """识别官能团"""
        fgs = []
        fg_counter = {}
        
        for name, category, pattern, is_ewg, is_edg, smarts in self._fg_patterns:
            matches = mol.GetSubstructMatches(pattern)
            for match in matches:
                # 生成唯一ID
                if name not in fg_counter:
                    fg_counter[name] = 0
                fg_counter[name] += 1
                fg_id = f"{name}_{fg_counter[name]}"
                
                # 确定中心原子（通常是第一个匹配的原子）
                center_atom = match[0] if match else -1
                
                fgs.append(FunctionalGroup(
                    fg_id=fg_id,
                    fg_type=name,
                    fg_category=category,
                    atoms=list(match),
                    center_atom=center_atom,
                    is_ewg=is_ewg if is_ewg else None,
                    is_edg=is_edg if is_edg else None,
                    smarts_matched=smarts
                ))
        
        return fgs
    
    def get_adjacent_groups(self, mol_data: MoleculeData, target_atom: int, radius: int = 2) -> List[Dict]:
        """获取指定原子周围的官能团
        
        这是给 SkillHub 跨域查询使用的便捷方法
        """
        adjacent = mol_data.get_adjacent_atoms(target_atom, radius)
        return [a.to_dict() for a in adjacent]


# ============================================================================
# 便捷函数
# ============================================================================

_default_parser = None

def get_parser() -> MoleculeParser:
    """获取默认解析器（单例）"""
    global _default_parser
    if _default_parser is None:
        _default_parser = MoleculeParser()
    return _default_parser


def parse_smiles(smiles: str, name: str = "") -> MoleculeData:
    """解析 SMILES 的便捷函数
    
    Args:
        smiles: SMILES 字符串
        name: 分子名称（可选）
        
    Returns:
        MoleculeData: 解析后的分子数据
    """
    return get_parser().parse(smiles, name)


def validate_smiles(smiles: str) -> Tuple[bool, str]:
    """验证 SMILES 是否有效
    
    Returns:
        (is_valid, canonical_smiles or error_message)
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False, f"Invalid SMILES: {smiles}"
    return True, Chem.MolToSmiles(mol)


def get_adjacent_groups(smiles: str, target_atom: int, radius: int = 2) -> List[Dict]:
    """获取邻近官能团的便捷函数"""
    mol_data = parse_smiles(smiles)
    if not mol_data.is_valid:
        return []
    return get_parser().get_adjacent_groups(mol_data, target_atom, radius)


# ============================================================================
# 命令行入口
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # 测试分子
    test_molecules = [
        ("FC1COC(=O)O1", "FEC (氟代碳酸乙烯酯)"),
        ("C1COC(=O)O1", "EC (碳酸乙烯酯)"),
        ("FC(F)(F)COCC(F)(F)F", "BTFE"),
        ("COC(=O)OC", "DMC"),
        ("OC(=O)c1ccccc1O", "水杨酸"),
    ]
    
    if len(sys.argv) > 1:
        # 命令行参数
        smiles = sys.argv[1]
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        test_molecules = [(smiles, name)]
    
    parser = MoleculeParser()
    
    for smiles, name in test_molecules:
        print("\n" + "=" * 60)
        print(f"分子: {name}")
        print(f"SMILES: {smiles}")
        print("=" * 60)
        
        mol_data = parser.parse(smiles, name)
        
        if mol_data.is_valid:
            print(mol_data.to_yaml_str())
            
            # 显示邻近基团分析
            if mol_data.atoms:
                print("\n邻近基团分析 (目标: 原子 0, 半径: 2):")
                adjacent = mol_data.get_adjacent_atoms(0, 2)
                for adj in adjacent:
                    print(f"  - 距离 {adj.distance}: {adj.symbol} (idx={adj.atom_idx}), "
                          f"fg={adj.fg_type}, ewg={adj.is_ewg}")
        else:
            print(f"解析错误: {mol_data.parse_error}")


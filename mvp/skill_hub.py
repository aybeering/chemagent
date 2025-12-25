#!/usr/bin/env python3
"""
Skill Hub — 技能中枢实现

核心功能：
1. 统一管理所有技能域的调用
2. 支持跨域查询（Cross-Domain Query）
3. 完整的 Pipeline 调度

架构：
                    ┌─────────────────────┐
                    │      SkillHub       │
                    │   (统一调度中心)     │
                    └────────┬────────────┘
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   OrganicChem ◄────────► PhysChem ◄────────► EleChem

使用方法：
    from skill_hub import SkillHub
    
    hub = SkillHub(client)
    result = hub.run_full_pipeline("FC1COC(=O)O1", "FEC")

作者：chemagent
日期：2025-12-25
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv
from openai import OpenAI

# 导入分子解析器
from molecule_parser import MoleculeParser, MoleculeData, parse_smiles, get_parser


# ============================================================================
# 配置
# ============================================================================

DEEPSEEK_API_BASE = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

SKILL_BASE = Path(__file__).parent.parent / "skill"


# ============================================================================
# 数据结构
# ============================================================================

class Domain(Enum):
    """技能域枚举"""
    ORGANIC_CHEM = "OrganicChem"
    PHYS_CHEM = "PhysChem"
    ELE_CHEM = "EleChem"


@dataclass
class QueryRequest:
    """跨域查询请求"""
    source_skill: str           # 发起查询的技能
    target_domain: Domain       # 目标域
    query_type: str             # 查询类型
    params: Dict[str, Any]      # 查询参数
    
    def to_dict(self) -> Dict:
        return {
            "source_skill": self.source_skill,
            "target_domain": self.target_domain.value,
            "query_type": self.query_type,
            "params": self.params
        }


@dataclass
class QueryResponse:
    """跨域查询响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        result = {"success": self.success}
        if self.data:
            result["data"] = self.data
        if self.error:
            result["error"] = self.error
        return result


@dataclass
class PipelineResult:
    """Pipeline 执行结果"""
    molecule: Dict[str, str]
    molecule_parsed: Optional[MoleculeData] = None  # 硬解析后的分子数据
    organic_chem: Optional[str] = None
    phys_chem: Optional[str] = None
    ele_chem: Optional[str] = None
    cross_domain_queries: List[Dict] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        sections = [
            f"# Skill Hub 分析报告",
            f"\n## 分子信息",
            f"- 名称: {self.molecule.get('name', 'N/A')}",
            f"- SMILES: {self.molecule.get('smiles', 'N/A')}",
        ]
        
        # 添加硬解析后的分子结构信息
        if self.molecule_parsed and self.molecule_parsed.is_valid:
            mp = self.molecule_parsed
            sections.append(f"\n## 分子结构（RDKit 硬解析）")
            sections.append(f"```yaml\n{mp.to_yaml_str()}\n```")
        
        if self.organic_chem:
            sections.append(f"\n## OrganicChem 分析\n{self.organic_chem}")
        
        if self.phys_chem:
            sections.append(f"\n## PhysChem 分析\n{self.phys_chem}")
        
        if self.ele_chem:
            sections.append(f"\n## EleChem 分析\n{self.ele_chem}")
        
        if self.cross_domain_queries:
            sections.append("\n## 跨域查询记录")
            for i, query in enumerate(self.cross_domain_queries, 1):
                sections.append(f"\n### 查询 {i}")
                sections.append(f"```yaml\n{json.dumps(query, indent=2, ensure_ascii=False)}\n```")
        
        return "\n".join(sections)


# ============================================================================
# 技能加载器
# ============================================================================

class SkillLoader:
    """技能文件加载器"""
    
    def __init__(self, skill_base: Path = SKILL_BASE):
        self.skill_base = skill_base
        self._cache: Dict[str, str] = {}
    
    def load_domain(self, domain: Domain) -> str:
        """加载指定域的所有技能"""
        cache_key = domain.value
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        skill_dir = self.skill_base / domain.value
        if not skill_dir.exists():
            return ""
        
        skills_content = []
        
        # 加载主目录下的接口文件
        for md_file in sorted(skill_dir.glob("*.md")):
            if (md_file.name.startswith("00_") or 
                md_file.name.endswith("_Router.md") or 
                md_file.name.endswith("_Schema.md") or
                md_file.name.endswith("_Integration_Guide.md")):
                content = md_file.read_text(encoding="utf-8")
                skills_content.append(f"--- {md_file.name} ---\n{content}")
        
        # 加载子目录下的 skill 卡片
        for subdir in sorted(skill_dir.iterdir()):
            if subdir.is_dir() and subdir.name.endswith("_skills"):
                for md_file in sorted(subdir.glob("*.md")):
                    content = md_file.read_text(encoding="utf-8")
                    skills_content.append(f"--- {subdir.name}/{md_file.name} ---\n{content}")
        
        result = "\n\n".join(skills_content)
        self._cache[cache_key] = result
        return result
    
    def load_hub_files(self) -> str:
        """加载 Skill Hub 相关文件"""
        hub_files = ["Skill_Hub.md", "Query_Catalog.md"]
        content = []
        for filename in hub_files:
            filepath = self.skill_base / filename
            if filepath.exists():
                content.append(f"--- {filename} ---\n{filepath.read_text(encoding='utf-8')}")
        return "\n\n".join(content)


# ============================================================================
# 跨域查询处理器
# ============================================================================

class CrossDomainQueryHandler:
    """跨域查询处理器"""
    
    def __init__(self, client: OpenAI, skill_loader: SkillLoader):
        self.client = client
        self.skill_loader = skill_loader
        self.query_log: List[Dict] = []
        self.mol_parser = MoleculeParser()  # 使用硬解析器
        self._mol_cache: Dict[str, MoleculeData] = {}
    
    def _get_mol_data(self, smiles: str) -> MoleculeData:
        """获取或缓存分子数据"""
        if smiles not in self._mol_cache:
            self._mol_cache[smiles] = self.mol_parser.parse(smiles)
        return self._mol_cache[smiles]
    
    def handle_query(self, request: QueryRequest) -> QueryResponse:
        """处理跨域查询"""
        self.query_log.append({
            "request": request.to_dict(),
            "response": None
        })
        
        # 根据目标域选择处理方法
        handlers = {
            Domain.ORGANIC_CHEM: self._handle_organic_chem_query,
            Domain.PHYS_CHEM: self._handle_phys_chem_query,
            Domain.ELE_CHEM: self._handle_ele_chem_query,
        }
        
        handler = handlers.get(request.target_domain)
        if not handler:
            response = QueryResponse(success=False, error=f"Unknown domain: {request.target_domain}")
        else:
            response = handler(request)
        
        self.query_log[-1]["response"] = response.to_dict()
        return response
    
    def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """调用 LLM"""
        try:
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.2,
                max_tokens=1500,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[LLM 调用失败: {e}]"
    
    def _handle_organic_chem_query(self, request: QueryRequest) -> QueryResponse:
        """处理 OrganicChem 域查询"""
        skills = self.skill_loader.load_domain(Domain.ORGANIC_CHEM)
        
        query_handlers = {
            "OC.adjacent_groups": self._query_adjacent_groups,
            "OC.functional_group_at": self._query_functional_group_at,
            "OC.conjugation_check": self._query_conjugation_check,
            "OC.ring_membership": self._query_ring_membership,
        }
        
        handler = query_handlers.get(request.query_type)
        if handler:
            return handler(request, skills)
        
        # 通用查询处理
        return self._generic_query(request, skills, "OrganicChem")
    
    def _handle_phys_chem_query(self, request: QueryRequest) -> QueryResponse:
        """处理 PhysChem 域查询"""
        skills = self.skill_loader.load_domain(Domain.PHYS_CHEM)
        
        query_handlers = {
            "PC.ewg_strength": self._query_ewg_strength,
            "PC.edg_strength": self._query_edg_strength,
            "PC.local_electron_density": self._query_electron_density,
            "PC.bond_activation": self._query_bond_activation,
            "PC.homo_contributor": self._query_homo_contributor,
            "PC.lumo_contributor": self._query_lumo_contributor,
        }
        
        handler = query_handlers.get(request.query_type)
        if handler:
            return handler(request, skills)
        
        return self._generic_query(request, skills, "PhysChem")
    
    def _handle_ele_chem_query(self, request: QueryRequest) -> QueryResponse:
        """处理 EleChem 域查询"""
        skills = self.skill_loader.load_domain(Domain.ELE_CHEM)
        return self._generic_query(request, skills, "EleChem")
    
    # =========== 具体查询实现 ===========
    
    def _query_adjacent_groups(self, request: QueryRequest, skills: str) -> QueryResponse:
        """查询邻近官能团（使用 RDKit 硬解析）"""
        smiles = request.params.get("smiles", "")
        target_atom = request.params.get("target_atom", 0)
        radius = request.params.get("radius", 2)
        
        # 使用硬解析而不是让 LLM 解析
        mol_data = self._get_mol_data(smiles)
        
        if not mol_data.is_valid:
            return QueryResponse(success=False, error=mol_data.parse_error)
        
        # 直接从硬解析结果获取邻近基团
        adjacent = mol_data.get_adjacent_atoms(target_atom, radius)
        
        adjacent_groups = []
        for adj in adjacent:
            adjacent_groups.append({
                "distance": adj.distance,
                "atom_index": adj.atom_idx,
                "element": adj.symbol,
                "fg_type": adj.fg_type,
                "is_ewg": adj.is_ewg,
                "is_edg": adj.is_edg
            })
        
        return QueryResponse(success=True, data={"adjacent_groups": adjacent_groups})
    
    def _query_ewg_strength(self, request: QueryRequest, skills: str) -> QueryResponse:
        """查询吸电子基强度（使用预解析分子数据）"""
        smiles = request.params.get("smiles", "")
        substituent_atom = request.params.get("substituent_atom")
        target_atom = request.params.get("target_atom")
        
        # 获取硬解析数据
        mol_data = self._get_mol_data(smiles)
        if not mol_data.is_valid:
            return QueryResponse(success=False, error=mol_data.parse_error)
        
        # 获取取代基原子信息
        sub_atom = mol_data.get_atom(substituent_atom) if substituent_atom is not None else None
        tgt_atom = mol_data.get_atom(target_atom) if target_atom is not None else None
        
        # 获取取代基所属官能团
        sub_fg = None
        for fg in mol_data.functional_groups:
            if substituent_atom in fg.atoms:
                sub_fg = fg
                break
        
        atom_context = ""
        if sub_atom:
            atom_context += f"取代基原子: {sub_atom.symbol} (idx={sub_atom.index}, hyb={sub_atom.hybridization}, charge={sub_atom.formal_charge})\n"
        if sub_fg:
            atom_context += f"所属官能团: {sub_fg.fg_type} (类别: {sub_fg.fg_category}, is_ewg={sub_fg.is_ewg})\n"
        if tgt_atom:
            atom_context += f"目标原子: {tgt_atom.symbol} (idx={tgt_atom.index}, hyb={tgt_atom.hybridization})\n"
        
        system_prompt = f"""你是一位物理有机化学专家，专注于电子效应分析。
你需要评估取代基的吸电子效应强度。

参考技能库（ELEC 模块）：
{skills[:10000]}

请以 JSON 格式返回结果：
{{
    "ewg_strength": {{
        "substituent": "<取代基描述>",
        "I_effect": {{"sign": "-I", "strength": "very_strong|strong|medium|weak"}},
        "M_effect": {{"sign": "-M|none", "strength": "strong|medium|weak|none"}},
        "net_classification": "strong_ewg|moderate_ewg|weak_ewg",
        "effect_on_target": {{
            "direction": "electron_withdrawing|electron_donating",
            "magnitude": "significant|moderate|weak"
        }}
    }}
}}"""

        user_message = f"""评估以下分子中取代基的吸电子效应：

# 分子信息 (RDKit 预解析)
SMILES: {smiles}
分子式: {mol_data.formula}

# 原子信息
{atom_context}

请分析该取代基的诱导效应(-I)和共振效应(-M)，以及对目标原子的影响。"""

        result = self._call_llm(system_prompt, user_message)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                data = json.loads(json_match.group())
                return QueryResponse(success=True, data=data)
        except json.JSONDecodeError:
            pass
        
        return QueryResponse(success=True, data={"raw_response": result})
    
    def _query_bond_activation(self, request: QueryRequest, skills: str) -> QueryResponse:
        """查询键活化程度（使用预解析分子数据）"""
        smiles = request.params.get("smiles", "")
        bond_atoms = request.params.get("bond_atoms", [])
        activation_type = request.params.get("activation_type", "reduction")
        
        # 获取硬解析数据
        mol_data = self._get_mol_data(smiles)
        if not mol_data.is_valid:
            return QueryResponse(success=False, error=mol_data.parse_error)
        
        # 获取键两端原子的邻近基团信息
        adjacent_info = ""
        for atom_idx in bond_atoms:
            adjacent = mol_data.get_adjacent_atoms(atom_idx, 2)
            adjacent_info += f"原子 {atom_idx} 邻近基团:\n"
            for adj in adjacent:
                adjacent_info += f"  - 距离 {adj.distance}: {adj.symbol} (idx={adj.atom_idx}), fg={adj.fg_type}, ewg={adj.is_ewg}\n"
        
        system_prompt = f"""你是一位物理有机化学专家。
你需要评估化学键的活化程度。

参考技能库：
{skills[:8000]}

请以 JSON 格式返回结果：
{{
    "bond_activation": {{
        "activation_level": "high|medium|low",
        "sigma_star_energy": "lowered|normal|raised",
        "activating_factors": [
            {{"factor": "<因素>", "effect": "<效应>"}}
        ],
        "susceptible_to": ["reduction", "radical_attack", ...]
    }}
}}"""

        user_message = f"""评估以下分子中键的活化程度：

# 分子信息 (RDKit 预解析)
SMILES: {smiles}
分子式: {mol_data.formula}

# 目标键
键原子: {bond_atoms}
活化类型: {activation_type}

# 邻近基团信息
{adjacent_info}

请基于以上预解析信息，分析该键在 {activation_type} 条件下的活化程度，以及影响因素。"""

        result = self._call_llm(system_prompt, user_message)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                data = json.loads(json_match.group())
                return QueryResponse(success=True, data=data)
        except json.JSONDecodeError:
            pass
        
        return QueryResponse(success=True, data={"raw_response": result})
    
    def _query_functional_group_at(self, request: QueryRequest, skills: str) -> QueryResponse:
        """查询指定位置的官能团"""
        return self._generic_query(request, skills, "OrganicChem")
    
    def _query_conjugation_check(self, request: QueryRequest, skills: str) -> QueryResponse:
        """检查共轭关系"""
        return self._generic_query(request, skills, "OrganicChem")
    
    def _query_ring_membership(self, request: QueryRequest, skills: str) -> QueryResponse:
        """查询环成员关系"""
        return self._generic_query(request, skills, "OrganicChem")
    
    def _query_edg_strength(self, request: QueryRequest, skills: str) -> QueryResponse:
        """查询推电子基强度"""
        return self._generic_query(request, skills, "PhysChem")
    
    def _query_electron_density(self, request: QueryRequest, skills: str) -> QueryResponse:
        """查询局部电子密度"""
        return self._generic_query(request, skills, "PhysChem")
    
    def _query_homo_contributor(self, request: QueryRequest, skills: str) -> QueryResponse:
        """查询 HOMO 贡献者"""
        return self._generic_query(request, skills, "PhysChem")
    
    def _query_lumo_contributor(self, request: QueryRequest, skills: str) -> QueryResponse:
        """查询 LUMO 贡献者"""
        return self._generic_query(request, skills, "PhysChem")
    
    def _generic_query(self, request: QueryRequest, skills: str, domain_name: str) -> QueryResponse:
        """通用查询处理"""
        system_prompt = f"""你是一位 {domain_name} 领域专家。
你需要回答关于分子结构和性质的查询。

参考技能库：
{skills[:6000]}

请以 JSON 格式返回结果。"""

        user_message = f"""查询类型: {request.query_type}
查询参数: {json.dumps(request.params, ensure_ascii=False)}

请根据技能库的知识回答这个查询。"""

        result = self._call_llm(system_prompt, user_message)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', result)
            if json_match:
                data = json.loads(json_match.group())
                return QueryResponse(success=True, data=data)
        except json.JSONDecodeError:
            pass
        
        return QueryResponse(success=True, data={"raw_response": result})


# ============================================================================
# Skill Hub 主类
# ============================================================================

class SkillHub:
    """技能中枢 - 统一调度所有技能的调用与跨域协调"""
    
    def __init__(self, client: OpenAI, skill_base: Path = SKILL_BASE):
        self.client = client
        self.skill_loader = SkillLoader(skill_base)
        self.query_handler = CrossDomainQueryHandler(client, self.skill_loader)
        self.mol_parser = MoleculeParser()  # 分子硬解析器
        self._mol_cache: Dict[str, MoleculeData] = {}  # 解析缓存
    
    def parse_molecule(self, smiles: str, name: str = "") -> MoleculeData:
        """解析分子（使用 RDKit 硬解析）
        
        这是所有分析的第一步，确保分子结构被准确识别。
        
        Args:
            smiles: SMILES 字符串
            name: 分子名称
            
        Returns:
            MoleculeData: 解析后的分子数据
        """
        # 使用缓存
        cache_key = smiles
        if cache_key in self._mol_cache:
            mol_data = self._mol_cache[cache_key]
            if name and not mol_data.name:
                mol_data.name = name
            return mol_data
        
        mol_data = self.mol_parser.parse(smiles, name)
        self._mol_cache[cache_key] = mol_data
        return mol_data
    
    def get_molecule_context(self, mol_data: MoleculeData) -> str:
        """生成分子上下文信息（供 LLM 使用）
        
        这个方法将硬解析结果转换为 LLM 友好的格式，
        确保 LLM 不需要自己解析 SMILES。
        """
        if not mol_data.is_valid:
            return f"分子解析失败: {mol_data.parse_error}"
        
        return mol_data.to_yaml_str()
    
    def query(self, 
              source_skill: str, 
              target_domain: str, 
              query_type: str, 
              params: Dict[str, Any]) -> QueryResponse:
        """发起跨域查询
        
        Args:
            source_skill: 发起查询的技能 ID
            target_domain: 目标域 ("OrganicChem" | "PhysChem" | "EleChem")
            query_type: 查询类型 (如 "OC.adjacent_groups")
            params: 查询参数
            
        Returns:
            QueryResponse: 查询结果
        """
        domain = Domain(target_domain)
        request = QueryRequest(
            source_skill=source_skill,
            target_domain=domain,
            query_type=query_type,
            params=params
        )
        return self.query_handler.handle_query(request)
    
    def run_organic_chem(self, smiles: str, name: str = "", mol_data: Optional[MoleculeData] = None) -> str:
        """运行 OrganicChem 分析
        
        Args:
            smiles: SMILES 字符串
            name: 分子名称
            mol_data: 预解析的分子数据（可选，如果不提供则自动解析）
        """
        # 如果没有提供预解析数据，则解析
        if mol_data is None:
            mol_data = self.parse_molecule(smiles, name)
        
        # 获取分子上下文
        mol_context = self.get_molecule_context(mol_data)
        
        skills = self.skill_loader.load_domain(Domain.ORGANIC_CHEM)
        
        system_prompt = f"""你是一位有机化学结构解析专家。

你拥有以下 OrganicChem 技能库：
{skills}

重要说明：
- 分子结构已经通过 RDKit 预解析，你不需要自己解析 SMILES
- 请直接使用下面提供的原子索引、官能团、环信息等
- 严格按照技能卡片中定义的框架和输出格式来分析"""

        user_message = f"""请对以下分子进行 OrganicChem 分析：

# 基本信息
SMILES: {smiles}
名称: {name or mol_data.name}

# 预解析的分子结构（RDKit）
{mol_context}

请基于以上预解析的结构信息，输出：
1. 结构解剖（骨架、官能团、杂原子、环系、共轭）
2. 反应敏感位点（亲核/亲电/消除/开环位点）
3. 官能团簇路由（推荐的 PhysChem 模块）

注意：请使用预解析中的原子索引（idx），确保一致性。
使用 YAML 格式输出关键信息。"""

        return self._call_llm(system_prompt, user_message)
    
    def run_phys_chem(self, smiles: str, name: str = "", organic_output: str = "", 
                      mol_data: Optional[MoleculeData] = None) -> str:
        """运行 PhysChem 分析
        
        Args:
            smiles: SMILES 字符串
            name: 分子名称
            organic_output: OrganicChem 上游输出
            mol_data: 预解析的分子数据
        """
        if mol_data is None:
            mol_data = self.parse_molecule(smiles, name)
        
        mol_context = self.get_molecule_context(mol_data)
        skills = self.skill_loader.load_domain(Domain.PHYS_CHEM)
        
        system_prompt = f"""你是一位物理化学专家。

你拥有以下 PhysChem 技能库：
{skills}

重要说明：
- 分子结构已经通过 RDKit 预解析，请直接使用提供的原子索引和官能团信息
- 严格按照技能卡片中定义的框架和输出格式来分析"""

        user_message = f"""请对以下分子进行 PhysChem 分析：

# 基本信息
SMILES: {smiles}
名称: {name or mol_data.name}

# 预解析的分子结构（RDKit）
{mol_context}

# OrganicChem 上游结果
{organic_output}

请输出：
1. 电子效应分析（ELEC）- 使用预解析的原子索引
2. 氧化倾向分析（HOMO）
3. 还原倾向分析（LUMO）
4. 界面位点排序

使用 YAML 格式输出关键信息。"""

        return self._call_llm(system_prompt, user_message, max_tokens=3000)
    
    def run_ele_chem(self, smiles: str, name: str = "", 
                     organic_output: str = "", phys_output: str = "",
                     mol_data: Optional[MoleculeData] = None) -> str:
        """运行 EleChem 分析（含跨域查询）
        
        Args:
            smiles: SMILES 字符串
            name: 分子名称
            organic_output: OrganicChem 上游输出
            phys_output: PhysChem 上游输出
            mol_data: 预解析的分子数据
        """
        if mol_data is None:
            mol_data = self.parse_molecule(smiles, name)
        
        mol_context = self.get_molecule_context(mol_data)
        skills = self.skill_loader.load_domain(Domain.ELE_CHEM)
        hub_files = self.skill_loader.load_hub_files()
        
        # 生成邻近基团信息（对于 C-F 键分析很重要）
        adjacent_info = ""
        for fg in mol_data.functional_groups:
            if fg.fg_type == "C-F":
                adjacent = mol_data.get_adjacent_atoms(fg.center_atom, 2)
                adjacent_info += f"\nC-F 键 (原子 {fg.atoms}) 邻近基团:\n"
                for adj in adjacent:
                    adjacent_info += f"  - 距离 {adj.distance}: {adj.symbol} (idx={adj.atom_idx}), fg={adj.fg_type}, ewg={adj.is_ewg}\n"
        
        system_prompt = f"""你是一位电化学机理专家。

你拥有以下 EleChem 技能库：
{skills}

跨域查询能力说明：
{hub_files[:3000]}

重要说明：
- 分子结构已经通过 RDKit 预解析，请直接使用提供的原子索引和官能团信息
- C-F 键的邻近基团信息已经预先计算，不需要额外查询
- 严格按照技能卡片中定义的框架和输出格式来分析"""

        user_message = f"""请对以下分子进行 EleChem 电化学机理分析：

# 基本信息
SMILES: {smiles}
名称: {name or mol_data.name}

# 预解析的分子结构（RDKit）
{mol_context}
{adjacent_info}

# OrganicChem 上游结果
{organic_output}

# PhysChem 上游结果
{phys_output}

请输出：
1. 角色假设（溶剂/添加剂/稀释剂）
2. SEI 路径分析（聚合膜/无机盐/LiF）- 使用预解析的 C-F 邻近基团信息
3. CEI 风险评估
4. 产气/聚合风险

使用 YAML 格式输出关键信息。"""

        return self._call_llm(system_prompt, user_message, max_tokens=4000)
    
    def run_full_pipeline(self, smiles: str, name: str = "") -> PipelineResult:
        """运行完整 Pipeline"""
        result = PipelineResult(molecule={"smiles": smiles, "name": name})
        
        print(f"\n{'='*60}")
        print(f"Skill Hub: 完整 Pipeline 分析")
        print(f"分子: {name} ({smiles})")
        print(f"{'='*60}")
        
        # 阶段 0: 分子硬解析（最上游）
        print("\n[0/4] 分子硬解析 (RDKit)...")
        mol_data = self.parse_molecule(smiles, name)
        result.molecule_parsed = mol_data
        
        if not mol_data.is_valid:
            print(f"    ✗ 解析失败: {mol_data.parse_error}")
            return result
        
        print(f"    ✓ 解析成功: {mol_data.formula}, {len(mol_data.atoms)} 个重原子")
        print(f"    ✓ 识别到 {len(mol_data.functional_groups)} 个官能团, {len(mol_data.rings)} 个环")
        
        # 阶段 1: OrganicChem（使用预解析数据）
        print("\n[1/4] 运行 OrganicChem 分析...")
        result.organic_chem = self.run_organic_chem(smiles, name, mol_data)
        print("    ✓ OrganicChem 完成")
        
        # 阶段 2: PhysChem（使用预解析数据）
        print("\n[2/4] 运行 PhysChem 分析...")
        result.phys_chem = self.run_phys_chem(smiles, name, result.organic_chem, mol_data)
        print("    ✓ PhysChem 完成")
        
        # 阶段 3: EleChem（使用预解析数据，含跨域查询）
        print("\n[3/4] 运行 EleChem 分析...")
        result.ele_chem = self.run_ele_chem(smiles, name, result.organic_chem, result.phys_chem, mol_data)
        
        # 处理跨域查询
        cross_queries = self._extract_cross_queries(result.ele_chem, smiles)
        for query_info in cross_queries:
            print(f"    → 执行跨域查询: {query_info['query_type']}")
            response = self.query(
                source_skill="EleChem",
                target_domain=query_info["domain"],
                query_type=query_info["query_type"],
                params={"smiles": smiles, **query_info.get("params", {})}
            )
            result.cross_domain_queries.append({
                "query": query_info,
                "response": response.to_dict()
            })
        
        print("    ✓ EleChem 完成")
        print(f"\n{'='*60}")
        print("Pipeline 执行完成")
        print(f"{'='*60}")
        
        return result
    
    def run_sei_lif_analysis(self, smiles: str, name: str = "") -> Dict:
        """专门运行 SEI LiF 倾向分析（展示跨域查询）"""
        print(f"\n{'='*60}")
        print(f"SEI LiF 倾向分析（跨域查询演示）")
        print(f"分子: {name} ({smiles})")
        print(f"{'='*60}")
        
        result = {
            "molecule": {"smiles": smiles, "name": name},
            "queries": [],
            "analysis": None
        }
        
        # Step 1: 查询邻近官能团
        print("\n[Step 1] 查询 C-F 键邻近官能团...")
        query1 = self.query(
            source_skill="SEI_04_lif_tendency_v1",
            target_domain="OrganicChem",
            query_type="OC.adjacent_groups",
            params={"smiles": smiles, "target_atom": 0, "radius": 2}
        )
        result["queries"].append({
            "step": 1,
            "description": "查询 C-F 键邻近官能团",
            "query_type": "OC.adjacent_groups",
            "response": query1.to_dict()
        })
        print(f"    ✓ 完成: {query1.success}")
        
        # Step 2: 查询吸电子效应强度
        print("\n[Step 2] 查询邻近基团的吸电子效应...")
        query2 = self.query(
            source_skill="SEI_04_lif_tendency_v1",
            target_domain="PhysChem",
            query_type="PC.ewg_strength",
            params={"smiles": smiles, "substituent_atom": 3, "target_atom": 0}
        )
        result["queries"].append({
            "step": 2,
            "description": "查询邻近基团的吸电子效应",
            "query_type": "PC.ewg_strength",
            "response": query2.to_dict()
        })
        print(f"    ✓ 完成: {query2.success}")
        
        # Step 3: 查询 C-F 键活化程度
        print("\n[Step 3] 查询 C-F 键活化程度...")
        query3 = self.query(
            source_skill="SEI_04_lif_tendency_v1",
            target_domain="PhysChem",
            query_type="PC.bond_activation",
            params={"smiles": smiles, "bond_atoms": [0, 1], "activation_type": "reduction"}
        )
        result["queries"].append({
            "step": 3,
            "description": "查询 C-F 键活化程度",
            "query_type": "PC.bond_activation",
            "response": query3.to_dict()
        })
        print(f"    ✓ 完成: {query3.success}")
        
        # 综合分析
        print("\n[Step 4] 综合分析 LiF 形成倾向...")
        analysis = self._synthesize_lif_analysis(smiles, name, result["queries"])
        result["analysis"] = analysis
        print(f"    ✓ 完成")
        
        print(f"\n{'='*60}")
        print("分析完成")
        print(f"{'='*60}")
        
        return result
    
    def _synthesize_lif_analysis(self, smiles: str, name: str, queries: List[Dict]) -> str:
        """综合 LiF 分析结果"""
        skills = self.skill_loader.load_domain(Domain.ELE_CHEM)
        
        system_prompt = f"""你是一位电化学专家，专注于 SEI 形成机理。

参考技能（SEI_04_lif_tendency）：
{skills[:5000]}

请根据跨域查询结果，综合分析 LiF 形成倾向。"""

        user_message = f"""分子: {name} ({smiles})

跨域查询结果：
{json.dumps(queries, indent=2, ensure_ascii=False)}

请综合以上信息，给出 LiF 形成倾向分析：
1. likelihood: high/medium/low/none
2. f_source: F 来源描述
3. mechanism: C-F 断裂机理
4. lif_contribution: LiF 对 SEI 的贡献
5. evidence: 支持结论的证据
6. confidence: 置信度

请以 YAML 格式输出。"""

        return self._call_llm(system_prompt, user_message)
    
    def _extract_cross_queries(self, ele_chem_output: str, smiles: str) -> List[Dict]:
        """从 EleChem 输出中提取跨域查询请求"""
        queries = []
        pattern = r'\[CROSS_QUERY:\s*(OC|PC|EC)\.(\w+)\]'
        matches = re.findall(pattern, ele_chem_output)
        
        for domain_prefix, query_name in matches:
            domain_map = {"OC": "OrganicChem", "PC": "PhysChem", "EC": "EleChem"}
            queries.append({
                "domain": domain_map.get(domain_prefix, domain_prefix),
                "query_type": f"{domain_prefix}.{query_name}",
                "params": {}
            })
        
        return queries
    
    def _call_llm(self, system_prompt: str, user_message: str, max_tokens: int = 2000) -> str:
        """调用 LLM"""
        try:
            response = self.client.chat.completions.create(
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
            return f"[LLM 调用失败: {e}]"


# ============================================================================
# 辅助函数
# ============================================================================

def load_env() -> str:
    """加载环境变量"""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        raise FileNotFoundError(f"未找到 .env 文件: {env_path}")
    
    load_dotenv(env_path)
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("DEEPSEEK_API_KEY 未设置或为默认值")
    
    return api_key


def save_result_to_file(result: dict, filename: str):
    """将结果保存到 output 文件夹"""
    import json
    from pathlib import Path

    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    filepath = output_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✓ 结果已保存到: {filepath}")
    return filepath


def create_hub() -> SkillHub:
    """创建 SkillHub 实例"""
    api_key = load_env()
    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_API_BASE)
    return SkillHub(client)


# ============================================================================
# 命令行入口
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("Skill Hub - 技能中枢")
    print("=" * 60)
    
    try:
        hub = create_hub()
        print("✓ SkillHub 初始化成功")
        
        # 默认测试分子：FEC
        smiles = "CC(=O)c1ccc(CF)c(C(F)(F)F)c1"
        name = "测试分子"
        
        if len(sys.argv) > 1:
            smiles = sys.argv[1]
            name = sys.argv[2] if len(sys.argv) > 2 else smiles
        
        # 运行 SEI LiF 分析（跨域查询演示）
        print(f"\n运行 SEI LiF 倾向分析...")
        lif_result = hub.run_sei_lif_analysis(smiles, name)

        # 保存 LiF 分析结果
        filename_lif = f"skill_hub_lif_{name.replace(' ', '_').replace('(', '').replace(')', '')}.json"
        save_result_to_file(lif_result, filename_lif)

        # 运行完整 Pipeline
        print(f"\n运行完整 Pipeline 分析...")
        pipeline_result = hub.run_full_pipeline(smiles, name)

        # 保存完整 Pipeline 结果
        filename_full = f"skill_hub_full_{name.replace(' ', '_').replace('(', '').replace(')', '')}.md"
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        filepath_full = output_dir / filename_full
        with open(filepath_full, 'w', encoding='utf-8') as f:
            f.write(pipeline_result.to_markdown())

        print(f"✓ 完整 Pipeline 结果已保存到: {filepath_full}")

        # 输出 LiF 分析结果
        print("\n" + "=" * 60)
        print("LiF 倾向分析结果")
        print("=" * 60)
        print(json.dumps(lif_result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


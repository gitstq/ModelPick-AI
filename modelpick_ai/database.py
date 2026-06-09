# -*- coding: utf-8 -*-
"""
模型数据库管理模块 / Model Database Management Module

加载和管理内置的模型数据库（JSON格式），提供模型查询、过滤和搜索功能。
Load and manage the built-in model database (JSON format), providing model
query, filtering, and search capabilities.
"""

import json
import os
from typing import Dict, List, Optional, Any


# 数据库文件路径 / Database file path
_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_DB_FILE = os.path.join(_DB_DIR, "models.json")


class ModelRecord:
    """模型记录数据类 / Model record data class

    封装单个模型的完整信息。
    Wraps the complete information of a single model.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        self._data = data

    @property
    def id(self) -> str:
        """模型唯一标识 / Unique model identifier"""
        return self._data.get("id", "")

    @property
    def name(self) -> str:
        """模型英文名称 / English model name"""
        return self._data.get("name", "")

    @property
    def name_zh(self) -> str:
        """模型中文名称 / Chinese model name"""
        return self._data.get("name_zh", "")

    @property
    def developer(self) -> str:
        """开发者英文名 / Developer name in English"""
        return self._data.get("developer", "")

    @property
    def developer_zh(self) -> str:
        """开发者中文名 / Developer name in Chinese"""
        return self._data.get("developer_zh", "")

    @property
    def param_count(self) -> str:
        """参数量字符串（如'7B'）/ Parameter count string (e.g., '7B')"""
        return self._data.get("param_count", "")

    @property
    def param_count_num(self) -> float:
        """参数量数值（如7.0）/ Parameter count number (e.g., 7.0)"""
        return self._data.get("param_count_num", 0)

    @property
    def vram_required_gb(self) -> float:
        """最低显存需求(GB) / Minimum VRAM required in GB"""
        return self._data.get("vram_required_gb", 0)

    @property
    def vram_recommended_gb(self) -> float:
        """推荐显存(GB) / Recommended VRAM in GB"""
        return self._data.get("vram_recommended_gb", 0)

    @property
    def ram_required_gb(self) -> float:
        """最低内存需求(GB) / Minimum RAM required in GB"""
        return self._data.get("ram_required_gb", 0)

    @property
    def disk_required_gb(self) -> float:
        """最低磁盘空间需求(GB) / Minimum disk space required in GB"""
        return self._data.get("disk_required_gb", 0)

    @property
    def context_length(self) -> int:
        """上下文长度 / Context length"""
        return self._data.get("context_length", 0)

    @property
    def quantization(self) -> List[str]:
        """支持的量化格式 / Supported quantization formats"""
        return self._data.get("quantization", [])

    @property
    def benchmarks(self) -> Dict[str, float]:
        """基准测试分数 / Benchmark scores"""
        return self._data.get("benchmarks", {})

    @property
    def scenarios(self) -> List[str]:
        """适用场景列表 / List of applicable scenarios"""
        return self._data.get("scenarios", [])

    @property
    def platforms(self) -> List[str]:
        """支持平台列表 / List of supported platforms"""
        return self._data.get("platforms", [])

    @property
    def ollama_command(self) -> str:
        """Ollama安装命令 / Ollama install command"""
        return self._data.get("ollama_command", "")

    @property
    def tags(self) -> List[str]:
        """标签列表 / Tag list"""
        return self._data.get("tags", [])

    @property
    def license(self) -> str:
        """开源协议 / Open source license"""
        return self._data.get("license", "")

    @property
    def description(self) -> str:
        """英文描述 / English description"""
        return self._data.get("description", "")

    @property
    def description_zh(self) -> str:
        """中文描述 / Chinese description"""
        return self._data.get("description_zh", "")

    def to_dict(self) -> Dict[str, Any]:
        """转换为原始字典 / Convert to raw dictionary"""
        return dict(self._data)

    def __repr__(self) -> str:
        return f"ModelRecord(id={self.id}, name={self.name}, params={self.param_count})"


class ModelDatabase:
    """模型数据库 / Model database

    加载和管理内置模型数据，提供查询、搜索、过滤功能。
    Load and manage built-in model data, providing query, search, and filter features.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        """初始化数据库 / Initialize database

        Args:
            db_path: 自定义数据库路径，默认使用内置路径
                     Custom database path, defaults to built-in path
        """
        self._db_path = db_path or _DB_FILE
        self._models: List[ModelRecord] = []
        self._version: str = ""
        self._load()

    def _load(self) -> None:
        """从JSON文件加载数据库 / Load database from JSON file"""
        try:
            with open(self._db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._version = data.get("version", "unknown")
            self._models = [ModelRecord(m) for m in data.get("models", [])]
        except FileNotFoundError:
            # 数据库文件不存在时使用空数据库 / Use empty database when file not found
            self._models = []
            self._version = "unknown"
        except json.JSONDecodeError:
            # JSON解析失败 / JSON parse failure
            self._models = []
            self._version = "error"

    @property
    def version(self) -> str:
        """数据库版本 / Database version"""
        return self._version

    @property
    def count(self) -> int:
        """模型总数 / Total model count"""
        return len(self._models)

    def get_all(self) -> List[ModelRecord]:
        """获取所有模型 / Get all models"""
        return list(self._models)

    def get_by_id(self, model_id: str) -> Optional[ModelRecord]:
        """根据ID获取模型 / Get model by ID

        Args:
            model_id: 模型唯一标识 / Model unique identifier

        Returns:
            匹配的模型记录，未找到返回None / Matched model record, None if not found
        """
        for model in self._models:
            if model.id == model_id:
                return model
        return None

    def search(self, keyword: str) -> List[ModelRecord]:
        """搜索模型 / Search models

        在名称、描述、开发者、标签中搜索关键词。
        Search keyword in name, description, developer, and tags.

        Args:
            keyword: 搜索关键词（不区分大小写）/ Search keyword (case-insensitive)

        Returns:
            匹配的模型列表 / List of matched models
        """
        keyword_lower = keyword.lower()
        results: List[ModelRecord] = []

        for model in self._models:
            # 在多个字段中搜索 / Search across multiple fields
            search_fields = [
                model.name,
                model.name_zh,
                model.developer,
                model.developer_zh,
                model.description,
                model.description_zh,
                model.id,
                " ".join(model.tags),
                " ".join(model.scenarios),
            ]
            search_text = " ".join(search_fields).lower()
            if keyword_lower in search_text:
                results.append(model)

        return results

    def filter_by_scenario(self, scenario: str) -> List[ModelRecord]:
        """按场景过滤模型 / Filter models by scenario

        Args:
            scenario: 场景名称（如'coding', 'chat'）/ Scenario name (e.g., 'coding', 'chat')

        Returns:
            支持该场景的模型列表 / List of models supporting the scenario
        """
        return [m for m in self._models if scenario.lower() in [s.lower() for s in m.scenarios]]

    def filter_by_max_params(self, max_params: float) -> List[ModelRecord]:
        """按最大参数量过滤 / Filter by maximum parameter count

        Args:
            max_params: 最大参数量（单位：B）/ Maximum parameter count (in billions)

        Returns:
            参数量不超过限制的模型列表 / List of models within parameter limit
        """
        return [m for m in self._models if m.param_count_num <= max_params]

    def filter_by_platform(self, platform: str) -> List[ModelRecord]:
        """按平台过滤 / Filter by platform

        Args:
            platform: 平台名称（如'huggingface', 'ollama', 'modelscope'）
                     Platform name (e.g., 'huggingface', 'ollama', 'modelscope')

        Returns:
            支持该平台的模型列表 / List of models supporting the platform
        """
        return [m for m in self._models if platform.lower() in [p.lower() for p in m.platforms]]

    def filter_by_vram(self, max_vram_gb: float) -> List[ModelRecord]:
        """按最大显存过滤 / Filter by maximum VRAM

        Args:
            max_vram_gb: 最大可用显存(GB) / Maximum available VRAM in GB

        Returns:
            显存需求在限制内的模型列表 / List of models within VRAM limit
        """
        return [m for m in self._models if m.vram_required_gb <= max_vram_gb]

    def filter_by_ram(self, max_ram_gb: float) -> List[ModelRecord]:
        """按最大内存过滤 / Filter by maximum RAM

        Args:
            max_ram_gb: 最大可用内存(GB) / Maximum available RAM in GB

        Returns:
            内存需求在限制内的模型列表 / List of models within RAM limit
        """
        return [m for m in self._models if m.ram_required_gb <= max_ram_gb]

    def filter_by_disk(self, max_disk_gb: float) -> List[ModelRecord]:
        """按最大磁盘空间过滤 / Filter by maximum disk space

        Args:
            max_disk_gb: 最大可用磁盘空间(GB) / Maximum available disk space in GB

        Returns:
            磁盘需求在限制内的模型列表 / List of models within disk limit
        """
        return [m for m in self._models if m.disk_required_gb <= max_disk_gb]

    def get_benchmark_ranking(self, benchmark: str, top_n: int = 10) -> List[ModelRecord]:
        """获取基准测试排行榜 / Get benchmark ranking

        Args:
            benchmark: 基准测试名称（如'mmlu', 'humaneval', 'c_eval'）
                      Benchmark name (e.g., 'mmlu', 'humaneval', 'c_eval')
            top_n: 返回前N名 / Return top N

        Returns:
            按分数降序排列的模型列表 / Models sorted by score descending
        """
        valid_models = [
            m for m in self._models
            if m.benchmarks.get(benchmark, 0) > 0
        ]
        return sorted(
            valid_models,
            key=lambda m: m.benchmarks.get(benchmark, 0),
            reverse=True
        )[:top_n]

    def get_all_scenarios(self) -> List[str]:
        """获取所有场景类型 / Get all scenario types"""
        scenarios = set()
        for model in self._models:
            scenarios.update(model.scenarios)
        return sorted(list(scenarios))

    def get_all_tags(self) -> List[str]:
        """获取所有标签 / Get all tags"""
        tags = set()
        for model in self._models:
            tags.update(model.tags)
        return sorted(list(tags))

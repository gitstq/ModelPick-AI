# -*- coding: utf-8 -*-
"""
推荐引擎核心逻辑 / Recommendation Engine Core Logic

根据硬件配置和用户需求，计算模型兼容性分数并排序推荐。
Calculate model compatibility scores and sort recommendations based on
hardware configuration and user requirements.
"""

from typing import Dict, List, Optional, Tuple
from .database import ModelDatabase, ModelRecord
from .detector import HardwareInfo


class RecommendationResult:
    """推荐结果数据类 / Recommendation result data class"""

    def __init__(
        self,
        model: ModelRecord,
        compatibility_score: float,
        performance_score: float,
        overall_score: float,
        reasons: List[str],
    ) -> None:
        self.model = model
        self.compatibility_score = compatibility_score  # 兼容性分数(0-100) / Compatibility score
        self.performance_score = performance_score  # 性能分数(0-100) / Performance score
        self.overall_score = overall_score  # 综合分数(0-100) / Overall score
        self.reasons = reasons  # 推荐理由 / Recommendation reasons

    def to_dict(self) -> Dict:
        """转换为字典 / Convert to dictionary"""
        return {
            "model_id": self.model.id,
            "model_name": self.model.name,
            "model_name_zh": self.model.name_zh,
            "param_count": self.model.param_count,
            "developer": self.model.developer,
            "developer_zh": self.model.developer_zh,
            "compatibility_score": round(self.compatibility_score, 1),
            "performance_score": round(self.performance_score, 1),
            "overall_score": round(self.overall_score, 1),
            "reasons": self.reasons,
            "vram_required_gb": self.model.vram_required_gb,
            "ram_required_gb": self.model.ram_required_gb,
            "disk_required_gb": self.model.disk_required_gb,
            "scenarios": self.model.scenarios,
            "platforms": self.model.platforms,
            "ollama_command": self.model.ollama_command,
            "license": self.model.license,
            "description_zh": self.model.description_zh,
        }


class Recommender:
    """推荐引擎 / Recommendation engine

    核心推荐逻辑：根据硬件配置计算兼容性分数，结合性能分数给出综合推荐。
    Core recommendation logic: calculate compatibility score based on hardware,
    combine with performance score for overall recommendation.
    """

    # 基准测试权重配置 / Benchmark weight configuration
    # 不同场景下各基准测试的权重 / Weights for each benchmark under different scenarios
    SCENARIO_BENCHMARK_WEIGHTS: Dict[str, Dict[str, float]] = {
        "coding": {"humaneval": 0.4, "mmlu": 0.2, "gsm8k": 0.1, "c_eval": 0.1, "cmmlu": 0.1, "gaokao_bench": 0.1},
        "chat": {"mmlu": 0.3, "c_eval": 0.2, "cmmlu": 0.2, "humaneval": 0.1, "gsm8k": 0.1, "gaokao_bench": 0.1},
        "writing": {"mmlu": 0.3, "c_eval": 0.2, "cmmlu": 0.2, "humaneval": 0.05, "gsm8k": 0.05, "gaokao_bench": 0.2},
        "math": {"gsm8k": 0.4, "mmlu": 0.2, "humaneval": 0.1, "c_eval": 0.1, "cmmlu": 0.1, "gaokao_bench": 0.1},
        "multimodal": {"mmlu": 0.3, "c_eval": 0.2, "cmmlu": 0.2, "humaneval": 0.1, "gsm8k": 0.1, "gaokao_bench": 0.1},
        "reasoning": {"gsm8k": 0.3, "mmlu": 0.25, "humaneval": 0.15, "c_eval": 0.1, "cmmlu": 0.1, "gaokao_bench": 0.1},
        "embedding": {"mmlu": 1.0},
    }

    # 默认基准测试权重 / Default benchmark weights
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "mmlu": 0.25,
        "humaneval": 0.15,
        "gsm8k": 0.15,
        "c_eval": 0.15,
        "cmmlu": 0.15,
        "gaokao_bench": 0.15,
    }

    def __init__(self, database: ModelDatabase, hardware: HardwareInfo) -> None:
        """初始化推荐引擎 / Initialize recommendation engine

        Args:
            database: 模型数据库 / Model database
            hardware: 硬件信息 / Hardware information
        """
        self.db = database
        self.hw = hardware

    def calculate_compatibility(self, model: ModelRecord) -> Tuple[float, List[str]]:
        """计算单个模型的兼容性分数 / Calculate compatibility score for a single model

        兼容性分数基于：显存、内存、磁盘空间是否满足需求。
        Compatibility score based on: VRAM, RAM, disk space requirements.

        Args:
            model: 模型记录 / Model record

        Returns:
            (兼容性分数0-100, 推荐理由列表) / (compatibility score 0-100, list of reasons)
        """
        score = 100.0
        reasons: List[str] = []

        # 获取硬件资源 / Get hardware resources
        max_vram = self.hw.get_max_vram_gb()
        total_vram = self.hw.get_total_vram_gb()
        ram_total = self.hw.ram_total_gb
        disk_free = self.hw.disk_free_gb

        # 1. 显存检查 / VRAM check
        if max_vram > 0:
            if model.vram_required_gb <= max_vram:
                if model.vram_recommended_gb <= max_vram:
                    reasons.append(f"显存充足({max_vram:.1f}GB >= 推荐{model.vram_recommended_gb}GB)")
                else:
                    # 显存满足最低但不够推荐 / Meets minimum but not recommended
                    score -= 10
                    reasons.append(f"显存满足最低要求({max_vram:.1f}GB >= {model.vram_required_gb}GB)，但低于推荐值")
            else:
                # 显存不足 / Insufficient VRAM
                deficit = model.vram_required_gb - max_vram
                score -= min(50, deficit * 5)
                reasons.append(f"显存不足(需要{model.vram_required_gb}GB，可用{max_vram:.1f}GB)")
        else:
            # 无独立GPU，检查是否可以用CPU推理 / No discrete GPU, check if CPU inference possible
            if model.param_count_num <= 3:
                score -= 15
                reasons.append("无独立GPU，小模型可CPU推理")
            elif model.param_count_num <= 8:
                score -= 30
                reasons.append("无独立GPU，中等模型CPU推理较慢")
            else:
                score -= 50
                reasons.append("无独立GPU，大模型CPU推理不推荐")

        # 2. 内存检查 / RAM check
        if ram_total > 0:
            if model.ram_required_gb <= ram_total:
                if ram_total >= model.ram_required_gb * 1.5:
                    reasons.append(f"内存充足({ram_total:.1f}GB)")
                else:
                    score -= 5
                    reasons.append(f"内存满足最低要求({ram_total:.1f}GB)")
            else:
                deficit = model.ram_required_gb - ram_total
                score -= min(30, deficit * 3)
                reasons.append(f"内存不足(需要{model.ram_required_gb}GB，可用{ram_total:.1f}GB)")

        # 3. 磁盘空间检查 / Disk space check
        if disk_free > 0:
            if model.disk_required_gb <= disk_free:
                reasons.append(f"磁盘空间充足(剩余{disk_free:.1f}GB)")
            else:
                deficit = model.disk_required_gb - disk_free
                score -= min(20, deficit * 2)
                reasons.append(f"磁盘空间不足(需要{model.disk_required_gb}GB，可用{disk_free:.1f}GB)")

        # 确保分数不低于0 / Ensure score doesn't go below 0
        score = max(0, min(100, score))
        return score, reasons

    def calculate_performance(self, model: ModelRecord, scenario: Optional[str] = None) -> float:
        """计算模型性能分数 / Calculate model performance score

        基于基准测试分数加权计算，不同场景使用不同权重。
        Weighted calculation based on benchmark scores, different weights for different scenarios.

        Args:
            model: 模型记录 / Model record
            scenario: 场景名称（可选）/ Scenario name (optional)

        Returns:
            性能分数(0-100) / Performance score (0-100)
        """
        benchmarks = model.benchmarks

        # 选择权重 / Select weights
        if scenario and scenario in self.SCENARIO_BENCHMARK_WEIGHTS:
            weights = self.SCENARIO_BENCHMARK_WEIGHTS[scenario]
        else:
            weights = self.DEFAULT_WEIGHTS

        # 加权计算 / Weighted calculation
        total_score = 0.0
        total_weight = 0.0

        for bench_name, weight in weights.items():
            bench_score = benchmarks.get(bench_name, 0)
            if bench_score > 0:
                total_score += bench_score * weight
                total_weight += weight

        if total_weight > 0:
            return total_score / total_weight
        return 0.0

    def recommend(
        self,
        scenario: Optional[str] = None,
        max_params: Optional[float] = None,
        top_n: int = 10,
        min_compatibility: float = 0.0,
    ) -> List[RecommendationResult]:
        """生成推荐列表 / Generate recommendation list

        Args:
            scenario: 场景过滤（如'coding'）/ Scenario filter (e.g., 'coding')
            max_params: 最大参数量限制(B) / Maximum parameter limit (in billions)
            top_n: 返回前N个结果 / Return top N results
            min_compatibility: 最低兼容性分数 / Minimum compatibility score

        Returns:
            按综合分数降序排列的推荐结果 / Recommendations sorted by overall score descending
        """
        # 获取候选模型 / Get candidate models
        candidates = self.db.get_all()

        # 按场景过滤 / Filter by scenario
        if scenario:
            candidates = self.db.filter_by_scenario(scenario)

        # 按参数量过滤 / Filter by parameter count
        if max_params is not None:
            candidates = [m for m in candidates if m.param_count_num <= max_params]

        # 计算每个模型的分数 / Calculate scores for each model
        results: List[RecommendationResult] = []
        for model in candidates:
            compatibility_score, reasons = self.calculate_compatibility(model)
            performance_score = self.calculate_performance(model, scenario)

            # 综合分数 = 兼容性 * 0.4 + 性能 * 0.6
            # Overall score = compatibility * 0.4 + performance * 0.6
            overall_score = compatibility_score * 0.4 + performance_score * 0.6

            # 过滤低兼容性模型 / Filter low compatibility models
            if compatibility_score >= min_compatibility:
                results.append(RecommendationResult(
                    model=model,
                    compatibility_score=compatibility_score,
                    performance_score=performance_score,
                    overall_score=overall_score,
                    reasons=reasons,
                ))

        # 按综合分数降序排序 / Sort by overall score descending
        results.sort(key=lambda r: r.overall_score, reverse=True)
        return results[:top_n]

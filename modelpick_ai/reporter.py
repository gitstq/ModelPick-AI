# -*- coding: utf-8 -*-
"""
报告生成与导出模块 / Report Generation and Export Module

支持JSON、Markdown、CSV三种格式的推荐结果导出。
Supports JSON, Markdown, and CSV format export for recommendation results.
"""

import json
import csv
import io
from typing import List, Optional
from .recommender import RecommendationResult
from .detector import HardwareInfo


class ReportExporter:
    """报告导出器 / Report exporter

    将推荐结果和硬件信息导出为多种格式。
    Export recommendation results and hardware info to multiple formats.
    """

    def __init__(self, hardware: HardwareInfo) -> None:
        """初始化导出器 / Initialize exporter

        Args:
            hardware: 硬件信息 / Hardware information
        """
        self.hardware = hardware

    def export_json(
        self,
        results: List[RecommendationResult],
        output_path: Optional[str] = None,
    ) -> str:
        """导出为JSON格式 / Export as JSON format

        Args:
            results: 推荐结果列表 / Recommendation results
            output_path: 输出文件路径，None则返回字符串 / Output file path, None to return string

        Returns:
            JSON字符串 / JSON string
        """
        data = {
            "hardware_info": self.hardware.to_dict(),
            "recommendations": [r.to_dict() for r in results],
            "total_count": len(results),
        }

        json_str = json.dumps(data, ensure_ascii=False, indent=2)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(json_str)

        return json_str

    def export_markdown(
        self,
        results: List[RecommendationResult],
        output_path: Optional[str] = None,
    ) -> str:
        """导出为Markdown格式 / Export as Markdown format

        Args:
            results: 推荐结果列表 / Recommendation results
            output_path: 输出文件路径，None则返回字符串 / Output file path, None to return string

        Returns:
            Markdown字符串 / Markdown string
        """
        lines: List[str] = []

        # 标题 / Title
        lines.append("# ModelPick-AI 模型推荐报告")
        lines.append("# ModelPick-AI Model Recommendation Report")
        lines.append("")

        # 硬件信息摘要 / Hardware info summary
        hw = self.hardware
        lines.append("## 硬件配置 / Hardware Configuration")
        lines.append("")
        lines.append(f"| 项目 / Item | 值 / Value |")
        lines.append(f"|---|---|")
        lines.append(f"| CPU | {hw.cpu_model or hw.cpu_arch} ({hw.cpu_count} cores) |")
        if hw.gpus:
            for gpu in hw.gpus:
                lines.append(f"| GPU | {gpu['vendor']} {gpu['model']} ({gpu['vram_gb']:.1f}GB VRAM) |")
        else:
            lines.append("| GPU | 未检测到 / Not detected |")
        lines.append(f"| 内存 / RAM | {hw.ram_total_gb:.1f} GB |")
        lines.append(f"| 磁盘可用 / Disk Free | {hw.disk_free_gb:.1f} GB |")
        lines.append(f"| 操作系统 / OS | {hw.os_name} {hw.os_version} |")
        lines.append("")

        # 推荐结果表格 / Recommendation results table
        lines.append("## 推荐模型 / Recommended Models")
        lines.append("")
        lines.append(
            "| 排名 / Rank | 模型 / Model | 参数量 / Params | 综合分 / Score | "
            "兼容性 / Compat | 显存需求 / VRAM | 场景 / Scenarios |"
        )
        lines.append(
            "|---|---|---|---|---|---|---|"
        )

        for i, r in enumerate(results, 1):
            scenarios_str = ", ".join(r.model.scenarios)
            lines.append(
                f"| {i} | {r.model.name} | {r.model.param_count} | "
                f"{r.overall_score:.1f} | {r.compatibility_score:.1f} | "
                f"{r.model.vram_required_gb:.1f}GB | {scenarios_str} |"
            )

        lines.append("")

        # 详细信息 / Detailed information
        lines.append("## 模型详情 / Model Details")
        lines.append("")

        for i, r in enumerate(results, 1):
            lines.append(f"### {i}. {r.model.name} ({r.model.name_zh})")
            lines.append("")
            lines.append(f"- **开发者 / Developer**: {r.model.developer} ({r.model.developer_zh})")
            lines.append(f"- **参数量 / Parameters**: {r.model.param_count}")
            lines.append(f"- **综合分数 / Overall Score**: {r.overall_score:.1f}")
            lines.append(f"- **兼容性分数 / Compatibility**: {r.compatibility_score:.1f}")
            lines.append(f"- **性能分数 / Performance**: {r.performance_score:.1f}")
            lines.append(f"- **显存需求 / VRAM Required**: {r.model.vram_required_gb}GB (推荐 {r.model.vram_recommended_gb}GB)")
            lines.append(f"- **内存需求 / RAM Required**: {r.model.ram_required_gb}GB")
            lines.append(f"- **上下文长度 / Context Length**: {r.model.context_length}")
            lines.append(f"- **支持量化 / Quantization**: {', '.join(r.model.quantization)}")
            lines.append(f"- **适用场景 / Scenarios**: {', '.join(r.model.scenarios)}")
            lines.append(f"- **支持平台 / Platforms**: {', '.join(r.model.platforms)}")
            lines.append(f"- **开源协议 / License**: {r.model.license}")
            if r.model.ollama_command:
                lines.append(f"- **Ollama安装 / Ollama Install**: `{r.model.ollama_command}`")
            lines.append(f"- **描述 / Description**: {r.model.description_zh}")
            lines.append("")

            # 推荐理由 / Recommendation reasons
            if r.reasons:
                lines.append("**推荐理由 / Reasons:**")
                for reason in r.reasons:
                    lines.append(f"  - {reason}")
                lines.append("")

        md_str = "\n".join(lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_str)

        return md_str

    def export_csv(
        self,
        results: List[RecommendationResult],
        output_path: Optional[str] = None,
    ) -> str:
        """导出为CSV格式 / Export as CSV format

        Args:
            results: 推荐结果列表 / Recommendation results
            output_path: 输出文件路径，None则返回字符串 / Output file path, None to return string

        Returns:
            CSV字符串 / CSV string
        """
        # 使用io.StringIO构建CSV / Use io.StringIO to build CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头 / Write header
        header = [
            "Rank",
            "Model ID",
            "Model Name",
            "Model Name (ZH)",
            "Developer",
            "Developer (ZH)",
            "Parameters",
            "Overall Score",
            "Compatibility Score",
            "Performance Score",
            "VRAM Required (GB)",
            "RAM Required (GB)",
            "Disk Required (GB)",
            "Context Length",
            "Scenarios",
            "Platforms",
            "Ollama Command",
            "License",
            "Description (ZH)",
            "Reasons",
        ]
        writer.writerow(header)

        # 写入数据行 / Write data rows
        for i, r in enumerate(results, 1):
            row = [
                i,
                r.model.id,
                r.model.name,
                r.model.name_zh,
                r.model.developer,
                r.model.developer_zh,
                r.model.param_count,
                round(r.overall_score, 1),
                round(r.compatibility_score, 1),
                round(r.performance_score, 1),
                r.model.vram_required_gb,
                r.model.ram_required_gb,
                r.model.disk_required_gb,
                r.model.context_length,
                ", ".join(r.model.scenarios),
                ", ".join(r.model.platforms),
                r.model.ollama_command,
                r.model.license,
                r.model.description_zh,
                "; ".join(r.reasons),
            ]
            writer.writerow(row)

        csv_str = output.getvalue()

        if output_path:
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                f.write(csv_str)

        return csv_str

    def export(
        self,
        results: List[RecommendationResult],
        format_type: str,
        output_path: Optional[str] = None,
    ) -> str:
        """通用导出方法 / Generic export method

        Args:
            results: 推荐结果列表 / Recommendation results
            format_type: 导出格式（json/markdown/csv）/ Export format (json/markdown/csv)
            output_path: 输出文件路径 / Output file path

        Returns:
            导出内容的字符串 / Exported content string
        """
        format_type = format_type.lower()

        if format_type in ("json",):
            return self.export_json(results, output_path)
        elif format_type in ("markdown", "md"):
            return self.export_markdown(results, output_path)
        elif format_type in ("csv",):
            return self.export_csv(results, output_path)
        else:
            raise ValueError(f"不支持的导出格式: {format_type} / Unsupported format: {format_type}")

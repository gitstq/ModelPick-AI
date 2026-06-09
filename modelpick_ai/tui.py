# -*- coding: utf-8 -*-
"""
TUI界面渲染模块 / TUI Interface Rendering Module

使用Rich库构建美观的终端界面，包括硬件信息展示、模型列表、推荐结果等。
Build beautiful terminal interfaces using the Rich library, including hardware
info display, model lists, recommendation results, etc.
"""

from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box

from .detector import HardwareInfo
from .database import ModelRecord, ModelDatabase
from .recommender import RecommendationResult


class TUIRenderer:
    """TUI渲染器 / TUI renderer

    使用Rich库渲染各种终端界面组件。
    Render various terminal UI components using the Rich library.
    """

    def __init__(self) -> None:
        self.console = Console()

    def print_banner(self) -> None:
        """打印程序横幅 / Print program banner"""
        banner_text = Text()
        banner_text.append("\n", style="default")
        banner_text.append("  ╔══════════════════════════════════════════════╗\n", style="bold cyan")
        banner_text.append("  ║                                            ║\n", style="bold cyan")
        banner_text.append("  ║", style="bold cyan")
        banner_text.append("       ModelPick-AI v1.0.0                    ", style="bold white on blue")
        banner_text.append("║\n", style="bold cyan")
        banner_text.append("  ║", style="bold cyan")
        banner_text.append("  轻量级终端AI模型智能推荐引擎                    ", style="bold yellow")
        banner_text.append("║\n", style="bold cyan")
        banner_text.append("  ║", style="bold cyan")
        banner_text.append("  Lightweight AI Model Recommender            ", style="bold green")
        banner_text.append("║\n", style="bold cyan")
        banner_text.append("  ║                                            ║\n", style="bold cyan")
        banner_text.append("  ╚══════════════════════════════════════════════╝\n", style="bold cyan")
        self.console.print(banner_text)

    def print_hardware_info(self, hw: HardwareInfo) -> None:
        """打印硬件信息 / Print hardware information

        Args:
            hw: 硬件信息 / Hardware information
        """
        # 系统信息面板 / System info panel
        system_text = (
            f"[bold cyan]操作系统 / OS:[/bold cyan] {hw.os_name} {hw.os_version}\n"
            f"[bold cyan]Python版本 / Version:[/bold cyan] {hw.python_version}"
        )
        self.console.print(Panel(system_text, title="[bold]系统信息 / System[/bold]", border_style="blue"))

        # CPU信息面板 / CPU info panel
        cpu_text = (
            f"[bold cyan]型号 / Model:[/bold cyan] {hw.cpu_model or 'N/A'}\n"
            f"[bold cyan]架构 / Architecture:[/bold cyan] {hw.cpu_arch}\n"
            f"[bold cyan]核心数 / Cores:[/bold cyan] {hw.cpu_count}"
        )
        self.console.print(Panel(cpu_text, title="[bold]CPU[/bold]", border_style="green"))

        # GPU信息面板 / GPU info panel
        if hw.gpus:
            for i, gpu in enumerate(hw.gpus):
                gpu_text = (
                    f"[bold cyan]厂商 / Vendor:[/bold cyan] {gpu.get('vendor', 'N/A')}\n"
                    f"[bold cyan]型号 / Model:[/bold cyan] {gpu.get('model', 'N/A')}\n"
                    f"[bold cyan]显存 / VRAM:[/bold cyan] {gpu.get('vram_gb', 0):.1f} GB\n"
                    f"[bold cyan]驱动 / Driver:[/bold cyan] {gpu.get('driver_version', 'N/A')}"
                )
                self.console.print(Panel(gpu_text, title=f"[bold]GPU #{i+1}[/bold]", border_style="magenta"))
        else:
            self.console.print(Panel(
                "[yellow]未检测到独立GPU / No discrete GPU detected\n"
                "将使用CPU推理模式 / Will use CPU inference mode[/yellow]",
                title="[bold]GPU[/bold]", border_style="yellow"
            ))

        # 内存和磁盘信息面板 / RAM and Disk info panel
        memory_text = (
            f"[bold cyan]总内存 / Total RAM:[/bold cyan] {hw.ram_total_gb:.1f} GB\n"
            f"[bold cyan]可用内存 / Available:[/bold cyan] {hw.ram_available_gb:.1f} GB\n"
            f"[bold cyan]总磁盘 / Total Disk:[/bold cyan] {hw.disk_total_gb:.1f} GB\n"
            f"[bold cyan]可用磁盘 / Free Disk:[/bold cyan] {hw.disk_free_gb:.1f} GB"
        )
        self.console.print(Panel(memory_text, title="[bold]内存 & 磁盘 / Memory & Disk[/bold]", border_style="red"))

    def print_model_list(
        self,
        models: List[ModelRecord],
        show_details: bool = False,
    ) -> None:
        """打印模型列表 / Print model list

        Args:
            models: 模型列表 / Model list
            show_details: 是否显示详细信息 / Whether to show detailed info
        """
        if not models:
            self.console.print("[yellow]未找到匹配的模型 / No matching models found[/yellow]")
            return

        table = Table(
            title=f"[bold]模型列表 / Model List ({len(models)} 个模型 / models)[/bold]",
            box=box.ROUNDED,
            show_lines=True,
            title_style="bold cyan",
        )

        # 基础列 / Basic columns
        table.add_column("#", style="dim", width=4)
        table.add_column("模型 / Model", style="bold", min_width=25)
        table.add_column("中文名 / Chinese", style="cyan", min_width=15)
        table.add_column("参数量 / Params", style="green", width=10)
        table.add_column("显存 / VRAM", style="yellow", width=12)
        table.add_column("场景 / Scenarios", style="magenta", min_width=20)

        if show_details:
            table.add_column("平台 / Platforms", style="blue", min_width=20)
            table.add_column("协议 / License", style="dim", width=15)

        for i, model in enumerate(models, 1):
            scenarios_str = ", ".join(model.scenarios[:3])
            if len(model.scenarios) > 3:
                scenarios_str += f" +{len(model.scenarios) - 3}"

            row = [
                str(i),
                model.name,
                model.name_zh,
                model.param_count,
                f"{model.vram_required_gb:.1f}GB / {model.vram_recommended_gb:.1f}GB",
                scenarios_str,
            ]

            if show_details:
                row.append(", ".join(model.platforms))
                row.append(model.license)

            table.add_row(*row)

        self.console.print(table)

    def print_recommendations(self, results: List[RecommendationResult]) -> None:
        """打印推荐结果 / Print recommendation results

        Args:
            results: 推荐结果列表 / Recommendation results
        """
        if not results:
            self.console.print("[yellow]没有找到合适的模型推荐 / No suitable model recommendations found[/yellow]")
            return

        # 综合推荐表格 / Overall recommendation table
        table = Table(
            title="[bold]推荐模型 / Recommended Models[/bold]",
            box=box.DOUBLE_EDGE,
            show_lines=True,
            title_style="bold green",
        )

        table.add_column("#", style="bold", width=4)
        table.add_column("模型 / Model", style="bold", min_width=22)
        table.add_column("中文名 / Chinese", style="cyan", min_width=15)
        table.add_column("参数量 / Params", style="green", width=8)
        table.add_column("综合分 / Overall", style="bold yellow", width=10)
        table.add_column("兼容性 / Compat", style="blue", width=10)
        table.add_column("性能 / Perf", style="red", width=8)
        table.add_column("显存 / VRAM", style="magenta", width=10)
        table.add_column("场景 / Scenarios", min_width=18)

        for i, r in enumerate(results, 1):
            # 根据分数设置颜色 / Set color based on score
            if r.overall_score >= 70:
                score_style = "bold green"
            elif r.overall_score >= 50:
                score_style = "bold yellow"
            else:
                score_style = "bold red"

            scenarios_str = ", ".join(r.model.scenarios[:3])
            if len(r.model.scenarios) > 3:
                scenarios_str += f" +{len(r.model.scenarios) - 3}"

            table.add_row(
                str(i),
                r.model.name,
                r.model.name_zh,
                r.model.param_count,
                f"[{score_style}]{r.overall_score:.1f}[/{score_style}]",
                f"{r.compatibility_score:.1f}",
                f"{r.performance_score:.1f}",
                f"{r.model.vram_required_gb:.1f}GB",
                scenarios_str,
            )

        self.console.print(table)

        # 推荐理由详情 / Recommendation reason details
        self.console.print("\n[bold]推荐理由 / Recommendation Details:[/bold]\n")
        for i, r in enumerate(results[:5], 1):  # 只显示前5个的理由 / Show reasons for top 5 only
            self.console.print(f"  [bold cyan]{i}. {r.model.name}[/bold cyan] ({r.model.name_zh})")
            for reason in r.reasons:
                self.console.print(f"    [dim]- {reason}[/dim]")
            if r.model.ollama_command:
                self.console.print(
                    f"    [bold green]Ollama安装 / Install:[/bold green] {r.model.ollama_command}"
                )
            self.console.print()

    def print_model_detail(self, model: ModelRecord) -> None:
        """打印模型详情 / Print model details

        Args:
            model: 模型记录 / Model record
        """
        # 基本信息面板 / Basic info panel
        basic_text = (
            f"[bold cyan]模型名称 / Name:[/bold cyan] {model.name}\n"
            f"[bold cyan]中文名称 / Chinese:[/bold cyan] {model.name_zh}\n"
            f"[bold cyan]开发者 / Developer:[/bold cyan] {model.developer} ({model.developer_zh})\n"
            f"[bold cyan]参数量 / Parameters:[/bold cyan] {model.param_count}\n"
            f"[bold cyan]开源协议 / License:[/bold cyan] {model.license}\n"
            f"[bold cyan]描述 / Description:[/bold cyan] {model.description_zh}"
        )
        self.console.print(Panel(basic_text, title="[bold]基本信息 / Basic Info[/bold]", border_style="cyan"))

        # 硬件需求面板 / Hardware requirements panel
        hw_text = (
            f"[bold cyan]最低显存 / Min VRAM:[/bold cyan] {model.vram_required_gb:.1f} GB\n"
            f"[bold cyan]推荐显存 / Rec VRAM:[/bold cyan] {model.vram_recommended_gb:.1f} GB\n"
            f"[bold cyan]最低内存 / Min RAM:[/bold cyan] {model.ram_required_gb:.1f} GB\n"
            f"[bold cyan]最低磁盘 / Min Disk:[/bold cyan] {model.disk_required_gb:.1f} GB\n"
            f"[bold cyan]上下文长度 / Context:[/bold cyan] {model.context_length:,}\n"
            f"[bold cyan]量化格式 / Quantization:[/bold cyan] {', '.join(model.quantization)}"
        )
        self.console.print(Panel(hw_text, title="[bold]硬件需求 / Requirements[/bold]", border_style="yellow"))

        # 基准测试面板 / Benchmarks panel
        bench_table = Table(title="[bold]基准测试 / Benchmarks[/bold]", box=box.SIMPLE)
        bench_table.add_column("基准 / Benchmark", style="cyan")
        bench_table.add_column("分数 / Score", style="green", justify="right")

        benchmark_names = {
            "mmlu": "MMLU (综合知识)",
            "humaneval": "HumanEval (代码生成)",
            "gsm8k": "GSM8K (数学推理)",
            "c_eval": "C-Eval (中文综合)",
            "cmmlu": "CMMLU (中文多领域)",
            "gaokao_bench": "GAOKAO-Bench (高考)",
        }

        for key, name in benchmark_names.items():
            score = model.benchmarks.get(key, 0)
            if score > 0:
                bench_table.add_row(name, f"{score:.1f}")

        self.console.print(bench_table)

        # 场景和平台 / Scenarios and platforms
        info_text = (
            f"[bold cyan]适用场景 / Scenarios:[/bold cyan] {', '.join(model.scenarios)}\n"
            f"[bold cyan]支持平台 / Platforms:[/bold cyan] {', '.join(model.platforms)}\n"
            f"[bold cyan]标签 / Tags:[/bold cyan] {', '.join(model.tags)}"
        )
        self.console.print(Panel(info_text, title="[bold]场景与平台 / Scenarios & Platforms[/bold]", border_style="green"))

        # 安装命令 / Install command
        if model.ollama_command:
            install_text = (
                f"[bold cyan]Ollama一键安装 / Ollama Install:[/bold cyan]\n"
                f"  [bold green]{model.ollama_command}[/bold green]\n\n"
                f"[bold cyan]HuggingFace:[/bold cyan] https://huggingface.co/{model.id}\n"
                f"[bold cyan]ModelScope:[/bold cyan] https://modelscope.cn/models/{model.id}"
            )
            self.console.print(Panel(install_text, title="[bold]安装方式 / Installation[/bold]", border_style="magenta"))

    def print_benchmark_ranking(
        self,
        benchmark: str,
        models: List[ModelRecord],
        top_n: int = 10,
    ) -> None:
        """打印基准测试排行榜 / Print benchmark ranking

        Args:
            benchmark: 基准测试名称 / Benchmark name
            models: 模型列表（已排序）/ Model list (already sorted)
            top_n: 显示前N名 / Show top N
        """
        benchmark_display = {
            "mmlu": "MMLU (综合知识 / General Knowledge)",
            "humaneval": "HumanEval (代码生成 / Code Generation)",
            "gsm8k": "GSM8K (数学推理 / Math Reasoning)",
            "c_eval": "C-Eval (中文综合 / Chinese General)",
            "cmmlu": "CMMLU (中文多领域 / Chinese Multi-domain)",
            "gaokao_bench": "GAOKAO-Bench (高考 / College Entrance Exam)",
        }

        title = benchmark_display.get(benchmark, benchmark)

        table = Table(
            title=f"[bold]{title} 排行榜 / Ranking[/bold]",
            box=box.ROUNDED,
            show_lines=True,
        )

        table.add_column("#", style="bold", width=4)
        table.add_column("模型 / Model", style="bold", min_width=22)
        table.add_column("中文名 / Chinese", style="cyan", min_width=15)
        table.add_column("参数量 / Params", style="green", width=10)
        table.add_column("分数 / Score", style="bold yellow", width=10)

        for i, model in enumerate(models[:top_n], 1):
            score = model.benchmarks.get(benchmark, 0)
            # 前三名用特殊样式 / Top 3 use special styles
            if i == 1:
                rank_style = "bold yellow"
            elif i == 2:
                rank_style = "bold white"
            elif i == 3:
                rank_style = "bold red"
            else:
                rank_style = "dim"

            table.add_row(
                f"[{rank_style}]{i}[/{rank_style}]",
                model.name,
                model.name_zh,
                model.param_count,
                f"{score:.1f}",
            )

        self.console.print(table)

    def print_scenarios(self, scenarios: List[str]) -> None:
        """打印可用场景列表 / Print available scenarios"""
        self.console.print("[bold]可用场景 / Available Scenarios:[/bold]")
        for scenario in scenarios:
            self.console.print(f"  [cyan]- {scenario}[/cyan]")

    def print_search_results(self, keyword: str, models: List[ModelRecord]) -> None:
        """打印搜索结果 / Print search results"""
        self.console.print(f"\n[bold]搜索结果 / Search Results for '[green]{keyword}[/green]' "
                           f"({len(models)} 个结果 / results):[/bold]\n")
        self.print_model_list(models)

    def print_export_success(self, format_type: str, output_path: str) -> None:
        """打印导出成功消息 / Print export success message"""
        self.console.print(
            f"\n[bold green]导出成功 / Export successful![/bold green]\n"
            f"  格式 / Format: {format_type.upper()}\n"
            f"  路径 / Path: {output_path}"
        )

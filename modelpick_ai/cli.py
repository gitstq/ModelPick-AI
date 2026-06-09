# -*- coding: utf-8 -*-
"""
CLI入口模块 / CLI Entry Module

使用Click框架定义命令行接口，提供硬件检测、模型推荐、搜索、导出等功能。
Define CLI interface using the Click framework, providing hardware detection,
model recommendation, search, export, and other features.
"""

import os
import sys
import click
from typing import Optional

from . import __version__
from .detector import HardwareDetector, detect_hardware
from .database import ModelDatabase
from .recommender import Recommender
from .reporter import ReportExporter
from .tui import TUIRenderer


def _get_default_export_path(format_type: str) -> str:
    """生成默认导出文件路径 / Generate default export file path"""
    return os.path.join(os.getcwd(), f"modelpick_recommendation.{format_type}")


@click.group()
@click.version_option(version=__version__, prog_name="ModelPick-AI")
@click.pass_context
def main(ctx: click.Context) -> None:
    """ModelPick-AI - 轻量级终端AI模型智能推荐引擎
    Lightweight Terminal AI Model Recommendation Engine

    根据您的硬件配置，智能推荐最适合的本地AI大语言模型。
    Intelligently recommend the best local AI LLM based on your hardware configuration.
    """
    ctx.ensure_object(dict)
    # 初始化共享组件 / Initialize shared components
    ctx.obj["db"] = ModelDatabase()
    ctx.obj["tui"] = TUIRenderer()


@main.command()
@click.pass_context
def detect(ctx: click.Context) -> None:
    """检测系统硬件配置 / Detect system hardware configuration

    自动检测CPU、GPU、内存、磁盘等硬件信息。
    Automatically detect CPU, GPU, RAM, disk and other hardware info.
    """
    tui: TUIRenderer = ctx.obj["tui"]
    tui.print_banner()

    click.echo("正在检测硬件 / Detecting hardware...\n")
    detector = HardwareDetector()
    hw = detector.detect_all()
    tui.print_hardware_info(hw)


@main.command()
@click.option(
    "--scene", "-s", default=None, type=str,
    help="指定推荐场景 / Specify recommendation scenario (e.g., coding, chat, math, writing)"
)
@click.option(
    "--max-params", "-p", default=None, type=float,
    help="最大参数量限制(B) / Maximum parameter count limit (in billions)"
)
@click.option(
    "--top", "-n", default=10, type=int,
    help="显示前N个推荐 / Show top N recommendations (default: 10)"
)
@click.option(
    "--min-compat", default=0.0, type=float,
    help="最低兼容性分数 / Minimum compatibility score (0-100)"
)
@click.pass_context
def recommend(
    ctx: click.Context,
    scene: Optional[str],
    max_params: Optional[float],
    top: int,
    min_compat: float,
) -> None:
    """智能推荐AI模型 / Intelligently recommend AI models

    根据硬件配置和需求场景，推荐最适合的模型。
    Recommend the most suitable models based on hardware and scenario requirements.
    """
    tui: TUIRenderer = ctx.obj["tui"]
    db: ModelDatabase = ctx.obj["db"]
    tui.print_banner()

    # 检测硬件 / Detect hardware
    click.echo("正在检测硬件 / Detecting hardware...\n")
    hw = detect_hardware()
    tui.print_hardware_info(hw)

    # 验证场景参数 / Validate scenario parameter
    if scene:
        valid_scenarios = db.get_all_scenarios()
        if scene.lower() not in [s.lower() for s in valid_scenarios]:
            click.echo(f"[red]错误 / Error: 未知场景 '{scene}'[/red]")
            click.echo(f"可用场景 / Available scenarios: {', '.join(valid_scenarios)}")
            return

    # 生成推荐 / Generate recommendations
    click.echo(f"\n正在生成推荐 / Generating recommendations...\n")
    recommender = Recommender(db, hw)
    results = recommender.recommend(
        scenario=scene,
        max_params=max_params,
        top_n=top,
        min_compatibility=min_compat,
    )

    # 保存结果供导出使用 / Save results for export
    ctx.obj["results"] = results
    ctx.obj["hardware"] = hw

    # 显示推荐结果 / Display recommendations
    tui.print_recommendations(results)


@main.command()
@click.argument("keyword", type=str)
@click.pass_context
def search(ctx: click.Context, keyword: str) -> None:
    """搜索模型 / Search models

    按关键词搜索模型数据库，支持名称、描述、标签等字段。
    Search model database by keyword, supporting name, description, tags, etc.

    KEYWORD: 搜索关键词 / Search keyword
    """
    tui: TUIRenderer = ctx.obj["tui"]
    db: ModelDatabase = ctx.obj["db"]
    tui.print_banner()

    results = db.search(keyword)
    tui.print_search_results(keyword, results)


@main.command()
@click.argument("model_id", type=str)
@click.pass_context
def detail(ctx: click.Context, model_id: str) -> None:
    """查看模型详情 / View model details

    MODEL_ID: 模型唯一标识 / Model unique identifier
    """
    tui: TUIRenderer = ctx.obj["tui"]
    db: ModelDatabase = ctx.obj["db"]
    tui.print_banner()

    model = db.get_by_id(model_id)
    if model:
        tui.print_model_detail(model)
    else:
        click.echo(f"[red]未找到模型 '{model_id}' / Model '{model_id}' not found[/red]")
        click.echo("\n提示 / Tip: 使用 'modelpick list' 查看所有可用模型ID")
        click.echo("Tip: Use 'modelpick list' to see all available model IDs")


@main.command("list")
@click.option(
    "--scene", "-s", default=None, type=str,
    help="按场景过滤 / Filter by scenario"
)
@click.option(
    "--details", "-d", is_flag=True, default=False,
    help="显示详细信息 / Show detailed information"
)
@click.pass_context
def list_cmd(ctx: click.Context, scene: Optional[str], details: bool) -> None:
    """列出所有模型 / List all models"""
    tui: TUIRenderer = ctx.obj["tui"]
    db: ModelDatabase = ctx.obj["db"]
    tui.print_banner()

    if scene:
        models = db.filter_by_scenario(scene)
        click.echo(f"场景 / Scenario: [bold]{scene}[/bold] ({len(models)} 个模型 / models)\n")
    else:
        models = db.get_all()
        click.echo(f"全部模型 / All models: [bold]{db.count}[/bold] 个模型 / models\n")

    tui.print_model_list(models, show_details=details)


@main.command()
@click.option(
    "--format", "-f", "format_type", default="json", type=click.Choice(["json", "markdown", "csv"]),
    help="导出格式 / Export format (json, markdown, csv)"
)
@click.option(
    "--output", "-o", default=None, type=str,
    help="输出文件路径 / Output file path (default: auto-generated)"
)
@click.option(
    "--scene", "-s", default=None, type=str,
    help="推荐场景 / Recommendation scenario"
)
@click.option(
    "--max-params", "-p", default=None, type=float,
    help="最大参数量(B) / Maximum parameter count (in billions)"
)
@click.option(
    "--top", "-n", default=10, type=int,
    help="推荐数量 / Number of recommendations"
)
@click.pass_context
def export(
    ctx: click.Context,
    format_type: str,
    output: Optional[str],
    scene: Optional[str],
    max_params: Optional[float],
    top: int,
) -> None:
    """导出推荐结果 / Export recommendation results

    支持JSON、Markdown、CSV格式导出。
    Supports JSON, Markdown, CSV format export.
    """
    tui: TUIRenderer = ctx.obj["tui"]
    db: ModelDatabase = ctx.obj["db"]

    # 检测硬件 / Detect hardware
    hw = detect_hardware()

    # 生成推荐 / Generate recommendations
    recommender = Recommender(db, hw)
    results = recommender.recommend(
        scenario=scene,
        max_params=max_params,
        top_n=top,
    )

    if not results:
        click.echo("[yellow]没有推荐结果可导出 / No recommendations to export[/yellow]")
        return

    # 确定输出路径 / Determine output path
    if output is None:
        ext = "md" if format_type == "markdown" else format_type
        output = _get_default_export_path(ext)

    # 导出 / Export
    exporter = ReportExporter(hw)
    exporter.export(results, format_type, output)
    tui.print_export_success(format_type, output)


@main.command()
@click.option(
    "--benchmark", "-b", default=None, type=str,
    help="指定基准测试 / Specify benchmark (mmlu, humaneval, gsm8k, c_eval, cmmlu, gaokao_bench)"
)
@click.option(
    "--top", "-n", default=10, type=int,
    help="显示前N名 / Show top N"
)
@click.pass_context
def benchmark(ctx: click.Context, benchmark: Optional[str], top: int) -> None:
    """显示基准测试排行榜 / Display benchmark rankings"""
    tui: TUIRenderer = ctx.obj["tui"]
    db: ModelDatabase = ctx.obj["db"]
    tui.print_banner()

    available_benchmarks = ["mmlu", "humaneval", "gsm8k", "c_eval", "cmmlu", "gaokao_bench"]

    if benchmark:
        if benchmark.lower() not in available_benchmarks:
            click.echo(f"[red]错误 / Error: 未知基准测试 '{benchmark}'[/red]")
            click.echo(f"可用基准 / Available: {', '.join(available_benchmarks)}")
            return

        models = db.get_benchmark_ranking(benchmark.lower(), top)
        tui.print_benchmark_ranking(benchmark.lower(), models, top)
    else:
        # 显示所有基准测试排行榜 / Show all benchmark rankings
        for b in available_benchmarks:
            models = db.get_benchmark_ranking(b, top)
            tui.print_benchmark_ranking(b, models, top)
            click.echo()


# 当作为模块直接运行时的默认行为 / Default behavior when run as module directly
def _run_default() -> None:
    """默认运行模式：检测硬件 + 推荐Top 10 / Default mode: detect hardware + recommend Top 10"""
    tui = TUIRenderer()
    db = ModelDatabase()

    tui.print_banner()

    # 检测硬件 / Detect hardware
    click.echo("正在检测硬件 / Detecting hardware...\n")
    hw = detect_hardware()
    tui.print_hardware_info(hw)

    # 生成推荐 / Generate recommendations
    click.echo("\n正在生成推荐 / Generating recommendations...\n")
    recommender = Recommender(db, hw)
    results = recommender.recommend(top_n=10)

    # 显示推荐结果 / Display recommendations
    tui.print_recommendations(results)

    # 提示其他命令 / Hint for other commands
    click.echo("[dim]提示 / Tips:[/dim]")
    click.echo("[dim]  modelpick detect       - 仅检测硬件 / Detect hardware only[/dim]")
    click.echo("[dim]  modelpick recommend -s coding - 按场景推荐 / Recommend by scenario[/dim]")
    click.echo("[dim]  modelpick search qwen  - 搜索模型 / Search models[/dim]")
    click.echo("[dim]  modelpick list         - 列出所有模型 / List all models[/dim]")
    click.echo("[dim]  modelpick export -f json - 导出结果 / Export results[/dim]")
    click.echo("[dim]  modelpick benchmark     - 基准测试排行 / Benchmark rankings[/dim]")


if __name__ == "__main__":
    main()

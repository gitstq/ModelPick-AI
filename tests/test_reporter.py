# -*- coding: utf-8 -*-
"""
报告导出模块测试 / Report Export Module Tests

测试JSON、Markdown、CSV格式导出功能。
Test JSON, Markdown, CSV format export functionality.
"""

import unittest
import json
import csv
import io
import os
import tempfile
from modelpick_ai.database import ModelDatabase
from modelpick_ai.detector import HardwareInfo
from modelpick_ai.recommender import Recommender
from modelpick_ai.reporter import ReportExporter


class TestReportExporter(unittest.TestCase):
    """报告导出器测试 / Report exporter tests"""

    @classmethod
    def setUpClass(cls) -> None:
        """初始化共享测试数据 / Initialize shared test data"""
        cls.db = ModelDatabase()
        hw = HardwareInfo()
        hw.cpu_count = 8
        hw.cpu_arch = "x86_64"
        hw.cpu_model = "Test CPU"
        hw.ram_total_gb = 16.0
        hw.ram_available_gb = 12.0
        hw.disk_total_gb = 500.0
        hw.disk_free_gb = 200.0
        hw.os_name = "Linux"
        hw.os_version = "Test"
        hw.python_version = "3.10.0"
        hw.gpus = [{"vendor": "NVIDIA", "model": "Test GPU", "vram_gb": 8.0}]

        recommender = Recommender(cls.db, hw)
        cls.results = recommender.recommend(top_n=5)
        cls.hw = hw

    def test_export_json(self) -> None:
        """测试JSON导出 / Test JSON export"""
        exporter = ReportExporter(self.hw)
        json_str = exporter.export_json(self.results)

        # 验证是有效JSON / Verify valid JSON
        data = json.loads(json_str)
        self.assertIn("hardware_info", data)
        self.assertIn("recommendations", data)
        self.assertEqual(len(data["recommendations"]), len(self.results))

        # 验证推荐结果字段 / Verify recommendation result fields
        first = data["recommendations"][0]
        self.assertIn("model_id", first)
        self.assertIn("overall_score", first)
        self.assertIn("compatibility_score", first)

    def test_export_json_to_file(self) -> None:
        """测试JSON导出到文件 / Test JSON export to file"""
        exporter = ReportExporter(self.hw)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            exporter.export_json(self.results, temp_path)
            with open(temp_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIn("hardware_info", data)
            self.assertIn("recommendations", data)
        finally:
            os.unlink(temp_path)

    def test_export_markdown(self) -> None:
        """测试Markdown导出 / Test Markdown export"""
        exporter = ReportExporter(self.hw)
        md_str = exporter.export_markdown(self.results)

        # 验证Markdown内容 / Verify Markdown content
        self.assertIn("# ModelPick-AI", md_str)
        self.assertIn("## 硬件配置", md_str)
        self.assertIn("## 推荐模型", md_str)
        self.assertIn("## 模型详情", md_str)

    def test_export_markdown_to_file(self) -> None:
        """测试Markdown导出到文件 / Test Markdown export to file"""
        exporter = ReportExporter(self.hw)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            temp_path = f.name

        try:
            exporter.export_markdown(self.results, temp_path)
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("ModelPick-AI", content)
        finally:
            os.unlink(temp_path)

    def test_export_csv(self) -> None:
        """测试CSV导出 / Test CSV export"""
        exporter = ReportExporter(self.hw)
        csv_str = exporter.export_csv(self.results)

        # 验证CSV格式 / Verify CSV format
        reader = csv.reader(io.StringIO(csv_str))
        rows = list(reader)
        self.assertGreater(len(rows), 1)  # 至少有表头 + 数据行 / At least header + data rows

        # 验证表头 / Verify header
        header = rows[0]
        self.assertIn("Model ID", header)
        self.assertIn("Overall Score", header)
        self.assertIn("Compatibility Score", header)

    def test_export_csv_to_file(self) -> None:
        """测试CSV导出到文件 / Test CSV export to file"""
        exporter = ReportExporter(self.hw)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            exporter.export_csv(self.results, temp_path)
            with open(temp_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
            self.assertGreater(len(rows), 1)
        finally:
            os.unlink(temp_path)

    def test_export_generic_json(self) -> None:
        """测试通用导出方法(JSON) / Test generic export method (JSON)"""
        exporter = ReportExporter(self.hw)
        result = exporter.export(self.results, "json")
        data = json.loads(result)
        self.assertIn("recommendations", data)

    def test_export_generic_markdown(self) -> None:
        """测试通用导出方法(Markdown) / Test generic export method (Markdown)"""
        exporter = ReportExporter(self.hw)
        result = exporter.export(self.results, "markdown")
        self.assertIn("ModelPick-AI", result)

    def test_export_generic_md(self) -> None:
        """测试通用导出方法(md别名) / Test generic export method (md alias)"""
        exporter = ReportExporter(self.hw)
        result = exporter.export(self.results, "md")
        self.assertIn("ModelPick-AI", result)

    def test_export_generic_csv(self) -> None:
        """测试通用导出方法(CSV) / Test generic export method (CSV)"""
        exporter = ReportExporter(self.hw)
        result = exporter.export(self.results, "csv")
        self.assertIn("Model ID", result)

    def test_export_unsupported_format(self) -> None:
        """测试不支持的格式 / Test unsupported format"""
        exporter = ReportExporter(self.hw)
        with self.assertRaises(ValueError):
            exporter.export(self.results, "xml")

    def test_export_empty_results(self) -> None:
        """测试空结果导出 / Test empty results export"""
        exporter = ReportExporter(self.hw)
        json_str = exporter.export_json([])
        data = json.loads(json_str)
        self.assertEqual(data["total_count"], 0)
        self.assertEqual(data["recommendations"], [])


if __name__ == "__main__":
    unittest.main()

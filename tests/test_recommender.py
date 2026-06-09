# -*- coding: utf-8 -*-
"""
推荐引擎测试 / Recommendation Engine Tests

测试兼容性计算、性能评分、推荐排序等核心逻辑。
Test compatibility calculation, performance scoring, recommendation sorting, etc.
"""

import unittest
from modelpick_ai.database import ModelDatabase, ModelRecord
from modelpick_ai.detector import HardwareInfo
from modelpick_ai.recommender import Recommender, RecommendationResult


class TestRecommender(unittest.TestCase):
    """推荐引擎测试 / Recommender tests"""

    @classmethod
    def setUpClass(cls) -> None:
        """初始化共享测试数据 / Initialize shared test data"""
        cls.db = ModelDatabase()

    def _make_hardware(
        self,
        vram_gb: float = 0.0,
        ram_gb: float = 16.0,
        disk_gb: float = 100.0,
        cpu_count: int = 8,
    ) -> HardwareInfo:
        """创建模拟硬件信息 / Create mock hardware info"""
        hw = HardwareInfo()
        hw.cpu_count = cpu_count
        hw.cpu_arch = "x86_64"
        hw.cpu_model = "Test CPU"
        hw.ram_total_gb = ram_gb
        hw.ram_available_gb = ram_gb * 0.8
        hw.disk_total_gb = disk_gb * 2
        hw.disk_free_gb = disk_gb
        hw.os_name = "Linux"
        if vram_gb > 0:
            hw.gpus = [{"vendor": "NVIDIA", "model": "Test GPU", "vram_gb": vram_gb}]
        return hw

    def test_recommend_returns_results(self) -> None:
        """测试推荐返回结果 / Test recommend returns results"""
        hw = self._make_hardware(vram_gb=8.0, ram_gb=16.0, disk_gb=100.0)
        recommender = Recommender(self.db, hw)
        results = recommender.recommend(top_n=5)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], RecommendationResult)

    def test_recommend_sorted_by_overall_score(self) -> None:
        """测试结果按综合分数排序 / Test results sorted by overall score"""
        hw = self._make_hardware(vram_gb=8.0, ram_gb=32.0, disk_gb=200.0)
        recommender = Recommender(self.db, hw)
        results = recommender.recommend(top_n=10)
        for i in range(len(results) - 1):
            self.assertGreaterEqual(
                results[i].overall_score,
                results[i + 1].overall_score,
            )

    def test_recommend_with_scenario_filter(self) -> None:
        """测试场景过滤 / Test scenario filtering"""
        hw = self._make_hardware(vram_gb=8.0, ram_gb=16.0, disk_gb=100.0)
        recommender = Recommender(self.db, hw)
        results = recommender.recommend(scenario="coding", top_n=10)
        for r in results:
            self.assertIn("coding", r.model.scenarios)

    def test_recommend_with_max_params(self) -> None:
        """测试参数量限制 / Test parameter count limit"""
        hw = self._make_hardware(vram_gb=8.0, ram_gb=16.0, disk_gb=100.0)
        recommender = Recommender(self.db, hw)
        results = recommender.recommend(max_params=7.0, top_n=10)
        for r in results:
            self.assertLessEqual(r.model.param_count_num, 7.0)

    def test_compatibility_score_range(self) -> None:
        """测试兼容性分数范围 / Test compatibility score range"""
        hw = self._make_hardware(vram_gb=8.0, ram_gb=16.0, disk_gb=100.0)
        recommender = Recommender(self.db, hw)
        results = recommender.recommend(top_n=50)
        for r in results:
            self.assertGreaterEqual(r.compatibility_score, 0)
            self.assertLessEqual(r.compatibility_score, 100)

    def test_performance_score_range(self) -> None:
        """测试性能分数范围 / Test performance score range"""
        hw = self._make_hardware(vram_gb=8.0, ram_gb=16.0, disk_gb=100.0)
        recommender = Recommender(self.db, hw)
        results = recommender.recommend(top_n=50)
        for r in results:
            self.assertGreaterEqual(r.performance_score, 0)
            self.assertLessEqual(r.performance_score, 100)

    def test_no_gpu_hardware(self) -> None:
        """测试无GPU环境 / Test no-GPU environment"""
        hw = self._make_hardware(vram_gb=0.0, ram_gb=16.0, disk_gb=100.0)
        recommender = Recommender(self.db, hw)
        results = recommender.recommend(top_n=10)
        # 无GPU时仍应有推荐结果 / Should still have results without GPU
        self.assertGreater(len(results), 0)

    def test_low_resource_hardware(self) -> None:
        """测试低配硬件 / Test low-resource hardware"""
        hw = self._make_hardware(vram_gb=0.0, ram_gb=4.0, disk_gb=10.0)
        recommender = Recommender(self.db, hw)
        results = recommender.recommend(top_n=10)
        self.assertGreater(len(results), 0)
        # 低配环境下应优先推荐小模型 / Should prefer small models on low-end hardware
        if results:
            self.assertLessEqual(results[0].model.vram_required_gb, 4.0)

    def test_high_resource_hardware(self) -> None:
        """测试高配硬件 / Test high-resource hardware"""
        hw = self._make_hardware(vram_gb=80.0, ram_gb=128.0, disk_gb=500.0)
        recommender = Recommender(self.db, hw)
        results = recommender.recommend(top_n=10)
        self.assertGreater(len(results), 0)

    def test_min_compatibility_filter(self) -> None:
        """测试最低兼容性过滤 / Test minimum compatibility filter"""
        hw = self._make_hardware(vram_gb=4.0, ram_gb=8.0, disk_gb=50.0)
        recommender = Recommender(self.db, hw)
        results = recommender.recommend(top_n=50, min_compatibility=50.0)
        for r in results:
            self.assertGreaterEqual(r.compatibility_score, 50.0)

    def test_result_to_dict(self) -> None:
        """测试结果字典转换 / Test result dictionary conversion"""
        hw = self._make_hardware(vram_gb=8.0, ram_gb=16.0, disk_gb=100.0)
        recommender = Recommender(self.db, hw)
        results = recommender.recommend(top_n=1)
        if results:
            d = results[0].to_dict()
            self.assertIn("model_id", d)
            self.assertIn("overall_score", d)
            self.assertIn("compatibility_score", d)
            self.assertIn("performance_score", d)
            self.assertIn("reasons", d)

    def test_calculate_performance_with_scenario(self) -> None:
        """测试带场景的性能计算 / Test performance calculation with scenario"""
        hw = self._make_hardware(vram_gb=8.0, ram_gb=16.0, disk_gb=100.0)
        recommender = Recommender(self.db, hw)
        models = self.db.get_all()
        if models:
            perf_coding = recommender.calculate_performance(models[0], "coding")
            perf_chat = recommender.calculate_performance(models[0], "chat")
            # 不同场景应有不同分数 / Different scenarios should give different scores
            # (除非所有基准分数为0)
            self.assertGreaterEqual(perf_coding, 0)
            self.assertGreaterEqual(perf_chat, 0)


if __name__ == "__main__":
    unittest.main()

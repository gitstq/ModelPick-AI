# -*- coding: utf-8 -*-
"""
硬件检测模块测试 / Hardware Detection Module Tests

测试CPU、GPU、内存、磁盘检测功能，以及HardwareInfo数据类。
Test CPU, GPU, RAM, disk detection functionality, and HardwareInfo data class.
"""

import unittest
from unittest.mock import patch, MagicMock
from modelpick_ai.detector import HardwareDetector, HardwareInfo, detect_hardware


class TestHardwareInfo(unittest.TestCase):
    """HardwareInfo数据类测试 / HardwareInfo data class tests"""

    def test_init_defaults(self) -> None:
        """测试默认初始化值 / Test default initialization values"""
        info = HardwareInfo()
        self.assertEqual(info.cpu_count, 0)
        self.assertEqual(info.cpu_arch, "")
        self.assertEqual(info.cpu_model, "")
        self.assertEqual(info.gpus, [])
        self.assertEqual(info.ram_total_gb, 0.0)
        self.assertEqual(info.ram_available_gb, 0.0)
        self.assertEqual(info.disk_free_gb, 0.0)
        self.assertEqual(info.disk_total_gb, 0.0)
        self.assertEqual(info.os_name, "")
        self.assertEqual(info.os_version, "")
        self.assertEqual(info.python_version, "")

    def test_to_dict(self) -> None:
        """测试字典转换 / Test dictionary conversion"""
        info = HardwareInfo()
        info.cpu_count = 8
        info.cpu_arch = "x86_64"
        info.cpu_model = "Test CPU"
        info.ram_total_gb = 16.0
        info.disk_free_gb = 100.0
        info.os_name = "Linux"

        d = info.to_dict()
        self.assertIn("cpu", d)
        self.assertEqual(d["cpu"]["count"], 8)
        self.assertEqual(d["cpu"]["architecture"], "x86_64")
        self.assertIn("gpu", d)
        self.assertIn("ram", d)
        self.assertEqual(d["ram"]["total_gb"], 16.0)
        self.assertIn("disk", d)
        self.assertEqual(d["disk"]["free_gb"], 100.0)
        self.assertIn("system", d)
        self.assertEqual(d["system"]["os"], "Linux")

    def test_get_total_vram_gb_empty(self) -> None:
        """测试无GPU时的总显存 / Test total VRAM with no GPUs"""
        info = HardwareInfo()
        self.assertEqual(info.get_total_vram_gb(), 0.0)

    def test_get_total_vram_gb_multiple(self) -> None:
        """测试多GPU总显存 / Test total VRAM with multiple GPUs"""
        info = HardwareInfo()
        info.gpus = [
            {"vram_gb": 8.0},
            {"vram_gb": 12.0},
        ]
        self.assertEqual(info.get_total_vram_gb(), 20.0)

    def test_get_max_vram_gb(self) -> None:
        """测试最大单GPU显存 / Test max single GPU VRAM"""
        info = HardwareInfo()
        info.gpus = [
            {"vram_gb": 8.0},
            {"vram_gb": 12.0},
        ]
        self.assertEqual(info.get_max_vram_gb(), 12.0)

    def test_get_max_vram_gb_empty(self) -> None:
        """测试无GPU时最大显存 / Test max VRAM with no GPUs"""
        info = HardwareInfo()
        self.assertEqual(info.get_max_vram_gb(), 0.0)


class TestHardwareDetector(unittest.TestCase):
    """HardwareDetector测试 / HardwareDetector tests"""

    def test_detect_all_returns_hardware_info(self) -> None:
        """测试detect_all返回HardwareInfo / Test detect_all returns HardwareInfo"""
        detector = HardwareDetector()
        info = detector.detect_all()
        self.assertIsInstance(info, HardwareInfo)

    def test_detect_system(self) -> None:
        """测试系统检测 / Test system detection"""
        detector = HardwareDetector()
        detector._detect_system()
        self.assertNotEqual(detector.info.os_name, "")
        self.assertNotEqual(detector.info.python_version, "")

    def test_detect_cpu(self) -> None:
        """测试CPU检测 / Test CPU detection"""
        detector = HardwareDetector()
        detector._detect_cpu()
        # 至少应获取到核心数 / Should at least get core count
        self.assertGreaterEqual(detector.info.cpu_count, 0)
        self.assertNotEqual(detector.info.cpu_arch, "")

    def test_detect_disk(self) -> None:
        """测试磁盘检测 / Test disk detection"""
        detector = HardwareDetector()
        detector._detect_disk()
        self.assertGreater(detector.info.disk_total_gb, 0)
        self.assertGreater(detector.info.disk_free_gb, 0)

    @patch("modelpick_ai.detector.subprocess.run")
    def test_detect_nvidia_gpu_success(self, mock_run: MagicMock) -> None:
        """测试NVIDIA GPU检测成功 / Test NVIDIA GPU detection success"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="NVIDIA GeForce RTX 4090, 24564, 535.129.03\n"
        )
        detector = HardwareDetector()
        detector._detect_nvidia_gpu()
        self.assertEqual(len(detector.info.gpus), 1)
        self.assertEqual(detector.info.gpus[0]["vendor"], "NVIDIA")
        self.assertIn("RTX 4090", detector.info.gpus[0]["model"])
        self.assertAlmostEqual(detector.info.gpus[0]["vram_gb"], 24.0, places=1)

    @patch("modelpick_ai.detector.subprocess.run", side_effect=FileNotFoundError)
    def test_detect_nvidia_gpu_not_found(self, mock_run: MagicMock) -> None:
        """测试NVIDIA GPU未安装nvidia-smi / Test nvidia-smi not installed"""
        detector = HardwareDetector()
        detector._detect_nvidia_gpu()
        self.assertEqual(len(detector.info.gpus), 0)

    @patch("modelpick_ai.detector.subprocess.run", side_effect=FileNotFoundError)
    def test_detect_amd_gpu_not_found(self, mock_run: MagicMock) -> None:
        """测试AMD GPU检测失败 / Test AMD GPU detection failure"""
        detector = HardwareDetector()
        detector._detect_amd_gpu()
        self.assertEqual(len(detector.info.gpus), 0)

    def test_detect_hardware_convenience(self) -> None:
        """测试便捷函数 / Test convenience function"""
        info = detect_hardware()
        self.assertIsInstance(info, HardwareInfo)
        self.assertNotEqual(info.os_name, "")
        self.assertGreaterEqual(info.cpu_count, 0)


if __name__ == "__main__":
    unittest.main()

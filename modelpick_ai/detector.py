# -*- coding: utf-8 -*-
"""
硬件检测模块 / Hardware Detection Module

自动检测系统硬件配置，包括CPU、GPU、内存和磁盘空间。
Automatically detect system hardware configuration including CPU, GPU, RAM, and disk space.
支持跨平台检测（Linux、macOS、Windows），检测失败时优雅降级。
Supports cross-platform detection (Linux, macOS, Windows) with graceful degradation on failure.
"""

import os
import platform
import subprocess
import re
import json
import shutil
from typing import Dict, List, Optional, Any


class HardwareInfo:
    """硬件信息数据类 / Hardware information data class"""

    def __init__(self) -> None:
        # CPU信息 / CPU information
        self.cpu_count: int = 0  # 逻辑CPU核心数 / Logical CPU core count
        self.cpu_arch: str = ""  # CPU架构 / CPU architecture
        self.cpu_model: str = ""  # CPU型号 / CPU model name

        # GPU信息 / GPU information
        self.gpus: List[Dict[str, Any]] = []  # GPU列表 / GPU list

        # 内存信息 / Memory information
        self.ram_total_gb: float = 0.0  # 总内存(GB) / Total RAM in GB
        self.ram_available_gb: float = 0.0  # 可用内存(GB) / Available RAM in GB

        # 磁盘信息 / Disk information
        self.disk_free_gb: float = 0.0  # 可用磁盘空间(GB) / Free disk space in GB
        self.disk_total_gb: float = 0.0  # 总磁盘空间(GB) / Total disk space in GB

        # 系统信息 / System information
        self.os_name: str = ""  # 操作系统名称 / OS name
        self.os_version: str = ""  # 操作系统版本 / OS version
        self.python_version: str = ""  # Python版本 / Python version

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 / Convert to dictionary"""
        return {
            "cpu": {
                "count": self.cpu_count,
                "architecture": self.cpu_arch,
                "model": self.cpu_model,
            },
            "gpu": self.gpus,
            "ram": {
                "total_gb": round(self.ram_total_gb, 2),
                "available_gb": round(self.ram_available_gb, 2),
            },
            "disk": {
                "total_gb": round(self.disk_total_gb, 2),
                "free_gb": round(self.disk_free_gb, 2),
            },
            "system": {
                "os": self.os_name,
                "os_version": self.os_version,
                "python_version": self.python_version,
            },
        }

    def get_total_vram_gb(self) -> float:
        """获取所有GPU的总显存(GB) / Get total VRAM across all GPUs in GB"""
        return sum(gpu.get("vram_gb", 0) for gpu in self.gpus)

    def get_max_vram_gb(self) -> float:
        """获取最大单GPU显存(GB) / Get max single GPU VRAM in GB"""
        if not self.gpus:
            return 0.0
        return max(gpu.get("vram_gb", 0) for gpu in self.gpus)


class HardwareDetector:
    """硬件检测器 / Hardware detector

    自动检测系统硬件配置，支持NVIDIA/AMD/Intel/Apple Silicon GPU。
    Automatically detect system hardware, supporting NVIDIA/AMD/Intel/Apple Silicon GPUs.
    """

    def __init__(self) -> None:
        self.info = HardwareInfo()

    def detect_all(self) -> HardwareInfo:
        """执行全部硬件检测 / Run all hardware detection"""
        self._detect_system()
        self._detect_cpu()
        self._detect_ram()
        self._detect_disk()
        self._detect_gpu()
        return self.info

    def _detect_system(self) -> None:
        """检测操作系统信息 / Detect OS information"""
        try:
            self.info.os_name = platform.system()
            self.info.os_version = platform.version()
            self.info.python_version = platform.python_version()
        except Exception:
            # 降级处理：设置默认值 / Graceful degradation: set defaults
            self.info.os_name = "Unknown"
            self.info.os_version = "Unknown"
            self.info.python_version = platform.python_version()

    def _detect_cpu(self) -> None:
        """检测CPU信息 / Detect CPU information"""
        try:
            self.info.cpu_count = os.cpu_count() or 0
            self.info.cpu_arch = platform.machine()

            # 根据平台获取CPU型号 / Get CPU model based on platform
            system = platform.system()
            if system == "Linux":
                self._detect_cpu_linux()
            elif system == "Darwin":
                self._detect_cpu_macos()
            elif system == "Windows":
                self._detect_cpu_windows()
        except Exception:
            # 降级：至少获取核心数 / Graceful degradation: at least get core count
            self.info.cpu_count = os.cpu_count() or 0
            self.info.cpu_arch = platform.machine()

    def _detect_cpu_linux(self) -> None:
        """Linux平台CPU检测 / CPU detection on Linux"""
        try:
            with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                content = f.read()
                # 提取CPU型号 / Extract CPU model name
                match = re.search(r"model name\s*:\s*(.+)", content)
                if match:
                    self.info.cpu_model = match.group(1).strip()
        except (FileNotFoundError, PermissionError):
            pass

    def _detect_cpu_macos(self) -> None:
        """macOS平台CPU检测 / CPU detection on macOS"""
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self.info.cpu_model = result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    def _detect_cpu_windows(self) -> None:
        """Windows平台CPU检测 / CPU detection on Windows"""
        try:
            result = subprocess.run(
                ["wmic", "cpu", "get", "name"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:
                    self.info.cpu_model = lines[1].strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    def _detect_ram(self) -> None:
        """检测内存信息 / Detect RAM information"""
        try:
            system = platform.system()
            if system == "Linux":
                self._detect_ram_linux()
            elif system == "Darwin":
                self._detect_ram_macos()
            elif system == "Windows":
                self._detect_ram_windows()
        except Exception:
            pass

    def _detect_ram_linux(self) -> None:
        """Linux平台内存检测 / RAM detection on Linux"""
        try:
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                content = f.read()

            # 解析总内存 / Parse total memory
            match = re.search(r"MemTotal:\s+(\d+)\s+kB", content)
            if match:
                self.info.ram_total_gb = int(match.group(1)) / (1024 * 1024)

            # 解析可用内存 / Parse available memory
            match = re.search(r"MemAvailable:\s+(\d+)\s+kB", content)
            if match:
                self.info.ram_available_gb = int(match.group(1)) / (1024 * 1024)
            else:
                # 旧内核可能没有MemAvailable / Older kernels may not have MemAvailable
                match = re.search(r"MemFree:\s+(\d+)\s+kB", content)
                if match:
                    self.info.ram_available_gb = int(match.group(1)) / (1024 * 1024)
        except (FileNotFoundError, PermissionError):
            pass

    def _detect_ram_macos(self) -> None:
        """macOS平台内存检测 / RAM detection on macOS"""
        try:
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                self.info.ram_total_gb = int(result.stdout.strip()) / (1024 ** 3)

            # macOS可用内存通过vm_stat获取 / Get available memory via vm_stat on macOS
            result = subprocess.run(
                ["vm_stat"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                match = re.search(r"Pages free:\s+(\d+)", result.stdout)
                if match:
                    free_pages = int(match.group(1))
                    self.info.ram_available_gb = (free_pages * 4096) / (1024 ** 3)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    def _detect_ram_windows(self) -> None:
        """Windows平台内存检测 / RAM detection on Windows"""
        try:
            result = subprocess.run(
                ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:
                    parts = lines[1].strip().split()
                    if len(parts) >= 2:
                        self.info.ram_total_gb = int(parts[0]) / (1024 * 1024)
                        self.info.ram_available_gb = int(parts[1]) / (1024 * 1024)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    def _detect_disk(self) -> None:
        """检测磁盘空间 / Detect disk space"""
        try:
            # 检测当前工作目录所在磁盘 / Detect disk of current working directory
            usage = shutil.disk_usage(os.getcwd())
            self.info.disk_total_gb = usage.total / (1024 ** 3)
            self.info.disk_free_gb = usage.free / (1024 ** 3)
        except Exception:
            pass

    def _detect_gpu(self) -> None:
        """检测GPU信息 / Detect GPU information

        按优先级尝试：NVIDIA > AMD > Intel > Apple Silicon
        Try in priority order: NVIDIA > AMD > Intel > Apple Silicon
        """
        self._detect_nvidia_gpu()
        if not self.info.gpus:
            self._detect_amd_gpu()
        if not self.info.gpus:
            self._detect_intel_gpu()
        if not self.info.gpus:
            self._detect_apple_silicon_gpu()

    def _detect_nvidia_gpu(self) -> None:
        """检测NVIDIA GPU / Detect NVIDIA GPU"""
        try:
            # 尝试使用nvidia-smi / Try using nvidia-smi
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if not line.strip():
                        continue
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 3:
                        self.info.gpus.append({
                            "vendor": "NVIDIA",
                            "model": parts[0],
                            "vram_gb": float(parts[1]) / 1024,  # MB to GB
                            "driver_version": parts[2],
                        })
        except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
            pass

    def _detect_amd_gpu(self) -> None:
        """检测AMD GPU / Detect AMD GPU"""
        try:
            # 尝试使用rocm-smi / Try using rocm-smi
            result = subprocess.run(
                ["rocm-smi", "--showproductname", "--showmeminfo", "vram"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                output = result.stdout
                # 解析GPU型号 / Parse GPU model
                model_match = re.search(r"GPU\s*\d+.*?:\s*(.+?)(?:\n|$)", output)
                # 解析显存 / Parse VRAM
                vram_match = re.search(r"VRAM.*?(\d+)\s*(MB|GB)", output, re.IGNORECASE)

                if model_match:
                    vram_gb = 0.0
                    if vram_match:
                        vram_val = float(vram_match.group(1))
                        unit = vram_match.group(2).upper()
                        vram_gb = vram_val / 1024 if unit == "MB" else vram_val

                    self.info.gpus.append({
                        "vendor": "AMD",
                        "model": model_match.group(1).strip(),
                        "vram_gb": vram_gb,
                        "driver_version": "ROCm",
                    })
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    def _detect_intel_gpu(self) -> None:
        """检测Intel GPU / Detect Intel GPU"""
        try:
            # 在Linux上检查Intel GPU / Check Intel GPU on Linux
            if platform.system() == "Linux":
                result = subprocess.run(
                    ["intel_gpu_top", "-l", "-1"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    self.info.gpus.append({
                        "vendor": "Intel",
                        "model": "Intel Integrated/Discrete GPU",
                        "vram_gb": 0.0,  # 集显通常共享内存 / Integrated usually shares memory
                        "driver_version": "Intel",
                    })
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    def _detect_apple_silicon_gpu(self) -> None:
        """检测Apple Silicon GPU / Detect Apple Silicon GPU"""
        try:
            if platform.system() == "Darwin":
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType", "-json"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    displays = data.get("SPDisplaysDataType", [])
                    for display in displays:
                        chip_name = display.get("chipset-model", "")
                        vram_str = display.get("vram", "")
                        # Apple Silicon统一内存架构 / Apple Silicon unified memory
                        vram_gb = 0.0
                        match = re.search(r"(\d+)\s*(GB|MB)", str(vram_str), re.IGNORECASE)
                        if match:
                            vram_val = float(match.group(1))
                            unit = match.group(2).upper()
                            vram_gb = vram_val / 1024 if unit == "MB" else vram_val

                        self.info.gpus.append({
                            "vendor": "Apple",
                            "model": chip_name,
                            "vram_gb": vram_gb,
                            "driver_version": "Metal",
                        })
        except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
            pass


def detect_hardware() -> HardwareInfo:
    """便捷函数：检测硬件并返回信息 / Convenience function: detect hardware and return info"""
    detector = HardwareDetector()
    return detector.detect_all()

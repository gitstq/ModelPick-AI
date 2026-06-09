# -*- coding: utf-8 -*-
"""
模块入口 / Module entry point

允许通过 `python -m modelpick_ai` 方式运行。
Allow running via `python -m modelpick_ai`.
"""

from modelpick_ai.cli import main, _run_default
import sys


if __name__ == "__main__":
    # 如果没有参数，运行默认模式 / If no arguments, run default mode
    if len(sys.argv) <= 1:
        _run_default()
    else:
        main()

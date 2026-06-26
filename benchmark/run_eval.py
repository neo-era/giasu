"""Chạy eval bộ chuẩn → báo cáo độ chính xác lớp kiểm chứng (NFR-01).

    python benchmark/run_eval.py            # ngưỡng mặc định 0.95
    BENCHMARK_THRESHOLD=0.98 python benchmark/run_eval.py

Thoát mã != 0 nếu độ chính xác dưới ngưỡng (dùng cho CI / cổng Go/No-Go).
"""

import os
import sys
from pathlib import Path

# Cho phép import package backend khi chạy từ gốc repo
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.benchmark.runner import chay_eval, load_dataset  # noqa: E402


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # tránh lỗi cp1252 trên Windows
    nguong = float(os.environ.get("BENCHMARK_THRESHOLD", "0.95"))
    report = chay_eval(load_dataset())
    print(f"Tổng: {report['tong']}  Khớp: {report['so_khop']}")
    print(f"Độ chính xác: {report['do_chinh_xac']:.2%}  (ngưỡng {nguong:.0%})")
    for d in report["sai_sot"]:
        print(f"  - SAI SÓT: {d}")
    if report["do_chinh_xac"] < nguong:
        print("KẾT QUẢ: DƯỚI NGƯỠNG ❌")
        return 1
    print("KẾT QUẢ: ĐẠT ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

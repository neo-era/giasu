import json
from pathlib import Path
from typing import Any

from app.models.enums import TrangThaiKiemChung
from app.verify import kiem_bien_doi, kiem_dao_ham, kiem_nghiem, kiem_tich_phan


def duong_dan_mac_dinh() -> Path:
    # app/benchmark/runner.py → parents[3] = <repo root>
    return Path(__file__).resolve().parents[3] / "benchmark" / "bo_chuan.json"


def load_dataset(path: Path | None = None) -> list[dict[str, Any]]:
    p = path or duong_dan_mac_dinh()
    return json.loads(p.read_text(encoding="utf-8"))


def _verdict(item: dict[str, Any]) -> str:
    loai = item["loai"]
    if loai == "bien_doi":
        vr = kiem_bien_doi(item["lhs"], item["rhs"])
    elif loai == "nghiem":
        vr = kiem_nghiem(item["pt"], item["nghiem"])
    elif loai == "dao_ham":
        vr = kiem_dao_ham(item["bieu_thuc"], item["dao_ham"])
    elif loai == "tich_phan":
        vr = kiem_tich_phan(
            item["bieu_thuc"],
            item["ket_qua"],
            can_duoi=item.get("can_duoi"),
            can_tren=item.get("can_tren"),
        )
    else:
        raise ValueError(f"Loại không hỗ trợ: {loai}")

    if vr.trang_thai == TrangThaiKiemChung.dung:
        return "dung"
    if vr.trang_thai == TrangThaiKiemChung.sai:
        return "sai"
    return "khac"


def chay_eval(items: list[dict[str, Any]]) -> dict[str, Any]:
    tong = len(items)
    so_khop = 0
    sai_sot: list[str] = []
    for it in items:
        verdict = _verdict(it)
        if verdict == it["ky_vong"]:
            so_khop += 1
        else:
            sai_sot.append(f"{it['id']}: kỳ vọng={it['ky_vong']} thực tế={verdict}")
    return {
        "tong": tong,
        "so_khop": so_khop,
        "do_chinh_xac": (so_khop / tong) if tong else 0.0,
        "sai_sot": sai_sot,
    }

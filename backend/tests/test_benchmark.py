from app.benchmark.runner import chay_eval, load_dataset


def test_load_dataset_co_du_lieu():
    items = load_dataset()
    assert len(items) >= 5


def test_eval_do_chinh_xac_tuyet_doi():
    # Bộ chuẩn được thiết kế để lớp kiểm chứng phán đúng 100%
    report = chay_eval(load_dataset())
    assert report["do_chinh_xac"] == 1.0, report["sai_sot"]


def test_gai_loi_giai_sai_bi_bat():
    # Mọi item ky_vong="sai" phải bị lớp kiểm chứng bắt là 'sai'
    items = [i for i in load_dataset() if i["ky_vong"] == "sai"]
    assert items
    report = chay_eval(items)
    assert report["so_khop"] == len(items)

from app.llm.tiers import BacModel
from app.models.enums import DoKho, PhanKhuc
from app.router import (
    PERSONA_GIAO_SU_NGO,
    PERSONA_THAY_AN,
    LLMRouter,
    RoutingPolicy,
    RoutingRequest,
    uoc_tinh_chi_phi,
)


def test_dai_tra_mac_dinh_can_bang():
    d = LLMRouter().route(RoutingRequest(PhanKhuc.dai_tra, do_kho=DoKho.van_dung))
    assert d.bac == BacModel.can_bang
    assert d.persona == PERSONA_THAY_AN
    assert d.cross_check is False
    assert d.can_ocr is False


def test_dai_tra_cau_don_gian_re():
    d = LLMRouter().route(RoutingRequest(PhanKhuc.dai_tra, do_kho=DoKho.nhan_biet))
    assert d.bac == BacModel.re


def test_dai_tra_free_ep_re():
    # Câu khó nhưng gói free → vẫn bậc rẻ (NFR-40)
    d = LLMRouter().route(
        RoutingRequest(PhanKhuc.dai_tra, do_kho=DoKho.van_dung_cao, is_free_plan=True)
    )
    assert d.bac == BacModel.re


def test_co_anh_can_ocr():
    d = LLMRouter().route(RoutingRequest(PhanKhuc.dai_tra, has_image=True))
    assert d.can_ocr is True
    assert d.ocr_bac == BacModel.vision


def test_tinh_hoa_reasoning_va_persona():
    d = LLMRouter().route(RoutingRequest(PhanKhuc.tinh_hoa, do_kho=DoKho.thong_hieu))
    assert d.bac == BacModel.reasoning
    assert d.persona == PERSONA_GIAO_SU_NGO
    assert d.cross_check is False  # không quan trọng → chưa cross-check


def test_tinh_hoa_quan_trong_cross_check():
    d = LLMRouter().route(RoutingRequest(PhanKhuc.tinh_hoa, is_important=True))
    assert d.cross_check is True
    assert d.so_model_cross_check == 2


def test_tinh_hoa_do_kho_cao_cross_check():
    d = LLMRouter().route(RoutingRequest(PhanKhuc.tinh_hoa, do_kho=DoKho.van_dung_cao))
    assert d.cross_check is True


def test_doi_threshold_qua_config():
    # Tắt 'free ép rẻ' → gói free + câu khó dùng bậc cân bằng
    policy = RoutingPolicy(free_forces_cheap=False, crosscheck_models=3)
    r = LLMRouter(policy)
    d = r.route(RoutingRequest(PhanKhuc.dai_tra, do_kho=DoKho.van_dung, is_free_plan=True))
    assert d.bac == BacModel.can_bang
    # crosscheck_models đổi qua config
    d2 = r.route(RoutingRequest(PhanKhuc.tinh_hoa, is_important=True))
    assert d2.so_model_cross_check == 3


def test_uoc_tinh_chi_phi_reasoning_dat_hon():
    re_cost = uoc_tinh_chi_phi(BacModel.re, 1000, 1000)
    reasoning_cost = uoc_tinh_chi_phi(BacModel.reasoning, 1000, 1000)
    assert reasoning_cost > re_cost > 0

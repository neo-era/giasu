import pytest

from app.personas import PersonaLoader, PromptError


def test_nap_thay_an_va_bien_level():
    loader = PersonaLoader()
    tpl = loader.load("thay_an")
    assert tpl.version == 1
    assert "[LEVEL]" in tpl.text
    assert tpl.required_vars == {"LEVEL"}


def test_render_inject_level():
    loader = PersonaLoader()
    out = loader.render("thay_an", LEVEL="yeu")
    assert "[LEVEL]" not in out  # đã thay
    assert "yeu" in out
    assert "Thầy An" in out


def test_thieu_bien_bao_loi_ro_rang():
    loader = PersonaLoader()
    with pytest.raises(PromptError) as exc:
        loader.render("thay_an")  # quên LEVEL
    assert "LEVEL" in str(exc.value)


def test_prompt_khong_ton_tai():
    loader = PersonaLoader()
    with pytest.raises(PromptError):
        loader.load("khong_co_prompt_nay")


def test_cache_tra_ve_cung_doi_tuong():
    loader = PersonaLoader()
    assert loader.load("thay_an") is loader.load("thay_an")


def test_cac_persona_dang_dung_ton_tai():
    loader = PersonaLoader()
    for name in ("thay_an", "giao_su_ngo", "ocr"):
        assert loader.load(name).text  # nạp được, có nội dung

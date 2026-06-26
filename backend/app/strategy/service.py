from pydantic import BaseModel

from app.llm import BacModel, ChatMessage, LLMError
from app.llm.jsonout import extract_json
from app.llm.service import LLMService, get_llm_service
from app.personas import get_persona_loader


class HuongTiepCan(BaseModel):
    ten: str
    y_tuong: str
    khi_nao_phu_hop: str = ""
    do_kho_tuong_doi: str = ""


class StrategyTree(BaseModel):
    ban_chat: str = ""
    huong_tiep_can: list[HuongTiepCan] = []


def sinh_cay(de_latex: str, llm: LLMService | None = None) -> StrategyTree:
    svc = llm or get_llm_service()
    system = get_persona_loader().load("strategy_tree").text
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=de_latex),
    ]
    try:
        out = svc.complete(BacModel.reasoning, messages)
        data = extract_json(out.text)
    except LLMError:
        data = None
    if not isinstance(data, dict):
        return StrategyTree()
    huong = [
        HuongTiepCan(
            ten=str(h.get("ten", "")),
            y_tuong=str(h.get("y_tuong", "")),
            khi_nao_phu_hop=str(h.get("khi_nao_phu_hop", "")),
            do_kho_tuong_doi=str(h.get("do_kho_tuong_doi", "")),
        )
        for h in data.get("huong_tiep_can", [])
    ]
    return StrategyTree(ban_chat=str(data.get("ban_chat", "")), huong_tiep_can=huong)

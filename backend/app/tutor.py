"""Logic sư phạm dùng chung: chế độ trả lời gợi mở / lời giải đầy đủ.

Hiện thực nguyên tắc bất biến #1 (gợi mở, KHÔNG giải hộ mặc định) ở tầng
backend — độc lập với việc model có "ngoan" hay không. Cổng nỗ lực thật
(quyết định `da_qua_cong_no_luc`) sẽ do B14 tính.
"""

from app.models.enums import CheDoTraLoi, PhanKhuc

_GOI_Y = (
    "CHẾ ĐỘ TRẢ LỜI: chỉ đưa GỢI Ý hoặc câu hỏi dẫn dắt, tập trung MỘT bước mỗi "
    "lượt. TUYỆT ĐỐI KHÔNG trình bày lời giải đầy đủ hay đáp số cuối cùng."
)
_LOI_GIAI = (
    "CHẾ ĐỘ TRẢ LỜI: học sinh đã nỗ lực đủ hoặc yêu cầu rõ — được phép trình bày "
    "lời giải đầy đủ, giải thích từng bước rõ ràng."
)
_CHUA_QUA_CONG = (
    "CHẾ ĐỘ TRẢ LỜI: học sinh muốn xem lời giải nhưng CHƯA qua cổng nỗ lực — hãy "
    "tiếp tục gợi ý và khuyến khích em thử thêm; CHƯA trình bày lời giải đầy đủ."
)


def directive_che_do(che_do: CheDoTraLoi, da_qua_cong_no_luc: bool) -> str:
    if che_do == CheDoTraLoi.loi_giai_day_du:
        return _LOI_GIAI if da_qua_cong_no_luc else _CHUA_QUA_CONG
    return _GOI_Y


_PHAM_VI_DAI_TRA = (
    "PHẠM VI: chỉ hỗ trợ Toán/Lí THPT (lớp 10–12). Câu hỏi ngoài phạm vi: từ chối "
    "lịch sự và nhẹ nhàng kéo em về đúng môn."
)


def directive_pham_vi(phan_khuc: PhanKhuc) -> str:
    """Nhắc phạm vi cho đại trà (FR-M07). Tinh hoa đa môn → không giới hạn ở đây."""
    return _PHAM_VI_DAI_TRA if phan_khuc == PhanKhuc.dai_tra else ""

"use client";

import { useEffect, useState } from "react";

import { Math } from "@/components/Math";
import { ocrConfirm, ocrExtract, type OcrResult } from "@/lib/api";

export default function OcrPage() {
  const [token, setToken] = useState("");
  const [raw, setRaw] = useState("");
  const [result, setResult] = useState<OcrResult | null>(null);
  const [deLatex, setDeLatex] = useState("");
  const [daKiemTra, setDaKiemTra] = useState(false);
  const [status, setStatus] = useState("");

  useEffect(() => {
    setToken(localStorage.getItem("giasu_token") ?? "");
  }, []);

  async function extract() {
    setStatus("Đang nhận diện…");
    try {
      const r = await ocrExtract(token, { text: raw });
      setResult(r);
      setDeLatex(r.de_latex);
      setDaKiemTra(!r.can_xac_nhan_lai);
      setStatus("");
    } catch (e) {
      setStatus(String(e));
    }
  }

  async function dungDe() {
    if (!result) return;
    try {
      await ocrConfirm(token, {
        de_latex: deLatex,
        mon: result.mon,
        lop: result.lop,
        do_kho: result.do_kho,
        can_xac_nhan_lai: result.can_xac_nhan_lai,
        da_xac_nhan: daKiemTra,
      });
      setStatus("Đã lưu đề ✓");
    } catch (e) {
      setStatus(String(e));
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col gap-3 p-4">
      <h1 className="text-lg font-semibold">Số hóa đề (OCR → LaTeX)</h1>

      <input
        className="rounded border p-2 text-base"
        value={token}
        onChange={(e) => setToken(e.target.value)}
        placeholder="Token (dev)"
      />
      <textarea
        className="min-h-24 rounded border p-2 text-base"
        value={raw}
        onChange={(e) => setRaw(e.target.value)}
        placeholder="Dán đề (hoặc URL ảnh) để nhận diện…"
      />
      <button
        className="rounded bg-black p-3 text-base text-white disabled:opacity-50"
        onClick={extract}
        disabled={!token || !raw.trim()}
      >
        Nhận diện đề
      </button>

      {result && (
        <div className="flex flex-col gap-2 rounded border p-3">
          <div className="text-sm text-gray-500">
            Độ tin cậy OCR: {(result.ocr_tin_cay * 100).toFixed(0)}%
          </div>

          {result.can_xac_nhan_lai && (
            <div className="rounded bg-yellow-100 p-2 text-sm text-yellow-800">
              ⚠️ Đề chưa chắc chắn — hãy kiểm tra/sửa lại trước khi dùng.
            </div>
          )}

          <label className="text-sm text-gray-500">Đề (sửa nếu cần)</label>
          <textarea
            className="min-h-20 rounded border p-2 font-mono text-sm"
            value={deLatex}
            onChange={(e) => setDeLatex(e.target.value)}
          />

          <label className="text-sm text-gray-500">Xem trước</label>
          <Math className="block rounded bg-gray-50 p-3 text-base">{deLatex}</Math>

          {result.can_xac_nhan_lai && (
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={daKiemTra}
                onChange={(e) => setDaKiemTra(e.target.checked)}
              />
              Tôi đã kiểm tra và xác nhận đề đúng
            </label>
          )}

          <button
            className="rounded bg-black p-3 text-base text-white disabled:opacity-50"
            onClick={dungDe}
            disabled={result.can_xac_nhan_lai && !daKiemTra}
          >
            Dùng đề này
          </button>
        </div>
      )}

      {status && <p className="text-sm text-gray-600">{status}</p>}
    </main>
  );
}

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function getToken(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("giasu_token") ?? "";
}

export function setToken(token: string): void {
  localStorage.setItem("giasu_token", token);
}

export function clearToken(): void {
  localStorage.removeItem("giasu_token");
}

async function _detail(r: Response): Promise<string> {
  try {
    const d = await r.json();
    return typeof d.detail === "string" ? d.detail : `Lỗi ${r.status}`;
  } catch {
    return `Lỗi ${r.status}`;
  }
}

export async function login(dinhDanh: string, password: string): Promise<string> {
  const r = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dinh_danh: dinhDanh, password }),
  });
  if (!r.ok) throw new Error(await _detail(r));
  const data = await r.json();
  setToken(data.access_token);
  return data.access_token;
}

export async function register(
  email: string,
  password: string,
  phanKhuc = "dai_tra",
): Promise<{ otp_dev?: string }> {
  const r = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, phan_khuc: phanKhuc }),
  });
  if (!r.ok) throw new Error(await _detail(r));
  return r.json();
}

export async function verifyOtp(dinhDanh: string, ma: string): Promise<void> {
  const r = await fetch(`${API}/auth/verify-otp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dinh_danh: dinhDanh, ma }),
  });
  if (!r.ok) throw new Error(await _detail(r));
}

export type Conversation = {
  id: string;
  chu_de: string | null;
  phan_khuc: string;
};

export async function createConversation(
  token: string,
  chuDe?: string,
): Promise<Conversation> {
  const r = await fetch(`${API}/chat/conversations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ chu_de: chuDe }),
  });
  if (!r.ok) throw new Error(`Tạo hội thoại lỗi: ${r.status}`);
  return r.json();
}

export type OcrResult = {
  de_latex: string;
  mon: string;
  lop: number | null;
  phan_khuc_goi_y: string;
  do_kho: string | null;
  ocr_tin_cay: number;
  can_xac_nhan_lai: boolean;
};

export async function ocrExtract(
  token: string,
  input: { image?: string; text?: string },
): Promise<OcrResult> {
  const r = await fetch(`${API}/ocr/extract`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(input),
  });
  if (!r.ok) throw new Error(`OCR lỗi: ${r.status}`);
  return r.json();
}

export async function ocrConfirm(
  token: string,
  body: {
    de_latex: string;
    mon?: string;
    lop?: number | null;
    do_kho?: string | null;
    can_xac_nhan_lai: boolean;
    da_xac_nhan: boolean;
  },
): Promise<{ id: string; de_latex: string }> {
  const r = await fetch(`${API}/ocr/confirm`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });
  if (r.status === 409) throw new Error("Cần xác nhận/sửa đề trước khi dùng");
  if (!r.ok) throw new Error(`Xác nhận lỗi: ${r.status}`);
  return r.json();
}

/** Stream câu trả lời theo SSE; yield từng đoạn văn bản. */
export async function* streamMessage(
  token: string,
  convId: string,
  noiDung: string,
): AsyncGenerator<string> {
  const r = await fetch(`${API}/chat/conversations/${convId}/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ noi_dung: noiDung }),
  });
  if (!r.ok) throw new Error(await _detail(r));
  if (!r.body) throw new Error("Phản hồi không có stream");

  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const parts = buf.split("\n\n");
    buf = parts.pop() ?? "";
    for (const part of parts) {
      const line = part.trim();
      if (!line.startsWith("data:")) continue;
      const data = line.slice(5).trim();
      if (data === "[DONE]") return;
      yield data;
    }
  }
}

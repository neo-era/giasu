const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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

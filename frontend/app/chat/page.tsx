"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import { Math } from "@/components/Math";
import { clearToken, createConversation, getToken, streamMessage } from "@/lib/api";

type Msg = { role: "user" | "assistant"; content: string };

export default function ChatPage() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [convId, setConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setToken(getToken());
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function start() {
    if (!token) return;
    setErr("");
    try {
      const conv = await createConversation(token);
      setConvId(conv.id);
      setMessages([]);
    } catch (e) {
      setErr(String(e instanceof Error ? e.message : e));
    }
  }

  function dangXuat() {
    clearToken();
    router.push("/dang-nhap");
  }

  async function send() {
    if (!convId || !token || !input.trim() || busy) return;
    const userMsg = input.trim();
    setInput("");
    setBusy(true);
    setMessages((m) => [...m, { role: "user", content: userMsg }, { role: "assistant", content: "" }]);
    try {
      for await (const chunk of streamMessage(token, convId, userMsg)) {
        setMessages((m) => {
          const next = [...m];
          next[next.length - 1] = {
            role: "assistant",
            content: next[next.length - 1].content + chunk,
          };
          return next;
        });
      }
    } catch (e) {
      const loi = e instanceof Error ? e.message : String(e);
      setMessages((m) => {
        const next = [...m];
        next[next.length - 1] = { role: "assistant", content: `⚠️ ${loi}` };
        return next;
      });
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col p-4">
      <div className="mb-3 flex items-center justify-between">
        <h1 className="text-lg font-semibold">Gia sư AI — Trò chuyện</h1>
        {token && (
          <button className="text-sm text-gray-500 underline" onClick={dangXuat}>
            Đăng xuất
          </button>
        )}
      </div>

      {token === null ? (
        <p className="text-sm text-gray-500">Đang tải…</p>
      ) : token === "" ? (
        <div className="flex flex-col gap-2">
          <p className="text-sm text-gray-600">Bạn chưa đăng nhập.</p>
          <Link
            href="/dang-nhap"
            className="rounded bg-black p-3 text-center text-base text-white"
          >
            Đăng nhập để bắt đầu
          </Link>
        </div>
      ) : !convId ? (
        <div className="flex flex-col gap-2">
          <button
            className="rounded bg-black p-3 text-base text-white"
            onClick={start}
          >
            Bắt đầu hội thoại
          </button>
          {err && <p className="text-sm text-red-600">{err}</p>}
        </div>
      ) : (
        <>
          <div className="flex-1 space-y-3 overflow-y-auto pb-24">
            {messages.map((m, i) => (
              <div
                key={i}
                className={m.role === "user" ? "text-right" : "text-left"}
              >
                <Math
                  className={
                    "inline-block max-w-[85%] rounded-2xl px-4 py-2 text-base " +
                    (m.role === "user" ? "bg-black text-white" : "bg-gray-100")
                  }
                >
                  {m.content}
                </Math>
              </div>
            ))}
            <div ref={endRef} />
          </div>

          <div className="fixed inset-x-0 bottom-0 mx-auto flex max-w-2xl gap-2 bg-white p-3">
            <input
              className="flex-1 rounded border p-3 text-base"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder="Nhập câu hỏi…"
              disabled={busy}
            />
            <button
              className="rounded bg-black px-4 text-base text-white disabled:opacity-50"
              onClick={send}
              disabled={busy || !input.trim()}
            >
              Gửi
            </button>
          </div>
        </>
      )}
    </main>
  );
}

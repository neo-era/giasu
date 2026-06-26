"use client";

import { useEffect, useRef, useState } from "react";

import { Math } from "@/components/Math";
import { createConversation, streamMessage } from "@/lib/api";

type Msg = { role: "user" | "assistant"; content: string };

export default function ChatPage() {
  const [token, setToken] = useState("");
  const [convId, setConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setToken(localStorage.getItem("giasu_token") ?? "");
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function start() {
    localStorage.setItem("giasu_token", token);
    const conv = await createConversation(token);
    setConvId(conv.id);
    setMessages([]);
  }

  async function send() {
    if (!convId || !input.trim() || busy) return;
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
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col p-4">
      <h1 className="mb-3 text-lg font-semibold">Gia sư AI — Trò chuyện</h1>

      {!convId ? (
        <div className="flex flex-col gap-2">
          <label className="text-sm text-gray-500">Token (dev)</label>
          <input
            className="rounded border p-2 text-base"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="Dán access_token"
          />
          <button
            className="rounded bg-black p-3 text-base text-white disabled:opacity-50"
            onClick={start}
            disabled={!token}
          >
            Bắt đầu hội thoại
          </button>
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

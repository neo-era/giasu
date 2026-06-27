"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { login, register, verifyOtp } from "@/lib/api";

type Mode = "login" | "register" | "otp";

export default function DangNhapPage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("demo@hs.vn");
  const [password, setPassword] = useState("matkhau123");
  const [otp, setOtp] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function doLogin() {
    setBusy(true);
    setMsg("");
    try {
      await login(email, password);
      router.push("/chat");
    } catch (e) {
      setMsg(String(e instanceof Error ? e.message : e));
    } finally {
      setBusy(false);
    }
  }

  async function doRegister() {
    setBusy(true);
    setMsg("");
    try {
      const res = await register(email, password);
      setMode("otp");
      if (res.otp_dev) {
        setOtp(res.otp_dev);
        setMsg(`Mã OTP (dev) đã điền sẵn: ${res.otp_dev}. Bấm "Xác thực & vào học".`);
      } else {
        setMsg("Đã gửi OTP. Kiểm tra email/SMS để lấy mã.");
      }
    } catch (e) {
      setMsg(String(e instanceof Error ? e.message : e));
    } finally {
      setBusy(false);
    }
  }

  async function doVerify() {
    setBusy(true);
    setMsg("");
    try {
      await verifyOtp(email, otp);
      await login(email, password);
      router.push("/chat");
    } catch (e) {
      setMsg(String(e instanceof Error ? e.message : e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center gap-3 p-6">
      <h1 className="text-center text-2xl font-bold">Gia sư AI</h1>

      {mode !== "otp" && (
        <div className="flex gap-2 text-sm">
          <button
            className={`flex-1 rounded p-2 ${mode === "login" ? "bg-black text-white" : "border"}`}
            onClick={() => setMode("login")}
          >
            Đăng nhập
          </button>
          <button
            className={`flex-1 rounded p-2 ${mode === "register" ? "bg-black text-white" : "border"}`}
            onClick={() => setMode("register")}
          >
            Đăng ký
          </button>
        </div>
      )}

      {mode === "otp" ? (
        <>
          <input
            className="rounded border p-3 text-base"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="Nhập mã OTP"
            inputMode="numeric"
          />
          <button
            className="rounded bg-black p-3 text-base text-white disabled:opacity-50"
            onClick={doVerify}
            disabled={busy || !otp}
          >
            Xác thực & vào học
          </button>
        </>
      ) : (
        <>
          <input
            className="rounded border p-3 text-base"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            autoComplete="username"
          />
          <input
            className="rounded border p-3 text-base"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Mật khẩu"
            autoComplete="current-password"
          />
          <button
            className="rounded bg-black p-3 text-base text-white disabled:opacity-50"
            onClick={mode === "login" ? doLogin : doRegister}
            disabled={busy || !email || !password}
          >
            {mode === "login" ? "Đăng nhập" : "Đăng ký"}
          </button>
        </>
      )}

      {msg && <p className="text-sm text-red-600">{msg}</p>}
    </main>
  );
}

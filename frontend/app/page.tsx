import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-6 p-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold">Gia sư AI</h1>
        <p className="mt-2 text-gray-500">
          Một nền tảng — hai phân khúc. Học để TỰ LÀM được, không giải hộ.
        </p>
      </div>

      <div className="flex flex-col gap-3">
        <Link
          href="/dang-nhap"
          className="rounded-xl bg-black p-4 text-center text-base font-medium text-white"
        >
          Đăng nhập / Đăng ký
        </Link>
        <Link
          href="/chat"
          className="rounded-xl border p-4 text-center text-base font-medium"
        >
          Vào học (Chat)
        </Link>
        <Link
          href="/ocr"
          className="rounded-xl border p-4 text-center text-base font-medium"
        >
          Số hóa đề (OCR → LaTeX)
        </Link>
      </div>

      <p className="text-center text-xs text-gray-400">
        Tài khoản demo: demo@hs.vn / matkhau123
      </p>
    </main>
  );
}

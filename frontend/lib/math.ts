import katex from "katex";

/** Render văn bản có công thức $...$ / $$...$$ thành HTML (KaTeX). */
export function renderMath(text: string): string {
  const escaped = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // $$...$$ (display) trước, rồi $...$ (inline)
  return escaped
    .replace(/\$\$([^$]+)\$\$/g, (_, expr: string) => tryKatex(expr, true))
    .replace(/\$([^$]+)\$/g, (_, expr: string) => tryKatex(expr, false));
}

function tryKatex(expr: string, displayMode: boolean): string {
  try {
    return katex.renderToString(expr, { throwOnError: false, displayMode });
  } catch {
    return expr;
  }
}

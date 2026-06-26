import { describe, expect, it } from "vitest";

import { renderMath } from "./math";

describe("renderMath", () => {
  it("render inline $...$", () => {
    const html = renderMath("Nghiệm là $x = 2$.");
    expect(html).toContain("katex");
    expect(html).not.toContain("$x = 2$");
  });

  it("render display $$...$$ (tích phân nhiều lớp)", () => {
    const html = renderMath("$$\\int_0^1 \\int_0^x f(t)\\,dt\\,dx$$");
    expect(html).toContain("katex");
  });

  it("render ma trận pmatrix", () => {
    const html = renderMath(
      "$\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}$",
    );
    expect(html).toContain("katex");
  });

  it("công thức lỗi không ném ngoại lệ (fallback)", () => {
    expect(() => renderMath("$\\frac{1}{$")).not.toThrow();
  });

  it("escape HTML trong văn bản thường", () => {
    const html = renderMath("1 < 2 & 3 > 0");
    expect(html).toContain("&lt;");
    expect(html).toContain("&amp;");
    expect(html).toContain("&gt;");
  });

  it("giữ văn bản thường ngoài công thức", () => {
    const html = renderMath("Đáp số: $x=1$ nhé");
    expect(html).toContain("Đáp số:");
    expect(html).toContain("nhé");
  });
});

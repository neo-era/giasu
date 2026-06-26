import { renderMath } from "@/lib/math";

type Props = {
  children: string;
  className?: string;
};

/** Hiển thị văn bản có công thức $...$ / $$...$$ (KaTeX), render đồng bộ
 * (không async) để tránh layout shift. */
export function Math({ children, className }: Props) {
  return (
    <span
      className={className}
      dangerouslySetInnerHTML={{ __html: renderMath(children) }}
    />
  );
}

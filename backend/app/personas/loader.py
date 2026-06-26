import re
from dataclasses import dataclass
from pathlib import Path

from app.config import settings

# Placeholder dạng [TÊN_BIẾN] viết HOA (quy ước: [LEVEL], [SUBJECT]…)
PLACEHOLDER_RE = re.compile(r"\[([A-Z][A-Z0-9_]*)\]")
_HEADER_RE = re.compile(r"#\s*(\w+)\s*:\s*(.+)")


class PromptError(Exception):
    """Lỗi nạp/chèn biến prompt — thông điệp phải rõ ràng."""


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    version: int
    text: str

    @property
    def required_vars(self) -> set[str]:
        return set(PLACEHOLDER_RE.findall(self.text))

    def render(self, **variables: object) -> str:
        missing = self.required_vars - set(variables)
        if missing:
            raise PromptError(f"Thiếu biến cho prompt '{self.name}': {sorted(missing)}")
        out = self.text
        for key, value in variables.items():
            out = out.replace(f"[{key}]", str(value))
        return out


def _default_dir() -> Path:
    # app/personas/loader.py → parents[2]=backend, parents[3]=<repo root>
    return Path(__file__).resolve().parents[3] / "prompts"


def _parse(raw: str, name: str) -> PromptTemplate:
    lines = raw.splitlines()
    version = 1
    i = 0
    while i < len(lines) and lines[i].lstrip().startswith("#"):
        m = _HEADER_RE.match(lines[i].strip())
        if m and m.group(1) == "version":
            try:
                version = int(m.group(2).strip())
            except ValueError:
                pass
        i += 1
    body = "\n".join(lines[i:]).strip("\n")
    return PromptTemplate(name=name, version=version, text=body)


class PersonaLoader:
    """Nạp prompt sản xuất từ thư mục `prompts/` (FR-C07). Có cache + versioning."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or (
            Path(settings.prompts_dir) if settings.prompts_dir else _default_dir()
        )
        self._cache: dict[tuple[str, int | None], PromptTemplate] = {}

    def _path(self, name: str, version: int | None) -> Path:
        fname = f"{name}.txt" if version is None else f"{name}.v{version}.txt"
        return self.base_dir / fname

    def load(self, name: str, version: int | None = None) -> PromptTemplate:
        cache_key = (name, version)
        if cache_key in self._cache:
            return self._cache[cache_key]
        path = self._path(name, version)
        if not path.exists():
            raise PromptError(f"Không tìm thấy prompt '{name}' tại {path}")
        template = _parse(path.read_text(encoding="utf-8"), name)
        self._cache[cache_key] = template
        return template

    def render(self, name: str, *, version: int | None = None, **variables: object) -> str:
        return self.load(name, version).render(**variables)

    def reload(self) -> None:
        self._cache.clear()


_loader: PersonaLoader | None = None


def get_persona_loader() -> PersonaLoader:
    global _loader
    if _loader is None:
        _loader = PersonaLoader()
    return _loader

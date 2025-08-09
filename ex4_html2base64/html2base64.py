"""
Utilidades para convertir imágenes <img> en HTML a data URIs base64.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import base64
import mimetypes
import json

from html.parser import HTMLParser
from html import escape


SUPPORTED_IMG_SCHEMES = ("", "file://",)


@dataclass
class ProcessResult:
    success: Dict[str, List[str]] = field(default_factory=dict)
    fail: Dict[str, List[str]] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "success": self.success,
            "fail": self.fail,
        }, ensure_ascii=False, indent=2)


def _is_local_image(src: str) -> bool:
    if not src:
        return False
    lower = src.lower()
    return lower.startswith(SUPPORTED_IMG_SCHEMES) and not (lower.startswith("http://") or lower.startswith("https://") or lower.startswith("data:"))


def _read_file_bytes(path: Path) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _ext_to_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.as_posix())
    if not mime:
        # fallback común para imágenes desconocidas
        return "application/octet-stream"
    return mime


def inline_images_in_html(html_path: Path, output_suffix: str = ".inlined.html") -> Tuple[Path, List[str], List[str]]:
    """
    Dado un archivo HTML, reemplaza <img src> locales por data URIs base64 y guarda un nuevo archivo.
    Retorna (ruta_salida, imagenes_ok, imagenes_fail)
    """
    html_path = Path(html_path)
    html_text = html_path.read_text(encoding="utf-8", errors="ignore")

    class ImgInliner(HTMLParser):
        def __init__(self, base_html: Path):
            super().__init__(convert_charrefs=True)
            self.base_html = base_html
            self.out: List[str] = []
            self.ok: List[str] = []
            self.bad: List[str] = []

        def _resolve_and_inline(self, src: str) -> str | None:
            if not _is_local_image(src):
                return None
            src_clean = src.replace("file://", "")
            if "?" in src_clean:
                src_clean = src_clean.split("?", 1)[0]
            if "#" in src_clean:
                src_clean = src_clean.split("#", 1)[0]
            candidate = Path(src_clean)
            if candidate.is_absolute():
                img_path = candidate
            else:
                img_path = (self.base_html.parent / candidate)
            img_path = img_path.resolve()
            try:
                data = _read_file_bytes(img_path)
                b64 = base64.b64encode(data).decode("ascii")
                mime = _ext_to_mime(img_path)
                self.ok.append(str(img_path))
                return f"data:{mime};base64,{b64}"
            except Exception:
                self.bad.append(str(img_path))
                return None

        def _attrs_to_str(self, attrs: List[Tuple[str, str | None]]) -> str:
            parts: List[str] = []
            for k, v in attrs:
                if v is None:
                    parts.append(k)
                else:
                    parts.append(f'{k}="{escape(v, quote=True)}"')
            return (" "+" ".join(parts)) if parts else ""

        def handle_decl(self, decl: str) -> None:
            self.out.append(f"<!{decl}>")

        def handle_startendtag(self, tag: str, attrs: List[Tuple[str, str | None]]):
            if tag.lower() == "img":
                new_attrs = []
                replaced = False
                for k, v in attrs:
                    if k.lower() == "src" and v is not None:
                        datauri = self._resolve_and_inline(v.strip())
                        if datauri:
                            new_attrs.append((k, datauri))
                            replaced = True
                            continue
                    new_attrs.append((k, v))
                self.out.append(f"<{tag}{self._attrs_to_str(new_attrs)}/>")
            else:
                self.out.append(f"<{tag}{self._attrs_to_str(attrs)}/>")

        def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]):
            if tag.lower() == "img":
                new_attrs = []
                for k, v in attrs:
                    if k.lower() == "src" and v is not None:
                        datauri = self._resolve_and_inline(v.strip())
                        if datauri:
                            new_attrs.append((k, datauri))
                            continue
                    new_attrs.append((k, v))
                self.out.append(f"<{tag}{self._attrs_to_str(new_attrs)}>")
            else:
                self.out.append(f"<{tag}{self._attrs_to_str(attrs)}>")

        def handle_endtag(self, tag: str):
            self.out.append(f"</{tag}>")

        def handle_data(self, data: str):
            self.out.append(data)

        def handle_comment(self, data: str):
            self.out.append(f"<!--{data}-->")

        def handle_entityref(self, name: str):
            self.out.append(f"&{name};")

        def handle_charref(self, name: str):
            self.out.append(f"&#{name};")

    parser = ImgInliner(html_path)
    parser.feed(html_text)

    # Salida
    out_path = html_path.with_suffix("")
    out_path = out_path.with_name(out_path.name + output_suffix)
    out_path.write_text("".join(parser.out), encoding="utf-8")

    return out_path, parser.ok, parser.bad


def find_html_files(inputs: Iterable[Path]) -> List[Path]:
    """
    Acepta rutas de archivos o directorios y retorna una lista de HTMLs (recursivo para directorios).
    """
    htmls: List[Path] = []
    for p in map(Path, inputs):
        p = p.resolve()
        if p.is_file() and p.suffix.lower() in {".html", ".htm"}:
            htmls.append(p)
        elif p.is_dir():
            for fp in p.rglob("*"):
                if fp.is_file() and fp.suffix.lower() in {".html", ".htm"}:
                    htmls.append(fp.resolve())
    return sorted(set(htmls))


def process(inputs: Iterable[Path]) -> ProcessResult:
    """
    Procesa todos los HTMLs encontrados; para cada uno inlinea imágenes locales y genera un archivo nuevo.
    Devuelve objeto con listas de imágenes exitosas y fallidas por HTML.
    """
    result = ProcessResult()
    for html in find_html_files(inputs):
        out, ok, bad = inline_images_in_html(html)
        result.success[str(html)] = ok
        if bad:
            result.fail[str(html)] = bad
    return result

import os
from pathlib import Path
from ex4_html2base64.html2base64 import inline_images_in_html

def test_inline_smoke(tmp_path: Path):
    # Crear archivos de prueba
    img = tmp_path / "img.png"
    img.write_bytes(b"\x89PNG\r\n\x1a\n")
    html = tmp_path / "index.html"
    html.write_text('<html><body><img src="img.png"></body></html>', encoding="utf-8")

    out, ok, bad = inline_images_in_html(html)

    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "data:" in text and ";base64," in text
    assert str(img.resolve()) in ok
    assert not bad

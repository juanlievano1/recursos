# Arma en _site/ la versión pública del sitio: solo entran los recursos cuya fecha de publicar.json ya llegó.
# Uso: python publicar.py  (para probar otra fecha: python publicar.py 2026-11-06T07:00:00-05:00)
import datetime as dt
import json
import pathlib
import re
import shutil
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
SALIDA = RAIZ / "_site"
NO_SE_PUBLICA = {".git", ".github", "_site", ".gitignore", "README.md", "publicar.py", "publicar.json"}
AVISO_VACIO = '  <p class="razon">Cada recurso aparece aquí el día que sale su video.</p>\n\n'


def filtrar_inicio(html, ocultos):
    for carpeta in ocultos:
        html = re.sub(rf'[ \t]*<a class="recurso" href="{re.escape(carpeta)}/">.*?</a>\n', "", html, flags=re.S)

    def seccion(m):
        if 'class="recurso"' in m.group(0):
            return m.group(0)
        nonlocal html_atajos
        html_atajos.append(m.group(1))
        return ""

    html_atajos = []
    html = re.sub(r'[ \t]*<section class="seccion" aria-labelledby="(\w+)">.*?</section>\n+', seccion, html, flags=re.S)
    for id_seccion in html_atajos:
        html = re.sub(rf'[ \t]*<a class="pildora" href="#{id_seccion}">.*?</a>\n', "", html)
    html = re.sub(r'[ \t]*<nav class="atajos"[^>]*>\s*</nav>\n', "", html)
    if 'class="recurso"' not in html:
        html = html.replace('  <footer class="pie">', AVISO_VACIO + '  <footer class="pie">')
    return html


def main():
    ahora = dt.datetime.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.datetime.now(dt.timezone.utc)
    fechas = json.loads((RAIZ / "publicar.json").read_text(encoding="utf-8"))["recursos"]
    carpetas = {p.name for p in RAIZ.iterdir() if p.is_dir() and (p / "index.html").exists() and p.name not in NO_SE_PUBLICA}

    # Un recurso sin fecha no se publica por accidente: la construcción falla y el sitio se queda como está.
    if carpetas != set(fechas):
        sys.exit(f"publicar.json no coincide con las carpetas. Sin fecha: {sorted(carpetas - set(fechas))}. Sin carpeta: {sorted(set(fechas) - carpetas)}")

    visibles = sorted(c for c in fechas if dt.datetime.fromisoformat(fechas[c]) <= ahora)
    ocultos = sorted(set(fechas) - set(visibles))

    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir()
    for p in RAIZ.iterdir():
        if p.name in NO_SE_PUBLICA or p.name in ocultos:
            continue
        shutil.copytree(p, SALIDA / p.name) if p.is_dir() else shutil.copy2(p, SALIDA / p.name)

    inicio = SALIDA / "index.html"
    html = filtrar_inicio(inicio.read_text(encoding="utf-8"), ocultos)
    for carpeta in ocultos:
        if f'href="{carpeta}/"' in html:
            sys.exit(f"El inicio todavía enlaza a {carpeta}/")
    inicio.write_text(html, encoding="utf-8", newline="\n")
    (SALIDA / "publicados.txt").write_text("\n".join(visibles) + "\n", encoding="utf-8", newline="\n")
    print("Visibles:", visibles or "ninguno", "| Ocultos:", ocultos or "ninguno")


if __name__ == "__main__":
    main()

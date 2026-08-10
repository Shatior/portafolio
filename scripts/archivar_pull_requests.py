#!/usr/bin/env python3
"""Archiva los hilos de los pull requests antes de una migración con `git push --mirror`.

    python scripts/archivar_pull_requests.py vigiabref/threat-intel-pipeline docs/pull-requests

Se commitea para que el archivo sea **reejecutable y contrastable**: cualquiera puede volver a
lanzarlo mientras los originales existan y comparar el resultado con lo que hay en el
repositorio. Es lo único que acerca una transcripción a un original — que la copia sea
reproducible por un tercero.

Copia los bytes tal como los devuelve la API. **No edita, no resume y no corrige**: el cometido
es conservar, y cualquier retoque destruiría lo que se quiere conservar.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = sys.argv[1]
API = f"https://api.github.com/repos/{REPO}"
DESTINO = Path(sys.argv[2])


def obtener(ruta: str) -> list | dict:
    """GET con paginación. Falla ruidosamente: un hilo a medias no se distingue de uno corto."""

    resultados: list = []
    pagina = 1
    while True:
        sep = "&" if "?" in ruta else "?"
        url = f"{API}{ruta}{sep}per_page=100&page={pagina}"
        salida = subprocess.run(
            ["curl", "-sS", "--fail-with-body", "-w", "\n%{http_code}", url],
            capture_output=True,
            text=True,
        )
        cuerpo, _, codigo = salida.stdout.rpartition("\n")
        if codigo.strip() != "200":
            raise RuntimeError(f"{url} devolvió {codigo!r}: {cuerpo[:300]}")
        datos = json.loads(cuerpo)
        if isinstance(datos, dict):
            return datos
        resultados += datos
        if len(datos) < 100:
            return resultados
        pagina += 1


def autor(objeto: dict) -> str:
    usuario = objeto.get("user") or {}
    return usuario.get("login") or "(autor no disponible)"


def cuerpo(objeto: dict) -> str:
    texto = objeto.get("body")
    if texto is None or texto.strip() == "":
        return "*(sin contenido)*"
    return texto


def archivar(numero: int) -> tuple[Path, int, list[str]]:
    pr = obtener(f"/pulls/{numero}")
    lagunas: list[str] = []

    # Tres orígenes distintos, que en la interfaz de GitHub se leen como un solo hilo:
    # comentarios generales, cuerpos de revisión y comentarios en línea sobre el diff.
    eventos: list[dict] = []
    for c in obtener(f"/issues/{numero}/comments"):
        eventos.append({"tipo": "comentario", "dato": c})
    for r in obtener(f"/pulls/{numero}/reviews"):
        # Una revisión sin cuerpo es una aprobación sin texto: se conserva igualmente, porque su
        # existencia es parte del hilo.
        eventos.append({"tipo": f"revisión ({r.get('state', '?').lower()})", "dato": r})
    for c in obtener(f"/pulls/{numero}/comments"):
        eventos.append({"tipo": "comentario en línea sobre el diff", "dato": c})

    def momento(evento: dict) -> str:
        d = evento["dato"]
        return d.get("created_at") or d.get("submitted_at") or ""

    eventos.sort(key=momento)

    lineas = [
        f"# Pull request #{numero} — {pr['title']}",
        "",
        "| | |",
        "|---|---|",
        f"| **Estado** | {pr['state']}{' · fusionado' if pr.get('merged_at') else ''} |",
        f"| **Autor** | @{autor(pr)} |",
        f"| **Creado** | {pr.get('created_at') or '—'} |",
        f"| **Fusionado** | {pr.get('merged_at') or '—'} |",
        f"| **Commit de fusión** | `{pr.get('merge_commit_sha') or '—'}` |",
        f"| **Rama** | `{(pr.get('head') or {}).get('ref', '—')}` → `{(pr.get('base') or {}).get('ref', '—')}` |",
        f"| **URL original** | {pr.get('html_url') or '—'} |",
        f"| **Comentarios archivados** | {len(eventos)} |",
        "",
        "## Descripción",
        "",
        cuerpo(pr),
        "",
        f"## Hilo — {len(eventos)} {'entrada' if len(eventos) == 1 else 'entradas'}, en orden cronológico",
        "",
        "*Cada entrada va precedida de una regla horizontal y de su línea de atribución en "
        "negrita. Los encabezados que aparezcan dentro de una entrada pertenecen al texto "
        "original y se conservan tal cual.*",
        "",
    ]

    if not eventos:
        lineas += ["*El pull request no tiene comentarios, revisiones ni comentarios en línea.*", ""]

    for indice, evento in enumerate(eventos, start=1):
        d = evento["dato"]
        fecha = momento(evento) or "(fecha no disponible)"
        # El andamiaje del archivo **no usa encabezados Markdown**: los cuerpos que transcribe
        # los usan por su cuenta —los informes de revisión traen su propia jerarquía— y competir
        # con ellos obligaría a retocar el texto transcrito, que es justo lo que no se hace.
        cabecera = f"**{indice}. @{autor(d)} · {fecha} · {evento['tipo']}**"
        if d.get("path"):
            cabecera += f" · `{d['path']}`"
        lineas += ["---", "", cabecera, ""]
        if d.get("html_url"):
            lineas += [f"<!-- original: {d['html_url']} -->", ""]
        lineas += [cuerpo(d), ""]
        if cuerpo(d) == "*(sin contenido)*" and not evento["tipo"].startswith("revisión"):
            lagunas.append(f"#{numero} entrada {indice}: comentario sin cuerpo recuperable")

    fichero = DESTINO / f"{numero:02d}.md"
    fichero.write_text("\n".join(lineas), encoding="utf-8")
    return fichero, len(eventos), lagunas


def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    listado = obtener("/pulls?state=all")
    numeros = sorted(p["number"] for p in listado)

    total_eventos = 0
    todas_lagunas: list[str] = []
    for numero in numeros:
        fichero, cuantos, lagunas = archivar(numero)
        total_eventos += cuantos
        todas_lagunas += lagunas
        print(f"  #{numero:>3} → {fichero.name}  ({cuantos} entradas del hilo)")

    print(f"\n{len(numeros)} pull requests archivados, {total_eventos} entradas de hilo en total.")
    if todas_lagunas:
        print("\nLagunas:")
        for laguna in todas_lagunas:
            print(f"  - {laguna}")
    else:
        print("Sin lagunas: todas las entradas traían cuerpo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

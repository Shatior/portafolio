#!/usr/bin/env python3
"""Construye el sitio estático del portafolio.

    python construir.py --informes ../threat-intel-pipeline/reports --salida publico \\
        --base https://shatior.github.io/portafolio

**El sitio no tiene dominio propio**, de modo que `--base` es obligatorio: de ahí salen las
rutas internas, la canónica, el `og:url` y el sitemap. No hay constante que diga dónde vive el
sitio, porque la había —`vigiabref.com`— y envejeció.

**El sitio no puede construirse sin informes, y eso es deliberado.** Si el directorio no existe
o no trae ni un fichero fechado, la construcción **falla con código distinto de cero** en lugar
de publicar una portada con guiones. Un sitio que se despliega en verde con las cifras vacías es
indistinguible de un sitio al día, y la sección de informes es la mitad del argumento: sin ella
lo que queda es un CV, que es exactamente lo que este sitio dice no ser.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from sitio import render
from sitio.lector import leer_informes
from sitio.rutas import Base, interpretar

RAIZ = Path(__file__).resolve().parent


def construir(dir_informes: Path, destino: Path, base: str) -> int:
    if not dir_informes.is_dir():
        print(f"error: no existe el directorio de informes: {dir_informes}", file=sys.stderr)
        return 1

    informes = leer_informes(dir_informes)
    if not informes:
        print(
            f"error: {dir_informes} no contiene ningún informe fechado (AAAA/AAAA-MM-DD.md).\n"
            "El sitio no se publica sin ellos: una portada con las cifras en blanco se lee igual "
            "que una al día.",
            file=sys.stderr,
        )
        return 1

    # El `--base` se resuelve **antes** de borrar nada: uno mal escrito tiene que fallar con el
    # sitio anterior todavía en su sitio, no dejar el directorio vacío.
    try:
        donde = interpretar(base)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)

    ultimo = informes[0]
    # La medición destacada —el porcentaje del panorama que ATT&CK no describe— sale del informe
    # más reciente **que la publique**. Cuando el más reciente la suprime, se hereda con su fecha
    # declarada, que es lo que el propio pipeline hace con las suyas; si ninguno la publica, la
    # portada muestra un guion con su motivo.
    con_panorama = next((i for i in informes if i.panorama_publicado), None)

    render.escribir(destino, "/", render.portada(ultimo, con_panorama, base=donde))
    render.escribir(destino, "/proyecto/", render.proyecto(ultimo, con_panorama, base=donde))

    # `/informes/` es el más reciente: es el destino por defecto de los dos botones del sitio.
    render.escribir(destino, "/informes/", render.informes_pagina(informes, ultimo, canonico="/informes/", base=donde))
    for informe in informes:
        render.escribir(
            destino,
            f"/informes/{informe.iso}/",
            render.informes_pagina(informes, informe, canonico=f"/informes/{informe.iso}/", base=donde),
        )

    shutil.copytree(RAIZ / "estatico", destino / "estatico")

    # **Aquí no se escribe ningún `CNAME`, y hace falta explicarlo porque su ausencia no se ve.**
    #
    # El `CNAME` es lo que reclama un dominio propio ante GitHub Pages: Pages lo lee como *el
    # dominio de este repositorio* y redirige la URL `github.io` hacia él. Sin dominio, escribirlo
    # solo puede hacer daño — apuntaría a un nombre que no resuelve y dejaría inalcanzable la
    # única URL que sí funciona.
    #
    # **Cómo se reactiva el día que haya dominio**, que son tres pasos y ninguno toca este
    # comentario:
    #
    #   1. Añadir aquí `(destino / "CNAME").write_text("elnuevodominio.com\n", encoding="utf-8")`,
    #      en la **raíz** del sitio publicado y no dentro de `estatico/`: ahí Pages lo serviría
    #      como un fichero más y el dominio no se aplicaría.
    #   2. Apuntar los registros DNS del dominio a Pages y declararlo en `Settings → Pages`.
    #   3. Cambiar `--base` en `.github/workflows/desplegar.yml` a `https://elnuevodominio.com`,
    #      **sin prefijo**: el sitio pasa a vivir en una raíz y las rutas internas se acortan
    #      solas. `test_el_despliegue_pasa_el_prefijo_con_el_que_se_sirve` romperá al hacerlo, y
    #      esa es su función: obligar a que las dos cosas se muevan juntas.
    #
    # No se deja el código escrito y desactivado tras una condición: una rama que nadie ejecuta
    # no es una funcionalidad lista, es una que nadie ha probado con el aspecto de estarlo.

    # Sin JavaScript en el sitio, de modo que no hay nada que rastrear; el `robots.txt` existe
    # para no dejar el 404 que algunos rastreadores registran como error del dominio.
    #
    # Bajo prefijo acaba en `/portafolio/robots.txt`, donde **ningún rastreador lo lee**: el
    # protocolo lo busca en la raíz del host. Se escribe igualmente —es el fichero del sitio, y
    # el sitio definitivo sí vivirá en una raíz— sabiendo que hoy es inerte.
    (destino / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {donde.url('/sitemap.xml')}\n", encoding="utf-8"
    )
    _sitemap(destino, informes, donde)

    print(f"Construido en {destino}: {len(informes)} informes, el más reciente {ultimo.iso}.")
    # Se declara siempre: el sitio ya no tiene un «sitio natural» contra el que contrastar, de
    # modo que la única forma de saber con qué URL se ha construido es leerla aquí. Con prefijo,
    # además, el árbol **no** es servible desde la raíz: publicarlo por error en `/` daría 404 en
    # todas las hojas de estilo.
    print(f"  servido en {donde.url('/')}")
    if con_panorama is None:
        print("  ningún informe publica el panorama de familias: la medición destacada no se publica")
    elif con_panorama.iso != ultimo.iso:
        print(f"  medición del panorama heredada del {con_panorama.iso}, declarada como tal")
    for informe in informes:
        faltan = [
            cifra.etiqueta
            for cifra in (informe.indicadores, informe.familias_observadas, informe.familias_con_entrada)
            if cifra.valor is None
        ]
        if faltan:
            # Se declara en el log en vez de pasar en silencio: una cifra ausente en el sitio
            # tiene detrás un informe que la suprimió, y conviene verlo al construir.
            print(f"  {informe.iso}: sin publicar {', '.join(faltan)}")
    return 0


def _sitemap(destino: Path, informes: list, donde: Base) -> None:
    urls = ["/", "/proyecto/", "/informes/"] + [f"/informes/{i.iso}/" for i in informes]
    cuerpo = "".join(f"<url><loc>{donde.url(u)}</loc></url>" for u in urls)
    (destino / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{cuerpo}</urlset>',
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Construye el sitio estático del portafolio.")
    parser.add_argument(
        "--informes",
        type=Path,
        default=Path("../threat-intel-pipeline/reports"),
        help="Directorio `reports/` del repositorio del pipeline.",
    )
    parser.add_argument("--salida", type=Path, default=RAIZ / "publico", help="Directorio de salida.")
    parser.add_argument(
        "--base",
        required=True,
        help=(
            "URL absoluta bajo la que se sirve el sitio, prefijo incluido: "
            "`https://shatior.github.io/portafolio` como se publica hoy, o "
            "`http://localhost:8000` para mirarlo en local. **Obligatorio**: el sitio no tiene "
            "dominio propio, de modo que no hay de dónde deducirlo, y un valor por defecto se "
            "olvidaría en la línea de órdenes produciendo canónicas hacia otro sitio."
        ),
    )
    args = parser.parse_args()
    return construir(args.informes.resolve(), args.salida.resolve(), args.base)


if __name__ == "__main__":
    raise SystemExit(main())

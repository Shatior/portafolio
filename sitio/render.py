"""Generación del HTML. Sin marco: funciones que devuelven cadenas.

**Por qué no hay plantillas ni motor.** El sitio tiene tres vistas y una lista; un motor de
plantillas añadiría una dependencia, un lenguaje más y un paso de compilación para sustituir a
un puñado de funciones. Lo que sí hay es una regla estricta: **todo lo que venga de un informe
pasa por `esc()`**. Los informes son ficheros generados por otro repositorio, y aunque hoy los
escriba nuestro propio pipeline, tratarlos como confiables sería confiar en que nadie cambie
nunca lo que escriben.

El diseño original llevaba los estilos en atributos `style` de cada elemento. Aquí van a una
hoja única, y no por gusto: las reglas de pantalla estrecha —que son el trabajo de móvil que el
encargo pide primero— no se pueden expresar con estilos en línea.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from . import contenido as c
from .lector import Cifra, Informe
from .rutas import Base


def esc(valor: object) -> str:
    """Escapa cualquier valor que vaya al HTML. Todo lo del informe pasa por aquí."""

    return escape(str(valor), quote=True)


# --- Andamiaje ------------------------------------------------------------------------


def _pagina(titulo: str, descripcion: str, activo: str, cuerpo: str, *, canonico: str, base: Base) -> str:
    """El andamiaje de toda página.

    Dos decisiones que no se ven en la plantilla, y que van aquí y no en un comentario HTML
    porque **un comentario HTML se publica**:

    - **La marca del encabezado es el nombre, no el dominio.** Decía `vigiabref.com`; un sitio
      rotulado con su dirección hay que reetiquetarlo cada vez que se muda, y este ya se ha
      mudado. El enlace sí sigue al prefijo.
    - **El pie no ofrece dirección de contacto.** La que había era de un dominio descartado y
      nunca recibió nada; el motivo largo está en `contenido.CORREO`. El enlace al repositorio se
      queda porque no es un canal de contacto: es la invitación a comprobar.
    """

    nav = [
        ("Portada", "/", "portada"),
        ("Proyecto 01", "/proyecto/", "proyecto"),
        ("Informes", "/informes/", "informes"),
    ]
    actual = ' aria-current="page"'
    enlaces = "".join(
        f'<a href="{esc(base.ruta(url))}"{actual if clave == activo else ""}>{esc(etiqueta)}</a>'
        for etiqueta, url, clave in nav
    )
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(descripcion)}">
<link rel="canonical" href="{esc(base.url(canonico))}">
<meta name="color-scheme" content="dark">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(descripcion)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{esc(base.url(canonico))}">
<link rel="preload" href="{esc(base.ruta("/estatico/fuentes/InterVariable.woff2"))}" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{esc(base.ruta("/estatico/estilo.css"))}">
</head>
<body>
<a class="saltar" href="#principal">Saltar al contenido</a>
<header class="barra">
  <a class="marca" href="{esc(base.ruta("/"))}">{esc(c.NOMBRE)}</a>
  <nav class="nav" aria-label="Secciones">{enlaces}</nav>
</header>
<main id="principal">
{cuerpo}
</main>
<footer class="pie">
  <div class="pie-enlaces">
    <a href="{esc(c.REPO)}" rel="noopener">GitHub</a>
  </div>
  <p class="pie-nota">{esc(c.PIE)}</p>
</footer>
</body>
</html>
"""


def _regla() -> str:
    return '<div class="regla"></div>'


def _cifra_grande(cifra: Cifra, *, sufijo: str = "") -> str:
    """Una cifra derivada del informe, con su ausencia visible cuando no la hay.

    Cuando el informe no publica la magnitud, el valor es un guion y el motivo viaja en el
    `title` y en el texto: una cifra ausente que se pinta igual que una presente invita a leer
    el guion como un cero.
    """

    ausente = " cifra--ausente" if cifra.valor is None else ""
    titulo = f' title="{esc(cifra.motivo)}"' if cifra.motivo else ""
    etiqueta = cifra.etiqueta if cifra.valor is not None else f"{cifra.etiqueta} — no publicado"
    return (
        f'<div class="cifra{ausente}"{titulo}>'
        f"<strong>{esc(cifra.texto)}{esc(sufijo)}</strong>"
        f"<span>{esc(etiqueta)}</span></div>"
    )


def _dato_resumen(cifra: Cifra) -> str:
    ausente = " dato--ausente" if cifra.valor is None else ""
    titulo = f' title="{esc(cifra.motivo)}"' if cifra.motivo else ""
    return (
        f'<div class="dato{ausente}"{titulo}>'
        f"<strong>{esc(cifra.texto)}</strong>"
        f"<span>{esc(cifra.etiqueta)}</span></div>"
    )


def _nota_cifra(cifra: Cifra) -> str:
    """Pinta la salvedad de una cifra que sí existe. Sin esto, `nota` sería un campo que nadie
    lee, que es como se pierden las salvedades."""

    if not cifra.nota:
        return ""
    return f'<p class="pie-nota">{esc(cifra.etiqueta.capitalize())}: {esc(cifra.nota)}.</p>'


def _acciones(base: Base, *, informes: bool = True) -> str:
    partes = []
    if informes:
        partes.append(f'<a class="boton" href="{esc(base.ruta("/informes/"))}">El front — Informes</a>')
    partes.append(f'<a class="boton boton--secundario" href="{esc(c.REPO)}" rel="noopener">El back — Repositorio</a>')
    return f'<div class="acciones">{"".join(partes)}</div>'


# --- Portada --------------------------------------------------------------------------


def _procedencia(ultimo: Informe, fuente: Informe | None) -> str:
    """De qué informe sale la medición destacada, y si es heredada.

    **Heredar una cifra es legítimo; heredarla en silencio no.** Es la misma regla que el
    pipeline aplica a las suyas: cuando el catálogo responde que no hay novedades, arrastra las
    magnitudes de la ejecución anterior «marcadas explícitamente como heredadas y con su fecha».
    Aquí ocurre lo propio cuando el informe más reciente suprime el panorama de familias: la
    alternativa —dejar la portada sin su medición— borraría una afirmación medida que sigue
    siendo cierta, y publicarla sin fecha fingiría que es de hoy.
    """

    if fuente is None:
        return ""
    if fuente.iso == ultimo.iso:
        return f"Cifra del informe del {esc(fuente.etiqueta_larga)}, generada por el pipeline. No está escrita en el sitio."
    return (
        f"Medición <strong>heredada del informe del {esc(fuente.etiqueta_larga)}</strong>: el del "
        f"{esc(ultimo.etiqueta_larga)} no publica el panorama de familias, y una medición que "
        "sigue siendo cierta no se borra por eso — se fecha."
    )


def portada(ultimo: Informe, con_panorama: Informe | None = None, *, base: Base) -> str:
    fuente = con_panorama
    porcentaje = fuente.porcentaje_sin_att_ck if fuente else None
    if porcentaje is None:
        medicion = _cifra_grande(
            Cifra(None, "del panorama observado no está descrito por MITRE ATT&CK", ultimo.familias_observadas.motivo)
        )
    else:
        medicion = (
            '<div class="cifra"><strong>'
            f"{esc(porcentaje)}%"
            "</strong><span>del panorama de amenazas observado no está descrito por MITRE ATT&amp;CK</span></div>"
        )

    cuerpo = f"""
<section class="bloque bloque--intro">
  <h1 class="titular" style="max-width:none">{esc(c.NOMBRE)}</h1>
  <p class="pie-nota" style="font-size:16px">{esc(c.ROL)}</p>
  <p class="destacado" style="max-width:20ch">{esc(c.LEMA)}</p>
</section>
{_regla()}
<section class="bloque">
  <div>
    <span class="epigrafe">01 · Pipeline de ciberinteligencia</span>
    <h2 class="subtitular">{esc(c.TITULO_PROYECTO)}</h2>
  </div>
  <p class="parrafo">{esc(c.ENTRADILLA)}</p>
  <div class="cifras">
    {medicion}
    {_cifra_grande(ultimo.indicadores)}
  </div>
  <p class="pie-nota">{_procedencia(ultimo, fuente) or f"Cifras del informe del {esc(ultimo.etiqueta_larga)}, generadas por el pipeline. No están escritas en el sitio."}</p>
  {_nota_cifra(ultimo.indicadores)}
  <p class="parrafo">{esc(c.VERIFICACION)}</p>
  <p class="pie-nota">{esc(c.COMPETENCIAS)}</p>
  {_acciones(base)}
  <a class="enlace-suelto" href="{esc(base.ruta("/proyecto/"))}">Leer el proyecto completo →</a>
</section>
"""
    return _pagina(
        f"{c.NOMBRE} — {c.ROL}",
        c.LEMA,
        "portada",
        cuerpo,
        canonico="/",
        base=base,
    )


# --- Proyecto -------------------------------------------------------------------------


def proyecto(ultimo: Informe, con_panorama: Informe | None = None, *, base: Base) -> str:
    tarjetas = "".join(f'<div class="tarjeta"><h4>{esc(t)}</h4><p>{esc(p)}</p></div>' for t, p in c.DECISIONES)
    metricas = "".join(
        f'<div class="tarjeta"><h4 style="color:inherit;font-size:14px">{esc(t)}</h4><p style="font-size:13px;color:var(--tinta-tenue)">{esc(p)}</p></div>'
        for t, p in c.METRICAS
    )

    fuente = con_panorama
    porcentaje = fuente.porcentaje_sin_att_ck if fuente else None
    observadas = fuente.familias_observadas if fuente else ultimo.familias_observadas
    con_entrada = fuente.familias_con_entrada if fuente else ultimo.familias_con_entrada
    if porcentaje is None:
        medicion = (
            '<p class="vacio">La medición no está disponible en el informe del '
            f"{esc(ultimo.etiqueta_larga)}: {esc(observadas.motivo or 'el informe no publica el denominador de familias')}.</p>"
        )
    else:
        sin_entrada = (observadas.valor or 0) - (con_entrada.valor or 0)
        medicion = f"""
  <p class="destacado">El {esc(porcentaje)}% del panorama de amenazas observado no está descrito por MITRE ATT&amp;CK.</p>
  <p class="parrafo">{esc(sin_entrada)} de {esc(observadas.valor)} familias activas carecen de entrada en el catálogo. No es una limitación del pipeline: es una afirmación medida sobre la distancia entre el catálogo de referencia del sector y la actividad real.</p>
  <p class="pie-nota">{_procedencia(ultimo, fuente)}</p>"""

    cifras = "".join(
        f'<div class="cifra"><strong>{esc(n)}</strong><span>{esc(t)}</span></div>' for n, t in c.CIFRAS_PROYECTO
    )
    cifras += _cifra_grande(ultimo.kev_publicadas)

    cuerpo = f"""
<section class="bloque">
  <span class="epigrafe">Proyecto 01</span>
  <h1 class="titular">{esc(c.TITULO_PROYECTO)}</h1>

  <h3>El problema</h3>
  <p class="parrafo">{esc(c.PROBLEMA)}</p>

  <h3>Cómo lo resolví</h3>
  <p class="parrafo">{esc(c.SOLUCION)}</p>

  <div class="tarjetas">{tarjetas}</div>

  <h3>Una medición que el proyecto produce</h3>
  {medicion}

  <h3>Cómo se construyó y cómo se verificó</h3>
  <p class="parrafo">{esc(c.VERIFICACION_HUMANA)}</p>
  <div class="rejilla-metricas">{metricas}</div>
  <p class="parrafo">{esc(c.DEFECTOS_EVITADOS)}</p>

  <h3>Qué exigió</h3>
  <p class="pie-nota" style="font-size:14px">{esc(c.COMPETENCIAS)}</p>

  <div class="regla" style="margin-left:0;margin-right:0"></div>
  <div class="cifras cifras--tres">{cifras}</div>
  {_acciones(base)}
</section>
"""
    return _pagina(
        f"{c.TITULO_PROYECTO} — {c.NOMBRE}",
        c.PROBLEMA,
        "proyecto",
        cuerpo,
        canonico="/proyecto/",
        base=base,
    )


# --- Informes -------------------------------------------------------------------------


def _archivo(informes: list[Informe], actual: Informe, base: Base) -> str:
    fichas = []
    for i, informe in enumerate(informes):
        sub = "Informe más reciente" if i == 0 else informe.modo.capitalize()
        actual_attr = ' aria-current="page"' if informe.iso == actual.iso else ""
        fichas.append(
            f'<a href="{esc(base.ruta(f"/informes/{informe.iso}/"))}"{actual_attr}>'
            f'<span class="fecha">{esc(informe.etiqueta_corta)}</span>'
            f'<span class="estado">{esc(sub)}</span></a>'
        )
    return (
        '<nav class="archivo" aria-label="Archivo de informes">'
        '<span class="epigrafe epigrafe--tenue">Archivo</span>'
        f"{''.join(fichas)}</nav>"
    )


def _tabla_kev(informe: Informe) -> str:
    if not informe.entradas_kev:
        return (
            '<p class="vacio">Este informe no publica entradas de vulnerabilidades explotadas '
            "activamente. Puede ser porque el catálogo no incorporó ninguna en el periodo, no "
            "porque no se mirara: el detalle está en el fichero original.</p>"
        )

    filas = []
    for e in informe.entradas_kev:
        reloj = (
            ' <span class="marca-plazo" title="Plazo dentro de los próximos días">⏰</span>' if e.plazo_proximo else ""
        )
        producto = f"{e.fabricante} {e.producto}".strip()
        filas.append(
            "<tr>"
            f'<td data-columna="CVE" class="num">{esc(e.cve)}{reloj}</td>'
            f'<td data-columna="Producto">{esc(producto)}</td>'
            f'<td data-columna="Uso en ransomware" class="tenue">{esc(e.ransomware)}</td>'
            f'<td data-columna="Fecha límite" class="num tenue">{esc(e.fecha_limite)}</td>'
            "</tr>"
        )

    return f"""<div class="tabla-envoltorio">
<table>
  <thead><tr>
    <th scope="col">CVE</th><th scope="col">Producto</th>
    <th scope="col">Uso en ransomware</th><th scope="col">Fecha límite</th>
  </tr></thead>
  <tbody>{"".join(filas)}</tbody>
</table></div>"""


def informes_pagina(informes: list[Informe], actual: Informe, *, canonico: str, base: Base) -> str:
    resumen = "".join(
        _dato_resumen(cifra)
        for cifra in (
            actual.indicadores,
            actual.familias_observadas,
            actual.familias_con_entrada,
            actual.kev_publicadas,
        )
    )

    lagunas = ""
    if actual.lagunas:
        elementos = "".join(f"<li>{esc(t)}</li>" for t in actual.lagunas)
        lagunas = f'<div class="laguna"><h4>Cálculos no publicados</h4><ul>{elementos}</ul></div>'

    modo = actual.modo
    if actual.motivo_linea_base:
        modo += f" · {actual.motivo_linea_base}"
    if actual.intervalo:
        modo += f" · intervalo {actual.intervalo.rstrip('.')}"

    crudo = f"{c.REPO}/blob/main/reports/{actual.fecha.year}/{actual.iso}.md"

    cuerpo = f"""
<div class="informes">
{_archivo(informes, actual, base)}
<article class="informe">
  <div>
    <span class="epigrafe">Informe diario · {esc(actual.etiqueta_larga)}</span>
    <h1 class="subtitular" style="max-width:none">Panorama observado</h1>
    <p class="tabla-nota">Modo: {esc(modo)}</p>
  </div>
  <div class="resumen">{resumen}</div>
  {lagunas}
  <div>
    <h2 class="tabla-titulo">{esc(actual.titulo_seccion_kev)}</h2>
    <p class="tabla-nota">Tal como las publica el informe. El reloj marca las de plazo próximo.</p>
    {_tabla_kev(actual)}
  </div>
  <div class="regla" style="margin-left:0;margin-right:0"></div>
  <a href="{esc(crudo)}" rel="noopener">Ver el fichero original en el repositorio →</a>
</article>
</div>
"""
    return _pagina(
        f"Informe del {actual.etiqueta_larga} — {c.NOMBRE}",
        f"Panorama de amenazas observado el {actual.etiqueta_larga}, generado por el pipeline.",
        "informes",
        cuerpo,
        canonico=canonico,
        base=base,
    )


# --- Escritura ------------------------------------------------------------------------


def escribir(destino: Path, ruta_relativa: str, html: str) -> Path:
    salida = destino / ruta_relativa.strip("/")
    salida.mkdir(parents=True, exist_ok=True)
    fichero = salida / "index.html"
    fichero.write_text(html, encoding="utf-8")
    return fichero

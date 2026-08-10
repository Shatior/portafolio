"""El sitio construido, contrastado contra lo que su propio pie promete.

El pie dice: «Este sitio no usa analítica, formularios ni recursos de terceros; las tipografías
se sirven desde vigiabref.com». Es la única afirmación comprobable del sitio, y la maqueta la
incumplía —cargaba Inter desde `fonts.googleapis.com` mientras el pie decía lo contrario—.

Una promesa que solo puede cumplirse por atención se rompe el día que alguien añade un icono
desde una CDN «solo para probar». Aquí se ejecuta.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import pytest

from construir import construir

FIXTURES = Path(__file__).parent / "fixtures"

#: Los únicos destinos externos admitidos, y solo como enlaces que el lector pulsa: el
#: repositorio del pipeline y el propio dominio. Nada que el navegador **cargue** solo.
DESTINOS_ADMITIDOS = ("https://github.com/Shatior/", "https://vigiabref.com")


@pytest.fixture(scope="module")
def sitio(tmp_path_factory) -> Path:
    destino = tmp_path_factory.mktemp("publico")
    shutil.rmtree(destino)
    assert construir(FIXTURES, destino) == 0
    return destino


def _paginas(sitio: Path) -> list[Path]:
    return sorted(sitio.rglob("*.html"))


def test_se_construyen_las_tres_vistas_y_una_pagina_por_informe(sitio):
    rutas = {p.relative_to(sitio).as_posix() for p in _paginas(sitio)}

    assert "index.html" in rutas
    assert "proyecto/index.html" in rutas
    assert "informes/index.html" in rutas
    assert "informes/2026-08-03/index.html" in rutas
    assert "informes/2026-08-02/index.html" in rutas


def test_informes_apunta_al_mas_reciente(sitio):
    """El destino por defecto de los dos botones del sitio es el informe de hoy."""

    portada_informes = (sitio / "informes" / "index.html").read_text(encoding="utf-8")

    assert "3 de agosto de 2026" in portada_informes


def test_ningun_recurso_de_terceros(sitio):
    """La promesa del pie, ejecutada.

    Se miran los atributos que hacen que el navegador **cargue** algo —`src`, `href` de
    hojas de estilo y precargas, `@import`, `url()` del CSS—, no los enlaces que el lector
    pulsa. Un enlace a GitHub no es un recurso de terceros; una hoja de estilo alojada fuera,
    sí.
    """

    cargas: list[str] = []
    for pagina in _paginas(sitio):
        html = pagina.read_text(encoding="utf-8")
        cargas += re.findall(r'<script[^>]*\ssrc="([^"]+)"', html)
        cargas += re.findall(r'<link[^>]+rel="(?:stylesheet|preload|preconnect)"[^>]*href="([^"]+)"', html)
        cargas += re.findall(r'<link[^>]+href="([^"]+)"[^>]*rel="(?:stylesheet|preload|preconnect)"', html)
        cargas += re.findall(r'<img[^>]*\ssrc="([^"]+)"', html)

    css = (sitio / "estatico" / "estilo.css").read_text(encoding="utf-8")
    cargas += re.findall(r'url\(["\']?([^"\')]+)', css)
    cargas += re.findall(r'@import\s+["\']([^"\']+)', css)

    externos = [u for u in cargas if u.startswith(("http://", "https://", "//"))]
    assert not externos, f"el sitio carga recursos de terceros: {externos}"


def test_ninguna_pagina_lleva_javascript(sitio):
    """Sin scripts no hay analítica posible, que es la otra mitad de la promesa."""

    for pagina in _paginas(sitio):
        html = pagina.read_text(encoding="utf-8")
        assert "<script" not in html, f"{pagina.name} lleva script"
        assert not re.search(r"\son[a-z]+=", html), f"{pagina.name} lleva un manejador en línea"


def test_ningun_formulario(sitio):
    for pagina in _paginas(sitio):
        assert "<form" not in pagina.read_text(encoding="utf-8")


def test_la_tipografia_se_sirve_desde_el_propio_dominio(sitio):
    css = (sitio / "estatico" / "estilo.css").read_text(encoding="utf-8")

    assert "@font-face" in css
    assert "/estatico/fuentes/InterVariable.woff2" in css
    assert (sitio / "estatico" / "fuentes" / "InterVariable.woff2").exists()
    # La licencia viaja con la fuente: es una obligación de la SIL OFL, no un adorno.
    assert (sitio / "estatico" / "fuentes" / "Inter-LICENSE.txt").exists()
    assert "fonts.googleapis.com" not in css
    assert "fonts.gstatic.com" not in css


def test_los_enlaces_externos_solo_van_a_destinos_conocidos(sitio):
    for pagina in _paginas(sitio):
        for url in re.findall(r'href="(https?://[^"]+)"', pagina.read_text(encoding="utf-8")):
            assert url.startswith(DESTINOS_ADMITIDOS), f"enlace externo inesperado: {url}"


# --- Las cifras vienen del informe, no del código -------------------------------------


def test_las_cifras_de_portada_salen_del_informe(sitio):
    """5.494 indicadores es del informe del 3 de agosto, no una constante del sitio."""

    portada = (sitio / "index.html").read_text(encoding="utf-8")

    assert "5.494" in portada
    assert "3 de agosto de 2026" in portada


def test_el_panorama_suprimido_por_el_informe_no_se_republica(sitio):
    """El defecto que encontró la revisión, convertido en regla.

    Los dos informes reales declaran «No se publica el panorama de familias» **y aun así**
    imprimen el denominador «88 familias observadas» dentro del reparto de motivos de su nota
    metodológica. Buscar la cifra en todo el texto la encontraba ahí, y el sitio publicaba como
    medición destacada un panorama que su propia fuente declaraba no publicado — en la misma
    página que reproducía la laguna que lo desmentía.

    Se comprueba sobre los informes **reales**, no sobre un fixture recortado a mano: era ese el
    otro medio hallazgo, que el instrumento estuviera calibrado sobre un caso construido para
    que pasara.
    """

    for pagina in _paginas(sitio):
        html = pagina.read_text(encoding="utf-8")
        assert "88 familias observadas" not in html
        assert "22 con entrada" not in html
        assert "75%" not in html
        assert "carecen de entrada en el catálogo" not in html


def test_una_cifra_con_salvedad_publica_su_salvedad(sitio):
    """Los 5.494 indicadores vienen íntegros de una fuente en estado `parcial`.

    La cifra es cierta y aun así necesita decirlo: `motivo` explica una ausencia, `nota` matiza
    una presencia, y publicar una cifra correcta sin su salvedad es el más silencioso de los dos
    defectos porque no deja hueco donde mirar.
    """

    portada = (sitio / "index.html").read_text(encoding="utf-8")

    assert "no da por correcta" in portada
    assert "threatfox (parcial)" in portada


def test_ninguna_cifra_de_la_maqueta_sobrevive_en_el_sitio(sitio):
    """La maqueta traía cifras inventadas: 7.464 indicadores, 76%, «68 de 90 familias», Mirai
    con 1.284 indicadores y objetos de ATT&CK que el informe no publica.

    Vigila la **retirada** de la maqueta. Que no vigila la **reintroducción** lo demostró la
    revisión añadiendo dos cifras nuevas a `CIFRAS_PROYECTO` sin que muriera un solo test; de
    eso se ocupa ahora el test de abajo, y por eso este conserva su alcance real en el nombre.
    """

    inventadas = ("7.464", "76%", "68 de 90", "S0093", "AsyncRAT", "Mirai", "1.284")
    for pagina in _paginas(sitio):
        html = pagina.read_text(encoding="utf-8")
        for cifra in inventadas:
            assert cifra not in html, f"{pagina.name} contiene un dato de la maqueta: {cifra}"


def test_las_cifras_escritas_a_mano_son_exactamente_las_declaradas():
    """La lista de cifras que **no** salen del informe está cerrada y se comprueba entera.

    Es lo que la lista negra no hacía: impedir que alguien añada un número a mano y quede
    envejeciendo en silencio con cara de medición. Añadir una cifra a `CIFRAS_PROYECTO` rompe
    aquí, y romper aquí obliga a decidirlo en vez de a teclearlo.

    Si la cifra que se quiere añadir depende de la última ejecución, no va aquí: va al lector.
    """

    from sitio import contenido

    assert contenido.CIFRAS_PROYECTO == [
        # 471 es la batería recolectada y ejecutada en verde sobre el pipeline en `4a7200e`,
        # no una cifra tomada de un documento: el 467 anterior no coincidía ni con el conteo
        # real ni con las 449 que declaraba el cierre de fase del que se copió.
        ("471", "pruebas automatizadas"),
        ("2 · 1 · 0", "fuentes públicas · informe diario · intervenciones manuales"),
    ], (
        "la lista de cifras escritas a mano ha cambiado. Si la nueva depende de la última "
        "ejecución, tiene que salir del informe y no de aquí."
    )


def test_una_magnitud_ausente_se_publica_como_guion_y_no_como_cero(sitio, tmp_path):
    """Un informe sin panorama de familias no puede producir «0 familias observadas»."""

    solo_sin_familias = tmp_path / "reports" / "2026"
    solo_sin_familias.mkdir(parents=True)
    origen = FIXTURES / "2026" / "2026-07-31-sin-familias.md"
    shutil.copy(origen, solo_sin_familias / "2026-07-31.md")

    destino = tmp_path / "publico"
    assert construir(solo_sin_familias.parent, destino) == 0

    portada = (destino / "index.html").read_text(encoding="utf-8")
    assert "—" in portada
    assert "no publicado" in portada
    assert ">0<" not in portada.replace(" ", "")


def test_sin_informes_la_construccion_falla(tmp_path):
    """Un sitio en verde con las cifras vacías es indistinguible de uno al día."""

    vacio = tmp_path / "reports"
    vacio.mkdir()

    assert construir(vacio, tmp_path / "publico") == 1
    assert not (tmp_path / "publico").exists()


def test_sin_directorio_de_informes_la_construccion_falla(tmp_path):
    assert construir(tmp_path / "no-existe", tmp_path / "publico") == 1


# --- Móvil ----------------------------------------------------------------------------


def test_las_tablas_llevan_el_nombre_de_su_columna_en_cada_celda(sitio):
    """En pantalla estrecha la tabla se apila y la cabecera desaparece: el nombre de la
    columna viaja en `data-columna` y lo pinta el CSS.

    Se comprueba que el generador lo escribe **en todas** las celdas: una sin él quedaría en el
    móvil como un valor suelto sin decir de qué es.
    """

    html = (sitio / "informes" / "index.html").read_text(encoding="utf-8")
    celdas = re.findall(r"<td([^>]*)>", html)

    assert celdas, "la página de informes no trae ninguna tabla"
    sin_columna = [c for c in celdas if "data-columna" not in c]
    assert not sin_columna, f"{len(sin_columna)} celdas sin `data-columna`"


def test_el_css_resuelve_el_archivo_y_las_tablas_en_pantalla_estrecha(sitio):
    css = (sitio / "estatico" / "estilo.css").read_text(encoding="utf-8")

    assert "@media (max-width: 900px)" in css, "falta el punto de ruptura del archivo"
    assert "@media (max-width: 700px)" in css, "falta el punto de ruptura de las tablas"
    assert "attr(data-columna)" in css, "las tablas apiladas no rotulan sus celdas"


def test_toda_pagina_declara_viewport_y_idioma(sitio):
    for pagina in _paginas(sitio):
        html = pagina.read_text(encoding="utf-8")
        assert 'name="viewport"' in html, f"{pagina.name} sin viewport: el móvil lo renderiza a 980px"
        assert '<html lang="es">' in html

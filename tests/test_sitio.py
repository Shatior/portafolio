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
    # Relativa a la hoja, no a la raíz: es lo que la mantiene resolviendo bajo un prefijo.
    assert 'url("fuentes/InterVariable.woff2")' in css
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


# --- Servido bajo un prefijo ----------------------------------------------------------

#: El despliegue provisional, mientras `vigiabref.com` no resuelva.
BASE_PROVISIONAL = "https://shatior.github.io/portafolio"
PREFIJO = "/portafolio"


@pytest.fixture(scope="module")
def sitio_con_prefijo(tmp_path_factory) -> Path:
    destino = tmp_path_factory.mktemp("bajo-prefijo")
    shutil.rmtree(destino)
    assert construir(FIXTURES, destino, BASE_PROVISIONAL) == 0
    return destino


def test_ninguna_ruta_interna_apunta_a_la_raiz_bajo_prefijo(sitio_con_prefijo):
    """**El defecto que rompe el sitio y no se ve hasta desplegarlo.**

    Servido en `shatior.github.io/portafolio/`, un `href="/estatico/estilo.css"` pide el fichero
    a `shatior.github.io/estatico/estilo.css` — que no existe. El sitio sale sin hoja de estilo,
    sin tipografía y con la navegación entera apuntando a la raíz de un host ajeno, y **la
    construcción termina en verde**: no hay nada en el árbol de salida que delate el fallo.

    Se comprueba sobre **todas** las rutas de todas las páginas, no sobre una lista de las que
    hoy existen: el modo de fallo es que alguien añada mañana la ruta número catorce.

    La revisión encontró que mirar solo `href` y `src` dejaba una vía abierta: `render.py` ya
    escribe atributos `style`, y un `style="background-image:url(/estatico/fondo.png)"` es
    exactamente el fallo que este test dice impedir. Ahora se miran también los `url()` en línea
    y el resto de atributos por los que un navegador pide un fichero.
    """

    for pagina in _paginas(sitio_con_prefijo):
        html = pagina.read_text(encoding="utf-8")
        rutas = re.findall(r'(?:href|src|srcset|poster|action|data|content)="([^"]+)"', html)
        # `url(...)` en un atributo `style`, que no es un atributo de ruta y carga igual.
        rutas += re.findall(r'url\(\s*["\']?([^"\')\s]+)', html)
        absolutas = [r for r in rutas if r.startswith("/")]

        assert absolutas, f"{pagina.name} no trae ninguna ruta interna: el test no vigila nada"
        a_la_raiz = [r for r in absolutas if not r.startswith(f"{PREFIJO}/")]
        assert not a_la_raiz, f"{pagina.name} apunta a la raíz del host: {a_la_raiz}"


def test_el_css_no_pide_la_tipografia_a_la_raiz(sitio_con_prefijo):
    """La hoja se copia tal cual, de modo que su `url()` **no** puede ser absoluta.

    Es la ruta que ningún prefijo reescribe: si fuera `/estatico/fuentes/…`, el sitio bajo
    subdirectorio se serviría con la tipografía rota y con todo lo demás bien, que es la forma
    más fácil de que el fallo pase por decisión de diseño.
    """

    css = (sitio_con_prefijo / "estatico" / "estilo.css").read_text(encoding="utf-8")

    for url in re.findall(r'url\(["\']?([^"\')]+)', css):
        assert not url.startswith("/"), f"el CSS pide {url} a la raíz del host"


def test_las_canonicas_y_el_sitemap_declaran_donde_se_sirve_la_copia(sitio_con_prefijo):
    """Una canónica es una afirmación sobre cuál es la versión buena de esta página.

    Publicar la copia provisional declarando canónicas en `vigiabref.com` señalaría como
    versión buena una URL que hoy no resuelve.
    """

    portada = (sitio_con_prefijo / "index.html").read_text(encoding="utf-8")
    assert f'<link rel="canonical" href="{BASE_PROVISIONAL}/">' in portada
    assert f'content="{BASE_PROVISIONAL}/"' in portada

    sitemap = (sitio_con_prefijo / "sitemap.xml").read_text(encoding="utf-8")
    assert f"<loc>{BASE_PROVISIONAL}/proyecto/</loc>" in sitemap
    assert "vigiabref.com" not in sitemap

    robots = (sitio_con_prefijo / "robots.txt").read_text(encoding="utf-8")
    assert f"Sitemap: {BASE_PROVISIONAL}/sitemap.xml" in robots


def test_la_copia_provisional_no_reclama_el_dominio_propio(sitio_con_prefijo, sitio):
    """**El bloqueante de la pasada 2.** Pages lee el CNAME como *el dominio de este
    repositorio* y redirige la URL `github.io` hacia él. Publicando la copia provisional con un
    CNAME que nombra un dominio que hoy no resuelve, el sitio no queda feo: queda inalcanzable,
    y el prefijo que existe para hacerlo alcanzable no sirve de nada.

    La versión anterior de este test fijaba exactamente lo contrario —que el CNAME estuviera—,
    de modo que blindaba el defecto en lugar de vigilarlo.

    El dominio **no se toca**: construido sin `--base`, el CNAME se escribe igual que siempre, y
    eso se comprueba aquí al lado para que suprimirlo de más también muera.
    """

    assert not (sitio_con_prefijo / "CNAME").exists(), (
        "la copia provisional reclama el dominio propio: Pages redirigiría la URL que sí "
        "funciona hacia una que no resuelve"
    )
    assert (sitio / "CNAME").read_text(encoding="utf-8").strip() == "vigiabref.com"


def test_el_despliegue_pasa_el_prefijo_con_el_que_se_sirve(sitio_con_prefijo):
    """El workflow es la única pieza que decide **dónde** se publica, y no la cubría nada.

    Retirar `--base` de `desplegar.yml` dejaba los 43 tests en verde y publicaba un sitio con
    todas las rutas apuntando a la raíz de `shatior.github.io`. Este test lo ata al valor con el
    que se construye la copia provisional: el día que `vigiabref.com` resuelva, romperá — y esa
    es su función, obligar a retirar las dos cosas a la vez y no solo una.
    """

    workflow = (Path(__file__).parent.parent / ".github/workflows/desplegar.yml").read_text(encoding="utf-8")

    assert f"--base {BASE_PROVISIONAL}" in workflow, (
        "el despliegue no pasa `--base`: publicaría el sitio con las rutas apuntando a la raíz "
        "del host. Si el dominio propio ya resuelve, retira también este test."
    )


def test_el_base_vacio_y_el_por_defecto_producen_el_mismo_sitio(sitio, tmp_path):
    """Pasar `--base ""` y no pasarlo tienen que ser **el mismo árbol, byte a byte**.

    **Lo que este test NO comprueba, y la revisión tuvo razón en señalarlo.** Su nombre anterior
    —«idéntico al de siempre»— prometía una comparación contra el sitio *anterior al cambio*, y
    lo que hace es comparar la rama consigo misma: detecta que el prefijo se cuele en el camino
    por defecto —una barra de más, un origen recompuesto—, y **nada más**.

    Y la promesa mayor era falsa: contra `main` sí hay una diferencia, en `estatico/estilo.css`,
    porque la tipografía pasó a ser relativa a la hoja. Es intencionada y es la única.
    """

    destino = tmp_path / "sin-base-explicita"
    assert construir(FIXTURES, destino, "") == 0

    por_defecto = {p.relative_to(sitio): p.read_bytes() for p in sitio.rglob("*") if p.is_file()}
    explicito = {p.relative_to(destino): p.read_bytes() for p in destino.rglob("*") if p.is_file()}

    assert por_defecto.keys() == explicito.keys()
    distintos = [str(r) for r in por_defecto if por_defecto[r] != explicito[r]]
    assert not distintos, f"`--base` vacío cambia el sitio: {distintos}"


def test_un_prefijo_relativo_se_rechaza_y_no_borra_el_sitio_anterior(tmp_path):
    """Un prefijo sin `/` inicial se resolvería contra la página que lo escribe, y las hay a dos
    niveles: `/informes/2026-08-03/` lo leería como `/informes/2026-08-03/portafolio/`.

    Se comprueba además que **el sitio anterior sigue ahí**. Una construcción que valida sus
    argumentos después de vaciar el directorio de salida convierte una errata en la línea de
    órdenes en un sitio caído.
    """

    destino = tmp_path / "publico"
    assert construir(FIXTURES, destino) == 0
    testigo = (destino / "index.html").read_bytes()

    assert construir(FIXTURES, destino, "portafolio") == 1
    assert (destino / "index.html").read_bytes() == testigo


@pytest.mark.parametrize(
    "base",
    [
        "//evil.example/portafolio",  # empieza por barra y **es un host**: referencia de red
        "/portafolio?v=2",
        "/portafolio#inicio",
        "/portafolio/../otro",
        "/porta folio",
    ],
)
def test_un_base_que_no_es_un_prefijo_se_rechaza(tmp_path, base):
    """«Empieza por `/`» no basta para ser una ruta.

    `//evil.example/x` empieza por barra y el navegador la resuelve **contra otro host**: un
    sitio que promete no cargar recursos de terceros los cargaría todos, y sin salir de la
    comprobación que lo daba por bueno.
    """

    assert construir(FIXTURES, tmp_path / f"salida-{abs(hash(base))}", base) == 1


def test_el_esquema_en_mayusculas_se_acepta(tmp_path):
    """Rechazar `HTTPS://…` pidiendo «una URL absoluta» es pedir lo que ya se escribió."""

    destino = tmp_path / "mayusculas"
    assert construir(FIXTURES, destino, "HTTPS://Shatior.github.io/portafolio") == 0
    assert '<link rel="canonical" href="https://Shatior.github.io/portafolio/">' in (destino / "index.html").read_text(
        encoding="utf-8"
    )


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

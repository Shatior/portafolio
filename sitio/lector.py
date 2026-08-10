"""Lectura de los informes de `threat-intel-pipeline`.

**El sitio no escribe informes: los lee.** Cada fichero de `reports/AAAA/AAAA-MM-DD.md` es la
salida real del pipeline, y de ahí salen tanto la sección de informes como las cifras de portada
y de la página del proyecto. Ninguna cifra se fija en el código.

**Lo que este módulo no hace, y es deliberado: no inventa.** Un informe puede no traer una
magnitud —porque el modo la suprime, porque una fuente no alcanzó estado `correcta`, o porque el
catálogo respondió que no hay novedades—, y en ese caso el campo queda en `None` y la página
publica un guion con su motivo. La alternativa —rellenar con el valor del día anterior, o con
cero— convertiría una ausencia de observación en una observación de ausencia, que es exactamente
lo que el informe que estamos leyendo se niega a hacer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

#: Modos de informe que el pipeline produce.
LINEA_BASE = "línea base"
DIFERENCIAL = "diferencial"
FALLO_TOTAL = "fallo total"


@dataclass(frozen=True, slots=True)
class EntradaKev:
    """Una fila de la sección 4: una vulnerabilidad explotada activamente."""

    cve: str
    fabricante: str
    producto: str
    ransomware: str
    fecha_limite: str
    plazo_proximo: bool


@dataclass(frozen=True, slots=True)
class Cifra:
    """Una magnitud del informe, que **puede no existir**.

    `valor` en `None` significa que el informe no la publica, y `motivo` dice por qué. Las dos
    cosas viajan juntas a propósito: una cifra ausente sin motivo es indistinguible de una cifra
    que dio cero.
    """

    valor: int | None
    etiqueta: str
    motivo: str | None = None
    #: Salvedad de una cifra que **sí** existe. `motivo` explica una ausencia; `nota` matiza una
    #: presencia, y son cosas distintas: publicar una cifra correcta sin su salvedad es el
    #: defecto más silencioso de los dos, porque no deja hueco donde mirar.
    nota: str | None = None

    @property
    def texto(self) -> str:
        if self.valor is None:
            return "—"
        return f"{self.valor:,}".replace(",", ".")


@dataclass(frozen=True, slots=True)
class Informe:
    """Un informe diario, ya interpretado."""

    fecha: date
    ruta: Path
    modo: str
    motivo_linea_base: str | None
    intervalo: str | None
    indicadores: Cifra
    familias_observadas: Cifra
    familias_con_entrada: Cifra
    kev_publicadas: Cifra
    entradas_kev: list[EntradaKev] = field(default_factory=list)
    lagunas: list[str] = field(default_factory=list)
    panorama_publicado: bool = True
    titulo_seccion_kev: str = "Vulnerabilidades explotadas activamente"

    @property
    def iso(self) -> str:
        return self.fecha.isoformat()

    @property
    def etiqueta_corta(self) -> str:
        meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
        return f"{self.fecha.day} {meses[self.fecha.month - 1]} {self.fecha.year}"

    @property
    def etiqueta_larga(self) -> str:
        meses = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
        ]  # fmt: skip
        return f"{self.fecha.day} de {meses[self.fecha.month - 1]} de {self.fecha.year}"

    @property
    def porcentaje_sin_att_ck(self) -> int | None:
        """Cuánto del panorama observado **no** está descrito por ATT&CK.

        Es la medición que la portada destaca, y se calcula aquí y en ningún otro sitio: sobre el
        **total de familias observadas**, nunca sobre las que mapean. Calcularlo sobre el
        subconjunto mapeado produciría un retrato del panorama a partir de una minoría sesgada.
        """

        total = self.familias_observadas.valor
        con_entrada = self.familias_con_entrada.valor
        if not total or con_entrada is None:
            return None
        return round(100 * (total - con_entrada) / total)


# --- Extracción -----------------------------------------------------------------------


def _seccion(texto: str, numero: int) -> str:
    """Devuelve el cuerpo de la sección N del informe, sin su encabezado."""

    patron = re.compile(rf"^## {numero}\. .*?$(.*?)(?=^## \d+\. |\Z)", re.MULTILINE | re.DOTALL)
    hallado = patron.search(texto)
    return hallado.group(1) if hallado else ""


def _titulo_seccion(texto: str, numero: int) -> str | None:
    hallado = re.search(rf"^## {numero}\. (.+)$", texto, re.MULTILINE)
    return hallado.group(1).strip() if hallado else None


def _campo_cabecera(texto: str, nombre: str) -> str | None:
    """Lee un campo con viñeta de la cabecera: `- **Nombre:** valor`."""

    hallado = re.search(rf"^- \*\*{re.escape(nombre)}:?\*\*:?\s*(.+)$", texto, re.MULTILINE)
    if not hallado:
        return None
    return hallado.group(1).strip().strip("`").strip()


def _filas_de_tabla(bloque: str) -> list[list[str]]:
    """Filas de datos de una tabla Markdown, ya despojadas de la cabecera y del separador."""

    filas = []
    for linea in bloque.splitlines():
        linea = linea.strip()
        if not linea.startswith("|") or set(linea) <= set("|- "):
            continue
        celdas = [c.strip() for c in linea.strip("|").split("|")]
        filas.append(celdas)
    return filas[1:] if filas else []


def _indicadores_normalizados(texto: str) -> Cifra:
    """Suma de registros obtenidos menos los descartados, sobre la tabla de estado por fuente.

    **No se toma del BLUF.** El BLUF cambia de forma con el modo del informe —en línea base
    publica un censo y en diferencial no—, mientras que la tabla de estado de recolección está
    en los dos y trae además los descartes, de modo que la magnitud es la misma se lea el
    informe que se lea.
    """

    bloque = re.search(r"### Estado de recolección por fuente(.*?)(?=^###|\Z)", texto, re.MULTILINE | re.DOTALL)
    if not bloque:
        return Cifra(None, "indicadores normalizados", "el informe no publica el estado de recolección")

    total = 0
    visto = False
    degradadas: list[str] = []
    for celdas in _filas_de_tabla(bloque.group(1)):
        if len(celdas) < 5 or not celdas[0].strip("` "):
            continue  # la fila de continuación que declara un campo por debajo de su umbral
        try:
            registros, invalidos, no_soportados = (int(celdas[2]), int(celdas[3]), int(celdas[4]))
        except ValueError:
            continue
        aporta = registros - invalidos - no_soportados
        total += aporta
        visto = True
        if aporta and celdas[1].strip("` ") != "correcta":
            degradadas.append(f"{celdas[0].strip('` ')} ({celdas[1].strip('` ')})")

    if not visto:
        return Cifra(None, "indicadores normalizados", "ninguna fuente declaró registros")

    # **La cifra es cierta y aun así necesita su salvedad.** Los indicadores se normalizaron de
    # verdad; lo que no se puede es presentarlos como un panorama completo cuando parte de ellos
    # viene de una fuente que el informe no da por correcta. El pipeline suprime el diferencial
    # y el panorama de esa fuente, y el sitio no puede publicar su volumen como si nada.
    nota = None
    if degradadas:
        nota = "incluye " + ", ".join(degradadas) + ", cuya recolección el informe no da por correcta"
    return Cifra(total, "indicadores normalizados", nota=nota)


def _familias(texto: str) -> tuple[Cifra, Cifra]:
    """Familias observadas y familias con entrada en ATT&CK.

    La segunda **no está escrita** en el informe: se deriva restando `familia_sin_entrada` del
    denominador. Las familias con canon ambiguo sí tienen entrada —el pipeline se abstiene de
    mapearlas, que es otra cosa—, de modo que restar solo las que carecen de entrada es lo
    correcto y no una aproximación.
    """

    # **La supresión que declara el informe manda sobre cualquier cifra que aparezca en él.**
    #
    # Esta comprobación va primero y no es defensiva: es el defecto que encontró la revisión. El
    # informe puede declarar en su cabecera y en su sección 5 que **no publica** el panorama de
    # familias —porque una fuente no alcanzó estado `correcta`— y aun así imprimir el
    # denominador «88 familias observadas» dentro del reparto de motivos de su nota
    # metodológica. Buscando la cifra en todo el texto se encontraba **esa**, y el sitio
    # publicaba como medición destacada un panorama que su propia fuente declaraba no publicado,
    # en la misma página que reproducía la laguna que lo desmentía.
    #
    # El productor decide qué publica. El consumidor no puede reconstruirlo de las migas.
    suprimido = re.search(r"No se publica el panorama de familias|El panorama de familias no está disponible", texto)
    if suprimido:
        motivo = (
            "el informe declara expresamente que no publica el panorama de familias: alguna "
            "fuente no alcanzó estado correcta y el denominador mediría una recolección truncada"
        )
        return (
            Cifra(None, "familias observadas", motivo),
            Cifra(None, "con entrada en ATT&CK", motivo),
        )

    observadas = re.search(r"denominador: \*\*(\d+) familias observadas\*\*", texto)
    if not observadas:
        motivo = "el informe no publica el denominador de familias observadas"
        return (
            Cifra(None, "familias observadas", motivo),
            Cifra(None, "con entrada en ATT&CK", motivo),
        )

    total = int(observadas.group(1))
    sin_entrada = re.search(r"`familia_sin_entrada`: (\d+) de \d+ familias", texto)
    if not sin_entrada:
        return (
            Cifra(total, "familias observadas"),
            Cifra(None, "con entrada en ATT&CK", "el informe no desglosa `familia_sin_entrada`"),
        )
    return (
        Cifra(total, "familias observadas"),
        Cifra(total - int(sin_entrada.group(1)), "con entrada en ATT&CK"),
    )


def _entradas_kev(texto: str) -> list[EntradaKev]:
    cuerpo = _seccion(texto, 4)
    entradas = []
    for celdas in _filas_de_tabla(cuerpo):
        if len(celdas) < 5:
            continue
        cve = celdas[0].strip("` ")
        entradas.append(
            EntradaKev(
                cve=cve.replace(" ⏰", "").strip("` "),
                fabricante=celdas[1],
                producto=celdas[2],
                ransomware=celdas[3],
                fecha_limite=celdas[4],
                # El pipeline marca con reloj las de plazo dentro de la ventana de vencimiento.
                plazo_proximo="⏰" in celdas[0],
            )
        )
    return entradas


def _lagunas(texto: str) -> list[str]:
    """Los cálculos que el informe declara no publicar.

    Es la sección que más importa reproducir en el sitio: un cálculo que desaparece sin nota es
    indistinguible de un cálculo que dio cero, y el informe se toma el trabajo de declararlo.
    """

    bloque = re.search(r"### Cálculos no publicados en esta ejecución(.*?)(?=^## |\Z)", texto, re.MULTILINE | re.DOTALL)
    if not bloque:
        return []
    lagunas = []
    for linea in bloque.group(1).splitlines():
        linea = linea.strip()
        if linea.startswith("- "):
            lagunas.append(_a_texto_plano(linea[2:]))
    return lagunas


def _a_texto_plano(markdown: str) -> str:
    """Quita el marcado en línea. El sitio le da su propio énfasis con CSS."""

    sin_codigo = re.sub(r"`([^`]*)`", r"\1", markdown)
    sin_negrita = re.sub(r"\*\*([^*]*)\*\*", r"\1", sin_codigo)
    return re.sub(r"\*([^*]*)\*", r"\1", sin_negrita).strip()


def _modo(texto: str) -> str:
    """El modo declarado por el informe. **Sin caída por defecto silenciosa.**

    La versión anterior devolvía «diferencial» cuando no encontraba el campo, de modo que un
    renombrado en el pipeline habría publicado toda línea base como diferencial sin que nada
    fallara: el formato del informe es un contrato externo, y un contrato roto que se degrada a
    un valor plausible es la peor forma de romperse. Ahora se distingue el fallo total —que
    declara su modo en prosa, no en campo— de la ausencia real del campo, que se rechaza.
    """

    declarado = _campo_cabecera(texto, "Modo del informe")
    if declarado is None:
        if "fallo total" in texto[:800].lower():
            return FALLO_TOTAL
        raise ValueError(
            "el informe no declara «Modo del informe» ni se identifica como fallo total: "
            "el formato del pipeline ha cambiado y el sitio no puede adivinar el modo"
        )
    declarado = declarado.lower().strip(" .*")
    if declarado.startswith("fallo total") or "fallo total de recolección" in declarado:
        return FALLO_TOTAL
    if declarado.startswith("línea base") or declarado.startswith("linea base"):
        return LINEA_BASE
    return DIFERENCIAL


def leer_informe(ruta: Path) -> Informe:
    """Interpreta un fichero de informe. No lanza ante secciones ausentes: las declara."""

    texto = ruta.read_text(encoding="utf-8")
    fecha_texto = re.search(r"(\d{4})-(\d{2})-(\d{2})", ruta.stem)
    if not fecha_texto:
        raise ValueError(f"el nombre del fichero no lleva fecha ISO: {ruta.name}")
    fecha = date(*(int(g) for g in fecha_texto.groups()))

    familias_observadas, familias_con_entrada = _familias(texto)
    entradas = _entradas_kev(texto)
    modo = _modo(texto)

    if modo is FALLO_TOTAL or modo == FALLO_TOTAL:
        motivo_kev = "el informe declara un fallo total de recolección"
        kev = Cifra(None, "entradas KEV publicadas", motivo_kev)
    else:
        kev = Cifra(len(entradas), "entradas KEV publicadas")

    return Informe(
        fecha=fecha,
        ruta=ruta,
        modo=modo,
        motivo_linea_base=_campo_cabecera(texto, "Motivo de la línea base"),
        intervalo=_campo_cabecera(texto, "Intervalo real"),
        indicadores=_indicadores_normalizados(texto),
        familias_observadas=familias_observadas,
        familias_con_entrada=familias_con_entrada,
        kev_publicadas=kev,
        entradas_kev=entradas,
        lagunas=_lagunas(texto),
        panorama_publicado=familias_observadas.valor is not None,
        titulo_seccion_kev=_titulo_seccion(texto, 4) or "Vulnerabilidades explotadas activamente",
    )


def leer_informes(directorio: Path) -> list[Informe]:
    """Todos los informes de `reports/`, **del más reciente al más antiguo**.

    `latest.md` se ignora a propósito: es una copia del más reciente y contarla duplicaría un día
    en el archivo. El archivo se construye con los ficheros fechados, que son la serie real.
    """

    ficheros = sorted(directorio.glob("*/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md"))
    informes = [leer_informe(f) for f in ficheros]
    return sorted(informes, key=lambda i: i.fecha, reverse=True)

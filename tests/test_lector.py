"""El lector de informes: lo que extrae, y sobre todo lo que se niega a inventar."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from sitio.lector import DIFERENCIAL, FALLO_TOTAL, LINEA_BASE, leer_informe, leer_informes

FIXTURES = Path(__file__).parent / "fixtures"


def _leer(nombre: str):
    return leer_informe(FIXTURES / "2026" / nombre)


# --- Lo que extrae --------------------------------------------------------------------


def test_lee_el_modo_y_el_motivo_de_una_linea_base():
    informe = _leer("2026-08-02.md")

    assert informe.modo == LINEA_BASE
    assert informe.motivo_linea_base == "estado_ausente"
    assert informe.fecha == date(2026, 8, 2)


def test_lee_el_modo_y_el_intervalo_de_un_diferencial():
    informe = _leer("2026-08-03.md")

    assert informe.modo == DIFERENCIAL
    assert informe.intervalo == "3.7 h"
    assert informe.motivo_linea_base is None


def test_los_indicadores_salen_de_la_tabla_de_recoleccion_y_descuentan_los_descartes():
    """1.656 de KEV + 5.712 de ThreatFox, menos cero inválidos y cero no soportados.

    Se toma de ahí y no del BLUF a propósito: el BLUF cambia de forma con el modo —en línea
    base publica un censo y en diferencial no—, mientras que la tabla está en los dos.
    """

    assert _leer("2026-08-02.md").indicadores.valor == 7368
    assert _leer("2026-08-03.md").indicadores.valor == 5494


def test_las_familias_con_entrada_se_derivan_restando_las_que_no_la_tienen():
    """89 observadas − 67 sin entrada = 22, sobre un informe que **sí** publica el panorama.

    Las familias de canon ambiguo **sí** tienen entrada —el pipeline se abstiene de mapearlas,
    que es otra cosa—, de modo que restar solo `familia_sin_entrada` es lo correcto.

    La fixture es construida y se dice por qué: **ningún informe real publica hoy el panorama**,
    porque ThreatFox lleva semanas sin alcanzar estado `correcta`. El caso contrario —el que sí
    ocurre— lo cubren los informes reales, sin retocar, en el test de más abajo.
    """

    informe = _leer("2026-07-29-panorama-publicado.md")

    assert informe.panorama_publicado
    assert informe.familias_observadas.valor == 89
    assert informe.familias_con_entrada.valor == 22


def test_el_porcentaje_sin_att_ck_se_calcula_sobre_el_total_observado():
    """Nunca sobre el subconjunto que mapea: (89-22)/89 = 75%, no 22/89 ni 67/22."""

    assert _leer("2026-07-29-panorama-publicado.md").porcentaje_sin_att_ck == 75


@pytest.mark.parametrize("nombre", ["2026-08-02.md", "2026-08-03.md"])
def test_un_panorama_que_el_informe_declara_suprimido_no_se_reconstruye(nombre):
    """El bloqueante que encontró la revisión, sobre los informes **reales** y sin retocar.

    Los dos declaran «No se publica el panorama de familias» en su cabecera y en su sección 5, y
    aun así imprimen «denominador: N familias observadas» dentro del reparto de motivos de la
    nota metodológica. Buscar la cifra en todo el texto la encontraba ahí.

    El productor decide qué publica; el consumidor no puede reconstruirlo de las migas.
    """

    informe = _leer(nombre)

    assert not informe.panorama_publicado
    assert informe.familias_observadas.valor is None
    assert informe.porcentaje_sin_att_ck is None
    assert "declara expresamente" in (informe.familias_observadas.motivo or "")


def test_los_indicadores_declaran_su_salvedad_si_una_fuente_no_esta_correcta():
    """La cifra es cierta y necesita decir de dónde sale."""

    con_salvedad = _leer("2026-08-03.md").indicadores
    sin_salvedad = _leer("2026-07-29-panorama-publicado.md").indicadores

    assert con_salvedad.valor == 5494
    assert "threatfox (parcial)" in (con_salvedad.nota or "")
    assert sin_salvedad.nota is None, "sin fuentes degradadas no hay salvedad que publicar"


def test_un_informe_sin_campo_de_modo_se_rechaza_en_vez_de_adivinarse():
    """El formato del informe es un contrato externo.

    Caer a «diferencial» ante un renombrado publicaría toda línea base como diferencial sin que
    nada fallara, que es la peor forma de romperse un contrato.
    """

    roto = FIXTURES / "2026" / "2026-07-28-sin-modo.md"
    roto.write_text("# Informe\n\n## 1. Cabecera\n\n- **Fecha (UTC):** 2026-07-28\n", encoding="utf-8")
    try:
        with pytest.raises(ValueError, match="Modo del informe"):
            leer_informe(roto)
    finally:
        roto.unlink()


def test_lee_la_tabla_kev_con_su_marca_de_plazo_proximo():
    informe = _leer("2026-08-03.md")

    assert [e.cve for e in informe.entradas_kev] == ["CVE-2026-60137", "CVE-2025-68686"]
    assert all(e.plazo_proximo for e in informe.entradas_kev)
    assert informe.entradas_kev[0].producto == "Core"
    assert informe.entradas_kev[0].fabricante == "WordPress"


def test_el_reloj_no_se_queda_pegado_al_cve():
    """El pipeline marca con ⏰ las de plazo próximo dentro de la celda del CVE."""

    assert "⏰" not in _leer("2026-08-03.md").entradas_kev[0].cve


def test_lee_los_calculos_no_publicados():
    """Es la sección que más importa reproducir: un cálculo suprimido sin nota es
    indistinguible de uno que dio cero."""

    lagunas = _leer("2026-08-03.md").lagunas

    assert len(lagunas) == 2
    assert any("caídos de" in t for t in lagunas)
    assert all("**" not in t and "`" not in t for t in lagunas), "el marcado debe quedar fuera"


def test_toma_el_titulo_real_de_la_seccion_4():
    """El título cambia con el modo, y el sitio no puede fijar uno propio."""

    assert "vigentes en el catálogo" in _leer("2026-08-02.md").titulo_seccion_kev
    assert "en este periodo" in _leer("2026-08-03.md").titulo_seccion_kev


# --- Lo que NO inventa ----------------------------------------------------------------


def test_una_magnitud_ausente_queda_en_none_y_declara_su_motivo():
    """El caso que importa: un informe sin panorama de familias.

    La alternativa —arrastrar la cifra del día anterior, o poner un cero— convertiría una
    ausencia de observación en una observación de ausencia, que es justamente lo que el informe
    que estamos leyendo se niega a hacer.
    """

    informe = _leer("2026-07-31-sin-familias.md")

    assert informe.familias_observadas.valor is None
    assert informe.familias_con_entrada.valor is None
    assert informe.porcentaje_sin_att_ck is None
    assert informe.familias_observadas.motivo
    assert informe.familias_observadas.texto == "—"


def test_un_fallo_total_no_publica_entradas_kev_como_cero():
    informe = _leer("2026-07-30-fallo-total.md")

    assert informe.modo == FALLO_TOTAL
    assert informe.kev_publicadas.valor is None
    assert informe.kev_publicadas.motivo


def test_un_informe_sin_tabla_de_recoleccion_no_inventa_indicadores():
    informe = _leer("2026-07-30-fallo-total.md")

    assert informe.indicadores.valor is None
    assert informe.indicadores.motivo


# --- El archivo -----------------------------------------------------------------------


def test_los_informes_llegan_del_mas_reciente_al_mas_antiguo():
    informes = leer_informes(FIXTURES)

    fechas = [i.iso for i in informes]
    assert fechas == sorted(fechas, reverse=True)
    assert fechas[0] == "2026-08-03"


def test_latest_no_entra_en_el_archivo():
    """`latest.md` es una copia del más reciente: contarla duplicaría un día."""

    informes = leer_informes(FIXTURES)

    assert len({i.iso for i in informes}) == len(informes)
    assert all(i.ruta.name != "latest.md" for i in informes)


def test_un_fichero_sin_fecha_iso_se_rechaza():
    with pytest.raises(ValueError, match="fecha ISO"):
        leer_informe(FIXTURES / "sin-fecha.md")

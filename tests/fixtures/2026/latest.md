# Informe de Ciberinteligencia — 2026-08-03 (UTC)

**TLP:CLEAR**

## 1. Cabecera

- **Fecha (UTC):** 2026-08-03 02:22:55
- **Modo del informe:** diferencial
- **Línea base vigente:** 2026-08-02 22:43:36 UTC
- **Intervalo real:** 3.7 h
- **Fuentes consultadas:** `cisa-kev` (correcta), `threatfox` (parcial)

### Cálculos no publicados en esta ejecución

- **No se publican los caídos de `threatfox`:** la fuente no alcanzó estado correcta (parcial), de modo que su diferencial no es publicable. Lo que sí se publica queda **sesgado en un solo sentido**: altas sí, bajas no.
- **No se publica el panorama de familias:** ThreatFox no alcanzó estado `correcta`, y un denominador de «familias observadas» calculado sobre una recolección truncada produce una cifra que aparenta medir el panorama y mide otra cosa.

## 2. BLUF

**2 vulnerabilidades explotadas activamente vencen su plazo de corrección en los próximos 7 días.** Es lo accionable de este informe; el detalle está en la sección 4.

**Cambio del periodo:** 0 indicadores nuevos y 0 reaparecidos, y 0 caídos en `cisa-kev`. Los caídos de `threatfox` **no son calculables** en esta ejecución, de modo que lo publicado solo puede crecer.

Intervalo real cubierto: 3.7 h.

## 3. Juicios clave

- Es **improbable** que la evolución publicada refleje el panorama completo: los caídos de `threatfox` no son calculables en esta ejecución, de modo que lo publicado solo puede crecer. *(confianza: alta — es una propiedad del cálculo, no una estimación)*

## 4. Vulnerabilidades explotadas activamente incorporadas en este periodo

**2 entradas**, ordenadas por fecha límite: primero lo que aún no ha vencido, de lo que vence antes a lo que vence después; después lo vencido, de lo más reciente a lo más antiguo. A igualdad de plazo, primero las de uso conocido en campañas de ransomware.

El uso conocido en campañas de ransomware lo declara CISA. Las de plazo dentro de los próximos 7 días van marcadas con ⏰.

| CVE | Fabricante | Producto | Uso en ransomware | Fecha límite |
|---|---|---|---|---|
| `CVE-2026-60137` ⏰ | WordPress | Core | Unknown | 2026-08-04 |
| `CVE-2025-68686` ⏰ | Fortinet | FortiOS | Unknown | 2026-08-10 |

## 5. Panorama de amenazas

**El panorama de familias no está disponible en esta ejecución.** ThreatFox no alcanzó estado `correcta`, y un denominador de «familias observadas» calculado sobre una recolección truncada produce una cifra que aparenta medir el panorama y mide una recolección incompleta. No se publica, en lugar de publicarse con una advertencia.

## 6. Indicadores destacados

Infraestructura observada de mayor confianza, con los valores **defanged** para evitar clics accidentales. Las vulnerabilidades no figuran aquí: tienen su propia sección, con producto, plazo y uso en ransomware. Los indicadores sin mapeo ATT&CK compiten en igualdad: el enriquecimiento es enriquecimiento, no una puerta de calidad.

| Indicador | Tipo | Fuente | Confianza | Familia | Técnicas |
|---|---|---|---|---|---|
| `amberalcove[.]top` | `domain-name` | `threatfox` | 100 | SmartApeSG | — |
| `shpu1xz9[.]gdcpemasaranbekasi[.]com` | `domain-name` | `threatfox` | 100 | ClearFake | — |
| `www[.]hygroscopiccycle[.]com` | `domain-name` | `threatfox` | 100 | IClickFix | — |
| `jennifer-campbell[.]co[.]uk` | `domain-name` | `threatfox` | 100 | IClickFix | — |
| `pjeobx[.]jadoou[.]lat` | `domain-name` | `threatfox` | 100 | ClearFake | — |
| `endormo[.]com` | `domain-name` | `threatfox` | 100 | IClickFix | — |
| `lasnegrascamps[.]com` | `domain-name` | `threatfox` | 100 | IClickFix | — |
| `strang-02-static[.]com` | `domain-name` | `threatfox` | 100 | PureLogs Stealer | — |
| `172[.]232[.]240[.]110` | `ipv4-addr` | `threatfox` | 100 | Jackskid | — |
| `www[.]smibert[.]com` | `domain-name` | `threatfox` | 100 | IClickFix | — |
| `www[.]vertuoseclub[.]com` | `domain-name` | `threatfox` | 100 | IClickFix | — |
| `85[.]137[.]240[.]26` | `ipv4-addr` | `threatfox` | 100 | Unknown malware | — |
| `implexions[.]com` | `domain-name` | `threatfox` | 100 | IClickFix | — |
| `ufpykr[.]rossbridgemedicalcenterlp[.]com` | `domain-name` | `threatfox` | 100 | ClearFake | — |
| `xn--b6bel7a3an0g[.]com` | `domain-name` | `threatfox` | 100 | IClickFix | — |

## 7. Recomendaciones y ventanas de decisión

1. **Priorizar el parcheo** de las 2 entradas KEV con plazo en los próximos 7 días: `CVE-2026-60137` (2026-08-04), `CVE-2025-68686` (2026-08-10).
2. **Revisar la recolección** de `threatfox`: no alcanzó estado `correcta`, y mientras dure, su parte del panorama y de la evolución no se publica. Plazo: antes de la siguiente ejecución diaria.

## 8. Nota metodológica

La metodología de mapeo a ATT&CK, con sus dos rutas y sus reglas de abstención, está en la documentación del proyecto. Ningún dato aparece en este informe sin una fuente identificable y sin un nivel de confianza declarado.

### Estado de recolección por fuente

| Fuente | Estado | Registros | Inválidos | No soportados | Cobertura evaluada |
|---|---|---|---|---|---|
| `cisa-kev` | correcta | 0 | 0 | 0 | no |
| `threatfox` | parcial | 5494 | 0 | 0 | sí |
| | ↳ campos por debajo de su umbral: `reference` al 3.7% | | | | |

### Catálogo ATT&CK

- **Versión del bundle:** 19.1
- **Digest:** `a6c366439edee3a87b79cf90dc0b93f5d7975956`
- **Procedencia:** caché local
- **Objetos Software indexados:** 821 (3 excluidos por revocados o deprecados)
- **Canons distintos:** 1096
- **Canons ambiguos:** 2 — coincide con la línea base declarada del catálogo
- **Cambio respecto a la ejecución anterior:** no se puede declarar todavía. El estado no persiste la versión ni el digest usados la vez anterior, de modo que este informe no sabe si el catálogo cambió. Es una laguna declarada, no un «no cambió»: un cambio de catálogo puede hacer aparecer o desaparecer un mapeo sin que la amenaza se haya movido.

### Motivos de mapeo ausente, cada uno a su nivel

**Nivel familia** — denominador: **88 familias observadas**.

- `ambiguedad_candidatos`: 1 de 88 familias
- `familia_sin_entrada`: 66 de 88 familias

**Nivel indicador** — denominador: **5494 indicadores de ThreatFox**.

- `sin_atribucion`: 536 de 5494


### Cobertura de la tabla de vectores de explotación

El catálogo KEV no aportó entradas en esta ejecución, de modo que la cobertura no se ha medido hoy. **No es 0%**: es que no hubo denominador sobre el que medirla.

### Cola de trabajo: entradas KEV **nuevas del periodo** sin clasificar

**0** entradas nuevas del periodo sin clasificar.

La cola está vacía en esta ejecución. Si el catálogo respondió que no hay novedades, eso no significa que la tabla esté al día: significa que no hubo entradas nuevas.

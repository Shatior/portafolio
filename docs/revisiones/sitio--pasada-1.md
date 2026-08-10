# Revisión independiente — sitio del portafolio y disparo desde el pipeline · pasada 1

- **Revisor:** sesión de agente independiente. No implementó ninguno de los dos cambios ni tuvo
  su contexto.
- **Fecha:** 2026-08-03
- **Corpus (R1):** `/home/user/portafolio` íntegro (`construir.py`, `sitio/*.py`,
  `estatico/estilo.css`, `tests/*.py`, `.github/workflows/*.yml`, `README.md`, fixtures); el
  diff de `claude/disparo-sitio` en `threat-intel-pipeline` (que está como cambios en árbol de
  trabajo, no commiteados: `.github/workflows/daily.yml` y `tests/test_workflow_diario.py`); los
  informes reales de `/home/user/threat-intel-pipeline/reports/`; y la maqueta original.
  No se leyó `CLAUDE.md` entero ni el histórico de actas.
- **Presupuesto (R2):** 10 minutos / 30 mutaciones. Consumido: ~10 min y **4 mutaciones**. El
  presupuesto de tiempo se agotó antes que el de mutaciones; el acta es **incremental**.
- **Independencia:** se informa, no se corrige. Las cuatro mutaciones se revirtieron desde copia
  y la batería vuelve a dar 30 en verde. **`/home/user/portafolio` no es un repositorio git**
  (no hay `.git`), de modo que la comprobación de reversión con `git status` no es posible ahí;
  se hizo por restauración desde copia + suite en verde. En `threat-intel-pipeline` no se tocó
  nada.

---

## Cobertura declarada contra la taxonomía numerada

| # | Categoría | Recorrida |
|---|---|---|
| 1 | Conjetura presentada como verificación | **Sí** — hallazgos 2, 4 |
| 2 | Contrato externo no verificado | **Sí, parcialmente** — hallazgo 10; no se auditó todo el formato del informe campo a campo |
| 3 | Validez sintáctica con sentido incorrecto | **Sí** — hallazgo 1 |
| 4 | Alarma degenerada | **Sí** — hallazgo 4 |
| 5 | Requisito de la especificación no satisfecho pese a estar implementado | **Sí** — hallazgos 1, 6 |
| 6 | Coste operativo no considerado | **No** |
| 7 | Deriva entre especificación y código | **No** (el sitio no tiene especificación escrita distinta del encargo y el README; lo que se contrastó contra el README va en el hallazgo 2) |
| 8 | Requisitos de OPSEC | **Sí** — sin hallazgo, ver abajo |
| 9 | Simetría de modos de fallo | **Sí** — hallazgos 1, 8 |
| 10 | Defecto introducido por una corrección | **No** — no había corrección previa que contrastar en este proyecto nuevo |
| 11 | Penalización de la propia retirada | **No** |

---

## Mutaciones ejecutadas

| # | Mutación | Resultado | Qué murió |
|---|---|---|---|
| M1 | `<link rel="stylesheet" href="https://cdn.jsdelivr.net/...">` en `render._pagina` | **Muerta** | `test_ningun_recurso_de_terceros`, `test_los_enlaces_externos_solo_van_a_destinos_conocidos` |
| M2 | `<script src="https://plausible.io/js/script.js">` en `<head>` | **Muerta** | `test_ningun_recurso_de_terceros`, `test_ninguna_pagina_lleva_javascript` |
| M3 | Dos cifras inventadas nuevas en `contenido.CIFRAS_PROYECTO` (`"9.812"` indicadores procesados hoy, `"93%"` de cobertura) | **SOBREVIVE** — 30/30 en verde | nada |
| M4 | `@import url(https://fonts.googleapis.com/...)` al inicio de `estilo.css` | **Muerta** | `test_ningun_recurso_de_terceros`, `test_la_tipografia_se_sirve_desde_el_propio_dominio` |

**Conclusión de las mutaciones:** la promesa del pie —«ningún recurso de terceros»— está
genuinamente ejecutada: las tres formas de introducir una carga externa (link, script, CSS)
mueren. La promesa de «ninguna cifra escrita a mano» **no** lo está (hallazgo 4).

Además se construyó el sitio contra los informes **reales** del pipeline
(`python construir.py --informes /home/user/threat-intel-pipeline/reports`) y se inspeccionó el
HTML generado. De ahí sale el hallazgo 1.

---

## Hallazgos

### BLOQUEANTE 1 — El sitio publica como medición destacada un panorama que el informe declara expresamente no publicado

**Fichero:** `sitio/lector.py:188` (`_familias`), con efecto en `sitio/render.py:124-134`
(portada), `sitio/render.py:179-190` (proyecto) y `sitio/render.py:289-297` (informes).
**Categorías:** 3, 5, 9.

`_familias()` busca `denominador: **(\d+) familias observadas**` **en todo el texto del
informe**. Si no la encuentra, devuelve `None` con el motivo correcto («el panorama de familias
no está disponible…»). El autor previó el caso; la detección está implementada al revés.

En el informe real del 2026-08-03 —el más reciente, el que alimenta la portada— la cabecera
declara:

> - **No se publica el panorama de familias:** ThreatFox no alcanzó estado `correcta`, y un
>   denominador de «familias observadas» calculado sobre una recolección truncada produce una
>   cifra que aparenta medir el panorama y mide otra cosa.

y la sección 5 lo repite. Pero la nota metodológica de §8.2 imprime igualmente, en su reparto de
motivos de mapeo ausente (línea 96 del informe), `**Nivel familia** — denominador: **88 familias
observadas**.` La expresión regular casa con **esa** línea. Resultado, verificado sobre el HTML
construido:

- `publico/index.html`: `<strong>75%</strong><span>del panorama de amenazas observado no está
  descrito por MITRE ATT&CK</span>`
- `publico/proyecto/index.html`: «El 75% del panorama de amenazas observado no está descrito por
  MITRE ATT&CK» y «66 de 88 familias activas carecen de entrada en el catálogo. **No es una
  limitación del pipeline: es una afirmación medida** sobre la distancia entre el catálogo de
  referencia del sector y la actividad real.»
- `publico/informes/index.html`: `88 familias observadas` y `22 con entrada en ATT&CK` en el
  resumen **y, dos bloques más abajo, en el propio bloque «Cálculos no publicados», la línea
  «No se publica el panorama de familias»**. La misma página se desmiente a sí misma.

Es exactamente el modo de fallo que el sitio se escribió para no tener: una cifra suprimida por
el productor, republicada por el consumidor con cara de medición, y destacada como «una medición
que el proyecto produce». Y no es un caso hipotético: es el estado del sitio hoy, con el informe
de hoy.

El campo del que salen las dos magnitudes derivadas (`familias_con_entrada`, y de ahí
`porcentaje_sin_att_ck`) hereda el defecto: 88 − 66 = 22 y 75% son aritmética correcta sobre un
denominador que el informe no autoriza a usar.

---

### BLOQUEANTE 2 — La prueba que vigila el hallazgo 1 se ejercita contra un fixture editado a mano, mientras el informe real recorre la rama contraria sin que nada falle

**Ficheros:** `tests/test_sitio.py:142-156`, `tests/fixtures/2026/2026-07-31-sin-familias.md:18`,
`tests/fixtures/2026/2026-08-03.md:16,96`, `README.md` («Y lo que el informe no publica, el sitio
tampoco»), `sitio/lector.py:7-12` (docstring).
**Categorías:** 1, 2, 9.

- `tests/fixtures/2026/2026-08-03.md` es **byte-idéntico** al informe real (`diff` vacío). Es
  decir: el caso que produce el defecto **ya está dentro de la batería**, y la batería pasa.
- `tests/fixtures/2026/2026-07-31-sin-familias.md` es una versión de la que se ha retirado la
  línea de §8.2. Es el único fixture que recorre la rama de ausencia, y es el que usa
  `test_una_magnitud_ausente_se_publica_como_guion_y_no_como_cero`.

De modo que la comprobación que el README presenta como garantía —«Si una fuente no alcanzó
estado correcta y el informe suprime el panorama de familias, la portada muestra un guion con su
motivo, no un cero»— solo es cierta sobre un informe que el pipeline no produce. Contra el
informe que el pipeline **sí** produce, la afirmación del README es falsa y ninguna prueba lo
dice. El docstring de `lector.py` («Lo que este módulo no hace, y es deliberado: no inventa»)
tiene el mismo problema.

Esto es lo que convierte el hallazgo 1 en bloqueante en vez de en un fallo de regex: el
instrumento que debía detectarlo está calibrado sobre un caso construido para que pase.

---

### RELEVANTE 3 — Un test consagra la cifra defectuosa como valor esperado

**Fichero:** `tests/test_sitio.py:118-125`.
**Categorías:** 1, 10 (prospectiva).

```python
def test_las_cifras_de_portada_salen_del_informe(sitio):
    """5.494 indicadores y 75% son del informe del 3 de agosto, no constantes del sitio."""
    assert "5.494" in portada
    assert "75%" in portada
```

El `75%` es el producto del hallazgo 1. Corregir `_familias()` hará fallar este test, y el
camino más corto para volver al verde —relajar la aserción o «arreglar» el fixture— reintroduce
el defecto. Se señala ahora precisamente para que la corrección no lo pise: la aserción correcta
tras el arreglo es que la portada **no** publique porcentaje para el informe del 03, y sí para el
del 02.

---

### RELEVANTE 4 — «Ninguna cifra de la maqueta sobrevive» no vigila lo que su docstring dice vigilar

**Fichero:** `tests/test_sitio.py:128-139`. **Mutación M3.**
**Categorías:** 4, 1.

El docstring dice: «Es la comprobación que impide el modo de fallo real de este sitio: que
**alguien reintroduzca un número a mano** y quede envejeciendo en silencio con cara de medición.»

Lo que hace es una lista negra de seis cadenas concretas de la maqueta
(`"7.464", "76%", "68 de 90", "S0093", "AsyncRAT", "Mirai"`). M3 añadió a
`contenido.CIFRAS_PROYECTO` dos cifras nuevas inventadas —`("9.812", "indicadores procesados
hoy")` y `("93%", "de cobertura del catálogo")`—, que es literalmente el modo de fallo descrito,
y **las 30 pruebas siguen en verde**.

La lista negra vigila la retirada de la maqueta (útil, y ya cumplida), no la reintroducción. Una
comprobación que sí lo haría: que ninguna entrada de `CIFRAS_PROYECTO` cambie sin declararlo, o
que toda cadena con forma de magnitud en el HTML esté trazada a un `Cifra` del lector o a la
lista corta y declarada de cifras de repositorio. Se informa el defecto, no se prescribe la
solución.

Nota relacionada: `CIFRAS_PROYECTO` contiene hoy `("467", "pruebas automatizadas")`, mientras el
propio `CLAUDE.md` del pipeline declara 449 tests en el cierre de fase 4. No se verificó cuál es
la correcta —queda en «no verificado»— pero es exactamente la clase de cifra que el mecanismo
anterior debería vigilar y no vigila.

---

### RELEVANTE 5 — «Indicadores normalizados» suma fuentes que no alcanzaron `correcta`, sin declararlo

**Fichero:** `sitio/lector.py:149-176`.
**Categorías:** 3, 9.

`_indicadores_normalizados` recorre la tabla «Estado de recolección por fuente» y suma
`registros − inválidos − no soportados` de **todas** las filas, sin mirar la columna de estado.
En el informe real del 03, los 5.494 vienen íntegros de `threatfox`, que está **`parcial`**;
`cisa-kev` aporta 0. La portada publica «5.494 indicadores normalizados» como cifra destacada,
sin la salvedad que el propio informe sí lleva (suprime el diferencial y el panorama de esa
fuente por esa misma razón).

Es menos grave que el hallazgo 1 —el recuento bruto sí corresponde a registros observados, no a
un cálculo suprimido— pero el sitio publica una cifra procedente de una recolección que el
informe declara incompleta, sin ninguna marca. La distinción entre «esto se observó entero» y
«esto se observó a medias» desaparece en el HTML.

---

### RELEVANTE 6 — Todos los enlaces de comprobación apuntan a un repositorio que el README declara privado

**Ficheros:** `sitio/render.py:116` (botón «El back — Repositorio», en las tres vistas y en cada
página de informe), `sitio/render.py:310,329` («Ver el fichero original en el repositorio →»),
`sitio/contenido.py:15`; contrastado con `README.md` (tabla de secretos:
`TOKEN_LECTURA_PIPELINE` … «leer `reports/` del pipeline, que es un repositorio privado») y
`.github/workflows/desplegar.yml:41-44`.
**Categoría:** 5.

El lema del sitio es «Un CV dice lo que sabes hacer. Aquí puedes comprobarlo», y el mecanismo de
comprobación que ofrece es el enlace al repositorio. Con el pipeline privado, ese botón y cada
enlace «Ver el fichero original» devuelven 404 a todo visitante que no sea el propietario. El
sitio no lo declara en ningún sitio; el README lo sabe y no lo conecta con esta consecuencia.

Es un requisito del encargo («los informes se leen de `reports/`… el archivo navegable»)
satisfecho en el generador y roto en la superficie que el lector usa para verificar.

---

### MENOR 7 — `panorama_disponible` se calcula y no lo lee nadie

**Fichero:** `sitio/lector.py:75,303`. **Categoría:** 5.

`grep -rn panorama_disponible --include=*.py` da exactamente dos usos, ambos su propia
definición y asignación. `render.py` no lo consulta. Es, además, el campo que habría permitido
resolver el hallazgo 1 si su valor viniera de la declaración explícita del informe («No se
publica el panorama de familias») en vez de de la presencia de una cifra.

---

### MENOR 8 — El comentario del disparo afirma una garantía que la guarda no da, y el camino que sí ocurre no está cubierto

**Fichero:** `threat-intel-pipeline/.github/workflows/daily.yml`, paso «Reconstruir el sitio del
portafolio» (líneas +180 a +212 del diff). **Categorías:** 1, 9.

El comentario justifica `if: steps.commit.outputs.publicado == 'true'` diciendo que «uno
incondicional tras un fallo total republicaría con las cifras de ayer sin que nada lo dijera».
La guarda no evita ese caso: el paso de commit corre con `if: always()` y —según su propio
comentario, dos líneas más arriba— **un fallo total sí commitea su informe**. Luego
`publicado=true` y el disparo se emite igualmente.

Lo que ocurre entonces es distinto de lo que el comentario teme, y tampoco está declarado: el
sitio se reconstruye tomando el informe de fallo total como el más reciente
(`construir.py:45`, `informes[0]`), y portada y proyecto pasan a guiones —comportamiento
verificado sobre `tests/fixtures/2026/2026-07-30-fallo-total.md`, que da `modo=fallo total` y
las cuatro cifras en `None`—. Puede ser el comportamiento correcto (una ausencia declarada), pero
no es el que el comentario describe, y ningún test lo cubre en ninguno de los dos repositorios.

Lo que la guarda sí evita es el disparo cuando no hubo cambios que commitear. Eso es real y es
menos de lo que el comentario dice.

---

### MENOR 9 — Los cuatro tests del disparo comprueban presencia de cadenas en el YAML

**Fichero:** `threat-intel-pipeline/tests/test_workflow_diario.py`, bloque añadido.
**Categoría:** 4.

`assert "steps.commit.outputs.publicado == 'true'" in ejecutable` pasa igualmente si el `if:`
cuelga del paso equivocado, si el paso está deshabilitado, o si la cadena aparece en un
comentario. No se ejecutó mutación sobre ellos por presupuesto; se declara como no verificado
más abajo. Es la clase de test que el propio proyecto llama, en otros sitios, comprobación que no
comprueba lo que dice.

---

### MENOR 10 — El formato del informe es un contrato externo sin canario

**Fichero:** `sitio/lector.py:127-133` (`_campo_cabecera`), `258-269` (`_modo`), `158`, `188`,
`199`, `239`. **Categoría:** 2.

Todo el lector depende de cadenas literales del renderizador del pipeline: `- **Modo del
informe:**`, `### Estado de recolección por fuente`, `denominador: **N familias observadas**`,
`` `familia_sin_entrada`: N de N familias ``, `### Cálculos no publicados en esta ejecución`. El
pipeline tiene un workflow de verificación de contratos para sus fuentes; el sitio no tiene nada
equivalente para la suya, que es el pipeline.

El modo de fallo concreto: `_modo()` cae a `DIFERENCIAL` por defecto cuando no encuentra el campo
de cabecera y no ve «fallo total» en los primeros 800 caracteres (`lector.py:261-263`). Un
renombrado del campo publicaría todo informe como diferencial en silencio, incluidas las líneas
base, que es la distinción de vocabulario que el pipeline se toma más trabajo en mantener. Los
guiones y separadores del texto (`—`, `·`) y la marca `⏰` de plazo próximo son igualmente
contrato no verificado.

---

## OPSEC (categoría 8) — recorrida, sin hallazgo

- `desplegar.yml`: `permissions: {}` global; `contents: read` en el job de construcción;
  `pages: write` + `id-token: write` **solo** en el job de despliegue. Las cuatro acciones de
  terceros van fijadas por SHA de commit con la versión en comentario.
- **El sitio no se despliega si la construcción falla**: `desplegar` declara `needs: construir`,
  y `construir.py` devuelve 1 sin informes. Verificado también en la suite
  (`test_sin_informes_la_construccion_falla`, `test_sin_directorio_de_informes...`), incluida la
  ausencia del directorio de salida.
- El token del disparo viaja por cabecera `Authorization`, no por URL ni por `echo`; no hay
  `set -x` en el paso; su ausencia se declara con `::warning::` y no revienta.
- No se encontraron secretos, claves ni correos de terceros en el repositorio del sitio. El único
  dato personal publicado es el nombre y un correo de contacto del propio titular, deliberados.
- Sin JavaScript, sin formularios, sin analítica: verificado por mutación (M1, M2, M4).

---

## Qué NO pude verificar

1. **Mutación sobre los tests del disparo** (hallazgo 9): no se ejecutó ninguna mutación en
   `threat-intel-pipeline` por presupuesto y por no tocar el otro repositorio. La afirmación de
   que pasarían con el `if:` en el paso equivocado es lectura, no ejecución.
2. **Render en un navegador real por debajo de 700 px.** La revisión de móvil fue estática sobre
   `estilo.css`: las dos reglas que el README promete existen y son coherentes
   (`@media (max-width: 900px)` para el archivo con `overflow-x: auto` y objetivo táctil de 44 px;
   `@media (max-width: 700px)` que apila la tabla con `td::before { content: attr(data-columna) }`
   y `thead` oculto accesiblemente; `min-width: 0` en la rejilla, `minmax(0, 1fr)` en todas las
   columnas). **No se comprobó desbordamiento real** de cadenas largas sin espacios —CVE, digest,
   URL del enlace al fichero— ni se encontró ninguna regla `overflow-wrap` / `word-break` en la
   hoja. Es la comprobación que haría falta y que no cabía en el presupuesto.
3. **El valor correcto de `("467", "pruebas automatizadas")`** frente a las 449 que declara el
   cierre de fase 4 del pipeline. No se contó la batería real.
4. **El comportamiento con más de dos informes** en el archivo: solo hay dos informes reales y
   cinco fixtures. El recorte, la ordenación y la tira desplazable del archivo no se ejercitaron
   con una serie larga.
5. **`repository_dispatch` de extremo a extremo**: ninguno de los dos repositorios existe todavía
   en GitHub, de modo que el disparo, los permisos de los tokens finos y el `CNAME` sobre
   `vigiabref.com` no se han observado funcionando. Todo lo dicho sobre ellos es lectura de YAML.
6. **Categorías 6, 7 y 11** de la taxonomía, no recorridas.

---

## Recuento por severidad

| Severidad | Nº |
|---|---|
| **BLOQUEANTE** | **2** |
| **RELEVANTE** | **4** |
| **MENOR** | **4** |
| **Total** | **10** |

Los dos bloqueantes son el mismo suceso visto desde los dos lados: el sitio republica una
magnitud que el informe suprime (1), y el aparato de verificación está calibrado sobre un caso
construido para que eso no se vea (2). Cerrar solo el primero dejaría el segundo intacto y el
siguiente defecto de la misma clase volvería a pasar en verde.

---

## Observación de proceso

No se escribe fila en `docs/metricas-revision.md`: ese registro es del pipeline y este es otro
proyecto. **Si el sitio va a revisarse con este protocolo de forma recurrente, necesita su propio
registro y su propio `docs/protocolo-revision.md`, o una declaración explícita de que hereda los
del pipeline.** Hoy no tiene ninguno de los dos, y esta acta es el primer artefacto de
`docs/revisiones/` del repositorio: se ha creado el directorio para alojarla.

Segunda observación: `/home/user/portafolio` **no está bajo control de versiones**. La regla del
protocolo que exige commitear el acta sin modificar, y la propia comprobación de que un revisor
no dejó mutaciones detrás, no son ejecutables hasta que lo esté.

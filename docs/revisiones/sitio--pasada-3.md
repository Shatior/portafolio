# Revisión independiente — retirada del dominio, `--base` obligatorio y absoluto · pasada 3

- **Revisor:** sesión de agente independiente. No implementó el cambio ni tuvo su contexto.
  Informa, no corrige.
- **Fecha:** 2026-08-10
- **Corpus (R1):** el diff de `claude/retirar-dominio` contra `main` en `/home/user/portafolio`
  (`construir.py`, `sitio/rutas.py`, `sitio/render.py`, `sitio/contenido.py`,
  `tests/test_sitio.py`, `estatico/estilo.css`, `pyproject.toml`,
  `.github/workflows/desplegar.yml`, `README.md`, y la eliminación de `dominio.txt`), leídos
  además enteros y no solo en el diff. Se ejecutó la batería, se construyó el sitio de verdad
  **bajo prefijo** (`--base https://shatior.github.io/portafolio`) y **en raíz**
  (`--base https://ejemplo.test`), y se sondeó `sitio.rutas.interpretar` con ocho `--base`
  límite fuera de la batería. Del protocolo se leyeron la taxonomía numerada, las reglas y las
  secciones R1–R6; como referencia de formato, únicamente el acta de la pasada 2. No se
  leyeron `docs/proceso-pendiente.md` ni el resto del histórico de actas.
- **Presupuesto (R2):** 10 minutos / 30 mutaciones. Consumido: **~14 min y 19 mutaciones**. El
  presupuesto de tiempo se agotó antes que el de mutaciones y **se excedió**: ~4 min se fueron
  en diagnosticar dos fallos de batería que resultaron ser artefacto del propio arnés de
  mutación (un `__pycache__` obsoleto tras restaurar un fichero), no del código revisado. Queda
  declarado porque una desviación de presupuesto silenciosa contamina la serie del registro. El
  acta es **incremental** y su cobertura declarada abajo lo refleja.
- **Independencia:** las 19 mutaciones se aplicaron sobre copias previas
  (`cp <fichero> /tmp/rev3bak/`) y se restauraron desde ellas, **sin** `git checkout --`. Tras
  restaurar se limpiaron los `__pycache__` y se verificó explícitamente que
  `git status --short` queda vacío y que la batería vuelve a dar **53 en verde**, cinco
  ejecuciones seguidas. Los únicos ficheros que esta sesión escribe son este acta y su fila en
  `docs/metricas-revision.md`.

---

## Cobertura declarada contra la taxonomía numerada

Orden seguido: el de R6 (prioridad por consecuencia en producción), no el numérico.

| # | Categoría | Recorrida |
|---|---|---|
| 1 | Conjetura presentada como verificación | **Sí** — hallazgo 4 |
| 2 | Contrato externo no verificado | **No, salvo por lectura.** El contrato externo aquí sigue siendo GitHub Pages —qué hace con un `CNAME` presente o ausente y dónde busca el `robots.txt`—, y esta sesión no tiene acceso al servicio ni al panel. Se declara no verificado, no se conjetura |
| 3 | Validez sintáctica con sentido incorrecto | **Sí** — hallazgos 3, 8 |
| 4 | Alarma degenerada | **Sí** — hallazgos 3, 4, 5, 7 |
| 5 | Requisito de la especificación no satisfecho pese a estar implementado | **Sí, sin hallazgo.** El requisito del cambio —que ninguna URL del sitio se derive de una constante— se cumple: canónica, `og:url`, sitemap, `robots.txt` y todas las rutas internas salen de `Base`, y el grep sobre la **salida generada** de las dos construcciones no encuentra `vigiabref`, `contacto@`, `mailto` ni `CNAME` |
| 6 | Coste operativo no considerado | **No recorrida** — el cambio no añade ejecución, almacenamiento ni llamadas a terceros; retira una lectura de fichero |
| 7 | Deriva entre especificación y código | **Sí** — hallazgos 1, 2, 6, 9 (aquí el README y los comentarios de `construir.py` son la única especificación escrita) |
| 8 | Requisitos de OPSEC | **Sí, sin hallazgo.** El workflow mantiene `permissions: {}` en la raíz y los mínimos por job, las tres acciones siguen fijadas por SHA, y el cambio **retira** un dato personal del material publicado (el buzón del pie). El nombre completo del propietario pasa a ser la marca del encabezado: es material de portafolio y publicarlo es su fin, se anota sin severidad |
| 9 | Simetría de modos de fallo | **Sí** — hallazgo 3 (la guarda contra `//host` se calibró para la forma de `--base` que este cambio elimina y no para la que deja) |
| 10 | Defecto introducido por una corrección | **Sí** — hallazgos 4, 5. El cambio es en sí la corrección del bloqueante de la pasada 2, y los dos hallazgos están en las líneas escritas para cerrarlo |
| 11 | Penalización de la propia retirada | **Sí** — hallazgo 2. La retirada del dominio se hizo sin coste; lo que sí tiene coste es la **reposición**, y el procedimiento que la documenta es el que falla |

---

## Mutaciones ejecutadas

Diecinueve mutaciones, aplicadas de una en una sobre el árbol limpio y revertidas siempre.
Batería de referencia: **53 en verde**.

| # | Mutación | Resultado | Qué murió |
|---|---|---|---|
| M1 | `construir.py` vuelve a escribir un `CNAME` en la raíz del sitio | **Muerta** | `test_no_se_escribe_cname_en_ninguna_construccion` |
| M2 | La marca del encabezado vuelve a ser el literal `vigiabref.com` | **Muerta** | `test_el_dominio_descartado_no_sobrevive_en_ninguna_pagina` |
| M3 | El pie recupera `mailto:contacto@vigiabref.com` | **Muerta** | `test_el_pie_no_ofrece_un_buzon_que_no_recibe`, `test_el_dominio_descartado…` |
| M4 | `Base.url` descarta el origen y devuelve solo prefijo + camino | **Muerta** | `test_las_canonicas_y_el_sitemap…`, `test_servido_en_raiz…`, `test_el_esquema_en_mayusculas…` |
| M5 | El sitemap compone sus `<loc>` con `Base.ruta` en vez de `Base.url` | **Muerta** | `test_las_canonicas_y_el_sitemap…`, `test_servido_en_raiz…` |
| M6 | El `robots.txt` declara el sitemap con una ruta, no con una URL absoluta | **Muerta** | `test_las_canonicas_y_el_sitemap…` |
| M7 | **`--base` deja de ser obligatorio**: `required=True` → `default="https://vigiabref.com"` | **SOBREVIVE** — 53/53 en verde | nada → **hallazgo 4** |
| M8 | El prefijo deja de despojarse de su barra final | **Muerta por equivalencia** — 53/53, pero la mutación no cambia el comportamiento (el `rstrip("/")` de entrada ya la quitó). No cuenta como superviviente |
| M9 | `interpretar` acepta un prefijo suelto sin esquema | **Muerta** | `test_un_prefijo_relativo_se_rechaza…`, `test_un_base_que_no_es_un_prefijo_se_rechaza[//evil.example/portafolio]` |
| M10 | Se retira el rechazo del **espacio** en `--base` | **SOBREVIVE** — 53/53 en verde | nada → **hallazgo 5** |
| M11 | Se retira el rechazo del **fragmento `#`** en `--base` | **SOBREVIVE** — 53/53 en verde | nada → **hallazgo 5** |
| M12 | El `--base` se valida **después** de `shutil.rmtree(destino)` | **Muerta** | `test_un_prefijo_relativo_se_rechaza_y_no_borra_el_sitio_anterior`, `test_sin_base…` |
| M13 | El esquema deja de aceptar mayúsculas | **Muerta** | `test_el_esquema_en_mayusculas_se_acepta` |
| M14 | Un `--base` sin host deja de rechazarse | **Muerta** | `test_un_prefijo_relativo…`, `test_sin_base…` |
| M15 | El `PIE` afirma que las tipografías vienen de Google Fonts | **Muerta** | `test_ningun_recurso_de_terceros` (comprobada por separado tras limpiar `__pycache__`) |
| M16 | La navegación emite sus `href` sin pasar por `Base.ruta` | **Muerta** | `test_ninguna_ruta_interna_apunta_a_la_raiz_bajo_prefijo` |
| M17 | La hoja de estilo se enlaza con una ruta absoluta fija | **Muerta** | `test_ninguna_ruta_interna_apunta_a_la_raiz_bajo_prefijo` |
| M18 | Se retira el rechazo de `..` en `--base` | **Muerta** | `test_un_prefijo_relativo…` (por vía indirecta; la guarda de `..` en sí no la ejercita ningún caso con esquema — ver hallazgo 5) |
| M19 | Sonda, no mutación: ocho `--base` límite contra `interpretar` (`https://h//p`, salto de línea interior, host en mayúsculas, puerto, `user:pw@`, `%20`, barra final, `HTTPS://`) | — | origen de los **hallazgos 3, 7, 8** |

**Conclusión de las mutaciones.** El núcleo del cambio está bien atado: las trece mutaciones que
tocan el camino origen→prefijo→canónica→sitemap→rutas internas mueren todas, y las tres nuevas
comprobaciones sobre la **salida generada** (dominio descartado, buzón, `CNAME`) hacen su
trabajo — M1, M2 y M3 mueren limpiamente. Los tres supervivientes reales caen en el mismo sitio:
**la frontera de entrada de `--base`**, que es exactamente la pieza que este cambio ascendió de
opcional a obligatoria.

---

## Hallazgos

### RELEVANTE 1 — El procedimiento para reponer el `CNAME` cita un test que este mismo diff renombró

**Fichero:** `construir.py:96`.
**Categorías:** 7.

El paso 3 del procedimiento dice, literalmente:

> `test_el_despliegue_pasa_el_prefijo_con_el_que_se_sirve` romperá al hacerlo, y esa es su
> función: obligar a que las dos cosas se muevan juntas.

Ese test **no existe**. El propio diff lo renombró a
`test_el_despliegue_pasa_la_url_con_la_que_se_sirve` (`tests/test_sitio.py:333`); el nombre
viejo solo sobrevive en este comentario y en un `.pyc`. `README.md:60` remite a `construir.py`
como el lugar donde está «el procedimiento completo», de modo que quien lo siga el día que haya
dominio buscará una red de seguridad por un nombre que no está en el repositorio. Es la clase de
referencia rota que el protocolo trata como defecto de aplicación, no como errata: el
procedimiento es lo único que queda del mecanismo retirado.

---

### RELEVANTE 2 — Los dos procedimientos de reposición se contradicen en el orden, y el que se declara «completo» es el incompleto

**Ficheros:** `construir.py:88-99` y `README.md:162-172`.
**Categorías:** 7, 11.

Existen dos copias del mismo procedimiento y no dicen lo mismo:

| | `construir.py:90-94` | `README.md:163-167` |
|---|---|---|
| 1 | escribir el `CNAME` | DNS + `Settings → Pages` |
| 2 | DNS + `Settings → Pages` | escribir el `CNAME` |
| 3 | cambiar `--base` | cambiar `--base` |

El README encabeza su lista con «**Tres pasos, y el orden importa**» (`README.md:162`) y a
continuación remite al otro documento como fuente («donde está el procedimiento completo»,
`README.md:165`). Si el orden importa, hay una de las dos listas que es la incorrecta y ninguna
señal de cuál.

Y hay una asimetría peor. El README nombra **los dos** tests que romperán —
`test_el_despliegue_pasa_la_url_con_la_que_se_sirve` y
`test_no_se_escribe_cname_en_ninguna_construccion` (`README.md:170-171`)—; `construir.py` nombra
**solo uno**, y encima con el nombre viejo (hallazgo 1). El procedimiento que el README declara
«completo» es, de los dos, el que omite que el test que este mismo diff introdujo para vigilar
la ausencia del `CNAME` es precisamente el que hay que tocar al reponerlo. Confirmado con M1:
escribir el `CNAME` mata `test_no_se_escribe_cname_en_ninguna_construccion` y nada más.

Esto es la categoría 11 en su forma menos visible: el mecanismo se retiró sin coste, pero
**reponerlo** cuesta seguir un procedimiento que contiene una referencia rota, un orden en
disputa y una omisión, y ese coste no aparece en ninguna discusión sobre la decisión.

---

### RELEVANTE 3 — La guarda contra `//host` protege la forma de `--base` que el cambio elimina, no la que deja

**Fichero:** `sitio/rutas.py:88-103`.
**Categorías:** 3, 4, 9.

`interpretar` razona explícitamente sobre el peligro (`rutas.py:90-94`):

> `//host/camino` empieza por barra y **no es una ruta**: es una referencia de red, que el
> navegador resolvería contra otro host conservando el esquema.

Pero esa pista y ese rechazo viven **dentro de la rama que dispara cuando falta el esquema**, es
decir, para la forma de `--base` que a partir de ahora se rechaza siempre. En la forma que sí se
acepta —URL absoluta— nada lo comprueba. Verificado en ejecución (M19):

```
interpretar("https://shatior.github.io//portafolio")
  → Base(origen='https://shatior.github.io', prefijo='//portafolio')
  → ruta("/estatico/estilo.css") == "//portafolio/estatico/estilo.css"
```

Toda ruta interna del sitio —hoja de estilo, precarga de la tipografía, navegación, botones,
archivo de informes— sale como referencia de red hacia un host llamado `portafolio`. Con
`https://shatior.github.io//evil.example` el sitio que promete no cargar recursos de terceros
los cargaría **todos** desde uno. Y la construcción **termina en verde**:
`test_ninguna_ruta_interna_apunta_a_la_raiz_bajo_prefijo` solo exige que las rutas empiecen por
`/portafolio/`, y `//portafolio/…` lo cumple; el resto de la batería usa un `--base` fijo.

Una barra doblada es una errata plausible en la única línea del repositorio donde se escribe la
URL de publicación (`desplegar.yml:73`). La lista de prohibidos de `rutas.py:76-85` rechaza `?`,
`#`, `..`, espacio y tabulador «antes de repartir»; `//` en el camino es el caso que el propio
módulo argumenta como el más grave y el único que no está en ella.

No se marca BLOQUEANTE porque el valor que hoy pasa el despliegue es correcto y está atado por
`test_el_despliegue_pasa_la_url_con_la_que_se_sirve`. Es un agujero latente, no un fallo activo.

---

### RELEVANTE 4 — «Olvidarlo no compila» es la afirmación central del cambio y es la única que no verifica nada

**Ficheros:** `construir.py:155-165`, `tests/test_sitio.py:353-362`; afirmada en
`README.md:45-47`, `construir.py:7` y `sitio/rutas.py:58-63`.
**Categorías:** 1, 4, 10.

La decisión que sustituye a `dominio.txt` es que `--base` no tenga valor por defecto, y se
enuncia tres veces con la misma fórmula: «sin valor por defecto, olvidarlo **no compila**». Esa
propiedad vive en una sola línea, `required=True` en `construir.py:157`, y **ningún test la
toca**.

Evidencia (M7): sustituir `required=True` por `default="https://vigiabref.com"` —o sea, deshacer
el cambio y reponer el dominio descartado como valor por defecto— deja la batería en **53 en
verde**. El test que parece cubrirlo, `test_sin_base_la_construccion_falla`, llama a
`construir(FIXTURES, tmp_path / "publico", "")`: comprueba la **función**, que recibe la cadena
vacía, no la capa de `argparse` donde vive la obligatoriedad. Son propiedades distintas y la
segunda es la que el README promete.

Detrás hay algo más general: **ningún test invoca `construir.py` como proceso**. No hay
`subprocess` en `tests/`, de modo que `main()`, el análisis de argumentos, el código de salida y
el guardián `if __name__ == "__main__"` quedan enteros fuera de la batería. El protocolo trata
esto por su nombre en la regla 6 —«todo punto de entrada ejecutable necesita una prueba que lo
invoque como proceso»— y con un incidente real detrás: un script inejecutable con once tests en
verde porque todos lo importaban.

Se comprobó a mano que la propiedad **hoy se cumple** (`python3 construir.py --informes … --salida …`
sin `--base` sale con código 2 y el mensaje de `argparse`). El hallazgo no es que esté rota: es
que se afirma tres veces como verificada y no hay nada que la sostenga mañana. Es además
categoría 10: la línea sin cubrir es exactamente la escrita para cerrar el bloqueante de la
pasada anterior.

---

### RELEVANTE 5 — El parametrizado de `--base` perdió su alcance al volverse absoluto el argumento

**Fichero:** `tests/test_sitio.py:426-444`.
**Categorías:** 4, 10.

`test_un_base_que_no_es_un_prefijo_se_rechaza` conserva sus cinco casos de la etapa anterior:
`//evil.example/portafolio`, `/portafolio?v=2`, `/portafolio#inicio`, `/portafolio/../otro`,
`/porta folio`. **Los cinco son prefijos sueltos sin esquema**, de modo que ahora los rechaza la
comprobación de URL absoluta de `rutas.py:88` y **ninguno llega jamás a la lista de caracteres
prohibidos** de `rutas.py:76-85`. El test sigue verde, pero ya no verifica lo que su docstring
dice verificar.

Confirmado con dos mutaciones: M10 (se retira el rechazo del espacio) y M11 (se retira el
rechazo del fragmento `#`) **sobreviven las dos con 53 en verde**. Es decir, la lista de
prohibidos está hoy sin cubrir para la única forma de `--base` que el programa acepta:
`https://host/porta folio` y `https://host/p#inicio` no los ejercita nada.

Es un caso de libro de pérdida de alcance al unificar los fixtures: la batería pasó a construir
todo bajo `BASE_PUBLICACION`, se reescribieron los tests de canónicas y sitemap, y este quedó
con sus valores viejos, que el cambio de contrato convirtió en redundantes entre sí — cinco
casos que hoy comprueban una sola cosa, la misma que ya comprueba
`test_un_prefijo_relativo_se_rechaza_y_no_borra_el_sitio_anterior`.

---

### MENOR 6 — `render.py` remite a una constante que el diff eliminó

**Ficheros:** `sitio/render.py:43-45`, `sitio/contenido.py:17-22`.
**Categorías:** 7.

El docstring de `_pagina` dice «el motivo largo está en `contenido.CORREO`». `CORREO` ya no
existe: el diff lo sustituyó por un comentario `#:` sin nombre delante de `NOMBRE`
(`contenido.py:17-22`), que es una buena decisión —conserva el razonamiento sin conservar el
dato— mal referenciada. Quien busque `CORREO` en el repositorio no encontrará nada. El mismo
comentario cierra con «entonces vuelve aquí y al pie de `render.py`», que sí es exacto.

---

### MENOR 7 — Los saltos de línea interiores no están en la lista de prohibidos, con el mismo argumento que sí prohíbe el espacio

**Fichero:** `sitio/rutas.py:76-85`.
**Categorías:** 4.

La lista rechaza `" "` y `"\t"` con el motivo «no sobrevive a un atributo HTML sin escaparse».
`\n` y `\r` interiores no están: `base.strip()` solo despoja los de los extremos. Verificado
(M19): `interpretar("https://host/a\nb")` devuelve `prefijo='/a\nb'` y el sitio se construye con
un salto de línea dentro de cada `href`, de cada `src`, de la canónica, del `og:url` y de los
`<loc>` del sitemap. No hay riesgo de inyección —`esc()` cubre lo que importa— pero el argumento
que justifica prohibir el espacio se aplica igual y la guarda no.

---

### MENOR 8 — El host no se normaliza a minúsculas, y un test fija esa conducta

**Ficheros:** `sitio/rutas.py:103`, `tests/test_sitio.py:447-457`.
**Categorías:** 3.

`Base(origen=f"{esquema.lower()}://{host}", …)`: se normaliza el esquema y no el host.
`test_el_esquema_en_mayusculas_se_acepta` construye con
`HTTPS://Shatior.github.io/portafolio` y **asserta** que la canónica sale como
`https://Shatior.github.io/portafolio/`. Aceptar el esquema en mayúsculas es correcto y está
bien argumentado; emitir la canónica con el host tal cual se escribió lo es menos —una canónica
es una afirmación sobre cuál es la URL buena de la página—, y el test lo convierte de conducta
tolerada en conducta fijada. El caso sonda `https://HOST.Example/X` lo reproduce. Consecuencia
práctica baja: el valor real del despliegue ya viene en minúsculas.

---

### MENOR 9 — Retirar el contacto no deja defecto de accesibilidad ni de SEO; lo que queda conviene decirlo

**Ficheros:** `sitio/render.py:83-88`, `estatico/estilo.css:508-524`.
**Categorías:** 7.

Comprobado sobre el HTML **generado** de las dos construcciones, no sobre el código:

- El pie conserva su envoltorio `<div class="pie-enlaces">` con un único enlace. El CSS
  (`.pie-enlaces`, `estilo.css:514-525`) no asumía dos hijos: no queda hueco, ni separador
  colgando, ni regla muerta. Correcto.
- No queda `mailto:` en ninguna página, y `test_el_pie_no_ofrece_un_buzon_que_no_recibe` lo
  vigila (M3 lo mata).
- El único enlace del pie lleva `rel="noopener"` sin `target="_blank"`. Es inerte, no un
  defecto, y ya estaba antes del cambio.
- No había `<address>`, ni datos estructurados, ni `og:image`, de modo que **no hay regresión de
  SEO**: no se retira ningún marcado, solo texto.
- Lo que sí cambia y no está escrito en ninguna parte del diff: el sitio queda **sin ninguna vía
  de contacto** salvo el enlace a GitHub, en un documento cuyo propósito es que alguien
  contacte. El README no lo menciona en ninguna de sus secciones. Es decisión declarada del
  propietario y no se objeta; se anota porque la decisión vive hoy solo en un comentario de
  `contenido.py:17-22` y en un test, y el README es el documento que un lector externo abre.

---

## Lo que NO se pudo verificar

- **El comportamiento real de GitHub Pages** sin `CNAME`: que servir bajo
  `shatior.github.io/portafolio/` funcione y que la ausencia del fichero sea efectivamente
  inocua. Sin acceso al servicio ni al panel desde esta sesión. Es el mismo hueco que declaró la
  pasada 2, y sigue abierto: el cambio invierte la decisión que aquella pasada bloqueó, y esa
  inversión tampoco está contrastada contra el sistema que la ejecuta.
- **Que el procedimiento de reposición del `CNAME` funcione**, más allá de que sus referencias
  internas sean correctas —que no lo son, hallazgos 1 y 2—. Que Pages lea un `CNAME` presente en
  el artefacto de `upload-pages-artifact` y no solo en una rama, en particular, no se ha
  comprobado: se lee como plausible y se declara no verificado.
- **El renderizado en un navegador** de ninguna de las dos construcciones. La comprobación es
  estática sobre el HTML y el CSS generados.
- **El sitio construido contra los informes reales del pipeline.** Solo se construyó contra
  `tests/fixtures`, cuyos seis informes cubren el panorama publicado, el fallo total y la
  ausencia de familias, pero no lo que el repositorio real contenga hoy.
- **Las once mutaciones no ejecutadas** del presupuesto de 30, agotado por tiempo. Quedaron sin
  ejercitar, entre otras: el orden relativo de `copytree` y la escritura de `robots.txt`; el
  comportamiento con `--salida` apuntando a un fichero existente; y las guardas de carácter
  aplicadas a un `--base` **con** esquema, que es justo lo que el hallazgo 5 señala que la
  batería no cubre.
- **Las categorías 2 y 6**, declaradas no recorridas arriba.

---

## Recuento

| Severidad | Nº |
|---|---|
| BLOQUEANTE | 0 |
| RELEVANTE | 5 |
| MENOR | 4 |

**Categorías con hallazgo:** 1, 3, 4, 7, 9, 10, 11.

**Lectura de conjunto, para que el recuento no engañe.** La decisión de fondo —no sustituir un
dominio por otro, sino retirar la constante— es correcta y está bien ejecutada donde más importa:
la salida generada no contiene ni el dominio descartado ni el buzón ni un `CNAME`, y eso se
comprueba **sobre los ficheros escritos**, que es el artefacto concluyente. Dieciséis de
diecinueve mutaciones mueren, y las tres comprobaciones nuevas sobre la salida hacen exactamente
lo que dicen. **Cero bloqueantes.**

Los cinco relevantes se agrupan en dos sitios, y ninguno de los dos es el código que el cambio
escribió para renderizar: son **la frontera de entrada de `--base`** —que ascendió de opcional a
obligatoria sin que su cobertura ascendiera con ella (hallazgos 3, 4, 5)— y **el procedimiento
escrito que sustituye al mecanismo retirado** (hallazgos 1, 2). Es coherente con lo que la
categoría 11 predice: cuando se retira un mecanismo, lo que queda a medio hacer no es lo que se
quita, sino la documentación de cómo volver.

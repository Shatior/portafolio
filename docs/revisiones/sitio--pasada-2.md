# Revisión independiente — `--base`, el sitio servido bajo un prefijo · pasada 2

- **Revisor:** sesión de agente independiente. No implementó el cambio ni tuvo su contexto.
  Informa, no corrige.
- **Fecha:** 2026-08-10
- **Corpus (R1):** el diff de `claude/prefijo-base` contra `main` en `/home/user/portafolio`
  (`sitio/rutas.py` nuevo, `sitio/render.py`, `construir.py`, `estatico/estilo.css`,
  `tests/test_sitio.py`, `.github/workflows/desplegar.yml`, `README.md`), leídos además enteros
  y no solo en el diff. Se ejecutó la batería y se construyó el sitio de verdad con y sin
  prefijo, y se construyó también con el código de `main` para comparar árboles. No se leyeron
  `docs/decisiones.md` ni `docs/proceso-pendiente.md`, ni el acta de la pasada 1 más allá de su
  formato.
- **Presupuesto (R2):** 10 minutos / 30 mutaciones. Consumido: **~11 min y 14 mutaciones**. El
  presupuesto de tiempo se agotó antes que el de mutaciones; el acta es **incremental** y su
  cobertura declarada abajo lo refleja.
- **Independencia:** las catorce mutaciones se revirtieron con `git checkout -- <fichero>` y se
  verificó explícitamente que `git status --short` queda vacío antes de escribir este fichero.
  La batería vuelve a dar **43 en verde**. Los únicos ficheros que esta sesión escribe son este
  acta y su fila en `docs/metricas-revision.md`.

---

## Cobertura declarada contra la taxonomía numerada

| # | Categoría | Recorrida |
|---|---|---|
| 1 | Conjetura presentada como verificación | **Sí** — hallazgos 1, 2, 3 |
| 2 | Contrato externo no verificado | **Sí, parcialmente** — el contrato externo aquí es GitHub Pages (cómo trata el `CNAME` publicado y dónde busca el `robots.txt`); no se pudo comprobar contra el servicio real, y eso es justamente el hallazgo 1 |
| 3 | Validez sintáctica con sentido incorrecto | **Sí** — hallazgos 5, 9 |
| 4 | Alarma degenerada | **Sí** — hallazgos 3, 4, 7, 8 |
| 5 | Requisito de la especificación no satisfecho pese a estar implementado | **Sí** — hallazgos 1, 6 |
| 6 | Coste operativo no considerado | **No** — el cambio no añade ejecución ni almacenamiento; no se recorrió |
| 7 | Deriva entre especificación y código | **Sí** — hallazgos 2, 3 (el README es aquí la única especificación escrita) |
| 8 | Requisitos de OPSEC | **Sí, superficialmente** — sin hallazgo: el workflow no amplía permisos, las acciones siguen fijadas por SHA y `--base` no introduce ningún secreto |
| 9 | Simetría de modos de fallo | **Sí** — hallazgos 4, 5, 7 |
| 10 | Defecto introducido por una corrección | **Sí** — el cambio es en sí una corrección de un modo de fallo declarado («el sitio saldría sin hoja de estilo»); los hallazgos 1 y 3 son defectos que trae la propia corrección |
| 11 | Penalización de la propia retirada | **Sí** — sin hallazgo, y con evidencia: la mutación M14 retira `--base` del workflow y la batería sigue en verde. Retirar el mecanismo no rompe nada, que es lo que la categoría pide. Su cara opuesta sí es un hallazgo (el 8) |

---

## Mutaciones ejecutadas

| # | Mutación | Resultado | Qué murió |
|---|---|---|---|
| M1 | La canónica de `render._pagina` vuelve a `https://vigiabref.com{canonico}`, ignorando la base | **Muerta** | `test_las_canonicas_y_el_sitemap_declaran_donde_se_sirve_la_copia` |
| M2 | `Base.ruta` devuelve `camino` y descarta el prefijo | **Muerta** | `test_ninguna_ruta_interna_apunta_a_la_raiz_bajo_prefijo` |
| M3 | `Base.url` compone `origen + camino`, sin el prefijo | **Muerta** | `test_las_canonicas_y_el_sitemap…` |
| M4 | `interpretar` deja de rechazar un prefijo relativo | **Muerta** | `test_un_prefijo_relativo_se_rechaza_y_no_borra_el_sitio_anterior` |
| M5 | El `--base` se valida **después** de `shutil.rmtree(destino)` | **Muerta** | `test_un_prefijo_relativo_se_rechaza_y_no_borra_el_sitio_anterior` |
| M6 | Un `href="/aviso/"` nuevo, absoluto, en `_acciones` — «la ruta número catorce» | **Muerta** | `test_ninguna_ruta_interna_apunta_a_la_raiz_bajo_prefijo` |
| M7 | La misma ruta absoluta, pero en un atributo `style`: `<body style="background-image:url(/estatico/fondo.png)">` | **SOBREVIVE** — 43/43 en verde | nada → **hallazgo 4** |
| M8 | El CSS vuelve a pedir la tipografía a `/estatico/fuentes/…` | **Muerta** | `test_la_tipografia_se_sirve_desde_el_propio_dominio`, `test_el_css_no_pide_la_tipografia_a_la_raiz` |
| M9 | El `CNAME` se reescribe con el host provisional | **Muerta** | `test_el_cname_no_lleva_prefijo_ni_cambia_con_el_host_provisional` |
| M10 | Deja de escribirse el `robots.txt` | **Muerta** | `test_robots_y_sitemap…` |
| M11 | El valor por defecto de `construir(..., base=)` pasa a `/portafolio` | **Muerta** | `test_sin_prefijo_el_sitio_es_identico_al_de_siempre` |
| M12 | El sitio en raíz deja de ser «el de siempre»: un comentario HTML nuevo en `<head>`, idéntico en ambas construcciones | **SOBREVIVE** — 43/43 en verde | nada → **hallazgo 3** |
| M13 | El aviso «servido bajo …» nunca se imprime | **SOBREVIVE** — 43/43 en verde | nada → **hallazgo 8** |
| M14 | El workflow despliega sin `--base` (retirada del mecanismo) | **SOBREVIVE** — 43/43 en verde | nada → categoría 11 sin penalización; ver hallazgo 8 |

**Conclusión de las mutaciones.** El núcleo del cambio —`Base`, `interpretar`, el orden de
validación antes de borrar, el CSS relativo, el `CNAME`— está genuinamente ejercitado: once de
catorce mutaciones mueren, y varias mueren en el test que les corresponde y no por accidente.
Lo que **no** está ejercitado es todo lo que vive fuera del par `href`/`src` (M7), la afirmación
de identidad con el sitio anterior (M12), el único aviso que recibe el operador (M13) y el
fichero donde el prefijo realmente vive, el workflow (M14).

Además se construyó tres veces y se leyó la salida:

```
python3 construir.py --informes tests/fixtures --salida /tmp/rev_raiz
python3 construir.py --informes tests/fixtures --salida /tmp/rev_pref --base https://shatior.github.io/portafolio
# y, desde un worktree de `main`:
python3 construir.py --informes …/tests/fixtures --salida /tmp/rev_main
```

En `/tmp/rev_pref` **todas** las rutas internas llevan el prefijo: no se encontró ninguna que se
escape (`href="/portafolio/estatico/estilo.css"`, `href="/portafolio/informes/2026-08-03/"`, …).
El objetivo declarado del cambio, en el árbol de salida, se cumple. Los hallazgos de abajo no
son sobre el árbol: son sobre lo que ocurre cuando ese árbol se sirve, y sobre lo que las
pruebas afirman vigilar y no vigilan.

Y se recorrieron 22 formas de `--base` contra `interpretar` (barras, mayúsculas, `http://`,
puerto, credenciales, query, fragmento, `..`, espacios, `//host`, vacío tras normalizar). De ahí
salen los hallazgos 5 y 9.

---

## Hallazgos

### BLOQUEANTE 1 — El artefacto provisional se publica con un `CNAME` que reclama un dominio que no resuelve, y eso es lo que decide si la URL provisional es alcanzable

**Ficheros:** `construir.py:76-82` (la escritura del `CNAME` y su comentario),
`.github/workflows/desplegar.yml:67-71`, `tests/test_sitio.py:305-312`
(`test_el_cname_no_lleva_prefijo_ni_cambia_con_el_host_provisional`), `README.md:33-38` y
`README.md:169-170`.
**Categorías:** 1, 2, 5, 10.

Todo el cambio existe para que el sitio sea **alcanzable hoy** en
`shatior.github.io/portafolio/` mientras `vigiabref.com` no resuelve. El diff resuelve con
cuidado la parte que se ve en el árbol de salida —las rutas internas— y deja intacta la que
decide si esa URL responde: el fichero `CNAME`, que sigue escribiéndose en la raíz del
artefacto con `vigiabref.com` dentro.

GitHub Pages **no trata el `CNAME` publicado como un fichero más del sitio**: lo lee y fija con
él el dominio personalizado del repositorio. Con el dominio personalizado fijado y su DNS
apuntando a otro sitio, la URL `github.io` del proyecto deja de servir el contenido y redirige
al dominio reclamado — que es exactamente el que no resuelve. Si es así, el resultado del
despliegue no es «el sitio bien servido bajo un prefijo»: es un redirección a ninguna parte, y
el cambio entero no consigue nada.

Lo que hace que esto sea un bloqueante y no una duda es **cómo está tratado en el diff**. La
suposición contraria —que el `CNAME` es inerte— no se comprueba en ningún sitio y se defiende
en tres a la vez:

- un comentario en `construir.py` en negrita: «**No lleva prefijo ni depende de `--base`, y es
  deliberado.** El CNAME no es una ruta del sitio»;
- un párrafo del README: «El `CNAME` y `dominio.txt` no se tocan mientras tanto: siguen siendo
  correctos para el destino final»;
- y un test, `test_el_cname_no_lleva_prefijo_ni_cambia_con_el_host_provisional`, que **fija la
  conducta como correcta por aserción**. La mutación M9 —reescribir el `CNAME` con el host
  provisional— muere contra ese test. Es decir: la batería impide activamente la única
  corrección obvia, y lo hace con un docstring que argumenta desde el destino final
  («entregaría el dominio propio el día que se recupere») sin preguntar si el destino
  provisional es alcanzable.

Tres defensas y ningún dato. Es la categoría 1 en su forma canónica —el código y su prueba
coinciden porque los escribió la misma persona— aplicada al único punto del cambio que no se
puede verificar desde el repositorio. Y es categoría 10: el defecto no existía como decisión
antes de esta corrección; lo trae ella, al elegir explícitamente no tocar el `CNAME`.

**Lo que esta sesión pudo y no pudo verificar,** porque prometer de más aquí sería el mismo
defecto un nivel más arriba: se verificó que el `CNAME` se escribe con `vigiabref.com` en las
dos construcciones, con y sin prefijo, y que ningún test comprueba nada sobre el despliegue
real. **No** se pudo comprobar el comportamiento de GitHub Pages contra el servicio: no hay
acceso al repositorio publicado ni al panel de Pages desde esta sesión. El hallazgo es, con
precisión: *el cambio descansa sobre una afirmación no verificada acerca de un sistema externo,
y si esa afirmación es falsa el cambio no produce ningún sitio accesible*. Es bloqueante porque
la comprobación cuesta un despliegue y una petición, y porque su resultado decide si el resto
del diff sirve para algo.

**Nótese el precedente en el propio README.** Lo que este diff borra es un párrafo que empezaba
por «**Comprobado, no supuesto**, en la ejecución del 2026-08-10» y transcribía el error 404
literal. El proyecto ya sabe cómo se declara un requisito de despliegue: comprobándolo. Aquí no
se hizo.

---

### RELEVANTE 2 — El README afirma como hecho comprobado que Pages está activado y que el sitio se publica hoy, y sustituye con esa afirmación un párrafo que sí estaba comprobado

**Fichero:** `README.md:145-149`.
**Categorías:** 1, 7.

El diff retira el bloque «Requisito de lanzamiento pendiente: Pages no está activado» —que se
apoyaba en una ejecución fechada y en el mensaje de error textual— y lo sustituye por:

> Pages está activado con origen GitHub Actions, de modo que **el sitio se publica hoy en
> [`shatior.github.io/portafolio/`](https://shatior.github.io/portafolio/)**

Sin fecha, sin ejecución citada y sin nada en el repositorio que lo sostenga. No hay en el diff
ningún artefacto —un log, un número de ejecución, una captura— que respalde ni que Pages se
activó ni que el sitio esté publicado; el segundo enunciado es además el que el hallazgo 1 pone
en duda por otra vía.

La asimetría es lo que lo hace relevante y no menor: el proyecto **tenía** en ese mismo párrafo
una afirmación con evidencia, y el cambio la degrada a una sin evidencia mientras sube el
listón de lo que afirma. Un lector del README ya no puede distinguir qué se comprobó. Si la
activación se comprobó, falta decir cuándo y contra qué; si se dedujo de que el workflow ya no
falla, eso es una deducción y se declara como tal.

---

### RELEVANTE 3 — «Byte a byte el sitio de siempre» no está fijado por el test que el README dice que lo fija, y de hecho hoy es falso

**Ficheros:** `tests/test_sitio.py:314-330` (`test_sin_prefijo_el_sitio_es_identico_al_de_siempre`),
`README.md:165-168`, `estatico/estilo.css:19-21`.
**Categorías:** 1, 4, 7.

El README promete:

> sin ella el sitio vuelve a construirse desde la raíz — el resultado es byte a byte el de
> siempre, y hay un test que lo fija (`test_sin_prefijo_el_sitio_es_identico_al_de_siempre`).

El test compara **dos construcciones de esta misma rama**: la del fixture `sitio`
(`construir(FIXTURES, destino)`, con el defecto) contra `construir(FIXTURES, destino, "")`. Lo
que fija es que el argumento por defecto y el vacío explícito coinciden — que es una propiedad
real y útil, y la mutación M11 confirma que la vigila. Pero **no compara nada con «el de
siempre»**: no hay ninguna referencia a `main` en la batería, y ningún fichero congelado contra
el que contrastar.

La mutación M12 lo demuestra: se añade un comentario HTML nuevo al `<head>`, que cambia todas
las páginas de las dos construcciones por igual. Las dos siguen siendo idénticas entre sí, y
**los 43 tests siguen en verde**. Cualquier deriva respecto del sitio anterior es invisible para
este test, por construcción: compara la rama consigo misma.

Y no es hipotético, porque **hoy ya es falso**. Construyendo con el código de `main` y con el
de la rama, ambos sin prefijo, y comparando los árboles con `diff -r`:

```
diff -r /tmp/rev_main/estatico/estilo.css /tmp/rev_raiz/estatico/estilo.css
19c19,21
<   src: url("/estatico/fuentes/InterVariable.woff2") format("woff2");
---
>   /* Relativa a esta hoja, no a la raíz del dominio: … */
>   src: url("fuentes/InterVariable.woff2") format("woff2");
```

El resto del árbol sí es idéntico. La diferencia es **benigna en su efecto** —relativa a la
hoja, `fuentes/…` resuelve a `/estatico/fuentes/…` igual que antes— y probablemente inevitable:
es la única ruta que ningún prefijo puede reescribir, y el cambio la trata bien. Lo que no es
correcto es la frase: el resultado no es byte a byte el de siempre, y el test citado como
garantía no puede detectar que deje de serlo. Es una alarma que no puede dispararse (categoría
4) presentada en el README como la que cierra el riesgo (categoría 1).

---

### RELEVANTE 4 — El vigilante de rutas internas solo mira `href` y `src`: una ruta absoluta en un atributo `style` pasa entera, y este fichero ya usa `style` a menudo

**Fichero:** `tests/test_sitio.py:250-268`
(`test_ninguna_ruta_interna_apunta_a_la_raiz_bajo_prefijo`), con eco en `README.md:160-164`.
**Categorías:** 4, 9, 10.

El test es el que el README nombra como la defensa del modo de fallo, y su propio docstring
declara el alcance que pretende:

> Se comprueba sobre **todos** los `href` y `src` de todas las páginas, no sobre una lista de
> los que hoy existen: el modo de fallo es que alguien añada mañana la ruta número catorce.

La expresión que ejecuta es `re.findall(r'(?:href|src)="([^"]+)"', html)`. Contra un `href`
nuevo funciona: la mutación M6 añade `<a class="boton" href="/aviso/">` y muere. Contra una ruta
absoluta que no viaje en `href` ni en `src`, no ve nada. La mutación M7 pone

```html
<body style="background-image:url(/estatico/fondo.png)">
```

y **los 43 tests siguen en verde**, con el sitio prefijado pidiendo ese fichero a la raíz de
`shatior.github.io` — el fallo exacto que el test existe para impedir, entrando por la puerta
de al lado. Quedan igualmente fuera `srcset`, `content`, `action`, `poster`, `data-*` y
cualquier atributo entre comillas simples.

Lo que lo saca de lo hipotético es que **`sitio/render.py` ya escribe atributos `style` de
forma habitual**: `render.py:211` los usa para las tarjetas de proyecto. La
costumbre existe, de modo que «la ruta número catorce» tiene una vía plausible y frecuentada
para nacer justo donde el guardia no mira. Y el test hermano
`test_el_css_no_pide_la_tipografia_a_la_raiz` cubre el CSS **externo**, lo que refuerza la
impresión de que las `url()` están vigiladas cuando las de los atributos no lo están.

Es también categoría 9: al escribir un vigilante lo bastante general para no ser una lista de
rutas, se eligió una generalidad por atributo (`href|src`) en vez de por forma de la ruta
(`"/…"` en cualquier parte del documento), y el hueco es la cara opuesta de esa elección.

---

### MENOR 5 — `interpretar` acepta como «prefijo» cosas que no son un prefijo de ruta, incluida una que manda las peticiones a otro host

**Fichero:** `sitio/rutas.py:49-84` (`interpretar`).
**Categorías:** 3, 9.

La única validación del prefijo es que empiece por `/`, con un razonamiento correcto y escrito
sobre por qué una ruta relativa no sirve. Lo que ese razonamiento no cubre es que empezar por
`/` no basta para ser una ruta. Verificado ejecutando `interpretar` sobre 22 entradas:

| `--base` | `Base` resultante | `ruta("/estatico/estilo.css")` |
|---|---|---|
| `//h/p` | prefijo `//h/p` | `//h/p/estatico/estilo.css` |
| `https://h/p?x=1` | prefijo `/p?x=1` | `/p?x=1/estatico/estilo.css` |
| `https://h/p#frag` | prefijo `/p#frag` | `/p#frag/estatico/estilo.css` |
| `/porta folio` | prefijo `/porta folio` | `/porta folio/estatico/estilo.css` |
| `https://h/p/../q` | prefijo `/p/../q` | `/p/../q/estatico/estilo.css` |
| `https://user:pw@h/p` | origen `https://user:pw@h` | — |

El primero es el que importa: `//h/p` es una **referencia de red**, no una ruta, y el navegador
la resuelve contra el host `h`. Un `--base //cdn.ejemplo/x` produciría un sitio que pide su hoja
de estilo a un tercero, en silencio y en verde — que es el modo de fallo que este módulo existe
para impedir, y también el que la batería del proyecto persigue desde el principio
(`test_ningun_recurso_de_terceros`, que no se ejecuta sobre la construcción prefijada; ver
hallazgo 7). Los demás casos son corrupción silenciosa de menor alcance: la query y el
fragmento se concatenan como si fueran segmentos de ruta.

Todos exigen una errata del operador en una línea del workflow, y por eso es menor y no
relevante. Pero el módulo ya decidió validar el prefijo, y la validación que hay se detiene un
carácter antes de donde hace falta: bastaría rechazar también lo que empieza por `//` y lo que
contiene `?`, `#` o espacios.

---

### MENOR 6 — Bajo un prefijo, el `robots.txt` es letra muerta, incluida la línea de `Sitemap` que el cambio se molesta en prefijar

**Fichero:** `construir.py:84-88`.
**Categorías:** 2, 5.

Los rastreadores leen el `robots.txt` **en la raíz del host** y en ningún otro sitio. Servido el
sitio en `shatior.github.io/portafolio/`, el fichero que el cambio genera vive en
`/portafolio/robots.txt` y nadie lo consulta: la raíz de ese host la sirve el sitio de usuario
de la cuenta, no este repositorio.

Consecuencias, ninguna grave: la declaración `Sitemap:` que el diff actualiza con cuidado a
`{donde.url('/sitemap.xml')}` no la consume nadie mientras dure el prefijo, y el motivo por el
que el fichero existe según su propio comentario —«para no dejar el 404 que algunos rastreadores
registran como error del dominio»— desaparece, porque el 404 que quedaría es el de otro host.
Se anota además que `Allow: /` se mantiene literal: si por cualquier vía llegara a leerse como
`robots.txt` de host, autorizaría el host entero y no solo esta copia.

No pide corrección necesariamente —el destino final sí es la raíz de un dominio, y ahí el
fichero es correcto—; pide que no se dé por hecho que este fichero hace algo durante el
provisional.

---

### MENOR 7 — La batería sustantiva del proyecto solo mira la construcción en raíz; el artefacto que se despliega es el otro

**Fichero:** `tests/test_sitio.py:28-46` (fixtures `sitio` y `sitio_con_prefijo`),
`tests/test_sitio.py:25` (`DESTINOS_ADMITIDOS`).
**Categorías:** 4, 9.

Las promesas que el sitio hace en su pie y que la batería existe para ejecutar —sin recursos de
terceros, sin JavaScript, enlaces externos solo a destinos conocidos, la tipografía servida
desde el propio dominio, el comportamiento en móvil— se comprueban sobre el fixture `sitio`, que
construye **sin prefijo**. Los cinco tests nuevos que sí miran `sitio_con_prefijo` comprueban
rutas, canónicas, CSS y `CNAME`, y ninguno vuelve a pasar los guardias anteriores.

Mientras dure el provisional, la construcción sin prefijo es la única que nadie publica. El
riesgo real es hoy bajo, porque el mismo código genera las dos y no hay ninguna rama que dependa
de `base` para decidir qué recursos carga; por eso es menor. Se anota igualmente porque la
constante `DESTINOS_ADMITIDOS = ("https://github.com/Shatior/", "https://vigiabref.com")` ya no
describe el artefacto que se sirve —el prefijado lleva `href` a `https://shatior.github.io/…` en
cada canónica— y nadie lo nota, porque el test que la usa nunca ve ese árbol.

---

### MENOR 8 — El aviso «servido bajo …» es la única señal que recibe el operador, y no lo comprueba nada; el prefijo real vive en un fichero que ninguna prueba lee

**Ficheros:** `construir.py:92-95`, `.github/workflows/desplegar.yml:67-71`.
**Categorías:** 4, 9. (La cara de la categoría 11 que aparece aquí se resolvió a favor del cambio; se explica abajo.)

El comentario que acompaña al aviso explica bien por qué existe: «un sitio con prefijo **no** es
servible desde la raíz: publicar por error en `/` este directorio daría 404 en todas las hojas
de estilo». Es la única advertencia que separa esa equivocación de ocurrir. La mutación M13 la
suprime por completo y **los 43 tests siguen en verde**.

En el mismo sentido, y en la dirección contraria: el prefijo que de verdad se usa vive en una
línea de `.github/workflows/desplegar.yml`, y ninguna prueba lee ese fichero. La mutación M14 lo
retira y la batería sigue verde — lo cual es la respuesta **correcta** para la categoría 11
(retirar el mecanismo el día que el dominio resuelva no rompe nada, tal como el README promete,
y eso queda verificado). Su cara opuesta es la zona ciega: si `--base` desapareciera del
workflow por accidente o por un rebase, el despliegue publicaría en `/portafolio/` un árbol
construido para la raíz —el fallo exacto que este cambio corrige— y nada en el repositorio se
enteraría. El mecanismo se retira sin coste y también se pierde sin coste.

---

### MENOR 9 — El sitio provisional se firma con un dominio que no lo sirve

**Fichero:** `sitio/render.py:64`.
**Categorías:** 3.

La marca del encabezado sigue siendo el literal `<a class="marca" href="…">vigiabref.com</a>`.
Bajo el prefijo, el enlace apunta bien —`/portafolio/`— pero el texto visible del sitio publicado
en `shatior.github.io` sigue anunciándose como `vigiabref.com`, un dominio que en este momento
no resuelve; y el pie con `mailto:contacto@vigiabref.com` está en la misma situación. Puede ser
deliberado —es el dominio que el sitio reclama, la misma lógica que se aplica al `CNAME`— pero
a diferencia del `CNAME` no está declarado en ninguna parte del diff, de modo que no consta si
se decidió o si no se miró.

---

## Lo que NO se pudo verificar

- **El comportamiento real de GitHub Pages** con el `CNAME` publicado y con el `robots.txt` bajo
  subdirectorio. Es el corazón del hallazgo 1 y del hallazgo 6, y no hay acceso desde esta sesión
  al repositorio publicado ni al panel de Pages. Las dos afirmaciones se enuncian como lo que
  son: el modo de fallo que hay que comprobar, no un hecho comprobado.
- **Si Pages está activado** y si `shatior.github.io/portafolio/` responde hoy (hallazgo 2). Solo
  se pudo constatar que el repositorio no contiene evidencia de ninguna de las dos cosas.
- **El sitio construido contra los informes reales del pipeline.** Se construyó solo contra
  `tests/fixtures`; la pasada 1 encontró su bloqueante principal precisamente al construir contra
  los informes reales, y esta pasada no repitió esa comprobación por presupuesto.
- **El renderizado en un navegador**, con y sin prefijo. Se inspeccionó el HTML y el CSS
  generados, no su resolución efectiva.
- **`docs/decisiones.md` y `docs/proceso-pendiente.md`**, que no se leyeron: si alguna de estas
  cuestiones está ya decidida y razonada ahí, esta acta no lo recoge.
- **Las 16 mutaciones no ejecutadas** del presupuesto de 30, que se agotó por tiempo. Quedaron
  sin ejercitar, entre otras: el manejo de `dominio.txt` ausente o vacío, el orden relativo de
  `copytree` y la escritura de `CNAME`, y la interacción de `--salida` con rutas existentes.

---

## Recuento

| Severidad | Nº |
|---|---|
| BLOQUEANTE | 1 |
| RELEVANTE | 3 |
| MENOR | 5 |

**Categorías con hallazgo:** 1, 2, 3, 4, 5, 7, 9, 10.

**Lectura de conjunto, para que el recuento no engañe.** El cambio está bien construido en lo
que se puede ver desde el repositorio: el árbol prefijado no deja escapar ni una ruta, la
separación entre origen y prefijo está bien argumentada y es la correcta, validar `--base` antes
de borrar el destino es un acierto que además está probado, y el CSS relativo resuelve el único
caso que ningún prefijo puede reescribir. Once de catorce mutaciones mueren. El bloqueante no
está en el código: está en que la pieza que decide si todo esto llega a servir de algo —el
`CNAME` publicado— se dejó fuera del cambio por un razonamiento plausible que nadie contrastó
con el sistema que lo ejecuta, y se blindó con un test que impide la corrección obvia.

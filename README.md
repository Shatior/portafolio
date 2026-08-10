# portafolio

Generador del sitio de [vigiabref.com](https://vigiabref.com). Estático, sin marco, sin
dependencias en tiempo de ejecución.

## Qué hace

Tres vistas —portada, proyecto e informes— y **una página por informe publicado**. La parte que
importa: la sección de informes y las cifras que la acompañan **se leen del repositorio
[`threat-intel-pipeline`](https://github.com/Shatior/threat-intel-pipeline)**, no se escriben
aquí.

De cada informe se derivan los indicadores normalizados, las familias observadas, las que tienen
entrada en ATT&CK y el porcentaje del panorama que el catálogo no describe. La maqueta original
traía esas cifras a mano —«76%», «7.464»— y para cuando se implementó el sitio ya eran otras.
**Una cifra fijada en el código envejece en silencio, que es la peor forma de envejecer: sigue
pareciendo una medición.**

**Y lo que el informe no publica, el sitio tampoco.** Si una fuente no alcanzó estado correcta y
el informe suprime el panorama de familias, la portada muestra un guion con su motivo, no un
cero. Arrastrar la cifra del día anterior convertiría una ausencia de observación en una
observación de ausencia, que es justamente lo que el informe que se está leyendo se niega a
hacer.

## Construir

```bash
python construir.py --informes ../threat-intel-pipeline/reports --salida publico
python -m http.server -d publico 8000
pytest
```

**`--base`, para cuando el sitio no se sirve en la raíz de su dominio.** Vacío por defecto, que
es lo de siempre. Admite una URL completa —`https://shatior.github.io/portafolio`— o solo el
prefijo —`/portafolio`—, y afecta a todas las rutas internas: navegación, hoja de estilo,
tipografía, canónicas, `og:url`, sitemap y `robots.txt`. **El `CNAME` no**: no es una ruta del
sitio, es el dominio que el sitio reclama como suyo, y no cambia porque una copia provisional se
sirva en otro sitio.

**Sin informes no hay sitio:** si el directorio no existe o no trae ningún fichero fechado, la
construcción falla con código distinto de cero y no se despliega nada. Un sitio en verde con las
cifras vacías es indistinguible de uno al día.

## Estructura

| | |
|---|---|
| `construir.py` | orquesta: lee, renderiza y escribe |
| `sitio/lector.py` | interpreta un informe; **lo que no encuentra, lo declara ausente** |
| `sitio/render.py` | el HTML, en funciones |
| `sitio/contenido.py` | la prosa — y ninguna cifra que produzca el informe diario |
| `sitio/rutas.py` | dónde se sirve el sitio; **el único módulo que lo sabe** |
| `estatico/` | la hoja de estilo y la tipografía |

## Sin recursos de terceros

El pie del sitio dice que no hay analítica, formularios ni recursos de terceros, y que las
tipografías se sirven desde el propio dominio. Es la única afirmación comprobable del sitio, y
**`tests/test_sitio.py` la comprueba**: ninguna página carga nada externo, ninguna lleva
JavaScript, y la Inter viaja en `estatico/fuentes/` con su licencia SIL OFL.

La maqueta la incumplía —cargaba Inter desde `fonts.googleapis.com` mientras el pie decía lo
contrario—. Una promesa que solo puede cumplirse por atención se rompe el día que alguien añade
un icono desde una CDN «solo para probar».

## Revisión: este sitio hereda el protocolo del pipeline

El sitio **no tiene protocolo de revisión propio: hereda el del pipeline**, que vive en
[`docs/protocolo-revision.md`](https://github.com/Shatior/threat-intel-pipeline/blob/main/docs/protocolo-revision.md)
de `Shatior/threat-intel-pipeline`. Se declara aquí porque la alternativa —no decir nada— deja
un repositorio que se revisa con un protocolo que no menciona, y un acta en `docs/revisiones/`
que cita reglas («presupuesto», «categorías», «independencia del acta») cuyo texto no está en
ningún sitio al que este repositorio apunte.

Lo que **sí** es propio es el registro: [`docs/metricas-revision.md`](docs/metricas-revision.md).
La instrumentación cuenta pasadas de **este** repositorio, y mezclarlas con las del pipeline
haría ilegibles las dos series. Hereda el protocolo, no el registro.

Es la laguna que señaló la propia revisión —«si el sitio va a revisarse con este protocolo de
forma recurrente, necesita su propio registro y su propio `docs/protocolo-revision.md`, o una
declaración explícita de que hereda los del pipeline»—, cerrada por la vía de declararlo.

## Móvil

Las dos cosas que peor sobreviven en pantalla estrecha se resuelven primero:

- **El archivo de informes** deja de ser una columna fija de 216 px y pasa a una tira que se
  desplaza en horizontal, con objetivos táctiles de 44 px. Apilarlo empujaría el informe una
  pantalla entera hacia abajo.
- **Las tablas** dejan de ser tablas y pasan a fichas apiladas por debajo de 700 px. El nombre
  de cada columna viaja en `data-columna` y lo pinta el CSS, de modo que no hay dos fuentes del
  rótulo. El marcado sigue siendo una tabla: un lector de pantalla conserva la relación entre
  celda y cabecera aunque la presentación cambie.

## Despliegue

GitHub Pages sobre `vigiabref.com`, con el dominio en `dominio.txt` y el `CNAME` escrito en la
raíz del sitio por el propio generador.

`.github/workflows/desplegar.yml` se dispara por tres caminos, y el que importa es el segundo:

1. `push` a `main` — cambia el sitio.
2. **`repository_dispatch` de tipo `informe-publicado`**, que emite el workflow diario del
   pipeline cuando publica un informe nuevo. Sin él, la portada seguiría mostrando las cifras
   del día en que alguien tocó este repositorio por última vez.
3. Manual.

### Lo que hay que configurar a mano, y por qué no puede automatizarse

| Dónde | Secreto | Para qué |
|---|---|---|
| `threat-intel-pipeline` | `TOKEN_DISPARO_PORTAFOLIO` | emitir el `repository_dispatch` sobre este repositorio |

`GITHUB_TOKEN` está acotado al repositorio en que se ejecuta: no puede dispararlo. Es un
*fine-grained token* de un solo repositorio, con permiso de escritura de contenido.

**Leer el pipeline ya no necesita credencial.** `Shatior/threat-intel-pipeline` es público, de
modo que el `checkout` de sus informes va sin `token:`. Antes hacía falta un
`TOKEN_LECTURA_PIPELINE` en los secretos de este repositorio; ese secreto ya no lo usa nada y
puede borrarse. Si el pipeline volviera a hacerse privado, habría que reponerlo.

**Si falta `TOKEN_DISPARO_PORTAFOLIO`**, el workflow del pipeline avisa y sigue: el informe se
publica igual y el sitio se queda con las cifras anteriores hasta el siguiente `push`. Se
prefiere eso a enrojecer una ejecución que sí produjo su producto.

### Requisito de lanzamiento pendiente: el DNS de `vigiabref.com` no es nuestro

El dominio está **delegado a una cuenta de Vercel a la que no se tiene acceso**. Hoy
`vigiabref.com` no resuelve a GitHub Pages, y mientras siga así **el sitio no puede servirse
ahí**: el `CNAME` que escribe el generador es correcto y no sirve de nada, porque el `CNAME` del
repositorio solo dice a Pages qué dominio aceptar — quien decide adónde apunta el nombre son los
registros DNS, y esos los controla la otra cuenta.

Es la condición que queda, y no se cierra con código. Las salidas son tres, por orden de coste:

1. **Recuperar el acceso a la cuenta de Vercel** y repuntar los registros a GitHub Pages.
2. **Cambiar los servidores de nombres** en el registrador del dominio, que es quien manda sobre
   la delegación, y rehacer los registros.
3. **Desplegar en Vercel** desde esa misma cuenta, si se recupera: el sitio generado es el mismo
   directorio estático y no cambia nada del código.

Se declara aquí en vez de descubrirse el día del lanzamiento, que es lo que este proyecto exige
hacer con una laguna.

#### Mientras tanto, el sitio se sirve bajo un prefijo

Pages está activado con origen GitHub Actions —**lo reporta el propietario del repositorio el
2026-08-10; no se ha comprobado desde la sesión que escribe esto, cuyo acceso de red no alcanza
`shatior.github.io`**— de modo que el sitio se publica en
[`shatior.github.io/portafolio/`](https://shatior.github.io/portafolio/): bajo un subdirectorio,
no en la raíz de un dominio.

Eso no es un detalle de URL: el sitio se escribió con rutas internas absolutas —`/informes/`,
`/estatico/estilo.css`—, que son lo correcto en la raíz de `vigiabref.com` y **lo único
correcto**, porque hay páginas a dos niveles de profundidad y una ruta relativa cambiaría de
significado según quién la escriba. Bajo un subdirectorio esa misma corrección pide cada fichero
a la raíz de `shatior.github.io`, donde no hay nada: el sitio saldría sin hoja de estilo, sin
tipografía y con toda la navegación rota. **Y la construcción terminaría en verde**, porque el
árbol de salida es idéntico — el fallo solo existe una vez servido.

Lo resuelve `--base`, que el workflow de despliegue pasa como
`https://shatior.github.io/portafolio`. Lo vigila
`test_ninguna_ruta_interna_apunta_a_la_raiz_bajo_prefijo`, que construye con prefijo y comprueba
**todos** los `href` y `src` de todas las páginas, no una lista de los que hoy existen: el modo
de fallo es que alguien añada mañana la ruta número catorce.

**La copia provisional no lleva `CNAME`, y eso lo encontró la revisión.** Pages no lee ese
fichero como un rótulo sino como *el dominio de este repositorio*, y redirige la URL `github.io`
hacia él: publicar la copia reclamando un dominio que hoy no resuelve la dejaría inalcanzable, y
el prefijo existe justo para lo contrario. `dominio.txt` **no se toca** y la construcción sin
`--base` escribe el `CNAME` igual que siempre; lo que se omite es reclamar el dominio desde una
copia que no vive en él.

**El prefijo se retira el día que `vigiabref.com` resuelva.** Es una línea del workflow, y sin
ella el sitio vuelve a construirse desde la raíz, con su `CNAME`. Dos avisos sobre el alcance de
los tests, porque prometer de más es el defecto que este proyecto persigue:

- `test_el_base_vacio_y_el_por_defecto_producen_el_mismo_sitio` compara la rama **consigo
  misma**. Contra el sitio anterior al cambio sí hay una diferencia, y es intencionada y única:
  la tipografía pasó a citarse relativa a la hoja en `estatico/estilo.css`.
- La batería sustantiva —sin recursos de terceros, sin JavaScript, destinos externos, móvil—
  se ejercita sobre la construcción **en raíz**, que durante el provisional es precisamente la
  que nadie publica. Bajo prefijo solo se comprueban las rutas, las canónicas y el `CNAME`.

### GitHub Pages y la visibilidad del repositorio

GitHub Pages sirve sitios desde repositorios privados **solo en planes de pago**. Con cuenta
gratuita, este repositorio tiene que ser público para publicar en `vigiabref.com` — lo cual es
razonable para un portafolio, pero es una decisión, no un detalle. La alternativa es Vercel, que
despliega desde repositorios privados; el sitio generado es el mismo directorio estático y no
cambia nada del código.

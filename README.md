# portafolio

Generador del sitio del portafolio, publicado hoy en
[`shatior.github.io/portafolio`](https://shatior.github.io/portafolio/). Estático, sin marco, sin
dependencias en tiempo de ejecución.

**No hay dominio propio, y el sitio no lo lleva escrito en ninguna parte.** El anterior
—`vigiabref.com`— se descartó, y en vez de sustituirlo por otro nombre se retiró la constante: la
URL con la que el sitio se declara llega por `--base` en cada construcción. Una constante que
afirma dónde vive el sitio envejece igual que una cifra fijada a mano, y con la misma cara de
dato.

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
python construir.py --informes ../threat-intel-pipeline/reports --salida publico \
    --base http://localhost:8000
python -m http.server -d publico 8000
pytest
```

**`--base` es obligatorio y es una URL absoluta.** De ahí salen las rutas internas —navegación,
hoja de estilo, tipografía— y también lo que el sitio declara ser: canónica, `og:url`, sitemap y
`robots.txt`. Como se publica hoy: `--base https://shatior.github.io/portafolio`.

Que no tenga valor por defecto es la decisión que sustituye al antiguo `dominio.txt`. Un `--base`
opcional se olvida en la línea de órdenes y produce un sitio que **se construye en verde**
declarando canónicas hacia otro sitio; sin valor por defecto, olvidarlo no compila.

**No se escribe ningún `CNAME`.** Es lo que reclama un dominio ante GitHub Pages, y sin dominio
solo puede hacer daño: dejaría inalcanzable la única URL que hoy funciona. El procedimiento para
reponerlo está escrito en `construir.py`, junto al sitio donde iría.

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
tipografías se sirven desde el propio sitio. Es la única afirmación comprobable del sitio, y
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

GitHub Pages, sin dominio propio: el sitio se publica en
[`shatior.github.io/portafolio/`](https://shatior.github.io/portafolio/), bajo un subdirectorio.
El generador no escribe `CNAME` y no existe `dominio.txt`.

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

### Servido bajo un subdirectorio, y qué cambia el día que haya dominio

Pages está activado con origen GitHub Actions —**lo reporta el propietario del repositorio el
2026-08-10; no se ha comprobado desde la sesión que escribe esto, cuyo acceso de red no alcanza
`shatior.github.io`**—, de modo que el sitio se publica bajo un subdirectorio y no en la raíz de
un dominio.

Eso no es un detalle de URL. El sitio usa rutas internas absolutas —`/informes/`,
`/estatico/estilo.css`—, que son lo correcto en la raíz de un dominio y **lo único correcto**:
hay páginas a dos niveles de profundidad y una ruta relativa cambiaría de significado según quién
la escriba. Bajo un subdirectorio esa misma corrección pide cada fichero a la raíz de
`shatior.github.io`, donde no hay nada: el sitio saldría sin hoja de estilo, sin tipografía y con
toda la navegación rota. **Y la construcción terminaría en verde**, porque el árbol de salida es
idéntico — el fallo solo existe una vez servido.

Lo resuelve `--base`, que el despliegue pasa como `https://shatior.github.io/portafolio`. Lo
vigila `test_ninguna_ruta_interna_apunta_a_la_raiz_bajo_prefijo`, que comprueba **todas** las
rutas de todas las páginas —incluidos los `url()` en atributos `style`—, no una lista de las que
hoy existen: el modo de fallo es que alguien añada mañana la ruta número catorce.

#### El día que se compre un dominio

Tres pasos, y el orden importa:

1. Apuntar los registros DNS del dominio a GitHub Pages y declararlo en `Settings → Pages`.
2. Reponer la escritura del `CNAME` en `construir.py`, donde está el procedimiento completo
   escrito junto al sitio exacto donde va.
3. Cambiar `--base` en `.github/workflows/desplegar.yml` a `https://elnuevodominio.com`, **sin
   prefijo**: el sitio pasa a vivir en una raíz y las rutas internas se acortan solas.

`test_el_despliegue_pasa_la_url_con_la_que_se_sirve` y
`test_no_se_escribe_cname_en_ninguna_construccion` romperán al hacerlo. Es su función: obligar a
que la URL de publicación, el `CNAME` y la batería se muevan juntos, en vez de descubrir en
producción que solo se movió uno.

#### Lo que la batería no cubre

La batería sustantiva ahora sí se ejercita sobre la construcción que se publica —bajo prefijo—;
durante la etapa anterior corría sobre una construcción en raíz que nadie publicaba, y esa
asimetría fue un hallazgo de la revisión. Lo que sigue sin cubrirse es el **renderizado real en
un navegador**: la comprobación es estática sobre el HTML y el CSS generados.

### GitHub Pages y la visibilidad del repositorio

GitHub Pages sirve sitios desde repositorios privados **solo en planes de pago**. Con cuenta
gratuita, este repositorio tiene que ser público para publicar el sitio — lo cual es razonable
para un portafolio, pero es una decisión, no un detalle. La alternativa es Vercel, que
despliega desde repositorios privados; el sitio generado es el mismo directorio estático y no
cambia nada del código.

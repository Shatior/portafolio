# portafolio

Generador del sitio de [vigiabref.com](https://vigiabref.com). Estático, sin marco, sin
dependencias en tiempo de ejecución.

## Qué hace

Tres vistas —portada, proyecto e informes— y **una página por informe publicado**. La parte que
importa: la sección de informes y las cifras que la acompañan **se leen del repositorio
[`threat-intel-pipeline`](https://github.com/vigiabref/threat-intel-pipeline)**, no se escriben
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
| `estatico/` | la hoja de estilo y la tipografía |

## Sin recursos de terceros

El pie del sitio dice que no hay analítica, formularios ni recursos de terceros, y que las
tipografías se sirven desde el propio dominio. Es la única afirmación comprobable del sitio, y
**`tests/test_sitio.py` la comprueba**: ninguna página carga nada externo, ninguna lleva
JavaScript, y la Inter viaja en `estatico/fuentes/` con su licencia SIL OFL.

La maqueta la incumplía —cargaba Inter desde `fonts.googleapis.com` mientras el pie decía lo
contrario—. Una promesa que solo puede cumplirse por atención se rompe el día que alguien añade
un icono desde una CDN «solo para probar».

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
| `portafolio` | `TOKEN_LECTURA_PIPELINE` | leer `reports/` del pipeline, que es un repositorio privado |
| `threat-intel-pipeline` | `TOKEN_DISPARO_PORTAFOLIO` | emitir el `repository_dispatch` sobre este repositorio |

`GITHUB_TOKEN` está acotado al repositorio en que se ejecuta: no puede leer otro ni dispararlo.
Ambos son *fine-grained tokens* de un solo repositorio cada uno —lectura de contenido el
primero, escritura de contenido el segundo—.

**Si el pipeline se hace público**, `TOKEN_LECTURA_PIPELINE` deja de hacer falta y esa línea del
workflow se retira.

**Si falta `TOKEN_DISPARO_PORTAFOLIO`**, el workflow del pipeline avisa y sigue: el informe se
publica igual y el sitio se queda con las cifras anteriores hasta el siguiente `push`. Se
prefiere eso a enrojecer una ejecución que sí produjo su producto.

### Requisito de lanzamiento: el pipeline tiene que ser público

El botón «El back — Repositorio» y el enlace «Ver el fichero original» de cada informe apuntan a
`vigiabref/threat-intel-pipeline`. **Mientras ese repositorio sea privado, todos devuelven 404 a
cualquier visitante**, en un sitio cuyo lema es «Aquí puedes comprobarlo». No es un defecto del
código —los enlaces son correctos— sino una condición que hay que cumplir antes de publicar.

Lo detectó la revisión independiente, y se escribe aquí porque es lo que este proyecto exige
hacer con una laguna: declararla en vez de descubrirla el día del lanzamiento.

### GitHub Pages y la visibilidad del repositorio

GitHub Pages sirve sitios desde repositorios privados **solo en planes de pago**. Con cuenta
gratuita, este repositorio tiene que ser público para publicar en `vigiabref.com` — lo cual es
razonable para un portafolio, pero es una decisión, no un detalle. La alternativa es Vercel, que
despliega desde repositorios privados; el sitio generado es el mismo directorio estático y no
cambia nada del código.

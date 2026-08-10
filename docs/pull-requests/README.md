# Transcripciones de los hilos de pull request

**Qué son estos ficheros, y qué no son.**

Son **transcripciones**, hechas por la sesión implementadora el 2026-08-09 como copia
de seguridad previa a una posible migración de este repositorio a otra cuenta de GitHub. La
migración se haría con `git push --mirror`, que conserva commits, ramas, etiquetas y autoría
pero **no los hilos de los pull requests**: descripciones, informes de revisión publicados como
comentarios y respuestas de la sesión implementadora.

**No son los originales.** Los originales están alojados en GitHub, donde la autoría y la fecha
de cada comentario las garantiza la plataforma: quién escribió cada línea y cuándo no depende de
la buena fe de nadie. **Aquí esa garantía no existe.** Los bytes de estos ficheros los ha
escrito y commiteado la parte interesada —la misma sesión que implementó los cambios que esos
hilos revisaban—, de modo que su valor probatorio es el de una declaración, no el de un
registro.

Se extrajeron llamando a la API de GitHub y copiando los cuerpos tal cual, sin editar, resumir
ni corregir. Eso reduce el riesgo de deriva al transcribir; **no** convierte la transcripción en
original, porque el propio proceso de extracción lo controló la parte interesada. El script está
en [`scripts/archivar_pull_requests.py`](../../scripts/archivar_pull_requests.py) precisamente
para que un tercero pueda reejecutarlo mientras los originales existan y comparar: que la copia
sea **reproducible** es lo único que la acerca a un original.

## Contenido

- **1 fichero**, uno por pull request, nombrado con su número.
- Con título, estado, autor, fechas, **commit de fusión**, rama de origen y destino, URL
  original, descripción íntegra y el hilo completo en orden cronológico, reuniendo los tres
  orígenes que GitHub presenta juntos: comentarios generales, cuerpos de revisión y comentarios
  en línea sobre el diff.
- **0 entradas de hilo.** El único pull request de este repositorio se fusionó **sin
  comentarios**: su informe de revisión independiente no se publicó en el hilo sino que se
  commiteó como fichero en [`docs/revisiones/`](../revisiones/), que **sí** viaja con
  `git push --mirror`.

De modo que, en este repositorio, la migración **no perdería casi nada**. Esta copia se hace
igualmente por dos motivos: la descripción del pull request sí se perdería —y contiene el
resumen de los hallazgos de la revisión y las dos condiciones de lanzamiento—, y el archivo
tiene que existir antes de la migración, no después.

## Qué conserva custodia, y hasta dónde — medido, no supuesto

El acta de revisión de [`docs/revisiones/`](../revisiones/) es un fichero del repositorio, de
modo que viaja con el historial. Lo que se puede afirmar de ella:

- `sitio--pasada-1.md` — un solo commit (`80cfe7f`), escrito por **Claude**, junto a otros 23 ficheros.

- Su **sha256** se publica abajo, de modo que cualquier alteración futura es detectable contra
  esta lista — con la salvedad de que esta lista la escribe también la parte interesada.

**Y lo que no se puede afirmar.** El protocolo de revisión pide que cada acta se commitee **en
un commit aislado por su propio revisor**. En este repositorio **no ocurrió**: el acta entró en
el commit de importación inicial del sitio, junto a los otros veintitrés ficheros, y firmada por
la sesión implementadora — no por la revisora que la escribió. Es una desviación del protocolo
propia de una importación inicial, y se declara aquí en lugar de dejar que la tabla de digests
sugiera una custodia que no hubo.

Lo verificable de verdad, sin confiar en nadie, es la **cadena de hashes de git**: cualquier
reescritura del historial cambia los identificadores, y eso sí lo comprueba un tercero.

## Digests de las actas

| Acta | sha256 |
|---|---|
| `sitio--pasada-1.md` | `2b2e7cacfd4a869fb19aeeedd5a61125a2004f36cbaa81f0a632591bc2eaf4e7` |

Se recalculan con:

```bash
sha256sum docs/revisiones/*.md | grep -v README
```

## Lo que este archivo no puede contener

El pull request que **introduce** este archivo no puede estar en él: se archiva antes de
existir. Lo mismo valdrá para cualquier pull request posterior. Reejecutar el script los
incorpora mientras los originales sigan accesibles; después de la migración, ya no.

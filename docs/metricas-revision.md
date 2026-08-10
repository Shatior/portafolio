# Registro de pasadas de revisión — sitio

Instrumentación del protocolo de
[`docs/protocolo-revision.md`](https://github.com/Shatior/threat-intel-pipeline/blob/main/docs/protocolo-revision.md),
que **este repositorio hereda del pipeline** y no reescribe. Su propósito, las cuatro preguntas
que debe responder y la regla de retirada están en ese documento, sección «Instrumentación del
protocolo»; aquí solo vive el registro.

**Por qué el registro sí es propio y el protocolo no.** El protocolo es una forma de trabajar y
se comparte sin coste. El registro es una serie temporal sobre un corpus concreto: mezclar las
pasadas del sitio con las del pipeline produciría una tabla en la que ninguna de las dos
tendencias es legible, y la regla de retirada se evalúa sobre una serie, no sobre una suma de
series ajenas.

**Es deliberadamente pobre**, igual que el del pipeline. Una tabla, sin totales, sin medias, sin
porcentajes y sin gráficos. Un agregado calculado invita a leerse como una conclusión antes de
que haya datos para sostener ninguna, y este registro nace con **una fila**.

**Quién anota.** El revisor añade su propia fila al publicar el informe, en el mismo commit, y la
escribe él mismo. Una fila anotada después, por quien recibió los hallazgos, es una fila
reconstruida: se marca con `†`. La ausencia de fila **no** es una opción, porque un hueco mudo es
indistinguible de «no hubo pasada».

## Registro

**Filas: 2** (1 con `†`).

| Fecha | PR | Fase | Pasada | Tipo de diff | Duración | Bloq. | Relev. | Menores | Categorías con hallazgo |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-03 | vigiabref#1 | n/a | 1 | comportamiento + documentación | ~10 min (presupuesto acotado: 10 min / 30 mutaciones; 4 mutaciones ejecutadas) | 2 | 4 | 4 | 1, 2, 3, 4, 5, 9 † |
| 2026-08-10 | Shatior#1 | n/a | 2 | comportamiento + configuración + documentación | ~11 min (presupuesto acotado: 10 min / 30 mutaciones; 14 mutaciones ejecutadas, 11 muertas) | 1 | 3 | 5 | 1, 2, 3, 4, 5, 7, 9, 10 |

Actas: [`docs/revisiones/sitio--pasada-1.md`](revisiones/sitio--pasada-1.md),
[`docs/revisiones/sitio--pasada-2.md`](revisiones/sitio--pasada-2.md).

## Cómo se lee este registro

- **`n/d`** significa que el dato no consta en ningún artefacto publicado. No se estima.
- **La columna PR lleva la cuenta por delante, y hace falta.** El repositorio migró de
  `vigiabref/portafolio` a `Shatior/portafolio`, y la numeración de pull requests **se reinició**:
  hay dos PR distintos que se llaman `#1`. Sin el prefijo, las dos filas de esta tabla parecerían
  la misma revisión contada dos veces. La fila de la pasada 2 la anotó su revisora con `#2`, que
  era el número previsto antes de abrir el PR; se corrigió al abrirlo y resultar ser el `#1` de la
  cuenta nueva.
- **`†`** marca una fila reconstruida: la anotó alguien distinto del revisor, o después de su
  informe. Su fecha y sus recuentos sobreviven a la reconstrucción; la duración y el criterio con
  que se asignó cada severidad, no.
- **Fase: `n/a`, y no es lo mismo que `n/d`.** El registro del pipeline usa esa columna porque
  sus reglas de uso se enuncian en fases del producto. **Este repositorio no tiene fases**: es un
  generador de sitio, no un producto por etapas. La columna se conserva para que las dos tablas
  se lean con el mismo esquema, y `n/a` dice que la pregunta no aplica aquí — a diferencia de
  `n/d`, que diría que aplica y no consta.
- **Regla de recuento de severidades.** Se toma **el resumen que declara el propio informe**;
  solo cuando no lo hay se cuentan sus hallazgos a mano. Aquí el acta declara su propio recuento
  por severidad, y es el que se registra.
- **«Categorías con hallazgo»** es el conjunto de categorías en las que el informe declaró al
  menos un hallazgo, de cualquier severidad. **La categoría 8 (OPSEC) no está en la fila y sí se
  recorrió**: el acta la marca «recorrida, sin hallazgo», que es un resultado y no un hueco. Una
  categoría recorrida sin hallazgos y una no recorrida se distinguen en el acta, no en esta
  columna; quien necesite esa distinción tiene que abrirla.

## Por qué la única fila lleva `†`

La escribió la sesión implementadora el 2026-08-10, siete días después de la revisión, al crear
este registro — no la sesión revisora, que cuando publicó su acta no tenía dónde anotarla porque
el fichero no existía.

Lo que consta en el acta y sobrevive a la reconstrucción: la fecha, el presupuesto, las cuatro
mutaciones ejecutadas, los recuentos por severidad y la tabla de cobertura de la que sale la
última columna. Lo que **no** consta y por tanto no se registra: cómo se decidió la frontera
entre «relevante» y «menor» en cada hallazgo concreto.

El acta añade además una segunda observación de proceso que esta fila no puede reflejar: el
protocolo pide que cada acta se commitee **en un commit aislado por su propio revisor**, y en
este repositorio no ocurrió — entró en el commit de importación inicial junto a otros veintitrés
ficheros, firmada por la sesión implementadora. Está declarado en
[`docs/pull-requests/README.md`](pull-requests/README.md) y se repite aquí porque una fila de
registro que no lo dijera sugeriría una custodia que no hubo.

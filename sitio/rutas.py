"""Dónde se sirve el sitio: origen y prefijo de ruta.

**El sitio no tiene dominio propio, y por eso no lo lleva escrito en ninguna parte.** El origen
—esquema y host— llega por `--base` en cada construcción, y de ahí salen la canónica, el
`og:url` y el sitemap. La versión anterior lo leía de un `dominio.txt` con `vigiabref.com`
dentro; ese dominio se descartó, y sustituirlo por otro habría repetido el mismo defecto un
nombre más tarde: **una constante que afirma dónde vive el sitio envejece igual que una cifra
fijada a mano, y con la misma cara de dato.**

**Las rutas internas empiezan por `/`**, que es lo correcto y lo único correcto: hay páginas a
dos niveles (`/informes/2026-08-03/`), y una ruta relativa cambiaría de significado según la
profundidad de la página que la escribe. Servido bajo un subdirectorio
—`shatior.github.io/portafolio/`— esa misma corrección pide cada fichero a la raíz del host,
donde no hay nada: el sitio sale sin hoja de estilo, sin tipografía y con la navegación rota.
**No falla al construir ni al probar: falla al desplegar**, que es el único sitio donde nadie lo
estaba mirando. De eso se ocupa el prefijo.

Este módulo es el único que sabe dónde se sirve el sitio. Todo lo demás pregunta.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Base:
    """El origen y el prefijo bajo los que se publica el sitio.

    Se separan porque son dos preguntas distintas: el **prefijo** afecta a lo que el navegador
    pide (`href`, `src`), y el **origen** a lo que el sitio declara ser (canónicas, `og:url`,
    sitemap).
    """

    #: Esquema y host, **sin** barra final: `https://shatior.github.io`.
    origen: str
    #: Prefijo de ruta, vacío o empezando por `/` y **sin** barra final: `/portafolio`.
    prefijo: str

    def ruta(self, camino: str) -> str:
        """Una ruta interna para un `href` o un `src`. `camino` siempre empieza por `/`."""

        return f"{self.prefijo}{camino}"

    def url(self, camino: str) -> str:
        """La URL absoluta de una página: lo que va en la canónica y en el sitemap."""

        return f"{self.origen}{self.prefijo}{camino}"


def interpretar(base: str) -> Base:
    """Convierte el `--base` de la línea de órdenes en un `Base`.

    **Es obligatorio y tiene que ser una URL absoluta.** No hay valor por defecto y no lo habrá
    mientras no haya dominio propio: el sitio no puede adivinar dónde lo van a servir, y la
    alternativa —suponer un origen— es exactamente lo que se acaba de retirar.

    Que no sea opcional es deliberado. Un `--base` con valor por defecto se olvida en la línea de
    órdenes y produce un sitio que se construye en verde y declara canónicas hacia un sitio que
    no es este. Sin valor por defecto, olvidarlo **no compila**.

        --base https://shatior.github.io/portafolio   # como se publica hoy
        --base http://localhost:8000                  # para mirarlo en local
    """

    original = base
    base = base.strip().rstrip("/")
    if not base:
        raise ValueError(
            "`--base` es obligatorio: sin él el sitio no sabe con qué URL declararse, y ya no "
            "hay dominio propio del que deducirlo. Para mirarlo en local: "
            "`--base http://localhost:8000`."
        )

    # Nada de esto tiene sentido en un origen ni en un prefijo de ruta, y todo ello colaba por
    # una comprobación que solo miraba el esquema. Se rechaza antes de repartir.
    for prohibido, porque in (
        (" ", "un espacio no sobrevive a un atributo HTML sin escaparse"),
        ("\t", "un tabulador no sobrevive a un atributo HTML sin escaparse"),
        ("?", "una cadena de consulta convertiría cada ruta interna en una petición distinta"),
        ("#", "un fragmento haría que toda ruta interna apuntase a la misma página"),
        ("..", "un salto hacia arriba deja de ser un prefijo"),
    ):
        if prohibido in base:
            raise ValueError(f"`--base` no admite {prohibido!r}: {original!r} — {porque}")

    # El esquema es insensible a mayúsculas, y rechazar `HTTPS://…` con un mensaje que pide una
    # URL absoluta es decirle a quien la escribió que escriba lo que ya escribió.
    if not base.lower().startswith(("http://", "https://")):
        # `//host/camino` empieza por barra y **no es una ruta**: es una referencia de red, que
        # el navegador resolvería contra otro host conservando el esquema.
        pista = (
            " Empieza por `//`, que es un host y no una ruta."
            if base.startswith("//")
            else " Un prefijo suelto ya no basta: sin dominio propio, el origen no se deduce de nada."
        )
        raise ValueError(f"`--base` tiene que ser una URL absoluta: {original!r}.{pista}")

    esquema, _, resto = base.partition("://")
    host, barra, camino = resto.partition("/")
    if not host:
        raise ValueError(f"`--base` no declara host: {original!r}")
    return Base(origen=f"{esquema.lower()}://{host}", prefijo=f"{barra}{camino}".rstrip("/"))

"""Dónde se sirve el sitio: origen y prefijo de ruta.

**El sitio se escribió dando por hecho que vive en la raíz de un dominio.** Todas sus rutas
internas empiezan por `/`, que es lo correcto cuando `vigiabref.com/` es el sitio y lo único
correcto: una ruta relativa cambiaría de significado según la profundidad de la página que la
escribe, y aquí hay páginas a dos niveles (`/informes/2026-08-03/`).

Servido bajo un subdirectorio —`shatior.github.io/portafolio/`— esa misma corrección se vuelve
el defecto: `/estatico/estilo.css` pide el fichero a `shatior.github.io/estatico/estilo.css`,
que no existe, y el sitio sale sin hoja de estilo, sin tipografía y con toda la navegación
apuntando a la raíz de un dominio ajeno. **No falla al construir ni al probar: falla al
desplegar**, que es el único sitio donde nadie lo estaba mirando.

Este módulo es el único que sabe dónde se sirve el sitio. Todo lo demás pregunta.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Base:
    """El origen y el prefijo bajo los que se publica el sitio.

    Se separan porque son dos preguntas distintas y el despliegue provisional las responde de
    forma distinta: el **prefijo** afecta a lo que el navegador pide (`href`, `src`), y el
    **origen** a lo que el sitio declara ser (canónicas, `og:url`, sitemap). Un sitio servido en
    `shatior.github.io/portafolio/` que declarase canónicas en `vigiabref.com` estaría
    señalando como versión buena una URL que hoy no resuelve.
    """

    #: Esquema y host, **sin** barra final: `https://vigiabref.com`.
    origen: str
    #: Prefijo de ruta, vacío o empezando por `/` y **sin** barra final: `/portafolio`.
    prefijo: str

    def ruta(self, camino: str) -> str:
        """Una ruta interna para un `href` o un `src`. `camino` siempre empieza por `/`."""

        return f"{self.prefijo}{camino}"

    def url(self, camino: str) -> str:
        """La URL absoluta de una página: lo que va en la canónica y en el sitemap."""

        return f"{self.origen}{self.prefijo}{camino}"


def interpretar(base: str, dominio: str) -> Base:
    """Convierte el `--base` de la línea de órdenes en un `Base`.

    Se admiten tres formas, y la de en medio es la que usa el despliegue provisional:

    - `""` — el sitio vive en la raíz de su propio dominio. **Es el valor por defecto y produce
      exactamente lo de siempre**: rutas que empiezan por `/` y canónicas en `dominio.txt`.
    - `https://shatior.github.io/portafolio` — origen y prefijo, ambos declarados.
    - `/portafolio` — solo el prefijo, con el origen de `dominio.txt`. Es legítimo cuando se
      sirve el dominio propio desde un subdirectorio, y **no** es lo que hace falta para
      publicar en otro host: ahí el origen también cambia y omitirlo deja las canónicas
      apuntando a un dominio que no sirve esa copia.

    Lo que no se admite es un prefijo que no empiece por `/`: sería una ruta relativa, y una
    ruta relativa significa cosas distintas en `/` y en `/informes/2026-08-03/`.
    """

    original = base
    base = base.strip().rstrip("/")
    if not base:
        return Base(origen=f"https://{dominio}", prefijo="")

    # Nada de esto tiene sentido en un prefijo de ruta ni en un origen, y todo ello colaba por
    # una comprobación que solo miraba la barra inicial. Se rechaza antes de repartir.
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
    if base.lower().startswith(("http://", "https://")):
        esquema, _, resto = base.partition("://")
        host, barra, camino = resto.partition("/")
        if not host:
            raise ValueError(f"`--base` no declara host: {original!r}")
        prefijo = f"{barra}{camino}".rstrip("/")
        return Base(origen=f"{esquema.lower()}://{host}", prefijo=prefijo)

    # `//host/camino` **empieza por barra y no es una ruta**: es una referencia de red, y el
    # navegador la resolvería contra otro host conservando el esquema. Un sitio que promete no
    # cargar recursos de terceros los cargaría todos, y «empieza por `/`» lo daba por bueno.
    if base.startswith("//"):
        raise ValueError(
            f"`--base` empieza por `//`, que es un host y no una ruta: {original!r}. "
            "Para publicar en otro host, decláralo entero: `https://host/prefijo`."
        )

    if not base.startswith("/"):
        raise ValueError(
            f"`--base` tiene que ser una URL absoluta o un prefijo que empiece por `/`: {original!r}. "
            "Un prefijo relativo se resolvería contra la página que lo escribe, y las hay a dos "
            "niveles de profundidad."
        )
    return Base(origen=f"https://{dominio}", prefijo=base)

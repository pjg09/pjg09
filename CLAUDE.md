# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es este repositorio

Repositorio de perfil de GitHub (`pjg09/pjg09`): el `README.md` es el que se muestra en
la página de perfil del usuario. No hay código de aplicación, ni build, ni tests, ni
gestor de paquetes.

El contenido es el `README.md`, la card de lenguajes generada en `profile/`, y el
pipeline de `scripts/` que la genera.

## Arquitectura

Un único sistema: la card de lenguajes, calculada **en local** y commiteada a mano.
No hay GitHub Actions ni ningún proceso automático; nada se actualiza solo.

Hubo un workflow (`.github/workflows/stats.yml`) que generaba `profile/top-langs.svg`
con `stats-organization/github-readme-stats-action` y lo commiteaba a diario. Se borró:
medía **bytes de lenguaje de los repos que posees**, no código que hayas escrito, y
publicaba un número distinto del de la card local sobre el mismo concepto. Si alguien
propone reintroducirlo, leer §2 de `docs/card-lenguajes-local.md` antes.

Consecuencias prácticas de que ya no haya bot:

- `profile/` sigue siendo un **directorio generado**, pero ahora lo genera
  `scripts/render.py`. No editar los SVG a mano.
- **La card tiene un ancho fijo de 520px** (`render.W`), en dos temas. Hubo una variante
  ancha de 840px para escritorio, elegida por `min-width` desde el `<picture>`; se quitó
  por preferencia de diseño (commit "volver a un único tamaño de card"). Si se
  reintroduce: un SVG dentro de un `<img>` no hace reflow, solo escala, así que hacen
  falta dos ficheros por tema y el umbral se mide sobre el **viewport**, no sobre el
  contenedor del README.
- **El texto de la card está en inglés**; el repo, los comentarios y esta documentación,
  en español. Al tocar `render.py`, las cadenas que acaban dentro del SVG van en inglés.
- Ya nada commitea solo: `origin/main` no diverge por su cuenta y el `git pull --rebase`
  defensivo antes de empujar ya no hace falta.
- Actualizar la card es manual y consciente: `build` + `render` + commit.

## Card de lenguajes local (implementada)

Pipeline propio en `scripts/`, que sustituye conceptualmente a `top-langs`. Mide
**líneas de `HEAD` que `git blame -w -M -C` atribuye a Pedro**, no bytes de repo.

```sh
python3 scripts/stats.py scan <ruta-repo>    # identidades de commit del repo
python3 scripts/stats.py add  <ruta-repo>    # analiza -> fichero de datos del repo
python3 scripts/stats.py add  <ruta> --private
python3 scripts/stats.py list                # repos ya analizados
python3 scripts/stats.py build               # agrega todo -> stats.json
python3 scripts/render.py                    # stats.json -> profile/langs-{light,dark}.svg
```

Invariantes que hay que respetar al tocar esto:

- **Los datos por repo viven fuera del repositorio**, en `~/.cache/pjg09-stats/repos/`
  (override: `PJG09_STATS_DATA`). Es deliberado: contienen rutas y nombres de repos
  privados, y este repo es público. `stats.json` sí se versiona y es anónimo: solo
  lenguajes y agregados.
- **Nada se suma incrementalmente.** `add` sobrescribe el fichero de ese repo y `build`
  recomputa la card entera. Reprocesar un repo es idempotente; añadir uno nuevo es
  `add` + `build` + `render`.
- **`scripts/authors.txt` es el punto de fallo silencioso.** Un email que falte ahí hace
  que ese código no cuente y nadie avisa. Antes de cada `add`, `scan` y comprobar.
  Son dos: `pedroj1229@gmail.com` (el habitual) y `p1000414322@gmail.com` (antiguo,
  único autor de `tic1`). El segundo no aparece en foodcash ni en pjg09: mirar pocos
  repos y concluir que un email no existe es justo el error que este fichero evita.
- **`scripts/exclude.txt` es lo que hace que el número valga algo.** Sin él entran
  `schema.d.ts` generados, skills de `.agents/`, lockfiles y bundles. Cuando un repo
  nuevo meta ruido, el arreglo va aquí, no en el script.
- El script además descarta ficheros con cabecera de autogenerado (`@generated`,
  `DO NOT EDIT`...) y minificados (longitud media de línea > 300).
- Lenguajes desconocidos: `add` imprime las extensiones que no reconoció. Añadirlas a
  `scripts/languages.py` si son código.
- **La card tiene dos secciones, cada una con su barra y sus porcentajes.** Arriba,
  código, y ahí entran CSS y HTML (se escriben a mano, línea a línea). Abajo,
  `MARKUP & DATA`: Markdown, JSON, YAML, TOML, XML, INI, notebooks... El reparto lo
  decide `languages.MARKUP_OR_DATA`. Se publica la cola entera, sin umbral ni "Other".
  Los **porcentajes de abajo son sobre el total de esa sección**, no sobre el global:
  es lo que hace que su barra sume 100, y por eso la cabecera lo dice explícitamente.
  Si eso cambia, cambiar también el texto o el número engaña.
- El **contador de commits** del subtítulo es `totals.commits`: suma de `commits_mine`,
  es decir commits **propios** (autor en `authors.txt`), **sin merges** y solo los
  alcanzables desde `HEAD` de la rama analizada. No son los commits totales del repo.
- `stats.json` guarda más de lo que la card pinta (`test_ratio`, `delete_ratio`,
  `avg_age_days`, `added`/`deleted` por lenguaje). Es deliberado: qué se publica es
  decisión del renderer, no de la recolección. Hoy no se pintan.
- `is_code` **se recalcula en `build`**, no se lee del fichero del repo. Es deliberado:
  si se leyera el guardado, mover un lenguaje entre secciones obligaría a reanalizar
  todos los repos.
- **Los colores de linguist se respetan salvo dos excepciones, ambas en `render.py`.**
  `contrast_fix` aclara en HLS los que se funden con el fondo oscuro (JSON, Markdown,
  Lua...); solo actúa en el tema oscuro, porque sobre blanco funcionan y tocarlos rompe
  los reconocibles. `distinguish` separa los que se confunden **entre sí**: Python
  (`#3572A5`) y TypeScript (`#3178c6`) son el mismo azul a ojo. Mueve solo la
  luminosidad, nunca el tono, y **solo en lenguajes con ≥3% de la barra**: por debajo
  de eso el segmento es una esquirla, el punto va etiquetado igual, y el único efecto
  sería alejar el color del oficial (HTML acababa salmón por chocar con SQL).
  La barra lleva además 2px de hueco entre segmentos, que separa cualquier par de
  colores sin falsear ninguno.

### Estado

Analizados 4 repos: `foodcash`, `pjg09`, `biblioteca-elysium` e `imaquina`. Faltan los demás; se
añaden por ruta local con `add`. `gh` sí está autenticado (`gh repo list` funciona), así
que el inventario se puede automatizar cuando interese.

Al añadir un repo, **mirar siempre las extensiones que `add` no reconoció**: ahí es donde
se pierden líneas en silencio. De `biblioteca-elysium` salieron `.puml`, `.archimate` y
`.gitignore`; de `imaquina`, `.env.example` (Dotenv), `.python-version` (Version File)
y `.mako`. Todas cuentan ya.

Quedan fuera a propósito: binarios (un `.dia` al que `git blame` atribuía 802 "líneas"
de gzip; `.png`/`.webp`), volcados de herramientas (un `err.txt` de Maven en UTF-16),
lockfiles (`uv.lock`, ahora en `exclude.txt`) y los **SVG de assets**: los 9 de
`imaquina` son exportaciones de una sola línea de hasta 633.000 caracteres, no ficheros
escritos. Aunque se añadieran al mapa, el filtro de minificado los descartaría igual.

El workflow `stats.yml` y `profile/top-langs.svg` están borrados: la card local es la
única que se publica. Con 2 repos analizados, el número aún es pobre — es lo que hay
hasta meter más repos.

`docs/card-lenguajes-local.md` guarda el diseño y las decisiones (métricas candidatas,
privacidad, riesgos). Leerlo antes de cambiar la métrica o publicar métricas nuevas.

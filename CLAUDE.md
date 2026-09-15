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

Analizados 10 repos: `foodcash`, `pjg09`, `biblioteca-elysium`, `imaquina`,
`obsia-front`, `pagina-web-5.7`, `biga-app` (el único privado hasta ahora: se añadió
con `--private`), `OilTech`, `tadb202620_examen_01` (también privado) y `ExamenDevOps`. Faltan los demás; se añaden por ruta local con `add`.

**Tres de esos clones ya no existen en disco** (`biblioteca-elysium`, `obsia-front`,
`pagina-web-5.7`). Sus datos siguen en la caché y la card los incluye, que es justo para
lo que el fichero por repo vive fuera del repositorio. Pero **no se pueden reanalizar**:
si se cambia `languages.py` o `exclude.txt`, esos tres conservan la clasificación del
día que se analizaron y el resto no. Para refrescarlos hay que volver a clonarlos. `gh` sí está autenticado (`gh repo list` funciona), así
que el inventario se puede automatizar cuando interese.

Al añadir un repo, **mirar siempre las extensiones que `add` no reconoció**: ahí es donde
se pierden líneas en silencio. De `biblioteca-elysium` salieron `.puml`, `.archimate` y
`.gitignore`; de `imaquina`, `.env.example` (Dotenv), `.python-version` (Version File)
y `.mako`; de `obsia-front`, `.properties` (Java Properties) y `.pro` (ProGuard);
de `pagina-web-5.7`, `.gs` (Apps Script, que es JavaScript) y `robots.txt`; de
`biga-app`, `requirements*.txt` (Pip Requirements). Todas cuentan ya.

De `OilTech` no salió ninguna extensión nueva, pero sí dos exclusiones: `*.pyc` y `*.db`
(tenía el `__pycache__` y un SQLite commiteados). De sus 134 ficheros solo 51 son
código: 41 PDFs y 31 imágenes.

`tadb202620_examen_01` aporta 1.340 líneas de SQL, pero deja fuera a propósito tres
extensiones que **no** se añadieron al mapa y conviene no añadir a la ligera:

- **`.conf`**: sus `postgresql.conf` (921 líneas), `pg_ident.conf` (72) y `pg_hba.conf`
  (62) son las plantillas por defecto de PostgreSQL. Son 1.055 líneas que nadie escribe,
  y `git blame` las atribuiría enteras a quien hizo el commit inicial.
- **`.csv`**: 1.480 líneas son resultados de consultas exportados y 1.001 el dataset de
  entrada del examen. Datos, no escritura.
- **`.pgerd`**: diagrama de pgAdmin, JSON de una línea generado por la GUI.

`ExamenDevOps` tiene el `build/` y el `.gradle/` commiteados: de sus 52 ficheros solo
12 son escritura. Obligó a excluir **`.gradle/*`** (la caché local de Gradle, que no es
lo mismo que el `gradle/` del wrapper) porque sus `gc.properties` y `cache.properties`
se colaban al reconocerse la extensión `.properties`. De paso entró `.vscode/*`, por el
mismo criterio que `.claude/`: lo escribe el IDE, no tú.

**`.svg` no cuenta, por decisión explícita.** Se probó a añadirlo: el filtro de
minificado descartaba solo los exportados (los 14 de foodcash e imaquina son de una
línea) y dejaba pasar los escritos a mano, como el favicon de 42 líneas de `biga-app`.
Aun así se descartó entero. No reintroducirlo.

**Las skills de `.claude/` y `.agents/` tampoco.** Es tentador contarlas porque
`git blame` las atribuye entera y limpiamente: 500 líneas de `huashu-design/SKILL.md`
salen como tuyas en dos repos distintos, y es una skill descargada con licencia de
terceros. Ese es justo el límite de la métrica — blame no distingue "instalado y
commiteado" de "escrito" — y por eso el filtro va por ruta.

Quedan fuera a propósito: binarios (un `.dia` al que `git blame` atribuía 802 "líneas"
de gzip; `.png`/`.webp`), volcados de herramientas (un `err.txt` de Maven en UTF-16),
lockfiles (`uv.lock`, ahora en `exclude.txt`) y los **SVG de assets**: los 9 de
`imaquina` son exportaciones de una sola línea de hasta 633.000 caracteres, no ficheros
escritos. Aunque se añadieran al mapa, el filtro de minificado los descartaría igual.

De `obsia-front` salen tres exclusiones que conviene entender, porque son el patrón que
se repetirá en proyectos Android y de ML:

- **El wrapper de Gradle** (`gradlew`, `gradlew.bat`, `gradle/wrapper/*`) lo distribuye
  Gradle. Son 251 líneas de shell que nadie escribe.
- **`assets/vosk-model-*/` y `jniLibs/`**: el modelo de reconocimiento de voz, con su
  propio `Copyright ... AC Technologies LLC`. 28 ficheros.
- **`assets/chunks.json`**: 14.511 líneas (2,6 MB) de texto clínico troceado por un
  script a partir de guías ajenas. Es un dataset derivado, no escritura; si entrara,
  JSON saltaría de 1.7k a 16.2k líneas y sería casi el primer lenguaje de la sección de
  marcado. Ojo con esto: un dataset formateado con indentación **no** lo pilla el filtro
  de minificado, así que hay que excluirlo a mano.

En `pagina-web-5.7` el filtro que importa es el de `.agents/`: 155 de sus 273 ficheros
son una skill de terceros (`huashu-design`, con su propia licencia), incluidos los 46
`.html` y los 43 `.mp3` del repo. Sin esa exclusión, la card diría que escribiste 46
ficheros HTML que no escribiste. Comprobar siempre que dentro de `.agents/skills/` no
haya también skills propias antes de dar la exclusión por buena.

Ese repo también deja el mejor ejemplo de por qué la métrica va por `blame` y no por
`git log`: su `CHANGELOG.md` tiene 363 líneas y **ninguna es tuya**, las escribió
`semantic-release-bot` en 65 commits. El filtro por autor lo descarta sin que haya que
excluir nada.

El workflow `stats.yml` y `profile/top-langs.svg` están borrados: la card local es la
única que se publica. Con 2 repos analizados, el número aún es pobre — es lo que hay
hasta meter más repos.

`docs/card-lenguajes-local.md` guarda el diseño y las decisiones (métricas candidatas,
privacidad, riesgos). Leerlo antes de cambiar la métrica o publicar métricas nuevas.

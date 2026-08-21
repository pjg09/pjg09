# Card de lenguajes y líneas propias (cálculo local)

Estado: **diseño, sin implementar**. Documento de trabajo para retomar la tarea más
adelante. Nada de lo que hay aquí se ha ejecutado todavía; los fragmentos de código son
bocetos, no comandos verificados. Lo que sí está verificado se marca como tal.

## 1. Objetivo

Sustituir la card `top-langs` actual por una generada en local que muestre:

- **Porcentaje por lenguaje** del código escrito por Pedro.
- **Líneas de código** escritas por Pedro (valor absoluto).

Cubriendo repositorios **públicos y privados**, sin que el código privado salga de la
máquina.

## 2. Por qué en local y no en GitHub Actions

La card actual (`.github/workflows/stats.yml`) mide **bytes de lenguaje de los repos que
posees**, no código que hayas escrito. Cuenta código de otros en repos tuyos, `vendor/`,
ficheros generados, etc. Ninguna opción de esa action lo cambia: la query GraphQL pide
`repositories { languages }` y no sabe nada de autoría.

La única alternativa automatizada con atribución real (`lowlighter/metrics` con
`plugin_languages_indepth`) se descartó por tres motivos:

1. Proyecto sin mantenimiento: último commit en `master` el **2023-12-18**, última release
   **v3.34 (2023-09-13)**. Verificado vía API.
2. Sus propios autores desaconsejan el modo indepth sobre código sensible: clona los
   repos en el runner y declinan responsabilidad por filtraciones.
3. Exigiría un PAT con scope `repo` entregado a una action Docker de terceros.

En local desaparecen los tres: los repos ya están (o se clonan) en la máquina de Pedro,
no hace falta ningún PAT con permisos de escritura, y el único artefacto que se publica
es un SVG.

**Coste asumido:** la card no se actualiza sola. Hay que ejecutar el script y commitear.

## 3. La decisión que más afecta al resultado: qué es "una línea mía"

Hay dos métricas defendibles y dan números muy distintos. Conviene elegir una
conscientemente y **escribirla en el propio README**, porque un número sin definición no
significa nada.

### Opción A — Líneas añadidas históricamente

```
git log --author=<email> --no-merges --numstat
```

Suma de `added` por fichero a lo largo de toda la historia.

- Mide *actividad*, no código existente.
- Un fichero escrito y borrado sigue contando.
- Un reformateo masivo o un cambio de licencia en 400 ficheros infla el número.
- Un `package-lock.json` commiteado son decenas de miles de líneas "tuyas".
- Barato de calcular.

### Opción B — Líneas supervivientes (`git blame`)

```
git blame --line-porcelain HEAD -- <fichero>
```

Contar las líneas de `HEAD` cuyo autor eres tú.

- Mide *código que escribiste y que sigue vivo*. Mucho más honesto.
- Inmune a ficheros borrados y a la mayor parte del ruido histórico.
- Sensible a reformateos: un `prettier` masivo te reasigna líneas ajenas.
  Mitigable con `git blame -w -C` (ignora whitespace y detecta movimientos de código) y
  con `--ignore-revs-file` para excluir commits de reformateo conocidos.
- Bastante más lento: recorre todos los ficheros de todos los repos.

**Recomendación: opción B**, con `-w -C`. Es la que responde de verdad a "código que yo
he escrito". Si resulta demasiado lenta sobre el conjunto real de repos, caer a la A y
decirlo explícitamente en la card.

Se puede calcular **ambas** y guardarlas en el JSON intermedio; decidir cuál se pinta es
un cambio en el renderer, no en la recolección.

## 4. Pipeline

Cuatro etapas desacopladas. Cada una escribe un fichero, de modo que se puede re-ejecutar
solo la última sin repetir el trabajo caro.

```
inventario  →  recolección   →  clasificación  →  render
(repos.json)   (raw.json)       (stats.json)      (SVG)
```

### 4.1 Inventario de repositorios

`gh` ya está instalado y autenticado (verificado: `gh version 2.45.0`). Los campos del
`--json` están verificados con `gh repo list --json`:

```sh
gh repo list --limit 500 --source --no-archived \
  --json nameWithOwner,isPrivate,isFork,isEmpty,defaultBranchRef,diskUsage \
  > repos.json
```

Notas:

- `--source` excluye forks; `--limit` por defecto es **30**, hay que subirlo o se
  truncará en silencio.
- `gh repo list` solo devuelve repos **propios**. Para contribuciones a repos de
  organizaciones o de terceros hay que listarlos aparte (`gh api /user/repos` con
  `affiliation=collaborator,organization_member`). Decidir si entran (ver §11).
- Filtrar `isEmpty` para no clonar repos vacíos.

### 4.2 Identidades de commit

Igual que en `metrics`, si falta un email el código no cuenta y **no avisa**. Descubrir
todas las identidades usadas realmente, en vez de asumirlas:

```sh
git log --all --format='%ae%n%an' | sort -u
```

Ejecutado sobre cada clon, produce la lista real de identidades. Revisar a mano y guardar
las propias en un `authors.txt` versionado (los emails ya son públicos en los commits, no
es un secreto nuevo).

Incluir con seguridad: `p1000414322@gmail.com`, la variante
`<id>+pjg09@users.noreply.github.com`, y cualquier email corporativo antiguo.

### 4.3 Clonado / actualización

Caché local fuera del repo, p. ej. `~/.cache/pjg09-stats/`:

```sh
git clone --filter=blob:none <url> <dest>   # o git -C <dest> fetch --all --prune
```

`--filter=blob:none` (partial clone) reduce mucho la descarga inicial, pero **`git blame`
necesita los blobs** y los irá pidiendo bajo demanda, lo que puede acabar siendo más lento
que un clon completo. Si se elige la opción B, probablemente convenga clon normal.
*Pendiente de medir.*

### 4.4 Clasificación por lenguaje

Ruby **no está instalado**, así que `github-linguist` (gema) queda descartado salvo que se
instale. Node 22 y `npx` sí están (verificado). Opciones:

1. **`linguist-js` vía `npx`** — puerto JS de linguist. Es lo que usa `metrics` por
   dentro. Detecta ficheros *vendored* y *generated*, que es justo lo que hay que
   descartar. Preferida.
2. **Mapa de extensiones propio en Python** (`python3` disponible). Trivial de escribir,
   pero hay que mantener a mano la lista de extensiones y toda la lógica de exclusión.

Recomendación: `linguist-js`, y usar su marca de vendored/generated como filtro.

### 4.5 Filtrado de ruido

Esta sección es la que decide si el número vale algo. Sin ella, el resultado es basura
con aspecto de dato.

Excluir:

- Ficheros marcados por linguist como `vendored` o `generated`.
- Lockfiles: `package-lock.json`, `yarn.lock`, `poetry.lock`, `Cargo.lock`, `go.sum`.
- Minificados y bundles: `*.min.js`, `*.min.css`, `dist/`, `build/`.
- Binarios y assets: linguist ya los clasifica como no-código.
- Commits de merge (`--no-merges`).
- Commits de importación masiva inicial (un "Initial commit" con 50k líneas de un
  proyecto que no escribiste tú). Detectables por umbral de líneas por commit; revisar a
  mano y meterlos en una lista de exclusión.
- Migraciones automáticas y ficheros de traducción, si aplica.

Mantener un `exclude.txt` versionado con globs y otro con SHAs de commits excluidos
(reformateos), reutilizable como `--ignore-revs-file` de `git blame`.

## 5. Formato intermedio

Que el render no dependa de cómo se calculó. Boceto:

```json
{
  "generated_at": "2026-08-18T00:00:00Z",
  "metric": "surviving_lines",
  "authors": ["p1000414322@gmail.com"],
  "repos_analyzed": 23,
  "repos_skipped": ["owner/repo-x"],
  "totals": { "lines": 128400, "files": 1820 },
  "languages": [
    { "name": "Python", "lines": 61200, "percent": 47.7, "color": "#3572A5" }
  ]
}
```

Versionar `stats.json` en el repo: hace auditables los cambios de la card entre commits y
permite regenerar el SVG sin recalcular.

## 6. Render de la card

SVG generado por un script propio, sin servicios externos. Puntos concretos:

- **Tema claro/oscuro.** GitHub no aplica su tema al SVG. El patrón que funciona en un
  README es servir dos ficheros:

  ```html
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./profile/langs-dark.svg">
    <img alt="Lenguajes" src="./profile/langs-light.svg">
  </picture>
  ```

  Las media queries *dentro* del SVG no son fiables al incrustarlo con `<img>`.
- **Sin `<script>` ni fuentes externas:** GitHub sanea el SVG y bloquea recursos remotos.
  Usar familias genéricas (`system-ui, sans-serif`) y todo el CSS inline.
- **Caché de camo:** GitHub proxea las imágenes del README. Tras commitear puede tardar
  en refrescarse; no es un bug del script.
- Incluir en la propia card la definición de la métrica y la fecha: *"líneas
  supervivientes en HEAD, 23 repos, 2026-08-18"*. Un porcentaje sin denominador es
  propaganda.

## 7. Privacidad: qué se publica

El SVG acaba en un repo público **y queda en el historial de git**. Decidir antes de la
primera ejecución:

- ¿Se publican líneas absolutas o solo porcentajes? El absoluto revela volumen de trabajo
  privado.
- Un lenguaje con presencia mínima puede delatar la existencia de un proyecto privado
  concreto. Agrupar la cola en "Other" con un umbral (p. ej. <2%).
- Nombres de repos privados: **nunca** deben aparecer en el SVG ni en `stats.json`
  publicado. Si `repos_skipped` lleva nombres privados, sacarlo del JSON versionado.

## 8. Estructura de ficheros propuesta

```
scripts/
  collect.py        # inventario + recolección → raw.json
  classify.py       # linguist + filtros → stats.json
  render.py         # stats.json → SVG (claro y oscuro)
  authors.txt
  exclude.txt
  ignore-revs.txt
docs/
  card-lenguajes-local.md   # este fichero
profile/
  langs-light.svg
  langs-dark.svg
stats.json
```

## 9. Interacción con el workflow actual

`.github/workflows/stats.yml` escribe en `profile/` y hace `git push` a diario como
`github-actions[bot]`. Si la card local vive en el mismo directorio:

- No hay colisión de ficheros mientras los nombres difieran
  (`top-langs.svg` vs `langs-*.svg`).
- Sí puede haber conflictos de push si se commitea en local a la vez que corre el cron.

Al implementar esto, **decidir si el workflow se elimina**. Mantener las dos cards a la
vez significa publicar dos números distintos del mismo concepto, uno de ellos engañoso.
Recomendación: borrar el workflow y el `top-langs.svg` cuando la card local funcione.

## 10. Métricas candidatas (pendientes de elegir)

Ninguna está decidida. Se documentan todas para que la elección sea explícita y no haya
que rehacer el análisis. **Todas derivan de datos que el pipeline de §4 ya recoge**
(`git blame --line-porcelain` da autor *y* fecha por línea; `git log --numstat` ya se
recorre entero), así que el coste marginal de casi todas es el render, no el cálculo.

Criterio de selección propuesto: elegir **tres como mucho**. Lenguajes y líneas ya
ocupan el espacio; cada métrica extra diluye las demás. El valor no está en parecer
profesional —nadie contrata por una card— sino en ser honesto e inusual.

### Riesgo común a todas

El cálculo incluye **repositorios privados**. Si alguno es de trabajo o de cliente,
publicar cualquiera de estas métricas publica datos derivados de código ajeno: el heatmap
revela horarios de la empresa, el ratio de tests revela su cultura de calidad, el volumen
revela el tamaño del proyecto. Revisar el contrato laboral **antes** de implementar, no
después de commitear el SVG. Esto ya aplicaba a lenguajes y líneas; con horarios el
problema es mayor.

### Candidatas con señal profesional

**A. Ratio de código de test** — porcentaje de tus líneas que viven en ficheros de test.

- Fuente: clasificación por ruta (`tests/`, `test/`, `*_test.go`, `*.spec.ts`,
  `*_spec.rb`, `conftest.py`) sobre la salida de linguist. Trivial.
- Casos límite: los repos sin tests hunden la media y no distinguen "no escribí tests" de
  "el proyecto no los tiene". Los tests generados o de snapshot inflan el número.
- Veredicto: de las poquísimas que dicen algo real sobre cómo trabajas, y no la lleva
  casi nadie. **Recomendada.**

**B. Supervivencia del código** — de las líneas escritas hace más de un año, cuántas
siguen vivas en `HEAD`. Variante: **edad media del código vivo** ("tu código tiene de
media 2,3 años").

- Fuente: `git blame --line-porcelain` ya devuelve `author-time`; comparar con la fecha
  actual. Coste casi nulo **si** se elige la métrica B de §3 (blame). Con la métrica A
  (`--numstat`) habría que ejecutar blame igualmente solo para esto.
- Casos límite: penaliza injustamente proyectos jóvenes o en desarrollo activo; un repo
  archivado hace años puntúa altísimo sin mérito. Un reformateo masivo resetea la edad de
  todo (mitigable con `--ignore-revs-file`, ver §4.5).
- Veredicto: la más interesante de la lista y la más difícil de falsear. Distingue
  construir de churnear. **Recomendada.**

**C. Tamaño mediano de commit** y % de commits por debajo de 100 líneas.

- Fuente: `git log --author --no-merges --numstat`. Trivial.
- Casos límite: usar **mediana, nunca media** — un import inicial de 40k líneas destroza
  el promedio. Los squash merges inflan artificialmente el tamaño (ver §12).
- Veredicto: señal de commits atómicos y revisables, pero fácil de gamear y un
  desconocido puede no leerla como virtud. Opcional.

**D. Ratio borrado/añadido** — "por cada 3 líneas que escribo, borro 1".

- Fuente: sumar `added`/`deleted` de `git log --numstat`. Trivial.
- Casos límite: borrar `vendor/` o un `dist/` commiteado por error dispara el ratio;
  aplican los mismos filtros de §4.5.
- Veredicto: la única de la lista donde **gamearla te hace mejor programador**, al
  contrario que las líneas totales. **Recomendada** por eso más que por su valor
  informativo.

### Candidatas friki

**E. Heatmap de hora del día / día de la semana.**

- Fuente: `git log --author --format='%ad' --date=format:'%u %H'`. Trivial.
- Casos límite: la zona horaria del commit es la del equipo donde se hizo; viajes y
  portátiles mal configurados ensucian el dato.
- Veredicto: divertida y clásica, pero **filtra tus horarios reales de trabajo** y los de
  tu empleador. Commits a las 3am no son el flex que parecen. Solo si asumes ese coste.

**F. Vocabulario de los mensajes de commit** — top 10 palabras, cuántas veces has escrito
`fix typo`, ratio español/inglés.

- Fuente: `git log --author --format='%s'` + recuento. Trivial.
- Casos límite: mensajes autogenerados (`Merge branch`, dependabot) dominan si no se
  filtran; conviene excluir merges y bots.
- Veredicto: cero valor informativo, mucha gracia, no la tiene nadie. Buena candidata si
  el objetivo declarado es friki.

**G. Récords** — el commit más grande, el día más productivo, el fichero más largo escrito.

- Fuente: misma pasada de `--numstat`. Trivial.
- Casos límite: casi siempre el récord es un fichero generado o un import masivo. Sin los
  filtros de §4.5 es directamente falso.
- Veredicto: entretenida, pero exige el filtrado bien hecho o es mentira.

### Candidata bloqueada

**H. Pull requests revisadas** — número de PRs revisadas y comentarios de revisión.

- Fuente: API de GitHub (`gh api`/`search`), **no** el pipeline local de §4. Es la única
  que requiere infraestructura nueva.
- Veredicto: sería mejor señal de colaboración que las líneas escritas. Pero con el grueso
  del trabajo en repos privados o en solitario saldrá cerca de cero, y una métrica de
  colaboración a cero es peor que no ponerla. **Descartada salvo que los números
  justifiquen lo contrario;** comprobar antes de invertir en ella.

### Descartadas explícitamente

Streaks, commits totales, "trophies", el grafo de contribuciones replicado. Son puro
volumen, están gameadas de forma generalizada y quien sabe leerlas las descuenta. Un
streak de 400 días dice que commiteaste el 25 de diciembre, no que seas bueno. Se dejan
anotadas aquí para no reabrir el debate.

### Checklist de decisión

- [ ] A. Ratio de código de test
- [ ] B. Supervivencia del código / edad media
- [ ] C. Tamaño mediano de commit
- [ ] D. Ratio borrado/añadido
- [ ] E. Heatmap horario *(implica publicar tus horarios)*
- [ ] F. Vocabulario de commits
- [ ] G. Récords
- [ ] H. PRs revisadas *(requiere API, probablemente ~0)*

Recomendación de partida: **A + B + D**. Señal profesional real, dato difícil de falsear
e incentivo sano, sin filtrar horarios.

## 11. Decisiones pendientes

1. Métrica: ¿supervivientes (`blame`) o añadidas (`log --numstat`)? → §3.
2. ¿Entran repos de organizaciones y colaboraciones, o solo los propios? → §4.1.
3. ¿Se publican líneas absolutas o solo porcentajes? → §7.
4. ¿Se borra el workflow `stats.yml`? → §9.
5. ¿Clon completo o `--filter=blob:none`? Medir sobre el conjunto real. → §4.3.
6. ¿Qué métricas extra se publican, además de lenguajes y líneas? → §10.

## 12. Riesgos conocidos

- **Squash merges**: un squash atribuye todo el cambio a quien mergeó. Si trabajas en
  repos con squash, o pierdes autoría o te apropias de la ajena, según el caso.
- **Pair programming / `Co-authored-by`**: `git log --author` no lo detecta; hay que
  parsear el *trailer* aparte si importa.
- **Historias reescritas** (`filter-branch`, `rebase` masivo) pueden haber cambiado el
  autor de commits antiguos.
- **El número siempre será una estimación.** Documentarlo en la card. Es preferible un
  número honesto y acotado que uno grande sin definición.

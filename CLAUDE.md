# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es este repositorio

Repositorio de perfil de GitHub (`pjg09/pjg09`): el `README.md` es el que se muestra en
la página de perfil del usuario. No hay código de aplicación, ni build, ni tests, ni
gestor de paquetes. Todo el repositorio son dos ficheros: `README.md` y
`.github/workflows/stats.yml`.

## Arquitectura

El único "sistema" aquí es un ciclo de generación de imágenes:

1. `.github/workflows/stats.yml` se ejecuta a diario (cron `0 3 * * *`) o a mano
   (`workflow_dispatch`).
2. Usa `stats-organization/github-readme-stats-action@v1` para generar la tarjeta
   `top-langs` en `profile/top-langs.svg`.
3. El propio workflow hace commit y push de `profile/` como `github-actions[bot]`
   (`permissions: contents: write`).
4. `README.md` referencia esa ruta: `![Top Langs](./profile/top-langs.svg)`.

Consecuencias prácticas:

- **`profile/` es un directorio generado.** No editar a mano su contenido: el siguiente
  ciclo del workflow lo sobrescribe. Ahora mismo `profile/` no existe en el repositorio;
  la imagen del README está rota hasta que el workflow corra por primera vez.
- Cambiar el aspecto de la tarjeta se hace en `options` del workflow
  (`layout=compact&theme=radical&langs_count=8`), no tocando el SVG.
- Si se cambia `path:` en el workflow, hay que actualizar también el enlace del README;
  son dos sitios acoplados por una ruta escrita a mano.
- El workflow hace `git push` directo sobre la rama por defecto: cualquier protección de
  rama que impida el push del bot romperá la ejecución.

## Comandos

Ejecutar el workflow manualmente (requiere `gh` autenticado):

```sh
gh workflow run stats.yml
gh run list --workflow=stats.yml
```

## Trabajo planificado

`docs/card-lenguajes-local.md` describe una sustitución planificada (aún **no
implementada**) de la card `top-langs` por una generada en local: porcentaje de lenguajes
y líneas de código atribuidas a Pedro, incluyendo repositorios privados, calculadas en su
máquina y publicadas solo como SVG. Contiene el razonamiento de por qué no se hace en
Actions y las decisiones aún abiertas. Leerlo antes de tocar `stats.yml` o `profile/`.

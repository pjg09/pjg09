"""Mapa extension -> lenguaje y clasificacion de rutas.

Subconjunto de linguist suficiente para una card de perfil. No pretende cubrir
los ~600 lenguajes de linguist: cubre lo que se escribe de verdad. Anadir aqui
cuando aparezca un lenguaje nuevo al procesar un repo.
"""

# Extension (en minuscula, con punto) -> (Lenguaje, color hex de linguist)
EXTENSIONS = {
    ".py": ("Python", "#3572A5"),
    ".pyi": ("Python", "#3572A5"),
    ".js": ("JavaScript", "#f1e05a"),
    ".mjs": ("JavaScript", "#f1e05a"),
    ".cjs": ("JavaScript", "#f1e05a"),
    ".jsx": ("JavaScript", "#f1e05a"),
    ".ts": ("TypeScript", "#3178c6"),
    ".mts": ("TypeScript", "#3178c6"),
    ".cts": ("TypeScript", "#3178c6"),
    ".tsx": ("TypeScript", "#3178c6"),
    ".java": ("Java", "#b07219"),
    ".kt": ("Kotlin", "#A97BFF"),
    ".kts": ("Kotlin", "#A97BFF"),
    ".c": ("C", "#555555"),
    ".h": ("C", "#555555"),
    ".cc": ("C++", "#f34b7d"),
    ".cpp": ("C++", "#f34b7d"),
    ".cxx": ("C++", "#f34b7d"),
    ".hpp": ("C++", "#f34b7d"),
    ".hh": ("C++", "#f34b7d"),
    ".cs": ("C#", "#178600"),
    ".go": ("Go", "#00ADD8"),
    ".rs": ("Rust", "#dea584"),
    ".rb": ("Ruby", "#701516"),
    ".php": ("PHP", "#4F5D95"),
    ".swift": ("Swift", "#F05138"),
    ".m": ("Objective-C", "#438eff"),
    ".mm": ("Objective-C++", "#6866fb"),
    ".dart": ("Dart", "#00B4AB"),
    ".scala": ("Scala", "#c22d40"),
    ".sc": ("Scala", "#c22d40"),
    ".clj": ("Clojure", "#db5855"),
    ".cljs": ("Clojure", "#db5855"),
    ".ex": ("Elixir", "#6e4a7e"),
    ".exs": ("Elixir", "#6e4a7e"),
    ".erl": ("Erlang", "#B83998"),
    ".hs": ("Haskell", "#5e5086"),
    ".lua": ("Lua", "#000080"),
    ".pl": ("Perl", "#0298c3"),
    ".pm": ("Perl", "#0298c3"),
    ".r": ("R", "#198CE7"),
    ".jl": ("Julia", "#a270ba"),
    ".zig": ("Zig", "#ec915c"),
    ".nim": ("Nim", "#ffc200"),
    ".v": ("V", "#4f87c4"),
    ".sh": ("Shell", "#89e051"),
    ".bash": ("Shell", "#89e051"),
    ".zsh": ("Shell", "#89e051"),
    ".fish": ("Shell", "#4aae47"),
    ".ps1": ("PowerShell", "#012456"),
    ".bat": ("Batchfile", "#C1F12E"),
    ".sql": ("SQL", "#e38c00"),
    ".html": ("HTML", "#e34c26"),
    ".htm": ("HTML", "#e34c26"),
    ".vue": ("Vue", "#41b883"),
    ".svelte": ("Svelte", "#ff3e00"),
    ".astro": ("Astro", "#ff5a03"),
    ".css": ("CSS", "#663399"),
    ".scss": ("SCSS", "#c6538c"),
    ".sass": ("Sass", "#a53b70"),
    ".less": ("Less", "#1d365d"),
    ".styl": ("Stylus", "#ff6347"),
    ".md": ("Markdown", "#083fa1"),
    ".mdx": ("MDX", "#fcb32c"),
    ".rst": ("reStructuredText", "#141414"),
    ".tex": ("TeX", "#3D6117"),
    ".yml": ("YAML", "#cb171e"),
    ".yaml": ("YAML", "#cb171e"),
    ".toml": ("TOML", "#9c4221"),
    ".json": ("JSON", "#292929"),
    ".jsonc": ("JSON", "#292929"),
    ".xml": ("XML", "#0060ac"),
    ".ini": ("INI", "#d1dbe0"),
    ".cfg": ("INI", "#d1dbe0"),
    ".gradle": ("Gradle", "#02303a"),
    ".properties": ("Java Properties", "#2A6277"),
    ".pro": ("ProGuard", "#4b8b3b"),
    ".tf": ("HCL", "#844FBA"),
    ".hcl": ("HCL", "#844FBA"),
    ".proto": ("Protocol Buffer", "#e3b72e"),
    ".graphql": ("GraphQL", "#e10098"),
    ".gql": ("GraphQL", "#e10098"),
    ".prisma": ("Prisma", "#0c344b"),
    ".sol": ("Solidity", "#AA6746"),
    ".asm": ("Assembly", "#6E4C13"),
    ".s": ("Assembly", "#6E4C13"),
    ".vim": ("Vim Script", "#199f4b"),
    ".el": ("Emacs Lisp", "#c065db"),
    ".ipynb": ("Jupyter Notebook", "#DA5B0B"),
    ".mako": ("Mako", "#7e858d"),
    ".puml": ("PlantUML", "#fbbd16"),
    ".iuml": ("PlantUML", "#fbbd16"),
    ".archimate": ("ArchiMate", "#2e75b6"),
    ".drawio": ("Diagrams.net", "#f08705"),
    ".cshtml": ("HTML+Razor", "#512be4"),
    ".razor": ("HTML+Razor", "#512be4"),
    ".ejs": ("EJS", "#a91e50"),
    ".hbs": ("Handlebars", "#f7931e"),
    ".twig": ("Twig", "#c1d026"),
    ".blade.php": ("Blade", "#f7523f"),
}

# Ficheros sin extension util, por nombre exacto (minuscula)
FILENAMES = {
    ".env": ("Dotenv", "#e5d559"),
    ".env.example": ("Dotenv", "#e5d559"),
    ".env.sample": ("Dotenv", "#e5d559"),
    ".env.template": ("Dotenv", "#e5d559"),
    ".python-version": ("Version File", "#6e7781"),
    ".node-version": ("Version File", "#6e7781"),
    ".nvmrc": ("Version File", "#6e7781"),
    ".ruby-version": ("Version File", "#6e7781"),
    ".tool-versions": ("Version File", "#6e7781"),
    ".gitignore": ("Ignore List", "#6e7781"),
    ".dockerignore": ("Ignore List", "#6e7781"),
    ".gitattributes": ("Git Attributes", "#6e7781"),
    "dockerfile": ("Dockerfile", "#384d54"),
    "containerfile": ("Dockerfile", "#384d54"),
    "makefile": ("Makefile", "#427819"),
    "gnumakefile": ("Makefile", "#427819"),
    "rakefile": ("Ruby", "#701516"),
    "gemfile": ("Ruby", "#701516"),
    "vagrantfile": ("Ruby", "#701516"),
    "justfile": ("Just", "#384d54"),
    "cmakelists.txt": ("CMake", "#DA3434"),
    "procfile": ("Procfile", "#a91e50"),
}

# Prosa, configuracion y datos. Se recogen y se publican igual, pero en una
# seccion aparte de la card: no entran en el porcentaje de codigo.
# CSS/HTML si cuentan como codigo: se escriben a mano, linea a linea.
MARKUP_OR_DATA = {
    "Markdown", "MDX", "reStructuredText", "TeX", "YAML", "TOML", "JSON",
    "XML", "INI", "Jupyter Notebook", "Procfile",
    "PlantUML", "ArchiMate", "Diagrams.net", "Ignore List", "Git Attributes",
    "Dotenv", "Version File", "Mako", "Java Properties", "ProGuard",
}


def classify(rel_path):
    """Devuelve (lenguaje, color) o (None, None) si no se reconoce."""
    name = rel_path.rsplit("/", 1)[-1].lower()
    if name in FILENAMES:
        return FILENAMES[name]
    if name.startswith("dockerfile."):
        return FILENAMES["dockerfile"]
    # extensiones compuestas primero (.blade.php)
    for ext, lang in EXTENSIONS.items():
        if ext.count(".") > 1 and name.endswith(ext):
            return lang
    idx = name.rfind(".")
    if idx <= 0:
        return (None, None)
    return EXTENSIONS.get(name[idx:], (None, None))


TEST_DIR_MARKERS = ("/test/", "/tests/", "/spec/", "/__tests__/", "/testing/")
TEST_NAME_MARKERS = ("_test.", "test_", ".test.", ".spec.", "_spec.")


def is_test(rel_path):
    p = "/" + rel_path.lower()
    if any(m in p for m in TEST_DIR_MARKERS):
        return True
    name = p.rsplit("/", 1)[-1]
    if name in ("conftest.py",):
        return True
    return any(m in name for m in TEST_NAME_MARKERS)

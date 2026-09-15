#!/usr/bin/env python3
"""stats.json -> profile/langs-light.svg y profile/langs-dark.svg

SVG autocontenido: sin <script>, sin fuentes remotas, todo el CSS inline.
GitHub sanea el SVG del README y bloquea recursos externos, y las media
queries dentro de un <img> no son fiables: por eso dos ficheros y un
<picture> en el README.
"""
import colorsys
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

THEMES = {
    "light": {
        "bg": "#ffffff", "border": "#d0d7de", "title": "#0969da",
        "text": "#1f2328", "muted": "#59636e", "track": "#eaeef2",
    },
    "dark": {
        "bg": "#0d1117", "border": "#30363d", "title": "#58a6ff",
        "text": "#c9d1d9", "muted": "#8b949e", "track": "#21262d",
    },
}

W = 520
PAD = 25
COLS = 2
ROW_H = 27           # alto de fila en las listas de lenguajes
BAR_H = 9
BAR_GAP = 26         # de la barra a la primera fila
SEC_GAP = 34         # del final de una seccion a la linea separadora
HEAD_GAP = 30        # del titulo de seccion a su barra
BOTTOM = 26
BAR_GAP_X = 2.0      # separacion entre segmentos de la barra

# Dos colores de linguist colisionan si comparten tono y luminosidad: Python
# (#3572A5) y TypeScript (#3178c6) son el mismo azul a ojo.
HUE_NEAR = 20 / 360
LUM_NEAR = 0.18
LUM_SHIFT = 0.22
# Por debajo de esto el segmento es una esquirla en la barra: da igual que su
# color choque con otro, y tocarlo solo lo aleja del color oficial.
MIN_PCT_TO_ADJUST = 3.0


def _lum(hexcol):
    """Luminancia relativa WCAG de un #rrggbb."""
    c = hexcol.lstrip("#")
    ch = [int(c[i:i+2], 16) / 255 for i in (0, 2, 4)]
    ch = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def _lighten(hexcol, min_l):
    """Sube la luminosidad conservando tono y saturacion. Mezclar con blanco
    desatura: el morado de CSS acaba rosa y el azul de Markdown, gris."""
    c = hexcol.lstrip("#")
    r, g, b = (int(c[i:i+2], 16) / 255 for i in (0, 2, 4))
    h, l, sat = colorsys.rgb_to_hls(r, g, b)
    if l >= min_l:
        return hexcol
    sat = max(sat, 0.30) if sat > 0.02 else sat   # los grises siguen grises
    r, g, b = colorsys.hls_to_rgb(h, min_l, sat)
    return "#%02x%02x%02x" % (round(r*255), round(g*255), round(b*255))


def contrast_fix(hexcol, theme_name):
    """El color oficial de un lenguaje puede fundirse con el fondo oscuro.
    Solo se corrige ahi: sobre blanco los colores de linguist funcionan, y
    tocarlos rompe los reconocibles (el amarillo de JavaScript, p.ej.)."""
    if theme_name != "dark":
        return hexcol
    try:
        if _lum(hexcol) < 0.10:
            return _lighten(hexcol, 0.55)
    except (ValueError, IndexError):
        pass
    return hexcol


def _hls(hexcol):
    c = hexcol.lstrip("#")
    r, g, b = (int(c[i:i+2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hls(r, g, b)


def _hex(h, l, sat):
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, min(1.0, l)), sat)
    return "#%02x%02x%02x" % (round(r*255), round(g*255), round(b*255))


def _hue_dist(h1, h2):
    d = abs(h1 - h2) % 1.0
    return min(d, 1.0 - d)


def distinguish(items, theme_name):
    """Devuelve {nombre: color} separando los que se confunden entre si.

    Se respeta el color de linguist siempre que se pueda: solo se mueve la
    luminosidad (nunca el tono) del lenguaje con menos lineas, que es el que
    menos se juega en ser reconocible. Los grises se dejan en paz.
    """
    out, used = {}, []
    for e in items:
        base = contrast_fix(e["color"], theme_name)
        h, l, sat = _hls(base)
        if sat > 0.15 and e["percent"] >= MIN_PCT_TO_ADJUST:
            for _ in range(3):
                clash = next((c for c in used
                              if c[2] > 0.15
                              and _hue_dist(h, c[0]) < HUE_NEAR
                              and abs(l - c[1]) < LUM_NEAR), None)
                if clash is None:
                    break
                l = l + LUM_SHIFT if l >= clash[1] else l - LUM_SHIFT
                if l > 0.82:
                    l = clash[1] - LUM_SHIFT
                elif l < 0.22:
                    l = clash[1] + LUM_SHIFT
        if e["percent"] >= MIN_PCT_TO_ADJUST:
            used.append((h, l, sat))
        out[e["name"]] = _hex(h, l, sat)
    return out


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def pct(v):
    """0.0% para una linea que existe es falso: mejor decir que es poca."""
    return "&lt;0.1%" if 0 < v < 0.05 else f"{v:.1f}%"


def human(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)


def rows_for(items):
    return (len(items) + COLS - 1) // COLS


def section_height(items):
    """Alto de una barra + su lista de lenguajes."""
    return BAR_H + BAR_GAP + (rows_for(items) - 1) * ROW_H + 11


def draw_section(p, items, y, theme, theme_name, clip_id):
    """Barra apilada y lista en columnas. Devuelve la y del borde inferior."""
    bw = W - 2 * PAD
    col = distinguish(items, theme_name)
    p.append(f'<clipPath id="{clip_id}"><rect x="{PAD}" y="{y}" width="{bw}" '
             f'height="{BAR_H}" rx="{BAR_H/2}"/></clipPath>')
    p.append(f'<g clip-path="url(#{clip_id})">')
    p.append(f'<rect x="{PAD}" y="{y}" width="{bw}" height="{BAR_H}" '
             f'fill="{theme["track"]}"/>')
    x = float(PAD)
    for e in items:
        seg = bw * e["percent"] / 100
        if seg <= 0:
            continue
        # el hueco entre segmentos separa dos colores parecidos mejor que
        # cualquier ajuste de color
        p.append(f'<rect x="{x:.2f}" y="{y}" '
                 f'width="{max(seg - BAR_GAP_X, 1.2):.2f}" '
                 f'height="{BAR_H}" fill="{col[e["name"]]}"/>')
        x += seg
    p.append('</g>')

    rows = rows_for(items)
    col_w = bw / COLS
    list_y = y + BAR_H + BAR_GAP
    for i, e in enumerate(items):
        cx = PAD + (i // rows) * col_w
        cy = list_y + (i % rows) * ROW_H
        p.append(f'<circle cx="{cx+5:.1f}" cy="{cy}" r="5" '
                 f'fill="{col[e["name"]]}"/>')
        p.append(f'<text class="n" x="{cx+17:.1f}" y="{cy}">{esc(e["name"])}</text>')
        p.append(f'<text class="v" x="{cx+col_w-14:.1f}" y="{cy}">'
                 f'{pct(e["percent"])}</text>')
        p.append(f'<text class="v" x="{cx+col_w-14:.1f}" y="{cy+10.5}" '
                 f'style="font-size:9px">{human(e["lines"])}</text>')
    return list_y + (rows - 1) * ROW_H + 11


def render(data, theme_name):
    t = THEMES[theme_name]
    langs = data["languages"]
    other = data.get("other", [])
    tot = data["totals"]

    bar1_y = 78
    end1 = bar1_y + section_height(langs)
    if other:
        sep_y = end1 + SEC_GAP
        bar2_y = sep_y + HEAD_GAP
        height = bar2_y + section_height(other) + BOTTOM
    else:
        height = end1 + BOTTOM

    sub = (f'{human(tot["lines"])} lines of code &#183; {tot["files"]} files '
           f'&#183; {tot["commits"]} commits &#183; {data["repos_analyzed"]} repos '
           f'&#183; {data["generated_at"][:10]}')

    p = []
    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" '
        f'aria-label="Languages written by Pedro">')
    p.append(
        '<style>'
        'text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",'
        'Helvetica,Arial,sans-serif;dominant-baseline:middle}'
        f'.t{{font-size:15px;font-weight:600;fill:{t["title"]}}}'
        f'.s{{font-size:10.5px;fill:{t["muted"]}}}'
        f'.n{{font-size:11.5px;font-weight:500;fill:{t["text"]}}}'
        f'.v{{font-size:10.5px;fill:{t["muted"]};text-anchor:end}}'
        f'.h{{font-size:9px;font-weight:600;fill:{t["muted"]};letter-spacing:.09em}}'
        '</style>')
    p.append(
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{height-1}" rx="6" '
        f'fill="{t["bg"]}" stroke="{t["border"]}"/>')
    p.append(f'<text class="t" x="{PAD}" y="26">Languages I have written</text>')
    p.append(f'<text class="s" x="{PAD}" y="45">{sub}</text>')
    p.append(f'<text class="s" x="{PAD}" y="60">'
             f'surviving lines in HEAD, attributed by git blame -w -M -C</text>')

    draw_section(p, langs, bar1_y, t, theme_name, "c1")

    if other:
        p.append(f'<line x1="{PAD}" y1="{sep_y}" x2="{W-PAD}" y2="{sep_y}" '
                 f'stroke="{t["border"]}"/>')
        # los porcentajes de esta seccion son sobre sus propias lineas, no
        # sobre el total: decirlo o el numero enganaria.
        p.append(f'<text class="h" x="{PAD}" y="{sep_y+17}">'
                 f'MARKUP &amp; DATA &#183; {human(tot["lines_other"])} LINES, '
                 f'EXCLUDED FROM CODE &#183; % OF THIS SECTION</text>')
        draw_section(p, other, bar2_y, t, theme_name, "c2")

    p.append('</svg>')
    return "\n".join(p) + "\n"


def main():
    src = os.path.join(ROOT, "stats.json")
    if not os.path.exists(src):
        sys.exit("Falta stats.json. Ejecuta: python3 scripts/stats.py build")
    with open(src, encoding="utf-8") as fh:
        data = json.load(fh)
    if not data["languages"]:
        sys.exit("stats.json no tiene lenguajes.")
    os.makedirs(os.path.join(ROOT, "profile"), exist_ok=True)
    for name in THEMES:
        dest = os.path.join(ROOT, "profile", f"langs-{name}.svg")
        with open(dest, "w", encoding="utf-8") as fh:
            fh.write(render(data, name))
        print(f"-> {dest}")


if __name__ == "__main__":
    main()

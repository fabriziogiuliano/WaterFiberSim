"""
Piccolo generatore di file .drawio.svg: un SVG normale (visibile ovunque) con il sorgente draw.io
(mxGraph) incorporato nell'attributo `content`, così il file si apre e si modifica in draw.io.

Ogni forma viene scritta due volte, con le stesse coordinate e gli stessi stili: una nell'SVG e una nel
sorgente draw.io. Gli stili draw.io sono scelti per somigliare all'SVG (raggio degli angoli fisso,
margini, font Helvetica).

    d = Drawing(1200, 800, nome="pagina")
    d.box(10, 10, 120, 40, ["Titolo", "riga 2"])
    d.line([(10, 100), (200, 100)], color="#ff6a00", arrow=True)
    d.save("docs/img/esempio.drawio.svg")
"""
import html

FONT = "Helvetica, Arial, sans-serif"


def _esc(s):
    return html.escape(str(s), quote=True)


class Drawing:
    def __init__(self, width, height, nome="pagina", background="#ffffff"):
        self.W, self.H, self.nome, self.bg = width, height, nome, background
        self.svg, self.cells, self.colors, self._n = [], [], set(), 1

    def _id(self):
        self._n += 1
        return f"c{self._n}"

    def _cell(self, value, style, x, y, w, h):
        self.cells.append(f'<mxCell id="{self._id()}" value="{_esc(value)}" style="{style}" vertex="1" parent="1">'
                          f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')

    # ------------------------------------------------------------------ testo
    def _text_svg(self, x, y, righe, size, color, weight, anchor, style):
        out = [f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
               f'font-style="{style}" fill="{color}" text-anchor="{anchor}">']
        for i, r in enumerate(righe):
            out.append(f'<tspan x="{x}" dy="{0 if i == 0 else size * 1.25}">{_esc(r)}</tspan>')
        out.append("</text>")
        self.svg.append("".join(out))

    def label(self, x, y, righe, size=12, color="#1b1f24", weight="normal", anchor="start", style="normal", w=300,
              rotation=0):
        """Testo libero; (x, y) = linea di base della prima riga."""
        if isinstance(righe, str):
            righe = [righe]
        if rotation:
            self.svg.append(f'<g transform="rotate({rotation} {x} {y})">')
        self._text_svg(x, y, righe, size, color, weight, anchor, style)
        if rotation:
            self.svg.append("</g>")
        val = "<br>".join(_esc(r) for r in righe)
        if weight == "bold":
            val = f"<b>{val}</b>"
        if style == "italic":
            val = f"<i>{val}</i>"
        al = {"middle": "center", "start": "left", "end": "right"}[anchor]
        h = len(righe) * size * 1.25 + 4
        gx = x - w / 2 if anchor == "middle" else (x if anchor == "start" else x - w)
        self._cell(val, f"text;html=1;fontFamily=Helvetica;spacing=0;align={al};verticalAlign=top;fontSize={size};"
                        f"fontColor={color};whiteSpace=wrap;" + (f"rotation={rotation};" if rotation else ""),
                   gx, y - size, w, h)

    # ------------------------------------------------------------------ forme
    def box(self, x, y, w, h, righe=(), fill="#ffffff", stroke="#1b1f24", size=12, bold_first=True, color="#1b1f24",
            radius=6, dashed=False, sw=1.5, align="center"):
        righe = list(righe)
        d = ' stroke-dasharray="6 4"' if dashed else ""
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" '
                        f'stroke-width="{sw}"{d}/>')
        n = len(righe)
        y0 = y + h / 2 - (n - 1) * size * 1.25 / 2 + size * 0.35
        tx, anchor = (x + w / 2, "middle") if align == "center" else (x + 10, "start")
        for i, r in enumerate(righe):
            self._text_svg(tx, y0 + i * size * 1.25, [r], size, color,
                           "bold" if (i == 0 and bold_first) else "normal", anchor, "normal")
        val = "<br>".join((f"<b>{_esc(r)}</b>" if (i == 0 and bold_first) else _esc(r)) for i, r in enumerate(righe))
        self._cell(val, f"rounded={1 if radius else 0};absoluteArcSize=1;arcSize={2 * radius};whiteSpace=wrap;html=1;"
                        f"fillColor={fill};strokeColor={stroke};fontFamily=Helvetica;fontColor={color};fontSize={size};"
                        f"align={align};verticalAlign=middle;spacingLeft={10 if align == 'left' else 2};strokeWidth={sw};"
                        + ("dashed=1;" if dashed else ""), x, y, w, h)

    def circle(self, cx, cy, r, fill, stroke="none", text="", size=10, color="#ffffff", sw=1.5):
        self.svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        if text:
            self._text_svg(cx, cy + size * 0.36, [text], size, color, "bold", "middle", "normal")
        self._cell(f"<b>{_esc(text)}</b>" if text else "",
                   f"ellipse;html=1;fillColor={fill};strokeColor={stroke};strokeWidth={sw};fontFamily=Helvetica;"
                   f"fontSize={size};fontColor={color};", cx - r, cy - r, 2 * r, 2 * r)

    def square(self, cx, cy, s, fill):
        self.svg.append(f'<rect x="{cx - s / 2}" y="{cy - s / 2}" width="{s}" height="{s}" fill="{fill}"/>')
        self._cell("", f"rounded=0;fillColor={fill};strokeColor=none;", cx - s / 2, cy - s / 2, s, s)

    def triangle(self, x, y, verso, color, s=7):
        """Punta di freccia centrata in (x, y); verso = 'e', 'w', 'n', 's'."""
        v = {"e": [(x + s, y), (x - s, y - s), (x - s, y + s)], "w": [(x - s, y), (x + s, y - s), (x + s, y + s)],
             "n": [(x, y - s), (x - s, y + s), (x + s, y + s)], "s": [(x, y + s), (x - s, y - s), (x + s, y - s)]}[verso]
        self.svg.append('<polygon points="%s" fill="%s"/>' % (" ".join(f"{a},{b}" for a, b in v), color))
        d = {"e": "east", "w": "west", "n": "north", "s": "south"}[verso]
        self._cell("", f"triangle;direction={d};fillColor={color};strokeColor=none;", x - s, y - s, 2 * s, 2 * s)

    def line(self, punti, color="#1b1f24", sw=2.0, arrow=False, dashed=False, cap="round"):
        self.colors.add(color)
        pts = " ".join(f"{x},{y}" for x, y in punti)
        d = ' stroke-dasharray="7 5"' if dashed else ""
        me = f' marker-end="url(#m_{color.strip("#")})"' if arrow else ""
        self.svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{sw}" '
                        f'stroke-linecap="{cap}" stroke-linejoin="round"{d}{me}/>')
        (x0, y0), (x1, y1) = punti[0], punti[-1]
        wp = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in punti[1:-1])
        st = (f"endArrow={'block' if arrow else 'none'};startArrow=none;html=1;rounded=0;strokeColor={color};"
              f"strokeWidth={sw};" + ("dashed=1;" if dashed else ""))
        self.cells.append(f'<mxCell id="{self._id()}" style="{st}" edge="1" parent="1"><mxGeometry relative="1" '
                          f'as="geometry"><mxPoint x="{x0}" y="{y0}" as="sourcePoint"/>'
                          f'<mxPoint x="{x1}" y="{y1}" as="targetPoint"/>'
                          + (f'<Array as="points">{wp}</Array>' if wp else "") + "</mxGeometry></mxCell>")

    # ------------------------------------------------------------------ file
    def save(self, path):
        markers = "".join(f'<marker id="m_{c.strip("#")}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
                          f'markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
                          for c in sorted(self.colors))
        mx = (f'<mxfile host="drawio" type="device"><diagram id="d1" name="{_esc(self.nome)}"><mxGraphModel dx="0" '
              f'dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" '
              f'pageScale="1" pageWidth="{self.W}" pageHeight="{self.H}" math="0" shadow="0"><root><mxCell id="0"/>'
              '<mxCell id="1" parent="0"/>' + "".join(self.cells) + "</root></mxGraphModel></diagram></mxfile>")
        out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" '
               f'viewBox="0 0 {self.W} {self.H}" content="{_esc(mx)}"><defs>{markers}</defs>'
               f'<rect width="{self.W}" height="{self.H}" fill="{self.bg}"/>' + "".join(self.svg) + "</svg>")
        with open(path, "w") as f:
            f.write(out)
        return path

"""Petit moteur SVG de Wantre : texte vectorisé (glyphes OFL en <use>), thèmes, grain.
Bibliothèque standard uniquement, pour tourner aussi dans GitHub Actions."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ATLAS = json.load(open(os.path.join(HERE, 'glyphs.json'), encoding='utf-8'))
SYMBOL = json.load(open(os.path.join(HERE, 'symbol.json'), encoding='utf-8'))

THEMES = {
 'dark': dict(bg='#0B0705', panel='#120A06', panel2='#1C110A', line='#FFF2DF', lineo=.14,
              ink='#FFF2DF', ink2='#D8C8B5', mute='#9C8A79', braise='#FF5E1A', ambre='#FF9F2E',
              miel='#FFCE7A', halo1='#FFF1DC', halo2='#FFB24E', glow='#FF5E1A', rouille='#8E2C0C',
              onhalo='#1A0C06', grain='#FFFFFF', graino=.07,
              levels=['#1E130C', '#5A230D', '#9C330E', '#E8560F', '#FFA640']),
 'light': dict(bg='#FFF8EF', panel='#FFFCF8', panel2='#FFF0E0', line='#1A0E08', lineo=.13,
              ink='#1A0E08', ink2='#4B3A2D', mute='#806B5B', braise='#D9480B', ambre='#C9700C',
              miel='#B07A12', halo1='#FFE2BC', halo2='#FFB062', glow='#FF8A3D', rouille='#E9B48C',
              onhalo='#1A0C06', grain='#3A1A08', graino=.06,
              levels=['#F2E5D6', '#FFCF9E', '#FF9C4A', '#EC5F12', '#A83707']),
}

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

class Doc:
    def __init__(self, w, h, theme, title=''):
        self.w, self.h, self.theme = w, h, theme
        self.t = THEMES[theme]
        self.used = {}
        self.defs = []
        self.body = []
        self.css = []
        self.title = title
        self._id = 0

    def uid(self, p='i'):
        self._id += 1
        return f'{p}{self._id}'

    # ---- texte
    def width(self, text, font='B', size=14, ls=0.0):
        f = ATLAS[font]; g = f['g']
        adv = sum(g.get(c, g['?'])[0] for c in text)
        return adv * size / f['upm'] + ls * size * max(len(text) - 1, 0)

    def text(self, x, y, text, font='B', size=14, fill=None, anchor='start', ls=0.0, attrs=''):
        f = ATLAS[font]; g = f['g']; upm = f['upm']
        k = size / upm
        w = self.width(text, font, size, ls)
        if anchor == 'middle': x -= w / 2
        elif anchor == 'end': x -= w
        cx = 0.0; uses = []
        for c in text:
            if c not in g: c = '?'
            if c != ' ':
                gid = f'{font}{ord(c):x}'
                self.used[gid] = g[c][1]
                uses.append(f'<use href="#{gid}" x="{cx:.0f}"/>')
            cx += g[c][0] + ls * upm
        fill = fill or self.t['ink']
        return f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.4f})" fill="{fill}" {attrs}>{"".join(uses)}</g>'

    def wrap(self, text, width, font='B', size=13):
        words, lines, cur = text.split(' '), [], ''
        for wd in words:
            t = (cur + ' ' + wd).strip()
            if self.width(t, font, size) > width and cur:
                lines.append(cur); cur = wd
            else:
                cur = t
        if cur: lines.append(cur)
        return lines

    # ---- décor
    def grain_filter(self):
        if any('id="grain"' in d for d in self.defs): return
        t = self.t; c = t['grain'].lstrip('#'); r, g_, b = (int(c[i:i+2], 16) / 255 for i in (0, 2, 4))
        self.defs.append(f'<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7" stitchTiles="stitch"/>'
                         f'<feColorMatrix values="0 0 0 0 {r:.2f} 0 0 0 0 {g_:.2f} 0 0 0 0 {b:.2f} 0 0 0 {t["graino"]*4.6:.2f} -{t["graino"]*1.65:.2f}"/></filter>')

    def grain(self, clip=None):
        self.grain_filter()
        c = f' clip-path="url(#{clip})"' if clip else ''
        return f'<rect width="{self.w}" height="{self.h}" filter="url(#grain)"{c}/>'

    def plus(self, x, y, s=7, o=.75, col=None):
        col = col or self.t['ink']
        return f'<path d="M{x-s} {y}H{x+s}M{x} {y-s}V{y+s}" stroke="{col}" stroke-opacity="{o}" stroke-width="1.3"/>'

    def dashed(self, x1, y1, x2, y2, o=.3, dur=8, col=None):
        col = col or self.t['ink']
        return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-opacity="{o}" stroke-width="1" stroke-dasharray="4 5">'
                f'<animate attributeName="stroke-dashoffset" from="0" to="-18" dur="{dur}s" repeatCount="indefinite"/></line>')

    def card(self, x, y, w, h, r=18, fill=None, clip_id=None):
        t = self.t; fill = fill or t['panel']
        out = f'<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="{r}" fill="{fill}" stroke="{t["line"]}" stroke-opacity="{t["lineo"]}"/>'
        if clip_id:
            self.defs.append(f'<clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath>')
        return out

    def symbol(self, x, y, size, gid=None, flat=False):
        """Symbole Wantre : disque fendu par un W (viewBox 16..240)."""
        t = self.t; s = size / 224
        if flat:
            top = rest = t['braise']
        else:
            gt, gr = self.uid('st'), self.uid('sr')
            self.defs.append(f'<linearGradient id="{gt}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF7EA"/><stop offset="1" stop-color="#FFD592"/></linearGradient>'
                             f'<linearGradient id="{gr}" x1=".2" y1="0" x2=".7" y2="1"><stop offset="0" stop-color="#FFA23A"/><stop offset=".55" stop-color="#FF5E1A"/><stop offset="1" stop-color="#C93A0E"/></linearGradient>')
            top, rest = f'url(#{gt})', f'url(#{gr})'
        P = SYMBOL
        return (f'<g transform="translate({x - 16*s:.2f} {y - 16*s:.2f}) scale({s:.4f})">'
                f'<path fill="{top}" d="{P["top"]}"/><path fill="{rest}" d="{P["left"]}{P["right"]}{P["bottom"]}"/></g>')

    def add(self, *parts):
        self.body.extend(parts)

    def render(self, width_attr=None):
        glyphs = ''.join(f'<path id="{k}" d="{d}"/>' for k, d in self.used.items())
        css = f'<style>{"".join(self.css)}</style>' if self.css else ''
        title = f'<title>{esc(self.title)}</title>' if self.title else ''
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" role="img" fill="none">'
                f'{title}{css}<defs>{glyphs}{"".join(self.defs)}</defs>{"".join(self.body)}</svg>\n')

def typing(doc, lines, T, start=0.4, cps=16, hold=0.93, caret=True, caret_col=None):
    """lines: [(x, y, text, font, size, fill, delay_after)] tapées l'une après l'autre (SMIL discret).
    Renvoie les éléments SVG. Le cycle dure T secondes et boucle."""
    out = []; t = start; cx_vals, cy_vals, ckt = [], [], []
    for (x, y, text, font, size, fill, pause) in lines:
        cid = doc.uid('ty')
        n = len(text)
        times = [t + i / cps for i in range(n + 1)]
        widths = [doc.width(text[:i], font, size) for i in range(n + 1)]
        kt = [0.0] + [min(tt / T, hold - 0.001) for tt in times] + [hold, 1.0]
        vals = [0] + widths + [widths[-1], 0]
        # dédoublonner les keyTimes strictement croissants
        KT, V = [], []
        for k_, v in zip(kt, vals):
            if KT and k_ <= KT[-1]: k_ = KT[-1] + 1e-5
            KT.append(min(k_, 1.0)); V.append(v)
        KT[-1] = 1.0
        h = size * 1.4
        doc.defs.append(f'<clipPath id="{cid}"><rect x="{x}" y="{y - size*1.05:.1f}" height="{h:.1f}" width="0">'
                        f'<animate attributeName="width" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{";".join(f"{k:.5f}" for k in KT)}" values="{";".join(f"{v:.1f}" for v in V)}"/></rect></clipPath>')
        out.append(f'<g clip-path="url(#{cid})">{doc.text(x, y, text, font, size, fill)}</g>')
        for tt, wv in zip(times, widths):
            cx_vals.append(x + wv + 2); cy_vals.append(y - size * .9); ckt.append(tt / T)
        t = times[-1] + pause
    if caret and cx_vals:
        last_x, last_y = cx_vals[-1], cy_vals[-1]
        KT, X, Y = [0.0], [lines[0][0]], [lines[0][1] - lines[0][4] * .9]
        for k_, xx, yy in zip(ckt, cx_vals, cy_vals):
            k_ = min(k_, hold - .001)
            if k_ <= KT[-1]: k_ = KT[-1] + 1e-5
            KT.append(k_); X.append(xx); Y.append(yy)
        KT += [hold, 1.0]; X += [lines[0][0], lines[0][0]]; Y += [Y[0], Y[0]]
        sz = lines[0][4]
        col = caret_col or doc.t['braise']
        out.append(f'<rect width="{sz*.55:.1f}" height="{sz*1.1:.1f}" rx="1" fill="{col}">'
                   f'<animate attributeName="x" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{";".join(f"{k:.5f}" for k in KT)}" values="{";".join(f"{v:.1f}" for v in X)}"/>'
                   f'<animate attributeName="y" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{";".join(f"{k:.5f}" for k in KT)}" values="{";".join(f"{v:.1f}" for v in Y)}"/>'
                   f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    return out, t

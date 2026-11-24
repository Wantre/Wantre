"""Génère les visuels animés du profil (assets/*.svg), en variantes dark et light.
Usage : python3 scripts/build_assets.py"""
import os, re, math
from wsvg import Doc, typing, THEMES
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets')
ICONS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
W = 830

def save(name, doc):
    p = os.path.join(OUT, f'{name}-{doc.theme}.svg')
    open(p, 'w', encoding='utf-8').write(doc.render())
    return p

def icon_path(slug):
    s = open(os.path.join(ICONS, slug + '.svg'), encoding='utf-8').read()
    return re.search(r' d="([^"]+)"', s).group(1)

# ------------------------------------------------------------------ HERO
def hero(theme):
    d = Doc(W, 280, theme, 'Wantre, développeur généraliste. Code, apps et agents IA. Lyon, France.')
    t = d.t
    d.defs.append(f'<clipPath id="hc"><rect width="{W}" height="280" rx="20"/></clipPath>'
                  f'<radialGradient id="h1"><stop offset="0" stop-color="{t["halo1"]}"/><stop offset=".38" stop-color="{t["halo2"]}" stop-opacity=".95"/><stop offset=".7" stop-color="{t["halo2"]}" stop-opacity=".25"/><stop offset="1" stop-color="{t["halo2"]}" stop-opacity="0"/></radialGradient>'
                  f'<radialGradient id="h2"><stop offset="0" stop-color="{t["glow"]}" stop-opacity=".95"/><stop offset=".5" stop-color="{t["rouille"]}" stop-opacity=".55"/><stop offset="1" stop-color="{t["rouille"]}" stop-opacity="0"/></radialGradient>')
    g = [f'<g clip-path="url(#hc)"><rect width="{W}" height="280" fill="{t["bg"]}"/>',
         f'<ellipse cx="660" cy="146" rx="300" ry="200" fill="url(#h1)"><animate attributeName="rx" values="290;330;290" dur="11s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
         f'<animate attributeName="ry" values="190;215;190" dur="11s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></ellipse>',
         f'<ellipse cx="80" cy="330" rx="330" ry="170" fill="url(#h2)"><animate attributeName="opacity" values=".65;1;.65" dur="9s" repeatCount="indefinite"/></ellipse>',
         f'<ellipse cx="420" cy="-40" rx="260" ry="90" fill="url(#h2)" opacity=".35"/>',
         d.dashed(0, 84, W, 84), d.dashed(0, 196, W, 196), d.dashed(478, 0, 478, 280, dur=10),
         d.plus(478, 84, 8, 1), d.plus(478, 196, 8, 1),
         d.plus(22, 22), d.plus(W-22, 22), d.plus(22, 258), d.plus(W-22, 258),
         d.symbol(34, 98, 84),
         d.text(136, 162, 'wantre', 'H', 96, t['ink'], ls=-.03)]
    lines = [(506, 120, 'développeur généraliste', 'M', 14.5, t['onhalo'], .7),
             (506, 146, 'apps, sites et agents IA', 'M', 14.5, t['onhalo'], .7),
             (506, 172, 'région lyonnaise', 'M', 14.5, t['onhalo'], 1)]
    ty, _ = typing(d, lines, T=14, cps=14, caret_col=t['braise'])
    g += ty
    g += [d.text(46, 246, 'github.com/Wantre', 'M', 11.5, t['ink'], attrs='opacity=".75"'),
          d.text(W-46, 246, 'freelance depuis mes 16 ans', 'M', 11.5, t['onhalo'] if theme == 'dark' else t['ink'], anchor='end', attrs='opacity=".8"'),
          d.grain(), '</g>',
          f'<rect x=".5" y=".5" width="{W-1}" height="279" rx="20" stroke="{t["line"]}" stroke-opacity="{t["lineo"]}"/>']
    d.add(*g)
    return d

# ------------------------------------------------------------------ TERMINAL
def terminal(theme):
    H = 332
    d = Doc(W, H, theme, 'Terminal : présentation de Wantre')
    t = d.t
    g = [d.card(0, 0, W, H, 18, t['panel'], 'tc'), f'<g clip-path="url(#tc)">',
         f'<rect width="{W}" height="40" fill="{t["panel2"]}"/><line x1="0" y1="40.5" x2="{W}" y2="40.5" stroke="{t["line"]}" stroke-opacity="{t["lineo"]}"/>']
    for i, c in enumerate([t['braise'], t['ambre'], t['miel']]):
        g.append(f'<circle cx="{24 + i*18}" cy="20" r="5.5" fill="{c}"/>')
    g.append(d.text(W/2, 25, 'wantre@lyon : ~', 'M', 12, t['mute'], anchor='middle'))
    seq = [('whoami', ['wantre · développeur généraliste · région lyonnaise']),
           ('cat parcours.txt', ['freelance en informatique depuis 16 ans · bac pro ARED · 2 ans à 42 Lyon']),
           ('ls projets/', ['verriere/  better-grokbot/  jarvis-mcp/  quant-lab/  calame/  cinevr/']),
           ('wantre --focus', ['studio d’agents IA en Rust et Tauri 2, sites animés, outils MCP'])]
    T = 20.0; y = 76; tt = 0.6; cps = 13; hold = .94
    for cmd, outs in seq:
        g.append(f'<g opacity="0">{d.text(24, y, "~ $", "M", 14, t["braise"])}'
                 f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;{max(tt-.3,0.01)/T:.4f};{hold};1" values="0;1;0;0"/></g>')
        lines = [(60, y, cmd, 'M', 14, t['ink'], 0)]
        ty, end = typing(d, lines, T, start=tt, cps=cps, hold=hold, caret=False)
        g += ty
        appear = (end + .35) / T
        for o in outs:
            y += 24
            g.append(f'<g opacity="0">{d.text(24, y, o, "M", 13.5, t["ink2"])}'
                     f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;{appear:.4f};{hold};1" values="0;1;0;0"/></g>')
        tt = end + 1.4; y += 34
    k0 = (tt - 1.0) / T
    g.append(f'<g opacity="0">{d.text(24, y, "~ $", "M", 14, t["braise"])}<rect x="60" y="{y-13}" width="8" height="16" rx="1" fill="{t["braise"]}"><animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.1s" repeatCount="indefinite" calcMode="discrete"/></rect>'
             f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;{k0:.4f};{hold};1" values="0;1;0;0"/></g>')
    g += [d.grain('tc'), '</g>']
    d.add(*g)
    return d

# ------------------------------------------------------------------ STACK
STACK = [
    ('Langages', [('python', 'Python'), ('typescript', 'TypeScript'), ('javascript', 'JavaScript'), ('rust', 'Rust'), ('go', 'Go'),
                  ('dotnet', 'C# .NET'), ('cplusplus', 'C++'), ('openjdk', 'Java'), ('lua', 'Lua'), ('html5', 'HTML'), ('css', 'CSS')]),
    ('Interfaces et apps', [('react', 'React'), ('nextdotjs', 'Next.js'), ('vite', 'Vite'), ('tailwindcss', 'Tailwind'), ('framer', 'Motion'),
                            ('threedotjs', 'Three.js'), ('electron', 'Electron'), ('tauri', 'Tauri 2'), ('expo', 'Expo')]),
    ('Serveurs et données', [('nodedotjs', 'Node.js'), ('express', 'Express'), ('fastify', 'Fastify'), ('socketdotio', 'Socket.io'),
                             ('sqlite', 'SQLite'), ('drizzle', 'Drizzle'), ('discord', 'discord.js')]),
    ('Jeux, 3D, matériel', [('unity', 'Unity'), ('vrchat', 'VRChat'), ('godotengine', 'Godot'), ('arduino', 'Arduino'), ('raspberrypi', 'Raspberry')]),
    ('Agents IA', [('modelcontextprotocol', 'MCP'), ('claude', 'Claude'), ('cursor', 'Cursor'), ('googlegemini', 'Gemini'), ('ollama', 'Ollama')]),
]
def stack(theme):
    rows = len(STACK); H = 78 + rows * 76 + 8
    d = Doc(W, H, theme, 'Stack vérifiée dans mes projets')
    t = d.t
    g = [d.card(0, 0, W, H, 18, t['panel'], 'sc'), '<g clip-path="url(#sc)">',
         d.text(24, 38, 'Stack', 'H', 22, t['ink']),
         d.text(96, 38, 'relevée dans mes projets, pas recopiée d’une liste', 'M', 11.5, t['mute']),
         d.plus(W-26, 30, 6, .6)]
    N = sum(len(r[1]) for r in STACK); k = 0; T = 12.0
    y = 66
    for label, items in STACK:
        g.append(d.text(24, y + 34, label, 'S', 13, t['ink2']))
        x = 182
        for slug, name in items:
            a = .06 + .78 * k / N
            kt = f'0;{a:.3f};{a+.025:.3f};{a+.07:.3f};1'
            g.append(f'<rect x="{x}" y="{y}" width="52" height="62" rx="10" fill="{t["panel2"]}" stroke="{t["line"]}" stroke-opacity="{t["lineo"]*.8:.2f}">'
                     f'<animate attributeName="stroke" dur="{T}s" repeatCount="indefinite" keyTimes="{kt}" values="{t["line"]};{t["line"]};{t["braise"]};{t["line"]};{t["line"]}"/></rect>')
            g.append(f'<g transform="translate({x+15} {y+10}) scale(.9167)"><path d="{icon_path(slug)}" fill="{t["ink2"]}">'
                     f'<animate attributeName="fill" dur="{T}s" repeatCount="indefinite" keyTimes="{kt}" values="{t["ink2"]};{t["ink2"]};{t["braise"]};{t["ink2"]};{t["ink2"]}"/></path></g>')
            g.append(d.text(x + 26, y + 52, name, 'M', 8.6 if len(name) < 9 else 7.4, t['mute'], anchor='middle'))
            x += 58; k += 1
        y += 76
    g += [d.grain('sc'), '</g>']
    d.add(*g)
    return d

# ------------------------------------------------------------------ PROJETS
PROJECTS = [
 ('verriere', 'app de bureau · privé', 'Verrière', 'Studio de création de sites piloté par des agents IA : éditeur visuel, timeline d’animation, CMS et serveur MCP de 47 outils.', ['Rust', 'Tauri 2', 'MCP'], 'en cours'),
 ('better-grokbot', 'outil · public', 'Better GrokBot', 'Une copie de Grok Bot avec un vrai châssis : rail, palette Ctrl K, barre Répond vers d’autres IA, quotas en direct.', ['C#', 'Node.js', 'Electron'], 'voir →'),
 ('jarvis', 'bot · MCP', 'JarvisMCP', 'Bot Discord et serveur MCP qui relient mes agents à mes outils et à mes machines.', ['Python', 'Discord', 'MCP'], 'privé'),
 ('quant', 'web · backend · mobile', 'Quant Lab', 'Laboratoire d’analyse quantitative : interface web, API et application Android.', ['Web', 'API', 'Expo'], 'privé'),
 ('calame', 'démo · interface', 'Calame', 'Démo d’application bancaire façon néobanque : cartes réalistes, code de sécurité, transitions soignées.', ['Web', 'Animation'], 'démo'),
 ('cinevr', 'auto-hébergé · vitrine', 'CineVR', 'Médiathèque personnelle hébergée sur mon serveur, avec une salle de cinéma dans VRChat.', ['Python', 'Unity', 'UdonSharp'], 'voir →'),
 ('psycho', 'site · contenu', 'Psychopédia', 'Site de vulgarisation en psychologie : articles clairs, navigation par thèmes.', ['Web', 'Contenu'], 'privé'),
 ('jeux', 'jeux · 3D', 'Jeux et mondes', 'Prototypes de jeux et de mondes : Godot, Three.js dans Electron, mondes et avatars VRChat sous Unity.', ['Godot', 'Three.js', 'Unity'], 'labo'),
]
def motif(d, key, x, y):
    t = d.t; b, a, m, i2 = t['braise'], t['ambre'], t['miel'], t['ink2']
    lo = t['lineo']
    if key == 'verriere':
        gid = d.uid('vg'); cid = d.uid('vc')
        d.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{m}" stop-opacity="0"/><stop offset=".5" stop-color="{m}" stop-opacity=".55"/><stop offset="1" stop-color="{m}" stop-opacity="0"/></linearGradient>'
                      f'<clipPath id="{cid}"><rect x="{x}" y="{y+8}" width="44" height="52" rx="8"/><rect x="{x+18}" y="{y}" width="44" height="52" rx="8"/><rect x="{x+34}" y="{y+18}" width="36" height="44" rx="8"/></clipPath>')
        return (f'<rect x="{x}" y="{y+8}" width="44" height="52" rx="8" fill="{i2}" fill-opacity=".06" stroke="{i2}" stroke-opacity=".35"/>'
                f'<rect x="{x+18}" y="{y}" width="44" height="52" rx="8" fill="{a}" fill-opacity=".10" stroke="{a}" stroke-opacity=".6"/>'
                f'<rect x="{x+34}" y="{y+18}" width="36" height="44" rx="8" fill="{b}" fill-opacity=".14" stroke="{b}" stroke-opacity=".8"/>'
                f'<g clip-path="url(#{cid})"><rect x="{x-40}" y="{y-10}" width="30" height="90" fill="url(#{gid})" transform="skewX(-20)">'
                f'<animateTransform attributeName="transform" type="translate" values="0 0;130 0;130 0" keyTimes="0;.45;1" dur="6s" repeatCount="indefinite" additive="sum"/></rect></g>')
    if key == 'better-grokbot':
        return (f'<rect x="{x}" y="{y+4}" width="70" height="56" rx="9" stroke="{i2}" stroke-opacity=".4"/>'
                + ''.join(f'<circle cx="{x+10}" cy="{y+16+j*11}" r="3" fill="{b if j==1 else i2}" fill-opacity="{1 if j==1 else .45}"/>' for j in range(4)) +
                f'<line x1="{x+20}" y1="{y+4}" x2="{x+20}" y2="{y+60}" stroke="{i2}" stroke-opacity=".25"/>'
                f'<rect x="{x+44}" y="{y+10}" width="20" height="44" rx="5" fill="{a}" fill-opacity=".25" stroke="{a}" stroke-opacity=".8">'
                f'<animate attributeName="x" values="{x+70};{x+44};{x+44};{x+70}" keyTimes="0;.18;.7;1" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines=".2 .8 .2 1;0 0 1 1;.6 0 .8 .2"/>'
                f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.18;.75;1" dur="7s" repeatCount="indefinite"/></rect>')
    if key == 'jarvis':
        cx, cy = x + 35, y + 32; out = ''
        pts = [(cx + 30*math.cos(k_*2*math.pi/5 - math.pi/2), cy + 28*math.sin(k_*2*math.pi/5 - math.pi/2)) for k_ in range(5)]
        for k_, (px, py) in enumerate(pts):
            out += f'<line x1="{cx}" y1="{cy}" x2="{px:.1f}" y2="{py:.1f}" stroke="{i2}" stroke-opacity=".3"/><circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{t["panel2"]}" stroke="{a}"/>'
            out += (f'<circle r="2.4" fill="{b}"><animateMotion dur="3.2s" begin="{k_*.64:.2f}s" repeatCount="indefinite" path="M{cx},{cy} L{px:.1f},{py:.1f}"/>'
                    f'<animate attributeName="opacity" values="0;1;0" dur="3.2s" begin="{k_*.64:.2f}s" repeatCount="indefinite"/></circle>')
        return out + f'<circle cx="{cx}" cy="{cy}" r="8" fill="{b}"><animate attributeName="r" values="7;9;7" dur="3.2s" repeatCount="indefinite"/></circle>'
    if key == 'quant':
        pts = [(0, 44), (10, 38), (20, 42), (30, 26), (40, 30), (50, 14), (60, 20), (70, 6)]
        dd = 'M' + ' L'.join(f'{x+px},{y+py+6}' for px, py in pts)
        grid = ''.join(f'<line x1="{x}" y1="{y+6+gy}" x2="{x+70}" y2="{y+6+gy}" stroke="{i2}" stroke-opacity=".15"/>' for gy in (10, 26, 42))
        return (grid + f'<path d="{dd}" stroke="{b}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="120" stroke-dashoffset="120">'
                f'<animate attributeName="stroke-dashoffset" values="120;0;0;120" keyTimes="0;.45;.85;1" dur="7s" repeatCount="indefinite"/></path>'
                f'<circle r="3.5" fill="{m}"><animateMotion dur="7s" repeatCount="indefinite" keyPoints="0;1;1;0" keyTimes="0;.45;.85;1" calcMode="linear" path="{dd.replace("M","M").replace(" L"," L")}"/></circle>')
    if key == 'calame':
        gid = d.uid('cg'); cid = d.uid('cc')
        d.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2A1A12"/><stop offset="1" stop-color="#0E0806"/></linearGradient>'
                      f'<clipPath id="{cid}"><rect x="{x}" y="{y+10}" width="72" height="46" rx="7"/></clipPath>')
        return (f'<g transform="rotate(-8 {x+36} {y+33})"><rect x="{x}" y="{y+10}" width="72" height="46" rx="7" fill="url(#{gid})" stroke="{a}" stroke-opacity=".7"/>'
                f'<rect x="{x+8}" y="{y+22}" width="12" height="9" rx="2" fill="{m}" fill-opacity=".85"/>'
                f'<rect x="{x+8}" y="{y+42}" width="34" height="3" rx="1.5" fill="#FFF2DF" fill-opacity=".5"/>'
                f'<g clip-path="url(#{cid})"><rect x="{x-30}" y="{y}" width="16" height="70" fill="#FFF2DF" fill-opacity=".22" transform="skewX(-25)">'
                f'<animateTransform attributeName="transform" type="translate" values="0 0;120 0;120 0" keyTimes="0;.4;1" dur="5.5s" repeatCount="indefinite" additive="sum"/></rect></g></g>')
    if key == 'cinevr':
        cid = d.uid('fc')
        d.defs.append(f'<clipPath id="{cid}"><rect x="{x}" y="{y+12}" width="72" height="40" rx="6"/></clipPath>')
        holes = ''.join(f'<rect x="{x - 12 + j*12}" y="{y+15}" width="6" height="5" rx="1" fill="{t["panel"]}"/><rect x="{x - 12 + j*12}" y="{y+44}" width="6" height="5" rx="1" fill="{t["panel"]}"/>' for j in range(9))
        return (f'<g clip-path="url(#{cid})"><rect x="{x}" y="{y+12}" width="72" height="40" fill="{a}" fill-opacity=".85"/>'
                f'<g>{holes}<animateTransform attributeName="transform" type="translate" values="0 0;12 0" dur="1.6s" repeatCount="indefinite"/></g></g>'
                f'<path d="M{x+31} {y+24} L{x+44} {y+32} L{x+31} {y+40}Z" fill="{t["panel"]}"/>')
    if key == 'psycho':
        cx, cy = x + 36, y + 32; out = ''
        for j in range(3):
            out += (f'<circle cx="{cx}" cy="{cy}" r="6" stroke="{b if j==0 else a}" stroke-width="1.5" fill="none">'
                    f'<animate attributeName="r" values="6;30" dur="6s" begin="{j*2}s" repeatCount="indefinite"/>'
                    f'<animate attributeName="opacity" values=".9;0" dur="6s" begin="{j*2}s" repeatCount="indefinite"/></circle>')
        return out + f'<circle cx="{cx}" cy="{cy}" r="6" fill="{b}"/>'
    if key == 'jeux':
        frames = []
        V = [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
        E = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
        for f in range(25):
            th = f / 24 * math.pi / 2; ph = .5
            P = []
            for vx, vy, vz in V:
                X = vx*math.cos(th) - vz*math.sin(th); Z = vx*math.sin(th) + vz*math.cos(th)
                Y = vy*math.cos(ph) - Z*math.sin(ph)
                P.append((x + 36 + X*17, y + 32 + Y*17))
            frames.append(' '.join(f'M{P[a_][0]:.1f} {P[a_][1]:.1f}L{P[b_][0]:.1f} {P[b_][1]:.1f}' for a_, b_ in E))
        return (f'<path d="{frames[0]}" stroke="{a}" stroke-width="1.6" stroke-linecap="round"><animate attributeName="d" dur="8s" repeatCount="indefinite" values="{";".join(frames)}"/></path>'
                f'<circle cx="{x+36}" cy="{y+32}" r="3" fill="{b}"/>')
    return ''

def project(theme, p):
    key, tag, name, desc, chips, status = p
    Wc, Hc = 410, 214
    d = Doc(Wc, Hc, theme, f'{name} : {desc}')
    t = d.t
    g = [d.card(0, 0, Wc, Hc, 16, t['panel'], 'pc'), '<g clip-path="url(#pc)">',
         d.text(22, 34, tag, 'M', 10.5, t['mute']),
         d.text(22, 70, name, 'H', 26, t['ink'])]
    for j, line in enumerate(d.wrap(desc, 286, 'B', 12.8)[:4]):
        g.append(d.text(22, 98 + j * 18, line, 'B', 12.8, t['ink2']))
    x = 22
    for c in chips:
        w = d.width(c, 'M', 10) + 16
        g.append(f'<rect x="{x}" y="{Hc-38}" width="{w:.1f}" height="22" rx="11" stroke="{t["line"]}" stroke-opacity="{t["lineo"]*1.6:.2f}"/>')
        g.append(d.text(x + 8, Hc - 23, c, 'M', 10, t['ink2']))
        x += w + 6
    col = t['braise'] if status.endswith('→') else t['mute']
    g.append(d.text(Wc - 22, Hc - 23, status, 'M', 10.5, col, anchor='end'))
    g.append(motif(d, key, Wc - 98, 22))
    g += [d.grain('pc'), '</g>']
    d.add(*g)
    return d

# ------------------------------------------------------------------ ORBITE AGENTS
def orbit(theme):
    H = 400
    d = Doc(W, H, theme, 'Système : mes agents IA, leurs outils et les CLI reliées')
    t = d.t
    g = [d.card(0, 0, W, H, 18, t['panel'], 'oc'), '<g clip-path="url(#oc)">']
    gg = d.uid('og')
    d.defs.append(f'<radialGradient id="{gg}"><stop offset="0" stop-color="{t["glow"]}" stop-opacity=".55"/><stop offset="1" stop-color="{t["glow"]}" stop-opacity="0"/></radialGradient>')
    cx, cy = 562, 200
    g.append(f'<circle cx="{cx}" cy="{cy}" r="120" fill="url(#{gg})"><animate attributeName="r" values="105;130;105" dur="8s" repeatCount="indefinite"/></circle>')
    g += [d.text(28, 46, 'système', 'M', 11.5, t['mute']), d.text(28, 86, 'Un studio', 'H', 30, t['ink']),
          d.text(28, 120, 'd’agents IA', 'H', 30, t['ink'])]
    body = ('Mes agents Grok Bot travaillent en équipe : design, recherche, code. Ils partagent une bibliothèque de skills '
            'et appellent mes serveurs MCP. Verrière et Better GrokBot les relient aux CLI officielles, sans clé API.')
    for j, l in enumerate(d.wrap(body, 300, 'B', 13.2)):
        g.append(d.text(28, 156 + j * 20, l, 'B', 13.2, t['ink2']))
    g.append(d.text(28, H - 30, 'les points tournent en continu : chaque orbite a sa vitesse', 'M', 10.5, t['mute']))
    orbits = [(100, 44, 26, ['skills', 'MCP · 47 outils']),
              (150, 68, 40, ['Claude Code', 'Codex', 'Cursor']),
              (194, 92, 58, ['Gemini CLI', 'Grok Bot', 'OpenCode', 'Discord'])]
    for oi, (rx, ry, dur, names) in enumerate(orbits):
        path = f'M{cx-rx},{cy} a{rx},{ry} 0 1,0 {2*rx},0 a{rx},{ry} 0 1,0 {-2*rx},0'
        g.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" stroke="{t["ink"]}" stroke-opacity=".22" stroke-dasharray="3 6">'
                 f'<animate attributeName="stroke-dashoffset" from="0" to="{-18 if oi%2==0 else 18}" dur="5s" repeatCount="indefinite"/></ellipse>')
        for k_, nm in enumerate(names):
            ph = k_ / len(names)
            col = [t['miel'], t['ambre'], t['braise']][oi]
            g.append(f'<g><circle r="4.5" fill="{col}"/><circle r="9" fill="{col}" fill-opacity=".18"/>{d.text(10, 4, nm, "M", 11, t["ink"])}'
                     f'<animateMotion dur="{dur}s" begin="-{ph*dur:.2f}s" repeatCount="indefinite" path="{path}"/></g>')
    g.append(d.symbol(cx - 30, cy - 30, 60))
    g += [d.grain('oc'), '</g>']
    d.add(*g)
    return d

# ------------------------------------------------------------------ TIMELINE
def timeline(theme):
    H = 236
    d = Doc(W, H, theme, 'Parcours de Wantre')
    t = d.t
    g = [d.card(0, 0, W, H, 18, t['panel'], 'lc'), '<g clip-path="url(#lc)">',
         d.text(24, 34, 'parcours', 'M', 11.5, t['mute'])]
    y0 = 128; xs = [112, 263, 415, 567, 718]
    lg = d.uid('lg')
    d.defs.append(f'<linearGradient id="{lg}" x1="0" x2="1"><stop offset="0" stop-color="{t["rouille"]}"/><stop offset=".6" stop-color="{t["braise"]}"/><stop offset="1" stop-color="{t["ambre"]}"/></linearGradient>')
    g.append(f'<line x1="40" y1="{y0}" x2="{W-40}" y2="{y0}" stroke="url(#{lg})" stroke-width="2"/>')
    stops = [('Dès 16 ans', 'freelance en informatique'), ('Bac pro ARED', 'audiovisuel, domotique, électricité'),
             ('École 42 Lyon', 'deux ans de parcours'), ('Jeux et mondes', 'Unity, VRChat, Godot, Roblox'),
             ('Agents IA', 'Rust, Tauri, MCP, aujourd’hui')]
    T = 14.0
    for i, (x, (a, b)) in enumerate(zip(xs, stops)):
        f = (x - 40) / (W - 80) * .8
        g.append(f'<circle cx="{x}" cy="{y0}" r="7" fill="{t["panel"]}" stroke="{t["braise"]}" stroke-width="2"/>'
                 f'<circle cx="{x}" cy="{y0}" r="3.5" fill="{t["braise"]}"><animate attributeName="r" dur="{T}s" repeatCount="indefinite" keyTimes="0;{f:.3f};{f+.03:.3f};{f+.12:.3f};1" values="3;3;6;3;3"/></circle>')
        up = i % 2 == 0
        ya = y0 - 52 if up else y0 + 44
        g.append(d.text(x, ya, a, 'S', 13.5, t['ink'], anchor='middle'))
        g.append(d.text(x, ya + 19, b, 'B', 11.5, t['mute'], anchor='middle'))
        g.append(f'<line x1="{x}" y1="{y0 + (-12 if up else 12)}" x2="{x}" y2="{y0 + (-28 if up else 26)}" stroke="{t["ink"]}" stroke-opacity=".25" stroke-dasharray="2 3"/>')
    g.append(f'<circle r="5" fill="{t["miel"]}"><animateMotion dur="{T}s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;.8;1" calcMode="linear" path="M40,{y0} L{W-40},{y0}"/>'
             f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" keyTimes="0;.05;.78;.86;1" values="0;1;1;0;0"/></circle>')
    g += [d.grain('lc'), '</g>']
    d.add(*g)
    return d

# ------------------------------------------------------------------ EN CE MOMENT
def now(theme):
    H = 206
    d = Doc(W, H, theme, 'En ce moment')
    t = d.t
    g = [d.card(0, 0, W, H, 18, t['panel'], 'nc'), '<g clip-path="url(#nc)">',
         f'<circle cx="30" cy="31" r="5" fill="{t["braise"]}"/><circle cx="30" cy="31" r="5" fill="none" stroke="{t["braise"]}">'
         f'<animate attributeName="r" values="5;14" dur="2.4s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="2.4s" repeatCount="indefinite"/></circle>',
         d.text(46, 36, 'En ce moment', 'S', 14, t['ink'])]
    rows = [('Verrière 0.4', 'appels d’outils natifs, réponses mot à mot, vision'),
            ('Better GrokBot', 'site public sur GitHub Pages, prochaines versions'),
            ('Profil Wantre', 'identité de marque et widgets générés par GitHub Actions')]
    for i, (a, b) in enumerate(rows):
        y = 78 + i * 44
        g.append(f'<line x1="24" y1="{y-26}" x2="{W-24}" y2="{y-26}" stroke="{t["line"]}" stroke-opacity="{t["lineo"]}"/>')
        g.append(d.text(24, y, a, 'H', 17, t['ink']))
        g.append(d.text(190, y, b, 'B', 13, t['ink2']))
        for j in range(4):
            x = W - 60 + j * 9
            vals = ';'.join(str(v) for v in [(4 + (j*7 + i*5 + s*3) % 14) for s in range(6)] + [4 + (j*7 + i*5) % 14])
            g.append(f'<rect x="{x}" y="{y-16}" width="5" height="16" rx="2" fill="{t["braise"] if j%2==0 else t["ambre"]}" fill-opacity=".85">'
                     f'<animate attributeName="height" values="{vals}" dur="{5 + i}s" repeatCount="indefinite" calcMode="spline" keySplines="{";".join([".45 0 .55 1"]*6)}"/>'
                     f'<animate attributeName="y" values="{";".join(str(y - int(v)) for v in vals.split(";"))}" dur="{5 + i}s" repeatCount="indefinite" calcMode="spline" keySplines="{";".join([".45 0 .55 1"]*6)}"/></rect>')
    g += [d.grain('nc'), '</g>']
    d.add(*g)
    return d

# ------------------------------------------------------------------ SÉPARATEUR
def divider(theme):
    d = Doc(W, 30, theme, '')
    t = d.t
    d.add(d.dashed(0, 15, 396, 15, .35, 9), d.dashed(434, 15, W, 15, .35, 9),
          d.symbol(405, 5, 20, flat=False),
          f'<circle r="2.6" fill="{t["braise"]}"><animateMotion dur="12s" repeatCount="indefinite" path="M0,15 L{W},15"/>'
          f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.92;1" dur="12s" repeatCount="indefinite"/></circle>')
    return d

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for th in THEMES:
        for fn in (hero, terminal, stack, orbit, timeline, now, divider):
            save(fn.__name__, fn(th))
        for p in PROJECTS:
            save('projet-' + p[0], project(th, p))
    tot = 0
    for f in sorted(os.listdir(OUT)):
        if f.endswith('.svg'):
            s = os.path.getsize(os.path.join(OUT, f)); tot += s
    print('svg', len([f for f in os.listdir(OUT) if f.endswith('.svg')]), 'total', tot // 1024, 'Ko', 'max', max(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.endswith('.svg')) // 1024, 'Ko')

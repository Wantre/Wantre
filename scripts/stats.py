"""Widgets dynamiques du profil Wantre, générés chaque jour par GitHub Actions.
Écrit dist/stats-{dark,light}.svg et dist/calendar-{dark,light}.svg aux couleurs Wantre.
Données : API GraphQL de GitHub (GITHUB_TOKEN). Sans jeton : API REST publique, sans calendrier
(ou --calendar-json pour un aperçu local). Bibliothèque standard uniquement."""
import argparse, datetime as dt, json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wsvg import Doc, THEMES

LEVEL = {'NONE': 0, 'FIRST_QUARTILE': 1, 'SECOND_QUARTILE': 2, 'THIRD_QUARTILE': 3, 'FOURTH_QUARTILE': 4}
Q = """query($login:String!){user(login:$login){
 followers{totalCount}
 contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}
 repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100){totalCount nodes{name stargazerCount
   languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}"""

def http(url, data=None, token=None):
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'wantre-widgets', 'Accept': 'application/vnd.github+json'})
    if token: req.add_header('Authorization', f'bearer {token}')
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def fetch(login, token, cal_json=None):
    if token:
        d = http('https://api.github.com/graphql', json.dumps({'query': Q, 'variables': {'login': login}}).encode(), token)
        if 'errors' in d: raise SystemExit(d['errors'])
        u = d['data']['user']
        cal = u['contributionsCollection']['contributionCalendar']
        days = [(x['date'], x['contributionCount'], LEVEL.get(x['contributionLevel'], 0)) for w in cal['weeks'] for x in w['contributionDays']]
        repos = u['repositories']['nodes']
        langs = {}
        for r in repos:
            for e in r['languages']['edges']:
                langs[e['node']['name']] = langs.get(e['node']['name'], 0) + e['size']
        return dict(total=cal['totalContributions'], days=days, repos=u['repositories']['totalCount'],
                    stars=sum(r['stargazerCount'] for r in repos), followers=u['followers']['totalCount'], langs=langs)
    # mode aperçu, sans jeton
    repos = http(f'https://api.github.com/users/{login}/repos?per_page=100&type=owner')
    repos = [r for r in repos if not r['fork']]
    langs = {}
    for r in repos:
        for k, v in http(r['languages_url']).items(): langs[k] = langs.get(k, 0) + v
    user = http(f'https://api.github.com/users/{login}')
    days, total = [], None
    if cal_json:
        raw = json.load(open(cal_json))
        mx = max(raw.values()) or 1
        today = dt.date.fromisoformat(max(raw)) if raw else dt.date.today()
        start = today - dt.timedelta(days=(today.weekday() + 1) % 7 + 52 * 7)
        d = start
        while d <= today:
            c = raw.get(d.isoformat(), 0)
            lv = 0 if c == 0 else min(4, 1 + int(3 * c / mx + .0001))
            days.append((d.isoformat(), c, lv)); d += dt.timedelta(days=1)
        total = sum(c for _, c, _ in days)
    return dict(total=total, days=days, repos=len(repos), stars=sum(r['stargazers_count'] for r in repos),
                followers=user.get('followers', 0), langs=langs)

def streaks(days):
    cur = best = run = 0
    for _, c, _ in days:
        run = run + 1 if c > 0 else 0
        best = max(best, run)
    # série actuelle : on tolère que la journée en cours soit encore vide
    seq = [c for _, c, _ in days]
    if seq and seq[-1] == 0: seq = seq[:-1]
    for c in reversed(seq):
        if c > 0: cur += 1
        else: break
    return cur, best

def fmt(n):
    return '—' if n is None else f'{n:,}'.replace(',', ' ')

def stats_svg(theme, data, stamp):
    W, H = 830, 200
    d = Doc(W, H, theme, 'Statistiques GitHub de Wantre, générées chaque jour')
    t = d.t
    cur, best = streaks(data['days']) if data['days'] else (None, None)
    g = [d.card(0, 0, W, H, 18, t['panel'], 'kc'), '<g clip-path="url(#kc)">',
         d.text(24, 34, 'en direct', 'M', 11.5, t['mute']),
         d.text(W - 24, 34, f'mis à jour le {stamp}', 'M', 11, t['mute'], anchor='end')]
    nums = [(fmt(data['total']), 'contributions', '12 derniers mois'), (fmt(cur), 'série actuelle', 'jours d’affilée'),
            (fmt(best), 'meilleure série', 'sur l’année'), (fmt(data['repos']), 'dépôts publics', f'{fmt(data["stars"])} étoile' + ('s' if (data['stars'] or 0) > 1 else ''))]
    for i, (n, a, b) in enumerate(nums):
        x = 24 + i * 112
        g.append(f'<g opacity="0">{d.text(x, 96, n, "H", 34, t["ink"])}<animate attributeName="opacity" values="0;1" dur=".9s" begin="{.15 + i*.18:.2f}s" fill="freeze"/></g>')
        g.append(d.text(x, 122, a, 'S', 12, t['ink2']))
        g.append(d.text(x, 140, b, 'M', 10, t['mute']))
    # langages (octets de code des dépôts publics)
    x0, w0, y0 = 486, 320, 70
    g.append(d.text(x0, y0 - 14, 'langages des dépôts publics', 'S', 12, t['ink2']))
    langs = sorted(data['langs'].items(), key=lambda kv: -kv[1])
    tot = sum(v for _, v in langs) or 1
    top = langs[:5]
    if len(langs) > 5: top.append(('Autres', sum(v for _, v in langs[5:])))
    cols = [t['braise'], t['ambre'], t['miel'], t['rouille'], t['ink2'], t['mute']]
    x = x0
    g.append(f'<rect x="{x0}" y="{y0}" width="{w0}" height="10" rx="5" fill="{t["panel2"]}"/>')
    cid = d.uid('lb'); d.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{w0}" height="10" rx="5"/></clipPath>')
    bars = []
    for i, (name, v) in enumerate(top):
        w = w0 * v / tot
        bars.append(f'<rect x="{x:.1f}" y="{y0}" width="{w:.1f}" height="10" fill="{cols[i]}"/>')
        x += w
    g.append(f'<g clip-path="url(#{cid})"><g>{"".join(bars)}<animateTransform attributeName="transform" type="translate" values="-{w0} 0;0 0" dur="1.6s" fill="freeze" calcMode="spline" keySplines=".2 .8 .2 1"/></g></g>')
    for i, (name, v) in enumerate(top):
        cx = x0 + (i % 2) * 165; cy = y0 + 36 + (i // 2) * 22
        g.append(f'<circle cx="{cx+5}" cy="{cy-4}" r="4.5" fill="{cols[i]}"/>')
        g.append(d.text(cx + 16, cy, f'{name} {100*v/tot:.0f} %', 'M', 11, t['ink2']))
    if not langs:
        g.append(d.text(x0, y0 + 40, 'aucun code public pour l’instant', 'M', 11, t['mute']))
    g.append(d.text(24, H - 24, 'généré par scripts/stats.py dans ce dépôt, chaque jour à 6 h', 'M', 10, t['mute']))
    g += [d.grain('kc'), '</g>']
    d.add(*g)
    return d

def calendar_svg(theme, data):
    days = data['days']
    W, H = 830, 190
    d = Doc(W, H, theme, 'Graphe de contributions de Wantre, aux couleurs braise')
    t = d.t
    g = [d.card(0, 0, W, H, 18, t['panel'], 'cc'), '<g clip-path="url(#cc)">',
         d.text(24, 34, 'contributions', 'M', 11.5, t['mute'])]
    if not days:
        g.append(d.text(24, 100, 'le calendrier apparaît après le premier passage de l’action', 'M', 12, t['mute']))
    else:
        first = dt.date.fromisoformat(days[0][0])
        off = (first.weekday() + 1) % 7  # 0 = dimanche
        cell, gap = 11, 3
        weeks = (len(days) + off + 6) // 7
        x0 = (W - weeks * (cell + gap) + gap) / 2; y0 = 52
        months = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
        cols = {}
        lastm = None
        for i, (ds, c, lv) in enumerate(days):
            k = i + off; wk, wd = divmod(k, 7)
            dd = dt.date.fromisoformat(ds)
            if wd == 0 and dd.month != lastm and dd.day <= 7:
                g.append(d.text(x0 + wk * (cell + gap), y0 - 8, months[dd.month - 1], 'M', 9.5, t['mute'])); lastm = dd.month
            cols.setdefault(wk, []).append(f'<rect x="{x0 + wk*(cell+gap):.1f}" y="{y0 + wd*(cell+gap)}" width="{cell}" height="{cell}" rx="2.5" fill="{t["levels"][lv]}"/>')
        T = 9.0
        for wk, rects in cols.items():
            a = .05 + .8 * wk / weeks
            g.append(f'<g>{"".join(rects)}<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" keyTimes="0;{a:.3f};{a+.04:.3f};{a+.12:.3f};1" values=".78;.78;1;.78;.78"/></g>')
        # légende
        lx = W - 24 - 5 * 14 - 60
        g.append(d.text(lx - 6, H - 20, 'moins', 'M', 9.5, t['mute'], anchor='end'))
        for i in range(5):
            g.append(f'<rect x="{lx + i*14}" y="{H-30}" width="11" height="11" rx="2.5" fill="{t["levels"][i]}"/>')
        g.append(d.text(lx + 5 * 14 + 4, H - 20, 'plus', 'M', 9.5, t['mute']))
        g.append(d.text(24, H - 20, f'{fmt(data["total"])} contributions sur 12 mois', 'M', 10, t['ink2']))
    g += [d.grain('cc'), '</g>']
    d.add(*g)
    return d

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--user', default='Wantre'); ap.add_argument('--out', default='dist')
    ap.add_argument('--calendar-json', help='aperçu local : {"AAAA-MM-JJ": nombre}')
    a = ap.parse_args()
    try:
        data = fetch(a.user, os.environ.get('GITHUB_TOKEN'), a.calendar_json)
    except Exception as e:  # GraphQL indisponible : on garde des widgets lisibles, sans calendrier
        print('GraphQL indisponible, repli sur l’API REST :', e, file=sys.stderr)
        data = fetch(a.user, None, a.calendar_json)
    os.makedirs(a.out, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=1))).strftime('%d/%m/%Y')
    for th in THEMES:
        open(os.path.join(a.out, f'stats-{th}.svg'), 'w', encoding='utf-8').write(stats_svg(th, data, stamp).render())
        open(os.path.join(a.out, f'calendar-{th}.svg'), 'w', encoding='utf-8').write(calendar_svg(th, data).render())
    print('ok', a.out, 'total', data['total'], 'repos', data['repos'], 'langs', list(data['langs'])[:5])

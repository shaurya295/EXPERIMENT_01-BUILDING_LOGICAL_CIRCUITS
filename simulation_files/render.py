from circuits import C, EQ, simulate, stats
from itertools import product

HI, LO = '#1f8ef1', '#3a3a3a'
GW = 64            # gate body width incl. bubble space
PIN = 22           # pin pitch

def gate_svg(t, x, y0, h):
    ym = y0 + h/2
    bub = t in ('NAND','NOR','XNOR','NOT')
    s = []
    base = t.replace('N','',1) if t in ('NAND','NOR') else ('XOR' if t=='XNOR' else t)
    st = 'fill="#fff" stroke="#222" stroke-width="2"'
    if base == 'AND':
        s.append(f'<path d="M{x},{y0} H{x+26} A26,{h/2} 0 0 1 {x+26},{y0+h} H{x} Z" {st}/>'); ox = x+52
    elif base in ('OR','XOR'):
        sx = x+8 if base=='XOR' else x
        s.append(f'<path d="M{sx},{y0} Q{sx+14},{ym} {sx},{y0+h} Q{sx+34},{y0+h} {sx+52},{ym} Q{sx+34},{y0} {sx},{y0} Z" {st}/>')
        if base=='XOR':
            s.append(f'<path d="M{x},{y0} Q{x+14},{ym} {x},{y0+h}" fill="none" stroke="#222" stroke-width="2"/>')
        ox = sx+52
    elif base == 'NOT':
        s.append(f'<path d="M{x},{y0} L{x+40},{ym} L{x},{y0+h} Z" {st}/>'); ox = x+40
    if bub:
        s.append(f'<circle cx="{ox+5}" cy="{ym}" r="5" {st}/>'); ox += 10
    return ''.join(s), ox

def render(key, sample=None):
    eq, title, gates, out = C[key]
    vars_, f = EQ[eq]
    lits = {i for _, _, ins in gates for i in ins}
    comp = {i[1:] for i in lits if i.startswith('!')}
    used = [v for v in vars_ if v in lits or v in comp or any(i in (v, '!'+v) for i in lits)]
    used = [v for v in vars_ if v in {i.lstrip('!') for i in lits}]
    # choose a sample input (a 1-output combination) to display
    combos = [dict(zip(vars_, map(bool, b))) for b in product([0,1], repeat=len(vars_))]
    if sample is None:
        ones = [e for e in combos if simulate(gates, out, e)[1]]
        sample = ones[len(ones)//2]
    val, fo = simulate(gates, out, sample)
    def V(s):
        if s.startswith('!'): return not sample[s[1:]]
        return sample[s] if s in sample else val[s]
    col = lambda b: HI if b else LO
    sw = lambda b: 3 if b else 2

    # ---- rails ----
    rail = {}; x = 70; top = 60
    nots = []
    for v in used:
        rail[v] = x
        if v in comp:
            rail['!'+v] = x + 92; nots.append(v); x += 92 + 56
        else:
            x += 84
    rails_end = x
    # ---- columns ----
    gid = {g[0]: g for g in gates}
    colof = {}
    for g, t, ins in gates:
        colof[g] = 1 + max([colof[i] for i in ins if i in gid] or [0])
    ncol = max(colof.values())
    # vertical channel slots per column
    chan = {c: [] for c in range(1, ncol+1)}
    for g, t, ins in gates:
        for k, i in enumerate(ins):
            if i in gid: chan[colof[g]].append((g, k))
    colx = {}; cx = rails_end + 20
    for c in range(1, ncol+1):
        cx += 26 + 14*len(chan[c]) if chan[c] else 10
        colx[c] = cx; cx += GW + 8
    # ---- rows (parent sits in the middle of its children) ----
    order, seen = [], set()
    def place(g):
        if g in seen: return
        seen.add(g)
        kids = [i for i in gid[g][2] if i in gid and i not in seen]
        half = (len(kids)+1)//2
        for k in kids[:half]: place(k)
        order.append(g)
        for k in kids[half:]: place(k)
    place(out)
    y = 175; geo = {}
    for g in order:
        n = len(gid[g][2]); h = max(44, PIN*n)
        geo[g] = (colx[colof[g]], y, h); y += h + 26
    H = y + 40
    W = cx + 150
    wires, dots, body, labels = [], [], [], []
    # rail NOT gates + rails
    for v in used:
        xr = rail[v]; b = sample[v]
        wires.append(f'<line x1="{xr}" y1="{top+22}" x2="{xr}" y2="{H-30}" stroke="{col(b)}" stroke-width="{sw(b)}"/>')
        if v in comp:
            ny = top + 62; xn = xr + 18
            s, ox = gate_svg('NOT', xn, ny-15, 30); body.append(s)
            wires.append(f'<line x1="{xr}" y1="{ny}" x2="{xn}" y2="{ny}" stroke="{col(b)}" stroke-width="{sw(b)}"/>')
            dots.append(f'<circle cx="{xr}" cy="{ny}" r="4" fill="{col(b)}"/>')
            xc = rail['!'+v]; nb = not b
            wires.append(f'<polyline points="{ox},{ny} {xc},{ny} {xc},{H-30}" fill="none" stroke="{col(nb)}" stroke-width="{sw(nb)}"/>')
            labels.append(f'<text x="{xc+6}" y="{ny+30}" class="rl">{v}\'</text>')
        # toggle switch
        body.append(f'<g><rect x="{xr-20}" y="{top-22}" width="40" height="44" rx="6" fill="{"#e8f3ff" if b else "#f2f2f2"}" stroke="#555" stroke-width="2"/>'
                    f'<rect x="{xr-9}" y="{top-16 if b else top+2}" width="18" height="14" rx="3" fill="{HI if b else "#9a9a9a"}"/>'
                    f'<text x="{xr}" y="{top+ (16 if b else -4)}" text-anchor="middle" class="sv">{int(b)}</text>'
                    f'<text x="{xr-27}" y="{top+5}" text-anchor="end" class="vn">{v}</text></g>')
    # gates
    pin_y = lambda g, k: geo[g][1] + geo[g][2]*(k+0.5)/len(gid[g][2])
    outpt = {}
    for g, t, ins in gates:
        gx, gy, h = geo[g]
        s, ox = gate_svg(t, gx, gy, h); outpt[g] = (ox, gy + h/2)
        body.append(s)
        labels.append(f'<text x="{gx+4}" y="{gy-5}" class="gl">{t}</text>')
    # wires to gate inputs
    slot = {}
    for c in chan:
        for n, (g, k) in enumerate(chan[c]):
            slot[(g, k)] = colx[c] - 16 - 14*n
    for g, t, ins in gates:
        gx = geo[g][0]
        for k, i in enumerate(ins):
            py = pin_y(g, k); b = V(i); xin = gx + (10 if t in ('OR','NOR','XOR','XNOR') else 0)
            if i in gid:
                sx, sy = outpt[i]; vx = slot[(g, k)]
                wires.append(f'<polyline points="{sx},{sy} {vx},{sy} {vx},{py} {xin},{py}" fill="none" stroke="{col(b)}" stroke-width="{sw(b)}"/>')
                if ins.count(i) > 1 or sum(i in gg[2] for gg in gates) > 1:
                    dots.append(f'<circle cx="{vx}" cy="{sy}" r="4" fill="{col(b)}"/>')
            else:
                xr = rail[i]
                wires.append(f'<line x1="{xr}" y1="{py}" x2="{xin}" y2="{py}" stroke="{col(b)}" stroke-width="{sw(b)}"/>')
                dots.append(f'<circle cx="{xr}" cy="{py}" r="4" fill="{col(b)}"/>')
    # output bulb
    ox, oy = outpt[out]; bx = ox + 60
    wires.append(f'<line x1="{ox}" y1="{oy}" x2="{bx-18}" y2="{oy}" stroke="{col(fo)}" stroke-width="{sw(fo)}"/>')
    glow = f'<circle cx="{bx}" cy="{oy}" r="30" fill="#ffe46b" opacity="0.35"/>' if fo else ''
    body.append(f'{glow}<circle cx="{bx}" cy="{oy}" r="18" fill="{"#ffd83a" if fo else "#d9d9d9"}" stroke="#555" stroke-width="2"/>'
                f'<rect x="{bx-8}" y="{oy+17}" width="16" height="9" fill="#888"/>'
                f'<text x="{bx}" y="{oy+46}" text-anchor="middle" class="vn">{eq} = {int(fo)}</text>')
    W = max(W, bx + 70)
    st = '  '.join(f'{v}={int(sample[v])}' for v in vars_)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H+30}" viewBox="0 0 {W} {H+30}">
<style>text{{font-family:Helvetica,Arial,sans-serif}} .vn{{font-size:17px;font-weight:700;fill:#222}} .sv{{font-size:11px;font-weight:700;fill:#333}}
.gl{{font-size:10px;fill:#777;letter-spacing:.5px}} .rl{{font-size:13px;font-weight:700;fill:#555}}</style>
<defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#e3e3e3"/></pattern></defs>
<rect width="100%" height="100%" fill="#fff"/><rect width="100%" height="100%" fill="url(#grid)"/>
{''.join(wires)}{''.join(body)}{''.join(dots)}{''.join(labels)}
<rect x="0" y="{H}" width="{W}" height="30" fill="#f4f6f8" stroke="#ddd"/>
<text x="12" y="{H+20}" font-size="13" fill="#444"><tspan font-weight="700">{title}</tspan>   |   test input: {st}  →  {eq} = {int(fo)}   (blue wire = logic 1)</text>
</svg>'''
    return svg, W, H+30

if __name__ == '__main__':
    import json, os
    os.makedirs('svg', exist_ok=True)
    meta = {}
    for k in C:
        s, w, h = render(k)
        open(f'svg/{k}.svg', 'w').write(s); meta[k] = [w, h]
    json.dump(meta, open('svg/meta.json', 'w'))

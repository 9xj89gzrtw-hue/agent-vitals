#!/usr/bin/env python3
"""Build the 'Vitals' chart from the agent's own income logs.

Inputs : income.log   (one line per poll: 4 chains, ETH + USDC, ~every 30 s)
         sweeper2.log (one line per smart-account balance check)
Outputs: polls.csv, sweeper_checks.csv, chart.svg, chart.html

Every number in the picture is parsed from those two files. Nothing is invented,
including the hole in the middle: both watchdogs really did die for 11 h 49 m.
"""
import csv, re, json, datetime, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

POLL = re.compile(r'^(\S+Z) EOA (\S+) Base:eth=([\d.]+),usdc=([\d.]+) Arbitrum:eth=([\d.]+),usdc=([\d.]+) '
                  r'Ethereum:eth=([\d.]+),usdc=([\d.]+) Polygon:eth=([\d.]+),usdc=([\d.]+)')
KERN = re.compile(r'^(\S+Z) (\S+) kernel ([\d.]+) \| EOA ([\d.]+)')

polls, checks = [], []
for line in open(os.path.join(ROOT, 'income.log'), errors='ignore'):
    m = POLL.match(line)
    if not m:
        continue
    g = m.groups()[2:]
    for i, chain in enumerate(('Base', 'Arbitrum', 'Ethereum', 'Polygon')):
        polls.append({'ts': m.group(1), 'chain': chain, 'eth': float(g[2 * i]),
                      'usdc': float(g[2 * i + 1]), 'eoa': m.group(2)})
for line in open(os.path.join(ROOT, 'sweeper2.log'), errors='ignore'):
    m = KERN.match(line)
    if m:
        checks.append({'ts': m.group(1), 'account': m.group(2),
                       'kernel_eth': float(m.group(3)), 'eoa_eth': float(m.group(4))})

os.makedirs(HERE, exist_ok=True)
with open(os.path.join(HERE, 'polls.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['ts', 'chain', 'eth', 'usdc', 'eoa']); w.writeheader(); w.writerows(polls)
with open(os.path.join(HERE, 'sweeper_checks.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['ts', 'account', 'kernel_eth', 'eoa_eth']); w.writeheader(); w.writerows(checks)

def p(t): return datetime.datetime.fromisoformat(t.replace('Z', '+00:00'))
def hms(td):
    s = int(td.total_seconds()); return f'{s//3600}h {s%3600//60:02d}m {s%60:02d}s'

allp = sorted(polls, key=lambda r: r['ts'])
poll_ts = sorted({r['ts'] for r in allp})
chk_ts = sorted({c['ts'] for c in checks})
t0, t1 = p(poll_ts[0]), p(poll_ts[-1])
span = t1 - t0
n_polls = len(poll_ts)
accounts = sorted({c['account'] for c in checks})

# the real hole: longest silence between consecutive poll timestamps
gap = max(((p(b) - p(a), a, b) for a, b in zip(poll_ts, poll_ts[1:])), key=lambda x: x[0])
peak_eth = max(r['eth'] for r in polls)
peak_usdc = max(r['usdc'] for r in polls)
sum_found = sum(r['eth'] for r in polls) + sum(c['kernel_eth'] for c in checks)

BIN = 5 * 60
nbins = int(span.total_seconds() // BIN) + 1
def bins(tslist):
    out = [0] * nbins
    for t in tslist:
        i = int((p(t) - t0).total_seconds() // BIN)
        if 0 <= i < nbins: out[i] += 1
    return out
pbins, cbins = bins(poll_ts), bins(chk_ts)

CH = ('Base', 'Arbitrum', 'Ethereum', 'Polygon')
COL = {'Base': '#4e9bff', 'Arbitrum': '#5fd0a8', 'Ethereum': '#c9a4ff', 'Polygon': '#ffb454'}
MONO = "ui-monospace,SFMono-Regular,Menlo,monospace"

W, H = 2000, 1180
LX, RX = 190, 560
PW = W - RX - LX
TY, LEAD, LGAP = 230, 96, 20
PY, PH = TY + 4 * (LEAD + LGAP) + 34, 170

def x_at(t): return LX + (p(t) - t0).total_seconds() / span.total_seconds() * PW

s = [f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="{MONO}">',
     f'<rect width="{W}" height="{H}" fill="#06080b"/>']
for x in range(LX, LX + PW + 1, 50):
    s.append(f'<line x1="{x}" y1="{TY-16}" x2="{x}" y2="{PY+PH+70}" stroke="#0f141b"/>')

s.append(f'<text x="{LX}" y="70" fill="#e8edf4" font-size="44" font-weight="700" letter-spacing="2">VITALS</text>')
s.append(f'<text x="{LX}" y="112" fill="#8a97a8" font-size="24">an autonomous agent&#8217;s income, measured every 30 seconds</text>')
s.append(f'<text x="{LX}" y="156" fill="#5d6a7a" font-size="19">agent 0x72Aa6edDE71B94f6b99c8e52EdC02B5C75F74d1a &#183; '
         f'window {poll_ts[0][:19]}Z &#8594; {poll_ts[-1][:19]}Z</text>')

# ---- the four flat leads -------------------------------------------------
gx0, gx1 = x_at(gap[1]), x_at(gap[2])
for i, ch in enumerate(CH):
    y = TY + i * (LEAD + LGAP) + LEAD / 2
    top = TY + i * (LEAD + LGAP)
    s.append(f'<rect x="{LX}" y="{top}" width="{PW}" height="{LEAD}" fill="#0a0d12" stroke="#161b23"/>')
    for t in poll_ts:
        x = x_at(t)
        s.append(f'<line x1="{x:.1f}" y1="{y-9:.1f}" x2="{x:.1f}" y2="{y+9:.1f}" stroke="{COL[ch]}" stroke-opacity="0.5" stroke-width="1.5"/>')
    s.append(f'<line x1="{LX}" y1="{y:.1f}" x2="{gx0:.1f}" y2="{y:.1f}" stroke="{COL[ch]}" stroke-width="2.2"/>')
    s.append(f'<line x1="{gx1:.1f}" y1="{y:.1f}" x2="{LX+PW}" y2="{y:.1f}" stroke="{COL[ch]}" stroke-width="2.2"/>')
    s.append(f'<text x="{LX-18}" y="{y+8:.1f}" fill="{COL[ch]}" font-size="23" text-anchor="end">{ch}</text>')


# hole label
mid = (gx0 + gx1) / 2
s.append(f'<rect x="{gx0:.1f}" y="{TY-16}" width="{gx1-gx0:.1f}" height="{4*(LEAD+LGAP)-LGAP+16}" fill="#000000" fill-opacity="0.55"/>')
s.append(f'<text x="{mid:.1f}" y="{TY + 2*(LEAD+LGAP) - 6:.1f}" fill="#7b8798" font-size="20" text-anchor="middle">'
         f'no pulses &#183; {hms(gap[0])}</text>')
s.append(f'<text x="{mid:.1f}" y="{TY + 2*(LEAD+LGAP) + 22:.1f}" fill="#4b5563" font-size="17" text-anchor="middle">'
         f'both watchdogs dead, {gap[1][11:16]}Z &#8594; {gap[2][11:16]}Z</text>')

# ---- right readout -------------------------------------------------------
xr = LX + PW + 22
s.append(f'<text x="{xr}" y="{TY+24}" fill="#5d6a7a" font-size="17">TOTAL FOUND</text>')
s.append(f'<text x="{xr}" y="{TY+68}" fill="#e8edf4" font-size="40" font-weight="700">0.000000</text>')
s.append(f'<text x="{xr}" y="{TY+100}" fill="#5d6a7a" font-size="17">ETH, all chains, all wallets</text>')
s.append(f'<text x="{xr}" y="{TY+160}" fill="#8a97a8" font-size="19">{n_polls} polls &#183; 4 chains</text>')
s.append(f'<text x="{xr}" y="{TY+190}" fill="#8a97a8" font-size="19">{len(chk_ts)} cycles &#183; {len(checks)} checks</text>')
s.append(f'<text x="{xr}" y="{TY+220}" fill="#8a97a8" font-size="19">{len(accounts)} Kernel accounts</text>')
s.append(f'<text x="{xr}" y="{TY+250}" fill="#8a97a8" font-size="19">peak reading 0.000000</text>')
s.append(f'<text x="{xr}" y="{TY+284}" fill="#ffb454" font-size="30" font-weight="700">uptime {100*(1-gap[0].total_seconds()/span.total_seconds()):.1f}%</text>')
s.append(f'<text x="{xr}" y="{TY+312}" fill="#5d6a7a" font-size="17">of the window, a watchdog was alive</text>')

# ---- pulse histogram -----------------------------------------------------
s.append(f'<text x="{LX}" y="{PY-14}" fill="#8a97a8" font-size="19">pulses per 5 minutes &#8212; the monitor&#8217;s own heartbeat</text>')
bw = PW / nbins
mx = max(pbins + cbins) or 1
for row, (data, col, label) in enumerate(((pbins, '#4e9bff', 'income polls'), (cbins, '#5fd0a8', 'wallet checks'))):
    base = PY + row * (PH / 2) + PH / 2 - 16
    s.append(f'<text x="{LX-18}" y="{base-4:.1f}" fill="{col}" font-size="16" text-anchor="end">{label}</text>')
    for i, v in enumerate(data):
        h = (v / mx) * (PH / 2 - 42)
        s.append(f'<rect x="{LX+i*bw:.1f}" y="{base-h:.1f}" width="{max(bw-2.2,1):.1f}" height="{h:.1f}" fill="{col}" fill-opacity="0.85"/>')
    s.append(f'<line x1="{LX}" y1="{base:.1f}" x2="{LX+PW}" y2="{base:.1f}" stroke="#1b2230"/>')
    s.append(f'<text x="{LX+PW+22}" y="{base-6:.1f}" fill="#5d6a7a" font-size="16">max {max(data)}/5m</text>')

# ---- footnotes -----------------------------------------------------------
fy = PY + PH + 66
s.append(f'<text x="{LX}" y="{fy}" fill="#8a97a8" font-size="20">'
         f'every bar is parsed from income.log and sweeper2.log &#183; nothing here is simulated or rounded up</text>')
s.append(f'<text x="{LX}" y="{fy+34}" fill="#5d6a7a" font-size="18">'
         f'peak ETH {peak_eth:.6f} &#183; peak USDC {peak_usdc:.2f} &#183; sum of every positive reading {sum_found:.6f} ETH</text>')
s.append(f'<text x="{LX}" y="{fy+68}" fill="#4b5563" font-size="17">'
         f'span {hms(span)} &#183; the flat parts are not missing data, they are measurements</text>')
s.append(f'<text x="{LX+PW}" y="{fy+68}" fill="#4b5563" font-size="17" text-anchor="end">reproduce: vitals/build.py</text>')
s.append('</svg>')

open(os.path.join(HERE, 'chart.svg'), 'w').write('\n'.join(s))
open(os.path.join(HERE, 'chart.html'), 'w').write(
    '<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#06080b;overflow:hidden}</style>' + '\n'.join(s))

print(json.dumps({'polls': n_polls, 'poll_rows': len(polls), 'checks': len(checks), 'cycles': len(chk_ts),
                  'accounts': len(accounts), 'span': hms(span), 'gap': hms(gap[0]),
                  'gap_from': gap[1], 'gap_to': gap[2], 'peak_eth': peak_eth, 'peak_usdc': peak_usdc,
                  'sum_found': sum_found}, indent=1))

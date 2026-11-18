"""Netlists for every circuit in Experiment 01, a simulator, and an SVG schematic renderer."""
from itertools import product

# ---------------- reference equations (exactly as written in the README) ----------------
EQ = {
 'F1': ('ABCD',   lambda A,B,C,D: (not A and B and C) or (A and B and not D) or (not B and C and D) or (A and not C and D)),
 'F2': ('ABCD',   lambda A,B,C,D: (A or not B or C) and (not A or B or D) and (B or not C or not D)),
 'F3': ('ABCD',   lambda A,B,C,D: not (((not (A or B)) or (C and D)) and (A or not (B or C)))),
 'F4': ('ABCD',   lambda A,B,C,D: ((A ^ B) and (C == D)) or (not A and B and (C ^ D))),
 'F5': ('ABCDE',  lambda A,B,C,D,E: (A and B and not C) or (not A and D and E) or (B and C and not E) or (not B and C and D)),
 'F6': ('ABCDEG', lambda A,B,C,D,E,G: ((A or B) and not (C or D)) or ((C ^ E) and (D or G)) or (not A and B and E)),
 'F7': ('ABCD',   lambda A,B,C,D: (not (A and B) and not (C or D)) or (not (A or C) and B and D)),
 'F8': ('ABCDEF', lambda A,B,C,D,E,F: ((A ^ B) and (C == D)) or (not (A or B) and C and E) or (A and B and not (D or F))),
}

# ---------------- circuits: (equation, title, [(id, type, inputs)], output id) ----------------
# inputs: 'A' = switch A, '!A' = complemented rail (NOT gate under the switch), otherwise a gate id
C = {}
C['F1_original'] = ('F1', "F1 – original SOP", [
  ('g1','AND',['!A','B','C']), ('g2','AND',['A','B','!D']), ('g3','AND',['!B','C','D']), ('g4','AND',['A','!C','D']),
  ('F1','OR',['g1','g2','g3','g4'])], 'F1')
C['F1_simplified'] = ('F1', "F1 – simplified POS  (A+C)(B+D)(A'+B'+C'+D')", [
  ('o1','OR',['A','C']), ('n1','NAND',['A','B','C','D']), ('o2','OR',['B','D']),
  ('F1','AND',['o1','n1','o2'])], 'F1')
C['F2_original'] = ('F2', "F2 – original POS", [
  ('s1','OR',['A','!B','C']), ('s2','OR',['!A','B','D']), ('s3','OR',['B','!C','!D']),
  ('F2','AND',['s1','s2','s3'])], 'F2')
C['F2_nand'] = ('F2', "F2 – NAND-only implementation", [
  ('na','NAND',['A','A']), ('nb','NAND',['B','B']), ('nc','NAND',['C','C']), ('nd','NAND',['D','D']),
  ('t1','NAND',['na','B','nc']), ('t2','NAND',['A','nb','nd']), ('t3','NAND',['nb','C','D']),
  ('m','NAND',['t1','t2','t3']), ('F2','NAND',['m','m'])], 'F2')
C['F3_original'] = ('F3', "F3 – original nested-complement circuit", [
  ('n1','NOR',['A','B']), ('a1','AND',['C','D']), ('x','OR',['n1','a1']),
  ('n2','NOR',['B','C']), ('y','OR',['A','n2']),
  ('F3','NAND',['x','y'])], 'F3')
C['F3_nand_nor'] = ('F3', "F3 – NAND/NOR implementation of (A+B+C)(A'+C'+D')", [
  ('p','NOR',['A','B','C']), ('q','NAND',['A','C','D']), ('r','NOR',['q','q']),
  ('F3','NOR',['p','r'])], 'F3')
C['F4_xor_xnor'] = ('F4', "F4 – XOR / XNOR implementation", [
  ('x1','XOR',['A','B']), ('x2','XNOR',['C','D']), ('a1','AND',['x1','x2']),
  ('x3','XOR',['C','D']), ('a2','AND',['!A','B','x3']),
  ('F4','OR',['a1','a2'])], 'F4')
C['F4_basic'] = ('F4', "F4 – basic-gate (AND/OR/NOT) implementation  A'B + AB'CD + AB'C'D'", [
  ('p1','AND',['!A','B']), ('p2','AND',['A','!B','C','D']), ('p3','AND',['A','!B','!C','!D']),
  ('F4','OR',['p1','p2','p3'])], 'F4')
C['F5'] = ('F5', "F5 – five-input SOP (already minimal)", [
  ('g1','AND',['A','B','!C']), ('g2','AND',['!A','D','E']), ('g3','AND',['B','C','!E']), ('g4','AND',['!B','C','D']),
  ('F5','OR',['g1','g2','g3','g4'])], 'F5')
C['F6'] = ('F6', "F6 – six-input mixed logic", [
  ('o1','OR',['A','B']), ('n1','NOR',['C','D']), ('t1','AND',['o1','n1']),
  ('x1','XOR',['C','E']), ('o2','OR',['D','G']), ('t2','AND',['x1','o2']),
  ('t3','AND',['!A','B','E']),
  ('F6','OR',['t1','t2','t3'])], 'F6')
C['F7_nand_nor'] = ('F7', "F7 – NAND-NOR hybrid implementation", [
  ('g1','NAND',['A','B']), ('g2','NOR',['C','D']), ('g3','NAND',['g1','g2']),
  ('g4','NOR',['A','C']), ('g5','NAND',['g4','B','D']),
  ('F7','NAND',['g3','g5'])], 'F7')
C['F7_simplified'] = ('F7', "F7 – simplified  A'BC' + B'C'D'  (NOR-only)", [
  ('nb','NOR',['B','B']), ('t1','NOR',['A','nb','C']), ('t2','NOR',['B','C','D']),
  ('m','NOR',['t1','t2']), ('F7','NOR',['m','m'])], 'F7')
C['F8'] = ('F8', "F8 – six-input advanced combinational logic", [
  ('x1','XOR',['A','B']), ('x2','XNOR',['C','D']), ('t1','AND',['x1','x2']),
  ('n1','NOR',['A','B']), ('t2','AND',['n1','C','E']),
  ('a1','AND',['A','B']), ('n2','NOR',['D','F']), ('t3','AND',['a1','n2']),
  ('F8','OR',['t1','t2','t3'])], 'F8')

OPS = {
 'AND': lambda v: all(v), 'OR': lambda v: any(v), 'NAND': lambda v: not all(v), 'NOR': lambda v: not any(v),
 'XOR': lambda v: sum(v) % 2 == 1, 'XNOR': lambda v: sum(v) % 2 == 0, 'NOT': lambda v: not v[0],
}

def simulate(gates, out, env):
    val = {}
    def get(s):
        if s.startswith('!'): return not env[s[1:]]
        if s in env: return env[s]
        return val[s]
    for gid, t, ins in gates:   # gates are listed in topological order
        val[gid] = OPS[t]([get(i) for i in ins])
    return val, val[out]

def stats(gates, out):
    lits = {i for _, _, ins in gates for i in ins}
    nots = sorted({i[1:] for i in lits if i.startswith('!')})
    cnt = {}
    for _, t, ins in gates:
        key = t if not (t in ('NAND', 'NOR') and len(set(ins)) == 1) else t + ' (as inverter)'
        cnt[key] = cnt.get(key, 0) + 1
    if nots: cnt['NOT'] = cnt.get('NOT', 0) + len(nots)
    lvl = {}
    def L(s):
        if s.startswith('!'): return 1
        if s in lvl: return lvl[s]
        return 0
    for gid, t, ins in gates:
        lvl[gid] = 1 + max(L(i) for i in ins)
    return cnt, sum(cnt.values()), lvl[out]

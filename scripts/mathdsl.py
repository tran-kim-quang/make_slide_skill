# -*- coding: utf-8 -*-
"""Tiny LaTeX-subset -> OMML converter.  Emits OMML for PowerPoint (a:rPr inside m:r),
OMML for Word/docx (w:rPr inside m:r, QA only) and a linear Unicode fallback string."""
from xml.sax.saxutils import escape
import re

SYM = {
    'beta': '\u03b2', 'gamma': '\u03b3', 'delta': '\u03b4', 'theta': '\u03b8', 'lambda': '\u03bb',
    'mu': '\u03bc', 'sigma': '\u03c3', 'omega': '\u03c9', 'varepsilon': '\u03b5', 'sim': '\u223c',
    'subset': '\u2282', 'cup': '\u222a', 'emptyset': '\u2205', 'leq': '\u2264', 'geq': '\u2265',
    'div': '\u00f7', 'mid': '\u2223', 'Leftarrow': '\u21d0', 'neg': '\u00ac',
    'cdot': '\u22c5', 'perp': '\u22a5', 'Leftrightarrow': '\u21d4', 'Rightarrow': '\u21d2',
    'ne': '\u2260', 'le': '\u2264', 'ge': '\u2265', 'exists': '\u2203', 'in': '\u2208',
    'pm': '\u00b1', 'approx': '\u2248', 'triangle': '\u25b3', 'circ': '\u00b0', 'angle': '\u2220',
    'forall': '\u2200', 'times': '\u00d7', 'quad': '\u2003', ',': '\u2009', ' ': '\u2002',
    'R': '\u211d', 'deg': '\u00b0', 'minus': '\u2212', 'parallel': '\u2225', 'equiv': '\u2261',
    'notin': '\u2209', 'cap': '\u2229', 'varphi': '\u03c6', 'alpha': '\u03b1', 'pi': '\u03c0',
    'ldots': '\u2026', 'infty': '\u221e', 'dots': '\u2026', 'cdots': '\u22ef', 'neq': '\u2260', 'to': '\u2192', 'lbrace': '{', 'rbrace': '}',
}
UPRIGHT_SYMS = set()


class Node:  # base
    pass


class Run(Node):
    def __init__(self, t, sty=None):
        self.t, self.sty = t, sty


class Seq(Node):
    def __init__(self, items):
        self.items = items


class Acc(Node):
    def __init__(self, e, chr_='\u20d7'):
        self.e, self.chr = e, chr_


class Frac(Node):
    def __init__(self, n, d):
        self.n, self.d = n, d


class Rad(Node):
    def __init__(self, e):
        self.e = e


class Scr(Node):
    def __init__(self, base, sub=None, sup=None):
        self.base, self.sub, self.sup = base, sub, sup


class Delim(Node):
    def __init__(self, e, beg, end):
        self.e, self.beg, self.end = e, beg, end


class Func(Node):
    def __init__(self, name, arg):
        self.name, self.arg = name, arg


class Bar(Node):
    def __init__(self, e):
        self.e = e


class Nary(Node):
    def __init__(self, chr_, sub, sup, e):
        self.chr, self.sub, self.sup, self.e = chr_, sub, sup, e


class EqArr(Node):
    def __init__(self, rows):
        self.rows = rows


# ---------------------------------------------------------------- parser
class Parser:
    def __init__(self, s):
        self.s, self.i = s, 0

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else None

    def group(self):
        """parse {...} or a single atom"""
        self.skip()
        if self.peek() == '{':
            self.i += 1
            items = self.seq(until='}')
            self.i += 1
            return Seq(items)
        return self.atom()

    def skip(self):
        while self.peek() == ' ':
            self.i += 1

    def cmdname(self):
        j = self.i
        if j < len(self.s) and not self.s[j].isalpha():
            self.i += 1
            return self.s[j]
        while j < len(self.s) and self.s[j].isalpha():
            j += 1
        name = self.s[self.i:j]
        self.i = j
        return name

    def atom(self):
        self.skip()
        c = self.peek()
        if c is None:
            return None
        if c == '\\':
            self.i += 1
            name = self.cmdname()
            if name == 'vec':
                return Acc(self.group())
            if name in ('overline', 'bar'):
                return Bar(self.group())
            if name == 'sum':
                sub = sup = None
                self.skip()
                if self.peek() == '_':
                    self.i += 1; sub = self.group(); self.skip()
                if self.peek() == '^':
                    self.i += 1; sup = self.group()
                return Nary('\u2211', sub, sup, self.group())
            if name == 'Delta':
                return Run('\u0394', 'p')
            if name in ('widehat', 'hat'):
                return Acc(self.group(), '\u0302')
            if name == 'frac':
                n = self.group(); d = self.group()
                return Frac(n, d)
            if name == 'sqrt':
                return Rad(self.group())
            if name == 'left':
                beg = self.delimchar()
                items = self.seq(until='\\right')
                self.i += len('\\right')
                end = self.delimchar()
                return Delim(Seq(items), beg, end)
            if name in ('cos', 'sin', 'tan', 'lim'):
                self.skip()
                sup = None
                if self.peek() == '^':
                    self.i += 1
                    sup = self.group()
                f = Func(name, self.group())
                f.sup = sup
                return f
            if name == 'text':
                self.skip(); assert self.peek() == '{'
                j = self.s.index('}', self.i)
                t = self.s[self.i + 1:j]
                self.i = j + 1
                return Run(t, 'p')
            if name == 'up':  # upright group (point labels etc.)
                g = self.group()
                return Run(lin(g), 'p')
            if name == 'sys':
                self.skip(); assert self.peek() == '{'
                self.i += 1
                rows, cur = [], []
                while True:
                    self.skip()
                    if self.s.startswith('\\\\', self.i):
                        self.i += 2; rows.append(Seq(cur)); cur = []; continue
                    if self.peek() == '}':
                        self.i += 1; rows.append(Seq(cur)); break
                    a = self.scripted()
                    cur.append(a)
                return Delim(EqArr(rows), '{', '')
            if name == 'numtxt':
                self.skip(); assert self.peek() == '{'
                j = self.s.index('}', self.i)
                t = self.s[self.i + 1:j]
                self.i = j + 1
                return Run(t, 'num')
            if name == 'mathbb':
                g = self.group()
                return Run(''.join({'N': '\u2115', 'R': '\u211d', 'Z': '\u2124', 'Q': '\u211a'}.get(c, c) for c in lin(g)), 'p')
            if name == 'R':
                return Run('\u211d', 'p')
            if name in SYM:
                return Run(SYM[name])
            raise ValueError('unknown cmd ' + name)
        if c == '{':
            return self.group()
        if c.isdigit():
            mt = re.match(r'\d+,(\d+|[a-z]+|(?=\())', self.s[self.i:])
            if mt:
                self.i += len(mt.group(0))
                return Run(mt.group(0), 'num')
            mt = re.match(r'\d+', self.s[self.i:])
            self.i += len(mt.group(0))
            return Run(mt.group(0))
        self.i += 1
        if c == "'":
            return Run('\u2032')
        if c == '-':
            return Run('\u2212')
        return Run(c)

    def delimchar(self):
        self.skip()
        if self.s.startswith('\\{', self.i):
            self.i += 2; return '{'
        if self.s.startswith('\\}', self.i):
            self.i += 2; return '}'
        c = self.s[self.i]; self.i += 1
        return '' if c == '.' else c

    def scripted(self):
        a = self.atom()
        while True:
            self.skip()
            c = self.peek()
            if c in ('_', '^'):
                self.i += 1
                g = self.group()
                if not isinstance(a, Scr):
                    a = Scr(a)
                if c == '_':
                    a.sub = g
                else:
                    a.sup = g
            elif c == "'" and isinstance(a, Run):
                self.i += 1
                a = Run(a.t + '\u2032', a.sty)
            else:
                return a

    def seq(self, until=None):
        items = []
        while True:
            self.skip()
            if self.i >= len(self.s):
                return items
            if until and self.s.startswith(until, self.i):
                return items
            if until == '}' and self.peek() == '}':
                return items
            items.append(self.scripted())


def parse(s):
    s = re.sub(r'(\d+)\^\{?\\circ\}?', lambda m: '\\numtxt{' + m.group(1) + '\u00b0}', s)
    s = s.replace('^{\\circ}', '\\deg ').replace('^\\circ', '\\deg ')
    return Seq(Parser(s).seq())


# ---------------------------------------------------------------- linear fallback
def lin(n):
    if n is None:
        return ''
    if isinstance(n, Run):
        return n.t
    if isinstance(n, Seq):
        return ''.join(lin(x) for x in n.items)
    if isinstance(n, Acc):
        return lin(n.e) + '\u20d7'
    if isinstance(n, Frac):
        a, b = lin(n.n), lin(n.d)
        a = a if len(a) == 1 else '(' + a + ')'
        b = b if len(b) == 1 else '(' + b + ')'
        return a + '/' + b
    if isinstance(n, Rad):
        return '\u221a(' + lin(n.e) + ')'
    if isinstance(n, Scr):
        sup = {'2': '\u00b2', '3': '\u00b3'}
        r = lin(n.base)
        if n.sub is not None:
            r += lin(n.sub)
        if n.sup is not None:
            s = lin(n.sup)
            r += sup.get(s, '^' + s)
        return r
    if isinstance(n, Delim):
        return n.beg + lin(n.e) + n.end
    if isinstance(n, Func):
        sp = ('^' + lin(n.sup)) if getattr(n, 'sup', None) is not None else ''
        return n.name + sp + ' ' + lin(n.arg)
    if isinstance(n, EqArr):
        return ' ; '.join(lin(r) for r in n.rows)
    if isinstance(n, Bar):
        return lin(n.e) + '\u0304'
    if isinstance(n, Nary):
        return '\u2211' + lin(n.e)
    raise TypeError(n)


# ---------------------------------------------------------------- OMML
class Style:
    def __init__(self, target='a', sz=16, color='FFFFFF', bold=False):
        self.target, self.sz, self.color, self.bold = target, sz, color, bold


def _rpr(st, upright):
    if st.target == 'a':
        b = ' b="1"' if st.bold else ''
        return (f'<a:rPr lang="en-US" sz="{int(st.sz*100)}" i="{0 if upright else 1}"{b}>'
                f'<a:solidFill><a:srgbClr val="{st.color}"/></a:solidFill>'
                f'<a:latin typeface="Cambria Math" panose="02040503050406030204" pitchFamily="18" charset="0"/>'
                f'<a:cs typeface="Cambria Math" panose="02040503050406030204" pitchFamily="18" charset="0"/></a:rPr>')
    b = '<w:b/>' if st.bold else ''
    return (f'<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/>{b}'
            f'<w:color w:val="{st.color}"/><w:sz w:val="{int(st.sz*2)}"/></w:rPr>')


def mrun(t, st, sty=None):
    up = sty in ('p', 'num')
    mrpr = '<m:rPr><m:sty m:val="p"/></m:rPr>' if up else ''
    if sty == 'num':
        mrpr = '<m:rPr><m:nor/></m:rPr>'
    if st.bold and not up:
        mrpr = '<m:rPr><m:sty m:val="bi"/></m:rPr>'
    return f'<m:r>{mrpr}{_rpr(st, up)}<m:t>{escape(t)}</m:t></m:r>'


def ctrl(st):
    if st.target == 'a':
        return f'<m:ctrlPr>{_rpr(st, False)}</m:ctrlPr>'
    return f'<m:ctrlPr>{_rpr(st, False)}</m:ctrlPr>'


def omml(n, st):
    if n is None:
        return ''
    if isinstance(n, Run):
        return mrun(n.t, st, n.sty)
    if isinstance(n, Seq):
        out, buf = [], ''
        # merge consecutive plain italic runs
        for x in n.items:
            if isinstance(x, Run) and x.sty is None:
                buf += x.t
            else:
                if buf:
                    out.append(mrun(buf, st)); buf = ''
                out.append(omml(x, st))
        if buf:
            out.append(mrun(buf, st))
        return ''.join(out)
    if isinstance(n, Acc):
        return (f'<m:acc><m:accPr><m:chr m:val="{n.chr}"/>{ctrl(st)}</m:accPr>'
                f'<m:e>{omml(n.e, st)}</m:e></m:acc>')
    if isinstance(n, Frac):
        return (f'<m:f><m:fPr>{ctrl(st)}</m:fPr><m:num>{omml(n.n, st)}</m:num>'
                f'<m:den>{omml(n.d, st)}</m:den></m:f>')
    if isinstance(n, Rad):
        return (f'<m:rad><m:radPr><m:degHide m:val="on"/>{ctrl(st)}</m:radPr><m:deg/>'
                f'<m:e>{omml(n.e, st)}</m:e></m:rad>')
    if isinstance(n, Scr):
        b = omml(n.base, st)
        if n.sub is not None and n.sup is not None:
            return (f'<m:sSubSup><m:sSubSupPr>{ctrl(st)}</m:sSubSupPr><m:e>{b}</m:e>'
                    f'<m:sub>{omml(n.sub, st)}</m:sub><m:sup>{omml(n.sup, st)}</m:sup></m:sSubSup>')
        if n.sub is not None:
            return (f'<m:sSub><m:sSubPr>{ctrl(st)}</m:sSubPr><m:e>{b}</m:e>'
                    f'<m:sub>{omml(n.sub, st)}</m:sub></m:sSub>')
        return (f'<m:sSup><m:sSupPr>{ctrl(st)}</m:sSupPr><m:e>{b}</m:e>'
                f'<m:sup>{omml(n.sup, st)}</m:sup></m:sSup>')
    if isinstance(n, Delim):
        return (f'<m:d><m:dPr><m:begChr m:val="{escape(n.beg)}"/><m:endChr m:val="{escape(n.end)}"/>'
                f'{ctrl(st)}</m:dPr><m:e>{omml(n.e, st)}</m:e></m:d>')
    if isinstance(n, Func):
        fn = mrun(n.name, st, "p")
        if getattr(n, 'sup', None) is not None:
            fn = f'<m:sSup><m:sSupPr>{ctrl(st)}</m:sSupPr><m:e>{fn}</m:e><m:sup>{omml(n.sup, st)}</m:sup></m:sSup>'
        return (f'<m:func><m:funcPr>{ctrl(st)}</m:funcPr><m:fName>{fn}</m:fName>'
                f'<m:e>{omml(n.arg, st)}</m:e></m:func>')
    if isinstance(n, Bar):
        return (f'<m:bar><m:barPr><m:pos m:val="top"/>{ctrl(st)}</m:barPr><m:e>{omml(n.e, st)}</m:e></m:bar>')
    if isinstance(n, Nary):
        hs = '' if n.sub is not None else '<m:subHide m:val="on"/>'
        hp = '' if n.sup is not None else '<m:supHide m:val="on"/>'
        return (f'<m:nary><m:naryPr><m:chr m:val="{n.chr}"/><m:limLoc m:val="undOvr"/>{hs}{hp}{ctrl(st)}</m:naryPr>'
                f'<m:sub>{omml(n.sub, st)}</m:sub><m:sup>{omml(n.sup, st)}</m:sup><m:e>{omml(n.e, st)}</m:e></m:nary>')
    if isinstance(n, EqArr):
        rows = ''.join(f'<m:e>{omml(r, st)}</m:e>' for r in n.rows)
        return f'<m:eqArr><m:eqArrPr>{ctrl(st)}</m:eqArrPr>{rows}</m:eqArr>'
    raise TypeError(n)

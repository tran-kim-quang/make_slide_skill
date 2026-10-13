# -*- coding: utf-8 -*-
import math as pymath
import re
from xml.sax.saxutils import escape
from mathdsl import parse, omml, lin, Style

EMU = 914400
FONT = 'Times New Roman'
# Palette: override by setting env var MATHSLIDE_PALETTE (JSON) BEFORE importing engine
# (build.py --palette does this). Keys: BG CARD BORDER YEL CYAN WHITE MINT ORANGE PINK
import json as _json, os as _os
_PAL = {'BG': '0E3822', 'CARD': '13462C', 'BORDER': '80DEEA', 'YEL': 'FFEB3B', 'CYAN': '80DEEA',
        'WHITE': 'F5F5F5', 'MINT': 'C8E6C9', 'ORANGE': 'FFAB91', 'PINK': 'F48FB1'}
_PAL.update(_json.loads(_os.environ.get('MATHSLIDE_PALETTE', '{}') or '{}'))
BG, CARD, BORDER, YEL, CYAN = _PAL['BG'], _PAL['CARD'], _PAL['BORDER'], _PAL['YEL'], _PAL['CYAN']
WHITE, MINT, ORANGE, PINK = _PAL['WHITE'], _PAL['MINT'], _PAL['ORANGE'], _PAL['PINK']


def E(v):
    return int(round(v * EMU))


# ------------------------------------------------------------ runs / paragraphs
class T:  # text run
    def __init__(self, t, b=False, i=False, color=WHITE, sz=None):
        self.t, self.b, self.i, self.color, self.sz = t, b, i, color, sz


class M:  # inline math run
    def __init__(self, src, color=WHITE, sz=None, bold=False):
        self.src, self.node, self.color, self.sz, self.bold = src, parse(src), color, sz, bold


class TAB:
    pass


class P:
    def __init__(self, runs, align='l', sz=16, before=0, after=4, display=False, tabs=None,
                 indent=0, hang=0, jc='centerGroup', line=None):
        self.runs, self.align, self.sz, self.before, self.after = runs, align, sz, before, after
        self.display, self.tabs, self.indent, self.hang, self.jc, self.line = display, tabs or [], indent, hang, jc, line

    def has_math(self):
        return any(isinstance(r, M) for r in self.runs)


def rich(s, color=WHITE, sz=None, mcolor=None):
    """'text $math$ text **bold**' -> runs"""
    runs = []
    parts = re.split(r'(\$[^$]*\$|\*\*[^*]*\*\*|\t)', s)
    for p in parts:
        if not p:
            continue
        if p == '\t':
            runs.append(TAB())
        elif p.startswith('$'):
            runs.append(M(p[1:-1], color=mcolor or color, sz=sz))
        elif p.startswith('**'):
            runs.append(T(p[2:-2], b=True, color=color, sz=sz))
        else:
            runs.append(T(p, color=color, sz=sz))
    return runs


# convenient paragraph builders
def H(text, sz=18, color=YEL, after=6):
    return P([T(text, b=True, color=color)], align='ctr', sz=sz, after=after)


BODY = [16]


def set_body(v):
    BODY[0] = v


def L(label, body='', sz=None, after=5, lc=CYAN, **kw):
    sz = sz or BODY[0]
    runs = []
    if label:
        for r in rich(label + ' ', color=lc):
            if isinstance(r, T):
                r.b = True
            runs.append(r)
    runs += rich(body)
    return P(runs, sz=sz, after=after, **kw)


def D(src, sz=None, after=5, before=0, color=WHITE, jc='centerGroup'):
    sz = sz or BODY[0]
    return P([M(src, color=color)], align='ctr', sz=sz, after=after, before=before, display=True, jc=jc)


def TX(s, sz=None, after=5, align='l', color=WHITE, **kw):
    sz = sz or BODY[0]
    return P(rich(s, color=color), sz=sz, after=after, align=align, **kw)


# ------------------------------------------------------------ pptx paragraph emitter
def a_rpr(r, psz):
    sz = r.sz or psz
    return (f'<a:rPr lang="vi-VN" sz="{int(sz*100)}" b="{1 if r.b else 0}" i="{1 if r.i else 0}" dirty="0">'
            f'<a:solidFill><a:srgbClr val="{r.color}"/></a:solidFill>'
            f'<a:latin typeface="{FONT}" panose="02020603050405020304" pitchFamily="18" charset="0"/>'
            f'<a:ea typeface="{FONT}"/><a:cs typeface="{FONT}" panose="02020603050405020304" pitchFamily="18" charset="0"/></a:rPr>')


def a_para(p, mode):
    """mode: 'math' (OMML) or 'lin' (fallback text)"""
    algn = {'l': 'l', 'ctr': 'ctr', 'r': 'r'}[p.align]
    ind = ''
    if p.indent or p.hang:
        ind = f' marL="{E(p.indent + p.hang)}" indent="{-E(p.hang)}"'
    tabs = ''
    if p.tabs:
        tabs = '<a:tabLst>' + ''.join(f'<a:tab pos="{E(t)}" algn="l"/>' for t in p.tabs) + '</a:tabLst>'
    ln = f'<a:lnSpc><a:spcPct val="{int(p.line*1000)}"/></a:lnSpc>' if p.line else ''
    ppr = (f'<a:pPr algn="{algn}"{ind}>{ln}<a:spcBef><a:spcPts val="{int(p.before*100)}"/></a:spcBef>'
           f'<a:spcAft><a:spcPts val="{int(p.after*100)}"/></a:spcAft><a:buNone/>{tabs}</a:pPr>')
    out = []
    for r in p.runs:
        if isinstance(r, T):
            out.append(f'<a:r>{a_rpr(r, p.sz)}<a:t>{escape(r.t)}</a:t></a:r>')
        elif isinstance(r, TAB):
            out.append(f'<a:r>{a_rpr(T(""), p.sz)}<a:t>\t</a:t></a:r>')
        elif isinstance(r, M):
            st = Style('a', r.sz or p.sz, r.color, r.bold)
            if mode == 'math':
                body = omml(r.node, st)
                if p.display:
                    out.append(f'<a14:m><m:oMathPara><m:oMathParaPr><m:jc m:val="{p.jc}"/></m:oMathParaPr>'
                               f'<m:oMath>{body}</m:oMath></m:oMathPara></a14:m>')
                else:
                    out.append(f'<a14:m><m:oMath>{body}</m:oMath></a14:m>')
            else:
                rr = T(lin(r.node), i=True, color=r.color, sz=r.sz, b=r.bold)
                out.append(f'<a:r>{a_rpr(rr, p.sz)}<a:t>{escape(rr.t)}</a:t></a:r>')
    end = (f'<a:endParaRPr lang="vi-VN" sz="{int(p.sz*100)}" dirty="0"><a:solidFill><a:srgbClr val="{WHITE}"/></a:solidFill>'
           f'<a:latin typeface="{FONT}"/></a:endParaRPr>')
    return f'<a:p>{ppr}{"".join(out)}{end}</a:p>'


# ------------------------------------------------------------ docx paragraph emitter (QA)
def w_para(p, k=1.0):
    jc = {'l': 'left', 'ctr': 'center', 'r': 'right'}[p.align]
    tabs = ''
    if p.tabs:
        tabs = '<w:tabs>' + ''.join(f'<w:tab w:val="left" w:pos="{int(t*1440*k)}"/>' for t in p.tabs) + '</w:tabs>'
    ind = ''
    if p.indent or p.hang:
        ind = f'<w:ind w:left="{int((p.indent+p.hang)*1440*k)}" w:hanging="{int(p.hang*1440*k)}"/>'
    line = int(240 * (p.line or 1.0) * 1.05)
    ppr = (f'<w:pPr>{tabs}<w:spacing w:before="{int(p.before*20*k)}" w:after="{int(p.after*20*k)}" '
           f'w:line="{line}" w:lineRule="auto"/>{ind}<w:jc w:val="{jc}"/></w:pPr>')
    out = []
    for r in p.runs:
        if isinstance(r, T):
            sz = r.sz or p.sz
            out.append(f'<w:r><w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FONT}"/>'
                       f'{"<w:b/>" if r.b else ""}{"<w:i/>" if r.i else ""}<w:color w:val="{r.color}"/>'
                       f'<w:sz w:val="{int(round(sz*2*k))}"/></w:rPr><w:t xml:space="preserve">{escape(r.t)}</w:t></w:r>')
        elif isinstance(r, TAB):
            out.append('<w:r><w:tab/></w:r>')
        else:
            st = Style('w', r.sz or p.sz, r.color, r.bold)
            body = omml(r.node, st)
            if p.display:
                j = 'center' if p.jc == 'centerGroup' else p.jc
                out.append(f'<m:oMathPara><m:oMathParaPr><m:jc m:val="{j}"/></m:oMathParaPr><m:oMath>{body}</m:oMath></m:oMathPara>')
            else:
                out.append(f'<m:oMath>{body}</m:oMath>')
    return f'<w:p>{ppr}{"".join(out)}</w:p>'


# ------------------------------------------------------------ slide
class Slide:
    def __init__(self, idx):
        self.idx = idx
        self.items = []  # xml strings or callables(mode)
        self.nid = 2
        self.qa_jobs = []  # (name, w, h, paras)
        self.pics = []  # (rid, filename)

    def id(self):
        self.nid += 1
        return self.nid

    # ---------------- generic text shape
    def shape(self, x, y, w, h, paras, geom='rect', fill=None, line=None, lw=1.5, ins=(0.18, 0.12, 0.18, 0.12),
              anchor='t', name='TextBox', txbox=True, adj=None, dash=None, shadow=False):
        sid = self.id()
        nm = f'{name} {sid}'
        fillx = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else '<a:noFill/>'
        dashx = f'<a:prstDash val="{dash}"/>' if dash else ''
        linex = (f'<a:ln w="{int(lw*12700)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill>{dashx}</a:ln>'
                 if line else '<a:ln><a:noFill/></a:ln>')
        av = f'<a:gd name="adj" fmla="val {adj}"/>' if adj is not None else ''
        l, t, r, b = ins
        cnv = '<p:cNvSpPr txBox="1"/>' if txbox else '<p:cNvSpPr/>'

        def build(mode):
            if mode == 'qa':
                body = '<a:p><a:endParaRPr lang="vi-VN"/></a:p>'
            else:
                body = ''.join(a_para(p, mode) for p in paras) or '<a:p><a:endParaRPr lang="vi-VN"/></a:p>'
            return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{nm}"/>{cnv}<p:nvPr/></p:nvSpPr>'
                    f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm>'
                    f'<a:prstGeom prst="{geom}"><a:avLst>{av}</a:avLst></a:prstGeom>{fillx}{linex}</p:spPr>'
                    f'<p:txBody><a:bodyPr wrap="square" lIns="{E(l)}" tIns="{E(t)}" rIns="{E(r)}" bIns="{E(b)}" '
                    f'anchor="{anchor}" rtlCol="0"><a:noAutofit/></a:bodyPr><a:lstStyle/>{body}</p:txBody></p:sp>')

        has_math = any(p.has_math() for p in paras)
        if has_math:
            jobname = f's{self.idx:02d}_{sid}'
            self.qa_jobs.append((jobname, w - l - r, h - t - b, paras, anchor))

            def item(mode, build=build, jobname=jobname):
                if mode == 'final':
                    return ('<mc:AlternateContent><mc:Choice Requires="a14">' + build('math') +
                            '</mc:Choice><mc:Fallback>' + build('lin') + '</mc:Fallback></mc:AlternateContent>')
                if mode == 'final_img':
                    # Choice: editable Office Math. Fallback (only for apps without equation support,
                    # e.g. PowerPoint 2007, Google Slides): the shape plus a rendered picture of its text,
                    # the same strategy PowerPoint itself uses when saving equations.
                    rid = f'rIdQ{len(self.pics)+10}'
                    self.pics.append((rid, jobname + '.png'))
                    pid = self.id(); gid = self.id()
                    pic = (f'<p:pic><p:nvPicPr><p:cNvPr id="{pid}" name="Equation Preview {pid}"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>'
                           f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
                           f'<p:spPr><a:xfrm><a:off x="{E(x+l)}" y="{E(y+t)}"/><a:ext cx="{E(w-l-r)}" cy="{E(h-t-b)}"/></a:xfrm>'
                           f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')
                    grp = (f'<p:grpSp><p:nvGrpSpPr><p:cNvPr id="{gid}" name="Equation Fallback {gid}"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
                           f'<p:grpSpPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/>'
                           f'<a:chOff x="{E(x)}" y="{E(y)}"/><a:chExt cx="{E(w)}" cy="{E(h)}"/></a:xfrm></p:grpSpPr>'
                           + build('qa') + pic + '</p:grpSp>')
                    return ('<mc:AlternateContent><mc:Choice Requires="a14">' + build('math') +
                            '</mc:Choice><mc:Fallback>' + grp + '</mc:Fallback></mc:AlternateContent>')
                if mode == 'qa':
                    rid = f'rIdQ{len(self.pics)+10}'
                    self.pics.append((rid, jobname + '.png'))
                    pid = self.id()
                    pic = (f'<p:pic><p:nvPicPr><p:cNvPr id="{pid}" name="QA {pid}"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>'
                           f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
                           f'<p:spPr><a:xfrm><a:off x="{E(x+l)}" y="{E(y+t)}"/><a:ext cx="{E(w-l-r)}" cy="{E(h-t-b)}"/></a:xfrm>'
                           f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')
                    return build('qa') + pic
                return build('lin')
            self.items.append(item)
        else:
            self.items.append(lambda mode, build=build: build('lin'))

    def table(self, x, y, colw, rows, rowh=0.36, sz=15, head_fill='2E6B47', fill=None, line=None,
              bold_first_col=False, hl=None, name='Table'):
        """native editable table; rows: list of list of str. hl: {(r,c): color} text highlight"""
        sid = self.id()
        fill = fill or CARD; line = line or BORDER
        hl = hl or {}
        W = sum(colw); H = rowh * len(rows)
        grid = ''.join(f'<a:gridCol w="{E(c)}"/>' for c in colw)
        trs = ''
        for ri, row in enumerate(rows):
            tcs = ''
            for ci, txt in enumerate(row):
                head = ri == 0
                b = head or (bold_first_col and ci == 0)
                col = hl.get((ri, ci), YEL if head else WHITE)
                ln = ''.join(f'<a:{t} w="12700"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:{t}>' for t in ('lnL', 'lnR', 'lnT', 'lnB'))
                f = head_fill if head else fill
                tcs += (f'<a:tc><a:txBody><a:bodyPr/><a:lstStyle/><a:p><a:pPr algn="ctr"/>'
                        f'<a:r>{a_rpr(T(txt, b=b, color=col), sz)}<a:t>{escape(txt)}</a:t></a:r></a:p></a:txBody>'
                        f'<a:tcPr marL="45720" marR="45720" marT="27432" marB="27432" anchor="ctr">{ln}'
                        f'<a:solidFill><a:srgbClr val="{f}"/></a:solidFill></a:tcPr></a:tc>')
            trs += f'<a:tr h="{E(rowh)}">{tcs}</a:tr>'
        xml = (f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{sid}" name="{name} {sid}"/>'
               f'<p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
               f'<p:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(W)}" cy="{E(H)}"/></p:xfrm>'
               f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
               f'<a:tbl><a:tblPr firstRow="1"/><a:tblGrid>{grid}</a:tblGrid>{trs}</a:tbl></a:graphicData></a:graphic></p:graphicFrame>')
        self.items.append(lambda mode, xml=xml: xml)

    def rect(self, x, y, w, h, fill, line=None, lw=1.0, name='Bar', alpha=None):
        sid = self.id()
        al = f'<a:alpha val="{int(alpha*1000)}"/>' if alpha is not None else ''
        linex = (f'<a:ln w="{int(lw*12700)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>' if line else '<a:ln><a:noFill/></a:ln>')
        xml = (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{name} {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
               f'<p:spPr><a:xfrm><a:off x="{E(x)}" y="{E(y)}"/><a:ext cx="{E(w)}" cy="{E(h)}"/></a:xfrm>'
               f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{fill}">{al}</a:srgbClr></a:solidFill>{linex}</p:spPr>'
               f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="vi-VN"/></a:p></p:txBody></p:sp>')
        self.items.append(lambda mode, xml=xml: xml)

    def card(self, x, y, w, h, paras, **kw):
        kw.setdefault('fill', CARD); kw.setdefault('line', BORDER); kw.setdefault('geom', 'roundRect')
        kw.setdefault('adj', 6000); kw.setdefault('name', 'Card'); kw.setdefault('txbox', False)
        self.shape(x, y, w, h, paras, **kw)

    def text(self, x, y, w, h, paras, **kw):
        kw.setdefault('ins', (0, 0, 0, 0))
        self.shape(x, y, w, h, paras, **kw)

    # ---------------- drawing primitives (all native, editable)
    def line(self, x1, y1, x2, y2, color=WHITE, w=1.75, dash=None, head=False, tail=False, name='Line'):
        sid = self.id()
        fh, fv = x2 < x1, y2 < y1
        ox, oy = min(x1, x2), min(y1, y2)
        cx, cy = abs(x2 - x1), abs(y2 - y1)
        flip = (' flipH="1"' if fh else '') + (' flipV="1"' if fv else '')
        dashx = f'<a:prstDash val="{dash}"/>' if dash else ''
        he = '<a:tailEnd type="triangle" w="med" len="med"/>' if head else ''
        te = '<a:headEnd type="triangle" w="med" len="med"/>' if tail else ''
        xml = (f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{sid}" name="{name} {sid}"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr>'
               f'<p:spPr><a:xfrm{flip}><a:off x="{E(ox)}" y="{E(oy)}"/><a:ext cx="{E(cx)}" cy="{E(cy)}"/></a:xfrm>'
               f'<a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
               f'<a:ln w="{int(w*12700)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{dashx}{te}{he}</a:ln></p:spPr></p:cxnSp>')
        self.items.append(lambda mode, xml=xml: xml)

    def arrow(self, x1, y1, x2, y2, color=YEL, w=2.25, dash=None, name='Vector'):
        self.line(x1, y1, x2, y2, color=color, w=w, dash=dash, head=True, name=name)

    def poly(self, pts, fill=None, color=None, w=1.5, closed=True, alpha=None, dash=None, name='Freeform'):
        sid = self.id()
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        ox, oy = min(xs), min(ys)
        cw, ch = max(max(xs) - ox, 0.01), max(max(ys) - oy, 0.01)
        path = f'<a:moveTo><a:pt x="{E(pts[0][0]-ox)}" y="{E(pts[0][1]-oy)}"/></a:moveTo>'
        for p in pts[1:]:
            path += f'<a:lnTo><a:pt x="{E(p[0]-ox)}" y="{E(p[1]-oy)}"/></a:lnTo>'
        if closed:
            path += '<a:close/>'
        al = f'<a:alpha val="{int(alpha*1000)}"/>' if alpha is not None else ''
        fillx = f'<a:solidFill><a:srgbClr val="{fill}">{al}</a:srgbClr></a:solidFill>' if fill else '<a:noFill/>'
        dashx = f'<a:prstDash val="{dash}"/>' if dash else ''
        linex = (f'<a:ln w="{int(w*12700)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>{dashx}</a:ln>'
                 if color else '<a:ln><a:noFill/></a:ln>')
        xml = (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{name} {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
               f'<p:spPr><a:xfrm><a:off x="{E(ox)}" y="{E(oy)}"/><a:ext cx="{E(cw)}" cy="{E(ch)}"/></a:xfrm>'
               f'<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>'
               f'<a:pathLst><a:path w="{E(cw)}" h="{E(ch)}">{path}</a:path></a:pathLst></a:custGeom>'
               f'{fillx}{linex}</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="vi-VN"/></a:p></p:txBody></p:sp>')
        self.items.append(lambda mode, xml=xml: xml)

    def arc(self, cx, cy, r, a1, a2, color=YEL, w=1.5, n=24):
        """angles in degrees, math orientation (counter-clockwise, y up)"""
        pts = []
        for k in range(n + 1):
            a = pymath.radians(a1 + (a2 - a1) * k / n)
            pts.append((cx + r * pymath.cos(a), cy - r * pymath.sin(a)))
        self.poly(pts, color=color, w=w, closed=False, name='Arc')

    def dot(self, x, y, r=0.045, color=WHITE):
        sid = self.id()
        xml = (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Point {sid}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
               f'<p:spPr><a:xfrm><a:off x="{E(x-r)}" y="{E(y-r)}"/><a:ext cx="{E(2*r)}" cy="{E(2*r)}"/></a:xfrm>'
               f'<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
               f'<a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="vi-VN"/></a:p></p:txBody></p:sp>')
        self.items.append(lambda mode, xml=xml: xml)

    def label(self, x, y, s, sz=15, color=WHITE, w=0.6, h=0.34, b=False, align='ctr', italic=True):
        """centered at (x, y). s: plain text (italic) or '$math$' rich"""
        if '$' in s:
            runs = rich(s, color=color, sz=sz)
        else:
            runs = [T(s, i=italic, b=b, color=color, sz=sz)]
        self.text(x - w / 2, y - h / 2, w, h, [P(runs, align=align, sz=sz, after=0)], anchor='ctr', name='Label')

    # ---------------- assemble
    def xml(self, mode):
        self.pics = []
        body = ''.join(it(mode) for it in self.items)
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
                'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
                'xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main" '
                'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
                f'<p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="{BG}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
                '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
                '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
                f'{body}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')


def docx_xml(paras, w, h, anchor='t', k=1.0):
    body = ''.join(w_para(p, k) for p in paras)
    w, h = w * k, h * k
    va = '<w:vAlign w:val="center"/>' if anchor == 'ctr' else ''
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><w:body>'
            f'{body}<w:sectPr><w:pgSz w:w="{int(w*1440)}" w:h="{int(h*1440)}"/>'
            '<w:pgMar w:top="0" w:right="0" w:bottom="0" w:left="0" w:header="0" w:footer="0" w:gutter="0"/>'
            f'{va}</w:sectPr></w:body></w:document>')

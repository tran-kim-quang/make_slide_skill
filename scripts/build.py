# -*- coding: utf-8 -*-
"""Build an editable math deck (PPTX) from a content file, reusing the original deck's package
(theme, master, layouts, background) as template.

Usage:
  python build.py --src goc.pptx --content content.py --out bai_giang.pptx \
      [--work /home/claude/work] [--bg 0E3822] [--frame 1B5E3A] [--title "..."] \
      [--palette '{"CARD":"13462C","BORDER":"80DEEA"}'] [--grid]

Pipeline (in this order):
  1. QA render: every text box that contains math is exported to its own small DOCX (same OMML),
     rendered by LibreOffice Writer (needs libreoffice-math) to a transparent PNG.
     Boxes whose DOCX needs >1 page are reported as OVERFLOW (text does not fit).
  2. qa.pptx: same deck where math boxes are replaced by those PNGs -> render it to LOOK at layout.
  3. final .pptx: every math box = mc:AlternateContent
        Choice  (Requires="a14") -> real Office Math (OMML), editable in PowerPoint 2010+
        Fallback                 -> the shape + PNG picture of its text (for PowerPoint 2007,
                                    Google Slides, WPS, Keynote ... which cannot read OMML)
     This is exactly what PowerPoint itself writes when it saves equations.
  4. --grid: render final deck (as a non-Office viewer sees it) into contact sheets for review.
"""
import argparse, glob, importlib.util, json, os, re, shutil, subprocess, sys, zipfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PPTX_SKILL = '/mnt/skills/public/pptx/scripts'


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, **kw)


def load_content(path):
    sys.path.insert(0, HERE)
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    spec = importlib.util.spec_from_file_location('content', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def unpack(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    zipfile.ZipFile(src).extractall(dst)


def layout_of_first_slide(pkg):
    rels = open(f'{pkg}/ppt/slides/_rels/slide1.xml.rels', encoding='utf-8').read()
    m = re.search(r'Target="\.\./slideLayouts/(slideLayout\d+\.xml)"', rels)
    return m.group(1) if m else 'slideLayout7.xml'


def base_package(srcdir, dst, n, a):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(srcdir, dst)
    pres = open(f'{dst}/ppt/presentation.xml', encoding='utf-8').read()
    ids = re.findall(r'<p:sldId [^>]*/>', pres)
    if len(ids) < n:
        raise SystemExit(f'Bản gốc chỉ có {len(ids)} slide, content có {n} slide. '
                         'Hãy nhân bản thêm slide trong bản gốc (add_slide.py của skill pptx) hoặc giảm số slide.')
    pres = pres.replace(''.join(ids), ''.join(ids[:n]))
    open(f'{dst}/ppt/presentation.xml', 'w', encoding='utf-8').write(pres)
    m = f'{dst}/ppt/slideMasters/slideMaster1.xml'
    d = open(m, encoding='utf-8').read()
    if a.bg:
        bg = f'<p:bg><p:bgPr><a:solidFill><a:srgbClr val="{a.bg}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
        if '<p:bg>' in d:
            d = re.sub(r'<p:bg>.*?</p:bg>', bg, d, count=1, flags=re.S)
        else:
            d = re.sub(r'(<p:cSld[^>]*>)', lambda m_: m_.group(1) + bg, d, count=1)
    if a.frame and 'Board Frame' not in d:
        frame = ('<p:sp><p:nvSpPr><p:cNvPr id="900" name="Board Frame"/><p:cNvSpPr/><p:nvPr userDrawn="1"/></p:nvSpPr>'
                 '<p:spPr><a:xfrm><a:off x="365760" y="365760"/><a:ext cx="11460175" cy="6126480"/></a:xfrm>'
                 f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/><a:ln w="25400"><a:solidFill><a:srgbClr val="{a.frame}"/></a:solidFill></a:ln></p:spPr>'
                 '<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="vi-VN"/></a:p></p:txBody></p:sp>')
        d = d.replace('</p:spTree>', frame + '</p:spTree>', 1)
    open(m, 'w', encoding='utf-8').write(d)
    t = f'{dst}/ppt/theme/theme1.xml'
    d = open(t, encoding='utf-8').read()
    d = re.sub(r'(<a:majorFont><a:latin typeface=")[^"]*(")', r'\1Times New Roman\2', d)
    d = re.sub(r'(<a:minorFont><a:latin typeface=")[^"]*(")', r'\1Times New Roman\2', d)
    open(t, 'w', encoding='utf-8').write(d)
    core = f'{dst}/docProps/core.xml'
    if a.title and os.path.exists(core):
        d = open(core, encoding='utf-8').read()
        if '<dc:title>' in d:
            d = re.sub(r'<dc:title>.*?</dc:title>', f'<dc:title>{a.title}</dc:title>', d)
        open(core, 'w', encoding='utf-8').write(d)


def write_slides(content, dst, mode, layout, imgdir=None):
    for s in content.slides:
        xml = s.xml(mode)
        open(f'{dst}/ppt/slides/slide{s.idx}.xml', 'w', encoding='utf-8').write(xml)
        rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/{layout}"/>')
        for rid, fn in s.pics:
            os.makedirs(f'{dst}/ppt/media', exist_ok=True)
            shutil.copy(f'{imgdir}/{fn}', f'{dst}/ppt/media/{fn}')
            rels += f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{fn}"/>'
        rels += '</Relationships>'
        open(f'{dst}/ppt/slides/_rels/slide{s.idx}.xml.rels', 'w', encoding='utf-8').write(rels)
    if any(s.pics for s in content.slides):
        ct = f'{dst}/[Content_Types].xml'
        d = open(ct, encoding='utf-8').read()
        if 'Extension="png"' not in d:
            d = d.replace('<Default ', '<Default Extension="png" ContentType="image/png"/><Default ', 1)
        open(ct, 'w', encoding='utf-8').write(d)


def zipdir(d, out):
    out = os.path.abspath(out)
    if os.path.exists(out):
        os.remove(out)
    subprocess.run(f'cd "{d}" && zip -qXr "{out}" .', shell=True, check=True)


DOCX_CT = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
           '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
           '<Default Extension="xml" ContentType="application/xml"/>'
           '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
           '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
DOCX_RELS = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
DOC_RELS = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
STYLES = ('<?xml version="1.0" encoding="UTF-8"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
          '<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="24"/>'
          '</w:rPr></w:rPrDefault></w:docDefaults></w:styles>')


def render_math_boxes(content, jd):
    """Each math text box -> DOCX -> PDF -> transparent PNG. Returns overflow list."""
    from engine import docx_xml, M
    from PIL import Image
    if os.path.exists(jd):
        shutil.rmtree(jd)
    os.makedirs(jd)
    jobs = [j for s in content.slides for j in s.qa_jobs]
    for name, w, h, paras, anchor in jobs:
        cnt = Counter((r.sz or p.sz) for p in paras for r in p.runs if isinstance(r, M))
        msz = cnt.most_common(1)[0][0]
        # LibreOffice Math ignores font size from OMML and always draws at 12 pt: scale the whole page
        # so that 12 pt corresponds to the intended size (x1.12 = Cambria Math is wider -> conservative).
        k = 12.0 / (msz * 1.12)
        z = zipfile.ZipFile(f'{jd}/{name}.docx', 'w')
        z.writestr('[Content_Types].xml', DOCX_CT)
        z.writestr('_rels/.rels', DOCX_RELS)
        z.writestr('word/document.xml', docx_xml(paras, w, h, anchor, k))
        z.writestr('word/styles.xml', STYLES)
        z.writestr('word/_rels/document.xml.rels', DOC_RELS)
        z.close()
    files = sorted(glob.glob(f'{jd}/*.docx'))
    if files:
        sh([sys.executable, f'{PPTX_SKILL}/office/soffice.py', '--headless', '--convert-to', 'pdf', '--outdir', jd] + files)
    overflow = []
    for name, *_ in jobs:
        pdf = f'{jd}/{name}.pdf'
        info = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout
        pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
        if pages > 1:
            overflow.append((name, pages))
        sh(['pdftocairo', '-png', '-transp', '-r', '220', '-f', '1', '-l', '1', '-singlefile', pdf, f'{jd}/{name}'])
        im = Image.open(f'{jd}/{name}.png').convert('RGBA')
        px = im.load()
        for yy in range(im.size[1]):          # LibreOffice draws math black: recolor to light text
            for xx in range(im.size[0]):
                r_, g_, b_, a_ = px[xx, yy]
                if a_ and r_ < 140 and g_ < 140 and b_ < 140:
                    px[xx, yy] = (255, 255, 255, a_)
        im.save(f'{jd}/{name}.png')
    return overflow


def grid(pptx, outdir, per=6, dpi=55):
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(f'{outdir}/*'):
        os.remove(f)
    sh([sys.executable, f'{PPTX_SKILL}/office/soffice.py', '--headless', '--convert-to', 'pdf', '--outdir', outdir, pptx])
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(pptx))[0] + '.pdf')
    sh(['pdftoppm', '-jpeg', '-r', str(dpi), pdf, f'{outdir}/p'])
    from PIL import Image
    fs = sorted(glob.glob(f'{outdir}/p-*.jpg'))
    ims = [Image.open(f) for f in fs]
    w, h = ims[0].size
    outs = []
    for g in range(0, len(ims), per):
        sub = ims[g:g + per]
        o = Image.new('RGB', (w * 2 + 10, h * ((per + 1) // 2) + 10 * ((per + 1) // 2)), 'white')
        for k, im in enumerate(sub):
            o.paste(im, ((k % 2) * (w + 10), (k // 2) * (h + 10)))
        p = f'{outdir}/grid{g // per + 1}.jpg'
        o.save(p, quality=85)
        outs.append(p)
    return outs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True, help='file PPTX gốc (dùng làm template: theme, master, nền)')
    ap.add_argument('--content', required=True, help='file content.py định nghĩa danh sách slides')
    ap.add_argument('--out', required=True)
    ap.add_argument('--work', default='/home/claude/mathslide_work')
    ap.add_argument('--bg', default=None, help='màu nền đặc (hex) đặt vào master, vd 0E3822')
    ap.add_argument('--frame', default=None, help='màu khung viền bảng (hex) đặt vào master, vd 1B5E3A')
    ap.add_argument('--title', default=None)
    ap.add_argument('--palette', default=None, help='JSON ghi đè bảng màu engine')
    ap.add_argument('--grid', action='store_true', help='render deck cuối thành ảnh lưới để rà soát')
    a = ap.parse_args()
    if a.palette:
        os.environ['MATHSLIDE_PALETTE'] = a.palette
    content = load_content(a.content)
    os.makedirs(a.work, exist_ok=True)
    srcdir = f'{a.work}/src'
    unpack(a.src, srcdir)
    layout = layout_of_first_slide(srcdir)
    n = len(content.slides)
    jd = f'{a.work}/math_png'
    overflow = render_math_boxes(content, jd)
    qa_pkg = f'{a.work}/pkg_qa'
    base_package(srcdir, qa_pkg, n, a)
    write_slides(content, qa_pkg, 'qa', layout, imgdir=jd)
    zipdir(qa_pkg, f'{a.work}/qa.pptx')
    fin = f'{a.work}/pkg_final'
    base_package(srcdir, fin, n, a)
    write_slides(content, fin, 'final_img', layout, imgdir=jd)
    sh([sys.executable, f'{PPTX_SKILL}/clean.py', fin])
    zipdir(fin, a.out)
    print(json.dumps({'slides': n, 'overflow': overflow, 'out': a.out, 'qa': f'{a.work}/qa.pptx'}, ensure_ascii=False))
    if a.grid:
        print('GRIDS:', grid(a.out, f'{a.work}/grid'))


if __name__ == '__main__':
    main()

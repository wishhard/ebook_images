from lxml import html, etree
import re
import os
import uuid


def chaters_paths(chrs_html_filepath):
    ch_p = []

    if chrs_html_filepath.__contains__(".html") or chrs_html_filepath.__contains__(".xhtml"):
        root = html.parse(chrs_html_filepath)

        a_list = root.findall('.//a')

        for a in a_list:
            hrf = str(a.get('href'))

            if hrf.__contains__("#"):
                hrf = hrf[0:hrf.find("#"):]

            if re.search(".html$", hrf):
                ch_p.append(hrf)

    elif chrs_html_filepath.__contains__(".ncx"):

        with open(chrs_html_filepath) as cont:
            opf = cont.read()

        utf8_parser = etree.XMLParser(encoding='utf-8')
        root = etree.fromstring(opf.encode('utf-8'), parser=utf8_parser)
        comments = root.xpath('//comment()')
        for c in comments:
            p = c.getparent()
            p.remove(c)

        for elem in root.getiterator():
            elem.tag = etree.QName(elem).localname

        etree.cleanup_namespaces(root)

        for g in root.iter('content'):
            c = g.get('src')

            if c.__contains__("#"):
                c = c[0:c.find("#"):]

            if re.search(".html$", c):
                ch_p.append(os.path.basename(c))



    return ch_p


def getparsed_imagechr(chr_html_page_path):
    return html.parse(chr_html_page_path)


def getimagechr_title(chr_html_root):
    ch_t = None
    try:
        ch_t = str(chr_html_root.xpath('.//title')[0].text) + ' ' + str(chr_html_root.xpath('.//span')[0].text)
    except:
        ch_t = str(chr_html_root.xpath('.//title')[0].text) + ' ' + str(uuid.uuid4())[:5]

    ch_t = re.subn("[\[\]{}()!:/<>\\\\|\",.`*-]", "", ch_t)
    return ch_t[0]


def getimagechr_list(chr_html_root, til_dir):
    chr = []
    img_list = chr_html_root.findall('.//img')
    piece  = None
    for h in img_list:
        f = h.get('src')
        if os.path.exists(til_dir + f and piece is None):
            f = os.path.basename(f)
            piece = find(f, til_dir)
            til_dir = piece[0:piece.rfind("/") + 1:]

        chr.append(til_dir + "" + f)

    return chr


def chrs_containing_images_dict(til_dir, chr_html_filepath):
    full_path = find(chr_html_filepath, til_dir)
    chrs_list = chaters_paths(full_path)

    piece = find(chrs_list[0], til_dir)
    piece = piece[0:piece.rfind("/") + 1:]

    images_dict = {}
    for ch in chrs_list:

        rot = getparsed_imagechr(piece + ch)
        cont_images_list = getimagechr_list(rot, til_dir)
        if len(cont_images_list) > 0:
            images_dict[getimagechr_title(rot)] = cont_images_list

    return images_dict


def find(name, path):
    if name.__contains__("#"):
        name = name[0:name.find("#"):]

    if name.find("/") > 0:
        name = os.path.basename(name)

    for root, dirs, files in os.walk(path):
        if name in files:
            n = os.path.join(root, name)
            n = n.replace("\\", "/")
            return n

# print(h.findtext('a'))

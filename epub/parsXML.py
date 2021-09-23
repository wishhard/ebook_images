from lxml import etree
import re
import os

CONTENT_REGEX = ["unique-identifier=\".*?\"", "xmlns:opf=\".*?\"", "opf:scheme=\".*?\"",
                 "<dc:description>.*</dc:description>"]
IMAGE_FROMATS = ['jpeg', 'png', 'gif', 'webp', 'tiff', 'bmp', 'jfif']


def get_content_file_path(meta_inf_path):
    rot = etree.parse(meta_inf_path)
    for elem in rot.getiterator():
        elem.tag = etree.QName(elem).localname

    etree.cleanup_namespaces(rot)

    return "".join(rot.xpath("//rootfiles/rootfile/@full-path[1]"))


def content_file_prep(content_opf_path):
    with open(content_opf_path) as cont:
        opf = cont.read()

        for i in range(len(CONTENT_REGEX)):
            rex = re.findall(CONTENT_REGEX[i], opf)
            opf = opf.replace("".join(rex), "")

    root = etree.fromstring(opf)
    for elem in root.getiterator():
        elem.tag = etree.QName(elem).localname

    etree.cleanup_namespaces(root)
    return root


def getbooktitle(root):
    return "".join(root.xpath('/package[@version="2.0"]/metadata/title/text()'))


# print(etree.tostring(root).decode())
def get_image_paths(wrking_dir, root):
    image_paths = []
    count = int(root.xpath('count(/package[@version="2.0"]/manifest//item)'))

    d_list = give_full_path(wrking_dir)
    the_turth = ""

    for i in range(0, count):
        m_type = root.xpath('/package[@version="2.0"]/manifest//item/@media-type')[i]

        for p in range(len(IMAGE_FROMATS)):
            if m_type.__contains__(IMAGE_FROMATS[p]):

                if the_turth == "":
                    for t in d_list:

                        if os.path.exists(t + '/' + root.xpath('/package[@version="2.0"]/manifest//item/@href')[i]):
                            the_turth = t
                            break

                image_paths.append(the_turth + '/' + root.xpath('/package[@version="2.0"]/manifest//item/@href')[i])

    return image_paths


def getchapters_page_path(root):
    for g in root.iter('reference'):

        if g.get('type') == 'toc':
            return g.get('href')


def give_full_path(wrking_dir):
    d = [x[0] for x in os.walk(wrking_dir)]
    for s in range(len(d)):
        d[s] = d[s].replace("\\", "/")

    return d

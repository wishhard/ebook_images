from lxml import html
import re



def chaters_paths(chrs_html_filepath):
    root = html.parse(chrs_html_filepath)
    ch_p = []
    a_list = root.findall('.//a')
    for a in a_list:
        hrf = str(a.get('href'))
        if re.search(".html$", hrf):
            ch_p.append(hrf)

    return ch_p


def getparsed_imagechr(chr_html_page_path):
    return html.parse(chr_html_page_path)


def getimagechr_title(chr_html_root):
    ch_t = str(chr_html_root.xpath('.//title')[0].text) + ' ' + str(chr_html_root.xpath('.//span')[0].text)
    ch_t = re.subn("[\[\]{}()!:/<>\\\\|\",.`*-]", "", ch_t)
    return ch_t[0]


def getimagechr_list(chr_html_root, til_dir):
    chr = []
    img_list = chr_html_root.findall('.//img')
    for h in img_list:
        chr.append(til_dir+""+h.get('src'))

    return chr


def chrs_containing_images_dict(til_dir, chr_html_filepath):
    chrs_list = chaters_paths(til_dir + chr_html_filepath)

    images_dict = {}
    for ch in chrs_list:
        rot = getparsed_imagechr(til_dir + ch)
        cont_images_list = getimagechr_list(rot, til_dir)
        if len(cont_images_list) > 0:
            images_dict[getimagechr_title(rot)] = cont_images_list

    return images_dict



# print(h.findtext('a'))


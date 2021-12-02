import fitz
import io
from PIL import Image
import re


def getPdfBookTitle(path=None):
    x = re.split("/", path)
    txt = x[len(x) - 1]
    txt = txt[:txt.find('.'):]
    return txt


def ext_pdf_imgs(workin_dir=None, path=None):
    imgs_name = []
    pdf_file = path
    pdf_file = fitz.open(pdf_file)

    for page_no in range(len(pdf_file)):
        curr_page = pdf_file[page_no]
        images = curr_page.get_images()

        for image_no, image in enumerate(curr_page.get_images()):
            xref = image[0]
            curr_image = pdf_file.extract_image(xref)
            img_bytes = curr_image["image"]
            img_extension = curr_image["ext"]
            image = Image.open(io.BytesIO(img_bytes))
            imgs_name.append(f"{workin_dir}/page{page_no + 1}_img{image_no}.{img_extension}")
            image.save(open(f"{workin_dir}/page{page_no + 1}_img{image_no}.{img_extension}", "wb"))

    return imgs_name

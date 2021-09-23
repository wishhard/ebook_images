from PyQt5.QtGui import QFontDatabase, QFont
import re
import resources.fonts_resr


def make_font_db():

    families = []
    fontDB = QFontDatabase()
    f_id = fontDB.addApplicationFont(":/fonts/theboldfont.ttf")

    families.append(fontDB.applicationFontFamilies(f_id))

    for i in range(len(families)):
        s = re.sub("[\[\]']", "", str(families[i]))
        families[i] = s
    return families




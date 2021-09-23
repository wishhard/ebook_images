import ui.ui_res
from ui.aui import App_Ui
import ui.aui as aui
import ui.ui_res as ui_r
import os
from PyQt5 import QtWidgets as qtw

import sys

tempdir = os.getcwd().replace("\\", "/")
tempdir += "/temp"
if not os.path.exists(tempdir):
    os.mkdir(tempdir)
os.chdir(tempdir)

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    aui.font_famiies = ui_r.make_font_db()
    app.setStyleSheet(aui.stylesheet)
    scr_size = app.primaryScreen()
    au = App_Ui(tempdir)

    sys.exit(app.exec_())






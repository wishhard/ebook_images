from PyQt5.QtWidgets import QFileDialog, QLabel
from PyQt5.QtCore import Qt, QObject
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as gui

from zipfile import ZipFile
import os, shutil
from epub import parsXML, parsHTML
import uuid
from PIL import Image

import resources.imgs_resr

font_famiies = []

stylesheet = """
#Main { 
background-color: #302f2f;
}

#FPLineEdit[readOnly=true] {
background-color: #4f4848;
border: 0px;
color: gray;
}

#ChooseFileBtn {
background-color: #4f4848;
border: 0px;
color: white;
}

#loading {
background-color: rgba( 255, 255, 255, 40% );
}



#ChooseFileBtn:pressed {
background-color: white;
color: #4f4848;
}

#LogLV::item {
height: 20px;
color: #999999;
font-size: 10px;
background: transparent;
}

QListView {
background-color: #5e5959;
margin: -1px -1px -1px -1px;
}

QListView::item {
height: 50px;
}

#chr_btn {
padding: 0px;
}

QTabWidget::pane {
    margin: 0px 0px 0px 0px;
}

QTabBar::tab {
border-right: 1px solid #302f2f;
border-left: 1px solid #302f2f;
border-bottom: 1px solid #302f2f;
padding-left: 16px;
padding-right: 16px;
padding-top: 6px;
padding-bottom: 6px;
background-color: #5e5959;
color: grey;
}

QTabBar::tab:selected {
border: 0px;
color: white;
}

"""


class Communicate(QObject):
    sg = qtc.pyqtSignal(str)
    loading_screen = qtc.pyqtSignal(int)
    reading_ex = qtc.pyqtSignal()


class App_Ui(qtw.QWidget):
    c = Communicate()
    thread1 = None
    thread2 = None
    thread3 = None
    worker = None
    worker2 = None
    reset_all = None

    __working_dir = None
    __book_tile = None
    __chaptrs_wid_imgs = None
    __all_imgs = None

    def __init__(self, wd):
        super().__init__()

        self.__working_dir = wd

        self.setObjectName('Main')
        self.setFixedSize(600, 300)
        self.setWindowTitle('EBook Images v1.1')
        self.setWindowIcon(gui.QIcon(":imgs/ebi_icon.png"))

        self.FilePathLineEdit = qtw.QLineEdit(self)
        self.FilePathLineEdit.setObjectName("FPLineEdit")
        self.FilePathLineEdit.setReadOnly(True)
        self.FilePathLineEdit.setGeometry(qtc.QRect(30, 40, 410, 25))

        self.ChooseFileBtn = qtw.QPushButton(self)
        self.ChooseFileBtn.setGeometry(qtc.QRect(460, 40, 100, 25))
        self.ChooseFileBtn.setObjectName("ChooseFileBtn")
        self.ChooseFileBtn.setText('Choose File')
        self.ChooseFileBtn.clicked.connect(self.on_choose_file_clicked)

        self.tabs = theTabs(self)

        self.loading = Loading(self)

        self.c.loading_screen.connect(self.loading.show_hide_loading)

        self.c.sg.connect(self.save_images)

        self.show()

    def on_choose_file_clicked(self):
        inputfile_path = QFileDialog.getOpenFileName(self, 'Choose File', '/', "Epub (*.epub);;All Files (*)")

        if inputfile_path[0] == "":
            self.tabs.scrollLabel('No file selected')
        if inputfile_path[0] != "" and not inputfile_path[0].__contains__('.epub'):
            self.tabs.scrollLabel('The file ' + inputfile_path[0] + ' can not be processed')
        if inputfile_path[0] != "" and inputfile_path[0].__contains__('.epub'):
            try:
                self.worker = Worker(self, inputfile_path[0])

                self.thread1 = qtc.QThread()
                self.reset_all = ClearAllWorker(self)
                self.reset_all.moveToThread(self.thread1)
                self.thread1.started.connect(self.reset_all.run)
                self.reset_all.finished.connect(self.thread1.quit)
                self.reset_all.finished.connect(self.run_the_worker)
                self.thread1.finished.connect(self.thread1.deleteLater)
                self.thread1.start()

            except Exception as e:
                self.tabs.scrollLabel(str(e))

    def extract_epub_worker(self, path):

        with ZipFile(path, 'r') as zip:
            zip.extractall(path=self.__working_dir)

            # uncompress_size = sum((file.file_size for file in zip.infolist()))
            #
            # extracted_size = 0
            #
            # for file in zip.infolist():
            #     extracted_size += file.file_size
            # print(int(extracted_size * 100 / uncompress_size))
            # zip.extract(file)

        self.c.loading_screen.emit(0)

    def save_images(self, key):

        try:
            name = qtw.QFileDialog.getSaveFileName(self, 'Save Folder', self.__book_tile.upper() + " " + key.title(),
                                                   "Audio Files (*.)")
            if not name[0] == "" and not os.path.exists(name[0]):
                os.mkdir(name[0])

                self.thread3 = qtc.QThread()
                self.worker2 = Worker2(self, key, name[0])
                self.worker2.moveToThread(self.thread3)
                self.thread3.started.connect(self.worker2.run)
                self.worker2.finished.connect(self.thread3.quit)
                self.thread3.finished.connect(self.thread3.deleteLater)
                self.thread3.start()



        except Exception as e:
            print(str(e))

    def reading_extracted_file(self):
        self.tabs.scrollLabel('Done')

        if os.path.isfile(self.__working_dir + '/META-INF/container.xml'):
            cont_path = parsXML.get_content_file_path(self.__working_dir + '/META-INF/container.xml')
            root_cont_xml = parsXML.content_file_prep(cont_path)
            self.__book_tile = parsXML.getbooktitle(root_cont_xml)
            self.__all_imgs = pics_paths = parsXML.get_image_paths(self.__working_dir, root_cont_xml)
            pics_paths_len = len(pics_paths)
            self.tabs.scrollLabel('There are ' + str(pics_paths_len) + ' image(s) find')
            if pics_paths_len > 0:
                self.tabs.make_chrs_btn_list("All Images")
                chrs_page_path = parsXML.getchapters_page_path(root_cont_xml)
                self.__chaptrs_wid_imgs = parsHTML.chrs_containing_images_dict(self.__working_dir + '/OEBPS/',
                                                                               chrs_page_path)
                for k in self.__chaptrs_wid_imgs:
                    self.tabs.make_chrs_btn_list(k)
                    self.tabs.scrollLabel(k)
                    for v in self.__chaptrs_wid_imgs[k]:
                        self.tabs.scrollLabel("   " + v)

    def save_imgs(self, key, name):
        self.c.loading_screen.emit(1)
        if key == "All Images":
            for a in self.__all_imgs:
                image = Image.open(a)
                file_ext = a[(a.rfind(".")):]
                image.save(name + "/" + self.__book_tile + "_" + str(str(uuid.uuid4())[:6]) + file_ext,
                           quality=90)
        else:
            for a in self.__chaptrs_wid_imgs[key]:
                image = Image.open(a)
                file_ext = a[(a.rfind(".")):]
                temp_t = key.replace(" ", "_")
                image.save(name + "/" + temp_t + "_" + str(str(uuid.uuid4())[:6]) + file_ext,
                           quality=90)
        self.c.loading_screen.emit(0)
        os.startfile(name)

    def clear_temp(self):
        dir = os.listdir(self.__working_dir)
        if len(dir) != 0:
            for f in dir:
                f_p = os.path.join(self.__working_dir, f)
                try:
                    if os.path.isfile(f_p):
                        os.unlink(f_p)
                    elif os.path.isdir(f_p):
                        shutil.rmtree(f_p)
                except Exception as e:
                    print(str(e))

    def reset_all_vars(self):
        self.c.loading_screen.emit(1)
        self.__book_tile = None
        self.__chaptrs_wid_imgs = None
        self.__all_imgs = None

        self.FilePathLineEdit.setText('')

        self.clear_temp()
        self.tabs.logModel.clear()
        self.tabs.model.clear()

    def run_the_worker(self):
        self.tabs.scrollLabel('File ' + self.worker.path + ' is being extracted to ' + self.__working_dir)
        self.thread2 = qtc.QThread()
        self.worker.moveToThread(self.thread2)
        self.thread2.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread2.quit)
        self.worker.finished.connect(self.reading_extracted_file)
        self.thread2.finished.connect(self.thread2.deleteLater)
        self.thread2.start()


class theTabs(qtw.QWidget):

    def __init__(self, parent):
        super(qtw.QWidget, self).__init__(parent)
        self.resize(500, 220)
        self.move(20, 80)
        self.layout = qtw.QVBoxLayout(self)

        self.tabs = qtw.QTabWidget()
        self.tab1 = qtw.QWidget()
        self.tab2 = qtw.QWidget()

        self.tabs.addTab(self.tab1, " Logs")
        self.tabs.addTab(self.tab2, "Save Images")

        self.logListView = qtw.QListView()
        self.logListView.setObjectName("LogLV")

        self.tab1.layout = qtw.QVBoxLayout(self)
        self.tab1.layout.setContentsMargins(0, 0, 0, 0)
        self.tab1.layout.addWidget(self.logListView)
        self.tab1.setLayout(self.tab1.layout)

        self.logModel = gui.QStandardItemModel(self.logListView)
        self.logListView.setModel(self.logModel)

        self.listView = qtw.QListView()

        self.tab2.layout = qtw.QVBoxLayout(self)
        self.tab2.layout.setContentsMargins(0, 0, 0, 0)
        self.tab2.layout.addWidget(self.listView)
        self.tab2.setLayout(self.tab2.layout)

        self.model = gui.QStandardItemModel(self.listView)
        self.listView.setModel(self.model)

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def scrollLabel(self, mg):
        item = gui.QStandardItem(mg)
        item.setSelectable(False)
        self.logModel.appendRow(item)

    def make_chrs_btn_list(self, key_title):
        item = gui.QStandardItem('')
        self.model.appendRow(item)
        cw = CustomListItem()
        cw.setText(key_title)
        cw.setFont(gui.QFont("Times", 15))
        self.listView.setIndexWidget(item.index(), cw)
        cw.clicked.connect(cw.get_title)


class CustomListItem(qtw.QPushButton):

    def __init__(self, parent=None):
        super(CustomListItem, self).__init__(parent)
        self.setObjectName('chr_btn')

    def get_title(self, n):
        n = self.text()
        App_Ui.c.sg.emit(n)


class Loading(qtw.QWidget):

    def __init__(self, parent=None):
        super(Loading, self).__init__(parent)
        self.setFixedSize(parent.width(), parent.height())
        self.setAttribute(qtc.Qt.WA_StyledBackground)
        self.setObjectName('loading')
        self.hide()

        self.load_mg_label = QLabel(self)
        self.load_mg_label.move((self.width() - self.load_mg_label.width()) / 2.2,
                                (self.height() - self.load_mg_label.height()) / 1.5)
        self.load_mg_label.setObjectName('loading_label')

        self.load_mg_label.setFont(gui.QFont(font_famiies[0], 17))
        self.load_mg_label.setText('please wait')

        self.m_label = QLabel(self)
        self.m_label.setFixedSize(150, 150)

        self.m_label.move((self.width() - self.m_label.width()) / 2,
                          (self.height() - self.m_label.height()) / 3.2)

        self.movie = gui.QMovie(":imgs/1488.gif")
        self.m_label.setMovie(self.movie)

    def show_hide_loading(self, show):
        if show == 1:
            self.show()
            self.movie.start()
        else:
            self.movie.stop()
            self.hide()


class Worker(qtc.QObject):
    finished = qtc.pyqtSignal()

    def __init__(self, o, path):
        super().__init__()
        self.o = o
        self.path = path

    def run(self):
        self.o.extract_epub_worker(self.path)
        self.o.FilePathLineEdit.setText(self.path)
        self.finished.emit()


class Worker2(qtc.QObject):
    finished = qtc.pyqtSignal()

    def __init__(self, o, key, name):
        super().__init__()
        self.o = o
        self.key = key
        self.name = name

    def run(self):
        self.o.save_imgs(self.key, self.name)
        self.finished.emit()


class ClearAllWorker(qtc.QObject):
    finished = qtc.pyqtSignal()

    def __init__(self, o):
        super().__init__()
        self.o = o

    def run(self):
        self.o.reset_all_vars()
        self.finished.emit()

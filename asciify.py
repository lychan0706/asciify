"""
알려진 버그:
1. 정상적으로 변환 후 잘못된 파일을 변환 시도하면 가장 마지막으로 변환한 txt파일을 반환함
sol: dropEvent에서 이미지를 grayscale로 변환하면 변환에 적합한 파일인지 바로 알 수 있으며, 변환에 부적합할시 config btn을 비활성화
해결 완료
"""

import time
import os
import subprocess
from PyQt5.QtGui import QDragEnterEvent
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QCheckBox, QSpinBox, QComboBox, QFileDialog, QFrame
from PyQt5.QtGui import QPixmap
import asciify_methods

class mainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.path_img : str # 사용자 지정 이미지의 절대경로
        self.path_dl : str # .txt 파일을 다운로드할 경로, 기본값은 현재 파일 위치
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("asciify - 아스키파이")
        self.setGeometry(100, 50, 400, 200)
        self.setAcceptDrops(True) # 드랍 허용 

        # show image path and pixmap 
        self.lbl_path_img = QLabel("이미지 파일을 끌어 프로그램 위에 드랍하십시오.\n")

        self.btn_find_img = QPushButton("혹은 직접 찾기")
        self.btn_find_img.clicked.connect(self.find_img)

        self.lbl_img = QLabel()
        self.lbl_img.resize(400,300)
        
        self.lbl_imgSize = QLabel()

        # newWidth spinbox
        newWidth_default = 200
        self.newWidth = newWidth_default
        
        self.lbl_newWidth = QLabel(f"Width - 가로 픽셀 수 (권장: 100 ~ 300)")

        self.sb_newWidth = QSpinBox()
        self.sb_newWidth.setEnabled(False)
        self.sb_newWidth.setRange(0, 2000)
        self.sb_newWidth.setSingleStep(1)
        self.sb_newWidth.setValue(newWidth_default)
        self.sb_newWidth.valueChanged.connect(self.updateWidth)

        # newWidth fix checkbox
        self.fix_width = False

        self.cb_widthFix = QCheckBox("사용자 지정 크기")
        self.cb_widthFix.setEnabled(False)
        self.cb_widthFix.setChecked(True)
        self.cb_widthFix.stateChanged.connect(self.updateWidth)

        # contrast spinbox
        contrast_default = 1
        self.contrast = contrast_default

        self.lbl_contrast = QLabel(f"Contrast - 명암대비 (권장: 1 ~ 2, 높을수록 명암 대비가 뚜렷함)")
        
        self.sb_contrast = QSpinBox()
        self.sb_contrast.setEnabled(False)
        self.sb_contrast.setRange(0, 10)
        self.sb_contrast.setSingleStep(1)        
        self.sb_contrast.setValue(contrast_default)
        self.sb_contrast.valueChanged.connect(self.updateContrast)

        # reverse checkbox
        self.reverse = False

        self.cb_reverse = QCheckBox("Reverse - 명암 반전")
        self.cb_reverse.setEnabled(False)
        self.cb_reverse.stateChanged.connect(self.updateReverse)

        #ascii character list combobox
        self.lbl_ACL = QLabel("사용할 ASCII CODE의 갯수\n(많을 수록 부드럽지만 이미지가 뭉개질 수 있음.)")

        self.cmb_ACL = QComboBox()
        self.cmb_ACL.setEnabled(False)
        self.cmb_ACL.addItem("3개")
        self.cmb_ACL.addItem("10개 (권장)")
        self.cmb_ACL.addItem("70개")
        self.cmb_ACL.addItem("91개")
        self.cmb_ACL.currentIndexChanged.connect(self.updateACL)
        self.cmb_ACL.setCurrentIndex(1)

        # select file dir filedialog
        self.cb_auto_dl = QCheckBox("현재 위치에 다운로드")
        self.cb_auto_dl.setChecked(True)
        self.path_dl = os.getcwd()
        self.path_dl_custom = os.getcwd()
        self.cb_auto_dl.stateChanged.connect(self.switch_auto_dl)

        self.lbl_fd_dl = QLabel("파일을 다운로드할 위치를 지정")

        self.btn_openDlFolder = QPushButton("Open Folder")
        self.btn_openDlFolder.setEnabled(False)
        self.btn_openDlFolder.clicked.connect(self.updatePath_dl)

        # convert and download button
        self.btn_convert = QPushButton("Convert and &Download")
        self.btn_convert.setEnabled(False)
        self.btn_convert.clicked.connect(self.convert)
        
        #status label
        self.lbl_status = QLabel()

        # openFile button
        self.convert_successful = False
        self.btn_openFile = QPushButton("&Open File")
        self.btn_openFile.setEnabled(False)
        self.btn_openFile.clicked.connect(self.openFile)

        # convert and open button
        self.btn_CnO = QPushButton("&Convert and Open")
        self.btn_CnO.setEnabled(False)
        self.btn_CnO.clicked.connect(self.convert)
        self.btn_CnO.clicked.connect(self.openFile)
        
        #layout
        lay_main = QVBoxLayout()

        lay_config = QVBoxLayout()
        lay_img = QVBoxLayout()
        lay_img_temp = QHBoxLayout()
        lay_img_temp.addWidget(self.lbl_path_img)
        lay_img_temp.addWidget(self.btn_find_img)
        lay_img.addLayout(lay_img_temp)
        lay_img.addWidget(self.lbl_img)
        lay_img.addStretch(1)
        lay_img.addWidget(self.lbl_imgSize)
        frm_img = QFrame()
        frm_img.setLineWidth(1)
        frm_img.setMidLineWidth(1)
        frm_img.setFrameShape(QFrame.Box | QFrame.Raised)
        frm_img.setLayout(lay_img)

        lay_width = QVBoxLayout()
        lay_width_temp = QHBoxLayout()
        lay_width_temp.addWidget(self.lbl_newWidth)
        lay_width_temp.addWidget(self.sb_newWidth)
        lay_width.addLayout(lay_width_temp)
        lay_width.addWidget(self.cb_widthFix)
        frm_width = QFrame()
        frm_width.setLineWidth(1)
        frm_width.setFrameShape(QFrame.Panel | QFrame.Sunken)
        frm_width.setLayout(lay_width)

        lay_cont = QVBoxLayout()
        lay_cont_temp = QHBoxLayout()
        lay_cont_temp.addWidget(self.lbl_contrast)
        lay_cont_temp.addWidget(self.sb_contrast)
        lay_cont.addLayout(lay_cont_temp)
        lay_cont.addWidget(self.cb_reverse)
        frm_cont = QFrame()
        frm_cont.setLineWidth(1)
        frm_cont.setFrameShape(QFrame.Panel | QFrame.Sunken)
        frm_cont.setLayout(lay_cont)

        lay_ACL = QHBoxLayout()
        lay_ACL.addWidget(self.lbl_ACL)
        lay_ACL.addWidget(self.cmb_ACL)
        frm_ACL = QFrame()
        frm_ACL.setLineWidth(1)
        frm_ACL.setFrameShape(QFrame.Panel | QFrame.Sunken)
        frm_ACL.setLayout(lay_ACL)

        lay_dl = QVBoxLayout()
        lay_dl_temp = QHBoxLayout()
        lay_dl.addWidget(self.cb_auto_dl)
        lay_dl_temp.addWidget(self.lbl_fd_dl)
        lay_dl_temp.addWidget(self.btn_openDlFolder)
        lay_dl.addLayout(lay_dl_temp)
        lay_dl.addWidget(self.lbl_status)
        frm_dl = QFrame()
        frm_dl.setLineWidth(1)
        frm_dl.setFrameShape(QFrame.Panel | QFrame.Sunken)
        frm_dl.setLayout(lay_dl)

        lay_btns = QVBoxLayout()
        lay_btns.addStretch(1)
        lay_temp = QHBoxLayout()
        lay_temp.addStretch(1)
        lay_temp.addWidget(self.btn_convert)
        lay_temp.addWidget(self.btn_openFile)
        lay_temp.addWidget(self.btn_CnO)
        lay_btns.addLayout(lay_temp)

        lay_main.addWidget(frm_img)
        lay_config.addWidget(QLabel(""))
        lay_config.addWidget(frm_width)
        lay_config.addWidget(QLabel(""))
        lay_config.addWidget(frm_cont)
        lay_config.addWidget(QLabel(""))
        lay_config.addWidget(frm_ACL)
        lay_config.addWidget(QLabel(""))
        lay_config.addWidget(frm_dl)
        lay_main.addLayout(lay_config)
        lay_main.addWidget(QLabel(""))
        lay_main.addLayout(lay_btns)

        self.setLayout(lay_main)

        self.show()

    def updateACL(self):
        self.index_ACL = self.cmb_ACL.currentIndex()
        self.sb_contrast.setValue(self.index_ACL)

    def setlbl_fd_dl(self, text: str):
        if len(text) > 35:
            text = "..." + text[len(text) - 35:]
        self.lbl_fd_dl.setText(text)

    def switch_auto_dl(self):
        self.auto_dl = self.cb_auto_dl.isChecked()
        if self.auto_dl:
            self.btn_openDlFolder.setEnabled(False)
            self.path_dl = os.getcwd()
        else:
            self.btn_openDlFolder.setEnabled(True)
            self.path_dl = self.path_dl_custom
        self.setlbl_fd_dl(self.path_dl)

    def updatePath_dl(self):
        self.path_dl_custom = QFileDialog.getExistingDirectory(self, "폴더 선택", "")
        self.path_dl = self.path_dl_custom
        self.setlbl_fd_dl(self.path_dl)

    def openFile(self):
        if self.convert_successful:
            path_file = f'{self.path_dl}\\\"{self.image_name}\"'
            subprocess.Popen(path_file, shell = True)

    def updateSampleImg(self, path_img):
        pm_img = QPixmap(path_img)
        self.img_width = pm_img.width()
        self.img_height = pm_img.height()
        maxw, maxh = (400, 300)
        if self.img_width > (maxw/maxh) * self.img_height:
            pm_img = pm_img.scaledToWidth(maxw)
        else:
            pm_img = pm_img.scaledToHeight(maxh)
        self.lbl_img.setPixmap(pm_img)
        self.lbl_imgSize.setText(f"Width : {self.img_width}px, Height : {self.img_height}px")

    def convert(self):
        if self.path_dl == "":
            self.lbl_fd_dl.setText("경로를 입력해주십시오.")
            self.convert_successful = False
            return None
        ACL_list = [[' ','=','@'],
                    [' ','.',':','-','=','+','*','#','%','@'],
                    [' ', '.', "'", '`', '^', '"', ',', ':', ';', 'I', 'l', '!', 'i', '>', '<', '~', '+', '_', '-', '?', ']', '[', '}', '{', '1', ')', '(', '|', '\\', '/', 't', 'f', 'j', 'r', 'x', 'n', 'u', 'v', 'c', 'z', 'X', 'Y', 'U', 'J', 'C', 'L', 'Q', '0', 'O', 'Z', 'm', 'w', 'q', 'p', 'd', 'b', 'k', 'h', 'a', 'o', '*', '#', 'M', 'W', '&', '8', '%', 'B', '@', '$'],
                    ['`', '.', '-', "'", ':', '_', ',', '^', '=', ';', '>', '<', '+', '!', 'r', 'c', '*', '/', 'z', '?', 's', 'L', 'T', 'v', ')', 'J', '7', '(', '|', 'F', 'i', '{', 'C', '}', 'f', 'I', '3', '1', 't', 'l', 'u', '[', 'n', 'e', 'o', 'Z', '5', 'Y', 'x', 'j', 'y', 'a', ']', '2', 'E', 'S', 'w', 'q', 'k', 'P', '6', 'h', '9', 'd', '4', 'V', 'p', 'O', 'G', 'b', 'U', 'A', 'K', 'X', 'H', 'm', '8', 'R', 'D', '#', '$', 'B', 'g', '0', 'M', 'N', 'W', 'Q', '%', '&', '@']
                   ]
        self.ascii_char_list = ACL_list[self.index_ACL]
        try:
            st = time.perf_counter()
            screen = asciify_methods.convertImageToAsciiArt(path_img = self.path_img, newWidth = self.newWidth,contrast_factor = self.contrast, reverse = self.reverse, ascii_char_list = self.ascii_char_list)
        except TypeError:
            self.path_img = ""
            self.lbl_path_img.setText("이미지를 읽는데 실패했습니다.\n경로에 한글이 있는지 확인해주십시오.")
            self.convert_successful = False
        else:
            self.image_name = self.path_img.split("/")[-1].rsplit(".", maxsplit = 1)[0]
            self.image_name = screen.createTextFile(file_name = self.image_name, path_dl = self.path_dl)
            #self.image_name = screen.createTextFile(file_name = self.image_name)
            et = time.perf_counter()
            self.lbl_status.setText(f'Image saved at {self.path_dl}, \nas {self.image_name}, time elapsed: {round(et - st, 3)}s.')
            self.btn_openFile.setEnabled(True)
            self.convert_successful = True

    def updateContrast(self):
        self.contrast = int(self.sb_contrast.value())
        self.lbl_contrast.setText(f"Contrast: {self.contrast}")

    def updateWidth(self):
        fix = not self.cb_widthFix.isChecked()
        if fix:
            self.sb_newWidth.setEnabled(False)
            self.newWidth = self.img_width
        else:
            self.sb_newWidth.setEnabled(True)
            self.newWidth = int(self.sb_newWidth.value())
        self.lbl_newWidth.setText(f"Width: {self.newWidth}")

    def updateReverse(self):
        self.reverse = self.cb_reverse.isChecked()
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event) -> None:
        self.path_img = event.mimeData().urls()[0].toLocalFile()
        self.update_img_path()
        self.updateSampleImg(self.path_img)

    def find_img(self):
        self.path_img = QFileDialog.getOpenFileName(self, "이미지 파일 선택", "", "All Files (*.*)")[0]
        self.update_img_path()
        self.updateSampleImg(self.path_img)

    def update_img_path(self):
        if len(self.path_img) > 55:
            text = "..." + self.path_img[len(self.path_img) - 55:]
        else:
            text = self.path_img
        self.lbl_path_img.setText(text)
        self.sb_contrast.setEnabled(True)
        self.sb_newWidth.setEnabled(True)
        self.cb_reverse.setEnabled(True)
        self.cb_widthFix.setEnabled(True)
        self.btn_convert.setEnabled(True)
        self.btn_CnO.setEnabled(True)
        self.cmb_ACL.setEnabled(True)

if __name__ == "__main__":
    app = QApplication([])
    myapp = mainApp()
    app.exec_()
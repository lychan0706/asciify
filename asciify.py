import sys
from PyQt5.QtGui import QDragEnterEvent, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QCheckBox, QSpinBox
import asciify_methods

class mainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.path = ""
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("asciify - 아스키파이")
        self.setGeometry(500,300,500,300)
        self.setAcceptDrops(True)

        #layout
        layout = QVBoxLayout()

        #label
        self.explanation = QLabel("이미지 파일을 끌어 프로그램 위에 드랍하십시오.\n")
        self.path_label = QLabel(self.path, self)
        self.scale_label = QLabel("Width - 가로 픽셀 수 (권장: 100 ~ 300)", self)
        self.contrast_label = QLabel("Contrast - 명암대비 (권장: 1 ~ 2)", self)
        self.completed_label = QLabel("")

        #buttons
        self.scaleDspinbox = QSpinBox()
        self.scaleDspinbox.setRange(0, 2000)
        self.scaleDspinbox.setSingleStep(1)
        self.newxRes = 200
        self.scaleDspinbox.valueChanged.connect(self.scaleUpdate)

        self.contDspinbox = QSpinBox()
        self.contDspinbox.setRange(0, 10)
        self.contDspinbox.setSingleStep(1)
        self.contrast_factor = 1
        self.contDspinbox.valueChanged.connect(self.contUpdate)

        self.reverseCheckbox = QCheckBox("Reverse", self)
        self.reverse = False
        self.reverseCheckbox.stateChanged.connect(self.reverseUpdate)

        self.convertBtn = QPushButton("&Convert", self)
        self.convertBtn.setEnabled(False)
        self.convertBtn.clicked.connect(self.startConv)

        #layout
        layout.addWidget(self.explanation)
        layout.addWidget(self.path_label)
        layout.addWidget(self.reverseCheckbox)
        layout.addWidget(self.contrast_label)
        layout.addWidget(self.contDspinbox)
        layout.addWidget(self.scale_label)
        layout.addWidget(self.scaleDspinbox)
        layout.addWidget(self.convertBtn)
        layout.addWidget(self.completed_label)
        self.setLayout(layout)

        self.show()

    def startConv(self):
        try:
            screen = asciify_methods.convertImageToAsciiArt(path = self.path, newxRes = self.newxRes,contrast_factor = self.contrast_factor, reverse = self.reverse, ascii_char_list = [' ','.',':','-','=','+','*','#','%','@'])
        except TypeError:
            self.path = ""
            self.path_label.setText("이미지를 읽는데 실패했습니다.\n경로에 한글이 있는지 확인해주십시오.")
        else:
            image_name = self.path.split("/")[-1].rsplit(".", maxsplit = 1)[0]
            image_name = screen.createTextFile(f"{image_name}")
            self.completed_label.setText(f"Image is saved as {image_name}")

    def contUpdate(self):
        self.contrast_factor = int(self.contDspinbox.value())
        self.contrast_label.setText(f"Contrast: {self.contrast_factor}")

    def scaleUpdate(self):
        self.newxRes = int(self.scaleDspinbox.value())
        self.scale_label.setText(f"Width: {self.newxRes}")
    
    def reverseUpdate(self):
        self.reverse = self.reverseCheckbox.isChecked()
    
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        self.path = event.mimeData().urls()[0].toLocalFile()
        self.path_label.setText(self.path)
        self.convertBtn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication([])
    myapp = mainApp()
    app.exec_()
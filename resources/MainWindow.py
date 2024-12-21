from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QStyleFactory, QComboBox, QGroupBox, QRadioButton, QCheckBox
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QWidget
from PyQt6 import QtGui
from PyQt6 import uic

import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.setWindowTitle("LIC Manager")
        # self.setWindowIcon(QtGui.QIcon("..\\resources\\LIC-Logo.png"))
        self.ui = uic.loadUi("untitled.ui", self)

        # button = QPushButton("Close.")
        self.ui.testbutton.pressed.connect(self.close)
        #
        # self.setCentralWidget(button)

        # QApplication.setStyle(QStyleFactory.create("Windows"))
        # styleComboBox = QComboBox()
        # styleComboBox.addItems(QStyleFactory.keys())
        # # self.addWidget(styleComboBox)
        #
        # self.originalPalette = QApplication.palette()
        # QApplication.setPalette(self.originalPalette)

        # self.widget = QWidget(self)
        # self.widget.setLayout(self.create_app_layout())
        # self.setCentralWidget(self.widget)
        self.show()

    def create_app_layout(self):
        btn_add_policy = QPushButton("Add Policy")
        btn_add_policy.setGeometry(200, 100, 100, 40)
        btn_add_policy.setStyleSheet("QPushButton"
                                     "{"
                                     "background-color : lightblue;"
                                     "}"
                                     "QPushButton::pressed"
                                     "{"
                                     "background-color : yellow;"
                                     "}"
                                     )

        btn_search_policy = QPushButton("Search Policy")
        btn_search_policy.setStyleSheet("background-color : lightblue")

        btn_premium = QPushButton("Premium Due")
        btn_premium.setStyleSheet("background-color : lightblue")


        topLayout = QHBoxLayout()
        topLayout.addWidget(btn_add_policy)
        topLayout.addWidget(btn_search_policy)
        topLayout.addWidget(btn_premium)


        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0)


        return mainLayout


def test():
    print('test pressed')


if __name__ == "__main__":
    # ui = None
    # ui = uic.loadUi("untitled.ui")
    # app = QApplication([])
    # window = Window()
    # form = Form()
    # ui.testbutton.pressed.connect(test())
    # form.setupUi(window)
    # window.show()
    # app.exec()
    app = QApplication(sys.argv)
    # w = MainWindow()
    # w.resize(800, 600)
    sys.exit(app.exec())


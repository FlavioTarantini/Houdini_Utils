import os
import sys
import json

from PySide2 import QtWidgets, QtGui, QtCore

from pyqtUtils import *

with open("themes.json", "r") as th:
    COLOR_PALETTE = json.load(th)["DEFAULT"]
_text_color = QtGui.QColor(COLOR_PALETTE["additional-color"])
_text_color.setAlpha(125)
DISABLED_TEXT_COLOR = _text_color.getRgb()


class AssetProcessingApp(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.resize(900, 500)
        self.setStyleSheet(f"""
                                background-color: {COLOR_PALETTE["app-color"]};
                                color: {COLOR_PALETTE["light-color"]};
                           """)
        
        self.setWindowTitle("Zip Extractor")
        self.setAcceptDrops(True)
        
        # Setting main layout
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.setLayout(self.main_layout)

        # Splitting main application 
        core_frame = QtWidgets.QFrame(self)
        core_frame.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        core_frame_layout = QtWidgets.QHBoxLayout()
        core_frame_layout.setContentsMargins(10,10,10,10)
        core_frame_layout.setSpacing(5)
        core_frame.setLayout(core_frame_layout)

        log_frame = QtWidgets.QFrame(self)
        log_frame.setMinimumHeight(20)
        log_frame.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        log_frame.setStyleSheet(f"""
                                    background-color: {COLOR_PALETTE["secondary-color"]};
                                """)
        log_frame_layout = QtWidgets.QHBoxLayout()
        log_frame_layout.setContentsMargins(0,0,0,0)
        log_frame_layout.setSpacing(0)
        log_frame.setLayout(log_frame_layout)

        self.main_layout.addWidget(core_frame)
        self.main_layout.addWidget(log_frame)

        # Setting core app frames
        folder_frame = QtWidgets.QFrame(self)
        folder_frame_layout = QtWidgets.QGridLayout()
        folder_frame_layout.setContentsMargins(0,0,0,0)
        folder_frame_layout.setSpacing(0)
        folder_frame.setLayout(folder_frame_layout)

        zip_frame = QtWidgets.QFrame(self)
        zip_frame.setMaximumWidth(350)
        zip_frame_layout = QtWidgets.QGridLayout()
        zip_frame_layout.setContentsMargins(0,0,0,0)
        zip_frame_layout.setSpacing(0)
        zip_frame.setLayout(zip_frame_layout)

        core_separator = QtWidgets.QFrame(self)
        core_separator.setFrameShape(QtWidgets.QFrame.VLine)
        core_separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        core_separator.setLineWidth(1)

        core_frame_layout.addWidget(zip_frame)
        core_frame_layout.addWidget(core_separator)
        core_frame_layout.addWidget(folder_frame)

        # Populating folder frame
        self.open_destination_btn = QtWidgets.QPushButton("Open Folder")
        self.open_destination_btn.clicked.connect(self.selectDestFolder)
        self.open_destination_btn.setStyleSheet(f"""
                                                    QPushButton {{
                                                        background-color: {COLOR_PALETTE["app-color"]};
                                                        border: 2px solid;
                                                        border-color: {COLOR_PALETTE["secondary-color"]};
                                                        padding: 6px;
                                                        text-align: center;
                                                        text-decoration: none;
                                                        border-radius: 4px;
                                                    }}
                                                    QPushButton:hover {{
                                                        background-color: {COLOR_PALETTE["secondary-color"]};
                                                    }}
                                                    QPushButton:pressed {{
                                                        background-color: {COLOR_PALETTE["app-color"]};
                                                    }}
                                                """)
        self.destination_label = ElideLabel("Path to Folder")
        self.destination_label.setStyleSheet(f"""
                                                margin-left: 10px;
                                                color: rgba{DISABLED_TEXT_COLOR};
                                            """)
        self.explorer_treeview_frame = QtWidgets.QFrame(self)
        self.explorer_treeview_frame.setLayout(QtWidgets.QVBoxLayout())
        self.empty_treeView_container_info = ElideLabel("Select OS Folder...")
        self.empty_treeView_container_info.setAlignment(QtCore.Qt.AlignCenter)
        self.empty_treeView_container_info.setStyleSheet(f"""
                                                            color: rgba{DISABLED_TEXT_COLOR};
                                                        """)
        self.explorer_treeview_frame.layout().addWidget(self.empty_treeView_container_info)
        bottom_spacer = QtWidgets.QFrame(self)
        bottom_spacer.setMaximumHeight(35)

        folder_frame_layout.addWidget(self.open_destination_btn, 0, 0)
        folder_frame_layout.addWidget(self.destination_label, 0, 1)
        folder_frame_layout.addWidget(self.explorer_treeview_frame, 1, 0, 1, 2)
        folder_frame_layout.addWidget(bottom_spacer, 2, 0, 1, 2)

        # Populating zip frame
        self.addzip_btn = QtWidgets.QPushButton("+ ZIP")
        self.addzip_btn.clicked.connect(self.addZipFolder)
        self.addzip_btn.setStyleSheet(f"""
                                        QPushButton {{
                                            background-color: {COLOR_PALETTE["app-color"]};
                                            border: 2px solid;
                                            border-color: {COLOR_PALETTE["secondary-color"]};
                                            padding: 6px;
                                            text-align: center;
                                            text-decoration: none;
                                            border-radius: 4px;
                                        }}
                                        QPushButton:hover {{
                                            background-color: {COLOR_PALETTE["secondary-color"]};
                                        }}
                                        QPushButton:pressed {{
                                            background-color: {COLOR_PALETTE["app-color"]};
                                        }}
                                    """)
        self.zip_tabwidget = QtWidgets.QTabWidget(self)
        self.zip_tabwidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.zip_tabwidget.setDocumentMode(True)
        self.zip_tabwidget.setStyleSheet(f"""
                                            
                                            QTabBar::tab {{
                                                            background-color: {COLOR_PALETTE["additional-color"]};
                                                            color: {COLOR_PALETTE["app-color"]};
                                                            padding: 8px;
                                                            border-top-left-radius: 4px;
                                                            border-top-right-radius: 4px;
                                                        }}

                                            QTabBar::tab:selected {{
                                                            background-color: {COLOR_PALETTE["secondary-color"]};
                                                            color: {COLOR_PALETTE["light-color"]};
                                                        }}

                                            QTabBar::tab:first {{
                                                            width: 0px;
                                                            padding: 0px;
                                                        }}
                                        """)

        # Set a starting tab
        starting_tab = QtWidgets.QLabel("Select a zip folder to start")
        starting_tab.setAlignment(QtCore.Qt.AlignCenter)
        starting_tab.setStyleSheet(f"""
                                        color: rgba{DISABLED_TEXT_COLOR};
                                    """)

        self.zip_tabwidget.addTab(starting_tab, "")

        self.extract_all_btn = QtWidgets.QPushButton("Extract All")
        self.extract_all_btn.setEnabled(False)
        self.extract_all_btn.clicked.connect(self.remove_tab)
        self.extract_all_btn.setFixedWidth(80)
        self.extract_all_btn.setStyleSheet(f"""
                                        QPushButton {{
                                            background-color: {COLOR_PALETTE["app-color"]};
                                            border: 2px solid;
                                            border-color: {COLOR_PALETTE["secondary-color"]};
                                            padding: 6px;
                                            text-align: center;
                                            text-decoration: none;
                                            border-radius: 4px;
                                            margin: 5px;
                                        }}
                                        QPushButton:hover {{
                                            background-color: {COLOR_PALETTE["secondary-color"]};
                                        }}
                                        QPushButton:pressed {{
                                            background-color: {COLOR_PALETTE["app-color"]};
                                        }}

                                        QPushButton:disabled {{
                                            color: rgba{DISABLED_TEXT_COLOR};
                                        }}
                                    """)
        self.zip_tabwidget.setCornerWidget(self.addzip_btn, QtCore.Qt.Corner.TopRightCorner)

        horizontal_spacer = QtWidgets.QSpacerItem(500, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        zip_frame_layout.addWidget(self.zip_tabwidget, 0, 0, 2, 0)
        zip_frame_layout.addItem(horizontal_spacer, 1, 1)
        zip_frame_layout.addWidget(self.extract_all_btn, 2, 2)

        # Populating log frame
        log_label = QtWidgets.QLabel("Log:")
        log_label.setStyleSheet(f"""
                                    color: {COLOR_PALETTE["app-color"]};
                                    padding: 5px;
                                """)
        self.log_message = ElideLabel()
        self.log_message.setElideMode(QtCore.Qt.ElideRight)
        self.log_message.setStyleSheet(f"""
                                                margin-left: 5px;
                                                color: rgba{DISABLED_TEXT_COLOR};
                                            """)

        log_frame_layout.addWidget(log_label)
        log_frame_layout.addWidget(self.log_message)

        self.msg_timer = QtCore.QTimer()
        self.msg_timer.setSingleShot(True)
        self.msg_timer.setTimerType(QtCore.Qt.PreciseTimer)
        

    def setLogMessage(self, text):
        self.log_message.setText(text)
        self.msg_timer.timeout.connect(lambda: self.log_message.setText(" "))
        self.msg_timer.start(8000)
        

    def addZipFolder(self):
        if (self.zip_tabwidget.count() <= 5):
            dialog = QtWidgets.QFileDialog(self)
            dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
            fileName = dialog.getOpenFileNames(self, "Open Zip File", "", "Zip Files (*.zip)")[0]
            
            for zippath in fileName:
                if os.path.exists(zippath):
                    # Add new zip tab
                    self.zip_treeview = zipTreeWidget(self, zippath)
                    self.zip_tabwidget.addTab(self.zip_treeview, "Zip")

                    index = self.zip_tabwidget.indexOf(self.zip_treeview)
                    self.zip_tabwidget.setCurrentIndex(index)
            
            zip_name = [os.path.basename(zippath) for zippath in fileName]
            self.setLogMessage(f"Zip Added: {', '.join(zip_name)}")
        else:
            msg_box = QtWidgets.QMessageBox()
            msg_box.setStyleSheet(f"""
                                QMessageBox {{
                                            background-color: {COLOR_PALETTE["secondary-color"]};
                                            color: {COLOR_PALETTE["light-color"]};
                                        }}
                                QPushButton {{
                                            background-color: {COLOR_PALETTE["app-color"]};
                                            border: 2px solid;
                                            border-color: {COLOR_PALETTE["secondary-color"]};
                                            padding: 6px;
                                            text-align: center;
                                            text-decoration: none;
                                            border-radius: 4px;
                                        }}
                                QPushButton:hover {{
                                            background-color: {COLOR_PALETTE["secondary-color"]};
                                        }}
                                QPushButton:pressed {{
                                            background-color: {COLOR_PALETTE["app-color"]};
                                        }}
                           """)
            msg_box.setWindowTitle("Warning!")
            msg_box.setText("Maximum zip count reached! \nCan't add more than 5 zip")
            msg_box.setIcon(QtWidgets.QMessageBox.Information)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            # Show the message box
            msg_box.exec_()

    def remove_tab(self, index=-1):
        self.zip_tabwidget.removeTab(1)

    def selectDestFolder(self):
        root_path = os.path.expanduser("~") + "/Desktop/TEST"    # Adding "/Desktop/TEST" for test purposes. Should be removed
        directory_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory", root_path, QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)

        if os.path.exists(directory_path):
            self.extract_all_btn.setEnabled(True)
            dest_treeView = CustomTreeView(self, directory_path)
            self.explorer_treeview_frame.layout().takeAt(0).widget().deleteLater()
            self.explorer_treeview_frame.layout().addWidget(dest_treeView)

            self.destination_label.setText(directory_path)

            # Update Log
            self.setLogMessage(f"Setting OS Folder to: {directory_path}")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = AssetProcessingApp()
    
    widget.show()
    sys.exit(app.exec_())
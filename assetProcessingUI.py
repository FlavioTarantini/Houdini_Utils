import sys
import json

from PySide2 import QtWidgets, QtGui, QtCore

from pyqtUtils import ElideLabel, CustomTreeView, DraggableTabBar

with open("themes.json", "r") as th:
    COLOR_PALETTE = json.load(th)["DEFAULT"]
ROOT_PATH = r"C:\Users\flavi\Desktop\test_folder"


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
        self.open_destination_btn = QtWidgets.QPushButton("Open Destination")
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
        self.destination_label = ElideLabel("Path to destination")
        self.destination_label.setStyleSheet(f"""
                                                margin-left: 10px;
                                            """)
        self.explorer_treeview = CustomTreeView(self, ROOT_PATH)
        # self.explorer_treeview.setFrameShape(QtWidgets.QFrame.Box)
        self.explorer_treeview.setAcceptDrops(True)


        folder_frame_layout.addWidget(self.open_destination_btn, 0, 0)
        folder_frame_layout.addWidget(self.destination_label, 0, 1)
        folder_frame_layout.addWidget(self.explorer_treeview, 1, 0, 2, 0)

        horizontal_spacer = QtWidgets.QSpacerItem(30, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        zip_frame_layout.addItem(horizontal_spacer, 2, 2)

        # Populating zip frame
        self.addzip_btn = QtWidgets.QPushButton("+ ZIP")
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
        self.zip_tabwidget.setTabBar(DraggableTabBar(self.zip_tabwidget))
        self.zip_tabwidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.zip_tabwidget.setDocumentMode(True)
        self.zip_tabwidget.setStyleSheet(f"""
                                         
                                            QTabBar::pane {{
                                                            border: 10px solid;
                                                            margin: 10px;
                                                        }}
                                            
                                            QTabBar::tab {{
                                                            background-color: #A5C9CA;
                                                            color: #2C3333;
                                                            padding: 8px;
                                                            border-top-left-radius: 4px;
                                                            border-top-right-radius: 4px;
                                                        }}

                                            QTabBar::tab:selected {{
                                                            background-color: #395B64;
                                                            color: #E7F6F2;
                                                        }}
                                        """)
        self.zip_treeview = CustomTreeView(self, ROOT_PATH)

        self.zip_tabwidget.addTab(self.zip_treeview, "zip1")
        self.button = QtWidgets.QPushButton("Extract All")
        self.button.setFixedWidth(80)
        self.button.setStyleSheet(f"""
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
        self.zip_tabwidget.setCornerWidget(self.addzip_btn, QtCore.Qt.Corner.TopRightCorner)

        horizontal_spacer = QtWidgets.QSpacerItem(500, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        zip_frame_layout.addWidget(self.zip_tabwidget, 0, 0, 2, 0)
        zip_frame_layout.addItem(horizontal_spacer, 0, 1)
        zip_frame_layout.addWidget(self.button, 1, 2)

        # Populating log frame
        log_label = QtWidgets.QLabel("Log:")
        log_label.setStyleSheet(f"""
                                    color: {COLOR_PALETTE["app-color"]};
                                    padding: 5px;
                                """)
        self.log_message = ElideLabel("This is a very long tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttext that may not fit in the window without resizing")
        self.log_message.setElideMode(QtCore.Qt.ElideRight)

        log_frame_layout.addWidget(log_label)
        log_frame_layout.addWidget(self.log_message)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    widget = AssetProcessingApp()
    
    widget.show()
    sys.exit(app.exec_())
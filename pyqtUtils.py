import json

from PySide2 import QtWidgets, QtGui, QtCore

with open("themes.json", "r") as th:
    COLOR_PALETTE = json.load(th)["DEFAULT"]

class ElideLabel(QtWidgets.QLabel):
    def __init__(self, text=None):
        super().__init__(text)

        self.setWordWrap(False)  # Disable word wrapping
        self.setFixedHeight(self.sizeHint().height())  # Set fixed height based on text height
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)  # Set horizontal policy to expanding
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)  # Align text to the top-left corner
        self.setMinimumSize(0, 0)
        
        self._elideMode = QtCore.Qt.ElideMiddle

    def elideMode(self):
        return self._elideMode

    def setElideMode(self, mode):
        if self._elideMode != mode and mode != QtCore.Qt.ElideNone:
            self._elideMode = mode
            self.updateGeometry()

    def minimumSizeHint(self):
        return self.sizeHint()

    def sizeHint(self):
        hint = self.fontMetrics().boundingRect(self.text()).size()
        l, t, r, b = self.getContentsMargins()
        margin = self.margin() * 2
        return QtCore.QSize(
            min(100, hint.width()) + l + r + margin, 
            min(self.fontMetrics().height(), hint.height()) + t + b + margin
        )

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        opt = QtWidgets.QStyleOptionFrame()
        self.initStyleOption(opt)
        self.style().drawControl(
            QtWidgets.QStyle.CE_ShapedFrame, opt, qp, self)
        l, t, r, b = self.getContentsMargins()
        margin = self.margin()
        try:
            # since Qt >= 5.11
            m = self.fontMetrics().horizontalAdvance('x') / 2 - margin
        except:
            m = self.fontMetrics().width('x') / 2 - margin
        r = self.contentsRect().adjusted(
            margin + m,  margin, -(margin + m), -margin)
        qp.drawText(r, self.alignment(), 
            self.fontMetrics().elidedText(
                self.text(), self.elideMode(), r.width()))


class CustomTreeView(QtWidgets.QTreeView):
    def __init__(self, parent, folder_path=None) -> None:
        super().__init__()
        self.folder_path = folder_path

        # Create the file system model
        self.model = QtWidgets.QFileSystemModel()
        self.model.setRootPath(self.folder_path)
        # Set the filter to show only directories
        self.model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot)

        self.setModel(self.model)

        palette = self.palette().color(QtGui.QPalette.Highlight).getRgb()
        highlight_color = (palette[0], palette[1], palette[2], 50)
        highlight_color_border = (palette[0]/3, palette[1]/3, palette[2]/3, 100)

        self.setStyleSheet(f"""
                                QTreeView::item {{
                                    border-radius: 6px;
                                    height: 30px;
                                }}
                                QTreeView {{
                                    margin-top: 10px;
                                }}

                                /*QTreeView::item:!has-children {{
                                    background-color: #555555;
                                }}*/

                                QTreeView::item:selected {{
                                    background-color: {COLOR_PALETTE["secondary-color"]};
                                    margin: 2px;
                                    color: {COLOR_PALETTE["light-color"]};
                                }}

                                """)  # Set style
                                
                                # /*QTreeView::branch {{
                                #     background-color: #555555; /* Background color for branches */
                                #     border: 0px;
                                #     border-radius: 0px;
                                # }}

                                # QTreeView::branch:siblings {{
                                #     margin-left: 10px;
                                #     margin-right: 19px;
                                # }}*/

        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setHeaderHidden(True)  # Hide header
        self.setIndentation(30)  # Set indentation
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        # Hide all sections except for the first one (name)
        for i in range(1, self.model.columnCount()):
            self.setColumnHidden(i, True)

        # Enable multi-selection
        self.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)
        
        # Set the root index of the tree view to the root index of the model
        self.setRootIndex(self.model.index(self.folder_path))

        # Expand all items in tree
        self.model.directoryLoaded.connect(self._fetchAndExpand)
        self.setItemsExpandable(False)
        self.setAcceptDrops(True)

    def _fetchAndExpand(self, path):
        index = self.model.index(path)
        self.expand(index)
        for i in range(self.model.rowCount(index)):
            child = index.child(i, 0)
            if self.model.isDir(child):
                self.model.setRootPath(self.model.filePath(child))

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            text = event.mimeData().text()
            print("Dropped:", text)
        else:
            event.ignore()

class DraggableTabBar(QtWidgets.QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMovable(True)
        self.drag_start_pos = None
        self.drag_index = -1

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_start_pos = event.pos()
            self.drag_index = self.tabAt(self.drag_start_pos)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_pos).manhattanLength() < QtWidgets.QApplication.startDragDistance():
            return
        drag = QtGui.QDrag(self)
        mime_data = QtCore.QMimeData()
        mime_data.setText("hello")  # Set the string value directly
        drag.setMimeData(mime_data)
        drag.exec_(QtCore.Qt.MoveAction)

    
    def dropEvent(self, event):
        if event.mimeData().hasText():
            text = event.mimeData().text()
            if text == "close":
                self.tabClosed.emit(self.drag_index)
            else:
                print("Dropped:", text)
                # Handle other dropped strings here
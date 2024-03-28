import os
import json
import zipfile
import pprint

from PySide2 import QtWidgets, QtGui, QtCore

with open("themes.json", "r") as th:
    COLOR_PALETTE = json.load(th)["DEFAULT"]
_text_color = QtGui.QColor(COLOR_PALETTE["additional-color"])
_text_color.setAlpha(125)
DISABLED_TEXT_COLOR = _text_color.getRgb()

class ElideLabel(QtWidgets.QLabel):
    def __init__(self, text=" "):
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
        self.model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot)      # Set the filter to show only directories
        self.setModel(self.model)

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
                                QScrollBar:vertical {{
                                    background: rgba{DISABLED_TEXT_COLOR};
                                    width: 8px;
                                    border-radius: 10px;
                                }}
                                QScrollBar::handle:vertical {{
                                    background: {COLOR_PALETTE["secondary-color"]};
                                    min-height: 10px;
                                    border-radius: 20px;
                                    padding: 0px;
                                }}
                                QScrollBar::add-line:vertical {{
                                    background: none;
                                }}
                                QScrollBar::sub-line:vertical {{
                                    background: none;
                                }}
                                QScrollBar::add-page:vertical, 
                                QScrollBar::sub-page:vertical {{
                                    background: none;
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

        self.setSelectionMode(QtWidgets.QTreeView.SingleSelection)        # Enable multi-selection
        self.setRootIndex(self.model.index(self.folder_path))               # Set the root index of the tree view to the root index of the model
        self.setItemsExpandable(True)
        self.setAcceptDrops(True)

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
            data_sharing = json.loads(event.mimeData().text())
            zippath = data_sharing["zippath"]
            member = data_sharing["member"]
            print(data_sharing)

            modelindex = self.indexAt(event.pos())
            if modelindex.isValid():
                dest_path = self.model.filePath(self.indexAt(event.pos()))
                self.extractZip(zippath, member, dest_path)
            else:
                dest_path = self.folder_path
                self.extractZip(zippath, member, dest_path)

            print("Dropped:", member)
        else:
            event.ignore()

    def extractZip(self, zippath, member, dest):
        with zipfile.ZipFile(zippath, "r") as zip:
            if not member:
                zip.extractall(dest)
            else:
                # TODO Implement extract zip of single members
                # _member = member  + "/"
                # zip.extractall(dest, members=[member])
                pass

            zip.close()
                

class zipTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent, zippath=None) -> None:
        super().__init__(parent)
        self.zippath = zippath
        self.setHeaderLabels(["Name", "type"])
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QTreeWidget.DragOnly)

        self.zip_name = os.path.basename(self.zippath)

        self._zipObject = zipfile.ZipFile(self.zippath, "r")
        # Open the zip file/s
        with self.zipObject as zip:
            # Get the list of files in the zip folder
            file_list = zip.namelist()  ################ PROBLEM HERE PRINT

            # Build directory structure
            # Setting zip root
            zip_structure = self.build_directory_structure(file_list)
            zip_root = QtWidgets.QTreeWidgetItem([self.zip_name])
            zip_root.setData(1, QtCore.Qt.UserRole, self.zippath)
            zip_root.setForeground(0, QtGui.QBrush(_text_color))
            fileInfo = QtCore.QFileInfo(self.zippath)                       # Gather OS zip Icon
            iconProvider = QtWidgets.QFileIconProvider()
            icon = iconProvider.icon(fileInfo)
            icon = icon.pixmap(icon.actualSize(QtCore.QSize(36, 36)))       # Scale to proper size
            zip_root.setIcon(0, icon)

            # pprint.pprint(zip_structure)
            self.populate_tree_widget(zip_structure, zip_root, self.zippath)
            self.addTopLevelItem(zip_root)
            self.sortItems(0, QtCore.Qt.AscendingOrder)
            self.sortItems(1, QtCore.Qt.AscendingOrder)
            self.setColumnHidden(1, True)
            zip_root.setExpanded(True)
            self.setAnimated(True)

        self.setStyleSheet(f"""
                                QTreeWidget::item {{
                                    border-radius: 6px;
                                    height: 30px;
                                }}
                                QTreeWidget {{
                                    margin-top: 10px;
                                }}

                                QTreeWidget::item:selected {{
                                    background-color: {COLOR_PALETTE["secondary-color"]};
                                    margin: 2px;
                                    color: {COLOR_PALETTE["light-color"]};
                                }}

                                QScrollBar:vertical {{
                                    background: rgba{DISABLED_TEXT_COLOR};
                                    width: 8px;
                                    border-radius: 10px;
                                }}
                                QScrollBar::handle:vertical {{
                                    background: {COLOR_PALETTE["secondary-color"]};
                                    min-height: 10px;
                                    border-radius: 20px;
                                    padding: 0px;
                                }}
                                QScrollBar::add-line:vertical {{
                                    background: none;
                                }}
                                QScrollBar::sub-line:vertical {{
                                    background: none;
                                }}
                                QScrollBar::add-page:vertical, 
                                QScrollBar::sub-page:vertical {{
                                    background: none;
                                }}

                                """)

        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setHeaderHidden(True)  # Hide header
        self.setIndentation(10)  # Set indentation
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSelectionMode(QtWidgets.QTreeView.ExtendedSelection)

    @property
    def zipObject(self):
        return self._zipObject
    
    def populate_tree_widget(self, dict, parent_item, zippath):
        if not dict:
            return
        for folder, child_dict in dict.items():
            _path = "/".join(child_dict[1][1:] + [folder])
            if not child_dict[0]:
                item = QtWidgets.QTreeWidgetItem([folder, "b"])
                item.setIcon(0, QtWidgets.QFileIconProvider().icon(QtWidgets.QFileIconProvider.File))
                item.setData(0, QtCore.Qt.UserRole, _path)
                item.setData(1, QtCore.Qt.UserRole, zippath)
                
                parent_item.addChild(item)
            else:
                item = QtWidgets.QTreeWidgetItem([folder, "a"])
                item.setIcon(0, QtWidgets.QFileIconProvider().icon(QtWidgets.QFileIconProvider.Folder))
                item.setData(0, QtCore.Qt.UserRole, _path)
                item.setData(1, QtCore.Qt.UserRole, zippath)
                
                parent_item.addChild(item)
                self.populate_tree_widget(child_dict[0], item, zippath)


    def build_directory_structure(self, file_list):
        directory_structure = {}
        for file_path in file_list:
            parts = file_path.split('/')
            current_level = directory_structure                         # Use a separate variable for traversal
            path = []
            for key, part in enumerate(parts):
                if part != "":
                    if key-1 != -1:
                        path.append(parts[key-1])
                    else:
                        path.append("__root__")
                    if part not in current_level:
                        current_level[part] = [{}, path.copy()]         # list is a mutuable object. Need to pass the copy of it to have it work properly
                    current_level = current_level[part][0]              # Move down one level
        return directory_structure
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        item = self.itemAt(event.pos())
        if item:
            self.startDrag(event, item)
 
    def startDrag(self, event, item):
        self.drag = QtGui.QDrag(self)
        pixmap = item.icon(0).pixmap(item.icon(0).actualSize(QtCore.QSize(64, 64)))     # Get the pixmap from the item's icon
        self.drag.setPixmap(pixmap)                                                     # Set the pixmap for visual representation of dragged item
        mime_data = QtCore.QMimeData()

        data_sharing = {}
        data_sharing["zippath"] = item.data(1, QtCore.Qt.UserRole)
        data_sharing["member"] = item.data(0, QtCore.Qt.UserRole)

        mime_data.setText(json.dumps(data_sharing))                                                     # Set the text to be dragged
        self.drag.setMimeData(mime_data)
        self.drag.exec_(QtCore.Qt.MoveAction)
        

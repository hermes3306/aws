import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, 
                             QFileDialog, QTextBrowser, QTreeView, QSplitter, QPlainTextEdit)
from PyQt5.QtGui import QPainter, QTextCursor, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QRect, QSize

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

class HTMLEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.updateLineNumberAreaWidth(0)

    def lineNumberAreaWidth(self):
        digits = 1
        max_value = max(1, self.blockCount())
        while max_value >= 10:
            max_value /= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, int(top), self.lineNumberArea.width(), self.fontMetrics().height(),
                                 Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

class HTMLViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Enhanced HTML Viewer')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # File Directory Tree
        self.file_tree = QTreeView()
        self.file_tree.setHeaderHidden(True)
        self.file_model = QStandardItemModel()
        self.file_tree.setModel(self.file_model)
        self.file_tree.clicked.connect(self.on_file_clicked)
        main_layout.addWidget(self.file_tree, 1)

        # Editor and Viewer
        editor_viewer_layout = QVBoxLayout()
        splitter = QSplitter(Qt.Vertical)

        self.text_edit = HTMLEditor()
        splitter.addWidget(self.text_edit)

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        splitter.addWidget(self.text_browser)

        editor_viewer_layout.addWidget(splitter)

        # Buttons
        button_layout = QHBoxLayout()
        btn_update = QPushButton('Update HTML View')
        btn_update.clicked.connect(self.update_html_view)
        button_layout.addWidget(btn_update)

        btn_save = QPushButton('Save HTML')
        btn_save.clicked.connect(self.save_html)
        button_layout.addWidget(btn_save)

        btn_load = QPushButton('Load HTML')
        btn_load.clicked.connect(self.load_html)
        button_layout.addWidget(btn_load)

        editor_viewer_layout.addLayout(button_layout)

        main_layout.addLayout(editor_viewer_layout, 3)

        self.update_file_tree()

    def update_file_tree(self, path='.'):
        self.file_model.clear()
        self.file_model.setHorizontalHeaderLabels(['File System'])
        
        root_path = os.path.abspath(path)
        root_item = QStandardItem(root_path)
        root_item.setData(root_path, Qt.UserRole)
        self.file_model.appendRow(root_item)
        self.populate_tree(root_item, root_path)

    def populate_tree(self, parent_item, parent_path):
        for name in os.listdir(parent_path):
            path = os.path.join(parent_path, name)
            item = QStandardItem(name)
            item.setData(path, Qt.UserRole)
            parent_item.appendRow(item)
            if os.path.isdir(path):
                self.populate_tree(item, path)

    def on_file_clicked(self, index):
        item = self.file_model.itemFromIndex(index)
        path = item.data(Qt.UserRole)
        if os.path.isfile(path):
            self.load_html(path)

    def update_html_view(self):
        html_content = self.text_edit.toPlainText()
        self.text_browser.setHtml(html_content)

    def save_html(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save HTML File", "", "HTML Files (*.html);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            print(f"Content saved to {file_name}")
            self.update_file_tree()

    def load_html(self, file_path=None):
        if not file_path:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(self, "Open HTML File", "", "HTML Files (*.html);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_edit.setPlainText(content)
            self.update_html_view()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = HTMLViewer()
    viewer.show()
    sys.exit(app.exec_())
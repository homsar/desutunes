#! /usr/bin/env python

import sys, os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from tablemodel import loadDatabase, col
from processfile import getMetadataForFileList
from processitunes import handleXML, exportXML
from player import AudioPlayer

class Desutunes(QWidget):
    def __init__(self, database):
        super().__init__()
        
        self._model = loadDatabase(database)
        if not self._model:
            print("Unable to load database.")
            sys.exit()
            
        self.initUI()

    def initUI(self):
        self.setAcceptDrops(True)
        self._tableView = self._model.createView("desutunes database")
        self._tableView.doubleClicked.connect(self.tableDoubleClick)
        self._player = AudioPlayer()
        boxes = QVBoxLayout()
        boxes.addWidget(self._player)
        boxes.addWidget(self._tableView)
        self.setLayout(boxes)
        self.resize(1024, 768)
        self.setWindowTitle("desutunes")
        self.show()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.reject()

    def dropEvent(self, e):
        try:
            files = [url.toLocalFile() for url in e.mimeData().urls()]
        except:
            return False
        else:
            if len(files) == 1 and files[0].endswith('xml'):
                self._model.addRecords(handleXML(files[0]))
            else:
                self._model.addRecords(getMetadataForFileList(files))

    def tableDoubleClick(self, cell):
        if not (cell.flags() & Qt.ItemIsEditable):
            row = cell.row()
            filename = self._model.data(self._model.index(row, col("File name")),
                                        Qt.DisplayRole)
            self._player.openFile(filename)
            self._player.play()

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Delete):
            selectionModel = self._tableView.selectionModel()
            for row in reversed(selectionModel.selectedRows()):
                self._model.removeRecord(row.row())
        super().keyPressEvent(event)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if 'inu' in sys.argv or 'inudesu' in sys.argv:
        icon = QIcon("inuicon.png")
        icon.addFile("inuicon_small.png")
        database = 'inudesutunes.db'
    else:
        icon = QIcon("icon.png")
        icon.addFile("icon_small.png")
        database = 'desutunes.db'
    app.setWindowIcon(icon)
    desutunes = Desutunes(database)
    if 'dump' in sys.argv:
        try:
            os.rename("songlibrary.xml", "songlibrary.xml.old")
        except:
            pass
        else:
            print("Backed up songlibrary.xml to songlibrary.xml.old, overwriting any previous backup/")
        exportXML(desutunes._model, "songlibrary.xml")
    else:
        desutunes.show()
        sys.exit(app.exec_())
    

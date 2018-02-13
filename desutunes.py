#! /usr/bin/env python

import sys, os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget, QVBoxLayout
from tablemodel import loadDatabase, col
from processfile import getMetadataForFileList
from processitunes import handleXML, exportXML
from player import AudioPlayer
from menu import setUpMenu

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
        self.palette().setColor(self.backgroundRole(), Qt.lightGray)
        self._menuBar, self._menu = setUpMenu(self)
        self.show()
        self.raise_()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.reject()

    def toggleDanger(self, checked):
        if self._model._lock_edits and checked:
            reply = QMessageBox.question(
                self,
                "Danger, danger!",
                "Danger mode removes the lock on editing the 'ID', 'File name', "
                "'Length', and 'Date added' fields. This could muck up"
                "the database state and/or nkd.su. Proceed with caution!\n\n"
                "Do you want to continue?",
                QMessageBox.Yes,
                QMessageBox.No
                )
            if reply == QMessageBox.Yes:
                self._model._lock_edits = False
                p  = self.palette()
                p.setColor(self.backgroundRole(), Qt.red)
                self.setPalette(p)
            else:
                self._menu['danger'].setChecked(False)
        else:
            self._model._lock_edits = True
            p = self.palette()
            p.setColor(self.backgroundRole(), Qt.lightGray)
            self.setPalette(p)

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
            self._player.openFile(
                filename,
                text='{} - {}'.format(
                    self._model.data(self._model.index(row, col("Track title"))),
                    self._model.data(self._model.index(row, col("Artist")))
                    ))
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
    

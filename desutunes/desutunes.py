#! /usr/bin/env python

import sys
import os
from pathlib import Path
from PyQt5.QtCore import Qt, QSettings, QSize, QPoint
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QApplication, QDialog, QFileDialog, QMessageBox,
                             QWidget, QVBoxLayout)
from .tablemodel import loadDatabase, col
from .processfile import getMetadataForFileList
from .processitunes import handleXML, exportXML
from .player import AudioPlayer
from .menu import setUpMenu
from shutil import move


class Desutunes(QWidget):
    def __init__(self, database, mode, settings):
        super().__init__()

        self.settings = settings
        libraryPath = self.settings.value(
            f'{mode}/libraryPath',
            defaultValue=os.path.expanduser(f'~/{mode}tunes'))
        self.libraryPath = Path(libraryPath)
        try:
            self.libraryPath.mkdir(parents=True, exist_ok=True)
        except Exception:
            QMessageBox.warning(self, "Couldn't create library",
                                "Unable to create a library folder.")
            sys.exit()

        self._model = loadDatabase(database, self.libraryPath)
        self._mode = mode
        if not self._model:
            QMessageBox.warning("Unable to load database.",
                                "desutunes couldn't load the database.")
            sys.exit()

        self.initUI()

    def initUI(self):
        self.setAcceptDrops(True)
        self._tableView = self._model.createView("desutunes database")
        self._tableView.doubleClicked.connect(self.tableDoubleClick)
        self._tableView.horizontalHeader().sectionClicked.connect(
            self.tableColumnHeaderClick)
        self._player = AudioPlayer()
        boxes = QVBoxLayout()
        boxes.addWidget(self._player)
        boxes.addWidget(self._tableView)
        self.setLayout(boxes)
        self.resize(
            self.settings.value(
                "window/size", defaultValue=QSize(1024, 768), type=QSize))
        self.move(
            self.settings.value(
                "window/pos", defaultValue=QPoint(200, 200), type=QPoint))
        self.setWindowTitle(f"{self._mode}tunes")
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.lightGray)
        self.setPalette(p)

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
                self, "Danger, danger!",
                "Danger mode removes the lock on editing the 'ID', "
                "'File name', 'Length', and 'Date added' fields. This "
                "could muck up the database state and/or nkd.su. "
                "Proceed with caution!\n\n"
                "Do you want to continue?", QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self._model._lock_edits = False
                p = self.palette()
                p.setColor(self.backgroundRole(), Qt.red)
                self.setPalette(p)
            else:
                self._menu['danger'].setChecked(False)
        else:
            self._model._lock_edits = True
            p = self.palette()
            p.setColor(self.backgroundRole(), Qt.lightGray)
            self.setPalette(p)

    def libraryLocation(self):
        browser = QFileDialog(
            self,
            f"Choose where to place the {self._mode} library",
        )
        browser.setFileMode(QFileDialog.DirectoryOnly)

        if browser.exec_() == QDialog.Accepted:
            self.settings.setValue(f'{self._mode}/libraryPath',
                                   browser.selectedFiles()[0])
            QMessageBox.information(
                self, 'Library location changed',
                'Library location changed.\n\n'
                'Reopen desutunes to load the new library.')
            self.close()

    def dropEvent(self, e):
        try:
            files = [url.toLocalFile() for url in e.mimeData().urls()]
        except Exception:
            return False
        else:
            if len(files) == 1 and files[0].endswith('xml'):
                self._model.addRecords(handleXML(files[0]))
            else:
                self._model.addRecords(getMetadataForFileList(files))

    def switch(self):
        if self._mode == 'nekodesu':
            newmode = 'inudesu'
        else:
            newmode = 'nekodesu'

        self.settings.setValue('mode', newmode)
        QMessageBox.information(
            self, f'Now in {newmode} mode',
            f'Restart desutunes to activate {newmode} mode.')
        self.close()

    def tableDoubleClick(self, cell):
        if not (cell.flags() & Qt.ItemIsEditable):
            row = cell.row()
            filename = self._model.data(
                self._model.index(row, col("File name")), Qt.DisplayRole)
            self._player.openFile(
                str(self.libraryPath / filename),
                text='{} - {}'.format(
                    self._model.data(
                        self._model.index(row, col("Track title"))),
                    self._model.data(self._model.index(row, col("Artist")))))
            self._player.play()

    def tableColumnHeaderClick(self, index):
        self._model.resort(index)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Delete):
            selectionModel = self._tableView.selectionModel()
            for row in reversed(selectionModel.selectedRows()):
                fileName = self._model.data(
                    self._model.index(row.row(), col("File name")))
                original = self.libraryPath / fileName
                if original.exists():
                    (self.libraryPath / "__deleted__").mkdir(
                        parents=True, exist_ok=True)
                    move(str(original), str(self.libraryPath / "__deleted__"))
                self._model.removeRecord(row.row())
        super().keyPressEvent(event)

    def closeEvent(self, event):
        self.settings.setValue('window/size', self.size())
        self.settings.setValue('window/pos', self.pos())
        event.accept()

    def dumpXML(self):
        browser = QFileDialog(self, "Pick a file to save the XML to.")
        browser.setAcceptMode(QFileDialog.AcceptSave)
        browser.setDefaultSuffix("xml")
        if browser.exec_() == QDialog.Accepted:
            exportXML(self._model, self.libraryPath,
                      browser.selectedFiles()[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    settings = QSettings('h0m54r', 'desutunes')
    if 'inu' in sys.argv or 'inudesu' in sys.argv:
        mode = 'inudesu'
    elif 'neko' in sys.argv or 'nekodesu' in sys.argv:
        mode = 'nekodesu'
    else:
        mode = settings.value('mode', defaultValue='nekodesu')

    if mode == 'nekodesu':
        icon = QIcon("icons/png/icon.png")
        icon.addFile("icons/png/icon_small.png")
        database = 'desutunes.db'
    else:
        icon = QIcon("icons/png/inuicon.png")
        icon.addFile("icons/png/inuicon_small.png")
        database = 'inudesutunes.db'

    app.setWindowIcon(icon)
    desutunes = Desutunes(database, mode, settings)
    if 'dump' in sys.argv:
        try:
            os.rename("songlibrary.xml", "songlibrary.xml.old")
        except Exception:
            pass
        else:
            print("Backed up songlibrary.xml to songlibrary.xml.old, "
                  "overwriting any previous backup.")
        exportXML(desutunes._model, desutunes.libraryPath, "songlibrary.xml")
    else:
        desutunes.show()
        sys.exit(app.exec_())

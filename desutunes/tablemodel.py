#!/usr/bin/env python


############################################################################
#
# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved.
#
# This file is part of the examples of PyQt.
#
# $QT_BEGIN_LICENSE:BSD$
# You may use this file under the terms of the BSD license as follows:
#
# "Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
#     the names of its contributors may be used to endorse or promote
#     products derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
# $QT_END_LICENSE$
#
############################################################################


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QTableView
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtSql import QSqlTableModel, QSqlDatabase, QSqlRecord

import shutil
import connection
import datetime

headers = [
    "ID",
    "File name",
    "Track title",
    "Artist",
    "Album",
    "Length",
    "Anime",
    "Role",
    "Role qualifier",
    "Label",
    "Composer",
    "In Myriad",
    "Date added"
    ]
col = headers.index


class desuplayerModel(QSqlTableModel):
    def __init__(self, libraryPath, parent=None, db=QSqlDatabase()):
        super(desuplayerModel, self).__init__(parent, db)

        self.setTable('tracks')

        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.select()
        self._lock_edits = True

        for index, name in enumerate(headers):
            self.setHeaderData(index, Qt.Horizontal, name)
        self.libraryPath = libraryPath

    def data(self, item, role=Qt.DisplayRole):
        if role == Qt.BackgroundRole:
            fileName = super().data(self.index(item.row(), col("File name")),
                                    Qt.DisplayRole)
            if not fileName:
                return super().data(item, role)
            file = self.libraryPath / fileName
            if not file.is_file():
                return QBrush(QColor(255, 128, 128))
            elif (super().data(self.index(item.row(), col("In Myriad")),
                               Qt.DisplayRole) in ["NO", "AWAITING EDITS"]
                  or super().data(self.index(item.row(), col("Label")),
                                  Qt.DisplayRole) == ''
                  or super().data(self.index(item.row(), col("Composer")),
                                  Qt.DisplayRole) == ''):
                return QBrush(QColor(255, 255, 128))
        return super().data(item, role)

    def flags(self, index):
        if (headers[index.column()] in (
                "ID", "File name", "Length", "Date added"
        ) and self._lock_edits):
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def addRecords(self, tracks):
        failures = []
        for idx, track in enumerate(tracks):
            print(f"Copying {track.OriginalFileName} ({idx} / {len(tracks)})...")
            try:
                if not (self.libraryPath / track.Filename.parent).is_dir():
                    (self.libraryPath / track.Filename.parent).mkdir()
                shutil.copyfile(track.OriginalFileName,
                                self.libraryPath / track.Filename)
            except Exception as ex:
                print(ex)
                failures.append(track)
                continue
            self._lock_edits = False
            record = self.record()
            for fieldName, fieldValue in track._asdict().items():
                if not fieldName == 'OriginalFileName':
                    record.setValue(fieldName, str(fieldValue))
            insertSuccess = self.insertRecord(-1, record)
            assert insertSuccess
            self._lock_edits = True
        self.submitAll()
        if len(failures) > 0:
            try:
                with open(self.libraryPath / 'failures.log', 'a') as f:
                    f.write(f"Import at {datetime.datetime.now()}:\n")
                    for track in failures:
                        f.write(f" - {track.Artist}, {track.Tracktitle}\n")
                    f.write("\n")
            except Exception as ex:
                print(ex)
                message = (
                    f'Unable to open {self.libraryPath / "failures.log"} '
                    'to write out failed track list.'
                )
            else:
                message = (
                    'List of failed tracks has been written to '
                    f'{self.libraryPath / "failures.log"}'
                )
            QMessageBox.warning(
                self.parent(),
                "Import error",
                f'{len(failures)} track{"" if len(failures) == 1 else "s"} '
                f'could not be imported successfully.\n\n{message}'
            )

        return True

    def createView(self, title):
        view = QTableView()
        view.setModel(self)
        view.setWindowTitle(title)
        return view

    def removeRecord(self, index):
        result = self.removeRow(index)
        result = result and self.submitAll()
        result = result and self.select()
        return result


def loadDatabase(database, libraryPath):
    if not connection.createConnection(libraryPath / database):
        return False
    return desuplayerModel(libraryPath)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    model = loadDatabase()

    view1 = createView("Table Model", model)
    view1.show()

    sys.exit(app.exec_())

from PyQt5 import QtGui, QtCore, QtWidgets

def setUpMenu(parent):
    menu = {}

    menu['danger'] = QtWidgets.QAction("&Danger mode", parent)
    menu['danger'].setShortcut('Ctrl+D')
    menu['danger'].setStatusTip('Enable editing protected fields')
    menu['danger'].setCheckable(True)
    menu['danger'].triggered.connect(parent.toggleDanger)

    menuBar = QtWidgets.QMenuBar(parent)
    toolsMenu = menuBar.addMenu('&Tools')
    for item in menu.values():
        toolsMenu.addAction(item)
        
    #QtWidgets.QStatusBar(parent)

    return menuBar, menu

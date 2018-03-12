from PyQt5 import QtGui, QtCore, QtWidgets

def setUpMenu(parent):
    menu = {}

    menu['danger'] = QtWidgets.QAction("&Danger mode", parent)
    menu['danger'].setShortcut('Ctrl+D')
    menu['danger'].setStatusTip('Enable editing protected fields')
    menu['danger'].setCheckable(True)
    menu['danger'].triggered.connect(parent.toggleDanger)

    menu['libraryLocation'] = QtWidgets.QAction("Set &library path...", parent)
    menu['libraryLocation'].setShortcut('Ctrl+L')
    menu['libraryLocation'].setStatusTip(
        'Choose a location to hold the music library'
    )
    menu['libraryLocation'].triggered.connect(parent.libraryLocation)

    menuBar = QtWidgets.QMenuBar(parent)
    toolsMenu = menuBar.addMenu('&Tools')
    for item in menu.values():
        toolsMenu.addAction(item)
        
    #QtWidgets.QStatusBar(parent)

    return menuBar, menu

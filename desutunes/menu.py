from PyQt5 import QtWidgets


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
        'Choose a location to hold the music library')
    menu['libraryLocation'].triggered.connect(parent.libraryLocation)

    menu['dump'] = QtWidgets.QAction("Dump &XML...", parent)
    menu['dump'].setShortcut('Ctrl+X')
    menu['dump'].setStatusTip(
        'Export the library as an iTunes XML file to upload to nkd.su')
    menu['dump'].triggered.connect(parent.dumpXML)

    if parent._mode == 'nekodesu':
        newMode = 'inu desu'
    else:
        newMode = 'neko desu'

    menu['switchDesu'] = QtWidgets.QAction(f"{newMode} mode", parent)
    menu['switchDesu'].setShortcut('Ctrl+M')
    menu['switchDesu'].setStatusTip(
        f'Switches over so manage the {newMode} library.')
    menu['switchDesu'].triggered.connect(parent.switch)

    menuBar = QtWidgets.QMenuBar(parent)
    toolsMenu = menuBar.addMenu('&Tools')
    for item in menu.values():
        toolsMenu.addAction(item)

    # QtWidgets.QStatusBar(parent)

    return menuBar, menu

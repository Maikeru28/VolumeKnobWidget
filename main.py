import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    tray = QSystemTrayIcon(QIcon("knob.ico"), app)
    tray.setToolTip("Volume Mixer")

    menu = QMenu()
    show_action = menu.addAction("Show Mixer")
    exit_action = menu.addAction("Exit")
    tray.setContextMenu(menu)

    window = MainWindow(tray)
    window.show()

    show_action.triggered.connect(window.show)
    exit_action.triggered.connect(app.quit)
    tray.activated.connect(lambda reason: window.show() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)

    tray.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
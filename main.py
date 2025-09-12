import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Create system tray icon
    tray = QSystemTrayIcon(QIcon("knob.ico"), app)
    tray.setToolTip("Volume Mixer")
    
    # Create tray menu
    menu = QMenu()
    show_action = menu.addAction("Show Mixer")
    exit_action = menu.addAction("Exit")
    tray.setContextMenu(menu)
    
    # Create main window
    window = MainWindow()
    window.show()  # Show the window initially
    
    # Connect menu actions
    show_action.triggered.connect(window.show)
    exit_action.triggered.connect(app.quit)
    
    # Show icon when double clicked
    tray.activated.connect(lambda reason: window.show() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None)
    
    tray.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
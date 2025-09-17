from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QSlider, QFrame, QPushButton, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt, QCoreApplication
from pycaw.pycaw import AudioUtilities, IMMDeviceEnumerator
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL



class MixerWindow(QWidget):
    def __init__(self, main_window, tray):
        super().__init__()
        self.main_window = main_window
        self.tray = tray
        self.setWindowTitle("Volume Mixer")
        self.setFixedWidth(400)  # Increased window width
        # Add Tool flag to prevent taskbar entry
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.volume_controller = self.main_window.volume_controller
        self.init_ui()
    
    def closeEvent(self, event):
        # Prevent the window from being destroyed, just hide it
        event.ignore()
        self.hide()
        
    def exit_application(self):
        self.tray.hide()  # Hide tray icon
        self.main_window.close()  # Close main window
        self.close()  # Close mixer window
        QCoreApplication.instance().quit()  # Quit application
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)  # Increased margins
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        # Device selector row
        device_row = QHBoxLayout()
        device_row.setContentsMargins(0, 0, 0, 0)
        
        device_label = QLabel("Output Device:")
        device_label.setFixedWidth(120)
        device_label.setStyleSheet("color: white;")
        
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(230)
        self.device_combo.setMaxVisibleItems(10)  # Show up to 10 items in dropdown
        self.device_combo.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px;
                selection-background-color: #00dfab;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
                background: #00dfab;
                width: 8px;
                height: 8px;
                border-radius: 4px;
                margin-right: 8px;
            }
            QComboBox:on {  /* when the combo box is open */
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: white;
                selection-background-color: #00dfab;
                selection-color: white;
                border: none;
                border-bottom-left-radius: 3px;
                border-bottom-right-radius: 3px;
                padding: 5px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 25px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #444444;
            }
        """)
        
        # Populate devices
        devices = self.volume_controller.get_output_devices()
        self.device_combo.clear()
        for name, dev_id in devices:
            self.device_combo.addItem(name, dev_id)

        self.device_combo.currentIndexChanged.connect(self._on_device_selected)
        
        # Set current device if available
        if self.device_combo.count() > 0:
            self.device_combo.setCurrentIndex(0)
        
        device_row.addWidget(device_label)
        device_row.addWidget(self.device_combo)
        device_row.addStretch()
        
        main_layout.addLayout(device_row)
        
        # Add separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #444444;")
        main_layout.addWidget(line)
        
        # Apps container
        apps_container = QWidget()
        self.apps_layout = QVBoxLayout(apps_container)
        self.apps_layout.setContentsMargins(0, 0, 0, 0)
        self.populate_apps()
        main_layout.addWidget(apps_container)
        
        # Bottom controls layout with proper alignment
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(5, 0, 5, 0)  # Reduce margins
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)  # Align items vertically
        
        # Add refresh button with transparent background
        refresh_button = QPushButton("⟳")
        refresh_button.setToolTip("Refresh Audio Apps")
        refresh_button.setFixedSize(24, 24)  # Smaller size to match checkbox
        refresh_button.clicked.connect(self.refresh_apps)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
                color: white;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover {
                color: #00dfab;
            }
        """)
        bottom_layout.addWidget(refresh_button)
        
        # Add lock position checkbox
        self.lock_position = QCheckBox("Lock Position")
        self.lock_position.setChecked(self.main_window.is_position_locked)
        self.lock_position.stateChanged.connect(self.toggle_position_lock)
        self.lock_position.setStyleSheet("""
            QCheckBox {
                margin-left: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::checked {
                color: #00dfab;
            }
        """)
        bottom_layout.addWidget(self.lock_position)
        
        # Add flexible space
        bottom_layout.addStretch()
        
        # Add exit button
        exit_button = QPushButton("Exit Program")
        exit_button.setFixedWidth(100)
        exit_button.setFixedHeight(24)  # Match height with other elements
        exit_button.clicked.connect(self.exit_application)
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #222222;
                border: none;
                border-radius: 3px;
                padding: 4px 15px;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #00dfab;
                color: #000000;
            }
        """)
        bottom_layout.addWidget(exit_button)
        
        main_layout.addLayout(bottom_layout)

    def populate_apps(self):
        # Clear existing items
        while self.apps_layout.count():
            child = self.apps_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Get all audio sessions
        sessions = self.volume_controller.get_applications()
        
        for app_name, session in sessions:
            app_frame = QFrame()
            app_layout = QHBoxLayout(app_frame)
            
            label = QLabel(app_name)
            label.setFixedWidth(150)
            app_layout.addWidget(label)
            
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(int(session.SimpleAudioVolume.GetMasterVolume() * 100))
            
            slider.valueChanged.connect(
                lambda value, s=session: s.SimpleAudioVolume.SetMasterVolume(value / 100, None)
            )
            
            app_layout.addWidget(slider)
            self.apps_layout.addWidget(app_frame)

    def refresh_apps(self):
        self.populate_apps()

    def toggle_position_lock(self, state):
        self.main_window.is_position_locked = bool(state)

    def change_output_device(self, index):
        device_id = self.device_combo.currentData()  # Get stored device_id
        if device_id and self.volume_controller.switch_output_device(device_id):
            self.refresh_apps()

    def _on_device_selected(self, index: int):
        dev_id = self.device_combo.currentData()
        if not dev_id:
            return
        if self.volume_controller.select_output_device(dev_id):
            print(f"DEBUG: Controlling selected device id={dev_id}")
        else:
            print(f"DEBUG: Failed to control device id={dev_id}")
        # If you still want to attempt changing the system default (optional):
        # self.volume_controller.set_default_output_device(dev_id)
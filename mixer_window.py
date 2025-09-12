from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QSlider, QFrame, QPushButton, QCheckBox)
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QIcon
from volume_controller import VolumeController

class MixerWindow(QWidget):
    def __init__(self, main_window, tray):
        super().__init__()
        self.main_window = main_window
        self.tray = tray
        self.setWindowTitle("Volume Mixer")
        self.setFixedWidth(300)
        # Add Tool flag to prevent taskbar entry
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.volume_controller = VolumeController()
        self.apps_layout = None  # Store reference to apps layout
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
        self.setLayout(main_layout)
        
        # Create a container for app sliders that we can refresh
        apps_container = QWidget()
        self.apps_layout = QVBoxLayout(apps_container)
        
        # Updated stylesheet with improved circular handle
        self.setStyleSheet("""
            QWidget {
                background-color: #333333;
                color: white;
            }
            QSlider {
                height: 24px;  /* Ensure enough vertical space for the handle */
            }
            QSlider::handle:horizontal {
                background: #00dfab;
                border: 2px solid #222222;
                width: 11px;
                height: 11px;
                margin: -6px 0;
                border-radius: 7px;  /* Slightly larger than half width/height */
            }
            QSlider::groove:horizontal {
                background: #333333;
                border: 2px solid #222222;
                height: 4px;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #222222;
                border: none;
                padding: 4px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #00dfab;
            }
            QCheckBox {
                color: white;
            }
        """)
        
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
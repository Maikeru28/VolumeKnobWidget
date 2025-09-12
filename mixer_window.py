from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                          QSlider, QFrame, QPushButton)
from PyQt6.QtCore import Qt, QCoreApplication
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
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: white;
            }
            QSlider::handle:horizontal {
                background: white;
                width: 18px;
            }
            QPushButton {
                background-color: #444444;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        
        self.volume_controller = VolumeController()
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
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Get all audio sessions
        sessions = self.volume_controller.get_applications()
        
        for app_name, session in sessions:
            # Create a frame for each app
            app_frame = QFrame()
            app_layout = QHBoxLayout(app_frame)
            
            # Add app name label
            label = QLabel(app_name)
            label.setFixedWidth(150)
            app_layout.addWidget(label)
            
            # Add volume slider
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(int(session.SimpleAudioVolume.GetMasterVolume() * 100))
            
            # Connect slider to volume control
            slider.valueChanged.connect(
                lambda value, s=session: s.SimpleAudioVolume.SetMasterVolume(value / 100, None)
            )
            
            app_layout.addWidget(slider)
            layout.addWidget(app_frame)
        
        # Add exit button at the bottom
        exit_button = QPushButton("Exit Program")
        exit_button.setFixedWidth(100)
        exit_button.clicked.connect(self.exit_application)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(exit_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
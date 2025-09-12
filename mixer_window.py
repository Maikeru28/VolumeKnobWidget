from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QFrame
from PyQt6.QtCore import Qt
from volume_controller import VolumeController

class MixerWindow(QWidget):
    def __init__(self):
        super().__init__()
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
        """)
        
        self.volume_controller = VolumeController()
        self.init_ui()
    
    def closeEvent(self, event):
        # Prevent the window from being destroyed, just hide it
        event.ignore()
        self.hide()
        
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
            def make_callback(s):
                return lambda v: s.SimpleAudioVolume.SetMasterVolume(v / 100, None)
            
            slider.valueChanged.connect(make_callback(session))
            
            app_layout.addWidget(slider)
            layout.addWidget(app_frame)
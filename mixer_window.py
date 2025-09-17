from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QFrame, QPushButton, QCheckBox
)
from PyQt6.QtCore import Qt, QCoreApplication

class MixerWindow(QWidget):
    def __init__(self, main_window, tray):
        super().__init__()
        self.main_window = main_window
        self.tray = tray
        self.volume_controller = self.main_window.volume_controller
        self.setWindowTitle("Volume Mixer")
        self.setFixedWidth(400)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.init_ui()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def exit_application(self):
        self.tray.hide()
        self.main_window.close()
        self.close()
        QCoreApplication.instance().quit()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.active_device_label = QLabel("")
        self.active_device_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(self.active_device_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background:#444;")
        layout.addWidget(line)

        self.apps_container = QWidget()
        self.apps_layout = QVBoxLayout(self.apps_container)
        self.apps_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.apps_container)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(5, 0, 5, 0)

        refresh_button = QPushButton("⟳")
        refresh_button.setToolTip("Refresh Audio Apps")
        refresh_button.setFixedSize(24, 24)
        refresh_button.clicked.connect(self.refresh_apps)
        refresh_button.setStyleSheet("""
            QPushButton { background:transparent; border:none; font-size:16px; color:white; }
            QPushButton:hover { color:#00dfab; }
        """)
        bottom.addWidget(refresh_button)


        self.lock_position = QCheckBox("Lock Position")
        self.lock_position.setChecked(self.main_window.is_position_locked)
        self.lock_position.stateChanged.connect(self.toggle_position_lock)
        self.lock_position.setStyleSheet("QCheckBox { color:white; }")
        bottom.addWidget(self.lock_position)

        bottom.addStretch()

        exit_button = QPushButton("Exit Program")
        exit_button.clicked.connect(self.exit_application)
        exit_button.setFixedHeight(24)
        exit_button.setStyleSheet("""
            QPushButton {
                background:#222; border:none; border-radius:3px;
                padding:4px 15px; color:white;
            }
            QPushButton:hover { background:#00dfab; color:#000; }
        """)
        bottom.addWidget(exit_button)

        layout.addLayout(bottom)

    def update_active_device_label(self):
        name = self.volume_controller.current_device_name  # always maintained by controller
        self.active_device_label.setText(f"Active Device: {name}")

    def populate_apps(self):
        while self.apps_layout.count():
            item = self.apps_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for app_name, session in self.volume_controller.get_applications():
            frame = QFrame()
            row = QHBoxLayout(frame)
            lbl = QLabel(app_name)
            lbl.setFixedWidth(150)
            lbl.setStyleSheet("color:white;")
            row.addWidget(lbl)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            try:
                slider.setValue(int(session.SimpleAudioVolume.GetMasterVolume() * 100))
            except:
                slider.setValue(0)
            slider.valueChanged.connect(
                lambda val, s=session: s.SimpleAudioVolume.SetMasterVolume(val / 100.0, None)
            )
            slider.setStyleSheet("""
                QSlider::groove:horizontal { height:6px; background:#333; border-radius:3px; }
                QSlider::handle:horizontal { width:14px; background:#00dfab; margin:-4px 0; border-radius:7px; }
                QSlider::sub-page:horizontal { background:#00dfab; border-radius:3px; }
            """)
            row.addWidget(slider)
            self.apps_layout.addWidget(frame)

    def refresh_apps(self):
        self.populate_apps()
        self.update_active_device_label()
        self.volume_controller.force_rebind()
        self.update_active_device_label()
        # Optionally also resync knob in main window
        if hasattr(self.main_window, "_sync_rotation_from_volume"):
            self.main_window._sync_rotation_from_volume()
        print("DEBUG: Manual device rebind triggered.")

    def toggle_position_lock(self, state):
        self.main_window.is_position_locked = bool(state)

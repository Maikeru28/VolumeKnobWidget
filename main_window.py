import math
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QImage, QPixmap, QFont, QColor
from volume_controller import VolumeController
from mixer_window import MixerWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Volume Knob")
        self.setFixedSize(100, 100)
        # Update window flags to include Tool flag which hides from taskbar
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Load knob image
        self.knob_image = QImage("knob.png")  # Put your image in the same folder
        self.volume_controller = VolumeController()
        self.mixer_window = None
        self.last_position = None
        
        # Initialize knob position with -120 degree offset
        self.rotation = (self.volume_controller.get_master_volume() * 270) - 120
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_position = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            print("Right click detected")  # Debug print
            self.show_mixer()
            
    def mouseMoveEvent(self, event):
        if self.last_position:
            delta = event.globalPosition().toPoint() - self.last_position
            self.move(self.pos() + delta)
            self.last_position = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        self.last_position = None
        
    def wheelEvent(self, event):
        # Get scroll direction (-1 or 1)
        delta = event.angleDelta().y() / 120
        
        # Get current volume (0-1 range)
        current_volume = self.volume_controller.get_master_volume()
        
        # Calculate new volume with small increments (0.02 = 2% per scroll)
        new_volume = current_volume + (delta * 0.02)
        
        # Ensure volume stays between 0 and 1
        new_volume = max(0.0, min(1.0, new_volume))
        
        # Update volume
        self.volume_controller.set_master_volume(new_volume)
        
        # Update rotation for visual feedback with -120 degree offset
        self.rotation = (new_volume * 270) - 135
        self.update()
        
    def show_mixer(self):
        print("Opening mixer window")  # Debug print
        if not self.mixer_window:
            print("Creating new mixer window")  # Debug print
            self.mixer_window = MixerWindow()
        self.mixer_window.show()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Calculate center point
        center = QPoint(50, 50)
        
        # Save the current state
        painter.save()
        
        # Translate to center, rotate, then translate back
        painter.translate(center)
        painter.rotate(self.rotation)
        painter.translate(-center)
        
        # Draw the knob image
        painter.drawImage(0, 0, self.knob_image)
        
        # Restore the original state
        painter.restore()
        
        # Draw volume percentage text
        volume_percent = int(self.volume_controller.get_master_volume() * 100)
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.setPen(QColor("#00dfab"))
        
        # Get text width to center it
        text = f"{volume_percent}"
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
        
        # Draw centered text
        painter.drawText(
            int(center.x() - text_width/2),
            int(center.y() + text_height/3),
            text
        )
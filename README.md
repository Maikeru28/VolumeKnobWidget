# Volume Knob

A Python application that allows you to control your system's volume using a custom knob interface. The app features a transparent, draggable window with a knob that adjusts the master volume when you scroll over it. It also includes a system tray icon and a volume mixer window for controlling individual application volumes.

---

## Features

- **Custom Volume Knob**: A draggable, transparent window with a knob to control the system's master volume.
- **Volume Mixer**: Right-click the knob to open a mixer window for adjusting individual application volumes.
- **System Tray Icon**: The app runs in the background with a tray icon for easy access.
- **Volume Display**: Displays the current volume percentage in the center of the knob.
- **Taskbar-Free**: The app does not appear in the taskbar.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/USERNAME/volume-knob.git
   cd volume-knob
   ```

2. **Install Dependencies**:
   Make sure you have Python 3.10+ installed. Then, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add the Knob Icon**:
   Place your `knob.ico` and `knob.png` files in the project directory.

---

## Usage

1. **Run the Application**:
   ```bash
   python main.py
   ```

2. **Controls**:
   - **Scroll**: Adjust the master volume.
   - **Drag**: Move the knob window.
   - **Right-Click**: Open the volume mixer window.
   - **System Tray**: Double-click the tray icon to show the knob window.

3. **Exit**:
   - Right-click the tray icon and select "Exit".

---

## Requirements

- Python 3.10+
- PyQt6
- pycaw

Install dependencies with:
```bash
pip install -r requirements.txt
```

---

## Project Structure

```
volume-knob/
├── main.py               # Entry point for the application
├── main_window.py        # Main knob window
├── mixer_window.py       # Volume mixer window
├── volume_controller.py  # Handles system and app volume control
├── knob.ico              # System tray icon
├── knob.png              # Knob image for the main window
└── requirements.txt      # Python dependencies
```

---

## Screenshots

### Main Knob Window
![Knob Window](screenshot_knob.png)

### Volume Mixer
![Volume Mixer](screenshot_mixer.png)

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## Author

Created by **Mixalis Vroutsis**.
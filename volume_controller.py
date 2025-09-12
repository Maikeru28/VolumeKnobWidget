from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class VolumeController:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        
    def get_master_volume(self):
        """Returns the current master volume level (0.0 to 1.0)"""
        return self.volume.GetMasterVolumeLevelScalar()
    
    def set_master_volume(self, value):
        """Sets the current master volume level (0.0 to 1.0)"""
        value = max(0.0, min(1.0, value))
        self.volume.SetMasterVolumeLevelScalar(value, None)
    
    def adjust_master_volume(self, delta):
        """Adjusts the master volume by the given delta"""
        current = self.get_master_volume()
        self.set_master_volume(current + delta)

    def get_applications(self):
        """Returns a list of active audio sessions"""
        sessions = AudioUtilities.GetAllSessions()
        apps = []
        for s in sessions:
            if s.State != 0:  # 0 = inactive
                name = s.Process.name() if s.Process else "System Sounds"
                # Capitalize first letter
                name = name.capitalize()
                apps.append((name, s))
        return apps
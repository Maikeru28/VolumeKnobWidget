from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


DEBUG = True

__all__ = ["VolumeController"]

class VolumeController:
    def __init__(self):
        self.volume = None
        self.current_device_key = None
        self.current_device_name = "Unknown"
        self._bind_to_default_device()

    def _log(self, *args):
        if DEBUG:
            print("DEBUG:", *args)
    # --- Friendly name resolution (robust enumeration approach) ---
    def _resolve_friendly_name(self, dev):
        """Attempt to obtain a stable, human‑readable friendly name for the
        provided device wrapper without relying on direct PROPERTYKEY access.

        Strategy:
          1. Try cached FriendlyName on the given device (if pycaw already set it).
          2. Determine the device id (id attribute or GetId() method).
          3. Enumerate all devices (AudioUtilities.GetAllDevices) – this forces
             pycaw to populate FriendlyName attributes for the list entries.
          4. Match by id; if found and FriendlyName present, return it.
          5. Fallback: pick first active render device with a FriendlyName.
          6. Final fallback: return device id or a generic placeholder.
        """
        # 1. Cached attribute
        cached = getattr(dev, "FriendlyName", None)
        if cached:
            return cached

        # 2. Obtain id
        dev_id = getattr(dev, "id", None)
        if not dev_id and hasattr(dev, "GetId"):
            try:
                dev_id = dev.GetId()
            except Exception:
                dev_id = None

        try:
            devices = AudioUtilities.GetAllDevices()
        except Exception as e:
            self._log("GetAllDevices failed while resolving name:", e)
            return dev_id or "Output Device"

        # 3/4. Match by id
        if dev_id:
            for d in devices:
                if getattr(d, "id", None) == dev_id:
                    fn = getattr(d, "FriendlyName", None)
                    if fn:
                        return fn

        # 5. First active render with FriendlyName
        for d in devices:
            try:
                if getattr(d, "dataflow", None) == 0 and getattr(d, "state", 0) == 1:
                    fn = getattr(d, "FriendlyName", None)
                    if fn:
                        return fn
            except Exception:
                continue

        # 6. Fallback
        return dev_id or "Output Device"
        return dev_id or "Output Device"

    def _default_device_and_key(self):
        try:
            dev = AudioUtilities.GetSpeakers()
            dev_id = getattr(dev, "id", None)
            name = self._resolve_friendly_name(dev)
            key = dev_id or name
            return dev, key, name
        except Exception as e:
            self._log("Get default device failed:", e)
            return None, None, None

    def _bind_to_default_device(self):
        dev, key, name = self._default_device_and_key()
        if not dev:
            self._log("No default device to bind.")
            return
        try:
            iface = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(iface, POINTER(IAudioEndpointVolume))
            self.current_device_key = key
            self.current_device_name = name
            self._log("Bound to default device:", name, "| key:", key)
        except Exception as e:
            self._log("Activate IAudioEndpointVolume failed:", e)

    def refresh_if_default_changed(self):
        dev, key, name = self._default_device_and_key()
        if not dev or not key:
            return
        if key != self.current_device_key:
            self._log("Default device change detected -> rebinding")
            try:
                iface = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume = cast(iface, POINTER(IAudioEndpointVolume))
                self.current_device_key = key
                self.current_device_name = name
                self._log("Rebound to:", name)
            except Exception as e:
                self._log("Rebind failed:", e)

    def force_rebind(self):
        self._log("Manual rebind requested.")
        self._bind_to_default_device()

    def get_current_device_name(self) -> str:
        return self.current_device_name

    @property
    def device_name(self) -> str:
        return self.current_device_name

    def get_master_volume(self) -> float:
        try:
            return self.volume.GetMasterVolumeLevelScalar()
        except Exception as e:
            self._log("Get master volume failed:", e)
            return 0.0

    def set_master_volume(self, value: float):
        try:
            value = max(0.0, min(1.0, value))
            self.volume.SetMasterVolumeLevelScalar(value, None)
        except Exception as e:
            self._log("Set master volume failed:", e)

    def adjust_master_volume(self, delta: float):
        self.set_master_volume(self.get_master_volume() + delta)

    def get_applications(self):
        sessions = AudioUtilities.GetAllSessions()
        out = []
        for s in sessions:
            try:
                if s.State != 0:
                    name = s.Process.name() if s.Process else "System Sounds"
                    out.append((name.capitalize(), s))
            except Exception:
                continue
        return out
# filepath: c:\Users\MixalisVroutsis\Documents\Python scripts\Volume knob\volume_controller.py
from ctypes import cast, POINTER, HRESULT, c_void_p, c_wchar_p, c_int
import comtypes
from comtypes import CLSCTX_ALL, GUID, COMMETHOD
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import subprocess
import shlex
import tempfile, os

# PolicyConfig (Win7+ works on modern Windows)
CLSID_PolicyConfigClient = GUID("{870AF99C-171D-4F9E-AF0D-E63DF40C2BC9}")
class IPolicyConfig(comtypes.IUnknown):
    _iid_ = GUID("{F8679F50-850A-41CF-9C72-430F290290C8}")
    _methods_ = (
        COMMETHOD([], HRESULT, 'GetMixFormat', (['in'], c_wchar_p), (['out'], POINTER(c_void_p))),
        COMMETHOD([], HRESULT, 'GetDeviceFormat', (['in'], c_wchar_p), (['in'], c_int), (['out'], POINTER(c_void_p))),
        COMMETHOD([], HRESULT, 'SetDeviceFormat', (['in'], c_wchar_p), (['in'], POINTER(c_void_p)), (['in'], POINTER(c_void_p))),
        COMMETHOD([], HRESULT, 'GetProcessingPeriod', (['in'], c_wchar_p), (['in'], c_int), (['out'], POINTER(c_void_p))),
        COMMETHOD([], HRESULT, 'SetProcessingPeriod', (['in'], c_wchar_p), (['in'], POINTER(c_void_p))),
        COMMETHOD([], HRESULT, 'GetShareMode', (['in'], c_wchar_p), (['out'], POINTER(c_void_p))),
        COMMETHOD([], HRESULT, 'SetShareMode', (['in'], c_wchar_p), (['in'], POINTER(c_void_p))),
        COMMETHOD([], HRESULT, 'GetPropertyValue', (['in'], c_wchar_p), (['in'], POINTER(c_void_p)), (['out'], POINTER(c_void_p))),
        COMMETHOD([], HRESULT, 'SetPropertyValue', (['in'], c_wchar_p), (['in'], POINTER(c_void_p)), (['in'], POINTER(c_void_p))),
        COMMETHOD([], HRESULT, 'SetDefaultEndpoint', (['in'], c_wchar_p), (['in'], c_int)),
        COMMETHOD([], HRESULT, 'SetEndpointVisibility', (['in'], c_wchar_p), (['in'], c_int)),
    )

class VolumeController:
    def __init__(self):
        self.current_device_id = None
        self.refresh_devices()  # default device at startup

    def refresh_devices(self):
        # Keep original default-device initialization
        speakers = AudioUtilities.GetSpeakers()
        iface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(iface, POINTER(IAudioEndpointVolume))
        # Try to capture its id if exposed
        self.current_device_id = getattr(speakers, "id", None)

    def get_master_volume(self):
        return self.volume.GetMasterVolumeLevelScalar()

    def set_master_volume(self, value: float):
        value = max(0.0, min(1.0, value))
        self.volume.SetMasterVolumeLevelScalar(value, None)

    def adjust_master_volume(self, delta: float):
        self.set_master_volume(self.get_master_volume() + delta)

    def get_applications(self):
        apps = []
        for s in AudioUtilities.GetAllSessions():
            try:
                if s.State != 0:
                    nm = s.Process.name() if s.Process else "System Sounds"
                    apps.append((nm.capitalize(), s))
            except:
                continue
        return apps

    def get_output_devices(self):
        out, seen = [], set()
        for d in AudioUtilities.GetAllDevices():
            try:
                state = getattr(d, "state", None)
                name  = getattr(d, "FriendlyName", None)
                did   = getattr(d, "id", None)
                if not (name and did and state):
                    continue
                if (state.value if hasattr(state, "value") else state) != 1:
                    continue
                low = name.lower()
                if any(k in low for k in ("microphone", "hands-free", "hands free", "headset (", "line in")):
                    continue
                if did not in seen:
                    out.append((name, did)); seen.add(did)
            except:
                continue
        if not out:
            try:
                spk = AudioUtilities.GetSpeakers()
                if getattr(spk, "FriendlyName", None) and getattr(spk, "id", None):
                    out.append((spk.FriendlyName, spk.id))
            except:
                pass
        print("DEBUG: Playback devices:", out)
        return out

    def set_default_output_device(self, device_id: str) -> bool:
        """
        Switch default playback device via PowerShell + C#.
        Returns True only if SetDefaultEndpoint returns 0 for all roles.
        """
        import tempfile, os, subprocess, re

        ps_template = r'''
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

[ComImport, Guid("870AF99C-171D-4F9E-AF0D-E63DF40C2BC9")]
class PolicyConfigClient {}

[ComImport, InterfaceType(ComInterfaceType.InterfaceIsIUnknown),
 Guid("F8679F50-850A-41CF-9C72-430F290290C8")]
interface IPolicyConfig {
  int GetMixFormat(string pszDeviceName, out IntPtr ppFormat);
  int GetDeviceFormat(string pszDeviceName, int bDefault, out IntPtr ppFormat);
  int SetDeviceFormat(string pszDeviceName, IntPtr pEndpointFormat, IntPtr pMixFormat);
  int GetProcessingPeriod(string pszDeviceName, int bDefault, out IntPtr pPeriod);
  int SetProcessingPeriod(string pszDeviceName, IntPtr pPeriod);
  int GetShareMode(string pszDeviceName, out IntPtr pMode);
  int SetShareMode(string pszDeviceName, IntPtr pMode);
  int GetPropertyValue(string pszDeviceName, IntPtr key, out IntPtr pv);
  int SetPropertyValue(string pszDeviceName, IntPtr key, IntPtr pv);
  int SetDefaultEndpoint(string pszDeviceName, int role);
  int SetEndpointVisibility(string pszDeviceName, int bVisible);
}

public static class AudioSwitch {
  public static int Set(string id) {
    var pc = (IPolicyConfig)(new PolicyConfigClient());
    int rc = 0;
    rc |= pc.SetDefaultEndpoint(id,0);
    rc |= pc.SetDefaultEndpoint(id,1);
    rc |= pc.SetDefaultEndpoint(id,2);
    return rc;
  }
}
"@ -ErrorAction Stop

$rc = [AudioSwitch]::Set("{DEV_ID}")
Write-Host "PSRETURN:$rc"
exit $rc
'''
        ps_code = ps_template.replace("{DEV_ID}", device_id)
        script_path = None
        try:
            import textwrap
            ps_code = textwrap.dedent(ps_code)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ps1", mode="w", encoding="utf-8") as f:
                f.write(ps_code)
                script_path = f.name
            proc = subprocess.run(
                ["powershell.exe","-NoProfile","-ExecutionPolicy","Bypass","-File",script_path],
                capture_output=True, text=True
            )
            stdout = proc.stdout.strip()
            stderr = proc.stderr.strip()
            if stdout:
                print("DEBUG: PS STDOUT:", stdout)
            if stderr:
                print("DEBUG: PS STDERR:", stderr)

            m = re.search(r'PSRETURN:(\d+)', stdout)
            if not m:
                print("DEBUG: Missing PSRETURN marker.")
                return False
            rc = int(m.group(1))
            if rc == 0 and proc.returncode == 0:
                self.refresh_devices()
                return True
            print(f"DEBUG: Switch failed rc={rc} exit={proc.returncode}")
            return False
        except Exception as e:
            print("DEBUG: PowerShell exception:", e)
            return False
        finally:
            if script_path and script_path and os.path.exists(script_path):
                try: os.remove(script_path)
                except: pass

    def select_output_device(self, device_id: str) -> bool:
        """
        Point volume operations to a specific (active) playback device by its endpoint ID.
        Does NOT change the system default device.
        """
        try:
            enumerator = AudioUtilities.GetDeviceEnumerator()
            imm_device = enumerator.GetDevice(device_id)
        except Exception as e:
            print(f"DEBUG: GetDevice failed for id={device_id}: {e}")
            return False
        try:
            iface = imm_device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(iface, POINTER(IAudioEndpointVolume))
            self.current_device_id = device_id
            # Optional: friendly name lookup for debug
            for name, did in self.get_output_devices():
                if did == device_id:
                    print(f"DEBUG: Now controlling volume of: {name}")
                    break
            return True
        except Exception as e:
            print(f"DEBUG: Activate IAudioEndpointVolume failed: {e}")
            return False
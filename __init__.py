import logging
import socket
import threading
import time
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_PASSWORD, CONF_USERNAME, Platform
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SELECT]

# Schema for the "Set All" service
SERVICE_SET_ALL_SCHEMA = vol.Schema({
    vol.Required("input"): int,
})

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Extron DXP from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    controller = ExtronController(host, port, username, password)
    hass.data[DOMAIN][entry.entry_id] = controller

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # --- REGISTER SERVICE ---
    async def handle_set_all(call: ServiceCall):
        """Handle the service call to set all outputs."""
        input_num = call.data.get("input")
        # Command: Input * Output ! -> X * ! (Set all outputs to X)
        # Note: 0 * ! disconnects all
        cmd = f"{input_num}*!"
        await hass.async_add_executor_job(controller.send_command, cmd)

    hass.services.async_register(
        DOMAIN, "set_all_outputs", handle_set_all, schema=SERVICE_SET_ALL_SCHEMA
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

class ExtronController:
    """Manages the Ethernet connection and Authentication."""
    def __init__(self, host, port, username=None, password=None):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._lock = threading.Lock()
        self._socket = None

    def _connect(self):
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(5.0)
            self._socket.connect((self._host, self._port))
            _LOGGER.info(f"Connecting to Extron at {self._host}...")

            if self._password:
                time.sleep(0.5)
                try:
                    data = self._socket.recv(4096).decode('utf-8', errors='ignore')
                except:
                    data = ""

                if "Password:" in data or "Login:" in data:
                    self._socket.sendall(f"{self._password}\r\n".encode('utf-8'))
                    time.sleep(0.5)
                    self._socket.recv(1024) # Clear buffer
            
            self._socket.settimeout(2.0)
        except Exception as e:
            _LOGGER.error(f"Failed to connect: {e}")
            self._socket = None

    def send_command(self, command):
        with self._lock:
            if self._socket is None:
                self._connect()
                if self._socket is None:
                    return None
            try:
                full_cmd = f"{command}\r".encode('utf-8')
                self._socket.sendall(full_cmd)
                return self._socket.recv(1024).decode('utf-8').strip()
            except Exception:
                if self._socket:
                    self._socket.close()
                self._socket = None
                return None
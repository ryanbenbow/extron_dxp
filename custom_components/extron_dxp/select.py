import logging
from datetime import timedelta
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Setup entities from a config entry."""
    controller = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    # Create 8 Output Entities
    for i in range(1, 9):
        entities.append(ExtronOutputSelect(controller, i))
    
    async_add_entities(entities)

class ExtronOutputSelect(SelectEntity):
    """Representation of an Extron Output."""
    def __init__(self, controller, output_num):
        self._controller = controller
        self._output = output_num
        self._attr_name = f"Extron Output {output_num}"
        self._attr_unique_id = f"extron_{controller._host}_out_{output_num}"
        self._attr_options = [str(i) for i in range(0, 17)] # 0-16
        self._current_option = "0"

    @property
    def current_option(self):
        return self._current_option

    def select_option(self, option: str) -> None:
        cmd = f"{option}*{self._output}!"
        self._controller.send_command(cmd)
        self._current_option = option
        self.schedule_update_ha_state()

    def update(self):
        resp = self._controller.send_command(f"{self._output}%")
        if resp:
            try:
                # Parse 'In4 All' or 'Ch4' responses
                if "In" in resp:
                    val = resp.split("In")[1].split(" ")[0]
                    self._current_option = str(int(val))
                elif "Ch" in resp:
                    val = resp.split("Ch")[1].split(" ")[0]
                    self._current_option = str(int(val))
            except Exception:
                pass
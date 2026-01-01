import voluptuous as vol
import socket
import logging
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_PASSWORD, CONF_USERNAME
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ExtronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Extron DXP."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})

            valid = await self.hass.async_add_executor_job(
                self._test_connection,
                user_input[CONF_HOST],
                user_input[CONF_PORT]
            )

            if valid:
                return self.async_create_entry(
                    title=f"Extron DXP ({user_input[CONF_HOST]})",
                    data=user_input
                )
            else:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=23): int,
            vol.Optional(CONF_PASSWORD): str,
            vol.Optional(CONF_USERNAME): str,
        })

        return self.async_show_form(
            step_id="user", 
            data_schema=data_schema, 
            errors=errors
        )

    def _test_connection(self, host, port):
        """Try to open a socket to verify connectivity."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((host, port))
            sock.close()
            return True
        except Exception:
            return False
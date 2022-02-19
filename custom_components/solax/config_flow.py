"""Config flow for solax integration."""
import logging
from typing import Any

from solax import real_time_api
from solax.inverter import DiscoveryError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_PORT
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 80
DEFAULT_PASSWORD = ""

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD): cv.string,
    }
)


def force_install_dev_version():
    import pkg_resources
    from importlib.metadata import version

    dep = "solax@git+https://github.com/VadimKraus/solax.git@feature/QVOLTHYBG33P-Inverter"
    req = pkg_resources.Requirement.parse(dep)
    installed_version = version(req.project_name)
    print(installed_version)
    if installed_version == "0.2.9":
        _LOGGER.error("Wrong version of solax installed")
        import subprocess
        import sys

        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        raise Exception("Wrong version of solax installed, had to force reinstall")


async def validate_api(data) -> str:
    """Validate the credentials."""
    force_install_dev_version()
    _LOGGER.error(f"Trying to connect to {data}")

    api = await real_time_api(
        data[CONF_IP_ADDRESS], data[CONF_PORT], data[CONF_PASSWORD]
    )
    response = await api.get_data()
    return response.serial_number


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solax."""

    async def async_step_user(self, user_input: dict[str, Any] = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, Any] = {}
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
            )

        try:
            serial_number = await validate_api(user_input)
        except (ConnectionError, DiscoveryError):
            _LOGGER.exception("Discovery fail")
            errors["base"] = "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            await self.async_set_unique_id(serial_number)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=serial_number, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, config: dict[str, Any]) -> FlowResult:
        """Handle import of solax config from YAML."""

        import_data = {
            CONF_IP_ADDRESS: config[CONF_IP_ADDRESS],
            CONF_PORT: config[CONF_PORT],
            CONF_PASSWORD: DEFAULT_PASSWORD,
        }

        return await self.async_step_user(user_input=import_data)

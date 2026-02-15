from homeassistant.components.number import NumberEntity
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.device_registry import DeviceInfo
from .constants import DOMAIN, STORAGE_KEY, STORAGE_VERSION, REGION,_LOGGER

class HarviaHumiditySetPoint(NumberEntity):
    """Representation of a number entity to set the target humidity."""

    def __init__(self, device, name, sauna):
        """Initialize the humidity setpoint number entity."""
        self._name = name + ' Steamer Humidity'
        self._state = None
        self._device = device
        self._device_id = device.id + '_humidity_set_point'
        self._sauna = sauna
        self._attr_unique_id = device.id + '_humidity_set_point'
        self._attr_icon = 'mdi:cloud-percent'
        # Bind this entity to a Home Assistant device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.id)},
            name=getattr(device, "name", None) or name,
            manufacturer="Harvia",
            model=getattr(device, "model", None) or "Xenio WiFi",
        )

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name


    @property
    def min_value(self):
        """Return the minimum humidity value that can be set."""
        return 0  # Set this to your desired minimum boundary value

    @property
    def max_value(self):
        """Return the maximum humidity value that can be set."""
        return 140  # Set this to your desired maximum boundary value

    @property
    def step(self):
        """Return the step size of the humidity setting."""
        return 1.0

    @property
    def unit_of_measurement(self):
        """Return the unit of this entity."""
        return PERCENTAGE

    @property
    def value(self):
        """Return the current set value."""
        return self._state

    async def async_added_to_hass(self):
        """Actions to perform when the entity is added to Home Assistant."""
        self._device.humidityNumber = self
        await self._device.update_ha_devices()

    async def update_state(self):
        # Avoid writing state for disabled entities (HA 2026+ warns about this)
        if not self.enabled:
            return
        self.async_write_ha_state()

    async def async_set_value(self, value):
        """Update the configured setpoint value."""
        self._state = value
        await self._device.set_target_relative_humidity(value)
        if self.enabled:
            self.async_write_ha_state()

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Harvia number entities."""
    devices = await hass.data[DOMAIN]['api'].get_devices()
    all_numbers = []  # Use a different variable name to avoid confusion

    for device in devices:
        _LOGGER.debug(f"Loading numbers for device: {device.name}")
        device_numbers = await device.get_numbers()  # Get number entities for the current device
        all_numbers.extend(device_numbers)  # Add the number entities to the list

    async_add_entities(all_numbers, True)

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.device_registry import DeviceInfo
from .constants import DOMAIN, STORAGE_KEY, STORAGE_VERSION, REGION,_LOGGER

class HarviaHumiditySensor(SensorEntity):
    """Representation of a humidity sensor."""

    def __init__(self, device, name, sauna):
        """Initialize the humidity sensor."""
        self._name = name + ' Humidity'
        self._state = None
        self._device = device
        self._device_id = device.id + '_humidity_sensor'
        self._sauna = sauna
        self._attr_unique_id = device.id + '_humidity_sensor'
        self._attr_icon = 'mdi:water-percent'
        # Bind this entity to a Home Assistant device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.id)},
            name=getattr(device, "name", None) or name,
            manufacturer="Harvia",
            model=getattr(device, "model", None) or "Xenio WiFi",
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit used for this sensor."""
        return PERCENTAGE

    async def async_added_to_hass(self):
        """Actions to perform when the entity is added to Home Assistant."""
        self._device.humiditySensor = self
        await self._device.update_ha_devices()

    async def update_state(self):
        # Avoid writing state for disabled entities (HA 2026+ warns about this)
        if not self.enabled:
            return
        self.async_write_ha_state()


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Harvia sensors."""
    devices = await hass.data[DOMAIN]['api'].get_devices()
    all_sensors = []  # Use a different variable name to avoid confusion

    for device in devices:
        _LOGGER.debug(f"Loading sensors for device: {device.name}")
        device_sensors = await device.get_sensors()  # Get sensors for the current device
        all_sensors.extend(device_sensors)  # Add the sensors to the list

    async_add_entities(all_sensors, True)
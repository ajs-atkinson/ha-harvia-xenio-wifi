from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from .constants import DOMAIN
from homeassistant.helpers.device_registry import DeviceInfo

class SaunaReadySensor(BinarySensorEntity):
    """Sensor indicating whether the sauna is on and has reached the target temperature."""

    def __init__(self, device, name, sauna):
        self._name = name + ' Ready'
        self._ready = False  # Set by parent device
        self._device = device
        self._device_id = device.id + '_ready_sensor'
        self._sauna = sauna
        self._attr_unique_id = device.id + '_ready_sensor'
        self._attr_icon = 'mdi:check-circle-outline'
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.id)},
            name=getattr(device, "name", None) or name,
            manufacturer="Harvia",
            model=getattr(device, "model", None) or "Xenio WiFi",
        )

    @property
    def name(self):
        return self._name

    @property
    def device_class(self):
        return BinarySensorDeviceClass.POWER  # Closest fit; or None

    @property
    def is_on(self):
        """Return True if sauna is on and temp >= target."""
        return self._ready

    async def async_added_to_hass(self):
        self._device.readySensor = self
        await self._device.update_ha_devices()

    async def update_state(self):
        if not self.enabled:
            return
        self.async_write_ha_state()
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from .constants import DOMAIN
from homeassistant.helpers.device_registry import DeviceInfo

class HarviaDoorSensor(BinarySensorEntity):
    """Sensor indicating whether the Harvia sauna door is open or closed."""

    def __init__(self, device, name, sauna):
        """
        Initialize the door sensor entity for the Harvia sauna.
        The state is determined by the parent device using statusCodes[1] == 9 (open), else closed.
        """
        self._name = name + ' Door'
        self._door_open = False  # This will be set by the parent device
        self._device = device
        self._device_id = device.id + '_door_sensor'
        self._sauna = sauna
        self._attr_unique_id = device.id + '_door_sensor'
        self._attr_icon = 'mdi:door'
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
    def device_class(self):
        return BinarySensorDeviceClass.DOOR

    @property
    def is_on(self):
        """
        Return True if the door is open, False if closed.
        This is set by the parent device using statusCodes[1] == 9.
        """
        return self._door_open

    async def async_added_to_hass(self):
        """Actions to perform when the entity is added to Home Assistant."""
        self._device.doorSensor = self
        await self._device.update_ha_devices()

    async def update_state(self):
        # Avoid writing state for disabled entities (HA 2026+ warns about this)
        if not self.enabled:
            return
        self.async_write_ha_state()


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Harvia binary sensors."""
    # Retrieve the integration instance stored per config entry
    harvia = hass.data[DOMAIN][entry.entry_id]
    devices = await harvia.get_devices()

    all_binary_sensors = []

    for device in devices:
        # Let the device create and return all of its binary sensors
        device_binary_sensors = await device.get_binary_sensors()
        all_binary_sensors.extend(device_binary_sensors)

    async_add_entities(all_binary_sensors, True)

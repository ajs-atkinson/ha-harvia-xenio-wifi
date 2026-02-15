from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from .constants import DOMAIN, STORAGE_KEY, STORAGE_VERSION, REGION,_LOGGER
from homeassistant.helpers.device_registry import DeviceInfo

class HarviaDoorSensor(BinarySensorEntity):
    """Sensor indicating whether the Harvia sauna door is open or closed."""

    def __init__(self, device, name, sauna):
        """Initialize the door sensor."""
        self._name = name + ' Door'
        self._state = False
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
        return  BinarySensorDeviceClass.DOOR

    @property
    def is_on(self):
        """Return True if the sensor detects that the door is open."""
        # Harvia realtime payload provides `doorSafetyState` (bool). In observed payloads:
        #   doorSafetyState == False -> door closed
        #   doorSafetyState == True  -> door open / safety triggered
        door_state = getattr(self._device, "doorSafetyState", None)
        if door_state is None:
            return bool(self._state)
        return bool(door_state)

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
    devices = await hass.data[DOMAIN]['api'].get_devices()
    all_binary_sensors = []  # Use a different variable name to avoid confusion

    for device in devices:
        _LOGGER.debug(f"Loading binary sensors for device: {device.name}")
        device_binary_sensors = await device.get_binary_sensors()  # Get binary sensors for the current device
        all_binary_sensors.extend(device_binary_sensors)  # Add the binary sensors to the list

    async_add_entities(all_binary_sensors, True)

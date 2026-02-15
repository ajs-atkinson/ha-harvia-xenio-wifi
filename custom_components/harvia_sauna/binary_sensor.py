from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from .constants import DOMAIN
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

class HarviaSafetySwitchSensor(BinarySensorEntity):
    """Sensor indicating whether the Harvia sauna safety switch is triggered."""

    def __init__(self, device, name, sauna):
        """Initialize the safety switch sensor."""
        self._name = name + ' Safety Switch'
        self._state = False
        self._device = device
        self._device_id = device.id + '_safety_switch_sensor'
        self._sauna = sauna
        self._attr_unique_id = device.id + '_safety_switch_sensor'
        self._attr_icon = 'mdi:shield-check'
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
        # Not all HA versions have a dedicated SAFETY device_class; keep it generic.
        return None

    @property
    def is_on(self):
        """Return True if the safety switch is triggered."""
        # Use realtime fields from the device payload.
        door_safety_state = getattr(self._device, "doorSafetyState", None)
        safety_relay = getattr(self._device, "safetyRelay", None)

        # If either indicates a triggered safety condition, report ON.
        if door_safety_state is not None and door_safety_state:
            return True
        if safety_relay is not None and safety_relay:
            return True

        return False

    async def async_added_to_hass(self):
        """Actions to perform when the entity is added to Home Assistant."""
        # Store reference on the device so `update_ha_devices()` can update it.
        self._device.safetySwitchSensor = self
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

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfTime, SIGNAL_STRENGTH_DECIBELS_MILLIWATT
from homeassistant.helpers.device_registry import DeviceInfo

class GenericAttributeSensor(SensorEntity):
    """Sensor to expose a generic device attribute for diagnostics."""

    def __init__(self, device, name, attr, icon=None, unit=None):
        self._name = f"{name} {attr.replace('_', ' ').title()}"
        self._state = None
        self._device = device
        self._attr_name = attr
        self._attr_unique_id = f"{device.id}_{attr}"
        self._attr_icon = icon or 'mdi:information-outline'
        if unit:
            self._attr_native_unit_of_measurement = unit
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.id)},
            name=getattr(device, "name", None) or name,
            manufacturer="Harvia",
            model=getattr(device, "model", None) or "Xenio WiFi",
        )

    @staticmethod
    def is_enabled(device, attr):
        # Only enable if the attribute exists and is not always 0/False/empty/None
        value = getattr(device, attr, None)
        if value in (None, 0, 0.0, False, "", [], {}):
            return False
        return True

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_added_to_hass(self):
        if not hasattr(self._device, 'generic_sensors'):
            self._device.generic_sensors = {}
        self._device.generic_sensors[self._attr_name] = self
        await self._device.update_ha_devices()

    async def update_state(self):
        if not self.enabled:
            return
        self.async_write_ha_state()
class StatusCodesSensor(SensorEntity):
    """Sensor to expose the raw statusCodes value for diagnostics."""

    def __init__(self, device, name):
        self._name = name + ' Status Codes'
        self._state = None
        self._device = device
        self._attr_unique_id = device.id + '_status_codes'
        self._attr_icon = 'mdi:code-tags'
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
    def state(self):
        return self._state

    async def async_added_to_hass(self):
        self._device.statusCodesSensor = self
        await self._device.update_ha_devices()

    async def update_state(self):
        if not self.enabled:
            return
        self.async_write_ha_state()
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfTime, SIGNAL_STRENGTH_DECIBELS_MILLIWATT
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


# Additional sensors for WiFi RSSI, Remaining Time, and Stove Power
class HarviaWifiRssiSensor(SensorEntity):
    """Representation of a WiFi RSSI sensor."""

    def __init__(self, device, name):
        self._name = name + ' WiFi RSSI'
        self._state = None
        self._device = device
        self._attr_unique_id = device.id + '_wifi_rssi'
        self._attr_icon = 'mdi:wifi'
        self._attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
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
    def state(self):
        return self._state

    async def async_added_to_hass(self):
        self._device.wifiRssiSensor = self
        await self._device.update_ha_devices()

    async def update_state(self):
        if not self.enabled:
            return
        self.async_write_ha_state()


class HarviaRemainingTimeSensor(SensorEntity):
    """Representation of remaining sauna time."""

    def __init__(self, device, name):
        self._name = name + ' Remaining Time'
        self._state = None
        self._device = device
        self._attr_unique_id = device.id + '_remaining_time'
        self._attr_icon = 'mdi:timer-outline'
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
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
    def state(self):
        return self._state

    async def async_added_to_hass(self):
        self._device.remainingTimeSensor = self
        await self._device.update_ha_devices()

    async def update_state(self):
        if not self.enabled:
            return
        self.async_write_ha_state()


class HarviaStovePowerSensor(SensorEntity):
    """Representation of stove power sensor."""

    def __init__(self, device, name):
        self._name = name + ' Stove Power'
        self._state = None
        self._device = device
        self._attr_unique_id = device.id + '_stove_power'
        self._attr_icon = 'mdi:fire'
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
    def state(self):
        return self._state

    async def async_added_to_hass(self):
        self._device.stovePowerSensor = self
        await self._device.update_ha_devices()

    async def update_state(self):
        if not self.enabled:
            return
        self.async_write_ha_state()


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the Harvia sensors."""
    devices = await hass.data[DOMAIN]['api'].get_devices()
    all_sensors = []
    for device in devices:
        _LOGGER.debug(f"Loading sensors for device: {device.name}")
        device_sensors = await device.get_sensors()
        all_sensors.extend(device_sensors)
        # Add generic attribute sensors for all attributes not already covered
        from .device_attributes import attribute_list
        covered = {s._attr_name for s in device_sensors if hasattr(s, '_attr_name')}
        for attr in attribute_list:
            if attr not in covered and GenericAttributeSensor.is_enabled(device, attr):
                sensor = GenericAttributeSensor(device, getattr(device, 'name', 'Sauna'), attr)
                all_sensors.append(sensor)
    async_add_entities(all_sensors, True)
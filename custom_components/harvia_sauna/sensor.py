from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.const import (
    PERCENTAGE, SIGNAL_STRENGTH_DECIBELS_MILLIWATT, UnitOfTime,
    UnitOfTemperature, UnitOfEnergy,
)
from .constants import DOMAIN, _LOGGER
from homeassistant.components.sensor import (
    SensorEntity, SensorDeviceClass, SensorStateClass, RestoreSensor,
)

# Map raw Harvia attribute names to HA sensor metadata so the generic
# diagnostic sensors get proper device classes / units / categories.
_TEMP_ATTRS = {"temperature", "targetTemp", "maxTemp", "minTemp"}
_HUMIDITY_ATTRS = {"humidity", "targetRh"}
_DURATION_ATTRS = {"heatUpTime", "onTime", "remainingTime", "maxOnTime"}
_COUNTER_ATTRS = {
    "heatOnCounter", "heatOnCounterLT", "steamOnCounter", "steamOnCounterLT",
    "ph1RelayCounter", "ph1RelayCounterLT", "ph2RelayCounter", "ph2RelayCounterLT",
    "ph3RelayCounter", "ph3RelayCounterLT",
}
_DIAGNOSTIC_ATTRS = {
    "deviceId", "tz", "displayName", "cmd", "otaId", "online", "otaChecked",
    "serialNum", "msgId", "hwVer", "devType", "swVer", "hwProperties", "macAddr",
    "expired", "errorCodes", "testVar1", "testVar2", "timedStart", "tempUnit",
    "dehumEn", "autoLight", "autoFan", "aromaEn", "aromaLevel", "wClkEn",
    "doorSafetyState", "safetyRelay", "active", "light", "fan", "steamEn",
}


def _classify(attr):
    """Return (device_class, unit, state_class, entity_category, icon) for an attr."""
    if attr in _TEMP_ATTRS:
        return (SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, SensorStateClass.MEASUREMENT, None, "mdi:thermometer")
    if attr in _HUMIDITY_ATTRS:
        return (SensorDeviceClass.HUMIDITY, PERCENTAGE, SensorStateClass.MEASUREMENT, None, "mdi:water-percent")
    if attr in _DURATION_ATTRS:
        return (SensorDeviceClass.DURATION, UnitOfTime.MINUTES, SensorStateClass.MEASUREMENT, None, "mdi:timer-outline")
    if attr in _COUNTER_ATTRS:
        return (None, None, SensorStateClass.TOTAL_INCREASING, EntityCategory.DIAGNOSTIC, "mdi:counter")
    if attr in _DIAGNOSTIC_ATTRS:
        return (None, None, None, EntityCategory.DIAGNOSTIC, "mdi:information-outline")
    return (None, None, None, None, "mdi:information-outline")


class GenericAttributeSensor(SensorEntity):
    """Sensor to expose a generic device attribute for diagnostics."""

    def __init__(self, device, name, attr, icon=None, unit=None):
        self._name = f"{name} {attr.replace('_', ' ').title()}"
        self._state = None
        self._device = device
        self._attr_name = attr
        self._attr_unique_id = f"{device.id}_{attr}"
        dev_class, dcl_unit, state_class, category, dcl_icon = _classify(attr)
        self._attr_icon = icon or dcl_icon
        if dev_class is not None:
            self._attr_device_class = dev_class
        if state_class is not None:
            self._attr_state_class = state_class
        if category is not None:
            self._attr_entity_category = category
        if unit or dcl_unit:
            self._attr_native_unit_of_measurement = unit or dcl_unit
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



class HarviaSaunaEnergySensor(RestoreSensor):
    """Cumulative stove energy (kWh) integrated from stove power, for the Energy dashboard."""

    def __init__(self, device, name):
        self._name = name + ' Stove Energy'
        self._device = device
        self._attr_unique_id = device.id + '_stove_energy'
        self._attr_icon = 'mdi:lightning-bolt'
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._energy = 0.0
        self._last_power = None
        self._last_time = None
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
    def native_value(self):
        return round(self._energy, 3)

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        try:
            last = await self.async_get_last_sensor_data()
            if last is not None and last.native_value is not None:
                self._energy = float(last.native_value)
        except Exception:
            pass
        self._device.energySensor = self
        await self._device.update_ha_devices()

    def _effective_power(self):
        """Use real stove power if reported (>0); else fall back to rated kW while heating."""
        sp = getattr(self._device, "stovePower", None)
        try:
            sp = float(sp)
        except (TypeError, ValueError):
            sp = 0.0
        if sp and sp > 0:
            return sp
        if getattr(self._device, "heatOn", False):
            rated = getattr(getattr(self._device, "sauna", None), "rated_power_w", 0) or 0
            try:
                return float(rated)
            except (TypeError, ValueError):
                return 0.0
        return 0.0

    def accumulate(self):
        """Integrate effective stove power (W) into kWh between updates."""
        import time as _t
        now = _t.monotonic()
        p = self._effective_power()
        if self._last_time is not None and self._last_power is not None:
            dt_h = (now - self._last_time) / 3600.0
            if 0 < dt_h < 24 and self._last_power >= 0:
                self._energy += (self._last_power * dt_h) / 1000.0
        self._last_time = now
        self._last_power = p if (p is not None and p >= 0) else 0.0

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
        # Add generic attribute sensors for all attributes not already covered, except those with dedicated sensors
        from .device_attributes import attribute_list
        covered = {s._attr_name for s in device_sensors if hasattr(s, '_attr_name')}
        # Exclude attributes with dedicated sensors
        excluded_attrs = {"wifiRSSI", "statusCodes", "heatOn"}
        for attr in attribute_list:
            if attr in excluded_attrs:
                continue
            if attr not in covered and GenericAttributeSensor.is_enabled(device, attr):
                sensor = GenericAttributeSensor(device, getattr(device, 'name', 'Sauna'), attr)
                all_sensors.append(sensor)
    async_add_entities(all_sensors, True)
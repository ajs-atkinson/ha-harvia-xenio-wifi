# Harvia Sauna integration for Home Assistant

[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

Unofficial Home Assistant component for Harvia Sauna (working with Xenio Wifi), using the same API as the MyHarvia App.


## WARNING: Pre-alpha development release

*This component is still in 'pre-alpha' and can exhibit unpredictable behavior. I have tested the component for a few days now and it seems to be quite stable. I have now managed to run the component for a day without it breaking. I would appreciate it if you install the component so that I can gather information and feedback to improve the component. After all, I only have one sauna and without extensive testing it won't get better. Keep an eye on this page..* 

(updated at April 9, 2024)

Components support at the moment:

- Light switch
- Power switch (enables heater)
- Fan switch
- Termostat (current and target temp)
- Door sensor (safety circuit)

## Compatibility
Component has been tested with the Harvia Xenio Wifi (CX001WIFI) and Harvia Cilindro PC90XE, but may also work with other sauna's compatible with the MyHarvia app, as it uses the same API.

## Installation

Add a custom repository [https://github.com/brettmeyerowitz/ha-harvia-xenio-wifi/](https://github.com/brettmeyerowitz/ha-harvia-xenio-wifi/) to HACS and search for Harvia Sauna to install.
Restart Homeassistant 

## Configuration

Go to settings, integrations and add 'Harvia Sauna'
Your username and password is corresponding with the MyHarvia app.

## Credits

This integration was developed by Ruben Harms. It uses the unofficial API of Harvia Xenio WiFi controllers and is not directly associated with Harvia.

[home-assistant-harvia-sauna]: https://github.com/brettmeyerowitz/ha-harvia-xenio-wifi
[buymecoffee]: https://www.buymeacoffee.com/rubenharms
[buymecoffeebadge]: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png

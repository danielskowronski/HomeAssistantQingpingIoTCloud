# ToDo

- [x] basic integration with one config entry per device, each exposing all known reading types as sensors withing entity
- [x] ensure no deprecation warning is present as of 2025-01
- [x] cached API key (instead of re-connect each time) -> auto-reneval of token on library side
- [-] more elegant config flow to set which reading types are available in specific devices - something like in Tuya integration; maybe add some defaults or read what is device exposing on first try -> assume all data reported by device, let user disable entities or devices normally
- [x] handle property types in sync with qingping-iot-cloud
- [x] provide help and guide
- [x] clean code
- [.] validate best practices
- [ ] add binary sensor for device online/offline status
- [ ] add data recording/upload interval configuration
- [x] exclude data older than some threshold (time now, timestamp of message, polling interval)
- [x] handle total API failure (immediately set data to unavailable)
- [x] test what happens when new device is added
- [x] test what happens when sensors are added
- [.] support webhook (https://developer.qingping.co/personal/dataPushSetting) - using public nabu.casa endpoint
- [ ] webhook signature verification
- [ ] webhook support event push
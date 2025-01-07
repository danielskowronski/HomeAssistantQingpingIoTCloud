# ToDo

- [x] basic integration with one config entry per device, each exposing all known reading types as sensors withing entity
- [x] ensure no deprecation warning is present as of 2025-01
- [ ] cached API key (instead of re-connect each time)
- [ ] more elegant config flow to set which reading types are available in specific devices - something like in Tuya integration; maybe add some defaults or read what is device exposing on first try
- [ ] handle property types in sync with qingping-iot-cloud
- [ ] provide help and guide
- [ ] clean code
- [ ] validate best practices
- [ ] add binary sensor for device online/offline status?
- [ ] add data recording/upload interval configuration

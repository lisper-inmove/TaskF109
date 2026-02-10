from enum import StrEnum


class DeviceEnums(StrEnum):
    DeviceA = "Device A"
    DeviceB = "Device B"
    DeviceC = "Device C"
    DeviceD = "Device D"


class Commands(StrEnum):
    SetVoltage = "Set Voltage"
    SpeedTest = "Speed Test"


class ButtonNames(StrEnum):
    SetA = "Set A"
    SetB = "Set B"
    SetC = "Set C"
    SetD = "Set D"
    SetAll = "Set All"
    SpeedTest = "Speed Test"
    LoadCSV = "Load CSV"


BtnToDeviceMap = {
    ButtonNames.SetA: DeviceEnums.DeviceA,
    ButtonNames.SetB: DeviceEnums.DeviceB,
    ButtonNames.SetC: DeviceEnums.DeviceC,
    ButtonNames.SetD: DeviceEnums.DeviceD,
}

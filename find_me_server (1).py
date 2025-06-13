
import dbus
import dbus.mainloop.glib
from gi.repository import GLib

# Constants
BLUEZ_SERVICE_NAME = 'org.bluez'
ADAPTER_IFACE = 'org.bluez.Adapter1'
GATT_MANAGER_IFACE = 'org.bluez.GattManager1'
ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_SERVICE_IFACE = 'org.bluez.GattService1'
GATT_CHARACTERISTIC_IFACE = 'org.bluez.GattCharacteristic1'
LE_ADVERTISEMENT_IFACE = 'org.bluez.LEAdvertisement1'

IAS_UUID = '1802'
ALERT_LEVEL_UUID = '2A06'


class FindMeServer:
    def __init__(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.mainloop = GLib.MainLoop()

        self.adapter_path = self.find_adapter()
        if not self.adapter_path:
            raise Exception("No Bluetooth adapter found.")

        self.adapter = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path), ADAPTER_IFACE)
        self.adapter_props = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path),
                                            'org.freedesktop.DBus.Properties')
        self.adapter_props.Set(ADAPTER_IFACE, 'Powered', dbus.Boolean(1))

        self.app_path = '/org/bluez/example/app'
        self.service_path = f'{self.app_path}/service0'
        self.char_path = f'{self.service_path}/char0'
        self.ad_path = '/org/bluez/example/advertisement0'

        self.notifying = False

        # Register all D-Bus objects
        dbus.service.Object(self.bus, self.app_path)
        dbus.service.Object(self.bus, self.service_path)
        dbus.service.Object(self.bus, self.char_path)
        dbus.service.Object(self.bus, self.ad_path)

        self.register_app()
        self.register_advertisement()

    def find_adapter(self):
        obj = self.bus.get_object(BLUEZ_SERVICE_NAME, '/')
        mgr = dbus.Interface(obj, 'org.freedesktop.DBus.ObjectManager')
        objects = mgr.GetManagedObjects()
        for path, ifaces in objects.items():
            if ADAPTER_IFACE in ifaces:
                return path
        return None

    def register_app(self):
        service_manager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path),
                                         GATT_MANAGER_IFACE)

        @dbus.service.method('org.freedesktop.DBus.ObjectManager',
                             out_signature='a{oa{sa{sv}}}')
        def GetManagedObjects():
            return {
                dbus.ObjectPath(self.service_path): {
                    GATT_SERVICE_IFACE: {
                        'UUID': IAS_UUID,
                        'Primary': True,
                        'Characteristics': dbus.Array([dbus.ObjectPath(self.char_path)], signature='o')
                    }
                },
                dbus.ObjectPath(self.char_path): {
                    GATT_CHARACTERISTIC_IFACE: {
                        'UUID': ALERT_LEVEL_UUID,
                        'Service': dbus.ObjectPath(self.service_path),
                        'Flags': dbus.Array(['write-without-response', 'notify'], signature='s'),
                        'Notifying': dbus.Boolean(self.notifying)
                    }
                }
            }

        self.GetManagedObjects = GetManagedObjects.__get__(self)

        @dbus.service.method(GATT_CHARACTERISTIC_IFACE,
                             in_signature='aya{sv}', out_signature='')
        def WriteValue(value, options):
            if not value:
                print("[AlertLevelCharacteristic] Received empty value")
                return

            level = int(value[0])
            msg = {0: "No Alert", 1: "Mild Alert", 2: "High Alert"}.get(level, "Unknown Alert")
            print(f"[AlertLevelCharacteristic] Received alert level: {msg}")
            self.send_notification(msg)

        self.WriteValue = WriteValue.__get__(self)

        @dbus.service.method(GATT_CHARACTERISTIC_IFACE,
                             in_signature='', out_signature='')
        def StartNotify():
            self.notifying = True
            print("[AlertLevelCharacteristic] Notifications enabled")

        self.StartNotify = StartNotify.__get__(self)

        @dbus.service.method(GATT_CHARACTERISTIC_IFACE,
                             in_signature='', out_signature='')
        def StopNotify():
            self.notifying = False
            print("[AlertLevelCharacteristic] Notifications disabled")

        self.StopNotify = StopNotify.__get__(self)

        @dbus.service.signal('org.freedesktop.DBus.Properties',
                             signature='sa{sv}as')
        def PropertiesChanged(interface, changed, invalidated):
            pass

        self.PropertiesChanged = PropertiesChanged.__get__(self)

        service_manager.RegisterApplication(self.app_path, {},
            reply_handler=lambda: print("GATT application registered"),
            error_handler=lambda e: print(f"Failed to register GATT application: {e}"))

    def send_notification(self, message):
        if not self.notifying:
            print("[AlertLevelCharacteristic] Notification skipped (not notifying)")
            return
        value = [dbus.Byte(ord(c)) for c in message]
        self.PropertiesChanged(GATT_CHARACTERISTIC_IFACE,
                               {'Value': dbus.Array(value, signature='y')}, [])

    def register_advertisement(self):
        ad_manager = dbus.Interface(self.bus.get_object(BLUEZ_SERVICE_NAME, self.adapter_path),
                                    ADVERTISING_MANAGER_IFACE)

        @dbus.service.method('org.freedesktop.DBus.Properties',
                             in_signature='s', out_signature='a{sv}')
        def GetAll(interface):
            if interface != LE_ADVERTISEMENT_IFACE:
                raise dbus.exceptions.DBusException('org.freedesktop.DBus.Error.InvalidArgs',
                                                    'Invalid interface requested')
            return {
                'Type': 'peripheral',
                'ServiceUUIDs': dbus.Array([IAS_UUID], signature='s'),
                'LocalName': dbus.String("FindMe"),
                'Includes': dbus.Array(['tx-power'], signature='s')
            }

        self.GetAll = GetAll.__get__(self)

        @dbus.service.method(LE_ADVERTISEMENT_IFACE,
                             in_signature='', out_signature='')
        def Release():
            print("Advertisement released")

        self.Release = Release.__get__(self)

        ad_manager.RegisterAdvertisement(self.ad_path, {},
            reply_handler=lambda: print("BLE advertisement registered"),
            error_handler=lambda e: print(f"Failed to register advertisement: {e}"))

    def run(self):
        try:
            print("FindMe GATT server running...")
            self.mainloop.run()
        except KeyboardInterrupt:
            print("\nServer stopped by user")


if __name__ == '__main__':
    server = FindMeServer()
    server.run()

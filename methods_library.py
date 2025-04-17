import dbus
import time 

BLUEZ_SERVICE='org.bluez'
BLUEZ_ADAPTER= 'org.bluez.Adapter1'
BLUEZ_DEVICE='org.bluez.Device1'

class BluetoothManager:
    def __init__(self):
        self.system_bus=dbus.SystemBus()
        self.obj_manager=self.system_bus.get_object(BLUEZ_SERVICE,'/')
        self.obj_ic=dbus.Interface(self.obj_manager,'org.freedesktop.DBus.ObjectManager')
        self.list_devices() 
        self.adapter_obj=self.system_bus.get_object(BLUEZ_SERVICE,self.adapter_path)
        self.adapter_ic=dbus.Interface(self.adapter_obj,BLUEZ_ADAPTER)
        self.prop_ic=dbus.Interface(self.adapter_obj,'org.freedesktop.DBus.Properties')
        self.agent_obj=self.system_bus.get_object(BLUEZ_SERVICE,'/org/bluez')
        self.agent_ic=dbus.Interface(self.agent_obj,'org.bluez.AgentManager1')
        

    def list_devices(self):
        '''
        Fetching adapter path and storing the discovered devices' name,address and path in devices[]

        returns: the devices[] list
        '''
        managed_objects=self.obj_ic.GetManagedObjects()
        devices=[]
        for path, interfaces in managed_objects.items():
                if BLUEZ_DEVICE in interfaces:
                        device=interfaces[BLUEZ_DEVICE]
                        name=device.get('Name','Unknown')
                        address=device.get('Address','Unknown')
                        self.adapter_path=device['Adapter']
                        devices.append((path,name,address))
        return devices 

    def get_property(self):
        '''
        Retrieve specific property of adapter interface and its current value
        '''
        property_name=input('Enter the name of property:')
        property_value=self.prop_ic.Get(BLUEZ_ADAPTER,property_name)
        print(f'{property_name}:{property_value}')

    
    def set_property(self):
        '''
        Modify the value of specific property
        '''
        property_name=input('Enter the name of property you want to set:')
        value_type=input('Enter the type of value (string,boolean,int32,uint32..etc)')
        value=input('Enter the value:')

        if value_type =='boolean':
                value=value.lower() in ['True','1']
                variant1=dbus.Boolean(value)
        else:
                variant1=dbus.String(value)
        self.prop_ic.Set(BLUEZ_ADAPTER,property_name,variant1)
        
    
    def start_discovery(self):
        '''
        Initiates bluetooth discovery process
        '''
        self.adapter_ic.StartDiscovery()
        print('Started scanning for devices...')
        time.sleep(10)

        managed_objects=self.obj_ic.GetManagedObjects()
        for path, interfaces in managed_objects.items():
                if BLUEZ_DEVICE in interfaces:
                        device=interfaces[BLUEZ_DEVICE]
                        name=device.get('Name','Unknown')
                        address=device.get('Address','Unknown')
                        print(f'Discovered device: {name} : [{address}]')
        self.adapter_ic.StopDiscovery()

    def get_device_interface(self,device_address):
        '''
        Creating device interface for specific devices to access the methods 
        args : Bluetooth address of the device
        '''
        devices=self.list_devices()

        device_path=None
        for path,name,address in devices:
                if address == device_address:
                        device_path=path
                        break

        device_obj=self.system_bus.get_object(BLUEZ_SERVICE,device_path)
        device_ic=dbus.Interface(device_obj,BLUEZ_DEVICE)
        return device_ic

    def pair_device(self,device_address):
        '''
        Initiate the pairing process

        args : Bluetooth address of the device you want to pair
        '''
        device_ic=self.get_device_interface(device_address)
        device_ic.Pair()
        print('Pairing completed..')
    
    def connect_profile(self,device_address):
        '''
        connects a Bluetooth device to a specific Bluetooth profile identified by its UUID 

        args : Bluetooth address of the device
        '''
        device_ic=self.get_device_interface(device_address)
        profile_uuid=input('Enter the UUID of the profile you want to connect:')
        device_ic.ConnectProfile(profile_uuid)
        print('profile connected....')

    def register_agent(self):
        '''
        registers a custom agent with BlueZ to handle Bluetooth pairing and authorization requests
        '''
        time.sleep(2)
        self.agent_ic.RegisterAgent('/org/bluez','NoInputNoOutput')
        print('Agent registered')

    def default_agent(self):
        '''
        Sets a previously registered Bluetooth agent as the default agent
        '''
        self.agent_ic.RequestDefaultAgent('/org/bluez')
        print('Default agent request successful')

    def unregister_agent(self):
        '''
        Unregisters a previously registered Bluetooth agent 
        '''
        self.agent_ic.UnregisterAgent('/org/bluez')
        print('Agent unregistered')

    def connect(self,device_address):
        '''
        Initiates a connection to a Bluetooth device 
        '''
        device_ic=self.get_device_interface(device_address)
        device_ic.Connect()
        print('Connected...')

    def disconnect(self,device_address):
        '''
        Disconnects an active Bluetooth connection to a remote device 
        '''
        device_ic=self.get_device_interface(device_address)
        device_ic.Disconnect()
        print('Disconnected..')

    def remove_device(self):
        '''
        Removes a previously paired or known Bluetooth device from the system
        '''
        managed_objects=self.obj_ic.GetManagedObjects()
        print('Paired devices---')
        for paths,interfaces in managed_objects.items():
                if BLUEZ_DEVICE in interfaces:
                        device=interfaces[BLUEZ_DEVICE]
                        if device['Paired'] == True:
                                print(device['Address'])
        device_address=input('Enter the BD-address of the device you want to remove:')
        device_path=f"{self.adapter_path}/dev_{device_address.replace(':','_')}"
        self.adapter_ic.RemoveDevice(device_path) 
 
        
    def media_player(self):
        '''
        Provides more detailed interaction with the specific mediaplayer  (obtain metadata and read/write properties)
        '''
        managed_objects=self.obj_ic.GetManagedObjects()
        for path,interfaces in managed_objects.items():
                if 'org.bluez.MediaPlayer1' in interfaces:
                        media_path=path
        media_obj=self.system_bus.get_object(BLUEZ_SERVICE,media_path)
        media_ic=dbus.Interface(media_obj,'org.bluez.MediaPlayer1')
        props_ic=dbus.Interface(media_obj,'org.freedesktop.DBus.Properties')
        while True:
            user_input=input('Choose an option: 1.Get property 2.Set property 3.Play 4.Pause 5.Exit :')
            if user_input == '1':
                property_name=input('Enter the name of property:')
                property_value=props_ic.Get('org.bluez.MediaPlayer1',property_name)
                print(f"{property_name}:{property_value}")
            elif user_input == '2':
                prop_name=input('Enter the name of property you want to change:')
                prop_value=input('Enter the value:')
                props_ic.Set('org.bluez.MediaPlayer1',prop_name,prop_value)
            elif user_input == '3':
                media_ic.Play()
            elif user_input == '4':
                media_ic.Pause()
            elif user_input == '5':
                break

    def media_control(self,device_address):
        '''
        Provides basic playback controls for media on remote device
        '''
        devices=self.list_devices()

        device_path=None
        for path,name,address in devices:
                if address == device_address:
                        device_path=path
                        break

        device_obj=self.system_bus.get_object(BLUEZ_SERVICE,device_path)
        device_ic=dbus.Interface(device_obj,'org.bluez.MediaControl1')
        while True:
            user_in=input('1.Start playing 2.Next 3.Stop playing 4.Exit...: ')
            if user_in == '1':
                device_ic.Play()
            
            elif user_in == '2':
                device_ic.Next()
    
            elif user_in == '3':
                device_ic.Pause()
            elif user_in == '4':
                break


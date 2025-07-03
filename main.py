from methods_library import BluetoothManager

BT_Manager=BluetoothManager()
while True:
        print('Choose an option:')
        print('1.Discover bluetooth devices')
        print('2.Pair with a device')
        print('3.Get properties')
        print('4.Set properties')
        print('5.register agent')
        print('6.Default agent')
        print('7.Unregister agent')
        print('8.Connect to a device')
        print('9.Connect profile')
        print('10.Media control')
        print('11.Disconnect device')
        print('12.Remove device')
        print('13.Media player')
        print('14.Exit')

        user_input=input('Enter your choice: ')
        if user_input == '1':
                BT_Manager.start_discovery()
        elif user_input == '2':
                device_address=input('Enter the BD_address of the device you wish to pair: ')
                BT_Manager.pair_device(device_address)
        elif user_input == '3':
                BT_Manager.get_property()
        elif user_input == '4':
                BT_Manager.set_property()
        elif user_input == '5':
                BT_Manager.register_agent()
        elif user_input == '6':
                BT_Manager.default_agent()
        elif user_input == '7':
                BT_Manager.unregister_agent()
        elif user_input =='8':
                device_addr=input('Enter the BD_address of the device you want to connect: ')
                BT_Manager.connect(device_addr)
        elif user_input == '9':
                device_addr=input('Enter the device Bd_addr:')
                BT_Manager.connect_profile(device_addr)
        elif user_input =='10':
                device_addr=input('Enter the device bd_addr:')
                BT_Manager.media_control(device_addr)
        elif user_input =='11':
                device_addr=input('Enter the Bd_addr:')
                BT_Manager.disconnect(device_addr)
        elif user_input == '12':
                BT_Manager.remove_device()
        elif user_input == '13':
                BT_Manager.media_player()
        elif user_input == '14':
                break

def start_bluetoothd_logs(self, log_text_browser=None):
    self.bluetoothd_log_name = os.path.join(self.log_path, "bluetoothd.log")

    # PREVENT OLD PROCESSES
    subprocess.run("pkill -f bluetoothd", shell=True)
    time.sleep(1)

    bluetoothd_command = '/usr/local/bluez/bluez-tools/libexec/bluetooth/bluetoothd -nd --compat'
    print(f"[INFO] Starting bluetoothd logs...{bluetoothd_command}")
    self.bluetoothd_process = subprocess.Popen(
        bluetoothd_command.split(),
        stdout=open(self.bluetoothd_log_name, 'a+'),
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True
    )
    time.sleep(1)

    self.bluetoothd_logfile_fd = open(self.bluetoothd_log_name, 'r')
    self.bluetoothd_file_position = self.bluetoothd_logfile_fd.tell()

    if log_text_browser is not None:
        self.bluetoothd_log_reader = HcidumpLogReader(self.bluetoothd_log_name)
        self.bluetoothd_log_reader.log_updated.connect(log_text_browser.append)
        self.bluetoothd_log_reader.start()

    print(f"[INFO] Bluetoothd logs started: {self.bluetoothd_log_name}")
    return True


def start_pulseaudio_logs(self, log_text_browser=None):
    self.pulseaudio_log_name = os.path.join(self.log_path, "pulseaudio.log")

    # PREVENT OLD PROCESSES
    subprocess.run("pkill -f pulseaudio", shell=True)
    time.sleep(1)

    pulseaudio_command = '/usr/local/bluez/pulseaudio-13.0_for_bluez-5.65/bin/pulseaudio -vvv'
    print(f"[INFO] Starting pulseaudio logs...{pulseaudio_command}")
    self.pulseaudio_process = subprocess.Popen(
        pulseaudio_command.split(),
        stdout=open(self.pulseaudio_log_name, 'a+'),
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True
    )
    time.sleep(1)

    self.pulseaudio_logfile_fd = open(self.pulseaudio_log_name, 'r')
    self.pulseaudio_file_position = self.pulseaudio_logfile_fd.tell()

    if log_text_browser is not None:
        self.pulseaudio_log_reader = HcidumpLogReader(self.pulseaudio_log_name)
        self.pulseaudio_log_reader.log_updated.connect(log_text_browser.append)
        self.pulseaudio_log_reader.start()

    print(f"[INFO] Pulseaudio logs started: {self.pulseaudio_log_name}")
    return True


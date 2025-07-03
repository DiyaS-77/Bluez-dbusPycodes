
def start_pulseaudio_logs(self, log_text_browser=None):
    """Start pulseaudio logs and optionally stream to QTextBrowser"""
    try:
        self.pulseaudio_log_name = os.path.join(self.log_path, "pulseaudio.log")
        pulseaudio_command = "/usr/local/bluez/pulseaudio-13.0_for_bluez-5.65/bin/pulseaudio -vvv"

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

    except Exception as e:
        print(f"[ERROR] Failed to start pulseaudio logs: {e}")
        return False

def stop_pulseaudio_logs(self):
    print("[INFO] Stopping pulseaudio logs...")

    if hasattr(self, 'pulseaudio_log_reader') and self.pulseaudio_log_reader:
        self.pulseaudio_log_reader.stop()
        self.pulseaudio_log_reader = None

    if self.pulseaudio_logfile_fd:
        self.pulseaudio_logfile_fd.close()
        self.pulseaudio_logfile_fd = None

    if hasattr(self, 'pulseaudio_process') and self.pulseaudio_process:
        try:
            self.pulseaudio_process.terminate()
            self.pulseaudio_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.pulseaudio_process.kill()
            self.pulseaudio_process.wait()
        self.pulseaudio_process = None
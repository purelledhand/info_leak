from __future__ import print_function
import argparse
import datetime
from io import StringIO
import struct
from utility.tskutil import TSKUtil
import pytsk3
from Registry import Registry


def main(evidence, image_type):
    print("[+] Opening {}".format(evidence))
    if image_type == "ewf":
        try:
            filenames = pyewf.glob(evidence)
        except IOError:
            _, e, _ = sys.exc_info()
            print("[-] Invalid EWF format:\n {}".format(e))
            sys.exit(2)
        ewf_handle = pyewf.handle()
        ewf_handle.open(filenames)
        img_info = EWFImgInfo(ewf_handle)
    else:
        img_info = pytsk3.img_info(evidence)

    tsk_util = TSKUtil(evidence, image_type)
    tsk_system_hive = tsk_util.recurse_files('system', '/Windows/system32/config', 'equals')
    tsk_software_hive = tsk_util.recurse_files('software', '/Windows/system32/config', 'equals')

    system_hive = open_file_as_reg(tsk_system_hive[0][2])
    software_hive = open_file_as_reg(tsk_software_hive[0][2])

    process_system_hive(system_hive)
    process_software_hive(software_hive)

class EWFImgInfo(pytsk3.img_info):
    def __init__(self, ewf_handle):
        self._ewf_handle = ewf_handle
        super(EWFImgInfo, self).__init__(url="", type=pytsk3.TSK_IMG_TYPE_EXTERNAL)
    def close(self):
        self._ewf_handle.close()
    def read(self, offset, size):
        self._ewf_handle.seek(offset)
        return self._ewf_handle.read(size)
    def get_size(self):
        return self._ewf_handle.get_media_size()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('EVIDENCE_FILE', help="Path to evidence file")
    args = parser.parse_args()
    main(args.EVIDENCE_FILE, "raw")

def open_file_as_reg(reg_file):
    file_size = reg_file.info.meta.size
    file_content = reg_file.read_random(0, file_size)
    file_like_obj = StringIO.StringIO(file_content)
    return Registry.Registry(file_like_obj)

def process_system_hive(hive):
    root = hive.root()
    current_control_set = root.find_key("Select").value("Current").value()
    control_set = root.find_key("ControlSet{:03d}".format(current_control_set))
    raw_shutdown_time = struct.unpack('<Q', control_set.find_key("Control").find_key("Windows").value("ShutdownTime").value())
    shutdown_time = parse_windows_filetime(raw_shutdown_time[0])
    print("Last Shutdown Time: {}".format(shutdown_time))

    time_zone = control_set.find_key("Control").find_key("TimeZoneInformation").value("TimeZoneKeyName").value()
    print("Machine Time Zone: {}".format(time_zone))

    computer_name = control_set.find_key("Control").find_key("ComputerName").find_key("ComputerName").value("ComputerName").value()
    print("Machine Name: {}".format(computer_name))

    last_access = control_set.find_key("Control").find_key("FileSystem").value("NtfsDisableLastAccessUpdate").value()
    last_access = "Disabled" if last_access == 1 else "enabled"
    print("Last Access Updates: {}".format(last_access))


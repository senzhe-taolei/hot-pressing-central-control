import time
import snap7
from utils import plc_read_utils, plc_write_utils, plc_utils, plc_read_universal, redis_utils
from config.ip_list import ip_list
from config.yeya_sites import yeya_sites
from config import conf


class YeYa:

    def __init__(self):
        self.plc = plc_utils.get_plc_connection(ip_list["液压站"])
        self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)

        pass

    def __del__(self):
        self.plc.disconnect()
        self.plc.destroy()

    def yeya_start(self):
        address1 = yeya_sites["低压泵启动"]["Address"]
        plc_write_utils.plc_write(self.plc, address1, str(1))

        address2 = yeya_sites["高压泵启动"]["Address"]
        plc_write_utils.plc_write(self.plc, address2, str(1))
        time.sleep(2)
        plc_write_utils.plc_write(self.plc, address1, str(0))
        plc_write_utils.plc_write(self.plc, address2, str(0))

        address3 = yeya_sites["油冷机启动"]["Address"]
        plc_write_utils.plc_write(self.plc, address3, str(1))

    def yeya_stop(self):
        address1 = yeya_sites["低压泵停止"]["Address"]
        plc_write_utils.plc_write(self.plc, address1, str(1))
        address2 = yeya_sites["高压泵停止"]["Address"]
        plc_write_utils.plc_write(self.plc, address2, str(1))
        time.sleep(2)
        plc_write_utils.plc_write(self.plc, address1, str(0))
        plc_write_utils.plc_write(self.plc, address2, str(0))

        address3 = yeya_sites["油冷机停止"]["Address"]
        plc_write_utils.plc_write(self.plc, address3, str(1))

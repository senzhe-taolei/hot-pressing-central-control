import time
import snap7
from utils import plc_utils, plc_read_universal, redis_utils, common
from config.ip_list import ip_list
from config.yeya_sites import yeya_sites
from config import conf, const


class YeYaListen:

    def __init__(self):
        self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)
        self.plc = None
        pass

    def yeya_loop_read_all_sites(self):
        while True:
            try:
                self.plc = plc_utils.get_plc_connection(ip_list["液压站"])
                data = self.plc.read_area(snap7.client.Areas.DB, 13, 0, 374)
                data_dict = plc_read_universal.split_address_values(yeya_sites, data)
                key = f"device_listen:{conf.device_name}:yeya"
                update_time = int(time.time() * 1000)
                data_dict["update_time"] = update_time
                self.redis_local_db.redis_hmset(key, data_dict)
                if conf.left_or_right == const.RIGHT:
                    self.redis_server_db.redis_hmset(key, data_dict)
            except Exception as e:
                print(e)
            finally:
                common.close_plc(self.plc)


if __name__ == "__main__":
    YeYaListen().yeya_loop_read_all_sites()

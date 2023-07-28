import time
import modbus_tk.defines as cst
from utils import redis_utils
from config import conf
from utils.modbus_utils import ModbusTcpUtils
from config.chengliao_sites import *
from config.ip_list import ip_list


class ChengLiaoListen:

    def __init__(self):

        self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)

    # 读取所有值
    def chengliao_loop_read_all_sites(self):
        while True:
            if conf.left_or_right == "left":
                left_right = {
                    "main:l": ModbusTcpUtils(ip_list["称料主左"]),
                    "auxiliary:l": ModbusTcpUtils(ip_list["称料辅左"]),
                }
            elif conf.left_or_right == "right":
                left_right = {
                    "main:r": ModbusTcpUtils(ip_list["称料主右"]),
                    "auxiliary:r": ModbusTcpUtils(ip_list["称料辅右"]),
                }
            else:
                raise

            for key, master in left_right.items():
                read_value_dict = {}
                write_value_dict = {}
                # read
                all_value_read = master.execute(1, cst.READ_HOLDING_REGISTERS, 2200, 26)  # todo 还是13
                bool_str = bin(all_value_read[0])[2:].zfill(16)
                bool_str_list = list(bool_str)
                for name, site in chengliao_read_sites:
                    address = site["Address"]
                    if address != "2200":
                        read_value_dict["工作完成数量"] = all_value_read[2]
                        read_value_dict["放料口已开口信号"] = all_value_read[24]
                        continue
                    if "." not in address:
                        raise
                    bit_addr = address.split(".")[1]
                    read_value_dict[name] = bool_str_list[-(int(bit_addr) + 1)]

                # write
                all_value_write = master.execute(1, cst.READ_HOLDING_REGISTERS, 2300, 16)
                for name, site in chengliao_write_sites:
                    address = site["Address"]
                    if address != "2300":
                        write_value_dict["工作重量设定-设置"] = all_value_write[4]
                        write_value_dict["工作工位设定-设置"] = all_value_write[6]
                        write_value_dict["物料剔除重量设定-设置"] = all_value_write[8]
                        write_value_dict["投料器取料号-设置"] = all_value_write[10]
                        write_value_dict["第1次放料开门时间-设置"] = all_value_write[12]
                        write_value_dict["第2次放料开门时间-设置"] = all_value_write[14]
                        continue
                    if "." not in address:
                        raise
                    bool_str = bin(all_value_write[0])[2:].zfill(16)
                    bool_str_list = list(bool_str)
                    bit_addr = address.split(".")[1]
                    write_value_dict[name] = bool_str_list[-(int(bit_addr) + 1)]
                key_base = conf.device_name + ":chengliao:" + key

                data_dict = write_value_dict | read_value_dict
                data_dict["update_time"] = int(time.time() * 1000)
                self.redis_local_db.redis_hmset(key_base, data_dict)
                self.redis_server_db.redis_hmset(key_base, data_dict)


if __name__ == "__main__":
    # 监听称料
    ChengLiaoListen().chengliao_loop_read_all_sites()

import time
import re
import snap7
from snap7.util import *
from utils import plc_read_universal, plc_read_utils, plc_write_utils, plc_utils, redis_utils
from config.robot_sites import *
from config.ip_list import ip_list
from config import conf, const
from utils.common import plc_bool_write


class RobotListen:
    def __init__(self, ):
        self.plc = plc_utils.get_plc_connection(ip_list["机械手"])
        self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)
        self.loop_read_sites_time = 0

        pass

    # 循环监听
    def robot_loop_read_all_sites(self):
        while True:
            if conf.left_or_right == const.LEFT:
                robot_sites = robot_left_sites
                robot_key_name = conf.device_name + ":robot:l"

            elif conf.left_or_right == const.RIGHT:
                robot_sites = robot_right_sites
                robot_key_name = conf.device_name + ":robot:r"
            else:
                raise

            # todo 滕工给的点位有问题尚需修改
            # robot_sites_left/right 511
            data1 = self.plc.read_area(snap7.client.Areas.DB, 511, 0, 548)
            read_dict = plc_read_universal.split_address_values(robot_sites, data1)

            if conf.left_or_right == const.LEFT:
                # robot_status_read_left_sites
                data2 = self.plc.read_area(snap7.client.Areas.DB, 500, 0, 1)
                status_read_dict = plc_read_universal.split_address_values(robot_left_status_read_sites, data2)
            else:
                # robot_status_read_right_sites
                data2 = self.plc.read_area(snap7.client.Areas.DB, 500, 274, 1)
                # 因为用的是旧数据，所以启动状态点位不同DB501.DBX116.0，
                status_read_site_1 = {key: val for key, val in robot_right_status_read_sites.items() if key != "启动状态-实时"}
                status_read_dict_1 = plc_read_universal.split_address_values(status_read_site_1, data2, 274)

                status_read_site_2 = {key: val for key, val in robot_right_status_read_sites.items() if key == "启动状态-实时"}
                status_read_dict_2 = plc_read_universal.split_address_values(status_read_site_2, data1)

                status_read_dict = status_read_dict_1 | status_read_dict_2


            # # robot_status_write_left_sites
            # data = self.plc.read_area(snap7.client.Areas.DB, 503, 22, 1)
            # left_status_write_dict = plc_read_universal.split_address_values(robot_status_write_left_sites, data, 22)

            # # robot_status_write_right_sites
            # data = self.plc.read_area(snap7.client.Areas.DB, 5033, 22, 1)
            # right_status_write_dict = plc_read_universal.split_address_values(robot_status_write_right_sites, data, 22)

            data_dict = read_dict | status_read_dict
            data_dict["update_time"] = int(time.time()*1000)
            self.redis_local_db.redis_hmset(robot_key_name, data_dict)

            self.redis_server_db.redis_hmset(robot_key_name, data_dict)

            time_diff = time.time() - self.loop_read_sites_time
            self.loop_read_sites_time = time.time()
            print(time_diff)
            # self.redis_local_db


if __name__ == "__main__":
    RobotListen().robot_loop_read_all_sites()

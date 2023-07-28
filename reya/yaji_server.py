import json
import time
import sys
from copy import deepcopy
from utils import redis_utils, common, plc_utils, plc_read_utils, logger
from config import conf, const
from config.yaji_sites import *
from config.ip_list import ip_list
from robot import Robot


class YaJiServer:
    def __init__(self, station):
        self.station = station
        self.redis_key = conf.device_name + ":yaji:0" + str(station)

        if station == 1:
            self.yaji_sites_read = yaji_1_sites_read
            self.yaji_sites_write = yaji_1_sites_write
        elif station == 2:
            self.yaji_sites_read = yaji_2_sites_read
            self.yaji_sites_write = yaji_2_sites_write
        elif station == 3:
            self.yaji_sites_read = yaji_3_sites_read
            self.yaji_sites_write = yaji_3_sites_write
        elif station == 4:
            self.yaji_sites_read = yaji_4_sites_read
            self.yaji_sites_write = yaji_4_sites_write
        else:
            raise
        if conf.left_or_right == const.LEFT:
            self.yaji_ip = ip_list["压机左"]
        else:
            self.yaji_ip = ip_list["压机右"]

        self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)

        self.plc = None

    def __del__(self):
        pass

    def get_station_plan_info(self):
        plan_id = self.redis_local_db.redis_hget(conf.redis_station_working_info_key,
                                                           self.station)
        self.redis_local_db.redis_hdel(conf.redis_station_working_info_key,
                                                           self.station)
        plan_info = self.redis_server_db.redis_hgetall(f"production_plan:{plan_id}")
        return plan_info

    def yaji_action_listen(self):
        station_status = 6
        station_status_address = self.yaji_sites_read["工位状态-实时"]["Address"]
        while True:
            try:
                self.plc = plc_utils.get_plc_connection(self.yaji_ip)
                station_status_new = plc_read_utils.plc_read_alone(self.plc, station_status_address)
                station_old = station_status
                station_status = station_status_new

                # 压制完成
                if station_status_new == 6 and station_old == 5:
                    # 计数，压机完成+腔数
                    plan_info = self.get_station_plan_info()
                    plan_id = plan_info["plan_id"]
                    finish_num = plan_info["完成数量"] + plan_info["模具腔数"]
                    #
                    self.redis_local_db.redis_hset(conf.redis_plan_local_info.format(plan_id), "完成数量", finish_num)
                    self.redis_server_db.redis_hset(f"production_plan:{plan_id}", "完成数量", finish_num)
                    pass

                time.sleep(0.5)
            except Exception as e:
                print(e)
            finally:
                common.close_plc(self.plc)


if __name__ == "__main__":
    # 启动1-4号压机，python3 yaji_server.py 1, python3 yaji_server.py 2,
    # python3 yaji_server.py 3, python3 yaji_server.py 4,
    args = sys.argv
    if len(args) < 2 and args[1] not in ["1", "2", "3", "4"]:
        # logger().error("参数错误", args)
        raise(Exception("参数错误"))
    else:
        YaJiServer(int(args[1])).yaji_action_listen()

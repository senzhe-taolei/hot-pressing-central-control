import time

import snap7
from snap7.util import *
from utils import plc_read_universal, plc_read_utils, plc_write_utils, plc_utils, redis_utils
from config.robot_sites import *
from config.ip_list import ip_list
from config import conf, const
from utils.common import plc_bool_write


class Robot:
    def __init__(self, ):
        self.plc = plc_utils.get_plc_connection(ip_list["机械手"])
        self.mvju_type = None
        self.workstation = None
        self.l_or_r = None
        self.robot_sites = None
        # if left_or_right == "left":
        #     self.robot_sites = robot_left_sites
        #     self.robot_status_read_sites = robot_left_status_read_sites
        # elif left_or_right == "right":
        #     self.robot_sites = robot_right_sites
        #     self.robot_status_read_sites = robot_right_status_read_sites
        # else:
        #     self.robot_sites = None
        #     self.robot_status_read_sites = None

        self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)

        self.loop_read_sites_time = 0

        pass

    def __del__(self):
        self.plc.destroy()

    def init(self):
        # 写申请参数 1
        self.set_write_param_status()

    def set_write_param_status(self):
        addr1 = self.robot_sites["申请参数"]["Address"]
        res2 = plc_write_utils.plc_write(self.plc, addr1, str(1))

    def get_write_param_status(self):
        addr1 = self.robot_sites["申请参数"]["Address"]
        result = plc_read_utils.plc_read_alone(self.plc, addr1)
        print("get_write_param_status", result)
        return result

    def set_params(self):

        # params = {
        #     "磨具类型": 2,
        #     "工作位": 3,
        # }
        # for key in params:
        addr1 = self.robot_sites["磨具类型"]["Address"]
        res1 = self.write_mujv_type(addr1, self.mvju_type)
        addr2 = self.robot_sites["工作位"]["Address"]
        res2 = plc_write_utils.plc_write(self.plc, addr2, str(1))
        pass

    def robot_start_reset(self):
        address = self.robot_sites["启动"]["Address"]
        plc_bool_write(self.plc, address, '1', 500)
        pass

    def robot_action(self):
        address = self.robot_sites["启动"]["Address"]
        plc_write_utils.plc_write(self.plc, address, str(1))

    def robot_reset(self):
        address = self.robot_sites["启动"]["Address"]
        plc_write_utils.plc_write(self.plc, address, str(0))

    def read_mujv_type(self, address):
        db_num, byte_index = self.get_dbd_indexs(address)
        data = self.plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 4)
        type = int.from_bytes(data[:2], 'big')
        return type

    def write_mujv_type(self, address, type=2):
        db_num, byte_index = self.get_dbd_indexs(address)
        val_step1 = struct.pack('>i', type)
        val = val_step1[2:4] + val_step1[:2]
        res = self.plc.write_area(snap7.client.Areas.DB, db_num, byte_index, val)
        print(res)

    def get_dbd_indexs(self, address):
        match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', address, re.I)
        x = int(match_value_index.group(2))  # 获取db点db区位置编号
        y = int(match_value_index.group(5))  # 获取db点byte位置编号
        return x, y

    def finish_status(self):
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
            data = self.plc.read_area(snap7.client.Areas.DB, 511, 0, 548)
            # left_read_dict = plc_read_universal.split_address_values(robot_left_sites, data)
            # right_read_dict = plc_read_universal.split_address_values(robot_right_sites, data)
            read_dict = plc_read_universal.split_address_values(robot_sites, data)

            if conf.left_or_right == const.LEFT:
                # robot_status_read_left_sites
                data = self.plc.read_area(snap7.client.Areas.DB, 500, 0, 1)
                status_read_dict = plc_read_universal.split_address_values(robot_left_status_read_sites, data)
            else:
                # robot_status_read_right_sites
                data = self.plc.read_area(snap7.client.Areas.DB, 5033, 22, 1)
                status_read_dict = plc_read_universal.split_address_values(robot_right_status_read_sites, data, 22)

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
    Robot().robot_loop_read_all_sites()

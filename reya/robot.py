import time
import re
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

        if conf.left_or_right == const.LEFT:
            self.robot_sites = robot_left_sites
            self.robot_status_read_sites = robot_left_status_read_sites
        elif conf.left_or_right == const.RIGHT:
            self.robot_sites = robot_right_sites
            self.robot_status_read_sites = robot_right_status_read_sites
        else:
            raise

        self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)

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

    # 检测 申请参数 是否为1
    def detect_request(self):
        while True:
            result = plc_read_utils.detect_plc_status(self.plc, self.robot_sites["申请参数"]["Address"], 1)
            if result:
                break
        return True

    # 机械臂任务开始流程
    def robot_proc(self, params):
        # 监听 申请参数 是否为 1
        self.detect_request()
        # write params
        for name in params:
            address = self.robot_sites[name]["Address"]
            data_type = self.robot_sites[name]["DataType"]
            if name == "模具类型":
                muju_type = params["模具类型"].split('-')[1]
                self.write_mujv_type(address, int(muju_type))
                continue
            if data_type.lower() == "real":
                result = plc_write_utils.plc_write(self.plc, address, str(params[name]), date_type='float')
            else:
                result = plc_write_utils.plc_write(self.plc, address, str(params[name]))
            print(name + ":" + str(result))
            pass

        # start
        self.robot_start_reset()

    def set_params(self, params):

        # params = {
        #     "磨具类型": 2,
        #     "工作位": 3,
        # }
        # for key in params:
        addr1 = self.robot_sites["模具类型"]["Address"]
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


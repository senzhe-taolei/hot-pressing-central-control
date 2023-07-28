import asyncio
import time
from copy import deepcopy
import modbus_tk.defines as cst
from utils import redis_utils
from config import conf
from utils.modbus_utils import ModbusTcpUtils
from config.chengliao_sites import *
from config.ip_list import ip_list


class ChengLiao:

    def __init__(self):

        self.main_master = None
        self.auxiliary_master = None

        # self.loop = asyncio.get_event_loop()
        # self.main_master_left = ModbusTcpUtils(ip_list["称料主左"])
        # self.auxiliary_master_left = ModbusTcpUtils(ip_list["称料辅左"])
        # self.main_master_right = ModbusTcpUtils(ip_list["称料主右"])
        # self.auxiliary_master_right = ModbusTcpUtils(ip_list["称料辅右"])

        # self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        # self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)

        self.hole_num = 0
        pass

    def init(self):
        # 初始时现将所有状态清零
        self.main_master.write_single_register(chengliao_write_action_status_addr, 0)
        self.auxiliary_master.write_single_register(chengliao_write_action_status_addr, 0)
        # 称重联动on开启
        addr = chengliao_write_sites["称重联动on"]["Address"]
        self.main_master.set_db_bool(addr, 1)
        self.auxiliary_master.set_db_bool(addr, 1)
        pass

    def set_params(self, params):
        # # 主料投料量  辅料投料量
        # if "主料投料量" not in params or params["主料投料量"] <= 0:
        #     return False, "称料，主料投料量参数错误"
        # if "辅料投料量" not in params or params["辅料投料量"] <= 0:
        #     return False, "称料，辅料投料量参数错误"
        # if "工作工位设定" not in params or params["工作工位设定"] <= 0 or params["工作工位设定"] > 8:
        #     return False, "称料，工作工位设定参数错误"
        # 设定腔数
        if "模具腔数" in params and params["模具腔数"]:
            self.hole_num = params["模具腔数"]

        data_base = {
            "工作工位设定": params["工作工位设定"],
            # "物料剔除": 0,
            "第1次放料开门时间": params.get("第1次放料开门时间", 15),
            "第2次放料开门时间": params.get("第2次放料开门时间", 0),
        }
        main_data = deepcopy(data_base)
        main_data["工作重量设定"] = params["主料投料量"]
        # 主料
        res1 = self.set_param_main_or_auxiliary(self.main_master, main_data)
        # 辅料
        auxiliary_data = deepcopy(data_base)
        auxiliary_data["工作重量设定"] = params["辅料投料量"]
        res2 = self.set_param_main_or_auxiliary(self.auxiliary_master, auxiliary_data)
        if not res1 or not res2:
            return False

    def set_param_main_or_auxiliary(self, master, data):
        for key in data:
            addr = chengliao_write_sites[key]["Address"]
            res = master.write_single_register(addr, data[key])
        return True

    def drop_material(self):
        pass

    # 称料逻辑
    def chengliao_single(self, master):
        print('333333')
        addr = chengliao_read_sites["允许称重"]["Address"]
        wait_status = master.detect_wait_bool2(addr, True, 10)
        if not wait_status:
            print("允许称重 err")
        print('iiiisss')
        addr = chengliao_write_sites["称重on"]["Address"]
        master.set_db_bool(addr, 1)
        print('iiiisss5555')
        addr = chengliao_read_sites["称重run"]["Address"]
        wait_status = master.detect_wait_bool2(addr, True, 10)
        print('iiiisss77777')
        if not wait_status:
            print("称重on err")

        # address, wait_val, data_type = None, out_time = None):
        addr = chengliao_read_sites["工作完成数量"]["Address"]

        data_type = chengliao_read_sites["工作完成数量"]["DataType"]
        wait_status = master.detect_wait_real(int(addr), self.hole_num, data_type)
        print("waitstat", wait_status)
        if not wait_status:
            print("工作完成数量 err")
            return False
        addr = chengliao_write_sites["称重on"]["Address"]
        master.set_db_bool(addr, 0)
        # await asyncio.sleep(0.1)
        addr = chengliao_write_sites["称重stop"]["Address"]
        master.set_db_bool(addr, 1)
        # await asyncio.sleep(0.1)
        time.sleep(0.5)
        master.set_db_bool(addr, 0)

        return True

    def start(self):
        print('sv-2')
        self.chengliao_single(self.main_master)
        self.chengliao_single(self.auxiliary_master)
        print('idifjsoso')

    def start2(self):
        # 主料
        # self.chengliao_single(self.main_master)
        print('chengliao.start')
        tasks = []
        task1 = self.loop.create_task(self.chengliao_single(self.main_master))
        tasks.append(task1)
        # 辅料
        task2 = self.loop.create_task(self.chengliao_single(self.auxiliary_master))
        tasks.append(task2)
        wait_coro = asyncio.wait(tasks)
        print('chengliao.start2222')
        self.loop.run_until_complete(wait_coro)
        print('chengliao.start33333')
        return True

    def stop(self):
        address = chengliao_write_sites["称重stop"]
        pass

    # 监听称料完成
    def get_finish_status(self):
        pass


if __name__ == "__main__":
    pass

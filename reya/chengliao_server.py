import asyncio
import json
import time
from copy import deepcopy
import modbus_tk.defines as cst
from utils import redis_utils, common
from config import conf
from utils.modbus_utils import ModbusTcpUtils
from config.chengliao_sites import *
from config.ip_list import ip_list
from robot import Robot


class ChengLiaoServer:
    # 称料监听

    def __init__(self):
        if conf.left_or_right == "left":
            self.modbus_main = ModbusTcpUtils(ip_list["称料主左"])
            self.modbus_auxiliary = ModbusTcpUtils(ip_list["称料辅左"])
        elif conf.left_or_right == "right":
            self.modbus_main = ModbusTcpUtils(ip_list["称料主右"])
            self.modbus_auxiliary = ModbusTcpUtils(ip_list["称料辅右"])
        else:
            raise

        self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)

        # set_bool(master, "称重联动on", 1) 始终开启
        pass

    def set_params(self, params):
        # 设置参数
        data_base = {
            "工作工位设定-设置": common.get_sub_station_from_work_station(params["work_station"]),
            "第1次放料开门时间-设置": params.get("第1次放料开门时间", 15),
            "第2次放料开门时间-设置": params.get("第2次放料开门时间", 0),
        }
        main_data = deepcopy(data_base)
        main_data["工作重量设定-设置"] = params["主料投料量"]
        main_data["物料剔除重量设定-设置"] = params["主料投料量"]
        # 主料
        res1 = self.set_param_main_or_auxiliary(self.modbus_main, main_data)
        # 辅料
        auxiliary_data = deepcopy(data_base)
        auxiliary_data["工作重量设定-设置"] = params["辅料投料量"]
        auxiliary_data["物料剔除重量设定-设置"] = params["辅料投料量"]
        res2 = self.set_param_main_or_auxiliary(self.modbus_auxiliary, auxiliary_data)
        if not res1 or not res2:
            return False

    def set_param_main_or_auxiliary(self, master, data):
        for key in data:
            addr = chengliao_write_sites[key]["Address"]
            res = master.write_single_register(addr, data[key])
        return True

    def detect_chengliao_finish(self, master, hole_num):
        while True:
            # 工作完成数量
            finish_num = master.execute(1, cst.READ_HOLDING_REGISTERS,
                                                  chengliao_read_sites["工作完成数量-实时"], 1)[0]
            print("工作完成数量", finish_num)
            if finish_num == hole_num:
                break
        return True

    def chengzhong_stop_this_time(self, master):
        master.write_single_register(chengliao_write_sites["称重on-设置"], 0)
        master.write_single_register(chengliao_write_sites["称重stop-设置"], 1)
        time.sleep(0.5)
        master.write_single_register(chengliao_write_sites["称重stop-设置"], 0)

    def task_listen(self):
        while True:

            # 监听是否有任务
            tasks_len = self.redis_local_db.redis_llen(conf.redis_chengliao_task_key)
            if not tasks_len:
                time.sleep(0.2)
                continue
            # 称重联动on 是否开启
            main_on = self.modbus_main.get_db_bool(chengliao_write_sites["称重联动on-设置"])
            auxiliary_on = self.modbus_auxiliary.get_db_bool(chengliao_write_sites["称重联动on-设置"])
            if not main_on or not auxiliary_on:
                time.sleep(1)
                continue

            # 允许称重 todo 现在同时监听，以后尝试并行
            while not self.modbus_main.detect_wait_bool(chengliao_read_sites["允许称重-实时"]):
                time.sleep(1)
            while not self.modbus_auxiliary.detect_wait_bool(chengliao_read_sites["允许称重-实时"]):
                time.sleep(1)

            # todo 取任务 判断此任务条件是否满足，满足执行，不满足将此任务后调
            # 压机状态如果为1， 继续，不为1，后调1位
            plan_id = self.redis_local_db.redis_lpop(conf.redis_chengliao_task_key)

            local_plan_info = self.redis_local_db.redis_hgetall(conf.redis_plan_local_info.format(plan_id))

            task_params = self.redis_server_db.redis_hgetall(f"production_plan:{plan_id}")
            if not task_params:
                # 任务被删除或出现其他情况
                continue

            # 判断这个任务是否继续
            if task_params['if_go_on'] != "y":
                # 任务已暂停 或中止
                continue

            # 判断压机状态是否为1, 不为1放在队列最后，执行下一个
            station = common.get_sub_station_from_work_station(task_params["work_station"])
            yaji_redis_key = f"device_listen:{conf.device_name}:yaji:{str(station).zfill(2)}"
            work_station_status = self.redis_local_db.redis_hget(yaji_redis_key, "工位状态-实时")
            if work_station_status != 1 and task_params["完成数量"] < task_params["加工数量"]:
                self.redis_local_db.redis_lpush(conf.redis_chengliao_task_key, plan_id)
                continue

            # 数量上判断是否进行下一轮称料
            if local_plan_info["完成数量"] + local_plan_info["模具腔数"] < local_plan_info["加工数量"]:
                self.redis_local_db.redis_lpush(conf.redis_chengliao_task_key, plan_id)

            # val = json.dumps({"plan_id": plan_id})
            # 工位对应的plan和状态填写
            self.redis_local_db.redis_hset(conf.redis_station_working_info_key,
                                           station, plan_id)

            self.set_params(task_params)

            # 称重开始 主
            self.modbus_main.write_single_register(chengliao_write_sites["称重on-设置"], 1)  # 主
            # 等待称重完成
            self.detect_chengliao_finish(self.modbus_main, task_params["模具腔数"])
            # 称重结束
            self.chengzhong_stop_this_time(self.modbus_main)

            # 称重开始 辅
            self.modbus_auxiliary.write_single_register(chengliao_write_sites["称重on-设置"], 1)  # 辅
            # 等待称重完成
            self.detect_chengliao_finish(self.modbus_auxiliary, task_params["模具腔数"])
            # 称重结束
            self.chengzhong_stop_this_time(self.modbus_auxiliary)

            # robot start
            Robot().robot_proc(task_params)


if __name__ == "__main__":
    ChengLiaoServer().task_listen()
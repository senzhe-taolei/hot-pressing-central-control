import asyncio
import json
import time

from check_detail import CheckDetail
from chengliao import ChengLiao
from robot import Robot
from yaji import YaJi
from yeya import YeYa
from utils import redis_utils
from utils.logger import MyLogging
from config import conf

logger = MyLogging("controlLog", file="../logs/control.log")


class ReYaControl:

    # "Workstation":"ZN-122/001#03"
    def __init__(self, ):
        self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)

        # self.robot_status = {"workstation": 0, "status": "stop"}  # onWork
        # self.yaji_status =
        # self.yaji = YaJi()
        # self.chengliao = ChengLiao()
        # self.yeya = YeYa()
        self.robot = None
        # 0: 空闲未称料，1：称料中，2：称料完成 等在接料
        self.chengliao_status = 0

        self.plan_num = 0
        self.finish_num = 0

    def plan(self, plan_id):
        # 获取计划参数
        params = self.redis_server_db.redis_hgetall(f"production_plan:{plan_id}")
        logger.info(params)
        # checkall status
        work_station = params.get("work_station")  # ZN-122/007#03
        station = int(work_station.split("#")[1])
        # 压机
        yaji = YaJi()
        yaji.set_params(params, station)
        # 检查压机状态是否到位
        # yaji.check_is_ok()
        # 检查各种报警
        # 压机热启动
        #
        plan_info = {
            "plan_id": plan_id,
            "加工数量": params["加工数量"],
            "完成数量": params["完成数量"],
            "模具腔数": params["模具腔数"],
            "work_station": params["work_station"]
        }
        # 写入称料redis 任务队列
        self.redis_local_db.redis_lpush(conf.redis_chengliao_task_key, plan_id)
        # 本地存储部分plan参数
        self.redis_local_db.redis_hmset(conf.redis_plan_local_info.format(plan_id), plan_info)
        # # 工位对应的plan和状态填写

        return ''

    # def app(self, recv_message):
    #     # 获取计划参数
    #     # todo 先一腔轮询
    #     # todo 加工数量 写入哪里
    #     params = recv_message["ParamValue"]
    #     work_station = int(recv_message["Workstation"].split("#")[-1])  # 1-8
    #     sub_station = work_station if work_station <= 4 else work_station - 4
    #     left_or_right = 'left' if work_station <= 4 else 'right'
    #     hole_num = params["模具腔数"]
    #     self.plan_num = params["加工数量"]
    #     # 液压启动
    #     self.yeya.yeya_start()
    #     # 写入压机参数
    #     self.yaji.set_params(params, work_station)
    #     # 压机启动
    #     self.yaji.heat_start()
    #     # todo 等待压机加热完成
    #
    #     # todo 给它首检确认信号, 后续在界面展示
    #     self.yaji.first_check()
    #
    #     chengliao_params = {
    #         "工作工位设定": sub_station,
    #         "第1次放料开门时间": 15,  # 不用变
    #         "第2次放料开门时间": 0,  # 不用变
    #         "模具腔数": hole_num,
    #         "主料投料量": params["主料投料量"],
    #         "辅料投料量": params["辅料投料量"],
    #     }
    #     # loop = asyncio.get_event_loop()
    #     # result = loop.run_until_complete(self.chengliao_process(chengliao_params))
    #     # loop.close()
    #
    #     # self.robot_process(left_or_right, hole_num, sub_station)
    #     self.chengliao_process(chengliao_params)
    #     self.robot_process(left_or_right, hole_num, sub_station)
    #
    #     # loop = asyncio.get_event_loop()
    #     # tasks = []
    #     # task1 = loop.create_task(self.chengliao_process(chengliao_params))
    #     # tasks.append(task1)
    #     # # 辅料
    #     # task2 = loop.create_task(self.robot_process(left_or_right, hole_num, sub_station))
    #     # tasks.append(task2)
    #     # wait_coro = asyncio.wait(tasks)
    #     # loop.run_until_complete(wait_coro)
    #     return True

    def need_chengliao(self):
        print("need-chengliao")
        # 最后的料已经接完, 在接料盒中
        last_one_status = self.chengliao_status == 2 and self.finish_num + 1 == self.plan_num
        # 是否需要称料
        if self.finish_num >= self.plan_num or last_one_status:
            return False
        print("need-chengliao, True")
        return True

    # async
    def chengliao_process(self, chengliao_params):
        print("chengliao_process")
        # 循环监听是否称料
        while self.need_chengliao():
            print('11111')
            self.chengliao_status = 1
            self.chengliao.set_params(chengliao_params)
            print('sv-1')
            chengliao_finish = self.chengliao.start()
            print('222222')
            if chengliao_finish:
                self.chengliao_status = 2
                print('33333')
                # await self.robot_process()

    # async
    def robot_process(self, left_or_right, hole_num, sub_station):
        print("robot_process")
        self.robot = Robot(left_or_right, hole_num, sub_station)
        # 监听
        while self.finish_num < self.plan_num:
            print("robot_process", self.finish_num, self.plan_num, self.chengliao_status,
                  self.robot.get_write_param_status())
            if self.chengliao_status == 2 and self.robot.get_write_param_status() in [1, '1', True, 'true']:
                # 机械臂接料
                print('iiiii')
                self.robot.set_params()
                self.robot.robot_start_reset()
                # todo 停止位置
                self.finish_num += 1
            time.sleep(1)

        pass

if __name__ == "__main__":
    # "Hole_Times": 2, "Num": 4,
    pass

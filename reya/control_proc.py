import asyncio
import json
import time

import websockets

from check_detail import CheckDetail
from chengliao import ChengLiao
from robot import Robot
from yaji import YaJi
from yeya import YeYa


IP_ADDR = "192.168.1.1"
IP_PORT = 8765
YAJI_WORKSTATION_PRE = "ZN-122"


class YaJiControl:

    # "Workstation":"ZN-122/001#03"
    def __init__(self, workstation):
        # self.start_listen_server()
        self.robot_status = {"workstation": 0, "status": "stop"}  # onWork
        # self.yaji_status =
        self.yaji = YaJi()
        self.chengliao = ChengLiao()
        self.yeya = YeYa()
        self.robot = None
        # 0: 空闲未称料，1：称料中，2：称料完成 等在接料
        self.chengliao_status = 0

        self.plan_num = 0
        self.finish_num = 0

    def app(self, recv_message):
        # todo 先一腔轮询
        # todo 加工数量 写入哪里
        params = recv_message["ParamValue"]
        work_station = int(recv_message["Workstation"].split("#")[-1])  # 1-8
        sub_station = work_station if work_station <= 4 else work_station - 4
        left_or_right = 'left' if work_station <= 4 else 'right'
        hole_num = params["模具腔数"]
        self.plan_num = params["加工数量"]
        # 液压启动
        self.yeya.yeya_start()
        # 写入压机参数
        self.yaji.set_params(params, work_station)
        # 压机启动
        self.yaji.heat_start()
        # todo 等待压机加热完成

        # todo 给它首检确认信号, 后续在界面展示
        self.yaji.first_check()

        chengliao_params = {
            "工作工位设定": sub_station,
            "第1次放料开门时间": 15,  # 不用变
            "第2次放料开门时间": 0,  # 不用变
            "模具腔数": hole_num,
            "主料投料量": params["主料投料量"],
            "辅料投料量": params["辅料投料量"],
        }
        # loop = asyncio.get_event_loop()
        # result = loop.run_until_complete(self.chengliao_process(chengliao_params))
        # loop.close()

        # self.robot_process(left_or_right, hole_num, sub_station)
        self.chengliao_process(chengliao_params)
        self.robot_process(left_or_right, hole_num, sub_station)

        # loop = asyncio.get_event_loop()
        # tasks = []
        # task1 = loop.create_task(self.chengliao_process(chengliao_params))
        # tasks.append(task1)
        # # 辅料
        # task2 = loop.create_task(self.robot_process(left_or_right, hole_num, sub_station))
        # tasks.append(task2)
        # wait_coro = asyncio.wait(tasks)
        # loop.run_until_complete(wait_coro)
        return True

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
            print("robot_process", self.finish_num, self.plan_num, self.chengliao_status, self.robot.get_write_param_status())
            if self.chengliao_status == 2 and self.robot.get_write_param_status() in [1, '1', True, 'true']:
                # 机械臂接料
                print('iiiii')
                self.robot.set_params()
                self.robot.robot_start_reset()
                # todo 停止位置
                self.finish_num += 1
            time.sleep(1)

        pass

    # def do_async_while_func(self, func, params):
    #     while func(params):


    async def receive_socket(self, websocket, path):
        async for message in websocket:
            message_dict = json.loads(message)
            echo = "OK"
            if not message_dict.get("Workstation", "").startswith(YAJI_WORKSTATION_PRE):
                echo = "Param erro: error Workstation"

            await websocket.send(echo)

    def start_listen_server(self):
        start_server = websockets.serve(self.receive_socket, IP_ADDR, IP_PORT)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    # "Hole_Times": 2, "Num": 4,
    params = {
        "Device": "ZN-122/014", "Workstation": "ZN-122/014#07", "ParamType": 6,
        "ParamValue": {
            "加工数量": 2,
            "循环次数": 1,
            "模具腔数": 3,
            "模腔类型": 1,
            "上模温度": 155.0,
            "中模温度01": 150.0, "中模温度02": 0.0,
            "下模温度01": 155.0, "下模温度02": 0.0, "下模温度03": 0.0, "下模温度04": 0.0,
            "一次加压时间": 15, "二次加压时间": 0, "三次加压时间": 0, "四次加压时间": 0, "五次加压时间": 0,
            "六次加压时间": 0, "七次加压时间": 0,
            "一次排气时间": 10,  "二次排气时间": 0, "三次排气时间": 0, "四次排气时间": 0, "五次排气时间": 0,
            "六次排气时间": 0, "七次排气时间": 0,
            "末次保压时间": 200, "放气距离": 20.0,
            "一次压力": 9.0, "二次压力": 0,   "三次压力": 0,  "四次压力": 0,   "五次压力": 0,
            "六次压力": 0,  "七次压力": 0,
            "末次保压": 9.0,
            "模具装料深度": 46.7,
            "产品厚度": 14.0,
            "主料投料量": 590, "辅料投料量": 150,
            "装盒数量": "14",

            "材料面积": "54.43", "热压简图": "A12240NNP",
            "主料料号": "AD103", "辅料料号": "UF003",
            "ATTACHMENT": [
              {
                "NAME": "A12240NNP.jpg",
                "PATH": "http://192.168.10.3:8001/api/FromPLM/GetCraftDrawing?imgPath=P230523ADE018/021/A12240NNP.jpg"
              }
            ],
            "产品订单": "P230523ADE018/021", "产品编号": "10230072514", "产品名称": "A12240NNP/AD103/18.90mm",
            "计划开始时间": "2023-07-18T13:43:58.7879878+08:00",
            "计划结束时间": "2023-07-18T13:43:58.7879897+08:00", "模具编号": "A12240XX-MZH-I05",
            "加料器名称": "", "MESWORKID": 100032062
        }, "Notes": ""
    }
    workstation = "ZN-122/001#07"
    YaJiControl(workstation).app(params)
    pass

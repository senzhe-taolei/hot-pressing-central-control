from ping3 import ping
import asyncio
from config.ip_list import *
from config import conf, const
import time
from utils import redis_utils


class CheckPing:

    def __init__(self):
        # ip 状态
        self.loop = asyncio.get_event_loop()
        self.ips = {}
        if conf.left_or_right == const.RIGHT:
            ip_keys = ip_left_keys
        else:
            ip_keys = ip_right_keys
        self.ips = {key: ip_list[key] for key in ip_keys}
        self.ips = {"111": "39.156.66.10", '222': "13.107.21.200"}
        self.ip_status = dict(zip(self.ips.keys(), [False for i in self.ips]))
        self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)

        pass

    def __del__(self):
        self.loop.close()

    async def ping_some_ip(self, name):
        start_time = time.time()
        ip = self.ips[name]
        status = True if ping(ip, timeout=1, unit="ms") else False
        # print(ip, status)
        self.ip_status[name] = str(status)
        if status:
            await asyncio.sleep(0.3)
        end_time = time.time()
        print(end_time-start_time)

    def check_ip_loop(self):
        while True:
            # start_time = time.time()*1000
            tasks = []
            for name in self.ips:
                task = self.loop.create_task(self.ping_some_ip(name))
                tasks.append(task)
            wait_coro = asyncio.wait(tasks)
            self.loop.run_until_complete(wait_coro)
            print(self.ip_status)
            self.redis_local_db.redis_hmset(conf.ip_listen_key, self.ip_status)
            self.redis_server_db.redis_hmset(conf.ip_listen_key, self.ip_status)
            # end_time = time.time() * 1000
            # print(end_time-start_time, self.ip_status)


if __name__ == "__main__":
    checkPing = CheckPing()
    checkPing.check_ip_loop()
    pass

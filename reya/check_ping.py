from ping3 import ping
import asyncio
from config.ip_list import ip_list
import time


class CheckPing:

    def __init__(self):
        # ip 状态
        self.loop = asyncio.get_event_loop()
        self.ip_status = dict(zip(ip_list.keys(), [False for i in ip_list]))
        # todo redis 写入？
        pass

    def __del__(self):
        self.loop.close()

    async def ping_some_ip(self, name):
        start_time = time.time()
        ip = ip_list[name]
        status = True if ping(ip, timeout=1, unit="ms") else False
        print(ip, status)
        self.ip_status[name] = status
        if status:
            await asyncio.sleep(0.3)
        end_time = time.time()
        print(end_time-start_time)

    def check_ip_loop(self):
        while True:
            # start_time = time.time()*1000
            tasks = []
            for name in ip_list:
                task = self.loop.create_task(self.ping_some_ip(name))
                tasks.append(task)
            wait_coro = asyncio.wait(tasks)
            self.loop.run_until_complete(wait_coro)

            # end_time = time.time() * 1000
            # print(end_time-start_time, self.ip_status)


if __name__ == "__main__":
    checkPing = CheckPing()
    checkPing.check_ip_loop()
    pass

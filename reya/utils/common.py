import asyncio
import time
from bak.utils2 import plc_write_utils, plc_read_utils


# 协程run函数
def run(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value


def wait_val_change():
    pass


# plc 状态复位，先给出信号，等一段时间后再复位
# pulse 脉冲毫秒，自动复位
async def plc_bool_write(plc, address, status, pulse=0):
    if status and status != '0' and str(status).lower() != 'false':
        set = '1'
        reset = '0'
    else:
        set = '0'
        reset = '1'
    plc_write_utils.plc_write(plc, address, str(set))
    if pulse:
        await asyncio.sleep(pulse/1000)
        plc_write_utils.plc_write(plc, address, str(reset))


# pulse 脉冲毫秒，自动复位
async def plc_wait(plc, address, status, out_time=None):
    wait_status = False
    start_time = time.time()
    if status and status != '0' and str(status).lower() != 'false':
        wait_status = True
    while plc_read_utils.plc_read_alone(plc, address) != wait_status:
        await asyncio.sleep(50/1000)
        end_time = time.time()
        span_time = end_time - start_time
        if out_time is not None:
            if span_time > out_time:
                return False
    return True



import snap7
from snap7.util import *
from config.ip_list import ip_list
from config import conf, const
from utils import plc_utils, plc_write_utils, plc_read_utils, plc_read_universal, redis_utils
from config import yaji_sites

# read
yaji_sites_read_map = {
    "压机-1": yaji_sites.yaji_1_sites_read,
    "压机-2": yaji_sites.yaji_2_sites_read,
    "压机-3": yaji_sites.yaji_3_sites_read,
    "压机-4": yaji_sites.yaji_4_sites_read,
}


yaji_sites_write_map = {
    "压机-1": yaji_sites.yaji_1_sites_write,
    "压机-2": yaji_sites.yaji_2_sites_write,
    "压机-3": yaji_sites.yaji_3_sites_write,
    "压机-4": yaji_sites.yaji_4_sites_write,
}


class YaJi:

    def __init__(self,):
        # yaji_ip_left = ip_list["压机左"]
        # yaji_ip_right = ip_list["压机右"]
        # self.plc_left = plc_utils.get_plc_connection(ip_list["压机左"])
        # self.plc_right = plc_utils.get_plc_connection(ip_list["压机右"])
        self.plc_left = None
        self.plc_right = None
        self.plc = None
        self.workstation = None
        self.yaji_read_sites = None
        self.yaji_write_sites = None

        self.params = None

        self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)

        self.yaji_redis_pre_key = f"device_listen:{conf.device_name}:yaji:"
        self.yaji_redis_key = None

    def __del__(self):
        if self.plc:
            self.plc.destroy()

    # 设置参数 MES 下发参数 {"Workstation": "001#03", }
    def set_params(self, params, station):
        # workstation = int(params["Workstation"] .split("#")[-1])
        if 1 <= station <= 4:
            yaji_ip = ip_list["压机右"]
            map_key = f"压机-{station}"
        elif 5 <= station <= 8:
            yaji_ip = ip_list["压机左"]
            map_key = f"压机-{station - 4}"
        else:
            return False
        sub_station = station if station <= 4 else station - 4
        self.workstation = station
        self.yaji_redis_key = self.yaji_redis_pre_key + str(sub_station).zfill(2)
        self.plc = plc_utils.get_plc_connection(yaji_ip)
        self.yaji_read_sites = yaji_sites_read_map[map_key]
        self.yaji_write_sites = yaji_sites_write_map[map_key]
        self.params = params
        # MES参数写入压机
        for key in params:
            name = f"{key}-设置"
            if name in self.yaji_write_sites:
                address = self.yaji_write_sites[name]["Address"]
                data_type = self.yaji_write_sites[name]["DataType"]
                if data_type.lower() == "real":
                    result = plc_write_utils.plc_write(self.plc, address, str(params[key]), date_type='float')
                else:
                    result = plc_write_utils.plc_write(self.plc, address, str(params[key]))

    # 初始值设置，先清零
    def init(self):
        pass

    # 加热启动
    def heat_start(self):
        address = self.yaji_write_sites["加热启动-设置"]["Address"]
        result = plc_write_utils.plc_write(self.plc, address, str(1))

    # 加热停止
    def heat_stop(self):
        address = self.yaji_write_sites["加热停止-设置"]["Address"]
        result = plc_write_utils.plc_write(self.plc, address, str(0))

    # 首检确认信号
    def first_check(self):
        address = self.yaji_write_sites["首检确认信号-设置"]["Address"]
        result = plc_write_utils.plc_write(self.plc, address, str(0))

    # 检查温度等条件是否就绪，先校验温度
    def check_is_ok(self, station):
        flag = False
        check_keys = ["上模温度", "中模温度01", "中模温度02", "下模温度01", "下模温度02", "下模温度03", "下模温度04"]
        while not flag:
            flag = True
            yaji_data = self.redis_local_db.redis_hgetall(self.yaji_redis_pre_key + str(station).zfill(2))
            for key in check_keys:
                real_key = key + "-实时"
                set_key = key + "-设置"
                if yaji_data[real_key] < yaji_data[set_key]:
                    flag = False
                    break


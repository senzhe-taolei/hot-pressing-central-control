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
        self.plc_left = plc_utils.get_plc_connection(ip_list["压机左"])
        self.plc_right = plc_utils.get_plc_connection(ip_list["压机右"])
        self.workstation = None
        self.plc = None
        self.yaji_read_sites = None
        self.yaji_write_sites = None

        self.redis_local_db = redis_utils.RedisUtils(conf.redis_local_host, conf.redis_local_port)
        self.redis_server_db = redis_utils.RedisUtils(conf.redis_server_host, conf.redis_server_port)


    def __del__(self):
        if self.plc:
            self.plc.destroy()

    # 设置参数 MES 下发参数 {"Workstation": "001#03", }
    def set_params(self, params, workstation):
        # workstation = int(params["Workstation"] .split("#")[-1])
        if 1 <= workstation <= 4:
            yaji_ip = ip_list["压机右"]
            map_key = f"压机-{workstation}"
        elif 5 <= workstation <= 8:
            yaji_ip = ip_list["压机左"]
            map_key = f"压机-{workstation-4}"
        else:
            return False
        self.workstation = workstation
        self.plc = plc_utils.get_plc_connection(yaji_ip)
        self.yaji_read_sites = yaji_sites_read_map[map_key]
        self.yaji_write_sites = yaji_sites_write_map[map_key]

        # 写MES参数
        for key in params:
            if key in self.yaji_write_sites:
                address = self.yaji_write_sites[key]["Address"]
                data_type = self.yaji_write_sites[key]["DataType"]
                if data_type.lower() == "real":
                    result = plc_write_utils.plc_write(self.plc, address, str(params[key]), date_type='float')
                else:
                    result = plc_write_utils.plc_write(self.plc, address, str(params[key]))

    # 初始值设置，先清零
    def init(self):
        pass

    # 加热启动
    def heat_start(self):
        address = self.yaji_write_sites["加热启动"]["Address"]
        result = plc_write_utils.plc_write(self.plc, address, str(1))

    # 加热停止
    def heat_stop(self):
        address = self.yaji_write_sites["加热停止"]["Address"]
        result = plc_write_utils.plc_write(self.plc, address, str(0))

    # 首检确认信号
    def first_check(self):
        address = self.yaji_write_sites["首检确认信号"]["Address"]
        result = plc_write_utils.plc_write(self.plc, address, str(0))

    # 读取状态值
    def yaji_loop_read_all_sites(self):
        # redis_key
        redis_key = conf.device_name + ":yaji"
        while True:
            if conf.left_or_right == const.LEFT:
                plc = self.plc_left
            elif conf.left_or_right == const.RIGHT:
                plc = self.plc_right
            else:
                raise
            # left read
            # left_right = {"left": self.plc_left, "right": self.plc_right}
            # for l_or_r, plc in left_right.items():
            data_db30 = plc.read_area(snap7.client.Areas.DB, 30, 0, 30)
            data_db17 = plc.read_area(snap7.client.Areas.DB, 17, 0, 420)
            data_db18 = plc.read_area(snap7.client.Areas.DB, 18, 0, 424)
            data_db19 = plc.read_area(snap7.client.Areas.DB, 19, 0, 424)
            data_db20 = plc.read_area(snap7.client.Areas.DB, 20, 0, 424)

            data_db40_330 = plc.read_area(snap7.client.Areas.DB, 40, 330, 1)
            data_db40_662 = plc.read_area(snap7.client.Areas.DB, 40, 662, 1)
            data_db40_994 = plc.read_area(snap7.client.Areas.DB, 40, 994, 1)
            data_db40_1236 = plc.read_area(snap7.client.Areas.DB, 40, 1236, 1)

            def get_site_val(sites):
                value_dict = {}
                for name, site in sites.items():
                    address = site["Address"]
                    db = address.split('.')[0][2:]  # DB
                    if db == "40":
                        index = address.split('.')[1][3:]
                        bool_index = int(address.split('.')[2])
                        if index == "330":
                            data_db40 = data_db40_330
                        elif index == "662":
                            data_db40 = data_db40_662
                        elif index == "994":
                            data_db40 = data_db40_994
                        elif index == "1236":
                            data_db40 = data_db40_1236
                        else:
                            raise
                        value = str(snap7.util.get_bool(data_db40, 0, bool_index)).lower()
                        value_dict[name] = value
                        continue
                    elif db == "30":
                        data_db = data_db30
                    elif db == "17":
                        data_db = data_db17
                    elif db == "18":
                        data_db = data_db18
                    elif db == "19":
                        data_db = data_db19
                    elif db == "20":
                        data_db = data_db20
                    else:
                        raise
                    value = plc_read_universal.get_value_from_sequence_data(site, data_db)
                    value_dict[name] = value
                return value_dict

            # yaji_1_sites_read
            yaji_1_read_dict = get_site_val(yaji_sites.yaji_1_sites_read)
            yaji_2_read_dict = get_site_val(yaji_sites.yaji_2_sites_read)
            yaji_3_read_dict = get_site_val(yaji_sites.yaji_3_sites_read)
            yaji_4_read_dict = get_site_val(yaji_sites.yaji_4_sites_read)

            yaji_1_write_dict = get_site_val(yaji_sites.yaji_1_sites_write)
            yaji_2_write_dict = get_site_val(yaji_sites.yaji_2_sites_write)
            yaji_3_write_dict = get_site_val(yaji_sites.yaji_3_sites_write)
            yaji_4_write_dict = get_site_val(yaji_sites.yaji_4_sites_write)


            def key_func(num):
                if conf.left_or_right == const.LEFT:
                    return "0"+str(num)
                else:
                    return "0"+str(num+4)

            yaji_1 = yaji_1_read_dict|yaji_1_write_dict
            yaji_2 = yaji_2_read_dict|yaji_2_write_dict
            yaji_3 = yaji_3_read_dict|yaji_3_write_dict
            yaji_4 = yaji_4_read_dict|yaji_4_write_dict
            update_time = int(time.time()*1000)
            yaji_1["update_time"] = update_time
            yaji_2["update_time"] = update_time
            yaji_3["update_time"] = update_time
            yaji_4["update_time"] = update_time
            self.redis_local_db.redis_hmset(redis_key+key_func(1), yaji_1)
            self.redis_local_db.redis_hmset(redis_key+key_func(2), yaji_2)
            self.redis_local_db.redis_hmset(redis_key+key_func(3), yaji_3)
            self.redis_local_db.redis_hmset(redis_key+key_func(4), yaji_4)

            self.redis_server_db.redis_hmset(redis_key + key_func(1), yaji_1)
            self.redis_server_db.redis_hmset(redis_key + key_func(2), yaji_2)
            self.redis_server_db.redis_hmset(redis_key + key_func(3), yaji_3)
            self.redis_server_db.redis_hmset(redis_key + key_func(4), yaji_4)


if __name__ == "__main__":
    YaJi().yaji_loop_read_all_sites()

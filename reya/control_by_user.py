from config.ip_list import ip_list as ip_list
from config.robot_sites import robot_left_sites as robot_left_sites, robot_right_sites as robot_right_sits
from utils.plc_utils import get_plc_connection
from utils.plc_write_utils import plc_write_alone
from config.yeya_sites import yeya_sites as yeya_site
from config.yaji_sites import yaji_1_sites_write as yaji_1_sites, yaji_2_sites_write as yaji_2_sites, yaji_3_sites_write as yaji_3_sites, yaji_4_sites_write as yaji_4_sites

# 设备手动单点控制指令或者参数下发
def device_user_control(device_name: str, control_name: str, control_value: str):
    if device_name.startswith("zhulioa") or device_name.startswith("fuliao"):   # modbus通讯
        pass
    else:  # snap7通讯
        if device_name.startswith("robot"):
            ip = ip_list.get("机械手")
            if device_name.endswith("l"):
                plc_address = robot_left_sites.get(control_name).get("Address")
            elif device_name.endswith("r"):
                plc_address = robot_right_sits.get(control_name).get("Address")
            else:
                return {"code": 500, "msg": f"参数device_name：{device_name}不合法！"}
        elif device_name.startswith("yeya"):
            ip = ip_list.get("液压站")
            plc_address = yeya_site.get(control_name).get("Address")
        elif device_name.startswith("yaji_l"):
            ip = ip_list.get("压机左")
            if device_name.endswith("1"):
                plc_address = yaji_1_sites.get(control_name).get("Address")
            elif device_name.endswith("2"):
                plc_address = yaji_2_sites.get(control_name).get("Address")
            elif device_name.endswith("3"):
                plc_address = yaji_3_sites.get(control_name).get("Address")
            elif device_name.endswith("4"):
                plc_address = yaji_4_sites.get(control_name).get("Address")
            else:
                return {"code": 500, "msg": f"参数device_name：{device_name}不合法！"}
        elif device_name.startswith("yaji_r"):
            ip = ip_list.get("压机右")
            if device_name.endswith("1"):
                plc_address = yaji_1_sites.get(control_name).get("Address")
            elif device_name.endswith("2"):
                plc_address = yaji_2_sites.get(control_name).get("Address")
            elif device_name.endswith("3"):
                plc_address = yaji_3_sites.get(control_name).get("Address")
            elif device_name.endswith("4"):
                plc_address = yaji_4_sites.get(control_name).get("Address")
            else:
                return {"code": 500, "msg": f"参数device_name：{device_name}不合法！"}
        else:
            return {"code": 500, "msg": f"参数device_name：{device_name}不合法！"}
        plc = get_plc_connection(ip)
        if type(plc) is not str:
            action = plc_write_alone(plc, plc_address, control_value)
            if action == "write_success":
                return {"code": 200, "data": {"result": "success"}}
            else:
                return {"code": 500, "msg": f"设备device_name：{device_name}的{control_name}参数写入plc失败！"}
        else:
            return {"code": 500, "msg": f"PLC连接失败-->{plc}"}

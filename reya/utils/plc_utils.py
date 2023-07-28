from ping3 import ping
import snap7


def get_plc_connection(ip):
    plc = None
    try:
        status = True if ping(ip, timeout=1, unit="ms") else False
        if not status:
            return f"IP={ip}的设备不在线"
        else:
            plc = snap7.client.Client()
            plc.connect(ip, 0, 1)
            if plc.get_connected():
                return plc
            else:
                return f"IP={ip}的设备连接失败"
    except Exception as e:
        print(e)
        if plc is not None:
            plc.disconnect()
            plc.destroy()
        return f"IP={ip}的设备连接报错：{e}"

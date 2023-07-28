import time
import snap7


def get_plc_connection(ip):
    plc = None
    try:
        plc = snap7.client.Client()
        plc.connect(ip, 0, 1)
        return plc
    except Exception as e:
        print(e)
        if plc is not None:
            plc.disconnect()
            plc.destroy()

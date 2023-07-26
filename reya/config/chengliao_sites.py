# 仅用于开始时清除称料机的运动状态
chengliao_write_action_status_addr = "2300"

chengliao_write_sites = {
    '称重联动on-设置': {'Name': '称重联动on-设置', 'unit': '', 'DataType': 'BOOL', 'Address': '2300.0'},
    '称重on-设置': {'Name': '称重on-设置', 'unit': '', 'DataType': 'BOOL', 'Address': '2300.1'},
    '机械臂给料on-设置': {'Name': '机械臂给料on-设置', 'unit': '', 'DataType': 'BOOL', 'Address': '2300.2'},
    '称重stop-设置': {'Name': '称重stop-设置', 'unit': '', 'DataType': 'BOOL', 'Address': '2300.3'},
    '物料剔除-设置': {'Name': '物料剔除-设置', 'unit': '', 'DataType': 'BOOL', 'Address': '2300.4'},
    '工作重量设定-设置': {'Name': '工作重量设定-设置', 'unit': '', 'DataType': 'DWORD', 'Address': '2304'},
    '工作工位设定-设置': {'Name': '工作工位设定-设置', 'unit': '', 'DataType': 'DWORD', 'Address': '2306'},
    '物料剔除重量设定-设置': {'Name': '物料剔除重量设定-设置', 'unit': '', 'DataType': 'DWORD', 'Address': '2308'},
    '投料器取料号-设置': {'Name': '投料器取料号-设置', 'unit': '', 'DataType': 'DWORD', 'Address': '2310'},
    '第1次放料开门时间-设置': {'Name': '第1次放料开门时间-设置', 'unit': '', 'DataType': 'DWORD', 'Address': '2312'},
    '第2次放料开门时间-设置': {'Name': '第2次放料开门时间-设置', 'unit': '', 'DataType': 'DWORD', 'Address': '2314'}
}

chengliao_read_sites = {
    '称重联动允许-实时': {'Name': '称重联动允许-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.0'},
    '称重联动run-实时': {'Name': '称重联动run-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.1'},
    '允许称重-实时': {'Name': '允许称重-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.2'},
    '称重run-实时': {'Name': '称重run-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.3'},
    '1#run-实时': {'Name': '1#run-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.4'},
    '2#run-实时': {'Name': '2#run-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.5'},
    '3#run-实时': {'Name': '3#run-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.6'},
    '4#run-实时': {'Name': '4#run-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.7'},
    '允许给料-实时': {'Name': '允许给料-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.8'},
    '机械臂给料run-实时': {'Name': '机械臂给料run-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.9'},
    '1#称重超时-实时': {'Name': '1#称重超时-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.10'},
    '2#称重超时-实时': {'Name': '2#称重超时-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.11'},
    '3#称重超时-实时': {'Name': '3#称重超时-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.12'},
    '4#称重超时-实时': {'Name': '4#称重超时-实时', 'unit': '', 'DataType': 'BOOL', 'Address': '2200.13'},
    '工作完成数量-实时': {'Name': '工作完成数量-实时', 'unit': '', 'DataType': 'DWORD', 'Address': '2202'},
    '放料口已开口信号-实时': {'Name': '放料口已开口信号-实时', 'unit': '', 'DataType': 'DWORD', 'Address': '2224'}
}

import snap7
from snap7 import util
import re


# DBX的批量读取，返回value列表
def dbx_read(plc, db_num, start_index, length):
    # 参数说明：snap7.client.Areas.DB————DB-DB区；PE，I区；PA，Q区
    # 参数说明：db_num————DB区的编号，I区和Q区写0
    # 参数说明：0————起始byte地址，注意不是bite地址
    # 参数说明：length————读取byte的长度

    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, start_index, length)
        dbx_value_list = []  # 初始化列表，将读取的所有值按照读取顺序放入列表中
        for x in range(0, length):  # 如果读取的是bool值，需要按照byte地址和bite地址提取
            for y in range(0, 8):
                # x是data中的byte序号，无论start_index的值是多少，都从0开始，y是bite地址（0-7）
                value = str(util.get_bool(data, x, y)).lower()
                dbx_value_list.append(value)
        return dbx_value_list
    except Exception as e:
        log = f"DBX批量读取脚本报错:{str(e)}"
        print(log)
        return 'connect_fail'


# I点的批量读取，返回value列表
def pe_read(plc, start_index, length):
    # 参数说明：snap7.client.Areas.DB————DB-DB区；PE，I区；PA，Q区
    # 参数说明：db_num————DB区的编号，I区和Q区写0
    # 参数说明：0————起始byte地址，注意不是bite地址
    # 参数说明：length————读取byte的长度
    try:
        data = plc.read_area(snap7.client.Areas.PE, 0, start_index, length)
        pe_value_list = []
        for x in range(0, length):
            for y in range(0, 8):
                value = str(util.get_bool(data, x, y)).lower()
                pe_value_list.append(value)
        return pe_value_list
    except Exception as e:
        log = f"I点批量读取脚本报错:{str(e)}"
        print(log)
        return ['connect_fail']


# Q点的批量读取，返回value列表
def pa_read(plc, start_index, length):
    # 参数说明：snap7.client.Areas.DB————DB-DB区；PE，I区；PA，Q区
    # 参数说明：db_num————DB区的编号，I区和Q区写0
    # 参数说明：0————起始byte地址，注意不是bite地址
    # 参数说明：length————读取byte的长度
    try:
        data = plc.read_area(snap7.client.Areas.PA, 0, start_index, length)
        pa_value_list = []
        for x in range(0, length):
            for y in range(0, 8):
                value = str(util.get_bool(data, x, y)).lower()
                pa_value_list.append(value)
        return pa_value_list
    except Exception as e:
        log = f"Q点批量读取脚本报错:{str(e)}"
        print(log)
        return ['connect_fail']


def m_read(plc, start_index, length):
    try:
        data = plc.read_area(snap7.client.Areas.MK, 0, start_index, length)
        m_value_list = []
        for x in range(0, length):
            for y in range(0, 8):
                value = str(util.get_bool(data, x, y)).lower()
                m_value_list.append(value)
        return m_value_list
    except Exception as e:
        log = f"M点批量读取脚本报错:{str(e)}"
        print(log)
        return ['connect_fail']


# dbb的批量读取，返回value列表
def dbb_read(plc, db_num, start_index, length):
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, start_index, length)
        dbb_value_list = []
        for x in range(0, length):
            value = util.get_int(data, x)
            dbb_value_list.append(value)
        return dbb_value_list
    except Exception as e:
        log = f"DBB点批量读取脚本报错:{str(e)}"
        print(log)
        return ['connect_fail']


# dbw的批量读取，返回value列表
def dbw_read(plc, db_num, start_index, length):
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, start_index, length)
        dbw_value_list = []
        for x in range(0, length - 1, 2):
            value = util.get_int(data, x)
            dbw_value_list.append(value)
        return dbw_value_list
    except Exception as e:
        log = f"DBW点批量读取脚本报错:{str(e)}"
        print(log)
        return ['connect_fail']


# dbd的批量读取，返回value列表
def dbd_read(plc, db_num, start_index, length):
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, start_index, length)
        dbd_value_list = []
        for x in range(0, length - 3, 4):
            value = util.get_dint(data, x)
            dbd_value_list.append(value)
        return dbd_value_list
    except Exception as e:
        log = f"DBD点批量读取脚本报错:{str(e)}"
        print(log)
        return ['connect_fail']


# 从读取的连续数据中，分离出site对应的值
def get_value_from_sequence_data(site, data, start_index_base=0):
    address = site["Address"]
    addr_type = address.split('.')[1][:3]  # DBW, DBD
    start_index = int(address.split('.')[1][3:]) - start_index_base  # data的相对index
    if addr_type.upper() == "DBW":
        value = util.get_int(data, start_index)
    elif addr_type.upper() == "DBD":
        value = util.get_dint(data, start_index)
    elif addr_type.upper() == "DBX" and site["DataType"].lower() == "bool":
        # 先默认bool
        bool_index = int(address.split('.')[2])
        value = str(util.get_bool(data, start_index, bool_index)).lower()
    else:
        return False
    return value


# 将连续地址分离从连续数据中读取，start_index: 读取data的开始地址, db_num校验用
def split_address_values(sites, data, start_index_base=0):
    resp_dict = {}
    for name, site in sites.items():
        address = site["Address"]
        addr_type = address.split('.')[1][:3]  # DBW, DBD
        start_index = int(address.split('.')[1][3:]) - start_index_base  # data的相对index
        if addr_type.upper() == "DBW":
            value = util.get_int(data, start_index)
        elif addr_type.upper() == "DBD":
            value = util.get_dint(data, start_index)
        elif addr_type.upper() == "DBX" and site["DataType"].lower() == "bool":
            # 先默认bool
            bool_index = int(address.split('.')[2])
            value = str(util.get_bool(data, start_index, bool_index)).lower()
        else:
            continue
        resp_dict[name] = value
    return resp_dict


# 堆垛机DB540批量读取
def srm_db540_read(plc):
    db540_list = []
    for i in range(0, 57, 2):
        db540_list.append(i)
    try:
        data = plc.read_area(snap7.client.Areas.DB, 540, 0, 58)
        db540_value_list = []
        for x in range(0, len(db540_list)):
            if db540_list[x] != 4 and db540_list[x] != 6 and db540_list[x] != 22 and db540_list[x] != 24:
                value = util.get_int(data, db540_list[x])
                db540_value_list.append(value)
            elif db540_list[x] == 4 or db540_list[x] == 22:
                value = util.get_dint(data, db540_list[x])
                db540_value_list.append(value)
            else:
                pass
        return db540_value_list
    except Exception as e:
        log = f"DB540批量读取脚本报错:{str(e)}"
        print(log)
        return ['connect_fail']


# 堆垛机DB541批量读取
def srm_db541_read(plc):
    db541_list = []
    for i in range(0, 63, 2):
        db541_list.append(i)
    try:
        data = plc.read_area(snap7.client.Areas.DB, 541, 0, 64)
        db541_value_list = []
        for x in range(0, len(db541_list)):
            if db541_list[x] not in [20, 22, 24, 26, 28, 30, 32, 34, 42, 44, 54, 56]:
                value = util.get_int(data, db541_list[x])
                db541_value_list.append(value)
            elif db541_list[x] in [20, 24, 28, 32, 42, 54]:
                value = util.get_dint(data, db541_list[x])
                db541_value_list.append(value)
            else:
                pass
        return db541_value_list
    except Exception as e:
        log = f"DB541批量读取脚本报错:{str(e)}"
        print(log)
        return ['connect_fail']


# PLC143RFID的批量读取，返回value列表
def plc143_rfid_read(plc):
    try:
        data = plc.read_area(snap7.client.Areas.DB, 119, 204, 8)
        all_value = ""
        for x in range(0, 8):
            value_first = util.get_byte(data, x)
            value_end = hex(int(value_first))[2:].upper()
            if len(value_end) < 2:
                value_end = '0' + value_end
            all_value += str(value_end)
        return all_value
    except Exception as e:
        log = f"plc143-rfid读取脚本报错:{str(e)}"
        print(log)
        return ['connect_fail']


# RGV的plc批量读取，返回value列表
def plc_rgv_read(plc):
    db3_list = []
    for i in range(0, 45, 2):
        db3_list.append(i)
    try:
        data = plc.read_area(snap7.client.Areas.DB, 3, 0, 46)
        rgv_value_list = []
        for x in range(0, len(db3_list)):
            if db3_list[x] not in [0, 2, 20, 22, 24, 26]:
                value = util.get_int(data, db3_list[x])
                rgv_value_list.append(value)
            elif db3_list[x] in [0, 20, 24]:
                value = util.get_dint(data, db3_list[x])
                rgv_value_list.append(value)
            else:
                pass
        return rgv_value_list
    except Exception as e:
        log = f"rgv-plc读取脚本报错:{str(e)}"
        print(log)
        return ['connect_fail']


def plc_rfid_read_alone(plc, read_address: str, log_name: str, db):
    match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBB)([0-9]+)$', read_address, re.I)
    db_num = int(match_value_index.group(2))  # 获取db点db区位置编号
    byte_index = int(match_value_index.group(5))  # 获取db点byte位置编号
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 8)
        all_value = ""
        for x in range(0, 8):
            value_first = util.get_byte(data, x)
            value_end = hex(int(value_first))[2:].upper()
            if len(value_end) < 2:
                value_end = '0' + value_end
            all_value += str(value_end)
        return all_value
    except Exception as e:
        log = f"rfid:{read_address}读取时报错:{str(e)}"
        print(log)
        return 'read_failed'


def on_link_plc_read_alone(plc, read_address: str, log_name: str, db):
    if re.match(r'^(DB100)(\.)(DBD)([0-9]+)$', read_address, re.I):
        match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', read_address, re.I)
        db_num = int(match_value_index.group(2))  # 获取db点db区位置编号
        byte_index = int(match_value_index.group(5))  # 获取db点byte位置编号
        try:
            data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 4)
            value = util.get_real(data, 0)
            return value
        except Exception as e:
            log = f"{read_address}读取时报错:{str(e)}"
            print(log)
            return 'read_failed'
    elif re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', read_address, re.I):
        match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', read_address, re.I)
        db_num = int(match_value_index.group(2))  # 获取db点db区位置编号
        byte_index = int(match_value_index.group(5))  # 获取db点byte位置编号
        try:
            data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 4)
            value = util.get_int(data, 0)
            return value
        except Exception as e:
            log = f"{read_address}读取时报错:{str(e)}"
            print(log)
            return 'read_failed'
    elif re.match(r'^(DB)([0-9]+)(\.)(DBW)([0-9]+)$', read_address, re.I):
        match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBW)([0-9]+)$', read_address, re.I)
        db_num = int(match_value_index.group(2))  # 获取db点db区位置编号
        byte_index = int(match_value_index.group(5))  # 获取db点byte位置编号
        try:
            data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 2)
            value = util.get_int(data, 0)
            return value
        except Exception as e:
            log = f"{read_address}读取时报错:{str(e)}"
            print(log)
            return 'read_failed'
    elif re.match(r'^(DB)([0-9]+)(\.)(DBB)([0-9]+)$', read_address, re.I):
        match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBB)([0-9]+)$', read_address, re.I)
        db_num = int(match_value_index.group(2))  # 获取db点db区位置编号
        byte_index = int(match_value_index.group(5))  # 获取db点byte位置编号
        try:
            data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 1)
            value = util.get_sint(data, 0)
            return value
        except Exception as e:
            log = f"{read_address}读取时报错:{str(e)}"
            print(log)
            return 'read_failed'
    elif re.match(r'^(DB)([0-9]+)(\.)(DBX)([0-9]+)(\.)([0-7])$', read_address, re.I):
        match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBX)([0-9]+)(\.)([0-7])$', read_address, re.I)
        db_num = int(match_value_index.group(2))  # 获取db点db区位置编号
        byte_index = int(match_value_index.group(5))  # 获取db点byte位置编号
        bit_index = int(match_value_index.group(7))  # 获取db点bite位置编号

        try:
            data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 1)
            # x是data中的byte序号，无论start_index的值是多少，都从0开始，y是bite地址（0-7）
            value = str(util.get_bool(data, 0, bit_index)).lower()
            return value
        except Exception as e:
            log = f"{read_address}读取时报错:{str(e)}"
            print(log)
            return 'read_failed'

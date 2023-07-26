import time
import snap7
from snap7 import util
import re

def plc_read_alone_dbd_float(plc, read_address: str):
    if re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', read_address, re.I):
        match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', read_address, re.I)
        x = int(match_value_index.group(2))  # 获取db点db区位置编号
        y = int(match_value_index.group(5))  # 获取db点byte位置编号
        dbd_value = dbd_read_alone_float(plc, x, y)
        # plc.disconnect()
        # plc.destroy()
        return dbd_value

def plc_read_alone(plc, read_address: str):
    if re.match(r'^(DB)([0-9]+)(\.)(DBX)([0-9]+)(\.)([0-7])$', read_address, re.I):
        match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBX)([0-9]+)(\.)([0-7])$', read_address, re.I)
        x = int(match_value_index.group(2))  # 获取db点db区位置编号
        y = int(match_value_index.group(5))  # 获取db点byte位置编号
        z = int(match_value_index.group(7))  # 获取db点bite位置编号
        dbx_value = dbx_read_alone(plc, x, y, z)
        # plc.disconnect()
        # plc.destroy()
        return dbx_value

    elif re.match(r'^(I)([0-9]+)(\.)([0-7])$', read_address, re.I):
        match_value_index = re.match(r'^(I)([0-9]+)(\.)([0-7])$', read_address, re.I)
        x = int(match_value_index.group(2))  # 获取db点db区位置编号
        y = int(match_value_index.group(4))  # 获取db点byte位置编号
        pe_value = pe_read_alone(plc, x, y)
        # plc.disconnect()
        # plc.destroy()
        return pe_value

    elif re.match(r'^(M)([0-9]+)(\.)([0-7])$', read_address, re.I):
        match_value_index = re.match(r'^(M)([0-9]+)(\.)([0-7])$', read_address, re.I)
        x = int(match_value_index.group(2))  # 获取db点db区位置编号
        y = int(match_value_index.group(4))  # 获取db点byte位置编号
        pe_value = m_read_alone(plc, x, y)
        # plc.disconnect()
        # plc.destroy()
        return pe_value

    elif re.match(r'^(DB)([0-9]+)(\.)(DBB)([0-9]+)$', read_address, re.I):
        match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBB)([0-9]+)$', read_address, re.I)
        x = int(match_value_index.group(2))  # 获取db点db区位置编号
        y = int(match_value_index.group(5))  # 获取db点byte位置编号
        dbb_value = dbb_read_alone(plc, x, y)
        # plc.disconnect()
        # plc.destroy()
        return dbb_value

    elif re.match(r'^(DB)([0-9]+)(\.)(DBW)([0-9]+)$', read_address, re.I):
        match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBW)([0-9]+)$', read_address, re.I)
        x = int(match_value_index.group(2))  # 获取db点db区位置编号
        y = int(match_value_index.group(5))  # 获取db点byte位置编号
        dbw_value = dbw_read_alone(plc, x, y)
        # plc.disconnect()
        # plc.destroy()
        return dbw_value

    elif re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', read_address, re.I):
        match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', read_address, re.I)
        x = int(match_value_index.group(2))  # 获取db点db区位置编号
        y = int(match_value_index.group(5))  # 获取db点byte位置编号
        dbd_value = dbd_read_alone(plc, x, y)
        # plc.disconnect()
        # plc.destroy()
        return dbd_value


    else:
        log = f"plc_read_alone读取{read_address}正则表达式匹配失败。"
        print(log)
        return 'read_failed'

# dbx的单点位读取，返回value值
def dbx_read_alone(plc, db_num, byte_index, bite_index):
    # 参数说明：snap7.client.Areas.DB————DB-DB区；PE，I区；PA，Q区
    # 参数说明：db_num————DB区的编号，I区和Q区写0
    # 参数说明：0————起始byte地址，注意不是bite地址
    # 参数说明：length————读取byte的长度
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 1)
        dbx_value = str(util.get_bool(data, 0, bite_index)).lower()
        return dbx_value
    except Exception as e:
        log = f"dbx_read_alone读取报错！-->{str(e)}。"
        print(log)
        return 'read_failed'


# dbx的单点位读取，返回value值
def pe_read_alone(plc, byte_index, bite_index):
    # 参数说明：snap7.client.Areas.DB————DB-DB区；PE，I区；PA，Q区
    # 参数说明：db_num————DB区的编号，I区和Q区写0
    # 参数说明：0————起始byte地址，注意不是bite地址
    # 参数说明：length————读取byte的长度
    try:
        data = plc.read_area(snap7.client.Areas.PE, 0, byte_index, 1)
        pe_value = str(util.get_bool(data, 0, bite_index)).lower()
        return pe_value
    except Exception as e:
        log = f"pe_read_alone读取报错！-->{str(e)}。"
        print(log)
        return 'read_failed'


# dbb的单点位读取，返回value值
def dbb_read_alone(plc, db_num, byte_index):
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 1)
        dbb_value = util.get_sint(data, 0)
        return dbb_value
    except Exception as e:
        log = f"dbb_read_alone读取报错！-->{str(e)}。"
        print(log)
        return 'read_failed'


# dbw的单点位读取，返回value值
def dbw_read_alone(plc, db_num, byte_index):
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 2)
        dbw_value = util.get_int(data, 0)
        return dbw_value
    except Exception as e:
        log = f"dbw_read_alone读取报错！-->{str(e)}。"
        print(log)
        return 'read_failed'


# dbd的单点位读取，返回value列表
def dbd_read_alone(plc, db_num, byte_index):
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 4)
        dbd_value = util.get_dint(data, 0)
        return dbd_value
    except Exception as e:
        log = f"dbd_read_alone读取报错！-->{str(e)}。"
        print(log)
        return 'read_failed'

# dbd的单点位读取，返回value列表
def dbd_read_alone_float(plc, db_num, byte_index):
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 4)
        dbd_value = util.get_real(data, 0)
        return dbd_value
    except Exception as e:
        log = f"dbd_read_alone读取报错！-->{str(e)}。"
        print(log)
        return 'read_failed'

def m_read_alone(plc, byte_index, bite_index):  # m byte_index.bite_index
    try:
        data = plc.read_area(snap7.client.Areas.MK, 0, byte_index, 1)
        value = str(util.get_bool(data, 0, bite_index)).lower()
        return value
    except Exception as e:
        print(f'data取值报错-->{e}')
        return ['connect_fail']

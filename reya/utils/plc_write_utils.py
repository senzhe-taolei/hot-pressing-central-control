import snap7
from snap7 import util
import re


# Q点写入
def pa_write(plc, byte_index, bite_index, value):
    bool_value = False
    if value.lower() == 'true':
        bool_value = True
    elif value.lower() == 'false':
        bool_value = False
    try:
        # bool_data = bytearray(1)  # 声明数据写入的byte位数
        bool_data = plc.read_area(snap7.client.Areas.PA, 0, byte_index, 1)
        util.set_bool(bool_data, 0, bite_index, bool_value)  # bite_index——bool值写入的bite位置，其他类型没有此参数
        plc.write_area(snap7.client.Areas.PA, 0, byte_index, bool_data)  # 0————db区编号，其他区为0；byte_index————byte位置编号
        return 'write_success'
    except Exception as e:
        print(f'error:{str(e)}')
        return 'write_failed'


# M点写入
def m_write(plc, byte_index, bite_index, value):
    bool_value = False
    if value.lower() == 'true':
        bool_value = True
    elif value.lower() == 'false':
        bool_value = False
    try:
        # 先读取到原本的数据，然后改变需要改变的bit位数值，然后整体写入
        bool_data = plc.read_area(snap7.client.Areas.MK, 0, byte_index, 1)
        util.set_bool(bool_data, 0, bite_index, bool_value)  # bite_index——bool值写入的bite位置，其他类型没有此参数
        plc.write_area(snap7.client.Areas.MK, 0, byte_index, bool_data)  # 0————db区编号，其他区为0；byte_index————byte位置编号
        return 'write_success'
    except Exception as e:
        print(f'error:{str(e)}')
        return 'write_failed'


# DBX写入
def dbx_write(plc, db_index: int, byte_index: int, bite_index: int, value: str):
    bool_value = False
    if value.lower() == 'true':
        bool_value = True
    elif value.lower() == 'false':
        bool_value = False
    try:
        # bool_data = bytearray(1)  # 声明数据写入的byte位数
        bool_data = plc.read_area(snap7.client.Areas.DB, db_index, byte_index, 1)
        util.set_bool(bool_data, 0, bite_index, bool_value)  # bite_index——bool值写入的bite位置，其他类型没有此参数
        plc.write_area(snap7.client.Areas.DB, db_index, byte_index,
                       bool_data)  # db_index————db区编号，byte_index————byte位置编号
        return 'write_success'
    except Exception as e:
        print(f'error:{str(e)}')
        return 'write_failed'


# DBW写入
def dbw_write(plc, db_index: int, byte_index: int, value: str):
    try:
        int_data = bytearray(2)  # 声明数据写入的byte位数
        util.set_int(int_data, 0, int(value))  # bite_index——bool值写入的bite位置，其他类型没有此参数
        plc.write_area(snap7.client.Areas.DB, db_index, byte_index,
                       int_data)  # db_index————db区编号，byte_index————byte位置编号
        return 'write_success'
    except Exception as e:
        print(f'DB{db_index}.DBW{byte_index},write error:{str(e)}')
        return 'write_failed'


# DBD写入
def dbd_write(plc, db_index: int, byte_index: int, value: str):
    try:
        dint_data = bytearray(4)  # 声明数据写入的byte位数
        util.set_dint(dint_data, 0, int(value))  # bite_index——bool值写入的bite位置，其他类型没有此参数
        plc.write_area(snap7.client.Areas.DB, db_index, byte_index,
                       dint_data)  # db_index————db区编号，byte_index————byte位置编号
        return 'write_success'
    except Exception as e:
        print(f'error:{str(e)}')
        return 'write_failed'

# DBD写入 float
def dbd_write_float(plc, db_index: int, byte_index: int, value: str):
    try:
        dint_data = bytearray(4)  # 声明数据写入的byte位数
        util.set_real(dint_data, 0, float(value))
        plc.write_area(snap7.client.Areas.DB, db_index, byte_index,
                       dint_data)  # db_index————db区编号，byte_index————byte位置编号
        return 'write_success'
    except Exception as e:
        print(f'error:{str(e)}')
        return 'write_failed'

# DBB写入
def dbb_write(plc, db_index: int, byte_index: int, value: str):
    try:
        dint_data = bytearray(1)  # 声明数据写入的byte位数
        util.set_sint(dint_data, 0, int(value))  # bite_index——bool值写入的bite位置，其他类型没有此参数
        plc.write_area(snap7.client.Areas.DB, db_index, byte_index,
                       dint_data)  # db_index————db区编号，byte_index————byte位置编号
        return 'write_success'
    except Exception as e:
        print(f'DB{db_index}.DBB{byte_index},write error:{str(e)}')
        return 'write_failed'


# rfid写入
def rfid_write(plc, db_index: int, byte_index: int, value: str):
    try:
        a = 0
        for i in [0, 2, 4, 6, 8, 10, 12, 14]:
            value_16 = value[i: i + 2]
            value_10 = int(value_16, 16)
            byte_index_new = byte_index + a
            site_data = bytearray(1)  # 声明数据写入的byte位数
            util.set_byte(site_data, 0, value_10)  # bite_index——bool值写入的bite位置，其他类型没有此参数
            plc.write_area(snap7.client.Areas.DB, db_index, byte_index_new,
                           site_data)  # db_index————db区编号，byte_index————byte位置编号
            a += 1
        return 'write_success'
    except Exception as e:
        print(f'rfid,DB{db_index}.DBB{byte_index},write error:{str(e)}')
        return 'write_failed'


def plc_write_batch(plc, db, write_args_list: list, log_name: str):
    for i in write_args_list:
        # i={'value_index':点位，'value':写入值}
        value_index = i['value_index']
        value = i['value']

        if re.match(r'^(DB)([0-9]+)(\.)(DBW)([0-9]+)$', value_index, re.I) \
                and re.match(r'^[0-9]+$', value):
            match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBW)([0-9]+)$', value_index, re.I)
            x = int(match_value_index.group(2))  # 获取db点db区位置编号
            y = int(match_value_index.group(5))  # 获取db点byte位置编号
            while True:
                read_value = str(dbw_read_alone(plc, x, y))
                # 如果读取失败
                if read_value == 'read_failed':
                    log = f"DB{x}.DBW{y}写入{value}读取校验时报错"
                    db.write_log_no_task_number(log_name, log)
                    return 'batch_write_failed'
                # 如果读取值等于写入值
                elif read_value == value:
                    break
                # 开始写入
                else:
                    write_result = dbw_write(plc, x, y, value)
                    if write_result == 'write_failed':
                        log = f"DB{x}.DBW{y}写入{value}写入时报错"
                        db.write_log_no_task_number(log_name, log)
                        return 'batch_write_failed'
                    else:
                        continue

        elif re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', value_index, re.I) \
                and re.match(r'^[0-9]+$', value):
            match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', value_index, re.I)
            x = int(match_value_index.group(2))  # 获取db点db区位置编号
            y = int(match_value_index.group(5))  # 获取db点byte位置编号
            while True:
                read_value = str(dbd_read_alone(plc, x, y))
                # 如果读取失败
                if read_value == 'read_failed':
                    log = f"DB{x}.DBD{y}写入{value}读取校验时报错"
                    db.write_log_no_task_number(log_name, log)
                    return 'batch_write_failed'
                # 如果读取值等于写入值
                elif read_value == value:
                    break
                # 开始写入
                else:
                    write_result = dbd_write(plc, x, y, value)
                    if write_result == 'write_failed':
                        log = f"DB{x}.DBD{y}写入{value}写入时时报错"
                        db.write_log_no_task_number(log_name, log)
                        return 'batch_write_failed'
                    else:
                        continue

        elif re.match(r'^(DB)([0-9]+)(\.)(DBX)([0-9]+)(\.)([0-7])$', value_index, re.I) \
                and (value.lower() == 'true' or value.lower() == 'false'):
            match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBX)([0-9]+)(\.)([0-7])$', value_index, re.I)
            x = int(match_value_index.group(2))  # 获取db点db区位置编号
            y = int(match_value_index.group(5))  # 获取db点byte位置编号
            z = int(match_value_index.group(7))  # 获取db点bite位置编号
            while True:
                read_value = str(dbx_read_alone(plc, x, y, z))
                # 如果读取失败
                if read_value == 'read_failed':
                    log = f"DB{x}.DBX{y}.{z}写入{value}读取校验时报错"
                    db.write_log_no_task_number(log_name, log)
                    return 'batch_write_failed'
                # 如果读取值等于写入值
                elif read_value == value:
                    break
                # 开始写入
                else:
                    write_result = dbx_write(plc, x, y, z, value)
                    if write_result == 'write_failed':
                        log = f"DB{x}.DBX{y}.{z}写入{value}写入时时报错"
                        db.write_log_no_task_number(log_name, log)
                        return 'batch_write_failed'
                    else:
                        continue

        else:
            log = f"{value_index}写入{value}匹配写入方法失败！"
            db.write_log_no_task_number(log_name, log)

    log = f">批量写入{write_args_list},写入完成！"
    db.write_log_no_task_number(log_name, log)
    return 'batch_write_success'


def plc_write_alone(plc, value_index: str, value: str, date_type='int'):
    try:
        # 如果是Q点
        if re.match(r'^(Q)([0-9]+)(\.)([0-7])$', value_index, re.I) \
                and (value.lower() == 'true' or value == ''):
            match_value_index = re.match(r'^(Q)([0-9]+)(\.)([0-7])$', value_index, re.I)
            x = int(match_value_index.group(2))  # 获取q点byte位置编号
            y = int(match_value_index.group(4))  # 获取q点bite位置编号
            while True:
                read_value = str(pa_read_alone(plc, x, y))
                # 如果读取失败
                if read_value == 'read_failed':
                    return 'write_failed'
                # 如果读取值等于写入值
                elif read_value == value:
                    return 'write_success'
                # 开始写入
                else:
                    write_result = pa_write(plc, x, y, value)
                    if write_result == 'write_failed':
                        return 'write_failed'
                    else:
                        continue
        # 如果是M点
        elif re.match(r'^(M)([0-9]+)(\.)([0-7])$', value_index, re.I) \
                and (value.lower() == 'true' or value == '' or value == 'false'):
            match_value_index = re.match(r'^(M)([0-9]+)(\.)([0-7])$', value_index, re.I)
            x = int(match_value_index.group(2))  # 获取m点byte位置编号
            y = int(match_value_index.group(4))  # 获取m点bite位置编号
            while True:
                read_value = str(mk_read_alone(plc, x, y))
                # 如果读取失败
                if read_value == 'read_failed':
                    return 'write_failed'
                # 如果读取值等于写入值
                elif read_value == value:
                    return 'write_success'
                # 开始写入
                else:
                    write_result = m_write(plc, x, y, value)
                    if write_result == 'write_failed':
                        return 'write_failed'
                    else:
                        continue
        # 如果是DBX点
        elif re.match(r'^(DB)([0-9]+)(\.)(DBX)([0-9]+)(\.)([0-7])$', value_index, re.I) \
                and (value.lower() == 'true' or value.lower() == 'false'):
            match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBX)([0-9]+)(\.)([0-7])$', value_index, re.I)
            x = int(match_value_index.group(2))  # 获取db点db区位置编号
            y = int(match_value_index.group(5))  # 获取db点byte位置编号
            z = int(match_value_index.group(7))  # 获取db点bite位置编号
            while True:
                read_value = str(dbx_read_alone(plc, x, y, z))
                # 如果读取失败
                if read_value == 'read_failed':
                    return 'write_failed'
                # 如果读取值等于写入值
                elif read_value == value:
                    return 'write_success'
                # 开始写入
                else:
                    write_result = dbx_write(plc, x, y, z, value)
                    if write_result == 'write_failed':
                        return 'write_failed'
                    else:
                        continue
        # 如果是DBB点
        elif re.match(r'^(DB)([0-9]+)(\.)(DBB)([0-9]+)$', value_index, re.I) \
                and re.match(r'^[0-9]+$', value):
            match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBB)([0-9]+)$', value_index, re.I)
            x = int(match_value_index.group(2))  # 获取db点db区位置编号
            y = int(match_value_index.group(5))  # 获取db点byte位置编号
            while True:
                read_value = str(dbb_read_alone(plc, x, y))
                # 如果读取失败
                if read_value == 'read_failed':
                    return 'write_failed'
                # 如果读取值等于写入值
                elif read_value == value:
                    return 'write_success'
                # 开始写入
                else:
                    write_result = dbb_write(plc, x, y, value)
                    if write_result == 'write_failed':
                        return 'write_failed'
                    else:
                        continue
        # 如果是DBW点
        elif re.match(r'^(DB)([0-9]+)(\.)(DBW)([0-9]+)$', value_index, re.I) \
                and re.match(r'^[0-9]+$', value):
            match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBW)([0-9]+)$', value_index, re.I)
            x = int(match_value_index.group(2))  # 获取db点db区位置编号
            y = int(match_value_index.group(5))  # 获取db点byte位置编号
            while True:
                read_value = str(dbw_read_alone(plc, x, y))
                # 如果读取失败
                if read_value == 'read_failed':
                    return 'write_failed'
                # 如果读取值等于写入值
                elif read_value == value:
                    return 'write_success'
                # 开始写入
                else:
                    write_result = dbw_write(plc, x, y, value)
                    if write_result == 'write_failed':
                        return 'write_failed'
                    else:
                        continue
        # 如果是DBD浮点数点
        elif re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', value_index, re.I) \
                and (date_type == 'float' or re.match(r'^[0-9]+(\.)[0-9]+$', value)):
            match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', value_index, re.I)
            x = int(match_value_index.group(2))  # 获取db点db区位置编号
            y = int(match_value_index.group(5))  # 获取db点byte位置编号
            while True:
                read_value = str(dbdf_read_alone(plc, x, y))
                # 如果读取失败
                if read_value == 'read_failed':
                    return 'write_failed'
                # 如果读取值等于写入值
                elif read_value in value:
                    return 'write_success'
                # 开始写入
                else:
                    write_result = dbd_write_float(plc, x, y, value)
                    if write_result == 'write_failed':
                        return 'write_failed'
                    else:
                        continue
        # 如果是DBD整形
        elif re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', value_index, re.I) \
                and re.match(r'^[0-9]+$', value):
            match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBD)([0-9]+)$', value_index, re.I)
            x = int(match_value_index.group(2))  # 获取db点db区位置编号
            y = int(match_value_index.group(5))  # 获取db点byte位置编号
            while True:
                read_value = str(dbd_read_alone(plc, x, y))
                # 如果读取失败
                if read_value == 'read_failed':
                    return 'write_failed'
                # 如果读取值等于写入值
                elif read_value == value:
                    return 'write_success'
                # 开始写入
                else:
                    write_result = dbd_write(plc, x, y, value)
                    if write_result == 'write_failed':
                        return 'write_failed'
                    else:
                        continue
        # 如果是RFID
        elif re.match(r'^(DB)([0-9]+)(\.)(DBB)([0-9]+)$', value_index, re.I) \
                and value[0] == 'E' and len(value) == 16:
            match_value_index = re.match(r'^(DB)([0-9]+)(\.)(DBB)([0-9]+)$', value_index, re.I)
            x = int(match_value_index.group(2))  # 获取db点db区位置编号
            y = int(match_value_index.group(5))  # 获取db点byte位置编号
            while True:
                read_value = str(rfid_read_alone(plc, x, y))
                # 如果读取失败
                if read_value == 'read_failed':
                    return 'write_failed'
                # 如果读取值等于写入值
                elif read_value == value:
                    return 'write_success'
                # 开始写入
                else:
                    write_result = rfid_write(plc, x, y, value)
                    if write_result == 'write_failed':
                        return 'write_failed'
                    else:
                        continue
        else:
            return f'{value_index}写入{value}匹配写入方法失败！'
    except Exception as e:
        return  f'{value_index}写入{value}匹配写入报错：{str(e)}'


# Q点的单点位读取，返回value值
def pa_read_alone(plc, byte_index, bite_index):
    # 参数说明：snap7.client.Areas.DB————DB-DB区；PE，I区；PA，Q区
    # 参数说明：db_num————DB区的编号，I区和Q区写0
    # 参数说明：0————起始byte地址，注意不是bite地址
    # 参数说明：length————读取byte的长度
    try:
        data = plc.read_area(snap7.client.Areas.PA, 0, byte_index, 1)
        pa_value = str(util.get_bool(data, 0, bite_index)).lower()
        return pa_value
    except Exception as e:
        print(f'error:{str(e)}')
        return 'read_failed'


# M点的单点位读取，返回value值
def mk_read_alone(plc, byte_index, bite_index):
    # 参数说明：snap7.client.Areas.DB————DB-DB区；PE，I区；PA，Q区
    # 参数说明：db_num————DB区的编号，I区和Q区写0
    # 参数说明：0————起始byte地址，注意不是bite地址
    # 参数说明：length————读取byte的长度
    try:
        data = plc.read_area(snap7.client.Areas.MK, 0, byte_index, 1)
        mk_value = str(util.get_bool(data, 0, bite_index)).lower()
        return mk_value
    except Exception as e:
        print(f'error:{str(e)}')
        return 'read_failed'


# dbx的单点位读取，返回value值
def dbx_read_alone(plc, db_num: int, byte_index: int, bite_index: int):
    # 参数说明：snap7.client.Areas.DB————DB-DB区；PE，I区；PA，Q区
    # 参数说明：db_num————DB区的编号，I区和Q区写0
    # 参数说明：0————起始byte地址，注意不是bite地址
    # 参数说明：length————读取byte的长度
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 1)
        value = str(util.get_bool(data, 0, bite_index)).lower()
        return value
    except Exception as e:
        print(f'error:{str(e)}')
        return 'read_failed'


# dbb的单点位读取，返回value值
def dbb_read_alone(plc, db_num: int, byte_index: int):
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 1)
        value = util.get_sint(data, 0)
        print(f'读取DB{db_num}.DBB{byte_index}的当前值为{value}')
        return value
    except Exception as e:
        print(f'DB{db_num}.DBB{byte_index},read error:{str(e)}')
        return 'read_failed'


# dbw的单点位读取，返回value值
def dbw_read_alone(plc, db_num: int, byte_index: int):
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 2)
        value = util.get_int(data, 0)
        return value
    except Exception as e:
        print(f'DB{db_num}.DBW{byte_index},read error:{str(e)}')
        return 'read_failed'


# dbd的浮点数单点位读取，返回value列表
def dbdf_read_alone(plc, db_num: int, byte_index: int):
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 4)
        value = util.get_real(data, 0)
        return value
    except Exception as e:
        print(f'error:{str(e)}')
        return 'read_failed'


# dbd的单点位读取，返回value列表
def dbd_read_alone(plc, db_num: int, byte_index: int):
    try:
        data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 4)
        value = util.get_dint(data, 0)
        return value
    except Exception as e:
        print(f'error:{str(e)}')
        return 'read_failed'


def rfid_read_alone(plc, db_num: int, byte_index: int):
    try:
        all_value = ''
        data = plc.read_area(snap7.client.Areas.DB, db_num, byte_index, 8)
        for i in range(0, 8):
            value_first = util.get_byte(data, i)
            value_end = hex(int(value_first))[2:].upper()
            if len(value_end) < 2:
                value_end = '0' + value_end
            all_value += str(value_end)
        return all_value
    except Exception as e:
        print(f'rfid,DB{db_num}.DBB{byte_index},read error:{str(e)}')
        return 'read_failed'



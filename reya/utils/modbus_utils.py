import asyncio
import time

import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp


class ModbusTcpUtils:
    def __init__(self, ip: str, port=502):
        self.master = modbus_tcp.TcpMaster(host=ip, port=port)
        self.master.set_timeout(5.0)

    def get_master(self):
        return self.master

    def execute(self, slave, function_code, starting_address, quantity_of_x=0, output_value=0, data_format="",
                expected_length=-1, write_starting_address_fc23=0, number_file=None, pdu="", returns_raw=False):

        self.master.execute(slave, function_code, starting_address, quantity_of_x, output_value, data_format,
                            expected_length, write_starting_address_fc23, number_file, pdu, returns_raw)

    # 设置DB区的值, 实数bit位代表bool值的情况
    # addr: 2300.2
    # val 0 or 1
    def set_db_bool(self, address: str, val=0):
        if '.' not in address:
            return False
        addr, bit_addr = address.split('.')
        bit_addr_desc = -(int(bit_addr) + 1)  # 0->-1, 1->-2
        res = self.master.execute(1, cst.READ_HOLDING_REGISTERS, int(addr), 1)[0]
        bool_str = bin(res)[2:].zfill(16)
        str_list = list(bool_str)
        str_list[bit_addr_desc] = str(val)
        z = "".join(str_list)
        new_val = int(z, 2)
        write_res = self.master.execute(1, cst.WRITE_SINGLE_REGISTER, int(addr), output_value=new_val)
        return write_res

    # 设置DB区的值， 实数bit位代表bool值的情况
    def get_db_bool(self, address):
        # bit_addr = detect_sites[name]
        addr, bit_addr = address.split('.')
        bit_addr_desc = -(int(bit_addr) + 1)
        res = self.master.execute(1, cst.READ_HOLDING_REGISTERS, int(addr), 1)[0]
        bool_str = bin(res)[2:].zfill(16)
        str_list = list(bool_str)
        bool_val = str_list[bit_addr_desc]
        if bool_val == "1":
            return True
        return False

    def write_single_register(self, addr, val):
        res = self.master.execute(1, cst.WRITE_SINGLE_REGISTER, int(addr), output_value=val)
        return res[0]

    def read_singe_register(self, addr, data_type: str):
        num = 1
        if data_type.lower() == "real":
            num = 1
        if data_type.lower() == "dword":
            num = 2
        res = self.master.execute(1, cst.READ_HOLDING_REGISTERS, int(addr), num)
        return res[0]

    def detect_wait_bool(self, address, wait_status=True, out_time=None):
        start_time = time.time()
        # print('self.get_db_bool(address)', self.get_db_bool(address))
        while self.get_db_bool(address) != wait_status:
            time.sleep(0.1)
            end_time = time.time()
            span_time = end_time - start_time
            if out_time is not None:
                if span_time > out_time:
                    return False
        return True

    async def detect_wait_bool_async(self, address, wait_status=True, out_time=None):
        start_time = time.time()
        print('self.get_db_bool(address)', self.get_db_bool(address))
        while self.get_db_bool(address) != wait_status:
            await asyncio.sleep(50 / 1000)
            end_time = time.time()
            span_time = end_time - start_time
            if out_time is not None:
                if span_time > out_time:
                    return False
        return True

    async def detect_wait_real(self, address, wait_val, data_type=None, out_time=None):
        start_time = time.time()
        while self.read_singe_register(address, data_type) != wait_val:
            await asyncio.sleep(50 / 1000)
            end_time = time.time()
            span_time = end_time - start_time
            if out_time is not None:
                if span_time > out_time:
                    return False
        return True

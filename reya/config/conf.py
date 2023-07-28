redis_local_host = '127.0.0.1'
redis_local_port = 6379

redis_server_host = '192.168.0.104'
redis_server_port = 6379

# 初始化时更新替换
device_name = "ZN-122/014"

# 是在左还是右（树莓派）
left_or_right = "right"

redis_chengliao_task_key = f"reya_task:{device_name}:chengliao:{left_or_right}"

redis_station_working_info_key = "station_working_info"

redis_plan_local_info = "redis_plan_local_info:{}"
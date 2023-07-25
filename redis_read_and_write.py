import redis
import time


def get_redis(host):
    if host == "server":
        ip = "127.0.0.1"
    elif host in ["ZN-122/007#01", "ZN-122/007#02", "ZN-122/007#03", "ZN-122/007#04"]:
        ip = "127.0.0.1"
    else:
        return "get_redis_failed"
    pool = redis.ConnectionPool(host=ip, port=6379, db=0, decode_responses=True)
    r = redis.StrictRedis(connection_pool=pool)  # 建立redis连接
    return r


def redis_write_initial(host: str, key_list: list, value: str):  # 用列表数据初始化redis的key值
    r = get_redis(host)
    for i in range(0, len(key_list)):
        # 遍历列表元素，逐一写入redis的key值，nx=True指的是只有不存在的key值会被写入，
        # 默认value的值为False
        r.set(key_list[i], value, nx=True)


def redis_write_ing(host: str, key_list, value_list):  # 将key列表和value列表的元素按照顺序逐一写入redis的key和value
    r = get_redis(host)
    for i in range(0, len(key_list)):
        r.set(key_list[i], str(value_list[i]))  # xx=True指的是只有存在的key的value会被写入


def redis_set(host: str, key: str, value):
    r = get_redis(host)
    return r.set(key, value)


def redis_setnx(host: str, key: str, value):
    r = get_redis(host)
    return r.set(key, value, nx=True)


def redis_get(host: str, key):
    r = get_redis(host)
    return r.get(key)


# redis取值后自动递增，默认递增1
def redis_set_add1(host: str, key):
    r = get_redis(host)
    return r.incr(key)


# redis取值后自动递增，默认递减1
def redis_set_cut1(host: str, key):
    r = get_redis(host)
    return r.decr(key)


# redis列表，从最左边插入值，不存在时新建
def redis_lpush(host: str, key: str, value: str):
    r = get_redis(host)
    return r.lpush(key, value)


# redis列表，从最右边插入值，不存在时新建
def redis_rpush(host: str, key: str, value: str):
    r = get_redis(host)
    return r.rpush(key, value)


# redis列表长度，不存在时返回0
def redis_llen(host: str, name: str):
    r = get_redis(host)
    return r.llen(name)


# redis列表，截取start-end片段
def redis_lrange(host: str, name: str, start: int, end: int):
    r = get_redis(host)
    return r.lrange(name, start, end)


# redis列表，删除最左边的值并返回最左边的值
def redis_lpop(host: str, name: str):
    r = get_redis(host)
    return r.lpop(name)


# redis列表，删除指定的值
def redis_lrem(host: str, name: str, count: int, value: str):
    r = get_redis(host)
    return r.lrem(name, count, value)


# redis列表，在指定的值前或后插入元素
def redis_linsert(host: str, name: str, before_or_after, value_old: str, value_new: str):
    r = get_redis(host)
    return r.linsert(name, before_or_after, value_old, value_new)


# redis列表，通过索引获取列表元素
def redis_lindex(host: str, name: str, index: int):
    r = get_redis(host)
    return r.lindex(name, index)


# redis哈希中增加多个键值对，不存在时新增
def redis_hmset(host: str, name: str, mapping: dict):
    r = get_redis(host)
    return r.hmset(name, mapping)


# redis哈希中增加单个键值对，不存在时新增
def redis_hset(host: str, name: str, key: str, value: str):
    r = get_redis(host)
    return r.hset(name, key, value)


# redis哈希中获取指定key的值
def redis_hget(host: str, name: str, key: str):
    r = get_redis(host)
    return r.hget(name, key)


# redis哈希中删除指定的key
def redis_hdel(host: str, name: str, key: str):
    r = get_redis(host)
    return r.hdel(name, key)


# redis删除指定name
def redis_del(host: str, name: str):
    r = get_redis(host)
    return r.delete(name)


# 用redis 实现分布式锁，通过将 now time + lock_expires 存入value, 用于判断锁是否过期
def redis_lock(host: str, name: str, lock_expires=2):
    lock = redis_setnx(host, name, int(time.time()) + lock_expires)
    if lock == 1:
        return True
    lock_val = redis_get(host, name)
    if not lock_val:
        return False
    if int(time.time()) > int(lock_val):
        # 锁已过期，可以重新设置
        redis_del(host, name)
    return False


if __name__ == '__main__':
    value = redis_hget("ZN-122/007#03", "production_plan:12345678", "production_status")
    print(value)
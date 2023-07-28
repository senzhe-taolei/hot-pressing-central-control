import redis


class RedisUtils:
    def __init__(self, ip, port=6379, db=0):
        pool = redis.ConnectionPool(host=ip, port=port, db=db, decode_responses=True)
        self.r = redis.StrictRedis(connection_pool=pool)  # 建立redis连接

    def redis_write_initial(self, key_list: list, value: str):  # 用列表数据初始化redis的key值
        for i in range(0, len(key_list)):
            # 遍历列表元素，逐一写入redis的key值，nx=True指的是只有不存在的key值会被写入，
            # 默认value的值为False
            self.r.set(key_list[i], value, nx=True)

    def redis_write_ing(self, key_list, value_list):  # 将key列表和value列表的元素按照顺序逐一写入redis的key和value
        for i in range(0, len(key_list)):
            self.r.set(key_list[i], str(value_list[i]))  # xx=True指的是只有存在的key的value会被写入

    def redis_set(self, key: str, value):
        return self.r.set(key, value)

    def redis_get(self, key):
        return self.r.get(key)

    # redis取值后自动递增，默认递增1
    def redis_set_add1(self, key):
        return self.r.incr(key)

    # redis取值后自动递增，默认递减1
    def redis_set_cut1(self, key):
        return self.r.decr(key)

    # redis列表，从最左边插入值，不存在时新建
    def redis_lpush(self, key: str, value: str):
        return self.r.lpush(key, value)

    # redis列表，从最右边插入值，不存在时新建
    def redis_rpush(self, key: str, value: str):
        return self.r.rpush(key, value)

    # redis列表长度，不存在时返回0
    def redis_llen(self, name: str):
        return self.r.llen(name)

    # redis列表，截取start-end片段
    def redis_lrange(self, name: str, start: int, end: int):
        return self.r.lrange(name, start, end)

    # redis列表，删除最左边的值并返回最左边的值
    def redis_lpop(self, name: str):
        return self.r.lpop(name)

    # redis列表，删除指定的值
    def redis_lrem(self, name: str, count: int, value: str):
        return self.r.lrem(name, count, value)

    # redis列表，在指定的值前或后插入元素
    def redis_linsert(self, name: str, before_or_after, value_old: str, value_new: str):
        return self.r.linsert(name, before_or_after, value_old, value_new)

    # redis列表，通过索引获取列表元素
    def redis_lindex(self, name: str, index: int):
        return self.r.lindex(name, index)

    # redis哈希中增加多个键值对，不存在时新增
    def redis_hmset(self, name: str, mapping: dict):
        return self.r.hmset(name, mapping)

    # redis哈希中增加单个键值对，不存在时新增
    def redis_hset(self, name: str, key: str, value: str):
        return self.r.hset(name, key, value)

    # redis哈希中获取指定key的值
    def redis_hget(self, name: str, key: str):
        return self.r.hget(name, key)

    # redis哈希中删除指定的key
    def redis_hdel(self, name: str, key: str):
        return self.r.hdel(name, [key])

    # redis删除指定name
    def redis_del(self, name: str):
        return self.r.delete(name)

    # redis
    def redis_hgetall(self, name: str):
        return self.r.hgetall(name)

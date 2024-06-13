import redis 


redis = redis.Redis(host='localhost', port=6379, db=0)


# invia un messaggio a redis
redis.publish('channel', 'hello world')
import pymysql.cursors
import yaml
import redis

cfg = yaml.safe_load(open('config.yaml', 'r'))

# Подключение к базе данных
connection = pymysql.connect(host=cfg["mysql"]["host"],
                             user=cfg["mysql"]["user"],
                             password=cfg["mysql"]["password"],
                             database=cfg["mysql"]["database"])

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


def cur(_type, arg):
    connection.autocommit(True)
    with connection.cursor() as cursor:
        match _type:
            case "query":
                cursor.execute(arg)
            case "fetch":
                cursor.execute(arg)
                result = cursor.fetchone()
                return result
            case "fetchall":
                cursor.execute(arg)
                result = cursor.fetchall()
                return result

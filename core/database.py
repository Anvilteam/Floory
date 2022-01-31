import pymysql.cursors
import yaml


cfg = yaml.safe_load(open('config.yaml', 'r'))

# Connect to the database
connection = pymysql.connect(host=cfg["mysql"]["host"],
                             user=cfg["mysql"]["user"],
                             password=cfg["mysql"]["password"],
                             database=cfg["mysql"]["database"],
                             cursorclass=pymysql.cursors.DictCursor)


async def cur(_type, arg):
    connection.autocommit(True)
    with connection.cursor() as cursor:
        match _type:
            case "query":
                cursor.execute(arg)
            case "fetch":
                await cursor.execute(arg)
                result = await cursor.fetchone()
                return f"{str(result)[2:-3]}"
            case "fetchall":
                await cursor.execute(arg)
                result = await cursor.fetchall()
                return f"{result}"

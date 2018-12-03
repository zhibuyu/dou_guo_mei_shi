import pymongo
from pymongo.collection import Collection


# mongodb 连接
class Connect_mogo(object):
    def __init__(self):
        self.client = pymongo.MongoClient(host='192.168.67.128',port=27017)
        self.db_data = self.client['dou_guo']

    # 插入数据
    def insert_item(self,item,table_name):
        print("插入数据的表",table_name)
        db_collection = Collection(self.db_data,table_name)
        db_collection.insert_many(item)


mongo_info = Connect_mogo()
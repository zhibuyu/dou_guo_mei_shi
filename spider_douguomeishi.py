import  requests
import json
# 引入了队列
from multiprocessing import  Queue
from handle_mongo import mongo_info
from concurrent.futures import ThreadPoolExecutor #线程池

# 创建队列
queue_list = Queue()
start = 0
end = 20

#封装请求函数，相同的请求头
def hndel_request(url,data):
    header = {
        "client": "4",
        "version": "6926.2",
        "device": "OPPO R11",
        "sdk": "19,4.4.2",
        "imei": "866174010224216",
        "channel": "d0525",
        # "mac": "E0:D5:5E:6E:65:71",
        "resolution": "1280*720",
        "dpi": "1.5",
        # "android-id": "e0d55e6e65717261",
        # "pseudo-id": "e6e65717261e0d55",
        "brand": "OPPO",
        "scale": "1.5",
        "timezone": "28800",
        "language": "zh",
        "cns": "3",
        # "carrier": "CMCC",
        "imsi": "460072242139411",
        "user-agent": "Mozilla/5.0 (Linux; Android 4.4.2; OPPO R11 Build/NMF26X) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36",
        "reach": "1",
        "newbie": "0",
        # "lon": "101.565413",
        # "lat": "40.001975",
        # "cid": "152900",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        # "Cookie": "duid=57876712",
        "Host": "api.douguo.net",
        # "Content-Length": "68",
    }
    # 设置代理ip
    proxy = {'http': '116.7.176.75:8118',
             'http': '183.129.207.82:11519',
             'http': '120.77.247.147:80',
             'http': '183.129.207.82:11234',
             'http': '183.129.207.82:11692',
             'http': '183.129.207.82:11827',
             'http': '121.232.148.118:9000',
             'http': '101.76.209.69:1080',
             'http': '111.75.193.25:48449',
             'http': '120.26.199.103:8118',
             'http': '111.43.70.58:51547',
             'http': '27.214.112.102:9000',
             'http': '124.42.7.103:80',
             'http': '113.69.137.222:8118',
             'http': '117.191.11.80:8080',
             'http': '118.182.33.6:42801',
             'http': '123.206.17.233:8118',
             'http': '101.200.50.18:8118',
             'http': '117.90.137.212:9000',
             'http': '111.75.193.25:48449',
             'http': '211.138.248.108:59692',
             'http': '112.25.6.24:80',
             'http': '60.173.203.83:31194'
             }
    # 请求函数构造好了
    response = requests.post(url=url,headers=header,data=data,proxies=proxy)
    return response

# 菜谱分类页面
def handle_index():
    url = 'http://api.douguo.net/recipe/flatcatalogs'
    data = {
        "client": "4",
        # "_session": "1543814714644866174010224216",
        # "v": "1543490229",
        "_vs": "2305",
    }
    response = hndel_request(url=url,data=data)
    index_response_dict = json.loads(response.text)
    for index_item in index_response_dict['result']['cs']:
        type1_name = index_item['name']
        # print("开始的类型==》" +type1_name)
        for index_item_1 in index_item['cs']:
            type2_name = type1_name+'.'+index_item_1['name']
            # print("二级目录==》" + type2_name)
            for item in index_item_1['cs']:
                type3_name = type2_name +'.'+ item['name'] #包含了各级目录名，后面作为数据库表名
                # print("三级目录==》" + type3_name)
                data_2 = {
                    "client": "4",
                    # "_session": "1543814714644866174010224216",
                    "keyword": item['name'],
                    "order": "0",
                    "_vs": "400",
                }
                data_3 = {
                    'type_name':type3_name,
                    'data':data_2
                }
                # 将data_2放进队列中
                queue_list.put(data_3)


# 线程的处理函数
# 请求的是菜谱列表和详情页
def handle_recipe_list(data_3):
    type_name = data_3['type_name']
    data = data_3['data']
    print("当前处理的名称==>"+data['keyword']+"=将要存储的表名==>"+type_name)
    recipe_list_url = 'http://api.douguo.net/recipe/v2/search/'+str(start)+'/'+str(end)
    handle_request_recipes(recipe_list_url,data,type_name)


def handle_request_recipes(url,data,type_name):
    print("当前请求的列表url：", url)
    global start
    global end
    # 获得菜谱列表数据
    recipe_lst_response = hndel_request(url=url,data=data)
    recipe_list_resonse_dict = json.loads(recipe_lst_response.text)
    recipe_lists = recipe_list_resonse_dict['result']['list']
    if recipe_lists:
        for item in recipe_lists:
            recipe_info = {}
            recipe_info['ingredients'] = data['keyword']  # 食材
            if item['type'] == 13:
                item_info = item['r']
                recipe_info['user_name'] = item_info['an']  # 食谱作者名
                recipe_info['ingredients_id'] = item_info['id']  # 食材id
                recipe_info['describe'] = item_info['cookstory'].replace('\n', '').replace(' ', '')
                recipe_info['recipe_name'] = item_info['n']  # 菜谱名
                recipe_info['recipe_img'] = item_info['img']  # 菜谱照片
                recipe_info['seasoning_list'] = item_info['major']  # 菜谱调料
                detail_url = 'http://api.douguo.net/recipe/detail/' + str(recipe_info['ingredients_id'])
                detail_data = {
                    "client": "4",
                    # "_session": "1543814714644866174010224216",
                    "author_id": "0",
                    "_vs": "2801",
                    "_ext": '{"query":{"id":' + str(recipe_info['ingredients_id']) + ',"kw":' + recipe_info[
                        'ingredients'] + ',"idx":"1","src":"2801","type":"13"}}',
                }
                # 获得菜谱详情数据
                detail_reponse = hndel_request(url=detail_url,data=detail_data)
                detail_reponse_dict = json.loads(detail_reponse.text)
                recipe_info['user_photo'] = detail_reponse_dict['result']['recipe']['user']['avatar_medium']  # 食谱作者头像
                recipe_info['tips'] = detail_reponse_dict['result']['recipe']['tips']
                recipe_info['cook_step'] = detail_reponse_dict['result']['recipe']['cookstep']
                print('当前菜谱名为：'+str(recipe_info['recipe_name'])+'入库的'+type_name+'表')
                # mongodb数据插入
                mongo_info.insert_item(recipe_info,type_name)
            else:
                continue
        start = end + 1
        end = start + len(recipe_lists)
        recipe_list_url1 = 'http://api.douguo.net/recipe/v2/search/' + str(start) + '/' + str(end)
        handle_request_recipes(recipe_list_url1, data, type_name)
    else:
        print('***恭喜，数据爬取完毕***')


handle_index()
# 实现多线程抓取，引入了线程池
pool = ThreadPoolExecutor(max_workers=30)#设置最大线程数
while queue_list.qsize()>0:
    pool.submit(handle_recipe_list,queue_list.get())
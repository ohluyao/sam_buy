from distutils.command.config import config
from email import header
import json
from textwrap import indent
from xml.sax import default_parser_list
import requests
from time import sleep
import datetime

# ## init config ###
# 填写个人信息

deviceid = 'x'
authtoken = 'x'
deliveryType = '0'  # 1：极速达 2：全城配送
cartDeliveryType = 1  # 1：极速达 2：全城配送
addressId = ''
storeId = ''
promotionId = ''
# ## init config over ###

## shared API data ##

commonHeaders = {}

## shared API data ##


def getAmout(goodlist):
    global amout
    myUrl = 'https://api-sams.walmartmobile.cn/api/v1/sams/trade/settlement/getSettleInfo'
    headers = commonHeaders
    data = {
        "goodsList": goodlist,
        "uid": uid,
        "addressId": addressList_item.get('addressId'),
        "deliveryInfoVO": {
            "storeDeliveryTemplateId": good_store.get('storeDeliveryTemplateId'),
            "deliveryModeId": good_store.get('deliveryModeId'),
            "storeType": good_store.get('storeType')
        },
        "cartDeliveryType": cartDeliveryType,
        "storeInfo": {
            "storeId": good_store.get('storeId'),
            "storeType": good_store.get('storeType'),
            "areaBlockId": good_store.get('areaBlockId')
        },
        "isSelfPickup": 0,
        "floorId": 1,
    }

    if promotionId != "":
        data["couponList"] = [{"promotionId":promotionId,"storeId":good_store.get('storeId')}]

    try:
        ret = requests.post(url=myUrl, headers=headers, data=json.dumps(data))
        myRet = json.loads(ret.text)
        #print(json.dumps(myRet, indent = 3, ensure_ascii = False))

        code = myRet['code']
        #print(json.dumps(myRet, indent=3, ensure_ascii=False))
        print('getAmount returned: ', code,)
        if code == "NO_MATCH_DELIVERY_MODE":
            return 0
        amout = myRet['data'].get('totalAmount')

        return amout
    except Exception as e:
        print('getAmout [Error]: ' + str(e))
    

def address_list():
    global addressList_item
    print('###初始化地址')
    myUrl = 'https://api-sams.walmartmobile.cn/api/v1/sams/sams-user/receiver_address/address_list'
    headers = commonHeaders
    ret = requests.get(url=myUrl, headers=headers)
    myRet = json.loads(ret.text)
    #print(json.dumps(myRet, indent = 3, ensure_ascii=False))
    addressList = myRet['data'].get('addressList')
    addressList_item = []

    s = -1
    for i in range(0, len(addressList)):
        if addressId != "" and addressList[i].get("addressId") == addressId:
            s = i
        addressList_item.append({
            'addressId': addressList[i].get("addressId"),
            'mobile': addressList[i].get("mobile"),
            'name': addressList[i].get("name"),
            'countryName': addressList[i].get('countryName'),
            'provinceName': addressList[i].get('provinceName'),
            'cityName': addressList[i].get('cityName'),
            'districtName': addressList[i].get('districtName'),
            'receiverAddress': addressList[i].get('receiverAddress'),
            'detailAddress': addressList[i].get('detailAddress'),
            'latitude': addressList[i].get('latitude'),
            'longitude': addressList[i].get('longitude')
        })
        print('[' + str(i) + ']' + '[' + addressList[i].get("addressId") + ']' + addressList[i].get("name") + addressList[i].get("mobile") + addressList[i].get("districtName") + addressList[i].get("receiverAddress"))
    if s == -1:
        print('根据编号选择地址:')
        s = int(input())
    else:
        print('使用默认地址：',s)
    addressList_item = addressList_item[s]
    # print(addressList_item)
    return addressList_item


def getRecommendStoreListByLocation(latitude, longitude):
    global uid
    global good_store

    storeList_item = []
    print('###初始化商店')
    myUrl = 'https://api-sams.walmartmobile.cn/api/v1/sams/merchant/storeApi/getRecommendStoreListByLocation'
    data = {
        'longitude': longitude,
        'latitude': latitude}
    headers = commonHeaders    
    try:
        ret = requests.post(url=myUrl, headers=headers, data=json.dumps(data))
        myRet = json.loads(ret.text)
        storeList = myRet['data'].get('storeList')
        s = -1
        for i in range(0, len(storeList)):
            if storeId != "" and storeList[i].get("storeId") == storeId:
                s = i
            storeList_item.append(
                {
                    'storeType': storeList[i].get("storeType"),
                    'storeId': storeList[i].get("storeId"),
                    'areaBlockId': storeList[i].get('storeAreaBlockVerifyData').get("areaBlockId"),
                    'storeDeliveryTemplateId': storeList[i].get('storeRecmdDeliveryTemplateData').get(
                        "storeDeliveryTemplateId"),
                    'deliveryModeId': storeList[i].get('storeDeliveryModeVerifyData').get("deliveryModeId"),
                    'storeName': storeList[i].get("storeName")
                })
            print('[' + str(i) + ']' + storeList_item[i].get("storeId") + storeList_item[i].get("storeName"))
        if s == -1:
            print('根据编号下单商店:')
            s = int(input())
        else:
            print('使用默认商店：', s)
        good_store = storeList_item[s]
        uidUrl = 'https://api-sams.walmartmobile.cn/api/v1/sams/sams-user/user/personal_center_info'
        ret = requests.get(url=uidUrl, headers=commonHeaders)
        # print(ret.text)
        uidRet = json.loads(ret.text)
        uid = uidRet['data']['memInfo']['uid']
        return storeList_item, uid
        # print(storeList_item)

    except Exception as e:
        print('getRecommendStoreListByLocation [Error]: ' + str(e))
        return False


def getUserCart(addressList, storeList, uid):
    global goodlist
    global amount

    myUrl = 'https://api-sams.walmartmobile.cn/api/v1/sams/trade/cart/getUserCart'
    data = {
        # YOUR SELF
        "uid": uid, "deliveryType": deliveryType, "deviceType": "ios", "storeList": storeList, "parentDeliveryType": 1,
        "homePagelongitude": addressList.get('longitude'), "homePagelatitude": addressList.get('latitude')
    }
    headers = commonHeaders
    try:
        ret = requests.post(url=myUrl, headers=headers, data=json.dumps(data))
        # print(ret.text)
        myRet = json.loads(ret.text)
        # print(myRet['data'].get('capcityResponseList')[0])
        normalGoodsList = (myRet['data'].get('floorInfoList')[0].get('normalGoodsList'))
        # time_list = myRet['data'].get('capcityResponseList')[0].get('list')
        for i in range(0, len(normalGoodsList)):
            spuId = normalGoodsList[i].get('spuId')
            storeId = normalGoodsList[i].get('storeId')
            quantity = normalGoodsList[i].get('quantity')
            goodlistitem = {
                "spuId": spuId,
                "storeId": storeId,
                "isSelected": 'true',
                "quantity": quantity,
            }
            print('目前有库存：' + normalGoodsList[i].get('goodsName') + '\t#数量：' + str(quantity) + '\t#金额：' + str(
                int(normalGoodsList[i].get('price')) / 100) + '元')
            goodlist.append(goodlistitem)
            
        amount = int(getAmout(goodlist))
        print('###获取购物车商品成功,总金额：' + str(int(amount) / 100))

        if Capacity_index > 0:
            getCapacityData()
            return False
        else:
            return True
    except Exception as e:
        print('getUserCart [Error]: ' + str(e))
        return False


def getCapacityData():
    global startRealTime
    global endRealTime

    myUrl = 'https://api-sams.walmartmobile.cn/api/v1/sams/delivery/portal/getCapacityData'
    date_list = []
    for i in range(7):
        date_list.append(
            (datetime.datetime.now() + datetime.timedelta(days=i)).strftime('%Y-%m-%d')
        )

    data = {
        # YOUR SELF
        "perDateList": date_list, 
        "storeDeliveryTemplateId": good_store.get('storeDeliveryTemplateId')
    }
    headers = commonHeaders
    
    try:
        ret = requests.post(url=myUrl, headers=headers, data=json.dumps(data))
        print(ret)
        # print(ret.text)
        myRet = json.loads(ret.text)
        print(json.dumps(myRet, indent=3, ensure_ascii=False))
        print('#无库存释放,等待中')
        status = (myRet['data'].get('capcityResponseList')[0].get('dateISFull'))
        time_list = myRet['data'].get('capcityResponseList')[0].get('list')
        for i in range(0, len(time_list)):
            if not time_list[i].get('timeISFull'):
                startRealTime = time_list[i].get('startRealTime')
                endRealTime = time_list[i].get('endRealTime')
                # print(startRealTime)
                print('#【成功】获取配送时间')
                order(startRealTime, endRealTime)
                return True
    except Exception as e:
        print('getCapacityData [Error]: ' + str(e))
        return False


def order(startRealTime, endRealTime):
    global index
    print('下单：' + startRealTime)
    myUrl = 'https://api-sams.walmartmobile.cn/api/v1/sams/trade/settlement/commitPay'
    data = {"goodsList": goodlist,
            "invoiceInfo": {},
            "cartDeliveryType": cartDeliveryType, "floorId": 1, "amount": amount, "purchaserName": "",
            "settleDeliveryInfo": {"expectArrivalTime": startRealTime, "expectArrivalEndTime": endRealTime,
                                   "deliveryType": deliveryType}, "tradeType": "APP", "purchaserId": "", "payType": 0,
            "currency": "CNY", "channel": "wechat", "shortageId": 1, "isSelfPickup": 0, "orderType": 0,
            "uid": uid, "appId": "wx57364320cb03dfba", "addressId": addressList_item.get('addressId'),
            "deliveryInfoVO": {"storeDeliveryTemplateId": good_store.get('storeDeliveryTemplateId'),
                               "deliveryModeId": good_store.get('deliveryModeId'),
                               "storeType": good_store.get('storeType')}, "remark": "",
            "storeInfo": {"storeId": good_store.get('storeId'), "storeType": good_store.get('storeType'),
                          "areaBlockId": good_store.get('areaBlockId')},
            "shortageDesc": "其他商品继续配送（缺货商品直接退款）", "payMethodId": "1486659732"}

    if promotionId != "":
        data["couponList"] = [{"promotionId":promotionId,"storeId":good_store.get('storeId')}]
    
    headers = commonHeaders

    try:
        ret = requests.post(url=myUrl, headers=headers, data=json.dumps(data))
        print(ret.text)
        myRet = json.loads(ret.text)
        status = myRet.get('success')
        if status:
            print('【成功】哥，咱家有菜了~')
            import os
            file = r"nb.mp3"
            os.system(file)
            exit()
        else:
            print(myRet.get('code'))
            if myRet.get('code') == 'STORE_HAS_CLOSED':
                sleep(60)
                getCapacityData()
                return
            elif myRet.get('code') == 'LIMITED':
                index += 1
                if index > 5:
                    index = 0
                    getCapacityData()
                order(startRealTime, endRealTime)
                return
            elif myRet.get('code') == 'OUT_OF_STOCK':
                print('warning OUT_OF_STOCK')
                getUserCart(addressList_item, good_store, uid)
                return
            else:
                getCapacityData()
                return

    except Exception as e:
        print('order [Error]: ' + str(e))
        getCapacityData()
        return False


def init():
    # global address
    # global store
    with open('userconfig.json') as configFile:
        configData = json.load(configFile)
    
    global deviceid, authtoken, commonHeaders, addressId, storeId, promotionId
    if configData != None:
        addressId = configData.get('addressid')
        storeId = configData.get('storeid')
        deviceid = configData.get('deviceid')
        authtoken = configData.get('authtoken')
        promotionId = configData.get('promotionid')
    
    commonHeaders = {
        'Host': 'api-sams.walmartmobile.cn',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'Content-Type': 'application/json;charset=UTF-8',
        #'Content-Length': '156',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': 'SamClub/5.0.47 (iPhone; iOS 15.4.1; Scale/3.00)',
        'device-name': 'iPhone_12',
        'device-os-version': '15.4.1',
        'device-id': deviceid,
        'device-type': 'ios',
        'auth-token': authtoken,
        'app-version': '5.0.47.0'
    }

    address = address_list()
    store, uid = getRecommendStoreListByLocation(address.get('latitude'), address.get('longitude'))

    commonHeaders["latitude"] = address.get('latitude')
    commonHeaders["longitude"] = address.get('longitude')
    return address, store, uid


if __name__ == '__main__':
    count = 0
    index = 0
    Capacity_index = 0
    startRealTime = ''
    endRealTime = ''
    goodlist = []
    # 初始化
    address, store, uid = init()
  
    userCartReady = False
    while 1:
        count += 1
        print('Count: ', count)
        if userCartReady == False:
            print('getUserCart..')
            if(getUserCart(address, store, uid)):
                userCartReady = True
                getCapacityData()
        else:
            getCapacityData()
        sleep(0.5)
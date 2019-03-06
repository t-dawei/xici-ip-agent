#!/usr/bin/env python
# @auther: T

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import telnetlib
import os
import time
import schedule

Max_depth = 3

list_key = ['ip', 'port', 'address', 'type', 'scheme']
path = r'ip.json'

def parse_html_xici():
    base_url = r'https://www.xicidaili.com/nn/'
    list_url = []
    for i in range(1, Max_depth):
        list_url.append(base_url + str(i))
    list_res = []
    for url in list_url:
        user_agent = getRandUserAgent()
        print('目前使用的用户代理为：{}'.format(user_agent))
        headers = {
            'user-agent': user_agent
        }
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        print(soup.prettify())
        ip_list = soup.find('table', id='ip_list')
        tr_list = ip_list.find_all('tr')

        global list_key
        for i in range(1, len(tr_list)):
            td_list = tr_list[i].find_all('td')
            dict_temp = {}
            for j in range(1, 6):
                dict_temp[list_key[j-1]] = td_list[j].text.strip()
            dict_temp['count'] = 0
            list_res.append(dict_temp)
        time.sleep(10)
    return list_res

def getRandUserAgent():
    return UserAgent().random

def getLocalIP(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as fr:
            list_ip = json.load(fr)
        return list_ip
    else:
        return []


def removeMultiple(list_ip):
    list_new = []
    exist_ip = []
    for a in list_ip:
        if a['ip'] not in exist_ip:
            list_new.append(a)
            exist_ip.append(a['ip'])
    return list_new

def verify(dict_ip):
    try:
        telnet = telnetlib.Telnet(dict_ip['ip'], dict_ip['port'], timeout=10)
    except:
        print('ip:[{}:{}]--不可用'.format(dict_ip['ip'], dict_ip['port']))
        return False
    else:
        print('ip:[{}:{}]--可用'.format(dict_ip['ip'], dict_ip['port']))
        return True

def testIP(list_new):
    list_verity = []
    for dict_ip in list_new:
        if verify(dict_ip):
            list_verity.append(dict_ip)
    return list_verity

def saveIP(path, list_verity):
    print(list_verity)
    with open(path, 'w', encoding='utf-8') as fw:
        json.dump(list_verity, fw, indent=4, ensure_ascii =False)

def main():
    global base_url, path
    list_res = parse_html_xici()
    list_ip = getLocalIP(path)
    list_new = removeMultiple(list_ip + list_res)
    list_verity = testIP(list_new)
    saveIP(path, list_verity)

if __name__ == '__main__':

    schedule.every(6).hours.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)


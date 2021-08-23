import os
import sys
from typing import Text
from utils import *
import requests
import random
from requests.sessions import session
from bs4 import BeautifulSoup
import json

requests.adapters.DEFAULT_RETRIES = 5

try_time = os.getenv('try_time',3)
qmsg_key = os.getenv('QMSG_TOKEN')
username = os.getenv('CUG_ID')
password = os.getenv('CUG_PWD')

if username is None or username == '':
  notice(qmsg_key,'无法获取CUG_ID')
  print('无法获取CUG_ID')
  sys.exit(1)

if password is None or password == '':
  notice(qmsg_key,'无法获取CUG_PWD')
  print('无法获取CUG_PWD')
  sys.exit(1)

class ClockIn:
  def __init__(self):
    self.session = requests.session()
    self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'

  def des(self,data):
    s = self.session
    url = 'http://127.0.0.1:5244'
    r = s.post(url, json={"data": data})
    return r.text

  def login(self):
    # 登录页面，拿到登录所需要的数据
    s = self.session
    try:
      html =s.get('http://sfrz.cug.edu.cn/tpass/login')
      soup = BeautifulSoup(html.text, 'html.parser')
      lt = soup.find('input', {'id': 'lt'})['value']
      form_uri = soup.find('form', {'id': 'loginForm'})['action']

      # 重新拿到验证码
      r = s.get('http://sfrz.cug.edu.cn/tpass/code?{}'.format(random.random()))
      # png = gif_to_png(gif)
      # png.show()
      code = ocr(r.content)
      code = "".join(list(filter(str.isdigit, code)))

      login_data = {
        'code': code,
        'ul': len(username),
        'pl': len(password),
        'sl': 0,
        'lt': lt,
        'execution': 'e1s1',
        '_eventId': 'submit',
        'rsa': self.des(username+password+lt),
      }
      # 提交登录
      r = s.post('http://sfrz.cug.edu.cn{}'.format(form_uri), data=login_data)
      if(r.text.find('登录失败')==-1): #url=/tp_up/
        print('登录成功')
        return True
      else:
        print('登录失败')
        return False
    except Exception as e:
      print('登录失败{}'.format(e))
      return False

  # 打开打卡页面
  def clock_in_page(self):
    s = self.session
    s.keep_alive = False
    proxies = {

    }
    try:
      r = s.get('http://yqapp.cug.edu.cn/xsfw/sys/swmxsyqxxsjapp/*default/index.do')
      if(r.text.find('var SERVER_PATH =')!=-1):
        print('打开打卡页面成功')
        return True
      else:
        print('打开打卡页面失败')
        return False
    except Exception as e:
      print('打开打卡页面失败{}'.format(e))
      return False
  
  # 打卡
  def clock_in(self):
    s = self.session
    # 获取个人信息,必须一步一步的请求
    SJD = get_sjd() #时间段
    try:
      print(s.post('http://yqapp.cug.edu.cn/xsfw/sys/swpubapp/MobileCommon/getSelRoleConfig.do',data={'data':'{"APPID":"5811260348942403","APPNAME":"swmxsyqxxsjapp"}'}).status_code)
      print(s.get('http://yqapp.cug.edu.cn/xsfw/sys/emappagelog/config/swmxsyqxxsjapp.do').status_code)
      print(s.post('http://yqapp.cug.edu.cn/xsfw/sys/swpubapp/MobileCommon/getMenuInfo.do',data={'data':'{"APPID":"5811260348942403","APPNAME":"swmxsyqxxsjapp"}'}).status_code)
      print(s.post('http://yqapp.cug.edu.cn/xsfw/i18n.do?appName=swmxsyqxxsjapp&EMAP_LANG=zh').status_code)
      print(s.get('http://yqapp.cug.edu.cn/xsfw/sys/swpubapp/userinfo/getUserPhoto.do?USERID={}'.format(username)).status_code)

      r = s.post('http://yqapp.cug.edu.cn/xsfw/sys/swmxsyqxxsjapp/modules/mrbpa/getStuXx.do', data={'data': '{"SJD":"'+SJD+'"}'}, verify=False)
      
      info = r.json()['data']
      print("打卡账号:{}".format(info["XH"]))
      data = {
        "SFDFHB_DISPLAY": "否",
        "DWDM": info['DWDM'],
        "JQQK_DISPLAY": "",
        "JTCYJKZK_DISPLAY": "正常",
        "SZDQ_DISPLAY": "",
        "SFSQZYFX_DISPLAY": "",
        "XLZK_DISPLAY": "无",
        "RYLB_DISPLAY": "",
        "XBDM": info["XBDM"],
        "LXDH": info["LXDH"],
        "JJLXRGX_DISPLAY": "",
        "XH": info["XH"],
        "XM": info["XM"],
        "SFJZ_DISPLAY": "",
        "XQDM_DISPLAY": "",
        "MRSZDQ_DISPLAY": "",
        "JJLXRJG_DISPLAY": "",
        "SFDFHB": info["SFDFHB"],
        "DWDM_DISPLAY": info["DWDM_DISPLAY"],
        "BRJKZT_DISPLAY": "正常",
        "GJDQ_DISPLAY": "",
        "TW_DISPLAY": "否",
        "XBDM_DISPLAY": info["XBDM_DISPLAY"],
        "isToday": 'true',
        "TBSJ": info["TBSJ"],
        "BRJKZT": "1",
        "TW": "0",
        "JTCYJKZK": "1",
        "XLZK": "www",
        "QTQK": "一切正常",
        "SJD": SJD
      }
      # 可能没有宿舍信息
      if('ZSDZ' in info):
        data['ZSDZ'] = info["ZSDZ"]
      r = s.post('http://yqapp.cug.edu.cn/xsfw/sys/swmxsyqxxsjapp/modules/mrbpa/saveMrdk.do',data={'data':json.dumps(data)})
      if(r.json()['code'] == "0"):
        print('打卡成功')
        notice(qmsg_key,'{}打卡成功'.format(info["XM"]))
        return True
      else:
        print('打卡失败')
        return False
    except BaseException as e:
      print('打卡失败{}'.format(e))
      return False
def do(name,method,exit=True):
  for i in range(try_time):
    print('第{}次尝试{}'.format(i+1,name))
    if(method()):
      return True
  notice(qmsg_key,'{}失败'.format(name))
  print('{}失败,退出'.format(name))
  if(exit):
    sys.exit(1)

if __name__ == '__main__':
  clock_in = ClockIn()
  do('登录',clock_in.login)
  do('打开打卡页面',clock_in.clock_in_page,False)
  do('打卡',clock_in.clock_in)
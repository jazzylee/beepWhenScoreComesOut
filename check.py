# -*- coding=utf-8 -*-
import time
import RSAJS
import winsound
import requests
from lxml import etree
from hex2b64 import HB64

class Longin():
    def __init__(self,user,password,login_url,login_KeyUrl):
        self.Username = user
        self.Password = password
        nowTime = lambda:str(round(time.time()*1000))
        self.now_time = nowTime()
        self.login_url = login_url
        self.login_Key = login_KeyUrl

    def Get_indexHtml(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8","Accept-Encoding": "gzip, deflate","Accept-Language": "zh-CN,zh;q=0.9","Cache-Control": "max-age=0","Connection": "keep-alive","Referer": self.login_url+ self.now_time,"Upgrade-Insecure-Requests": "1"})
        self.response = self.session.get(self.login_url+ self.now_time, verify = False).content.decode("utf-8")

    def Get_csrftoken(self):
        lxml = etree.HTML(self.response)
        self.csrftoken = lxml.xpath("//input[@id='csrftoken']/@value")[0]

    def Get_PublicKey(self):
        key_html = self.session.get(self.login_Key + self.now_time)
        key_data = key_html.json()
        self.modulus = key_data["modulus"]
        self.exponent = key_data["exponent"]

    def Get_RSA_Password(self):
        rsaKey = RSAJS.RSAKey()
        rsaKey.setPublic(HB64().b642hex(self.modulus),HB64().b642hex(self.exponent))
        self.enPassword = HB64().hex2b64(rsaKey.encrypt(self.Password))

    def Longin_Home(self):
        self.Get_indexHtml()
        self.Get_csrftoken()
        self.Get_PublicKey()
        self.Get_RSA_Password()
        login_data = [("csrftoken", self.csrftoken),("yhm", self.Username),("mm", self.enPassword),("mm", self.enPassword)]
        login_html = self.session.post(self.login_url + self.now_time, data=login_data)
        if login_html.url.find("login_slogin.html") == -1:
            print("登录成功")
            return self.session
        else:
            print("用户名或密码不正确，登录失败")
            exit()

    def GPAform(self,count):
    	year = input('输入要查询的学年(如：2019-2020则输入2019)：')
    	term = input('输入要查询的学期(如：1或2)：')
    	if term == '1':
    		term = '3'
    	elif term == '2':
    		term = '12'
    	else:
    		term = '3'
    		print('输入错误，默认将查询第一学期的成绩')

    	timestamp = str(int(time.time()*1000))
    	data = {'xnm':year,'xqm':term,'_search':'false','nd':timestamp,'queryModel.showCount':'15','queryModel.currentPage':'1','queryModel.sortName':'','queryModel.sortOrder':'asc','time':'count'}
    	return data

if __name__ == "__main__":
    login_url = "https://jwgl.njtech.edu.cn/xtgl/login_slogin.html?"
    login_KeyUrl = "https://jwgl.njtech.edu.cn/xtgl/login_getPublicKey.html?time="           
    stu_id = input('请输入学号:')
    passwd = input('请输入密码:')
    requests.packages.urllib3.disable_warnings()
    njtech = Longin(stu_id, passwd, login_url, login_KeyUrl)
    response_cookies = njtech.Longin_Home()
    GPAurl = 'https://jwgl.njtech.edu.cn/cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdm=N305005'
    totalCount_old = 0;
    freq = 440
    duration = 1000
    while True:
	    formdata = njtech.GPAform(0)
	    cj = response_cookies.get(GPAurl,params = formdata)
	    cjjson = cj.json()
	    totalCount = cjjson['totalCount']
	    showCount = cjjson['showCount']
	    loop = min(totalCount,showCount)
	    print('已出成绩数量:{}    {}'.format(totalCount,time.strftime("%H:%M:%S")))
	    if totalCount != totalCount_old:
	    	winsound.Beep(freq, duration)
	    	totalCount_old = totalCount
	    	for i in range(loop):
	    		name = cjjson['items'][i]['kcmc']
	    		score = cjjson['items'][i]['bfzcj']
	    		gpa = cjjson['items'][i]['jd']
	    		print(name,'\t',score,'\t',gpa)
	    time.sleep(300)
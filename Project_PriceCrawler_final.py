import urllib.request
import random
import os
import re

def test(html):#检测函数，检测html保存情况，主函数中不启用
    f = open("out.txt","w",encoding = 'utf-8')
    f.write(html)
    f.close()

def url_open(url):#网页打开函数，提供虚拟ip地址和访问头，以及html的保存
    req = urllib.request.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0')

    proxies = ['103.233.198.156:8081','46.166.151.198:5836','175.43.58.44:9999']
    proxy = random.choice(proxies)#随即从ip列表中挑选一个使用

    proxy_support = urllib.request.ProxyHandler({'http':proxy})
    opener = urllib.request.build_opener(proxy_support)
    urllib.request.install_opener(opener)

    response = urllib.request.urlopen(url)
    html = response.read()

    return html#返回一个html文件

def url_get(url):#最初网页地址转具体分区函数，能将最初url导向具体的游戏分区
    html = url_open(url).decode('utf-8')
    
    #test(html)

    next_url = re.findall(r'/dota2/[0-9][0-9][0-9]\?[a-z][a-z][a-z][a-z]\=[0-9]',html)

    next_url = url + next_url[0]
    print('目标地址已获取：'+next_url)
    return next_url

def get_name(url):
    html = url_open(url).decode('utf-8')
    name_list = re.findall(r'alt\="dota2 (.*)" title\=".*"',html)

    return name_list

def get_next(url):#板块信息获取，绑定函数，获取分区中所有分板块的地址后缀和对应名称，并且将其绑定为一个字典，作为自定义爬取的参数
    html = url_open(url).decode('utf-8')
    #test(html)

    next_url = re.findall(r'id="(1[0-2][0-9][0-9])"',html)
    name_list = get_name(url)

    temp = next_url
    next_url = []
    for i in range(len(name_list)):
        next_url.append(temp[i])#剔除脏数据，使得板块地址后缀和名称一一对应

    all_list = dict(zip(name_list,next_url))
    print (all_list)#绑定为字典

    return next_url

def add_next(page_url,list,i):#板块网页获取函数
    next_url = page_url + '&type_id='+list[i]

    return next_url

def maxpage_get(url):#获取板块最大页面数（尾页）函数，防止循环越界
    html = url_open(url).decode('utf-8')

    all_page = re.findall(r'page_no="([0-9][0-9]|[0-9])"',html)
    all_page.sort()#将列表进行排序，第一个为页面最大值
    
    return all_page[0]

def good_get(url,begin_url,t,max_page):#目标物件地址获取函数
    if (t<20):#单个页面的最大货物量
        html = url_open(url).decode('utf-8')

        next_url = re.findall(r'/product/570/[0-9][0-9][0-9][0-9][0-9][0-9]',html)

        good_page = begin_url + next_url[t]
        print('目标物件地址已获取：'+good_page)

        return good_page
    else:#在单页面超过20个时，视作超页处理，重新导向第n页，获取物品地址
        z = t//20
        url = url+'&page_no=' +str(z+1)
        print(url)
        
        html = url_open(url).decode('utf-8')

        next_url = re.findall(r'/product/570/[0-9][0-9][0-9][0-9][0-9][0-9]',html)

        good_page = begin_url + next_url[t%20]
        print('超页重定向完成，目标物件地址已获取：'+good_page)

        return good_page

def get_lastpagenum(url,max_page):#获取尾页最大物件数，防止循环越界
    url = url+'&page_no=' +str(max_page)

    html = url_open(url).decode('utf-8')

    last_pagenum = len(re.findall(r'/product/570/[0-9][0-9][0-9][0-9][0-9][0-9]',html))
    print('尾页最大物品量已获取：'+str(last_pagenum))
    return last_pagenum

def find_imgs(url):#获取目标物品的图片
    html = url_open(url).decode('utf-8')

    good_pic = re.findall(r'//igstatic\.igxe\.cn/steam/image/\d\d\d/[^"]+\.png',html)[0]
    
    good_pic = 'https:'+ good_pic 
    print ('目标物品图片地址已获取：'+good_pic)

    return good_pic

def find_price(url):#获取目标物品的价格列表，未完善
    html = url_open(url).decode('utf-8')

    good_price = re.findall(r'￥(\d+\.\d{0,2})',html)
    for i in range(0,4):
        good_price.pop()

    print('目标价格列表已获取')
    return(good_price)

def find_name(url):#获取目标物品的名称
    html = url_open(url).decode('utf-8')

    good_name = re.findall(r'class="name" style="width: 100%;">(.*)</div>',html)
   
    print('目标名称已获取')
    return(good_name)

def save_imgs(folder,img_addrs,good_name):#保存目标物品的图片至相应板块名称文件下
    filename = good_name[0] + img_addrs[-4:]
    with open(filename,'wb') as f:
        img = url_open(img_addrs)
        f.write(img)
        f.close()
    print( filename +'图片已保存至'+folder)

def save_price(folder,list,good_name):#保存价格表至相应板块名称文件下
    filename = folder + '_price.txt'
    good_price = open(filename,'a+')
    good_price.write(str(good_name+list)+'\n')
    print(good_name[0] + '价格已存入')

def download_dota2(folder = 'igxe_dota2',Craw_number = 1):#Craw_number为抓取的最大板块数
    try:
        os.chdir(folder)
    except(FileNotFoundError):
        os.mkdir(folder)
        os.chdir(folder)
    
    url = "https://www.igxe.cn"
    page_url = url_get(url)#从初始地址导航到具体的游戏板块
    next_url_get = get_next(page_url)#进入板块后获取所有子页面地址的列表
    for i in range(Craw_number):
        next_url = add_next(page_url,next_url_get,i)#获取下一个子页面的地址，i为获取的位置
        print('目标板块已获取：'+next_url)
        max_page = maxpage_get(next_url)#获得子页面最大页数
        last_pagesnum = get_lastpagenum(next_url,max_page)
        the_name = get_name(next_url)[i]
        try:
            os.chdir(the_name)
        except(FileNotFoundError):
            os.mkdir(the_name)
            os.chdir(the_name)
        for t in range((int(max_page)-1)*20+last_pagesnum):
            final_url = good_get(next_url,url,t,max_page)
            img_addrs = find_imgs(final_url)
            price_addrs = find_price(final_url)
            good_name = find_name(final_url)
            save_imgs(the_name,img_addrs,good_name)
            save_price(the_name,price_addrs,good_name)

if __name__ =='__main__':
    download_dota2()

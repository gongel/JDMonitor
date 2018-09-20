import json
import time
import bs4
import requests
import Mail
mail=Mail.Mail()

class Monitor():
    def __init__(self,sess,stock_id,price,area_id,clock):
        self.sess=sess
        self.stock_id=stock_id
        self.price=price
        self.area_id=area_id
        self.clock=clock
        self.notify=0

    def response_status(self,resp):
        if resp.status_code != requests.codes.OK:
            print('Status: %u, Url: %s' % (resp.status_code, resp.url))
            return False
        return True

    def tags_val(self,tag, key='', index=0):
        '''
        return html tag list attribute @key @index
        if @key is empty, return tag content
        '''
        if len(tag) == 0 or len(tag) <= index:
            return ''
        elif key:
            txt = tag[index].get(key)
            return txt.strip(' \t\r\n') if txt else ''
        else:
            txt = tag[index].text
            return txt.strip(' \t\r\n') if txt else ''


    def good_stock(self):
        '''
        33 : on sale,
        34 : out of stock
        '''
        # http://ss.jd.com/ss/areaStockState/mget?app=cart_pc&ch=1&skuNum=3180350,1&area=1,72,2799,0
        #   response: {"3180350":{"a":"34","b":"1","c":"-1"}}
        # stock_url = 'http://ss.jd.com/ss/areaStockState/mget'

        # http://c0.3.cn/stocks?callback=jQuery2289454&type=getstocks&skuIds=3133811&area=1_72_2799_0&_=1490694504044
        # jQuery2289454({"3133811":{"StockState":33,"freshEdi":null,"skuState":1,"PopType":0,"sidDely":"40","channel":1,"StockStateName":"现货","rid":null,"rfg":0,"ArrivalDate":"","IsPurchase":true,"rn":-1}})
        # jsonp or json both work
        stock_url = 'https://c0.3.cn/stocks'

        payload = {
            'type': 'getstocks',
            'skuIds': str(self.stock_id),
            'area': self.area_id or '1_72_2799_0',  # area change as needed
        }

        try:
            # get stock state
            resp =self.sess.get(stock_url, params=payload)
            if not self.response_status(resp):
                print(u'获取商品库存失败')
                return (0, '')

            # return json
            resp.encoding = 'gbk'
            stock_info = json.loads(resp.text)
            stock_stat = int(stock_info[self.stock_id]['StockState'])
            stock_stat_name = stock_info[self.stock_id]['StockStateName']

            # 33 : on sale, 34 : out of stock, 36: presell
            return stock_stat, stock_stat_name

        except Exception as e:
            print('Stocks Exception:', e)
            time.sleep(5)

        return (0, '')

    def good_price(self):
            # get good price
            url = 'http://p.3.cn/prices/mgets'
            payload = {
                'type': 1,
                'pduid': int(time.time() * 1000),
                'skuIds': 'J_' + self.stock_id,
            }

            price = '?'
            try:
                resp = self.sess.get(url, params=payload)
                resp_txt = resp.text.strip()
                # print resp_txt

                js = json.loads(resp_txt[1:-1])
                # print u'价格', 'P: {0}, M: {1}'.format(js['p'], js['m'])
                price = js.get('p')

            except Exception as e:
                print('Exp {0}'.format(e))

            return price

    def good_detail(self,area_id=None):
        # return good detail
            good_data = {
                'id': self.stock_id,
                'name': '',
                'link': '',
                'price': '',
                'stock': '',
                'stockName': '',
            }

            stock_link = 'http://item.jd.com/{0}.html'.format(self.stock_id)
            try:
                # shop page
                resp = self.sess.get(stock_link)

                # good page
                soup = bs4.BeautifulSoup(resp.text, "html.parser")

                # good name
                tags = soup.select('div#name h1')
                if len(tags) == 0:
                    tags = soup.select('div.sku-name')
                good_data['name'] = self.tags_val(tags).strip(' \t\r\n')

                # cart link
                tags = soup.select('a#InitCartUrl')
                link = self.tags_val(tags, key='href')

                if link[:2] == '//': link = 'http:' + link
                good_data['link'] = link

            except Exception as e:
                print('Exp {0}',e)

            # good price
            good_data['price'] = self.good_price()

            # good stock
            good_data['stock'], good_data['stockName'] = self.good_stock()
            # stock_str = u'有货' if good_data['stock'] == 33 else u'无货'
            if good_data['stock']==33:
                if self.price!=None and float(good_data['price'])<float(self.price):
                    content="监控的商品已降价（有货），详情如下：\n编号：{}\n名称：{}\n库存：{}\n价格：{}\n时间：{}\n链接：{}\n".format(good_data['id'],good_data['name'],good_data['stockName'],good_data['price'],time.ctime(),stock_link)
                    mail.SendMailMessage(content)
                    self.notify += 1

                if not self.price==None:
                    content="监控的商品已有货，详情如下：\n编号：{}\n名称：{}\n库存：{}\n价格：{}\n时间：{}\n链接：{}\n".format(good_data['id'],good_data['name'],good_data['stockName'],good_data['price'],time.ctime(),stock_link)
                    mail.SendMailMessage(content)
                    self.notify+=1

    def good_detail_loop(self):
        while self.notify<1:
            self.good_detail()
            time.sleep(self.clock) #每clock秒钟监控一次；有货的话仅通知三次，无货继续监控

#area_id='2_2830_51800_0' 上海浦东新区

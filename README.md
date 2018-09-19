# 京东商品监控
通过微信文件助手发送监控商品的id，price，clock（用于监控的频率）
## id，price，clock发送样例
### id:12345,price:10,clock:5
监控id为12345的商品，价格低于10元时发送降价通知（最多通知3次），否则发送有货通知，无货则不发通知，每5秒钟监控一次;<br>
price（默认None）和clock（默认5）都可以为空.<br>

## 附加聊天文件监控

## 邮件通知

## ref：scraper-jd.py



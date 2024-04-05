### **核心函数**
以下函数都可以从smawe_tools包中进行导入  
例如: from smawe_tools import retry  

- rename(src=""):  
    对src路径指定的目录中的文件进行重命名(支持绝对路径和相对路径)  
    格式为第xxx章  
    第某某章必须在一亿章以下  
    例如:  
        &ensp;&ensp;&ensp;&ensp;第一百章.txt -> 第100章.txt   
        &ensp;&ensp;&ensp;&ensp;第两千零一章.txt -> 第2001章.txt  


- text_conversion(s):  
    功能: 文本转换  
    描述: 如果s为空, 则返回0.  
    参数s: str
    返回值: 整数
    列如:  
        &ensp;&ensp;&ensp;&ensp;两千零一 -> 2001  
        &ensp;&ensp;&ensp;&ensp;十万零一百 -> 100100


- get_ip(url, domain):  
    获取目标网站url或者域名domain的ip地址  
    返回包含ip地址的列表


- get_pubnet_ip():  
    获取本机的公网ip(也就是上网时所使用的ip)  
    return: str


- retry(stop_max_attempt_number=None, wait_random_min=None, wait_random_max=None, retry_on_exception=None):  
    0.3.6中添加了实例方法, 类方法, 静态方法的支持  
    发生异常进行重试，默认进行1次重试且每次重试前睡眠0-1s的随机时间，超过最大重试次数后还发生异常，则抛出MaxRetryError异常 
    重试期间如果正常返回结果或没发生异常，则不进行重试。
    stop_max_attempt_number: 停止时的最大重试次数，超出次数后还发生异常，则抛出MaxRetryError异常  
    wait_random_min：随机等待的最小时间(单位毫秒)  
    wait_random_max: 随机等待的最大时间(单位毫秒)  
    retry_on_exception: 要重试的异常类型，默认为Exception
  
- modify_encoding():   
    此函数要从smawe_tools.settings模块进行导入, 如: 
    ~~~ python
    from smawe_tools.settings import modify_encoding 
    # 直接调用即可
    modify_encoding()  
    ~~~
    调用此函数可以修正以下此类的错误:  
    UnicodeEncodeError: 'gbk' codec can't encode character '\xa0' in position 188608: illegal multibyte sequence
    
---

**启用默认日志**  
*默认日志级别为logging.INFO*

    >>> import smawe_tools.settings as settings
    >>> import logging
    >>> settings.ENABLED_LOG = True
    >>> logging.info("test")
    2023-04-04 18:10:39,183:test.py:MainThread:INFO:test

---
**可以自行使用text_conversion函数进行扩展**

#### 示例

    >>> from smawe_tools import text_conversion
    >>> print(text_conversion("两千"))
    2000
    >>> print(text_conversion("两千万零一"))
    20000001

---
**retry使用方法**  
*retry_exception没传参默认为Exception, 也就是发生Exception异常自动进行重试*<br>
***注意事项***  
0.3.4中重构了retry函数, 已经支持任意传参，例如:  
@retry(3, 1000, 2000, Exception)   
@retry(3, wait_random_min=1000, wait_random_max=2000, retry_exception=Exception)  
@retry(3, 1000, wait_random_max=2000, retry_exception=Exception)  
@retry(3, 1000, 2000, retry_exception=Exception)  
@retry(stop_max_attempt_number=3, wait_random_min=1000, wait_random_max=2000, retry_exception=Exception)  

#### 示例1

    >>> from smawe_tools import retry
    >>> @retry()
    ... def test():
    ...     print(1)
    ...     print(2)
    ...     raise Exception()
    ...
    >>> test()
    >>>
    >>> @retry(3， 1000， 2000) # retry_exception没传参数，所以这里是Exception
    ... def test():
    ...    pass
    ...
    >>> @retry(stop_max_attempt_number=3, wait_random_min=1000, wait_random_max=3000) # retry_exception没传参数，所以这里也是Exception
    ... def test():
    ...     pass
    ... # 如果发生异常，则进行重试，每次重试前休眠1-3s的随机时间
    ...
    >>>

---
#### 示例2

    >>> from smawe_tools import retry
    >>> @retry(3, 1000, 2000, ValueError)
    ... def test(a, b):
    ...     print(1)
    ...     print(2)
    ...     print(a, b)
    ...     raise ValueError()
    ...
    >>> test(1, 2) #发生ValueError就进行重试
    >>> @retry(3, 1000, 2000, retry_exception=IndexError)
    ... def test(a, b):
    ...     print(1)
    ...     print(2)
    ...     print(a, b)
    ...     raise ValueError()
    ...
    >>> test(1, 2) #发生IndexError就进行重试

---
此包提供了一个smawe_tools.utils模块, 用于将日志记录发送到QQ邮箱  
简单使用如下:  
```python
import logging
from smawe_tools.utils import ErrorLogger

error_logger = ErrorLogger(
    from_addr="xxxx@qq.com",
    to_addrs=["xyzxxxx@qq.com", "abcdefg@qq.com"],
    subject="python test",
    password="xxxxxxxxx", #这里是QQ授权码
    handler_level=logging.INFO,
    logger_level=logging.INFO
)

# 这里已经将日志记录发送到QQ邮箱了
error_logger.info("test message")
# 然后你的QQ邮箱会收到这样类似的消息
# test.py <module> INFO: (45)test message...
```

---
此包还提供了一个对配置进行读取和保存的子模块smawe_tools.config  
简单使用如下:  
```python
from smawe_tools.config import Config

config = Config()
# 切换节，设置选项和值
config.switch_to_section("s1").set("k1", "v1")
config.switch_to_section("s2").set("k2", "v2")
config.switch_to_section("s3").set("k3", "v3")
# 切换到默认节"DEFAULT"
config.switch_to_section("DEFAULT").set("accept", "true")
# 保存配置
config.save_config("test.ini")
```
读取配置

```python
from smawe_tools.config import Config

config = Config()
config.read_config("test.ini")
# 获取配置中的值
print(config.get("s1", "k1"))
print(config.get("s1", "kk1", fallback="vv2"))
# 获取默认节中的值, 将其转为布尔值
print(config.get_boolean("s1", "accept"))

# 将其它值转为布尔值
config.boolean_states = {"access": True}

config.set("s1", "can", "access")
print(config.switch_to_section("s1").get_boolean("can"))
```

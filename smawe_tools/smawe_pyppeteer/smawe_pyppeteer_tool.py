import asyncio
from pyppeteer.page import Page
import pyppeteer.network_manager
import pretend as _pretend
import pyppeteer.errors
import inspect


class PyppeteerRequest:
    """
    使用pyppeteer对指定网站进行渲染
    """

    def __init__(self, **kwargs):
        """
        :headless(bool): 是否启动无头模式, 默认是True.(启用了此参数(参数被设置为True时), auto_close被强制设为True)
        :path(str): 要运行的 Chromium 或 Chrome 可执行文件的路径.
        :auto_close(bool): 脚本完成后自动关闭浏览器进程. 默认为 True.
        :window_width(str): 浏览器窗口宽度, 以像素为单位.注意window_width和window_height必须同时设置, 否则会不生效
        :window_height(str): 浏览器窗口高度, 以像素为单位.注意window_width和window_height必须同时设置, 否则会不生效
        :args(list[str]): 传递给浏览器进程的附加参数.
        :enabled_maximize(bool): 是否启用窗口最大化, 默认为True, 如果同时指定了注意window_width和window_height, 此参数不会生效
        :param kwargs:
        """
        headless = kwargs.pop("headless", None)
        path = kwargs.pop("path", None)
        user_data_dir = kwargs.pop("user_data_dir", None)
        auto_close = kwargs.pop("auto_close", True)
        window_width = kwargs.pop("window_width", None)
        window_height = kwargs.pop("window_height", None)
        args = kwargs.pop("args", None)
        enabled_maximize = kwargs.pop("enabled_maximize", True)
        if headless:
            auto_close = True
        if args is None:
            args = ["--disable-infobars"]
        else:
            args.append("--disable-infobars")
        if enabled_maximize:
            args.append("--start-maximized")
        if window_width and window_height:
            args.append(f"--window-size={window_width},{window_height}")
            try:
                args.remove("--start-maximized")
            except ValueError:
                pass

        self._launcher = pyppeteer.launch(
            headless=headless, executablePath=path, args=args, userDataDir=user_data_dir, autoClose=auto_close
        )
        self._initialized = False
        self._browser = None
        self._enabled_interception = False
        self._meta_data = {}

    async def init(self):
        """执行初始化"""
        if not self._initialized:
            self._browser = await self._launcher
            self._initialized = True

    async def request(self, url, ua=None, callable=None, **kwargs):
        """
        使用pyppeteer对指定的url进行渲染
        kwargs包含以下参数
            param wait_for: css选择器或者xpath, 等待指定的元素出现在页面上
            param page_width: 页面宽度
            param page_height: 页面高度
            param delay: 打开指定url后要等待的秒数, 默认为None不进行等待(同时指定了delay和wait_for,则先delay,然后再wait_for)
            param pretend(bool): 是否启用伪装, 默认启用
            param enabled_interception: 是否启用请求拦截
            param script: js表达式/js函数, 脚本在最后才执行, 即page关闭前执行
        :param url: url
        :param ua: userAgent(可选), 将userAgent设置为指定的ua, 如果未提供则使用内置的userAgent
        :param callable: 启动了请求拦截后要调用的协程函数, 它接受单个request参数, 未提供则使用默认实现.
        :param kwargs:
        :return: PyppeteerResponse
        """
        await self.init()
        delay = kwargs.pop("delay", None)
        wait_for = kwargs.pop("wait_for", None)
        width = kwargs.pop("page_width")
        width = 800 if width is None else width
        height = kwargs.pop("page_height")
        height = 600 if height is None else height
        page: Page = await self._browser.newPage()

        if ua is not None:
            await page.setUserAgent(ua)
        else:
            ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0Safari/537.36"
            await page.setUserAgent(ua)

        await page.setViewport({"width": width, "height": height})

        if kwargs.pop("pretend", True):
            for script in _pretend.SCRIPTS:
                await page.evaluateOnNewDocument(script)

        self.enabled_interception(bool(kwargs.pop("enabled_interception", False)))
        if self._enabled_interception:
            await page.setRequestInterception(True)
            if not callable:
                page.on("request", lambda request: asyncio.ensure_future(self.handle_request(request)))

            if inspect.iscoroutinefunction(callable):
                page.on("request", lambda request: asyncio.ensure_future(callable(request)))
            else:
                raise TypeError("callable must be coroutine function.")

        try:
            response = await page.goto(url, {"timeout": 30000, "waitUntil": "load"})
        except pyppeteer.errors.TimeoutError as e:
            response = type("response", (object,), {"status": 504, "request": None, "headers": {}})()
            print(f"Error during page.goto(): {str(e)}")

        if delay is not None:
            await asyncio.sleep(delay)

        if wait_for:
            await page.waitFor(wait_for)

        script = kwargs.pop("script", None)
        script_result = None
        if script:
            script_result = await page.evaluate(script)

        self._meta_data["cookies"] = await page.cookies()
        self._meta_data["text"] = await page.content()
        self._meta_data["status"] = response.status
        self._meta_data["request"] = response.request
        self._meta_data["headers"] = response.headers
        self._meta_data["script_result"] = script_result

        await self.close(page)

        return PyppeteerResponse(meta_data=self._meta_data)

    @staticmethod
    async def handle_request(request: pyppeteer.network_manager.Request):
        """
        当page发出请求时进行拦截, 可重载此方法进行自定义实现, 默认实现是打印每个请求的headers, 然后继续请求
        :param request:
        :return:
        """
        print(request.headers)
        await request.continue_()

    def enabled_interception(self, value):
        """
        是否启动请求拦截
        :param value: bool
        :return:
        """
        self._enabled_interception = value

    async def close(self, page):
        await page.close()
        await self._browser.close()
        self._initialized = False


class PyppeteerResponse:

    def __init__(self, **kwargs):
        self.meta_data = kwargs.pop("meta_data", {})

    @property
    def text(self):
        """
        获取页面的完整HTML内容。
        :return: str
        """
        return self.meta_data.get("text")

    @property
    def cookies(self):
        """
        返回当前页面URL的cookie
        :return: list[dict]
        """
        return self.meta_data.get("cookies")

    @property
    def headers(self):
        """
        返回响应headers
        :return:
        """
        return self.meta_data.get("headers")

    @property
    def status(self):
        """
        返回响应状态码
        :return:
        """
        return self.meta_data.get("status")

    @property
    def request(self):
        """
        返回响应对应的请求对象
        :return:
        """
        return self.meta_data.get("request")

    @property
    def script_result(self):
        """
        返回js脚本的执行结果, 未提供script, 默认返回None
        :return:
        """
        return self.meta_data.get("script_result")


async def get(
    url, delay=None, wait_for=None, page_width=None, page_height=None,
    enabled_interception=None, script=None, callable=None, **kwargs
):
    """
    使用pyppeteer对指定url进行渲染
    :param url: url
    :param wait_for: css选择器或者xpath, 等待指定的元素出现在页面上
    :param delay: 打开指定url后要等待的秒数, 默认为None不进行等待(同时指定了delay和wait_for,则先delay,然后再wait_for)
    :param page_width: 页面宽度
    :param page_height: 页面高度
    :param enabled_interception: 是否启用请求拦截
    :param callable: 启动了请求拦截后要调用的协程函数, 它接受单个request参数, 未提供则使用默认实现.
    :param script: js表达式/js函数, 脚本在最后才执行, 即page关闭前执行. 结果可通过PyppeteerResponse.script_result属性获取.
    :param kwargs:
        headless(bool): 是否启动无头模式, 默认是True.(启用了此参数(参数被设置为True时), auto_close被强制设为True)
        path(str): 要运行的 Chromium 或 Chrome 可执行文件的路径.
        auto_close(bool): 脚本完成后自动关闭浏览器进程. 默认为 True.
        window_width(str): 浏览器窗口宽度, 以像素为单位.注意window_width和window_height必须同时设置, 否则会不生效
        window_height(str): 浏览器窗口高度, 以像素为单位.注意window_width和window_height必须同时设置, 否则会不生效
        args(list[str]): 传递给浏览器进程的附加参数.
        enabled_maximize(bool): 是否启用窗口最大化, 默认为True, 如果同时指定了注意window_width和window_height, 此参数不会生效
    :return: PyppeteerResponse
    """
    pretend = kwargs.pop("pretend", True)
    return await PyppeteerRequest(**kwargs).request(
        url, delay=delay, wait_for=wait_for, page_height=page_height, page_width=page_width,
        pretend=pretend, enabled_interception=enabled_interception, script=script, callable=callable
    )


__all__ = ["PyppeteerRequest", "PyppeteerResponse", "get"]

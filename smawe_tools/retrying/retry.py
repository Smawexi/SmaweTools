import functools
import time
import random
import logging
import importlib
import warnings
_exception = importlib.import_module(".exception", package="smawe_tools")


class Retrying(object):

    def __init__(
            self,
            func,
            stop_max_attempt_number=None,
            wait_random_min=None,
            wait_random_max=None,
            retry_on_exception=None,
    ):
        if not callable(func) and not isinstance(func, (classmethod, staticmethod)):
            raise ValueError("func param error")
        functools.update_wrapper(self, func)
        self._func = func

        self._retry_on_exception = retry_on_exception if retry_on_exception is not None else Exception

        self._stop_max_attempt_number = stop_max_attempt_number if stop_max_attempt_number else 1

        self._wait_random_min = wait_random_min / 1000 if isinstance(wait_random_min, int) else 0
        self._wait_random_max = wait_random_max / 1000 if isinstance(wait_random_max, int) else 1
        if self._wait_random_max <= self._wait_random_min:
            raise ValueError("wait_random_min is greater than or equal to wait_random_max")

    def __get__(self, instance, owner=None):
        if isinstance(self._func, (staticmethod, classmethod)):
            self._func = self._func.__get__(instance, owner)
            return self

        self._f = self._func.__get__(instance, owner)
        return self

    def __call__(self, *args, **kwargs):
        current_retry_num = 0
        while True:
            if current_retry_num > self._stop_max_attempt_number:
                raise _exception.MaxRetryError("Exceeded maximum retry count error")
            try:
                if current_retry_num:
                    logging.info("\033[1;34mThis is currently the {} retry\033[0m".format(current_retry_num))
                    time.sleep(random.uniform(self._wait_random_min, self._wait_random_max))
                return self._f(*args, **kwargs)
            except self._retry_on_exception:
                current_retry_num += 1


def retry(
    stop_max_attempt_number=None, wait_random_min=None, wait_random_max=None,
    retry_on_exception=None, **kwargs
):
    """
    异常重试装饰器, 0.3.6中添加了实例方法, 类方法, 静态方法的支持
    :param stop_max_attempt_number: 最大重试次数(默认为1次)
    :param wait_random_min: 重试间隔的随机等待最小时间(默认为0s), 单位毫秒
    :param wait_random_max: 重试间隔的随机等待最大时间(默认为1s), 单位毫秒
    :param retry_on_exception: 要重试的异常类型(默认为Exception)
    :return:
    """
    if retry_on_exception is None:
        retry_on_exception = kwargs.get('retry_exception')
        warnings.warn("retry_exception param was deprecated, please use retry_on_exception param",  category=DeprecationWarning, stacklevel=2)

    _kwargs = _merger_setting(
        stop_max_attempt_number=stop_max_attempt_number, wait_random_min=wait_random_min,
        wait_random_max=wait_random_max, retry_on_exception=retry_on_exception
    )
    return functools.partial(Retrying, **_kwargs)


def _merger_setting(**kwargs):
    new_dict = {}
    new_dict.update(kwargs)
    return new_dict


__all__ = ["retry"]

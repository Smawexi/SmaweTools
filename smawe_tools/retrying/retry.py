import functools
import time
import random
import logging
import importlib
exception = importlib.import_module(".exception", package="smawe_tools")


class Retrying(object):

    def __init__(
            self,
            func,
            stop_max_attempt_number=None,
            wait_random_min=None,
            wait_random_max=None,
            retry_exception=None,
    ):
        if not callable(func):
            raise ValueError("func param error")
        functools.update_wrapper(self, func)
        self._func = func

        self._retry_exception = retry_exception if retry_exception is not None else Exception

        self._stop_max_attempt_number = stop_max_attempt_number if stop_max_attempt_number else 1

        self._wait_random_min = wait_random_min / 1000 if isinstance(wait_random_min, int) else 0
        self._wait_random_max = wait_random_max / 1000 if isinstance(wait_random_max, int) else 1
        if self._wait_random_max <= self._wait_random_min:
            raise ValueError("wait_random_min is greater than or equal to wait_random_max")

    def __call__(self, *args, **kwargs):
        current_retry_num = 0

        while True:
            if current_retry_num > self._stop_max_attempt_number:
                raise exception.MaxRetryError("Exceeded maximum retry count error")
            try:
                if current_retry_num:
                    logging.info("\033[1;34mThis is currently the {} retry\033[0m".format(current_retry_num))
                    time.sleep(random.uniform(self._wait_random_min, self._wait_random_max))
                return self._func(*args, **kwargs)
            except self._retry_exception:
                current_retry_num += 1


def retry(
    stop_max_attempt_number=None, wait_random_min=None, wait_random_max=None,
    retry_exception=None
):
    """
    异常重试装饰器
    :param stop_max_attempt_number: 最大重试次数(默认为1次)
    :param wait_random_min: 重试间隔的随机等待最小时间(默认为0s), 单位毫秒
    :param wait_random_max: 重试间隔的随机等待最大时间(默认为1s), 单位毫秒
    :param retry_exception: 要重试的异常类型(默认为Exception)
    :return:
    """
    kwargs = _merger_setting(
        stop_max_attempt_number=stop_max_attempt_number, wait_random_min=wait_random_min,
        wait_random_max=wait_random_max, retry_exception=retry_exception
    )
    return functools.partial(Retrying, **kwargs)


def _merger_setting(**kwargs):
    new_dict = {}
    new_dict.update(kwargs)
    return new_dict


__all__ = ["retry"]

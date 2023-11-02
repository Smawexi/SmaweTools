import logging.handlers


class ErrorLogger:
    """错误记录器，将日志记录发送到QQ邮箱."""

    def __new__(cls, *args, **kwargs):
        """
        返回一个name为error_logger的logging.Logger对象

        :param kwargs:
            '''

            from_addr: 发件人QQ邮箱, 未提供则为""

            to_addrs: 收件人QQ邮箱列表, 未提供则默认发送到from_addr

            subject: 邮件主题, 未提供则默认为"Program running"

            password: QQ授权码, 未提供则为""

            handler_level: 处理器记录级别, 未提供则默认为logging.INFO

            logger_level: 记录器记录级别, 未提供则默认为logging.INFO
            '''
        """
        from_addr = kwargs.pop("from_addr", "")
        to_addrs = kwargs.pop("to_addrs", [from_addr])
        subject = kwargs.pop("subject", "Program running")
        password = kwargs.pop("password", "")
        smtp_handler = logging.handlers.SMTPHandler(
            mailhost=("smtp.qq.com", 25), fromaddr=from_addr, toaddrs=to_addrs, subject=subject,
            credentials=(from_addr, password), secure=(), timeout=10
        )
        smtp_handler.setLevel(kwargs.pop("handler_level", logging.INFO))
        fmt = logging.Formatter("%(filename)s %(funcName)s %(levelname)s: (%(lineno)d)%(message)s")
        smtp_handler.setFormatter(fmt)
        error_logger = logging.getLogger("error_logger")
        error_logger.setLevel(kwargs.pop("logger_level", logging.INFO))
        error_logger.addHandler(smtp_handler)
        return error_logger


class Email:

    def __init__(self, **kwargs):
        pass

    def send_mail(self, **kwargs):
        pass


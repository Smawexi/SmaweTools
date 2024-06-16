import abc
import logging.handlers
import smtplib
from typing import List, Union, IO
from email.message import EmailMessage
import mimetypes
import re


class File(IO, metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is File:
            if any('read' in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented


SMTP_CONFIG = {
    'qq': {
        'host': "smtp.qq.com",
        'port': 465
    },
    '163': {
        'host': "smtp.163.com",
        'port': 465
    }
}


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
        error_logger.email_helper = EmailHelper(user=from_addr, password=password)
        return error_logger


class EmailHelper:

    def __init__(self, user: str = None, password: str = None, host: str = None, port: int = None):
        """
        Support (QQ, 163) email
        :param user: username
        :param password: password
        :param host: smtp host
        :param port: smtp port
        """
        self.user = user
        brand = None
        pattern = '@([^\.]*)\.'
        match_obj = re.search(pattern, user)
        if match_obj is not None:
            brand = match_obj.group(1)

        config = None
        if brand is not None:
            _brand = brand.lower()
            try:
                config = SMTP_CONFIG[_brand]
            except KeyError:
                pass

        if config is not None:
            host = config.get('host')
            port = config.get('port')
            self.smtp_client = smtplib.SMTP_SSL(host=host, port=port)
            self.smtp_client.login(user=user, password=password)
            return

        if host is None:
            raise ValueError('Require following params: host')

        if port is None:
            port = 465

        self.smtp_client = smtplib.SMTP_SSL(host=host, port=port)
        self.smtp_client.login(user=user, password=password)

    def send_mail(
            self, message: str, to: List[str] = None, subject: str = None,
            file: Union[str, bytes, File] = None, file_name: str = None,
            files: List[Union[str, bytes, File]] = None, file_names: List[str] = None, strict=True
    ):
        """
        :param message: text message
        :param to: recipients, if is None, then is self
        :param subject: title
        :param file: open() -> file obj, used for single attachment
        :param file_name: 
        :param files: Used for multiple attachments
        :param file_names: List of file names corresponding to 'files'
        :param strict: default: True, when files and file_names inconsistent length, raised ValueError
        :return: 
        """
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.user
        if to is None:
            to = [self.user]
        msg['To'] = ', '.join(to)
        msg.set_content(message)
        if file is not None:
            msg = self.set_attachment(msg, file, file_name)
        if files and file_names:
            if strict:
                if len(files) != len(file_names):
                    raise ValueError('files and file_names inconsistent length')

            for file, file_name in zip(files, file_names):
                msg = self.set_attachment(msg=msg, file=file, file_name=file_name)
        self.smtp_client.send_message(msg=msg)

    def set_attachment(self, msg: EmailMessage, file: Union[str, bytes, File], file_name: str) -> EmailMessage:
        if isinstance(file, str):
            attachment_content = open(file, 'rb').read()
            path = file
        elif isinstance(file, bytes):
            attachment_content = file
            path = ''
        else:
            attachment_content = file.read()
            if isinstance(attachment_content, str):
                attachment_content = attachment_content.encode()
            path = file.name
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        msg.add_attachment(
            attachment_content,
            maintype=maintype,
            subtype=subtype,
            filename=file_name
        )
        return msg

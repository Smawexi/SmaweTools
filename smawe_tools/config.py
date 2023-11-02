"""
遍历Config对象时, 将返回每一个Section对象
遍历Section对象时, 将返回每一个选项的名称
"""

import configparser


class Config:
    """
    读取和保存配置设置
    """

    def __init__(self, **kwargs):
        self._default_section = kwargs.pop("default_section", configparser.DEFAULTSECT)
        i = kwargs.pop("interpolation_level", 1)
        map_set = (None, configparser.BasicInterpolation(), configparser.ExtendedInterpolation())
        try:
            self._interpolation = map_set[i]
        except TypeError:
            raise ValueError("interpolation_level param is not a integer number")
        except IndexError:
            raise ValueError("interpolation_level param must be one of (0,1,2)")
        self._config = configparser.ConfigParser(
            default_section=self._default_section, interpolation=self._interpolation, **kwargs
        )

    def set(self, section, option, value):
        """设置section中的option的值为value.
        如果配置中不存在指定的section, 则会先添加section, 然后再设置值
        """
        if not self.has_section(section):
            self._config.add_section(section)
        self._config.set(section, option, value)

    def get(self, section, option, fallback=None, **kwargs):
        """获取section中option的值, 获取不到则返回fallback"""
        return self._config.get(section, option, fallback=fallback, **kwargs)

    def save_config(self, filename):
        """保存配置"""
        with open(filename, "w", encoding="utf-8") as fp:
            self._config.write(fp)

    def read_config(self, filename):
        """
        读取配置文件设置，读取成功返回True,否则返回False
        :param filename:
        :return: bool
        """
        try:
            with open(filename, "r") as fp:
                self._config.read_file(fp)
            return True
        except (OSError, TypeError):
            return False

    def switch_to_section(self, section):
        """
        切换当前节，节如果不存在则先添加然后返回，否则切换到指定的节并返回
        :param section:
        :return: Section object
        """
        try:
            self._config.add_section(section)
        except configparser.DuplicateSectionError:
            return Section(self._config, section)
        except ValueError:
            return Section(self._config, section)
        else:
            return Section(self._config, section)

    def get_options(self, section):
        """获取所有选项"""
        return self._config.options(section)

    def get_sections(self):
        """
        获取所有可用的节, default section 不包括在该列表中
        :return: list
        """
        return self._config.sections()

    @property
    def default_section(self):
        return self._config.default_section

    @default_section.setter
    def default_section(self, value):
        self._config.default_section = value

    @property
    def boolean_states(self):
        return self._config.BOOLEAN_STATES

    @boolean_states.setter
    def boolean_states(self, value: dict):
        self._config.BOOLEAN_STATES = value

    def get_boolean(self, section, option, fallback=None, **kwargs):
        """将section中option的值转为布尔值, 可通过修改boolean_states以支持多值转换"""
        raw = kwargs.pop("raw", False)
        vars_ = kwargs.pop("vars", None)
        return self._config.getboolean(section, option, raw=raw, vars=vars_, fallback=fallback)

    def has_section(self, section):
        """配置中是否存在指定的section"""
        return self._config.has_section(section)

    def has_option(self, section, option):
        """section中是否存在指定的option"""
        return self._config.has_option(section, option)

    def defaults(self):
        """返回包含实例范围内默认值的字典。"""
        return self._config.defaults()

    def remove_section(self, section):
        """从配置中移除section"""
        return self._config.remove_section(section)

    def remove_option(self, section, option):
        """从指定的section中移除指定的option"""
        try:
            return self._config.remove_option(section, option)
        except configparser.NoSectionError:
            pass

    def __iter__(self):
        self._sections = self.get_sections()
        self._start = 0
        self._length = len(self._sections)
        return self

    def __next__(self):
        if self._start > self._length - 1:
            raise StopIteration
        self._start += 1
        return Section(self._config, self._sections[self._start - 1])

    def __len__(self):
        """返回可用的节的长度"""
        return len(self.get_sections())


class Section:

    def __init__(self, conf=None, section=None):
        self._conf: configparser.ConfigParser = conf
        self._section: configparser.SectionProxy = self._conf[section]
        self._section_name = section

    def __repr__(self):
        return "<Section: {}>".format(self._section_name)

    def get(self, option, fallback=None, **kwargs):
        """获取当前节中指定option的值"""
        return self._section.get(option, fallback=fallback, **kwargs)

    def set(self, option, value):
        """设置当前节中option的值为value"""
        self._section[option] = value

    def get_boolean(self, option, fallback=None, **kwargs):
        """将当前节中option的值转为布尔值"""
        raw = kwargs.pop("raw", False)
        vars_ = kwargs.pop("vars", None)
        return self._section.getboolean(option, raw=raw, vars=vars_, fallback=fallback)

    def items(self):
        return self._section.items()

    def keys(self):
        return self._section.keys()

    def values(self):
        return self._section.values()

    def get_options(self):
        """返回当前节的选项名列表"""
        return list(self.keys())

    def has_option(self, option):
        """当前节中是否存在指定的option"""
        return self._conf.has_option(self._section_name, option)

    def remove_option(self, option):
        """移除当前节中指定的option"""
        return self._conf.remove_option(self._section_name, option)

    def __iter__(self):
        self._iter = iter(self.keys())
        return self

    def __next__(self):
        return next(self._iter)

    def __len__(self):
        """返回可用的选项的长度"""
        return len(self.keys())


__all__ = ["Config", "Section"]

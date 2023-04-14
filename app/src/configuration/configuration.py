from enum import Enum
import yaml
import os
import logging


class Environment():
    def get_env(self, key, default=None):
        return os.environ.get(key, default)


class ConfigurationError(Exception):
    pass


class ConfigurationParser():
    __MANDATORY_DELIMITER = ':?'
    __OPTIONAL_DELIMITER = ':'

    def __parse_optional_variable(self, variable: str):
        variable, default = variable.split(self.__OPTIONAL_DELIMITER, 1)
        return self.environment.get_env(variable, default)

    def __parse_mandatory_variable(self, variable: str):
        variable, error = variable.split(self.__MANDATORY_DELIMITER, 1)
        variable = self.environment.get_env(variable)
        if variable is None:
            raise ConfigurationError(error)
        return variable

    def parse(self, variable: str, environment: Environment = Environment()):
        self.environment = environment
        if not variable.startswith('${') or not variable.endswith('}'):
            return variable
        variable = variable[2:-1]
        if self.__MANDATORY_DELIMITER in variable:
            self.__parse_mandatory_variable(variable)
        if self.__OPTIONAL_DELIMITER in variable:
            return self.__parse_optional_variable(variable)
        return environment.get_env(variable)


def read_config_from_file(file_path: str):
    return open(file_path, 'r')


class Configuration():
    def get_key_from_config(self, key):
        if key not in self.config:
            raise ConfigurationError(
                f'Key {key} is not defined in the configuration')

        return self.config[key]

    def __init__(self, config: str, configuration_parser: ConfigurationParser = ConfigurationParser()):
        self.configuration_parser = configuration_parser
        self.config = yaml.safe_load(config)

# create enum for log_level


class LogLevel(Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'
    DISABLE = 'NOTSET'


class FrogConfiguration(Configuration):
    ROOT_KEY = 'frog'

    def __init__(self, config: str, configuration_parser: ConfigurationParser = ConfigurationParser()):
        super().__init__(config, configuration_parser)
        self.config = super().get_key_from_config(self.ROOT_KEY)

    def get_port(self):
        port = self.configuration_parser.parse(
            str(super().get_key_from_config('port')))
        return int(port) if port else None

    def get_hostname(self):
        return self.configuration_parser.parse(
            str(super().get_key_from_config('hostname')))

    def get_log_level(self):
        log_level = 'info'
        try:
            log_level = super().get_key_from_config('log_level')
        except ConfigurationError:
            logging.info("No login level set, default set (INFO)")
            pass
        return LogLevel(log_level.upper())

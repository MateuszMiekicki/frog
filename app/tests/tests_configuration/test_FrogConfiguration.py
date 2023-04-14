from src.configuration.configuration import FrogConfiguration, LogLevel
import mock
import pytest

CONFIG = '''frog:
    hostname: ${FROG_HOST:0.0.0.0}
    port: ${FROG_PORT:8000}
    log_level: debug
'''


def test_when_port_is_configuration_in__file_it_should_be_able_to_be_extracted():
    frog = FrogConfiguration(CONFIG)
    assert frog.get_port() == 8000


def test_when_log_level_is_set_should_return_selected_level():
    frog = FrogConfiguration(CONFIG)
    assert frog.get_log_level() == LogLevel.DEBUG


def test_when_log_level_is_not_set_should_return_info_level():
    CONFIG_WITHOUT_LOG_LEVEL = '''frog:
    port: 8080
'''
    frog = FrogConfiguration(CONFIG_WITHOUT_LOG_LEVEL)
    assert frog.get_log_level() == LogLevel.INFO


def test_should_get_hostname_from_config_and_return_like_string():
    frog = FrogConfiguration(CONFIG)
    assert frog.get_hostname() == '0.0.0.0'

from src.configuration.configuration import Environment, ConfigurationParser, ConfigurationError
import mock
import pytest


@mock.patch('src.configuration.configuration.Environment.get_env')
def test_if_mandatory_environment_variable_exists_it_should_return_its_value(mock_environment):
    variable = '${FROG_DATABASE_PASSWORD:?You need to set FROG_DATABASE_PASSWORD environment_variable}'
    environment = Environment()
    mock_environment.return_value = 'frog!123'
    assert ConfigurationParser().parse(
        variable, environment) == 'frog!123'


@mock.patch('src.configuration.configuration.Environment.get_env')
def test_if_mandatory_environment_variable_not_exists_it_should_return_its_value(mock_environment):
    variable = '${FROG_DATABASE_PASSWORD:?You need to set the FROG_DATABASE_PASSWORD environment variable}'
    environment = Environment()
    mock_environment.return_value = None
    with pytest.raises(ConfigurationError):
        ConfigurationParser().parse(
            variable, environment)


@mock.patch('src.configuration.configuration.Environment.get_env')
def test_if_optional_environment_variable_exists_it_should_return_its_value(mock_environment):
    variable = '${FROG_DATABASE_PASSWORD:frogDefaultPassword}'
    environment = Environment()
    mock_environment.return_value = 'frog!123'
    assert ConfigurationParser().parse(
        variable, environment) == 'frog!123'


@mock.patch('src.configuration.configuration.Environment.get_env')
def test_if_optional_environment_variable_not_exists_it_should_return_its_value(mock_environment):
    variable = '${FROG_DATABASE_PASSWORD:frogDefaultPassword}'
    environment = Environment()
    mock_environment.return_value = 'frogDefaultPassword'
    assert ConfigurationParser().parse(
        variable, environment) == 'frogDefaultPassword'


@mock.patch('src.configuration.configuration.Environment.get_env')
def test_if_variable_does_not_contain_any_options_its_value_should_be_retrieved(mock_environment):
    variable = '${FROG_DATABASE_PASSWORD}'
    environment = Environment()
    mock_environment.return_value = 'frogDefaultPassword'
    assert ConfigurationParser().parse(
        variable, environment) == 'frogDefaultPassword'


@mock.patch('src.configuration.configuration.Environment.get_env')
def test_if_variable_does_not_contain_any_options_its_value_should_be_taken_if_it_exists(mock_environment):
    variable = '${FROG_DATABASE_PASSWORD}'
    environment = Environment()
    mock_environment.return_value = 'frogDefaultPassword'
    assert ConfigurationParser().parse(
        variable, environment) == 'frogDefaultPassword'


def test_if_variable_contains_no_options_its_value_should_be_taken_if_it_doesnt_exist_it_should_be_returned_none():
    variable = '${FROG_DATABASE_PASSWORD}'
    environment = Environment()
    assert ConfigurationParser().parse(
        variable, environment) == None

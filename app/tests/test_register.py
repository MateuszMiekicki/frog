# import pytest
# import app.src.controller


# @mock.path("repository.user.User")
# def test_register_endpoint_call_add_user_method_with_correct_parameters(mock_user):
#     user = dto.User("test@test.com", "password")
#     mock_user.is_user_exist.return_value = False
#     mock_user.add_user.return_value = True
#     register.login(user)
#     mock_user.add_user.assert_called_with(email=user.email, password=hashing.hash(
#         user.password.get_secret_value()), role='user')

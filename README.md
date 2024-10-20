## Usage
```
# TODO: API Calls that require inputs are untested

from mullvad_api_wrapper import SubmitAProblemReportParameters

with MullvadAPIEngine() as mv:
    # Public API https://api.mullvad.net/public/documentation
    print(mv.public_api_get_open_vpn_server_list().model_dump_json())
    print(mv.public_api_get_wireguard_server_list_v1().model_dump_json())
    print(mv.public_api_get_wireguard_server_list_v2().model_dump_json())
    print(mv.public_api_create_account().model_dump_json())
    print(mv.public_api_get_account_information(token="").model_dump_json())
    print(mv.public_api_activate_voucher_code(account="", code=""))
    
    # App API https://api.mullvad.net/app/documentation
    print(mv.app_api_relay_list().model_dump_json())
    print(mv.app_api_list_ip_addresses_for_reaching_the_api().json())
    print(mv.app_api_submit_a_voucher(access_token="", voucher_code=""))
    problem_report_parameters = SubmitAProblemReportParameters(access="", message="", log="", metadata="")
    print(mv.app_api_submit_a_problem_report(submit_a_problem_report_parameters=problem_report_parameters).model_dump_json())
    print(mv.app_api_request_a_website_auth_token(access_token="").model_dump_json())
    print(mv.app_api_information_about_app_release(platform="", version="").model_dump_json())
    print(mv.app_api_create_an_apple_in_app_payment(access_token="", receipt_string="").model_dump_json())
    
    # Am I API
    print(mv.am_i_ip().text)
    print(mv.am_i_city().text)
    print(mv.am_i_country().text)
    print(mv.am_i_connected().text)
    print(mv.am_i_json().json())
```
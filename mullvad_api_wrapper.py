import requests
from pydantic import BaseModel, Field


class Account(BaseModel):
    id: str | None = Field(None, description="The account token")
    expiry: str | None = Field(
        None, description="The expiry time of the account in ISO 8601 format"
    )


class CreateAccountResponse(Account):
    pass


class GetAccountInformationResponse(Account):
    pass


class OpenVPNRelay(BaseModel):
    hostname: str | None = None
    location: str | None = None
    active: bool | None = None
    owned: bool | None = None
    provider: str | None = None
    stboot: bool | None = None
    ipv4_addr_in: str | None = None
    include_in_country: bool | None = None
    weight: int | None = None


class BridgeRelay(OpenVPNRelay):
    pass


class WireGuardRelay(BaseModel):
    hostname: str | None = None
    location: str | None = None
    active: bool | None = None
    owned: bool | None = None
    provider: str | None = None
    stboot: bool | None = None
    ipv4_addr_in: str | None = None
    include_in_country: bool | None = None
    weight: int | None = None
    public_key: str | None = None
    ipv6_addr_in: str | None = None


class WireGuardShadowsocksPortRanges(BaseModel):
    shadowsocks_port_ranges: list[int]


class Location(BaseModel):
    city: str | None = None
    country: str | None = None
    latitude: str | None = None
    longitude: str | None = None


class Locations(BaseModel):
    locations: dict[str, Location] | None = None


class OpenVPNPort(BaseModel):
    port: int
    protocol: str


class BridgeShadowsocks(BaseModel):
    protocol: str
    port: int
    cipher: str
    password: str


class RelayList(BaseModel):
    locations: Locations
    openvpn: dict[str, list[OpenVPNRelay] | list[OpenVPNPort]]
    wireguard: dict[
        str,
        list[WireGuardRelay]
        | list[list[int]]
        | list[WireGuardShadowsocksPortRanges]
        | str,
    ]
    bridge: dict[str, list[BridgeRelay] | str, list[BridgeShadowsocks]]


class Wireguard(BaseModel):
    port_ranges: list[list[int, int]] | None = None
    ipv4_gateway: str | None = None
    ipv6_gateway: str | None = None
    relays: list[WireGuardRelay] | None = None


class Hostname(BaseModel):
    hostname: str | None = None
    ipv4_addr_in: str | None = None
    ipv6_addr_in: str | None = None
    public_key: str | None = None
    multihop_port: int | None = None
    weight: int | None = None


class City(BaseModel):
    name: str | None = None
    code: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    relays: list[Hostname] | None


class Country(BaseModel):
    name: str | None = None
    code: str | None = None
    cities: list[City] | None


class Countries(BaseModel):
    countries: list[Country] | None


class OpenVPNServerListResponse(Countries):
    pass


class WireGuardServerListResponseV1(Countries):
    pass


class Voucher(BaseModel):
    account: str | None = None
    code: str | None = None


class WireGuardServerListResponseV2(BaseModel):
    locations: Locations | None = None
    wireguard: Wireguard | None = None


class ActivateVoucherCodeResponse(BaseModel):
    response: str


class SubmitAVoucherResponse(BaseModel):
    time_added: int
    new_expiry: str


class SubmitAProblemReportParameters(BaseModel):
    address: str
    message: str
    log: str
    metadata: dict


class SubmitAProblemReportResponse(BaseModel):
    code: str
    error: str


class AuthToken(BaseModel):
    auth_token: str


class InformationAboutAppReleaseResponse(BaseModel):
    supported: bool
    latest: str
    latest_stable: str
    latest_beta: str


class CreateAnAppleInAppPaymentResponse(BaseModel):
    receipt_string: str


class MullvadAPIEngine:
    """
    API calls to api.mullvad.net and am.i.mullvad.net
    https://api.mullvad.net/app/documentation
    https://api.mullvad.net/public/documentation
    """

    APP_API_URL = "https://api.mullvad.net/app"
    PUBLIC_API_URL = "https://api.mullvad.net/public"
    AM_I_URL = "https://am.i.mullvad.net"

    def __init__(self):
        self.session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def __del__(self):
        self.session.close()

    def _get(self, url: str, **kwargs) -> requests.Response:
        response = self.session.get(url=url, **kwargs)
        response.raise_for_status()
        return response

    def _post(self, url: str, **kwargs) -> requests.Response:
        response = self.session.post(url=url, **kwargs)
        response.raise_for_status()
        return response

    def app_api_relay_list(self) -> RelayList:
        """
        List relays
        :return: RelayList
        """
        ENDPOINT = "/v1/relays"
        return RelayList(**self._get(url=self.APP_API_URL + ENDPOINT).json())

    def app_api_list_ip_addresses_for_reaching_the_api(self) -> requests.Response:
        """
        List IP addresses for reaching the API
        :return: requests.Response
        """
        ENDPOINT = "/v1/api-addrs"
        return self._get(url=self.APP_API_URL + ENDPOINT)

    def app_api_submit_a_voucher(
            self, access_token: str, voucher_code: str
    ) -> SubmitAVoucherResponse:
        """
        Submit a voucher
        :param access_token: str Bearer token
        :param voucher_code: str voucher code
        :return: SubmitAVoucherResponse
        """
        ENDPOINT = "/v1/submit-voucher"
        return SubmitAVoucherResponse(
            **self._post(
                url=self.APP_API_URL + ENDPOINT,
                headers={f"Authorization": f"Bearer {access_token}"},
                data={"voucher_code": voucher_code},
            ).json()
        )

    def app_api_submit_a_problem_report(
            self, submit_a_problem_report_parameters: SubmitAProblemReportParameters
    ) -> SubmitAProblemReportResponse:
        """
        Submit a problem report
        :return: SubmitAVoucherResponse
        """
        ENDPOINT = "/v1/problem-report"
        return SubmitAProblemReportResponse(
            **self._post(
                url=self.APP_API_URL + ENDPOINT,
                data=submit_a_problem_report_parameters.model_dump(),
            ).json()
        )

    def app_api_request_a_website_auth_token(self, access_token: str) -> AuthToken:
        """
        Request a website authorization token
        :return: AuthToken
        """
        ENDPOINT = "/v1/www-auth-token"
        return AuthToken(
            **self._post(
                url=self.APP_API_URL + ENDPOINT,
                headers={f"Authorization": f"Bearer {access_token}"},
            ).json()
        )

    def app_api_information_about_app_release(
            self, platform: str, version: str
    ) -> InformationAboutAppReleaseResponse:
        """
        Information about the application release
        :return: InformationAboutAppReleaseResponse
        """
        ENDPOINT = f"/v1/releases/{platform}/{version}"
        return InformationAboutAppReleaseResponse(
            **self._get(url=self.APP_API_URL + ENDPOINT).json()
        )

    def app_api_create_an_apple_in_app_payment(
            self, access_token: str, receipt_string: str
    ) -> CreateAnAppleInAppPaymentResponse:
        """
        Create an Apple In-App payment
        :param access_token: str Bearer token
        :param receipt_string: str An encrypted Base64-encoded App Store receipt
        :return: CreateAnAppleInAppPaymentResponse
        """
        ENDPOINT = "/v1/create-apple-payment"
        return CreateAnAppleInAppPaymentResponse(
            **self._post(
                url=self.APP_API_URL + ENDPOINT,
                headers={f"Authorization": f"Bearer {access_token}"},
                data={"receipt_string": receipt_string},
            ).json()
        )

    def public_api_get_open_vpn_server_list(self) -> OpenVPNServerListResponse:
        """
        Returns a list of OpenVPN servers.
        :return: OpenVPNServerListResponse
        """
        ENDPOINT = "/relays/v1"
        return OpenVPNServerListResponse(
            **self._get(url=self.PUBLIC_API_URL + ENDPOINT).json()
        )

    def public_api_get_wireguard_server_list_v1(self) -> WireGuardServerListResponseV1:
        """
        Returns a list of WireGuard servers from the v1 endpoint.
        :return: WireGuardServerListResponseV1
        """
        ENDPOINT = "/relays/wireguard/v1"
        return WireGuardServerListResponseV1(
            **self._get(url=self.PUBLIC_API_URL + ENDPOINT).json()
        )

    def public_api_get_wireguard_server_list_v2(self) -> WireGuardServerListResponseV2:
        """
        Returns a list of WireGuard servers from the v2 endpoint.
        :return: WireGuardServerListResponseV2
        """
        ENDPOINT = "/relays/wireguard/v2"
        return WireGuardServerListResponseV2(**self._get(url=self.PUBLIC_API_URL + ENDPOINT).json())

    def public_api_create_account(self) -> CreateAccountResponse:
        """
        Creates a new account.
        :return: CreateAccountResponse
        """
        ENDPOINT = "/accounts/v1"
        return CreateAccountResponse(
            **self._post(url=self.PUBLIC_API_URL + ENDPOINT).json()
        )

    def public_api_get_account_information(
            self, token: str
    ) -> GetAccountInformationResponse:
        """
        Returns information about an account.
        :param token: str ID of the account
        :return: GetAccountInformationResponse
        """
        ENDPOINT = f"/accounts/v1/{token}"
        return GetAccountInformationResponse(
            **self._get(url=self.PUBLIC_API_URL + ENDPOINT).json()
        )

    def public_api_activate_voucher_code(
            self,
            account: str,
            code: str,
    ) -> ActivateVoucherCodeResponse:
        """
        Activate a voucher code on an account.
        :param account: str The account to redeem the voucher to
        :param code: str The voucher code to redeem
        :return: ActivateVoucherCodeResponse
        """
        ENDPOINT = "/vouchers/submit/v1"
        response = self._post(
            url=self.PUBLIC_API_URL + ENDPOINT,
            headers={"Content-type": "application/x-www-form-urlencoded"},
            data=Voucher(account=account, code=code).model_dump(),
        )
        return ActivateVoucherCodeResponse(response=response.text)

    def am_i_connected(self) -> requests.Response:
        """
        Check if you are connected to Mullvad using am.i.mullvad.net/connected
        :return: requests.Response
        """
        ENDPOINT = "/connected"
        return self._get(url=self.AM_I_URL + ENDPOINT)

    def am_i_ip(self) -> requests.Response:
        """
        Check your IP address using am.i.mullvad.net/ip
        :return: requests.Response
        """
        ENDPOINT = "/ip"
        return self._get(url=self.AM_I_URL + ENDPOINT)

    def am_i_city(self) -> requests.Response:
        """
        Check your IP geocoded city using am.i.mullvad.net/city
        :return: requests.Response
        """
        ENDPOINT = "/city"
        return self._get(url=self.AM_I_URL + ENDPOINT)

    def am_i_country(self) -> requests.Response:
        """
        Check your IP geocoded country using am.i.mullvad.net/country
        :return: requests.Response
        """
        ENDPOINT = "/country"
        return self._get(url=self.AM_I_URL + ENDPOINT)

    def am_i_json(self) -> requests.Response:
        """
        Return your full IP profile using am.i.mullvad.net/json
        :return: requests.Response
        """
        ENDPOINT = "/json"
        return self._get(url=self.AM_I_URL + ENDPOINT)


mv = MullvadAPIEngine()

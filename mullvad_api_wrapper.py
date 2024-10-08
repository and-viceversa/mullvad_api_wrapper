import requests
from pydantic import BaseModel, Field


class Account(BaseModel):
    id: str | None = Field(None, description="The account token")
    expiry: str | None = Field(
        None, description="The expiry time of the account in ISO 8601 format"
    )


class Location(BaseModel):
    city: str | None = None
    country: str | None = None
    latitude: str | None = None
    longitude: str | None = None


class Locations(BaseModel):
    locations: dict[str, Location] | None = None


class WireGuardRelay(BaseModel):
    hostname: str | None = None
    location: str | None = None
    active: bool | None = None
    owned: bool | None = None
    provider: str | None = None
    ipv4_addr_in: str | None = None
    include_in_country: bool | None = None
    weight: int | None = None
    public_key: str | None = None
    ipv6_addr_in: str | None = None


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


class Voucher(BaseModel):
    account: str | None = None
    code: str | None = None


class OpenVPNServerListResponse(Countries):
    pass


class WireGuardServerListResponseV1(Countries):
    pass


class WireGuardServerListResponseV2(BaseModel):
    locations: Locations | None = None
    wireguard: Wireguard | None = None


class CreateAccountResponse(Account):
    pass


class GetAccountInformationResponse(Account):
    pass


class ActivateVoucherCodeResponse(BaseModel):
    response: str | None = None


class MullvadAPIEngine:
    """
    API calls to api.mullvad.net and am.i.mullvad.net
    """

    API_URL = "https://api.mullvad.net/public"
    AM_I_URL = "https://am.i.mullvad.net"

    def __init__(self):
        self.session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def get_open_vpn_server_list(self) -> OpenVPNServerListResponse:
        """
        Returns a list of OpenVPN servers.
        :return: OpenVPNServerListResponse
        """
        ENDPOINT = "/relays/v1"
        response = self.session.get(url=self.API_URL + ENDPOINT)
        response.raise_for_status()
        return OpenVPNServerListResponse(**response.json())

    def get_wireguard_server_list_v1(self) -> WireGuardServerListResponseV1:
        """
        Returns a list of WireGuard servers from the v1 endpoint.
        :return: WireGuardServerListResponseV1
        """
        ENDPOINT = "/relays/wireguard/v1"
        response = self.session.get(url=self.API_URL + ENDPOINT)
        response.raise_for_status()
        return WireGuardServerListResponseV1(**response.json())

    def get_wireguard_server_list_v2(self) -> WireGuardServerListResponseV2:
        """
        Returns a list of WireGuard servers from the v2 endpoint.
        :return: WireGuardServerListResponseV2
        """
        ENDPOINT = "/relays/wireguard/v2"
        response = self.session.get(url=self.API_URL + ENDPOINT)
        response.raise_for_status()
        return WireGuardServerListResponseV2(**response.json())

    def create_account(self) -> CreateAccountResponse:
        """
        Creates a new account.
        :return: CreateAccountResponse
        """
        ENDPOINT = "/accounts/v1"
        response = self.session.post(url=self.API_URL + ENDPOINT)
        response.raise_for_status()
        return CreateAccountResponse(**response.json())

    def get_account_information(self, token: str) -> GetAccountInformationResponse:
        """
        Returns information about an account.
        :param token: str ID of the account
        :return: GetAccountInformationResponse
        """
        ENDPOINT = "/accounts/v1/"
        response = self.session.get(url=self.API_URL + ENDPOINT + token)
        response.raise_for_status()
        return GetAccountInformationResponse(**response.json())

    def activate_voucher_code(
        self, account: str, code: str, force: bool=False
    ) -> ActivateVoucherCodeResponse:
        """
        Activate a voucher code on an account.
        :param account: str The account to redeem the voucher to
        :param code: str The voucher code to redeem
        TODO: Test with a voucher, remove force param
        :param force: bool True to test
        :return: ActivateVoucherCodeResponse
        """
        if force:
            ENDPOINT = "/vouchers/submit/v1"
            response = self.session.post(
                url=self.API_URL + ENDPOINT,
                headers={"Content-type": "application/x-www-form-urlencoded"},
                data=Voucher(account=account, code=code).model_dump(),
            )
            response.raise_for_status()
            return ActivateVoucherCodeResponse(response=response.text)
        else:
            raise NotImplemented("activate_voucher_code() hasn't been tested with a real voucher. "
                                 "pass force=true to test it.")

    def am_i_connected(self) -> requests.Response:
        """
        Check if you are connected to Mullvad using am.i.mullvad.net/connected
        :return: requests.Response
        """
        ENDPOINT = "/connected"
        response = self.session.get(url=self.AM_I_URL + ENDPOINT)
        response.raise_for_status()
        return response

    def am_i_ip(self) -> requests.Response:
        """
        Check your IP address using am.i.mullvad.net/ip
        :return: requests.Response
        """
        ENDPOINT = "/ip"
        response = self.session.get(url=self.AM_I_URL + ENDPOINT)
        response.raise_for_status()
        return response

    def am_i_city(self) -> requests.Response:
        """
        Check your IP geocoded city using am.i.mullvad.net/city
        :return: requests.Response
        """
        ENDPOINT = "/city"
        response = self.session.get(url=self.AM_I_URL + ENDPOINT)
        response.raise_for_status()
        return response

    def am_i_country(self) -> requests.Response:
        """
        Check your IP geocoded country using am.i.mullvad.net/country
        :return: requests.Response
        """
        ENDPOINT = "/country"
        response = self.session.get(url=self.AM_I_URL + ENDPOINT)
        response.raise_for_status()
        return response

    def am_i_json(self) -> requests.Response:
        """
        Return your full IP profile using am.i.mullvad.net/json
        :return: requests.Response
        """
        ENDPOINT = "/json"
        response = self.session.get(url=self.AM_I_URL + ENDPOINT)
        response.raise_for_status()
        return response

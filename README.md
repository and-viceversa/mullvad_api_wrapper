## Usage
```
with MullvadAPIEngine() as engine:
    print(engine.get_open_vpn_server_list().model_dump(exclude_none=True))
    print(engine.get_wireguard_server_list_v2().model_dump(exclude_none=True))
    print(engine.am_i_country().text)
    print(engine.am_i_json().json())
```
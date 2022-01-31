# Alerta Enhancer Plugin

## Configuration

Add `netbox` to the list of enabled `PLUGINS` and a valid [Netbox](https://github.com/netbox-community/netbox) config (url and token) in `alertad.conf` server configuration file and set plugin-specific variables either in the server configuration file or as environment variables.

```python
PLUGINS = ["netbox"]

NETBOX_URL = "https://demo.netbox.dev"
NETBOK_TOKEN = "some-secret-token"
```

from typing import Any, Callable, Dict, List, Optional

from aiohttp import ClientSession, web

from .views import routes


async def client_session(app: web.Application):
    async with ClientSession() as session:
        app["session"] = session
        yield


def oauth2_app(  # pylint: disable=too-many-arguments
    client_id: str,
    client_secret: str,
    authorize_url: str,
    token_url: str,
    scopes: Optional[List[str]] = None,
    on_login: Optional[Callable[[web.Request, Dict[str, Any]], web.Response]] = None,
    on_error: Optional[Callable[[web.Request, str], web.Response]] = None,
    json_data=True,
    auth_extras=None,
    force_ssl=False,
) -> web.Application:
    """
    Factory to generate an aiohttp application configured as an oauth2 client.

    :param client_id: OAuth2 Client ID (generated by the provider)
    :param client_secret: OAauth2 Client Secret (generated by the provider)
    :param authorize_url: Authorization URL (defined by the provider)
    :param token_url: Token URL (defined by the provider)
    :param scopes: List of scopes to request, typically required.
    :param on_login: Callback to handle the login response. This receives the
                     request (note: this is the request object of _the oauth2 app,
                     not the main app_) and the response retrieved from the token
                     endpoint. It should return an aiohttp.web.Response object.
    :param on_error: Callback to handle the error response, otherwise the user gets
                     a 500.
    :param json_data: True (default) to send JSON to the server in the oauth2 callback,
                      False will use Form Data instead.
    :param auth_extras: If the oauth2 provider supports non-standard parameters this is
                        a way to provide them to the authorization request.
    :param force_ssl: Force the callback URL to use the https scheme.
    """
    app = web.Application()

    app.update(  # pylint: disable=no-member
        CLIENT_ID=client_id,
        CLIENT_SECRET=client_secret,
        AUTHORIZE_URL=authorize_url,
        TOKEN_URL=token_url,
        SCOPES=scopes,
        ON_LOGIN=on_login,
        ON_ERROR=on_error,
        DATA_AS_JSON=json_data,
        AUTH_EXTRAS=auth_extras or {},
        FORCE_SSL=force_ssl,
    )
    app.cleanup_ctx.append(client_session)

    app.add_routes(routes)

    return app

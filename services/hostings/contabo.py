import aiohttp
import contabo_config
import uuid

from data.models.node import Node
from data.models.server_configuration import ServerConfiguration
from data.models.server import Server as NodeServer, Server


async def get_token_data():
    async with aiohttp.ClientSession() as session:
        payload = {
            'client_id': contabo_config.CLIENT_ID,
            'client_secret': contabo_config.CLIENT_SECRET,
            'username': contabo_config.API_USER,
            'password': contabo_config.API_PASSWORD,
            'grant_type': 'password'
        }

        async with session.post(
                'https://auth.contabo.com/auth/realms/contabo/protocol/openid-connect/token',
                proxy='http://127.0.0.1:1087',
                data=payload) as response:

            if response.status != 200:
                return
            return await response.json()


async def get_instances(params: dict = None):
    if params is None:
        query_parameters = ""
    else:
        query_parameters = '?' + '&'.join(key + '=' + value for key, value in params.items())

    request = '/v1/compute/instances' + query_parameters
    while True:
        response_json = await api_get(f'https://api.contabo.com{request}')
        yield response_json['data']
        if response_json['_links']['next'] == '':
            break
        request = response_json['_links']['next']


async def create_server(node: Node, server_configuration: ServerConfiguration):
    try:
        token_data = await get_token_data()
    except:
        return None

    if token_data is None:
        return None

    async with aiohttp.ClientSession() as session:
        headers = {
            'Authorization': f'Bearer {token_data["access_token"]}',
            'x-request-id': f'{uuid.uuid4()}',
        }
        payload = {
            'imageId': f'{server_configuration.image}',
            'productId': f'{server_configuration.server_type}',
            'region': f'{server_configuration.location}',
            'sshKeys': [int(server_configuration.ssh_key)],
            'period': 1,
            'displayName': f'bb-{str.lower(node.type.name)}-{node.id}',
            'defaultUser': 'root'
        }
        try:
            async with session.post(
                    'https://api.contabo.com/v1/compute/instances',
                    headers=headers,
                    json=payload) as response:
                if response.status == 201:
                    response_json = await response.json()
                    response_server_data = response_json['data'][0] if len(response_json['data']) else None
                    if response_server_data is None:
                        return None
                    return NodeServer.create(
                        hosting_id=server_configuration.hosting_id,
                        server_configuration_id=server_configuration.id,
                        hosting_server_id=response_server_data['instanceId'],
                        hosting_status=response_server_data['status'],
                        obsolete=False
                    )
                else:
                    return None
        except:
            return None


async def get_server_status(server: Server):
    server_data = await get_server_data(server)
    if server_data is None:
        return None
    else:
        try:
            return server_data['status']
        except:
            return None


async def get_server_data(server: Server):
    response_json = await api_get(f'https://api.contabo.com/v1/compute/instances/{server.hosting_server_id}')
    response_data = response_json['data'][0] if len(response_json['data']) else None
    if response_data is None:
        return None
    return response_data


async def api_get(url):
    try:
        token_data = await get_token_data()
    except Exception as e:
        print(e)
        return None

    if token_data is None:
        return None

    async with aiohttp.ClientSession() as session:
        headers = {
            'Authorization': f'Bearer {token_data["access_token"]}',
            'x-request-id': f'{uuid.uuid4()}',
        }
        try:
            async with session.get(
                    url,
                    proxy='http://127.0.0.1:1087',
                    headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
        except:
            return None


async def api_post(url, body):
    try:
        token_data = await get_token_data()
    except:
        return None

    if token_data is None:
        return None

    async with aiohttp.ClientSession() as session:
        headers = {
            'Authorization': f'Bearer {token_data["access_token"]}',
            'x-request-id': f'{uuid.uuid4()}',
        }
        payload = body
        try:
            async with session.post(
                    url,
                    headers=headers,
                    json=payload) as response:
                if response.status == 201:
                    response_json = await response.json()
                    response_data = response_json['data'][0] if len(response_json['data']) else None
                    if response_data is None:
                        return None
                    return response_data
                else:
                    return None
        except:
            return None
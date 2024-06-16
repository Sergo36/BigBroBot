import aiohttp
import asyncio
import contabo_config
import uuid

from data.models.node import Node
from data.models.server_configuration import ServerConfiguration


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
                data=payload) as response:

            if response.status != 200:
                # to do logging
                return

            return await response.json()


async def get_instances():
    token_data = get_token_data()
    if token_data is None:
        return

    async with aiohttp.ClientSession() as session:
        headers = {
            'Authorization': f'Bearer {token_data["access_token"]}',
            'x-request-id': f'{uuid.uuid4()}',
        }
        async with session.get(
                'https://api.contabo.com/v1/compute/instances',
                headers=headers) as response:
            if response.status != 200:
                # to do logging
                return

            return await response.json()


async def create_instances(server_configuration: ServerConfiguration, node: Node):
    token_data = get_token_data()
    if token_data is None:
        return

    async with aiohttp.ClientSession() as session:
        headers = {
            'Authorization': f'Bearer {token_data["access_token"]}',
            'x-request-id': f'{uuid.uuid4()}',
        }
        payload = {
            'imageId': f'{server_configuration.image}',
            'productId': f'{server_configuration.server_type}',
            'region': f'{server_configuration.location}',
            'sshKeys': [int(server_configuration.ssh_key)], # as integer
            'period': 1,
            'displayName': f'bb-{node.type}-{node.id}',
            'defaultUser': 'root'
        }
        async with session.post(
                'https://api.contabo.com/v1/compute/instances',
                headers=headers,
                json=payload) as response:
            if response.status != 201:
                # to do logging
                return

            return await response.json()

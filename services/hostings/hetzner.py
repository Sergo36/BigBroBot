from hcloud import Client, APIException
from hcloud.images import Image
from hcloud.locations import Location
from hcloud.server_types import ServerType, ServerTypesClient
from hcloud.servers import Server
from hcloud.ssh_keys import SSHKey

from data.models.node import Node
from data.models.server_configuration import ServerConfiguration
from data.models.server import Server as NodeServer


def get_server_types():
    token = 'CK5V8kZQJwwKL02VP6ZLNx48CXOFgQR7Kn1ObexThOyZzCNhB6CLF3cMCLEiQE3K'
    client = Client(token=token)  # Please paste your API token here
    types = client.server_types.get_all()
    print("Types")
    for type in types:
        print(f'name:{type.data_model.name} discription:{type.data_model.description}')
    locations = client.locations.get_all()
    print("Locations")
    for location in locations:
        print(f'name:{location.data_model.name} discription:{location.data_model.description}')
    images = client.images.get_all()
    print("Images")
    for image in images:
        print(f'name:{image.data_model.name} discription:{image.data_model.description}')
    print("Ssh")
    keys = client.ssh_keys.get_all()
    for key in keys:
        print(f'name:{key.data_model.name} id:{key.data_model.id}')
    servers = client.servers.get_all()
    print("Servers")
    for server in servers:
        print(f'name:{server.data_model.name} id:{server.data_model.id}')


def create_server(node: Node, server_configuration: ServerConfiguration) -> NodeServer:
    token = server_configuration.token
    client = Client(token=token)

    try:
        response = client.servers.create(
            name=f"bb-{node.id}",
            location=Location(name=server_configuration.location),
            image=Image(name=server_configuration.image),
            server_type=ServerType(name=server_configuration.server_type),
            ssh_keys=[SSHKey(name=server_configuration.ssh_key)]
        )
    except:
        return None
    if response.action.complete:
        server = response.server
        return NodeServer.create(
            hosting_id=server_configuration.hosting_id,
            server_configuration_id=server_configuration.id,
            hosting_server_id=server.id,
            obsolete=False
        )
    return None


def delete_server(item_id: int, token: str) -> bool:
    client = Client(token=token)
    server = Server(id=item_id)
    try:
        response = client.servers.delete(server)
    except APIException:
        return False
    return response.complete

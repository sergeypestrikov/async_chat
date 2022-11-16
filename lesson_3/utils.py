import json
from variables import MSG_LENGTH, ENCODING



def get_msg(client):
    encoded_response = client.recv(MSG_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_msg(sock, message):
    json_msg = json.dumps(message)
    encoded_msg = json_msg.encode(ENCODING)
    sock.send(encoded_msg)
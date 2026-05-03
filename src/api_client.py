import json
import zlib
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from base64 import b64encode, b64decode
from fake_useragent import UserAgent


ua = UserAgent()


class ResponseUtil:
    """
    Utility for parsing and decrypting the response from the Levels FYI API.

    NOTE: The API response payload is encrypted and compressed. This decryption is based on the rendered JS code

    Source: https://stackoverflow.com/questions/76496884/how-levels-fyi-is-encoding-the-api-response
    """

    def __init__(self):
        self.key = "levelstothemoon!!"
        self.n = 16

    def parse(self, t):
        if "payload" not in t:
            return t
        r = t["payload"]
        a = MD5.new(self.key.encode()).digest()
        a_base64 = b64encode(a)[: self.n]
        cipher = AES.new(a_base64, AES.MODE_ECB)
        decrypted_data = cipher.decrypt(b64decode(r))
        decompressed_data = zlib.decompress(decrypted_data)
        return json.loads(decompressed_data.decode())


_parser = ResponseUtil()


def parse_levels_api_response(body: dict | list) -> dict | list:
    """
    Decrypt/decompress Levels API JSON when wrapped in ``payload``; return passthrough body otherwise.

    Plain JSON arrays/objects are returned unchanged.
    """
    return _parser.parse(body)

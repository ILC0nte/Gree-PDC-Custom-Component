import base64
import json
import socket
import logging
import threading
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

_LOGGER = logging.getLogger(__name__)

from .const import GENERIC_KEY

class GreePDCClient:
    @staticmethod
    def scan(host, timeout=2):
        """Scan for devices at the given host (can be a specific IP or broadcast)."""
        devices = []
        _LOGGER.debug("Scanning for devices at %s", host)
        s = socket.socket(type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        s.settimeout(timeout)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if host.endswith('.255'):
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
        try:
            s.sendto(b'{"t":"scan"}', (host, 7000))
            while True:
                try:
                    data, addr = s.recvfrom(2048)
                    resp = json.loads(data.decode('utf-8'))
                    # We need a temporary client to decrypt the pack
                    temp_client = GreePDCClient(addr[0], "", "")
                    pack_decrypted = temp_client._decrypt(resp['pack'], GENERIC_KEY)
                    pack_json = json.loads(pack_decrypted)
                    
                    device_id = pack_json.get('cid') or resp.get('cid')
                    name = pack_json.get('name', 'Unknown Device')
                    
                    if device_id:
                        devices.append({
                            "id": device_id,
                            "name": name,
                            "host": addr[0]
                        })
                    if not host.endswith('.255'): # If it's a specific IP, we probably only want one
                        break
                except socket.timeout:
                    break
        except Exception as e:
            _LOGGER.error("Scan failed for %s: %s", host, e)
        finally:
            s.close()
        return devices

    def bind(self):
        """Bind to the device to get the specific encryption key."""
        _LOGGER.debug("Binding to device %s at %s", self.device_id, self.host)
        bind_pack = f'{{"mac":"{self.device_id}","t":"bind","uid":0}}'
        bind_pack_encrypted = self._encrypt(bind_pack, GENERIC_KEY)
        
        bind_request = {
            "cid": "app",
            "i": 1,
            "pack": bind_pack_encrypted,
            "t": "pack",
            "tcid": self.device_id,
            "uid": 0
        }
        
        try:
            bind_resp_str = self._send_data(json.dumps(bind_request))
            bind_resp = json.loads(bind_resp_str)
            
            if bind_resp.get("t") == "pack":
                bind_pack_decrypted = self._decrypt(bind_resp["pack"], GENERIC_KEY)
                bind_result = json.loads(bind_pack_decrypted)
                
                if bind_result.get("t", "").lower() == "bindok":
                    self.device_key = bind_result["key"]
                    return True
                else:
                    _LOGGER.error("Binding failed for %s: %s", self.host, bind_result)
            else:
                _LOGGER.error("Unexpected binding response for %s: %s", self.host, bind_resp)
        except Exception as e:
            _LOGGER.error("Binding failed for %s: %s", self.host, e)
            
        return False

    def __init__(self, host, device_id, device_key):
        self.host = host
        self.device_id = device_id
        self.device_key = device_key
        self.port = 7000
        self._lock = threading.Lock()

    def _add_pkcs7_padding(self, data):
        length = 16 - (len(data) % 16)
        padded = data + chr(length) * length
        return padded

    def _create_cipher(self, key):
        return Cipher(algorithms.AES(key.encode('utf-8')), modes.ECB(), backend=default_backend())

    def _encrypt(self, pack, key):
        encryptor = self._create_cipher(key).encryptor()
        pack_padded = self._add_pkcs7_padding(pack)
        pack_encrypted = encryptor.update(bytes(pack_padded, encoding='utf-8')) + encryptor.finalize()
        pack_encoded = base64.b64encode(pack_encrypted)
        return pack_encoded.decode('utf-8')

    def _decrypt(self, pack_encoded, key):
        decryptor = self._create_cipher(key).decryptor()
        pack_decoded = base64.b64decode(pack_encoded)
        pack_decrypted = decryptor.update(pack_decoded) + decryptor.finalize()
        pack_unpadded = pack_decrypted[0:pack_decrypted.rfind(b'}') + 1]
        return pack_unpadded.decode('utf-8')

    def _send_data(self, data):
        with self._lock:
            s = socket.socket(type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
            s.settimeout(3)
            try:
                s.sendto(data.encode('utf-8'), (self.host, self.port))
                response, _ = s.recvfrom(2048)
                return response.decode('utf-8')
            except socket.timeout:
                _LOGGER.error("Timeout (3s) sending data to %s", self.host)
                raise
            except Exception as e:
                _LOGGER.error("Error sending data to %s: %s", self.host, e)
                raise
            finally:
                s.close()

    def get_values(self, cols):
        cols_str = ','.join(f'"{c}"' for c in cols)
        pack = f'{{"cols":[{cols_str}],"mac":"{self.device_id}","t":"status"}}'
        pack_encrypted = self._encrypt(pack, self.device_key)
        
        _LOGGER.debug("Sending status request to %s for %d columns", self.host, len(cols))
        request = {
            "cid": "app",
            "i": 0,
            "pack": pack_encrypted,
            "t": "pack",
            "tcid": self.device_id,
            "uid": 0
        }
        
        response_str = self._send_data(json.dumps(request))
        response = json.loads(response_str)
        
        if response.get("t") == "pack":
            pack_decrypted = self._decrypt(response["pack"], self.device_key)
            return json.loads(pack_decrypted)
        return None

    def set_values(self, values_dict):
        opts = list(values_dict.keys())
        ps = list(values_dict.values())
        
        opts_str = ','.join(f'"{o}"' for o in opts)
        ps_str = ','.join(str(p) for p in ps)
        
        pack = f'{{"opt":[{opts_str}],"p":[{ps_str}],"t":"cmd"}}'
        pack_encrypted = self._encrypt(pack, self.device_key)
        
        request_obj = {
            "cid": "app",
            "i": 0,
            "pack": pack_encrypted,
            "t": "pack",
            "tcid": self.device_id,
            "uid": 0
        }
        request_str = json.dumps(request_obj)

        for attempt in range(6):  # Initial attempt + up to 5 retries
            if attempt > 0:
                _LOGGER.debug("Retrying command to %s (retry %d/5)", self.host, attempt)
            else:
                _LOGGER.debug("Sending command to %s: %s", self.host, values_dict)
                
            try:
                response_str = self._send_data(request_str)
                response = json.loads(response_str)
                
                if response.get("t") == "pack":
                    pack_decrypted = self._decrypt(response["pack"], self.device_key)
                    result = json.loads(pack_decrypted)
                    success = result.get("r") == 200
                    if success:
                        _LOGGER.debug("Command successful on %s", self.host)
                        return True
                    else:
                        _LOGGER.error("Command failed on %s (attempt %d): %s", self.host, attempt + 1, result)
                else:
                    _LOGGER.error("Unexpected response from %s (attempt %d): %s", self.host, attempt + 1, response)
            except Exception as e:
                _LOGGER.error("Error sending command to %s (attempt %d): %s", self.host, attempt + 1, e)
            
            if attempt < 5:
                time.sleep(1)
        
        _LOGGER.error("Command failed on %s after 5 retries", self.host)
        return False

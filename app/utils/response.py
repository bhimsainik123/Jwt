import requests
from app.proto import my_pb2, output_pb2
from app.utils.gen_token import encrypt_message, get_token
from config import AES_KEY, AES_IV
import binascii
from datetime import datetime, timezone
from app.utils.decode_token import decode
from pprint import pprint
import json
from byte import *
from config import *
from app.utils.xthug import DeCode_PackEt
def parse_response(response_content):
    # Parse the response to extract key fields
    response_dict = {}
    lines = response_content.split("\n")
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            response_dict[key.strip()] = value.strip().strip('"')
    return response_dict

def GeT_PLayer_level(uid, Token,region):
    try:
        payload_hex = "08" + Encrypt_ID(str(uid)) + "1801"
        data = bytes.fromhex(encrypt_api(payload_hex))

        if region == "IND":
             uri = "https://client.ind.freefiremobile.com/"
        elif region in {"BR", "US", "SAC", "NA"}:
            uri = "https://client.us.freefiremobile.com/"
        else:
             uri = "https://clientbp.ggwhitehawk.com/"
        
        url = uri+"GetPlayerPersonalShow"
        print(url,uid)
        headers = {
            "Authorization": f"Bearer {Token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": REALEASE_VERSION,
            "Content-Type": "application/octet-stream",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-N975F Build/PI)",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close"
        }

        response = requests.post(url, headers=headers, data=data, verify=False)
        
        if response.status_code != 200:
            
            return None,None 
            
        # --- D�codage de la r�ponse ---
        packet = binascii.hexlify(response.content).decode('utf-8')
        decoded = DeCode_PackEt(packet)
        Thug_data = json.loads(decoded)
        player_data = Thug_data.get("1", {}).get("data", {})

        level = player_data.get("6", {}).get("data", "0")
        exp = player_data.get("7", {}).get("data", "0")
        return level,exp

    except Exception:
        return None,None
    
def process_token(uid, password):
    error, token_data = get_token(password, uid)
    
    # if not token_data:
    #     return {"uid": uid, "error": "Failed to retrieve token"},500
    
    
    
    if error ==True:
        error =token_data.get("error")
        return {"error": True,"message":error,"status_code": 500}
    
    def current_timestamp(fmt="iso", tz=timezone.utc):
        now = datetime.now(tz)
        if fmt == "iso":
            # ISO 8601 with Z suffix for UTC
            return now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
        if fmt == "epoch":
            return int(now.timestamp())
        # assume custom strftime format
        return now.strftime(fmt)

    game_data = my_pb2.GameData()
    game_data.timestamp = current_timestamp()
    game_data.game_name = "free fire"
    game_data.game_version = 1
    game_data.version_code = "2.120.3"
    game_data.os_info = "Android OS 11 / API-30 (RKQ1.201112.002/eng.realme.20221110.193122)"
    game_data.device_type = "Handheld"
    game_data.network_provider = "JIO"
    game_data.connection_type = "MOBILE"
    game_data.screen_width = 720
    game_data.screen_height = 1600
    game_data.dpi = "280"
    game_data.cpu_info = "ARM Cortex-A73 | 2200 | 4"
    game_data.total_ram = 4096
    game_data.gpu_name = "Adreno (TM) 610"
    game_data.gpu_version = "OpenGL ES 3.2"
    game_data.user_id = "Google|c71ff1e2-457f-4e2d-83a1-c519fa3f2a44"
    game_data.ip_address = "182.75.115.22"
    game_data.language = "en"
    game_data.open_id = token_data["open_id"]
    game_data.access_token = token_data["access_token"]
    game_data.platform_type = 4
    game_data.device_form_factor = "Handheld"
    game_data.device_model = "realme RMX1825"
    game_data.field_60 = 30000
    game_data.field_61 = 27500
    game_data.field_62 = 1940
    game_data.field_63 = 720
    game_data.field_64 = 28000
    game_data.field_65 = 30000
    game_data.field_66 = 28000
    game_data.field_67 = 30000
    game_data.field_70 = 4
    game_data.field_73 = 2
    game_data.library_path = "/data/app/com.dts.freefireth-XaT5M7jRwEL-nPaKOQvqdg==/lib/arm"
    game_data.field_76 = 1
    game_data.apk_info = "2f4a7f349f3a3ea581fc4d803bc5a977|/data/app/com.dts.freefireth-XaT5M7jRwEL-nPaKOQvqdg==/base.apk"
    game_data.field_78 = 6
    game_data.field_79 = 1
    game_data.os_architecture = "64"
    game_data.build_number = "2022041388"
    game_data.field_85 = 1
    game_data.graphics_backend = "OpenGLES3"
    game_data.max_texture_units = 16383
    game_data.rendering_api = 4
    game_data.encoded_field_89 = "\x10U\x15\x03\x02\t\rPYN\tEX\x03AZO9X\x07\rU\niZPVj\x05\rm\t\x04c"
    game_data.field_92 = 8999
    game_data.marketplace = "3rd_party"
    game_data.encryption_key = "Jp2DT7F3Is55K/92LSJ4PWkJxZnMzSNn+HEBK2AFBDBdrLpWTA3bZjtbU3JbXigkIFFJ5ZJKi0fpnlJCPDD2A7h2aPQ="
    game_data.total_storage = 64000
    game_data.field_97 = 1
    game_data.field_98 = 1
    game_data.field_99 = "4"
    game_data.field_100 = b"4"
    

    # Serialize the data
    serialized_data = game_data.SerializeToString()

    # Encrypt the data
    encrypted_data = encrypt_message(AES_KEY, AES_IV, serialized_data)
    hex_encrypted_data = binascii.hexlify(encrypted_data).decode("utf-8")

    # Send the encrypted data to the server
    url = "https://loginbp.ggpolarbear.com/MajorLogin"
    headers = {  
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PPR1.180720.122)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": REALEASE_VERSION
    }
    edata = bytes.fromhex(hex_encrypted_data)
    # print(edata)
    try:
        response = requests.post(
            url, data=edata, headers=headers, verify=False, timeout=10
        )
        if response.status_code == 200:
            
            example_msg = output_pb2.Lokesh()
            try:
                example_msg.ParseFromString(response.content)
                # Parse the response to extract key fields
                response_dict = parse_response(str(example_msg))
                token = response_dict.get("token", "N/A")
                region=response_dict.get("region", "N/A")

                account_id ,nickname,release_version =decode(token)
                level,exp = GeT_PLayer_level(account_id,token,region)
                print( level,exp)
                if not level or not exp:
                    level,exp = 0,0

                
                mssg= {
                    "status_code":response.status_code,
                    "server":region ,
                    "token": token,
                    "token_access" : game_data.access_token,
                    "open_id":game_data.open_id,
                    "account_id":account_id,
                    "nickname":nickname,

                    "error":False,
                    "exp":exp,
                    "level":level,
                }
                
                return mssg
            except Exception as e:
                return {"uid": uid, "error": f"Failed to deserialize the response: {e}"}
        else:
            print(f"Failed to retrieve token2 for UID {uid}: {response.text}")
            return {
                "status_code":response.status_code,
                "message":{response.reason},
                "error": True,
            }
    except requests.RequestException as e:
        return {"status_code":response.status_code,"uid": uid, "error": f"An error occurred while making the request: {e}"}

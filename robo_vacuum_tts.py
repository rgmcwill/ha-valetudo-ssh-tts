import sys, logging, json, ipaddress, pathlib, configparser
import urllib.parse
import urllib.request
import paramiko.client

# constants
TTS_URL_ENDPOINT = "api/tts_get_url"
TEMP_AUDIO_FILE = "/tmp/tts.wav"

# methods
def is_valid_url(url):
    try:
        return all([url.scheme, url.netloc])
    except ValueError:
        return False

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def is_valid_file_path(file_path):
    try:
        path = pathlib.Path(file_path)
        # Check if the path exists and is a file
        return path.is_file()
    except Exception:
        return False

config = configparser.ConfigParser()
config.read('config.ini')

# args (home assistant url, home assistant token, robo vacuum ip, robo vacuum ssh key file path)
if (len(sys.argv) < 3):
    logging.error("Wrong number of params. Got {} but wanted 2".format((len(sys.argv)-1)))
    exit()

MESSAGE = sys.argv[2]
HOMEASSISTANT_BASE_URL = config.get('Settings', 'homeassistant_url')
BEARER_TOKEN = sys.argv[1]
ROBO_VACCUM_IP = config.get('Settings', 'robot_ip')
ROBO_VACCUM_SSH_KEY_PATH = config.get('Settings', 'robot_ssh_key_path')

# no need to check 1st arg
# check 2nd arg
homeassistant_url = urllib.parse.urlparse(HOMEASSISTANT_BASE_URL + ('' if HOMEASSISTANT_BASE_URL[-1] == '/' else '/') + TTS_URL_ENDPOINT)
if (not is_valid_url(homeassistant_url)):
    logging.error("The provided url is invalid: {}".format(homeassistant_url))
    exit()

# no need to check 3rd arg
# check 4th arg
if (not is_valid_ip(ROBO_VACCUM_IP)):
    logging.error("The provided ip is invalid: {}".format(ROBO_VACCUM_IP))
    exit()

# check 5th arg
if (not is_valid_file_path(ROBO_VACCUM_SSH_KEY_PATH)):
    logging.error("The provided path to the ssh privatre key is invalid: {}".format(ROBO_VACCUM_SSH_KEY_PATH))
    exit()

body = {
    "engine_id": "tts.piper",
    "message": MESSAGE,
    "options": {
        "voice": "en_US-libritts_r-medium"
  }
}

ha_request = urllib.request.Request(homeassistant_url.geturl(), data=json.dumps(body).encode('utf-8'), method='POST')
ha_request.add_header('Authorization','Bearer {}'.format(BEARER_TOKEN))
ha_request.add_header('Content-Type','application/json')

audio_clip_url = None
try:
    with urllib.request.urlopen(ha_request) as response:
        # Read and saves the url from the response
        audio_clip_url = json.loads(response.read().decode("utf-8")).get('url')
except Exception as e:
    logging.error(f"An error occurred: {e}")
    exit()

logging.info(audio_clip_url)

# Create an SSH client
client = paramiko.SSHClient()

try:
    # Automatically add the server's host key (this is insecure and should be used with caution)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Load the private key
    private_key = paramiko.RSAKey(filename=ROBO_VACCUM_SSH_KEY_PATH)

    # Connect to the SSH server
    client.connect(ROBO_VACCUM_IP, 22, username='root', pkey=private_key)

    # Run some commands on the server
    commands = [
        f"wget -O {TEMP_AUDIO_FILE} {audio_clip_url}",
        f"aplay {TEMP_AUDIO_FILE}"
    ]

    for command in commands:
        stdin, stdout, stderr = client.exec_command(command)
        logging.info(f"Output of '{command}':\n{stdout.read().decode('utf-8')}")

finally:
    # Close the SSH connection
    client.close()
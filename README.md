## ha-valetudo-ssh-tts
This is a basic python script that makes a request to a home assistant server to generate a `.wav` audio file, then login as root to a robot vacuum via ssh, pull down that generated `.wav` file from the home assistant server via `wget` and play it with the `aplay` command. 

### Prerequisites:
* Python 3.x
    * I am assuming theses are basic and well maintained enough dependencies where there are no breaking changes between Python 3 minor versions.
* A Home Assistant server running the [piper add-on](https://github.com/rhasspy/piper/).
* A Home Assistant [long-lived access tokens](https://www.home-assistant.io/docs/authentication/#your-account-profile).
* A robot vacuum with root/ssh access, an ssh key file used to login and `aplay`
    * I setup [Valetudo](https://valetudo.cloud/) on my robot vacuum which provided ssh access.

### To Run:
1. Edit the `config.ini` and fill in with your values.
2. Run `pip install -r requirements.txt` to install the required dependencies.
3. Run with `--help` arg for usage:
    * `python robo_vacuum_tts.py --help`

### Examples:
```shell
python robo_vacuum_tts.py --token "eyabcdefghijklmnopqrstuvwxyz13456789.eyabcdefghijklmnopqrstuvwxyz13456789abcdefghijklmnopqrstuvwxyz13456789abcdefghijklmnopqrstuvwxyz13456789abcdefghijklmnopqrstuvwxyz13456789.abcdefghijklmnopqrstuvwxyz13456789" --message"A Message"
```

```shell
python robo_vacuum_tts.py -i
```
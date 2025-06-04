import paramiko
import os
from dotenv import load_dotenv

class Server:
    def __init__(self):
        load_dotenv()
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(os.getenv("server_ip"), port=22, username=os.getenv("server_user"), password=os.getenv("server_password"))
    
    @property
    def suricata_datas(self):
        
        self.client.exec_command(f"suricata -r pcap_datas/2024-09-19-file-downloader-to-Lumma-Stealer.pcap")
        sftp = self.client.open_sftp()
        sftp.get(f"{os.getenv("remote_path")}/eve.json",f"{os.getcwd()}/eve.json")

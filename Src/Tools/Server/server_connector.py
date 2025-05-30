import paramiko
import os
from dotenv import load_dotenv
import pandas as pd

class Server:
    def __init__(self):
        load_dotenv()
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect("IP Address", port=22, username="user", password="password")
    
    @property
    def suricata_datas(self):
        
        self.client.exec_command(f"suricata -r pcap_datas/2024-09-19-file-downloader-to-Lumma-Stealer.pcap")
        sftp = self.client.open_sftp()
        sftp.get(f"{path}eve.json",f"{os.getcwd()}/eve.json")

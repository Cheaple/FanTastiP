# -*- coding: utf-8 -*-
"""An FTP client class based on RFC 959.

@author: CHEN Yule
"""

import socket
import re
import os
import random
from time import sleep
class FTP:
    def __init__(self):
        self.logged_ = False
        self.mode = 'PORT'
        
    def print_(self, s):
        print(s)
        
    def send(self, cmd):
        self.print_("Send command: " + cmd)
        self.ctr_socket_.sendall(cmd.encode("utf-8"))
        return self.receive()
        
    def receive(self):
        rps = self.ctr_socket_.recv(1024).decode("utf-8")
        self.print_("Response from server: " + rps)
        return rps
    
    def login(self, ip = '127.0.0.1', port = 21, password = "anonymous@", username = "anonymous"):
        self.server_ip = ip
        self.ctr_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ctr_socket_.connect((ip, port))       
        self.start_point = 0
        self.print_('Response from server:' + self.ctr_socket_.recv(1024).decode("utf-8"))
        if not self.send("USER " + username + "\r\n").startswith('331'):
            return False
        if not self.send("PASS " + password + "\r\n").startswith('230'):
            self.logged_ = True 
            return False
        if not self.set_type('I'):  # Set server to binary mode
            return False
        return True
    
    def logout(self):
        rps = self.send("QUIT\r\n")
        self.ctr_socket_.close()
        self.logged_ = False
        return rps.startswith('221')
    
    def set_port_mode(self):
        self.mode = 'PORT'
        
    def set_pasv_mode(self):
        self.mode = 'PASV'
        
    def port(self):
        '''Build a data connection in PORT mode.'''
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        #ip = sock.getsockname()[0]  # get local ip address
        ip = self.ctr_socket_.getsockname()[0]
        port = random.randint(20000, 65536)
        addr = ip.replace('.', ',') + ',' + str(port // 256) + "," + str(port % 256)
        if not self.send("PORT " + addr + "\r\n").startswith('200'):
            return False
        
        self.data_listen_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_listen_socket_.bind((ip, port))
        self.data_listen_socket_.listen(10)
        
        return True
    
    def pasv(self):
        '''Build a data connection in PASV mode.'''
        rps = self.send("PASV\r\n")
        if not rps.startswith('227'):
            return False
        pattern = re.compile(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', re.ASCII)
        match = pattern.search(rps)
        num = match.groups()
        server_ip = '.'.join(num[:4])
        server_port = int(num[4]) * 256 + int(num[5])
        sleep(1)
        self.data_socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket_.connect((self.server_ip, server_port))   
        return True
    
    def set_rest(self, start_point):
        self.start_point = start_point
    
    def build_data_connection(self, cmd):
        '''Build a data connection depending on client's mode for file transfer.'''
        if self.mode == 'PASV' and self.pasv():
            if self.start_point == 0 or self.send("REST " + str(self.start_point) + "\r\n"):  # Set start point
                if self.send(cmd).startswith('150'):
                    return True
        elif self.mode == 'PORT' and self.port():
            if self.start_point == 0 or self.send("REST " + str(self.start_point) + "\r\n"):  # Set start point
                if self.send(cmd).startswith('150'):
                    self.data_socket_, addr = self.data_listen_socket_.accept()
                    return True
        return False
    
    def close_data_connection(self):
        '''close the data connection depending on client's mode for file transfer.'''
        if self.mode == 'PORT': 
            self.data_listen_socket_.close()
        self.data_socket_.close()
            
    def download_file(self, path, local_path, output_progress = None, buf_size = 8192):
        '''Download a file from remote server.
        If function output_progress is not None, use it to output the number of bytes transferred
        '''
        downloaded_size = 0
        if os.path.isfile(local_path):  # If file had been partly transferred, 
            downloaded_size = (os.path.getsize(local_path))
            self.set_rest(downloaded_size)  # set start point to resume transfer
        if not self.build_data_connection("RETR " + path + "\r\n"):
            return False
        
        # transfer in binary mode
        try:
            with open(local_path, "ab") as fp:
                size = downloaded_size
                while 1:
                    data = self.data_socket_.recv(buf_size)
                    if not data:
                        break;
                    fp.write(data)
                    size += len(data)
                    if output_progress != None:
                        output_progress(size)
        finally:
            self.close_data_connection()
            self.start_point = 0  # Reset start point
        if not self.receive().startswith('226'):
            return False
        return True
        
    def upload_file(self, path, output_progress = None, buf_size = 8192):
        '''Upload a local file to remote server.
        If function output_progress is not None, use it to output transfer process.
        '''
        uploaded_size = 0
        rps = self.send("SIZE " + path.split('/')[-1] + "\r\n")
        if rps.startswith("213"):  # If file had been partly transferred, 
            uploaded_size = int(rps[4:])
            self.set_rest(uploaded_size)  # set start point to resume transfer
        
        # Path may be a absolute path. In STOR command, we transform path to a relative path
        if not self.build_data_connection("STOR " + path.split('/')[-1] + "\r\n"):
            return False
                    
        # transfer in binary mode
        try:
            with open(path,'rb') as fp:
                size = uploaded_size
                fp.seek(uploaded_size)
                while 1:
                   data = fp.read(buf_size)
                   if not data:
                       break
                   self.data_socket_.sendall(data)
                   size += len(data)
                   # print("Having uploaded %d bytes" % size)
                   if output_progress != None:
                       output_progress(size)
        finally:        
            self.close_data_connection()
            self.start_point = 0  # Reset start point
        if not self.receive().startswith('226'):
            return False
        return True
    
    def list(self, path = '', print_func = print):
        '''Get a list of files from remote server.'''
        if not self.build_data_connection("LIST " + path + "\r\n"):
            return False
        with self.data_socket_.makefile('rb') as server_file:
            for line in server_file:
                print_func(line.decode('utf-8'))
        self.close_data_connection()
        if not self.receive().startswith('226'):
            return True
    
    def get_file_size(self, path):
        '''If path is a directory, return size of its last file;
        if path is a file, return its size.
        '''
        rps = self.send("SIZE " + path + "\r\n")
        if not rps.startswith('213'):
            return -1
        return int(rps[4:])
    
    def cwd(self, path):
        return self.send("CWD " + path + "\r\n").startswith('250')
    
    def pwd(self):
        rps = self.send("PWD\r\n")
        if rps.startswith('257'):
            return True
        return False
    
    def mkd(self, path):
        return self.send("MKD " + path + "\r\n")
    
    def rmd(self, path):
        return self.send("RMD " + path + "\r\n").startswith('250')
    
    def set_type(self, repr_type = 'I'):
        return self.send("TYPE " + repr_type + "\r\n").startswith('200')
    
    def sys_type(self):
        rps = self.send("SYST\r\n")
        if rps.startswith('215'):
            return rps[4:] 
        return None
    
    def rename(self, path, new_path):
        if not self.send("RNFR " + path + "\r\n").startswith('350'):
            return ''
        return self.send("RNTO " + new_path + "\r\n")

    
    
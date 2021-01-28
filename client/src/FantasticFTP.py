# -*- coding: utf-8 -*-
"""An FTP client GUI class.

@author: CHEN Yule
"""

from FanTastiP import FTP
import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
import re
import os
from PIL import Image, ImageTk


class FantasticFTP(FTP):
    '''GUI of FanTastiP client'''
    def __init__(self):
        FTP.__init__(self)
        
        self.top_ = tk.Tk()  
        self.top_.title("Fantastic FTP")
        self.top_.geometry("460x568")  
        
        # server ip and port
        self.ip_label_ = tk.Label(self.top_, text = "Server IP")
        self.ip_label_.place(x = 10,y = 16)
        
        self.port_label_ = tk.Label(self.top_, text = "Server Port",)
        self.port_label_.place(x = 180, y = 16)
        
        self.ip_entry_ = tk.Entry(self.top_)
        self.ip_entry_.place(x = 70, y = 16, width = 100)
        
        self.port_entry_ = tk.Entry(self.top_)
        self.port_entry_.place(x = 254, y = 16, width = 100)
        self.port_entry_.insert(0, '21')  # Default server port: 21
        
        # connect and disconnect buttons
        self.connect_button_ = tk.Button(self.top_, command = self.connect, text = "Connect", font = ('Comic Sans MS',10))
        self.connect_button_.place(x = 370, y = 10, width = 75)
        
        # command line window
        self.cmd_line_win_ = tk.Listbox(self.top_, font = ('candara', 10), selectbackground = 'black')
        self.cmd_line_win_.place(x = 20, y = 60, width = 420)
    
        # file operation buttons
        self.img_back_ = ImageTk.PhotoImage(Image.open ("back.jpg").resize((12, 12)))
        self.back_button_ = tk.Button(self.top_, command = self.click_back, image = self.img_back_, state = tk.DISABLED)
        self.back_button_.place(x = 20, y = 236)
        
        self.img_mkd_ = ImageTk.PhotoImage(Image.open ("mkd.jpg").resize((12, 12)))
        self.mkd_button_ = tk.Button(self.top_, command = self.click_mkd, image = self.img_mkd_, state = tk.DISABLED)
        self.mkd_button_.place(x = 45, y = 236)
        
        self.img_rmd_ = ImageTk.PhotoImage(Image.open ("rmd.jpg").resize((12, 12)))
        self.rmd_button_ = tk.Button(self.top_, command = self.click_rmd, image = self.img_rmd_, state = tk.DISABLED)
        self.rmd_button_.place(x = 70, y = 236)
        
        self.img_rename_ = ImageTk.PhotoImage(Image.open ("rename.jpg").resize((12, 12)))
        self.rename_button_ = tk.Button(self.top_, command = self.click_rename, image = self.img_rename_, state = tk.DISABLED)
        self.rename_button_.place(x = 95, y = 236)
        
        # server directory window
        self.server_dir_label_ = tk.Label(self.top_, text = "Server Working Directory", font = ('Comic Sans MS',10))
        self.server_dir_label_.place(x = 150, y = 234, width = 420)
        
        self.type_label_ = tk.Label(self.top_, text = "Type")
        self.type_label_.place(x = 20,y = 255)
        
        self.size_label_ = tk.Label(self.top_, text = "Size")
        self.size_label_.place(x = 80,y = 255)
        
        self.time_label_ = tk.Label(self.top_, text = "Time")
        self.time_label_.place(x = 160,y = 255)
        
        self.name_label_ = tk.Label(self.top_, text = "Name")
        self.name_label_.place(x = 260,y = 255)
        
        self.server_dir_win_ = tk.Listbox(self.top_, font = ('candara', 10), cursor = 'cross', height = 5, selectbackground = 'black')
        self.server_dir_win_.place(x = 20, y = 275, width = 420)
        self.server_dir_win_.bind('<Double-Button-1>', self.click_file)
        
        # Download
        self.server_file_label_ = tk.Label(self.top_, text = "Server File")
        self.server_file_label_.place(x = 20,y = 376)
        
        self.server_file_entry_ = tk.Entry(self.top_)
        self.server_file_entry_.place(x = 90, y = 376, width = 200)
        
        self.img_reset_ = ImageTk.PhotoImage(Image.open ("reset.jpg").resize((12, 12)))
        self.reset_button_ = tk.Button(self.top_, command = self.reset_server_file, image = self.img_reset_, state = tk.DISABLED)
        self.reset_button_.place(x = 295, y = 376)
        
        self.download_button_ = tk.Button(self.top_, command = self.download, text = "Download", font = ('Comic Sans MS',10), state = tk.DISABLED)
        self.download_button_.place(x = 370, y = 370, width = 75)
        
        # Upload
        self.local_file_label_ = tk.Label(self.top_, text = "Local File")
        self.local_file_label_.place(x = 20,y = 411)
        
        self.local_file_entry_ = tk.Entry(self.top_)
        self.local_file_entry_.place(x = 90, y = 411, width = 200)
        
        self.img_open_ = ImageTk.PhotoImage(Image.open ("open.jpg").resize((12, 12)))
        self.open_button_ = tk.Button(self.top_, command = self.choose_local_file, image = self.img_open_, state = tk.DISABLED)
        self.open_button_.place(x = 295, y = 411)
        
        self.upload_button_ = tk.Button(self.top_, text = "Upload", command = self.upload, font = ('Comic Sans MS',10), state = tk.DISABLED)
        self.upload_button_.place(x = 370, y = 405, width = 75)
        
        # mode change button
        self.mode_button_ = tk.Button(self.top_, text = "PORT", command = self.change_port, font = ('Comic Sans MS',10), state = tk.DISABLED)
        self.mode_button_.place(x = 16, y = 443, width = 75)
        
        # task window
        self.task_label_ = tk.Label(self.top_, text = "Task", font = ('Comic Sans MS',10))
        self.task_label_.place(x = 407, y = 455)
        
        self.task_win_ = tk.Listbox(self.top_, font = ('candara', 10), height = 4, selectbackground = 'black')
        self.task_win_.place(x = 20, y = 478, width = 420)
        
        # Close GUI
        self.top_.protocol('WM_DELETE_WINDOW', self.close_window)
        
        self.refresh()
        self.run()
    
    def close_window(self):
        if self.logged_:  # if connected,
            self.ctr_socket_.sendall("QUIT\r\n".encode("utf-8"))  # close connection
        self.top_.destroy()
    
    def print_(self, msg):
        '''Overload self.print_() to output to GUI's command line window.'''
        print(msg)
        self.cmd_line_win_.insert('end', msg)  # Output records onto command line window
        
        # Set color
        if msg.startswith('Send'):
            self.cmd_line_win_.itemconfigure('end', fg = 'green')
        elif msg.startswith('Res'):
            self.cmd_line_win_.itemconfigure('end', fg = 'purple')
        elif msg.startswith('Err'):
            self.cmd_line_win_.itemconfigure('end', fg = 'red')
        self.cmd_line_win_.see(self.cmd_line_win_.size())  # Move to command line window's latest record
            
    def print_to_server_dir(self, msg):
        '''Add a file to server directory window'''
        print(msg)
        self.server_dir_win_.insert('end', self.parse_file_info(msg))
        if msg[0] == 'd':
            self.server_dir_win_.itemconfigure('end', fg = 'blue')
    
    def print_to_task_win(self, msg):
        '''Print to task window'''
        self.task_win_.insert('end', msg)
        self.task_win_.update()
    
    def update_server_dir_win(self):
        self.server_dir_win_.delete(0, 'end')  # Clear server directory window
        try:
            self.list(print_func = self.print_to_server_dir)  # Update server directory window
            self.pwd()
        except Exception as err:
            self.print_("Error: " + str(err))
            tk.messagebox.showerror("errorWindow", err)
    
    def parse_file_info(self, file_info):
        '''Parse file info returned by LIST command.
        This function need to be overloaded or modified if server didn't response to LIST command with Unix file info formats.
        Standardized Unix file info format: '-rw-r--r-- 1 owner group     21674012 May 13 21:52 hw1.pdf'
        '''
        try:
            file_info = file_info.split()
            file_info[8] = ' '.join(file_info[8:])  # in case file name contains spaces
            if file_info[0][0] == 'd':
                file_type = '   dir'
            elif len(file_info[8].split('.')) > 1:
                file_type = '   ' + file_info[8].split('.')[-1]  # Use filename's suffix as file type
            else:
                file_type = 'none'  # unknown file type
        
            if file_type == '   dir':
                size = ''
            else:
                size = self.calculate_size(int(file_info[4]))
            time = "%s %s %s" % (file_info[5], file_info[6], file_info[7])
            name = file_info[-1]
            return "{} {} {} {}".format(file_type.ljust(17), size.ljust(17, ' '), time.ljust(24), name)
        except:  # when file info is not in Unix file format
            # Cannot retrieve information about server directory
            tk.messagebox.showwarning("Warning","Failed to parse file information.")
            sleep(2)  
            os._exit(0)  # Exit
            return file_info
    
    def calculate_size(self, size):
        if size < 1024:
            return str(size) + ' B'
        elif size < 1024 * 1024:
            return str(size // 1024) + ' KB'
        elif size < 1024 * 1024 * 1024:
            return str(size // 1024 // 1024) + ' MB'
        else:
            return str(size // 1024 // 1024 // 1024) + ' GB'
    
    def connect(self):
        # Get and check server ip
        ip = self.ip_entry_.get()
        pattern = re.compile(r'^((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}$', re.ASCII)
        match = pattern.search(ip)  # Use regular expression to check given ip address
        if not match:
            self.ip_entry_.delete(0, 'end')  # Clear server ip
            tk.messagebox.showwarning("Warning","Wrong IP address!")  
            return
        
        # Get and check server port
        port = self.port_entry_.get()
        try:
            port = int(port)
        except:
            self.port_entry_.delete(0, 'end')  # Clear server port
            self.port_entry_.insert(0, '21')  # Default server port: 21
            tk.messagebox.showwarning("Warning","Wrong port number!") 
            return
        
        # Get a username and a password
        user = tk.simpledialog.askstring(title = 'Username ', prompt = 'Enter your username:')
        if user == '':
            user = "anonymous"
        elif user == None:
            return
        pass_word = tk.simpledialog.askstring(title = 'Password ', prompt = 'Enter your password:')
        if pass_word == None:
            return
        
        self.top_.configure(cursor = 'watch')
        try:
            self.print_("Connecting ...")
            self.cmd_line_win_.update()
            self.login(ip, port, pass_word, user)
        except Exception as err:
            self.print_("Error: " + str(err))
            tk.messagebox.showerror("errorWindow", err)
            return
        finally:
            self.top_.configure(cursor = 'arrow')
        
        self.connect_button_.configure(text = 'Disconnect', command = self.disconnect)
        self.directory_level = 0  # Indicate that server's working directory is its root directory
        
        # Activate all buttons except back button, for server's working directory is its root directory
        self.active_state()
        self.back_button_['state'] = tk.DISABLED
        
        # Generate server directory window
        self.update_server_dir_win()
        self.print_('Connected to server %s successfully.' % ip)
        
    def disconnect(self):
        try:
            self.logout()
        except Exception as err:
            self.print_("Error: " + str(err))
            tk.messagebox.showerror("errorWindow", err)
            
        self.print_('Disconnected.')
        self.connect_button_.configure(text = 'Connect', command = self.connect)
        self.server_dir_win_.delete(0, 'end')  # Clear server directory window
        self.server_file_entry_.delete(0, 'end')  # Clear server file entry
        self.local_file_entry_.delete(0, 'end')  # Clear local file entry
        
        # Disable all buttons except connect button
        self.back_button_['state'] = tk.DISABLED
        self.mkd_button_['state'] = tk.DISABLED
        self.rmd_button_['state'] = tk.DISABLED
        self.rename_button_['state'] = tk.DISABLED
        self.download_button_['state'] = tk.DISABLED
        self.upload_button_['state'] = tk.DISABLED
        self.reset_button_['state'] = tk.DISABLED
        self.open_button_['state'] = tk.DISABLED
        self.mode_button_['state'] = tk.DISABLED
        
    def click_back(self):
        '''When clicking back button, go back to parent directory.'''
        try:
            self.cwd('..')  # Change working directory to its parent directory
        except Exception as err:
            self.print_("Error: " + str(err))
            tk.messagebox.showerror("errorWindow", err)
            return
        self.directory_level -= 1
        if self.directory_level == 0:  # when back to root directory
            self.back_button_['state'] = tk.DISABLED  # Disable back_button
        self.update_server_dir_win()
        self.print_('Return to parent directory.')
    
    def click_mkd(self):
        '''When clicking back button, make a new directory.'''
        dir_name = tk.simpledialog.askstring(title = 'Create New Directory', prompt ='Enter a directory name:',initialvalue = 'new_directory')
        if dir_name == None: 
            return
        try:
            rps = self.mkd(dir_name)
        except Exception as err:
            self.print_("Error: " + str(err))
            tk.messagebox.showerror("errorWindow", err)
            return
        if not rps.startswith('257'):
            tk.messagebox.showerror("errorWindow", rps[4:])
            return
        self.update_server_dir_win()
        self.print_('Created new directory ./%s successfully.' % dir_name)
        
    def click_rmd(self):
        '''When clicking back button, remove chosen directory.'''
        try:
            index = int(self.server_dir_win_.curselection()[0])  # Get select file's index
        except:
            tk.messagebox.showwarning("Warning","Please first select a file.") 
            return
        dir_info = self.server_dir_win_.get(index).split()
        if dir_info[0] == 'dir':  # when a sub-directory is chosen
            dir_name = ' '.join(dir_info[4:])  # in case directory name contains spaces
            try:
                if not self.rmd(dir_name):  # Remove chosen sub-directory
                    tk.messagebox.showwarning("Warning","Directory not empty.") 
                    return
            except Exception as err:
                self.print_("Error: " + str(err))
                tk.messagebox.showerror("errorWindow", err)
                return
            self.update_server_dir_win()
            self.print_('Removed directory ./%s successfully.' % dir_name)
            return
        else:
            tk.messagebox.showwarning("Warning","Cannot delete a file.") 
        
    def click_rename(self):
        '''When clicking back button, rename chosen directory.'''
        try:
            index = int(self.server_dir_win_.curselection()[0])  # Get select file's index
        except:
            tk.messagebox.showwarning("Warning","Please first select a file.") 
            return
        path_info = self.server_dir_win_.get(index).split()
        if path_info[0] == 'dir':        
            path = ' '.join(path_info[4:])  # in case directory name contains spaces
            path_type = 'Directory'
        else:
            path = ' '.join(path_info[6:])  # in case file name contains spaces
            path_type = 'File'
        new_path = tk.simpledialog.askstring(title = 'Remove ' + path_type, prompt = 'Enter a new name:')
        if new_path == None:
            return
        try:
            rps = self.rename(path, new_path)
            if not rps.startswith('250'):  
                tk.messagebox.showerror("errorWindow", rps[4:])
                return
        except Exception as err:
            self.print_("Error: " + str(err))
            tk.messagebox.showerror("errorWindow", err)
            return
        self.update_server_dir_win()
        self.print_('Renamed ./%s to ./%s successfully.' % (path, new_path))
        
    def click_file(self, event):
        '''When double clicking a sub-directory in server directory window,
        enter this sub-directory and 5change server's working directory;
        when double clicking a file in server directory window, enter it onto server file entry.
        '''
        w = event.widget
        index = int(w.curselection()[0])
        path_info = w.get(index).split()
        if path_info[0] != 'dir':  # when double clicking a file rather than a sub-directory
            filename = ' '.join(path_info[6:])  # in case file name contains spaces
            self.server_file_entry_.delete(0, 'end')  # Clear server file entry
            self.server_file_entry_.insert(0, filename)  # Enter chosen file
        else:  # when double clicking a sub-directory rather than a file
            dir_name = ' '.join(path_info[4:])  # in case directory name contains spaces
            self.cwd(dir_name)  # Change working directory to clicked sub-directory
            self.directory_level += 1
            self.back_button_['state'] = tk.ACTIVE  # Set back button active
            self.update_server_dir_win()
            self.print_('Enter ./%s.' % dir_name)
    
    def download(self):
        '''Download chosen file from server.'''
        target_file = self.server_file_entry_.get()
        if not target_file:
            tk.messagebox.showwarning("Warning","Please first select a file.") 
            return
        try:
            self.file_size = self.get_file_size(target_file)
        except Exception as err:
            self.print_("Error: " + str(err))
            tk.messagebox.showerror("errorWindow", err)
        if self.file_size == -1:
            self.server_file_entry_.delete(0, 'end')  # Clear server file entry
            tk.messagebox.showwarning("Warning","Target file not exist.") 
            return
        path = askdirectory(title = 'Choose a directory')
        if not path:
            return
        localpath = path + '/' + target_file.split('/')[-1]  # concatenate local file path
        self.print_to_task_win('Downloading ' + target_file)
        self.print_to_task_win('To ' + localpath)
        self.print_to_task_win('Total Size: ' + self.calculate_size(self.file_size))
        self.task_win_.itemconfigure('end', fg = 'blue')
        self.print_to_task_win('')
        self.top_.configure(cursor = 'watch')
        self.blocked_state()
        try:
            if self.download_file(target_file, localpath, self.print_progress):
                self.print_('Download ./%s successfully.' % target_file)
            else:
                self.print_("Failed to download.")
        except Exception as err:
            self.print_("Error: " + str(err))
            tk.messagebox.showerror("errorWindow", err)
        finally:
            self.active_state()
            self.top_.configure(cursor = 'arrow')
            self.server_file_entry_.delete(0, 'end')  # Clear server file entry
            self.task_win_.delete(0, 'end')  # Clear task window
        
    def reset_server_file(self):
        self.server_file_entry_.delete(0, 'end')  # Clear server file entry
        
    def upload(self):
        '''Upload chosen file to server.'''
        filepath = self.local_file_entry_.get()
        if not filepath:
            tk.messagebox.showwarning("Warning","Please first select a file.") 
            return
        if not os.path.exists(filepath):
            self.local_file_entry_.delete(0, 'end')  # Clear local file entry
            tk.messagebox.showwarning("Warning","File not exist.") 
            return
        self.file_size = os.path.getsize(filepath)
        self.print_to_task_win('Uploading ' + filepath)
        self.print_to_task_win('Total Size: ' + self.calculate_size(self.file_size))
        self.task_win_.itemconfigure('end', fg = 'blue')
        self.print_to_task_win('')
        self.top_.configure(cursor = 'watch')
        self.blocked_state()
        try:
            if  self.upload_file(filepath, self.print_progress):
                self.update_server_dir_win()
                self.print_('Upload %s successfully.' % filepath)
            else:
                self.print_("Failed to upload.")
        except Exception as err:
            self.print_("Error: " + str(err))
            tk.messagebox.showerror("errorWindow", err)
        finally:
            self.active_state()
            self.top_.configure(cursor = 'arrow')
            self.local_file_entry_.delete(0, 'end')  # Clear local file entry
            self.task_win_.delete(0, 'end')  # Clear task window
        
    def choose_local_file(self):
        '''Choose a local file and enter its path onto local file entry.'''
        filepath = askopenfilename(title = 'Choose a local file')
        self.local_file_entry_.delete(0, 'end')  # Clear local file entry
        self.local_file_entry_.insert(0, filepath)  # Enter chosen file
        
    def print_progress(self, size):
        '''Print transfer process to task window.'''
        progress = 100 * size / self.file_size  # Calculate transfer process
        self.task_win_.delete('end', 'end')  # Delete task window's last line, which displays an old progress
        self.task_win_.insert('end', "Having transferred {:.4}%".format(progress))  # And display new progress
        self.task_win_.itemconfigure('end', fg = 'green')
        self.task_win_.update()
    
    def change_pasv(self):
        self.set_port_mode()
        self.mode_button_.configure(text = 'PORT', command = self.change_port)
        self.print_('Changed to PORT mode.')
        
    def change_port(self):
        self.set_pasv_mode()
        self.mode_button_.configure(text = 'PASV', command = self.change_pasv)
        self.print_('Changed to PASV mode.')
    
    def blocked_state(self):
        '''When transferring file, block those buttons which may affect file transfer'''
        self.connect_button_['state'] = tk.DISABLED
        self.back_button_['state'] = tk.DISABLED
        self.mkd_button_['state'] = tk.DISABLED
        self.rmd_button_['state'] = tk.DISABLED
        self.rename_button_['state'] = tk.DISABLED
        self.download_button_['state'] = tk.DISABLED
        self.upload_button_['state'] = tk.DISABLED
        self.mode_button_['state'] = tk.DISABLED
        
    def active_state(self):
        '''Activate all buttons'''
        self.connect_button_['state'] = tk.ACTIVE
        self.back_button_['state'] = tk.ACTIVE
        self.mkd_button_['state'] = tk.ACTIVE
        self.rmd_button_['state'] = tk.ACTIVE
        self.rename_button_['state'] = tk.ACTIVE
        self.download_button_['state'] = tk.ACTIVE
        self.upload_button_['state'] = tk.ACTIVE
        self.reset_button_['state'] = tk.ACTIVE
        self.open_button_['state'] = tk.ACTIVE
        self.mode_button_['state'] = tk.ACTIVE
    
    def refresh(self):
        self.top_.after(100, self.refresh)    
    
    def run(self):
        self.top_.mainloop()





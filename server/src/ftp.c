#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include "ftp.h"

int receive(State *state, char *cmd) {
    int len;
    if((len = read(state->connfd, state->cmd, BUFLEN - 1)) > 0) {
		state->cmd[len] = '\0';
		printf("%d Command from user: %s\r\n", state->pid, state->cmd);
		sscanf(state->cmd, "%s", cmd);
        return 0;
	}
    else
        return 1;
}

int response(State *state) {
    if (write(state->connfd, state->rps, strlen(state->rps)) == -1) {
        printf("Error write(): %s(%d)\r\n", strerror(errno), errno);
		return 1;
    }
    printf("%d    Response: %s", state->pid, state->rps);
    return 0;
}

int ftp_user(State *state) {
    if (sscanf(state->cmd + 4, "%s", state->username) != 1) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    if (0 == strcmp(state->username, "anonymous")) {
        sprintf(state->rps, "331 Guest logged in. Send your complete e-mail address as password.\r\n");
        response(state);
        return 0;
    }
    else {
        sprintf(state->rps, "530 Login failed. Unacceptable user.\r\n");
        response(state);
        return 1;
    }
}

int ftp_pass(State *state) {
    if (sscanf(state->cmd + 4, "%s", state->password) != 1) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    sprintf(state->rps, "230 Welcome to FanTastic FTP.\r\n");
    response(state);
    return 0;
}

int ftp_rest(State *state) {
    if (sscanf(state->cmd + 4, "%d", &state->start_point) != 1) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    sprintf(state->rps, "350 Restarting at %d. Send STOR or RETR to initiate transfer.\r\n", state->start_point);
    response(state);
    return 0;
}

int ftp_retr(State *state) {
    char path[2 * BUFLEN], file_path[BUFLEN];
    if (sscanf(state->cmd + 4, "%s", file_path) != 1) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    sprintf(path, "%s/%s", state->working_dir, file_path);  // Concatenate working directory path and given path
    if (access(path, R_OK) != 0) {
        sprintf(state->rps, "550 File %s doesn't exist or permission denied.\r\n", path);
        response(state);
        return 1;
    }
    
    if (build_data_connection(state, path) != 0) {
       return 1;
    }

    // file transfer
    FILE *fp;
    int len;
    char buffer[BUFLEN];
    if((fp = fopen(path, "rb")) != NULL){
        fseek(fp, 0L, SEEK_END);
        int size = ftell(fp);  // Get file size
        if (fseek(fp, state->start_point, SEEK_SET) != 0)  // Start file transfer from the start point
            fseek(fp, 0L, SEEK_SET);  // If start point is out of range, start file transfer from beginning
        printf("%d Transferring the %d-byte file ...\r\n", state->pid, size);
        while (!feof(fp)) {
            len = fread(buffer, 1, sizeof(buffer), fp);
            write(state->data_connfd, buffer, len);
        }
        fclose(fp);
        sprintf(state->rps, "226 Transfer complete.\r\n");
        response(state);
    }
    else {
        sprintf(state->rps, "551 Can't read file %s.\r\n", path);
        response(state);
        printf("%d Cannot open file.\n", state->pid);
    }
    state->start_point = 0;

    // Close data connection and reset mode
    close(state->data_connfd);
    if (state->mode == PASV) 
        close(state->data_listenfd);
    state->mode = UNSET;
    return 0;
}
 
int ftp_stor(State *state) {
    char path[2 * BUFLEN], file_path[BUFLEN];
    if (sscanf(state->cmd + 4, "%s", file_path) != 1) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    sprintf(path, "%s/%s", state->working_dir, file_path);  // Concatenate working directory path and given path
    if (build_data_connection(state, path) != 0) {
       return 1;
    }

    FILE *fp;
    int len, received_size = 0;
    char buffer[BUFLEN];
    if((fp = fopen(path, "wb")) != NULL) {
        printf("%d Receiving file %s\r\n", state->pid, path);
        if (fseek(fp, state->start_point, SEEK_SET) != 0)  // Start file transfer from the start point
            fseek(fp, 0L, SEEK_SET);  // If start point is out of range, start file transfer from beginning
        while ((len = read(state->data_connfd, buffer, BUFLEN - 1)) > 0) {
            buffer[len] = '\0';
            fwrite(buffer, 1, len, fp);
            received_size += len;
            printf("%d Having received %d bytes\n", state->pid, received_size );
        }
        fclose(fp);
        sprintf(state->rps, "226 Transfer complete.\r\n");
        response(state);
    }
    else {
        sprintf(state->rps, "551 Can't read file %s.\r\n", path);
        response(state);
        printf("%d Cannot open file.\n", state->pid);
    }
    state->start_point = 0;

    // Close data connection and reset mode
    close(state->data_connfd);
    if (state->mode == PASV) 
        close(state->data_listenfd);
    state->mode = UNSET;
    return 0;
}

int ftp_list(State *state) {
    char path[2 * BUFLEN], file_path[BUFLEN];
    if (sscanf(state->cmd + 4, "%s", file_path) > 0)
        sprintf(path, "%s/%s", state->working_dir, file_path);  // Concatenate working directory path and given path
    else
        strcpy(path, state->working_dir);  // default listed directory: working directory
    if (access(path, R_OK) != 0) {
        sprintf(state->rps, "550 Directory %s doesn't exist or permission denied.\r\n", path);
        response(state);
        return 1;
    }
    
    if (build_data_connection(state, path) != 0) {
       return 1;
    }

    // Get directory information using Shell command ls
    FILE *fp = NULL;
	char buffer[BUFLEN];
    char cmd[50] = "ls -l ";
    strcat(cmd, path); 
	fp = popen(cmd, "r");
	while (fgets(buffer, BUFLEN, fp) != NULL) {
        if (buffer[0] == '-' || buffer[0] == 'd')
            write(state->data_connfd, buffer, strlen(buffer));
	}
	pclose(fp);
    sprintf(state->rps, "250 Listing completed.\r\n");
    response(state);

    // Close data connection and reset mode
    close(state->data_connfd);
    if (state->mode == PASV) 
        close(state->data_listenfd);
    state->mode = UNSET;
    return 0;
}

int ftp_size(State *state) {
    char path[2 * BUFLEN], file_path[BUFLEN];
    if (sscanf(state->cmd + 4, "%s", file_path) != 1) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    sprintf(path, "%s/%s", state->working_dir, file_path);  // Concatenate working directory path and given path
    if (access(path, R_OK) != 0) {
        sprintf(state->rps, "550 File %s doesn't exist or permission denied.\r\n", path);
        response(state);
        return 1;
    }

	DIR *dirp;
    char buffer[3 * BUFLEN];
    int len;
	struct stat dir_stat;
	if (0 > stat(path, &dir_stat)) {
		printf("Error stat(): %s(%d)\n", strerror(errno), errno);
		return 1;
	}

	if (S_ISREG(dir_stat.st_mode)) {  // normal file
        sprintf(state->rps, "213 %ld\r\n", dir_stat.st_size);
        response(state);
        closedir(dirp);
        return 0;
	}  
    else {  // directory
        sprintf(state->rps, "550 File %s doesn't exist.\r\n", path);
        response(state);
        closedir(dirp);
        return 1;	
	}
}

int ftp_port(State *state) {
    if (state->mode == PASV) {
        close(state->data_listenfd);
        close(state->data_connfd);
    }  // Close old listening socket and data connection

    state->mode = PORT;
    int port[2];
    if (sscanf(state->cmd + 4, "%d,%d,%d,%d,%d,%d", &state->ip[0], &state->ip[1], &state->ip[2], &state->ip[3], &port[0], &port[1]) != 6) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    state->data_port = port[0] * 256 + port[1];  // Calculate and store client's port for data connection
    sprintf(state->rps, "200 PORT command successful.\r\n");
    response(state);
    return 0;
}

int ftp_pasv(State *state) {
    if (state->mode == PASV) {
        close(state->data_listenfd);
        close(state->data_connfd);
    }  // Close old listening socket and data connection

    state->mode = PASV;
    srand((unsigned)time(NULL));
    state->data_port = rand() % 45535 + 20000;  // generate a temporary random port number between 20000 and 65535
    int ip[4];
    get_ip_addr(state->connfd, ip);
    sprintf(state->rps, "227 Entering Passive Mode (%d,%d,%d,%d,%d,%d)\r\n", 
        ip[0], ip[1], ip[2], ip[3], state->data_port / 256, state->data_port % 256);
    response(state);

    // Build a data connection
    state->data_listenfd = create_socket(state->data_port);
	state->data_connfd = build_connection_pasv(state->data_listenfd);
    printf("%d Established a new data connection at port %d.\r\n", state->pid, state->data_port);
    return 0;
}

int ftp_syst(State *state) {
    sprintf(state->rps, "215 UNIX Type: L8\r\n");
    response(state);
    return 0;
}

int ftp_type(State *state) {
    char argv[5];
    argv[4] = '\0';
    if (sscanf(state->cmd + 4, "%s\n", argv) != 1) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    if (0 == strcmp(argv, "I")) {
        sprintf(state->rps, "200 Type set to I.\r\n");
        response(state);
        return 0;
    }
    else {
        sprintf(state->rps, "501 Unsupported type.\r\n");
        response(state);
        return 1;
    }
}

int ftp_quit(State *state) {
    sprintf(state->rps, "221-Thank you for using FanTastic FTP.\r\n221 Goodbye.\r\n");
    response(state);
    close(state->connfd);  // Child process closes connected socket
	printf("%d Connection closed with a client.\n", state->pid);
	exit(0);  // Child process exits
}

int ftp_cwd(State *state) {
    char path[2 * BUFLEN], file_path[BUFLEN];
    if (sscanf(state->cmd + 4, "%s", file_path) != 1) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    if (0 == strcmp(state->root, state->working_dir) && 0 == strcmp("..", file_path)) {
        sprintf(state->rps, "550 Permission denied.\r\n");
        response(state);
        return 1;
    }  // Not permitted to change working directory to root directory's parent directory
    if (0 == strcmp("..", file_path)) {
        for (int i = strlen(state->working_dir); i > 0; --i)
            if (state->working_dir[i] == '/') {
                state->working_dir[i] = '\0';
                strcpy(path, state->working_dir);
                break;
            }
    }
    else
        sprintf(path, "%s/%s", state->working_dir, file_path);  // Concatenate working directory path and given path
    if (access(path, R_OK) != 0) {
        sprintf(state->rps, "550 Directory %s doesn't exist or permission denied.\r\n", path);
        response(state);
        return 1;
    }
    strcpy(state->working_dir, path);
    sprintf(state->rps, "250 Working directory changed to %s\r\n", path);
    response(state);
    return 0;
}

int ftp_pwd(State *state) {
    sprintf(state->rps, "257 Working directory: %s\r\n", state->working_dir);
    response(state);
    return 0;
}

int ftp_mkd(State *state) {
    char path[2 * BUFLEN], file_path[BUFLEN];
    if (sscanf(state->cmd + 4, "%s", file_path) != 1) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    sprintf(path, "%s/%s", state->working_dir, file_path);  // Concatenate working directory path and given path
    if (mkdir(path, S_IRUSR | S_IWUSR | S_IXUSR | S_IRWXG | S_IRWXO) != 0) {
        sprintf(state->rps, "553 Cannot create new directory %s\r\n", path);
        response(state);
        return 1;
    }
    sprintf(state->rps, "257 Directory %s created.\r\n", path);
    response(state);
    return 0;
}

int ftp_rmd(State *state) {
    char path[2 * BUFLEN], file_path[BUFLEN];
    if (sscanf(state->cmd + 4, "%s", file_path) != 1) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    sprintf(path, "%s/%s", state->working_dir, file_path);  // Concatenate working directory path and given path
    if (access(path, R_OK) != 0) {
        sprintf(state->rps, "550 Directory %s doesn't exist or permission denied.\r\n", path);
        response(state);
        return 1;
    }

    if (remove_dir(path) == 0) {
        sprintf(state->rps, "250 Directory %s removed.\r\n", path);
        response(state);
        return 0;
    }
    else {
        sprintf(state->rps, "553 Cannot remove directory %s\r\n", path);
        response(state);
        return 1;
    }
}

int ftp_rnfr(State *state) {
    char path[2 * BUFLEN], file_path[BUFLEN];
    if (sscanf(state->cmd + 4, "%s", file_path) != 1) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    sprintf(path, "%s/%s", state->working_dir, file_path); // Concatenate working directory path and given path
    if (access(path, R_OK) != 0) {
        sprintf(state->rps, "550 Directory %s doesn't exist or permission denied.\r\n", path);
        response(state);
        return 1;
    }
    strcpy(state->pathname, path);
    sprintf(state->rps, "350 Ready to rename. Send a new pathname.\r\n");
    response(state);
    return 0;
}

int ftp_rnto(State *state) {
    char path[2 * BUFLEN], file_path[BUFLEN];
    if (sscanf(state->cmd + 4, "%s", file_path) != 1) {
        sprintf(state->rps, "501 Syntax error in parameters or arguments.\r\n");
        response(state);
        return 1;
    }
    sprintf(path, "%s/%s", state->working_dir, file_path); // Concatenate working directory path and given path
    if (rename(state->pathname, path) == 0) {
        sprintf(state->rps, "250 %s renamed to %s\r\n", state->pathname, path);
        response(state);
        return 0;
    }
    else {
        printf("Error rename(): %s(%d)\n", strerror(errno), errno);
        sprintf(state->rps, "553 Cannot rename %s\r\n", state->pathname);
        response(state);
        return 1;
    }
}

// Create a socket
// Bind it with an ip address and a given port
// Return the file descriptor
// Used by main(), ftp_port() and ftp_pasv()
int create_socket(int port) {
    int sockfd;  // file descriptor for listening socket
    struct sockaddr_in addr;
    int reuse = 1; 

    // Create a listening socket
    if ((sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) == -1) {
		printf("Error socket(): %s(%d)\n", strerror(errno), errno);
		return -1;
	}

    // set socket reusable
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0)
    {
        printf("Error setsockopt(): %s(%d)\n", strerror(errno), errno);
		return -1;
    }

    // Set the ip address and control port for the listening socket
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;  
    addr.sin_addr.s_addr = htonl(INADDR_ANY);	// default ip address: 0.0.0.0
    addr.sin_port = htons(port);
    if (bind(sockfd, (struct sockaddr *)&addr, sizeof(addr)) == -1) {
		printf("Error bind(): %s(%d)\n", strerror(errno), errno);
		return -1;
	}

    return sockfd;
}

// Connect a given socket to a given address (ip, port) 
// Used by ftp_retr() in PORT mode
int build_connection_port(int sockfd, int *ip, int port) {
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);	// default ip address: 0.0.0.0
	addr.sin_port = htons(port);
    char ip_addr[30];
    sprintf(ip_addr, "%d.%d.%d.%d", ip[0], ip[1], ip[2], ip[3]);
	if (inet_pton(AF_INET, ip_addr, &addr.sin_addr) <= 0) {		
		printf("Error inet_pton(): %s(%d)\n", strerror(errno), errno);
		return 1;
	}
    if (connect(sockfd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
		printf("Error connect(): %s(%d)\n", strerror(errno), errno);
		return 1;
	}
    return 0;
}

// Use a specific listening socket to create a connected socket
// Return the file descriptor
// Used by ftp_pasv() in PASV mode
int build_connection_pasv(int listenfd) {
    int connfd = 0;
    struct sockaddr_in cliaddr;
    socklen_t cliaddrlen = sizeof(cliaddr);
    
    if (listen(listenfd, 1) == -1) {
		printf("Error listen(): %s(%d)\n", strerror(errno), errno);
		return -1;
	}  // Listen for one connection
    
    if ((connfd = accept(listenfd, (struct sockaddr *) &cliaddr, &cliaddrlen)) == -1) {
		printf("Error accept(): %s(%d)\n", strerror(errno), errno);
	    return -1;
	}  // Establish a connected socket
    return connfd;
}

// Build a data connection depending on mode
// Used by ftp_retr and ftp_stor()
int build_data_connection(State *state, char *path) {
    if (state->mode == PORT) {  // if in PORT mode
        sprintf(state->rps, "150 Opening BINARY mode data connection for %s\r\n", path);
        response(state);
        state->data_connfd = create_socket(DATA_PORT);
	    if ((build_connection_port(state->data_connfd, state->ip, state->data_port)) == 0) 
            printf("%d Established a new data connection at port %d.\r\n", state->pid, DATA_PORT);
    }  
    else if (state->mode == PASV) {
        sprintf(state->rps, "150 Opening BINARY mode data connection for %s.\r\n", path);
        response(state);
        // Data connection has been established in the last PASV command
        // So do nothing more to build a data connection
    }
    else if (state->mode == UNSET) {  // else if mode is unset
        sprintf(state->rps, "425 Can't open data connection. Need a PORT or PASV command.\r\n");
        response(state);
        return 1;
    }
    return 0;
}

// Get socket's local ip address
// Used by ftp_pasv() 
int get_ip_addr(int fp, int *ip) {
    socklen_t addr_size = sizeof(struct sockaddr_in);
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    char *ip_addr, *part;
    getsockname(fp, (struct sockaddr *)&addr, &addr_size);
    ip_addr = inet_ntoa(addr.sin_addr);
    part = strtok(ip_addr, ".");
    for (int i = 0; i < 4; ++i) {
        ip[i] = atoi(part);
        part = strtok(NULL, ".");
    }
    return 0;
}

// Empty and remove a given directory
// Used by ftp_rmd()
int remove_dir(char *path) {
    char pwd[] = ".";
	char ppwd[] = "..";
	char dir_name[BUFLEN];
	DIR *dirp;
	struct dirent *dp;
	struct stat dir_stat;

	if (0 > stat(path, &dir_stat)) {
		printf("Error stat(): %s(%d)\n", strerror(errno), errno);
		return 1;
	}

	if (S_ISREG(dir_stat.st_mode)) { 
		remove(path);
	}  // remove normal file
    else if (S_ISDIR(dir_stat.st_mode)) {  // sub-directory
		dirp = opendir(path);
		while ((dp = readdir(dirp)) != NULL) {
			if ((0 == strcmp(pwd, dp->d_name)) || (0 == strcmp(ppwd, dp->d_name))) {
				continue;
			}  // ignore path "." and ".."
            sprintf(dir_name, "%s/%s", path, dp->d_name);
			remove_dir(dir_name);   // recursively empty the directory
		}
		closedir(dirp);
		rmdir(path);  // remove the empty directory
	}
	return 0;
}
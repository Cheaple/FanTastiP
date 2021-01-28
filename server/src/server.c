#include "ftp.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <wait.h>

int main(int argc, char **argv) {
    int listenfd;  // file descriptor for control connection's listening socket
	int len;
	char cmd[5];
	State *state = (State *)malloc(sizeof(State));
	memset(state, 0, sizeof(State));
	state->if_logged_in = -1;
	state->mode = UNSET;  // default mode: unset
	state->port = CTR_PORT;  // default control port: 21
	state->start_point = 0;
	strcpy(state->working_dir, "/tmp");  // default working directory
	strcpy(state->root, "/tmp");  // default working directory
	
	state->pid = getpid();
	if (argc == 3) {
		if (0 == strcmp(argv[1], "-port"))
			state->port = atoi(argv[2]);
		else if (0 == strcmp(argv[1], "-root")) {
			strcpy(state->working_dir, argv[2]);
			strcpy(state->root, argv[2]);
		}
		else {
			printf("Error: invalid option \"%s\"\r\n", argv[2]);
			exit(0);
		}
	}
	else if (argc == 5) {
		if (0 == strcmp(argv[1], "-port"))
			state->port = atoi(argv[2]);
		else if (0 == strcmp(argv[1], "-root")) {
			strcpy(state->working_dir, argv[2]);
			strcpy(state->root, argv[2]);
		}
		else {
			printf("Error: invalid option \"%s\"\r\n", argv[1]);
			exit(0);
		}
		if (0 == strcmp(argv[3], "-port"))
			state->port = atoi(argv[4]);
		else if (0 == strcmp(argv[3], "-root")) {
			strcpy(state->working_dir, argv[4]);
			strcpy(state->root, argv[4]);
		}
		else {
			printf("Error: invalid option \"%s\"\r\n", argv[3]);
			exit(0);
		}
	}
	else if (argc != 1) {
		printf("Error: invalid option \"%s\"\r\n", argv[1]);
		exit(0);
	}

    listenfd = create_socket(state->port);

    // Listen for connections, at most 10 connections
	if (listen(listenfd, 10) == -1) {
		printf("Error listen(): %s(%d)\n", strerror(errno), errno);
		return 1;
	}

    while (1) {
        // Establish a connected socket
        if ((state->connfd = accept(listenfd, NULL, NULL)) == -1) {
			printf("Error accept(): %s(%d)\n", strerror(errno), errno);
			continue;
		}
		printf("%d Connected with a new client.\r\n", state->pid);

		sprintf(state->rps, "220 FanTastic FTP server ready.\r\n");
		response(state);

		if (fork() == 0) {  // child process 
			close(listenfd);  // Close listening socket
			state->pid = getpid();
			// Read a command
			while (1) {	
				if(receive(state, cmd) == 0) {
					if (0 == strcmp(cmd, "USER"))
						ftp_user(state);
					else if (0 == strcmp(cmd, "PASS"))
						ftp_pass(state);
					else if (0 == strcmp(cmd, "PASV"))
						ftp_pasv(state);
					else if (0 == strcmp(cmd, "PORT"))
						ftp_port(state);
					else if (0 == strcmp(cmd, "REST"))
						ftp_rest(state);
					else if (0 == strcmp(cmd, "RETR"))
						ftp_retr(state);
					else if (0 == strcmp(cmd, "STOR"))
						ftp_stor(state);
					else if (0 == strcmp(cmd, "SYST")) 
						ftp_syst(state);
					else if (0 == strcmp(cmd, "TYPE")) 
						ftp_type(state);
					else if (0 == strcmp(cmd, "QUIT") || 0 == strcmp(cmd, "ABOR"))
						ftp_quit(state);
					else if (0 == strcmp(cmd, "CWD"))
						ftp_cwd(state);
					else if (0 == strcmp(cmd, "PWD"))
						ftp_pwd(state);
					else if (0 == strcmp(cmd, "MKD"))
						ftp_mkd(state);
					else if (0 == strcmp(cmd, "RMD"))
						ftp_rmd(state);
					else if (0 == strcmp(cmd, "LIST"))
						ftp_list(state);
					else if (0 == strcmp(cmd, "SIZE"))
						ftp_size(state);
					else if (0 == strcmp(cmd, "RNFR"))
						ftp_rnfr(state);
					else if (0 == strcmp(cmd, "RNTO"))
						ftp_rnto(state);
					else {
						sprintf(state->rps, "502 Command not implemented.\r\n");
        				response(state);
					}
				}
			}
		}
		close(state->connfd);  // Parent process closes connected socket
	}
    close(listenfd);  // Parent process closes listening socket
}
#pragma once
#include <sys/types.h>

#define BUFLEN 1024
#define CTR_PORT 21  // port for control connection
#define DATA_PORT 20  // port for data connection in PORT mode

typedef enum Mode {PORT, PASV, UNSET} Mode;

typedef struct State {
    pid_t pid;
    int connfd;  // file descriptor for control connection's connected socket
    int data_listenfd;  // file descriptor for data connection's listening socket in PORT mode
    int data_connfd;  // file descriptor for data connection's connected socket
    char cmd[BUFLEN];  // command message received by server
    char rps[BUFLEN];  // response message sent to client
    int if_logged_in;
    Mode mode;
    char username[BUFLEN];
    char password[BUFLEN];
    char working_dir[BUFLEN];
    char root[BUFLEN];
    int start_point;  // to store a start point passed by a REST command
    char pathname[BUFLEN];  // to store a pathname upon receiving a RNFR command
    int port;  // control port
    int data_port;  // in PASV mode, server's port for data connection; in PORT mode, client's port for data connection
    int ip[4];  // to store client's ip address in PORT mode
} State;

int receive(State *, char *);
int response(State *);

int ftp_user(State *);
int ftp_pass(State *);
int ftp_port(State *);
int ftp_pasv(State *);
int ftp_rest(State *);
int ftp_retr(State *);
int ftp_stor(State *);
int ftp_syst(State *);
int ftp_type(State *);
int ftp_quit(State *);
int ftp_cwd(State *);
int ftp_pwd(State *);
int ftp_mkd(State *);
int ftp_rmd(State *);
int ftp_list(State *);
int ftp_size(State *);
int ftp_rnfr(State *);
int ftp_rnto(State *);

int create_socket(int);
int build_connection_port(int, int *, int);
int build_connection_pasv(int);
int build_data_connection(State *, char *);
int get_ip_addr(int, int *);
int remove_dir(char *);
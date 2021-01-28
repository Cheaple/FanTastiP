server: ftp.o server.o ftp.h
	gcc ftp.o server.o -g -o server
ftp.o: ftp.c ftp.h
	gcc -c ftp.c -g -o ftp.o
server.o: server.c ftp.h
	gcc -c server.c -g -o server.o
clean :
	rm server server.o ftp.o 

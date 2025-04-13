CC ?= gcc
CFLAGS=-Wall -mconsole
OBJS = main.o motor.o

formbot: $(OBJS)
	$(CC) $(CFLAGS) -o formbot $(OBJS)

%.o: %.c
	$(CC) $(CFLAGS) -c $<

clean:
	rm -f *.o formbot

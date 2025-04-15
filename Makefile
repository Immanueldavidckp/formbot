CXX = g++
CXXFLAGS = `pkg-config --cflags --libs opencv4`

SRC = main.cpp camera.cpp gps.cpp moto.cpp radar.cpp servo.cpp ultrasonic.cpp
OUT = farmbot

all:
	$(CXX) $(SRC) $(CXXFLAGS) -o $(OUT)

run:
	./farmbot
clean:
	rm  farmbot

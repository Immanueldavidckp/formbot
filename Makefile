CXX = g++
CXXFLAGS = `pkg-config --cflags --libs opencv4`

SRC = main.cpp  gps.cpp motor.cpp radar.cpp ultrasonic.cpp
OUT = farmbot

all:
	$(CXX) $(SRC) $(CXXFLAGS) -o $(OUT)

run:
	sudo ./farmbot
clean:
	rm  farmbot

git:
	git status
	git add .
	git commit -m "new change"
	git push origin main

pull:
	git pull origin main

	
CC := g++

C_SRCS += \
../src/relay.c \
../src/configInterface.c \
../src/main.c 

OBJS += \
./src/relay.o \
./src/configInterface.o \
./src/main.o 

C_DEPS += \
./src/relay.d \
./src/configInterface.d \
./src/main.d 

src/%.o: src/%.cpp
	@echo 'Building file: $<'
	@echo 'Invoking: GCC C++ Compiler'
	$(CC) -std=c++14 -D__FILENAME__="$(subst src/,,$<)" $(LIBS) -Wall -c -fmessage-length=0 -fPIC -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '

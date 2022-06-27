# Set up gRPC-device as startup
 This startup script will configure the gRPC-device executable to run as soon as the Linux-RT target starts up. In order to install the script and run it as startup do the following:
 
# Download the startup script
 1. Download grpcStartup.sh, or clone the repo
 2. Copy grpcStartup.sh to /home/lvuser/natinst/bin - this location is available at startup
 3. Use chmod +x to give permissions to execute to grpcStartup.sh
 4. Test the script by executing it, you can use "./grpcStartup.sh start" and "./grpcStartup stop" to start and stop the grpc service
 
# Install the startup script to run on boot
1. Copy the startup script to /etc/init.d (cp grpcStartup.sh /etc/init.d) - This folder contains startup scripts to run
2. Add it to the list of startup executables with "/usr/sbin/update-rc.d -f grpcStartup.sh defaults"  
3. Reboot the Linux-RT server and test that the gRPC server is running on startup
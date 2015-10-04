import pyaudio, sys, socket, wave

port = 3003
ip = "192.168.2.218"

chunk = 16
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

p = pyaudio.PyAudio()
stream = p.open(format = FORMAT, channels = CHANNELS, rate = RATE, input = True,output = True, frames_per_buffer = chunk)

#Create a socket connection for connecting to the server:
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip, port))
print "connected to socket"

wo = wave.open("monica2.wav",'wb')
wo.setnchannels(2)
wo.setsampwidth(2)
wo.setframerate(48000)





while True:
    print "Connection from ",  socket.gethostbyname(socket.gethostname())
    while 1:
        data = client_socket.recv(64)
        wo.writeframes(data)
        print "WROTE STUFF"
        print "RECIEVED:" , data

wo.close()
client_socket.close()
#while True:


   #Recieve data from the server:
 #  print "AM I WORKING"
  # data = client_socket.recv(512)
   #print "WHERE DO I STOP"
   #stream.write(data,chunk)
   #wo.writeframes(data)
   #print "wrote stuff"
   
#print "complete"
#wo.close()
#socket.close()
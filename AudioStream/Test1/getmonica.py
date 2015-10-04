import  sys, socket, wave

port = 3443
ip = "192.168.2.204"


#Create a socket connection for connecting to the server:
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip, port))
print ("connected to socket")

wo = wave.open("monica2.wav",'wb')
audioParams = (1,2,8000,0,'NONE','not compressed')
wo.setparams(audioParams)




while True:
  print ("Connection from ",  socket.gethostbyname(socket.gethostname()))
  while 1:
      data = client_socket.recv(1024)
      if data:
        wo.writeframes(data)
        print ("WROTE STUFF")
        print ("RECIEVED:", data)
      else:
        break
wo.close()
client_socket.close()
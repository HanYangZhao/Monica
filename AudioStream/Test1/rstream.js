var settings = {
  ip: "192.168.2.204",
  port: 3443
};


var fs = require("fs");

var rstream = fs.createReadStream('monica.wav');
var Writable = require('stream').Writable
var ws = Writable();

var readHeader = function() {
  var b = new Buffer(1024);
  b.read('RIFF', 0);
  /* file length */
  b.readUInt32LE(32 + samplesLength * 2, 4);
  //b.writeUint32LE(0, 4);

  b.read('WAVE', 8);
  /* format chunk identifier */
  b.read('fmt ', 12);

  /* format chunk length */
  b.readUInt32LE(16, 16);

  /* sample format (raw) */
  b.readUInt16LE(1, 20);

  /* channel count */
  b.readUInt16LE(1, 22);

  /* sample rate */
  b.readUInt32LE(sampleRate, 24);

  /* byte rate (sample rate * block align) */
  b.readUInt32LE(sampleRate * 2, 28);

  /* block align (channel count * bytes per sample) */
  b.readUInt16LE(2, 32);

  /* bits per sample */
  b.readUInt16LE(16, 34);

  /* data chunk identifier */
  b.read('data', 36);

  /* data chunk length */
  //b.writeUInt32LE(40, samplesLength * 2);
  b.readUInt32LE(0, 40);


  rstream.read(b.slice(0, 50));
};



readHeader(rstream);



var net = require('net');
console.log("connecting...");
client = net.connect(settings.port, settings.ip, function () {
  client.setNoDelay(true);

    client.on("data", function (data) {
        try {
      console.log("SENDING DATA");
      var readable = rstream.read(data);
      readable.pipe(ws)
      ws.write(data);
      console.log("sent chunk of " + data.toString('hex'));
    }
        catch (ex) {
            console.error("Er!" + ex);
        }
    });
});



setTimeout(function() {
  console.log('sending for 30 seconds');
  client.end();
  outStream.end();
  process.exit(0);
}, 30 * 1000);

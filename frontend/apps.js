//sudo apt-get install -y nodejs
//sudo apt-get install -y npm
// sudo npm -g install hotnode

var server = require('http').createServer(handler);
var io = require('socket.io')(server);
var url = require('url');
var fs = require('fs');

// server
var tgserv = require('./lib/tgserver');


function handler(request,response){ 
	if(request.url.indexOf('.css') != -1){
		fs.readFile(__dirname + '/public/'+request.url, function (err, data) {
        if (err) console.log(err);
        response.writeHead(200, {'Content-Type': 'text/css'});
        response.write(data);
        response.end();
      	});

	}else if(request.url.indexOf('.js') != -1){
		//console.log("Trying to load js: "+request.url);
		fs.readFile(__dirname + '/public/'+request.url, function (err, data) {
        if (err) console.log(err);
        response.writeHead(200, {'Content-Type': 'text/js'});
        response.write(data);
        response.end();
      	});

	}
	else{

	switch(true){
		case request.url === "/":
			// need to serve my index.html here
			fs.readFile("./public/home.html", function(err, data){
				if(err){send404(request,response);}
				response.writeHead(200,{'content-type': 'text/html'});
				response.write(data,'utf8');
				response.end();
			}); 
 

		break;
		default:
		//console.log("error!");
		send404(request, response);
	}
	//console.log("test");
 }
 
} 

server.listen(8080); //process.env.PORT || 5000);

send404 = function(request, response){
			response.writeHead(404);
			response.write("Error 404. Could not find page "+request.url+"\n");
			response.end();
}

io.on('connection', function (socket) {
  console.log("connection established:"+socket.id);
  socket.emit('talk', { id: socket.id });

  socket.on('check_if_connector_is_installed', function(data){
	var connector_res = tgserv.check_local_connector();
	if (connector_res['isOK'] === false) {
		socket.emit('connector_already_present', {});
	}
  })
  socket.on('check_url_and_token', function(data){
		console.log(data)

		var url_res = tgserv.check_url(data["url"]);
		console.log(url_res)
		if (url_res['isOK'] === false) {
			socket.emit('url_error', {});
		}

		var token_res = tgserv.check_token(data["token"]);
		if (token_res['isOK'] === false) {
			socket.emit('token_error', {});
		}
		if (token_res['isOK'] === true && url_res['isOK'] === true ) {
			socket.emit('url_token_ok', {});
		}

		//socket.emit('conn_status', { "is_installed": is_installed});
	});

	socket.on('check_token', function(data){
		console.log(data)

		
		//
	});
});

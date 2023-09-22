//sudo apt-get install -y nodejs
//sudo apt-get install -y npm
// sudo npm -g install hotnode

var server = require('http').createServer(handler);
//var io = require('socket.io')(server);
const { Server } = require("socket.io");
const io = new Server(server);
var url = require('url');
var fs = require('fs');
var tenantconf = require('./tenantconf.json');

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


send404 = function(request, response){
			response.writeHead(404);
			response.write("Error 404. Could not find page "+request.url+"\n");
			response.end();
}

io.on('connection', function (socket) {

  socket.on('get_default_tenant', function(data){
	var resp = {}
	if (tenantconf.hasOwnProperty("tenant")) {
		if (tenantconf['tenant'] == ""){
			resp = {"found":false,"tenant":""}
		}else{
			
			resp = {"found":true,"tenant":tenantconf['tenant']}
		}
	}else{
		resp = {"found":false,"tenant":""}
	}
	
	socket.emit('default_tenant', resp);
	});


  socket.on('check_if_connector_is_installed', function(data){
	var connector_res = tgserv.check_local_connector();
	if (connector_res['isOK'] === false) {
		socket.emit('connector_already_present', {});
	}
  });
  
  socket.on('check_url_and_token', function(data){
	console.log("got check url & token event")
	var url_res = tgserv.check_url(data["url"]);
	
	if (url_res['isOK'] === false) {
		socket.emit('url_error', {});
	}
	var thetenant = url_res['tenant']
	var token_res = tgserv.check_token(data["token"]);
	if (token_res['isOK'] === false) {
		socket.emit('token_error', {});
	}
	if (token_res['isOK'] === true && url_res['isOK'] === true ) {	
		socket.emit('url_token_ok', {tenant:thetenant});
	}
	});

	socket.on('store_info', function(data){
		console.log("got store info event")
		try{
			resp = tgserv.store_token_and_tenant(data,socket);
		}catch(err){
			console.log("error on storing info: "+err)
		}
	});

	socket.on('validate_token_scope2', function(data){
		console.log("got validate token scope event")
		try{
			resp = tgserv.validate_token(socket);

		}catch(err){
			console.log("error on validate token scope: "+err)
			//socket.emit('token_scope_error',err)
		}

	});

	socket.on('create_rn', function(data){
		console.log("got create RN event")
		resp = tgserv.create_remote_network(socket);
	});

	socket.on('create_connector', function(data){
		console.log("got create connector event")
		console.log("in create_connector_a")
		console.log(typeof(data))
		console.log(data)
		// data: {"id":"UmVtb3RlTmV0d29yazo2NTI5OA==","name":"Home Network"}
		console.log("remote network in connector creation:"+data)

		tgserv.create_connector(data,socket);
		
		//resp = 
	});

	socket.on('get_subnet', function(data){ 
		console.log("in get_subnet_a")
		console.log(typeof(data))
		console.log(data)
			resp = tgserv.get_subnet(data,socket);
	});

	socket.on('create_resource', function(data){
		console.log("in create_resource_a")
		console.log(typeof(data))
		console.log(data)
		//try{
			resp = tgserv.create_resource(data,socket);
			socket.emit('resource_created',resp)

		//}catch(err){
		//	socket.emit('resource_failed',err)
		//}

	});

});

server.listen(80); //process.env.PORT || 5000);
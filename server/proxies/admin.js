/*jshint node:true*/

module.exports = function(app) {
  // For options, see:
  // https://github.com/nodejitsu/node-http-proxy
  var proxy = require('http-proxy').createProxyServer({});

  proxy.on('error', function(err, req) {
    console.error(err, req.url);
  });

  app.use('/admin', function(req, res, next){
    // include root path in proxied request
    req.url = '/admin' + req.url;
    proxy.web(req, res, { target: 'http://127.0.0.1:8001' });
  });
  app.use('/static', function(req, res, next){
    // include root path in proxied request
    req.url = '/static' + req.url;
    proxy.web(req, res, { target: 'http://127.0.0.1:8001' });
  });
  app.use('/status', function(req, res, next){
    // include root path in proxied request
    req.url = '/status' + req.url;
    proxy.web(req, res, { target: 'http://127.0.0.1:8001' });
  });
};

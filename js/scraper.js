// helper functions
String.format = function(src) {
  if (arguments.length == 0) return null;
  var args = Array.prototype.slice.call(arguments, 1);
  return src.replace(/\{(\d+)\}/g, function(m, i) {
    return args[i];
  });
};

// constants
var bid = 601021;
var today = '12-22'

var url_home = 'http://guba.eastmoney.com/'
var url_bar = url_home + 'list,{0},f_{1}.html'

var casper = require('casper').create();
casper.start();

var n = 1;
var finish = false;
while (!finish) {
  var url = String.format(url_bar, bid, n);
  casper.thenOpen(url, function() {
    this.echo('Scraping: ' + url);
    var articles = this.evaluate(function() {
      return document.querySelectorAll('div[class~=articleh]');
    });
    for (var art in articles) {
      this.echo(art.getHTML('.l6'));
    }
  });
  n += 1;
  finish = true;
}

casper.run();

var casper = require('casper').create();

casper.start('http://guba.eastmoney.com/news,gssz,132514837.html', function() {
  this.echo(this.getHTML());
});

casper.run();

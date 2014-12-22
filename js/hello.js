var page = require('webpage').create()
console.log('The default user agent is ' + page.settings.userAgent);
page.open('http://guba.eastmoney.com/news,gssz,132514837.html', function(status) {
  if (status !== 'success') {
    console.log('Unable to access network');
  } else {
    var ua = page.evaluate(function() {
      return document.getElementsByClassName('pagernum');
    });
    console.log(ua);
  }
  phantom.exit();
});

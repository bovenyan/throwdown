var mysql      = require('mysql');
var connection = mysql.createConnection({
  host     : 'localhost',
  port     : 9000,
  user     : 'root',
  password : '',
  database : 'myboly'
});

connection.connect();

connection.query('select * from lsp', function(err, results, fields) {
  if (err) return console.log(err);

  console.log(JSON.parse(JSON.stringify(results)));
});

connection.end();
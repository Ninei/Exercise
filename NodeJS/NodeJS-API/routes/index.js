var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index', { title: 'HI~~! Express' });
});

// router.post('/point/save/:type', async(req, res)=>{
//   let {type} = req.params;
//   let userData = req.body.user;

//   console.log(type);
//   console.log(userData.sn);
//   console.log(userData.point);

//   res.send("ok\ntype: " + type + ", sn: " + userData.sn + ", point: " + userData.point);
// });

module.exports = router;

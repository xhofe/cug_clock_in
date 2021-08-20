const Koa = require('koa');
const bodyParser = require('koa-bodyparser');
const desEnc = require('./des');

const app = new Koa();
app.use(bodyParser());
app.use(async ctx => {
  const data = ctx.request.body.data
  if(data){
    ctx.body = desEnc(data,'1','2','3');
  }
});

const port = process.argv[2] || 5244;
console.log(`listening on ${port}`);
app.listen(port);
  

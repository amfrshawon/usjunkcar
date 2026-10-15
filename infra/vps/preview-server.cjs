// Static site server: private preview on dev, public static site on main. Replaced by the future Next.js application.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.join(__dirname, 'public');
const types = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.gif':'image/gif','.woff':'font/woff','.woff2':'font/woff2','.ttf':'font/ttf','.ico':'image/x-icon','.xml':'application/xml; charset=utf-8','.txt':'text/plain; charset=utf-8','.webmanifest':'application/manifest+json'};
const server = http.createServer((req,res) => {
  const production = process.env.APP_ENV === 'production';
  if (!production) res.setHeader('X-Robots-Tag','noindex, nofollow, noarchive');
  res.setHeader('Cache-Control', production ? 'public, max-age=300' : 'private, no-store');
  res.setHeader('X-Content-Type-Options','nosniff');
  if (!['GET','HEAD'].includes(req.method)) { res.writeHead(405); return res.end('Method not allowed.'); }
  let pathname;
  try { pathname = decodeURIComponent(new URL(req.url,'http://localhost').pathname); }
  catch { res.writeHead(400); return res.end(); }
  if (pathname === '/api/v1/health') {
    res.setHeader('Content-Type','application/json');
    return res.end(JSON.stringify({data:{status:'ok',commit:process.env.RELEASE_SHA,environment:process.env.APP_ENV}}));
  }
  const file = path.resolve(root, '.' + (pathname.endsWith('/') ? pathname + 'index.html' : pathname));
  if (!file.startsWith(root + path.sep) || pathname.includes('\0') || pathname.split('/').some(p=>p.startsWith('.'))) {
    res.writeHead(404); return res.end();
  }
  fs.stat(file,(error,stat)=> {
    if(!error && stat.isDirectory()) { res.writeHead(301,{Location: pathname + '/'}); return res.end(); }
    if(error || !stat.isFile()) {
      res.writeHead(404,{'Content-Type':'text/html; charset=utf-8'});
      return res.end('<h1>Page not found</h1><p>Sorry, that page does not exist.</p><a href="/">Return to the US Junk Cars homepage</a>');
    }
    res.writeHead(200,{'Content-Type':types[path.extname(file).toLowerCase()] || 'application/octet-stream','Content-Length':stat.size});
    if(req.method==='HEAD') return res.end();
    fs.createReadStream(file).on('error',()=>res.destroy()).pipe(res);
  });
});
if (require.main === module) {
  if(!['development','production'].includes(process.env.APP_ENV)) throw new Error('APP_ENV must be development or production');
  server.listen(Number(process.env.PORT || 4174),process.env.HOSTNAME || '127.0.0.1');
}
module.exports = server;

(function(){
 var store={}; var mem={getItem:function(k){return k in store?store[k]:null},setItem:function(k,v){store[k]=String(v)},removeItem:function(k){delete store[k]}};
 Object.defineProperty(window,'localStorage',{get:function(){return mem}});
 window.__ND_MOCK=true;
 var tree={}, listeners=[], bc=new BroadcastChannel('nd');
 var uid='u'+Math.random().toString(36).slice(2,8);
 function parts(p){return p.split('/').filter(Boolean)}
 function get(p){var n=tree;var ks=parts(p);for(var i=0;i<ks.length;i++){if(n==null||typeof n!=='object')return null;n=n[ks[i]];}return n===undefined?null:n}
 function resolve(v){ if(v&&typeof v==='object'){ if(v['.sv']) return Date.now(); var o={}; for(var k in v) o[k]=resolve(v[k]); return o;} return v;}
 function setRaw(p,v){var ks=parts(p);var n=tree;for(var i=0;i<ks.length-1;i++){if(n[ks[i]]==null||typeof n[ks[i]]!=='object')n[ks[i]]={};n=n[ks[i]];} if(v===null||v===undefined) delete n[ks[ks.length-1]]; else n[ks[ks.length-1]]=JSON.parse(JSON.stringify(v));}
 function clone(v){return v==null?null:JSON.parse(JSON.stringify(v))}
 function notify(p){ listeners.slice().forEach(function(l){ if(p.indexOf(l.p)===0||l.p.indexOf(p)===0){ var v=clone(get(l.p)); if(l.lim&&v&&typeof v==='object'){var ks=Object.keys(v).sort().slice(-l.lim),o={};ks.forEach(function(k){o[k]=v[k]});v=o;} var s=JSON.stringify(v); if(s!==l.last){l.last=s; l.cb({val:function(){return clone(v)}});} } }); }
 function apply(p,v,b){ setRaw(p,v); notify(p); if(b) bc.postMessage({p:p,v:v}); }
 bc.onmessage=function(e){ var d=e.data; if(d.hello){ bc.postMessage({full:tree}); return; } if(d.full){ if(!Object.keys(tree).length && Object.keys(d.full).length){ tree=d.full; listeners.slice().forEach(function(l){ var v=clone(get(l.p)); if(l.lim&&v&&typeof v==='object'){var ks=Object.keys(v).sort().slice(-l.lim),o={};ks.forEach(function(k){o[k]=v[k]});v=o;} var s=JSON.stringify(v); if(s!==l.last){l.last=s; l.cb({val:function(){return clone(v)}});} }); } return; } apply(d.p,d.v,false); };
 bc.postMessage({hello:1});
 function Ref(p){ this.p=p.replace(/^\/+|\/+$/g,''); }
 Ref.prototype.child=function(c){return new Ref(this.p+'/'+c)};
 Ref.prototype.set=function(v){ apply(this.p,resolve(v),true); return Promise.resolve(); };
 Ref.prototype.update=function(o){ for(var k in o) apply(this.p+'/'+k, resolve(o[k]), true); return Promise.resolve(); };
 Ref.prototype.on=function(ev,cb){ if(this.p==='.info/connected'){ setTimeout(function(){cb({val:function(){return true}})},10); return cb;} if(this.p==='.info/serverTimeOffset'){ setTimeout(function(){cb({val:function(){return 0}})},10); return cb;} var l={p:this.p,cb:cb,lim:this.lim}; var v=clone(get(this.p)); if(l.lim&&v&&typeof v==='object'){var ks=Object.keys(v).sort().slice(-l.lim),o={};ks.forEach(function(k){o[k]=v[k]});v=o;} l.last=JSON.stringify(v); listeners.push(l); setTimeout(function(){cb({val:function(){return clone(v)}})},5); return cb; };
 Ref.prototype.limitToLast=function(n){ var self=this, r=Object.create(Ref.prototype); r.p=self.p; r.lim=n; return r; };
 Ref.prototype.off=function(ev,cb){ listeners=listeners.filter(function(l){return l.cb!==cb}); };
 Ref.prototype.transaction=function(fn){ var nv=fn(clone(get(this.p))); if(nv!==undefined) apply(this.p,nv,true); return Promise.resolve({committed:true}); };
 Ref.prototype.once=function(){var v=clone(get(this.p));return Promise.resolve({val:function(){return v}})};
 Ref.prototype.remove=function(){apply(this.p,null,true);return Promise.resolve()};
 Ref.prototype.onDisconnect=function(){ return {update:function(){return Promise.resolve()},remove:function(){return Promise.resolve()},set:function(){return Promise.resolve()}}; };
 window.__db={get:get};
 var db={ref:function(p){return new Ref(p||'')}};
 var AU={currentUser:null,onAuthStateChanged:function(cb){var self=this;setTimeout(function(){cb(self.currentUser)},5);return function(){}},
 signInAnonymously:function(){this.currentUser={uid:uid,isAnonymous:true,linkWithPopup:function(){AU.currentUser.isAnonymous=false;AU.currentUser.email="jean@gmail.com";return Promise.resolve({user:AU.currentUser})}};return Promise.resolve({user:this.currentUser})},
 getRedirectResult:function(){return Promise.resolve({user:null})}};
 var authFn=function(){return AU}; authFn.GoogleAuthProvider=function(){};
 window.firebase={apps:[],initializeApp:function(){this.apps.push(1)},auth:authFn,database:Object.assign(function(){return db},{ServerValue:{TIMESTAMP:{'.sv':'timestamp'}}})};
})();

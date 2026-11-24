const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('preview/index.html','utf8');
const js=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x=>x[1]).find(x=>x.includes('function shoppingList'));
const memory=new Map([['kz-state','PRODUCTION SENTINEL']]),handlers={},els={};
function el(id){if(els[id])return els[id];const attrs={};return els[id]={id,style:{setProperty(){},removeProperty(){}},dataset:{},value:'',innerHTML:'',offsetWidth:100,offsetHeight:40,offsetLeft:0,scrollTop:0,classList:{contains(){return false},add(){},remove(){},toggle(){}},setAttribute(k,v){attrs[k]=v},getAttribute(k){return attrs[k]||null},removeAttribute(k){delete attrs[k]},querySelectorAll(){return[]},querySelector(){return null},getBoundingClientRect(){return{top:0,bottom:40,left:0,right:100}},getAnimations(){return[]},animate(){},appendChild(){},remove(){},focus(){},addEventListener(k,f){(handlers[id+':'+k]??=[]).push(f)}}}
const doc={documentElement:el('root'),body:el('body'),head:el('head'),visibilityState:'visible',getElementById:el,querySelectorAll(){return[]},querySelector(){return null},createElement(){return el('created')},addEventListener(){}};
const c={console,document:doc,navigator:{},localStorage:{getItem:k=>memory.get(k)||null,setItem:(k,v)=>memory.set(k,String(v))},matchMedia:()=>({matches:false,addEventListener(){}}),setTimeout:()=>0,clearTimeout(){},setInterval:()=>0,clearInterval(){},requestAnimationFrame(){},addEventListener(){},scrollTo(){},scrollBy(){},scrollY:0,scrollX:0,innerHeight:800,innerWidth:390,crypto:require('crypto').webcrypto,URL,Blob,File,TextEncoder,AbortController,fetch:()=>{throw Error('Unexpected external request')},getComputedStyle:()=>({top:'0'})};c.window=c;vm.createContext(c);
vm.runInContext(js.replace(/boot\(\);\s*$/,'Object.assign(S,exampleState());migrate();'),c);
function run(s){return vm.runInContext(s,c)}
function click(a,extra={}){const b={dataset:{a,...extra},textContent:'',isConnected:true};for(const f of handlers['body:click']||[])f({target:{closest:()=>b}})}
run('render()');assert(run('S.recipes.length')>0);assert(run('shoppingList().length')>0);
const initial=run('JSON.stringify(S)');const count=run('entries(S.plan.week).length');
for(const design of ['classic','glass'])for(const theme of ['light','dark','auto']){
 click('design',{v:design});click('theme',{v:theme});for(const tab of ['week','recipes','shop','settings']){click('tab',{tab});assert(els.app.innerHTML.length>100)}
 assert.equal(run('JSON.stringify(S)'),initial,'Styling must not mutate data');
}
assert(els.app.innerHTML.includes('Классик'));assert(els.app.innerHTML.includes('Стекло'));
const id=run('entries(S.plan.week)[0].e.id'),portion=run('entries(S.plan.week)[0].e.servings');
click('serv',{id,d:'1'});assert.equal(run('entries(S.plan.week)[0].e.servings'),portion+1);click('serv',{id,d:'-1'});
const beforeClear=run('JSON.stringify(S.plan)');click('clearWeek');assert.equal(run('entries(S.plan.week).length'),0);assert.equal(run('UI.undo.left'),5);click('undo');assert.equal(run('JSON.stringify(S.plan)'),beforeClear);
const beforeList=run('listItems().length');click('clearList');assert.equal(run('listItems().length'),0);click('undo');assert.equal(run('listItems().length'),beforeList);
el('exItem').value='Тестовый товар';click('addExtra');assert(run('S.plan.extras.some(x=>x.name==="Тестовый товар")'));const exId=run('S.plan.extras.at(-1).id');click('rmExtra',{id:exId});assert(!run('S.plan.extras.some(x=>x.id==='+JSON.stringify(exId)+')'));
const snap=run('JSON.stringify(S)');run('localSave()');assert.equal(memory.get('kz-preview-state'),snap);assert.equal(memory.get('kz-state'),'PRODUCTION SENTINEL');
run('UI.sheet={t:"pick",k:"0-b"};render()');const rid=run('S.recipes[0].id');click('pickAdd',{id:rid});assert.equal(run('entries(S.plan.week).length'),count+1);
run('UI.sheet={t:"item",key:shoppingList()[0].key};render()');assert(els.sheetBody.innerHTML.length>0);
run('UI.sheet=null;UI.sel=S.recipes[0].id;UI.tab="recipes";render()');assert(els.app.innerHTML.length>0);
const recipesBefore=run('S.recipes.length');
run('UI.sheet=null;openEditor({name:"Проверка рецепта",servings:2,ingredients:[{name:"Рис",qty:200,unit:"г",cat:"Крупы, макароны, мука",pantry:false}]},true)');
click('saveEditor');assert.equal(run('S.recipes.length'),recipesBefore+1);
const newId=run('S.recipes.at(-1).id');
click('edit',{id:newId});run('UI.editor.name="Изменённый рецепт"');click('saveEditor');assert.equal(run('S.recipes.at(-1).name'),'Изменённый рецепт');
click('delRecipe',{id:newId});assert.equal(run('S.recipes.length'),recipesBefore);click('undo');assert.equal(run('S.recipes.length'),recipesBefore+1);
console.log('PASS: 24 theme/screen combinations; unchanged data on theme switch; portions; clear/undo menu and shopping; 5s undo; extra goods; isolated persistence; dish picker; recipe/item rendering; create/edit/delete/restore recipe.');

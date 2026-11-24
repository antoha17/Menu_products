from pathlib import Path
import re,json,shutil
root=Path(__file__).resolve().parent.parent
s=(root/'src/korzina.html').read_text()
# A separate source copy: production source and generated files remain untouched.
s=s.replace('kz-', 'kz-preview-').replace('data/users/', 'data/preview-users/')
s=s.replace('</style>', (root/'preview-source/redesign.css').read_text()+'\n</style>',1)
old='''<div class="sechead"><h1>Меню недели</h1>${n?"":`<p class="sub">Пока ничего не запланировано</p>`}</div>
  ${n?`<div class="actions"><button class="btn danger" data-a="clearWeek">Очистить меню</button></div>`:""}'''
new='''<div class="sechead weekhead"><h1>Меню недели</h1>${n?`<button class="btn clear-menu" data-a="clearWeek" aria-label="Очистить меню недели">Очистить</button>`:""}${n?"":`<p class="sub">Пока ничего не запланировано</p>`}</div>'''
assert old in s
s=s.replace(old,new)
marker='  <div class="gtitle">Оформление</div>'
assert marker in s
s=s.replace(marker,'''  <p class="preview-note">Тестовая версия · данные хранятся отдельно от основной.</p>
  <div class="gtitle">Оформление</div>
  <div class="style-options" role="radiogroup" aria-label="Стиль">
  ${[["classic","Классик"],["glass","Стекло"]].map(([k,l])=>`<button class="style-choice" role="radio" aria-checked="${designPref()===k}" data-a="design" data-v="${k}"><span class="style-sample ${k==="glass"?"glassy":""}" aria-hidden="true"><i></i><i></i><i></i></span>${l}</button>`).join("")}
  </div>''')
s=s.replace('   <div class="lbl" style="margin-top:6px">Цвет фона</div>','   <details class="custom-colors"><summary>Настроить цвета</summary><div class="lbl" style="margin-top:6px">Цвет фона</div>',1)
needle='value="${getAcc().h??151}" aria-label="Цвет кнопок">'
assert needle in s
s=s.replace(needle,needle+'</details>',1)
design='''
function designPref(){return lsGet("kz-preview-design")==="glass"?"glass":"classic"}
function applyDesign(){
  const style=designPref(),d=isDark(),el=document.documentElement,st=el.style;
  el.dataset.design=style;
  const classic=style==="classic";
  const vars={"--bg":d?(classic?"#111916":"#111622"):(classic?"#F5F7F5":"#EFF4F6"),
    "--surface":d?"#1C2722":"#FFFFFF","--ink":d?"#F1F6F3":"#14241D",
    "--muted":d?"#A9B8B0":"#5C6D64","--line":d?"rgba(215,235,225,.14)":"rgba(28,65,47,.12)",
    "--preview-card":classic?(d?"#1C2722":"#FFFFFF"):(d?"rgba(37,48,64,.88)":"rgba(255,255,255,.76)"),
    "--glass":d?"rgba(27,38,49,.9)":"rgba(255,255,255,.82)",
    "--shadow":d?"rgba(0,0,0,.18)":"rgba(30,60,46,.06)"};
  Object.entries(vars).forEach(([k,v])=>st.setProperty(k,v));
  if(!classic&&!lsGet("kz-preview-palette")){
    st.setProperty("--blob1",d?"#163A3D":"#CEF2E7");st.setProperty("--blob3",d?"#302D50":"#DDDDF8");
  }
}
'''
s=s.replace('function applyPalette(){',design+'\nfunction applyPalette(){',1)
s=s.replace('else st.removeProperty("--bg");','else st.removeProperty("--bg");\n  applyDesign();',1)
s=s.replace('    case "theme":','    case "design":lsSet("kz-preview-design",b.dataset.v);applyPalette();render();break;\n    case "theme":',1)
p=root/'preview-source/korzina.html';p.parent.mkdir(exist_ok=True);p.write_text(s)

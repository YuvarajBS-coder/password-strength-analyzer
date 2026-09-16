const $=id=>document.getElementById(id);
const password=$("password"), userId=$("userId"), bar=$("bar"), strength=$("strength"), feedback=$("feedback");

function mark(id,ok,text){$(id).textContent=(ok?"✓ ":"○ ")+text}

async function analyze(){
  const res=await fetch("/analyze",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({user_id:userId.value,password:password.value})});
  const d=await res.json();
  mark("length",d.length>=8,"8+ characters");
  mark("lowercase",d.lowercase,"Lowercase letter");
  mark("uppercase",d.uppercase,"Uppercase letter");
  mark("number",d.number,"Number");
  mark("special",d.special,"Special character");
  mark("unique",d.unique_characters>=Math.max(4,Math.floor(d.length*.55)),"Unique character variety");
  strength.textContent=d.strength;
  bar.style.width=(d.level*20)+"%";
  $("reuse").textContent=d.reused?"⚠ Password reuse detected":"";
  feedback.innerHTML="";
  d.feedback.forEach(x=>{const li=document.createElement("li");li.textContent=x;feedback.appendChild(li)});
}
password.addEventListener("input",analyze); userId.addEventListener("input",()=>{if(password.value)analyze()});
$("toggle").onclick=()=>{password.type=password.type==="password"?"text":"password";$("toggle").textContent=password.type==="password"?"Show":"Hide"};
$("save").onclick=async()=>{
  const res=await fetch("/save",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({user_id:userId.value,password:password.value})});
  const d=await res.json(); $("message").textContent=d.message;
  if(res.ok) analyze();
};
$("generate").onclick=async()=>{
  const n=$("genLength").value||16;
  const d=await (await fetch("/generate?length="+encodeURIComponent(n))).json();
  $("generated").value=d.password; password.value=d.password; analyze();
};
$("copy").onclick=async()=>{
  if(!$("generated").value)return;
  await navigator.clipboard.writeText($("generated").value);
  $("copy").textContent="Copied!";setTimeout(()=>$("copy").textContent="Copy",1200);
};

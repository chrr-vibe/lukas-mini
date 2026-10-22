/* 배경 그리기 코드: 내 방(makeRoom) + 페이지 배경 프리셋(PAGE_BG) */
function makeRoom(room,lampOn,night){
  const c=document.createElement('canvas');c.width=W;c.height=ROOM_H;const x=c.getContext('2d');
  if(room==='bed'){
    // wall
    R(x,0,0,128,54,'#cdb9ef');
    for(let i=0;i<128;i+=8)for(let j=3;j<50;j+=8)R(x,i+((j/8|0)%2?4:0),j,2,2,'#dccbf7');
    R(x,0,50,128,4,'#a98fd6');
    // floor
    R(x,0,54,128,34,'#e9be93');
    for(let j=58;j<88;j+=6){R(x,0,j,128,1,'#d6a57a');for(let i=(j%12?6:20);i<128;i+=28)R(x,i,j-5,1,5,'#d6a57a');}
    // window
    const day=lampOn&&!night;   // 밤이면 창문도 어둡게
    R(x,88,8,32,24,'#7d5ba6');R(x,90,10,28,20,day?'#bfe9ff':'#3c3f7a');
    R(x,103,10,2,20,'#7d5ba6');R(x,90,19,28,2,'#7d5ba6');
    if(!day){R(x,95,13,2,2,'#fff8c8');R(x,110,23,1,1,'#fff8c8');R(x,113,13,1,1,'#fff8c8');}
    else{R(x,92,12,6,3,'#ffffff');R(x,108,22,7,3,'#ffffff');}
    if(night){x.fillStyle='#fff3b0';x.beginPath();x.arc(112,15,3,0,7);x.fill();x.fillStyle='#3c3f7a';x.beginPath();x.arc(113,14,2.5,0,7);x.fill();}
    R(x,86,6,6,30,'#ff9cc8');R(x,116,6,6,30,'#ff9cc8');R(x,86,6,36,3,'#ff7fb6');
    // frame
    R(x,20,8,14,12,'#ffffff');R(x,21,9,12,10,'#ffd5e6');R(x,24,12,6,5,'#ff8fbf');
    // pendant lamp (전등)
    R(x,63,0,1,6,'#5b4475');
    x.fillStyle=lampOn?'#ffe58a':'#9d8fb3';x.beginPath();x.moveTo(57,13);x.lineTo(70,13);x.lineTo(66,6);x.lineTo(61,6);x.closePath();x.fill();
    R(x,57,13,13,1,'#5b4475');
    if(lampOn){x.fillStyle='rgba(255,240,170,.28)';x.beginPath();x.moveTo(57,14);x.lineTo(70,14);x.lineTo(84,40);x.lineTo(43,40);x.closePath();x.fill();}
    // bed
    R(x,2,26,46,30,'#8a5a48');R(x,4,28,42,26,'#b57a5e');   // headboard
    R(x,6,30,38,3,'#d79a78');
    R(x,0,46,52,22,'#8a5a48');                              // frame
    R(x,2,44,48,16,'#ffffff');                              // mattress/sheet
    R(x,4,40,20,8,'#fff6fb');R(x,4,47,20,1,'#e7d3e3');      // pillow
    R(x,14,48,38,18,'#ff9cc8');R(x,14,48,38,2,'#ffc2dd');   // blanket
    for(let i=18;i<52;i+=8)for(let j=53;j<66;j+=6)R(x,i+((j/6|0)%2?4:0),j,2,2,'#ffe1ee');
    R(x,2,66,4,6,'#6d4536');R(x,46,66,4,6,'#6d4536');
    // bedside table + small lamp
    R(x,100,50,22,16,'#b57a5e');R(x,100,50,22,2,'#d79a78');R(x,102,56,18,1,'#8a5a48');R(x,110,58,2,2,'#ffe58a');
    R(x,102,66,3,6,'#8a5a48');R(x,117,66,3,6,'#8a5a48');
    R(x,110,40,2,10,'#8a5a48');x.fillStyle=lampOn?'#fff1a8':'#a99bc0';x.beginPath();x.moveTo(104,41);x.lineTo(118,41);x.lineTo(115,33);x.lineTo(107,33);x.closePath();x.fill();
    // rug
    x.fillStyle='#c6f0e2';x.beginPath();x.ellipse(66,80,30,7,0,0,Math.PI*2);x.fill();
    x.fillStyle='#9fdcc8';x.beginPath();x.ellipse(66,80,24,5,0,0,Math.PI*2);x.fill();
  }
  return c;
}

const PAGE_BG=[
  {name:'기본',     make:null},
  {name:'별밤',     make:(x)=>{R(x,0,0,90,160,'#3d3a7a');R(x,0,60,90,60,'#4d4890');R(x,0,110,90,50,'#6a5aa8');
      for(let i=0;i<60;i++){const sx=(i*37)%90, sy=(i*53)%120; R(x,sx,sy,1,1,i%5?'#fff6c8':'#ffd1f0'); if(i%9===0){R(x,sx-1,sy,3,1,'#fff6c8');R(x,sx,sy-1,1,3,'#fff6c8');}}
      x.fillStyle='#fff3b8';x.beginPath();x.arc(66,22,10,0,7);x.fill();x.fillStyle='#3d3a7a';x.beginPath();x.arc(71,19,9,0,7);x.fill();
      for(let i=0;i<90;i+=6){x.fillStyle='#2f2d63';x.beginPath();x.arc(i,152,7,Math.PI,0);x.fill();} R(x,0,152,90,8,'#2f2d63');}},
  {name:'민트 도트', make:(x)=>{R(x,0,0,90,160,'#d9f6ec');for(let y=4;y<160;y+=8)for(let i=4;i<90;i+=8)R(x,i,y,2,2,'#ffffff');}},
  {name:'라벤더 도트', make:(x)=>{R(x,0,0,90,160,'#e6defa');for(let y=4;y<160;y+=8)for(let i=4;i<90;i+=8)R(x,i,y,2,2,(i/8+y/8)%2?'#ffc8e2':'#ffffff');}},
  {name:'딸기체크', make:(x)=>{R(x,0,0,90,160,'#fff5f7');
      for(let j=0;j<160;j+=10)for(let i=0;i<90;i+=10){if((i/10+j/10)%2)R(x,i,j,10,10,'#ffd6e0');} for(let j=0;j<160;j+=10)R(x,0,j,90,5,'rgba(255,170,195,.35)');
      const sb=(cx,cy)=>{R(x,cx+1,cy,4,1,'#5fbf6a');R(x,cx+2,cy-1,2,1,'#5fbf6a');R(x,cx,cy+1,6,3,'#ff5a7a');R(x,cx+1,cy+4,4,1,'#ff5a7a');R(x,cx+2,cy+5,2,1,'#ff5a7a');
        R(x,cx+1,cy+2,1,1,'#fff3a0');R(x,cx+4,cy+2,1,1,'#fff3a0');R(x,cx+2,cy+4,1,1,'#fff3a0');};
      for(let j=4;j<160;j+=20)for(let i=(j/20%2)?12:2;i<90;i+=20)sb(i,j);}},
  {name:'노을바다', make:(x)=>{const sky=['#ffd1a8','#ffbfae','#ffb0bf','#f7a7d1','#d9a8ea'];sky.forEach((c,i)=>R(x,0,i*18,90,18,c));
      x.fillStyle='#fff0a8';x.beginPath();x.arc(45,86,14,Math.PI,0);x.fill();
      R(x,0,86,90,74,'#8fc9e8');for(let j=90;j<160;j+=6)for(let i=(j%12?0:6);i<90;i+=12)R(x,i,j,6,1,'#c2e6f7');
      for(let j=88;j<120;j+=3)R(x,45-(j-86)*.6,j,(j-86)*1.2,1,'rgba(255,240,170,.55)');
      R(x,0,146,90,14,'#ffe2b8');for(let i=3;i<90;i+=9)R(x,i,149,2,1,'#f5c98f');
      R(x,10,140,6,1,'#ffffff');R(x,70,128,8,1,'#ffffff');}},
];

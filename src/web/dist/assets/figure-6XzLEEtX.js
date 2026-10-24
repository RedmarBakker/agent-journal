import{H as ne,A as ie,p as me,a as Ap,b as Rp,h as Ql,s as Cp,o as Pp,P as Lp,R as Ip,f as Dp,F as Np,g as Up,c as Op,U as ya,G as ws,V as Fp,l as Bp,d as kp,T as zp,e as Hp,i as ss,L as Gp,j as Vp}from"./main-ygTY08rz.js";import{e as el}from"./tokens-CDlVDfIF.js";import"./tip-mA-Xgc0k.js";import"./preload-helper-Dp1pzeXC.js";/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const eh="170",Wp=0,Vh=1,Xp=2,Vd=1,qp=2,Mi=3,Ti=0,yn=1,An=2,Zi=0,nr=1,Wh=2,Xh=3,qh=4,jp=5,vs=100,$p=101,Yp=102,Kp=103,Zp=104,Jp=200,Qp=201,em=202,tm=203,tl=204,nl=205,nm=206,im=207,sm=208,rm=209,om=210,am=211,cm=212,lm=213,hm=214,il=0,sl=1,rl=2,cr=3,ol=4,al=5,cl=6,ll=7,Wd=0,um=1,dm=2,Ji=0,fm=1,pm=2,mm=3,gm=4,_m=5,xm=6,vm=7,jh="attached",ym="detached",Xd=300,lr=301,hr=302,hl=303,ul=304,Da=306,ur=1e3,qi=1001,Ma=1002,pn=1003,qd=1004,$r=1005,Dn=1006,ha=1007,bi=1008,Ai=1009,jd=1010,$d=1011,io=1012,th=1013,Es=1014,Jn=1015,uo=1016,nh=1017,ih=1018,dr=1020,Yd=35902,Kd=1021,Zd=1022,kn=1023,Jd=1024,Qd=1025,ir=1026,fr=1027,sh=1028,rh=1029,ef=1030,oh=1031,ah=1033,ua=33776,da=33777,fa=33778,pa=33779,dl=35840,fl=35841,pl=35842,ml=35843,gl=36196,_l=37492,xl=37496,vl=37808,yl=37809,Ml=37810,wl=37811,bl=37812,Sl=37813,El=37814,Tl=37815,Al=37816,Rl=37817,Cl=37818,Pl=37819,Ll=37820,Il=37821,ma=36492,Dl=36494,Nl=36495,tf=36283,Ul=36284,Ol=36285,Fl=36286,so=2300,ro=2301,ec=2302,$h=2400,Yh=2401,Kh=2402,Mm=2500,wm=0,nf=1,Bl=2,bm=3200,Sm=3201,sf=0,Em=1,Wi="",qt="srgb",mn="srgb-linear",Na="linear",Rt="srgb",Ds=7680,Zh=519,Tm=512,Am=513,Rm=514,rf=515,Cm=516,Pm=517,Lm=518,Im=519,kl=35044,Jh="300 es",Si=2e3,wa=2001;class Mr{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,o=s.length;r<o;r++)s[r].call(this,e);e.target=null}}}const an=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Qh=1234567;const sr=Math.PI/180,pr=180/Math.PI;function zn(){const i=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(an[i&255]+an[i>>8&255]+an[i>>16&255]+an[i>>24&255]+"-"+an[e&255]+an[e>>8&255]+"-"+an[e>>16&15|64]+an[e>>24&255]+"-"+an[t&63|128]+an[t>>8&255]+"-"+an[t>>16&255]+an[t>>24&255]+an[n&255]+an[n>>8&255]+an[n>>16&255]+an[n>>24&255]).toLowerCase()}function Yt(i,e,t){return Math.max(e,Math.min(t,i))}function ch(i,e){return(i%e+e)%e}function Dm(i,e,t,n,s){return n+(i-e)*(s-n)/(t-e)}function Nm(i,e,t){return i!==e?(t-i)/(e-i):0}function Zr(i,e,t){return(1-t)*i+t*e}function Um(i,e,t,n){return Zr(i,e,1-Math.exp(-t*n))}function Om(i,e=1){return e-Math.abs(ch(i,e*2)-e)}function Fm(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*(3-2*i))}function Bm(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*i*(i*(i*6-15)+10))}function km(i,e){return i+Math.floor(Math.random()*(e-i+1))}function zm(i,e){return i+Math.random()*(e-i)}function Hm(i){return i*(.5-Math.random())}function Gm(i){i!==void 0&&(Qh=i);let e=Qh+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function Vm(i){return i*sr}function Wm(i){return i*pr}function Xm(i){return(i&i-1)===0&&i!==0}function qm(i){return Math.pow(2,Math.ceil(Math.log(i)/Math.LN2))}function jm(i){return Math.pow(2,Math.floor(Math.log(i)/Math.LN2))}function $m(i,e,t,n,s){const r=Math.cos,o=Math.sin,a=r(t/2),c=o(t/2),l=r((e+n)/2),h=o((e+n)/2),u=r((e-n)/2),d=o((e-n)/2),f=r((n-e)/2),m=o((n-e)/2);switch(s){case"XYX":i.set(a*h,c*u,c*d,a*l);break;case"YZY":i.set(c*d,a*h,c*u,a*l);break;case"ZXZ":i.set(c*u,c*d,a*h,a*l);break;case"XZX":i.set(a*h,c*m,c*f,a*l);break;case"YXY":i.set(c*f,a*h,c*m,a*l);break;case"ZYZ":i.set(c*m,c*f,a*h,a*l);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+s)}}function Zn(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function Tt(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const Ft={DEG2RAD:sr,RAD2DEG:pr,generateUUID:zn,clamp:Yt,euclideanModulo:ch,mapLinear:Dm,inverseLerp:Nm,lerp:Zr,damp:Um,pingpong:Om,smoothstep:Fm,smootherstep:Bm,randInt:km,randFloat:zm,randFloatSpread:Hm,seededRandom:Gm,degToRad:Vm,radToDeg:Wm,isPowerOfTwo:Xm,ceilPowerOfTwo:qm,floorPowerOfTwo:jm,setQuaternionFromProperEuler:$m,normalize:Tt,denormalize:Zn};class te{constructor(e=0,t=0){te.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6],this.y=s[1]*t+s[4]*n+s[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Yt(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),s=Math.sin(t),r=this.x-e.x,o=this.y-e.y;return this.x=r*n-o*s+e.x,this.y=r*s+o*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class rt{constructor(e,t,n,s,r,o,a,c,l){rt.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,o,a,c,l)}set(e,t,n,s,r,o,a,c,l){const h=this.elements;return h[0]=e,h[1]=s,h[2]=a,h[3]=t,h[4]=r,h[5]=c,h[6]=n,h[7]=o,h[8]=l,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,o=n[0],a=n[3],c=n[6],l=n[1],h=n[4],u=n[7],d=n[2],f=n[5],m=n[8],_=s[0],g=s[3],p=s[6],y=s[1],M=s[4],x=s[7],E=s[2],T=s[5],P=s[8];return r[0]=o*_+a*y+c*E,r[3]=o*g+a*M+c*T,r[6]=o*p+a*x+c*P,r[1]=l*_+h*y+u*E,r[4]=l*g+h*M+u*T,r[7]=l*p+h*x+u*P,r[2]=d*_+f*y+m*E,r[5]=d*g+f*M+m*T,r[8]=d*p+f*x+m*P,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],c=e[6],l=e[7],h=e[8];return t*o*h-t*a*l-n*r*h+n*a*c+s*r*l-s*o*c}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],c=e[6],l=e[7],h=e[8],u=h*o-a*l,d=a*c-h*r,f=l*r-o*c,m=t*u+n*d+s*f;if(m===0)return this.set(0,0,0,0,0,0,0,0,0);const _=1/m;return e[0]=u*_,e[1]=(s*l-h*n)*_,e[2]=(a*n-s*o)*_,e[3]=d*_,e[4]=(h*t-s*c)*_,e[5]=(s*r-a*t)*_,e[6]=f*_,e[7]=(n*c-l*t)*_,e[8]=(o*t-n*r)*_,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,s,r,o,a){const c=Math.cos(r),l=Math.sin(r);return this.set(n*c,n*l,-n*(c*o+l*a)+o+e,-s*l,s*c,-s*(-l*o+c*a)+a+t,0,0,1),this}scale(e,t){return this.premultiply(tc.makeScale(e,t)),this}rotate(e){return this.premultiply(tc.makeRotation(-e)),this}translate(e,t){return this.premultiply(tc.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<9;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const tc=new rt;function of(i){for(let e=i.length-1;e>=0;--e)if(i[e]>=65535)return!0;return!1}function oo(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function Ym(){const i=oo("canvas");return i.style.display="block",i}const eu={};function Yr(i){i in eu||(eu[i]=!0,console.warn(i))}function Km(i,e,t){return new Promise(function(n,s){function r(){switch(i.clientWaitSync(e,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:s();break;case i.TIMEOUT_EXPIRED:setTimeout(r,t);break;default:n()}}setTimeout(r,t)})}function Zm(i){const e=i.elements;e[2]=.5*e[2]+.5*e[3],e[6]=.5*e[6]+.5*e[7],e[10]=.5*e[10]+.5*e[11],e[14]=.5*e[14]+.5*e[15]}function Jm(i){const e=i.elements;e[11]===-1?(e[10]=-e[10]-1,e[14]=-e[14]):(e[10]=-e[10],e[14]=-e[14]+1)}const ft={enabled:!0,workingColorSpace:mn,spaces:{},convert:function(i,e,t){return this.enabled===!1||e===t||!e||!t||(this.spaces[e].transfer===Rt&&(i.r=Ei(i.r),i.g=Ei(i.g),i.b=Ei(i.b)),this.spaces[e].primaries!==this.spaces[t].primaries&&(i.applyMatrix3(this.spaces[e].toXYZ),i.applyMatrix3(this.spaces[t].fromXYZ)),this.spaces[t].transfer===Rt&&(i.r=rr(i.r),i.g=rr(i.g),i.b=rr(i.b))),i},fromWorkingColorSpace:function(i,e){return this.convert(i,this.workingColorSpace,e)},toWorkingColorSpace:function(i,e){return this.convert(i,e,this.workingColorSpace)},getPrimaries:function(i){return this.spaces[i].primaries},getTransfer:function(i){return i===Wi?Na:this.spaces[i].transfer},getLuminanceCoefficients:function(i,e=this.workingColorSpace){return i.fromArray(this.spaces[e].luminanceCoefficients)},define:function(i){Object.assign(this.spaces,i)},_getMatrix:function(i,e,t){return i.copy(this.spaces[e].toXYZ).multiply(this.spaces[t].fromXYZ)},_getDrawingBufferColorSpace:function(i){return this.spaces[i].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(i=this.workingColorSpace){return this.spaces[i].workingColorSpaceConfig.unpackColorSpace}};function Ei(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function rr(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}const tu=[.64,.33,.3,.6,.15,.06],nu=[.2126,.7152,.0722],iu=[.3127,.329],su=new rt().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),ru=new rt().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);ft.define({[mn]:{primaries:tu,whitePoint:iu,transfer:Na,toXYZ:su,fromXYZ:ru,luminanceCoefficients:nu,workingColorSpaceConfig:{unpackColorSpace:qt},outputColorSpaceConfig:{drawingBufferColorSpace:qt}},[qt]:{primaries:tu,whitePoint:iu,transfer:Rt,toXYZ:su,fromXYZ:ru,luminanceCoefficients:nu,outputColorSpaceConfig:{drawingBufferColorSpace:qt}}});let Ns;class Qm{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{Ns===void 0&&(Ns=oo("canvas")),Ns.width=e.width,Ns.height=e.height;const n=Ns.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=Ns}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=oo("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const s=n.getImageData(0,0,e.width,e.height),r=s.data;for(let o=0;o<r.length;o++)r[o]=Ei(r[o]/255)*255;return n.putImageData(s,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(Ei(t[n]/255)*255):t[n]=Ei(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let e0=0;class af{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:e0++}),this.uuid=zn(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},s=this.data;if(s!==null){let r;if(Array.isArray(s)){r=[];for(let o=0,a=s.length;o<a;o++)s[o].isDataTexture?r.push(nc(s[o].image)):r.push(nc(s[o]))}else r=nc(s);n.url=r}return t||(e.images[this.uuid]=n),n}}function nc(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?Qm.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let t0=0;class Qt extends Mr{constructor(e=Qt.DEFAULT_IMAGE,t=Qt.DEFAULT_MAPPING,n=qi,s=qi,r=Dn,o=bi,a=kn,c=Ai,l=Qt.DEFAULT_ANISOTROPY,h=Wi){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:t0++}),this.uuid=zn(),this.name="",this.source=new af(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=s,this.magFilter=r,this.minFilter=o,this.anisotropy=l,this.format=a,this.internalFormat=null,this.type=c,this.offset=new te(0,0),this.repeat=new te(1,1),this.center=new te(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new rt,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=h,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==Xd)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case ur:e.x=e.x-Math.floor(e.x);break;case qi:e.x=e.x<0?0:1;break;case Ma:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case ur:e.y=e.y-Math.floor(e.y);break;case qi:e.y=e.y<0?0:1;break;case Ma:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}Qt.DEFAULT_IMAGE=null;Qt.DEFAULT_MAPPING=Xd;Qt.DEFAULT_ANISOTROPY=1;class yt{constructor(e=0,t=0,n=0,s=1){yt.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=s}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,s){return this.x=e,this.y=t,this.z=n,this.w=s,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=this.w,o=e.elements;return this.x=o[0]*t+o[4]*n+o[8]*s+o[12]*r,this.y=o[1]*t+o[5]*n+o[9]*s+o[13]*r,this.z=o[2]*t+o[6]*n+o[10]*s+o[14]*r,this.w=o[3]*t+o[7]*n+o[11]*s+o[15]*r,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,s,r;const c=e.elements,l=c[0],h=c[4],u=c[8],d=c[1],f=c[5],m=c[9],_=c[2],g=c[6],p=c[10];if(Math.abs(h-d)<.01&&Math.abs(u-_)<.01&&Math.abs(m-g)<.01){if(Math.abs(h+d)<.1&&Math.abs(u+_)<.1&&Math.abs(m+g)<.1&&Math.abs(l+f+p-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const M=(l+1)/2,x=(f+1)/2,E=(p+1)/2,T=(h+d)/4,P=(u+_)/4,C=(m+g)/4;return M>x&&M>E?M<.01?(n=0,s=.707106781,r=.707106781):(n=Math.sqrt(M),s=T/n,r=P/n):x>E?x<.01?(n=.707106781,s=0,r=.707106781):(s=Math.sqrt(x),n=T/s,r=C/s):E<.01?(n=.707106781,s=.707106781,r=0):(r=Math.sqrt(E),n=P/r,s=C/r),this.set(n,s,r,t),this}let y=Math.sqrt((g-m)*(g-m)+(u-_)*(u-_)+(d-h)*(d-h));return Math.abs(y)<.001&&(y=1),this.x=(g-m)/y,this.y=(u-_)/y,this.z=(d-h)/y,this.w=Math.acos((l+f+p-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class n0 extends Mr{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new yt(0,0,e,t),this.scissorTest=!1,this.viewport=new yt(0,0,e,t);const s={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:Dn,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const r=new Qt(s,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);r.flipY=!1,r.generateMipmaps=n.generateMipmaps,r.internalFormat=n.internalFormat,this.textures=[];const o=n.count;for(let a=0;a<o;a++)this.textures[a]=r.clone(),this.textures[a].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let s=0,r=this.textures.length;s<r;s++)this.textures[s].image.width=e,this.textures[s].image.height=t,this.textures[s].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,s=e.textures.length;n<s;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new af(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Ts extends n0{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class cf extends Qt{constructor(e=null,t=1,n=1,s=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=pn,this.minFilter=pn,this.wrapR=qi,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class i0 extends Qt{constructor(e=null,t=1,n=1,s=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=pn,this.minFilter=pn,this.wrapR=qi,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class Gn{constructor(e=0,t=0,n=0,s=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=s}static slerpFlat(e,t,n,s,r,o,a){let c=n[s+0],l=n[s+1],h=n[s+2],u=n[s+3];const d=r[o+0],f=r[o+1],m=r[o+2],_=r[o+3];if(a===0){e[t+0]=c,e[t+1]=l,e[t+2]=h,e[t+3]=u;return}if(a===1){e[t+0]=d,e[t+1]=f,e[t+2]=m,e[t+3]=_;return}if(u!==_||c!==d||l!==f||h!==m){let g=1-a;const p=c*d+l*f+h*m+u*_,y=p>=0?1:-1,M=1-p*p;if(M>Number.EPSILON){const E=Math.sqrt(M),T=Math.atan2(E,p*y);g=Math.sin(g*T)/E,a=Math.sin(a*T)/E}const x=a*y;if(c=c*g+d*x,l=l*g+f*x,h=h*g+m*x,u=u*g+_*x,g===1-a){const E=1/Math.sqrt(c*c+l*l+h*h+u*u);c*=E,l*=E,h*=E,u*=E}}e[t]=c,e[t+1]=l,e[t+2]=h,e[t+3]=u}static multiplyQuaternionsFlat(e,t,n,s,r,o){const a=n[s],c=n[s+1],l=n[s+2],h=n[s+3],u=r[o],d=r[o+1],f=r[o+2],m=r[o+3];return e[t]=a*m+h*u+c*f-l*d,e[t+1]=c*m+h*d+l*u-a*f,e[t+2]=l*m+h*f+a*d-c*u,e[t+3]=h*m-a*u-c*d-l*f,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,s){return this._x=e,this._y=t,this._z=n,this._w=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,s=e._y,r=e._z,o=e._order,a=Math.cos,c=Math.sin,l=a(n/2),h=a(s/2),u=a(r/2),d=c(n/2),f=c(s/2),m=c(r/2);switch(o){case"XYZ":this._x=d*h*u+l*f*m,this._y=l*f*u-d*h*m,this._z=l*h*m+d*f*u,this._w=l*h*u-d*f*m;break;case"YXZ":this._x=d*h*u+l*f*m,this._y=l*f*u-d*h*m,this._z=l*h*m-d*f*u,this._w=l*h*u+d*f*m;break;case"ZXY":this._x=d*h*u-l*f*m,this._y=l*f*u+d*h*m,this._z=l*h*m+d*f*u,this._w=l*h*u-d*f*m;break;case"ZYX":this._x=d*h*u-l*f*m,this._y=l*f*u+d*h*m,this._z=l*h*m-d*f*u,this._w=l*h*u+d*f*m;break;case"YZX":this._x=d*h*u+l*f*m,this._y=l*f*u+d*h*m,this._z=l*h*m-d*f*u,this._w=l*h*u-d*f*m;break;case"XZY":this._x=d*h*u-l*f*m,this._y=l*f*u-d*h*m,this._z=l*h*m+d*f*u,this._w=l*h*u+d*f*m;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+o)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,s=Math.sin(n);return this._x=e.x*s,this._y=e.y*s,this._z=e.z*s,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],s=t[4],r=t[8],o=t[1],a=t[5],c=t[9],l=t[2],h=t[6],u=t[10],d=n+a+u;if(d>0){const f=.5/Math.sqrt(d+1);this._w=.25/f,this._x=(h-c)*f,this._y=(r-l)*f,this._z=(o-s)*f}else if(n>a&&n>u){const f=2*Math.sqrt(1+n-a-u);this._w=(h-c)/f,this._x=.25*f,this._y=(s+o)/f,this._z=(r+l)/f}else if(a>u){const f=2*Math.sqrt(1+a-n-u);this._w=(r-l)/f,this._x=(s+o)/f,this._y=.25*f,this._z=(c+h)/f}else{const f=2*Math.sqrt(1+u-n-a);this._w=(o-s)/f,this._x=(r+l)/f,this._y=(c+h)/f,this._z=.25*f}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Yt(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const s=Math.min(1,t/n);return this.slerp(e,s),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,s=e._y,r=e._z,o=e._w,a=t._x,c=t._y,l=t._z,h=t._w;return this._x=n*h+o*a+s*l-r*c,this._y=s*h+o*c+r*a-n*l,this._z=r*h+o*l+n*c-s*a,this._w=o*h-n*a-s*c-r*l,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,s=this._y,r=this._z,o=this._w;let a=o*e._w+n*e._x+s*e._y+r*e._z;if(a<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,a=-a):this.copy(e),a>=1)return this._w=o,this._x=n,this._y=s,this._z=r,this;const c=1-a*a;if(c<=Number.EPSILON){const f=1-t;return this._w=f*o+t*this._w,this._x=f*n+t*this._x,this._y=f*s+t*this._y,this._z=f*r+t*this._z,this.normalize(),this}const l=Math.sqrt(c),h=Math.atan2(l,a),u=Math.sin((1-t)*h)/l,d=Math.sin(t*h)/l;return this._w=o*u+this._w*d,this._x=n*u+this._x*d,this._y=s*u+this._y*d,this._z=r*u+this._z*d,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),s=Math.sqrt(1-n),r=Math.sqrt(n);return this.set(s*Math.sin(e),s*Math.cos(e),r*Math.sin(t),r*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class v{constructor(e=0,t=0,n=0){v.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(ou.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(ou.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6]*s,this.y=r[1]*t+r[4]*n+r[7]*s,this.z=r[2]*t+r[5]*n+r[8]*s,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=e.elements,o=1/(r[3]*t+r[7]*n+r[11]*s+r[15]);return this.x=(r[0]*t+r[4]*n+r[8]*s+r[12])*o,this.y=(r[1]*t+r[5]*n+r[9]*s+r[13])*o,this.z=(r[2]*t+r[6]*n+r[10]*s+r[14])*o,this}applyQuaternion(e){const t=this.x,n=this.y,s=this.z,r=e.x,o=e.y,a=e.z,c=e.w,l=2*(o*s-a*n),h=2*(a*t-r*s),u=2*(r*n-o*t);return this.x=t+c*l+o*u-a*h,this.y=n+c*h+a*l-r*u,this.z=s+c*u+r*h-o*l,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[4]*n+r[8]*s,this.y=r[1]*t+r[5]*n+r[9]*s,this.z=r[2]*t+r[6]*n+r[10]*s,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,s=e.y,r=e.z,o=t.x,a=t.y,c=t.z;return this.x=s*c-r*a,this.y=r*o-n*c,this.z=n*a-s*o,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return ic.copy(this).projectOnVector(e),this.sub(ic)}reflect(e){return this.sub(ic.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Yt(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,s=this.z-e.z;return t*t+n*n+s*s}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const s=Math.sin(t)*e;return this.x=s*Math.sin(n),this.y=Math.cos(t)*e,this.z=s*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),s=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=s,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const ic=new v,ou=new Gn;class tn{constructor(e=new v(1/0,1/0,1/0),t=new v(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(jn.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(jn.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=jn.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const r=n.getAttribute("position");if(t===!0&&r!==void 0&&e.isInstancedMesh!==!0)for(let o=0,a=r.count;o<a;o++)e.isMesh===!0?e.getVertexPosition(o,jn):jn.fromBufferAttribute(r,o),jn.applyMatrix4(e.matrixWorld),this.expandByPoint(jn);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),bo.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),bo.copy(n.boundingBox)),bo.applyMatrix4(e.matrixWorld),this.union(bo)}const s=e.children;for(let r=0,o=s.length;r<o;r++)this.expandByObject(s[r],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,jn),jn.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Ir),So.subVectors(this.max,Ir),Us.subVectors(e.a,Ir),Os.subVectors(e.b,Ir),Fs.subVectors(e.c,Ir),Ui.subVectors(Os,Us),Oi.subVectors(Fs,Os),rs.subVectors(Us,Fs);let t=[0,-Ui.z,Ui.y,0,-Oi.z,Oi.y,0,-rs.z,rs.y,Ui.z,0,-Ui.x,Oi.z,0,-Oi.x,rs.z,0,-rs.x,-Ui.y,Ui.x,0,-Oi.y,Oi.x,0,-rs.y,rs.x,0];return!sc(t,Us,Os,Fs,So)||(t=[1,0,0,0,1,0,0,0,1],!sc(t,Us,Os,Fs,So))?!1:(Eo.crossVectors(Ui,Oi),t=[Eo.x,Eo.y,Eo.z],sc(t,Us,Os,Fs,So))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,jn).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(jn).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(pi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),pi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),pi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),pi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),pi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),pi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),pi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),pi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(pi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const pi=[new v,new v,new v,new v,new v,new v,new v,new v],jn=new v,bo=new tn,Us=new v,Os=new v,Fs=new v,Ui=new v,Oi=new v,rs=new v,Ir=new v,So=new v,Eo=new v,os=new v;function sc(i,e,t,n,s){for(let r=0,o=i.length-3;r<=o;r+=3){os.fromArray(i,r);const a=s.x*Math.abs(os.x)+s.y*Math.abs(os.y)+s.z*Math.abs(os.z),c=e.dot(os),l=t.dot(os),h=n.dot(os);if(Math.max(-Math.max(c,l,h),Math.min(c,l,h))>a)return!1}return!0}const s0=new tn,Dr=new v,rc=new v;class ci{constructor(e=new v,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):s0.setFromPoints(e).getCenter(n);let s=0;for(let r=0,o=e.length;r<o;r++)s=Math.max(s,n.distanceToSquared(e[r]));return this.radius=Math.sqrt(s),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;Dr.subVectors(e,this.center);const t=Dr.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),s=(n-this.radius)*.5;this.center.addScaledVector(Dr,s/n),this.radius+=s}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(rc.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(Dr.copy(e.center).add(rc)),this.expandByPoint(Dr.copy(e.center).sub(rc))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const mi=new v,oc=new v,To=new v,Fi=new v,ac=new v,Ao=new v,cc=new v;class Ua{constructor(e=new v,t=new v(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,mi)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=mi.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(mi.copy(this.origin).addScaledVector(this.direction,t),mi.distanceToSquared(e))}distanceSqToSegment(e,t,n,s){oc.copy(e).add(t).multiplyScalar(.5),To.copy(t).sub(e).normalize(),Fi.copy(this.origin).sub(oc);const r=e.distanceTo(t)*.5,o=-this.direction.dot(To),a=Fi.dot(this.direction),c=-Fi.dot(To),l=Fi.lengthSq(),h=Math.abs(1-o*o);let u,d,f,m;if(h>0)if(u=o*c-a,d=o*a-c,m=r*h,u>=0)if(d>=-m)if(d<=m){const _=1/h;u*=_,d*=_,f=u*(u+o*d+2*a)+d*(o*u+d+2*c)+l}else d=r,u=Math.max(0,-(o*d+a)),f=-u*u+d*(d+2*c)+l;else d=-r,u=Math.max(0,-(o*d+a)),f=-u*u+d*(d+2*c)+l;else d<=-m?(u=Math.max(0,-(-o*r+a)),d=u>0?-r:Math.min(Math.max(-r,-c),r),f=-u*u+d*(d+2*c)+l):d<=m?(u=0,d=Math.min(Math.max(-r,-c),r),f=d*(d+2*c)+l):(u=Math.max(0,-(o*r+a)),d=u>0?r:Math.min(Math.max(-r,-c),r),f=-u*u+d*(d+2*c)+l);else d=o>0?-r:r,u=Math.max(0,-(o*d+a)),f=-u*u+d*(d+2*c)+l;return n&&n.copy(this.origin).addScaledVector(this.direction,u),s&&s.copy(oc).addScaledVector(To,d),f}intersectSphere(e,t){mi.subVectors(e.center,this.origin);const n=mi.dot(this.direction),s=mi.dot(mi)-n*n,r=e.radius*e.radius;if(s>r)return null;const o=Math.sqrt(r-s),a=n-o,c=n+o;return c<0?null:a<0?this.at(c,t):this.at(a,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,s,r,o,a,c;const l=1/this.direction.x,h=1/this.direction.y,u=1/this.direction.z,d=this.origin;return l>=0?(n=(e.min.x-d.x)*l,s=(e.max.x-d.x)*l):(n=(e.max.x-d.x)*l,s=(e.min.x-d.x)*l),h>=0?(r=(e.min.y-d.y)*h,o=(e.max.y-d.y)*h):(r=(e.max.y-d.y)*h,o=(e.min.y-d.y)*h),n>o||r>s||((r>n||isNaN(n))&&(n=r),(o<s||isNaN(s))&&(s=o),u>=0?(a=(e.min.z-d.z)*u,c=(e.max.z-d.z)*u):(a=(e.max.z-d.z)*u,c=(e.min.z-d.z)*u),n>c||a>s)||((a>n||n!==n)&&(n=a),(c<s||s!==s)&&(s=c),s<0)?null:this.at(n>=0?n:s,t)}intersectsBox(e){return this.intersectBox(e,mi)!==null}intersectTriangle(e,t,n,s,r){ac.subVectors(t,e),Ao.subVectors(n,e),cc.crossVectors(ac,Ao);let o=this.direction.dot(cc),a;if(o>0){if(s)return null;a=1}else if(o<0)a=-1,o=-o;else return null;Fi.subVectors(this.origin,e);const c=a*this.direction.dot(Ao.crossVectors(Fi,Ao));if(c<0)return null;const l=a*this.direction.dot(ac.cross(Fi));if(l<0||c+l>o)return null;const h=-a*Fi.dot(cc);return h<0?null:this.at(h/o,r)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Ae{constructor(e,t,n,s,r,o,a,c,l,h,u,d,f,m,_,g){Ae.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,o,a,c,l,h,u,d,f,m,_,g)}set(e,t,n,s,r,o,a,c,l,h,u,d,f,m,_,g){const p=this.elements;return p[0]=e,p[4]=t,p[8]=n,p[12]=s,p[1]=r,p[5]=o,p[9]=a,p[13]=c,p[2]=l,p[6]=h,p[10]=u,p[14]=d,p[3]=f,p[7]=m,p[11]=_,p[15]=g,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Ae().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,s=1/Bs.setFromMatrixColumn(e,0).length(),r=1/Bs.setFromMatrixColumn(e,1).length(),o=1/Bs.setFromMatrixColumn(e,2).length();return t[0]=n[0]*s,t[1]=n[1]*s,t[2]=n[2]*s,t[3]=0,t[4]=n[4]*r,t[5]=n[5]*r,t[6]=n[6]*r,t[7]=0,t[8]=n[8]*o,t[9]=n[9]*o,t[10]=n[10]*o,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,s=e.y,r=e.z,o=Math.cos(n),a=Math.sin(n),c=Math.cos(s),l=Math.sin(s),h=Math.cos(r),u=Math.sin(r);if(e.order==="XYZ"){const d=o*h,f=o*u,m=a*h,_=a*u;t[0]=c*h,t[4]=-c*u,t[8]=l,t[1]=f+m*l,t[5]=d-_*l,t[9]=-a*c,t[2]=_-d*l,t[6]=m+f*l,t[10]=o*c}else if(e.order==="YXZ"){const d=c*h,f=c*u,m=l*h,_=l*u;t[0]=d+_*a,t[4]=m*a-f,t[8]=o*l,t[1]=o*u,t[5]=o*h,t[9]=-a,t[2]=f*a-m,t[6]=_+d*a,t[10]=o*c}else if(e.order==="ZXY"){const d=c*h,f=c*u,m=l*h,_=l*u;t[0]=d-_*a,t[4]=-o*u,t[8]=m+f*a,t[1]=f+m*a,t[5]=o*h,t[9]=_-d*a,t[2]=-o*l,t[6]=a,t[10]=o*c}else if(e.order==="ZYX"){const d=o*h,f=o*u,m=a*h,_=a*u;t[0]=c*h,t[4]=m*l-f,t[8]=d*l+_,t[1]=c*u,t[5]=_*l+d,t[9]=f*l-m,t[2]=-l,t[6]=a*c,t[10]=o*c}else if(e.order==="YZX"){const d=o*c,f=o*l,m=a*c,_=a*l;t[0]=c*h,t[4]=_-d*u,t[8]=m*u+f,t[1]=u,t[5]=o*h,t[9]=-a*h,t[2]=-l*h,t[6]=f*u+m,t[10]=d-_*u}else if(e.order==="XZY"){const d=o*c,f=o*l,m=a*c,_=a*l;t[0]=c*h,t[4]=-u,t[8]=l*h,t[1]=d*u+_,t[5]=o*h,t[9]=f*u-m,t[2]=m*u-f,t[6]=a*h,t[10]=_*u+d}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(r0,e,o0)}lookAt(e,t,n){const s=this.elements;return Pn.subVectors(e,t),Pn.lengthSq()===0&&(Pn.z=1),Pn.normalize(),Bi.crossVectors(n,Pn),Bi.lengthSq()===0&&(Math.abs(n.z)===1?Pn.x+=1e-4:Pn.z+=1e-4,Pn.normalize(),Bi.crossVectors(n,Pn)),Bi.normalize(),Ro.crossVectors(Pn,Bi),s[0]=Bi.x,s[4]=Ro.x,s[8]=Pn.x,s[1]=Bi.y,s[5]=Ro.y,s[9]=Pn.y,s[2]=Bi.z,s[6]=Ro.z,s[10]=Pn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,o=n[0],a=n[4],c=n[8],l=n[12],h=n[1],u=n[5],d=n[9],f=n[13],m=n[2],_=n[6],g=n[10],p=n[14],y=n[3],M=n[7],x=n[11],E=n[15],T=s[0],P=s[4],C=s[8],b=s[12],w=s[1],L=s[5],F=s[9],O=s[13],k=s[2],K=s[6],X=s[10],j=s[14],V=s[3],oe=s[7],_e=s[11],Re=s[15];return r[0]=o*T+a*w+c*k+l*V,r[4]=o*P+a*L+c*K+l*oe,r[8]=o*C+a*F+c*X+l*_e,r[12]=o*b+a*O+c*j+l*Re,r[1]=h*T+u*w+d*k+f*V,r[5]=h*P+u*L+d*K+f*oe,r[9]=h*C+u*F+d*X+f*_e,r[13]=h*b+u*O+d*j+f*Re,r[2]=m*T+_*w+g*k+p*V,r[6]=m*P+_*L+g*K+p*oe,r[10]=m*C+_*F+g*X+p*_e,r[14]=m*b+_*O+g*j+p*Re,r[3]=y*T+M*w+x*k+E*V,r[7]=y*P+M*L+x*K+E*oe,r[11]=y*C+M*F+x*X+E*_e,r[15]=y*b+M*O+x*j+E*Re,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],s=e[8],r=e[12],o=e[1],a=e[5],c=e[9],l=e[13],h=e[2],u=e[6],d=e[10],f=e[14],m=e[3],_=e[7],g=e[11],p=e[15];return m*(+r*c*u-s*l*u-r*a*d+n*l*d+s*a*f-n*c*f)+_*(+t*c*f-t*l*d+r*o*d-s*o*f+s*l*h-r*c*h)+g*(+t*l*u-t*a*f-r*o*u+n*o*f+r*a*h-n*l*h)+p*(-s*a*h-t*c*u+t*a*d+s*o*u-n*o*d+n*c*h)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const s=this.elements;return e.isVector3?(s[12]=e.x,s[13]=e.y,s[14]=e.z):(s[12]=e,s[13]=t,s[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],c=e[6],l=e[7],h=e[8],u=e[9],d=e[10],f=e[11],m=e[12],_=e[13],g=e[14],p=e[15],y=u*g*l-_*d*l+_*c*f-a*g*f-u*c*p+a*d*p,M=m*d*l-h*g*l-m*c*f+o*g*f+h*c*p-o*d*p,x=h*_*l-m*u*l+m*a*f-o*_*f-h*a*p+o*u*p,E=m*u*c-h*_*c-m*a*d+o*_*d+h*a*g-o*u*g,T=t*y+n*M+s*x+r*E;if(T===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const P=1/T;return e[0]=y*P,e[1]=(_*d*r-u*g*r-_*s*f+n*g*f+u*s*p-n*d*p)*P,e[2]=(a*g*r-_*c*r+_*s*l-n*g*l-a*s*p+n*c*p)*P,e[3]=(u*c*r-a*d*r-u*s*l+n*d*l+a*s*f-n*c*f)*P,e[4]=M*P,e[5]=(h*g*r-m*d*r+m*s*f-t*g*f-h*s*p+t*d*p)*P,e[6]=(m*c*r-o*g*r-m*s*l+t*g*l+o*s*p-t*c*p)*P,e[7]=(o*d*r-h*c*r+h*s*l-t*d*l-o*s*f+t*c*f)*P,e[8]=x*P,e[9]=(m*u*r-h*_*r-m*n*f+t*_*f+h*n*p-t*u*p)*P,e[10]=(o*_*r-m*a*r+m*n*l-t*_*l-o*n*p+t*a*p)*P,e[11]=(h*a*r-o*u*r-h*n*l+t*u*l+o*n*f-t*a*f)*P,e[12]=E*P,e[13]=(h*_*s-m*u*s+m*n*d-t*_*d-h*n*g+t*u*g)*P,e[14]=(m*a*s-o*_*s-m*n*c+t*_*c+o*n*g-t*a*g)*P,e[15]=(o*u*s-h*a*s+h*n*c-t*u*c-o*n*d+t*a*d)*P,this}scale(e){const t=this.elements,n=e.x,s=e.y,r=e.z;return t[0]*=n,t[4]*=s,t[8]*=r,t[1]*=n,t[5]*=s,t[9]*=r,t[2]*=n,t[6]*=s,t[10]*=r,t[3]*=n,t[7]*=s,t[11]*=r,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],s=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,s))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),s=Math.sin(t),r=1-n,o=e.x,a=e.y,c=e.z,l=r*o,h=r*a;return this.set(l*o+n,l*a-s*c,l*c+s*a,0,l*a+s*c,h*a+n,h*c-s*o,0,l*c-s*a,h*c+s*o,r*c*c+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,s,r,o){return this.set(1,n,r,0,e,1,o,0,t,s,1,0,0,0,0,1),this}compose(e,t,n){const s=this.elements,r=t._x,o=t._y,a=t._z,c=t._w,l=r+r,h=o+o,u=a+a,d=r*l,f=r*h,m=r*u,_=o*h,g=o*u,p=a*u,y=c*l,M=c*h,x=c*u,E=n.x,T=n.y,P=n.z;return s[0]=(1-(_+p))*E,s[1]=(f+x)*E,s[2]=(m-M)*E,s[3]=0,s[4]=(f-x)*T,s[5]=(1-(d+p))*T,s[6]=(g+y)*T,s[7]=0,s[8]=(m+M)*P,s[9]=(g-y)*P,s[10]=(1-(d+_))*P,s[11]=0,s[12]=e.x,s[13]=e.y,s[14]=e.z,s[15]=1,this}decompose(e,t,n){const s=this.elements;let r=Bs.set(s[0],s[1],s[2]).length();const o=Bs.set(s[4],s[5],s[6]).length(),a=Bs.set(s[8],s[9],s[10]).length();this.determinant()<0&&(r=-r),e.x=s[12],e.y=s[13],e.z=s[14],$n.copy(this);const l=1/r,h=1/o,u=1/a;return $n.elements[0]*=l,$n.elements[1]*=l,$n.elements[2]*=l,$n.elements[4]*=h,$n.elements[5]*=h,$n.elements[6]*=h,$n.elements[8]*=u,$n.elements[9]*=u,$n.elements[10]*=u,t.setFromRotationMatrix($n),n.x=r,n.y=o,n.z=a,this}makePerspective(e,t,n,s,r,o,a=Si){const c=this.elements,l=2*r/(t-e),h=2*r/(n-s),u=(t+e)/(t-e),d=(n+s)/(n-s);let f,m;if(a===Si)f=-(o+r)/(o-r),m=-2*o*r/(o-r);else if(a===wa)f=-o/(o-r),m=-o*r/(o-r);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+a);return c[0]=l,c[4]=0,c[8]=u,c[12]=0,c[1]=0,c[5]=h,c[9]=d,c[13]=0,c[2]=0,c[6]=0,c[10]=f,c[14]=m,c[3]=0,c[7]=0,c[11]=-1,c[15]=0,this}makeOrthographic(e,t,n,s,r,o,a=Si){const c=this.elements,l=1/(t-e),h=1/(n-s),u=1/(o-r),d=(t+e)*l,f=(n+s)*h;let m,_;if(a===Si)m=(o+r)*u,_=-2*u;else if(a===wa)m=r*u,_=-1*u;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+a);return c[0]=2*l,c[4]=0,c[8]=0,c[12]=-d,c[1]=0,c[5]=2*h,c[9]=0,c[13]=-f,c[2]=0,c[6]=0,c[10]=_,c[14]=-m,c[3]=0,c[7]=0,c[11]=0,c[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<16;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const Bs=new v,$n=new Ae,r0=new v(0,0,0),o0=new v(1,1,1),Bi=new v,Ro=new v,Pn=new v,au=new Ae,cu=new Gn;class wn{constructor(e=0,t=0,n=0,s=wn.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=s}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,s=this._order){return this._x=e,this._y=t,this._z=n,this._order=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const s=e.elements,r=s[0],o=s[4],a=s[8],c=s[1],l=s[5],h=s[9],u=s[2],d=s[6],f=s[10];switch(t){case"XYZ":this._y=Math.asin(Yt(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(-h,f),this._z=Math.atan2(-o,r)):(this._x=Math.atan2(d,l),this._z=0);break;case"YXZ":this._x=Math.asin(-Yt(h,-1,1)),Math.abs(h)<.9999999?(this._y=Math.atan2(a,f),this._z=Math.atan2(c,l)):(this._y=Math.atan2(-u,r),this._z=0);break;case"ZXY":this._x=Math.asin(Yt(d,-1,1)),Math.abs(d)<.9999999?(this._y=Math.atan2(-u,f),this._z=Math.atan2(-o,l)):(this._y=0,this._z=Math.atan2(c,r));break;case"ZYX":this._y=Math.asin(-Yt(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(d,f),this._z=Math.atan2(c,r)):(this._x=0,this._z=Math.atan2(-o,l));break;case"YZX":this._z=Math.asin(Yt(c,-1,1)),Math.abs(c)<.9999999?(this._x=Math.atan2(-h,l),this._y=Math.atan2(-u,r)):(this._x=0,this._y=Math.atan2(a,f));break;case"XZY":this._z=Math.asin(-Yt(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(d,l),this._y=Math.atan2(a,r)):(this._x=Math.atan2(-h,f),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return au.makeRotationFromQuaternion(e),this.setFromRotationMatrix(au,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return cu.setFromEuler(this),this.setFromQuaternion(cu,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}wn.DEFAULT_ORDER="XYZ";class lf{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let a0=0;const lu=new v,ks=new Gn,gi=new Ae,Co=new v,Nr=new v,c0=new v,l0=new Gn,hu=new v(1,0,0),uu=new v(0,1,0),du=new v(0,0,1),fu={type:"added"},h0={type:"removed"},zs={type:"childadded",child:null},lc={type:"childremoved",child:null};class Nt extends Mr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:a0++}),this.uuid=zn(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=Nt.DEFAULT_UP.clone();const e=new v,t=new wn,n=new Gn,s=new v(1,1,1);function r(){n.setFromEuler(t,!1)}function o(){t.setFromQuaternion(n,void 0,!1)}t._onChange(r),n._onChange(o),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:s},modelViewMatrix:{value:new Ae},normalMatrix:{value:new rt}}),this.matrix=new Ae,this.matrixWorld=new Ae,this.matrixAutoUpdate=Nt.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=Nt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new lf,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return ks.setFromAxisAngle(e,t),this.quaternion.multiply(ks),this}rotateOnWorldAxis(e,t){return ks.setFromAxisAngle(e,t),this.quaternion.premultiply(ks),this}rotateX(e){return this.rotateOnAxis(hu,e)}rotateY(e){return this.rotateOnAxis(uu,e)}rotateZ(e){return this.rotateOnAxis(du,e)}translateOnAxis(e,t){return lu.copy(e).applyQuaternion(this.quaternion),this.position.add(lu.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(hu,e)}translateY(e){return this.translateOnAxis(uu,e)}translateZ(e){return this.translateOnAxis(du,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(gi.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?Co.copy(e):Co.set(e,t,n);const s=this.parent;this.updateWorldMatrix(!0,!1),Nr.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?gi.lookAt(Nr,Co,this.up):gi.lookAt(Co,Nr,this.up),this.quaternion.setFromRotationMatrix(gi),s&&(gi.extractRotation(s.matrixWorld),ks.setFromRotationMatrix(gi),this.quaternion.premultiply(ks.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(fu),zs.child=e,this.dispatchEvent(zs),zs.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(h0),lc.child=e,this.dispatchEvent(lc),lc.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),gi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),gi.multiply(e.parent.matrixWorld)),e.applyMatrix4(gi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(fu),zs.child=e,this.dispatchEvent(zs),zs.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,s=this.children.length;n<s;n++){const o=this.children[n].getObjectByProperty(e,t);if(o!==void 0)return o}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const s=this.children;for(let r=0,o=s.length;r<o;r++)s[r].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Nr,e,c0),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(Nr,l0,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const s=this.children;for(let r=0,o=s.length;r<o;r++)s[r].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const s={};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.castShadow===!0&&(s.castShadow=!0),this.receiveShadow===!0&&(s.receiveShadow=!0),this.visible===!1&&(s.visible=!1),this.frustumCulled===!1&&(s.frustumCulled=!1),this.renderOrder!==0&&(s.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(s.userData=this.userData),s.layers=this.layers.mask,s.matrix=this.matrix.toArray(),s.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(s.matrixAutoUpdate=!1),this.isInstancedMesh&&(s.type="InstancedMesh",s.count=this.count,s.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(s.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(s.type="BatchedMesh",s.perObjectFrustumCulled=this.perObjectFrustumCulled,s.sortObjects=this.sortObjects,s.drawRanges=this._drawRanges,s.reservedRanges=this._reservedRanges,s.visibility=this._visibility,s.active=this._active,s.bounds=this._bounds.map(a=>({boxInitialized:a.boxInitialized,boxMin:a.box.min.toArray(),boxMax:a.box.max.toArray(),sphereInitialized:a.sphereInitialized,sphereRadius:a.sphere.radius,sphereCenter:a.sphere.center.toArray()})),s.maxInstanceCount=this._maxInstanceCount,s.maxVertexCount=this._maxVertexCount,s.maxIndexCount=this._maxIndexCount,s.geometryInitialized=this._geometryInitialized,s.geometryCount=this._geometryCount,s.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(s.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(s.boundingSphere={center:s.boundingSphere.center.toArray(),radius:s.boundingSphere.radius}),this.boundingBox!==null&&(s.boundingBox={min:s.boundingBox.min.toArray(),max:s.boundingBox.max.toArray()}));function r(a,c){return a[c.uuid]===void 0&&(a[c.uuid]=c.toJSON(e)),c.uuid}if(this.isScene)this.background&&(this.background.isColor?s.background=this.background.toJSON():this.background.isTexture&&(s.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(s.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){s.geometry=r(e.geometries,this.geometry);const a=this.geometry.parameters;if(a!==void 0&&a.shapes!==void 0){const c=a.shapes;if(Array.isArray(c))for(let l=0,h=c.length;l<h;l++){const u=c[l];r(e.shapes,u)}else r(e.shapes,c)}}if(this.isSkinnedMesh&&(s.bindMode=this.bindMode,s.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(r(e.skeletons,this.skeleton),s.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const a=[];for(let c=0,l=this.material.length;c<l;c++)a.push(r(e.materials,this.material[c]));s.material=a}else s.material=r(e.materials,this.material);if(this.children.length>0){s.children=[];for(let a=0;a<this.children.length;a++)s.children.push(this.children[a].toJSON(e).object)}if(this.animations.length>0){s.animations=[];for(let a=0;a<this.animations.length;a++){const c=this.animations[a];s.animations.push(r(e.animations,c))}}if(t){const a=o(e.geometries),c=o(e.materials),l=o(e.textures),h=o(e.images),u=o(e.shapes),d=o(e.skeletons),f=o(e.animations),m=o(e.nodes);a.length>0&&(n.geometries=a),c.length>0&&(n.materials=c),l.length>0&&(n.textures=l),h.length>0&&(n.images=h),u.length>0&&(n.shapes=u),d.length>0&&(n.skeletons=d),f.length>0&&(n.animations=f),m.length>0&&(n.nodes=m)}return n.object=s,n;function o(a){const c=[];for(const l in a){const h=a[l];delete h.metadata,c.push(h)}return c}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const s=e.children[n];this.add(s.clone())}return this}}Nt.DEFAULT_UP=new v(0,1,0);Nt.DEFAULT_MATRIX_AUTO_UPDATE=!0;Nt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const Yn=new v,_i=new v,hc=new v,xi=new v,Hs=new v,Gs=new v,pu=new v,uc=new v,dc=new v,fc=new v,pc=new yt,mc=new yt,gc=new yt;class Bn{constructor(e=new v,t=new v,n=new v){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,s){s.subVectors(n,t),Yn.subVectors(e,t),s.cross(Yn);const r=s.lengthSq();return r>0?s.multiplyScalar(1/Math.sqrt(r)):s.set(0,0,0)}static getBarycoord(e,t,n,s,r){Yn.subVectors(s,t),_i.subVectors(n,t),hc.subVectors(e,t);const o=Yn.dot(Yn),a=Yn.dot(_i),c=Yn.dot(hc),l=_i.dot(_i),h=_i.dot(hc),u=o*l-a*a;if(u===0)return r.set(0,0,0),null;const d=1/u,f=(l*c-a*h)*d,m=(o*h-a*c)*d;return r.set(1-f-m,m,f)}static containsPoint(e,t,n,s){return this.getBarycoord(e,t,n,s,xi)===null?!1:xi.x>=0&&xi.y>=0&&xi.x+xi.y<=1}static getInterpolation(e,t,n,s,r,o,a,c){return this.getBarycoord(e,t,n,s,xi)===null?(c.x=0,c.y=0,"z"in c&&(c.z=0),"w"in c&&(c.w=0),null):(c.setScalar(0),c.addScaledVector(r,xi.x),c.addScaledVector(o,xi.y),c.addScaledVector(a,xi.z),c)}static getInterpolatedAttribute(e,t,n,s,r,o){return pc.setScalar(0),mc.setScalar(0),gc.setScalar(0),pc.fromBufferAttribute(e,t),mc.fromBufferAttribute(e,n),gc.fromBufferAttribute(e,s),o.setScalar(0),o.addScaledVector(pc,r.x),o.addScaledVector(mc,r.y),o.addScaledVector(gc,r.z),o}static isFrontFacing(e,t,n,s){return Yn.subVectors(n,t),_i.subVectors(e,t),Yn.cross(_i).dot(s)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,s){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[s]),this}setFromAttributeAndIndices(e,t,n,s){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,s),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return Yn.subVectors(this.c,this.b),_i.subVectors(this.a,this.b),Yn.cross(_i).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Bn.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Bn.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,s,r){return Bn.getInterpolation(e,this.a,this.b,this.c,t,n,s,r)}containsPoint(e){return Bn.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Bn.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,s=this.b,r=this.c;let o,a;Hs.subVectors(s,n),Gs.subVectors(r,n),uc.subVectors(e,n);const c=Hs.dot(uc),l=Gs.dot(uc);if(c<=0&&l<=0)return t.copy(n);dc.subVectors(e,s);const h=Hs.dot(dc),u=Gs.dot(dc);if(h>=0&&u<=h)return t.copy(s);const d=c*u-h*l;if(d<=0&&c>=0&&h<=0)return o=c/(c-h),t.copy(n).addScaledVector(Hs,o);fc.subVectors(e,r);const f=Hs.dot(fc),m=Gs.dot(fc);if(m>=0&&f<=m)return t.copy(r);const _=f*l-c*m;if(_<=0&&l>=0&&m<=0)return a=l/(l-m),t.copy(n).addScaledVector(Gs,a);const g=h*m-f*u;if(g<=0&&u-h>=0&&f-m>=0)return pu.subVectors(r,s),a=(u-h)/(u-h+(f-m)),t.copy(s).addScaledVector(pu,a);const p=1/(g+_+d);return o=_*p,a=d*p,t.copy(n).addScaledVector(Hs,o).addScaledVector(Gs,a)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const hf={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},ki={h:0,s:0,l:0},Po={h:0,s:0,l:0};function _c(i,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?i+(e-i)*6*t:t<1/2?e:t<2/3?i+(e-i)*6*(2/3-t):i}class Ve{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const s=e;s&&s.isColor?this.copy(s):typeof s=="number"?this.setHex(s):typeof s=="string"&&this.setStyle(s)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=qt){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,ft.toWorkingColorSpace(this,t),this}setRGB(e,t,n,s=ft.workingColorSpace){return this.r=e,this.g=t,this.b=n,ft.toWorkingColorSpace(this,s),this}setHSL(e,t,n,s=ft.workingColorSpace){if(e=ch(e,1),t=Yt(t,0,1),n=Yt(n,0,1),t===0)this.r=this.g=this.b=n;else{const r=n<=.5?n*(1+t):n+t-n*t,o=2*n-r;this.r=_c(o,r,e+1/3),this.g=_c(o,r,e),this.b=_c(o,r,e-1/3)}return ft.toWorkingColorSpace(this,s),this}setStyle(e,t=qt){function n(r){r!==void 0&&parseFloat(r)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let s;if(s=/^(\w+)\(([^\)]*)\)/.exec(e)){let r;const o=s[1],a=s[2];switch(o){case"rgb":case"rgba":if(r=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setRGB(Math.min(255,parseInt(r[1],10))/255,Math.min(255,parseInt(r[2],10))/255,Math.min(255,parseInt(r[3],10))/255,t);if(r=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setRGB(Math.min(100,parseInt(r[1],10))/100,Math.min(100,parseInt(r[2],10))/100,Math.min(100,parseInt(r[3],10))/100,t);break;case"hsl":case"hsla":if(r=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setHSL(parseFloat(r[1])/360,parseFloat(r[2])/100,parseFloat(r[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(s=/^\#([A-Fa-f\d]+)$/.exec(e)){const r=s[1],o=r.length;if(o===3)return this.setRGB(parseInt(r.charAt(0),16)/15,parseInt(r.charAt(1),16)/15,parseInt(r.charAt(2),16)/15,t);if(o===6)return this.setHex(parseInt(r,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=qt){const n=hf[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Ei(e.r),this.g=Ei(e.g),this.b=Ei(e.b),this}copyLinearToSRGB(e){return this.r=rr(e.r),this.g=rr(e.g),this.b=rr(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=qt){return ft.fromWorkingColorSpace(cn.copy(this),e),Math.round(Yt(cn.r*255,0,255))*65536+Math.round(Yt(cn.g*255,0,255))*256+Math.round(Yt(cn.b*255,0,255))}getHexString(e=qt){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=ft.workingColorSpace){ft.fromWorkingColorSpace(cn.copy(this),t);const n=cn.r,s=cn.g,r=cn.b,o=Math.max(n,s,r),a=Math.min(n,s,r);let c,l;const h=(a+o)/2;if(a===o)c=0,l=0;else{const u=o-a;switch(l=h<=.5?u/(o+a):u/(2-o-a),o){case n:c=(s-r)/u+(s<r?6:0);break;case s:c=(r-n)/u+2;break;case r:c=(n-s)/u+4;break}c/=6}return e.h=c,e.s=l,e.l=h,e}getRGB(e,t=ft.workingColorSpace){return ft.fromWorkingColorSpace(cn.copy(this),t),e.r=cn.r,e.g=cn.g,e.b=cn.b,e}getStyle(e=qt){ft.fromWorkingColorSpace(cn.copy(this),e);const t=cn.r,n=cn.g,s=cn.b;return e!==qt?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${s.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(s*255)})`}offsetHSL(e,t,n){return this.getHSL(ki),this.setHSL(ki.h+e,ki.s+t,ki.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(ki),e.getHSL(Po);const n=Zr(ki.h,Po.h,t),s=Zr(ki.s,Po.s,t),r=Zr(ki.l,Po.l,t);return this.setHSL(n,s,r),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,s=this.b,r=e.elements;return this.r=r[0]*t+r[3]*n+r[6]*s,this.g=r[1]*t+r[4]*n+r[7]*s,this.b=r[2]*t+r[5]*n+r[8]*s,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const cn=new Ve;Ve.NAMES=hf;let u0=0;class ri extends Mr{static get type(){return"Material"}get type(){return this.constructor.type}set type(e){}constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:u0++}),this.uuid=zn(),this.name="",this.blending=nr,this.side=Ti,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=tl,this.blendDst=nl,this.blendEquation=vs,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new Ve(0,0,0),this.blendAlpha=0,this.depthFunc=cr,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Zh,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Ds,this.stencilZFail=Ds,this.stencilZPass=Ds,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const s=this[t];if(s===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}s&&s.isColor?s.set(n):s&&s.isVector3&&n&&n.isVector3?s.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==nr&&(n.blending=this.blending),this.side!==Ti&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==tl&&(n.blendSrc=this.blendSrc),this.blendDst!==nl&&(n.blendDst=this.blendDst),this.blendEquation!==vs&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==cr&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Zh&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Ds&&(n.stencilFail=this.stencilFail),this.stencilZFail!==Ds&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==Ds&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function s(r){const o=[];for(const a in r){const c=r[a];delete c.metadata,o.push(c)}return o}if(t){const r=s(e.textures),o=s(e.images);r.length>0&&(n.textures=r),o.length>0&&(n.images=o)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const s=t.length;n=new Array(s);for(let r=0;r!==s;++r)n[r]=t[r].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class fn extends ri{static get type(){return"MeshBasicMaterial"}constructor(e){super(),this.isMeshBasicMaterial=!0,this.color=new Ve(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new wn,this.combine=Wd,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const jt=new v,Lo=new te;class en{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=kl,this.updateRanges=[],this.gpuType=Jn,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let s=0,r=this.itemSize;s<r;s++)this.array[e+s]=t.array[n+s];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)Lo.fromBufferAttribute(this,t),Lo.applyMatrix3(e),this.setXY(t,Lo.x,Lo.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)jt.fromBufferAttribute(this,t),jt.applyMatrix3(e),this.setXYZ(t,jt.x,jt.y,jt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)jt.fromBufferAttribute(this,t),jt.applyMatrix4(e),this.setXYZ(t,jt.x,jt.y,jt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)jt.fromBufferAttribute(this,t),jt.applyNormalMatrix(e),this.setXYZ(t,jt.x,jt.y,jt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)jt.fromBufferAttribute(this,t),jt.transformDirection(e),this.setXYZ(t,jt.x,jt.y,jt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=Zn(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Tt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=Zn(t,this.array)),t}setX(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=Zn(t,this.array)),t}setY(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=Zn(t,this.array)),t}setZ(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=Zn(t,this.array)),t}setW(e,t){return this.normalized&&(t=Tt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,s){return e*=this.itemSize,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),s=Tt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e*=this.itemSize,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),s=Tt(s,this.array),r=Tt(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this.array[e+3]=r,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==kl&&(e.usage=this.usage),e}}class lh extends en{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class uf extends en{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class ct extends en{constructor(e,t,n){super(new Float32Array(e),t,n)}}let d0=0;const On=new Ae,xc=new Nt,Vs=new v,Ln=new tn,Ur=new tn,Jt=new v;class Gt extends Mr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:d0++}),this.uuid=zn(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(of(e)?uf:lh)(e,1):this.index=e,this}setIndirect(e){return this.indirect=e,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const r=new rt().getNormalMatrix(e);n.applyNormalMatrix(r),n.needsUpdate=!0}const s=this.attributes.tangent;return s!==void 0&&(s.transformDirection(e),s.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return On.makeRotationFromQuaternion(e),this.applyMatrix4(On),this}rotateX(e){return On.makeRotationX(e),this.applyMatrix4(On),this}rotateY(e){return On.makeRotationY(e),this.applyMatrix4(On),this}rotateZ(e){return On.makeRotationZ(e),this.applyMatrix4(On),this}translate(e,t,n){return On.makeTranslation(e,t,n),this.applyMatrix4(On),this}scale(e,t,n){return On.makeScale(e,t,n),this.applyMatrix4(On),this}lookAt(e){return xc.lookAt(e),xc.updateMatrix(),this.applyMatrix4(xc.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Vs).negate(),this.translate(Vs.x,Vs.y,Vs.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const n=[];for(let s=0,r=e.length;s<r;s++){const o=e[s];n.push(o.x,o.y,o.z||0)}this.setAttribute("position",new ct(n,3))}else{for(let n=0,s=t.count;n<s;n++){const r=e[n];t.setXYZ(n,r.x,r.y,r.z||0)}e.length>t.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new tn);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new v(-1/0,-1/0,-1/0),new v(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,s=t.length;n<s;n++){const r=t[n];Ln.setFromBufferAttribute(r),this.morphTargetsRelative?(Jt.addVectors(this.boundingBox.min,Ln.min),this.boundingBox.expandByPoint(Jt),Jt.addVectors(this.boundingBox.max,Ln.max),this.boundingBox.expandByPoint(Jt)):(this.boundingBox.expandByPoint(Ln.min),this.boundingBox.expandByPoint(Ln.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new ci);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new v,1/0);return}if(e){const n=this.boundingSphere.center;if(Ln.setFromBufferAttribute(e),t)for(let r=0,o=t.length;r<o;r++){const a=t[r];Ur.setFromBufferAttribute(a),this.morphTargetsRelative?(Jt.addVectors(Ln.min,Ur.min),Ln.expandByPoint(Jt),Jt.addVectors(Ln.max,Ur.max),Ln.expandByPoint(Jt)):(Ln.expandByPoint(Ur.min),Ln.expandByPoint(Ur.max))}Ln.getCenter(n);let s=0;for(let r=0,o=e.count;r<o;r++)Jt.fromBufferAttribute(e,r),s=Math.max(s,n.distanceToSquared(Jt));if(t)for(let r=0,o=t.length;r<o;r++){const a=t[r],c=this.morphTargetsRelative;for(let l=0,h=a.count;l<h;l++)Jt.fromBufferAttribute(a,l),c&&(Vs.fromBufferAttribute(e,l),Jt.add(Vs)),s=Math.max(s,n.distanceToSquared(Jt))}this.boundingSphere.radius=Math.sqrt(s),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,s=t.normal,r=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new en(new Float32Array(4*n.count),4));const o=this.getAttribute("tangent"),a=[],c=[];for(let C=0;C<n.count;C++)a[C]=new v,c[C]=new v;const l=new v,h=new v,u=new v,d=new te,f=new te,m=new te,_=new v,g=new v;function p(C,b,w){l.fromBufferAttribute(n,C),h.fromBufferAttribute(n,b),u.fromBufferAttribute(n,w),d.fromBufferAttribute(r,C),f.fromBufferAttribute(r,b),m.fromBufferAttribute(r,w),h.sub(l),u.sub(l),f.sub(d),m.sub(d);const L=1/(f.x*m.y-m.x*f.y);isFinite(L)&&(_.copy(h).multiplyScalar(m.y).addScaledVector(u,-f.y).multiplyScalar(L),g.copy(u).multiplyScalar(f.x).addScaledVector(h,-m.x).multiplyScalar(L),a[C].add(_),a[b].add(_),a[w].add(_),c[C].add(g),c[b].add(g),c[w].add(g))}let y=this.groups;y.length===0&&(y=[{start:0,count:e.count}]);for(let C=0,b=y.length;C<b;++C){const w=y[C],L=w.start,F=w.count;for(let O=L,k=L+F;O<k;O+=3)p(e.getX(O+0),e.getX(O+1),e.getX(O+2))}const M=new v,x=new v,E=new v,T=new v;function P(C){E.fromBufferAttribute(s,C),T.copy(E);const b=a[C];M.copy(b),M.sub(E.multiplyScalar(E.dot(b))).normalize(),x.crossVectors(T,b);const L=x.dot(c[C])<0?-1:1;o.setXYZW(C,M.x,M.y,M.z,L)}for(let C=0,b=y.length;C<b;++C){const w=y[C],L=w.start,F=w.count;for(let O=L,k=L+F;O<k;O+=3)P(e.getX(O+0)),P(e.getX(O+1)),P(e.getX(O+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new en(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let d=0,f=n.count;d<f;d++)n.setXYZ(d,0,0,0);const s=new v,r=new v,o=new v,a=new v,c=new v,l=new v,h=new v,u=new v;if(e)for(let d=0,f=e.count;d<f;d+=3){const m=e.getX(d+0),_=e.getX(d+1),g=e.getX(d+2);s.fromBufferAttribute(t,m),r.fromBufferAttribute(t,_),o.fromBufferAttribute(t,g),h.subVectors(o,r),u.subVectors(s,r),h.cross(u),a.fromBufferAttribute(n,m),c.fromBufferAttribute(n,_),l.fromBufferAttribute(n,g),a.add(h),c.add(h),l.add(h),n.setXYZ(m,a.x,a.y,a.z),n.setXYZ(_,c.x,c.y,c.z),n.setXYZ(g,l.x,l.y,l.z)}else for(let d=0,f=t.count;d<f;d+=3)s.fromBufferAttribute(t,d+0),r.fromBufferAttribute(t,d+1),o.fromBufferAttribute(t,d+2),h.subVectors(o,r),u.subVectors(s,r),h.cross(u),n.setXYZ(d+0,h.x,h.y,h.z),n.setXYZ(d+1,h.x,h.y,h.z),n.setXYZ(d+2,h.x,h.y,h.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)Jt.fromBufferAttribute(e,t),Jt.normalize(),e.setXYZ(t,Jt.x,Jt.y,Jt.z)}toNonIndexed(){function e(a,c){const l=a.array,h=a.itemSize,u=a.normalized,d=new l.constructor(c.length*h);let f=0,m=0;for(let _=0,g=c.length;_<g;_++){a.isInterleavedBufferAttribute?f=c[_]*a.data.stride+a.offset:f=c[_]*h;for(let p=0;p<h;p++)d[m++]=l[f++]}return new en(d,h,u)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new Gt,n=this.index.array,s=this.attributes;for(const a in s){const c=s[a],l=e(c,n);t.setAttribute(a,l)}const r=this.morphAttributes;for(const a in r){const c=[],l=r[a];for(let h=0,u=l.length;h<u;h++){const d=l[h],f=e(d,n);c.push(f)}t.morphAttributes[a]=c}t.morphTargetsRelative=this.morphTargetsRelative;const o=this.groups;for(let a=0,c=o.length;a<c;a++){const l=o[a];t.addGroup(l.start,l.count,l.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const c=this.parameters;for(const l in c)c[l]!==void 0&&(e[l]=c[l]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const c in n){const l=n[c];e.data.attributes[c]=l.toJSON(e.data)}const s={};let r=!1;for(const c in this.morphAttributes){const l=this.morphAttributes[c],h=[];for(let u=0,d=l.length;u<d;u++){const f=l[u];h.push(f.toJSON(e.data))}h.length>0&&(s[c]=h,r=!0)}r&&(e.data.morphAttributes=s,e.data.morphTargetsRelative=this.morphTargetsRelative);const o=this.groups;o.length>0&&(e.data.groups=JSON.parse(JSON.stringify(o)));const a=this.boundingSphere;return a!==null&&(e.data.boundingSphere={center:a.center.toArray(),radius:a.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const s=e.attributes;for(const l in s){const h=s[l];this.setAttribute(l,h.clone(t))}const r=e.morphAttributes;for(const l in r){const h=[],u=r[l];for(let d=0,f=u.length;d<f;d++)h.push(u[d].clone(t));this.morphAttributes[l]=h}this.morphTargetsRelative=e.morphTargetsRelative;const o=e.groups;for(let l=0,h=o.length;l<h;l++){const u=o[l];this.addGroup(u.start,u.count,u.materialIndex)}const a=e.boundingBox;a!==null&&(this.boundingBox=a.clone());const c=e.boundingSphere;return c!==null&&(this.boundingSphere=c.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const mu=new Ae,as=new Ua,Io=new ci,gu=new v,Do=new v,No=new v,Uo=new v,vc=new v,Oo=new v,_u=new v,Fo=new v;class Xt extends Nt{constructor(e=new Gt,t=new fn){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}getVertexPosition(e,t){const n=this.geometry,s=n.attributes.position,r=n.morphAttributes.position,o=n.morphTargetsRelative;t.fromBufferAttribute(s,e);const a=this.morphTargetInfluences;if(r&&a){Oo.set(0,0,0);for(let c=0,l=r.length;c<l;c++){const h=a[c],u=r[c];h!==0&&(vc.fromBufferAttribute(u,e),o?Oo.addScaledVector(vc,h):Oo.addScaledVector(vc.sub(t),h))}t.add(Oo)}return t}raycast(e,t){const n=this.geometry,s=this.material,r=this.matrixWorld;s!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),Io.copy(n.boundingSphere),Io.applyMatrix4(r),as.copy(e.ray).recast(e.near),!(Io.containsPoint(as.origin)===!1&&(as.intersectSphere(Io,gu)===null||as.origin.distanceToSquared(gu)>(e.far-e.near)**2))&&(mu.copy(r).invert(),as.copy(e.ray).applyMatrix4(mu),!(n.boundingBox!==null&&as.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,as)))}_computeIntersections(e,t,n){let s;const r=this.geometry,o=this.material,a=r.index,c=r.attributes.position,l=r.attributes.uv,h=r.attributes.uv1,u=r.attributes.normal,d=r.groups,f=r.drawRange;if(a!==null)if(Array.isArray(o))for(let m=0,_=d.length;m<_;m++){const g=d[m],p=o[g.materialIndex],y=Math.max(g.start,f.start),M=Math.min(a.count,Math.min(g.start+g.count,f.start+f.count));for(let x=y,E=M;x<E;x+=3){const T=a.getX(x),P=a.getX(x+1),C=a.getX(x+2);s=Bo(this,p,e,n,l,h,u,T,P,C),s&&(s.faceIndex=Math.floor(x/3),s.face.materialIndex=g.materialIndex,t.push(s))}}else{const m=Math.max(0,f.start),_=Math.min(a.count,f.start+f.count);for(let g=m,p=_;g<p;g+=3){const y=a.getX(g),M=a.getX(g+1),x=a.getX(g+2);s=Bo(this,o,e,n,l,h,u,y,M,x),s&&(s.faceIndex=Math.floor(g/3),t.push(s))}}else if(c!==void 0)if(Array.isArray(o))for(let m=0,_=d.length;m<_;m++){const g=d[m],p=o[g.materialIndex],y=Math.max(g.start,f.start),M=Math.min(c.count,Math.min(g.start+g.count,f.start+f.count));for(let x=y,E=M;x<E;x+=3){const T=x,P=x+1,C=x+2;s=Bo(this,p,e,n,l,h,u,T,P,C),s&&(s.faceIndex=Math.floor(x/3),s.face.materialIndex=g.materialIndex,t.push(s))}}else{const m=Math.max(0,f.start),_=Math.min(c.count,f.start+f.count);for(let g=m,p=_;g<p;g+=3){const y=g,M=g+1,x=g+2;s=Bo(this,o,e,n,l,h,u,y,M,x),s&&(s.faceIndex=Math.floor(g/3),t.push(s))}}}}function f0(i,e,t,n,s,r,o,a){let c;if(e.side===yn?c=n.intersectTriangle(o,r,s,!0,a):c=n.intersectTriangle(s,r,o,e.side===Ti,a),c===null)return null;Fo.copy(a),Fo.applyMatrix4(i.matrixWorld);const l=t.ray.origin.distanceTo(Fo);return l<t.near||l>t.far?null:{distance:l,point:Fo.clone(),object:i}}function Bo(i,e,t,n,s,r,o,a,c,l){i.getVertexPosition(a,Do),i.getVertexPosition(c,No),i.getVertexPosition(l,Uo);const h=f0(i,e,t,n,Do,No,Uo,_u);if(h){const u=new v;Bn.getBarycoord(_u,Do,No,Uo,u),s&&(h.uv=Bn.getInterpolatedAttribute(s,a,c,l,u,new te)),r&&(h.uv1=Bn.getInterpolatedAttribute(r,a,c,l,u,new te)),o&&(h.normal=Bn.getInterpolatedAttribute(o,a,c,l,u,new v),h.normal.dot(n.direction)>0&&h.normal.multiplyScalar(-1));const d={a,b:c,c:l,normal:new v,materialIndex:0};Bn.getNormal(Do,No,Uo,d.normal),h.face=d,h.barycoord=u}return h}class ht extends Gt{constructor(e=1,t=1,n=1,s=1,r=1,o=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:s,heightSegments:r,depthSegments:o};const a=this;s=Math.floor(s),r=Math.floor(r),o=Math.floor(o);const c=[],l=[],h=[],u=[];let d=0,f=0;m("z","y","x",-1,-1,n,t,e,o,r,0),m("z","y","x",1,-1,n,t,-e,o,r,1),m("x","z","y",1,1,e,n,t,s,o,2),m("x","z","y",1,-1,e,n,-t,s,o,3),m("x","y","z",1,-1,e,t,n,s,r,4),m("x","y","z",-1,-1,e,t,-n,s,r,5),this.setIndex(c),this.setAttribute("position",new ct(l,3)),this.setAttribute("normal",new ct(h,3)),this.setAttribute("uv",new ct(u,2));function m(_,g,p,y,M,x,E,T,P,C,b){const w=x/P,L=E/C,F=x/2,O=E/2,k=T/2,K=P+1,X=C+1;let j=0,V=0;const oe=new v;for(let _e=0;_e<X;_e++){const Re=_e*L-O;for(let tt=0;tt<K;tt++){const wt=tt*w-F;oe[_]=wt*y,oe[g]=Re*M,oe[p]=k,l.push(oe.x,oe.y,oe.z),oe[_]=0,oe[g]=0,oe[p]=T>0?1:-1,h.push(oe.x,oe.y,oe.z),u.push(tt/P),u.push(1-_e/C),j+=1}}for(let _e=0;_e<C;_e++)for(let Re=0;Re<P;Re++){const tt=d+Re+K*_e,wt=d+Re+K*(_e+1),Z=d+(Re+1)+K*(_e+1),he=d+(Re+1)+K*_e;c.push(tt,wt,he),c.push(wt,Z,he),V+=6}a.addGroup(f,V,b),f+=V,d+=j}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ht(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function mr(i){const e={};for(const t in i){e[t]={};for(const n in i[t]){const s=i[t][n];s&&(s.isColor||s.isMatrix3||s.isMatrix4||s.isVector2||s.isVector3||s.isVector4||s.isTexture||s.isQuaternion)?s.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=s.clone():Array.isArray(s)?e[t][n]=s.slice():e[t][n]=s}}return e}function _n(i){const e={};for(let t=0;t<i.length;t++){const n=mr(i[t]);for(const s in n)e[s]=n[s]}return e}function p0(i){const e=[];for(let t=0;t<i.length;t++)e.push(i[t].clone());return e}function df(i){const e=i.getRenderTarget();return e===null?i.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:ft.workingColorSpace}const m0={clone:mr,merge:_n};var g0=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,_0=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class oi extends ri{static get type(){return"ShaderMaterial"}constructor(e){super(),this.isShaderMaterial=!0,this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=g0,this.fragmentShader=_0,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=mr(e.uniforms),this.uniformsGroups=p0(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const s in this.uniforms){const o=this.uniforms[s].value;o&&o.isTexture?t.uniforms[s]={type:"t",value:o.toJSON(e).uuid}:o&&o.isColor?t.uniforms[s]={type:"c",value:o.getHex()}:o&&o.isVector2?t.uniforms[s]={type:"v2",value:o.toArray()}:o&&o.isVector3?t.uniforms[s]={type:"v3",value:o.toArray()}:o&&o.isVector4?t.uniforms[s]={type:"v4",value:o.toArray()}:o&&o.isMatrix3?t.uniforms[s]={type:"m3",value:o.toArray()}:o&&o.isMatrix4?t.uniforms[s]={type:"m4",value:o.toArray()}:t.uniforms[s]={value:o}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const s in this.extensions)this.extensions[s]===!0&&(n[s]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class ff extends Nt{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Ae,this.projectionMatrix=new Ae,this.projectionMatrixInverse=new Ae,this.coordinateSystem=Si}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const zi=new v,xu=new te,vu=new te;class Tn extends ff{constructor(e=50,t=1,n=.1,s=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=s,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=pr*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(sr*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return pr*2*Math.atan(Math.tan(sr*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){zi.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(zi.x,zi.y).multiplyScalar(-e/zi.z),zi.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(zi.x,zi.y).multiplyScalar(-e/zi.z)}getViewSize(e,t){return this.getViewBounds(e,xu,vu),t.subVectors(vu,xu)}setViewOffset(e,t,n,s,r,o){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(sr*.5*this.fov)/this.zoom,n=2*t,s=this.aspect*n,r=-.5*s;const o=this.view;if(this.view!==null&&this.view.enabled){const c=o.fullWidth,l=o.fullHeight;r+=o.offsetX*s/c,t-=o.offsetY*n/l,s*=o.width/c,n*=o.height/l}const a=this.filmOffset;a!==0&&(r+=e*a/this.getFilmWidth()),this.projectionMatrix.makePerspective(r,r+s,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Ws=-90,Xs=1;class x0 extends Nt{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const s=new Tn(Ws,Xs,e,t);s.layers=this.layers,this.add(s);const r=new Tn(Ws,Xs,e,t);r.layers=this.layers,this.add(r);const o=new Tn(Ws,Xs,e,t);o.layers=this.layers,this.add(o);const a=new Tn(Ws,Xs,e,t);a.layers=this.layers,this.add(a);const c=new Tn(Ws,Xs,e,t);c.layers=this.layers,this.add(c);const l=new Tn(Ws,Xs,e,t);l.layers=this.layers,this.add(l)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,s,r,o,a,c]=t;for(const l of t)this.remove(l);if(e===Si)n.up.set(0,1,0),n.lookAt(1,0,0),s.up.set(0,1,0),s.lookAt(-1,0,0),r.up.set(0,0,-1),r.lookAt(0,1,0),o.up.set(0,0,1),o.lookAt(0,-1,0),a.up.set(0,1,0),a.lookAt(0,0,1),c.up.set(0,1,0),c.lookAt(0,0,-1);else if(e===wa)n.up.set(0,-1,0),n.lookAt(-1,0,0),s.up.set(0,-1,0),s.lookAt(1,0,0),r.up.set(0,0,1),r.lookAt(0,1,0),o.up.set(0,0,-1),o.lookAt(0,-1,0),a.up.set(0,-1,0),a.lookAt(0,0,1),c.up.set(0,-1,0),c.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const l of t)this.add(l),l.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:s}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[r,o,a,c,l,h]=this.children,u=e.getRenderTarget(),d=e.getActiveCubeFace(),f=e.getActiveMipmapLevel(),m=e.xr.enabled;e.xr.enabled=!1;const _=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,s),e.render(t,r),e.setRenderTarget(n,1,s),e.render(t,o),e.setRenderTarget(n,2,s),e.render(t,a),e.setRenderTarget(n,3,s),e.render(t,c),e.setRenderTarget(n,4,s),e.render(t,l),n.texture.generateMipmaps=_,e.setRenderTarget(n,5,s),e.render(t,h),e.setRenderTarget(u,d,f),e.xr.enabled=m,n.texture.needsPMREMUpdate=!0}}class pf extends Qt{constructor(e,t,n,s,r,o,a,c,l,h){e=e!==void 0?e:[],t=t!==void 0?t:lr,super(e,t,n,s,r,o,a,c,l,h),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class v0 extends Ts{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},s=[n,n,n,n,n,n];this.texture=new pf(s,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:Dn}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},s=new ht(5,5,5),r=new oi({name:"CubemapFromEquirect",uniforms:mr(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:yn,blending:Zi});r.uniforms.tEquirect.value=t;const o=new Xt(s,r),a=t.minFilter;return t.minFilter===bi&&(t.minFilter=Dn),new x0(1,10,this).update(e,o),t.minFilter=a,o.geometry.dispose(),o.material.dispose(),this}clear(e,t,n,s){const r=e.getRenderTarget();for(let o=0;o<6;o++)e.setRenderTarget(this,o),e.clear(t,n,s);e.setRenderTarget(r)}}const yc=new v,y0=new v,M0=new rt;class _s{constructor(e=new v(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,s){return this.normal.set(e,t,n),this.constant=s,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const s=yc.subVectors(n,t).cross(y0.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(s,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(yc),s=this.normal.dot(n);if(s===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const r=-(e.start.dot(this.normal)+this.constant)/s;return r<0||r>1?null:t.copy(e.start).addScaledVector(n,r)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||M0.getNormalMatrix(e),s=this.coplanarPoint(yc).applyMatrix4(e),r=this.normal.applyMatrix3(n).normalize();return this.constant=-s.dot(r),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const cs=new ci,ko=new v;class hh{constructor(e=new _s,t=new _s,n=new _s,s=new _s,r=new _s,o=new _s){this.planes=[e,t,n,s,r,o]}set(e,t,n,s,r,o){const a=this.planes;return a[0].copy(e),a[1].copy(t),a[2].copy(n),a[3].copy(s),a[4].copy(r),a[5].copy(o),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Si){const n=this.planes,s=e.elements,r=s[0],o=s[1],a=s[2],c=s[3],l=s[4],h=s[5],u=s[6],d=s[7],f=s[8],m=s[9],_=s[10],g=s[11],p=s[12],y=s[13],M=s[14],x=s[15];if(n[0].setComponents(c-r,d-l,g-f,x-p).normalize(),n[1].setComponents(c+r,d+l,g+f,x+p).normalize(),n[2].setComponents(c+o,d+h,g+m,x+y).normalize(),n[3].setComponents(c-o,d-h,g-m,x-y).normalize(),n[4].setComponents(c-a,d-u,g-_,x-M).normalize(),t===Si)n[5].setComponents(c+a,d+u,g+_,x+M).normalize();else if(t===wa)n[5].setComponents(a,u,_,M).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),cs.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),cs.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(cs)}intersectsSprite(e){return cs.center.set(0,0,0),cs.radius=.7071067811865476,cs.applyMatrix4(e.matrixWorld),this.intersectsSphere(cs)}intersectsSphere(e){const t=this.planes,n=e.center,s=-e.radius;for(let r=0;r<6;r++)if(t[r].distanceToPoint(n)<s)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const s=t[n];if(ko.x=s.normal.x>0?e.max.x:e.min.x,ko.y=s.normal.y>0?e.max.y:e.min.y,ko.z=s.normal.z>0?e.max.z:e.min.z,s.distanceToPoint(ko)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function mf(){let i=null,e=!1,t=null,n=null;function s(r,o){t(r,o),n=i.requestAnimationFrame(s)}return{start:function(){e!==!0&&t!==null&&(n=i.requestAnimationFrame(s),e=!0)},stop:function(){i.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(r){t=r},setContext:function(r){i=r}}}function w0(i){const e=new WeakMap;function t(a,c){const l=a.array,h=a.usage,u=l.byteLength,d=i.createBuffer();i.bindBuffer(c,d),i.bufferData(c,l,h),a.onUploadCallback();let f;if(l instanceof Float32Array)f=i.FLOAT;else if(l instanceof Uint16Array)a.isFloat16BufferAttribute?f=i.HALF_FLOAT:f=i.UNSIGNED_SHORT;else if(l instanceof Int16Array)f=i.SHORT;else if(l instanceof Uint32Array)f=i.UNSIGNED_INT;else if(l instanceof Int32Array)f=i.INT;else if(l instanceof Int8Array)f=i.BYTE;else if(l instanceof Uint8Array)f=i.UNSIGNED_BYTE;else if(l instanceof Uint8ClampedArray)f=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+l);return{buffer:d,type:f,bytesPerElement:l.BYTES_PER_ELEMENT,version:a.version,size:u}}function n(a,c,l){const h=c.array,u=c.updateRanges;if(i.bindBuffer(l,a),u.length===0)i.bufferSubData(l,0,h);else{u.sort((f,m)=>f.start-m.start);let d=0;for(let f=1;f<u.length;f++){const m=u[d],_=u[f];_.start<=m.start+m.count+1?m.count=Math.max(m.count,_.start+_.count-m.start):(++d,u[d]=_)}u.length=d+1;for(let f=0,m=u.length;f<m;f++){const _=u[f];i.bufferSubData(l,_.start*h.BYTES_PER_ELEMENT,h,_.start,_.count)}c.clearUpdateRanges()}c.onUploadCallback()}function s(a){return a.isInterleavedBufferAttribute&&(a=a.data),e.get(a)}function r(a){a.isInterleavedBufferAttribute&&(a=a.data);const c=e.get(a);c&&(i.deleteBuffer(c.buffer),e.delete(a))}function o(a,c){if(a.isInterleavedBufferAttribute&&(a=a.data),a.isGLBufferAttribute){const h=e.get(a);(!h||h.version<a.version)&&e.set(a,{buffer:a.buffer,type:a.type,bytesPerElement:a.elementSize,version:a.version});return}const l=e.get(a);if(l===void 0)e.set(a,t(a,c));else if(l.version<a.version){if(l.size!==a.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(l.buffer,a,c),l.version=a.version}}return{get:s,remove:r,update:o}}class ai extends Gt{constructor(e=1,t=1,n=1,s=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:s};const r=e/2,o=t/2,a=Math.floor(n),c=Math.floor(s),l=a+1,h=c+1,u=e/a,d=t/c,f=[],m=[],_=[],g=[];for(let p=0;p<h;p++){const y=p*d-o;for(let M=0;M<l;M++){const x=M*u-r;m.push(x,-y,0),_.push(0,0,1),g.push(M/a),g.push(1-p/c)}}for(let p=0;p<c;p++)for(let y=0;y<a;y++){const M=y+l*p,x=y+l*(p+1),E=y+1+l*(p+1),T=y+1+l*p;f.push(M,x,T),f.push(x,E,T)}this.setIndex(f),this.setAttribute("position",new ct(m,3)),this.setAttribute("normal",new ct(_,3)),this.setAttribute("uv",new ct(g,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ai(e.width,e.height,e.widthSegments,e.heightSegments)}}var b0=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,S0=`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,E0=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,T0=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,A0=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,R0=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,C0=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,P0=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,L0=`#ifdef USE_BATCHING
	#if ! defined( GL_ANGLE_multi_draw )
	#define gl_DrawID _gl_DrawID
	uniform int _gl_DrawID;
	#endif
	uniform highp sampler2D batchingTexture;
	uniform highp usampler2D batchingIdTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
	float getIndirectIndex( const in int i ) {
		int size = textureSize( batchingIdTexture, 0 ).x;
		int x = i % size;
		int y = i / size;
		return float( texelFetch( batchingIdTexture, ivec2( x, y ), 0 ).r );
	}
#endif
#ifdef USE_BATCHING_COLOR
	uniform sampler2D batchingColorTexture;
	vec3 getBatchingColor( const in float i ) {
		int size = textureSize( batchingColorTexture, 0 ).x;
		int j = int( i );
		int x = j % size;
		int y = j / size;
		return texelFetch( batchingColorTexture, ivec2( x, y ), 0 ).rgb;
	}
#endif`,I0=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,D0=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,N0=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,U0=`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,O0=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,F0=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,B0=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#ifdef ALPHA_TO_COVERAGE
		float distanceToPlane, distanceGradient;
		float clipOpacity = 1.0;
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
			distanceGradient = fwidth( distanceToPlane ) / 2.0;
			clipOpacity *= smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			if ( clipOpacity == 0.0 ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			float unionClipOpacity = 1.0;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
				distanceGradient = fwidth( distanceToPlane ) / 2.0;
				unionClipOpacity *= 1.0 - smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			}
			#pragma unroll_loop_end
			clipOpacity *= 1.0 - unionClipOpacity;
		#endif
		diffuseColor.a *= clipOpacity;
		if ( diffuseColor.a == 0.0 ) discard;
	#else
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			bool clipped = true;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
			}
			#pragma unroll_loop_end
			if ( clipped ) discard;
		#endif
	#endif
#endif`,k0=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,z0=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,H0=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,G0=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,V0=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,W0=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,X0=`#if defined( USE_COLOR_ALPHA )
	vColor = vec4( 1.0 );
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	vColor = vec3( 1.0 );
#endif
#ifdef USE_COLOR
	vColor *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.xyz *= instanceColor.xyz;
#endif
#ifdef USE_BATCHING_COLOR
	vec3 batchingColor = getBatchingColor( getIndirectIndex( gl_DrawID ) );
	vColor.xyz *= batchingColor.xyz;
#endif`,q0=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
vec3 inverseTransformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( vec4( dir, 0.0 ) * matrix ).xyz );
}
mat3 transposeMat3( const in mat3 m ) {
	mat3 tmp;
	tmp[ 0 ] = vec3( m[ 0 ].x, m[ 1 ].x, m[ 2 ].x );
	tmp[ 1 ] = vec3( m[ 0 ].y, m[ 1 ].y, m[ 2 ].y );
	tmp[ 2 ] = vec3( m[ 0 ].z, m[ 1 ].z, m[ 2 ].z );
	return tmp;
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,j0=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,$0=`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
	#ifdef FLIP_SIDED
		transformedTangent = - transformedTangent;
	#endif
#endif`,Y0=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,K0=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,Z0=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,J0=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,Q0="gl_FragColor = linearToOutputTexel( gl_FragColor );",eg=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,tg=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, envMapRotation * vec3( flipEnvMap * reflectVec.x, reflectVec.yz ) );
	#else
		vec4 envColor = vec4( 0.0 );
	#endif
	#ifdef ENVMAP_BLENDING_MULTIPLY
		outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_MIX )
		outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_ADD )
		outgoingLight += envColor.xyz * specularStrength * reflectivity;
	#endif
#endif`,ng=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,ig=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,sg=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,rg=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,og=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,ag=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,cg=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,lg=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,hg=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,ug=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,dg=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,fg=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,pg=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
	if ( cutoffDistance > 0.0 ) {
		distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
	}
	return distanceFalloff;
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif`,mg=`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, roughness * roughness) );
			reflectVec = inverseTransformDirection( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,gg=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,_g=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,xg=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,vg=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,yg=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb * ( 1.0 - metalnessFactor );
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = mix( min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_DISPERSION
	material.dispersion = dispersion;
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.07, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,Mg=`struct PhysicalMaterial {
	vec3 diffuseColor;
	float roughness;
	vec3 specularColor;
	float specularF90;
	float dispersion;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		float v = 0.5 / ( gv + gl );
		return saturate(v);
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColor;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transposeMat3( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float a = roughness < 0.25 ? -339.2 * r2 + 161.4 * roughness - 25.9 : -8.48 * r2 + 14.3 * roughness - 9.95;
	float b = roughness < 0.25 ? 44.0 * r2 - 23.7 * roughness + 3.26 : 1.97 * r2 - 3.27 * roughness + 0.72;
	float DG = exp( a * dotNV + b ) + ( roughness < 0.25 ? 0.0 : 0.1 * ( roughness - 0.25 ) );
	return saturate( DG * RECIPROCAL_PI );
}
vec2 DFGApprox( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	const vec4 c0 = vec4( - 1, - 0.0275, - 0.572, 0.022 );
	const vec4 c1 = vec4( 1, 0.0425, 1.04, - 0.04 );
	vec4 r = roughness * c0 + c1;
	float a004 = min( r.x * r.x, exp2( - 9.28 * dotNV ) ) * r.x + r.y;
	vec2 fab = vec2( - 1.04, 1.04 ) * a004 + r.zw;
	return fab;
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColor * t2.x + ( vec3( 1.0 ) - material.specularColor ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseColor * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
	#endif
	vec3 singleScattering = vec3( 0.0 );
	vec3 multiScattering = vec3( 0.0 );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnel, material.roughness, singleScattering, multiScattering );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScattering, multiScattering );
	#endif
	vec3 totalScattering = singleScattering + multiScattering;
	vec3 diffuse = material.diffuseColor * ( 1.0 - max( max( totalScattering.r, totalScattering.g ), totalScattering.b ) );
	reflectedLight.indirectSpecular += radiance * singleScattering;
	reflectedLight.indirectSpecular += multiScattering * cosineWeightedIrradiance;
	reflectedLight.indirectDiffuse += diffuse * cosineWeightedIrradiance;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,wg=`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnel = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowIntensity, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowIntensity, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,bg=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )
		iblIrradiance += getIBLIrradiance( geometryNormal );
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,Sg=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,Eg=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,Tg=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,Ag=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,Rg=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,Cg=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,Pg=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,Lg=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,Ig=`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,Dg=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,Ng=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,Ug=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,Og=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,Fg=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,Bg=`#ifdef USE_MORPHTARGETS
	#ifndef USE_INSTANCING_MORPH
		uniform float morphTargetBaseInfluence;
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	#endif
	uniform sampler2DArray morphTargetsTexture;
	uniform ivec2 morphTargetsTextureSize;
	vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
		int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
		int y = texelIndex / morphTargetsTextureSize.x;
		int x = texelIndex - y * morphTargetsTextureSize.x;
		ivec3 morphUV = ivec3( x, y, morphTargetIndex );
		return texelFetch( morphTargetsTexture, morphUV, 0 );
	}
#endif`,kg=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,zg=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,Hg=`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,Gg=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,Vg=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,Wg=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,Xg=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,qg=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,jg=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,$g=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,Yg=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,Kg=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,Zg=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;const float ShiftRight8 = 1. / 256.;
const float Inv255 = 1. / 255.;
const vec4 PackFactors = vec4( 1.0, 256.0, 256.0 * 256.0, 256.0 * 256.0 * 256.0 );
const vec2 UnpackFactors2 = vec2( UnpackDownscale, 1.0 / PackFactors.g );
const vec3 UnpackFactors3 = vec3( UnpackDownscale / PackFactors.rg, 1.0 / PackFactors.b );
const vec4 UnpackFactors4 = vec4( UnpackDownscale / PackFactors.rgb, 1.0 / PackFactors.a );
vec4 packDepthToRGBA( const in float v ) {
	if( v <= 0.0 )
		return vec4( 0., 0., 0., 0. );
	if( v >= 1.0 )
		return vec4( 1., 1., 1., 1. );
	float vuf;
	float af = modf( v * PackFactors.a, vuf );
	float bf = modf( vuf * ShiftRight8, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec4( vuf * Inv255, gf * PackUpscale, bf * PackUpscale, af );
}
vec3 packDepthToRGB( const in float v ) {
	if( v <= 0.0 )
		return vec3( 0., 0., 0. );
	if( v >= 1.0 )
		return vec3( 1., 1., 1. );
	float vuf;
	float bf = modf( v * PackFactors.b, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec3( vuf * Inv255, gf * PackUpscale, bf );
}
vec2 packDepthToRG( const in float v ) {
	if( v <= 0.0 )
		return vec2( 0., 0. );
	if( v >= 1.0 )
		return vec2( 1., 1. );
	float vuf;
	float gf = modf( v * 256., vuf );
	return vec2( vuf * Inv255, gf );
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors4 );
}
float unpackRGBToDepth( const in vec3 v ) {
	return dot( v, UnpackFactors3 );
}
float unpackRGToDepth( const in vec2 v ) {
	return v.r * UnpackFactors2.r + v.g * UnpackFactors2.g;
}
vec4 pack2HalfToRGBA( const in vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( const in vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return depth * ( near - far ) - near;
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return ( near * far ) / ( ( far - near ) * depth - far );
}`,Jg=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,Qg=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,e_=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,t_=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,n_=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,i_=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,s_=`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform sampler2D pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	float texture2DCompare( sampler2D depths, vec2 uv, float compare ) {
		return step( compare, unpackRGBAToDepth( texture2D( depths, uv ) ) );
	}
	vec2 texture2DDistribution( sampler2D shadow, vec2 uv ) {
		return unpackRGBATo2Half( texture2D( shadow, uv ) );
	}
	float VSMShadow (sampler2D shadow, vec2 uv, float compare ){
		float occlusion = 1.0;
		vec2 distribution = texture2DDistribution( shadow, uv );
		float hard_shadow = step( compare , distribution.x );
		if (hard_shadow != 1.0 ) {
			float distance = compare - distribution.x ;
			float variance = max( 0.00000, distribution.y * distribution.y );
			float softness_probability = variance / (variance + distance * distance );			softness_probability = clamp( ( softness_probability - 0.3 ) / ( 0.95 - 0.3 ), 0.0, 1.0 );			occlusion = clamp( max( hard_shadow, softness_probability ), 0.0, 1.0 );
		}
		return occlusion;
	}
	float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
		float shadow = 1.0;
		shadowCoord.xyz /= shadowCoord.w;
		shadowCoord.z += shadowBias;
		bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
		bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
		if ( frustumTest ) {
		#if defined( SHADOWMAP_TYPE_PCF )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx0 = - texelSize.x * shadowRadius;
			float dy0 = - texelSize.y * shadowRadius;
			float dx1 = + texelSize.x * shadowRadius;
			float dy1 = + texelSize.y * shadowRadius;
			float dx2 = dx0 / 2.0;
			float dy2 = dy0 / 2.0;
			float dx3 = dx1 / 2.0;
			float dy3 = dy1 / 2.0;
			shadow = (
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy1 ), shadowCoord.z )
			) * ( 1.0 / 17.0 );
		#elif defined( SHADOWMAP_TYPE_PCF_SOFT )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx = texelSize.x;
			float dy = texelSize.y;
			vec2 uv = shadowCoord.xy;
			vec2 f = fract( uv * shadowMapSize + 0.5 );
			uv -= f * texelSize;
			shadow = (
				texture2DCompare( shadowMap, uv, shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( dx, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( 0.0, dy ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + texelSize, shadowCoord.z ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, 0.0 ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 0.0 ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, dy ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( 0.0, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 0.0, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( texture2DCompare( shadowMap, uv + vec2( dx, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( dx, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( mix( texture2DCompare( shadowMap, uv + vec2( -dx, -dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, -dy ), shadowCoord.z ),
						  f.x ),
					 mix( texture2DCompare( shadowMap, uv + vec2( -dx, 2.0 * dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 2.0 * dy ), shadowCoord.z ),
						  f.x ),
					 f.y )
			) * ( 1.0 / 9.0 );
		#elif defined( SHADOWMAP_TYPE_VSM )
			shadow = VSMShadow( shadowMap, shadowCoord.xy, shadowCoord.z );
		#else
			shadow = texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z );
		#endif
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	vec2 cubeToUV( vec3 v, float texelSizeY ) {
		vec3 absV = abs( v );
		float scaleToCube = 1.0 / max( absV.x, max( absV.y, absV.z ) );
		absV *= scaleToCube;
		v *= scaleToCube * ( 1.0 - 2.0 * texelSizeY );
		vec2 planar = v.xy;
		float almostATexel = 1.5 * texelSizeY;
		float almostOne = 1.0 - almostATexel;
		if ( absV.z >= almostOne ) {
			if ( v.z > 0.0 )
				planar.x = 4.0 - v.x;
		} else if ( absV.x >= almostOne ) {
			float signX = sign( v.x );
			planar.x = v.z * signX + 2.0 * signX;
		} else if ( absV.y >= almostOne ) {
			float signY = sign( v.y );
			planar.x = v.x + 2.0 * signY + 2.0;
			planar.y = v.z * signY - 2.0;
		}
		return vec2( 0.125, 0.25 ) * planar + vec2( 0.375, 0.75 );
	}
	float getPointShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		
		float lightToPositionLength = length( lightToPosition );
		if ( lightToPositionLength - shadowCameraFar <= 0.0 && lightToPositionLength - shadowCameraNear >= 0.0 ) {
			float dp = ( lightToPositionLength - shadowCameraNear ) / ( shadowCameraFar - shadowCameraNear );			dp += shadowBias;
			vec3 bd3D = normalize( lightToPosition );
			vec2 texelSize = vec2( 1.0 ) / ( shadowMapSize * vec2( 4.0, 2.0 ) );
			#if defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_PCF_SOFT ) || defined( SHADOWMAP_TYPE_VSM )
				vec2 offset = vec2( - 1, 1 ) * shadowRadius * texelSize.y;
				shadow = (
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxx, texelSize.y ), dp )
				) * ( 1.0 / 9.0 );
			#else
				shadow = texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp );
			#endif
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
#endif`,r_=`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,o_=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	vec3 shadowWorldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,a_=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowIntensity, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowIntensity, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowIntensity, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,c_=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,l_=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,h_=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,u_=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,d_=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,f_=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,p_=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,m_=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 CineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color *= toneMappingExposure;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	color = clamp( color, 0.0, 1.0 );
	return color;
}
vec3 NeutralToneMapping( vec3 color ) {
	const float StartCompression = 0.8 - 0.04;
	const float Desaturation = 0.15;
	color *= toneMappingExposure;
	float x = min( color.r, min( color.g, color.b ) );
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max( color.r, max( color.g, color.b ) );
	if ( peak < StartCompression ) return color;
	float d = 1. - StartCompression;
	float newPeak = 1. - d * d / ( peak + d - StartCompression );
	color *= newPeak / peak;
	float g = 1. - 1. / ( Desaturation * ( peak - newPeak ) + 1. );
	return mix( color, vec3( newPeak ), g );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,g_=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = inverseTransformDirection( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseColor, material.specularColor, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.dispersion, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,__=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float dispersion, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec4 transmittedLight;
		vec3 transmittance;
		#ifdef USE_DISPERSION
			float halfSpread = ( ior - 1.0 ) * 0.025 * dispersion;
			vec3 iors = vec3( ior - halfSpread, ior, ior + halfSpread );
			for ( int i = 0; i < 3; i ++ ) {
				vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, iors[ i ], modelMatrix );
				vec3 refractedRayExit = position + transmissionRay;
		
				vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
				vec2 refractionCoords = ndcPos.xy / ndcPos.w;
				refractionCoords += 1.0;
				refractionCoords /= 2.0;
		
				vec4 transmissionSample = getTransmissionSample( refractionCoords, roughness, iors[ i ] );
				transmittedLight[ i ] = transmissionSample[ i ];
				transmittedLight.a += transmissionSample.a;
				transmittance[ i ] = diffuseColor[ i ] * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance )[ i ];
			}
			transmittedLight.a /= 3.0;
		
		#else
		
			vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
			vec3 refractedRayExit = position + transmissionRay;
			vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
			vec2 refractionCoords = ndcPos.xy / ndcPos.w;
			refractionCoords += 1.0;
			refractionCoords /= 2.0;
			transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
			transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		
		#endif
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,x_=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,v_=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,y_=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,M_=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const w_=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,b_=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,S_=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,E_=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float flipEnvMap;
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
uniform mat3 backgroundRotation;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, backgroundRotation * vec3( flipEnvMap * vWorldDirection.x, vWorldDirection.yz ) );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, backgroundRotation * vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,T_=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,A_=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,R_=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,C_=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	float fragCoordZ = 0.5 * vHighPrecisionZW[0] / vHighPrecisionZW[1] + 0.5;
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#elif DEPTH_PACKING == 3202
		gl_FragColor = vec4( packDepthToRGB( fragCoordZ ), 1.0 );
	#elif DEPTH_PACKING == 3203
		gl_FragColor = vec4( packDepthToRG( fragCoordZ ), 0.0, 1.0 );
	#endif
}`,P_=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,L_=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main () {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = packDepthToRGBA( dist );
}`,I_=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,D_=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,N_=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,U_=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,O_=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,F_=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,B_=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,k_=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,z_=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,H_=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,G_=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,V_=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <packing>
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 0.0, 0.0, 0.0, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( packNormalToRGB( normal ), diffuseColor.a );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,W_=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,X_=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,q_=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,j_=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_DISPERSION
	uniform float dispersion;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
		float sheenEnergyComp = 1.0 - 0.157 * max3( material.sheenColor );
		outgoingLight = outgoingLight * sheenEnergyComp + sheenSpecularDirect + sheenSpecularIndirect;
	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,$_=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Y_=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,K_=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,Z_=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,J_=`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Q_=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <packing>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,ex=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix[ 3 ];
	vec2 scale = vec2( length( modelMatrix[ 0 ].xyz ), length( modelMatrix[ 1 ].xyz ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,tx=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,at={alphahash_fragment:b0,alphahash_pars_fragment:S0,alphamap_fragment:E0,alphamap_pars_fragment:T0,alphatest_fragment:A0,alphatest_pars_fragment:R0,aomap_fragment:C0,aomap_pars_fragment:P0,batching_pars_vertex:L0,batching_vertex:I0,begin_vertex:D0,beginnormal_vertex:N0,bsdfs:U0,iridescence_fragment:O0,bumpmap_pars_fragment:F0,clipping_planes_fragment:B0,clipping_planes_pars_fragment:k0,clipping_planes_pars_vertex:z0,clipping_planes_vertex:H0,color_fragment:G0,color_pars_fragment:V0,color_pars_vertex:W0,color_vertex:X0,common:q0,cube_uv_reflection_fragment:j0,defaultnormal_vertex:$0,displacementmap_pars_vertex:Y0,displacementmap_vertex:K0,emissivemap_fragment:Z0,emissivemap_pars_fragment:J0,colorspace_fragment:Q0,colorspace_pars_fragment:eg,envmap_fragment:tg,envmap_common_pars_fragment:ng,envmap_pars_fragment:ig,envmap_pars_vertex:sg,envmap_physical_pars_fragment:mg,envmap_vertex:rg,fog_vertex:og,fog_pars_vertex:ag,fog_fragment:cg,fog_pars_fragment:lg,gradientmap_pars_fragment:hg,lightmap_pars_fragment:ug,lights_lambert_fragment:dg,lights_lambert_pars_fragment:fg,lights_pars_begin:pg,lights_toon_fragment:gg,lights_toon_pars_fragment:_g,lights_phong_fragment:xg,lights_phong_pars_fragment:vg,lights_physical_fragment:yg,lights_physical_pars_fragment:Mg,lights_fragment_begin:wg,lights_fragment_maps:bg,lights_fragment_end:Sg,logdepthbuf_fragment:Eg,logdepthbuf_pars_fragment:Tg,logdepthbuf_pars_vertex:Ag,logdepthbuf_vertex:Rg,map_fragment:Cg,map_pars_fragment:Pg,map_particle_fragment:Lg,map_particle_pars_fragment:Ig,metalnessmap_fragment:Dg,metalnessmap_pars_fragment:Ng,morphinstance_vertex:Ug,morphcolor_vertex:Og,morphnormal_vertex:Fg,morphtarget_pars_vertex:Bg,morphtarget_vertex:kg,normal_fragment_begin:zg,normal_fragment_maps:Hg,normal_pars_fragment:Gg,normal_pars_vertex:Vg,normal_vertex:Wg,normalmap_pars_fragment:Xg,clearcoat_normal_fragment_begin:qg,clearcoat_normal_fragment_maps:jg,clearcoat_pars_fragment:$g,iridescence_pars_fragment:Yg,opaque_fragment:Kg,packing:Zg,premultiplied_alpha_fragment:Jg,project_vertex:Qg,dithering_fragment:e_,dithering_pars_fragment:t_,roughnessmap_fragment:n_,roughnessmap_pars_fragment:i_,shadowmap_pars_fragment:s_,shadowmap_pars_vertex:r_,shadowmap_vertex:o_,shadowmask_pars_fragment:a_,skinbase_vertex:c_,skinning_pars_vertex:l_,skinning_vertex:h_,skinnormal_vertex:u_,specularmap_fragment:d_,specularmap_pars_fragment:f_,tonemapping_fragment:p_,tonemapping_pars_fragment:m_,transmission_fragment:g_,transmission_pars_fragment:__,uv_pars_fragment:x_,uv_pars_vertex:v_,uv_vertex:y_,worldpos_vertex:M_,background_vert:w_,background_frag:b_,backgroundCube_vert:S_,backgroundCube_frag:E_,cube_vert:T_,cube_frag:A_,depth_vert:R_,depth_frag:C_,distanceRGBA_vert:P_,distanceRGBA_frag:L_,equirect_vert:I_,equirect_frag:D_,linedashed_vert:N_,linedashed_frag:U_,meshbasic_vert:O_,meshbasic_frag:F_,meshlambert_vert:B_,meshlambert_frag:k_,meshmatcap_vert:z_,meshmatcap_frag:H_,meshnormal_vert:G_,meshnormal_frag:V_,meshphong_vert:W_,meshphong_frag:X_,meshphysical_vert:q_,meshphysical_frag:j_,meshtoon_vert:$_,meshtoon_frag:Y_,points_vert:K_,points_frag:Z_,shadow_vert:J_,shadow_frag:Q_,sprite_vert:ex,sprite_frag:tx},xe={common:{diffuse:{value:new Ve(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new rt},alphaMap:{value:null},alphaMapTransform:{value:new rt},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new rt}},envmap:{envMap:{value:null},envMapRotation:{value:new rt},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new rt}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new rt}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new rt},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new rt},normalScale:{value:new te(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new rt},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new rt}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new rt}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new rt}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new Ve(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new Ve(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new rt},alphaTest:{value:0},uvTransform:{value:new rt}},sprite:{diffuse:{value:new Ve(16777215)},opacity:{value:1},center:{value:new te(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new rt},alphaMap:{value:null},alphaMapTransform:{value:new rt},alphaTest:{value:0}}},ni={basic:{uniforms:_n([xe.common,xe.specularmap,xe.envmap,xe.aomap,xe.lightmap,xe.fog]),vertexShader:at.meshbasic_vert,fragmentShader:at.meshbasic_frag},lambert:{uniforms:_n([xe.common,xe.specularmap,xe.envmap,xe.aomap,xe.lightmap,xe.emissivemap,xe.bumpmap,xe.normalmap,xe.displacementmap,xe.fog,xe.lights,{emissive:{value:new Ve(0)}}]),vertexShader:at.meshlambert_vert,fragmentShader:at.meshlambert_frag},phong:{uniforms:_n([xe.common,xe.specularmap,xe.envmap,xe.aomap,xe.lightmap,xe.emissivemap,xe.bumpmap,xe.normalmap,xe.displacementmap,xe.fog,xe.lights,{emissive:{value:new Ve(0)},specular:{value:new Ve(1118481)},shininess:{value:30}}]),vertexShader:at.meshphong_vert,fragmentShader:at.meshphong_frag},standard:{uniforms:_n([xe.common,xe.envmap,xe.aomap,xe.lightmap,xe.emissivemap,xe.bumpmap,xe.normalmap,xe.displacementmap,xe.roughnessmap,xe.metalnessmap,xe.fog,xe.lights,{emissive:{value:new Ve(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:at.meshphysical_vert,fragmentShader:at.meshphysical_frag},toon:{uniforms:_n([xe.common,xe.aomap,xe.lightmap,xe.emissivemap,xe.bumpmap,xe.normalmap,xe.displacementmap,xe.gradientmap,xe.fog,xe.lights,{emissive:{value:new Ve(0)}}]),vertexShader:at.meshtoon_vert,fragmentShader:at.meshtoon_frag},matcap:{uniforms:_n([xe.common,xe.bumpmap,xe.normalmap,xe.displacementmap,xe.fog,{matcap:{value:null}}]),vertexShader:at.meshmatcap_vert,fragmentShader:at.meshmatcap_frag},points:{uniforms:_n([xe.points,xe.fog]),vertexShader:at.points_vert,fragmentShader:at.points_frag},dashed:{uniforms:_n([xe.common,xe.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:at.linedashed_vert,fragmentShader:at.linedashed_frag},depth:{uniforms:_n([xe.common,xe.displacementmap]),vertexShader:at.depth_vert,fragmentShader:at.depth_frag},normal:{uniforms:_n([xe.common,xe.bumpmap,xe.normalmap,xe.displacementmap,{opacity:{value:1}}]),vertexShader:at.meshnormal_vert,fragmentShader:at.meshnormal_frag},sprite:{uniforms:_n([xe.sprite,xe.fog]),vertexShader:at.sprite_vert,fragmentShader:at.sprite_frag},background:{uniforms:{uvTransform:{value:new rt},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:at.background_vert,fragmentShader:at.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new rt}},vertexShader:at.backgroundCube_vert,fragmentShader:at.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:at.cube_vert,fragmentShader:at.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:at.equirect_vert,fragmentShader:at.equirect_frag},distanceRGBA:{uniforms:_n([xe.common,xe.displacementmap,{referencePosition:{value:new v},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:at.distanceRGBA_vert,fragmentShader:at.distanceRGBA_frag},shadow:{uniforms:_n([xe.lights,xe.fog,{color:{value:new Ve(0)},opacity:{value:1}}]),vertexShader:at.shadow_vert,fragmentShader:at.shadow_frag}};ni.physical={uniforms:_n([ni.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new rt},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new rt},clearcoatNormalScale:{value:new te(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new rt},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new rt},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new rt},sheen:{value:0},sheenColor:{value:new Ve(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new rt},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new rt},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new rt},transmissionSamplerSize:{value:new te},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new rt},attenuationDistance:{value:0},attenuationColor:{value:new Ve(0)},specularColor:{value:new Ve(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new rt},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new rt},anisotropyVector:{value:new te},anisotropyMap:{value:null},anisotropyMapTransform:{value:new rt}}]),vertexShader:at.meshphysical_vert,fragmentShader:at.meshphysical_frag};const zo={r:0,b:0,g:0},ls=new wn,nx=new Ae;function ix(i,e,t,n,s,r,o){const a=new Ve(0);let c=r===!0?0:1,l,h,u=null,d=0,f=null;function m(y){let M=y.isScene===!0?y.background:null;return M&&M.isTexture&&(M=(y.backgroundBlurriness>0?t:e).get(M)),M}function _(y){let M=!1;const x=m(y);x===null?p(a,c):x&&x.isColor&&(p(x,1),M=!0);const E=i.xr.getEnvironmentBlendMode();E==="additive"?n.buffers.color.setClear(0,0,0,1,o):E==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,o),(i.autoClear||M)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function g(y,M){const x=m(M);x&&(x.isCubeTexture||x.mapping===Da)?(h===void 0&&(h=new Xt(new ht(1,1,1),new oi({name:"BackgroundCubeMaterial",uniforms:mr(ni.backgroundCube.uniforms),vertexShader:ni.backgroundCube.vertexShader,fragmentShader:ni.backgroundCube.fragmentShader,side:yn,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),h.geometry.deleteAttribute("uv"),h.onBeforeRender=function(E,T,P){this.matrixWorld.copyPosition(P.matrixWorld)},Object.defineProperty(h.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),s.update(h)),ls.copy(M.backgroundRotation),ls.x*=-1,ls.y*=-1,ls.z*=-1,x.isCubeTexture&&x.isRenderTargetTexture===!1&&(ls.y*=-1,ls.z*=-1),h.material.uniforms.envMap.value=x,h.material.uniforms.flipEnvMap.value=x.isCubeTexture&&x.isRenderTargetTexture===!1?-1:1,h.material.uniforms.backgroundBlurriness.value=M.backgroundBlurriness,h.material.uniforms.backgroundIntensity.value=M.backgroundIntensity,h.material.uniforms.backgroundRotation.value.setFromMatrix4(nx.makeRotationFromEuler(ls)),h.material.toneMapped=ft.getTransfer(x.colorSpace)!==Rt,(u!==x||d!==x.version||f!==i.toneMapping)&&(h.material.needsUpdate=!0,u=x,d=x.version,f=i.toneMapping),h.layers.enableAll(),y.unshift(h,h.geometry,h.material,0,0,null)):x&&x.isTexture&&(l===void 0&&(l=new Xt(new ai(2,2),new oi({name:"BackgroundMaterial",uniforms:mr(ni.background.uniforms),vertexShader:ni.background.vertexShader,fragmentShader:ni.background.fragmentShader,side:Ti,depthTest:!1,depthWrite:!1,fog:!1})),l.geometry.deleteAttribute("normal"),Object.defineProperty(l.material,"map",{get:function(){return this.uniforms.t2D.value}}),s.update(l)),l.material.uniforms.t2D.value=x,l.material.uniforms.backgroundIntensity.value=M.backgroundIntensity,l.material.toneMapped=ft.getTransfer(x.colorSpace)!==Rt,x.matrixAutoUpdate===!0&&x.updateMatrix(),l.material.uniforms.uvTransform.value.copy(x.matrix),(u!==x||d!==x.version||f!==i.toneMapping)&&(l.material.needsUpdate=!0,u=x,d=x.version,f=i.toneMapping),l.layers.enableAll(),y.unshift(l,l.geometry,l.material,0,0,null))}function p(y,M){y.getRGB(zo,df(i)),n.buffers.color.setClear(zo.r,zo.g,zo.b,M,o)}return{getClearColor:function(){return a},setClearColor:function(y,M=1){a.set(y),c=M,p(a,c)},getClearAlpha:function(){return c},setClearAlpha:function(y){c=y,p(a,c)},render:_,addToRenderList:g}}function sx(i,e){const t=i.getParameter(i.MAX_VERTEX_ATTRIBS),n={},s=d(null);let r=s,o=!1;function a(w,L,F,O,k){let K=!1;const X=u(O,F,L);r!==X&&(r=X,l(r.object)),K=f(w,O,F,k),K&&m(w,O,F,k),k!==null&&e.update(k,i.ELEMENT_ARRAY_BUFFER),(K||o)&&(o=!1,x(w,L,F,O),k!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,e.get(k).buffer))}function c(){return i.createVertexArray()}function l(w){return i.bindVertexArray(w)}function h(w){return i.deleteVertexArray(w)}function u(w,L,F){const O=F.wireframe===!0;let k=n[w.id];k===void 0&&(k={},n[w.id]=k);let K=k[L.id];K===void 0&&(K={},k[L.id]=K);let X=K[O];return X===void 0&&(X=d(c()),K[O]=X),X}function d(w){const L=[],F=[],O=[];for(let k=0;k<t;k++)L[k]=0,F[k]=0,O[k]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:L,enabledAttributes:F,attributeDivisors:O,object:w,attributes:{},index:null}}function f(w,L,F,O){const k=r.attributes,K=L.attributes;let X=0;const j=F.getAttributes();for(const V in j)if(j[V].location>=0){const _e=k[V];let Re=K[V];if(Re===void 0&&(V==="instanceMatrix"&&w.instanceMatrix&&(Re=w.instanceMatrix),V==="instanceColor"&&w.instanceColor&&(Re=w.instanceColor)),_e===void 0||_e.attribute!==Re||Re&&_e.data!==Re.data)return!0;X++}return r.attributesNum!==X||r.index!==O}function m(w,L,F,O){const k={},K=L.attributes;let X=0;const j=F.getAttributes();for(const V in j)if(j[V].location>=0){let _e=K[V];_e===void 0&&(V==="instanceMatrix"&&w.instanceMatrix&&(_e=w.instanceMatrix),V==="instanceColor"&&w.instanceColor&&(_e=w.instanceColor));const Re={};Re.attribute=_e,_e&&_e.data&&(Re.data=_e.data),k[V]=Re,X++}r.attributes=k,r.attributesNum=X,r.index=O}function _(){const w=r.newAttributes;for(let L=0,F=w.length;L<F;L++)w[L]=0}function g(w){p(w,0)}function p(w,L){const F=r.newAttributes,O=r.enabledAttributes,k=r.attributeDivisors;F[w]=1,O[w]===0&&(i.enableVertexAttribArray(w),O[w]=1),k[w]!==L&&(i.vertexAttribDivisor(w,L),k[w]=L)}function y(){const w=r.newAttributes,L=r.enabledAttributes;for(let F=0,O=L.length;F<O;F++)L[F]!==w[F]&&(i.disableVertexAttribArray(F),L[F]=0)}function M(w,L,F,O,k,K,X){X===!0?i.vertexAttribIPointer(w,L,F,k,K):i.vertexAttribPointer(w,L,F,O,k,K)}function x(w,L,F,O){_();const k=O.attributes,K=F.getAttributes(),X=L.defaultAttributeValues;for(const j in K){const V=K[j];if(V.location>=0){let oe=k[j];if(oe===void 0&&(j==="instanceMatrix"&&w.instanceMatrix&&(oe=w.instanceMatrix),j==="instanceColor"&&w.instanceColor&&(oe=w.instanceColor)),oe!==void 0){const _e=oe.normalized,Re=oe.itemSize,tt=e.get(oe);if(tt===void 0)continue;const wt=tt.buffer,Z=tt.type,he=tt.bytesPerElement,Ne=Z===i.INT||Z===i.UNSIGNED_INT||oe.gpuType===th;if(oe.isInterleavedBufferAttribute){const pe=oe.data,We=pe.stride,Ze=oe.offset;if(pe.isInstancedInterleavedBuffer){for(let je=0;je<V.locationSize;je++)p(V.location+je,pe.meshPerAttribute);w.isInstancedMesh!==!0&&O._maxInstanceCount===void 0&&(O._maxInstanceCount=pe.meshPerAttribute*pe.count)}else for(let je=0;je<V.locationSize;je++)g(V.location+je);i.bindBuffer(i.ARRAY_BUFFER,wt);for(let je=0;je<V.locationSize;je++)M(V.location+je,Re/V.locationSize,Z,_e,We*he,(Ze+Re/V.locationSize*je)*he,Ne)}else{if(oe.isInstancedBufferAttribute){for(let pe=0;pe<V.locationSize;pe++)p(V.location+pe,oe.meshPerAttribute);w.isInstancedMesh!==!0&&O._maxInstanceCount===void 0&&(O._maxInstanceCount=oe.meshPerAttribute*oe.count)}else for(let pe=0;pe<V.locationSize;pe++)g(V.location+pe);i.bindBuffer(i.ARRAY_BUFFER,wt);for(let pe=0;pe<V.locationSize;pe++)M(V.location+pe,Re/V.locationSize,Z,_e,Re*he,Re/V.locationSize*pe*he,Ne)}}else if(X!==void 0){const _e=X[j];if(_e!==void 0)switch(_e.length){case 2:i.vertexAttrib2fv(V.location,_e);break;case 3:i.vertexAttrib3fv(V.location,_e);break;case 4:i.vertexAttrib4fv(V.location,_e);break;default:i.vertexAttrib1fv(V.location,_e)}}}}y()}function E(){C();for(const w in n){const L=n[w];for(const F in L){const O=L[F];for(const k in O)h(O[k].object),delete O[k];delete L[F]}delete n[w]}}function T(w){if(n[w.id]===void 0)return;const L=n[w.id];for(const F in L){const O=L[F];for(const k in O)h(O[k].object),delete O[k];delete L[F]}delete n[w.id]}function P(w){for(const L in n){const F=n[L];if(F[w.id]===void 0)continue;const O=F[w.id];for(const k in O)h(O[k].object),delete O[k];delete F[w.id]}}function C(){b(),o=!0,r!==s&&(r=s,l(r.object))}function b(){s.geometry=null,s.program=null,s.wireframe=!1}return{setup:a,reset:C,resetDefaultState:b,dispose:E,releaseStatesOfGeometry:T,releaseStatesOfProgram:P,initAttributes:_,enableAttribute:g,disableUnusedAttributes:y}}function rx(i,e,t){let n;function s(l){n=l}function r(l,h){i.drawArrays(n,l,h),t.update(h,n,1)}function o(l,h,u){u!==0&&(i.drawArraysInstanced(n,l,h,u),t.update(h,n,u))}function a(l,h,u){if(u===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,l,0,h,0,u);let f=0;for(let m=0;m<u;m++)f+=h[m];t.update(f,n,1)}function c(l,h,u,d){if(u===0)return;const f=e.get("WEBGL_multi_draw");if(f===null)for(let m=0;m<l.length;m++)o(l[m],h[m],d[m]);else{f.multiDrawArraysInstancedWEBGL(n,l,0,h,0,d,0,u);let m=0;for(let _=0;_<u;_++)m+=h[_]*d[_];t.update(m,n,1)}}this.setMode=s,this.render=r,this.renderInstances=o,this.renderMultiDraw=a,this.renderMultiDrawInstances=c}function ox(i,e,t,n){let s;function r(){if(s!==void 0)return s;if(e.has("EXT_texture_filter_anisotropic")===!0){const P=e.get("EXT_texture_filter_anisotropic");s=i.getParameter(P.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else s=0;return s}function o(P){return!(P!==kn&&n.convert(P)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function a(P){const C=P===uo&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(P!==Ai&&n.convert(P)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&P!==Jn&&!C)}function c(P){if(P==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";P="mediump"}return P==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let l=t.precision!==void 0?t.precision:"highp";const h=c(l);h!==l&&(console.warn("THREE.WebGLRenderer:",l,"not supported, using",h,"instead."),l=h);const u=t.logarithmicDepthBuffer===!0,d=t.reverseDepthBuffer===!0&&e.has("EXT_clip_control"),f=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),m=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),_=i.getParameter(i.MAX_TEXTURE_SIZE),g=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),p=i.getParameter(i.MAX_VERTEX_ATTRIBS),y=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),M=i.getParameter(i.MAX_VARYING_VECTORS),x=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),E=m>0,T=i.getParameter(i.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:r,getMaxPrecision:c,textureFormatReadable:o,textureTypeReadable:a,precision:l,logarithmicDepthBuffer:u,reverseDepthBuffer:d,maxTextures:f,maxVertexTextures:m,maxTextureSize:_,maxCubemapSize:g,maxAttributes:p,maxVertexUniforms:y,maxVaryings:M,maxFragmentUniforms:x,vertexTextures:E,maxSamples:T}}function ax(i){const e=this;let t=null,n=0,s=!1,r=!1;const o=new _s,a=new rt,c={value:null,needsUpdate:!1};this.uniform=c,this.numPlanes=0,this.numIntersection=0,this.init=function(u,d){const f=u.length!==0||d||n!==0||s;return s=d,n=u.length,f},this.beginShadows=function(){r=!0,h(null)},this.endShadows=function(){r=!1},this.setGlobalState=function(u,d){t=h(u,d,0)},this.setState=function(u,d,f){const m=u.clippingPlanes,_=u.clipIntersection,g=u.clipShadows,p=i.get(u);if(!s||m===null||m.length===0||r&&!g)r?h(null):l();else{const y=r?0:n,M=y*4;let x=p.clippingState||null;c.value=x,x=h(m,d,M,f);for(let E=0;E!==M;++E)x[E]=t[E];p.clippingState=x,this.numIntersection=_?this.numPlanes:0,this.numPlanes+=y}};function l(){c.value!==t&&(c.value=t,c.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function h(u,d,f,m){const _=u!==null?u.length:0;let g=null;if(_!==0){if(g=c.value,m!==!0||g===null){const p=f+_*4,y=d.matrixWorldInverse;a.getNormalMatrix(y),(g===null||g.length<p)&&(g=new Float32Array(p));for(let M=0,x=f;M!==_;++M,x+=4)o.copy(u[M]).applyMatrix4(y,a),o.normal.toArray(g,x),g[x+3]=o.constant}c.value=g,c.needsUpdate=!0}return e.numPlanes=_,e.numIntersection=0,g}}function cx(i){let e=new WeakMap;function t(o,a){return a===hl?o.mapping=lr:a===ul&&(o.mapping=hr),o}function n(o){if(o&&o.isTexture){const a=o.mapping;if(a===hl||a===ul)if(e.has(o)){const c=e.get(o).texture;return t(c,o.mapping)}else{const c=o.image;if(c&&c.height>0){const l=new v0(c.height);return l.fromEquirectangularTexture(i,o),e.set(o,l),o.addEventListener("dispose",s),t(l.texture,o.mapping)}else return null}}return o}function s(o){const a=o.target;a.removeEventListener("dispose",s);const c=e.get(a);c!==void 0&&(e.delete(a),c.dispose())}function r(){e=new WeakMap}return{get:n,dispose:r}}class Oa extends ff{constructor(e=-1,t=1,n=1,s=-1,r=.1,o=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=s,this.near=r,this.far=o,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,s,r,o){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,s=(this.top+this.bottom)/2;let r=n-e,o=n+e,a=s+t,c=s-t;if(this.view!==null&&this.view.enabled){const l=(this.right-this.left)/this.view.fullWidth/this.zoom,h=(this.top-this.bottom)/this.view.fullHeight/this.zoom;r+=l*this.view.offsetX,o=r+l*this.view.width,a-=h*this.view.offsetY,c=a-h*this.view.height}this.projectionMatrix.makeOrthographic(r,o,a,c,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Qs=4,yu=[.125,.215,.35,.446,.526,.582],ys=20,Mc=new Oa,Mu=new Ve;let wc=null,bc=0,Sc=0,Ec=!1;const xs=(1+Math.sqrt(5))/2,qs=1/xs,wu=[new v(-xs,qs,0),new v(xs,qs,0),new v(-qs,0,xs),new v(qs,0,xs),new v(0,xs,-qs),new v(0,xs,qs),new v(-1,1,-1),new v(1,1,-1),new v(-1,1,1),new v(1,1,1)];class bu{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,s=100){wc=this._renderer.getRenderTarget(),bc=this._renderer.getActiveCubeFace(),Sc=this._renderer.getActiveMipmapLevel(),Ec=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const r=this._allocateTargets();return r.depthBuffer=!0,this._sceneToCubeUV(e,n,s,r),t>0&&this._blur(r,0,0,t),this._applyPMREM(r),this._cleanup(r),r}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=Tu(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=Eu(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(wc,bc,Sc),this._renderer.xr.enabled=Ec,e.scissorTest=!1,Ho(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===lr||e.mapping===hr?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),wc=this._renderer.getRenderTarget(),bc=this._renderer.getActiveCubeFace(),Sc=this._renderer.getActiveMipmapLevel(),Ec=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:Dn,minFilter:Dn,generateMipmaps:!1,type:uo,format:kn,colorSpace:mn,depthBuffer:!1},s=Su(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=Su(e,t,n);const{_lodMax:r}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=lx(r)),this._blurMaterial=hx(r,e,t)}return s}_compileMaterial(e){const t=new Xt(this._lodPlanes[0],e);this._renderer.compile(t,Mc)}_sceneToCubeUV(e,t,n,s){const a=new Tn(90,1,t,n),c=[1,-1,1,1,1,1],l=[1,1,1,-1,-1,-1],h=this._renderer,u=h.autoClear,d=h.toneMapping;h.getClearColor(Mu),h.toneMapping=Ji,h.autoClear=!1;const f=new fn({name:"PMREM.Background",side:yn,depthWrite:!1,depthTest:!1}),m=new Xt(new ht,f);let _=!1;const g=e.background;g?g.isColor&&(f.color.copy(g),e.background=null,_=!0):(f.color.copy(Mu),_=!0);for(let p=0;p<6;p++){const y=p%3;y===0?(a.up.set(0,c[p],0),a.lookAt(l[p],0,0)):y===1?(a.up.set(0,0,c[p]),a.lookAt(0,l[p],0)):(a.up.set(0,c[p],0),a.lookAt(0,0,l[p]));const M=this._cubeSize;Ho(s,y*M,p>2?M:0,M,M),h.setRenderTarget(s),_&&h.render(m,a),h.render(e,a)}m.geometry.dispose(),m.material.dispose(),h.toneMapping=d,h.autoClear=u,e.background=g}_textureToCubeUV(e,t){const n=this._renderer,s=e.mapping===lr||e.mapping===hr;s?(this._cubemapMaterial===null&&(this._cubemapMaterial=Tu()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=Eu());const r=s?this._cubemapMaterial:this._equirectMaterial,o=new Xt(this._lodPlanes[0],r),a=r.uniforms;a.envMap.value=e;const c=this._cubeSize;Ho(t,0,0,3*c,2*c),n.setRenderTarget(t),n.render(o,Mc)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const s=this._lodPlanes.length;for(let r=1;r<s;r++){const o=Math.sqrt(this._sigmas[r]*this._sigmas[r]-this._sigmas[r-1]*this._sigmas[r-1]),a=wu[(s-r-1)%wu.length];this._blur(e,r-1,r,o,a)}t.autoClear=n}_blur(e,t,n,s,r){const o=this._pingPongRenderTarget;this._halfBlur(e,o,t,n,s,"latitudinal",r),this._halfBlur(o,e,n,n,s,"longitudinal",r)}_halfBlur(e,t,n,s,r,o,a){const c=this._renderer,l=this._blurMaterial;o!=="latitudinal"&&o!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const h=3,u=new Xt(this._lodPlanes[s],l),d=l.uniforms,f=this._sizeLods[n]-1,m=isFinite(r)?Math.PI/(2*f):2*Math.PI/(2*ys-1),_=r/m,g=isFinite(r)?1+Math.floor(h*_):ys;g>ys&&console.warn(`sigmaRadians, ${r}, is too large and will clip, as it requested ${g} samples when the maximum is set to ${ys}`);const p=[];let y=0;for(let P=0;P<ys;++P){const C=P/_,b=Math.exp(-C*C/2);p.push(b),P===0?y+=b:P<g&&(y+=2*b)}for(let P=0;P<p.length;P++)p[P]=p[P]/y;d.envMap.value=e.texture,d.samples.value=g,d.weights.value=p,d.latitudinal.value=o==="latitudinal",a&&(d.poleAxis.value=a);const{_lodMax:M}=this;d.dTheta.value=m,d.mipInt.value=M-n;const x=this._sizeLods[s],E=3*x*(s>M-Qs?s-M+Qs:0),T=4*(this._cubeSize-x);Ho(t,E,T,3*x,2*x),c.setRenderTarget(t),c.render(u,Mc)}}function lx(i){const e=[],t=[],n=[];let s=i;const r=i-Qs+1+yu.length;for(let o=0;o<r;o++){const a=Math.pow(2,s);t.push(a);let c=1/a;o>i-Qs?c=yu[o-i+Qs-1]:o===0&&(c=0),n.push(c);const l=1/(a-2),h=-l,u=1+l,d=[h,h,u,h,u,u,h,h,u,u,h,u],f=6,m=6,_=3,g=2,p=1,y=new Float32Array(_*m*f),M=new Float32Array(g*m*f),x=new Float32Array(p*m*f);for(let T=0;T<f;T++){const P=T%3*2/3-1,C=T>2?0:-1,b=[P,C,0,P+2/3,C,0,P+2/3,C+1,0,P,C,0,P+2/3,C+1,0,P,C+1,0];y.set(b,_*m*T),M.set(d,g*m*T);const w=[T,T,T,T,T,T];x.set(w,p*m*T)}const E=new Gt;E.setAttribute("position",new en(y,_)),E.setAttribute("uv",new en(M,g)),E.setAttribute("faceIndex",new en(x,p)),e.push(E),s>Qs&&s--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function Su(i,e,t){const n=new Ts(i,e,t);return n.texture.mapping=Da,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function Ho(i,e,t,n,s){i.viewport.set(e,t,n,s),i.scissor.set(e,t,n,s)}function hx(i,e,t){const n=new Float32Array(ys),s=new v(0,1,0);return new oi({name:"SphericalGaussianBlur",defines:{n:ys,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:s}},vertexShader:uh(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:Zi,depthTest:!1,depthWrite:!1})}function Eu(){return new oi({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:uh(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:Zi,depthTest:!1,depthWrite:!1})}function Tu(){return new oi({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:uh(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Zi,depthTest:!1,depthWrite:!1})}function uh(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}function ux(i){let e=new WeakMap,t=null;function n(a){if(a&&a.isTexture){const c=a.mapping,l=c===hl||c===ul,h=c===lr||c===hr;if(l||h){let u=e.get(a);const d=u!==void 0?u.texture.pmremVersion:0;if(a.isRenderTargetTexture&&a.pmremVersion!==d)return t===null&&(t=new bu(i)),u=l?t.fromEquirectangular(a,u):t.fromCubemap(a,u),u.texture.pmremVersion=a.pmremVersion,e.set(a,u),u.texture;if(u!==void 0)return u.texture;{const f=a.image;return l&&f&&f.height>0||h&&f&&s(f)?(t===null&&(t=new bu(i)),u=l?t.fromEquirectangular(a):t.fromCubemap(a),u.texture.pmremVersion=a.pmremVersion,e.set(a,u),a.addEventListener("dispose",r),u.texture):null}}}return a}function s(a){let c=0;const l=6;for(let h=0;h<l;h++)a[h]!==void 0&&c++;return c===l}function r(a){const c=a.target;c.removeEventListener("dispose",r);const l=e.get(c);l!==void 0&&(e.delete(c),l.dispose())}function o(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:o}}function dx(i){const e={};function t(n){if(e[n]!==void 0)return e[n];let s;switch(n){case"WEBGL_depth_texture":s=i.getExtension("WEBGL_depth_texture")||i.getExtension("MOZ_WEBGL_depth_texture")||i.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":s=i.getExtension("EXT_texture_filter_anisotropic")||i.getExtension("MOZ_EXT_texture_filter_anisotropic")||i.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":s=i.getExtension("WEBGL_compressed_texture_s3tc")||i.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":s=i.getExtension("WEBGL_compressed_texture_pvrtc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:s=i.getExtension(n)}return e[n]=s,s}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const s=t(n);return s===null&&Yr("THREE.WebGLRenderer: "+n+" extension not supported."),s}}}function fx(i,e,t,n){const s={},r=new WeakMap;function o(u){const d=u.target;d.index!==null&&e.remove(d.index);for(const m in d.attributes)e.remove(d.attributes[m]);for(const m in d.morphAttributes){const _=d.morphAttributes[m];for(let g=0,p=_.length;g<p;g++)e.remove(_[g])}d.removeEventListener("dispose",o),delete s[d.id];const f=r.get(d);f&&(e.remove(f),r.delete(d)),n.releaseStatesOfGeometry(d),d.isInstancedBufferGeometry===!0&&delete d._maxInstanceCount,t.memory.geometries--}function a(u,d){return s[d.id]===!0||(d.addEventListener("dispose",o),s[d.id]=!0,t.memory.geometries++),d}function c(u){const d=u.attributes;for(const m in d)e.update(d[m],i.ARRAY_BUFFER);const f=u.morphAttributes;for(const m in f){const _=f[m];for(let g=0,p=_.length;g<p;g++)e.update(_[g],i.ARRAY_BUFFER)}}function l(u){const d=[],f=u.index,m=u.attributes.position;let _=0;if(f!==null){const y=f.array;_=f.version;for(let M=0,x=y.length;M<x;M+=3){const E=y[M+0],T=y[M+1],P=y[M+2];d.push(E,T,T,P,P,E)}}else if(m!==void 0){const y=m.array;_=m.version;for(let M=0,x=y.length/3-1;M<x;M+=3){const E=M+0,T=M+1,P=M+2;d.push(E,T,T,P,P,E)}}else return;const g=new(of(d)?uf:lh)(d,1);g.version=_;const p=r.get(u);p&&e.remove(p),r.set(u,g)}function h(u){const d=r.get(u);if(d){const f=u.index;f!==null&&d.version<f.version&&l(u)}else l(u);return r.get(u)}return{get:a,update:c,getWireframeAttribute:h}}function px(i,e,t){let n;function s(d){n=d}let r,o;function a(d){r=d.type,o=d.bytesPerElement}function c(d,f){i.drawElements(n,f,r,d*o),t.update(f,n,1)}function l(d,f,m){m!==0&&(i.drawElementsInstanced(n,f,r,d*o,m),t.update(f,n,m))}function h(d,f,m){if(m===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,f,0,r,d,0,m);let g=0;for(let p=0;p<m;p++)g+=f[p];t.update(g,n,1)}function u(d,f,m,_){if(m===0)return;const g=e.get("WEBGL_multi_draw");if(g===null)for(let p=0;p<d.length;p++)l(d[p]/o,f[p],_[p]);else{g.multiDrawElementsInstancedWEBGL(n,f,0,r,d,0,_,0,m);let p=0;for(let y=0;y<m;y++)p+=f[y]*_[y];t.update(p,n,1)}}this.setMode=s,this.setIndex=a,this.render=c,this.renderInstances=l,this.renderMultiDraw=h,this.renderMultiDrawInstances=u}function mx(i){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(r,o,a){switch(t.calls++,o){case i.TRIANGLES:t.triangles+=a*(r/3);break;case i.LINES:t.lines+=a*(r/2);break;case i.LINE_STRIP:t.lines+=a*(r-1);break;case i.LINE_LOOP:t.lines+=a*r;break;case i.POINTS:t.points+=a*r;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",o);break}}function s(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:s,update:n}}function gx(i,e,t){const n=new WeakMap,s=new yt;function r(o,a,c){const l=o.morphTargetInfluences,h=a.morphAttributes.position||a.morphAttributes.normal||a.morphAttributes.color,u=h!==void 0?h.length:0;let d=n.get(a);if(d===void 0||d.count!==u){let b=function(){P.dispose(),n.delete(a),a.removeEventListener("dispose",b)};d!==void 0&&d.texture.dispose();const f=a.morphAttributes.position!==void 0,m=a.morphAttributes.normal!==void 0,_=a.morphAttributes.color!==void 0,g=a.morphAttributes.position||[],p=a.morphAttributes.normal||[],y=a.morphAttributes.color||[];let M=0;f===!0&&(M=1),m===!0&&(M=2),_===!0&&(M=3);let x=a.attributes.position.count*M,E=1;x>e.maxTextureSize&&(E=Math.ceil(x/e.maxTextureSize),x=e.maxTextureSize);const T=new Float32Array(x*E*4*u),P=new cf(T,x,E,u);P.type=Jn,P.needsUpdate=!0;const C=M*4;for(let w=0;w<u;w++){const L=g[w],F=p[w],O=y[w],k=x*E*4*w;for(let K=0;K<L.count;K++){const X=K*C;f===!0&&(s.fromBufferAttribute(L,K),T[k+X+0]=s.x,T[k+X+1]=s.y,T[k+X+2]=s.z,T[k+X+3]=0),m===!0&&(s.fromBufferAttribute(F,K),T[k+X+4]=s.x,T[k+X+5]=s.y,T[k+X+6]=s.z,T[k+X+7]=0),_===!0&&(s.fromBufferAttribute(O,K),T[k+X+8]=s.x,T[k+X+9]=s.y,T[k+X+10]=s.z,T[k+X+11]=O.itemSize===4?s.w:1)}}d={count:u,texture:P,size:new te(x,E)},n.set(a,d),a.addEventListener("dispose",b)}if(o.isInstancedMesh===!0&&o.morphTexture!==null)c.getUniforms().setValue(i,"morphTexture",o.morphTexture,t);else{let f=0;for(let _=0;_<l.length;_++)f+=l[_];const m=a.morphTargetsRelative?1:1-f;c.getUniforms().setValue(i,"morphTargetBaseInfluence",m),c.getUniforms().setValue(i,"morphTargetInfluences",l)}c.getUniforms().setValue(i,"morphTargetsTexture",d.texture,t),c.getUniforms().setValue(i,"morphTargetsTextureSize",d.size)}return{update:r}}function _x(i,e,t,n){let s=new WeakMap;function r(c){const l=n.render.frame,h=c.geometry,u=e.get(c,h);if(s.get(u)!==l&&(e.update(u),s.set(u,l)),c.isInstancedMesh&&(c.hasEventListener("dispose",a)===!1&&c.addEventListener("dispose",a),s.get(c)!==l&&(t.update(c.instanceMatrix,i.ARRAY_BUFFER),c.instanceColor!==null&&t.update(c.instanceColor,i.ARRAY_BUFFER),s.set(c,l))),c.isSkinnedMesh){const d=c.skeleton;s.get(d)!==l&&(d.update(),s.set(d,l))}return u}function o(){s=new WeakMap}function a(c){const l=c.target;l.removeEventListener("dispose",a),t.remove(l.instanceMatrix),l.instanceColor!==null&&t.remove(l.instanceColor)}return{update:r,dispose:o}}class gf extends Qt{constructor(e,t,n,s,r,o,a,c,l,h=ir){if(h!==ir&&h!==fr)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&h===ir&&(n=Es),n===void 0&&h===fr&&(n=dr),super(null,s,r,o,a,c,h,n,l),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=a!==void 0?a:pn,this.minFilter=c!==void 0?c:pn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const _f=new Qt,Au=new gf(1,1),xf=new cf,vf=new i0,yf=new pf,Ru=[],Cu=[],Pu=new Float32Array(16),Lu=new Float32Array(9),Iu=new Float32Array(4);function wr(i,e,t){const n=i[0];if(n<=0||n>0)return i;const s=e*t;let r=Ru[s];if(r===void 0&&(r=new Float32Array(s),Ru[s]=r),e!==0){n.toArray(r,0);for(let o=1,a=0;o!==e;++o)a+=t,i[o].toArray(r,a)}return r}function Kt(i,e){if(i.length!==e.length)return!1;for(let t=0,n=i.length;t<n;t++)if(i[t]!==e[t])return!1;return!0}function Zt(i,e){for(let t=0,n=e.length;t<n;t++)i[t]=e[t]}function Fa(i,e){let t=Cu[e];t===void 0&&(t=new Int32Array(e),Cu[e]=t);for(let n=0;n!==e;++n)t[n]=i.allocateTextureUnit();return t}function xx(i,e){const t=this.cache;t[0]!==e&&(i.uniform1f(this.addr,e),t[0]=e)}function vx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Kt(t,e))return;i.uniform2fv(this.addr,e),Zt(t,e)}}function yx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(i.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(Kt(t,e))return;i.uniform3fv(this.addr,e),Zt(t,e)}}function Mx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Kt(t,e))return;i.uniform4fv(this.addr,e),Zt(t,e)}}function wx(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Kt(t,e))return;i.uniformMatrix2fv(this.addr,!1,e),Zt(t,e)}else{if(Kt(t,n))return;Iu.set(n),i.uniformMatrix2fv(this.addr,!1,Iu),Zt(t,n)}}function bx(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Kt(t,e))return;i.uniformMatrix3fv(this.addr,!1,e),Zt(t,e)}else{if(Kt(t,n))return;Lu.set(n),i.uniformMatrix3fv(this.addr,!1,Lu),Zt(t,n)}}function Sx(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Kt(t,e))return;i.uniformMatrix4fv(this.addr,!1,e),Zt(t,e)}else{if(Kt(t,n))return;Pu.set(n),i.uniformMatrix4fv(this.addr,!1,Pu),Zt(t,n)}}function Ex(i,e){const t=this.cache;t[0]!==e&&(i.uniform1i(this.addr,e),t[0]=e)}function Tx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Kt(t,e))return;i.uniform2iv(this.addr,e),Zt(t,e)}}function Ax(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Kt(t,e))return;i.uniform3iv(this.addr,e),Zt(t,e)}}function Rx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Kt(t,e))return;i.uniform4iv(this.addr,e),Zt(t,e)}}function Cx(i,e){const t=this.cache;t[0]!==e&&(i.uniform1ui(this.addr,e),t[0]=e)}function Px(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Kt(t,e))return;i.uniform2uiv(this.addr,e),Zt(t,e)}}function Lx(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Kt(t,e))return;i.uniform3uiv(this.addr,e),Zt(t,e)}}function Ix(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Kt(t,e))return;i.uniform4uiv(this.addr,e),Zt(t,e)}}function Dx(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s);let r;this.type===i.SAMPLER_2D_SHADOW?(Au.compareFunction=rf,r=Au):r=_f,t.setTexture2D(e||r,s)}function Nx(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture3D(e||vf,s)}function Ux(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTextureCube(e||yf,s)}function Ox(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture2DArray(e||xf,s)}function Fx(i){switch(i){case 5126:return xx;case 35664:return vx;case 35665:return yx;case 35666:return Mx;case 35674:return wx;case 35675:return bx;case 35676:return Sx;case 5124:case 35670:return Ex;case 35667:case 35671:return Tx;case 35668:case 35672:return Ax;case 35669:case 35673:return Rx;case 5125:return Cx;case 36294:return Px;case 36295:return Lx;case 36296:return Ix;case 35678:case 36198:case 36298:case 36306:case 35682:return Dx;case 35679:case 36299:case 36307:return Nx;case 35680:case 36300:case 36308:case 36293:return Ux;case 36289:case 36303:case 36311:case 36292:return Ox}}function Bx(i,e){i.uniform1fv(this.addr,e)}function kx(i,e){const t=wr(e,this.size,2);i.uniform2fv(this.addr,t)}function zx(i,e){const t=wr(e,this.size,3);i.uniform3fv(this.addr,t)}function Hx(i,e){const t=wr(e,this.size,4);i.uniform4fv(this.addr,t)}function Gx(i,e){const t=wr(e,this.size,4);i.uniformMatrix2fv(this.addr,!1,t)}function Vx(i,e){const t=wr(e,this.size,9);i.uniformMatrix3fv(this.addr,!1,t)}function Wx(i,e){const t=wr(e,this.size,16);i.uniformMatrix4fv(this.addr,!1,t)}function Xx(i,e){i.uniform1iv(this.addr,e)}function qx(i,e){i.uniform2iv(this.addr,e)}function jx(i,e){i.uniform3iv(this.addr,e)}function $x(i,e){i.uniform4iv(this.addr,e)}function Yx(i,e){i.uniform1uiv(this.addr,e)}function Kx(i,e){i.uniform2uiv(this.addr,e)}function Zx(i,e){i.uniform3uiv(this.addr,e)}function Jx(i,e){i.uniform4uiv(this.addr,e)}function Qx(i,e,t){const n=this.cache,s=e.length,r=Fa(t,s);Kt(n,r)||(i.uniform1iv(this.addr,r),Zt(n,r));for(let o=0;o!==s;++o)t.setTexture2D(e[o]||_f,r[o])}function ev(i,e,t){const n=this.cache,s=e.length,r=Fa(t,s);Kt(n,r)||(i.uniform1iv(this.addr,r),Zt(n,r));for(let o=0;o!==s;++o)t.setTexture3D(e[o]||vf,r[o])}function tv(i,e,t){const n=this.cache,s=e.length,r=Fa(t,s);Kt(n,r)||(i.uniform1iv(this.addr,r),Zt(n,r));for(let o=0;o!==s;++o)t.setTextureCube(e[o]||yf,r[o])}function nv(i,e,t){const n=this.cache,s=e.length,r=Fa(t,s);Kt(n,r)||(i.uniform1iv(this.addr,r),Zt(n,r));for(let o=0;o!==s;++o)t.setTexture2DArray(e[o]||xf,r[o])}function iv(i){switch(i){case 5126:return Bx;case 35664:return kx;case 35665:return zx;case 35666:return Hx;case 35674:return Gx;case 35675:return Vx;case 35676:return Wx;case 5124:case 35670:return Xx;case 35667:case 35671:return qx;case 35668:case 35672:return jx;case 35669:case 35673:return $x;case 5125:return Yx;case 36294:return Kx;case 36295:return Zx;case 36296:return Jx;case 35678:case 36198:case 36298:case 36306:case 35682:return Qx;case 35679:case 36299:case 36307:return ev;case 35680:case 36300:case 36308:case 36293:return tv;case 36289:case 36303:case 36311:case 36292:return nv}}class sv{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=Fx(t.type)}}class rv{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=iv(t.type)}}class ov{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const s=this.seq;for(let r=0,o=s.length;r!==o;++r){const a=s[r];a.setValue(e,t[a.id],n)}}}const Tc=/(\w+)(\])?(\[|\.)?/g;function Du(i,e){i.seq.push(e),i.map[e.id]=e}function av(i,e,t){const n=i.name,s=n.length;for(Tc.lastIndex=0;;){const r=Tc.exec(n),o=Tc.lastIndex;let a=r[1];const c=r[2]==="]",l=r[3];if(c&&(a=a|0),l===void 0||l==="["&&o+2===s){Du(t,l===void 0?new sv(a,i,e):new rv(a,i,e));break}else{let u=t.map[a];u===void 0&&(u=new ov(a),Du(t,u)),t=u}}}class ga{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let s=0;s<n;++s){const r=e.getActiveUniform(t,s),o=e.getUniformLocation(t,r.name);av(r,o,this)}}setValue(e,t,n,s){const r=this.map[t];r!==void 0&&r.setValue(e,n,s)}setOptional(e,t,n){const s=t[n];s!==void 0&&this.setValue(e,n,s)}static upload(e,t,n,s){for(let r=0,o=t.length;r!==o;++r){const a=t[r],c=n[a.id];c.needsUpdate!==!1&&a.setValue(e,c.value,s)}}static seqWithValue(e,t){const n=[];for(let s=0,r=e.length;s!==r;++s){const o=e[s];o.id in t&&n.push(o)}return n}}function Nu(i,e,t){const n=i.createShader(e);return i.shaderSource(n,t),i.compileShader(n),n}const cv=37297;let lv=0;function hv(i,e){const t=i.split(`
`),n=[],s=Math.max(e-6,0),r=Math.min(e+6,t.length);for(let o=s;o<r;o++){const a=o+1;n.push(`${a===e?">":" "} ${a}: ${t[o]}`)}return n.join(`
`)}const Uu=new rt;function uv(i){ft._getMatrix(Uu,ft.workingColorSpace,i);const e=`mat3( ${Uu.elements.map(t=>t.toFixed(4))} )`;switch(ft.getTransfer(i)){case Na:return[e,"LinearTransferOETF"];case Rt:return[e,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",i),[e,"LinearTransferOETF"]}}function Ou(i,e,t){const n=i.getShaderParameter(e,i.COMPILE_STATUS),s=i.getShaderInfoLog(e).trim();if(n&&s==="")return"";const r=/ERROR: 0:(\d+)/.exec(s);if(r){const o=parseInt(r[1]);return t.toUpperCase()+`

`+s+`

`+hv(i.getShaderSource(e),o)}else return s}function dv(i,e){const t=uv(e);return[`vec4 ${i}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}function fv(i,e){let t;switch(e){case fm:t="Linear";break;case pm:t="Reinhard";break;case mm:t="Cineon";break;case gm:t="ACESFilmic";break;case xm:t="AgX";break;case vm:t="Neutral";break;case _m:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+i+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const Go=new v;function pv(){ft.getLuminanceCoefficients(Go);const i=Go.x.toFixed(4),e=Go.y.toFixed(4),t=Go.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function mv(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Kr).join(`
`)}function gv(i){const e=[];for(const t in i){const n=i[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function _v(i,e){const t={},n=i.getProgramParameter(e,i.ACTIVE_ATTRIBUTES);for(let s=0;s<n;s++){const r=i.getActiveAttrib(e,s),o=r.name;let a=1;r.type===i.FLOAT_MAT2&&(a=2),r.type===i.FLOAT_MAT3&&(a=3),r.type===i.FLOAT_MAT4&&(a=4),t[o]={type:r.type,location:i.getAttribLocation(e,o),locationSize:a}}return t}function Kr(i){return i!==""}function Fu(i,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function Bu(i,e){return i.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const xv=/^[ \t]*#include +<([\w\d./]+)>/gm;function zl(i){return i.replace(xv,yv)}const vv=new Map;function yv(i,e){let t=at[e];if(t===void 0){const n=vv.get(e);if(n!==void 0)t=at[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return zl(t)}const Mv=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function ku(i){return i.replace(Mv,wv)}function wv(i,e,t,n){let s="";for(let r=parseInt(e);r<parseInt(t);r++)s+=n.replace(/\[\s*i\s*\]/g,"[ "+r+" ]").replace(/UNROLLED_LOOP_INDEX/g,r);return s}function zu(i){let e=`precision ${i.precision} float;
	precision ${i.precision} int;
	precision ${i.precision} sampler2D;
	precision ${i.precision} samplerCube;
	precision ${i.precision} sampler3D;
	precision ${i.precision} sampler2DArray;
	precision ${i.precision} sampler2DShadow;
	precision ${i.precision} samplerCubeShadow;
	precision ${i.precision} sampler2DArrayShadow;
	precision ${i.precision} isampler2D;
	precision ${i.precision} isampler3D;
	precision ${i.precision} isamplerCube;
	precision ${i.precision} isampler2DArray;
	precision ${i.precision} usampler2D;
	precision ${i.precision} usampler3D;
	precision ${i.precision} usamplerCube;
	precision ${i.precision} usampler2DArray;
	`;return i.precision==="highp"?e+=`
#define HIGH_PRECISION`:i.precision==="mediump"?e+=`
#define MEDIUM_PRECISION`:i.precision==="lowp"&&(e+=`
#define LOW_PRECISION`),e}function bv(i){let e="SHADOWMAP_TYPE_BASIC";return i.shadowMapType===Vd?e="SHADOWMAP_TYPE_PCF":i.shadowMapType===qp?e="SHADOWMAP_TYPE_PCF_SOFT":i.shadowMapType===Mi&&(e="SHADOWMAP_TYPE_VSM"),e}function Sv(i){let e="ENVMAP_TYPE_CUBE";if(i.envMap)switch(i.envMapMode){case lr:case hr:e="ENVMAP_TYPE_CUBE";break;case Da:e="ENVMAP_TYPE_CUBE_UV";break}return e}function Ev(i){let e="ENVMAP_MODE_REFLECTION";if(i.envMap)switch(i.envMapMode){case hr:e="ENVMAP_MODE_REFRACTION";break}return e}function Tv(i){let e="ENVMAP_BLENDING_NONE";if(i.envMap)switch(i.combine){case Wd:e="ENVMAP_BLENDING_MULTIPLY";break;case um:e="ENVMAP_BLENDING_MIX";break;case dm:e="ENVMAP_BLENDING_ADD";break}return e}function Av(i){const e=i.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),112)),texelHeight:n,maxMip:t}}function Rv(i,e,t,n){const s=i.getContext(),r=t.defines;let o=t.vertexShader,a=t.fragmentShader;const c=bv(t),l=Sv(t),h=Ev(t),u=Tv(t),d=Av(t),f=mv(t),m=gv(r),_=s.createProgram();let g,p,y=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(g=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m].filter(Kr).join(`
`),g.length>0&&(g+=`
`),p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m].filter(Kr).join(`
`),p.length>0&&(p+=`
`)):(g=[zu(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+c:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Kr).join(`
`),p=[zu(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+l:"",t.envMap?"#define "+h:"",t.envMap?"#define "+u:"",d?"#define CUBEUV_TEXEL_WIDTH "+d.texelWidth:"",d?"#define CUBEUV_TEXEL_HEIGHT "+d.texelHeight:"",d?"#define CUBEUV_MAX_MIP "+d.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+c:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==Ji?"#define TONE_MAPPING":"",t.toneMapping!==Ji?at.tonemapping_pars_fragment:"",t.toneMapping!==Ji?fv("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",at.colorspace_pars_fragment,dv("linearToOutputTexel",t.outputColorSpace),pv(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(Kr).join(`
`)),o=zl(o),o=Fu(o,t),o=Bu(o,t),a=zl(a),a=Fu(a,t),a=Bu(a,t),o=ku(o),a=ku(a),t.isRawShaderMaterial!==!0&&(y=`#version 300 es
`,g=[f,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+g,p=["#define varying in",t.glslVersion===Jh?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Jh?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+p);const M=y+g+o,x=y+p+a,E=Nu(s,s.VERTEX_SHADER,M),T=Nu(s,s.FRAGMENT_SHADER,x);s.attachShader(_,E),s.attachShader(_,T),t.index0AttributeName!==void 0?s.bindAttribLocation(_,0,t.index0AttributeName):t.morphTargets===!0&&s.bindAttribLocation(_,0,"position"),s.linkProgram(_);function P(L){if(i.debug.checkShaderErrors){const F=s.getProgramInfoLog(_).trim(),O=s.getShaderInfoLog(E).trim(),k=s.getShaderInfoLog(T).trim();let K=!0,X=!0;if(s.getProgramParameter(_,s.LINK_STATUS)===!1)if(K=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(s,_,E,T);else{const j=Ou(s,E,"vertex"),V=Ou(s,T,"fragment");console.error("THREE.WebGLProgram: Shader Error "+s.getError()+" - VALIDATE_STATUS "+s.getProgramParameter(_,s.VALIDATE_STATUS)+`

Material Name: `+L.name+`
Material Type: `+L.type+`

Program Info Log: `+F+`
`+j+`
`+V)}else F!==""?console.warn("THREE.WebGLProgram: Program Info Log:",F):(O===""||k==="")&&(X=!1);X&&(L.diagnostics={runnable:K,programLog:F,vertexShader:{log:O,prefix:g},fragmentShader:{log:k,prefix:p}})}s.deleteShader(E),s.deleteShader(T),C=new ga(s,_),b=_v(s,_)}let C;this.getUniforms=function(){return C===void 0&&P(this),C};let b;this.getAttributes=function(){return b===void 0&&P(this),b};let w=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return w===!1&&(w=s.getProgramParameter(_,cv)),w},this.destroy=function(){n.releaseStatesOfProgram(this),s.deleteProgram(_),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=lv++,this.cacheKey=e,this.usedTimes=1,this.program=_,this.vertexShader=E,this.fragmentShader=T,this}let Cv=0;class Pv{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,s=this._getShaderStage(t),r=this._getShaderStage(n),o=this._getShaderCacheForMaterial(e);return o.has(s)===!1&&(o.add(s),s.usedTimes++),o.has(r)===!1&&(o.add(r),r.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new Lv(e),t.set(e,n)),n}}class Lv{constructor(e){this.id=Cv++,this.code=e,this.usedTimes=0}}function Iv(i,e,t,n,s,r,o){const a=new lf,c=new Pv,l=new Set,h=[],u=s.logarithmicDepthBuffer,d=s.vertexTextures;let f=s.precision;const m={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function _(b){return l.add(b),b===0?"uv":`uv${b}`}function g(b,w,L,F,O){const k=F.fog,K=O.geometry,X=b.isMeshStandardMaterial?F.environment:null,j=(b.isMeshStandardMaterial?t:e).get(b.envMap||X),V=j&&j.mapping===Da?j.image.height:null,oe=m[b.type];b.precision!==null&&(f=s.getMaxPrecision(b.precision),f!==b.precision&&console.warn("THREE.WebGLProgram.getParameters:",b.precision,"not supported, using",f,"instead."));const _e=K.morphAttributes.position||K.morphAttributes.normal||K.morphAttributes.color,Re=_e!==void 0?_e.length:0;let tt=0;K.morphAttributes.position!==void 0&&(tt=1),K.morphAttributes.normal!==void 0&&(tt=2),K.morphAttributes.color!==void 0&&(tt=3);let wt,Z,he,Ne;if(oe){const Et=ni[oe];wt=Et.vertexShader,Z=Et.fragmentShader}else wt=b.vertexShader,Z=b.fragmentShader,c.update(b),he=c.getVertexShaderID(b),Ne=c.getFragmentShaderID(b);const pe=i.getRenderTarget(),We=i.state.buffers.depth.getReversed(),Ze=O.isInstancedMesh===!0,je=O.isBatchedMesh===!0,gt=!!b.map,Q=!!b.matcap,le=!!j,I=!!b.aoMap,ze=!!b.lightMap,re=!!b.bumpMap,Le=!!b.normalMap,ge=!!b.displacementMap,Xe=!!b.emissiveMap,Ce=!!b.metalnessMap,R=!!b.roughnessMap,S=b.anisotropy>0,B=b.clearcoat>0,$=b.dispersion>0,ee=b.iridescence>0,Y=b.sheen>0,Oe=b.transmission>0,ye=S&&!!b.anisotropyMap,Pe=B&&!!b.clearcoatMap,dt=B&&!!b.clearcoatNormalMap,ae=B&&!!b.clearcoatRoughnessMap,Ie=ee&&!!b.iridescenceMap,qe=ee&&!!b.iridescenceThicknessMap,Ye=Y&&!!b.sheenColorMap,De=Y&&!!b.sheenRoughnessMap,pt=!!b.specularMap,ot=!!b.specularColorMap,Lt=!!b.specularIntensityMap,D=Oe&&!!b.transmissionMap,Me=Oe&&!!b.thicknessMap,q=!!b.gradientMap,J=!!b.alphaMap,Se=b.alphaTest>0,we=!!b.alphaHash,it=!!b.extensions;let Wt=Ji;b.toneMapped&&(pe===null||pe.isXRRenderTarget===!0)&&(Wt=i.toneMapping);const on={shaderID:oe,shaderType:b.type,shaderName:b.name,vertexShader:wt,fragmentShader:Z,defines:b.defines,customVertexShaderID:he,customFragmentShaderID:Ne,isRawShaderMaterial:b.isRawShaderMaterial===!0,glslVersion:b.glslVersion,precision:f,batching:je,batchingColor:je&&O._colorsTexture!==null,instancing:Ze,instancingColor:Ze&&O.instanceColor!==null,instancingMorph:Ze&&O.morphTexture!==null,supportsVertexTextures:d,outputColorSpace:pe===null?i.outputColorSpace:pe.isXRRenderTarget===!0?pe.texture.colorSpace:mn,alphaToCoverage:!!b.alphaToCoverage,map:gt,matcap:Q,envMap:le,envMapMode:le&&j.mapping,envMapCubeUVHeight:V,aoMap:I,lightMap:ze,bumpMap:re,normalMap:Le,displacementMap:d&&ge,emissiveMap:Xe,normalMapObjectSpace:Le&&b.normalMapType===Em,normalMapTangentSpace:Le&&b.normalMapType===sf,metalnessMap:Ce,roughnessMap:R,anisotropy:S,anisotropyMap:ye,clearcoat:B,clearcoatMap:Pe,clearcoatNormalMap:dt,clearcoatRoughnessMap:ae,dispersion:$,iridescence:ee,iridescenceMap:Ie,iridescenceThicknessMap:qe,sheen:Y,sheenColorMap:Ye,sheenRoughnessMap:De,specularMap:pt,specularColorMap:ot,specularIntensityMap:Lt,transmission:Oe,transmissionMap:D,thicknessMap:Me,gradientMap:q,opaque:b.transparent===!1&&b.blending===nr&&b.alphaToCoverage===!1,alphaMap:J,alphaTest:Se,alphaHash:we,combine:b.combine,mapUv:gt&&_(b.map.channel),aoMapUv:I&&_(b.aoMap.channel),lightMapUv:ze&&_(b.lightMap.channel),bumpMapUv:re&&_(b.bumpMap.channel),normalMapUv:Le&&_(b.normalMap.channel),displacementMapUv:ge&&_(b.displacementMap.channel),emissiveMapUv:Xe&&_(b.emissiveMap.channel),metalnessMapUv:Ce&&_(b.metalnessMap.channel),roughnessMapUv:R&&_(b.roughnessMap.channel),anisotropyMapUv:ye&&_(b.anisotropyMap.channel),clearcoatMapUv:Pe&&_(b.clearcoatMap.channel),clearcoatNormalMapUv:dt&&_(b.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:ae&&_(b.clearcoatRoughnessMap.channel),iridescenceMapUv:Ie&&_(b.iridescenceMap.channel),iridescenceThicknessMapUv:qe&&_(b.iridescenceThicknessMap.channel),sheenColorMapUv:Ye&&_(b.sheenColorMap.channel),sheenRoughnessMapUv:De&&_(b.sheenRoughnessMap.channel),specularMapUv:pt&&_(b.specularMap.channel),specularColorMapUv:ot&&_(b.specularColorMap.channel),specularIntensityMapUv:Lt&&_(b.specularIntensityMap.channel),transmissionMapUv:D&&_(b.transmissionMap.channel),thicknessMapUv:Me&&_(b.thicknessMap.channel),alphaMapUv:J&&_(b.alphaMap.channel),vertexTangents:!!K.attributes.tangent&&(Le||S),vertexColors:b.vertexColors,vertexAlphas:b.vertexColors===!0&&!!K.attributes.color&&K.attributes.color.itemSize===4,pointsUvs:O.isPoints===!0&&!!K.attributes.uv&&(gt||J),fog:!!k,useFog:b.fog===!0,fogExp2:!!k&&k.isFogExp2,flatShading:b.flatShading===!0,sizeAttenuation:b.sizeAttenuation===!0,logarithmicDepthBuffer:u,reverseDepthBuffer:We,skinning:O.isSkinnedMesh===!0,morphTargets:K.morphAttributes.position!==void 0,morphNormals:K.morphAttributes.normal!==void 0,morphColors:K.morphAttributes.color!==void 0,morphTargetsCount:Re,morphTextureStride:tt,numDirLights:w.directional.length,numPointLights:w.point.length,numSpotLights:w.spot.length,numSpotLightMaps:w.spotLightMap.length,numRectAreaLights:w.rectArea.length,numHemiLights:w.hemi.length,numDirLightShadows:w.directionalShadowMap.length,numPointLightShadows:w.pointShadowMap.length,numSpotLightShadows:w.spotShadowMap.length,numSpotLightShadowsWithMaps:w.numSpotLightShadowsWithMaps,numLightProbes:w.numLightProbes,numClippingPlanes:o.numPlanes,numClipIntersection:o.numIntersection,dithering:b.dithering,shadowMapEnabled:i.shadowMap.enabled&&L.length>0,shadowMapType:i.shadowMap.type,toneMapping:Wt,decodeVideoTexture:gt&&b.map.isVideoTexture===!0&&ft.getTransfer(b.map.colorSpace)===Rt,decodeVideoTextureEmissive:Xe&&b.emissiveMap.isVideoTexture===!0&&ft.getTransfer(b.emissiveMap.colorSpace)===Rt,premultipliedAlpha:b.premultipliedAlpha,doubleSided:b.side===An,flipSided:b.side===yn,useDepthPacking:b.depthPacking>=0,depthPacking:b.depthPacking||0,index0AttributeName:b.index0AttributeName,extensionClipCullDistance:it&&b.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(it&&b.extensions.multiDraw===!0||je)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:b.customProgramCacheKey()};return on.vertexUv1s=l.has(1),on.vertexUv2s=l.has(2),on.vertexUv3s=l.has(3),l.clear(),on}function p(b){const w=[];if(b.shaderID?w.push(b.shaderID):(w.push(b.customVertexShaderID),w.push(b.customFragmentShaderID)),b.defines!==void 0)for(const L in b.defines)w.push(L),w.push(b.defines[L]);return b.isRawShaderMaterial===!1&&(y(w,b),M(w,b),w.push(i.outputColorSpace)),w.push(b.customProgramCacheKey),w.join()}function y(b,w){b.push(w.precision),b.push(w.outputColorSpace),b.push(w.envMapMode),b.push(w.envMapCubeUVHeight),b.push(w.mapUv),b.push(w.alphaMapUv),b.push(w.lightMapUv),b.push(w.aoMapUv),b.push(w.bumpMapUv),b.push(w.normalMapUv),b.push(w.displacementMapUv),b.push(w.emissiveMapUv),b.push(w.metalnessMapUv),b.push(w.roughnessMapUv),b.push(w.anisotropyMapUv),b.push(w.clearcoatMapUv),b.push(w.clearcoatNormalMapUv),b.push(w.clearcoatRoughnessMapUv),b.push(w.iridescenceMapUv),b.push(w.iridescenceThicknessMapUv),b.push(w.sheenColorMapUv),b.push(w.sheenRoughnessMapUv),b.push(w.specularMapUv),b.push(w.specularColorMapUv),b.push(w.specularIntensityMapUv),b.push(w.transmissionMapUv),b.push(w.thicknessMapUv),b.push(w.combine),b.push(w.fogExp2),b.push(w.sizeAttenuation),b.push(w.morphTargetsCount),b.push(w.morphAttributeCount),b.push(w.numDirLights),b.push(w.numPointLights),b.push(w.numSpotLights),b.push(w.numSpotLightMaps),b.push(w.numHemiLights),b.push(w.numRectAreaLights),b.push(w.numDirLightShadows),b.push(w.numPointLightShadows),b.push(w.numSpotLightShadows),b.push(w.numSpotLightShadowsWithMaps),b.push(w.numLightProbes),b.push(w.shadowMapType),b.push(w.toneMapping),b.push(w.numClippingPlanes),b.push(w.numClipIntersection),b.push(w.depthPacking)}function M(b,w){a.disableAll(),w.supportsVertexTextures&&a.enable(0),w.instancing&&a.enable(1),w.instancingColor&&a.enable(2),w.instancingMorph&&a.enable(3),w.matcap&&a.enable(4),w.envMap&&a.enable(5),w.normalMapObjectSpace&&a.enable(6),w.normalMapTangentSpace&&a.enable(7),w.clearcoat&&a.enable(8),w.iridescence&&a.enable(9),w.alphaTest&&a.enable(10),w.vertexColors&&a.enable(11),w.vertexAlphas&&a.enable(12),w.vertexUv1s&&a.enable(13),w.vertexUv2s&&a.enable(14),w.vertexUv3s&&a.enable(15),w.vertexTangents&&a.enable(16),w.anisotropy&&a.enable(17),w.alphaHash&&a.enable(18),w.batching&&a.enable(19),w.dispersion&&a.enable(20),w.batchingColor&&a.enable(21),b.push(a.mask),a.disableAll(),w.fog&&a.enable(0),w.useFog&&a.enable(1),w.flatShading&&a.enable(2),w.logarithmicDepthBuffer&&a.enable(3),w.reverseDepthBuffer&&a.enable(4),w.skinning&&a.enable(5),w.morphTargets&&a.enable(6),w.morphNormals&&a.enable(7),w.morphColors&&a.enable(8),w.premultipliedAlpha&&a.enable(9),w.shadowMapEnabled&&a.enable(10),w.doubleSided&&a.enable(11),w.flipSided&&a.enable(12),w.useDepthPacking&&a.enable(13),w.dithering&&a.enable(14),w.transmission&&a.enable(15),w.sheen&&a.enable(16),w.opaque&&a.enable(17),w.pointsUvs&&a.enable(18),w.decodeVideoTexture&&a.enable(19),w.decodeVideoTextureEmissive&&a.enable(20),w.alphaToCoverage&&a.enable(21),b.push(a.mask)}function x(b){const w=m[b.type];let L;if(w){const F=ni[w];L=m0.clone(F.uniforms)}else L=b.uniforms;return L}function E(b,w){let L;for(let F=0,O=h.length;F<O;F++){const k=h[F];if(k.cacheKey===w){L=k,++L.usedTimes;break}}return L===void 0&&(L=new Rv(i,w,b,r),h.push(L)),L}function T(b){if(--b.usedTimes===0){const w=h.indexOf(b);h[w]=h[h.length-1],h.pop(),b.destroy()}}function P(b){c.remove(b)}function C(){c.dispose()}return{getParameters:g,getProgramCacheKey:p,getUniforms:x,acquireProgram:E,releaseProgram:T,releaseShaderCache:P,programs:h,dispose:C}}function Dv(){let i=new WeakMap;function e(o){return i.has(o)}function t(o){let a=i.get(o);return a===void 0&&(a={},i.set(o,a)),a}function n(o){i.delete(o)}function s(o,a,c){i.get(o)[a]=c}function r(){i=new WeakMap}return{has:e,get:t,remove:n,update:s,dispose:r}}function Nv(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.material.id!==e.material.id?i.material.id-e.material.id:i.z!==e.z?i.z-e.z:i.id-e.id}function Hu(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.z!==e.z?e.z-i.z:i.id-e.id}function Gu(){const i=[];let e=0;const t=[],n=[],s=[];function r(){e=0,t.length=0,n.length=0,s.length=0}function o(u,d,f,m,_,g){let p=i[e];return p===void 0?(p={id:u.id,object:u,geometry:d,material:f,groupOrder:m,renderOrder:u.renderOrder,z:_,group:g},i[e]=p):(p.id=u.id,p.object=u,p.geometry=d,p.material=f,p.groupOrder=m,p.renderOrder=u.renderOrder,p.z=_,p.group=g),e++,p}function a(u,d,f,m,_,g){const p=o(u,d,f,m,_,g);f.transmission>0?n.push(p):f.transparent===!0?s.push(p):t.push(p)}function c(u,d,f,m,_,g){const p=o(u,d,f,m,_,g);f.transmission>0?n.unshift(p):f.transparent===!0?s.unshift(p):t.unshift(p)}function l(u,d){t.length>1&&t.sort(u||Nv),n.length>1&&n.sort(d||Hu),s.length>1&&s.sort(d||Hu)}function h(){for(let u=e,d=i.length;u<d;u++){const f=i[u];if(f.id===null)break;f.id=null,f.object=null,f.geometry=null,f.material=null,f.group=null}}return{opaque:t,transmissive:n,transparent:s,init:r,push:a,unshift:c,finish:h,sort:l}}function Uv(){let i=new WeakMap;function e(n,s){const r=i.get(n);let o;return r===void 0?(o=new Gu,i.set(n,[o])):s>=r.length?(o=new Gu,r.push(o)):o=r[s],o}function t(){i=new WeakMap}return{get:e,dispose:t}}function Ov(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new v,color:new Ve};break;case"SpotLight":t={position:new v,direction:new v,color:new Ve,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new v,color:new Ve,distance:0,decay:0};break;case"HemisphereLight":t={direction:new v,skyColor:new Ve,groundColor:new Ve};break;case"RectAreaLight":t={color:new Ve,position:new v,halfWidth:new v,halfHeight:new v};break}return i[e.id]=t,t}}}function Fv(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new te};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new te};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new te,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[e.id]=t,t}}}let Bv=0;function kv(i,e){return(e.castShadow?2:0)-(i.castShadow?2:0)+(e.map?1:0)-(i.map?1:0)}function zv(i){const e=new Ov,t=Fv(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let l=0;l<9;l++)n.probe.push(new v);const s=new v,r=new Ae,o=new Ae;function a(l){let h=0,u=0,d=0;for(let b=0;b<9;b++)n.probe[b].set(0,0,0);let f=0,m=0,_=0,g=0,p=0,y=0,M=0,x=0,E=0,T=0,P=0;l.sort(kv);for(let b=0,w=l.length;b<w;b++){const L=l[b],F=L.color,O=L.intensity,k=L.distance,K=L.shadow&&L.shadow.map?L.shadow.map.texture:null;if(L.isAmbientLight)h+=F.r*O,u+=F.g*O,d+=F.b*O;else if(L.isLightProbe){for(let X=0;X<9;X++)n.probe[X].addScaledVector(L.sh.coefficients[X],O);P++}else if(L.isDirectionalLight){const X=e.get(L);if(X.color.copy(L.color).multiplyScalar(L.intensity),L.castShadow){const j=L.shadow,V=t.get(L);V.shadowIntensity=j.intensity,V.shadowBias=j.bias,V.shadowNormalBias=j.normalBias,V.shadowRadius=j.radius,V.shadowMapSize=j.mapSize,n.directionalShadow[f]=V,n.directionalShadowMap[f]=K,n.directionalShadowMatrix[f]=L.shadow.matrix,y++}n.directional[f]=X,f++}else if(L.isSpotLight){const X=e.get(L);X.position.setFromMatrixPosition(L.matrixWorld),X.color.copy(F).multiplyScalar(O),X.distance=k,X.coneCos=Math.cos(L.angle),X.penumbraCos=Math.cos(L.angle*(1-L.penumbra)),X.decay=L.decay,n.spot[_]=X;const j=L.shadow;if(L.map&&(n.spotLightMap[E]=L.map,E++,j.updateMatrices(L),L.castShadow&&T++),n.spotLightMatrix[_]=j.matrix,L.castShadow){const V=t.get(L);V.shadowIntensity=j.intensity,V.shadowBias=j.bias,V.shadowNormalBias=j.normalBias,V.shadowRadius=j.radius,V.shadowMapSize=j.mapSize,n.spotShadow[_]=V,n.spotShadowMap[_]=K,x++}_++}else if(L.isRectAreaLight){const X=e.get(L);X.color.copy(F).multiplyScalar(O),X.halfWidth.set(L.width*.5,0,0),X.halfHeight.set(0,L.height*.5,0),n.rectArea[g]=X,g++}else if(L.isPointLight){const X=e.get(L);if(X.color.copy(L.color).multiplyScalar(L.intensity),X.distance=L.distance,X.decay=L.decay,L.castShadow){const j=L.shadow,V=t.get(L);V.shadowIntensity=j.intensity,V.shadowBias=j.bias,V.shadowNormalBias=j.normalBias,V.shadowRadius=j.radius,V.shadowMapSize=j.mapSize,V.shadowCameraNear=j.camera.near,V.shadowCameraFar=j.camera.far,n.pointShadow[m]=V,n.pointShadowMap[m]=K,n.pointShadowMatrix[m]=L.shadow.matrix,M++}n.point[m]=X,m++}else if(L.isHemisphereLight){const X=e.get(L);X.skyColor.copy(L.color).multiplyScalar(O),X.groundColor.copy(L.groundColor).multiplyScalar(O),n.hemi[p]=X,p++}}g>0&&(i.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=xe.LTC_FLOAT_1,n.rectAreaLTC2=xe.LTC_FLOAT_2):(n.rectAreaLTC1=xe.LTC_HALF_1,n.rectAreaLTC2=xe.LTC_HALF_2)),n.ambient[0]=h,n.ambient[1]=u,n.ambient[2]=d;const C=n.hash;(C.directionalLength!==f||C.pointLength!==m||C.spotLength!==_||C.rectAreaLength!==g||C.hemiLength!==p||C.numDirectionalShadows!==y||C.numPointShadows!==M||C.numSpotShadows!==x||C.numSpotMaps!==E||C.numLightProbes!==P)&&(n.directional.length=f,n.spot.length=_,n.rectArea.length=g,n.point.length=m,n.hemi.length=p,n.directionalShadow.length=y,n.directionalShadowMap.length=y,n.pointShadow.length=M,n.pointShadowMap.length=M,n.spotShadow.length=x,n.spotShadowMap.length=x,n.directionalShadowMatrix.length=y,n.pointShadowMatrix.length=M,n.spotLightMatrix.length=x+E-T,n.spotLightMap.length=E,n.numSpotLightShadowsWithMaps=T,n.numLightProbes=P,C.directionalLength=f,C.pointLength=m,C.spotLength=_,C.rectAreaLength=g,C.hemiLength=p,C.numDirectionalShadows=y,C.numPointShadows=M,C.numSpotShadows=x,C.numSpotMaps=E,C.numLightProbes=P,n.version=Bv++)}function c(l,h){let u=0,d=0,f=0,m=0,_=0;const g=h.matrixWorldInverse;for(let p=0,y=l.length;p<y;p++){const M=l[p];if(M.isDirectionalLight){const x=n.directional[u];x.direction.setFromMatrixPosition(M.matrixWorld),s.setFromMatrixPosition(M.target.matrixWorld),x.direction.sub(s),x.direction.transformDirection(g),u++}else if(M.isSpotLight){const x=n.spot[f];x.position.setFromMatrixPosition(M.matrixWorld),x.position.applyMatrix4(g),x.direction.setFromMatrixPosition(M.matrixWorld),s.setFromMatrixPosition(M.target.matrixWorld),x.direction.sub(s),x.direction.transformDirection(g),f++}else if(M.isRectAreaLight){const x=n.rectArea[m];x.position.setFromMatrixPosition(M.matrixWorld),x.position.applyMatrix4(g),o.identity(),r.copy(M.matrixWorld),r.premultiply(g),o.extractRotation(r),x.halfWidth.set(M.width*.5,0,0),x.halfHeight.set(0,M.height*.5,0),x.halfWidth.applyMatrix4(o),x.halfHeight.applyMatrix4(o),m++}else if(M.isPointLight){const x=n.point[d];x.position.setFromMatrixPosition(M.matrixWorld),x.position.applyMatrix4(g),d++}else if(M.isHemisphereLight){const x=n.hemi[_];x.direction.setFromMatrixPosition(M.matrixWorld),x.direction.transformDirection(g),_++}}}return{setup:a,setupView:c,state:n}}function Vu(i){const e=new zv(i),t=[],n=[];function s(h){l.camera=h,t.length=0,n.length=0}function r(h){t.push(h)}function o(h){n.push(h)}function a(){e.setup(t)}function c(h){e.setupView(t,h)}const l={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:s,state:l,setupLights:a,setupLightsView:c,pushLight:r,pushShadow:o}}function Hv(i){let e=new WeakMap;function t(s,r=0){const o=e.get(s);let a;return o===void 0?(a=new Vu(i),e.set(s,[a])):r>=o.length?(a=new Vu(i),o.push(a)):a=o[r],a}function n(){e=new WeakMap}return{get:t,dispose:n}}class Gv extends ri{static get type(){return"MeshDepthMaterial"}constructor(e){super(),this.isMeshDepthMaterial=!0,this.depthPacking=bm,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class Vv extends ri{static get type(){return"MeshDistanceMaterial"}constructor(e){super(),this.isMeshDistanceMaterial=!0,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const Wv=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,Xv=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
#include <packing>
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = unpackRGBATo2Half( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ) );
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = unpackRGBAToDepth( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ) );
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( squared_mean - mean * mean );
	gl_FragColor = pack2HalfToRGBA( vec2( mean, std_dev ) );
}`;function qv(i,e,t){let n=new hh;const s=new te,r=new te,o=new yt,a=new Gv({depthPacking:Sm}),c=new Vv,l={},h=t.maxTextureSize,u={[Ti]:yn,[yn]:Ti,[An]:An},d=new oi({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new te},radius:{value:4}},vertexShader:Wv,fragmentShader:Xv}),f=d.clone();f.defines.HORIZONTAL_PASS=1;const m=new Gt;m.setAttribute("position",new en(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const _=new Xt(m,d),g=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Vd;let p=this.type;this.render=function(T,P,C){if(g.enabled===!1||g.autoUpdate===!1&&g.needsUpdate===!1||T.length===0)return;const b=i.getRenderTarget(),w=i.getActiveCubeFace(),L=i.getActiveMipmapLevel(),F=i.state;F.setBlending(Zi),F.buffers.color.setClear(1,1,1,1),F.buffers.depth.setTest(!0),F.setScissorTest(!1);const O=p!==Mi&&this.type===Mi,k=p===Mi&&this.type!==Mi;for(let K=0,X=T.length;K<X;K++){const j=T[K],V=j.shadow;if(V===void 0){console.warn("THREE.WebGLShadowMap:",j,"has no shadow.");continue}if(V.autoUpdate===!1&&V.needsUpdate===!1)continue;s.copy(V.mapSize);const oe=V.getFrameExtents();if(s.multiply(oe),r.copy(V.mapSize),(s.x>h||s.y>h)&&(s.x>h&&(r.x=Math.floor(h/oe.x),s.x=r.x*oe.x,V.mapSize.x=r.x),s.y>h&&(r.y=Math.floor(h/oe.y),s.y=r.y*oe.y,V.mapSize.y=r.y)),V.map===null||O===!0||k===!0){const Re=this.type!==Mi?{minFilter:pn,magFilter:pn}:{};V.map!==null&&V.map.dispose(),V.map=new Ts(s.x,s.y,Re),V.map.texture.name=j.name+".shadowMap",V.camera.updateProjectionMatrix()}i.setRenderTarget(V.map),i.clear();const _e=V.getViewportCount();for(let Re=0;Re<_e;Re++){const tt=V.getViewport(Re);o.set(r.x*tt.x,r.y*tt.y,r.x*tt.z,r.y*tt.w),F.viewport(o),V.updateMatrices(j,Re),n=V.getFrustum(),x(P,C,V.camera,j,this.type)}V.isPointLightShadow!==!0&&this.type===Mi&&y(V,C),V.needsUpdate=!1}p=this.type,g.needsUpdate=!1,i.setRenderTarget(b,w,L)};function y(T,P){const C=e.update(_);d.defines.VSM_SAMPLES!==T.blurSamples&&(d.defines.VSM_SAMPLES=T.blurSamples,f.defines.VSM_SAMPLES=T.blurSamples,d.needsUpdate=!0,f.needsUpdate=!0),T.mapPass===null&&(T.mapPass=new Ts(s.x,s.y)),d.uniforms.shadow_pass.value=T.map.texture,d.uniforms.resolution.value=T.mapSize,d.uniforms.radius.value=T.radius,i.setRenderTarget(T.mapPass),i.clear(),i.renderBufferDirect(P,null,C,d,_,null),f.uniforms.shadow_pass.value=T.mapPass.texture,f.uniforms.resolution.value=T.mapSize,f.uniforms.radius.value=T.radius,i.setRenderTarget(T.map),i.clear(),i.renderBufferDirect(P,null,C,f,_,null)}function M(T,P,C,b){let w=null;const L=C.isPointLight===!0?T.customDistanceMaterial:T.customDepthMaterial;if(L!==void 0)w=L;else if(w=C.isPointLight===!0?c:a,i.localClippingEnabled&&P.clipShadows===!0&&Array.isArray(P.clippingPlanes)&&P.clippingPlanes.length!==0||P.displacementMap&&P.displacementScale!==0||P.alphaMap&&P.alphaTest>0||P.map&&P.alphaTest>0){const F=w.uuid,O=P.uuid;let k=l[F];k===void 0&&(k={},l[F]=k);let K=k[O];K===void 0&&(K=w.clone(),k[O]=K,P.addEventListener("dispose",E)),w=K}if(w.visible=P.visible,w.wireframe=P.wireframe,b===Mi?w.side=P.shadowSide!==null?P.shadowSide:P.side:w.side=P.shadowSide!==null?P.shadowSide:u[P.side],w.alphaMap=P.alphaMap,w.alphaTest=P.alphaTest,w.map=P.map,w.clipShadows=P.clipShadows,w.clippingPlanes=P.clippingPlanes,w.clipIntersection=P.clipIntersection,w.displacementMap=P.displacementMap,w.displacementScale=P.displacementScale,w.displacementBias=P.displacementBias,w.wireframeLinewidth=P.wireframeLinewidth,w.linewidth=P.linewidth,C.isPointLight===!0&&w.isMeshDistanceMaterial===!0){const F=i.properties.get(w);F.light=C}return w}function x(T,P,C,b,w){if(T.visible===!1)return;if(T.layers.test(P.layers)&&(T.isMesh||T.isLine||T.isPoints)&&(T.castShadow||T.receiveShadow&&w===Mi)&&(!T.frustumCulled||n.intersectsObject(T))){T.modelViewMatrix.multiplyMatrices(C.matrixWorldInverse,T.matrixWorld);const O=e.update(T),k=T.material;if(Array.isArray(k)){const K=O.groups;for(let X=0,j=K.length;X<j;X++){const V=K[X],oe=k[V.materialIndex];if(oe&&oe.visible){const _e=M(T,oe,b,w);T.onBeforeShadow(i,T,P,C,O,_e,V),i.renderBufferDirect(C,null,O,_e,T,V),T.onAfterShadow(i,T,P,C,O,_e,V)}}}else if(k.visible){const K=M(T,k,b,w);T.onBeforeShadow(i,T,P,C,O,K,null),i.renderBufferDirect(C,null,O,K,T,null),T.onAfterShadow(i,T,P,C,O,K,null)}}const F=T.children;for(let O=0,k=F.length;O<k;O++)x(F[O],P,C,b,w)}function E(T){T.target.removeEventListener("dispose",E);for(const C in l){const b=l[C],w=T.target.uuid;w in b&&(b[w].dispose(),delete b[w])}}}const jv={[il]:sl,[rl]:cl,[ol]:ll,[cr]:al,[sl]:il,[cl]:rl,[ll]:ol,[al]:cr};function $v(i,e){function t(){let D=!1;const Me=new yt;let q=null;const J=new yt(0,0,0,0);return{setMask:function(Se){q!==Se&&!D&&(i.colorMask(Se,Se,Se,Se),q=Se)},setLocked:function(Se){D=Se},setClear:function(Se,we,it,Wt,on){on===!0&&(Se*=Wt,we*=Wt,it*=Wt),Me.set(Se,we,it,Wt),J.equals(Me)===!1&&(i.clearColor(Se,we,it,Wt),J.copy(Me))},reset:function(){D=!1,q=null,J.set(-1,0,0,0)}}}function n(){let D=!1,Me=!1,q=null,J=null,Se=null;return{setReversed:function(we){if(Me!==we){const it=e.get("EXT_clip_control");Me?it.clipControlEXT(it.LOWER_LEFT_EXT,it.ZERO_TO_ONE_EXT):it.clipControlEXT(it.LOWER_LEFT_EXT,it.NEGATIVE_ONE_TO_ONE_EXT);const Wt=Se;Se=null,this.setClear(Wt)}Me=we},getReversed:function(){return Me},setTest:function(we){we?pe(i.DEPTH_TEST):We(i.DEPTH_TEST)},setMask:function(we){q!==we&&!D&&(i.depthMask(we),q=we)},setFunc:function(we){if(Me&&(we=jv[we]),J!==we){switch(we){case il:i.depthFunc(i.NEVER);break;case sl:i.depthFunc(i.ALWAYS);break;case rl:i.depthFunc(i.LESS);break;case cr:i.depthFunc(i.LEQUAL);break;case ol:i.depthFunc(i.EQUAL);break;case al:i.depthFunc(i.GEQUAL);break;case cl:i.depthFunc(i.GREATER);break;case ll:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}J=we}},setLocked:function(we){D=we},setClear:function(we){Se!==we&&(Me&&(we=1-we),i.clearDepth(we),Se=we)},reset:function(){D=!1,q=null,J=null,Se=null,Me=!1}}}function s(){let D=!1,Me=null,q=null,J=null,Se=null,we=null,it=null,Wt=null,on=null;return{setTest:function(Et){D||(Et?pe(i.STENCIL_TEST):We(i.STENCIL_TEST))},setMask:function(Et){Me!==Et&&!D&&(i.stencilMask(Et),Me=Et)},setFunc:function(Et,Xn,di){(q!==Et||J!==Xn||Se!==di)&&(i.stencilFunc(Et,Xn,di),q=Et,J=Xn,Se=di)},setOp:function(Et,Xn,di){(we!==Et||it!==Xn||Wt!==di)&&(i.stencilOp(Et,Xn,di),we=Et,it=Xn,Wt=di)},setLocked:function(Et){D=Et},setClear:function(Et){on!==Et&&(i.clearStencil(Et),on=Et)},reset:function(){D=!1,Me=null,q=null,J=null,Se=null,we=null,it=null,Wt=null,on=null}}}const r=new t,o=new n,a=new s,c=new WeakMap,l=new WeakMap;let h={},u={},d=new WeakMap,f=[],m=null,_=!1,g=null,p=null,y=null,M=null,x=null,E=null,T=null,P=new Ve(0,0,0),C=0,b=!1,w=null,L=null,F=null,O=null,k=null;const K=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let X=!1,j=0;const V=i.getParameter(i.VERSION);V.indexOf("WebGL")!==-1?(j=parseFloat(/^WebGL (\d)/.exec(V)[1]),X=j>=1):V.indexOf("OpenGL ES")!==-1&&(j=parseFloat(/^OpenGL ES (\d)/.exec(V)[1]),X=j>=2);let oe=null,_e={};const Re=i.getParameter(i.SCISSOR_BOX),tt=i.getParameter(i.VIEWPORT),wt=new yt().fromArray(Re),Z=new yt().fromArray(tt);function he(D,Me,q,J){const Se=new Uint8Array(4),we=i.createTexture();i.bindTexture(D,we),i.texParameteri(D,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(D,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let it=0;it<q;it++)D===i.TEXTURE_3D||D===i.TEXTURE_2D_ARRAY?i.texImage3D(Me,0,i.RGBA,1,1,J,0,i.RGBA,i.UNSIGNED_BYTE,Se):i.texImage2D(Me+it,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,Se);return we}const Ne={};Ne[i.TEXTURE_2D]=he(i.TEXTURE_2D,i.TEXTURE_2D,1),Ne[i.TEXTURE_CUBE_MAP]=he(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),Ne[i.TEXTURE_2D_ARRAY]=he(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),Ne[i.TEXTURE_3D]=he(i.TEXTURE_3D,i.TEXTURE_3D,1,1),r.setClear(0,0,0,1),o.setClear(1),a.setClear(0),pe(i.DEPTH_TEST),o.setFunc(cr),re(!1),Le(Vh),pe(i.CULL_FACE),I(Zi);function pe(D){h[D]!==!0&&(i.enable(D),h[D]=!0)}function We(D){h[D]!==!1&&(i.disable(D),h[D]=!1)}function Ze(D,Me){return u[D]!==Me?(i.bindFramebuffer(D,Me),u[D]=Me,D===i.DRAW_FRAMEBUFFER&&(u[i.FRAMEBUFFER]=Me),D===i.FRAMEBUFFER&&(u[i.DRAW_FRAMEBUFFER]=Me),!0):!1}function je(D,Me){let q=f,J=!1;if(D){q=d.get(Me),q===void 0&&(q=[],d.set(Me,q));const Se=D.textures;if(q.length!==Se.length||q[0]!==i.COLOR_ATTACHMENT0){for(let we=0,it=Se.length;we<it;we++)q[we]=i.COLOR_ATTACHMENT0+we;q.length=Se.length,J=!0}}else q[0]!==i.BACK&&(q[0]=i.BACK,J=!0);J&&i.drawBuffers(q)}function gt(D){return m!==D?(i.useProgram(D),m=D,!0):!1}const Q={[vs]:i.FUNC_ADD,[$p]:i.FUNC_SUBTRACT,[Yp]:i.FUNC_REVERSE_SUBTRACT};Q[Kp]=i.MIN,Q[Zp]=i.MAX;const le={[Jp]:i.ZERO,[Qp]:i.ONE,[em]:i.SRC_COLOR,[tl]:i.SRC_ALPHA,[om]:i.SRC_ALPHA_SATURATE,[sm]:i.DST_COLOR,[nm]:i.DST_ALPHA,[tm]:i.ONE_MINUS_SRC_COLOR,[nl]:i.ONE_MINUS_SRC_ALPHA,[rm]:i.ONE_MINUS_DST_COLOR,[im]:i.ONE_MINUS_DST_ALPHA,[am]:i.CONSTANT_COLOR,[cm]:i.ONE_MINUS_CONSTANT_COLOR,[lm]:i.CONSTANT_ALPHA,[hm]:i.ONE_MINUS_CONSTANT_ALPHA};function I(D,Me,q,J,Se,we,it,Wt,on,Et){if(D===Zi){_===!0&&(We(i.BLEND),_=!1);return}if(_===!1&&(pe(i.BLEND),_=!0),D!==jp){if(D!==g||Et!==b){if((p!==vs||x!==vs)&&(i.blendEquation(i.FUNC_ADD),p=vs,x=vs),Et)switch(D){case nr:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Wh:i.blendFunc(i.ONE,i.ONE);break;case Xh:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case qh:i.blendFuncSeparate(i.ZERO,i.SRC_COLOR,i.ZERO,i.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",D);break}else switch(D){case nr:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Wh:i.blendFunc(i.SRC_ALPHA,i.ONE);break;case Xh:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case qh:i.blendFunc(i.ZERO,i.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",D);break}y=null,M=null,E=null,T=null,P.set(0,0,0),C=0,g=D,b=Et}return}Se=Se||Me,we=we||q,it=it||J,(Me!==p||Se!==x)&&(i.blendEquationSeparate(Q[Me],Q[Se]),p=Me,x=Se),(q!==y||J!==M||we!==E||it!==T)&&(i.blendFuncSeparate(le[q],le[J],le[we],le[it]),y=q,M=J,E=we,T=it),(Wt.equals(P)===!1||on!==C)&&(i.blendColor(Wt.r,Wt.g,Wt.b,on),P.copy(Wt),C=on),g=D,b=!1}function ze(D,Me){D.side===An?We(i.CULL_FACE):pe(i.CULL_FACE);let q=D.side===yn;Me&&(q=!q),re(q),D.blending===nr&&D.transparent===!1?I(Zi):I(D.blending,D.blendEquation,D.blendSrc,D.blendDst,D.blendEquationAlpha,D.blendSrcAlpha,D.blendDstAlpha,D.blendColor,D.blendAlpha,D.premultipliedAlpha),o.setFunc(D.depthFunc),o.setTest(D.depthTest),o.setMask(D.depthWrite),r.setMask(D.colorWrite);const J=D.stencilWrite;a.setTest(J),J&&(a.setMask(D.stencilWriteMask),a.setFunc(D.stencilFunc,D.stencilRef,D.stencilFuncMask),a.setOp(D.stencilFail,D.stencilZFail,D.stencilZPass)),Xe(D.polygonOffset,D.polygonOffsetFactor,D.polygonOffsetUnits),D.alphaToCoverage===!0?pe(i.SAMPLE_ALPHA_TO_COVERAGE):We(i.SAMPLE_ALPHA_TO_COVERAGE)}function re(D){w!==D&&(D?i.frontFace(i.CW):i.frontFace(i.CCW),w=D)}function Le(D){D!==Wp?(pe(i.CULL_FACE),D!==L&&(D===Vh?i.cullFace(i.BACK):D===Xp?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):We(i.CULL_FACE),L=D}function ge(D){D!==F&&(X&&i.lineWidth(D),F=D)}function Xe(D,Me,q){D?(pe(i.POLYGON_OFFSET_FILL),(O!==Me||k!==q)&&(i.polygonOffset(Me,q),O=Me,k=q)):We(i.POLYGON_OFFSET_FILL)}function Ce(D){D?pe(i.SCISSOR_TEST):We(i.SCISSOR_TEST)}function R(D){D===void 0&&(D=i.TEXTURE0+K-1),oe!==D&&(i.activeTexture(D),oe=D)}function S(D,Me,q){q===void 0&&(oe===null?q=i.TEXTURE0+K-1:q=oe);let J=_e[q];J===void 0&&(J={type:void 0,texture:void 0},_e[q]=J),(J.type!==D||J.texture!==Me)&&(oe!==q&&(i.activeTexture(q),oe=q),i.bindTexture(D,Me||Ne[D]),J.type=D,J.texture=Me)}function B(){const D=_e[oe];D!==void 0&&D.type!==void 0&&(i.bindTexture(D.type,null),D.type=void 0,D.texture=void 0)}function $(){try{i.compressedTexImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function ee(){try{i.compressedTexImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Y(){try{i.texSubImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Oe(){try{i.texSubImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function ye(){try{i.compressedTexSubImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Pe(){try{i.compressedTexSubImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function dt(){try{i.texStorage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function ae(){try{i.texStorage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Ie(){try{i.texImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function qe(){try{i.texImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Ye(D){wt.equals(D)===!1&&(i.scissor(D.x,D.y,D.z,D.w),wt.copy(D))}function De(D){Z.equals(D)===!1&&(i.viewport(D.x,D.y,D.z,D.w),Z.copy(D))}function pt(D,Me){let q=l.get(Me);q===void 0&&(q=new WeakMap,l.set(Me,q));let J=q.get(D);J===void 0&&(J=i.getUniformBlockIndex(Me,D.name),q.set(D,J))}function ot(D,Me){const J=l.get(Me).get(D);c.get(Me)!==J&&(i.uniformBlockBinding(Me,J,D.__bindingPointIndex),c.set(Me,J))}function Lt(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),o.setReversed(!1),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),h={},oe=null,_e={},u={},d=new WeakMap,f=[],m=null,_=!1,g=null,p=null,y=null,M=null,x=null,E=null,T=null,P=new Ve(0,0,0),C=0,b=!1,w=null,L=null,F=null,O=null,k=null,wt.set(0,0,i.canvas.width,i.canvas.height),Z.set(0,0,i.canvas.width,i.canvas.height),r.reset(),o.reset(),a.reset()}return{buffers:{color:r,depth:o,stencil:a},enable:pe,disable:We,bindFramebuffer:Ze,drawBuffers:je,useProgram:gt,setBlending:I,setMaterial:ze,setFlipSided:re,setCullFace:Le,setLineWidth:ge,setPolygonOffset:Xe,setScissorTest:Ce,activeTexture:R,bindTexture:S,unbindTexture:B,compressedTexImage2D:$,compressedTexImage3D:ee,texImage2D:Ie,texImage3D:qe,updateUBOMapping:pt,uniformBlockBinding:ot,texStorage2D:dt,texStorage3D:ae,texSubImage2D:Y,texSubImage3D:Oe,compressedTexSubImage2D:ye,compressedTexSubImage3D:Pe,scissor:Ye,viewport:De,reset:Lt}}function Wu(i,e,t,n){const s=Yv(n);switch(t){case Kd:return i*e;case Jd:return i*e;case Qd:return i*e*2;case sh:return i*e/s.components*s.byteLength;case rh:return i*e/s.components*s.byteLength;case ef:return i*e*2/s.components*s.byteLength;case oh:return i*e*2/s.components*s.byteLength;case Zd:return i*e*3/s.components*s.byteLength;case kn:return i*e*4/s.components*s.byteLength;case ah:return i*e*4/s.components*s.byteLength;case ua:case da:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case fa:case pa:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case fl:case ml:return Math.max(i,16)*Math.max(e,8)/4;case dl:case pl:return Math.max(i,8)*Math.max(e,8)/2;case gl:case _l:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case xl:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case vl:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case yl:return Math.floor((i+4)/5)*Math.floor((e+3)/4)*16;case Ml:return Math.floor((i+4)/5)*Math.floor((e+4)/5)*16;case wl:return Math.floor((i+5)/6)*Math.floor((e+4)/5)*16;case bl:return Math.floor((i+5)/6)*Math.floor((e+5)/6)*16;case Sl:return Math.floor((i+7)/8)*Math.floor((e+4)/5)*16;case El:return Math.floor((i+7)/8)*Math.floor((e+5)/6)*16;case Tl:return Math.floor((i+7)/8)*Math.floor((e+7)/8)*16;case Al:return Math.floor((i+9)/10)*Math.floor((e+4)/5)*16;case Rl:return Math.floor((i+9)/10)*Math.floor((e+5)/6)*16;case Cl:return Math.floor((i+9)/10)*Math.floor((e+7)/8)*16;case Pl:return Math.floor((i+9)/10)*Math.floor((e+9)/10)*16;case Ll:return Math.floor((i+11)/12)*Math.floor((e+9)/10)*16;case Il:return Math.floor((i+11)/12)*Math.floor((e+11)/12)*16;case ma:case Dl:case Nl:return Math.ceil(i/4)*Math.ceil(e/4)*16;case tf:case Ul:return Math.ceil(i/4)*Math.ceil(e/4)*8;case Ol:case Fl:return Math.ceil(i/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function Yv(i){switch(i){case Ai:case jd:return{byteLength:1,components:1};case io:case $d:case uo:return{byteLength:2,components:1};case nh:case ih:return{byteLength:2,components:4};case Es:case th:case Jn:return{byteLength:4,components:1};case Yd:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}function Kv(i,e,t,n,s,r,o){const a=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,c=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),l=new te,h=new WeakMap;let u;const d=new WeakMap;let f=!1;try{f=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function m(R,S){return f?new OffscreenCanvas(R,S):oo("canvas")}function _(R,S,B){let $=1;const ee=Ce(R);if((ee.width>B||ee.height>B)&&($=B/Math.max(ee.width,ee.height)),$<1)if(typeof HTMLImageElement<"u"&&R instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&R instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&R instanceof ImageBitmap||typeof VideoFrame<"u"&&R instanceof VideoFrame){const Y=Math.floor($*ee.width),Oe=Math.floor($*ee.height);u===void 0&&(u=m(Y,Oe));const ye=S?m(Y,Oe):u;return ye.width=Y,ye.height=Oe,ye.getContext("2d").drawImage(R,0,0,Y,Oe),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+ee.width+"x"+ee.height+") to ("+Y+"x"+Oe+")."),ye}else return"data"in R&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+ee.width+"x"+ee.height+")."),R;return R}function g(R){return R.generateMipmaps}function p(R){i.generateMipmap(R)}function y(R){return R.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:R.isWebGL3DRenderTarget?i.TEXTURE_3D:R.isWebGLArrayRenderTarget||R.isCompressedArrayTexture?i.TEXTURE_2D_ARRAY:i.TEXTURE_2D}function M(R,S,B,$,ee=!1){if(R!==null){if(i[R]!==void 0)return i[R];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+R+"'")}let Y=S;if(S===i.RED&&(B===i.FLOAT&&(Y=i.R32F),B===i.HALF_FLOAT&&(Y=i.R16F),B===i.UNSIGNED_BYTE&&(Y=i.R8)),S===i.RED_INTEGER&&(B===i.UNSIGNED_BYTE&&(Y=i.R8UI),B===i.UNSIGNED_SHORT&&(Y=i.R16UI),B===i.UNSIGNED_INT&&(Y=i.R32UI),B===i.BYTE&&(Y=i.R8I),B===i.SHORT&&(Y=i.R16I),B===i.INT&&(Y=i.R32I)),S===i.RG&&(B===i.FLOAT&&(Y=i.RG32F),B===i.HALF_FLOAT&&(Y=i.RG16F),B===i.UNSIGNED_BYTE&&(Y=i.RG8)),S===i.RG_INTEGER&&(B===i.UNSIGNED_BYTE&&(Y=i.RG8UI),B===i.UNSIGNED_SHORT&&(Y=i.RG16UI),B===i.UNSIGNED_INT&&(Y=i.RG32UI),B===i.BYTE&&(Y=i.RG8I),B===i.SHORT&&(Y=i.RG16I),B===i.INT&&(Y=i.RG32I)),S===i.RGB_INTEGER&&(B===i.UNSIGNED_BYTE&&(Y=i.RGB8UI),B===i.UNSIGNED_SHORT&&(Y=i.RGB16UI),B===i.UNSIGNED_INT&&(Y=i.RGB32UI),B===i.BYTE&&(Y=i.RGB8I),B===i.SHORT&&(Y=i.RGB16I),B===i.INT&&(Y=i.RGB32I)),S===i.RGBA_INTEGER&&(B===i.UNSIGNED_BYTE&&(Y=i.RGBA8UI),B===i.UNSIGNED_SHORT&&(Y=i.RGBA16UI),B===i.UNSIGNED_INT&&(Y=i.RGBA32UI),B===i.BYTE&&(Y=i.RGBA8I),B===i.SHORT&&(Y=i.RGBA16I),B===i.INT&&(Y=i.RGBA32I)),S===i.RGB&&B===i.UNSIGNED_INT_5_9_9_9_REV&&(Y=i.RGB9_E5),S===i.RGBA){const Oe=ee?Na:ft.getTransfer($);B===i.FLOAT&&(Y=i.RGBA32F),B===i.HALF_FLOAT&&(Y=i.RGBA16F),B===i.UNSIGNED_BYTE&&(Y=Oe===Rt?i.SRGB8_ALPHA8:i.RGBA8),B===i.UNSIGNED_SHORT_4_4_4_4&&(Y=i.RGBA4),B===i.UNSIGNED_SHORT_5_5_5_1&&(Y=i.RGB5_A1)}return(Y===i.R16F||Y===i.R32F||Y===i.RG16F||Y===i.RG32F||Y===i.RGBA16F||Y===i.RGBA32F)&&e.get("EXT_color_buffer_float"),Y}function x(R,S){let B;return R?S===null||S===Es||S===dr?B=i.DEPTH24_STENCIL8:S===Jn?B=i.DEPTH32F_STENCIL8:S===io&&(B=i.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):S===null||S===Es||S===dr?B=i.DEPTH_COMPONENT24:S===Jn?B=i.DEPTH_COMPONENT32F:S===io&&(B=i.DEPTH_COMPONENT16),B}function E(R,S){return g(R)===!0||R.isFramebufferTexture&&R.minFilter!==pn&&R.minFilter!==Dn?Math.log2(Math.max(S.width,S.height))+1:R.mipmaps!==void 0&&R.mipmaps.length>0?R.mipmaps.length:R.isCompressedTexture&&Array.isArray(R.image)?S.mipmaps.length:1}function T(R){const S=R.target;S.removeEventListener("dispose",T),C(S),S.isVideoTexture&&h.delete(S)}function P(R){const S=R.target;S.removeEventListener("dispose",P),w(S)}function C(R){const S=n.get(R);if(S.__webglInit===void 0)return;const B=R.source,$=d.get(B);if($){const ee=$[S.__cacheKey];ee.usedTimes--,ee.usedTimes===0&&b(R),Object.keys($).length===0&&d.delete(B)}n.remove(R)}function b(R){const S=n.get(R);i.deleteTexture(S.__webglTexture);const B=R.source,$=d.get(B);delete $[S.__cacheKey],o.memory.textures--}function w(R){const S=n.get(R);if(R.depthTexture&&(R.depthTexture.dispose(),n.remove(R.depthTexture)),R.isWebGLCubeRenderTarget)for(let $=0;$<6;$++){if(Array.isArray(S.__webglFramebuffer[$]))for(let ee=0;ee<S.__webglFramebuffer[$].length;ee++)i.deleteFramebuffer(S.__webglFramebuffer[$][ee]);else i.deleteFramebuffer(S.__webglFramebuffer[$]);S.__webglDepthbuffer&&i.deleteRenderbuffer(S.__webglDepthbuffer[$])}else{if(Array.isArray(S.__webglFramebuffer))for(let $=0;$<S.__webglFramebuffer.length;$++)i.deleteFramebuffer(S.__webglFramebuffer[$]);else i.deleteFramebuffer(S.__webglFramebuffer);if(S.__webglDepthbuffer&&i.deleteRenderbuffer(S.__webglDepthbuffer),S.__webglMultisampledFramebuffer&&i.deleteFramebuffer(S.__webglMultisampledFramebuffer),S.__webglColorRenderbuffer)for(let $=0;$<S.__webglColorRenderbuffer.length;$++)S.__webglColorRenderbuffer[$]&&i.deleteRenderbuffer(S.__webglColorRenderbuffer[$]);S.__webglDepthRenderbuffer&&i.deleteRenderbuffer(S.__webglDepthRenderbuffer)}const B=R.textures;for(let $=0,ee=B.length;$<ee;$++){const Y=n.get(B[$]);Y.__webglTexture&&(i.deleteTexture(Y.__webglTexture),o.memory.textures--),n.remove(B[$])}n.remove(R)}let L=0;function F(){L=0}function O(){const R=L;return R>=s.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+R+" texture units while this GPU supports only "+s.maxTextures),L+=1,R}function k(R){const S=[];return S.push(R.wrapS),S.push(R.wrapT),S.push(R.wrapR||0),S.push(R.magFilter),S.push(R.minFilter),S.push(R.anisotropy),S.push(R.internalFormat),S.push(R.format),S.push(R.type),S.push(R.generateMipmaps),S.push(R.premultiplyAlpha),S.push(R.flipY),S.push(R.unpackAlignment),S.push(R.colorSpace),S.join()}function K(R,S){const B=n.get(R);if(R.isVideoTexture&&ge(R),R.isRenderTargetTexture===!1&&R.version>0&&B.__version!==R.version){const $=R.image;if($===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if($.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{Z(B,R,S);return}}t.bindTexture(i.TEXTURE_2D,B.__webglTexture,i.TEXTURE0+S)}function X(R,S){const B=n.get(R);if(R.version>0&&B.__version!==R.version){Z(B,R,S);return}t.bindTexture(i.TEXTURE_2D_ARRAY,B.__webglTexture,i.TEXTURE0+S)}function j(R,S){const B=n.get(R);if(R.version>0&&B.__version!==R.version){Z(B,R,S);return}t.bindTexture(i.TEXTURE_3D,B.__webglTexture,i.TEXTURE0+S)}function V(R,S){const B=n.get(R);if(R.version>0&&B.__version!==R.version){he(B,R,S);return}t.bindTexture(i.TEXTURE_CUBE_MAP,B.__webglTexture,i.TEXTURE0+S)}const oe={[ur]:i.REPEAT,[qi]:i.CLAMP_TO_EDGE,[Ma]:i.MIRRORED_REPEAT},_e={[pn]:i.NEAREST,[qd]:i.NEAREST_MIPMAP_NEAREST,[$r]:i.NEAREST_MIPMAP_LINEAR,[Dn]:i.LINEAR,[ha]:i.LINEAR_MIPMAP_NEAREST,[bi]:i.LINEAR_MIPMAP_LINEAR},Re={[Tm]:i.NEVER,[Im]:i.ALWAYS,[Am]:i.LESS,[rf]:i.LEQUAL,[Rm]:i.EQUAL,[Lm]:i.GEQUAL,[Cm]:i.GREATER,[Pm]:i.NOTEQUAL};function tt(R,S){if(S.type===Jn&&e.has("OES_texture_float_linear")===!1&&(S.magFilter===Dn||S.magFilter===ha||S.magFilter===$r||S.magFilter===bi||S.minFilter===Dn||S.minFilter===ha||S.minFilter===$r||S.minFilter===bi)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(R,i.TEXTURE_WRAP_S,oe[S.wrapS]),i.texParameteri(R,i.TEXTURE_WRAP_T,oe[S.wrapT]),(R===i.TEXTURE_3D||R===i.TEXTURE_2D_ARRAY)&&i.texParameteri(R,i.TEXTURE_WRAP_R,oe[S.wrapR]),i.texParameteri(R,i.TEXTURE_MAG_FILTER,_e[S.magFilter]),i.texParameteri(R,i.TEXTURE_MIN_FILTER,_e[S.minFilter]),S.compareFunction&&(i.texParameteri(R,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(R,i.TEXTURE_COMPARE_FUNC,Re[S.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(S.magFilter===pn||S.minFilter!==$r&&S.minFilter!==bi||S.type===Jn&&e.has("OES_texture_float_linear")===!1)return;if(S.anisotropy>1||n.get(S).__currentAnisotropy){const B=e.get("EXT_texture_filter_anisotropic");i.texParameterf(R,B.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(S.anisotropy,s.getMaxAnisotropy())),n.get(S).__currentAnisotropy=S.anisotropy}}}function wt(R,S){let B=!1;R.__webglInit===void 0&&(R.__webglInit=!0,S.addEventListener("dispose",T));const $=S.source;let ee=d.get($);ee===void 0&&(ee={},d.set($,ee));const Y=k(S);if(Y!==R.__cacheKey){ee[Y]===void 0&&(ee[Y]={texture:i.createTexture(),usedTimes:0},o.memory.textures++,B=!0),ee[Y].usedTimes++;const Oe=ee[R.__cacheKey];Oe!==void 0&&(ee[R.__cacheKey].usedTimes--,Oe.usedTimes===0&&b(S)),R.__cacheKey=Y,R.__webglTexture=ee[Y].texture}return B}function Z(R,S,B){let $=i.TEXTURE_2D;(S.isDataArrayTexture||S.isCompressedArrayTexture)&&($=i.TEXTURE_2D_ARRAY),S.isData3DTexture&&($=i.TEXTURE_3D);const ee=wt(R,S),Y=S.source;t.bindTexture($,R.__webglTexture,i.TEXTURE0+B);const Oe=n.get(Y);if(Y.version!==Oe.__version||ee===!0){t.activeTexture(i.TEXTURE0+B);const ye=ft.getPrimaries(ft.workingColorSpace),Pe=S.colorSpace===Wi?null:ft.getPrimaries(S.colorSpace),dt=S.colorSpace===Wi||ye===Pe?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,S.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,S.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,S.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,dt);let ae=_(S.image,!1,s.maxTextureSize);ae=Xe(S,ae);const Ie=r.convert(S.format,S.colorSpace),qe=r.convert(S.type);let Ye=M(S.internalFormat,Ie,qe,S.colorSpace,S.isVideoTexture);tt($,S);let De;const pt=S.mipmaps,ot=S.isVideoTexture!==!0,Lt=Oe.__version===void 0||ee===!0,D=Y.dataReady,Me=E(S,ae);if(S.isDepthTexture)Ye=x(S.format===fr,S.type),Lt&&(ot?t.texStorage2D(i.TEXTURE_2D,1,Ye,ae.width,ae.height):t.texImage2D(i.TEXTURE_2D,0,Ye,ae.width,ae.height,0,Ie,qe,null));else if(S.isDataTexture)if(pt.length>0){ot&&Lt&&t.texStorage2D(i.TEXTURE_2D,Me,Ye,pt[0].width,pt[0].height);for(let q=0,J=pt.length;q<J;q++)De=pt[q],ot?D&&t.texSubImage2D(i.TEXTURE_2D,q,0,0,De.width,De.height,Ie,qe,De.data):t.texImage2D(i.TEXTURE_2D,q,Ye,De.width,De.height,0,Ie,qe,De.data);S.generateMipmaps=!1}else ot?(Lt&&t.texStorage2D(i.TEXTURE_2D,Me,Ye,ae.width,ae.height),D&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,ae.width,ae.height,Ie,qe,ae.data)):t.texImage2D(i.TEXTURE_2D,0,Ye,ae.width,ae.height,0,Ie,qe,ae.data);else if(S.isCompressedTexture)if(S.isCompressedArrayTexture){ot&&Lt&&t.texStorage3D(i.TEXTURE_2D_ARRAY,Me,Ye,pt[0].width,pt[0].height,ae.depth);for(let q=0,J=pt.length;q<J;q++)if(De=pt[q],S.format!==kn)if(Ie!==null)if(ot){if(D)if(S.layerUpdates.size>0){const Se=Wu(De.width,De.height,S.format,S.type);for(const we of S.layerUpdates){const it=De.data.subarray(we*Se/De.data.BYTES_PER_ELEMENT,(we+1)*Se/De.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,q,0,0,we,De.width,De.height,1,Ie,it)}S.clearLayerUpdates()}else t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,q,0,0,0,De.width,De.height,ae.depth,Ie,De.data)}else t.compressedTexImage3D(i.TEXTURE_2D_ARRAY,q,Ye,De.width,De.height,ae.depth,0,De.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else ot?D&&t.texSubImage3D(i.TEXTURE_2D_ARRAY,q,0,0,0,De.width,De.height,ae.depth,Ie,qe,De.data):t.texImage3D(i.TEXTURE_2D_ARRAY,q,Ye,De.width,De.height,ae.depth,0,Ie,qe,De.data)}else{ot&&Lt&&t.texStorage2D(i.TEXTURE_2D,Me,Ye,pt[0].width,pt[0].height);for(let q=0,J=pt.length;q<J;q++)De=pt[q],S.format!==kn?Ie!==null?ot?D&&t.compressedTexSubImage2D(i.TEXTURE_2D,q,0,0,De.width,De.height,Ie,De.data):t.compressedTexImage2D(i.TEXTURE_2D,q,Ye,De.width,De.height,0,De.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):ot?D&&t.texSubImage2D(i.TEXTURE_2D,q,0,0,De.width,De.height,Ie,qe,De.data):t.texImage2D(i.TEXTURE_2D,q,Ye,De.width,De.height,0,Ie,qe,De.data)}else if(S.isDataArrayTexture)if(ot){if(Lt&&t.texStorage3D(i.TEXTURE_2D_ARRAY,Me,Ye,ae.width,ae.height,ae.depth),D)if(S.layerUpdates.size>0){const q=Wu(ae.width,ae.height,S.format,S.type);for(const J of S.layerUpdates){const Se=ae.data.subarray(J*q/ae.data.BYTES_PER_ELEMENT,(J+1)*q/ae.data.BYTES_PER_ELEMENT);t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,J,ae.width,ae.height,1,Ie,qe,Se)}S.clearLayerUpdates()}else t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,ae.width,ae.height,ae.depth,Ie,qe,ae.data)}else t.texImage3D(i.TEXTURE_2D_ARRAY,0,Ye,ae.width,ae.height,ae.depth,0,Ie,qe,ae.data);else if(S.isData3DTexture)ot?(Lt&&t.texStorage3D(i.TEXTURE_3D,Me,Ye,ae.width,ae.height,ae.depth),D&&t.texSubImage3D(i.TEXTURE_3D,0,0,0,0,ae.width,ae.height,ae.depth,Ie,qe,ae.data)):t.texImage3D(i.TEXTURE_3D,0,Ye,ae.width,ae.height,ae.depth,0,Ie,qe,ae.data);else if(S.isFramebufferTexture){if(Lt)if(ot)t.texStorage2D(i.TEXTURE_2D,Me,Ye,ae.width,ae.height);else{let q=ae.width,J=ae.height;for(let Se=0;Se<Me;Se++)t.texImage2D(i.TEXTURE_2D,Se,Ye,q,J,0,Ie,qe,null),q>>=1,J>>=1}}else if(pt.length>0){if(ot&&Lt){const q=Ce(pt[0]);t.texStorage2D(i.TEXTURE_2D,Me,Ye,q.width,q.height)}for(let q=0,J=pt.length;q<J;q++)De=pt[q],ot?D&&t.texSubImage2D(i.TEXTURE_2D,q,0,0,Ie,qe,De):t.texImage2D(i.TEXTURE_2D,q,Ye,Ie,qe,De);S.generateMipmaps=!1}else if(ot){if(Lt){const q=Ce(ae);t.texStorage2D(i.TEXTURE_2D,Me,Ye,q.width,q.height)}D&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,Ie,qe,ae)}else t.texImage2D(i.TEXTURE_2D,0,Ye,Ie,qe,ae);g(S)&&p($),Oe.__version=Y.version,S.onUpdate&&S.onUpdate(S)}R.__version=S.version}function he(R,S,B){if(S.image.length!==6)return;const $=wt(R,S),ee=S.source;t.bindTexture(i.TEXTURE_CUBE_MAP,R.__webglTexture,i.TEXTURE0+B);const Y=n.get(ee);if(ee.version!==Y.__version||$===!0){t.activeTexture(i.TEXTURE0+B);const Oe=ft.getPrimaries(ft.workingColorSpace),ye=S.colorSpace===Wi?null:ft.getPrimaries(S.colorSpace),Pe=S.colorSpace===Wi||Oe===ye?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,S.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,S.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,S.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Pe);const dt=S.isCompressedTexture||S.image[0].isCompressedTexture,ae=S.image[0]&&S.image[0].isDataTexture,Ie=[];for(let J=0;J<6;J++)!dt&&!ae?Ie[J]=_(S.image[J],!0,s.maxCubemapSize):Ie[J]=ae?S.image[J].image:S.image[J],Ie[J]=Xe(S,Ie[J]);const qe=Ie[0],Ye=r.convert(S.format,S.colorSpace),De=r.convert(S.type),pt=M(S.internalFormat,Ye,De,S.colorSpace),ot=S.isVideoTexture!==!0,Lt=Y.__version===void 0||$===!0,D=ee.dataReady;let Me=E(S,qe);tt(i.TEXTURE_CUBE_MAP,S);let q;if(dt){ot&&Lt&&t.texStorage2D(i.TEXTURE_CUBE_MAP,Me,pt,qe.width,qe.height);for(let J=0;J<6;J++){q=Ie[J].mipmaps;for(let Se=0;Se<q.length;Se++){const we=q[Se];S.format!==kn?Ye!==null?ot?D&&t.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Se,0,0,we.width,we.height,Ye,we.data):t.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Se,pt,we.width,we.height,0,we.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):ot?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Se,0,0,we.width,we.height,Ye,De,we.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Se,pt,we.width,we.height,0,Ye,De,we.data)}}}else{if(q=S.mipmaps,ot&&Lt){q.length>0&&Me++;const J=Ce(Ie[0]);t.texStorage2D(i.TEXTURE_CUBE_MAP,Me,pt,J.width,J.height)}for(let J=0;J<6;J++)if(ae){ot?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,0,0,Ie[J].width,Ie[J].height,Ye,De,Ie[J].data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,pt,Ie[J].width,Ie[J].height,0,Ye,De,Ie[J].data);for(let Se=0;Se<q.length;Se++){const it=q[Se].image[J].image;ot?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Se+1,0,0,it.width,it.height,Ye,De,it.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Se+1,pt,it.width,it.height,0,Ye,De,it.data)}}else{ot?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,0,0,Ye,De,Ie[J]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,pt,Ye,De,Ie[J]);for(let Se=0;Se<q.length;Se++){const we=q[Se];ot?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Se+1,0,0,Ye,De,we.image[J]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Se+1,pt,Ye,De,we.image[J])}}}g(S)&&p(i.TEXTURE_CUBE_MAP),Y.__version=ee.version,S.onUpdate&&S.onUpdate(S)}R.__version=S.version}function Ne(R,S,B,$,ee,Y){const Oe=r.convert(B.format,B.colorSpace),ye=r.convert(B.type),Pe=M(B.internalFormat,Oe,ye,B.colorSpace),dt=n.get(S),ae=n.get(B);if(ae.__renderTarget=S,!dt.__hasExternalTextures){const Ie=Math.max(1,S.width>>Y),qe=Math.max(1,S.height>>Y);ee===i.TEXTURE_3D||ee===i.TEXTURE_2D_ARRAY?t.texImage3D(ee,Y,Pe,Ie,qe,S.depth,0,Oe,ye,null):t.texImage2D(ee,Y,Pe,Ie,qe,0,Oe,ye,null)}t.bindFramebuffer(i.FRAMEBUFFER,R),Le(S)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,$,ee,ae.__webglTexture,0,re(S)):(ee===i.TEXTURE_2D||ee>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&ee<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,$,ee,ae.__webglTexture,Y),t.bindFramebuffer(i.FRAMEBUFFER,null)}function pe(R,S,B){if(i.bindRenderbuffer(i.RENDERBUFFER,R),S.depthBuffer){const $=S.depthTexture,ee=$&&$.isDepthTexture?$.type:null,Y=x(S.stencilBuffer,ee),Oe=S.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,ye=re(S);Le(S)?a.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,ye,Y,S.width,S.height):B?i.renderbufferStorageMultisample(i.RENDERBUFFER,ye,Y,S.width,S.height):i.renderbufferStorage(i.RENDERBUFFER,Y,S.width,S.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,Oe,i.RENDERBUFFER,R)}else{const $=S.textures;for(let ee=0;ee<$.length;ee++){const Y=$[ee],Oe=r.convert(Y.format,Y.colorSpace),ye=r.convert(Y.type),Pe=M(Y.internalFormat,Oe,ye,Y.colorSpace),dt=re(S);B&&Le(S)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,dt,Pe,S.width,S.height):Le(S)?a.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,dt,Pe,S.width,S.height):i.renderbufferStorage(i.RENDERBUFFER,Pe,S.width,S.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function We(R,S){if(S&&S.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(i.FRAMEBUFFER,R),!(S.depthTexture&&S.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const $=n.get(S.depthTexture);$.__renderTarget=S,(!$.__webglTexture||S.depthTexture.image.width!==S.width||S.depthTexture.image.height!==S.height)&&(S.depthTexture.image.width=S.width,S.depthTexture.image.height=S.height,S.depthTexture.needsUpdate=!0),K(S.depthTexture,0);const ee=$.__webglTexture,Y=re(S);if(S.depthTexture.format===ir)Le(S)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,ee,0,Y):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,ee,0);else if(S.depthTexture.format===fr)Le(S)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,ee,0,Y):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,ee,0);else throw new Error("Unknown depthTexture format")}function Ze(R){const S=n.get(R),B=R.isWebGLCubeRenderTarget===!0;if(S.__boundDepthTexture!==R.depthTexture){const $=R.depthTexture;if(S.__depthDisposeCallback&&S.__depthDisposeCallback(),$){const ee=()=>{delete S.__boundDepthTexture,delete S.__depthDisposeCallback,$.removeEventListener("dispose",ee)};$.addEventListener("dispose",ee),S.__depthDisposeCallback=ee}S.__boundDepthTexture=$}if(R.depthTexture&&!S.__autoAllocateDepthBuffer){if(B)throw new Error("target.depthTexture not supported in Cube render targets");We(S.__webglFramebuffer,R)}else if(B){S.__webglDepthbuffer=[];for(let $=0;$<6;$++)if(t.bindFramebuffer(i.FRAMEBUFFER,S.__webglFramebuffer[$]),S.__webglDepthbuffer[$]===void 0)S.__webglDepthbuffer[$]=i.createRenderbuffer(),pe(S.__webglDepthbuffer[$],R,!1);else{const ee=R.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Y=S.__webglDepthbuffer[$];i.bindRenderbuffer(i.RENDERBUFFER,Y),i.framebufferRenderbuffer(i.FRAMEBUFFER,ee,i.RENDERBUFFER,Y)}}else if(t.bindFramebuffer(i.FRAMEBUFFER,S.__webglFramebuffer),S.__webglDepthbuffer===void 0)S.__webglDepthbuffer=i.createRenderbuffer(),pe(S.__webglDepthbuffer,R,!1);else{const $=R.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,ee=S.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,ee),i.framebufferRenderbuffer(i.FRAMEBUFFER,$,i.RENDERBUFFER,ee)}t.bindFramebuffer(i.FRAMEBUFFER,null)}function je(R,S,B){const $=n.get(R);S!==void 0&&Ne($.__webglFramebuffer,R,R.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),B!==void 0&&Ze(R)}function gt(R){const S=R.texture,B=n.get(R),$=n.get(S);R.addEventListener("dispose",P);const ee=R.textures,Y=R.isWebGLCubeRenderTarget===!0,Oe=ee.length>1;if(Oe||($.__webglTexture===void 0&&($.__webglTexture=i.createTexture()),$.__version=S.version,o.memory.textures++),Y){B.__webglFramebuffer=[];for(let ye=0;ye<6;ye++)if(S.mipmaps&&S.mipmaps.length>0){B.__webglFramebuffer[ye]=[];for(let Pe=0;Pe<S.mipmaps.length;Pe++)B.__webglFramebuffer[ye][Pe]=i.createFramebuffer()}else B.__webglFramebuffer[ye]=i.createFramebuffer()}else{if(S.mipmaps&&S.mipmaps.length>0){B.__webglFramebuffer=[];for(let ye=0;ye<S.mipmaps.length;ye++)B.__webglFramebuffer[ye]=i.createFramebuffer()}else B.__webglFramebuffer=i.createFramebuffer();if(Oe)for(let ye=0,Pe=ee.length;ye<Pe;ye++){const dt=n.get(ee[ye]);dt.__webglTexture===void 0&&(dt.__webglTexture=i.createTexture(),o.memory.textures++)}if(R.samples>0&&Le(R)===!1){B.__webglMultisampledFramebuffer=i.createFramebuffer(),B.__webglColorRenderbuffer=[],t.bindFramebuffer(i.FRAMEBUFFER,B.__webglMultisampledFramebuffer);for(let ye=0;ye<ee.length;ye++){const Pe=ee[ye];B.__webglColorRenderbuffer[ye]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,B.__webglColorRenderbuffer[ye]);const dt=r.convert(Pe.format,Pe.colorSpace),ae=r.convert(Pe.type),Ie=M(Pe.internalFormat,dt,ae,Pe.colorSpace,R.isXRRenderTarget===!0),qe=re(R);i.renderbufferStorageMultisample(i.RENDERBUFFER,qe,Ie,R.width,R.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+ye,i.RENDERBUFFER,B.__webglColorRenderbuffer[ye])}i.bindRenderbuffer(i.RENDERBUFFER,null),R.depthBuffer&&(B.__webglDepthRenderbuffer=i.createRenderbuffer(),pe(B.__webglDepthRenderbuffer,R,!0)),t.bindFramebuffer(i.FRAMEBUFFER,null)}}if(Y){t.bindTexture(i.TEXTURE_CUBE_MAP,$.__webglTexture),tt(i.TEXTURE_CUBE_MAP,S);for(let ye=0;ye<6;ye++)if(S.mipmaps&&S.mipmaps.length>0)for(let Pe=0;Pe<S.mipmaps.length;Pe++)Ne(B.__webglFramebuffer[ye][Pe],R,S,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+ye,Pe);else Ne(B.__webglFramebuffer[ye],R,S,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+ye,0);g(S)&&p(i.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Oe){for(let ye=0,Pe=ee.length;ye<Pe;ye++){const dt=ee[ye],ae=n.get(dt);t.bindTexture(i.TEXTURE_2D,ae.__webglTexture),tt(i.TEXTURE_2D,dt),Ne(B.__webglFramebuffer,R,dt,i.COLOR_ATTACHMENT0+ye,i.TEXTURE_2D,0),g(dt)&&p(i.TEXTURE_2D)}t.unbindTexture()}else{let ye=i.TEXTURE_2D;if((R.isWebGL3DRenderTarget||R.isWebGLArrayRenderTarget)&&(ye=R.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),t.bindTexture(ye,$.__webglTexture),tt(ye,S),S.mipmaps&&S.mipmaps.length>0)for(let Pe=0;Pe<S.mipmaps.length;Pe++)Ne(B.__webglFramebuffer[Pe],R,S,i.COLOR_ATTACHMENT0,ye,Pe);else Ne(B.__webglFramebuffer,R,S,i.COLOR_ATTACHMENT0,ye,0);g(S)&&p(ye),t.unbindTexture()}R.depthBuffer&&Ze(R)}function Q(R){const S=R.textures;for(let B=0,$=S.length;B<$;B++){const ee=S[B];if(g(ee)){const Y=y(R),Oe=n.get(ee).__webglTexture;t.bindTexture(Y,Oe),p(Y),t.unbindTexture()}}}const le=[],I=[];function ze(R){if(R.samples>0){if(Le(R)===!1){const S=R.textures,B=R.width,$=R.height;let ee=i.COLOR_BUFFER_BIT;const Y=R.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Oe=n.get(R),ye=S.length>1;if(ye)for(let Pe=0;Pe<S.length;Pe++)t.bindFramebuffer(i.FRAMEBUFFER,Oe.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Pe,i.RENDERBUFFER,null),t.bindFramebuffer(i.FRAMEBUFFER,Oe.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Pe,i.TEXTURE_2D,null,0);t.bindFramebuffer(i.READ_FRAMEBUFFER,Oe.__webglMultisampledFramebuffer),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Oe.__webglFramebuffer);for(let Pe=0;Pe<S.length;Pe++){if(R.resolveDepthBuffer&&(R.depthBuffer&&(ee|=i.DEPTH_BUFFER_BIT),R.stencilBuffer&&R.resolveStencilBuffer&&(ee|=i.STENCIL_BUFFER_BIT)),ye){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,Oe.__webglColorRenderbuffer[Pe]);const dt=n.get(S[Pe]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,dt,0)}i.blitFramebuffer(0,0,B,$,0,0,B,$,ee,i.NEAREST),c===!0&&(le.length=0,I.length=0,le.push(i.COLOR_ATTACHMENT0+Pe),R.depthBuffer&&R.resolveDepthBuffer===!1&&(le.push(Y),I.push(Y),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,I)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,le))}if(t.bindFramebuffer(i.READ_FRAMEBUFFER,null),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),ye)for(let Pe=0;Pe<S.length;Pe++){t.bindFramebuffer(i.FRAMEBUFFER,Oe.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Pe,i.RENDERBUFFER,Oe.__webglColorRenderbuffer[Pe]);const dt=n.get(S[Pe]).__webglTexture;t.bindFramebuffer(i.FRAMEBUFFER,Oe.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Pe,i.TEXTURE_2D,dt,0)}t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Oe.__webglMultisampledFramebuffer)}else if(R.depthBuffer&&R.resolveDepthBuffer===!1&&c){const S=R.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[S])}}}function re(R){return Math.min(s.maxSamples,R.samples)}function Le(R){const S=n.get(R);return R.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&S.__useRenderToTexture!==!1}function ge(R){const S=o.render.frame;h.get(R)!==S&&(h.set(R,S),R.update())}function Xe(R,S){const B=R.colorSpace,$=R.format,ee=R.type;return R.isCompressedTexture===!0||R.isVideoTexture===!0||B!==mn&&B!==Wi&&(ft.getTransfer(B)===Rt?($!==kn||ee!==Ai)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",B)),S}function Ce(R){return typeof HTMLImageElement<"u"&&R instanceof HTMLImageElement?(l.width=R.naturalWidth||R.width,l.height=R.naturalHeight||R.height):typeof VideoFrame<"u"&&R instanceof VideoFrame?(l.width=R.displayWidth,l.height=R.displayHeight):(l.width=R.width,l.height=R.height),l}this.allocateTextureUnit=O,this.resetTextureUnits=F,this.setTexture2D=K,this.setTexture2DArray=X,this.setTexture3D=j,this.setTextureCube=V,this.rebindTextures=je,this.setupRenderTarget=gt,this.updateRenderTargetMipmap=Q,this.updateMultisampleRenderTarget=ze,this.setupDepthRenderbuffer=Ze,this.setupFrameBufferTexture=Ne,this.useMultisampledRTT=Le}function Zv(i,e){function t(n,s=Wi){let r;const o=ft.getTransfer(s);if(n===Ai)return i.UNSIGNED_BYTE;if(n===nh)return i.UNSIGNED_SHORT_4_4_4_4;if(n===ih)return i.UNSIGNED_SHORT_5_5_5_1;if(n===Yd)return i.UNSIGNED_INT_5_9_9_9_REV;if(n===jd)return i.BYTE;if(n===$d)return i.SHORT;if(n===io)return i.UNSIGNED_SHORT;if(n===th)return i.INT;if(n===Es)return i.UNSIGNED_INT;if(n===Jn)return i.FLOAT;if(n===uo)return i.HALF_FLOAT;if(n===Kd)return i.ALPHA;if(n===Zd)return i.RGB;if(n===kn)return i.RGBA;if(n===Jd)return i.LUMINANCE;if(n===Qd)return i.LUMINANCE_ALPHA;if(n===ir)return i.DEPTH_COMPONENT;if(n===fr)return i.DEPTH_STENCIL;if(n===sh)return i.RED;if(n===rh)return i.RED_INTEGER;if(n===ef)return i.RG;if(n===oh)return i.RG_INTEGER;if(n===ah)return i.RGBA_INTEGER;if(n===ua||n===da||n===fa||n===pa)if(o===Rt)if(r=e.get("WEBGL_compressed_texture_s3tc_srgb"),r!==null){if(n===ua)return r.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===da)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===fa)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===pa)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(r=e.get("WEBGL_compressed_texture_s3tc"),r!==null){if(n===ua)return r.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===da)return r.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===fa)return r.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===pa)return r.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===dl||n===fl||n===pl||n===ml)if(r=e.get("WEBGL_compressed_texture_pvrtc"),r!==null){if(n===dl)return r.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===fl)return r.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===pl)return r.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===ml)return r.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===gl||n===_l||n===xl)if(r=e.get("WEBGL_compressed_texture_etc"),r!==null){if(n===gl||n===_l)return o===Rt?r.COMPRESSED_SRGB8_ETC2:r.COMPRESSED_RGB8_ETC2;if(n===xl)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:r.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===vl||n===yl||n===Ml||n===wl||n===bl||n===Sl||n===El||n===Tl||n===Al||n===Rl||n===Cl||n===Pl||n===Ll||n===Il)if(r=e.get("WEBGL_compressed_texture_astc"),r!==null){if(n===vl)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:r.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===yl)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:r.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Ml)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:r.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===wl)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:r.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===bl)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:r.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===Sl)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:r.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===El)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:r.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===Tl)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:r.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===Al)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:r.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===Rl)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:r.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===Cl)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:r.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===Pl)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:r.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Ll)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:r.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===Il)return o===Rt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:r.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===ma||n===Dl||n===Nl)if(r=e.get("EXT_texture_compression_bptc"),r!==null){if(n===ma)return o===Rt?r.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:r.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===Dl)return r.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===Nl)return r.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===tf||n===Ul||n===Ol||n===Fl)if(r=e.get("EXT_texture_compression_rgtc"),r!==null){if(n===ma)return r.COMPRESSED_RED_RGTC1_EXT;if(n===Ul)return r.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===Ol)return r.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===Fl)return r.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===dr?i.UNSIGNED_INT_24_8:i[n]!==void 0?i[n]:null}return{convert:t}}class Jv extends Tn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class Ct extends Nt{constructor(){super(),this.isGroup=!0,this.type="Group"}}const Qv={type:"move"};class Ac{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Ct,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Ct,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new v,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new v),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Ct,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new v,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new v),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let s=null,r=null,o=null;const a=this._targetRay,c=this._grip,l=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(l&&e.hand){o=!0;for(const _ of e.hand.values()){const g=t.getJointPose(_,n),p=this._getHandJoint(l,_);g!==null&&(p.matrix.fromArray(g.transform.matrix),p.matrix.decompose(p.position,p.rotation,p.scale),p.matrixWorldNeedsUpdate=!0,p.jointRadius=g.radius),p.visible=g!==null}const h=l.joints["index-finger-tip"],u=l.joints["thumb-tip"],d=h.position.distanceTo(u.position),f=.02,m=.005;l.inputState.pinching&&d>f+m?(l.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!l.inputState.pinching&&d<=f-m&&(l.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else c!==null&&e.gripSpace&&(r=t.getPose(e.gripSpace,n),r!==null&&(c.matrix.fromArray(r.transform.matrix),c.matrix.decompose(c.position,c.rotation,c.scale),c.matrixWorldNeedsUpdate=!0,r.linearVelocity?(c.hasLinearVelocity=!0,c.linearVelocity.copy(r.linearVelocity)):c.hasLinearVelocity=!1,r.angularVelocity?(c.hasAngularVelocity=!0,c.angularVelocity.copy(r.angularVelocity)):c.hasAngularVelocity=!1));a!==null&&(s=t.getPose(e.targetRaySpace,n),s===null&&r!==null&&(s=r),s!==null&&(a.matrix.fromArray(s.transform.matrix),a.matrix.decompose(a.position,a.rotation,a.scale),a.matrixWorldNeedsUpdate=!0,s.linearVelocity?(a.hasLinearVelocity=!0,a.linearVelocity.copy(s.linearVelocity)):a.hasLinearVelocity=!1,s.angularVelocity?(a.hasAngularVelocity=!0,a.angularVelocity.copy(s.angularVelocity)):a.hasAngularVelocity=!1,this.dispatchEvent(Qv)))}return a!==null&&(a.visible=s!==null),c!==null&&(c.visible=r!==null),l!==null&&(l.visible=o!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new Ct;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const ey=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,ty=`
uniform sampler2DArray depthColor;
uniform float depthWidth;
uniform float depthHeight;

void main() {

	vec2 coord = vec2( gl_FragCoord.x / depthWidth, gl_FragCoord.y / depthHeight );

	if ( coord.x >= 1.0 ) {

		gl_FragDepth = texture( depthColor, vec3( coord.x - 1.0, coord.y, 1 ) ).r;

	} else {

		gl_FragDepth = texture( depthColor, vec3( coord.x, coord.y, 0 ) ).r;

	}

}`;class ny{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const s=new Qt,r=e.properties.get(s);r.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=s}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new oi({vertexShader:ey,fragmentShader:ty,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new Xt(new ai(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class iy extends Mr{constructor(e,t){super();const n=this;let s=null,r=1,o=null,a="local-floor",c=1,l=null,h=null,u=null,d=null,f=null,m=null;const _=new ny,g=t.getContextAttributes();let p=null,y=null;const M=[],x=[],E=new te;let T=null;const P=new Tn;P.viewport=new yt;const C=new Tn;C.viewport=new yt;const b=[P,C],w=new Jv;let L=null,F=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(Z){let he=M[Z];return he===void 0&&(he=new Ac,M[Z]=he),he.getTargetRaySpace()},this.getControllerGrip=function(Z){let he=M[Z];return he===void 0&&(he=new Ac,M[Z]=he),he.getGripSpace()},this.getHand=function(Z){let he=M[Z];return he===void 0&&(he=new Ac,M[Z]=he),he.getHandSpace()};function O(Z){const he=x.indexOf(Z.inputSource);if(he===-1)return;const Ne=M[he];Ne!==void 0&&(Ne.update(Z.inputSource,Z.frame,l||o),Ne.dispatchEvent({type:Z.type,data:Z.inputSource}))}function k(){s.removeEventListener("select",O),s.removeEventListener("selectstart",O),s.removeEventListener("selectend",O),s.removeEventListener("squeeze",O),s.removeEventListener("squeezestart",O),s.removeEventListener("squeezeend",O),s.removeEventListener("end",k),s.removeEventListener("inputsourceschange",K);for(let Z=0;Z<M.length;Z++){const he=x[Z];he!==null&&(x[Z]=null,M[Z].disconnect(he))}L=null,F=null,_.reset(),e.setRenderTarget(p),f=null,d=null,u=null,s=null,y=null,wt.stop(),n.isPresenting=!1,e.setPixelRatio(T),e.setSize(E.width,E.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(Z){r=Z,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(Z){a=Z,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return l||o},this.setReferenceSpace=function(Z){l=Z},this.getBaseLayer=function(){return d!==null?d:f},this.getBinding=function(){return u},this.getFrame=function(){return m},this.getSession=function(){return s},this.setSession=async function(Z){if(s=Z,s!==null){if(p=e.getRenderTarget(),s.addEventListener("select",O),s.addEventListener("selectstart",O),s.addEventListener("selectend",O),s.addEventListener("squeeze",O),s.addEventListener("squeezestart",O),s.addEventListener("squeezeend",O),s.addEventListener("end",k),s.addEventListener("inputsourceschange",K),g.xrCompatible!==!0&&await t.makeXRCompatible(),T=e.getPixelRatio(),e.getSize(E),s.renderState.layers===void 0){const he={antialias:g.antialias,alpha:!0,depth:g.depth,stencil:g.stencil,framebufferScaleFactor:r};f=new XRWebGLLayer(s,t,he),s.updateRenderState({baseLayer:f}),e.setPixelRatio(1),e.setSize(f.framebufferWidth,f.framebufferHeight,!1),y=new Ts(f.framebufferWidth,f.framebufferHeight,{format:kn,type:Ai,colorSpace:e.outputColorSpace,stencilBuffer:g.stencil})}else{let he=null,Ne=null,pe=null;g.depth&&(pe=g.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,he=g.stencil?fr:ir,Ne=g.stencil?dr:Es);const We={colorFormat:t.RGBA8,depthFormat:pe,scaleFactor:r};u=new XRWebGLBinding(s,t),d=u.createProjectionLayer(We),s.updateRenderState({layers:[d]}),e.setPixelRatio(1),e.setSize(d.textureWidth,d.textureHeight,!1),y=new Ts(d.textureWidth,d.textureHeight,{format:kn,type:Ai,depthTexture:new gf(d.textureWidth,d.textureHeight,Ne,void 0,void 0,void 0,void 0,void 0,void 0,he),stencilBuffer:g.stencil,colorSpace:e.outputColorSpace,samples:g.antialias?4:0,resolveDepthBuffer:d.ignoreDepthValues===!1})}y.isXRRenderTarget=!0,this.setFoveation(c),l=null,o=await s.requestReferenceSpace(a),wt.setContext(s),wt.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(s!==null)return s.environmentBlendMode},this.getDepthTexture=function(){return _.getDepthTexture()};function K(Z){for(let he=0;he<Z.removed.length;he++){const Ne=Z.removed[he],pe=x.indexOf(Ne);pe>=0&&(x[pe]=null,M[pe].disconnect(Ne))}for(let he=0;he<Z.added.length;he++){const Ne=Z.added[he];let pe=x.indexOf(Ne);if(pe===-1){for(let Ze=0;Ze<M.length;Ze++)if(Ze>=x.length){x.push(Ne),pe=Ze;break}else if(x[Ze]===null){x[Ze]=Ne,pe=Ze;break}if(pe===-1)break}const We=M[pe];We&&We.connect(Ne)}}const X=new v,j=new v;function V(Z,he,Ne){X.setFromMatrixPosition(he.matrixWorld),j.setFromMatrixPosition(Ne.matrixWorld);const pe=X.distanceTo(j),We=he.projectionMatrix.elements,Ze=Ne.projectionMatrix.elements,je=We[14]/(We[10]-1),gt=We[14]/(We[10]+1),Q=(We[9]+1)/We[5],le=(We[9]-1)/We[5],I=(We[8]-1)/We[0],ze=(Ze[8]+1)/Ze[0],re=je*I,Le=je*ze,ge=pe/(-I+ze),Xe=ge*-I;if(he.matrixWorld.decompose(Z.position,Z.quaternion,Z.scale),Z.translateX(Xe),Z.translateZ(ge),Z.matrixWorld.compose(Z.position,Z.quaternion,Z.scale),Z.matrixWorldInverse.copy(Z.matrixWorld).invert(),We[10]===-1)Z.projectionMatrix.copy(he.projectionMatrix),Z.projectionMatrixInverse.copy(he.projectionMatrixInverse);else{const Ce=je+ge,R=gt+ge,S=re-Xe,B=Le+(pe-Xe),$=Q*gt/R*Ce,ee=le*gt/R*Ce;Z.projectionMatrix.makePerspective(S,B,$,ee,Ce,R),Z.projectionMatrixInverse.copy(Z.projectionMatrix).invert()}}function oe(Z,he){he===null?Z.matrixWorld.copy(Z.matrix):Z.matrixWorld.multiplyMatrices(he.matrixWorld,Z.matrix),Z.matrixWorldInverse.copy(Z.matrixWorld).invert()}this.updateCamera=function(Z){if(s===null)return;let he=Z.near,Ne=Z.far;_.texture!==null&&(_.depthNear>0&&(he=_.depthNear),_.depthFar>0&&(Ne=_.depthFar)),w.near=C.near=P.near=he,w.far=C.far=P.far=Ne,(L!==w.near||F!==w.far)&&(s.updateRenderState({depthNear:w.near,depthFar:w.far}),L=w.near,F=w.far),P.layers.mask=Z.layers.mask|2,C.layers.mask=Z.layers.mask|4,w.layers.mask=P.layers.mask|C.layers.mask;const pe=Z.parent,We=w.cameras;oe(w,pe);for(let Ze=0;Ze<We.length;Ze++)oe(We[Ze],pe);We.length===2?V(w,P,C):w.projectionMatrix.copy(P.projectionMatrix),_e(Z,w,pe)};function _e(Z,he,Ne){Ne===null?Z.matrix.copy(he.matrixWorld):(Z.matrix.copy(Ne.matrixWorld),Z.matrix.invert(),Z.matrix.multiply(he.matrixWorld)),Z.matrix.decompose(Z.position,Z.quaternion,Z.scale),Z.updateMatrixWorld(!0),Z.projectionMatrix.copy(he.projectionMatrix),Z.projectionMatrixInverse.copy(he.projectionMatrixInverse),Z.isPerspectiveCamera&&(Z.fov=pr*2*Math.atan(1/Z.projectionMatrix.elements[5]),Z.zoom=1)}this.getCamera=function(){return w},this.getFoveation=function(){if(!(d===null&&f===null))return c},this.setFoveation=function(Z){c=Z,d!==null&&(d.fixedFoveation=Z),f!==null&&f.fixedFoveation!==void 0&&(f.fixedFoveation=Z)},this.hasDepthSensing=function(){return _.texture!==null},this.getDepthSensingMesh=function(){return _.getMesh(w)};let Re=null;function tt(Z,he){if(h=he.getViewerPose(l||o),m=he,h!==null){const Ne=h.views;f!==null&&(e.setRenderTargetFramebuffer(y,f.framebuffer),e.setRenderTarget(y));let pe=!1;Ne.length!==w.cameras.length&&(w.cameras.length=0,pe=!0);for(let Ze=0;Ze<Ne.length;Ze++){const je=Ne[Ze];let gt=null;if(f!==null)gt=f.getViewport(je);else{const le=u.getViewSubImage(d,je);gt=le.viewport,Ze===0&&(e.setRenderTargetTextures(y,le.colorTexture,d.ignoreDepthValues?void 0:le.depthStencilTexture),e.setRenderTarget(y))}let Q=b[Ze];Q===void 0&&(Q=new Tn,Q.layers.enable(Ze),Q.viewport=new yt,b[Ze]=Q),Q.matrix.fromArray(je.transform.matrix),Q.matrix.decompose(Q.position,Q.quaternion,Q.scale),Q.projectionMatrix.fromArray(je.projectionMatrix),Q.projectionMatrixInverse.copy(Q.projectionMatrix).invert(),Q.viewport.set(gt.x,gt.y,gt.width,gt.height),Ze===0&&(w.matrix.copy(Q.matrix),w.matrix.decompose(w.position,w.quaternion,w.scale)),pe===!0&&w.cameras.push(Q)}const We=s.enabledFeatures;if(We&&We.includes("depth-sensing")){const Ze=u.getDepthInformation(Ne[0]);Ze&&Ze.isValid&&Ze.texture&&_.init(e,Ze,s.renderState)}}for(let Ne=0;Ne<M.length;Ne++){const pe=x[Ne],We=M[Ne];pe!==null&&We!==void 0&&We.update(pe,he,l||o)}Re&&Re(Z,he),he.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:he}),m=null}const wt=new mf;wt.setAnimationLoop(tt),this.setAnimationLoop=function(Z){Re=Z},this.dispose=function(){}}}const hs=new wn,sy=new Ae;function ry(i,e){function t(g,p){g.matrixAutoUpdate===!0&&g.updateMatrix(),p.value.copy(g.matrix)}function n(g,p){p.color.getRGB(g.fogColor.value,df(i)),p.isFog?(g.fogNear.value=p.near,g.fogFar.value=p.far):p.isFogExp2&&(g.fogDensity.value=p.density)}function s(g,p,y,M,x){p.isMeshBasicMaterial||p.isMeshLambertMaterial?r(g,p):p.isMeshToonMaterial?(r(g,p),u(g,p)):p.isMeshPhongMaterial?(r(g,p),h(g,p)):p.isMeshStandardMaterial?(r(g,p),d(g,p),p.isMeshPhysicalMaterial&&f(g,p,x)):p.isMeshMatcapMaterial?(r(g,p),m(g,p)):p.isMeshDepthMaterial?r(g,p):p.isMeshDistanceMaterial?(r(g,p),_(g,p)):p.isMeshNormalMaterial?r(g,p):p.isLineBasicMaterial?(o(g,p),p.isLineDashedMaterial&&a(g,p)):p.isPointsMaterial?c(g,p,y,M):p.isSpriteMaterial?l(g,p):p.isShadowMaterial?(g.color.value.copy(p.color),g.opacity.value=p.opacity):p.isShaderMaterial&&(p.uniformsNeedUpdate=!1)}function r(g,p){g.opacity.value=p.opacity,p.color&&g.diffuse.value.copy(p.color),p.emissive&&g.emissive.value.copy(p.emissive).multiplyScalar(p.emissiveIntensity),p.map&&(g.map.value=p.map,t(p.map,g.mapTransform)),p.alphaMap&&(g.alphaMap.value=p.alphaMap,t(p.alphaMap,g.alphaMapTransform)),p.bumpMap&&(g.bumpMap.value=p.bumpMap,t(p.bumpMap,g.bumpMapTransform),g.bumpScale.value=p.bumpScale,p.side===yn&&(g.bumpScale.value*=-1)),p.normalMap&&(g.normalMap.value=p.normalMap,t(p.normalMap,g.normalMapTransform),g.normalScale.value.copy(p.normalScale),p.side===yn&&g.normalScale.value.negate()),p.displacementMap&&(g.displacementMap.value=p.displacementMap,t(p.displacementMap,g.displacementMapTransform),g.displacementScale.value=p.displacementScale,g.displacementBias.value=p.displacementBias),p.emissiveMap&&(g.emissiveMap.value=p.emissiveMap,t(p.emissiveMap,g.emissiveMapTransform)),p.specularMap&&(g.specularMap.value=p.specularMap,t(p.specularMap,g.specularMapTransform)),p.alphaTest>0&&(g.alphaTest.value=p.alphaTest);const y=e.get(p),M=y.envMap,x=y.envMapRotation;M&&(g.envMap.value=M,hs.copy(x),hs.x*=-1,hs.y*=-1,hs.z*=-1,M.isCubeTexture&&M.isRenderTargetTexture===!1&&(hs.y*=-1,hs.z*=-1),g.envMapRotation.value.setFromMatrix4(sy.makeRotationFromEuler(hs)),g.flipEnvMap.value=M.isCubeTexture&&M.isRenderTargetTexture===!1?-1:1,g.reflectivity.value=p.reflectivity,g.ior.value=p.ior,g.refractionRatio.value=p.refractionRatio),p.lightMap&&(g.lightMap.value=p.lightMap,g.lightMapIntensity.value=p.lightMapIntensity,t(p.lightMap,g.lightMapTransform)),p.aoMap&&(g.aoMap.value=p.aoMap,g.aoMapIntensity.value=p.aoMapIntensity,t(p.aoMap,g.aoMapTransform))}function o(g,p){g.diffuse.value.copy(p.color),g.opacity.value=p.opacity,p.map&&(g.map.value=p.map,t(p.map,g.mapTransform))}function a(g,p){g.dashSize.value=p.dashSize,g.totalSize.value=p.dashSize+p.gapSize,g.scale.value=p.scale}function c(g,p,y,M){g.diffuse.value.copy(p.color),g.opacity.value=p.opacity,g.size.value=p.size*y,g.scale.value=M*.5,p.map&&(g.map.value=p.map,t(p.map,g.uvTransform)),p.alphaMap&&(g.alphaMap.value=p.alphaMap,t(p.alphaMap,g.alphaMapTransform)),p.alphaTest>0&&(g.alphaTest.value=p.alphaTest)}function l(g,p){g.diffuse.value.copy(p.color),g.opacity.value=p.opacity,g.rotation.value=p.rotation,p.map&&(g.map.value=p.map,t(p.map,g.mapTransform)),p.alphaMap&&(g.alphaMap.value=p.alphaMap,t(p.alphaMap,g.alphaMapTransform)),p.alphaTest>0&&(g.alphaTest.value=p.alphaTest)}function h(g,p){g.specular.value.copy(p.specular),g.shininess.value=Math.max(p.shininess,1e-4)}function u(g,p){p.gradientMap&&(g.gradientMap.value=p.gradientMap)}function d(g,p){g.metalness.value=p.metalness,p.metalnessMap&&(g.metalnessMap.value=p.metalnessMap,t(p.metalnessMap,g.metalnessMapTransform)),g.roughness.value=p.roughness,p.roughnessMap&&(g.roughnessMap.value=p.roughnessMap,t(p.roughnessMap,g.roughnessMapTransform)),p.envMap&&(g.envMapIntensity.value=p.envMapIntensity)}function f(g,p,y){g.ior.value=p.ior,p.sheen>0&&(g.sheenColor.value.copy(p.sheenColor).multiplyScalar(p.sheen),g.sheenRoughness.value=p.sheenRoughness,p.sheenColorMap&&(g.sheenColorMap.value=p.sheenColorMap,t(p.sheenColorMap,g.sheenColorMapTransform)),p.sheenRoughnessMap&&(g.sheenRoughnessMap.value=p.sheenRoughnessMap,t(p.sheenRoughnessMap,g.sheenRoughnessMapTransform))),p.clearcoat>0&&(g.clearcoat.value=p.clearcoat,g.clearcoatRoughness.value=p.clearcoatRoughness,p.clearcoatMap&&(g.clearcoatMap.value=p.clearcoatMap,t(p.clearcoatMap,g.clearcoatMapTransform)),p.clearcoatRoughnessMap&&(g.clearcoatRoughnessMap.value=p.clearcoatRoughnessMap,t(p.clearcoatRoughnessMap,g.clearcoatRoughnessMapTransform)),p.clearcoatNormalMap&&(g.clearcoatNormalMap.value=p.clearcoatNormalMap,t(p.clearcoatNormalMap,g.clearcoatNormalMapTransform),g.clearcoatNormalScale.value.copy(p.clearcoatNormalScale),p.side===yn&&g.clearcoatNormalScale.value.negate())),p.dispersion>0&&(g.dispersion.value=p.dispersion),p.iridescence>0&&(g.iridescence.value=p.iridescence,g.iridescenceIOR.value=p.iridescenceIOR,g.iridescenceThicknessMinimum.value=p.iridescenceThicknessRange[0],g.iridescenceThicknessMaximum.value=p.iridescenceThicknessRange[1],p.iridescenceMap&&(g.iridescenceMap.value=p.iridescenceMap,t(p.iridescenceMap,g.iridescenceMapTransform)),p.iridescenceThicknessMap&&(g.iridescenceThicknessMap.value=p.iridescenceThicknessMap,t(p.iridescenceThicknessMap,g.iridescenceThicknessMapTransform))),p.transmission>0&&(g.transmission.value=p.transmission,g.transmissionSamplerMap.value=y.texture,g.transmissionSamplerSize.value.set(y.width,y.height),p.transmissionMap&&(g.transmissionMap.value=p.transmissionMap,t(p.transmissionMap,g.transmissionMapTransform)),g.thickness.value=p.thickness,p.thicknessMap&&(g.thicknessMap.value=p.thicknessMap,t(p.thicknessMap,g.thicknessMapTransform)),g.attenuationDistance.value=p.attenuationDistance,g.attenuationColor.value.copy(p.attenuationColor)),p.anisotropy>0&&(g.anisotropyVector.value.set(p.anisotropy*Math.cos(p.anisotropyRotation),p.anisotropy*Math.sin(p.anisotropyRotation)),p.anisotropyMap&&(g.anisotropyMap.value=p.anisotropyMap,t(p.anisotropyMap,g.anisotropyMapTransform))),g.specularIntensity.value=p.specularIntensity,g.specularColor.value.copy(p.specularColor),p.specularColorMap&&(g.specularColorMap.value=p.specularColorMap,t(p.specularColorMap,g.specularColorMapTransform)),p.specularIntensityMap&&(g.specularIntensityMap.value=p.specularIntensityMap,t(p.specularIntensityMap,g.specularIntensityMapTransform))}function m(g,p){p.matcap&&(g.matcap.value=p.matcap)}function _(g,p){const y=e.get(p).light;g.referencePosition.value.setFromMatrixPosition(y.matrixWorld),g.nearDistance.value=y.shadow.camera.near,g.farDistance.value=y.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:s}}function oy(i,e,t,n){let s={},r={},o=[];const a=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function c(y,M){const x=M.program;n.uniformBlockBinding(y,x)}function l(y,M){let x=s[y.id];x===void 0&&(m(y),x=h(y),s[y.id]=x,y.addEventListener("dispose",g));const E=M.program;n.updateUBOMapping(y,E);const T=e.render.frame;r[y.id]!==T&&(d(y),r[y.id]=T)}function h(y){const M=u();y.__bindingPointIndex=M;const x=i.createBuffer(),E=y.__size,T=y.usage;return i.bindBuffer(i.UNIFORM_BUFFER,x),i.bufferData(i.UNIFORM_BUFFER,E,T),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,M,x),x}function u(){for(let y=0;y<a;y++)if(o.indexOf(y)===-1)return o.push(y),y;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function d(y){const M=s[y.id],x=y.uniforms,E=y.__cache;i.bindBuffer(i.UNIFORM_BUFFER,M);for(let T=0,P=x.length;T<P;T++){const C=Array.isArray(x[T])?x[T]:[x[T]];for(let b=0,w=C.length;b<w;b++){const L=C[b];if(f(L,T,b,E)===!0){const F=L.__offset,O=Array.isArray(L.value)?L.value:[L.value];let k=0;for(let K=0;K<O.length;K++){const X=O[K],j=_(X);typeof X=="number"||typeof X=="boolean"?(L.__data[0]=X,i.bufferSubData(i.UNIFORM_BUFFER,F+k,L.__data)):X.isMatrix3?(L.__data[0]=X.elements[0],L.__data[1]=X.elements[1],L.__data[2]=X.elements[2],L.__data[3]=0,L.__data[4]=X.elements[3],L.__data[5]=X.elements[4],L.__data[6]=X.elements[5],L.__data[7]=0,L.__data[8]=X.elements[6],L.__data[9]=X.elements[7],L.__data[10]=X.elements[8],L.__data[11]=0):(X.toArray(L.__data,k),k+=j.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,F,L.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function f(y,M,x,E){const T=y.value,P=M+"_"+x;if(E[P]===void 0)return typeof T=="number"||typeof T=="boolean"?E[P]=T:E[P]=T.clone(),!0;{const C=E[P];if(typeof T=="number"||typeof T=="boolean"){if(C!==T)return E[P]=T,!0}else if(C.equals(T)===!1)return C.copy(T),!0}return!1}function m(y){const M=y.uniforms;let x=0;const E=16;for(let P=0,C=M.length;P<C;P++){const b=Array.isArray(M[P])?M[P]:[M[P]];for(let w=0,L=b.length;w<L;w++){const F=b[w],O=Array.isArray(F.value)?F.value:[F.value];for(let k=0,K=O.length;k<K;k++){const X=O[k],j=_(X),V=x%E,oe=V%j.boundary,_e=V+oe;x+=oe,_e!==0&&E-_e<j.storage&&(x+=E-_e),F.__data=new Float32Array(j.storage/Float32Array.BYTES_PER_ELEMENT),F.__offset=x,x+=j.storage}}}const T=x%E;return T>0&&(x+=E-T),y.__size=x,y.__cache={},this}function _(y){const M={boundary:0,storage:0};return typeof y=="number"||typeof y=="boolean"?(M.boundary=4,M.storage=4):y.isVector2?(M.boundary=8,M.storage=8):y.isVector3||y.isColor?(M.boundary=16,M.storage=12):y.isVector4?(M.boundary=16,M.storage=16):y.isMatrix3?(M.boundary=48,M.storage=48):y.isMatrix4?(M.boundary=64,M.storage=64):y.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",y),M}function g(y){const M=y.target;M.removeEventListener("dispose",g);const x=o.indexOf(M.__bindingPointIndex);o.splice(x,1),i.deleteBuffer(s[M.id]),delete s[M.id],delete r[M.id]}function p(){for(const y in s)i.deleteBuffer(s[y]);o=[],s={},r={}}return{bind:c,update:l,dispose:p}}class ay{constructor(e={}){const{canvas:t=Ym(),context:n=null,depth:s=!0,stencil:r=!1,alpha:o=!1,antialias:a=!1,premultipliedAlpha:c=!0,preserveDrawingBuffer:l=!1,powerPreference:h="default",failIfMajorPerformanceCaveat:u=!1,reverseDepthBuffer:d=!1}=e;this.isWebGLRenderer=!0;let f;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");f=n.getContextAttributes().alpha}else f=o;const m=new Uint32Array(4),_=new Int32Array(4);let g=null,p=null;const y=[],M=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=qt,this.toneMapping=Ji,this.toneMappingExposure=1;const x=this;let E=!1,T=0,P=0,C=null,b=-1,w=null;const L=new yt,F=new yt;let O=null;const k=new Ve(0);let K=0,X=t.width,j=t.height,V=1,oe=null,_e=null;const Re=new yt(0,0,X,j),tt=new yt(0,0,X,j);let wt=!1;const Z=new hh;let he=!1,Ne=!1;const pe=new Ae,We=new Ae,Ze=new v,je=new yt,gt={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Q=!1;function le(){return C===null?V:1}let I=n;function ze(A,N){return t.getContext(A,N)}try{const A={alpha:!0,depth:s,stencil:r,antialias:a,premultipliedAlpha:c,preserveDrawingBuffer:l,powerPreference:h,failIfMajorPerformanceCaveat:u};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${eh}`),t.addEventListener("webglcontextlost",J,!1),t.addEventListener("webglcontextrestored",Se,!1),t.addEventListener("webglcontextcreationerror",we,!1),I===null){const N="webgl2";if(I=ze(N,A),I===null)throw ze(N)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(A){throw console.error("THREE.WebGLRenderer: "+A.message),A}let re,Le,ge,Xe,Ce,R,S,B,$,ee,Y,Oe,ye,Pe,dt,ae,Ie,qe,Ye,De,pt,ot,Lt,D;function Me(){re=new dx(I),re.init(),ot=new Zv(I,re),Le=new ox(I,re,e,ot),ge=new $v(I,re),Le.reverseDepthBuffer&&d&&ge.buffers.depth.setReversed(!0),Xe=new mx(I),Ce=new Dv,R=new Kv(I,re,ge,Ce,Le,ot,Xe),S=new cx(x),B=new ux(x),$=new w0(I),Lt=new sx(I,$),ee=new fx(I,$,Xe,Lt),Y=new _x(I,ee,$,Xe),Ye=new gx(I,Le,R),ae=new ax(Ce),Oe=new Iv(x,S,B,re,Le,Lt,ae),ye=new ry(x,Ce),Pe=new Uv,dt=new Hv(re),qe=new ix(x,S,B,ge,Y,f,c),Ie=new qv(x,Y,Le),D=new oy(I,Xe,Le,ge),De=new rx(I,re,Xe),pt=new px(I,re,Xe),Xe.programs=Oe.programs,x.capabilities=Le,x.extensions=re,x.properties=Ce,x.renderLists=Pe,x.shadowMap=Ie,x.state=ge,x.info=Xe}Me();const q=new iy(x,I);this.xr=q,this.getContext=function(){return I},this.getContextAttributes=function(){return I.getContextAttributes()},this.forceContextLoss=function(){const A=re.get("WEBGL_lose_context");A&&A.loseContext()},this.forceContextRestore=function(){const A=re.get("WEBGL_lose_context");A&&A.restoreContext()},this.getPixelRatio=function(){return V},this.setPixelRatio=function(A){A!==void 0&&(V=A,this.setSize(X,j,!1))},this.getSize=function(A){return A.set(X,j)},this.setSize=function(A,N,G=!0){if(q.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}X=A,j=N,t.width=Math.floor(A*V),t.height=Math.floor(N*V),G===!0&&(t.style.width=A+"px",t.style.height=N+"px"),this.setViewport(0,0,A,N)},this.getDrawingBufferSize=function(A){return A.set(X*V,j*V).floor()},this.setDrawingBufferSize=function(A,N,G){X=A,j=N,V=G,t.width=Math.floor(A*G),t.height=Math.floor(N*G),this.setViewport(0,0,A,N)},this.getCurrentViewport=function(A){return A.copy(L)},this.getViewport=function(A){return A.copy(Re)},this.setViewport=function(A,N,G,W){A.isVector4?Re.set(A.x,A.y,A.z,A.w):Re.set(A,N,G,W),ge.viewport(L.copy(Re).multiplyScalar(V).round())},this.getScissor=function(A){return A.copy(tt)},this.setScissor=function(A,N,G,W){A.isVector4?tt.set(A.x,A.y,A.z,A.w):tt.set(A,N,G,W),ge.scissor(F.copy(tt).multiplyScalar(V).round())},this.getScissorTest=function(){return wt},this.setScissorTest=function(A){ge.setScissorTest(wt=A)},this.setOpaqueSort=function(A){oe=A},this.setTransparentSort=function(A){_e=A},this.getClearColor=function(A){return A.copy(qe.getClearColor())},this.setClearColor=function(){qe.setClearColor.apply(qe,arguments)},this.getClearAlpha=function(){return qe.getClearAlpha()},this.setClearAlpha=function(){qe.setClearAlpha.apply(qe,arguments)},this.clear=function(A=!0,N=!0,G=!0){let W=0;if(A){let U=!1;if(C!==null){const ue=C.texture.format;U=ue===ah||ue===oh||ue===rh}if(U){const ue=C.texture.type,be=ue===Ai||ue===Es||ue===io||ue===dr||ue===nh||ue===ih,Fe=qe.getClearColor(),Be=qe.getClearAlpha(),Je=Fe.r,st=Fe.g,ke=Fe.b;be?(m[0]=Je,m[1]=st,m[2]=ke,m[3]=Be,I.clearBufferuiv(I.COLOR,0,m)):(_[0]=Je,_[1]=st,_[2]=ke,_[3]=Be,I.clearBufferiv(I.COLOR,0,_))}else W|=I.COLOR_BUFFER_BIT}N&&(W|=I.DEPTH_BUFFER_BIT),G&&(W|=I.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),I.clear(W)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",J,!1),t.removeEventListener("webglcontextrestored",Se,!1),t.removeEventListener("webglcontextcreationerror",we,!1),Pe.dispose(),dt.dispose(),Ce.dispose(),S.dispose(),B.dispose(),Y.dispose(),Lt.dispose(),D.dispose(),Oe.dispose(),q.dispose(),q.removeEventListener("sessionstart",Uh),q.removeEventListener("sessionend",Oh),is.stop()};function J(A){A.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),E=!0}function Se(){console.log("THREE.WebGLRenderer: Context Restored."),E=!1;const A=Xe.autoReset,N=Ie.enabled,G=Ie.autoUpdate,W=Ie.needsUpdate,U=Ie.type;Me(),Xe.autoReset=A,Ie.enabled=N,Ie.autoUpdate=G,Ie.needsUpdate=W,Ie.type=U}function we(A){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",A.statusMessage)}function it(A){const N=A.target;N.removeEventListener("dispose",it),Wt(N)}function Wt(A){on(A),Ce.remove(A)}function on(A){const N=Ce.get(A).programs;N!==void 0&&(N.forEach(function(G){Oe.releaseProgram(G)}),A.isShaderMaterial&&Oe.releaseShaderCache(A))}this.renderBufferDirect=function(A,N,G,W,U,ue){N===null&&(N=gt);const be=U.isMesh&&U.matrixWorld.determinant()<0,Fe=Sp(A,N,G,W,U);ge.setMaterial(W,be);let Be=G.index,Je=1;if(W.wireframe===!0){if(Be=ee.getWireframeAttribute(G),Be===void 0)return;Je=2}const st=G.drawRange,ke=G.attributes.position;let _t=st.start*Je,It=(st.start+st.count)*Je;ue!==null&&(_t=Math.max(_t,ue.start*Je),It=Math.min(It,(ue.start+ue.count)*Je)),Be!==null?(_t=Math.max(_t,0),It=Math.min(It,Be.count)):ke!=null&&(_t=Math.max(_t,0),It=Math.min(It,ke.count));const Ut=It-_t;if(Ut<0||Ut===1/0)return;Lt.setup(U,W,Fe,G,Be);let Sn,bt=De;if(Be!==null&&(Sn=$.get(Be),bt=pt,bt.setIndex(Sn)),U.isMesh)W.wireframe===!0?(ge.setLineWidth(W.wireframeLinewidth*le()),bt.setMode(I.LINES)):bt.setMode(I.TRIANGLES);else if(U.isLine){let He=W.linewidth;He===void 0&&(He=1),ge.setLineWidth(He*le()),U.isLineSegments?bt.setMode(I.LINES):U.isLineLoop?bt.setMode(I.LINE_LOOP):bt.setMode(I.LINE_STRIP)}else U.isPoints?bt.setMode(I.POINTS):U.isSprite&&bt.setMode(I.TRIANGLES);if(U.isBatchedMesh)if(U._multiDrawInstances!==null)bt.renderMultiDrawInstances(U._multiDrawStarts,U._multiDrawCounts,U._multiDrawCount,U._multiDrawInstances);else if(re.get("WEBGL_multi_draw"))bt.renderMultiDraw(U._multiDrawStarts,U._multiDrawCounts,U._multiDrawCount);else{const He=U._multiDrawStarts,fi=U._multiDrawCounts,St=U._multiDrawCount,qn=Be?$.get(Be).bytesPerElement:1,Is=Ce.get(W).currentProgram.getUniforms();for(let Cn=0;Cn<St;Cn++)Is.setValue(I,"_gl_DrawID",Cn),bt.render(He[Cn]/qn,fi[Cn])}else if(U.isInstancedMesh)bt.renderInstances(_t,Ut,U.count);else if(G.isInstancedBufferGeometry){const He=G._maxInstanceCount!==void 0?G._maxInstanceCount:1/0,fi=Math.min(G.instanceCount,He);bt.renderInstances(_t,Ut,fi)}else bt.render(_t,Ut)};function Et(A,N,G){A.transparent===!0&&A.side===An&&A.forceSinglePass===!1?(A.side=yn,A.needsUpdate=!0,wo(A,N,G),A.side=Ti,A.needsUpdate=!0,wo(A,N,G),A.side=An):wo(A,N,G)}this.compile=function(A,N,G=null){G===null&&(G=A),p=dt.get(G),p.init(N),M.push(p),G.traverseVisible(function(U){U.isLight&&U.layers.test(N.layers)&&(p.pushLight(U),U.castShadow&&p.pushShadow(U))}),A!==G&&A.traverseVisible(function(U){U.isLight&&U.layers.test(N.layers)&&(p.pushLight(U),U.castShadow&&p.pushShadow(U))}),p.setupLights();const W=new Set;return A.traverse(function(U){if(!(U.isMesh||U.isPoints||U.isLine||U.isSprite))return;const ue=U.material;if(ue)if(Array.isArray(ue))for(let be=0;be<ue.length;be++){const Fe=ue[be];Et(Fe,G,U),W.add(Fe)}else Et(ue,G,U),W.add(ue)}),M.pop(),p=null,W},this.compileAsync=function(A,N,G=null){const W=this.compile(A,N,G);return new Promise(U=>{function ue(){if(W.forEach(function(be){Ce.get(be).currentProgram.isReady()&&W.delete(be)}),W.size===0){U(A);return}setTimeout(ue,10)}re.get("KHR_parallel_shader_compile")!==null?ue():setTimeout(ue,10)})};let Xn=null;function di(A){Xn&&Xn(A)}function Uh(){is.stop()}function Oh(){is.start()}const is=new mf;is.setAnimationLoop(di),typeof self<"u"&&is.setContext(self),this.setAnimationLoop=function(A){Xn=A,q.setAnimationLoop(A),A===null?is.stop():is.start()},q.addEventListener("sessionstart",Uh),q.addEventListener("sessionend",Oh),this.render=function(A,N){if(N!==void 0&&N.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(E===!0)return;if(A.matrixWorldAutoUpdate===!0&&A.updateMatrixWorld(),N.parent===null&&N.matrixWorldAutoUpdate===!0&&N.updateMatrixWorld(),q.enabled===!0&&q.isPresenting===!0&&(q.cameraAutoUpdate===!0&&q.updateCamera(N),N=q.getCamera()),A.isScene===!0&&A.onBeforeRender(x,A,N,C),p=dt.get(A,M.length),p.init(N),M.push(p),We.multiplyMatrices(N.projectionMatrix,N.matrixWorldInverse),Z.setFromProjectionMatrix(We),Ne=this.localClippingEnabled,he=ae.init(this.clippingPlanes,Ne),g=Pe.get(A,y.length),g.init(),y.push(g),q.enabled===!0&&q.isPresenting===!0){const ue=x.xr.getDepthSensingMesh();ue!==null&&Qa(ue,N,-1/0,x.sortObjects)}Qa(A,N,0,x.sortObjects),g.finish(),x.sortObjects===!0&&g.sort(oe,_e),Q=q.enabled===!1||q.isPresenting===!1||q.hasDepthSensing()===!1,Q&&qe.addToRenderList(g,A),this.info.render.frame++,he===!0&&ae.beginShadows();const G=p.state.shadowsArray;Ie.render(G,A,N),he===!0&&ae.endShadows(),this.info.autoReset===!0&&this.info.reset();const W=g.opaque,U=g.transmissive;if(p.setupLights(),N.isArrayCamera){const ue=N.cameras;if(U.length>0)for(let be=0,Fe=ue.length;be<Fe;be++){const Be=ue[be];Bh(W,U,A,Be)}Q&&qe.render(A);for(let be=0,Fe=ue.length;be<Fe;be++){const Be=ue[be];Fh(g,A,Be,Be.viewport)}}else U.length>0&&Bh(W,U,A,N),Q&&qe.render(A),Fh(g,A,N);C!==null&&(R.updateMultisampleRenderTarget(C),R.updateRenderTargetMipmap(C)),A.isScene===!0&&A.onAfterRender(x,A,N),Lt.resetDefaultState(),b=-1,w=null,M.pop(),M.length>0?(p=M[M.length-1],he===!0&&ae.setGlobalState(x.clippingPlanes,p.state.camera)):p=null,y.pop(),y.length>0?g=y[y.length-1]:g=null};function Qa(A,N,G,W){if(A.visible===!1)return;if(A.layers.test(N.layers)){if(A.isGroup)G=A.renderOrder;else if(A.isLOD)A.autoUpdate===!0&&A.update(N);else if(A.isLight)p.pushLight(A),A.castShadow&&p.pushShadow(A);else if(A.isSprite){if(!A.frustumCulled||Z.intersectsSprite(A)){W&&je.setFromMatrixPosition(A.matrixWorld).applyMatrix4(We);const be=Y.update(A),Fe=A.material;Fe.visible&&g.push(A,be,Fe,G,je.z,null)}}else if((A.isMesh||A.isLine||A.isPoints)&&(!A.frustumCulled||Z.intersectsObject(A))){const be=Y.update(A),Fe=A.material;if(W&&(A.boundingSphere!==void 0?(A.boundingSphere===null&&A.computeBoundingSphere(),je.copy(A.boundingSphere.center)):(be.boundingSphere===null&&be.computeBoundingSphere(),je.copy(be.boundingSphere.center)),je.applyMatrix4(A.matrixWorld).applyMatrix4(We)),Array.isArray(Fe)){const Be=be.groups;for(let Je=0,st=Be.length;Je<st;Je++){const ke=Be[Je],_t=Fe[ke.materialIndex];_t&&_t.visible&&g.push(A,be,_t,G,je.z,ke)}}else Fe.visible&&g.push(A,be,Fe,G,je.z,null)}}const ue=A.children;for(let be=0,Fe=ue.length;be<Fe;be++)Qa(ue[be],N,G,W)}function Fh(A,N,G,W){const U=A.opaque,ue=A.transmissive,be=A.transparent;p.setupLightsView(G),he===!0&&ae.setGlobalState(x.clippingPlanes,G),W&&ge.viewport(L.copy(W)),U.length>0&&Mo(U,N,G),ue.length>0&&Mo(ue,N,G),be.length>0&&Mo(be,N,G),ge.buffers.depth.setTest(!0),ge.buffers.depth.setMask(!0),ge.buffers.color.setMask(!0),ge.setPolygonOffset(!1)}function Bh(A,N,G,W){if((G.isScene===!0?G.overrideMaterial:null)!==null)return;p.state.transmissionRenderTarget[W.id]===void 0&&(p.state.transmissionRenderTarget[W.id]=new Ts(1,1,{generateMipmaps:!0,type:re.has("EXT_color_buffer_half_float")||re.has("EXT_color_buffer_float")?uo:Ai,minFilter:bi,samples:4,stencilBuffer:r,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:ft.workingColorSpace}));const ue=p.state.transmissionRenderTarget[W.id],be=W.viewport||L;ue.setSize(be.z,be.w);const Fe=x.getRenderTarget();x.setRenderTarget(ue),x.getClearColor(k),K=x.getClearAlpha(),K<1&&x.setClearColor(16777215,.5),x.clear(),Q&&qe.render(G);const Be=x.toneMapping;x.toneMapping=Ji;const Je=W.viewport;if(W.viewport!==void 0&&(W.viewport=void 0),p.setupLightsView(W),he===!0&&ae.setGlobalState(x.clippingPlanes,W),Mo(A,G,W),R.updateMultisampleRenderTarget(ue),R.updateRenderTargetMipmap(ue),re.has("WEBGL_multisampled_render_to_texture")===!1){let st=!1;for(let ke=0,_t=N.length;ke<_t;ke++){const It=N[ke],Ut=It.object,Sn=It.geometry,bt=It.material,He=It.group;if(bt.side===An&&Ut.layers.test(W.layers)){const fi=bt.side;bt.side=yn,bt.needsUpdate=!0,kh(Ut,G,W,Sn,bt,He),bt.side=fi,bt.needsUpdate=!0,st=!0}}st===!0&&(R.updateMultisampleRenderTarget(ue),R.updateRenderTargetMipmap(ue))}x.setRenderTarget(Fe),x.setClearColor(k,K),Je!==void 0&&(W.viewport=Je),x.toneMapping=Be}function Mo(A,N,G){const W=N.isScene===!0?N.overrideMaterial:null;for(let U=0,ue=A.length;U<ue;U++){const be=A[U],Fe=be.object,Be=be.geometry,Je=W===null?be.material:W,st=be.group;Fe.layers.test(G.layers)&&kh(Fe,N,G,Be,Je,st)}}function kh(A,N,G,W,U,ue){A.onBeforeRender(x,N,G,W,U,ue),A.modelViewMatrix.multiplyMatrices(G.matrixWorldInverse,A.matrixWorld),A.normalMatrix.getNormalMatrix(A.modelViewMatrix),U.onBeforeRender(x,N,G,W,A,ue),U.transparent===!0&&U.side===An&&U.forceSinglePass===!1?(U.side=yn,U.needsUpdate=!0,x.renderBufferDirect(G,N,W,U,A,ue),U.side=Ti,U.needsUpdate=!0,x.renderBufferDirect(G,N,W,U,A,ue),U.side=An):x.renderBufferDirect(G,N,W,U,A,ue),A.onAfterRender(x,N,G,W,U,ue)}function wo(A,N,G){N.isScene!==!0&&(N=gt);const W=Ce.get(A),U=p.state.lights,ue=p.state.shadowsArray,be=U.state.version,Fe=Oe.getParameters(A,U.state,ue,N,G),Be=Oe.getProgramCacheKey(Fe);let Je=W.programs;W.environment=A.isMeshStandardMaterial?N.environment:null,W.fog=N.fog,W.envMap=(A.isMeshStandardMaterial?B:S).get(A.envMap||W.environment),W.envMapRotation=W.environment!==null&&A.envMap===null?N.environmentRotation:A.envMapRotation,Je===void 0&&(A.addEventListener("dispose",it),Je=new Map,W.programs=Je);let st=Je.get(Be);if(st!==void 0){if(W.currentProgram===st&&W.lightsStateVersion===be)return Hh(A,Fe),st}else Fe.uniforms=Oe.getUniforms(A),A.onBeforeCompile(Fe,x),st=Oe.acquireProgram(Fe,Be),Je.set(Be,st),W.uniforms=Fe.uniforms;const ke=W.uniforms;return(!A.isShaderMaterial&&!A.isRawShaderMaterial||A.clipping===!0)&&(ke.clippingPlanes=ae.uniform),Hh(A,Fe),W.needsLights=Tp(A),W.lightsStateVersion=be,W.needsLights&&(ke.ambientLightColor.value=U.state.ambient,ke.lightProbe.value=U.state.probe,ke.directionalLights.value=U.state.directional,ke.directionalLightShadows.value=U.state.directionalShadow,ke.spotLights.value=U.state.spot,ke.spotLightShadows.value=U.state.spotShadow,ke.rectAreaLights.value=U.state.rectArea,ke.ltc_1.value=U.state.rectAreaLTC1,ke.ltc_2.value=U.state.rectAreaLTC2,ke.pointLights.value=U.state.point,ke.pointLightShadows.value=U.state.pointShadow,ke.hemisphereLights.value=U.state.hemi,ke.directionalShadowMap.value=U.state.directionalShadowMap,ke.directionalShadowMatrix.value=U.state.directionalShadowMatrix,ke.spotShadowMap.value=U.state.spotShadowMap,ke.spotLightMatrix.value=U.state.spotLightMatrix,ke.spotLightMap.value=U.state.spotLightMap,ke.pointShadowMap.value=U.state.pointShadowMap,ke.pointShadowMatrix.value=U.state.pointShadowMatrix),W.currentProgram=st,W.uniformsList=null,st}function zh(A){if(A.uniformsList===null){const N=A.currentProgram.getUniforms();A.uniformsList=ga.seqWithValue(N.seq,A.uniforms)}return A.uniformsList}function Hh(A,N){const G=Ce.get(A);G.outputColorSpace=N.outputColorSpace,G.batching=N.batching,G.batchingColor=N.batchingColor,G.instancing=N.instancing,G.instancingColor=N.instancingColor,G.instancingMorph=N.instancingMorph,G.skinning=N.skinning,G.morphTargets=N.morphTargets,G.morphNormals=N.morphNormals,G.morphColors=N.morphColors,G.morphTargetsCount=N.morphTargetsCount,G.numClippingPlanes=N.numClippingPlanes,G.numIntersection=N.numClipIntersection,G.vertexAlphas=N.vertexAlphas,G.vertexTangents=N.vertexTangents,G.toneMapping=N.toneMapping}function Sp(A,N,G,W,U){N.isScene!==!0&&(N=gt),R.resetTextureUnits();const ue=N.fog,be=W.isMeshStandardMaterial?N.environment:null,Fe=C===null?x.outputColorSpace:C.isXRRenderTarget===!0?C.texture.colorSpace:mn,Be=(W.isMeshStandardMaterial?B:S).get(W.envMap||be),Je=W.vertexColors===!0&&!!G.attributes.color&&G.attributes.color.itemSize===4,st=!!G.attributes.tangent&&(!!W.normalMap||W.anisotropy>0),ke=!!G.morphAttributes.position,_t=!!G.morphAttributes.normal,It=!!G.morphAttributes.color;let Ut=Ji;W.toneMapped&&(C===null||C.isXRRenderTarget===!0)&&(Ut=x.toneMapping);const Sn=G.morphAttributes.position||G.morphAttributes.normal||G.morphAttributes.color,bt=Sn!==void 0?Sn.length:0,He=Ce.get(W),fi=p.state.lights;if(he===!0&&(Ne===!0||A!==w)){const Un=A===w&&W.id===b;ae.setState(W,A,Un)}let St=!1;W.version===He.__version?(He.needsLights&&He.lightsStateVersion!==fi.state.version||He.outputColorSpace!==Fe||U.isBatchedMesh&&He.batching===!1||!U.isBatchedMesh&&He.batching===!0||U.isBatchedMesh&&He.batchingColor===!0&&U.colorTexture===null||U.isBatchedMesh&&He.batchingColor===!1&&U.colorTexture!==null||U.isInstancedMesh&&He.instancing===!1||!U.isInstancedMesh&&He.instancing===!0||U.isSkinnedMesh&&He.skinning===!1||!U.isSkinnedMesh&&He.skinning===!0||U.isInstancedMesh&&He.instancingColor===!0&&U.instanceColor===null||U.isInstancedMesh&&He.instancingColor===!1&&U.instanceColor!==null||U.isInstancedMesh&&He.instancingMorph===!0&&U.morphTexture===null||U.isInstancedMesh&&He.instancingMorph===!1&&U.morphTexture!==null||He.envMap!==Be||W.fog===!0&&He.fog!==ue||He.numClippingPlanes!==void 0&&(He.numClippingPlanes!==ae.numPlanes||He.numIntersection!==ae.numIntersection)||He.vertexAlphas!==Je||He.vertexTangents!==st||He.morphTargets!==ke||He.morphNormals!==_t||He.morphColors!==It||He.toneMapping!==Ut||He.morphTargetsCount!==bt)&&(St=!0):(St=!0,He.__version=W.version);let qn=He.currentProgram;St===!0&&(qn=wo(W,N,U));let Is=!1,Cn=!1,Pr=!1;const Ot=qn.getUniforms(),Qn=He.uniforms;if(ge.useProgram(qn.program)&&(Is=!0,Cn=!0,Pr=!0),W.id!==b&&(b=W.id,Cn=!0),Is||w!==A){ge.buffers.depth.getReversed()?(pe.copy(A.projectionMatrix),Zm(pe),Jm(pe),Ot.setValue(I,"projectionMatrix",pe)):Ot.setValue(I,"projectionMatrix",A.projectionMatrix),Ot.setValue(I,"viewMatrix",A.matrixWorldInverse);const Di=Ot.map.cameraPosition;Di!==void 0&&Di.setValue(I,Ze.setFromMatrixPosition(A.matrixWorld)),Le.logarithmicDepthBuffer&&Ot.setValue(I,"logDepthBufFC",2/(Math.log(A.far+1)/Math.LN2)),(W.isMeshPhongMaterial||W.isMeshToonMaterial||W.isMeshLambertMaterial||W.isMeshBasicMaterial||W.isMeshStandardMaterial||W.isShaderMaterial)&&Ot.setValue(I,"isOrthographic",A.isOrthographicCamera===!0),w!==A&&(w=A,Cn=!0,Pr=!0)}if(U.isSkinnedMesh){Ot.setOptional(I,U,"bindMatrix"),Ot.setOptional(I,U,"bindMatrixInverse");const Un=U.skeleton;Un&&(Un.boneTexture===null&&Un.computeBoneTexture(),Ot.setValue(I,"boneTexture",Un.boneTexture,R))}U.isBatchedMesh&&(Ot.setOptional(I,U,"batchingTexture"),Ot.setValue(I,"batchingTexture",U._matricesTexture,R),Ot.setOptional(I,U,"batchingIdTexture"),Ot.setValue(I,"batchingIdTexture",U._indirectTexture,R),Ot.setOptional(I,U,"batchingColorTexture"),U._colorsTexture!==null&&Ot.setValue(I,"batchingColorTexture",U._colorsTexture,R));const Lr=G.morphAttributes;if((Lr.position!==void 0||Lr.normal!==void 0||Lr.color!==void 0)&&Ye.update(U,G,qn),(Cn||He.receiveShadow!==U.receiveShadow)&&(He.receiveShadow=U.receiveShadow,Ot.setValue(I,"receiveShadow",U.receiveShadow)),W.isMeshGouraudMaterial&&W.envMap!==null&&(Qn.envMap.value=Be,Qn.flipEnvMap.value=Be.isCubeTexture&&Be.isRenderTargetTexture===!1?-1:1),W.isMeshStandardMaterial&&W.envMap===null&&N.environment!==null&&(Qn.envMapIntensity.value=N.environmentIntensity),Cn&&(Ot.setValue(I,"toneMappingExposure",x.toneMappingExposure),He.needsLights&&Ep(Qn,Pr),ue&&W.fog===!0&&ye.refreshFogUniforms(Qn,ue),ye.refreshMaterialUniforms(Qn,W,V,j,p.state.transmissionRenderTarget[A.id]),ga.upload(I,zh(He),Qn,R)),W.isShaderMaterial&&W.uniformsNeedUpdate===!0&&(ga.upload(I,zh(He),Qn,R),W.uniformsNeedUpdate=!1),W.isSpriteMaterial&&Ot.setValue(I,"center",U.center),Ot.setValue(I,"modelViewMatrix",U.modelViewMatrix),Ot.setValue(I,"normalMatrix",U.normalMatrix),Ot.setValue(I,"modelMatrix",U.matrixWorld),W.isShaderMaterial||W.isRawShaderMaterial){const Un=W.uniformsGroups;for(let Di=0,Ni=Un.length;Di<Ni;Di++){const Gh=Un[Di];D.update(Gh,qn),D.bind(Gh,qn)}}return qn}function Ep(A,N){A.ambientLightColor.needsUpdate=N,A.lightProbe.needsUpdate=N,A.directionalLights.needsUpdate=N,A.directionalLightShadows.needsUpdate=N,A.pointLights.needsUpdate=N,A.pointLightShadows.needsUpdate=N,A.spotLights.needsUpdate=N,A.spotLightShadows.needsUpdate=N,A.rectAreaLights.needsUpdate=N,A.hemisphereLights.needsUpdate=N}function Tp(A){return A.isMeshLambertMaterial||A.isMeshToonMaterial||A.isMeshPhongMaterial||A.isMeshStandardMaterial||A.isShadowMaterial||A.isShaderMaterial&&A.lights===!0}this.getActiveCubeFace=function(){return T},this.getActiveMipmapLevel=function(){return P},this.getRenderTarget=function(){return C},this.setRenderTargetTextures=function(A,N,G){Ce.get(A.texture).__webglTexture=N,Ce.get(A.depthTexture).__webglTexture=G;const W=Ce.get(A);W.__hasExternalTextures=!0,W.__autoAllocateDepthBuffer=G===void 0,W.__autoAllocateDepthBuffer||re.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),W.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(A,N){const G=Ce.get(A);G.__webglFramebuffer=N,G.__useDefaultFramebuffer=N===void 0},this.setRenderTarget=function(A,N=0,G=0){C=A,T=N,P=G;let W=!0,U=null,ue=!1,be=!1;if(A){const Be=Ce.get(A);if(Be.__useDefaultFramebuffer!==void 0)ge.bindFramebuffer(I.FRAMEBUFFER,null),W=!1;else if(Be.__webglFramebuffer===void 0)R.setupRenderTarget(A);else if(Be.__hasExternalTextures)R.rebindTextures(A,Ce.get(A.texture).__webglTexture,Ce.get(A.depthTexture).__webglTexture);else if(A.depthBuffer){const ke=A.depthTexture;if(Be.__boundDepthTexture!==ke){if(ke!==null&&Ce.has(ke)&&(A.width!==ke.image.width||A.height!==ke.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");R.setupDepthRenderbuffer(A)}}const Je=A.texture;(Je.isData3DTexture||Je.isDataArrayTexture||Je.isCompressedArrayTexture)&&(be=!0);const st=Ce.get(A).__webglFramebuffer;A.isWebGLCubeRenderTarget?(Array.isArray(st[N])?U=st[N][G]:U=st[N],ue=!0):A.samples>0&&R.useMultisampledRTT(A)===!1?U=Ce.get(A).__webglMultisampledFramebuffer:Array.isArray(st)?U=st[G]:U=st,L.copy(A.viewport),F.copy(A.scissor),O=A.scissorTest}else L.copy(Re).multiplyScalar(V).floor(),F.copy(tt).multiplyScalar(V).floor(),O=wt;if(ge.bindFramebuffer(I.FRAMEBUFFER,U)&&W&&ge.drawBuffers(A,U),ge.viewport(L),ge.scissor(F),ge.setScissorTest(O),ue){const Be=Ce.get(A.texture);I.framebufferTexture2D(I.FRAMEBUFFER,I.COLOR_ATTACHMENT0,I.TEXTURE_CUBE_MAP_POSITIVE_X+N,Be.__webglTexture,G)}else if(be){const Be=Ce.get(A.texture),Je=N||0;I.framebufferTextureLayer(I.FRAMEBUFFER,I.COLOR_ATTACHMENT0,Be.__webglTexture,G||0,Je)}b=-1},this.readRenderTargetPixels=function(A,N,G,W,U,ue,be){if(!(A&&A.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Fe=Ce.get(A).__webglFramebuffer;if(A.isWebGLCubeRenderTarget&&be!==void 0&&(Fe=Fe[be]),Fe){ge.bindFramebuffer(I.FRAMEBUFFER,Fe);try{const Be=A.texture,Je=Be.format,st=Be.type;if(!Le.textureFormatReadable(Je)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!Le.textureTypeReadable(st)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}N>=0&&N<=A.width-W&&G>=0&&G<=A.height-U&&I.readPixels(N,G,W,U,ot.convert(Je),ot.convert(st),ue)}finally{const Be=C!==null?Ce.get(C).__webglFramebuffer:null;ge.bindFramebuffer(I.FRAMEBUFFER,Be)}}},this.readRenderTargetPixelsAsync=async function(A,N,G,W,U,ue,be){if(!(A&&A.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Fe=Ce.get(A).__webglFramebuffer;if(A.isWebGLCubeRenderTarget&&be!==void 0&&(Fe=Fe[be]),Fe){const Be=A.texture,Je=Be.format,st=Be.type;if(!Le.textureFormatReadable(Je))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!Le.textureTypeReadable(st))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(N>=0&&N<=A.width-W&&G>=0&&G<=A.height-U){ge.bindFramebuffer(I.FRAMEBUFFER,Fe);const ke=I.createBuffer();I.bindBuffer(I.PIXEL_PACK_BUFFER,ke),I.bufferData(I.PIXEL_PACK_BUFFER,ue.byteLength,I.STREAM_READ),I.readPixels(N,G,W,U,ot.convert(Je),ot.convert(st),0);const _t=C!==null?Ce.get(C).__webglFramebuffer:null;ge.bindFramebuffer(I.FRAMEBUFFER,_t);const It=I.fenceSync(I.SYNC_GPU_COMMANDS_COMPLETE,0);return I.flush(),await Km(I,It,4),I.bindBuffer(I.PIXEL_PACK_BUFFER,ke),I.getBufferSubData(I.PIXEL_PACK_BUFFER,0,ue),I.deleteBuffer(ke),I.deleteSync(It),ue}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(A,N=null,G=0){A.isTexture!==!0&&(Yr("WebGLRenderer: copyFramebufferToTexture function signature has changed."),N=arguments[0]||null,A=arguments[1]);const W=Math.pow(2,-G),U=Math.floor(A.image.width*W),ue=Math.floor(A.image.height*W),be=N!==null?N.x:0,Fe=N!==null?N.y:0;R.setTexture2D(A,0),I.copyTexSubImage2D(I.TEXTURE_2D,G,0,0,be,Fe,U,ue),ge.unbindTexture()},this.copyTextureToTexture=function(A,N,G=null,W=null,U=0){A.isTexture!==!0&&(Yr("WebGLRenderer: copyTextureToTexture function signature has changed."),W=arguments[0]||null,A=arguments[1],N=arguments[2],U=arguments[3]||0,G=null);let ue,be,Fe,Be,Je,st,ke,_t,It;const Ut=A.isCompressedTexture?A.mipmaps[U]:A.image;G!==null?(ue=G.max.x-G.min.x,be=G.max.y-G.min.y,Fe=G.isBox3?G.max.z-G.min.z:1,Be=G.min.x,Je=G.min.y,st=G.isBox3?G.min.z:0):(ue=Ut.width,be=Ut.height,Fe=Ut.depth||1,Be=0,Je=0,st=0),W!==null?(ke=W.x,_t=W.y,It=W.z):(ke=0,_t=0,It=0);const Sn=ot.convert(N.format),bt=ot.convert(N.type);let He;N.isData3DTexture?(R.setTexture3D(N,0),He=I.TEXTURE_3D):N.isDataArrayTexture||N.isCompressedArrayTexture?(R.setTexture2DArray(N,0),He=I.TEXTURE_2D_ARRAY):(R.setTexture2D(N,0),He=I.TEXTURE_2D),I.pixelStorei(I.UNPACK_FLIP_Y_WEBGL,N.flipY),I.pixelStorei(I.UNPACK_PREMULTIPLY_ALPHA_WEBGL,N.premultiplyAlpha),I.pixelStorei(I.UNPACK_ALIGNMENT,N.unpackAlignment);const fi=I.getParameter(I.UNPACK_ROW_LENGTH),St=I.getParameter(I.UNPACK_IMAGE_HEIGHT),qn=I.getParameter(I.UNPACK_SKIP_PIXELS),Is=I.getParameter(I.UNPACK_SKIP_ROWS),Cn=I.getParameter(I.UNPACK_SKIP_IMAGES);I.pixelStorei(I.UNPACK_ROW_LENGTH,Ut.width),I.pixelStorei(I.UNPACK_IMAGE_HEIGHT,Ut.height),I.pixelStorei(I.UNPACK_SKIP_PIXELS,Be),I.pixelStorei(I.UNPACK_SKIP_ROWS,Je),I.pixelStorei(I.UNPACK_SKIP_IMAGES,st);const Pr=A.isDataArrayTexture||A.isData3DTexture,Ot=N.isDataArrayTexture||N.isData3DTexture;if(A.isRenderTargetTexture||A.isDepthTexture){const Qn=Ce.get(A),Lr=Ce.get(N),Un=Ce.get(Qn.__renderTarget),Di=Ce.get(Lr.__renderTarget);ge.bindFramebuffer(I.READ_FRAMEBUFFER,Un.__webglFramebuffer),ge.bindFramebuffer(I.DRAW_FRAMEBUFFER,Di.__webglFramebuffer);for(let Ni=0;Ni<Fe;Ni++)Pr&&I.framebufferTextureLayer(I.READ_FRAMEBUFFER,I.COLOR_ATTACHMENT0,Ce.get(A).__webglTexture,U,st+Ni),A.isDepthTexture?(Ot&&I.framebufferTextureLayer(I.DRAW_FRAMEBUFFER,I.COLOR_ATTACHMENT0,Ce.get(N).__webglTexture,U,It+Ni),I.blitFramebuffer(Be,Je,ue,be,ke,_t,ue,be,I.DEPTH_BUFFER_BIT,I.NEAREST)):Ot?I.copyTexSubImage3D(He,U,ke,_t,It+Ni,Be,Je,ue,be):I.copyTexSubImage2D(He,U,ke,_t,It+Ni,Be,Je,ue,be);ge.bindFramebuffer(I.READ_FRAMEBUFFER,null),ge.bindFramebuffer(I.DRAW_FRAMEBUFFER,null)}else Ot?A.isDataTexture||A.isData3DTexture?I.texSubImage3D(He,U,ke,_t,It,ue,be,Fe,Sn,bt,Ut.data):N.isCompressedArrayTexture?I.compressedTexSubImage3D(He,U,ke,_t,It,ue,be,Fe,Sn,Ut.data):I.texSubImage3D(He,U,ke,_t,It,ue,be,Fe,Sn,bt,Ut):A.isDataTexture?I.texSubImage2D(I.TEXTURE_2D,U,ke,_t,ue,be,Sn,bt,Ut.data):A.isCompressedTexture?I.compressedTexSubImage2D(I.TEXTURE_2D,U,ke,_t,Ut.width,Ut.height,Sn,Ut.data):I.texSubImage2D(I.TEXTURE_2D,U,ke,_t,ue,be,Sn,bt,Ut);I.pixelStorei(I.UNPACK_ROW_LENGTH,fi),I.pixelStorei(I.UNPACK_IMAGE_HEIGHT,St),I.pixelStorei(I.UNPACK_SKIP_PIXELS,qn),I.pixelStorei(I.UNPACK_SKIP_ROWS,Is),I.pixelStorei(I.UNPACK_SKIP_IMAGES,Cn),U===0&&N.generateMipmaps&&I.generateMipmap(He),ge.unbindTexture()},this.copyTextureToTexture3D=function(A,N,G=null,W=null,U=0){return A.isTexture!==!0&&(Yr("WebGLRenderer: copyTextureToTexture3D function signature has changed."),G=arguments[0]||null,W=arguments[1]||null,A=arguments[2],N=arguments[3],U=arguments[4]||0),Yr('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(A,N,G,W,U)},this.initRenderTarget=function(A){Ce.get(A).__webglFramebuffer===void 0&&R.setupRenderTarget(A)},this.initTexture=function(A){A.isCubeTexture?R.setTextureCube(A,0):A.isData3DTexture?R.setTexture3D(A,0):A.isDataArrayTexture||A.isCompressedArrayTexture?R.setTexture2DArray(A,0):R.setTexture2D(A,0),ge.unbindTexture()},this.resetState=function(){T=0,P=0,C=null,ge.reset(),Lt.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Si}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorspace=ft._getDrawingBufferColorSpace(e),t.unpackColorSpace=ft._getUnpackColorSpace()}}class Ba extends Nt{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new wn,this.environmentIntensity=1,this.environmentRotation=new wn,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class cy{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=kl,this.updateRanges=[],this.version=0,this.uuid=zn()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let s=0,r=this.stride;s<r;s++)this.array[e+s]=t.array[n+s];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=zn()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=zn()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const gn=new v;class dh{constructor(e,t,n,s=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=s}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)gn.fromBufferAttribute(this,t),gn.applyMatrix4(e),this.setXYZ(t,gn.x,gn.y,gn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)gn.fromBufferAttribute(this,t),gn.applyNormalMatrix(e),this.setXYZ(t,gn.x,gn.y,gn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)gn.fromBufferAttribute(this,t),gn.transformDirection(e),this.setXYZ(t,gn.x,gn.y,gn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=Zn(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Tt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=Tt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=Zn(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=Zn(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=Zn(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=Zn(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),s=Tt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=Tt(t,this.array),n=Tt(n,this.array),s=Tt(s,this.array),r=Tt(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this.data.array[e+3]=r,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return new en(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new dh(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}const Xu=new v,qu=new yt,ju=new yt,ly=new v,$u=new Ae,Vo=new v,Rc=new ci,Yu=new Ae,Cc=new Ua;class fh extends Xt{constructor(e,t){super(e,t),this.isSkinnedMesh=!0,this.type="SkinnedMesh",this.bindMode=jh,this.bindMatrix=new Ae,this.bindMatrixInverse=new Ae,this.boundingBox=null,this.boundingSphere=null}computeBoundingBox(){const e=this.geometry;this.boundingBox===null&&(this.boundingBox=new tn),this.boundingBox.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,Vo),this.boundingBox.expandByPoint(Vo)}computeBoundingSphere(){const e=this.geometry;this.boundingSphere===null&&(this.boundingSphere=new ci),this.boundingSphere.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,Vo),this.boundingSphere.expandByPoint(Vo)}copy(e,t){return super.copy(e,t),this.bindMode=e.bindMode,this.bindMatrix.copy(e.bindMatrix),this.bindMatrixInverse.copy(e.bindMatrixInverse),this.skeleton=e.skeleton,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}raycast(e,t){const n=this.material,s=this.matrixWorld;n!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Rc.copy(this.boundingSphere),Rc.applyMatrix4(s),e.ray.intersectsSphere(Rc)!==!1&&(Yu.copy(s).invert(),Cc.copy(e.ray).applyMatrix4(Yu),!(this.boundingBox!==null&&Cc.intersectsBox(this.boundingBox)===!1)&&this._computeIntersections(e,t,Cc)))}getVertexPosition(e,t){return super.getVertexPosition(e,t),this.applyBoneTransform(e,t),t}bind(e,t){this.skeleton=e,t===void 0&&(this.updateMatrixWorld(!0),this.skeleton.calculateInverses(),t=this.matrixWorld),this.bindMatrix.copy(t),this.bindMatrixInverse.copy(t).invert()}pose(){this.skeleton.pose()}normalizeSkinWeights(){const e=new yt,t=this.geometry.attributes.skinWeight;for(let n=0,s=t.count;n<s;n++){e.fromBufferAttribute(t,n);const r=1/e.manhattanLength();r!==1/0?e.multiplyScalar(r):e.set(1,0,0,0),t.setXYZW(n,e.x,e.y,e.z,e.w)}}updateMatrixWorld(e){super.updateMatrixWorld(e),this.bindMode===jh?this.bindMatrixInverse.copy(this.matrixWorld).invert():this.bindMode===ym?this.bindMatrixInverse.copy(this.bindMatrix).invert():console.warn("THREE.SkinnedMesh: Unrecognized bindMode: "+this.bindMode)}applyBoneTransform(e,t){const n=this.skeleton,s=this.geometry;qu.fromBufferAttribute(s.attributes.skinIndex,e),ju.fromBufferAttribute(s.attributes.skinWeight,e),Xu.copy(t).applyMatrix4(this.bindMatrix),t.set(0,0,0);for(let r=0;r<4;r++){const o=ju.getComponent(r);if(o!==0){const a=qu.getComponent(r);$u.multiplyMatrices(n.bones[a].matrixWorld,n.boneInverses[a]),t.addScaledVector(ly.copy(Xu).applyMatrix4($u),o)}}return t.applyMatrix4(this.bindMatrixInverse)}}class Mf extends Nt{constructor(){super(),this.isBone=!0,this.type="Bone"}}class ph extends Qt{constructor(e=null,t=1,n=1,s,r,o,a,c,l=pn,h=pn,u,d){super(null,o,a,c,l,h,s,r,u,d),this.isDataTexture=!0,this.image={data:e,width:t,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const Ku=new Ae,hy=new Ae;class mh{constructor(e=[],t=[]){this.uuid=zn(),this.bones=e.slice(0),this.boneInverses=t,this.boneMatrices=null,this.boneTexture=null,this.init()}init(){const e=this.bones,t=this.boneInverses;if(this.boneMatrices=new Float32Array(e.length*16),t.length===0)this.calculateInverses();else if(e.length!==t.length){console.warn("THREE.Skeleton: Number of inverse bone matrices does not match amount of bones."),this.boneInverses=[];for(let n=0,s=this.bones.length;n<s;n++)this.boneInverses.push(new Ae)}}calculateInverses(){this.boneInverses.length=0;for(let e=0,t=this.bones.length;e<t;e++){const n=new Ae;this.bones[e]&&n.copy(this.bones[e].matrixWorld).invert(),this.boneInverses.push(n)}}pose(){for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&n.matrixWorld.copy(this.boneInverses[e]).invert()}for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&(n.parent&&n.parent.isBone?(n.matrix.copy(n.parent.matrixWorld).invert(),n.matrix.multiply(n.matrixWorld)):n.matrix.copy(n.matrixWorld),n.matrix.decompose(n.position,n.quaternion,n.scale))}}update(){const e=this.bones,t=this.boneInverses,n=this.boneMatrices,s=this.boneTexture;for(let r=0,o=e.length;r<o;r++){const a=e[r]?e[r].matrixWorld:hy;Ku.multiplyMatrices(a,t[r]),Ku.toArray(n,r*16)}s!==null&&(s.needsUpdate=!0)}clone(){return new mh(this.bones,this.boneInverses)}computeBoneTexture(){let e=Math.sqrt(this.bones.length*4);e=Math.ceil(e/4)*4,e=Math.max(e,4);const t=new Float32Array(e*e*4);t.set(this.boneMatrices);const n=new ph(t,e,e,kn,Jn);return n.needsUpdate=!0,this.boneMatrices=t,this.boneTexture=n,this}getBoneByName(e){for(let t=0,n=this.bones.length;t<n;t++){const s=this.bones[t];if(s.name===e)return s}}dispose(){this.boneTexture!==null&&(this.boneTexture.dispose(),this.boneTexture=null)}fromJSON(e,t){this.uuid=e.uuid;for(let n=0,s=e.bones.length;n<s;n++){const r=e.bones[n];let o=t[r];o===void 0&&(console.warn("THREE.Skeleton: No bone found with UUID:",r),o=new Mf),this.bones.push(o),this.boneInverses.push(new Ae().fromArray(e.boneInverses[n]))}return this.init(),this}toJSON(){const e={metadata:{version:4.6,type:"Skeleton",generator:"Skeleton.toJSON"},bones:[],boneInverses:[]};e.uuid=this.uuid;const t=this.bones,n=this.boneInverses;for(let s=0,r=t.length;s<r;s++){const o=t[s];e.bones.push(o.uuid);const a=n[s];e.boneInverses.push(a.toArray())}return e}}class Hl extends en{constructor(e,t,n,s=1){super(e,t,n),this.isInstancedBufferAttribute=!0,this.meshPerAttribute=s}copy(e){return super.copy(e),this.meshPerAttribute=e.meshPerAttribute,this}toJSON(){const e=super.toJSON();return e.meshPerAttribute=this.meshPerAttribute,e.isInstancedBufferAttribute=!0,e}}const js=new Ae,Zu=new Ae,Wo=[],Ju=new tn,uy=new Ae,Or=new Xt,Fr=new ci;class dy extends Xt{constructor(e,t,n){super(e,t),this.isInstancedMesh=!0,this.instanceMatrix=new Hl(new Float32Array(n*16),16),this.instanceColor=null,this.morphTexture=null,this.count=n,this.boundingBox=null,this.boundingSphere=null;for(let s=0;s<n;s++)this.setMatrixAt(s,uy)}computeBoundingBox(){const e=this.geometry,t=this.count;this.boundingBox===null&&(this.boundingBox=new tn),e.boundingBox===null&&e.computeBoundingBox(),this.boundingBox.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,js),Ju.copy(e.boundingBox).applyMatrix4(js),this.boundingBox.union(Ju)}computeBoundingSphere(){const e=this.geometry,t=this.count;this.boundingSphere===null&&(this.boundingSphere=new ci),e.boundingSphere===null&&e.computeBoundingSphere(),this.boundingSphere.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,js),Fr.copy(e.boundingSphere).applyMatrix4(js),this.boundingSphere.union(Fr)}copy(e,t){return super.copy(e,t),this.instanceMatrix.copy(e.instanceMatrix),e.morphTexture!==null&&(this.morphTexture=e.morphTexture.clone()),e.instanceColor!==null&&(this.instanceColor=e.instanceColor.clone()),this.count=e.count,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}getColorAt(e,t){t.fromArray(this.instanceColor.array,e*3)}getMatrixAt(e,t){t.fromArray(this.instanceMatrix.array,e*16)}getMorphAt(e,t){const n=t.morphTargetInfluences,s=this.morphTexture.source.data.data,r=n.length+1,o=e*r+1;for(let a=0;a<n.length;a++)n[a]=s[o+a]}raycast(e,t){const n=this.matrixWorld,s=this.count;if(Or.geometry=this.geometry,Or.material=this.material,Or.material!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Fr.copy(this.boundingSphere),Fr.applyMatrix4(n),e.ray.intersectsSphere(Fr)!==!1))for(let r=0;r<s;r++){this.getMatrixAt(r,js),Zu.multiplyMatrices(n,js),Or.matrixWorld=Zu,Or.raycast(e,Wo);for(let o=0,a=Wo.length;o<a;o++){const c=Wo[o];c.instanceId=r,c.object=this,t.push(c)}Wo.length=0}}setColorAt(e,t){this.instanceColor===null&&(this.instanceColor=new Hl(new Float32Array(this.instanceMatrix.count*3).fill(1),3)),t.toArray(this.instanceColor.array,e*3)}setMatrixAt(e,t){t.toArray(this.instanceMatrix.array,e*16)}setMorphAt(e,t){const n=t.morphTargetInfluences,s=n.length+1;this.morphTexture===null&&(this.morphTexture=new ph(new Float32Array(s*this.count),s,this.count,sh,Jn));const r=this.morphTexture.source.data.data;let o=0;for(let l=0;l<n.length;l++)o+=n[l];const a=this.geometry.morphTargetsRelative?1:1-o,c=s*e;r[c]=a,r.set(n,c+1)}updateMorphTargets(){}dispose(){return this.dispatchEvent({type:"dispose"}),this.morphTexture!==null&&(this.morphTexture.dispose(),this.morphTexture=null),this}}class As extends ri{static get type(){return"LineBasicMaterial"}constructor(e){super(),this.isLineBasicMaterial=!0,this.color=new Ve(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const ba=new v,Sa=new v,Qu=new Ae,Br=new Ua,Xo=new ci,Pc=new v,ed=new v;class gh extends Nt{constructor(e=new Gt,t=new As){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let s=1,r=t.count;s<r;s++)ba.fromBufferAttribute(t,s-1),Sa.fromBufferAttribute(t,s),n[s]=n[s-1],n[s]+=ba.distanceTo(Sa);e.setAttribute("lineDistance",new ct(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Line.threshold,o=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Xo.copy(n.boundingSphere),Xo.applyMatrix4(s),Xo.radius+=r,e.ray.intersectsSphere(Xo)===!1)return;Qu.copy(s).invert(),Br.copy(e.ray).applyMatrix4(Qu);const a=r/((this.scale.x+this.scale.y+this.scale.z)/3),c=a*a,l=this.isLineSegments?2:1,h=n.index,d=n.attributes.position;if(h!==null){const f=Math.max(0,o.start),m=Math.min(h.count,o.start+o.count);for(let _=f,g=m-1;_<g;_+=l){const p=h.getX(_),y=h.getX(_+1),M=qo(this,e,Br,c,p,y);M&&t.push(M)}if(this.isLineLoop){const _=h.getX(m-1),g=h.getX(f),p=qo(this,e,Br,c,_,g);p&&t.push(p)}}else{const f=Math.max(0,o.start),m=Math.min(d.count,o.start+o.count);for(let _=f,g=m-1;_<g;_+=l){const p=qo(this,e,Br,c,_,_+1);p&&t.push(p)}if(this.isLineLoop){const _=qo(this,e,Br,c,m-1,f);_&&t.push(_)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}}function qo(i,e,t,n,s,r){const o=i.geometry.attributes.position;if(ba.fromBufferAttribute(o,s),Sa.fromBufferAttribute(o,r),t.distanceSqToSegment(ba,Sa,Pc,ed)>n)return;Pc.applyMatrix4(i.matrixWorld);const c=e.ray.origin.distanceTo(Pc);if(!(c<e.near||c>e.far))return{distance:c,point:ed.clone().applyMatrix4(i.matrixWorld),index:s,face:null,faceIndex:null,barycoord:null,object:i}}const td=new v,nd=new v;class fo extends gh{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let s=0,r=t.count;s<r;s+=2)td.fromBufferAttribute(t,s),nd.fromBufferAttribute(t,s+1),n[s]=s===0?0:n[s-1],n[s+1]=n[s]+td.distanceTo(nd);e.setAttribute("lineDistance",new ct(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class wf extends gh{constructor(e,t){super(e,t),this.isLineLoop=!0,this.type="LineLoop"}}class bf extends ri{static get type(){return"PointsMaterial"}constructor(e){super(),this.isPointsMaterial=!0,this.color=new Ve(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const id=new Ae,Gl=new Ua,jo=new ci,$o=new v;class fy extends Nt{constructor(e=new Gt,t=new bf){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Points.threshold,o=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),jo.copy(n.boundingSphere),jo.applyMatrix4(s),jo.radius+=r,e.ray.intersectsSphere(jo)===!1)return;id.copy(s).invert(),Gl.copy(e.ray).applyMatrix4(id);const a=r/((this.scale.x+this.scale.y+this.scale.z)/3),c=a*a,l=n.index,u=n.attributes.position;if(l!==null){const d=Math.max(0,o.start),f=Math.min(l.count,o.start+o.count);for(let m=d,_=f;m<_;m++){const g=l.getX(m);$o.fromBufferAttribute(u,g),sd($o,g,c,s,e,t,this)}}else{const d=Math.max(0,o.start),f=Math.min(u.count,o.start+o.count);for(let m=d,_=f;m<_;m++)$o.fromBufferAttribute(u,m),sd($o,m,c,s,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}}function sd(i,e,t,n,s,r,o){const a=Gl.distanceSqToPoint(i);if(a<t){const c=new v;Gl.closestPointToPoint(i,c),c.applyMatrix4(n);const l=s.ray.origin.distanceTo(c);if(l<s.near||l>s.far)return;r.push({distance:l,distanceToRay:Math.sqrt(a),point:c,index:e,face:null,faceIndex:null,barycoord:null,object:o})}}class li{constructor(){this.type="Curve",this.arcLengthDivisions=200}getPoint(){return console.warn("THREE.Curve: .getPoint() not implemented."),null}getPointAt(e,t){const n=this.getUtoTmapping(e);return this.getPoint(n,t)}getPoints(e=5){const t=[];for(let n=0;n<=e;n++)t.push(this.getPoint(n/e));return t}getSpacedPoints(e=5){const t=[];for(let n=0;n<=e;n++)t.push(this.getPointAt(n/e));return t}getLength(){const e=this.getLengths();return e[e.length-1]}getLengths(e=this.arcLengthDivisions){if(this.cacheArcLengths&&this.cacheArcLengths.length===e+1&&!this.needsUpdate)return this.cacheArcLengths;this.needsUpdate=!1;const t=[];let n,s=this.getPoint(0),r=0;t.push(0);for(let o=1;o<=e;o++)n=this.getPoint(o/e),r+=n.distanceTo(s),t.push(r),s=n;return this.cacheArcLengths=t,t}updateArcLengths(){this.needsUpdate=!0,this.getLengths()}getUtoTmapping(e,t){const n=this.getLengths();let s=0;const r=n.length;let o;t?o=t:o=e*n[r-1];let a=0,c=r-1,l;for(;a<=c;)if(s=Math.floor(a+(c-a)/2),l=n[s]-o,l<0)a=s+1;else if(l>0)c=s-1;else{c=s;break}if(s=c,n[s]===o)return s/(r-1);const h=n[s],d=n[s+1]-h,f=(o-h)/d;return(s+f)/(r-1)}getTangent(e,t){let s=e-1e-4,r=e+1e-4;s<0&&(s=0),r>1&&(r=1);const o=this.getPoint(s),a=this.getPoint(r),c=t||(o.isVector2?new te:new v);return c.copy(a).sub(o).normalize(),c}getTangentAt(e,t){const n=this.getUtoTmapping(e);return this.getTangent(n,t)}computeFrenetFrames(e,t){const n=new v,s=[],r=[],o=[],a=new v,c=new Ae;for(let f=0;f<=e;f++){const m=f/e;s[f]=this.getTangentAt(m,new v)}r[0]=new v,o[0]=new v;let l=Number.MAX_VALUE;const h=Math.abs(s[0].x),u=Math.abs(s[0].y),d=Math.abs(s[0].z);h<=l&&(l=h,n.set(1,0,0)),u<=l&&(l=u,n.set(0,1,0)),d<=l&&n.set(0,0,1),a.crossVectors(s[0],n).normalize(),r[0].crossVectors(s[0],a),o[0].crossVectors(s[0],r[0]);for(let f=1;f<=e;f++){if(r[f]=r[f-1].clone(),o[f]=o[f-1].clone(),a.crossVectors(s[f-1],s[f]),a.length()>Number.EPSILON){a.normalize();const m=Math.acos(Yt(s[f-1].dot(s[f]),-1,1));r[f].applyMatrix4(c.makeRotationAxis(a,m))}o[f].crossVectors(s[f],r[f])}if(t===!0){let f=Math.acos(Yt(r[0].dot(r[e]),-1,1));f/=e,s[0].dot(a.crossVectors(r[0],r[e]))>0&&(f=-f);for(let m=1;m<=e;m++)r[m].applyMatrix4(c.makeRotationAxis(s[m],f*m)),o[m].crossVectors(s[m],r[m])}return{tangents:s,normals:r,binormals:o}}clone(){return new this.constructor().copy(this)}copy(e){return this.arcLengthDivisions=e.arcLengthDivisions,this}toJSON(){const e={metadata:{version:4.6,type:"Curve",generator:"Curve.toJSON"}};return e.arcLengthDivisions=this.arcLengthDivisions,e.type=this.type,e}fromJSON(e){return this.arcLengthDivisions=e.arcLengthDivisions,this}}class _h extends li{constructor(e=0,t=0,n=1,s=1,r=0,o=Math.PI*2,a=!1,c=0){super(),this.isEllipseCurve=!0,this.type="EllipseCurve",this.aX=e,this.aY=t,this.xRadius=n,this.yRadius=s,this.aStartAngle=r,this.aEndAngle=o,this.aClockwise=a,this.aRotation=c}getPoint(e,t=new te){const n=t,s=Math.PI*2;let r=this.aEndAngle-this.aStartAngle;const o=Math.abs(r)<Number.EPSILON;for(;r<0;)r+=s;for(;r>s;)r-=s;r<Number.EPSILON&&(o?r=0:r=s),this.aClockwise===!0&&!o&&(r===s?r=-s:r=r-s);const a=this.aStartAngle+e*r;let c=this.aX+this.xRadius*Math.cos(a),l=this.aY+this.yRadius*Math.sin(a);if(this.aRotation!==0){const h=Math.cos(this.aRotation),u=Math.sin(this.aRotation),d=c-this.aX,f=l-this.aY;c=d*h-f*u+this.aX,l=d*u+f*h+this.aY}return n.set(c,l)}copy(e){return super.copy(e),this.aX=e.aX,this.aY=e.aY,this.xRadius=e.xRadius,this.yRadius=e.yRadius,this.aStartAngle=e.aStartAngle,this.aEndAngle=e.aEndAngle,this.aClockwise=e.aClockwise,this.aRotation=e.aRotation,this}toJSON(){const e=super.toJSON();return e.aX=this.aX,e.aY=this.aY,e.xRadius=this.xRadius,e.yRadius=this.yRadius,e.aStartAngle=this.aStartAngle,e.aEndAngle=this.aEndAngle,e.aClockwise=this.aClockwise,e.aRotation=this.aRotation,e}fromJSON(e){return super.fromJSON(e),this.aX=e.aX,this.aY=e.aY,this.xRadius=e.xRadius,this.yRadius=e.yRadius,this.aStartAngle=e.aStartAngle,this.aEndAngle=e.aEndAngle,this.aClockwise=e.aClockwise,this.aRotation=e.aRotation,this}}class py extends _h{constructor(e,t,n,s,r,o){super(e,t,n,n,s,r,o),this.isArcCurve=!0,this.type="ArcCurve"}}function xh(){let i=0,e=0,t=0,n=0;function s(r,o,a,c){i=r,e=a,t=-3*r+3*o-2*a-c,n=2*r-2*o+a+c}return{initCatmullRom:function(r,o,a,c,l){s(o,a,l*(a-r),l*(c-o))},initNonuniformCatmullRom:function(r,o,a,c,l,h,u){let d=(o-r)/l-(a-r)/(l+h)+(a-o)/h,f=(a-o)/h-(c-o)/(h+u)+(c-a)/u;d*=h,f*=h,s(o,a,d,f)},calc:function(r){const o=r*r,a=o*r;return i+e*r+t*o+n*a}}}const Yo=new v,Lc=new xh,Ic=new xh,Dc=new xh;class ka extends li{constructor(e=[],t=!1,n="centripetal",s=.5){super(),this.isCatmullRomCurve3=!0,this.type="CatmullRomCurve3",this.points=e,this.closed=t,this.curveType=n,this.tension=s}getPoint(e,t=new v){const n=t,s=this.points,r=s.length,o=(r-(this.closed?0:1))*e;let a=Math.floor(o),c=o-a;this.closed?a+=a>0?0:(Math.floor(Math.abs(a)/r)+1)*r:c===0&&a===r-1&&(a=r-2,c=1);let l,h;this.closed||a>0?l=s[(a-1)%r]:(Yo.subVectors(s[0],s[1]).add(s[0]),l=Yo);const u=s[a%r],d=s[(a+1)%r];if(this.closed||a+2<r?h=s[(a+2)%r]:(Yo.subVectors(s[r-1],s[r-2]).add(s[r-1]),h=Yo),this.curveType==="centripetal"||this.curveType==="chordal"){const f=this.curveType==="chordal"?.5:.25;let m=Math.pow(l.distanceToSquared(u),f),_=Math.pow(u.distanceToSquared(d),f),g=Math.pow(d.distanceToSquared(h),f);_<1e-4&&(_=1),m<1e-4&&(m=_),g<1e-4&&(g=_),Lc.initNonuniformCatmullRom(l.x,u.x,d.x,h.x,m,_,g),Ic.initNonuniformCatmullRom(l.y,u.y,d.y,h.y,m,_,g),Dc.initNonuniformCatmullRom(l.z,u.z,d.z,h.z,m,_,g)}else this.curveType==="catmullrom"&&(Lc.initCatmullRom(l.x,u.x,d.x,h.x,this.tension),Ic.initCatmullRom(l.y,u.y,d.y,h.y,this.tension),Dc.initCatmullRom(l.z,u.z,d.z,h.z,this.tension));return n.set(Lc.calc(c),Ic.calc(c),Dc.calc(c)),n}copy(e){super.copy(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(s.clone())}return this.closed=e.closed,this.curveType=e.curveType,this.tension=e.tension,this}toJSON(){const e=super.toJSON();e.points=[];for(let t=0,n=this.points.length;t<n;t++){const s=this.points[t];e.points.push(s.toArray())}return e.closed=this.closed,e.curveType=this.curveType,e.tension=this.tension,e}fromJSON(e){super.fromJSON(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(new v().fromArray(s))}return this.closed=e.closed,this.curveType=e.curveType,this.tension=e.tension,this}}function rd(i,e,t,n,s){const r=(n-e)*.5,o=(s-t)*.5,a=i*i,c=i*a;return(2*t-2*n+r+o)*c+(-3*t+3*n-2*r-o)*a+r*i+t}function my(i,e){const t=1-i;return t*t*e}function gy(i,e){return 2*(1-i)*i*e}function _y(i,e){return i*i*e}function Jr(i,e,t,n){return my(i,e)+gy(i,t)+_y(i,n)}function xy(i,e){const t=1-i;return t*t*t*e}function vy(i,e){const t=1-i;return 3*t*t*i*e}function yy(i,e){return 3*(1-i)*i*i*e}function My(i,e){return i*i*i*e}function Qr(i,e,t,n,s){return xy(i,e)+vy(i,t)+yy(i,n)+My(i,s)}class Sf extends li{constructor(e=new te,t=new te,n=new te,s=new te){super(),this.isCubicBezierCurve=!0,this.type="CubicBezierCurve",this.v0=e,this.v1=t,this.v2=n,this.v3=s}getPoint(e,t=new te){const n=t,s=this.v0,r=this.v1,o=this.v2,a=this.v3;return n.set(Qr(e,s.x,r.x,o.x,a.x),Qr(e,s.y,r.y,o.y,a.y)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this.v3.copy(e.v3),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e.v3=this.v3.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this.v3.fromArray(e.v3),this}}class wy extends li{constructor(e=new v,t=new v,n=new v,s=new v){super(),this.isCubicBezierCurve3=!0,this.type="CubicBezierCurve3",this.v0=e,this.v1=t,this.v2=n,this.v3=s}getPoint(e,t=new v){const n=t,s=this.v0,r=this.v1,o=this.v2,a=this.v3;return n.set(Qr(e,s.x,r.x,o.x,a.x),Qr(e,s.y,r.y,o.y,a.y),Qr(e,s.z,r.z,o.z,a.z)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this.v3.copy(e.v3),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e.v3=this.v3.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this.v3.fromArray(e.v3),this}}class Ef extends li{constructor(e=new te,t=new te){super(),this.isLineCurve=!0,this.type="LineCurve",this.v1=e,this.v2=t}getPoint(e,t=new te){const n=t;return e===1?n.copy(this.v2):(n.copy(this.v2).sub(this.v1),n.multiplyScalar(e).add(this.v1)),n}getPointAt(e,t){return this.getPoint(e,t)}getTangent(e,t=new te){return t.subVectors(this.v2,this.v1).normalize()}getTangentAt(e,t){return this.getTangent(e,t)}copy(e){return super.copy(e),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class Tf extends li{constructor(e=new v,t=new v){super(),this.isLineCurve3=!0,this.type="LineCurve3",this.v1=e,this.v2=t}getPoint(e,t=new v){const n=t;return e===1?n.copy(this.v2):(n.copy(this.v2).sub(this.v1),n.multiplyScalar(e).add(this.v1)),n}getPointAt(e,t){return this.getPoint(e,t)}getTangent(e,t=new v){return t.subVectors(this.v2,this.v1).normalize()}getTangentAt(e,t){return this.getTangent(e,t)}copy(e){return super.copy(e),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class Af extends li{constructor(e=new te,t=new te,n=new te){super(),this.isQuadraticBezierCurve=!0,this.type="QuadraticBezierCurve",this.v0=e,this.v1=t,this.v2=n}getPoint(e,t=new te){const n=t,s=this.v0,r=this.v1,o=this.v2;return n.set(Jr(e,s.x,r.x,o.x),Jr(e,s.y,r.y,o.y)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class vh extends li{constructor(e=new v,t=new v,n=new v){super(),this.isQuadraticBezierCurve3=!0,this.type="QuadraticBezierCurve3",this.v0=e,this.v1=t,this.v2=n}getPoint(e,t=new v){const n=t,s=this.v0,r=this.v1,o=this.v2;return n.set(Jr(e,s.x,r.x,o.x),Jr(e,s.y,r.y,o.y),Jr(e,s.z,r.z,o.z)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class Rf extends li{constructor(e=[]){super(),this.isSplineCurve=!0,this.type="SplineCurve",this.points=e}getPoint(e,t=new te){const n=t,s=this.points,r=(s.length-1)*e,o=Math.floor(r),a=r-o,c=s[o===0?o:o-1],l=s[o],h=s[o>s.length-2?s.length-1:o+1],u=s[o>s.length-3?s.length-1:o+2];return n.set(rd(a,c.x,l.x,h.x,u.x),rd(a,c.y,l.y,h.y,u.y)),n}copy(e){super.copy(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(s.clone())}return this}toJSON(){const e=super.toJSON();e.points=[];for(let t=0,n=this.points.length;t<n;t++){const s=this.points[t];e.points.push(s.toArray())}return e}fromJSON(e){super.fromJSON(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(new te().fromArray(s))}return this}}var Ea=Object.freeze({__proto__:null,ArcCurve:py,CatmullRomCurve3:ka,CubicBezierCurve:Sf,CubicBezierCurve3:wy,EllipseCurve:_h,LineCurve:Ef,LineCurve3:Tf,QuadraticBezierCurve:Af,QuadraticBezierCurve3:vh,SplineCurve:Rf});class by extends li{constructor(){super(),this.type="CurvePath",this.curves=[],this.autoClose=!1}add(e){this.curves.push(e)}closePath(){const e=this.curves[0].getPoint(0),t=this.curves[this.curves.length-1].getPoint(1);if(!e.equals(t)){const n=e.isVector2===!0?"LineCurve":"LineCurve3";this.curves.push(new Ea[n](t,e))}return this}getPoint(e,t){const n=e*this.getLength(),s=this.getCurveLengths();let r=0;for(;r<s.length;){if(s[r]>=n){const o=s[r]-n,a=this.curves[r],c=a.getLength(),l=c===0?0:1-o/c;return a.getPointAt(l,t)}r++}return null}getLength(){const e=this.getCurveLengths();return e[e.length-1]}updateArcLengths(){this.needsUpdate=!0,this.cacheLengths=null,this.getCurveLengths()}getCurveLengths(){if(this.cacheLengths&&this.cacheLengths.length===this.curves.length)return this.cacheLengths;const e=[];let t=0;for(let n=0,s=this.curves.length;n<s;n++)t+=this.curves[n].getLength(),e.push(t);return this.cacheLengths=e,e}getSpacedPoints(e=40){const t=[];for(let n=0;n<=e;n++)t.push(this.getPoint(n/e));return this.autoClose&&t.push(t[0]),t}getPoints(e=12){const t=[];let n;for(let s=0,r=this.curves;s<r.length;s++){const o=r[s],a=o.isEllipseCurve?e*2:o.isLineCurve||o.isLineCurve3?1:o.isSplineCurve?e*o.points.length:e,c=o.getPoints(a);for(let l=0;l<c.length;l++){const h=c[l];n&&n.equals(h)||(t.push(h),n=h)}}return this.autoClose&&t.length>1&&!t[t.length-1].equals(t[0])&&t.push(t[0]),t}copy(e){super.copy(e),this.curves=[];for(let t=0,n=e.curves.length;t<n;t++){const s=e.curves[t];this.curves.push(s.clone())}return this.autoClose=e.autoClose,this}toJSON(){const e=super.toJSON();e.autoClose=this.autoClose,e.curves=[];for(let t=0,n=this.curves.length;t<n;t++){const s=this.curves[t];e.curves.push(s.toJSON())}return e}fromJSON(e){super.fromJSON(e),this.autoClose=e.autoClose,this.curves=[];for(let t=0,n=e.curves.length;t<n;t++){const s=e.curves[t];this.curves.push(new Ea[s.type]().fromJSON(s))}return this}}class Vl extends by{constructor(e){super(),this.type="Path",this.currentPoint=new te,e&&this.setFromPoints(e)}setFromPoints(e){this.moveTo(e[0].x,e[0].y);for(let t=1,n=e.length;t<n;t++)this.lineTo(e[t].x,e[t].y);return this}moveTo(e,t){return this.currentPoint.set(e,t),this}lineTo(e,t){const n=new Ef(this.currentPoint.clone(),new te(e,t));return this.curves.push(n),this.currentPoint.set(e,t),this}quadraticCurveTo(e,t,n,s){const r=new Af(this.currentPoint.clone(),new te(e,t),new te(n,s));return this.curves.push(r),this.currentPoint.set(n,s),this}bezierCurveTo(e,t,n,s,r,o){const a=new Sf(this.currentPoint.clone(),new te(e,t),new te(n,s),new te(r,o));return this.curves.push(a),this.currentPoint.set(r,o),this}splineThru(e){const t=[this.currentPoint.clone()].concat(e),n=new Rf(t);return this.curves.push(n),this.currentPoint.copy(e[e.length-1]),this}arc(e,t,n,s,r,o){const a=this.currentPoint.x,c=this.currentPoint.y;return this.absarc(e+a,t+c,n,s,r,o),this}absarc(e,t,n,s,r,o){return this.absellipse(e,t,n,n,s,r,o),this}ellipse(e,t,n,s,r,o,a,c){const l=this.currentPoint.x,h=this.currentPoint.y;return this.absellipse(e+l,t+h,n,s,r,o,a,c),this}absellipse(e,t,n,s,r,o,a,c){const l=new _h(e,t,n,s,r,o,a,c);if(this.curves.length>0){const u=l.getPoint(0);u.equals(this.currentPoint)||this.lineTo(u.x,u.y)}this.curves.push(l);const h=l.getPoint(1);return this.currentPoint.copy(h),this}copy(e){return super.copy(e),this.currentPoint.copy(e.currentPoint),this}toJSON(){const e=super.toJSON();return e.currentPoint=this.currentPoint.toArray(),e}fromJSON(e){return super.fromJSON(e),this.currentPoint.fromArray(e.currentPoint),this}}class br extends Gt{constructor(e=[new te(0,-.5),new te(.5,0),new te(0,.5)],t=12,n=0,s=Math.PI*2){super(),this.type="LatheGeometry",this.parameters={points:e,segments:t,phiStart:n,phiLength:s},t=Math.floor(t),s=Yt(s,0,Math.PI*2);const r=[],o=[],a=[],c=[],l=[],h=1/t,u=new v,d=new te,f=new v,m=new v,_=new v;let g=0,p=0;for(let y=0;y<=e.length-1;y++)switch(y){case 0:g=e[y+1].x-e[y].x,p=e[y+1].y-e[y].y,f.x=p*1,f.y=-g,f.z=p*0,_.copy(f),f.normalize(),c.push(f.x,f.y,f.z);break;case e.length-1:c.push(_.x,_.y,_.z);break;default:g=e[y+1].x-e[y].x,p=e[y+1].y-e[y].y,f.x=p*1,f.y=-g,f.z=p*0,m.copy(f),f.x+=_.x,f.y+=_.y,f.z+=_.z,f.normalize(),c.push(f.x,f.y,f.z),_.copy(m)}for(let y=0;y<=t;y++){const M=n+y*h*s,x=Math.sin(M),E=Math.cos(M);for(let T=0;T<=e.length-1;T++){u.x=e[T].x*x,u.y=e[T].y,u.z=e[T].x*E,o.push(u.x,u.y,u.z),d.x=y/t,d.y=T/(e.length-1),a.push(d.x,d.y);const P=c[3*T+0]*x,C=c[3*T+1],b=c[3*T+0]*E;l.push(P,C,b)}}for(let y=0;y<t;y++)for(let M=0;M<e.length-1;M++){const x=M+y*e.length,E=x,T=x+e.length,P=x+e.length+1,C=x+1;r.push(E,T,C),r.push(P,C,T)}this.setIndex(r),this.setAttribute("position",new ct(o,3)),this.setAttribute("uv",new ct(a,2)),this.setAttribute("normal",new ct(l,3))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new br(e.points,e.segments,e.phiStart,e.phiLength)}}class yh extends br{constructor(e=1,t=1,n=4,s=8){const r=new Vl;r.absarc(0,-t/2,e,Math.PI*1.5,0),r.absarc(0,t/2,e,0,Math.PI*.5),super(r.getPoints(n),s),this.type="CapsuleGeometry",this.parameters={radius:e,length:t,capSegments:n,radialSegments:s}}static fromJSON(e){return new yh(e.radius,e.length,e.capSegments,e.radialSegments)}}class Ri extends Gt{constructor(e=1,t=32,n=0,s=Math.PI*2){super(),this.type="CircleGeometry",this.parameters={radius:e,segments:t,thetaStart:n,thetaLength:s},t=Math.max(3,t);const r=[],o=[],a=[],c=[],l=new v,h=new te;o.push(0,0,0),a.push(0,0,1),c.push(.5,.5);for(let u=0,d=3;u<=t;u++,d+=3){const f=n+u/t*s;l.x=e*Math.cos(f),l.y=e*Math.sin(f),o.push(l.x,l.y,l.z),a.push(0,0,1),h.x=(o[d]/e+1)/2,h.y=(o[d+1]/e+1)/2,c.push(h.x,h.y)}for(let u=1;u<=t;u++)r.push(u,u+1,0);this.setIndex(r),this.setAttribute("position",new ct(o,3)),this.setAttribute("normal",new ct(a,3)),this.setAttribute("uv",new ct(c,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ri(e.radius,e.segments,e.thetaStart,e.thetaLength)}}class et extends Gt{constructor(e=1,t=1,n=1,s=32,r=1,o=!1,a=0,c=Math.PI*2){super(),this.type="CylinderGeometry",this.parameters={radiusTop:e,radiusBottom:t,height:n,radialSegments:s,heightSegments:r,openEnded:o,thetaStart:a,thetaLength:c};const l=this;s=Math.floor(s),r=Math.floor(r);const h=[],u=[],d=[],f=[];let m=0;const _=[],g=n/2;let p=0;y(),o===!1&&(e>0&&M(!0),t>0&&M(!1)),this.setIndex(h),this.setAttribute("position",new ct(u,3)),this.setAttribute("normal",new ct(d,3)),this.setAttribute("uv",new ct(f,2));function y(){const x=new v,E=new v;let T=0;const P=(t-e)/n;for(let C=0;C<=r;C++){const b=[],w=C/r,L=w*(t-e)+e;for(let F=0;F<=s;F++){const O=F/s,k=O*c+a,K=Math.sin(k),X=Math.cos(k);E.x=L*K,E.y=-w*n+g,E.z=L*X,u.push(E.x,E.y,E.z),x.set(K,P,X).normalize(),d.push(x.x,x.y,x.z),f.push(O,1-w),b.push(m++)}_.push(b)}for(let C=0;C<s;C++)for(let b=0;b<r;b++){const w=_[b][C],L=_[b+1][C],F=_[b+1][C+1],O=_[b][C+1];(e>0||b!==0)&&(h.push(w,L,O),T+=3),(t>0||b!==r-1)&&(h.push(L,F,O),T+=3)}l.addGroup(p,T,0),p+=T}function M(x){const E=m,T=new te,P=new v;let C=0;const b=x===!0?e:t,w=x===!0?1:-1;for(let F=1;F<=s;F++)u.push(0,g*w,0),d.push(0,w,0),f.push(.5,.5),m++;const L=m;for(let F=0;F<=s;F++){const k=F/s*c+a,K=Math.cos(k),X=Math.sin(k);P.x=b*X,P.y=g*w,P.z=b*K,u.push(P.x,P.y,P.z),d.push(0,w,0),T.x=K*.5+.5,T.y=X*.5*w+.5,f.push(T.x,T.y),m++}for(let F=0;F<s;F++){const O=E+F,k=L+F;x===!0?h.push(k,k+1,O):h.push(k+1,k,O),C+=3}l.addGroup(p,C,x===!0?1:2),p+=C}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new et(e.radiusTop,e.radiusBottom,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class si extends et{constructor(e=1,t=1,n=32,s=1,r=!1,o=0,a=Math.PI*2){super(0,e,t,n,s,r,o,a),this.type="ConeGeometry",this.parameters={radius:e,height:t,radialSegments:n,heightSegments:s,openEnded:r,thetaStart:o,thetaLength:a}}static fromJSON(e){return new si(e.radius,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class za extends Gt{constructor(e=[],t=[],n=1,s=0){super(),this.type="PolyhedronGeometry",this.parameters={vertices:e,indices:t,radius:n,detail:s};const r=[],o=[];a(s),l(n),h(),this.setAttribute("position",new ct(r,3)),this.setAttribute("normal",new ct(r.slice(),3)),this.setAttribute("uv",new ct(o,2)),s===0?this.computeVertexNormals():this.normalizeNormals();function a(y){const M=new v,x=new v,E=new v;for(let T=0;T<t.length;T+=3)f(t[T+0],M),f(t[T+1],x),f(t[T+2],E),c(M,x,E,y)}function c(y,M,x,E){const T=E+1,P=[];for(let C=0;C<=T;C++){P[C]=[];const b=y.clone().lerp(x,C/T),w=M.clone().lerp(x,C/T),L=T-C;for(let F=0;F<=L;F++)F===0&&C===T?P[C][F]=b:P[C][F]=b.clone().lerp(w,F/L)}for(let C=0;C<T;C++)for(let b=0;b<2*(T-C)-1;b++){const w=Math.floor(b/2);b%2===0?(d(P[C][w+1]),d(P[C+1][w]),d(P[C][w])):(d(P[C][w+1]),d(P[C+1][w+1]),d(P[C+1][w]))}}function l(y){const M=new v;for(let x=0;x<r.length;x+=3)M.x=r[x+0],M.y=r[x+1],M.z=r[x+2],M.normalize().multiplyScalar(y),r[x+0]=M.x,r[x+1]=M.y,r[x+2]=M.z}function h(){const y=new v;for(let M=0;M<r.length;M+=3){y.x=r[M+0],y.y=r[M+1],y.z=r[M+2];const x=g(y)/2/Math.PI+.5,E=p(y)/Math.PI+.5;o.push(x,1-E)}m(),u()}function u(){for(let y=0;y<o.length;y+=6){const M=o[y+0],x=o[y+2],E=o[y+4],T=Math.max(M,x,E),P=Math.min(M,x,E);T>.9&&P<.1&&(M<.2&&(o[y+0]+=1),x<.2&&(o[y+2]+=1),E<.2&&(o[y+4]+=1))}}function d(y){r.push(y.x,y.y,y.z)}function f(y,M){const x=y*3;M.x=e[x+0],M.y=e[x+1],M.z=e[x+2]}function m(){const y=new v,M=new v,x=new v,E=new v,T=new te,P=new te,C=new te;for(let b=0,w=0;b<r.length;b+=9,w+=6){y.set(r[b+0],r[b+1],r[b+2]),M.set(r[b+3],r[b+4],r[b+5]),x.set(r[b+6],r[b+7],r[b+8]),T.set(o[w+0],o[w+1]),P.set(o[w+2],o[w+3]),C.set(o[w+4],o[w+5]),E.copy(y).add(M).add(x).divideScalar(3);const L=g(E);_(T,w+0,y,L),_(P,w+2,M,L),_(C,w+4,x,L)}}function _(y,M,x,E){E<0&&y.x===1&&(o[M]=y.x-1),x.x===0&&x.z===0&&(o[M]=E/2/Math.PI+.5)}function g(y){return Math.atan2(y.z,-y.x)}function p(y){return Math.atan2(-y.y,Math.sqrt(y.x*y.x+y.z*y.z))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new za(e.vertices,e.indices,e.radius,e.details)}}const Ko=new v,Zo=new v,Nc=new v,Jo=new Bn;class Ha extends Gt{constructor(e=null,t=1){if(super(),this.type="EdgesGeometry",this.parameters={geometry:e,thresholdAngle:t},e!==null){const s=Math.pow(10,4),r=Math.cos(sr*t),o=e.getIndex(),a=e.getAttribute("position"),c=o?o.count:a.count,l=[0,0,0],h=["a","b","c"],u=new Array(3),d={},f=[];for(let m=0;m<c;m+=3){o?(l[0]=o.getX(m),l[1]=o.getX(m+1),l[2]=o.getX(m+2)):(l[0]=m,l[1]=m+1,l[2]=m+2);const{a:_,b:g,c:p}=Jo;if(_.fromBufferAttribute(a,l[0]),g.fromBufferAttribute(a,l[1]),p.fromBufferAttribute(a,l[2]),Jo.getNormal(Nc),u[0]=`${Math.round(_.x*s)},${Math.round(_.y*s)},${Math.round(_.z*s)}`,u[1]=`${Math.round(g.x*s)},${Math.round(g.y*s)},${Math.round(g.z*s)}`,u[2]=`${Math.round(p.x*s)},${Math.round(p.y*s)},${Math.round(p.z*s)}`,!(u[0]===u[1]||u[1]===u[2]||u[2]===u[0]))for(let y=0;y<3;y++){const M=(y+1)%3,x=u[y],E=u[M],T=Jo[h[y]],P=Jo[h[M]],C=`${x}_${E}`,b=`${E}_${x}`;b in d&&d[b]?(Nc.dot(d[b].normal)<=r&&(f.push(T.x,T.y,T.z),f.push(P.x,P.y,P.z)),d[b]=null):C in d||(d[C]={index0:l[y],index1:l[M],normal:Nc.clone()})}}for(const m in d)if(d[m]){const{index0:_,index1:g}=d[m];Ko.fromBufferAttribute(a,_),Zo.fromBufferAttribute(a,g),f.push(Ko.x,Ko.y,Ko.z),f.push(Zo.x,Zo.y,Zo.z)}this.setAttribute("position",new ct(f,3))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}}class Ps extends Vl{constructor(e){super(e),this.uuid=zn(),this.type="Shape",this.holes=[]}getPointsHoles(e){const t=[];for(let n=0,s=this.holes.length;n<s;n++)t[n]=this.holes[n].getPoints(e);return t}extractPoints(e){return{shape:this.getPoints(e),holes:this.getPointsHoles(e)}}copy(e){super.copy(e),this.holes=[];for(let t=0,n=e.holes.length;t<n;t++){const s=e.holes[t];this.holes.push(s.clone())}return this}toJSON(){const e=super.toJSON();e.uuid=this.uuid,e.holes=[];for(let t=0,n=this.holes.length;t<n;t++){const s=this.holes[t];e.holes.push(s.toJSON())}return e}fromJSON(e){super.fromJSON(e),this.uuid=e.uuid,this.holes=[];for(let t=0,n=e.holes.length;t<n;t++){const s=e.holes[t];this.holes.push(new Vl().fromJSON(s))}return this}}const Sy={triangulate:function(i,e,t=2){const n=e&&e.length,s=n?e[0]*t:i.length;let r=Cf(i,0,s,t,!0);const o=[];if(!r||r.next===r.prev)return o;let a,c,l,h,u,d,f;if(n&&(r=Cy(i,e,r,t)),i.length>80*t){a=l=i[0],c=h=i[1];for(let m=t;m<s;m+=t)u=i[m],d=i[m+1],u<a&&(a=u),d<c&&(c=d),u>l&&(l=u),d>h&&(h=d);f=Math.max(l-a,h-c),f=f!==0?32767/f:0}return ao(r,o,t,a,c,f,0),o}};function Cf(i,e,t,n,s){let r,o;if(s===zy(i,e,t,n)>0)for(r=e;r<t;r+=n)o=od(r,i[r],i[r+1],o);else for(r=t-n;r>=e;r-=n)o=od(r,i[r],i[r+1],o);return o&&Ga(o,o.next)&&(lo(o),o=o.next),o}function Rs(i,e){if(!i)return i;e||(e=i);let t=i,n;do if(n=!1,!t.steiner&&(Ga(t,t.next)||zt(t.prev,t,t.next)===0)){if(lo(t),t=e=t.prev,t===t.next)break;n=!0}else t=t.next;while(n||t!==e);return e}function ao(i,e,t,n,s,r,o){if(!i)return;!o&&r&&Ny(i,n,s,r);let a=i,c,l;for(;i.prev!==i.next;){if(c=i.prev,l=i.next,r?Ty(i,n,s,r):Ey(i)){e.push(c.i/t|0),e.push(i.i/t|0),e.push(l.i/t|0),lo(i),i=l.next,a=l.next;continue}if(i=l,i===a){o?o===1?(i=Ay(Rs(i),e,t),ao(i,e,t,n,s,r,2)):o===2&&Ry(i,e,t,n,s,r):ao(Rs(i),e,t,n,s,r,1);break}}}function Ey(i){const e=i.prev,t=i,n=i.next;if(zt(e,t,n)>=0)return!1;const s=e.x,r=t.x,o=n.x,a=e.y,c=t.y,l=n.y,h=s<r?s<o?s:o:r<o?r:o,u=a<c?a<l?a:l:c<l?c:l,d=s>r?s>o?s:o:r>o?r:o,f=a>c?a>l?a:l:c>l?c:l;let m=n.next;for(;m!==e;){if(m.x>=h&&m.x<=d&&m.y>=u&&m.y<=f&&er(s,a,r,c,o,l,m.x,m.y)&&zt(m.prev,m,m.next)>=0)return!1;m=m.next}return!0}function Ty(i,e,t,n){const s=i.prev,r=i,o=i.next;if(zt(s,r,o)>=0)return!1;const a=s.x,c=r.x,l=o.x,h=s.y,u=r.y,d=o.y,f=a<c?a<l?a:l:c<l?c:l,m=h<u?h<d?h:d:u<d?u:d,_=a>c?a>l?a:l:c>l?c:l,g=h>u?h>d?h:d:u>d?u:d,p=Wl(f,m,e,t,n),y=Wl(_,g,e,t,n);let M=i.prevZ,x=i.nextZ;for(;M&&M.z>=p&&x&&x.z<=y;){if(M.x>=f&&M.x<=_&&M.y>=m&&M.y<=g&&M!==s&&M!==o&&er(a,h,c,u,l,d,M.x,M.y)&&zt(M.prev,M,M.next)>=0||(M=M.prevZ,x.x>=f&&x.x<=_&&x.y>=m&&x.y<=g&&x!==s&&x!==o&&er(a,h,c,u,l,d,x.x,x.y)&&zt(x.prev,x,x.next)>=0))return!1;x=x.nextZ}for(;M&&M.z>=p;){if(M.x>=f&&M.x<=_&&M.y>=m&&M.y<=g&&M!==s&&M!==o&&er(a,h,c,u,l,d,M.x,M.y)&&zt(M.prev,M,M.next)>=0)return!1;M=M.prevZ}for(;x&&x.z<=y;){if(x.x>=f&&x.x<=_&&x.y>=m&&x.y<=g&&x!==s&&x!==o&&er(a,h,c,u,l,d,x.x,x.y)&&zt(x.prev,x,x.next)>=0)return!1;x=x.nextZ}return!0}function Ay(i,e,t){let n=i;do{const s=n.prev,r=n.next.next;!Ga(s,r)&&Pf(s,n,n.next,r)&&co(s,r)&&co(r,s)&&(e.push(s.i/t|0),e.push(n.i/t|0),e.push(r.i/t|0),lo(n),lo(n.next),n=i=r),n=n.next}while(n!==i);return Rs(n)}function Ry(i,e,t,n,s,r){let o=i;do{let a=o.next.next;for(;a!==o.prev;){if(o.i!==a.i&&Fy(o,a)){let c=Lf(o,a);o=Rs(o,o.next),c=Rs(c,c.next),ao(o,e,t,n,s,r,0),ao(c,e,t,n,s,r,0);return}a=a.next}o=o.next}while(o!==i)}function Cy(i,e,t,n){const s=[];let r,o,a,c,l;for(r=0,o=e.length;r<o;r++)a=e[r]*n,c=r<o-1?e[r+1]*n:i.length,l=Cf(i,a,c,n,!1),l===l.next&&(l.steiner=!0),s.push(Oy(l));for(s.sort(Py),r=0;r<s.length;r++)t=Ly(s[r],t);return t}function Py(i,e){return i.x-e.x}function Ly(i,e){const t=Iy(i,e);if(!t)return e;const n=Lf(t,i);return Rs(n,n.next),Rs(t,t.next)}function Iy(i,e){let t=e,n=-1/0,s;const r=i.x,o=i.y;do{if(o<=t.y&&o>=t.next.y&&t.next.y!==t.y){const d=t.x+(o-t.y)*(t.next.x-t.x)/(t.next.y-t.y);if(d<=r&&d>n&&(n=d,s=t.x<t.next.x?t:t.next,d===r))return s}t=t.next}while(t!==e);if(!s)return null;const a=s,c=s.x,l=s.y;let h=1/0,u;t=s;do r>=t.x&&t.x>=c&&r!==t.x&&er(o<l?r:n,o,c,l,o<l?n:r,o,t.x,t.y)&&(u=Math.abs(o-t.y)/(r-t.x),co(t,i)&&(u<h||u===h&&(t.x>s.x||t.x===s.x&&Dy(s,t)))&&(s=t,h=u)),t=t.next;while(t!==a);return s}function Dy(i,e){return zt(i.prev,i,e.prev)<0&&zt(e.next,i,i.next)<0}function Ny(i,e,t,n){let s=i;do s.z===0&&(s.z=Wl(s.x,s.y,e,t,n)),s.prevZ=s.prev,s.nextZ=s.next,s=s.next;while(s!==i);s.prevZ.nextZ=null,s.prevZ=null,Uy(s)}function Uy(i){let e,t,n,s,r,o,a,c,l=1;do{for(t=i,i=null,r=null,o=0;t;){for(o++,n=t,a=0,e=0;e<l&&(a++,n=n.nextZ,!!n);e++);for(c=l;a>0||c>0&&n;)a!==0&&(c===0||!n||t.z<=n.z)?(s=t,t=t.nextZ,a--):(s=n,n=n.nextZ,c--),r?r.nextZ=s:i=s,s.prevZ=r,r=s;t=n}r.nextZ=null,l*=2}while(o>1);return i}function Wl(i,e,t,n,s){return i=(i-t)*s|0,e=(e-n)*s|0,i=(i|i<<8)&16711935,i=(i|i<<4)&252645135,i=(i|i<<2)&858993459,i=(i|i<<1)&1431655765,e=(e|e<<8)&16711935,e=(e|e<<4)&252645135,e=(e|e<<2)&858993459,e=(e|e<<1)&1431655765,i|e<<1}function Oy(i){let e=i,t=i;do(e.x<t.x||e.x===t.x&&e.y<t.y)&&(t=e),e=e.next;while(e!==i);return t}function er(i,e,t,n,s,r,o,a){return(s-o)*(e-a)>=(i-o)*(r-a)&&(i-o)*(n-a)>=(t-o)*(e-a)&&(t-o)*(r-a)>=(s-o)*(n-a)}function Fy(i,e){return i.next.i!==e.i&&i.prev.i!==e.i&&!By(i,e)&&(co(i,e)&&co(e,i)&&ky(i,e)&&(zt(i.prev,i,e.prev)||zt(i,e.prev,e))||Ga(i,e)&&zt(i.prev,i,i.next)>0&&zt(e.prev,e,e.next)>0)}function zt(i,e,t){return(e.y-i.y)*(t.x-e.x)-(e.x-i.x)*(t.y-e.y)}function Ga(i,e){return i.x===e.x&&i.y===e.y}function Pf(i,e,t,n){const s=ea(zt(i,e,t)),r=ea(zt(i,e,n)),o=ea(zt(t,n,i)),a=ea(zt(t,n,e));return!!(s!==r&&o!==a||s===0&&Qo(i,t,e)||r===0&&Qo(i,n,e)||o===0&&Qo(t,i,n)||a===0&&Qo(t,e,n))}function Qo(i,e,t){return e.x<=Math.max(i.x,t.x)&&e.x>=Math.min(i.x,t.x)&&e.y<=Math.max(i.y,t.y)&&e.y>=Math.min(i.y,t.y)}function ea(i){return i>0?1:i<0?-1:0}function By(i,e){let t=i;do{if(t.i!==i.i&&t.next.i!==i.i&&t.i!==e.i&&t.next.i!==e.i&&Pf(t,t.next,i,e))return!0;t=t.next}while(t!==i);return!1}function co(i,e){return zt(i.prev,i,i.next)<0?zt(i,e,i.next)>=0&&zt(i,i.prev,e)>=0:zt(i,e,i.prev)<0||zt(i,i.next,e)<0}function ky(i,e){let t=i,n=!1;const s=(i.x+e.x)/2,r=(i.y+e.y)/2;do t.y>r!=t.next.y>r&&t.next.y!==t.y&&s<(t.next.x-t.x)*(r-t.y)/(t.next.y-t.y)+t.x&&(n=!n),t=t.next;while(t!==i);return n}function Lf(i,e){const t=new Xl(i.i,i.x,i.y),n=new Xl(e.i,e.x,e.y),s=i.next,r=e.prev;return i.next=e,e.prev=i,t.next=s,s.prev=t,n.next=t,t.prev=n,r.next=n,n.prev=r,n}function od(i,e,t,n){const s=new Xl(i,e,t);return n?(s.next=n.next,s.prev=n,n.next.prev=s,n.next=s):(s.prev=s,s.next=s),s}function lo(i){i.next.prev=i.prev,i.prev.next=i.next,i.prevZ&&(i.prevZ.nextZ=i.nextZ),i.nextZ&&(i.nextZ.prevZ=i.prevZ)}function Xl(i,e,t){this.i=i,this.x=e,this.y=t,this.prev=null,this.next=null,this.z=0,this.prevZ=null,this.nextZ=null,this.steiner=!1}function zy(i,e,t,n){let s=0;for(let r=e,o=t-n;r<t;r+=n)s+=(i[o]-i[r])*(i[r+1]+i[o+1]),o=r;return s}class Qi{static area(e){const t=e.length;let n=0;for(let s=t-1,r=0;r<t;s=r++)n+=e[s].x*e[r].y-e[r].x*e[s].y;return n*.5}static isClockWise(e){return Qi.area(e)<0}static triangulateShape(e,t){const n=[],s=[],r=[];ad(e),cd(n,e);let o=e.length;t.forEach(ad);for(let c=0;c<t.length;c++)s.push(o),o+=t[c].length,cd(n,t[c]);const a=Sy.triangulate(n,s);for(let c=0;c<a.length;c+=3)r.push(a.slice(c,c+3));return r}}function ad(i){const e=i.length;e>2&&i[e-1].equals(i[0])&&i.pop()}function cd(i,e){for(let t=0;t<e.length;t++)i.push(e[t].x),i.push(e[t].y)}class po extends Gt{constructor(e=new Ps([new te(.5,.5),new te(-.5,.5),new te(-.5,-.5),new te(.5,-.5)]),t={}){super(),this.type="ExtrudeGeometry",this.parameters={shapes:e,options:t},e=Array.isArray(e)?e:[e];const n=this,s=[],r=[];for(let a=0,c=e.length;a<c;a++){const l=e[a];o(l)}this.setAttribute("position",new ct(s,3)),this.setAttribute("uv",new ct(r,2)),this.computeVertexNormals();function o(a){const c=[],l=t.curveSegments!==void 0?t.curveSegments:12,h=t.steps!==void 0?t.steps:1,u=t.depth!==void 0?t.depth:1;let d=t.bevelEnabled!==void 0?t.bevelEnabled:!0,f=t.bevelThickness!==void 0?t.bevelThickness:.2,m=t.bevelSize!==void 0?t.bevelSize:f-.1,_=t.bevelOffset!==void 0?t.bevelOffset:0,g=t.bevelSegments!==void 0?t.bevelSegments:3;const p=t.extrudePath,y=t.UVGenerator!==void 0?t.UVGenerator:Hy;let M,x=!1,E,T,P,C;p&&(M=p.getSpacedPoints(h),x=!0,d=!1,E=p.computeFrenetFrames(h,!1),T=new v,P=new v,C=new v),d||(g=0,f=0,m=0,_=0);const b=a.extractPoints(l);let w=b.shape;const L=b.holes;if(!Qi.isClockWise(w)){w=w.reverse();for(let Q=0,le=L.length;Q<le;Q++){const I=L[Q];Qi.isClockWise(I)&&(L[Q]=I.reverse())}}const O=Qi.triangulateShape(w,L),k=w;for(let Q=0,le=L.length;Q<le;Q++){const I=L[Q];w=w.concat(I)}function K(Q,le,I){return le||console.error("THREE.ExtrudeGeometry: vec does not exist"),Q.clone().addScaledVector(le,I)}const X=w.length,j=O.length;function V(Q,le,I){let ze,re,Le;const ge=Q.x-le.x,Xe=Q.y-le.y,Ce=I.x-Q.x,R=I.y-Q.y,S=ge*ge+Xe*Xe,B=ge*R-Xe*Ce;if(Math.abs(B)>Number.EPSILON){const $=Math.sqrt(S),ee=Math.sqrt(Ce*Ce+R*R),Y=le.x-Xe/$,Oe=le.y+ge/$,ye=I.x-R/ee,Pe=I.y+Ce/ee,dt=((ye-Y)*R-(Pe-Oe)*Ce)/(ge*R-Xe*Ce);ze=Y+ge*dt-Q.x,re=Oe+Xe*dt-Q.y;const ae=ze*ze+re*re;if(ae<=2)return new te(ze,re);Le=Math.sqrt(ae/2)}else{let $=!1;ge>Number.EPSILON?Ce>Number.EPSILON&&($=!0):ge<-Number.EPSILON?Ce<-Number.EPSILON&&($=!0):Math.sign(Xe)===Math.sign(R)&&($=!0),$?(ze=-Xe,re=ge,Le=Math.sqrt(S)):(ze=ge,re=Xe,Le=Math.sqrt(S/2))}return new te(ze/Le,re/Le)}const oe=[];for(let Q=0,le=k.length,I=le-1,ze=Q+1;Q<le;Q++,I++,ze++)I===le&&(I=0),ze===le&&(ze=0),oe[Q]=V(k[Q],k[I],k[ze]);const _e=[];let Re,tt=oe.concat();for(let Q=0,le=L.length;Q<le;Q++){const I=L[Q];Re=[];for(let ze=0,re=I.length,Le=re-1,ge=ze+1;ze<re;ze++,Le++,ge++)Le===re&&(Le=0),ge===re&&(ge=0),Re[ze]=V(I[ze],I[Le],I[ge]);_e.push(Re),tt=tt.concat(Re)}for(let Q=0;Q<g;Q++){const le=Q/g,I=f*Math.cos(le*Math.PI/2),ze=m*Math.sin(le*Math.PI/2)+_;for(let re=0,Le=k.length;re<Le;re++){const ge=K(k[re],oe[re],ze);pe(ge.x,ge.y,-I)}for(let re=0,Le=L.length;re<Le;re++){const ge=L[re];Re=_e[re];for(let Xe=0,Ce=ge.length;Xe<Ce;Xe++){const R=K(ge[Xe],Re[Xe],ze);pe(R.x,R.y,-I)}}}const wt=m+_;for(let Q=0;Q<X;Q++){const le=d?K(w[Q],tt[Q],wt):w[Q];x?(P.copy(E.normals[0]).multiplyScalar(le.x),T.copy(E.binormals[0]).multiplyScalar(le.y),C.copy(M[0]).add(P).add(T),pe(C.x,C.y,C.z)):pe(le.x,le.y,0)}for(let Q=1;Q<=h;Q++)for(let le=0;le<X;le++){const I=d?K(w[le],tt[le],wt):w[le];x?(P.copy(E.normals[Q]).multiplyScalar(I.x),T.copy(E.binormals[Q]).multiplyScalar(I.y),C.copy(M[Q]).add(P).add(T),pe(C.x,C.y,C.z)):pe(I.x,I.y,u/h*Q)}for(let Q=g-1;Q>=0;Q--){const le=Q/g,I=f*Math.cos(le*Math.PI/2),ze=m*Math.sin(le*Math.PI/2)+_;for(let re=0,Le=k.length;re<Le;re++){const ge=K(k[re],oe[re],ze);pe(ge.x,ge.y,u+I)}for(let re=0,Le=L.length;re<Le;re++){const ge=L[re];Re=_e[re];for(let Xe=0,Ce=ge.length;Xe<Ce;Xe++){const R=K(ge[Xe],Re[Xe],ze);x?pe(R.x,R.y+M[h-1].y,M[h-1].x+I):pe(R.x,R.y,u+I)}}}Z(),he();function Z(){const Q=s.length/3;if(d){let le=0,I=X*le;for(let ze=0;ze<j;ze++){const re=O[ze];We(re[2]+I,re[1]+I,re[0]+I)}le=h+g*2,I=X*le;for(let ze=0;ze<j;ze++){const re=O[ze];We(re[0]+I,re[1]+I,re[2]+I)}}else{for(let le=0;le<j;le++){const I=O[le];We(I[2],I[1],I[0])}for(let le=0;le<j;le++){const I=O[le];We(I[0]+X*h,I[1]+X*h,I[2]+X*h)}}n.addGroup(Q,s.length/3-Q,0)}function he(){const Q=s.length/3;let le=0;Ne(k,le),le+=k.length;for(let I=0,ze=L.length;I<ze;I++){const re=L[I];Ne(re,le),le+=re.length}n.addGroup(Q,s.length/3-Q,1)}function Ne(Q,le){let I=Q.length;for(;--I>=0;){const ze=I;let re=I-1;re<0&&(re=Q.length-1);for(let Le=0,ge=h+g*2;Le<ge;Le++){const Xe=X*Le,Ce=X*(Le+1),R=le+ze+Xe,S=le+re+Xe,B=le+re+Ce,$=le+ze+Ce;Ze(R,S,B,$)}}}function pe(Q,le,I){c.push(Q),c.push(le),c.push(I)}function We(Q,le,I){je(Q),je(le),je(I);const ze=s.length/3,re=y.generateTopUV(n,s,ze-3,ze-2,ze-1);gt(re[0]),gt(re[1]),gt(re[2])}function Ze(Q,le,I,ze){je(Q),je(le),je(ze),je(le),je(I),je(ze);const re=s.length/3,Le=y.generateSideWallUV(n,s,re-6,re-3,re-2,re-1);gt(Le[0]),gt(Le[1]),gt(Le[3]),gt(Le[1]),gt(Le[2]),gt(Le[3])}function je(Q){s.push(c[Q*3+0]),s.push(c[Q*3+1]),s.push(c[Q*3+2])}function gt(Q){r.push(Q.x),r.push(Q.y)}}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}toJSON(){const e=super.toJSON(),t=this.parameters.shapes,n=this.parameters.options;return Gy(t,n,e)}static fromJSON(e,t){const n=[];for(let r=0,o=e.shapes.length;r<o;r++){const a=t[e.shapes[r]];n.push(a)}const s=e.options.extrudePath;return s!==void 0&&(e.options.extrudePath=new Ea[s.type]().fromJSON(s)),new po(n,e.options)}}const Hy={generateTopUV:function(i,e,t,n,s){const r=e[t*3],o=e[t*3+1],a=e[n*3],c=e[n*3+1],l=e[s*3],h=e[s*3+1];return[new te(r,o),new te(a,c),new te(l,h)]},generateSideWallUV:function(i,e,t,n,s,r){const o=e[t*3],a=e[t*3+1],c=e[t*3+2],l=e[n*3],h=e[n*3+1],u=e[n*3+2],d=e[s*3],f=e[s*3+1],m=e[s*3+2],_=e[r*3],g=e[r*3+1],p=e[r*3+2];return Math.abs(a-h)<Math.abs(o-l)?[new te(o,1-c),new te(l,1-u),new te(d,1-m),new te(_,1-p)]:[new te(a,1-c),new te(h,1-u),new te(f,1-m),new te(g,1-p)]}};function Gy(i,e,t){if(t.shapes=[],Array.isArray(i))for(let n=0,s=i.length;n<s;n++){const r=i[n];t.shapes.push(r.uuid)}else t.shapes.push(i.uuid);return t.options=Object.assign({},e),e.extrudePath!==void 0&&(t.options.extrudePath=e.extrudePath.toJSON()),t}class Va extends za{constructor(e=1,t=0){const n=(1+Math.sqrt(5))/2,s=[-1,n,0,1,n,0,-1,-n,0,1,-n,0,0,-1,n,0,1,n,0,-1,-n,0,1,-n,n,0,-1,n,0,1,-n,0,-1,-n,0,1],r=[0,11,5,0,5,1,0,1,7,0,7,10,0,10,11,1,5,9,5,11,4,11,10,2,10,7,6,7,1,8,3,9,4,3,4,2,3,2,6,3,6,8,3,8,9,4,9,5,2,4,11,6,2,10,8,6,7,9,8,1];super(s,r,e,t),this.type="IcosahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new Va(e.radius,e.detail)}}class Mh extends za{constructor(e=1,t=0){const n=[1,0,0,-1,0,0,0,1,0,0,-1,0,0,0,1,0,0,-1],s=[0,2,4,0,4,3,0,3,5,0,5,2,1,2,5,1,5,3,1,3,4,1,4,2];super(n,s,e,t),this.type="OctahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new Mh(e.radius,e.detail)}}class wh extends Gt{constructor(e=.5,t=1,n=32,s=1,r=0,o=Math.PI*2){super(),this.type="RingGeometry",this.parameters={innerRadius:e,outerRadius:t,thetaSegments:n,phiSegments:s,thetaStart:r,thetaLength:o},n=Math.max(3,n),s=Math.max(1,s);const a=[],c=[],l=[],h=[];let u=e;const d=(t-e)/s,f=new v,m=new te;for(let _=0;_<=s;_++){for(let g=0;g<=n;g++){const p=r+g/n*o;f.x=u*Math.cos(p),f.y=u*Math.sin(p),c.push(f.x,f.y,f.z),l.push(0,0,1),m.x=(f.x/t+1)/2,m.y=(f.y/t+1)/2,h.push(m.x,m.y)}u+=d}for(let _=0;_<s;_++){const g=_*(n+1);for(let p=0;p<n;p++){const y=p+g,M=y,x=y+n+1,E=y+n+2,T=y+1;a.push(M,x,T),a.push(x,E,T)}}this.setIndex(a),this.setAttribute("position",new ct(c,3)),this.setAttribute("normal",new ct(l,3)),this.setAttribute("uv",new ct(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new wh(e.innerRadius,e.outerRadius,e.thetaSegments,e.phiSegments,e.thetaStart,e.thetaLength)}}class Wa extends Gt{constructor(e=new Ps([new te(0,.5),new te(-.5,-.5),new te(.5,-.5)]),t=12){super(),this.type="ShapeGeometry",this.parameters={shapes:e,curveSegments:t};const n=[],s=[],r=[],o=[];let a=0,c=0;if(Array.isArray(e)===!1)l(e);else for(let h=0;h<e.length;h++)l(e[h]),this.addGroup(a,c,h),a+=c,c=0;this.setIndex(n),this.setAttribute("position",new ct(s,3)),this.setAttribute("normal",new ct(r,3)),this.setAttribute("uv",new ct(o,2));function l(h){const u=s.length/3,d=h.extractPoints(t);let f=d.shape;const m=d.holes;Qi.isClockWise(f)===!1&&(f=f.reverse());for(let g=0,p=m.length;g<p;g++){const y=m[g];Qi.isClockWise(y)===!0&&(m[g]=y.reverse())}const _=Qi.triangulateShape(f,m);for(let g=0,p=m.length;g<p;g++){const y=m[g];f=f.concat(y)}for(let g=0,p=f.length;g<p;g++){const y=f[g];s.push(y.x,y.y,0),r.push(0,0,1),o.push(y.x,y.y)}for(let g=0,p=_.length;g<p;g++){const y=_[g],M=y[0]+u,x=y[1]+u,E=y[2]+u;n.push(M,x,E),c+=3}}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}toJSON(){const e=super.toJSON(),t=this.parameters.shapes;return Vy(t,e)}static fromJSON(e,t){const n=[];for(let s=0,r=e.shapes.length;s<r;s++){const o=t[e.shapes[s]];n.push(o)}return new Wa(n,e.curveSegments)}}function Vy(i,e){if(e.shapes=[],Array.isArray(i))for(let t=0,n=i.length;t<n;t++){const s=i[t];e.shapes.push(s.uuid)}else e.shapes.push(i.uuid);return e}class Mn extends Gt{constructor(e=1,t=32,n=16,s=0,r=Math.PI*2,o=0,a=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:n,phiStart:s,phiLength:r,thetaStart:o,thetaLength:a},t=Math.max(3,Math.floor(t)),n=Math.max(2,Math.floor(n));const c=Math.min(o+a,Math.PI);let l=0;const h=[],u=new v,d=new v,f=[],m=[],_=[],g=[];for(let p=0;p<=n;p++){const y=[],M=p/n;let x=0;p===0&&o===0?x=.5/t:p===n&&c===Math.PI&&(x=-.5/t);for(let E=0;E<=t;E++){const T=E/t;u.x=-e*Math.cos(s+T*r)*Math.sin(o+M*a),u.y=e*Math.cos(o+M*a),u.z=e*Math.sin(s+T*r)*Math.sin(o+M*a),m.push(u.x,u.y,u.z),d.copy(u).normalize(),_.push(d.x,d.y,d.z),g.push(T+x,1-M),y.push(l++)}h.push(y)}for(let p=0;p<n;p++)for(let y=0;y<t;y++){const M=h[p][y+1],x=h[p][y],E=h[p+1][y],T=h[p+1][y+1];(p!==0||o>0)&&f.push(M,x,T),(p!==n-1||c<Math.PI)&&f.push(x,E,T)}this.setIndex(f),this.setAttribute("position",new ct(m,3)),this.setAttribute("normal",new ct(_,3)),this.setAttribute("uv",new ct(g,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Mn(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}class Hn extends Gt{constructor(e=1,t=.4,n=12,s=48,r=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:e,tube:t,radialSegments:n,tubularSegments:s,arc:r},n=Math.floor(n),s=Math.floor(s);const o=[],a=[],c=[],l=[],h=new v,u=new v,d=new v;for(let f=0;f<=n;f++)for(let m=0;m<=s;m++){const _=m/s*r,g=f/n*Math.PI*2;u.x=(e+t*Math.cos(g))*Math.cos(_),u.y=(e+t*Math.cos(g))*Math.sin(_),u.z=t*Math.sin(g),a.push(u.x,u.y,u.z),h.x=e*Math.cos(_),h.y=e*Math.sin(_),d.subVectors(u,h).normalize(),c.push(d.x,d.y,d.z),l.push(m/s),l.push(f/n)}for(let f=1;f<=n;f++)for(let m=1;m<=s;m++){const _=(s+1)*f+m-1,g=(s+1)*(f-1)+m-1,p=(s+1)*(f-1)+m,y=(s+1)*f+m;o.push(_,g,y),o.push(g,p,y)}this.setIndex(o),this.setAttribute("position",new ct(a,3)),this.setAttribute("normal",new ct(c,3)),this.setAttribute("uv",new ct(l,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Hn(e.radius,e.tube,e.radialSegments,e.tubularSegments,e.arc)}}class gr extends Gt{constructor(e=new vh(new v(-1,-1,0),new v(-1,1,0),new v(1,1,0)),t=64,n=1,s=8,r=!1){super(),this.type="TubeGeometry",this.parameters={path:e,tubularSegments:t,radius:n,radialSegments:s,closed:r};const o=e.computeFrenetFrames(t,r);this.tangents=o.tangents,this.normals=o.normals,this.binormals=o.binormals;const a=new v,c=new v,l=new te;let h=new v;const u=[],d=[],f=[],m=[];_(),this.setIndex(m),this.setAttribute("position",new ct(u,3)),this.setAttribute("normal",new ct(d,3)),this.setAttribute("uv",new ct(f,2));function _(){for(let M=0;M<t;M++)g(M);g(r===!1?t:0),y(),p()}function g(M){h=e.getPointAt(M/t,h);const x=o.normals[M],E=o.binormals[M];for(let T=0;T<=s;T++){const P=T/s*Math.PI*2,C=Math.sin(P),b=-Math.cos(P);c.x=b*x.x+C*E.x,c.y=b*x.y+C*E.y,c.z=b*x.z+C*E.z,c.normalize(),d.push(c.x,c.y,c.z),a.x=h.x+n*c.x,a.y=h.y+n*c.y,a.z=h.z+n*c.z,u.push(a.x,a.y,a.z)}}function p(){for(let M=1;M<=t;M++)for(let x=1;x<=s;x++){const E=(s+1)*(M-1)+(x-1),T=(s+1)*M+(x-1),P=(s+1)*M+x,C=(s+1)*(M-1)+x;m.push(E,T,C),m.push(T,P,C)}}function y(){for(let M=0;M<=t;M++)for(let x=0;x<=s;x++)l.x=M/t,l.y=x/s,f.push(l.x,l.y)}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}toJSON(){const e=super.toJSON();return e.path=this.parameters.path.toJSON(),e}static fromJSON(e){return new gr(new Ea[e.path.type]().fromJSON(e.path),e.tubularSegments,e.radius,e.radialSegments,e.closed)}}class bh extends ri{static get type(){return"MeshStandardMaterial"}constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.color=new Ve(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new Ve(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=sf,this.normalScale=new te(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new wn,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class hi extends bh{static get type(){return"MeshPhysicalMaterial"}constructor(e){super(),this.isMeshPhysicalMaterial=!0,this.defines={STANDARD:"",PHYSICAL:""},this.anisotropyRotation=0,this.anisotropyMap=null,this.clearcoatMap=null,this.clearcoatRoughness=0,this.clearcoatRoughnessMap=null,this.clearcoatNormalScale=new te(1,1),this.clearcoatNormalMap=null,this.ior=1.5,Object.defineProperty(this,"reflectivity",{get:function(){return Yt(2.5*(this.ior-1)/(this.ior+1),0,1)},set:function(t){this.ior=(1+.4*t)/(1-.4*t)}}),this.iridescenceMap=null,this.iridescenceIOR=1.3,this.iridescenceThicknessRange=[100,400],this.iridescenceThicknessMap=null,this.sheenColor=new Ve(0),this.sheenColorMap=null,this.sheenRoughness=1,this.sheenRoughnessMap=null,this.transmissionMap=null,this.thickness=0,this.thicknessMap=null,this.attenuationDistance=1/0,this.attenuationColor=new Ve(1,1,1),this.specularIntensity=1,this.specularIntensityMap=null,this.specularColor=new Ve(1,1,1),this.specularColorMap=null,this._anisotropy=0,this._clearcoat=0,this._dispersion=0,this._iridescence=0,this._sheen=0,this._transmission=0,this.setValues(e)}get anisotropy(){return this._anisotropy}set anisotropy(e){this._anisotropy>0!=e>0&&this.version++,this._anisotropy=e}get clearcoat(){return this._clearcoat}set clearcoat(e){this._clearcoat>0!=e>0&&this.version++,this._clearcoat=e}get iridescence(){return this._iridescence}set iridescence(e){this._iridescence>0!=e>0&&this.version++,this._iridescence=e}get dispersion(){return this._dispersion}set dispersion(e){this._dispersion>0!=e>0&&this.version++,this._dispersion=e}get sheen(){return this._sheen}set sheen(e){this._sheen>0!=e>0&&this.version++,this._sheen=e}get transmission(){return this._transmission}set transmission(e){this._transmission>0!=e>0&&this.version++,this._transmission=e}copy(e){return super.copy(e),this.defines={STANDARD:"",PHYSICAL:""},this.anisotropy=e.anisotropy,this.anisotropyRotation=e.anisotropyRotation,this.anisotropyMap=e.anisotropyMap,this.clearcoat=e.clearcoat,this.clearcoatMap=e.clearcoatMap,this.clearcoatRoughness=e.clearcoatRoughness,this.clearcoatRoughnessMap=e.clearcoatRoughnessMap,this.clearcoatNormalMap=e.clearcoatNormalMap,this.clearcoatNormalScale.copy(e.clearcoatNormalScale),this.dispersion=e.dispersion,this.ior=e.ior,this.iridescence=e.iridescence,this.iridescenceMap=e.iridescenceMap,this.iridescenceIOR=e.iridescenceIOR,this.iridescenceThicknessRange=[...e.iridescenceThicknessRange],this.iridescenceThicknessMap=e.iridescenceThicknessMap,this.sheen=e.sheen,this.sheenColor.copy(e.sheenColor),this.sheenColorMap=e.sheenColorMap,this.sheenRoughness=e.sheenRoughness,this.sheenRoughnessMap=e.sheenRoughnessMap,this.transmission=e.transmission,this.transmissionMap=e.transmissionMap,this.thickness=e.thickness,this.thicknessMap=e.thicknessMap,this.attenuationDistance=e.attenuationDistance,this.attenuationColor.copy(e.attenuationColor),this.specularIntensity=e.specularIntensity,this.specularIntensityMap=e.specularIntensityMap,this.specularColor.copy(e.specularColor),this.specularColorMap=e.specularColorMap,this}}function ta(i,e,t){return!i||!t&&i.constructor===e?i:typeof e.BYTES_PER_ELEMENT=="number"?new e(i):Array.prototype.slice.call(i)}function Wy(i){return ArrayBuffer.isView(i)&&!(i instanceof DataView)}function Xy(i){function e(s,r){return i[s]-i[r]}const t=i.length,n=new Array(t);for(let s=0;s!==t;++s)n[s]=s;return n.sort(e),n}function ld(i,e,t){const n=i.length,s=new i.constructor(n);for(let r=0,o=0;o!==n;++r){const a=t[r]*e;for(let c=0;c!==e;++c)s[o++]=i[a+c]}return s}function If(i,e,t,n){let s=1,r=i[0];for(;r!==void 0&&r[n]===void 0;)r=i[s++];if(r===void 0)return;let o=r[n];if(o!==void 0)if(Array.isArray(o))do o=r[n],o!==void 0&&(e.push(r.time),t.push.apply(t,o)),r=i[s++];while(r!==void 0);else if(o.toArray!==void 0)do o=r[n],o!==void 0&&(e.push(r.time),o.toArray(t,t.length)),r=i[s++];while(r!==void 0);else do o=r[n],o!==void 0&&(e.push(r.time),t.push(o)),r=i[s++];while(r!==void 0)}class mo{constructor(e,t,n,s){this.parameterPositions=e,this._cachedIndex=0,this.resultBuffer=s!==void 0?s:new t.constructor(n),this.sampleValues=t,this.valueSize=n,this.settings=null,this.DefaultSettings_={}}evaluate(e){const t=this.parameterPositions;let n=this._cachedIndex,s=t[n],r=t[n-1];n:{e:{let o;t:{i:if(!(e<s)){for(let a=n+2;;){if(s===void 0){if(e<r)break i;return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}if(n===a)break;if(r=s,s=t[++n],e<s)break e}o=t.length;break t}if(!(e>=r)){const a=t[1];e<a&&(n=2,r=a);for(let c=n-2;;){if(r===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(n===c)break;if(s=r,r=t[--n-1],e>=r)break e}o=n,n=0;break t}break n}for(;n<o;){const a=n+o>>>1;e<t[a]?o=a:n=a+1}if(s=t[n],r=t[n-1],r===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(s===void 0)return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}this._cachedIndex=n,this.intervalChanged_(n,r,s)}return this.interpolate_(n,r,e,s)}getSettings_(){return this.settings||this.DefaultSettings_}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,s=this.valueSize,r=e*s;for(let o=0;o!==s;++o)t[o]=n[r+o];return t}interpolate_(){throw new Error("call to abstract method")}intervalChanged_(){}}class qy extends mo{constructor(e,t,n,s){super(e,t,n,s),this._weightPrev=-0,this._offsetPrev=-0,this._weightNext=-0,this._offsetNext=-0,this.DefaultSettings_={endingStart:$h,endingEnd:$h}}intervalChanged_(e,t,n){const s=this.parameterPositions;let r=e-2,o=e+1,a=s[r],c=s[o];if(a===void 0)switch(this.getSettings_().endingStart){case Yh:r=e,a=2*t-n;break;case Kh:r=s.length-2,a=t+s[r]-s[r+1];break;default:r=e,a=n}if(c===void 0)switch(this.getSettings_().endingEnd){case Yh:o=e,c=2*n-t;break;case Kh:o=1,c=n+s[1]-s[0];break;default:o=e-1,c=t}const l=(n-t)*.5,h=this.valueSize;this._weightPrev=l/(t-a),this._weightNext=l/(c-n),this._offsetPrev=r*h,this._offsetNext=o*h}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=e*a,l=c-a,h=this._offsetPrev,u=this._offsetNext,d=this._weightPrev,f=this._weightNext,m=(n-t)/(s-t),_=m*m,g=_*m,p=-d*g+2*d*_-d*m,y=(1+d)*g+(-1.5-2*d)*_+(-.5+d)*m+1,M=(-1-f)*g+(1.5+f)*_+.5*m,x=f*g-f*_;for(let E=0;E!==a;++E)r[E]=p*o[h+E]+y*o[l+E]+M*o[c+E]+x*o[u+E];return r}}class jy extends mo{constructor(e,t,n,s){super(e,t,n,s)}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=e*a,l=c-a,h=(n-t)/(s-t),u=1-h;for(let d=0;d!==a;++d)r[d]=o[l+d]*u+o[c+d]*h;return r}}class $y extends mo{constructor(e,t,n,s){super(e,t,n,s)}interpolate_(e){return this.copySampleValue_(e-1)}}class ui{constructor(e,t,n,s){if(e===void 0)throw new Error("THREE.KeyframeTrack: track name is undefined");if(t===void 0||t.length===0)throw new Error("THREE.KeyframeTrack: no keyframes in track named "+e);this.name=e,this.times=ta(t,this.TimeBufferType),this.values=ta(n,this.ValueBufferType),this.setInterpolation(s||this.DefaultInterpolation)}static toJSON(e){const t=e.constructor;let n;if(t.toJSON!==this.toJSON)n=t.toJSON(e);else{n={name:e.name,times:ta(e.times,Array),values:ta(e.values,Array)};const s=e.getInterpolation();s!==e.DefaultInterpolation&&(n.interpolation=s)}return n.type=e.ValueTypeName,n}InterpolantFactoryMethodDiscrete(e){return new $y(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodLinear(e){return new jy(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodSmooth(e){return new qy(this.times,this.values,this.getValueSize(),e)}setInterpolation(e){let t;switch(e){case so:t=this.InterpolantFactoryMethodDiscrete;break;case ro:t=this.InterpolantFactoryMethodLinear;break;case ec:t=this.InterpolantFactoryMethodSmooth;break}if(t===void 0){const n="unsupported interpolation for "+this.ValueTypeName+" keyframe track named "+this.name;if(this.createInterpolant===void 0)if(e!==this.DefaultInterpolation)this.setInterpolation(this.DefaultInterpolation);else throw new Error(n);return console.warn("THREE.KeyframeTrack:",n),this}return this.createInterpolant=t,this}getInterpolation(){switch(this.createInterpolant){case this.InterpolantFactoryMethodDiscrete:return so;case this.InterpolantFactoryMethodLinear:return ro;case this.InterpolantFactoryMethodSmooth:return ec}}getValueSize(){return this.values.length/this.times.length}shift(e){if(e!==0){const t=this.times;for(let n=0,s=t.length;n!==s;++n)t[n]+=e}return this}scale(e){if(e!==1){const t=this.times;for(let n=0,s=t.length;n!==s;++n)t[n]*=e}return this}trim(e,t){const n=this.times,s=n.length;let r=0,o=s-1;for(;r!==s&&n[r]<e;)++r;for(;o!==-1&&n[o]>t;)--o;if(++o,r!==0||o!==s){r>=o&&(o=Math.max(o,1),r=o-1);const a=this.getValueSize();this.times=n.slice(r,o),this.values=this.values.slice(r*a,o*a)}return this}validate(){let e=!0;const t=this.getValueSize();t-Math.floor(t)!==0&&(console.error("THREE.KeyframeTrack: Invalid value size in track.",this),e=!1);const n=this.times,s=this.values,r=n.length;r===0&&(console.error("THREE.KeyframeTrack: Track is empty.",this),e=!1);let o=null;for(let a=0;a!==r;a++){const c=n[a];if(typeof c=="number"&&isNaN(c)){console.error("THREE.KeyframeTrack: Time is not a valid number.",this,a,c),e=!1;break}if(o!==null&&o>c){console.error("THREE.KeyframeTrack: Out of order keys.",this,a,c,o),e=!1;break}o=c}if(s!==void 0&&Wy(s))for(let a=0,c=s.length;a!==c;++a){const l=s[a];if(isNaN(l)){console.error("THREE.KeyframeTrack: Value is not a valid number.",this,a,l),e=!1;break}}return e}optimize(){const e=this.times.slice(),t=this.values.slice(),n=this.getValueSize(),s=this.getInterpolation()===ec,r=e.length-1;let o=1;for(let a=1;a<r;++a){let c=!1;const l=e[a],h=e[a+1];if(l!==h&&(a!==1||l!==e[0]))if(s)c=!0;else{const u=a*n,d=u-n,f=u+n;for(let m=0;m!==n;++m){const _=t[u+m];if(_!==t[d+m]||_!==t[f+m]){c=!0;break}}}if(c){if(a!==o){e[o]=e[a];const u=a*n,d=o*n;for(let f=0;f!==n;++f)t[d+f]=t[u+f]}++o}}if(r>0){e[o]=e[r];for(let a=r*n,c=o*n,l=0;l!==n;++l)t[c+l]=t[a+l];++o}return o!==e.length?(this.times=e.slice(0,o),this.values=t.slice(0,o*n)):(this.times=e,this.values=t),this}clone(){const e=this.times.slice(),t=this.values.slice(),n=this.constructor,s=new n(this.name,e,t);return s.createInterpolant=this.createInterpolant,s}}ui.prototype.TimeBufferType=Float32Array;ui.prototype.ValueBufferType=Float32Array;ui.prototype.DefaultInterpolation=ro;class Sr extends ui{constructor(e,t,n){super(e,t,n)}}Sr.prototype.ValueTypeName="bool";Sr.prototype.ValueBufferType=Array;Sr.prototype.DefaultInterpolation=so;Sr.prototype.InterpolantFactoryMethodLinear=void 0;Sr.prototype.InterpolantFactoryMethodSmooth=void 0;class Df extends ui{}Df.prototype.ValueTypeName="color";class _r extends ui{}_r.prototype.ValueTypeName="number";class Yy extends mo{constructor(e,t,n,s){super(e,t,n,s)}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=(n-t)/(s-t);let l=e*a;for(let h=l+a;l!==h;l+=4)Gn.slerpFlat(r,0,o,l-a,o,l,c);return r}}class xr extends ui{InterpolantFactoryMethodLinear(e){return new Yy(this.times,this.values,this.getValueSize(),e)}}xr.prototype.ValueTypeName="quaternion";xr.prototype.InterpolantFactoryMethodSmooth=void 0;class Er extends ui{constructor(e,t,n){super(e,t,n)}}Er.prototype.ValueTypeName="string";Er.prototype.ValueBufferType=Array;Er.prototype.DefaultInterpolation=so;Er.prototype.InterpolantFactoryMethodLinear=void 0;Er.prototype.InterpolantFactoryMethodSmooth=void 0;class vr extends ui{}vr.prototype.ValueTypeName="vector";class Ky{constructor(e="",t=-1,n=[],s=Mm){this.name=e,this.tracks=n,this.duration=t,this.blendMode=s,this.uuid=zn(),this.duration<0&&this.resetDuration()}static parse(e){const t=[],n=e.tracks,s=1/(e.fps||1);for(let o=0,a=n.length;o!==a;++o)t.push(Jy(n[o]).scale(s));const r=new this(e.name,e.duration,t,e.blendMode);return r.uuid=e.uuid,r}static toJSON(e){const t=[],n=e.tracks,s={name:e.name,duration:e.duration,tracks:t,uuid:e.uuid,blendMode:e.blendMode};for(let r=0,o=n.length;r!==o;++r)t.push(ui.toJSON(n[r]));return s}static CreateFromMorphTargetSequence(e,t,n,s){const r=t.length,o=[];for(let a=0;a<r;a++){let c=[],l=[];c.push((a+r-1)%r,a,(a+1)%r),l.push(0,1,0);const h=Xy(c);c=ld(c,1,h),l=ld(l,1,h),!s&&c[0]===0&&(c.push(r),l.push(l[0])),o.push(new _r(".morphTargetInfluences["+t[a].name+"]",c,l).scale(1/n))}return new this(e,-1,o)}static findByName(e,t){let n=e;if(!Array.isArray(e)){const s=e;n=s.geometry&&s.geometry.animations||s.animations}for(let s=0;s<n.length;s++)if(n[s].name===t)return n[s];return null}static CreateClipsFromMorphTargetSequences(e,t,n){const s={},r=/^([\w-]*?)([\d]+)$/;for(let a=0,c=e.length;a<c;a++){const l=e[a],h=l.name.match(r);if(h&&h.length>1){const u=h[1];let d=s[u];d||(s[u]=d=[]),d.push(l)}}const o=[];for(const a in s)o.push(this.CreateFromMorphTargetSequence(a,s[a],t,n));return o}static parseAnimation(e,t){if(!e)return console.error("THREE.AnimationClip: No animation in JSONLoader data."),null;const n=function(u,d,f,m,_){if(f.length!==0){const g=[],p=[];If(f,g,p,m),g.length!==0&&_.push(new u(d,g,p))}},s=[],r=e.name||"default",o=e.fps||30,a=e.blendMode;let c=e.length||-1;const l=e.hierarchy||[];for(let u=0;u<l.length;u++){const d=l[u].keys;if(!(!d||d.length===0))if(d[0].morphTargets){const f={};let m;for(m=0;m<d.length;m++)if(d[m].morphTargets)for(let _=0;_<d[m].morphTargets.length;_++)f[d[m].morphTargets[_]]=-1;for(const _ in f){const g=[],p=[];for(let y=0;y!==d[m].morphTargets.length;++y){const M=d[m];g.push(M.time),p.push(M.morphTarget===_?1:0)}s.push(new _r(".morphTargetInfluence["+_+"]",g,p))}c=f.length*o}else{const f=".bones["+t[u].name+"]";n(vr,f+".position",d,"pos",s),n(xr,f+".quaternion",d,"rot",s),n(vr,f+".scale",d,"scl",s)}}return s.length===0?null:new this(r,c,s,a)}resetDuration(){const e=this.tracks;let t=0;for(let n=0,s=e.length;n!==s;++n){const r=this.tracks[n];t=Math.max(t,r.times[r.times.length-1])}return this.duration=t,this}trim(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].trim(0,this.duration);return this}validate(){let e=!0;for(let t=0;t<this.tracks.length;t++)e=e&&this.tracks[t].validate();return e}optimize(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].optimize();return this}clone(){const e=[];for(let t=0;t<this.tracks.length;t++)e.push(this.tracks[t].clone());return new this.constructor(this.name,this.duration,e,this.blendMode)}toJSON(){return this.constructor.toJSON(this)}}function Zy(i){switch(i.toLowerCase()){case"scalar":case"double":case"float":case"number":case"integer":return _r;case"vector":case"vector2":case"vector3":case"vector4":return vr;case"color":return Df;case"quaternion":return xr;case"bool":case"boolean":return Sr;case"string":return Er}throw new Error("THREE.KeyframeTrack: Unsupported typeName: "+i)}function Jy(i){if(i.type===void 0)throw new Error("THREE.KeyframeTrack: track type undefined, can not parse");const e=Zy(i.type);if(i.times===void 0){const t=[],n=[];If(i.keys,t,n,"value"),i.times=t,i.values=n}return e.parse!==void 0?e.parse(i):new e(i.name,i.times,i.values,i.interpolation)}const ji={enabled:!1,files:{},add:function(i,e){this.enabled!==!1&&(this.files[i]=e)},get:function(i){if(this.enabled!==!1)return this.files[i]},remove:function(i){delete this.files[i]},clear:function(){this.files={}}};class Qy{constructor(e,t,n){const s=this;let r=!1,o=0,a=0,c;const l=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this.itemStart=function(h){a++,r===!1&&s.onStart!==void 0&&s.onStart(h,o,a),r=!0},this.itemEnd=function(h){o++,s.onProgress!==void 0&&s.onProgress(h,o,a),o===a&&(r=!1,s.onLoad!==void 0&&s.onLoad())},this.itemError=function(h){s.onError!==void 0&&s.onError(h)},this.resolveURL=function(h){return c?c(h):h},this.setURLModifier=function(h){return c=h,this},this.addHandler=function(h,u){return l.push(h,u),this},this.removeHandler=function(h){const u=l.indexOf(h);return u!==-1&&l.splice(u,2),this},this.getHandler=function(h){for(let u=0,d=l.length;u<d;u+=2){const f=l[u],m=l[u+1];if(f.global&&(f.lastIndex=0),f.test(h))return m}return null}}}const eM=new Qy;class Ls{constructor(e){this.manager=e!==void 0?e:eM,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){const n=this;return new Promise(function(s,r){n.load(e,s,t,r)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}}Ls.DEFAULT_MATERIAL_NAME="__DEFAULT";const vi={};class tM extends Error{constructor(e,t){super(e),this.response=t}}class Ta extends Ls{constructor(e){super(e)}load(e,t,n,s){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const r=ji.get(e);if(r!==void 0)return this.manager.itemStart(e),setTimeout(()=>{t&&t(r),this.manager.itemEnd(e)},0),r;if(vi[e]!==void 0){vi[e].push({onLoad:t,onProgress:n,onError:s});return}vi[e]=[],vi[e].push({onLoad:t,onProgress:n,onError:s});const o=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin"}),a=this.mimeType,c=this.responseType;fetch(o).then(l=>{if(l.status===200||l.status===0){if(l.status===0&&console.warn("THREE.FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||l.body===void 0||l.body.getReader===void 0)return l;const h=vi[e],u=l.body.getReader(),d=l.headers.get("X-File-Size")||l.headers.get("Content-Length"),f=d?parseInt(d):0,m=f!==0;let _=0;const g=new ReadableStream({start(p){y();function y(){u.read().then(({done:M,value:x})=>{if(M)p.close();else{_+=x.byteLength;const E=new ProgressEvent("progress",{lengthComputable:m,loaded:_,total:f});for(let T=0,P=h.length;T<P;T++){const C=h[T];C.onProgress&&C.onProgress(E)}p.enqueue(x),y()}},M=>{p.error(M)})}}});return new Response(g)}else throw new tM(`fetch for "${l.url}" responded with ${l.status}: ${l.statusText}`,l)}).then(l=>{switch(c){case"arraybuffer":return l.arrayBuffer();case"blob":return l.blob();case"document":return l.text().then(h=>new DOMParser().parseFromString(h,a));case"json":return l.json();default:if(a===void 0)return l.text();{const u=/charset="?([^;"\s]*)"?/i.exec(a),d=u&&u[1]?u[1].toLowerCase():void 0,f=new TextDecoder(d);return l.arrayBuffer().then(m=>f.decode(m))}}}).then(l=>{ji.add(e,l);const h=vi[e];delete vi[e];for(let u=0,d=h.length;u<d;u++){const f=h[u];f.onLoad&&f.onLoad(l)}}).catch(l=>{const h=vi[e];if(h===void 0)throw this.manager.itemError(e),l;delete vi[e];for(let u=0,d=h.length;u<d;u++){const f=h[u];f.onError&&f.onError(l)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}}class nM extends Ls{constructor(e){super(e)}load(e,t,n,s){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const r=this,o=ji.get(e);if(o!==void 0)return r.manager.itemStart(e),setTimeout(function(){t&&t(o),r.manager.itemEnd(e)},0),o;const a=oo("img");function c(){h(),ji.add(e,this),t&&t(this),r.manager.itemEnd(e)}function l(u){h(),s&&s(u),r.manager.itemError(e),r.manager.itemEnd(e)}function h(){a.removeEventListener("load",c,!1),a.removeEventListener("error",l,!1)}return a.addEventListener("load",c,!1),a.addEventListener("error",l,!1),e.slice(0,5)!=="data:"&&this.crossOrigin!==void 0&&(a.crossOrigin=this.crossOrigin),r.manager.itemStart(e),a.src=e,a}}class iM extends Ls{constructor(e){super(e)}load(e,t,n,s){const r=new Qt,o=new nM(this.manager);return o.setCrossOrigin(this.crossOrigin),o.setPath(this.path),o.load(e,function(a){r.image=a,r.needsUpdate=!0,t!==void 0&&t(r)},n,s),r}}class Sh extends Nt{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new Ve(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}const Uc=new Ae,hd=new v,ud=new v;class Eh{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new te(512,512),this.map=null,this.mapPass=null,this.matrix=new Ae,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new hh,this._frameExtents=new te(1,1),this._viewportCount=1,this._viewports=[new yt(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;hd.setFromMatrixPosition(e.matrixWorld),t.position.copy(hd),ud.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(ud),t.updateMatrixWorld(),Uc.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Uc),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(Uc)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class sM extends Eh{constructor(){super(new Tn(50,1,.5,500)),this.isSpotLightShadow=!0,this.focus=1}updateMatrices(e){const t=this.camera,n=pr*2*e.angle*this.focus,s=this.mapSize.width/this.mapSize.height,r=e.distance||t.far;(n!==t.fov||s!==t.aspect||r!==t.far)&&(t.fov=n,t.aspect=s,t.far=r,t.updateProjectionMatrix()),super.updateMatrices(e)}copy(e){return super.copy(e),this.focus=e.focus,this}}class rM extends Sh{constructor(e,t,n=0,s=Math.PI/3,r=0,o=2){super(e,t),this.isSpotLight=!0,this.type="SpotLight",this.position.copy(Nt.DEFAULT_UP),this.updateMatrix(),this.target=new Nt,this.distance=n,this.angle=s,this.penumbra=r,this.decay=o,this.map=null,this.shadow=new sM}get power(){return this.intensity*Math.PI}set power(e){this.intensity=e/Math.PI}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.angle=e.angle,this.penumbra=e.penumbra,this.decay=e.decay,this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}const dd=new Ae,kr=new v,Oc=new v;class oM extends Eh{constructor(){super(new Tn(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new te(4,2),this._viewportCount=6,this._viewports=[new yt(2,1,1,1),new yt(0,1,1,1),new yt(3,1,1,1),new yt(1,1,1,1),new yt(3,0,1,1),new yt(1,0,1,1)],this._cubeDirections=[new v(1,0,0),new v(-1,0,0),new v(0,0,1),new v(0,0,-1),new v(0,1,0),new v(0,-1,0)],this._cubeUps=[new v(0,1,0),new v(0,1,0),new v(0,1,0),new v(0,1,0),new v(0,0,1),new v(0,0,-1)]}updateMatrices(e,t=0){const n=this.camera,s=this.matrix,r=e.distance||n.far;r!==n.far&&(n.far=r,n.updateProjectionMatrix()),kr.setFromMatrixPosition(e.matrixWorld),n.position.copy(kr),Oc.copy(n.position),Oc.add(this._cubeDirections[t]),n.up.copy(this._cubeUps[t]),n.lookAt(Oc),n.updateMatrixWorld(),s.makeTranslation(-kr.x,-kr.y,-kr.z),dd.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(dd)}}class aM extends Sh{constructor(e,t,n=0,s=2){super(e,t),this.isPointLight=!0,this.type="PointLight",this.distance=n,this.decay=s,this.shadow=new oM}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}}class cM extends Eh{constructor(){super(new Oa(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class lM extends Sh{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(Nt.DEFAULT_UP),this.updateMatrix(),this.target=new Nt,this.shadow=new cM}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class eo{static decodeText(e){if(console.warn("THREE.LoaderUtils: decodeText() has been deprecated with r165 and will be removed with r175. Use TextDecoder instead."),typeof TextDecoder<"u")return new TextDecoder().decode(e);let t="";for(let n=0,s=e.length;n<s;n++)t+=String.fromCharCode(e[n]);try{return decodeURIComponent(escape(t))}catch{return t}}static extractUrlBase(e){const t=e.lastIndexOf("/");return t===-1?"./":e.slice(0,t+1)}static resolveURL(e,t){return typeof e!="string"||e===""?"":(/^https?:\/\//i.test(t)&&/^\//.test(e)&&(t=t.replace(/(^https?:\/\/[^\/]+).*/i,"$1")),/^(https?:)?\/\//i.test(e)||/^data:.*,.*$/i.test(e)||/^blob:.*$/i.test(e)?e:t+e)}}class hM extends Ls{constructor(e){super(e),this.isImageBitmapLoader=!0,typeof createImageBitmap>"u"&&console.warn("THREE.ImageBitmapLoader: createImageBitmap() not supported."),typeof fetch>"u"&&console.warn("THREE.ImageBitmapLoader: fetch() not supported."),this.options={premultiplyAlpha:"none"}}setOptions(e){return this.options=e,this}load(e,t,n,s){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const r=this,o=ji.get(e);if(o!==void 0){if(r.manager.itemStart(e),o.then){o.then(l=>{t&&t(l),r.manager.itemEnd(e)}).catch(l=>{s&&s(l)});return}return setTimeout(function(){t&&t(o),r.manager.itemEnd(e)},0),o}const a={};a.credentials=this.crossOrigin==="anonymous"?"same-origin":"include",a.headers=this.requestHeader;const c=fetch(e,a).then(function(l){return l.blob()}).then(function(l){return createImageBitmap(l,Object.assign(r.options,{colorSpaceConversion:"none"}))}).then(function(l){return ji.add(e,l),t&&t(l),r.manager.itemEnd(e),l}).catch(function(l){s&&s(l),ji.remove(e),r.manager.itemError(e),r.manager.itemEnd(e)});ji.add(e,c),r.manager.itemStart(e)}}const Th="\\[\\]\\.:\\/",uM=new RegExp("["+Th+"]","g"),Ah="[^"+Th+"]",dM="[^"+Th.replace("\\.","")+"]",fM=/((?:WC+[\/:])*)/.source.replace("WC",Ah),pM=/(WCOD+)?/.source.replace("WCOD",dM),mM=/(?:\.(WC+)(?:\[(.+)\])?)?/.source.replace("WC",Ah),gM=/\.(WC+)(?:\[(.+)\])?/.source.replace("WC",Ah),_M=new RegExp("^"+fM+pM+mM+gM+"$"),xM=["material","materials","bones","map"];class vM{constructor(e,t,n){const s=n||At.parseTrackName(t);this._targetGroup=e,this._bindings=e.subscribe_(t,s)}getValue(e,t){this.bind();const n=this._targetGroup.nCachedObjects_,s=this._bindings[n];s!==void 0&&s.getValue(e,t)}setValue(e,t){const n=this._bindings;for(let s=this._targetGroup.nCachedObjects_,r=n.length;s!==r;++s)n[s].setValue(e,t)}bind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].bind()}unbind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].unbind()}}class At{constructor(e,t,n){this.path=t,this.parsedPath=n||At.parseTrackName(t),this.node=At.findNode(e,this.parsedPath.nodeName),this.rootNode=e,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}static create(e,t,n){return e&&e.isAnimationObjectGroup?new At.Composite(e,t,n):new At(e,t,n)}static sanitizeNodeName(e){return e.replace(/\s/g,"_").replace(uM,"")}static parseTrackName(e){const t=_M.exec(e);if(t===null)throw new Error("PropertyBinding: Cannot parse trackName: "+e);const n={nodeName:t[2],objectName:t[3],objectIndex:t[4],propertyName:t[5],propertyIndex:t[6]},s=n.nodeName&&n.nodeName.lastIndexOf(".");if(s!==void 0&&s!==-1){const r=n.nodeName.substring(s+1);xM.indexOf(r)!==-1&&(n.nodeName=n.nodeName.substring(0,s),n.objectName=r)}if(n.propertyName===null||n.propertyName.length===0)throw new Error("PropertyBinding: can not parse propertyName from trackName: "+e);return n}static findNode(e,t){if(t===void 0||t===""||t==="."||t===-1||t===e.name||t===e.uuid)return e;if(e.skeleton){const n=e.skeleton.getBoneByName(t);if(n!==void 0)return n}if(e.children){const n=function(r){for(let o=0;o<r.length;o++){const a=r[o];if(a.name===t||a.uuid===t)return a;const c=n(a.children);if(c)return c}return null},s=n(e.children);if(s)return s}return null}_getValue_unavailable(){}_setValue_unavailable(){}_getValue_direct(e,t){e[t]=this.targetObject[this.propertyName]}_getValue_array(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)e[t++]=n[s]}_getValue_arrayElement(e,t){e[t]=this.resolvedProperty[this.propertyIndex]}_getValue_toArray(e,t){this.resolvedProperty.toArray(e,t)}_setValue_direct(e,t){this.targetObject[this.propertyName]=e[t]}_setValue_direct_setNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.needsUpdate=!0}_setValue_direct_setMatrixWorldNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_array(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)n[s]=e[t++]}_setValue_array_setNeedsUpdate(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)n[s]=e[t++];this.targetObject.needsUpdate=!0}_setValue_array_setMatrixWorldNeedsUpdate(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)n[s]=e[t++];this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_arrayElement(e,t){this.resolvedProperty[this.propertyIndex]=e[t]}_setValue_arrayElement_setNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.needsUpdate=!0}_setValue_arrayElement_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_fromArray(e,t){this.resolvedProperty.fromArray(e,t)}_setValue_fromArray_setNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.needsUpdate=!0}_setValue_fromArray_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.matrixWorldNeedsUpdate=!0}_getValue_unbound(e,t){this.bind(),this.getValue(e,t)}_setValue_unbound(e,t){this.bind(),this.setValue(e,t)}bind(){let e=this.node;const t=this.parsedPath,n=t.objectName,s=t.propertyName;let r=t.propertyIndex;if(e||(e=At.findNode(this.rootNode,t.nodeName),this.node=e),this.getValue=this._getValue_unavailable,this.setValue=this._setValue_unavailable,!e){console.warn("THREE.PropertyBinding: No target node found for track: "+this.path+".");return}if(n){let l=t.objectIndex;switch(n){case"materials":if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.materials){console.error("THREE.PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.",this);return}e=e.material.materials;break;case"bones":if(!e.skeleton){console.error("THREE.PropertyBinding: Can not bind to bones as node does not have a skeleton.",this);return}e=e.skeleton.bones;for(let h=0;h<e.length;h++)if(e[h].name===l){l=h;break}break;case"map":if("map"in e){e=e.map;break}if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.map){console.error("THREE.PropertyBinding: Can not bind to material.map as node.material does not have a map.",this);return}e=e.material.map;break;default:if(e[n]===void 0){console.error("THREE.PropertyBinding: Can not bind to objectName of node undefined.",this);return}e=e[n]}if(l!==void 0){if(e[l]===void 0){console.error("THREE.PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.",this,e);return}e=e[l]}}const o=e[s];if(o===void 0){const l=t.nodeName;console.error("THREE.PropertyBinding: Trying to update property for track: "+l+"."+s+" but it wasn't found.",e);return}let a=this.Versioning.None;this.targetObject=e,e.needsUpdate!==void 0?a=this.Versioning.NeedsUpdate:e.matrixWorldNeedsUpdate!==void 0&&(a=this.Versioning.MatrixWorldNeedsUpdate);let c=this.BindingType.Direct;if(r!==void 0){if(s==="morphTargetInfluences"){if(!e.geometry){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.",this);return}if(!e.geometry.morphAttributes){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.",this);return}e.morphTargetDictionary[r]!==void 0&&(r=e.morphTargetDictionary[r])}c=this.BindingType.ArrayElement,this.resolvedProperty=o,this.propertyIndex=r}else o.fromArray!==void 0&&o.toArray!==void 0?(c=this.BindingType.HasFromToArray,this.resolvedProperty=o):Array.isArray(o)?(c=this.BindingType.EntireArray,this.resolvedProperty=o):this.propertyName=s;this.getValue=this.GetterByBindingType[c],this.setValue=this.SetterByBindingTypeAndVersioning[c][a]}unbind(){this.node=null,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}}At.Composite=vM;At.prototype.BindingType={Direct:0,EntireArray:1,ArrayElement:2,HasFromToArray:3};At.prototype.Versioning={None:0,NeedsUpdate:1,MatrixWorldNeedsUpdate:2};At.prototype.GetterByBindingType=[At.prototype._getValue_direct,At.prototype._getValue_array,At.prototype._getValue_arrayElement,At.prototype._getValue_toArray];At.prototype.SetterByBindingTypeAndVersioning=[[At.prototype._setValue_direct,At.prototype._setValue_direct_setNeedsUpdate,At.prototype._setValue_direct_setMatrixWorldNeedsUpdate],[At.prototype._setValue_array,At.prototype._setValue_array_setNeedsUpdate,At.prototype._setValue_array_setMatrixWorldNeedsUpdate],[At.prototype._setValue_arrayElement,At.prototype._setValue_arrayElement_setNeedsUpdate,At.prototype._setValue_arrayElement_setMatrixWorldNeedsUpdate],[At.prototype._setValue_fromArray,At.prototype._setValue_fromArray_setNeedsUpdate,At.prototype._setValue_fromArray_setMatrixWorldNeedsUpdate]];typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:eh}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=eh);const yM=12,MM=Ft.degToRad(yM),wM=1e-7,bM=1e-7,SM=new v(1,1,1),Nf=i=>new Ae().makeTranslation(i.x,i.y,i.z),fd=(i,e,t)=>e.get(t).clone().multiply(Nf(i.heads.get(t)));function Fc(i,e,t){const n=i.parents.get(t),s=fd(i,e,t);return n?fd(i,e,n).invert().multiply(s):s}const Bc=i=>{const e=new v,t=new Gn,n=new v;return i.decompose(e,t,n),{at:e,turn:t}};function EM(i,e,t,n,s=e,r=MM){const o=new Map,a=new Map;let c=n>=1;for(const l of i.order){const h=Bc(Fc(i,e,l)),u=Bc(Fc(i,t,l)),d=Bc(Fc(i,s,l)),f=h.at.lerp(u.at,n),m=h.turn.slerp(u.turn,n),_=d.turn.angleTo(m),g=d.turn.slerp(m,_>r?r/_:1),p=new Ae().compose(f,g,SM),y=i.parents.get(l),M=y?o.get(y).clone().multiply(p):p;o.set(l,M),a.set(l,M.clone().multiply(Nf(i.heads.get(l).clone().negate()))),c&&(c=g.angleTo(u.turn)<wM&&f.distanceTo(u.at)<bM)}return{moves:a,settled:c}}const xn={hat:{base:3.62,crown:.86,height:1,brim:.2,thick:.05,curl:.18,band:[.04,.24],bandOut:.015,sides:48},white:[.97,.97,.95],whites:["hand_shell_l","hand_shell_r","butler_bow_tie__knot","butler_bow_tie__loop_l","butler_bow_tie__loop_r","butler_shirt__collar_band","butler_shirt__collar_point_l","butler_shirt__collar_point_r"],wing:{points:[[.04,2.47],[.19,2.45],[.09,2.36]],z:.43,thick:.02},tails:{side:[[-.3,1.78],[-.47,1.78],[-.68,.72],[-.58,.72]],across:[.04,.36]},satin:[.15,.15,.24],removed:["butler_bowler_hat","butler_tailcoat__tail_l","butler_tailcoat__tail_r"],satOn:["butler_tail_l","butler_tail_r"]};function na(i,e,t,n){t.applyMatrix4(i.matrixWorld.clone().invert());const s=t.attributes.position.count,r=i.geometry.attributes.skinIndex.getX(0);t.setAttribute("skinIndex",new lh(Array.from({length:s*4},(a,c)=>c%4?0:r),4)),t.setAttribute("skinWeight",new ct(Array.from({length:s*4},(a,c)=>c%4?0:1),4));const o=new fh(t,new fn({color:new Ve(...n)}));return o.name=e,o.userData={item:e},o.position.copy(i.position),o.quaternion.copy(i.quaternion),o.scale.copy(i.scale),i.parent.add(o),o.bind(i.skeleton,i.bindMatrix),o.updateMatrixWorld(!0),o}function Uf(){const{crown:i,height:e,brim:t,thick:n,curl:s,sides:r}=xn.hat,o=i+t,a=[[.001,0],[o,0],[o,n],[i,n],[i,e],[.001,e]],c=new br(a.map(([h,u])=>new te(h,u)),r),l=c.attributes.position;for(let h=0;h<l.count;h++){const[u,d,f]=[l.getX(h),l.getY(h),l.getZ(h)],m=Math.hypot(u,f);d<=n+1e-6&&m>i&&l.setY(h,d+s*((m-i)/t)**2*(u/m)**2)}return c.computeVertexNormals(),c}function Of(){const{crown:i,band:e,bandOut:t,sides:n}=xn.hat,s=new et(i+t,i+t,e[1]-e[0],n,1,!0);return s.translate(0,(e[0]+e[1])/2,0),s}function TM(i){const{points:e,z:t,thick:n}=xn.wing,s=new Ps(e.map(([o,a])=>new te(i*o,a))),r=new po(s,{depth:n,bevelEnabled:!1});return r.translate(0,0,t),r}function AM(i){const{side:e,across:t}=xn.tails,n=new Ps(e.map(([r,o])=>new te(r,o))),s=new po(n,{depth:t[1]-t[0],bevelEnabled:!1});return s.rotateY(-Math.PI/2),s.translate(i>0?t[1]:-.04,0,0),s.computeVertexNormals(),s}function RM(i){const e=h=>i.find(u=>u.name===h);for(const h of i.filter(u=>xn.whites.includes(u.name)))h.material=h.material.clone(),h.material.color.setRGB(...xn.white);const t=e("butler_bowler_hat__crown"),n=new tn().setFromObject(t).getCenter(new v),s=t.material.color.toArray(),r=e("butler_tailcoat__body").material.color.toArray(),o=e("butler_bow_tie__knot"),a=e("butler_tailcoat__tail_l"),c=[na(t,"butler_top_hat",Uf().translate(n.x,xn.hat.base,n.z),s),na(t,"butler_top_hat_band",Of().translate(n.x,xn.hat.base,n.z),xn.satin),...[1,-1].map(h=>na(o,`butler_wing_collar_${h>0?"l":"r"}`,TM(h),xn.white)),...[1,-1].map(h=>na(a,`butler_tail_${h>0?"l":"r"}`,AM(h),r))],l=i.filter(h=>xn.removed.some(u=>h.name.startsWith(u)));for(const h of l)h.parent.remove(h);return[...i.filter(h=>!l.includes(h)),...c]}function pd(i,e){if(e===wm)return console.warn("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles."),i;if(e===Bl||e===nf){let t=i.getIndex();if(t===null){const o=[],a=i.getAttribute("position");if(a!==void 0){for(let c=0;c<a.count;c++)o.push(c);i.setIndex(o),t=i.getIndex()}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible."),i}const n=t.count-2,s=[];if(e===Bl)for(let o=1;o<=n;o++)s.push(t.getX(0)),s.push(t.getX(o)),s.push(t.getX(o+1));else for(let o=0;o<n;o++)o%2===0?(s.push(t.getX(o)),s.push(t.getX(o+1)),s.push(t.getX(o+2))):(s.push(t.getX(o+2)),s.push(t.getX(o+1)),s.push(t.getX(o)));s.length/3!==n&&console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.");const r=i.clone();return r.setIndex(s),r.clearGroups(),r}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:",e),i}class CM extends Ls{constructor(e){super(e),this.dracoLoader=null,this.ktx2Loader=null,this.meshoptDecoder=null,this.pluginCallbacks=[],this.register(function(t){return new NM(t)}),this.register(function(t){return new UM(t)}),this.register(function(t){return new WM(t)}),this.register(function(t){return new XM(t)}),this.register(function(t){return new qM(t)}),this.register(function(t){return new FM(t)}),this.register(function(t){return new BM(t)}),this.register(function(t){return new kM(t)}),this.register(function(t){return new zM(t)}),this.register(function(t){return new DM(t)}),this.register(function(t){return new HM(t)}),this.register(function(t){return new OM(t)}),this.register(function(t){return new VM(t)}),this.register(function(t){return new GM(t)}),this.register(function(t){return new LM(t)}),this.register(function(t){return new jM(t)}),this.register(function(t){return new $M(t)})}load(e,t,n,s){const r=this;let o;if(this.resourcePath!=="")o=this.resourcePath;else if(this.path!==""){const l=eo.extractUrlBase(e);o=eo.resolveURL(l,this.path)}else o=eo.extractUrlBase(e);this.manager.itemStart(e);const a=function(l){s?s(l):console.error(l),r.manager.itemError(e),r.manager.itemEnd(e)},c=new Ta(this.manager);c.setPath(this.path),c.setResponseType("arraybuffer"),c.setRequestHeader(this.requestHeader),c.setWithCredentials(this.withCredentials),c.load(e,function(l){try{r.parse(l,o,function(h){t(h),r.manager.itemEnd(e)},a)}catch(h){a(h)}},n,a)}setDRACOLoader(e){return this.dracoLoader=e,this}setKTX2Loader(e){return this.ktx2Loader=e,this}setMeshoptDecoder(e){return this.meshoptDecoder=e,this}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,s){let r;const o={},a={},c=new TextDecoder;if(typeof e=="string")r=JSON.parse(e);else if(e instanceof ArrayBuffer)if(c.decode(new Uint8Array(e,0,4))===Ff){try{o[ut.KHR_BINARY_GLTF]=new YM(e)}catch(u){s&&s(u);return}r=JSON.parse(o[ut.KHR_BINARY_GLTF].content)}else r=JSON.parse(c.decode(e));else r=e;if(r.asset===void 0||r.asset.version[0]<2){s&&s(new Error("THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported."));return}const l=new cw(r,{path:t||this.resourcePath||"",crossOrigin:this.crossOrigin,requestHeader:this.requestHeader,manager:this.manager,ktx2Loader:this.ktx2Loader,meshoptDecoder:this.meshoptDecoder});l.fileLoader.setRequestHeader(this.requestHeader);for(let h=0;h<this.pluginCallbacks.length;h++){const u=this.pluginCallbacks[h](l);u.name||console.error("THREE.GLTFLoader: Invalid plugin found: missing name"),a[u.name]=u,o[u.name]=!0}if(r.extensionsUsed)for(let h=0;h<r.extensionsUsed.length;++h){const u=r.extensionsUsed[h],d=r.extensionsRequired||[];switch(u){case ut.KHR_MATERIALS_UNLIT:o[u]=new IM;break;case ut.KHR_DRACO_MESH_COMPRESSION:o[u]=new KM(r,this.dracoLoader);break;case ut.KHR_TEXTURE_TRANSFORM:o[u]=new ZM;break;case ut.KHR_MESH_QUANTIZATION:o[u]=new JM;break;default:d.indexOf(u)>=0&&a[u]===void 0&&console.warn('THREE.GLTFLoader: Unknown extension "'+u+'".')}}l.setExtensions(o),l.setPlugins(a),l.parse(n,s)}parseAsync(e,t){const n=this;return new Promise(function(s,r){n.parse(e,t,s,r)})}}function PM(){let i={};return{get:function(e){return i[e]},add:function(e,t){i[e]=t},remove:function(e){delete i[e]},removeAll:function(){i={}}}}const ut={KHR_BINARY_GLTF:"KHR_binary_glTF",KHR_DRACO_MESH_COMPRESSION:"KHR_draco_mesh_compression",KHR_LIGHTS_PUNCTUAL:"KHR_lights_punctual",KHR_MATERIALS_CLEARCOAT:"KHR_materials_clearcoat",KHR_MATERIALS_DISPERSION:"KHR_materials_dispersion",KHR_MATERIALS_IOR:"KHR_materials_ior",KHR_MATERIALS_SHEEN:"KHR_materials_sheen",KHR_MATERIALS_SPECULAR:"KHR_materials_specular",KHR_MATERIALS_TRANSMISSION:"KHR_materials_transmission",KHR_MATERIALS_IRIDESCENCE:"KHR_materials_iridescence",KHR_MATERIALS_ANISOTROPY:"KHR_materials_anisotropy",KHR_MATERIALS_UNLIT:"KHR_materials_unlit",KHR_MATERIALS_VOLUME:"KHR_materials_volume",KHR_TEXTURE_BASISU:"KHR_texture_basisu",KHR_TEXTURE_TRANSFORM:"KHR_texture_transform",KHR_MESH_QUANTIZATION:"KHR_mesh_quantization",KHR_MATERIALS_EMISSIVE_STRENGTH:"KHR_materials_emissive_strength",EXT_MATERIALS_BUMP:"EXT_materials_bump",EXT_TEXTURE_WEBP:"EXT_texture_webp",EXT_TEXTURE_AVIF:"EXT_texture_avif",EXT_MESHOPT_COMPRESSION:"EXT_meshopt_compression",EXT_MESH_GPU_INSTANCING:"EXT_mesh_gpu_instancing"};class LM{constructor(e){this.parser=e,this.name=ut.KHR_LIGHTS_PUNCTUAL,this.cache={refs:{},uses:{}}}_markDefs(){const e=this.parser,t=this.parser.json.nodes||[];for(let n=0,s=t.length;n<s;n++){const r=t[n];r.extensions&&r.extensions[this.name]&&r.extensions[this.name].light!==void 0&&e._addNodeRef(this.cache,r.extensions[this.name].light)}}_loadLight(e){const t=this.parser,n="light:"+e;let s=t.cache.get(n);if(s)return s;const r=t.json,c=((r.extensions&&r.extensions[this.name]||{}).lights||[])[e];let l;const h=new Ve(16777215);c.color!==void 0&&h.setRGB(c.color[0],c.color[1],c.color[2],mn);const u=c.range!==void 0?c.range:0;switch(c.type){case"directional":l=new lM(h),l.target.position.set(0,0,-1),l.add(l.target);break;case"point":l=new aM(h),l.distance=u;break;case"spot":l=new rM(h),l.distance=u,c.spot=c.spot||{},c.spot.innerConeAngle=c.spot.innerConeAngle!==void 0?c.spot.innerConeAngle:0,c.spot.outerConeAngle=c.spot.outerConeAngle!==void 0?c.spot.outerConeAngle:Math.PI/4,l.angle=c.spot.outerConeAngle,l.penumbra=1-c.spot.innerConeAngle/c.spot.outerConeAngle,l.target.position.set(0,0,-1),l.add(l.target);break;default:throw new Error("THREE.GLTFLoader: Unexpected light type: "+c.type)}return l.position.set(0,0,0),l.decay=2,wi(l,c),c.intensity!==void 0&&(l.intensity=c.intensity),l.name=t.createUniqueName(c.name||"light_"+e),s=Promise.resolve(l),t.cache.add(n,s),s}getDependency(e,t){if(e==="light")return this._loadLight(t)}createNodeAttachment(e){const t=this,n=this.parser,r=n.json.nodes[e],a=(r.extensions&&r.extensions[this.name]||{}).light;return a===void 0?null:this._loadLight(a).then(function(c){return n._getNodeRef(t.cache,a,c)})}}class IM{constructor(){this.name=ut.KHR_MATERIALS_UNLIT}getMaterialType(){return fn}extendParams(e,t,n){const s=[];e.color=new Ve(1,1,1),e.opacity=1;const r=t.pbrMetallicRoughness;if(r){if(Array.isArray(r.baseColorFactor)){const o=r.baseColorFactor;e.color.setRGB(o[0],o[1],o[2],mn),e.opacity=o[3]}r.baseColorTexture!==void 0&&s.push(n.assignTexture(e,"map",r.baseColorTexture,qt))}return Promise.all(s)}}class DM{constructor(e){this.parser=e,this.name=ut.KHR_MATERIALS_EMISSIVE_STRENGTH}extendMaterialParams(e,t){const s=this.parser.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=s.extensions[this.name].emissiveStrength;return r!==void 0&&(t.emissiveIntensity=r),Promise.resolve()}}class NM{constructor(e){this.parser=e,this.name=ut.KHR_MATERIALS_CLEARCOAT}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:hi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];if(o.clearcoatFactor!==void 0&&(t.clearcoat=o.clearcoatFactor),o.clearcoatTexture!==void 0&&r.push(n.assignTexture(t,"clearcoatMap",o.clearcoatTexture)),o.clearcoatRoughnessFactor!==void 0&&(t.clearcoatRoughness=o.clearcoatRoughnessFactor),o.clearcoatRoughnessTexture!==void 0&&r.push(n.assignTexture(t,"clearcoatRoughnessMap",o.clearcoatRoughnessTexture)),o.clearcoatNormalTexture!==void 0&&(r.push(n.assignTexture(t,"clearcoatNormalMap",o.clearcoatNormalTexture)),o.clearcoatNormalTexture.scale!==void 0)){const a=o.clearcoatNormalTexture.scale;t.clearcoatNormalScale=new te(a,a)}return Promise.all(r)}}class UM{constructor(e){this.parser=e,this.name=ut.KHR_MATERIALS_DISPERSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:hi}extendMaterialParams(e,t){const s=this.parser.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=s.extensions[this.name];return t.dispersion=r.dispersion!==void 0?r.dispersion:0,Promise.resolve()}}class OM{constructor(e){this.parser=e,this.name=ut.KHR_MATERIALS_IRIDESCENCE}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:hi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return o.iridescenceFactor!==void 0&&(t.iridescence=o.iridescenceFactor),o.iridescenceTexture!==void 0&&r.push(n.assignTexture(t,"iridescenceMap",o.iridescenceTexture)),o.iridescenceIor!==void 0&&(t.iridescenceIOR=o.iridescenceIor),t.iridescenceThicknessRange===void 0&&(t.iridescenceThicknessRange=[100,400]),o.iridescenceThicknessMinimum!==void 0&&(t.iridescenceThicknessRange[0]=o.iridescenceThicknessMinimum),o.iridescenceThicknessMaximum!==void 0&&(t.iridescenceThicknessRange[1]=o.iridescenceThicknessMaximum),o.iridescenceThicknessTexture!==void 0&&r.push(n.assignTexture(t,"iridescenceThicknessMap",o.iridescenceThicknessTexture)),Promise.all(r)}}class FM{constructor(e){this.parser=e,this.name=ut.KHR_MATERIALS_SHEEN}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:hi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[];t.sheenColor=new Ve(0,0,0),t.sheenRoughness=0,t.sheen=1;const o=s.extensions[this.name];if(o.sheenColorFactor!==void 0){const a=o.sheenColorFactor;t.sheenColor.setRGB(a[0],a[1],a[2],mn)}return o.sheenRoughnessFactor!==void 0&&(t.sheenRoughness=o.sheenRoughnessFactor),o.sheenColorTexture!==void 0&&r.push(n.assignTexture(t,"sheenColorMap",o.sheenColorTexture,qt)),o.sheenRoughnessTexture!==void 0&&r.push(n.assignTexture(t,"sheenRoughnessMap",o.sheenRoughnessTexture)),Promise.all(r)}}class BM{constructor(e){this.parser=e,this.name=ut.KHR_MATERIALS_TRANSMISSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:hi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return o.transmissionFactor!==void 0&&(t.transmission=o.transmissionFactor),o.transmissionTexture!==void 0&&r.push(n.assignTexture(t,"transmissionMap",o.transmissionTexture)),Promise.all(r)}}class kM{constructor(e){this.parser=e,this.name=ut.KHR_MATERIALS_VOLUME}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:hi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];t.thickness=o.thicknessFactor!==void 0?o.thicknessFactor:0,o.thicknessTexture!==void 0&&r.push(n.assignTexture(t,"thicknessMap",o.thicknessTexture)),t.attenuationDistance=o.attenuationDistance||1/0;const a=o.attenuationColor||[1,1,1];return t.attenuationColor=new Ve().setRGB(a[0],a[1],a[2],mn),Promise.all(r)}}class zM{constructor(e){this.parser=e,this.name=ut.KHR_MATERIALS_IOR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:hi}extendMaterialParams(e,t){const s=this.parser.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=s.extensions[this.name];return t.ior=r.ior!==void 0?r.ior:1.5,Promise.resolve()}}class HM{constructor(e){this.parser=e,this.name=ut.KHR_MATERIALS_SPECULAR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:hi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];t.specularIntensity=o.specularFactor!==void 0?o.specularFactor:1,o.specularTexture!==void 0&&r.push(n.assignTexture(t,"specularIntensityMap",o.specularTexture));const a=o.specularColorFactor||[1,1,1];return t.specularColor=new Ve().setRGB(a[0],a[1],a[2],mn),o.specularColorTexture!==void 0&&r.push(n.assignTexture(t,"specularColorMap",o.specularColorTexture,qt)),Promise.all(r)}}class GM{constructor(e){this.parser=e,this.name=ut.EXT_MATERIALS_BUMP}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:hi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return t.bumpScale=o.bumpFactor!==void 0?o.bumpFactor:1,o.bumpTexture!==void 0&&r.push(n.assignTexture(t,"bumpMap",o.bumpTexture)),Promise.all(r)}}class VM{constructor(e){this.parser=e,this.name=ut.KHR_MATERIALS_ANISOTROPY}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:hi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return o.anisotropyStrength!==void 0&&(t.anisotropy=o.anisotropyStrength),o.anisotropyRotation!==void 0&&(t.anisotropyRotation=o.anisotropyRotation),o.anisotropyTexture!==void 0&&r.push(n.assignTexture(t,"anisotropyMap",o.anisotropyTexture)),Promise.all(r)}}class WM{constructor(e){this.parser=e,this.name=ut.KHR_TEXTURE_BASISU}loadTexture(e){const t=this.parser,n=t.json,s=n.textures[e];if(!s.extensions||!s.extensions[this.name])return null;const r=s.extensions[this.name],o=t.options.ktx2Loader;if(!o){if(n.extensionsRequired&&n.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setKTX2Loader must be called before loading KTX2 textures");return null}return t.loadTextureImage(e,r.source,o)}}class XM{constructor(e){this.parser=e,this.name=ut.EXT_TEXTURE_WEBP,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,s=n.json,r=s.textures[e];if(!r.extensions||!r.extensions[t])return null;const o=r.extensions[t],a=s.images[o.source];let c=n.textureLoader;if(a.uri){const l=n.options.manager.getHandler(a.uri);l!==null&&(c=l)}return this.detectSupport().then(function(l){if(l)return n.loadTextureImage(e,o.source,c);if(s.extensionsRequired&&s.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: WebP required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class qM{constructor(e){this.parser=e,this.name=ut.EXT_TEXTURE_AVIF,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,s=n.json,r=s.textures[e];if(!r.extensions||!r.extensions[t])return null;const o=r.extensions[t],a=s.images[o.source];let c=n.textureLoader;if(a.uri){const l=n.options.manager.getHandler(a.uri);l!==null&&(c=l)}return this.detectSupport().then(function(l){if(l)return n.loadTextureImage(e,o.source,c);if(s.extensionsRequired&&s.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: AVIF required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAABcAAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAEAAAABAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQAMAAAAABNjb2xybmNseAACAAIABoAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAAB9tZGF0EgAKCBgABogQEDQgMgkQAAAAB8dSLfI=",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class jM{constructor(e){this.name=ut.EXT_MESHOPT_COMPRESSION,this.parser=e}loadBufferView(e){const t=this.parser.json,n=t.bufferViews[e];if(n.extensions&&n.extensions[this.name]){const s=n.extensions[this.name],r=this.parser.getDependency("buffer",s.buffer),o=this.parser.options.meshoptDecoder;if(!o||!o.supported){if(t.extensionsRequired&&t.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files");return null}return r.then(function(a){const c=s.byteOffset||0,l=s.byteLength||0,h=s.count,u=s.byteStride,d=new Uint8Array(a,c,l);return o.decodeGltfBufferAsync?o.decodeGltfBufferAsync(h,u,d,s.mode,s.filter).then(function(f){return f.buffer}):o.ready.then(function(){const f=new ArrayBuffer(h*u);return o.decodeGltfBuffer(new Uint8Array(f),h,u,d,s.mode,s.filter),f})})}else return null}}class $M{constructor(e){this.name=ut.EXT_MESH_GPU_INSTANCING,this.parser=e}createNodeMesh(e){const t=this.parser.json,n=t.nodes[e];if(!n.extensions||!n.extensions[this.name]||n.mesh===void 0)return null;const s=t.meshes[n.mesh];for(const l of s.primitives)if(l.mode!==Fn.TRIANGLES&&l.mode!==Fn.TRIANGLE_STRIP&&l.mode!==Fn.TRIANGLE_FAN&&l.mode!==void 0)return null;const o=n.extensions[this.name].attributes,a=[],c={};for(const l in o)a.push(this.parser.getDependency("accessor",o[l]).then(h=>(c[l]=h,c[l])));return a.length<1?null:(a.push(this.parser.createNodeMesh(e)),Promise.all(a).then(l=>{const h=l.pop(),u=h.isGroup?h.children:[h],d=l[0].count,f=[];for(const m of u){const _=new Ae,g=new v,p=new Gn,y=new v(1,1,1),M=new dy(m.geometry,m.material,d);for(let x=0;x<d;x++)c.TRANSLATION&&g.fromBufferAttribute(c.TRANSLATION,x),c.ROTATION&&p.fromBufferAttribute(c.ROTATION,x),c.SCALE&&y.fromBufferAttribute(c.SCALE,x),M.setMatrixAt(x,_.compose(g,p,y));for(const x in c)if(x==="_COLOR_0"){const E=c[x];M.instanceColor=new Hl(E.array,E.itemSize,E.normalized)}else x!=="TRANSLATION"&&x!=="ROTATION"&&x!=="SCALE"&&m.geometry.setAttribute(x,c[x]);Nt.prototype.copy.call(M,m),this.parser.assignFinalMaterial(M),f.push(M)}return h.isGroup?(h.clear(),h.add(...f),h):f[0]}))}}const Ff="glTF",zr=12,md={JSON:1313821514,BIN:5130562};class YM{constructor(e){this.name=ut.KHR_BINARY_GLTF,this.content=null,this.body=null;const t=new DataView(e,0,zr),n=new TextDecoder;if(this.header={magic:n.decode(new Uint8Array(e.slice(0,4))),version:t.getUint32(4,!0),length:t.getUint32(8,!0)},this.header.magic!==Ff)throw new Error("THREE.GLTFLoader: Unsupported glTF-Binary header.");if(this.header.version<2)throw new Error("THREE.GLTFLoader: Legacy binary file detected.");const s=this.header.length-zr,r=new DataView(e,zr);let o=0;for(;o<s;){const a=r.getUint32(o,!0);o+=4;const c=r.getUint32(o,!0);if(o+=4,c===md.JSON){const l=new Uint8Array(e,zr+o,a);this.content=n.decode(l)}else if(c===md.BIN){const l=zr+o;this.body=e.slice(l,l+a)}o+=a}if(this.content===null)throw new Error("THREE.GLTFLoader: JSON content not found.")}}class KM{constructor(e,t){if(!t)throw new Error("THREE.GLTFLoader: No DRACOLoader instance provided.");this.name=ut.KHR_DRACO_MESH_COMPRESSION,this.json=e,this.dracoLoader=t,this.dracoLoader.preload()}decodePrimitive(e,t){const n=this.json,s=this.dracoLoader,r=e.extensions[this.name].bufferView,o=e.extensions[this.name].attributes,a={},c={},l={};for(const h in o){const u=ql[h]||h.toLowerCase();a[u]=o[h]}for(const h in e.attributes){const u=ql[h]||h.toLowerCase();if(o[h]!==void 0){const d=n.accessors[e.attributes[h]],f=or[d.componentType];l[u]=f.name,c[u]=d.normalized===!0}}return t.getDependency("bufferView",r).then(function(h){return new Promise(function(u,d){s.decodeDracoFile(h,function(f){for(const m in f.attributes){const _=f.attributes[m],g=c[m];g!==void 0&&(_.normalized=g)}u(f)},a,l,mn,d)})})}}class ZM{constructor(){this.name=ut.KHR_TEXTURE_TRANSFORM}extendTexture(e,t){return(t.texCoord===void 0||t.texCoord===e.channel)&&t.offset===void 0&&t.rotation===void 0&&t.scale===void 0||(e=e.clone(),t.texCoord!==void 0&&(e.channel=t.texCoord),t.offset!==void 0&&e.offset.fromArray(t.offset),t.rotation!==void 0&&(e.rotation=t.rotation),t.scale!==void 0&&e.repeat.fromArray(t.scale),e.needsUpdate=!0),e}}class JM{constructor(){this.name=ut.KHR_MESH_QUANTIZATION}}class Bf extends mo{constructor(e,t,n,s){super(e,t,n,s)}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,s=this.valueSize,r=e*s*3+s;for(let o=0;o!==s;o++)t[o]=n[r+o];return t}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=a*2,l=a*3,h=s-t,u=(n-t)/h,d=u*u,f=d*u,m=e*l,_=m-l,g=-2*f+3*d,p=f-d,y=1-g,M=p-d+u;for(let x=0;x!==a;x++){const E=o[_+x+a],T=o[_+x+c]*h,P=o[m+x+a],C=o[m+x]*h;r[x]=y*E+M*T+g*P+p*C}return r}}const QM=new Gn;class ew extends Bf{interpolate_(e,t,n,s){const r=super.interpolate_(e,t,n,s);return QM.fromArray(r).normalize().toArray(r),r}}const Fn={POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6},or={5120:Int8Array,5121:Uint8Array,5122:Int16Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},gd={9728:pn,9729:Dn,9984:qd,9985:ha,9986:$r,9987:bi},_d={33071:qi,33648:Ma,10497:ur},kc={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16},ql={POSITION:"position",NORMAL:"normal",TANGENT:"tangent",TEXCOORD_0:"uv",TEXCOORD_1:"uv1",TEXCOORD_2:"uv2",TEXCOORD_3:"uv3",COLOR_0:"color",WEIGHTS_0:"skinWeight",JOINTS_0:"skinIndex"},Hi={scale:"scale",translation:"position",rotation:"quaternion",weights:"morphTargetInfluences"},tw={CUBICSPLINE:void 0,LINEAR:ro,STEP:so},zc={OPAQUE:"OPAQUE",MASK:"MASK",BLEND:"BLEND"};function nw(i){return i.DefaultMaterial===void 0&&(i.DefaultMaterial=new bh({color:16777215,emissive:0,metalness:1,roughness:1,transparent:!1,depthTest:!0,side:Ti})),i.DefaultMaterial}function us(i,e,t){for(const n in t.extensions)i[n]===void 0&&(e.userData.gltfExtensions=e.userData.gltfExtensions||{},e.userData.gltfExtensions[n]=t.extensions[n])}function wi(i,e){e.extras!==void 0&&(typeof e.extras=="object"?Object.assign(i.userData,e.extras):console.warn("THREE.GLTFLoader: Ignoring primitive type .extras, "+e.extras))}function iw(i,e,t){let n=!1,s=!1,r=!1;for(let l=0,h=e.length;l<h;l++){const u=e[l];if(u.POSITION!==void 0&&(n=!0),u.NORMAL!==void 0&&(s=!0),u.COLOR_0!==void 0&&(r=!0),n&&s&&r)break}if(!n&&!s&&!r)return Promise.resolve(i);const o=[],a=[],c=[];for(let l=0,h=e.length;l<h;l++){const u=e[l];if(n){const d=u.POSITION!==void 0?t.getDependency("accessor",u.POSITION):i.attributes.position;o.push(d)}if(s){const d=u.NORMAL!==void 0?t.getDependency("accessor",u.NORMAL):i.attributes.normal;a.push(d)}if(r){const d=u.COLOR_0!==void 0?t.getDependency("accessor",u.COLOR_0):i.attributes.color;c.push(d)}}return Promise.all([Promise.all(o),Promise.all(a),Promise.all(c)]).then(function(l){const h=l[0],u=l[1],d=l[2];return n&&(i.morphAttributes.position=h),s&&(i.morphAttributes.normal=u),r&&(i.morphAttributes.color=d),i.morphTargetsRelative=!0,i})}function sw(i,e){if(i.updateMorphTargets(),e.weights!==void 0)for(let t=0,n=e.weights.length;t<n;t++)i.morphTargetInfluences[t]=e.weights[t];if(e.extras&&Array.isArray(e.extras.targetNames)){const t=e.extras.targetNames;if(i.morphTargetInfluences.length===t.length){i.morphTargetDictionary={};for(let n=0,s=t.length;n<s;n++)i.morphTargetDictionary[t[n]]=n}else console.warn("THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.")}}function rw(i){let e;const t=i.extensions&&i.extensions[ut.KHR_DRACO_MESH_COMPRESSION];if(t?e="draco:"+t.bufferView+":"+t.indices+":"+Hc(t.attributes):e=i.indices+":"+Hc(i.attributes)+":"+i.mode,i.targets!==void 0)for(let n=0,s=i.targets.length;n<s;n++)e+=":"+Hc(i.targets[n]);return e}function Hc(i){let e="";const t=Object.keys(i).sort();for(let n=0,s=t.length;n<s;n++)e+=t[n]+":"+i[t[n]]+";";return e}function jl(i){switch(i){case Int8Array:return 1/127;case Uint8Array:return 1/255;case Int16Array:return 1/32767;case Uint16Array:return 1/65535;default:throw new Error("THREE.GLTFLoader: Unsupported normalized accessor component type.")}}function ow(i){return i.search(/\.jpe?g($|\?)/i)>0||i.search(/^data\:image\/jpeg/)===0?"image/jpeg":i.search(/\.webp($|\?)/i)>0||i.search(/^data\:image\/webp/)===0?"image/webp":i.search(/\.ktx2($|\?)/i)>0||i.search(/^data\:image\/ktx2/)===0?"image/ktx2":"image/png"}const aw=new Ae;class cw{constructor(e={},t={}){this.json=e,this.extensions={},this.plugins={},this.options=t,this.cache=new PM,this.associations=new Map,this.primitiveCache={},this.nodeCache={},this.meshCache={refs:{},uses:{}},this.cameraCache={refs:{},uses:{}},this.lightCache={refs:{},uses:{}},this.sourceCache={},this.textureCache={},this.nodeNamesUsed={};let n=!1,s=-1,r=!1,o=-1;if(typeof navigator<"u"){const a=navigator.userAgent;n=/^((?!chrome|android).)*safari/i.test(a)===!0;const c=a.match(/Version\/(\d+)/);s=n&&c?parseInt(c[1],10):-1,r=a.indexOf("Firefox")>-1,o=r?a.match(/Firefox\/([0-9]+)\./)[1]:-1}typeof createImageBitmap>"u"||n&&s<17||r&&o<98?this.textureLoader=new iM(this.options.manager):this.textureLoader=new hM(this.options.manager),this.textureLoader.setCrossOrigin(this.options.crossOrigin),this.textureLoader.setRequestHeader(this.options.requestHeader),this.fileLoader=new Ta(this.options.manager),this.fileLoader.setResponseType("arraybuffer"),this.options.crossOrigin==="use-credentials"&&this.fileLoader.setWithCredentials(!0)}setExtensions(e){this.extensions=e}setPlugins(e){this.plugins=e}parse(e,t){const n=this,s=this.json,r=this.extensions;this.cache.removeAll(),this.nodeCache={},this._invokeAll(function(o){return o._markDefs&&o._markDefs()}),Promise.all(this._invokeAll(function(o){return o.beforeRoot&&o.beforeRoot()})).then(function(){return Promise.all([n.getDependencies("scene"),n.getDependencies("animation"),n.getDependencies("camera")])}).then(function(o){const a={scene:o[0][s.scene||0],scenes:o[0],animations:o[1],cameras:o[2],asset:s.asset,parser:n,userData:{}};return us(r,a,s),wi(a,s),Promise.all(n._invokeAll(function(c){return c.afterRoot&&c.afterRoot(a)})).then(function(){for(const c of a.scenes)c.updateMatrixWorld();e(a)})}).catch(t)}_markDefs(){const e=this.json.nodes||[],t=this.json.skins||[],n=this.json.meshes||[];for(let s=0,r=t.length;s<r;s++){const o=t[s].joints;for(let a=0,c=o.length;a<c;a++)e[o[a]].isBone=!0}for(let s=0,r=e.length;s<r;s++){const o=e[s];o.mesh!==void 0&&(this._addNodeRef(this.meshCache,o.mesh),o.skin!==void 0&&(n[o.mesh].isSkinnedMesh=!0)),o.camera!==void 0&&this._addNodeRef(this.cameraCache,o.camera)}}_addNodeRef(e,t){t!==void 0&&(e.refs[t]===void 0&&(e.refs[t]=e.uses[t]=0),e.refs[t]++)}_getNodeRef(e,t,n){if(e.refs[t]<=1)return n;const s=n.clone(),r=(o,a)=>{const c=this.associations.get(o);c!=null&&this.associations.set(a,c);for(const[l,h]of o.children.entries())r(h,a.children[l])};return r(n,s),s.name+="_instance_"+e.uses[t]++,s}_invokeOne(e){const t=Object.values(this.plugins);t.push(this);for(let n=0;n<t.length;n++){const s=e(t[n]);if(s)return s}return null}_invokeAll(e){const t=Object.values(this.plugins);t.unshift(this);const n=[];for(let s=0;s<t.length;s++){const r=e(t[s]);r&&n.push(r)}return n}getDependency(e,t){const n=e+":"+t;let s=this.cache.get(n);if(!s){switch(e){case"scene":s=this.loadScene(t);break;case"node":s=this._invokeOne(function(r){return r.loadNode&&r.loadNode(t)});break;case"mesh":s=this._invokeOne(function(r){return r.loadMesh&&r.loadMesh(t)});break;case"accessor":s=this.loadAccessor(t);break;case"bufferView":s=this._invokeOne(function(r){return r.loadBufferView&&r.loadBufferView(t)});break;case"buffer":s=this.loadBuffer(t);break;case"material":s=this._invokeOne(function(r){return r.loadMaterial&&r.loadMaterial(t)});break;case"texture":s=this._invokeOne(function(r){return r.loadTexture&&r.loadTexture(t)});break;case"skin":s=this.loadSkin(t);break;case"animation":s=this._invokeOne(function(r){return r.loadAnimation&&r.loadAnimation(t)});break;case"camera":s=this.loadCamera(t);break;default:if(s=this._invokeOne(function(r){return r!=this&&r.getDependency&&r.getDependency(e,t)}),!s)throw new Error("Unknown type: "+e);break}this.cache.add(n,s)}return s}getDependencies(e){let t=this.cache.get(e);if(!t){const n=this,s=this.json[e+(e==="mesh"?"es":"s")]||[];t=Promise.all(s.map(function(r,o){return n.getDependency(e,o)})),this.cache.add(e,t)}return t}loadBuffer(e){const t=this.json.buffers[e],n=this.fileLoader;if(t.type&&t.type!=="arraybuffer")throw new Error("THREE.GLTFLoader: "+t.type+" buffer type is not supported.");if(t.uri===void 0&&e===0)return Promise.resolve(this.extensions[ut.KHR_BINARY_GLTF].body);const s=this.options;return new Promise(function(r,o){n.load(eo.resolveURL(t.uri,s.path),r,void 0,function(){o(new Error('THREE.GLTFLoader: Failed to load buffer "'+t.uri+'".'))})})}loadBufferView(e){const t=this.json.bufferViews[e];return this.getDependency("buffer",t.buffer).then(function(n){const s=t.byteLength||0,r=t.byteOffset||0;return n.slice(r,r+s)})}loadAccessor(e){const t=this,n=this.json,s=this.json.accessors[e];if(s.bufferView===void 0&&s.sparse===void 0){const o=kc[s.type],a=or[s.componentType],c=s.normalized===!0,l=new a(s.count*o);return Promise.resolve(new en(l,o,c))}const r=[];return s.bufferView!==void 0?r.push(this.getDependency("bufferView",s.bufferView)):r.push(null),s.sparse!==void 0&&(r.push(this.getDependency("bufferView",s.sparse.indices.bufferView)),r.push(this.getDependency("bufferView",s.sparse.values.bufferView))),Promise.all(r).then(function(o){const a=o[0],c=kc[s.type],l=or[s.componentType],h=l.BYTES_PER_ELEMENT,u=h*c,d=s.byteOffset||0,f=s.bufferView!==void 0?n.bufferViews[s.bufferView].byteStride:void 0,m=s.normalized===!0;let _,g;if(f&&f!==u){const p=Math.floor(d/f),y="InterleavedBuffer:"+s.bufferView+":"+s.componentType+":"+p+":"+s.count;let M=t.cache.get(y);M||(_=new l(a,p*f,s.count*f/h),M=new cy(_,f/h),t.cache.add(y,M)),g=new dh(M,c,d%f/h,m)}else a===null?_=new l(s.count*c):_=new l(a,d,s.count*c),g=new en(_,c,m);if(s.sparse!==void 0){const p=kc.SCALAR,y=or[s.sparse.indices.componentType],M=s.sparse.indices.byteOffset||0,x=s.sparse.values.byteOffset||0,E=new y(o[1],M,s.sparse.count*p),T=new l(o[2],x,s.sparse.count*c);a!==null&&(g=new en(g.array.slice(),g.itemSize,g.normalized)),g.normalized=!1;for(let P=0,C=E.length;P<C;P++){const b=E[P];if(g.setX(b,T[P*c]),c>=2&&g.setY(b,T[P*c+1]),c>=3&&g.setZ(b,T[P*c+2]),c>=4&&g.setW(b,T[P*c+3]),c>=5)throw new Error("THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.")}g.normalized=m}return g})}loadTexture(e){const t=this.json,n=this.options,r=t.textures[e].source,o=t.images[r];let a=this.textureLoader;if(o.uri){const c=n.manager.getHandler(o.uri);c!==null&&(a=c)}return this.loadTextureImage(e,r,a)}loadTextureImage(e,t,n){const s=this,r=this.json,o=r.textures[e],a=r.images[t],c=(a.uri||a.bufferView)+":"+o.sampler;if(this.textureCache[c])return this.textureCache[c];const l=this.loadImageSource(t,n).then(function(h){h.flipY=!1,h.name=o.name||a.name||"",h.name===""&&typeof a.uri=="string"&&a.uri.startsWith("data:image/")===!1&&(h.name=a.uri);const d=(r.samplers||{})[o.sampler]||{};return h.magFilter=gd[d.magFilter]||Dn,h.minFilter=gd[d.minFilter]||bi,h.wrapS=_d[d.wrapS]||ur,h.wrapT=_d[d.wrapT]||ur,h.generateMipmaps=!h.isCompressedTexture&&h.minFilter!==pn&&h.minFilter!==Dn,s.associations.set(h,{textures:e}),h}).catch(function(){return null});return this.textureCache[c]=l,l}loadImageSource(e,t){const n=this,s=this.json,r=this.options;if(this.sourceCache[e]!==void 0)return this.sourceCache[e].then(u=>u.clone());const o=s.images[e],a=self.URL||self.webkitURL;let c=o.uri||"",l=!1;if(o.bufferView!==void 0)c=n.getDependency("bufferView",o.bufferView).then(function(u){l=!0;const d=new Blob([u],{type:o.mimeType});return c=a.createObjectURL(d),c});else if(o.uri===void 0)throw new Error("THREE.GLTFLoader: Image "+e+" is missing URI and bufferView");const h=Promise.resolve(c).then(function(u){return new Promise(function(d,f){let m=d;t.isImageBitmapLoader===!0&&(m=function(_){const g=new Qt(_);g.needsUpdate=!0,d(g)}),t.load(eo.resolveURL(u,r.path),m,void 0,f)})}).then(function(u){return l===!0&&a.revokeObjectURL(c),wi(u,o),u.userData.mimeType=o.mimeType||ow(o.uri),u}).catch(function(u){throw console.error("THREE.GLTFLoader: Couldn't load texture",c),u});return this.sourceCache[e]=h,h}assignTexture(e,t,n,s){const r=this;return this.getDependency("texture",n.index).then(function(o){if(!o)return null;if(n.texCoord!==void 0&&n.texCoord>0&&(o=o.clone(),o.channel=n.texCoord),r.extensions[ut.KHR_TEXTURE_TRANSFORM]){const a=n.extensions!==void 0?n.extensions[ut.KHR_TEXTURE_TRANSFORM]:void 0;if(a){const c=r.associations.get(o);o=r.extensions[ut.KHR_TEXTURE_TRANSFORM].extendTexture(o,a),r.associations.set(o,c)}}return s!==void 0&&(o.colorSpace=s),e[t]=o,o})}assignFinalMaterial(e){const t=e.geometry;let n=e.material;const s=t.attributes.tangent===void 0,r=t.attributes.color!==void 0,o=t.attributes.normal===void 0;if(e.isPoints){const a="PointsMaterial:"+n.uuid;let c=this.cache.get(a);c||(c=new bf,ri.prototype.copy.call(c,n),c.color.copy(n.color),c.map=n.map,c.sizeAttenuation=!1,this.cache.add(a,c)),n=c}else if(e.isLine){const a="LineBasicMaterial:"+n.uuid;let c=this.cache.get(a);c||(c=new As,ri.prototype.copy.call(c,n),c.color.copy(n.color),c.map=n.map,this.cache.add(a,c)),n=c}if(s||r||o){let a="ClonedMaterial:"+n.uuid+":";s&&(a+="derivative-tangents:"),r&&(a+="vertex-colors:"),o&&(a+="flat-shading:");let c=this.cache.get(a);c||(c=n.clone(),r&&(c.vertexColors=!0),o&&(c.flatShading=!0),s&&(c.normalScale&&(c.normalScale.y*=-1),c.clearcoatNormalScale&&(c.clearcoatNormalScale.y*=-1)),this.cache.add(a,c),this.associations.set(c,this.associations.get(n))),n=c}e.material=n}getMaterialType(){return bh}loadMaterial(e){const t=this,n=this.json,s=this.extensions,r=n.materials[e];let o;const a={},c=r.extensions||{},l=[];if(c[ut.KHR_MATERIALS_UNLIT]){const u=s[ut.KHR_MATERIALS_UNLIT];o=u.getMaterialType(),l.push(u.extendParams(a,r,t))}else{const u=r.pbrMetallicRoughness||{};if(a.color=new Ve(1,1,1),a.opacity=1,Array.isArray(u.baseColorFactor)){const d=u.baseColorFactor;a.color.setRGB(d[0],d[1],d[2],mn),a.opacity=d[3]}u.baseColorTexture!==void 0&&l.push(t.assignTexture(a,"map",u.baseColorTexture,qt)),a.metalness=u.metallicFactor!==void 0?u.metallicFactor:1,a.roughness=u.roughnessFactor!==void 0?u.roughnessFactor:1,u.metallicRoughnessTexture!==void 0&&(l.push(t.assignTexture(a,"metalnessMap",u.metallicRoughnessTexture)),l.push(t.assignTexture(a,"roughnessMap",u.metallicRoughnessTexture))),o=this._invokeOne(function(d){return d.getMaterialType&&d.getMaterialType(e)}),l.push(Promise.all(this._invokeAll(function(d){return d.extendMaterialParams&&d.extendMaterialParams(e,a)})))}r.doubleSided===!0&&(a.side=An);const h=r.alphaMode||zc.OPAQUE;if(h===zc.BLEND?(a.transparent=!0,a.depthWrite=!1):(a.transparent=!1,h===zc.MASK&&(a.alphaTest=r.alphaCutoff!==void 0?r.alphaCutoff:.5)),r.normalTexture!==void 0&&o!==fn&&(l.push(t.assignTexture(a,"normalMap",r.normalTexture)),a.normalScale=new te(1,1),r.normalTexture.scale!==void 0)){const u=r.normalTexture.scale;a.normalScale.set(u,u)}if(r.occlusionTexture!==void 0&&o!==fn&&(l.push(t.assignTexture(a,"aoMap",r.occlusionTexture)),r.occlusionTexture.strength!==void 0&&(a.aoMapIntensity=r.occlusionTexture.strength)),r.emissiveFactor!==void 0&&o!==fn){const u=r.emissiveFactor;a.emissive=new Ve().setRGB(u[0],u[1],u[2],mn)}return r.emissiveTexture!==void 0&&o!==fn&&l.push(t.assignTexture(a,"emissiveMap",r.emissiveTexture,qt)),Promise.all(l).then(function(){const u=new o(a);return r.name&&(u.name=r.name),wi(u,r),t.associations.set(u,{materials:e}),r.extensions&&us(s,u,r),u})}createUniqueName(e){const t=At.sanitizeNodeName(e||"");return t in this.nodeNamesUsed?t+"_"+ ++this.nodeNamesUsed[t]:(this.nodeNamesUsed[t]=0,t)}loadGeometries(e){const t=this,n=this.extensions,s=this.primitiveCache;function r(a){return n[ut.KHR_DRACO_MESH_COMPRESSION].decodePrimitive(a,t).then(function(c){return xd(c,a,t)})}const o=[];for(let a=0,c=e.length;a<c;a++){const l=e[a],h=rw(l),u=s[h];if(u)o.push(u.promise);else{let d;l.extensions&&l.extensions[ut.KHR_DRACO_MESH_COMPRESSION]?d=r(l):d=xd(new Gt,l,t),s[h]={primitive:l,promise:d},o.push(d)}}return Promise.all(o)}loadMesh(e){const t=this,n=this.json,s=this.extensions,r=n.meshes[e],o=r.primitives,a=[];for(let c=0,l=o.length;c<l;c++){const h=o[c].material===void 0?nw(this.cache):this.getDependency("material",o[c].material);a.push(h)}return a.push(t.loadGeometries(o)),Promise.all(a).then(function(c){const l=c.slice(0,c.length-1),h=c[c.length-1],u=[];for(let f=0,m=h.length;f<m;f++){const _=h[f],g=o[f];let p;const y=l[f];if(g.mode===Fn.TRIANGLES||g.mode===Fn.TRIANGLE_STRIP||g.mode===Fn.TRIANGLE_FAN||g.mode===void 0)p=r.isSkinnedMesh===!0?new fh(_,y):new Xt(_,y),p.isSkinnedMesh===!0&&p.normalizeSkinWeights(),g.mode===Fn.TRIANGLE_STRIP?p.geometry=pd(p.geometry,nf):g.mode===Fn.TRIANGLE_FAN&&(p.geometry=pd(p.geometry,Bl));else if(g.mode===Fn.LINES)p=new fo(_,y);else if(g.mode===Fn.LINE_STRIP)p=new gh(_,y);else if(g.mode===Fn.LINE_LOOP)p=new wf(_,y);else if(g.mode===Fn.POINTS)p=new fy(_,y);else throw new Error("THREE.GLTFLoader: Primitive mode unsupported: "+g.mode);Object.keys(p.geometry.morphAttributes).length>0&&sw(p,r),p.name=t.createUniqueName(r.name||"mesh_"+e),wi(p,r),g.extensions&&us(s,p,g),t.assignFinalMaterial(p),u.push(p)}for(let f=0,m=u.length;f<m;f++)t.associations.set(u[f],{meshes:e,primitives:f});if(u.length===1)return r.extensions&&us(s,u[0],r),u[0];const d=new Ct;r.extensions&&us(s,d,r),t.associations.set(d,{meshes:e});for(let f=0,m=u.length;f<m;f++)d.add(u[f]);return d})}loadCamera(e){let t;const n=this.json.cameras[e],s=n[n.type];if(!s){console.warn("THREE.GLTFLoader: Missing camera parameters.");return}return n.type==="perspective"?t=new Tn(Ft.radToDeg(s.yfov),s.aspectRatio||1,s.znear||1,s.zfar||2e6):n.type==="orthographic"&&(t=new Oa(-s.xmag,s.xmag,s.ymag,-s.ymag,s.znear,s.zfar)),n.name&&(t.name=this.createUniqueName(n.name)),wi(t,n),Promise.resolve(t)}loadSkin(e){const t=this.json.skins[e],n=[];for(let s=0,r=t.joints.length;s<r;s++)n.push(this._loadNodeShallow(t.joints[s]));return t.inverseBindMatrices!==void 0?n.push(this.getDependency("accessor",t.inverseBindMatrices)):n.push(null),Promise.all(n).then(function(s){const r=s.pop(),o=s,a=[],c=[];for(let l=0,h=o.length;l<h;l++){const u=o[l];if(u){a.push(u);const d=new Ae;r!==null&&d.fromArray(r.array,l*16),c.push(d)}else console.warn('THREE.GLTFLoader: Joint "%s" could not be found.',t.joints[l])}return new mh(a,c)})}loadAnimation(e){const t=this.json,n=this,s=t.animations[e],r=s.name?s.name:"animation_"+e,o=[],a=[],c=[],l=[],h=[];for(let u=0,d=s.channels.length;u<d;u++){const f=s.channels[u],m=s.samplers[f.sampler],_=f.target,g=_.node,p=s.parameters!==void 0?s.parameters[m.input]:m.input,y=s.parameters!==void 0?s.parameters[m.output]:m.output;_.node!==void 0&&(o.push(this.getDependency("node",g)),a.push(this.getDependency("accessor",p)),c.push(this.getDependency("accessor",y)),l.push(m),h.push(_))}return Promise.all([Promise.all(o),Promise.all(a),Promise.all(c),Promise.all(l),Promise.all(h)]).then(function(u){const d=u[0],f=u[1],m=u[2],_=u[3],g=u[4],p=[];for(let y=0,M=d.length;y<M;y++){const x=d[y],E=f[y],T=m[y],P=_[y],C=g[y];if(x===void 0)continue;x.updateMatrix&&x.updateMatrix();const b=n._createAnimationTracks(x,E,T,P,C);if(b)for(let w=0;w<b.length;w++)p.push(b[w])}return new Ky(r,void 0,p)})}createNodeMesh(e){const t=this.json,n=this,s=t.nodes[e];return s.mesh===void 0?null:n.getDependency("mesh",s.mesh).then(function(r){const o=n._getNodeRef(n.meshCache,s.mesh,r);return s.weights!==void 0&&o.traverse(function(a){if(a.isMesh)for(let c=0,l=s.weights.length;c<l;c++)a.morphTargetInfluences[c]=s.weights[c]}),o})}loadNode(e){const t=this.json,n=this,s=t.nodes[e],r=n._loadNodeShallow(e),o=[],a=s.children||[];for(let l=0,h=a.length;l<h;l++)o.push(n.getDependency("node",a[l]));const c=s.skin===void 0?Promise.resolve(null):n.getDependency("skin",s.skin);return Promise.all([r,Promise.all(o),c]).then(function(l){const h=l[0],u=l[1],d=l[2];d!==null&&h.traverse(function(f){f.isSkinnedMesh&&f.bind(d,aw)});for(let f=0,m=u.length;f<m;f++)h.add(u[f]);return h})}_loadNodeShallow(e){const t=this.json,n=this.extensions,s=this;if(this.nodeCache[e]!==void 0)return this.nodeCache[e];const r=t.nodes[e],o=r.name?s.createUniqueName(r.name):"",a=[],c=s._invokeOne(function(l){return l.createNodeMesh&&l.createNodeMesh(e)});return c&&a.push(c),r.camera!==void 0&&a.push(s.getDependency("camera",r.camera).then(function(l){return s._getNodeRef(s.cameraCache,r.camera,l)})),s._invokeAll(function(l){return l.createNodeAttachment&&l.createNodeAttachment(e)}).forEach(function(l){a.push(l)}),this.nodeCache[e]=Promise.all(a).then(function(l){let h;if(r.isBone===!0?h=new Mf:l.length>1?h=new Ct:l.length===1?h=l[0]:h=new Nt,h!==l[0])for(let u=0,d=l.length;u<d;u++)h.add(l[u]);if(r.name&&(h.userData.name=r.name,h.name=o),wi(h,r),r.extensions&&us(n,h,r),r.matrix!==void 0){const u=new Ae;u.fromArray(r.matrix),h.applyMatrix4(u)}else r.translation!==void 0&&h.position.fromArray(r.translation),r.rotation!==void 0&&h.quaternion.fromArray(r.rotation),r.scale!==void 0&&h.scale.fromArray(r.scale);return s.associations.has(h)||s.associations.set(h,{}),s.associations.get(h).nodes=e,h}),this.nodeCache[e]}loadScene(e){const t=this.extensions,n=this.json.scenes[e],s=this,r=new Ct;n.name&&(r.name=s.createUniqueName(n.name)),wi(r,n),n.extensions&&us(t,r,n);const o=n.nodes||[],a=[];for(let c=0,l=o.length;c<l;c++)a.push(s.getDependency("node",o[c]));return Promise.all(a).then(function(c){for(let h=0,u=c.length;h<u;h++)r.add(c[h]);const l=h=>{const u=new Map;for(const[d,f]of s.associations)(d instanceof ri||d instanceof Qt)&&u.set(d,f);return h.traverse(d=>{const f=s.associations.get(d);f!=null&&u.set(d,f)}),u};return s.associations=l(r),r})}_createAnimationTracks(e,t,n,s,r){const o=[],a=e.name?e.name:e.uuid,c=[];Hi[r.path]===Hi.weights?e.traverse(function(d){d.morphTargetInfluences&&c.push(d.name?d.name:d.uuid)}):c.push(a);let l;switch(Hi[r.path]){case Hi.weights:l=_r;break;case Hi.rotation:l=xr;break;case Hi.position:case Hi.scale:l=vr;break;default:switch(n.itemSize){case 1:l=_r;break;case 2:case 3:default:l=vr;break}break}const h=s.interpolation!==void 0?tw[s.interpolation]:ro,u=this._getArrayFromAccessor(n);for(let d=0,f=c.length;d<f;d++){const m=new l(c[d]+"."+Hi[r.path],t.array,u,h);s.interpolation==="CUBICSPLINE"&&this._createCubicSplineTrackInterpolant(m),o.push(m)}return o}_getArrayFromAccessor(e){let t=e.array;if(e.normalized){const n=jl(t.constructor),s=new Float32Array(t.length);for(let r=0,o=t.length;r<o;r++)s[r]=t[r]*n;t=s}return t}_createCubicSplineTrackInterpolant(e){e.createInterpolant=function(n){const s=this instanceof xr?ew:Bf;return new s(this.times,this.values,this.getValueSize()/3,n)},e.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline=!0}}function lw(i,e,t){const n=e.attributes,s=new tn;if(n.POSITION!==void 0){const a=t.json.accessors[n.POSITION],c=a.min,l=a.max;if(c!==void 0&&l!==void 0){if(s.set(new v(c[0],c[1],c[2]),new v(l[0],l[1],l[2])),a.normalized){const h=jl(or[a.componentType]);s.min.multiplyScalar(h),s.max.multiplyScalar(h)}}else{console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.");return}}else return;const r=e.targets;if(r!==void 0){const a=new v,c=new v;for(let l=0,h=r.length;l<h;l++){const u=r[l];if(u.POSITION!==void 0){const d=t.json.accessors[u.POSITION],f=d.min,m=d.max;if(f!==void 0&&m!==void 0){if(c.setX(Math.max(Math.abs(f[0]),Math.abs(m[0]))),c.setY(Math.max(Math.abs(f[1]),Math.abs(m[1]))),c.setZ(Math.max(Math.abs(f[2]),Math.abs(m[2]))),d.normalized){const _=jl(or[d.componentType]);c.multiplyScalar(_)}a.max(c)}else console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.")}}s.expandByVector(a)}i.boundingBox=s;const o=new ci;s.getCenter(o.center),o.radius=s.min.distanceTo(s.max)/2,i.boundingSphere=o}function xd(i,e,t){const n=e.attributes,s=[];function r(o,a){return t.getDependency("accessor",o).then(function(c){i.setAttribute(a,c)})}for(const o in n){const a=ql[o]||o.toLowerCase();a in i.attributes||s.push(r(n[o],a))}if(e.indices!==void 0&&!i.index){const o=t.getDependency("accessor",e.indices).then(function(a){i.setIndex(a)});s.push(o)}return ft.workingColorSpace!==mn&&"COLOR_0"in n&&console.warn(`THREE.GLTFLoader: Converting vertex colors from "srgb-linear" to "${ft.workingColorSpace}" not supported.`),wi(i,e),lw(i,e,t),Promise.all(s).then(function(){return e.targets!==void 0?iw(i,e.targets,t):i})}const Gc=new WeakMap;class hw extends Ls{constructor(e){super(e),this.decoderPath="",this.decoderConfig={},this.decoderBinary=null,this.decoderPending=null,this.workerLimit=4,this.workerPool=[],this.workerNextTaskID=1,this.workerSourceURL="",this.defaultAttributeIDs={position:"POSITION",normal:"NORMAL",color:"COLOR",uv:"TEX_COORD"},this.defaultAttributeTypes={position:"Float32Array",normal:"Float32Array",color:"Float32Array",uv:"Float32Array"}}setDecoderPath(e){return this.decoderPath=e,this}setDecoderConfig(e){return this.decoderConfig=e,this}setWorkerLimit(e){return this.workerLimit=e,this}load(e,t,n,s){const r=new Ta(this.manager);r.setPath(this.path),r.setResponseType("arraybuffer"),r.setRequestHeader(this.requestHeader),r.setWithCredentials(this.withCredentials),r.load(e,o=>{this.parse(o,t,s)},n,s)}parse(e,t,n=()=>{}){this.decodeDracoFile(e,t,null,null,qt,n).catch(n)}decodeDracoFile(e,t,n,s,r=mn,o=()=>{}){const a={attributeIDs:n||this.defaultAttributeIDs,attributeTypes:s||this.defaultAttributeTypes,useUniqueIDs:!!n,vertexColorSpace:r};return this.decodeGeometry(e,a).then(t).catch(o)}decodeGeometry(e,t){const n=JSON.stringify(t);if(Gc.has(e)){const c=Gc.get(e);if(c.key===n)return c.promise;if(e.byteLength===0)throw new Error("THREE.DRACOLoader: Unable to re-decode a buffer with different settings. Buffer has already been transferred.")}let s;const r=this.workerNextTaskID++,o=e.byteLength,a=this._getWorker(r,o).then(c=>(s=c,new Promise((l,h)=>{s._callbacks[r]={resolve:l,reject:h},s.postMessage({type:"decode",id:r,taskConfig:t,buffer:e},[e])}))).then(c=>this._createGeometry(c.geometry));return a.catch(()=>!0).then(()=>{s&&r&&this._releaseTask(s,r)}),Gc.set(e,{key:n,promise:a}),a}_createGeometry(e){const t=new Gt;e.index&&t.setIndex(new en(e.index.array,1));for(let n=0;n<e.attributes.length;n++){const s=e.attributes[n],r=s.name,o=s.array,a=s.itemSize,c=new en(o,a);r==="color"&&(this._assignVertexColorSpace(c,s.vertexColorSpace),c.normalized=!(o instanceof Float32Array)),t.setAttribute(r,c)}return t}_assignVertexColorSpace(e,t){if(t!==qt)return;const n=new Ve;for(let s=0,r=e.count;s<r;s++)n.fromBufferAttribute(e,s),ft.toWorkingColorSpace(n,qt),e.setXYZ(s,n.r,n.g,n.b)}_loadLibrary(e,t){const n=new Ta(this.manager);return n.setPath(this.decoderPath),n.setResponseType(t),n.setWithCredentials(this.withCredentials),new Promise((s,r)=>{n.load(e,s,void 0,r)})}preload(){return this._initDecoder(),this}_initDecoder(){if(this.decoderPending)return this.decoderPending;const e=typeof WebAssembly!="object"||this.decoderConfig.type==="js",t=[];return e?t.push(this._loadLibrary("draco_decoder.js","text")):(t.push(this._loadLibrary("draco_wasm_wrapper.js","text")),t.push(this._loadLibrary("draco_decoder.wasm","arraybuffer"))),this.decoderPending=Promise.all(t).then(n=>{const s=n[0];e||(this.decoderConfig.wasmBinary=n[1]);const r=uw.toString(),o=["/* draco decoder */",s,"","/* worker */",r.substring(r.indexOf("{")+1,r.lastIndexOf("}"))].join(`
`);this.workerSourceURL=URL.createObjectURL(new Blob([o]))}),this.decoderPending}_getWorker(e,t){return this._initDecoder().then(()=>{if(this.workerPool.length<this.workerLimit){const s=new Worker(this.workerSourceURL);s._callbacks={},s._taskCosts={},s._taskLoad=0,s.postMessage({type:"init",decoderConfig:this.decoderConfig}),s.onmessage=function(r){const o=r.data;switch(o.type){case"decode":s._callbacks[o.id].resolve(o);break;case"error":s._callbacks[o.id].reject(o);break;default:console.error('THREE.DRACOLoader: Unexpected message, "'+o.type+'"')}},this.workerPool.push(s)}else this.workerPool.sort(function(s,r){return s._taskLoad>r._taskLoad?-1:1});const n=this.workerPool[this.workerPool.length-1];return n._taskCosts[e]=t,n._taskLoad+=t,n})}_releaseTask(e,t){e._taskLoad-=e._taskCosts[t],delete e._callbacks[t],delete e._taskCosts[t]}debug(){console.log("Task load: ",this.workerPool.map(e=>e._taskLoad))}dispose(){for(let e=0;e<this.workerPool.length;++e)this.workerPool[e].terminate();return this.workerPool.length=0,this.workerSourceURL!==""&&URL.revokeObjectURL(this.workerSourceURL),this}}function uw(){let i,e;onmessage=function(o){const a=o.data;switch(a.type){case"init":i=a.decoderConfig,e=new Promise(function(h){i.onModuleLoaded=function(u){h({draco:u})},DracoDecoderModule(i)});break;case"decode":const c=a.buffer,l=a.taskConfig;e.then(h=>{const u=h.draco,d=new u.Decoder;try{const f=t(u,d,new Int8Array(c),l),m=f.attributes.map(_=>_.array.buffer);f.index&&m.push(f.index.array.buffer),self.postMessage({type:"decode",id:a.id,geometry:f},m)}catch(f){console.error(f),self.postMessage({type:"error",id:a.id,error:f.message})}finally{u.destroy(d)}});break}};function t(o,a,c,l){const h=l.attributeIDs,u=l.attributeTypes;let d,f;const m=a.GetEncodedGeometryType(c);if(m===o.TRIANGULAR_MESH)d=new o.Mesh,f=a.DecodeArrayToMesh(c,c.byteLength,d);else if(m===o.POINT_CLOUD)d=new o.PointCloud,f=a.DecodeArrayToPointCloud(c,c.byteLength,d);else throw new Error("THREE.DRACOLoader: Unexpected geometry type.");if(!f.ok()||d.ptr===0)throw new Error("THREE.DRACOLoader: Decoding failed: "+f.error_msg());const _={index:null,attributes:[]};for(const g in h){const p=self[u[g]];let y,M;if(l.useUniqueIDs)M=h[g],y=a.GetAttributeByUniqueId(d,M);else{if(M=a.GetAttributeId(d,o[h[g]]),M===-1)continue;y=a.GetAttribute(d,M)}const x=s(o,a,d,g,p,y);g==="color"&&(x.vertexColorSpace=l.vertexColorSpace),_.attributes.push(x)}return m===o.TRIANGULAR_MESH&&(_.index=n(o,a,d)),o.destroy(d),_}function n(o,a,c){const h=c.num_faces()*3,u=h*4,d=o._malloc(u);a.GetTrianglesUInt32Array(c,u,d);const f=new Uint32Array(o.HEAPF32.buffer,d,h).slice();return o._free(d),{array:f,itemSize:1}}function s(o,a,c,l,h,u){const d=u.num_components(),m=c.num_points()*d,_=m*h.BYTES_PER_ELEMENT,g=r(o,h),p=o._malloc(_);a.GetAttributeDataArrayForAllPoints(c,u,g,_,p);const y=new h(o.HEAPF32.buffer,p,m).slice();return o._free(p),{name:l,array:y,itemSize:d}}function r(o,a){switch(a){case Float32Array:return o.DT_FLOAT32;case Int8Array:return o.DT_INT8;case Int16Array:return o.DT_INT16;case Int32Array:return o.DT_INT32;case Uint8Array:return o.DT_UINT8;case Uint16Array:return o.DT_UINT16;case Uint32Array:return o.DT_UINT32}}}const dw=224,{height:Ht,middle:Nn}=Np,Vc=8,vd=3,fw="https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/libs/draco/gltf/",oT=(Ht/2-Nn)/Ht,yi=2,pw=.5,mw=.5,yd=i=>Math.min(pw*i.width/dw,mw),gw=new v(-.35,-.8,.5),_w=.6,$l=new v(.6,.6,.7),xw=new v(.02,.02,.05),vw=.036,H={l:1,r:-1},Cs=65,Xa=25,yw=25,Mw=-6,Md=95,ww=30,bw=20,kf=40,zf=25,Hf=10,Wc=[.4,-.92,2.1],Gf=[.6,.3,-1],Sw=4,to=18,Ew=new Set(["butler_tray","butler_towel"]),Xc="butler_tablet",Vf=new Set(["colleague_mug"]),qa=new Set([...Vf,"squire_shield","coach_clipboard"]),Mt=new Set([...qa,"squire_quill"]),Tw=.06,Aw={forearm:new v(0,0,-1),shin:new v(1,0,0)},Tr=new Ae().set(1,0,0,0,0,0,1,0,0,-1,0,0,0,0,0,1),ja=Tr.clone().invert(),Aa=i=>i.clone().applyMatrix4(ja),bs=i=>new Ae().makeTranslation(i.x,i.y,i.z),Qe=Ft.degToRad,Rw=1.2,$i=(i,e,t)=>new Ae().makeRotationFromEuler(new wn(Qe(i),Qe(e),Qe(t),"ZYX"));function ds(i,e){return bs(i).multiply(e).multiply(bs(i.clone().negate()))}function Cw(i){const e=i.match(/^(.*)_([lr])$/);return e?{base:e[1],side:e[2]}:{base:i,side:""}}function Pw(i,e){const{x:t,y:n,z:s}=Aw[i];return e==="l"?new v(t,n,s):new v(t,-n,-s)}class Lw{constructor(e,t="stand",n=0){this.rig=e,this.final=new Map,this.eyes=1,this.eyeShape=null,this.eyeGlance=[0,0],this.bulbLit=0,this.eyeTint=null,this.hearts=0,this.stars=0,this.squeezed=0,this.dozing=0,this.whoa=!1,this.laptop=!1,this.tablet=!1,this.book=null,this.props=new Map,this.stowed=new Set,this.keep=new Set,this.tap=0,this.gaze=null,this.posture=t,this.sway=0,this.stride=n,this.sky=null,this.throws=null,this.leanWay=0,this.walkWay=0,this.screen=null,this.facing=0,this.target=null}standing(e){const t=this.rig.parents.get(e);return t?this.matrix(t):new Ae}matrix(e){return this.final.get(e)??this.standing(e)}head(e,t){return this.rig.heads.get(e).clone().applyMatrix4(t)}turn(e,{x:t=0,y:n=0,z:s=0}){const r=this.matrix(e);this.final.set(e,ds(this.head(e,r),$i(t,n,s)).multiply(r))}face(e,{x:t=0,y:n=0,z:s=0}){const r=this.head(e,this.standing(e)),o=this.rig.heads.get(e).clone().negate();this.final.set(e,bs(r).multiply($i(t,n,s)).multiply(bs(o)))}lift(e,{x:t=0,y:n=0,z:s=0}){this.final.set(e,bs(new v(t,n,s)).multiply(this.matrix(e)))}bend(e,t){const{base:n,side:s}=Cw(e),r=this.standing(e),o=Pw(n,s).transformDirection(r).normalize(),a=new Ae().makeRotationAxis(o,Qe(t));this.final.set(e,ds(this.head(e,r),a).multiply(r))}aim(e,t){const n=this.standing(e),s=this.rig.along.get(e).clone().transformDirection(n),r=new Ae().makeRotationFromQuaternion(new Gn().setFromUnitVectors(s,t.clone().normalize()));this.final.set(e,ds(this.head(e,n),r).multiply(n))}reach(e,t,n){this.limbTo(e,["upper_arm","forearm","hand"],t,n)}withinReach(e,t,n){const[s,r,o]=["upper_arm","forearm","hand"].map(f=>this.rig.heads.get(`${f}_${e}`)),[a,c]=[r.distanceTo(s),o.distanceTo(r)],l=(a+c)*n,h=Math.abs(a-c)*Rw,u=this.head(`upper_arm_${e}`,this.standing(`upper_arm_${e}`)),d=t.clone().sub(u);return d.length()>l?u.clone().add(d.setLength(l)):d.length()>=h?t:u.clone().add(d.setLength(h))}step(e,t,n){this.limbTo(e,["thigh","shin","foot"],t,n)}limbTo(e,t,n,s){const[r,o,a]=t.map(p=>`${p}_${e}`),c=this.rig.heads.get(o).distanceTo(this.rig.heads.get(r)),l=this.rig.heads.get(a).distanceTo(this.rig.heads.get(o)),h=this.head(r,this.standing(r)),u=n.clone().sub(h),d=u.length();if(d<Math.abs(c-l)||d>c+l)throw new Error(`the ${r} cannot reach ${d.toFixed(3)}`);const f=u.clone().normalize(),m=(c*c-l*l+d*d)/(2*d),_=s.clone();e==="r"&&(_.x=-_.x),_.sub(f.clone().multiplyScalar(_.dot(f)));const g=h.clone().add(f.multiplyScalar(m)).add(_.normalize().multiplyScalar(Math.sqrt(Math.max(c*c-m*m,0))));this.aim(r,g.clone().sub(h)),this.aim(o,n.clone().sub(g))}turnAll({x:e=0,y:t=0,z:n=0},s=new v){const r=ds(s,$i(e,t,n));this.final=new Map(this.rig.order.map(o=>[o,r.clone().multiply(this.matrix(o))]))}revolve(e){this.turnAll({z:e})}bendAbove(e,{x:t=0,y:n=0,z:s=0}){const r=ds(this.head(e,this.matrix(e)),$i(t,n,s)),o=a=>a===e||!!a&&o(this.rig.parents.get(a));this.final=new Map(this.rig.order.map(a=>[a,o(a)?r.clone().multiply(this.matrix(a)):this.matrix(a)]))}offsetAll(e){const t=bs(new v(...e));this.final=new Map(this.rig.order.map(n=>[n,t.clone().multiply(this.matrix(n))]))}carried(e){return e.clone().add(this.head("root",this.matrix("root")).sub(this.rig.heads.get("root")))}swing(e){this.sway=e}shutEyes(e){this.eyes=Math.max(e,Tw)}glanceEyes(e,t){this.eyeGlance=[t,e]}shapeEyes(e,t=1,n=1){this.eyeShape=t>0?{name:e,strength:t,way:n}:null}tintEyes(e){this.eyeTint=e}heartEyes(e){this.hearts=e}starEyes(e){this.stars=e}squeezeEyes(e){this.squeezed=e}doze(e){this.dozing=e}holdLaptop(){this.laptop=!0}holdTablet(){this.tablet=!0}holdBook(e,t,n){this.book={open:e,page:t,visible:n}}holdProp(e,t,n=[0,0,0],s={}){this.props.set(e,{bone:`hand_${t}`,frame:`hand_${t}`,at:this.grip(t,n),turn:s})}holdUpright(e,t,n=[0,0,0],s={}){this.props.set(e,{bone:`hand_${t}`,frame:"root",at:this.grip(t,n),turn:s})}standProp(e,t,n={},s=1){this.props.set(e,{bone:"root",frame:"root",at:new v(...t),turn:n,size:s})}lightBulb(e,t,n){const[s,r,o]=ar.at;this.standProp("light_bulb",[n*s,r,o]),Object.assign(this.props.get("light_bulb"),{size:e,lit:t}),this.bulbLit=t}wearProp(e,t,n={}){this.props.set(e,{bone:"head",frame:"head",at:this.rig.heads.get("head").clone().add(new v(...t)),turn:n})}roll(e,t){const n=this.matrix(e),s=this.rig.along.get(e).clone().transformDirection(n).normalize();this.final.set(e,ds(this.head(e,n),new Ae().makeRotationAxis(s,Qe(t))).multiply(n))}clench(e,t){const n=`hand_${e}`,s=this.rig.heads.get(n),r=this.rig.along.get(n).clone().normalize(),o=new Ae().set(1+(t-1)*r.x*r.x,(t-1)*r.x*r.y,(t-1)*r.x*r.z,0,(t-1)*r.y*r.x,1+(t-1)*r.y*r.y,(t-1)*r.y*r.z,0,(t-1)*r.z*r.x,(t-1)*r.z*r.y,1+(t-1)*r.z*r.z,0,0,0,0,1);this.final.set(n,this.matrix(n).clone().multiply(ds(s,o)))}grip(e,t){return this.rig.heads.get(`hand_${e}`).clone().add(new v(H[e]*(Pi.grip+t[0]),Pi.forward+t[1],t[2]))}putAway(...e){e.forEach(t=>this.stowed.add(t))}moves(e){const t=new Ae().makeRotationZ(Qe(e)),n=new Map;for(const s of this.rig.order){const r=this.rig.parents.get(s);n.set(s,this.final.get(s)??(r?n.get(r):new Ae))}return new Map([...n].map(([s,r])=>[s,t.clone().multiply(r)]))}}const Ee=(i,e=1)=>Math.sin(2*Math.PI*e*i);function de(i,e,t=1){i.turn("spine",{x:1*t*Ee(e)}),i.turn("chest",{x:1.5*t*Ee(e-.05)}),i.turn("neck",{x:-.8*t*Ee(e-.1)}),i.turn("head",{x:-1.2*t*Ee(e-.12)})}function se(i,{lean:e=0,twist:t=0,nod:n=0,turn:s=0,tilt:r=0}){i.turn("spine",{x:e*.4,z:t*.4}),i.turn("chest",{x:e*.6,z:t*.6}),i.turn("neck",{x:n*.3,z:s*.3,y:r*.3}),i.turn("head",{x:n*.7,z:s*.7,y:r*.7})}function Wf(i,e,t=0,n=10){i.turn(`upper_arm_${e}`,{y:H[e]*Cs}),i.turn(`upper_arm_${e}`,{x:t}),i.bend(`forearm_${e}`,n)}function Iw(i,e,t=Mw,n=0,s=0){const r=H[e];i.turn(`upper_arm_${e}`,{y:r*Cs}),i.turn(`upper_arm_${e}`,{x:-n}),i.turn(`upper_arm_${e}`,{z:r*bw}),i.face(`forearm_${e}`,{y:-r*t,z:-r*Md}),i.face(`hand_${e}`,{x:s,z:-r*(Md-ww)})}function ve(i,e,t=[],n={},s=e.level){var r;for(const o of Object.keys(H))if(!t.includes(o)){if(s.has(o)){Iw(i,o);continue}Wf(i,o,n[o]??0),(r=e.shield)!=null&&r.has(o)&&i.turn(`hand_${o}`,{y:-H[o]*yb,z:H[o]*vb})}}const nt=i=>i.busy.has("r")?"l":"r",Xf=(i,e)=>{const t=e===H.l?"l":e===H.r?"r":null;return t&&!i.busy.has(t)?t:nt(i)};function $a(i,e,t){de(i,t),ve(i,e),i.swing(Ee(t))}function Dw(i,e,t){const n=Math.max(Ee(t,2),0);se(i,{lean:4*n,nod:26*n}),ve(i,e)}const $s={at:[0,-.62,1.95],apart:.07,circle:.13,nod:8,turn:70};function Nw(i,e,t){const n=ie.hand_rub,s=Vt(t,n.frames),r=me(s,n.together)*(1-me(s,n.apart)),o=2*Math.PI*n.rubs*mt(s,n.together[1],n.apart[0]);de(i,0),se(i,{lean:4*r,nod:$s.nod*r*(.5+.5*Math.sin(2*o))}),i.putAway(...Mt),ve(i,e,r?Object.keys(H):[]);const[a,c,l]=$s.at;for(const[h,u]of Object.entries(H)){const d=new v(a+u*($s.apart+$s.circle*Math.cos(o)),c,l+u*$s.circle*Math.sin(o));r&&lt(i,h,r,i.withinReach(h,i.carried(d),.97),new v(...z.elbow))}Ke(i,"amused",r),Math.abs(Math.sin(Qe(i.facing??0)))<.5&&i.revolve($s.turn*r)}function Uw(i,e,t){se(i,{turn:28*Ee(t,2),tilt:4*Ee(t,2)}),ve(i,e)}function Ow(i,e,t){const n=nt(e),s=H[n];se(i,{twist:-s*4,turn:-s*8,tilt:-s*6}),ve(i,e,[n]),qf(i,n,t)}function qf(i,e,t){i.turn(`upper_arm_${e}`,{x:-85}),i.turn(`upper_arm_${e}`,{z:H[e]*kf}),i.bend(`forearm_${e}`,zf+Hf*Ee(t))}const dn={tilt:22,nod:-12,sway:4,cheek:[.38,-.78,2.6],finger:[.2,.15,1],elbow:[.1,-.5,-1],inboard:.1,under:.12,folded:[1,-.6,-.4],glance:[.35,.3],gotIt:[.85,-.45,2.75]};function Fw(i,e,t,n,s,r){lt(i,e,t,n.clone().addScaledVector(s,-Pi.grip),r),i.aim(`hand_${e}`,new v(0,0,-1).lerp(s,t).normalize())}function Bw(i,e,t,n){const s=i.head(`forearm_${t}`,i.matrix(`forearm_${t}`)),r=new v(s.x*dn.inboard,s.y,s.z-dn.under);lt(i,e,n,i.withinReach(e,r,.97),new v(...dn.folded))}function kw(i,e,t,{thinking:n,sway:s,got:r,raised:o}){const a=nt(e),c=a==="l"?"r":"l",l=H[a];de(i,t),se(i,{nod:dn.nod*n-10*r,tilt:-l*(dn.tilt*n+dn.sway*s),turn:3*s}),i.putAway(...Mt),ve(i,e,[...n+r?[a]:[],...n?[c]:[]]),n+r&&jf(i,a,Math.max(n,r),o),n&&Bw(i,c,a,n),i.glanceEyes(dn.glance[0]*n,-l*dn.glance[1]*n),Ke(i,"startled",r)}function jf(i,e,t,n=0){const s=H[e],[r,o,a]=dn.cheek,c=new v(s*r,o,a).applyMatrix4(i.matrix("head")),[l,h,u]=dn.gotIt,d=i.carried(new v(s*l,h,u+Pi.grip)),[f,m,_]=dn.finger;Fw(i,e,t,c.lerp(d,n),new v(-s*f,m,_).normalize(),new v(...dn.elbow))}const qc=i=>(e,t,n)=>{const s=Vt(n,i.frames),r=i.cloud?me(s,i.into)*(1-me(s,i.rise)):0,o=!!i.lights,a=o?me(s,i.rise)*(1-me(s,i.fades)):0;kw(e,t,n,{thinking:r,sway:(i.sways?Math.sin(2*Math.PI*i.sways*s):0)*r,got:a,raised:o?me(s,i.rise):0}),o&&s>=i.appears[0]&&e.lightBulb(me(s,i.appears)*(1-me(s,i.goes)),me(s,i.lights)*(1-me(s,i.fades)),H[nt(t)])};function zw(i,e,t){const n=Math.max(Math.sin(2*Math.PI*2*t),0);i.lift("root",{z:.28*n}),i.turn("hips",{z:6*Ee(t,2)}),se(i,{lean:-5,turn:-6*Ee(t,2)});const s=Object.keys(H).filter(r=>!e.busy.has(r));ve(i,e,s);for(const r of s)H[r],sn(i,r,1,{y:-Xa,bend:10+6*Ee(t,4)});for(const r of Object.keys(H))i.turn(`thigh_${r}`,{x:-18*n}),i.turn(`shin_${r}`,{x:34*n}),i.turn(`foot_${r}`,{x:-10*n})}function Hw(i,e,t){const n=t*(z.yawnFrames+to);if(n<z.yawnFrames)return op(i,e,n/z.yawnFrames);const s=Ee((n-z.yawnFrames)/to);se(i,{lean:4+1.5*s,nod:8+2*s,tilt:H[nt(e)]*Sw}),ve(i,e),i.shutEyes(0)}function Gw(i,e,t){i.stride=t;const n=2*Math.PI*t;Rh(i),i.turn("hips",{z:5*Math.sin(n)}),se(i,{lean:3,twist:-7*Math.sin(n),turn:3*Math.sin(n)}),ve(i,e,[],{l:22*Math.sin(n),r:-22*Math.sin(n)}),Ch(i)}function Rh(i){i.lift("root",{z:.05*Math.cos(4*Math.PI*i.stride)})}function Ch(i,e=1){for(const[t,n]of[["l",0],["r",Math.PI]]){const s=2*Math.PI*i.stride+n,r=-30*e*Math.sin(s),o=42*e*Math.max(Math.cos(s),0);i.turn(`thigh_${t}`,{x:r}),i.turn(`shin_${t}`,{x:o}),i.turn(`foot_${t}`,{x:-.8*(r+o)+6*e})}}const Ra=4.4,$f=.72,Yf=.94,Ph=[1.84,.38,.2],Lh=[1.36,.6,.16],wd=.14,Vw=.2,Ww=68,Xw=1.25,qw=2.91,jc={back:.58,up:.36,rise:.38},jw=new v(1,-1,-1);function Ci(i){return i=Math.min(Math.max(i,0),1),i*i*(3-2*i)}function Vt(i,e){return Math.min(Math.max(i*e/(e-1),0),1)}const mt=(i,e,t)=>Math.min(Math.max((i-e)/(t-e),0),1),ce=(i,e,t)=>Ci(mt(i,e,t)),Ge=(i,e,t)=>Math.sin(Math.PI*mt(i,e,t)),Bt=(i,e,t)=>i+(e-i)*t,bd=(i,e,t)=>Math.exp(-t*i)*Math.sin(2*Math.PI*e*i)*(1-i);function $w(i,e){return i!=="pull_ups"||!(e.busy.size||e.level.size)}function $c(i){i.lift("root",{z:Vw}),i.putAway(...xn.satOn)}const Vi={lean:-24,feet:18,hands:[.62,.5],floor:1.4};function Yw(i){for(const e of Object.keys(H))i.turn(`thigh_${e}`,{x:-88}),i.turn(`foot_${e}`,{x:Vi.feet});se(i,{lean:Vi.lean,nod:-Vi.lean*.6});for(const[e,t]of Object.entries(H)){const n=new v(t*Vi.hands[0],Vi.hands[1],Vi.floor);lt(i,e,1,i.withinReach(e,n,.97),new v(.6,1,0)),i.face(`hand_${e}`,{x:-80})}}const Hr={feet:[.3,-.72,1.5],hands:[.78,-.05],nod:-4,floor:Vi.floor};function Kw(i){for(const[e,t]of Object.entries(H)){const[n,s,r]=Hr.feet;i.step(e,new v(t*n,s,r),new v(0,-1,1))}se(i,{nod:Hr.nod});for(const[e,t]of Object.entries(H)){const n=new v(t*Hr.hands[0],Hr.hands[1],Hr.floor);lt(i,e,1,i.withinReach(e,n,.97),new v(1,.3,0)),i.face(`hand_${e}`,{x:-80})}}function Zw(i){for(const[e,t]of Object.entries(H))i.turn(`thigh_${e}`,{x:-66}),i.bend(`shin_${e}`,Ww+t*9*i.sway),i.turn(`foot_${e}`,{x:-t*5*i.sway+(e==="r"?i.tap:0)})}function Li(i,e){i.posture==="stand"&&(i.lift("root",{z:-e}),ts(i,e))}function Ya(i,e,t,n,s=Gf){ve(i,e,[...e.free]);for(const r of e.free)lt(i,r,t,i.carried(new v(H[r]*n[0],n[1],n[2])),new v(...s))}const Kf={hearts:{open:1,tint:null,hearts:!0},amused:{open:.3,tint:[1,.85,.4]},startled:{open:1.5,tint:[1,1,1]},worried:{open:.7,tint:[.6,.75,1]},angry:{open:.45,tint:[1,.35,.3]},reading:{open:.8,tint:null},admiring:{open:1.2,tint:[1,.86,.5]},serene:{open:.35,tint:[1,.93,.62]}},Sd={open:.42,cycles:6};function Zf(i,e,t){i.shutEyes(Bt(1,Sd.open,t)),t>.5&&i.tintEyes(new Ve().setHSL(e*Sd.cycles%1,1,.6).toArray())}function Ke(i,e,t=1){const{open:n,tint:s,shape:r}=Kf[e];i.shutEyes(Bt(1,n,t)),s&&t>.5&&i.tintEyes(s),r&&i.shapeEyes(r,t)}const _a=[.3,-.45,2],Jw=[.46,-.82,2.04];function Qw(i,e,t){const n=Ge(t,.55,.75),s=(1-n)*Ee(t,6);de(i,0),se(i,{lean:6,nod:20-4*n,turn:2*Ee(t)}),Ya(i,e,1,[_a[0],_a[1],_a[2]+.035*s]),i.holdLaptop(),Ke(i,"reading")}function eb(i,e,t){const n=Vt(t,ie.joy.frames),s=Math.max(Math.sin(2*Math.PI*ie.joy.jumps*mt(n,.06,.94)),0)*(1-.3*n);i.lift("root",{z:.32*s}),de(i,0),se(i,{lean:-5*s,nod:-14+4*s}),Wn(i,e,0,70+55*s,6*Ee(t,4)),ns(i,.5*s)}function tb(i,e,t){const n=Vt(t,28),s=ce(n,0,.2)*(1-ce(n,.82,1)),r=Ge(n,.28,.82);de(i,0),se(i,{lean:4*s,nod:10*s,turn:24*r*Ee(mt(n,.28,.82),1.5)}),Ya(i,e,s,Jw);for(const o of e.free)i.face(`hand_${o}`,{z:-H[o]*90*s});Ke(i,"worried",s)}function nb(i,e,t){const n=Vt(t,24),s=Ge(n,.05,.9);de(i,0),se(i,{lean:-10*s,nod:-10*s}),Wn(i,e,0,100*s),i.shutEyes(1-.9*Ge(n,.2,.75))}function ib(i,e,t,n){i=(i%1+1)%1;const s=e*t;if(i<t)return[-s/2+e*i,0];const r=(i-t)/(1-t);return[s/2-s*Ci(r),n*Math.sin(Math.PI*r)]}function Ka(i,e,t,n,s,r=0){const o=i.rig.heads.get(`thigh_${e}`),a=i.rig.heads.get(`shin_${e}`),c=i.rig.heads.get(`foot_${e}`),l=o.z-a.z,h=a.z-c.z,u=l+h+s-n,d=(t*t+u*u-l*l-h*h)/(2*l*h);if(d<-1-1e-10||d>1+1e-10)throw new RangeError(`${e} stride target is outside the unchanged leg reach`);const f=Math.acos(Math.round(d*1e10)/1e10),m=Math.atan2(t,u)-Math.atan2(h*Math.sin(f),l+h*Math.cos(f));i.turn(`thigh_${e}`,{x:m*180/Math.PI}),i.bend(`shin_${e}`,f*180/Math.PI),i.face(`foot_${e}`,{x:r})}function Za(i,e,t,n,{running:s=!1,lean:r=s?10:3,clearance:o,apart:a=[],drop:c=0,bend:l={},behind:h=0}={}){const[u,d,f]=s?Ph:Lh,m=t%.5,_=s&&m>d?Math.max(0,Math.sin(Math.PI*(m-d)/(.5-d))):0,g=n*(-(s?.075:.11)+(s?.055*_:0))-c;i.lift("root",{z:g}),de(i,0),se(i,{...l,lean:r*n+(l.lean??0),nod:(s?-6:-2)*n+(l.nod??0)});const p=(s?24:14)*Ee(t)*n,y=e.carried??e.busy,M=Object.keys(H).filter(x=>s&&!y.has(x)&&!e.level.has(x)&&!a.includes(x));ve(i,e,[...M,...a],Object.fromEntries(Object.entries(H).map(([x,E])=>[x,y.has(x)?0:E*p])));for(const x of M)Wf(i,x,H[x]*p,10+40*n);if(n>0||c||h)for(const[x,E]of[["l",0],["r",.5]]){const[T,P]=ib(t+E,u,d,o??f),C=(t+E)%1,b=C>=d?(C-d)/(1-d):0,w=(s?14:11)*Math.sin(Math.PI*b)*n;Ka(i,x,n*T+h,n*P,g,w)}}function Ar(i,e,t,n,s,r={}){const o=mt(t,0,n),a=Ci(o);return i.lift("root",{y:Ra*(1-a)}),Za(i,e,Ra*a/(r.running?Ph:Lh)[0],1-Ci((o-.76)/.24),r),90*(1-ce(t,n,s))}function go(i,e,t,n,s,r={}){const o=mt(t,n+wd/2,1),a=(o<.3?o*o/.6:o-.15)/.85;return i.lift("root",{y:-Ra*a}),Za(i,e,Ra*a/(r.running?Ph:Lh)[0],Ci(o/.25),r),s*90*ce(t,n,n+wd)}function Jf(i,e,t,n,s=!1){i.revolve(Ar(i,e,Vt(t,n),$f,Yf,{running:s}))}function sb(i,e,t){Jf(i,e,t,40)}function rb(i,e,t){Jf(i,e,t,28,!0)}const Yc={grip:[.32,-.55,2.55],reach:.55,knee:48};function ob(i,e,t){const n=Math.sin(2*Math.PI*t);de(i,0),se(i,{lean:10,nod:-8}),i.putAway(...Mt),ve(i,e,Object.keys(H));const[s,r,o]=Yc.grip;for(const[a,c]of Object.entries(H)){const l=(1+c*n)/2;lt(i,a,1,i.withinReach(a,i.carried(new v(c*s,r,o+Yc.reach*l)),.97),new v(c,.4,-.6)),i.face(`hand_${a}`,{x:-90});const h=Yc.knee*(1-l);i.turn(`thigh_${a}`,{x:-h}),i.turn(`shin_${a}`,{x:h*1.2})}}function ab(i,e,t){if(!$w("pull_ups",e)){$a(i,e,t);return}Qf(i,e,t,{pull:.5-.5*Math.cos(2*Math.PI*t),swing:0})}const Ed=i=>(e,t,n)=>Qf(e,t,n,{pull:0,swing:Ee(n),grips:[i]});function Qf(i,e,t,{pull:n,swing:s,grips:r=Object.keys(H)}){const o=r.filter(a=>e.free.has(a));i.lift("root",{y:jc.back,z:jc.up+jc.rise*n}),se(i,{nod:-3*n,turn:2*s}),ve(i,e,o);for(const[a,c]of Object.entries(H))i.turn(`thigh_${a}`,{x:-8+7*s*c}),i.bend(`shin_${a}`,18+8*s*c),i.turn(`foot_${a}`,{x:-10}),o.includes(a)&&(i.reach(a,new v(c*Xw,0,qw),jw),i.face(`hand_${a}`,{x:-90}))}const cb=36,lb=28,Gr=.5,Td=.36,hb=16,ub=7,Ad=-2.45,Rd=-1.54,Kc=new v(1,-.6,.02),db=new v(1,-1,-1),fb=new v(0,1,0),pb={y:-15,z:-10,bend:15},mb=.97,_o=new v(...Gf),Yi=.24,ep=.1,gb=6.04,_b=10.36,ia=.52,Vr=.42,Cd=.6,xb={y:60,z:-10,bend:15},vb=60,yb=45,tp={y:30,z:-25,bend:10},Mb={y:0,z:-15,bend:0};function sn(i,e,t,{y:n=Cs,x:s=0,z:r=0,bend:o=10}){const a=H[e];i.turn(`upper_arm_${e}`,{y:a*Bt(Cs,n,t)}),i.turn(`upper_arm_${e}`,{x:s*t}),i.turn(`upper_arm_${e}`,{z:a*r*t}),i.bend(`forearm_${e}`,Bt(10,o,t))}function lt(i,e,t,n,s){const r=i.head(`upper_arm_${e}`,i.standing(`upper_arm_${e}`)),o=n.clone().sub(r),c=new v(H[e]*Math.cos(Qe(Cs)),0,-Math.sin(Qe(Cs))).lerp(o.clone().normalize(),t).normalize();i.reach(e,r.clone().add(c.multiplyScalar(Bt(mb,o.length(),t))),fb.clone().lerp(s,t))}const xo=i=>new v(H[i]*Wc[0],Wc[1],Wc[2]);function ts(i,e){for(const t of Object.keys(H))Ka(i,t,0,0,-e)}function wb(i,e,t){[...e.level].sort().forEach((n,s)=>{const r=Math.max(t-.05*s,0);i.turn(`hand_${n}`,{x:hb*bd(r,3,2.5),y:H[n]*ub*bd(r,2.5,3)})})}const np=(i,e)=>e.reduce((t,n)=>t+Ge(i,n,n+.05),0),Rr=i=>[...i.carried].filter(e=>!i.busy.has(e));function bb(i,e,t){const n=Ge(t,Gr,Gr+.22),s=Ar(i,e,t,Gr,Gr+.14,{running:!0,lean:15,drop:.12*n,bend:{lean:-7*n,nod:5*n}});wb(i,e,mt(t,Gr,1)),i.revolve(s)}function Sb(i,e,t){const n=Ge(t,0,Td);i.revolve(go(i,e,t,Td,-1,{bend:{lean:30*n,nod:24*n}}))}function Eb(i,e,t){const n=mt(t,.55,.72),s=t<.72?0:Yi*(1-ce(t,.84,1)),r=t<.55?Bt(-4.4,Ad,ce(t,0,.16))+(Rd-Ad)*ce(t,.3,.55):t<.72?Bt(Rd,-Yi,n)+1.2*Math.sin(Math.PI*n):-s;i.lift("root",{z:r}),de(i,0),se(i,{turn:25*Math.sin(2*Math.PI*mt(t,.06,.2)),lean:14*(s/Yi)+8*ce(t,.3,.55)*(1-n),nod:-10*Ge(t,.86,1)});const o=t>=.2&&t<.55?ce(t,.2,.27):0,a=Ge(t,.55,.74);ve(i,e,o||a?Object.keys(H):[]);for(const c of Object.keys(H))o?(lt(i,c,o,new v(H[c]*Kc.x,Kc.y,Kc.z),db),i.face(`hand_${c}`,{z:-H[c]*90*o})):a&&sn(i,c,a,pb);ts(i,t<.72?Bt(0,Yi,n)+ep*Math.sin(Math.PI*n):s)}function Tb(i,e,t){const n=mt(t,.3,1),s=ce(t,.05,.3),r=ce(t,.3,.42);i.lift("root",{y:-2.4*n,z:t<.3?-Yi*s:-Yi+gb*n-_b*n*n}),de(i,0),se(i,{lean:15*s*(1-r),nod:18*s*(1-r)});for(const o of Object.keys(H))sn(i,o,s,{y:Bt(Cs,-15,r),x:Bt(40,0,r),z:-10*r,bend:10});ts(i,t<.3?Yi*s:Yi*(1-r)+2*ep*Ge(t,.36,.62)),i.revolve(-35*ce(t,0,.2))}function Ab(i,e,t){const n=[...e.busy],s=Rr(e),r=1-ce(t,.7,.92),o=Ge(t,ia,ia+.2),a=Ar(i,e,t,ia,ia+.14,{running:!0,lean:14,apart:[...n,...s],drop:.14*o,bend:{lean:-6*o}});n.forEach(c=>sn(i,c,r,xb)),s.forEach(c=>sn(i,c,r,tp)),i.shutEyes(1-.45*r),i.revolve(a)}function Rb(i,e,t){const n=Rr(e),s=ce(t,0,.12)*(1-ce(t,.24,.34)),r=go(i,e,t,.34,-1,{clearance:.18,lean:0,apart:s?n:[],bend:{nod:10*Ge(t,.1,.26)}});s&&n.forEach(o=>lt(i,o,s,xo(o),_o)),i.revolve(r)}function Cb(i,e,t){const n=nt(e),s=ce(t,Vr,Vr+.04)*(1-ce(t,.62,.7)),r=6*mt(t,Vr,.7),o=-.05*s*Math.abs(Ee(r)),a=ce(t,.7,.76)*(1-ce(t,.9,.98)),c=np(t,[.77,.83]);i.lift("root",{z:o});const l=Ar(i,e,t,Vr,Vr+.1,{running:!0,lean:6,apart:a?[n]:[],bend:{nod:7*c,lean:2*c}});if(a&&lt(i,n,a,xo(n),_o),s)for(const[h,u]of[["l",0],["r",.5]])Ka(i,h,0,.22*s*Math.max(Ee(r+u),0),o);i.shutEyes(1-.6*c),i.revolve(l)}function Pb(i,e,t){const n=nt(e),s=ce(t,0,.06)*(1-ce(t,.2,.26)),r=ce(t,.26,.32)*(1-ce(t,.42,.5)),o=np(t,[.07,.13]),a=go(i,e,t,.4,H[n],{running:!0,lean:6,apart:s||r?[n]:[],bend:{nod:7*o,lean:2*o}});s&&lt(i,n,s,xo(n),_o),r&&sn(i,n,r,Mb),i.shutEyes(1-.6*o),i.revolve(a)}function Lb(i,e,t){const n=ce(t,.72,.8)*(1-ce(t,.9,.98)),s=Ge(t,.78,.92),r=[...e.level].sort(),o=Ar(i,e,t,Cd,Cd+.12,{apart:n?r:[],bend:{nod:-8*s}});n&&ap(i,e,n,s),i.shutEyes(1-.7*s),i.revolve(o)}function Ib(i,e,t){const n=nt(e),s=ce(t,0,.08)*(1-ce(t,.24,.32)),r=go(i,e,t,.3,H[n],{apart:s?[n]:[],bend:{tilt:-H[n]*5*s}});s&&sn(i,n,s,{y:0,x:-85,z:kf,bend:zf+Hf*Ee(mt(t,0,.32),2)}),i.revolve(r)}function Db(i,e,t){i.revolve(Ar(i,e,t,$f,Yf))}function Nb(i,e,t){i.revolve(go(i,e,t,0,-1))}const Ub={bare:Db,butler:bb,homie:Eb,squire:Ab,coach:Cb,colleague:Lb},Ob={bare:Nb,butler:Sb,homie:Tb,squire:Rb,coach:Pb,colleague:Ib};function Fb(i,e,t){Ub[e.voice](i,e,Vt(t,cb))}function Bb(i,e,t){Ob[e.voice](i,e,Vt(t,lb))}const kb=.2,sa={sweep:14,lean:10,nod:16,turn:70},Pd=(i,e,t)=>i.clone().add(e.clone().sub(i).setLength(t)),zb=1.4,Ld=.13;function Hb(i){return ce(i,0,.22)-2*ce(i,.32,.62)+ce(i,.7,.85)}function Gb(i,e,t){const n=H[nt(e)],s=Hb(t);Li(i,kb),de(i,0),se(i,{lean:sa.lean,nod:sa.nod,turn:n*sa.sweep*s}),ve(i,e),Ke(i,"reading"),i.posture==="stand"&&i.revolve(n*sa.turn)}const fs={depth:.3,ahead:[1.6,.3,.2],out:1.25,share:.8,lean:8,size:1.2};function Vb(i,e){return i.at?new v((i.at.x-.5)*Ht,e,Nn+(.5-i.at.y)*Ht).applyAxisAngle(new v(0,0,1),Qe(-i.facing)):null}function Wb(i,e,t){const{wall:n,contact:s,tilt:r,hip:o,inner:a,outer:c}=ie.lean,l=i.leanWay||1,h=l===H.l?"l":"r",u=h==="l"?"r":"l";i.turn(`thigh_${h}`,{y:H[h]*a}),i.turn(`thigh_${u}`,{y:H[u]*c,x:-12});const d=l*r*(1+.06*Ee(t));i.turn("root",{y:d}),de(i,t),se(i,{tilt:-d*.4}),ve(i,e,[h,...e.free.has(u)?[u]:[]]),lt(i,h,1,i.withinReach(h,i.carried(new v(l*n*Ht,0,s)),.99),new v(l,.2,-1)),i.face(`hand_${h}`,{z:-H[h]*90});const f=new v(H[u]*o[0],o[1],o[2]).applyAxisAngle(new v(0,1,0),Qe(d));e.free.has(u)&&lt(i,u,1,i.withinReach(u,i.carried(f),.97),new v(H[u],.3,0)),Ke(i,"amused",.4)}function Xb(i,e,t){const n=i.rig.eyes.reduce((p,y)=>p.add(y),new v).divideScalar(i.rig.eyes.length).applyMatrix4(i.matrix("head")),[s,r,o]=fs.ahead,a=Vb(i,fs.depth)??n.clone().add(new v(H[nt(e)]*s,r,o)),c=Xf(e,Math.sign(a.x-n.x));de(i,t),ve(i,e,[c]),se(i,{tilt:-H[c]*fs.lean});const l=a.clone().sub(n),h=Ft.radToDeg(Math.atan2(l.x,-l.y)),u=Ft.radToDeg(Math.atan2(-l.z,Math.hypot(l.x,l.y))),d=new v(0,0,1).applyMatrix4($i(u,0,h)),f=p=>{const y=i.carried(p.clone().addScaledVector(d,-(ho.handle/2+ho.radius)*fs.size));return i.withinReach(c,y,.97).distanceTo(y)<.02},m=Math.min(fs.out,l.length()*fs.share),_=Array.from({length:8},(p,y)=>m*(1-y/10)),g=Pd(n,a,_.find(p=>f(Pd(n,a,p)))??_.at(-1));cp(i,c,1,g,0,{tip:u,roll:0,slant:h,size:fs.size}),Ke(i,"reading")}const vt={intro:12,hold:48,outro:12,fps:12,ready:3,opens:11,pageEvery:24,pageFrom:12,pageTo:20,lines:4,referenceArm:.985,forward:.68,drop:.3,drawDrop:.18,elbow:[1,-1,-1],wristTurn:90},Yl=vt.intro+vt.hold+vt.outro,Pi={grip:.34,forward:.02},z={intro:8,hold:32,outro:8,fps:12,yawnFrames:28,pastimeFrames:40,greetingFrames:24,hopFrames:20,stumbleFrames:24,elbow:[1,-.15,-.35],wrist:[.72,-.72,1.76],supportLift:.22,whistleLift:.25,clothLift:.2,clothTurn:-90,compactFps:6,tap:10,rock:3,turn:12,nod:8,writeStroke:.035,writeHeight:.02,glance:22,hop:.18,stumble:12,writingWrist:[.38,-.76,2.1],yawnWrist:[.48,-.86,2.12],whistleWrist:[.48,-.82,2.2],sipWrist:[.7,-.63,2.17],shieldWrist:[.22,-.64,2.13],wipeWrist:[.1,-.7,1.9],saluteWrist:[1.28,-.32,2.59],gestureIn:.2,gestureOut:.8,yawnEyes:.94,yawnSpan:[.08,.92],pastimeSpan:[.3,.7],whistleEyes:.65,sipEyes:.5,sipTip:12,grooveEyes:.4,beats:4,sways:2,wipes:3,wipeLift:.035,wipeAcross:.04,bowLean:18,bowNod:10,leapSpan:[.18,.78],catchSpan:[.15,.45],recoverSpan:[.45,.85],recover:.3},ip={butler:"writing_stylus",coach:"writing_pencil",colleague:"writing_pen",homie:"writing_marker",squire:"writing_quill"},Ca=z.intro+z.hold+z.outro,hn={intro:8,hold:144,outro:8,whistleSpan:[.7,.98],beats:12,sways:3},Kl=hn.intro+hn.hold+hn.outro,xa={across:.04,top:.52,bottom:.44,forward:[0,-1,0]};function sp(i){const e=i*Ca,t=e>=z.intro&&e<z.intro+z.hold,n=e<z.intro?e:Ca-1-e;return{frame:e,held:t,ready:t?1:ce(n,0,z.intro-1),phase:t?(e-z.intro)/z.hold:0}}function qb(i){const e=i*Kl,t=e>=hn.intro&&e<hn.intro+hn.hold,n=e<hn.intro?e:Kl-1-e;return{ready:t?1:ce(n,0,hn.intro-1),phase:t?(e-hn.intro)/hn.hold:0}}function Vn(i,e){const t=Vt(i,e);return{u:t,ready:ce(t,0,z.gestureIn)*(1-ce(t,z.gestureOut,1))}}function jb(i,e,t=[0,0,0]){return i.rig.heads.get(`hand_${e}`).clone().add(new v(H[e]*(Pi.grip+t[0]),Pi.forward+t[1],t[2])).applyMatrix4(i.matrix(`hand_${e}`))}function rn(i,e,t,n,s={}){t&&(lt(i,e,t,i.carried(new v(H[e]*n[0],n[1],n[2])),new v(...z.elbow)),i.face(`hand_${e}`,{z:-H[e]*90*t,...s}))}const Pa=65,Id={down:35,up:25};function rp(i,e,t=1){const n=i.rig.eyes.reduce((u,d)=>u.add(d),new v).divideScalar(i.rig.eyes.length),s=i.head("head",i.standing("head")),r=e.clone().sub(s),o=n.z-i.rig.heads.get("head").z,a=Bp(r.x,-r.y,r.z,o),c=Ft.clamp(a.pitch,Qe(-Id.up),Qe(Id.down)),l=Ft.radToDeg(a.yaw),h=Ft.clamp(l,-Pa,Pa);return i.face("head",{x:Ft.radToDeg(c)*t,z:h*t}),i.gaze={target:e.toArray(),forward:xa.forward},(l-h)*t}function $b(i,e,t){const n=t*Yl,s=n>=vt.intro&&n<vt.intro+vt.hold,r=n<vt.intro?n:Yl-1-n,o=s?1:ce(r,0,vt.ready),a=s?1:ce(r,vt.ready,vt.opens),c=s?(n-vt.intro)%vt.pageEvery:0,l=s?ce(c,vt.pageFrom,vt.pageTo):0;de(i,0),ve(i,e);const h=Math.min(...Object.keys(H).map(x=>{const E=T=>i.rig.heads.get(`${T}_${x}`);return E("upper_arm").distanceTo(E("forearm"))+E("forearm").distanceTo(E("hand"))}))/vt.referenceArm,u=Object.keys(H).map(x=>i.head(`upper_arm_${x}`,i.standing(`upper_arm_${x}`))),d=u[0].clone().add(u[1]).multiplyScalar(.5),f=Mp(a),m=Ki("l",a).add(Ki("r",a)).multiplyScalar(.5).applyMatrix4(f),_=new v(d.x-m.x*h,d.z-(vt.drop+vt.drawDrop*(1-o))*h-m.y*h,-d.y+vt.forward*h-m.z*h),g=new Ae().makeTranslation(_.x,_.y,_.z).multiply(f).scale(new v(h,h,h));for(const[x,E]of Object.entries(H)){const T=Aa(Ki(x,a).applyMatrix4(g));if(!o)continue;lt(i,x,o,T,new v(...vt.elbow));const P=Ft.radToDeg(Math.atan2(Ue.closedGrip*(1-a),Ue.gripBack));i.face(`hand_${x}`,{z:-E*(vt.wristTurn+P)*o})}const p=Math.floor(c/(vt.pageEvery/vt.lines)),y=c%(vt.pageEvery/vt.lines)/(vt.pageEvery/vt.lines-1),M=new v(Bt(-.04,xa.across,y),Bt(xa.top,xa.bottom,p/(vt.lines-1)),-Ue.pages).applyMatrix4(g);rp(i,Aa(M),a),i.holdBook(a,l,s||r>=vt.ready),Ke(i,"reading",a)}function Yb(i,e,t){const{ready:n,phase:s}=qb(t),r=e.voice==="butler",o=Ge(s,...hn.whistleSpan)*n;de(i,0),se(i,{turn:z.turn*n,nod:-z.nod*o/2,lean:z.rock*Ee(s,hn.sways)*(r?o:n)}),ve(i,e),i.tap=z.tap*Math.max(Ee(s,hn.beats),0)*n,i.posture==="stand"&&i.turn("foot_r",{x:i.tap}),o&&i.shutEyes(1-z.whistleEyes*o)}function op(i,e,t){const{u:n,ready:s}=Vn(t,z.yawnFrames),r=nt(e);de(i,0),se(i,{lean:-z.rock*s,nod:-z.nod*s}),ve(i,e),rn(i,r,s,z.yawnWrist),s&&i.putAway(...Mt),i.shutEyes(1-z.yawnEyes*Ge(n,...z.yawnSpan))}function Kb(i,e,t){const{u:n,ready:s}=Vn(t,z.pastimeFrames),r=Ge(n,...z.pastimeSpan),o=nt(e);de(i,0),se(i,{lean:-z.rock*r,nod:-z.nod*r}),ve(i,e),rn(i,o,s,z.whistleWrist),s&&i.putAway(...Mt,"coach_whistle"),s>.5&&i.holdProp("hand_whistle",o,[0,0,z.whistleLift],{z:H[o]*90}),i.shutEyes(1-z.whistleEyes*r)}const Dt={frames:120,fps:8,down:[0,.1],up:[.9,1],tunes:[[.3,.45],[.62,.8]],beats:40,pillow:[0,1,3.2],tilt:72,across:-1.6,kneeUp:60,kneeBend:105,glance:40,ankle:[-.15,-.15,-.1],crossedKnee:[1,-.4,.6],footBob:18,wrist:[.6,.55,2.85],fingers:[-1,.4,.4],elbow:[1,-.3,.8],straw:[.14,-.9,.4],strawTip:115,strawWag:8,eyes:.45,whistleEyes:.2},Zb=i=>Dt.tunes.reduce((e,[t,n])=>e+Ge(i,t,n),0);function Jb(i,e,t){const n=Vt(t,Dt.frames),s=ce(n,...Dt.down)*(1-ce(n,...Dt.up)),r=Zb(n),o=Math.max(Ee(n,Dt.beats),0);if(de(i,0),ve(i,e,s?Object.keys(H):[]),!s)return;i.putAway(...Mt),se(i,{turn:-Dt.glance*s});for(const[h,u]of Object.entries(H)){const[d,f,m]=Dt.wrist;lt(i,h,s,new v(u*d,f,m),new v(...Dt.elbow));const[_,g,p]=Dt.fingers;i.aim(`hand_${h}`,new v(u*_,g,p))}i.turn("thigh_l",{x:-Dt.kneeUp*s}),i.bend("shin_l",Dt.kneeBend*s);const a=i.head("shin_l",i.matrix("shin_l")),c=i.head("foot_r",i.standing("foot_r"));i.step("r",c.lerp(a.add(new v(...Dt.ankle)),s),new v(...Dt.crossedKnee)),i.turn("foot_r",{x:-Dt.footBob*r*o}),i.wearProp("straw",Dt.straw,{x:Dt.strawTip+Dt.strawWag*(1+r)*Ee(n,9)});const l=new v(...Dt.pillow);i.turnAll({x:-Dt.tilt*s},l),i.turnAll({z:90*s},l),i.offsetAll([Dt.across*s,-l.y*s,-l.z*s]),i.shutEyes(Bt(1,Bt(Dt.eyes,Dt.whistleEyes,r),s))}function ap(i,e,t,n){for(const s of e.level)rn(i,s,t,z.sipWrist,{x:-z.sipTip*n})}function Qb(i,e,t){const{u:n,ready:s}=Vn(t,z.pastimeFrames);de(i,0),se(i,{nod:-z.rock*s}),ve(i,e),ap(i,e,s,Ge(n,...z.pastimeSpan)),i.shutEyes(1-z.sipEyes*Ge(n,...z.pastimeSpan))}function eS(i,e,t){const{u:n,ready:s}=Vn(t,z.pastimeFrames);de(i,0),se(i,{nod:z.nod*Ee(n,z.beats)*s,tilt:z.rock*Ee(n,z.sways)*s}),ve(i,e),i.swing(Ee(n,z.sways)*s),i.shutEyes(1-z.grooveEyes*s)}function tS(i,e,t){const{u:n,ready:s}=Vn(t,z.pastimeFrames),r=[...e.shield][0];if(!r)return $a(i,e,t);const o=r==="l"?"r":"l";de(i,0),se(i,{nod:z.nod*s}),ve(i,e),rn(i,r,s,z.shieldWrist),rn(i,o,s,[z.wipeWrist[0],z.wipeWrist[1]+z.wipeAcross*Ee(n,z.wipes),z.wipeWrist[2]+z.wipeLift*Ee(n,z.wipes*2)]),s&&(i.putAway("squire_quill"),i.keep.add("squire_shield")),s>.5&&i.holdProp("polishing_cloth",o,[0,0,z.clothLift],{x:z.clothTurn})}function nS(i,e,t){const{ready:n,phase:s}=sp(t),r=z.writeStroke*Ee(s,z.beats);if(de(i,0),se(i,{nod:z.nod*n,lean:z.rock*n}),ve(i,e),rn(i,"l",n,z.wrist),rn(i,"r",n,[z.writingWrist[0]+r,z.writingWrist[1],z.writingWrist[2]]),n&&i.putAway(...Mt),n>=1){const o=e.voice==="butler",a=ln.paper.thickness*(o?2.5:.5),c=z.wrist[2]+z.supportLift+a+ln.pen.length/2+ln.pen.tip-z.writingWrist[2];i.holdProp(ip[e.voice]||"writing_pen","r",[0,0,c],{z:-90}),i.holdProp(e.voice==="butler"?"writing_tablet":"writing_paper","l",[0,-z.wrist[0],z.supportLift],{z:90})}Ke(i,"reading",n)}function iS(i,e,t){const{ready:n,phase:s}=sp(t);de(i,0),se(i,{nod:z.nod*n}),ve(i,e),rn(i,"l",n,z.wrist),rn(i,"r",n,[z.wrist[0]+z.writeStroke*Ee(s,z.sways),z.wrist[1],z.wrist[2]+z.writeHeight*Math.max(Ee(s,z.sways),0)]),n&&i.putAway(...Mt),n>=1&&(i.holdProp("papers","l",[0,-z.wrist[0],z.supportLift],{z:90}),i.props.get("papers").phase=s)}function sS(i,e,t){const{ready:n}=Vn(t,z.greetingFrames);de(i,0),se(i,{lean:z.bowLean*n,nod:z.bowNod*n}),ve(i,e),n&&i.putAway(...Mt)}function rS(i,e,t){const{ready:n}=Vn(t,z.greetingFrames),s=nt(e);de(i,0),se(i,{nod:-z.rock*n}),ve(i,e),rn(i,s,n,z.saluteWrist),n&&i.putAway(...Mt)}function oS(i,e,t){const{u:n,ready:s}=Vn(t,z.hopFrames),r=Ge(n,...z.leapSpan);Li(i,z.hop*Ge(n,0,z.leapSpan[0])),i.lift("root",{z:z.hop*r}),de(i,0),se(i,{lean:-z.rock*r}),Wn(i,e,0,Xa*r),i.posture==="stand"&&ns(i,r),Ke(i,"startled",s)}function aS(i,e,t){const{u:n,ready:s}=Vn(t,z.stumbleFrames),r=Ge(n,...z.catchSpan)-z.recover*Ge(n,...z.recoverSpan);de(i,0),se(i,{lean:z.stumble*r,tilt:z.rock*r}),Wn(i,e,0,Xa*s),Ke(i,"startled",Math.max(r,0))}function cS(i,e,t){const{ready:n}=Vn(t,z.greetingFrames);de(i,0),se(i,{turn:z.glance*n,nod:-z.rock*n}),ve(i,e)}const un={blows:1,blowFrames:8,fps:10,lands:.3,snap:50,thumb:90,roll:-90,fist:.62,turn:80,strike:.413,landsAt:[.72,-1.81]};function lS(i){const e=i*un.blows%1;return e<un.lands?1-(e/un.lands)**2:Ci(mt(e,un.lands,1))}function aT(i){const e=H[nt(i)],[t,n]=un.landsAt,s=Qe(e*un.turn);return(e*t*Math.cos(s)-n*Math.sin(s))/Ht}function hS(i,e,t){const n=nt(e),s=Math.max(lS(t),un.strike),r=1-s;Li(i,.04*r),de(i,0),se(i,{lean:8+6*r,nod:10}),ve(i,e,[n]),sn(i,n,1,{y:Bt(75,5,s),z:-35,bend:Bt(15,70,s)}),i.roll(`forearm_${n}`,H[n]*un.roll),i.clench(n,un.fist),i.holdProp("work_hammer",n,[0,0,0],{x:un.thumb,z:H[n]*un.snap*r}),i.posture==="stand"&&i.revolve(H[n]*un.turn)}const $t={frames:60,fps:12,out:[0,.08],along:[.08,.76],pause:[.76,.9],away:[.92,1],turn:65,bend:.35,lean:34,nod:22,nodded:10,box:[.72,-1.81,1.2],between:.5,front:-1.2,sweep:.4,size:1.45,tip:35,slant:-35};function uS(i){const[e,t,n]=$t.box;return new v(i*e,t,n).applyAxisAngle(new v(0,0,1),Qe(i*un.turn))}function dS(i,e,t){const n=uS(e),s=new v(n.x-i.x,0,n.z-i.z).normalize();return{lens:new v(Bt(i.x,n.x,$t.between)+$t.sweep*t,$t.front,Bt(i.z,n.z,$t.between)),way:s}}function cp(i,e,t,n,s,{tip:r,roll:o,slant:a,size:c}){const l=new v(0,0,1).applyMatrix4($i(r,o,a)),h=n.clone().addScaledVector(l,-(ho.handle/2+ho.radius)*c).applyAxisAngle(new v(0,0,1),-s);lt(i,e,t,i.withinReach(e,i.carried(h),.97),new v(...z.elbow)),i.putAway(...Mt),!(t<=.3)&&(i.holdUpright("magnifying_glass",e,[0,0,0],{x:r,y:o,z:a-Ft.radToDeg(s)}),Object.assign(i.props.get("magnifying_glass"),{magnifies:t,size:c,roll:o}))}function fS(i,e,t){const n=nt(e),s=H[n],r=me(t,$t.out)*(1-me(t,$t.away)),o=Math.sin(2*Math.PI*mt(t,...$t.along)),a=Ge(t,...$t.pause),c=new v(0,0,1),l=Qe(s*$t.turn);Li(i,$t.bend*r),de(i,0),se(i,{lean:$t.lean*r,nod:($t.nod+$t.nodded*a)*r}),ve(i,e,[n]);const h=i.rig.eyes.reduce((m,_)=>m.add(_),new v).divideScalar(i.rig.eyes.length).applyMatrix4(i.matrix("head")),{lens:u,way:d}=dS(h.applyAxisAngle(c,l),s,o),f=Ft.radToDeg(Math.atan2(d.x,d.z));cp(i,n,r,u,l,{tip:$t.tip,roll:f,slant:s*$t.slant,size:$t.size}),Ke(i,"reading",r),i.posture==="stand"&&i.revolve(s*$t.turn)}const Xi={step:.6,hop:.12,lean:8,shadeWrist:[1.18,-.5,2.72],shadeHand:[-.35,-1,.2]},La=-1.2,cT=Math.abs(La)/Ht,lT=i=>.5-(i.rig.heads.get("head").z-Nn)/Ht,hT=i=>(i.rig.eyes.reduce((e,t)=>e+t.z,0)/i.rig.eyes.length-i.rig.heads.get("head").z)/Ht;function pS(i,e,t=0){const n=new v((e.x-.5)*Ht,e.behind?-La:La,Nn+(.5-e.y)*Ht),s=i.matrix("head").clone(),r=rp(i,n.applyAxisAngle(new v(0,0,1),Qe(-t))),o=e.amount??1;return o<1&&i.final.set("head",mS(s,i.matrix("head"),o)),r*o*o}function mS(i,e,t){const[n,s]=[i,e].map(r=>{const o={at:new v,turn:new Gn,size:new v};return r.decompose(o.at,o.turn,o.size),o});return new Ae().compose(n.at.lerp(s.at,t),n.turn.slerp(s.turn,t),n.size.lerp(s.size,t))}function gS(i,e,t){const{shade:n,back:s}=i.sky??{shade:0,back:0};i.lift("root",{y:Xi.step*s,z:Xi.hop*Math.sin(Math.PI*s)}),de(i,t),se(i,{lean:-Xi.lean*s});const r=nt(e);if(ve(i,e,n?[r]:[]),n){rn(i,r,n,Xi.shadeWrist);const[o,a,c]=Xi.shadeHand,l=`hand_${r}`,h=i.rig.along.get(l).clone().transformDirection(i.matrix(l));i.aim(l,h.lerp(new v(H[r]*o,a,c),n)),i.putAway(...Mt)}}const vn={lean:34,nod:-42,drop:.25,behind:.2,hands:[.42,-1.3,.6],turn:4,intro:9,stride:6,fps:12};function _S(i){const e=i*(vn.intro+vn.stride);return e>=vn.intro?1:Ci((e-vn.turn)/(vn.intro-vn.turn))}function xS(i,e,t){const n=_S(t);Za(i,e,i.stride,i.posture==="walk"?1:0,{lean:0,drop:vn.drop*n,behind:vn.behind*n,bend:{nod:vn.nod*n}}),i.bendAbove("spine",{x:vn.lean*n});const[s,r,o]=vn.hands;for(const[a,c]of Object.entries(H))lt(i,a,n,i.withinReach(a,new v(c*s,r,o),.97),new v(...z.elbow)),i.face(`hand_${a}`,{z:-c*90*n});i.putAway(...Mt)}function vS(i,e,t){const n=nt(e);de(i,0),se(i,{nod:-14,lean:-3,tilt:-H[n]*5}),ve(i,e,[n]),sn(i,n,1,{y:-12+3*Ee(t),z:-15,bend:10}),Ke(i,"worried",.6)}function Wn(i,e,t,n,s=0){ve(i,e,[...e.free]);for(const r of e.free){const o=H[r],a=Math.min(Math.max(n/yw,0),1);sn(i,r,a,{x:t+s*o,y:-Math.min(n,Xa),bend:10})}}function ns(i,e,t=0){for(const[n,s]of Object.entries(H))i.turn(`thigh_${n}`,{x:-24*e+t*s}),i.turn(`shin_${n}`,{x:44*e}),i.turn(`foot_${n}`,{x:-8*e})}function yS(i,e,t){const n=Vt(t,16),s=ce(n,0,.26)*(1-ce(n,.26,.36)),r=ce(n,.3,.45);i.lift("root",{z:.1*r}),de(i,0),se(i,{lean:14*s-6*r,nod:-4*r}),Wn(i,e,40*s,80*ce(n,.26,.42)*(1-.4*ce(n,.6,1))),ts(i,.28*s),ns(i,r)}const MS=25,wS=360;function bS(i,e,t){const n=Vt(t,22),s=ce(n,0,.26)*(1-ce(n,.26,.34)),r=ce(n,.3,.86),o=ce(n,.28,.4)*(1-ce(n,.86,.95));i.lift("root",{z:.1*o}),de(i,0),se(i,{lean:12*s}),Wn(i,e,30*s,MS*o),ts(i,.28*s),ns(i,1.2*o),i.turnAll({x:wS*r},i.head("hips",i.matrix("hips")))}function SS(i,e,t){const n=Vt(t,12),s=ce(n,0,.2),r=Ge(n,0,.3);i.lift("root",{z:.1*s}),de(i,0),se(i,{lean:-9*s-8*r,nod:-6*s-10*r,tilt:4*Ee(t,3)*s}),Wn(i,e,0,(70+8*Ee(t,3))*s+25*r,14*Ee(t,3)*s),Ke(i,"startled",Math.max(r,.6*s)),ns(i,.5*s,14*Ee(t,3)*s)}function ES(i,e,t){const n=Vt(t,Zl.frames),s=ce(n,0,.2)*(1-ce(n,.2,1));de(i,0),se(i,{lean:16*s,nod:8*s}),Wn(i,e,0,38*s),ts(i,.32*s)}function TS(i,e,t){const n=Vt(t,24),s=n<.5,r=zb*(s?Ci(mt(n,0,.5)):1-Ci(mt(n,.5,1))),o=Math.sqrt(Math.max(Math.sin(Math.PI*n),0)),a=Rr(e);i.lift("root",{y:s?-r:r}),Za(i,e,4*n,o,{running:!0,lean:12,apart:a}),a.forEach(c=>sn(i,c,o,tp)),i.revolve((s?90:-90)*Math.min(1,3*Math.sin(Math.PI*n)))}function Dd(i,e,t){const n=Ld*Math.max(Ee(3*t),0)*Ge(t,0,1);de(i,0),se(i,{tilt:8*Ge(t,0,1),nod:6*Ge(t,0,1),turn:10*Ge(t,0,1)}),ve(i,e),Ka(i,"r",0,n,0,15*n/Ld)}function AS(i,e,t){const n=Ge(t,0,1);de(i,0),se(i,{tilt:14*n,nod:-8*n});for(const s of Object.keys(H))sn(i,s,n,{y:30,z:-15,bend:100})}function RS(i,e,t){const n=nt(e),s=ce(t,0,.15)*(1-ce(t,.8,1)),r=Ge(t,.2,.75);de(i,0),se(i,{lean:-4*r,nod:-6*r}),ve(i,e,s?[n]:[]),s&&lt(i,n,s,xo(n),_o),i.shutEyes(1-.7*r)}function CS(i,e,t){const n=nt(e),s=ce(t,0,.2)*(1-ce(t,.6,.85));de(i,0),se(i,{nod:18*s*(1-ce(t,.35,.5)),turn:-H[n]*8*s}),ve(i,e,s?[n]:[]),s&&lt(i,n,s,xo(n),_o)}function PS(i,e,t){const n=Rr(e),s=ce(t,0,.2)*(1-ce(t,.75,1));de(i,0),se(i,{tilt:-5*s,nod:4*s}),ve(i,e,s?n:[]),s&&n.forEach(r=>sn(i,r,s,{y:30,z:-25+5*Ee(3*t),bend:10}))}const LS={bare:Dd,butler:Dd,homie:AS,coach:RS,colleague:CS,squire:PS};function IS(i,e,t){LS[e.voice](i,e,Vt(t,20))}const fe={frames:36,fps:12,hatOn:1.101,hatWrist:[1.05,-.2,2.85],hatRaised:[.95,-.5,2.85],hatTip:25,hatFingers:.25,hatBow:22,hatNod:14,monocleWrist:[.55,-.8,2.62],monocleWorn:[.354,-.95,.66],monoclePeer:8,monocleTilt:9,toastWrist:[.78,-.72,2.55],toastClink:.12,sipWrist:[.42,-.78,2.38],sipTip:20,shakaWrist:[1.22,-.25,2.72],shakaWaggle:28,shakaWaggles:3,shadesWrist:[.5,-.82,2.55],shadesWorn:[0,-.96,.66],shadesLean:7,shadesTilt:10,fireWrist:[.48,-.86,2.28],fireSize:2.4,thumbWrist:[.62,-.84,2.3],glassesWrist:[.32,-.8,2.47],peerLean:12,peerTurn:18,prayerWrist:[.12,-.62,2],prayerRoll:180,thanksBow:14,popperWrist:[.95,-.45,2.85],popAt:.4,popHop:.12,flex:{y:0,x:-85,z:15,bend:115},flexPump:15,trophy:{y:-55,x:15,z:0,bend:15},trophyHop:.1,sword:{y:-62,x:18,z:0,bend:12},swordThrust:12,shieldWrist:[.24,-.78,2.3],shieldCrouch:.08,shieldBump:.5,castleWrist:[.55,-.88,2.34]},vo=i=>qa.forEach(e=>i.keep.add(e)),bn=i=>Vn(i,fe.frames);function Ii(i,e,t,n,s={}){rn(i,e,t,n,{x:-60*t,...s})}const DS=new v(0,0,1);function NS(i,e,t){const{u:n,ready:s}=bn(t),r=nt(e),o=ce(n,.2,.3)*(1-ce(n,.7,.8)),a=ce(n,.3,.4)*(1-ce(n,.6,.7)),c=Ge(n,.32,.72);if(de(i,0),se(i,{lean:fe.hatBow*c,nod:fe.hatNod*c}),ve(i,e,s?[r]:[]),Ii(i,r,s,fe.hatWrist.map((l,h)=>Bt(l,fe.hatRaised[h],a))),s&&i.aim(`hand_${r}`,i.rig.along.get(`hand_${r}`).clone().transformDirection(i.matrix(`hand_${r}`)).lerp(DS,s)),o){const l={y:H[r]*fe.hatTip*o};i.putAway("butler_top_hat","butler_top_hat_band"),i.wearProp("top_hat",US(i,r,o,l).toArray(),l)}Ke(i,"amused",c)}function US(i,e,t,n){const s=new v(H[e]*(xn.hat.crown+xn.hat.brim),0,0).applyMatrix4($i(0,n.y,0)),o=jb(i,e,[fe.hatFingers,0,0]).applyMatrix4(i.matrix("head").clone().invert()).sub(s).sub(i.rig.heads.get("head"));return new v(0,0,fe.hatOn).lerp(o,t)}function OS(i,e,t){const{u:n}=bn(t),s=nt(e),r=H[s],o=ce(n,0,.2)*(1-ce(n,.82,1)),a=ce(n,.26,.36)*(1-ce(n,.66,.76));de(i,0),se(i,{lean:fe.monoclePeer*a,nod:fe.monoclePeer*a,tilt:r*fe.monocleTilt*a}),ve(i,e,o?[s]:[]);const c=1-.35*a;Ii(i,s,o,fe.monocleWrist.map((d,f)=>f===2?d-.25*(1-c):d));const[l,h,u]=fe.monocleWorn;n>.18&&n<.8?i.wearProp("monocle",[r*l,h,u]):o>.4&&i.holdUpright("monocle",s,[0,0,.2]),Ke(i,"startled",.6*a)}function FS(i,e,t){const{u:n,ready:s}=bn(t),r=nt(e),o=Ge(n,.3,.42),a=Ge(n,.5,.78);de(i,0),se(i,{lean:4*o,nod:-6*a}),ve(i,e,s?[r]:[]);const c=fe.toastWrist.map((l,h)=>Bt(l,fe.sipWrist[h],a)+(h===1?-fe.toastClink*o:0));Ii(i,r,s,c),s>.3&&i.holdUpright("champagne_flute",r,[0,0,.1],{x:fe.sipTip*a,y:H[r]*fe.sipTip*a}),i.shutEyes(1-.7*a),o>.5&&Ke(i,"amused",o)}function BS(i,e,t){const{u:n,ready:s}=bn(t),r=nt(e),o=H[r];de(i,0),se(i,{lean:-5*s,tilt:-o*8*s,turn:-o*6*s}),ve(i,e,s?[r]:[]),Ii(i,r,s,fe.shakaWrist,{y:fe.shakaWaggle*Ee(mt(n,.2,.8),fe.shakaWaggles)*s}),s>.5&&i.holdUpright("shaka",r,[0,0,.32]),Ke(i,"amused",s)}function kS(i,e,t){const{u:n}=bn(t),s=nt(e),r=H[s],o=ce(n,0,.15)*(1-ce(n,.15,.3)),a=ce(n,.72,.86)*(1-ce(n,.86,1)),c=n>.22&&n<.82,l=ce(n,.28,.38)*(1-ce(n,.66,.76));de(i,0),se(i,{lean:-fe.shadesLean*l,tilt:r*fe.shadesTilt*l,nod:6*l*Math.max(Ee(mt(n,.38,.66),2),0)});const h=Math.max(o,a);ve(i,e,h?[s]:[]),Ii(i,s,h,fe.shadesWrist),c?i.wearProp("sunglasses",fe.shadesWorn):h>.4&&i.holdUpright("sunglasses",s,[0,-.1,.25])}function zS(i,e,t){const{u:n,ready:s}=bn(t),r=nt(e),o=ce(n,.18,.28)*(1-ce(n,.66,.74)),a=Ge(n,.66,.84);de(i,0),se(i,{nod:8*o*Math.max(Ee(mt(n,.28,.66),3),0)+6*a,tilt:H[r]*5*o}),ve(i,e,s?[r]:[]),Ii(i,r,s,fe.fireWrist,{y:25*a*Ee(n,9)}),o>.02&&(i.holdUpright("flame",r,[0,0,.18]),Object.assign(i.props.get("flame"),{phase:n,size:fe.fireSize*o})),Ke(i,a>.3?"startled":"amused",Math.max(o,a))}function HS(i,e,t){const{u:n,ready:s}=bn(t),r=nt(e),o=Ge(n,.35,.6);de(i,0),se(i,{nod:14*o,lean:3*s}),ve(i,e,s?[r]:[]),Ii(i,r,s,fe.thumbWrist,{y:0}),s>.5&&(i.holdUpright("thumb",r,[0,0,.3]),vo(i)),Ke(i,"amused",o)}function GS(i,e,t){const{u:n}=bn(t),s=nt(e),r=ce(n,0,.14)*(1-ce(n,.24,.36)),o=ce(n,.26,.38)*(1-ce(n,.8,.95)),a=Ge(n,.38,.58)-Ge(n,.58,.8);de(i,0),se(i,{lean:fe.peerLean*o,nod:6*o,turn:fe.peerTurn*a}),ve(i,e,r?[s]:[]);const[c,l,h]=fe.glassesWrist;Ii(i,s,r,[c,l,h+.08*ce(n,.12,.22)]),Ke(i,"reading",o)}function VS(i,e,t){const{u:n,ready:s}=bn(t),r=Ge(n,.25,.8);de(i,0),se(i,{lean:fe.thanksBow*r,nod:10*r}),ve(i,e,s?Object.keys(H):[]),s&&i.putAway(...Mt);for(const[o,a]of Object.entries(H))rn(i,o,s,fe.prayerWrist,{x:fe.prayerRoll*s,y:-a*90*s,z:0});i.shutEyes(1-.85*r)}function WS(i,e,t){const{u:n,ready:s}=bn(t),r=nt(e),o=Ge(n,fe.popAt,fe.popAt+.2);i.lift("root",{z:fe.popHop*o}),de(i,0),se(i,{lean:-4*o,nod:-8*o}),ve(i,e,s?[r]:[]),Ii(i,r,s,fe.popperWrist),s>.4&&(i.holdUpright("party_popper",r,[0,0,.1],{y:H[r]*25}),i.props.get("party_popper").burst=mt(n,fe.popAt,.95),vo(i)),Ke(i,"amused",o)}function XS(i,e,t){const{u:n,ready:s}=bn(t),r=nt(e),o=Math.max(Ee(mt(n,.25,.75),2),0);de(i,0),se(i,{lean:-5*s,twist:-H[r]*10*s,tilt:H[r]*4*s,nod:-4*s}),ve(i,e,s?[r]:[]),s&&sn(i,r,s,{...fe.flex,bend:fe.flex.bend+fe.flexPump*o}),Ke(i,"angry",.6*o)}function qS(i,e,t){const{u:n,ready:s}=bn(t),r=nt(e),o=Math.max(Ee(mt(n,.25,.75),2),0);i.lift("root",{z:fe.trophyHop*o}),de(i,0),se(i,{nod:-12*s,lean:-4*s}),ve(i,e,s?[r]:[]),s&&sn(i,r,s,fe.trophy),s>.4&&(i.holdUpright("trophy",r,[0,0,.3]),vo(i)),Ke(i,"amused",s)}function jS(i,e,t){const{u:n,ready:s}=bn(t),r=Rr(e)[0]||nt(e),o=Math.max(Ee(mt(n,.25,.75),2),0);de(i,0),se(i,{lean:-4*s,nod:-10*s}),ve(i,e,s?[r]:[]),s&&sn(i,r,s,{...fe.sword,y:fe.sword.y-fe.swordThrust*o}),s&&i.putAway("squire_quill"),s>.4&&(i.holdUpright("sword",r,[0,0,.15],{x:-15}),vo(i)),Ke(i,"angry",s)}function $S(i,e,t){const{u:n,ready:s}=bn(t),r=[...e.shield][0];if(!r)return $a(i,e,t);const o=Ge(n,fe.shieldBump,fe.shieldBump+.12);Li(i,fe.shieldCrouch*s),de(i,0),se(i,{lean:8*s-8*o,nod:6*s}),ve(i,e,s?[r]:[]);const[a,c,l]=fe.shieldWrist;rn(i,r,s,[a,c+.08*o,l]),i.keep.add("squire_shield"),Ke(i,o>.3?"startled":"angry",s)}function YS(i,e,t){const{u:n,ready:s}=bn(t),r=Rr(e)[0]||nt(e),o=Ge(n,.35,.75);de(i,0),se(i,{nod:12*o,lean:4*o}),ve(i,e,s?[r]:[]),rn(i,r,s,fe.castleWrist,{x:-30*s}),s&&i.putAway("squire_quill"),s>.4&&(i.holdUpright("castle",r,[0,0,.12]),vo(i)),Ke(i,"amused",o)}const yr={high:[1,-.25,2.92],sign:[.5,-.25,3],signWaggle:.1,drawer:[1.16,-.4,1.66],drop:.12,binoculars:[.24,-.8,2.36],sweep:30,nozzle:[1.1,-.55,1.88],torchSweep:.16,corner:[1,-.42,1.36],lift:.3,crouch:.6,peekLean:34},KS=(i,e,t)=>i.map((n,s)=>Bt(n,e[s],t)),yo=i=>i.putAway(...[...Mt].filter(e=>!qa.has(e)));function Ja(i,e,t,n,s={}){const r=nt(e);ve(i,e,t?[r]:[]),rn(i,r,t,n,s),t&&yo(i)}const Kn={bend:.9,lean:30,nod:18,talkNod:7,ear:[1.24,.05,3.3],handsetLean:16,tilt:8,wrist:[0,-.12,.3],palm:.16};function ps(i,e=0){return i.clone().applyAxisAngle(new v(1,0,0),Qe(Pt.tip)).add(new v(Pt.at[0],Pt.at[1],e))}const lp=i=>new v(i.x,-i.z,i.y);function hp(){const{base:i}=Pt,[e,t]=[[i.depth/2,0],i.brow],n=new te(t[1],e[0]-t[0]).normalize(),s=new v(0,(e[1]+t[1])/2,(e[0]+t[0])/2).add(new v(0,n.y,n.x).multiplyScalar(Ih()));return new Ae().compose(s,new Gn().setFromEuler(new wn(Math.atan2(n.x,n.y),0,0)),new v(1,1,1))}const Ih=()=>Pt.base.round*.8,up=i=>Pt.base.height+Ih()+Pt.base.dome*Math.max(1-(i/(Pt.base.width/2))**2,0),ra=()=>lp(new v(0,up(Pt.cradle.apart)+Pt.cradle.height+Pt.handset.rest,Pt.cradle.at));function ZS(i){const{dial:e}=Pt,t=Qe(e.first-i);return lp(new v(Math.cos(t)*e.ring,e.face*1.5,-Math.sin(t)*e.ring).applyMatrix4(hp()))}function JS(i){const e=H[i],t=new v(0,Math.sin(Qe(Kn.handsetLean)),Math.cos(Qe(Kn.handsetLean))),n=new v(e,0,0),s=new Ae().makeBasis(t,n.clone().cross(t),n),r=new wn().setFromRotationMatrix(s,"ZYX");return{along:t,turn:{x:Ft.radToDeg(r.x),y:Ft.radToDeg(r.y),z:Ft.radToDeg(r.z)}}}function QS(i){const e=ie.phone_call,t=mt(i,...e.drop),n=mt(i,...e.settle),s=n>0&&n<1?Math.sin(Math.PI*e.wobbles*n)*(1-n)**2:0,r=mt(i,...e.goes),o=mt(i,...e.poof);return{here:r<.5,above:e.above*(1-t*t),squash:e.squash*s,puff:i>=e.goes[0]?r:o<1?.3+.7*o:null}}function eE(i,e,t){const n=ie.phone_call,s=Vt(t,n.frames),r=nt(e),o=r==="l"?"r":"l",a=Math.max(me(s,n.reach)*(1-me(s,n.lift)),me(s,n.finger)*(1-me(s,n.back)),me(s,[n.hang[0],(n.hang[0]+n.hang[1])/2])*(1-me(s,[n.hang[1],n.goes[0]]))),c=me(s,n.lift)*(1-me(s,[n.hang[0],n.hang[0]+(n.hang[1]-n.hang[0])*.7])),l=mt(s,...n.talk),h=Kn.bend*a;Li(i,h),de(i,0),se(i,{lean:Kn.lean*a,nod:Kn.nod*a+Kn.talkNod*Math.sin(Math.PI*n.nods*l)**2,tilt:H[r]*Kn.tilt*c}),i.putAway(...Mt),ve(i,e,[r,o]);const{handset:u}=Pt,d=JS(r),[f,m,_]=Kn.ear,p=new v(H[r]*f,m,_).applyMatrix4(i.matrix("head")).clone().addScaledVector(d.along,-u.length/2),y=ps(ra()),M=s>=n.reach[1]&&s<n.hang[1]?1:me(s,n.reach)*(1-me(s,[n.hang[1],n.goes[0]])),x=new v(0,0,-1).lerp(new v(-H[r],0,0),c).normalize(),E=y.clone().lerp(p,c).addScaledVector(x,-Kn.palm);lt(i,r,M,i.withinReach(r,E,.97),new v(1,.4,-.6));const T=s>=n.reach[1]&&s<n.hang[1],P=new v(1,0,0).lerp(d.along,c).normalize();if(T){const V=i.rig.along.get(`hand_${r}`).clone().transformDirection(i.matrix(`hand_${r}`));i.aim(`hand_${r}`,V.lerp(d.along,c).normalize())}const C=T&&i.grip(r,[0,0,0]).applyMatrix4(i.matrix(`hand_${r}`)).addScaledVector(x,Kn.palm),b=T?C.clone().addScaledVector(P,-u.length/2):ps(ra().add(new v(-u.length/2,0,-u.drop-u.end[1])));T?(i.holdUpright("telephone_handset",r,[0,0,0],{x:d.turn.x*c+Pt.tip*(1-c),y:d.turn.y*c,z:d.turn.z*c}),i.props.get("telephone_handset").at=C.clone().applyMatrix4(i.matrix(`hand_${r}`).clone().invert())):i.standProp("telephone_handset",ps(ra(),h),{x:Pt.tip});const w=n.turn*me(s,n.dial)*(1-me(s,n.back)),L=me(s,n.finger)*(1-me(s,n.back)),F=ps(ZS(n.turn*me(s,n.dial))).add(new v(...Kn.wrist));lt(i,o,L,i.withinReach(o,F,.97),new v(-1,.2,-.6)),Ke(i,"amused",l>0&&l<1?1:0);const O=QS(s),k=O.puff??0;if(k>0&&k<1&&(i.standProp("telephone_poof",ps(new v(0,0,Pt.base.height/2+(s<n.goes[0]?n.above:0)),h)),Object.assign(i.props.get("telephone_poof"),{puff:k})),!O.here){i.props.delete("telephone_handset");return}const K=new v(0,0,O.above);i.standProp("telephone",ps(new v,h).add(K),{x:Pt.tip}),Object.assign(i.props.get("telephone"),{squash:O.squash,dial:w}),T||i.props.get("telephone_handset").at.add(K).add(new v(0,0,-O.squash*ra().z)),i.standProp("telephone_cord",[0,0,h]);const X=new v(0,0,-h),j=T?b:b.add(K);Object.assign(i.props.get("telephone_cord"),{from:ps(new v(-H[r]*Pt.base.width*.4,.25,Pt.base.height*.3)).add(K).sub(X),to:j.sub(X)})}function tE(i,e,t){const n=ie.ask_sign,s=Vt(t,n.frames),r=me(s,n.raise)*(1-me(s,n.lower)),o=Ee(mt(s,...n.waggle),n.waggles)*Ge(s,...n.waggle),[a,c,l]=yr.sign;de(i,0),se(i,{nod:-10*r,tilt:4*o}),Ja(i,e,r,[a+yr.signWaggle*o,c,l]),Ke(i,"worried",r)}const ei={at:[0,-.74,2.02],across:.4,closed:.08,apart:.6,elbow:[1,.4,-.6],nod:16,lineNod:4,scan:12,sweep:.6};function nE(i,e,t){const n=ie.scroll,s=Vt(t,n.frames),r=me(s,n.raise)*(1-me(s,n.lower)),o=me(s,n.unrolls)*(1-me(s,n.rolls)),a=mt(s,n.unrolls[1],n.rolls[0]);de(i,0),se(i,{lean:3*r}),i.putAway(...Mt),ve(i,e,r?Object.keys(H):[]);const c=nt(e),[l,h,u]=ei.at;for(const[_,g]of Object.entries(H)){const p=u+(_===c?1:-1)*Bt(ei.closed,ei.apart,o)/2,y=new v(l+g*ei.across,h,p);r&&lt(i,_,r,i.withinReach(_,i.carried(y),.97),new v(...ei.elbow))}const d=Math.min(Math.floor(a*n.lines),n.lines-1),f=a*n.lines-d,m=ei.scan*(1-2*me(f,[0,ei.sweep])+2*me(f,[ei.sweep,1]));i.face("head",{x:(ei.nod+ei.lineNod*d)*o,z:m*o}),Ke(i,"reading",o),r&&iE(i,c,r===1?c==="l"?"r":"l":null,o)}function iE(i,e,t,n){const s=l=>i.grip(l,[0,0,0]).applyMatrix4(i.matrix(`hand_${l}`)),r=s(e),o=t?s(t):r.clone().add(new v(0,0,-wp.rolled)),a=r.clone().add(o).multiplyScalar(.5);t&&(r.x=o.x=a.x);const c=i.matrix("root").clone().invert();i.standProp("report_scroll",a.clone().applyMatrix4(c).toArray()),Object.assign(i.props.get("report_scroll"),{top:r.sub(a),bottom:o.sub(a),open:n})}function sE(i,e,t){const n=ie.file_card,s=Vt(t,n.frames),r=me(s,n.reach)*(1-me(s,n.back)),[o,a,c]=yr.drawer;de(i,0),se(i,{lean:10*r,nod:14*r}),Ja(i,e,r,[o,a,c-yr.drop*me(s,n.filed)])}const Zc={sink:2.1,hop:.75,leap:1};function rE(i,e,t){const n=ie.pack_box,{into:s,out:r}=Ql(n,t),o=Ge(s,...n.hop),a=me(s,n.into)*(1-me(r,[n.pops,n.pops+.2])),c=Ge(r,...n.leap);i.lift("root",{z:Zc.hop*o-Zc.sink*a+Zc.leap*c}),de(i,0),se(i,{lean:6*o,nod:12*a-10*c}),Wn(i,e,0,60*o+120*c),ns(i,.7*o+.6*c),i.putAway(...Mt),Ke(i,"amused",c)}function oE(i,e,t){const n=ie.press,{into:s,out:r}=Ql(n,t),o=me(s,[.2,.55])*(1-me(r,[.2,.5]));de(i,0),se(i,{nod:-8*o}),Wn(i,e,0,140*o),i.putAway(...Mt),i.shutEyes(1-.8*me(s,n.squashes)*(1-me(r,n.frees)))}function aE(i,e,t){const{held:n,into:s,out:r}=Ql(ie.vacuum,t),[o,a,c]=yr.nozzle;de(i,0),se(i,{lean:8,nod:14,turn:-H[nt(e)]*14}),Ja(i,e,s*(1-r),[o,a,c-.12*Ee(n??0,2)],{x:-10})}const Gi={intro:18,hold:12,outro:6,fps:12,taps:6,tap:18,point:[1.25,-.45,1.75],bounce:.14,wiggle:7,sparkle:.25};function cE(i,e,t){const{intro:n,hold:s,outro:r,taps:o,tap:a,point:c,bounce:l,wiggle:h,sparkle:u}=Gi,d=t*(n+s+r),f=d<n?Math.sin(Math.PI*d/n):0,m=d<n?ce(d/n,.7,1):1-ce((d-n-s)/r,0,1),_=d>=n&&d<n+s?(d-n)/s:null,g=_===null?0:Math.abs(Math.sin(2*Math.PI*_)),p=Ee(d/n,o);i.lift("root",{z:l*g}),de(i,0),se(i,{lean:6*m,nod:14*m+4*g,twist:h*(_===null?f*p:Ee(_,2))}),i.posture==="stand"&&(i.turn("foot_l",{x:a*f*Math.max(p,0)}),i.turn("foot_r",{x:a*f*Math.max(-p,0)})),ve(i,e,m?[...e.free]:[]);for(const M of e.free)rn(i,M,m,[c[0],c[1],c[2]+.1*g*H[M]],{x:40});m&&yo(i);const y=Math.min(d/4,1)*(1-mt(d,n+s,n+s+r));i.starEyes(y*(1+u*Math.abs(Ee(d/6))))}function lE(i,e,t){const n=ie.fume,s=Vt(t,n.frames),r=Ge(s,n.crushed[0],n.crushed[1]+.06),o=me(s,[n.mad[0],n.mad[0]+.06])*(1-me(s,[n.mad[1],1])),a=Ee(mt(s,...n.mad),n.stamps/2);Li(i,.14*r),i.lift("root",{z:.12*o*Math.abs(a)}),de(i,0),se(i,{lean:16*r+6*o,nod:28*r+10*o,tilt:5*o*Ee(s,14)}),ve(i,e,o?[...e.free]:[]);for(const c of e.free)sn(i,c,o,{y:40,z:-25,bend:95});if(i.posture==="stand")for(const[c,l]of[["l",1],["r",-1]]){const h=o*Math.max(l*a,0);i.turn(`thigh_${c}`,{x:-34*h,y:l*18*h}),i.turn(`shin_${c}`,{x:52*h})}r>o?Ke(i,"worried",r):Ke(i,"angry",o)}const ii={frames:36,fps:12,head:18,body:5,up:10},Jc=(i,e)=>(t,n,s)=>{const r=Vt(s,ii.frames),o=ce(r,.08,.25)*(1-ce(r,.75,.92));se(t,{twist:i*ii.body*o,turn:i*ii.head*o,nod:-e*ii.up*o}),ve(t,n)},Zl={frames:6,fps:20},In={frames:48,fps:12,trip:[0,.14],down:[.05,.11],bounce:[.11,.18],shake:[.3,.58],shakes:3,up:[.62,.8],hop:[.8,.96],drop:.74};function hE(i,e,t){const n=Vt(t,In.frames),s=ce(n,...In.down)*(1-ce(n,...In.up)),r=Ge(n,...In.trip),o=Ee(mt(n,...In.shake),In.shakes)*Ge(n,...In.shake),a=Ge(n,...In.hop);if(i.lift("root",{z:-In.drop*s+.1*Ge(n,...In.bounce)+.16*a}),i.posture==="stand")for(const c of Object.keys(H))i.turn(`shin_${c}`,{x:90*s});se(i,{lean:12*s+10*r*(1-s),nod:12*s,turn:26*o}),Wn(i,e,0,100*r*(1-s)+60*a,8*r),i.putAway(...Mt),a>.1?Ke(i,"amused",a):Ke(i,s>.5?"worried":"startled",Math.max(s,r))}const oa={hands:[.8,.18],lean:-7,nod:-3,toes:14};function uE(i,e,t){de(i,t),se(i,{lean:oa.lean,nod:oa.nod+2*Ee(t)});const[n,s]=oa.hands;ve(i,e,[...e.free]);for(const r of e.free)lt(i,r,1,i.withinReach(r,new v(H[r]*n,s,Vi.floor),.97),new v(1,.6,.2)),i.face(`hand_${r}`,{x:-80});e.free.size&&yo(i),i.swing(.6*Ee(t)),i.tap=oa.toes*Math.max(Ee(t,2),0)}const Wr={pocket:[.35,-.5,1.45],held:[.15,-.95,1.95],look:18,out:[.1,.3],back:[.72,.92]};function dE(i,e,t){const n=nt(e),s=me(t,Wr.out)*(1-me(t,Wr.back)),r=o=>new v(H[n]*o[0],o[1],o[2]);de(i,t),se(i,{lean:4*s,nod:Wr.look*s}),ve(i,e,[n]),lt(i,n,Math.max(s,.001),i.withinReach(n,r(Wr.pocket).lerp(r(Wr.held),s),.97),new v(H[n]*.6,-.5,-.6)),s>.15&&i.holdUpright("pocket_watch",n,[0,0,0],{x:-30}),i.swing(.4*Ee(t))}const Nd={nod:24,lean:8};function fE(i,e,t){const n=.7+.3*Math.sin(2*Math.PI*t);de(i,t),se(i,{lean:Nd.lean*n,nod:Nd.nod*n}),ve(i,e),i.shutEyes(0),i.doze(1+Math.floor(t*4)%2),i.swing(.15*Ee(t))}function pE(i,e,t){const n=Ee(t);de(i,0),se(i,{lean:8,nod:-12}),Wn(i,e,0,110+20*n),ns(i,.6+.2*n)}const Ss={at:[.3,-.8,2.45],across:1.5,low:1.1,high:3.4,swats:4,giggle:4};function mE(i){if(!i.at)return null;const e=Math.min(Math.max((i.at.x-.5)*Ht,-1.5),Ss.across),t=Math.min(Math.max(Nn+(.5-i.at.y)*Ht,Ss.low),Ss.high);return new v(e,Ss.at[1],t)}function gE(i,e,t){const n=t*Ss.swats,s=mE(i),r=s?s.x*H.l>0?"l":"r":Math.floor(n)%2?"l":"r",o=Math.sin(Math.PI*(n%1));de(i,t),se(i,{tilt:Ss.giggle*Math.sin(2*Math.PI*n*2),nod:-3}),i.putAway(...Mt),ve(i,e,Object.keys(H));for(const a of Object.keys(H)){const[c,l,h]=Ss.at,u=a===r&&s?i.withinReach(a,s,.95):new v(H[a]*c,l,h);lt(i,a,a===r?o:.25,u,new v(1,-.4,-.3))}i.squeezeEyes(1)}const aa={up:[1.2,-.3,2.85],down:[.95,-.25,1.3],sway:12,bounce:.18};function _E(i,e,t){const{beats:n}=ie.disco,s=t*n,r=Math.floor(s)%2?1:-1,o=Math.sin(Math.PI*Math.min(s%1*3,1)*.5),a=me(t,[0,.06])*(1-me(t,[.94,1]));de(i,t),se(i,{tilt:r*aa.sway*o*a,nod:-4}),i.putAway(...Mt),ve(i,e,Object.keys(H));for(const c of Object.keys(H)){const l=H[c],[h,u,d]=l===r?aa.up:aa.down;lt(i,c,a,new v(l*h,u,d),new v(1,-.3,l===r?.2:-.6))}ts(i,aa.bounce*Math.abs(Math.sin(Math.PI*s))*a),Ke(i,"amused",a)}const Rn={grip:[-.1,-.62,2],down:12,fore:.9,behind:[-.45,.45,1.45],kick:.13,climb:7,shoulder:7,turn:22,cheek:14,steep:60};function dp(i,e=Rn.down,t=1){const n=e-Rn.climb*i,s=new v(t*Math.cos(Qe(n)),0,-Math.sin(Qe(n))),[r,o,a]=Rn.grip;return{grip:new v(t*r,o,a).addScaledVector(s,-Rn.kick*i),along:s,pitch:n}}const xE=i=>{const{shots:e,count:t}=ie.bug_shot;return i<=e[0]||i>=e[1]?0:Math.max(0,1-(i-e[0])/(e[1]-e[0])*t%1*3)};function vE(i,e){if(!i)return{turn:H.l*Rn.turn,down:Rn.down,way:1,point:null};const t=new v((i.x-.5)*Ht,La,Nn+(.5-i.y)*Ht).applyAxisAngle(new v(0,0,1),Qe(-e)),n=Ft.radToDeg(Math.atan2(-(t.z-Rn.grip[2]),Math.hypot(t.x,t.y))),s=t.x>=0||n<-Rn.steep?1:-1,r=Ft.radToDeg(Math.atan2(s*t.y,s*t.x))*s*Math.cos(Qe(n)),o=dp(0,Rn.down,s).grip.applyAxisAngle(new v(0,0,1),Qe(r)),a=t.clone().sub(o);return{turn:r,down:Ft.radToDeg(Math.atan2(-a.z,Math.hypot(a.x,a.y))),way:s,point:t}}function fp(i){const e=Math.max(i.z,0),t=new v(0,-e,1-e).normalize(),n=t.sub(i.clone().multiplyScalar(t.dot(i))).normalize();return new Ae().makeBasis(i.clone(),n.clone().cross(i),n)}function pp(i){const e=new wn().setFromRotationMatrix(fp(i),"ZYX");return{x:Ft.radToDeg(e.x),y:Ft.radToDeg(e.y),z:Ft.radToDeg(e.z)}}function yE(i,e,t,n){if(!e)return n;const s=e.clone().applyAxisAngle(new v(0,0,1),Qe(-t)),r=a=>i.clone().add(mp(a).multiplyScalar(Ms.barrel)),o=s.clone().sub(r(s.clone().sub(i).normalize())).normalize();return s.sub(r(o)).normalize()}const mp=i=>new v().setFromMatrixColumn(fp(i),2),ME=i=>{const e=Math.max(-i,0)/90;return new v(0,0,-Ms.low*e)};function wE(i,e,t,n,s){const r=mp(s).negate(),o=f=>n.clone().addScaledVector(s,f-Pi.grip).addScaledVector(r,Ms.under),a=f=>i.withinReach(e,o(f),.97).distanceTo(o(f))<.02,c=Array.from({length:6},(f,m)=>Ms.fore-m*(Ms.fore-Ms.nearest)/5),l=o(c.find(a)??c.at(-1)),h=H[e]>0?s:s.clone().negate();lt(i,e,t,i.withinReach(e,l,.97),new v(H[e]*.6,-.6,-.6));const{y:u,z:d}=pp(h);t>.5&&i.face(`hand_${e}`,{x:Ms.roll,y:u,z:d})}function bE(i,e,t){const n=ie.bug_shot,s=(n.draw[0]+n.draw[1])/2,r=me(t,[n.draw[0],s])*(1-me(t,[s,n.draw[1]])),o=me(t,[s,n.draw[1]])*(1-me(t,[n.drops[0]+.05,n.drops[0]+.2])),a=xE(t),c=vE(i.target,i.facing),l=dp(a,c.down,c.way),[h,u]=c.way>0?["r","l"]:["l","r"],[d,f,m]=Rn.behind;de(i,t),i.turn("chest",{z:-c.way*Rn.shoulder*a}),se(i,{nod:Rn.cheek*o-4*a,turn:c.way*Rn.cheek*o,tilt:-c.way*Rn.cheek*.4*o}),i.putAway(...Mt),ve(i,e,Object.keys(H)),r>o?lt(i,h,r,new v(c.way*d,f,m),new v(-c.way,.5,-.5)):lt(i,h,o,i.withinReach(h,l.grip.clone().add(ME(c.down)),.97),new v(-c.way,-.2,-.6));const _=i.grip(h,[0,0,0]).applyMatrix4(i.matrix(`hand_${h}`)),g=yE(_,c.point,c.turn*o,l.along);wE(i,u,o,_,g),(o>.05||r>.3)&&(i.holdUpright("rifle",h,[0,0,0],pp(g)),i.props.get("rifle").firing=a>.6),Zf(i,t,me(t,n.draw)*(1-me(t,[n.fly[0],n.fly[1]]))),i.posture==="stand"&&i.revolve(c.turn*o)}const Ia={rest:{grip:[.3,-.5,1.5],way:[.6,-.2,-.77]},top:{grip:[-.25,-.8,2.2],way:[.25,-1.35,1.6]},blow:{grip:[.5,-.6,1.4],way:[1.7,.1,-.98]},apart:.3,turn:30};function SE(i){const{raise:e,swing:t,lower:n}=ie.bug_smash,s=o=>({grip:new v(...Ia[o].grip),way:new v(...Ia[o].way).normalize()}),r=(o,a,c)=>({grip:o.grip.clone().lerp(a.grip,c),way:o.way.clone().lerp(a.way,c).normalize()});return i<t[0]?r(s("rest"),s("top"),me(i,e)):i<n[0]?r(s("top"),s("blow"),me(i,t)**2):r(s("blow"),s("rest"),me(i,n))}function EE(i,e,t){const n=ie.bug_smash,s=Math.abs(i.walkWay)*me(t,[n.walk[0]-.03,n.walk[0]])*(1-me(t,[n.walk[1],n.walk[1]+.04])),r=me(t,[n.raise[0]-.08,n.raise[0]])*(1-me(t,[n.lower[1]-.04,n.lower[1]])),{grip:o,way:a}=SE(t),c=Ge(t,n.blow-.02,n.blow+.06);s&&Rh(i),de(i,t),se(i,{lean:10*c,nod:6*c}),Li(i,.12*c),i.putAway(...Mt),ve(i,e,Object.keys(H)),lt(i,"r",r,i.withinReach("r",o,.97),new v(-.6,-.4,-.6)),lt(i,"l",r,i.withinReach("l",o.clone().addScaledVector(a,Ia.apart),.97),new v(.6,-.4,-.6));const l={y:Ft.radToDeg(-Math.asin(a.z)),z:Ft.radToDeg(Math.atan2(a.y,a.x))};r>.3&&i.holdUpright("big_mallet","r",[0,0,0],l),Zf(i,t,r*(1-me(t,n.gone))),s&&Ch(i,s),i.posture==="stand"&&i.revolve(H.l*Ia.turn*r+i.walkWay*90*s)}const no={above:2.42,radius:.42,ring:.07,tip:28,hands:[.1,-.62,2.05]};function TE(i,e,t){const n=ie.halo,s=me(t,n.grows)*(1-me(t,n.fades));de(i,t),i.lift("root",{z:n.float*s*(1+Math.sin(2*Math.PI*t))}),se(i,{nod:-8*s,tilt:4*s}),i.putAway(...Mt),Ya(i,{...e,free:new Set(Object.keys(H))},s,no.hands),i.wearProp("halo",[0,0,no.above]),i.props.get("halo").size=Math.max(s,.01),Ke(i,"serene",s)}const ms={pocket:[-.55,-.1,1.4],low:[-.3,-.7,1.9],high:[-1.1,-.45,2.75],chest:[.15,-.72,1.95],tremble:.025,look:16};function AE(i,e,t){const n=ie.repent,s=me(t,n.kneel)*(1-me(t,n.rise)),r=me(t,n.out)*(1-me(t,n.down)),o=me(t,n.up)*(1-me(t,n.down)),a=ms.tremble*Math.sin(2*Math.PI*9*t)*Ge(t,n.hold[0],n.hold[1]);if(de(i,t),i.lift("root",{z:-In.drop*s}),i.posture==="stand")for(const h of Object.keys(H))i.turn(`shin_${h}`,{x:90*s});se(i,{lean:6*s,nod:-ms.look*o+8*(s-o),turn:ms.look*o}),i.putAway(...Mt),ve(i,e,Object.keys(H));const c=new v(...ms.low).lerp(new v(...ms.high),o).add(new v(0,0,a)),l=new v(...ms.pocket).lerp(c,r);lt(i,"r",Math.max(r,.001),i.withinReach("r",l,.97),new v(-.6,-.5,-.6)),lt(i,"l",o,i.withinReach("l",new v(...ms.chest),.97),new v(.6,-.5,-.6)),r>.2&&i.holdUpright("crucifix","r",[0,0,0],{}),Ke(i,"worried",Math.max(s,o))}const RE=[.42,-.55,1.55],CE=[.45,.45,1.45];function PE(i,e,t){const n=ie.pogo,s=me(t,[n.draw[0],n.draw[1]*.5])*(1-me(t,[n.draw[1]*.5,n.draw[1]])),r=me(t,[n.draw[1]*.6,n.draw[1]])*(1-me(t,n.release)),o=Ap(Rp(),(t-n.bounces[0])/(n.bounces[1]-n.bounces[0])),a=t>n.bounces[0]&&t<n.bounces[1]?1-Math.sin(Math.PI*o.s):0;de(i,t),se(i,{lean:6*r,nod:-6*r}),i.putAway(...Mt),ve(i,e,Object.keys(H));const[c,l,h]=RE,[u,d,f]=CE;for(const m of Object.keys(H)){const _=H[m];m==="r"&&s>r?lt(i,m,s,new v(_*u,d,f),new v(1,.5,-.5)):lt(i,m,r,new v(_*c,l,h),new v(1,-.2,-.4))}ts(i,.35*a*r),Ke(i,"amused",r)}const va={arm:.29,up:2.6,forward:-.1,above:.35},LE=[ie.rope_swing.ties*Ht/2-va.arm,va.forward,va.up];function IE(i,e,t){const n=Cp(t)/ie.rope_swing.sway;i.lift("root",{z:va.above*Pp(t)}),i.standProp("rope_swing",new v(0,0,Lp.sit.drop*Ht).sub(i.carried(new v)).toArray()),de(i,t),se(i,{lean:-5*n,nod:-4}),i.putAway(...Mt);const[s,r,o]=LE;ve(i,e,Object.keys(H));for(const a of Object.keys(H))lt(i,a,1,i.carried(new v(H[a]*s,r,o)),new v(1,0,-.4)),i.face(`hand_${a}`,{z:-H[a]*90});i.swing(1.2*n),Ke(i,"amused")}const DE=[1.25,0,2.95];function NE(i,e,t){const n=Ee(t);de(i,t),se(i,{nod:-6,tilt:3*n}),i.putAway(...Mt);const[s,r,o]=DE;ve(i,e,Object.keys(H));for(const a of Object.keys(H))lt(i,a,1,i.withinReach(a,i.carried(new v(H[a]*s,r,o)),.97),new v(1,0,-.4)),i.face(`hand_${a}`,{z:-H[a]*90});ns(i,.05,6*n),Ke(i,"amused")}const ca={ahead:.45,below:.06,hands:.22,turn:35};function UE(i,e,t){const n=ie.binoculars,s=.4*yr.sweep*Ee(t,n.sweep),r=n.up+n.scan*Ee(t,2);se(i,{twist:s,nod:-r}),ve(i,e,["l","r"]);const o=i.rig.eyes.reduce((l,h)=>l.add(h),new v).divideScalar(i.rig.eyes.length).applyMatrix4(i.matrix("head")),a=new v(0,-Math.cos(Qe(r)),Math.sin(Qe(r))),c=o.clone().addScaledVector(a,ca.ahead).add(new v(0,0,-ca.below));i.standProp("binoculars",c.toArray(),{x:-r,z:s});for(const l of["l","r"]){const h=i.carried(c.clone().add(new v(H[l]*ca.hands,.1,-.16)));lt(i,l,1,i.withinReach(l,h,.97),new v(...z.elbow))}yo(i),i.posture==="stand"&&i.revolve(H[nt(e)]*ca.turn)}const ti={crouch:.3,lean:48,nod:12,hands:[.3,-1.45,1.75],dig:.3,elbow:[1,-.4,-.6],turn:90,wiggle:6};function OE(i,e,t){const n=ie.rummage,s=Xf(e,i.leanWay),r=me(t,n.leans)*(1-me(t,n.pops)),o=Ee(t,n.digs);Li(i,ti.crouch*r),de(i,0),se(i,{nod:ti.nod*r,tilt:ti.wiggle*o*r}),i.bendAbove("spine",{x:(ti.lean+ti.wiggle*o)*r}),ve(i,e,r?["l","r"]:[]);const[a,c,l]=ti.hands;for(const[h,u]of r?[["l",1],["r",-1]]:[]){const d=i.carried(new v(H[h]*a,c,l+u*ti.dig*o));lt(i,h,r,i.withinReach(h,d,.97),new v(...ti.elbow))}Ip.forEach((h,u)=>{const d=Dp(u,t,i.throws??void 0);d&&i.standProp(h,[d.at[0],d.at[1],d.at[2]+ti.crouch*r],{x:d.turn,z:d.turn/3},1-d.landed)}),i.posture==="stand"&&i.revolve(H[s]*ti.turn*r)}function FE(i,e,t){const n=nt(e),s=H[n],[r,o,a]=_a;de(i,t),se(i,{lean:2,nod:dn.nod/2+2*Ee(t),tilt:-s*dn.tilt*.7}),Ya(i,e,1,[r,o,a+.03*Math.max(Ee(t,2),0)]),jf(i,n,1),i.holdLaptop(),i.glanceEyes(dn.glance[0],-s*dn.glance[1])}function BE(i,e,t){const{u:n,ready:s}=Vn(t,z.greetingFrames),r=Ge(n,.3,.75);de(i,0),se(i,{lean:-4*s,nod:-10*s}),Ja(i,e,s,KS([.7,-.62,2.34],[.3,-.84,2.38],r),{x:-40}),i.shutEyes(1-.6*r)}function kE(i,e,t){const{back:n}=i.sky??{back:0};i.lift("root",{y:Xi.step*n,z:Xi.hop*Math.sin(Math.PI*n)}),de(i,t),se(i,{lean:-Xi.lean*n});const s=nt(e);ve(i,e,[s]),qf(i,s,t),yo(i),Ke(i,"amused")}const Ud={sit:{under:$c,over:Zw},lounge:{under:$c,over:Yw},composed:{under:$c,over:Kw},walk:{under:Rh,over:Ch}},$e=["stand","sit","lounge","composed","walk"],xt=["stand"],Od=["hang"],Ys=["sit","lounge"],zE=["stand","sit","walk"],Fd=5,uT=[{name:"idle",head:ne.free,frames:24,fps:8,loops:!0,leaves:8,postures:$e,pose:$a},{name:"nod",head:ne.gestures,frames:10,fps:12,loops:!1,postures:$e,pose:Dw},{name:"hand_rub",head:ne.gestures,frames:ie.hand_rub.frames,fps:ie.hand_rub.fps,loops:!1,postures:xt,pose:Nw},{name:"ponder",head:ne.holds,frames:ie.ponder.frames,fps:ie.ponder.fps,loops:!1,postures:$e,pose:qc(ie.ponder)},{name:"think_cloud",head:ne.holds,frames:ie.think_cloud.frames,fps:ie.think_cloud.fps,loops:!1,postures:$e,pose:qc(ie.think_cloud)},{name:"got_it",head:ne.holds,frames:ie.got_it.frames,fps:ie.got_it.fps,loops:!1,postures:$e,pose:qc(ie.got_it)},{name:"shake",head:ne.gestures,frames:12,fps:12,loops:!1,postures:$e,pose:Uw},{name:"wave",head:ne.gestures,frames:12,fps:12,loops:!0,postures:$e,pose:Ow},{name:"celebrate",head:ne.gestures,frames:12,fps:10,loops:!0,postures:xt,pose:zw},{name:"sleep",head:ne.holds,frames:z.yawnFrames+to,intro:z.yawnFrames,leaves:to,fps:6,loops:!0,postures:$e,marks:{mark:"Z",frames:[[z.yawnFrames,z.yawnFrames+to]]},pose:Hw},{name:"walk",head:ne.free,frames:12,fps:12,loops:!0,interruptible:!0,postures:xt,pose:Gw},{name:"walk_in",head:ne.free,frames:40,fps:12,loops:!1,postures:xt,pose:sb},{name:"run_in",head:ne.free,frames:28,fps:12,loops:!1,postures:xt,pose:rb},{name:"pull_ups",head:ne.holds,frames:24,fps:10,loops:!0,postures:xt,pose:ab},{name:"ladder_climb",head:ne.holds,frames:16,fps:8,loops:!0,interruptible:!0,postures:xt,pose:ob},{name:"hang_l",head:ne.holds,frames:24,fps:8,loops:!0,leaves:8,postures:Od,pose:Ed("l")},{name:"hang_r",head:ne.holds,frames:24,fps:8,loops:!0,leaves:8,postures:Od,pose:Ed("r")},{name:"enter",head:ne.gestures,frames:36,fps:12,loops:!1,postures:xt,pose:Fb},{name:"exit",head:ne.gestures,frames:28,fps:12,loops:!1,postures:xt,pose:Bb},{name:"search",head:ne.holds,frames:80,fps:10,loops:!0,postures:["stand"],pose:Gb},{name:"glass_bubble",head:ne.free,frames:48,fps:10,loops:!0,postures:["stand"],pose:Xb},{name:"lean",head:ne.free,frames:48,fps:8,loops:!0,leaves:24,postures:["stand"],pose:Wb},{name:"read",head:ne.holds,frames:Yl,fps:vt.fps,loops:!0,intro:vt.intro,outro:vt.outro,leaves:vt.pageEvery,postures:$e,pose:$b},{name:"write",head:ne.holds,frames:Ca,intro:z.intro,outro:z.outro,leaves:z.hold,fps:z.fps,loops:!0,postures:$e,pose:nS},{name:"waiting",head:ne.free,frames:Kl,intro:hn.intro,outro:hn.outro,leaves:hn.hold,fps:z.fps,loops:!0,postures:["stand","sit"],pose:Yb},{name:"compacting",head:ne.gestures,frames:Ca,intro:z.intro,outro:z.outro,leaves:z.hold,fps:z.compactFps,loops:!0,postures:$e,pose:iS},{name:"yawn",head:ne.gestures,frames:z.yawnFrames,fps:z.fps,loops:!1,postures:$e,pose:op},{name:"rest",head:ne.free,frames:Dt.frames,fps:Dt.fps,loops:!1,postures:xt,marks:{mark:"♪",frames:Dt.tunes.map(i=>i.map(e=>e*Dt.frames))},pose:Jb},{name:"whistle",head:ne.gestures,frames:z.pastimeFrames,fps:z.fps,loops:!1,postures:$e,voices:["coach"],pose:Kb},{name:"phone_call",head:ne.gestures,frames:ie.phone_call.frames,fps:ie.phone_call.fps,loops:!1,postures:xt,pose:eE},{name:"sip",head:ne.gestures,frames:z.pastimeFrames,fps:z.fps,loops:!1,postures:$e,voices:["colleague"],pose:Qb},{name:"groove",head:ne.gestures,frames:z.pastimeFrames,fps:z.fps,loops:!1,postures:$e,voices:["homie"],pose:eS},{name:"shield_polish",head:ne.gestures,frames:z.pastimeFrames,fps:z.fps,loops:!1,postures:$e,voices:["squire"],pose:tS},{name:"bow",head:ne.gestures,frames:z.greetingFrames,fps:z.fps,loops:!1,postures:$e,voices:["butler"],pose:sS},{name:"salute",head:ne.gestures,frames:z.greetingFrames,fps:z.fps,loops:!1,postures:$e,voices:["squire"],pose:rS},{name:"startled",head:ne.gestures,frames:z.hopFrames,fps:z.fps,loops:!1,postures:$e,pose:oS},{name:"stumble",head:ne.gestures,frames:z.stumbleFrames,fps:z.fps,loops:!1,postures:["walk"],pose:aS},{name:"glance",head:ne.holds,frames:z.greetingFrames,fps:z.fps,loops:!1,postures:$e,pose:cS},{name:"work",head:ne.free,frames:un.blows*un.blowFrames,fps:un.fps,loops:!0,postures:["stand","sit"],pose:hS},{name:"inspect",head:ne.holds,frames:$t.frames,fps:$t.fps,loops:!0,postures:["stand"],pose:fS},{name:"point",head:ne.gestures,frames:12,fps:8,loops:!0,postures:$e,pose:vS},{name:"watch",head:ne.free,frames:8,fps:8,loops:!0,cuts:!0,postures:["stand","sit"],pose:gS},{name:"push",head:ne.holds,frames:vn.intro+vn.stride,intro:vn.intro,fps:vn.fps,loops:!0,legs:!0,postures:["walk","stand"],pose:xS},{name:"jump",head:ne.gestures,frames:16,fps:20,loops:!1,postures:xt,pose:yS},{name:"tickle_swat",head:ne.free,frames:24,fps:16,loops:!1,cuts:!0,postures:$e,pose:gE},{name:"disco",head:ne.holds,frames:ie.disco.frames,fps:ie.disco.fps,loops:!1,postures:xt,pose:_E},{name:"bug_shot",head:ne.holds,frames:ie.bug_shot.frames,fps:ie.bug_shot.fps,loops:!1,postures:xt,pose:bE},{name:"bug_smash",head:ne.holds,frames:ie.bug_smash.frames,fps:ie.bug_smash.fps,loops:!1,postures:xt,pose:EE},{name:"halo",head:ne.gestures,frames:ie.halo.frames,fps:ie.halo.fps,loops:!1,postures:xt,pose:TE},{name:"repent",head:ne.gestures,frames:ie.repent.frames,fps:ie.repent.fps,loops:!1,postures:xt,pose:AE},{name:"pogo",head:ne.holds,frames:ie.pogo.frames,fps:ie.pogo.fps,loops:!1,postures:xt,pose:PE},{name:"fall",head:ne.gestures,frames:12,fps:12,loops:!1,interruptible:!0,postures:xt,pose:SS},{name:"backflip",head:ne.holds,frames:22,fps:20,loops:!1,postures:xt,pose:bS},{name:"land",head:ne.gestures,frames:Zl.frames,fps:Zl.fps,loops:!1,postures:xt,pose:ES},{name:"type",head:ne.holds,frames:24,fps:8,loops:!0,leaves:8,least:Fd,aside:!0,postures:Ys,pose:Qw},{name:"joy",head:ne.gestures,frames:ie.joy.frames,fps:ie.joy.fps,loops:!1,postures:$e,pose:eb},{name:"dismay",head:ne.gestures,frames:28,fps:10,loops:!1,postures:$e,pose:tb},{name:"stretch",head:ne.gestures,frames:24,fps:8,loops:!1,postures:$e,pose:nb},{name:"squire_chase",head:ne.gestures,frames:24,fps:12,loops:!1,postures:xt,pose:TS},{name:"pointed",head:ne.gestures,frames:20,fps:10,loops:!1,postures:xt,pose:IS},{name:"hat_tip",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,holds:!0,postures:$e,voices:["butler"],pose:NS},{name:"monocle",head:ne.holds,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["butler"],pose:OS},{name:"toast",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["butler"],pose:FS},{name:"shaka",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["homie"],pose:BS},{name:"shades",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["homie"],pose:kS},{name:"fire",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["homie"],pose:zS},{name:"thumbs_up",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["colleague"],pose:HS},{name:"peer",head:ne.holds,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["colleague"],pose:GS},{name:"thanks",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,pose:VS},{name:"party_popper",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["coach"],pose:WS},{name:"flex",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["coach"],pose:XS},{name:"trophy",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["coach"],pose:qS},{name:"sword",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["squire"],pose:jS},{name:"shield_up",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["squire"],pose:$S},{name:"castle",head:ne.gestures,frames:fe.frames,fps:fe.fps,loops:!1,postures:$e,voices:["squire"],pose:YS},{name:"ask_sign",head:ne.gestures,frames:ie.ask_sign.frames,fps:ie.ask_sign.fps,loops:!1,postures:$e,pose:tE},{name:"scroll",head:ne.holds,frames:ie.scroll.frames,fps:ie.scroll.fps,loops:!1,postures:$e,pose:nE},{name:"file_card",head:ne.gestures,frames:ie.file_card.frames,fps:ie.file_card.fps,loops:!1,postures:xt,pose:sE},{name:"pack_box",head:ne.gestures,frames:ie.pack_box.intro+ie.pack_box.hold+ie.pack_box.outro,intro:ie.pack_box.intro,outro:ie.pack_box.outro,leaves:ie.pack_box.hold,fps:ie.pack_box.fps,loops:!0,postures:xt,pose:rE},{name:"press",head:ne.gestures,frames:ie.press.intro+ie.press.hold+ie.press.outro,intro:ie.press.intro,outro:ie.press.outro,leaves:ie.press.hold,fps:ie.press.fps,loops:!0,postures:$e,pose:oE},{name:"vacuum",head:ne.gestures,frames:ie.vacuum.intro+ie.vacuum.hold+ie.vacuum.outro,intro:ie.vacuum.intro,outro:ie.vacuum.outro,leaves:ie.vacuum.hold,fps:ie.vacuum.fps,loops:!0,postures:xt,pose:aE},{name:"eager",head:ne.free,frames:Gi.intro+Gi.hold+Gi.outro,intro:Gi.intro,outro:Gi.outro,leaves:Gi.hold,fps:Gi.fps,loops:!0,holds:!0,postures:xt,pose:cE},{name:"fume",head:ne.gestures,frames:ie.fume.frames,fps:ie.fume.fps,loops:!1,cuts:!0,postures:xt,pose:lE},{name:"look_left",head:ne.holds,frames:ii.frames,fps:ii.fps,loops:!1,postures:$e,pose:Jc(-1,0)},{name:"look_right",head:ne.holds,frames:ii.frames,fps:ii.fps,loops:!1,postures:$e,pose:Jc(1,0)},{name:"look_up",head:ne.holds,frames:ii.frames,fps:ii.fps,loops:!1,postures:$e,pose:Jc(0,1)},{name:"tumble",head:ne.holds,frames:In.frames,fps:In.fps,loops:!1,postures:xt,pose:hE},{name:"ledge_sit",head:ne.free,frames:32,fps:8,loops:!0,leaves:8,postures:Ys,pose:uE},{name:"pocket_watch",head:ne.holds,frames:48,fps:10,loops:!0,postures:Ys,pose:dE},{name:"doze",head:ne.holds,frames:48,fps:8,loops:!0,leaves:24,postures:Ys,pose:fE},{name:"hop_up",head:ne.free,frames:8,fps:16,loops:!0,interruptible:!0,cuts:!0,postures:xt,pose:pE},{name:"rope_swing",head:ne.gestures,frames:ie.rope_swing.intro+ie.rope_swing.hold+ie.rope_swing.outro,intro:ie.rope_swing.intro,outro:ie.rope_swing.outro,leaves:ie.rope_swing.hold,fps:ie.rope_swing.fps,loops:!0,postures:Ys,pose:IE},{name:"chute",head:ne.holds,frames:ie.chute.frames,fps:ie.chute.fps,loops:!0,interruptible:!0,cuts:!0,postures:xt,pose:NE},{name:"binoculars",head:ne.holds,frames:ie.binoculars.frames,fps:ie.binoculars.fps,loops:!0,postures:zE,pose:UE},{name:"rummage",head:ne.holds,frames:ie.rummage.frames,fps:ie.rummage.fps,loops:!0,postures:xt,pose:OE},{name:"type_ponder",head:ne.holds,frames:ie.type_ponder.frames,fps:ie.type_ponder.fps,loops:!0,leaves:8,least:Fd,aside:!0,postures:Ys,pose:FE},{name:"wipe_brow",head:ne.gestures,frames:z.greetingFrames,fps:z.fps,loops:!1,postures:$e,pose:BE},{name:"wave_up",head:ne.gestures,frames:12,fps:12,loops:!0,cuts:!0,postures:["stand","sit"],pose:kE}],gp=`
    #include <common>
    #include <skinning_pars_vertex>
    attribute vec3 hullNormal;
    uniform float push;
    varying vec3 worldNormal;
    varying vec3 worldPosition;
    varying vec3 localPosition;

    void main() {
        localPosition = position;
        #include <beginnormal_vertex>
        #ifdef HULL
            objectNormal = hullNormal;
        #endif
        #include <skinbase_vertex>
        #include <skinnormal_vertex>
        #include <begin_vertex>
        #include <skinning_vertex>
        transformed += normalize(objectNormal) * push;
        worldNormal = normalize(mat3(modelMatrix) * objectNormal);
        worldPosition = (modelMatrix * vec4(transformed, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(transformed, 1.0);
    }
`,HE=`
    uniform vec3 colour;
    uniform vec3 light;
    uniform vec3 shade;
    uniform float litFrom;
    uniform vec3 bulbAt;
    uniform vec3 bulbGlow;
    uniform float bulbFalloff;
    varying vec3 worldNormal;
    varying vec3 worldPosition;

    void main() {
        vec3 normal = normalize(worldNormal);
        if (!gl_FrontFacing) {
            normal = -normal;
        }
        float lit = step(litFrom, dot(normal, light));
        vec3 toBulb = bulbAt - worldPosition;
        float bulb = max(dot(normal, normalize(toBulb)), 0.0) / (1.0 + dot(toBulb, toBulb) * bulbFalloff);
        gl_FragColor = vec4(colour * mix(shade, vec3(1.0), lit) + bulbGlow * bulb * mix(colour, vec3(1.0), 0.35), 1.0);
        #include <colorspace_fragment>
    }
`,GE=["headphones"],nn={gap:.16,dark:.35,glass:[.006,.007,.01],off:.0025,bezel:{width:.035,shade:.75,round:.42},halo:{strength:0,soft:.55,reach:2},glare:{strength:.012,from:.5},shine:{lift:1,core:.55,tightness:6},framesBehind:6},VE=`
    uniform vec3 glow;
    uniform float lit;
    uniform float across;
    uniform float open;
    uniform float flash;
    uniform float core;
    uniform vec2 middle;
    uniform vec2 extent;
    uniform sampler2D pixels;
    uniform vec2 grid;
    uniform float gap;
    uniform float soften;
    uniform float dark;
    uniform vec3 glass;
    uniform float off;
    uniform vec3 bezel;
    uniform vec3 halo;
    uniform vec2 glare;
    uniform vec3 shine;
    varying vec3 localPosition;

    // the colour and how lit a pixel of the grid is, by its column and row
    vec4 pixelAt(vec2 cell) {
        return texture2D(pixels, (clamp(cell, vec2(0.0), grid - 1.0) + 0.5) / grid);
    }

    void main() {
        vec2 from = abs(localPosition.xy - middle) / extent;
        float band = step(from.x, across) * step(from.y, open);
        vec2 place = clamp(vec2(localPosition.x - middle.x + extent.x, middle.y + extent.y - localPosition.y) / (2.0 * extent), 0.0, 0.9999) * grid;
        vec2 cell = fract(place);
        // the dark lines between the pixels, gap of each pixel wide and widened only by the softening, centred on the borders between
        // pixels, their edges blended over one drawn fragment so a screen drawn small shows no jagged steps or shimmer
        vec2 lines = clamp(vec2(gap) + soften * fwidth(place), 0.0, 0.5);
        vec2 border = min(cell, 1.0 - cell);
        vec2 blend = fwidth(place) * 0.5;
        vec2 edges = smoothstep(lines * 0.5 - blend, lines * 0.5 + blend, border);
        float pixel = edges.x * edges.y;
        vec4 shown = pixelAt(floor(place));
        // how far inside the rounded outline this point is, in the figure's units
        vec2 corner = from - (1.0 - bezel.z);
        float outside = length(max(corner, 0.0)) + min(max(corner.x, corner.y), 0.0) - bezel.z;
        vec2 way = corner.x > 0.0 && corner.y > 0.0 ? normalize(corner) : (corner.x > corner.y ? vec2(1.0, 0.0) : vec2(0.0, 1.0));
        float inside = -outside / length(way / extent);
        // the glow the lit pixels about it spill here
        vec3 spill = vec3(0.0);
        for (int dx = -2; dx <= 2; dx++) {
            for (int dy = -2; dy <= 2; dy++) {
                vec2 other = floor(place) + vec2(float(dx), float(dy));
                vec4 near = pixelAt(other);
                float apart = length(place - other - 0.5);
                spill += near.rgb * near.a * exp(-apart * apart / (2.0 * halo.y * halo.y)) * step(apart, halo.z + 0.5);
            }
        }
        float rim = 1.0 - smoothstep(bezel.x * 0.5, bezel.x, inside);
        vec3 screen = glass * (1.0 - bezel.y * rim) + (off + halo.x * spill) * pixel * (1.0 - rim);
        screen += glare.x * smoothstep(glare.y, 1.0, (localPosition.y - middle.y) / extent.y) * (1.0 - rim);
        vec2 offMiddle = cell - 0.5;
        vec3 glowing = shown.rgb * (1.0 + shine.x) + shine.y * exp(-dot(offMiddle, offMiddle) * shine.z) * mix(shown.rgb, vec3(1.0), 0.5);
        vec3 drawn = mix(screen, glowing, shown.a * pixel);
        float centre = max(1.0 - length(from), 0.0);
        vec3 shine = glow * lit * mix(dark, 1.0, pixel);
        vec3 lighted = mix(shine + (vec3(1.0) - glow) * core * centre * centre * pixel, vec3(1.0), flash);
        gl_FragColor = vec4(mix(drawn * (1.0 - step(0.001, lit + flash) * 0.6), lighted, band * max(lit, flash)), 1.0);
        #include <colorspace_fragment>
    }
`;function WE(i){const e=Dh(i);e.fragmentShader=VE;const t=new tn().setFromBufferAttribute(i.geometry.attributes.position),n=t.getCenter(new v),s=t.getSize(new v).multiplyScalar(.5);return Object.assign(e.uniforms,{glow:{value:new v},lit:{value:0},across:{value:0},open:{value:0},flash:{value:0},core:{value:Fp.core},middle:{value:new te(n.x,n.y)},extent:{value:new te(s.x,s.y)},pixels:{value:KE()},grid:{value:new te(ws.columns,ws.rows)},gap:{value:nn.gap},soften:{value:0},dark:{value:nn.dark},glass:{value:new v(...nn.glass)},off:{value:nn.off},bezel:{value:new v(nn.bezel.width,nn.bezel.shade,nn.bezel.round)},halo:{value:new v(nn.halo.strength,nn.halo.soft,nn.halo.reach)},glare:{value:new te(nn.glare.strength,nn.glare.from)},shine:{value:new v(nn.shine.lift,nn.shine.core,nn.shine.tightness)}}),e}const Qc={depth:.06,behind:.01},XE=i=>i.name==="head_shell"||i.name.endsWith("__shell");function Bd(i,e=.05){const t=i.attributes.position,n=a=>i.index?i.index.getX(a):a,s=i.index?i.index.count:t.count,r=(a,c)=>a*100003+c,o=new Map;for(let a=0;a<s;a+=3){const c=[0,1,2].map(g=>{const p=n(a+g);return{x:t.getX(p),y:t.getY(p),z:t.getZ(p)}}),[l,h,u]=c,[d,f]=[Math.floor(Math.min(l.x,h.x,u.x)/e),Math.floor(Math.max(l.x,h.x,u.x)/e)],[m,_]=[Math.floor(Math.min(l.y,h.y,u.y)/e),Math.floor(Math.max(l.y,h.y,u.y)/e)];for(let g=d;g<=f;g++)for(let p=m;p<=_;p++){const y=r(g,p);o.has(y)||o.set(y,[]),o.get(y).push(c)}}return(a,c)=>(o.get(r(Math.floor(a/e),Math.floor(c/e)))??[]).reduce((l,h)=>{const u=qE(h,a,c);return u===null||l!==null&&l>=u?l:u},null)}function qE([i,e,t],n,s){const r=(e.x-i.x)*(t.y-i.y)-(t.x-i.x)*(e.y-i.y);if(Math.abs(r)<1e-12)return null;const o=((e.x-n)*(t.y-s)-(t.x-n)*(e.y-s))/r,a=((t.x-n)*(i.y-s)-(i.x-n)*(t.y-s))/r,c=1-o-a;return o>=-1e-9&&a>=-1e-9&&c>=-1e-9?o*i.z+a*e.z+c*t.z:null}const jE=(i,e,t)=>i.map(n=>n(e,t)).reduce((n,s)=>s===null||n!==null&&n>=s?n:s,null);function $E(i,e){const t=e.map(o=>Bd(o)),n=i.attributes.position;let s=-1/0;for(let o=0;o<n.count;o++)s=Math.max(s,n.getZ(o)-(jE(t,n.getX(o),n.getY(o))??1/0));i.translate(0,0,-(s+Qc.depth));const r=Bd(i);for(const o of e){const a=o.attributes.position;for(let c=0;c<a.count;c++){const l=r(a.getX(c),a.getY(c));l!==null&&a.getZ(c)>l-Qc.behind&&a.setZ(c,l-Qc.behind)}a.needsUpdate=!0}}function YE(i,e,t){var o,a;const n=(o=i.userData).waiting??(o.waiting=[]),s=e.map(({column:c,row:l,colour:h})=>`${c},${l},${h.join(",")}`).join(";");if(s!==(((a=n.at(-1))==null?void 0:a.key)??i.userData.shownKey)&&n.push({key:s,lit:e}),n.length>nn.framesBehind&&n.splice(0,n.length-nn.framesBehind),i.userData.frame===t||!n.length)return;const r=n.shift();ZE(i.uniforms.pixels.value,r.lit),i.userData.shownKey=r.key,i.userData.frame=t}function KE(){const i=new ph(new Uint8Array(ws.columns*ws.rows*4),ws.columns,ws.rows);return i.magFilter=i.minFilter=pn,i.needsUpdate=!0,i}function ZE(i,e){const t=i.image.data;t.fill(0);for(const{column:n,row:s,colour:r}of e)t.set([...r.map(o=>Math.round(o*255)),255],(s*ws.columns+n)*4);i.needsUpdate=!0}const JE=`
    uniform vec3 colour;

    void main() {
        gl_FragColor = vec4(colour, 1.0);
        #include <colorspace_fragment>
    }
`,_p=(i,e)=>({push:{value:e/i.getWorldScale(new v).x}});function Dh(i){const{r:e,g:t,b:n}=i.material.color;return new oi({vertexShader:gp,fragmentShader:HE,side:An,uniforms:{..._p(i,0),colour:{value:new v(e,t,n)},light:{value:gw.clone().normalize().applyMatrix4(Tr)},shade:{value:$l},litFrom:{value:_w},bulbAt:{value:new v},bulbGlow:{value:new v},bulbFalloff:{value:ar.falloff}}})}function xp(i){return new oi({vertexShader:gp,fragmentShader:JE,side:yn,defines:{HULL:""},uniforms:{..._p(i,vw),colour:{value:xw}}})}const QE=-.5;function Nh(i){const e=i.attributes.position,t=Array.from({length:e.count},(o,a)=>new v().fromBufferAttribute(i.attributes.normal,a)),n=new Map,s=o=>`${e.getX(o).toFixed(5)},${e.getY(o).toFixed(5)},${e.getZ(o).toFixed(5)}`;for(let o=0;o<e.count;o++){const a=n.get(s(o))??[];a.push(o),n.set(s(o),a)}const r=new Float32Array(e.count*3);for(let o=0;o<e.count;o++){const a=new v;for(const c of n.get(s(o)).filter(l=>t[o].dot(t[l])>QE))a.add(t[c]);a.normalize().toArray(r,o*3)}i.setAttribute("hullNormal",new en(r,3))}function Xr(i,e){const t=new Set;for(const n of i.filter(s=>e.has(s.userData.item)))t.add(new tn().setFromObject(n).getCenter(new v).x>=0?"l":"r");return t}function e1(i){const e=[];i.traverse(a=>a.isBone&&e.push(a));const t=new Map(e.map(a=>[a.name,a.parent.isBone?a.parent.name:""])),n=new Map(e.map(a=>[a.name,a.matrixWorld.clone()])),s=new Map(e.map(a=>[a.name,Aa(new v().setFromMatrixPosition(a.matrixWorld))])),r=new Map(e.map(a=>[a.name,new v().setFromMatrixColumn(a.matrixWorld,1).transformDirection(ja)])),o=[];return i.traverse(a=>{!a.isSkinnedMesh||!a.name.startsWith("eye_")||!a.userData.hull||o.push(Aa(new tn().setFromBufferAttribute(a.geometry.attributes.position).getCenter(new v).applyMatrix4(a.matrixWorld)))}),{bones:e,order:e.map(a=>a.name),parents:t,rest:n,heads:s,along:r,eyes:o}}async function t1(i){const e=await el.raw(i);if(e.ok)return e.arrayBuffer();const t=await el.raw(`${i}.txt`).then(n=>n.text());return Uint8Array.from(atob(t),n=>n.charCodeAt(0)).buffer}async function dT(i,e,t){const[n,s]=await Promise.all([t1(i),el.raw(e).then(a=>a.json())]),r=t==="bare",o=new Set((r?[]:s.outfits[t]).flatMap(a=>s.assets[a].hide_base_parts));return i1(n,t,fw,a=>!o.has(a.name)&&!(r&&a.userData.item))}const n1={butler:RM};async function i1(i,e,t,n=()=>!0){const r=(await new CM().setDRACOLoader(new hw().setDecoderPath(t)).parseAsync(i,"")).scene;r.updateMatrixWorld(!0);const o=[];r.traverse(E=>E.isSkinnedMesh&&o.push(E));const a=(n1[e]??(E=>E))(o);$E(a.find(E=>E.name===la).geometry,a.filter(XE).map(E=>E.geometry));const c=[],l=[];for(const E of a){E.visible=n(E)&&!Ew.has(E.userData.item)&&E.userData.item!==Xc,Nh(E.geometry);const T=new fh(E.geometry,xp(E));T.bind(E.skeleton,E.bindMatrix),T.visible=E.visible,E.userData.hull=T,T.userData.item=E.userData.item,T.frustumCulled=E.frustumCulled=!1,E.material=E.name===la?WE(E):Dh(E),E.name===la&&c.push(E.material),E.name===la&&l.push(T),E.parent.add(T),T.position.copy(E.position),T.quaternion.copy(E.quaternion),T.scale.copy(E.scale),E.name.startsWith("eye_")&&(E.visible=T.visible=!1),GE.some(P=>E.name.startsWith(P))&&(E.visible=T.visible=!1)}const h=a.filter(E=>E.visible),u=Xr(h,qa),d=a.filter(E=>E.userData.item===Xc&&n(E)),f={voice:e,level:Xr(h,Vf),busy:u,carried:Xr(h,Mt),free:new Set(Object.keys(H).filter(E=>!u.has(E))),tablet:Xr(d,new Set([Xc])),shield:Xr(h,new Set(["squire_shield"]))},m=r1(),_=F1(),g=d1();r.add(m,_,...g.values());const p={bulbAt:{value:new v},bulbGlow:{value:new v}};r.traverse(E=>{var T,P;return((P=(T=E.material)==null?void 0:T.uniforms)==null?void 0:P.bulbGlow)&&Object.assign(E.material.uniforms,p)});const y=E=>E.flatMap(T=>[T,T.userData.hull]),M=h.filter(E=>Mt.has(E.userData.item)),x=y(h.filter(E=>E.userData.item));return{scene:r,rig:e1(r),stance:f,screens:c,visorHulls:l,laptop:m,book:_,propByName:g,props:[...g.values()],stowable:x,tablet:y(d),inHand:y(M),bulbLight:p}}const s1={width:1.7,depth:.62,thickness:.1,open:105},qr={base:4672082,lid:2829880,screen:1776932,edge:11120056,mark:6186185},es=(i,e)=>{const t=new Xt(i,new fn({color:e,side:An}));return t.frustumCulled=!1,t};function r1(){const{width:i,depth:e,thickness:t,open:n}=s1,s=(u,d,f,m)=>{const _=es(new ht(d,f,m),u);return _.add(new fo(new Ha(_.geometry),new As({color:qr.edge}))),_},r=s(qr.base,i,t,e);r.position.set(0,t/2,-e/2);const o=s(qr.lid,i,e,t);o.position.set(0,e/2,t/2);const a=es(new ai(i*.88,e*.82),qr.screen);a.position.set(0,e/2,-.002);const c=es(new Ri(e*.12,20),qr.mark);c.position.set(0,e/2,t+.002);const l=new Ct;l.position.y=t,l.rotation.x=Qe(n-90),l.add(o,a,c);const h=new Ct;return h.matrixAutoUpdate=!1,h.visible=!1,h.add(r,l),h}const Zs={lights:[.144,.267,.389,.511],light:.047,vents:[.633,.711,.789,.867],vent:[.033,.49]},Js={front:1842725,top:2895673,side:1184536,vent:329224,edge:4869724};function o1(i){const e=ss.width*i,t=Math.asin(ss.top/ss.width),n=(ss.height-ss.top)*i/Math.cos(t)/ss.units,[s,r,o]=[Js.side,Js.top,Js.front].map(u=>new fn({color:u})),a=[],c=Array.from({length:ss.units},(u,d)=>{const f=new Xt(new ht(e,n,e),[s,s,r,s,o,s]);f.add(new fo(new Ha(f.geometry),new As({color:Js.edge}))),f.position.set(0,n*(d+.5),-e/2);const m=(_,g)=>(_.position.set(e*(g-.5),0,e/2+.002),f.add(_),_);return a.push(...Zs.lights.map(_=>m(new Xt(new Ri(e*Zs.light,12),new fn),_))),Zs.vents.forEach(_=>m(es(new ai(e*Zs.vent[0],n*Zs.vent[1]),Js.vent),_)),f}),l=new Ct;l.rotation.x=t,l.add(...c);const h=new Ba;return h.add(l),h.updateMatrixWorld(!0),{scene:h,lights:a,bounds:new tn().setFromObject(l)}}function a1(i,e,t){const n=new Ve(Js.front);i.lights.forEach((s,r)=>{const o=new Ve().setRGB(...Gp[e],qt);s.material.color.copy(n.clone().lerp(o,Vp(e,t,r%Zs.lights.length)))})}const kt={hull:[[0,-.27],[.32,-.29],[.64,-.2],[.92,-.06],[1,0],[.93,.07],[.62,.15],[.38,.19],[0,.2]],band:.04,dome:.4,antenna:[.16,.05],lights:10,light:.075,lamp:.26,tilt:16,colours:{hull:12172744,band:6119792,dome:13625087,antenna:6119792,dark:3816778,lamp:16774056,lit:[15251530,6514417]}};function c1(i){const e=ya.width/2*i,t=new Ct;t.name="saucer";const n=new br(kt.hull.map(([h,u])=>new te(h*e,u*e)),48);Te(t,"hull",n,kt.colours.hull),Te(t,"band",new Hn(e*.985,e*kt.band,8,64),kt.colours.band).rotation.x=Math.PI/2;const s=kt.hull.at(-1)[1]*e*.9;Te(t,"dome",new Mn(e*kt.dome,32,16,0,Math.PI*2,0,Math.PI/2),kt.colours.dome,[0,s,0]);const[r,o]=kt.antenna.map(h=>h*e);Te(t,"antenna",new et(o*.25,o*.25,r,8),kt.colours.antenna,[0,s+e*kt.dome+r/2,0]),Te(t,"ball",new Mn(o,12,8),kt.colours.lit[0],[0,s+e*kt.dome+r,0]);const a=Array.from({length:kt.lights},(h,u)=>{const d=u/kt.lights*Math.PI*2;return Te(t,`light_${u}`,new Mn(e*kt.light,12,8),kt.colours.dark,[Math.sin(d)*e,0,Math.cos(d)*e])}),c=-(ya.belly*i)/Math.cos(Qe(kt.tilt));Te(t,"lamp",new et(e*kt.lamp,e*kt.lamp*1.15,e*.07,24),kt.colours.lamp,[0,c,0]),t.rotation.x=Qe(kt.tilt),t.position.y=Nn;const l=new Ba;return l.add(t),l.updateMatrixWorld(!0),{scene:l,lights:a,middle:new v(0,Nn,0),bounds:new tn().setFromObject(t)}}function l1(i,e){i.lights.forEach((t,n)=>{const s=new Ve(n%ya.blink===e?kt.colours.lit[Math.floor(n/ya.blink)%2]:kt.colours.dark);t.material.uniforms.colour.value.set(s.r,s.g,s.b)})}const En={panels:8,reach:1.15,flat:.62,vent:.14,tilt:14,lines:[-.35,.35],colours:{gores:[14238011,16183779],vent:9382438}};function h1(i,e){const t=ie.chute.width*e/2/Math.sin(En.reach)*i,n=new Ct;n.name="canopy";const s=new Ct;s.name="canopy",s.scale.y=En.flat,n.add(s);for(let u=0;u<En.panels;u++){const d=new Mn(t,8,10,u/En.panels*Math.PI*2,Math.PI*2/En.panels,0,En.reach);Te(s,`gore_${u}`,d,En.colours.gores[u%2])}Te(s,"vent",new Mn(t*1.01,16,4,0,Math.PI*2,0,En.vent),En.colours.vent);const r=t*Math.sin(En.reach),o=t*Math.cos(En.reach)*En.flat,c=[-1,1].flatMap(u=>En.lines.map(d=>new v(u*r*Math.cos(d),o,r*Math.sin(d)))).map(u=>{const d=new Nt;return d.position.copy(u),n.add(d),d});n.rotation.x=Qe(En.tilt),n.position.y=Nn-o;const l=new Ba;l.add(n),l.updateMatrixWorld(!0);const h=new v(0,o,0).applyMatrix4(n.matrixWorld);return{scene:l,middle:h,ends:c.map(u=>new v().setFromMatrixPosition(u.matrixWorld)),bounds:new tn().setFromObject(n)}}const ho={radius:.52,rim:.08,handle:.5,grip:.07},jr={rim:2829880,lens:13625087,handle:4672082,edge:11120056,glint:16777215};function u1(i){const{radius:e,rim:t,handle:n,grip:s}=ho,r=(u,d,f={})=>{const m=new Xt(u,new fn({color:d,side:An,...f}));return m.frustumCulled=!1,m},o=new Ct;i.add(o);const a=r(new Hn(e,t,12,48),jr.rim);a.position.y=n/2+e,a.add(new fo(new Ha(new Ri(e+t,48)),new As({color:jr.edge})));const c=r(new Ri(e,48),jr.lens,{transparent:!0,opacity:.18,depthWrite:!1});c.position.y=n/2+e;const l=r(new wh(e*.55,e*.72,24,1,Math.PI*.55,Math.PI*.4),jr.glint);l.position.set(0,n/2+e,.008);const h=r(new et(s,s*1.2,n,16),jr.handle);o.add(h,a,c,l),i.userData.shape=({magnifies:u=0,size:d=1,roll:f=0})=>{o.scale.setScalar(u?d:1),l.rotation.z=Qe(f)}}const Ue={width:.82,height:1.2,cover:.055,pages:.06,spine:.18,inset:.035,open:160,tilt:8,gripHeight:.02,gripSide:.1,closedGrip:.2,gripBack:.6,leaf:.004,curl:2,pageSegments:12,pageBow:.24,lines:5,lineWidth:.004},gs={cover:6514417,spine:3487563,pages:15986399,paper:16776175,edge:2303282,rule:13024940},vp=i=>Qe((180-Ue.open*i)/2);function Jl(i,e){const t=H[i],n=i==="l"?1:e;return new v(t*Ue.width*n,Ue.gripHeight,Ue.cover/2).applyAxisAngle(new v(0,1,0),t*vp(e)).add(new v(t*Ue.spine/2,0,0))}function yp(i){const e=Jl("l",i).sub(Jl("r",i)).normalize(),t=new v(0,1,0);return new Ae().makeBasis(e,t,e.clone().cross(t))}function Mp(i){return new Ae().makeRotationX(Qe(Ue.tilt)).multiply(yp(i).invert())}function Ki(i,e){const t=yp(e),n=new v().setFromMatrixColumn(t,0),s=new v().setFromMatrixColumn(t,2);return Jl(i,e).addScaledVector(n,H[i]*(Ue.gripSide+Ue.closedGrip*(1-e))).addScaledVector(s,-Ue.gripBack)}const ln={pen:{radius:.027,length:.58,tip:.08,sides:12,markerScale:1.8,pencilSides:6,bandScale:1.05,bandAt:1/3},feather:{at:1/4,points:[[0,0],[-.12,.18],[-.08,.42],[.03,.6],[.14,.34],[.1,.12]]},paper:{width:1.58,depth:.54,thickness:.012,count:4,spread:.04,tabletLayers:3,screenWidth:.91,screenDepth:.85,screenLift:2},whistle:{body:[.13,.1,.16],mouthpiece:[.08,.04,.15],mouthAt:[0,.01,-.12]},cloth:{width:.35,depth:.26,thickness:.02},hammer:{handleRadius:.06,handleLength:1.2,gripFrom:.15,head:[.55,.22,.22],sides:10,tilt:45},straw:{radius:.03,length:.7,head:[.045,.16]},colours:{ink:2566454,silver:11120056,paper:15986399,white:16052973,accent:6514417,pencil:14069867,handle:9067051,straw:15255146}};function d1(){const i=new Map,e=f=>{const m=new Ct;return m.name=f,m.visible=!1,m.matrixAutoUpdate=!1,i.set(f,m),m},t=(f,m,_,g,p=[0,0,0])=>{const y=es(_,g);return y.name=`${f.name}_${m}`,y.position.set(...p),f.add(y),y},{pen:n,paper:s,cloth:r,colours:o}=ln;for(const f of Object.values(ip)){const m=e(f),_=f==="writing_marker",g=f==="writing_pencil",p=n.radius*(_?n.markerScale:1);t(m,"barrel",new et(p,p,n.length,g?n.pencilSides:n.sides),g?o.pencil:o.ink);const y=t(m,"nib",new si(p,n.tip,n.sides),o.silver,[0,-(n.length+n.tip)/2,0]);if(y.rotation.z=Math.PI,t(m,"band",new et(p*n.bandScale,p*n.bandScale,n.tip/2,n.sides),o.accent,[0,n.length*n.bandAt,0]),f==="writing_quill"){const x=new Ps;x.moveTo(...ln.feather.points[0]);for(const E of ln.feather.points.slice(1))x.lineTo(...E);x.closePath(),t(m,"feather",new Wa(x),o.white,[0,n.length*ln.feather.at,0])}const M=new Nt;M.name="tip",M.position.y=-n.length/2-n.tip,m.add(M),m.userData.tip=M}for(const f of["papers","writing_paper","writing_tablet"]){const m=e(f),_=f==="writing_tablet",g=f==="papers"?s.count:1;m.userData.sheets=[];for(let p=0;p<g;p++){const y=t(m,`sheet_${p}`,new ht(s.width,s.thickness*(_?s.tabletLayers:1),s.depth),_?o.ink:o.paper,[0,p*s.thickness,0]);m.userData.sheets.push(y)}_&&t(m,"screen",new ht(s.width*s.screenWidth,s.thickness,s.depth*s.screenDepth),o.accent,[0,s.thickness*s.screenLift,0])}i.get("papers").userData.shape=({phase:f})=>{const m=ce(f,0,.3)*(1-ce(f,.8,1));i.get("papers").userData.sheets.forEach((_,g)=>{_.position.x=s.spread*g*(1-m),_.rotation.y=s.spread*g*(1-m)})};const a=e("hand_whistle");t(a,"body",new ht(...ln.whistle.body),o.accent),t(a,"mouthpiece",new ht(...ln.whistle.mouthpiece),o.silver,ln.whistle.mouthAt);const{hammer:c}=ln,l=e("work_hammer");t(l,"handle",new et(c.handleRadius,c.handleRadius,c.handleLength,c.sides),o.handle,[0,c.handleLength/2-c.gripFrom,0]),t(l,"head",new ht(...c.head),o.silver,[0,c.handleLength-c.gripFrom,0]);const{straw:h}=ln,u=e("straw");t(u,"stalk",new et(h.radius,h.radius,h.length,6),o.straw,[0,h.length/2,0]),t(u,"seeds",new si(...h.head,6),o.pencil,[0,h.length+h.head[1]/2,0]),u1(e("magnifying_glass"));const d=e("polishing_cloth");return t(d,"fold",new ht(r.width,r.thickness,r.depth),o.white),D1(e,t),L1(e("telephone"),e("telephone_handset"),e("telephone_cord"),e("telephone_poof")),C1(e("light_bulb")),R1(e("report_scroll")),A1(e("binoculars")),g1(e("rifle")),x1(e("big_mallet")),v1(e("halo")),M1(e("crucifix")),b1(e("pocket_watch")),E1(e("rope_swing")),p1(e),i}const f1={papers:{sheet:[.9,.02,.66],count:3,fan:18},boot:{shaft:[.4,.72,.45],foot:[.4,.3,.84],sole:.07},bone:{spine:1.1,ribs:5,rib:.5,head:[.24,.18,.08],tail:[.2,.26],thick:.035},book:{cover:[.75,.15,.56],pages:[.7,.12,.53]},colours:{paper:16183779,leather:7029798,sole:2761760,bone:15525074,cover:11022906,pages:15985362}};function p1(i){const{papers:e,boot:t,bone:n,book:s,colours:r}=f1,o=[],a=_=>{const g=i(_),p=new Ct;return p.name=_,g.add(p),g.userData.shape=({size:y=1})=>p.scale.setScalar(Math.max(y,.001)),o.push(p),p},c=a("rummage_papers");for(let _=0;_<e.count;_++){const g=Te(c,`sheet_${_}`,new ht(...e.sheet),r.paper,[0,_*e.sheet[1]*2,0]);g.rotation.y=Qe(e.fan*(_-(e.count-1)/2))}const l=a("rummage_boot");Te(l,"shaft",new ht(...t.shaft),r.leather,[0,t.foot[1]+t.shaft[1]/2,0]),Te(l,"foot",new ht(...t.foot),r.leather,[0,t.foot[1]/2,(t.foot[2]-t.shaft[2])/2]),Te(l,"sole",new ht(t.foot[0]*1.05,t.sole,t.foot[2]*1.04),r.sole,[0,0,(t.foot[2]-t.shaft[2])/2]);const h=a("rummage_bone"),u=Te(h,"spine",new et(n.thick,n.thick,n.spine,6),r.bone);u.rotation.z=Math.PI/2;for(let _=0;_<n.ribs;_++){const g=(_/(n.ribs-1)-.5)*n.spine*.7,p=n.rib*(1-Math.abs(g)/n.spine);Te(h,`rib_${_}`,new et(n.thick*.7,n.thick*.7,p,5),r.bone,[g,0,0])}Te(h,"head",new Mn(1,14,10),r.bone,[n.spine/2+n.head[0]*.8,0,0]).scale.set(...n.head);const f=Te(h,"tail",new si(n.tail[0],n.tail[1],3),r.bone,[-n.spine/2-n.tail[1]/2,0,0]);f.rotation.z=-Math.PI/2;const m=a("rummage_book");Te(m,"cover",new ht(...s.cover),r.cover),Te(m,"pages",new ht(...s.pages),r.pages,[(s.cover[0]-s.pages[0])/2+.03,0,0]);for(const _ of o){_.updateMatrixWorld(!0);const g=new tn().setFromObject(_).getCenter(new v).sub(_.getWorldPosition(new v));for(const p of _.children)p.position.sub(g)}}const m1={barrel:.24,length:.6,apart:.54,rim:.045,eyepiece:[.15,.14],bridge:[.28,.13,.22],colours:{body:2763830,rim:10133677,eyepiece:1776674,lens:9356799}},tr={scale:1.4,stock:[[-.42,0,0],[.5,.09,.16]],receiver:[[.1,0,.04],[.46,.1,.14]],grip:[[-.03,0,-.1],[.08,.08,.2]],magazine:[[.2,0,-.15],[.1,.07,.26]],handguard:[[.55,0,.04],[.42,.1,.11]],sight:[[.24,0,.14],[.06,.04,.06]],front:[[1.17,0,.11],[.03,.03,.07]],barrel:{from:.76,to:1.24,radius:.03,up:.06},colours:{wood:9067051,metal:2829880,barrel:4672082,flash:16765530}},Ms={barrel:tr.barrel.up*tr.scale,fore:.55*tr.scale,nearest:.38*tr.scale,under:.17,roll:90,low:.5};function Cr(i){const e=new Ct;return e.name=i.name,e.rotation.x=-Math.PI/2,i.add(e),e}function g1(i){const e=Cr(i),{colours:t,barrel:n,scale:s}=tr,r=d=>d.map(f=>f*s);for(const d of["stock","receiver","grip","magazine","handguard","sight","front"]){const[f,m]=tr[d];Te(e,d,new ht(...r(m)),["stock","handguard"].includes(d)?t.wood:t.metal,r(f))}const[o,a,c,l]=r([n.from,n.to,n.radius,n.up]),h=Te(e,"barrel",new et(c,c,a-o,12),t.barrel,[(o+a)/2,0,l]);h.rotation.z=Math.PI/2;const u=Te(e,"flash",new Mh(.12*s,0),t.flash,[a+.1*s,0,l]);u.scale.set(1.6,.6,1),i.userData.shape=({firing:d})=>u.visible=!!d}const _1={handle:2,grip:.06,head:.42,width:.85,band:.04,colours:{handle:11565637,head:10185274,band:7040892}};function x1(i){const e=Cr(i),{handle:t,grip:n,head:s,width:r,band:o,colours:a}=_1;Te(e,"handle",new et(n,n*1.2,t,12),a.handle,[t/2,0,0]).rotation.z=Math.PI/2,Te(e,"head",new et(s,s,r,20),a.head,[t,0,0]).rotation.x=Math.PI/2;for(const c of[-1,1])Te(e,`band_${c}`,new et(s*1.04,s*1.04,o,20),a.band,[t,0,c*(r/2-o)]).rotation.x=Math.PI/2}function v1(i){const e=Te(Cr(i),"ring",new Hn(no.radius,no.ring,10,40),15910987);e.rotation.x=Qe(no.tip),i.userData.shape=({size:t})=>e.scale.setScalar(t??1)}const y1={long:.86,across:.5,bar:.09,at:.24,colours:{wood:14263361,gold:16180129}};function M1(i){const e=Cr(i),{long:t,across:n,bar:s,at:r,colours:o}=y1;Te(e,"upright",new ht(s,s,t),o.wood,[0,0,t*.2]),Te(e,"crossbar",new ht(n,s,s),o.wood,[0,0,t*.2+r]),Te(e,"centre",new Mn(s*.7,10,8),o.gold,[0,-s*.5,t*.2+r])}const w1={radius:.2,depth:.08,bow:.06,colours:{gold:15251530,face:16183779,hands:2566454}};function b1(i){const e=Cr(i),{radius:t,depth:n,bow:s,colours:r}=w1,o=new wn(Math.PI/2,0,0);Te(e,"case",new et(t,t,n,24).applyMatrix4(new Ae().makeRotationFromEuler(o)),r.gold,[0,0,0]),Te(e,"face",new et(t*.82,t*.82,n*.3,24).applyMatrix4(new Ae().makeRotationFromEuler(o)),r.face,[0,-n*.45,0]),Te(e,"hour_hand",new ht(t*.08,n*.2,t*.45),r.hands,[t*.1,-n*.62,t*.18]),Te(e,"minute_hand",new ht(t*.6,n*.2,t*.06),r.hands,[t*.28,-n*.62,0]),Te(e,"bow",new Hn(s,s*.3,8,16).applyMatrix4(new Ae().makeRotationFromEuler(o)),r.gold,[0,0,t+s*.8])}const S1={thick:.14,front:-.12,back:.4,cord:.035,knot:.08,colours:{wood:9067051,rope:13215082}};function E1(i){const e=Cr(i),[t,n,s,r]=["seat","ties","rope","under"].map(f=>ie.rope_swing[f]*Ht),{thick:o,front:a,back:c,cord:l,knot:h,colours:u}=S1,d=(a+c)/2;Te(e,"seat",new ht(t,c-a,o),u.wood,[0,d,-r-o/2]);for(const[f,m]of Object.entries(H)){const _=new et(l,l,s+r,8).rotateX(Math.PI/2);Te(e,`rope_${f}`,_,u.rope,[m*n/2,d,(s-r)/2]),Te(e,`knot_${f}`,new Va(h,1),u.rope,[m*n/2,d,s])}}const Ks={long:15,tilt:22,colours:{body:8016434,head:4861724,leg:2829880,shine:12094044}};function T1(i,e){const t=Ks.long*i,n=new Ct;n.name="bug",Te(n,"body",new Mn(t*.38,18,12),Ks.colours.body,[t*.1,0,t*.3]).scale.set(1.3,.85,.75),Te(n,"head",new Mn(t*.2,14,10),Ks.colours.head,[-t*.42,0,t*.3]);for(const[o,a]of[-.18,.1,.38].entries())for(const c of[-1,1]){const l=Math.sin(Math.PI*(e+o/3+(c>0?.5:0))*2)*.12,h=Te(n,`leg_${o}_${c}`,new et(t*.035,t*.035,t*.42,6),Ks.colours.leg,[t*(a+l),c*t*.28,t*.14]);h.rotation.x=c*.9}for(const o of[-1,1])Te(n,`feeler_${o}`,new et(t*.02,t*.02,t*.36,5),Ks.colours.leg,[-t*.64,o*t*.08,t*.48]).rotation.set(o*.4,0,.9);n.rotation.x=Qe(Ks.tilt),n.position.y=Nn;const r=new Ba;return r.add(n),r.updateMatrixWorld(!0),{scene:r,foot:new v(0,Nn,0),bounds:new tn().setFromObject(n)}}function A1(i){const{barrel:e,length:t,apart:n,rim:s,eyepiece:r,bridge:o,colours:a}=m1,c=l=>(l.rotation.x=Math.PI/2,l);for(const[l,h]of[-1,1].entries()){const u=h*n/2;c(Te(i,`barrel_${l}`,new et(e,e*.9,t,20),a.body,[u,0,t/2])),Te(i,`rim_${l}`,new Hn(e,s,10,28),a.rim,[u,0,t]),c(Te(i,`eyepiece_${l}`,new et(r[0],r[0],r[1],16),a.eyepiece,[u,0,-r[1]/2]));const d=new Xt(new Ri(e*.85,24),new fn({color:a.lens,side:An}));d.name=`${i.name}_lens_${l}`,d.position.set(u,0,t+.004),d.frustumCulled=!1,i.add(d)}Te(i,"bridge",new ht(...o),a.body,[0,0,t*.45])}const wp={roller:.045,length:1.25,knob:.075,wound:.11,unwound:.06,turns:1.5,width:1,bow:.06,curl:.08,rows:10,columns:16,rolled:.22,colours:{wood:9067051,knob:7029280,back:14469020,wound:15128238}};function R1(i){const{roller:e,length:t,knob:n,wound:s,unwound:r,turns:o,width:a,bow:c,curl:l,rows:h,columns:u,colours:d}=wp,f=["top","bottom"].map(p=>{const y=new Ct;y.name=`${i.name}_${p}`,i.add(y);const M=Te(y,"roller",new et(e,e,t,14),d.wood);M.rotation.z=Math.PI/2;for(const E of[-1,1])Te(y,`knob_${E>0?"l":"r"}`,new Mn(n,14,10),d.knob,[E*t/2,0,0]);const x=Te(y,"wound",new et(1,1,a,18),d.wound);return x.rotation.z=Math.PI/2,{group:y,sleeve:x,rod:M}}),m=new ai(a,1,u,h),_=Te(i,"parchment",m,d.back),g=p=>new v(p.x,p.z,-p.y);i.userData.shape=({top:p,bottom:y,open:M})=>{const[x,E]=[g(p),g(y)],T=Bt(s,r,M);f.forEach(({group:C,sleeve:b,rod:w},L)=>{C.position.copy(L?E:x),b.scale.set(T,1,T),w.rotation.x=(L?-1:1)*o*2*Math.PI*M}),_.visible=M>.02;const P=m.attributes.position;for(let C=0;C<=h;C++){const b=C/h,w=x.clone().lerp(E,b);for(let L=0;L<=u;L++){const F=L/u-.5,O=c*Math.sin(Math.PI*b)*M-l*(2*F)**4;P.setXYZ(C*(u+1)+L,w.x+F*a,w.y,w.z+T+O)}}P.needsUpdate=!0,m.computeVertexNormals(),m.setAttribute("hullNormal",m.attributes.normal.clone())}}const ar={at:[.95,-.25,4.05],globe:.36,neck:.15,base:[.15,.22],threads:3,filament:.14,wire:.014,halo:1.7,strength:1.4,falloff:.6,colours:{glass:14937587,glassLit:16769658,base:12041414,contact:3816775,filament:5988203,filamentLit:16774338,warm:[1,.82,.42]}};function C1(i){const{globe:e,neck:t,base:n,threads:s,filament:r,wire:o,halo:a,colours:c}=ar,l=new Ct;l.name=i.name,i.add(l);const h=[[0,e*1.95],[e*.55,e*1.85],[e*.92,e*1.45],[e,e],[e*.88,e*.55],[t*1.2,e*.18],[t,0]].map(([E,T])=>new te(E,T)).reverse(),u=Te(l,"glass",new br(h,28),c.glass);u.material.uniforms.shade={value:$l.clone()};const[d,f]=n;Te(l,"base",new et(d,d*.92,f,20),c.base,[0,-f/2,0]);for(let E=0;E<s;E++)Te(l,`thread_${E}`,new Hn(d*1.02,f/(s*4),6,20),c.base,[0,-f*((E+.6)/s),0]).rotation.x=Math.PI/2;Te(l,"contact",new Mn(d*.45,12,8),c.contact,[0,-f,0]);const m=new ka([[-r,e*.6],[-r*.5,e*1.15],[0,e*.95],[r*.5,e*1.15],[r,e*.6]].map(([E,T])=>new v(E,T,0))),_=new Ct;l.add(_);const p=[new gr(m,24,o*1.4,6),...[-1,1].map(E=>new gr(new Tf(new v(E*r,.02,0),new v(E*r,e*.6,0)),1,o,6))].map(E=>{const T=new Xt(E,new fn({color:c.filament,depthTest:!1}));return T.renderOrder=2,T.frustumCulled=!1,_.add(T),T}),y=new Xt(new Ri(e*a,32),new fn({color:new Ve(...c.warm),transparent:!0,depthWrite:!1}));y.position.set(0,e,-e*1.2),y.frustumCulled=!1,l.add(y);const M=new Ve(c.glass),x=new Ve(c.glassLit);i.userData.shape=({size:E,lit:T})=>{l.scale.setScalar(Math.max(E,.001));const P=M.clone().lerp(x,T);u.material.uniforms.colour.value.set(P.r,P.g,P.b),u.material.uniforms.shade.value.copy($l).lerp(new v(1.25,1.25,1.25),T);for(const C of p)C.material.color.set(c.filament).lerp(new Ve(c.filamentLit),T);y.visible=T>0,y.material.opacity=.35*T}}const Pt={at:[0,-.92],tip:10,base:{width:1.2,narrow:.18,depth:.85,height:.88,brow:[.08,.8],round:.16,dome:.06},dial:{plate:.42,face:.045,marks:.37,radius:.31,holes:10,hole:.05,ring:.22,first:60,spread:290,label:.11},cradle:{at:-.14,apart:.3,post:.055,height:.13},handset:{length:1.4,grip:.085,drop:.15,end:[.2,.15],rest:.06},cord:.022,coils:14,coil:.05,poof:{puffs:11,puff:.24,from:.5,to:.95},colours:{body:11022893,face:15853263,wheel:2829880,hole:16052973,mark:2829880,label:16052973,grille:2829880,smoke:15131630}};function Te(i,e,t,n,s=[0,0,0]){const r=new Xt(t,new fn({color:n}));Nh(t),r.material=Dh(r);const o=new Xt(t,xp(r));return o.frustumCulled=r.frustumCulled=!1,r.add(o),r.name=`${i.name}_${e}`,r.position.set(...s),i.add(r),r}function P1(){const{width:i,narrow:e,depth:t,height:n,brow:s,round:r,dome:o}=Pt.base,a=new Ps;a.moveTo(-t/2+r*.5,0),a.lineTo(t/2-r*.5,0),a.quadraticCurveTo(t/2,0,t/2-r*.2,r*.5),a.lineTo(s[0]+r*.3,s[1]-r*.4),a.quadraticCurveTo(s[0]-r*.2,n,s[0]-r*1.6,n),a.lineTo(-t/2+r*1.8,n),a.quadraticCurveTo(-t/2+r*.1,n,-t/2+r*.1,n-r*1.6),a.lineTo(-t/2,r*.5),a.quadraticCurveTo(-t/2,0,-t/2+r*.5,0);const c=i-2*r,l=new po(a,{depth:c,bevelEnabled:!0,bevelThickness:r,bevelSize:Ih(),bevelSegments:6,curveSegments:12});l.rotateY(-Math.PI/2).translate(c/2,0,0);const h=l.attributes.position;for(let u=0;u<h.count;u++){const[d,f]=[h.getX(u),Math.max(h.getY(u),0)];h.setX(u,d*(1-e*f/n)),h.setY(u,h.getY(u)+o*(f/n)**2*Math.max(1-(d/(i/2))**2,0))}return l.computeVertexNormals(),l}function L1(i,e,t,n){const{base:s,dial:r,cradle:o,colours:a}=Pt,c=new Ct;c.name=i.name,i.add(c),Te(c,"base",P1(),a.body);const l=new Ct;l.name=i.name,l.matrixAutoUpdate=!1,l.matrix.copy(hp()),c.add(l),Te(l,"dial_plate",new et(r.plate,r.plate,r.face,40),a.face,[0,r.face/2,0]);for(let C=0;C<r.holes;C++){const b=Qe(r.first+r.spread*C/(r.holes-1));Te(l,`number_${C}`,new ht(.03,r.face*.6,.045),a.mark,[Math.cos(b)*r.marks,r.face,-Math.sin(b)*r.marks])}const h=new Ct;h.name=i.name,h.position.y=r.face,l.add(h),Te(h,"dial_wheel",new et(r.radius,r.radius,r.face*.6,36),a.wheel,[0,r.face*.3,0]);for(let C=0;C<r.holes;C++){const b=Qe(r.first+r.spread*C/(r.holes-1));Te(h,`hole_${C}`,new et(r.hole,r.hole,r.face*.7,12),a.hole,[Math.cos(b)*r.ring,r.face*.4,-Math.sin(b)*r.ring])}Te(l,"dial_label",new et(r.label,r.label,r.face*1.6,24),a.label,[0,r.face,0]);const u=Qe(r.first+r.spread+22);Te(l,"dial_stop",new ht(.04,r.face*2.2,.1),a.label,[Math.cos(u)*(r.radius+.02),r.face*1.2,-Math.sin(u)*(r.radius+.02)]);for(const C of[1,-1]){const b=up(o.apart)+o.height;Te(c,`prong_${C}`,new et(o.post,o.post*1.4,o.height+.04,12),a.body,[C*o.apart,b-o.height/2-.02,o.at]),Te(c,`saddle_${C}`,new Hn(Pt.handset.grip*1.1,o.post*.45,8,14,Math.PI),a.body,[C*o.apart,b+Pt.handset.grip*.4,o.at]).rotation.set(0,Math.PI/2,Math.PI)}const d=new Ct;d.name=e.name,e.add(d);const{length:f,grip:m,drop:_,end:g}=Pt.handset,p=new ka([[-f/2,-_],[-f/2+.24,.02],[0,.06],[f/2-.24,.02],[f/2,-_]].map(([C,b])=>new v(C,b,0)));Te(d,"handle",new gr(p,32,m,12),a.body);for(const[C,b]of[["ear",1],["mouth",-1]]){const w=new Ct;w.name=e.name,w.position.set(b*f/2,-_,0),w.rotation.z=b*.22,d.add(w),Te(w,`${C}_piece`,new Mn(g[0],24,16),a.body,[0,-g[1]*.45,0]).scale.set(1,g[1]/g[0],1),Te(w,`${C}_grille`,new et(g[0]*.62,g[0]*.62,.025,20),a.grille,[0,-g[1]*.92,0])}i.userData.shape=({squash:C,dial:b})=>{c.scale.set(1+C/2,1-C,1+C/2),h.rotation.y=Qe(b)};const y=Te(t,"cord",kd(new v,new v(1,0,0)),a.body);t.userData.shape=({from:C,to:b})=>{y.geometry.dispose(),y.geometry=y.children[0].geometry=kd(C,b),Nh(y.geometry)};const{puffs:M,puff:x,from:E,to:T}=Pt.poof,P=Array.from({length:M},(C,b)=>Te(n,`puff_${b}`,new Va(x*(.75+.5*(b*7%5)/4),1),a.smoke));n.userData.shape=({puff:C})=>{P.forEach((b,w)=>{const L=2*Math.PI*w/M,F=E+(T-E)*Math.sqrt(C);b.position.set(Math.cos(L)*F,Math.sin(L*2)*F*.35,Math.sin(L)*F*.6),b.scale.setScalar(Math.max(Math.sin(Math.PI*C),.001))})}}function kd(i,e){const{cord:t,coils:n,coil:s}=Pt,r=u=>new v(u.x,u.z,-u.y),[o,a]=[r(i),r(e)],c=o.clone().lerp(a,.5).add(new v(0,-.35*o.distanceTo(a),0)),l=new vh(o,c,a),h=Array.from({length:n*8+1},(u,d)=>{const f=d/(n*8),m=l.getPoint(f),_=l.getTangent(f),g=new v(0,1,0).cross(_).normalize(),p=_.clone().cross(g).normalize(),y=2*Math.PI*n*f;return m.addScaledVector(g,Math.cos(y)*s).addScaledVector(p,Math.sin(y)*s)});return new gr(new ka(h),n*16,t,6)}const I1={monocle:{radius:.2,tube:.028,chain:.55,chainWidth:.012},flute:{base:.13,baseDepth:.025,stem:.022,stemLength:.35,rim:.12,bottom:.05,bowl:.4,fill:.27},shades:{lens:[.56,.34,.05],apart:.37,bridge:[.2,.05,.05],temple:[.04,.04,.7],shine:[.2,.035,.01]},flame:{outer:[.17,.55],inner:[.09,.32],sides:12,flickers:7},finger:{radius:.09,length:.22,splay:.6},popper:{mouth:.14,length:.45,sides:12},confetti:{count:18,size:.08,reach:1.5,fall:.9,spin:9},trophy:{base:[.38,.12,.38],stem:[.05,.08,.22],rim:.3,bottom:.12,cup:.38,handle:.12,handleTube:.03},sword:{grip:[.035,.26],guard:[.42,.06,.07],blade:[.09,1.3,.025],point:.15,pommel:.06},castle:{wall:[.6,.3,.25],crenel:[.1,.08,.25],tower:[.11,.5],roof:[.15,.24],gate:[.14,.18],pole:.24,flag:.14},colours:{hat:2697787,band:16052973,gold:15251530,glass:14542574,champagne:15848058,lens:1316380,flame:16742938,fire:16765503,hand:16116959,wood:8014374,stone:13222580,confetti:[6514417,15251530,15681391,448160,1149618]}};function D1(i,e){const{monocle:t,flute:n,shades:s,flame:r,finger:o,popper:a,confetti:c,trophy:l,sword:h,castle:u,colours:d}=I1,f=ln.colours.ink,m=ln.colours.silver,_=ln.colours.accent,g=i("top_hat");e(g,"crown",Uf(),d.hat),e(g,"band",Of(),new Ve(...xn.satin).getHex());const p=i("monocle");e(p,"ring",new Hn(t.radius,t.tube,8,24),d.gold),e(p,"lens",new Ri(t.radius,24),d.glass),e(p,"chain",new et(t.chainWidth,t.chainWidth,t.chain,6),d.gold,[t.radius*.7,-t.radius*.7-t.chain/2,0]);const y=i("champagne_flute");e(y,"base",new et(n.base,n.base,n.baseDepth,16),d.glass,[0,-n.stemLength/2,0]),e(y,"stem",new et(n.stem,n.stem,n.stemLength,8),d.glass),e(y,"bowl",new et(n.rim,n.bottom,n.bowl,16,1,!0),d.glass,[0,(n.stemLength+n.bowl)/2,0]),e(y,"wine",new et(n.rim*.9,n.bottom*.9,n.fill,16),d.champagne,[0,n.stemLength/2+n.fill/2+.01,0]);const M=i("sunglasses");for(const j of[1,-1])e(M,`lens_${j}`,new ht(...s.lens),d.lens,[j*s.apart,0,0]),e(M,`temple_${j}`,new ht(...s.temple),f,[j*(s.apart+s.lens[0]/2),s.lens[1]/4,-s.temple[2]/2]),e(M,`shine_${j}`,new ht(...s.shine),ln.colours.white,[j*s.apart-s.lens[0]/5,s.lens[1]/4,s.lens[2]/2]).rotation.z=.5;e(M,"bridge",new ht(...s.bridge),f,[0,s.lens[1]/4,0]);const x=i("flame"),E=e(x,"outer",new si(r.outer[0],r.outer[1],r.sides),d.flame,[0,r.outer[1]/2,0]),T=e(x,"inner",new si(r.inner[0],r.inner[1],r.sides),d.fire,[0,r.inner[1]/2,.03]);x.userData.shape=({phase:j,size:V})=>{const oe=1+.18*Math.sin(2*Math.PI*r.flickers*j)+.08*Math.sin(2*Math.PI*2.3*r.flickers*j);x.scale.set(V*(2-oe),V*oe,V*(2-oe)),E.rotation.z=T.rotation.z=.12*Math.sin(2*Math.PI*1.7*r.flickers*j)};const P=()=>new yh(o.radius,o.length,4,8);e(i("thumb"),"thumb",P(),d.hand,[0,o.length/2+o.radius,0]);const C=i("shaka");for(const j of[1,-1])e(C,`finger_${j}`,P(),d.hand,[j*o.length*.6,o.length/2,0]).rotation.z=-j*o.splay;const b=i("party_popper");e(b,"cone",new si(a.mouth,a.length,a.sides,1,!0),_,[0,a.length/2,0]).rotation.x=Math.PI,e(b,"rim",new Hn(a.mouth,.02,6,a.sides),d.gold,[0,a.length,0]).rotation.x=Math.PI/2;const w=Array.from({length:c.count},(j,V)=>{const oe=e(b,`confetti_${V}`,new ai(c.size,c.size),d.confetti[V%d.confetti.length]),_e=V*2.39996,Re=.25+.5*(V*7%c.count)/c.count;return oe.userData.way=new v(Math.sin(Re)*Math.cos(_e),Math.cos(Re),Math.sin(Re)*Math.sin(_e)),oe});b.userData.shape=({burst:j})=>{for(const[V,oe]of w.entries()){oe.visible=j>0&&j<1;const _e=c.reach*Math.sqrt(j);oe.position.set(oe.userData.way.x*_e,a.length+oe.userData.way.y*_e-c.fall*j*j,oe.userData.way.z*_e),oe.rotation.set(c.spin*j+V,c.spin*j*.7,V)}};const L=i("trophy");e(L,"base",new ht(...l.base),d.wood,[0,-l.stem[2]-l.base[1]/2,0]),e(L,"stem",new et(l.stem[0],l.stem[1],l.stem[2],12),d.gold,[0,-l.stem[2]/2,0]),e(L,"cup",new et(l.rim,l.bottom,l.cup,16),d.gold,[0,l.cup/2,0]);for(const j of[1,-1])e(L,`handle_${j}`,new Hn(l.handle,l.handleTube,6,12),d.gold,[j*l.rim,l.cup*.6,0]);const F=i("sword");e(F,"grip",new et(h.grip[0],h.grip[0],h.grip[1],8),d.wood),e(F,"pommel",new Mn(h.pommel,8,6),d.gold,[0,-h.grip[1]/2-h.pommel/2,0]),e(F,"guard",new ht(...h.guard),d.gold,[0,h.grip[1]/2+h.guard[1]/2,0]),e(F,"blade",new ht(...h.blade),m,[0,h.grip[1]/2+h.guard[1]+h.blade[1]/2,0]);const O=e(F,"point",new si(h.blade[0]/Math.SQRT2,h.point,4),m,[0,h.grip[1]/2+h.guard[1]+h.blade[1]+h.point/2,0]);O.rotation.y=Math.PI/4,O.scale.z=h.blade[2]/h.blade[0];const k=i("castle");e(k,"wall",new ht(...u.wall),d.stone,[0,u.wall[1]/2,0]);for(const j of[-1,0,1])e(k,`crenel_${j}`,new ht(...u.crenel),d.stone,[j*u.wall[0]/3,u.wall[1]+u.crenel[1]/2,0]);for(const j of[1,-1])e(k,`tower_${j}`,new et(u.tower[0],u.tower[0],u.tower[1],12),d.stone,[j*u.wall[0]/2,u.tower[1]/2,0]),e(k,`roof_${j}`,new si(...u.roof,12),_,[j*u.wall[0]/2,u.tower[1]+u.roof[1]/2,0]);e(k,"gate",new ai(...u.gate),f,[0,u.gate[1]/2,u.wall[2]/2+.005]);const K=u.tower[1]+u.roof[1];e(k,"pole",new et(.01,.01,u.pole,4),f,[u.wall[0]/2,K+u.pole/2,0]);const X=new Ps;X.moveTo(0,0),X.lineTo(u.flag,-u.flag/3),X.lineTo(0,-u.flag*2/3),X.closePath(),e(k,"flag",new Wa(X),d.gold,[u.wall[0]/2,K+u.pole,0])}function N1(i,{bone:e,frame:t,at:n,turn:s}){const r=n.clone().applyMatrix4(i.get(e));return Tr.clone().multiply(bs(r)).multiply(new Ae().extractRotation(i.get(t))).multiply($i(s.x||0,s.y||0,s.z||0)).multiply(ja)}function U1(i,e){const{bulbAt:t,bulbGlow:n}=i.bulbLight;n.value.set(...ar.colours.warm).multiplyScalar(ar.strength*e.bulbLit),e.bulbLit&&t.value.setFromMatrixPosition(i.propByName.get("light_bulb").matrix).add(new v(0,ar.globe,0))}function O1(i,e,t){var n,s;for(const[r,o]of i.propByName){const a=e.props.get(r);o.visible=!!a,a&&(o.matrix.copy(N1(t,a)),o.matrixWorldNeedsUpdate=!0,(s=(n=o.userData).shape)==null||s.call(n,a))}}function F1(){const i=(l,h,u,d,f)=>{const m=es(new ht(u,d,f),h);return m.name=l,m.add(new fo(new Ha(m.geometry),new As({color:gs.edge}))),m},e=new Ct;e.name="reading_book",e.matrixAutoUpdate=!1,e.visible=!1;const t=i("book_spine",gs.spine,Ue.spine,Ue.height,Ue.cover);e.add(t);const n={},s={},r={},o={};for(const[l,h]of Object.entries(H)){const u=new Ct;u.name=`book_hinge_${l}`,u.position.x=h*Ue.spine/2;const d=i(`book_cover_${l}`,gs.cover,Ue.width,Ue.height,Ue.cover);d.position.set(h*Ue.width/2,0,Ue.cover/2);const f=i(`book_pages_${l}`,gs.pages,Ue.width-Ue.inset,Ue.height-Ue.inset*2,Ue.pages);f.position.set(h*(Ue.width-Ue.inset)/2,0,-Ue.pages/2);for(let _=1;_<=Ue.lines;_++){const g=es(new ht(Ue.width-Ue.inset,Ue.lineWidth,Ue.lineWidth),gs.rule);g.position.set(f.position.x,-Ue.height/2+Ue.inset,-Ue.pages*_/(Ue.lines+1)),u.add(g)}u.add(d,f),e.add(u),n[l]=u,s[l]=d,r[l]=f;const m=new Nt;m.name=`book_grip_${l}`,e.add(m),o[l]=m}const a=es(new ai(Ue.width-Ue.inset,Ue.height-Ue.inset*2,Ue.pageSegments,1),gs.paper);a.geometry.translate(-(Ue.width-Ue.inset)/2,0,0),a.name="book_turning_page";const c=new wf(new Gt,new As({color:gs.rule}));return c.frustumCulled=!1,a.add(c),a.userData.edge=c,e.add(a),e.userData={hinges:n,covers:s,pages:r,grips:o,leaf:a},e}function B1(i,e){const t=i.l.clone(),n=i.r.clone(),s=t.clone().sub(n).normalize(),r=new v(0,1,0).addScaledVector(s,-s.y).normalize(),o=s.clone().cross(r).normalize(),a=new Ae().makeBasis(s,r,o).multiply(Mp(e)),c=t.distanceTo(n)/Ki("l",e).distanceTo(Ki("r",e)),l=Ki("l",e).add(Ki("r",e)).multiplyScalar(.5).applyMatrix4(a).multiplyScalar(c);return a.scale(new v(c,c,c)).setPosition(t.add(n).multiplyScalar(.5).sub(l))}function k1(i,e,t){const n=vp(e);for(const[h,u]of Object.entries(H))i.userData.hinges[h].rotation.y=u*n,i.userData.grips[h].position.copy(Ki(h,e));const s=i.userData.leaf,r=Ue.pages+Ue.leaf;s.position.set(Bt(-Ue.spine/2+r*Math.sin(n),Ue.spine/2-r*Math.sin(n),t),0,-r*Math.cos(n)),s.rotation.y=-n-Qe(Ue.open*e)*t,s.visible=e>0;const o=Ue.curl*Math.sin(Math.PI*t),a=Ue.width-Ue.inset,c=s.geometry.attributes.position;for(let h=0;h<2;h++)for(let u=0;u<=Ue.pageSegments;u++){const d=1-u/Ue.pageSegments,f=h*(Ue.pageSegments+1)+u,m=Ue.pageBow*Math.sin(Math.PI*t)*d*d;c.setX(f,(o?-a*Math.sin(o*d)/o:-a*d)-Math.sin(s.rotation.y)*m),c.setZ(f,(o?a*(1-Math.cos(o*d))/o:0)+Math.cos(s.rotation.y)*m)}c.needsUpdate=!0;const l=[];for(let h=0;h<=Ue.pageSegments;h++)l.push(new v().fromBufferAttribute(c,h));for(let h=Ue.pageSegments;h>=0;h--)l.push(new v().fromBufferAttribute(c,Ue.pageSegments+1+h));s.userData.edge.geometry.setFromPoints(l)}const z1=1.95,H1=.3;function G1(i){const e=a=>new v().setFromMatrixPosition(i.get(a)),t=e("thigh_l").add(e("thigh_r")).multiplyScalar(.5),n=e("shin_l").add(e("shin_r")).multiplyScalar(.5),s=n.clone().sub(t).setY(0).normalize(),r=new v(0,1,0),o=t.lerp(n,z1).addScaledVector(r,H1);return new Ae().makeBasis(r.clone().cross(s),r,s).setPosition(o)}function V1(i,e){return Object.fromEntries(Object.keys(H).map(t=>[t,i.grip(t,[0,0,0]).applyMatrix4(e.get(`hand_${t}`)).applyMatrix4(Tr)]))}function W1(i,e,t,n){var d;const s=e.moves(t),r=n?EM(i.rig,n.from,s,n.k,n.previous):{moves:s,settled:!0};n&&(n.settled=r.settled);const o=r.moves,a=new Map;for(const f of i.rig.bones){const m=Tr.clone().multiply(o.get(f.name)).multiply(ja).multiply(i.rig.rest.get(f.name));a.set(f.name,m),(f.parent.isBone?a.get(f.parent.name):f.parent.matrixWorld).clone().invert().multiply(m).decompose(f.position,f.quaternion,f.scale)}i.laptop.visible=e.laptop,i.book.visible=!!((d=e.book)!=null&&d.visible),i.book.visible&&(k1(i.book,e.book.open,e.book.page),i.book.matrix.copy(B1(V1(e,o),e.book.open)),i.book.matrixWorldNeedsUpdate=!0);for(const f of i.tablet)f.visible=e.tablet;const c=e.laptop||e.book||e.props.size>0;for(const f of i.stowable)f.visible=!e.stowed.has(f.userData.item);for(const f of i.inHand)f.visible=!e.stowed.has(f.userData.item)&&(!c||e.keep.has(f.userData.item));O1(i,e,o),U1(i,e),e.laptop&&(i.laptop.matrix.copy(G1(a)),i.laptop.matrixWorldNeedsUpdate=!0);const l=e.screen??eT,h=e.eyeShape&&{...e.eyeShape,colour:J1(e.screen)},u=kp({eyed:l.eyes>Q1,eyes:e.eyes,glance:e.eyeGlance,tint:e.eyeTint,hearts:e.hearts,stars:e.stars,squeezed:e.squeezed,dozing:e.dozing,whoa:e.whoa,sign:h,ticker:e.ticker});for(const f of i.screens)f.uniforms.lit.value=l.glow,f.uniforms.across.value=l.across,f.uniforms.open.value=l.open,f.uniforms.flash.value=l.flash,e.screen&&f.uniforms.glow.value.set(...e.screen.colour),YE(f,u,Math.floor(performance.now()*(e.ticker?zp.fps:Hp)/1e3));for(const f of i.visorHulls)f.visible=!e.screen||!!e.screen.sign;return o}const X1=(i,e)=>i==="walk"?0:e,zd=.8,Hd={into:.35,out:.45},bp=({seconds:i,lasts:e})=>me(i,[0,Hd.into])*(1-me(i,[e-Hd.out,e]));function q1(i){const e=i%zd/zd;return 1+.28*Ge(e,0,.3)+.14*Ge(e,.3,.55)}function j1(i){Ke(i,"startled"),i.whoa=!0}function $1(i,{mood:e,seconds:t,lasts:n}){const s=bp({seconds:t,lasts:n});Kf[e].hearts?i.heartEyes(s*q1(t)):Ke(i,e,s)}const Gd={share:.8,lean:.12},Y1=.55,K1=(i,e)=>i==="sit"&&!e?Y1:0;function Z1(i,e,t){const n=((e+180)%360+360)%360-180,s=Gd.lean*n,r=Ft.clamp(Gd.share*n-s,-Pa,Pa);i.bendAbove("chest",{z:-s*t}),i.turn("neck",{z:-.3*r*t}),i.turn("head",{z:-.7*r*t})}const J1=i=>{const e=i==null?void 0:i.sign;return e?i.colour.map(t=>(t+(1-t)*e.white)*e.lit):[1,1,1]},la="face_screen",Q1=.05,eT={eyes:1,across:0,open:0,flash:0,glow:0},tT=i=>i!=="lounge";class fT{constructor(){const e=Ht/2;this.camera=new Oa(-e,e,e,-e,Vc-vd,Vc+vd),this.camera.position.set(0,Nn,Vc),this.camera.lookAt(0,Nn,0),this.renderer=new ay({antialias:!0,alpha:!0,preserveDrawingBuffer:!0}),this.renderer.setPixelRatio(1),this.renderer.setClearColor(0,0)}headAt(e,t){if(!t)return{x:.5,y:.3};const n=e.rig.eyes.reduce((s,r)=>s.add(r),new v).divideScalar(e.rig.eyes.length);return this.pictured(n.applyMatrix4(t.get("head")))}handAt(e,t){const n=nt(e.stance),s=n==="l"?"r":"l";return t?{...this.gripAt(e,t,n),out:H[n],other:this.gripAt(e,t,s)}:{x:.5+H[n]*.25,y:.6,out:H[n],other:{x:.5-H[n]*.25,y:.6}}}gripAt(e,t,n){const s=new v(H[n]*Pi.grip,Pi.forward,0).add(e.rig.heads.get(`hand_${n}`));return this.pictured(s.applyMatrix4(t.get(`hand_${n}`)))}pictured(e){const t=e.applyMatrix4(Tr).project(this.camera);return{x:(t.x+1)/2,y:(1-t.y)/2}}draw(e,t,n,s,r,{posture:o="stand",eyes:a=null,stride:c=0,blend:l=null,sky:h=null,throws:u=null,leanWay:d=0,walkWay:f=0,at:m=null,target:_=null,open:g=1,screen:p=null,tilt:y=0,ticker:M=null,grabbed:x=!1}={}){var F,O;const E=new Lw(e.rig,o,c);E.ticker=M,E.sky=h,E.throws=u,E.leanWay=d,E.walkWay=f,E.screen=p,E.at=m,E.target=_,E.facing=s,t.legs||(F=Ud[o])==null||F.under(E),t.pose(E,e.stance,n/t.frames),y&&se(E,{tilt:y}),t.legs||(O=Ud[o])==null||O.over(E);const T=!tT(o),P=s+(m&&!T?X1(o,pS(E,m,s)):0);g<1&&E.shutEyes(Math.min(E.eyes,g)),p&&E.shutEyes(Math.min(E.eyes,p.eyes));const C=Math.max(a?bp(a):0,p?Up(p):0,K1(o,m));C&&!E.gaze&&!T&&!Op(t)&&Z1(E,P,C),a&&$1(E,a),m!=null&&m.mood&&Ke(E,m.mood,m.amount),x&&j1(E),p!=null&&p.sign&&E.shapeEyes(p.sign.name,p.sign.strength);const b=W1(e,E,P,l),w=r.width*yi;for(const k of e.screens)k.uniforms.soften.value=yd(r);this.renderer.domElement.width!==w&&this.renderer.setSize(w,w,!1),this.renderer.render(e.scene,this.camera);const L=r.getContext("2d");return L.clearRect(0,0,r.width,r.height),L.imageSmoothingQuality="high",L.filter=`blur(${yd(r)}px)`,L.drawImage(this.renderer.domElement,0,0,r.width,r.height),b}drawBlock(e,t,n,s){this.blockFor!==n&&(this.block=o1(Ht/n)),this.blockFor=n,a1(this.block,e,t);const r=this.propPicture(this.block,new v(0,0,0),n,s);return{canvas:r.canvas,below:r.height-r.at.y}}drawSaucer(e,t,n){this.saucerFor!==t&&(this.saucer=c1(Ht/t)),this.saucerFor=t,l1(this.saucer,e);const s=this.propPicture(this.saucer,this.saucer.middle,t,n);return{canvas:s.canvas,at:s.at}}drawBug(e,t,n){const s=T1(Ht/t,e),r=this.propPicture(s,s.foot,t,n);return{canvas:r.canvas,at:r.at}}drawCanopy(e,t){const n=h1(Ht/e,e),s=this.propPicture(n,n.middle,e,t),r=n.middle.clone().project(this.camera),o=c=>(c+1)/2*e,a=n.ends.map(c=>{const l=c.clone().project(this.camera);return{x:s.at.x+o(l.x)-o(r.x),y:s.at.y-o(l.y)+o(r.y)}});return{canvas:s.canvas,at:s.at,ends:a}}propPicture({scene:e,bounds:t},n,s,r){const o=Math.round(s*r)*yi;this.renderer.domElement.width!==o&&this.renderer.setSize(o,o,!1),this.renderer.render(e,this.camera);const{min:a,max:c}=t,l=[a.x,c.x].flatMap(M=>[a.y,c.y].flatMap(x=>[a.z,c.z].map(E=>new v(M,x,E).project(this.camera)))),h=M=>(M+1)/2*o,u=Math.floor(Math.min(...l.map(M=>h(M.x))))-yi,d=Math.ceil(Math.max(...l.map(M=>h(M.x))))+yi,f=Math.floor(Math.min(...l.map(M=>o-h(M.y))))-yi,m=Math.ceil(Math.max(...l.map(M=>o-h(M.y))))+yi,_=document.createElement("canvas");_.width=Math.round((d-u)/yi),_.height=Math.round((m-f)/yi);const g=_.getContext("2d");g.imageSmoothingQuality="high",g.drawImage(this.renderer.domElement,u,f,d-u,m-f,0,0,_.width,_.height);const p=n.clone().project(this.camera),y=M=>M/yi/r;return{canvas:_,height:y(m-f),at:{x:y(h(p.x)-u),y:y(o-h(p.y)-f)}}}}export{yr as ACTED,z as ACTING,_1 as BIG_MALLET,m1 as BINOCULARS,ca as BINOCULAR_HOLD,Ue as BOOK,Ks as BUG,Kn as CALL,En as CANOPY,dw as CELL,DE as CHUTE_GRIP,uT as CLIPS,Hr as COMPOSED,y1 as CRUCIFIX,ms as CRUCIFIX_HOLD,Nd as DOZE,Gi as EAGERNESS,Kf as EYES,Sd as FIGHT_EYES,ii as GLANCE,ho as GLASS,fs as GLASS_BUBBLE,oT as GROUND,no as HALO_RING,Pi as HAND,Id as HEAD_TIP,Pa as HEAD_TURN,GE as HIDDEN_PARTS,$t as INSPECTING,Yc as LADDER_CLIMB,Zl as LANDING,oa as LEDGE,Ew as LEFT_OUT,Ud as LEGS,ar as LIGHT_BULB,La as LOOK_DEPTH,Hd as LOOK_EASE,cT as LOOK_REACH,Vi as LOUNGE,Ia as MALLET_SWING,w1 as POCKET_WATCH,dn as PONDERING,Lw as Posing,fe as REACTING,I1 as REACTION_PROPS,wp as REPORT_SCROLL,Dt as REST,Rn as RIFLE,Ms as RIFLE_HOLD,tr as RIFLE_PARTS,$s as RUB,ti as RUMMAGE,f1 as RUMMAGE_THINGS,kt as SAUCER,nn as SCREEN,Qc as SCREEN_INSET,ei as SCROLL,sa as SEARCHING,Y1 as SEATED_TOWARD,vn as SHOVE,H as SIDES,Xi as SKY,S1 as SWING,va as SWING_HOLD,fT as Stage,Pt as TELEPHONE,ln as TOOLS,Gd as TOWARD_VIEWER,In as TUMBLE,Fd as TYPING_SECONDS,hn as WAIT,Wr as WATCH_CHECK,un as WORK,ip as WRITING,x1 as bigMalletOf,A1 as binocularsOf,aT as blowsLandAt,X1 as bodyTurnFor,uS as boxSeen,T1 as bugOf,xE as burstKick,h1 as canopyOf,M1 as crucifixOf,hT as eyesAboveOf,i1 as figureOf,Bd as frontOf,u1 as glassOf,dS as glassSeen,v1 as haloOf,lT as headPivotOf,q1 as heartBeat,_S as leanOf,Pd as lensBefore,C1 as lightBulbOf,U1 as lightFromBulb,l1 as lightSaucer,dT as loadFigure,bp as lookStrength,pS as lookToward,Vb as lookedPoint,SE as malletAt,O1 as moveProps,QS as phoneArrival,KE as pixelTexture,b1 as pocketWatchOf,d1 as propsOf,Xf as reachSide,R1 as reportScrollOf,vE as rifleAim,dp as rifleLine,g1 as rifleOf,E1 as ropeSwingOf,c1 as saucerOf,YE as screenFrame,WE as screenMaterial,K1 as seatedTurn,$E as setScreenIn,ZE as showPixels,J1 as signColour,$w as supportsClip,L1 as telephoneOf,Z1 as turnToViewer,tT as turnsToViewer};

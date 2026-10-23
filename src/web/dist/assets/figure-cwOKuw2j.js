import{A as ce,p as Te,a as ep,b as tp,h as Il,s as np,g as ip,P as Qi,L as sp,c as rp,V as op}from"./main-Bq6pd9pC.js";import{e as Lc}from"./tokens-DQuY9per.js";import"./tip-CqTMCEIB.js";import"./preload-helper-Dp1pzeXC.js";/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const Dl="170",ap=0,yu=1,cp=2,vf=1,lp=2,di=3,vi=0,fn=1,Mn=2,Vi=0,Ws=1,Mu=2,Su=3,bu=4,up=5,fs=100,hp=101,fp=102,dp=103,pp=104,mp=200,gp=201,_p=202,xp=203,Ic=204,Dc=205,vp=206,yp=207,Mp=208,Sp=209,bp=210,wp=211,Ep=212,Tp=213,Ap=214,Nc=0,Uc=1,Oc=2,Ks=3,Fc=4,Bc=5,kc=6,zc=7,yf=0,Rp=1,Cp=2,Gi=0,Pp=1,Lp=2,Ip=3,Dp=4,Np=5,Up=6,Op=7,wu="attached",Fp="detached",Mf=300,Zs=301,Js=302,Hc=303,Vc=304,ha=306,Qs=1e3,Fi=1001,ta=1002,dn=1003,Sf=1004,Ir=1005,Sn=1006,qo=1007,gi=1008,yi=1009,bf=1010,wf=1011,Hr=1012,Nl=1013,ms=1014,Xn=1015,$r=1016,Ul=1017,Ol=1018,er=1020,Ef=35902,Tf=1021,Af=1022,In=1023,Rf=1024,Cf=1025,Xs=1026,tr=1027,Fl=1028,Bl=1029,Pf=1030,kl=1031,zl=1033,Yo=33776,jo=33777,$o=33778,Ko=33779,Gc=35840,Wc=35841,Xc=35842,qc=35843,Yc=36196,jc=37492,$c=37496,Kc=37808,Zc=37809,Jc=37810,Qc=37811,el=37812,tl=37813,nl=37814,il=37815,sl=37816,rl=37817,ol=37818,al=37819,cl=37820,ll=37821,Zo=36492,ul=36494,hl=36495,Lf=36283,fl=36284,dl=36285,pl=36286,Vr=2300,Gr=2301,Aa=2302,Eu=2400,Tu=2401,Au=2402,Bp=2500,kp=0,If=1,ml=2,zp=3200,Hp=3201,Df=0,Vp=1,Ui="",Ht="srgb",an="srgb-linear",fa="linear",St="srgb",bs=7680,Ru=519,Gp=512,Wp=513,Xp=514,Nf=515,qp=516,Yp=517,jp=518,$p=519,gl=35044,Cu="300 es",_i=2e3,na=2001;class cr{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,o=s.length;r<o;r++)s[r].call(this,e);e.target=null}}}const Qt=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let Pu=1234567;const qs=Math.PI/180,nr=180/Math.PI;function Nn(){const i=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(Qt[i&255]+Qt[i>>8&255]+Qt[i>>16&255]+Qt[i>>24&255]+"-"+Qt[e&255]+Qt[e>>8&255]+"-"+Qt[e>>16&15|64]+Qt[e>>24&255]+"-"+Qt[t&63|128]+Qt[t>>8&255]+"-"+Qt[t>>16&255]+Qt[t>>24&255]+Qt[n&255]+Qt[n>>8&255]+Qt[n>>16&255]+Qt[n>>24&255]).toLowerCase()}function Wt(i,e,t){return Math.max(e,Math.min(t,i))}function Hl(i,e){return(i%e+e)%e}function Kp(i,e,t,n,s){return n+(i-e)*(s-n)/(t-e)}function Zp(i,e,t){return i!==e?(t-i)/(e-i):0}function Or(i,e,t){return(1-t)*i+t*e}function Jp(i,e,t,n){return Or(i,e,1-Math.exp(-t*n))}function Qp(i,e=1){return e-Math.abs(Hl(i,e*2)-e)}function em(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*(3-2*i))}function tm(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*i*(i*(i*6-15)+10))}function nm(i,e){return i+Math.floor(Math.random()*(e-i+1))}function im(i,e){return i+Math.random()*(e-i)}function sm(i){return i*(.5-Math.random())}function rm(i){i!==void 0&&(Pu=i);let e=Pu+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function om(i){return i*qs}function am(i){return i*nr}function cm(i){return(i&i-1)===0&&i!==0}function lm(i){return Math.pow(2,Math.ceil(Math.log(i)/Math.LN2))}function um(i){return Math.pow(2,Math.floor(Math.log(i)/Math.LN2))}function hm(i,e,t,n,s){const r=Math.cos,o=Math.sin,a=r(t/2),c=o(t/2),l=r((e+n)/2),u=o((e+n)/2),h=r((e-n)/2),f=o((e-n)/2),d=r((n-e)/2),g=o((n-e)/2);switch(s){case"XYX":i.set(a*u,c*h,c*f,a*l);break;case"YZY":i.set(c*f,a*u,c*h,a*l);break;case"ZXZ":i.set(c*h,c*f,a*u,a*l);break;case"XZX":i.set(a*u,c*g,c*d,a*l);break;case"YXY":i.set(c*d,a*u,c*g,a*l);break;case"ZYZ":i.set(c*g,c*d,a*u,a*l);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+s)}}function Wn(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function vt(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const Dn={DEG2RAD:qs,RAD2DEG:nr,generateUUID:Nn,clamp:Wt,euclideanModulo:Hl,mapLinear:Kp,inverseLerp:Zp,lerp:Or,damp:Jp,pingpong:Qp,smoothstep:em,smootherstep:tm,randInt:nm,randFloat:im,randFloatSpread:sm,seededRandom:rm,degToRad:om,radToDeg:am,isPowerOfTwo:cm,ceilPowerOfTwo:lm,floorPowerOfTwo:um,setQuaternionFromProperEuler:hm,normalize:vt,denormalize:Wn};class te{constructor(e=0,t=0){te.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6],this.y=s[1]*t+s[4]*n+s[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Wt(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),s=Math.sin(t),r=this.x-e.x,o=this.y-e.y;return this.x=r*n-o*s+e.x,this.y=r*s+o*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class tt{constructor(e,t,n,s,r,o,a,c,l){tt.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,o,a,c,l)}set(e,t,n,s,r,o,a,c,l){const u=this.elements;return u[0]=e,u[1]=s,u[2]=a,u[3]=t,u[4]=r,u[5]=c,u[6]=n,u[7]=o,u[8]=l,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,o=n[0],a=n[3],c=n[6],l=n[1],u=n[4],h=n[7],f=n[2],d=n[5],g=n[8],_=s[0],p=s[3],m=s[6],v=s[1],y=s[4],x=s[7],P=s[2],A=s[5],E=s[8];return r[0]=o*_+a*v+c*P,r[3]=o*p+a*y+c*A,r[6]=o*m+a*x+c*E,r[1]=l*_+u*v+h*P,r[4]=l*p+u*y+h*A,r[7]=l*m+u*x+h*E,r[2]=f*_+d*v+g*P,r[5]=f*p+d*y+g*A,r[8]=f*m+d*x+g*E,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],c=e[6],l=e[7],u=e[8];return t*o*u-t*a*l-n*r*u+n*a*c+s*r*l-s*o*c}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],c=e[6],l=e[7],u=e[8],h=u*o-a*l,f=a*c-u*r,d=l*r-o*c,g=t*h+n*f+s*d;if(g===0)return this.set(0,0,0,0,0,0,0,0,0);const _=1/g;return e[0]=h*_,e[1]=(s*l-u*n)*_,e[2]=(a*n-s*o)*_,e[3]=f*_,e[4]=(u*t-s*c)*_,e[5]=(s*r-a*t)*_,e[6]=d*_,e[7]=(n*c-l*t)*_,e[8]=(o*t-n*r)*_,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,s,r,o,a){const c=Math.cos(r),l=Math.sin(r);return this.set(n*c,n*l,-n*(c*o+l*a)+o+e,-s*l,s*c,-s*(-l*o+c*a)+a+t,0,0,1),this}scale(e,t){return this.premultiply(Ra.makeScale(e,t)),this}rotate(e){return this.premultiply(Ra.makeRotation(-e)),this}translate(e,t){return this.premultiply(Ra.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<9;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Ra=new tt;function Uf(i){for(let e=i.length-1;e>=0;--e)if(i[e]>=65535)return!0;return!1}function Wr(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function fm(){const i=Wr("canvas");return i.style.display="block",i}const Lu={};function Dr(i){i in Lu||(Lu[i]=!0,console.warn(i))}function dm(i,e,t){return new Promise(function(n,s){function r(){switch(i.clientWaitSync(e,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:s();break;case i.TIMEOUT_EXPIRED:setTimeout(r,t);break;default:n()}}setTimeout(r,t)})}function pm(i){const e=i.elements;e[2]=.5*e[2]+.5*e[3],e[6]=.5*e[6]+.5*e[7],e[10]=.5*e[10]+.5*e[11],e[14]=.5*e[14]+.5*e[15]}function mm(i){const e=i.elements;e[11]===-1?(e[10]=-e[10]-1,e[14]=-e[14]):(e[10]=-e[10],e[14]=-e[14]+1)}const at={enabled:!0,workingColorSpace:an,spaces:{},convert:function(i,e,t){return this.enabled===!1||e===t||!e||!t||(this.spaces[e].transfer===St&&(i.r=xi(i.r),i.g=xi(i.g),i.b=xi(i.b)),this.spaces[e].primaries!==this.spaces[t].primaries&&(i.applyMatrix3(this.spaces[e].toXYZ),i.applyMatrix3(this.spaces[t].fromXYZ)),this.spaces[t].transfer===St&&(i.r=Ys(i.r),i.g=Ys(i.g),i.b=Ys(i.b))),i},fromWorkingColorSpace:function(i,e){return this.convert(i,this.workingColorSpace,e)},toWorkingColorSpace:function(i,e){return this.convert(i,e,this.workingColorSpace)},getPrimaries:function(i){return this.spaces[i].primaries},getTransfer:function(i){return i===Ui?fa:this.spaces[i].transfer},getLuminanceCoefficients:function(i,e=this.workingColorSpace){return i.fromArray(this.spaces[e].luminanceCoefficients)},define:function(i){Object.assign(this.spaces,i)},_getMatrix:function(i,e,t){return i.copy(this.spaces[e].toXYZ).multiply(this.spaces[t].fromXYZ)},_getDrawingBufferColorSpace:function(i){return this.spaces[i].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(i=this.workingColorSpace){return this.spaces[i].workingColorSpaceConfig.unpackColorSpace}};function xi(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function Ys(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}const Iu=[.64,.33,.3,.6,.15,.06],Du=[.2126,.7152,.0722],Nu=[.3127,.329],Uu=new tt().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),Ou=new tt().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);at.define({[an]:{primaries:Iu,whitePoint:Nu,transfer:fa,toXYZ:Uu,fromXYZ:Ou,luminanceCoefficients:Du,workingColorSpaceConfig:{unpackColorSpace:Ht},outputColorSpaceConfig:{drawingBufferColorSpace:Ht}},[Ht]:{primaries:Iu,whitePoint:Nu,transfer:St,toXYZ:Uu,fromXYZ:Ou,luminanceCoefficients:Du,outputColorSpaceConfig:{drawingBufferColorSpace:Ht}}});let ws;class gm{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{ws===void 0&&(ws=Wr("canvas")),ws.width=e.width,ws.height=e.height;const n=ws.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=ws}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=Wr("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const s=n.getImageData(0,0,e.width,e.height),r=s.data;for(let o=0;o<r.length;o++)r[o]=xi(r[o]/255)*255;return n.putImageData(s,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(xi(t[n]/255)*255):t[n]=xi(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let _m=0;class Of{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:_m++}),this.uuid=Nn(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},s=this.data;if(s!==null){let r;if(Array.isArray(s)){r=[];for(let o=0,a=s.length;o<a;o++)s[o].isDataTexture?r.push(Ca(s[o].image)):r.push(Ca(s[o]))}else r=Ca(s);n.url=r}return t||(e.images[this.uuid]=n),n}}function Ca(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?gm.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let xm=0;class jt extends cr{constructor(e=jt.DEFAULT_IMAGE,t=jt.DEFAULT_MAPPING,n=Fi,s=Fi,r=Sn,o=gi,a=In,c=yi,l=jt.DEFAULT_ANISOTROPY,u=Ui){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:xm++}),this.uuid=Nn(),this.name="",this.source=new Of(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=s,this.magFilter=r,this.minFilter=o,this.anisotropy=l,this.format=a,this.internalFormat=null,this.type=c,this.offset=new te(0,0),this.repeat=new te(1,1),this.center=new te(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new tt,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=u,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==Mf)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Qs:e.x=e.x-Math.floor(e.x);break;case Fi:e.x=e.x<0?0:1;break;case ta:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Qs:e.y=e.y-Math.floor(e.y);break;case Fi:e.y=e.y<0?0:1;break;case ta:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}jt.DEFAULT_IMAGE=null;jt.DEFAULT_MAPPING=Mf;jt.DEFAULT_ANISOTROPY=1;class dt{constructor(e=0,t=0,n=0,s=1){dt.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=s}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,s){return this.x=e,this.y=t,this.z=n,this.w=s,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=this.w,o=e.elements;return this.x=o[0]*t+o[4]*n+o[8]*s+o[12]*r,this.y=o[1]*t+o[5]*n+o[9]*s+o[13]*r,this.z=o[2]*t+o[6]*n+o[10]*s+o[14]*r,this.w=o[3]*t+o[7]*n+o[11]*s+o[15]*r,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,s,r;const c=e.elements,l=c[0],u=c[4],h=c[8],f=c[1],d=c[5],g=c[9],_=c[2],p=c[6],m=c[10];if(Math.abs(u-f)<.01&&Math.abs(h-_)<.01&&Math.abs(g-p)<.01){if(Math.abs(u+f)<.1&&Math.abs(h+_)<.1&&Math.abs(g+p)<.1&&Math.abs(l+d+m-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const y=(l+1)/2,x=(d+1)/2,P=(m+1)/2,A=(u+f)/4,E=(h+_)/4,R=(g+p)/4;return y>x&&y>P?y<.01?(n=0,s=.707106781,r=.707106781):(n=Math.sqrt(y),s=A/n,r=E/n):x>P?x<.01?(n=.707106781,s=0,r=.707106781):(s=Math.sqrt(x),n=A/s,r=R/s):P<.01?(n=.707106781,s=.707106781,r=0):(r=Math.sqrt(P),n=E/r,s=R/r),this.set(n,s,r,t),this}let v=Math.sqrt((p-g)*(p-g)+(h-_)*(h-_)+(f-u)*(f-u));return Math.abs(v)<.001&&(v=1),this.x=(p-g)/v,this.y=(h-_)/v,this.z=(f-u)/v,this.w=Math.acos((l+d+m-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class vm extends cr{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new dt(0,0,e,t),this.scissorTest=!1,this.viewport=new dt(0,0,e,t);const s={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:Sn,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const r=new jt(s,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);r.flipY=!1,r.generateMipmaps=n.generateMipmaps,r.internalFormat=n.internalFormat,this.textures=[];const o=n.count;for(let a=0;a<o;a++)this.textures[a]=r.clone(),this.textures[a].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let s=0,r=this.textures.length;s<r;s++)this.textures[s].image.width=e,this.textures[s].image.height=t,this.textures[s].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,s=e.textures.length;n<s;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Of(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class gs extends vm{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class Ff extends jt{constructor(e=null,t=1,n=1,s=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=dn,this.minFilter=dn,this.wrapR=Fi,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class ym extends jt{constructor(e=null,t=1,n=1,s=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=dn,this.minFilter=dn,this.wrapR=Fi,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class On{constructor(e=0,t=0,n=0,s=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=s}static slerpFlat(e,t,n,s,r,o,a){let c=n[s+0],l=n[s+1],u=n[s+2],h=n[s+3];const f=r[o+0],d=r[o+1],g=r[o+2],_=r[o+3];if(a===0){e[t+0]=c,e[t+1]=l,e[t+2]=u,e[t+3]=h;return}if(a===1){e[t+0]=f,e[t+1]=d,e[t+2]=g,e[t+3]=_;return}if(h!==_||c!==f||l!==d||u!==g){let p=1-a;const m=c*f+l*d+u*g+h*_,v=m>=0?1:-1,y=1-m*m;if(y>Number.EPSILON){const P=Math.sqrt(y),A=Math.atan2(P,m*v);p=Math.sin(p*A)/P,a=Math.sin(a*A)/P}const x=a*v;if(c=c*p+f*x,l=l*p+d*x,u=u*p+g*x,h=h*p+_*x,p===1-a){const P=1/Math.sqrt(c*c+l*l+u*u+h*h);c*=P,l*=P,u*=P,h*=P}}e[t]=c,e[t+1]=l,e[t+2]=u,e[t+3]=h}static multiplyQuaternionsFlat(e,t,n,s,r,o){const a=n[s],c=n[s+1],l=n[s+2],u=n[s+3],h=r[o],f=r[o+1],d=r[o+2],g=r[o+3];return e[t]=a*g+u*h+c*d-l*f,e[t+1]=c*g+u*f+l*h-a*d,e[t+2]=l*g+u*d+a*f-c*h,e[t+3]=u*g-a*h-c*f-l*d,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,s){return this._x=e,this._y=t,this._z=n,this._w=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,s=e._y,r=e._z,o=e._order,a=Math.cos,c=Math.sin,l=a(n/2),u=a(s/2),h=a(r/2),f=c(n/2),d=c(s/2),g=c(r/2);switch(o){case"XYZ":this._x=f*u*h+l*d*g,this._y=l*d*h-f*u*g,this._z=l*u*g+f*d*h,this._w=l*u*h-f*d*g;break;case"YXZ":this._x=f*u*h+l*d*g,this._y=l*d*h-f*u*g,this._z=l*u*g-f*d*h,this._w=l*u*h+f*d*g;break;case"ZXY":this._x=f*u*h-l*d*g,this._y=l*d*h+f*u*g,this._z=l*u*g+f*d*h,this._w=l*u*h-f*d*g;break;case"ZYX":this._x=f*u*h-l*d*g,this._y=l*d*h+f*u*g,this._z=l*u*g-f*d*h,this._w=l*u*h+f*d*g;break;case"YZX":this._x=f*u*h+l*d*g,this._y=l*d*h+f*u*g,this._z=l*u*g-f*d*h,this._w=l*u*h-f*d*g;break;case"XZY":this._x=f*u*h-l*d*g,this._y=l*d*h-f*u*g,this._z=l*u*g+f*d*h,this._w=l*u*h+f*d*g;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+o)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,s=Math.sin(n);return this._x=e.x*s,this._y=e.y*s,this._z=e.z*s,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],s=t[4],r=t[8],o=t[1],a=t[5],c=t[9],l=t[2],u=t[6],h=t[10],f=n+a+h;if(f>0){const d=.5/Math.sqrt(f+1);this._w=.25/d,this._x=(u-c)*d,this._y=(r-l)*d,this._z=(o-s)*d}else if(n>a&&n>h){const d=2*Math.sqrt(1+n-a-h);this._w=(u-c)/d,this._x=.25*d,this._y=(s+o)/d,this._z=(r+l)/d}else if(a>h){const d=2*Math.sqrt(1+a-n-h);this._w=(r-l)/d,this._x=(s+o)/d,this._y=.25*d,this._z=(c+u)/d}else{const d=2*Math.sqrt(1+h-n-a);this._w=(o-s)/d,this._x=(r+l)/d,this._y=(c+u)/d,this._z=.25*d}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Wt(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const s=Math.min(1,t/n);return this.slerp(e,s),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,s=e._y,r=e._z,o=e._w,a=t._x,c=t._y,l=t._z,u=t._w;return this._x=n*u+o*a+s*l-r*c,this._y=s*u+o*c+r*a-n*l,this._z=r*u+o*l+n*c-s*a,this._w=o*u-n*a-s*c-r*l,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,s=this._y,r=this._z,o=this._w;let a=o*e._w+n*e._x+s*e._y+r*e._z;if(a<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,a=-a):this.copy(e),a>=1)return this._w=o,this._x=n,this._y=s,this._z=r,this;const c=1-a*a;if(c<=Number.EPSILON){const d=1-t;return this._w=d*o+t*this._w,this._x=d*n+t*this._x,this._y=d*s+t*this._y,this._z=d*r+t*this._z,this.normalize(),this}const l=Math.sqrt(c),u=Math.atan2(l,a),h=Math.sin((1-t)*u)/l,f=Math.sin(t*u)/l;return this._w=o*h+this._w*f,this._x=n*h+this._x*f,this._y=s*h+this._y*f,this._z=r*h+this._z*f,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),s=Math.sqrt(1-n),r=Math.sqrt(n);return this.set(s*Math.sin(e),s*Math.cos(e),r*Math.sin(t),r*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class M{constructor(e=0,t=0,n=0){M.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Fu.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Fu.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6]*s,this.y=r[1]*t+r[4]*n+r[7]*s,this.z=r[2]*t+r[5]*n+r[8]*s,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=e.elements,o=1/(r[3]*t+r[7]*n+r[11]*s+r[15]);return this.x=(r[0]*t+r[4]*n+r[8]*s+r[12])*o,this.y=(r[1]*t+r[5]*n+r[9]*s+r[13])*o,this.z=(r[2]*t+r[6]*n+r[10]*s+r[14])*o,this}applyQuaternion(e){const t=this.x,n=this.y,s=this.z,r=e.x,o=e.y,a=e.z,c=e.w,l=2*(o*s-a*n),u=2*(a*t-r*s),h=2*(r*n-o*t);return this.x=t+c*l+o*h-a*u,this.y=n+c*u+a*l-r*h,this.z=s+c*h+r*u-o*l,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[4]*n+r[8]*s,this.y=r[1]*t+r[5]*n+r[9]*s,this.z=r[2]*t+r[6]*n+r[10]*s,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,s=e.y,r=e.z,o=t.x,a=t.y,c=t.z;return this.x=s*c-r*a,this.y=r*o-n*c,this.z=n*a-s*o,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return Pa.copy(this).projectOnVector(e),this.sub(Pa)}reflect(e){return this.sub(Pa.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Wt(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,s=this.z-e.z;return t*t+n*n+s*s}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const s=Math.sin(t)*e;return this.x=s*Math.sin(n),this.y=Math.cos(t)*e,this.z=s*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),s=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=s,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const Pa=new M,Fu=new On;class pn{constructor(e=new M(1/0,1/0,1/0),t=new M(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(zn.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(zn.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=zn.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const r=n.getAttribute("position");if(t===!0&&r!==void 0&&e.isInstancedMesh!==!0)for(let o=0,a=r.count;o<a;o++)e.isMesh===!0?e.getVertexPosition(o,zn):zn.fromBufferAttribute(r,o),zn.applyMatrix4(e.matrixWorld),this.expandByPoint(zn);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),oo.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),oo.copy(n.boundingBox)),oo.applyMatrix4(e.matrixWorld),this.union(oo)}const s=e.children;for(let r=0,o=s.length;r<o;r++)this.expandByObject(s[r],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,zn),zn.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(xr),ao.subVectors(this.max,xr),Es.subVectors(e.a,xr),Ts.subVectors(e.b,xr),As.subVectors(e.c,xr),Ti.subVectors(Ts,Es),Ai.subVectors(As,Ts),es.subVectors(Es,As);let t=[0,-Ti.z,Ti.y,0,-Ai.z,Ai.y,0,-es.z,es.y,Ti.z,0,-Ti.x,Ai.z,0,-Ai.x,es.z,0,-es.x,-Ti.y,Ti.x,0,-Ai.y,Ai.x,0,-es.y,es.x,0];return!La(t,Es,Ts,As,ao)||(t=[1,0,0,0,1,0,0,0,1],!La(t,Es,Ts,As,ao))?!1:(co.crossVectors(Ti,Ai),t=[co.x,co.y,co.z],La(t,Es,Ts,As,ao))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,zn).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(zn).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(oi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),oi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),oi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),oi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),oi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),oi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),oi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),oi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(oi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const oi=[new M,new M,new M,new M,new M,new M,new M,new M],zn=new M,oo=new pn,Es=new M,Ts=new M,As=new M,Ti=new M,Ai=new M,es=new M,xr=new M,ao=new M,co=new M,ts=new M;function La(i,e,t,n,s){for(let r=0,o=i.length-3;r<=o;r+=3){ts.fromArray(i,r);const a=s.x*Math.abs(ts.x)+s.y*Math.abs(ts.y)+s.z*Math.abs(ts.z),c=e.dot(ts),l=t.dot(ts),u=n.dot(ts);if(Math.max(-Math.max(c,l,u),Math.min(c,l,u))>a)return!1}return!0}const Mm=new pn,vr=new M,Ia=new M;class ei{constructor(e=new M,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):Mm.setFromPoints(e).getCenter(n);let s=0;for(let r=0,o=e.length;r<o;r++)s=Math.max(s,n.distanceToSquared(e[r]));return this.radius=Math.sqrt(s),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;vr.subVectors(e,this.center);const t=vr.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),s=(n-this.radius)*.5;this.center.addScaledVector(vr,s/n),this.radius+=s}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(Ia.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(vr.copy(e.center).add(Ia)),this.expandByPoint(vr.copy(e.center).sub(Ia))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const ai=new M,Da=new M,lo=new M,Ri=new M,Na=new M,uo=new M,Ua=new M;class da{constructor(e=new M,t=new M(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,ai)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=ai.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(ai.copy(this.origin).addScaledVector(this.direction,t),ai.distanceToSquared(e))}distanceSqToSegment(e,t,n,s){Da.copy(e).add(t).multiplyScalar(.5),lo.copy(t).sub(e).normalize(),Ri.copy(this.origin).sub(Da);const r=e.distanceTo(t)*.5,o=-this.direction.dot(lo),a=Ri.dot(this.direction),c=-Ri.dot(lo),l=Ri.lengthSq(),u=Math.abs(1-o*o);let h,f,d,g;if(u>0)if(h=o*c-a,f=o*a-c,g=r*u,h>=0)if(f>=-g)if(f<=g){const _=1/u;h*=_,f*=_,d=h*(h+o*f+2*a)+f*(o*h+f+2*c)+l}else f=r,h=Math.max(0,-(o*f+a)),d=-h*h+f*(f+2*c)+l;else f=-r,h=Math.max(0,-(o*f+a)),d=-h*h+f*(f+2*c)+l;else f<=-g?(h=Math.max(0,-(-o*r+a)),f=h>0?-r:Math.min(Math.max(-r,-c),r),d=-h*h+f*(f+2*c)+l):f<=g?(h=0,f=Math.min(Math.max(-r,-c),r),d=f*(f+2*c)+l):(h=Math.max(0,-(o*r+a)),f=h>0?r:Math.min(Math.max(-r,-c),r),d=-h*h+f*(f+2*c)+l);else f=o>0?-r:r,h=Math.max(0,-(o*f+a)),d=-h*h+f*(f+2*c)+l;return n&&n.copy(this.origin).addScaledVector(this.direction,h),s&&s.copy(Da).addScaledVector(lo,f),d}intersectSphere(e,t){ai.subVectors(e.center,this.origin);const n=ai.dot(this.direction),s=ai.dot(ai)-n*n,r=e.radius*e.radius;if(s>r)return null;const o=Math.sqrt(r-s),a=n-o,c=n+o;return c<0?null:a<0?this.at(c,t):this.at(a,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,s,r,o,a,c;const l=1/this.direction.x,u=1/this.direction.y,h=1/this.direction.z,f=this.origin;return l>=0?(n=(e.min.x-f.x)*l,s=(e.max.x-f.x)*l):(n=(e.max.x-f.x)*l,s=(e.min.x-f.x)*l),u>=0?(r=(e.min.y-f.y)*u,o=(e.max.y-f.y)*u):(r=(e.max.y-f.y)*u,o=(e.min.y-f.y)*u),n>o||r>s||((r>n||isNaN(n))&&(n=r),(o<s||isNaN(s))&&(s=o),h>=0?(a=(e.min.z-f.z)*h,c=(e.max.z-f.z)*h):(a=(e.max.z-f.z)*h,c=(e.min.z-f.z)*h),n>c||a>s)||((a>n||n!==n)&&(n=a),(c<s||s!==s)&&(s=c),s<0)?null:this.at(n>=0?n:s,t)}intersectsBox(e){return this.intersectBox(e,ai)!==null}intersectTriangle(e,t,n,s,r){Na.subVectors(t,e),uo.subVectors(n,e),Ua.crossVectors(Na,uo);let o=this.direction.dot(Ua),a;if(o>0){if(s)return null;a=1}else if(o<0)a=-1,o=-o;else return null;Ri.subVectors(this.origin,e);const c=a*this.direction.dot(uo.crossVectors(Ri,uo));if(c<0)return null;const l=a*this.direction.dot(Na.cross(Ri));if(l<0||c+l>o)return null;const u=-a*Ri.dot(Ua);return u<0?null:this.at(u/o,r)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Le{constructor(e,t,n,s,r,o,a,c,l,u,h,f,d,g,_,p){Le.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,o,a,c,l,u,h,f,d,g,_,p)}set(e,t,n,s,r,o,a,c,l,u,h,f,d,g,_,p){const m=this.elements;return m[0]=e,m[4]=t,m[8]=n,m[12]=s,m[1]=r,m[5]=o,m[9]=a,m[13]=c,m[2]=l,m[6]=u,m[10]=h,m[14]=f,m[3]=d,m[7]=g,m[11]=_,m[15]=p,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Le().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,s=1/Rs.setFromMatrixColumn(e,0).length(),r=1/Rs.setFromMatrixColumn(e,1).length(),o=1/Rs.setFromMatrixColumn(e,2).length();return t[0]=n[0]*s,t[1]=n[1]*s,t[2]=n[2]*s,t[3]=0,t[4]=n[4]*r,t[5]=n[5]*r,t[6]=n[6]*r,t[7]=0,t[8]=n[8]*o,t[9]=n[9]*o,t[10]=n[10]*o,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,s=e.y,r=e.z,o=Math.cos(n),a=Math.sin(n),c=Math.cos(s),l=Math.sin(s),u=Math.cos(r),h=Math.sin(r);if(e.order==="XYZ"){const f=o*u,d=o*h,g=a*u,_=a*h;t[0]=c*u,t[4]=-c*h,t[8]=l,t[1]=d+g*l,t[5]=f-_*l,t[9]=-a*c,t[2]=_-f*l,t[6]=g+d*l,t[10]=o*c}else if(e.order==="YXZ"){const f=c*u,d=c*h,g=l*u,_=l*h;t[0]=f+_*a,t[4]=g*a-d,t[8]=o*l,t[1]=o*h,t[5]=o*u,t[9]=-a,t[2]=d*a-g,t[6]=_+f*a,t[10]=o*c}else if(e.order==="ZXY"){const f=c*u,d=c*h,g=l*u,_=l*h;t[0]=f-_*a,t[4]=-o*h,t[8]=g+d*a,t[1]=d+g*a,t[5]=o*u,t[9]=_-f*a,t[2]=-o*l,t[6]=a,t[10]=o*c}else if(e.order==="ZYX"){const f=o*u,d=o*h,g=a*u,_=a*h;t[0]=c*u,t[4]=g*l-d,t[8]=f*l+_,t[1]=c*h,t[5]=_*l+f,t[9]=d*l-g,t[2]=-l,t[6]=a*c,t[10]=o*c}else if(e.order==="YZX"){const f=o*c,d=o*l,g=a*c,_=a*l;t[0]=c*u,t[4]=_-f*h,t[8]=g*h+d,t[1]=h,t[5]=o*u,t[9]=-a*u,t[2]=-l*u,t[6]=d*h+g,t[10]=f-_*h}else if(e.order==="XZY"){const f=o*c,d=o*l,g=a*c,_=a*l;t[0]=c*u,t[4]=-h,t[8]=l*u,t[1]=f*h+_,t[5]=o*u,t[9]=d*h-g,t[2]=g*h-d,t[6]=a*u,t[10]=_*h+f}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(Sm,e,bm)}lookAt(e,t,n){const s=this.elements;return vn.subVectors(e,t),vn.lengthSq()===0&&(vn.z=1),vn.normalize(),Ci.crossVectors(n,vn),Ci.lengthSq()===0&&(Math.abs(n.z)===1?vn.x+=1e-4:vn.z+=1e-4,vn.normalize(),Ci.crossVectors(n,vn)),Ci.normalize(),ho.crossVectors(vn,Ci),s[0]=Ci.x,s[4]=ho.x,s[8]=vn.x,s[1]=Ci.y,s[5]=ho.y,s[9]=vn.y,s[2]=Ci.z,s[6]=ho.z,s[10]=vn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,o=n[0],a=n[4],c=n[8],l=n[12],u=n[1],h=n[5],f=n[9],d=n[13],g=n[2],_=n[6],p=n[10],m=n[14],v=n[3],y=n[7],x=n[11],P=n[15],A=s[0],E=s[4],R=s[8],b=s[12],S=s[1],I=s[5],B=s[9],O=s[13],k=s[2],K=s[6],W=s[10],q=s[14],V=s[3],se=s[7],me=s[11],Se=s[15];return r[0]=o*A+a*S+c*k+l*V,r[4]=o*E+a*I+c*K+l*se,r[8]=o*R+a*B+c*W+l*me,r[12]=o*b+a*O+c*q+l*Se,r[1]=u*A+h*S+f*k+d*V,r[5]=u*E+h*I+f*K+d*se,r[9]=u*R+h*B+f*W+d*me,r[13]=u*b+h*O+f*q+d*Se,r[2]=g*A+_*S+p*k+m*V,r[6]=g*E+_*I+p*K+m*se,r[10]=g*R+_*B+p*W+m*me,r[14]=g*b+_*O+p*q+m*Se,r[3]=v*A+y*S+x*k+P*V,r[7]=v*E+y*I+x*K+P*se,r[11]=v*R+y*B+x*W+P*me,r[15]=v*b+y*O+x*q+P*Se,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],s=e[8],r=e[12],o=e[1],a=e[5],c=e[9],l=e[13],u=e[2],h=e[6],f=e[10],d=e[14],g=e[3],_=e[7],p=e[11],m=e[15];return g*(+r*c*h-s*l*h-r*a*f+n*l*f+s*a*d-n*c*d)+_*(+t*c*d-t*l*f+r*o*f-s*o*d+s*l*u-r*c*u)+p*(+t*l*h-t*a*d-r*o*h+n*o*d+r*a*u-n*l*u)+m*(-s*a*u-t*c*h+t*a*f+s*o*h-n*o*f+n*c*u)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const s=this.elements;return e.isVector3?(s[12]=e.x,s[13]=e.y,s[14]=e.z):(s[12]=e,s[13]=t,s[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],c=e[6],l=e[7],u=e[8],h=e[9],f=e[10],d=e[11],g=e[12],_=e[13],p=e[14],m=e[15],v=h*p*l-_*f*l+_*c*d-a*p*d-h*c*m+a*f*m,y=g*f*l-u*p*l-g*c*d+o*p*d+u*c*m-o*f*m,x=u*_*l-g*h*l+g*a*d-o*_*d-u*a*m+o*h*m,P=g*h*c-u*_*c-g*a*f+o*_*f+u*a*p-o*h*p,A=t*v+n*y+s*x+r*P;if(A===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const E=1/A;return e[0]=v*E,e[1]=(_*f*r-h*p*r-_*s*d+n*p*d+h*s*m-n*f*m)*E,e[2]=(a*p*r-_*c*r+_*s*l-n*p*l-a*s*m+n*c*m)*E,e[3]=(h*c*r-a*f*r-h*s*l+n*f*l+a*s*d-n*c*d)*E,e[4]=y*E,e[5]=(u*p*r-g*f*r+g*s*d-t*p*d-u*s*m+t*f*m)*E,e[6]=(g*c*r-o*p*r-g*s*l+t*p*l+o*s*m-t*c*m)*E,e[7]=(o*f*r-u*c*r+u*s*l-t*f*l-o*s*d+t*c*d)*E,e[8]=x*E,e[9]=(g*h*r-u*_*r-g*n*d+t*_*d+u*n*m-t*h*m)*E,e[10]=(o*_*r-g*a*r+g*n*l-t*_*l-o*n*m+t*a*m)*E,e[11]=(u*a*r-o*h*r-u*n*l+t*h*l+o*n*d-t*a*d)*E,e[12]=P*E,e[13]=(u*_*s-g*h*s+g*n*f-t*_*f-u*n*p+t*h*p)*E,e[14]=(g*a*s-o*_*s-g*n*c+t*_*c+o*n*p-t*a*p)*E,e[15]=(o*h*s-u*a*s+u*n*c-t*h*c-o*n*f+t*a*f)*E,this}scale(e){const t=this.elements,n=e.x,s=e.y,r=e.z;return t[0]*=n,t[4]*=s,t[8]*=r,t[1]*=n,t[5]*=s,t[9]*=r,t[2]*=n,t[6]*=s,t[10]*=r,t[3]*=n,t[7]*=s,t[11]*=r,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],s=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,s))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),s=Math.sin(t),r=1-n,o=e.x,a=e.y,c=e.z,l=r*o,u=r*a;return this.set(l*o+n,l*a-s*c,l*c+s*a,0,l*a+s*c,u*a+n,u*c-s*o,0,l*c-s*a,u*c+s*o,r*c*c+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,s,r,o){return this.set(1,n,r,0,e,1,o,0,t,s,1,0,0,0,0,1),this}compose(e,t,n){const s=this.elements,r=t._x,o=t._y,a=t._z,c=t._w,l=r+r,u=o+o,h=a+a,f=r*l,d=r*u,g=r*h,_=o*u,p=o*h,m=a*h,v=c*l,y=c*u,x=c*h,P=n.x,A=n.y,E=n.z;return s[0]=(1-(_+m))*P,s[1]=(d+x)*P,s[2]=(g-y)*P,s[3]=0,s[4]=(d-x)*A,s[5]=(1-(f+m))*A,s[6]=(p+v)*A,s[7]=0,s[8]=(g+y)*E,s[9]=(p-v)*E,s[10]=(1-(f+_))*E,s[11]=0,s[12]=e.x,s[13]=e.y,s[14]=e.z,s[15]=1,this}decompose(e,t,n){const s=this.elements;let r=Rs.set(s[0],s[1],s[2]).length();const o=Rs.set(s[4],s[5],s[6]).length(),a=Rs.set(s[8],s[9],s[10]).length();this.determinant()<0&&(r=-r),e.x=s[12],e.y=s[13],e.z=s[14],Hn.copy(this);const l=1/r,u=1/o,h=1/a;return Hn.elements[0]*=l,Hn.elements[1]*=l,Hn.elements[2]*=l,Hn.elements[4]*=u,Hn.elements[5]*=u,Hn.elements[6]*=u,Hn.elements[8]*=h,Hn.elements[9]*=h,Hn.elements[10]*=h,t.setFromRotationMatrix(Hn),n.x=r,n.y=o,n.z=a,this}makePerspective(e,t,n,s,r,o,a=_i){const c=this.elements,l=2*r/(t-e),u=2*r/(n-s),h=(t+e)/(t-e),f=(n+s)/(n-s);let d,g;if(a===_i)d=-(o+r)/(o-r),g=-2*o*r/(o-r);else if(a===na)d=-o/(o-r),g=-o*r/(o-r);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+a);return c[0]=l,c[4]=0,c[8]=h,c[12]=0,c[1]=0,c[5]=u,c[9]=f,c[13]=0,c[2]=0,c[6]=0,c[10]=d,c[14]=g,c[3]=0,c[7]=0,c[11]=-1,c[15]=0,this}makeOrthographic(e,t,n,s,r,o,a=_i){const c=this.elements,l=1/(t-e),u=1/(n-s),h=1/(o-r),f=(t+e)*l,d=(n+s)*u;let g,_;if(a===_i)g=(o+r)*h,_=-2*h;else if(a===na)g=r*h,_=-1*h;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+a);return c[0]=2*l,c[4]=0,c[8]=0,c[12]=-f,c[1]=0,c[5]=2*u,c[9]=0,c[13]=-d,c[2]=0,c[6]=0,c[10]=_,c[14]=-g,c[3]=0,c[7]=0,c[11]=0,c[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<16;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const Rs=new M,Hn=new Le,Sm=new M(0,0,0),bm=new M(1,1,1),Ci=new M,ho=new M,vn=new M,Bu=new Le,ku=new On;class wn{constructor(e=0,t=0,n=0,s=wn.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=s}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,s=this._order){return this._x=e,this._y=t,this._z=n,this._order=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const s=e.elements,r=s[0],o=s[4],a=s[8],c=s[1],l=s[5],u=s[9],h=s[2],f=s[6],d=s[10];switch(t){case"XYZ":this._y=Math.asin(Wt(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(-u,d),this._z=Math.atan2(-o,r)):(this._x=Math.atan2(f,l),this._z=0);break;case"YXZ":this._x=Math.asin(-Wt(u,-1,1)),Math.abs(u)<.9999999?(this._y=Math.atan2(a,d),this._z=Math.atan2(c,l)):(this._y=Math.atan2(-h,r),this._z=0);break;case"ZXY":this._x=Math.asin(Wt(f,-1,1)),Math.abs(f)<.9999999?(this._y=Math.atan2(-h,d),this._z=Math.atan2(-o,l)):(this._y=0,this._z=Math.atan2(c,r));break;case"ZYX":this._y=Math.asin(-Wt(h,-1,1)),Math.abs(h)<.9999999?(this._x=Math.atan2(f,d),this._z=Math.atan2(c,r)):(this._x=0,this._z=Math.atan2(-o,l));break;case"YZX":this._z=Math.asin(Wt(c,-1,1)),Math.abs(c)<.9999999?(this._x=Math.atan2(-u,l),this._y=Math.atan2(-h,r)):(this._x=0,this._y=Math.atan2(a,d));break;case"XZY":this._z=Math.asin(-Wt(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(f,l),this._y=Math.atan2(a,r)):(this._x=Math.atan2(-u,d),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Bu.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Bu,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return ku.setFromEuler(this),this.setFromQuaternion(ku,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}wn.DEFAULT_ORDER="XYZ";class Bf{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let wm=0;const zu=new M,Cs=new On,ci=new Le,fo=new M,yr=new M,Em=new M,Tm=new On,Hu=new M(1,0,0),Vu=new M(0,1,0),Gu=new M(0,0,1),Wu={type:"added"},Am={type:"removed"},Ps={type:"childadded",child:null},Oa={type:"childremoved",child:null};class It extends cr{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:wm++}),this.uuid=Nn(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=It.DEFAULT_UP.clone();const e=new M,t=new wn,n=new On,s=new M(1,1,1);function r(){n.setFromEuler(t,!1)}function o(){t.setFromQuaternion(n,void 0,!1)}t._onChange(r),n._onChange(o),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:s},modelViewMatrix:{value:new Le},normalMatrix:{value:new tt}}),this.matrix=new Le,this.matrixWorld=new Le,this.matrixAutoUpdate=It.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=It.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Bf,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Cs.setFromAxisAngle(e,t),this.quaternion.multiply(Cs),this}rotateOnWorldAxis(e,t){return Cs.setFromAxisAngle(e,t),this.quaternion.premultiply(Cs),this}rotateX(e){return this.rotateOnAxis(Hu,e)}rotateY(e){return this.rotateOnAxis(Vu,e)}rotateZ(e){return this.rotateOnAxis(Gu,e)}translateOnAxis(e,t){return zu.copy(e).applyQuaternion(this.quaternion),this.position.add(zu.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Hu,e)}translateY(e){return this.translateOnAxis(Vu,e)}translateZ(e){return this.translateOnAxis(Gu,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(ci.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?fo.copy(e):fo.set(e,t,n);const s=this.parent;this.updateWorldMatrix(!0,!1),yr.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?ci.lookAt(yr,fo,this.up):ci.lookAt(fo,yr,this.up),this.quaternion.setFromRotationMatrix(ci),s&&(ci.extractRotation(s.matrixWorld),Cs.setFromRotationMatrix(ci),this.quaternion.premultiply(Cs.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(Wu),Ps.child=e,this.dispatchEvent(Ps),Ps.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(Am),Oa.child=e,this.dispatchEvent(Oa),Oa.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),ci.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),ci.multiply(e.parent.matrixWorld)),e.applyMatrix4(ci),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(Wu),Ps.child=e,this.dispatchEvent(Ps),Ps.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,s=this.children.length;n<s;n++){const o=this.children[n].getObjectByProperty(e,t);if(o!==void 0)return o}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const s=this.children;for(let r=0,o=s.length;r<o;r++)s[r].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(yr,e,Em),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(yr,Tm,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const s=this.children;for(let r=0,o=s.length;r<o;r++)s[r].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const s={};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.castShadow===!0&&(s.castShadow=!0),this.receiveShadow===!0&&(s.receiveShadow=!0),this.visible===!1&&(s.visible=!1),this.frustumCulled===!1&&(s.frustumCulled=!1),this.renderOrder!==0&&(s.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(s.userData=this.userData),s.layers=this.layers.mask,s.matrix=this.matrix.toArray(),s.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(s.matrixAutoUpdate=!1),this.isInstancedMesh&&(s.type="InstancedMesh",s.count=this.count,s.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(s.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(s.type="BatchedMesh",s.perObjectFrustumCulled=this.perObjectFrustumCulled,s.sortObjects=this.sortObjects,s.drawRanges=this._drawRanges,s.reservedRanges=this._reservedRanges,s.visibility=this._visibility,s.active=this._active,s.bounds=this._bounds.map(a=>({boxInitialized:a.boxInitialized,boxMin:a.box.min.toArray(),boxMax:a.box.max.toArray(),sphereInitialized:a.sphereInitialized,sphereRadius:a.sphere.radius,sphereCenter:a.sphere.center.toArray()})),s.maxInstanceCount=this._maxInstanceCount,s.maxVertexCount=this._maxVertexCount,s.maxIndexCount=this._maxIndexCount,s.geometryInitialized=this._geometryInitialized,s.geometryCount=this._geometryCount,s.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(s.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(s.boundingSphere={center:s.boundingSphere.center.toArray(),radius:s.boundingSphere.radius}),this.boundingBox!==null&&(s.boundingBox={min:s.boundingBox.min.toArray(),max:s.boundingBox.max.toArray()}));function r(a,c){return a[c.uuid]===void 0&&(a[c.uuid]=c.toJSON(e)),c.uuid}if(this.isScene)this.background&&(this.background.isColor?s.background=this.background.toJSON():this.background.isTexture&&(s.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(s.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){s.geometry=r(e.geometries,this.geometry);const a=this.geometry.parameters;if(a!==void 0&&a.shapes!==void 0){const c=a.shapes;if(Array.isArray(c))for(let l=0,u=c.length;l<u;l++){const h=c[l];r(e.shapes,h)}else r(e.shapes,c)}}if(this.isSkinnedMesh&&(s.bindMode=this.bindMode,s.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(r(e.skeletons,this.skeleton),s.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const a=[];for(let c=0,l=this.material.length;c<l;c++)a.push(r(e.materials,this.material[c]));s.material=a}else s.material=r(e.materials,this.material);if(this.children.length>0){s.children=[];for(let a=0;a<this.children.length;a++)s.children.push(this.children[a].toJSON(e).object)}if(this.animations.length>0){s.animations=[];for(let a=0;a<this.animations.length;a++){const c=this.animations[a];s.animations.push(r(e.animations,c))}}if(t){const a=o(e.geometries),c=o(e.materials),l=o(e.textures),u=o(e.images),h=o(e.shapes),f=o(e.skeletons),d=o(e.animations),g=o(e.nodes);a.length>0&&(n.geometries=a),c.length>0&&(n.materials=c),l.length>0&&(n.textures=l),u.length>0&&(n.images=u),h.length>0&&(n.shapes=h),f.length>0&&(n.skeletons=f),d.length>0&&(n.animations=d),g.length>0&&(n.nodes=g)}return n.object=s,n;function o(a){const c=[];for(const l in a){const u=a[l];delete u.metadata,c.push(u)}return c}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const s=e.children[n];this.add(s.clone())}return this}}It.DEFAULT_UP=new M(0,1,0);It.DEFAULT_MATRIX_AUTO_UPDATE=!0;It.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const Vn=new M,li=new M,Fa=new M,ui=new M,Ls=new M,Is=new M,Xu=new M,Ba=new M,ka=new M,za=new M,Ha=new dt,Va=new dt,Ga=new dt;class Ln{constructor(e=new M,t=new M,n=new M){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,s){s.subVectors(n,t),Vn.subVectors(e,t),s.cross(Vn);const r=s.lengthSq();return r>0?s.multiplyScalar(1/Math.sqrt(r)):s.set(0,0,0)}static getBarycoord(e,t,n,s,r){Vn.subVectors(s,t),li.subVectors(n,t),Fa.subVectors(e,t);const o=Vn.dot(Vn),a=Vn.dot(li),c=Vn.dot(Fa),l=li.dot(li),u=li.dot(Fa),h=o*l-a*a;if(h===0)return r.set(0,0,0),null;const f=1/h,d=(l*c-a*u)*f,g=(o*u-a*c)*f;return r.set(1-d-g,g,d)}static containsPoint(e,t,n,s){return this.getBarycoord(e,t,n,s,ui)===null?!1:ui.x>=0&&ui.y>=0&&ui.x+ui.y<=1}static getInterpolation(e,t,n,s,r,o,a,c){return this.getBarycoord(e,t,n,s,ui)===null?(c.x=0,c.y=0,"z"in c&&(c.z=0),"w"in c&&(c.w=0),null):(c.setScalar(0),c.addScaledVector(r,ui.x),c.addScaledVector(o,ui.y),c.addScaledVector(a,ui.z),c)}static getInterpolatedAttribute(e,t,n,s,r,o){return Ha.setScalar(0),Va.setScalar(0),Ga.setScalar(0),Ha.fromBufferAttribute(e,t),Va.fromBufferAttribute(e,n),Ga.fromBufferAttribute(e,s),o.setScalar(0),o.addScaledVector(Ha,r.x),o.addScaledVector(Va,r.y),o.addScaledVector(Ga,r.z),o}static isFrontFacing(e,t,n,s){return Vn.subVectors(n,t),li.subVectors(e,t),Vn.cross(li).dot(s)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,s){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[s]),this}setFromAttributeAndIndices(e,t,n,s){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,s),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return Vn.subVectors(this.c,this.b),li.subVectors(this.a,this.b),Vn.cross(li).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Ln.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Ln.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,s,r){return Ln.getInterpolation(e,this.a,this.b,this.c,t,n,s,r)}containsPoint(e){return Ln.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Ln.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,s=this.b,r=this.c;let o,a;Ls.subVectors(s,n),Is.subVectors(r,n),Ba.subVectors(e,n);const c=Ls.dot(Ba),l=Is.dot(Ba);if(c<=0&&l<=0)return t.copy(n);ka.subVectors(e,s);const u=Ls.dot(ka),h=Is.dot(ka);if(u>=0&&h<=u)return t.copy(s);const f=c*h-u*l;if(f<=0&&c>=0&&u<=0)return o=c/(c-u),t.copy(n).addScaledVector(Ls,o);za.subVectors(e,r);const d=Ls.dot(za),g=Is.dot(za);if(g>=0&&d<=g)return t.copy(r);const _=d*l-c*g;if(_<=0&&l>=0&&g<=0)return a=l/(l-g),t.copy(n).addScaledVector(Is,a);const p=u*g-d*h;if(p<=0&&h-u>=0&&d-g>=0)return Xu.subVectors(r,s),a=(h-u)/(h-u+(d-g)),t.copy(s).addScaledVector(Xu,a);const m=1/(p+_+f);return o=_*m,a=f*m,t.copy(n).addScaledVector(Ls,o).addScaledVector(Is,a)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const kf={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},Pi={h:0,s:0,l:0},po={h:0,s:0,l:0};function Wa(i,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?i+(e-i)*6*t:t<1/2?e:t<2/3?i+(e-i)*6*(2/3-t):i}class ze{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const s=e;s&&s.isColor?this.copy(s):typeof s=="number"?this.setHex(s):typeof s=="string"&&this.setStyle(s)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=Ht){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,at.toWorkingColorSpace(this,t),this}setRGB(e,t,n,s=at.workingColorSpace){return this.r=e,this.g=t,this.b=n,at.toWorkingColorSpace(this,s),this}setHSL(e,t,n,s=at.workingColorSpace){if(e=Hl(e,1),t=Wt(t,0,1),n=Wt(n,0,1),t===0)this.r=this.g=this.b=n;else{const r=n<=.5?n*(1+t):n+t-n*t,o=2*n-r;this.r=Wa(o,r,e+1/3),this.g=Wa(o,r,e),this.b=Wa(o,r,e-1/3)}return at.toWorkingColorSpace(this,s),this}setStyle(e,t=Ht){function n(r){r!==void 0&&parseFloat(r)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let s;if(s=/^(\w+)\(([^\)]*)\)/.exec(e)){let r;const o=s[1],a=s[2];switch(o){case"rgb":case"rgba":if(r=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setRGB(Math.min(255,parseInt(r[1],10))/255,Math.min(255,parseInt(r[2],10))/255,Math.min(255,parseInt(r[3],10))/255,t);if(r=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setRGB(Math.min(100,parseInt(r[1],10))/100,Math.min(100,parseInt(r[2],10))/100,Math.min(100,parseInt(r[3],10))/100,t);break;case"hsl":case"hsla":if(r=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setHSL(parseFloat(r[1])/360,parseFloat(r[2])/100,parseFloat(r[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(s=/^\#([A-Fa-f\d]+)$/.exec(e)){const r=s[1],o=r.length;if(o===3)return this.setRGB(parseInt(r.charAt(0),16)/15,parseInt(r.charAt(1),16)/15,parseInt(r.charAt(2),16)/15,t);if(o===6)return this.setHex(parseInt(r,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=Ht){const n=kf[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=xi(e.r),this.g=xi(e.g),this.b=xi(e.b),this}copyLinearToSRGB(e){return this.r=Ys(e.r),this.g=Ys(e.g),this.b=Ys(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=Ht){return at.fromWorkingColorSpace(en.copy(this),e),Math.round(Wt(en.r*255,0,255))*65536+Math.round(Wt(en.g*255,0,255))*256+Math.round(Wt(en.b*255,0,255))}getHexString(e=Ht){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=at.workingColorSpace){at.fromWorkingColorSpace(en.copy(this),t);const n=en.r,s=en.g,r=en.b,o=Math.max(n,s,r),a=Math.min(n,s,r);let c,l;const u=(a+o)/2;if(a===o)c=0,l=0;else{const h=o-a;switch(l=u<=.5?h/(o+a):h/(2-o-a),o){case n:c=(s-r)/h+(s<r?6:0);break;case s:c=(r-n)/h+2;break;case r:c=(n-s)/h+4;break}c/=6}return e.h=c,e.s=l,e.l=u,e}getRGB(e,t=at.workingColorSpace){return at.fromWorkingColorSpace(en.copy(this),t),e.r=en.r,e.g=en.g,e.b=en.b,e}getStyle(e=Ht){at.fromWorkingColorSpace(en.copy(this),e);const t=en.r,n=en.g,s=en.b;return e!==Ht?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${s.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(s*255)})`}offsetHSL(e,t,n){return this.getHSL(Pi),this.setHSL(Pi.h+e,Pi.s+t,Pi.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(Pi),e.getHSL(po);const n=Or(Pi.h,po.h,t),s=Or(Pi.s,po.s,t),r=Or(Pi.l,po.l,t);return this.setHSL(n,s,r),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,s=this.b,r=e.elements;return this.r=r[0]*t+r[3]*n+r[6]*s,this.g=r[1]*t+r[4]*n+r[7]*s,this.b=r[2]*t+r[5]*n+r[8]*s,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const en=new ze;ze.NAMES=kf;let Rm=0;class Kn extends cr{static get type(){return"Material"}get type(){return this.constructor.type}set type(e){}constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:Rm++}),this.uuid=Nn(),this.name="",this.blending=Ws,this.side=vi,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=Ic,this.blendDst=Dc,this.blendEquation=fs,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new ze(0,0,0),this.blendAlpha=0,this.depthFunc=Ks,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=Ru,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=bs,this.stencilZFail=bs,this.stencilZPass=bs,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const s=this[t];if(s===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}s&&s.isColor?s.set(n):s&&s.isVector3&&n&&n.isVector3?s.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==Ws&&(n.blending=this.blending),this.side!==vi&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==Ic&&(n.blendSrc=this.blendSrc),this.blendDst!==Dc&&(n.blendDst=this.blendDst),this.blendEquation!==fs&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Ks&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==Ru&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==bs&&(n.stencilFail=this.stencilFail),this.stencilZFail!==bs&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==bs&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function s(r){const o=[];for(const a in r){const c=r[a];delete c.metadata,o.push(c)}return o}if(t){const r=s(e.textures),o=s(e.images);r.length>0&&(n.textures=r),o.length>0&&(n.images=o)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const s=t.length;n=new Array(s);for(let r=0;r!==s;++r)n[r]=t[r].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class on extends Kn{static get type(){return"MeshBasicMaterial"}constructor(e){super(),this.isMeshBasicMaterial=!0,this.color=new ze(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new wn,this.combine=yf,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const Gt=new M,mo=new te;class $t{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=gl,this.updateRanges=[],this.gpuType=Xn,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let s=0,r=this.itemSize;s<r;s++)this.array[e+s]=t.array[n+s];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)mo.fromBufferAttribute(this,t),mo.applyMatrix3(e),this.setXY(t,mo.x,mo.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)Gt.fromBufferAttribute(this,t),Gt.applyMatrix3(e),this.setXYZ(t,Gt.x,Gt.y,Gt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)Gt.fromBufferAttribute(this,t),Gt.applyMatrix4(e),this.setXYZ(t,Gt.x,Gt.y,Gt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Gt.fromBufferAttribute(this,t),Gt.applyNormalMatrix(e),this.setXYZ(t,Gt.x,Gt.y,Gt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Gt.fromBufferAttribute(this,t),Gt.transformDirection(e),this.setXYZ(t,Gt.x,Gt.y,Gt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=Wn(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=vt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=Wn(t,this.array)),t}setX(e,t){return this.normalized&&(t=vt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=Wn(t,this.array)),t}setY(e,t){return this.normalized&&(t=vt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=Wn(t,this.array)),t}setZ(e,t){return this.normalized&&(t=vt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=Wn(t,this.array)),t}setW(e,t){return this.normalized&&(t=vt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=vt(t,this.array),n=vt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,s){return e*=this.itemSize,this.normalized&&(t=vt(t,this.array),n=vt(n,this.array),s=vt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e*=this.itemSize,this.normalized&&(t=vt(t,this.array),n=vt(n,this.array),s=vt(s,this.array),r=vt(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this.array[e+3]=r,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==gl&&(e.usage=this.usage),e}}class Vl extends $t{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class zf extends $t{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class rt extends $t{constructor(e,t,n){super(new Float32Array(e),t,n)}}let Cm=0;const An=new Le,Xa=new It,Ds=new M,yn=new pn,Mr=new pn,Yt=new M;class zt extends cr{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:Cm++}),this.uuid=Nn(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Uf(e)?zf:Vl)(e,1):this.index=e,this}setIndirect(e){return this.indirect=e,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const r=new tt().getNormalMatrix(e);n.applyNormalMatrix(r),n.needsUpdate=!0}const s=this.attributes.tangent;return s!==void 0&&(s.transformDirection(e),s.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return An.makeRotationFromQuaternion(e),this.applyMatrix4(An),this}rotateX(e){return An.makeRotationX(e),this.applyMatrix4(An),this}rotateY(e){return An.makeRotationY(e),this.applyMatrix4(An),this}rotateZ(e){return An.makeRotationZ(e),this.applyMatrix4(An),this}translate(e,t,n){return An.makeTranslation(e,t,n),this.applyMatrix4(An),this}scale(e,t,n){return An.makeScale(e,t,n),this.applyMatrix4(An),this}lookAt(e){return Xa.lookAt(e),Xa.updateMatrix(),this.applyMatrix4(Xa.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Ds).negate(),this.translate(Ds.x,Ds.y,Ds.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const n=[];for(let s=0,r=e.length;s<r;s++){const o=e[s];n.push(o.x,o.y,o.z||0)}this.setAttribute("position",new rt(n,3))}else{for(let n=0,s=t.count;n<s;n++){const r=e[n];t.setXYZ(n,r.x,r.y,r.z||0)}e.length>t.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new pn);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new M(-1/0,-1/0,-1/0),new M(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,s=t.length;n<s;n++){const r=t[n];yn.setFromBufferAttribute(r),this.morphTargetsRelative?(Yt.addVectors(this.boundingBox.min,yn.min),this.boundingBox.expandByPoint(Yt),Yt.addVectors(this.boundingBox.max,yn.max),this.boundingBox.expandByPoint(Yt)):(this.boundingBox.expandByPoint(yn.min),this.boundingBox.expandByPoint(yn.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new ei);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new M,1/0);return}if(e){const n=this.boundingSphere.center;if(yn.setFromBufferAttribute(e),t)for(let r=0,o=t.length;r<o;r++){const a=t[r];Mr.setFromBufferAttribute(a),this.morphTargetsRelative?(Yt.addVectors(yn.min,Mr.min),yn.expandByPoint(Yt),Yt.addVectors(yn.max,Mr.max),yn.expandByPoint(Yt)):(yn.expandByPoint(Mr.min),yn.expandByPoint(Mr.max))}yn.getCenter(n);let s=0;for(let r=0,o=e.count;r<o;r++)Yt.fromBufferAttribute(e,r),s=Math.max(s,n.distanceToSquared(Yt));if(t)for(let r=0,o=t.length;r<o;r++){const a=t[r],c=this.morphTargetsRelative;for(let l=0,u=a.count;l<u;l++)Yt.fromBufferAttribute(a,l),c&&(Ds.fromBufferAttribute(e,l),Yt.add(Ds)),s=Math.max(s,n.distanceToSquared(Yt))}this.boundingSphere.radius=Math.sqrt(s),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,s=t.normal,r=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new $t(new Float32Array(4*n.count),4));const o=this.getAttribute("tangent"),a=[],c=[];for(let R=0;R<n.count;R++)a[R]=new M,c[R]=new M;const l=new M,u=new M,h=new M,f=new te,d=new te,g=new te,_=new M,p=new M;function m(R,b,S){l.fromBufferAttribute(n,R),u.fromBufferAttribute(n,b),h.fromBufferAttribute(n,S),f.fromBufferAttribute(r,R),d.fromBufferAttribute(r,b),g.fromBufferAttribute(r,S),u.sub(l),h.sub(l),d.sub(f),g.sub(f);const I=1/(d.x*g.y-g.x*d.y);isFinite(I)&&(_.copy(u).multiplyScalar(g.y).addScaledVector(h,-d.y).multiplyScalar(I),p.copy(h).multiplyScalar(d.x).addScaledVector(u,-g.x).multiplyScalar(I),a[R].add(_),a[b].add(_),a[S].add(_),c[R].add(p),c[b].add(p),c[S].add(p))}let v=this.groups;v.length===0&&(v=[{start:0,count:e.count}]);for(let R=0,b=v.length;R<b;++R){const S=v[R],I=S.start,B=S.count;for(let O=I,k=I+B;O<k;O+=3)m(e.getX(O+0),e.getX(O+1),e.getX(O+2))}const y=new M,x=new M,P=new M,A=new M;function E(R){P.fromBufferAttribute(s,R),A.copy(P);const b=a[R];y.copy(b),y.sub(P.multiplyScalar(P.dot(b))).normalize(),x.crossVectors(A,b);const I=x.dot(c[R])<0?-1:1;o.setXYZW(R,y.x,y.y,y.z,I)}for(let R=0,b=v.length;R<b;++R){const S=v[R],I=S.start,B=S.count;for(let O=I,k=I+B;O<k;O+=3)E(e.getX(O+0)),E(e.getX(O+1)),E(e.getX(O+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new $t(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let f=0,d=n.count;f<d;f++)n.setXYZ(f,0,0,0);const s=new M,r=new M,o=new M,a=new M,c=new M,l=new M,u=new M,h=new M;if(e)for(let f=0,d=e.count;f<d;f+=3){const g=e.getX(f+0),_=e.getX(f+1),p=e.getX(f+2);s.fromBufferAttribute(t,g),r.fromBufferAttribute(t,_),o.fromBufferAttribute(t,p),u.subVectors(o,r),h.subVectors(s,r),u.cross(h),a.fromBufferAttribute(n,g),c.fromBufferAttribute(n,_),l.fromBufferAttribute(n,p),a.add(u),c.add(u),l.add(u),n.setXYZ(g,a.x,a.y,a.z),n.setXYZ(_,c.x,c.y,c.z),n.setXYZ(p,l.x,l.y,l.z)}else for(let f=0,d=t.count;f<d;f+=3)s.fromBufferAttribute(t,f+0),r.fromBufferAttribute(t,f+1),o.fromBufferAttribute(t,f+2),u.subVectors(o,r),h.subVectors(s,r),u.cross(h),n.setXYZ(f+0,u.x,u.y,u.z),n.setXYZ(f+1,u.x,u.y,u.z),n.setXYZ(f+2,u.x,u.y,u.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)Yt.fromBufferAttribute(e,t),Yt.normalize(),e.setXYZ(t,Yt.x,Yt.y,Yt.z)}toNonIndexed(){function e(a,c){const l=a.array,u=a.itemSize,h=a.normalized,f=new l.constructor(c.length*u);let d=0,g=0;for(let _=0,p=c.length;_<p;_++){a.isInterleavedBufferAttribute?d=c[_]*a.data.stride+a.offset:d=c[_]*u;for(let m=0;m<u;m++)f[g++]=l[d++]}return new $t(f,u,h)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new zt,n=this.index.array,s=this.attributes;for(const a in s){const c=s[a],l=e(c,n);t.setAttribute(a,l)}const r=this.morphAttributes;for(const a in r){const c=[],l=r[a];for(let u=0,h=l.length;u<h;u++){const f=l[u],d=e(f,n);c.push(d)}t.morphAttributes[a]=c}t.morphTargetsRelative=this.morphTargetsRelative;const o=this.groups;for(let a=0,c=o.length;a<c;a++){const l=o[a];t.addGroup(l.start,l.count,l.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const c=this.parameters;for(const l in c)c[l]!==void 0&&(e[l]=c[l]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const c in n){const l=n[c];e.data.attributes[c]=l.toJSON(e.data)}const s={};let r=!1;for(const c in this.morphAttributes){const l=this.morphAttributes[c],u=[];for(let h=0,f=l.length;h<f;h++){const d=l[h];u.push(d.toJSON(e.data))}u.length>0&&(s[c]=u,r=!0)}r&&(e.data.morphAttributes=s,e.data.morphTargetsRelative=this.morphTargetsRelative);const o=this.groups;o.length>0&&(e.data.groups=JSON.parse(JSON.stringify(o)));const a=this.boundingSphere;return a!==null&&(e.data.boundingSphere={center:a.center.toArray(),radius:a.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const s=e.attributes;for(const l in s){const u=s[l];this.setAttribute(l,u.clone(t))}const r=e.morphAttributes;for(const l in r){const u=[],h=r[l];for(let f=0,d=h.length;f<d;f++)u.push(h[f].clone(t));this.morphAttributes[l]=u}this.morphTargetsRelative=e.morphTargetsRelative;const o=e.groups;for(let l=0,u=o.length;l<u;l++){const h=o[l];this.addGroup(h.start,h.count,h.materialIndex)}const a=e.boundingBox;a!==null&&(this.boundingBox=a.clone());const c=e.boundingSphere;return c!==null&&(this.boundingSphere=c.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const qu=new Le,ns=new da,go=new ei,Yu=new M,_o=new M,xo=new M,vo=new M,qa=new M,yo=new M,ju=new M,Mo=new M;class kt extends It{constructor(e=new zt,t=new on){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}getVertexPosition(e,t){const n=this.geometry,s=n.attributes.position,r=n.morphAttributes.position,o=n.morphTargetsRelative;t.fromBufferAttribute(s,e);const a=this.morphTargetInfluences;if(r&&a){yo.set(0,0,0);for(let c=0,l=r.length;c<l;c++){const u=a[c],h=r[c];u!==0&&(qa.fromBufferAttribute(h,e),o?yo.addScaledVector(qa,u):yo.addScaledVector(qa.sub(t),u))}t.add(yo)}return t}raycast(e,t){const n=this.geometry,s=this.material,r=this.matrixWorld;s!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),go.copy(n.boundingSphere),go.applyMatrix4(r),ns.copy(e.ray).recast(e.near),!(go.containsPoint(ns.origin)===!1&&(ns.intersectSphere(go,Yu)===null||ns.origin.distanceToSquared(Yu)>(e.far-e.near)**2))&&(qu.copy(r).invert(),ns.copy(e.ray).applyMatrix4(qu),!(n.boundingBox!==null&&ns.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,ns)))}_computeIntersections(e,t,n){let s;const r=this.geometry,o=this.material,a=r.index,c=r.attributes.position,l=r.attributes.uv,u=r.attributes.uv1,h=r.attributes.normal,f=r.groups,d=r.drawRange;if(a!==null)if(Array.isArray(o))for(let g=0,_=f.length;g<_;g++){const p=f[g],m=o[p.materialIndex],v=Math.max(p.start,d.start),y=Math.min(a.count,Math.min(p.start+p.count,d.start+d.count));for(let x=v,P=y;x<P;x+=3){const A=a.getX(x),E=a.getX(x+1),R=a.getX(x+2);s=So(this,m,e,n,l,u,h,A,E,R),s&&(s.faceIndex=Math.floor(x/3),s.face.materialIndex=p.materialIndex,t.push(s))}}else{const g=Math.max(0,d.start),_=Math.min(a.count,d.start+d.count);for(let p=g,m=_;p<m;p+=3){const v=a.getX(p),y=a.getX(p+1),x=a.getX(p+2);s=So(this,o,e,n,l,u,h,v,y,x),s&&(s.faceIndex=Math.floor(p/3),t.push(s))}}else if(c!==void 0)if(Array.isArray(o))for(let g=0,_=f.length;g<_;g++){const p=f[g],m=o[p.materialIndex],v=Math.max(p.start,d.start),y=Math.min(c.count,Math.min(p.start+p.count,d.start+d.count));for(let x=v,P=y;x<P;x+=3){const A=x,E=x+1,R=x+2;s=So(this,m,e,n,l,u,h,A,E,R),s&&(s.faceIndex=Math.floor(x/3),s.face.materialIndex=p.materialIndex,t.push(s))}}else{const g=Math.max(0,d.start),_=Math.min(c.count,d.start+d.count);for(let p=g,m=_;p<m;p+=3){const v=p,y=p+1,x=p+2;s=So(this,o,e,n,l,u,h,v,y,x),s&&(s.faceIndex=Math.floor(p/3),t.push(s))}}}}function Pm(i,e,t,n,s,r,o,a){let c;if(e.side===fn?c=n.intersectTriangle(o,r,s,!0,a):c=n.intersectTriangle(s,r,o,e.side===vi,a),c===null)return null;Mo.copy(a),Mo.applyMatrix4(i.matrixWorld);const l=t.ray.origin.distanceTo(Mo);return l<t.near||l>t.far?null:{distance:l,point:Mo.clone(),object:i}}function So(i,e,t,n,s,r,o,a,c,l){i.getVertexPosition(a,_o),i.getVertexPosition(c,xo),i.getVertexPosition(l,vo);const u=Pm(i,e,t,n,_o,xo,vo,ju);if(u){const h=new M;Ln.getBarycoord(ju,_o,xo,vo,h),s&&(u.uv=Ln.getInterpolatedAttribute(s,a,c,l,h,new te)),r&&(u.uv1=Ln.getInterpolatedAttribute(r,a,c,l,h,new te)),o&&(u.normal=Ln.getInterpolatedAttribute(o,a,c,l,h,new M),u.normal.dot(n.direction)>0&&u.normal.multiplyScalar(-1));const f={a,b:c,c:l,normal:new M,materialIndex:0};Ln.getNormal(_o,xo,vo,f.normal),u.face=f,u.barycoord=h}return u}class Ct extends zt{constructor(e=1,t=1,n=1,s=1,r=1,o=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:s,heightSegments:r,depthSegments:o};const a=this;s=Math.floor(s),r=Math.floor(r),o=Math.floor(o);const c=[],l=[],u=[],h=[];let f=0,d=0;g("z","y","x",-1,-1,n,t,e,o,r,0),g("z","y","x",1,-1,n,t,-e,o,r,1),g("x","z","y",1,1,e,n,t,s,o,2),g("x","z","y",1,-1,e,n,-t,s,o,3),g("x","y","z",1,-1,e,t,n,s,r,4),g("x","y","z",-1,-1,e,t,-n,s,r,5),this.setIndex(c),this.setAttribute("position",new rt(l,3)),this.setAttribute("normal",new rt(u,3)),this.setAttribute("uv",new rt(h,2));function g(_,p,m,v,y,x,P,A,E,R,b){const S=x/E,I=P/R,B=x/2,O=P/2,k=A/2,K=E+1,W=R+1;let q=0,V=0;const se=new M;for(let me=0;me<W;me++){const Se=me*I-O;for(let Ze=0;Ze<K;Ze++){const pt=Ze*S-B;se[_]=pt*v,se[p]=Se*y,se[m]=k,l.push(se.x,se.y,se.z),se[_]=0,se[p]=0,se[m]=A>0?1:-1,u.push(se.x,se.y,se.z),h.push(Ze/E),h.push(1-me/R),q+=1}}for(let me=0;me<R;me++)for(let Se=0;Se<E;Se++){const Ze=f+Se+K*me,pt=f+Se+K*(me+1),Z=f+(Se+1)+K*(me+1),le=f+(Se+1)+K*me;c.push(Ze,pt,le),c.push(pt,Z,le),V+=6}a.addGroup(d,V,b),d+=V,f+=q}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ct(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function ir(i){const e={};for(const t in i){e[t]={};for(const n in i[t]){const s=i[t][n];s&&(s.isColor||s.isMatrix3||s.isMatrix4||s.isVector2||s.isVector3||s.isVector4||s.isTexture||s.isQuaternion)?s.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=s.clone():Array.isArray(s)?e[t][n]=s.slice():e[t][n]=s}}return e}function ln(i){const e={};for(let t=0;t<i.length;t++){const n=ir(i[t]);for(const s in n)e[s]=n[s]}return e}function Lm(i){const e=[];for(let t=0;t<i.length;t++)e.push(i[t].clone());return e}function Hf(i){const e=i.getRenderTarget();return e===null?i.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:at.workingColorSpace}const Im={clone:ir,merge:ln};var Dm=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,Nm=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Zn extends Kn{static get type(){return"ShaderMaterial"}constructor(e){super(),this.isShaderMaterial=!0,this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=Dm,this.fragmentShader=Nm,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=ir(e.uniforms),this.uniformsGroups=Lm(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const s in this.uniforms){const o=this.uniforms[s].value;o&&o.isTexture?t.uniforms[s]={type:"t",value:o.toJSON(e).uuid}:o&&o.isColor?t.uniforms[s]={type:"c",value:o.getHex()}:o&&o.isVector2?t.uniforms[s]={type:"v2",value:o.toArray()}:o&&o.isVector3?t.uniforms[s]={type:"v3",value:o.toArray()}:o&&o.isVector4?t.uniforms[s]={type:"v4",value:o.toArray()}:o&&o.isMatrix3?t.uniforms[s]={type:"m3",value:o.toArray()}:o&&o.isMatrix4?t.uniforms[s]={type:"m4",value:o.toArray()}:t.uniforms[s]={value:o}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const s in this.extensions)this.extensions[s]===!0&&(n[s]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class Vf extends It{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Le,this.projectionMatrix=new Le,this.projectionMatrixInverse=new Le,this.coordinateSystem=_i}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const Li=new M,$u=new te,Ku=new te;class _n extends Vf{constructor(e=50,t=1,n=.1,s=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=s,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=nr*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(qs*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return nr*2*Math.atan(Math.tan(qs*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){Li.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(Li.x,Li.y).multiplyScalar(-e/Li.z),Li.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(Li.x,Li.y).multiplyScalar(-e/Li.z)}getViewSize(e,t){return this.getViewBounds(e,$u,Ku),t.subVectors(Ku,$u)}setViewOffset(e,t,n,s,r,o){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(qs*.5*this.fov)/this.zoom,n=2*t,s=this.aspect*n,r=-.5*s;const o=this.view;if(this.view!==null&&this.view.enabled){const c=o.fullWidth,l=o.fullHeight;r+=o.offsetX*s/c,t-=o.offsetY*n/l,s*=o.width/c,n*=o.height/l}const a=this.filmOffset;a!==0&&(r+=e*a/this.getFilmWidth()),this.projectionMatrix.makePerspective(r,r+s,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Ns=-90,Us=1;class Um extends It{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const s=new _n(Ns,Us,e,t);s.layers=this.layers,this.add(s);const r=new _n(Ns,Us,e,t);r.layers=this.layers,this.add(r);const o=new _n(Ns,Us,e,t);o.layers=this.layers,this.add(o);const a=new _n(Ns,Us,e,t);a.layers=this.layers,this.add(a);const c=new _n(Ns,Us,e,t);c.layers=this.layers,this.add(c);const l=new _n(Ns,Us,e,t);l.layers=this.layers,this.add(l)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,s,r,o,a,c]=t;for(const l of t)this.remove(l);if(e===_i)n.up.set(0,1,0),n.lookAt(1,0,0),s.up.set(0,1,0),s.lookAt(-1,0,0),r.up.set(0,0,-1),r.lookAt(0,1,0),o.up.set(0,0,1),o.lookAt(0,-1,0),a.up.set(0,1,0),a.lookAt(0,0,1),c.up.set(0,1,0),c.lookAt(0,0,-1);else if(e===na)n.up.set(0,-1,0),n.lookAt(-1,0,0),s.up.set(0,-1,0),s.lookAt(1,0,0),r.up.set(0,0,1),r.lookAt(0,1,0),o.up.set(0,0,-1),o.lookAt(0,-1,0),a.up.set(0,-1,0),a.lookAt(0,0,1),c.up.set(0,-1,0),c.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const l of t)this.add(l),l.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:s}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[r,o,a,c,l,u]=this.children,h=e.getRenderTarget(),f=e.getActiveCubeFace(),d=e.getActiveMipmapLevel(),g=e.xr.enabled;e.xr.enabled=!1;const _=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,s),e.render(t,r),e.setRenderTarget(n,1,s),e.render(t,o),e.setRenderTarget(n,2,s),e.render(t,a),e.setRenderTarget(n,3,s),e.render(t,c),e.setRenderTarget(n,4,s),e.render(t,l),n.texture.generateMipmaps=_,e.setRenderTarget(n,5,s),e.render(t,u),e.setRenderTarget(h,f,d),e.xr.enabled=g,n.texture.needsPMREMUpdate=!0}}class Gf extends jt{constructor(e,t,n,s,r,o,a,c,l,u){e=e!==void 0?e:[],t=t!==void 0?t:Zs,super(e,t,n,s,r,o,a,c,l,u),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class Om extends gs{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},s=[n,n,n,n,n,n];this.texture=new Gf(s,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:Sn}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},s=new Ct(5,5,5),r=new Zn({name:"CubemapFromEquirect",uniforms:ir(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:fn,blending:Vi});r.uniforms.tEquirect.value=t;const o=new kt(s,r),a=t.minFilter;return t.minFilter===gi&&(t.minFilter=Sn),new Um(1,10,this).update(e,o),t.minFilter=a,o.geometry.dispose(),o.material.dispose(),this}clear(e,t,n,s){const r=e.getRenderTarget();for(let o=0;o<6;o++)e.setRenderTarget(this,o),e.clear(t,n,s);e.setRenderTarget(r)}}const Ya=new M,Fm=new M,Bm=new tt;class us{constructor(e=new M(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,s){return this.normal.set(e,t,n),this.constant=s,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const s=Ya.subVectors(n,t).cross(Fm.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(s,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(Ya),s=this.normal.dot(n);if(s===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const r=-(e.start.dot(this.normal)+this.constant)/s;return r<0||r>1?null:t.copy(e.start).addScaledVector(n,r)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||Bm.getNormalMatrix(e),s=this.coplanarPoint(Ya).applyMatrix4(e),r=this.normal.applyMatrix3(n).normalize();return this.constant=-s.dot(r),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const is=new ei,bo=new M;class Gl{constructor(e=new us,t=new us,n=new us,s=new us,r=new us,o=new us){this.planes=[e,t,n,s,r,o]}set(e,t,n,s,r,o){const a=this.planes;return a[0].copy(e),a[1].copy(t),a[2].copy(n),a[3].copy(s),a[4].copy(r),a[5].copy(o),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=_i){const n=this.planes,s=e.elements,r=s[0],o=s[1],a=s[2],c=s[3],l=s[4],u=s[5],h=s[6],f=s[7],d=s[8],g=s[9],_=s[10],p=s[11],m=s[12],v=s[13],y=s[14],x=s[15];if(n[0].setComponents(c-r,f-l,p-d,x-m).normalize(),n[1].setComponents(c+r,f+l,p+d,x+m).normalize(),n[2].setComponents(c+o,f+u,p+g,x+v).normalize(),n[3].setComponents(c-o,f-u,p-g,x-v).normalize(),n[4].setComponents(c-a,f-h,p-_,x-y).normalize(),t===_i)n[5].setComponents(c+a,f+h,p+_,x+y).normalize();else if(t===na)n[5].setComponents(a,h,_,y).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),is.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),is.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(is)}intersectsSprite(e){return is.center.set(0,0,0),is.radius=.7071067811865476,is.applyMatrix4(e.matrixWorld),this.intersectsSphere(is)}intersectsSphere(e){const t=this.planes,n=e.center,s=-e.radius;for(let r=0;r<6;r++)if(t[r].distanceToPoint(n)<s)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const s=t[n];if(bo.x=s.normal.x>0?e.max.x:e.min.x,bo.y=s.normal.y>0?e.max.y:e.min.y,bo.z=s.normal.z>0?e.max.z:e.min.z,s.distanceToPoint(bo)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Wf(){let i=null,e=!1,t=null,n=null;function s(r,o){t(r,o),n=i.requestAnimationFrame(s)}return{start:function(){e!==!0&&t!==null&&(n=i.requestAnimationFrame(s),e=!0)},stop:function(){i.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(r){t=r},setContext:function(r){i=r}}}function km(i){const e=new WeakMap;function t(a,c){const l=a.array,u=a.usage,h=l.byteLength,f=i.createBuffer();i.bindBuffer(c,f),i.bufferData(c,l,u),a.onUploadCallback();let d;if(l instanceof Float32Array)d=i.FLOAT;else if(l instanceof Uint16Array)a.isFloat16BufferAttribute?d=i.HALF_FLOAT:d=i.UNSIGNED_SHORT;else if(l instanceof Int16Array)d=i.SHORT;else if(l instanceof Uint32Array)d=i.UNSIGNED_INT;else if(l instanceof Int32Array)d=i.INT;else if(l instanceof Int8Array)d=i.BYTE;else if(l instanceof Uint8Array)d=i.UNSIGNED_BYTE;else if(l instanceof Uint8ClampedArray)d=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+l);return{buffer:f,type:d,bytesPerElement:l.BYTES_PER_ELEMENT,version:a.version,size:h}}function n(a,c,l){const u=c.array,h=c.updateRanges;if(i.bindBuffer(l,a),h.length===0)i.bufferSubData(l,0,u);else{h.sort((d,g)=>d.start-g.start);let f=0;for(let d=1;d<h.length;d++){const g=h[f],_=h[d];_.start<=g.start+g.count+1?g.count=Math.max(g.count,_.start+_.count-g.start):(++f,h[f]=_)}h.length=f+1;for(let d=0,g=h.length;d<g;d++){const _=h[d];i.bufferSubData(l,_.start*u.BYTES_PER_ELEMENT,u,_.start,_.count)}c.clearUpdateRanges()}c.onUploadCallback()}function s(a){return a.isInterleavedBufferAttribute&&(a=a.data),e.get(a)}function r(a){a.isInterleavedBufferAttribute&&(a=a.data);const c=e.get(a);c&&(i.deleteBuffer(c.buffer),e.delete(a))}function o(a,c){if(a.isInterleavedBufferAttribute&&(a=a.data),a.isGLBufferAttribute){const u=e.get(a);(!u||u.version<a.version)&&e.set(a,{buffer:a.buffer,type:a.type,bytesPerElement:a.elementSize,version:a.version});return}const l=e.get(a);if(l===void 0)e.set(a,t(a,c));else if(l.version<a.version){if(l.size!==a.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(l.buffer,a,c),l.version=a.version}}return{get:s,remove:r,update:o}}class Jn extends zt{constructor(e=1,t=1,n=1,s=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:s};const r=e/2,o=t/2,a=Math.floor(n),c=Math.floor(s),l=a+1,u=c+1,h=e/a,f=t/c,d=[],g=[],_=[],p=[];for(let m=0;m<u;m++){const v=m*f-o;for(let y=0;y<l;y++){const x=y*h-r;g.push(x,-v,0),_.push(0,0,1),p.push(y/a),p.push(1-m/c)}}for(let m=0;m<c;m++)for(let v=0;v<a;v++){const y=v+l*m,x=v+l*(m+1),P=v+1+l*(m+1),A=v+1+l*m;d.push(y,x,A),d.push(x,P,A)}this.setIndex(d),this.setAttribute("position",new rt(g,3)),this.setAttribute("normal",new rt(_,3)),this.setAttribute("uv",new rt(p,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Jn(e.width,e.height,e.widthSegments,e.heightSegments)}}var zm=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,Hm=`#ifdef USE_ALPHAHASH
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
#endif`,Vm=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,Gm=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,Wm=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,Xm=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,qm=`#ifdef USE_AOMAP
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
#endif`,Ym=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,jm=`#ifdef USE_BATCHING
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
#endif`,$m=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,Km=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,Zm=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,Jm=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,Qm=`#ifdef USE_IRIDESCENCE
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
#endif`,eg=`#ifdef USE_BUMPMAP
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
#endif`,tg=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,ng=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,ig=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,sg=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,rg=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,og=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,ag=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,cg=`#if defined( USE_COLOR_ALPHA )
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
#endif`,lg=`#define PI 3.141592653589793
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
} // validated`,ug=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,hg=`vec3 transformedNormal = objectNormal;
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
#endif`,fg=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,dg=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,pg=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,mg=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,gg="gl_FragColor = linearToOutputTexel( gl_FragColor );",_g=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,xg=`#ifdef USE_ENVMAP
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
#endif`,vg=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,yg=`#ifdef USE_ENVMAP
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
#endif`,Mg=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,Sg=`#ifdef USE_ENVMAP
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
#endif`,bg=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,wg=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,Eg=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,Tg=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,Ag=`#ifdef USE_GRADIENTMAP
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
}`,Rg=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,Cg=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,Pg=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,Lg=`uniform bool receiveShadow;
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
#endif`,Ig=`#ifdef USE_ENVMAP
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
#endif`,Dg=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,Ng=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,Ug=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,Og=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,Fg=`PhysicalMaterial material;
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
#endif`,Bg=`struct PhysicalMaterial {
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
}`,kg=`
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
#endif`,zg=`#if defined( RE_IndirectDiffuse )
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
#endif`,Hg=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,Vg=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,Gg=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,Wg=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,Xg=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,qg=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,Yg=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,jg=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,$g=`#if defined( USE_POINTS_UV )
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
#endif`,Kg=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,Zg=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,Jg=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,Qg=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,e0=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,t0=`#ifdef USE_MORPHTARGETS
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
#endif`,n0=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,i0=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,s0=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,r0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,o0=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,a0=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,c0=`#ifdef USE_NORMALMAP
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
#endif`,l0=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,u0=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,h0=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,f0=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,d0=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,p0=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,m0=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,g0=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,_0=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,x0=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,v0=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,y0=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,M0=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,S0=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,b0=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,w0=`float getShadowMask() {
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
}`,E0=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,T0=`#ifdef USE_SKINNING
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
#endif`,A0=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,R0=`#ifdef USE_SKINNING
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
#endif`,C0=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,P0=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,L0=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,I0=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,D0=`#ifdef USE_TRANSMISSION
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
#endif`,N0=`#ifdef USE_TRANSMISSION
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
#endif`,U0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,O0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,F0=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,B0=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const k0=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,z0=`uniform sampler2D t2D;
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
}`,H0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,V0=`#ifdef ENVMAP_TYPE_CUBE
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
}`,G0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,W0=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,X0=`#include <common>
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
}`,q0=`#if DEPTH_PACKING == 3200
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
}`,Y0=`#define DISTANCE
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
}`,j0=`#define DISTANCE
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
}`,$0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,K0=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Z0=`uniform float scale;
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
}`,J0=`uniform vec3 diffuse;
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
}`,Q0=`#include <common>
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
}`,e_=`uniform vec3 diffuse;
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
}`,t_=`#define LAMBERT
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
}`,n_=`#define LAMBERT
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
}`,i_=`#define MATCAP
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
}`,s_=`#define MATCAP
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
}`,r_=`#define NORMAL
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
}`,o_=`#define NORMAL
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
}`,a_=`#define PHONG
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
}`,c_=`#define PHONG
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
}`,l_=`#define STANDARD
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
}`,u_=`#define STANDARD
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
}`,h_=`#define TOON
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
}`,f_=`#define TOON
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
}`,d_=`uniform float size;
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
}`,p_=`uniform vec3 diffuse;
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
}`,m_=`#include <common>
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
}`,g_=`uniform vec3 color;
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
}`,__=`uniform float rotation;
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
}`,x_=`uniform vec3 diffuse;
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
}`,it={alphahash_fragment:zm,alphahash_pars_fragment:Hm,alphamap_fragment:Vm,alphamap_pars_fragment:Gm,alphatest_fragment:Wm,alphatest_pars_fragment:Xm,aomap_fragment:qm,aomap_pars_fragment:Ym,batching_pars_vertex:jm,batching_vertex:$m,begin_vertex:Km,beginnormal_vertex:Zm,bsdfs:Jm,iridescence_fragment:Qm,bumpmap_pars_fragment:eg,clipping_planes_fragment:tg,clipping_planes_pars_fragment:ng,clipping_planes_pars_vertex:ig,clipping_planes_vertex:sg,color_fragment:rg,color_pars_fragment:og,color_pars_vertex:ag,color_vertex:cg,common:lg,cube_uv_reflection_fragment:ug,defaultnormal_vertex:hg,displacementmap_pars_vertex:fg,displacementmap_vertex:dg,emissivemap_fragment:pg,emissivemap_pars_fragment:mg,colorspace_fragment:gg,colorspace_pars_fragment:_g,envmap_fragment:xg,envmap_common_pars_fragment:vg,envmap_pars_fragment:yg,envmap_pars_vertex:Mg,envmap_physical_pars_fragment:Ig,envmap_vertex:Sg,fog_vertex:bg,fog_pars_vertex:wg,fog_fragment:Eg,fog_pars_fragment:Tg,gradientmap_pars_fragment:Ag,lightmap_pars_fragment:Rg,lights_lambert_fragment:Cg,lights_lambert_pars_fragment:Pg,lights_pars_begin:Lg,lights_toon_fragment:Dg,lights_toon_pars_fragment:Ng,lights_phong_fragment:Ug,lights_phong_pars_fragment:Og,lights_physical_fragment:Fg,lights_physical_pars_fragment:Bg,lights_fragment_begin:kg,lights_fragment_maps:zg,lights_fragment_end:Hg,logdepthbuf_fragment:Vg,logdepthbuf_pars_fragment:Gg,logdepthbuf_pars_vertex:Wg,logdepthbuf_vertex:Xg,map_fragment:qg,map_pars_fragment:Yg,map_particle_fragment:jg,map_particle_pars_fragment:$g,metalnessmap_fragment:Kg,metalnessmap_pars_fragment:Zg,morphinstance_vertex:Jg,morphcolor_vertex:Qg,morphnormal_vertex:e0,morphtarget_pars_vertex:t0,morphtarget_vertex:n0,normal_fragment_begin:i0,normal_fragment_maps:s0,normal_pars_fragment:r0,normal_pars_vertex:o0,normal_vertex:a0,normalmap_pars_fragment:c0,clearcoat_normal_fragment_begin:l0,clearcoat_normal_fragment_maps:u0,clearcoat_pars_fragment:h0,iridescence_pars_fragment:f0,opaque_fragment:d0,packing:p0,premultiplied_alpha_fragment:m0,project_vertex:g0,dithering_fragment:_0,dithering_pars_fragment:x0,roughnessmap_fragment:v0,roughnessmap_pars_fragment:y0,shadowmap_pars_fragment:M0,shadowmap_pars_vertex:S0,shadowmap_vertex:b0,shadowmask_pars_fragment:w0,skinbase_vertex:E0,skinning_pars_vertex:T0,skinning_vertex:A0,skinnormal_vertex:R0,specularmap_fragment:C0,specularmap_pars_fragment:P0,tonemapping_fragment:L0,tonemapping_pars_fragment:I0,transmission_fragment:D0,transmission_pars_fragment:N0,uv_pars_fragment:U0,uv_pars_vertex:O0,uv_vertex:F0,worldpos_vertex:B0,background_vert:k0,background_frag:z0,backgroundCube_vert:H0,backgroundCube_frag:V0,cube_vert:G0,cube_frag:W0,depth_vert:X0,depth_frag:q0,distanceRGBA_vert:Y0,distanceRGBA_frag:j0,equirect_vert:$0,equirect_frag:K0,linedashed_vert:Z0,linedashed_frag:J0,meshbasic_vert:Q0,meshbasic_frag:e_,meshlambert_vert:t_,meshlambert_frag:n_,meshmatcap_vert:i_,meshmatcap_frag:s_,meshnormal_vert:r_,meshnormal_frag:o_,meshphong_vert:a_,meshphong_frag:c_,meshphysical_vert:l_,meshphysical_frag:u_,meshtoon_vert:h_,meshtoon_frag:f_,points_vert:d_,points_frag:p_,shadow_vert:m_,shadow_frag:g_,sprite_vert:__,sprite_frag:x_},ge={common:{diffuse:{value:new ze(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new tt},alphaMap:{value:null},alphaMapTransform:{value:new tt},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new tt}},envmap:{envMap:{value:null},envMapRotation:{value:new tt},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new tt}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new tt}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new tt},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new tt},normalScale:{value:new te(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new tt},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new tt}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new tt}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new tt}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new ze(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new ze(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new tt},alphaTest:{value:0},uvTransform:{value:new tt}},sprite:{diffuse:{value:new ze(16777215)},opacity:{value:1},center:{value:new te(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new tt},alphaMap:{value:null},alphaMapTransform:{value:new tt},alphaTest:{value:0}}},jn={basic:{uniforms:ln([ge.common,ge.specularmap,ge.envmap,ge.aomap,ge.lightmap,ge.fog]),vertexShader:it.meshbasic_vert,fragmentShader:it.meshbasic_frag},lambert:{uniforms:ln([ge.common,ge.specularmap,ge.envmap,ge.aomap,ge.lightmap,ge.emissivemap,ge.bumpmap,ge.normalmap,ge.displacementmap,ge.fog,ge.lights,{emissive:{value:new ze(0)}}]),vertexShader:it.meshlambert_vert,fragmentShader:it.meshlambert_frag},phong:{uniforms:ln([ge.common,ge.specularmap,ge.envmap,ge.aomap,ge.lightmap,ge.emissivemap,ge.bumpmap,ge.normalmap,ge.displacementmap,ge.fog,ge.lights,{emissive:{value:new ze(0)},specular:{value:new ze(1118481)},shininess:{value:30}}]),vertexShader:it.meshphong_vert,fragmentShader:it.meshphong_frag},standard:{uniforms:ln([ge.common,ge.envmap,ge.aomap,ge.lightmap,ge.emissivemap,ge.bumpmap,ge.normalmap,ge.displacementmap,ge.roughnessmap,ge.metalnessmap,ge.fog,ge.lights,{emissive:{value:new ze(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:it.meshphysical_vert,fragmentShader:it.meshphysical_frag},toon:{uniforms:ln([ge.common,ge.aomap,ge.lightmap,ge.emissivemap,ge.bumpmap,ge.normalmap,ge.displacementmap,ge.gradientmap,ge.fog,ge.lights,{emissive:{value:new ze(0)}}]),vertexShader:it.meshtoon_vert,fragmentShader:it.meshtoon_frag},matcap:{uniforms:ln([ge.common,ge.bumpmap,ge.normalmap,ge.displacementmap,ge.fog,{matcap:{value:null}}]),vertexShader:it.meshmatcap_vert,fragmentShader:it.meshmatcap_frag},points:{uniforms:ln([ge.points,ge.fog]),vertexShader:it.points_vert,fragmentShader:it.points_frag},dashed:{uniforms:ln([ge.common,ge.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:it.linedashed_vert,fragmentShader:it.linedashed_frag},depth:{uniforms:ln([ge.common,ge.displacementmap]),vertexShader:it.depth_vert,fragmentShader:it.depth_frag},normal:{uniforms:ln([ge.common,ge.bumpmap,ge.normalmap,ge.displacementmap,{opacity:{value:1}}]),vertexShader:it.meshnormal_vert,fragmentShader:it.meshnormal_frag},sprite:{uniforms:ln([ge.sprite,ge.fog]),vertexShader:it.sprite_vert,fragmentShader:it.sprite_frag},background:{uniforms:{uvTransform:{value:new tt},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:it.background_vert,fragmentShader:it.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new tt}},vertexShader:it.backgroundCube_vert,fragmentShader:it.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:it.cube_vert,fragmentShader:it.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:it.equirect_vert,fragmentShader:it.equirect_frag},distanceRGBA:{uniforms:ln([ge.common,ge.displacementmap,{referencePosition:{value:new M},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:it.distanceRGBA_vert,fragmentShader:it.distanceRGBA_frag},shadow:{uniforms:ln([ge.lights,ge.fog,{color:{value:new ze(0)},opacity:{value:1}}]),vertexShader:it.shadow_vert,fragmentShader:it.shadow_frag}};jn.physical={uniforms:ln([jn.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new tt},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new tt},clearcoatNormalScale:{value:new te(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new tt},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new tt},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new tt},sheen:{value:0},sheenColor:{value:new ze(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new tt},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new tt},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new tt},transmissionSamplerSize:{value:new te},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new tt},attenuationDistance:{value:0},attenuationColor:{value:new ze(0)},specularColor:{value:new ze(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new tt},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new tt},anisotropyVector:{value:new te},anisotropyMap:{value:null},anisotropyMapTransform:{value:new tt}}]),vertexShader:it.meshphysical_vert,fragmentShader:it.meshphysical_frag};const wo={r:0,b:0,g:0},ss=new wn,v_=new Le;function y_(i,e,t,n,s,r,o){const a=new ze(0);let c=r===!0?0:1,l,u,h=null,f=0,d=null;function g(v){let y=v.isScene===!0?v.background:null;return y&&y.isTexture&&(y=(v.backgroundBlurriness>0?t:e).get(y)),y}function _(v){let y=!1;const x=g(v);x===null?m(a,c):x&&x.isColor&&(m(x,1),y=!0);const P=i.xr.getEnvironmentBlendMode();P==="additive"?n.buffers.color.setClear(0,0,0,1,o):P==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,o),(i.autoClear||y)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function p(v,y){const x=g(y);x&&(x.isCubeTexture||x.mapping===ha)?(u===void 0&&(u=new kt(new Ct(1,1,1),new Zn({name:"BackgroundCubeMaterial",uniforms:ir(jn.backgroundCube.uniforms),vertexShader:jn.backgroundCube.vertexShader,fragmentShader:jn.backgroundCube.fragmentShader,side:fn,depthTest:!1,depthWrite:!1,fog:!1})),u.geometry.deleteAttribute("normal"),u.geometry.deleteAttribute("uv"),u.onBeforeRender=function(P,A,E){this.matrixWorld.copyPosition(E.matrixWorld)},Object.defineProperty(u.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),s.update(u)),ss.copy(y.backgroundRotation),ss.x*=-1,ss.y*=-1,ss.z*=-1,x.isCubeTexture&&x.isRenderTargetTexture===!1&&(ss.y*=-1,ss.z*=-1),u.material.uniforms.envMap.value=x,u.material.uniforms.flipEnvMap.value=x.isCubeTexture&&x.isRenderTargetTexture===!1?-1:1,u.material.uniforms.backgroundBlurriness.value=y.backgroundBlurriness,u.material.uniforms.backgroundIntensity.value=y.backgroundIntensity,u.material.uniforms.backgroundRotation.value.setFromMatrix4(v_.makeRotationFromEuler(ss)),u.material.toneMapped=at.getTransfer(x.colorSpace)!==St,(h!==x||f!==x.version||d!==i.toneMapping)&&(u.material.needsUpdate=!0,h=x,f=x.version,d=i.toneMapping),u.layers.enableAll(),v.unshift(u,u.geometry,u.material,0,0,null)):x&&x.isTexture&&(l===void 0&&(l=new kt(new Jn(2,2),new Zn({name:"BackgroundMaterial",uniforms:ir(jn.background.uniforms),vertexShader:jn.background.vertexShader,fragmentShader:jn.background.fragmentShader,side:vi,depthTest:!1,depthWrite:!1,fog:!1})),l.geometry.deleteAttribute("normal"),Object.defineProperty(l.material,"map",{get:function(){return this.uniforms.t2D.value}}),s.update(l)),l.material.uniforms.t2D.value=x,l.material.uniforms.backgroundIntensity.value=y.backgroundIntensity,l.material.toneMapped=at.getTransfer(x.colorSpace)!==St,x.matrixAutoUpdate===!0&&x.updateMatrix(),l.material.uniforms.uvTransform.value.copy(x.matrix),(h!==x||f!==x.version||d!==i.toneMapping)&&(l.material.needsUpdate=!0,h=x,f=x.version,d=i.toneMapping),l.layers.enableAll(),v.unshift(l,l.geometry,l.material,0,0,null))}function m(v,y){v.getRGB(wo,Hf(i)),n.buffers.color.setClear(wo.r,wo.g,wo.b,y,o)}return{getClearColor:function(){return a},setClearColor:function(v,y=1){a.set(v),c=y,m(a,c)},getClearAlpha:function(){return c},setClearAlpha:function(v){c=v,m(a,c)},render:_,addToRenderList:p}}function M_(i,e){const t=i.getParameter(i.MAX_VERTEX_ATTRIBS),n={},s=f(null);let r=s,o=!1;function a(S,I,B,O,k){let K=!1;const W=h(O,B,I);r!==W&&(r=W,l(r.object)),K=d(S,O,B,k),K&&g(S,O,B,k),k!==null&&e.update(k,i.ELEMENT_ARRAY_BUFFER),(K||o)&&(o=!1,x(S,I,B,O),k!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,e.get(k).buffer))}function c(){return i.createVertexArray()}function l(S){return i.bindVertexArray(S)}function u(S){return i.deleteVertexArray(S)}function h(S,I,B){const O=B.wireframe===!0;let k=n[S.id];k===void 0&&(k={},n[S.id]=k);let K=k[I.id];K===void 0&&(K={},k[I.id]=K);let W=K[O];return W===void 0&&(W=f(c()),K[O]=W),W}function f(S){const I=[],B=[],O=[];for(let k=0;k<t;k++)I[k]=0,B[k]=0,O[k]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:I,enabledAttributes:B,attributeDivisors:O,object:S,attributes:{},index:null}}function d(S,I,B,O){const k=r.attributes,K=I.attributes;let W=0;const q=B.getAttributes();for(const V in q)if(q[V].location>=0){const me=k[V];let Se=K[V];if(Se===void 0&&(V==="instanceMatrix"&&S.instanceMatrix&&(Se=S.instanceMatrix),V==="instanceColor"&&S.instanceColor&&(Se=S.instanceColor)),me===void 0||me.attribute!==Se||Se&&me.data!==Se.data)return!0;W++}return r.attributesNum!==W||r.index!==O}function g(S,I,B,O){const k={},K=I.attributes;let W=0;const q=B.getAttributes();for(const V in q)if(q[V].location>=0){let me=K[V];me===void 0&&(V==="instanceMatrix"&&S.instanceMatrix&&(me=S.instanceMatrix),V==="instanceColor"&&S.instanceColor&&(me=S.instanceColor));const Se={};Se.attribute=me,me&&me.data&&(Se.data=me.data),k[V]=Se,W++}r.attributes=k,r.attributesNum=W,r.index=O}function _(){const S=r.newAttributes;for(let I=0,B=S.length;I<B;I++)S[I]=0}function p(S){m(S,0)}function m(S,I){const B=r.newAttributes,O=r.enabledAttributes,k=r.attributeDivisors;B[S]=1,O[S]===0&&(i.enableVertexAttribArray(S),O[S]=1),k[S]!==I&&(i.vertexAttribDivisor(S,I),k[S]=I)}function v(){const S=r.newAttributes,I=r.enabledAttributes;for(let B=0,O=I.length;B<O;B++)I[B]!==S[B]&&(i.disableVertexAttribArray(B),I[B]=0)}function y(S,I,B,O,k,K,W){W===!0?i.vertexAttribIPointer(S,I,B,k,K):i.vertexAttribPointer(S,I,B,O,k,K)}function x(S,I,B,O){_();const k=O.attributes,K=B.getAttributes(),W=I.defaultAttributeValues;for(const q in K){const V=K[q];if(V.location>=0){let se=k[q];if(se===void 0&&(q==="instanceMatrix"&&S.instanceMatrix&&(se=S.instanceMatrix),q==="instanceColor"&&S.instanceColor&&(se=S.instanceColor)),se!==void 0){const me=se.normalized,Se=se.itemSize,Ze=e.get(se);if(Ze===void 0)continue;const pt=Ze.buffer,Z=Ze.type,le=Ze.bytesPerElement,Ie=Z===i.INT||Z===i.UNSIGNED_INT||se.gpuType===Nl;if(se.isInterleavedBufferAttribute){const fe=se.data,He=fe.stride,je=se.offset;if(fe.isInstancedInterleavedBuffer){for(let qe=0;qe<V.locationSize;qe++)m(V.location+qe,fe.meshPerAttribute);S.isInstancedMesh!==!0&&O._maxInstanceCount===void 0&&(O._maxInstanceCount=fe.meshPerAttribute*fe.count)}else for(let qe=0;qe<V.locationSize;qe++)p(V.location+qe);i.bindBuffer(i.ARRAY_BUFFER,pt);for(let qe=0;qe<V.locationSize;qe++)y(V.location+qe,Se/V.locationSize,Z,me,He*le,(je+Se/V.locationSize*qe)*le,Ie)}else{if(se.isInstancedBufferAttribute){for(let fe=0;fe<V.locationSize;fe++)m(V.location+fe,se.meshPerAttribute);S.isInstancedMesh!==!0&&O._maxInstanceCount===void 0&&(O._maxInstanceCount=se.meshPerAttribute*se.count)}else for(let fe=0;fe<V.locationSize;fe++)p(V.location+fe);i.bindBuffer(i.ARRAY_BUFFER,pt);for(let fe=0;fe<V.locationSize;fe++)y(V.location+fe,Se/V.locationSize,Z,me,Se*le,Se/V.locationSize*fe*le,Ie)}}else if(W!==void 0){const me=W[q];if(me!==void 0)switch(me.length){case 2:i.vertexAttrib2fv(V.location,me);break;case 3:i.vertexAttrib3fv(V.location,me);break;case 4:i.vertexAttrib4fv(V.location,me);break;default:i.vertexAttrib1fv(V.location,me)}}}}v()}function P(){R();for(const S in n){const I=n[S];for(const B in I){const O=I[B];for(const k in O)u(O[k].object),delete O[k];delete I[B]}delete n[S]}}function A(S){if(n[S.id]===void 0)return;const I=n[S.id];for(const B in I){const O=I[B];for(const k in O)u(O[k].object),delete O[k];delete I[B]}delete n[S.id]}function E(S){for(const I in n){const B=n[I];if(B[S.id]===void 0)continue;const O=B[S.id];for(const k in O)u(O[k].object),delete O[k];delete B[S.id]}}function R(){b(),o=!0,r!==s&&(r=s,l(r.object))}function b(){s.geometry=null,s.program=null,s.wireframe=!1}return{setup:a,reset:R,resetDefaultState:b,dispose:P,releaseStatesOfGeometry:A,releaseStatesOfProgram:E,initAttributes:_,enableAttribute:p,disableUnusedAttributes:v}}function S_(i,e,t){let n;function s(l){n=l}function r(l,u){i.drawArrays(n,l,u),t.update(u,n,1)}function o(l,u,h){h!==0&&(i.drawArraysInstanced(n,l,u,h),t.update(u,n,h))}function a(l,u,h){if(h===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,l,0,u,0,h);let d=0;for(let g=0;g<h;g++)d+=u[g];t.update(d,n,1)}function c(l,u,h,f){if(h===0)return;const d=e.get("WEBGL_multi_draw");if(d===null)for(let g=0;g<l.length;g++)o(l[g],u[g],f[g]);else{d.multiDrawArraysInstancedWEBGL(n,l,0,u,0,f,0,h);let g=0;for(let _=0;_<h;_++)g+=u[_]*f[_];t.update(g,n,1)}}this.setMode=s,this.render=r,this.renderInstances=o,this.renderMultiDraw=a,this.renderMultiDrawInstances=c}function b_(i,e,t,n){let s;function r(){if(s!==void 0)return s;if(e.has("EXT_texture_filter_anisotropic")===!0){const E=e.get("EXT_texture_filter_anisotropic");s=i.getParameter(E.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else s=0;return s}function o(E){return!(E!==In&&n.convert(E)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function a(E){const R=E===$r&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(E!==yi&&n.convert(E)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&E!==Xn&&!R)}function c(E){if(E==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";E="mediump"}return E==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let l=t.precision!==void 0?t.precision:"highp";const u=c(l);u!==l&&(console.warn("THREE.WebGLRenderer:",l,"not supported, using",u,"instead."),l=u);const h=t.logarithmicDepthBuffer===!0,f=t.reverseDepthBuffer===!0&&e.has("EXT_clip_control"),d=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),g=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),_=i.getParameter(i.MAX_TEXTURE_SIZE),p=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),m=i.getParameter(i.MAX_VERTEX_ATTRIBS),v=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),y=i.getParameter(i.MAX_VARYING_VECTORS),x=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),P=g>0,A=i.getParameter(i.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:r,getMaxPrecision:c,textureFormatReadable:o,textureTypeReadable:a,precision:l,logarithmicDepthBuffer:h,reverseDepthBuffer:f,maxTextures:d,maxVertexTextures:g,maxTextureSize:_,maxCubemapSize:p,maxAttributes:m,maxVertexUniforms:v,maxVaryings:y,maxFragmentUniforms:x,vertexTextures:P,maxSamples:A}}function w_(i){const e=this;let t=null,n=0,s=!1,r=!1;const o=new us,a=new tt,c={value:null,needsUpdate:!1};this.uniform=c,this.numPlanes=0,this.numIntersection=0,this.init=function(h,f){const d=h.length!==0||f||n!==0||s;return s=f,n=h.length,d},this.beginShadows=function(){r=!0,u(null)},this.endShadows=function(){r=!1},this.setGlobalState=function(h,f){t=u(h,f,0)},this.setState=function(h,f,d){const g=h.clippingPlanes,_=h.clipIntersection,p=h.clipShadows,m=i.get(h);if(!s||g===null||g.length===0||r&&!p)r?u(null):l();else{const v=r?0:n,y=v*4;let x=m.clippingState||null;c.value=x,x=u(g,f,y,d);for(let P=0;P!==y;++P)x[P]=t[P];m.clippingState=x,this.numIntersection=_?this.numPlanes:0,this.numPlanes+=v}};function l(){c.value!==t&&(c.value=t,c.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function u(h,f,d,g){const _=h!==null?h.length:0;let p=null;if(_!==0){if(p=c.value,g!==!0||p===null){const m=d+_*4,v=f.matrixWorldInverse;a.getNormalMatrix(v),(p===null||p.length<m)&&(p=new Float32Array(m));for(let y=0,x=d;y!==_;++y,x+=4)o.copy(h[y]).applyMatrix4(v,a),o.normal.toArray(p,x),p[x+3]=o.constant}c.value=p,c.needsUpdate=!0}return e.numPlanes=_,e.numIntersection=0,p}}function E_(i){let e=new WeakMap;function t(o,a){return a===Hc?o.mapping=Zs:a===Vc&&(o.mapping=Js),o}function n(o){if(o&&o.isTexture){const a=o.mapping;if(a===Hc||a===Vc)if(e.has(o)){const c=e.get(o).texture;return t(c,o.mapping)}else{const c=o.image;if(c&&c.height>0){const l=new Om(c.height);return l.fromEquirectangularTexture(i,o),e.set(o,l),o.addEventListener("dispose",s),t(l.texture,o.mapping)}else return null}}return o}function s(o){const a=o.target;a.removeEventListener("dispose",s);const c=e.get(a);c!==void 0&&(e.delete(a),c.dispose())}function r(){e=new WeakMap}return{get:n,dispose:r}}class pa extends Vf{constructor(e=-1,t=1,n=1,s=-1,r=.1,o=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=s,this.near=r,this.far=o,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,s,r,o){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,s=(this.top+this.bottom)/2;let r=n-e,o=n+e,a=s+t,c=s-t;if(this.view!==null&&this.view.enabled){const l=(this.right-this.left)/this.view.fullWidth/this.zoom,u=(this.top-this.bottom)/this.view.fullHeight/this.zoom;r+=l*this.view.offsetX,o=r+l*this.view.width,a-=u*this.view.offsetY,c=a-u*this.view.height}this.projectionMatrix.makeOrthographic(r,o,a,c,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Hs=4,Zu=[.125,.215,.35,.446,.526,.582],ds=20,ja=new pa,Ju=new ze;let $a=null,Ka=0,Za=0,Ja=!1;const hs=(1+Math.sqrt(5))/2,Os=1/hs,Qu=[new M(-hs,Os,0),new M(hs,Os,0),new M(-Os,0,hs),new M(Os,0,hs),new M(0,hs,-Os),new M(0,hs,Os),new M(-1,1,-1),new M(1,1,-1),new M(-1,1,1),new M(1,1,1)];class eh{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,s=100){$a=this._renderer.getRenderTarget(),Ka=this._renderer.getActiveCubeFace(),Za=this._renderer.getActiveMipmapLevel(),Ja=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const r=this._allocateTargets();return r.depthBuffer=!0,this._sceneToCubeUV(e,n,s,r),t>0&&this._blur(r,0,0,t),this._applyPMREM(r),this._cleanup(r),r}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=ih(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=nh(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget($a,Ka,Za),this._renderer.xr.enabled=Ja,e.scissorTest=!1,Eo(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Zs||e.mapping===Js?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),$a=this._renderer.getRenderTarget(),Ka=this._renderer.getActiveCubeFace(),Za=this._renderer.getActiveMipmapLevel(),Ja=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:Sn,minFilter:Sn,generateMipmaps:!1,type:$r,format:In,colorSpace:an,depthBuffer:!1},s=th(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=th(e,t,n);const{_lodMax:r}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=T_(r)),this._blurMaterial=A_(r,e,t)}return s}_compileMaterial(e){const t=new kt(this._lodPlanes[0],e);this._renderer.compile(t,ja)}_sceneToCubeUV(e,t,n,s){const a=new _n(90,1,t,n),c=[1,-1,1,1,1,1],l=[1,1,1,-1,-1,-1],u=this._renderer,h=u.autoClear,f=u.toneMapping;u.getClearColor(Ju),u.toneMapping=Gi,u.autoClear=!1;const d=new on({name:"PMREM.Background",side:fn,depthWrite:!1,depthTest:!1}),g=new kt(new Ct,d);let _=!1;const p=e.background;p?p.isColor&&(d.color.copy(p),e.background=null,_=!0):(d.color.copy(Ju),_=!0);for(let m=0;m<6;m++){const v=m%3;v===0?(a.up.set(0,c[m],0),a.lookAt(l[m],0,0)):v===1?(a.up.set(0,0,c[m]),a.lookAt(0,l[m],0)):(a.up.set(0,c[m],0),a.lookAt(0,0,l[m]));const y=this._cubeSize;Eo(s,v*y,m>2?y:0,y,y),u.setRenderTarget(s),_&&u.render(g,a),u.render(e,a)}g.geometry.dispose(),g.material.dispose(),u.toneMapping=f,u.autoClear=h,e.background=p}_textureToCubeUV(e,t){const n=this._renderer,s=e.mapping===Zs||e.mapping===Js;s?(this._cubemapMaterial===null&&(this._cubemapMaterial=ih()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=nh());const r=s?this._cubemapMaterial:this._equirectMaterial,o=new kt(this._lodPlanes[0],r),a=r.uniforms;a.envMap.value=e;const c=this._cubeSize;Eo(t,0,0,3*c,2*c),n.setRenderTarget(t),n.render(o,ja)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const s=this._lodPlanes.length;for(let r=1;r<s;r++){const o=Math.sqrt(this._sigmas[r]*this._sigmas[r]-this._sigmas[r-1]*this._sigmas[r-1]),a=Qu[(s-r-1)%Qu.length];this._blur(e,r-1,r,o,a)}t.autoClear=n}_blur(e,t,n,s,r){const o=this._pingPongRenderTarget;this._halfBlur(e,o,t,n,s,"latitudinal",r),this._halfBlur(o,e,n,n,s,"longitudinal",r)}_halfBlur(e,t,n,s,r,o,a){const c=this._renderer,l=this._blurMaterial;o!=="latitudinal"&&o!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const u=3,h=new kt(this._lodPlanes[s],l),f=l.uniforms,d=this._sizeLods[n]-1,g=isFinite(r)?Math.PI/(2*d):2*Math.PI/(2*ds-1),_=r/g,p=isFinite(r)?1+Math.floor(u*_):ds;p>ds&&console.warn(`sigmaRadians, ${r}, is too large and will clip, as it requested ${p} samples when the maximum is set to ${ds}`);const m=[];let v=0;for(let E=0;E<ds;++E){const R=E/_,b=Math.exp(-R*R/2);m.push(b),E===0?v+=b:E<p&&(v+=2*b)}for(let E=0;E<m.length;E++)m[E]=m[E]/v;f.envMap.value=e.texture,f.samples.value=p,f.weights.value=m,f.latitudinal.value=o==="latitudinal",a&&(f.poleAxis.value=a);const{_lodMax:y}=this;f.dTheta.value=g,f.mipInt.value=y-n;const x=this._sizeLods[s],P=3*x*(s>y-Hs?s-y+Hs:0),A=4*(this._cubeSize-x);Eo(t,P,A,3*x,2*x),c.setRenderTarget(t),c.render(h,ja)}}function T_(i){const e=[],t=[],n=[];let s=i;const r=i-Hs+1+Zu.length;for(let o=0;o<r;o++){const a=Math.pow(2,s);t.push(a);let c=1/a;o>i-Hs?c=Zu[o-i+Hs-1]:o===0&&(c=0),n.push(c);const l=1/(a-2),u=-l,h=1+l,f=[u,u,h,u,h,h,u,u,h,h,u,h],d=6,g=6,_=3,p=2,m=1,v=new Float32Array(_*g*d),y=new Float32Array(p*g*d),x=new Float32Array(m*g*d);for(let A=0;A<d;A++){const E=A%3*2/3-1,R=A>2?0:-1,b=[E,R,0,E+2/3,R,0,E+2/3,R+1,0,E,R,0,E+2/3,R+1,0,E,R+1,0];v.set(b,_*g*A),y.set(f,p*g*A);const S=[A,A,A,A,A,A];x.set(S,m*g*A)}const P=new zt;P.setAttribute("position",new $t(v,_)),P.setAttribute("uv",new $t(y,p)),P.setAttribute("faceIndex",new $t(x,m)),e.push(P),s>Hs&&s--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function th(i,e,t){const n=new gs(i,e,t);return n.texture.mapping=ha,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function Eo(i,e,t,n,s){i.viewport.set(e,t,n,s),i.scissor.set(e,t,n,s)}function A_(i,e,t){const n=new Float32Array(ds),s=new M(0,1,0);return new Zn({name:"SphericalGaussianBlur",defines:{n:ds,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:s}},vertexShader:Wl(),fragmentShader:`

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
		`,blending:Vi,depthTest:!1,depthWrite:!1})}function nh(){return new Zn({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Wl(),fragmentShader:`

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
		`,blending:Vi,depthTest:!1,depthWrite:!1})}function ih(){return new Zn({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Wl(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Vi,depthTest:!1,depthWrite:!1})}function Wl(){return`

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
	`}function R_(i){let e=new WeakMap,t=null;function n(a){if(a&&a.isTexture){const c=a.mapping,l=c===Hc||c===Vc,u=c===Zs||c===Js;if(l||u){let h=e.get(a);const f=h!==void 0?h.texture.pmremVersion:0;if(a.isRenderTargetTexture&&a.pmremVersion!==f)return t===null&&(t=new eh(i)),h=l?t.fromEquirectangular(a,h):t.fromCubemap(a,h),h.texture.pmremVersion=a.pmremVersion,e.set(a,h),h.texture;if(h!==void 0)return h.texture;{const d=a.image;return l&&d&&d.height>0||u&&d&&s(d)?(t===null&&(t=new eh(i)),h=l?t.fromEquirectangular(a):t.fromCubemap(a),h.texture.pmremVersion=a.pmremVersion,e.set(a,h),a.addEventListener("dispose",r),h.texture):null}}}return a}function s(a){let c=0;const l=6;for(let u=0;u<l;u++)a[u]!==void 0&&c++;return c===l}function r(a){const c=a.target;c.removeEventListener("dispose",r);const l=e.get(c);l!==void 0&&(e.delete(c),l.dispose())}function o(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:o}}function C_(i){const e={};function t(n){if(e[n]!==void 0)return e[n];let s;switch(n){case"WEBGL_depth_texture":s=i.getExtension("WEBGL_depth_texture")||i.getExtension("MOZ_WEBGL_depth_texture")||i.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":s=i.getExtension("EXT_texture_filter_anisotropic")||i.getExtension("MOZ_EXT_texture_filter_anisotropic")||i.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":s=i.getExtension("WEBGL_compressed_texture_s3tc")||i.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":s=i.getExtension("WEBGL_compressed_texture_pvrtc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:s=i.getExtension(n)}return e[n]=s,s}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const s=t(n);return s===null&&Dr("THREE.WebGLRenderer: "+n+" extension not supported."),s}}}function P_(i,e,t,n){const s={},r=new WeakMap;function o(h){const f=h.target;f.index!==null&&e.remove(f.index);for(const g in f.attributes)e.remove(f.attributes[g]);for(const g in f.morphAttributes){const _=f.morphAttributes[g];for(let p=0,m=_.length;p<m;p++)e.remove(_[p])}f.removeEventListener("dispose",o),delete s[f.id];const d=r.get(f);d&&(e.remove(d),r.delete(f)),n.releaseStatesOfGeometry(f),f.isInstancedBufferGeometry===!0&&delete f._maxInstanceCount,t.memory.geometries--}function a(h,f){return s[f.id]===!0||(f.addEventListener("dispose",o),s[f.id]=!0,t.memory.geometries++),f}function c(h){const f=h.attributes;for(const g in f)e.update(f[g],i.ARRAY_BUFFER);const d=h.morphAttributes;for(const g in d){const _=d[g];for(let p=0,m=_.length;p<m;p++)e.update(_[p],i.ARRAY_BUFFER)}}function l(h){const f=[],d=h.index,g=h.attributes.position;let _=0;if(d!==null){const v=d.array;_=d.version;for(let y=0,x=v.length;y<x;y+=3){const P=v[y+0],A=v[y+1],E=v[y+2];f.push(P,A,A,E,E,P)}}else if(g!==void 0){const v=g.array;_=g.version;for(let y=0,x=v.length/3-1;y<x;y+=3){const P=y+0,A=y+1,E=y+2;f.push(P,A,A,E,E,P)}}else return;const p=new(Uf(f)?zf:Vl)(f,1);p.version=_;const m=r.get(h);m&&e.remove(m),r.set(h,p)}function u(h){const f=r.get(h);if(f){const d=h.index;d!==null&&f.version<d.version&&l(h)}else l(h);return r.get(h)}return{get:a,update:c,getWireframeAttribute:u}}function L_(i,e,t){let n;function s(f){n=f}let r,o;function a(f){r=f.type,o=f.bytesPerElement}function c(f,d){i.drawElements(n,d,r,f*o),t.update(d,n,1)}function l(f,d,g){g!==0&&(i.drawElementsInstanced(n,d,r,f*o,g),t.update(d,n,g))}function u(f,d,g){if(g===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,d,0,r,f,0,g);let p=0;for(let m=0;m<g;m++)p+=d[m];t.update(p,n,1)}function h(f,d,g,_){if(g===0)return;const p=e.get("WEBGL_multi_draw");if(p===null)for(let m=0;m<f.length;m++)l(f[m]/o,d[m],_[m]);else{p.multiDrawElementsInstancedWEBGL(n,d,0,r,f,0,_,0,g);let m=0;for(let v=0;v<g;v++)m+=d[v]*_[v];t.update(m,n,1)}}this.setMode=s,this.setIndex=a,this.render=c,this.renderInstances=l,this.renderMultiDraw=u,this.renderMultiDrawInstances=h}function I_(i){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(r,o,a){switch(t.calls++,o){case i.TRIANGLES:t.triangles+=a*(r/3);break;case i.LINES:t.lines+=a*(r/2);break;case i.LINE_STRIP:t.lines+=a*(r-1);break;case i.LINE_LOOP:t.lines+=a*r;break;case i.POINTS:t.points+=a*r;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",o);break}}function s(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:s,update:n}}function D_(i,e,t){const n=new WeakMap,s=new dt;function r(o,a,c){const l=o.morphTargetInfluences,u=a.morphAttributes.position||a.morphAttributes.normal||a.morphAttributes.color,h=u!==void 0?u.length:0;let f=n.get(a);if(f===void 0||f.count!==h){let b=function(){E.dispose(),n.delete(a),a.removeEventListener("dispose",b)};f!==void 0&&f.texture.dispose();const d=a.morphAttributes.position!==void 0,g=a.morphAttributes.normal!==void 0,_=a.morphAttributes.color!==void 0,p=a.morphAttributes.position||[],m=a.morphAttributes.normal||[],v=a.morphAttributes.color||[];let y=0;d===!0&&(y=1),g===!0&&(y=2),_===!0&&(y=3);let x=a.attributes.position.count*y,P=1;x>e.maxTextureSize&&(P=Math.ceil(x/e.maxTextureSize),x=e.maxTextureSize);const A=new Float32Array(x*P*4*h),E=new Ff(A,x,P,h);E.type=Xn,E.needsUpdate=!0;const R=y*4;for(let S=0;S<h;S++){const I=p[S],B=m[S],O=v[S],k=x*P*4*S;for(let K=0;K<I.count;K++){const W=K*R;d===!0&&(s.fromBufferAttribute(I,K),A[k+W+0]=s.x,A[k+W+1]=s.y,A[k+W+2]=s.z,A[k+W+3]=0),g===!0&&(s.fromBufferAttribute(B,K),A[k+W+4]=s.x,A[k+W+5]=s.y,A[k+W+6]=s.z,A[k+W+7]=0),_===!0&&(s.fromBufferAttribute(O,K),A[k+W+8]=s.x,A[k+W+9]=s.y,A[k+W+10]=s.z,A[k+W+11]=O.itemSize===4?s.w:1)}}f={count:h,texture:E,size:new te(x,P)},n.set(a,f),a.addEventListener("dispose",b)}if(o.isInstancedMesh===!0&&o.morphTexture!==null)c.getUniforms().setValue(i,"morphTexture",o.morphTexture,t);else{let d=0;for(let _=0;_<l.length;_++)d+=l[_];const g=a.morphTargetsRelative?1:1-d;c.getUniforms().setValue(i,"morphTargetBaseInfluence",g),c.getUniforms().setValue(i,"morphTargetInfluences",l)}c.getUniforms().setValue(i,"morphTargetsTexture",f.texture,t),c.getUniforms().setValue(i,"morphTargetsTextureSize",f.size)}return{update:r}}function N_(i,e,t,n){let s=new WeakMap;function r(c){const l=n.render.frame,u=c.geometry,h=e.get(c,u);if(s.get(h)!==l&&(e.update(h),s.set(h,l)),c.isInstancedMesh&&(c.hasEventListener("dispose",a)===!1&&c.addEventListener("dispose",a),s.get(c)!==l&&(t.update(c.instanceMatrix,i.ARRAY_BUFFER),c.instanceColor!==null&&t.update(c.instanceColor,i.ARRAY_BUFFER),s.set(c,l))),c.isSkinnedMesh){const f=c.skeleton;s.get(f)!==l&&(f.update(),s.set(f,l))}return h}function o(){s=new WeakMap}function a(c){const l=c.target;l.removeEventListener("dispose",a),t.remove(l.instanceMatrix),l.instanceColor!==null&&t.remove(l.instanceColor)}return{update:r,dispose:o}}class Xf extends jt{constructor(e,t,n,s,r,o,a,c,l,u=Xs){if(u!==Xs&&u!==tr)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&u===Xs&&(n=ms),n===void 0&&u===tr&&(n=er),super(null,s,r,o,a,c,u,n,l),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=a!==void 0?a:dn,this.minFilter=c!==void 0?c:dn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const qf=new jt,sh=new Xf(1,1),Yf=new Ff,jf=new ym,$f=new Gf,rh=[],oh=[],ah=new Float32Array(16),ch=new Float32Array(9),lh=new Float32Array(4);function lr(i,e,t){const n=i[0];if(n<=0||n>0)return i;const s=e*t;let r=rh[s];if(r===void 0&&(r=new Float32Array(s),rh[s]=r),e!==0){n.toArray(r,0);for(let o=1,a=0;o!==e;++o)a+=t,i[o].toArray(r,a)}return r}function Xt(i,e){if(i.length!==e.length)return!1;for(let t=0,n=i.length;t<n;t++)if(i[t]!==e[t])return!1;return!0}function qt(i,e){for(let t=0,n=e.length;t<n;t++)i[t]=e[t]}function ma(i,e){let t=oh[e];t===void 0&&(t=new Int32Array(e),oh[e]=t);for(let n=0;n!==e;++n)t[n]=i.allocateTextureUnit();return t}function U_(i,e){const t=this.cache;t[0]!==e&&(i.uniform1f(this.addr,e),t[0]=e)}function O_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Xt(t,e))return;i.uniform2fv(this.addr,e),qt(t,e)}}function F_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(i.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(Xt(t,e))return;i.uniform3fv(this.addr,e),qt(t,e)}}function B_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Xt(t,e))return;i.uniform4fv(this.addr,e),qt(t,e)}}function k_(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Xt(t,e))return;i.uniformMatrix2fv(this.addr,!1,e),qt(t,e)}else{if(Xt(t,n))return;lh.set(n),i.uniformMatrix2fv(this.addr,!1,lh),qt(t,n)}}function z_(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Xt(t,e))return;i.uniformMatrix3fv(this.addr,!1,e),qt(t,e)}else{if(Xt(t,n))return;ch.set(n),i.uniformMatrix3fv(this.addr,!1,ch),qt(t,n)}}function H_(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(Xt(t,e))return;i.uniformMatrix4fv(this.addr,!1,e),qt(t,e)}else{if(Xt(t,n))return;ah.set(n),i.uniformMatrix4fv(this.addr,!1,ah),qt(t,n)}}function V_(i,e){const t=this.cache;t[0]!==e&&(i.uniform1i(this.addr,e),t[0]=e)}function G_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Xt(t,e))return;i.uniform2iv(this.addr,e),qt(t,e)}}function W_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Xt(t,e))return;i.uniform3iv(this.addr,e),qt(t,e)}}function X_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Xt(t,e))return;i.uniform4iv(this.addr,e),qt(t,e)}}function q_(i,e){const t=this.cache;t[0]!==e&&(i.uniform1ui(this.addr,e),t[0]=e)}function Y_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Xt(t,e))return;i.uniform2uiv(this.addr,e),qt(t,e)}}function j_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Xt(t,e))return;i.uniform3uiv(this.addr,e),qt(t,e)}}function $_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Xt(t,e))return;i.uniform4uiv(this.addr,e),qt(t,e)}}function K_(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s);let r;this.type===i.SAMPLER_2D_SHADOW?(sh.compareFunction=Nf,r=sh):r=qf,t.setTexture2D(e||r,s)}function Z_(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture3D(e||jf,s)}function J_(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTextureCube(e||$f,s)}function Q_(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture2DArray(e||Yf,s)}function ex(i){switch(i){case 5126:return U_;case 35664:return O_;case 35665:return F_;case 35666:return B_;case 35674:return k_;case 35675:return z_;case 35676:return H_;case 5124:case 35670:return V_;case 35667:case 35671:return G_;case 35668:case 35672:return W_;case 35669:case 35673:return X_;case 5125:return q_;case 36294:return Y_;case 36295:return j_;case 36296:return $_;case 35678:case 36198:case 36298:case 36306:case 35682:return K_;case 35679:case 36299:case 36307:return Z_;case 35680:case 36300:case 36308:case 36293:return J_;case 36289:case 36303:case 36311:case 36292:return Q_}}function tx(i,e){i.uniform1fv(this.addr,e)}function nx(i,e){const t=lr(e,this.size,2);i.uniform2fv(this.addr,t)}function ix(i,e){const t=lr(e,this.size,3);i.uniform3fv(this.addr,t)}function sx(i,e){const t=lr(e,this.size,4);i.uniform4fv(this.addr,t)}function rx(i,e){const t=lr(e,this.size,4);i.uniformMatrix2fv(this.addr,!1,t)}function ox(i,e){const t=lr(e,this.size,9);i.uniformMatrix3fv(this.addr,!1,t)}function ax(i,e){const t=lr(e,this.size,16);i.uniformMatrix4fv(this.addr,!1,t)}function cx(i,e){i.uniform1iv(this.addr,e)}function lx(i,e){i.uniform2iv(this.addr,e)}function ux(i,e){i.uniform3iv(this.addr,e)}function hx(i,e){i.uniform4iv(this.addr,e)}function fx(i,e){i.uniform1uiv(this.addr,e)}function dx(i,e){i.uniform2uiv(this.addr,e)}function px(i,e){i.uniform3uiv(this.addr,e)}function mx(i,e){i.uniform4uiv(this.addr,e)}function gx(i,e,t){const n=this.cache,s=e.length,r=ma(t,s);Xt(n,r)||(i.uniform1iv(this.addr,r),qt(n,r));for(let o=0;o!==s;++o)t.setTexture2D(e[o]||qf,r[o])}function _x(i,e,t){const n=this.cache,s=e.length,r=ma(t,s);Xt(n,r)||(i.uniform1iv(this.addr,r),qt(n,r));for(let o=0;o!==s;++o)t.setTexture3D(e[o]||jf,r[o])}function xx(i,e,t){const n=this.cache,s=e.length,r=ma(t,s);Xt(n,r)||(i.uniform1iv(this.addr,r),qt(n,r));for(let o=0;o!==s;++o)t.setTextureCube(e[o]||$f,r[o])}function vx(i,e,t){const n=this.cache,s=e.length,r=ma(t,s);Xt(n,r)||(i.uniform1iv(this.addr,r),qt(n,r));for(let o=0;o!==s;++o)t.setTexture2DArray(e[o]||Yf,r[o])}function yx(i){switch(i){case 5126:return tx;case 35664:return nx;case 35665:return ix;case 35666:return sx;case 35674:return rx;case 35675:return ox;case 35676:return ax;case 5124:case 35670:return cx;case 35667:case 35671:return lx;case 35668:case 35672:return ux;case 35669:case 35673:return hx;case 5125:return fx;case 36294:return dx;case 36295:return px;case 36296:return mx;case 35678:case 36198:case 36298:case 36306:case 35682:return gx;case 35679:case 36299:case 36307:return _x;case 35680:case 36300:case 36308:case 36293:return xx;case 36289:case 36303:case 36311:case 36292:return vx}}class Mx{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=ex(t.type)}}class Sx{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=yx(t.type)}}class bx{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const s=this.seq;for(let r=0,o=s.length;r!==o;++r){const a=s[r];a.setValue(e,t[a.id],n)}}}const Qa=/(\w+)(\])?(\[|\.)?/g;function uh(i,e){i.seq.push(e),i.map[e.id]=e}function wx(i,e,t){const n=i.name,s=n.length;for(Qa.lastIndex=0;;){const r=Qa.exec(n),o=Qa.lastIndex;let a=r[1];const c=r[2]==="]",l=r[3];if(c&&(a=a|0),l===void 0||l==="["&&o+2===s){uh(t,l===void 0?new Mx(a,i,e):new Sx(a,i,e));break}else{let h=t.map[a];h===void 0&&(h=new bx(a),uh(t,h)),t=h}}}class Jo{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let s=0;s<n;++s){const r=e.getActiveUniform(t,s),o=e.getUniformLocation(t,r.name);wx(r,o,this)}}setValue(e,t,n,s){const r=this.map[t];r!==void 0&&r.setValue(e,n,s)}setOptional(e,t,n){const s=t[n];s!==void 0&&this.setValue(e,n,s)}static upload(e,t,n,s){for(let r=0,o=t.length;r!==o;++r){const a=t[r],c=n[a.id];c.needsUpdate!==!1&&a.setValue(e,c.value,s)}}static seqWithValue(e,t){const n=[];for(let s=0,r=e.length;s!==r;++s){const o=e[s];o.id in t&&n.push(o)}return n}}function hh(i,e,t){const n=i.createShader(e);return i.shaderSource(n,t),i.compileShader(n),n}const Ex=37297;let Tx=0;function Ax(i,e){const t=i.split(`
`),n=[],s=Math.max(e-6,0),r=Math.min(e+6,t.length);for(let o=s;o<r;o++){const a=o+1;n.push(`${a===e?">":" "} ${a}: ${t[o]}`)}return n.join(`
`)}const fh=new tt;function Rx(i){at._getMatrix(fh,at.workingColorSpace,i);const e=`mat3( ${fh.elements.map(t=>t.toFixed(4))} )`;switch(at.getTransfer(i)){case fa:return[e,"LinearTransferOETF"];case St:return[e,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",i),[e,"LinearTransferOETF"]}}function dh(i,e,t){const n=i.getShaderParameter(e,i.COMPILE_STATUS),s=i.getShaderInfoLog(e).trim();if(n&&s==="")return"";const r=/ERROR: 0:(\d+)/.exec(s);if(r){const o=parseInt(r[1]);return t.toUpperCase()+`

`+s+`

`+Ax(i.getShaderSource(e),o)}else return s}function Cx(i,e){const t=Rx(e);return[`vec4 ${i}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}function Px(i,e){let t;switch(e){case Pp:t="Linear";break;case Lp:t="Reinhard";break;case Ip:t="Cineon";break;case Dp:t="ACESFilmic";break;case Up:t="AgX";break;case Op:t="Neutral";break;case Np:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+i+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const To=new M;function Lx(){at.getLuminanceCoefficients(To);const i=To.x.toFixed(4),e=To.y.toFixed(4),t=To.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function Ix(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(Nr).join(`
`)}function Dx(i){const e=[];for(const t in i){const n=i[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function Nx(i,e){const t={},n=i.getProgramParameter(e,i.ACTIVE_ATTRIBUTES);for(let s=0;s<n;s++){const r=i.getActiveAttrib(e,s),o=r.name;let a=1;r.type===i.FLOAT_MAT2&&(a=2),r.type===i.FLOAT_MAT3&&(a=3),r.type===i.FLOAT_MAT4&&(a=4),t[o]={type:r.type,location:i.getAttribLocation(e,o),locationSize:a}}return t}function Nr(i){return i!==""}function ph(i,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function mh(i,e){return i.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const Ux=/^[ \t]*#include +<([\w\d./]+)>/gm;function _l(i){return i.replace(Ux,Fx)}const Ox=new Map;function Fx(i,e){let t=it[e];if(t===void 0){const n=Ox.get(e);if(n!==void 0)t=it[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return _l(t)}const Bx=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function gh(i){return i.replace(Bx,kx)}function kx(i,e,t,n){let s="";for(let r=parseInt(e);r<parseInt(t);r++)s+=n.replace(/\[\s*i\s*\]/g,"[ "+r+" ]").replace(/UNROLLED_LOOP_INDEX/g,r);return s}function _h(i){let e=`precision ${i.precision} float;
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
#define LOW_PRECISION`),e}function zx(i){let e="SHADOWMAP_TYPE_BASIC";return i.shadowMapType===vf?e="SHADOWMAP_TYPE_PCF":i.shadowMapType===lp?e="SHADOWMAP_TYPE_PCF_SOFT":i.shadowMapType===di&&(e="SHADOWMAP_TYPE_VSM"),e}function Hx(i){let e="ENVMAP_TYPE_CUBE";if(i.envMap)switch(i.envMapMode){case Zs:case Js:e="ENVMAP_TYPE_CUBE";break;case ha:e="ENVMAP_TYPE_CUBE_UV";break}return e}function Vx(i){let e="ENVMAP_MODE_REFLECTION";if(i.envMap)switch(i.envMapMode){case Js:e="ENVMAP_MODE_REFRACTION";break}return e}function Gx(i){let e="ENVMAP_BLENDING_NONE";if(i.envMap)switch(i.combine){case yf:e="ENVMAP_BLENDING_MULTIPLY";break;case Rp:e="ENVMAP_BLENDING_MIX";break;case Cp:e="ENVMAP_BLENDING_ADD";break}return e}function Wx(i){const e=i.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),112)),texelHeight:n,maxMip:t}}function Xx(i,e,t,n){const s=i.getContext(),r=t.defines;let o=t.vertexShader,a=t.fragmentShader;const c=zx(t),l=Hx(t),u=Vx(t),h=Gx(t),f=Wx(t),d=Ix(t),g=Dx(r),_=s.createProgram();let p,m,v=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g].filter(Nr).join(`
`),p.length>0&&(p+=`
`),m=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g].filter(Nr).join(`
`),m.length>0&&(m+=`
`)):(p=[_h(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+u:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+c:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(Nr).join(`
`),m=[_h(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,g,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+l:"",t.envMap?"#define "+u:"",t.envMap?"#define "+h:"",f?"#define CUBEUV_TEXEL_WIDTH "+f.texelWidth:"",f?"#define CUBEUV_TEXEL_HEIGHT "+f.texelHeight:"",f?"#define CUBEUV_MAX_MIP "+f.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+c:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==Gi?"#define TONE_MAPPING":"",t.toneMapping!==Gi?it.tonemapping_pars_fragment:"",t.toneMapping!==Gi?Px("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",it.colorspace_pars_fragment,Cx("linearToOutputTexel",t.outputColorSpace),Lx(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(Nr).join(`
`)),o=_l(o),o=ph(o,t),o=mh(o,t),a=_l(a),a=ph(a,t),a=mh(a,t),o=gh(o),a=gh(a),t.isRawShaderMaterial!==!0&&(v=`#version 300 es
`,p=[d,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+p,m=["#define varying in",t.glslVersion===Cu?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Cu?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+m);const y=v+p+o,x=v+m+a,P=hh(s,s.VERTEX_SHADER,y),A=hh(s,s.FRAGMENT_SHADER,x);s.attachShader(_,P),s.attachShader(_,A),t.index0AttributeName!==void 0?s.bindAttribLocation(_,0,t.index0AttributeName):t.morphTargets===!0&&s.bindAttribLocation(_,0,"position"),s.linkProgram(_);function E(I){if(i.debug.checkShaderErrors){const B=s.getProgramInfoLog(_).trim(),O=s.getShaderInfoLog(P).trim(),k=s.getShaderInfoLog(A).trim();let K=!0,W=!0;if(s.getProgramParameter(_,s.LINK_STATUS)===!1)if(K=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(s,_,P,A);else{const q=dh(s,P,"vertex"),V=dh(s,A,"fragment");console.error("THREE.WebGLProgram: Shader Error "+s.getError()+" - VALIDATE_STATUS "+s.getProgramParameter(_,s.VALIDATE_STATUS)+`

Material Name: `+I.name+`
Material Type: `+I.type+`

Program Info Log: `+B+`
`+q+`
`+V)}else B!==""?console.warn("THREE.WebGLProgram: Program Info Log:",B):(O===""||k==="")&&(W=!1);W&&(I.diagnostics={runnable:K,programLog:B,vertexShader:{log:O,prefix:p},fragmentShader:{log:k,prefix:m}})}s.deleteShader(P),s.deleteShader(A),R=new Jo(s,_),b=Nx(s,_)}let R;this.getUniforms=function(){return R===void 0&&E(this),R};let b;this.getAttributes=function(){return b===void 0&&E(this),b};let S=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return S===!1&&(S=s.getProgramParameter(_,Ex)),S},this.destroy=function(){n.releaseStatesOfProgram(this),s.deleteProgram(_),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=Tx++,this.cacheKey=e,this.usedTimes=1,this.program=_,this.vertexShader=P,this.fragmentShader=A,this}let qx=0;class Yx{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,s=this._getShaderStage(t),r=this._getShaderStage(n),o=this._getShaderCacheForMaterial(e);return o.has(s)===!1&&(o.add(s),s.usedTimes++),o.has(r)===!1&&(o.add(r),r.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new jx(e),t.set(e,n)),n}}class jx{constructor(e){this.id=qx++,this.code=e,this.usedTimes=0}}function $x(i,e,t,n,s,r,o){const a=new Bf,c=new Yx,l=new Set,u=[],h=s.logarithmicDepthBuffer,f=s.vertexTextures;let d=s.precision;const g={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function _(b){return l.add(b),b===0?"uv":`uv${b}`}function p(b,S,I,B,O){const k=B.fog,K=O.geometry,W=b.isMeshStandardMaterial?B.environment:null,q=(b.isMeshStandardMaterial?t:e).get(b.envMap||W),V=q&&q.mapping===ha?q.image.height:null,se=g[b.type];b.precision!==null&&(d=s.getMaxPrecision(b.precision),d!==b.precision&&console.warn("THREE.WebGLProgram.getParameters:",b.precision,"not supported, using",d,"instead."));const me=K.morphAttributes.position||K.morphAttributes.normal||K.morphAttributes.color,Se=me!==void 0?me.length:0;let Ze=0;K.morphAttributes.position!==void 0&&(Ze=1),K.morphAttributes.normal!==void 0&&(Ze=2),K.morphAttributes.color!==void 0&&(Ze=3);let pt,Z,le,Ie;if(se){const xt=jn[se];pt=xt.vertexShader,Z=xt.fragmentShader}else pt=b.vertexShader,Z=b.fragmentShader,c.update(b),le=c.getVertexShaderID(b),Ie=c.getFragmentShaderID(b);const fe=i.getRenderTarget(),He=i.state.buffers.depth.getReversed(),je=O.isInstancedMesh===!0,qe=O.isBatchedMesh===!0,ut=!!b.map,Q=!!b.matcap,ae=!!q,L=!!b.aoMap,Be=!!b.lightMap,ie=!!b.bumpMap,Ee=!!b.normalMap,de=!!b.displacementMap,We=!!b.emissiveMap,be=!!b.metalnessMap,C=!!b.roughnessMap,w=b.anisotropy>0,F=b.clearcoat>0,j=b.dispersion>0,ee=b.iridescence>0,$=b.sheen>0,Ne=b.transmission>0,_e=w&&!!b.anisotropyMap,we=F&&!!b.clearcoatMap,ot=F&&!!b.clearcoatNormalMap,re=F&&!!b.clearcoatRoughnessMap,Ce=ee&&!!b.iridescenceMap,Xe=ee&&!!b.iridescenceThicknessMap,Ye=$&&!!b.sheenColorMap,Pe=$&&!!b.sheenRoughnessMap,ct=!!b.specularMap,nt=!!b.specularColorMap,Tt=!!b.specularIntensityMap,D=Ne&&!!b.transmissionMap,xe=Ne&&!!b.thicknessMap,X=!!b.gradientMap,J=!!b.alphaMap,Me=b.alphaTest>0,ve=!!b.alphaHash,Qe=!!b.extensions;let Ot=Gi;b.toneMapped&&(fe===null||fe.isXRRenderTarget===!0)&&(Ot=i.toneMapping);const Jt={shaderID:se,shaderType:b.type,shaderName:b.name,vertexShader:pt,fragmentShader:Z,defines:b.defines,customVertexShaderID:le,customFragmentShaderID:Ie,isRawShaderMaterial:b.isRawShaderMaterial===!0,glslVersion:b.glslVersion,precision:d,batching:qe,batchingColor:qe&&O._colorsTexture!==null,instancing:je,instancingColor:je&&O.instanceColor!==null,instancingMorph:je&&O.morphTexture!==null,supportsVertexTextures:f,outputColorSpace:fe===null?i.outputColorSpace:fe.isXRRenderTarget===!0?fe.texture.colorSpace:an,alphaToCoverage:!!b.alphaToCoverage,map:ut,matcap:Q,envMap:ae,envMapMode:ae&&q.mapping,envMapCubeUVHeight:V,aoMap:L,lightMap:Be,bumpMap:ie,normalMap:Ee,displacementMap:f&&de,emissiveMap:We,normalMapObjectSpace:Ee&&b.normalMapType===Vp,normalMapTangentSpace:Ee&&b.normalMapType===Df,metalnessMap:be,roughnessMap:C,anisotropy:w,anisotropyMap:_e,clearcoat:F,clearcoatMap:we,clearcoatNormalMap:ot,clearcoatRoughnessMap:re,dispersion:j,iridescence:ee,iridescenceMap:Ce,iridescenceThicknessMap:Xe,sheen:$,sheenColorMap:Ye,sheenRoughnessMap:Pe,specularMap:ct,specularColorMap:nt,specularIntensityMap:Tt,transmission:Ne,transmissionMap:D,thicknessMap:xe,gradientMap:X,opaque:b.transparent===!1&&b.blending===Ws&&b.alphaToCoverage===!1,alphaMap:J,alphaTest:Me,alphaHash:ve,combine:b.combine,mapUv:ut&&_(b.map.channel),aoMapUv:L&&_(b.aoMap.channel),lightMapUv:Be&&_(b.lightMap.channel),bumpMapUv:ie&&_(b.bumpMap.channel),normalMapUv:Ee&&_(b.normalMap.channel),displacementMapUv:de&&_(b.displacementMap.channel),emissiveMapUv:We&&_(b.emissiveMap.channel),metalnessMapUv:be&&_(b.metalnessMap.channel),roughnessMapUv:C&&_(b.roughnessMap.channel),anisotropyMapUv:_e&&_(b.anisotropyMap.channel),clearcoatMapUv:we&&_(b.clearcoatMap.channel),clearcoatNormalMapUv:ot&&_(b.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:re&&_(b.clearcoatRoughnessMap.channel),iridescenceMapUv:Ce&&_(b.iridescenceMap.channel),iridescenceThicknessMapUv:Xe&&_(b.iridescenceThicknessMap.channel),sheenColorMapUv:Ye&&_(b.sheenColorMap.channel),sheenRoughnessMapUv:Pe&&_(b.sheenRoughnessMap.channel),specularMapUv:ct&&_(b.specularMap.channel),specularColorMapUv:nt&&_(b.specularColorMap.channel),specularIntensityMapUv:Tt&&_(b.specularIntensityMap.channel),transmissionMapUv:D&&_(b.transmissionMap.channel),thicknessMapUv:xe&&_(b.thicknessMap.channel),alphaMapUv:J&&_(b.alphaMap.channel),vertexTangents:!!K.attributes.tangent&&(Ee||w),vertexColors:b.vertexColors,vertexAlphas:b.vertexColors===!0&&!!K.attributes.color&&K.attributes.color.itemSize===4,pointsUvs:O.isPoints===!0&&!!K.attributes.uv&&(ut||J),fog:!!k,useFog:b.fog===!0,fogExp2:!!k&&k.isFogExp2,flatShading:b.flatShading===!0,sizeAttenuation:b.sizeAttenuation===!0,logarithmicDepthBuffer:h,reverseDepthBuffer:He,skinning:O.isSkinnedMesh===!0,morphTargets:K.morphAttributes.position!==void 0,morphNormals:K.morphAttributes.normal!==void 0,morphColors:K.morphAttributes.color!==void 0,morphTargetsCount:Se,morphTextureStride:Ze,numDirLights:S.directional.length,numPointLights:S.point.length,numSpotLights:S.spot.length,numSpotLightMaps:S.spotLightMap.length,numRectAreaLights:S.rectArea.length,numHemiLights:S.hemi.length,numDirLightShadows:S.directionalShadowMap.length,numPointLightShadows:S.pointShadowMap.length,numSpotLightShadows:S.spotShadowMap.length,numSpotLightShadowsWithMaps:S.numSpotLightShadowsWithMaps,numLightProbes:S.numLightProbes,numClippingPlanes:o.numPlanes,numClipIntersection:o.numIntersection,dithering:b.dithering,shadowMapEnabled:i.shadowMap.enabled&&I.length>0,shadowMapType:i.shadowMap.type,toneMapping:Ot,decodeVideoTexture:ut&&b.map.isVideoTexture===!0&&at.getTransfer(b.map.colorSpace)===St,decodeVideoTextureEmissive:We&&b.emissiveMap.isVideoTexture===!0&&at.getTransfer(b.emissiveMap.colorSpace)===St,premultipliedAlpha:b.premultipliedAlpha,doubleSided:b.side===Mn,flipSided:b.side===fn,useDepthPacking:b.depthPacking>=0,depthPacking:b.depthPacking||0,index0AttributeName:b.index0AttributeName,extensionClipCullDistance:Qe&&b.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(Qe&&b.extensions.multiDraw===!0||qe)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:b.customProgramCacheKey()};return Jt.vertexUv1s=l.has(1),Jt.vertexUv2s=l.has(2),Jt.vertexUv3s=l.has(3),l.clear(),Jt}function m(b){const S=[];if(b.shaderID?S.push(b.shaderID):(S.push(b.customVertexShaderID),S.push(b.customFragmentShaderID)),b.defines!==void 0)for(const I in b.defines)S.push(I),S.push(b.defines[I]);return b.isRawShaderMaterial===!1&&(v(S,b),y(S,b),S.push(i.outputColorSpace)),S.push(b.customProgramCacheKey),S.join()}function v(b,S){b.push(S.precision),b.push(S.outputColorSpace),b.push(S.envMapMode),b.push(S.envMapCubeUVHeight),b.push(S.mapUv),b.push(S.alphaMapUv),b.push(S.lightMapUv),b.push(S.aoMapUv),b.push(S.bumpMapUv),b.push(S.normalMapUv),b.push(S.displacementMapUv),b.push(S.emissiveMapUv),b.push(S.metalnessMapUv),b.push(S.roughnessMapUv),b.push(S.anisotropyMapUv),b.push(S.clearcoatMapUv),b.push(S.clearcoatNormalMapUv),b.push(S.clearcoatRoughnessMapUv),b.push(S.iridescenceMapUv),b.push(S.iridescenceThicknessMapUv),b.push(S.sheenColorMapUv),b.push(S.sheenRoughnessMapUv),b.push(S.specularMapUv),b.push(S.specularColorMapUv),b.push(S.specularIntensityMapUv),b.push(S.transmissionMapUv),b.push(S.thicknessMapUv),b.push(S.combine),b.push(S.fogExp2),b.push(S.sizeAttenuation),b.push(S.morphTargetsCount),b.push(S.morphAttributeCount),b.push(S.numDirLights),b.push(S.numPointLights),b.push(S.numSpotLights),b.push(S.numSpotLightMaps),b.push(S.numHemiLights),b.push(S.numRectAreaLights),b.push(S.numDirLightShadows),b.push(S.numPointLightShadows),b.push(S.numSpotLightShadows),b.push(S.numSpotLightShadowsWithMaps),b.push(S.numLightProbes),b.push(S.shadowMapType),b.push(S.toneMapping),b.push(S.numClippingPlanes),b.push(S.numClipIntersection),b.push(S.depthPacking)}function y(b,S){a.disableAll(),S.supportsVertexTextures&&a.enable(0),S.instancing&&a.enable(1),S.instancingColor&&a.enable(2),S.instancingMorph&&a.enable(3),S.matcap&&a.enable(4),S.envMap&&a.enable(5),S.normalMapObjectSpace&&a.enable(6),S.normalMapTangentSpace&&a.enable(7),S.clearcoat&&a.enable(8),S.iridescence&&a.enable(9),S.alphaTest&&a.enable(10),S.vertexColors&&a.enable(11),S.vertexAlphas&&a.enable(12),S.vertexUv1s&&a.enable(13),S.vertexUv2s&&a.enable(14),S.vertexUv3s&&a.enable(15),S.vertexTangents&&a.enable(16),S.anisotropy&&a.enable(17),S.alphaHash&&a.enable(18),S.batching&&a.enable(19),S.dispersion&&a.enable(20),S.batchingColor&&a.enable(21),b.push(a.mask),a.disableAll(),S.fog&&a.enable(0),S.useFog&&a.enable(1),S.flatShading&&a.enable(2),S.logarithmicDepthBuffer&&a.enable(3),S.reverseDepthBuffer&&a.enable(4),S.skinning&&a.enable(5),S.morphTargets&&a.enable(6),S.morphNormals&&a.enable(7),S.morphColors&&a.enable(8),S.premultipliedAlpha&&a.enable(9),S.shadowMapEnabled&&a.enable(10),S.doubleSided&&a.enable(11),S.flipSided&&a.enable(12),S.useDepthPacking&&a.enable(13),S.dithering&&a.enable(14),S.transmission&&a.enable(15),S.sheen&&a.enable(16),S.opaque&&a.enable(17),S.pointsUvs&&a.enable(18),S.decodeVideoTexture&&a.enable(19),S.decodeVideoTextureEmissive&&a.enable(20),S.alphaToCoverage&&a.enable(21),b.push(a.mask)}function x(b){const S=g[b.type];let I;if(S){const B=jn[S];I=Im.clone(B.uniforms)}else I=b.uniforms;return I}function P(b,S){let I;for(let B=0,O=u.length;B<O;B++){const k=u[B];if(k.cacheKey===S){I=k,++I.usedTimes;break}}return I===void 0&&(I=new Xx(i,S,b,r),u.push(I)),I}function A(b){if(--b.usedTimes===0){const S=u.indexOf(b);u[S]=u[u.length-1],u.pop(),b.destroy()}}function E(b){c.remove(b)}function R(){c.dispose()}return{getParameters:p,getProgramCacheKey:m,getUniforms:x,acquireProgram:P,releaseProgram:A,releaseShaderCache:E,programs:u,dispose:R}}function Kx(){let i=new WeakMap;function e(o){return i.has(o)}function t(o){let a=i.get(o);return a===void 0&&(a={},i.set(o,a)),a}function n(o){i.delete(o)}function s(o,a,c){i.get(o)[a]=c}function r(){i=new WeakMap}return{has:e,get:t,remove:n,update:s,dispose:r}}function Zx(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.material.id!==e.material.id?i.material.id-e.material.id:i.z!==e.z?i.z-e.z:i.id-e.id}function xh(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.z!==e.z?e.z-i.z:i.id-e.id}function vh(){const i=[];let e=0;const t=[],n=[],s=[];function r(){e=0,t.length=0,n.length=0,s.length=0}function o(h,f,d,g,_,p){let m=i[e];return m===void 0?(m={id:h.id,object:h,geometry:f,material:d,groupOrder:g,renderOrder:h.renderOrder,z:_,group:p},i[e]=m):(m.id=h.id,m.object=h,m.geometry=f,m.material=d,m.groupOrder=g,m.renderOrder=h.renderOrder,m.z=_,m.group=p),e++,m}function a(h,f,d,g,_,p){const m=o(h,f,d,g,_,p);d.transmission>0?n.push(m):d.transparent===!0?s.push(m):t.push(m)}function c(h,f,d,g,_,p){const m=o(h,f,d,g,_,p);d.transmission>0?n.unshift(m):d.transparent===!0?s.unshift(m):t.unshift(m)}function l(h,f){t.length>1&&t.sort(h||Zx),n.length>1&&n.sort(f||xh),s.length>1&&s.sort(f||xh)}function u(){for(let h=e,f=i.length;h<f;h++){const d=i[h];if(d.id===null)break;d.id=null,d.object=null,d.geometry=null,d.material=null,d.group=null}}return{opaque:t,transmissive:n,transparent:s,init:r,push:a,unshift:c,finish:u,sort:l}}function Jx(){let i=new WeakMap;function e(n,s){const r=i.get(n);let o;return r===void 0?(o=new vh,i.set(n,[o])):s>=r.length?(o=new vh,r.push(o)):o=r[s],o}function t(){i=new WeakMap}return{get:e,dispose:t}}function Qx(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new M,color:new ze};break;case"SpotLight":t={position:new M,direction:new M,color:new ze,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new M,color:new ze,distance:0,decay:0};break;case"HemisphereLight":t={direction:new M,skyColor:new ze,groundColor:new ze};break;case"RectAreaLight":t={color:new ze,position:new M,halfWidth:new M,halfHeight:new M};break}return i[e.id]=t,t}}}function ev(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new te};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new te};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new te,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[e.id]=t,t}}}let tv=0;function nv(i,e){return(e.castShadow?2:0)-(i.castShadow?2:0)+(e.map?1:0)-(i.map?1:0)}function iv(i){const e=new Qx,t=ev(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let l=0;l<9;l++)n.probe.push(new M);const s=new M,r=new Le,o=new Le;function a(l){let u=0,h=0,f=0;for(let b=0;b<9;b++)n.probe[b].set(0,0,0);let d=0,g=0,_=0,p=0,m=0,v=0,y=0,x=0,P=0,A=0,E=0;l.sort(nv);for(let b=0,S=l.length;b<S;b++){const I=l[b],B=I.color,O=I.intensity,k=I.distance,K=I.shadow&&I.shadow.map?I.shadow.map.texture:null;if(I.isAmbientLight)u+=B.r*O,h+=B.g*O,f+=B.b*O;else if(I.isLightProbe){for(let W=0;W<9;W++)n.probe[W].addScaledVector(I.sh.coefficients[W],O);E++}else if(I.isDirectionalLight){const W=e.get(I);if(W.color.copy(I.color).multiplyScalar(I.intensity),I.castShadow){const q=I.shadow,V=t.get(I);V.shadowIntensity=q.intensity,V.shadowBias=q.bias,V.shadowNormalBias=q.normalBias,V.shadowRadius=q.radius,V.shadowMapSize=q.mapSize,n.directionalShadow[d]=V,n.directionalShadowMap[d]=K,n.directionalShadowMatrix[d]=I.shadow.matrix,v++}n.directional[d]=W,d++}else if(I.isSpotLight){const W=e.get(I);W.position.setFromMatrixPosition(I.matrixWorld),W.color.copy(B).multiplyScalar(O),W.distance=k,W.coneCos=Math.cos(I.angle),W.penumbraCos=Math.cos(I.angle*(1-I.penumbra)),W.decay=I.decay,n.spot[_]=W;const q=I.shadow;if(I.map&&(n.spotLightMap[P]=I.map,P++,q.updateMatrices(I),I.castShadow&&A++),n.spotLightMatrix[_]=q.matrix,I.castShadow){const V=t.get(I);V.shadowIntensity=q.intensity,V.shadowBias=q.bias,V.shadowNormalBias=q.normalBias,V.shadowRadius=q.radius,V.shadowMapSize=q.mapSize,n.spotShadow[_]=V,n.spotShadowMap[_]=K,x++}_++}else if(I.isRectAreaLight){const W=e.get(I);W.color.copy(B).multiplyScalar(O),W.halfWidth.set(I.width*.5,0,0),W.halfHeight.set(0,I.height*.5,0),n.rectArea[p]=W,p++}else if(I.isPointLight){const W=e.get(I);if(W.color.copy(I.color).multiplyScalar(I.intensity),W.distance=I.distance,W.decay=I.decay,I.castShadow){const q=I.shadow,V=t.get(I);V.shadowIntensity=q.intensity,V.shadowBias=q.bias,V.shadowNormalBias=q.normalBias,V.shadowRadius=q.radius,V.shadowMapSize=q.mapSize,V.shadowCameraNear=q.camera.near,V.shadowCameraFar=q.camera.far,n.pointShadow[g]=V,n.pointShadowMap[g]=K,n.pointShadowMatrix[g]=I.shadow.matrix,y++}n.point[g]=W,g++}else if(I.isHemisphereLight){const W=e.get(I);W.skyColor.copy(I.color).multiplyScalar(O),W.groundColor.copy(I.groundColor).multiplyScalar(O),n.hemi[m]=W,m++}}p>0&&(i.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=ge.LTC_FLOAT_1,n.rectAreaLTC2=ge.LTC_FLOAT_2):(n.rectAreaLTC1=ge.LTC_HALF_1,n.rectAreaLTC2=ge.LTC_HALF_2)),n.ambient[0]=u,n.ambient[1]=h,n.ambient[2]=f;const R=n.hash;(R.directionalLength!==d||R.pointLength!==g||R.spotLength!==_||R.rectAreaLength!==p||R.hemiLength!==m||R.numDirectionalShadows!==v||R.numPointShadows!==y||R.numSpotShadows!==x||R.numSpotMaps!==P||R.numLightProbes!==E)&&(n.directional.length=d,n.spot.length=_,n.rectArea.length=p,n.point.length=g,n.hemi.length=m,n.directionalShadow.length=v,n.directionalShadowMap.length=v,n.pointShadow.length=y,n.pointShadowMap.length=y,n.spotShadow.length=x,n.spotShadowMap.length=x,n.directionalShadowMatrix.length=v,n.pointShadowMatrix.length=y,n.spotLightMatrix.length=x+P-A,n.spotLightMap.length=P,n.numSpotLightShadowsWithMaps=A,n.numLightProbes=E,R.directionalLength=d,R.pointLength=g,R.spotLength=_,R.rectAreaLength=p,R.hemiLength=m,R.numDirectionalShadows=v,R.numPointShadows=y,R.numSpotShadows=x,R.numSpotMaps=P,R.numLightProbes=E,n.version=tv++)}function c(l,u){let h=0,f=0,d=0,g=0,_=0;const p=u.matrixWorldInverse;for(let m=0,v=l.length;m<v;m++){const y=l[m];if(y.isDirectionalLight){const x=n.directional[h];x.direction.setFromMatrixPosition(y.matrixWorld),s.setFromMatrixPosition(y.target.matrixWorld),x.direction.sub(s),x.direction.transformDirection(p),h++}else if(y.isSpotLight){const x=n.spot[d];x.position.setFromMatrixPosition(y.matrixWorld),x.position.applyMatrix4(p),x.direction.setFromMatrixPosition(y.matrixWorld),s.setFromMatrixPosition(y.target.matrixWorld),x.direction.sub(s),x.direction.transformDirection(p),d++}else if(y.isRectAreaLight){const x=n.rectArea[g];x.position.setFromMatrixPosition(y.matrixWorld),x.position.applyMatrix4(p),o.identity(),r.copy(y.matrixWorld),r.premultiply(p),o.extractRotation(r),x.halfWidth.set(y.width*.5,0,0),x.halfHeight.set(0,y.height*.5,0),x.halfWidth.applyMatrix4(o),x.halfHeight.applyMatrix4(o),g++}else if(y.isPointLight){const x=n.point[f];x.position.setFromMatrixPosition(y.matrixWorld),x.position.applyMatrix4(p),f++}else if(y.isHemisphereLight){const x=n.hemi[_];x.direction.setFromMatrixPosition(y.matrixWorld),x.direction.transformDirection(p),_++}}}return{setup:a,setupView:c,state:n}}function yh(i){const e=new iv(i),t=[],n=[];function s(u){l.camera=u,t.length=0,n.length=0}function r(u){t.push(u)}function o(u){n.push(u)}function a(){e.setup(t)}function c(u){e.setupView(t,u)}const l={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:s,state:l,setupLights:a,setupLightsView:c,pushLight:r,pushShadow:o}}function sv(i){let e=new WeakMap;function t(s,r=0){const o=e.get(s);let a;return o===void 0?(a=new yh(i),e.set(s,[a])):r>=o.length?(a=new yh(i),o.push(a)):a=o[r],a}function n(){e=new WeakMap}return{get:t,dispose:n}}class rv extends Kn{static get type(){return"MeshDepthMaterial"}constructor(e){super(),this.isMeshDepthMaterial=!0,this.depthPacking=zp,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class ov extends Kn{static get type(){return"MeshDistanceMaterial"}constructor(e){super(),this.isMeshDistanceMaterial=!0,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const av=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,cv=`uniform sampler2D shadow_pass;
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
}`;function lv(i,e,t){let n=new Gl;const s=new te,r=new te,o=new dt,a=new rv({depthPacking:Hp}),c=new ov,l={},u=t.maxTextureSize,h={[vi]:fn,[fn]:vi,[Mn]:Mn},f=new Zn({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new te},radius:{value:4}},vertexShader:av,fragmentShader:cv}),d=f.clone();d.defines.HORIZONTAL_PASS=1;const g=new zt;g.setAttribute("position",new $t(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const _=new kt(g,f),p=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=vf;let m=this.type;this.render=function(A,E,R){if(p.enabled===!1||p.autoUpdate===!1&&p.needsUpdate===!1||A.length===0)return;const b=i.getRenderTarget(),S=i.getActiveCubeFace(),I=i.getActiveMipmapLevel(),B=i.state;B.setBlending(Vi),B.buffers.color.setClear(1,1,1,1),B.buffers.depth.setTest(!0),B.setScissorTest(!1);const O=m!==di&&this.type===di,k=m===di&&this.type!==di;for(let K=0,W=A.length;K<W;K++){const q=A[K],V=q.shadow;if(V===void 0){console.warn("THREE.WebGLShadowMap:",q,"has no shadow.");continue}if(V.autoUpdate===!1&&V.needsUpdate===!1)continue;s.copy(V.mapSize);const se=V.getFrameExtents();if(s.multiply(se),r.copy(V.mapSize),(s.x>u||s.y>u)&&(s.x>u&&(r.x=Math.floor(u/se.x),s.x=r.x*se.x,V.mapSize.x=r.x),s.y>u&&(r.y=Math.floor(u/se.y),s.y=r.y*se.y,V.mapSize.y=r.y)),V.map===null||O===!0||k===!0){const Se=this.type!==di?{minFilter:dn,magFilter:dn}:{};V.map!==null&&V.map.dispose(),V.map=new gs(s.x,s.y,Se),V.map.texture.name=q.name+".shadowMap",V.camera.updateProjectionMatrix()}i.setRenderTarget(V.map),i.clear();const me=V.getViewportCount();for(let Se=0;Se<me;Se++){const Ze=V.getViewport(Se);o.set(r.x*Ze.x,r.y*Ze.y,r.x*Ze.z,r.y*Ze.w),B.viewport(o),V.updateMatrices(q,Se),n=V.getFrustum(),x(E,R,V.camera,q,this.type)}V.isPointLightShadow!==!0&&this.type===di&&v(V,R),V.needsUpdate=!1}m=this.type,p.needsUpdate=!1,i.setRenderTarget(b,S,I)};function v(A,E){const R=e.update(_);f.defines.VSM_SAMPLES!==A.blurSamples&&(f.defines.VSM_SAMPLES=A.blurSamples,d.defines.VSM_SAMPLES=A.blurSamples,f.needsUpdate=!0,d.needsUpdate=!0),A.mapPass===null&&(A.mapPass=new gs(s.x,s.y)),f.uniforms.shadow_pass.value=A.map.texture,f.uniforms.resolution.value=A.mapSize,f.uniforms.radius.value=A.radius,i.setRenderTarget(A.mapPass),i.clear(),i.renderBufferDirect(E,null,R,f,_,null),d.uniforms.shadow_pass.value=A.mapPass.texture,d.uniforms.resolution.value=A.mapSize,d.uniforms.radius.value=A.radius,i.setRenderTarget(A.map),i.clear(),i.renderBufferDirect(E,null,R,d,_,null)}function y(A,E,R,b){let S=null;const I=R.isPointLight===!0?A.customDistanceMaterial:A.customDepthMaterial;if(I!==void 0)S=I;else if(S=R.isPointLight===!0?c:a,i.localClippingEnabled&&E.clipShadows===!0&&Array.isArray(E.clippingPlanes)&&E.clippingPlanes.length!==0||E.displacementMap&&E.displacementScale!==0||E.alphaMap&&E.alphaTest>0||E.map&&E.alphaTest>0){const B=S.uuid,O=E.uuid;let k=l[B];k===void 0&&(k={},l[B]=k);let K=k[O];K===void 0&&(K=S.clone(),k[O]=K,E.addEventListener("dispose",P)),S=K}if(S.visible=E.visible,S.wireframe=E.wireframe,b===di?S.side=E.shadowSide!==null?E.shadowSide:E.side:S.side=E.shadowSide!==null?E.shadowSide:h[E.side],S.alphaMap=E.alphaMap,S.alphaTest=E.alphaTest,S.map=E.map,S.clipShadows=E.clipShadows,S.clippingPlanes=E.clippingPlanes,S.clipIntersection=E.clipIntersection,S.displacementMap=E.displacementMap,S.displacementScale=E.displacementScale,S.displacementBias=E.displacementBias,S.wireframeLinewidth=E.wireframeLinewidth,S.linewidth=E.linewidth,R.isPointLight===!0&&S.isMeshDistanceMaterial===!0){const B=i.properties.get(S);B.light=R}return S}function x(A,E,R,b,S){if(A.visible===!1)return;if(A.layers.test(E.layers)&&(A.isMesh||A.isLine||A.isPoints)&&(A.castShadow||A.receiveShadow&&S===di)&&(!A.frustumCulled||n.intersectsObject(A))){A.modelViewMatrix.multiplyMatrices(R.matrixWorldInverse,A.matrixWorld);const O=e.update(A),k=A.material;if(Array.isArray(k)){const K=O.groups;for(let W=0,q=K.length;W<q;W++){const V=K[W],se=k[V.materialIndex];if(se&&se.visible){const me=y(A,se,b,S);A.onBeforeShadow(i,A,E,R,O,me,V),i.renderBufferDirect(R,null,O,me,A,V),A.onAfterShadow(i,A,E,R,O,me,V)}}}else if(k.visible){const K=y(A,k,b,S);A.onBeforeShadow(i,A,E,R,O,K,null),i.renderBufferDirect(R,null,O,K,A,null),A.onAfterShadow(i,A,E,R,O,K,null)}}const B=A.children;for(let O=0,k=B.length;O<k;O++)x(B[O],E,R,b,S)}function P(A){A.target.removeEventListener("dispose",P);for(const R in l){const b=l[R],S=A.target.uuid;S in b&&(b[S].dispose(),delete b[S])}}}const uv={[Nc]:Uc,[Oc]:kc,[Fc]:zc,[Ks]:Bc,[Uc]:Nc,[kc]:Oc,[zc]:Fc,[Bc]:Ks};function hv(i,e){function t(){let D=!1;const xe=new dt;let X=null;const J=new dt(0,0,0,0);return{setMask:function(Me){X!==Me&&!D&&(i.colorMask(Me,Me,Me,Me),X=Me)},setLocked:function(Me){D=Me},setClear:function(Me,ve,Qe,Ot,Jt){Jt===!0&&(Me*=Ot,ve*=Ot,Qe*=Ot),xe.set(Me,ve,Qe,Ot),J.equals(xe)===!1&&(i.clearColor(Me,ve,Qe,Ot),J.copy(xe))},reset:function(){D=!1,X=null,J.set(-1,0,0,0)}}}function n(){let D=!1,xe=!1,X=null,J=null,Me=null;return{setReversed:function(ve){if(xe!==ve){const Qe=e.get("EXT_clip_control");xe?Qe.clipControlEXT(Qe.LOWER_LEFT_EXT,Qe.ZERO_TO_ONE_EXT):Qe.clipControlEXT(Qe.LOWER_LEFT_EXT,Qe.NEGATIVE_ONE_TO_ONE_EXT);const Ot=Me;Me=null,this.setClear(Ot)}xe=ve},getReversed:function(){return xe},setTest:function(ve){ve?fe(i.DEPTH_TEST):He(i.DEPTH_TEST)},setMask:function(ve){X!==ve&&!D&&(i.depthMask(ve),X=ve)},setFunc:function(ve){if(xe&&(ve=uv[ve]),J!==ve){switch(ve){case Nc:i.depthFunc(i.NEVER);break;case Uc:i.depthFunc(i.ALWAYS);break;case Oc:i.depthFunc(i.LESS);break;case Ks:i.depthFunc(i.LEQUAL);break;case Fc:i.depthFunc(i.EQUAL);break;case Bc:i.depthFunc(i.GEQUAL);break;case kc:i.depthFunc(i.GREATER);break;case zc:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}J=ve}},setLocked:function(ve){D=ve},setClear:function(ve){Me!==ve&&(xe&&(ve=1-ve),i.clearDepth(ve),Me=ve)},reset:function(){D=!1,X=null,J=null,Me=null,xe=!1}}}function s(){let D=!1,xe=null,X=null,J=null,Me=null,ve=null,Qe=null,Ot=null,Jt=null;return{setTest:function(xt){D||(xt?fe(i.STENCIL_TEST):He(i.STENCIL_TEST))},setMask:function(xt){xe!==xt&&!D&&(i.stencilMask(xt),xe=xt)},setFunc:function(xt,Bn,si){(X!==xt||J!==Bn||Me!==si)&&(i.stencilFunc(xt,Bn,si),X=xt,J=Bn,Me=si)},setOp:function(xt,Bn,si){(ve!==xt||Qe!==Bn||Ot!==si)&&(i.stencilOp(xt,Bn,si),ve=xt,Qe=Bn,Ot=si)},setLocked:function(xt){D=xt},setClear:function(xt){Jt!==xt&&(i.clearStencil(xt),Jt=xt)},reset:function(){D=!1,xe=null,X=null,J=null,Me=null,ve=null,Qe=null,Ot=null,Jt=null}}}const r=new t,o=new n,a=new s,c=new WeakMap,l=new WeakMap;let u={},h={},f=new WeakMap,d=[],g=null,_=!1,p=null,m=null,v=null,y=null,x=null,P=null,A=null,E=new ze(0,0,0),R=0,b=!1,S=null,I=null,B=null,O=null,k=null;const K=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let W=!1,q=0;const V=i.getParameter(i.VERSION);V.indexOf("WebGL")!==-1?(q=parseFloat(/^WebGL (\d)/.exec(V)[1]),W=q>=1):V.indexOf("OpenGL ES")!==-1&&(q=parseFloat(/^OpenGL ES (\d)/.exec(V)[1]),W=q>=2);let se=null,me={};const Se=i.getParameter(i.SCISSOR_BOX),Ze=i.getParameter(i.VIEWPORT),pt=new dt().fromArray(Se),Z=new dt().fromArray(Ze);function le(D,xe,X,J){const Me=new Uint8Array(4),ve=i.createTexture();i.bindTexture(D,ve),i.texParameteri(D,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(D,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let Qe=0;Qe<X;Qe++)D===i.TEXTURE_3D||D===i.TEXTURE_2D_ARRAY?i.texImage3D(xe,0,i.RGBA,1,1,J,0,i.RGBA,i.UNSIGNED_BYTE,Me):i.texImage2D(xe+Qe,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,Me);return ve}const Ie={};Ie[i.TEXTURE_2D]=le(i.TEXTURE_2D,i.TEXTURE_2D,1),Ie[i.TEXTURE_CUBE_MAP]=le(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),Ie[i.TEXTURE_2D_ARRAY]=le(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),Ie[i.TEXTURE_3D]=le(i.TEXTURE_3D,i.TEXTURE_3D,1,1),r.setClear(0,0,0,1),o.setClear(1),a.setClear(0),fe(i.DEPTH_TEST),o.setFunc(Ks),ie(!1),Ee(yu),fe(i.CULL_FACE),L(Vi);function fe(D){u[D]!==!0&&(i.enable(D),u[D]=!0)}function He(D){u[D]!==!1&&(i.disable(D),u[D]=!1)}function je(D,xe){return h[D]!==xe?(i.bindFramebuffer(D,xe),h[D]=xe,D===i.DRAW_FRAMEBUFFER&&(h[i.FRAMEBUFFER]=xe),D===i.FRAMEBUFFER&&(h[i.DRAW_FRAMEBUFFER]=xe),!0):!1}function qe(D,xe){let X=d,J=!1;if(D){X=f.get(xe),X===void 0&&(X=[],f.set(xe,X));const Me=D.textures;if(X.length!==Me.length||X[0]!==i.COLOR_ATTACHMENT0){for(let ve=0,Qe=Me.length;ve<Qe;ve++)X[ve]=i.COLOR_ATTACHMENT0+ve;X.length=Me.length,J=!0}}else X[0]!==i.BACK&&(X[0]=i.BACK,J=!0);J&&i.drawBuffers(X)}function ut(D){return g!==D?(i.useProgram(D),g=D,!0):!1}const Q={[fs]:i.FUNC_ADD,[hp]:i.FUNC_SUBTRACT,[fp]:i.FUNC_REVERSE_SUBTRACT};Q[dp]=i.MIN,Q[pp]=i.MAX;const ae={[mp]:i.ZERO,[gp]:i.ONE,[_p]:i.SRC_COLOR,[Ic]:i.SRC_ALPHA,[bp]:i.SRC_ALPHA_SATURATE,[Mp]:i.DST_COLOR,[vp]:i.DST_ALPHA,[xp]:i.ONE_MINUS_SRC_COLOR,[Dc]:i.ONE_MINUS_SRC_ALPHA,[Sp]:i.ONE_MINUS_DST_COLOR,[yp]:i.ONE_MINUS_DST_ALPHA,[wp]:i.CONSTANT_COLOR,[Ep]:i.ONE_MINUS_CONSTANT_COLOR,[Tp]:i.CONSTANT_ALPHA,[Ap]:i.ONE_MINUS_CONSTANT_ALPHA};function L(D,xe,X,J,Me,ve,Qe,Ot,Jt,xt){if(D===Vi){_===!0&&(He(i.BLEND),_=!1);return}if(_===!1&&(fe(i.BLEND),_=!0),D!==up){if(D!==p||xt!==b){if((m!==fs||x!==fs)&&(i.blendEquation(i.FUNC_ADD),m=fs,x=fs),xt)switch(D){case Ws:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Mu:i.blendFunc(i.ONE,i.ONE);break;case Su:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case bu:i.blendFuncSeparate(i.ZERO,i.SRC_COLOR,i.ZERO,i.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",D);break}else switch(D){case Ws:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Mu:i.blendFunc(i.SRC_ALPHA,i.ONE);break;case Su:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case bu:i.blendFunc(i.ZERO,i.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",D);break}v=null,y=null,P=null,A=null,E.set(0,0,0),R=0,p=D,b=xt}return}Me=Me||xe,ve=ve||X,Qe=Qe||J,(xe!==m||Me!==x)&&(i.blendEquationSeparate(Q[xe],Q[Me]),m=xe,x=Me),(X!==v||J!==y||ve!==P||Qe!==A)&&(i.blendFuncSeparate(ae[X],ae[J],ae[ve],ae[Qe]),v=X,y=J,P=ve,A=Qe),(Ot.equals(E)===!1||Jt!==R)&&(i.blendColor(Ot.r,Ot.g,Ot.b,Jt),E.copy(Ot),R=Jt),p=D,b=!1}function Be(D,xe){D.side===Mn?He(i.CULL_FACE):fe(i.CULL_FACE);let X=D.side===fn;xe&&(X=!X),ie(X),D.blending===Ws&&D.transparent===!1?L(Vi):L(D.blending,D.blendEquation,D.blendSrc,D.blendDst,D.blendEquationAlpha,D.blendSrcAlpha,D.blendDstAlpha,D.blendColor,D.blendAlpha,D.premultipliedAlpha),o.setFunc(D.depthFunc),o.setTest(D.depthTest),o.setMask(D.depthWrite),r.setMask(D.colorWrite);const J=D.stencilWrite;a.setTest(J),J&&(a.setMask(D.stencilWriteMask),a.setFunc(D.stencilFunc,D.stencilRef,D.stencilFuncMask),a.setOp(D.stencilFail,D.stencilZFail,D.stencilZPass)),We(D.polygonOffset,D.polygonOffsetFactor,D.polygonOffsetUnits),D.alphaToCoverage===!0?fe(i.SAMPLE_ALPHA_TO_COVERAGE):He(i.SAMPLE_ALPHA_TO_COVERAGE)}function ie(D){S!==D&&(D?i.frontFace(i.CW):i.frontFace(i.CCW),S=D)}function Ee(D){D!==ap?(fe(i.CULL_FACE),D!==I&&(D===yu?i.cullFace(i.BACK):D===cp?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):He(i.CULL_FACE),I=D}function de(D){D!==B&&(W&&i.lineWidth(D),B=D)}function We(D,xe,X){D?(fe(i.POLYGON_OFFSET_FILL),(O!==xe||k!==X)&&(i.polygonOffset(xe,X),O=xe,k=X)):He(i.POLYGON_OFFSET_FILL)}function be(D){D?fe(i.SCISSOR_TEST):He(i.SCISSOR_TEST)}function C(D){D===void 0&&(D=i.TEXTURE0+K-1),se!==D&&(i.activeTexture(D),se=D)}function w(D,xe,X){X===void 0&&(se===null?X=i.TEXTURE0+K-1:X=se);let J=me[X];J===void 0&&(J={type:void 0,texture:void 0},me[X]=J),(J.type!==D||J.texture!==xe)&&(se!==X&&(i.activeTexture(X),se=X),i.bindTexture(D,xe||Ie[D]),J.type=D,J.texture=xe)}function F(){const D=me[se];D!==void 0&&D.type!==void 0&&(i.bindTexture(D.type,null),D.type=void 0,D.texture=void 0)}function j(){try{i.compressedTexImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function ee(){try{i.compressedTexImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function $(){try{i.texSubImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Ne(){try{i.texSubImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function _e(){try{i.compressedTexSubImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function we(){try{i.compressedTexSubImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function ot(){try{i.texStorage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function re(){try{i.texStorage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Ce(){try{i.texImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Xe(){try{i.texImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Ye(D){pt.equals(D)===!1&&(i.scissor(D.x,D.y,D.z,D.w),pt.copy(D))}function Pe(D){Z.equals(D)===!1&&(i.viewport(D.x,D.y,D.z,D.w),Z.copy(D))}function ct(D,xe){let X=l.get(xe);X===void 0&&(X=new WeakMap,l.set(xe,X));let J=X.get(D);J===void 0&&(J=i.getUniformBlockIndex(xe,D.name),X.set(D,J))}function nt(D,xe){const J=l.get(xe).get(D);c.get(xe)!==J&&(i.uniformBlockBinding(xe,J,D.__bindingPointIndex),c.set(xe,J))}function Tt(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),o.setReversed(!1),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),u={},se=null,me={},h={},f=new WeakMap,d=[],g=null,_=!1,p=null,m=null,v=null,y=null,x=null,P=null,A=null,E=new ze(0,0,0),R=0,b=!1,S=null,I=null,B=null,O=null,k=null,pt.set(0,0,i.canvas.width,i.canvas.height),Z.set(0,0,i.canvas.width,i.canvas.height),r.reset(),o.reset(),a.reset()}return{buffers:{color:r,depth:o,stencil:a},enable:fe,disable:He,bindFramebuffer:je,drawBuffers:qe,useProgram:ut,setBlending:L,setMaterial:Be,setFlipSided:ie,setCullFace:Ee,setLineWidth:de,setPolygonOffset:We,setScissorTest:be,activeTexture:C,bindTexture:w,unbindTexture:F,compressedTexImage2D:j,compressedTexImage3D:ee,texImage2D:Ce,texImage3D:Xe,updateUBOMapping:ct,uniformBlockBinding:nt,texStorage2D:ot,texStorage3D:re,texSubImage2D:$,texSubImage3D:Ne,compressedTexSubImage2D:_e,compressedTexSubImage3D:we,scissor:Ye,viewport:Pe,reset:Tt}}function Mh(i,e,t,n){const s=fv(n);switch(t){case Tf:return i*e;case Rf:return i*e;case Cf:return i*e*2;case Fl:return i*e/s.components*s.byteLength;case Bl:return i*e/s.components*s.byteLength;case Pf:return i*e*2/s.components*s.byteLength;case kl:return i*e*2/s.components*s.byteLength;case Af:return i*e*3/s.components*s.byteLength;case In:return i*e*4/s.components*s.byteLength;case zl:return i*e*4/s.components*s.byteLength;case Yo:case jo:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case $o:case Ko:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Wc:case qc:return Math.max(i,16)*Math.max(e,8)/4;case Gc:case Xc:return Math.max(i,8)*Math.max(e,8)/2;case Yc:case jc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case $c:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Kc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Zc:return Math.floor((i+4)/5)*Math.floor((e+3)/4)*16;case Jc:return Math.floor((i+4)/5)*Math.floor((e+4)/5)*16;case Qc:return Math.floor((i+5)/6)*Math.floor((e+4)/5)*16;case el:return Math.floor((i+5)/6)*Math.floor((e+5)/6)*16;case tl:return Math.floor((i+7)/8)*Math.floor((e+4)/5)*16;case nl:return Math.floor((i+7)/8)*Math.floor((e+5)/6)*16;case il:return Math.floor((i+7)/8)*Math.floor((e+7)/8)*16;case sl:return Math.floor((i+9)/10)*Math.floor((e+4)/5)*16;case rl:return Math.floor((i+9)/10)*Math.floor((e+5)/6)*16;case ol:return Math.floor((i+9)/10)*Math.floor((e+7)/8)*16;case al:return Math.floor((i+9)/10)*Math.floor((e+9)/10)*16;case cl:return Math.floor((i+11)/12)*Math.floor((e+9)/10)*16;case ll:return Math.floor((i+11)/12)*Math.floor((e+11)/12)*16;case Zo:case ul:case hl:return Math.ceil(i/4)*Math.ceil(e/4)*16;case Lf:case fl:return Math.ceil(i/4)*Math.ceil(e/4)*8;case dl:case pl:return Math.ceil(i/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function fv(i){switch(i){case yi:case bf:return{byteLength:1,components:1};case Hr:case wf:case $r:return{byteLength:2,components:1};case Ul:case Ol:return{byteLength:2,components:4};case ms:case Nl:case Xn:return{byteLength:4,components:1};case Ef:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}function dv(i,e,t,n,s,r,o){const a=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,c=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),l=new te,u=new WeakMap;let h;const f=new WeakMap;let d=!1;try{d=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function g(C,w){return d?new OffscreenCanvas(C,w):Wr("canvas")}function _(C,w,F){let j=1;const ee=be(C);if((ee.width>F||ee.height>F)&&(j=F/Math.max(ee.width,ee.height)),j<1)if(typeof HTMLImageElement<"u"&&C instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&C instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&C instanceof ImageBitmap||typeof VideoFrame<"u"&&C instanceof VideoFrame){const $=Math.floor(j*ee.width),Ne=Math.floor(j*ee.height);h===void 0&&(h=g($,Ne));const _e=w?g($,Ne):h;return _e.width=$,_e.height=Ne,_e.getContext("2d").drawImage(C,0,0,$,Ne),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+ee.width+"x"+ee.height+") to ("+$+"x"+Ne+")."),_e}else return"data"in C&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+ee.width+"x"+ee.height+")."),C;return C}function p(C){return C.generateMipmaps}function m(C){i.generateMipmap(C)}function v(C){return C.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:C.isWebGL3DRenderTarget?i.TEXTURE_3D:C.isWebGLArrayRenderTarget||C.isCompressedArrayTexture?i.TEXTURE_2D_ARRAY:i.TEXTURE_2D}function y(C,w,F,j,ee=!1){if(C!==null){if(i[C]!==void 0)return i[C];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+C+"'")}let $=w;if(w===i.RED&&(F===i.FLOAT&&($=i.R32F),F===i.HALF_FLOAT&&($=i.R16F),F===i.UNSIGNED_BYTE&&($=i.R8)),w===i.RED_INTEGER&&(F===i.UNSIGNED_BYTE&&($=i.R8UI),F===i.UNSIGNED_SHORT&&($=i.R16UI),F===i.UNSIGNED_INT&&($=i.R32UI),F===i.BYTE&&($=i.R8I),F===i.SHORT&&($=i.R16I),F===i.INT&&($=i.R32I)),w===i.RG&&(F===i.FLOAT&&($=i.RG32F),F===i.HALF_FLOAT&&($=i.RG16F),F===i.UNSIGNED_BYTE&&($=i.RG8)),w===i.RG_INTEGER&&(F===i.UNSIGNED_BYTE&&($=i.RG8UI),F===i.UNSIGNED_SHORT&&($=i.RG16UI),F===i.UNSIGNED_INT&&($=i.RG32UI),F===i.BYTE&&($=i.RG8I),F===i.SHORT&&($=i.RG16I),F===i.INT&&($=i.RG32I)),w===i.RGB_INTEGER&&(F===i.UNSIGNED_BYTE&&($=i.RGB8UI),F===i.UNSIGNED_SHORT&&($=i.RGB16UI),F===i.UNSIGNED_INT&&($=i.RGB32UI),F===i.BYTE&&($=i.RGB8I),F===i.SHORT&&($=i.RGB16I),F===i.INT&&($=i.RGB32I)),w===i.RGBA_INTEGER&&(F===i.UNSIGNED_BYTE&&($=i.RGBA8UI),F===i.UNSIGNED_SHORT&&($=i.RGBA16UI),F===i.UNSIGNED_INT&&($=i.RGBA32UI),F===i.BYTE&&($=i.RGBA8I),F===i.SHORT&&($=i.RGBA16I),F===i.INT&&($=i.RGBA32I)),w===i.RGB&&F===i.UNSIGNED_INT_5_9_9_9_REV&&($=i.RGB9_E5),w===i.RGBA){const Ne=ee?fa:at.getTransfer(j);F===i.FLOAT&&($=i.RGBA32F),F===i.HALF_FLOAT&&($=i.RGBA16F),F===i.UNSIGNED_BYTE&&($=Ne===St?i.SRGB8_ALPHA8:i.RGBA8),F===i.UNSIGNED_SHORT_4_4_4_4&&($=i.RGBA4),F===i.UNSIGNED_SHORT_5_5_5_1&&($=i.RGB5_A1)}return($===i.R16F||$===i.R32F||$===i.RG16F||$===i.RG32F||$===i.RGBA16F||$===i.RGBA32F)&&e.get("EXT_color_buffer_float"),$}function x(C,w){let F;return C?w===null||w===ms||w===er?F=i.DEPTH24_STENCIL8:w===Xn?F=i.DEPTH32F_STENCIL8:w===Hr&&(F=i.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):w===null||w===ms||w===er?F=i.DEPTH_COMPONENT24:w===Xn?F=i.DEPTH_COMPONENT32F:w===Hr&&(F=i.DEPTH_COMPONENT16),F}function P(C,w){return p(C)===!0||C.isFramebufferTexture&&C.minFilter!==dn&&C.minFilter!==Sn?Math.log2(Math.max(w.width,w.height))+1:C.mipmaps!==void 0&&C.mipmaps.length>0?C.mipmaps.length:C.isCompressedTexture&&Array.isArray(C.image)?w.mipmaps.length:1}function A(C){const w=C.target;w.removeEventListener("dispose",A),R(w),w.isVideoTexture&&u.delete(w)}function E(C){const w=C.target;w.removeEventListener("dispose",E),S(w)}function R(C){const w=n.get(C);if(w.__webglInit===void 0)return;const F=C.source,j=f.get(F);if(j){const ee=j[w.__cacheKey];ee.usedTimes--,ee.usedTimes===0&&b(C),Object.keys(j).length===0&&f.delete(F)}n.remove(C)}function b(C){const w=n.get(C);i.deleteTexture(w.__webglTexture);const F=C.source,j=f.get(F);delete j[w.__cacheKey],o.memory.textures--}function S(C){const w=n.get(C);if(C.depthTexture&&(C.depthTexture.dispose(),n.remove(C.depthTexture)),C.isWebGLCubeRenderTarget)for(let j=0;j<6;j++){if(Array.isArray(w.__webglFramebuffer[j]))for(let ee=0;ee<w.__webglFramebuffer[j].length;ee++)i.deleteFramebuffer(w.__webglFramebuffer[j][ee]);else i.deleteFramebuffer(w.__webglFramebuffer[j]);w.__webglDepthbuffer&&i.deleteRenderbuffer(w.__webglDepthbuffer[j])}else{if(Array.isArray(w.__webglFramebuffer))for(let j=0;j<w.__webglFramebuffer.length;j++)i.deleteFramebuffer(w.__webglFramebuffer[j]);else i.deleteFramebuffer(w.__webglFramebuffer);if(w.__webglDepthbuffer&&i.deleteRenderbuffer(w.__webglDepthbuffer),w.__webglMultisampledFramebuffer&&i.deleteFramebuffer(w.__webglMultisampledFramebuffer),w.__webglColorRenderbuffer)for(let j=0;j<w.__webglColorRenderbuffer.length;j++)w.__webglColorRenderbuffer[j]&&i.deleteRenderbuffer(w.__webglColorRenderbuffer[j]);w.__webglDepthRenderbuffer&&i.deleteRenderbuffer(w.__webglDepthRenderbuffer)}const F=C.textures;for(let j=0,ee=F.length;j<ee;j++){const $=n.get(F[j]);$.__webglTexture&&(i.deleteTexture($.__webglTexture),o.memory.textures--),n.remove(F[j])}n.remove(C)}let I=0;function B(){I=0}function O(){const C=I;return C>=s.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+C+" texture units while this GPU supports only "+s.maxTextures),I+=1,C}function k(C){const w=[];return w.push(C.wrapS),w.push(C.wrapT),w.push(C.wrapR||0),w.push(C.magFilter),w.push(C.minFilter),w.push(C.anisotropy),w.push(C.internalFormat),w.push(C.format),w.push(C.type),w.push(C.generateMipmaps),w.push(C.premultiplyAlpha),w.push(C.flipY),w.push(C.unpackAlignment),w.push(C.colorSpace),w.join()}function K(C,w){const F=n.get(C);if(C.isVideoTexture&&de(C),C.isRenderTargetTexture===!1&&C.version>0&&F.__version!==C.version){const j=C.image;if(j===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(j.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{Z(F,C,w);return}}t.bindTexture(i.TEXTURE_2D,F.__webglTexture,i.TEXTURE0+w)}function W(C,w){const F=n.get(C);if(C.version>0&&F.__version!==C.version){Z(F,C,w);return}t.bindTexture(i.TEXTURE_2D_ARRAY,F.__webglTexture,i.TEXTURE0+w)}function q(C,w){const F=n.get(C);if(C.version>0&&F.__version!==C.version){Z(F,C,w);return}t.bindTexture(i.TEXTURE_3D,F.__webglTexture,i.TEXTURE0+w)}function V(C,w){const F=n.get(C);if(C.version>0&&F.__version!==C.version){le(F,C,w);return}t.bindTexture(i.TEXTURE_CUBE_MAP,F.__webglTexture,i.TEXTURE0+w)}const se={[Qs]:i.REPEAT,[Fi]:i.CLAMP_TO_EDGE,[ta]:i.MIRRORED_REPEAT},me={[dn]:i.NEAREST,[Sf]:i.NEAREST_MIPMAP_NEAREST,[Ir]:i.NEAREST_MIPMAP_LINEAR,[Sn]:i.LINEAR,[qo]:i.LINEAR_MIPMAP_NEAREST,[gi]:i.LINEAR_MIPMAP_LINEAR},Se={[Gp]:i.NEVER,[$p]:i.ALWAYS,[Wp]:i.LESS,[Nf]:i.LEQUAL,[Xp]:i.EQUAL,[jp]:i.GEQUAL,[qp]:i.GREATER,[Yp]:i.NOTEQUAL};function Ze(C,w){if(w.type===Xn&&e.has("OES_texture_float_linear")===!1&&(w.magFilter===Sn||w.magFilter===qo||w.magFilter===Ir||w.magFilter===gi||w.minFilter===Sn||w.minFilter===qo||w.minFilter===Ir||w.minFilter===gi)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(C,i.TEXTURE_WRAP_S,se[w.wrapS]),i.texParameteri(C,i.TEXTURE_WRAP_T,se[w.wrapT]),(C===i.TEXTURE_3D||C===i.TEXTURE_2D_ARRAY)&&i.texParameteri(C,i.TEXTURE_WRAP_R,se[w.wrapR]),i.texParameteri(C,i.TEXTURE_MAG_FILTER,me[w.magFilter]),i.texParameteri(C,i.TEXTURE_MIN_FILTER,me[w.minFilter]),w.compareFunction&&(i.texParameteri(C,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(C,i.TEXTURE_COMPARE_FUNC,Se[w.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(w.magFilter===dn||w.minFilter!==Ir&&w.minFilter!==gi||w.type===Xn&&e.has("OES_texture_float_linear")===!1)return;if(w.anisotropy>1||n.get(w).__currentAnisotropy){const F=e.get("EXT_texture_filter_anisotropic");i.texParameterf(C,F.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(w.anisotropy,s.getMaxAnisotropy())),n.get(w).__currentAnisotropy=w.anisotropy}}}function pt(C,w){let F=!1;C.__webglInit===void 0&&(C.__webglInit=!0,w.addEventListener("dispose",A));const j=w.source;let ee=f.get(j);ee===void 0&&(ee={},f.set(j,ee));const $=k(w);if($!==C.__cacheKey){ee[$]===void 0&&(ee[$]={texture:i.createTexture(),usedTimes:0},o.memory.textures++,F=!0),ee[$].usedTimes++;const Ne=ee[C.__cacheKey];Ne!==void 0&&(ee[C.__cacheKey].usedTimes--,Ne.usedTimes===0&&b(w)),C.__cacheKey=$,C.__webglTexture=ee[$].texture}return F}function Z(C,w,F){let j=i.TEXTURE_2D;(w.isDataArrayTexture||w.isCompressedArrayTexture)&&(j=i.TEXTURE_2D_ARRAY),w.isData3DTexture&&(j=i.TEXTURE_3D);const ee=pt(C,w),$=w.source;t.bindTexture(j,C.__webglTexture,i.TEXTURE0+F);const Ne=n.get($);if($.version!==Ne.__version||ee===!0){t.activeTexture(i.TEXTURE0+F);const _e=at.getPrimaries(at.workingColorSpace),we=w.colorSpace===Ui?null:at.getPrimaries(w.colorSpace),ot=w.colorSpace===Ui||_e===we?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,w.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,w.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,w.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,ot);let re=_(w.image,!1,s.maxTextureSize);re=We(w,re);const Ce=r.convert(w.format,w.colorSpace),Xe=r.convert(w.type);let Ye=y(w.internalFormat,Ce,Xe,w.colorSpace,w.isVideoTexture);Ze(j,w);let Pe;const ct=w.mipmaps,nt=w.isVideoTexture!==!0,Tt=Ne.__version===void 0||ee===!0,D=$.dataReady,xe=P(w,re);if(w.isDepthTexture)Ye=x(w.format===tr,w.type),Tt&&(nt?t.texStorage2D(i.TEXTURE_2D,1,Ye,re.width,re.height):t.texImage2D(i.TEXTURE_2D,0,Ye,re.width,re.height,0,Ce,Xe,null));else if(w.isDataTexture)if(ct.length>0){nt&&Tt&&t.texStorage2D(i.TEXTURE_2D,xe,Ye,ct[0].width,ct[0].height);for(let X=0,J=ct.length;X<J;X++)Pe=ct[X],nt?D&&t.texSubImage2D(i.TEXTURE_2D,X,0,0,Pe.width,Pe.height,Ce,Xe,Pe.data):t.texImage2D(i.TEXTURE_2D,X,Ye,Pe.width,Pe.height,0,Ce,Xe,Pe.data);w.generateMipmaps=!1}else nt?(Tt&&t.texStorage2D(i.TEXTURE_2D,xe,Ye,re.width,re.height),D&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,re.width,re.height,Ce,Xe,re.data)):t.texImage2D(i.TEXTURE_2D,0,Ye,re.width,re.height,0,Ce,Xe,re.data);else if(w.isCompressedTexture)if(w.isCompressedArrayTexture){nt&&Tt&&t.texStorage3D(i.TEXTURE_2D_ARRAY,xe,Ye,ct[0].width,ct[0].height,re.depth);for(let X=0,J=ct.length;X<J;X++)if(Pe=ct[X],w.format!==In)if(Ce!==null)if(nt){if(D)if(w.layerUpdates.size>0){const Me=Mh(Pe.width,Pe.height,w.format,w.type);for(const ve of w.layerUpdates){const Qe=Pe.data.subarray(ve*Me/Pe.data.BYTES_PER_ELEMENT,(ve+1)*Me/Pe.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,X,0,0,ve,Pe.width,Pe.height,1,Ce,Qe)}w.clearLayerUpdates()}else t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,X,0,0,0,Pe.width,Pe.height,re.depth,Ce,Pe.data)}else t.compressedTexImage3D(i.TEXTURE_2D_ARRAY,X,Ye,Pe.width,Pe.height,re.depth,0,Pe.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else nt?D&&t.texSubImage3D(i.TEXTURE_2D_ARRAY,X,0,0,0,Pe.width,Pe.height,re.depth,Ce,Xe,Pe.data):t.texImage3D(i.TEXTURE_2D_ARRAY,X,Ye,Pe.width,Pe.height,re.depth,0,Ce,Xe,Pe.data)}else{nt&&Tt&&t.texStorage2D(i.TEXTURE_2D,xe,Ye,ct[0].width,ct[0].height);for(let X=0,J=ct.length;X<J;X++)Pe=ct[X],w.format!==In?Ce!==null?nt?D&&t.compressedTexSubImage2D(i.TEXTURE_2D,X,0,0,Pe.width,Pe.height,Ce,Pe.data):t.compressedTexImage2D(i.TEXTURE_2D,X,Ye,Pe.width,Pe.height,0,Pe.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):nt?D&&t.texSubImage2D(i.TEXTURE_2D,X,0,0,Pe.width,Pe.height,Ce,Xe,Pe.data):t.texImage2D(i.TEXTURE_2D,X,Ye,Pe.width,Pe.height,0,Ce,Xe,Pe.data)}else if(w.isDataArrayTexture)if(nt){if(Tt&&t.texStorage3D(i.TEXTURE_2D_ARRAY,xe,Ye,re.width,re.height,re.depth),D)if(w.layerUpdates.size>0){const X=Mh(re.width,re.height,w.format,w.type);for(const J of w.layerUpdates){const Me=re.data.subarray(J*X/re.data.BYTES_PER_ELEMENT,(J+1)*X/re.data.BYTES_PER_ELEMENT);t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,J,re.width,re.height,1,Ce,Xe,Me)}w.clearLayerUpdates()}else t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,re.width,re.height,re.depth,Ce,Xe,re.data)}else t.texImage3D(i.TEXTURE_2D_ARRAY,0,Ye,re.width,re.height,re.depth,0,Ce,Xe,re.data);else if(w.isData3DTexture)nt?(Tt&&t.texStorage3D(i.TEXTURE_3D,xe,Ye,re.width,re.height,re.depth),D&&t.texSubImage3D(i.TEXTURE_3D,0,0,0,0,re.width,re.height,re.depth,Ce,Xe,re.data)):t.texImage3D(i.TEXTURE_3D,0,Ye,re.width,re.height,re.depth,0,Ce,Xe,re.data);else if(w.isFramebufferTexture){if(Tt)if(nt)t.texStorage2D(i.TEXTURE_2D,xe,Ye,re.width,re.height);else{let X=re.width,J=re.height;for(let Me=0;Me<xe;Me++)t.texImage2D(i.TEXTURE_2D,Me,Ye,X,J,0,Ce,Xe,null),X>>=1,J>>=1}}else if(ct.length>0){if(nt&&Tt){const X=be(ct[0]);t.texStorage2D(i.TEXTURE_2D,xe,Ye,X.width,X.height)}for(let X=0,J=ct.length;X<J;X++)Pe=ct[X],nt?D&&t.texSubImage2D(i.TEXTURE_2D,X,0,0,Ce,Xe,Pe):t.texImage2D(i.TEXTURE_2D,X,Ye,Ce,Xe,Pe);w.generateMipmaps=!1}else if(nt){if(Tt){const X=be(re);t.texStorage2D(i.TEXTURE_2D,xe,Ye,X.width,X.height)}D&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,Ce,Xe,re)}else t.texImage2D(i.TEXTURE_2D,0,Ye,Ce,Xe,re);p(w)&&m(j),Ne.__version=$.version,w.onUpdate&&w.onUpdate(w)}C.__version=w.version}function le(C,w,F){if(w.image.length!==6)return;const j=pt(C,w),ee=w.source;t.bindTexture(i.TEXTURE_CUBE_MAP,C.__webglTexture,i.TEXTURE0+F);const $=n.get(ee);if(ee.version!==$.__version||j===!0){t.activeTexture(i.TEXTURE0+F);const Ne=at.getPrimaries(at.workingColorSpace),_e=w.colorSpace===Ui?null:at.getPrimaries(w.colorSpace),we=w.colorSpace===Ui||Ne===_e?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,w.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,w.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,w.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,we);const ot=w.isCompressedTexture||w.image[0].isCompressedTexture,re=w.image[0]&&w.image[0].isDataTexture,Ce=[];for(let J=0;J<6;J++)!ot&&!re?Ce[J]=_(w.image[J],!0,s.maxCubemapSize):Ce[J]=re?w.image[J].image:w.image[J],Ce[J]=We(w,Ce[J]);const Xe=Ce[0],Ye=r.convert(w.format,w.colorSpace),Pe=r.convert(w.type),ct=y(w.internalFormat,Ye,Pe,w.colorSpace),nt=w.isVideoTexture!==!0,Tt=$.__version===void 0||j===!0,D=ee.dataReady;let xe=P(w,Xe);Ze(i.TEXTURE_CUBE_MAP,w);let X;if(ot){nt&&Tt&&t.texStorage2D(i.TEXTURE_CUBE_MAP,xe,ct,Xe.width,Xe.height);for(let J=0;J<6;J++){X=Ce[J].mipmaps;for(let Me=0;Me<X.length;Me++){const ve=X[Me];w.format!==In?Ye!==null?nt?D&&t.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Me,0,0,ve.width,ve.height,Ye,ve.data):t.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Me,ct,ve.width,ve.height,0,ve.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):nt?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Me,0,0,ve.width,ve.height,Ye,Pe,ve.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Me,ct,ve.width,ve.height,0,Ye,Pe,ve.data)}}}else{if(X=w.mipmaps,nt&&Tt){X.length>0&&xe++;const J=be(Ce[0]);t.texStorage2D(i.TEXTURE_CUBE_MAP,xe,ct,J.width,J.height)}for(let J=0;J<6;J++)if(re){nt?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,0,0,Ce[J].width,Ce[J].height,Ye,Pe,Ce[J].data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,ct,Ce[J].width,Ce[J].height,0,Ye,Pe,Ce[J].data);for(let Me=0;Me<X.length;Me++){const Qe=X[Me].image[J].image;nt?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Me+1,0,0,Qe.width,Qe.height,Ye,Pe,Qe.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Me+1,ct,Qe.width,Qe.height,0,Ye,Pe,Qe.data)}}else{nt?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,0,0,Ye,Pe,Ce[J]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,ct,Ye,Pe,Ce[J]);for(let Me=0;Me<X.length;Me++){const ve=X[Me];nt?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Me+1,0,0,Ye,Pe,ve.image[J]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Me+1,ct,Ye,Pe,ve.image[J])}}}p(w)&&m(i.TEXTURE_CUBE_MAP),$.__version=ee.version,w.onUpdate&&w.onUpdate(w)}C.__version=w.version}function Ie(C,w,F,j,ee,$){const Ne=r.convert(F.format,F.colorSpace),_e=r.convert(F.type),we=y(F.internalFormat,Ne,_e,F.colorSpace),ot=n.get(w),re=n.get(F);if(re.__renderTarget=w,!ot.__hasExternalTextures){const Ce=Math.max(1,w.width>>$),Xe=Math.max(1,w.height>>$);ee===i.TEXTURE_3D||ee===i.TEXTURE_2D_ARRAY?t.texImage3D(ee,$,we,Ce,Xe,w.depth,0,Ne,_e,null):t.texImage2D(ee,$,we,Ce,Xe,0,Ne,_e,null)}t.bindFramebuffer(i.FRAMEBUFFER,C),Ee(w)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,j,ee,re.__webglTexture,0,ie(w)):(ee===i.TEXTURE_2D||ee>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&ee<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,j,ee,re.__webglTexture,$),t.bindFramebuffer(i.FRAMEBUFFER,null)}function fe(C,w,F){if(i.bindRenderbuffer(i.RENDERBUFFER,C),w.depthBuffer){const j=w.depthTexture,ee=j&&j.isDepthTexture?j.type:null,$=x(w.stencilBuffer,ee),Ne=w.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,_e=ie(w);Ee(w)?a.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,_e,$,w.width,w.height):F?i.renderbufferStorageMultisample(i.RENDERBUFFER,_e,$,w.width,w.height):i.renderbufferStorage(i.RENDERBUFFER,$,w.width,w.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,Ne,i.RENDERBUFFER,C)}else{const j=w.textures;for(let ee=0;ee<j.length;ee++){const $=j[ee],Ne=r.convert($.format,$.colorSpace),_e=r.convert($.type),we=y($.internalFormat,Ne,_e,$.colorSpace),ot=ie(w);F&&Ee(w)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,ot,we,w.width,w.height):Ee(w)?a.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,ot,we,w.width,w.height):i.renderbufferStorage(i.RENDERBUFFER,we,w.width,w.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function He(C,w){if(w&&w.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(i.FRAMEBUFFER,C),!(w.depthTexture&&w.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const j=n.get(w.depthTexture);j.__renderTarget=w,(!j.__webglTexture||w.depthTexture.image.width!==w.width||w.depthTexture.image.height!==w.height)&&(w.depthTexture.image.width=w.width,w.depthTexture.image.height=w.height,w.depthTexture.needsUpdate=!0),K(w.depthTexture,0);const ee=j.__webglTexture,$=ie(w);if(w.depthTexture.format===Xs)Ee(w)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,ee,0,$):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,ee,0);else if(w.depthTexture.format===tr)Ee(w)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,ee,0,$):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,ee,0);else throw new Error("Unknown depthTexture format")}function je(C){const w=n.get(C),F=C.isWebGLCubeRenderTarget===!0;if(w.__boundDepthTexture!==C.depthTexture){const j=C.depthTexture;if(w.__depthDisposeCallback&&w.__depthDisposeCallback(),j){const ee=()=>{delete w.__boundDepthTexture,delete w.__depthDisposeCallback,j.removeEventListener("dispose",ee)};j.addEventListener("dispose",ee),w.__depthDisposeCallback=ee}w.__boundDepthTexture=j}if(C.depthTexture&&!w.__autoAllocateDepthBuffer){if(F)throw new Error("target.depthTexture not supported in Cube render targets");He(w.__webglFramebuffer,C)}else if(F){w.__webglDepthbuffer=[];for(let j=0;j<6;j++)if(t.bindFramebuffer(i.FRAMEBUFFER,w.__webglFramebuffer[j]),w.__webglDepthbuffer[j]===void 0)w.__webglDepthbuffer[j]=i.createRenderbuffer(),fe(w.__webglDepthbuffer[j],C,!1);else{const ee=C.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,$=w.__webglDepthbuffer[j];i.bindRenderbuffer(i.RENDERBUFFER,$),i.framebufferRenderbuffer(i.FRAMEBUFFER,ee,i.RENDERBUFFER,$)}}else if(t.bindFramebuffer(i.FRAMEBUFFER,w.__webglFramebuffer),w.__webglDepthbuffer===void 0)w.__webglDepthbuffer=i.createRenderbuffer(),fe(w.__webglDepthbuffer,C,!1);else{const j=C.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,ee=w.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,ee),i.framebufferRenderbuffer(i.FRAMEBUFFER,j,i.RENDERBUFFER,ee)}t.bindFramebuffer(i.FRAMEBUFFER,null)}function qe(C,w,F){const j=n.get(C);w!==void 0&&Ie(j.__webglFramebuffer,C,C.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),F!==void 0&&je(C)}function ut(C){const w=C.texture,F=n.get(C),j=n.get(w);C.addEventListener("dispose",E);const ee=C.textures,$=C.isWebGLCubeRenderTarget===!0,Ne=ee.length>1;if(Ne||(j.__webglTexture===void 0&&(j.__webglTexture=i.createTexture()),j.__version=w.version,o.memory.textures++),$){F.__webglFramebuffer=[];for(let _e=0;_e<6;_e++)if(w.mipmaps&&w.mipmaps.length>0){F.__webglFramebuffer[_e]=[];for(let we=0;we<w.mipmaps.length;we++)F.__webglFramebuffer[_e][we]=i.createFramebuffer()}else F.__webglFramebuffer[_e]=i.createFramebuffer()}else{if(w.mipmaps&&w.mipmaps.length>0){F.__webglFramebuffer=[];for(let _e=0;_e<w.mipmaps.length;_e++)F.__webglFramebuffer[_e]=i.createFramebuffer()}else F.__webglFramebuffer=i.createFramebuffer();if(Ne)for(let _e=0,we=ee.length;_e<we;_e++){const ot=n.get(ee[_e]);ot.__webglTexture===void 0&&(ot.__webglTexture=i.createTexture(),o.memory.textures++)}if(C.samples>0&&Ee(C)===!1){F.__webglMultisampledFramebuffer=i.createFramebuffer(),F.__webglColorRenderbuffer=[],t.bindFramebuffer(i.FRAMEBUFFER,F.__webglMultisampledFramebuffer);for(let _e=0;_e<ee.length;_e++){const we=ee[_e];F.__webglColorRenderbuffer[_e]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,F.__webglColorRenderbuffer[_e]);const ot=r.convert(we.format,we.colorSpace),re=r.convert(we.type),Ce=y(we.internalFormat,ot,re,we.colorSpace,C.isXRRenderTarget===!0),Xe=ie(C);i.renderbufferStorageMultisample(i.RENDERBUFFER,Xe,Ce,C.width,C.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+_e,i.RENDERBUFFER,F.__webglColorRenderbuffer[_e])}i.bindRenderbuffer(i.RENDERBUFFER,null),C.depthBuffer&&(F.__webglDepthRenderbuffer=i.createRenderbuffer(),fe(F.__webglDepthRenderbuffer,C,!0)),t.bindFramebuffer(i.FRAMEBUFFER,null)}}if($){t.bindTexture(i.TEXTURE_CUBE_MAP,j.__webglTexture),Ze(i.TEXTURE_CUBE_MAP,w);for(let _e=0;_e<6;_e++)if(w.mipmaps&&w.mipmaps.length>0)for(let we=0;we<w.mipmaps.length;we++)Ie(F.__webglFramebuffer[_e][we],C,w,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+_e,we);else Ie(F.__webglFramebuffer[_e],C,w,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+_e,0);p(w)&&m(i.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Ne){for(let _e=0,we=ee.length;_e<we;_e++){const ot=ee[_e],re=n.get(ot);t.bindTexture(i.TEXTURE_2D,re.__webglTexture),Ze(i.TEXTURE_2D,ot),Ie(F.__webglFramebuffer,C,ot,i.COLOR_ATTACHMENT0+_e,i.TEXTURE_2D,0),p(ot)&&m(i.TEXTURE_2D)}t.unbindTexture()}else{let _e=i.TEXTURE_2D;if((C.isWebGL3DRenderTarget||C.isWebGLArrayRenderTarget)&&(_e=C.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),t.bindTexture(_e,j.__webglTexture),Ze(_e,w),w.mipmaps&&w.mipmaps.length>0)for(let we=0;we<w.mipmaps.length;we++)Ie(F.__webglFramebuffer[we],C,w,i.COLOR_ATTACHMENT0,_e,we);else Ie(F.__webglFramebuffer,C,w,i.COLOR_ATTACHMENT0,_e,0);p(w)&&m(_e),t.unbindTexture()}C.depthBuffer&&je(C)}function Q(C){const w=C.textures;for(let F=0,j=w.length;F<j;F++){const ee=w[F];if(p(ee)){const $=v(C),Ne=n.get(ee).__webglTexture;t.bindTexture($,Ne),m($),t.unbindTexture()}}}const ae=[],L=[];function Be(C){if(C.samples>0){if(Ee(C)===!1){const w=C.textures,F=C.width,j=C.height;let ee=i.COLOR_BUFFER_BIT;const $=C.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Ne=n.get(C),_e=w.length>1;if(_e)for(let we=0;we<w.length;we++)t.bindFramebuffer(i.FRAMEBUFFER,Ne.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+we,i.RENDERBUFFER,null),t.bindFramebuffer(i.FRAMEBUFFER,Ne.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+we,i.TEXTURE_2D,null,0);t.bindFramebuffer(i.READ_FRAMEBUFFER,Ne.__webglMultisampledFramebuffer),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ne.__webglFramebuffer);for(let we=0;we<w.length;we++){if(C.resolveDepthBuffer&&(C.depthBuffer&&(ee|=i.DEPTH_BUFFER_BIT),C.stencilBuffer&&C.resolveStencilBuffer&&(ee|=i.STENCIL_BUFFER_BIT)),_e){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,Ne.__webglColorRenderbuffer[we]);const ot=n.get(w[we]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,ot,0)}i.blitFramebuffer(0,0,F,j,0,0,F,j,ee,i.NEAREST),c===!0&&(ae.length=0,L.length=0,ae.push(i.COLOR_ATTACHMENT0+we),C.depthBuffer&&C.resolveDepthBuffer===!1&&(ae.push($),L.push($),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,L)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,ae))}if(t.bindFramebuffer(i.READ_FRAMEBUFFER,null),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),_e)for(let we=0;we<w.length;we++){t.bindFramebuffer(i.FRAMEBUFFER,Ne.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+we,i.RENDERBUFFER,Ne.__webglColorRenderbuffer[we]);const ot=n.get(w[we]).__webglTexture;t.bindFramebuffer(i.FRAMEBUFFER,Ne.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+we,i.TEXTURE_2D,ot,0)}t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ne.__webglMultisampledFramebuffer)}else if(C.depthBuffer&&C.resolveDepthBuffer===!1&&c){const w=C.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[w])}}}function ie(C){return Math.min(s.maxSamples,C.samples)}function Ee(C){const w=n.get(C);return C.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&w.__useRenderToTexture!==!1}function de(C){const w=o.render.frame;u.get(C)!==w&&(u.set(C,w),C.update())}function We(C,w){const F=C.colorSpace,j=C.format,ee=C.type;return C.isCompressedTexture===!0||C.isVideoTexture===!0||F!==an&&F!==Ui&&(at.getTransfer(F)===St?(j!==In||ee!==yi)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",F)),w}function be(C){return typeof HTMLImageElement<"u"&&C instanceof HTMLImageElement?(l.width=C.naturalWidth||C.width,l.height=C.naturalHeight||C.height):typeof VideoFrame<"u"&&C instanceof VideoFrame?(l.width=C.displayWidth,l.height=C.displayHeight):(l.width=C.width,l.height=C.height),l}this.allocateTextureUnit=O,this.resetTextureUnits=B,this.setTexture2D=K,this.setTexture2DArray=W,this.setTexture3D=q,this.setTextureCube=V,this.rebindTextures=qe,this.setupRenderTarget=ut,this.updateRenderTargetMipmap=Q,this.updateMultisampleRenderTarget=Be,this.setupDepthRenderbuffer=je,this.setupFrameBufferTexture=Ie,this.useMultisampledRTT=Ee}function pv(i,e){function t(n,s=Ui){let r;const o=at.getTransfer(s);if(n===yi)return i.UNSIGNED_BYTE;if(n===Ul)return i.UNSIGNED_SHORT_4_4_4_4;if(n===Ol)return i.UNSIGNED_SHORT_5_5_5_1;if(n===Ef)return i.UNSIGNED_INT_5_9_9_9_REV;if(n===bf)return i.BYTE;if(n===wf)return i.SHORT;if(n===Hr)return i.UNSIGNED_SHORT;if(n===Nl)return i.INT;if(n===ms)return i.UNSIGNED_INT;if(n===Xn)return i.FLOAT;if(n===$r)return i.HALF_FLOAT;if(n===Tf)return i.ALPHA;if(n===Af)return i.RGB;if(n===In)return i.RGBA;if(n===Rf)return i.LUMINANCE;if(n===Cf)return i.LUMINANCE_ALPHA;if(n===Xs)return i.DEPTH_COMPONENT;if(n===tr)return i.DEPTH_STENCIL;if(n===Fl)return i.RED;if(n===Bl)return i.RED_INTEGER;if(n===Pf)return i.RG;if(n===kl)return i.RG_INTEGER;if(n===zl)return i.RGBA_INTEGER;if(n===Yo||n===jo||n===$o||n===Ko)if(o===St)if(r=e.get("WEBGL_compressed_texture_s3tc_srgb"),r!==null){if(n===Yo)return r.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===jo)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===$o)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===Ko)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(r=e.get("WEBGL_compressed_texture_s3tc"),r!==null){if(n===Yo)return r.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===jo)return r.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===$o)return r.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===Ko)return r.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Gc||n===Wc||n===Xc||n===qc)if(r=e.get("WEBGL_compressed_texture_pvrtc"),r!==null){if(n===Gc)return r.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Wc)return r.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Xc)return r.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===qc)return r.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Yc||n===jc||n===$c)if(r=e.get("WEBGL_compressed_texture_etc"),r!==null){if(n===Yc||n===jc)return o===St?r.COMPRESSED_SRGB8_ETC2:r.COMPRESSED_RGB8_ETC2;if(n===$c)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:r.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Kc||n===Zc||n===Jc||n===Qc||n===el||n===tl||n===nl||n===il||n===sl||n===rl||n===ol||n===al||n===cl||n===ll)if(r=e.get("WEBGL_compressed_texture_astc"),r!==null){if(n===Kc)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:r.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Zc)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:r.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Jc)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:r.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===Qc)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:r.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===el)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:r.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===tl)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:r.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===nl)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:r.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===il)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:r.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===sl)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:r.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===rl)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:r.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===ol)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:r.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===al)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:r.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===cl)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:r.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===ll)return o===St?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:r.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===Zo||n===ul||n===hl)if(r=e.get("EXT_texture_compression_bptc"),r!==null){if(n===Zo)return o===St?r.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:r.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===ul)return r.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===hl)return r.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Lf||n===fl||n===dl||n===pl)if(r=e.get("EXT_texture_compression_rgtc"),r!==null){if(n===Zo)return r.COMPRESSED_RED_RGTC1_EXT;if(n===fl)return r.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===dl)return r.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===pl)return r.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===er?i.UNSIGNED_INT_24_8:i[n]!==void 0?i[n]:null}return{convert:t}}class mv extends _n{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class Bt extends It{constructor(){super(),this.isGroup=!0,this.type="Group"}}const gv={type:"move"};class ec{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Bt,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Bt,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new M,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new M),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Bt,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new M,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new M),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let s=null,r=null,o=null;const a=this._targetRay,c=this._grip,l=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(l&&e.hand){o=!0;for(const _ of e.hand.values()){const p=t.getJointPose(_,n),m=this._getHandJoint(l,_);p!==null&&(m.matrix.fromArray(p.transform.matrix),m.matrix.decompose(m.position,m.rotation,m.scale),m.matrixWorldNeedsUpdate=!0,m.jointRadius=p.radius),m.visible=p!==null}const u=l.joints["index-finger-tip"],h=l.joints["thumb-tip"],f=u.position.distanceTo(h.position),d=.02,g=.005;l.inputState.pinching&&f>d+g?(l.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!l.inputState.pinching&&f<=d-g&&(l.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else c!==null&&e.gripSpace&&(r=t.getPose(e.gripSpace,n),r!==null&&(c.matrix.fromArray(r.transform.matrix),c.matrix.decompose(c.position,c.rotation,c.scale),c.matrixWorldNeedsUpdate=!0,r.linearVelocity?(c.hasLinearVelocity=!0,c.linearVelocity.copy(r.linearVelocity)):c.hasLinearVelocity=!1,r.angularVelocity?(c.hasAngularVelocity=!0,c.angularVelocity.copy(r.angularVelocity)):c.hasAngularVelocity=!1));a!==null&&(s=t.getPose(e.targetRaySpace,n),s===null&&r!==null&&(s=r),s!==null&&(a.matrix.fromArray(s.transform.matrix),a.matrix.decompose(a.position,a.rotation,a.scale),a.matrixWorldNeedsUpdate=!0,s.linearVelocity?(a.hasLinearVelocity=!0,a.linearVelocity.copy(s.linearVelocity)):a.hasLinearVelocity=!1,s.angularVelocity?(a.hasAngularVelocity=!0,a.angularVelocity.copy(s.angularVelocity)):a.hasAngularVelocity=!1,this.dispatchEvent(gv)))}return a!==null&&(a.visible=s!==null),c!==null&&(c.visible=r!==null),l!==null&&(l.visible=o!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new Bt;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const _v=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,xv=`
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

}`;class vv{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const s=new jt,r=e.properties.get(s);r.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=s}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new Zn({vertexShader:_v,fragmentShader:xv,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new kt(new Jn(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class yv extends cr{constructor(e,t){super();const n=this;let s=null,r=1,o=null,a="local-floor",c=1,l=null,u=null,h=null,f=null,d=null,g=null;const _=new vv,p=t.getContextAttributes();let m=null,v=null;const y=[],x=[],P=new te;let A=null;const E=new _n;E.viewport=new dt;const R=new _n;R.viewport=new dt;const b=[E,R],S=new mv;let I=null,B=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(Z){let le=y[Z];return le===void 0&&(le=new ec,y[Z]=le),le.getTargetRaySpace()},this.getControllerGrip=function(Z){let le=y[Z];return le===void 0&&(le=new ec,y[Z]=le),le.getGripSpace()},this.getHand=function(Z){let le=y[Z];return le===void 0&&(le=new ec,y[Z]=le),le.getHandSpace()};function O(Z){const le=x.indexOf(Z.inputSource);if(le===-1)return;const Ie=y[le];Ie!==void 0&&(Ie.update(Z.inputSource,Z.frame,l||o),Ie.dispatchEvent({type:Z.type,data:Z.inputSource}))}function k(){s.removeEventListener("select",O),s.removeEventListener("selectstart",O),s.removeEventListener("selectend",O),s.removeEventListener("squeeze",O),s.removeEventListener("squeezestart",O),s.removeEventListener("squeezeend",O),s.removeEventListener("end",k),s.removeEventListener("inputsourceschange",K);for(let Z=0;Z<y.length;Z++){const le=x[Z];le!==null&&(x[Z]=null,y[Z].disconnect(le))}I=null,B=null,_.reset(),e.setRenderTarget(m),d=null,f=null,h=null,s=null,v=null,pt.stop(),n.isPresenting=!1,e.setPixelRatio(A),e.setSize(P.width,P.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(Z){r=Z,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(Z){a=Z,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return l||o},this.setReferenceSpace=function(Z){l=Z},this.getBaseLayer=function(){return f!==null?f:d},this.getBinding=function(){return h},this.getFrame=function(){return g},this.getSession=function(){return s},this.setSession=async function(Z){if(s=Z,s!==null){if(m=e.getRenderTarget(),s.addEventListener("select",O),s.addEventListener("selectstart",O),s.addEventListener("selectend",O),s.addEventListener("squeeze",O),s.addEventListener("squeezestart",O),s.addEventListener("squeezeend",O),s.addEventListener("end",k),s.addEventListener("inputsourceschange",K),p.xrCompatible!==!0&&await t.makeXRCompatible(),A=e.getPixelRatio(),e.getSize(P),s.renderState.layers===void 0){const le={antialias:p.antialias,alpha:!0,depth:p.depth,stencil:p.stencil,framebufferScaleFactor:r};d=new XRWebGLLayer(s,t,le),s.updateRenderState({baseLayer:d}),e.setPixelRatio(1),e.setSize(d.framebufferWidth,d.framebufferHeight,!1),v=new gs(d.framebufferWidth,d.framebufferHeight,{format:In,type:yi,colorSpace:e.outputColorSpace,stencilBuffer:p.stencil})}else{let le=null,Ie=null,fe=null;p.depth&&(fe=p.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,le=p.stencil?tr:Xs,Ie=p.stencil?er:ms);const He={colorFormat:t.RGBA8,depthFormat:fe,scaleFactor:r};h=new XRWebGLBinding(s,t),f=h.createProjectionLayer(He),s.updateRenderState({layers:[f]}),e.setPixelRatio(1),e.setSize(f.textureWidth,f.textureHeight,!1),v=new gs(f.textureWidth,f.textureHeight,{format:In,type:yi,depthTexture:new Xf(f.textureWidth,f.textureHeight,Ie,void 0,void 0,void 0,void 0,void 0,void 0,le),stencilBuffer:p.stencil,colorSpace:e.outputColorSpace,samples:p.antialias?4:0,resolveDepthBuffer:f.ignoreDepthValues===!1})}v.isXRRenderTarget=!0,this.setFoveation(c),l=null,o=await s.requestReferenceSpace(a),pt.setContext(s),pt.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(s!==null)return s.environmentBlendMode},this.getDepthTexture=function(){return _.getDepthTexture()};function K(Z){for(let le=0;le<Z.removed.length;le++){const Ie=Z.removed[le],fe=x.indexOf(Ie);fe>=0&&(x[fe]=null,y[fe].disconnect(Ie))}for(let le=0;le<Z.added.length;le++){const Ie=Z.added[le];let fe=x.indexOf(Ie);if(fe===-1){for(let je=0;je<y.length;je++)if(je>=x.length){x.push(Ie),fe=je;break}else if(x[je]===null){x[je]=Ie,fe=je;break}if(fe===-1)break}const He=y[fe];He&&He.connect(Ie)}}const W=new M,q=new M;function V(Z,le,Ie){W.setFromMatrixPosition(le.matrixWorld),q.setFromMatrixPosition(Ie.matrixWorld);const fe=W.distanceTo(q),He=le.projectionMatrix.elements,je=Ie.projectionMatrix.elements,qe=He[14]/(He[10]-1),ut=He[14]/(He[10]+1),Q=(He[9]+1)/He[5],ae=(He[9]-1)/He[5],L=(He[8]-1)/He[0],Be=(je[8]+1)/je[0],ie=qe*L,Ee=qe*Be,de=fe/(-L+Be),We=de*-L;if(le.matrixWorld.decompose(Z.position,Z.quaternion,Z.scale),Z.translateX(We),Z.translateZ(de),Z.matrixWorld.compose(Z.position,Z.quaternion,Z.scale),Z.matrixWorldInverse.copy(Z.matrixWorld).invert(),He[10]===-1)Z.projectionMatrix.copy(le.projectionMatrix),Z.projectionMatrixInverse.copy(le.projectionMatrixInverse);else{const be=qe+de,C=ut+de,w=ie-We,F=Ee+(fe-We),j=Q*ut/C*be,ee=ae*ut/C*be;Z.projectionMatrix.makePerspective(w,F,j,ee,be,C),Z.projectionMatrixInverse.copy(Z.projectionMatrix).invert()}}function se(Z,le){le===null?Z.matrixWorld.copy(Z.matrix):Z.matrixWorld.multiplyMatrices(le.matrixWorld,Z.matrix),Z.matrixWorldInverse.copy(Z.matrixWorld).invert()}this.updateCamera=function(Z){if(s===null)return;let le=Z.near,Ie=Z.far;_.texture!==null&&(_.depthNear>0&&(le=_.depthNear),_.depthFar>0&&(Ie=_.depthFar)),S.near=R.near=E.near=le,S.far=R.far=E.far=Ie,(I!==S.near||B!==S.far)&&(s.updateRenderState({depthNear:S.near,depthFar:S.far}),I=S.near,B=S.far),E.layers.mask=Z.layers.mask|2,R.layers.mask=Z.layers.mask|4,S.layers.mask=E.layers.mask|R.layers.mask;const fe=Z.parent,He=S.cameras;se(S,fe);for(let je=0;je<He.length;je++)se(He[je],fe);He.length===2?V(S,E,R):S.projectionMatrix.copy(E.projectionMatrix),me(Z,S,fe)};function me(Z,le,Ie){Ie===null?Z.matrix.copy(le.matrixWorld):(Z.matrix.copy(Ie.matrixWorld),Z.matrix.invert(),Z.matrix.multiply(le.matrixWorld)),Z.matrix.decompose(Z.position,Z.quaternion,Z.scale),Z.updateMatrixWorld(!0),Z.projectionMatrix.copy(le.projectionMatrix),Z.projectionMatrixInverse.copy(le.projectionMatrixInverse),Z.isPerspectiveCamera&&(Z.fov=nr*2*Math.atan(1/Z.projectionMatrix.elements[5]),Z.zoom=1)}this.getCamera=function(){return S},this.getFoveation=function(){if(!(f===null&&d===null))return c},this.setFoveation=function(Z){c=Z,f!==null&&(f.fixedFoveation=Z),d!==null&&d.fixedFoveation!==void 0&&(d.fixedFoveation=Z)},this.hasDepthSensing=function(){return _.texture!==null},this.getDepthSensingMesh=function(){return _.getMesh(S)};let Se=null;function Ze(Z,le){if(u=le.getViewerPose(l||o),g=le,u!==null){const Ie=u.views;d!==null&&(e.setRenderTargetFramebuffer(v,d.framebuffer),e.setRenderTarget(v));let fe=!1;Ie.length!==S.cameras.length&&(S.cameras.length=0,fe=!0);for(let je=0;je<Ie.length;je++){const qe=Ie[je];let ut=null;if(d!==null)ut=d.getViewport(qe);else{const ae=h.getViewSubImage(f,qe);ut=ae.viewport,je===0&&(e.setRenderTargetTextures(v,ae.colorTexture,f.ignoreDepthValues?void 0:ae.depthStencilTexture),e.setRenderTarget(v))}let Q=b[je];Q===void 0&&(Q=new _n,Q.layers.enable(je),Q.viewport=new dt,b[je]=Q),Q.matrix.fromArray(qe.transform.matrix),Q.matrix.decompose(Q.position,Q.quaternion,Q.scale),Q.projectionMatrix.fromArray(qe.projectionMatrix),Q.projectionMatrixInverse.copy(Q.projectionMatrix).invert(),Q.viewport.set(ut.x,ut.y,ut.width,ut.height),je===0&&(S.matrix.copy(Q.matrix),S.matrix.decompose(S.position,S.quaternion,S.scale)),fe===!0&&S.cameras.push(Q)}const He=s.enabledFeatures;if(He&&He.includes("depth-sensing")){const je=h.getDepthInformation(Ie[0]);je&&je.isValid&&je.texture&&_.init(e,je,s.renderState)}}for(let Ie=0;Ie<y.length;Ie++){const fe=x[Ie],He=y[Ie];fe!==null&&He!==void 0&&He.update(fe,le,l||o)}Se&&Se(Z,le),le.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:le}),g=null}const pt=new Wf;pt.setAnimationLoop(Ze),this.setAnimationLoop=function(Z){Se=Z},this.dispose=function(){}}}const rs=new wn,Mv=new Le;function Sv(i,e){function t(p,m){p.matrixAutoUpdate===!0&&p.updateMatrix(),m.value.copy(p.matrix)}function n(p,m){m.color.getRGB(p.fogColor.value,Hf(i)),m.isFog?(p.fogNear.value=m.near,p.fogFar.value=m.far):m.isFogExp2&&(p.fogDensity.value=m.density)}function s(p,m,v,y,x){m.isMeshBasicMaterial||m.isMeshLambertMaterial?r(p,m):m.isMeshToonMaterial?(r(p,m),h(p,m)):m.isMeshPhongMaterial?(r(p,m),u(p,m)):m.isMeshStandardMaterial?(r(p,m),f(p,m),m.isMeshPhysicalMaterial&&d(p,m,x)):m.isMeshMatcapMaterial?(r(p,m),g(p,m)):m.isMeshDepthMaterial?r(p,m):m.isMeshDistanceMaterial?(r(p,m),_(p,m)):m.isMeshNormalMaterial?r(p,m):m.isLineBasicMaterial?(o(p,m),m.isLineDashedMaterial&&a(p,m)):m.isPointsMaterial?c(p,m,v,y):m.isSpriteMaterial?l(p,m):m.isShadowMaterial?(p.color.value.copy(m.color),p.opacity.value=m.opacity):m.isShaderMaterial&&(m.uniformsNeedUpdate=!1)}function r(p,m){p.opacity.value=m.opacity,m.color&&p.diffuse.value.copy(m.color),m.emissive&&p.emissive.value.copy(m.emissive).multiplyScalar(m.emissiveIntensity),m.map&&(p.map.value=m.map,t(m.map,p.mapTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.bumpMap&&(p.bumpMap.value=m.bumpMap,t(m.bumpMap,p.bumpMapTransform),p.bumpScale.value=m.bumpScale,m.side===fn&&(p.bumpScale.value*=-1)),m.normalMap&&(p.normalMap.value=m.normalMap,t(m.normalMap,p.normalMapTransform),p.normalScale.value.copy(m.normalScale),m.side===fn&&p.normalScale.value.negate()),m.displacementMap&&(p.displacementMap.value=m.displacementMap,t(m.displacementMap,p.displacementMapTransform),p.displacementScale.value=m.displacementScale,p.displacementBias.value=m.displacementBias),m.emissiveMap&&(p.emissiveMap.value=m.emissiveMap,t(m.emissiveMap,p.emissiveMapTransform)),m.specularMap&&(p.specularMap.value=m.specularMap,t(m.specularMap,p.specularMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest);const v=e.get(m),y=v.envMap,x=v.envMapRotation;y&&(p.envMap.value=y,rs.copy(x),rs.x*=-1,rs.y*=-1,rs.z*=-1,y.isCubeTexture&&y.isRenderTargetTexture===!1&&(rs.y*=-1,rs.z*=-1),p.envMapRotation.value.setFromMatrix4(Mv.makeRotationFromEuler(rs)),p.flipEnvMap.value=y.isCubeTexture&&y.isRenderTargetTexture===!1?-1:1,p.reflectivity.value=m.reflectivity,p.ior.value=m.ior,p.refractionRatio.value=m.refractionRatio),m.lightMap&&(p.lightMap.value=m.lightMap,p.lightMapIntensity.value=m.lightMapIntensity,t(m.lightMap,p.lightMapTransform)),m.aoMap&&(p.aoMap.value=m.aoMap,p.aoMapIntensity.value=m.aoMapIntensity,t(m.aoMap,p.aoMapTransform))}function o(p,m){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,m.map&&(p.map.value=m.map,t(m.map,p.mapTransform))}function a(p,m){p.dashSize.value=m.dashSize,p.totalSize.value=m.dashSize+m.gapSize,p.scale.value=m.scale}function c(p,m,v,y){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,p.size.value=m.size*v,p.scale.value=y*.5,m.map&&(p.map.value=m.map,t(m.map,p.uvTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest)}function l(p,m){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,p.rotation.value=m.rotation,m.map&&(p.map.value=m.map,t(m.map,p.mapTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest)}function u(p,m){p.specular.value.copy(m.specular),p.shininess.value=Math.max(m.shininess,1e-4)}function h(p,m){m.gradientMap&&(p.gradientMap.value=m.gradientMap)}function f(p,m){p.metalness.value=m.metalness,m.metalnessMap&&(p.metalnessMap.value=m.metalnessMap,t(m.metalnessMap,p.metalnessMapTransform)),p.roughness.value=m.roughness,m.roughnessMap&&(p.roughnessMap.value=m.roughnessMap,t(m.roughnessMap,p.roughnessMapTransform)),m.envMap&&(p.envMapIntensity.value=m.envMapIntensity)}function d(p,m,v){p.ior.value=m.ior,m.sheen>0&&(p.sheenColor.value.copy(m.sheenColor).multiplyScalar(m.sheen),p.sheenRoughness.value=m.sheenRoughness,m.sheenColorMap&&(p.sheenColorMap.value=m.sheenColorMap,t(m.sheenColorMap,p.sheenColorMapTransform)),m.sheenRoughnessMap&&(p.sheenRoughnessMap.value=m.sheenRoughnessMap,t(m.sheenRoughnessMap,p.sheenRoughnessMapTransform))),m.clearcoat>0&&(p.clearcoat.value=m.clearcoat,p.clearcoatRoughness.value=m.clearcoatRoughness,m.clearcoatMap&&(p.clearcoatMap.value=m.clearcoatMap,t(m.clearcoatMap,p.clearcoatMapTransform)),m.clearcoatRoughnessMap&&(p.clearcoatRoughnessMap.value=m.clearcoatRoughnessMap,t(m.clearcoatRoughnessMap,p.clearcoatRoughnessMapTransform)),m.clearcoatNormalMap&&(p.clearcoatNormalMap.value=m.clearcoatNormalMap,t(m.clearcoatNormalMap,p.clearcoatNormalMapTransform),p.clearcoatNormalScale.value.copy(m.clearcoatNormalScale),m.side===fn&&p.clearcoatNormalScale.value.negate())),m.dispersion>0&&(p.dispersion.value=m.dispersion),m.iridescence>0&&(p.iridescence.value=m.iridescence,p.iridescenceIOR.value=m.iridescenceIOR,p.iridescenceThicknessMinimum.value=m.iridescenceThicknessRange[0],p.iridescenceThicknessMaximum.value=m.iridescenceThicknessRange[1],m.iridescenceMap&&(p.iridescenceMap.value=m.iridescenceMap,t(m.iridescenceMap,p.iridescenceMapTransform)),m.iridescenceThicknessMap&&(p.iridescenceThicknessMap.value=m.iridescenceThicknessMap,t(m.iridescenceThicknessMap,p.iridescenceThicknessMapTransform))),m.transmission>0&&(p.transmission.value=m.transmission,p.transmissionSamplerMap.value=v.texture,p.transmissionSamplerSize.value.set(v.width,v.height),m.transmissionMap&&(p.transmissionMap.value=m.transmissionMap,t(m.transmissionMap,p.transmissionMapTransform)),p.thickness.value=m.thickness,m.thicknessMap&&(p.thicknessMap.value=m.thicknessMap,t(m.thicknessMap,p.thicknessMapTransform)),p.attenuationDistance.value=m.attenuationDistance,p.attenuationColor.value.copy(m.attenuationColor)),m.anisotropy>0&&(p.anisotropyVector.value.set(m.anisotropy*Math.cos(m.anisotropyRotation),m.anisotropy*Math.sin(m.anisotropyRotation)),m.anisotropyMap&&(p.anisotropyMap.value=m.anisotropyMap,t(m.anisotropyMap,p.anisotropyMapTransform))),p.specularIntensity.value=m.specularIntensity,p.specularColor.value.copy(m.specularColor),m.specularColorMap&&(p.specularColorMap.value=m.specularColorMap,t(m.specularColorMap,p.specularColorMapTransform)),m.specularIntensityMap&&(p.specularIntensityMap.value=m.specularIntensityMap,t(m.specularIntensityMap,p.specularIntensityMapTransform))}function g(p,m){m.matcap&&(p.matcap.value=m.matcap)}function _(p,m){const v=e.get(m).light;p.referencePosition.value.setFromMatrixPosition(v.matrixWorld),p.nearDistance.value=v.shadow.camera.near,p.farDistance.value=v.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:s}}function bv(i,e,t,n){let s={},r={},o=[];const a=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function c(v,y){const x=y.program;n.uniformBlockBinding(v,x)}function l(v,y){let x=s[v.id];x===void 0&&(g(v),x=u(v),s[v.id]=x,v.addEventListener("dispose",p));const P=y.program;n.updateUBOMapping(v,P);const A=e.render.frame;r[v.id]!==A&&(f(v),r[v.id]=A)}function u(v){const y=h();v.__bindingPointIndex=y;const x=i.createBuffer(),P=v.__size,A=v.usage;return i.bindBuffer(i.UNIFORM_BUFFER,x),i.bufferData(i.UNIFORM_BUFFER,P,A),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,y,x),x}function h(){for(let v=0;v<a;v++)if(o.indexOf(v)===-1)return o.push(v),v;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function f(v){const y=s[v.id],x=v.uniforms,P=v.__cache;i.bindBuffer(i.UNIFORM_BUFFER,y);for(let A=0,E=x.length;A<E;A++){const R=Array.isArray(x[A])?x[A]:[x[A]];for(let b=0,S=R.length;b<S;b++){const I=R[b];if(d(I,A,b,P)===!0){const B=I.__offset,O=Array.isArray(I.value)?I.value:[I.value];let k=0;for(let K=0;K<O.length;K++){const W=O[K],q=_(W);typeof W=="number"||typeof W=="boolean"?(I.__data[0]=W,i.bufferSubData(i.UNIFORM_BUFFER,B+k,I.__data)):W.isMatrix3?(I.__data[0]=W.elements[0],I.__data[1]=W.elements[1],I.__data[2]=W.elements[2],I.__data[3]=0,I.__data[4]=W.elements[3],I.__data[5]=W.elements[4],I.__data[6]=W.elements[5],I.__data[7]=0,I.__data[8]=W.elements[6],I.__data[9]=W.elements[7],I.__data[10]=W.elements[8],I.__data[11]=0):(W.toArray(I.__data,k),k+=q.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,B,I.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function d(v,y,x,P){const A=v.value,E=y+"_"+x;if(P[E]===void 0)return typeof A=="number"||typeof A=="boolean"?P[E]=A:P[E]=A.clone(),!0;{const R=P[E];if(typeof A=="number"||typeof A=="boolean"){if(R!==A)return P[E]=A,!0}else if(R.equals(A)===!1)return R.copy(A),!0}return!1}function g(v){const y=v.uniforms;let x=0;const P=16;for(let E=0,R=y.length;E<R;E++){const b=Array.isArray(y[E])?y[E]:[y[E]];for(let S=0,I=b.length;S<I;S++){const B=b[S],O=Array.isArray(B.value)?B.value:[B.value];for(let k=0,K=O.length;k<K;k++){const W=O[k],q=_(W),V=x%P,se=V%q.boundary,me=V+se;x+=se,me!==0&&P-me<q.storage&&(x+=P-me),B.__data=new Float32Array(q.storage/Float32Array.BYTES_PER_ELEMENT),B.__offset=x,x+=q.storage}}}const A=x%P;return A>0&&(x+=P-A),v.__size=x,v.__cache={},this}function _(v){const y={boundary:0,storage:0};return typeof v=="number"||typeof v=="boolean"?(y.boundary=4,y.storage=4):v.isVector2?(y.boundary=8,y.storage=8):v.isVector3||v.isColor?(y.boundary=16,y.storage=12):v.isVector4?(y.boundary=16,y.storage=16):v.isMatrix3?(y.boundary=48,y.storage=48):v.isMatrix4?(y.boundary=64,y.storage=64):v.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",v),y}function p(v){const y=v.target;y.removeEventListener("dispose",p);const x=o.indexOf(y.__bindingPointIndex);o.splice(x,1),i.deleteBuffer(s[y.id]),delete s[y.id],delete r[y.id]}function m(){for(const v in s)i.deleteBuffer(s[v]);o=[],s={},r={}}return{bind:c,update:l,dispose:m}}class wv{constructor(e={}){const{canvas:t=fm(),context:n=null,depth:s=!0,stencil:r=!1,alpha:o=!1,antialias:a=!1,premultipliedAlpha:c=!0,preserveDrawingBuffer:l=!1,powerPreference:u="default",failIfMajorPerformanceCaveat:h=!1,reverseDepthBuffer:f=!1}=e;this.isWebGLRenderer=!0;let d;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");d=n.getContextAttributes().alpha}else d=o;const g=new Uint32Array(4),_=new Int32Array(4);let p=null,m=null;const v=[],y=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=Ht,this.toneMapping=Gi,this.toneMappingExposure=1;const x=this;let P=!1,A=0,E=0,R=null,b=-1,S=null;const I=new dt,B=new dt;let O=null;const k=new ze(0);let K=0,W=t.width,q=t.height,V=1,se=null,me=null;const Se=new dt(0,0,W,q),Ze=new dt(0,0,W,q);let pt=!1;const Z=new Gl;let le=!1,Ie=!1;const fe=new Le,He=new Le,je=new M,qe=new dt,ut={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Q=!1;function ae(){return R===null?V:1}let L=n;function Be(T,N){return t.getContext(T,N)}try{const T={alpha:!0,depth:s,stencil:r,antialias:a,premultipliedAlpha:c,preserveDrawingBuffer:l,powerPreference:u,failIfMajorPerformanceCaveat:h};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${Dl}`),t.addEventListener("webglcontextlost",J,!1),t.addEventListener("webglcontextrestored",Me,!1),t.addEventListener("webglcontextcreationerror",ve,!1),L===null){const N="webgl2";if(L=Be(N,T),L===null)throw Be(N)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(T){throw console.error("THREE.WebGLRenderer: "+T.message),T}let ie,Ee,de,We,be,C,w,F,j,ee,$,Ne,_e,we,ot,re,Ce,Xe,Ye,Pe,ct,nt,Tt,D;function xe(){ie=new C_(L),ie.init(),nt=new pv(L,ie),Ee=new b_(L,ie,e,nt),de=new hv(L,ie),Ee.reverseDepthBuffer&&f&&de.buffers.depth.setReversed(!0),We=new I_(L),be=new Kx,C=new dv(L,ie,de,be,Ee,nt,We),w=new E_(x),F=new R_(x),j=new km(L),Tt=new M_(L,j),ee=new P_(L,j,We,Tt),$=new N_(L,ee,j,We),Ye=new D_(L,Ee,C),re=new w_(be),Ne=new $x(x,w,F,ie,Ee,Tt,re),_e=new Sv(x,be),we=new Jx,ot=new sv(ie),Xe=new y_(x,w,F,de,$,d,c),Ce=new lv(x,$,Ee),D=new bv(L,We,Ee,de),Pe=new S_(L,ie,We),ct=new L_(L,ie,We),We.programs=Ne.programs,x.capabilities=Ee,x.extensions=ie,x.properties=be,x.renderLists=we,x.shadowMap=Ce,x.state=de,x.info=We}xe();const X=new yv(x,L);this.xr=X,this.getContext=function(){return L},this.getContextAttributes=function(){return L.getContextAttributes()},this.forceContextLoss=function(){const T=ie.get("WEBGL_lose_context");T&&T.loseContext()},this.forceContextRestore=function(){const T=ie.get("WEBGL_lose_context");T&&T.restoreContext()},this.getPixelRatio=function(){return V},this.setPixelRatio=function(T){T!==void 0&&(V=T,this.setSize(W,q,!1))},this.getSize=function(T){return T.set(W,q)},this.setSize=function(T,N,H=!0){if(X.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}W=T,q=N,t.width=Math.floor(T*V),t.height=Math.floor(N*V),H===!0&&(t.style.width=T+"px",t.style.height=N+"px"),this.setViewport(0,0,T,N)},this.getDrawingBufferSize=function(T){return T.set(W*V,q*V).floor()},this.setDrawingBufferSize=function(T,N,H){W=T,q=N,V=H,t.width=Math.floor(T*H),t.height=Math.floor(N*H),this.setViewport(0,0,T,N)},this.getCurrentViewport=function(T){return T.copy(I)},this.getViewport=function(T){return T.copy(Se)},this.setViewport=function(T,N,H,G){T.isVector4?Se.set(T.x,T.y,T.z,T.w):Se.set(T,N,H,G),de.viewport(I.copy(Se).multiplyScalar(V).round())},this.getScissor=function(T){return T.copy(Ze)},this.setScissor=function(T,N,H,G){T.isVector4?Ze.set(T.x,T.y,T.z,T.w):Ze.set(T,N,H,G),de.scissor(B.copy(Ze).multiplyScalar(V).round())},this.getScissorTest=function(){return pt},this.setScissorTest=function(T){de.setScissorTest(pt=T)},this.setOpaqueSort=function(T){se=T},this.setTransparentSort=function(T){me=T},this.getClearColor=function(T){return T.copy(Xe.getClearColor())},this.setClearColor=function(){Xe.setClearColor.apply(Xe,arguments)},this.getClearAlpha=function(){return Xe.getClearAlpha()},this.setClearAlpha=function(){Xe.setClearAlpha.apply(Xe,arguments)},this.clear=function(T=!0,N=!0,H=!0){let G=0;if(T){let U=!1;if(R!==null){const ue=R.texture.format;U=ue===zl||ue===kl||ue===Bl}if(U){const ue=R.texture.type,ye=ue===yi||ue===ms||ue===Hr||ue===er||ue===Ul||ue===Ol,Ue=Xe.getClearColor(),Oe=Xe.getClearAlpha(),$e=Ue.r,et=Ue.g,Fe=Ue.b;ye?(g[0]=$e,g[1]=et,g[2]=Fe,g[3]=Oe,L.clearBufferuiv(L.COLOR,0,g)):(_[0]=$e,_[1]=et,_[2]=Fe,_[3]=Oe,L.clearBufferiv(L.COLOR,0,_))}else G|=L.COLOR_BUFFER_BIT}N&&(G|=L.DEPTH_BUFFER_BIT),H&&(G|=L.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),L.clear(G)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",J,!1),t.removeEventListener("webglcontextrestored",Me,!1),t.removeEventListener("webglcontextcreationerror",ve,!1),we.dispose(),ot.dispose(),be.dispose(),w.dispose(),F.dispose(),$.dispose(),Tt.dispose(),D.dispose(),Ne.dispose(),X.dispose(),X.removeEventListener("sessionstart",fu),X.removeEventListener("sessionend",du),Ji.stop()};function J(T){T.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),P=!0}function Me(){console.log("THREE.WebGLRenderer: Context Restored."),P=!1;const T=We.autoReset,N=Ce.enabled,H=Ce.autoUpdate,G=Ce.needsUpdate,U=Ce.type;xe(),We.autoReset=T,Ce.enabled=N,Ce.autoUpdate=H,Ce.needsUpdate=G,Ce.type=U}function ve(T){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",T.statusMessage)}function Qe(T){const N=T.target;N.removeEventListener("dispose",Qe),Ot(N)}function Ot(T){Jt(T),be.remove(T)}function Jt(T){const N=be.get(T).programs;N!==void 0&&(N.forEach(function(H){Ne.releaseProgram(H)}),T.isShaderMaterial&&Ne.releaseShaderCache(T))}this.renderBufferDirect=function(T,N,H,G,U,ue){N===null&&(N=ut);const ye=U.isMesh&&U.matrixWorld.determinant()<0,Ue=Zd(T,N,H,G,U);de.setMaterial(G,ye);let Oe=H.index,$e=1;if(G.wireframe===!0){if(Oe=ee.getWireframeAttribute(H),Oe===void 0)return;$e=2}const et=H.drawRange,Fe=H.attributes.position;let ht=et.start*$e,At=(et.start+et.count)*$e;ue!==null&&(ht=Math.max(ht,ue.start*$e),At=Math.min(At,(ue.start+ue.count)*$e)),Oe!==null?(ht=Math.max(ht,0),At=Math.min(At,Oe.count)):Fe!=null&&(ht=Math.max(ht,0),At=Math.min(At,Fe.count));const Pt=At-ht;if(Pt<0||Pt===1/0)return;Tt.setup(U,G,Ue,H,Oe);let gn,mt=Pe;if(Oe!==null&&(gn=j.get(Oe),mt=ct,mt.setIndex(gn)),U.isMesh)G.wireframe===!0?(de.setLineWidth(G.wireframeLinewidth*ae()),mt.setMode(L.LINES)):mt.setMode(L.TRIANGLES);else if(U.isLine){let ke=G.linewidth;ke===void 0&&(ke=1),de.setLineWidth(ke*ae()),U.isLineSegments?mt.setMode(L.LINES):U.isLineLoop?mt.setMode(L.LINE_LOOP):mt.setMode(L.LINE_STRIP)}else U.isPoints?mt.setMode(L.POINTS):U.isSprite&&mt.setMode(L.TRIANGLES);if(U.isBatchedMesh)if(U._multiDrawInstances!==null)mt.renderMultiDrawInstances(U._multiDrawStarts,U._multiDrawCounts,U._multiDrawCount,U._multiDrawInstances);else if(ie.get("WEBGL_multi_draw"))mt.renderMultiDraw(U._multiDrawStarts,U._multiDrawCounts,U._multiDrawCount);else{const ke=U._multiDrawStarts,ri=U._multiDrawCounts,gt=U._multiDrawCount,kn=Oe?j.get(Oe).bytesPerElement:1,Ss=be.get(G).currentProgram.getUniforms();for(let xn=0;xn<gt;xn++)Ss.setValue(L,"_gl_DrawID",xn),mt.render(ke[xn]/kn,ri[xn])}else if(U.isInstancedMesh)mt.renderInstances(ht,Pt,U.count);else if(H.isInstancedBufferGeometry){const ke=H._maxInstanceCount!==void 0?H._maxInstanceCount:1/0,ri=Math.min(H.instanceCount,ke);mt.renderInstances(ht,Pt,ri)}else mt.render(ht,Pt)};function xt(T,N,H){T.transparent===!0&&T.side===Mn&&T.forceSinglePass===!1?(T.side=fn,T.needsUpdate=!0,ro(T,N,H),T.side=vi,T.needsUpdate=!0,ro(T,N,H),T.side=Mn):ro(T,N,H)}this.compile=function(T,N,H=null){H===null&&(H=T),m=ot.get(H),m.init(N),y.push(m),H.traverseVisible(function(U){U.isLight&&U.layers.test(N.layers)&&(m.pushLight(U),U.castShadow&&m.pushShadow(U))}),T!==H&&T.traverseVisible(function(U){U.isLight&&U.layers.test(N.layers)&&(m.pushLight(U),U.castShadow&&m.pushShadow(U))}),m.setupLights();const G=new Set;return T.traverse(function(U){if(!(U.isMesh||U.isPoints||U.isLine||U.isSprite))return;const ue=U.material;if(ue)if(Array.isArray(ue))for(let ye=0;ye<ue.length;ye++){const Ue=ue[ye];xt(Ue,H,U),G.add(Ue)}else xt(ue,H,U),G.add(ue)}),y.pop(),m=null,G},this.compileAsync=function(T,N,H=null){const G=this.compile(T,N,H);return new Promise(U=>{function ue(){if(G.forEach(function(ye){be.get(ye).currentProgram.isReady()&&G.delete(ye)}),G.size===0){U(T);return}setTimeout(ue,10)}ie.get("KHR_parallel_shader_compile")!==null?ue():setTimeout(ue,10)})};let Bn=null;function si(T){Bn&&Bn(T)}function fu(){Ji.stop()}function du(){Ji.start()}const Ji=new Wf;Ji.setAnimationLoop(si),typeof self<"u"&&Ji.setContext(self),this.setAnimationLoop=function(T){Bn=T,X.setAnimationLoop(T),T===null?Ji.stop():Ji.start()},X.addEventListener("sessionstart",fu),X.addEventListener("sessionend",du),this.render=function(T,N){if(N!==void 0&&N.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(P===!0)return;if(T.matrixWorldAutoUpdate===!0&&T.updateMatrixWorld(),N.parent===null&&N.matrixWorldAutoUpdate===!0&&N.updateMatrixWorld(),X.enabled===!0&&X.isPresenting===!0&&(X.cameraAutoUpdate===!0&&X.updateCamera(N),N=X.getCamera()),T.isScene===!0&&T.onBeforeRender(x,T,N,R),m=ot.get(T,y.length),m.init(N),y.push(m),He.multiplyMatrices(N.projectionMatrix,N.matrixWorldInverse),Z.setFromProjectionMatrix(He),Ie=this.localClippingEnabled,le=re.init(this.clippingPlanes,Ie),p=we.get(T,v.length),p.init(),v.push(p),X.enabled===!0&&X.isPresenting===!0){const ue=x.xr.getDepthSensingMesh();ue!==null&&Ta(ue,N,-1/0,x.sortObjects)}Ta(T,N,0,x.sortObjects),p.finish(),x.sortObjects===!0&&p.sort(se,me),Q=X.enabled===!1||X.isPresenting===!1||X.hasDepthSensing()===!1,Q&&Xe.addToRenderList(p,T),this.info.render.frame++,le===!0&&re.beginShadows();const H=m.state.shadowsArray;Ce.render(H,T,N),le===!0&&re.endShadows(),this.info.autoReset===!0&&this.info.reset();const G=p.opaque,U=p.transmissive;if(m.setupLights(),N.isArrayCamera){const ue=N.cameras;if(U.length>0)for(let ye=0,Ue=ue.length;ye<Ue;ye++){const Oe=ue[ye];mu(G,U,T,Oe)}Q&&Xe.render(T);for(let ye=0,Ue=ue.length;ye<Ue;ye++){const Oe=ue[ye];pu(p,T,Oe,Oe.viewport)}}else U.length>0&&mu(G,U,T,N),Q&&Xe.render(T),pu(p,T,N);R!==null&&(C.updateMultisampleRenderTarget(R),C.updateRenderTargetMipmap(R)),T.isScene===!0&&T.onAfterRender(x,T,N),Tt.resetDefaultState(),b=-1,S=null,y.pop(),y.length>0?(m=y[y.length-1],le===!0&&re.setGlobalState(x.clippingPlanes,m.state.camera)):m=null,v.pop(),v.length>0?p=v[v.length-1]:p=null};function Ta(T,N,H,G){if(T.visible===!1)return;if(T.layers.test(N.layers)){if(T.isGroup)H=T.renderOrder;else if(T.isLOD)T.autoUpdate===!0&&T.update(N);else if(T.isLight)m.pushLight(T),T.castShadow&&m.pushShadow(T);else if(T.isSprite){if(!T.frustumCulled||Z.intersectsSprite(T)){G&&qe.setFromMatrixPosition(T.matrixWorld).applyMatrix4(He);const ye=$.update(T),Ue=T.material;Ue.visible&&p.push(T,ye,Ue,H,qe.z,null)}}else if((T.isMesh||T.isLine||T.isPoints)&&(!T.frustumCulled||Z.intersectsObject(T))){const ye=$.update(T),Ue=T.material;if(G&&(T.boundingSphere!==void 0?(T.boundingSphere===null&&T.computeBoundingSphere(),qe.copy(T.boundingSphere.center)):(ye.boundingSphere===null&&ye.computeBoundingSphere(),qe.copy(ye.boundingSphere.center)),qe.applyMatrix4(T.matrixWorld).applyMatrix4(He)),Array.isArray(Ue)){const Oe=ye.groups;for(let $e=0,et=Oe.length;$e<et;$e++){const Fe=Oe[$e],ht=Ue[Fe.materialIndex];ht&&ht.visible&&p.push(T,ye,ht,H,qe.z,Fe)}}else Ue.visible&&p.push(T,ye,Ue,H,qe.z,null)}}const ue=T.children;for(let ye=0,Ue=ue.length;ye<Ue;ye++)Ta(ue[ye],N,H,G)}function pu(T,N,H,G){const U=T.opaque,ue=T.transmissive,ye=T.transparent;m.setupLightsView(H),le===!0&&re.setGlobalState(x.clippingPlanes,H),G&&de.viewport(I.copy(G)),U.length>0&&so(U,N,H),ue.length>0&&so(ue,N,H),ye.length>0&&so(ye,N,H),de.buffers.depth.setTest(!0),de.buffers.depth.setMask(!0),de.buffers.color.setMask(!0),de.setPolygonOffset(!1)}function mu(T,N,H,G){if((H.isScene===!0?H.overrideMaterial:null)!==null)return;m.state.transmissionRenderTarget[G.id]===void 0&&(m.state.transmissionRenderTarget[G.id]=new gs(1,1,{generateMipmaps:!0,type:ie.has("EXT_color_buffer_half_float")||ie.has("EXT_color_buffer_float")?$r:yi,minFilter:gi,samples:4,stencilBuffer:r,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:at.workingColorSpace}));const ue=m.state.transmissionRenderTarget[G.id],ye=G.viewport||I;ue.setSize(ye.z,ye.w);const Ue=x.getRenderTarget();x.setRenderTarget(ue),x.getClearColor(k),K=x.getClearAlpha(),K<1&&x.setClearColor(16777215,.5),x.clear(),Q&&Xe.render(H);const Oe=x.toneMapping;x.toneMapping=Gi;const $e=G.viewport;if(G.viewport!==void 0&&(G.viewport=void 0),m.setupLightsView(G),le===!0&&re.setGlobalState(x.clippingPlanes,G),so(T,H,G),C.updateMultisampleRenderTarget(ue),C.updateRenderTargetMipmap(ue),ie.has("WEBGL_multisampled_render_to_texture")===!1){let et=!1;for(let Fe=0,ht=N.length;Fe<ht;Fe++){const At=N[Fe],Pt=At.object,gn=At.geometry,mt=At.material,ke=At.group;if(mt.side===Mn&&Pt.layers.test(G.layers)){const ri=mt.side;mt.side=fn,mt.needsUpdate=!0,gu(Pt,H,G,gn,mt,ke),mt.side=ri,mt.needsUpdate=!0,et=!0}}et===!0&&(C.updateMultisampleRenderTarget(ue),C.updateRenderTargetMipmap(ue))}x.setRenderTarget(Ue),x.setClearColor(k,K),$e!==void 0&&(G.viewport=$e),x.toneMapping=Oe}function so(T,N,H){const G=N.isScene===!0?N.overrideMaterial:null;for(let U=0,ue=T.length;U<ue;U++){const ye=T[U],Ue=ye.object,Oe=ye.geometry,$e=G===null?ye.material:G,et=ye.group;Ue.layers.test(H.layers)&&gu(Ue,N,H,Oe,$e,et)}}function gu(T,N,H,G,U,ue){T.onBeforeRender(x,N,H,G,U,ue),T.modelViewMatrix.multiplyMatrices(H.matrixWorldInverse,T.matrixWorld),T.normalMatrix.getNormalMatrix(T.modelViewMatrix),U.onBeforeRender(x,N,H,G,T,ue),U.transparent===!0&&U.side===Mn&&U.forceSinglePass===!1?(U.side=fn,U.needsUpdate=!0,x.renderBufferDirect(H,N,G,U,T,ue),U.side=vi,U.needsUpdate=!0,x.renderBufferDirect(H,N,G,U,T,ue),U.side=Mn):x.renderBufferDirect(H,N,G,U,T,ue),T.onAfterRender(x,N,H,G,U,ue)}function ro(T,N,H){N.isScene!==!0&&(N=ut);const G=be.get(T),U=m.state.lights,ue=m.state.shadowsArray,ye=U.state.version,Ue=Ne.getParameters(T,U.state,ue,N,H),Oe=Ne.getProgramCacheKey(Ue);let $e=G.programs;G.environment=T.isMeshStandardMaterial?N.environment:null,G.fog=N.fog,G.envMap=(T.isMeshStandardMaterial?F:w).get(T.envMap||G.environment),G.envMapRotation=G.environment!==null&&T.envMap===null?N.environmentRotation:T.envMapRotation,$e===void 0&&(T.addEventListener("dispose",Qe),$e=new Map,G.programs=$e);let et=$e.get(Oe);if(et!==void 0){if(G.currentProgram===et&&G.lightsStateVersion===ye)return xu(T,Ue),et}else Ue.uniforms=Ne.getUniforms(T),T.onBeforeCompile(Ue,x),et=Ne.acquireProgram(Ue,Oe),$e.set(Oe,et),G.uniforms=Ue.uniforms;const Fe=G.uniforms;return(!T.isShaderMaterial&&!T.isRawShaderMaterial||T.clipping===!0)&&(Fe.clippingPlanes=re.uniform),xu(T,Ue),G.needsLights=Qd(T),G.lightsStateVersion=ye,G.needsLights&&(Fe.ambientLightColor.value=U.state.ambient,Fe.lightProbe.value=U.state.probe,Fe.directionalLights.value=U.state.directional,Fe.directionalLightShadows.value=U.state.directionalShadow,Fe.spotLights.value=U.state.spot,Fe.spotLightShadows.value=U.state.spotShadow,Fe.rectAreaLights.value=U.state.rectArea,Fe.ltc_1.value=U.state.rectAreaLTC1,Fe.ltc_2.value=U.state.rectAreaLTC2,Fe.pointLights.value=U.state.point,Fe.pointLightShadows.value=U.state.pointShadow,Fe.hemisphereLights.value=U.state.hemi,Fe.directionalShadowMap.value=U.state.directionalShadowMap,Fe.directionalShadowMatrix.value=U.state.directionalShadowMatrix,Fe.spotShadowMap.value=U.state.spotShadowMap,Fe.spotLightMatrix.value=U.state.spotLightMatrix,Fe.spotLightMap.value=U.state.spotLightMap,Fe.pointShadowMap.value=U.state.pointShadowMap,Fe.pointShadowMatrix.value=U.state.pointShadowMatrix),G.currentProgram=et,G.uniformsList=null,et}function _u(T){if(T.uniformsList===null){const N=T.currentProgram.getUniforms();T.uniformsList=Jo.seqWithValue(N.seq,T.uniforms)}return T.uniformsList}function xu(T,N){const H=be.get(T);H.outputColorSpace=N.outputColorSpace,H.batching=N.batching,H.batchingColor=N.batchingColor,H.instancing=N.instancing,H.instancingColor=N.instancingColor,H.instancingMorph=N.instancingMorph,H.skinning=N.skinning,H.morphTargets=N.morphTargets,H.morphNormals=N.morphNormals,H.morphColors=N.morphColors,H.morphTargetsCount=N.morphTargetsCount,H.numClippingPlanes=N.numClippingPlanes,H.numIntersection=N.numClipIntersection,H.vertexAlphas=N.vertexAlphas,H.vertexTangents=N.vertexTangents,H.toneMapping=N.toneMapping}function Zd(T,N,H,G,U){N.isScene!==!0&&(N=ut),C.resetTextureUnits();const ue=N.fog,ye=G.isMeshStandardMaterial?N.environment:null,Ue=R===null?x.outputColorSpace:R.isXRRenderTarget===!0?R.texture.colorSpace:an,Oe=(G.isMeshStandardMaterial?F:w).get(G.envMap||ye),$e=G.vertexColors===!0&&!!H.attributes.color&&H.attributes.color.itemSize===4,et=!!H.attributes.tangent&&(!!G.normalMap||G.anisotropy>0),Fe=!!H.morphAttributes.position,ht=!!H.morphAttributes.normal,At=!!H.morphAttributes.color;let Pt=Gi;G.toneMapped&&(R===null||R.isXRRenderTarget===!0)&&(Pt=x.toneMapping);const gn=H.morphAttributes.position||H.morphAttributes.normal||H.morphAttributes.color,mt=gn!==void 0?gn.length:0,ke=be.get(G),ri=m.state.lights;if(le===!0&&(Ie===!0||T!==S)){const Tn=T===S&&G.id===b;re.setState(G,T,Tn)}let gt=!1;G.version===ke.__version?(ke.needsLights&&ke.lightsStateVersion!==ri.state.version||ke.outputColorSpace!==Ue||U.isBatchedMesh&&ke.batching===!1||!U.isBatchedMesh&&ke.batching===!0||U.isBatchedMesh&&ke.batchingColor===!0&&U.colorTexture===null||U.isBatchedMesh&&ke.batchingColor===!1&&U.colorTexture!==null||U.isInstancedMesh&&ke.instancing===!1||!U.isInstancedMesh&&ke.instancing===!0||U.isSkinnedMesh&&ke.skinning===!1||!U.isSkinnedMesh&&ke.skinning===!0||U.isInstancedMesh&&ke.instancingColor===!0&&U.instanceColor===null||U.isInstancedMesh&&ke.instancingColor===!1&&U.instanceColor!==null||U.isInstancedMesh&&ke.instancingMorph===!0&&U.morphTexture===null||U.isInstancedMesh&&ke.instancingMorph===!1&&U.morphTexture!==null||ke.envMap!==Oe||G.fog===!0&&ke.fog!==ue||ke.numClippingPlanes!==void 0&&(ke.numClippingPlanes!==re.numPlanes||ke.numIntersection!==re.numIntersection)||ke.vertexAlphas!==$e||ke.vertexTangents!==et||ke.morphTargets!==Fe||ke.morphNormals!==ht||ke.morphColors!==At||ke.toneMapping!==Pt||ke.morphTargetsCount!==mt)&&(gt=!0):(gt=!0,ke.__version=G.version);let kn=ke.currentProgram;gt===!0&&(kn=ro(G,N,U));let Ss=!1,xn=!1,gr=!1;const Lt=kn.getUniforms(),qn=ke.uniforms;if(de.useProgram(kn.program)&&(Ss=!0,xn=!0,gr=!0),G.id!==b&&(b=G.id,xn=!0),Ss||S!==T){de.buffers.depth.getReversed()?(fe.copy(T.projectionMatrix),pm(fe),mm(fe),Lt.setValue(L,"projectionMatrix",fe)):Lt.setValue(L,"projectionMatrix",T.projectionMatrix),Lt.setValue(L,"viewMatrix",T.matrixWorldInverse);const wi=Lt.map.cameraPosition;wi!==void 0&&wi.setValue(L,je.setFromMatrixPosition(T.matrixWorld)),Ee.logarithmicDepthBuffer&&Lt.setValue(L,"logDepthBufFC",2/(Math.log(T.far+1)/Math.LN2)),(G.isMeshPhongMaterial||G.isMeshToonMaterial||G.isMeshLambertMaterial||G.isMeshBasicMaterial||G.isMeshStandardMaterial||G.isShaderMaterial)&&Lt.setValue(L,"isOrthographic",T.isOrthographicCamera===!0),S!==T&&(S=T,xn=!0,gr=!0)}if(U.isSkinnedMesh){Lt.setOptional(L,U,"bindMatrix"),Lt.setOptional(L,U,"bindMatrixInverse");const Tn=U.skeleton;Tn&&(Tn.boneTexture===null&&Tn.computeBoneTexture(),Lt.setValue(L,"boneTexture",Tn.boneTexture,C))}U.isBatchedMesh&&(Lt.setOptional(L,U,"batchingTexture"),Lt.setValue(L,"batchingTexture",U._matricesTexture,C),Lt.setOptional(L,U,"batchingIdTexture"),Lt.setValue(L,"batchingIdTexture",U._indirectTexture,C),Lt.setOptional(L,U,"batchingColorTexture"),U._colorsTexture!==null&&Lt.setValue(L,"batchingColorTexture",U._colorsTexture,C));const _r=H.morphAttributes;if((_r.position!==void 0||_r.normal!==void 0||_r.color!==void 0)&&Ye.update(U,H,kn),(xn||ke.receiveShadow!==U.receiveShadow)&&(ke.receiveShadow=U.receiveShadow,Lt.setValue(L,"receiveShadow",U.receiveShadow)),G.isMeshGouraudMaterial&&G.envMap!==null&&(qn.envMap.value=Oe,qn.flipEnvMap.value=Oe.isCubeTexture&&Oe.isRenderTargetTexture===!1?-1:1),G.isMeshStandardMaterial&&G.envMap===null&&N.environment!==null&&(qn.envMapIntensity.value=N.environmentIntensity),xn&&(Lt.setValue(L,"toneMappingExposure",x.toneMappingExposure),ke.needsLights&&Jd(qn,gr),ue&&G.fog===!0&&_e.refreshFogUniforms(qn,ue),_e.refreshMaterialUniforms(qn,G,V,q,m.state.transmissionRenderTarget[T.id]),Jo.upload(L,_u(ke),qn,C)),G.isShaderMaterial&&G.uniformsNeedUpdate===!0&&(Jo.upload(L,_u(ke),qn,C),G.uniformsNeedUpdate=!1),G.isSpriteMaterial&&Lt.setValue(L,"center",U.center),Lt.setValue(L,"modelViewMatrix",U.modelViewMatrix),Lt.setValue(L,"normalMatrix",U.normalMatrix),Lt.setValue(L,"modelMatrix",U.matrixWorld),G.isShaderMaterial||G.isRawShaderMaterial){const Tn=G.uniformsGroups;for(let wi=0,Ei=Tn.length;wi<Ei;wi++){const vu=Tn[wi];D.update(vu,kn),D.bind(vu,kn)}}return kn}function Jd(T,N){T.ambientLightColor.needsUpdate=N,T.lightProbe.needsUpdate=N,T.directionalLights.needsUpdate=N,T.directionalLightShadows.needsUpdate=N,T.pointLights.needsUpdate=N,T.pointLightShadows.needsUpdate=N,T.spotLights.needsUpdate=N,T.spotLightShadows.needsUpdate=N,T.rectAreaLights.needsUpdate=N,T.hemisphereLights.needsUpdate=N}function Qd(T){return T.isMeshLambertMaterial||T.isMeshToonMaterial||T.isMeshPhongMaterial||T.isMeshStandardMaterial||T.isShadowMaterial||T.isShaderMaterial&&T.lights===!0}this.getActiveCubeFace=function(){return A},this.getActiveMipmapLevel=function(){return E},this.getRenderTarget=function(){return R},this.setRenderTargetTextures=function(T,N,H){be.get(T.texture).__webglTexture=N,be.get(T.depthTexture).__webglTexture=H;const G=be.get(T);G.__hasExternalTextures=!0,G.__autoAllocateDepthBuffer=H===void 0,G.__autoAllocateDepthBuffer||ie.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),G.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(T,N){const H=be.get(T);H.__webglFramebuffer=N,H.__useDefaultFramebuffer=N===void 0},this.setRenderTarget=function(T,N=0,H=0){R=T,A=N,E=H;let G=!0,U=null,ue=!1,ye=!1;if(T){const Oe=be.get(T);if(Oe.__useDefaultFramebuffer!==void 0)de.bindFramebuffer(L.FRAMEBUFFER,null),G=!1;else if(Oe.__webglFramebuffer===void 0)C.setupRenderTarget(T);else if(Oe.__hasExternalTextures)C.rebindTextures(T,be.get(T.texture).__webglTexture,be.get(T.depthTexture).__webglTexture);else if(T.depthBuffer){const Fe=T.depthTexture;if(Oe.__boundDepthTexture!==Fe){if(Fe!==null&&be.has(Fe)&&(T.width!==Fe.image.width||T.height!==Fe.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");C.setupDepthRenderbuffer(T)}}const $e=T.texture;($e.isData3DTexture||$e.isDataArrayTexture||$e.isCompressedArrayTexture)&&(ye=!0);const et=be.get(T).__webglFramebuffer;T.isWebGLCubeRenderTarget?(Array.isArray(et[N])?U=et[N][H]:U=et[N],ue=!0):T.samples>0&&C.useMultisampledRTT(T)===!1?U=be.get(T).__webglMultisampledFramebuffer:Array.isArray(et)?U=et[H]:U=et,I.copy(T.viewport),B.copy(T.scissor),O=T.scissorTest}else I.copy(Se).multiplyScalar(V).floor(),B.copy(Ze).multiplyScalar(V).floor(),O=pt;if(de.bindFramebuffer(L.FRAMEBUFFER,U)&&G&&de.drawBuffers(T,U),de.viewport(I),de.scissor(B),de.setScissorTest(O),ue){const Oe=be.get(T.texture);L.framebufferTexture2D(L.FRAMEBUFFER,L.COLOR_ATTACHMENT0,L.TEXTURE_CUBE_MAP_POSITIVE_X+N,Oe.__webglTexture,H)}else if(ye){const Oe=be.get(T.texture),$e=N||0;L.framebufferTextureLayer(L.FRAMEBUFFER,L.COLOR_ATTACHMENT0,Oe.__webglTexture,H||0,$e)}b=-1},this.readRenderTargetPixels=function(T,N,H,G,U,ue,ye){if(!(T&&T.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Ue=be.get(T).__webglFramebuffer;if(T.isWebGLCubeRenderTarget&&ye!==void 0&&(Ue=Ue[ye]),Ue){de.bindFramebuffer(L.FRAMEBUFFER,Ue);try{const Oe=T.texture,$e=Oe.format,et=Oe.type;if(!Ee.textureFormatReadable($e)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!Ee.textureTypeReadable(et)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}N>=0&&N<=T.width-G&&H>=0&&H<=T.height-U&&L.readPixels(N,H,G,U,nt.convert($e),nt.convert(et),ue)}finally{const Oe=R!==null?be.get(R).__webglFramebuffer:null;de.bindFramebuffer(L.FRAMEBUFFER,Oe)}}},this.readRenderTargetPixelsAsync=async function(T,N,H,G,U,ue,ye){if(!(T&&T.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Ue=be.get(T).__webglFramebuffer;if(T.isWebGLCubeRenderTarget&&ye!==void 0&&(Ue=Ue[ye]),Ue){const Oe=T.texture,$e=Oe.format,et=Oe.type;if(!Ee.textureFormatReadable($e))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!Ee.textureTypeReadable(et))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(N>=0&&N<=T.width-G&&H>=0&&H<=T.height-U){de.bindFramebuffer(L.FRAMEBUFFER,Ue);const Fe=L.createBuffer();L.bindBuffer(L.PIXEL_PACK_BUFFER,Fe),L.bufferData(L.PIXEL_PACK_BUFFER,ue.byteLength,L.STREAM_READ),L.readPixels(N,H,G,U,nt.convert($e),nt.convert(et),0);const ht=R!==null?be.get(R).__webglFramebuffer:null;de.bindFramebuffer(L.FRAMEBUFFER,ht);const At=L.fenceSync(L.SYNC_GPU_COMMANDS_COMPLETE,0);return L.flush(),await dm(L,At,4),L.bindBuffer(L.PIXEL_PACK_BUFFER,Fe),L.getBufferSubData(L.PIXEL_PACK_BUFFER,0,ue),L.deleteBuffer(Fe),L.deleteSync(At),ue}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(T,N=null,H=0){T.isTexture!==!0&&(Dr("WebGLRenderer: copyFramebufferToTexture function signature has changed."),N=arguments[0]||null,T=arguments[1]);const G=Math.pow(2,-H),U=Math.floor(T.image.width*G),ue=Math.floor(T.image.height*G),ye=N!==null?N.x:0,Ue=N!==null?N.y:0;C.setTexture2D(T,0),L.copyTexSubImage2D(L.TEXTURE_2D,H,0,0,ye,Ue,U,ue),de.unbindTexture()},this.copyTextureToTexture=function(T,N,H=null,G=null,U=0){T.isTexture!==!0&&(Dr("WebGLRenderer: copyTextureToTexture function signature has changed."),G=arguments[0]||null,T=arguments[1],N=arguments[2],U=arguments[3]||0,H=null);let ue,ye,Ue,Oe,$e,et,Fe,ht,At;const Pt=T.isCompressedTexture?T.mipmaps[U]:T.image;H!==null?(ue=H.max.x-H.min.x,ye=H.max.y-H.min.y,Ue=H.isBox3?H.max.z-H.min.z:1,Oe=H.min.x,$e=H.min.y,et=H.isBox3?H.min.z:0):(ue=Pt.width,ye=Pt.height,Ue=Pt.depth||1,Oe=0,$e=0,et=0),G!==null?(Fe=G.x,ht=G.y,At=G.z):(Fe=0,ht=0,At=0);const gn=nt.convert(N.format),mt=nt.convert(N.type);let ke;N.isData3DTexture?(C.setTexture3D(N,0),ke=L.TEXTURE_3D):N.isDataArrayTexture||N.isCompressedArrayTexture?(C.setTexture2DArray(N,0),ke=L.TEXTURE_2D_ARRAY):(C.setTexture2D(N,0),ke=L.TEXTURE_2D),L.pixelStorei(L.UNPACK_FLIP_Y_WEBGL,N.flipY),L.pixelStorei(L.UNPACK_PREMULTIPLY_ALPHA_WEBGL,N.premultiplyAlpha),L.pixelStorei(L.UNPACK_ALIGNMENT,N.unpackAlignment);const ri=L.getParameter(L.UNPACK_ROW_LENGTH),gt=L.getParameter(L.UNPACK_IMAGE_HEIGHT),kn=L.getParameter(L.UNPACK_SKIP_PIXELS),Ss=L.getParameter(L.UNPACK_SKIP_ROWS),xn=L.getParameter(L.UNPACK_SKIP_IMAGES);L.pixelStorei(L.UNPACK_ROW_LENGTH,Pt.width),L.pixelStorei(L.UNPACK_IMAGE_HEIGHT,Pt.height),L.pixelStorei(L.UNPACK_SKIP_PIXELS,Oe),L.pixelStorei(L.UNPACK_SKIP_ROWS,$e),L.pixelStorei(L.UNPACK_SKIP_IMAGES,et);const gr=T.isDataArrayTexture||T.isData3DTexture,Lt=N.isDataArrayTexture||N.isData3DTexture;if(T.isRenderTargetTexture||T.isDepthTexture){const qn=be.get(T),_r=be.get(N),Tn=be.get(qn.__renderTarget),wi=be.get(_r.__renderTarget);de.bindFramebuffer(L.READ_FRAMEBUFFER,Tn.__webglFramebuffer),de.bindFramebuffer(L.DRAW_FRAMEBUFFER,wi.__webglFramebuffer);for(let Ei=0;Ei<Ue;Ei++)gr&&L.framebufferTextureLayer(L.READ_FRAMEBUFFER,L.COLOR_ATTACHMENT0,be.get(T).__webglTexture,U,et+Ei),T.isDepthTexture?(Lt&&L.framebufferTextureLayer(L.DRAW_FRAMEBUFFER,L.COLOR_ATTACHMENT0,be.get(N).__webglTexture,U,At+Ei),L.blitFramebuffer(Oe,$e,ue,ye,Fe,ht,ue,ye,L.DEPTH_BUFFER_BIT,L.NEAREST)):Lt?L.copyTexSubImage3D(ke,U,Fe,ht,At+Ei,Oe,$e,ue,ye):L.copyTexSubImage2D(ke,U,Fe,ht,At+Ei,Oe,$e,ue,ye);de.bindFramebuffer(L.READ_FRAMEBUFFER,null),de.bindFramebuffer(L.DRAW_FRAMEBUFFER,null)}else Lt?T.isDataTexture||T.isData3DTexture?L.texSubImage3D(ke,U,Fe,ht,At,ue,ye,Ue,gn,mt,Pt.data):N.isCompressedArrayTexture?L.compressedTexSubImage3D(ke,U,Fe,ht,At,ue,ye,Ue,gn,Pt.data):L.texSubImage3D(ke,U,Fe,ht,At,ue,ye,Ue,gn,mt,Pt):T.isDataTexture?L.texSubImage2D(L.TEXTURE_2D,U,Fe,ht,ue,ye,gn,mt,Pt.data):T.isCompressedTexture?L.compressedTexSubImage2D(L.TEXTURE_2D,U,Fe,ht,Pt.width,Pt.height,gn,Pt.data):L.texSubImage2D(L.TEXTURE_2D,U,Fe,ht,ue,ye,gn,mt,Pt);L.pixelStorei(L.UNPACK_ROW_LENGTH,ri),L.pixelStorei(L.UNPACK_IMAGE_HEIGHT,gt),L.pixelStorei(L.UNPACK_SKIP_PIXELS,kn),L.pixelStorei(L.UNPACK_SKIP_ROWS,Ss),L.pixelStorei(L.UNPACK_SKIP_IMAGES,xn),U===0&&N.generateMipmaps&&L.generateMipmap(ke),de.unbindTexture()},this.copyTextureToTexture3D=function(T,N,H=null,G=null,U=0){return T.isTexture!==!0&&(Dr("WebGLRenderer: copyTextureToTexture3D function signature has changed."),H=arguments[0]||null,G=arguments[1]||null,T=arguments[2],N=arguments[3],U=arguments[4]||0),Dr('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(T,N,H,G,U)},this.initRenderTarget=function(T){be.get(T).__webglFramebuffer===void 0&&C.setupRenderTarget(T)},this.initTexture=function(T){T.isCubeTexture?C.setTextureCube(T,0):T.isData3DTexture?C.setTexture3D(T,0):T.isDataArrayTexture||T.isCompressedArrayTexture?C.setTexture2DArray(T,0):C.setTexture2D(T,0),de.unbindTexture()},this.resetState=function(){A=0,E=0,R=null,de.reset(),Tt.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return _i}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorspace=at._getDrawingBufferColorSpace(e),t.unpackColorSpace=at._getUnpackColorSpace()}}class Ev extends It{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new wn,this.environmentIntensity=1,this.environmentRotation=new wn,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class Tv{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=gl,this.updateRanges=[],this.version=0,this.uuid=Nn()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let s=0,r=this.stride;s<r;s++)this.array[e+s]=t.array[n+s];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Nn()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=Nn()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const cn=new M;class Xl{constructor(e,t,n,s=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=s}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)cn.fromBufferAttribute(this,t),cn.applyMatrix4(e),this.setXYZ(t,cn.x,cn.y,cn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)cn.fromBufferAttribute(this,t),cn.applyNormalMatrix(e),this.setXYZ(t,cn.x,cn.y,cn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)cn.fromBufferAttribute(this,t),cn.transformDirection(e),this.setXYZ(t,cn.x,cn.y,cn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=Wn(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=vt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=vt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=vt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=vt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=vt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=Wn(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=Wn(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=Wn(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=Wn(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=vt(t,this.array),n=vt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=vt(t,this.array),n=vt(n,this.array),s=vt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=vt(t,this.array),n=vt(n,this.array),s=vt(s,this.array),r=vt(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this.data.array[e+3]=r,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return new $t(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new Xl(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}const Sh=new M,bh=new dt,wh=new dt,Av=new M,Eh=new Le,Ao=new M,tc=new ei,Th=new Le,nc=new da;class ql extends kt{constructor(e,t){super(e,t),this.isSkinnedMesh=!0,this.type="SkinnedMesh",this.bindMode=wu,this.bindMatrix=new Le,this.bindMatrixInverse=new Le,this.boundingBox=null,this.boundingSphere=null}computeBoundingBox(){const e=this.geometry;this.boundingBox===null&&(this.boundingBox=new pn),this.boundingBox.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,Ao),this.boundingBox.expandByPoint(Ao)}computeBoundingSphere(){const e=this.geometry;this.boundingSphere===null&&(this.boundingSphere=new ei),this.boundingSphere.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,Ao),this.boundingSphere.expandByPoint(Ao)}copy(e,t){return super.copy(e,t),this.bindMode=e.bindMode,this.bindMatrix.copy(e.bindMatrix),this.bindMatrixInverse.copy(e.bindMatrixInverse),this.skeleton=e.skeleton,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}raycast(e,t){const n=this.material,s=this.matrixWorld;n!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),tc.copy(this.boundingSphere),tc.applyMatrix4(s),e.ray.intersectsSphere(tc)!==!1&&(Th.copy(s).invert(),nc.copy(e.ray).applyMatrix4(Th),!(this.boundingBox!==null&&nc.intersectsBox(this.boundingBox)===!1)&&this._computeIntersections(e,t,nc)))}getVertexPosition(e,t){return super.getVertexPosition(e,t),this.applyBoneTransform(e,t),t}bind(e,t){this.skeleton=e,t===void 0&&(this.updateMatrixWorld(!0),this.skeleton.calculateInverses(),t=this.matrixWorld),this.bindMatrix.copy(t),this.bindMatrixInverse.copy(t).invert()}pose(){this.skeleton.pose()}normalizeSkinWeights(){const e=new dt,t=this.geometry.attributes.skinWeight;for(let n=0,s=t.count;n<s;n++){e.fromBufferAttribute(t,n);const r=1/e.manhattanLength();r!==1/0?e.multiplyScalar(r):e.set(1,0,0,0),t.setXYZW(n,e.x,e.y,e.z,e.w)}}updateMatrixWorld(e){super.updateMatrixWorld(e),this.bindMode===wu?this.bindMatrixInverse.copy(this.matrixWorld).invert():this.bindMode===Fp?this.bindMatrixInverse.copy(this.bindMatrix).invert():console.warn("THREE.SkinnedMesh: Unrecognized bindMode: "+this.bindMode)}applyBoneTransform(e,t){const n=this.skeleton,s=this.geometry;bh.fromBufferAttribute(s.attributes.skinIndex,e),wh.fromBufferAttribute(s.attributes.skinWeight,e),Sh.copy(t).applyMatrix4(this.bindMatrix),t.set(0,0,0);for(let r=0;r<4;r++){const o=wh.getComponent(r);if(o!==0){const a=bh.getComponent(r);Eh.multiplyMatrices(n.bones[a].matrixWorld,n.boneInverses[a]),t.addScaledVector(Av.copy(Sh).applyMatrix4(Eh),o)}}return t.applyMatrix4(this.bindMatrixInverse)}}class Kf extends It{constructor(){super(),this.isBone=!0,this.type="Bone"}}class Zf extends jt{constructor(e=null,t=1,n=1,s,r,o,a,c,l=dn,u=dn,h,f){super(null,o,a,c,l,u,s,r,h,f),this.isDataTexture=!0,this.image={data:e,width:t,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const Ah=new Le,Rv=new Le;class Yl{constructor(e=[],t=[]){this.uuid=Nn(),this.bones=e.slice(0),this.boneInverses=t,this.boneMatrices=null,this.boneTexture=null,this.init()}init(){const e=this.bones,t=this.boneInverses;if(this.boneMatrices=new Float32Array(e.length*16),t.length===0)this.calculateInverses();else if(e.length!==t.length){console.warn("THREE.Skeleton: Number of inverse bone matrices does not match amount of bones."),this.boneInverses=[];for(let n=0,s=this.bones.length;n<s;n++)this.boneInverses.push(new Le)}}calculateInverses(){this.boneInverses.length=0;for(let e=0,t=this.bones.length;e<t;e++){const n=new Le;this.bones[e]&&n.copy(this.bones[e].matrixWorld).invert(),this.boneInverses.push(n)}}pose(){for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&n.matrixWorld.copy(this.boneInverses[e]).invert()}for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&(n.parent&&n.parent.isBone?(n.matrix.copy(n.parent.matrixWorld).invert(),n.matrix.multiply(n.matrixWorld)):n.matrix.copy(n.matrixWorld),n.matrix.decompose(n.position,n.quaternion,n.scale))}}update(){const e=this.bones,t=this.boneInverses,n=this.boneMatrices,s=this.boneTexture;for(let r=0,o=e.length;r<o;r++){const a=e[r]?e[r].matrixWorld:Rv;Ah.multiplyMatrices(a,t[r]),Ah.toArray(n,r*16)}s!==null&&(s.needsUpdate=!0)}clone(){return new Yl(this.bones,this.boneInverses)}computeBoneTexture(){let e=Math.sqrt(this.bones.length*4);e=Math.ceil(e/4)*4,e=Math.max(e,4);const t=new Float32Array(e*e*4);t.set(this.boneMatrices);const n=new Zf(t,e,e,In,Xn);return n.needsUpdate=!0,this.boneMatrices=t,this.boneTexture=n,this}getBoneByName(e){for(let t=0,n=this.bones.length;t<n;t++){const s=this.bones[t];if(s.name===e)return s}}dispose(){this.boneTexture!==null&&(this.boneTexture.dispose(),this.boneTexture=null)}fromJSON(e,t){this.uuid=e.uuid;for(let n=0,s=e.bones.length;n<s;n++){const r=e.bones[n];let o=t[r];o===void 0&&(console.warn("THREE.Skeleton: No bone found with UUID:",r),o=new Kf),this.bones.push(o),this.boneInverses.push(new Le().fromArray(e.boneInverses[n]))}return this.init(),this}toJSON(){const e={metadata:{version:4.6,type:"Skeleton",generator:"Skeleton.toJSON"},bones:[],boneInverses:[]};e.uuid=this.uuid;const t=this.bones,n=this.boneInverses;for(let s=0,r=t.length;s<r;s++){const o=t[s];e.bones.push(o.uuid);const a=n[s];e.boneInverses.push(a.toArray())}return e}}class xl extends $t{constructor(e,t,n,s=1){super(e,t,n),this.isInstancedBufferAttribute=!0,this.meshPerAttribute=s}copy(e){return super.copy(e),this.meshPerAttribute=e.meshPerAttribute,this}toJSON(){const e=super.toJSON();return e.meshPerAttribute=this.meshPerAttribute,e.isInstancedBufferAttribute=!0,e}}const Fs=new Le,Rh=new Le,Ro=[],Ch=new pn,Cv=new Le,Sr=new kt,br=new ei;class Pv extends kt{constructor(e,t,n){super(e,t),this.isInstancedMesh=!0,this.instanceMatrix=new xl(new Float32Array(n*16),16),this.instanceColor=null,this.morphTexture=null,this.count=n,this.boundingBox=null,this.boundingSphere=null;for(let s=0;s<n;s++)this.setMatrixAt(s,Cv)}computeBoundingBox(){const e=this.geometry,t=this.count;this.boundingBox===null&&(this.boundingBox=new pn),e.boundingBox===null&&e.computeBoundingBox(),this.boundingBox.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,Fs),Ch.copy(e.boundingBox).applyMatrix4(Fs),this.boundingBox.union(Ch)}computeBoundingSphere(){const e=this.geometry,t=this.count;this.boundingSphere===null&&(this.boundingSphere=new ei),e.boundingSphere===null&&e.computeBoundingSphere(),this.boundingSphere.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,Fs),br.copy(e.boundingSphere).applyMatrix4(Fs),this.boundingSphere.union(br)}copy(e,t){return super.copy(e,t),this.instanceMatrix.copy(e.instanceMatrix),e.morphTexture!==null&&(this.morphTexture=e.morphTexture.clone()),e.instanceColor!==null&&(this.instanceColor=e.instanceColor.clone()),this.count=e.count,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}getColorAt(e,t){t.fromArray(this.instanceColor.array,e*3)}getMatrixAt(e,t){t.fromArray(this.instanceMatrix.array,e*16)}getMorphAt(e,t){const n=t.morphTargetInfluences,s=this.morphTexture.source.data.data,r=n.length+1,o=e*r+1;for(let a=0;a<n.length;a++)n[a]=s[o+a]}raycast(e,t){const n=this.matrixWorld,s=this.count;if(Sr.geometry=this.geometry,Sr.material=this.material,Sr.material!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),br.copy(this.boundingSphere),br.applyMatrix4(n),e.ray.intersectsSphere(br)!==!1))for(let r=0;r<s;r++){this.getMatrixAt(r,Fs),Rh.multiplyMatrices(n,Fs),Sr.matrixWorld=Rh,Sr.raycast(e,Ro);for(let o=0,a=Ro.length;o<a;o++){const c=Ro[o];c.instanceId=r,c.object=this,t.push(c)}Ro.length=0}}setColorAt(e,t){this.instanceColor===null&&(this.instanceColor=new xl(new Float32Array(this.instanceMatrix.count*3).fill(1),3)),t.toArray(this.instanceColor.array,e*3)}setMatrixAt(e,t){t.toArray(this.instanceMatrix.array,e*16)}setMorphAt(e,t){const n=t.morphTargetInfluences,s=n.length+1;this.morphTexture===null&&(this.morphTexture=new Zf(new Float32Array(s*this.count),s,this.count,Fl,Xn));const r=this.morphTexture.source.data.data;let o=0;for(let l=0;l<n.length;l++)o+=n[l];const a=this.geometry.morphTargetsRelative?1:1-o,c=s*e;r[c]=a,r.set(n,c+1)}updateMorphTargets(){}dispose(){return this.dispatchEvent({type:"dispose"}),this.morphTexture!==null&&(this.morphTexture.dispose(),this.morphTexture=null),this}}class _s extends Kn{static get type(){return"LineBasicMaterial"}constructor(e){super(),this.isLineBasicMaterial=!0,this.color=new ze(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const ia=new M,sa=new M,Ph=new Le,wr=new da,Co=new ei,ic=new M,Lh=new M;class jl extends It{constructor(e=new zt,t=new _s){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let s=1,r=t.count;s<r;s++)ia.fromBufferAttribute(t,s-1),sa.fromBufferAttribute(t,s),n[s]=n[s-1],n[s]+=ia.distanceTo(sa);e.setAttribute("lineDistance",new rt(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Line.threshold,o=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Co.copy(n.boundingSphere),Co.applyMatrix4(s),Co.radius+=r,e.ray.intersectsSphere(Co)===!1)return;Ph.copy(s).invert(),wr.copy(e.ray).applyMatrix4(Ph);const a=r/((this.scale.x+this.scale.y+this.scale.z)/3),c=a*a,l=this.isLineSegments?2:1,u=n.index,f=n.attributes.position;if(u!==null){const d=Math.max(0,o.start),g=Math.min(u.count,o.start+o.count);for(let _=d,p=g-1;_<p;_+=l){const m=u.getX(_),v=u.getX(_+1),y=Po(this,e,wr,c,m,v);y&&t.push(y)}if(this.isLineLoop){const _=u.getX(g-1),p=u.getX(d),m=Po(this,e,wr,c,_,p);m&&t.push(m)}}else{const d=Math.max(0,o.start),g=Math.min(f.count,o.start+o.count);for(let _=d,p=g-1;_<p;_+=l){const m=Po(this,e,wr,c,_,_+1);m&&t.push(m)}if(this.isLineLoop){const _=Po(this,e,wr,c,g-1,d);_&&t.push(_)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}}function Po(i,e,t,n,s,r){const o=i.geometry.attributes.position;if(ia.fromBufferAttribute(o,s),sa.fromBufferAttribute(o,r),t.distanceSqToSegment(ia,sa,ic,Lh)>n)return;ic.applyMatrix4(i.matrixWorld);const c=e.ray.origin.distanceTo(ic);if(!(c<e.near||c>e.far))return{distance:c,point:Lh.clone().applyMatrix4(i.matrixWorld),index:s,face:null,faceIndex:null,barycoord:null,object:i}}const Ih=new M,Dh=new M;class Kr extends jl{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let s=0,r=t.count;s<r;s+=2)Ih.fromBufferAttribute(t,s),Dh.fromBufferAttribute(t,s+1),n[s]=s===0?0:n[s-1],n[s+1]=n[s]+Ih.distanceTo(Dh);e.setAttribute("lineDistance",new rt(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class Jf extends jl{constructor(e,t){super(e,t),this.isLineLoop=!0,this.type="LineLoop"}}class Qf extends Kn{static get type(){return"PointsMaterial"}constructor(e){super(),this.isPointsMaterial=!0,this.color=new ze(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Nh=new Le,vl=new da,Lo=new ei,Io=new M;class Lv extends It{constructor(e=new zt,t=new Qf){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Points.threshold,o=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Lo.copy(n.boundingSphere),Lo.applyMatrix4(s),Lo.radius+=r,e.ray.intersectsSphere(Lo)===!1)return;Nh.copy(s).invert(),vl.copy(e.ray).applyMatrix4(Nh);const a=r/((this.scale.x+this.scale.y+this.scale.z)/3),c=a*a,l=n.index,h=n.attributes.position;if(l!==null){const f=Math.max(0,o.start),d=Math.min(l.count,o.start+o.count);for(let g=f,_=d;g<_;g++){const p=l.getX(g);Io.fromBufferAttribute(h,p),Uh(Io,p,c,s,e,t,this)}}else{const f=Math.max(0,o.start),d=Math.min(h.count,o.start+o.count);for(let g=f,_=d;g<_;g++)Io.fromBufferAttribute(h,g),Uh(Io,g,c,s,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}}function Uh(i,e,t,n,s,r,o){const a=vl.distanceSqToPoint(i);if(a<t){const c=new M;vl.closestPointToPoint(i,c),c.applyMatrix4(n);const l=s.ray.origin.distanceTo(c);if(l<s.near||l>s.far)return;r.push({distance:l,distanceToRay:Math.sqrt(a),point:c,index:e,face:null,faceIndex:null,barycoord:null,object:o})}}class ti{constructor(){this.type="Curve",this.arcLengthDivisions=200}getPoint(){return console.warn("THREE.Curve: .getPoint() not implemented."),null}getPointAt(e,t){const n=this.getUtoTmapping(e);return this.getPoint(n,t)}getPoints(e=5){const t=[];for(let n=0;n<=e;n++)t.push(this.getPoint(n/e));return t}getSpacedPoints(e=5){const t=[];for(let n=0;n<=e;n++)t.push(this.getPointAt(n/e));return t}getLength(){const e=this.getLengths();return e[e.length-1]}getLengths(e=this.arcLengthDivisions){if(this.cacheArcLengths&&this.cacheArcLengths.length===e+1&&!this.needsUpdate)return this.cacheArcLengths;this.needsUpdate=!1;const t=[];let n,s=this.getPoint(0),r=0;t.push(0);for(let o=1;o<=e;o++)n=this.getPoint(o/e),r+=n.distanceTo(s),t.push(r),s=n;return this.cacheArcLengths=t,t}updateArcLengths(){this.needsUpdate=!0,this.getLengths()}getUtoTmapping(e,t){const n=this.getLengths();let s=0;const r=n.length;let o;t?o=t:o=e*n[r-1];let a=0,c=r-1,l;for(;a<=c;)if(s=Math.floor(a+(c-a)/2),l=n[s]-o,l<0)a=s+1;else if(l>0)c=s-1;else{c=s;break}if(s=c,n[s]===o)return s/(r-1);const u=n[s],f=n[s+1]-u,d=(o-u)/f;return(s+d)/(r-1)}getTangent(e,t){let s=e-1e-4,r=e+1e-4;s<0&&(s=0),r>1&&(r=1);const o=this.getPoint(s),a=this.getPoint(r),c=t||(o.isVector2?new te:new M);return c.copy(a).sub(o).normalize(),c}getTangentAt(e,t){const n=this.getUtoTmapping(e);return this.getTangent(n,t)}computeFrenetFrames(e,t){const n=new M,s=[],r=[],o=[],a=new M,c=new Le;for(let d=0;d<=e;d++){const g=d/e;s[d]=this.getTangentAt(g,new M)}r[0]=new M,o[0]=new M;let l=Number.MAX_VALUE;const u=Math.abs(s[0].x),h=Math.abs(s[0].y),f=Math.abs(s[0].z);u<=l&&(l=u,n.set(1,0,0)),h<=l&&(l=h,n.set(0,1,0)),f<=l&&n.set(0,0,1),a.crossVectors(s[0],n).normalize(),r[0].crossVectors(s[0],a),o[0].crossVectors(s[0],r[0]);for(let d=1;d<=e;d++){if(r[d]=r[d-1].clone(),o[d]=o[d-1].clone(),a.crossVectors(s[d-1],s[d]),a.length()>Number.EPSILON){a.normalize();const g=Math.acos(Wt(s[d-1].dot(s[d]),-1,1));r[d].applyMatrix4(c.makeRotationAxis(a,g))}o[d].crossVectors(s[d],r[d])}if(t===!0){let d=Math.acos(Wt(r[0].dot(r[e]),-1,1));d/=e,s[0].dot(a.crossVectors(r[0],r[e]))>0&&(d=-d);for(let g=1;g<=e;g++)r[g].applyMatrix4(c.makeRotationAxis(s[g],d*g)),o[g].crossVectors(s[g],r[g])}return{tangents:s,normals:r,binormals:o}}clone(){return new this.constructor().copy(this)}copy(e){return this.arcLengthDivisions=e.arcLengthDivisions,this}toJSON(){const e={metadata:{version:4.6,type:"Curve",generator:"Curve.toJSON"}};return e.arcLengthDivisions=this.arcLengthDivisions,e.type=this.type,e}fromJSON(e){return this.arcLengthDivisions=e.arcLengthDivisions,this}}class $l extends ti{constructor(e=0,t=0,n=1,s=1,r=0,o=Math.PI*2,a=!1,c=0){super(),this.isEllipseCurve=!0,this.type="EllipseCurve",this.aX=e,this.aY=t,this.xRadius=n,this.yRadius=s,this.aStartAngle=r,this.aEndAngle=o,this.aClockwise=a,this.aRotation=c}getPoint(e,t=new te){const n=t,s=Math.PI*2;let r=this.aEndAngle-this.aStartAngle;const o=Math.abs(r)<Number.EPSILON;for(;r<0;)r+=s;for(;r>s;)r-=s;r<Number.EPSILON&&(o?r=0:r=s),this.aClockwise===!0&&!o&&(r===s?r=-s:r=r-s);const a=this.aStartAngle+e*r;let c=this.aX+this.xRadius*Math.cos(a),l=this.aY+this.yRadius*Math.sin(a);if(this.aRotation!==0){const u=Math.cos(this.aRotation),h=Math.sin(this.aRotation),f=c-this.aX,d=l-this.aY;c=f*u-d*h+this.aX,l=f*h+d*u+this.aY}return n.set(c,l)}copy(e){return super.copy(e),this.aX=e.aX,this.aY=e.aY,this.xRadius=e.xRadius,this.yRadius=e.yRadius,this.aStartAngle=e.aStartAngle,this.aEndAngle=e.aEndAngle,this.aClockwise=e.aClockwise,this.aRotation=e.aRotation,this}toJSON(){const e=super.toJSON();return e.aX=this.aX,e.aY=this.aY,e.xRadius=this.xRadius,e.yRadius=this.yRadius,e.aStartAngle=this.aStartAngle,e.aEndAngle=this.aEndAngle,e.aClockwise=this.aClockwise,e.aRotation=this.aRotation,e}fromJSON(e){return super.fromJSON(e),this.aX=e.aX,this.aY=e.aY,this.xRadius=e.xRadius,this.yRadius=e.yRadius,this.aStartAngle=e.aStartAngle,this.aEndAngle=e.aEndAngle,this.aClockwise=e.aClockwise,this.aRotation=e.aRotation,this}}class Iv extends $l{constructor(e,t,n,s,r,o){super(e,t,n,n,s,r,o),this.isArcCurve=!0,this.type="ArcCurve"}}function Kl(){let i=0,e=0,t=0,n=0;function s(r,o,a,c){i=r,e=a,t=-3*r+3*o-2*a-c,n=2*r-2*o+a+c}return{initCatmullRom:function(r,o,a,c,l){s(o,a,l*(a-r),l*(c-o))},initNonuniformCatmullRom:function(r,o,a,c,l,u,h){let f=(o-r)/l-(a-r)/(l+u)+(a-o)/u,d=(a-o)/u-(c-o)/(u+h)+(c-a)/h;f*=u,d*=u,s(o,a,f,d)},calc:function(r){const o=r*r,a=o*r;return i+e*r+t*o+n*a}}}const Do=new M,sc=new Kl,rc=new Kl,oc=new Kl;class ga extends ti{constructor(e=[],t=!1,n="centripetal",s=.5){super(),this.isCatmullRomCurve3=!0,this.type="CatmullRomCurve3",this.points=e,this.closed=t,this.curveType=n,this.tension=s}getPoint(e,t=new M){const n=t,s=this.points,r=s.length,o=(r-(this.closed?0:1))*e;let a=Math.floor(o),c=o-a;this.closed?a+=a>0?0:(Math.floor(Math.abs(a)/r)+1)*r:c===0&&a===r-1&&(a=r-2,c=1);let l,u;this.closed||a>0?l=s[(a-1)%r]:(Do.subVectors(s[0],s[1]).add(s[0]),l=Do);const h=s[a%r],f=s[(a+1)%r];if(this.closed||a+2<r?u=s[(a+2)%r]:(Do.subVectors(s[r-1],s[r-2]).add(s[r-1]),u=Do),this.curveType==="centripetal"||this.curveType==="chordal"){const d=this.curveType==="chordal"?.5:.25;let g=Math.pow(l.distanceToSquared(h),d),_=Math.pow(h.distanceToSquared(f),d),p=Math.pow(f.distanceToSquared(u),d);_<1e-4&&(_=1),g<1e-4&&(g=_),p<1e-4&&(p=_),sc.initNonuniformCatmullRom(l.x,h.x,f.x,u.x,g,_,p),rc.initNonuniformCatmullRom(l.y,h.y,f.y,u.y,g,_,p),oc.initNonuniformCatmullRom(l.z,h.z,f.z,u.z,g,_,p)}else this.curveType==="catmullrom"&&(sc.initCatmullRom(l.x,h.x,f.x,u.x,this.tension),rc.initCatmullRom(l.y,h.y,f.y,u.y,this.tension),oc.initCatmullRom(l.z,h.z,f.z,u.z,this.tension));return n.set(sc.calc(c),rc.calc(c),oc.calc(c)),n}copy(e){super.copy(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(s.clone())}return this.closed=e.closed,this.curveType=e.curveType,this.tension=e.tension,this}toJSON(){const e=super.toJSON();e.points=[];for(let t=0,n=this.points.length;t<n;t++){const s=this.points[t];e.points.push(s.toArray())}return e.closed=this.closed,e.curveType=this.curveType,e.tension=this.tension,e}fromJSON(e){super.fromJSON(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(new M().fromArray(s))}return this.closed=e.closed,this.curveType=e.curveType,this.tension=e.tension,this}}function Oh(i,e,t,n,s){const r=(n-e)*.5,o=(s-t)*.5,a=i*i,c=i*a;return(2*t-2*n+r+o)*c+(-3*t+3*n-2*r-o)*a+r*i+t}function Dv(i,e){const t=1-i;return t*t*e}function Nv(i,e){return 2*(1-i)*i*e}function Uv(i,e){return i*i*e}function Fr(i,e,t,n){return Dv(i,e)+Nv(i,t)+Uv(i,n)}function Ov(i,e){const t=1-i;return t*t*t*e}function Fv(i,e){const t=1-i;return 3*t*t*i*e}function Bv(i,e){return 3*(1-i)*i*i*e}function kv(i,e){return i*i*i*e}function Br(i,e,t,n,s){return Ov(i,e)+Fv(i,t)+Bv(i,n)+kv(i,s)}class ed extends ti{constructor(e=new te,t=new te,n=new te,s=new te){super(),this.isCubicBezierCurve=!0,this.type="CubicBezierCurve",this.v0=e,this.v1=t,this.v2=n,this.v3=s}getPoint(e,t=new te){const n=t,s=this.v0,r=this.v1,o=this.v2,a=this.v3;return n.set(Br(e,s.x,r.x,o.x,a.x),Br(e,s.y,r.y,o.y,a.y)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this.v3.copy(e.v3),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e.v3=this.v3.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this.v3.fromArray(e.v3),this}}class zv extends ti{constructor(e=new M,t=new M,n=new M,s=new M){super(),this.isCubicBezierCurve3=!0,this.type="CubicBezierCurve3",this.v0=e,this.v1=t,this.v2=n,this.v3=s}getPoint(e,t=new M){const n=t,s=this.v0,r=this.v1,o=this.v2,a=this.v3;return n.set(Br(e,s.x,r.x,o.x,a.x),Br(e,s.y,r.y,o.y,a.y),Br(e,s.z,r.z,o.z,a.z)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this.v3.copy(e.v3),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e.v3=this.v3.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this.v3.fromArray(e.v3),this}}class td extends ti{constructor(e=new te,t=new te){super(),this.isLineCurve=!0,this.type="LineCurve",this.v1=e,this.v2=t}getPoint(e,t=new te){const n=t;return e===1?n.copy(this.v2):(n.copy(this.v2).sub(this.v1),n.multiplyScalar(e).add(this.v1)),n}getPointAt(e,t){return this.getPoint(e,t)}getTangent(e,t=new te){return t.subVectors(this.v2,this.v1).normalize()}getTangentAt(e,t){return this.getTangent(e,t)}copy(e){return super.copy(e),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class nd extends ti{constructor(e=new M,t=new M){super(),this.isLineCurve3=!0,this.type="LineCurve3",this.v1=e,this.v2=t}getPoint(e,t=new M){const n=t;return e===1?n.copy(this.v2):(n.copy(this.v2).sub(this.v1),n.multiplyScalar(e).add(this.v1)),n}getPointAt(e,t){return this.getPoint(e,t)}getTangent(e,t=new M){return t.subVectors(this.v2,this.v1).normalize()}getTangentAt(e,t){return this.getTangent(e,t)}copy(e){return super.copy(e),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class id extends ti{constructor(e=new te,t=new te,n=new te){super(),this.isQuadraticBezierCurve=!0,this.type="QuadraticBezierCurve",this.v0=e,this.v1=t,this.v2=n}getPoint(e,t=new te){const n=t,s=this.v0,r=this.v1,o=this.v2;return n.set(Fr(e,s.x,r.x,o.x),Fr(e,s.y,r.y,o.y)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class Zl extends ti{constructor(e=new M,t=new M,n=new M){super(),this.isQuadraticBezierCurve3=!0,this.type="QuadraticBezierCurve3",this.v0=e,this.v1=t,this.v2=n}getPoint(e,t=new M){const n=t,s=this.v0,r=this.v1,o=this.v2;return n.set(Fr(e,s.x,r.x,o.x),Fr(e,s.y,r.y,o.y),Fr(e,s.z,r.z,o.z)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class sd extends ti{constructor(e=[]){super(),this.isSplineCurve=!0,this.type="SplineCurve",this.points=e}getPoint(e,t=new te){const n=t,s=this.points,r=(s.length-1)*e,o=Math.floor(r),a=r-o,c=s[o===0?o:o-1],l=s[o],u=s[o>s.length-2?s.length-1:o+1],h=s[o>s.length-3?s.length-1:o+2];return n.set(Oh(a,c.x,l.x,u.x,h.x),Oh(a,c.y,l.y,u.y,h.y)),n}copy(e){super.copy(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(s.clone())}return this}toJSON(){const e=super.toJSON();e.points=[];for(let t=0,n=this.points.length;t<n;t++){const s=this.points[t];e.points.push(s.toArray())}return e}fromJSON(e){super.fromJSON(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(new te().fromArray(s))}return this}}var ra=Object.freeze({__proto__:null,ArcCurve:Iv,CatmullRomCurve3:ga,CubicBezierCurve:ed,CubicBezierCurve3:zv,EllipseCurve:$l,LineCurve:td,LineCurve3:nd,QuadraticBezierCurve:id,QuadraticBezierCurve3:Zl,SplineCurve:sd});class Hv extends ti{constructor(){super(),this.type="CurvePath",this.curves=[],this.autoClose=!1}add(e){this.curves.push(e)}closePath(){const e=this.curves[0].getPoint(0),t=this.curves[this.curves.length-1].getPoint(1);if(!e.equals(t)){const n=e.isVector2===!0?"LineCurve":"LineCurve3";this.curves.push(new ra[n](t,e))}return this}getPoint(e,t){const n=e*this.getLength(),s=this.getCurveLengths();let r=0;for(;r<s.length;){if(s[r]>=n){const o=s[r]-n,a=this.curves[r],c=a.getLength(),l=c===0?0:1-o/c;return a.getPointAt(l,t)}r++}return null}getLength(){const e=this.getCurveLengths();return e[e.length-1]}updateArcLengths(){this.needsUpdate=!0,this.cacheLengths=null,this.getCurveLengths()}getCurveLengths(){if(this.cacheLengths&&this.cacheLengths.length===this.curves.length)return this.cacheLengths;const e=[];let t=0;for(let n=0,s=this.curves.length;n<s;n++)t+=this.curves[n].getLength(),e.push(t);return this.cacheLengths=e,e}getSpacedPoints(e=40){const t=[];for(let n=0;n<=e;n++)t.push(this.getPoint(n/e));return this.autoClose&&t.push(t[0]),t}getPoints(e=12){const t=[];let n;for(let s=0,r=this.curves;s<r.length;s++){const o=r[s],a=o.isEllipseCurve?e*2:o.isLineCurve||o.isLineCurve3?1:o.isSplineCurve?e*o.points.length:e,c=o.getPoints(a);for(let l=0;l<c.length;l++){const u=c[l];n&&n.equals(u)||(t.push(u),n=u)}}return this.autoClose&&t.length>1&&!t[t.length-1].equals(t[0])&&t.push(t[0]),t}copy(e){super.copy(e),this.curves=[];for(let t=0,n=e.curves.length;t<n;t++){const s=e.curves[t];this.curves.push(s.clone())}return this.autoClose=e.autoClose,this}toJSON(){const e=super.toJSON();e.autoClose=this.autoClose,e.curves=[];for(let t=0,n=this.curves.length;t<n;t++){const s=this.curves[t];e.curves.push(s.toJSON())}return e}fromJSON(e){super.fromJSON(e),this.autoClose=e.autoClose,this.curves=[];for(let t=0,n=e.curves.length;t<n;t++){const s=e.curves[t];this.curves.push(new ra[s.type]().fromJSON(s))}return this}}class yl extends Hv{constructor(e){super(),this.type="Path",this.currentPoint=new te,e&&this.setFromPoints(e)}setFromPoints(e){this.moveTo(e[0].x,e[0].y);for(let t=1,n=e.length;t<n;t++)this.lineTo(e[t].x,e[t].y);return this}moveTo(e,t){return this.currentPoint.set(e,t),this}lineTo(e,t){const n=new td(this.currentPoint.clone(),new te(e,t));return this.curves.push(n),this.currentPoint.set(e,t),this}quadraticCurveTo(e,t,n,s){const r=new id(this.currentPoint.clone(),new te(e,t),new te(n,s));return this.curves.push(r),this.currentPoint.set(n,s),this}bezierCurveTo(e,t,n,s,r,o){const a=new ed(this.currentPoint.clone(),new te(e,t),new te(n,s),new te(r,o));return this.curves.push(a),this.currentPoint.set(r,o),this}splineThru(e){const t=[this.currentPoint.clone()].concat(e),n=new sd(t);return this.curves.push(n),this.currentPoint.copy(e[e.length-1]),this}arc(e,t,n,s,r,o){const a=this.currentPoint.x,c=this.currentPoint.y;return this.absarc(e+a,t+c,n,s,r,o),this}absarc(e,t,n,s,r,o){return this.absellipse(e,t,n,n,s,r,o),this}ellipse(e,t,n,s,r,o,a,c){const l=this.currentPoint.x,u=this.currentPoint.y;return this.absellipse(e+l,t+u,n,s,r,o,a,c),this}absellipse(e,t,n,s,r,o,a,c){const l=new $l(e,t,n,s,r,o,a,c);if(this.curves.length>0){const h=l.getPoint(0);h.equals(this.currentPoint)||this.lineTo(h.x,h.y)}this.curves.push(l);const u=l.getPoint(1);return this.currentPoint.copy(u),this}copy(e){return super.copy(e),this.currentPoint.copy(e.currentPoint),this}toJSON(){const e=super.toJSON();return e.currentPoint=this.currentPoint.toArray(),e}fromJSON(e){return super.fromJSON(e),this.currentPoint.fromArray(e.currentPoint),this}}class Zr extends zt{constructor(e=[new te(0,-.5),new te(.5,0),new te(0,.5)],t=12,n=0,s=Math.PI*2){super(),this.type="LatheGeometry",this.parameters={points:e,segments:t,phiStart:n,phiLength:s},t=Math.floor(t),s=Wt(s,0,Math.PI*2);const r=[],o=[],a=[],c=[],l=[],u=1/t,h=new M,f=new te,d=new M,g=new M,_=new M;let p=0,m=0;for(let v=0;v<=e.length-1;v++)switch(v){case 0:p=e[v+1].x-e[v].x,m=e[v+1].y-e[v].y,d.x=m*1,d.y=-p,d.z=m*0,_.copy(d),d.normalize(),c.push(d.x,d.y,d.z);break;case e.length-1:c.push(_.x,_.y,_.z);break;default:p=e[v+1].x-e[v].x,m=e[v+1].y-e[v].y,d.x=m*1,d.y=-p,d.z=m*0,g.copy(d),d.x+=_.x,d.y+=_.y,d.z+=_.z,d.normalize(),c.push(d.x,d.y,d.z),_.copy(g)}for(let v=0;v<=t;v++){const y=n+v*u*s,x=Math.sin(y),P=Math.cos(y);for(let A=0;A<=e.length-1;A++){h.x=e[A].x*x,h.y=e[A].y,h.z=e[A].x*P,o.push(h.x,h.y,h.z),f.x=v/t,f.y=A/(e.length-1),a.push(f.x,f.y);const E=c[3*A+0]*x,R=c[3*A+1],b=c[3*A+0]*P;l.push(E,R,b)}}for(let v=0;v<t;v++)for(let y=0;y<e.length-1;y++){const x=y+v*e.length,P=x,A=x+e.length,E=x+e.length+1,R=x+1;r.push(P,A,R),r.push(E,R,A)}this.setIndex(r),this.setAttribute("position",new rt(o,3)),this.setAttribute("uv",new rt(a,2)),this.setAttribute("normal",new rt(l,3))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Zr(e.points,e.segments,e.phiStart,e.phiLength)}}class Jl extends Zr{constructor(e=1,t=1,n=4,s=8){const r=new yl;r.absarc(0,-t/2,e,Math.PI*1.5,0),r.absarc(0,t/2,e,0,Math.PI*.5),super(r.getPoints(n),s),this.type="CapsuleGeometry",this.parameters={radius:e,length:t,capSegments:n,radialSegments:s}}static fromJSON(e){return new Jl(e.radius,e.length,e.capSegments,e.radialSegments)}}class Yi extends zt{constructor(e=1,t=32,n=0,s=Math.PI*2){super(),this.type="CircleGeometry",this.parameters={radius:e,segments:t,thetaStart:n,thetaLength:s},t=Math.max(3,t);const r=[],o=[],a=[],c=[],l=new M,u=new te;o.push(0,0,0),a.push(0,0,1),c.push(.5,.5);for(let h=0,f=3;h<=t;h++,f+=3){const d=n+h/t*s;l.x=e*Math.cos(d),l.y=e*Math.sin(d),o.push(l.x,l.y,l.z),a.push(0,0,1),u.x=(o[f]/e+1)/2,u.y=(o[f+1]/e+1)/2,c.push(u.x,u.y)}for(let h=1;h<=t;h++)r.push(h,h+1,0);this.setIndex(r),this.setAttribute("position",new rt(o,3)),this.setAttribute("normal",new rt(a,3)),this.setAttribute("uv",new rt(c,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Yi(e.radius,e.segments,e.thetaStart,e.thetaLength)}}class bt extends zt{constructor(e=1,t=1,n=1,s=32,r=1,o=!1,a=0,c=Math.PI*2){super(),this.type="CylinderGeometry",this.parameters={radiusTop:e,radiusBottom:t,height:n,radialSegments:s,heightSegments:r,openEnded:o,thetaStart:a,thetaLength:c};const l=this;s=Math.floor(s),r=Math.floor(r);const u=[],h=[],f=[],d=[];let g=0;const _=[],p=n/2;let m=0;v(),o===!1&&(e>0&&y(!0),t>0&&y(!1)),this.setIndex(u),this.setAttribute("position",new rt(h,3)),this.setAttribute("normal",new rt(f,3)),this.setAttribute("uv",new rt(d,2));function v(){const x=new M,P=new M;let A=0;const E=(t-e)/n;for(let R=0;R<=r;R++){const b=[],S=R/r,I=S*(t-e)+e;for(let B=0;B<=s;B++){const O=B/s,k=O*c+a,K=Math.sin(k),W=Math.cos(k);P.x=I*K,P.y=-S*n+p,P.z=I*W,h.push(P.x,P.y,P.z),x.set(K,E,W).normalize(),f.push(x.x,x.y,x.z),d.push(O,1-S),b.push(g++)}_.push(b)}for(let R=0;R<s;R++)for(let b=0;b<r;b++){const S=_[b][R],I=_[b+1][R],B=_[b+1][R+1],O=_[b][R+1];(e>0||b!==0)&&(u.push(S,I,O),A+=3),(t>0||b!==r-1)&&(u.push(I,B,O),A+=3)}l.addGroup(m,A,0),m+=A}function y(x){const P=g,A=new te,E=new M;let R=0;const b=x===!0?e:t,S=x===!0?1:-1;for(let B=1;B<=s;B++)h.push(0,p*S,0),f.push(0,S,0),d.push(.5,.5),g++;const I=g;for(let B=0;B<=s;B++){const k=B/s*c+a,K=Math.cos(k),W=Math.sin(k);E.x=b*W,E.y=p*S,E.z=b*K,h.push(E.x,E.y,E.z),f.push(0,S,0),A.x=K*.5+.5,A.y=W*.5*S+.5,d.push(A.x,A.y),g++}for(let B=0;B<s;B++){const O=P+B,k=I+B;x===!0?u.push(k,k+1,O):u.push(k+1,k,O),R+=3}l.addGroup(m,R,x===!0?1:2),m+=R}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new bt(e.radiusTop,e.radiusBottom,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class mi extends bt{constructor(e=1,t=1,n=32,s=1,r=!1,o=0,a=Math.PI*2){super(0,e,t,n,s,r,o,a),this.type="ConeGeometry",this.parameters={radius:e,height:t,radialSegments:n,heightSegments:s,openEnded:r,thetaStart:o,thetaLength:a}}static fromJSON(e){return new mi(e.radius,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class Ql extends zt{constructor(e=[],t=[],n=1,s=0){super(),this.type="PolyhedronGeometry",this.parameters={vertices:e,indices:t,radius:n,detail:s};const r=[],o=[];a(s),l(n),u(),this.setAttribute("position",new rt(r,3)),this.setAttribute("normal",new rt(r.slice(),3)),this.setAttribute("uv",new rt(o,2)),s===0?this.computeVertexNormals():this.normalizeNormals();function a(v){const y=new M,x=new M,P=new M;for(let A=0;A<t.length;A+=3)d(t[A+0],y),d(t[A+1],x),d(t[A+2],P),c(y,x,P,v)}function c(v,y,x,P){const A=P+1,E=[];for(let R=0;R<=A;R++){E[R]=[];const b=v.clone().lerp(x,R/A),S=y.clone().lerp(x,R/A),I=A-R;for(let B=0;B<=I;B++)B===0&&R===A?E[R][B]=b:E[R][B]=b.clone().lerp(S,B/I)}for(let R=0;R<A;R++)for(let b=0;b<2*(A-R)-1;b++){const S=Math.floor(b/2);b%2===0?(f(E[R][S+1]),f(E[R+1][S]),f(E[R][S])):(f(E[R][S+1]),f(E[R+1][S+1]),f(E[R+1][S]))}}function l(v){const y=new M;for(let x=0;x<r.length;x+=3)y.x=r[x+0],y.y=r[x+1],y.z=r[x+2],y.normalize().multiplyScalar(v),r[x+0]=y.x,r[x+1]=y.y,r[x+2]=y.z}function u(){const v=new M;for(let y=0;y<r.length;y+=3){v.x=r[y+0],v.y=r[y+1],v.z=r[y+2];const x=p(v)/2/Math.PI+.5,P=m(v)/Math.PI+.5;o.push(x,1-P)}g(),h()}function h(){for(let v=0;v<o.length;v+=6){const y=o[v+0],x=o[v+2],P=o[v+4],A=Math.max(y,x,P),E=Math.min(y,x,P);A>.9&&E<.1&&(y<.2&&(o[v+0]+=1),x<.2&&(o[v+2]+=1),P<.2&&(o[v+4]+=1))}}function f(v){r.push(v.x,v.y,v.z)}function d(v,y){const x=v*3;y.x=e[x+0],y.y=e[x+1],y.z=e[x+2]}function g(){const v=new M,y=new M,x=new M,P=new M,A=new te,E=new te,R=new te;for(let b=0,S=0;b<r.length;b+=9,S+=6){v.set(r[b+0],r[b+1],r[b+2]),y.set(r[b+3],r[b+4],r[b+5]),x.set(r[b+6],r[b+7],r[b+8]),A.set(o[S+0],o[S+1]),E.set(o[S+2],o[S+3]),R.set(o[S+4],o[S+5]),P.copy(v).add(y).add(x).divideScalar(3);const I=p(P);_(A,S+0,v,I),_(E,S+2,y,I),_(R,S+4,x,I)}}function _(v,y,x,P){P<0&&v.x===1&&(o[y]=v.x-1),x.x===0&&x.z===0&&(o[y]=P/2/Math.PI+.5)}function p(v){return Math.atan2(v.z,-v.x)}function m(v){return Math.atan2(-v.y,Math.sqrt(v.x*v.x+v.z*v.z))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ql(e.vertices,e.indices,e.radius,e.details)}}const No=new M,Uo=new M,ac=new M,Oo=new Ln;class _a extends zt{constructor(e=null,t=1){if(super(),this.type="EdgesGeometry",this.parameters={geometry:e,thresholdAngle:t},e!==null){const s=Math.pow(10,4),r=Math.cos(qs*t),o=e.getIndex(),a=e.getAttribute("position"),c=o?o.count:a.count,l=[0,0,0],u=["a","b","c"],h=new Array(3),f={},d=[];for(let g=0;g<c;g+=3){o?(l[0]=o.getX(g),l[1]=o.getX(g+1),l[2]=o.getX(g+2)):(l[0]=g,l[1]=g+1,l[2]=g+2);const{a:_,b:p,c:m}=Oo;if(_.fromBufferAttribute(a,l[0]),p.fromBufferAttribute(a,l[1]),m.fromBufferAttribute(a,l[2]),Oo.getNormal(ac),h[0]=`${Math.round(_.x*s)},${Math.round(_.y*s)},${Math.round(_.z*s)}`,h[1]=`${Math.round(p.x*s)},${Math.round(p.y*s)},${Math.round(p.z*s)}`,h[2]=`${Math.round(m.x*s)},${Math.round(m.y*s)},${Math.round(m.z*s)}`,!(h[0]===h[1]||h[1]===h[2]||h[2]===h[0]))for(let v=0;v<3;v++){const y=(v+1)%3,x=h[v],P=h[y],A=Oo[u[v]],E=Oo[u[y]],R=`${x}_${P}`,b=`${P}_${x}`;b in f&&f[b]?(ac.dot(f[b].normal)<=r&&(d.push(A.x,A.y,A.z),d.push(E.x,E.y,E.z)),f[b]=null):R in f||(f[R]={index0:l[v],index1:l[y],normal:ac.clone()})}}for(const g in f)if(f[g]){const{index0:_,index1:p}=f[g];No.fromBufferAttribute(a,_),Uo.fromBufferAttribute(a,p),d.push(No.x,No.y,No.z),d.push(Uo.x,Uo.y,Uo.z)}this.setAttribute("position",new rt(d,3))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}}class Un extends yl{constructor(e){super(e),this.uuid=Nn(),this.type="Shape",this.holes=[]}getPointsHoles(e){const t=[];for(let n=0,s=this.holes.length;n<s;n++)t[n]=this.holes[n].getPoints(e);return t}extractPoints(e){return{shape:this.getPoints(e),holes:this.getPointsHoles(e)}}copy(e){super.copy(e),this.holes=[];for(let t=0,n=e.holes.length;t<n;t++){const s=e.holes[t];this.holes.push(s.clone())}return this}toJSON(){const e=super.toJSON();e.uuid=this.uuid,e.holes=[];for(let t=0,n=this.holes.length;t<n;t++){const s=this.holes[t];e.holes.push(s.toJSON())}return e}fromJSON(e){super.fromJSON(e),this.uuid=e.uuid,this.holes=[];for(let t=0,n=e.holes.length;t<n;t++){const s=e.holes[t];this.holes.push(new yl().fromJSON(s))}return this}}const Vv={triangulate:function(i,e,t=2){const n=e&&e.length,s=n?e[0]*t:i.length;let r=rd(i,0,s,t,!0);const o=[];if(!r||r.next===r.prev)return o;let a,c,l,u,h,f,d;if(n&&(r=Yv(i,e,r,t)),i.length>80*t){a=l=i[0],c=u=i[1];for(let g=t;g<s;g+=t)h=i[g],f=i[g+1],h<a&&(a=h),f<c&&(c=f),h>l&&(l=h),f>u&&(u=f);d=Math.max(l-a,u-c),d=d!==0?32767/d:0}return Xr(r,o,t,a,c,d,0),o}};function rd(i,e,t,n,s){let r,o;if(s===sy(i,e,t,n)>0)for(r=e;r<t;r+=n)o=Fh(r,i[r],i[r+1],o);else for(r=t-n;r>=e;r-=n)o=Fh(r,i[r],i[r+1],o);return o&&xa(o,o.next)&&(Yr(o),o=o.next),o}function xs(i,e){if(!i)return i;e||(e=i);let t=i,n;do if(n=!1,!t.steiner&&(xa(t,t.next)||Dt(t.prev,t,t.next)===0)){if(Yr(t),t=e=t.prev,t===t.next)break;n=!0}else t=t.next;while(n||t!==e);return e}function Xr(i,e,t,n,s,r,o){if(!i)return;!o&&r&&Jv(i,n,s,r);let a=i,c,l;for(;i.prev!==i.next;){if(c=i.prev,l=i.next,r?Wv(i,n,s,r):Gv(i)){e.push(c.i/t|0),e.push(i.i/t|0),e.push(l.i/t|0),Yr(i),i=l.next,a=l.next;continue}if(i=l,i===a){o?o===1?(i=Xv(xs(i),e,t),Xr(i,e,t,n,s,r,2)):o===2&&qv(i,e,t,n,s,r):Xr(xs(i),e,t,n,s,r,1);break}}}function Gv(i){const e=i.prev,t=i,n=i.next;if(Dt(e,t,n)>=0)return!1;const s=e.x,r=t.x,o=n.x,a=e.y,c=t.y,l=n.y,u=s<r?s<o?s:o:r<o?r:o,h=a<c?a<l?a:l:c<l?c:l,f=s>r?s>o?s:o:r>o?r:o,d=a>c?a>l?a:l:c>l?c:l;let g=n.next;for(;g!==e;){if(g.x>=u&&g.x<=f&&g.y>=h&&g.y<=d&&Vs(s,a,r,c,o,l,g.x,g.y)&&Dt(g.prev,g,g.next)>=0)return!1;g=g.next}return!0}function Wv(i,e,t,n){const s=i.prev,r=i,o=i.next;if(Dt(s,r,o)>=0)return!1;const a=s.x,c=r.x,l=o.x,u=s.y,h=r.y,f=o.y,d=a<c?a<l?a:l:c<l?c:l,g=u<h?u<f?u:f:h<f?h:f,_=a>c?a>l?a:l:c>l?c:l,p=u>h?u>f?u:f:h>f?h:f,m=Ml(d,g,e,t,n),v=Ml(_,p,e,t,n);let y=i.prevZ,x=i.nextZ;for(;y&&y.z>=m&&x&&x.z<=v;){if(y.x>=d&&y.x<=_&&y.y>=g&&y.y<=p&&y!==s&&y!==o&&Vs(a,u,c,h,l,f,y.x,y.y)&&Dt(y.prev,y,y.next)>=0||(y=y.prevZ,x.x>=d&&x.x<=_&&x.y>=g&&x.y<=p&&x!==s&&x!==o&&Vs(a,u,c,h,l,f,x.x,x.y)&&Dt(x.prev,x,x.next)>=0))return!1;x=x.nextZ}for(;y&&y.z>=m;){if(y.x>=d&&y.x<=_&&y.y>=g&&y.y<=p&&y!==s&&y!==o&&Vs(a,u,c,h,l,f,y.x,y.y)&&Dt(y.prev,y,y.next)>=0)return!1;y=y.prevZ}for(;x&&x.z<=v;){if(x.x>=d&&x.x<=_&&x.y>=g&&x.y<=p&&x!==s&&x!==o&&Vs(a,u,c,h,l,f,x.x,x.y)&&Dt(x.prev,x,x.next)>=0)return!1;x=x.nextZ}return!0}function Xv(i,e,t){let n=i;do{const s=n.prev,r=n.next.next;!xa(s,r)&&od(s,n,n.next,r)&&qr(s,r)&&qr(r,s)&&(e.push(s.i/t|0),e.push(n.i/t|0),e.push(r.i/t|0),Yr(n),Yr(n.next),n=i=r),n=n.next}while(n!==i);return xs(n)}function qv(i,e,t,n,s,r){let o=i;do{let a=o.next.next;for(;a!==o.prev;){if(o.i!==a.i&&ty(o,a)){let c=ad(o,a);o=xs(o,o.next),c=xs(c,c.next),Xr(o,e,t,n,s,r,0),Xr(c,e,t,n,s,r,0);return}a=a.next}o=o.next}while(o!==i)}function Yv(i,e,t,n){const s=[];let r,o,a,c,l;for(r=0,o=e.length;r<o;r++)a=e[r]*n,c=r<o-1?e[r+1]*n:i.length,l=rd(i,a,c,n,!1),l===l.next&&(l.steiner=!0),s.push(ey(l));for(s.sort(jv),r=0;r<s.length;r++)t=$v(s[r],t);return t}function jv(i,e){return i.x-e.x}function $v(i,e){const t=Kv(i,e);if(!t)return e;const n=ad(t,i);return xs(n,n.next),xs(t,t.next)}function Kv(i,e){let t=e,n=-1/0,s;const r=i.x,o=i.y;do{if(o<=t.y&&o>=t.next.y&&t.next.y!==t.y){const f=t.x+(o-t.y)*(t.next.x-t.x)/(t.next.y-t.y);if(f<=r&&f>n&&(n=f,s=t.x<t.next.x?t:t.next,f===r))return s}t=t.next}while(t!==e);if(!s)return null;const a=s,c=s.x,l=s.y;let u=1/0,h;t=s;do r>=t.x&&t.x>=c&&r!==t.x&&Vs(o<l?r:n,o,c,l,o<l?n:r,o,t.x,t.y)&&(h=Math.abs(o-t.y)/(r-t.x),qr(t,i)&&(h<u||h===u&&(t.x>s.x||t.x===s.x&&Zv(s,t)))&&(s=t,u=h)),t=t.next;while(t!==a);return s}function Zv(i,e){return Dt(i.prev,i,e.prev)<0&&Dt(e.next,i,i.next)<0}function Jv(i,e,t,n){let s=i;do s.z===0&&(s.z=Ml(s.x,s.y,e,t,n)),s.prevZ=s.prev,s.nextZ=s.next,s=s.next;while(s!==i);s.prevZ.nextZ=null,s.prevZ=null,Qv(s)}function Qv(i){let e,t,n,s,r,o,a,c,l=1;do{for(t=i,i=null,r=null,o=0;t;){for(o++,n=t,a=0,e=0;e<l&&(a++,n=n.nextZ,!!n);e++);for(c=l;a>0||c>0&&n;)a!==0&&(c===0||!n||t.z<=n.z)?(s=t,t=t.nextZ,a--):(s=n,n=n.nextZ,c--),r?r.nextZ=s:i=s,s.prevZ=r,r=s;t=n}r.nextZ=null,l*=2}while(o>1);return i}function Ml(i,e,t,n,s){return i=(i-t)*s|0,e=(e-n)*s|0,i=(i|i<<8)&16711935,i=(i|i<<4)&252645135,i=(i|i<<2)&858993459,i=(i|i<<1)&1431655765,e=(e|e<<8)&16711935,e=(e|e<<4)&252645135,e=(e|e<<2)&858993459,e=(e|e<<1)&1431655765,i|e<<1}function ey(i){let e=i,t=i;do(e.x<t.x||e.x===t.x&&e.y<t.y)&&(t=e),e=e.next;while(e!==i);return t}function Vs(i,e,t,n,s,r,o,a){return(s-o)*(e-a)>=(i-o)*(r-a)&&(i-o)*(n-a)>=(t-o)*(e-a)&&(t-o)*(r-a)>=(s-o)*(n-a)}function ty(i,e){return i.next.i!==e.i&&i.prev.i!==e.i&&!ny(i,e)&&(qr(i,e)&&qr(e,i)&&iy(i,e)&&(Dt(i.prev,i,e.prev)||Dt(i,e.prev,e))||xa(i,e)&&Dt(i.prev,i,i.next)>0&&Dt(e.prev,e,e.next)>0)}function Dt(i,e,t){return(e.y-i.y)*(t.x-e.x)-(e.x-i.x)*(t.y-e.y)}function xa(i,e){return i.x===e.x&&i.y===e.y}function od(i,e,t,n){const s=Bo(Dt(i,e,t)),r=Bo(Dt(i,e,n)),o=Bo(Dt(t,n,i)),a=Bo(Dt(t,n,e));return!!(s!==r&&o!==a||s===0&&Fo(i,t,e)||r===0&&Fo(i,n,e)||o===0&&Fo(t,i,n)||a===0&&Fo(t,e,n))}function Fo(i,e,t){return e.x<=Math.max(i.x,t.x)&&e.x>=Math.min(i.x,t.x)&&e.y<=Math.max(i.y,t.y)&&e.y>=Math.min(i.y,t.y)}function Bo(i){return i>0?1:i<0?-1:0}function ny(i,e){let t=i;do{if(t.i!==i.i&&t.next.i!==i.i&&t.i!==e.i&&t.next.i!==e.i&&od(t,t.next,i,e))return!0;t=t.next}while(t!==i);return!1}function qr(i,e){return Dt(i.prev,i,i.next)<0?Dt(i,e,i.next)>=0&&Dt(i,i.prev,e)>=0:Dt(i,e,i.prev)<0||Dt(i,i.next,e)<0}function iy(i,e){let t=i,n=!1;const s=(i.x+e.x)/2,r=(i.y+e.y)/2;do t.y>r!=t.next.y>r&&t.next.y!==t.y&&s<(t.next.x-t.x)*(r-t.y)/(t.next.y-t.y)+t.x&&(n=!n),t=t.next;while(t!==i);return n}function ad(i,e){const t=new Sl(i.i,i.x,i.y),n=new Sl(e.i,e.x,e.y),s=i.next,r=e.prev;return i.next=e,e.prev=i,t.next=s,s.prev=t,n.next=t,t.prev=n,r.next=n,n.prev=r,n}function Fh(i,e,t,n){const s=new Sl(i,e,t);return n?(s.next=n.next,s.prev=n,n.next.prev=s,n.next=s):(s.prev=s,s.next=s),s}function Yr(i){i.next.prev=i.prev,i.prev.next=i.next,i.prevZ&&(i.prevZ.nextZ=i.nextZ),i.nextZ&&(i.nextZ.prevZ=i.prevZ)}function Sl(i,e,t){this.i=i,this.x=e,this.y=t,this.prev=null,this.next=null,this.z=0,this.prevZ=null,this.nextZ=null,this.steiner=!1}function sy(i,e,t,n){let s=0;for(let r=e,o=t-n;r<t;r+=n)s+=(i[o]-i[r])*(i[r+1]+i[o+1]),o=r;return s}class Wi{static area(e){const t=e.length;let n=0;for(let s=t-1,r=0;r<t;s=r++)n+=e[s].x*e[r].y-e[r].x*e[s].y;return n*.5}static isClockWise(e){return Wi.area(e)<0}static triangulateShape(e,t){const n=[],s=[],r=[];Bh(e),kh(n,e);let o=e.length;t.forEach(Bh);for(let c=0;c<t.length;c++)s.push(o),o+=t[c].length,kh(n,t[c]);const a=Vv.triangulate(n,s);for(let c=0;c<a.length;c+=3)r.push(a.slice(c,c+3));return r}}function Bh(i){const e=i.length;e>2&&i[e-1].equals(i[0])&&i.pop()}function kh(i,e){for(let t=0;t<e.length;t++)i.push(e[t].x),i.push(e[t].y)}class Jr extends zt{constructor(e=new Un([new te(.5,.5),new te(-.5,.5),new te(-.5,-.5),new te(.5,-.5)]),t={}){super(),this.type="ExtrudeGeometry",this.parameters={shapes:e,options:t},e=Array.isArray(e)?e:[e];const n=this,s=[],r=[];for(let a=0,c=e.length;a<c;a++){const l=e[a];o(l)}this.setAttribute("position",new rt(s,3)),this.setAttribute("uv",new rt(r,2)),this.computeVertexNormals();function o(a){const c=[],l=t.curveSegments!==void 0?t.curveSegments:12,u=t.steps!==void 0?t.steps:1,h=t.depth!==void 0?t.depth:1;let f=t.bevelEnabled!==void 0?t.bevelEnabled:!0,d=t.bevelThickness!==void 0?t.bevelThickness:.2,g=t.bevelSize!==void 0?t.bevelSize:d-.1,_=t.bevelOffset!==void 0?t.bevelOffset:0,p=t.bevelSegments!==void 0?t.bevelSegments:3;const m=t.extrudePath,v=t.UVGenerator!==void 0?t.UVGenerator:ry;let y,x=!1,P,A,E,R;m&&(y=m.getSpacedPoints(u),x=!0,f=!1,P=m.computeFrenetFrames(u,!1),A=new M,E=new M,R=new M),f||(p=0,d=0,g=0,_=0);const b=a.extractPoints(l);let S=b.shape;const I=b.holes;if(!Wi.isClockWise(S)){S=S.reverse();for(let Q=0,ae=I.length;Q<ae;Q++){const L=I[Q];Wi.isClockWise(L)&&(I[Q]=L.reverse())}}const O=Wi.triangulateShape(S,I),k=S;for(let Q=0,ae=I.length;Q<ae;Q++){const L=I[Q];S=S.concat(L)}function K(Q,ae,L){return ae||console.error("THREE.ExtrudeGeometry: vec does not exist"),Q.clone().addScaledVector(ae,L)}const W=S.length,q=O.length;function V(Q,ae,L){let Be,ie,Ee;const de=Q.x-ae.x,We=Q.y-ae.y,be=L.x-Q.x,C=L.y-Q.y,w=de*de+We*We,F=de*C-We*be;if(Math.abs(F)>Number.EPSILON){const j=Math.sqrt(w),ee=Math.sqrt(be*be+C*C),$=ae.x-We/j,Ne=ae.y+de/j,_e=L.x-C/ee,we=L.y+be/ee,ot=((_e-$)*C-(we-Ne)*be)/(de*C-We*be);Be=$+de*ot-Q.x,ie=Ne+We*ot-Q.y;const re=Be*Be+ie*ie;if(re<=2)return new te(Be,ie);Ee=Math.sqrt(re/2)}else{let j=!1;de>Number.EPSILON?be>Number.EPSILON&&(j=!0):de<-Number.EPSILON?be<-Number.EPSILON&&(j=!0):Math.sign(We)===Math.sign(C)&&(j=!0),j?(Be=-We,ie=de,Ee=Math.sqrt(w)):(Be=de,ie=We,Ee=Math.sqrt(w/2))}return new te(Be/Ee,ie/Ee)}const se=[];for(let Q=0,ae=k.length,L=ae-1,Be=Q+1;Q<ae;Q++,L++,Be++)L===ae&&(L=0),Be===ae&&(Be=0),se[Q]=V(k[Q],k[L],k[Be]);const me=[];let Se,Ze=se.concat();for(let Q=0,ae=I.length;Q<ae;Q++){const L=I[Q];Se=[];for(let Be=0,ie=L.length,Ee=ie-1,de=Be+1;Be<ie;Be++,Ee++,de++)Ee===ie&&(Ee=0),de===ie&&(de=0),Se[Be]=V(L[Be],L[Ee],L[de]);me.push(Se),Ze=Ze.concat(Se)}for(let Q=0;Q<p;Q++){const ae=Q/p,L=d*Math.cos(ae*Math.PI/2),Be=g*Math.sin(ae*Math.PI/2)+_;for(let ie=0,Ee=k.length;ie<Ee;ie++){const de=K(k[ie],se[ie],Be);fe(de.x,de.y,-L)}for(let ie=0,Ee=I.length;ie<Ee;ie++){const de=I[ie];Se=me[ie];for(let We=0,be=de.length;We<be;We++){const C=K(de[We],Se[We],Be);fe(C.x,C.y,-L)}}}const pt=g+_;for(let Q=0;Q<W;Q++){const ae=f?K(S[Q],Ze[Q],pt):S[Q];x?(E.copy(P.normals[0]).multiplyScalar(ae.x),A.copy(P.binormals[0]).multiplyScalar(ae.y),R.copy(y[0]).add(E).add(A),fe(R.x,R.y,R.z)):fe(ae.x,ae.y,0)}for(let Q=1;Q<=u;Q++)for(let ae=0;ae<W;ae++){const L=f?K(S[ae],Ze[ae],pt):S[ae];x?(E.copy(P.normals[Q]).multiplyScalar(L.x),A.copy(P.binormals[Q]).multiplyScalar(L.y),R.copy(y[Q]).add(E).add(A),fe(R.x,R.y,R.z)):fe(L.x,L.y,h/u*Q)}for(let Q=p-1;Q>=0;Q--){const ae=Q/p,L=d*Math.cos(ae*Math.PI/2),Be=g*Math.sin(ae*Math.PI/2)+_;for(let ie=0,Ee=k.length;ie<Ee;ie++){const de=K(k[ie],se[ie],Be);fe(de.x,de.y,h+L)}for(let ie=0,Ee=I.length;ie<Ee;ie++){const de=I[ie];Se=me[ie];for(let We=0,be=de.length;We<be;We++){const C=K(de[We],Se[We],Be);x?fe(C.x,C.y+y[u-1].y,y[u-1].x+L):fe(C.x,C.y,h+L)}}}Z(),le();function Z(){const Q=s.length/3;if(f){let ae=0,L=W*ae;for(let Be=0;Be<q;Be++){const ie=O[Be];He(ie[2]+L,ie[1]+L,ie[0]+L)}ae=u+p*2,L=W*ae;for(let Be=0;Be<q;Be++){const ie=O[Be];He(ie[0]+L,ie[1]+L,ie[2]+L)}}else{for(let ae=0;ae<q;ae++){const L=O[ae];He(L[2],L[1],L[0])}for(let ae=0;ae<q;ae++){const L=O[ae];He(L[0]+W*u,L[1]+W*u,L[2]+W*u)}}n.addGroup(Q,s.length/3-Q,0)}function le(){const Q=s.length/3;let ae=0;Ie(k,ae),ae+=k.length;for(let L=0,Be=I.length;L<Be;L++){const ie=I[L];Ie(ie,ae),ae+=ie.length}n.addGroup(Q,s.length/3-Q,1)}function Ie(Q,ae){let L=Q.length;for(;--L>=0;){const Be=L;let ie=L-1;ie<0&&(ie=Q.length-1);for(let Ee=0,de=u+p*2;Ee<de;Ee++){const We=W*Ee,be=W*(Ee+1),C=ae+Be+We,w=ae+ie+We,F=ae+ie+be,j=ae+Be+be;je(C,w,F,j)}}}function fe(Q,ae,L){c.push(Q),c.push(ae),c.push(L)}function He(Q,ae,L){qe(Q),qe(ae),qe(L);const Be=s.length/3,ie=v.generateTopUV(n,s,Be-3,Be-2,Be-1);ut(ie[0]),ut(ie[1]),ut(ie[2])}function je(Q,ae,L,Be){qe(Q),qe(ae),qe(Be),qe(ae),qe(L),qe(Be);const ie=s.length/3,Ee=v.generateSideWallUV(n,s,ie-6,ie-3,ie-2,ie-1);ut(Ee[0]),ut(Ee[1]),ut(Ee[3]),ut(Ee[1]),ut(Ee[2]),ut(Ee[3])}function qe(Q){s.push(c[Q*3+0]),s.push(c[Q*3+1]),s.push(c[Q*3+2])}function ut(Q){r.push(Q.x),r.push(Q.y)}}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}toJSON(){const e=super.toJSON(),t=this.parameters.shapes,n=this.parameters.options;return oy(t,n,e)}static fromJSON(e,t){const n=[];for(let r=0,o=e.shapes.length;r<o;r++){const a=t[e.shapes[r]];n.push(a)}const s=e.options.extrudePath;return s!==void 0&&(e.options.extrudePath=new ra[s.type]().fromJSON(s)),new Jr(n,e.options)}}const ry={generateTopUV:function(i,e,t,n,s){const r=e[t*3],o=e[t*3+1],a=e[n*3],c=e[n*3+1],l=e[s*3],u=e[s*3+1];return[new te(r,o),new te(a,c),new te(l,u)]},generateSideWallUV:function(i,e,t,n,s,r){const o=e[t*3],a=e[t*3+1],c=e[t*3+2],l=e[n*3],u=e[n*3+1],h=e[n*3+2],f=e[s*3],d=e[s*3+1],g=e[s*3+2],_=e[r*3],p=e[r*3+1],m=e[r*3+2];return Math.abs(a-u)<Math.abs(o-l)?[new te(o,1-c),new te(l,1-h),new te(f,1-g),new te(_,1-m)]:[new te(a,1-c),new te(u,1-h),new te(d,1-g),new te(p,1-m)]}};function oy(i,e,t){if(t.shapes=[],Array.isArray(i))for(let n=0,s=i.length;n<s;n++){const r=i[n];t.shapes.push(r.uuid)}else t.shapes.push(i.uuid);return t.options=Object.assign({},e),e.extrudePath!==void 0&&(t.options.extrudePath=e.extrudePath.toJSON()),t}class eu extends Ql{constructor(e=1,t=0){const n=(1+Math.sqrt(5))/2,s=[-1,n,0,1,n,0,-1,-n,0,1,-n,0,0,-1,n,0,1,n,0,-1,-n,0,1,-n,n,0,-1,n,0,1,-n,0,-1,-n,0,1],r=[0,11,5,0,5,1,0,1,7,0,7,10,0,10,11,1,5,9,5,11,4,11,10,2,10,7,6,7,1,8,3,9,4,3,4,2,3,2,6,3,6,8,3,8,9,4,9,5,2,4,11,6,2,10,8,6,7,9,8,1];super(s,r,e,t),this.type="IcosahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new eu(e.radius,e.detail)}}class Mi extends zt{constructor(e=new Un([new te(0,.5),new te(-.5,-.5),new te(.5,-.5)]),t=12){super(),this.type="ShapeGeometry",this.parameters={shapes:e,curveSegments:t};const n=[],s=[],r=[],o=[];let a=0,c=0;if(Array.isArray(e)===!1)l(e);else for(let u=0;u<e.length;u++)l(e[u]),this.addGroup(a,c,u),a+=c,c=0;this.setIndex(n),this.setAttribute("position",new rt(s,3)),this.setAttribute("normal",new rt(r,3)),this.setAttribute("uv",new rt(o,2));function l(u){const h=s.length/3,f=u.extractPoints(t);let d=f.shape;const g=f.holes;Wi.isClockWise(d)===!1&&(d=d.reverse());for(let p=0,m=g.length;p<m;p++){const v=g[p];Wi.isClockWise(v)===!0&&(g[p]=v.reverse())}const _=Wi.triangulateShape(d,g);for(let p=0,m=g.length;p<m;p++){const v=g[p];d=d.concat(v)}for(let p=0,m=d.length;p<m;p++){const v=d[p];s.push(v.x,v.y,0),r.push(0,0,1),o.push(v.x,v.y)}for(let p=0,m=_.length;p<m;p++){const v=_[p],y=v[0]+h,x=v[1]+h,P=v[2]+h;n.push(y,x,P),c+=3}}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}toJSON(){const e=super.toJSON(),t=this.parameters.shapes;return ay(t,e)}static fromJSON(e,t){const n=[];for(let s=0,r=e.shapes.length;s<r;s++){const o=t[e.shapes[s]];n.push(o)}return new Mi(n,e.curveSegments)}}function ay(i,e){if(e.shapes=[],Array.isArray(i))for(let t=0,n=i.length;t<n;t++){const s=i[t];e.shapes.push(s.uuid)}else e.shapes.push(i.uuid);return e}class ur extends zt{constructor(e=1,t=32,n=16,s=0,r=Math.PI*2,o=0,a=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:n,phiStart:s,phiLength:r,thetaStart:o,thetaLength:a},t=Math.max(3,Math.floor(t)),n=Math.max(2,Math.floor(n));const c=Math.min(o+a,Math.PI);let l=0;const u=[],h=new M,f=new M,d=[],g=[],_=[],p=[];for(let m=0;m<=n;m++){const v=[],y=m/n;let x=0;m===0&&o===0?x=.5/t:m===n&&c===Math.PI&&(x=-.5/t);for(let P=0;P<=t;P++){const A=P/t;h.x=-e*Math.cos(s+A*r)*Math.sin(o+y*a),h.y=e*Math.cos(o+y*a),h.z=e*Math.sin(s+A*r)*Math.sin(o+y*a),g.push(h.x,h.y,h.z),f.copy(h).normalize(),_.push(f.x,f.y,f.z),p.push(A+x,1-y),v.push(l++)}u.push(v)}for(let m=0;m<n;m++)for(let v=0;v<t;v++){const y=u[m][v+1],x=u[m][v],P=u[m+1][v],A=u[m+1][v+1];(m!==0||o>0)&&d.push(y,x,A),(m!==n-1||c<Math.PI)&&d.push(x,P,A)}this.setIndex(d),this.setAttribute("position",new rt(g,3)),this.setAttribute("normal",new rt(_,3)),this.setAttribute("uv",new rt(p,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ur(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}class Xi extends zt{constructor(e=1,t=.4,n=12,s=48,r=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:e,tube:t,radialSegments:n,tubularSegments:s,arc:r},n=Math.floor(n),s=Math.floor(s);const o=[],a=[],c=[],l=[],u=new M,h=new M,f=new M;for(let d=0;d<=n;d++)for(let g=0;g<=s;g++){const _=g/s*r,p=d/n*Math.PI*2;h.x=(e+t*Math.cos(p))*Math.cos(_),h.y=(e+t*Math.cos(p))*Math.sin(_),h.z=t*Math.sin(p),a.push(h.x,h.y,h.z),u.x=e*Math.cos(_),u.y=e*Math.sin(_),f.subVectors(h,u).normalize(),c.push(f.x,f.y,f.z),l.push(g/s),l.push(d/n)}for(let d=1;d<=n;d++)for(let g=1;g<=s;g++){const _=(s+1)*d+g-1,p=(s+1)*(d-1)+g-1,m=(s+1)*(d-1)+g,v=(s+1)*d+g;o.push(_,p,v),o.push(p,m,v)}this.setIndex(o),this.setAttribute("position",new rt(a,3)),this.setAttribute("normal",new rt(c,3)),this.setAttribute("uv",new rt(l,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Xi(e.radius,e.tube,e.radialSegments,e.tubularSegments,e.arc)}}class sr extends zt{constructor(e=new Zl(new M(-1,-1,0),new M(-1,1,0),new M(1,1,0)),t=64,n=1,s=8,r=!1){super(),this.type="TubeGeometry",this.parameters={path:e,tubularSegments:t,radius:n,radialSegments:s,closed:r};const o=e.computeFrenetFrames(t,r);this.tangents=o.tangents,this.normals=o.normals,this.binormals=o.binormals;const a=new M,c=new M,l=new te;let u=new M;const h=[],f=[],d=[],g=[];_(),this.setIndex(g),this.setAttribute("position",new rt(h,3)),this.setAttribute("normal",new rt(f,3)),this.setAttribute("uv",new rt(d,2));function _(){for(let y=0;y<t;y++)p(y);p(r===!1?t:0),v(),m()}function p(y){u=e.getPointAt(y/t,u);const x=o.normals[y],P=o.binormals[y];for(let A=0;A<=s;A++){const E=A/s*Math.PI*2,R=Math.sin(E),b=-Math.cos(E);c.x=b*x.x+R*P.x,c.y=b*x.y+R*P.y,c.z=b*x.z+R*P.z,c.normalize(),f.push(c.x,c.y,c.z),a.x=u.x+n*c.x,a.y=u.y+n*c.y,a.z=u.z+n*c.z,h.push(a.x,a.y,a.z)}}function m(){for(let y=1;y<=t;y++)for(let x=1;x<=s;x++){const P=(s+1)*(y-1)+(x-1),A=(s+1)*y+(x-1),E=(s+1)*y+x,R=(s+1)*(y-1)+x;g.push(P,A,R),g.push(A,E,R)}}function v(){for(let y=0;y<=t;y++)for(let x=0;x<=s;x++)l.x=y/t,l.y=x/s,d.push(l.x,l.y)}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}toJSON(){const e=super.toJSON();return e.path=this.parameters.path.toJSON(),e}static fromJSON(e){return new sr(new ra[e.path.type]().fromJSON(e.path),e.tubularSegments,e.radius,e.radialSegments,e.closed)}}class tu extends Kn{static get type(){return"MeshStandardMaterial"}constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.color=new ze(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new ze(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=Df,this.normalScale=new te(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new wn,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class ni extends tu{static get type(){return"MeshPhysicalMaterial"}constructor(e){super(),this.isMeshPhysicalMaterial=!0,this.defines={STANDARD:"",PHYSICAL:""},this.anisotropyRotation=0,this.anisotropyMap=null,this.clearcoatMap=null,this.clearcoatRoughness=0,this.clearcoatRoughnessMap=null,this.clearcoatNormalScale=new te(1,1),this.clearcoatNormalMap=null,this.ior=1.5,Object.defineProperty(this,"reflectivity",{get:function(){return Wt(2.5*(this.ior-1)/(this.ior+1),0,1)},set:function(t){this.ior=(1+.4*t)/(1-.4*t)}}),this.iridescenceMap=null,this.iridescenceIOR=1.3,this.iridescenceThicknessRange=[100,400],this.iridescenceThicknessMap=null,this.sheenColor=new ze(0),this.sheenColorMap=null,this.sheenRoughness=1,this.sheenRoughnessMap=null,this.transmissionMap=null,this.thickness=0,this.thicknessMap=null,this.attenuationDistance=1/0,this.attenuationColor=new ze(1,1,1),this.specularIntensity=1,this.specularIntensityMap=null,this.specularColor=new ze(1,1,1),this.specularColorMap=null,this._anisotropy=0,this._clearcoat=0,this._dispersion=0,this._iridescence=0,this._sheen=0,this._transmission=0,this.setValues(e)}get anisotropy(){return this._anisotropy}set anisotropy(e){this._anisotropy>0!=e>0&&this.version++,this._anisotropy=e}get clearcoat(){return this._clearcoat}set clearcoat(e){this._clearcoat>0!=e>0&&this.version++,this._clearcoat=e}get iridescence(){return this._iridescence}set iridescence(e){this._iridescence>0!=e>0&&this.version++,this._iridescence=e}get dispersion(){return this._dispersion}set dispersion(e){this._dispersion>0!=e>0&&this.version++,this._dispersion=e}get sheen(){return this._sheen}set sheen(e){this._sheen>0!=e>0&&this.version++,this._sheen=e}get transmission(){return this._transmission}set transmission(e){this._transmission>0!=e>0&&this.version++,this._transmission=e}copy(e){return super.copy(e),this.defines={STANDARD:"",PHYSICAL:""},this.anisotropy=e.anisotropy,this.anisotropyRotation=e.anisotropyRotation,this.anisotropyMap=e.anisotropyMap,this.clearcoat=e.clearcoat,this.clearcoatMap=e.clearcoatMap,this.clearcoatRoughness=e.clearcoatRoughness,this.clearcoatRoughnessMap=e.clearcoatRoughnessMap,this.clearcoatNormalMap=e.clearcoatNormalMap,this.clearcoatNormalScale.copy(e.clearcoatNormalScale),this.dispersion=e.dispersion,this.ior=e.ior,this.iridescence=e.iridescence,this.iridescenceMap=e.iridescenceMap,this.iridescenceIOR=e.iridescenceIOR,this.iridescenceThicknessRange=[...e.iridescenceThicknessRange],this.iridescenceThicknessMap=e.iridescenceThicknessMap,this.sheen=e.sheen,this.sheenColor.copy(e.sheenColor),this.sheenColorMap=e.sheenColorMap,this.sheenRoughness=e.sheenRoughness,this.sheenRoughnessMap=e.sheenRoughnessMap,this.transmission=e.transmission,this.transmissionMap=e.transmissionMap,this.thickness=e.thickness,this.thicknessMap=e.thicknessMap,this.attenuationDistance=e.attenuationDistance,this.attenuationColor.copy(e.attenuationColor),this.specularIntensity=e.specularIntensity,this.specularIntensityMap=e.specularIntensityMap,this.specularColor.copy(e.specularColor),this.specularColorMap=e.specularColorMap,this}}function ko(i,e,t){return!i||!t&&i.constructor===e?i:typeof e.BYTES_PER_ELEMENT=="number"?new e(i):Array.prototype.slice.call(i)}function cy(i){return ArrayBuffer.isView(i)&&!(i instanceof DataView)}function ly(i){function e(s,r){return i[s]-i[r]}const t=i.length,n=new Array(t);for(let s=0;s!==t;++s)n[s]=s;return n.sort(e),n}function zh(i,e,t){const n=i.length,s=new i.constructor(n);for(let r=0,o=0;o!==n;++r){const a=t[r]*e;for(let c=0;c!==e;++c)s[o++]=i[a+c]}return s}function cd(i,e,t,n){let s=1,r=i[0];for(;r!==void 0&&r[n]===void 0;)r=i[s++];if(r===void 0)return;let o=r[n];if(o!==void 0)if(Array.isArray(o))do o=r[n],o!==void 0&&(e.push(r.time),t.push.apply(t,o)),r=i[s++];while(r!==void 0);else if(o.toArray!==void 0)do o=r[n],o!==void 0&&(e.push(r.time),o.toArray(t,t.length)),r=i[s++];while(r!==void 0);else do o=r[n],o!==void 0&&(e.push(r.time),t.push(o)),r=i[s++];while(r!==void 0)}class Qr{constructor(e,t,n,s){this.parameterPositions=e,this._cachedIndex=0,this.resultBuffer=s!==void 0?s:new t.constructor(n),this.sampleValues=t,this.valueSize=n,this.settings=null,this.DefaultSettings_={}}evaluate(e){const t=this.parameterPositions;let n=this._cachedIndex,s=t[n],r=t[n-1];n:{e:{let o;t:{i:if(!(e<s)){for(let a=n+2;;){if(s===void 0){if(e<r)break i;return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}if(n===a)break;if(r=s,s=t[++n],e<s)break e}o=t.length;break t}if(!(e>=r)){const a=t[1];e<a&&(n=2,r=a);for(let c=n-2;;){if(r===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(n===c)break;if(s=r,r=t[--n-1],e>=r)break e}o=n,n=0;break t}break n}for(;n<o;){const a=n+o>>>1;e<t[a]?o=a:n=a+1}if(s=t[n],r=t[n-1],r===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(s===void 0)return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}this._cachedIndex=n,this.intervalChanged_(n,r,s)}return this.interpolate_(n,r,e,s)}getSettings_(){return this.settings||this.DefaultSettings_}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,s=this.valueSize,r=e*s;for(let o=0;o!==s;++o)t[o]=n[r+o];return t}interpolate_(){throw new Error("call to abstract method")}intervalChanged_(){}}class uy extends Qr{constructor(e,t,n,s){super(e,t,n,s),this._weightPrev=-0,this._offsetPrev=-0,this._weightNext=-0,this._offsetNext=-0,this.DefaultSettings_={endingStart:Eu,endingEnd:Eu}}intervalChanged_(e,t,n){const s=this.parameterPositions;let r=e-2,o=e+1,a=s[r],c=s[o];if(a===void 0)switch(this.getSettings_().endingStart){case Tu:r=e,a=2*t-n;break;case Au:r=s.length-2,a=t+s[r]-s[r+1];break;default:r=e,a=n}if(c===void 0)switch(this.getSettings_().endingEnd){case Tu:o=e,c=2*n-t;break;case Au:o=1,c=n+s[1]-s[0];break;default:o=e-1,c=t}const l=(n-t)*.5,u=this.valueSize;this._weightPrev=l/(t-a),this._weightNext=l/(c-n),this._offsetPrev=r*u,this._offsetNext=o*u}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=e*a,l=c-a,u=this._offsetPrev,h=this._offsetNext,f=this._weightPrev,d=this._weightNext,g=(n-t)/(s-t),_=g*g,p=_*g,m=-f*p+2*f*_-f*g,v=(1+f)*p+(-1.5-2*f)*_+(-.5+f)*g+1,y=(-1-d)*p+(1.5+d)*_+.5*g,x=d*p-d*_;for(let P=0;P!==a;++P)r[P]=m*o[u+P]+v*o[l+P]+y*o[c+P]+x*o[h+P];return r}}class hy extends Qr{constructor(e,t,n,s){super(e,t,n,s)}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=e*a,l=c-a,u=(n-t)/(s-t),h=1-u;for(let f=0;f!==a;++f)r[f]=o[l+f]*h+o[c+f]*u;return r}}class fy extends Qr{constructor(e,t,n,s){super(e,t,n,s)}interpolate_(e){return this.copySampleValue_(e-1)}}class ii{constructor(e,t,n,s){if(e===void 0)throw new Error("THREE.KeyframeTrack: track name is undefined");if(t===void 0||t.length===0)throw new Error("THREE.KeyframeTrack: no keyframes in track named "+e);this.name=e,this.times=ko(t,this.TimeBufferType),this.values=ko(n,this.ValueBufferType),this.setInterpolation(s||this.DefaultInterpolation)}static toJSON(e){const t=e.constructor;let n;if(t.toJSON!==this.toJSON)n=t.toJSON(e);else{n={name:e.name,times:ko(e.times,Array),values:ko(e.values,Array)};const s=e.getInterpolation();s!==e.DefaultInterpolation&&(n.interpolation=s)}return n.type=e.ValueTypeName,n}InterpolantFactoryMethodDiscrete(e){return new fy(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodLinear(e){return new hy(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodSmooth(e){return new uy(this.times,this.values,this.getValueSize(),e)}setInterpolation(e){let t;switch(e){case Vr:t=this.InterpolantFactoryMethodDiscrete;break;case Gr:t=this.InterpolantFactoryMethodLinear;break;case Aa:t=this.InterpolantFactoryMethodSmooth;break}if(t===void 0){const n="unsupported interpolation for "+this.ValueTypeName+" keyframe track named "+this.name;if(this.createInterpolant===void 0)if(e!==this.DefaultInterpolation)this.setInterpolation(this.DefaultInterpolation);else throw new Error(n);return console.warn("THREE.KeyframeTrack:",n),this}return this.createInterpolant=t,this}getInterpolation(){switch(this.createInterpolant){case this.InterpolantFactoryMethodDiscrete:return Vr;case this.InterpolantFactoryMethodLinear:return Gr;case this.InterpolantFactoryMethodSmooth:return Aa}}getValueSize(){return this.values.length/this.times.length}shift(e){if(e!==0){const t=this.times;for(let n=0,s=t.length;n!==s;++n)t[n]+=e}return this}scale(e){if(e!==1){const t=this.times;for(let n=0,s=t.length;n!==s;++n)t[n]*=e}return this}trim(e,t){const n=this.times,s=n.length;let r=0,o=s-1;for(;r!==s&&n[r]<e;)++r;for(;o!==-1&&n[o]>t;)--o;if(++o,r!==0||o!==s){r>=o&&(o=Math.max(o,1),r=o-1);const a=this.getValueSize();this.times=n.slice(r,o),this.values=this.values.slice(r*a,o*a)}return this}validate(){let e=!0;const t=this.getValueSize();t-Math.floor(t)!==0&&(console.error("THREE.KeyframeTrack: Invalid value size in track.",this),e=!1);const n=this.times,s=this.values,r=n.length;r===0&&(console.error("THREE.KeyframeTrack: Track is empty.",this),e=!1);let o=null;for(let a=0;a!==r;a++){const c=n[a];if(typeof c=="number"&&isNaN(c)){console.error("THREE.KeyframeTrack: Time is not a valid number.",this,a,c),e=!1;break}if(o!==null&&o>c){console.error("THREE.KeyframeTrack: Out of order keys.",this,a,c,o),e=!1;break}o=c}if(s!==void 0&&cy(s))for(let a=0,c=s.length;a!==c;++a){const l=s[a];if(isNaN(l)){console.error("THREE.KeyframeTrack: Value is not a valid number.",this,a,l),e=!1;break}}return e}optimize(){const e=this.times.slice(),t=this.values.slice(),n=this.getValueSize(),s=this.getInterpolation()===Aa,r=e.length-1;let o=1;for(let a=1;a<r;++a){let c=!1;const l=e[a],u=e[a+1];if(l!==u&&(a!==1||l!==e[0]))if(s)c=!0;else{const h=a*n,f=h-n,d=h+n;for(let g=0;g!==n;++g){const _=t[h+g];if(_!==t[f+g]||_!==t[d+g]){c=!0;break}}}if(c){if(a!==o){e[o]=e[a];const h=a*n,f=o*n;for(let d=0;d!==n;++d)t[f+d]=t[h+d]}++o}}if(r>0){e[o]=e[r];for(let a=r*n,c=o*n,l=0;l!==n;++l)t[c+l]=t[a+l];++o}return o!==e.length?(this.times=e.slice(0,o),this.values=t.slice(0,o*n)):(this.times=e,this.values=t),this}clone(){const e=this.times.slice(),t=this.values.slice(),n=this.constructor,s=new n(this.name,e,t);return s.createInterpolant=this.createInterpolant,s}}ii.prototype.TimeBufferType=Float32Array;ii.prototype.ValueBufferType=Float32Array;ii.prototype.DefaultInterpolation=Gr;class hr extends ii{constructor(e,t,n){super(e,t,n)}}hr.prototype.ValueTypeName="bool";hr.prototype.ValueBufferType=Array;hr.prototype.DefaultInterpolation=Vr;hr.prototype.InterpolantFactoryMethodLinear=void 0;hr.prototype.InterpolantFactoryMethodSmooth=void 0;class ld extends ii{}ld.prototype.ValueTypeName="color";class rr extends ii{}rr.prototype.ValueTypeName="number";class dy extends Qr{constructor(e,t,n,s){super(e,t,n,s)}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=(n-t)/(s-t);let l=e*a;for(let u=l+a;l!==u;l+=4)On.slerpFlat(r,0,o,l-a,o,l,c);return r}}class or extends ii{InterpolantFactoryMethodLinear(e){return new dy(this.times,this.values,this.getValueSize(),e)}}or.prototype.ValueTypeName="quaternion";or.prototype.InterpolantFactoryMethodSmooth=void 0;class fr extends ii{constructor(e,t,n){super(e,t,n)}}fr.prototype.ValueTypeName="string";fr.prototype.ValueBufferType=Array;fr.prototype.DefaultInterpolation=Vr;fr.prototype.InterpolantFactoryMethodLinear=void 0;fr.prototype.InterpolantFactoryMethodSmooth=void 0;class ar extends ii{}ar.prototype.ValueTypeName="vector";class py{constructor(e="",t=-1,n=[],s=Bp){this.name=e,this.tracks=n,this.duration=t,this.blendMode=s,this.uuid=Nn(),this.duration<0&&this.resetDuration()}static parse(e){const t=[],n=e.tracks,s=1/(e.fps||1);for(let o=0,a=n.length;o!==a;++o)t.push(gy(n[o]).scale(s));const r=new this(e.name,e.duration,t,e.blendMode);return r.uuid=e.uuid,r}static toJSON(e){const t=[],n=e.tracks,s={name:e.name,duration:e.duration,tracks:t,uuid:e.uuid,blendMode:e.blendMode};for(let r=0,o=n.length;r!==o;++r)t.push(ii.toJSON(n[r]));return s}static CreateFromMorphTargetSequence(e,t,n,s){const r=t.length,o=[];for(let a=0;a<r;a++){let c=[],l=[];c.push((a+r-1)%r,a,(a+1)%r),l.push(0,1,0);const u=ly(c);c=zh(c,1,u),l=zh(l,1,u),!s&&c[0]===0&&(c.push(r),l.push(l[0])),o.push(new rr(".morphTargetInfluences["+t[a].name+"]",c,l).scale(1/n))}return new this(e,-1,o)}static findByName(e,t){let n=e;if(!Array.isArray(e)){const s=e;n=s.geometry&&s.geometry.animations||s.animations}for(let s=0;s<n.length;s++)if(n[s].name===t)return n[s];return null}static CreateClipsFromMorphTargetSequences(e,t,n){const s={},r=/^([\w-]*?)([\d]+)$/;for(let a=0,c=e.length;a<c;a++){const l=e[a],u=l.name.match(r);if(u&&u.length>1){const h=u[1];let f=s[h];f||(s[h]=f=[]),f.push(l)}}const o=[];for(const a in s)o.push(this.CreateFromMorphTargetSequence(a,s[a],t,n));return o}static parseAnimation(e,t){if(!e)return console.error("THREE.AnimationClip: No animation in JSONLoader data."),null;const n=function(h,f,d,g,_){if(d.length!==0){const p=[],m=[];cd(d,p,m,g),p.length!==0&&_.push(new h(f,p,m))}},s=[],r=e.name||"default",o=e.fps||30,a=e.blendMode;let c=e.length||-1;const l=e.hierarchy||[];for(let h=0;h<l.length;h++){const f=l[h].keys;if(!(!f||f.length===0))if(f[0].morphTargets){const d={};let g;for(g=0;g<f.length;g++)if(f[g].morphTargets)for(let _=0;_<f[g].morphTargets.length;_++)d[f[g].morphTargets[_]]=-1;for(const _ in d){const p=[],m=[];for(let v=0;v!==f[g].morphTargets.length;++v){const y=f[g];p.push(y.time),m.push(y.morphTarget===_?1:0)}s.push(new rr(".morphTargetInfluence["+_+"]",p,m))}c=d.length*o}else{const d=".bones["+t[h].name+"]";n(ar,d+".position",f,"pos",s),n(or,d+".quaternion",f,"rot",s),n(ar,d+".scale",f,"scl",s)}}return s.length===0?null:new this(r,c,s,a)}resetDuration(){const e=this.tracks;let t=0;for(let n=0,s=e.length;n!==s;++n){const r=this.tracks[n];t=Math.max(t,r.times[r.times.length-1])}return this.duration=t,this}trim(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].trim(0,this.duration);return this}validate(){let e=!0;for(let t=0;t<this.tracks.length;t++)e=e&&this.tracks[t].validate();return e}optimize(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].optimize();return this}clone(){const e=[];for(let t=0;t<this.tracks.length;t++)e.push(this.tracks[t].clone());return new this.constructor(this.name,this.duration,e,this.blendMode)}toJSON(){return this.constructor.toJSON(this)}}function my(i){switch(i.toLowerCase()){case"scalar":case"double":case"float":case"number":case"integer":return rr;case"vector":case"vector2":case"vector3":case"vector4":return ar;case"color":return ld;case"quaternion":return or;case"bool":case"boolean":return hr;case"string":return fr}throw new Error("THREE.KeyframeTrack: Unsupported typeName: "+i)}function gy(i){if(i.type===void 0)throw new Error("THREE.KeyframeTrack: track type undefined, can not parse");const e=my(i.type);if(i.times===void 0){const t=[],n=[];cd(i.keys,t,n,"value"),i.times=t,i.values=n}return e.parse!==void 0?e.parse(i):new e(i.name,i.times,i.values,i.interpolation)}const Bi={enabled:!1,files:{},add:function(i,e){this.enabled!==!1&&(this.files[i]=e)},get:function(i){if(this.enabled!==!1)return this.files[i]},remove:function(i){delete this.files[i]},clear:function(){this.files={}}};class _y{constructor(e,t,n){const s=this;let r=!1,o=0,a=0,c;const l=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this.itemStart=function(u){a++,r===!1&&s.onStart!==void 0&&s.onStart(u,o,a),r=!0},this.itemEnd=function(u){o++,s.onProgress!==void 0&&s.onProgress(u,o,a),o===a&&(r=!1,s.onLoad!==void 0&&s.onLoad())},this.itemError=function(u){s.onError!==void 0&&s.onError(u)},this.resolveURL=function(u){return c?c(u):u},this.setURLModifier=function(u){return c=u,this},this.addHandler=function(u,h){return l.push(u,h),this},this.removeHandler=function(u){const h=l.indexOf(u);return h!==-1&&l.splice(h,2),this},this.getHandler=function(u){for(let h=0,f=l.length;h<f;h+=2){const d=l[h],g=l[h+1];if(d.global&&(d.lastIndex=0),d.test(u))return g}return null}}}const xy=new _y;class ys{constructor(e){this.manager=e!==void 0?e:xy,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){const n=this;return new Promise(function(s,r){n.load(e,s,t,r)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}}ys.DEFAULT_MATERIAL_NAME="__DEFAULT";const hi={};class vy extends Error{constructor(e,t){super(e),this.response=t}}class oa extends ys{constructor(e){super(e)}load(e,t,n,s){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const r=Bi.get(e);if(r!==void 0)return this.manager.itemStart(e),setTimeout(()=>{t&&t(r),this.manager.itemEnd(e)},0),r;if(hi[e]!==void 0){hi[e].push({onLoad:t,onProgress:n,onError:s});return}hi[e]=[],hi[e].push({onLoad:t,onProgress:n,onError:s});const o=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin"}),a=this.mimeType,c=this.responseType;fetch(o).then(l=>{if(l.status===200||l.status===0){if(l.status===0&&console.warn("THREE.FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||l.body===void 0||l.body.getReader===void 0)return l;const u=hi[e],h=l.body.getReader(),f=l.headers.get("X-File-Size")||l.headers.get("Content-Length"),d=f?parseInt(f):0,g=d!==0;let _=0;const p=new ReadableStream({start(m){v();function v(){h.read().then(({done:y,value:x})=>{if(y)m.close();else{_+=x.byteLength;const P=new ProgressEvent("progress",{lengthComputable:g,loaded:_,total:d});for(let A=0,E=u.length;A<E;A++){const R=u[A];R.onProgress&&R.onProgress(P)}m.enqueue(x),v()}},y=>{m.error(y)})}}});return new Response(p)}else throw new vy(`fetch for "${l.url}" responded with ${l.status}: ${l.statusText}`,l)}).then(l=>{switch(c){case"arraybuffer":return l.arrayBuffer();case"blob":return l.blob();case"document":return l.text().then(u=>new DOMParser().parseFromString(u,a));case"json":return l.json();default:if(a===void 0)return l.text();{const h=/charset="?([^;"\s]*)"?/i.exec(a),f=h&&h[1]?h[1].toLowerCase():void 0,d=new TextDecoder(f);return l.arrayBuffer().then(g=>d.decode(g))}}}).then(l=>{Bi.add(e,l);const u=hi[e];delete hi[e];for(let h=0,f=u.length;h<f;h++){const d=u[h];d.onLoad&&d.onLoad(l)}}).catch(l=>{const u=hi[e];if(u===void 0)throw this.manager.itemError(e),l;delete hi[e];for(let h=0,f=u.length;h<f;h++){const d=u[h];d.onError&&d.onError(l)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}}class yy extends ys{constructor(e){super(e)}load(e,t,n,s){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const r=this,o=Bi.get(e);if(o!==void 0)return r.manager.itemStart(e),setTimeout(function(){t&&t(o),r.manager.itemEnd(e)},0),o;const a=Wr("img");function c(){u(),Bi.add(e,this),t&&t(this),r.manager.itemEnd(e)}function l(h){u(),s&&s(h),r.manager.itemError(e),r.manager.itemEnd(e)}function u(){a.removeEventListener("load",c,!1),a.removeEventListener("error",l,!1)}return a.addEventListener("load",c,!1),a.addEventListener("error",l,!1),e.slice(0,5)!=="data:"&&this.crossOrigin!==void 0&&(a.crossOrigin=this.crossOrigin),r.manager.itemStart(e),a.src=e,a}}class My extends ys{constructor(e){super(e)}load(e,t,n,s){const r=new jt,o=new yy(this.manager);return o.setCrossOrigin(this.crossOrigin),o.setPath(this.path),o.load(e,function(a){r.image=a,r.needsUpdate=!0,t!==void 0&&t(r)},n,s),r}}class nu extends It{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new ze(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}const cc=new Le,Hh=new M,Vh=new M;class iu{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new te(512,512),this.map=null,this.mapPass=null,this.matrix=new Le,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Gl,this._frameExtents=new te(1,1),this._viewportCount=1,this._viewports=[new dt(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;Hh.setFromMatrixPosition(e.matrixWorld),t.position.copy(Hh),Vh.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Vh),t.updateMatrixWorld(),cc.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(cc),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(cc)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class Sy extends iu{constructor(){super(new _n(50,1,.5,500)),this.isSpotLightShadow=!0,this.focus=1}updateMatrices(e){const t=this.camera,n=nr*2*e.angle*this.focus,s=this.mapSize.width/this.mapSize.height,r=e.distance||t.far;(n!==t.fov||s!==t.aspect||r!==t.far)&&(t.fov=n,t.aspect=s,t.far=r,t.updateProjectionMatrix()),super.updateMatrices(e)}copy(e){return super.copy(e),this.focus=e.focus,this}}class by extends nu{constructor(e,t,n=0,s=Math.PI/3,r=0,o=2){super(e,t),this.isSpotLight=!0,this.type="SpotLight",this.position.copy(It.DEFAULT_UP),this.updateMatrix(),this.target=new It,this.distance=n,this.angle=s,this.penumbra=r,this.decay=o,this.map=null,this.shadow=new Sy}get power(){return this.intensity*Math.PI}set power(e){this.intensity=e/Math.PI}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.angle=e.angle,this.penumbra=e.penumbra,this.decay=e.decay,this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}const Gh=new Le,Er=new M,lc=new M;class wy extends iu{constructor(){super(new _n(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new te(4,2),this._viewportCount=6,this._viewports=[new dt(2,1,1,1),new dt(0,1,1,1),new dt(3,1,1,1),new dt(1,1,1,1),new dt(3,0,1,1),new dt(1,0,1,1)],this._cubeDirections=[new M(1,0,0),new M(-1,0,0),new M(0,0,1),new M(0,0,-1),new M(0,1,0),new M(0,-1,0)],this._cubeUps=[new M(0,1,0),new M(0,1,0),new M(0,1,0),new M(0,1,0),new M(0,0,1),new M(0,0,-1)]}updateMatrices(e,t=0){const n=this.camera,s=this.matrix,r=e.distance||n.far;r!==n.far&&(n.far=r,n.updateProjectionMatrix()),Er.setFromMatrixPosition(e.matrixWorld),n.position.copy(Er),lc.copy(n.position),lc.add(this._cubeDirections[t]),n.up.copy(this._cubeUps[t]),n.lookAt(lc),n.updateMatrixWorld(),s.makeTranslation(-Er.x,-Er.y,-Er.z),Gh.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Gh)}}class Ey extends nu{constructor(e,t,n=0,s=2){super(e,t),this.isPointLight=!0,this.type="PointLight",this.distance=n,this.decay=s,this.shadow=new wy}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}}class Ty extends iu{constructor(){super(new pa(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class Ay extends nu{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(It.DEFAULT_UP),this.updateMatrix(),this.target=new It,this.shadow=new Ty}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class kr{static decodeText(e){if(console.warn("THREE.LoaderUtils: decodeText() has been deprecated with r165 and will be removed with r175. Use TextDecoder instead."),typeof TextDecoder<"u")return new TextDecoder().decode(e);let t="";for(let n=0,s=e.length;n<s;n++)t+=String.fromCharCode(e[n]);try{return decodeURIComponent(escape(t))}catch{return t}}static extractUrlBase(e){const t=e.lastIndexOf("/");return t===-1?"./":e.slice(0,t+1)}static resolveURL(e,t){return typeof e!="string"||e===""?"":(/^https?:\/\//i.test(t)&&/^\//.test(e)&&(t=t.replace(/(^https?:\/\/[^\/]+).*/i,"$1")),/^(https?:)?\/\//i.test(e)||/^data:.*,.*$/i.test(e)||/^blob:.*$/i.test(e)?e:t+e)}}class Ry extends ys{constructor(e){super(e),this.isImageBitmapLoader=!0,typeof createImageBitmap>"u"&&console.warn("THREE.ImageBitmapLoader: createImageBitmap() not supported."),typeof fetch>"u"&&console.warn("THREE.ImageBitmapLoader: fetch() not supported."),this.options={premultiplyAlpha:"none"}}setOptions(e){return this.options=e,this}load(e,t,n,s){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const r=this,o=Bi.get(e);if(o!==void 0){if(r.manager.itemStart(e),o.then){o.then(l=>{t&&t(l),r.manager.itemEnd(e)}).catch(l=>{s&&s(l)});return}return setTimeout(function(){t&&t(o),r.manager.itemEnd(e)},0),o}const a={};a.credentials=this.crossOrigin==="anonymous"?"same-origin":"include",a.headers=this.requestHeader;const c=fetch(e,a).then(function(l){return l.blob()}).then(function(l){return createImageBitmap(l,Object.assign(r.options,{colorSpaceConversion:"none"}))}).then(function(l){return Bi.add(e,l),t&&t(l),r.manager.itemEnd(e),l}).catch(function(l){s&&s(l),Bi.remove(e),r.manager.itemError(e),r.manager.itemEnd(e)});Bi.add(e,c),r.manager.itemStart(e)}}const su="\\[\\]\\.:\\/",Cy=new RegExp("["+su+"]","g"),ru="[^"+su+"]",Py="[^"+su.replace("\\.","")+"]",Ly=/((?:WC+[\/:])*)/.source.replace("WC",ru),Iy=/(WCOD+)?/.source.replace("WCOD",Py),Dy=/(?:\.(WC+)(?:\[(.+)\])?)?/.source.replace("WC",ru),Ny=/\.(WC+)(?:\[(.+)\])?/.source.replace("WC",ru),Uy=new RegExp("^"+Ly+Iy+Dy+Ny+"$"),Oy=["material","materials","bones","map"];class Fy{constructor(e,t,n){const s=n||yt.parseTrackName(t);this._targetGroup=e,this._bindings=e.subscribe_(t,s)}getValue(e,t){this.bind();const n=this._targetGroup.nCachedObjects_,s=this._bindings[n];s!==void 0&&s.getValue(e,t)}setValue(e,t){const n=this._bindings;for(let s=this._targetGroup.nCachedObjects_,r=n.length;s!==r;++s)n[s].setValue(e,t)}bind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].bind()}unbind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].unbind()}}class yt{constructor(e,t,n){this.path=t,this.parsedPath=n||yt.parseTrackName(t),this.node=yt.findNode(e,this.parsedPath.nodeName),this.rootNode=e,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}static create(e,t,n){return e&&e.isAnimationObjectGroup?new yt.Composite(e,t,n):new yt(e,t,n)}static sanitizeNodeName(e){return e.replace(/\s/g,"_").replace(Cy,"")}static parseTrackName(e){const t=Uy.exec(e);if(t===null)throw new Error("PropertyBinding: Cannot parse trackName: "+e);const n={nodeName:t[2],objectName:t[3],objectIndex:t[4],propertyName:t[5],propertyIndex:t[6]},s=n.nodeName&&n.nodeName.lastIndexOf(".");if(s!==void 0&&s!==-1){const r=n.nodeName.substring(s+1);Oy.indexOf(r)!==-1&&(n.nodeName=n.nodeName.substring(0,s),n.objectName=r)}if(n.propertyName===null||n.propertyName.length===0)throw new Error("PropertyBinding: can not parse propertyName from trackName: "+e);return n}static findNode(e,t){if(t===void 0||t===""||t==="."||t===-1||t===e.name||t===e.uuid)return e;if(e.skeleton){const n=e.skeleton.getBoneByName(t);if(n!==void 0)return n}if(e.children){const n=function(r){for(let o=0;o<r.length;o++){const a=r[o];if(a.name===t||a.uuid===t)return a;const c=n(a.children);if(c)return c}return null},s=n(e.children);if(s)return s}return null}_getValue_unavailable(){}_setValue_unavailable(){}_getValue_direct(e,t){e[t]=this.targetObject[this.propertyName]}_getValue_array(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)e[t++]=n[s]}_getValue_arrayElement(e,t){e[t]=this.resolvedProperty[this.propertyIndex]}_getValue_toArray(e,t){this.resolvedProperty.toArray(e,t)}_setValue_direct(e,t){this.targetObject[this.propertyName]=e[t]}_setValue_direct_setNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.needsUpdate=!0}_setValue_direct_setMatrixWorldNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_array(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)n[s]=e[t++]}_setValue_array_setNeedsUpdate(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)n[s]=e[t++];this.targetObject.needsUpdate=!0}_setValue_array_setMatrixWorldNeedsUpdate(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)n[s]=e[t++];this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_arrayElement(e,t){this.resolvedProperty[this.propertyIndex]=e[t]}_setValue_arrayElement_setNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.needsUpdate=!0}_setValue_arrayElement_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_fromArray(e,t){this.resolvedProperty.fromArray(e,t)}_setValue_fromArray_setNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.needsUpdate=!0}_setValue_fromArray_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.matrixWorldNeedsUpdate=!0}_getValue_unbound(e,t){this.bind(),this.getValue(e,t)}_setValue_unbound(e,t){this.bind(),this.setValue(e,t)}bind(){let e=this.node;const t=this.parsedPath,n=t.objectName,s=t.propertyName;let r=t.propertyIndex;if(e||(e=yt.findNode(this.rootNode,t.nodeName),this.node=e),this.getValue=this._getValue_unavailable,this.setValue=this._setValue_unavailable,!e){console.warn("THREE.PropertyBinding: No target node found for track: "+this.path+".");return}if(n){let l=t.objectIndex;switch(n){case"materials":if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.materials){console.error("THREE.PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.",this);return}e=e.material.materials;break;case"bones":if(!e.skeleton){console.error("THREE.PropertyBinding: Can not bind to bones as node does not have a skeleton.",this);return}e=e.skeleton.bones;for(let u=0;u<e.length;u++)if(e[u].name===l){l=u;break}break;case"map":if("map"in e){e=e.map;break}if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.map){console.error("THREE.PropertyBinding: Can not bind to material.map as node.material does not have a map.",this);return}e=e.material.map;break;default:if(e[n]===void 0){console.error("THREE.PropertyBinding: Can not bind to objectName of node undefined.",this);return}e=e[n]}if(l!==void 0){if(e[l]===void 0){console.error("THREE.PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.",this,e);return}e=e[l]}}const o=e[s];if(o===void 0){const l=t.nodeName;console.error("THREE.PropertyBinding: Trying to update property for track: "+l+"."+s+" but it wasn't found.",e);return}let a=this.Versioning.None;this.targetObject=e,e.needsUpdate!==void 0?a=this.Versioning.NeedsUpdate:e.matrixWorldNeedsUpdate!==void 0&&(a=this.Versioning.MatrixWorldNeedsUpdate);let c=this.BindingType.Direct;if(r!==void 0){if(s==="morphTargetInfluences"){if(!e.geometry){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.",this);return}if(!e.geometry.morphAttributes){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.",this);return}e.morphTargetDictionary[r]!==void 0&&(r=e.morphTargetDictionary[r])}c=this.BindingType.ArrayElement,this.resolvedProperty=o,this.propertyIndex=r}else o.fromArray!==void 0&&o.toArray!==void 0?(c=this.BindingType.HasFromToArray,this.resolvedProperty=o):Array.isArray(o)?(c=this.BindingType.EntireArray,this.resolvedProperty=o):this.propertyName=s;this.getValue=this.GetterByBindingType[c],this.setValue=this.SetterByBindingTypeAndVersioning[c][a]}unbind(){this.node=null,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}}yt.Composite=Fy;yt.prototype.BindingType={Direct:0,EntireArray:1,ArrayElement:2,HasFromToArray:3};yt.prototype.Versioning={None:0,NeedsUpdate:1,MatrixWorldNeedsUpdate:2};yt.prototype.GetterByBindingType=[yt.prototype._getValue_direct,yt.prototype._getValue_array,yt.prototype._getValue_arrayElement,yt.prototype._getValue_toArray];yt.prototype.SetterByBindingTypeAndVersioning=[[yt.prototype._setValue_direct,yt.prototype._setValue_direct_setNeedsUpdate,yt.prototype._setValue_direct_setMatrixWorldNeedsUpdate],[yt.prototype._setValue_array,yt.prototype._setValue_array_setNeedsUpdate,yt.prototype._setValue_array_setMatrixWorldNeedsUpdate],[yt.prototype._setValue_arrayElement,yt.prototype._setValue_arrayElement_setNeedsUpdate,yt.prototype._setValue_arrayElement_setMatrixWorldNeedsUpdate],[yt.prototype._setValue_fromArray,yt.prototype._setValue_fromArray_setNeedsUpdate,yt.prototype._setValue_fromArray_setMatrixWorldNeedsUpdate]];typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:Dl}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=Dl);const By=12,ky=Dn.degToRad(By),zy=1e-7,Hy=1e-7,Vy=new M(1,1,1),ud=i=>new Le().makeTranslation(i.x,i.y,i.z),Wh=(i,e,t)=>e.get(t).clone().multiply(ud(i.heads.get(t)));function uc(i,e,t){const n=i.parents.get(t),s=Wh(i,e,t);return n?Wh(i,e,n).invert().multiply(s):s}const hc=i=>{const e=new M,t=new On,n=new M;return i.decompose(e,t,n),{at:e,turn:t}};function Gy(i,e,t,n,s=e,r=ky){const o=new Map,a=new Map;let c=n>=1;for(const l of i.order){const u=hc(uc(i,e,l)),h=hc(uc(i,t,l)),f=hc(uc(i,s,l)),d=u.at.lerp(h.at,n),g=u.turn.slerp(h.turn,n),_=f.turn.angleTo(g),p=f.turn.slerp(g,_>r?r/_:1),m=new Le().compose(d,p,Vy),v=i.parents.get(l),y=v?o.get(v).clone().multiply(m):m;o.set(l,y),a.set(l,y.clone().multiply(ud(i.heads.get(l).clone().negate()))),c&&(c=p.angleTo(h.turn)<zy&&d.distanceTo(h.at)<Hy)}return{moves:a,settled:c}}const un={hat:{base:3.53,crown:.86,height:1,brim:.2,thick:.05,curl:.18,band:[.04,.24],bandOut:.015,sides:48},white:[.97,.97,.95],whites:["hand_shell_l","hand_shell_r","butler_bow_tie__knot","butler_bow_tie__loop_l","butler_bow_tie__loop_r","butler_shirt__collar_band","butler_shirt__collar_point_l","butler_shirt__collar_point_r"],wing:{points:[[.04,2.47],[.19,2.45],[.09,2.36]],z:.43,thick:.02},tails:{side:[[-.3,1.78],[-.47,1.78],[-.68,.72],[-.58,.72]],across:[.04,.36]},satin:[.15,.15,.24],removed:["butler_bowler_hat","butler_tailcoat__tail_l","butler_tailcoat__tail_r"],satOn:["butler_tail_l","butler_tail_r"]};function zo(i,e,t,n){t.applyMatrix4(i.matrixWorld.clone().invert());const s=t.attributes.position.count,r=i.geometry.attributes.skinIndex.getX(0);t.setAttribute("skinIndex",new Vl(Array.from({length:s*4},(a,c)=>c%4?0:r),4)),t.setAttribute("skinWeight",new rt(Array.from({length:s*4},(a,c)=>c%4?0:1),4));const o=new ql(t,new on({color:new ze(...n)}));return o.name=e,o.userData={item:e},o.position.copy(i.position),o.quaternion.copy(i.quaternion),o.scale.copy(i.scale),i.parent.add(o),o.bind(i.skeleton,i.bindMatrix),o.updateMatrixWorld(!0),o}function hd(){const{crown:i,height:e,brim:t,thick:n,curl:s,sides:r}=un.hat,o=i+t,a=[[.001,0],[o,0],[o,n],[i,n],[i,e],[.001,e]],c=new Zr(a.map(([u,h])=>new te(u,h)),r),l=c.attributes.position;for(let u=0;u<l.count;u++){const[h,f,d]=[l.getX(u),l.getY(u),l.getZ(u)],g=Math.hypot(h,d);f<=n+1e-6&&g>i&&l.setY(u,f+s*((g-i)/t)**2*(h/g)**2)}return c.computeVertexNormals(),c}function fd(){const{crown:i,band:e,bandOut:t,sides:n}=un.hat,s=new bt(i+t,i+t,e[1]-e[0],n,1,!0);return s.translate(0,(e[0]+e[1])/2,0),s}function Wy(i){const{points:e,z:t,thick:n}=un.wing,s=new Un(e.map(([o,a])=>new te(i*o,a))),r=new Jr(s,{depth:n,bevelEnabled:!1});return r.translate(0,0,t),r}function Xy(i){const{side:e,across:t}=un.tails,n=new Un(e.map(([r,o])=>new te(r,o))),s=new Jr(n,{depth:t[1]-t[0],bevelEnabled:!1});return s.rotateY(-Math.PI/2),s.translate(i>0?t[1]:-.04,0,0),s.computeVertexNormals(),s}function qy(i){const e=u=>i.find(h=>h.name===u);for(const u of i.filter(h=>un.whites.includes(h.name)))u.material=u.material.clone(),u.material.color.setRGB(...un.white);const t=e("butler_bowler_hat__crown"),n=new pn().setFromObject(t).getCenter(new M),s=t.material.color.toArray(),r=e("butler_tailcoat__body").material.color.toArray(),o=e("butler_bow_tie__knot"),a=e("butler_tailcoat__tail_l"),c=[zo(t,"butler_top_hat",hd().translate(n.x,un.hat.base,n.z),s),zo(t,"butler_top_hat_band",fd().translate(n.x,un.hat.base,n.z),un.satin),...[1,-1].map(u=>zo(o,`butler_wing_collar_${u>0?"l":"r"}`,Wy(u),un.white)),...[1,-1].map(u=>zo(a,`butler_tail_${u>0?"l":"r"}`,Xy(u),r))],l=i.filter(u=>un.removed.some(h=>u.name.startsWith(h)));for(const u of l)u.parent.remove(u);return[...i.filter(u=>!l.includes(u)),...c]}function Xh(i,e){if(e===kp)return console.warn("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles."),i;if(e===ml||e===If){let t=i.getIndex();if(t===null){const o=[],a=i.getAttribute("position");if(a!==void 0){for(let c=0;c<a.count;c++)o.push(c);i.setIndex(o),t=i.getIndex()}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible."),i}const n=t.count-2,s=[];if(e===ml)for(let o=1;o<=n;o++)s.push(t.getX(0)),s.push(t.getX(o)),s.push(t.getX(o+1));else for(let o=0;o<n;o++)o%2===0?(s.push(t.getX(o)),s.push(t.getX(o+1)),s.push(t.getX(o+2))):(s.push(t.getX(o+2)),s.push(t.getX(o+1)),s.push(t.getX(o)));s.length/3!==n&&console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.");const r=i.clone();return r.setIndex(s),r.clearGroups(),r}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:",e),i}class Yy extends ys{constructor(e){super(e),this.dracoLoader=null,this.ktx2Loader=null,this.meshoptDecoder=null,this.pluginCallbacks=[],this.register(function(t){return new Jy(t)}),this.register(function(t){return new Qy(t)}),this.register(function(t){return new cM(t)}),this.register(function(t){return new lM(t)}),this.register(function(t){return new uM(t)}),this.register(function(t){return new tM(t)}),this.register(function(t){return new nM(t)}),this.register(function(t){return new iM(t)}),this.register(function(t){return new sM(t)}),this.register(function(t){return new Zy(t)}),this.register(function(t){return new rM(t)}),this.register(function(t){return new eM(t)}),this.register(function(t){return new aM(t)}),this.register(function(t){return new oM(t)}),this.register(function(t){return new $y(t)}),this.register(function(t){return new hM(t)}),this.register(function(t){return new fM(t)})}load(e,t,n,s){const r=this;let o;if(this.resourcePath!=="")o=this.resourcePath;else if(this.path!==""){const l=kr.extractUrlBase(e);o=kr.resolveURL(l,this.path)}else o=kr.extractUrlBase(e);this.manager.itemStart(e);const a=function(l){s?s(l):console.error(l),r.manager.itemError(e),r.manager.itemEnd(e)},c=new oa(this.manager);c.setPath(this.path),c.setResponseType("arraybuffer"),c.setRequestHeader(this.requestHeader),c.setWithCredentials(this.withCredentials),c.load(e,function(l){try{r.parse(l,o,function(u){t(u),r.manager.itemEnd(e)},a)}catch(u){a(u)}},n,a)}setDRACOLoader(e){return this.dracoLoader=e,this}setKTX2Loader(e){return this.ktx2Loader=e,this}setMeshoptDecoder(e){return this.meshoptDecoder=e,this}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,s){let r;const o={},a={},c=new TextDecoder;if(typeof e=="string")r=JSON.parse(e);else if(e instanceof ArrayBuffer)if(c.decode(new Uint8Array(e,0,4))===dd){try{o[st.KHR_BINARY_GLTF]=new dM(e)}catch(h){s&&s(h);return}r=JSON.parse(o[st.KHR_BINARY_GLTF].content)}else r=JSON.parse(c.decode(e));else r=e;if(r.asset===void 0||r.asset.version[0]<2){s&&s(new Error("THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported."));return}const l=new TM(r,{path:t||this.resourcePath||"",crossOrigin:this.crossOrigin,requestHeader:this.requestHeader,manager:this.manager,ktx2Loader:this.ktx2Loader,meshoptDecoder:this.meshoptDecoder});l.fileLoader.setRequestHeader(this.requestHeader);for(let u=0;u<this.pluginCallbacks.length;u++){const h=this.pluginCallbacks[u](l);h.name||console.error("THREE.GLTFLoader: Invalid plugin found: missing name"),a[h.name]=h,o[h.name]=!0}if(r.extensionsUsed)for(let u=0;u<r.extensionsUsed.length;++u){const h=r.extensionsUsed[u],f=r.extensionsRequired||[];switch(h){case st.KHR_MATERIALS_UNLIT:o[h]=new Ky;break;case st.KHR_DRACO_MESH_COMPRESSION:o[h]=new pM(r,this.dracoLoader);break;case st.KHR_TEXTURE_TRANSFORM:o[h]=new mM;break;case st.KHR_MESH_QUANTIZATION:o[h]=new gM;break;default:f.indexOf(h)>=0&&a[h]===void 0&&console.warn('THREE.GLTFLoader: Unknown extension "'+h+'".')}}l.setExtensions(o),l.setPlugins(a),l.parse(n,s)}parseAsync(e,t){const n=this;return new Promise(function(s,r){n.parse(e,t,s,r)})}}function jy(){let i={};return{get:function(e){return i[e]},add:function(e,t){i[e]=t},remove:function(e){delete i[e]},removeAll:function(){i={}}}}const st={KHR_BINARY_GLTF:"KHR_binary_glTF",KHR_DRACO_MESH_COMPRESSION:"KHR_draco_mesh_compression",KHR_LIGHTS_PUNCTUAL:"KHR_lights_punctual",KHR_MATERIALS_CLEARCOAT:"KHR_materials_clearcoat",KHR_MATERIALS_DISPERSION:"KHR_materials_dispersion",KHR_MATERIALS_IOR:"KHR_materials_ior",KHR_MATERIALS_SHEEN:"KHR_materials_sheen",KHR_MATERIALS_SPECULAR:"KHR_materials_specular",KHR_MATERIALS_TRANSMISSION:"KHR_materials_transmission",KHR_MATERIALS_IRIDESCENCE:"KHR_materials_iridescence",KHR_MATERIALS_ANISOTROPY:"KHR_materials_anisotropy",KHR_MATERIALS_UNLIT:"KHR_materials_unlit",KHR_MATERIALS_VOLUME:"KHR_materials_volume",KHR_TEXTURE_BASISU:"KHR_texture_basisu",KHR_TEXTURE_TRANSFORM:"KHR_texture_transform",KHR_MESH_QUANTIZATION:"KHR_mesh_quantization",KHR_MATERIALS_EMISSIVE_STRENGTH:"KHR_materials_emissive_strength",EXT_MATERIALS_BUMP:"EXT_materials_bump",EXT_TEXTURE_WEBP:"EXT_texture_webp",EXT_TEXTURE_AVIF:"EXT_texture_avif",EXT_MESHOPT_COMPRESSION:"EXT_meshopt_compression",EXT_MESH_GPU_INSTANCING:"EXT_mesh_gpu_instancing"};class $y{constructor(e){this.parser=e,this.name=st.KHR_LIGHTS_PUNCTUAL,this.cache={refs:{},uses:{}}}_markDefs(){const e=this.parser,t=this.parser.json.nodes||[];for(let n=0,s=t.length;n<s;n++){const r=t[n];r.extensions&&r.extensions[this.name]&&r.extensions[this.name].light!==void 0&&e._addNodeRef(this.cache,r.extensions[this.name].light)}}_loadLight(e){const t=this.parser,n="light:"+e;let s=t.cache.get(n);if(s)return s;const r=t.json,c=((r.extensions&&r.extensions[this.name]||{}).lights||[])[e];let l;const u=new ze(16777215);c.color!==void 0&&u.setRGB(c.color[0],c.color[1],c.color[2],an);const h=c.range!==void 0?c.range:0;switch(c.type){case"directional":l=new Ay(u),l.target.position.set(0,0,-1),l.add(l.target);break;case"point":l=new Ey(u),l.distance=h;break;case"spot":l=new by(u),l.distance=h,c.spot=c.spot||{},c.spot.innerConeAngle=c.spot.innerConeAngle!==void 0?c.spot.innerConeAngle:0,c.spot.outerConeAngle=c.spot.outerConeAngle!==void 0?c.spot.outerConeAngle:Math.PI/4,l.angle=c.spot.outerConeAngle,l.penumbra=1-c.spot.innerConeAngle/c.spot.outerConeAngle,l.target.position.set(0,0,-1),l.add(l.target);break;default:throw new Error("THREE.GLTFLoader: Unexpected light type: "+c.type)}return l.position.set(0,0,0),l.decay=2,pi(l,c),c.intensity!==void 0&&(l.intensity=c.intensity),l.name=t.createUniqueName(c.name||"light_"+e),s=Promise.resolve(l),t.cache.add(n,s),s}getDependency(e,t){if(e==="light")return this._loadLight(t)}createNodeAttachment(e){const t=this,n=this.parser,r=n.json.nodes[e],a=(r.extensions&&r.extensions[this.name]||{}).light;return a===void 0?null:this._loadLight(a).then(function(c){return n._getNodeRef(t.cache,a,c)})}}class Ky{constructor(){this.name=st.KHR_MATERIALS_UNLIT}getMaterialType(){return on}extendParams(e,t,n){const s=[];e.color=new ze(1,1,1),e.opacity=1;const r=t.pbrMetallicRoughness;if(r){if(Array.isArray(r.baseColorFactor)){const o=r.baseColorFactor;e.color.setRGB(o[0],o[1],o[2],an),e.opacity=o[3]}r.baseColorTexture!==void 0&&s.push(n.assignTexture(e,"map",r.baseColorTexture,Ht))}return Promise.all(s)}}class Zy{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_EMISSIVE_STRENGTH}extendMaterialParams(e,t){const s=this.parser.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=s.extensions[this.name].emissiveStrength;return r!==void 0&&(t.emissiveIntensity=r),Promise.resolve()}}class Jy{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_CLEARCOAT}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:ni}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];if(o.clearcoatFactor!==void 0&&(t.clearcoat=o.clearcoatFactor),o.clearcoatTexture!==void 0&&r.push(n.assignTexture(t,"clearcoatMap",o.clearcoatTexture)),o.clearcoatRoughnessFactor!==void 0&&(t.clearcoatRoughness=o.clearcoatRoughnessFactor),o.clearcoatRoughnessTexture!==void 0&&r.push(n.assignTexture(t,"clearcoatRoughnessMap",o.clearcoatRoughnessTexture)),o.clearcoatNormalTexture!==void 0&&(r.push(n.assignTexture(t,"clearcoatNormalMap",o.clearcoatNormalTexture)),o.clearcoatNormalTexture.scale!==void 0)){const a=o.clearcoatNormalTexture.scale;t.clearcoatNormalScale=new te(a,a)}return Promise.all(r)}}class Qy{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_DISPERSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:ni}extendMaterialParams(e,t){const s=this.parser.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=s.extensions[this.name];return t.dispersion=r.dispersion!==void 0?r.dispersion:0,Promise.resolve()}}class eM{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_IRIDESCENCE}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:ni}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return o.iridescenceFactor!==void 0&&(t.iridescence=o.iridescenceFactor),o.iridescenceTexture!==void 0&&r.push(n.assignTexture(t,"iridescenceMap",o.iridescenceTexture)),o.iridescenceIor!==void 0&&(t.iridescenceIOR=o.iridescenceIor),t.iridescenceThicknessRange===void 0&&(t.iridescenceThicknessRange=[100,400]),o.iridescenceThicknessMinimum!==void 0&&(t.iridescenceThicknessRange[0]=o.iridescenceThicknessMinimum),o.iridescenceThicknessMaximum!==void 0&&(t.iridescenceThicknessRange[1]=o.iridescenceThicknessMaximum),o.iridescenceThicknessTexture!==void 0&&r.push(n.assignTexture(t,"iridescenceThicknessMap",o.iridescenceThicknessTexture)),Promise.all(r)}}class tM{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_SHEEN}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:ni}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[];t.sheenColor=new ze(0,0,0),t.sheenRoughness=0,t.sheen=1;const o=s.extensions[this.name];if(o.sheenColorFactor!==void 0){const a=o.sheenColorFactor;t.sheenColor.setRGB(a[0],a[1],a[2],an)}return o.sheenRoughnessFactor!==void 0&&(t.sheenRoughness=o.sheenRoughnessFactor),o.sheenColorTexture!==void 0&&r.push(n.assignTexture(t,"sheenColorMap",o.sheenColorTexture,Ht)),o.sheenRoughnessTexture!==void 0&&r.push(n.assignTexture(t,"sheenRoughnessMap",o.sheenRoughnessTexture)),Promise.all(r)}}class nM{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_TRANSMISSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:ni}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return o.transmissionFactor!==void 0&&(t.transmission=o.transmissionFactor),o.transmissionTexture!==void 0&&r.push(n.assignTexture(t,"transmissionMap",o.transmissionTexture)),Promise.all(r)}}class iM{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_VOLUME}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:ni}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];t.thickness=o.thicknessFactor!==void 0?o.thicknessFactor:0,o.thicknessTexture!==void 0&&r.push(n.assignTexture(t,"thicknessMap",o.thicknessTexture)),t.attenuationDistance=o.attenuationDistance||1/0;const a=o.attenuationColor||[1,1,1];return t.attenuationColor=new ze().setRGB(a[0],a[1],a[2],an),Promise.all(r)}}class sM{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_IOR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:ni}extendMaterialParams(e,t){const s=this.parser.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=s.extensions[this.name];return t.ior=r.ior!==void 0?r.ior:1.5,Promise.resolve()}}class rM{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_SPECULAR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:ni}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];t.specularIntensity=o.specularFactor!==void 0?o.specularFactor:1,o.specularTexture!==void 0&&r.push(n.assignTexture(t,"specularIntensityMap",o.specularTexture));const a=o.specularColorFactor||[1,1,1];return t.specularColor=new ze().setRGB(a[0],a[1],a[2],an),o.specularColorTexture!==void 0&&r.push(n.assignTexture(t,"specularColorMap",o.specularColorTexture,Ht)),Promise.all(r)}}class oM{constructor(e){this.parser=e,this.name=st.EXT_MATERIALS_BUMP}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:ni}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return t.bumpScale=o.bumpFactor!==void 0?o.bumpFactor:1,o.bumpTexture!==void 0&&r.push(n.assignTexture(t,"bumpMap",o.bumpTexture)),Promise.all(r)}}class aM{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_ANISOTROPY}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:ni}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return o.anisotropyStrength!==void 0&&(t.anisotropy=o.anisotropyStrength),o.anisotropyRotation!==void 0&&(t.anisotropyRotation=o.anisotropyRotation),o.anisotropyTexture!==void 0&&r.push(n.assignTexture(t,"anisotropyMap",o.anisotropyTexture)),Promise.all(r)}}class cM{constructor(e){this.parser=e,this.name=st.KHR_TEXTURE_BASISU}loadTexture(e){const t=this.parser,n=t.json,s=n.textures[e];if(!s.extensions||!s.extensions[this.name])return null;const r=s.extensions[this.name],o=t.options.ktx2Loader;if(!o){if(n.extensionsRequired&&n.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setKTX2Loader must be called before loading KTX2 textures");return null}return t.loadTextureImage(e,r.source,o)}}class lM{constructor(e){this.parser=e,this.name=st.EXT_TEXTURE_WEBP,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,s=n.json,r=s.textures[e];if(!r.extensions||!r.extensions[t])return null;const o=r.extensions[t],a=s.images[o.source];let c=n.textureLoader;if(a.uri){const l=n.options.manager.getHandler(a.uri);l!==null&&(c=l)}return this.detectSupport().then(function(l){if(l)return n.loadTextureImage(e,o.source,c);if(s.extensionsRequired&&s.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: WebP required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class uM{constructor(e){this.parser=e,this.name=st.EXT_TEXTURE_AVIF,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,s=n.json,r=s.textures[e];if(!r.extensions||!r.extensions[t])return null;const o=r.extensions[t],a=s.images[o.source];let c=n.textureLoader;if(a.uri){const l=n.options.manager.getHandler(a.uri);l!==null&&(c=l)}return this.detectSupport().then(function(l){if(l)return n.loadTextureImage(e,o.source,c);if(s.extensionsRequired&&s.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: AVIF required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAABcAAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAEAAAABAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQAMAAAAABNjb2xybmNseAACAAIABoAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAAB9tZGF0EgAKCBgABogQEDQgMgkQAAAAB8dSLfI=",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class hM{constructor(e){this.name=st.EXT_MESHOPT_COMPRESSION,this.parser=e}loadBufferView(e){const t=this.parser.json,n=t.bufferViews[e];if(n.extensions&&n.extensions[this.name]){const s=n.extensions[this.name],r=this.parser.getDependency("buffer",s.buffer),o=this.parser.options.meshoptDecoder;if(!o||!o.supported){if(t.extensionsRequired&&t.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files");return null}return r.then(function(a){const c=s.byteOffset||0,l=s.byteLength||0,u=s.count,h=s.byteStride,f=new Uint8Array(a,c,l);return o.decodeGltfBufferAsync?o.decodeGltfBufferAsync(u,h,f,s.mode,s.filter).then(function(d){return d.buffer}):o.ready.then(function(){const d=new ArrayBuffer(u*h);return o.decodeGltfBuffer(new Uint8Array(d),u,h,f,s.mode,s.filter),d})})}else return null}}class fM{constructor(e){this.name=st.EXT_MESH_GPU_INSTANCING,this.parser=e}createNodeMesh(e){const t=this.parser.json,n=t.nodes[e];if(!n.extensions||!n.extensions[this.name]||n.mesh===void 0)return null;const s=t.meshes[n.mesh];for(const l of s.primitives)if(l.mode!==Pn.TRIANGLES&&l.mode!==Pn.TRIANGLE_STRIP&&l.mode!==Pn.TRIANGLE_FAN&&l.mode!==void 0)return null;const o=n.extensions[this.name].attributes,a=[],c={};for(const l in o)a.push(this.parser.getDependency("accessor",o[l]).then(u=>(c[l]=u,c[l])));return a.length<1?null:(a.push(this.parser.createNodeMesh(e)),Promise.all(a).then(l=>{const u=l.pop(),h=u.isGroup?u.children:[u],f=l[0].count,d=[];for(const g of h){const _=new Le,p=new M,m=new On,v=new M(1,1,1),y=new Pv(g.geometry,g.material,f);for(let x=0;x<f;x++)c.TRANSLATION&&p.fromBufferAttribute(c.TRANSLATION,x),c.ROTATION&&m.fromBufferAttribute(c.ROTATION,x),c.SCALE&&v.fromBufferAttribute(c.SCALE,x),y.setMatrixAt(x,_.compose(p,m,v));for(const x in c)if(x==="_COLOR_0"){const P=c[x];y.instanceColor=new xl(P.array,P.itemSize,P.normalized)}else x!=="TRANSLATION"&&x!=="ROTATION"&&x!=="SCALE"&&g.geometry.setAttribute(x,c[x]);It.prototype.copy.call(y,g),this.parser.assignFinalMaterial(y),d.push(y)}return u.isGroup?(u.clear(),u.add(...d),u):d[0]}))}}const dd="glTF",Tr=12,qh={JSON:1313821514,BIN:5130562};class dM{constructor(e){this.name=st.KHR_BINARY_GLTF,this.content=null,this.body=null;const t=new DataView(e,0,Tr),n=new TextDecoder;if(this.header={magic:n.decode(new Uint8Array(e.slice(0,4))),version:t.getUint32(4,!0),length:t.getUint32(8,!0)},this.header.magic!==dd)throw new Error("THREE.GLTFLoader: Unsupported glTF-Binary header.");if(this.header.version<2)throw new Error("THREE.GLTFLoader: Legacy binary file detected.");const s=this.header.length-Tr,r=new DataView(e,Tr);let o=0;for(;o<s;){const a=r.getUint32(o,!0);o+=4;const c=r.getUint32(o,!0);if(o+=4,c===qh.JSON){const l=new Uint8Array(e,Tr+o,a);this.content=n.decode(l)}else if(c===qh.BIN){const l=Tr+o;this.body=e.slice(l,l+a)}o+=a}if(this.content===null)throw new Error("THREE.GLTFLoader: JSON content not found.")}}class pM{constructor(e,t){if(!t)throw new Error("THREE.GLTFLoader: No DRACOLoader instance provided.");this.name=st.KHR_DRACO_MESH_COMPRESSION,this.json=e,this.dracoLoader=t,this.dracoLoader.preload()}decodePrimitive(e,t){const n=this.json,s=this.dracoLoader,r=e.extensions[this.name].bufferView,o=e.extensions[this.name].attributes,a={},c={},l={};for(const u in o){const h=bl[u]||u.toLowerCase();a[h]=o[u]}for(const u in e.attributes){const h=bl[u]||u.toLowerCase();if(o[u]!==void 0){const f=n.accessors[e.attributes[u]],d=js[f.componentType];l[h]=d.name,c[h]=f.normalized===!0}}return t.getDependency("bufferView",r).then(function(u){return new Promise(function(h,f){s.decodeDracoFile(u,function(d){for(const g in d.attributes){const _=d.attributes[g],p=c[g];p!==void 0&&(_.normalized=p)}h(d)},a,l,an,f)})})}}class mM{constructor(){this.name=st.KHR_TEXTURE_TRANSFORM}extendTexture(e,t){return(t.texCoord===void 0||t.texCoord===e.channel)&&t.offset===void 0&&t.rotation===void 0&&t.scale===void 0||(e=e.clone(),t.texCoord!==void 0&&(e.channel=t.texCoord),t.offset!==void 0&&e.offset.fromArray(t.offset),t.rotation!==void 0&&(e.rotation=t.rotation),t.scale!==void 0&&e.repeat.fromArray(t.scale),e.needsUpdate=!0),e}}class gM{constructor(){this.name=st.KHR_MESH_QUANTIZATION}}class pd extends Qr{constructor(e,t,n,s){super(e,t,n,s)}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,s=this.valueSize,r=e*s*3+s;for(let o=0;o!==s;o++)t[o]=n[r+o];return t}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=a*2,l=a*3,u=s-t,h=(n-t)/u,f=h*h,d=f*h,g=e*l,_=g-l,p=-2*d+3*f,m=d-f,v=1-p,y=m-f+h;for(let x=0;x!==a;x++){const P=o[_+x+a],A=o[_+x+c]*u,E=o[g+x+a],R=o[g+x]*u;r[x]=v*P+y*A+p*E+m*R}return r}}const _M=new On;class xM extends pd{interpolate_(e,t,n,s){const r=super.interpolate_(e,t,n,s);return _M.fromArray(r).normalize().toArray(r),r}}const Pn={POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6},js={5120:Int8Array,5121:Uint8Array,5122:Int16Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},Yh={9728:dn,9729:Sn,9984:Sf,9985:qo,9986:Ir,9987:gi},jh={33071:Fi,33648:ta,10497:Qs},fc={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16},bl={POSITION:"position",NORMAL:"normal",TANGENT:"tangent",TEXCOORD_0:"uv",TEXCOORD_1:"uv1",TEXCOORD_2:"uv2",TEXCOORD_3:"uv3",COLOR_0:"color",WEIGHTS_0:"skinWeight",JOINTS_0:"skinIndex"},Ii={scale:"scale",translation:"position",rotation:"quaternion",weights:"morphTargetInfluences"},vM={CUBICSPLINE:void 0,LINEAR:Gr,STEP:Vr},dc={OPAQUE:"OPAQUE",MASK:"MASK",BLEND:"BLEND"};function yM(i){return i.DefaultMaterial===void 0&&(i.DefaultMaterial=new tu({color:16777215,emissive:0,metalness:1,roughness:1,transparent:!1,depthTest:!0,side:vi})),i.DefaultMaterial}function os(i,e,t){for(const n in t.extensions)i[n]===void 0&&(e.userData.gltfExtensions=e.userData.gltfExtensions||{},e.userData.gltfExtensions[n]=t.extensions[n])}function pi(i,e){e.extras!==void 0&&(typeof e.extras=="object"?Object.assign(i.userData,e.extras):console.warn("THREE.GLTFLoader: Ignoring primitive type .extras, "+e.extras))}function MM(i,e,t){let n=!1,s=!1,r=!1;for(let l=0,u=e.length;l<u;l++){const h=e[l];if(h.POSITION!==void 0&&(n=!0),h.NORMAL!==void 0&&(s=!0),h.COLOR_0!==void 0&&(r=!0),n&&s&&r)break}if(!n&&!s&&!r)return Promise.resolve(i);const o=[],a=[],c=[];for(let l=0,u=e.length;l<u;l++){const h=e[l];if(n){const f=h.POSITION!==void 0?t.getDependency("accessor",h.POSITION):i.attributes.position;o.push(f)}if(s){const f=h.NORMAL!==void 0?t.getDependency("accessor",h.NORMAL):i.attributes.normal;a.push(f)}if(r){const f=h.COLOR_0!==void 0?t.getDependency("accessor",h.COLOR_0):i.attributes.color;c.push(f)}}return Promise.all([Promise.all(o),Promise.all(a),Promise.all(c)]).then(function(l){const u=l[0],h=l[1],f=l[2];return n&&(i.morphAttributes.position=u),s&&(i.morphAttributes.normal=h),r&&(i.morphAttributes.color=f),i.morphTargetsRelative=!0,i})}function SM(i,e){if(i.updateMorphTargets(),e.weights!==void 0)for(let t=0,n=e.weights.length;t<n;t++)i.morphTargetInfluences[t]=e.weights[t];if(e.extras&&Array.isArray(e.extras.targetNames)){const t=e.extras.targetNames;if(i.morphTargetInfluences.length===t.length){i.morphTargetDictionary={};for(let n=0,s=t.length;n<s;n++)i.morphTargetDictionary[t[n]]=n}else console.warn("THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.")}}function bM(i){let e;const t=i.extensions&&i.extensions[st.KHR_DRACO_MESH_COMPRESSION];if(t?e="draco:"+t.bufferView+":"+t.indices+":"+pc(t.attributes):e=i.indices+":"+pc(i.attributes)+":"+i.mode,i.targets!==void 0)for(let n=0,s=i.targets.length;n<s;n++)e+=":"+pc(i.targets[n]);return e}function pc(i){let e="";const t=Object.keys(i).sort();for(let n=0,s=t.length;n<s;n++)e+=t[n]+":"+i[t[n]]+";";return e}function wl(i){switch(i){case Int8Array:return 1/127;case Uint8Array:return 1/255;case Int16Array:return 1/32767;case Uint16Array:return 1/65535;default:throw new Error("THREE.GLTFLoader: Unsupported normalized accessor component type.")}}function wM(i){return i.search(/\.jpe?g($|\?)/i)>0||i.search(/^data\:image\/jpeg/)===0?"image/jpeg":i.search(/\.webp($|\?)/i)>0||i.search(/^data\:image\/webp/)===0?"image/webp":i.search(/\.ktx2($|\?)/i)>0||i.search(/^data\:image\/ktx2/)===0?"image/ktx2":"image/png"}const EM=new Le;class TM{constructor(e={},t={}){this.json=e,this.extensions={},this.plugins={},this.options=t,this.cache=new jy,this.associations=new Map,this.primitiveCache={},this.nodeCache={},this.meshCache={refs:{},uses:{}},this.cameraCache={refs:{},uses:{}},this.lightCache={refs:{},uses:{}},this.sourceCache={},this.textureCache={},this.nodeNamesUsed={};let n=!1,s=-1,r=!1,o=-1;if(typeof navigator<"u"){const a=navigator.userAgent;n=/^((?!chrome|android).)*safari/i.test(a)===!0;const c=a.match(/Version\/(\d+)/);s=n&&c?parseInt(c[1],10):-1,r=a.indexOf("Firefox")>-1,o=r?a.match(/Firefox\/([0-9]+)\./)[1]:-1}typeof createImageBitmap>"u"||n&&s<17||r&&o<98?this.textureLoader=new My(this.options.manager):this.textureLoader=new Ry(this.options.manager),this.textureLoader.setCrossOrigin(this.options.crossOrigin),this.textureLoader.setRequestHeader(this.options.requestHeader),this.fileLoader=new oa(this.options.manager),this.fileLoader.setResponseType("arraybuffer"),this.options.crossOrigin==="use-credentials"&&this.fileLoader.setWithCredentials(!0)}setExtensions(e){this.extensions=e}setPlugins(e){this.plugins=e}parse(e,t){const n=this,s=this.json,r=this.extensions;this.cache.removeAll(),this.nodeCache={},this._invokeAll(function(o){return o._markDefs&&o._markDefs()}),Promise.all(this._invokeAll(function(o){return o.beforeRoot&&o.beforeRoot()})).then(function(){return Promise.all([n.getDependencies("scene"),n.getDependencies("animation"),n.getDependencies("camera")])}).then(function(o){const a={scene:o[0][s.scene||0],scenes:o[0],animations:o[1],cameras:o[2],asset:s.asset,parser:n,userData:{}};return os(r,a,s),pi(a,s),Promise.all(n._invokeAll(function(c){return c.afterRoot&&c.afterRoot(a)})).then(function(){for(const c of a.scenes)c.updateMatrixWorld();e(a)})}).catch(t)}_markDefs(){const e=this.json.nodes||[],t=this.json.skins||[],n=this.json.meshes||[];for(let s=0,r=t.length;s<r;s++){const o=t[s].joints;for(let a=0,c=o.length;a<c;a++)e[o[a]].isBone=!0}for(let s=0,r=e.length;s<r;s++){const o=e[s];o.mesh!==void 0&&(this._addNodeRef(this.meshCache,o.mesh),o.skin!==void 0&&(n[o.mesh].isSkinnedMesh=!0)),o.camera!==void 0&&this._addNodeRef(this.cameraCache,o.camera)}}_addNodeRef(e,t){t!==void 0&&(e.refs[t]===void 0&&(e.refs[t]=e.uses[t]=0),e.refs[t]++)}_getNodeRef(e,t,n){if(e.refs[t]<=1)return n;const s=n.clone(),r=(o,a)=>{const c=this.associations.get(o);c!=null&&this.associations.set(a,c);for(const[l,u]of o.children.entries())r(u,a.children[l])};return r(n,s),s.name+="_instance_"+e.uses[t]++,s}_invokeOne(e){const t=Object.values(this.plugins);t.push(this);for(let n=0;n<t.length;n++){const s=e(t[n]);if(s)return s}return null}_invokeAll(e){const t=Object.values(this.plugins);t.unshift(this);const n=[];for(let s=0;s<t.length;s++){const r=e(t[s]);r&&n.push(r)}return n}getDependency(e,t){const n=e+":"+t;let s=this.cache.get(n);if(!s){switch(e){case"scene":s=this.loadScene(t);break;case"node":s=this._invokeOne(function(r){return r.loadNode&&r.loadNode(t)});break;case"mesh":s=this._invokeOne(function(r){return r.loadMesh&&r.loadMesh(t)});break;case"accessor":s=this.loadAccessor(t);break;case"bufferView":s=this._invokeOne(function(r){return r.loadBufferView&&r.loadBufferView(t)});break;case"buffer":s=this.loadBuffer(t);break;case"material":s=this._invokeOne(function(r){return r.loadMaterial&&r.loadMaterial(t)});break;case"texture":s=this._invokeOne(function(r){return r.loadTexture&&r.loadTexture(t)});break;case"skin":s=this.loadSkin(t);break;case"animation":s=this._invokeOne(function(r){return r.loadAnimation&&r.loadAnimation(t)});break;case"camera":s=this.loadCamera(t);break;default:if(s=this._invokeOne(function(r){return r!=this&&r.getDependency&&r.getDependency(e,t)}),!s)throw new Error("Unknown type: "+e);break}this.cache.add(n,s)}return s}getDependencies(e){let t=this.cache.get(e);if(!t){const n=this,s=this.json[e+(e==="mesh"?"es":"s")]||[];t=Promise.all(s.map(function(r,o){return n.getDependency(e,o)})),this.cache.add(e,t)}return t}loadBuffer(e){const t=this.json.buffers[e],n=this.fileLoader;if(t.type&&t.type!=="arraybuffer")throw new Error("THREE.GLTFLoader: "+t.type+" buffer type is not supported.");if(t.uri===void 0&&e===0)return Promise.resolve(this.extensions[st.KHR_BINARY_GLTF].body);const s=this.options;return new Promise(function(r,o){n.load(kr.resolveURL(t.uri,s.path),r,void 0,function(){o(new Error('THREE.GLTFLoader: Failed to load buffer "'+t.uri+'".'))})})}loadBufferView(e){const t=this.json.bufferViews[e];return this.getDependency("buffer",t.buffer).then(function(n){const s=t.byteLength||0,r=t.byteOffset||0;return n.slice(r,r+s)})}loadAccessor(e){const t=this,n=this.json,s=this.json.accessors[e];if(s.bufferView===void 0&&s.sparse===void 0){const o=fc[s.type],a=js[s.componentType],c=s.normalized===!0,l=new a(s.count*o);return Promise.resolve(new $t(l,o,c))}const r=[];return s.bufferView!==void 0?r.push(this.getDependency("bufferView",s.bufferView)):r.push(null),s.sparse!==void 0&&(r.push(this.getDependency("bufferView",s.sparse.indices.bufferView)),r.push(this.getDependency("bufferView",s.sparse.values.bufferView))),Promise.all(r).then(function(o){const a=o[0],c=fc[s.type],l=js[s.componentType],u=l.BYTES_PER_ELEMENT,h=u*c,f=s.byteOffset||0,d=s.bufferView!==void 0?n.bufferViews[s.bufferView].byteStride:void 0,g=s.normalized===!0;let _,p;if(d&&d!==h){const m=Math.floor(f/d),v="InterleavedBuffer:"+s.bufferView+":"+s.componentType+":"+m+":"+s.count;let y=t.cache.get(v);y||(_=new l(a,m*d,s.count*d/u),y=new Tv(_,d/u),t.cache.add(v,y)),p=new Xl(y,c,f%d/u,g)}else a===null?_=new l(s.count*c):_=new l(a,f,s.count*c),p=new $t(_,c,g);if(s.sparse!==void 0){const m=fc.SCALAR,v=js[s.sparse.indices.componentType],y=s.sparse.indices.byteOffset||0,x=s.sparse.values.byteOffset||0,P=new v(o[1],y,s.sparse.count*m),A=new l(o[2],x,s.sparse.count*c);a!==null&&(p=new $t(p.array.slice(),p.itemSize,p.normalized)),p.normalized=!1;for(let E=0,R=P.length;E<R;E++){const b=P[E];if(p.setX(b,A[E*c]),c>=2&&p.setY(b,A[E*c+1]),c>=3&&p.setZ(b,A[E*c+2]),c>=4&&p.setW(b,A[E*c+3]),c>=5)throw new Error("THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.")}p.normalized=g}return p})}loadTexture(e){const t=this.json,n=this.options,r=t.textures[e].source,o=t.images[r];let a=this.textureLoader;if(o.uri){const c=n.manager.getHandler(o.uri);c!==null&&(a=c)}return this.loadTextureImage(e,r,a)}loadTextureImage(e,t,n){const s=this,r=this.json,o=r.textures[e],a=r.images[t],c=(a.uri||a.bufferView)+":"+o.sampler;if(this.textureCache[c])return this.textureCache[c];const l=this.loadImageSource(t,n).then(function(u){u.flipY=!1,u.name=o.name||a.name||"",u.name===""&&typeof a.uri=="string"&&a.uri.startsWith("data:image/")===!1&&(u.name=a.uri);const f=(r.samplers||{})[o.sampler]||{};return u.magFilter=Yh[f.magFilter]||Sn,u.minFilter=Yh[f.minFilter]||gi,u.wrapS=jh[f.wrapS]||Qs,u.wrapT=jh[f.wrapT]||Qs,u.generateMipmaps=!u.isCompressedTexture&&u.minFilter!==dn&&u.minFilter!==Sn,s.associations.set(u,{textures:e}),u}).catch(function(){return null});return this.textureCache[c]=l,l}loadImageSource(e,t){const n=this,s=this.json,r=this.options;if(this.sourceCache[e]!==void 0)return this.sourceCache[e].then(h=>h.clone());const o=s.images[e],a=self.URL||self.webkitURL;let c=o.uri||"",l=!1;if(o.bufferView!==void 0)c=n.getDependency("bufferView",o.bufferView).then(function(h){l=!0;const f=new Blob([h],{type:o.mimeType});return c=a.createObjectURL(f),c});else if(o.uri===void 0)throw new Error("THREE.GLTFLoader: Image "+e+" is missing URI and bufferView");const u=Promise.resolve(c).then(function(h){return new Promise(function(f,d){let g=f;t.isImageBitmapLoader===!0&&(g=function(_){const p=new jt(_);p.needsUpdate=!0,f(p)}),t.load(kr.resolveURL(h,r.path),g,void 0,d)})}).then(function(h){return l===!0&&a.revokeObjectURL(c),pi(h,o),h.userData.mimeType=o.mimeType||wM(o.uri),h}).catch(function(h){throw console.error("THREE.GLTFLoader: Couldn't load texture",c),h});return this.sourceCache[e]=u,u}assignTexture(e,t,n,s){const r=this;return this.getDependency("texture",n.index).then(function(o){if(!o)return null;if(n.texCoord!==void 0&&n.texCoord>0&&(o=o.clone(),o.channel=n.texCoord),r.extensions[st.KHR_TEXTURE_TRANSFORM]){const a=n.extensions!==void 0?n.extensions[st.KHR_TEXTURE_TRANSFORM]:void 0;if(a){const c=r.associations.get(o);o=r.extensions[st.KHR_TEXTURE_TRANSFORM].extendTexture(o,a),r.associations.set(o,c)}}return s!==void 0&&(o.colorSpace=s),e[t]=o,o})}assignFinalMaterial(e){const t=e.geometry;let n=e.material;const s=t.attributes.tangent===void 0,r=t.attributes.color!==void 0,o=t.attributes.normal===void 0;if(e.isPoints){const a="PointsMaterial:"+n.uuid;let c=this.cache.get(a);c||(c=new Qf,Kn.prototype.copy.call(c,n),c.color.copy(n.color),c.map=n.map,c.sizeAttenuation=!1,this.cache.add(a,c)),n=c}else if(e.isLine){const a="LineBasicMaterial:"+n.uuid;let c=this.cache.get(a);c||(c=new _s,Kn.prototype.copy.call(c,n),c.color.copy(n.color),c.map=n.map,this.cache.add(a,c)),n=c}if(s||r||o){let a="ClonedMaterial:"+n.uuid+":";s&&(a+="derivative-tangents:"),r&&(a+="vertex-colors:"),o&&(a+="flat-shading:");let c=this.cache.get(a);c||(c=n.clone(),r&&(c.vertexColors=!0),o&&(c.flatShading=!0),s&&(c.normalScale&&(c.normalScale.y*=-1),c.clearcoatNormalScale&&(c.clearcoatNormalScale.y*=-1)),this.cache.add(a,c),this.associations.set(c,this.associations.get(n))),n=c}e.material=n}getMaterialType(){return tu}loadMaterial(e){const t=this,n=this.json,s=this.extensions,r=n.materials[e];let o;const a={},c=r.extensions||{},l=[];if(c[st.KHR_MATERIALS_UNLIT]){const h=s[st.KHR_MATERIALS_UNLIT];o=h.getMaterialType(),l.push(h.extendParams(a,r,t))}else{const h=r.pbrMetallicRoughness||{};if(a.color=new ze(1,1,1),a.opacity=1,Array.isArray(h.baseColorFactor)){const f=h.baseColorFactor;a.color.setRGB(f[0],f[1],f[2],an),a.opacity=f[3]}h.baseColorTexture!==void 0&&l.push(t.assignTexture(a,"map",h.baseColorTexture,Ht)),a.metalness=h.metallicFactor!==void 0?h.metallicFactor:1,a.roughness=h.roughnessFactor!==void 0?h.roughnessFactor:1,h.metallicRoughnessTexture!==void 0&&(l.push(t.assignTexture(a,"metalnessMap",h.metallicRoughnessTexture)),l.push(t.assignTexture(a,"roughnessMap",h.metallicRoughnessTexture))),o=this._invokeOne(function(f){return f.getMaterialType&&f.getMaterialType(e)}),l.push(Promise.all(this._invokeAll(function(f){return f.extendMaterialParams&&f.extendMaterialParams(e,a)})))}r.doubleSided===!0&&(a.side=Mn);const u=r.alphaMode||dc.OPAQUE;if(u===dc.BLEND?(a.transparent=!0,a.depthWrite=!1):(a.transparent=!1,u===dc.MASK&&(a.alphaTest=r.alphaCutoff!==void 0?r.alphaCutoff:.5)),r.normalTexture!==void 0&&o!==on&&(l.push(t.assignTexture(a,"normalMap",r.normalTexture)),a.normalScale=new te(1,1),r.normalTexture.scale!==void 0)){const h=r.normalTexture.scale;a.normalScale.set(h,h)}if(r.occlusionTexture!==void 0&&o!==on&&(l.push(t.assignTexture(a,"aoMap",r.occlusionTexture)),r.occlusionTexture.strength!==void 0&&(a.aoMapIntensity=r.occlusionTexture.strength)),r.emissiveFactor!==void 0&&o!==on){const h=r.emissiveFactor;a.emissive=new ze().setRGB(h[0],h[1],h[2],an)}return r.emissiveTexture!==void 0&&o!==on&&l.push(t.assignTexture(a,"emissiveMap",r.emissiveTexture,Ht)),Promise.all(l).then(function(){const h=new o(a);return r.name&&(h.name=r.name),pi(h,r),t.associations.set(h,{materials:e}),r.extensions&&os(s,h,r),h})}createUniqueName(e){const t=yt.sanitizeNodeName(e||"");return t in this.nodeNamesUsed?t+"_"+ ++this.nodeNamesUsed[t]:(this.nodeNamesUsed[t]=0,t)}loadGeometries(e){const t=this,n=this.extensions,s=this.primitiveCache;function r(a){return n[st.KHR_DRACO_MESH_COMPRESSION].decodePrimitive(a,t).then(function(c){return $h(c,a,t)})}const o=[];for(let a=0,c=e.length;a<c;a++){const l=e[a],u=bM(l),h=s[u];if(h)o.push(h.promise);else{let f;l.extensions&&l.extensions[st.KHR_DRACO_MESH_COMPRESSION]?f=r(l):f=$h(new zt,l,t),s[u]={primitive:l,promise:f},o.push(f)}}return Promise.all(o)}loadMesh(e){const t=this,n=this.json,s=this.extensions,r=n.meshes[e],o=r.primitives,a=[];for(let c=0,l=o.length;c<l;c++){const u=o[c].material===void 0?yM(this.cache):this.getDependency("material",o[c].material);a.push(u)}return a.push(t.loadGeometries(o)),Promise.all(a).then(function(c){const l=c.slice(0,c.length-1),u=c[c.length-1],h=[];for(let d=0,g=u.length;d<g;d++){const _=u[d],p=o[d];let m;const v=l[d];if(p.mode===Pn.TRIANGLES||p.mode===Pn.TRIANGLE_STRIP||p.mode===Pn.TRIANGLE_FAN||p.mode===void 0)m=r.isSkinnedMesh===!0?new ql(_,v):new kt(_,v),m.isSkinnedMesh===!0&&m.normalizeSkinWeights(),p.mode===Pn.TRIANGLE_STRIP?m.geometry=Xh(m.geometry,If):p.mode===Pn.TRIANGLE_FAN&&(m.geometry=Xh(m.geometry,ml));else if(p.mode===Pn.LINES)m=new Kr(_,v);else if(p.mode===Pn.LINE_STRIP)m=new jl(_,v);else if(p.mode===Pn.LINE_LOOP)m=new Jf(_,v);else if(p.mode===Pn.POINTS)m=new Lv(_,v);else throw new Error("THREE.GLTFLoader: Primitive mode unsupported: "+p.mode);Object.keys(m.geometry.morphAttributes).length>0&&SM(m,r),m.name=t.createUniqueName(r.name||"mesh_"+e),pi(m,r),p.extensions&&os(s,m,p),t.assignFinalMaterial(m),h.push(m)}for(let d=0,g=h.length;d<g;d++)t.associations.set(h[d],{meshes:e,primitives:d});if(h.length===1)return r.extensions&&os(s,h[0],r),h[0];const f=new Bt;r.extensions&&os(s,f,r),t.associations.set(f,{meshes:e});for(let d=0,g=h.length;d<g;d++)f.add(h[d]);return f})}loadCamera(e){let t;const n=this.json.cameras[e],s=n[n.type];if(!s){console.warn("THREE.GLTFLoader: Missing camera parameters.");return}return n.type==="perspective"?t=new _n(Dn.radToDeg(s.yfov),s.aspectRatio||1,s.znear||1,s.zfar||2e6):n.type==="orthographic"&&(t=new pa(-s.xmag,s.xmag,s.ymag,-s.ymag,s.znear,s.zfar)),n.name&&(t.name=this.createUniqueName(n.name)),pi(t,n),Promise.resolve(t)}loadSkin(e){const t=this.json.skins[e],n=[];for(let s=0,r=t.joints.length;s<r;s++)n.push(this._loadNodeShallow(t.joints[s]));return t.inverseBindMatrices!==void 0?n.push(this.getDependency("accessor",t.inverseBindMatrices)):n.push(null),Promise.all(n).then(function(s){const r=s.pop(),o=s,a=[],c=[];for(let l=0,u=o.length;l<u;l++){const h=o[l];if(h){a.push(h);const f=new Le;r!==null&&f.fromArray(r.array,l*16),c.push(f)}else console.warn('THREE.GLTFLoader: Joint "%s" could not be found.',t.joints[l])}return new Yl(a,c)})}loadAnimation(e){const t=this.json,n=this,s=t.animations[e],r=s.name?s.name:"animation_"+e,o=[],a=[],c=[],l=[],u=[];for(let h=0,f=s.channels.length;h<f;h++){const d=s.channels[h],g=s.samplers[d.sampler],_=d.target,p=_.node,m=s.parameters!==void 0?s.parameters[g.input]:g.input,v=s.parameters!==void 0?s.parameters[g.output]:g.output;_.node!==void 0&&(o.push(this.getDependency("node",p)),a.push(this.getDependency("accessor",m)),c.push(this.getDependency("accessor",v)),l.push(g),u.push(_))}return Promise.all([Promise.all(o),Promise.all(a),Promise.all(c),Promise.all(l),Promise.all(u)]).then(function(h){const f=h[0],d=h[1],g=h[2],_=h[3],p=h[4],m=[];for(let v=0,y=f.length;v<y;v++){const x=f[v],P=d[v],A=g[v],E=_[v],R=p[v];if(x===void 0)continue;x.updateMatrix&&x.updateMatrix();const b=n._createAnimationTracks(x,P,A,E,R);if(b)for(let S=0;S<b.length;S++)m.push(b[S])}return new py(r,void 0,m)})}createNodeMesh(e){const t=this.json,n=this,s=t.nodes[e];return s.mesh===void 0?null:n.getDependency("mesh",s.mesh).then(function(r){const o=n._getNodeRef(n.meshCache,s.mesh,r);return s.weights!==void 0&&o.traverse(function(a){if(a.isMesh)for(let c=0,l=s.weights.length;c<l;c++)a.morphTargetInfluences[c]=s.weights[c]}),o})}loadNode(e){const t=this.json,n=this,s=t.nodes[e],r=n._loadNodeShallow(e),o=[],a=s.children||[];for(let l=0,u=a.length;l<u;l++)o.push(n.getDependency("node",a[l]));const c=s.skin===void 0?Promise.resolve(null):n.getDependency("skin",s.skin);return Promise.all([r,Promise.all(o),c]).then(function(l){const u=l[0],h=l[1],f=l[2];f!==null&&u.traverse(function(d){d.isSkinnedMesh&&d.bind(f,EM)});for(let d=0,g=h.length;d<g;d++)u.add(h[d]);return u})}_loadNodeShallow(e){const t=this.json,n=this.extensions,s=this;if(this.nodeCache[e]!==void 0)return this.nodeCache[e];const r=t.nodes[e],o=r.name?s.createUniqueName(r.name):"",a=[],c=s._invokeOne(function(l){return l.createNodeMesh&&l.createNodeMesh(e)});return c&&a.push(c),r.camera!==void 0&&a.push(s.getDependency("camera",r.camera).then(function(l){return s._getNodeRef(s.cameraCache,r.camera,l)})),s._invokeAll(function(l){return l.createNodeAttachment&&l.createNodeAttachment(e)}).forEach(function(l){a.push(l)}),this.nodeCache[e]=Promise.all(a).then(function(l){let u;if(r.isBone===!0?u=new Kf:l.length>1?u=new Bt:l.length===1?u=l[0]:u=new It,u!==l[0])for(let h=0,f=l.length;h<f;h++)u.add(l[h]);if(r.name&&(u.userData.name=r.name,u.name=o),pi(u,r),r.extensions&&os(n,u,r),r.matrix!==void 0){const h=new Le;h.fromArray(r.matrix),u.applyMatrix4(h)}else r.translation!==void 0&&u.position.fromArray(r.translation),r.rotation!==void 0&&u.quaternion.fromArray(r.rotation),r.scale!==void 0&&u.scale.fromArray(r.scale);return s.associations.has(u)||s.associations.set(u,{}),s.associations.get(u).nodes=e,u}),this.nodeCache[e]}loadScene(e){const t=this.extensions,n=this.json.scenes[e],s=this,r=new Bt;n.name&&(r.name=s.createUniqueName(n.name)),pi(r,n),n.extensions&&os(t,r,n);const o=n.nodes||[],a=[];for(let c=0,l=o.length;c<l;c++)a.push(s.getDependency("node",o[c]));return Promise.all(a).then(function(c){for(let u=0,h=c.length;u<h;u++)r.add(c[u]);const l=u=>{const h=new Map;for(const[f,d]of s.associations)(f instanceof Kn||f instanceof jt)&&h.set(f,d);return u.traverse(f=>{const d=s.associations.get(f);d!=null&&h.set(f,d)}),h};return s.associations=l(r),r})}_createAnimationTracks(e,t,n,s,r){const o=[],a=e.name?e.name:e.uuid,c=[];Ii[r.path]===Ii.weights?e.traverse(function(f){f.morphTargetInfluences&&c.push(f.name?f.name:f.uuid)}):c.push(a);let l;switch(Ii[r.path]){case Ii.weights:l=rr;break;case Ii.rotation:l=or;break;case Ii.position:case Ii.scale:l=ar;break;default:switch(n.itemSize){case 1:l=rr;break;case 2:case 3:default:l=ar;break}break}const u=s.interpolation!==void 0?vM[s.interpolation]:Gr,h=this._getArrayFromAccessor(n);for(let f=0,d=c.length;f<d;f++){const g=new l(c[f]+"."+Ii[r.path],t.array,h,u);s.interpolation==="CUBICSPLINE"&&this._createCubicSplineTrackInterpolant(g),o.push(g)}return o}_getArrayFromAccessor(e){let t=e.array;if(e.normalized){const n=wl(t.constructor),s=new Float32Array(t.length);for(let r=0,o=t.length;r<o;r++)s[r]=t[r]*n;t=s}return t}_createCubicSplineTrackInterpolant(e){e.createInterpolant=function(n){const s=this instanceof or?xM:pd;return new s(this.times,this.values,this.getValueSize()/3,n)},e.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline=!0}}function AM(i,e,t){const n=e.attributes,s=new pn;if(n.POSITION!==void 0){const a=t.json.accessors[n.POSITION],c=a.min,l=a.max;if(c!==void 0&&l!==void 0){if(s.set(new M(c[0],c[1],c[2]),new M(l[0],l[1],l[2])),a.normalized){const u=wl(js[a.componentType]);s.min.multiplyScalar(u),s.max.multiplyScalar(u)}}else{console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.");return}}else return;const r=e.targets;if(r!==void 0){const a=new M,c=new M;for(let l=0,u=r.length;l<u;l++){const h=r[l];if(h.POSITION!==void 0){const f=t.json.accessors[h.POSITION],d=f.min,g=f.max;if(d!==void 0&&g!==void 0){if(c.setX(Math.max(Math.abs(d[0]),Math.abs(g[0]))),c.setY(Math.max(Math.abs(d[1]),Math.abs(g[1]))),c.setZ(Math.max(Math.abs(d[2]),Math.abs(g[2]))),f.normalized){const _=wl(js[f.componentType]);c.multiplyScalar(_)}a.max(c)}else console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.")}}s.expandByVector(a)}i.boundingBox=s;const o=new ei;s.getCenter(o.center),o.radius=s.min.distanceTo(s.max)/2,i.boundingSphere=o}function $h(i,e,t){const n=e.attributes,s=[];function r(o,a){return t.getDependency("accessor",o).then(function(c){i.setAttribute(a,c)})}for(const o in n){const a=bl[o]||o.toLowerCase();a in i.attributes||s.push(r(n[o],a))}if(e.indices!==void 0&&!i.index){const o=t.getDependency("accessor",e.indices).then(function(a){i.setIndex(a)});s.push(o)}return at.workingColorSpace!==an&&"COLOR_0"in n&&console.warn(`THREE.GLTFLoader: Converting vertex colors from "srgb-linear" to "${at.workingColorSpace}" not supported.`),pi(i,e),AM(i,e,t),Promise.all(s).then(function(){return e.targets!==void 0?MM(i,e.targets,t):i})}const mc=new WeakMap;class RM extends ys{constructor(e){super(e),this.decoderPath="",this.decoderConfig={},this.decoderBinary=null,this.decoderPending=null,this.workerLimit=4,this.workerPool=[],this.workerNextTaskID=1,this.workerSourceURL="",this.defaultAttributeIDs={position:"POSITION",normal:"NORMAL",color:"COLOR",uv:"TEX_COORD"},this.defaultAttributeTypes={position:"Float32Array",normal:"Float32Array",color:"Float32Array",uv:"Float32Array"}}setDecoderPath(e){return this.decoderPath=e,this}setDecoderConfig(e){return this.decoderConfig=e,this}setWorkerLimit(e){return this.workerLimit=e,this}load(e,t,n,s){const r=new oa(this.manager);r.setPath(this.path),r.setResponseType("arraybuffer"),r.setRequestHeader(this.requestHeader),r.setWithCredentials(this.withCredentials),r.load(e,o=>{this.parse(o,t,s)},n,s)}parse(e,t,n=()=>{}){this.decodeDracoFile(e,t,null,null,Ht,n).catch(n)}decodeDracoFile(e,t,n,s,r=an,o=()=>{}){const a={attributeIDs:n||this.defaultAttributeIDs,attributeTypes:s||this.defaultAttributeTypes,useUniqueIDs:!!n,vertexColorSpace:r};return this.decodeGeometry(e,a).then(t).catch(o)}decodeGeometry(e,t){const n=JSON.stringify(t);if(mc.has(e)){const c=mc.get(e);if(c.key===n)return c.promise;if(e.byteLength===0)throw new Error("THREE.DRACOLoader: Unable to re-decode a buffer with different settings. Buffer has already been transferred.")}let s;const r=this.workerNextTaskID++,o=e.byteLength,a=this._getWorker(r,o).then(c=>(s=c,new Promise((l,u)=>{s._callbacks[r]={resolve:l,reject:u},s.postMessage({type:"decode",id:r,taskConfig:t,buffer:e},[e])}))).then(c=>this._createGeometry(c.geometry));return a.catch(()=>!0).then(()=>{s&&r&&this._releaseTask(s,r)}),mc.set(e,{key:n,promise:a}),a}_createGeometry(e){const t=new zt;e.index&&t.setIndex(new $t(e.index.array,1));for(let n=0;n<e.attributes.length;n++){const s=e.attributes[n],r=s.name,o=s.array,a=s.itemSize,c=new $t(o,a);r==="color"&&(this._assignVertexColorSpace(c,s.vertexColorSpace),c.normalized=!(o instanceof Float32Array)),t.setAttribute(r,c)}return t}_assignVertexColorSpace(e,t){if(t!==Ht)return;const n=new ze;for(let s=0,r=e.count;s<r;s++)n.fromBufferAttribute(e,s),at.toWorkingColorSpace(n,Ht),e.setXYZ(s,n.r,n.g,n.b)}_loadLibrary(e,t){const n=new oa(this.manager);return n.setPath(this.decoderPath),n.setResponseType(t),n.setWithCredentials(this.withCredentials),new Promise((s,r)=>{n.load(e,s,void 0,r)})}preload(){return this._initDecoder(),this}_initDecoder(){if(this.decoderPending)return this.decoderPending;const e=typeof WebAssembly!="object"||this.decoderConfig.type==="js",t=[];return e?t.push(this._loadLibrary("draco_decoder.js","text")):(t.push(this._loadLibrary("draco_wasm_wrapper.js","text")),t.push(this._loadLibrary("draco_decoder.wasm","arraybuffer"))),this.decoderPending=Promise.all(t).then(n=>{const s=n[0];e||(this.decoderConfig.wasmBinary=n[1]);const r=CM.toString(),o=["/* draco decoder */",s,"","/* worker */",r.substring(r.indexOf("{")+1,r.lastIndexOf("}"))].join(`
`);this.workerSourceURL=URL.createObjectURL(new Blob([o]))}),this.decoderPending}_getWorker(e,t){return this._initDecoder().then(()=>{if(this.workerPool.length<this.workerLimit){const s=new Worker(this.workerSourceURL);s._callbacks={},s._taskCosts={},s._taskLoad=0,s.postMessage({type:"init",decoderConfig:this.decoderConfig}),s.onmessage=function(r){const o=r.data;switch(o.type){case"decode":s._callbacks[o.id].resolve(o);break;case"error":s._callbacks[o.id].reject(o);break;default:console.error('THREE.DRACOLoader: Unexpected message, "'+o.type+'"')}},this.workerPool.push(s)}else this.workerPool.sort(function(s,r){return s._taskLoad>r._taskLoad?-1:1});const n=this.workerPool[this.workerPool.length-1];return n._taskCosts[e]=t,n._taskLoad+=t,n})}_releaseTask(e,t){e._taskLoad-=e._taskCosts[t],delete e._callbacks[t],delete e._taskCosts[t]}debug(){console.log("Task load: ",this.workerPool.map(e=>e._taskLoad))}dispose(){for(let e=0;e<this.workerPool.length;++e)this.workerPool[e].terminate();return this.workerPool.length=0,this.workerSourceURL!==""&&URL.revokeObjectURL(this.workerSourceURL),this}}function CM(){let i,e;onmessage=function(o){const a=o.data;switch(a.type){case"init":i=a.decoderConfig,e=new Promise(function(u){i.onModuleLoaded=function(h){u({draco:h})},DracoDecoderModule(i)});break;case"decode":const c=a.buffer,l=a.taskConfig;e.then(u=>{const h=u.draco,f=new h.Decoder;try{const d=t(h,f,new Int8Array(c),l),g=d.attributes.map(_=>_.array.buffer);d.index&&g.push(d.index.array.buffer),self.postMessage({type:"decode",id:a.id,geometry:d},g)}catch(d){console.error(d),self.postMessage({type:"error",id:a.id,error:d.message})}finally{h.destroy(f)}});break}};function t(o,a,c,l){const u=l.attributeIDs,h=l.attributeTypes;let f,d;const g=a.GetEncodedGeometryType(c);if(g===o.TRIANGULAR_MESH)f=new o.Mesh,d=a.DecodeArrayToMesh(c,c.byteLength,f);else if(g===o.POINT_CLOUD)f=new o.PointCloud,d=a.DecodeArrayToPointCloud(c,c.byteLength,f);else throw new Error("THREE.DRACOLoader: Unexpected geometry type.");if(!d.ok()||f.ptr===0)throw new Error("THREE.DRACOLoader: Decoding failed: "+d.error_msg());const _={index:null,attributes:[]};for(const p in u){const m=self[h[p]];let v,y;if(l.useUniqueIDs)y=u[p],v=a.GetAttributeByUniqueId(f,y);else{if(y=a.GetAttributeId(f,o[u[p]]),y===-1)continue;v=a.GetAttribute(f,y)}const x=s(o,a,f,p,m,v);p==="color"&&(x.vertexColorSpace=l.vertexColorSpace),_.attributes.push(x)}return g===o.TRIANGULAR_MESH&&(_.index=n(o,a,f)),o.destroy(f),_}function n(o,a,c){const u=c.num_faces()*3,h=u*4,f=o._malloc(h);a.GetTrianglesUInt32Array(c,h,f);const d=new Uint32Array(o.HEAPF32.buffer,f,u).slice();return o._free(f),{array:d,itemSize:1}}function s(o,a,c,l,u,h){const f=h.num_components(),g=c.num_points()*f,_=g*u.BYTES_PER_ELEMENT,p=r(o,u),m=o._malloc(_);a.GetAttributeDataArrayForAllPoints(c,h,p,_,m);const v=new u(o.HEAPF32.buffer,m,g).slice();return o._free(m),{name:l,array:v,itemSize:f}}function r(o,a){switch(a){case Float32Array:return o.DT_FLOAT32;case Int8Array:return o.DT_INT8;case Int16Array:return o.DT_INT16;case Int32Array:return o.DT_INT32;case Uint8Array:return o.DT_UINT8;case Uint16Array:return o.DT_UINT16;case Uint32Array:return o.DT_UINT32}}}const PM=224,Qn=5.4,jr=2.4,gc=8,Kh=3,LM="https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/libs/draco/gltf/",BE=(Qn/2-jr)/Qn,fi=2,IM=.5,DM=new M(-.35,-.8,.5),NM=.6,El=new M(.6,.6,.7),UM=new M(.02,.02,.05),OM=.036,Y={l:1,r:-1},vs=65,va=25,FM=25,BM=-6,Zh=95,kM=30,zM=20,md=40,gd=25,_d=10,_c=[.4,-.92,2.1],xd=[.6,.3,-1],HM=4,zr=18,VM=new Set(["butler_tray"]),xc="butler_tablet",vc="butler_towel",vd=new Set(["colleague_mug"]),ya=new Set([...vd,"squire_shield","coach_clipboard"]),Et=new Set([...ya,"squire_quill"]),Tl=.06,GM={forearm:new M(0,0,-1),shin:new M(1,0,0)},dr=new Le().set(1,0,0,0,0,0,1,0,0,-1,0,0,0,0,0,1),Ma=dr.clone().invert(),aa=i=>i.clone().applyMatrix4(Ma),ki=i=>new Le().makeTranslation(i.x,i.y,i.z),Nt=Dn.degToRad,Gs=(i,e,t)=>new Le().makeRotationFromEuler(new wn(Nt(i),Nt(e),Nt(t),"ZYX"));function as(i,e){return ki(i).multiply(e).multiply(ki(i.clone().negate()))}function WM(i){const e=i.match(/^(.*)_([lr])$/);return e?{base:e[1],side:e[2]}:{base:i,side:""}}function XM(i,e){const{x:t,y:n,z:s}=GM[i];return e==="l"?new M(t,n,s):new M(t,-n,-s)}class qM{constructor(e,t="stand",n=0){this.rig=e,this.final=new Map,this.eyes=1,this.eyeShape=null,this.eyeShift=[0,0],this.bulbLit=0,this.eyeTint=null,this.hearts=0,this.stars=0,this.squeezed=0,this.laptop=!1,this.tablet=!1,this.cloth=!1,this.book=null,this.props=new Map,this.stowed=new Set,this.keep=new Set,this.tap=0,this.gaze=null,this.posture=t,this.sway=0,this.stride=n,this.sky=null,this.screen=null}standing(e){const t=this.rig.parents.get(e);return t?this.matrix(t):new Le}matrix(e){return this.final.get(e)??this.standing(e)}head(e,t){return this.rig.heads.get(e).clone().applyMatrix4(t)}turn(e,{x:t=0,y:n=0,z:s=0}){const r=this.matrix(e);this.final.set(e,as(this.head(e,r),Gs(t,n,s)).multiply(r))}face(e,{x:t=0,y:n=0,z:s=0}){const r=this.head(e,this.standing(e)),o=this.rig.heads.get(e).clone().negate();this.final.set(e,ki(r).multiply(Gs(t,n,s)).multiply(ki(o)))}lift(e,{x:t=0,y:n=0,z:s=0}){this.final.set(e,ki(new M(t,n,s)).multiply(this.matrix(e)))}bend(e,t){const{base:n,side:s}=WM(e),r=this.standing(e),o=XM(n,s).transformDirection(r).normalize(),a=new Le().makeRotationAxis(o,Nt(t));this.final.set(e,as(this.head(e,r),a).multiply(r))}aim(e,t){const n=this.standing(e),s=this.rig.along.get(e).clone().transformDirection(n),r=new Le().makeRotationFromQuaternion(new On().setFromUnitVectors(s,t.clone().normalize()));this.final.set(e,as(this.head(e,n),r).multiply(n))}reach(e,t,n){this.limbTo(e,["upper_arm","forearm","hand"],t,n)}withinReach(e,t,n){const[s,r,o]=["upper_arm","forearm","hand"].map(u=>this.rig.heads.get(`${u}_${e}`)),a=(r.distanceTo(s)+o.distanceTo(r))*n,c=this.head(`upper_arm_${e}`,this.standing(`upper_arm_${e}`)),l=t.clone().sub(c);return l.length()<=a?t:c.clone().add(l.setLength(a))}step(e,t,n){this.limbTo(e,["thigh","shin","foot"],t,n)}limbTo(e,t,n,s){const[r,o,a]=t.map(m=>`${m}_${e}`),c=this.rig.heads.get(o).distanceTo(this.rig.heads.get(r)),l=this.rig.heads.get(a).distanceTo(this.rig.heads.get(o)),u=this.head(r,this.standing(r)),h=n.clone().sub(u),f=h.length();if(f<Math.abs(c-l)||f>c+l)throw new Error(`the ${r} cannot reach ${f.toFixed(3)}`);const d=h.clone().normalize(),g=(c*c-l*l+f*f)/(2*f),_=s.clone();e==="r"&&(_.x=-_.x),_.sub(d.clone().multiplyScalar(_.dot(d)));const p=u.clone().add(d.multiplyScalar(g)).add(_.normalize().multiplyScalar(Math.sqrt(Math.max(c*c-g*g,0))));this.aim(r,p.clone().sub(u)),this.aim(o,n.clone().sub(p))}turnAll({x:e=0,y:t=0,z:n=0},s=new M){const r=as(s,Gs(e,t,n));this.final=new Map(this.rig.order.map(o=>[o,r.clone().multiply(this.matrix(o))]))}revolve(e){this.turnAll({z:e})}bendAbove(e,{x:t=0,y:n=0,z:s=0}){const r=as(this.head(e,this.matrix(e)),Gs(t,n,s)),o=a=>a===e||!!a&&o(this.rig.parents.get(a));this.final=new Map(this.rig.order.map(a=>[a,o(a)?r.clone().multiply(this.matrix(a)):this.matrix(a)]))}shiftAll(e){const t=ki(new M(...e));this.final=new Map(this.rig.order.map(n=>[n,t.clone().multiply(this.matrix(n))]))}carried(e){return e.clone().add(this.head("root",this.matrix("root")).sub(this.rig.heads.get("root")))}swing(e){this.sway=e}shutEyes(e){this.eyes=Math.max(e,Tl)}glanceEyes(e,t){this.eyeShift=[t,e]}shapeEyes(e,t=1,n=1){this.eyeShape=t>0?{name:e,strength:t,way:n}:null}tintEyes(e){this.eyeTint=e}heartEyes(e){this.hearts=e}starEyes(e){this.stars=e}squeezeEyes(e){this.squeezed=e}holdLaptop(){this.laptop=!0}holdTablet(){this.tablet=!0}holdCloth(){this.cloth=!0}holdBook(e,t,n){this.book={open:e,page:t,visible:n}}holdProp(e,t,n=[0,0,0],s={}){this.props.set(e,{bone:`hand_${t}`,frame:`hand_${t}`,at:this.grip(t,n),turn:s})}holdUpright(e,t,n=[0,0,0],s={}){this.props.set(e,{bone:`hand_${t}`,frame:"root",at:this.grip(t,n),turn:s})}standProp(e,t,n={}){this.props.set(e,{bone:"root",frame:"root",at:new M(...t),turn:n})}lightBulb(e,t,n){const[s,r,o]=$s.at;this.standProp("light_bulb",[n*s,r,o]),Object.assign(this.props.get("light_bulb"),{size:e,lit:t}),this.bulbLit=t}wearProp(e,t,n={}){this.props.set(e,{bone:"head",frame:"head",at:this.rig.heads.get("head").clone().add(new M(...t)),turn:n})}roll(e,t){const n=this.matrix(e),s=this.rig.along.get(e).clone().transformDirection(n).normalize();this.final.set(e,as(this.head(e,n),new Le().makeRotationAxis(s,Nt(t))).multiply(n))}clench(e,t){const n=`hand_${e}`,s=this.rig.heads.get(n),r=this.rig.along.get(n).clone().normalize(),o=new Le().set(1+(t-1)*r.x*r.x,(t-1)*r.x*r.y,(t-1)*r.x*r.z,0,(t-1)*r.y*r.x,1+(t-1)*r.y*r.y,(t-1)*r.y*r.z,0,(t-1)*r.z*r.x,(t-1)*r.z*r.y,1+(t-1)*r.z*r.z,0,0,0,0,1);this.final.set(n,this.matrix(n).clone().multiply(as(s,o)))}grip(e,t){return this.rig.heads.get(`hand_${e}`).clone().add(new M(Y[e]*(ji.grip+t[0]),ji.forward+t[1],t[2]))}putAway(...e){e.forEach(t=>this.stowed.add(t))}moves(e){const t=new Le().makeRotationZ(Nt(e)),n=new Map;for(const s of this.rig.order){const r=this.rig.parents.get(s);n.set(s,this.final.get(s)??(r?n.get(r):new Le))}return new Map([...n].map(([s,r])=>[s,t.clone().multiply(r)]))}}const Re=(i,e=1)=>Math.sin(2*Math.PI*e*i);function pe(i,e,t=1){i.turn("spine",{x:1*t*Re(e)}),i.turn("chest",{x:1.5*t*Re(e-.05)}),i.turn("neck",{x:-.8*t*Re(e-.1)}),i.turn("head",{x:-1.2*t*Re(e-.12)})}function oe(i,{lean:e=0,twist:t=0,nod:n=0,turn:s=0,tilt:r=0}){i.turn("spine",{x:e*.4,z:t*.4}),i.turn("chest",{x:e*.6,z:t*.6}),i.turn("neck",{x:n*.3,z:s*.3,y:r*.3}),i.turn("head",{x:n*.7,z:s*.7,y:r*.7})}function yd(i,e,t=0,n=10){i.turn(`upper_arm_${e}`,{y:Y[e]*vs}),i.turn(`upper_arm_${e}`,{x:t}),i.bend(`forearm_${e}`,n)}function YM(i,e,t=BM,n=0,s=0){const r=Y[e];i.turn(`upper_arm_${e}`,{y:r*vs}),i.turn(`upper_arm_${e}`,{x:-n}),i.turn(`upper_arm_${e}`,{z:r*zM}),i.face(`forearm_${e}`,{y:-r*t,z:-r*Zh}),i.face(`hand_${e}`,{x:s,z:-r*(Zh-kM)})}function Ae(i,e,t=[],n={},s=e.level){var r;for(const o of Object.keys(Y))if(!t.includes(o)){if(s.has(o)){YM(i,o);continue}yd(i,o,n[o]??0),(r=e.shield)!=null&&r.has(o)&&i.turn(`hand_${o}`,{y:-Y[o]*NS,z:Y[o]*DS})}}const Je=i=>i.busy.has("r")?"l":"r";function Sa(i,e,t){pe(i,t),Ae(i,e),i.swing(Re(t))}function jM(i,e,t){const n=Math.max(Re(t,2),0);oe(i,{lean:4*n,nod:26*n}),Ae(i,e)}const Ar={at:[0,-.62,1.95],apart:.07,circle:.13,nod:8};function $M(i,e,t){const n=ce.hand_rub,s=Ut(t,n.frames),r=Te(s,n.together)*(1-Te(s,n.apart)),o=2*Math.PI*n.rubs*lt(s,n.together[1],n.apart[0]);pe(i,0),oe(i,{lean:4*r,nod:Ar.nod*r*(.5+.5*Math.sin(2*o))}),i.putAway(...Et),Ae(i,e,r?Object.keys(Y):[]);const[a,c,l]=Ar.at;for(const[u,h]of Object.entries(Y)){const f=new M(a+h*(Ar.apart+Ar.circle*Math.cos(o)),c,l+h*Ar.circle*Math.sin(o));r&&_t(i,u,r,i.withinReach(u,i.carried(f),.97),new M(...z.elbow))}Ke(i,"amused",r)}function KM(i,e,t){oe(i,{turn:28*Re(t,2),tilt:4*Re(t,2)}),Ae(i,e)}function ZM(i,e,t){const n=Je(e),s=Y[n];oe(i,{twist:-s*4,turn:-s*8,tilt:-s*6}),Ae(i,e,[n]),Md(i,n,t)}function Md(i,e,t){i.turn(`upper_arm_${e}`,{x:-85}),i.turn(`upper_arm_${e}`,{z:Y[e]*md}),i.bend(`forearm_${e}`,gd+_d*Re(t))}const rn={tilt:22,nod:-12,sway:4,cheek:[.38,-.78,2.6],finger:[.2,.15,1],elbow:[.1,-.5,-1],inboard:.1,under:.12,folded:[1,-.6,-.4],glance:[.35,.3],gotIt:[.85,-.45,2.75]};function JM(i,e,t,n,s,r){_t(i,e,t,n.clone().addScaledVector(s,-ji.grip),r),i.aim(`hand_${e}`,new M(0,0,-1).lerp(s,t).normalize())}function QM(i,e,t,n){const s=i.head(`forearm_${t}`,i.matrix(`forearm_${t}`)),r=new M(s.x*rn.inboard,s.y,s.z-rn.under);_t(i,e,n,i.withinReach(e,r,.97),new M(...rn.folded))}function eS(i,e,t,{thinking:n,sway:s,got:r,raised:o}){const a=Je(e),c=a==="l"?"r":"l",l=Y[a];pe(i,t),oe(i,{nod:rn.nod*n-10*r,tilt:-l*(rn.tilt*n+rn.sway*s),turn:3*s}),i.putAway(...Et),Ae(i,e,[...n+r?[a]:[],...n?[c]:[]]),n+r&&Sd(i,a,Math.max(n,r),o),n&&QM(i,c,a,n),i.glanceEyes(rn.glance[0]*n,-l*rn.glance[1]*n),Ke(i,"startled",r)}function Sd(i,e,t,n=0){const s=Y[e],[r,o,a]=rn.cheek,c=new M(s*r,o,a).applyMatrix4(i.matrix("head")),[l,u,h]=rn.gotIt,f=i.carried(new M(s*l,u,h+ji.grip)),[d,g,_]=rn.finger;JM(i,e,t,c.lerp(f,n),new M(-s*d,g,_).normalize(),new M(...rn.elbow))}const yc=i=>(e,t,n)=>{const s=Ut(n,i.frames),r=i.cloud?Te(s,i.into)*(1-Te(s,i.rise)):0,o=!!i.lights,a=o?Te(s,i.rise)*(1-Te(s,i.fades)):0;eS(e,t,n,{thinking:r,sway:(i.sways?Math.sin(2*Math.PI*i.sways*s):0)*r,got:a,raised:o?Te(s,i.rise):0}),o&&s>=i.appears[0]&&e.lightBulb(Te(s,i.appears)*(1-Te(s,i.goes)),Te(s,i.lights)*(1-Te(s,i.fades)),Y[Je(t)])};function tS(i,e,t){const n=Math.max(Math.sin(2*Math.PI*2*t),0);i.lift("root",{z:.28*n}),i.turn("hips",{z:6*Re(t,2)}),oe(i,{lean:-5,turn:-6*Re(t,2)});const s=Object.keys(Y).filter(r=>!e.busy.has(r));Ae(i,e,s);for(const r of s)Y[r],Kt(i,r,1,{y:-va,bend:10+6*Re(t,4)});for(const r of Object.keys(Y))i.turn(`thigh_${r}`,{x:-18*n}),i.turn(`shin_${r}`,{x:34*n}),i.turn(`foot_${r}`,{x:-10*n})}function nS(i,e,t){const n=t*(z.yawnFrames+zr);if(n<z.yawnFrames)return Fd(i,e,n/z.yawnFrames);const s=Re((n-z.yawnFrames)/zr);oe(i,{lean:4+1.5*s,nod:8+2*s,tilt:Y[Je(e)]*HM}),Ae(i,e),i.shutEyes(0)}function iS(i,e,t){i.stride=t;const n=2*Math.PI*t;bd(i),i.turn("hips",{z:5*Math.sin(n)}),oe(i,{lean:3,twist:-7*Math.sin(n),turn:3*Math.sin(n)}),Ae(i,e,[],{l:22*Math.sin(n),r:-22*Math.sin(n)}),wd(i)}function bd(i){i.lift("root",{z:.05*Math.cos(4*Math.PI*i.stride)})}function wd(i){for(const[e,t]of[["l",0],["r",Math.PI]]){const n=2*Math.PI*i.stride+t,s=-30*Math.sin(n),r=42*Math.max(Math.cos(n),0);i.turn(`thigh_${e}`,{x:s}),i.turn(`shin_${e}`,{x:r}),i.turn(`foot_${e}`,{x:-.8*(s+r)+6})}}const ca=4.4,Ed=.72,Td=.94,ou=[1.84,.38,.2],au=[1.36,.6,.16],Jh=.14,sS=.2,rS=66,oS=1.25,aS=2.91,Mc={back:.58,up:.36,rise:.38},cS=new M(1,-1,-1);function Si(i){return i=Math.min(Math.max(i,0),1),i*i*(3-2*i)}function Ut(i,e){return Math.min(Math.max(i*e/(e-1),0),1)}const lt=(i,e,t)=>Math.min(Math.max((i-e)/(t-e),0),1),ne=(i,e,t)=>Si(lt(i,e,t)),Ve=(i,e,t)=>Math.sin(Math.PI*lt(i,e,t)),Vt=(i,e,t)=>i+(e-i)*t,Qh=(i,e,t)=>Math.exp(-t*i)*Math.sin(2*Math.PI*e*i)*(1-i);function lS(i,e){return i!=="pull_ups"||!(e.busy.size||e.level.size)}function Sc(i){i.lift("root",{z:sS}),i.putAway(...un.satOn)}const Ni={lean:-24,feet:18,hands:[.62,.5],floor:1.4};function uS(i){for(const e of Object.keys(Y))i.turn(`thigh_${e}`,{x:-88}),i.turn(`foot_${e}`,{x:Ni.feet});oe(i,{lean:Ni.lean,nod:-Ni.lean*.6});for(const[e,t]of Object.entries(Y)){const n=new M(t*Ni.hands[0],Ni.hands[1],Ni.floor);_t(i,e,1,i.withinReach(e,n,.97),new M(.6,1,0)),i.face(`hand_${e}`,{x:-80})}}const Rr={feet:[.3,-.72,1.5],hands:[.78,-.05],nod:-4,floor:Ni.floor};function hS(i){for(const[e,t]of Object.entries(Y)){const[n,s,r]=Rr.feet;i.step(e,new M(t*n,s,r),new M(0,-1,1))}oe(i,{nod:Rr.nod});for(const[e,t]of Object.entries(Y)){const n=new M(t*Rr.hands[0],Rr.hands[1],Rr.floor);_t(i,e,1,i.withinReach(e,n,.97),new M(1,.3,0)),i.face(`hand_${e}`,{x:-80})}}function fS(i){for(const[e,t]of Object.entries(Y))i.turn(`thigh_${e}`,{x:-88}),i.bend(`shin_${e}`,rS+t*9*i.sway),i.turn(`foot_${e}`,{x:-t*5*i.sway+(e==="r"?i.tap:0)})}function $i(i,e){i.posture==="stand"&&(i.lift("root",{z:-e}),Ki(i,e))}function cu(i,e,t,n,s=xd){Ae(i,e,[...e.free]);for(const r of e.free)_t(i,r,t,i.carried(new M(Y[r]*n[0],n[1],n[2])),new M(...s))}const Ad={hearts:{open:1,tint:null,hearts:!0},amused:{open:.3,tint:[1,.85,.4]},startled:{open:1.5,tint:[1,1,1]},worried:{open:.7,tint:[.6,.75,1]},angry:{open:.45,tint:[1,.35,.3]},reading:{open:.8,tint:null}};function Ke(i,e,t=1){const{open:n,tint:s,shape:r}=Ad[e];i.shutEyes(Vt(1,n,t)),s&&t>.5&&i.tintEyes(s),r&&i.shapeEyes(r,t)}const Qo=[.3,-.45,2],dS=[.46,-.82,2.04];function pS(i,e,t){const n=Ve(t,.55,.75),s=(1-n)*Re(t,6);pe(i,0),oe(i,{lean:6,nod:20-4*n,turn:2*Re(t)}),cu(i,e,1,[Qo[0],Qo[1],Qo[2]+.035*s]),i.holdLaptop(),Ke(i,"reading")}function mS(i,e,t){const n=Ut(t,ce.joy.frames),s=Math.max(Math.sin(2*Math.PI*ce.joy.jumps*lt(n,.06,.94)),0)*(1-.3*n);i.lift("root",{z:.32*s}),pe(i,0),oe(i,{lean:-5*s,nod:-14+4*s}),En(i,e,0,70+55*s,6*Re(t,4)),Zi(i,.5*s)}function gS(i,e,t){const n=Ut(t,28),s=ne(n,0,.2)*(1-ne(n,.82,1)),r=Ve(n,.28,.82);pe(i,0),oe(i,{lean:4*s,nod:10*s,turn:24*r*Re(lt(n,.28,.82),1.5)}),cu(i,e,s,dS);for(const o of e.free)i.face(`hand_${o}`,{z:-Y[o]*90*s});Ke(i,"worried",s)}function _S(i,e,t){const n=Ut(t,24),s=Ve(n,.05,.9);pe(i,0),oe(i,{lean:-10*s,nod:-10*s}),En(i,e,0,100*s),i.shutEyes(1-.9*Ve(n,.2,.75))}function xS(i,e,t,n){i=(i%1+1)%1;const s=e*t;if(i<t)return[-s/2+e*i,0];const r=(i-t)/(1-t);return[s/2-s*Si(r),n*Math.sin(Math.PI*r)]}function ba(i,e,t,n,s,r=0){const o=i.rig.heads.get(`thigh_${e}`),a=i.rig.heads.get(`shin_${e}`),c=i.rig.heads.get(`foot_${e}`),l=o.z-a.z,u=a.z-c.z,h=l+u+s-n,f=(t*t+h*h-l*l-u*u)/(2*l*u);if(f<-1-1e-10||f>1+1e-10)throw new RangeError(`${e} stride target is outside the unchanged leg reach`);const d=Math.acos(Math.round(f*1e10)/1e10),g=Math.atan2(t,h)-Math.atan2(u*Math.sin(d),l+u*Math.cos(d));i.turn(`thigh_${e}`,{x:g*180/Math.PI}),i.bend(`shin_${e}`,d*180/Math.PI),i.face(`foot_${e}`,{x:r})}function wa(i,e,t,n,{running:s=!1,lean:r=s?10:3,clearance:o,apart:a=[],drop:c=0,bend:l={},behind:u=0}={}){const[h,f,d]=s?ou:au,g=t%.5,_=s&&g>f?Math.max(0,Math.sin(Math.PI*(g-f)/(.5-f))):0,p=n*(-(s?.075:.11)+(s?.055*_:0))-c;i.lift("root",{z:p}),pe(i,0),oe(i,{...l,lean:r*n+(l.lean??0),nod:(s?-6:-2)*n+(l.nod??0)});const m=(s?24:14)*Re(t)*n,v=e.carried??e.busy,y=Object.keys(Y).filter(x=>s&&!v.has(x)&&!e.level.has(x)&&!a.includes(x));Ae(i,e,[...y,...a],Object.fromEntries(Object.entries(Y).map(([x,P])=>[x,v.has(x)?0:P*m])));for(const x of y)yd(i,x,Y[x]*m,10+40*n);if(n>0||c||u)for(const[x,P]of[["l",0],["r",.5]]){const[A,E]=xS(t+P,h,f,o??d),R=(t+P)%1,b=R>=f?(R-f)/(1-f):0,S=(s?14:11)*Math.sin(Math.PI*b)*n;ba(i,x,n*A+u,n*E,p,S)}}function pr(i,e,t,n,s,r={}){const o=lt(t,0,n),a=Si(o);return i.lift("root",{y:ca*(1-a)}),wa(i,e,ca*a/(r.running?ou:au)[0],1-Si((o-.76)/.24),r),90*(1-ne(t,n,s))}function eo(i,e,t,n,s,r={}){const o=lt(t,n+Jh/2,1),a=(o<.3?o*o/.6:o-.15)/.85;return i.lift("root",{y:-ca*a}),wa(i,e,ca*a/(r.running?ou:au)[0],Si(o/.25),r),s*90*ne(t,n,n+Jh)}function Rd(i,e,t,n,s=!1){i.revolve(pr(i,e,Ut(t,n),Ed,Td,{running:s}))}function vS(i,e,t){Rd(i,e,t,40)}function yS(i,e,t){Rd(i,e,t,28,!0)}function MS(i,e,t){if(!lS("pull_ups",e)){Sa(i,e,t);return}Cd(i,e,t,{pull:.5-.5*Math.cos(2*Math.PI*t),swing:0})}const ef=i=>(e,t,n)=>Cd(e,t,n,{pull:0,swing:Re(n),grips:[i]});function Cd(i,e,t,{pull:n,swing:s,grips:r=Object.keys(Y)}){const o=r.filter(a=>e.free.has(a));i.lift("root",{y:Mc.back,z:Mc.up+Mc.rise*n}),oe(i,{nod:-3*n,turn:2*s}),Ae(i,e,o);for(const[a,c]of Object.entries(Y))i.turn(`thigh_${a}`,{x:-8+7*s*c}),i.bend(`shin_${a}`,18+8*s*c),i.turn(`foot_${a}`,{x:-10}),o.includes(a)&&(i.reach(a,new M(c*oS,0,aS),cS),i.face(`hand_${a}`,{x:-90}))}const SS=36,bS=28,Cr=.5,tf=.36,wS=16,ES=7,nf=-2.45,sf=-1.54,bc=new M(1,-.6,.02),TS=new M(1,-1,-1),AS=new M(0,1,0),RS={y:-15,z:-10,bend:15},CS=.97,to=new M(...xd),zi=.24,Pd=.1,PS=6.04,LS=10.36,Ho=.52,Pr=.42,rf=.6,IS={y:60,z:-10,bend:15},DS=60,NS=45,Ld={y:30,z:-25,bend:10},US={y:0,z:-15,bend:0};function Kt(i,e,t,{y:n=vs,x:s=0,z:r=0,bend:o=10}){const a=Y[e];i.turn(`upper_arm_${e}`,{y:a*Vt(vs,n,t)}),i.turn(`upper_arm_${e}`,{x:s*t}),i.turn(`upper_arm_${e}`,{z:a*r*t}),i.bend(`forearm_${e}`,Vt(10,o,t))}function _t(i,e,t,n,s){const r=i.head(`upper_arm_${e}`,i.standing(`upper_arm_${e}`)),o=n.clone().sub(r),c=new M(Y[e]*Math.cos(Nt(vs)),0,-Math.sin(Nt(vs))).lerp(o.clone().normalize(),t).normalize();i.reach(e,r.clone().add(c.multiplyScalar(Vt(CS,o.length(),t))),AS.clone().lerp(s,t))}const no=i=>new M(Y[i]*_c[0],_c[1],_c[2]);function Ki(i,e){for(const t of Object.keys(Y))ba(i,t,0,0,-e)}function OS(i,e,t){[...e.level].sort().forEach((n,s)=>{const r=Math.max(t-.05*s,0);i.turn(`hand_${n}`,{x:wS*Qh(r,3,2.5),y:Y[n]*ES*Qh(r,2.5,3)})})}const Id=(i,e)=>e.reduce((t,n)=>t+Ve(i,n,n+.05),0),mr=i=>[...i.carried].filter(e=>!i.busy.has(e));function FS(i,e,t){const n=Ve(t,Cr,Cr+.22),s=pr(i,e,t,Cr,Cr+.14,{running:!0,lean:15,drop:.12*n,bend:{lean:-7*n,nod:5*n}});OS(i,e,lt(t,Cr,1)),i.revolve(s)}function BS(i,e,t){const n=Ve(t,0,tf);i.revolve(eo(i,e,t,tf,-1,{bend:{lean:30*n,nod:24*n}}))}function kS(i,e,t){const n=lt(t,.55,.72),s=t<.72?0:zi*(1-ne(t,.84,1)),r=t<.55?Vt(-4.4,nf,ne(t,0,.16))+(sf-nf)*ne(t,.3,.55):t<.72?Vt(sf,-zi,n)+1.2*Math.sin(Math.PI*n):-s;i.lift("root",{z:r}),pe(i,0),oe(i,{turn:25*Math.sin(2*Math.PI*lt(t,.06,.2)),lean:14*(s/zi)+8*ne(t,.3,.55)*(1-n),nod:-10*Ve(t,.86,1)});const o=t>=.2&&t<.55?ne(t,.2,.27):0,a=Ve(t,.55,.74);Ae(i,e,o||a?Object.keys(Y):[]);for(const c of Object.keys(Y))o?(_t(i,c,o,new M(Y[c]*bc.x,bc.y,bc.z),TS),i.face(`hand_${c}`,{z:-Y[c]*90*o})):a&&Kt(i,c,a,RS);Ki(i,t<.72?Vt(0,zi,n)+Pd*Math.sin(Math.PI*n):s)}function zS(i,e,t){const n=lt(t,.3,1),s=ne(t,.05,.3),r=ne(t,.3,.42);i.lift("root",{y:-2.4*n,z:t<.3?-zi*s:-zi+PS*n-LS*n*n}),pe(i,0),oe(i,{lean:15*s*(1-r),nod:18*s*(1-r)});for(const o of Object.keys(Y))Kt(i,o,s,{y:Vt(vs,-15,r),x:Vt(40,0,r),z:-10*r,bend:10});Ki(i,t<.3?zi*s:zi*(1-r)+2*Pd*Ve(t,.36,.62)),i.revolve(-35*ne(t,0,.2))}function HS(i,e,t){const n=[...e.busy],s=mr(e),r=1-ne(t,.7,.92),o=Ve(t,Ho,Ho+.2),a=pr(i,e,t,Ho,Ho+.14,{running:!0,lean:14,apart:[...n,...s],drop:.14*o,bend:{lean:-6*o}});n.forEach(c=>Kt(i,c,r,IS)),s.forEach(c=>Kt(i,c,r,Ld)),i.shutEyes(1-.45*r),i.revolve(a)}function VS(i,e,t){const n=mr(e),s=ne(t,0,.12)*(1-ne(t,.24,.34)),r=eo(i,e,t,.34,-1,{clearance:.18,lean:0,apart:s?n:[],bend:{nod:10*Ve(t,.1,.26)}});s&&n.forEach(o=>_t(i,o,s,no(o),to)),i.revolve(r)}function GS(i,e,t){const n=Je(e),s=ne(t,Pr,Pr+.04)*(1-ne(t,.62,.7)),r=6*lt(t,Pr,.7),o=-.05*s*Math.abs(Re(r)),a=ne(t,.7,.76)*(1-ne(t,.9,.98)),c=Id(t,[.77,.83]);i.lift("root",{z:o});const l=pr(i,e,t,Pr,Pr+.1,{running:!0,lean:6,apart:a?[n]:[],bend:{nod:7*c,lean:2*c}});if(a&&_t(i,n,a,no(n),to),s)for(const[u,h]of[["l",0],["r",.5]])ba(i,u,0,.22*s*Math.max(Re(r+h),0),o);i.shutEyes(1-.6*c),i.revolve(l)}function WS(i,e,t){const n=Je(e),s=ne(t,0,.06)*(1-ne(t,.2,.26)),r=ne(t,.26,.32)*(1-ne(t,.42,.5)),o=Id(t,[.07,.13]),a=eo(i,e,t,.4,Y[n],{running:!0,lean:6,apart:s||r?[n]:[],bend:{nod:7*o,lean:2*o}});s&&_t(i,n,s,no(n),to),r&&Kt(i,n,r,US),i.shutEyes(1-.6*o),i.revolve(a)}function XS(i,e,t){const n=ne(t,.72,.8)*(1-ne(t,.9,.98)),s=Ve(t,.78,.92),r=[...e.level].sort(),o=pr(i,e,t,rf,rf+.12,{apart:n?r:[],bend:{nod:-8*s}});n&&Bd(i,e,n,s),i.shutEyes(1-.7*s),i.revolve(o)}function qS(i,e,t){const n=Je(e),s=ne(t,0,.08)*(1-ne(t,.24,.32)),r=eo(i,e,t,.3,Y[n],{apart:s?[n]:[],bend:{tilt:-Y[n]*5*s}});s&&Kt(i,n,s,{y:0,x:-85,z:md,bend:gd+_d*Re(lt(t,0,.32),2)}),i.revolve(r)}function YS(i,e,t){i.revolve(pr(i,e,t,Ed,Td))}function jS(i,e,t){i.revolve(eo(i,e,t,0,-1))}const $S={bare:YS,butler:FS,homie:kS,squire:HS,coach:GS,colleague:XS},KS={bare:jS,butler:BS,homie:zS,squire:VS,coach:WS,colleague:qS};function ZS(i,e,t){$S[e.voice](i,e,Ut(t,SS))}function JS(i,e,t){KS[e.voice](i,e,Ut(t,bS))}const QS=.2,eb=1.4,of=.13;function Dd(i){return ne(i,0,.22)-2*ne(i,.32,.62)+ne(i,.7,.85)}function tb(i,e,t){const n=Je(e),s=Dd(t);$i(i,QS),pe(i,0),oe(i,{lean:26,nod:20,turn:-Y[n]*28*s,twist:-Y[n]*10*s}),Ae(i,e,[n]),Kt(i,n,1,{y:30,z:-60+25*s,bend:80}),i.holdUpright("magnifying_glass",n,[0,0,0],{x:tE}),Ke(i,"reading")}const ft={intro:12,hold:48,outro:12,fps:12,ready:3,opens:11,pageEvery:24,pageFrom:12,pageTo:20,lines:4,referenceArm:.985,forward:.68,drop:.3,drawDrop:.18,elbow:[1,-1,-1],wristTurn:90},Al=ft.intro+ft.hold+ft.outro,ji={grip:.34,forward:.02},z={intro:8,hold:32,outro:8,fps:12,yawnFrames:28,pastimeFrames:40,greetingFrames:24,hopFrames:20,stumbleFrames:24,elbow:[1,-.15,-.35],wrist:[.72,-.72,1.76],supportLift:.22,whistleLift:.25,clothLift:.2,clothTurn:-90,compactFps:6,tap:10,rock:3,turn:12,nod:8,writeStroke:.035,writeHeight:.02,glance:22,hop:.18,stumble:12,writingWrist:[.38,-.76,2.1],yawnWrist:[.48,-.86,2.12],whistleWrist:[.48,-.82,2.2],sipWrist:[.7,-.63,2.17],shieldWrist:[.22,-.64,2.13],wipeWrist:[.1,-.7,1.9],saluteWrist:[1.28,-.32,2.59],gestureIn:.2,gestureOut:.8,yawnEyes:.94,yawnSpan:[.08,.92],pastimeSpan:[.3,.7],whistleEyes:.65,sipEyes:.5,sipTip:12,headphoneEyes:.4,beats:4,sways:2,wipes:3,wipeLift:.035,wipeAcross:.04,bowLean:18,bowNod:10,leapSpan:[.18,.78],catchSpan:[.15,.45],recoverSpan:[.45,.85],recover:.3},Nd={butler:"writing_stylus",coach:"writing_pencil",colleague:"writing_pen",homie:"writing_marker",squire:"writing_quill"},la=z.intro+z.hold+z.outro,nn={intro:8,hold:144,outro:8,whistleSpan:[.7,.98],beats:12,sways:3},Rl=nn.intro+nn.hold+nn.outro,ea={across:.04,top:.52,bottom:.44,forward:[0,-1,0]};function Ud(i){const e=i*la,t=e>=z.intro&&e<z.intro+z.hold,n=e<z.intro?e:la-1-e;return{frame:e,held:t,ready:t?1:ne(n,0,z.intro-1),phase:t?(e-z.intro)/z.hold:0}}function nb(i){const e=i*Rl,t=e>=nn.intro&&e<nn.intro+nn.hold,n=e<nn.intro?e:Rl-1-e;return{ready:t?1:ne(n,0,nn.intro-1),phase:t?(e-nn.intro)/nn.hold:0}}function Fn(i,e){const t=Ut(i,e);return{u:t,ready:ne(t,0,z.gestureIn)*(1-ne(t,z.gestureOut,1))}}function ib(i,e,t=[0,0,0]){return i.rig.heads.get(`hand_${e}`).clone().add(new M(Y[e]*(ji.grip+t[0]),ji.forward+t[1],t[2])).applyMatrix4(i.matrix(`hand_${e}`))}function Zt(i,e,t,n,s={}){t&&(_t(i,e,t,i.carried(new M(Y[e]*n[0],n[1],n[2])),new M(...z.elbow)),i.face(`hand_${e}`,{z:-Y[e]*90*t,...s}))}const ua=65;function Od(i,e,t=1){const n=i.rig.eyes.reduce((u,h)=>u.add(h),new M).divideScalar(i.rig.eyes.length),s=i.head("head",i.standing("head")),r=e.clone().sub(s),o=n.z-i.rig.heads.get("head").z,a=Math.asin(Dn.clamp(o/r.length(),-1,1))-Math.atan2(r.z,Math.hypot(r.x,r.y)),c=Dn.radToDeg(Math.atan2(r.x,-r.y)),l=Dn.clamp(c,-ua,ua);return i.face("head",{x:Dn.radToDeg(a)*t,z:l*t}),i.gaze={target:e.toArray(),forward:ea.forward},(c-l)*t}function sb(i,e,t){const n=t*Al,s=n>=ft.intro&&n<ft.intro+ft.hold,r=n<ft.intro?n:Al-1-n,o=s?1:ne(r,0,ft.ready),a=s?1:ne(r,ft.ready,ft.opens),c=s?(n-ft.intro)%ft.pageEvery:0,l=s?ne(c,ft.pageFrom,ft.pageTo):0;pe(i,0),Ae(i,e);const u=Math.min(...Object.keys(Y).map(x=>{const P=A=>i.rig.heads.get(`${A}_${x}`);return P("upper_arm").distanceTo(P("forearm"))+P("forearm").distanceTo(P("hand"))}))/ft.referenceArm,h=Object.keys(Y).map(x=>i.head(`upper_arm_${x}`,i.standing(`upper_arm_${x}`))),f=h[0].clone().add(h[1]).multiplyScalar(.5),d=Yd(a),g=Hi("l",a).add(Hi("r",a)).multiplyScalar(.5).applyMatrix4(d),_=new M(f.x-g.x*u,f.z-(ft.drop+ft.drawDrop*(1-o))*u-g.y*u,-f.y+ft.forward*u-g.z*u),p=new Le().makeTranslation(_.x,_.y,_.z).multiply(d).scale(new M(u,u,u));for(const[x,P]of Object.entries(Y)){const A=aa(Hi(x,a).applyMatrix4(p));if(!o)continue;_t(i,x,o,A,new M(...ft.elbow));const E=Dn.radToDeg(Math.atan2(De.closedGrip*(1-a),De.gripBack));i.face(`hand_${x}`,{z:-P*(ft.wristTurn+E)*o})}const m=Math.floor(c/(ft.pageEvery/ft.lines)),v=c%(ft.pageEvery/ft.lines)/(ft.pageEvery/ft.lines-1),y=new M(Vt(-.04,ea.across,v),Vt(ea.top,ea.bottom,m/(ft.lines-1)),-De.pages).applyMatrix4(p);Od(i,aa(y),a),i.holdBook(a,l,s||r>=ft.ready),Ke(i,"reading",a)}const rb=[.55,-.35,1.35],ob=[.65,-.92,2.04],wc=[.7,.2,-1],af=.06;function ab(i,e,t){pe(i,t);const n=[...e.cloth];Ae(i,e,n);const s=ne(t,.15,.3)*(1-ne(t,.75,.9)),r=ne(t,.08,.15)*(1-ne(t,.88,.95)),o=ne(t,.3,.35)*(1-ne(t,.7,.75));oe(i,{nod:6*s,tilt:4*o*Math.sin(2*Math.PI*3*t)});for(const a of n){const c=Y[a],l=2*Math.PI*4*t,u=rb.map((f,d)=>f+(ob[d]-f)*s),h=new M(c*(u[0]+af*o*Math.cos(l)),u[1],u[2]+af*o*Math.sin(l));_t(i,a,r,i.carried(h),new M(c*wc[0],wc[1],wc[2])),i.face(`hand_${a}`,{z:-c*90*r}),r>.5&&i.holdCloth()}Ke(i,o>.5?"amused":"reading")}function cb(i,e,t){const{ready:n,phase:s}=nb(t),r=e.voice==="butler",o=Ve(s,...nn.whistleSpan)*n;pe(i,0),oe(i,{turn:z.turn*n,nod:-z.nod*o/2,lean:z.rock*Re(s,nn.sways)*(r?o:n)}),Ae(i,e),i.tap=z.tap*Math.max(Re(s,nn.beats),0)*n,i.posture==="stand"&&i.turn("foot_r",{x:i.tap}),o&&i.shutEyes(1-z.whistleEyes*o)}function Fd(i,e,t){const{u:n,ready:s}=Fn(t,z.yawnFrames),r=Je(e);pe(i,0),oe(i,{lean:-z.rock*s,nod:-z.nod*s}),Ae(i,e),Zt(i,r,s,z.yawnWrist),s&&i.putAway(...Et),i.shutEyes(1-z.yawnEyes*Ve(n,...z.yawnSpan))}function lb(i,e,t){const{u:n,ready:s}=Fn(t,z.pastimeFrames),r=Ve(n,...z.pastimeSpan),o=Je(e);pe(i,0),oe(i,{lean:-z.rock*r,nod:-z.nod*r}),Ae(i,e),Zt(i,o,s,z.whistleWrist),s&&i.putAway(...Et,"coach_whistle"),s>.5&&i.holdProp("hand_whistle",o,[0,0,z.whistleLift],{z:Y[o]*90}),i.shutEyes(1-z.whistleEyes*r)}const Rt={frames:120,fps:8,down:[0,.1],up:[.9,1],tunes:[[.3,.45],[.62,.8]],beats:40,pillow:[0,1,3.2],tilt:72,across:-1.6,kneeUp:60,kneeBend:105,glance:40,ankle:[-.15,-.15,-.1],crossedKnee:[1,-.4,.6],footBob:18,wrist:[.6,.55,2.85],fingers:[-1,.4,.4],elbow:[1,-.3,.8],straw:[.14,-.9,.4],strawTip:115,strawWag:8,eyes:.45,whistleEyes:.2},ub=i=>Rt.tunes.reduce((e,[t,n])=>e+Ve(i,t,n),0);function hb(i,e,t){const n=Ut(t,Rt.frames),s=ne(n,...Rt.down)*(1-ne(n,...Rt.up)),r=ub(n),o=Math.max(Re(n,Rt.beats),0);if(pe(i,0),Ae(i,e,s?Object.keys(Y):[]),!s)return;i.putAway(...Et),oe(i,{turn:-Rt.glance*s});for(const[u,h]of Object.entries(Y)){const[f,d,g]=Rt.wrist;_t(i,u,s,new M(h*f,d,g),new M(...Rt.elbow));const[_,p,m]=Rt.fingers;i.aim(`hand_${u}`,new M(h*_,p,m))}i.turn("thigh_l",{x:-Rt.kneeUp*s}),i.bend("shin_l",Rt.kneeBend*s);const a=i.head("shin_l",i.matrix("shin_l")),c=i.head("foot_r",i.standing("foot_r"));i.step("r",c.lerp(a.add(new M(...Rt.ankle)),s),new M(...Rt.crossedKnee)),i.turn("foot_r",{x:-Rt.footBob*r*o}),i.wearProp("straw",Rt.straw,{x:Rt.strawTip+Rt.strawWag*(1+r)*Re(n,9)});const l=new M(...Rt.pillow);i.turnAll({x:-Rt.tilt*s},l),i.turnAll({z:90*s},l),i.shiftAll([Rt.across*s,-l.y*s,-l.z*s]),i.shutEyes(Vt(1,Vt(Rt.eyes,Rt.whistleEyes,r),s))}function Bd(i,e,t,n){for(const s of e.level)Zt(i,s,t,z.sipWrist,{x:-z.sipTip*n})}function fb(i,e,t){const{u:n,ready:s}=Fn(t,z.pastimeFrames);pe(i,0),oe(i,{nod:-z.rock*s}),Ae(i,e),Bd(i,e,s,Ve(n,...z.pastimeSpan)),i.shutEyes(1-z.sipEyes*Ve(n,...z.pastimeSpan))}function db(i,e,t){const{u:n,ready:s}=Fn(t,z.pastimeFrames);pe(i,0),oe(i,{nod:z.nod*Re(n,z.beats)*s,tilt:z.rock*Re(n,z.sways)*s}),Ae(i,e),i.swing(Re(n,z.sways)*s),i.shutEyes(1-z.headphoneEyes*s)}function pb(i,e,t){const{u:n,ready:s}=Fn(t,z.pastimeFrames),r=[...e.shield][0];if(!r)return Sa(i,e,t);const o=r==="l"?"r":"l";pe(i,0),oe(i,{nod:z.nod*s}),Ae(i,e),Zt(i,r,s,z.shieldWrist),Zt(i,o,s,[z.wipeWrist[0],z.wipeWrist[1]+z.wipeAcross*Re(n,z.wipes),z.wipeWrist[2]+z.wipeLift*Re(n,z.wipes*2)]),s&&(i.putAway("squire_quill"),i.keep.add("squire_shield")),s>.5&&i.holdProp("polishing_cloth",o,[0,0,z.clothLift],{x:z.clothTurn})}function mb(i,e,t){const{ready:n,phase:s}=Ud(t),r=z.writeStroke*Re(s,z.beats);if(pe(i,0),oe(i,{nod:z.nod*n,lean:z.rock*n}),Ae(i,e),Zt(i,"l",n,z.wrist),Zt(i,"r",n,[z.writingWrist[0]+r,z.writingWrist[1],z.writingWrist[2]]),n&&i.putAway(...Et),n>=1){const o=e.voice==="butler",a=tn.paper.thickness*(o?2.5:.5),c=z.wrist[2]+z.supportLift+a+tn.pen.length/2+tn.pen.tip-z.writingWrist[2];i.holdProp(Nd[e.voice]||"writing_pen","r",[0,0,c],{z:-90}),i.holdProp(e.voice==="butler"?"writing_tablet":"writing_paper","l",[0,-z.wrist[0],z.supportLift],{z:90})}Ke(i,"reading",n)}function gb(i,e,t){const{ready:n,phase:s}=Ud(t);pe(i,0),oe(i,{nod:z.nod*n}),Ae(i,e),Zt(i,"l",n,z.wrist),Zt(i,"r",n,[z.wrist[0]+z.writeStroke*Re(s,z.sways),z.wrist[1],z.wrist[2]+z.writeHeight*Math.max(Re(s,z.sways),0)]),n&&i.putAway(...Et),n>=1&&(i.holdProp("papers","l",[0,-z.wrist[0],z.supportLift],{z:90}),i.props.get("papers").phase=s)}function _b(i,e,t){const{ready:n}=Fn(t,z.greetingFrames);pe(i,0),oe(i,{lean:z.bowLean*n,nod:z.bowNod*n}),Ae(i,e),n&&i.putAway(...Et)}function xb(i,e,t){const{ready:n}=Fn(t,z.greetingFrames),s=Je(e);pe(i,0),oe(i,{nod:-z.rock*n}),Ae(i,e),Zt(i,s,n,z.saluteWrist),n&&i.putAway(...Et)}function vb(i,e,t){const{u:n,ready:s}=Fn(t,z.hopFrames),r=Ve(n,...z.leapSpan);$i(i,z.hop*Ve(n,0,z.leapSpan[0])),i.lift("root",{z:z.hop*r}),pe(i,0),oe(i,{lean:-z.rock*r}),En(i,e,0,va*r),i.posture==="stand"&&Zi(i,r),Ke(i,"startled",s)}function yb(i,e,t){const{u:n,ready:s}=Fn(t,z.stumbleFrames),r=Ve(n,...z.catchSpan)-z.recover*Ve(n,...z.recoverSpan);pe(i,0),oe(i,{lean:z.stumble*r,tilt:z.rock*r}),En(i,e,0,va*s),Ke(i,"startled",Math.max(r,0))}function Mb(i,e,t){const{ready:n}=Fn(t,z.greetingFrames);pe(i,0),oe(i,{turn:z.glance*n,nod:-z.rock*n}),Ae(i,e)}const sn={blows:1,blowFrames:8,fps:10,lands:.3,snap:50,thumb:90,roll:-90,fist:.62,turn:80,strike:.413,landsAt:[.72,-1.81]};function Sb(i){const e=i*sn.blows%1;return e<sn.lands?1-(e/sn.lands)**2:Si(lt(e,sn.lands,1))}function kE(i){const e=Y[Je(i)],[t,n]=sn.landsAt,s=Nt(e*sn.turn);return(e*t*Math.cos(s)-n*Math.sin(s))/Qn}function bb(i,e,t){const n=Je(e),s=Math.max(Sb(t),sn.strike),r=1-s;$i(i,.04*r),pe(i,0),oe(i,{lean:8+6*r,nod:10}),Ae(i,e,[n]),Kt(i,n,1,{y:Vt(75,5,s),z:-35,bend:Vt(15,70,s)}),i.roll(`forearm_${n}`,Y[n]*sn.roll),i.clench(n,sn.fist),i.holdProp("work_hammer",n,[0,0,0],{x:sn.thumb,z:Y[n]*sn.snap*r}),i.posture==="stand"&&i.revolve(Y[n]*sn.turn)}const Rn={frames:22,fps:12,out:[0,.18],away:[.82,1],bend:.28,lean:30,nod:24,held:[.55,-1.2,1.7],sweep:.12,tip:45};function wb(i,e,t){const n=Je(e),s=Te(t,Rn.out)*(1-Te(t,Rn.away)),r=Rn.sweep*Re(lt(t,Rn.out[1],Rn.away[0]));$i(i,Rn.bend*s),pe(i,0),oe(i,{lean:Rn.lean*s,nod:Rn.nod*s}),Ae(i,e,[n]);const[o,a,c]=Rn.held;_t(i,n,s,i.withinReach(n,i.carried(new M(Y[n]*(o+r),a,c)),.97),new M(...z.elbow)),i.putAway(...Et),s>.3&&i.holdUpright("magnifying_glass",n,[0,0,0],{x:Rn.tip*s}),Ke(i,"reading",s),i.posture==="stand"&&i.revolve(Y[n]*sn.turn)}const Oi={step:.6,hop:.12,lean:8,shadeWrist:[1.18,-.5,2.72],shadeHand:[-.35,-1,.2]},cf=-1.2;function Eb(i,e,t=0){const n=new M((e.x-.5)*Qn,e.behind?-cf:cf,jr+(.5-e.y)*Qn),s=i.matrix("head").clone(),r=Od(i,n.applyAxisAngle(new M(0,0,1),Nt(-t))),o=e.amount??1;return o<1&&i.final.set("head",Tb(s,i.matrix("head"),o)),r*o*o}function Tb(i,e,t){const[n,s]=[i,e].map(r=>{const o={at:new M,turn:new On,size:new M};return r.decompose(o.at,o.turn,o.size),o});return new Le().compose(n.at.lerp(s.at,t),n.turn.slerp(s.turn,t),n.size.lerp(s.size,t))}function Ab(i,e,t){const{shade:n,back:s}=i.sky??{shade:0,back:0};i.lift("root",{y:Oi.step*s,z:Oi.hop*Math.sin(Math.PI*s)}),pe(i,t),oe(i,{lean:-Oi.lean*s});const r=Je(e);if(Ae(i,e,n?[r]:[]),n){Zt(i,r,n,Oi.shadeWrist);const[o,a,c]=Oi.shadeHand,l=`hand_${r}`,u=i.rig.along.get(l).clone().transformDirection(i.matrix(l));i.aim(l,u.lerp(new M(Y[r]*o,a,c),n)),i.putAway(...Et)}}const hn={lean:60,nod:4,drop:.3,behind:.25,hands:[.4,-.25,.8],turn:4,intro:9,stride:6,fps:12};function Rb(i){const e=i*(hn.intro+hn.stride);return e>=hn.intro?1:Si((e-hn.turn)/(hn.intro-hn.turn))}function Cb(i,e,t){const n=Rb(t);wa(i,e,i.stride,i.posture==="walk"?1:0,{lean:0,drop:hn.drop*n,behind:hn.behind*n,bend:{nod:hn.nod*n}}),i.bendAbove("spine",{x:hn.lean*n});const[s,r,o]=hn.hands;for(const[a,c]of Object.entries(Y))_t(i,a,n,i.withinReach(a,new M(c*s,r,o),.97),new M(...z.elbow)),i.face(`hand_${a}`,{z:-c*90*n});i.putAway(...Et)}function Pb(i,e,t){const n=Je(e);pe(i,0),oe(i,{nod:-14,lean:-3,tilt:-Y[n]*5}),Ae(i,e,[n]),Kt(i,n,1,{y:-12+3*Re(t),z:-15,bend:10}),Ke(i,"worried",.6)}function En(i,e,t,n,s=0){Ae(i,e,[...e.free]);for(const r of e.free){const o=Y[r],a=Math.min(Math.max(n/FM,0),1);Kt(i,r,a,{x:t+s*o,y:-Math.min(n,va),bend:10})}}function Zi(i,e,t=0){for(const[n,s]of Object.entries(Y))i.turn(`thigh_${n}`,{x:-24*e+t*s}),i.turn(`shin_${n}`,{x:44*e}),i.turn(`foot_${n}`,{x:-8*e})}function Lb(i,e,t){const n=Ut(t,16),s=ne(n,0,.26)*(1-ne(n,.26,.36)),r=ne(n,.3,.45);i.lift("root",{z:.1*r}),pe(i,0),oe(i,{lean:14*s-6*r,nod:-4*r}),En(i,e,40*s,80*ne(n,.26,.42)*(1-.4*ne(n,.6,1))),Ki(i,.28*s),Zi(i,r)}const Ib=25,Db=360;function Nb(i,e,t){const n=Ut(t,22),s=ne(n,0,.26)*(1-ne(n,.26,.34)),r=ne(n,.3,.86),o=ne(n,.28,.4)*(1-ne(n,.86,.95));i.lift("root",{z:.1*o}),pe(i,0),oe(i,{lean:12*s}),En(i,e,30*s,Ib*o),Ki(i,.28*s),Zi(i,1.2*o),i.turnAll({x:Db*r},i.head("hips",i.matrix("hips")))}function Ub(i,e,t){const n=Ut(t,12),s=ne(n,0,.2),r=Ve(n,0,.3);i.lift("root",{z:.1*s}),pe(i,0),oe(i,{lean:-9*s-8*r,nod:-6*s-10*r,tilt:4*Re(t,3)*s}),En(i,e,0,(70+8*Re(t,3))*s+25*r,14*Re(t,3)*s),Ke(i,"startled",Math.max(r,.6*s)),Zi(i,.5*s,14*Re(t,3)*s)}function Ob(i,e,t){const n=Ut(t,Cl.frames),s=ne(n,0,.2)*(1-ne(n,.2,1));pe(i,0),oe(i,{lean:16*s,nod:8*s}),En(i,e,0,38*s),Ki(i,.32*s)}function Fb(i,e,t){const n=Ut(t,24),s=n<.5,r=eb*(s?Si(lt(n,0,.5)):1-Si(lt(n,.5,1))),o=Math.sqrt(Math.max(Math.sin(Math.PI*n),0)),a=mr(e);i.lift("root",{y:s?-r:r}),wa(i,e,4*n,o,{running:!0,lean:12,apart:a}),a.forEach(c=>Kt(i,c,o,Ld)),i.revolve((s?90:-90)*Math.min(1,3*Math.sin(Math.PI*n)))}function lf(i,e,t){const n=of*Math.max(Re(3*t),0)*Ve(t,0,1);pe(i,0),oe(i,{tilt:8*Ve(t,0,1),nod:6*Ve(t,0,1),turn:10*Ve(t,0,1)}),Ae(i,e),ba(i,"r",0,n,0,15*n/of)}function Bb(i,e,t){const n=Ve(t,0,1);pe(i,0),oe(i,{tilt:14*n,nod:-8*n});for(const s of Object.keys(Y))Kt(i,s,n,{y:30,z:-15,bend:100})}function kb(i,e,t){const n=Je(e),s=ne(t,0,.15)*(1-ne(t,.8,1)),r=Ve(t,.2,.75);pe(i,0),oe(i,{lean:-4*r,nod:-6*r}),Ae(i,e,s?[n]:[]),s&&_t(i,n,s,no(n),to),i.shutEyes(1-.7*r)}function zb(i,e,t){const n=Je(e),s=ne(t,0,.2)*(1-ne(t,.6,.85));pe(i,0),oe(i,{nod:18*s*(1-ne(t,.35,.5)),turn:-Y[n]*8*s}),Ae(i,e,s?[n]:[]),s&&_t(i,n,s,no(n),to)}function Hb(i,e,t){const n=mr(e),s=ne(t,0,.2)*(1-ne(t,.75,1));pe(i,0),oe(i,{tilt:-5*s,nod:4*s}),Ae(i,e,s?n:[]),s&&n.forEach(r=>Kt(i,r,s,{y:30,z:-25+5*Re(3*t),bend:10}))}const Vb={bare:lf,butler:lf,homie:Bb,coach:kb,colleague:zb,squire:Hb};function Gb(i,e,t){Vb[e.voice](i,e,Ut(t,20))}const he={frames:36,fps:12,hatOn:1.101,hatWrist:[1.05,-.2,2.85],hatRaised:[.95,-.5,2.85],hatTip:25,hatFingers:.25,hatBow:22,hatNod:14,monocleWrist:[.55,-.8,2.62],monocleWorn:[.354,-.95,.66],monoclePeer:8,monocleTilt:9,toastWrist:[.78,-.72,2.55],toastClink:.12,sipWrist:[.42,-.78,2.38],sipTip:20,shakaWrist:[1.22,-.25,2.72],shakaWaggle:28,shakaWaggles:3,shadesWrist:[.5,-.82,2.55],shadesWorn:[0,-.96,.66],shadesLean:7,shadesTilt:10,fireWrist:[.48,-.86,2.28],fireSize:2.4,thumbWrist:[.62,-.84,2.3],glassesWrist:[.32,-.8,2.47],peerLean:12,peerTurn:18,prayerWrist:[.12,-.62,2],prayerRoll:180,thanksBow:14,popperWrist:[.95,-.45,2.85],popAt:.4,popHop:.12,flex:{y:0,x:-85,z:15,bend:115},flexPump:15,trophy:{y:-55,x:15,z:0,bend:15},trophyHop:.1,sword:{y:-62,x:18,z:0,bend:12},swordThrust:12,shieldWrist:[.24,-.78,2.3],shieldCrouch:.08,shieldBump:.5,castleWrist:[.55,-.88,2.34]},io=i=>ya.forEach(e=>i.keep.add(e)),mn=i=>Fn(i,he.frames);function bi(i,e,t,n,s={}){Zt(i,e,t,n,{x:-60*t,...s})}const Wb=new M(0,0,1);function Xb(i,e,t){const{u:n,ready:s}=mn(t),r=Je(e),o=ne(n,.2,.3)*(1-ne(n,.7,.8)),a=ne(n,.3,.4)*(1-ne(n,.6,.7)),c=Ve(n,.32,.72);if(pe(i,0),oe(i,{lean:he.hatBow*c,nod:he.hatNod*c}),Ae(i,e,s?[r]:[]),bi(i,r,s,he.hatWrist.map((l,u)=>Vt(l,he.hatRaised[u],a))),s&&i.aim(`hand_${r}`,i.rig.along.get(`hand_${r}`).clone().transformDirection(i.matrix(`hand_${r}`)).lerp(Wb,s)),o){const l={y:Y[r]*he.hatTip*o};i.putAway("butler_top_hat","butler_top_hat_band"),i.wearProp("top_hat",qb(i,r,o,l).toArray(),l)}Ke(i,"amused",c)}function qb(i,e,t,n){const s=new M(Y[e]*(un.hat.crown+un.hat.brim),0,0).applyMatrix4(Gs(0,n.y,0)),o=ib(i,e,[he.hatFingers,0,0]).applyMatrix4(i.matrix("head").clone().invert()).sub(s).sub(i.rig.heads.get("head"));return new M(0,0,he.hatOn).lerp(o,t)}function Yb(i,e,t){const{u:n}=mn(t),s=Je(e),r=Y[s],o=ne(n,0,.2)*(1-ne(n,.82,1)),a=ne(n,.26,.36)*(1-ne(n,.66,.76));pe(i,0),oe(i,{lean:he.monoclePeer*a,nod:he.monoclePeer*a,tilt:r*he.monocleTilt*a}),Ae(i,e,o?[s]:[]);const c=1-.35*a;bi(i,s,o,he.monocleWrist.map((f,d)=>d===2?f-.25*(1-c):f));const[l,u,h]=he.monocleWorn;n>.18&&n<.8?i.wearProp("monocle",[r*l,u,h]):o>.4&&i.holdUpright("monocle",s,[0,0,.2]),Ke(i,"startled",.6*a)}function jb(i,e,t){const{u:n,ready:s}=mn(t),r=Je(e),o=Ve(n,.3,.42),a=Ve(n,.5,.78);pe(i,0),oe(i,{lean:4*o,nod:-6*a}),Ae(i,e,s?[r]:[]);const c=he.toastWrist.map((l,u)=>Vt(l,he.sipWrist[u],a)+(u===1?-he.toastClink*o:0));bi(i,r,s,c),s>.3&&i.holdUpright("champagne_flute",r,[0,0,.1],{x:he.sipTip*a,y:Y[r]*he.sipTip*a}),i.shutEyes(1-.7*a),o>.5&&Ke(i,"amused",o)}function $b(i,e,t){const{u:n,ready:s}=mn(t),r=Je(e),o=Y[r];pe(i,0),oe(i,{lean:-5*s,tilt:-o*8*s,turn:-o*6*s}),Ae(i,e,s?[r]:[]),bi(i,r,s,he.shakaWrist,{y:he.shakaWaggle*Re(lt(n,.2,.8),he.shakaWaggles)*s}),s>.5&&i.holdUpright("shaka",r,[0,0,.32]),Ke(i,"amused",s)}function Kb(i,e,t){const{u:n}=mn(t),s=Je(e),r=Y[s],o=ne(n,0,.15)*(1-ne(n,.15,.3)),a=ne(n,.72,.86)*(1-ne(n,.86,1)),c=n>.22&&n<.82,l=ne(n,.28,.38)*(1-ne(n,.66,.76));pe(i,0),oe(i,{lean:-he.shadesLean*l,tilt:r*he.shadesTilt*l,nod:6*l*Math.max(Re(lt(n,.38,.66),2),0)});const u=Math.max(o,a);Ae(i,e,u?[s]:[]),bi(i,s,u,he.shadesWrist),c?i.wearProp("sunglasses",he.shadesWorn):u>.4&&i.holdUpright("sunglasses",s,[0,-.1,.25])}function Zb(i,e,t){const{u:n,ready:s}=mn(t),r=Je(e),o=ne(n,.18,.28)*(1-ne(n,.66,.74)),a=Ve(n,.66,.84);pe(i,0),oe(i,{nod:8*o*Math.max(Re(lt(n,.28,.66),3),0)+6*a,tilt:Y[r]*5*o}),Ae(i,e,s?[r]:[]),bi(i,r,s,he.fireWrist,{y:25*a*Re(n,9)}),o>.02&&(i.holdUpright("flame",r,[0,0,.18]),Object.assign(i.props.get("flame"),{phase:n,size:he.fireSize*o})),Ke(i,a>.3?"startled":"amused",Math.max(o,a))}function Jb(i,e,t){const{u:n,ready:s}=mn(t),r=Je(e),o=Ve(n,.35,.6);pe(i,0),oe(i,{nod:14*o,lean:3*s}),Ae(i,e,s?[r]:[]),bi(i,r,s,he.thumbWrist,{y:0}),s>.5&&(i.holdUpright("thumb",r,[0,0,.3]),io(i)),Ke(i,"amused",o)}function Qb(i,e,t){const{u:n}=mn(t),s=Je(e),r=ne(n,0,.14)*(1-ne(n,.24,.36)),o=ne(n,.26,.38)*(1-ne(n,.8,.95)),a=Ve(n,.38,.58)-Ve(n,.58,.8);pe(i,0),oe(i,{lean:he.peerLean*o,nod:6*o,turn:he.peerTurn*a}),Ae(i,e,r?[s]:[]);const[c,l,u]=he.glassesWrist;bi(i,s,r,[c,l,u+.08*ne(n,.12,.22)]),Ke(i,"reading",o)}function ew(i,e,t){const{u:n,ready:s}=mn(t),r=Ve(n,.25,.8);pe(i,0),oe(i,{lean:he.thanksBow*r,nod:10*r}),Ae(i,e,s?Object.keys(Y):[]),s&&i.putAway(...Et);for(const[o,a]of Object.entries(Y))Zt(i,o,s,he.prayerWrist,{x:he.prayerRoll*s,y:-a*90*s,z:0});i.shutEyes(1-.85*r)}function tw(i,e,t){const{u:n,ready:s}=mn(t),r=Je(e),o=Ve(n,he.popAt,he.popAt+.2);i.lift("root",{z:he.popHop*o}),pe(i,0),oe(i,{lean:-4*o,nod:-8*o}),Ae(i,e,s?[r]:[]),bi(i,r,s,he.popperWrist),s>.4&&(i.holdUpright("party_popper",r,[0,0,.1],{y:Y[r]*25}),i.props.get("party_popper").burst=lt(n,he.popAt,.95),io(i)),Ke(i,"amused",o)}function nw(i,e,t){const{u:n,ready:s}=mn(t),r=Je(e),o=Math.max(Re(lt(n,.25,.75),2),0);pe(i,0),oe(i,{lean:-5*s,twist:-Y[r]*10*s,tilt:Y[r]*4*s,nod:-4*s}),Ae(i,e,s?[r]:[]),s&&Kt(i,r,s,{...he.flex,bend:he.flex.bend+he.flexPump*o}),Ke(i,"angry",.6*o)}function iw(i,e,t){const{u:n,ready:s}=mn(t),r=Je(e),o=Math.max(Re(lt(n,.25,.75),2),0);i.lift("root",{z:he.trophyHop*o}),pe(i,0),oe(i,{nod:-12*s,lean:-4*s}),Ae(i,e,s?[r]:[]),s&&Kt(i,r,s,he.trophy),s>.4&&(i.holdUpright("trophy",r,[0,0,.3]),io(i)),Ke(i,"amused",s)}function sw(i,e,t){const{u:n,ready:s}=mn(t),r=mr(e)[0]||Je(e),o=Math.max(Re(lt(n,.25,.75),2),0);pe(i,0),oe(i,{lean:-4*s,nod:-10*s}),Ae(i,e,s?[r]:[]),s&&Kt(i,r,s,{...he.sword,y:he.sword.y-he.swordThrust*o}),s&&i.putAway("squire_quill"),s>.4&&(i.holdUpright("sword",r,[0,0,.15],{x:-15}),io(i)),Ke(i,"angry",s)}function rw(i,e,t){const{u:n,ready:s}=mn(t),r=[...e.shield][0];if(!r)return Sa(i,e,t);const o=Ve(n,he.shieldBump,he.shieldBump+.12);$i(i,he.shieldCrouch*s),pe(i,0),oe(i,{lean:8*s-8*o,nod:6*s}),Ae(i,e,s?[r]:[]);const[a,c,l]=he.shieldWrist;Zt(i,r,s,[a,c+.08*o,l]),i.keep.add("squire_shield"),Ke(i,o>.3?"startled":"angry",s)}function ow(i,e,t){const{u:n,ready:s}=mn(t),r=mr(e)[0]||Je(e),o=Ve(n,.35,.75);pe(i,0),oe(i,{nod:12*o,lean:4*o}),Ae(i,e,s?[r]:[]),Zt(i,r,s,he.castleWrist,{x:-30*s}),s&&i.putAway("squire_quill"),s>.4&&(i.holdUpright("castle",r,[0,0,.12]),io(i)),Ke(i,"amused",o)}const bn={high:[1,-.25,2.92],sign:[.5,-.25,3],signWaggle:.1,drawer:[1.16,-.4,1.66],drop:.12,binoculars:[.24,-.8,2.36],sweep:30,torch:[1.1,-.55,1.88],torchSweep:.16,corner:[1,-.42,1.36],lift:.3,crouch:.6,peekLean:34},aw=(i,e,t)=>i.map((n,s)=>Vt(n,e[s],t)),Ea=i=>i.putAway(...[...Et].filter(e=>!ya.has(e)));function Ms(i,e,t,n,s={}){const r=Je(e);Ae(i,e,t?[r]:[]),Zt(i,r,t,n,s),t&&Ea(i)}const Gn={bend:.9,lean:30,nod:18,talkNod:7,ear:[1.24,.05,3.3],handsetLean:16,tilt:8,wrist:[0,-.12,.3],palm:.16};function cs(i,e=0){return i.clone().applyAxisAngle(new M(1,0,0),Nt(wt.tip)).add(new M(wt.at[0],wt.at[1],e))}const kd=i=>new M(i.x,-i.z,i.y);function zd(){const{base:i}=wt,[e,t]=[[i.depth/2,0],i.brow],n=new te(t[1],e[0]-t[0]).normalize(),s=new M(0,(e[1]+t[1])/2,(e[0]+t[0])/2).add(new M(0,n.y,n.x).multiplyScalar(lu()));return new Le().compose(s,new On().setFromEuler(new wn(Math.atan2(n.x,n.y),0,0)),new M(1,1,1))}const lu=()=>wt.base.round*.8,Hd=i=>wt.base.height+lu()+wt.base.dome*Math.max(1-(i/(wt.base.width/2))**2,0),Vo=()=>kd(new M(0,Hd(wt.cradle.apart)+wt.cradle.height+wt.handset.rest,wt.cradle.at));function cw(i){const{dial:e}=wt,t=Nt(e.first-i);return kd(new M(Math.cos(t)*e.ring,e.face*1.5,-Math.sin(t)*e.ring).applyMatrix4(zd()))}function lw(i){const e=Y[i],t=new M(0,Math.sin(Nt(Gn.handsetLean)),Math.cos(Nt(Gn.handsetLean))),n=new M(e,0,0),s=new Le().makeBasis(t,n.clone().cross(t),n),r=new wn().setFromRotationMatrix(s,"ZYX");return{along:t,turn:{x:Dn.radToDeg(r.x),y:Dn.radToDeg(r.y),z:Dn.radToDeg(r.z)}}}function uw(i){const e=ce.phone_call,t=lt(i,...e.drop),n=lt(i,...e.settle),s=n>0&&n<1?Math.sin(Math.PI*e.wobbles*n)*(1-n)**2:0,r=lt(i,...e.goes),o=lt(i,...e.poof);return{here:r<.5,above:e.above*(1-t*t),squash:e.squash*s,puff:i>=e.goes[0]?r:o<1?.3+.7*o:null}}function hw(i,e,t){const n=ce.phone_call,s=Ut(t,n.frames),r=Je(e),o=r==="l"?"r":"l",a=Math.max(Te(s,n.reach)*(1-Te(s,n.lift)),Te(s,n.finger)*(1-Te(s,n.back)),Te(s,[n.hang[0],(n.hang[0]+n.hang[1])/2])*(1-Te(s,[n.hang[1],n.goes[0]]))),c=Te(s,n.lift)*(1-Te(s,[n.hang[0],n.hang[0]+(n.hang[1]-n.hang[0])*.7])),l=lt(s,...n.talk),u=Gn.bend*a;$i(i,u),pe(i,0),oe(i,{lean:Gn.lean*a,nod:Gn.nod*a+Gn.talkNod*Math.sin(Math.PI*n.nods*l)**2,tilt:Y[r]*Gn.tilt*c}),i.putAway(...Et),Ae(i,e,[r,o]);const{handset:h}=wt,f=lw(r),[d,g,_]=Gn.ear,m=new M(Y[r]*d,g,_).applyMatrix4(i.matrix("head")).clone().addScaledVector(f.along,-h.length/2),v=cs(Vo()),y=s>=n.reach[1]&&s<n.hang[1]?1:Te(s,n.reach)*(1-Te(s,[n.hang[1],n.goes[0]])),x=new M(0,0,-1).lerp(new M(-Y[r],0,0),c).normalize(),P=v.clone().lerp(m,c).addScaledVector(x,-Gn.palm);_t(i,r,y,i.withinReach(r,P,.97),new M(1,.4,-.6));const A=s>=n.reach[1]&&s<n.hang[1],E=new M(1,0,0).lerp(f.along,c).normalize();if(A){const V=i.rig.along.get(`hand_${r}`).clone().transformDirection(i.matrix(`hand_${r}`));i.aim(`hand_${r}`,V.lerp(f.along,c).normalize())}const R=A&&i.grip(r,[0,0,0]).applyMatrix4(i.matrix(`hand_${r}`)).addScaledVector(x,Gn.palm),b=A?R.clone().addScaledVector(E,-h.length/2):cs(Vo().add(new M(-h.length/2,0,-h.drop-h.end[1])));A?(i.holdUpright("telephone_handset",r,[0,0,0],{x:f.turn.x*c+wt.tip*(1-c),y:f.turn.y*c,z:f.turn.z*c}),i.props.get("telephone_handset").at=R.clone().applyMatrix4(i.matrix(`hand_${r}`).clone().invert())):i.standProp("telephone_handset",cs(Vo(),u),{x:wt.tip});const S=n.turn*Te(s,n.dial)*(1-Te(s,n.back)),I=Te(s,n.finger)*(1-Te(s,n.back)),B=cs(cw(n.turn*Te(s,n.dial))).add(new M(...Gn.wrist));_t(i,o,I,i.withinReach(o,B,.97),new M(-1,.2,-.6)),Ke(i,"amused",l>0&&l<1?1:0);const O=uw(s),k=O.puff??0;if(k>0&&k<1&&(i.standProp("telephone_poof",cs(new M(0,0,wt.base.height/2+(s<n.goes[0]?n.above:0)),u)),Object.assign(i.props.get("telephone_poof"),{puff:k})),!O.here){i.props.delete("telephone_handset");return}const K=new M(0,0,O.above);i.standProp("telephone",cs(new M,u).add(K),{x:wt.tip}),Object.assign(i.props.get("telephone"),{squash:O.squash,dial:S}),A||i.props.get("telephone_handset").at.add(K).add(new M(0,0,-O.squash*Vo().z)),i.standProp("telephone_cord",[0,0,u]);const W=new M(0,0,-u),q=A?b:b.add(K);Object.assign(i.props.get("telephone_cord"),{from:cs(new M(-Y[r]*wt.base.width*.4,.25,wt.base.height*.3)).add(K).sub(W),to:q.sub(W)})}function fw(i,e,t){const n=ce.ask_sign,s=Ut(t,n.frames),r=Te(s,n.raise)*(1-Te(s,n.lower)),o=Re(lt(s,...n.waggle),n.waggles)*Ve(s,...n.waggle),[a,c,l]=bn.sign;pe(i,0),oe(i,{nod:-10*r,tilt:4*o}),Ms(i,e,r,[a+bn.signWaggle*o,c,l]),Ke(i,"worried",r)}const Yn={at:[0,-.74,2.02],across:.4,closed:.08,apart:.6,elbow:[1,.4,-.6],nod:16,lineNod:4,scan:12,sweep:.6};function dw(i,e,t){const n=ce.scroll,s=Ut(t,n.frames),r=Te(s,n.raise)*(1-Te(s,n.lower)),o=Te(s,n.unrolls)*(1-Te(s,n.rolls)),a=lt(s,n.unrolls[1],n.rolls[0]);pe(i,0),oe(i,{lean:3*r}),i.putAway(...Et),Ae(i,e,r?Object.keys(Y):[]);const c=Je(e),[l,u,h]=Yn.at;for(const[_,p]of Object.entries(Y)){const m=h+(_===c?1:-1)*Vt(Yn.closed,Yn.apart,o)/2,v=new M(l+p*Yn.across,u,m);r&&_t(i,_,r,i.withinReach(_,i.carried(v),.97),new M(...Yn.elbow))}const f=Math.min(Math.floor(a*n.lines),n.lines-1),d=a*n.lines-f,g=Yn.scan*(1-2*Te(d,[0,Yn.sweep])+2*Te(d,[Yn.sweep,1]));i.face("head",{x:(Yn.nod+Yn.lineNod*f)*o,z:g*o}),Ke(i,"reading",o),r&&pw(i,c,r===1?c==="l"?"r":"l":null,o)}function pw(i,e,t,n){const s=l=>i.grip(l,[0,0,0]).applyMatrix4(i.matrix(`hand_${l}`)),r=s(e),o=t?s(t):r.clone().add(new M(0,0,-jd.rolled)),a=r.clone().add(o).multiplyScalar(.5);t&&(r.x=o.x=a.x);const c=i.matrix("root").clone().invert();i.standProp("report_scroll",a.clone().applyMatrix4(c).toArray()),Object.assign(i.props.get("report_scroll"),{top:r.sub(a),bottom:o.sub(a),open:n})}function mw(i,e,t){const n=ce.file_card,s=Ut(t,n.frames),r=Te(s,n.reach)*(1-Te(s,n.back)),[o,a,c]=bn.drawer;pe(i,0),oe(i,{lean:10*r,nod:14*r}),Ms(i,e,r,[o,a,c-bn.drop*Te(s,n.filed)])}const Ec={sink:2.1,hop:.75,leap:1};function gw(i,e,t){const n=ce.pack_box,{into:s,out:r}=Il(n,t),o=Ve(s,...n.hop),a=Te(s,n.into)*(1-Te(r,[n.pops,n.pops+.2])),c=Ve(r,...n.leap);i.lift("root",{z:Ec.hop*o-Ec.sink*a+Ec.leap*c}),pe(i,0),oe(i,{lean:6*o,nod:12*a-10*c}),En(i,e,0,60*o+120*c),Zi(i,.7*o+.6*c),i.putAway(...Et),Ke(i,"amused",c)}function _w(i,e,t){const n=ce.press,{into:s,out:r}=Il(n,t),o=Te(s,[.2,.55])*(1-Te(r,[.2,.5]));pe(i,0),oe(i,{nod:-8*o}),En(i,e,0,140*o),i.putAway(...Et),i.shutEyes(1-.8*Te(s,n.squashes)*(1-Te(r,n.frees)))}function xw(i,e,t){const{held:n,into:s,out:r}=Il(ce.vacuum,t),[o,a,c]=bn.torch;pe(i,0),oe(i,{lean:8,nod:14,turn:-Y[Je(e)]*14}),Ms(i,e,s*(1-r),[o,a,c-.12*Re(n??0,2)],{x:-10})}const Di={intro:18,hold:12,outro:6,fps:12,taps:6,tap:18,point:[1.25,-.45,1.75],bounce:.14,wiggle:7,sparkle:.25};function vw(i,e,t){const{intro:n,hold:s,outro:r,taps:o,tap:a,point:c,bounce:l,wiggle:u,sparkle:h}=Di,f=t*(n+s+r),d=f<n?Math.sin(Math.PI*f/n):0,g=f<n?ne(f/n,.7,1):1-ne((f-n-s)/r,0,1),_=f>=n&&f<n+s?(f-n)/s:null,p=_===null?0:Math.abs(Math.sin(2*Math.PI*_)),m=Re(f/n,o);i.lift("root",{z:l*p}),pe(i,0),oe(i,{lean:6*g,nod:14*g+4*p,twist:u*(_===null?d*m:Re(_,2))}),i.posture==="stand"&&(i.turn("foot_l",{x:a*d*Math.max(m,0)}),i.turn("foot_r",{x:a*d*Math.max(-m,0)})),Ae(i,e,g?[...e.free]:[]);for(const y of e.free)Zt(i,y,g,[c[0],c[1],c[2]+.1*p*Y[y]],{x:40});g&&Ea(i);const v=Math.min(f/4,1)*(1-lt(f,n+s,n+s+r));i.starEyes(v*(1+h*Math.abs(Re(f/6))))}function yw(i,e,t){const n=ce.fume,s=Ut(t,n.frames),r=Ve(s,n.crushed[0],n.crushed[1]+.06),o=Te(s,[n.mad[0],n.mad[0]+.06])*(1-Te(s,[n.mad[1],1])),a=Re(lt(s,...n.mad),n.stamps/2);$i(i,.14*r),i.lift("root",{z:.12*o*Math.abs(a)}),pe(i,0),oe(i,{lean:16*r+6*o,nod:28*r+10*o,tilt:5*o*Re(s,14)}),Ae(i,e,o?[...e.free]:[]);for(const c of e.free)Kt(i,c,o,{y:40,z:-25,bend:95});if(i.posture==="stand")for(const[c,l]of[["l",1],["r",-1]]){const u=o*Math.max(l*a,0);i.turn(`thigh_${c}`,{x:-34*u,y:l*18*u}),i.turn(`shin_${c}`,{x:52*u})}r>o?Ke(i,"worried",r):Ke(i,"angry",o)}const $n={frames:36,fps:12,head:18,body:5,up:10},Tc=(i,e)=>(t,n,s)=>{const r=Ut(s,$n.frames),o=ne(r,.08,.25)*(1-ne(r,.75,.92));oe(t,{twist:i*$n.body*o,turn:i*$n.head*o,nod:-e*$n.up*o}),Ae(t,n)},Cl={frames:6,fps:20},Cn={frames:48,fps:12,trip:[0,.14],down:[.05,.11],bounce:[.11,.18],shake:[.3,.58],shakes:3,up:[.62,.8],hop:[.8,.96],drop:.74};function Mw(i,e,t){const n=Ut(t,Cn.frames),s=ne(n,...Cn.down)*(1-ne(n,...Cn.up)),r=Ve(n,...Cn.trip),o=Re(lt(n,...Cn.shake),Cn.shakes)*Ve(n,...Cn.shake),a=Ve(n,...Cn.hop);if(i.lift("root",{z:-Cn.drop*s+.1*Ve(n,...Cn.bounce)+.16*a}),i.posture==="stand")for(const c of Object.keys(Y))i.turn(`shin_${c}`,{x:90*s});oe(i,{lean:12*s+10*r*(1-s),nod:12*s,turn:26*o}),En(i,e,0,100*r*(1-s)+60*a,8*r),i.putAway(...Et),a>.1?Ke(i,"amused",a):Ke(i,s>.5?"worried":"startled",Math.max(s,r))}const Ac={hands:[.8,.18],lean:-7,nod:-3};function Sw(i,e,t){pe(i,t),oe(i,{lean:Ac.lean,nod:Ac.nod+2*Re(t)});const[n,s]=Ac.hands;Ae(i,e,[...e.free]);for(const r of e.free)_t(i,r,1,i.withinReach(r,new M(Y[r]*n,s,Ni.floor),.97),new M(1,.6,.2)),i.face(`hand_${r}`,{x:-80});e.free.size&&Ea(i),i.swing(.6*Re(t))}function bw(i,e,t){const n=Re(t);pe(i,0),oe(i,{lean:8,nod:-12}),En(i,e,0,110+20*n),Zi(i,.6+.2*n)}const ps={at:[.3,-.8,2.45],across:1.5,low:1.1,high:3.4,swats:4,giggle:4};function ww(i){if(!i.at)return null;const e=Math.min(Math.max((i.at.x-.5)*Qn,-1.5),ps.across),t=Math.min(Math.max(jr+(.5-i.at.y)*Qn,ps.low),ps.high);return new M(e,ps.at[1],t)}function Ew(i,e,t){const n=t*ps.swats,s=ww(i),r=s?s.x*Y.l>0?"l":"r":Math.floor(n)%2?"l":"r",o=Math.sin(Math.PI*(n%1));pe(i,t),oe(i,{tilt:ps.giggle*Math.sin(2*Math.PI*n*2),nod:-3}),i.putAway(...Et),Ae(i,e,Object.keys(Y));for(const a of Object.keys(Y)){const[c,l,u]=ps.at,h=a===r&&s?i.withinReach(a,s,.95):new M(Y[a]*c,l,u);_t(i,a,a===r?o:.25,h,new M(1,-.4,-.3))}i.squeezeEyes(1)}const Go={up:[1.2,-.3,2.85],down:[.95,-.25,1.3],sway:12,bounce:.18};function Tw(i,e,t){const{beats:n}=ce.disco,s=t*n,r=Math.floor(s)%2?1:-1,o=Math.sin(Math.PI*Math.min(s%1*3,1)*.5),a=Te(t,[0,.06])*(1-Te(t,[.94,1]));pe(i,t),oe(i,{tilt:r*Go.sway*o*a,nod:-4}),i.putAway(...Et),Ae(i,e,Object.keys(Y));for(const c of Object.keys(Y)){const l=Y[c],[u,h,f]=l===r?Go.up:Go.down;_t(i,c,a,new M(l*u,h,f),new M(1,-.3,l===r?.2:-.6))}Ki(i,Go.bounce*Math.abs(Math.sin(Math.PI*s))*a),Ke(i,"amused",a)}const Rc={trigger:[.5,-.4,1.7],fore:[.12,-.45,1.85],behind:[.45,.45,1.45]};function Aw(i,e,t){const n=ce.bug_shot,s=(n.draw[0]+n.draw[1])/2,r=Te(t,[n.draw[0],s])*(1-Te(t,[s,n.draw[1]])),o=Te(t,[s,n.draw[1]])*(1-Te(t,[n.drops[0]+.05,n.drops[0]+.2])),a=Math.min(Math.max((t-n.shots[0])/(n.shots[1]-n.shots[0]),0),1)*n.count,c=t>n.shots[0]&&t<n.shots[1]?Math.max(0,1-a%1*3):0,l=Je(e),u=Y[l];pe(i,t),oe(i,{twist:-u*25*o,lean:4*o-5*c}),i.putAway(...Et),Ae(i,e,Object.keys(Y));const h=(f,d=u)=>new M(d*f[0],f[1],f[2]);r>o?_t(i,l,r,h(Rc.behind),new M(1,.5,-.5)):_t(i,l,o,h(Rc.trigger),new M(1,-.2,-.4)),_t(i,l==="l"?"r":"l",o,h(Rc.fore),new M(-1,-.4,-.4)),Ke(i,"amused",o)}const Rw=[.42,-.55,1.55],Cw=[.45,.45,1.45];function Pw(i,e,t){const n=ce.pogo,s=Te(t,[n.draw[0],n.draw[1]*.5])*(1-Te(t,[n.draw[1]*.5,n.draw[1]])),r=Te(t,[n.draw[1]*.6,n.draw[1]])*(1-Te(t,n.release)),o=ep(tp(),(t-n.bounces[0])/(n.bounces[1]-n.bounces[0])),a=t>n.bounces[0]&&t<n.bounces[1]?1-Math.sin(Math.PI*o.s):0;pe(i,t),oe(i,{lean:6*r,nod:-6*r}),i.putAway(...Et),Ae(i,e,Object.keys(Y));const[c,l,u]=Rw,[h,f,d]=Cw;for(const g of Object.keys(Y)){const _=Y[g];g==="r"&&s>r?_t(i,g,s,new M(_*h,f,d),new M(1,.5,-.5)):_t(i,g,r,new M(_*c,l,u),new M(1,-.2,-.4))}Ki(i,.35*a*r),Ke(i,"amused",r)}const Lw=[ce.rope_swing.ties*Qn/2,-.1,2.6];function Iw(i,e,t){const n=np(t)/ce.rope_swing.sway;pe(i,t),oe(i,{lean:-5*n,nod:-4}),i.putAway(...Et);const[s,r,o]=Lw;Ae(i,e,Object.keys(Y));for(const a of Object.keys(Y))_t(i,a,1,i.carried(new M(Y[a]*s,r,o)),new M(1,0,-.4)),i.face(`hand_${a}`,{z:-Y[a]*90});i.swing(1.2*n),Ke(i,"amused")}function Dw(i,e,t){const n=Re(t);pe(i,t),oe(i,{nod:-6,tilt:3*n}),En(i,e,0,150),i.putAway(...Et),Zi(i,.15,6*n),Ke(i,"amused")}function Nw(i,e,t){const n=bn.sweep*Re(t,ce.binoculars.sweep);oe(i,{twist:n,nod:-4});const s=Je(e),[r,o,a]=bn.binoculars,c=new M(Y[s]*r,o,a).applyAxisAngle(new M(0,0,1),Nt(n));Ms(i,e,1,[Y[s]*c.x,c.y,c.z],{x:-60})}function Uw(i,e,t){const n=Dd(t),[s,r,o]=bn.torch;pe(i,0),oe(i,{lean:10,nod:18,turn:-Y[Je(e)]*20}),Ms(i,e,1,[s,r,o-bn.torchSweep*n],{x:-10}),Ke(i,"reading")}function Ow(i,e,t){const n=ce.peek_under,s=Te(t,[0,n.lift[0]+.1])*(1-Te(t,[n.down[1],1])),r=Te(t,n.lift)*(1-Te(t,n.down)),o=Te(t,n.peek)*(1-Te(t,n.down));$i(i,bn.crouch*s),pe(i,0),oe(i,{lean:bn.peekLean*s,nod:14*s+10*o,turn:-Y[Je(e)]*24*o,tilt:8*o});const[a,c,l]=bn.corner;Ms(i,e,s,[a,c,l+bn.lift*r]),Ke(i,"reading",o)}function Fw(i,e,t){const n=Je(e),s=Y[n],[r,o,a]=Qo;pe(i,t),oe(i,{lean:2,nod:rn.nod/2+2*Re(t),tilt:-s*rn.tilt*.7}),cu(i,e,1,[r,o,a+.03*Math.max(Re(t,2),0)]),Sd(i,n,1),i.holdLaptop(),i.glanceEyes(rn.glance[0],-s*rn.glance[1])}function Bw(i,e,t){const{u:n,ready:s}=Fn(t,z.greetingFrames),r=Ve(n,.3,.75);pe(i,0),oe(i,{lean:-4*s,nod:-10*s}),Ms(i,e,s,aw([.7,-.62,2.34],[.3,-.84,2.38],r),{x:-40}),i.shutEyes(1-.6*r)}function kw(i,e,t){const{back:n}=i.sky??{back:0};i.lift("root",{y:Oi.step*n,z:Oi.hop*Math.sin(Math.PI*n)}),pe(i,t),oe(i,{lean:-Oi.lean*n});const s=Je(e);Ae(i,e,[s]),Md(i,s,t),Ea(i),Ke(i,"amused")}const uf={sit:{under:Sc,over:fS},lounge:{under:Sc,over:uS},composed:{under:Sc,over:hS},walk:{under:bd,over:wd}},Ge=["stand","sit","lounge","composed","walk"],Mt=["stand"],hf=["hang"],Wo=["sit","lounge"],zw=["stand","sit","walk"],ff=5,zE=[{name:"idle",frames:24,fps:8,loops:!0,leaves:8,postures:Ge,pose:Sa},{name:"nod",frames:10,fps:12,loops:!1,postures:Ge,pose:jM},{name:"hand_rub",frames:ce.hand_rub.frames,fps:ce.hand_rub.fps,loops:!1,postures:Ge,pose:$M},{name:"ponder",frames:ce.ponder.frames,fps:ce.ponder.fps,loops:!1,ownLook:!0,postures:Ge,pose:yc(ce.ponder)},{name:"think_cloud",frames:ce.think_cloud.frames,fps:ce.think_cloud.fps,loops:!1,ownLook:!0,postures:Ge,pose:yc(ce.think_cloud)},{name:"got_it",frames:ce.got_it.frames,fps:ce.got_it.fps,loops:!1,ownLook:!0,postures:Ge,pose:yc(ce.got_it)},{name:"shake",frames:12,fps:12,loops:!1,postures:Ge,pose:KM},{name:"wave",frames:12,fps:12,loops:!0,postures:Ge,pose:ZM},{name:"celebrate",frames:12,fps:10,loops:!0,postures:Mt,pose:tS},{name:"sleep",frames:z.yawnFrames+zr,intro:z.yawnFrames,leaves:zr,fps:6,loops:!0,postures:Ge,marks:{mark:"Z",frames:[[z.yawnFrames,z.yawnFrames+zr]]},pose:nS},{name:"walk",frames:12,fps:12,loops:!0,interruptible:!0,postures:Mt,pose:iS},{name:"walk_in",frames:40,fps:12,loops:!1,postures:Mt,pose:vS},{name:"run_in",frames:28,fps:12,loops:!1,postures:Mt,pose:yS},{name:"pull_ups",frames:24,fps:10,loops:!0,postures:Mt,pose:MS},{name:"hang_l",frames:24,fps:8,loops:!0,leaves:8,postures:hf,pose:ef("l")},{name:"hang_r",frames:24,fps:8,loops:!0,leaves:8,postures:hf,pose:ef("r")},{name:"enter",frames:36,fps:12,loops:!1,postures:Mt,pose:ZS},{name:"exit",frames:28,fps:12,loops:!1,postures:Mt,pose:JS},{name:"search",frames:80,fps:10,loops:!0,postures:Ge,pose:tb},{name:"read",frames:Al,fps:ft.fps,loops:!0,intro:ft.intro,outro:ft.outro,leaves:ft.pageEvery,postures:Ge,pose:sb},{name:"write",frames:la,intro:z.intro,outro:z.outro,leaves:z.hold,fps:z.fps,loops:!0,postures:Ge,pose:mb},{name:"waiting",frames:Rl,intro:nn.intro,outro:nn.outro,leaves:nn.hold,fps:z.fps,loops:!0,postures:["stand","sit"],pose:cb},{name:"compacting",frames:la,intro:z.intro,outro:z.outro,leaves:z.hold,fps:z.compactFps,loops:!0,postures:Ge,pose:gb},{name:"yawn",frames:z.yawnFrames,fps:z.fps,loops:!1,postures:Ge,pose:Fd},{name:"rest",frames:Rt.frames,fps:Rt.fps,loops:!1,postures:Mt,marks:{mark:"♪",frames:Rt.tunes.map(i=>i.map(e=>e*Rt.frames))},pose:hb},{name:"whistle",frames:z.pastimeFrames,fps:z.fps,loops:!1,postures:Ge,voices:["coach"],pose:lb},{name:"phone_call",frames:ce.phone_call.frames,fps:ce.phone_call.fps,loops:!1,postures:Mt,pose:hw},{name:"sip",frames:z.pastimeFrames,fps:z.fps,loops:!1,postures:Ge,voices:["colleague"],pose:fb},{name:"headphones",frames:z.pastimeFrames,fps:z.fps,loops:!1,postures:Ge,voices:["homie"],pose:db},{name:"shield_polish",frames:z.pastimeFrames,fps:z.fps,loops:!1,postures:Ge,voices:["squire"],pose:pb},{name:"bow",frames:z.greetingFrames,fps:z.fps,loops:!1,postures:Ge,voices:["butler"],pose:_b},{name:"salute",frames:z.greetingFrames,fps:z.fps,loops:!1,postures:Ge,voices:["squire"],pose:xb},{name:"startled",frames:z.hopFrames,fps:z.fps,loops:!1,postures:Ge,pose:vb},{name:"stumble",frames:z.stumbleFrames,fps:z.fps,loops:!1,postures:["walk"],pose:yb},{name:"glance",frames:z.greetingFrames,fps:z.fps,loops:!1,postures:Ge,pose:Mb},{name:"work",frames:sn.blows*sn.blowFrames,fps:sn.fps,loops:!0,postures:["stand","sit"],pose:bb},{name:"inspect",frames:Rn.frames,fps:Rn.fps,loops:!0,postures:["stand"],pose:wb},{name:"point",frames:12,fps:8,loops:!0,postures:Ge,pose:Pb},{name:"watch",frames:8,fps:8,loops:!0,cuts:!0,postures:["stand","sit"],pose:Ab},{name:"push",frames:hn.intro+hn.stride,intro:hn.intro,fps:hn.fps,loops:!0,legs:!0,ownLook:!0,postures:["walk","stand"],pose:Cb},{name:"jump",frames:16,fps:20,loops:!1,postures:Mt,pose:Lb},{name:"tickle_swat",frames:24,fps:16,loops:!1,cuts:!0,ownLook:!0,postures:Ge,pose:Ew},{name:"disco",frames:ce.disco.frames,fps:ce.disco.fps,loops:!1,ownLook:!0,postures:Mt,pose:Tw},{name:"bug_shot",frames:ce.bug_shot.frames,fps:ce.bug_shot.fps,loops:!1,postures:Mt,pose:Aw},{name:"pogo",frames:ce.pogo.frames,fps:ce.pogo.fps,loops:!1,postures:Mt,pose:Pw},{name:"fall",frames:12,fps:12,loops:!1,interruptible:!0,postures:Mt,pose:Ub},{name:"backflip",frames:22,fps:20,loops:!1,postures:Mt,pose:Nb},{name:"land",frames:Cl.frames,fps:Cl.fps,loops:!1,postures:Mt,pose:Ob},{name:"type",frames:24,fps:8,loops:!0,leaves:8,least:ff,aside:!0,postures:Wo,pose:pS},{name:"joy",frames:ce.joy.frames,fps:ce.joy.fps,loops:!1,postures:Ge,pose:mS},{name:"dismay",frames:28,fps:10,loops:!1,postures:Ge,pose:gS},{name:"polish",frames:40,fps:12,loops:!1,postures:Ge,voices:["butler"],pose:ab},{name:"stretch",frames:24,fps:8,loops:!1,postures:Ge,pose:_S},{name:"squire_chase",frames:24,fps:12,loops:!1,postures:Mt,pose:Fb},{name:"pointed",frames:20,fps:10,loops:!1,postures:Mt,pose:Gb},{name:"hat_tip",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["butler"],pose:Xb},{name:"monocle",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["butler"],pose:Yb},{name:"toast",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["butler"],pose:jb},{name:"shaka",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["homie"],pose:$b},{name:"shades",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["homie"],pose:Kb},{name:"fire",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["homie"],pose:Zb},{name:"thumbs_up",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["colleague"],pose:Jb},{name:"peer",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["colleague"],pose:Qb},{name:"thanks",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,pose:ew},{name:"party_popper",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["coach"],pose:tw},{name:"flex",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["coach"],pose:nw},{name:"trophy",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["coach"],pose:iw},{name:"sword",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["squire"],pose:sw},{name:"shield_up",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["squire"],pose:rw},{name:"castle",frames:he.frames,fps:he.fps,loops:!1,postures:Ge,voices:["squire"],pose:ow},{name:"ask_sign",frames:ce.ask_sign.frames,fps:ce.ask_sign.fps,loops:!1,postures:Ge,pose:fw},{name:"scroll",frames:ce.scroll.frames,fps:ce.scroll.fps,loops:!1,ownLook:!0,postures:Ge,pose:dw},{name:"file_card",frames:ce.file_card.frames,fps:ce.file_card.fps,loops:!1,postures:Mt,pose:mw},{name:"pack_box",frames:ce.pack_box.intro+ce.pack_box.hold+ce.pack_box.outro,intro:ce.pack_box.intro,outro:ce.pack_box.outro,leaves:ce.pack_box.hold,fps:ce.pack_box.fps,loops:!0,postures:Mt,pose:gw},{name:"press",frames:ce.press.intro+ce.press.hold+ce.press.outro,intro:ce.press.intro,outro:ce.press.outro,leaves:ce.press.hold,fps:ce.press.fps,loops:!0,postures:Ge,pose:_w},{name:"vacuum",frames:ce.vacuum.intro+ce.vacuum.hold+ce.vacuum.outro,intro:ce.vacuum.intro,outro:ce.vacuum.outro,leaves:ce.vacuum.hold,fps:ce.vacuum.fps,loops:!0,postures:Mt,pose:xw},{name:"eager",frames:Di.intro+Di.hold+Di.outro,intro:Di.intro,outro:Di.outro,leaves:Di.hold,fps:Di.fps,loops:!0,holds:!0,postures:Mt,pose:vw},{name:"fume",frames:ce.fume.frames,fps:ce.fume.fps,loops:!1,cuts:!0,postures:Mt,pose:yw},{name:"look_left",frames:$n.frames,fps:$n.fps,loops:!1,postures:Ge,pose:Tc(-1,0)},{name:"look_right",frames:$n.frames,fps:$n.fps,loops:!1,postures:Ge,pose:Tc(1,0)},{name:"look_up",frames:$n.frames,fps:$n.fps,loops:!1,postures:Ge,pose:Tc(0,1)},{name:"tumble",frames:Cn.frames,fps:Cn.fps,loops:!1,postures:Mt,pose:Mw},{name:"ledge_sit",frames:32,fps:8,loops:!0,leaves:8,postures:Wo,pose:Sw},{name:"hop_up",frames:8,fps:16,loops:!0,interruptible:!0,cuts:!0,postures:Mt,pose:bw},{name:"rope_swing",frames:ce.rope_swing.intro+ce.rope_swing.hold+ce.rope_swing.outro,intro:ce.rope_swing.intro,outro:ce.rope_swing.outro,leaves:ce.rope_swing.hold,fps:ce.rope_swing.fps,loops:!0,postures:Wo,pose:Iw},{name:"chute",frames:ce.chute.frames,fps:ce.chute.fps,loops:!0,interruptible:!0,cuts:!0,postures:Mt,pose:Dw},{name:"binoculars",frames:ce.binoculars.frames,fps:ce.binoculars.fps,loops:!0,postures:zw,pose:Nw},{name:"flashlight",frames:ce.flashlight.frames,fps:ce.flashlight.fps,loops:!0,postures:Mt,pose:Uw},{name:"peek_under",frames:ce.peek_under.frames,fps:ce.peek_under.fps,loops:!0,postures:Mt,pose:Ow},{name:"type_ponder",frames:ce.type_ponder.frames,fps:ce.type_ponder.fps,loops:!0,leaves:8,least:ff,aside:!0,ownLook:!0,postures:Wo,pose:Fw},{name:"wipe_brow",frames:z.greetingFrames,fps:z.fps,loops:!1,postures:Ge,pose:Bw},{name:"wave_up",frames:12,fps:12,loops:!0,cuts:!0,postures:["stand","sit"],pose:kw}],Vd=`
    #include <common>
    #include <skinning_pars_vertex>
    attribute vec3 hullNormal;
    uniform float push;
    uniform float openness;
    uniform float eyeMiddle;
    uniform float eyeHeight;
    uniform vec2 eyeShift;
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
        transformed.y = eyeMiddle + (transformed.y - eyeMiddle) * openness;
        transformed.xy += eyeShift * eyeHeight;
        #include <skinning_vertex>
        transformed += normalize(objectNormal) * push;
        worldNormal = normalize(mat3(modelMatrix) * objectNormal);
        worldPosition = (modelMatrix * vec4(transformed, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(transformed, 1.0);
    }
`,Hw=`
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
`,Cc={pitch:.1,gap:.24,dark:.3},Vw=`
    uniform vec3 colour;
    uniform vec3 light;
    uniform vec3 shade;
    uniform float litFrom;
    uniform vec3 glow;
    uniform float lit;
    uniform float across;
    uniform float open;
    uniform float flash;
    uniform float core;
    uniform vec2 middle;
    uniform vec2 extent;
    uniform float pitch;
    uniform float gap;
    uniform float dark;
    varying vec3 worldNormal;
    varying vec3 worldPosition;
    varying vec3 localPosition;

    void main() {
        vec3 normal = normalize(worldNormal);
        if (!gl_FrontFacing) {
            normal = -normal;
        }
        vec3 shaded = colour * mix(shade, vec3(1.0), step(litFrom, dot(normal, light)));
        vec2 from = abs(localPosition.xy - middle) / extent;
        float band = step(from.x, across) * step(from.y, open);
        vec2 cell = fract(worldPosition.xy / pitch);
        float pixel = step(gap, cell.x) * step(gap, cell.y);
        float centre = max(1.0 - length(from), 0.0);
        vec3 lit = glow * mix(dark, 1.0, pixel);
        vec3 screen = mix(lit + (vec3(1.0) - glow) * core * centre * centre * pixel, vec3(1.0), flash);
        gl_FragColor = vec4(mix(shaded * (1.0 - step(0.001, lit + flash) * 0.6), screen, band * max(lit, flash)), 1.0);
        #include <colorspace_fragment>
    }
`;function Gw(i){const e=uu(i);e.fragmentShader=Vw;const t=new pn().setFromBufferAttribute(i.geometry.attributes.position),n=t.getCenter(new M),s=t.getSize(new M).multiplyScalar(.5);return Object.assign(e.uniforms,{glow:{value:new M},lit:{value:0},across:{value:0},open:{value:0},flash:{value:0},core:{value:op.core},middle:{value:new te(n.x,n.y)},extent:{value:new te(s.x,s.y)},pitch:{value:Cc.pitch},gap:{value:Cc.gap},dark:{value:Cc.dark}}),e}const Ww=`
    uniform vec3 colour;

    void main() {
        gl_FragColor = vec4(colour, 1.0);
        #include <colorspace_fragment>
    }
`;function Gd(i,e){const t=i.geometry.attributes.position;let n=0,[s,r]=[1/0,-1/0];for(let o=0;o<t.count;o++)n+=t.getY(o)/t.count,[s,r]=[Math.min(s,t.getY(o)),Math.max(r,t.getY(o))];return{push:{value:e/i.getWorldScale(new M).x},openness:{value:1},eyeMiddle:{value:n},eyeHeight:{value:r-s},eyeShift:{value:new te}}}function uu(i){const{r:e,g:t,b:n}=i.material.color;return new Zn({vertexShader:Vd,fragmentShader:Hw,side:Mn,uniforms:{...Gd(i,0),colour:{value:new M(e,t,n)},light:{value:DM.clone().normalize().applyMatrix4(dr)},shade:{value:El},litFrom:{value:NM},bulbAt:{value:new M},bulbGlow:{value:new M},bulbFalloff:{value:$s.falloff}}})}function Wd(i){return new Zn({vertexShader:Vd,fragmentShader:Ww,side:fn,defines:{HULL:""},uniforms:{...Gd(i,OM),colour:{value:UM}}})}const Xw=-.5;function hu(i){const e=i.attributes.position,t=Array.from({length:e.count},(o,a)=>new M().fromBufferAttribute(i.attributes.normal,a)),n=new Map,s=o=>`${e.getX(o).toFixed(5)},${e.getY(o).toFixed(5)},${e.getZ(o).toFixed(5)}`;for(let o=0;o<e.count;o++){const a=n.get(s(o))??[];a.push(o),n.set(s(o),a)}const r=new Float32Array(e.count*3);for(let o=0;o<e.count;o++){const a=new M;for(const c of n.get(s(o)).filter(l=>t[o].dot(t[l])>Xw))a.add(t[c]);a.normalize().toArray(r,o*3)}i.setAttribute("hullNormal",new $t(r,3))}function Bs(i,e){const t=new Set;for(const n of i.filter(s=>e.has(s.userData.item)))t.add(new pn().setFromObject(n).getCenter(new M).x>=0?"l":"r");return t}function qw(i){const e=[];i.traverse(a=>a.isBone&&e.push(a));const t=new Map(e.map(a=>[a.name,a.parent.isBone?a.parent.name:""])),n=new Map(e.map(a=>[a.name,a.matrixWorld.clone()])),s=new Map(e.map(a=>[a.name,aa(new M().setFromMatrixPosition(a.matrixWorld))])),r=new Map(e.map(a=>[a.name,new M().setFromMatrixColumn(a.matrixWorld,1).transformDirection(Ma)])),o=[];return i.traverse(a=>{!a.isSkinnedMesh||!a.name.startsWith("eye_")||!a.userData.hull||o.push(aa(new pn().setFromBufferAttribute(a.geometry.attributes.position).getCenter(new M).applyMatrix4(a.matrixWorld)))}),{bones:e,order:e.map(a=>a.name),parents:t,rest:n,heads:s,along:r,eyes:o}}async function Yw(i){const e=await Lc.raw(i);if(e.ok)return e.arrayBuffer();const t=await Lc.raw(`${i}.txt`).then(n=>n.text());return Uint8Array.from(atob(t),n=>n.charCodeAt(0)).buffer}async function HE(i,e,t){const[n,s]=await Promise.all([Yw(i),Lc.raw(e).then(a=>a.json())]),r=t==="bare",o=new Set((r?[]:s.outfits[t]).flatMap(a=>s.assets[a].hide_base_parts));return $w(n,t,LM,a=>!o.has(a.name)&&!(r&&a.userData.item))}const jw={butler:qy};async function $w(i,e,t,n=()=>!0){const r=(await new Yy().setDRACOLoader(new RM().setDecoderPath(t)).parseAsync(i,"")).scene;r.updateMatrixWorld(!0);const o=[];r.traverse(E=>E.isSkinnedMesh&&o.push(E));const a=(jw[e]??(E=>E))(o),c={materials:[],shapes:[],hearts:[],stars:[],squeezed:[],over:[]},l=[],u=[];for(const E of a){E.visible=n(E)&&!VM.has(E.userData.item)&&E.userData.item!==xc&&E.userData.item!==vc,hu(E.geometry);const R=new ql(E.geometry,Wd(E));if(R.bind(E.skeleton,E.bindMatrix),R.visible=E.visible,E.userData.hull=R,R.userData.item=E.userData.item,R.frustumCulled=E.frustumCulled=!1,E.material=E.name===Pc?Gw(E):uu(E),E.name===Pc&&l.push(E.material),E.name===Pc&&u.push(R),E.parent.add(R),R.position.copy(E.position),R.quaternion.copy(E.quaternion),R.scale.copy(E.scale),E.name.startsWith("eye_")){E.material.userData.colour=E.material.uniforms.colour.value.toArray(),c.materials.push(E.material,R.material),c.shapes.push(E,R),c.hearts.push(Ur(E,vE,ME)),c.stars.push(Ur(E,SE,wE)),c.squeezed.push(Object.assign(Ur(E,EE,Ll),{userData:{way:E.name==="eye_l"?-1:1}}));for(const[b,{geometry:S,glows:I}]of Object.entries($d))c.over.push(Object.assign(Ur(E,S,Ll),{userData:{name:b,halo:!1}})),I&&c.over.push(Object.assign(TE(E,S),{userData:{name:b,halo:!0}}))}}const h=a.filter(E=>E.visible),f=Bs(h,ya),d=a.filter(E=>E.userData.item===xc&&n(E)),g=a.filter(E=>E.userData.item===vc&&n(E)),_={voice:e,level:Bs(h,vd),busy:f,carried:Bs(h,Et),free:new Set(Object.keys(Y).filter(E=>!f.has(E))),tablet:Bs(d,new Set([xc])),cloth:Bs(g,new Set([vc])),shield:Bs(h,new Set(["squire_shield"]))},p=Zw(),m=dE(),v=iE();r.add(p,m,...v.values());const y={bulbAt:{value:new M},bulbGlow:{value:new M}};r.traverse(E=>{var R,b;return((b=(R=E.material)==null?void 0:R.uniforms)==null?void 0:b.bulbGlow)&&Object.assign(E.material.uniforms,y)});const x=E=>E.flatMap(R=>[R,R.userData.hull]),P=h.filter(E=>Et.has(E.userData.item)),A=x(h.filter(E=>E.userData.item));return{scene:r,rig:qw(r),stance:_,eyes:c,screens:l,visorHulls:u,laptop:p,book:m,propByName:v,props:[...v.values()],stowable:A,tablet:x(d),cloth:x(g),inHand:x(P),bulbLight:y}}const Kw={width:1.7,depth:.62,thickness:.1,open:105},Lr={base:4672082,lid:2829880,screen:1776932,edge:11120056,mark:6186185},qi=(i,e)=>{const t=new kt(i,new on({color:e,side:Mn}));return t.frustumCulled=!1,t};function Zw(){const{width:i,depth:e,thickness:t,open:n}=Kw,s=(h,f,d,g)=>{const _=qi(new Ct(f,d,g),h);return _.add(new Kr(new _a(_.geometry),new _s({color:Lr.edge}))),_},r=s(Lr.base,i,t,e);r.position.set(0,t/2,-e/2);const o=s(Lr.lid,i,e,t);o.position.set(0,e/2,t/2);const a=qi(new Jn(i*.88,e*.82),Lr.screen);a.position.set(0,e/2,-.002);const c=qi(new Yi(e*.12,20),Lr.mark);c.position.set(0,e/2,t+.002);const l=new Bt;l.position.y=t,l.rotation.x=Nt(n-90),l.add(o,a,c);const u=new Bt;return u.matrixAutoUpdate=!1,u.visible=!1,u.add(r,l),u}const ks={lights:[.144,.267,.389,.511],light:.047,vents:[.633,.711,.789,.867],vent:[.033,.49]},zs={front:1842725,top:2895673,side:1184536,vent:329224,edge:4869724};function Jw(i){const e=Qi.width*i,t=Math.asin(Qi.top/Qi.width),n=(Qi.height-Qi.top)*i/Math.cos(t)/Qi.units,[s,r,o]=[zs.side,zs.top,zs.front].map(h=>new on({color:h})),a=[],c=Array.from({length:Qi.units},(h,f)=>{const d=new kt(new Ct(e,n,e),[s,s,r,s,o,s]);d.add(new Kr(new _a(d.geometry),new _s({color:zs.edge}))),d.position.set(0,n*(f+.5),-e/2);const g=(_,p)=>(_.position.set(e*(p-.5),0,e/2+.002),d.add(_),_);return a.push(...ks.lights.map(_=>g(new kt(new Yi(e*ks.light,12),new on),_))),ks.vents.forEach(_=>g(qi(new Jn(e*ks.vent[0],n*ks.vent[1]),zs.vent),_)),d}),l=new Bt;l.rotation.x=t,l.add(...c);const u=new Ev;return u.add(l),u.updateMatrixWorld(!0),{scene:u,lights:a,bounds:new pn().setFromObject(l)}}function Qw(i,e,t){const n=new ze(zs.front);i.lights.forEach((s,r)=>{const o=new ze().setRGB(...sp[e],Ht);s.material.color.copy(n.clone().lerp(o,rp(e,t,r%ks.lights.length)))})}const eE={radius:.52,rim:.08,handle:.5,grip:.07},Xo={rim:2829880,lens:13625087,handle:4672082,edge:11120056},tE=40;function nE(i){const{radius:e,rim:t,handle:n,grip:s}=eE,r=(l,u,h={})=>{const f=new kt(l,new on({color:u,side:Mn,...h}));return f.frustumCulled=!1,f},o=r(new Xi(e,t,12,48),Xo.rim);o.position.y=n/2+e,o.add(new Kr(new _a(new Yi(e+t,48)),new _s({color:Xo.edge})));const a=r(new Yi(e,48),Xo.lens,{transparent:!0,opacity:.35,depthWrite:!1});a.position.y=n/2+e;const c=r(new bt(s,s*1.2,n,16),Xo.handle);i.add(c,o,a)}const De={width:.82,height:1.2,cover:.055,pages:.06,spine:.18,inset:.035,open:160,tilt:8,gripHeight:.02,gripSide:.1,closedGrip:.2,gripBack:.6,leaf:.004,curl:2,pageSegments:12,pageBow:.24,lines:5,lineWidth:.004},ls={cover:6514417,spine:3487563,pages:15986399,paper:16776175,edge:2303282,rule:13024940},Xd=i=>Nt((180-De.open*i)/2);function Pl(i,e){const t=Y[i],n=i==="l"?1:e;return new M(t*De.width*n,De.gripHeight,De.cover/2).applyAxisAngle(new M(0,1,0),t*Xd(e)).add(new M(t*De.spine/2,0,0))}function qd(i){const e=Pl("l",i).sub(Pl("r",i)).normalize(),t=new M(0,1,0);return new Le().makeBasis(e,t,e.clone().cross(t))}function Yd(i){return new Le().makeRotationX(Nt(De.tilt)).multiply(qd(i).invert())}function Hi(i,e){const t=qd(e),n=new M().setFromMatrixColumn(t,0),s=new M().setFromMatrixColumn(t,2);return Pl(i,e).addScaledVector(n,Y[i]*(De.gripSide+De.closedGrip*(1-e))).addScaledVector(s,-De.gripBack)}const tn={pen:{radius:.027,length:.58,tip:.08,sides:12,markerScale:1.8,pencilSides:6,bandScale:1.05,bandAt:1/3},feather:{at:1/4,points:[[0,0],[-.12,.18],[-.08,.42],[.03,.6],[.14,.34],[.1,.12]]},paper:{width:1.58,depth:.54,thickness:.012,count:4,spread:.04,tabletLayers:3,screenWidth:.91,screenDepth:.85,screenLift:2},whistle:{body:[.13,.1,.16],mouthpiece:[.08,.04,.15],mouthAt:[0,.01,-.12]},cloth:{width:.35,depth:.26,thickness:.02},hammer:{handleRadius:.06,handleLength:1.2,gripFrom:.15,head:[.55,.22,.22],sides:10,tilt:45},straw:{radius:.03,length:.7,head:[.045,.16]},colours:{ink:2566454,silver:11120056,paper:15986399,white:16052973,accent:6514417,pencil:14069867,handle:9067051,straw:15255146}};function iE(){const i=new Map,e=d=>{const g=new Bt;return g.name=d,g.visible=!1,g.matrixAutoUpdate=!1,i.set(d,g),g},t=(d,g,_,p,m=[0,0,0])=>{const v=qi(_,p);return v.name=`${d.name}_${g}`,v.position.set(...m),d.add(v),v},{pen:n,paper:s,cloth:r,colours:o}=tn;for(const d of Object.values(Nd)){const g=e(d),_=d==="writing_marker",p=d==="writing_pencil",m=n.radius*(_?n.markerScale:1);t(g,"barrel",new bt(m,m,n.length,p?n.pencilSides:n.sides),p?o.pencil:o.ink);const v=t(g,"nib",new mi(m,n.tip,n.sides),o.silver,[0,-(n.length+n.tip)/2,0]);if(v.rotation.z=Math.PI,t(g,"band",new bt(m*n.bandScale,m*n.bandScale,n.tip/2,n.sides),o.accent,[0,n.length*n.bandAt,0]),d==="writing_quill"){const x=new Un;x.moveTo(...tn.feather.points[0]);for(const P of tn.feather.points.slice(1))x.lineTo(...P);x.closePath(),t(g,"feather",new Mi(x),o.white,[0,n.length*tn.feather.at,0])}const y=new It;y.name="tip",y.position.y=-n.length/2-n.tip,g.add(y),g.userData.tip=y}for(const d of["papers","writing_paper","writing_tablet"]){const g=e(d),_=d==="writing_tablet",p=d==="papers"?s.count:1;g.userData.sheets=[];for(let m=0;m<p;m++){const v=t(g,`sheet_${m}`,new Ct(s.width,s.thickness*(_?s.tabletLayers:1),s.depth),_?o.ink:o.paper,[0,m*s.thickness,0]);g.userData.sheets.push(v)}_&&t(g,"screen",new Ct(s.width*s.screenWidth,s.thickness,s.depth*s.screenDepth),o.accent,[0,s.thickness*s.screenLift,0])}i.get("papers").userData.shape=({phase:d})=>{const g=ne(d,0,.3)*(1-ne(d,.8,1));i.get("papers").userData.sheets.forEach((_,p)=>{_.position.x=s.spread*p*(1-g),_.rotation.y=s.spread*p*(1-g)})};const a=e("hand_whistle");t(a,"body",new Ct(...tn.whistle.body),o.accent),t(a,"mouthpiece",new Ct(...tn.whistle.mouthpiece),o.silver,tn.whistle.mouthAt);const{hammer:c}=tn,l=e("work_hammer");t(l,"handle",new bt(c.handleRadius,c.handleRadius,c.handleLength,c.sides),o.handle,[0,c.handleLength/2-c.gripFrom,0]),t(l,"head",new Ct(...c.head),o.silver,[0,c.handleLength-c.gripFrom,0]);const{straw:u}=tn,h=e("straw");t(h,"stalk",new bt(u.radius,u.radius,u.length,6),o.straw,[0,u.length/2,0]),t(h,"seeds",new mi(...u.head,6),o.pencil,[0,u.length+u.head[1]/2,0]),nE(e("magnifying_glass"));const f=e("polishing_cloth");return t(f,"fold",new Ct(r.width,r.thickness,r.depth),o.white),lE(e,t),aE(e("telephone"),e("telephone_handset"),e("telephone_cord"),e("telephone_poof")),rE(e("light_bulb")),sE(e("report_scroll")),i}const jd={roller:.045,length:1.25,knob:.075,wound:.11,unwound:.06,turns:1.5,width:1,bow:.06,curl:.08,rows:10,columns:16,rolled:.22,colours:{wood:9067051,knob:7029280,back:14469020,wound:15128238}};function sE(i){const{roller:e,length:t,knob:n,wound:s,unwound:r,turns:o,width:a,bow:c,curl:l,rows:u,columns:h,colours:f}=jd,d=["top","bottom"].map(m=>{const v=new Bt;v.name=`${i.name}_${m}`,i.add(v);const y=Ft(v,"roller",new bt(e,e,t,14),f.wood);y.rotation.z=Math.PI/2;for(const P of[-1,1])Ft(v,`knob_${P>0?"l":"r"}`,new ur(n,14,10),f.knob,[P*t/2,0,0]);const x=Ft(v,"wound",new bt(1,1,a,18),f.wound);return x.rotation.z=Math.PI/2,{group:v,sleeve:x,rod:y}}),g=new Jn(a,1,h,u),_=Ft(i,"parchment",g,f.back),p=m=>new M(m.x,m.z,-m.y);i.userData.shape=({top:m,bottom:v,open:y})=>{const[x,P]=[p(m),p(v)],A=Vt(s,r,y);d.forEach(({group:R,sleeve:b,rod:S},I)=>{R.position.copy(I?P:x),b.scale.set(A,1,A),S.rotation.x=(I?-1:1)*o*2*Math.PI*y}),_.visible=y>.02;const E=g.attributes.position;for(let R=0;R<=u;R++){const b=R/u,S=x.clone().lerp(P,b);for(let I=0;I<=h;I++){const B=I/h-.5,O=c*Math.sin(Math.PI*b)*y-l*(2*B)**4;E.setXYZ(R*(h+1)+I,S.x+B*a,S.y,S.z+A+O)}}E.needsUpdate=!0,g.computeVertexNormals(),g.setAttribute("hullNormal",g.attributes.normal.clone())}}const $s={at:[.95,-.25,4.05],globe:.36,neck:.15,base:[.15,.22],threads:3,filament:.14,wire:.014,halo:1.7,strength:1.4,falloff:.6,colours:{glass:14937587,glassLit:16769658,base:12041414,contact:3816775,filament:5988203,filamentLit:16774338,warm:[1,.82,.42]}};function rE(i){const{globe:e,neck:t,base:n,threads:s,filament:r,wire:o,halo:a,colours:c}=$s,l=new Bt;l.name=i.name,i.add(l);const u=[[0,e*1.95],[e*.55,e*1.85],[e*.92,e*1.45],[e,e],[e*.88,e*.55],[t*1.2,e*.18],[t,0]].map(([P,A])=>new te(P,A)).reverse(),h=Ft(l,"glass",new Zr(u,28),c.glass);h.material.uniforms.shade={value:El.clone()};const[f,d]=n;Ft(l,"base",new bt(f,f*.92,d,20),c.base,[0,-d/2,0]);for(let P=0;P<s;P++)Ft(l,`thread_${P}`,new Xi(f*1.02,d/(s*4),6,20),c.base,[0,-d*((P+.6)/s),0]).rotation.x=Math.PI/2;Ft(l,"contact",new ur(f*.45,12,8),c.contact,[0,-d,0]);const g=new ga([[-r,e*.6],[-r*.5,e*1.15],[0,e*.95],[r*.5,e*1.15],[r,e*.6]].map(([P,A])=>new M(P,A,0))),_=new Bt;l.add(_);const m=[new sr(g,24,o*1.4,6),...[-1,1].map(P=>new sr(new nd(new M(P*r,.02,0),new M(P*r,e*.6,0)),1,o,6))].map(P=>{const A=new kt(P,new on({color:c.filament,depthTest:!1}));return A.renderOrder=2,A.frustumCulled=!1,_.add(A),A}),v=new kt(new Yi(e*a,32),new on({color:new ze(...c.warm),transparent:!0,depthWrite:!1}));v.position.set(0,e,-e*1.2),v.frustumCulled=!1,l.add(v);const y=new ze(c.glass),x=new ze(c.glassLit);i.userData.shape=({size:P,lit:A})=>{l.scale.setScalar(Math.max(P,.001));const E=y.clone().lerp(x,A);h.material.uniforms.colour.value.set(E.r,E.g,E.b),h.material.uniforms.shade.value.copy(El).lerp(new M(1.25,1.25,1.25),A);for(const R of m)R.material.color.set(c.filament).lerp(new ze(c.filamentLit),A);v.visible=A>0,v.material.opacity=.35*A}}const wt={at:[0,-.92],tip:10,base:{width:1.2,narrow:.18,depth:.85,height:.88,brow:[.08,.8],round:.16,dome:.06},dial:{plate:.42,face:.045,marks:.37,radius:.31,holes:10,hole:.05,ring:.22,first:60,spread:290,label:.11},cradle:{at:-.14,apart:.3,post:.055,height:.13},handset:{length:1.4,grip:.085,drop:.15,end:[.2,.15],rest:.06},cord:.022,coils:14,coil:.05,poof:{puffs:11,puff:.24,from:.5,to:.95},colours:{body:11022893,face:15853263,wheel:2829880,hole:16052973,mark:2829880,label:16052973,grille:2829880,smoke:15131630}};function Ft(i,e,t,n,s=[0,0,0]){const r=new kt(t,new on({color:n}));hu(t),r.material=uu(r);const o=new kt(t,Wd(r));return o.frustumCulled=r.frustumCulled=!1,r.add(o),r.name=`${i.name}_${e}`,r.position.set(...s),i.add(r),r}function oE(){const{width:i,narrow:e,depth:t,height:n,brow:s,round:r,dome:o}=wt.base,a=new Un;a.moveTo(-t/2+r*.5,0),a.lineTo(t/2-r*.5,0),a.quadraticCurveTo(t/2,0,t/2-r*.2,r*.5),a.lineTo(s[0]+r*.3,s[1]-r*.4),a.quadraticCurveTo(s[0]-r*.2,n,s[0]-r*1.6,n),a.lineTo(-t/2+r*1.8,n),a.quadraticCurveTo(-t/2+r*.1,n,-t/2+r*.1,n-r*1.6),a.lineTo(-t/2,r*.5),a.quadraticCurveTo(-t/2,0,-t/2+r*.5,0);const c=i-2*r,l=new Jr(a,{depth:c,bevelEnabled:!0,bevelThickness:r,bevelSize:lu(),bevelSegments:6,curveSegments:12});l.rotateY(-Math.PI/2).translate(c/2,0,0);const u=l.attributes.position;for(let h=0;h<u.count;h++){const[f,d]=[u.getX(h),Math.max(u.getY(h),0)];u.setX(h,f*(1-e*d/n)),u.setY(h,u.getY(h)+o*(d/n)**2*Math.max(1-(f/(i/2))**2,0))}return l.computeVertexNormals(),l}function aE(i,e,t,n){const{base:s,dial:r,cradle:o,colours:a}=wt,c=new Bt;c.name=i.name,i.add(c),Ft(c,"base",oE(),a.body);const l=new Bt;l.name=i.name,l.matrixAutoUpdate=!1,l.matrix.copy(zd()),c.add(l),Ft(l,"dial_plate",new bt(r.plate,r.plate,r.face,40),a.face,[0,r.face/2,0]);for(let R=0;R<r.holes;R++){const b=Nt(r.first+r.spread*R/(r.holes-1));Ft(l,`number_${R}`,new Ct(.03,r.face*.6,.045),a.mark,[Math.cos(b)*r.marks,r.face,-Math.sin(b)*r.marks])}const u=new Bt;u.name=i.name,u.position.y=r.face,l.add(u),Ft(u,"dial_wheel",new bt(r.radius,r.radius,r.face*.6,36),a.wheel,[0,r.face*.3,0]);for(let R=0;R<r.holes;R++){const b=Nt(r.first+r.spread*R/(r.holes-1));Ft(u,`hole_${R}`,new bt(r.hole,r.hole,r.face*.7,12),a.hole,[Math.cos(b)*r.ring,r.face*.4,-Math.sin(b)*r.ring])}Ft(l,"dial_label",new bt(r.label,r.label,r.face*1.6,24),a.label,[0,r.face,0]);const h=Nt(r.first+r.spread+22);Ft(l,"dial_stop",new Ct(.04,r.face*2.2,.1),a.label,[Math.cos(h)*(r.radius+.02),r.face*1.2,-Math.sin(h)*(r.radius+.02)]);for(const R of[1,-1]){const b=Hd(o.apart)+o.height;Ft(c,`prong_${R}`,new bt(o.post,o.post*1.4,o.height+.04,12),a.body,[R*o.apart,b-o.height/2-.02,o.at]),Ft(c,`saddle_${R}`,new Xi(wt.handset.grip*1.1,o.post*.45,8,14,Math.PI),a.body,[R*o.apart,b+wt.handset.grip*.4,o.at]).rotation.set(0,Math.PI/2,Math.PI)}const f=new Bt;f.name=e.name,e.add(f);const{length:d,grip:g,drop:_,end:p}=wt.handset,m=new ga([[-d/2,-_],[-d/2+.24,.02],[0,.06],[d/2-.24,.02],[d/2,-_]].map(([R,b])=>new M(R,b,0)));Ft(f,"handle",new sr(m,32,g,12),a.body);for(const[R,b]of[["ear",1],["mouth",-1]]){const S=new Bt;S.name=e.name,S.position.set(b*d/2,-_,0),S.rotation.z=b*.22,f.add(S),Ft(S,`${R}_piece`,new ur(p[0],24,16),a.body,[0,-p[1]*.45,0]).scale.set(1,p[1]/p[0],1),Ft(S,`${R}_grille`,new bt(p[0]*.62,p[0]*.62,.025,20),a.grille,[0,-p[1]*.92,0])}i.userData.shape=({squash:R,dial:b})=>{c.scale.set(1+R/2,1-R,1+R/2),u.rotation.y=Nt(b)};const v=Ft(t,"cord",df(new M,new M(1,0,0)),a.body);t.userData.shape=({from:R,to:b})=>{v.geometry.dispose(),v.geometry=v.children[0].geometry=df(R,b),hu(v.geometry)};const{puffs:y,puff:x,from:P,to:A}=wt.poof,E=Array.from({length:y},(R,b)=>Ft(n,`puff_${b}`,new eu(x*(.75+.5*(b*7%5)/4),1),a.smoke));n.userData.shape=({puff:R})=>{E.forEach((b,S)=>{const I=2*Math.PI*S/y,B=P+(A-P)*Math.sqrt(R);b.position.set(Math.cos(I)*B,Math.sin(I*2)*B*.35,Math.sin(I)*B*.6),b.scale.setScalar(Math.max(Math.sin(Math.PI*R),.001))})}}function df(i,e){const{cord:t,coils:n,coil:s}=wt,r=h=>new M(h.x,h.z,-h.y),[o,a]=[r(i),r(e)],c=o.clone().lerp(a,.5).add(new M(0,-.35*o.distanceTo(a),0)),l=new Zl(o,c,a),u=Array.from({length:n*8+1},(h,f)=>{const d=f/(n*8),g=l.getPoint(d),_=l.getTangent(d),p=new M(0,1,0).cross(_).normalize(),m=_.clone().cross(p).normalize(),v=2*Math.PI*n*d;return g.addScaledVector(p,Math.cos(v)*s).addScaledVector(m,Math.sin(v)*s)});return new sr(new ga(u),n*16,t,6)}const cE={monocle:{radius:.2,tube:.028,chain:.55,chainWidth:.012},flute:{base:.13,baseDepth:.025,stem:.022,stemLength:.35,rim:.12,bottom:.05,bowl:.4,fill:.27},shades:{lens:[.56,.34,.05],apart:.37,bridge:[.2,.05,.05],temple:[.04,.04,.7],shine:[.2,.035,.01]},flame:{outer:[.17,.55],inner:[.09,.32],sides:12,flickers:7},finger:{radius:.09,length:.22,splay:.6},popper:{mouth:.14,length:.45,sides:12},confetti:{count:18,size:.08,reach:1.5,fall:.9,spin:9},trophy:{base:[.38,.12,.38],stem:[.05,.08,.22],rim:.3,bottom:.12,cup:.38,handle:.12,handleTube:.03},sword:{grip:[.035,.26],guard:[.42,.06,.07],blade:[.09,1.3,.025],point:.15,pommel:.06},castle:{wall:[.6,.3,.25],crenel:[.1,.08,.25],tower:[.11,.5],roof:[.15,.24],gate:[.14,.18],pole:.24,flag:.14},colours:{hat:2697787,band:16052973,gold:15251530,glass:14542574,champagne:15848058,lens:1316380,flame:16742938,fire:16765503,hand:16116959,wood:8014374,stone:13222580,confetti:[6514417,15251530,15681391,448160,1149618]}};function lE(i,e){const{monocle:t,flute:n,shades:s,flame:r,finger:o,popper:a,confetti:c,trophy:l,sword:u,castle:h,colours:f}=cE,d=tn.colours.ink,g=tn.colours.silver,_=tn.colours.accent,p=i("top_hat");e(p,"crown",hd(),f.hat),e(p,"band",fd(),new ze(...un.satin).getHex());const m=i("monocle");e(m,"ring",new Xi(t.radius,t.tube,8,24),f.gold),e(m,"lens",new Yi(t.radius,24),f.glass),e(m,"chain",new bt(t.chainWidth,t.chainWidth,t.chain,6),f.gold,[t.radius*.7,-t.radius*.7-t.chain/2,0]);const v=i("champagne_flute");e(v,"base",new bt(n.base,n.base,n.baseDepth,16),f.glass,[0,-n.stemLength/2,0]),e(v,"stem",new bt(n.stem,n.stem,n.stemLength,8),f.glass),e(v,"bowl",new bt(n.rim,n.bottom,n.bowl,16,1,!0),f.glass,[0,(n.stemLength+n.bowl)/2,0]),e(v,"wine",new bt(n.rim*.9,n.bottom*.9,n.fill,16),f.champagne,[0,n.stemLength/2+n.fill/2+.01,0]);const y=i("sunglasses");for(const q of[1,-1])e(y,`lens_${q}`,new Ct(...s.lens),f.lens,[q*s.apart,0,0]),e(y,`temple_${q}`,new Ct(...s.temple),d,[q*(s.apart+s.lens[0]/2),s.lens[1]/4,-s.temple[2]/2]),e(y,`shine_${q}`,new Ct(...s.shine),tn.colours.white,[q*s.apart-s.lens[0]/5,s.lens[1]/4,s.lens[2]/2]).rotation.z=.5;e(y,"bridge",new Ct(...s.bridge),d,[0,s.lens[1]/4,0]);const x=i("flame"),P=e(x,"outer",new mi(r.outer[0],r.outer[1],r.sides),f.flame,[0,r.outer[1]/2,0]),A=e(x,"inner",new mi(r.inner[0],r.inner[1],r.sides),f.fire,[0,r.inner[1]/2,.03]);x.userData.shape=({phase:q,size:V})=>{const se=1+.18*Math.sin(2*Math.PI*r.flickers*q)+.08*Math.sin(2*Math.PI*2.3*r.flickers*q);x.scale.set(V*(2-se),V*se,V*(2-se)),P.rotation.z=A.rotation.z=.12*Math.sin(2*Math.PI*1.7*r.flickers*q)};const E=()=>new Jl(o.radius,o.length,4,8);e(i("thumb"),"thumb",E(),f.hand,[0,o.length/2+o.radius,0]);const R=i("shaka");for(const q of[1,-1])e(R,`finger_${q}`,E(),f.hand,[q*o.length*.6,o.length/2,0]).rotation.z=-q*o.splay;const b=i("party_popper");e(b,"cone",new mi(a.mouth,a.length,a.sides,1,!0),_,[0,a.length/2,0]).rotation.x=Math.PI,e(b,"rim",new Xi(a.mouth,.02,6,a.sides),f.gold,[0,a.length,0]).rotation.x=Math.PI/2;const S=Array.from({length:c.count},(q,V)=>{const se=e(b,`confetti_${V}`,new Jn(c.size,c.size),f.confetti[V%f.confetti.length]),me=V*2.39996,Se=.25+.5*(V*7%c.count)/c.count;return se.userData.way=new M(Math.sin(Se)*Math.cos(me),Math.cos(Se),Math.sin(Se)*Math.sin(me)),se});b.userData.shape=({burst:q})=>{for(const[V,se]of S.entries()){se.visible=q>0&&q<1;const me=c.reach*Math.sqrt(q);se.position.set(se.userData.way.x*me,a.length+se.userData.way.y*me-c.fall*q*q,se.userData.way.z*me),se.rotation.set(c.spin*q+V,c.spin*q*.7,V)}};const I=i("trophy");e(I,"base",new Ct(...l.base),f.wood,[0,-l.stem[2]-l.base[1]/2,0]),e(I,"stem",new bt(l.stem[0],l.stem[1],l.stem[2],12),f.gold,[0,-l.stem[2]/2,0]),e(I,"cup",new bt(l.rim,l.bottom,l.cup,16),f.gold,[0,l.cup/2,0]);for(const q of[1,-1])e(I,`handle_${q}`,new Xi(l.handle,l.handleTube,6,12),f.gold,[q*l.rim,l.cup*.6,0]);const B=i("sword");e(B,"grip",new bt(u.grip[0],u.grip[0],u.grip[1],8),f.wood),e(B,"pommel",new ur(u.pommel,8,6),f.gold,[0,-u.grip[1]/2-u.pommel/2,0]),e(B,"guard",new Ct(...u.guard),f.gold,[0,u.grip[1]/2+u.guard[1]/2,0]),e(B,"blade",new Ct(...u.blade),g,[0,u.grip[1]/2+u.guard[1]+u.blade[1]/2,0]);const O=e(B,"point",new mi(u.blade[0]/Math.SQRT2,u.point,4),g,[0,u.grip[1]/2+u.guard[1]+u.blade[1]+u.point/2,0]);O.rotation.y=Math.PI/4,O.scale.z=u.blade[2]/u.blade[0];const k=i("castle");e(k,"wall",new Ct(...h.wall),f.stone,[0,h.wall[1]/2,0]);for(const q of[-1,0,1])e(k,`crenel_${q}`,new Ct(...h.crenel),f.stone,[q*h.wall[0]/3,h.wall[1]+h.crenel[1]/2,0]);for(const q of[1,-1])e(k,`tower_${q}`,new bt(h.tower[0],h.tower[0],h.tower[1],12),f.stone,[q*h.wall[0]/2,h.tower[1]/2,0]),e(k,`roof_${q}`,new mi(...h.roof,12),_,[q*h.wall[0]/2,h.tower[1]+h.roof[1]/2,0]);e(k,"gate",new Jn(...h.gate),d,[0,h.gate[1]/2,h.wall[2]/2+.005]);const K=h.tower[1]+h.roof[1];e(k,"pole",new bt(.01,.01,h.pole,4),d,[h.wall[0]/2,K+h.pole/2,0]);const W=new Un;W.moveTo(0,0),W.lineTo(h.flag,-h.flag/3),W.lineTo(0,-h.flag*2/3),W.closePath(),e(k,"flag",new Mi(W),f.gold,[h.wall[0]/2,K+h.pole,0])}function uE(i,{bone:e,frame:t,at:n,turn:s}){const r=n.clone().applyMatrix4(i.get(e));return dr.clone().multiply(ki(r)).multiply(new Le().extractRotation(i.get(t))).multiply(Gs(s.x||0,s.y||0,s.z||0)).multiply(Ma)}function hE(i,e){const{bulbAt:t,bulbGlow:n}=i.bulbLight;n.value.set(...$s.colours.warm).multiplyScalar($s.strength*e.bulbLit),e.bulbLit&&t.value.setFromMatrixPosition(i.propByName.get("light_bulb").matrix).add(new M(0,$s.globe,0))}function fE(i,e,t){var n,s;for(const[r,o]of i.propByName){const a=e.props.get(r);o.visible=!!a,a&&(o.matrix.copy(uE(t,a)),o.matrixWorldNeedsUpdate=!0,(s=(n=o.userData).shape)==null||s.call(n,a))}}function dE(){const i=(l,u,h,f,d)=>{const g=qi(new Ct(h,f,d),u);return g.name=l,g.add(new Kr(new _a(g.geometry),new _s({color:ls.edge}))),g},e=new Bt;e.name="reading_book",e.matrixAutoUpdate=!1,e.visible=!1;const t=i("book_spine",ls.spine,De.spine,De.height,De.cover);e.add(t);const n={},s={},r={},o={};for(const[l,u]of Object.entries(Y)){const h=new Bt;h.name=`book_hinge_${l}`,h.position.x=u*De.spine/2;const f=i(`book_cover_${l}`,ls.cover,De.width,De.height,De.cover);f.position.set(u*De.width/2,0,De.cover/2);const d=i(`book_pages_${l}`,ls.pages,De.width-De.inset,De.height-De.inset*2,De.pages);d.position.set(u*(De.width-De.inset)/2,0,-De.pages/2);for(let _=1;_<=De.lines;_++){const p=qi(new Ct(De.width-De.inset,De.lineWidth,De.lineWidth),ls.rule);p.position.set(d.position.x,-De.height/2+De.inset,-De.pages*_/(De.lines+1)),h.add(p)}h.add(f,d),e.add(h),n[l]=h,s[l]=f,r[l]=d;const g=new It;g.name=`book_grip_${l}`,e.add(g),o[l]=g}const a=qi(new Jn(De.width-De.inset,De.height-De.inset*2,De.pageSegments,1),ls.paper);a.geometry.translate(-(De.width-De.inset)/2,0,0),a.name="book_turning_page";const c=new Jf(new zt,new _s({color:ls.rule}));return c.frustumCulled=!1,a.add(c),a.userData.edge=c,e.add(a),e.userData={hinges:n,covers:s,pages:r,grips:o,leaf:a},e}function pE(i,e){const t=i.l.clone(),n=i.r.clone(),s=t.clone().sub(n).normalize(),r=new M(0,1,0).addScaledVector(s,-s.y).normalize(),o=s.clone().cross(r).normalize(),a=new Le().makeBasis(s,r,o).multiply(Yd(e)),c=t.distanceTo(n)/Hi("l",e).distanceTo(Hi("r",e)),l=Hi("l",e).add(Hi("r",e)).multiplyScalar(.5).applyMatrix4(a).multiplyScalar(c);return a.scale(new M(c,c,c)).setPosition(t.add(n).multiplyScalar(.5).sub(l))}function mE(i,e,t){const n=Xd(e);for(const[u,h]of Object.entries(Y))i.userData.hinges[u].rotation.y=h*n,i.userData.grips[u].position.copy(Hi(u,e));const s=i.userData.leaf,r=De.pages+De.leaf;s.position.set(Vt(-De.spine/2+r*Math.sin(n),De.spine/2-r*Math.sin(n),t),0,-r*Math.cos(n)),s.rotation.y=-n-Nt(De.open*e)*t,s.visible=e>0;const o=De.curl*Math.sin(Math.PI*t),a=De.width-De.inset,c=s.geometry.attributes.position;for(let u=0;u<2;u++)for(let h=0;h<=De.pageSegments;h++){const f=1-h/De.pageSegments,d=u*(De.pageSegments+1)+h,g=De.pageBow*Math.sin(Math.PI*t)*f*f;c.setX(d,(o?-a*Math.sin(o*f)/o:-a*f)-Math.sin(s.rotation.y)*g),c.setZ(d,(o?a*(1-Math.cos(o*f))/o:0)+Math.cos(s.rotation.y)*g)}c.needsUpdate=!0;const l=[];for(let u=0;u<=De.pageSegments;u++)l.push(new M().fromBufferAttribute(c,u));for(let u=De.pageSegments;u>=0;u--)l.push(new M().fromBufferAttribute(c,De.pageSegments+1+u));s.userData.edge.geometry.setFromPoints(l)}const gE=1.95,_E=.3;function xE(i){const e=a=>new M().setFromMatrixPosition(i.get(a)),t=e("thigh_l").add(e("thigh_r")).multiplyScalar(.5),n=e("shin_l").add(e("shin_r")).multiplyScalar(.5),s=n.clone().sub(t).setY(0).normalize(),r=new M(0,1,0),o=t.lerp(n,gE).addScaledVector(r,_E);return new Le().makeBasis(r.clone().cross(s),r,s).setPosition(o)}const vE=(()=>{const i=new Un;return i.moveTo(0,-.5),i.bezierCurveTo(-.16,-.3,-.5,-.16,-.5,.12),i.bezierCurveTo(-.5,.4,-.2,.5,0,.26),i.bezierCurveTo(.2,.5,.5,.4,.5,.12),i.bezierCurveTo(.5,-.16,.16,-.3,0,-.5),new Mi(i,12)})(),yE=.42,ME=new ze(1,.3,.5),SE=(()=>{const i=new Un;for(let e=0;e<10;e++){const t=e%2?.22:.55,n=Math.PI/2+e*Math.PI/5;i[e?"lineTo":"moveTo"](t*Math.cos(n),t*Math.sin(n))}return new Mi(i)})(),bE=.46,wE=new ze(1,.86,.3),EE=(()=>{const i=[[-.4,.42],[.42,0],[-.4,-.42],[-.4,-.2],[.04,0],[-.4,.2]];return new Mi(new Un(i.map(([e,t])=>new te(e,t))))})(),pf=.5,Ll=new ze(1,.94,.81),$d={cross:{geometry:new Mi([[-1,1],[1,-1]].map(([i,e])=>new Un([[-.5*i,.5],[-.5*i+.18*e,.5],[.5*i,-.5],[.5*i-.18*e,-.5]].map(([t,n])=>new te(t,n))))),size:.4,aside:0,up:0,glows:!0},tick:{geometry:new Mi(new Un([[-.5,.02],[-.32,.18],[-.12,-.04],[.36,.52],[.52,.36],[-.12,-.36]].map(([i,e])=>new te(i,e)))),size:.42,aside:0,up:0,glows:!0}};function Ur(i,e,t){const n=new pn().setFromBufferAttribute(i.geometry.attributes.position).applyMatrix4(i.matrixWorld),s=n.getCenter(new M).setZ(n.max.z+.01),r=i.skeleton.getBoneByName("head"),o=new Bt;o.matrixAutoUpdate=!1,o.matrix.copy(r.matrixWorld).invert().multiply(ki(s));const a=new kt(e,new on({color:t}));return a.frustumCulled=!1,a.visible=!1,o.add(a),r.add(o),a}const mf={size:1.45,opacity:.4};function TE(i,e){const t=Ur(i,e,Ll);return t.material.transparent=!0,t.material.depthWrite=!1,t}function AE(i,e){return Object.fromEntries(Object.keys(Y).map(t=>[t,i.grip(t,[0,0,0]).applyMatrix4(e.get(`hand_${t}`)).applyMatrix4(dr)]))}function RE(i,e,t,n){var d,g,_;const s=e.moves(t),r=n?Gy(i.rig,n.from,s,n.k,n.previous):{moves:s,settled:!0};n&&(n.settled=r.settled);const o=r.moves,a=new Map;for(const p of i.rig.bones){const m=dr.clone().multiply(o.get(p.name)).multiply(Ma).multiply(i.rig.rest.get(p.name));a.set(p.name,m),(p.parent.isBone?a.get(p.parent.name):p.parent.matrixWorld).clone().invert().multiply(m).decompose(p.position,p.quaternion,p.scale)}for(const p of i.eyes.materials)p.uniforms.openness.value=Math.max(e.eyes*(1-(((d=e.eyeShape)==null?void 0:d.strength)??0)),Tl),p.uniforms.eyeShift.value.set(...e.eyeShift),p.uniforms.light&&p.uniforms.colour.value.set(...e.eyeTint??p.userData.colour);i.laptop.visible=e.laptop,i.book.visible=!!((g=e.book)!=null&&g.visible),i.book.visible&&(mE(i.book,e.book.open,e.book.page),i.book.matrix.copy(pE(AE(e,o),e.book.open)),i.book.matrixWorldNeedsUpdate=!0);for(const p of i.tablet)p.visible=e.tablet;const c=e.laptop||e.book||e.props.size>0;for(const p of i.stowable)p.visible=!e.stowed.has(p.userData.item);for(const p of i.inHand)p.visible=!e.stowed.has(p.userData.item)&&(!c||e.keep.has(p.userData.item));fE(i,e,o),hE(i,e);for(const p of i.cloth)p.visible=e.cloth;e.laptop&&(i.laptop.matrix.copy(xE(a)),i.laptop.matrixWorldNeedsUpdate=!0);const l=e.screen??IE;for(const p of i.screens)p.uniforms.lit.value=l.glow,p.uniforms.across.value=l.across,p.uniforms.open.value=l.open,p.uniforms.flash.value=l.flash,e.screen&&p.uniforms.glow.value.set(...e.screen.colour);for(const p of i.visorHulls)p.visible=!e.screen||!!e.screen.sign;const u=l.eyes>LE,h=e.eyeShape&&!e.hearts&&!e.stars&&!e.squeezed?e.eyeShape:null;for(const p of i.eyes.shapes)p.visible=u&&!e.hearts&&!e.stars&&!e.squeezed&&!((h==null?void 0:h.strength)>=1);for(const p of i.eyes.hearts)p.visible=u&&e.hearts>0,p.scale.setScalar(yE*e.hearts);for(const p of i.eyes.stars)p.visible=u&&e.stars>0&&!e.hearts,p.scale.setScalar(bE*e.stars),p.rotation.z=1.2*(e.stars-1);for(const p of i.eyes.squeezed)p.visible=u&&e.squeezed>0&&!e.hearts&&!e.stars,p.scale.set(pf*e.squeezed*p.userData.way,pf*e.squeezed,1);const f=(_=e.screen)==null?void 0:_.sign;for(const p of i.eyes.over){const{name:m,halo:v}=p.userData;if(p.visible=u&&(h==null?void 0:h.name)===m,!p.visible)continue;const{size:y,aside:x,up:P}=$d[m],A=y*(v?mf.size:1);p.scale.set(A,A*Math.max(h.strength,Tl),1),p.position.set(x*h.way,P,v?-.004:0),f&&p.material.color.setRGB(...e.screen.colour.map(E=>(E+(1-E)*f.white)*f.lit)),v&&(p.material.opacity=mf.opacity*((f==null?void 0:f.lit)??1))}return o}const gf=.8,_f={into:.35,out:.45},Kd=({seconds:i,lasts:e})=>Te(i,[0,_f.into])*(1-Te(i,[e-_f.out,e]));function CE(i,{mood:e,seconds:t,lasts:n}){const s=Kd({seconds:t,lasts:n});if(Ad[e].hearts){const r=t%gf/gf;i.heartEyes(s*(1+.28*Ve(r,0,.3)+.14*Ve(r,.3,.55)))}else Ke(i,e,s)}const xf={share:.8,lean:.12};function PE(i,e,t){const n=((e+180)%360+360)%360-180,s=xf.lean*n,r=Dn.clamp(xf.share*n-s,-ua,ua);i.bendAbove("chest",{z:-s*t}),i.turn("neck",{z:-.3*r*t}),i.turn("head",{z:-.7*r*t})}const Pc="face_screen",LE=.05,IE={eyes:1,across:0,open:0,flash:0,glow:0},DE=i=>i!=="lounge";class VE{constructor(){const e=Qn/2;this.camera=new pa(-e,e,e,-e,gc-Kh,gc+Kh),this.camera.position.set(0,jr,gc),this.camera.lookAt(0,jr,0),this.renderer=new wv({antialias:!0,alpha:!0,preserveDrawingBuffer:!0}),this.renderer.setPixelRatio(1),this.renderer.setClearColor(0,0)}headAt(e,t){if(!t)return{x:.5,y:.3};const n=e.rig.eyes.reduce((s,r)=>s.add(r),new M).divideScalar(e.rig.eyes.length);return this.pictured(n.applyMatrix4(t.get("head")))}handAt(e,t){const n=Je(e.stance),s=n==="l"?"r":"l";return t?{...this.gripAt(e,t,n),out:Y[n],other:this.gripAt(e,t,s)}:{x:.5+Y[n]*.25,y:.6,out:Y[n],other:{x:.5-Y[n]*.25,y:.6}}}gripAt(e,t,n){const s=new M(Y[n]*ji.grip,ji.forward,0).add(e.rig.heads.get(`hand_${n}`));return this.pictured(s.applyMatrix4(t.get(`hand_${n}`)))}pictured(e){const t=e.applyMatrix4(dr).project(this.camera);return{x:(t.x+1)/2,y:(1-t.y)/2}}draw(e,t,n,s,r,{posture:o="stand",eyes:a=null,stride:c=0,blend:l=null,sky:u=null,at:h=null,open:f=1,screen:d=null,tilt:g=0}={}){var A,E;const _=new qM(e.rig,o,c);_.sky=u,_.screen=d,_.at=h,t.legs||(A=uf[o])==null||A.under(_),t.pose(_,e.stance,n/t.frames),g&&oe(_,{tilt:g}),t.legs||(E=uf[o])==null||E.over(_);const p=!DE(o),m=s+(h&&!p?Eb(_,h,s):0);f<1&&_.shutEyes(Math.min(_.eyes,f)),d&&_.shutEyes(Math.min(_.eyes,d.eyes));const v=Math.max(a?Kd(a):0,d?ip(d):0);v&&!_.gaze&&!p&&!t.ownLook&&PE(_,m,v),a&&CE(_,a),d!=null&&d.sign&&_.shapeEyes(d.sign.name,d.sign.strength);const y=RE(e,_,m,l),x=r.width*fi;this.renderer.domElement.width!==x&&this.renderer.setSize(x,x,!1),this.renderer.render(e.scene,this.camera);const P=r.getContext("2d");return P.clearRect(0,0,r.width,r.height),P.imageSmoothingQuality="high",P.filter=`blur(${IM*r.width/PM}px)`,P.drawImage(this.renderer.domElement,0,0,r.width,r.height),y}drawBlock(e,t,n,s){this.blockFor!==n&&(this.block=Jw(Qn/n)),this.blockFor=n,Qw(this.block,e,t);const r=Math.round(n*s)*fi;this.renderer.domElement.width!==r&&this.renderer.setSize(r,r,!1),this.renderer.render(this.block.scene,this.camera);const{min:o,max:a}=this.block.bounds,c=[o.x,a.x].flatMap(m=>[o.y,a.y].flatMap(v=>[o.z,a.z].map(y=>new M(m,v,y).project(this.camera)))),l=m=>(m+1)/2*r,u=Math.floor(Math.min(...c.map(m=>l(m.x))))-fi,h=Math.ceil(Math.max(...c.map(m=>l(m.x))))+fi,f=Math.floor(Math.min(...c.map(m=>r-l(m.y))))-fi,d=Math.ceil(Math.max(...c.map(m=>r-l(m.y))))+fi,g=document.createElement("canvas");g.width=Math.round((h-u)/fi),g.height=Math.round((d-f)/fi);const _=g.getContext("2d");_.imageSmoothingQuality="high",_.drawImage(this.renderer.domElement,u,f,h-u,d-f,0,0,g.width,g.height);const p=r-l(new M(0,0,0).project(this.camera).y);return{canvas:g,below:(d-p)/fi/s}}}export{bn as ACTED,z as ACTING,De as BOOK,Gn as CALL,PM as CELL,zE as CLIPS,Rr as COMPOSED,Di as EAGERNESS,Ad as EYES,$d as EYE_SHAPES,$n as GLANCE,BE as GROUND,ji as HAND,ua as HEAD_TURN,Rn as INSPECTING,Cl as LANDING,Ac as LEDGE,uf as LEGS,$s as LIGHT_BULB,_f as LOOK_EASE,Ni as LOUNGE,rn as PONDERING,qM as Posing,he as REACTING,cE as REACTION_PROPS,jd as REPORT_SCROLL,Rt as REST,Ar as RUB,Cc as SCREEN,Yn as SCROLL,hn as SHOVE,Y as SIDES,Oi as SKY,VE as Stage,wt as TELEPHONE,tn as TOOLS,xf as TOWARD_VIEWER,Cn as TUMBLE,ff as TYPING_SECONDS,nn as WAIT,sn as WORK,Nd as WRITING,kE as blowsLandAt,$w as figureOf,Rb as leanOf,rE as lightBulbOf,hE as lightFromBulb,HE as loadFigure,Kd as lookStrength,Eb as lookToward,uw as phoneArrival,sE as reportScrollOf,lS as supportsClip,aE as telephoneOf,PE as turnToViewer,DE as turnsToViewer};

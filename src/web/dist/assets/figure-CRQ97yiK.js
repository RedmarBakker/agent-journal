import{H as se,A as ie,p as ne,a as mm,b as gm,h as Ga,s as _m,o as xm,P as _f,R as vm,f as ym,G as hc,c as Ci,F as Mm,S as wm,g as bm,d as Sm,U as Ra,e as Ss,V as Em,i as Tm,T as Am,j as Rm,k as ls,L as Cm,m as Pm,n as Lm,q as Im,r as Dm}from"./main-Dy3lbDRi.js";import{e as xl}from"./tokens-BKAkHm6K.js";import"./tip-aBppuKDT.js";import"./preload-helper-Dp1pzeXC.js";/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const yh="170",Nm=0,du=1,Um=2,xf=1,Om=2,Ai=3,Ni=0,Sn=1,Pn=2,ns=0,rr=1,fu=2,pu=3,mu=4,Fm=5,ws=100,Bm=101,km=102,zm=103,Hm=104,Gm=200,Vm=201,Wm=202,Xm=203,vl=204,yl=205,qm=206,$m=207,jm=208,Ym=209,Km=210,Zm=211,Jm=212,Qm=213,e0=214,Ml=0,wl=1,bl=2,ur=3,Sl=4,El=5,Tl=6,Al=7,vf=0,t0=1,n0=2,is=0,i0=1,s0=2,r0=3,o0=4,a0=5,c0=6,l0=7,gu="attached",h0="detached",yf=300,dr=301,fr=302,Rl=303,Cl=304,Va=306,pr=1e3,Zi=1001,Ca=1002,xn=1003,Mf=1004,Qr=1005,Un=1006,xa=1007,Li=1008,Ui=1009,wf=1010,bf=1011,ho=1012,Mh=1013,Ts=1014,ri=1015,Mo=1016,wh=1017,bh=1018,mr=1020,Sf=35902,Ef=1021,Tf=1022,Xn=1023,Af=1024,Rf=1025,or=1026,gr=1027,Sh=1028,Eh=1029,Cf=1030,Th=1031,Ah=1033,va=33776,ya=33777,Ma=33778,wa=33779,Pl=35840,Ll=35841,Il=35842,Dl=35843,Nl=36196,Ul=37492,Ol=37496,Fl=37808,Bl=37809,kl=37810,zl=37811,Hl=37812,Gl=37813,Vl=37814,Wl=37815,Xl=37816,ql=37817,$l=37818,jl=37819,Yl=37820,Kl=37821,ba=36492,Zl=36494,Jl=36495,Pf=36283,Ql=36284,eh=36285,th=36286,uo=2300,fo=2301,uc=2302,_u=2400,xu=2401,vu=2402,u0=2500,d0=0,Lf=1,nh=2,f0=3200,p0=3201,If=0,m0=1,Yi="",Yt="srgb",vn="srgb-linear",Wa="linear",Nt="srgb",Us=7680,yu=519,g0=512,_0=513,x0=514,Df=515,v0=516,y0=517,M0=518,w0=519,ih=35044,Mu="300 es",Ii=2e3,Pa=2001;class Er{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,o=s.length;r<o;r++)s[r].call(this,e);e.target=null}}}const dn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let wu=1234567;const ar=Math.PI/180,_r=180/Math.PI;function $n(){const i=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(dn[i&255]+dn[i>>8&255]+dn[i>>16&255]+dn[i>>24&255]+"-"+dn[e&255]+dn[e>>8&255]+"-"+dn[e>>16&15|64]+dn[e>>24&255]+"-"+dn[t&63|128]+dn[t>>8&255]+"-"+dn[t>>16&255]+dn[t>>24&255]+dn[n&255]+dn[n>>8&255]+dn[n>>16&255]+dn[n>>24&255]).toLowerCase()}function Qt(i,e,t){return Math.max(e,Math.min(t,i))}function Rh(i,e){return(i%e+e)%e}function b0(i,e,t,n,s){return n+(i-e)*(s-n)/(t-e)}function S0(i,e,t){return i!==e?(t-i)/(e-i):0}function io(i,e,t){return(1-t)*i+t*e}function E0(i,e,t,n){return io(i,e,1-Math.exp(-t*n))}function T0(i,e=1){return e-Math.abs(Rh(i,e*2)-e)}function A0(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*(3-2*i))}function R0(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*i*(i*(i*6-15)+10))}function C0(i,e){return i+Math.floor(Math.random()*(e-i+1))}function P0(i,e){return i+Math.random()*(e-i)}function L0(i){return i*(.5-Math.random())}function I0(i){i!==void 0&&(wu=i);let e=wu+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function D0(i){return i*ar}function N0(i){return i*_r}function U0(i){return(i&i-1)===0&&i!==0}function O0(i){return Math.pow(2,Math.ceil(Math.log(i)/Math.LN2))}function F0(i){return Math.pow(2,Math.floor(Math.log(i)/Math.LN2))}function B0(i,e,t,n,s){const r=Math.cos,o=Math.sin,a=r(t/2),c=o(t/2),l=r((e+n)/2),h=o((e+n)/2),u=r((e-n)/2),d=o((e-n)/2),f=r((n-e)/2),m=o((n-e)/2);switch(s){case"XYX":i.set(a*h,c*u,c*d,a*l);break;case"YZY":i.set(c*d,a*h,c*u,a*l);break;case"ZXZ":i.set(c*u,c*d,a*h,a*l);break;case"XZX":i.set(a*h,c*m,c*f,a*l);break;case"YXY":i.set(c*f,a*h,c*m,a*l);break;case"ZYZ":i.set(c*m,c*f,a*h,a*l);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+s)}}function si(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function Pt(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const yt={DEG2RAD:ar,RAD2DEG:_r,generateUUID:$n,clamp:Qt,euclideanModulo:Rh,mapLinear:b0,inverseLerp:S0,lerp:io,damp:E0,pingpong:T0,smoothstep:A0,smootherstep:R0,randInt:C0,randFloat:P0,randFloatSpread:L0,seededRandom:I0,degToRad:D0,radToDeg:N0,isPowerOfTwo:U0,ceilPowerOfTwo:O0,floorPowerOfTwo:F0,setQuaternionFromProperEuler:B0,normalize:Pt,denormalize:si};class re{constructor(e=0,t=0){re.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6],this.y=s[1]*t+s[4]*n+s[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Qt(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),s=Math.sin(t),r=this.x-e.x,o=this.y-e.y;return this.x=r*n-o*s+e.x,this.y=r*s+o*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class ot{constructor(e,t,n,s,r,o,a,c,l){ot.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,o,a,c,l)}set(e,t,n,s,r,o,a,c,l){const h=this.elements;return h[0]=e,h[1]=s,h[2]=a,h[3]=t,h[4]=r,h[5]=c,h[6]=n,h[7]=o,h[8]=l,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,o=n[0],a=n[3],c=n[6],l=n[1],h=n[4],u=n[7],d=n[2],f=n[5],m=n[8],_=s[0],g=s[3],p=s[6],y=s[1],M=s[4],x=s[7],A=s[2],E=s[5],P=s[8];return r[0]=o*_+a*y+c*A,r[3]=o*g+a*M+c*E,r[6]=o*p+a*x+c*P,r[1]=l*_+h*y+u*A,r[4]=l*g+h*M+u*E,r[7]=l*p+h*x+u*P,r[2]=d*_+f*y+m*A,r[5]=d*g+f*M+m*E,r[8]=d*p+f*x+m*P,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],c=e[6],l=e[7],h=e[8];return t*o*h-t*a*l-n*r*h+n*a*c+s*r*l-s*o*c}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],c=e[6],l=e[7],h=e[8],u=h*o-a*l,d=a*c-h*r,f=l*r-o*c,m=t*u+n*d+s*f;if(m===0)return this.set(0,0,0,0,0,0,0,0,0);const _=1/m;return e[0]=u*_,e[1]=(s*l-h*n)*_,e[2]=(a*n-s*o)*_,e[3]=d*_,e[4]=(h*t-s*c)*_,e[5]=(s*r-a*t)*_,e[6]=f*_,e[7]=(n*c-l*t)*_,e[8]=(o*t-n*r)*_,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,s,r,o,a){const c=Math.cos(r),l=Math.sin(r);return this.set(n*c,n*l,-n*(c*o+l*a)+o+e,-s*l,s*c,-s*(-l*o+c*a)+a+t,0,0,1),this}scale(e,t){return this.premultiply(dc.makeScale(e,t)),this}rotate(e){return this.premultiply(dc.makeRotation(-e)),this}translate(e,t){return this.premultiply(dc.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<9;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const dc=new ot;function Nf(i){for(let e=i.length-1;e>=0;--e)if(i[e]>=65535)return!0;return!1}function po(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function k0(){const i=po("canvas");return i.style.display="block",i}const bu={};function eo(i){i in bu||(bu[i]=!0,console.warn(i))}function z0(i,e,t){return new Promise(function(n,s){function r(){switch(i.clientWaitSync(e,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:s();break;case i.TIMEOUT_EXPIRED:setTimeout(r,t);break;default:n()}}setTimeout(r,t)})}function H0(i){const e=i.elements;e[2]=.5*e[2]+.5*e[3],e[6]=.5*e[6]+.5*e[7],e[10]=.5*e[10]+.5*e[11],e[14]=.5*e[14]+.5*e[15]}function G0(i){const e=i.elements;e[11]===-1?(e[10]=-e[10]-1,e[14]=-e[14]):(e[10]=-e[10],e[14]=-e[14]+1)}const pt={enabled:!0,workingColorSpace:vn,spaces:{},convert:function(i,e,t){return this.enabled===!1||e===t||!e||!t||(this.spaces[e].transfer===Nt&&(i.r=Di(i.r),i.g=Di(i.g),i.b=Di(i.b)),this.spaces[e].primaries!==this.spaces[t].primaries&&(i.applyMatrix3(this.spaces[e].toXYZ),i.applyMatrix3(this.spaces[t].fromXYZ)),this.spaces[t].transfer===Nt&&(i.r=cr(i.r),i.g=cr(i.g),i.b=cr(i.b))),i},fromWorkingColorSpace:function(i,e){return this.convert(i,this.workingColorSpace,e)},toWorkingColorSpace:function(i,e){return this.convert(i,e,this.workingColorSpace)},getPrimaries:function(i){return this.spaces[i].primaries},getTransfer:function(i){return i===Yi?Wa:this.spaces[i].transfer},getLuminanceCoefficients:function(i,e=this.workingColorSpace){return i.fromArray(this.spaces[e].luminanceCoefficients)},define:function(i){Object.assign(this.spaces,i)},_getMatrix:function(i,e,t){return i.copy(this.spaces[e].toXYZ).multiply(this.spaces[t].fromXYZ)},_getDrawingBufferColorSpace:function(i){return this.spaces[i].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(i=this.workingColorSpace){return this.spaces[i].workingColorSpaceConfig.unpackColorSpace}};function Di(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function cr(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}const Su=[.64,.33,.3,.6,.15,.06],Eu=[.2126,.7152,.0722],Tu=[.3127,.329],Au=new ot().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),Ru=new ot().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);pt.define({[vn]:{primaries:Su,whitePoint:Tu,transfer:Wa,toXYZ:Au,fromXYZ:Ru,luminanceCoefficients:Eu,workingColorSpaceConfig:{unpackColorSpace:Yt},outputColorSpaceConfig:{drawingBufferColorSpace:Yt}},[Yt]:{primaries:Su,whitePoint:Tu,transfer:Nt,toXYZ:Au,fromXYZ:Ru,luminanceCoefficients:Eu,outputColorSpaceConfig:{drawingBufferColorSpace:Yt}}});let Os;class V0{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{Os===void 0&&(Os=po("canvas")),Os.width=e.width,Os.height=e.height;const n=Os.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=Os}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=po("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const s=n.getImageData(0,0,e.width,e.height),r=s.data;for(let o=0;o<r.length;o++)r[o]=Di(r[o]/255)*255;return n.putImageData(s,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(Di(t[n]/255)*255):t[n]=Di(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let W0=0;class Uf{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:W0++}),this.uuid=$n(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},s=this.data;if(s!==null){let r;if(Array.isArray(s)){r=[];for(let o=0,a=s.length;o<a;o++)s[o].isDataTexture?r.push(fc(s[o].image)):r.push(fc(s[o]))}else r=fc(s);n.url=r}return t||(e.images[this.uuid]=n),n}}function fc(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?V0.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let X0=0;class rn extends Er{constructor(e=rn.DEFAULT_IMAGE,t=rn.DEFAULT_MAPPING,n=Zi,s=Zi,r=Un,o=Li,a=Xn,c=Ui,l=rn.DEFAULT_ANISOTROPY,h=Yi){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:X0++}),this.uuid=$n(),this.name="",this.source=new Uf(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=s,this.magFilter=r,this.minFilter=o,this.anisotropy=l,this.format=a,this.internalFormat=null,this.type=c,this.offset=new re(0,0),this.repeat=new re(1,1),this.center=new re(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new ot,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=h,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==yf)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case pr:e.x=e.x-Math.floor(e.x);break;case Zi:e.x=e.x<0?0:1;break;case Ca:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case pr:e.y=e.y-Math.floor(e.y);break;case Zi:e.y=e.y<0?0:1;break;case Ca:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}rn.DEFAULT_IMAGE=null;rn.DEFAULT_MAPPING=yf;rn.DEFAULT_ANISOTROPY=1;class bt{constructor(e=0,t=0,n=0,s=1){bt.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=s}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,s){return this.x=e,this.y=t,this.z=n,this.w=s,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=this.w,o=e.elements;return this.x=o[0]*t+o[4]*n+o[8]*s+o[12]*r,this.y=o[1]*t+o[5]*n+o[9]*s+o[13]*r,this.z=o[2]*t+o[6]*n+o[10]*s+o[14]*r,this.w=o[3]*t+o[7]*n+o[11]*s+o[15]*r,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,s,r;const c=e.elements,l=c[0],h=c[4],u=c[8],d=c[1],f=c[5],m=c[9],_=c[2],g=c[6],p=c[10];if(Math.abs(h-d)<.01&&Math.abs(u-_)<.01&&Math.abs(m-g)<.01){if(Math.abs(h+d)<.1&&Math.abs(u+_)<.1&&Math.abs(m+g)<.1&&Math.abs(l+f+p-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const M=(l+1)/2,x=(f+1)/2,A=(p+1)/2,E=(h+d)/4,P=(u+_)/4,R=(m+g)/4;return M>x&&M>A?M<.01?(n=0,s=.707106781,r=.707106781):(n=Math.sqrt(M),s=E/n,r=P/n):x>A?x<.01?(n=.707106781,s=0,r=.707106781):(s=Math.sqrt(x),n=E/s,r=R/s):A<.01?(n=.707106781,s=.707106781,r=0):(r=Math.sqrt(A),n=P/r,s=R/r),this.set(n,s,r,t),this}let y=Math.sqrt((g-m)*(g-m)+(u-_)*(u-_)+(d-h)*(d-h));return Math.abs(y)<.001&&(y=1),this.x=(g-m)/y,this.y=(u-_)/y,this.z=(d-h)/y,this.w=Math.acos((l+f+p-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class q0 extends Er{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new bt(0,0,e,t),this.scissorTest=!1,this.viewport=new bt(0,0,e,t);const s={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:Un,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const r=new rn(s,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);r.flipY=!1,r.generateMipmaps=n.generateMipmaps,r.internalFormat=n.internalFormat,this.textures=[];const o=n.count;for(let a=0;a<o;a++)this.textures[a]=r.clone(),this.textures[a].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let s=0,r=this.textures.length;s<r;s++)this.textures[s].image.width=e,this.textures[s].image.height=t,this.textures[s].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,s=e.textures.length;n<s;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Uf(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class As extends q0{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class Of extends rn{constructor(e=null,t=1,n=1,s=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=xn,this.minFilter=xn,this.wrapR=Zi,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class $0 extends rn{constructor(e=null,t=1,n=1,s=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=xn,this.minFilter=xn,this.wrapR=Zi,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class It{constructor(e=0,t=0,n=0,s=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=s}static slerpFlat(e,t,n,s,r,o,a){let c=n[s+0],l=n[s+1],h=n[s+2],u=n[s+3];const d=r[o+0],f=r[o+1],m=r[o+2],_=r[o+3];if(a===0){e[t+0]=c,e[t+1]=l,e[t+2]=h,e[t+3]=u;return}if(a===1){e[t+0]=d,e[t+1]=f,e[t+2]=m,e[t+3]=_;return}if(u!==_||c!==d||l!==f||h!==m){let g=1-a;const p=c*d+l*f+h*m+u*_,y=p>=0?1:-1,M=1-p*p;if(M>Number.EPSILON){const A=Math.sqrt(M),E=Math.atan2(A,p*y);g=Math.sin(g*E)/A,a=Math.sin(a*E)/A}const x=a*y;if(c=c*g+d*x,l=l*g+f*x,h=h*g+m*x,u=u*g+_*x,g===1-a){const A=1/Math.sqrt(c*c+l*l+h*h+u*u);c*=A,l*=A,h*=A,u*=A}}e[t]=c,e[t+1]=l,e[t+2]=h,e[t+3]=u}static multiplyQuaternionsFlat(e,t,n,s,r,o){const a=n[s],c=n[s+1],l=n[s+2],h=n[s+3],u=r[o],d=r[o+1],f=r[o+2],m=r[o+3];return e[t]=a*m+h*u+c*f-l*d,e[t+1]=c*m+h*d+l*u-a*f,e[t+2]=l*m+h*f+a*d-c*u,e[t+3]=h*m-a*u-c*d-l*f,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,s){return this._x=e,this._y=t,this._z=n,this._w=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,s=e._y,r=e._z,o=e._order,a=Math.cos,c=Math.sin,l=a(n/2),h=a(s/2),u=a(r/2),d=c(n/2),f=c(s/2),m=c(r/2);switch(o){case"XYZ":this._x=d*h*u+l*f*m,this._y=l*f*u-d*h*m,this._z=l*h*m+d*f*u,this._w=l*h*u-d*f*m;break;case"YXZ":this._x=d*h*u+l*f*m,this._y=l*f*u-d*h*m,this._z=l*h*m-d*f*u,this._w=l*h*u+d*f*m;break;case"ZXY":this._x=d*h*u-l*f*m,this._y=l*f*u+d*h*m,this._z=l*h*m+d*f*u,this._w=l*h*u-d*f*m;break;case"ZYX":this._x=d*h*u-l*f*m,this._y=l*f*u+d*h*m,this._z=l*h*m-d*f*u,this._w=l*h*u+d*f*m;break;case"YZX":this._x=d*h*u+l*f*m,this._y=l*f*u+d*h*m,this._z=l*h*m-d*f*u,this._w=l*h*u-d*f*m;break;case"XZY":this._x=d*h*u-l*f*m,this._y=l*f*u-d*h*m,this._z=l*h*m+d*f*u,this._w=l*h*u+d*f*m;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+o)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,s=Math.sin(n);return this._x=e.x*s,this._y=e.y*s,this._z=e.z*s,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],s=t[4],r=t[8],o=t[1],a=t[5],c=t[9],l=t[2],h=t[6],u=t[10],d=n+a+u;if(d>0){const f=.5/Math.sqrt(d+1);this._w=.25/f,this._x=(h-c)*f,this._y=(r-l)*f,this._z=(o-s)*f}else if(n>a&&n>u){const f=2*Math.sqrt(1+n-a-u);this._w=(h-c)/f,this._x=.25*f,this._y=(s+o)/f,this._z=(r+l)/f}else if(a>u){const f=2*Math.sqrt(1+a-n-u);this._w=(r-l)/f,this._x=(s+o)/f,this._y=.25*f,this._z=(c+h)/f}else{const f=2*Math.sqrt(1+u-n-a);this._w=(o-s)/f,this._x=(r+l)/f,this._y=(c+h)/f,this._z=.25*f}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Qt(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const s=Math.min(1,t/n);return this.slerp(e,s),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,s=e._y,r=e._z,o=e._w,a=t._x,c=t._y,l=t._z,h=t._w;return this._x=n*h+o*a+s*l-r*c,this._y=s*h+o*c+r*a-n*l,this._z=r*h+o*l+n*c-s*a,this._w=o*h-n*a-s*c-r*l,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,s=this._y,r=this._z,o=this._w;let a=o*e._w+n*e._x+s*e._y+r*e._z;if(a<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,a=-a):this.copy(e),a>=1)return this._w=o,this._x=n,this._y=s,this._z=r,this;const c=1-a*a;if(c<=Number.EPSILON){const f=1-t;return this._w=f*o+t*this._w,this._x=f*n+t*this._x,this._y=f*s+t*this._y,this._z=f*r+t*this._z,this.normalize(),this}const l=Math.sqrt(c),h=Math.atan2(l,a),u=Math.sin((1-t)*h)/l,d=Math.sin(t*h)/l;return this._w=o*u+this._w*d,this._x=n*u+this._x*d,this._y=s*u+this._y*d,this._z=r*u+this._z*d,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),s=Math.sqrt(1-n),r=Math.sqrt(n);return this.set(s*Math.sin(e),s*Math.cos(e),r*Math.sin(t),r*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class v{constructor(e=0,t=0,n=0){v.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(Cu.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(Cu.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6]*s,this.y=r[1]*t+r[4]*n+r[7]*s,this.z=r[2]*t+r[5]*n+r[8]*s,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=e.elements,o=1/(r[3]*t+r[7]*n+r[11]*s+r[15]);return this.x=(r[0]*t+r[4]*n+r[8]*s+r[12])*o,this.y=(r[1]*t+r[5]*n+r[9]*s+r[13])*o,this.z=(r[2]*t+r[6]*n+r[10]*s+r[14])*o,this}applyQuaternion(e){const t=this.x,n=this.y,s=this.z,r=e.x,o=e.y,a=e.z,c=e.w,l=2*(o*s-a*n),h=2*(a*t-r*s),u=2*(r*n-o*t);return this.x=t+c*l+o*u-a*h,this.y=n+c*h+a*l-r*u,this.z=s+c*u+r*h-o*l,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[4]*n+r[8]*s,this.y=r[1]*t+r[5]*n+r[9]*s,this.z=r[2]*t+r[6]*n+r[10]*s,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,s=e.y,r=e.z,o=t.x,a=t.y,c=t.z;return this.x=s*c-r*a,this.y=r*o-n*c,this.z=n*a-s*o,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return pc.copy(this).projectOnVector(e),this.sub(pc)}reflect(e){return this.sub(pc.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Qt(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,s=this.z-e.z;return t*t+n*n+s*s}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const s=Math.sin(t)*e;return this.x=s*Math.sin(n),this.y=Math.cos(t)*e,this.z=s*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),s=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=s,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const pc=new v,Cu=new It;class an{constructor(e=new v(1/0,1/0,1/0),t=new v(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(ei.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(ei.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=ei.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const r=n.getAttribute("position");if(t===!0&&r!==void 0&&e.isInstancedMesh!==!0)for(let o=0,a=r.count;o<a;o++)e.isMesh===!0?e.getVertexPosition(o,ei):ei.fromBufferAttribute(r,o),ei.applyMatrix4(e.matrixWorld),this.expandByPoint(ei);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),Io.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),Io.copy(n.boundingBox)),Io.applyMatrix4(e.matrixWorld),this.union(Io)}const s=e.children;for(let r=0,o=s.length;r<o;r++)this.expandByObject(s[r],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,ei),ei.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Br),Do.subVectors(this.max,Br),Fs.subVectors(e.a,Br),Bs.subVectors(e.b,Br),ks.subVectors(e.c,Br),zi.subVectors(Bs,Fs),Hi.subVectors(ks,Bs),hs.subVectors(Fs,ks);let t=[0,-zi.z,zi.y,0,-Hi.z,Hi.y,0,-hs.z,hs.y,zi.z,0,-zi.x,Hi.z,0,-Hi.x,hs.z,0,-hs.x,-zi.y,zi.x,0,-Hi.y,Hi.x,0,-hs.y,hs.x,0];return!mc(t,Fs,Bs,ks,Do)||(t=[1,0,0,0,1,0,0,0,1],!mc(t,Fs,Bs,ks,Do))?!1:(No.crossVectors(zi,Hi),t=[No.x,No.y,No.z],mc(t,Fs,Bs,ks,Do))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,ei).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(ei).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(yi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),yi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),yi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),yi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),yi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),yi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),yi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),yi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(yi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const yi=[new v,new v,new v,new v,new v,new v,new v,new v],ei=new v,Io=new an,Fs=new v,Bs=new v,ks=new v,zi=new v,Hi=new v,hs=new v,Br=new v,Do=new v,No=new v,us=new v;function mc(i,e,t,n,s){for(let r=0,o=i.length-3;r<=o;r+=3){us.fromArray(i,r);const a=s.x*Math.abs(us.x)+s.y*Math.abs(us.y)+s.z*Math.abs(us.z),c=e.dot(us),l=t.dot(us),h=n.dot(us);if(Math.max(-Math.max(c,l,h),Math.min(c,l,h))>a)return!1}return!0}const j0=new an,kr=new v,gc=new v;class pi{constructor(e=new v,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):j0.setFromPoints(e).getCenter(n);let s=0;for(let r=0,o=e.length;r<o;r++)s=Math.max(s,n.distanceToSquared(e[r]));return this.radius=Math.sqrt(s),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;kr.subVectors(e,this.center);const t=kr.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),s=(n-this.radius)*.5;this.center.addScaledVector(kr,s/n),this.radius+=s}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(gc.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(kr.copy(e.center).add(gc)),this.expandByPoint(kr.copy(e.center).sub(gc))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Mi=new v,_c=new v,Uo=new v,Gi=new v,xc=new v,Oo=new v,vc=new v;class Xa{constructor(e=new v,t=new v(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Mi)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Mi.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Mi.copy(this.origin).addScaledVector(this.direction,t),Mi.distanceToSquared(e))}distanceSqToSegment(e,t,n,s){_c.copy(e).add(t).multiplyScalar(.5),Uo.copy(t).sub(e).normalize(),Gi.copy(this.origin).sub(_c);const r=e.distanceTo(t)*.5,o=-this.direction.dot(Uo),a=Gi.dot(this.direction),c=-Gi.dot(Uo),l=Gi.lengthSq(),h=Math.abs(1-o*o);let u,d,f,m;if(h>0)if(u=o*c-a,d=o*a-c,m=r*h,u>=0)if(d>=-m)if(d<=m){const _=1/h;u*=_,d*=_,f=u*(u+o*d+2*a)+d*(o*u+d+2*c)+l}else d=r,u=Math.max(0,-(o*d+a)),f=-u*u+d*(d+2*c)+l;else d=-r,u=Math.max(0,-(o*d+a)),f=-u*u+d*(d+2*c)+l;else d<=-m?(u=Math.max(0,-(-o*r+a)),d=u>0?-r:Math.min(Math.max(-r,-c),r),f=-u*u+d*(d+2*c)+l):d<=m?(u=0,d=Math.min(Math.max(-r,-c),r),f=d*(d+2*c)+l):(u=Math.max(0,-(o*r+a)),d=u>0?r:Math.min(Math.max(-r,-c),r),f=-u*u+d*(d+2*c)+l);else d=o>0?-r:r,u=Math.max(0,-(o*d+a)),f=-u*u+d*(d+2*c)+l;return n&&n.copy(this.origin).addScaledVector(this.direction,u),s&&s.copy(_c).addScaledVector(Uo,d),f}intersectSphere(e,t){Mi.subVectors(e.center,this.origin);const n=Mi.dot(this.direction),s=Mi.dot(Mi)-n*n,r=e.radius*e.radius;if(s>r)return null;const o=Math.sqrt(r-s),a=n-o,c=n+o;return c<0?null:a<0?this.at(c,t):this.at(a,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,s,r,o,a,c;const l=1/this.direction.x,h=1/this.direction.y,u=1/this.direction.z,d=this.origin;return l>=0?(n=(e.min.x-d.x)*l,s=(e.max.x-d.x)*l):(n=(e.max.x-d.x)*l,s=(e.min.x-d.x)*l),h>=0?(r=(e.min.y-d.y)*h,o=(e.max.y-d.y)*h):(r=(e.max.y-d.y)*h,o=(e.min.y-d.y)*h),n>o||r>s||((r>n||isNaN(n))&&(n=r),(o<s||isNaN(s))&&(s=o),u>=0?(a=(e.min.z-d.z)*u,c=(e.max.z-d.z)*u):(a=(e.max.z-d.z)*u,c=(e.min.z-d.z)*u),n>c||a>s)||((a>n||n!==n)&&(n=a),(c<s||s!==s)&&(s=c),s<0)?null:this.at(n>=0?n:s,t)}intersectsBox(e){return this.intersectBox(e,Mi)!==null}intersectTriangle(e,t,n,s,r){xc.subVectors(t,e),Oo.subVectors(n,e),vc.crossVectors(xc,Oo);let o=this.direction.dot(vc),a;if(o>0){if(s)return null;a=1}else if(o<0)a=-1,o=-o;else return null;Gi.subVectors(this.origin,e);const c=a*this.direction.dot(Oo.crossVectors(Gi,Oo));if(c<0)return null;const l=a*this.direction.dot(xc.cross(Gi));if(l<0||c+l>o)return null;const h=-a*Gi.dot(vc);return h<0?null:this.at(h/o,r)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class ge{constructor(e,t,n,s,r,o,a,c,l,h,u,d,f,m,_,g){ge.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,o,a,c,l,h,u,d,f,m,_,g)}set(e,t,n,s,r,o,a,c,l,h,u,d,f,m,_,g){const p=this.elements;return p[0]=e,p[4]=t,p[8]=n,p[12]=s,p[1]=r,p[5]=o,p[9]=a,p[13]=c,p[2]=l,p[6]=h,p[10]=u,p[14]=d,p[3]=f,p[7]=m,p[11]=_,p[15]=g,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new ge().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,s=1/zs.setFromMatrixColumn(e,0).length(),r=1/zs.setFromMatrixColumn(e,1).length(),o=1/zs.setFromMatrixColumn(e,2).length();return t[0]=n[0]*s,t[1]=n[1]*s,t[2]=n[2]*s,t[3]=0,t[4]=n[4]*r,t[5]=n[5]*r,t[6]=n[6]*r,t[7]=0,t[8]=n[8]*o,t[9]=n[9]*o,t[10]=n[10]*o,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,s=e.y,r=e.z,o=Math.cos(n),a=Math.sin(n),c=Math.cos(s),l=Math.sin(s),h=Math.cos(r),u=Math.sin(r);if(e.order==="XYZ"){const d=o*h,f=o*u,m=a*h,_=a*u;t[0]=c*h,t[4]=-c*u,t[8]=l,t[1]=f+m*l,t[5]=d-_*l,t[9]=-a*c,t[2]=_-d*l,t[6]=m+f*l,t[10]=o*c}else if(e.order==="YXZ"){const d=c*h,f=c*u,m=l*h,_=l*u;t[0]=d+_*a,t[4]=m*a-f,t[8]=o*l,t[1]=o*u,t[5]=o*h,t[9]=-a,t[2]=f*a-m,t[6]=_+d*a,t[10]=o*c}else if(e.order==="ZXY"){const d=c*h,f=c*u,m=l*h,_=l*u;t[0]=d-_*a,t[4]=-o*u,t[8]=m+f*a,t[1]=f+m*a,t[5]=o*h,t[9]=_-d*a,t[2]=-o*l,t[6]=a,t[10]=o*c}else if(e.order==="ZYX"){const d=o*h,f=o*u,m=a*h,_=a*u;t[0]=c*h,t[4]=m*l-f,t[8]=d*l+_,t[1]=c*u,t[5]=_*l+d,t[9]=f*l-m,t[2]=-l,t[6]=a*c,t[10]=o*c}else if(e.order==="YZX"){const d=o*c,f=o*l,m=a*c,_=a*l;t[0]=c*h,t[4]=_-d*u,t[8]=m*u+f,t[1]=u,t[5]=o*h,t[9]=-a*h,t[2]=-l*h,t[6]=f*u+m,t[10]=d-_*u}else if(e.order==="XZY"){const d=o*c,f=o*l,m=a*c,_=a*l;t[0]=c*h,t[4]=-u,t[8]=l*h,t[1]=d*u+_,t[5]=o*h,t[9]=f*u-m,t[2]=m*u-f,t[6]=a*h,t[10]=_*u+d}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(Y0,e,K0)}lookAt(e,t,n){const s=this.elements;return Dn.subVectors(e,t),Dn.lengthSq()===0&&(Dn.z=1),Dn.normalize(),Vi.crossVectors(n,Dn),Vi.lengthSq()===0&&(Math.abs(n.z)===1?Dn.x+=1e-4:Dn.z+=1e-4,Dn.normalize(),Vi.crossVectors(n,Dn)),Vi.normalize(),Fo.crossVectors(Dn,Vi),s[0]=Vi.x,s[4]=Fo.x,s[8]=Dn.x,s[1]=Vi.y,s[5]=Fo.y,s[9]=Dn.y,s[2]=Vi.z,s[6]=Fo.z,s[10]=Dn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,o=n[0],a=n[4],c=n[8],l=n[12],h=n[1],u=n[5],d=n[9],f=n[13],m=n[2],_=n[6],g=n[10],p=n[14],y=n[3],M=n[7],x=n[11],A=n[15],E=s[0],P=s[4],R=s[8],b=s[12],w=s[1],L=s[5],B=s[9],F=s[13],G=s[2],Z=s[6],X=s[10],$=s[14],W=s[3],ce=s[7],ve=s[11],Re=s[15];return r[0]=o*E+a*w+c*G+l*W,r[4]=o*P+a*L+c*Z+l*ce,r[8]=o*R+a*B+c*X+l*ve,r[12]=o*b+a*F+c*$+l*Re,r[1]=h*E+u*w+d*G+f*W,r[5]=h*P+u*L+d*Z+f*ce,r[9]=h*R+u*B+d*X+f*ve,r[13]=h*b+u*F+d*$+f*Re,r[2]=m*E+_*w+g*G+p*W,r[6]=m*P+_*L+g*Z+p*ce,r[10]=m*R+_*B+g*X+p*ve,r[14]=m*b+_*F+g*$+p*Re,r[3]=y*E+M*w+x*G+A*W,r[7]=y*P+M*L+x*Z+A*ce,r[11]=y*R+M*B+x*X+A*ve,r[15]=y*b+M*F+x*$+A*Re,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],s=e[8],r=e[12],o=e[1],a=e[5],c=e[9],l=e[13],h=e[2],u=e[6],d=e[10],f=e[14],m=e[3],_=e[7],g=e[11],p=e[15];return m*(+r*c*u-s*l*u-r*a*d+n*l*d+s*a*f-n*c*f)+_*(+t*c*f-t*l*d+r*o*d-s*o*f+s*l*h-r*c*h)+g*(+t*l*u-t*a*f-r*o*u+n*o*f+r*a*h-n*l*h)+p*(-s*a*h-t*c*u+t*a*d+s*o*u-n*o*d+n*c*h)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const s=this.elements;return e.isVector3?(s[12]=e.x,s[13]=e.y,s[14]=e.z):(s[12]=e,s[13]=t,s[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],c=e[6],l=e[7],h=e[8],u=e[9],d=e[10],f=e[11],m=e[12],_=e[13],g=e[14],p=e[15],y=u*g*l-_*d*l+_*c*f-a*g*f-u*c*p+a*d*p,M=m*d*l-h*g*l-m*c*f+o*g*f+h*c*p-o*d*p,x=h*_*l-m*u*l+m*a*f-o*_*f-h*a*p+o*u*p,A=m*u*c-h*_*c-m*a*d+o*_*d+h*a*g-o*u*g,E=t*y+n*M+s*x+r*A;if(E===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const P=1/E;return e[0]=y*P,e[1]=(_*d*r-u*g*r-_*s*f+n*g*f+u*s*p-n*d*p)*P,e[2]=(a*g*r-_*c*r+_*s*l-n*g*l-a*s*p+n*c*p)*P,e[3]=(u*c*r-a*d*r-u*s*l+n*d*l+a*s*f-n*c*f)*P,e[4]=M*P,e[5]=(h*g*r-m*d*r+m*s*f-t*g*f-h*s*p+t*d*p)*P,e[6]=(m*c*r-o*g*r-m*s*l+t*g*l+o*s*p-t*c*p)*P,e[7]=(o*d*r-h*c*r+h*s*l-t*d*l-o*s*f+t*c*f)*P,e[8]=x*P,e[9]=(m*u*r-h*_*r-m*n*f+t*_*f+h*n*p-t*u*p)*P,e[10]=(o*_*r-m*a*r+m*n*l-t*_*l-o*n*p+t*a*p)*P,e[11]=(h*a*r-o*u*r-h*n*l+t*u*l+o*n*f-t*a*f)*P,e[12]=A*P,e[13]=(h*_*s-m*u*s+m*n*d-t*_*d-h*n*g+t*u*g)*P,e[14]=(m*a*s-o*_*s-m*n*c+t*_*c+o*n*g-t*a*g)*P,e[15]=(o*u*s-h*a*s+h*n*c-t*u*c-o*n*d+t*a*d)*P,this}scale(e){const t=this.elements,n=e.x,s=e.y,r=e.z;return t[0]*=n,t[4]*=s,t[8]*=r,t[1]*=n,t[5]*=s,t[9]*=r,t[2]*=n,t[6]*=s,t[10]*=r,t[3]*=n,t[7]*=s,t[11]*=r,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],s=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,s))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),s=Math.sin(t),r=1-n,o=e.x,a=e.y,c=e.z,l=r*o,h=r*a;return this.set(l*o+n,l*a-s*c,l*c+s*a,0,l*a+s*c,h*a+n,h*c-s*o,0,l*c-s*a,h*c+s*o,r*c*c+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,s,r,o){return this.set(1,n,r,0,e,1,o,0,t,s,1,0,0,0,0,1),this}compose(e,t,n){const s=this.elements,r=t._x,o=t._y,a=t._z,c=t._w,l=r+r,h=o+o,u=a+a,d=r*l,f=r*h,m=r*u,_=o*h,g=o*u,p=a*u,y=c*l,M=c*h,x=c*u,A=n.x,E=n.y,P=n.z;return s[0]=(1-(_+p))*A,s[1]=(f+x)*A,s[2]=(m-M)*A,s[3]=0,s[4]=(f-x)*E,s[5]=(1-(d+p))*E,s[6]=(g+y)*E,s[7]=0,s[8]=(m+M)*P,s[9]=(g-y)*P,s[10]=(1-(d+_))*P,s[11]=0,s[12]=e.x,s[13]=e.y,s[14]=e.z,s[15]=1,this}decompose(e,t,n){const s=this.elements;let r=zs.set(s[0],s[1],s[2]).length();const o=zs.set(s[4],s[5],s[6]).length(),a=zs.set(s[8],s[9],s[10]).length();this.determinant()<0&&(r=-r),e.x=s[12],e.y=s[13],e.z=s[14],ti.copy(this);const l=1/r,h=1/o,u=1/a;return ti.elements[0]*=l,ti.elements[1]*=l,ti.elements[2]*=l,ti.elements[4]*=h,ti.elements[5]*=h,ti.elements[6]*=h,ti.elements[8]*=u,ti.elements[9]*=u,ti.elements[10]*=u,t.setFromRotationMatrix(ti),n.x=r,n.y=o,n.z=a,this}makePerspective(e,t,n,s,r,o,a=Ii){const c=this.elements,l=2*r/(t-e),h=2*r/(n-s),u=(t+e)/(t-e),d=(n+s)/(n-s);let f,m;if(a===Ii)f=-(o+r)/(o-r),m=-2*o*r/(o-r);else if(a===Pa)f=-o/(o-r),m=-o*r/(o-r);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+a);return c[0]=l,c[4]=0,c[8]=u,c[12]=0,c[1]=0,c[5]=h,c[9]=d,c[13]=0,c[2]=0,c[6]=0,c[10]=f,c[14]=m,c[3]=0,c[7]=0,c[11]=-1,c[15]=0,this}makeOrthographic(e,t,n,s,r,o,a=Ii){const c=this.elements,l=1/(t-e),h=1/(n-s),u=1/(o-r),d=(t+e)*l,f=(n+s)*h;let m,_;if(a===Ii)m=(o+r)*u,_=-2*u;else if(a===Pa)m=r*u,_=-1*u;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+a);return c[0]=2*l,c[4]=0,c[8]=0,c[12]=-d,c[1]=0,c[5]=2*h,c[9]=0,c[13]=-f,c[2]=0,c[6]=0,c[10]=_,c[14]=-m,c[3]=0,c[7]=0,c[11]=0,c[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<16;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const zs=new v,ti=new ge,Y0=new v(0,0,0),K0=new v(1,1,1),Vi=new v,Fo=new v,Dn=new v,Pu=new ge,Lu=new It;class cn{constructor(e=0,t=0,n=0,s=cn.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=s}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,s=this._order){return this._x=e,this._y=t,this._z=n,this._order=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const s=e.elements,r=s[0],o=s[4],a=s[8],c=s[1],l=s[5],h=s[9],u=s[2],d=s[6],f=s[10];switch(t){case"XYZ":this._y=Math.asin(Qt(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(-h,f),this._z=Math.atan2(-o,r)):(this._x=Math.atan2(d,l),this._z=0);break;case"YXZ":this._x=Math.asin(-Qt(h,-1,1)),Math.abs(h)<.9999999?(this._y=Math.atan2(a,f),this._z=Math.atan2(c,l)):(this._y=Math.atan2(-u,r),this._z=0);break;case"ZXY":this._x=Math.asin(Qt(d,-1,1)),Math.abs(d)<.9999999?(this._y=Math.atan2(-u,f),this._z=Math.atan2(-o,l)):(this._y=0,this._z=Math.atan2(c,r));break;case"ZYX":this._y=Math.asin(-Qt(u,-1,1)),Math.abs(u)<.9999999?(this._x=Math.atan2(d,f),this._z=Math.atan2(c,r)):(this._x=0,this._z=Math.atan2(-o,l));break;case"YZX":this._z=Math.asin(Qt(c,-1,1)),Math.abs(c)<.9999999?(this._x=Math.atan2(-h,l),this._y=Math.atan2(-u,r)):(this._x=0,this._y=Math.atan2(a,f));break;case"XZY":this._z=Math.asin(-Qt(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(d,l),this._y=Math.atan2(a,r)):(this._x=Math.atan2(-h,f),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return Pu.makeRotationFromQuaternion(e),this.setFromRotationMatrix(Pu,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return Lu.setFromEuler(this),this.setFromQuaternion(Lu,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}cn.DEFAULT_ORDER="XYZ";class Ff{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let Z0=0;const Iu=new v,Hs=new It,wi=new ge,Bo=new v,zr=new v,J0=new v,Q0=new It,Du=new v(1,0,0),Nu=new v(0,1,0),Uu=new v(0,0,1),Ou={type:"added"},eg={type:"removed"},Gs={type:"childadded",child:null},yc={type:"childremoved",child:null};class kt extends Er{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:Z0++}),this.uuid=$n(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=kt.DEFAULT_UP.clone();const e=new v,t=new cn,n=new It,s=new v(1,1,1);function r(){n.setFromEuler(t,!1)}function o(){t.setFromQuaternion(n,void 0,!1)}t._onChange(r),n._onChange(o),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:s},modelViewMatrix:{value:new ge},normalMatrix:{value:new ot}}),this.matrix=new ge,this.matrixWorld=new ge,this.matrixAutoUpdate=kt.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=kt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Ff,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return Hs.setFromAxisAngle(e,t),this.quaternion.multiply(Hs),this}rotateOnWorldAxis(e,t){return Hs.setFromAxisAngle(e,t),this.quaternion.premultiply(Hs),this}rotateX(e){return this.rotateOnAxis(Du,e)}rotateY(e){return this.rotateOnAxis(Nu,e)}rotateZ(e){return this.rotateOnAxis(Uu,e)}translateOnAxis(e,t){return Iu.copy(e).applyQuaternion(this.quaternion),this.position.add(Iu.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(Du,e)}translateY(e){return this.translateOnAxis(Nu,e)}translateZ(e){return this.translateOnAxis(Uu,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(wi.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?Bo.copy(e):Bo.set(e,t,n);const s=this.parent;this.updateWorldMatrix(!0,!1),zr.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?wi.lookAt(zr,Bo,this.up):wi.lookAt(Bo,zr,this.up),this.quaternion.setFromRotationMatrix(wi),s&&(wi.extractRotation(s.matrixWorld),Hs.setFromRotationMatrix(wi),this.quaternion.premultiply(Hs.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(Ou),Gs.child=e,this.dispatchEvent(Gs),Gs.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(eg),yc.child=e,this.dispatchEvent(yc),yc.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),wi.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),wi.multiply(e.parent.matrixWorld)),e.applyMatrix4(wi),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(Ou),Gs.child=e,this.dispatchEvent(Gs),Gs.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,s=this.children.length;n<s;n++){const o=this.children[n].getObjectByProperty(e,t);if(o!==void 0)return o}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const s=this.children;for(let r=0,o=s.length;r<o;r++)s[r].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(zr,e,J0),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(zr,Q0,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const s=this.children;for(let r=0,o=s.length;r<o;r++)s[r].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const s={};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.castShadow===!0&&(s.castShadow=!0),this.receiveShadow===!0&&(s.receiveShadow=!0),this.visible===!1&&(s.visible=!1),this.frustumCulled===!1&&(s.frustumCulled=!1),this.renderOrder!==0&&(s.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(s.userData=this.userData),s.layers=this.layers.mask,s.matrix=this.matrix.toArray(),s.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(s.matrixAutoUpdate=!1),this.isInstancedMesh&&(s.type="InstancedMesh",s.count=this.count,s.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(s.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(s.type="BatchedMesh",s.perObjectFrustumCulled=this.perObjectFrustumCulled,s.sortObjects=this.sortObjects,s.drawRanges=this._drawRanges,s.reservedRanges=this._reservedRanges,s.visibility=this._visibility,s.active=this._active,s.bounds=this._bounds.map(a=>({boxInitialized:a.boxInitialized,boxMin:a.box.min.toArray(),boxMax:a.box.max.toArray(),sphereInitialized:a.sphereInitialized,sphereRadius:a.sphere.radius,sphereCenter:a.sphere.center.toArray()})),s.maxInstanceCount=this._maxInstanceCount,s.maxVertexCount=this._maxVertexCount,s.maxIndexCount=this._maxIndexCount,s.geometryInitialized=this._geometryInitialized,s.geometryCount=this._geometryCount,s.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(s.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(s.boundingSphere={center:s.boundingSphere.center.toArray(),radius:s.boundingSphere.radius}),this.boundingBox!==null&&(s.boundingBox={min:s.boundingBox.min.toArray(),max:s.boundingBox.max.toArray()}));function r(a,c){return a[c.uuid]===void 0&&(a[c.uuid]=c.toJSON(e)),c.uuid}if(this.isScene)this.background&&(this.background.isColor?s.background=this.background.toJSON():this.background.isTexture&&(s.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(s.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){s.geometry=r(e.geometries,this.geometry);const a=this.geometry.parameters;if(a!==void 0&&a.shapes!==void 0){const c=a.shapes;if(Array.isArray(c))for(let l=0,h=c.length;l<h;l++){const u=c[l];r(e.shapes,u)}else r(e.shapes,c)}}if(this.isSkinnedMesh&&(s.bindMode=this.bindMode,s.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(r(e.skeletons,this.skeleton),s.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const a=[];for(let c=0,l=this.material.length;c<l;c++)a.push(r(e.materials,this.material[c]));s.material=a}else s.material=r(e.materials,this.material);if(this.children.length>0){s.children=[];for(let a=0;a<this.children.length;a++)s.children.push(this.children[a].toJSON(e).object)}if(this.animations.length>0){s.animations=[];for(let a=0;a<this.animations.length;a++){const c=this.animations[a];s.animations.push(r(e.animations,c))}}if(t){const a=o(e.geometries),c=o(e.materials),l=o(e.textures),h=o(e.images),u=o(e.shapes),d=o(e.skeletons),f=o(e.animations),m=o(e.nodes);a.length>0&&(n.geometries=a),c.length>0&&(n.materials=c),l.length>0&&(n.textures=l),h.length>0&&(n.images=h),u.length>0&&(n.shapes=u),d.length>0&&(n.skeletons=d),f.length>0&&(n.animations=f),m.length>0&&(n.nodes=m)}return n.object=s,n;function o(a){const c=[];for(const l in a){const h=a[l];delete h.metadata,c.push(h)}return c}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const s=e.children[n];this.add(s.clone())}return this}}kt.DEFAULT_UP=new v(0,1,0);kt.DEFAULT_MATRIX_AUTO_UPDATE=!0;kt.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const ni=new v,bi=new v,Mc=new v,Si=new v,Vs=new v,Ws=new v,Fu=new v,wc=new v,bc=new v,Sc=new v,Ec=new bt,Tc=new bt,Ac=new bt;class Wn{constructor(e=new v,t=new v,n=new v){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,s){s.subVectors(n,t),ni.subVectors(e,t),s.cross(ni);const r=s.lengthSq();return r>0?s.multiplyScalar(1/Math.sqrt(r)):s.set(0,0,0)}static getBarycoord(e,t,n,s,r){ni.subVectors(s,t),bi.subVectors(n,t),Mc.subVectors(e,t);const o=ni.dot(ni),a=ni.dot(bi),c=ni.dot(Mc),l=bi.dot(bi),h=bi.dot(Mc),u=o*l-a*a;if(u===0)return r.set(0,0,0),null;const d=1/u,f=(l*c-a*h)*d,m=(o*h-a*c)*d;return r.set(1-f-m,m,f)}static containsPoint(e,t,n,s){return this.getBarycoord(e,t,n,s,Si)===null?!1:Si.x>=0&&Si.y>=0&&Si.x+Si.y<=1}static getInterpolation(e,t,n,s,r,o,a,c){return this.getBarycoord(e,t,n,s,Si)===null?(c.x=0,c.y=0,"z"in c&&(c.z=0),"w"in c&&(c.w=0),null):(c.setScalar(0),c.addScaledVector(r,Si.x),c.addScaledVector(o,Si.y),c.addScaledVector(a,Si.z),c)}static getInterpolatedAttribute(e,t,n,s,r,o){return Ec.setScalar(0),Tc.setScalar(0),Ac.setScalar(0),Ec.fromBufferAttribute(e,t),Tc.fromBufferAttribute(e,n),Ac.fromBufferAttribute(e,s),o.setScalar(0),o.addScaledVector(Ec,r.x),o.addScaledVector(Tc,r.y),o.addScaledVector(Ac,r.z),o}static isFrontFacing(e,t,n,s){return ni.subVectors(n,t),bi.subVectors(e,t),ni.cross(bi).dot(s)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,s){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[s]),this}setFromAttributeAndIndices(e,t,n,s){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,s),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return ni.subVectors(this.c,this.b),bi.subVectors(this.a,this.b),ni.cross(bi).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return Wn.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return Wn.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,s,r){return Wn.getInterpolation(e,this.a,this.b,this.c,t,n,s,r)}containsPoint(e){return Wn.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return Wn.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,s=this.b,r=this.c;let o,a;Vs.subVectors(s,n),Ws.subVectors(r,n),wc.subVectors(e,n);const c=Vs.dot(wc),l=Ws.dot(wc);if(c<=0&&l<=0)return t.copy(n);bc.subVectors(e,s);const h=Vs.dot(bc),u=Ws.dot(bc);if(h>=0&&u<=h)return t.copy(s);const d=c*u-h*l;if(d<=0&&c>=0&&h<=0)return o=c/(c-h),t.copy(n).addScaledVector(Vs,o);Sc.subVectors(e,r);const f=Vs.dot(Sc),m=Ws.dot(Sc);if(m>=0&&f<=m)return t.copy(r);const _=f*l-c*m;if(_<=0&&l>=0&&m<=0)return a=l/(l-m),t.copy(n).addScaledVector(Ws,a);const g=h*m-f*u;if(g<=0&&u-h>=0&&f-m>=0)return Fu.subVectors(r,s),a=(u-h)/(u-h+(f-m)),t.copy(s).addScaledVector(Fu,a);const p=1/(g+_+d);return o=_*p,a=d*p,t.copy(n).addScaledVector(Vs,o).addScaledVector(Ws,a)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const Bf={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},Wi={h:0,s:0,l:0},ko={h:0,s:0,l:0};function Rc(i,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?i+(e-i)*6*t:t<1/2?e:t<2/3?i+(e-i)*6*(2/3-t):i}class Ve{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const s=e;s&&s.isColor?this.copy(s):typeof s=="number"?this.setHex(s):typeof s=="string"&&this.setStyle(s)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=Yt){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,pt.toWorkingColorSpace(this,t),this}setRGB(e,t,n,s=pt.workingColorSpace){return this.r=e,this.g=t,this.b=n,pt.toWorkingColorSpace(this,s),this}setHSL(e,t,n,s=pt.workingColorSpace){if(e=Rh(e,1),t=Qt(t,0,1),n=Qt(n,0,1),t===0)this.r=this.g=this.b=n;else{const r=n<=.5?n*(1+t):n+t-n*t,o=2*n-r;this.r=Rc(o,r,e+1/3),this.g=Rc(o,r,e),this.b=Rc(o,r,e-1/3)}return pt.toWorkingColorSpace(this,s),this}setStyle(e,t=Yt){function n(r){r!==void 0&&parseFloat(r)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let s;if(s=/^(\w+)\(([^\)]*)\)/.exec(e)){let r;const o=s[1],a=s[2];switch(o){case"rgb":case"rgba":if(r=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setRGB(Math.min(255,parseInt(r[1],10))/255,Math.min(255,parseInt(r[2],10))/255,Math.min(255,parseInt(r[3],10))/255,t);if(r=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setRGB(Math.min(100,parseInt(r[1],10))/100,Math.min(100,parseInt(r[2],10))/100,Math.min(100,parseInt(r[3],10))/100,t);break;case"hsl":case"hsla":if(r=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setHSL(parseFloat(r[1])/360,parseFloat(r[2])/100,parseFloat(r[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(s=/^\#([A-Fa-f\d]+)$/.exec(e)){const r=s[1],o=r.length;if(o===3)return this.setRGB(parseInt(r.charAt(0),16)/15,parseInt(r.charAt(1),16)/15,parseInt(r.charAt(2),16)/15,t);if(o===6)return this.setHex(parseInt(r,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=Yt){const n=Bf[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Di(e.r),this.g=Di(e.g),this.b=Di(e.b),this}copyLinearToSRGB(e){return this.r=cr(e.r),this.g=cr(e.g),this.b=cr(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=Yt){return pt.fromWorkingColorSpace(fn.copy(this),e),Math.round(Qt(fn.r*255,0,255))*65536+Math.round(Qt(fn.g*255,0,255))*256+Math.round(Qt(fn.b*255,0,255))}getHexString(e=Yt){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=pt.workingColorSpace){pt.fromWorkingColorSpace(fn.copy(this),t);const n=fn.r,s=fn.g,r=fn.b,o=Math.max(n,s,r),a=Math.min(n,s,r);let c,l;const h=(a+o)/2;if(a===o)c=0,l=0;else{const u=o-a;switch(l=h<=.5?u/(o+a):u/(2-o-a),o){case n:c=(s-r)/u+(s<r?6:0);break;case s:c=(r-n)/u+2;break;case r:c=(n-s)/u+4;break}c/=6}return e.h=c,e.s=l,e.l=h,e}getRGB(e,t=pt.workingColorSpace){return pt.fromWorkingColorSpace(fn.copy(this),t),e.r=fn.r,e.g=fn.g,e.b=fn.b,e}getStyle(e=Yt){pt.fromWorkingColorSpace(fn.copy(this),e);const t=fn.r,n=fn.g,s=fn.b;return e!==Yt?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${s.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(s*255)})`}offsetHSL(e,t,n){return this.getHSL(Wi),this.setHSL(Wi.h+e,Wi.s+t,Wi.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(Wi),e.getHSL(ko);const n=io(Wi.h,ko.h,t),s=io(Wi.s,ko.s,t),r=io(Wi.l,ko.l,t);return this.setHSL(n,s,r),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,s=this.b,r=e.elements;return this.r=r[0]*t+r[3]*n+r[6]*s,this.g=r[1]*t+r[4]*n+r[7]*s,this.b=r[2]*t+r[5]*n+r[8]*s,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const fn=new Ve;Ve.NAMES=Bf;let tg=0;class ui extends Er{static get type(){return"Material"}get type(){return this.constructor.type}set type(e){}constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:tg++}),this.uuid=$n(),this.name="",this.blending=rr,this.side=Ni,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=vl,this.blendDst=yl,this.blendEquation=ws,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new Ve(0,0,0),this.blendAlpha=0,this.depthFunc=ur,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=yu,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Us,this.stencilZFail=Us,this.stencilZPass=Us,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const s=this[t];if(s===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}s&&s.isColor?s.set(n):s&&s.isVector3&&n&&n.isVector3?s.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==rr&&(n.blending=this.blending),this.side!==Ni&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==vl&&(n.blendSrc=this.blendSrc),this.blendDst!==yl&&(n.blendDst=this.blendDst),this.blendEquation!==ws&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==ur&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==yu&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Us&&(n.stencilFail=this.stencilFail),this.stencilZFail!==Us&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==Us&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function s(r){const o=[];for(const a in r){const c=r[a];delete c.metadata,o.push(c)}return o}if(t){const r=s(e.textures),o=s(e.images);r.length>0&&(n.textures=r),o.length>0&&(n.images=o)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const s=t.length;n=new Array(s);for(let r=0;r!==s;++r)n[r]=t[r].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class _n extends ui{static get type(){return"MeshBasicMaterial"}constructor(e){super(),this.isMeshBasicMaterial=!0,this.color=new Ve(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new cn,this.combine=vf,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const Zt=new v,zo=new re;class on{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=ih,this.updateRanges=[],this.gpuType=ri,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let s=0,r=this.itemSize;s<r;s++)this.array[e+s]=t.array[n+s];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)zo.fromBufferAttribute(this,t),zo.applyMatrix3(e),this.setXY(t,zo.x,zo.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)Zt.fromBufferAttribute(this,t),Zt.applyMatrix3(e),this.setXYZ(t,Zt.x,Zt.y,Zt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)Zt.fromBufferAttribute(this,t),Zt.applyMatrix4(e),this.setXYZ(t,Zt.x,Zt.y,Zt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Zt.fromBufferAttribute(this,t),Zt.applyNormalMatrix(e),this.setXYZ(t,Zt.x,Zt.y,Zt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Zt.fromBufferAttribute(this,t),Zt.transformDirection(e),this.setXYZ(t,Zt.x,Zt.y,Zt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=si(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Pt(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=si(t,this.array)),t}setX(e,t){return this.normalized&&(t=Pt(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=si(t,this.array)),t}setY(e,t){return this.normalized&&(t=Pt(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=si(t,this.array)),t}setZ(e,t){return this.normalized&&(t=Pt(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=si(t,this.array)),t}setW(e,t){return this.normalized&&(t=Pt(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=Pt(t,this.array),n=Pt(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,s){return e*=this.itemSize,this.normalized&&(t=Pt(t,this.array),n=Pt(n,this.array),s=Pt(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e*=this.itemSize,this.normalized&&(t=Pt(t,this.array),n=Pt(n,this.array),s=Pt(s,this.array),r=Pt(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this.array[e+3]=r,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==ih&&(e.usage=this.usage),e}}class Ch extends on{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class kf extends on{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class ht extends on{constructor(e,t,n){super(new Float32Array(e),t,n)}}let ng=0;const Hn=new ge,Cc=new kt,Xs=new v,Nn=new an,Hr=new an,nn=new v;class Xt extends Er{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:ng++}),this.uuid=$n(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Nf(e)?kf:Ch)(e,1):this.index=e,this}setIndirect(e){return this.indirect=e,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const r=new ot().getNormalMatrix(e);n.applyNormalMatrix(r),n.needsUpdate=!0}const s=this.attributes.tangent;return s!==void 0&&(s.transformDirection(e),s.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return Hn.makeRotationFromQuaternion(e),this.applyMatrix4(Hn),this}rotateX(e){return Hn.makeRotationX(e),this.applyMatrix4(Hn),this}rotateY(e){return Hn.makeRotationY(e),this.applyMatrix4(Hn),this}rotateZ(e){return Hn.makeRotationZ(e),this.applyMatrix4(Hn),this}translate(e,t,n){return Hn.makeTranslation(e,t,n),this.applyMatrix4(Hn),this}scale(e,t,n){return Hn.makeScale(e,t,n),this.applyMatrix4(Hn),this}lookAt(e){return Cc.lookAt(e),Cc.updateMatrix(),this.applyMatrix4(Cc.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(Xs).negate(),this.translate(Xs.x,Xs.y,Xs.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const n=[];for(let s=0,r=e.length;s<r;s++){const o=e[s];n.push(o.x,o.y,o.z||0)}this.setAttribute("position",new ht(n,3))}else{for(let n=0,s=t.count;n<s;n++){const r=e[n];t.setXYZ(n,r.x,r.y,r.z||0)}e.length>t.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new an);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new v(-1/0,-1/0,-1/0),new v(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,s=t.length;n<s;n++){const r=t[n];Nn.setFromBufferAttribute(r),this.morphTargetsRelative?(nn.addVectors(this.boundingBox.min,Nn.min),this.boundingBox.expandByPoint(nn),nn.addVectors(this.boundingBox.max,Nn.max),this.boundingBox.expandByPoint(nn)):(this.boundingBox.expandByPoint(Nn.min),this.boundingBox.expandByPoint(Nn.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new pi);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new v,1/0);return}if(e){const n=this.boundingSphere.center;if(Nn.setFromBufferAttribute(e),t)for(let r=0,o=t.length;r<o;r++){const a=t[r];Hr.setFromBufferAttribute(a),this.morphTargetsRelative?(nn.addVectors(Nn.min,Hr.min),Nn.expandByPoint(nn),nn.addVectors(Nn.max,Hr.max),Nn.expandByPoint(nn)):(Nn.expandByPoint(Hr.min),Nn.expandByPoint(Hr.max))}Nn.getCenter(n);let s=0;for(let r=0,o=e.count;r<o;r++)nn.fromBufferAttribute(e,r),s=Math.max(s,n.distanceToSquared(nn));if(t)for(let r=0,o=t.length;r<o;r++){const a=t[r],c=this.morphTargetsRelative;for(let l=0,h=a.count;l<h;l++)nn.fromBufferAttribute(a,l),c&&(Xs.fromBufferAttribute(e,l),nn.add(Xs)),s=Math.max(s,n.distanceToSquared(nn))}this.boundingSphere.radius=Math.sqrt(s),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,s=t.normal,r=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new on(new Float32Array(4*n.count),4));const o=this.getAttribute("tangent"),a=[],c=[];for(let R=0;R<n.count;R++)a[R]=new v,c[R]=new v;const l=new v,h=new v,u=new v,d=new re,f=new re,m=new re,_=new v,g=new v;function p(R,b,w){l.fromBufferAttribute(n,R),h.fromBufferAttribute(n,b),u.fromBufferAttribute(n,w),d.fromBufferAttribute(r,R),f.fromBufferAttribute(r,b),m.fromBufferAttribute(r,w),h.sub(l),u.sub(l),f.sub(d),m.sub(d);const L=1/(f.x*m.y-m.x*f.y);isFinite(L)&&(_.copy(h).multiplyScalar(m.y).addScaledVector(u,-f.y).multiplyScalar(L),g.copy(u).multiplyScalar(f.x).addScaledVector(h,-m.x).multiplyScalar(L),a[R].add(_),a[b].add(_),a[w].add(_),c[R].add(g),c[b].add(g),c[w].add(g))}let y=this.groups;y.length===0&&(y=[{start:0,count:e.count}]);for(let R=0,b=y.length;R<b;++R){const w=y[R],L=w.start,B=w.count;for(let F=L,G=L+B;F<G;F+=3)p(e.getX(F+0),e.getX(F+1),e.getX(F+2))}const M=new v,x=new v,A=new v,E=new v;function P(R){A.fromBufferAttribute(s,R),E.copy(A);const b=a[R];M.copy(b),M.sub(A.multiplyScalar(A.dot(b))).normalize(),x.crossVectors(E,b);const L=x.dot(c[R])<0?-1:1;o.setXYZW(R,M.x,M.y,M.z,L)}for(let R=0,b=y.length;R<b;++R){const w=y[R],L=w.start,B=w.count;for(let F=L,G=L+B;F<G;F+=3)P(e.getX(F+0)),P(e.getX(F+1)),P(e.getX(F+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new on(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let d=0,f=n.count;d<f;d++)n.setXYZ(d,0,0,0);const s=new v,r=new v,o=new v,a=new v,c=new v,l=new v,h=new v,u=new v;if(e)for(let d=0,f=e.count;d<f;d+=3){const m=e.getX(d+0),_=e.getX(d+1),g=e.getX(d+2);s.fromBufferAttribute(t,m),r.fromBufferAttribute(t,_),o.fromBufferAttribute(t,g),h.subVectors(o,r),u.subVectors(s,r),h.cross(u),a.fromBufferAttribute(n,m),c.fromBufferAttribute(n,_),l.fromBufferAttribute(n,g),a.add(h),c.add(h),l.add(h),n.setXYZ(m,a.x,a.y,a.z),n.setXYZ(_,c.x,c.y,c.z),n.setXYZ(g,l.x,l.y,l.z)}else for(let d=0,f=t.count;d<f;d+=3)s.fromBufferAttribute(t,d+0),r.fromBufferAttribute(t,d+1),o.fromBufferAttribute(t,d+2),h.subVectors(o,r),u.subVectors(s,r),h.cross(u),n.setXYZ(d+0,h.x,h.y,h.z),n.setXYZ(d+1,h.x,h.y,h.z),n.setXYZ(d+2,h.x,h.y,h.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)nn.fromBufferAttribute(e,t),nn.normalize(),e.setXYZ(t,nn.x,nn.y,nn.z)}toNonIndexed(){function e(a,c){const l=a.array,h=a.itemSize,u=a.normalized,d=new l.constructor(c.length*h);let f=0,m=0;for(let _=0,g=c.length;_<g;_++){a.isInterleavedBufferAttribute?f=c[_]*a.data.stride+a.offset:f=c[_]*h;for(let p=0;p<h;p++)d[m++]=l[f++]}return new on(d,h,u)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new Xt,n=this.index.array,s=this.attributes;for(const a in s){const c=s[a],l=e(c,n);t.setAttribute(a,l)}const r=this.morphAttributes;for(const a in r){const c=[],l=r[a];for(let h=0,u=l.length;h<u;h++){const d=l[h],f=e(d,n);c.push(f)}t.morphAttributes[a]=c}t.morphTargetsRelative=this.morphTargetsRelative;const o=this.groups;for(let a=0,c=o.length;a<c;a++){const l=o[a];t.addGroup(l.start,l.count,l.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const c=this.parameters;for(const l in c)c[l]!==void 0&&(e[l]=c[l]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const c in n){const l=n[c];e.data.attributes[c]=l.toJSON(e.data)}const s={};let r=!1;for(const c in this.morphAttributes){const l=this.morphAttributes[c],h=[];for(let u=0,d=l.length;u<d;u++){const f=l[u];h.push(f.toJSON(e.data))}h.length>0&&(s[c]=h,r=!0)}r&&(e.data.morphAttributes=s,e.data.morphTargetsRelative=this.morphTargetsRelative);const o=this.groups;o.length>0&&(e.data.groups=JSON.parse(JSON.stringify(o)));const a=this.boundingSphere;return a!==null&&(e.data.boundingSphere={center:a.center.toArray(),radius:a.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const s=e.attributes;for(const l in s){const h=s[l];this.setAttribute(l,h.clone(t))}const r=e.morphAttributes;for(const l in r){const h=[],u=r[l];for(let d=0,f=u.length;d<f;d++)h.push(u[d].clone(t));this.morphAttributes[l]=h}this.morphTargetsRelative=e.morphTargetsRelative;const o=e.groups;for(let l=0,h=o.length;l<h;l++){const u=o[l];this.addGroup(u.start,u.count,u.materialIndex)}const a=e.boundingBox;a!==null&&(this.boundingBox=a.clone());const c=e.boundingSphere;return c!==null&&(this.boundingSphere=c.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const Bu=new ge,ds=new Xa,Ho=new pi,ku=new v,Go=new v,Vo=new v,Wo=new v,Pc=new v,Xo=new v,zu=new v,qo=new v;class jt extends kt{constructor(e=new Xt,t=new _n){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}getVertexPosition(e,t){const n=this.geometry,s=n.attributes.position,r=n.morphAttributes.position,o=n.morphTargetsRelative;t.fromBufferAttribute(s,e);const a=this.morphTargetInfluences;if(r&&a){Xo.set(0,0,0);for(let c=0,l=r.length;c<l;c++){const h=a[c],u=r[c];h!==0&&(Pc.fromBufferAttribute(u,e),o?Xo.addScaledVector(Pc,h):Xo.addScaledVector(Pc.sub(t),h))}t.add(Xo)}return t}raycast(e,t){const n=this.geometry,s=this.material,r=this.matrixWorld;s!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),Ho.copy(n.boundingSphere),Ho.applyMatrix4(r),ds.copy(e.ray).recast(e.near),!(Ho.containsPoint(ds.origin)===!1&&(ds.intersectSphere(Ho,ku)===null||ds.origin.distanceToSquared(ku)>(e.far-e.near)**2))&&(Bu.copy(r).invert(),ds.copy(e.ray).applyMatrix4(Bu),!(n.boundingBox!==null&&ds.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,ds)))}_computeIntersections(e,t,n){let s;const r=this.geometry,o=this.material,a=r.index,c=r.attributes.position,l=r.attributes.uv,h=r.attributes.uv1,u=r.attributes.normal,d=r.groups,f=r.drawRange;if(a!==null)if(Array.isArray(o))for(let m=0,_=d.length;m<_;m++){const g=d[m],p=o[g.materialIndex],y=Math.max(g.start,f.start),M=Math.min(a.count,Math.min(g.start+g.count,f.start+f.count));for(let x=y,A=M;x<A;x+=3){const E=a.getX(x),P=a.getX(x+1),R=a.getX(x+2);s=$o(this,p,e,n,l,h,u,E,P,R),s&&(s.faceIndex=Math.floor(x/3),s.face.materialIndex=g.materialIndex,t.push(s))}}else{const m=Math.max(0,f.start),_=Math.min(a.count,f.start+f.count);for(let g=m,p=_;g<p;g+=3){const y=a.getX(g),M=a.getX(g+1),x=a.getX(g+2);s=$o(this,o,e,n,l,h,u,y,M,x),s&&(s.faceIndex=Math.floor(g/3),t.push(s))}}else if(c!==void 0)if(Array.isArray(o))for(let m=0,_=d.length;m<_;m++){const g=d[m],p=o[g.materialIndex],y=Math.max(g.start,f.start),M=Math.min(c.count,Math.min(g.start+g.count,f.start+f.count));for(let x=y,A=M;x<A;x+=3){const E=x,P=x+1,R=x+2;s=$o(this,p,e,n,l,h,u,E,P,R),s&&(s.faceIndex=Math.floor(x/3),s.face.materialIndex=g.materialIndex,t.push(s))}}else{const m=Math.max(0,f.start),_=Math.min(c.count,f.start+f.count);for(let g=m,p=_;g<p;g+=3){const y=g,M=g+1,x=g+2;s=$o(this,o,e,n,l,h,u,y,M,x),s&&(s.faceIndex=Math.floor(g/3),t.push(s))}}}}function ig(i,e,t,n,s,r,o,a){let c;if(e.side===Sn?c=n.intersectTriangle(o,r,s,!0,a):c=n.intersectTriangle(s,r,o,e.side===Ni,a),c===null)return null;qo.copy(a),qo.applyMatrix4(i.matrixWorld);const l=t.ray.origin.distanceTo(qo);return l<t.near||l>t.far?null:{distance:l,point:qo.clone(),object:i}}function $o(i,e,t,n,s,r,o,a,c,l){i.getVertexPosition(a,Go),i.getVertexPosition(c,Vo),i.getVertexPosition(l,Wo);const h=ig(i,e,t,n,Go,Vo,Wo,zu);if(h){const u=new v;Wn.getBarycoord(zu,Go,Vo,Wo,u),s&&(h.uv=Wn.getInterpolatedAttribute(s,a,c,l,u,new re)),r&&(h.uv1=Wn.getInterpolatedAttribute(r,a,c,l,u,new re)),o&&(h.normal=Wn.getInterpolatedAttribute(o,a,c,l,u,new v),h.normal.dot(n.direction)>0&&h.normal.multiplyScalar(-1));const d={a,b:c,c:l,normal:new v,materialIndex:0};Wn.getNormal(Go,Vo,Wo,d.normal),h.face=d,h.barycoord=u}return h}class ut extends Xt{constructor(e=1,t=1,n=1,s=1,r=1,o=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:s,heightSegments:r,depthSegments:o};const a=this;s=Math.floor(s),r=Math.floor(r),o=Math.floor(o);const c=[],l=[],h=[],u=[];let d=0,f=0;m("z","y","x",-1,-1,n,t,e,o,r,0),m("z","y","x",1,-1,n,t,-e,o,r,1),m("x","z","y",1,1,e,n,t,s,o,2),m("x","z","y",1,-1,e,n,-t,s,o,3),m("x","y","z",1,-1,e,t,n,s,r,4),m("x","y","z",-1,-1,e,t,-n,s,r,5),this.setIndex(c),this.setAttribute("position",new ht(l,3)),this.setAttribute("normal",new ht(h,3)),this.setAttribute("uv",new ht(u,2));function m(_,g,p,y,M,x,A,E,P,R,b){const w=x/P,L=A/R,B=x/2,F=A/2,G=E/2,Z=P+1,X=R+1;let $=0,W=0;const ce=new v;for(let ve=0;ve<X;ve++){const Re=ve*L-F;for(let it=0;it<Z;it++){const St=it*w-B;ce[_]=St*y,ce[g]=Re*M,ce[p]=G,l.push(ce.x,ce.y,ce.z),ce[_]=0,ce[g]=0,ce[p]=E>0?1:-1,h.push(ce.x,ce.y,ce.z),u.push(it/P),u.push(1-ve/R),$+=1}}for(let ve=0;ve<R;ve++)for(let Re=0;Re<P;Re++){const it=d+Re+Z*ve,St=d+Re+Z*(ve+1),K=d+(Re+1)+Z*(ve+1),ue=d+(Re+1)+Z*ve;c.push(it,St,ue),c.push(St,K,ue),W+=6}a.addGroup(f,W,b),f+=W,d+=$}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ut(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function xr(i){const e={};for(const t in i){e[t]={};for(const n in i[t]){const s=i[t][n];s&&(s.isColor||s.isMatrix3||s.isMatrix4||s.isVector2||s.isVector3||s.isVector4||s.isTexture||s.isQuaternion)?s.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=s.clone():Array.isArray(s)?e[t][n]=s.slice():e[t][n]=s}}return e}function Mn(i){const e={};for(let t=0;t<i.length;t++){const n=xr(i[t]);for(const s in n)e[s]=n[s]}return e}function sg(i){const e=[];for(let t=0;t<i.length;t++)e.push(i[t].clone());return e}function zf(i){const e=i.getRenderTarget();return e===null?i.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:pt.workingColorSpace}const rg={clone:xr,merge:Mn};var og=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,ag=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class di extends ui{static get type(){return"ShaderMaterial"}constructor(e){super(),this.isShaderMaterial=!0,this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=og,this.fragmentShader=ag,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=xr(e.uniforms),this.uniformsGroups=sg(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const s in this.uniforms){const o=this.uniforms[s].value;o&&o.isTexture?t.uniforms[s]={type:"t",value:o.toJSON(e).uuid}:o&&o.isColor?t.uniforms[s]={type:"c",value:o.getHex()}:o&&o.isVector2?t.uniforms[s]={type:"v2",value:o.toArray()}:o&&o.isVector3?t.uniforms[s]={type:"v3",value:o.toArray()}:o&&o.isVector4?t.uniforms[s]={type:"v4",value:o.toArray()}:o&&o.isMatrix3?t.uniforms[s]={type:"m3",value:o.toArray()}:o&&o.isMatrix4?t.uniforms[s]={type:"m4",value:o.toArray()}:t.uniforms[s]={value:o}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const s in this.extensions)this.extensions[s]===!0&&(n[s]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class Hf extends kt{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new ge,this.projectionMatrix=new ge,this.projectionMatrixInverse=new ge,this.coordinateSystem=Ii}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const Xi=new v,Hu=new re,Gu=new re;class Cn extends Hf{constructor(e=50,t=1,n=.1,s=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=s,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=_r*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(ar*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return _r*2*Math.atan(Math.tan(ar*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){Xi.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(Xi.x,Xi.y).multiplyScalar(-e/Xi.z),Xi.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(Xi.x,Xi.y).multiplyScalar(-e/Xi.z)}getViewSize(e,t){return this.getViewBounds(e,Hu,Gu),t.subVectors(Gu,Hu)}setViewOffset(e,t,n,s,r,o){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(ar*.5*this.fov)/this.zoom,n=2*t,s=this.aspect*n,r=-.5*s;const o=this.view;if(this.view!==null&&this.view.enabled){const c=o.fullWidth,l=o.fullHeight;r+=o.offsetX*s/c,t-=o.offsetY*n/l,s*=o.width/c,n*=o.height/l}const a=this.filmOffset;a!==0&&(r+=e*a/this.getFilmWidth()),this.projectionMatrix.makePerspective(r,r+s,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const qs=-90,$s=1;class cg extends kt{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const s=new Cn(qs,$s,e,t);s.layers=this.layers,this.add(s);const r=new Cn(qs,$s,e,t);r.layers=this.layers,this.add(r);const o=new Cn(qs,$s,e,t);o.layers=this.layers,this.add(o);const a=new Cn(qs,$s,e,t);a.layers=this.layers,this.add(a);const c=new Cn(qs,$s,e,t);c.layers=this.layers,this.add(c);const l=new Cn(qs,$s,e,t);l.layers=this.layers,this.add(l)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,s,r,o,a,c]=t;for(const l of t)this.remove(l);if(e===Ii)n.up.set(0,1,0),n.lookAt(1,0,0),s.up.set(0,1,0),s.lookAt(-1,0,0),r.up.set(0,0,-1),r.lookAt(0,1,0),o.up.set(0,0,1),o.lookAt(0,-1,0),a.up.set(0,1,0),a.lookAt(0,0,1),c.up.set(0,1,0),c.lookAt(0,0,-1);else if(e===Pa)n.up.set(0,-1,0),n.lookAt(-1,0,0),s.up.set(0,-1,0),s.lookAt(1,0,0),r.up.set(0,0,1),r.lookAt(0,1,0),o.up.set(0,0,-1),o.lookAt(0,-1,0),a.up.set(0,-1,0),a.lookAt(0,0,1),c.up.set(0,-1,0),c.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const l of t)this.add(l),l.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:s}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[r,o,a,c,l,h]=this.children,u=e.getRenderTarget(),d=e.getActiveCubeFace(),f=e.getActiveMipmapLevel(),m=e.xr.enabled;e.xr.enabled=!1;const _=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,s),e.render(t,r),e.setRenderTarget(n,1,s),e.render(t,o),e.setRenderTarget(n,2,s),e.render(t,a),e.setRenderTarget(n,3,s),e.render(t,c),e.setRenderTarget(n,4,s),e.render(t,l),n.texture.generateMipmaps=_,e.setRenderTarget(n,5,s),e.render(t,h),e.setRenderTarget(u,d,f),e.xr.enabled=m,n.texture.needsPMREMUpdate=!0}}class Gf extends rn{constructor(e,t,n,s,r,o,a,c,l,h){e=e!==void 0?e:[],t=t!==void 0?t:dr,super(e,t,n,s,r,o,a,c,l,h),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class lg extends As{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},s=[n,n,n,n,n,n];this.texture=new Gf(s,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:Un}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},s=new ut(5,5,5),r=new di({name:"CubemapFromEquirect",uniforms:xr(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:Sn,blending:ns});r.uniforms.tEquirect.value=t;const o=new jt(s,r),a=t.minFilter;return t.minFilter===Li&&(t.minFilter=Un),new cg(1,10,this).update(e,o),t.minFilter=a,o.geometry.dispose(),o.material.dispose(),this}clear(e,t,n,s){const r=e.getRenderTarget();for(let o=0;o<6;o++)e.setRenderTarget(this,o),e.clear(t,n,s);e.setRenderTarget(r)}}const Lc=new v,hg=new v,ug=new ot;class ys{constructor(e=new v(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,s){return this.normal.set(e,t,n),this.constant=s,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const s=Lc.subVectors(n,t).cross(hg.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(s,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(Lc),s=this.normal.dot(n);if(s===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const r=-(e.start.dot(this.normal)+this.constant)/s;return r<0||r>1?null:t.copy(e.start).addScaledVector(n,r)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||ug.getNormalMatrix(e),s=this.coplanarPoint(Lc).applyMatrix4(e),r=this.normal.applyMatrix3(n).normalize();return this.constant=-s.dot(r),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const fs=new pi,jo=new v;class Ph{constructor(e=new ys,t=new ys,n=new ys,s=new ys,r=new ys,o=new ys){this.planes=[e,t,n,s,r,o]}set(e,t,n,s,r,o){const a=this.planes;return a[0].copy(e),a[1].copy(t),a[2].copy(n),a[3].copy(s),a[4].copy(r),a[5].copy(o),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Ii){const n=this.planes,s=e.elements,r=s[0],o=s[1],a=s[2],c=s[3],l=s[4],h=s[5],u=s[6],d=s[7],f=s[8],m=s[9],_=s[10],g=s[11],p=s[12],y=s[13],M=s[14],x=s[15];if(n[0].setComponents(c-r,d-l,g-f,x-p).normalize(),n[1].setComponents(c+r,d+l,g+f,x+p).normalize(),n[2].setComponents(c+o,d+h,g+m,x+y).normalize(),n[3].setComponents(c-o,d-h,g-m,x-y).normalize(),n[4].setComponents(c-a,d-u,g-_,x-M).normalize(),t===Ii)n[5].setComponents(c+a,d+u,g+_,x+M).normalize();else if(t===Pa)n[5].setComponents(a,u,_,M).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),fs.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),fs.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(fs)}intersectsSprite(e){return fs.center.set(0,0,0),fs.radius=.7071067811865476,fs.applyMatrix4(e.matrixWorld),this.intersectsSphere(fs)}intersectsSphere(e){const t=this.planes,n=e.center,s=-e.radius;for(let r=0;r<6;r++)if(t[r].distanceToPoint(n)<s)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const s=t[n];if(jo.x=s.normal.x>0?e.max.x:e.min.x,jo.y=s.normal.y>0?e.max.y:e.min.y,jo.z=s.normal.z>0?e.max.z:e.min.z,s.distanceToPoint(jo)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Vf(){let i=null,e=!1,t=null,n=null;function s(r,o){t(r,o),n=i.requestAnimationFrame(s)}return{start:function(){e!==!0&&t!==null&&(n=i.requestAnimationFrame(s),e=!0)},stop:function(){i.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(r){t=r},setContext:function(r){i=r}}}function dg(i){const e=new WeakMap;function t(a,c){const l=a.array,h=a.usage,u=l.byteLength,d=i.createBuffer();i.bindBuffer(c,d),i.bufferData(c,l,h),a.onUploadCallback();let f;if(l instanceof Float32Array)f=i.FLOAT;else if(l instanceof Uint16Array)a.isFloat16BufferAttribute?f=i.HALF_FLOAT:f=i.UNSIGNED_SHORT;else if(l instanceof Int16Array)f=i.SHORT;else if(l instanceof Uint32Array)f=i.UNSIGNED_INT;else if(l instanceof Int32Array)f=i.INT;else if(l instanceof Int8Array)f=i.BYTE;else if(l instanceof Uint8Array)f=i.UNSIGNED_BYTE;else if(l instanceof Uint8ClampedArray)f=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+l);return{buffer:d,type:f,bytesPerElement:l.BYTES_PER_ELEMENT,version:a.version,size:u}}function n(a,c,l){const h=c.array,u=c.updateRanges;if(i.bindBuffer(l,a),u.length===0)i.bufferSubData(l,0,h);else{u.sort((f,m)=>f.start-m.start);let d=0;for(let f=1;f<u.length;f++){const m=u[d],_=u[f];_.start<=m.start+m.count+1?m.count=Math.max(m.count,_.start+_.count-m.start):(++d,u[d]=_)}u.length=d+1;for(let f=0,m=u.length;f<m;f++){const _=u[f];i.bufferSubData(l,_.start*h.BYTES_PER_ELEMENT,h,_.start,_.count)}c.clearUpdateRanges()}c.onUploadCallback()}function s(a){return a.isInterleavedBufferAttribute&&(a=a.data),e.get(a)}function r(a){a.isInterleavedBufferAttribute&&(a=a.data);const c=e.get(a);c&&(i.deleteBuffer(c.buffer),e.delete(a))}function o(a,c){if(a.isInterleavedBufferAttribute&&(a=a.data),a.isGLBufferAttribute){const h=e.get(a);(!h||h.version<a.version)&&e.set(a,{buffer:a.buffer,type:a.type,bytesPerElement:a.elementSize,version:a.version});return}const l=e.get(a);if(l===void 0)e.set(a,t(a,c));else if(l.version<a.version){if(l.size!==a.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(l.buffer,a,c),l.version=a.version}}return{get:s,remove:r,update:o}}class fi extends Xt{constructor(e=1,t=1,n=1,s=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:s};const r=e/2,o=t/2,a=Math.floor(n),c=Math.floor(s),l=a+1,h=c+1,u=e/a,d=t/c,f=[],m=[],_=[],g=[];for(let p=0;p<h;p++){const y=p*d-o;for(let M=0;M<l;M++){const x=M*u-r;m.push(x,-y,0),_.push(0,0,1),g.push(M/a),g.push(1-p/c)}}for(let p=0;p<c;p++)for(let y=0;y<a;y++){const M=y+l*p,x=y+l*(p+1),A=y+1+l*(p+1),E=y+1+l*p;f.push(M,x,E),f.push(x,A,E)}this.setIndex(f),this.setAttribute("position",new ht(m,3)),this.setAttribute("normal",new ht(_,3)),this.setAttribute("uv",new ht(g,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new fi(e.width,e.height,e.widthSegments,e.heightSegments)}}var fg=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,pg=`#ifdef USE_ALPHAHASH
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
#endif`,mg=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,gg=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,_g=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,xg=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,vg=`#ifdef USE_AOMAP
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
#endif`,yg=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,Mg=`#ifdef USE_BATCHING
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
#endif`,wg=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,bg=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,Sg=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,Eg=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,Tg=`#ifdef USE_IRIDESCENCE
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
#endif`,Ag=`#ifdef USE_BUMPMAP
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
#endif`,Rg=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,Cg=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,Pg=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,Lg=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,Ig=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,Dg=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,Ng=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,Ug=`#if defined( USE_COLOR_ALPHA )
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
#endif`,Og=`#define PI 3.141592653589793
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
} // validated`,Fg=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,Bg=`vec3 transformedNormal = objectNormal;
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
#endif`,kg=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,zg=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,Hg=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,Gg=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,Vg="gl_FragColor = linearToOutputTexel( gl_FragColor );",Wg=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,Xg=`#ifdef USE_ENVMAP
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
#endif`,qg=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,$g=`#ifdef USE_ENVMAP
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
#endif`,jg=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,Yg=`#ifdef USE_ENVMAP
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
#endif`,Kg=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,Zg=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,Jg=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,Qg=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,e_=`#ifdef USE_GRADIENTMAP
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
}`,t_=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,n_=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,i_=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,s_=`uniform bool receiveShadow;
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
#endif`,r_=`#ifdef USE_ENVMAP
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
#endif`,o_=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,a_=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,c_=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,l_=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,h_=`PhysicalMaterial material;
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
#endif`,u_=`struct PhysicalMaterial {
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
}`,d_=`
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
#endif`,f_=`#if defined( RE_IndirectDiffuse )
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
#endif`,p_=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,m_=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,g_=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,__=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,x_=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,v_=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,y_=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,M_=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,w_=`#if defined( USE_POINTS_UV )
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
#endif`,b_=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,S_=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,E_=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,T_=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,A_=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,R_=`#ifdef USE_MORPHTARGETS
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
#endif`,C_=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,P_=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,L_=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,I_=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,D_=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,N_=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,U_=`#ifdef USE_NORMALMAP
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
#endif`,O_=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,F_=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,B_=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,k_=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,z_=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,H_=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,G_=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,V_=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,W_=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,X_=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,q_=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,$_=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,j_=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,Y_=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,K_=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,Z_=`float getShadowMask() {
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
}`,J_=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,Q_=`#ifdef USE_SKINNING
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
#endif`,ex=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,tx=`#ifdef USE_SKINNING
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
#endif`,nx=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,ix=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,sx=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,rx=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,ox=`#ifdef USE_TRANSMISSION
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
#endif`,ax=`#ifdef USE_TRANSMISSION
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
#endif`,cx=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,lx=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,hx=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,ux=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const dx=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,fx=`uniform sampler2D t2D;
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
}`,px=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,mx=`#ifdef ENVMAP_TYPE_CUBE
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
}`,gx=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,_x=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,xx=`#include <common>
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
}`,vx=`#if DEPTH_PACKING == 3200
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
}`,yx=`#define DISTANCE
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
}`,Mx=`#define DISTANCE
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
}`,wx=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,bx=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Sx=`uniform float scale;
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
}`,Ex=`uniform vec3 diffuse;
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
}`,Tx=`#include <common>
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
}`,Ax=`uniform vec3 diffuse;
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
}`,Rx=`#define LAMBERT
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
}`,Cx=`#define LAMBERT
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
}`,Px=`#define MATCAP
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
}`,Lx=`#define MATCAP
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
}`,Ix=`#define NORMAL
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
}`,Dx=`#define NORMAL
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
}`,Nx=`#define PHONG
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
}`,Ux=`#define PHONG
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
}`,Ox=`#define STANDARD
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
}`,Fx=`#define STANDARD
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
}`,Bx=`#define TOON
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
}`,kx=`#define TOON
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
}`,zx=`uniform float size;
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
}`,Hx=`uniform vec3 diffuse;
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
}`,Gx=`#include <common>
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
}`,Vx=`uniform vec3 color;
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
}`,Wx=`uniform float rotation;
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
}`,Xx=`uniform vec3 diffuse;
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
}`,lt={alphahash_fragment:fg,alphahash_pars_fragment:pg,alphamap_fragment:mg,alphamap_pars_fragment:gg,alphatest_fragment:_g,alphatest_pars_fragment:xg,aomap_fragment:vg,aomap_pars_fragment:yg,batching_pars_vertex:Mg,batching_vertex:wg,begin_vertex:bg,beginnormal_vertex:Sg,bsdfs:Eg,iridescence_fragment:Tg,bumpmap_pars_fragment:Ag,clipping_planes_fragment:Rg,clipping_planes_pars_fragment:Cg,clipping_planes_pars_vertex:Pg,clipping_planes_vertex:Lg,color_fragment:Ig,color_pars_fragment:Dg,color_pars_vertex:Ng,color_vertex:Ug,common:Og,cube_uv_reflection_fragment:Fg,defaultnormal_vertex:Bg,displacementmap_pars_vertex:kg,displacementmap_vertex:zg,emissivemap_fragment:Hg,emissivemap_pars_fragment:Gg,colorspace_fragment:Vg,colorspace_pars_fragment:Wg,envmap_fragment:Xg,envmap_common_pars_fragment:qg,envmap_pars_fragment:$g,envmap_pars_vertex:jg,envmap_physical_pars_fragment:r_,envmap_vertex:Yg,fog_vertex:Kg,fog_pars_vertex:Zg,fog_fragment:Jg,fog_pars_fragment:Qg,gradientmap_pars_fragment:e_,lightmap_pars_fragment:t_,lights_lambert_fragment:n_,lights_lambert_pars_fragment:i_,lights_pars_begin:s_,lights_toon_fragment:o_,lights_toon_pars_fragment:a_,lights_phong_fragment:c_,lights_phong_pars_fragment:l_,lights_physical_fragment:h_,lights_physical_pars_fragment:u_,lights_fragment_begin:d_,lights_fragment_maps:f_,lights_fragment_end:p_,logdepthbuf_fragment:m_,logdepthbuf_pars_fragment:g_,logdepthbuf_pars_vertex:__,logdepthbuf_vertex:x_,map_fragment:v_,map_pars_fragment:y_,map_particle_fragment:M_,map_particle_pars_fragment:w_,metalnessmap_fragment:b_,metalnessmap_pars_fragment:S_,morphinstance_vertex:E_,morphcolor_vertex:T_,morphnormal_vertex:A_,morphtarget_pars_vertex:R_,morphtarget_vertex:C_,normal_fragment_begin:P_,normal_fragment_maps:L_,normal_pars_fragment:I_,normal_pars_vertex:D_,normal_vertex:N_,normalmap_pars_fragment:U_,clearcoat_normal_fragment_begin:O_,clearcoat_normal_fragment_maps:F_,clearcoat_pars_fragment:B_,iridescence_pars_fragment:k_,opaque_fragment:z_,packing:H_,premultiplied_alpha_fragment:G_,project_vertex:V_,dithering_fragment:W_,dithering_pars_fragment:X_,roughnessmap_fragment:q_,roughnessmap_pars_fragment:$_,shadowmap_pars_fragment:j_,shadowmap_pars_vertex:Y_,shadowmap_vertex:K_,shadowmask_pars_fragment:Z_,skinbase_vertex:J_,skinning_pars_vertex:Q_,skinning_vertex:ex,skinnormal_vertex:tx,specularmap_fragment:nx,specularmap_pars_fragment:ix,tonemapping_fragment:sx,tonemapping_pars_fragment:rx,transmission_fragment:ox,transmission_pars_fragment:ax,uv_pars_fragment:cx,uv_pars_vertex:lx,uv_vertex:hx,worldpos_vertex:ux,background_vert:dx,background_frag:fx,backgroundCube_vert:px,backgroundCube_frag:mx,cube_vert:gx,cube_frag:_x,depth_vert:xx,depth_frag:vx,distanceRGBA_vert:yx,distanceRGBA_frag:Mx,equirect_vert:wx,equirect_frag:bx,linedashed_vert:Sx,linedashed_frag:Ex,meshbasic_vert:Tx,meshbasic_frag:Ax,meshlambert_vert:Rx,meshlambert_frag:Cx,meshmatcap_vert:Px,meshmatcap_frag:Lx,meshnormal_vert:Ix,meshnormal_frag:Dx,meshphong_vert:Nx,meshphong_frag:Ux,meshphysical_vert:Ox,meshphysical_frag:Fx,meshtoon_vert:Bx,meshtoon_frag:kx,points_vert:zx,points_frag:Hx,shadow_vert:Gx,shadow_frag:Vx,sprite_vert:Wx,sprite_frag:Xx},ye={common:{diffuse:{value:new Ve(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new ot},alphaMap:{value:null},alphaMapTransform:{value:new ot},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new ot}},envmap:{envMap:{value:null},envMapRotation:{value:new ot},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new ot}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new ot}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new ot},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new ot},normalScale:{value:new re(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new ot},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new ot}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new ot}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new ot}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new Ve(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new Ve(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new ot},alphaTest:{value:0},uvTransform:{value:new ot}},sprite:{diffuse:{value:new Ve(16777215)},opacity:{value:1},center:{value:new re(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new ot},alphaMap:{value:null},alphaMapTransform:{value:new ot},alphaTest:{value:0}}},ci={basic:{uniforms:Mn([ye.common,ye.specularmap,ye.envmap,ye.aomap,ye.lightmap,ye.fog]),vertexShader:lt.meshbasic_vert,fragmentShader:lt.meshbasic_frag},lambert:{uniforms:Mn([ye.common,ye.specularmap,ye.envmap,ye.aomap,ye.lightmap,ye.emissivemap,ye.bumpmap,ye.normalmap,ye.displacementmap,ye.fog,ye.lights,{emissive:{value:new Ve(0)}}]),vertexShader:lt.meshlambert_vert,fragmentShader:lt.meshlambert_frag},phong:{uniforms:Mn([ye.common,ye.specularmap,ye.envmap,ye.aomap,ye.lightmap,ye.emissivemap,ye.bumpmap,ye.normalmap,ye.displacementmap,ye.fog,ye.lights,{emissive:{value:new Ve(0)},specular:{value:new Ve(1118481)},shininess:{value:30}}]),vertexShader:lt.meshphong_vert,fragmentShader:lt.meshphong_frag},standard:{uniforms:Mn([ye.common,ye.envmap,ye.aomap,ye.lightmap,ye.emissivemap,ye.bumpmap,ye.normalmap,ye.displacementmap,ye.roughnessmap,ye.metalnessmap,ye.fog,ye.lights,{emissive:{value:new Ve(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:lt.meshphysical_vert,fragmentShader:lt.meshphysical_frag},toon:{uniforms:Mn([ye.common,ye.aomap,ye.lightmap,ye.emissivemap,ye.bumpmap,ye.normalmap,ye.displacementmap,ye.gradientmap,ye.fog,ye.lights,{emissive:{value:new Ve(0)}}]),vertexShader:lt.meshtoon_vert,fragmentShader:lt.meshtoon_frag},matcap:{uniforms:Mn([ye.common,ye.bumpmap,ye.normalmap,ye.displacementmap,ye.fog,{matcap:{value:null}}]),vertexShader:lt.meshmatcap_vert,fragmentShader:lt.meshmatcap_frag},points:{uniforms:Mn([ye.points,ye.fog]),vertexShader:lt.points_vert,fragmentShader:lt.points_frag},dashed:{uniforms:Mn([ye.common,ye.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:lt.linedashed_vert,fragmentShader:lt.linedashed_frag},depth:{uniforms:Mn([ye.common,ye.displacementmap]),vertexShader:lt.depth_vert,fragmentShader:lt.depth_frag},normal:{uniforms:Mn([ye.common,ye.bumpmap,ye.normalmap,ye.displacementmap,{opacity:{value:1}}]),vertexShader:lt.meshnormal_vert,fragmentShader:lt.meshnormal_frag},sprite:{uniforms:Mn([ye.sprite,ye.fog]),vertexShader:lt.sprite_vert,fragmentShader:lt.sprite_frag},background:{uniforms:{uvTransform:{value:new ot},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:lt.background_vert,fragmentShader:lt.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new ot}},vertexShader:lt.backgroundCube_vert,fragmentShader:lt.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:lt.cube_vert,fragmentShader:lt.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:lt.equirect_vert,fragmentShader:lt.equirect_frag},distanceRGBA:{uniforms:Mn([ye.common,ye.displacementmap,{referencePosition:{value:new v},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:lt.distanceRGBA_vert,fragmentShader:lt.distanceRGBA_frag},shadow:{uniforms:Mn([ye.lights,ye.fog,{color:{value:new Ve(0)},opacity:{value:1}}]),vertexShader:lt.shadow_vert,fragmentShader:lt.shadow_frag}};ci.physical={uniforms:Mn([ci.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new ot},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new ot},clearcoatNormalScale:{value:new re(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new ot},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new ot},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new ot},sheen:{value:0},sheenColor:{value:new Ve(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new ot},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new ot},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new ot},transmissionSamplerSize:{value:new re},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new ot},attenuationDistance:{value:0},attenuationColor:{value:new Ve(0)},specularColor:{value:new Ve(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new ot},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new ot},anisotropyVector:{value:new re},anisotropyMap:{value:null},anisotropyMapTransform:{value:new ot}}]),vertexShader:lt.meshphysical_vert,fragmentShader:lt.meshphysical_frag};const Yo={r:0,b:0,g:0},ps=new cn,qx=new ge;function $x(i,e,t,n,s,r,o){const a=new Ve(0);let c=r===!0?0:1,l,h,u=null,d=0,f=null;function m(y){let M=y.isScene===!0?y.background:null;return M&&M.isTexture&&(M=(y.backgroundBlurriness>0?t:e).get(M)),M}function _(y){let M=!1;const x=m(y);x===null?p(a,c):x&&x.isColor&&(p(x,1),M=!0);const A=i.xr.getEnvironmentBlendMode();A==="additive"?n.buffers.color.setClear(0,0,0,1,o):A==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,o),(i.autoClear||M)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function g(y,M){const x=m(M);x&&(x.isCubeTexture||x.mapping===Va)?(h===void 0&&(h=new jt(new ut(1,1,1),new di({name:"BackgroundCubeMaterial",uniforms:xr(ci.backgroundCube.uniforms),vertexShader:ci.backgroundCube.vertexShader,fragmentShader:ci.backgroundCube.fragmentShader,side:Sn,depthTest:!1,depthWrite:!1,fog:!1})),h.geometry.deleteAttribute("normal"),h.geometry.deleteAttribute("uv"),h.onBeforeRender=function(A,E,P){this.matrixWorld.copyPosition(P.matrixWorld)},Object.defineProperty(h.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),s.update(h)),ps.copy(M.backgroundRotation),ps.x*=-1,ps.y*=-1,ps.z*=-1,x.isCubeTexture&&x.isRenderTargetTexture===!1&&(ps.y*=-1,ps.z*=-1),h.material.uniforms.envMap.value=x,h.material.uniforms.flipEnvMap.value=x.isCubeTexture&&x.isRenderTargetTexture===!1?-1:1,h.material.uniforms.backgroundBlurriness.value=M.backgroundBlurriness,h.material.uniforms.backgroundIntensity.value=M.backgroundIntensity,h.material.uniforms.backgroundRotation.value.setFromMatrix4(qx.makeRotationFromEuler(ps)),h.material.toneMapped=pt.getTransfer(x.colorSpace)!==Nt,(u!==x||d!==x.version||f!==i.toneMapping)&&(h.material.needsUpdate=!0,u=x,d=x.version,f=i.toneMapping),h.layers.enableAll(),y.unshift(h,h.geometry,h.material,0,0,null)):x&&x.isTexture&&(l===void 0&&(l=new jt(new fi(2,2),new di({name:"BackgroundMaterial",uniforms:xr(ci.background.uniforms),vertexShader:ci.background.vertexShader,fragmentShader:ci.background.fragmentShader,side:Ni,depthTest:!1,depthWrite:!1,fog:!1})),l.geometry.deleteAttribute("normal"),Object.defineProperty(l.material,"map",{get:function(){return this.uniforms.t2D.value}}),s.update(l)),l.material.uniforms.t2D.value=x,l.material.uniforms.backgroundIntensity.value=M.backgroundIntensity,l.material.toneMapped=pt.getTransfer(x.colorSpace)!==Nt,x.matrixAutoUpdate===!0&&x.updateMatrix(),l.material.uniforms.uvTransform.value.copy(x.matrix),(u!==x||d!==x.version||f!==i.toneMapping)&&(l.material.needsUpdate=!0,u=x,d=x.version,f=i.toneMapping),l.layers.enableAll(),y.unshift(l,l.geometry,l.material,0,0,null))}function p(y,M){y.getRGB(Yo,zf(i)),n.buffers.color.setClear(Yo.r,Yo.g,Yo.b,M,o)}return{getClearColor:function(){return a},setClearColor:function(y,M=1){a.set(y),c=M,p(a,c)},getClearAlpha:function(){return c},setClearAlpha:function(y){c=y,p(a,c)},render:_,addToRenderList:g}}function jx(i,e){const t=i.getParameter(i.MAX_VERTEX_ATTRIBS),n={},s=d(null);let r=s,o=!1;function a(w,L,B,F,G){let Z=!1;const X=u(F,B,L);r!==X&&(r=X,l(r.object)),Z=f(w,F,B,G),Z&&m(w,F,B,G),G!==null&&e.update(G,i.ELEMENT_ARRAY_BUFFER),(Z||o)&&(o=!1,x(w,L,B,F),G!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,e.get(G).buffer))}function c(){return i.createVertexArray()}function l(w){return i.bindVertexArray(w)}function h(w){return i.deleteVertexArray(w)}function u(w,L,B){const F=B.wireframe===!0;let G=n[w.id];G===void 0&&(G={},n[w.id]=G);let Z=G[L.id];Z===void 0&&(Z={},G[L.id]=Z);let X=Z[F];return X===void 0&&(X=d(c()),Z[F]=X),X}function d(w){const L=[],B=[],F=[];for(let G=0;G<t;G++)L[G]=0,B[G]=0,F[G]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:L,enabledAttributes:B,attributeDivisors:F,object:w,attributes:{},index:null}}function f(w,L,B,F){const G=r.attributes,Z=L.attributes;let X=0;const $=B.getAttributes();for(const W in $)if($[W].location>=0){const ve=G[W];let Re=Z[W];if(Re===void 0&&(W==="instanceMatrix"&&w.instanceMatrix&&(Re=w.instanceMatrix),W==="instanceColor"&&w.instanceColor&&(Re=w.instanceColor)),ve===void 0||ve.attribute!==Re||Re&&ve.data!==Re.data)return!0;X++}return r.attributesNum!==X||r.index!==F}function m(w,L,B,F){const G={},Z=L.attributes;let X=0;const $=B.getAttributes();for(const W in $)if($[W].location>=0){let ve=Z[W];ve===void 0&&(W==="instanceMatrix"&&w.instanceMatrix&&(ve=w.instanceMatrix),W==="instanceColor"&&w.instanceColor&&(ve=w.instanceColor));const Re={};Re.attribute=ve,ve&&ve.data&&(Re.data=ve.data),G[W]=Re,X++}r.attributes=G,r.attributesNum=X,r.index=F}function _(){const w=r.newAttributes;for(let L=0,B=w.length;L<B;L++)w[L]=0}function g(w){p(w,0)}function p(w,L){const B=r.newAttributes,F=r.enabledAttributes,G=r.attributeDivisors;B[w]=1,F[w]===0&&(i.enableVertexAttribArray(w),F[w]=1),G[w]!==L&&(i.vertexAttribDivisor(w,L),G[w]=L)}function y(){const w=r.newAttributes,L=r.enabledAttributes;for(let B=0,F=L.length;B<F;B++)L[B]!==w[B]&&(i.disableVertexAttribArray(B),L[B]=0)}function M(w,L,B,F,G,Z,X){X===!0?i.vertexAttribIPointer(w,L,B,G,Z):i.vertexAttribPointer(w,L,B,F,G,Z)}function x(w,L,B,F){_();const G=F.attributes,Z=B.getAttributes(),X=L.defaultAttributeValues;for(const $ in Z){const W=Z[$];if(W.location>=0){let ce=G[$];if(ce===void 0&&($==="instanceMatrix"&&w.instanceMatrix&&(ce=w.instanceMatrix),$==="instanceColor"&&w.instanceColor&&(ce=w.instanceColor)),ce!==void 0){const ve=ce.normalized,Re=ce.itemSize,it=e.get(ce);if(it===void 0)continue;const St=it.buffer,K=it.type,ue=it.bytesPerElement,Ne=K===i.INT||K===i.UNSIGNED_INT||ce.gpuType===Mh;if(ce.isInterleavedBufferAttribute){const me=ce.data,We=me.stride,Qe=ce.offset;if(me.isInstancedInterleavedBuffer){for(let je=0;je<W.locationSize;je++)p(W.location+je,me.meshPerAttribute);w.isInstancedMesh!==!0&&F._maxInstanceCount===void 0&&(F._maxInstanceCount=me.meshPerAttribute*me.count)}else for(let je=0;je<W.locationSize;je++)g(W.location+je);i.bindBuffer(i.ARRAY_BUFFER,St);for(let je=0;je<W.locationSize;je++)M(W.location+je,Re/W.locationSize,K,ve,We*ue,(Qe+Re/W.locationSize*je)*ue,Ne)}else{if(ce.isInstancedBufferAttribute){for(let me=0;me<W.locationSize;me++)p(W.location+me,ce.meshPerAttribute);w.isInstancedMesh!==!0&&F._maxInstanceCount===void 0&&(F._maxInstanceCount=ce.meshPerAttribute*ce.count)}else for(let me=0;me<W.locationSize;me++)g(W.location+me);i.bindBuffer(i.ARRAY_BUFFER,St);for(let me=0;me<W.locationSize;me++)M(W.location+me,Re/W.locationSize,K,ve,Re*ue,Re/W.locationSize*me*ue,Ne)}}else if(X!==void 0){const ve=X[$];if(ve!==void 0)switch(ve.length){case 2:i.vertexAttrib2fv(W.location,ve);break;case 3:i.vertexAttrib3fv(W.location,ve);break;case 4:i.vertexAttrib4fv(W.location,ve);break;default:i.vertexAttrib1fv(W.location,ve)}}}}y()}function A(){R();for(const w in n){const L=n[w];for(const B in L){const F=L[B];for(const G in F)h(F[G].object),delete F[G];delete L[B]}delete n[w]}}function E(w){if(n[w.id]===void 0)return;const L=n[w.id];for(const B in L){const F=L[B];for(const G in F)h(F[G].object),delete F[G];delete L[B]}delete n[w.id]}function P(w){for(const L in n){const B=n[L];if(B[w.id]===void 0)continue;const F=B[w.id];for(const G in F)h(F[G].object),delete F[G];delete B[w.id]}}function R(){b(),o=!0,r!==s&&(r=s,l(r.object))}function b(){s.geometry=null,s.program=null,s.wireframe=!1}return{setup:a,reset:R,resetDefaultState:b,dispose:A,releaseStatesOfGeometry:E,releaseStatesOfProgram:P,initAttributes:_,enableAttribute:g,disableUnusedAttributes:y}}function Yx(i,e,t){let n;function s(l){n=l}function r(l,h){i.drawArrays(n,l,h),t.update(h,n,1)}function o(l,h,u){u!==0&&(i.drawArraysInstanced(n,l,h,u),t.update(h,n,u))}function a(l,h,u){if(u===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,l,0,h,0,u);let f=0;for(let m=0;m<u;m++)f+=h[m];t.update(f,n,1)}function c(l,h,u,d){if(u===0)return;const f=e.get("WEBGL_multi_draw");if(f===null)for(let m=0;m<l.length;m++)o(l[m],h[m],d[m]);else{f.multiDrawArraysInstancedWEBGL(n,l,0,h,0,d,0,u);let m=0;for(let _=0;_<u;_++)m+=h[_]*d[_];t.update(m,n,1)}}this.setMode=s,this.render=r,this.renderInstances=o,this.renderMultiDraw=a,this.renderMultiDrawInstances=c}function Kx(i,e,t,n){let s;function r(){if(s!==void 0)return s;if(e.has("EXT_texture_filter_anisotropic")===!0){const P=e.get("EXT_texture_filter_anisotropic");s=i.getParameter(P.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else s=0;return s}function o(P){return!(P!==Xn&&n.convert(P)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function a(P){const R=P===Mo&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(P!==Ui&&n.convert(P)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&P!==ri&&!R)}function c(P){if(P==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";P="mediump"}return P==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let l=t.precision!==void 0?t.precision:"highp";const h=c(l);h!==l&&(console.warn("THREE.WebGLRenderer:",l,"not supported, using",h,"instead."),l=h);const u=t.logarithmicDepthBuffer===!0,d=t.reverseDepthBuffer===!0&&e.has("EXT_clip_control"),f=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),m=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),_=i.getParameter(i.MAX_TEXTURE_SIZE),g=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),p=i.getParameter(i.MAX_VERTEX_ATTRIBS),y=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),M=i.getParameter(i.MAX_VARYING_VECTORS),x=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),A=m>0,E=i.getParameter(i.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:r,getMaxPrecision:c,textureFormatReadable:o,textureTypeReadable:a,precision:l,logarithmicDepthBuffer:u,reverseDepthBuffer:d,maxTextures:f,maxVertexTextures:m,maxTextureSize:_,maxCubemapSize:g,maxAttributes:p,maxVertexUniforms:y,maxVaryings:M,maxFragmentUniforms:x,vertexTextures:A,maxSamples:E}}function Zx(i){const e=this;let t=null,n=0,s=!1,r=!1;const o=new ys,a=new ot,c={value:null,needsUpdate:!1};this.uniform=c,this.numPlanes=0,this.numIntersection=0,this.init=function(u,d){const f=u.length!==0||d||n!==0||s;return s=d,n=u.length,f},this.beginShadows=function(){r=!0,h(null)},this.endShadows=function(){r=!1},this.setGlobalState=function(u,d){t=h(u,d,0)},this.setState=function(u,d,f){const m=u.clippingPlanes,_=u.clipIntersection,g=u.clipShadows,p=i.get(u);if(!s||m===null||m.length===0||r&&!g)r?h(null):l();else{const y=r?0:n,M=y*4;let x=p.clippingState||null;c.value=x,x=h(m,d,M,f);for(let A=0;A!==M;++A)x[A]=t[A];p.clippingState=x,this.numIntersection=_?this.numPlanes:0,this.numPlanes+=y}};function l(){c.value!==t&&(c.value=t,c.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function h(u,d,f,m){const _=u!==null?u.length:0;let g=null;if(_!==0){if(g=c.value,m!==!0||g===null){const p=f+_*4,y=d.matrixWorldInverse;a.getNormalMatrix(y),(g===null||g.length<p)&&(g=new Float32Array(p));for(let M=0,x=f;M!==_;++M,x+=4)o.copy(u[M]).applyMatrix4(y,a),o.normal.toArray(g,x),g[x+3]=o.constant}c.value=g,c.needsUpdate=!0}return e.numPlanes=_,e.numIntersection=0,g}}function Jx(i){let e=new WeakMap;function t(o,a){return a===Rl?o.mapping=dr:a===Cl&&(o.mapping=fr),o}function n(o){if(o&&o.isTexture){const a=o.mapping;if(a===Rl||a===Cl)if(e.has(o)){const c=e.get(o).texture;return t(c,o.mapping)}else{const c=o.image;if(c&&c.height>0){const l=new lg(c.height);return l.fromEquirectangularTexture(i,o),e.set(o,l),o.addEventListener("dispose",s),t(l.texture,o.mapping)}else return null}}return o}function s(o){const a=o.target;a.removeEventListener("dispose",s);const c=e.get(a);c!==void 0&&(e.delete(a),c.dispose())}function r(){e=new WeakMap}return{get:n,dispose:r}}class qa extends Hf{constructor(e=-1,t=1,n=1,s=-1,r=.1,o=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=s,this.near=r,this.far=o,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,s,r,o){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,s=(this.top+this.bottom)/2;let r=n-e,o=n+e,a=s+t,c=s-t;if(this.view!==null&&this.view.enabled){const l=(this.right-this.left)/this.view.fullWidth/this.zoom,h=(this.top-this.bottom)/this.view.fullHeight/this.zoom;r+=l*this.view.offsetX,o=r+l*this.view.width,a-=h*this.view.offsetY,c=a-h*this.view.height}this.projectionMatrix.makeOrthographic(r,o,a,c,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const tr=4,Vu=[.125,.215,.35,.446,.526,.582],bs=20,Ic=new qa,Wu=new Ve;let Dc=null,Nc=0,Uc=0,Oc=!1;const Ms=(1+Math.sqrt(5))/2,js=1/Ms,Xu=[new v(-Ms,js,0),new v(Ms,js,0),new v(-js,0,Ms),new v(js,0,Ms),new v(0,Ms,-js),new v(0,Ms,js),new v(-1,1,-1),new v(1,1,-1),new v(-1,1,1),new v(1,1,1)];class qu{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,s=100){Dc=this._renderer.getRenderTarget(),Nc=this._renderer.getActiveCubeFace(),Uc=this._renderer.getActiveMipmapLevel(),Oc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const r=this._allocateTargets();return r.depthBuffer=!0,this._sceneToCubeUV(e,n,s,r),t>0&&this._blur(r,0,0,t),this._applyPMREM(r),this._cleanup(r),r}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=Yu(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=ju(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(Dc,Nc,Uc),this._renderer.xr.enabled=Oc,e.scissorTest=!1,Ko(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===dr||e.mapping===fr?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),Dc=this._renderer.getRenderTarget(),Nc=this._renderer.getActiveCubeFace(),Uc=this._renderer.getActiveMipmapLevel(),Oc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:Un,minFilter:Un,generateMipmaps:!1,type:Mo,format:Xn,colorSpace:vn,depthBuffer:!1},s=$u(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=$u(e,t,n);const{_lodMax:r}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=Qx(r)),this._blurMaterial=ev(r,e,t)}return s}_compileMaterial(e){const t=new jt(this._lodPlanes[0],e);this._renderer.compile(t,Ic)}_sceneToCubeUV(e,t,n,s){const a=new Cn(90,1,t,n),c=[1,-1,1,1,1,1],l=[1,1,1,-1,-1,-1],h=this._renderer,u=h.autoClear,d=h.toneMapping;h.getClearColor(Wu),h.toneMapping=is,h.autoClear=!1;const f=new _n({name:"PMREM.Background",side:Sn,depthWrite:!1,depthTest:!1}),m=new jt(new ut,f);let _=!1;const g=e.background;g?g.isColor&&(f.color.copy(g),e.background=null,_=!0):(f.color.copy(Wu),_=!0);for(let p=0;p<6;p++){const y=p%3;y===0?(a.up.set(0,c[p],0),a.lookAt(l[p],0,0)):y===1?(a.up.set(0,0,c[p]),a.lookAt(0,l[p],0)):(a.up.set(0,c[p],0),a.lookAt(0,0,l[p]));const M=this._cubeSize;Ko(s,y*M,p>2?M:0,M,M),h.setRenderTarget(s),_&&h.render(m,a),h.render(e,a)}m.geometry.dispose(),m.material.dispose(),h.toneMapping=d,h.autoClear=u,e.background=g}_textureToCubeUV(e,t){const n=this._renderer,s=e.mapping===dr||e.mapping===fr;s?(this._cubemapMaterial===null&&(this._cubemapMaterial=Yu()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=ju());const r=s?this._cubemapMaterial:this._equirectMaterial,o=new jt(this._lodPlanes[0],r),a=r.uniforms;a.envMap.value=e;const c=this._cubeSize;Ko(t,0,0,3*c,2*c),n.setRenderTarget(t),n.render(o,Ic)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const s=this._lodPlanes.length;for(let r=1;r<s;r++){const o=Math.sqrt(this._sigmas[r]*this._sigmas[r]-this._sigmas[r-1]*this._sigmas[r-1]),a=Xu[(s-r-1)%Xu.length];this._blur(e,r-1,r,o,a)}t.autoClear=n}_blur(e,t,n,s,r){const o=this._pingPongRenderTarget;this._halfBlur(e,o,t,n,s,"latitudinal",r),this._halfBlur(o,e,n,n,s,"longitudinal",r)}_halfBlur(e,t,n,s,r,o,a){const c=this._renderer,l=this._blurMaterial;o!=="latitudinal"&&o!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const h=3,u=new jt(this._lodPlanes[s],l),d=l.uniforms,f=this._sizeLods[n]-1,m=isFinite(r)?Math.PI/(2*f):2*Math.PI/(2*bs-1),_=r/m,g=isFinite(r)?1+Math.floor(h*_):bs;g>bs&&console.warn(`sigmaRadians, ${r}, is too large and will clip, as it requested ${g} samples when the maximum is set to ${bs}`);const p=[];let y=0;for(let P=0;P<bs;++P){const R=P/_,b=Math.exp(-R*R/2);p.push(b),P===0?y+=b:P<g&&(y+=2*b)}for(let P=0;P<p.length;P++)p[P]=p[P]/y;d.envMap.value=e.texture,d.samples.value=g,d.weights.value=p,d.latitudinal.value=o==="latitudinal",a&&(d.poleAxis.value=a);const{_lodMax:M}=this;d.dTheta.value=m,d.mipInt.value=M-n;const x=this._sizeLods[s],A=3*x*(s>M-tr?s-M+tr:0),E=4*(this._cubeSize-x);Ko(t,A,E,3*x,2*x),c.setRenderTarget(t),c.render(u,Ic)}}function Qx(i){const e=[],t=[],n=[];let s=i;const r=i-tr+1+Vu.length;for(let o=0;o<r;o++){const a=Math.pow(2,s);t.push(a);let c=1/a;o>i-tr?c=Vu[o-i+tr-1]:o===0&&(c=0),n.push(c);const l=1/(a-2),h=-l,u=1+l,d=[h,h,u,h,u,u,h,h,u,u,h,u],f=6,m=6,_=3,g=2,p=1,y=new Float32Array(_*m*f),M=new Float32Array(g*m*f),x=new Float32Array(p*m*f);for(let E=0;E<f;E++){const P=E%3*2/3-1,R=E>2?0:-1,b=[P,R,0,P+2/3,R,0,P+2/3,R+1,0,P,R,0,P+2/3,R+1,0,P,R+1,0];y.set(b,_*m*E),M.set(d,g*m*E);const w=[E,E,E,E,E,E];x.set(w,p*m*E)}const A=new Xt;A.setAttribute("position",new on(y,_)),A.setAttribute("uv",new on(M,g)),A.setAttribute("faceIndex",new on(x,p)),e.push(A),s>tr&&s--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function $u(i,e,t){const n=new As(i,e,t);return n.texture.mapping=Va,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function Ko(i,e,t,n,s){i.viewport.set(e,t,n,s),i.scissor.set(e,t,n,s)}function ev(i,e,t){const n=new Float32Array(bs),s=new v(0,1,0);return new di({name:"SphericalGaussianBlur",defines:{n:bs,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:s}},vertexShader:Lh(),fragmentShader:`

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
		`,blending:ns,depthTest:!1,depthWrite:!1})}function ju(){return new di({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:Lh(),fragmentShader:`

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
		`,blending:ns,depthTest:!1,depthWrite:!1})}function Yu(){return new di({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:Lh(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:ns,depthTest:!1,depthWrite:!1})}function Lh(){return`

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
	`}function tv(i){let e=new WeakMap,t=null;function n(a){if(a&&a.isTexture){const c=a.mapping,l=c===Rl||c===Cl,h=c===dr||c===fr;if(l||h){let u=e.get(a);const d=u!==void 0?u.texture.pmremVersion:0;if(a.isRenderTargetTexture&&a.pmremVersion!==d)return t===null&&(t=new qu(i)),u=l?t.fromEquirectangular(a,u):t.fromCubemap(a,u),u.texture.pmremVersion=a.pmremVersion,e.set(a,u),u.texture;if(u!==void 0)return u.texture;{const f=a.image;return l&&f&&f.height>0||h&&f&&s(f)?(t===null&&(t=new qu(i)),u=l?t.fromEquirectangular(a):t.fromCubemap(a),u.texture.pmremVersion=a.pmremVersion,e.set(a,u),a.addEventListener("dispose",r),u.texture):null}}}return a}function s(a){let c=0;const l=6;for(let h=0;h<l;h++)a[h]!==void 0&&c++;return c===l}function r(a){const c=a.target;c.removeEventListener("dispose",r);const l=e.get(c);l!==void 0&&(e.delete(c),l.dispose())}function o(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:o}}function nv(i){const e={};function t(n){if(e[n]!==void 0)return e[n];let s;switch(n){case"WEBGL_depth_texture":s=i.getExtension("WEBGL_depth_texture")||i.getExtension("MOZ_WEBGL_depth_texture")||i.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":s=i.getExtension("EXT_texture_filter_anisotropic")||i.getExtension("MOZ_EXT_texture_filter_anisotropic")||i.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":s=i.getExtension("WEBGL_compressed_texture_s3tc")||i.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":s=i.getExtension("WEBGL_compressed_texture_pvrtc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:s=i.getExtension(n)}return e[n]=s,s}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const s=t(n);return s===null&&eo("THREE.WebGLRenderer: "+n+" extension not supported."),s}}}function iv(i,e,t,n){const s={},r=new WeakMap;function o(u){const d=u.target;d.index!==null&&e.remove(d.index);for(const m in d.attributes)e.remove(d.attributes[m]);for(const m in d.morphAttributes){const _=d.morphAttributes[m];for(let g=0,p=_.length;g<p;g++)e.remove(_[g])}d.removeEventListener("dispose",o),delete s[d.id];const f=r.get(d);f&&(e.remove(f),r.delete(d)),n.releaseStatesOfGeometry(d),d.isInstancedBufferGeometry===!0&&delete d._maxInstanceCount,t.memory.geometries--}function a(u,d){return s[d.id]===!0||(d.addEventListener("dispose",o),s[d.id]=!0,t.memory.geometries++),d}function c(u){const d=u.attributes;for(const m in d)e.update(d[m],i.ARRAY_BUFFER);const f=u.morphAttributes;for(const m in f){const _=f[m];for(let g=0,p=_.length;g<p;g++)e.update(_[g],i.ARRAY_BUFFER)}}function l(u){const d=[],f=u.index,m=u.attributes.position;let _=0;if(f!==null){const y=f.array;_=f.version;for(let M=0,x=y.length;M<x;M+=3){const A=y[M+0],E=y[M+1],P=y[M+2];d.push(A,E,E,P,P,A)}}else if(m!==void 0){const y=m.array;_=m.version;for(let M=0,x=y.length/3-1;M<x;M+=3){const A=M+0,E=M+1,P=M+2;d.push(A,E,E,P,P,A)}}else return;const g=new(Nf(d)?kf:Ch)(d,1);g.version=_;const p=r.get(u);p&&e.remove(p),r.set(u,g)}function h(u){const d=r.get(u);if(d){const f=u.index;f!==null&&d.version<f.version&&l(u)}else l(u);return r.get(u)}return{get:a,update:c,getWireframeAttribute:h}}function sv(i,e,t){let n;function s(d){n=d}let r,o;function a(d){r=d.type,o=d.bytesPerElement}function c(d,f){i.drawElements(n,f,r,d*o),t.update(f,n,1)}function l(d,f,m){m!==0&&(i.drawElementsInstanced(n,f,r,d*o,m),t.update(f,n,m))}function h(d,f,m){if(m===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,f,0,r,d,0,m);let g=0;for(let p=0;p<m;p++)g+=f[p];t.update(g,n,1)}function u(d,f,m,_){if(m===0)return;const g=e.get("WEBGL_multi_draw");if(g===null)for(let p=0;p<d.length;p++)l(d[p]/o,f[p],_[p]);else{g.multiDrawElementsInstancedWEBGL(n,f,0,r,d,0,_,0,m);let p=0;for(let y=0;y<m;y++)p+=f[y]*_[y];t.update(p,n,1)}}this.setMode=s,this.setIndex=a,this.render=c,this.renderInstances=l,this.renderMultiDraw=h,this.renderMultiDrawInstances=u}function rv(i){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(r,o,a){switch(t.calls++,o){case i.TRIANGLES:t.triangles+=a*(r/3);break;case i.LINES:t.lines+=a*(r/2);break;case i.LINE_STRIP:t.lines+=a*(r-1);break;case i.LINE_LOOP:t.lines+=a*r;break;case i.POINTS:t.points+=a*r;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",o);break}}function s(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:s,update:n}}function ov(i,e,t){const n=new WeakMap,s=new bt;function r(o,a,c){const l=o.morphTargetInfluences,h=a.morphAttributes.position||a.morphAttributes.normal||a.morphAttributes.color,u=h!==void 0?h.length:0;let d=n.get(a);if(d===void 0||d.count!==u){let b=function(){P.dispose(),n.delete(a),a.removeEventListener("dispose",b)};d!==void 0&&d.texture.dispose();const f=a.morphAttributes.position!==void 0,m=a.morphAttributes.normal!==void 0,_=a.morphAttributes.color!==void 0,g=a.morphAttributes.position||[],p=a.morphAttributes.normal||[],y=a.morphAttributes.color||[];let M=0;f===!0&&(M=1),m===!0&&(M=2),_===!0&&(M=3);let x=a.attributes.position.count*M,A=1;x>e.maxTextureSize&&(A=Math.ceil(x/e.maxTextureSize),x=e.maxTextureSize);const E=new Float32Array(x*A*4*u),P=new Of(E,x,A,u);P.type=ri,P.needsUpdate=!0;const R=M*4;for(let w=0;w<u;w++){const L=g[w],B=p[w],F=y[w],G=x*A*4*w;for(let Z=0;Z<L.count;Z++){const X=Z*R;f===!0&&(s.fromBufferAttribute(L,Z),E[G+X+0]=s.x,E[G+X+1]=s.y,E[G+X+2]=s.z,E[G+X+3]=0),m===!0&&(s.fromBufferAttribute(B,Z),E[G+X+4]=s.x,E[G+X+5]=s.y,E[G+X+6]=s.z,E[G+X+7]=0),_===!0&&(s.fromBufferAttribute(F,Z),E[G+X+8]=s.x,E[G+X+9]=s.y,E[G+X+10]=s.z,E[G+X+11]=F.itemSize===4?s.w:1)}}d={count:u,texture:P,size:new re(x,A)},n.set(a,d),a.addEventListener("dispose",b)}if(o.isInstancedMesh===!0&&o.morphTexture!==null)c.getUniforms().setValue(i,"morphTexture",o.morphTexture,t);else{let f=0;for(let _=0;_<l.length;_++)f+=l[_];const m=a.morphTargetsRelative?1:1-f;c.getUniforms().setValue(i,"morphTargetBaseInfluence",m),c.getUniforms().setValue(i,"morphTargetInfluences",l)}c.getUniforms().setValue(i,"morphTargetsTexture",d.texture,t),c.getUniforms().setValue(i,"morphTargetsTextureSize",d.size)}return{update:r}}function av(i,e,t,n){let s=new WeakMap;function r(c){const l=n.render.frame,h=c.geometry,u=e.get(c,h);if(s.get(u)!==l&&(e.update(u),s.set(u,l)),c.isInstancedMesh&&(c.hasEventListener("dispose",a)===!1&&c.addEventListener("dispose",a),s.get(c)!==l&&(t.update(c.instanceMatrix,i.ARRAY_BUFFER),c.instanceColor!==null&&t.update(c.instanceColor,i.ARRAY_BUFFER),s.set(c,l))),c.isSkinnedMesh){const d=c.skeleton;s.get(d)!==l&&(d.update(),s.set(d,l))}return u}function o(){s=new WeakMap}function a(c){const l=c.target;l.removeEventListener("dispose",a),t.remove(l.instanceMatrix),l.instanceColor!==null&&t.remove(l.instanceColor)}return{update:r,dispose:o}}class Wf extends rn{constructor(e,t,n,s,r,o,a,c,l,h=or){if(h!==or&&h!==gr)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&h===or&&(n=Ts),n===void 0&&h===gr&&(n=mr),super(null,s,r,o,a,c,h,n,l),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=a!==void 0?a:xn,this.minFilter=c!==void 0?c:xn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const Xf=new rn,Ku=new Wf(1,1),qf=new Of,$f=new $0,jf=new Gf,Zu=[],Ju=[],Qu=new Float32Array(16),ed=new Float32Array(9),td=new Float32Array(4);function Tr(i,e,t){const n=i[0];if(n<=0||n>0)return i;const s=e*t;let r=Zu[s];if(r===void 0&&(r=new Float32Array(s),Zu[s]=r),e!==0){n.toArray(r,0);for(let o=1,a=0;o!==e;++o)a+=t,i[o].toArray(r,a)}return r}function en(i,e){if(i.length!==e.length)return!1;for(let t=0,n=i.length;t<n;t++)if(i[t]!==e[t])return!1;return!0}function tn(i,e){for(let t=0,n=e.length;t<n;t++)i[t]=e[t]}function $a(i,e){let t=Ju[e];t===void 0&&(t=new Int32Array(e),Ju[e]=t);for(let n=0;n!==e;++n)t[n]=i.allocateTextureUnit();return t}function cv(i,e){const t=this.cache;t[0]!==e&&(i.uniform1f(this.addr,e),t[0]=e)}function lv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(en(t,e))return;i.uniform2fv(this.addr,e),tn(t,e)}}function hv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(i.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(en(t,e))return;i.uniform3fv(this.addr,e),tn(t,e)}}function uv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(en(t,e))return;i.uniform4fv(this.addr,e),tn(t,e)}}function dv(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(en(t,e))return;i.uniformMatrix2fv(this.addr,!1,e),tn(t,e)}else{if(en(t,n))return;td.set(n),i.uniformMatrix2fv(this.addr,!1,td),tn(t,n)}}function fv(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(en(t,e))return;i.uniformMatrix3fv(this.addr,!1,e),tn(t,e)}else{if(en(t,n))return;ed.set(n),i.uniformMatrix3fv(this.addr,!1,ed),tn(t,n)}}function pv(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(en(t,e))return;i.uniformMatrix4fv(this.addr,!1,e),tn(t,e)}else{if(en(t,n))return;Qu.set(n),i.uniformMatrix4fv(this.addr,!1,Qu),tn(t,n)}}function mv(i,e){const t=this.cache;t[0]!==e&&(i.uniform1i(this.addr,e),t[0]=e)}function gv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(en(t,e))return;i.uniform2iv(this.addr,e),tn(t,e)}}function _v(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(en(t,e))return;i.uniform3iv(this.addr,e),tn(t,e)}}function xv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(en(t,e))return;i.uniform4iv(this.addr,e),tn(t,e)}}function vv(i,e){const t=this.cache;t[0]!==e&&(i.uniform1ui(this.addr,e),t[0]=e)}function yv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(en(t,e))return;i.uniform2uiv(this.addr,e),tn(t,e)}}function Mv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(en(t,e))return;i.uniform3uiv(this.addr,e),tn(t,e)}}function wv(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(en(t,e))return;i.uniform4uiv(this.addr,e),tn(t,e)}}function bv(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s);let r;this.type===i.SAMPLER_2D_SHADOW?(Ku.compareFunction=Df,r=Ku):r=Xf,t.setTexture2D(e||r,s)}function Sv(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture3D(e||$f,s)}function Ev(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTextureCube(e||jf,s)}function Tv(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture2DArray(e||qf,s)}function Av(i){switch(i){case 5126:return cv;case 35664:return lv;case 35665:return hv;case 35666:return uv;case 35674:return dv;case 35675:return fv;case 35676:return pv;case 5124:case 35670:return mv;case 35667:case 35671:return gv;case 35668:case 35672:return _v;case 35669:case 35673:return xv;case 5125:return vv;case 36294:return yv;case 36295:return Mv;case 36296:return wv;case 35678:case 36198:case 36298:case 36306:case 35682:return bv;case 35679:case 36299:case 36307:return Sv;case 35680:case 36300:case 36308:case 36293:return Ev;case 36289:case 36303:case 36311:case 36292:return Tv}}function Rv(i,e){i.uniform1fv(this.addr,e)}function Cv(i,e){const t=Tr(e,this.size,2);i.uniform2fv(this.addr,t)}function Pv(i,e){const t=Tr(e,this.size,3);i.uniform3fv(this.addr,t)}function Lv(i,e){const t=Tr(e,this.size,4);i.uniform4fv(this.addr,t)}function Iv(i,e){const t=Tr(e,this.size,4);i.uniformMatrix2fv(this.addr,!1,t)}function Dv(i,e){const t=Tr(e,this.size,9);i.uniformMatrix3fv(this.addr,!1,t)}function Nv(i,e){const t=Tr(e,this.size,16);i.uniformMatrix4fv(this.addr,!1,t)}function Uv(i,e){i.uniform1iv(this.addr,e)}function Ov(i,e){i.uniform2iv(this.addr,e)}function Fv(i,e){i.uniform3iv(this.addr,e)}function Bv(i,e){i.uniform4iv(this.addr,e)}function kv(i,e){i.uniform1uiv(this.addr,e)}function zv(i,e){i.uniform2uiv(this.addr,e)}function Hv(i,e){i.uniform3uiv(this.addr,e)}function Gv(i,e){i.uniform4uiv(this.addr,e)}function Vv(i,e,t){const n=this.cache,s=e.length,r=$a(t,s);en(n,r)||(i.uniform1iv(this.addr,r),tn(n,r));for(let o=0;o!==s;++o)t.setTexture2D(e[o]||Xf,r[o])}function Wv(i,e,t){const n=this.cache,s=e.length,r=$a(t,s);en(n,r)||(i.uniform1iv(this.addr,r),tn(n,r));for(let o=0;o!==s;++o)t.setTexture3D(e[o]||$f,r[o])}function Xv(i,e,t){const n=this.cache,s=e.length,r=$a(t,s);en(n,r)||(i.uniform1iv(this.addr,r),tn(n,r));for(let o=0;o!==s;++o)t.setTextureCube(e[o]||jf,r[o])}function qv(i,e,t){const n=this.cache,s=e.length,r=$a(t,s);en(n,r)||(i.uniform1iv(this.addr,r),tn(n,r));for(let o=0;o!==s;++o)t.setTexture2DArray(e[o]||qf,r[o])}function $v(i){switch(i){case 5126:return Rv;case 35664:return Cv;case 35665:return Pv;case 35666:return Lv;case 35674:return Iv;case 35675:return Dv;case 35676:return Nv;case 5124:case 35670:return Uv;case 35667:case 35671:return Ov;case 35668:case 35672:return Fv;case 35669:case 35673:return Bv;case 5125:return kv;case 36294:return zv;case 36295:return Hv;case 36296:return Gv;case 35678:case 36198:case 36298:case 36306:case 35682:return Vv;case 35679:case 36299:case 36307:return Wv;case 35680:case 36300:case 36308:case 36293:return Xv;case 36289:case 36303:case 36311:case 36292:return qv}}class jv{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=Av(t.type)}}class Yv{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=$v(t.type)}}class Kv{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const s=this.seq;for(let r=0,o=s.length;r!==o;++r){const a=s[r];a.setValue(e,t[a.id],n)}}}const Fc=/(\w+)(\])?(\[|\.)?/g;function nd(i,e){i.seq.push(e),i.map[e.id]=e}function Zv(i,e,t){const n=i.name,s=n.length;for(Fc.lastIndex=0;;){const r=Fc.exec(n),o=Fc.lastIndex;let a=r[1];const c=r[2]==="]",l=r[3];if(c&&(a=a|0),l===void 0||l==="["&&o+2===s){nd(t,l===void 0?new jv(a,i,e):new Yv(a,i,e));break}else{let u=t.map[a];u===void 0&&(u=new Kv(a),nd(t,u)),t=u}}}class Sa{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let s=0;s<n;++s){const r=e.getActiveUniform(t,s),o=e.getUniformLocation(t,r.name);Zv(r,o,this)}}setValue(e,t,n,s){const r=this.map[t];r!==void 0&&r.setValue(e,n,s)}setOptional(e,t,n){const s=t[n];s!==void 0&&this.setValue(e,n,s)}static upload(e,t,n,s){for(let r=0,o=t.length;r!==o;++r){const a=t[r],c=n[a.id];c.needsUpdate!==!1&&a.setValue(e,c.value,s)}}static seqWithValue(e,t){const n=[];for(let s=0,r=e.length;s!==r;++s){const o=e[s];o.id in t&&n.push(o)}return n}}function id(i,e,t){const n=i.createShader(e);return i.shaderSource(n,t),i.compileShader(n),n}const Jv=37297;let Qv=0;function ey(i,e){const t=i.split(`
`),n=[],s=Math.max(e-6,0),r=Math.min(e+6,t.length);for(let o=s;o<r;o++){const a=o+1;n.push(`${a===e?">":" "} ${a}: ${t[o]}`)}return n.join(`
`)}const sd=new ot;function ty(i){pt._getMatrix(sd,pt.workingColorSpace,i);const e=`mat3( ${sd.elements.map(t=>t.toFixed(4))} )`;switch(pt.getTransfer(i)){case Wa:return[e,"LinearTransferOETF"];case Nt:return[e,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",i),[e,"LinearTransferOETF"]}}function rd(i,e,t){const n=i.getShaderParameter(e,i.COMPILE_STATUS),s=i.getShaderInfoLog(e).trim();if(n&&s==="")return"";const r=/ERROR: 0:(\d+)/.exec(s);if(r){const o=parseInt(r[1]);return t.toUpperCase()+`

`+s+`

`+ey(i.getShaderSource(e),o)}else return s}function ny(i,e){const t=ty(e);return[`vec4 ${i}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}function iy(i,e){let t;switch(e){case i0:t="Linear";break;case s0:t="Reinhard";break;case r0:t="Cineon";break;case o0:t="ACESFilmic";break;case c0:t="AgX";break;case l0:t="Neutral";break;case a0:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+i+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const Zo=new v;function sy(){pt.getLuminanceCoefficients(Zo);const i=Zo.x.toFixed(4),e=Zo.y.toFixed(4),t=Zo.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function ry(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(to).join(`
`)}function oy(i){const e=[];for(const t in i){const n=i[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function ay(i,e){const t={},n=i.getProgramParameter(e,i.ACTIVE_ATTRIBUTES);for(let s=0;s<n;s++){const r=i.getActiveAttrib(e,s),o=r.name;let a=1;r.type===i.FLOAT_MAT2&&(a=2),r.type===i.FLOAT_MAT3&&(a=3),r.type===i.FLOAT_MAT4&&(a=4),t[o]={type:r.type,location:i.getAttribLocation(e,o),locationSize:a}}return t}function to(i){return i!==""}function od(i,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function ad(i,e){return i.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const cy=/^[ \t]*#include +<([\w\d./]+)>/gm;function sh(i){return i.replace(cy,hy)}const ly=new Map;function hy(i,e){let t=lt[e];if(t===void 0){const n=ly.get(e);if(n!==void 0)t=lt[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return sh(t)}const uy=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function cd(i){return i.replace(uy,dy)}function dy(i,e,t,n){let s="";for(let r=parseInt(e);r<parseInt(t);r++)s+=n.replace(/\[\s*i\s*\]/g,"[ "+r+" ]").replace(/UNROLLED_LOOP_INDEX/g,r);return s}function ld(i){let e=`precision ${i.precision} float;
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
#define LOW_PRECISION`),e}function fy(i){let e="SHADOWMAP_TYPE_BASIC";return i.shadowMapType===xf?e="SHADOWMAP_TYPE_PCF":i.shadowMapType===Om?e="SHADOWMAP_TYPE_PCF_SOFT":i.shadowMapType===Ai&&(e="SHADOWMAP_TYPE_VSM"),e}function py(i){let e="ENVMAP_TYPE_CUBE";if(i.envMap)switch(i.envMapMode){case dr:case fr:e="ENVMAP_TYPE_CUBE";break;case Va:e="ENVMAP_TYPE_CUBE_UV";break}return e}function my(i){let e="ENVMAP_MODE_REFLECTION";if(i.envMap)switch(i.envMapMode){case fr:e="ENVMAP_MODE_REFRACTION";break}return e}function gy(i){let e="ENVMAP_BLENDING_NONE";if(i.envMap)switch(i.combine){case vf:e="ENVMAP_BLENDING_MULTIPLY";break;case t0:e="ENVMAP_BLENDING_MIX";break;case n0:e="ENVMAP_BLENDING_ADD";break}return e}function _y(i){const e=i.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),112)),texelHeight:n,maxMip:t}}function xy(i,e,t,n){const s=i.getContext(),r=t.defines;let o=t.vertexShader,a=t.fragmentShader;const c=fy(t),l=py(t),h=my(t),u=gy(t),d=_y(t),f=ry(t),m=oy(r),_=s.createProgram();let g,p,y=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(g=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m].filter(to).join(`
`),g.length>0&&(g+=`
`),p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m].filter(to).join(`
`),p.length>0&&(p+=`
`)):(g=[ld(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+h:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+c:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(to).join(`
`),p=[ld(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+l:"",t.envMap?"#define "+h:"",t.envMap?"#define "+u:"",d?"#define CUBEUV_TEXEL_WIDTH "+d.texelWidth:"",d?"#define CUBEUV_TEXEL_HEIGHT "+d.texelHeight:"",d?"#define CUBEUV_MAX_MIP "+d.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+c:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==is?"#define TONE_MAPPING":"",t.toneMapping!==is?lt.tonemapping_pars_fragment:"",t.toneMapping!==is?iy("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",lt.colorspace_pars_fragment,ny("linearToOutputTexel",t.outputColorSpace),sy(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(to).join(`
`)),o=sh(o),o=od(o,t),o=ad(o,t),a=sh(a),a=od(a,t),a=ad(a,t),o=cd(o),a=cd(a),t.isRawShaderMaterial!==!0&&(y=`#version 300 es
`,g=[f,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+g,p=["#define varying in",t.glslVersion===Mu?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Mu?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+p);const M=y+g+o,x=y+p+a,A=id(s,s.VERTEX_SHADER,M),E=id(s,s.FRAGMENT_SHADER,x);s.attachShader(_,A),s.attachShader(_,E),t.index0AttributeName!==void 0?s.bindAttribLocation(_,0,t.index0AttributeName):t.morphTargets===!0&&s.bindAttribLocation(_,0,"position"),s.linkProgram(_);function P(L){if(i.debug.checkShaderErrors){const B=s.getProgramInfoLog(_).trim(),F=s.getShaderInfoLog(A).trim(),G=s.getShaderInfoLog(E).trim();let Z=!0,X=!0;if(s.getProgramParameter(_,s.LINK_STATUS)===!1)if(Z=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(s,_,A,E);else{const $=rd(s,A,"vertex"),W=rd(s,E,"fragment");console.error("THREE.WebGLProgram: Shader Error "+s.getError()+" - VALIDATE_STATUS "+s.getProgramParameter(_,s.VALIDATE_STATUS)+`

Material Name: `+L.name+`
Material Type: `+L.type+`

Program Info Log: `+B+`
`+$+`
`+W)}else B!==""?console.warn("THREE.WebGLProgram: Program Info Log:",B):(F===""||G==="")&&(X=!1);X&&(L.diagnostics={runnable:Z,programLog:B,vertexShader:{log:F,prefix:g},fragmentShader:{log:G,prefix:p}})}s.deleteShader(A),s.deleteShader(E),R=new Sa(s,_),b=ay(s,_)}let R;this.getUniforms=function(){return R===void 0&&P(this),R};let b;this.getAttributes=function(){return b===void 0&&P(this),b};let w=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return w===!1&&(w=s.getProgramParameter(_,Jv)),w},this.destroy=function(){n.releaseStatesOfProgram(this),s.deleteProgram(_),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=Qv++,this.cacheKey=e,this.usedTimes=1,this.program=_,this.vertexShader=A,this.fragmentShader=E,this}let vy=0;class yy{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,s=this._getShaderStage(t),r=this._getShaderStage(n),o=this._getShaderCacheForMaterial(e);return o.has(s)===!1&&(o.add(s),s.usedTimes++),o.has(r)===!1&&(o.add(r),r.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new My(e),t.set(e,n)),n}}class My{constructor(e){this.id=vy++,this.code=e,this.usedTimes=0}}function wy(i,e,t,n,s,r,o){const a=new Ff,c=new yy,l=new Set,h=[],u=s.logarithmicDepthBuffer,d=s.vertexTextures;let f=s.precision;const m={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function _(b){return l.add(b),b===0?"uv":`uv${b}`}function g(b,w,L,B,F){const G=B.fog,Z=F.geometry,X=b.isMeshStandardMaterial?B.environment:null,$=(b.isMeshStandardMaterial?t:e).get(b.envMap||X),W=$&&$.mapping===Va?$.image.height:null,ce=m[b.type];b.precision!==null&&(f=s.getMaxPrecision(b.precision),f!==b.precision&&console.warn("THREE.WebGLProgram.getParameters:",b.precision,"not supported, using",f,"instead."));const ve=Z.morphAttributes.position||Z.morphAttributes.normal||Z.morphAttributes.color,Re=ve!==void 0?ve.length:0;let it=0;Z.morphAttributes.position!==void 0&&(it=1),Z.morphAttributes.normal!==void 0&&(it=2),Z.morphAttributes.color!==void 0&&(it=3);let St,K,ue,Ne;if(ce){const Rt=ci[ce];St=Rt.vertexShader,K=Rt.fragmentShader}else St=b.vertexShader,K=b.fragmentShader,c.update(b),ue=c.getVertexShaderID(b),Ne=c.getFragmentShaderID(b);const me=i.getRenderTarget(),We=i.state.buffers.depth.getReversed(),Qe=F.isInstancedMesh===!0,je=F.isBatchedMesh===!0,_t=!!b.map,ee=!!b.matcap,he=!!$,I=!!b.aoMap,ze=!!b.lightMap,ae=!!b.bumpMap,Le=!!b.normalMap,_e=!!b.displacementMap,qe=!!b.emissiveMap,Ce=!!b.metalnessMap,C=!!b.roughnessMap,S=b.anisotropy>0,k=b.clearcoat>0,j=b.dispersion>0,te=b.iridescence>0,Y=b.sheen>0,Oe=b.transmission>0,Me=S&&!!b.anisotropyMap,Pe=k&&!!b.clearcoatMap,ft=k&&!!b.clearcoatNormalMap,le=k&&!!b.clearcoatRoughnessMap,Ie=te&&!!b.iridescenceMap,$e=te&&!!b.iridescenceThicknessMap,Je=Y&&!!b.sheenColorMap,De=Y&&!!b.sheenRoughnessMap,mt=!!b.specularMap,ct=!!b.specularColorMap,Ot=!!b.specularIntensityMap,D=Oe&&!!b.transmissionMap,we=Oe&&!!b.thicknessMap,q=!!b.gradientMap,J=!!b.alphaMap,Ee=b.alphaTest>0,be=!!b.alphaHash,st=!!b.extensions;let qt=is;b.toneMapped&&(me===null||me.isXRRenderTarget===!0)&&(qt=i.toneMapping);const un={shaderID:ce,shaderType:b.type,shaderName:b.name,vertexShader:St,fragmentShader:K,defines:b.defines,customVertexShaderID:ue,customFragmentShaderID:Ne,isRawShaderMaterial:b.isRawShaderMaterial===!0,glslVersion:b.glslVersion,precision:f,batching:je,batchingColor:je&&F._colorsTexture!==null,instancing:Qe,instancingColor:Qe&&F.instanceColor!==null,instancingMorph:Qe&&F.morphTexture!==null,supportsVertexTextures:d,outputColorSpace:me===null?i.outputColorSpace:me.isXRRenderTarget===!0?me.texture.colorSpace:vn,alphaToCoverage:!!b.alphaToCoverage,map:_t,matcap:ee,envMap:he,envMapMode:he&&$.mapping,envMapCubeUVHeight:W,aoMap:I,lightMap:ze,bumpMap:ae,normalMap:Le,displacementMap:d&&_e,emissiveMap:qe,normalMapObjectSpace:Le&&b.normalMapType===m0,normalMapTangentSpace:Le&&b.normalMapType===If,metalnessMap:Ce,roughnessMap:C,anisotropy:S,anisotropyMap:Me,clearcoat:k,clearcoatMap:Pe,clearcoatNormalMap:ft,clearcoatRoughnessMap:le,dispersion:j,iridescence:te,iridescenceMap:Ie,iridescenceThicknessMap:$e,sheen:Y,sheenColorMap:Je,sheenRoughnessMap:De,specularMap:mt,specularColorMap:ct,specularIntensityMap:Ot,transmission:Oe,transmissionMap:D,thicknessMap:we,gradientMap:q,opaque:b.transparent===!1&&b.blending===rr&&b.alphaToCoverage===!1,alphaMap:J,alphaTest:Ee,alphaHash:be,combine:b.combine,mapUv:_t&&_(b.map.channel),aoMapUv:I&&_(b.aoMap.channel),lightMapUv:ze&&_(b.lightMap.channel),bumpMapUv:ae&&_(b.bumpMap.channel),normalMapUv:Le&&_(b.normalMap.channel),displacementMapUv:_e&&_(b.displacementMap.channel),emissiveMapUv:qe&&_(b.emissiveMap.channel),metalnessMapUv:Ce&&_(b.metalnessMap.channel),roughnessMapUv:C&&_(b.roughnessMap.channel),anisotropyMapUv:Me&&_(b.anisotropyMap.channel),clearcoatMapUv:Pe&&_(b.clearcoatMap.channel),clearcoatNormalMapUv:ft&&_(b.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:le&&_(b.clearcoatRoughnessMap.channel),iridescenceMapUv:Ie&&_(b.iridescenceMap.channel),iridescenceThicknessMapUv:$e&&_(b.iridescenceThicknessMap.channel),sheenColorMapUv:Je&&_(b.sheenColorMap.channel),sheenRoughnessMapUv:De&&_(b.sheenRoughnessMap.channel),specularMapUv:mt&&_(b.specularMap.channel),specularColorMapUv:ct&&_(b.specularColorMap.channel),specularIntensityMapUv:Ot&&_(b.specularIntensityMap.channel),transmissionMapUv:D&&_(b.transmissionMap.channel),thicknessMapUv:we&&_(b.thicknessMap.channel),alphaMapUv:J&&_(b.alphaMap.channel),vertexTangents:!!Z.attributes.tangent&&(Le||S),vertexColors:b.vertexColors,vertexAlphas:b.vertexColors===!0&&!!Z.attributes.color&&Z.attributes.color.itemSize===4,pointsUvs:F.isPoints===!0&&!!Z.attributes.uv&&(_t||J),fog:!!G,useFog:b.fog===!0,fogExp2:!!G&&G.isFogExp2,flatShading:b.flatShading===!0,sizeAttenuation:b.sizeAttenuation===!0,logarithmicDepthBuffer:u,reverseDepthBuffer:We,skinning:F.isSkinnedMesh===!0,morphTargets:Z.morphAttributes.position!==void 0,morphNormals:Z.morphAttributes.normal!==void 0,morphColors:Z.morphAttributes.color!==void 0,morphTargetsCount:Re,morphTextureStride:it,numDirLights:w.directional.length,numPointLights:w.point.length,numSpotLights:w.spot.length,numSpotLightMaps:w.spotLightMap.length,numRectAreaLights:w.rectArea.length,numHemiLights:w.hemi.length,numDirLightShadows:w.directionalShadowMap.length,numPointLightShadows:w.pointShadowMap.length,numSpotLightShadows:w.spotShadowMap.length,numSpotLightShadowsWithMaps:w.numSpotLightShadowsWithMaps,numLightProbes:w.numLightProbes,numClippingPlanes:o.numPlanes,numClipIntersection:o.numIntersection,dithering:b.dithering,shadowMapEnabled:i.shadowMap.enabled&&L.length>0,shadowMapType:i.shadowMap.type,toneMapping:qt,decodeVideoTexture:_t&&b.map.isVideoTexture===!0&&pt.getTransfer(b.map.colorSpace)===Nt,decodeVideoTextureEmissive:qe&&b.emissiveMap.isVideoTexture===!0&&pt.getTransfer(b.emissiveMap.colorSpace)===Nt,premultipliedAlpha:b.premultipliedAlpha,doubleSided:b.side===Pn,flipSided:b.side===Sn,useDepthPacking:b.depthPacking>=0,depthPacking:b.depthPacking||0,index0AttributeName:b.index0AttributeName,extensionClipCullDistance:st&&b.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(st&&b.extensions.multiDraw===!0||je)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:b.customProgramCacheKey()};return un.vertexUv1s=l.has(1),un.vertexUv2s=l.has(2),un.vertexUv3s=l.has(3),l.clear(),un}function p(b){const w=[];if(b.shaderID?w.push(b.shaderID):(w.push(b.customVertexShaderID),w.push(b.customFragmentShaderID)),b.defines!==void 0)for(const L in b.defines)w.push(L),w.push(b.defines[L]);return b.isRawShaderMaterial===!1&&(y(w,b),M(w,b),w.push(i.outputColorSpace)),w.push(b.customProgramCacheKey),w.join()}function y(b,w){b.push(w.precision),b.push(w.outputColorSpace),b.push(w.envMapMode),b.push(w.envMapCubeUVHeight),b.push(w.mapUv),b.push(w.alphaMapUv),b.push(w.lightMapUv),b.push(w.aoMapUv),b.push(w.bumpMapUv),b.push(w.normalMapUv),b.push(w.displacementMapUv),b.push(w.emissiveMapUv),b.push(w.metalnessMapUv),b.push(w.roughnessMapUv),b.push(w.anisotropyMapUv),b.push(w.clearcoatMapUv),b.push(w.clearcoatNormalMapUv),b.push(w.clearcoatRoughnessMapUv),b.push(w.iridescenceMapUv),b.push(w.iridescenceThicknessMapUv),b.push(w.sheenColorMapUv),b.push(w.sheenRoughnessMapUv),b.push(w.specularMapUv),b.push(w.specularColorMapUv),b.push(w.specularIntensityMapUv),b.push(w.transmissionMapUv),b.push(w.thicknessMapUv),b.push(w.combine),b.push(w.fogExp2),b.push(w.sizeAttenuation),b.push(w.morphTargetsCount),b.push(w.morphAttributeCount),b.push(w.numDirLights),b.push(w.numPointLights),b.push(w.numSpotLights),b.push(w.numSpotLightMaps),b.push(w.numHemiLights),b.push(w.numRectAreaLights),b.push(w.numDirLightShadows),b.push(w.numPointLightShadows),b.push(w.numSpotLightShadows),b.push(w.numSpotLightShadowsWithMaps),b.push(w.numLightProbes),b.push(w.shadowMapType),b.push(w.toneMapping),b.push(w.numClippingPlanes),b.push(w.numClipIntersection),b.push(w.depthPacking)}function M(b,w){a.disableAll(),w.supportsVertexTextures&&a.enable(0),w.instancing&&a.enable(1),w.instancingColor&&a.enable(2),w.instancingMorph&&a.enable(3),w.matcap&&a.enable(4),w.envMap&&a.enable(5),w.normalMapObjectSpace&&a.enable(6),w.normalMapTangentSpace&&a.enable(7),w.clearcoat&&a.enable(8),w.iridescence&&a.enable(9),w.alphaTest&&a.enable(10),w.vertexColors&&a.enable(11),w.vertexAlphas&&a.enable(12),w.vertexUv1s&&a.enable(13),w.vertexUv2s&&a.enable(14),w.vertexUv3s&&a.enable(15),w.vertexTangents&&a.enable(16),w.anisotropy&&a.enable(17),w.alphaHash&&a.enable(18),w.batching&&a.enable(19),w.dispersion&&a.enable(20),w.batchingColor&&a.enable(21),b.push(a.mask),a.disableAll(),w.fog&&a.enable(0),w.useFog&&a.enable(1),w.flatShading&&a.enable(2),w.logarithmicDepthBuffer&&a.enable(3),w.reverseDepthBuffer&&a.enable(4),w.skinning&&a.enable(5),w.morphTargets&&a.enable(6),w.morphNormals&&a.enable(7),w.morphColors&&a.enable(8),w.premultipliedAlpha&&a.enable(9),w.shadowMapEnabled&&a.enable(10),w.doubleSided&&a.enable(11),w.flipSided&&a.enable(12),w.useDepthPacking&&a.enable(13),w.dithering&&a.enable(14),w.transmission&&a.enable(15),w.sheen&&a.enable(16),w.opaque&&a.enable(17),w.pointsUvs&&a.enable(18),w.decodeVideoTexture&&a.enable(19),w.decodeVideoTextureEmissive&&a.enable(20),w.alphaToCoverage&&a.enable(21),b.push(a.mask)}function x(b){const w=m[b.type];let L;if(w){const B=ci[w];L=rg.clone(B.uniforms)}else L=b.uniforms;return L}function A(b,w){let L;for(let B=0,F=h.length;B<F;B++){const G=h[B];if(G.cacheKey===w){L=G,++L.usedTimes;break}}return L===void 0&&(L=new xy(i,w,b,r),h.push(L)),L}function E(b){if(--b.usedTimes===0){const w=h.indexOf(b);h[w]=h[h.length-1],h.pop(),b.destroy()}}function P(b){c.remove(b)}function R(){c.dispose()}return{getParameters:g,getProgramCacheKey:p,getUniforms:x,acquireProgram:A,releaseProgram:E,releaseShaderCache:P,programs:h,dispose:R}}function by(){let i=new WeakMap;function e(o){return i.has(o)}function t(o){let a=i.get(o);return a===void 0&&(a={},i.set(o,a)),a}function n(o){i.delete(o)}function s(o,a,c){i.get(o)[a]=c}function r(){i=new WeakMap}return{has:e,get:t,remove:n,update:s,dispose:r}}function Sy(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.material.id!==e.material.id?i.material.id-e.material.id:i.z!==e.z?i.z-e.z:i.id-e.id}function hd(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.z!==e.z?e.z-i.z:i.id-e.id}function ud(){const i=[];let e=0;const t=[],n=[],s=[];function r(){e=0,t.length=0,n.length=0,s.length=0}function o(u,d,f,m,_,g){let p=i[e];return p===void 0?(p={id:u.id,object:u,geometry:d,material:f,groupOrder:m,renderOrder:u.renderOrder,z:_,group:g},i[e]=p):(p.id=u.id,p.object=u,p.geometry=d,p.material=f,p.groupOrder=m,p.renderOrder=u.renderOrder,p.z=_,p.group=g),e++,p}function a(u,d,f,m,_,g){const p=o(u,d,f,m,_,g);f.transmission>0?n.push(p):f.transparent===!0?s.push(p):t.push(p)}function c(u,d,f,m,_,g){const p=o(u,d,f,m,_,g);f.transmission>0?n.unshift(p):f.transparent===!0?s.unshift(p):t.unshift(p)}function l(u,d){t.length>1&&t.sort(u||Sy),n.length>1&&n.sort(d||hd),s.length>1&&s.sort(d||hd)}function h(){for(let u=e,d=i.length;u<d;u++){const f=i[u];if(f.id===null)break;f.id=null,f.object=null,f.geometry=null,f.material=null,f.group=null}}return{opaque:t,transmissive:n,transparent:s,init:r,push:a,unshift:c,finish:h,sort:l}}function Ey(){let i=new WeakMap;function e(n,s){const r=i.get(n);let o;return r===void 0?(o=new ud,i.set(n,[o])):s>=r.length?(o=new ud,r.push(o)):o=r[s],o}function t(){i=new WeakMap}return{get:e,dispose:t}}function Ty(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new v,color:new Ve};break;case"SpotLight":t={position:new v,direction:new v,color:new Ve,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new v,color:new Ve,distance:0,decay:0};break;case"HemisphereLight":t={direction:new v,skyColor:new Ve,groundColor:new Ve};break;case"RectAreaLight":t={color:new Ve,position:new v,halfWidth:new v,halfHeight:new v};break}return i[e.id]=t,t}}}function Ay(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new re};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new re};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new re,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[e.id]=t,t}}}let Ry=0;function Cy(i,e){return(e.castShadow?2:0)-(i.castShadow?2:0)+(e.map?1:0)-(i.map?1:0)}function Py(i){const e=new Ty,t=Ay(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let l=0;l<9;l++)n.probe.push(new v);const s=new v,r=new ge,o=new ge;function a(l){let h=0,u=0,d=0;for(let b=0;b<9;b++)n.probe[b].set(0,0,0);let f=0,m=0,_=0,g=0,p=0,y=0,M=0,x=0,A=0,E=0,P=0;l.sort(Cy);for(let b=0,w=l.length;b<w;b++){const L=l[b],B=L.color,F=L.intensity,G=L.distance,Z=L.shadow&&L.shadow.map?L.shadow.map.texture:null;if(L.isAmbientLight)h+=B.r*F,u+=B.g*F,d+=B.b*F;else if(L.isLightProbe){for(let X=0;X<9;X++)n.probe[X].addScaledVector(L.sh.coefficients[X],F);P++}else if(L.isDirectionalLight){const X=e.get(L);if(X.color.copy(L.color).multiplyScalar(L.intensity),L.castShadow){const $=L.shadow,W=t.get(L);W.shadowIntensity=$.intensity,W.shadowBias=$.bias,W.shadowNormalBias=$.normalBias,W.shadowRadius=$.radius,W.shadowMapSize=$.mapSize,n.directionalShadow[f]=W,n.directionalShadowMap[f]=Z,n.directionalShadowMatrix[f]=L.shadow.matrix,y++}n.directional[f]=X,f++}else if(L.isSpotLight){const X=e.get(L);X.position.setFromMatrixPosition(L.matrixWorld),X.color.copy(B).multiplyScalar(F),X.distance=G,X.coneCos=Math.cos(L.angle),X.penumbraCos=Math.cos(L.angle*(1-L.penumbra)),X.decay=L.decay,n.spot[_]=X;const $=L.shadow;if(L.map&&(n.spotLightMap[A]=L.map,A++,$.updateMatrices(L),L.castShadow&&E++),n.spotLightMatrix[_]=$.matrix,L.castShadow){const W=t.get(L);W.shadowIntensity=$.intensity,W.shadowBias=$.bias,W.shadowNormalBias=$.normalBias,W.shadowRadius=$.radius,W.shadowMapSize=$.mapSize,n.spotShadow[_]=W,n.spotShadowMap[_]=Z,x++}_++}else if(L.isRectAreaLight){const X=e.get(L);X.color.copy(B).multiplyScalar(F),X.halfWidth.set(L.width*.5,0,0),X.halfHeight.set(0,L.height*.5,0),n.rectArea[g]=X,g++}else if(L.isPointLight){const X=e.get(L);if(X.color.copy(L.color).multiplyScalar(L.intensity),X.distance=L.distance,X.decay=L.decay,L.castShadow){const $=L.shadow,W=t.get(L);W.shadowIntensity=$.intensity,W.shadowBias=$.bias,W.shadowNormalBias=$.normalBias,W.shadowRadius=$.radius,W.shadowMapSize=$.mapSize,W.shadowCameraNear=$.camera.near,W.shadowCameraFar=$.camera.far,n.pointShadow[m]=W,n.pointShadowMap[m]=Z,n.pointShadowMatrix[m]=L.shadow.matrix,M++}n.point[m]=X,m++}else if(L.isHemisphereLight){const X=e.get(L);X.skyColor.copy(L.color).multiplyScalar(F),X.groundColor.copy(L.groundColor).multiplyScalar(F),n.hemi[p]=X,p++}}g>0&&(i.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=ye.LTC_FLOAT_1,n.rectAreaLTC2=ye.LTC_FLOAT_2):(n.rectAreaLTC1=ye.LTC_HALF_1,n.rectAreaLTC2=ye.LTC_HALF_2)),n.ambient[0]=h,n.ambient[1]=u,n.ambient[2]=d;const R=n.hash;(R.directionalLength!==f||R.pointLength!==m||R.spotLength!==_||R.rectAreaLength!==g||R.hemiLength!==p||R.numDirectionalShadows!==y||R.numPointShadows!==M||R.numSpotShadows!==x||R.numSpotMaps!==A||R.numLightProbes!==P)&&(n.directional.length=f,n.spot.length=_,n.rectArea.length=g,n.point.length=m,n.hemi.length=p,n.directionalShadow.length=y,n.directionalShadowMap.length=y,n.pointShadow.length=M,n.pointShadowMap.length=M,n.spotShadow.length=x,n.spotShadowMap.length=x,n.directionalShadowMatrix.length=y,n.pointShadowMatrix.length=M,n.spotLightMatrix.length=x+A-E,n.spotLightMap.length=A,n.numSpotLightShadowsWithMaps=E,n.numLightProbes=P,R.directionalLength=f,R.pointLength=m,R.spotLength=_,R.rectAreaLength=g,R.hemiLength=p,R.numDirectionalShadows=y,R.numPointShadows=M,R.numSpotShadows=x,R.numSpotMaps=A,R.numLightProbes=P,n.version=Ry++)}function c(l,h){let u=0,d=0,f=0,m=0,_=0;const g=h.matrixWorldInverse;for(let p=0,y=l.length;p<y;p++){const M=l[p];if(M.isDirectionalLight){const x=n.directional[u];x.direction.setFromMatrixPosition(M.matrixWorld),s.setFromMatrixPosition(M.target.matrixWorld),x.direction.sub(s),x.direction.transformDirection(g),u++}else if(M.isSpotLight){const x=n.spot[f];x.position.setFromMatrixPosition(M.matrixWorld),x.position.applyMatrix4(g),x.direction.setFromMatrixPosition(M.matrixWorld),s.setFromMatrixPosition(M.target.matrixWorld),x.direction.sub(s),x.direction.transformDirection(g),f++}else if(M.isRectAreaLight){const x=n.rectArea[m];x.position.setFromMatrixPosition(M.matrixWorld),x.position.applyMatrix4(g),o.identity(),r.copy(M.matrixWorld),r.premultiply(g),o.extractRotation(r),x.halfWidth.set(M.width*.5,0,0),x.halfHeight.set(0,M.height*.5,0),x.halfWidth.applyMatrix4(o),x.halfHeight.applyMatrix4(o),m++}else if(M.isPointLight){const x=n.point[d];x.position.setFromMatrixPosition(M.matrixWorld),x.position.applyMatrix4(g),d++}else if(M.isHemisphereLight){const x=n.hemi[_];x.direction.setFromMatrixPosition(M.matrixWorld),x.direction.transformDirection(g),_++}}}return{setup:a,setupView:c,state:n}}function dd(i){const e=new Py(i),t=[],n=[];function s(h){l.camera=h,t.length=0,n.length=0}function r(h){t.push(h)}function o(h){n.push(h)}function a(){e.setup(t)}function c(h){e.setupView(t,h)}const l={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:s,state:l,setupLights:a,setupLightsView:c,pushLight:r,pushShadow:o}}function Ly(i){let e=new WeakMap;function t(s,r=0){const o=e.get(s);let a;return o===void 0?(a=new dd(i),e.set(s,[a])):r>=o.length?(a=new dd(i),o.push(a)):a=o[r],a}function n(){e=new WeakMap}return{get:t,dispose:n}}class Iy extends ui{static get type(){return"MeshDepthMaterial"}constructor(e){super(),this.isMeshDepthMaterial=!0,this.depthPacking=f0,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class Dy extends ui{static get type(){return"MeshDistanceMaterial"}constructor(e){super(),this.isMeshDistanceMaterial=!0,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const Ny=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,Uy=`uniform sampler2D shadow_pass;
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
}`;function Oy(i,e,t){let n=new Ph;const s=new re,r=new re,o=new bt,a=new Iy({depthPacking:p0}),c=new Dy,l={},h=t.maxTextureSize,u={[Ni]:Sn,[Sn]:Ni,[Pn]:Pn},d=new di({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new re},radius:{value:4}},vertexShader:Ny,fragmentShader:Uy}),f=d.clone();f.defines.HORIZONTAL_PASS=1;const m=new Xt;m.setAttribute("position",new on(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const _=new jt(m,d),g=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=xf;let p=this.type;this.render=function(E,P,R){if(g.enabled===!1||g.autoUpdate===!1&&g.needsUpdate===!1||E.length===0)return;const b=i.getRenderTarget(),w=i.getActiveCubeFace(),L=i.getActiveMipmapLevel(),B=i.state;B.setBlending(ns),B.buffers.color.setClear(1,1,1,1),B.buffers.depth.setTest(!0),B.setScissorTest(!1);const F=p!==Ai&&this.type===Ai,G=p===Ai&&this.type!==Ai;for(let Z=0,X=E.length;Z<X;Z++){const $=E[Z],W=$.shadow;if(W===void 0){console.warn("THREE.WebGLShadowMap:",$,"has no shadow.");continue}if(W.autoUpdate===!1&&W.needsUpdate===!1)continue;s.copy(W.mapSize);const ce=W.getFrameExtents();if(s.multiply(ce),r.copy(W.mapSize),(s.x>h||s.y>h)&&(s.x>h&&(r.x=Math.floor(h/ce.x),s.x=r.x*ce.x,W.mapSize.x=r.x),s.y>h&&(r.y=Math.floor(h/ce.y),s.y=r.y*ce.y,W.mapSize.y=r.y)),W.map===null||F===!0||G===!0){const Re=this.type!==Ai?{minFilter:xn,magFilter:xn}:{};W.map!==null&&W.map.dispose(),W.map=new As(s.x,s.y,Re),W.map.texture.name=$.name+".shadowMap",W.camera.updateProjectionMatrix()}i.setRenderTarget(W.map),i.clear();const ve=W.getViewportCount();for(let Re=0;Re<ve;Re++){const it=W.getViewport(Re);o.set(r.x*it.x,r.y*it.y,r.x*it.z,r.y*it.w),B.viewport(o),W.updateMatrices($,Re),n=W.getFrustum(),x(P,R,W.camera,$,this.type)}W.isPointLightShadow!==!0&&this.type===Ai&&y(W,R),W.needsUpdate=!1}p=this.type,g.needsUpdate=!1,i.setRenderTarget(b,w,L)};function y(E,P){const R=e.update(_);d.defines.VSM_SAMPLES!==E.blurSamples&&(d.defines.VSM_SAMPLES=E.blurSamples,f.defines.VSM_SAMPLES=E.blurSamples,d.needsUpdate=!0,f.needsUpdate=!0),E.mapPass===null&&(E.mapPass=new As(s.x,s.y)),d.uniforms.shadow_pass.value=E.map.texture,d.uniforms.resolution.value=E.mapSize,d.uniforms.radius.value=E.radius,i.setRenderTarget(E.mapPass),i.clear(),i.renderBufferDirect(P,null,R,d,_,null),f.uniforms.shadow_pass.value=E.mapPass.texture,f.uniforms.resolution.value=E.mapSize,f.uniforms.radius.value=E.radius,i.setRenderTarget(E.map),i.clear(),i.renderBufferDirect(P,null,R,f,_,null)}function M(E,P,R,b){let w=null;const L=R.isPointLight===!0?E.customDistanceMaterial:E.customDepthMaterial;if(L!==void 0)w=L;else if(w=R.isPointLight===!0?c:a,i.localClippingEnabled&&P.clipShadows===!0&&Array.isArray(P.clippingPlanes)&&P.clippingPlanes.length!==0||P.displacementMap&&P.displacementScale!==0||P.alphaMap&&P.alphaTest>0||P.map&&P.alphaTest>0){const B=w.uuid,F=P.uuid;let G=l[B];G===void 0&&(G={},l[B]=G);let Z=G[F];Z===void 0&&(Z=w.clone(),G[F]=Z,P.addEventListener("dispose",A)),w=Z}if(w.visible=P.visible,w.wireframe=P.wireframe,b===Ai?w.side=P.shadowSide!==null?P.shadowSide:P.side:w.side=P.shadowSide!==null?P.shadowSide:u[P.side],w.alphaMap=P.alphaMap,w.alphaTest=P.alphaTest,w.map=P.map,w.clipShadows=P.clipShadows,w.clippingPlanes=P.clippingPlanes,w.clipIntersection=P.clipIntersection,w.displacementMap=P.displacementMap,w.displacementScale=P.displacementScale,w.displacementBias=P.displacementBias,w.wireframeLinewidth=P.wireframeLinewidth,w.linewidth=P.linewidth,R.isPointLight===!0&&w.isMeshDistanceMaterial===!0){const B=i.properties.get(w);B.light=R}return w}function x(E,P,R,b,w){if(E.visible===!1)return;if(E.layers.test(P.layers)&&(E.isMesh||E.isLine||E.isPoints)&&(E.castShadow||E.receiveShadow&&w===Ai)&&(!E.frustumCulled||n.intersectsObject(E))){E.modelViewMatrix.multiplyMatrices(R.matrixWorldInverse,E.matrixWorld);const F=e.update(E),G=E.material;if(Array.isArray(G)){const Z=F.groups;for(let X=0,$=Z.length;X<$;X++){const W=Z[X],ce=G[W.materialIndex];if(ce&&ce.visible){const ve=M(E,ce,b,w);E.onBeforeShadow(i,E,P,R,F,ve,W),i.renderBufferDirect(R,null,F,ve,E,W),E.onAfterShadow(i,E,P,R,F,ve,W)}}}else if(G.visible){const Z=M(E,G,b,w);E.onBeforeShadow(i,E,P,R,F,Z,null),i.renderBufferDirect(R,null,F,Z,E,null),E.onAfterShadow(i,E,P,R,F,Z,null)}}const B=E.children;for(let F=0,G=B.length;F<G;F++)x(B[F],P,R,b,w)}function A(E){E.target.removeEventListener("dispose",A);for(const R in l){const b=l[R],w=E.target.uuid;w in b&&(b[w].dispose(),delete b[w])}}}const Fy={[Ml]:wl,[bl]:Tl,[Sl]:Al,[ur]:El,[wl]:Ml,[Tl]:bl,[Al]:Sl,[El]:ur};function By(i,e){function t(){let D=!1;const we=new bt;let q=null;const J=new bt(0,0,0,0);return{setMask:function(Ee){q!==Ee&&!D&&(i.colorMask(Ee,Ee,Ee,Ee),q=Ee)},setLocked:function(Ee){D=Ee},setClear:function(Ee,be,st,qt,un){un===!0&&(Ee*=qt,be*=qt,st*=qt),we.set(Ee,be,st,qt),J.equals(we)===!1&&(i.clearColor(Ee,be,st,qt),J.copy(we))},reset:function(){D=!1,q=null,J.set(-1,0,0,0)}}}function n(){let D=!1,we=!1,q=null,J=null,Ee=null;return{setReversed:function(be){if(we!==be){const st=e.get("EXT_clip_control");we?st.clipControlEXT(st.LOWER_LEFT_EXT,st.ZERO_TO_ONE_EXT):st.clipControlEXT(st.LOWER_LEFT_EXT,st.NEGATIVE_ONE_TO_ONE_EXT);const qt=Ee;Ee=null,this.setClear(qt)}we=be},getReversed:function(){return we},setTest:function(be){be?me(i.DEPTH_TEST):We(i.DEPTH_TEST)},setMask:function(be){q!==be&&!D&&(i.depthMask(be),q=be)},setFunc:function(be){if(we&&(be=Fy[be]),J!==be){switch(be){case Ml:i.depthFunc(i.NEVER);break;case wl:i.depthFunc(i.ALWAYS);break;case bl:i.depthFunc(i.LESS);break;case ur:i.depthFunc(i.LEQUAL);break;case Sl:i.depthFunc(i.EQUAL);break;case El:i.depthFunc(i.GEQUAL);break;case Tl:i.depthFunc(i.GREATER);break;case Al:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}J=be}},setLocked:function(be){D=be},setClear:function(be){Ee!==be&&(we&&(be=1-be),i.clearDepth(be),Ee=be)},reset:function(){D=!1,q=null,J=null,Ee=null,we=!1}}}function s(){let D=!1,we=null,q=null,J=null,Ee=null,be=null,st=null,qt=null,un=null;return{setTest:function(Rt){D||(Rt?me(i.STENCIL_TEST):We(i.STENCIL_TEST))},setMask:function(Rt){we!==Rt&&!D&&(i.stencilMask(Rt),we=Rt)},setFunc:function(Rt,Jn,xi){(q!==Rt||J!==Jn||Ee!==xi)&&(i.stencilFunc(Rt,Jn,xi),q=Rt,J=Jn,Ee=xi)},setOp:function(Rt,Jn,xi){(be!==Rt||st!==Jn||qt!==xi)&&(i.stencilOp(Rt,Jn,xi),be=Rt,st=Jn,qt=xi)},setLocked:function(Rt){D=Rt},setClear:function(Rt){un!==Rt&&(i.clearStencil(Rt),un=Rt)},reset:function(){D=!1,we=null,q=null,J=null,Ee=null,be=null,st=null,qt=null,un=null}}}const r=new t,o=new n,a=new s,c=new WeakMap,l=new WeakMap;let h={},u={},d=new WeakMap,f=[],m=null,_=!1,g=null,p=null,y=null,M=null,x=null,A=null,E=null,P=new Ve(0,0,0),R=0,b=!1,w=null,L=null,B=null,F=null,G=null;const Z=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let X=!1,$=0;const W=i.getParameter(i.VERSION);W.indexOf("WebGL")!==-1?($=parseFloat(/^WebGL (\d)/.exec(W)[1]),X=$>=1):W.indexOf("OpenGL ES")!==-1&&($=parseFloat(/^OpenGL ES (\d)/.exec(W)[1]),X=$>=2);let ce=null,ve={};const Re=i.getParameter(i.SCISSOR_BOX),it=i.getParameter(i.VIEWPORT),St=new bt().fromArray(Re),K=new bt().fromArray(it);function ue(D,we,q,J){const Ee=new Uint8Array(4),be=i.createTexture();i.bindTexture(D,be),i.texParameteri(D,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(D,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let st=0;st<q;st++)D===i.TEXTURE_3D||D===i.TEXTURE_2D_ARRAY?i.texImage3D(we,0,i.RGBA,1,1,J,0,i.RGBA,i.UNSIGNED_BYTE,Ee):i.texImage2D(we+st,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,Ee);return be}const Ne={};Ne[i.TEXTURE_2D]=ue(i.TEXTURE_2D,i.TEXTURE_2D,1),Ne[i.TEXTURE_CUBE_MAP]=ue(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),Ne[i.TEXTURE_2D_ARRAY]=ue(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),Ne[i.TEXTURE_3D]=ue(i.TEXTURE_3D,i.TEXTURE_3D,1,1),r.setClear(0,0,0,1),o.setClear(1),a.setClear(0),me(i.DEPTH_TEST),o.setFunc(ur),ae(!1),Le(du),me(i.CULL_FACE),I(ns);function me(D){h[D]!==!0&&(i.enable(D),h[D]=!0)}function We(D){h[D]!==!1&&(i.disable(D),h[D]=!1)}function Qe(D,we){return u[D]!==we?(i.bindFramebuffer(D,we),u[D]=we,D===i.DRAW_FRAMEBUFFER&&(u[i.FRAMEBUFFER]=we),D===i.FRAMEBUFFER&&(u[i.DRAW_FRAMEBUFFER]=we),!0):!1}function je(D,we){let q=f,J=!1;if(D){q=d.get(we),q===void 0&&(q=[],d.set(we,q));const Ee=D.textures;if(q.length!==Ee.length||q[0]!==i.COLOR_ATTACHMENT0){for(let be=0,st=Ee.length;be<st;be++)q[be]=i.COLOR_ATTACHMENT0+be;q.length=Ee.length,J=!0}}else q[0]!==i.BACK&&(q[0]=i.BACK,J=!0);J&&i.drawBuffers(q)}function _t(D){return m!==D?(i.useProgram(D),m=D,!0):!1}const ee={[ws]:i.FUNC_ADD,[Bm]:i.FUNC_SUBTRACT,[km]:i.FUNC_REVERSE_SUBTRACT};ee[zm]=i.MIN,ee[Hm]=i.MAX;const he={[Gm]:i.ZERO,[Vm]:i.ONE,[Wm]:i.SRC_COLOR,[vl]:i.SRC_ALPHA,[Km]:i.SRC_ALPHA_SATURATE,[jm]:i.DST_COLOR,[qm]:i.DST_ALPHA,[Xm]:i.ONE_MINUS_SRC_COLOR,[yl]:i.ONE_MINUS_SRC_ALPHA,[Ym]:i.ONE_MINUS_DST_COLOR,[$m]:i.ONE_MINUS_DST_ALPHA,[Zm]:i.CONSTANT_COLOR,[Jm]:i.ONE_MINUS_CONSTANT_COLOR,[Qm]:i.CONSTANT_ALPHA,[e0]:i.ONE_MINUS_CONSTANT_ALPHA};function I(D,we,q,J,Ee,be,st,qt,un,Rt){if(D===ns){_===!0&&(We(i.BLEND),_=!1);return}if(_===!1&&(me(i.BLEND),_=!0),D!==Fm){if(D!==g||Rt!==b){if((p!==ws||x!==ws)&&(i.blendEquation(i.FUNC_ADD),p=ws,x=ws),Rt)switch(D){case rr:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case fu:i.blendFunc(i.ONE,i.ONE);break;case pu:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case mu:i.blendFuncSeparate(i.ZERO,i.SRC_COLOR,i.ZERO,i.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",D);break}else switch(D){case rr:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case fu:i.blendFunc(i.SRC_ALPHA,i.ONE);break;case pu:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case mu:i.blendFunc(i.ZERO,i.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",D);break}y=null,M=null,A=null,E=null,P.set(0,0,0),R=0,g=D,b=Rt}return}Ee=Ee||we,be=be||q,st=st||J,(we!==p||Ee!==x)&&(i.blendEquationSeparate(ee[we],ee[Ee]),p=we,x=Ee),(q!==y||J!==M||be!==A||st!==E)&&(i.blendFuncSeparate(he[q],he[J],he[be],he[st]),y=q,M=J,A=be,E=st),(qt.equals(P)===!1||un!==R)&&(i.blendColor(qt.r,qt.g,qt.b,un),P.copy(qt),R=un),g=D,b=!1}function ze(D,we){D.side===Pn?We(i.CULL_FACE):me(i.CULL_FACE);let q=D.side===Sn;we&&(q=!q),ae(q),D.blending===rr&&D.transparent===!1?I(ns):I(D.blending,D.blendEquation,D.blendSrc,D.blendDst,D.blendEquationAlpha,D.blendSrcAlpha,D.blendDstAlpha,D.blendColor,D.blendAlpha,D.premultipliedAlpha),o.setFunc(D.depthFunc),o.setTest(D.depthTest),o.setMask(D.depthWrite),r.setMask(D.colorWrite);const J=D.stencilWrite;a.setTest(J),J&&(a.setMask(D.stencilWriteMask),a.setFunc(D.stencilFunc,D.stencilRef,D.stencilFuncMask),a.setOp(D.stencilFail,D.stencilZFail,D.stencilZPass)),qe(D.polygonOffset,D.polygonOffsetFactor,D.polygonOffsetUnits),D.alphaToCoverage===!0?me(i.SAMPLE_ALPHA_TO_COVERAGE):We(i.SAMPLE_ALPHA_TO_COVERAGE)}function ae(D){w!==D&&(D?i.frontFace(i.CW):i.frontFace(i.CCW),w=D)}function Le(D){D!==Nm?(me(i.CULL_FACE),D!==L&&(D===du?i.cullFace(i.BACK):D===Um?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):We(i.CULL_FACE),L=D}function _e(D){D!==B&&(X&&i.lineWidth(D),B=D)}function qe(D,we,q){D?(me(i.POLYGON_OFFSET_FILL),(F!==we||G!==q)&&(i.polygonOffset(we,q),F=we,G=q)):We(i.POLYGON_OFFSET_FILL)}function Ce(D){D?me(i.SCISSOR_TEST):We(i.SCISSOR_TEST)}function C(D){D===void 0&&(D=i.TEXTURE0+Z-1),ce!==D&&(i.activeTexture(D),ce=D)}function S(D,we,q){q===void 0&&(ce===null?q=i.TEXTURE0+Z-1:q=ce);let J=ve[q];J===void 0&&(J={type:void 0,texture:void 0},ve[q]=J),(J.type!==D||J.texture!==we)&&(ce!==q&&(i.activeTexture(q),ce=q),i.bindTexture(D,we||Ne[D]),J.type=D,J.texture=we)}function k(){const D=ve[ce];D!==void 0&&D.type!==void 0&&(i.bindTexture(D.type,null),D.type=void 0,D.texture=void 0)}function j(){try{i.compressedTexImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function te(){try{i.compressedTexImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Y(){try{i.texSubImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Oe(){try{i.texSubImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Me(){try{i.compressedTexSubImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Pe(){try{i.compressedTexSubImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function ft(){try{i.texStorage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function le(){try{i.texStorage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Ie(){try{i.texImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function $e(){try{i.texImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Je(D){St.equals(D)===!1&&(i.scissor(D.x,D.y,D.z,D.w),St.copy(D))}function De(D){K.equals(D)===!1&&(i.viewport(D.x,D.y,D.z,D.w),K.copy(D))}function mt(D,we){let q=l.get(we);q===void 0&&(q=new WeakMap,l.set(we,q));let J=q.get(D);J===void 0&&(J=i.getUniformBlockIndex(we,D.name),q.set(D,J))}function ct(D,we){const J=l.get(we).get(D);c.get(we)!==J&&(i.uniformBlockBinding(we,J,D.__bindingPointIndex),c.set(we,J))}function Ot(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),o.setReversed(!1),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),h={},ce=null,ve={},u={},d=new WeakMap,f=[],m=null,_=!1,g=null,p=null,y=null,M=null,x=null,A=null,E=null,P=new Ve(0,0,0),R=0,b=!1,w=null,L=null,B=null,F=null,G=null,St.set(0,0,i.canvas.width,i.canvas.height),K.set(0,0,i.canvas.width,i.canvas.height),r.reset(),o.reset(),a.reset()}return{buffers:{color:r,depth:o,stencil:a},enable:me,disable:We,bindFramebuffer:Qe,drawBuffers:je,useProgram:_t,setBlending:I,setMaterial:ze,setFlipSided:ae,setCullFace:Le,setLineWidth:_e,setPolygonOffset:qe,setScissorTest:Ce,activeTexture:C,bindTexture:S,unbindTexture:k,compressedTexImage2D:j,compressedTexImage3D:te,texImage2D:Ie,texImage3D:$e,updateUBOMapping:mt,uniformBlockBinding:ct,texStorage2D:ft,texStorage3D:le,texSubImage2D:Y,texSubImage3D:Oe,compressedTexSubImage2D:Me,compressedTexSubImage3D:Pe,scissor:Je,viewport:De,reset:Ot}}function fd(i,e,t,n){const s=ky(n);switch(t){case Ef:return i*e;case Af:return i*e;case Rf:return i*e*2;case Sh:return i*e/s.components*s.byteLength;case Eh:return i*e/s.components*s.byteLength;case Cf:return i*e*2/s.components*s.byteLength;case Th:return i*e*2/s.components*s.byteLength;case Tf:return i*e*3/s.components*s.byteLength;case Xn:return i*e*4/s.components*s.byteLength;case Ah:return i*e*4/s.components*s.byteLength;case va:case ya:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case Ma:case wa:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Ll:case Dl:return Math.max(i,16)*Math.max(e,8)/4;case Pl:case Il:return Math.max(i,8)*Math.max(e,8)/2;case Nl:case Ul:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case Ol:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Fl:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Bl:return Math.floor((i+4)/5)*Math.floor((e+3)/4)*16;case kl:return Math.floor((i+4)/5)*Math.floor((e+4)/5)*16;case zl:return Math.floor((i+5)/6)*Math.floor((e+4)/5)*16;case Hl:return Math.floor((i+5)/6)*Math.floor((e+5)/6)*16;case Gl:return Math.floor((i+7)/8)*Math.floor((e+4)/5)*16;case Vl:return Math.floor((i+7)/8)*Math.floor((e+5)/6)*16;case Wl:return Math.floor((i+7)/8)*Math.floor((e+7)/8)*16;case Xl:return Math.floor((i+9)/10)*Math.floor((e+4)/5)*16;case ql:return Math.floor((i+9)/10)*Math.floor((e+5)/6)*16;case $l:return Math.floor((i+9)/10)*Math.floor((e+7)/8)*16;case jl:return Math.floor((i+9)/10)*Math.floor((e+9)/10)*16;case Yl:return Math.floor((i+11)/12)*Math.floor((e+9)/10)*16;case Kl:return Math.floor((i+11)/12)*Math.floor((e+11)/12)*16;case ba:case Zl:case Jl:return Math.ceil(i/4)*Math.ceil(e/4)*16;case Pf:case Ql:return Math.ceil(i/4)*Math.ceil(e/4)*8;case eh:case th:return Math.ceil(i/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function ky(i){switch(i){case Ui:case wf:return{byteLength:1,components:1};case ho:case bf:case Mo:return{byteLength:2,components:1};case wh:case bh:return{byteLength:2,components:4};case Ts:case Mh:case ri:return{byteLength:4,components:1};case Sf:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}function zy(i,e,t,n,s,r,o){const a=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,c=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),l=new re,h=new WeakMap;let u;const d=new WeakMap;let f=!1;try{f=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function m(C,S){return f?new OffscreenCanvas(C,S):po("canvas")}function _(C,S,k){let j=1;const te=Ce(C);if((te.width>k||te.height>k)&&(j=k/Math.max(te.width,te.height)),j<1)if(typeof HTMLImageElement<"u"&&C instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&C instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&C instanceof ImageBitmap||typeof VideoFrame<"u"&&C instanceof VideoFrame){const Y=Math.floor(j*te.width),Oe=Math.floor(j*te.height);u===void 0&&(u=m(Y,Oe));const Me=S?m(Y,Oe):u;return Me.width=Y,Me.height=Oe,Me.getContext("2d").drawImage(C,0,0,Y,Oe),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+te.width+"x"+te.height+") to ("+Y+"x"+Oe+")."),Me}else return"data"in C&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+te.width+"x"+te.height+")."),C;return C}function g(C){return C.generateMipmaps}function p(C){i.generateMipmap(C)}function y(C){return C.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:C.isWebGL3DRenderTarget?i.TEXTURE_3D:C.isWebGLArrayRenderTarget||C.isCompressedArrayTexture?i.TEXTURE_2D_ARRAY:i.TEXTURE_2D}function M(C,S,k,j,te=!1){if(C!==null){if(i[C]!==void 0)return i[C];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+C+"'")}let Y=S;if(S===i.RED&&(k===i.FLOAT&&(Y=i.R32F),k===i.HALF_FLOAT&&(Y=i.R16F),k===i.UNSIGNED_BYTE&&(Y=i.R8)),S===i.RED_INTEGER&&(k===i.UNSIGNED_BYTE&&(Y=i.R8UI),k===i.UNSIGNED_SHORT&&(Y=i.R16UI),k===i.UNSIGNED_INT&&(Y=i.R32UI),k===i.BYTE&&(Y=i.R8I),k===i.SHORT&&(Y=i.R16I),k===i.INT&&(Y=i.R32I)),S===i.RG&&(k===i.FLOAT&&(Y=i.RG32F),k===i.HALF_FLOAT&&(Y=i.RG16F),k===i.UNSIGNED_BYTE&&(Y=i.RG8)),S===i.RG_INTEGER&&(k===i.UNSIGNED_BYTE&&(Y=i.RG8UI),k===i.UNSIGNED_SHORT&&(Y=i.RG16UI),k===i.UNSIGNED_INT&&(Y=i.RG32UI),k===i.BYTE&&(Y=i.RG8I),k===i.SHORT&&(Y=i.RG16I),k===i.INT&&(Y=i.RG32I)),S===i.RGB_INTEGER&&(k===i.UNSIGNED_BYTE&&(Y=i.RGB8UI),k===i.UNSIGNED_SHORT&&(Y=i.RGB16UI),k===i.UNSIGNED_INT&&(Y=i.RGB32UI),k===i.BYTE&&(Y=i.RGB8I),k===i.SHORT&&(Y=i.RGB16I),k===i.INT&&(Y=i.RGB32I)),S===i.RGBA_INTEGER&&(k===i.UNSIGNED_BYTE&&(Y=i.RGBA8UI),k===i.UNSIGNED_SHORT&&(Y=i.RGBA16UI),k===i.UNSIGNED_INT&&(Y=i.RGBA32UI),k===i.BYTE&&(Y=i.RGBA8I),k===i.SHORT&&(Y=i.RGBA16I),k===i.INT&&(Y=i.RGBA32I)),S===i.RGB&&k===i.UNSIGNED_INT_5_9_9_9_REV&&(Y=i.RGB9_E5),S===i.RGBA){const Oe=te?Wa:pt.getTransfer(j);k===i.FLOAT&&(Y=i.RGBA32F),k===i.HALF_FLOAT&&(Y=i.RGBA16F),k===i.UNSIGNED_BYTE&&(Y=Oe===Nt?i.SRGB8_ALPHA8:i.RGBA8),k===i.UNSIGNED_SHORT_4_4_4_4&&(Y=i.RGBA4),k===i.UNSIGNED_SHORT_5_5_5_1&&(Y=i.RGB5_A1)}return(Y===i.R16F||Y===i.R32F||Y===i.RG16F||Y===i.RG32F||Y===i.RGBA16F||Y===i.RGBA32F)&&e.get("EXT_color_buffer_float"),Y}function x(C,S){let k;return C?S===null||S===Ts||S===mr?k=i.DEPTH24_STENCIL8:S===ri?k=i.DEPTH32F_STENCIL8:S===ho&&(k=i.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):S===null||S===Ts||S===mr?k=i.DEPTH_COMPONENT24:S===ri?k=i.DEPTH_COMPONENT32F:S===ho&&(k=i.DEPTH_COMPONENT16),k}function A(C,S){return g(C)===!0||C.isFramebufferTexture&&C.minFilter!==xn&&C.minFilter!==Un?Math.log2(Math.max(S.width,S.height))+1:C.mipmaps!==void 0&&C.mipmaps.length>0?C.mipmaps.length:C.isCompressedTexture&&Array.isArray(C.image)?S.mipmaps.length:1}function E(C){const S=C.target;S.removeEventListener("dispose",E),R(S),S.isVideoTexture&&h.delete(S)}function P(C){const S=C.target;S.removeEventListener("dispose",P),w(S)}function R(C){const S=n.get(C);if(S.__webglInit===void 0)return;const k=C.source,j=d.get(k);if(j){const te=j[S.__cacheKey];te.usedTimes--,te.usedTimes===0&&b(C),Object.keys(j).length===0&&d.delete(k)}n.remove(C)}function b(C){const S=n.get(C);i.deleteTexture(S.__webglTexture);const k=C.source,j=d.get(k);delete j[S.__cacheKey],o.memory.textures--}function w(C){const S=n.get(C);if(C.depthTexture&&(C.depthTexture.dispose(),n.remove(C.depthTexture)),C.isWebGLCubeRenderTarget)for(let j=0;j<6;j++){if(Array.isArray(S.__webglFramebuffer[j]))for(let te=0;te<S.__webglFramebuffer[j].length;te++)i.deleteFramebuffer(S.__webglFramebuffer[j][te]);else i.deleteFramebuffer(S.__webglFramebuffer[j]);S.__webglDepthbuffer&&i.deleteRenderbuffer(S.__webglDepthbuffer[j])}else{if(Array.isArray(S.__webglFramebuffer))for(let j=0;j<S.__webglFramebuffer.length;j++)i.deleteFramebuffer(S.__webglFramebuffer[j]);else i.deleteFramebuffer(S.__webglFramebuffer);if(S.__webglDepthbuffer&&i.deleteRenderbuffer(S.__webglDepthbuffer),S.__webglMultisampledFramebuffer&&i.deleteFramebuffer(S.__webglMultisampledFramebuffer),S.__webglColorRenderbuffer)for(let j=0;j<S.__webglColorRenderbuffer.length;j++)S.__webglColorRenderbuffer[j]&&i.deleteRenderbuffer(S.__webglColorRenderbuffer[j]);S.__webglDepthRenderbuffer&&i.deleteRenderbuffer(S.__webglDepthRenderbuffer)}const k=C.textures;for(let j=0,te=k.length;j<te;j++){const Y=n.get(k[j]);Y.__webglTexture&&(i.deleteTexture(Y.__webglTexture),o.memory.textures--),n.remove(k[j])}n.remove(C)}let L=0;function B(){L=0}function F(){const C=L;return C>=s.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+C+" texture units while this GPU supports only "+s.maxTextures),L+=1,C}function G(C){const S=[];return S.push(C.wrapS),S.push(C.wrapT),S.push(C.wrapR||0),S.push(C.magFilter),S.push(C.minFilter),S.push(C.anisotropy),S.push(C.internalFormat),S.push(C.format),S.push(C.type),S.push(C.generateMipmaps),S.push(C.premultiplyAlpha),S.push(C.flipY),S.push(C.unpackAlignment),S.push(C.colorSpace),S.join()}function Z(C,S){const k=n.get(C);if(C.isVideoTexture&&_e(C),C.isRenderTargetTexture===!1&&C.version>0&&k.__version!==C.version){const j=C.image;if(j===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(j.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{K(k,C,S);return}}t.bindTexture(i.TEXTURE_2D,k.__webglTexture,i.TEXTURE0+S)}function X(C,S){const k=n.get(C);if(C.version>0&&k.__version!==C.version){K(k,C,S);return}t.bindTexture(i.TEXTURE_2D_ARRAY,k.__webglTexture,i.TEXTURE0+S)}function $(C,S){const k=n.get(C);if(C.version>0&&k.__version!==C.version){K(k,C,S);return}t.bindTexture(i.TEXTURE_3D,k.__webglTexture,i.TEXTURE0+S)}function W(C,S){const k=n.get(C);if(C.version>0&&k.__version!==C.version){ue(k,C,S);return}t.bindTexture(i.TEXTURE_CUBE_MAP,k.__webglTexture,i.TEXTURE0+S)}const ce={[pr]:i.REPEAT,[Zi]:i.CLAMP_TO_EDGE,[Ca]:i.MIRRORED_REPEAT},ve={[xn]:i.NEAREST,[Mf]:i.NEAREST_MIPMAP_NEAREST,[Qr]:i.NEAREST_MIPMAP_LINEAR,[Un]:i.LINEAR,[xa]:i.LINEAR_MIPMAP_NEAREST,[Li]:i.LINEAR_MIPMAP_LINEAR},Re={[g0]:i.NEVER,[w0]:i.ALWAYS,[_0]:i.LESS,[Df]:i.LEQUAL,[x0]:i.EQUAL,[M0]:i.GEQUAL,[v0]:i.GREATER,[y0]:i.NOTEQUAL};function it(C,S){if(S.type===ri&&e.has("OES_texture_float_linear")===!1&&(S.magFilter===Un||S.magFilter===xa||S.magFilter===Qr||S.magFilter===Li||S.minFilter===Un||S.minFilter===xa||S.minFilter===Qr||S.minFilter===Li)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(C,i.TEXTURE_WRAP_S,ce[S.wrapS]),i.texParameteri(C,i.TEXTURE_WRAP_T,ce[S.wrapT]),(C===i.TEXTURE_3D||C===i.TEXTURE_2D_ARRAY)&&i.texParameteri(C,i.TEXTURE_WRAP_R,ce[S.wrapR]),i.texParameteri(C,i.TEXTURE_MAG_FILTER,ve[S.magFilter]),i.texParameteri(C,i.TEXTURE_MIN_FILTER,ve[S.minFilter]),S.compareFunction&&(i.texParameteri(C,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(C,i.TEXTURE_COMPARE_FUNC,Re[S.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(S.magFilter===xn||S.minFilter!==Qr&&S.minFilter!==Li||S.type===ri&&e.has("OES_texture_float_linear")===!1)return;if(S.anisotropy>1||n.get(S).__currentAnisotropy){const k=e.get("EXT_texture_filter_anisotropic");i.texParameterf(C,k.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(S.anisotropy,s.getMaxAnisotropy())),n.get(S).__currentAnisotropy=S.anisotropy}}}function St(C,S){let k=!1;C.__webglInit===void 0&&(C.__webglInit=!0,S.addEventListener("dispose",E));const j=S.source;let te=d.get(j);te===void 0&&(te={},d.set(j,te));const Y=G(S);if(Y!==C.__cacheKey){te[Y]===void 0&&(te[Y]={texture:i.createTexture(),usedTimes:0},o.memory.textures++,k=!0),te[Y].usedTimes++;const Oe=te[C.__cacheKey];Oe!==void 0&&(te[C.__cacheKey].usedTimes--,Oe.usedTimes===0&&b(S)),C.__cacheKey=Y,C.__webglTexture=te[Y].texture}return k}function K(C,S,k){let j=i.TEXTURE_2D;(S.isDataArrayTexture||S.isCompressedArrayTexture)&&(j=i.TEXTURE_2D_ARRAY),S.isData3DTexture&&(j=i.TEXTURE_3D);const te=St(C,S),Y=S.source;t.bindTexture(j,C.__webglTexture,i.TEXTURE0+k);const Oe=n.get(Y);if(Y.version!==Oe.__version||te===!0){t.activeTexture(i.TEXTURE0+k);const Me=pt.getPrimaries(pt.workingColorSpace),Pe=S.colorSpace===Yi?null:pt.getPrimaries(S.colorSpace),ft=S.colorSpace===Yi||Me===Pe?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,S.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,S.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,S.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,ft);let le=_(S.image,!1,s.maxTextureSize);le=qe(S,le);const Ie=r.convert(S.format,S.colorSpace),$e=r.convert(S.type);let Je=M(S.internalFormat,Ie,$e,S.colorSpace,S.isVideoTexture);it(j,S);let De;const mt=S.mipmaps,ct=S.isVideoTexture!==!0,Ot=Oe.__version===void 0||te===!0,D=Y.dataReady,we=A(S,le);if(S.isDepthTexture)Je=x(S.format===gr,S.type),Ot&&(ct?t.texStorage2D(i.TEXTURE_2D,1,Je,le.width,le.height):t.texImage2D(i.TEXTURE_2D,0,Je,le.width,le.height,0,Ie,$e,null));else if(S.isDataTexture)if(mt.length>0){ct&&Ot&&t.texStorage2D(i.TEXTURE_2D,we,Je,mt[0].width,mt[0].height);for(let q=0,J=mt.length;q<J;q++)De=mt[q],ct?D&&t.texSubImage2D(i.TEXTURE_2D,q,0,0,De.width,De.height,Ie,$e,De.data):t.texImage2D(i.TEXTURE_2D,q,Je,De.width,De.height,0,Ie,$e,De.data);S.generateMipmaps=!1}else ct?(Ot&&t.texStorage2D(i.TEXTURE_2D,we,Je,le.width,le.height),D&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,le.width,le.height,Ie,$e,le.data)):t.texImage2D(i.TEXTURE_2D,0,Je,le.width,le.height,0,Ie,$e,le.data);else if(S.isCompressedTexture)if(S.isCompressedArrayTexture){ct&&Ot&&t.texStorage3D(i.TEXTURE_2D_ARRAY,we,Je,mt[0].width,mt[0].height,le.depth);for(let q=0,J=mt.length;q<J;q++)if(De=mt[q],S.format!==Xn)if(Ie!==null)if(ct){if(D)if(S.layerUpdates.size>0){const Ee=fd(De.width,De.height,S.format,S.type);for(const be of S.layerUpdates){const st=De.data.subarray(be*Ee/De.data.BYTES_PER_ELEMENT,(be+1)*Ee/De.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,q,0,0,be,De.width,De.height,1,Ie,st)}S.clearLayerUpdates()}else t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,q,0,0,0,De.width,De.height,le.depth,Ie,De.data)}else t.compressedTexImage3D(i.TEXTURE_2D_ARRAY,q,Je,De.width,De.height,le.depth,0,De.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else ct?D&&t.texSubImage3D(i.TEXTURE_2D_ARRAY,q,0,0,0,De.width,De.height,le.depth,Ie,$e,De.data):t.texImage3D(i.TEXTURE_2D_ARRAY,q,Je,De.width,De.height,le.depth,0,Ie,$e,De.data)}else{ct&&Ot&&t.texStorage2D(i.TEXTURE_2D,we,Je,mt[0].width,mt[0].height);for(let q=0,J=mt.length;q<J;q++)De=mt[q],S.format!==Xn?Ie!==null?ct?D&&t.compressedTexSubImage2D(i.TEXTURE_2D,q,0,0,De.width,De.height,Ie,De.data):t.compressedTexImage2D(i.TEXTURE_2D,q,Je,De.width,De.height,0,De.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):ct?D&&t.texSubImage2D(i.TEXTURE_2D,q,0,0,De.width,De.height,Ie,$e,De.data):t.texImage2D(i.TEXTURE_2D,q,Je,De.width,De.height,0,Ie,$e,De.data)}else if(S.isDataArrayTexture)if(ct){if(Ot&&t.texStorage3D(i.TEXTURE_2D_ARRAY,we,Je,le.width,le.height,le.depth),D)if(S.layerUpdates.size>0){const q=fd(le.width,le.height,S.format,S.type);for(const J of S.layerUpdates){const Ee=le.data.subarray(J*q/le.data.BYTES_PER_ELEMENT,(J+1)*q/le.data.BYTES_PER_ELEMENT);t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,J,le.width,le.height,1,Ie,$e,Ee)}S.clearLayerUpdates()}else t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,le.width,le.height,le.depth,Ie,$e,le.data)}else t.texImage3D(i.TEXTURE_2D_ARRAY,0,Je,le.width,le.height,le.depth,0,Ie,$e,le.data);else if(S.isData3DTexture)ct?(Ot&&t.texStorage3D(i.TEXTURE_3D,we,Je,le.width,le.height,le.depth),D&&t.texSubImage3D(i.TEXTURE_3D,0,0,0,0,le.width,le.height,le.depth,Ie,$e,le.data)):t.texImage3D(i.TEXTURE_3D,0,Je,le.width,le.height,le.depth,0,Ie,$e,le.data);else if(S.isFramebufferTexture){if(Ot)if(ct)t.texStorage2D(i.TEXTURE_2D,we,Je,le.width,le.height);else{let q=le.width,J=le.height;for(let Ee=0;Ee<we;Ee++)t.texImage2D(i.TEXTURE_2D,Ee,Je,q,J,0,Ie,$e,null),q>>=1,J>>=1}}else if(mt.length>0){if(ct&&Ot){const q=Ce(mt[0]);t.texStorage2D(i.TEXTURE_2D,we,Je,q.width,q.height)}for(let q=0,J=mt.length;q<J;q++)De=mt[q],ct?D&&t.texSubImage2D(i.TEXTURE_2D,q,0,0,Ie,$e,De):t.texImage2D(i.TEXTURE_2D,q,Je,Ie,$e,De);S.generateMipmaps=!1}else if(ct){if(Ot){const q=Ce(le);t.texStorage2D(i.TEXTURE_2D,we,Je,q.width,q.height)}D&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,Ie,$e,le)}else t.texImage2D(i.TEXTURE_2D,0,Je,Ie,$e,le);g(S)&&p(j),Oe.__version=Y.version,S.onUpdate&&S.onUpdate(S)}C.__version=S.version}function ue(C,S,k){if(S.image.length!==6)return;const j=St(C,S),te=S.source;t.bindTexture(i.TEXTURE_CUBE_MAP,C.__webglTexture,i.TEXTURE0+k);const Y=n.get(te);if(te.version!==Y.__version||j===!0){t.activeTexture(i.TEXTURE0+k);const Oe=pt.getPrimaries(pt.workingColorSpace),Me=S.colorSpace===Yi?null:pt.getPrimaries(S.colorSpace),Pe=S.colorSpace===Yi||Oe===Me?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,S.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,S.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,S.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,Pe);const ft=S.isCompressedTexture||S.image[0].isCompressedTexture,le=S.image[0]&&S.image[0].isDataTexture,Ie=[];for(let J=0;J<6;J++)!ft&&!le?Ie[J]=_(S.image[J],!0,s.maxCubemapSize):Ie[J]=le?S.image[J].image:S.image[J],Ie[J]=qe(S,Ie[J]);const $e=Ie[0],Je=r.convert(S.format,S.colorSpace),De=r.convert(S.type),mt=M(S.internalFormat,Je,De,S.colorSpace),ct=S.isVideoTexture!==!0,Ot=Y.__version===void 0||j===!0,D=te.dataReady;let we=A(S,$e);it(i.TEXTURE_CUBE_MAP,S);let q;if(ft){ct&&Ot&&t.texStorage2D(i.TEXTURE_CUBE_MAP,we,mt,$e.width,$e.height);for(let J=0;J<6;J++){q=Ie[J].mipmaps;for(let Ee=0;Ee<q.length;Ee++){const be=q[Ee];S.format!==Xn?Je!==null?ct?D&&t.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Ee,0,0,be.width,be.height,Je,be.data):t.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Ee,mt,be.width,be.height,0,be.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):ct?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Ee,0,0,be.width,be.height,Je,De,be.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Ee,mt,be.width,be.height,0,Je,De,be.data)}}}else{if(q=S.mipmaps,ct&&Ot){q.length>0&&we++;const J=Ce(Ie[0]);t.texStorage2D(i.TEXTURE_CUBE_MAP,we,mt,J.width,J.height)}for(let J=0;J<6;J++)if(le){ct?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,0,0,Ie[J].width,Ie[J].height,Je,De,Ie[J].data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,mt,Ie[J].width,Ie[J].height,0,Je,De,Ie[J].data);for(let Ee=0;Ee<q.length;Ee++){const st=q[Ee].image[J].image;ct?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Ee+1,0,0,st.width,st.height,Je,De,st.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Ee+1,mt,st.width,st.height,0,Je,De,st.data)}}else{ct?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,0,0,Je,De,Ie[J]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,mt,Je,De,Ie[J]);for(let Ee=0;Ee<q.length;Ee++){const be=q[Ee];ct?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Ee+1,0,0,Je,De,be.image[J]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+J,Ee+1,mt,Je,De,be.image[J])}}}g(S)&&p(i.TEXTURE_CUBE_MAP),Y.__version=te.version,S.onUpdate&&S.onUpdate(S)}C.__version=S.version}function Ne(C,S,k,j,te,Y){const Oe=r.convert(k.format,k.colorSpace),Me=r.convert(k.type),Pe=M(k.internalFormat,Oe,Me,k.colorSpace),ft=n.get(S),le=n.get(k);if(le.__renderTarget=S,!ft.__hasExternalTextures){const Ie=Math.max(1,S.width>>Y),$e=Math.max(1,S.height>>Y);te===i.TEXTURE_3D||te===i.TEXTURE_2D_ARRAY?t.texImage3D(te,Y,Pe,Ie,$e,S.depth,0,Oe,Me,null):t.texImage2D(te,Y,Pe,Ie,$e,0,Oe,Me,null)}t.bindFramebuffer(i.FRAMEBUFFER,C),Le(S)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,j,te,le.__webglTexture,0,ae(S)):(te===i.TEXTURE_2D||te>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&te<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,j,te,le.__webglTexture,Y),t.bindFramebuffer(i.FRAMEBUFFER,null)}function me(C,S,k){if(i.bindRenderbuffer(i.RENDERBUFFER,C),S.depthBuffer){const j=S.depthTexture,te=j&&j.isDepthTexture?j.type:null,Y=x(S.stencilBuffer,te),Oe=S.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Me=ae(S);Le(S)?a.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,Me,Y,S.width,S.height):k?i.renderbufferStorageMultisample(i.RENDERBUFFER,Me,Y,S.width,S.height):i.renderbufferStorage(i.RENDERBUFFER,Y,S.width,S.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,Oe,i.RENDERBUFFER,C)}else{const j=S.textures;for(let te=0;te<j.length;te++){const Y=j[te],Oe=r.convert(Y.format,Y.colorSpace),Me=r.convert(Y.type),Pe=M(Y.internalFormat,Oe,Me,Y.colorSpace),ft=ae(S);k&&Le(S)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,ft,Pe,S.width,S.height):Le(S)?a.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,ft,Pe,S.width,S.height):i.renderbufferStorage(i.RENDERBUFFER,Pe,S.width,S.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function We(C,S){if(S&&S.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(i.FRAMEBUFFER,C),!(S.depthTexture&&S.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const j=n.get(S.depthTexture);j.__renderTarget=S,(!j.__webglTexture||S.depthTexture.image.width!==S.width||S.depthTexture.image.height!==S.height)&&(S.depthTexture.image.width=S.width,S.depthTexture.image.height=S.height,S.depthTexture.needsUpdate=!0),Z(S.depthTexture,0);const te=j.__webglTexture,Y=ae(S);if(S.depthTexture.format===or)Le(S)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,te,0,Y):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,te,0);else if(S.depthTexture.format===gr)Le(S)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,te,0,Y):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,te,0);else throw new Error("Unknown depthTexture format")}function Qe(C){const S=n.get(C),k=C.isWebGLCubeRenderTarget===!0;if(S.__boundDepthTexture!==C.depthTexture){const j=C.depthTexture;if(S.__depthDisposeCallback&&S.__depthDisposeCallback(),j){const te=()=>{delete S.__boundDepthTexture,delete S.__depthDisposeCallback,j.removeEventListener("dispose",te)};j.addEventListener("dispose",te),S.__depthDisposeCallback=te}S.__boundDepthTexture=j}if(C.depthTexture&&!S.__autoAllocateDepthBuffer){if(k)throw new Error("target.depthTexture not supported in Cube render targets");We(S.__webglFramebuffer,C)}else if(k){S.__webglDepthbuffer=[];for(let j=0;j<6;j++)if(t.bindFramebuffer(i.FRAMEBUFFER,S.__webglFramebuffer[j]),S.__webglDepthbuffer[j]===void 0)S.__webglDepthbuffer[j]=i.createRenderbuffer(),me(S.__webglDepthbuffer[j],C,!1);else{const te=C.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Y=S.__webglDepthbuffer[j];i.bindRenderbuffer(i.RENDERBUFFER,Y),i.framebufferRenderbuffer(i.FRAMEBUFFER,te,i.RENDERBUFFER,Y)}}else if(t.bindFramebuffer(i.FRAMEBUFFER,S.__webglFramebuffer),S.__webglDepthbuffer===void 0)S.__webglDepthbuffer=i.createRenderbuffer(),me(S.__webglDepthbuffer,C,!1);else{const j=C.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,te=S.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,te),i.framebufferRenderbuffer(i.FRAMEBUFFER,j,i.RENDERBUFFER,te)}t.bindFramebuffer(i.FRAMEBUFFER,null)}function je(C,S,k){const j=n.get(C);S!==void 0&&Ne(j.__webglFramebuffer,C,C.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),k!==void 0&&Qe(C)}function _t(C){const S=C.texture,k=n.get(C),j=n.get(S);C.addEventListener("dispose",P);const te=C.textures,Y=C.isWebGLCubeRenderTarget===!0,Oe=te.length>1;if(Oe||(j.__webglTexture===void 0&&(j.__webglTexture=i.createTexture()),j.__version=S.version,o.memory.textures++),Y){k.__webglFramebuffer=[];for(let Me=0;Me<6;Me++)if(S.mipmaps&&S.mipmaps.length>0){k.__webglFramebuffer[Me]=[];for(let Pe=0;Pe<S.mipmaps.length;Pe++)k.__webglFramebuffer[Me][Pe]=i.createFramebuffer()}else k.__webglFramebuffer[Me]=i.createFramebuffer()}else{if(S.mipmaps&&S.mipmaps.length>0){k.__webglFramebuffer=[];for(let Me=0;Me<S.mipmaps.length;Me++)k.__webglFramebuffer[Me]=i.createFramebuffer()}else k.__webglFramebuffer=i.createFramebuffer();if(Oe)for(let Me=0,Pe=te.length;Me<Pe;Me++){const ft=n.get(te[Me]);ft.__webglTexture===void 0&&(ft.__webglTexture=i.createTexture(),o.memory.textures++)}if(C.samples>0&&Le(C)===!1){k.__webglMultisampledFramebuffer=i.createFramebuffer(),k.__webglColorRenderbuffer=[],t.bindFramebuffer(i.FRAMEBUFFER,k.__webglMultisampledFramebuffer);for(let Me=0;Me<te.length;Me++){const Pe=te[Me];k.__webglColorRenderbuffer[Me]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,k.__webglColorRenderbuffer[Me]);const ft=r.convert(Pe.format,Pe.colorSpace),le=r.convert(Pe.type),Ie=M(Pe.internalFormat,ft,le,Pe.colorSpace,C.isXRRenderTarget===!0),$e=ae(C);i.renderbufferStorageMultisample(i.RENDERBUFFER,$e,Ie,C.width,C.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Me,i.RENDERBUFFER,k.__webglColorRenderbuffer[Me])}i.bindRenderbuffer(i.RENDERBUFFER,null),C.depthBuffer&&(k.__webglDepthRenderbuffer=i.createRenderbuffer(),me(k.__webglDepthRenderbuffer,C,!0)),t.bindFramebuffer(i.FRAMEBUFFER,null)}}if(Y){t.bindTexture(i.TEXTURE_CUBE_MAP,j.__webglTexture),it(i.TEXTURE_CUBE_MAP,S);for(let Me=0;Me<6;Me++)if(S.mipmaps&&S.mipmaps.length>0)for(let Pe=0;Pe<S.mipmaps.length;Pe++)Ne(k.__webglFramebuffer[Me][Pe],C,S,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+Me,Pe);else Ne(k.__webglFramebuffer[Me],C,S,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+Me,0);g(S)&&p(i.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Oe){for(let Me=0,Pe=te.length;Me<Pe;Me++){const ft=te[Me],le=n.get(ft);t.bindTexture(i.TEXTURE_2D,le.__webglTexture),it(i.TEXTURE_2D,ft),Ne(k.__webglFramebuffer,C,ft,i.COLOR_ATTACHMENT0+Me,i.TEXTURE_2D,0),g(ft)&&p(i.TEXTURE_2D)}t.unbindTexture()}else{let Me=i.TEXTURE_2D;if((C.isWebGL3DRenderTarget||C.isWebGLArrayRenderTarget)&&(Me=C.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),t.bindTexture(Me,j.__webglTexture),it(Me,S),S.mipmaps&&S.mipmaps.length>0)for(let Pe=0;Pe<S.mipmaps.length;Pe++)Ne(k.__webglFramebuffer[Pe],C,S,i.COLOR_ATTACHMENT0,Me,Pe);else Ne(k.__webglFramebuffer,C,S,i.COLOR_ATTACHMENT0,Me,0);g(S)&&p(Me),t.unbindTexture()}C.depthBuffer&&Qe(C)}function ee(C){const S=C.textures;for(let k=0,j=S.length;k<j;k++){const te=S[k];if(g(te)){const Y=y(C),Oe=n.get(te).__webglTexture;t.bindTexture(Y,Oe),p(Y),t.unbindTexture()}}}const he=[],I=[];function ze(C){if(C.samples>0){if(Le(C)===!1){const S=C.textures,k=C.width,j=C.height;let te=i.COLOR_BUFFER_BIT;const Y=C.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Oe=n.get(C),Me=S.length>1;if(Me)for(let Pe=0;Pe<S.length;Pe++)t.bindFramebuffer(i.FRAMEBUFFER,Oe.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Pe,i.RENDERBUFFER,null),t.bindFramebuffer(i.FRAMEBUFFER,Oe.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Pe,i.TEXTURE_2D,null,0);t.bindFramebuffer(i.READ_FRAMEBUFFER,Oe.__webglMultisampledFramebuffer),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Oe.__webglFramebuffer);for(let Pe=0;Pe<S.length;Pe++){if(C.resolveDepthBuffer&&(C.depthBuffer&&(te|=i.DEPTH_BUFFER_BIT),C.stencilBuffer&&C.resolveStencilBuffer&&(te|=i.STENCIL_BUFFER_BIT)),Me){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,Oe.__webglColorRenderbuffer[Pe]);const ft=n.get(S[Pe]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,ft,0)}i.blitFramebuffer(0,0,k,j,0,0,k,j,te,i.NEAREST),c===!0&&(he.length=0,I.length=0,he.push(i.COLOR_ATTACHMENT0+Pe),C.depthBuffer&&C.resolveDepthBuffer===!1&&(he.push(Y),I.push(Y),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,I)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,he))}if(t.bindFramebuffer(i.READ_FRAMEBUFFER,null),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),Me)for(let Pe=0;Pe<S.length;Pe++){t.bindFramebuffer(i.FRAMEBUFFER,Oe.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+Pe,i.RENDERBUFFER,Oe.__webglColorRenderbuffer[Pe]);const ft=n.get(S[Pe]).__webglTexture;t.bindFramebuffer(i.FRAMEBUFFER,Oe.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+Pe,i.TEXTURE_2D,ft,0)}t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Oe.__webglMultisampledFramebuffer)}else if(C.depthBuffer&&C.resolveDepthBuffer===!1&&c){const S=C.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[S])}}}function ae(C){return Math.min(s.maxSamples,C.samples)}function Le(C){const S=n.get(C);return C.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&S.__useRenderToTexture!==!1}function _e(C){const S=o.render.frame;h.get(C)!==S&&(h.set(C,S),C.update())}function qe(C,S){const k=C.colorSpace,j=C.format,te=C.type;return C.isCompressedTexture===!0||C.isVideoTexture===!0||k!==vn&&k!==Yi&&(pt.getTransfer(k)===Nt?(j!==Xn||te!==Ui)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",k)),S}function Ce(C){return typeof HTMLImageElement<"u"&&C instanceof HTMLImageElement?(l.width=C.naturalWidth||C.width,l.height=C.naturalHeight||C.height):typeof VideoFrame<"u"&&C instanceof VideoFrame?(l.width=C.displayWidth,l.height=C.displayHeight):(l.width=C.width,l.height=C.height),l}this.allocateTextureUnit=F,this.resetTextureUnits=B,this.setTexture2D=Z,this.setTexture2DArray=X,this.setTexture3D=$,this.setTextureCube=W,this.rebindTextures=je,this.setupRenderTarget=_t,this.updateRenderTargetMipmap=ee,this.updateMultisampleRenderTarget=ze,this.setupDepthRenderbuffer=Qe,this.setupFrameBufferTexture=Ne,this.useMultisampledRTT=Le}function Hy(i,e){function t(n,s=Yi){let r;const o=pt.getTransfer(s);if(n===Ui)return i.UNSIGNED_BYTE;if(n===wh)return i.UNSIGNED_SHORT_4_4_4_4;if(n===bh)return i.UNSIGNED_SHORT_5_5_5_1;if(n===Sf)return i.UNSIGNED_INT_5_9_9_9_REV;if(n===wf)return i.BYTE;if(n===bf)return i.SHORT;if(n===ho)return i.UNSIGNED_SHORT;if(n===Mh)return i.INT;if(n===Ts)return i.UNSIGNED_INT;if(n===ri)return i.FLOAT;if(n===Mo)return i.HALF_FLOAT;if(n===Ef)return i.ALPHA;if(n===Tf)return i.RGB;if(n===Xn)return i.RGBA;if(n===Af)return i.LUMINANCE;if(n===Rf)return i.LUMINANCE_ALPHA;if(n===or)return i.DEPTH_COMPONENT;if(n===gr)return i.DEPTH_STENCIL;if(n===Sh)return i.RED;if(n===Eh)return i.RED_INTEGER;if(n===Cf)return i.RG;if(n===Th)return i.RG_INTEGER;if(n===Ah)return i.RGBA_INTEGER;if(n===va||n===ya||n===Ma||n===wa)if(o===Nt)if(r=e.get("WEBGL_compressed_texture_s3tc_srgb"),r!==null){if(n===va)return r.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===ya)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Ma)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===wa)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(r=e.get("WEBGL_compressed_texture_s3tc"),r!==null){if(n===va)return r.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===ya)return r.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Ma)return r.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===wa)return r.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===Pl||n===Ll||n===Il||n===Dl)if(r=e.get("WEBGL_compressed_texture_pvrtc"),r!==null){if(n===Pl)return r.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Ll)return r.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Il)return r.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===Dl)return r.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Nl||n===Ul||n===Ol)if(r=e.get("WEBGL_compressed_texture_etc"),r!==null){if(n===Nl||n===Ul)return o===Nt?r.COMPRESSED_SRGB8_ETC2:r.COMPRESSED_RGB8_ETC2;if(n===Ol)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:r.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Fl||n===Bl||n===kl||n===zl||n===Hl||n===Gl||n===Vl||n===Wl||n===Xl||n===ql||n===$l||n===jl||n===Yl||n===Kl)if(r=e.get("WEBGL_compressed_texture_astc"),r!==null){if(n===Fl)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:r.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Bl)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:r.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===kl)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:r.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===zl)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:r.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===Hl)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:r.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===Gl)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:r.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===Vl)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:r.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===Wl)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:r.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===Xl)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:r.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===ql)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:r.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===$l)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:r.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===jl)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:r.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Yl)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:r.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===Kl)return o===Nt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:r.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===ba||n===Zl||n===Jl)if(r=e.get("EXT_texture_compression_bptc"),r!==null){if(n===ba)return o===Nt?r.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:r.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===Zl)return r.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===Jl)return r.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Pf||n===Ql||n===eh||n===th)if(r=e.get("EXT_texture_compression_rgtc"),r!==null){if(n===ba)return r.COMPRESSED_RED_RGTC1_EXT;if(n===Ql)return r.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===eh)return r.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===th)return r.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===mr?i.UNSIGNED_INT_24_8:i[n]!==void 0?i[n]:null}return{convert:t}}class Gy extends Cn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class Ut extends kt{constructor(){super(),this.isGroup=!0,this.type="Group"}}const Vy={type:"move"};class Bc{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Ut,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Ut,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new v,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new v),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Ut,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new v,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new v),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let s=null,r=null,o=null;const a=this._targetRay,c=this._grip,l=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(l&&e.hand){o=!0;for(const _ of e.hand.values()){const g=t.getJointPose(_,n),p=this._getHandJoint(l,_);g!==null&&(p.matrix.fromArray(g.transform.matrix),p.matrix.decompose(p.position,p.rotation,p.scale),p.matrixWorldNeedsUpdate=!0,p.jointRadius=g.radius),p.visible=g!==null}const h=l.joints["index-finger-tip"],u=l.joints["thumb-tip"],d=h.position.distanceTo(u.position),f=.02,m=.005;l.inputState.pinching&&d>f+m?(l.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!l.inputState.pinching&&d<=f-m&&(l.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else c!==null&&e.gripSpace&&(r=t.getPose(e.gripSpace,n),r!==null&&(c.matrix.fromArray(r.transform.matrix),c.matrix.decompose(c.position,c.rotation,c.scale),c.matrixWorldNeedsUpdate=!0,r.linearVelocity?(c.hasLinearVelocity=!0,c.linearVelocity.copy(r.linearVelocity)):c.hasLinearVelocity=!1,r.angularVelocity?(c.hasAngularVelocity=!0,c.angularVelocity.copy(r.angularVelocity)):c.hasAngularVelocity=!1));a!==null&&(s=t.getPose(e.targetRaySpace,n),s===null&&r!==null&&(s=r),s!==null&&(a.matrix.fromArray(s.transform.matrix),a.matrix.decompose(a.position,a.rotation,a.scale),a.matrixWorldNeedsUpdate=!0,s.linearVelocity?(a.hasLinearVelocity=!0,a.linearVelocity.copy(s.linearVelocity)):a.hasLinearVelocity=!1,s.angularVelocity?(a.hasAngularVelocity=!0,a.angularVelocity.copy(s.angularVelocity)):a.hasAngularVelocity=!1,this.dispatchEvent(Vy)))}return a!==null&&(a.visible=s!==null),c!==null&&(c.visible=r!==null),l!==null&&(l.visible=o!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new Ut;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const Wy=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,Xy=`
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

}`;class qy{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const s=new rn,r=e.properties.get(s);r.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=s}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new di({vertexShader:Wy,fragmentShader:Xy,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new jt(new fi(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class $y extends Er{constructor(e,t){super();const n=this;let s=null,r=1,o=null,a="local-floor",c=1,l=null,h=null,u=null,d=null,f=null,m=null;const _=new qy,g=t.getContextAttributes();let p=null,y=null;const M=[],x=[],A=new re;let E=null;const P=new Cn;P.viewport=new bt;const R=new Cn;R.viewport=new bt;const b=[P,R],w=new Gy;let L=null,B=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(K){let ue=M[K];return ue===void 0&&(ue=new Bc,M[K]=ue),ue.getTargetRaySpace()},this.getControllerGrip=function(K){let ue=M[K];return ue===void 0&&(ue=new Bc,M[K]=ue),ue.getGripSpace()},this.getHand=function(K){let ue=M[K];return ue===void 0&&(ue=new Bc,M[K]=ue),ue.getHandSpace()};function F(K){const ue=x.indexOf(K.inputSource);if(ue===-1)return;const Ne=M[ue];Ne!==void 0&&(Ne.update(K.inputSource,K.frame,l||o),Ne.dispatchEvent({type:K.type,data:K.inputSource}))}function G(){s.removeEventListener("select",F),s.removeEventListener("selectstart",F),s.removeEventListener("selectend",F),s.removeEventListener("squeeze",F),s.removeEventListener("squeezestart",F),s.removeEventListener("squeezeend",F),s.removeEventListener("end",G),s.removeEventListener("inputsourceschange",Z);for(let K=0;K<M.length;K++){const ue=x[K];ue!==null&&(x[K]=null,M[K].disconnect(ue))}L=null,B=null,_.reset(),e.setRenderTarget(p),f=null,d=null,u=null,s=null,y=null,St.stop(),n.isPresenting=!1,e.setPixelRatio(E),e.setSize(A.width,A.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(K){r=K,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(K){a=K,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return l||o},this.setReferenceSpace=function(K){l=K},this.getBaseLayer=function(){return d!==null?d:f},this.getBinding=function(){return u},this.getFrame=function(){return m},this.getSession=function(){return s},this.setSession=async function(K){if(s=K,s!==null){if(p=e.getRenderTarget(),s.addEventListener("select",F),s.addEventListener("selectstart",F),s.addEventListener("selectend",F),s.addEventListener("squeeze",F),s.addEventListener("squeezestart",F),s.addEventListener("squeezeend",F),s.addEventListener("end",G),s.addEventListener("inputsourceschange",Z),g.xrCompatible!==!0&&await t.makeXRCompatible(),E=e.getPixelRatio(),e.getSize(A),s.renderState.layers===void 0){const ue={antialias:g.antialias,alpha:!0,depth:g.depth,stencil:g.stencil,framebufferScaleFactor:r};f=new XRWebGLLayer(s,t,ue),s.updateRenderState({baseLayer:f}),e.setPixelRatio(1),e.setSize(f.framebufferWidth,f.framebufferHeight,!1),y=new As(f.framebufferWidth,f.framebufferHeight,{format:Xn,type:Ui,colorSpace:e.outputColorSpace,stencilBuffer:g.stencil})}else{let ue=null,Ne=null,me=null;g.depth&&(me=g.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,ue=g.stencil?gr:or,Ne=g.stencil?mr:Ts);const We={colorFormat:t.RGBA8,depthFormat:me,scaleFactor:r};u=new XRWebGLBinding(s,t),d=u.createProjectionLayer(We),s.updateRenderState({layers:[d]}),e.setPixelRatio(1),e.setSize(d.textureWidth,d.textureHeight,!1),y=new As(d.textureWidth,d.textureHeight,{format:Xn,type:Ui,depthTexture:new Wf(d.textureWidth,d.textureHeight,Ne,void 0,void 0,void 0,void 0,void 0,void 0,ue),stencilBuffer:g.stencil,colorSpace:e.outputColorSpace,samples:g.antialias?4:0,resolveDepthBuffer:d.ignoreDepthValues===!1})}y.isXRRenderTarget=!0,this.setFoveation(c),l=null,o=await s.requestReferenceSpace(a),St.setContext(s),St.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(s!==null)return s.environmentBlendMode},this.getDepthTexture=function(){return _.getDepthTexture()};function Z(K){for(let ue=0;ue<K.removed.length;ue++){const Ne=K.removed[ue],me=x.indexOf(Ne);me>=0&&(x[me]=null,M[me].disconnect(Ne))}for(let ue=0;ue<K.added.length;ue++){const Ne=K.added[ue];let me=x.indexOf(Ne);if(me===-1){for(let Qe=0;Qe<M.length;Qe++)if(Qe>=x.length){x.push(Ne),me=Qe;break}else if(x[Qe]===null){x[Qe]=Ne,me=Qe;break}if(me===-1)break}const We=M[me];We&&We.connect(Ne)}}const X=new v,$=new v;function W(K,ue,Ne){X.setFromMatrixPosition(ue.matrixWorld),$.setFromMatrixPosition(Ne.matrixWorld);const me=X.distanceTo($),We=ue.projectionMatrix.elements,Qe=Ne.projectionMatrix.elements,je=We[14]/(We[10]-1),_t=We[14]/(We[10]+1),ee=(We[9]+1)/We[5],he=(We[9]-1)/We[5],I=(We[8]-1)/We[0],ze=(Qe[8]+1)/Qe[0],ae=je*I,Le=je*ze,_e=me/(-I+ze),qe=_e*-I;if(ue.matrixWorld.decompose(K.position,K.quaternion,K.scale),K.translateX(qe),K.translateZ(_e),K.matrixWorld.compose(K.position,K.quaternion,K.scale),K.matrixWorldInverse.copy(K.matrixWorld).invert(),We[10]===-1)K.projectionMatrix.copy(ue.projectionMatrix),K.projectionMatrixInverse.copy(ue.projectionMatrixInverse);else{const Ce=je+_e,C=_t+_e,S=ae-qe,k=Le+(me-qe),j=ee*_t/C*Ce,te=he*_t/C*Ce;K.projectionMatrix.makePerspective(S,k,j,te,Ce,C),K.projectionMatrixInverse.copy(K.projectionMatrix).invert()}}function ce(K,ue){ue===null?K.matrixWorld.copy(K.matrix):K.matrixWorld.multiplyMatrices(ue.matrixWorld,K.matrix),K.matrixWorldInverse.copy(K.matrixWorld).invert()}this.updateCamera=function(K){if(s===null)return;let ue=K.near,Ne=K.far;_.texture!==null&&(_.depthNear>0&&(ue=_.depthNear),_.depthFar>0&&(Ne=_.depthFar)),w.near=R.near=P.near=ue,w.far=R.far=P.far=Ne,(L!==w.near||B!==w.far)&&(s.updateRenderState({depthNear:w.near,depthFar:w.far}),L=w.near,B=w.far),P.layers.mask=K.layers.mask|2,R.layers.mask=K.layers.mask|4,w.layers.mask=P.layers.mask|R.layers.mask;const me=K.parent,We=w.cameras;ce(w,me);for(let Qe=0;Qe<We.length;Qe++)ce(We[Qe],me);We.length===2?W(w,P,R):w.projectionMatrix.copy(P.projectionMatrix),ve(K,w,me)};function ve(K,ue,Ne){Ne===null?K.matrix.copy(ue.matrixWorld):(K.matrix.copy(Ne.matrixWorld),K.matrix.invert(),K.matrix.multiply(ue.matrixWorld)),K.matrix.decompose(K.position,K.quaternion,K.scale),K.updateMatrixWorld(!0),K.projectionMatrix.copy(ue.projectionMatrix),K.projectionMatrixInverse.copy(ue.projectionMatrixInverse),K.isPerspectiveCamera&&(K.fov=_r*2*Math.atan(1/K.projectionMatrix.elements[5]),K.zoom=1)}this.getCamera=function(){return w},this.getFoveation=function(){if(!(d===null&&f===null))return c},this.setFoveation=function(K){c=K,d!==null&&(d.fixedFoveation=K),f!==null&&f.fixedFoveation!==void 0&&(f.fixedFoveation=K)},this.hasDepthSensing=function(){return _.texture!==null},this.getDepthSensingMesh=function(){return _.getMesh(w)};let Re=null;function it(K,ue){if(h=ue.getViewerPose(l||o),m=ue,h!==null){const Ne=h.views;f!==null&&(e.setRenderTargetFramebuffer(y,f.framebuffer),e.setRenderTarget(y));let me=!1;Ne.length!==w.cameras.length&&(w.cameras.length=0,me=!0);for(let Qe=0;Qe<Ne.length;Qe++){const je=Ne[Qe];let _t=null;if(f!==null)_t=f.getViewport(je);else{const he=u.getViewSubImage(d,je);_t=he.viewport,Qe===0&&(e.setRenderTargetTextures(y,he.colorTexture,d.ignoreDepthValues?void 0:he.depthStencilTexture),e.setRenderTarget(y))}let ee=b[Qe];ee===void 0&&(ee=new Cn,ee.layers.enable(Qe),ee.viewport=new bt,b[Qe]=ee),ee.matrix.fromArray(je.transform.matrix),ee.matrix.decompose(ee.position,ee.quaternion,ee.scale),ee.projectionMatrix.fromArray(je.projectionMatrix),ee.projectionMatrixInverse.copy(ee.projectionMatrix).invert(),ee.viewport.set(_t.x,_t.y,_t.width,_t.height),Qe===0&&(w.matrix.copy(ee.matrix),w.matrix.decompose(w.position,w.quaternion,w.scale)),me===!0&&w.cameras.push(ee)}const We=s.enabledFeatures;if(We&&We.includes("depth-sensing")){const Qe=u.getDepthInformation(Ne[0]);Qe&&Qe.isValid&&Qe.texture&&_.init(e,Qe,s.renderState)}}for(let Ne=0;Ne<M.length;Ne++){const me=x[Ne],We=M[Ne];me!==null&&We!==void 0&&We.update(me,ue,l||o)}Re&&Re(K,ue),ue.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:ue}),m=null}const St=new Vf;St.setAnimationLoop(it),this.setAnimationLoop=function(K){Re=K},this.dispose=function(){}}}const ms=new cn,jy=new ge;function Yy(i,e){function t(g,p){g.matrixAutoUpdate===!0&&g.updateMatrix(),p.value.copy(g.matrix)}function n(g,p){p.color.getRGB(g.fogColor.value,zf(i)),p.isFog?(g.fogNear.value=p.near,g.fogFar.value=p.far):p.isFogExp2&&(g.fogDensity.value=p.density)}function s(g,p,y,M,x){p.isMeshBasicMaterial||p.isMeshLambertMaterial?r(g,p):p.isMeshToonMaterial?(r(g,p),u(g,p)):p.isMeshPhongMaterial?(r(g,p),h(g,p)):p.isMeshStandardMaterial?(r(g,p),d(g,p),p.isMeshPhysicalMaterial&&f(g,p,x)):p.isMeshMatcapMaterial?(r(g,p),m(g,p)):p.isMeshDepthMaterial?r(g,p):p.isMeshDistanceMaterial?(r(g,p),_(g,p)):p.isMeshNormalMaterial?r(g,p):p.isLineBasicMaterial?(o(g,p),p.isLineDashedMaterial&&a(g,p)):p.isPointsMaterial?c(g,p,y,M):p.isSpriteMaterial?l(g,p):p.isShadowMaterial?(g.color.value.copy(p.color),g.opacity.value=p.opacity):p.isShaderMaterial&&(p.uniformsNeedUpdate=!1)}function r(g,p){g.opacity.value=p.opacity,p.color&&g.diffuse.value.copy(p.color),p.emissive&&g.emissive.value.copy(p.emissive).multiplyScalar(p.emissiveIntensity),p.map&&(g.map.value=p.map,t(p.map,g.mapTransform)),p.alphaMap&&(g.alphaMap.value=p.alphaMap,t(p.alphaMap,g.alphaMapTransform)),p.bumpMap&&(g.bumpMap.value=p.bumpMap,t(p.bumpMap,g.bumpMapTransform),g.bumpScale.value=p.bumpScale,p.side===Sn&&(g.bumpScale.value*=-1)),p.normalMap&&(g.normalMap.value=p.normalMap,t(p.normalMap,g.normalMapTransform),g.normalScale.value.copy(p.normalScale),p.side===Sn&&g.normalScale.value.negate()),p.displacementMap&&(g.displacementMap.value=p.displacementMap,t(p.displacementMap,g.displacementMapTransform),g.displacementScale.value=p.displacementScale,g.displacementBias.value=p.displacementBias),p.emissiveMap&&(g.emissiveMap.value=p.emissiveMap,t(p.emissiveMap,g.emissiveMapTransform)),p.specularMap&&(g.specularMap.value=p.specularMap,t(p.specularMap,g.specularMapTransform)),p.alphaTest>0&&(g.alphaTest.value=p.alphaTest);const y=e.get(p),M=y.envMap,x=y.envMapRotation;M&&(g.envMap.value=M,ms.copy(x),ms.x*=-1,ms.y*=-1,ms.z*=-1,M.isCubeTexture&&M.isRenderTargetTexture===!1&&(ms.y*=-1,ms.z*=-1),g.envMapRotation.value.setFromMatrix4(jy.makeRotationFromEuler(ms)),g.flipEnvMap.value=M.isCubeTexture&&M.isRenderTargetTexture===!1?-1:1,g.reflectivity.value=p.reflectivity,g.ior.value=p.ior,g.refractionRatio.value=p.refractionRatio),p.lightMap&&(g.lightMap.value=p.lightMap,g.lightMapIntensity.value=p.lightMapIntensity,t(p.lightMap,g.lightMapTransform)),p.aoMap&&(g.aoMap.value=p.aoMap,g.aoMapIntensity.value=p.aoMapIntensity,t(p.aoMap,g.aoMapTransform))}function o(g,p){g.diffuse.value.copy(p.color),g.opacity.value=p.opacity,p.map&&(g.map.value=p.map,t(p.map,g.mapTransform))}function a(g,p){g.dashSize.value=p.dashSize,g.totalSize.value=p.dashSize+p.gapSize,g.scale.value=p.scale}function c(g,p,y,M){g.diffuse.value.copy(p.color),g.opacity.value=p.opacity,g.size.value=p.size*y,g.scale.value=M*.5,p.map&&(g.map.value=p.map,t(p.map,g.uvTransform)),p.alphaMap&&(g.alphaMap.value=p.alphaMap,t(p.alphaMap,g.alphaMapTransform)),p.alphaTest>0&&(g.alphaTest.value=p.alphaTest)}function l(g,p){g.diffuse.value.copy(p.color),g.opacity.value=p.opacity,g.rotation.value=p.rotation,p.map&&(g.map.value=p.map,t(p.map,g.mapTransform)),p.alphaMap&&(g.alphaMap.value=p.alphaMap,t(p.alphaMap,g.alphaMapTransform)),p.alphaTest>0&&(g.alphaTest.value=p.alphaTest)}function h(g,p){g.specular.value.copy(p.specular),g.shininess.value=Math.max(p.shininess,1e-4)}function u(g,p){p.gradientMap&&(g.gradientMap.value=p.gradientMap)}function d(g,p){g.metalness.value=p.metalness,p.metalnessMap&&(g.metalnessMap.value=p.metalnessMap,t(p.metalnessMap,g.metalnessMapTransform)),g.roughness.value=p.roughness,p.roughnessMap&&(g.roughnessMap.value=p.roughnessMap,t(p.roughnessMap,g.roughnessMapTransform)),p.envMap&&(g.envMapIntensity.value=p.envMapIntensity)}function f(g,p,y){g.ior.value=p.ior,p.sheen>0&&(g.sheenColor.value.copy(p.sheenColor).multiplyScalar(p.sheen),g.sheenRoughness.value=p.sheenRoughness,p.sheenColorMap&&(g.sheenColorMap.value=p.sheenColorMap,t(p.sheenColorMap,g.sheenColorMapTransform)),p.sheenRoughnessMap&&(g.sheenRoughnessMap.value=p.sheenRoughnessMap,t(p.sheenRoughnessMap,g.sheenRoughnessMapTransform))),p.clearcoat>0&&(g.clearcoat.value=p.clearcoat,g.clearcoatRoughness.value=p.clearcoatRoughness,p.clearcoatMap&&(g.clearcoatMap.value=p.clearcoatMap,t(p.clearcoatMap,g.clearcoatMapTransform)),p.clearcoatRoughnessMap&&(g.clearcoatRoughnessMap.value=p.clearcoatRoughnessMap,t(p.clearcoatRoughnessMap,g.clearcoatRoughnessMapTransform)),p.clearcoatNormalMap&&(g.clearcoatNormalMap.value=p.clearcoatNormalMap,t(p.clearcoatNormalMap,g.clearcoatNormalMapTransform),g.clearcoatNormalScale.value.copy(p.clearcoatNormalScale),p.side===Sn&&g.clearcoatNormalScale.value.negate())),p.dispersion>0&&(g.dispersion.value=p.dispersion),p.iridescence>0&&(g.iridescence.value=p.iridescence,g.iridescenceIOR.value=p.iridescenceIOR,g.iridescenceThicknessMinimum.value=p.iridescenceThicknessRange[0],g.iridescenceThicknessMaximum.value=p.iridescenceThicknessRange[1],p.iridescenceMap&&(g.iridescenceMap.value=p.iridescenceMap,t(p.iridescenceMap,g.iridescenceMapTransform)),p.iridescenceThicknessMap&&(g.iridescenceThicknessMap.value=p.iridescenceThicknessMap,t(p.iridescenceThicknessMap,g.iridescenceThicknessMapTransform))),p.transmission>0&&(g.transmission.value=p.transmission,g.transmissionSamplerMap.value=y.texture,g.transmissionSamplerSize.value.set(y.width,y.height),p.transmissionMap&&(g.transmissionMap.value=p.transmissionMap,t(p.transmissionMap,g.transmissionMapTransform)),g.thickness.value=p.thickness,p.thicknessMap&&(g.thicknessMap.value=p.thicknessMap,t(p.thicknessMap,g.thicknessMapTransform)),g.attenuationDistance.value=p.attenuationDistance,g.attenuationColor.value.copy(p.attenuationColor)),p.anisotropy>0&&(g.anisotropyVector.value.set(p.anisotropy*Math.cos(p.anisotropyRotation),p.anisotropy*Math.sin(p.anisotropyRotation)),p.anisotropyMap&&(g.anisotropyMap.value=p.anisotropyMap,t(p.anisotropyMap,g.anisotropyMapTransform))),g.specularIntensity.value=p.specularIntensity,g.specularColor.value.copy(p.specularColor),p.specularColorMap&&(g.specularColorMap.value=p.specularColorMap,t(p.specularColorMap,g.specularColorMapTransform)),p.specularIntensityMap&&(g.specularIntensityMap.value=p.specularIntensityMap,t(p.specularIntensityMap,g.specularIntensityMapTransform))}function m(g,p){p.matcap&&(g.matcap.value=p.matcap)}function _(g,p){const y=e.get(p).light;g.referencePosition.value.setFromMatrixPosition(y.matrixWorld),g.nearDistance.value=y.shadow.camera.near,g.farDistance.value=y.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:s}}function Ky(i,e,t,n){let s={},r={},o=[];const a=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function c(y,M){const x=M.program;n.uniformBlockBinding(y,x)}function l(y,M){let x=s[y.id];x===void 0&&(m(y),x=h(y),s[y.id]=x,y.addEventListener("dispose",g));const A=M.program;n.updateUBOMapping(y,A);const E=e.render.frame;r[y.id]!==E&&(d(y),r[y.id]=E)}function h(y){const M=u();y.__bindingPointIndex=M;const x=i.createBuffer(),A=y.__size,E=y.usage;return i.bindBuffer(i.UNIFORM_BUFFER,x),i.bufferData(i.UNIFORM_BUFFER,A,E),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,M,x),x}function u(){for(let y=0;y<a;y++)if(o.indexOf(y)===-1)return o.push(y),y;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function d(y){const M=s[y.id],x=y.uniforms,A=y.__cache;i.bindBuffer(i.UNIFORM_BUFFER,M);for(let E=0,P=x.length;E<P;E++){const R=Array.isArray(x[E])?x[E]:[x[E]];for(let b=0,w=R.length;b<w;b++){const L=R[b];if(f(L,E,b,A)===!0){const B=L.__offset,F=Array.isArray(L.value)?L.value:[L.value];let G=0;for(let Z=0;Z<F.length;Z++){const X=F[Z],$=_(X);typeof X=="number"||typeof X=="boolean"?(L.__data[0]=X,i.bufferSubData(i.UNIFORM_BUFFER,B+G,L.__data)):X.isMatrix3?(L.__data[0]=X.elements[0],L.__data[1]=X.elements[1],L.__data[2]=X.elements[2],L.__data[3]=0,L.__data[4]=X.elements[3],L.__data[5]=X.elements[4],L.__data[6]=X.elements[5],L.__data[7]=0,L.__data[8]=X.elements[6],L.__data[9]=X.elements[7],L.__data[10]=X.elements[8],L.__data[11]=0):(X.toArray(L.__data,G),G+=$.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,B,L.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function f(y,M,x,A){const E=y.value,P=M+"_"+x;if(A[P]===void 0)return typeof E=="number"||typeof E=="boolean"?A[P]=E:A[P]=E.clone(),!0;{const R=A[P];if(typeof E=="number"||typeof E=="boolean"){if(R!==E)return A[P]=E,!0}else if(R.equals(E)===!1)return R.copy(E),!0}return!1}function m(y){const M=y.uniforms;let x=0;const A=16;for(let P=0,R=M.length;P<R;P++){const b=Array.isArray(M[P])?M[P]:[M[P]];for(let w=0,L=b.length;w<L;w++){const B=b[w],F=Array.isArray(B.value)?B.value:[B.value];for(let G=0,Z=F.length;G<Z;G++){const X=F[G],$=_(X),W=x%A,ce=W%$.boundary,ve=W+ce;x+=ce,ve!==0&&A-ve<$.storage&&(x+=A-ve),B.__data=new Float32Array($.storage/Float32Array.BYTES_PER_ELEMENT),B.__offset=x,x+=$.storage}}}const E=x%A;return E>0&&(x+=A-E),y.__size=x,y.__cache={},this}function _(y){const M={boundary:0,storage:0};return typeof y=="number"||typeof y=="boolean"?(M.boundary=4,M.storage=4):y.isVector2?(M.boundary=8,M.storage=8):y.isVector3||y.isColor?(M.boundary=16,M.storage=12):y.isVector4?(M.boundary=16,M.storage=16):y.isMatrix3?(M.boundary=48,M.storage=48):y.isMatrix4?(M.boundary=64,M.storage=64):y.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",y),M}function g(y){const M=y.target;M.removeEventListener("dispose",g);const x=o.indexOf(M.__bindingPointIndex);o.splice(x,1),i.deleteBuffer(s[M.id]),delete s[M.id],delete r[M.id]}function p(){for(const y in s)i.deleteBuffer(s[y]);o=[],s={},r={}}return{bind:c,update:l,dispose:p}}class pd{constructor(e={}){const{canvas:t=k0(),context:n=null,depth:s=!0,stencil:r=!1,alpha:o=!1,antialias:a=!1,premultipliedAlpha:c=!0,preserveDrawingBuffer:l=!1,powerPreference:h="default",failIfMajorPerformanceCaveat:u=!1,reverseDepthBuffer:d=!1}=e;this.isWebGLRenderer=!0;let f;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");f=n.getContextAttributes().alpha}else f=o;const m=new Uint32Array(4),_=new Int32Array(4);let g=null,p=null;const y=[],M=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=Yt,this.toneMapping=is,this.toneMappingExposure=1;const x=this;let A=!1,E=0,P=0,R=null,b=-1,w=null;const L=new bt,B=new bt;let F=null;const G=new Ve(0);let Z=0,X=t.width,$=t.height,W=1,ce=null,ve=null;const Re=new bt(0,0,X,$),it=new bt(0,0,X,$);let St=!1;const K=new Ph;let ue=!1,Ne=!1;const me=new ge,We=new ge,Qe=new v,je=new bt,_t={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let ee=!1;function he(){return R===null?W:1}let I=n;function ze(T,U){return t.getContext(T,U)}try{const T={alpha:!0,depth:s,stencil:r,antialias:a,premultipliedAlpha:c,preserveDrawingBuffer:l,powerPreference:h,failIfMajorPerformanceCaveat:u};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${yh}`),t.addEventListener("webglcontextlost",J,!1),t.addEventListener("webglcontextrestored",Ee,!1),t.addEventListener("webglcontextcreationerror",be,!1),I===null){const U="webgl2";if(I=ze(U,T),I===null)throw ze(U)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(T){throw console.error("THREE.WebGLRenderer: "+T.message),T}let ae,Le,_e,qe,Ce,C,S,k,j,te,Y,Oe,Me,Pe,ft,le,Ie,$e,Je,De,mt,ct,Ot,D;function we(){ae=new nv(I),ae.init(),ct=new Hy(I,ae),Le=new Kx(I,ae,e,ct),_e=new By(I,ae),Le.reverseDepthBuffer&&d&&_e.buffers.depth.setReversed(!0),qe=new rv(I),Ce=new by,C=new zy(I,ae,_e,Ce,Le,ct,qe),S=new Jx(x),k=new tv(x),j=new dg(I),Ot=new jx(I,j),te=new iv(I,j,qe,Ot),Y=new av(I,te,j,qe),Je=new ov(I,Le,C),le=new Zx(Ce),Oe=new wy(x,S,k,ae,Le,Ot,le),Me=new Yy(x,Ce),Pe=new Ey,ft=new Ly(ae),$e=new $x(x,S,k,_e,Y,f,c),Ie=new Oy(x,Y,Le),D=new Ky(I,qe,Le,_e),De=new Yx(I,ae,qe),mt=new sv(I,ae,qe),qe.programs=Oe.programs,x.capabilities=Le,x.extensions=ae,x.properties=Ce,x.renderLists=Pe,x.shadowMap=Ie,x.state=_e,x.info=qe}we();const q=new $y(x,I);this.xr=q,this.getContext=function(){return I},this.getContextAttributes=function(){return I.getContextAttributes()},this.forceContextLoss=function(){const T=ae.get("WEBGL_lose_context");T&&T.loseContext()},this.forceContextRestore=function(){const T=ae.get("WEBGL_lose_context");T&&T.restoreContext()},this.getPixelRatio=function(){return W},this.setPixelRatio=function(T){T!==void 0&&(W=T,this.setSize(X,$,!1))},this.getSize=function(T){return T.set(X,$)},this.setSize=function(T,U,H=!0){if(q.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}X=T,$=U,t.width=Math.floor(T*W),t.height=Math.floor(U*W),H===!0&&(t.style.width=T+"px",t.style.height=U+"px"),this.setViewport(0,0,T,U)},this.getDrawingBufferSize=function(T){return T.set(X*W,$*W).floor()},this.setDrawingBufferSize=function(T,U,H){X=T,$=U,W=H,t.width=Math.floor(T*H),t.height=Math.floor(U*H),this.setViewport(0,0,T,U)},this.getCurrentViewport=function(T){return T.copy(L)},this.getViewport=function(T){return T.copy(Re)},this.setViewport=function(T,U,H,V){T.isVector4?Re.set(T.x,T.y,T.z,T.w):Re.set(T,U,H,V),_e.viewport(L.copy(Re).multiplyScalar(W).round())},this.getScissor=function(T){return T.copy(it)},this.setScissor=function(T,U,H,V){T.isVector4?it.set(T.x,T.y,T.z,T.w):it.set(T,U,H,V),_e.scissor(B.copy(it).multiplyScalar(W).round())},this.getScissorTest=function(){return St},this.setScissorTest=function(T){_e.setScissorTest(St=T)},this.setOpaqueSort=function(T){ce=T},this.setTransparentSort=function(T){ve=T},this.getClearColor=function(T){return T.copy($e.getClearColor())},this.setClearColor=function(){$e.setClearColor.apply($e,arguments)},this.getClearAlpha=function(){return $e.getClearAlpha()},this.setClearAlpha=function(){$e.setClearAlpha.apply($e,arguments)},this.clear=function(T=!0,U=!0,H=!0){let V=0;if(T){let O=!1;if(R!==null){const de=R.texture.format;O=de===Ah||de===Th||de===Eh}if(O){const de=R.texture.type,Se=de===Ui||de===Ts||de===ho||de===mr||de===wh||de===bh,Fe=$e.getClearColor(),Be=$e.getClearAlpha(),et=Fe.r,rt=Fe.g,ke=Fe.b;Se?(m[0]=et,m[1]=rt,m[2]=ke,m[3]=Be,I.clearBufferuiv(I.COLOR,0,m)):(_[0]=et,_[1]=rt,_[2]=ke,_[3]=Be,I.clearBufferiv(I.COLOR,0,_))}else V|=I.COLOR_BUFFER_BIT}U&&(V|=I.DEPTH_BUFFER_BIT),H&&(V|=I.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),I.clear(V)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",J,!1),t.removeEventListener("webglcontextrestored",Ee,!1),t.removeEventListener("webglcontextcreationerror",be,!1),Pe.dispose(),ft.dispose(),Ce.dispose(),S.dispose(),k.dispose(),Y.dispose(),Ot.dispose(),D.dispose(),Oe.dispose(),q.dispose(),q.removeEventListener("sessionstart",su),q.removeEventListener("sessionend",ru),cs.stop()};function J(T){T.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),A=!0}function Ee(){console.log("THREE.WebGLRenderer: Context Restored."),A=!1;const T=qe.autoReset,U=Ie.enabled,H=Ie.autoUpdate,V=Ie.needsUpdate,O=Ie.type;we(),qe.autoReset=T,Ie.enabled=U,Ie.autoUpdate=H,Ie.needsUpdate=V,Ie.type=O}function be(T){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",T.statusMessage)}function st(T){const U=T.target;U.removeEventListener("dispose",st),qt(U)}function qt(T){un(T),Ce.remove(T)}function un(T){const U=Ce.get(T).programs;U!==void 0&&(U.forEach(function(H){Oe.releaseProgram(H)}),T.isShaderMaterial&&Oe.releaseShaderCache(T))}this.renderBufferDirect=function(T,U,H,V,O,de){U===null&&(U=_t);const Se=O.isMesh&&O.matrixWorld.determinant()<0,Fe=dm(T,U,H,V,O);_e.setMaterial(V,Se);let Be=H.index,et=1;if(V.wireframe===!0){if(Be=te.getWireframeAttribute(H),Be===void 0)return;et=2}const rt=H.drawRange,ke=H.attributes.position;let vt=rt.start*et,Ft=(rt.start+rt.count)*et;de!==null&&(vt=Math.max(vt,de.start*et),Ft=Math.min(Ft,(de.start+de.count)*et)),Be!==null?(vt=Math.max(vt,0),Ft=Math.min(Ft,Be.count)):ke!=null&&(vt=Math.max(vt,0),Ft=Math.min(Ft,ke.count));const zt=Ft-vt;if(zt<0||zt===1/0)return;Ot.setup(O,V,Fe,H,Be);let An,Et=De;if(Be!==null&&(An=j.get(Be),Et=mt,Et.setIndex(An)),O.isMesh)V.wireframe===!0?(_e.setLineWidth(V.wireframeLinewidth*he()),Et.setMode(I.LINES)):Et.setMode(I.TRIANGLES);else if(O.isLine){let Ge=V.linewidth;Ge===void 0&&(Ge=1),_e.setLineWidth(Ge*he()),O.isLineSegments?Et.setMode(I.LINES):O.isLineLoop?Et.setMode(I.LINE_LOOP):Et.setMode(I.LINE_STRIP)}else O.isPoints?Et.setMode(I.POINTS):O.isSprite&&Et.setMode(I.TRIANGLES);if(O.isBatchedMesh)if(O._multiDrawInstances!==null)Et.renderMultiDrawInstances(O._multiDrawStarts,O._multiDrawCounts,O._multiDrawCount,O._multiDrawInstances);else if(ae.get("WEBGL_multi_draw"))Et.renderMultiDraw(O._multiDrawStarts,O._multiDrawCounts,O._multiDrawCount);else{const Ge=O._multiDrawStarts,vi=O._multiDrawCounts,Tt=O._multiDrawCount,Qn=Be?j.get(Be).bytesPerElement:1,Ns=Ce.get(V).currentProgram.getUniforms();for(let In=0;In<Tt;In++)Ns.setValue(I,"_gl_DrawID",In),Et.render(Ge[In]/Qn,vi[In])}else if(O.isInstancedMesh)Et.renderInstances(vt,zt,O.count);else if(H.isInstancedBufferGeometry){const Ge=H._maxInstanceCount!==void 0?H._maxInstanceCount:1/0,vi=Math.min(H.instanceCount,Ge);Et.renderInstances(vt,zt,vi)}else Et.render(vt,zt)};function Rt(T,U,H){T.transparent===!0&&T.side===Pn&&T.forceSinglePass===!1?(T.side=Sn,T.needsUpdate=!0,Lo(T,U,H),T.side=Ni,T.needsUpdate=!0,Lo(T,U,H),T.side=Pn):Lo(T,U,H)}this.compile=function(T,U,H=null){H===null&&(H=T),p=ft.get(H),p.init(U),M.push(p),H.traverseVisible(function(O){O.isLight&&O.layers.test(U.layers)&&(p.pushLight(O),O.castShadow&&p.pushShadow(O))}),T!==H&&T.traverseVisible(function(O){O.isLight&&O.layers.test(U.layers)&&(p.pushLight(O),O.castShadow&&p.pushShadow(O))}),p.setupLights();const V=new Set;return T.traverse(function(O){if(!(O.isMesh||O.isPoints||O.isLine||O.isSprite))return;const de=O.material;if(de)if(Array.isArray(de))for(let Se=0;Se<de.length;Se++){const Fe=de[Se];Rt(Fe,H,O),V.add(Fe)}else Rt(de,H,O),V.add(de)}),M.pop(),p=null,V},this.compileAsync=function(T,U,H=null){const V=this.compile(T,U,H);return new Promise(O=>{function de(){if(V.forEach(function(Se){Ce.get(Se).currentProgram.isReady()&&V.delete(Se)}),V.size===0){O(T);return}setTimeout(de,10)}ae.get("KHR_parallel_shader_compile")!==null?de():setTimeout(de,10)})};let Jn=null;function xi(T){Jn&&Jn(T)}function su(){cs.stop()}function ru(){cs.start()}const cs=new Vf;cs.setAnimationLoop(xi),typeof self<"u"&&cs.setContext(self),this.setAnimationLoop=function(T){Jn=T,q.setAnimationLoop(T),T===null?cs.stop():cs.start()},q.addEventListener("sessionstart",su),q.addEventListener("sessionend",ru),this.render=function(T,U){if(U!==void 0&&U.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(A===!0)return;if(T.matrixWorldAutoUpdate===!0&&T.updateMatrixWorld(),U.parent===null&&U.matrixWorldAutoUpdate===!0&&U.updateMatrixWorld(),q.enabled===!0&&q.isPresenting===!0&&(q.cameraAutoUpdate===!0&&q.updateCamera(U),U=q.getCamera()),T.isScene===!0&&T.onBeforeRender(x,T,U,R),p=ft.get(T,M.length),p.init(U),M.push(p),We.multiplyMatrices(U.projectionMatrix,U.matrixWorldInverse),K.setFromProjectionMatrix(We),Ne=this.localClippingEnabled,ue=le.init(this.clippingPlanes,Ne),g=Pe.get(T,y.length),g.init(),y.push(g),q.enabled===!0&&q.isPresenting===!0){const de=x.xr.getDepthSensingMesh();de!==null&&lc(de,U,-1/0,x.sortObjects)}lc(T,U,0,x.sortObjects),g.finish(),x.sortObjects===!0&&g.sort(ce,ve),ee=q.enabled===!1||q.isPresenting===!1||q.hasDepthSensing()===!1,ee&&$e.addToRenderList(g,T),this.info.render.frame++,ue===!0&&le.beginShadows();const H=p.state.shadowsArray;Ie.render(H,T,U),ue===!0&&le.endShadows(),this.info.autoReset===!0&&this.info.reset();const V=g.opaque,O=g.transmissive;if(p.setupLights(),U.isArrayCamera){const de=U.cameras;if(O.length>0)for(let Se=0,Fe=de.length;Se<Fe;Se++){const Be=de[Se];au(V,O,T,Be)}ee&&$e.render(T);for(let Se=0,Fe=de.length;Se<Fe;Se++){const Be=de[Se];ou(g,T,Be,Be.viewport)}}else O.length>0&&au(V,O,T,U),ee&&$e.render(T),ou(g,T,U);R!==null&&(C.updateMultisampleRenderTarget(R),C.updateRenderTargetMipmap(R)),T.isScene===!0&&T.onAfterRender(x,T,U),Ot.resetDefaultState(),b=-1,w=null,M.pop(),M.length>0?(p=M[M.length-1],ue===!0&&le.setGlobalState(x.clippingPlanes,p.state.camera)):p=null,y.pop(),y.length>0?g=y[y.length-1]:g=null};function lc(T,U,H,V){if(T.visible===!1)return;if(T.layers.test(U.layers)){if(T.isGroup)H=T.renderOrder;else if(T.isLOD)T.autoUpdate===!0&&T.update(U);else if(T.isLight)p.pushLight(T),T.castShadow&&p.pushShadow(T);else if(T.isSprite){if(!T.frustumCulled||K.intersectsSprite(T)){V&&je.setFromMatrixPosition(T.matrixWorld).applyMatrix4(We);const Se=Y.update(T),Fe=T.material;Fe.visible&&g.push(T,Se,Fe,H,je.z,null)}}else if((T.isMesh||T.isLine||T.isPoints)&&(!T.frustumCulled||K.intersectsObject(T))){const Se=Y.update(T),Fe=T.material;if(V&&(T.boundingSphere!==void 0?(T.boundingSphere===null&&T.computeBoundingSphere(),je.copy(T.boundingSphere.center)):(Se.boundingSphere===null&&Se.computeBoundingSphere(),je.copy(Se.boundingSphere.center)),je.applyMatrix4(T.matrixWorld).applyMatrix4(We)),Array.isArray(Fe)){const Be=Se.groups;for(let et=0,rt=Be.length;et<rt;et++){const ke=Be[et],vt=Fe[ke.materialIndex];vt&&vt.visible&&g.push(T,Se,vt,H,je.z,ke)}}else Fe.visible&&g.push(T,Se,Fe,H,je.z,null)}}const de=T.children;for(let Se=0,Fe=de.length;Se<Fe;Se++)lc(de[Se],U,H,V)}function ou(T,U,H,V){const O=T.opaque,de=T.transmissive,Se=T.transparent;p.setupLightsView(H),ue===!0&&le.setGlobalState(x.clippingPlanes,H),V&&_e.viewport(L.copy(V)),O.length>0&&Po(O,U,H),de.length>0&&Po(de,U,H),Se.length>0&&Po(Se,U,H),_e.buffers.depth.setTest(!0),_e.buffers.depth.setMask(!0),_e.buffers.color.setMask(!0),_e.setPolygonOffset(!1)}function au(T,U,H,V){if((H.isScene===!0?H.overrideMaterial:null)!==null)return;p.state.transmissionRenderTarget[V.id]===void 0&&(p.state.transmissionRenderTarget[V.id]=new As(1,1,{generateMipmaps:!0,type:ae.has("EXT_color_buffer_half_float")||ae.has("EXT_color_buffer_float")?Mo:Ui,minFilter:Li,samples:4,stencilBuffer:r,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:pt.workingColorSpace}));const de=p.state.transmissionRenderTarget[V.id],Se=V.viewport||L;de.setSize(Se.z,Se.w);const Fe=x.getRenderTarget();x.setRenderTarget(de),x.getClearColor(G),Z=x.getClearAlpha(),Z<1&&x.setClearColor(16777215,.5),x.clear(),ee&&$e.render(H);const Be=x.toneMapping;x.toneMapping=is;const et=V.viewport;if(V.viewport!==void 0&&(V.viewport=void 0),p.setupLightsView(V),ue===!0&&le.setGlobalState(x.clippingPlanes,V),Po(T,H,V),C.updateMultisampleRenderTarget(de),C.updateRenderTargetMipmap(de),ae.has("WEBGL_multisampled_render_to_texture")===!1){let rt=!1;for(let ke=0,vt=U.length;ke<vt;ke++){const Ft=U[ke],zt=Ft.object,An=Ft.geometry,Et=Ft.material,Ge=Ft.group;if(Et.side===Pn&&zt.layers.test(V.layers)){const vi=Et.side;Et.side=Sn,Et.needsUpdate=!0,cu(zt,H,V,An,Et,Ge),Et.side=vi,Et.needsUpdate=!0,rt=!0}}rt===!0&&(C.updateMultisampleRenderTarget(de),C.updateRenderTargetMipmap(de))}x.setRenderTarget(Fe),x.setClearColor(G,Z),et!==void 0&&(V.viewport=et),x.toneMapping=Be}function Po(T,U,H){const V=U.isScene===!0?U.overrideMaterial:null;for(let O=0,de=T.length;O<de;O++){const Se=T[O],Fe=Se.object,Be=Se.geometry,et=V===null?Se.material:V,rt=Se.group;Fe.layers.test(H.layers)&&cu(Fe,U,H,Be,et,rt)}}function cu(T,U,H,V,O,de){T.onBeforeRender(x,U,H,V,O,de),T.modelViewMatrix.multiplyMatrices(H.matrixWorldInverse,T.matrixWorld),T.normalMatrix.getNormalMatrix(T.modelViewMatrix),O.onBeforeRender(x,U,H,V,T,de),O.transparent===!0&&O.side===Pn&&O.forceSinglePass===!1?(O.side=Sn,O.needsUpdate=!0,x.renderBufferDirect(H,U,V,O,T,de),O.side=Ni,O.needsUpdate=!0,x.renderBufferDirect(H,U,V,O,T,de),O.side=Pn):x.renderBufferDirect(H,U,V,O,T,de),T.onAfterRender(x,U,H,V,O,de)}function Lo(T,U,H){U.isScene!==!0&&(U=_t);const V=Ce.get(T),O=p.state.lights,de=p.state.shadowsArray,Se=O.state.version,Fe=Oe.getParameters(T,O.state,de,U,H),Be=Oe.getProgramCacheKey(Fe);let et=V.programs;V.environment=T.isMeshStandardMaterial?U.environment:null,V.fog=U.fog,V.envMap=(T.isMeshStandardMaterial?k:S).get(T.envMap||V.environment),V.envMapRotation=V.environment!==null&&T.envMap===null?U.environmentRotation:T.envMapRotation,et===void 0&&(T.addEventListener("dispose",st),et=new Map,V.programs=et);let rt=et.get(Be);if(rt!==void 0){if(V.currentProgram===rt&&V.lightsStateVersion===Se)return hu(T,Fe),rt}else Fe.uniforms=Oe.getUniforms(T),T.onBeforeCompile(Fe,x),rt=Oe.acquireProgram(Fe,Be),et.set(Be,rt),V.uniforms=Fe.uniforms;const ke=V.uniforms;return(!T.isShaderMaterial&&!T.isRawShaderMaterial||T.clipping===!0)&&(ke.clippingPlanes=le.uniform),hu(T,Fe),V.needsLights=pm(T),V.lightsStateVersion=Se,V.needsLights&&(ke.ambientLightColor.value=O.state.ambient,ke.lightProbe.value=O.state.probe,ke.directionalLights.value=O.state.directional,ke.directionalLightShadows.value=O.state.directionalShadow,ke.spotLights.value=O.state.spot,ke.spotLightShadows.value=O.state.spotShadow,ke.rectAreaLights.value=O.state.rectArea,ke.ltc_1.value=O.state.rectAreaLTC1,ke.ltc_2.value=O.state.rectAreaLTC2,ke.pointLights.value=O.state.point,ke.pointLightShadows.value=O.state.pointShadow,ke.hemisphereLights.value=O.state.hemi,ke.directionalShadowMap.value=O.state.directionalShadowMap,ke.directionalShadowMatrix.value=O.state.directionalShadowMatrix,ke.spotShadowMap.value=O.state.spotShadowMap,ke.spotLightMatrix.value=O.state.spotLightMatrix,ke.spotLightMap.value=O.state.spotLightMap,ke.pointShadowMap.value=O.state.pointShadowMap,ke.pointShadowMatrix.value=O.state.pointShadowMatrix),V.currentProgram=rt,V.uniformsList=null,rt}function lu(T){if(T.uniformsList===null){const U=T.currentProgram.getUniforms();T.uniformsList=Sa.seqWithValue(U.seq,T.uniforms)}return T.uniformsList}function hu(T,U){const H=Ce.get(T);H.outputColorSpace=U.outputColorSpace,H.batching=U.batching,H.batchingColor=U.batchingColor,H.instancing=U.instancing,H.instancingColor=U.instancingColor,H.instancingMorph=U.instancingMorph,H.skinning=U.skinning,H.morphTargets=U.morphTargets,H.morphNormals=U.morphNormals,H.morphColors=U.morphColors,H.morphTargetsCount=U.morphTargetsCount,H.numClippingPlanes=U.numClippingPlanes,H.numIntersection=U.numClipIntersection,H.vertexAlphas=U.vertexAlphas,H.vertexTangents=U.vertexTangents,H.toneMapping=U.toneMapping}function dm(T,U,H,V,O){U.isScene!==!0&&(U=_t),C.resetTextureUnits();const de=U.fog,Se=V.isMeshStandardMaterial?U.environment:null,Fe=R===null?x.outputColorSpace:R.isXRRenderTarget===!0?R.texture.colorSpace:vn,Be=(V.isMeshStandardMaterial?k:S).get(V.envMap||Se),et=V.vertexColors===!0&&!!H.attributes.color&&H.attributes.color.itemSize===4,rt=!!H.attributes.tangent&&(!!V.normalMap||V.anisotropy>0),ke=!!H.morphAttributes.position,vt=!!H.morphAttributes.normal,Ft=!!H.morphAttributes.color;let zt=is;V.toneMapped&&(R===null||R.isXRRenderTarget===!0)&&(zt=x.toneMapping);const An=H.morphAttributes.position||H.morphAttributes.normal||H.morphAttributes.color,Et=An!==void 0?An.length:0,Ge=Ce.get(V),vi=p.state.lights;if(ue===!0&&(Ne===!0||T!==w)){const zn=T===w&&V.id===b;le.setState(V,T,zn)}let Tt=!1;V.version===Ge.__version?(Ge.needsLights&&Ge.lightsStateVersion!==vi.state.version||Ge.outputColorSpace!==Fe||O.isBatchedMesh&&Ge.batching===!1||!O.isBatchedMesh&&Ge.batching===!0||O.isBatchedMesh&&Ge.batchingColor===!0&&O.colorTexture===null||O.isBatchedMesh&&Ge.batchingColor===!1&&O.colorTexture!==null||O.isInstancedMesh&&Ge.instancing===!1||!O.isInstancedMesh&&Ge.instancing===!0||O.isSkinnedMesh&&Ge.skinning===!1||!O.isSkinnedMesh&&Ge.skinning===!0||O.isInstancedMesh&&Ge.instancingColor===!0&&O.instanceColor===null||O.isInstancedMesh&&Ge.instancingColor===!1&&O.instanceColor!==null||O.isInstancedMesh&&Ge.instancingMorph===!0&&O.morphTexture===null||O.isInstancedMesh&&Ge.instancingMorph===!1&&O.morphTexture!==null||Ge.envMap!==Be||V.fog===!0&&Ge.fog!==de||Ge.numClippingPlanes!==void 0&&(Ge.numClippingPlanes!==le.numPlanes||Ge.numIntersection!==le.numIntersection)||Ge.vertexAlphas!==et||Ge.vertexTangents!==rt||Ge.morphTargets!==ke||Ge.morphNormals!==vt||Ge.morphColors!==Ft||Ge.toneMapping!==zt||Ge.morphTargetsCount!==Et)&&(Tt=!0):(Tt=!0,Ge.__version=V.version);let Qn=Ge.currentProgram;Tt===!0&&(Qn=Lo(V,U,O));let Ns=!1,In=!1,Or=!1;const Ht=Qn.getUniforms(),oi=Ge.uniforms;if(_e.useProgram(Qn.program)&&(Ns=!0,In=!0,Or=!0),V.id!==b&&(b=V.id,In=!0),Ns||w!==T){_e.buffers.depth.getReversed()?(me.copy(T.projectionMatrix),H0(me),G0(me),Ht.setValue(I,"projectionMatrix",me)):Ht.setValue(I,"projectionMatrix",T.projectionMatrix),Ht.setValue(I,"viewMatrix",T.matrixWorldInverse);const Bi=Ht.map.cameraPosition;Bi!==void 0&&Bi.setValue(I,Qe.setFromMatrixPosition(T.matrixWorld)),Le.logarithmicDepthBuffer&&Ht.setValue(I,"logDepthBufFC",2/(Math.log(T.far+1)/Math.LN2)),(V.isMeshPhongMaterial||V.isMeshToonMaterial||V.isMeshLambertMaterial||V.isMeshBasicMaterial||V.isMeshStandardMaterial||V.isShaderMaterial)&&Ht.setValue(I,"isOrthographic",T.isOrthographicCamera===!0),w!==T&&(w=T,In=!0,Or=!0)}if(O.isSkinnedMesh){Ht.setOptional(I,O,"bindMatrix"),Ht.setOptional(I,O,"bindMatrixInverse");const zn=O.skeleton;zn&&(zn.boneTexture===null&&zn.computeBoneTexture(),Ht.setValue(I,"boneTexture",zn.boneTexture,C))}O.isBatchedMesh&&(Ht.setOptional(I,O,"batchingTexture"),Ht.setValue(I,"batchingTexture",O._matricesTexture,C),Ht.setOptional(I,O,"batchingIdTexture"),Ht.setValue(I,"batchingIdTexture",O._indirectTexture,C),Ht.setOptional(I,O,"batchingColorTexture"),O._colorsTexture!==null&&Ht.setValue(I,"batchingColorTexture",O._colorsTexture,C));const Fr=H.morphAttributes;if((Fr.position!==void 0||Fr.normal!==void 0||Fr.color!==void 0)&&Je.update(O,H,Qn),(In||Ge.receiveShadow!==O.receiveShadow)&&(Ge.receiveShadow=O.receiveShadow,Ht.setValue(I,"receiveShadow",O.receiveShadow)),V.isMeshGouraudMaterial&&V.envMap!==null&&(oi.envMap.value=Be,oi.flipEnvMap.value=Be.isCubeTexture&&Be.isRenderTargetTexture===!1?-1:1),V.isMeshStandardMaterial&&V.envMap===null&&U.environment!==null&&(oi.envMapIntensity.value=U.environmentIntensity),In&&(Ht.setValue(I,"toneMappingExposure",x.toneMappingExposure),Ge.needsLights&&fm(oi,Or),de&&V.fog===!0&&Me.refreshFogUniforms(oi,de),Me.refreshMaterialUniforms(oi,V,W,$,p.state.transmissionRenderTarget[T.id]),Sa.upload(I,lu(Ge),oi,C)),V.isShaderMaterial&&V.uniformsNeedUpdate===!0&&(Sa.upload(I,lu(Ge),oi,C),V.uniformsNeedUpdate=!1),V.isSpriteMaterial&&Ht.setValue(I,"center",O.center),Ht.setValue(I,"modelViewMatrix",O.modelViewMatrix),Ht.setValue(I,"normalMatrix",O.normalMatrix),Ht.setValue(I,"modelMatrix",O.matrixWorld),V.isShaderMaterial||V.isRawShaderMaterial){const zn=V.uniformsGroups;for(let Bi=0,ki=zn.length;Bi<ki;Bi++){const uu=zn[Bi];D.update(uu,Qn),D.bind(uu,Qn)}}return Qn}function fm(T,U){T.ambientLightColor.needsUpdate=U,T.lightProbe.needsUpdate=U,T.directionalLights.needsUpdate=U,T.directionalLightShadows.needsUpdate=U,T.pointLights.needsUpdate=U,T.pointLightShadows.needsUpdate=U,T.spotLights.needsUpdate=U,T.spotLightShadows.needsUpdate=U,T.rectAreaLights.needsUpdate=U,T.hemisphereLights.needsUpdate=U}function pm(T){return T.isMeshLambertMaterial||T.isMeshToonMaterial||T.isMeshPhongMaterial||T.isMeshStandardMaterial||T.isShadowMaterial||T.isShaderMaterial&&T.lights===!0}this.getActiveCubeFace=function(){return E},this.getActiveMipmapLevel=function(){return P},this.getRenderTarget=function(){return R},this.setRenderTargetTextures=function(T,U,H){Ce.get(T.texture).__webglTexture=U,Ce.get(T.depthTexture).__webglTexture=H;const V=Ce.get(T);V.__hasExternalTextures=!0,V.__autoAllocateDepthBuffer=H===void 0,V.__autoAllocateDepthBuffer||ae.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),V.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(T,U){const H=Ce.get(T);H.__webglFramebuffer=U,H.__useDefaultFramebuffer=U===void 0},this.setRenderTarget=function(T,U=0,H=0){R=T,E=U,P=H;let V=!0,O=null,de=!1,Se=!1;if(T){const Be=Ce.get(T);if(Be.__useDefaultFramebuffer!==void 0)_e.bindFramebuffer(I.FRAMEBUFFER,null),V=!1;else if(Be.__webglFramebuffer===void 0)C.setupRenderTarget(T);else if(Be.__hasExternalTextures)C.rebindTextures(T,Ce.get(T.texture).__webglTexture,Ce.get(T.depthTexture).__webglTexture);else if(T.depthBuffer){const ke=T.depthTexture;if(Be.__boundDepthTexture!==ke){if(ke!==null&&Ce.has(ke)&&(T.width!==ke.image.width||T.height!==ke.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");C.setupDepthRenderbuffer(T)}}const et=T.texture;(et.isData3DTexture||et.isDataArrayTexture||et.isCompressedArrayTexture)&&(Se=!0);const rt=Ce.get(T).__webglFramebuffer;T.isWebGLCubeRenderTarget?(Array.isArray(rt[U])?O=rt[U][H]:O=rt[U],de=!0):T.samples>0&&C.useMultisampledRTT(T)===!1?O=Ce.get(T).__webglMultisampledFramebuffer:Array.isArray(rt)?O=rt[H]:O=rt,L.copy(T.viewport),B.copy(T.scissor),F=T.scissorTest}else L.copy(Re).multiplyScalar(W).floor(),B.copy(it).multiplyScalar(W).floor(),F=St;if(_e.bindFramebuffer(I.FRAMEBUFFER,O)&&V&&_e.drawBuffers(T,O),_e.viewport(L),_e.scissor(B),_e.setScissorTest(F),de){const Be=Ce.get(T.texture);I.framebufferTexture2D(I.FRAMEBUFFER,I.COLOR_ATTACHMENT0,I.TEXTURE_CUBE_MAP_POSITIVE_X+U,Be.__webglTexture,H)}else if(Se){const Be=Ce.get(T.texture),et=U||0;I.framebufferTextureLayer(I.FRAMEBUFFER,I.COLOR_ATTACHMENT0,Be.__webglTexture,H||0,et)}b=-1},this.readRenderTargetPixels=function(T,U,H,V,O,de,Se){if(!(T&&T.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Fe=Ce.get(T).__webglFramebuffer;if(T.isWebGLCubeRenderTarget&&Se!==void 0&&(Fe=Fe[Se]),Fe){_e.bindFramebuffer(I.FRAMEBUFFER,Fe);try{const Be=T.texture,et=Be.format,rt=Be.type;if(!Le.textureFormatReadable(et)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!Le.textureTypeReadable(rt)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}U>=0&&U<=T.width-V&&H>=0&&H<=T.height-O&&I.readPixels(U,H,V,O,ct.convert(et),ct.convert(rt),de)}finally{const Be=R!==null?Ce.get(R).__webglFramebuffer:null;_e.bindFramebuffer(I.FRAMEBUFFER,Be)}}},this.readRenderTargetPixelsAsync=async function(T,U,H,V,O,de,Se){if(!(T&&T.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Fe=Ce.get(T).__webglFramebuffer;if(T.isWebGLCubeRenderTarget&&Se!==void 0&&(Fe=Fe[Se]),Fe){const Be=T.texture,et=Be.format,rt=Be.type;if(!Le.textureFormatReadable(et))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!Le.textureTypeReadable(rt))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(U>=0&&U<=T.width-V&&H>=0&&H<=T.height-O){_e.bindFramebuffer(I.FRAMEBUFFER,Fe);const ke=I.createBuffer();I.bindBuffer(I.PIXEL_PACK_BUFFER,ke),I.bufferData(I.PIXEL_PACK_BUFFER,de.byteLength,I.STREAM_READ),I.readPixels(U,H,V,O,ct.convert(et),ct.convert(rt),0);const vt=R!==null?Ce.get(R).__webglFramebuffer:null;_e.bindFramebuffer(I.FRAMEBUFFER,vt);const Ft=I.fenceSync(I.SYNC_GPU_COMMANDS_COMPLETE,0);return I.flush(),await z0(I,Ft,4),I.bindBuffer(I.PIXEL_PACK_BUFFER,ke),I.getBufferSubData(I.PIXEL_PACK_BUFFER,0,de),I.deleteBuffer(ke),I.deleteSync(Ft),de}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(T,U=null,H=0){T.isTexture!==!0&&(eo("WebGLRenderer: copyFramebufferToTexture function signature has changed."),U=arguments[0]||null,T=arguments[1]);const V=Math.pow(2,-H),O=Math.floor(T.image.width*V),de=Math.floor(T.image.height*V),Se=U!==null?U.x:0,Fe=U!==null?U.y:0;C.setTexture2D(T,0),I.copyTexSubImage2D(I.TEXTURE_2D,H,0,0,Se,Fe,O,de),_e.unbindTexture()},this.copyTextureToTexture=function(T,U,H=null,V=null,O=0){T.isTexture!==!0&&(eo("WebGLRenderer: copyTextureToTexture function signature has changed."),V=arguments[0]||null,T=arguments[1],U=arguments[2],O=arguments[3]||0,H=null);let de,Se,Fe,Be,et,rt,ke,vt,Ft;const zt=T.isCompressedTexture?T.mipmaps[O]:T.image;H!==null?(de=H.max.x-H.min.x,Se=H.max.y-H.min.y,Fe=H.isBox3?H.max.z-H.min.z:1,Be=H.min.x,et=H.min.y,rt=H.isBox3?H.min.z:0):(de=zt.width,Se=zt.height,Fe=zt.depth||1,Be=0,et=0,rt=0),V!==null?(ke=V.x,vt=V.y,Ft=V.z):(ke=0,vt=0,Ft=0);const An=ct.convert(U.format),Et=ct.convert(U.type);let Ge;U.isData3DTexture?(C.setTexture3D(U,0),Ge=I.TEXTURE_3D):U.isDataArrayTexture||U.isCompressedArrayTexture?(C.setTexture2DArray(U,0),Ge=I.TEXTURE_2D_ARRAY):(C.setTexture2D(U,0),Ge=I.TEXTURE_2D),I.pixelStorei(I.UNPACK_FLIP_Y_WEBGL,U.flipY),I.pixelStorei(I.UNPACK_PREMULTIPLY_ALPHA_WEBGL,U.premultiplyAlpha),I.pixelStorei(I.UNPACK_ALIGNMENT,U.unpackAlignment);const vi=I.getParameter(I.UNPACK_ROW_LENGTH),Tt=I.getParameter(I.UNPACK_IMAGE_HEIGHT),Qn=I.getParameter(I.UNPACK_SKIP_PIXELS),Ns=I.getParameter(I.UNPACK_SKIP_ROWS),In=I.getParameter(I.UNPACK_SKIP_IMAGES);I.pixelStorei(I.UNPACK_ROW_LENGTH,zt.width),I.pixelStorei(I.UNPACK_IMAGE_HEIGHT,zt.height),I.pixelStorei(I.UNPACK_SKIP_PIXELS,Be),I.pixelStorei(I.UNPACK_SKIP_ROWS,et),I.pixelStorei(I.UNPACK_SKIP_IMAGES,rt);const Or=T.isDataArrayTexture||T.isData3DTexture,Ht=U.isDataArrayTexture||U.isData3DTexture;if(T.isRenderTargetTexture||T.isDepthTexture){const oi=Ce.get(T),Fr=Ce.get(U),zn=Ce.get(oi.__renderTarget),Bi=Ce.get(Fr.__renderTarget);_e.bindFramebuffer(I.READ_FRAMEBUFFER,zn.__webglFramebuffer),_e.bindFramebuffer(I.DRAW_FRAMEBUFFER,Bi.__webglFramebuffer);for(let ki=0;ki<Fe;ki++)Or&&I.framebufferTextureLayer(I.READ_FRAMEBUFFER,I.COLOR_ATTACHMENT0,Ce.get(T).__webglTexture,O,rt+ki),T.isDepthTexture?(Ht&&I.framebufferTextureLayer(I.DRAW_FRAMEBUFFER,I.COLOR_ATTACHMENT0,Ce.get(U).__webglTexture,O,Ft+ki),I.blitFramebuffer(Be,et,de,Se,ke,vt,de,Se,I.DEPTH_BUFFER_BIT,I.NEAREST)):Ht?I.copyTexSubImage3D(Ge,O,ke,vt,Ft+ki,Be,et,de,Se):I.copyTexSubImage2D(Ge,O,ke,vt,Ft+ki,Be,et,de,Se);_e.bindFramebuffer(I.READ_FRAMEBUFFER,null),_e.bindFramebuffer(I.DRAW_FRAMEBUFFER,null)}else Ht?T.isDataTexture||T.isData3DTexture?I.texSubImage3D(Ge,O,ke,vt,Ft,de,Se,Fe,An,Et,zt.data):U.isCompressedArrayTexture?I.compressedTexSubImage3D(Ge,O,ke,vt,Ft,de,Se,Fe,An,zt.data):I.texSubImage3D(Ge,O,ke,vt,Ft,de,Se,Fe,An,Et,zt):T.isDataTexture?I.texSubImage2D(I.TEXTURE_2D,O,ke,vt,de,Se,An,Et,zt.data):T.isCompressedTexture?I.compressedTexSubImage2D(I.TEXTURE_2D,O,ke,vt,zt.width,zt.height,An,zt.data):I.texSubImage2D(I.TEXTURE_2D,O,ke,vt,de,Se,An,Et,zt);I.pixelStorei(I.UNPACK_ROW_LENGTH,vi),I.pixelStorei(I.UNPACK_IMAGE_HEIGHT,Tt),I.pixelStorei(I.UNPACK_SKIP_PIXELS,Qn),I.pixelStorei(I.UNPACK_SKIP_ROWS,Ns),I.pixelStorei(I.UNPACK_SKIP_IMAGES,In),O===0&&U.generateMipmaps&&I.generateMipmap(Ge),_e.unbindTexture()},this.copyTextureToTexture3D=function(T,U,H=null,V=null,O=0){return T.isTexture!==!0&&(eo("WebGLRenderer: copyTextureToTexture3D function signature has changed."),H=arguments[0]||null,V=arguments[1]||null,T=arguments[2],U=arguments[3],O=arguments[4]||0),eo('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(T,U,H,V,O)},this.initRenderTarget=function(T){Ce.get(T).__webglFramebuffer===void 0&&C.setupRenderTarget(T)},this.initTexture=function(T){T.isCubeTexture?C.setTextureCube(T,0):T.isData3DTexture?C.setTexture3D(T,0):T.isDataArrayTexture||T.isCompressedArrayTexture?C.setTexture2DArray(T,0):C.setTexture2D(T,0),_e.unbindTexture()},this.resetState=function(){E=0,P=0,R=null,_e.reset(),Ot.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Ii}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorspace=pt._getDrawingBufferColorSpace(e),t.unpackColorSpace=pt._getUnpackColorSpace()}}class ja extends kt{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new cn,this.environmentIntensity=1,this.environmentRotation=new cn,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class Zy{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=ih,this.updateRanges=[],this.version=0,this.uuid=$n()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let s=0,r=this.stride;s<r;s++)this.array[e+s]=t.array[n+s];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=$n()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=$n()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const yn=new v;class Ih{constructor(e,t,n,s=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=s}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)yn.fromBufferAttribute(this,t),yn.applyMatrix4(e),this.setXYZ(t,yn.x,yn.y,yn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)yn.fromBufferAttribute(this,t),yn.applyNormalMatrix(e),this.setXYZ(t,yn.x,yn.y,yn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)yn.fromBufferAttribute(this,t),yn.transformDirection(e),this.setXYZ(t,yn.x,yn.y,yn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=si(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=Pt(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=Pt(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=Pt(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=Pt(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=Pt(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=si(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=si(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=si(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=si(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=Pt(t,this.array),n=Pt(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=Pt(t,this.array),n=Pt(n,this.array),s=Pt(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=Pt(t,this.array),n=Pt(n,this.array),s=Pt(s,this.array),r=Pt(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this.data.array[e+3]=r,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return new on(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new Ih(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}const md=new v,gd=new bt,_d=new bt,Jy=new v,xd=new ge,Jo=new v,kc=new pi,vd=new ge,zc=new Xa;class Dh extends jt{constructor(e,t){super(e,t),this.isSkinnedMesh=!0,this.type="SkinnedMesh",this.bindMode=gu,this.bindMatrix=new ge,this.bindMatrixInverse=new ge,this.boundingBox=null,this.boundingSphere=null}computeBoundingBox(){const e=this.geometry;this.boundingBox===null&&(this.boundingBox=new an),this.boundingBox.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,Jo),this.boundingBox.expandByPoint(Jo)}computeBoundingSphere(){const e=this.geometry;this.boundingSphere===null&&(this.boundingSphere=new pi),this.boundingSphere.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,Jo),this.boundingSphere.expandByPoint(Jo)}copy(e,t){return super.copy(e,t),this.bindMode=e.bindMode,this.bindMatrix.copy(e.bindMatrix),this.bindMatrixInverse.copy(e.bindMatrixInverse),this.skeleton=e.skeleton,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}raycast(e,t){const n=this.material,s=this.matrixWorld;n!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),kc.copy(this.boundingSphere),kc.applyMatrix4(s),e.ray.intersectsSphere(kc)!==!1&&(vd.copy(s).invert(),zc.copy(e.ray).applyMatrix4(vd),!(this.boundingBox!==null&&zc.intersectsBox(this.boundingBox)===!1)&&this._computeIntersections(e,t,zc)))}getVertexPosition(e,t){return super.getVertexPosition(e,t),this.applyBoneTransform(e,t),t}bind(e,t){this.skeleton=e,t===void 0&&(this.updateMatrixWorld(!0),this.skeleton.calculateInverses(),t=this.matrixWorld),this.bindMatrix.copy(t),this.bindMatrixInverse.copy(t).invert()}pose(){this.skeleton.pose()}normalizeSkinWeights(){const e=new bt,t=this.geometry.attributes.skinWeight;for(let n=0,s=t.count;n<s;n++){e.fromBufferAttribute(t,n);const r=1/e.manhattanLength();r!==1/0?e.multiplyScalar(r):e.set(1,0,0,0),t.setXYZW(n,e.x,e.y,e.z,e.w)}}updateMatrixWorld(e){super.updateMatrixWorld(e),this.bindMode===gu?this.bindMatrixInverse.copy(this.matrixWorld).invert():this.bindMode===h0?this.bindMatrixInverse.copy(this.bindMatrix).invert():console.warn("THREE.SkinnedMesh: Unrecognized bindMode: "+this.bindMode)}applyBoneTransform(e,t){const n=this.skeleton,s=this.geometry;gd.fromBufferAttribute(s.attributes.skinIndex,e),_d.fromBufferAttribute(s.attributes.skinWeight,e),md.copy(t).applyMatrix4(this.bindMatrix),t.set(0,0,0);for(let r=0;r<4;r++){const o=_d.getComponent(r);if(o!==0){const a=gd.getComponent(r);xd.multiplyMatrices(n.bones[a].matrixWorld,n.boneInverses[a]),t.addScaledVector(Jy.copy(md).applyMatrix4(xd),o)}}return t.applyMatrix4(this.bindMatrixInverse)}}class Yf extends kt{constructor(){super(),this.isBone=!0,this.type="Bone"}}class Nh extends rn{constructor(e=null,t=1,n=1,s,r,o,a,c,l=xn,h=xn,u,d){super(null,o,a,c,l,h,s,r,u,d),this.isDataTexture=!0,this.image={data:e,width:t,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const yd=new ge,Qy=new ge;class Uh{constructor(e=[],t=[]){this.uuid=$n(),this.bones=e.slice(0),this.boneInverses=t,this.boneMatrices=null,this.boneTexture=null,this.init()}init(){const e=this.bones,t=this.boneInverses;if(this.boneMatrices=new Float32Array(e.length*16),t.length===0)this.calculateInverses();else if(e.length!==t.length){console.warn("THREE.Skeleton: Number of inverse bone matrices does not match amount of bones."),this.boneInverses=[];for(let n=0,s=this.bones.length;n<s;n++)this.boneInverses.push(new ge)}}calculateInverses(){this.boneInverses.length=0;for(let e=0,t=this.bones.length;e<t;e++){const n=new ge;this.bones[e]&&n.copy(this.bones[e].matrixWorld).invert(),this.boneInverses.push(n)}}pose(){for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&n.matrixWorld.copy(this.boneInverses[e]).invert()}for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&(n.parent&&n.parent.isBone?(n.matrix.copy(n.parent.matrixWorld).invert(),n.matrix.multiply(n.matrixWorld)):n.matrix.copy(n.matrixWorld),n.matrix.decompose(n.position,n.quaternion,n.scale))}}update(){const e=this.bones,t=this.boneInverses,n=this.boneMatrices,s=this.boneTexture;for(let r=0,o=e.length;r<o;r++){const a=e[r]?e[r].matrixWorld:Qy;yd.multiplyMatrices(a,t[r]),yd.toArray(n,r*16)}s!==null&&(s.needsUpdate=!0)}clone(){return new Uh(this.bones,this.boneInverses)}computeBoneTexture(){let e=Math.sqrt(this.bones.length*4);e=Math.ceil(e/4)*4,e=Math.max(e,4);const t=new Float32Array(e*e*4);t.set(this.boneMatrices);const n=new Nh(t,e,e,Xn,ri);return n.needsUpdate=!0,this.boneMatrices=t,this.boneTexture=n,this}getBoneByName(e){for(let t=0,n=this.bones.length;t<n;t++){const s=this.bones[t];if(s.name===e)return s}}dispose(){this.boneTexture!==null&&(this.boneTexture.dispose(),this.boneTexture=null)}fromJSON(e,t){this.uuid=e.uuid;for(let n=0,s=e.bones.length;n<s;n++){const r=e.bones[n];let o=t[r];o===void 0&&(console.warn("THREE.Skeleton: No bone found with UUID:",r),o=new Yf),this.bones.push(o),this.boneInverses.push(new ge().fromArray(e.boneInverses[n]))}return this.init(),this}toJSON(){const e={metadata:{version:4.6,type:"Skeleton",generator:"Skeleton.toJSON"},bones:[],boneInverses:[]};e.uuid=this.uuid;const t=this.bones,n=this.boneInverses;for(let s=0,r=t.length;s<r;s++){const o=t[s];e.bones.push(o.uuid);const a=n[s];e.boneInverses.push(a.toArray())}return e}}class rh extends on{constructor(e,t,n,s=1){super(e,t,n),this.isInstancedBufferAttribute=!0,this.meshPerAttribute=s}copy(e){return super.copy(e),this.meshPerAttribute=e.meshPerAttribute,this}toJSON(){const e=super.toJSON();return e.meshPerAttribute=this.meshPerAttribute,e.isInstancedBufferAttribute=!0,e}}const Ys=new ge,Md=new ge,Qo=[],wd=new an,eM=new ge,Gr=new jt,Vr=new pi;class tM extends jt{constructor(e,t,n){super(e,t),this.isInstancedMesh=!0,this.instanceMatrix=new rh(new Float32Array(n*16),16),this.instanceColor=null,this.morphTexture=null,this.count=n,this.boundingBox=null,this.boundingSphere=null;for(let s=0;s<n;s++)this.setMatrixAt(s,eM)}computeBoundingBox(){const e=this.geometry,t=this.count;this.boundingBox===null&&(this.boundingBox=new an),e.boundingBox===null&&e.computeBoundingBox(),this.boundingBox.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,Ys),wd.copy(e.boundingBox).applyMatrix4(Ys),this.boundingBox.union(wd)}computeBoundingSphere(){const e=this.geometry,t=this.count;this.boundingSphere===null&&(this.boundingSphere=new pi),e.boundingSphere===null&&e.computeBoundingSphere(),this.boundingSphere.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,Ys),Vr.copy(e.boundingSphere).applyMatrix4(Ys),this.boundingSphere.union(Vr)}copy(e,t){return super.copy(e,t),this.instanceMatrix.copy(e.instanceMatrix),e.morphTexture!==null&&(this.morphTexture=e.morphTexture.clone()),e.instanceColor!==null&&(this.instanceColor=e.instanceColor.clone()),this.count=e.count,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}getColorAt(e,t){t.fromArray(this.instanceColor.array,e*3)}getMatrixAt(e,t){t.fromArray(this.instanceMatrix.array,e*16)}getMorphAt(e,t){const n=t.morphTargetInfluences,s=this.morphTexture.source.data.data,r=n.length+1,o=e*r+1;for(let a=0;a<n.length;a++)n[a]=s[o+a]}raycast(e,t){const n=this.matrixWorld,s=this.count;if(Gr.geometry=this.geometry,Gr.material=this.material,Gr.material!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),Vr.copy(this.boundingSphere),Vr.applyMatrix4(n),e.ray.intersectsSphere(Vr)!==!1))for(let r=0;r<s;r++){this.getMatrixAt(r,Ys),Md.multiplyMatrices(n,Ys),Gr.matrixWorld=Md,Gr.raycast(e,Qo);for(let o=0,a=Qo.length;o<a;o++){const c=Qo[o];c.instanceId=r,c.object=this,t.push(c)}Qo.length=0}}setColorAt(e,t){this.instanceColor===null&&(this.instanceColor=new rh(new Float32Array(this.instanceMatrix.count*3).fill(1),3)),t.toArray(this.instanceColor.array,e*3)}setMatrixAt(e,t){t.toArray(this.instanceMatrix.array,e*16)}setMorphAt(e,t){const n=t.morphTargetInfluences,s=n.length+1;this.morphTexture===null&&(this.morphTexture=new Nh(new Float32Array(s*this.count),s,this.count,Sh,ri));const r=this.morphTexture.source.data.data;let o=0;for(let l=0;l<n.length;l++)o+=n[l];const a=this.geometry.morphTargetsRelative?1:1-o,c=s*e;r[c]=a,r.set(n,c+1)}updateMorphTargets(){}dispose(){return this.dispatchEvent({type:"dispose"}),this.morphTexture!==null&&(this.morphTexture.dispose(),this.morphTexture=null),this}}class Rs extends ui{static get type(){return"LineBasicMaterial"}constructor(e){super(),this.isLineBasicMaterial=!0,this.color=new Ve(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const La=new v,Ia=new v,bd=new ge,Wr=new Xa,ea=new pi,Hc=new v,Sd=new v;class Oh extends kt{constructor(e=new Xt,t=new Rs){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let s=1,r=t.count;s<r;s++)La.fromBufferAttribute(t,s-1),Ia.fromBufferAttribute(t,s),n[s]=n[s-1],n[s]+=La.distanceTo(Ia);e.setAttribute("lineDistance",new ht(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Line.threshold,o=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),ea.copy(n.boundingSphere),ea.applyMatrix4(s),ea.radius+=r,e.ray.intersectsSphere(ea)===!1)return;bd.copy(s).invert(),Wr.copy(e.ray).applyMatrix4(bd);const a=r/((this.scale.x+this.scale.y+this.scale.z)/3),c=a*a,l=this.isLineSegments?2:1,h=n.index,d=n.attributes.position;if(h!==null){const f=Math.max(0,o.start),m=Math.min(h.count,o.start+o.count);for(let _=f,g=m-1;_<g;_+=l){const p=h.getX(_),y=h.getX(_+1),M=ta(this,e,Wr,c,p,y);M&&t.push(M)}if(this.isLineLoop){const _=h.getX(m-1),g=h.getX(f),p=ta(this,e,Wr,c,_,g);p&&t.push(p)}}else{const f=Math.max(0,o.start),m=Math.min(d.count,o.start+o.count);for(let _=f,g=m-1;_<g;_+=l){const p=ta(this,e,Wr,c,_,_+1);p&&t.push(p)}if(this.isLineLoop){const _=ta(this,e,Wr,c,m-1,f);_&&t.push(_)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}}function ta(i,e,t,n,s,r){const o=i.geometry.attributes.position;if(La.fromBufferAttribute(o,s),Ia.fromBufferAttribute(o,r),t.distanceSqToSegment(La,Ia,Hc,Sd)>n)return;Hc.applyMatrix4(i.matrixWorld);const c=e.ray.origin.distanceTo(Hc);if(!(c<e.near||c>e.far))return{distance:c,point:Sd.clone().applyMatrix4(i.matrixWorld),index:s,face:null,faceIndex:null,barycoord:null,object:i}}const Ed=new v,Td=new v;class wo extends Oh{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let s=0,r=t.count;s<r;s+=2)Ed.fromBufferAttribute(t,s),Td.fromBufferAttribute(t,s+1),n[s]=s===0?0:n[s-1],n[s+1]=n[s]+Ed.distanceTo(Td);e.setAttribute("lineDistance",new ht(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class Kf extends Oh{constructor(e,t){super(e,t),this.isLineLoop=!0,this.type="LineLoop"}}class Zf extends ui{static get type(){return"PointsMaterial"}constructor(e){super(),this.isPointsMaterial=!0,this.color=new Ve(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Ad=new ge,oh=new Xa,na=new pi,ia=new v;class nM extends kt{constructor(e=new Xt,t=new Zf){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Points.threshold,o=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),na.copy(n.boundingSphere),na.applyMatrix4(s),na.radius+=r,e.ray.intersectsSphere(na)===!1)return;Ad.copy(s).invert(),oh.copy(e.ray).applyMatrix4(Ad);const a=r/((this.scale.x+this.scale.y+this.scale.z)/3),c=a*a,l=n.index,u=n.attributes.position;if(l!==null){const d=Math.max(0,o.start),f=Math.min(l.count,o.start+o.count);for(let m=d,_=f;m<_;m++){const g=l.getX(m);ia.fromBufferAttribute(u,g),Rd(ia,g,c,s,e,t,this)}}else{const d=Math.max(0,o.start),f=Math.min(u.count,o.start+o.count);for(let m=d,_=f;m<_;m++)ia.fromBufferAttribute(u,m),Rd(ia,m,c,s,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}}function Rd(i,e,t,n,s,r,o){const a=oh.distanceSqToPoint(i);if(a<t){const c=new v;oh.closestPointToPoint(i,c),c.applyMatrix4(n);const l=s.ray.origin.distanceTo(c);if(l<s.near||l>s.far)return;r.push({distance:l,distanceToRay:Math.sqrt(a),point:c,index:e,face:null,faceIndex:null,barycoord:null,object:o})}}class mi{constructor(){this.type="Curve",this.arcLengthDivisions=200}getPoint(){return console.warn("THREE.Curve: .getPoint() not implemented."),null}getPointAt(e,t){const n=this.getUtoTmapping(e);return this.getPoint(n,t)}getPoints(e=5){const t=[];for(let n=0;n<=e;n++)t.push(this.getPoint(n/e));return t}getSpacedPoints(e=5){const t=[];for(let n=0;n<=e;n++)t.push(this.getPointAt(n/e));return t}getLength(){const e=this.getLengths();return e[e.length-1]}getLengths(e=this.arcLengthDivisions){if(this.cacheArcLengths&&this.cacheArcLengths.length===e+1&&!this.needsUpdate)return this.cacheArcLengths;this.needsUpdate=!1;const t=[];let n,s=this.getPoint(0),r=0;t.push(0);for(let o=1;o<=e;o++)n=this.getPoint(o/e),r+=n.distanceTo(s),t.push(r),s=n;return this.cacheArcLengths=t,t}updateArcLengths(){this.needsUpdate=!0,this.getLengths()}getUtoTmapping(e,t){const n=this.getLengths();let s=0;const r=n.length;let o;t?o=t:o=e*n[r-1];let a=0,c=r-1,l;for(;a<=c;)if(s=Math.floor(a+(c-a)/2),l=n[s]-o,l<0)a=s+1;else if(l>0)c=s-1;else{c=s;break}if(s=c,n[s]===o)return s/(r-1);const h=n[s],d=n[s+1]-h,f=(o-h)/d;return(s+f)/(r-1)}getTangent(e,t){let s=e-1e-4,r=e+1e-4;s<0&&(s=0),r>1&&(r=1);const o=this.getPoint(s),a=this.getPoint(r),c=t||(o.isVector2?new re:new v);return c.copy(a).sub(o).normalize(),c}getTangentAt(e,t){const n=this.getUtoTmapping(e);return this.getTangent(n,t)}computeFrenetFrames(e,t){const n=new v,s=[],r=[],o=[],a=new v,c=new ge;for(let f=0;f<=e;f++){const m=f/e;s[f]=this.getTangentAt(m,new v)}r[0]=new v,o[0]=new v;let l=Number.MAX_VALUE;const h=Math.abs(s[0].x),u=Math.abs(s[0].y),d=Math.abs(s[0].z);h<=l&&(l=h,n.set(1,0,0)),u<=l&&(l=u,n.set(0,1,0)),d<=l&&n.set(0,0,1),a.crossVectors(s[0],n).normalize(),r[0].crossVectors(s[0],a),o[0].crossVectors(s[0],r[0]);for(let f=1;f<=e;f++){if(r[f]=r[f-1].clone(),o[f]=o[f-1].clone(),a.crossVectors(s[f-1],s[f]),a.length()>Number.EPSILON){a.normalize();const m=Math.acos(Qt(s[f-1].dot(s[f]),-1,1));r[f].applyMatrix4(c.makeRotationAxis(a,m))}o[f].crossVectors(s[f],r[f])}if(t===!0){let f=Math.acos(Qt(r[0].dot(r[e]),-1,1));f/=e,s[0].dot(a.crossVectors(r[0],r[e]))>0&&(f=-f);for(let m=1;m<=e;m++)r[m].applyMatrix4(c.makeRotationAxis(s[m],f*m)),o[m].crossVectors(s[m],r[m])}return{tangents:s,normals:r,binormals:o}}clone(){return new this.constructor().copy(this)}copy(e){return this.arcLengthDivisions=e.arcLengthDivisions,this}toJSON(){const e={metadata:{version:4.6,type:"Curve",generator:"Curve.toJSON"}};return e.arcLengthDivisions=this.arcLengthDivisions,e.type=this.type,e}fromJSON(e){return this.arcLengthDivisions=e.arcLengthDivisions,this}}class Fh extends mi{constructor(e=0,t=0,n=1,s=1,r=0,o=Math.PI*2,a=!1,c=0){super(),this.isEllipseCurve=!0,this.type="EllipseCurve",this.aX=e,this.aY=t,this.xRadius=n,this.yRadius=s,this.aStartAngle=r,this.aEndAngle=o,this.aClockwise=a,this.aRotation=c}getPoint(e,t=new re){const n=t,s=Math.PI*2;let r=this.aEndAngle-this.aStartAngle;const o=Math.abs(r)<Number.EPSILON;for(;r<0;)r+=s;for(;r>s;)r-=s;r<Number.EPSILON&&(o?r=0:r=s),this.aClockwise===!0&&!o&&(r===s?r=-s:r=r-s);const a=this.aStartAngle+e*r;let c=this.aX+this.xRadius*Math.cos(a),l=this.aY+this.yRadius*Math.sin(a);if(this.aRotation!==0){const h=Math.cos(this.aRotation),u=Math.sin(this.aRotation),d=c-this.aX,f=l-this.aY;c=d*h-f*u+this.aX,l=d*u+f*h+this.aY}return n.set(c,l)}copy(e){return super.copy(e),this.aX=e.aX,this.aY=e.aY,this.xRadius=e.xRadius,this.yRadius=e.yRadius,this.aStartAngle=e.aStartAngle,this.aEndAngle=e.aEndAngle,this.aClockwise=e.aClockwise,this.aRotation=e.aRotation,this}toJSON(){const e=super.toJSON();return e.aX=this.aX,e.aY=this.aY,e.xRadius=this.xRadius,e.yRadius=this.yRadius,e.aStartAngle=this.aStartAngle,e.aEndAngle=this.aEndAngle,e.aClockwise=this.aClockwise,e.aRotation=this.aRotation,e}fromJSON(e){return super.fromJSON(e),this.aX=e.aX,this.aY=e.aY,this.xRadius=e.xRadius,this.yRadius=e.yRadius,this.aStartAngle=e.aStartAngle,this.aEndAngle=e.aEndAngle,this.aClockwise=e.aClockwise,this.aRotation=e.aRotation,this}}class iM extends Fh{constructor(e,t,n,s,r,o){super(e,t,n,n,s,r,o),this.isArcCurve=!0,this.type="ArcCurve"}}function Bh(){let i=0,e=0,t=0,n=0;function s(r,o,a,c){i=r,e=a,t=-3*r+3*o-2*a-c,n=2*r-2*o+a+c}return{initCatmullRom:function(r,o,a,c,l){s(o,a,l*(a-r),l*(c-o))},initNonuniformCatmullRom:function(r,o,a,c,l,h,u){let d=(o-r)/l-(a-r)/(l+h)+(a-o)/h,f=(a-o)/h-(c-o)/(h+u)+(c-a)/u;d*=h,f*=h,s(o,a,d,f)},calc:function(r){const o=r*r,a=o*r;return i+e*r+t*o+n*a}}}const sa=new v,Gc=new Bh,Vc=new Bh,Wc=new Bh;class Ya extends mi{constructor(e=[],t=!1,n="centripetal",s=.5){super(),this.isCatmullRomCurve3=!0,this.type="CatmullRomCurve3",this.points=e,this.closed=t,this.curveType=n,this.tension=s}getPoint(e,t=new v){const n=t,s=this.points,r=s.length,o=(r-(this.closed?0:1))*e;let a=Math.floor(o),c=o-a;this.closed?a+=a>0?0:(Math.floor(Math.abs(a)/r)+1)*r:c===0&&a===r-1&&(a=r-2,c=1);let l,h;this.closed||a>0?l=s[(a-1)%r]:(sa.subVectors(s[0],s[1]).add(s[0]),l=sa);const u=s[a%r],d=s[(a+1)%r];if(this.closed||a+2<r?h=s[(a+2)%r]:(sa.subVectors(s[r-1],s[r-2]).add(s[r-1]),h=sa),this.curveType==="centripetal"||this.curveType==="chordal"){const f=this.curveType==="chordal"?.5:.25;let m=Math.pow(l.distanceToSquared(u),f),_=Math.pow(u.distanceToSquared(d),f),g=Math.pow(d.distanceToSquared(h),f);_<1e-4&&(_=1),m<1e-4&&(m=_),g<1e-4&&(g=_),Gc.initNonuniformCatmullRom(l.x,u.x,d.x,h.x,m,_,g),Vc.initNonuniformCatmullRom(l.y,u.y,d.y,h.y,m,_,g),Wc.initNonuniformCatmullRom(l.z,u.z,d.z,h.z,m,_,g)}else this.curveType==="catmullrom"&&(Gc.initCatmullRom(l.x,u.x,d.x,h.x,this.tension),Vc.initCatmullRom(l.y,u.y,d.y,h.y,this.tension),Wc.initCatmullRom(l.z,u.z,d.z,h.z,this.tension));return n.set(Gc.calc(c),Vc.calc(c),Wc.calc(c)),n}copy(e){super.copy(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(s.clone())}return this.closed=e.closed,this.curveType=e.curveType,this.tension=e.tension,this}toJSON(){const e=super.toJSON();e.points=[];for(let t=0,n=this.points.length;t<n;t++){const s=this.points[t];e.points.push(s.toArray())}return e.closed=this.closed,e.curveType=this.curveType,e.tension=this.tension,e}fromJSON(e){super.fromJSON(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(new v().fromArray(s))}return this.closed=e.closed,this.curveType=e.curveType,this.tension=e.tension,this}}function Cd(i,e,t,n,s){const r=(n-e)*.5,o=(s-t)*.5,a=i*i,c=i*a;return(2*t-2*n+r+o)*c+(-3*t+3*n-2*r-o)*a+r*i+t}function sM(i,e){const t=1-i;return t*t*e}function rM(i,e){return 2*(1-i)*i*e}function oM(i,e){return i*i*e}function so(i,e,t,n){return sM(i,e)+rM(i,t)+oM(i,n)}function aM(i,e){const t=1-i;return t*t*t*e}function cM(i,e){const t=1-i;return 3*t*t*i*e}function lM(i,e){return 3*(1-i)*i*i*e}function hM(i,e){return i*i*i*e}function ro(i,e,t,n,s){return aM(i,e)+cM(i,t)+lM(i,n)+hM(i,s)}class Jf extends mi{constructor(e=new re,t=new re,n=new re,s=new re){super(),this.isCubicBezierCurve=!0,this.type="CubicBezierCurve",this.v0=e,this.v1=t,this.v2=n,this.v3=s}getPoint(e,t=new re){const n=t,s=this.v0,r=this.v1,o=this.v2,a=this.v3;return n.set(ro(e,s.x,r.x,o.x,a.x),ro(e,s.y,r.y,o.y,a.y)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this.v3.copy(e.v3),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e.v3=this.v3.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this.v3.fromArray(e.v3),this}}class uM extends mi{constructor(e=new v,t=new v,n=new v,s=new v){super(),this.isCubicBezierCurve3=!0,this.type="CubicBezierCurve3",this.v0=e,this.v1=t,this.v2=n,this.v3=s}getPoint(e,t=new v){const n=t,s=this.v0,r=this.v1,o=this.v2,a=this.v3;return n.set(ro(e,s.x,r.x,o.x,a.x),ro(e,s.y,r.y,o.y,a.y),ro(e,s.z,r.z,o.z,a.z)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this.v3.copy(e.v3),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e.v3=this.v3.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this.v3.fromArray(e.v3),this}}class Qf extends mi{constructor(e=new re,t=new re){super(),this.isLineCurve=!0,this.type="LineCurve",this.v1=e,this.v2=t}getPoint(e,t=new re){const n=t;return e===1?n.copy(this.v2):(n.copy(this.v2).sub(this.v1),n.multiplyScalar(e).add(this.v1)),n}getPointAt(e,t){return this.getPoint(e,t)}getTangent(e,t=new re){return t.subVectors(this.v2,this.v1).normalize()}getTangentAt(e,t){return this.getTangent(e,t)}copy(e){return super.copy(e),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class ep extends mi{constructor(e=new v,t=new v){super(),this.isLineCurve3=!0,this.type="LineCurve3",this.v1=e,this.v2=t}getPoint(e,t=new v){const n=t;return e===1?n.copy(this.v2):(n.copy(this.v2).sub(this.v1),n.multiplyScalar(e).add(this.v1)),n}getPointAt(e,t){return this.getPoint(e,t)}getTangent(e,t=new v){return t.subVectors(this.v2,this.v1).normalize()}getTangentAt(e,t){return this.getTangent(e,t)}copy(e){return super.copy(e),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class tp extends mi{constructor(e=new re,t=new re,n=new re){super(),this.isQuadraticBezierCurve=!0,this.type="QuadraticBezierCurve",this.v0=e,this.v1=t,this.v2=n}getPoint(e,t=new re){const n=t,s=this.v0,r=this.v1,o=this.v2;return n.set(so(e,s.x,r.x,o.x),so(e,s.y,r.y,o.y)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class kh extends mi{constructor(e=new v,t=new v,n=new v){super(),this.isQuadraticBezierCurve3=!0,this.type="QuadraticBezierCurve3",this.v0=e,this.v1=t,this.v2=n}getPoint(e,t=new v){const n=t,s=this.v0,r=this.v1,o=this.v2;return n.set(so(e,s.x,r.x,o.x),so(e,s.y,r.y,o.y),so(e,s.z,r.z,o.z)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class np extends mi{constructor(e=[]){super(),this.isSplineCurve=!0,this.type="SplineCurve",this.points=e}getPoint(e,t=new re){const n=t,s=this.points,r=(s.length-1)*e,o=Math.floor(r),a=r-o,c=s[o===0?o:o-1],l=s[o],h=s[o>s.length-2?s.length-1:o+1],u=s[o>s.length-3?s.length-1:o+2];return n.set(Cd(a,c.x,l.x,h.x,u.x),Cd(a,c.y,l.y,h.y,u.y)),n}copy(e){super.copy(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(s.clone())}return this}toJSON(){const e=super.toJSON();e.points=[];for(let t=0,n=this.points.length;t<n;t++){const s=this.points[t];e.points.push(s.toArray())}return e}fromJSON(e){super.fromJSON(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(new re().fromArray(s))}return this}}var Da=Object.freeze({__proto__:null,ArcCurve:iM,CatmullRomCurve3:Ya,CubicBezierCurve:Jf,CubicBezierCurve3:uM,EllipseCurve:Fh,LineCurve:Qf,LineCurve3:ep,QuadraticBezierCurve:tp,QuadraticBezierCurve3:kh,SplineCurve:np});class dM extends mi{constructor(){super(),this.type="CurvePath",this.curves=[],this.autoClose=!1}add(e){this.curves.push(e)}closePath(){const e=this.curves[0].getPoint(0),t=this.curves[this.curves.length-1].getPoint(1);if(!e.equals(t)){const n=e.isVector2===!0?"LineCurve":"LineCurve3";this.curves.push(new Da[n](t,e))}return this}getPoint(e,t){const n=e*this.getLength(),s=this.getCurveLengths();let r=0;for(;r<s.length;){if(s[r]>=n){const o=s[r]-n,a=this.curves[r],c=a.getLength(),l=c===0?0:1-o/c;return a.getPointAt(l,t)}r++}return null}getLength(){const e=this.getCurveLengths();return e[e.length-1]}updateArcLengths(){this.needsUpdate=!0,this.cacheLengths=null,this.getCurveLengths()}getCurveLengths(){if(this.cacheLengths&&this.cacheLengths.length===this.curves.length)return this.cacheLengths;const e=[];let t=0;for(let n=0,s=this.curves.length;n<s;n++)t+=this.curves[n].getLength(),e.push(t);return this.cacheLengths=e,e}getSpacedPoints(e=40){const t=[];for(let n=0;n<=e;n++)t.push(this.getPoint(n/e));return this.autoClose&&t.push(t[0]),t}getPoints(e=12){const t=[];let n;for(let s=0,r=this.curves;s<r.length;s++){const o=r[s],a=o.isEllipseCurve?e*2:o.isLineCurve||o.isLineCurve3?1:o.isSplineCurve?e*o.points.length:e,c=o.getPoints(a);for(let l=0;l<c.length;l++){const h=c[l];n&&n.equals(h)||(t.push(h),n=h)}}return this.autoClose&&t.length>1&&!t[t.length-1].equals(t[0])&&t.push(t[0]),t}copy(e){super.copy(e),this.curves=[];for(let t=0,n=e.curves.length;t<n;t++){const s=e.curves[t];this.curves.push(s.clone())}return this.autoClose=e.autoClose,this}toJSON(){const e=super.toJSON();e.autoClose=this.autoClose,e.curves=[];for(let t=0,n=this.curves.length;t<n;t++){const s=this.curves[t];e.curves.push(s.toJSON())}return e}fromJSON(e){super.fromJSON(e),this.autoClose=e.autoClose,this.curves=[];for(let t=0,n=e.curves.length;t<n;t++){const s=e.curves[t];this.curves.push(new Da[s.type]().fromJSON(s))}return this}}class ah extends dM{constructor(e){super(),this.type="Path",this.currentPoint=new re,e&&this.setFromPoints(e)}setFromPoints(e){this.moveTo(e[0].x,e[0].y);for(let t=1,n=e.length;t<n;t++)this.lineTo(e[t].x,e[t].y);return this}moveTo(e,t){return this.currentPoint.set(e,t),this}lineTo(e,t){const n=new Qf(this.currentPoint.clone(),new re(e,t));return this.curves.push(n),this.currentPoint.set(e,t),this}quadraticCurveTo(e,t,n,s){const r=new tp(this.currentPoint.clone(),new re(e,t),new re(n,s));return this.curves.push(r),this.currentPoint.set(n,s),this}bezierCurveTo(e,t,n,s,r,o){const a=new Jf(this.currentPoint.clone(),new re(e,t),new re(n,s),new re(r,o));return this.curves.push(a),this.currentPoint.set(r,o),this}splineThru(e){const t=[this.currentPoint.clone()].concat(e),n=new np(t);return this.curves.push(n),this.currentPoint.copy(e[e.length-1]),this}arc(e,t,n,s,r,o){const a=this.currentPoint.x,c=this.currentPoint.y;return this.absarc(e+a,t+c,n,s,r,o),this}absarc(e,t,n,s,r,o){return this.absellipse(e,t,n,n,s,r,o),this}ellipse(e,t,n,s,r,o,a,c){const l=this.currentPoint.x,h=this.currentPoint.y;return this.absellipse(e+l,t+h,n,s,r,o,a,c),this}absellipse(e,t,n,s,r,o,a,c){const l=new Fh(e,t,n,s,r,o,a,c);if(this.curves.length>0){const u=l.getPoint(0);u.equals(this.currentPoint)||this.lineTo(u.x,u.y)}this.curves.push(l);const h=l.getPoint(1);return this.currentPoint.copy(h),this}copy(e){return super.copy(e),this.currentPoint.copy(e.currentPoint),this}toJSON(){const e=super.toJSON();return e.currentPoint=this.currentPoint.toArray(),e}fromJSON(e){return super.fromJSON(e),this.currentPoint.fromArray(e.currentPoint),this}}class Ar extends Xt{constructor(e=[new re(0,-.5),new re(.5,0),new re(0,.5)],t=12,n=0,s=Math.PI*2){super(),this.type="LatheGeometry",this.parameters={points:e,segments:t,phiStart:n,phiLength:s},t=Math.floor(t),s=Qt(s,0,Math.PI*2);const r=[],o=[],a=[],c=[],l=[],h=1/t,u=new v,d=new re,f=new v,m=new v,_=new v;let g=0,p=0;for(let y=0;y<=e.length-1;y++)switch(y){case 0:g=e[y+1].x-e[y].x,p=e[y+1].y-e[y].y,f.x=p*1,f.y=-g,f.z=p*0,_.copy(f),f.normalize(),c.push(f.x,f.y,f.z);break;case e.length-1:c.push(_.x,_.y,_.z);break;default:g=e[y+1].x-e[y].x,p=e[y+1].y-e[y].y,f.x=p*1,f.y=-g,f.z=p*0,m.copy(f),f.x+=_.x,f.y+=_.y,f.z+=_.z,f.normalize(),c.push(f.x,f.y,f.z),_.copy(m)}for(let y=0;y<=t;y++){const M=n+y*h*s,x=Math.sin(M),A=Math.cos(M);for(let E=0;E<=e.length-1;E++){u.x=e[E].x*x,u.y=e[E].y,u.z=e[E].x*A,o.push(u.x,u.y,u.z),d.x=y/t,d.y=E/(e.length-1),a.push(d.x,d.y);const P=c[3*E+0]*x,R=c[3*E+1],b=c[3*E+0]*A;l.push(P,R,b)}}for(let y=0;y<t;y++)for(let M=0;M<e.length-1;M++){const x=M+y*e.length,A=x,E=x+e.length,P=x+e.length+1,R=x+1;r.push(A,E,R),r.push(P,R,E)}this.setIndex(r),this.setAttribute("position",new ht(o,3)),this.setAttribute("uv",new ht(a,2)),this.setAttribute("normal",new ht(l,3))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ar(e.points,e.segments,e.phiStart,e.phiLength)}}class zh extends Ar{constructor(e=1,t=1,n=4,s=8){const r=new ah;r.absarc(0,-t/2,e,Math.PI*1.5,0),r.absarc(0,t/2,e,0,Math.PI*.5),super(r.getPoints(n),s),this.type="CapsuleGeometry",this.parameters={radius:e,length:t,capSegments:n,radialSegments:s}}static fromJSON(e){return new zh(e.radius,e.length,e.capSegments,e.radialSegments)}}class Oi extends Xt{constructor(e=1,t=32,n=0,s=Math.PI*2){super(),this.type="CircleGeometry",this.parameters={radius:e,segments:t,thetaStart:n,thetaLength:s},t=Math.max(3,t);const r=[],o=[],a=[],c=[],l=new v,h=new re;o.push(0,0,0),a.push(0,0,1),c.push(.5,.5);for(let u=0,d=3;u<=t;u++,d+=3){const f=n+u/t*s;l.x=e*Math.cos(f),l.y=e*Math.sin(f),o.push(l.x,l.y,l.z),a.push(0,0,1),h.x=(o[d]/e+1)/2,h.y=(o[d+1]/e+1)/2,c.push(h.x,h.y)}for(let u=1;u<=t;u++)r.push(u,u+1,0);this.setIndex(r),this.setAttribute("position",new ht(o,3)),this.setAttribute("normal",new ht(a,3)),this.setAttribute("uv",new ht(c,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Oi(e.radius,e.segments,e.thetaStart,e.thetaLength)}}class tt extends Xt{constructor(e=1,t=1,n=1,s=32,r=1,o=!1,a=0,c=Math.PI*2){super(),this.type="CylinderGeometry",this.parameters={radiusTop:e,radiusBottom:t,height:n,radialSegments:s,heightSegments:r,openEnded:o,thetaStart:a,thetaLength:c};const l=this;s=Math.floor(s),r=Math.floor(r);const h=[],u=[],d=[],f=[];let m=0;const _=[],g=n/2;let p=0;y(),o===!1&&(e>0&&M(!0),t>0&&M(!1)),this.setIndex(h),this.setAttribute("position",new ht(u,3)),this.setAttribute("normal",new ht(d,3)),this.setAttribute("uv",new ht(f,2));function y(){const x=new v,A=new v;let E=0;const P=(t-e)/n;for(let R=0;R<=r;R++){const b=[],w=R/r,L=w*(t-e)+e;for(let B=0;B<=s;B++){const F=B/s,G=F*c+a,Z=Math.sin(G),X=Math.cos(G);A.x=L*Z,A.y=-w*n+g,A.z=L*X,u.push(A.x,A.y,A.z),x.set(Z,P,X).normalize(),d.push(x.x,x.y,x.z),f.push(F,1-w),b.push(m++)}_.push(b)}for(let R=0;R<s;R++)for(let b=0;b<r;b++){const w=_[b][R],L=_[b+1][R],B=_[b+1][R+1],F=_[b][R+1];(e>0||b!==0)&&(h.push(w,L,F),E+=3),(t>0||b!==r-1)&&(h.push(L,B,F),E+=3)}l.addGroup(p,E,0),p+=E}function M(x){const A=m,E=new re,P=new v;let R=0;const b=x===!0?e:t,w=x===!0?1:-1;for(let B=1;B<=s;B++)u.push(0,g*w,0),d.push(0,w,0),f.push(.5,.5),m++;const L=m;for(let B=0;B<=s;B++){const G=B/s*c+a,Z=Math.cos(G),X=Math.sin(G);P.x=b*X,P.y=g*w,P.z=b*Z,u.push(P.x,P.y,P.z),d.push(0,w,0),E.x=Z*.5+.5,E.y=X*.5*w+.5,f.push(E.x,E.y),m++}for(let B=0;B<s;B++){const F=A+B,G=L+B;x===!0?h.push(G,G+1,F):h.push(G+1,G,F),R+=3}l.addGroup(p,R,x===!0?1:2),p+=R}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new tt(e.radiusTop,e.radiusBottom,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class hi extends tt{constructor(e=1,t=1,n=32,s=1,r=!1,o=0,a=Math.PI*2){super(0,e,t,n,s,r,o,a),this.type="ConeGeometry",this.parameters={radius:e,height:t,radialSegments:n,heightSegments:s,openEnded:r,thetaStart:o,thetaLength:a}}static fromJSON(e){return new hi(e.radius,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class Ka extends Xt{constructor(e=[],t=[],n=1,s=0){super(),this.type="PolyhedronGeometry",this.parameters={vertices:e,indices:t,radius:n,detail:s};const r=[],o=[];a(s),l(n),h(),this.setAttribute("position",new ht(r,3)),this.setAttribute("normal",new ht(r.slice(),3)),this.setAttribute("uv",new ht(o,2)),s===0?this.computeVertexNormals():this.normalizeNormals();function a(y){const M=new v,x=new v,A=new v;for(let E=0;E<t.length;E+=3)f(t[E+0],M),f(t[E+1],x),f(t[E+2],A),c(M,x,A,y)}function c(y,M,x,A){const E=A+1,P=[];for(let R=0;R<=E;R++){P[R]=[];const b=y.clone().lerp(x,R/E),w=M.clone().lerp(x,R/E),L=E-R;for(let B=0;B<=L;B++)B===0&&R===E?P[R][B]=b:P[R][B]=b.clone().lerp(w,B/L)}for(let R=0;R<E;R++)for(let b=0;b<2*(E-R)-1;b++){const w=Math.floor(b/2);b%2===0?(d(P[R][w+1]),d(P[R+1][w]),d(P[R][w])):(d(P[R][w+1]),d(P[R+1][w+1]),d(P[R+1][w]))}}function l(y){const M=new v;for(let x=0;x<r.length;x+=3)M.x=r[x+0],M.y=r[x+1],M.z=r[x+2],M.normalize().multiplyScalar(y),r[x+0]=M.x,r[x+1]=M.y,r[x+2]=M.z}function h(){const y=new v;for(let M=0;M<r.length;M+=3){y.x=r[M+0],y.y=r[M+1],y.z=r[M+2];const x=g(y)/2/Math.PI+.5,A=p(y)/Math.PI+.5;o.push(x,1-A)}m(),u()}function u(){for(let y=0;y<o.length;y+=6){const M=o[y+0],x=o[y+2],A=o[y+4],E=Math.max(M,x,A),P=Math.min(M,x,A);E>.9&&P<.1&&(M<.2&&(o[y+0]+=1),x<.2&&(o[y+2]+=1),A<.2&&(o[y+4]+=1))}}function d(y){r.push(y.x,y.y,y.z)}function f(y,M){const x=y*3;M.x=e[x+0],M.y=e[x+1],M.z=e[x+2]}function m(){const y=new v,M=new v,x=new v,A=new v,E=new re,P=new re,R=new re;for(let b=0,w=0;b<r.length;b+=9,w+=6){y.set(r[b+0],r[b+1],r[b+2]),M.set(r[b+3],r[b+4],r[b+5]),x.set(r[b+6],r[b+7],r[b+8]),E.set(o[w+0],o[w+1]),P.set(o[w+2],o[w+3]),R.set(o[w+4],o[w+5]),A.copy(y).add(M).add(x).divideScalar(3);const L=g(A);_(E,w+0,y,L),_(P,w+2,M,L),_(R,w+4,x,L)}}function _(y,M,x,A){A<0&&y.x===1&&(o[M]=y.x-1),x.x===0&&x.z===0&&(o[M]=A/2/Math.PI+.5)}function g(y){return Math.atan2(y.z,-y.x)}function p(y){return Math.atan2(-y.y,Math.sqrt(y.x*y.x+y.z*y.z))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ka(e.vertices,e.indices,e.radius,e.details)}}const ra=new v,oa=new v,Xc=new v,aa=new Wn;class Za extends Xt{constructor(e=null,t=1){if(super(),this.type="EdgesGeometry",this.parameters={geometry:e,thresholdAngle:t},e!==null){const s=Math.pow(10,4),r=Math.cos(ar*t),o=e.getIndex(),a=e.getAttribute("position"),c=o?o.count:a.count,l=[0,0,0],h=["a","b","c"],u=new Array(3),d={},f=[];for(let m=0;m<c;m+=3){o?(l[0]=o.getX(m),l[1]=o.getX(m+1),l[2]=o.getX(m+2)):(l[0]=m,l[1]=m+1,l[2]=m+2);const{a:_,b:g,c:p}=aa;if(_.fromBufferAttribute(a,l[0]),g.fromBufferAttribute(a,l[1]),p.fromBufferAttribute(a,l[2]),aa.getNormal(Xc),u[0]=`${Math.round(_.x*s)},${Math.round(_.y*s)},${Math.round(_.z*s)}`,u[1]=`${Math.round(g.x*s)},${Math.round(g.y*s)},${Math.round(g.z*s)}`,u[2]=`${Math.round(p.x*s)},${Math.round(p.y*s)},${Math.round(p.z*s)}`,!(u[0]===u[1]||u[1]===u[2]||u[2]===u[0]))for(let y=0;y<3;y++){const M=(y+1)%3,x=u[y],A=u[M],E=aa[h[y]],P=aa[h[M]],R=`${x}_${A}`,b=`${A}_${x}`;b in d&&d[b]?(Xc.dot(d[b].normal)<=r&&(f.push(E.x,E.y,E.z),f.push(P.x,P.y,P.z)),d[b]=null):R in d||(d[R]={index0:l[y],index1:l[M],normal:Xc.clone()})}}for(const m in d)if(d[m]){const{index0:_,index1:g}=d[m];ra.fromBufferAttribute(a,_),oa.fromBufferAttribute(a,g),f.push(ra.x,ra.y,ra.z),f.push(oa.x,oa.y,oa.z)}this.setAttribute("position",new ht(f,3))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}}class Ls extends ah{constructor(e){super(e),this.uuid=$n(),this.type="Shape",this.holes=[]}getPointsHoles(e){const t=[];for(let n=0,s=this.holes.length;n<s;n++)t[n]=this.holes[n].getPoints(e);return t}extractPoints(e){return{shape:this.getPoints(e),holes:this.getPointsHoles(e)}}copy(e){super.copy(e),this.holes=[];for(let t=0,n=e.holes.length;t<n;t++){const s=e.holes[t];this.holes.push(s.clone())}return this}toJSON(){const e=super.toJSON();e.uuid=this.uuid,e.holes=[];for(let t=0,n=this.holes.length;t<n;t++){const s=this.holes[t];e.holes.push(s.toJSON())}return e}fromJSON(e){super.fromJSON(e),this.uuid=e.uuid,this.holes=[];for(let t=0,n=e.holes.length;t<n;t++){const s=e.holes[t];this.holes.push(new ah().fromJSON(s))}return this}}const fM={triangulate:function(i,e,t=2){const n=e&&e.length,s=n?e[0]*t:i.length;let r=ip(i,0,s,t,!0);const o=[];if(!r||r.next===r.prev)return o;let a,c,l,h,u,d,f;if(n&&(r=xM(i,e,r,t)),i.length>80*t){a=l=i[0],c=h=i[1];for(let m=t;m<s;m+=t)u=i[m],d=i[m+1],u<a&&(a=u),d<c&&(c=d),u>l&&(l=u),d>h&&(h=d);f=Math.max(l-a,h-c),f=f!==0?32767/f:0}return mo(r,o,t,a,c,f,0),o}};function ip(i,e,t,n,s){let r,o;if(s===CM(i,e,t,n)>0)for(r=e;r<t;r+=n)o=Pd(r,i[r],i[r+1],o);else for(r=t-n;r>=e;r-=n)o=Pd(r,i[r],i[r+1],o);return o&&Ja(o,o.next)&&(_o(o),o=o.next),o}function Cs(i,e){if(!i)return i;e||(e=i);let t=i,n;do if(n=!1,!t.steiner&&(Ja(t,t.next)||Wt(t.prev,t,t.next)===0)){if(_o(t),t=e=t.prev,t===t.next)break;n=!0}else t=t.next;while(n||t!==e);return e}function mo(i,e,t,n,s,r,o){if(!i)return;!o&&r&&bM(i,n,s,r);let a=i,c,l;for(;i.prev!==i.next;){if(c=i.prev,l=i.next,r?mM(i,n,s,r):pM(i)){e.push(c.i/t|0),e.push(i.i/t|0),e.push(l.i/t|0),_o(i),i=l.next,a=l.next;continue}if(i=l,i===a){o?o===1?(i=gM(Cs(i),e,t),mo(i,e,t,n,s,r,2)):o===2&&_M(i,e,t,n,s,r):mo(Cs(i),e,t,n,s,r,1);break}}}function pM(i){const e=i.prev,t=i,n=i.next;if(Wt(e,t,n)>=0)return!1;const s=e.x,r=t.x,o=n.x,a=e.y,c=t.y,l=n.y,h=s<r?s<o?s:o:r<o?r:o,u=a<c?a<l?a:l:c<l?c:l,d=s>r?s>o?s:o:r>o?r:o,f=a>c?a>l?a:l:c>l?c:l;let m=n.next;for(;m!==e;){if(m.x>=h&&m.x<=d&&m.y>=u&&m.y<=f&&nr(s,a,r,c,o,l,m.x,m.y)&&Wt(m.prev,m,m.next)>=0)return!1;m=m.next}return!0}function mM(i,e,t,n){const s=i.prev,r=i,o=i.next;if(Wt(s,r,o)>=0)return!1;const a=s.x,c=r.x,l=o.x,h=s.y,u=r.y,d=o.y,f=a<c?a<l?a:l:c<l?c:l,m=h<u?h<d?h:d:u<d?u:d,_=a>c?a>l?a:l:c>l?c:l,g=h>u?h>d?h:d:u>d?u:d,p=ch(f,m,e,t,n),y=ch(_,g,e,t,n);let M=i.prevZ,x=i.nextZ;for(;M&&M.z>=p&&x&&x.z<=y;){if(M.x>=f&&M.x<=_&&M.y>=m&&M.y<=g&&M!==s&&M!==o&&nr(a,h,c,u,l,d,M.x,M.y)&&Wt(M.prev,M,M.next)>=0||(M=M.prevZ,x.x>=f&&x.x<=_&&x.y>=m&&x.y<=g&&x!==s&&x!==o&&nr(a,h,c,u,l,d,x.x,x.y)&&Wt(x.prev,x,x.next)>=0))return!1;x=x.nextZ}for(;M&&M.z>=p;){if(M.x>=f&&M.x<=_&&M.y>=m&&M.y<=g&&M!==s&&M!==o&&nr(a,h,c,u,l,d,M.x,M.y)&&Wt(M.prev,M,M.next)>=0)return!1;M=M.prevZ}for(;x&&x.z<=y;){if(x.x>=f&&x.x<=_&&x.y>=m&&x.y<=g&&x!==s&&x!==o&&nr(a,h,c,u,l,d,x.x,x.y)&&Wt(x.prev,x,x.next)>=0)return!1;x=x.nextZ}return!0}function gM(i,e,t){let n=i;do{const s=n.prev,r=n.next.next;!Ja(s,r)&&sp(s,n,n.next,r)&&go(s,r)&&go(r,s)&&(e.push(s.i/t|0),e.push(n.i/t|0),e.push(r.i/t|0),_o(n),_o(n.next),n=i=r),n=n.next}while(n!==i);return Cs(n)}function _M(i,e,t,n,s,r){let o=i;do{let a=o.next.next;for(;a!==o.prev;){if(o.i!==a.i&&TM(o,a)){let c=rp(o,a);o=Cs(o,o.next),c=Cs(c,c.next),mo(o,e,t,n,s,r,0),mo(c,e,t,n,s,r,0);return}a=a.next}o=o.next}while(o!==i)}function xM(i,e,t,n){const s=[];let r,o,a,c,l;for(r=0,o=e.length;r<o;r++)a=e[r]*n,c=r<o-1?e[r+1]*n:i.length,l=ip(i,a,c,n,!1),l===l.next&&(l.steiner=!0),s.push(EM(l));for(s.sort(vM),r=0;r<s.length;r++)t=yM(s[r],t);return t}function vM(i,e){return i.x-e.x}function yM(i,e){const t=MM(i,e);if(!t)return e;const n=rp(t,i);return Cs(n,n.next),Cs(t,t.next)}function MM(i,e){let t=e,n=-1/0,s;const r=i.x,o=i.y;do{if(o<=t.y&&o>=t.next.y&&t.next.y!==t.y){const d=t.x+(o-t.y)*(t.next.x-t.x)/(t.next.y-t.y);if(d<=r&&d>n&&(n=d,s=t.x<t.next.x?t:t.next,d===r))return s}t=t.next}while(t!==e);if(!s)return null;const a=s,c=s.x,l=s.y;let h=1/0,u;t=s;do r>=t.x&&t.x>=c&&r!==t.x&&nr(o<l?r:n,o,c,l,o<l?n:r,o,t.x,t.y)&&(u=Math.abs(o-t.y)/(r-t.x),go(t,i)&&(u<h||u===h&&(t.x>s.x||t.x===s.x&&wM(s,t)))&&(s=t,h=u)),t=t.next;while(t!==a);return s}function wM(i,e){return Wt(i.prev,i,e.prev)<0&&Wt(e.next,i,i.next)<0}function bM(i,e,t,n){let s=i;do s.z===0&&(s.z=ch(s.x,s.y,e,t,n)),s.prevZ=s.prev,s.nextZ=s.next,s=s.next;while(s!==i);s.prevZ.nextZ=null,s.prevZ=null,SM(s)}function SM(i){let e,t,n,s,r,o,a,c,l=1;do{for(t=i,i=null,r=null,o=0;t;){for(o++,n=t,a=0,e=0;e<l&&(a++,n=n.nextZ,!!n);e++);for(c=l;a>0||c>0&&n;)a!==0&&(c===0||!n||t.z<=n.z)?(s=t,t=t.nextZ,a--):(s=n,n=n.nextZ,c--),r?r.nextZ=s:i=s,s.prevZ=r,r=s;t=n}r.nextZ=null,l*=2}while(o>1);return i}function ch(i,e,t,n,s){return i=(i-t)*s|0,e=(e-n)*s|0,i=(i|i<<8)&16711935,i=(i|i<<4)&252645135,i=(i|i<<2)&858993459,i=(i|i<<1)&1431655765,e=(e|e<<8)&16711935,e=(e|e<<4)&252645135,e=(e|e<<2)&858993459,e=(e|e<<1)&1431655765,i|e<<1}function EM(i){let e=i,t=i;do(e.x<t.x||e.x===t.x&&e.y<t.y)&&(t=e),e=e.next;while(e!==i);return t}function nr(i,e,t,n,s,r,o,a){return(s-o)*(e-a)>=(i-o)*(r-a)&&(i-o)*(n-a)>=(t-o)*(e-a)&&(t-o)*(r-a)>=(s-o)*(n-a)}function TM(i,e){return i.next.i!==e.i&&i.prev.i!==e.i&&!AM(i,e)&&(go(i,e)&&go(e,i)&&RM(i,e)&&(Wt(i.prev,i,e.prev)||Wt(i,e.prev,e))||Ja(i,e)&&Wt(i.prev,i,i.next)>0&&Wt(e.prev,e,e.next)>0)}function Wt(i,e,t){return(e.y-i.y)*(t.x-e.x)-(e.x-i.x)*(t.y-e.y)}function Ja(i,e){return i.x===e.x&&i.y===e.y}function sp(i,e,t,n){const s=la(Wt(i,e,t)),r=la(Wt(i,e,n)),o=la(Wt(t,n,i)),a=la(Wt(t,n,e));return!!(s!==r&&o!==a||s===0&&ca(i,t,e)||r===0&&ca(i,n,e)||o===0&&ca(t,i,n)||a===0&&ca(t,e,n))}function ca(i,e,t){return e.x<=Math.max(i.x,t.x)&&e.x>=Math.min(i.x,t.x)&&e.y<=Math.max(i.y,t.y)&&e.y>=Math.min(i.y,t.y)}function la(i){return i>0?1:i<0?-1:0}function AM(i,e){let t=i;do{if(t.i!==i.i&&t.next.i!==i.i&&t.i!==e.i&&t.next.i!==e.i&&sp(t,t.next,i,e))return!0;t=t.next}while(t!==i);return!1}function go(i,e){return Wt(i.prev,i,i.next)<0?Wt(i,e,i.next)>=0&&Wt(i,i.prev,e)>=0:Wt(i,e,i.prev)<0||Wt(i,i.next,e)<0}function RM(i,e){let t=i,n=!1;const s=(i.x+e.x)/2,r=(i.y+e.y)/2;do t.y>r!=t.next.y>r&&t.next.y!==t.y&&s<(t.next.x-t.x)*(r-t.y)/(t.next.y-t.y)+t.x&&(n=!n),t=t.next;while(t!==i);return n}function rp(i,e){const t=new lh(i.i,i.x,i.y),n=new lh(e.i,e.x,e.y),s=i.next,r=e.prev;return i.next=e,e.prev=i,t.next=s,s.prev=t,n.next=t,t.prev=n,r.next=n,n.prev=r,n}function Pd(i,e,t,n){const s=new lh(i,e,t);return n?(s.next=n.next,s.prev=n,n.next.prev=s,n.next=s):(s.prev=s,s.next=s),s}function _o(i){i.next.prev=i.prev,i.prev.next=i.next,i.prevZ&&(i.prevZ.nextZ=i.nextZ),i.nextZ&&(i.nextZ.prevZ=i.prevZ)}function lh(i,e,t){this.i=i,this.x=e,this.y=t,this.prev=null,this.next=null,this.z=0,this.prevZ=null,this.nextZ=null,this.steiner=!1}function CM(i,e,t,n){let s=0;for(let r=e,o=t-n;r<t;r+=n)s+=(i[o]-i[r])*(i[r+1]+i[o+1]),o=r;return s}class ss{static area(e){const t=e.length;let n=0;for(let s=t-1,r=0;r<t;s=r++)n+=e[s].x*e[r].y-e[r].x*e[s].y;return n*.5}static isClockWise(e){return ss.area(e)<0}static triangulateShape(e,t){const n=[],s=[],r=[];Ld(e),Id(n,e);let o=e.length;t.forEach(Ld);for(let c=0;c<t.length;c++)s.push(o),o+=t[c].length,Id(n,t[c]);const a=fM.triangulate(n,s);for(let c=0;c<a.length;c+=3)r.push(a.slice(c,c+3));return r}}function Ld(i){const e=i.length;e>2&&i[e-1].equals(i[0])&&i.pop()}function Id(i,e){for(let t=0;t<e.length;t++)i.push(e[t].x),i.push(e[t].y)}class bo extends Xt{constructor(e=new Ls([new re(.5,.5),new re(-.5,.5),new re(-.5,-.5),new re(.5,-.5)]),t={}){super(),this.type="ExtrudeGeometry",this.parameters={shapes:e,options:t},e=Array.isArray(e)?e:[e];const n=this,s=[],r=[];for(let a=0,c=e.length;a<c;a++){const l=e[a];o(l)}this.setAttribute("position",new ht(s,3)),this.setAttribute("uv",new ht(r,2)),this.computeVertexNormals();function o(a){const c=[],l=t.curveSegments!==void 0?t.curveSegments:12,h=t.steps!==void 0?t.steps:1,u=t.depth!==void 0?t.depth:1;let d=t.bevelEnabled!==void 0?t.bevelEnabled:!0,f=t.bevelThickness!==void 0?t.bevelThickness:.2,m=t.bevelSize!==void 0?t.bevelSize:f-.1,_=t.bevelOffset!==void 0?t.bevelOffset:0,g=t.bevelSegments!==void 0?t.bevelSegments:3;const p=t.extrudePath,y=t.UVGenerator!==void 0?t.UVGenerator:PM;let M,x=!1,A,E,P,R;p&&(M=p.getSpacedPoints(h),x=!0,d=!1,A=p.computeFrenetFrames(h,!1),E=new v,P=new v,R=new v),d||(g=0,f=0,m=0,_=0);const b=a.extractPoints(l);let w=b.shape;const L=b.holes;if(!ss.isClockWise(w)){w=w.reverse();for(let ee=0,he=L.length;ee<he;ee++){const I=L[ee];ss.isClockWise(I)&&(L[ee]=I.reverse())}}const F=ss.triangulateShape(w,L),G=w;for(let ee=0,he=L.length;ee<he;ee++){const I=L[ee];w=w.concat(I)}function Z(ee,he,I){return he||console.error("THREE.ExtrudeGeometry: vec does not exist"),ee.clone().addScaledVector(he,I)}const X=w.length,$=F.length;function W(ee,he,I){let ze,ae,Le;const _e=ee.x-he.x,qe=ee.y-he.y,Ce=I.x-ee.x,C=I.y-ee.y,S=_e*_e+qe*qe,k=_e*C-qe*Ce;if(Math.abs(k)>Number.EPSILON){const j=Math.sqrt(S),te=Math.sqrt(Ce*Ce+C*C),Y=he.x-qe/j,Oe=he.y+_e/j,Me=I.x-C/te,Pe=I.y+Ce/te,ft=((Me-Y)*C-(Pe-Oe)*Ce)/(_e*C-qe*Ce);ze=Y+_e*ft-ee.x,ae=Oe+qe*ft-ee.y;const le=ze*ze+ae*ae;if(le<=2)return new re(ze,ae);Le=Math.sqrt(le/2)}else{let j=!1;_e>Number.EPSILON?Ce>Number.EPSILON&&(j=!0):_e<-Number.EPSILON?Ce<-Number.EPSILON&&(j=!0):Math.sign(qe)===Math.sign(C)&&(j=!0),j?(ze=-qe,ae=_e,Le=Math.sqrt(S)):(ze=_e,ae=qe,Le=Math.sqrt(S/2))}return new re(ze/Le,ae/Le)}const ce=[];for(let ee=0,he=G.length,I=he-1,ze=ee+1;ee<he;ee++,I++,ze++)I===he&&(I=0),ze===he&&(ze=0),ce[ee]=W(G[ee],G[I],G[ze]);const ve=[];let Re,it=ce.concat();for(let ee=0,he=L.length;ee<he;ee++){const I=L[ee];Re=[];for(let ze=0,ae=I.length,Le=ae-1,_e=ze+1;ze<ae;ze++,Le++,_e++)Le===ae&&(Le=0),_e===ae&&(_e=0),Re[ze]=W(I[ze],I[Le],I[_e]);ve.push(Re),it=it.concat(Re)}for(let ee=0;ee<g;ee++){const he=ee/g,I=f*Math.cos(he*Math.PI/2),ze=m*Math.sin(he*Math.PI/2)+_;for(let ae=0,Le=G.length;ae<Le;ae++){const _e=Z(G[ae],ce[ae],ze);me(_e.x,_e.y,-I)}for(let ae=0,Le=L.length;ae<Le;ae++){const _e=L[ae];Re=ve[ae];for(let qe=0,Ce=_e.length;qe<Ce;qe++){const C=Z(_e[qe],Re[qe],ze);me(C.x,C.y,-I)}}}const St=m+_;for(let ee=0;ee<X;ee++){const he=d?Z(w[ee],it[ee],St):w[ee];x?(P.copy(A.normals[0]).multiplyScalar(he.x),E.copy(A.binormals[0]).multiplyScalar(he.y),R.copy(M[0]).add(P).add(E),me(R.x,R.y,R.z)):me(he.x,he.y,0)}for(let ee=1;ee<=h;ee++)for(let he=0;he<X;he++){const I=d?Z(w[he],it[he],St):w[he];x?(P.copy(A.normals[ee]).multiplyScalar(I.x),E.copy(A.binormals[ee]).multiplyScalar(I.y),R.copy(M[ee]).add(P).add(E),me(R.x,R.y,R.z)):me(I.x,I.y,u/h*ee)}for(let ee=g-1;ee>=0;ee--){const he=ee/g,I=f*Math.cos(he*Math.PI/2),ze=m*Math.sin(he*Math.PI/2)+_;for(let ae=0,Le=G.length;ae<Le;ae++){const _e=Z(G[ae],ce[ae],ze);me(_e.x,_e.y,u+I)}for(let ae=0,Le=L.length;ae<Le;ae++){const _e=L[ae];Re=ve[ae];for(let qe=0,Ce=_e.length;qe<Ce;qe++){const C=Z(_e[qe],Re[qe],ze);x?me(C.x,C.y+M[h-1].y,M[h-1].x+I):me(C.x,C.y,u+I)}}}K(),ue();function K(){const ee=s.length/3;if(d){let he=0,I=X*he;for(let ze=0;ze<$;ze++){const ae=F[ze];We(ae[2]+I,ae[1]+I,ae[0]+I)}he=h+g*2,I=X*he;for(let ze=0;ze<$;ze++){const ae=F[ze];We(ae[0]+I,ae[1]+I,ae[2]+I)}}else{for(let he=0;he<$;he++){const I=F[he];We(I[2],I[1],I[0])}for(let he=0;he<$;he++){const I=F[he];We(I[0]+X*h,I[1]+X*h,I[2]+X*h)}}n.addGroup(ee,s.length/3-ee,0)}function ue(){const ee=s.length/3;let he=0;Ne(G,he),he+=G.length;for(let I=0,ze=L.length;I<ze;I++){const ae=L[I];Ne(ae,he),he+=ae.length}n.addGroup(ee,s.length/3-ee,1)}function Ne(ee,he){let I=ee.length;for(;--I>=0;){const ze=I;let ae=I-1;ae<0&&(ae=ee.length-1);for(let Le=0,_e=h+g*2;Le<_e;Le++){const qe=X*Le,Ce=X*(Le+1),C=he+ze+qe,S=he+ae+qe,k=he+ae+Ce,j=he+ze+Ce;Qe(C,S,k,j)}}}function me(ee,he,I){c.push(ee),c.push(he),c.push(I)}function We(ee,he,I){je(ee),je(he),je(I);const ze=s.length/3,ae=y.generateTopUV(n,s,ze-3,ze-2,ze-1);_t(ae[0]),_t(ae[1]),_t(ae[2])}function Qe(ee,he,I,ze){je(ee),je(he),je(ze),je(he),je(I),je(ze);const ae=s.length/3,Le=y.generateSideWallUV(n,s,ae-6,ae-3,ae-2,ae-1);_t(Le[0]),_t(Le[1]),_t(Le[3]),_t(Le[1]),_t(Le[2]),_t(Le[3])}function je(ee){s.push(c[ee*3+0]),s.push(c[ee*3+1]),s.push(c[ee*3+2])}function _t(ee){r.push(ee.x),r.push(ee.y)}}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}toJSON(){const e=super.toJSON(),t=this.parameters.shapes,n=this.parameters.options;return LM(t,n,e)}static fromJSON(e,t){const n=[];for(let r=0,o=e.shapes.length;r<o;r++){const a=t[e.shapes[r]];n.push(a)}const s=e.options.extrudePath;return s!==void 0&&(e.options.extrudePath=new Da[s.type]().fromJSON(s)),new bo(n,e.options)}}const PM={generateTopUV:function(i,e,t,n,s){const r=e[t*3],o=e[t*3+1],a=e[n*3],c=e[n*3+1],l=e[s*3],h=e[s*3+1];return[new re(r,o),new re(a,c),new re(l,h)]},generateSideWallUV:function(i,e,t,n,s,r){const o=e[t*3],a=e[t*3+1],c=e[t*3+2],l=e[n*3],h=e[n*3+1],u=e[n*3+2],d=e[s*3],f=e[s*3+1],m=e[s*3+2],_=e[r*3],g=e[r*3+1],p=e[r*3+2];return Math.abs(a-h)<Math.abs(o-l)?[new re(o,1-c),new re(l,1-u),new re(d,1-m),new re(_,1-p)]:[new re(a,1-c),new re(h,1-u),new re(f,1-m),new re(g,1-p)]}};function LM(i,e,t){if(t.shapes=[],Array.isArray(i))for(let n=0,s=i.length;n<s;n++){const r=i[n];t.shapes.push(r.uuid)}else t.shapes.push(i.uuid);return t.options=Object.assign({},e),e.extrudePath!==void 0&&(t.options.extrudePath=e.extrudePath.toJSON()),t}class Qa extends Ka{constructor(e=1,t=0){const n=(1+Math.sqrt(5))/2,s=[-1,n,0,1,n,0,-1,-n,0,1,-n,0,0,-1,n,0,1,n,0,-1,-n,0,1,-n,n,0,-1,n,0,1,-n,0,-1,-n,0,1],r=[0,11,5,0,5,1,0,1,7,0,7,10,0,10,11,1,5,9,5,11,4,11,10,2,10,7,6,7,1,8,3,9,4,3,4,2,3,2,6,3,6,8,3,8,9,4,9,5,2,4,11,6,2,10,8,6,7,9,8,1];super(s,r,e,t),this.type="IcosahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new Qa(e.radius,e.detail)}}class Hh extends Ka{constructor(e=1,t=0){const n=[1,0,0,-1,0,0,0,1,0,0,-1,0,0,0,1,0,0,-1],s=[0,2,4,0,4,3,0,3,5,0,5,2,1,2,5,1,5,3,1,3,4,1,4,2];super(n,s,e,t),this.type="OctahedronGeometry",this.parameters={radius:e,detail:t}}static fromJSON(e){return new Hh(e.radius,e.detail)}}class Gh extends Xt{constructor(e=.5,t=1,n=32,s=1,r=0,o=Math.PI*2){super(),this.type="RingGeometry",this.parameters={innerRadius:e,outerRadius:t,thetaSegments:n,phiSegments:s,thetaStart:r,thetaLength:o},n=Math.max(3,n),s=Math.max(1,s);const a=[],c=[],l=[],h=[];let u=e;const d=(t-e)/s,f=new v,m=new re;for(let _=0;_<=s;_++){for(let g=0;g<=n;g++){const p=r+g/n*o;f.x=u*Math.cos(p),f.y=u*Math.sin(p),c.push(f.x,f.y,f.z),l.push(0,0,1),m.x=(f.x/t+1)/2,m.y=(f.y/t+1)/2,h.push(m.x,m.y)}u+=d}for(let _=0;_<s;_++){const g=_*(n+1);for(let p=0;p<n;p++){const y=p+g,M=y,x=y+n+1,A=y+n+2,E=y+1;a.push(M,x,E),a.push(x,A,E)}}this.setIndex(a),this.setAttribute("position",new ht(c,3)),this.setAttribute("normal",new ht(l,3)),this.setAttribute("uv",new ht(h,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Gh(e.innerRadius,e.outerRadius,e.thetaSegments,e.phiSegments,e.thetaStart,e.thetaLength)}}class ec extends Xt{constructor(e=new Ls([new re(0,.5),new re(-.5,-.5),new re(.5,-.5)]),t=12){super(),this.type="ShapeGeometry",this.parameters={shapes:e,curveSegments:t};const n=[],s=[],r=[],o=[];let a=0,c=0;if(Array.isArray(e)===!1)l(e);else for(let h=0;h<e.length;h++)l(e[h]),this.addGroup(a,c,h),a+=c,c=0;this.setIndex(n),this.setAttribute("position",new ht(s,3)),this.setAttribute("normal",new ht(r,3)),this.setAttribute("uv",new ht(o,2));function l(h){const u=s.length/3,d=h.extractPoints(t);let f=d.shape;const m=d.holes;ss.isClockWise(f)===!1&&(f=f.reverse());for(let g=0,p=m.length;g<p;g++){const y=m[g];ss.isClockWise(y)===!0&&(m[g]=y.reverse())}const _=ss.triangulateShape(f,m);for(let g=0,p=m.length;g<p;g++){const y=m[g];f=f.concat(y)}for(let g=0,p=f.length;g<p;g++){const y=f[g];s.push(y.x,y.y,0),r.push(0,0,1),o.push(y.x,y.y)}for(let g=0,p=_.length;g<p;g++){const y=_[g],M=y[0]+u,x=y[1]+u,A=y[2]+u;n.push(M,x,A),c+=3}}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}toJSON(){const e=super.toJSON(),t=this.parameters.shapes;return IM(t,e)}static fromJSON(e,t){const n=[];for(let s=0,r=e.shapes.length;s<r;s++){const o=t[e.shapes[s]];n.push(o)}return new ec(n,e.curveSegments)}}function IM(i,e){if(e.shapes=[],Array.isArray(i))for(let t=0,n=i.length;t<n;t++){const s=i[t];e.shapes.push(s.uuid)}else e.shapes.push(i.uuid);return e}class En extends Xt{constructor(e=1,t=32,n=16,s=0,r=Math.PI*2,o=0,a=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:n,phiStart:s,phiLength:r,thetaStart:o,thetaLength:a},t=Math.max(3,Math.floor(t)),n=Math.max(2,Math.floor(n));const c=Math.min(o+a,Math.PI);let l=0;const h=[],u=new v,d=new v,f=[],m=[],_=[],g=[];for(let p=0;p<=n;p++){const y=[],M=p/n;let x=0;p===0&&o===0?x=.5/t:p===n&&c===Math.PI&&(x=-.5/t);for(let A=0;A<=t;A++){const E=A/t;u.x=-e*Math.cos(s+E*r)*Math.sin(o+M*a),u.y=e*Math.cos(o+M*a),u.z=e*Math.sin(s+E*r)*Math.sin(o+M*a),m.push(u.x,u.y,u.z),d.copy(u).normalize(),_.push(d.x,d.y,d.z),g.push(E+x,1-M),y.push(l++)}h.push(y)}for(let p=0;p<n;p++)for(let y=0;y<t;y++){const M=h[p][y+1],x=h[p][y],A=h[p+1][y],E=h[p+1][y+1];(p!==0||o>0)&&f.push(M,x,E),(p!==n-1||c<Math.PI)&&f.push(x,A,E)}this.setIndex(f),this.setAttribute("position",new ht(m,3)),this.setAttribute("normal",new ht(_,3)),this.setAttribute("uv",new ht(g,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new En(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}class jn extends Xt{constructor(e=1,t=.4,n=12,s=48,r=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:e,tube:t,radialSegments:n,tubularSegments:s,arc:r},n=Math.floor(n),s=Math.floor(s);const o=[],a=[],c=[],l=[],h=new v,u=new v,d=new v;for(let f=0;f<=n;f++)for(let m=0;m<=s;m++){const _=m/s*r,g=f/n*Math.PI*2;u.x=(e+t*Math.cos(g))*Math.cos(_),u.y=(e+t*Math.cos(g))*Math.sin(_),u.z=t*Math.sin(g),a.push(u.x,u.y,u.z),h.x=e*Math.cos(_),h.y=e*Math.sin(_),d.subVectors(u,h).normalize(),c.push(d.x,d.y,d.z),l.push(m/s),l.push(f/n)}for(let f=1;f<=n;f++)for(let m=1;m<=s;m++){const _=(s+1)*f+m-1,g=(s+1)*(f-1)+m-1,p=(s+1)*(f-1)+m,y=(s+1)*f+m;o.push(_,g,y),o.push(g,p,y)}this.setIndex(o),this.setAttribute("position",new ht(a,3)),this.setAttribute("normal",new ht(c,3)),this.setAttribute("uv",new ht(l,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new jn(e.radius,e.tube,e.radialSegments,e.tubularSegments,e.arc)}}class vr extends Xt{constructor(e=new kh(new v(-1,-1,0),new v(-1,1,0),new v(1,1,0)),t=64,n=1,s=8,r=!1){super(),this.type="TubeGeometry",this.parameters={path:e,tubularSegments:t,radius:n,radialSegments:s,closed:r};const o=e.computeFrenetFrames(t,r);this.tangents=o.tangents,this.normals=o.normals,this.binormals=o.binormals;const a=new v,c=new v,l=new re;let h=new v;const u=[],d=[],f=[],m=[];_(),this.setIndex(m),this.setAttribute("position",new ht(u,3)),this.setAttribute("normal",new ht(d,3)),this.setAttribute("uv",new ht(f,2));function _(){for(let M=0;M<t;M++)g(M);g(r===!1?t:0),y(),p()}function g(M){h=e.getPointAt(M/t,h);const x=o.normals[M],A=o.binormals[M];for(let E=0;E<=s;E++){const P=E/s*Math.PI*2,R=Math.sin(P),b=-Math.cos(P);c.x=b*x.x+R*A.x,c.y=b*x.y+R*A.y,c.z=b*x.z+R*A.z,c.normalize(),d.push(c.x,c.y,c.z),a.x=h.x+n*c.x,a.y=h.y+n*c.y,a.z=h.z+n*c.z,u.push(a.x,a.y,a.z)}}function p(){for(let M=1;M<=t;M++)for(let x=1;x<=s;x++){const A=(s+1)*(M-1)+(x-1),E=(s+1)*M+(x-1),P=(s+1)*M+x,R=(s+1)*(M-1)+x;m.push(A,E,R),m.push(E,P,R)}}function y(){for(let M=0;M<=t;M++)for(let x=0;x<=s;x++)l.x=M/t,l.y=x/s,f.push(l.x,l.y)}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}toJSON(){const e=super.toJSON();return e.path=this.parameters.path.toJSON(),e}static fromJSON(e){return new vr(new Da[e.path.type]().fromJSON(e.path),e.tubularSegments,e.radius,e.radialSegments,e.closed)}}class Vh extends ui{static get type(){return"MeshStandardMaterial"}constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.color=new Ve(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new Ve(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=If,this.normalScale=new re(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new cn,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class gi extends Vh{static get type(){return"MeshPhysicalMaterial"}constructor(e){super(),this.isMeshPhysicalMaterial=!0,this.defines={STANDARD:"",PHYSICAL:""},this.anisotropyRotation=0,this.anisotropyMap=null,this.clearcoatMap=null,this.clearcoatRoughness=0,this.clearcoatRoughnessMap=null,this.clearcoatNormalScale=new re(1,1),this.clearcoatNormalMap=null,this.ior=1.5,Object.defineProperty(this,"reflectivity",{get:function(){return Qt(2.5*(this.ior-1)/(this.ior+1),0,1)},set:function(t){this.ior=(1+.4*t)/(1-.4*t)}}),this.iridescenceMap=null,this.iridescenceIOR=1.3,this.iridescenceThicknessRange=[100,400],this.iridescenceThicknessMap=null,this.sheenColor=new Ve(0),this.sheenColorMap=null,this.sheenRoughness=1,this.sheenRoughnessMap=null,this.transmissionMap=null,this.thickness=0,this.thicknessMap=null,this.attenuationDistance=1/0,this.attenuationColor=new Ve(1,1,1),this.specularIntensity=1,this.specularIntensityMap=null,this.specularColor=new Ve(1,1,1),this.specularColorMap=null,this._anisotropy=0,this._clearcoat=0,this._dispersion=0,this._iridescence=0,this._sheen=0,this._transmission=0,this.setValues(e)}get anisotropy(){return this._anisotropy}set anisotropy(e){this._anisotropy>0!=e>0&&this.version++,this._anisotropy=e}get clearcoat(){return this._clearcoat}set clearcoat(e){this._clearcoat>0!=e>0&&this.version++,this._clearcoat=e}get iridescence(){return this._iridescence}set iridescence(e){this._iridescence>0!=e>0&&this.version++,this._iridescence=e}get dispersion(){return this._dispersion}set dispersion(e){this._dispersion>0!=e>0&&this.version++,this._dispersion=e}get sheen(){return this._sheen}set sheen(e){this._sheen>0!=e>0&&this.version++,this._sheen=e}get transmission(){return this._transmission}set transmission(e){this._transmission>0!=e>0&&this.version++,this._transmission=e}copy(e){return super.copy(e),this.defines={STANDARD:"",PHYSICAL:""},this.anisotropy=e.anisotropy,this.anisotropyRotation=e.anisotropyRotation,this.anisotropyMap=e.anisotropyMap,this.clearcoat=e.clearcoat,this.clearcoatMap=e.clearcoatMap,this.clearcoatRoughness=e.clearcoatRoughness,this.clearcoatRoughnessMap=e.clearcoatRoughnessMap,this.clearcoatNormalMap=e.clearcoatNormalMap,this.clearcoatNormalScale.copy(e.clearcoatNormalScale),this.dispersion=e.dispersion,this.ior=e.ior,this.iridescence=e.iridescence,this.iridescenceMap=e.iridescenceMap,this.iridescenceIOR=e.iridescenceIOR,this.iridescenceThicknessRange=[...e.iridescenceThicknessRange],this.iridescenceThicknessMap=e.iridescenceThicknessMap,this.sheen=e.sheen,this.sheenColor.copy(e.sheenColor),this.sheenColorMap=e.sheenColorMap,this.sheenRoughness=e.sheenRoughness,this.sheenRoughnessMap=e.sheenRoughnessMap,this.transmission=e.transmission,this.transmissionMap=e.transmissionMap,this.thickness=e.thickness,this.thicknessMap=e.thicknessMap,this.attenuationDistance=e.attenuationDistance,this.attenuationColor.copy(e.attenuationColor),this.specularIntensity=e.specularIntensity,this.specularIntensityMap=e.specularIntensityMap,this.specularColor.copy(e.specularColor),this.specularColorMap=e.specularColorMap,this}}function ha(i,e,t){return!i||!t&&i.constructor===e?i:typeof e.BYTES_PER_ELEMENT=="number"?new e(i):Array.prototype.slice.call(i)}function DM(i){return ArrayBuffer.isView(i)&&!(i instanceof DataView)}function NM(i){function e(s,r){return i[s]-i[r]}const t=i.length,n=new Array(t);for(let s=0;s!==t;++s)n[s]=s;return n.sort(e),n}function Dd(i,e,t){const n=i.length,s=new i.constructor(n);for(let r=0,o=0;o!==n;++r){const a=t[r]*e;for(let c=0;c!==e;++c)s[o++]=i[a+c]}return s}function op(i,e,t,n){let s=1,r=i[0];for(;r!==void 0&&r[n]===void 0;)r=i[s++];if(r===void 0)return;let o=r[n];if(o!==void 0)if(Array.isArray(o))do o=r[n],o!==void 0&&(e.push(r.time),t.push.apply(t,o)),r=i[s++];while(r!==void 0);else if(o.toArray!==void 0)do o=r[n],o!==void 0&&(e.push(r.time),o.toArray(t,t.length)),r=i[s++];while(r!==void 0);else do o=r[n],o!==void 0&&(e.push(r.time),t.push(o)),r=i[s++];while(r!==void 0)}class So{constructor(e,t,n,s){this.parameterPositions=e,this._cachedIndex=0,this.resultBuffer=s!==void 0?s:new t.constructor(n),this.sampleValues=t,this.valueSize=n,this.settings=null,this.DefaultSettings_={}}evaluate(e){const t=this.parameterPositions;let n=this._cachedIndex,s=t[n],r=t[n-1];n:{e:{let o;t:{i:if(!(e<s)){for(let a=n+2;;){if(s===void 0){if(e<r)break i;return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}if(n===a)break;if(r=s,s=t[++n],e<s)break e}o=t.length;break t}if(!(e>=r)){const a=t[1];e<a&&(n=2,r=a);for(let c=n-2;;){if(r===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(n===c)break;if(s=r,r=t[--n-1],e>=r)break e}o=n,n=0;break t}break n}for(;n<o;){const a=n+o>>>1;e<t[a]?o=a:n=a+1}if(s=t[n],r=t[n-1],r===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(s===void 0)return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}this._cachedIndex=n,this.intervalChanged_(n,r,s)}return this.interpolate_(n,r,e,s)}getSettings_(){return this.settings||this.DefaultSettings_}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,s=this.valueSize,r=e*s;for(let o=0;o!==s;++o)t[o]=n[r+o];return t}interpolate_(){throw new Error("call to abstract method")}intervalChanged_(){}}class UM extends So{constructor(e,t,n,s){super(e,t,n,s),this._weightPrev=-0,this._offsetPrev=-0,this._weightNext=-0,this._offsetNext=-0,this.DefaultSettings_={endingStart:_u,endingEnd:_u}}intervalChanged_(e,t,n){const s=this.parameterPositions;let r=e-2,o=e+1,a=s[r],c=s[o];if(a===void 0)switch(this.getSettings_().endingStart){case xu:r=e,a=2*t-n;break;case vu:r=s.length-2,a=t+s[r]-s[r+1];break;default:r=e,a=n}if(c===void 0)switch(this.getSettings_().endingEnd){case xu:o=e,c=2*n-t;break;case vu:o=1,c=n+s[1]-s[0];break;default:o=e-1,c=t}const l=(n-t)*.5,h=this.valueSize;this._weightPrev=l/(t-a),this._weightNext=l/(c-n),this._offsetPrev=r*h,this._offsetNext=o*h}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=e*a,l=c-a,h=this._offsetPrev,u=this._offsetNext,d=this._weightPrev,f=this._weightNext,m=(n-t)/(s-t),_=m*m,g=_*m,p=-d*g+2*d*_-d*m,y=(1+d)*g+(-1.5-2*d)*_+(-.5+d)*m+1,M=(-1-f)*g+(1.5+f)*_+.5*m,x=f*g-f*_;for(let A=0;A!==a;++A)r[A]=p*o[h+A]+y*o[l+A]+M*o[c+A]+x*o[u+A];return r}}class OM extends So{constructor(e,t,n,s){super(e,t,n,s)}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=e*a,l=c-a,h=(n-t)/(s-t),u=1-h;for(let d=0;d!==a;++d)r[d]=o[l+d]*u+o[c+d]*h;return r}}class FM extends So{constructor(e,t,n,s){super(e,t,n,s)}interpolate_(e){return this.copySampleValue_(e-1)}}class _i{constructor(e,t,n,s){if(e===void 0)throw new Error("THREE.KeyframeTrack: track name is undefined");if(t===void 0||t.length===0)throw new Error("THREE.KeyframeTrack: no keyframes in track named "+e);this.name=e,this.times=ha(t,this.TimeBufferType),this.values=ha(n,this.ValueBufferType),this.setInterpolation(s||this.DefaultInterpolation)}static toJSON(e){const t=e.constructor;let n;if(t.toJSON!==this.toJSON)n=t.toJSON(e);else{n={name:e.name,times:ha(e.times,Array),values:ha(e.values,Array)};const s=e.getInterpolation();s!==e.DefaultInterpolation&&(n.interpolation=s)}return n.type=e.ValueTypeName,n}InterpolantFactoryMethodDiscrete(e){return new FM(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodLinear(e){return new OM(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodSmooth(e){return new UM(this.times,this.values,this.getValueSize(),e)}setInterpolation(e){let t;switch(e){case uo:t=this.InterpolantFactoryMethodDiscrete;break;case fo:t=this.InterpolantFactoryMethodLinear;break;case uc:t=this.InterpolantFactoryMethodSmooth;break}if(t===void 0){const n="unsupported interpolation for "+this.ValueTypeName+" keyframe track named "+this.name;if(this.createInterpolant===void 0)if(e!==this.DefaultInterpolation)this.setInterpolation(this.DefaultInterpolation);else throw new Error(n);return console.warn("THREE.KeyframeTrack:",n),this}return this.createInterpolant=t,this}getInterpolation(){switch(this.createInterpolant){case this.InterpolantFactoryMethodDiscrete:return uo;case this.InterpolantFactoryMethodLinear:return fo;case this.InterpolantFactoryMethodSmooth:return uc}}getValueSize(){return this.values.length/this.times.length}shift(e){if(e!==0){const t=this.times;for(let n=0,s=t.length;n!==s;++n)t[n]+=e}return this}scale(e){if(e!==1){const t=this.times;for(let n=0,s=t.length;n!==s;++n)t[n]*=e}return this}trim(e,t){const n=this.times,s=n.length;let r=0,o=s-1;for(;r!==s&&n[r]<e;)++r;for(;o!==-1&&n[o]>t;)--o;if(++o,r!==0||o!==s){r>=o&&(o=Math.max(o,1),r=o-1);const a=this.getValueSize();this.times=n.slice(r,o),this.values=this.values.slice(r*a,o*a)}return this}validate(){let e=!0;const t=this.getValueSize();t-Math.floor(t)!==0&&(console.error("THREE.KeyframeTrack: Invalid value size in track.",this),e=!1);const n=this.times,s=this.values,r=n.length;r===0&&(console.error("THREE.KeyframeTrack: Track is empty.",this),e=!1);let o=null;for(let a=0;a!==r;a++){const c=n[a];if(typeof c=="number"&&isNaN(c)){console.error("THREE.KeyframeTrack: Time is not a valid number.",this,a,c),e=!1;break}if(o!==null&&o>c){console.error("THREE.KeyframeTrack: Out of order keys.",this,a,c,o),e=!1;break}o=c}if(s!==void 0&&DM(s))for(let a=0,c=s.length;a!==c;++a){const l=s[a];if(isNaN(l)){console.error("THREE.KeyframeTrack: Value is not a valid number.",this,a,l),e=!1;break}}return e}optimize(){const e=this.times.slice(),t=this.values.slice(),n=this.getValueSize(),s=this.getInterpolation()===uc,r=e.length-1;let o=1;for(let a=1;a<r;++a){let c=!1;const l=e[a],h=e[a+1];if(l!==h&&(a!==1||l!==e[0]))if(s)c=!0;else{const u=a*n,d=u-n,f=u+n;for(let m=0;m!==n;++m){const _=t[u+m];if(_!==t[d+m]||_!==t[f+m]){c=!0;break}}}if(c){if(a!==o){e[o]=e[a];const u=a*n,d=o*n;for(let f=0;f!==n;++f)t[d+f]=t[u+f]}++o}}if(r>0){e[o]=e[r];for(let a=r*n,c=o*n,l=0;l!==n;++l)t[c+l]=t[a+l];++o}return o!==e.length?(this.times=e.slice(0,o),this.values=t.slice(0,o*n)):(this.times=e,this.values=t),this}clone(){const e=this.times.slice(),t=this.values.slice(),n=this.constructor,s=new n(this.name,e,t);return s.createInterpolant=this.createInterpolant,s}}_i.prototype.TimeBufferType=Float32Array;_i.prototype.ValueBufferType=Float32Array;_i.prototype.DefaultInterpolation=fo;class Rr extends _i{constructor(e,t,n){super(e,t,n)}}Rr.prototype.ValueTypeName="bool";Rr.prototype.ValueBufferType=Array;Rr.prototype.DefaultInterpolation=uo;Rr.prototype.InterpolantFactoryMethodLinear=void 0;Rr.prototype.InterpolantFactoryMethodSmooth=void 0;class ap extends _i{}ap.prototype.ValueTypeName="color";class yr extends _i{}yr.prototype.ValueTypeName="number";class BM extends So{constructor(e,t,n,s){super(e,t,n,s)}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=(n-t)/(s-t);let l=e*a;for(let h=l+a;l!==h;l+=4)It.slerpFlat(r,0,o,l-a,o,l,c);return r}}class Mr extends _i{InterpolantFactoryMethodLinear(e){return new BM(this.times,this.values,this.getValueSize(),e)}}Mr.prototype.ValueTypeName="quaternion";Mr.prototype.InterpolantFactoryMethodSmooth=void 0;class Cr extends _i{constructor(e,t,n){super(e,t,n)}}Cr.prototype.ValueTypeName="string";Cr.prototype.ValueBufferType=Array;Cr.prototype.DefaultInterpolation=uo;Cr.prototype.InterpolantFactoryMethodLinear=void 0;Cr.prototype.InterpolantFactoryMethodSmooth=void 0;class wr extends _i{}wr.prototype.ValueTypeName="vector";class kM{constructor(e="",t=-1,n=[],s=u0){this.name=e,this.tracks=n,this.duration=t,this.blendMode=s,this.uuid=$n(),this.duration<0&&this.resetDuration()}static parse(e){const t=[],n=e.tracks,s=1/(e.fps||1);for(let o=0,a=n.length;o!==a;++o)t.push(HM(n[o]).scale(s));const r=new this(e.name,e.duration,t,e.blendMode);return r.uuid=e.uuid,r}static toJSON(e){const t=[],n=e.tracks,s={name:e.name,duration:e.duration,tracks:t,uuid:e.uuid,blendMode:e.blendMode};for(let r=0,o=n.length;r!==o;++r)t.push(_i.toJSON(n[r]));return s}static CreateFromMorphTargetSequence(e,t,n,s){const r=t.length,o=[];for(let a=0;a<r;a++){let c=[],l=[];c.push((a+r-1)%r,a,(a+1)%r),l.push(0,1,0);const h=NM(c);c=Dd(c,1,h),l=Dd(l,1,h),!s&&c[0]===0&&(c.push(r),l.push(l[0])),o.push(new yr(".morphTargetInfluences["+t[a].name+"]",c,l).scale(1/n))}return new this(e,-1,o)}static findByName(e,t){let n=e;if(!Array.isArray(e)){const s=e;n=s.geometry&&s.geometry.animations||s.animations}for(let s=0;s<n.length;s++)if(n[s].name===t)return n[s];return null}static CreateClipsFromMorphTargetSequences(e,t,n){const s={},r=/^([\w-]*?)([\d]+)$/;for(let a=0,c=e.length;a<c;a++){const l=e[a],h=l.name.match(r);if(h&&h.length>1){const u=h[1];let d=s[u];d||(s[u]=d=[]),d.push(l)}}const o=[];for(const a in s)o.push(this.CreateFromMorphTargetSequence(a,s[a],t,n));return o}static parseAnimation(e,t){if(!e)return console.error("THREE.AnimationClip: No animation in JSONLoader data."),null;const n=function(u,d,f,m,_){if(f.length!==0){const g=[],p=[];op(f,g,p,m),g.length!==0&&_.push(new u(d,g,p))}},s=[],r=e.name||"default",o=e.fps||30,a=e.blendMode;let c=e.length||-1;const l=e.hierarchy||[];for(let u=0;u<l.length;u++){const d=l[u].keys;if(!(!d||d.length===0))if(d[0].morphTargets){const f={};let m;for(m=0;m<d.length;m++)if(d[m].morphTargets)for(let _=0;_<d[m].morphTargets.length;_++)f[d[m].morphTargets[_]]=-1;for(const _ in f){const g=[],p=[];for(let y=0;y!==d[m].morphTargets.length;++y){const M=d[m];g.push(M.time),p.push(M.morphTarget===_?1:0)}s.push(new yr(".morphTargetInfluence["+_+"]",g,p))}c=f.length*o}else{const f=".bones["+t[u].name+"]";n(wr,f+".position",d,"pos",s),n(Mr,f+".quaternion",d,"rot",s),n(wr,f+".scale",d,"scl",s)}}return s.length===0?null:new this(r,c,s,a)}resetDuration(){const e=this.tracks;let t=0;for(let n=0,s=e.length;n!==s;++n){const r=this.tracks[n];t=Math.max(t,r.times[r.times.length-1])}return this.duration=t,this}trim(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].trim(0,this.duration);return this}validate(){let e=!0;for(let t=0;t<this.tracks.length;t++)e=e&&this.tracks[t].validate();return e}optimize(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].optimize();return this}clone(){const e=[];for(let t=0;t<this.tracks.length;t++)e.push(this.tracks[t].clone());return new this.constructor(this.name,this.duration,e,this.blendMode)}toJSON(){return this.constructor.toJSON(this)}}function zM(i){switch(i.toLowerCase()){case"scalar":case"double":case"float":case"number":case"integer":return yr;case"vector":case"vector2":case"vector3":case"vector4":return wr;case"color":return ap;case"quaternion":return Mr;case"bool":case"boolean":return Rr;case"string":return Cr}throw new Error("THREE.KeyframeTrack: Unsupported typeName: "+i)}function HM(i){if(i.type===void 0)throw new Error("THREE.KeyframeTrack: track type undefined, can not parse");const e=zM(i.type);if(i.times===void 0){const t=[],n=[];op(i.keys,t,n,"value"),i.times=t,i.values=n}return e.parse!==void 0?e.parse(i):new e(i.name,i.times,i.values,i.interpolation)}const Ji={enabled:!1,files:{},add:function(i,e){this.enabled!==!1&&(this.files[i]=e)},get:function(i){if(this.enabled!==!1)return this.files[i]},remove:function(i){delete this.files[i]},clear:function(){this.files={}}};class GM{constructor(e,t,n){const s=this;let r=!1,o=0,a=0,c;const l=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this.itemStart=function(h){a++,r===!1&&s.onStart!==void 0&&s.onStart(h,o,a),r=!0},this.itemEnd=function(h){o++,s.onProgress!==void 0&&s.onProgress(h,o,a),o===a&&(r=!1,s.onLoad!==void 0&&s.onLoad())},this.itemError=function(h){s.onError!==void 0&&s.onError(h)},this.resolveURL=function(h){return c?c(h):h},this.setURLModifier=function(h){return c=h,this},this.addHandler=function(h,u){return l.push(h,u),this},this.removeHandler=function(h){const u=l.indexOf(h);return u!==-1&&l.splice(u,2),this},this.getHandler=function(h){for(let u=0,d=l.length;u<d;u+=2){const f=l[u],m=l[u+1];if(f.global&&(f.lastIndex=0),f.test(h))return m}return null}}}const VM=new GM;class Is{constructor(e){this.manager=e!==void 0?e:VM,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){const n=this;return new Promise(function(s,r){n.load(e,s,t,r)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}}Is.DEFAULT_MATERIAL_NAME="__DEFAULT";const Ei={};class WM extends Error{constructor(e,t){super(e),this.response=t}}class Na extends Is{constructor(e){super(e)}load(e,t,n,s){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const r=Ji.get(e);if(r!==void 0)return this.manager.itemStart(e),setTimeout(()=>{t&&t(r),this.manager.itemEnd(e)},0),r;if(Ei[e]!==void 0){Ei[e].push({onLoad:t,onProgress:n,onError:s});return}Ei[e]=[],Ei[e].push({onLoad:t,onProgress:n,onError:s});const o=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin"}),a=this.mimeType,c=this.responseType;fetch(o).then(l=>{if(l.status===200||l.status===0){if(l.status===0&&console.warn("THREE.FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||l.body===void 0||l.body.getReader===void 0)return l;const h=Ei[e],u=l.body.getReader(),d=l.headers.get("X-File-Size")||l.headers.get("Content-Length"),f=d?parseInt(d):0,m=f!==0;let _=0;const g=new ReadableStream({start(p){y();function y(){u.read().then(({done:M,value:x})=>{if(M)p.close();else{_+=x.byteLength;const A=new ProgressEvent("progress",{lengthComputable:m,loaded:_,total:f});for(let E=0,P=h.length;E<P;E++){const R=h[E];R.onProgress&&R.onProgress(A)}p.enqueue(x),y()}},M=>{p.error(M)})}}});return new Response(g)}else throw new WM(`fetch for "${l.url}" responded with ${l.status}: ${l.statusText}`,l)}).then(l=>{switch(c){case"arraybuffer":return l.arrayBuffer();case"blob":return l.blob();case"document":return l.text().then(h=>new DOMParser().parseFromString(h,a));case"json":return l.json();default:if(a===void 0)return l.text();{const u=/charset="?([^;"\s]*)"?/i.exec(a),d=u&&u[1]?u[1].toLowerCase():void 0,f=new TextDecoder(d);return l.arrayBuffer().then(m=>f.decode(m))}}}).then(l=>{Ji.add(e,l);const h=Ei[e];delete Ei[e];for(let u=0,d=h.length;u<d;u++){const f=h[u];f.onLoad&&f.onLoad(l)}}).catch(l=>{const h=Ei[e];if(h===void 0)throw this.manager.itemError(e),l;delete Ei[e];for(let u=0,d=h.length;u<d;u++){const f=h[u];f.onError&&f.onError(l)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}}class XM extends Is{constructor(e){super(e)}load(e,t,n,s){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const r=this,o=Ji.get(e);if(o!==void 0)return r.manager.itemStart(e),setTimeout(function(){t&&t(o),r.manager.itemEnd(e)},0),o;const a=po("img");function c(){h(),Ji.add(e,this),t&&t(this),r.manager.itemEnd(e)}function l(u){h(),s&&s(u),r.manager.itemError(e),r.manager.itemEnd(e)}function h(){a.removeEventListener("load",c,!1),a.removeEventListener("error",l,!1)}return a.addEventListener("load",c,!1),a.addEventListener("error",l,!1),e.slice(0,5)!=="data:"&&this.crossOrigin!==void 0&&(a.crossOrigin=this.crossOrigin),r.manager.itemStart(e),a.src=e,a}}class qM extends Is{constructor(e){super(e)}load(e,t,n,s){const r=new rn,o=new XM(this.manager);return o.setCrossOrigin(this.crossOrigin),o.setPath(this.path),o.load(e,function(a){r.image=a,r.needsUpdate=!0,t!==void 0&&t(r)},n,s),r}}class Wh extends kt{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new Ve(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}const qc=new ge,Nd=new v,Ud=new v;class Xh{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new re(512,512),this.map=null,this.mapPass=null,this.matrix=new ge,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new Ph,this._frameExtents=new re(1,1),this._viewportCount=1,this._viewports=[new bt(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;Nd.setFromMatrixPosition(e.matrixWorld),t.position.copy(Nd),Ud.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(Ud),t.updateMatrixWorld(),qc.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(qc),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(qc)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class $M extends Xh{constructor(){super(new Cn(50,1,.5,500)),this.isSpotLightShadow=!0,this.focus=1}updateMatrices(e){const t=this.camera,n=_r*2*e.angle*this.focus,s=this.mapSize.width/this.mapSize.height,r=e.distance||t.far;(n!==t.fov||s!==t.aspect||r!==t.far)&&(t.fov=n,t.aspect=s,t.far=r,t.updateProjectionMatrix()),super.updateMatrices(e)}copy(e){return super.copy(e),this.focus=e.focus,this}}class jM extends Wh{constructor(e,t,n=0,s=Math.PI/3,r=0,o=2){super(e,t),this.isSpotLight=!0,this.type="SpotLight",this.position.copy(kt.DEFAULT_UP),this.updateMatrix(),this.target=new kt,this.distance=n,this.angle=s,this.penumbra=r,this.decay=o,this.map=null,this.shadow=new $M}get power(){return this.intensity*Math.PI}set power(e){this.intensity=e/Math.PI}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.angle=e.angle,this.penumbra=e.penumbra,this.decay=e.decay,this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}const Od=new ge,Xr=new v,$c=new v;class YM extends Xh{constructor(){super(new Cn(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new re(4,2),this._viewportCount=6,this._viewports=[new bt(2,1,1,1),new bt(0,1,1,1),new bt(3,1,1,1),new bt(1,1,1,1),new bt(3,0,1,1),new bt(1,0,1,1)],this._cubeDirections=[new v(1,0,0),new v(-1,0,0),new v(0,0,1),new v(0,0,-1),new v(0,1,0),new v(0,-1,0)],this._cubeUps=[new v(0,1,0),new v(0,1,0),new v(0,1,0),new v(0,1,0),new v(0,0,1),new v(0,0,-1)]}updateMatrices(e,t=0){const n=this.camera,s=this.matrix,r=e.distance||n.far;r!==n.far&&(n.far=r,n.updateProjectionMatrix()),Xr.setFromMatrixPosition(e.matrixWorld),n.position.copy(Xr),$c.copy(n.position),$c.add(this._cubeDirections[t]),n.up.copy(this._cubeUps[t]),n.lookAt($c),n.updateMatrixWorld(),s.makeTranslation(-Xr.x,-Xr.y,-Xr.z),Od.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(Od)}}class KM extends Wh{constructor(e,t,n=0,s=2){super(e,t),this.isPointLight=!0,this.type="PointLight",this.distance=n,this.decay=s,this.shadow=new YM}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}}class ZM extends Xh{constructor(){super(new qa(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class JM extends Wh{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(kt.DEFAULT_UP),this.updateMatrix(),this.target=new kt,this.shadow=new ZM}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class oo{static decodeText(e){if(console.warn("THREE.LoaderUtils: decodeText() has been deprecated with r165 and will be removed with r175. Use TextDecoder instead."),typeof TextDecoder<"u")return new TextDecoder().decode(e);let t="";for(let n=0,s=e.length;n<s;n++)t+=String.fromCharCode(e[n]);try{return decodeURIComponent(escape(t))}catch{return t}}static extractUrlBase(e){const t=e.lastIndexOf("/");return t===-1?"./":e.slice(0,t+1)}static resolveURL(e,t){return typeof e!="string"||e===""?"":(/^https?:\/\//i.test(t)&&/^\//.test(e)&&(t=t.replace(/(^https?:\/\/[^\/]+).*/i,"$1")),/^(https?:)?\/\//i.test(e)||/^data:.*,.*$/i.test(e)||/^blob:.*$/i.test(e)?e:t+e)}}class QM extends Is{constructor(e){super(e),this.isImageBitmapLoader=!0,typeof createImageBitmap>"u"&&console.warn("THREE.ImageBitmapLoader: createImageBitmap() not supported."),typeof fetch>"u"&&console.warn("THREE.ImageBitmapLoader: fetch() not supported."),this.options={premultiplyAlpha:"none"}}setOptions(e){return this.options=e,this}load(e,t,n,s){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const r=this,o=Ji.get(e);if(o!==void 0){if(r.manager.itemStart(e),o.then){o.then(l=>{t&&t(l),r.manager.itemEnd(e)}).catch(l=>{s&&s(l)});return}return setTimeout(function(){t&&t(o),r.manager.itemEnd(e)},0),o}const a={};a.credentials=this.crossOrigin==="anonymous"?"same-origin":"include",a.headers=this.requestHeader;const c=fetch(e,a).then(function(l){return l.blob()}).then(function(l){return createImageBitmap(l,Object.assign(r.options,{colorSpaceConversion:"none"}))}).then(function(l){return Ji.add(e,l),t&&t(l),r.manager.itemEnd(e),l}).catch(function(l){s&&s(l),Ji.remove(e),r.manager.itemError(e),r.manager.itemEnd(e)});Ji.add(e,c),r.manager.itemStart(e)}}const qh="\\[\\]\\.:\\/",ew=new RegExp("["+qh+"]","g"),$h="[^"+qh+"]",tw="[^"+qh.replace("\\.","")+"]",nw=/((?:WC+[\/:])*)/.source.replace("WC",$h),iw=/(WCOD+)?/.source.replace("WCOD",tw),sw=/(?:\.(WC+)(?:\[(.+)\])?)?/.source.replace("WC",$h),rw=/\.(WC+)(?:\[(.+)\])?/.source.replace("WC",$h),ow=new RegExp("^"+nw+iw+sw+rw+"$"),aw=["material","materials","bones","map"];class cw{constructor(e,t,n){const s=n||Lt.parseTrackName(t);this._targetGroup=e,this._bindings=e.subscribe_(t,s)}getValue(e,t){this.bind();const n=this._targetGroup.nCachedObjects_,s=this._bindings[n];s!==void 0&&s.getValue(e,t)}setValue(e,t){const n=this._bindings;for(let s=this._targetGroup.nCachedObjects_,r=n.length;s!==r;++s)n[s].setValue(e,t)}bind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].bind()}unbind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].unbind()}}class Lt{constructor(e,t,n){this.path=t,this.parsedPath=n||Lt.parseTrackName(t),this.node=Lt.findNode(e,this.parsedPath.nodeName),this.rootNode=e,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}static create(e,t,n){return e&&e.isAnimationObjectGroup?new Lt.Composite(e,t,n):new Lt(e,t,n)}static sanitizeNodeName(e){return e.replace(/\s/g,"_").replace(ew,"")}static parseTrackName(e){const t=ow.exec(e);if(t===null)throw new Error("PropertyBinding: Cannot parse trackName: "+e);const n={nodeName:t[2],objectName:t[3],objectIndex:t[4],propertyName:t[5],propertyIndex:t[6]},s=n.nodeName&&n.nodeName.lastIndexOf(".");if(s!==void 0&&s!==-1){const r=n.nodeName.substring(s+1);aw.indexOf(r)!==-1&&(n.nodeName=n.nodeName.substring(0,s),n.objectName=r)}if(n.propertyName===null||n.propertyName.length===0)throw new Error("PropertyBinding: can not parse propertyName from trackName: "+e);return n}static findNode(e,t){if(t===void 0||t===""||t==="."||t===-1||t===e.name||t===e.uuid)return e;if(e.skeleton){const n=e.skeleton.getBoneByName(t);if(n!==void 0)return n}if(e.children){const n=function(r){for(let o=0;o<r.length;o++){const a=r[o];if(a.name===t||a.uuid===t)return a;const c=n(a.children);if(c)return c}return null},s=n(e.children);if(s)return s}return null}_getValue_unavailable(){}_setValue_unavailable(){}_getValue_direct(e,t){e[t]=this.targetObject[this.propertyName]}_getValue_array(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)e[t++]=n[s]}_getValue_arrayElement(e,t){e[t]=this.resolvedProperty[this.propertyIndex]}_getValue_toArray(e,t){this.resolvedProperty.toArray(e,t)}_setValue_direct(e,t){this.targetObject[this.propertyName]=e[t]}_setValue_direct_setNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.needsUpdate=!0}_setValue_direct_setMatrixWorldNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_array(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)n[s]=e[t++]}_setValue_array_setNeedsUpdate(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)n[s]=e[t++];this.targetObject.needsUpdate=!0}_setValue_array_setMatrixWorldNeedsUpdate(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)n[s]=e[t++];this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_arrayElement(e,t){this.resolvedProperty[this.propertyIndex]=e[t]}_setValue_arrayElement_setNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.needsUpdate=!0}_setValue_arrayElement_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_fromArray(e,t){this.resolvedProperty.fromArray(e,t)}_setValue_fromArray_setNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.needsUpdate=!0}_setValue_fromArray_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.matrixWorldNeedsUpdate=!0}_getValue_unbound(e,t){this.bind(),this.getValue(e,t)}_setValue_unbound(e,t){this.bind(),this.setValue(e,t)}bind(){let e=this.node;const t=this.parsedPath,n=t.objectName,s=t.propertyName;let r=t.propertyIndex;if(e||(e=Lt.findNode(this.rootNode,t.nodeName),this.node=e),this.getValue=this._getValue_unavailable,this.setValue=this._setValue_unavailable,!e){console.warn("THREE.PropertyBinding: No target node found for track: "+this.path+".");return}if(n){let l=t.objectIndex;switch(n){case"materials":if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.materials){console.error("THREE.PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.",this);return}e=e.material.materials;break;case"bones":if(!e.skeleton){console.error("THREE.PropertyBinding: Can not bind to bones as node does not have a skeleton.",this);return}e=e.skeleton.bones;for(let h=0;h<e.length;h++)if(e[h].name===l){l=h;break}break;case"map":if("map"in e){e=e.map;break}if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.map){console.error("THREE.PropertyBinding: Can not bind to material.map as node.material does not have a map.",this);return}e=e.material.map;break;default:if(e[n]===void 0){console.error("THREE.PropertyBinding: Can not bind to objectName of node undefined.",this);return}e=e[n]}if(l!==void 0){if(e[l]===void 0){console.error("THREE.PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.",this,e);return}e=e[l]}}const o=e[s];if(o===void 0){const l=t.nodeName;console.error("THREE.PropertyBinding: Trying to update property for track: "+l+"."+s+" but it wasn't found.",e);return}let a=this.Versioning.None;this.targetObject=e,e.needsUpdate!==void 0?a=this.Versioning.NeedsUpdate:e.matrixWorldNeedsUpdate!==void 0&&(a=this.Versioning.MatrixWorldNeedsUpdate);let c=this.BindingType.Direct;if(r!==void 0){if(s==="morphTargetInfluences"){if(!e.geometry){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.",this);return}if(!e.geometry.morphAttributes){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.",this);return}e.morphTargetDictionary[r]!==void 0&&(r=e.morphTargetDictionary[r])}c=this.BindingType.ArrayElement,this.resolvedProperty=o,this.propertyIndex=r}else o.fromArray!==void 0&&o.toArray!==void 0?(c=this.BindingType.HasFromToArray,this.resolvedProperty=o):Array.isArray(o)?(c=this.BindingType.EntireArray,this.resolvedProperty=o):this.propertyName=s;this.getValue=this.GetterByBindingType[c],this.setValue=this.SetterByBindingTypeAndVersioning[c][a]}unbind(){this.node=null,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}}Lt.Composite=cw;Lt.prototype.BindingType={Direct:0,EntireArray:1,ArrayElement:2,HasFromToArray:3};Lt.prototype.Versioning={None:0,NeedsUpdate:1,MatrixWorldNeedsUpdate:2};Lt.prototype.GetterByBindingType=[Lt.prototype._getValue_direct,Lt.prototype._getValue_array,Lt.prototype._getValue_arrayElement,Lt.prototype._getValue_toArray];Lt.prototype.SetterByBindingTypeAndVersioning=[[Lt.prototype._setValue_direct,Lt.prototype._setValue_direct_setNeedsUpdate,Lt.prototype._setValue_direct_setMatrixWorldNeedsUpdate],[Lt.prototype._setValue_array,Lt.prototype._setValue_array_setNeedsUpdate,Lt.prototype._setValue_array_setMatrixWorldNeedsUpdate],[Lt.prototype._setValue_arrayElement,Lt.prototype._setValue_arrayElement_setNeedsUpdate,Lt.prototype._setValue_arrayElement_setMatrixWorldNeedsUpdate],[Lt.prototype._setValue_fromArray,Lt.prototype._setValue_fromArray_setNeedsUpdate,Lt.prototype._setValue_fromArray_setMatrixWorldNeedsUpdate]];typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:yh}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=yh);const lw=12,hw=yt.degToRad(lw),uw=1e-7,Fd=1e-7,cp=i=>new ge().makeTranslation(i.x,i.y,i.z),Bd=(i,e,t)=>e.get(t).clone().multiply(cp(i.heads.get(t)));function jc(i,e,t){const n=i.parents.get(t),s=Bd(i,e,t);return n?Bd(i,e,n).invert().multiply(s):s}const Yc=i=>{const e=new v,t=new It,n=new v;return i.decompose(e,t,n),{at:e,turn:t,scale:n}};function dw(i,e,t,n,s=e,r=hw){const o=new Map,a=new Map;let c=n>=1;for(const l of i.order){const h=Yc(jc(i,e,l)),u=Yc(jc(i,t,l)),d=Yc(jc(i,s,l)),f=h.at.lerp(u.at,n),m=h.scale.lerp(u.scale,n),_=h.turn.slerp(u.turn,n),g=d.turn.angleTo(_),p=d.turn.slerp(_,g>r?r/g:1),y=new ge().compose(f,p,m),M=i.parents.get(l),x=M?o.get(M).clone().multiply(y):y;o.set(l,x),a.set(l,x.clone().multiply(cp(i.heads.get(l).clone().negate()))),c&&(c=p.angleTo(u.turn)<uw&&f.distanceTo(u.at)<Fd&&m.distanceTo(u.scale)<Fd)}return{moves:a,settled:c}}const wn={hat:{base:3.62,crown:.86,height:1,brim:.2,thick:.05,curl:.18,band:[.04,.24],bandOut:.015,sides:48},white:[.97,.97,.95],whites:["hand_shell_l","hand_shell_r","butler_bow_tie__knot","butler_bow_tie__loop_l","butler_bow_tie__loop_r","butler_shirt__collar_band","butler_shirt__collar_point_l","butler_shirt__collar_point_r"],wing:{points:[[.04,2.47],[.19,2.45],[.09,2.36]],z:.43,thick:.02},tails:{side:[[-.3,1.78],[-.47,1.78],[-.68,.72],[-.58,.72]],across:[.04,.36]},satin:[.15,.15,.24],removed:["butler_bowler_hat","butler_tailcoat__tail_l","butler_tailcoat__tail_r"],satOn:["butler_tail_l","butler_tail_r"]};function ua(i,e,t,n){t.applyMatrix4(i.matrixWorld.clone().invert());const s=t.attributes.position.count,r=i.geometry.attributes.skinIndex.getX(0);t.setAttribute("skinIndex",new Ch(Array.from({length:s*4},(a,c)=>c%4?0:r),4)),t.setAttribute("skinWeight",new ht(Array.from({length:s*4},(a,c)=>c%4?0:1),4));const o=new Dh(t,new _n({color:new Ve(...n)}));return o.name=e,o.userData={item:e},o.position.copy(i.position),o.quaternion.copy(i.quaternion),o.scale.copy(i.scale),i.parent.add(o),o.bind(i.skeleton,i.bindMatrix),o.updateMatrixWorld(!0),o}function lp(){const{crown:i,height:e,brim:t,thick:n,curl:s,sides:r}=wn.hat,o=i+t,a=[[.001,0],[o,0],[o,n],[i,n],[i,e],[.001,e]],c=new Ar(a.map(([h,u])=>new re(h,u)),r),l=c.attributes.position;for(let h=0;h<l.count;h++){const[u,d,f]=[l.getX(h),l.getY(h),l.getZ(h)],m=Math.hypot(u,f);d<=n+1e-6&&m>i&&l.setY(h,d+s*((m-i)/t)**2*(u/m)**2)}return c.computeVertexNormals(),c}function hp(){const{crown:i,band:e,bandOut:t,sides:n}=wn.hat,s=new tt(i+t,i+t,e[1]-e[0],n,1,!0);return s.translate(0,(e[0]+e[1])/2,0),s}function fw(i){const{points:e,z:t,thick:n}=wn.wing,s=new Ls(e.map(([o,a])=>new re(i*o,a))),r=new bo(s,{depth:n,bevelEnabled:!1});return r.translate(0,0,t),r}function pw(i){const{side:e,across:t}=wn.tails,n=new Ls(e.map(([r,o])=>new re(r,o))),s=new bo(n,{depth:t[1]-t[0],bevelEnabled:!1});return s.rotateY(-Math.PI/2),s.translate(i>0?t[1]:-.04,0,0),s.computeVertexNormals(),s}function mw(i){const e=h=>i.find(u=>u.name===h);for(const h of i.filter(u=>wn.whites.includes(u.name)))h.material=h.material.clone(),h.material.color.setRGB(...wn.white);const t=e("butler_bowler_hat__crown"),n=new an().setFromObject(t).getCenter(new v),s=t.material.color.toArray(),r=e("butler_tailcoat__body").material.color.toArray(),o=e("butler_bow_tie__knot"),a=e("butler_tailcoat__tail_l"),c=[ua(t,"butler_top_hat",lp().translate(n.x,wn.hat.base,n.z),s),ua(t,"butler_top_hat_band",hp().translate(n.x,wn.hat.base,n.z),wn.satin),...[1,-1].map(h=>ua(o,`butler_wing_collar_${h>0?"l":"r"}`,fw(h),wn.white)),...[1,-1].map(h=>ua(a,`butler_tail_${h>0?"l":"r"}`,pw(h),r))],l=i.filter(h=>wn.removed.some(u=>h.name.startsWith(u)));for(const h of l)h.parent.remove(h);return[...i.filter(h=>!l.includes(h)),...c]}function kd(i,e){if(e===d0)return console.warn("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles."),i;if(e===nh||e===Lf){let t=i.getIndex();if(t===null){const o=[],a=i.getAttribute("position");if(a!==void 0){for(let c=0;c<a.count;c++)o.push(c);i.setIndex(o),t=i.getIndex()}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible."),i}const n=t.count-2,s=[];if(e===nh)for(let o=1;o<=n;o++)s.push(t.getX(0)),s.push(t.getX(o)),s.push(t.getX(o+1));else for(let o=0;o<n;o++)o%2===0?(s.push(t.getX(o)),s.push(t.getX(o+1)),s.push(t.getX(o+2))):(s.push(t.getX(o+2)),s.push(t.getX(o+1)),s.push(t.getX(o)));s.length/3!==n&&console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.");const r=i.clone();return r.setIndex(s),r.clearGroups(),r}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:",e),i}class gw extends Is{constructor(e){super(e),this.dracoLoader=null,this.ktx2Loader=null,this.meshoptDecoder=null,this.pluginCallbacks=[],this.register(function(t){return new Mw(t)}),this.register(function(t){return new ww(t)}),this.register(function(t){return new Lw(t)}),this.register(function(t){return new Iw(t)}),this.register(function(t){return new Dw(t)}),this.register(function(t){return new Sw(t)}),this.register(function(t){return new Ew(t)}),this.register(function(t){return new Tw(t)}),this.register(function(t){return new Aw(t)}),this.register(function(t){return new yw(t)}),this.register(function(t){return new Rw(t)}),this.register(function(t){return new bw(t)}),this.register(function(t){return new Pw(t)}),this.register(function(t){return new Cw(t)}),this.register(function(t){return new xw(t)}),this.register(function(t){return new Nw(t)}),this.register(function(t){return new Uw(t)})}load(e,t,n,s){const r=this;let o;if(this.resourcePath!=="")o=this.resourcePath;else if(this.path!==""){const l=oo.extractUrlBase(e);o=oo.resolveURL(l,this.path)}else o=oo.extractUrlBase(e);this.manager.itemStart(e);const a=function(l){s?s(l):console.error(l),r.manager.itemError(e),r.manager.itemEnd(e)},c=new Na(this.manager);c.setPath(this.path),c.setResponseType("arraybuffer"),c.setRequestHeader(this.requestHeader),c.setWithCredentials(this.withCredentials),c.load(e,function(l){try{r.parse(l,o,function(h){t(h),r.manager.itemEnd(e)},a)}catch(h){a(h)}},n,a)}setDRACOLoader(e){return this.dracoLoader=e,this}setKTX2Loader(e){return this.ktx2Loader=e,this}setMeshoptDecoder(e){return this.meshoptDecoder=e,this}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,s){let r;const o={},a={},c=new TextDecoder;if(typeof e=="string")r=JSON.parse(e);else if(e instanceof ArrayBuffer)if(c.decode(new Uint8Array(e,0,4))===up){try{o[dt.KHR_BINARY_GLTF]=new Ow(e)}catch(u){s&&s(u);return}r=JSON.parse(o[dt.KHR_BINARY_GLTF].content)}else r=JSON.parse(c.decode(e));else r=e;if(r.asset===void 0||r.asset.version[0]<2){s&&s(new Error("THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported."));return}const l=new Yw(r,{path:t||this.resourcePath||"",crossOrigin:this.crossOrigin,requestHeader:this.requestHeader,manager:this.manager,ktx2Loader:this.ktx2Loader,meshoptDecoder:this.meshoptDecoder});l.fileLoader.setRequestHeader(this.requestHeader);for(let h=0;h<this.pluginCallbacks.length;h++){const u=this.pluginCallbacks[h](l);u.name||console.error("THREE.GLTFLoader: Invalid plugin found: missing name"),a[u.name]=u,o[u.name]=!0}if(r.extensionsUsed)for(let h=0;h<r.extensionsUsed.length;++h){const u=r.extensionsUsed[h],d=r.extensionsRequired||[];switch(u){case dt.KHR_MATERIALS_UNLIT:o[u]=new vw;break;case dt.KHR_DRACO_MESH_COMPRESSION:o[u]=new Fw(r,this.dracoLoader);break;case dt.KHR_TEXTURE_TRANSFORM:o[u]=new Bw;break;case dt.KHR_MESH_QUANTIZATION:o[u]=new kw;break;default:d.indexOf(u)>=0&&a[u]===void 0&&console.warn('THREE.GLTFLoader: Unknown extension "'+u+'".')}}l.setExtensions(o),l.setPlugins(a),l.parse(n,s)}parseAsync(e,t){const n=this;return new Promise(function(s,r){n.parse(e,t,s,r)})}}function _w(){let i={};return{get:function(e){return i[e]},add:function(e,t){i[e]=t},remove:function(e){delete i[e]},removeAll:function(){i={}}}}const dt={KHR_BINARY_GLTF:"KHR_binary_glTF",KHR_DRACO_MESH_COMPRESSION:"KHR_draco_mesh_compression",KHR_LIGHTS_PUNCTUAL:"KHR_lights_punctual",KHR_MATERIALS_CLEARCOAT:"KHR_materials_clearcoat",KHR_MATERIALS_DISPERSION:"KHR_materials_dispersion",KHR_MATERIALS_IOR:"KHR_materials_ior",KHR_MATERIALS_SHEEN:"KHR_materials_sheen",KHR_MATERIALS_SPECULAR:"KHR_materials_specular",KHR_MATERIALS_TRANSMISSION:"KHR_materials_transmission",KHR_MATERIALS_IRIDESCENCE:"KHR_materials_iridescence",KHR_MATERIALS_ANISOTROPY:"KHR_materials_anisotropy",KHR_MATERIALS_UNLIT:"KHR_materials_unlit",KHR_MATERIALS_VOLUME:"KHR_materials_volume",KHR_TEXTURE_BASISU:"KHR_texture_basisu",KHR_TEXTURE_TRANSFORM:"KHR_texture_transform",KHR_MESH_QUANTIZATION:"KHR_mesh_quantization",KHR_MATERIALS_EMISSIVE_STRENGTH:"KHR_materials_emissive_strength",EXT_MATERIALS_BUMP:"EXT_materials_bump",EXT_TEXTURE_WEBP:"EXT_texture_webp",EXT_TEXTURE_AVIF:"EXT_texture_avif",EXT_MESHOPT_COMPRESSION:"EXT_meshopt_compression",EXT_MESH_GPU_INSTANCING:"EXT_mesh_gpu_instancing"};class xw{constructor(e){this.parser=e,this.name=dt.KHR_LIGHTS_PUNCTUAL,this.cache={refs:{},uses:{}}}_markDefs(){const e=this.parser,t=this.parser.json.nodes||[];for(let n=0,s=t.length;n<s;n++){const r=t[n];r.extensions&&r.extensions[this.name]&&r.extensions[this.name].light!==void 0&&e._addNodeRef(this.cache,r.extensions[this.name].light)}}_loadLight(e){const t=this.parser,n="light:"+e;let s=t.cache.get(n);if(s)return s;const r=t.json,c=((r.extensions&&r.extensions[this.name]||{}).lights||[])[e];let l;const h=new Ve(16777215);c.color!==void 0&&h.setRGB(c.color[0],c.color[1],c.color[2],vn);const u=c.range!==void 0?c.range:0;switch(c.type){case"directional":l=new JM(h),l.target.position.set(0,0,-1),l.add(l.target);break;case"point":l=new KM(h),l.distance=u;break;case"spot":l=new jM(h),l.distance=u,c.spot=c.spot||{},c.spot.innerConeAngle=c.spot.innerConeAngle!==void 0?c.spot.innerConeAngle:0,c.spot.outerConeAngle=c.spot.outerConeAngle!==void 0?c.spot.outerConeAngle:Math.PI/4,l.angle=c.spot.outerConeAngle,l.penumbra=1-c.spot.innerConeAngle/c.spot.outerConeAngle,l.target.position.set(0,0,-1),l.add(l.target);break;default:throw new Error("THREE.GLTFLoader: Unexpected light type: "+c.type)}return l.position.set(0,0,0),l.decay=2,Ri(l,c),c.intensity!==void 0&&(l.intensity=c.intensity),l.name=t.createUniqueName(c.name||"light_"+e),s=Promise.resolve(l),t.cache.add(n,s),s}getDependency(e,t){if(e==="light")return this._loadLight(t)}createNodeAttachment(e){const t=this,n=this.parser,r=n.json.nodes[e],a=(r.extensions&&r.extensions[this.name]||{}).light;return a===void 0?null:this._loadLight(a).then(function(c){return n._getNodeRef(t.cache,a,c)})}}class vw{constructor(){this.name=dt.KHR_MATERIALS_UNLIT}getMaterialType(){return _n}extendParams(e,t,n){const s=[];e.color=new Ve(1,1,1),e.opacity=1;const r=t.pbrMetallicRoughness;if(r){if(Array.isArray(r.baseColorFactor)){const o=r.baseColorFactor;e.color.setRGB(o[0],o[1],o[2],vn),e.opacity=o[3]}r.baseColorTexture!==void 0&&s.push(n.assignTexture(e,"map",r.baseColorTexture,Yt))}return Promise.all(s)}}class yw{constructor(e){this.parser=e,this.name=dt.KHR_MATERIALS_EMISSIVE_STRENGTH}extendMaterialParams(e,t){const s=this.parser.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=s.extensions[this.name].emissiveStrength;return r!==void 0&&(t.emissiveIntensity=r),Promise.resolve()}}class Mw{constructor(e){this.parser=e,this.name=dt.KHR_MATERIALS_CLEARCOAT}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:gi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];if(o.clearcoatFactor!==void 0&&(t.clearcoat=o.clearcoatFactor),o.clearcoatTexture!==void 0&&r.push(n.assignTexture(t,"clearcoatMap",o.clearcoatTexture)),o.clearcoatRoughnessFactor!==void 0&&(t.clearcoatRoughness=o.clearcoatRoughnessFactor),o.clearcoatRoughnessTexture!==void 0&&r.push(n.assignTexture(t,"clearcoatRoughnessMap",o.clearcoatRoughnessTexture)),o.clearcoatNormalTexture!==void 0&&(r.push(n.assignTexture(t,"clearcoatNormalMap",o.clearcoatNormalTexture)),o.clearcoatNormalTexture.scale!==void 0)){const a=o.clearcoatNormalTexture.scale;t.clearcoatNormalScale=new re(a,a)}return Promise.all(r)}}class ww{constructor(e){this.parser=e,this.name=dt.KHR_MATERIALS_DISPERSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:gi}extendMaterialParams(e,t){const s=this.parser.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=s.extensions[this.name];return t.dispersion=r.dispersion!==void 0?r.dispersion:0,Promise.resolve()}}class bw{constructor(e){this.parser=e,this.name=dt.KHR_MATERIALS_IRIDESCENCE}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:gi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return o.iridescenceFactor!==void 0&&(t.iridescence=o.iridescenceFactor),o.iridescenceTexture!==void 0&&r.push(n.assignTexture(t,"iridescenceMap",o.iridescenceTexture)),o.iridescenceIor!==void 0&&(t.iridescenceIOR=o.iridescenceIor),t.iridescenceThicknessRange===void 0&&(t.iridescenceThicknessRange=[100,400]),o.iridescenceThicknessMinimum!==void 0&&(t.iridescenceThicknessRange[0]=o.iridescenceThicknessMinimum),o.iridescenceThicknessMaximum!==void 0&&(t.iridescenceThicknessRange[1]=o.iridescenceThicknessMaximum),o.iridescenceThicknessTexture!==void 0&&r.push(n.assignTexture(t,"iridescenceThicknessMap",o.iridescenceThicknessTexture)),Promise.all(r)}}class Sw{constructor(e){this.parser=e,this.name=dt.KHR_MATERIALS_SHEEN}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:gi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[];t.sheenColor=new Ve(0,0,0),t.sheenRoughness=0,t.sheen=1;const o=s.extensions[this.name];if(o.sheenColorFactor!==void 0){const a=o.sheenColorFactor;t.sheenColor.setRGB(a[0],a[1],a[2],vn)}return o.sheenRoughnessFactor!==void 0&&(t.sheenRoughness=o.sheenRoughnessFactor),o.sheenColorTexture!==void 0&&r.push(n.assignTexture(t,"sheenColorMap",o.sheenColorTexture,Yt)),o.sheenRoughnessTexture!==void 0&&r.push(n.assignTexture(t,"sheenRoughnessMap",o.sheenRoughnessTexture)),Promise.all(r)}}class Ew{constructor(e){this.parser=e,this.name=dt.KHR_MATERIALS_TRANSMISSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:gi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return o.transmissionFactor!==void 0&&(t.transmission=o.transmissionFactor),o.transmissionTexture!==void 0&&r.push(n.assignTexture(t,"transmissionMap",o.transmissionTexture)),Promise.all(r)}}class Tw{constructor(e){this.parser=e,this.name=dt.KHR_MATERIALS_VOLUME}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:gi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];t.thickness=o.thicknessFactor!==void 0?o.thicknessFactor:0,o.thicknessTexture!==void 0&&r.push(n.assignTexture(t,"thicknessMap",o.thicknessTexture)),t.attenuationDistance=o.attenuationDistance||1/0;const a=o.attenuationColor||[1,1,1];return t.attenuationColor=new Ve().setRGB(a[0],a[1],a[2],vn),Promise.all(r)}}class Aw{constructor(e){this.parser=e,this.name=dt.KHR_MATERIALS_IOR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:gi}extendMaterialParams(e,t){const s=this.parser.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=s.extensions[this.name];return t.ior=r.ior!==void 0?r.ior:1.5,Promise.resolve()}}class Rw{constructor(e){this.parser=e,this.name=dt.KHR_MATERIALS_SPECULAR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:gi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];t.specularIntensity=o.specularFactor!==void 0?o.specularFactor:1,o.specularTexture!==void 0&&r.push(n.assignTexture(t,"specularIntensityMap",o.specularTexture));const a=o.specularColorFactor||[1,1,1];return t.specularColor=new Ve().setRGB(a[0],a[1],a[2],vn),o.specularColorTexture!==void 0&&r.push(n.assignTexture(t,"specularColorMap",o.specularColorTexture,Yt)),Promise.all(r)}}class Cw{constructor(e){this.parser=e,this.name=dt.EXT_MATERIALS_BUMP}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:gi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return t.bumpScale=o.bumpFactor!==void 0?o.bumpFactor:1,o.bumpTexture!==void 0&&r.push(n.assignTexture(t,"bumpMap",o.bumpTexture)),Promise.all(r)}}class Pw{constructor(e){this.parser=e,this.name=dt.KHR_MATERIALS_ANISOTROPY}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:gi}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return o.anisotropyStrength!==void 0&&(t.anisotropy=o.anisotropyStrength),o.anisotropyRotation!==void 0&&(t.anisotropyRotation=o.anisotropyRotation),o.anisotropyTexture!==void 0&&r.push(n.assignTexture(t,"anisotropyMap",o.anisotropyTexture)),Promise.all(r)}}class Lw{constructor(e){this.parser=e,this.name=dt.KHR_TEXTURE_BASISU}loadTexture(e){const t=this.parser,n=t.json,s=n.textures[e];if(!s.extensions||!s.extensions[this.name])return null;const r=s.extensions[this.name],o=t.options.ktx2Loader;if(!o){if(n.extensionsRequired&&n.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setKTX2Loader must be called before loading KTX2 textures");return null}return t.loadTextureImage(e,r.source,o)}}class Iw{constructor(e){this.parser=e,this.name=dt.EXT_TEXTURE_WEBP,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,s=n.json,r=s.textures[e];if(!r.extensions||!r.extensions[t])return null;const o=r.extensions[t],a=s.images[o.source];let c=n.textureLoader;if(a.uri){const l=n.options.manager.getHandler(a.uri);l!==null&&(c=l)}return this.detectSupport().then(function(l){if(l)return n.loadTextureImage(e,o.source,c);if(s.extensionsRequired&&s.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: WebP required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class Dw{constructor(e){this.parser=e,this.name=dt.EXT_TEXTURE_AVIF,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,s=n.json,r=s.textures[e];if(!r.extensions||!r.extensions[t])return null;const o=r.extensions[t],a=s.images[o.source];let c=n.textureLoader;if(a.uri){const l=n.options.manager.getHandler(a.uri);l!==null&&(c=l)}return this.detectSupport().then(function(l){if(l)return n.loadTextureImage(e,o.source,c);if(s.extensionsRequired&&s.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: AVIF required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAABcAAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAEAAAABAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQAMAAAAABNjb2xybmNseAACAAIABoAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAAB9tZGF0EgAKCBgABogQEDQgMgkQAAAAB8dSLfI=",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class Nw{constructor(e){this.name=dt.EXT_MESHOPT_COMPRESSION,this.parser=e}loadBufferView(e){const t=this.parser.json,n=t.bufferViews[e];if(n.extensions&&n.extensions[this.name]){const s=n.extensions[this.name],r=this.parser.getDependency("buffer",s.buffer),o=this.parser.options.meshoptDecoder;if(!o||!o.supported){if(t.extensionsRequired&&t.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files");return null}return r.then(function(a){const c=s.byteOffset||0,l=s.byteLength||0,h=s.count,u=s.byteStride,d=new Uint8Array(a,c,l);return o.decodeGltfBufferAsync?o.decodeGltfBufferAsync(h,u,d,s.mode,s.filter).then(function(f){return f.buffer}):o.ready.then(function(){const f=new ArrayBuffer(h*u);return o.decodeGltfBuffer(new Uint8Array(f),h,u,d,s.mode,s.filter),f})})}else return null}}class Uw{constructor(e){this.name=dt.EXT_MESH_GPU_INSTANCING,this.parser=e}createNodeMesh(e){const t=this.parser.json,n=t.nodes[e];if(!n.extensions||!n.extensions[this.name]||n.mesh===void 0)return null;const s=t.meshes[n.mesh];for(const l of s.primitives)if(l.mode!==Vn.TRIANGLES&&l.mode!==Vn.TRIANGLE_STRIP&&l.mode!==Vn.TRIANGLE_FAN&&l.mode!==void 0)return null;const o=n.extensions[this.name].attributes,a=[],c={};for(const l in o)a.push(this.parser.getDependency("accessor",o[l]).then(h=>(c[l]=h,c[l])));return a.length<1?null:(a.push(this.parser.createNodeMesh(e)),Promise.all(a).then(l=>{const h=l.pop(),u=h.isGroup?h.children:[h],d=l[0].count,f=[];for(const m of u){const _=new ge,g=new v,p=new It,y=new v(1,1,1),M=new tM(m.geometry,m.material,d);for(let x=0;x<d;x++)c.TRANSLATION&&g.fromBufferAttribute(c.TRANSLATION,x),c.ROTATION&&p.fromBufferAttribute(c.ROTATION,x),c.SCALE&&y.fromBufferAttribute(c.SCALE,x),M.setMatrixAt(x,_.compose(g,p,y));for(const x in c)if(x==="_COLOR_0"){const A=c[x];M.instanceColor=new rh(A.array,A.itemSize,A.normalized)}else x!=="TRANSLATION"&&x!=="ROTATION"&&x!=="SCALE"&&m.geometry.setAttribute(x,c[x]);kt.prototype.copy.call(M,m),this.parser.assignFinalMaterial(M),f.push(M)}return h.isGroup?(h.clear(),h.add(...f),h):f[0]}))}}const up="glTF",qr=12,zd={JSON:1313821514,BIN:5130562};class Ow{constructor(e){this.name=dt.KHR_BINARY_GLTF,this.content=null,this.body=null;const t=new DataView(e,0,qr),n=new TextDecoder;if(this.header={magic:n.decode(new Uint8Array(e.slice(0,4))),version:t.getUint32(4,!0),length:t.getUint32(8,!0)},this.header.magic!==up)throw new Error("THREE.GLTFLoader: Unsupported glTF-Binary header.");if(this.header.version<2)throw new Error("THREE.GLTFLoader: Legacy binary file detected.");const s=this.header.length-qr,r=new DataView(e,qr);let o=0;for(;o<s;){const a=r.getUint32(o,!0);o+=4;const c=r.getUint32(o,!0);if(o+=4,c===zd.JSON){const l=new Uint8Array(e,qr+o,a);this.content=n.decode(l)}else if(c===zd.BIN){const l=qr+o;this.body=e.slice(l,l+a)}o+=a}if(this.content===null)throw new Error("THREE.GLTFLoader: JSON content not found.")}}class Fw{constructor(e,t){if(!t)throw new Error("THREE.GLTFLoader: No DRACOLoader instance provided.");this.name=dt.KHR_DRACO_MESH_COMPRESSION,this.json=e,this.dracoLoader=t,this.dracoLoader.preload()}decodePrimitive(e,t){const n=this.json,s=this.dracoLoader,r=e.extensions[this.name].bufferView,o=e.extensions[this.name].attributes,a={},c={},l={};for(const h in o){const u=hh[h]||h.toLowerCase();a[u]=o[h]}for(const h in e.attributes){const u=hh[h]||h.toLowerCase();if(o[h]!==void 0){const d=n.accessors[e.attributes[h]],f=lr[d.componentType];l[u]=f.name,c[u]=d.normalized===!0}}return t.getDependency("bufferView",r).then(function(h){return new Promise(function(u,d){s.decodeDracoFile(h,function(f){for(const m in f.attributes){const _=f.attributes[m],g=c[m];g!==void 0&&(_.normalized=g)}u(f)},a,l,vn,d)})})}}class Bw{constructor(){this.name=dt.KHR_TEXTURE_TRANSFORM}extendTexture(e,t){return(t.texCoord===void 0||t.texCoord===e.channel)&&t.offset===void 0&&t.rotation===void 0&&t.scale===void 0||(e=e.clone(),t.texCoord!==void 0&&(e.channel=t.texCoord),t.offset!==void 0&&e.offset.fromArray(t.offset),t.rotation!==void 0&&(e.rotation=t.rotation),t.scale!==void 0&&e.repeat.fromArray(t.scale),e.needsUpdate=!0),e}}class kw{constructor(){this.name=dt.KHR_MESH_QUANTIZATION}}class dp extends So{constructor(e,t,n,s){super(e,t,n,s)}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,s=this.valueSize,r=e*s*3+s;for(let o=0;o!==s;o++)t[o]=n[r+o];return t}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=a*2,l=a*3,h=s-t,u=(n-t)/h,d=u*u,f=d*u,m=e*l,_=m-l,g=-2*f+3*d,p=f-d,y=1-g,M=p-d+u;for(let x=0;x!==a;x++){const A=o[_+x+a],E=o[_+x+c]*h,P=o[m+x+a],R=o[m+x]*h;r[x]=y*A+M*E+g*P+p*R}return r}}const zw=new It;class Hw extends dp{interpolate_(e,t,n,s){const r=super.interpolate_(e,t,n,s);return zw.fromArray(r).normalize().toArray(r),r}}const Vn={POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6},lr={5120:Int8Array,5121:Uint8Array,5122:Int16Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},Hd={9728:xn,9729:Un,9984:Mf,9985:xa,9986:Qr,9987:Li},Gd={33071:Zi,33648:Ca,10497:pr},Kc={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16},hh={POSITION:"position",NORMAL:"normal",TANGENT:"tangent",TEXCOORD_0:"uv",TEXCOORD_1:"uv1",TEXCOORD_2:"uv2",TEXCOORD_3:"uv3",COLOR_0:"color",WEIGHTS_0:"skinWeight",JOINTS_0:"skinIndex"},qi={scale:"scale",translation:"position",rotation:"quaternion",weights:"morphTargetInfluences"},Gw={CUBICSPLINE:void 0,LINEAR:fo,STEP:uo},Zc={OPAQUE:"OPAQUE",MASK:"MASK",BLEND:"BLEND"};function Vw(i){return i.DefaultMaterial===void 0&&(i.DefaultMaterial=new Vh({color:16777215,emissive:0,metalness:1,roughness:1,transparent:!1,depthTest:!0,side:Ni})),i.DefaultMaterial}function gs(i,e,t){for(const n in t.extensions)i[n]===void 0&&(e.userData.gltfExtensions=e.userData.gltfExtensions||{},e.userData.gltfExtensions[n]=t.extensions[n])}function Ri(i,e){e.extras!==void 0&&(typeof e.extras=="object"?Object.assign(i.userData,e.extras):console.warn("THREE.GLTFLoader: Ignoring primitive type .extras, "+e.extras))}function Ww(i,e,t){let n=!1,s=!1,r=!1;for(let l=0,h=e.length;l<h;l++){const u=e[l];if(u.POSITION!==void 0&&(n=!0),u.NORMAL!==void 0&&(s=!0),u.COLOR_0!==void 0&&(r=!0),n&&s&&r)break}if(!n&&!s&&!r)return Promise.resolve(i);const o=[],a=[],c=[];for(let l=0,h=e.length;l<h;l++){const u=e[l];if(n){const d=u.POSITION!==void 0?t.getDependency("accessor",u.POSITION):i.attributes.position;o.push(d)}if(s){const d=u.NORMAL!==void 0?t.getDependency("accessor",u.NORMAL):i.attributes.normal;a.push(d)}if(r){const d=u.COLOR_0!==void 0?t.getDependency("accessor",u.COLOR_0):i.attributes.color;c.push(d)}}return Promise.all([Promise.all(o),Promise.all(a),Promise.all(c)]).then(function(l){const h=l[0],u=l[1],d=l[2];return n&&(i.morphAttributes.position=h),s&&(i.morphAttributes.normal=u),r&&(i.morphAttributes.color=d),i.morphTargetsRelative=!0,i})}function Xw(i,e){if(i.updateMorphTargets(),e.weights!==void 0)for(let t=0,n=e.weights.length;t<n;t++)i.morphTargetInfluences[t]=e.weights[t];if(e.extras&&Array.isArray(e.extras.targetNames)){const t=e.extras.targetNames;if(i.morphTargetInfluences.length===t.length){i.morphTargetDictionary={};for(let n=0,s=t.length;n<s;n++)i.morphTargetDictionary[t[n]]=n}else console.warn("THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.")}}function qw(i){let e;const t=i.extensions&&i.extensions[dt.KHR_DRACO_MESH_COMPRESSION];if(t?e="draco:"+t.bufferView+":"+t.indices+":"+Jc(t.attributes):e=i.indices+":"+Jc(i.attributes)+":"+i.mode,i.targets!==void 0)for(let n=0,s=i.targets.length;n<s;n++)e+=":"+Jc(i.targets[n]);return e}function Jc(i){let e="";const t=Object.keys(i).sort();for(let n=0,s=t.length;n<s;n++)e+=t[n]+":"+i[t[n]]+";";return e}function uh(i){switch(i){case Int8Array:return 1/127;case Uint8Array:return 1/255;case Int16Array:return 1/32767;case Uint16Array:return 1/65535;default:throw new Error("THREE.GLTFLoader: Unsupported normalized accessor component type.")}}function $w(i){return i.search(/\.jpe?g($|\?)/i)>0||i.search(/^data\:image\/jpeg/)===0?"image/jpeg":i.search(/\.webp($|\?)/i)>0||i.search(/^data\:image\/webp/)===0?"image/webp":i.search(/\.ktx2($|\?)/i)>0||i.search(/^data\:image\/ktx2/)===0?"image/ktx2":"image/png"}const jw=new ge;class Yw{constructor(e={},t={}){this.json=e,this.extensions={},this.plugins={},this.options=t,this.cache=new _w,this.associations=new Map,this.primitiveCache={},this.nodeCache={},this.meshCache={refs:{},uses:{}},this.cameraCache={refs:{},uses:{}},this.lightCache={refs:{},uses:{}},this.sourceCache={},this.textureCache={},this.nodeNamesUsed={};let n=!1,s=-1,r=!1,o=-1;if(typeof navigator<"u"){const a=navigator.userAgent;n=/^((?!chrome|android).)*safari/i.test(a)===!0;const c=a.match(/Version\/(\d+)/);s=n&&c?parseInt(c[1],10):-1,r=a.indexOf("Firefox")>-1,o=r?a.match(/Firefox\/([0-9]+)\./)[1]:-1}typeof createImageBitmap>"u"||n&&s<17||r&&o<98?this.textureLoader=new qM(this.options.manager):this.textureLoader=new QM(this.options.manager),this.textureLoader.setCrossOrigin(this.options.crossOrigin),this.textureLoader.setRequestHeader(this.options.requestHeader),this.fileLoader=new Na(this.options.manager),this.fileLoader.setResponseType("arraybuffer"),this.options.crossOrigin==="use-credentials"&&this.fileLoader.setWithCredentials(!0)}setExtensions(e){this.extensions=e}setPlugins(e){this.plugins=e}parse(e,t){const n=this,s=this.json,r=this.extensions;this.cache.removeAll(),this.nodeCache={},this._invokeAll(function(o){return o._markDefs&&o._markDefs()}),Promise.all(this._invokeAll(function(o){return o.beforeRoot&&o.beforeRoot()})).then(function(){return Promise.all([n.getDependencies("scene"),n.getDependencies("animation"),n.getDependencies("camera")])}).then(function(o){const a={scene:o[0][s.scene||0],scenes:o[0],animations:o[1],cameras:o[2],asset:s.asset,parser:n,userData:{}};return gs(r,a,s),Ri(a,s),Promise.all(n._invokeAll(function(c){return c.afterRoot&&c.afterRoot(a)})).then(function(){for(const c of a.scenes)c.updateMatrixWorld();e(a)})}).catch(t)}_markDefs(){const e=this.json.nodes||[],t=this.json.skins||[],n=this.json.meshes||[];for(let s=0,r=t.length;s<r;s++){const o=t[s].joints;for(let a=0,c=o.length;a<c;a++)e[o[a]].isBone=!0}for(let s=0,r=e.length;s<r;s++){const o=e[s];o.mesh!==void 0&&(this._addNodeRef(this.meshCache,o.mesh),o.skin!==void 0&&(n[o.mesh].isSkinnedMesh=!0)),o.camera!==void 0&&this._addNodeRef(this.cameraCache,o.camera)}}_addNodeRef(e,t){t!==void 0&&(e.refs[t]===void 0&&(e.refs[t]=e.uses[t]=0),e.refs[t]++)}_getNodeRef(e,t,n){if(e.refs[t]<=1)return n;const s=n.clone(),r=(o,a)=>{const c=this.associations.get(o);c!=null&&this.associations.set(a,c);for(const[l,h]of o.children.entries())r(h,a.children[l])};return r(n,s),s.name+="_instance_"+e.uses[t]++,s}_invokeOne(e){const t=Object.values(this.plugins);t.push(this);for(let n=0;n<t.length;n++){const s=e(t[n]);if(s)return s}return null}_invokeAll(e){const t=Object.values(this.plugins);t.unshift(this);const n=[];for(let s=0;s<t.length;s++){const r=e(t[s]);r&&n.push(r)}return n}getDependency(e,t){const n=e+":"+t;let s=this.cache.get(n);if(!s){switch(e){case"scene":s=this.loadScene(t);break;case"node":s=this._invokeOne(function(r){return r.loadNode&&r.loadNode(t)});break;case"mesh":s=this._invokeOne(function(r){return r.loadMesh&&r.loadMesh(t)});break;case"accessor":s=this.loadAccessor(t);break;case"bufferView":s=this._invokeOne(function(r){return r.loadBufferView&&r.loadBufferView(t)});break;case"buffer":s=this.loadBuffer(t);break;case"material":s=this._invokeOne(function(r){return r.loadMaterial&&r.loadMaterial(t)});break;case"texture":s=this._invokeOne(function(r){return r.loadTexture&&r.loadTexture(t)});break;case"skin":s=this.loadSkin(t);break;case"animation":s=this._invokeOne(function(r){return r.loadAnimation&&r.loadAnimation(t)});break;case"camera":s=this.loadCamera(t);break;default:if(s=this._invokeOne(function(r){return r!=this&&r.getDependency&&r.getDependency(e,t)}),!s)throw new Error("Unknown type: "+e);break}this.cache.add(n,s)}return s}getDependencies(e){let t=this.cache.get(e);if(!t){const n=this,s=this.json[e+(e==="mesh"?"es":"s")]||[];t=Promise.all(s.map(function(r,o){return n.getDependency(e,o)})),this.cache.add(e,t)}return t}loadBuffer(e){const t=this.json.buffers[e],n=this.fileLoader;if(t.type&&t.type!=="arraybuffer")throw new Error("THREE.GLTFLoader: "+t.type+" buffer type is not supported.");if(t.uri===void 0&&e===0)return Promise.resolve(this.extensions[dt.KHR_BINARY_GLTF].body);const s=this.options;return new Promise(function(r,o){n.load(oo.resolveURL(t.uri,s.path),r,void 0,function(){o(new Error('THREE.GLTFLoader: Failed to load buffer "'+t.uri+'".'))})})}loadBufferView(e){const t=this.json.bufferViews[e];return this.getDependency("buffer",t.buffer).then(function(n){const s=t.byteLength||0,r=t.byteOffset||0;return n.slice(r,r+s)})}loadAccessor(e){const t=this,n=this.json,s=this.json.accessors[e];if(s.bufferView===void 0&&s.sparse===void 0){const o=Kc[s.type],a=lr[s.componentType],c=s.normalized===!0,l=new a(s.count*o);return Promise.resolve(new on(l,o,c))}const r=[];return s.bufferView!==void 0?r.push(this.getDependency("bufferView",s.bufferView)):r.push(null),s.sparse!==void 0&&(r.push(this.getDependency("bufferView",s.sparse.indices.bufferView)),r.push(this.getDependency("bufferView",s.sparse.values.bufferView))),Promise.all(r).then(function(o){const a=o[0],c=Kc[s.type],l=lr[s.componentType],h=l.BYTES_PER_ELEMENT,u=h*c,d=s.byteOffset||0,f=s.bufferView!==void 0?n.bufferViews[s.bufferView].byteStride:void 0,m=s.normalized===!0;let _,g;if(f&&f!==u){const p=Math.floor(d/f),y="InterleavedBuffer:"+s.bufferView+":"+s.componentType+":"+p+":"+s.count;let M=t.cache.get(y);M||(_=new l(a,p*f,s.count*f/h),M=new Zy(_,f/h),t.cache.add(y,M)),g=new Ih(M,c,d%f/h,m)}else a===null?_=new l(s.count*c):_=new l(a,d,s.count*c),g=new on(_,c,m);if(s.sparse!==void 0){const p=Kc.SCALAR,y=lr[s.sparse.indices.componentType],M=s.sparse.indices.byteOffset||0,x=s.sparse.values.byteOffset||0,A=new y(o[1],M,s.sparse.count*p),E=new l(o[2],x,s.sparse.count*c);a!==null&&(g=new on(g.array.slice(),g.itemSize,g.normalized)),g.normalized=!1;for(let P=0,R=A.length;P<R;P++){const b=A[P];if(g.setX(b,E[P*c]),c>=2&&g.setY(b,E[P*c+1]),c>=3&&g.setZ(b,E[P*c+2]),c>=4&&g.setW(b,E[P*c+3]),c>=5)throw new Error("THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.")}g.normalized=m}return g})}loadTexture(e){const t=this.json,n=this.options,r=t.textures[e].source,o=t.images[r];let a=this.textureLoader;if(o.uri){const c=n.manager.getHandler(o.uri);c!==null&&(a=c)}return this.loadTextureImage(e,r,a)}loadTextureImage(e,t,n){const s=this,r=this.json,o=r.textures[e],a=r.images[t],c=(a.uri||a.bufferView)+":"+o.sampler;if(this.textureCache[c])return this.textureCache[c];const l=this.loadImageSource(t,n).then(function(h){h.flipY=!1,h.name=o.name||a.name||"",h.name===""&&typeof a.uri=="string"&&a.uri.startsWith("data:image/")===!1&&(h.name=a.uri);const d=(r.samplers||{})[o.sampler]||{};return h.magFilter=Hd[d.magFilter]||Un,h.minFilter=Hd[d.minFilter]||Li,h.wrapS=Gd[d.wrapS]||pr,h.wrapT=Gd[d.wrapT]||pr,h.generateMipmaps=!h.isCompressedTexture&&h.minFilter!==xn&&h.minFilter!==Un,s.associations.set(h,{textures:e}),h}).catch(function(){return null});return this.textureCache[c]=l,l}loadImageSource(e,t){const n=this,s=this.json,r=this.options;if(this.sourceCache[e]!==void 0)return this.sourceCache[e].then(u=>u.clone());const o=s.images[e],a=self.URL||self.webkitURL;let c=o.uri||"",l=!1;if(o.bufferView!==void 0)c=n.getDependency("bufferView",o.bufferView).then(function(u){l=!0;const d=new Blob([u],{type:o.mimeType});return c=a.createObjectURL(d),c});else if(o.uri===void 0)throw new Error("THREE.GLTFLoader: Image "+e+" is missing URI and bufferView");const h=Promise.resolve(c).then(function(u){return new Promise(function(d,f){let m=d;t.isImageBitmapLoader===!0&&(m=function(_){const g=new rn(_);g.needsUpdate=!0,d(g)}),t.load(oo.resolveURL(u,r.path),m,void 0,f)})}).then(function(u){return l===!0&&a.revokeObjectURL(c),Ri(u,o),u.userData.mimeType=o.mimeType||$w(o.uri),u}).catch(function(u){throw console.error("THREE.GLTFLoader: Couldn't load texture",c),u});return this.sourceCache[e]=h,h}assignTexture(e,t,n,s){const r=this;return this.getDependency("texture",n.index).then(function(o){if(!o)return null;if(n.texCoord!==void 0&&n.texCoord>0&&(o=o.clone(),o.channel=n.texCoord),r.extensions[dt.KHR_TEXTURE_TRANSFORM]){const a=n.extensions!==void 0?n.extensions[dt.KHR_TEXTURE_TRANSFORM]:void 0;if(a){const c=r.associations.get(o);o=r.extensions[dt.KHR_TEXTURE_TRANSFORM].extendTexture(o,a),r.associations.set(o,c)}}return s!==void 0&&(o.colorSpace=s),e[t]=o,o})}assignFinalMaterial(e){const t=e.geometry;let n=e.material;const s=t.attributes.tangent===void 0,r=t.attributes.color!==void 0,o=t.attributes.normal===void 0;if(e.isPoints){const a="PointsMaterial:"+n.uuid;let c=this.cache.get(a);c||(c=new Zf,ui.prototype.copy.call(c,n),c.color.copy(n.color),c.map=n.map,c.sizeAttenuation=!1,this.cache.add(a,c)),n=c}else if(e.isLine){const a="LineBasicMaterial:"+n.uuid;let c=this.cache.get(a);c||(c=new Rs,ui.prototype.copy.call(c,n),c.color.copy(n.color),c.map=n.map,this.cache.add(a,c)),n=c}if(s||r||o){let a="ClonedMaterial:"+n.uuid+":";s&&(a+="derivative-tangents:"),r&&(a+="vertex-colors:"),o&&(a+="flat-shading:");let c=this.cache.get(a);c||(c=n.clone(),r&&(c.vertexColors=!0),o&&(c.flatShading=!0),s&&(c.normalScale&&(c.normalScale.y*=-1),c.clearcoatNormalScale&&(c.clearcoatNormalScale.y*=-1)),this.cache.add(a,c),this.associations.set(c,this.associations.get(n))),n=c}e.material=n}getMaterialType(){return Vh}loadMaterial(e){const t=this,n=this.json,s=this.extensions,r=n.materials[e];let o;const a={},c=r.extensions||{},l=[];if(c[dt.KHR_MATERIALS_UNLIT]){const u=s[dt.KHR_MATERIALS_UNLIT];o=u.getMaterialType(),l.push(u.extendParams(a,r,t))}else{const u=r.pbrMetallicRoughness||{};if(a.color=new Ve(1,1,1),a.opacity=1,Array.isArray(u.baseColorFactor)){const d=u.baseColorFactor;a.color.setRGB(d[0],d[1],d[2],vn),a.opacity=d[3]}u.baseColorTexture!==void 0&&l.push(t.assignTexture(a,"map",u.baseColorTexture,Yt)),a.metalness=u.metallicFactor!==void 0?u.metallicFactor:1,a.roughness=u.roughnessFactor!==void 0?u.roughnessFactor:1,u.metallicRoughnessTexture!==void 0&&(l.push(t.assignTexture(a,"metalnessMap",u.metallicRoughnessTexture)),l.push(t.assignTexture(a,"roughnessMap",u.metallicRoughnessTexture))),o=this._invokeOne(function(d){return d.getMaterialType&&d.getMaterialType(e)}),l.push(Promise.all(this._invokeAll(function(d){return d.extendMaterialParams&&d.extendMaterialParams(e,a)})))}r.doubleSided===!0&&(a.side=Pn);const h=r.alphaMode||Zc.OPAQUE;if(h===Zc.BLEND?(a.transparent=!0,a.depthWrite=!1):(a.transparent=!1,h===Zc.MASK&&(a.alphaTest=r.alphaCutoff!==void 0?r.alphaCutoff:.5)),r.normalTexture!==void 0&&o!==_n&&(l.push(t.assignTexture(a,"normalMap",r.normalTexture)),a.normalScale=new re(1,1),r.normalTexture.scale!==void 0)){const u=r.normalTexture.scale;a.normalScale.set(u,u)}if(r.occlusionTexture!==void 0&&o!==_n&&(l.push(t.assignTexture(a,"aoMap",r.occlusionTexture)),r.occlusionTexture.strength!==void 0&&(a.aoMapIntensity=r.occlusionTexture.strength)),r.emissiveFactor!==void 0&&o!==_n){const u=r.emissiveFactor;a.emissive=new Ve().setRGB(u[0],u[1],u[2],vn)}return r.emissiveTexture!==void 0&&o!==_n&&l.push(t.assignTexture(a,"emissiveMap",r.emissiveTexture,Yt)),Promise.all(l).then(function(){const u=new o(a);return r.name&&(u.name=r.name),Ri(u,r),t.associations.set(u,{materials:e}),r.extensions&&gs(s,u,r),u})}createUniqueName(e){const t=Lt.sanitizeNodeName(e||"");return t in this.nodeNamesUsed?t+"_"+ ++this.nodeNamesUsed[t]:(this.nodeNamesUsed[t]=0,t)}loadGeometries(e){const t=this,n=this.extensions,s=this.primitiveCache;function r(a){return n[dt.KHR_DRACO_MESH_COMPRESSION].decodePrimitive(a,t).then(function(c){return Vd(c,a,t)})}const o=[];for(let a=0,c=e.length;a<c;a++){const l=e[a],h=qw(l),u=s[h];if(u)o.push(u.promise);else{let d;l.extensions&&l.extensions[dt.KHR_DRACO_MESH_COMPRESSION]?d=r(l):d=Vd(new Xt,l,t),s[h]={primitive:l,promise:d},o.push(d)}}return Promise.all(o)}loadMesh(e){const t=this,n=this.json,s=this.extensions,r=n.meshes[e],o=r.primitives,a=[];for(let c=0,l=o.length;c<l;c++){const h=o[c].material===void 0?Vw(this.cache):this.getDependency("material",o[c].material);a.push(h)}return a.push(t.loadGeometries(o)),Promise.all(a).then(function(c){const l=c.slice(0,c.length-1),h=c[c.length-1],u=[];for(let f=0,m=h.length;f<m;f++){const _=h[f],g=o[f];let p;const y=l[f];if(g.mode===Vn.TRIANGLES||g.mode===Vn.TRIANGLE_STRIP||g.mode===Vn.TRIANGLE_FAN||g.mode===void 0)p=r.isSkinnedMesh===!0?new Dh(_,y):new jt(_,y),p.isSkinnedMesh===!0&&p.normalizeSkinWeights(),g.mode===Vn.TRIANGLE_STRIP?p.geometry=kd(p.geometry,Lf):g.mode===Vn.TRIANGLE_FAN&&(p.geometry=kd(p.geometry,nh));else if(g.mode===Vn.LINES)p=new wo(_,y);else if(g.mode===Vn.LINE_STRIP)p=new Oh(_,y);else if(g.mode===Vn.LINE_LOOP)p=new Kf(_,y);else if(g.mode===Vn.POINTS)p=new nM(_,y);else throw new Error("THREE.GLTFLoader: Primitive mode unsupported: "+g.mode);Object.keys(p.geometry.morphAttributes).length>0&&Xw(p,r),p.name=t.createUniqueName(r.name||"mesh_"+e),Ri(p,r),g.extensions&&gs(s,p,g),t.assignFinalMaterial(p),u.push(p)}for(let f=0,m=u.length;f<m;f++)t.associations.set(u[f],{meshes:e,primitives:f});if(u.length===1)return r.extensions&&gs(s,u[0],r),u[0];const d=new Ut;r.extensions&&gs(s,d,r),t.associations.set(d,{meshes:e});for(let f=0,m=u.length;f<m;f++)d.add(u[f]);return d})}loadCamera(e){let t;const n=this.json.cameras[e],s=n[n.type];if(!s){console.warn("THREE.GLTFLoader: Missing camera parameters.");return}return n.type==="perspective"?t=new Cn(yt.radToDeg(s.yfov),s.aspectRatio||1,s.znear||1,s.zfar||2e6):n.type==="orthographic"&&(t=new qa(-s.xmag,s.xmag,s.ymag,-s.ymag,s.znear,s.zfar)),n.name&&(t.name=this.createUniqueName(n.name)),Ri(t,n),Promise.resolve(t)}loadSkin(e){const t=this.json.skins[e],n=[];for(let s=0,r=t.joints.length;s<r;s++)n.push(this._loadNodeShallow(t.joints[s]));return t.inverseBindMatrices!==void 0?n.push(this.getDependency("accessor",t.inverseBindMatrices)):n.push(null),Promise.all(n).then(function(s){const r=s.pop(),o=s,a=[],c=[];for(let l=0,h=o.length;l<h;l++){const u=o[l];if(u){a.push(u);const d=new ge;r!==null&&d.fromArray(r.array,l*16),c.push(d)}else console.warn('THREE.GLTFLoader: Joint "%s" could not be found.',t.joints[l])}return new Uh(a,c)})}loadAnimation(e){const t=this.json,n=this,s=t.animations[e],r=s.name?s.name:"animation_"+e,o=[],a=[],c=[],l=[],h=[];for(let u=0,d=s.channels.length;u<d;u++){const f=s.channels[u],m=s.samplers[f.sampler],_=f.target,g=_.node,p=s.parameters!==void 0?s.parameters[m.input]:m.input,y=s.parameters!==void 0?s.parameters[m.output]:m.output;_.node!==void 0&&(o.push(this.getDependency("node",g)),a.push(this.getDependency("accessor",p)),c.push(this.getDependency("accessor",y)),l.push(m),h.push(_))}return Promise.all([Promise.all(o),Promise.all(a),Promise.all(c),Promise.all(l),Promise.all(h)]).then(function(u){const d=u[0],f=u[1],m=u[2],_=u[3],g=u[4],p=[];for(let y=0,M=d.length;y<M;y++){const x=d[y],A=f[y],E=m[y],P=_[y],R=g[y];if(x===void 0)continue;x.updateMatrix&&x.updateMatrix();const b=n._createAnimationTracks(x,A,E,P,R);if(b)for(let w=0;w<b.length;w++)p.push(b[w])}return new kM(r,void 0,p)})}createNodeMesh(e){const t=this.json,n=this,s=t.nodes[e];return s.mesh===void 0?null:n.getDependency("mesh",s.mesh).then(function(r){const o=n._getNodeRef(n.meshCache,s.mesh,r);return s.weights!==void 0&&o.traverse(function(a){if(a.isMesh)for(let c=0,l=s.weights.length;c<l;c++)a.morphTargetInfluences[c]=s.weights[c]}),o})}loadNode(e){const t=this.json,n=this,s=t.nodes[e],r=n._loadNodeShallow(e),o=[],a=s.children||[];for(let l=0,h=a.length;l<h;l++)o.push(n.getDependency("node",a[l]));const c=s.skin===void 0?Promise.resolve(null):n.getDependency("skin",s.skin);return Promise.all([r,Promise.all(o),c]).then(function(l){const h=l[0],u=l[1],d=l[2];d!==null&&h.traverse(function(f){f.isSkinnedMesh&&f.bind(d,jw)});for(let f=0,m=u.length;f<m;f++)h.add(u[f]);return h})}_loadNodeShallow(e){const t=this.json,n=this.extensions,s=this;if(this.nodeCache[e]!==void 0)return this.nodeCache[e];const r=t.nodes[e],o=r.name?s.createUniqueName(r.name):"",a=[],c=s._invokeOne(function(l){return l.createNodeMesh&&l.createNodeMesh(e)});return c&&a.push(c),r.camera!==void 0&&a.push(s.getDependency("camera",r.camera).then(function(l){return s._getNodeRef(s.cameraCache,r.camera,l)})),s._invokeAll(function(l){return l.createNodeAttachment&&l.createNodeAttachment(e)}).forEach(function(l){a.push(l)}),this.nodeCache[e]=Promise.all(a).then(function(l){let h;if(r.isBone===!0?h=new Yf:l.length>1?h=new Ut:l.length===1?h=l[0]:h=new kt,h!==l[0])for(let u=0,d=l.length;u<d;u++)h.add(l[u]);if(r.name&&(h.userData.name=r.name,h.name=o),Ri(h,r),r.extensions&&gs(n,h,r),r.matrix!==void 0){const u=new ge;u.fromArray(r.matrix),h.applyMatrix4(u)}else r.translation!==void 0&&h.position.fromArray(r.translation),r.rotation!==void 0&&h.quaternion.fromArray(r.rotation),r.scale!==void 0&&h.scale.fromArray(r.scale);return s.associations.has(h)||s.associations.set(h,{}),s.associations.get(h).nodes=e,h}),this.nodeCache[e]}loadScene(e){const t=this.extensions,n=this.json.scenes[e],s=this,r=new Ut;n.name&&(r.name=s.createUniqueName(n.name)),Ri(r,n),n.extensions&&gs(t,r,n);const o=n.nodes||[],a=[];for(let c=0,l=o.length;c<l;c++)a.push(s.getDependency("node",o[c]));return Promise.all(a).then(function(c){for(let h=0,u=c.length;h<u;h++)r.add(c[h]);const l=h=>{const u=new Map;for(const[d,f]of s.associations)(d instanceof ui||d instanceof rn)&&u.set(d,f);return h.traverse(d=>{const f=s.associations.get(d);f!=null&&u.set(d,f)}),u};return s.associations=l(r),r})}_createAnimationTracks(e,t,n,s,r){const o=[],a=e.name?e.name:e.uuid,c=[];qi[r.path]===qi.weights?e.traverse(function(d){d.morphTargetInfluences&&c.push(d.name?d.name:d.uuid)}):c.push(a);let l;switch(qi[r.path]){case qi.weights:l=yr;break;case qi.rotation:l=Mr;break;case qi.position:case qi.scale:l=wr;break;default:switch(n.itemSize){case 1:l=yr;break;case 2:case 3:default:l=wr;break}break}const h=s.interpolation!==void 0?Gw[s.interpolation]:fo,u=this._getArrayFromAccessor(n);for(let d=0,f=c.length;d<f;d++){const m=new l(c[d]+"."+qi[r.path],t.array,u,h);s.interpolation==="CUBICSPLINE"&&this._createCubicSplineTrackInterpolant(m),o.push(m)}return o}_getArrayFromAccessor(e){let t=e.array;if(e.normalized){const n=uh(t.constructor),s=new Float32Array(t.length);for(let r=0,o=t.length;r<o;r++)s[r]=t[r]*n;t=s}return t}_createCubicSplineTrackInterpolant(e){e.createInterpolant=function(n){const s=this instanceof Mr?Hw:dp;return new s(this.times,this.values,this.getValueSize()/3,n)},e.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline=!0}}function Kw(i,e,t){const n=e.attributes,s=new an;if(n.POSITION!==void 0){const a=t.json.accessors[n.POSITION],c=a.min,l=a.max;if(c!==void 0&&l!==void 0){if(s.set(new v(c[0],c[1],c[2]),new v(l[0],l[1],l[2])),a.normalized){const h=uh(lr[a.componentType]);s.min.multiplyScalar(h),s.max.multiplyScalar(h)}}else{console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.");return}}else return;const r=e.targets;if(r!==void 0){const a=new v,c=new v;for(let l=0,h=r.length;l<h;l++){const u=r[l];if(u.POSITION!==void 0){const d=t.json.accessors[u.POSITION],f=d.min,m=d.max;if(f!==void 0&&m!==void 0){if(c.setX(Math.max(Math.abs(f[0]),Math.abs(m[0]))),c.setY(Math.max(Math.abs(f[1]),Math.abs(m[1]))),c.setZ(Math.max(Math.abs(f[2]),Math.abs(m[2]))),d.normalized){const _=uh(lr[d.componentType]);c.multiplyScalar(_)}a.max(c)}else console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.")}}s.expandByVector(a)}i.boundingBox=s;const o=new pi;s.getCenter(o.center),o.radius=s.min.distanceTo(s.max)/2,i.boundingSphere=o}function Vd(i,e,t){const n=e.attributes,s=[];function r(o,a){return t.getDependency("accessor",o).then(function(c){i.setAttribute(a,c)})}for(const o in n){const a=hh[o]||o.toLowerCase();a in i.attributes||s.push(r(n[o],a))}if(e.indices!==void 0&&!i.index){const o=t.getDependency("accessor",e.indices).then(function(a){i.setIndex(a)});s.push(o)}return pt.workingColorSpace!==vn&&"COLOR_0"in n&&console.warn(`THREE.GLTFLoader: Converting vertex colors from "srgb-linear" to "${pt.workingColorSpace}" not supported.`),Ri(i,e),Kw(i,e,t),Promise.all(s).then(function(){return e.targets!==void 0?Ww(i,e.targets,t):i})}const Qc=new WeakMap;class Zw extends Is{constructor(e){super(e),this.decoderPath="",this.decoderConfig={},this.decoderBinary=null,this.decoderPending=null,this.workerLimit=4,this.workerPool=[],this.workerNextTaskID=1,this.workerSourceURL="",this.defaultAttributeIDs={position:"POSITION",normal:"NORMAL",color:"COLOR",uv:"TEX_COORD"},this.defaultAttributeTypes={position:"Float32Array",normal:"Float32Array",color:"Float32Array",uv:"Float32Array"}}setDecoderPath(e){return this.decoderPath=e,this}setDecoderConfig(e){return this.decoderConfig=e,this}setWorkerLimit(e){return this.workerLimit=e,this}load(e,t,n,s){const r=new Na(this.manager);r.setPath(this.path),r.setResponseType("arraybuffer"),r.setRequestHeader(this.requestHeader),r.setWithCredentials(this.withCredentials),r.load(e,o=>{this.parse(o,t,s)},n,s)}parse(e,t,n=()=>{}){this.decodeDracoFile(e,t,null,null,Yt,n).catch(n)}decodeDracoFile(e,t,n,s,r=vn,o=()=>{}){const a={attributeIDs:n||this.defaultAttributeIDs,attributeTypes:s||this.defaultAttributeTypes,useUniqueIDs:!!n,vertexColorSpace:r};return this.decodeGeometry(e,a).then(t).catch(o)}decodeGeometry(e,t){const n=JSON.stringify(t);if(Qc.has(e)){const c=Qc.get(e);if(c.key===n)return c.promise;if(e.byteLength===0)throw new Error("THREE.DRACOLoader: Unable to re-decode a buffer with different settings. Buffer has already been transferred.")}let s;const r=this.workerNextTaskID++,o=e.byteLength,a=this._getWorker(r,o).then(c=>(s=c,new Promise((l,h)=>{s._callbacks[r]={resolve:l,reject:h},s.postMessage({type:"decode",id:r,taskConfig:t,buffer:e},[e])}))).then(c=>this._createGeometry(c.geometry));return a.catch(()=>!0).then(()=>{s&&r&&this._releaseTask(s,r)}),Qc.set(e,{key:n,promise:a}),a}_createGeometry(e){const t=new Xt;e.index&&t.setIndex(new on(e.index.array,1));for(let n=0;n<e.attributes.length;n++){const s=e.attributes[n],r=s.name,o=s.array,a=s.itemSize,c=new on(o,a);r==="color"&&(this._assignVertexColorSpace(c,s.vertexColorSpace),c.normalized=!(o instanceof Float32Array)),t.setAttribute(r,c)}return t}_assignVertexColorSpace(e,t){if(t!==Yt)return;const n=new Ve;for(let s=0,r=e.count;s<r;s++)n.fromBufferAttribute(e,s),pt.toWorkingColorSpace(n,Yt),e.setXYZ(s,n.r,n.g,n.b)}_loadLibrary(e,t){const n=new Na(this.manager);return n.setPath(this.decoderPath),n.setResponseType(t),n.setWithCredentials(this.withCredentials),new Promise((s,r)=>{n.load(e,s,void 0,r)})}preload(){return this._initDecoder(),this}_initDecoder(){if(this.decoderPending)return this.decoderPending;const e=typeof WebAssembly!="object"||this.decoderConfig.type==="js",t=[];return e?t.push(this._loadLibrary("draco_decoder.js","text")):(t.push(this._loadLibrary("draco_wasm_wrapper.js","text")),t.push(this._loadLibrary("draco_decoder.wasm","arraybuffer"))),this.decoderPending=Promise.all(t).then(n=>{const s=n[0];e||(this.decoderConfig.wasmBinary=n[1]);const r=Jw.toString(),o=["/* draco decoder */",s,"","/* worker */",r.substring(r.indexOf("{")+1,r.lastIndexOf("}"))].join(`
`);this.workerSourceURL=URL.createObjectURL(new Blob([o]))}),this.decoderPending}_getWorker(e,t){return this._initDecoder().then(()=>{if(this.workerPool.length<this.workerLimit){const s=new Worker(this.workerSourceURL);s._callbacks={},s._taskCosts={},s._taskLoad=0,s.postMessage({type:"init",decoderConfig:this.decoderConfig}),s.onmessage=function(r){const o=r.data;switch(o.type){case"decode":s._callbacks[o.id].resolve(o);break;case"error":s._callbacks[o.id].reject(o);break;default:console.error('THREE.DRACOLoader: Unexpected message, "'+o.type+'"')}},this.workerPool.push(s)}else this.workerPool.sort(function(s,r){return s._taskLoad>r._taskLoad?-1:1});const n=this.workerPool[this.workerPool.length-1];return n._taskCosts[e]=t,n._taskLoad+=t,n})}_releaseTask(e,t){e._taskLoad-=e._taskCosts[t],delete e._callbacks[t],delete e._taskCosts[t]}debug(){console.log("Task load: ",this.workerPool.map(e=>e._taskLoad))}dispose(){for(let e=0;e<this.workerPool.length;++e)this.workerPool[e].terminate();return this.workerPool.length=0,this.workerSourceURL!==""&&URL.revokeObjectURL(this.workerSourceURL),this}}function Jw(){let i,e;onmessage=function(o){const a=o.data;switch(a.type){case"init":i=a.decoderConfig,e=new Promise(function(h){i.onModuleLoaded=function(u){h({draco:u})},DracoDecoderModule(i)});break;case"decode":const c=a.buffer,l=a.taskConfig;e.then(h=>{const u=h.draco,d=new u.Decoder;try{const f=t(u,d,new Int8Array(c),l),m=f.attributes.map(_=>_.array.buffer);f.index&&m.push(f.index.array.buffer),self.postMessage({type:"decode",id:a.id,geometry:f},m)}catch(f){console.error(f),self.postMessage({type:"error",id:a.id,error:f.message})}finally{u.destroy(d)}});break}};function t(o,a,c,l){const h=l.attributeIDs,u=l.attributeTypes;let d,f;const m=a.GetEncodedGeometryType(c);if(m===o.TRIANGULAR_MESH)d=new o.Mesh,f=a.DecodeArrayToMesh(c,c.byteLength,d);else if(m===o.POINT_CLOUD)d=new o.PointCloud,f=a.DecodeArrayToPointCloud(c,c.byteLength,d);else throw new Error("THREE.DRACOLoader: Unexpected geometry type.");if(!f.ok()||d.ptr===0)throw new Error("THREE.DRACOLoader: Decoding failed: "+f.error_msg());const _={index:null,attributes:[]};for(const g in h){const p=self[u[g]];let y,M;if(l.useUniqueIDs)M=h[g],y=a.GetAttributeByUniqueId(d,M);else{if(M=a.GetAttributeId(d,o[h[g]]),M===-1)continue;y=a.GetAttribute(d,M)}const x=s(o,a,d,g,p,y);g==="color"&&(x.vertexColorSpace=l.vertexColorSpace),_.attributes.push(x)}return m===o.TRIANGULAR_MESH&&(_.index=n(o,a,d)),o.destroy(d),_}function n(o,a,c){const h=c.num_faces()*3,u=h*4,d=o._malloc(u);a.GetTrianglesUInt32Array(c,u,d);const f=new Uint32Array(o.HEAPF32.buffer,d,h).slice();return o._free(d),{array:f,itemSize:1}}function s(o,a,c,l,h,u){const d=u.num_components(),m=c.num_points()*d,_=m*h.BYTES_PER_ELEMENT,g=r(o,h),p=o._malloc(_);a.GetAttributeDataArrayForAllPoints(c,u,g,_,p);const y=new h(o.HEAPF32.buffer,p,m).slice();return o._free(p),{name:l,array:y,itemSize:d}}function r(o,a){switch(a){case Float32Array:return o.DT_FLOAT32;case Int8Array:return o.DT_INT8;case Int16Array:return o.DT_INT16;case Int32Array:return o.DT_INT32;case Uint8Array:return o.DT_UINT8;case Uint16Array:return o.DT_UINT16;case Uint32Array:return o.DT_UINT32}}}const Qw=224,{height:Gt,middle:Fn}=Mm,el=8,Wd=3,eb="https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/libs/draco/gltf/",QT=(Gt/2-Fn)/Gt,tb=2,nb=.5,ib=.5,sb=i=>Math.min(nb*i.width/Qw,ib),Ti=4,rb=new v(-.35,-.8,.5),ob=.6,dh=new v(.6,.6,.7),ab=new v(.02,.02,.05),fp=.036,N={l:1,r:-1},Ps=65,tc=25,cb=25,lb=-6,Xd=95,hb=30,ub=20,pp=40,mp=25,gp=10,tl=[.4,-.92,2.1],_p=[.6,.3,-1],qd=4,ao=18,db=new Set(["butler_tray","butler_towel"]),nl="butler_tablet",xp=new Set(["colleague_mug"]),nc=new Set([...xp,"squire_shield","coach_clipboard"]),Mt=new Set([...nc,"squire_quill"]),fb=.06,pb={forearm:new v(0,0,-1),shin:new v(1,0,0)},Pr=new ge().set(1,0,0,0,0,0,1,0,0,-1,0,0,0,0,0,1),ic=Pr.clone().invert(),xo=i=>i.clone().applyMatrix4(ic),Ln=i=>new ge().makeTranslation(i.x,i.y,i.z),Xe=yt.degToRad,mb=1.2,il=new WeakMap;function gb(i){var t;if(il.has(i))return il.get(i);const e=new Map(i.order.map(n=>[n,[]]));for(const n of i.order)for(let s=i.parents.get(n);s;s=i.parents.get(s))(t=e.get(s))==null||t.push(n);return il.set(i,e),e}const On=(i,e,t)=>new ge().makeRotationFromEuler(new cn(Xe(i),Xe(e),Xe(t),"ZYX"));function _s(i,e){return Ln(i).multiply(e).multiply(Ln(i.clone().negate()))}function _b(i){const e=i.match(/^(.*)_([lr])$/);return e?{base:e[1],side:e[2]}:{base:i,side:""}}function xb(i,e){const{x:t,y:n,z:s}=pb[i];return e==="l"?new v(t,n,s):new v(t,-n,-s)}class vb{constructor(e,t="stand",n=0){this.rig=e,this.descendants=gb(e),this.final=new Map,this.eyes=1,this.eyeShape=null,this.eyeGlance=[0,0],this.bulbLit=0,this.eyeTint=null,this.hearts=0,this.stars=0,this.squeezed=0,this.dozing=0,this.whoa=!1,this.laptop=!1,this.tablet=!1,this.book=null,this.props=new Map,this.stowed=new Set,this.keep=new Set,this.inUse=new Set,this.tap=0,this.gaze=null,this.posture=t,this.sway=0,this.kneesApart=!0,this.stride=n,this.sky=null,this.throws=null,this.leanWay=0,this.phoneWay=1,this.walkWay=0,this.screen=null,this.facing=0,this.target=null,this.headContact=0}standing(e){const t=this.rig.parents.get(e);return t?this.matrix(t):new ge}matrix(e){return this.final.get(e)??this.standing(e)}head(e,t){return this.rig.heads.get(e).clone().applyMatrix4(t)}setMove(e,t){const n=(this.descendants.get(e)??[]).filter(s=>this.final.has(s));if(n.length){const s=t.clone().multiply(this.matrix(e).clone().invert());for(const r of n)this.final.set(r,s.clone().multiply(this.final.get(r)))}this.final.set(e,t)}turn(e,{x:t=0,y:n=0,z:s=0}){const r=this.matrix(e);this.setMove(e,_s(this.head(e,r),On(t,n,s)).multiply(r))}face(e,{x:t=0,y:n=0,z:s=0}){const r=this.head(e,this.standing(e)),o=this.rig.heads.get(e).clone().negate();this.setMove(e,Ln(r).multiply(On(t,n,s)).multiply(Ln(o)))}lift(e,{x:t=0,y:n=0,z:s=0}){this.setMove(e,Ln(new v(t,n,s)).multiply(this.matrix(e)))}bend(e,t){const{base:n,side:s}=_b(e),r=this.standing(e),o=xb(n,s).transformDirection(r).normalize(),a=new ge().makeRotationAxis(o,Xe(t));this.setMove(e,_s(this.head(e,r),a).multiply(r))}aim(e,t){const n=this.standing(e),s=this.rig.along.get(e).clone().transformDirection(n),r=new ge().makeRotationFromQuaternion(new It().setFromUnitVectors(s,t.clone().normalize()));this.setMove(e,_s(this.head(e,n),r).multiply(n))}reach(e,t,n){this.limbTo(e,["upper_arm","forearm","hand"],t,n)}withinReach(e,t,n){const[s,r,o]=["upper_arm","forearm","hand"].map(u=>this.rig.heads.get(`${u}_${e}`)),a=(r.distanceTo(s)+o.distanceTo(r))*n,c=this.foldedReach(e),l=this.head(`upper_arm_${e}`,this.standing(`upper_arm_${e}`)),h=t.clone().sub(l);return h.length()>a?l.clone().add(h.setLength(a)):h.length()>=c?t:l.clone().add(h.setLength(c))}foldedReach(e){const[t,n,s]=["upper_arm","forearm","hand"].map(r=>this.rig.heads.get(`${r}_${e}`));return Math.abs(n.distanceTo(t)-s.distanceTo(n))*mb}step(e,t,n){this.limbTo(e,["thigh","shin","foot"],t,n)}limbTo(e,t,n,s){const[r,o,a]=t.map(p=>`${p}_${e}`),c=this.rig.heads.get(o).distanceTo(this.rig.heads.get(r)),l=this.rig.heads.get(a).distanceTo(this.rig.heads.get(o)),h=this.head(r,this.standing(r)),u=n.clone().sub(h),d=u.length();if(d<Math.abs(c-l)||d>c+l)throw new Error(`the ${r} cannot reach ${d.toFixed(3)}`);const f=u.clone().normalize(),m=(c*c-l*l+d*d)/(2*d),_=s.clone();e==="r"&&(_.x=-_.x),_.sub(f.clone().multiplyScalar(_.dot(f)));const g=h.clone().add(f.multiplyScalar(m)).add(_.normalize().multiplyScalar(Math.sqrt(Math.max(c*c-m*m,0))));this.aim(r,g.clone().sub(h)),this.aim(o,n.clone().sub(g))}turnAll({x:e=0,y:t=0,z:n=0},s=new v){const r=_s(s,On(e,t,n));this.final=new Map(this.rig.order.map(o=>[o,r.clone().multiply(this.matrix(o))]))}revolve(e){this.turnAll({z:e})}bendAbove(e,{x:t=0,y:n=0,z:s=0}){const r=_s(this.head(e,this.matrix(e)),On(t,n,s)),o=a=>a===e||!!a&&o(this.rig.parents.get(a));this.final=new Map(this.rig.order.map(a=>[a,o(a)?r.clone().multiply(this.matrix(a)):this.matrix(a)]))}offsetAll(e){const t=Ln(new v(...e));this.final=new Map(this.rig.order.map(n=>[n,t.clone().multiply(this.matrix(n))]))}carried(e){return e.clone().add(this.head("root",this.matrix("root")).sub(this.rig.heads.get("root")))}swing(e){this.sway=e}kneesTogether(){this.kneesApart=!1}shutEyes(e){this.eyes=Math.max(e,fb)}glanceEyes(e,t){this.eyeGlance=[t,e]}shapeEyes(e,t=1,n=1){this.eyeShape=t>0?{name:e,strength:t,way:n}:null}tintEyes(e){this.eyeTint=e}heartEyes(e){this.hearts=e}starEyes(e){this.stars=e}squeezeEyes(e){this.squeezed=e}doze(e){this.dozing=e}eyesShown(){var e;return Math.min(Math.max(((e=this.eyeShape)==null?void 0:e.strength)??0,this.hearts,this.stars,this.squeezed,this.dozing,this.whoa?1:0),1)}holdLaptop(){this.laptop=!0}holdTablet(){this.tablet=!0}holdBook(e,t,n){this.book={open:e,page:t,visible:n}}holdProp(e,t,n=[0,0,0],s={}){this.props.set(e,{bone:`hand_${t}`,frame:`hand_${t}`,at:this.grip(t,n),turn:s})}holdUpright(e,t,n=[0,0,0],s={}){this.props.set(e,{bone:`hand_${t}`,frame:"root",at:this.grip(t,n),turn:s})}standProp(e,t,n={},s=1){this.props.set(e,{bone:"root",frame:"root",at:new v(...t),turn:n,size:s})}lightBulb(e,t,n){const[s,r,o]=hr.at;this.standProp("light_bulb",[n*s,r,o]),Object.assign(this.props.get("light_bulb"),{size:e,lit:t}),this.bulbLit=t}wearProp(e,t,n={}){this.props.set(e,{bone:"head",frame:"head",at:this.rig.heads.get("head").clone().add(new v(...t)),turn:n})}roll(e,t){const n=this.matrix(e),s=this.rig.along.get(e).clone().transformDirection(n).normalize();this.final.set(e,_s(this.head(e,n),new ge().makeRotationAxis(s,Xe(t))).multiply(n))}clench(e,t){const n=`hand_${e}`,s=this.rig.heads.get(n),r=this.rig.along.get(n).clone().normalize(),o=new ge().set(1+(t-1)*r.x*r.x,(t-1)*r.x*r.y,(t-1)*r.x*r.z,0,(t-1)*r.y*r.x,1+(t-1)*r.y*r.y,(t-1)*r.y*r.z,0,(t-1)*r.z*r.x,(t-1)*r.z*r.y,1+(t-1)*r.z*r.z,0,0,0,0,1);this.final.set(n,this.matrix(n).clone().multiply(_s(s,o)))}grip(e,t){return this.rig.heads.get(`hand_${e}`).clone().add(new v(N[e]*(hn.grip+t[0]),hn.forward+t[1],t[2]))}putAway(...e){e.forEach(t=>this.stowed.add(t))}moves(e){const t=new ge().makeRotationZ(Xe(e)),n=new Map;for(const s of this.rig.order){const r=this.rig.parents.get(s);n.set(s,this.final.get(s)??(r?n.get(r):new ge))}return new Map([...n].map(([s,r])=>[s,t.clone().multiply(r)]))}}const Te=(i,e=1)=>Math.sin(2*Math.PI*e*i);function fe(i,e,t=1){i.turn("spine",{x:1*t*Te(e)}),i.turn("chest",{x:1.5*t*Te(e-.05)}),i.turn("neck",{x:-.8*t*Te(e-.1)}),i.turn("head",{x:-1.2*t*Te(e-.12)})}function oe(i,{lean:e=0,twist:t=0,nod:n=0,turn:s=0,tilt:r=0}){i.turn("spine",{x:e*.4,z:t*.4}),i.turn("chest",{x:e*.6,z:t*.6}),i.turn("neck",{x:n*.3,z:s*.3,y:r*.3}),i.turn("head",{x:n*.7,z:s*.7,y:r*.7})}function jh(i,e,t=0,n=10){i.turn(`upper_arm_${e}`,{y:N[e]*Ps}),i.turn(`upper_arm_${e}`,{x:t}),i.bend(`forearm_${e}`,n)}function vp(i,e,t=lb,n=0,s=0){const r=N[e];i.turn(`upper_arm_${e}`,{y:r*Ps}),i.turn(`upper_arm_${e}`,{x:-n}),i.turn(`upper_arm_${e}`,{z:r*ub}),i.face(`forearm_${e}`,{y:-r*t,z:-r*Xd}),i.face(`hand_${e}`,{x:s,z:-r*(Xd-hb)})}function xe(i,e,t=[],n={},s=e.level){var r;i.restArms={stance:e,swing:n,level:s};for(const o of Object.keys(N))if(!t.includes(o)){if(s.has(o)){vp(i,o);continue}jh(i,o,n[o]??0),(r=e.shield)!=null&&r.has(o)&&i.turn(`hand_${o}`,{y:-N[o]*Lp,z:N[o]*Pp})}}const Ke=i=>i.busy.has("r")?"l":"r",yb=(i,e)=>{const t=e===N.l?"l":e===N.r?"r":null;return t&&!i.busy.has(t)?t:Ke(i)};function sc(i,e,t){fe(i,t),xe(i,e),i.swing(Te(t))}function Mb(i,e,t){const n=Math.max(Te(Dt(t,10),2),0)**2;oe(i,{lean:4*n,nod:26*n}),xe(i,e)}const Ks={at:[0,-.62,1.95],apart:.07,circle:.13,nod:8,turn:70};function wb(i,e,t){const n=ie.hand_rub,s=Dt(t,n.frames),r=ne(s,n.together)*(1-ne(s,n.apart)),o=2*Math.PI*n.rubs*at(s,n.together[1],n.apart[0]);fe(i,0),oe(i,{lean:4*r,nod:Ks.nod*r*(.5+.5*Math.sin(2*o))}),i.putAway(...Mt),xe(i,e,r?Object.keys(N):[]);const[a,c,l]=Ks.at;for(const[h,u]of Object.entries(N)){const d=new v(a+u*(Ks.apart+Ks.circle*Math.cos(o)),c,l+u*Ks.circle*Math.sin(o));r&&At(i,h,r,i.withinReach(h,i.carried(d),.97),new v(...z.elbow))}Ze(i,"amused",r),Math.abs(Math.sin(Xe(i.facing??0)))<.5&&i.revolve(Ks.turn*r)}function bb(i,e,t){const n=Dt(t,12),s=Q(n,0,.12)*(1-Q(n,.78,1));oe(i,{turn:28*Te(n,2)*s,tilt:4*Te(n,2)*s}),xe(i,e)}function Sb(i,e,t){const n=Ke(e),s=N[n];oe(i,{twist:-s*4,turn:-s*8,tilt:-s*6}),xe(i,e,[n]),yp(i,n,t)}function yp(i,e,t){i.turn(`upper_arm_${e}`,{x:-85}),i.turn(`upper_arm_${e}`,{z:N[e]*pp}),i.bend(`forearm_${e}`,mp+gp*Te(t))}const gn={tilt:22,nod:-12,sway:4,cheek:[.38,-.78,2.6],finger:[.2,.15,1],elbow:[.1,-.5,-1],inboard:.1,under:.12,folded:[1,-.6,-.4],glance:[.35,.3],gotIt:[.85,-.45,2.75]};function Eb(i,e,t,n,s,r){Ds(i,e),os(i,e,t,n.clone().addScaledVector(s,-hn.grip),null,r.toArray()),Op(i,e,t,s)}function Tb(i,e,t,n){const s=i.head(`forearm_${t}`,i.matrix(`forearm_${t}`)),r=new v(s.x*gn.inboard,s.y,s.z-gn.under);Ds(i,e),os(i,e,n,i.withinReach(e,r,.97),null,gn.folded)}function Ab(i,e,t,{thinking:n,sway:s,got:r,raised:o}){const a=Ke(e),c=a==="l"?"r":"l",l=N[a];fe(i,t),oe(i,{nod:gn.nod*n-10*r,tilt:-l*(gn.tilt*n+gn.sway*s),turn:3*s}),i.putAway(...Mt),xe(i,e,[...n+r?[a]:[],...n?[c]:[]]),n+r&&Mp(i,a,Math.max(n,r),o),n&&Tb(i,c,a,n),i.glanceEyes(gn.glance[0]*n,-l*gn.glance[1]*n),Ze(i,"startled",r)}function Mp(i,e,t,n=0){const s=N[e],[r,o,a]=gn.cheek,c=new v(s*r,o,a).applyMatrix4(i.matrix("head")),[l,h,u]=gn.gotIt,d=i.carried(new v(s*l,h,u+hn.grip)),[f,m,_]=gn.finger;Eb(i,e,t,c.lerp(d,n),new v(-s*f,m,_).normalize(),new v(...gn.elbow))}const sl=i=>(e,t,n)=>{const s=Dt(n,i.frames),r=i.cloud?ne(s,i.into)*(1-ne(s,i.rise)):0,o=!!i.lights,a=o?ne(s,i.rise)*(1-ne(s,i.fades)):0;Ab(e,t,n,{thinking:r,sway:(i.sways?Math.sin(2*Math.PI*i.sways*s):0)*r,got:a,raised:o?ne(s,i.rise):0}),o&&s>=i.appears[0]&&e.lightBulb(ne(s,i.appears)*(1-ne(s,i.goes)),ne(s,i.lights)*(1-ne(s,i.fades)),N[Ke(t)])};function Rb(i,e,t){const n=Math.max(Math.sin(2*Math.PI*2*t),0);i.lift("root",{z:.28*n}),i.turn("hips",{z:6*Te(t,2)}),oe(i,{lean:-5,turn:-6*Te(t,2)});const s=Object.keys(N).filter(r=>!e.busy.has(r));xe(i,e,s);for(const r of s)N[r],ln(i,r,1,{y:-tc,bend:10+6*Te(t,4)});for(const r of Object.keys(N))i.turn(`thigh_${r}`,{x:-18*n}),i.turn(`shin_${r}`,{x:34*n}),i.turn(`foot_${r}`,{x:-10*n})}function Cb(i,e,t){const n=t*(z.yawnFrames+ao);if(n<z.yawnFrames){zp(i,e,n/z.yawnFrames);const r=Q(n,z.yawnFrames-5,z.yawnFrames);oe(i,{lean:4*r,nod:8*r,tilt:N[Ke(e)]*qd*r});for(const o of Object.keys(N))Ds(i,o);Fp(i,Ke(e),kn(n/z.yawnFrames,z.yawnFrames).ready),i.shutEyes(i.eyes*(1-r));return}const s=Te((n-z.yawnFrames)/ao);fe(i,0),oe(i,{lean:4+1.5*s,nod:8+2*s,tilt:N[Ke(e)]*qd}),xe(i,e),i.shutEyes(0)}function Pb(i,e,t){i.stride=t;const n=2*Math.PI*t;Yh(i),i.turn("hips",{z:5*Math.sin(n)}),oe(i,{lean:3,twist:-7*Math.sin(n),turn:3*Math.sin(n)}),xe(i,e,[],{l:22*Math.sin(n),r:-22*Math.sin(n)}),rc(i)}function Yh(i){const e=-.11+.012*Math.cos(4*Math.PI*i.stride);i.lift("root",{z:e-(i.strideHeight??0)}),i.strideHeight=e}function rc(i,e=1){for(const[t,n]of[["l",0],["r",.5]]){const[s,r]=Tp(i.stride+n,Qi[0],Qi[1],Qi[2]),o=i.rig.heads.get(`foot_${t}`),a=Xe(i.strideTurn??0),c=new v(0,0,1),l=i.carried(o).add(new v(0,s*e,r*e-(i.strideHeight??0)).applyAxisAngle(c,a));i.step(t,l,new v(0,-1,0).applyAxisAngle(c,a)),i.face(`foot_${t}`,{x:-8*r/Qi[2]*e,z:i.strideTurn??0})}}const Ua=4.4,wp=.72,bp=.94,Kh=[1.84,.38,.2],Qi=[hc.length,hc.planted,hc.clearance],$d=.14,Lb=.2,Ib=68,Db=16,Nb=1.25,Ub=2.91,rl={back:.58,up:.36,rise:.38},Ob=new v(1,-1,-1);function Yn(i){return i=Math.min(Math.max(i,0),1),i*i*(3-2*i)}function Dt(i,e){return Math.min(Math.max(i*e/(e-1),0),1)}const at=(i,e,t)=>Math.min(Math.max((i-e)/(t-e),0),1),Q=(i,e,t)=>Yn(at(i,e,t)),He=(i,e,t)=>Math.sin(Math.PI*at(i,e,t)),nt=(i,e,t)=>i+(e-i)*t,jd=(i,e,t)=>Math.exp(-t*i)*Math.sin(2*Math.PI*e*i)*(1-i);function Fb(i,e){return i!=="pull_ups"||!(e.busy.size||e.level.size)}function Zh(i){i.lift("root",{z:Lb}),i.putAway(...wn.satOn)}const qn={lean:-24,feet:18,hands:[.62,.5],floor:1.4};function Bb(i){Zh(i),oe(i,{lean:qn.lean,nod:-qn.lean*.6})}function kb(i){for(const e of Object.keys(N))i.turn(`thigh_${e}`,{x:-88}),i.turn(`foot_${e}`,{x:qn.feet});for(const[e,t]of Object.entries(N)){if(i.inUse.has(e))continue;const n=new v(t*qn.hands[0],qn.hands[1],qn.floor);At(i,e,1,i.withinReach(e,n,.97),new v(.6,1,0)),i.face(`hand_${e}`,{x:-80})}}const Kt={feet:[.32,-.8,qn.floor+.33],hands:[.78,-.05],nod:-4,floor:qn.floor,free:.4,lean:{tilt:12,out:1,knee:[0,-.2,.12]}};function zb(i){Zh(i),oe(i,{nod:Kt.nod}),i.leanWay&&i.bendAbove("spine",{y:i.leanWay*Kt.lean.tilt})}function Hb(i){for(const[n,s]of Object.entries(N)){const[r,o,a]=Kt.feet;i.step(n,new v(s*r,o,a),new v(0,-1,1))}const e=i.leanWay,t=Math.sign(Ci(i.facing));for(const[n,s]of Object.entries(N))i.inUse.has(n)||(e&&s!==e?Fa(i,n):e?Oa(i,n,Kt.lean.out):!t||s===t?Oa(i,n,Kt.hands[0]):i.head(`hand_${n}`,i.matrix(`hand_${n}`)).z<Kt.floor+Kt.free&&Fa(i,n))}function Oa(i,e,t){const n=new v(N[e]*t,Kt.hands[1],Kt.floor);At(i,e,1,i.withinReach(e,n,.97),new v(1,.3,0)),i.face(`hand_${e}`,{x:-80})}function Fa(i,e){const t=i.head(`shin_${e}`,i.matrix(`shin_${e}`)).add(new v(...Kt.lean.knee));At(i,e,1,i.withinReach(e,t,.97),new v(1,.3,0)),i.face(`hand_${e}`,{x:-80})}function Gb(i){for(const[e,t]of Object.entries(N))i.turn(`thigh_${e}`,{x:-66,z:i.kneesApart?t*Db:0}),i.bend(`shin_${e}`,Ib+t*9*i.sway),i.turn(`foot_${e}`,{x:-t*5*i.sway+(e==="r"?i.tap:0)})}function Kn(i,e){i.posture==="stand"&&(i.lift("root",{z:-e}),Ir(i,e))}function oc(i,e,t,n,s=_p){xe(i,e,[...e.free]);for(const r of e.free)At(i,r,t,i.carried(new v(N[r]*n[0],n[1],n[2])),new v(...s))}const Sp={hearts:{open:1,tint:null,hearts:!0},amused:{open:.3,tint:[1,.85,.4]},startled:{open:1.5,tint:[1,1,1]},worried:{open:.7,tint:[.6,.75,1]},angry:{open:.45,tint:[1,.35,.3]},reading:{open:.8,tint:null},admiring:{open:1.2,tint:[1,.86,.5]},serene:{open:.35,tint:[1,.93,.62]}},Yd={open:.42,cycles:6};function Ep(i,e,t){i.shutEyes(nt(1,Yd.open,t)),t>.5&&i.tintEyes(new Ve().setHSL(e*Yd.cycles%1,1,.6).toArray())}function Ze(i,e,t=1){const{open:n,tint:s,shape:r}=Sp[e];i.shutEyes(nt(1,n,t)),s&&t>.5&&i.tintEyes(s),r&&i.shapeEyes(r,t)}const Ea=[.3,-.45,2],Vb=[.46,-.82,2.04];function Wb(i,e,t){const n=He(t,.55,.75),s=(1-n)*Te(t,6);fe(i,0),oe(i,{lean:6,nod:20-4*n,turn:2*Te(t)}),oc(i,e,1,[Ea[0],Ea[1],Ea[2]+.035*s]),i.holdLaptop(),Ze(i,"reading")}function Xb(i,e,t){const n=Dt(t,ie.joy.frames),s=Math.max(Math.sin(2*Math.PI*ie.joy.jumps*at(n,.06,.94)),0)*(1-.3*n);i.lift("root",{z:.32*s}),fe(i,0),oe(i,{lean:-5*s,nod:-14+4*s}),Zn(i,e,0,70+55*s,6*Te(t,4)),as(i,.5*s)}function qb(i,e,t){const n=Dt(t,28),s=Q(n,0,.2)*(1-Q(n,.82,1)),r=He(n,.28,.82);fe(i,0),oe(i,{lean:4*s,nod:10*s,turn:24*r*Te(at(n,.28,.82),1.5)}),oc(i,e,s,Vb);for(const o of e.free)i.face(`hand_${o}`,{z:-N[o]*90*s});Ze(i,"worried",s)}function $b(i,e,t){const n=Dt(t,24),s=He(n,.05,.9);fe(i,0),oe(i,{lean:-10*s,nod:-10*s}),Zn(i,e,0,100*s),i.shutEyes(1-.9*He(n,.2,.75))}function Tp(i,e,t,n){i=(i%1+1)%1;const s=e*t;if(i<t)return[-s/2+e*i,0];const r=(i-t)/(1-t);return[s/2-s*Yn(r),n*Math.sin(Math.PI*r)]}function ac(i,e,t,n,s,r=0){const o=i.rig.heads.get(`thigh_${e}`),a=i.rig.heads.get(`shin_${e}`),c=i.rig.heads.get(`foot_${e}`),l=o.z-a.z,h=a.z-c.z,u=l+h+s-n,d=(t*t+u*u-l*l-h*h)/(2*l*h);if(d<-1-1e-10||d>1+1e-10)throw new RangeError(`${e} stride target is outside the unchanged leg reach`);const f=Math.acos(Math.round(d*1e10)/1e10),m=Math.atan2(t,u)-Math.atan2(h*Math.sin(f),l+h*Math.cos(f));i.turn(`thigh_${e}`,{x:m*180/Math.PI}),i.bend(`shin_${e}`,f*180/Math.PI),i.face(`foot_${e}`,{x:r})}function cc(i,e,t,n,{running:s=!1,lean:r=s?10:3,clearance:o,apart:a=[],drop:c=0,bend:l={},behind:h=0}={}){const[u,d,f]=s?Kh:Qi,m=t%.5,_=s&&m>d?Math.max(0,Math.sin(Math.PI*(m-d)/(.5-d))):0,g=n*(-(s?.075:.11)+(s?.055*_:0))-c;i.lift("root",{z:g}),fe(i,0),oe(i,{...l,lean:r*n+(l.lean??0),nod:(s?-6:-2)*n+(l.nod??0)});const p=(s?24:14)*Te(t)*n,y=e.carried??e.busy,M=Object.keys(N).filter(x=>s&&!y.has(x)&&!e.level.has(x)&&!a.includes(x));xe(i,e,[...M,...a],Object.fromEntries(Object.entries(N).map(([x,A])=>[x,y.has(x)?0:A*p])));for(const x of M)jh(i,x,N[x]*p,10+40*n);if(n>0||c||h)for(const[x,A]of[["l",0],["r",.5]]){const[E,P]=Tp(t+A,u,d,o??f),R=(t+A)%1,b=R>=d?(R-d)/(1-d):0,w=(s?14:11)*Math.sin(Math.PI*b)*n;ac(i,x,n*E+h,n*P,g,w)}}function Lr(i,e,t,n,s,r={}){const o=at(t,0,n),a=Yn(o);return i.lift("root",{y:Ua*(1-a)}),cc(i,e,Ua*a/(r.running?Kh:Qi)[0],1-Yn((o-.76)/.24),r),90*(1-Q(t,n,s))}function Eo(i,e,t,n,s,r={}){const o=at(t,n+$d/2,1),a=(o<.3?o*o/.6:o-.15)/.85;return i.lift("root",{y:-Ua*a}),cc(i,e,Ua*a/(r.running?Kh:Qi)[0],Yn(o/.25),r),s*90*Q(t,n,n+$d)}function Ap(i,e,t,n,s=!1){i.revolve(Lr(i,e,Dt(t,n),wp,bp,{running:s}))}function jb(i,e,t){Ap(i,e,t,40)}function Yb(i,e,t){Ap(i,e,t,28,!0)}const ol={grip:[.32,-.55,2.55],reach:.55,knee:48};function Kb(i,e,t){const n=Math.sin(2*Math.PI*t);fe(i,0),oe(i,{lean:10,nod:-8}),i.putAway(...Mt),xe(i,e,Object.keys(N));const[s,r,o]=ol.grip;for(const[a,c]of Object.entries(N)){const l=(1+c*n)/2;At(i,a,1,i.withinReach(a,i.carried(new v(c*s,r,o+ol.reach*l)),.97),new v(c,.4,-.6)),i.face(`hand_${a}`,{x:-90});const h=ol.knee*(1-l);i.turn(`thigh_${a}`,{x:-h}),i.turn(`shin_${a}`,{x:h*1.2})}}function Zb(i,e,t){if(!Fb("pull_ups",e)){sc(i,e,t);return}Rp(i,e,t,{pull:.5-.5*Math.cos(2*Math.PI*t),swing:0})}const Kd=i=>(e,t,n)=>Rp(e,t,n,{pull:0,swing:Te(n),grips:[i]});function Rp(i,e,t,{pull:n,swing:s,grips:r=Object.keys(N)}){const o=r.filter(a=>e.free.has(a));i.lift("root",{y:rl.back,z:rl.up+rl.rise*n}),oe(i,{nod:-3*n,turn:2*s}),xe(i,e,o);for(const[a,c]of Object.entries(N))i.turn(`thigh_${a}`,{x:-8+7*s*c}),i.bend(`shin_${a}`,18+8*s*c),i.turn(`foot_${a}`,{x:-10}),o.includes(a)&&(i.reach(a,new v(c*Nb,0,Ub),Ob),i.face(`hand_${a}`,{x:-90}))}const Jb=36,Qb=28,$r=.5,Zd=.36,eS=16,tS=7,Jd=-2.45,Qd=-1.54,al=new v(1,-.6,.02),nS=new v(1,-1,-1),fh=new v(0,1,0),iS={y:-15,z:-10,bend:15},sS=.97,To=new v(..._p),es=.24,Cp=.1,rS=6.04,oS=10.36,da=.52,jr=.42,ef=.6,aS={y:60,z:-10,bend:15},Pp=60,Lp=45,Ip={y:30,z:-25,bend:10},cS={y:0,z:-15,bend:0};function ln(i,e,t,{y:n=Ps,x:s=0,z:r=0,bend:o=10}){const a=N[e];i.turn(`upper_arm_${e}`,{y:a*nt(Ps,n,t)}),i.turn(`upper_arm_${e}`,{x:s*t}),i.turn(`upper_arm_${e}`,{z:a*r*t}),i.bend(`forearm_${e}`,nt(10,o,t))}function At(i,e,t,n,s){const r=i.head(`upper_arm_${e}`,i.standing(`upper_arm_${e}`)),o=i.withinReach(e,n,.999999).clone().sub(r),c=new v(N[e]*Math.cos(Xe(Ps)),0,-Math.sin(Xe(Ps))).lerp(o.clone().normalize(),t).normalize();i.reach(e,r.clone().add(c.multiplyScalar(nt(sS,o.length(),t))),fh.clone().lerp(s,t))}const Ao=i=>new v(N[i]*tl[0],tl[1],tl[2]);function Ir(i,e){for(const t of Object.keys(N))ac(i,t,0,0,-e)}function lS(i,e,t){[...e.level].sort().forEach((n,s)=>{const r=Math.max(t-.05*s,0);i.turn(`hand_${n}`,{x:eS*jd(r,3,2.5),y:N[n]*tS*jd(r,2.5,3)})})}const Dp=(i,e)=>e.reduce((t,n)=>t+He(i,n,n+.05),0),Dr=i=>[...i.carried].filter(e=>!i.busy.has(e));function hS(i,e,t){const n=He(t,$r,$r+.22),s=Lr(i,e,t,$r,$r+.14,{running:!0,lean:15,drop:.12*n,bend:{lean:-7*n,nod:5*n}});lS(i,e,at(t,$r,1)),i.revolve(s)}function uS(i,e,t){const n=He(t,0,Zd);i.revolve(Eo(i,e,t,Zd,-1,{bend:{lean:30*n,nod:24*n}}))}function dS(i,e,t){const n=at(t,.55,.72),s=t<.72?0:es*(1-Q(t,.84,1)),r=t<.55?nt(-4.4,Jd,Q(t,0,.16))+(Qd-Jd)*Q(t,.3,.55):t<.72?nt(Qd,-es,n)+1.2*Math.sin(Math.PI*n):-s;i.lift("root",{z:r}),fe(i,0),oe(i,{turn:25*Math.sin(2*Math.PI*at(t,.06,.2)),lean:14*(s/es)+8*Q(t,.3,.55)*(1-n),nod:-10*He(t,.86,1)});const o=t>=.2&&t<.55?Q(t,.2,.27):0,a=He(t,.55,.74);xe(i,e,o||a?Object.keys(N):[]);for(const c of Object.keys(N))o?(At(i,c,o,new v(N[c]*al.x,al.y,al.z),nS),i.face(`hand_${c}`,{z:-N[c]*90*o})):a&&ln(i,c,a,iS);Ir(i,t<.72?nt(0,es,n)+Cp*Math.sin(Math.PI*n):s)}function fS(i,e,t){const n=at(t,.3,1),s=Q(t,.05,.3),r=Q(t,.3,.42);i.lift("root",{y:-2.4*n,z:t<.3?-es*s:-es+rS*n-oS*n*n}),fe(i,0),oe(i,{lean:15*s*(1-r),nod:18*s*(1-r)});for(const o of Object.keys(N))ln(i,o,s,{y:nt(Ps,-15,r),x:nt(40,0,r),z:-10*r,bend:10});Ir(i,t<.3?es*s:es*(1-r)+2*Cp*He(t,.36,.62)),i.revolve(-35*Q(t,0,.2))}function pS(i,e,t){const n=[...e.busy],s=Dr(e),r=1-Q(t,.7,.92),o=He(t,da,da+.2),a=Lr(i,e,t,da,da+.14,{running:!0,lean:14,apart:[...n,...s],drop:.14*o,bend:{lean:-6*o}});n.forEach(c=>ln(i,c,r,aS)),s.forEach(c=>ln(i,c,r,Ip)),i.shutEyes(1-.45*r),i.revolve(a)}function mS(i,e,t){const n=Dr(e),s=Q(t,0,.12)*(1-Q(t,.24,.34)),r=Eo(i,e,t,.34,-1,{clearance:.18,lean:0,apart:s?n:[],bend:{nod:10*He(t,.1,.26)}});s&&n.forEach(o=>At(i,o,s,Ao(o),To)),i.revolve(r)}function gS(i,e,t){const n=Ke(e),s=Q(t,jr,jr+.04)*(1-Q(t,.62,.7)),r=6*at(t,jr,.7),o=-.05*s*Math.abs(Te(r)),a=Q(t,.7,.76)*(1-Q(t,.9,.98)),c=Dp(t,[.77,.83]);i.lift("root",{z:o});const l=Lr(i,e,t,jr,jr+.1,{running:!0,lean:6,apart:a?[n]:[],bend:{nod:7*c,lean:2*c}});if(a&&At(i,n,a,Ao(n),To),s)for(const[h,u]of[["l",0],["r",.5]])ac(i,h,0,.22*s*Math.max(Te(r+u),0),o);i.shutEyes(1-.6*c),i.revolve(l)}function _S(i,e,t){const n=Ke(e),s=Q(t,0,.06)*(1-Q(t,.2,.26)),r=Q(t,.26,.32)*(1-Q(t,.42,.5)),o=Dp(t,[.07,.13]),a=Eo(i,e,t,.4,N[n],{running:!0,lean:6,apart:s||r?[n]:[],bend:{nod:7*o,lean:2*o}});s&&At(i,n,s,Ao(n),To),r&&ln(i,n,r,cS),i.shutEyes(1-.6*o),i.revolve(a)}function xS(i,e,t){const n=Q(t,.72,.8)*(1-Q(t,.9,.98)),s=He(t,.78,.92),r=[...e.level].sort(),o=Lr(i,e,t,ef,ef+.12,{apart:n?r:[],bend:{nod:-8*s}});n&&Hp(i,e,n,s),i.shutEyes(1-.7*s),i.revolve(o)}function vS(i,e,t){const n=Ke(e),s=Q(t,0,.08)*(1-Q(t,.24,.32)),r=Eo(i,e,t,.3,N[n],{apart:s?[n]:[],bend:{tilt:-N[n]*5*s}});s&&ln(i,n,s,{y:0,x:-85,z:pp,bend:mp+gp*Te(at(t,0,.32),2)}),i.revolve(r)}function yS(i,e,t){i.revolve(Lr(i,e,t,wp,bp))}function MS(i,e,t){i.revolve(Eo(i,e,t,0,-1))}const wS={bare:yS,butler:hS,homie:dS,squire:pS,coach:gS,colleague:xS},bS={bare:MS,butler:uS,homie:fS,squire:mS,coach:_S,colleague:vS};function SS(i,e,t){wS[e.voice](i,e,Dt(t,Jb))}function ES(i,e,t){bS[e.voice](i,e,Dt(t,Qb))}const TS=.2,fa={sweep:14,lean:10,nod:16,turn:70},tf=(i,e,t)=>i.clone().add(e.clone().sub(i).setLength(t)),AS=1.4,nf=.13;function RS(i){return Q(i,0,.22)-2*Q(i,.32,.62)+Q(i,.7,.85)}function CS(i,e,t){const n=N[Ke(e)],s=RS(t);Kn(i,TS),fe(i,0),oe(i,{lean:fa.lean,nod:fa.nod,turn:n*fa.sweep*s}),xe(i,e),Ze(i,"reading"),i.posture==="stand"&&i.revolve(n*fa.turn)}const xs={depth:.3,ahead:[1.6,.3,.2],out:1.25,share:.8,lean:8,size:1.2};function PS(i,e){return i.at?new v((i.at.x-.5)*Gt,e,Fn+(.5-i.at.y)*Gt).applyAxisAngle(new v(0,0,1),Xe(-i.facing)):null}function LS(i,e,t){const{wall:n,contact:s,tilt:r,hip:o,inner:a,outer:c}=ie.lean,l=i.leanWay||1,h=l===N.l?"l":"r",u=h==="l"?"r":"l";i.turn(`thigh_${h}`,{y:N[h]*a}),i.turn(`thigh_${u}`,{y:N[u]*c,x:-12});const d=new Map(Object.keys(N).map(_=>{const g=i.head(`foot_${_}`,i.matrix(`foot_${_}`));return g.z=i.rig.heads.get(`foot_${_}`).z,[_,g]})),f=l*r*(1+.06*Te(t));i.lift("root",{z:-.12}),i.turn("root",{y:f}),fe(i,t),oe(i,{tilt:-f*.4});for(const[_,g]of d)i.step(_,g,new v(0,-1,0)),i.face(`foot_${_}`,{});xe(i,e,[h,...e.free.has(u)?[u]:[]]),At(i,h,1,i.withinReach(h,i.carried(new v(l*n*Gt,0,s)),.99),new v(l,.2,-1)),i.face(`hand_${h}`,{z:-N[h]*90});const m=new v(N[u]*o[0],o[1],o[2]).applyAxisAngle(new v(0,1,0),Xe(f));e.free.has(u)&&At(i,u,1,i.withinReach(u,i.carried(m),.97),new v(N[u],.3,0)),Ze(i,"amused",.4)}function IS(i,e,t){const n=i.rig.eyes.reduce((x,A)=>x.add(A),new v).divideScalar(i.rig.eyes.length),s=n.clone().applyMatrix4(i.matrix("head")),[r,o,a]=xs.ahead,c=PS(i,xs.depth)??s.clone().add(new v(N[Ke(e)]*r,o,a)),l=Math.sign(c.x-s.x),h=l?l>0?"l":"r":Ke(e);fe(i,t),oe(i,{tilt:-N[h]*xs.lean}),xe(i,e,[h]);const u=n.applyMatrix4(i.matrix("head")),d=c.clone().sub(u),f=yt.radToDeg(Math.atan2(d.x,-d.y)),m=yt.radToDeg(Math.atan2(-d.z,Math.hypot(d.x,d.y))),_=new v(0,0,1).applyMatrix4(On(m,0,f)),g=x=>{const A=i.carried(x.clone().addScaledVector(_,-(yo.handle/2+yo.radius)*xs.size));return i.withinReach(h,A,.97).distanceTo(A)<.02},p=Math.min(xs.out,d.length()*xs.share),y=Array.from({length:8},(x,A)=>p*(1-A/10)),M=tf(u,c,y.find(x=>g(tf(u,c,x)))??y.at(-1));Gp(i,h,1,M,0,{tip:m,roll:0,slant:f,size:xs.size}),Ze(i,"reading")}const Ct={intro:12,hold:48,outro:12,fps:12,ready:3,opens:11,pageEvery:24,pageFrom:12,pageTo:20,lines:4,referenceArm:.985,forward:.68,drop:.3,drawDrop:.18,elbow:[1,-1,-1],wristTurn:90},ph=Ct.intro+Ct.hold+Ct.outro,hn={grip:.34,forward:.02},z={intro:8,hold:32,outro:8,fps:12,yawnFrames:28,pastimeFrames:40,greetingFrames:24,hopFrames:20,stumbleFrames:24,elbow:[1,-.15,-.35],wrist:[.72,-.72,1.76],supportLift:.22,whistleLift:.25,clothLift:.2,clothTurn:-90,compactFps:6,tap:10,rock:3,turn:12,nod:8,writeStroke:.035,writeHeight:.02,glance:22,hop:.18,stumble:12,writingWrist:[.38,-.76,2.1],yawnWrist:[.48,-.86,2.12],whistleWrist:[.48,-.82,2.2],sipWrist:[.7,-.63,2.17],shieldWrist:[.22,-.64,2.13],wipeWrist:[.1,-.7,1.9],saluteWrist:[1.28,-.32,2.59],gestureIn:.2,gestureOut:.8,yawnEyes:.94,yawnSpan:[.08,.92],pastimeSpan:[.3,.7],whistleEyes:.65,sipEyes:.5,sipTip:12,grooveEyes:.4,beats:4,sways:2,wipes:3,wipeLift:.035,wipeAcross:.04,bowLean:18,bowNod:10,leapSpan:[.18,.78],catchSpan:[.15,.45],recoverSpan:[.45,.85],recover:.3},Np={butler:"writing_stylus",coach:"writing_pencil",colleague:"writing_pen",homie:"writing_marker",squire:"writing_quill"},Ba=z.intro+z.hold+z.outro,pn={intro:8,hold:144,outro:8,whistleSpan:[.7,.98],beats:12,sways:3},mh=pn.intro+pn.hold+pn.outro,Ta={across:.04,top:.52,bottom:.44,forward:[0,-1,0]};function Up(i){const e=i*Ba,t=e>=z.intro&&e<z.intro+z.hold,n=e<z.intro?e:Ba-1-e;return{frame:e,held:t,ready:t?1:Q(n,0,z.intro-1),phase:t?(e-z.intro)/z.hold:0}}function DS(i){const e=i*mh,t=e>=pn.intro&&e<pn.intro+pn.hold,n=e<pn.intro?e:mh-1-e;return{ready:t?1:Q(n,0,pn.intro-1),phase:t?(e-pn.intro)/pn.hold:0}}function kn(i,e){const t=Dt(i,e);return{u:t,ready:Q(t,0,z.gestureIn)*(1-Q(t,z.gestureOut,1))}}function NS(i,e,t=[0,0,0]){return i.rig.heads.get(`hand_${e}`).clone().add(new v(N[e]*(hn.grip+t[0]),hn.forward+t[1],t[2])).applyMatrix4(i.matrix(`hand_${e}`))}function Bn(i,e,t,n,s={}){t&&(Ds(i,e),os(i,e,t,i.carried(new v(N[e]*n[0],n[1],n[2])),{z:-N[e]*90,...s}))}function Ds(i,e){var r;for(const o of["upper_arm","forearm","hand"])i.final.delete(`${o}_${e}`);const{stance:t,swing:n,level:s}=i.restArms;if(s.has(e))return vp(i,e);jh(i,e,n[e]??0),(r=t.shield)!=null&&r.has(e)&&i.turn(`hand_${e}`,{y:-N[e]*Lp,z:N[e]*Pp})}function os(i,e,t,n,s,r=z.elbow){const o=["upper_arm","forearm","hand"].map(h=>`${h}_${e}`),a=new Map(o.map(h=>[h,i.matrix(h).clone()]));i.reach(e,i.withinReach(e,n,.999999),new v(...r));const c=new Map(o.map(h=>[h,i.matrix(h).clone()]));for(const h of o.slice(0,2)){const u=i.head(h,i.standing(h)),d=new It().setFromRotationMatrix(new ge().extractRotation(a.get(h))),f=new It().setFromRotationMatrix(new ge().extractRotation(c.get(h))),m=Ln(u).multiply(new ge().makeRotationFromQuaternion(d.slerp(f,t))).multiply(Ln(i.rig.heads.get(h).clone().negate()));i.setMove(h,m)}const l=s??new It().setFromRotationMatrix(new ge().extractRotation(c.get(o[2])));Jh(i,e,t,l,a.get(o[2]))}function Jh(i,e,t,n,s=i.matrix(`hand_${e}`)){const r=`hand_${e}`,o=i.head(r,i.standing(r)),a=new v,c=new It,l=new v;s.decompose(a,c,l);const{x:h=0,y:u=0,z:d=0}=n,f=n.isQuaternion?n:new It().setFromRotationMatrix(On(h,u,d)),m=new ge().compose(o,c.slerp(f,t),l).multiply(Ln(i.rig.heads.get(r).clone().negate()));i.setMove(r,m)}function Op(i,e,t,n){const s=`hand_${e}`,r=i.matrix(s).clone();i.aim(s,n);const o=new It().setFromRotationMatrix(new ge().extractRotation(i.matrix(s)));Jh(i,e,t,o,r)}function Ro(i,e,t,n,s,r,o=0){if(!t)return;const a=N[e],c=i.matrix("head"),l=new It().setFromRotationMatrix(new ge().extractRotation(c)).multiply(new It().setFromRotationMatrix(On(s.x??0,s.y??0,s.z??0))),h=new v(a*n[0],n[1],n[2]).applyMatrix4(c).sub(r.clone().applyQuaternion(l));o&&i.lift(`shoulder_${e}`,{z:o*t}),US(i,e),os(i,e,t,h,l,[1,-.35,-.6]),i.inUse.add(e),i.headContact=Math.max(i.headContact,t)}function US(i,e){if(Ds(i,e),i.posture==="lounge"){const t=new v(N[e]*qn.hands[0],qn.hands[1],qn.floor);At(i,e,1,i.withinReach(e,t,.97),new v(.6,1,0)),i.face(`hand_${e}`,{x:-80})}else if(i.posture==="composed"){const t=N[e],n=Math.sign(Ci(i.facing)),[s,r,o]=Kt.feet;i.step(e,new v(t*s,r,o),new v(0,-1,1)),i.leanWay&&t!==i.leanWay?Fa(i,e):i.leanWay?Oa(i,e,Kt.lean.out):!n||t===n?Oa(i,e,Kt.hands[0]):i.head(`hand_${e}`,i.matrix(`hand_${e}`)).z<Kt.floor+Kt.free&&Fa(i,e)}}function Fp(i,e,t){const n=N[e];Ro(i,e,t,[.1,-1,2.67],{y:-n*55,z:-n*110},new v(n*hn.grip,hn.forward,0))}const ka=65,sf={down:35,up:25};function Bp(i,e){const t=i.rig.eyes.reduce((s,r)=>s.add(r),new v).divideScalar(i.rig.eyes.length),n=e.clone().sub(i.head("head",i.standing("head")));return Im(n.x,-n.y,n.z,t.z-i.rig.heads.get("head").z)}function kp(i,e,t=1){const n=Bp(i,e),s=yt.clamp(n.pitch,Xe(-sf.up),Xe(sf.down)),r=yt.radToDeg(n.yaw),o=yt.clamp(r,-ka,ka);return i.face("head",{x:yt.radToDeg(s)*t,z:o*t}),i.gaze={target:e.toArray(),forward:Ta.forward},(r-o)*t}function OS(i,e,t){const n=t*ph,s=n>=Ct.intro&&n<Ct.intro+Ct.hold,r=n<Ct.intro?n:ph-1-n,o=s?1:Q(r,0,Ct.ready),a=s?1:Q(r,Ct.ready,Ct.opens),c=s?(n-Ct.intro)%Ct.pageEvery:0,l=s?Q(c,Ct.pageFrom,Ct.pageTo):0;fe(i,0),xe(i,e);const h=Math.min(...Object.keys(N).map(R=>{const b=w=>i.rig.heads.get(`${w}_${R}`);return b("upper_arm").distanceTo(b("forearm"))+b("forearm").distanceTo(b("hand"))}))/Ct.referenceArm,u=Object.keys(N).map(R=>i.head(`upper_arm_${R}`,i.standing(`upper_arm_${R}`))),d=u[0].clone().add(u[1]).multiplyScalar(.5),f=cm(a),m=ts("l",a).add(ts("r",a)).multiplyScalar(.5).applyMatrix4(f),_=new v(d.x-m.x*h,d.z-(Ct.drop+Ct.drawDrop*(1-o))*h-m.y*h,-d.y+Ct.forward*h-m.z*h),g=new ge().makeTranslation(_.x,_.y,_.z).multiply(f).scale(new v(h,h,h));for(const[R,b]of Object.entries(N)){const w=xo(ts(R,a).applyMatrix4(g));if(!o)continue;const L=yt.radToDeg(Math.atan2(Ue.closedGrip*(1-a),Ue.gripBack));os(i,R,o,w,{z:-b*(Ct.wristTurn+L)},Ct.elbow)}const p=c/(Ct.pageEvery/Ct.lines),y=Math.floor(p),M=p-y,x=Q(M,.7,1),A=Q(M,0,.7)*(1-x),E=Math.min((y+x)/(Ct.lines-1),1)*(y===Ct.lines-1?1-x:1),P=new v(nt(-.04,Ta.across,A),nt(Ta.top,Ta.bottom,E),-Ue.pages).applyMatrix4(g);kp(i,xo(P),a),i.holdBook(a,l,s||r>=Ct.ready),Ze(i,"reading",a)}function FS(i,e,t){const{ready:n,phase:s}=DS(t),r=e.voice==="butler",o=He(s,...pn.whistleSpan)*n;fe(i,0),oe(i,{turn:z.turn*n,nod:-z.nod*o/2,lean:z.rock*Te(s,pn.sways)*(r?o:n)}),xe(i,e),i.tap=z.tap*Math.max(Te(s,pn.beats),0)*n,i.posture==="stand"&&i.turn("foot_r",{x:i.tap}),o&&i.shutEyes(1-z.whistleEyes*o)}function zp(i,e,t){const{u:n,ready:s}=kn(t,z.yawnFrames),r=Ke(e);fe(i,0),oe(i,{lean:-z.rock*s,nod:-z.nod*s}),xe(i,e),Fp(i,r,s),s&&i.putAway(...Mt),i.shutEyes(1-z.yawnEyes*He(n,...z.yawnSpan))}function BS(i,e,t){const{u:n,ready:s}=kn(t,z.pastimeFrames),r=He(n,...z.pastimeSpan),o=Ke(e);fe(i,0),oe(i,{lean:-z.rock*r,nod:-z.nod*r}),xe(i,e);const a=xo(new v(...sn.whistle.mouthAt).add(new v(0,0,-sn.whistle.mouthpiece[2]/2))).applyMatrix4(On(0,0,N[o]*90)),c=new v(N[o]*hn.grip,hn.forward,z.whistleLift).add(a);Ro(i,o,s,[.1,-.96,2.66],{z:-N[o]*90},c,.06),s&&i.putAway(...Mt,"coach_whistle"),s>.5&&i.holdProp("hand_whistle",o,[0,0,z.whistleLift],{z:N[o]*90}),i.shutEyes(1-z.whistleEyes*r)}const Bt={frames:120,fps:8,down:[0,.1],up:[.9,1],tunes:[[.3,.45],[.62,.8]],beats:40,pillow:[0,1,3.2],tilt:72,across:-1.6,kneeUp:60,kneeBend:105,glance:40,ankle:[-.15,-.15,-.1],crossedKnee:[1,-.4,.6],footBob:18,wrist:[.6,.55,2.85],fingers:[-1,.4,.4],elbow:[1,-.3,.8],straw:[.14,-.9,.4],strawTip:115,strawWag:8,eyes:.45,whistleEyes:.2},kS=i=>Bt.tunes.reduce((e,[t,n])=>e+He(i,t,n),0);function zS(i,e,t){const n=Dt(t,Bt.frames),s=Q(n,...Bt.down)*(1-Q(n,...Bt.up)),r=kS(n),o=Math.max(Te(n,Bt.beats),0);if(fe(i,0),xe(i,e,s?Object.keys(N):[]),!s)return;i.putAway(...Mt),oe(i,{turn:-Bt.glance*s});for(const[h,u]of Object.entries(N)){const[d,f,m]=Bt.wrist;Ds(i,h),os(i,h,s,new v(u*d,f,m),null,Bt.elbow);const[_,g,p]=Bt.fingers;Op(i,h,s,new v(u*_,g,p))}i.turn("thigh_l",{x:-Bt.kneeUp*s}),i.bend("shin_l",Bt.kneeBend*s);const a=i.head("shin_l",i.matrix("shin_l")),c=i.head("foot_r",i.standing("foot_r"));i.step("r",c.lerp(a.add(new v(...Bt.ankle)),s),new v(...Bt.crossedKnee)),i.turn("foot_r",{x:-Bt.footBob*r*o}),i.wearProp("straw",Bt.straw,{x:Bt.strawTip+Bt.strawWag*(1+r)*Te(n,9)});const l=new v(...Bt.pillow);i.turnAll({x:-Bt.tilt*s},l),i.turnAll({z:90*s},l),i.offsetAll([Bt.across*s,-l.y*s,-l.z*s]),i.shutEyes(nt(1,nt(Bt.eyes,Bt.whistleEyes,r),s))}const cl=[1.781,-.22,2.360018];function Hp(i,e,t,n){if(t)for(const s of e.level){const r=new v(N[s]*cl[0],cl[1],cl[2]).sub(i.rig.heads.get(`hand_${s}`));Ro(i,s,t,[.18,-.96,2.66],{y:-N[s]*z.sipTip*n,z:-N[s]*90},r)}}function HS(i,e,t){const{u:n,ready:s}=kn(t,z.pastimeFrames);fe(i,0),oe(i,{nod:-z.rock*s}),xe(i,e),Hp(i,e,s,He(n,...z.pastimeSpan)),i.shutEyes(1-z.sipEyes*He(n,...z.pastimeSpan))}function GS(i,e,t){const{u:n,ready:s}=kn(t,z.pastimeFrames);fe(i,0),oe(i,{nod:z.nod*Te(n,z.beats)*s,tilt:z.rock*Te(n,z.sways)*s}),xe(i,e),i.swing(Te(n,z.sways)*s),i.shutEyes(1-z.grooveEyes*s)}function VS(i,e,t){const{u:n,ready:s}=kn(t,z.pastimeFrames),r=[...e.shield][0];if(!r)return sc(i,e,t);const o=r==="l"?"r":"l";fe(i,0),oe(i,{nod:z.nod*s}),xe(i,e),Bn(i,r,s,z.shieldWrist),Bn(i,o,s,[z.wipeWrist[0],z.wipeWrist[1]+z.wipeAcross*Te(n,z.wipes),z.wipeWrist[2]+z.wipeLift*Te(n,z.wipes*2)]),s&&(i.putAway("squire_quill"),i.keep.add("squire_shield")),s>.5&&i.holdProp("polishing_cloth",o,[0,0,z.clothLift],{x:z.clothTurn})}function WS(i,e,t){const{ready:n,phase:s}=Up(t),r=z.writeStroke*Te(s,z.beats);if(fe(i,0),oe(i,{nod:z.nod*n,lean:z.rock*n}),xe(i,e),Bn(i,"l",n,z.wrist),Bn(i,"r",n,[z.writingWrist[0]+r,z.writingWrist[1],z.writingWrist[2]]),n&&i.putAway(...Mt),n>=1){const o=e.voice==="butler",a=sn.paper.thickness*(o?2.5:.5),c=z.wrist[2]+z.supportLift+a+sn.pen.length/2+sn.pen.tip-z.writingWrist[2];i.holdProp(Np[e.voice]||"writing_pen","r",[0,0,c],{z:-90}),i.holdProp(e.voice==="butler"?"writing_tablet":"writing_paper","l",[0,-z.wrist[0],z.supportLift],{z:90})}Ze(i,"reading",n)}function XS(i,e,t){const{ready:n,phase:s}=Up(t);fe(i,0),oe(i,{nod:z.nod*n}),xe(i,e),Bn(i,"l",n,z.wrist),Bn(i,"r",n,[z.wrist[0]+z.writeStroke*Te(s,z.sways),z.wrist[1],z.wrist[2]+z.writeHeight*Math.max(Te(s,z.sways),0)]),n&&i.putAway(...Mt),n>=1&&(i.holdProp("papers","l",[0,-z.wrist[0],z.supportLift],{z:90}),i.props.get("papers").phase=s)}function qS(i,e,t){const{ready:n}=kn(t,z.greetingFrames);fe(i,0),oe(i,{lean:z.bowLean*n,nod:z.bowNod*n}),xe(i,e),n&&i.putAway(...Mt)}function $S(i,e,t){const{ready:n}=kn(t,z.greetingFrames),s=Ke(e);fe(i,0),oe(i,{nod:-z.rock*n}),xe(i,e);const r=N[s];Ro(i,s,n,[1,-.1,3.5],{y:-r*117},new v(r*hn.grip,hn.forward,0),.32),n&&i.putAway(...Mt)}function jS(i,e,t){const{u:n,ready:s}=kn(t,z.hopFrames),r=He(n,...z.leapSpan);Kn(i,z.hop*He(n,0,z.leapSpan[0])),i.lift("root",{z:z.hop*r}),fe(i,0),oe(i,{lean:-z.rock*r}),Zn(i,e,0,tc*r),i.posture==="stand"&&as(i,r),Ze(i,"startled",s)}function YS(i,e,t){const{u:n,ready:s}=kn(t,z.stumbleFrames),r=He(n,...z.catchSpan)-z.recover*He(n,...z.recoverSpan);fe(i,0),oe(i,{lean:z.stumble*r,tilt:z.rock*r}),Zn(i,e,0,tc*s),Ze(i,"startled",Math.max(r,0))}function KS(i,e,t){const{ready:n}=kn(t,z.greetingFrames);fe(i,0),oe(i,{turn:z.glance*n,nod:-z.rock*n}),xe(i,e)}const gt={blows:1,blowFrames:8,fps:10,lands:.3,prepare:.08,contact:.34,rebound:.46,poised:.94,bounce:.035,snap:50,thumb:90,roll:-90,fist:.62,turn:80,strike:.432,landsAt:[.72,-1.81]};function ZS(i){const e=(i*gt.blows%1+1)%1;return e<gt.prepare?nt(gt.poised,1,Yn(e/gt.prepare)):e<gt.lands?nt(1,gt.strike,at(e,gt.prepare,gt.lands)**2):e<gt.contact?gt.strike:e<gt.rebound?gt.strike+gt.bounce*Math.sin(Math.PI*at(e,gt.contact,gt.rebound))**2:nt(gt.strike,gt.poised,Yn(at(e,gt.rebound,1)))}function eA(i){const e=N[Ke(i)],[t,n]=gt.landsAt,s=Xe(e*gt.turn);return(e*t*Math.cos(s)-n*Math.sin(s))/Gt}function JS(i,e,t){const n=Ke(e),s=Math.max(ZS(t),gt.strike),r=1-s,o=(t*gt.blows%1+1)%1,a=Math.sin(Math.PI*at(o,0,gt.prepare))**2,c=He(o,gt.lands,gt.rebound);Kn(i,.04*r),fe(i,0),oe(i,{lean:8+6*r-2*a,nod:9+2*c}),xe(i,e,[n]),ln(i,n,1,{y:nt(75,5,s),z:-35,bend:nt(15,70,s)}),i.roll(`forearm_${n}`,N[n]*gt.roll),i.clench(n,gt.fist),i.holdProp("work_hammer",n,[0,0,0],{x:gt.thumb,z:N[n]*gt.snap*r}),i.posture==="stand"&&i.revolve(N[n]*gt.turn)}const Jt={frames:60,fps:12,out:[0,.08],along:[.08,.76],pause:[.76,.9],away:[.92,1],turn:65,bend:.35,lean:34,nod:22,nodded:10,box:[.72,-1.81,1.2],between:.5,front:-1.2,sweep:.4,size:1.45,tip:35,slant:-35};function QS(i){const[e,t,n]=Jt.box;return new v(i*e,t,n).applyAxisAngle(new v(0,0,1),Xe(i*gt.turn))}function e1(i,e,t){const n=QS(e),s=new v(n.x-i.x,0,n.z-i.z).normalize();return{lens:new v(nt(i.x,n.x,Jt.between)+Jt.sweep*t,Jt.front,nt(i.z,n.z,Jt.between)),way:s}}function Gp(i,e,t,n,s,{tip:r,roll:o,slant:a,size:c}){const l=new v(0,0,1).applyMatrix4(On(r,o,a)),h=n.clone().addScaledVector(l,-(yo.handle/2+yo.radius)*c).applyAxisAngle(new v(0,0,1),-s);At(i,e,t,i.withinReach(e,i.carried(h),.97),new v(...z.elbow)),i.putAway(...Mt),!(t<=.3)&&(i.holdUpright("magnifying_glass",e,[0,0,0],{x:r,y:o,z:a-yt.radToDeg(s)}),Object.assign(i.props.get("magnifying_glass"),{magnifies:t,size:c,roll:o}))}function t1(i,e,t){const n=Ke(e),s=N[n],r=ne(t,Jt.out)*(1-ne(t,Jt.away)),o=Math.sin(2*Math.PI*at(t,...Jt.along)),a=He(t,...Jt.pause),c=new v(0,0,1),l=Xe(s*Jt.turn);Kn(i,Jt.bend*r),fe(i,0),oe(i,{lean:Jt.lean*r,nod:(Jt.nod+Jt.nodded*a)*r}),xe(i,e,[n]);const h=i.rig.eyes.reduce((m,_)=>m.add(_),new v).divideScalar(i.rig.eyes.length).applyMatrix4(i.matrix("head")),{lens:u,way:d}=e1(h.applyAxisAngle(c,l),s,o),f=yt.radToDeg(Math.atan2(d.x,d.z));Gp(i,n,r,u,l,{tip:Jt.tip,roll:f,slant:s*Jt.slant,size:Jt.size}),Ze(i,"reading",r),i.posture==="stand"&&i.revolve(s*Jt.turn)}const Ki={step:.6,hop:.12,lean:8,shadeWrist:[1.18,-.5,2.72],shadeHand:[-.35,-1,.2]},za=-1.2,tA=Math.abs(za)/Gt,nA=i=>.5-(i.rig.heads.get("head").z-Fn)/Gt,iA=i=>(i.rig.eyes.reduce((e,t)=>e+t.z,0)/i.rig.eyes.length-i.rig.heads.get("head").z)/Gt;function n1(i,e,t=0){const n=new v((e.x-.5)*Gt,e.behind?-za:za,Fn+(.5-e.y)*Gt),s=h=>n.clone().applyAxisAngle(new v(0,0,1),Xe(-(t+h))),r=e.most??1/0,o=e.faces&&i.posture==="stand"?Math.min(Math.max(yt.radToDeg(Bp(i,s(0)).yaw),-r),r):0,a=i.matrix("head").clone(),c=o+kp(i,s(o)),l=e.amount??1;return l<1&&i.final.set("head",i1(a,i.matrix("head"),l)),c*l*l}function i1(i,e,t){const[n,s]=[i,e].map(r=>{const o={at:new v,turn:new It,size:new v};return r.decompose(o.at,o.turn,o.size),o});return new ge().compose(n.at.lerp(s.at,t),n.turn.slerp(s.turn,t),n.size.lerp(s.size,t))}function s1(i,e,t){const{shade:n,back:s}=i.sky??{shade:0,back:0};i.lift("root",{y:Ki.step*s,z:Ki.hop*Math.sin(Math.PI*s)}),fe(i,t),oe(i,{lean:-Ki.lean*s});const r=Ke(e);if(xe(i,e,n?[r]:[]),n){Bn(i,r,n,Ki.shadeWrist);const[o,a,c]=Ki.shadeHand,l=`hand_${r}`,h=i.rig.along.get(l).clone().transformDirection(i.matrix(l));i.aim(l,h.lerp(new v(N[r]*o,a,c),n)),i.putAway(...Mt)}}const bn={lean:34,nod:-42,drop:.25,behind:.2,hands:[.42,-1.3,.6],turn:4,intro:9,stride:6,fps:12};function r1(i){const e=i*(bn.intro+bn.stride);return e>=bn.intro?1:Yn((e-bn.turn)/(bn.intro-bn.turn))}function o1(i,e,t){const n=r1(t);cc(i,e,i.stride,i.posture==="walk"?1:0,{lean:0,drop:bn.drop*n,behind:bn.behind*n,bend:{nod:bn.nod*n}}),i.bendAbove("spine",{x:bn.lean*n});const[s,r,o]=bn.hands;for(const[a,c]of Object.entries(N))At(i,a,n,i.withinReach(a,new v(c*s,r,o),.97),new v(...z.elbow)),i.face(`hand_${a}`,{z:-c*90*n});i.putAway(...Mt)}function a1(i,e,t){const n=Ke(e);fe(i,0),oe(i,{nod:-14,lean:-3,tilt:-N[n]*5}),xe(i,e,[n]),ln(i,n,1,{y:-12+3*Te(t),z:-15,bend:10}),Ze(i,"worried",.6)}function Zn(i,e,t,n,s=0){xe(i,e,[...e.free]);for(const r of e.free){const o=N[r],a=Math.min(Math.max(n/cb,0),1);ln(i,r,a,{x:t+s*o,y:-Math.min(n,tc),bend:10})}}function as(i,e,t=0){for(const[n,s]of Object.entries(N))i.turn(`thigh_${n}`,{x:-24*e+t*s}),i.turn(`shin_${n}`,{x:44*e}),i.turn(`foot_${n}`,{x:-8*e})}function c1(i,e,t){const n=Dt(t,16),s=Q(n,0,.26)*(1-Q(n,.26,.36)),r=Q(n,.3,.45);i.lift("root",{z:.1*r-.28*s}),fe(i,0),oe(i,{lean:14*s-6*r,nod:-4*r}),Zn(i,e,40*s,80*Q(n,.26,.42)*(1-.4*Q(n,.6,1))),Ir(i,.28*s),as(i,r)}const l1=25,h1=360;function u1(i,e,t){const n=Dt(t,22),s=Q(n,0,.26)*(1-Q(n,.26,.34)),r=Q(n,.3,.86),o=Q(n,.28,.4)*(1-Q(n,.86,.95));i.lift("root",{z:.1*o-.28*s}),fe(i,0),oe(i,{lean:12*s}),Zn(i,e,30*s,l1*o),Ir(i,.28*s),as(i,1.2*o);const a=i.head("chest",i.matrix("chest")).lerp(i.head("neck",i.matrix("neck")),.75);i.turnAll({x:h1*r},a)}function d1(i,e,t){const n=Dt(t,12),s=Q(n,0,.2),r=He(n,0,.3);i.lift("root",{z:.1*s}),fe(i,0),oe(i,{lean:-9*s-8*r,nod:-6*s-10*r,tilt:4*Te(t,3)*s}),Zn(i,e,0,(70+8*Te(t,3))*s+25*r,14*Te(t,3)*s),Ze(i,"startled",Math.max(r,.6*s)),as(i,.5*s,14*Te(t,3)*s)}function f1(i,e,t){const n=Dt(t,_h.frames),s=Q(n,0,.2)*(1-Q(n,.2,1));i.lift("root",{z:-.32*s}),fe(i,0),oe(i,{lean:16*s,nod:8*s}),Zn(i,e,0,38*s),Ir(i,.32*s)}function p1(i,e,t){const n=Dt(t,24),s=AS*(n<.5?Q(n,0,.5):1-Q(n,.5,1)),r=He(n,.4,.6),o=n===0||n===1?0:Yn(Math.sin(Math.PI*n))*(1-.85*r),a=90*Q(n,0,.12)-180*Q(n,.4,.6)+90*Q(n,.88,1),c=Dr(e);cc(i,e,4*n,o,{running:!0,lean:12,apart:c}),c.forEach(l=>ln(i,l,o,Ip)),i.revolve(a),i.offsetAll([s,0,0])}function rf(i,e,t){const n=nf*Math.max(Te(3*t),0)*He(t,0,1);fe(i,0),oe(i,{tilt:8*He(t,0,1),nod:6*He(t,0,1),turn:10*He(t,0,1)}),xe(i,e),ac(i,"r",0,n,0,15*n/nf)}function m1(i,e,t){const n=He(t,0,1);fe(i,0),oe(i,{tilt:14*n,nod:-8*n});for(const s of Object.keys(N))ln(i,s,n,{y:30,z:-15,bend:100})}function g1(i,e,t){const n=Ke(e),s=Q(t,0,.15)*(1-Q(t,.8,1)),r=He(t,.2,.75);fe(i,0),oe(i,{lean:-4*r,nod:-6*r}),xe(i,e,s?[n]:[]),s&&At(i,n,s,Ao(n),To),i.shutEyes(1-.7*r)}function _1(i,e,t){const n=Ke(e),s=Q(t,0,.2)*(1-Q(t,.6,.85));fe(i,0),oe(i,{nod:18*s*(1-Q(t,.35,.5)),turn:-N[n]*8*s}),xe(i,e,s?[n]:[]),s&&At(i,n,s,Ao(n),To)}function x1(i,e,t){const n=Dr(e),s=Q(t,0,.2)*(1-Q(t,.75,1));fe(i,0),oe(i,{tilt:-5*s,nod:4*s}),xe(i,e,s?n:[]),s&&n.forEach(r=>ln(i,r,s,{y:30,z:-25+5*Te(3*t),bend:10}))}const v1={bare:rf,butler:rf,homie:m1,coach:g1,colleague:_1,squire:x1};function y1(i,e,t){v1[e.voice](i,e,Dt(t,20))}const pe={frames:36,fps:12,hatOn:1.101,hatWrist:[1.05,-.2,2.85],hatRaised:[.95,-.5,2.85],hatTip:25,hatFingers:.25,hatBow:22,hatNod:14,monocleWrist:[.55,-.8,2.62],monocleWorn:[.354,-.95,.66],monoclePeer:8,monocleTilt:9,toastWrist:[.78,-.72,2.55],toastClink:.12,sipWrist:[.42,-.78,2.38],sipTip:20,shakaWrist:[1.22,-.25,2.72],shakaWaggle:28,shakaWaggles:3,shadesWrist:[.5,-.82,2.55],shadesWorn:[0,-.96,.66],shadesLean:7,shadesTilt:10,fireWrist:[.48,-.86,2.28],fireSize:2.4,thumbWrist:[.62,-.84,2.3],glassesWrist:[.32,-.8,2.47],peerLean:12,peerTurn:18,prayerWrist:[.12,-.62,2],prayerRoll:180,thanksBow:14,popperWrist:[.95,-.45,2.85],popAt:.4,popHop:.12,flex:{y:0,x:-85,z:15,bend:115},flexPump:15,trophy:{y:-55,x:15,z:0,bend:15},trophyHop:.1,sword:{y:-62,x:18,z:0,bend:12},swordThrust:12,shieldWrist:[.24,-.78,2.3],shieldCrouch:.08,shieldBump:.5,castleWrist:[.55,-.88,2.34]},Co=i=>nc.forEach(e=>i.keep.add(e)),Tn=i=>kn(i,pe.frames);function Fi(i,e,t,n,s={}){Bn(i,e,t,n,{x:-60,...s})}const M1=new v(0,0,1);function w1(i,e,t){const{u:n,ready:s}=Tn(t),r=Ke(e),o=Q(n,.2,.3)*(1-Q(n,.7,.8)),a=Q(n,.3,.4)*(1-Q(n,.6,.7)),c=He(n,.32,.72);if(fe(i,0),oe(i,{lean:pe.hatBow*c,nod:pe.hatNod*c}),xe(i,e,s?[r]:[]),Fi(i,r,s,pe.hatWrist.map((l,h)=>nt(l,pe.hatRaised[h],a))),s&&i.aim(`hand_${r}`,i.rig.along.get(`hand_${r}`).clone().transformDirection(i.matrix(`hand_${r}`)).lerp(M1,s)),o){const l={y:N[r]*pe.hatTip*o};i.putAway("butler_top_hat","butler_top_hat_band"),i.wearProp("top_hat",b1(i,r,o,l).toArray(),l)}Ze(i,"amused",c)}function b1(i,e,t,n){const s=new v(N[e]*(wn.hat.crown+wn.hat.brim),0,0).applyMatrix4(On(0,n.y,0)),o=NS(i,e,[pe.hatFingers,0,0]).applyMatrix4(i.matrix("head").clone().invert()).sub(s).sub(i.rig.heads.get("head"));return new v(0,0,pe.hatOn).lerp(o,t)}function S1(i,e,t){const{u:n}=Tn(t),s=Ke(e),r=N[s],o=Q(n,0,.2)*(1-Q(n,.82,1)),a=Q(n,.26,.36)*(1-Q(n,.66,.76));fe(i,0),oe(i,{lean:pe.monoclePeer*a,nod:pe.monoclePeer*a,tilt:r*pe.monocleTilt*a}),xe(i,e,o?[s]:[]);const c=1-.35*a;Fi(i,s,o,pe.monocleWrist.map((d,f)=>f===2?d-.25*(1-c):d));const[l,h,u]=pe.monocleWorn;n>.18&&n<.8?i.wearProp("monocle",[r*l,h,u]):o>.4&&i.holdUpright("monocle",s,[0,0,.2]),Ze(i,"startled",.6*a)}function E1(i,e,t){const{u:n,ready:s}=Tn(t),r=Ke(e),o=He(n,.3,.42),a=He(n,.5,.78);fe(i,0),oe(i,{lean:4*o,nod:-6*a}),xe(i,e,s?[r]:[]);const c=pe.toastWrist.map((l,h)=>nt(l,pe.sipWrist[h],a)+(h===1?-pe.toastClink*o:0));Fi(i,r,s,c),s>.3&&i.holdUpright("champagne_flute",r,[0,0,.1],{x:pe.sipTip*a,y:N[r]*pe.sipTip*a}),i.shutEyes(1-.7*a),o>.5&&Ze(i,"amused",o)}function T1(i,e,t){const{u:n,ready:s}=Tn(t),r=Ke(e),o=N[r];fe(i,0),oe(i,{lean:-5*s,tilt:-o*8*s,turn:-o*6*s}),xe(i,e,s?[r]:[]),Fi(i,r,s,pe.shakaWrist,{y:pe.shakaWaggle*Te(at(n,.2,.8),pe.shakaWaggles)*s}),s>.5&&i.holdUpright("shaka",r,[0,0,.32]),Ze(i,"amused",s)}function A1(i,e,t){const{u:n}=Tn(t),s=Ke(e),r=N[s],o=Q(n,0,.15)*(1-Q(n,.15,.3)),a=Q(n,.72,.86)*(1-Q(n,.86,1)),c=n>.22&&n<.82,l=Q(n,.28,.38)*(1-Q(n,.66,.76));fe(i,0),oe(i,{lean:-pe.shadesLean*l,tilt:r*pe.shadesTilt*l,nod:6*l*Math.max(Te(at(n,.38,.66),2),0)});const h=Math.max(o,a);xe(i,e,h?[s]:[]),Fi(i,s,h,pe.shadesWrist),c?i.wearProp("sunglasses",pe.shadesWorn):h>.4&&i.holdUpright("sunglasses",s,[0,-.1,.25])}function R1(i,e,t){const{u:n,ready:s}=Tn(t),r=Ke(e),o=Q(n,.18,.28)*(1-Q(n,.66,.74)),a=He(n,.66,.84);fe(i,0),oe(i,{nod:8*o*Math.max(Te(at(n,.28,.66),3),0)+6*a,tilt:N[r]*5*o}),xe(i,e,s?[r]:[]),Fi(i,r,s,pe.fireWrist,{y:25*a*Te(n,9)}),o>.02&&(i.holdUpright("flame",r,[0,0,.18]),Object.assign(i.props.get("flame"),{phase:n,size:pe.fireSize*o})),Ze(i,a>.3?"startled":"amused",Math.max(o,a))}function C1(i,e,t){const{u:n,ready:s}=Tn(t),r=Ke(e),o=He(n,.35,.6);fe(i,0),oe(i,{nod:14*o,lean:3*s}),xe(i,e,s?[r]:[]),Fi(i,r,s,pe.thumbWrist,{y:0}),s>.5&&(i.holdUpright("thumb",r,[0,0,.3]),Co(i)),Ze(i,"amused",o)}function P1(i,e,t){const{u:n}=Tn(t),s=Ke(e),r=Q(n,0,.14)*(1-Q(n,.24,.36)),o=Q(n,.26,.38)*(1-Q(n,.8,.95)),a=He(n,.38,.58)-He(n,.58,.8);fe(i,0),oe(i,{lean:pe.peerLean*o,nod:6*o,turn:pe.peerTurn*a}),xe(i,e,r?[s]:[]);const[c,l,h]=pe.glassesWrist;Fi(i,s,r,[c,l,h+.08*Q(n,.12,.22)]),Ze(i,"reading",o)}function L1(i,e,t){const{u:n,ready:s}=Tn(t),r=He(n,.25,.8);fe(i,0),oe(i,{lean:pe.thanksBow*r,nod:10*r}),xe(i,e,s?Object.keys(N):[]),s&&i.putAway(...Mt);for(const[o,a]of Object.entries(N))Bn(i,o,s,pe.prayerWrist,{x:pe.prayerRoll,y:-a*90,z:0});i.shutEyes(1-.85*r)}function I1(i,e,t){const{u:n,ready:s}=Tn(t),r=Ke(e),o=He(n,pe.popAt,pe.popAt+.2);i.lift("root",{z:pe.popHop*o}),fe(i,0),oe(i,{lean:-4*o,nod:-8*o}),xe(i,e,s?[r]:[]),Fi(i,r,s,pe.popperWrist),s>.4&&(i.holdUpright("party_popper",r,[0,0,.1],{y:N[r]*25}),i.props.get("party_popper").burst=at(n,pe.popAt,.95),Co(i)),Ze(i,"amused",o)}function D1(i,e,t){const{u:n,ready:s}=Tn(t),r=Ke(e),o=Math.max(Te(at(n,.25,.75),2),0);fe(i,0),oe(i,{lean:-5*s,twist:-N[r]*10*s,tilt:N[r]*4*s,nod:-4*s}),xe(i,e,s?[r]:[]),s&&ln(i,r,s,{...pe.flex,bend:pe.flex.bend+pe.flexPump*o}),Ze(i,"angry",.6*o)}function N1(i,e,t){const{u:n,ready:s}=Tn(t),r=Ke(e),o=Math.max(Te(at(n,.25,.75),2),0);i.lift("root",{z:pe.trophyHop*o}),fe(i,0),oe(i,{nod:-12*s,lean:-4*s}),xe(i,e,s?[r]:[]),s&&ln(i,r,s,pe.trophy),s>.4&&(i.holdUpright("trophy",r,[0,0,.3]),Co(i)),Ze(i,"amused",s)}function U1(i,e,t){const{u:n,ready:s}=Tn(t),r=Dr(e)[0]||Ke(e),o=Math.max(Te(at(n,.25,.75),2),0);fe(i,0),oe(i,{lean:-4*s,nod:-10*s}),xe(i,e,s?[r]:[]),s&&ln(i,r,s,{...pe.sword,y:pe.sword.y-pe.swordThrust*o}),s&&i.putAway("squire_quill"),s>.4&&(i.holdUpright("sword",r,[0,0,.15],{x:-15}),Co(i)),Ze(i,"angry",s)}function O1(i,e,t){const{u:n,ready:s}=Tn(t),r=[...e.shield][0];if(!r)return sc(i,e,t);const o=He(n,pe.shieldBump,pe.shieldBump+.12);Kn(i,pe.shieldCrouch*s),fe(i,0),oe(i,{lean:8*s-8*o,nod:6*s}),xe(i,e,s?[r]:[]);const[a,c,l]=pe.shieldWrist;Bn(i,r,s,[a,c+.08*o,l]),i.keep.add("squire_shield"),Ze(i,o>.3?"startled":"angry",s)}function F1(i,e,t){const{u:n,ready:s}=Tn(t),r=Dr(e)[0]||Ke(e),o=He(n,.35,.75);fe(i,0),oe(i,{nod:12*o,lean:4*o}),xe(i,e,s?[r]:[]),Bn(i,r,s,pe.castleWrist,{x:-30}),s&&i.putAway("squire_quill"),s>.4&&(i.holdUpright("castle",r,[0,0,.12]),Co(i)),Ze(i,"amused",o)}const br={high:[1,-.25,2.92],sign:[.5,-.25,3],signWaggle:.1,drawer:[1.16,-.4,1.66],drop:.12,binoculars:[.24,-.8,2.36],sweep:30,nozzle:[1.1,-.55,1.88],torchSweep:.16,corner:[1,-.42,1.36],lift:.3,crouch:.6,peekLean:34},B1=(i,e,t)=>i.map((n,s)=>nt(n,e[s],t)),Nr=i=>i.putAway(...[...Mt].filter(e=>!nc.has(e)));function Qh(i,e,t,n,s={}){const r=Ke(e);xe(i,e,t?[r]:[]),Bn(i,r,t,n,s),t&&Nr(i)}const $t={bend:.9,lean:30,nod:18,talkNod:5,ear:[.94,.05,3.48],handsetLean:50,tilt:8,finger:.28,palm:.13,grip:.68,across:.2,arc:[.28,-.18,.25]};function Sr(i,e){return i.clone().applyAxisAngle(new v(1,0,0),Xe(xt.tip)).add(e)}function Vp(i,e,t,n,s){const r=i.head(`upper_arm_${e}`,i.standing(`upper_arm_${e}`)),o=n.clone().sub(r),[a,c]=[o.length(),i.foldedReach(e)*1.01];o.normalize();const l=a-$t.finger>=c?0:Math.acos(yt.clamp((a**2+$t.finger**2-c**2)/(2*a*$t.finger),-1,1)),h=new v(0,0,-1).projectOnPlane(o).normalize(),u=o.multiplyScalar(Math.cos(l)).addScaledVector(h,Math.sin(l));Wp(i,e,t,i.withinReach(e,n.clone().addScaledVector(u,-$t.finger),.97),s);const d=i.rig.along.get(`hand_${e}`).clone().transformDirection(i.matrix(`hand_${e}`));i.aim(`hand_${e}`,d.lerp(u,t).normalize()),Xp(i,e,t)}function Wp(i,e,t,n,s){if(i.posture!=="composed")return At(i,e,t,n,s);const r=i.withinReach(e,k1(i,e),.97),o=i.head(`upper_arm_${e}`,i.standing(`upper_arm_${e}`)),a=r.sub(o),c=n.clone().sub(o),l=nt(a.length(),c.length(),t),h=a.normalize().lerp(c.normalize(),t).normalize();i.reach(e,o.addScaledVector(h,l),new v(1,.3,0).lerp(s,t))}function k1(i,e){const t=N[e],n=i.leanWay||Math.sign(Ci(i.facing));if(n&&t!==n){const[r,o,a]=Kt.feet;return i.step(e,new v(t*r,o,a),new v(0,-1,1)),i.head(`shin_${e}`,i.matrix(`shin_${e}`)).add(new v(...Kt.lean.knee))}const s=i.leanWay?Kt.lean.out:Kt.hands[0];return new v(t*s,Kt.hands[1],Kt.floor)}function Xp(i,e,t){if(i.posture!=="composed"||t>=1)return;const n=`hand_${e}`,s=i.head(n,i.matrix(n)),r=new It().setFromRotationMatrix(On(-80,0,0)),o=new It().setFromRotationMatrix(new ge().extractRotation(i.matrix(n))),a=new ge().makeRotationFromQuaternion(r.slerp(o,t));i.final.set(n,Ln(s).multiply(a).multiply(Ln(i.rig.heads.get(n).clone().negate())))}const qp=i=>new v(i.x,-i.z,i.y);function $p(){const{base:i}=xt,[e,t]=[[i.depth/2,0],i.brow],n=new re(t[1],e[0]-t[0]).normalize(),s=new v(0,(e[1]+t[1])/2,(e[0]+t[0])/2).add(new v(0,n.y,n.x).multiplyScalar(eu()));return new ge().compose(s,new It().setFromEuler(new cn(Math.atan2(n.x,n.y),0,0)),new v(1,1,1))}const eu=()=>xt.base.round*.8,jp=i=>xt.base.height+eu()+xt.base.dome*Math.max(1-(i/(xt.base.width/2))**2,0),vo=()=>qp(new v(0,jp(xt.cradle.apart)+xt.cradle.height+xt.handset.rest,xt.cradle.at));function Yp(i){const{dial:e}=xt,t=Xe(e.first-i);return qp(new v(Math.cos(t)*e.ring,e.face*1.5,-Math.sin(t)*e.ring).applyMatrix4($p()))}function z1(i){const e=N[i],t=Math.sqrt(1-$t.across**2),n=new v(e*$t.across,t*Math.sin(Xe($t.handsetLean)),t*Math.cos(Xe($t.handsetLean))),s=new v(e,0,0).projectOnPlane(n).normalize(),r=new ge().makeBasis(n,s.clone().cross(n),s),o=new cn().setFromRotationMatrix(r,"ZYX");return{along:n,basis:r,turn:{x:yt.radToDeg(o.x),y:yt.radToDeg(o.y),z:yt.radToDeg(o.z)}}}const Kp=i=>new v(i*(xt.handset.length/2+xt.handset.end[1]*xt.handset.grille*Math.sin(.22)),0,-xt.handset.drop-xt.handset.end[1]*xt.handset.grille*Math.cos(.22));function Ha(i,e){const t=at(i,...e);return t**3*(10-15*t+6*t*t)}function H1(i){const e=ie.phone_call,t=at(i,...e.drop),n=at(i,...e.settle),s=n>0&&n<1?Math.sin(Math.PI*e.wobbles*n)*(1-n)**2:0,r=at(i,...e.goes),o=at(i,...e.poof);return{here:r<.5,above:e.above*(1-t*t),squash:e.squash*s,puff:i>=e.goes[0]?r:o<1?.3+.7*o:null}}function G1(i,e,t){if(i.posture!=="stand")return V1(i,e,t);const n=ie.phone_call,s=Dt(t,n.frames),r=Ke(e),o=r==="l"?"r":"l",a=Math.max(ne(s,n.reach)*(1-ne(s,n.lift)),ne(s,n.finger)*(1-ne(s,n.back)),ne(s,[n.hang[0],(n.hang[0]+n.hang[1])/2])*(1-ne(s,[n.hang[1],n.goes[0]]))),c=Ha(s,n.lift)*(1-Ha(s,[n.hang[0],n.hang[0]+(n.hang[1]-n.hang[0])*.7])),l=at(s,...n.talk),h=$t.bend*a;Kn(i,h),fe(i,0),oe(i,{lean:$t.lean*a,nod:$t.nod*a+$t.talkNod*Math.sin(Math.PI*n.nods*l)**2,tilt:N[r]*$t.tilt*c}),i.bendAbove("chest",{y:N[r]*(e.voice==="butler"?1.2:2)*c}),i.putAway(...Mt),xe(i,e,[r,o]);const u=s>=n.reach[1]&&s<n.hang[1]?1:ne(s,n.reach)*(1-ne(s,[n.hang[1],n.goes[0]])),d=s>=n.reach[1]&&s<n.hang[1],f=Zp(i,r,{base:pl,reach:u,lifted:c,inHand:d}),m=n.turn*ne(s,n.dial)*(1-ne(s,n.back)),_=ne(s,n.finger)*(1-ne(s,n.back));Vp(i,o,_,Sr(Yp(n.turn*ne(s,n.dial)),pl),new v(-1,.2,-.6)),Ze(i,"amused",l>0&&l<1?1:0),Jp(i,{u:s,base:pl,root:new v(0,0,-h),side:r,inHand:d,mouth:f,turned:m})}function V1(i,e,t){i.kneesTogether();const n=ie.phone_call,{finger:s,dial:r,back:o,reach:a,lift:c,beside:l,behind:h}=n.seated,u=Dt(t,n.frames),d=i.phoneWay*Math.cos(Xe(i.facing))>=0?"l":"r",f=new v(N[d]*l,h,_f[i.posture].drop*Gt),m=ne(u,s)*(1-ne(u,o)),_=Ha(u,c)*(1-Ha(u,[n.hang[0],n.hang[0]+(n.hang[1]-n.hang[0])*.7])),g=at(u,...n.talk);fe(i,0),oe(i,{nod:$t.talkNod*Math.sin(Math.PI*n.nods*g)**2,tilt:N[d]*$t.tilt*_}),i.bendAbove("chest",{y:N[d]*(e.voice==="butler"?1.6:2.6)*_}),i.putAway(...Mt),xe(i,e,[d]),i.inUse.add(d);const p=u>=a[1]&&u<n.hang[1]?1:ne(u,a)*(1-ne(u,[n.hang[1],n.goes[0]])),y=u>=a[1]&&u<n.hang[1],M=n.turn*ne(u,r)*(1-ne(u,o)),x=u<a[0]?Sr(vo().add(gh()),f):Zp(i,d,{base:f,reach:p,lifted:_,inHand:y});u<a[0]&&Vp(i,d,m,Sr(Yp(n.turn*ne(u,r)),f),new v(1,.2,-.6)),Ze(i,"amused",g>0&&g<1?1:0),Jp(i,{u,base:f,root:i.carried(new v),side:d,inHand:y,mouth:x,turned:M})}const gh=()=>Kp(-1);function Zp(i,e,{base:t,reach:n,lifted:s,inHand:r}){const o=z1(e),[a,c,l]=$t.ear,h=new v(N[e]*a,c,l).applyMatrix4(i.matrix("head")),u=new ge().extractRotation(i.matrix("head")).multiply(o.basis),d=h.clone().sub(Kp(1).applyMatrix4(u)),f=Sr(vo(),t),m=new It().setFromRotationMatrix(On(xt.tip,0,0)).slerp(new It().setFromRotationMatrix(u),s),_=new ge().makeRotationFromQuaternion(m),g=new v(0,0,1).applyQuaternion(m),p=Math.sin(Math.PI*s)**2,M=f.clone().lerp(d,s).add(new v(N[e]*$t.arc[0],$t.arc[1],$t.arc[2]).multiplyScalar(p)).clone().addScaledVector(g,$t.palm),x=i.head(`upper_arm_${e}`,i.standing(`upper_arm_${e}`)),A=M.clone().sub(x).normalize(),E=`hand_${e}`,P=Yn(at(n,.65,1)),R=new v(1,i.posture==="stand"?.3:-.1,nt(-.6,-.12,s)),b=B=>{Wp(i,e,n,i.withinReach(e,B,.97),R);const F=i.rig.along.get(E).clone().transformDirection(i.standing(E));return i.aim(E,F.lerp(A,n).normalize()),i.roll(E,N[e]*18*n*s),Xp(i,e,n),i.clench(e,nt(1,$t.grip,P)),M.clone().sub(i.grip(e,[0,0,0]).applyMatrix4(i.matrix(E)).sub(i.head(E,i.matrix(E))))};if(b(b(b(M))),!r)return Sr(vo().add(gh()),t);const w=i.grip(e,[0,0,0]).applyMatrix4(i.matrix(E)).addScaledVector(g,-$t.palm),L=new cn().setFromQuaternion(m,"ZYX");return i.holdUpright("telephone_handset",e,[0,0,0],{x:yt.radToDeg(L.x),y:yt.radToDeg(L.y),z:yt.radToDeg(L.z)}),i.props.get("telephone_handset").at=w.clone().applyMatrix4(i.matrix(E).clone().invert()),w.add(gh().applyMatrix4(_))}function Jp(i,{u:e,base:t,root:n,side:s,inHand:r,mouth:o,turned:a}){const c=ie.phone_call,l=m=>Sr(m,t).sub(n);r||i.standProp("telephone_handset",l(vo()).toArray(),{x:xt.tip});const h=H1(e),u=h.puff??0;if(u>0&&u<1&&(i.standProp("telephone_poof",l(new v(0,0,xt.base.height/2+(e<c.goes[0]?c.above:0))).toArray()),Object.assign(i.props.get("telephone_poof"),{puff:u})),!h.here){i.props.delete("telephone_handset");return}const d=new v(0,0,h.above);i.standProp("telephone",l(new v).add(d).toArray(),{x:xt.tip}),Object.assign(i.props.get("telephone"),{squash:h.squash,dial:a}),r||i.props.get("telephone_handset").at.add(d).add(new v(0,0,-h.squash*vo().z)),i.standProp("telephone_cord",n.clone().negate().toArray());const f=r?o:o.add(d);Object.assign(i.props.get("telephone_cord"),{from:l(new v(-N[s]*xt.base.width*.4,.25,xt.base.height*.3)).add(d),to:f.sub(n)})}function W1(i,e,t){const n=ie.ask_sign,s=Dt(t,n.frames),r=ne(s,n.raise)*(1-ne(s,n.lower)),o=Te(at(s,...n.waggle),n.waggles)*He(s,...n.waggle),[a,c,l]=br.sign;fe(i,0),oe(i,{nod:-10*r,tilt:4*o}),Qh(i,e,r,[a+br.signWaggle*o,c,l]),Ze(i,"worried",r)}const ii={at:[0,-.74,2.02],across:.4,closed:.08,apart:.64,elbow:[1,.4,-.6],nod:16,lineNod:4,scan:12,sweep:.6};function X1(i,e,t){const n=ie.scroll,s=Dt(t,n.frames),r=ne(s,n.raise)*(1-ne(s,n.lower)),o=ne(s,n.unrolls)*(1-ne(s,n.rolls)),a=at(s,n.unrolls[1],n.rolls[0]);fe(i,0),oe(i,{lean:3*r}),i.putAway(...Mt),xe(i,e,r?Object.keys(N):[]);const c=Ke(e),[l,h,u]=ii.at;for(const[g,p]of Object.entries(N)){const y=u+(g===c?1:-1)*nt(ii.closed,ii.apart,o)/2,M=new v(l+p*ii.across,h,y);r&&At(i,g,r,i.withinReach(g,i.carried(M),.97),new v(...ii.elbow))}const d=Math.min(Math.floor(a*n.lines),n.lines-1),f=a*n.lines-d,m=ii.scan*(1-2*ne(f,[0,ii.sweep])+2*ne(f,[ii.sweep,1])),_=Math.min(d+ne(f,[ii.sweep,1]),n.lines-1);i.face("head",{x:(ii.nod+ii.lineNod*_)*o,z:m*o}),Ze(i,"reading",o),r&&q1(i,c,r===1?c==="l"?"r":"l":null,o)}function q1(i,e,t,n){const s=l=>i.grip(l,[0,0,0]).applyMatrix4(i.matrix(`hand_${l}`)),r=s(e),o=t?s(t):r.clone().add(new v(0,0,-lm.rolled)),a=r.clone().add(o).multiplyScalar(.5);t&&(r.x=o.x=a.x);const c=i.matrix("root").clone().invert();i.standProp("report_scroll",a.clone().applyMatrix4(c).toArray()),Object.assign(i.props.get("report_scroll"),{top:r.sub(a),bottom:o.sub(a),open:n})}function $1(i,e,t){const n=ie.file_card,s=Dt(t,n.frames),r=ne(s,n.reach)*(1-ne(s,n.back)),[o,a,c]=br.drawer;fe(i,0),oe(i,{lean:10*r,nod:14*r}),Qh(i,e,r,[o,a,c-br.drop*ne(s,n.filed)])}const ll={sink:2.1,hop:.75,leap:1};function j1(i,e,t){const n=ie.pack_box,{into:s,out:r}=Ga(n,t),o=He(s,...n.hop),a=ne(s,n.into)*(1-ne(r,[n.pops,n.pops+.2])),c=He(r,...n.leap);i.lift("root",{z:ll.hop*o-ll.sink*a+ll.leap*c}),fe(i,0),oe(i,{lean:6*o,nod:12*a-10*c}),Zn(i,e,0,60*o+120*c),as(i,.7*o+.6*c),i.putAway(...Mt),Ze(i,"amused",c)}function Y1(i,e,t){const n=ie.press,{into:s,out:r}=Ga(n,t),o=ne(s,[.2,.55])*(1-ne(r,[.2,.5]));fe(i,0),oe(i,{nod:-8*o}),Zn(i,e,0,140*o),i.putAway(...Mt),i.shutEyes(1-.8*ne(s,n.squashes)*(1-ne(r,n.frees)))}function K1(i,e,t){const{held:n,into:s,out:r}=Ga(ie.vacuum,t),[o,a,c]=br.nozzle;fe(i,0),oe(i,{lean:8,nod:14,turn:-N[Ke(e)]*14}),Qh(i,e,s*(1-r),[o,a,c-.12*Te(n??0,2)],{x:-10})}const $i={intro:18,hold:12,outro:6,fps:12,taps:6,tap:18,point:[1.25,-.45,1.75],bounce:.14,wiggle:7,sparkle:.25};function Z1(i,e,t){const{intro:n,hold:s,outro:r,taps:o,tap:a,point:c,bounce:l,wiggle:h,sparkle:u}=$i,d=t*(n+s+r),f=d<n?Math.sin(Math.PI*d/n):0,m=d<n?Q(d/n,.7,1):1-Q((d-n-s)/r,0,1),_=d>=n&&d<n+s?(d-n)/s:null,g=_===null?0:Math.abs(Math.sin(2*Math.PI*_)),p=Te(d/n,o);i.lift("root",{z:l*g}),fe(i,0),oe(i,{lean:6*m,nod:14*m+4*g,twist:h*(_===null?f*p:Te(_,2))}),i.posture==="stand"&&(i.turn("foot_l",{x:a*f*Math.max(p,0)}),i.turn("foot_r",{x:a*f*Math.max(-p,0)})),xe(i,e,m?[...e.free]:[]);for(const M of e.free)Bn(i,M,m,[c[0],c[1],c[2]+.1*g*N[M]],{x:40});m&&Nr(i);const y=Math.min(d/4,1)*(1-at(d,n+s,n+s+r));i.starEyes(y*(1+u*Math.abs(Te(d/6))))}function J1(i,e,t){const n=ie.fume,s=Dt(t,n.frames),r=He(s,n.crushed[0],n.crushed[1]+.06),o=ne(s,[n.mad[0],n.mad[0]+.06])*(1-ne(s,[n.mad[1]-.1,1])),a=Te(at(s,...n.mad),n.stamps/2);Kn(i,.14*r),i.lift("root",{z:.12*o*Math.abs(a)}),fe(i,0),oe(i,{lean:16*r+6*o,nod:28*r+10*o,tilt:5*o*Te(s,14)}),xe(i,e,[...e.free]);for(const c of e.free)ln(i,c,o,{y:40,z:-25,bend:95}),i.clench(c,1-.28*o);if(i.posture==="stand")for(const[c,l]of[["l",1],["r",-1]]){const h=o*Math.max(l*a,0);i.turn(`thigh_${c}`,{x:-34*h,y:l*18*h}),i.turn(`shin_${c}`,{x:52*h})}r>o?Ze(i,"worried",r):Ze(i,"angry",o)}const li={frames:36,fps:12,head:18,body:5,up:10},hl=(i,e)=>(t,n,s)=>{const r=Dt(s,li.frames),o=Q(r,.08,.25)*(1-Q(r,.75,.92));oe(t,{twist:i*li.body*o,turn:i*li.head*o,nod:-e*li.up*o}),xe(t,n)},_h={frames:6,fps:20},Gn={frames:48,fps:12,trip:[0,.14],down:[.05,.11],bounce:[.11,.18],shake:[.3,.58],shakes:3,up:[.62,.8],hop:[.8,.96],drop:.74};function Q1(i,e,t){const n=Dt(t,Gn.frames),s=Q(n,...Gn.down)*(1-Q(n,...Gn.up)),r=He(n,...Gn.trip),o=Te(at(n,...Gn.shake),Gn.shakes)*He(n,...Gn.shake),a=He(n,...Gn.hop);if(i.lift("root",{z:-Gn.drop*s+.1*He(n,...Gn.bounce)+.16*a}),i.posture==="stand")for(const c of Object.keys(N))i.turn(`shin_${c}`,{x:90*s});oe(i,{lean:12*s+10*r*(1-s),nod:12*s,turn:26*o}),Zn(i,e,0,100*r*(1-s)+60*a,8*r),i.putAway(...Mt),a>.1?Ze(i,"amused",a):Ze(i,s>.5?"worried":"startled",Math.max(s,r))}const pa={hands:[.8,.18],lean:-7,nod:-3,toes:14};function eE(i,e,t){fe(i,t),oe(i,{lean:pa.lean,nod:pa.nod+2*Te(t)});const[n,s]=pa.hands;xe(i,e,[...e.free]);for(const r of e.free)At(i,r,1,i.withinReach(r,new v(N[r]*n,s,qn.floor),.97),new v(1,.6,.2)),i.face(`hand_${r}`,{x:-80});e.free.size&&Nr(i),i.swing(.6*Te(t)),i.tap=pa.toes*Math.max(Te(t,2),0)}const Yr={pocket:[.35,-.5,1.45],held:[.15,-.95,1.95],look:18,out:[.1,.3],back:[.72,.92]};function tE(i,e,t){const n=Ke(e),s=ne(t,Yr.out)*(1-ne(t,Yr.back)),r=o=>new v(N[n]*o[0],o[1],o[2]);fe(i,t),oe(i,{lean:4*s,nod:Yr.look*s}),xe(i,e,[n]),At(i,n,Math.max(s,.001),i.withinReach(n,r(Yr.pocket).lerp(r(Yr.held),s),.97),new v(N[n]*.6,-.5,-.6)),s>.15&&i.holdUpright("pocket_watch",n,[0,0,0],{x:-30}),i.swing(.4*Te(t))}const of={nod:24,lean:8};function nE(i,e,t){const n=.7+.3*Math.sin(2*Math.PI*t);fe(i,t),oe(i,{lean:of.lean*n,nod:of.nod*n}),xe(i,e),i.shutEyes(0),i.doze(1+Math.floor(t*4)%2),i.swing(.15*Te(t))}function iE(i,e,t){const n=Te(t);fe(i,0),oe(i,{lean:8,nod:-12}),Zn(i,e,0,110+20*n),as(i,.6+.2*n)}const Es={at:[.3,-.8,2.45],across:1.5,low:1.1,high:3.4,swats:4,giggle:4};function sE(i){if(!i.at)return null;const e=Math.min(Math.max((i.at.x-.5)*Gt,-1.5),Es.across),t=Math.min(Math.max(Fn+(.5-i.at.y)*Gt,Es.low),Es.high);return new v(e,Es.at[1],t)}function rE(i,e,t){const n=Dt(t,24),s=Q(n,0,.12)*(1-Q(n,.88,1)),r=t*Es.swats,o=sE(i),a=o?o.x*N.l>0?"l":"r":Math.floor(r)%2?"l":"r",c=Math.sin(Math.PI*(r%1));fe(i,n),oe(i,{tilt:Es.giggle*Math.sin(2*Math.PI*r*2)*s,nod:-3*s}),i.putAway(...Mt),xe(i,e,Object.keys(N));for(const l of Object.keys(N)){const[h,u,d]=Es.at,f=l===a&&o?i.withinReach(l,o,.95):new v(N[l]*h,u,d),m=s*(.25+(l===a?.75*c:0));Ds(i,l),os(i,l,m,f,null,[1,-.4,-.3])}i.squeezeEyes(1)}const ma={up:[1.2,-.3,2.85],down:[.95,-.25,1.3],sway:12,bounce:.18};function oE(i,e,t){const n=ie.disco,s=Dt(t,n.frames),r=s*n.beats,a=(Math.floor(r)%2?1:-1)*(2*Q(r%1,0,.42)-1),c=ne(s,[0,.08])*(1-ne(s,[.88,1])),l=Math.sin(Math.PI*r)**2*c;Kn(i,ma.bounce*l),fe(i,s),oe(i,{tilt:a*ma.sway*c,nod:-4*c+2*l}),i.putAway(...Mt),xe(i,e,Object.keys(N));for(const h of Object.keys(N)){const u=N[h],d=(1+u*a)/2,f=new v(...ma.down).lerp(new v(...ma.up),d);f.x*=u;const m=new v(1,.4,nt(-.6,.2,d));At(i,h,c,i.carried(f),m)}Ze(i,"amused",c)}const mn={grip:[-.1,-.62,2],down:12,fore:.9,behind:[-.45,.45,1.45],kick:.13,climb:7,shoulder:7,turn:22,cheek:14,steep:60};function xh(i,e=mn.down,t=1){const n=e-mn.climb*i,s=new v(t*Math.cos(Xe(n)),0,-Math.sin(Xe(n))),[r,o,a]=mn.grip;return{grip:new v(t*r,o,a).addScaledVector(s,-mn.kick*i),along:s,pitch:n}}const af=i=>{const{shots:e,count:t}=ie.bug_shot;if(i<=e[0]||i>=e[1])return 0;const n=(i-e[0])/(e[1]-e[0])*t%1;return n<.08?Yn(n/.08):1-Yn(at(n,.08,.5))};function aE(i,e){if(!i)return{turn:N.l*mn.turn,down:mn.down,way:1,handed:1,point:null};const t=new v((i.x-.5)*Gt,za,Fn+(.5-i.y)*Gt).applyAxisAngle(new v(0,0,1),Xe(-e)),n=yt.radToDeg(Math.atan2(-(t.z-mn.grip[2]),Math.hypot(t.x,t.y))),s=t.x>=0||n<-mn.steep?1:-1,r=ne(t.x,[-3,3]),o=1-ne(n,[-mn.steep-5,-mn.steep+5]),a=2*nt(r,1,o)-1,c=yt.radToDeg(Math.atan2(t.y,t.x))*Math.cos(Xe(n)),l=-yt.radToDeg(Math.atan2(-t.y,-t.x))*Math.cos(Xe(n)),h=nt(l,c,(a+1)/2),u=xh(0,mn.down,a).grip.applyAxisAngle(new v(0,0,1),Xe(h)),d=t.clone().sub(u);return{turn:h,down:yt.radToDeg(Math.atan2(-d.z,Math.hypot(d.x,d.y))),way:s,handed:a,point:t}}function tu(i){const e=Math.max(i.z,0),t=new v(0,-e,1-e).normalize(),n=t.sub(i.clone().multiplyScalar(t.dot(i))).normalize();return new ge().makeBasis(i.clone(),n.clone().cross(i),n)}function cE(i){const e=new cn().setFromRotationMatrix(tu(i),"ZYX");return{x:yt.radToDeg(e.x),y:yt.radToDeg(e.y),z:yt.radToDeg(e.z)}}function lE(i,e,t,n){if(!e)return n;const s=e.clone().applyAxisAngle(new v(0,0,1),Xe(-t)),r=a=>i.clone().add(Qp(a).multiplyScalar(sr.barrel)),o=s.clone().sub(r(s.clone().sub(i).normalize())).normalize();return s.sub(r(o)).normalize()}const Qp=i=>new v().setFromMatrixColumn(tu(i),2),hE=i=>{const e=Math.max(-i,0)/90;return new v(0,0,-sr.low*e)};function em(i,e){const t=`upper_arm_${e}`;let n=new It().setFromRotationMatrix(new ge().extractRotation(i.standing(t)));for(const s of["upper_arm","forearm"]){const r=`${s}_${e}`,o=i.rig.along.get(r).clone().applyQuaternion(n).normalize(),a=i.rig.along.get(r).clone().transformDirection(i.matrix(r)).normalize();n=new It().setFromUnitVectors(o,a).multiply(n)}return n}function tm(i,e,t){return new It(nt(i.x,e.x,t),nt(i.y,e.y,t),nt(i.z,e.z,t),nt(i.w,e.w,t)).normalize()}function uE(i,e,t,n,s){const r=Qp(s).negate(),o=x=>n.clone().addScaledVector(s,x-hn.grip).addScaledVector(r,sr.under),a=i.head(`upper_arm_${e}`,i.standing(`upper_arm_${e}`)),c=i.rig.heads.get(`upper_arm_${e}`),l=i.rig.heads.get(`forearm_${e}`),h=i.rig.heads.get(`hand_${e}`),u=(c.distanceTo(l)+l.distanceTo(h))*.97,d=o(0).sub(a),f=d.dot(s),m=-f+Math.sqrt(Math.max(f**2-d.lengthSq()+u**2,0)),_=o(Math.max(sr.nearest,Math.min(sr.fore,m)));At(i,e,t,i.withinReach(e,_,.97),new v(N[e]*.6,-.6,-.6));const g=Math.asin(-N[e]*s.z),p=Math.atan2(s.y,s.x)+(e==="r"?Math.PI:0),y=new It().setFromEuler(new cn(Xe(sr.roll),g,p,"ZYX")),M=tm(em(i,e),y,t);return Jh(i,e,1,M),M}function dE(i,e,t,n,s,r,o,a){const[c,l,h]=mn.behind,u=new v(t*c,l,h).lerp(n.grip.clone().add(hE(a)),r);u.x-=t*.55*Math.sin(Math.PI*r);const d=new v(-t,.5,-.5).lerp(new v(-t,-.2,-.6),r);At(i,e,s,i.withinReach(e,u,.97),d),i.clench(e,nt(1,.66,o))}function cf(i,e,t=em(i,e)){const n=`hand_${e}`,s=new v;return i.matrix(n).decompose(new v,new It,s),{point:i.grip(e,[0,0,0]).applyMatrix4(i.matrix(n)),rotation:t,scale:s}}function fE(i,e,t,n,s,r){const o=(e.handed+1)/2,a={},c={};for(const[d,f]of[["r",1],["l",-1]])dE(i,d,f,xh(t,e.down,f),n,s,r,e.down),a[d]=cf(i,d);const l=a.l.point.clone().lerp(a.r.point,o),h=lE(l,e.point,e.turn*r,xh(t,e.down,e.handed).along);for(const d of Object.keys(N)){i.final.delete(`hand_${d}`);const f=uE(i,d,r,l,h);c[d]=cf(i,d,f)}const u=new v(0,1,0).applyMatrix4(tu(h));for(const d of Object.keys(N)){const f=d==="l"?o:1-o,m=a[d],_=c[d],g=tm(m.rotation,_.rotation,f),p=m.scale.clone().lerp(_.scale,f),y=new ge().compose(new v,g,p),M=m.point.clone().lerp(l,r).lerp(_.point,f).addScaledVector(u,N[d]*.12*Math.sin(Math.PI*o)*r),x=`hand_${d}`,A=i.grip(d,[0,0,0]).sub(i.rig.heads.get(x)).applyMatrix4(y),E=i.withinReach(d,M.sub(A),.999999-.03*n*Math.sin(Math.PI*f)**2),P=new v(N[d],nt(.5,-.2,s),nt(-.5,-.6,s)),R=new v(N[d]*.6,-.6,-.6),b=fh.clone().lerp(P,n).lerp(fh.clone().lerp(R,r),f);b.y+=Math.sin(Math.PI*f)*n,i.reach(d,E,b),i.setMove(x,Ln(E).multiply(y).multiply(Ln(i.rig.heads.get(x).clone().negate())))}return{held:l,along:h}}function nm(i,e,t,n,s=0){i.stride*=n*Gt/Qi[0],i.strideTurn=i.walkWay*90*Math.sign(i.stride||1)-t-i.facing,Yh(i);const r=.1*Math.abs(Math.sin(Xe(i.strideTurn))),o=(i.strideHeight-r)*e-s*(1-e);i.lift("root",{z:o-i.strideHeight}),i.strideHeight=o}function pE(i,e,t){const n=ie.bug_shot,s=(n.draw[0]+n.draw[1])/2,r=ne(t,[n.draw[0],s])*(1-ne(t,[s,n.draw[1]])),o=ne(t,[s,n.draw[1]])*(1-ne(t,[n.drops[0]+.05,n.drops[0]+.2])),a=af(t),c=af(t-.008),l=aE(i.target,i.facing),h=l.way>0?"r":"l",u=t>=n.splat?ne(t,[n.splat,n.splat+.025]):ne(t,[n.draw[1],n.draw[1]+.025])*(1-ne(t,[n.aim[1]-.025,n.aim[1]])),d=Math.abs(i.walkWay)*u;d?nm(i,d,l.turn*o,n.back.stride,.025*o):Kn(i,.025*o),fe(i,t,1-.65*o),i.turn("chest",{z:-l.handed*mn.shoulder*c}),oe(i,{lean:2*o-2*c,nod:mn.cheek*o-4*c,turn:l.handed*mn.cheek*o,tilt:-l.handed*mn.cheek*.4*o}),i.putAway(...Mt),xe(i,e,Object.keys(N));const f=ne(t,[s,n.draw[1]]),m=ne(t,[n.draw[0],s])*(1-ne(t,[n.drops[0]+.05,n.drops[0]+.2])),{held:_,along:g}=fE(i,l,a,m,f,o);if(o>.05||r>.3){i.holdUpright("rifle",h,[0,0,0],cE(g));const p=i.props.get("rifle");p.at=_.clone().applyMatrix4(i.matrix(`hand_${h}`).clone().invert()),p.firing=a>.6}Ep(i,t,ne(t,n.draw)*(1-ne(t,[n.fly[0],n.fly[1]]))),d&&rc(i,d),i.posture==="stand"&&i.revolve(l.turn*o)}const co={rest:{grip:[.1,-.65,1.6],way:[1.6,-.6,-1]},top:{grip:[-.05,-.75,2.2],way:[.25,-1.35,1.6]},blow:{grip:[.25,-.75,1.68],way:[1.7,-.45,-1.1]},apart:.3,turn:30};function mE(i){const{raise:e,swing:t,lower:n}=ie.bug_smash,s=o=>({grip:new v(...co[o].grip),way:new v(...co[o].way).normalize()}),r=(o,a,c)=>({grip:o.grip.clone().lerp(a.grip,c),way:o.way.clone().lerp(a.way,c).normalize()});if(i<t[0]){const o=ne(i,e),a=r(s("rest"),s("top"),o);return a.grip.y-=.14*Math.sin(Math.PI*o),a}if(i<t[1]){const o=at(i,...t)**2,a=r(s("top"),s("blow"),o);return a.grip.y-=.1*Math.sin(Math.PI*o),a}if(i<n[0]){const o=.13*Math.sin(Math.PI*at(i,t[1],t[1]+.07))**2,a=s("blow");return a.grip.z+=o,a}return r(s("blow"),s("rest"),ne(i,n))}function ul(i,e,t,n,s){const r=n.clone();for(let o=0;o<3;o++){i.final.delete(`hand_${e}`),At(i,e,t,i.withinReach(e,r,.97),s),i.clench(e,nt(1,.68,t));const a=i.grip(e,[0,0,0]).applyMatrix4(i.matrix(`hand_${e}`));r.addScaledVector(n.clone().sub(a),t**3)}}function gE(i,e,t){const n=ie.bug_smash,s=Math.abs(i.walkWay)*ne(t,[n.walk[0],n.walk[0]+.025])*(1-ne(t,[n.walk[1]-.035,n.walk[1]])),r=ne(t,[n.raise[0]-.08,n.raise[0]])*(1-ne(t,[n.lower[1],1])),{grip:o,way:a}=mE(t),c=o.clone(),l=ne(t,n.raise)*(1-ne(t,n.swing)),h=ne(t,n.swing),u=1-ne(t,[n.blow+.015,n.blow+.11]),d=h*u;s&&nm(i,s,N.l*co.turn*r+i.walkWay*90*s,Dm.stride),fe(i,t,1-.7*r),oe(i,{lean:-4*l+11*d,nod:-4*l+8*d,twist:-4*l}),Kn(i,.045*l+.14*d),i.putAway(...Mt),xe(i,e,Object.keys(N)),ul(i,"r",r,o,new v(-.6,-.4,-.6));let f=i.grip("r",[0,0,0]).applyMatrix4(i.matrix("hand_r"));const m=no.head*Math.abs(a.z)+no.width*.5*Math.sqrt(1-a.z**2),_=Math.max(m+.006-f.z-a.z*no.handle,0);r>.85&&_>0&&(o.z+=_*ne(r,[.85,1]),ul(i,"r",r,o,new v(-.6,-.4,-.6)),f=i.grip("r",[0,0,0]).applyMatrix4(i.matrix("hand_r"))),ul(i,"l",r,f.clone().addScaledVector(a,co.apart),new v(.6,-.4,-.6));const g={y:yt.radToDeg(-Math.asin(a.z)),z:yt.radToDeg(Math.atan2(a.y,a.x))};if(r>.3)if(r<1){const p=c.lerp(f,ne(r,[.85,1]));p.z=Math.max(p.z,m+.006-a.z*no.handle),i.standProp("big_mallet",p.toArray(),g)}else i.holdUpright("big_mallet","r",[0,0,0],g);Ep(i,t,r*(1-ne(t,n.gone))),s&&rc(i,s),i.posture==="stand"&&i.revolve(N.l*co.turn*r+i.walkWay*90*s)}const lo={above:2.42,radius:.42,ring:.07,tip:28,hands:[.1,-.62,2.05]};function _E(i,e,t){const n=ie.halo,s=ne(t,n.grows)*(1-ne(t,n.fades));fe(i,t),i.lift("root",{z:n.float*s*(1+Math.sin(2*Math.PI*t))}),oe(i,{nod:-8*s,tilt:4*s}),i.putAway(...Mt),oc(i,{...e,free:new Set(Object.keys(N))},s,lo.hands),i.wearProp("halo",[0,0,lo.above]),i.props.get("halo").size=Math.max(s,.01),Ze(i,"serene",s)}const dl={pocket:[-.4,-.4,1.45],front:[-.04,-.59,2.02],apart:.08,tremble:.006},Pi={drop:.654,back:.12,ankleBack:.376,sole:.33,instep:.18,toe:.44,lean:18,bow:30,shoulders:.055};function xE(i,e){if(e)for(const t of Object.keys(N)){const n=Q(e,.35,1),s=Math.PI*n,r=i.rig.heads.get(`foot_${t}`).clone();r.y+=Pi.ankleBack*n,r.z=Math.max(Pi.sole*Math.cos(s),-Pi.instep*Math.cos(s))+Pi.toe*Math.sin(s);const o=i.rig.heads.get(`shin_${t}`).clone().sub(i.rig.heads.get(`thigh_${t}`));t==="r"&&(o.x=-o.x),i.step(t,r,o.lerp(new v(0,-1,0),e)),i.face(`foot_${t}`,{x:180*n})}}function vE(i,e,t,n){const s=`hand_${e}`,r=i.head(`upper_arm_${e}`,i.standing(`upper_arm_${e}`)),o=i.head(`forearm_${e}`,i.matrix(`forearm_${e}`)).sub(r);e==="r"&&(o.x=-o.x);const a=i.head(s,i.matrix(s)),c=i.rig.along.get(s).clone().transformDirection(i.matrix(s)),l=new v(-N[e],0,.12).normalize(),h=nt(1,.72,t),u=n.clone().addScaledVector(l,-hn.grip*h),d=a.lerp(u,t);d.z+=.08*Math.sin(Math.PI*t),i.reach(e,i.withinReach(e,d,.997),o.lerp(new v(1,-.35,-.6),t)),i.aim(s,c.lerp(l,t).normalize()),i.clench(e,h)}function yE(i,e,t){const n=ie.repent,s=Dt(t,n.frames),r=ne(s,n.kneel)*(1-ne(s,n.rise)),o=ne(s,n.out)*(1-Q(s,n.down[0],1)),a=Q(s,n.stand[1]*.5,n.up[1])*(1-Q(s,n.rise[0],1)),c=He(s,n.hold[0],n.hold[1]),l=.6*Math.sin(2*Math.PI*s*1.4)*He(s,0,1)*(1-.85*c),h=dl.tremble*Math.sin(2*Math.PI*5*s)*c;i.lift("root",{y:Pi.back*r,z:-Pi.drop*r}),i.posture==="stand"&&xE(i,r),oe(i,{lean:Pi.lean*r+l,nod:Pi.bow*a-l*.5,tilt:2*c});for(const f of Object.keys(N))i.lift(`shoulder_${f}`,{z:-Pi.shoulders*a});i.putAway(...Mt),xe(i,e);const u=new v(...dl.front).applyMatrix4(i.matrix("chest"));u.z+=h;for(const f of o?Object.keys(N):[]){const m=u.clone().add(new v(f==="l"?dl.apart:0,f==="l"?-.025:0,f==="l"?.025:0));vE(i,f,o,m)}const d=ne(s,n.up)*(1-ne(s,n.down));d>0&&(i.holdUpright("crucifix","r",[0,0,0],{x:-8*o}),i.props.get("crucifix").size=d),Ze(i,"worried",Math.max(r,a)),i.glanceEyes(-.2*a,0)}const ME=[.42,-.55,1.55],wE=[.45,.45,1.45];function bE(i,e,t){const n=ie.pogo,s=ne(t,[n.draw[0],n.draw[1]*.5])*(1-ne(t,[n.draw[1]*.5,n.draw[1]])),r=ne(t,[n.draw[1]*.6,n.draw[1]])*(1-ne(t,n.release)),o=mm(gm(),(t-n.bounces[0])/(n.bounces[1]-n.bounces[0])),a=t<n.bounces[0]?ne(t,[n.bounces[0]-.04,n.bounces[0]]):t<=n.bounces[1]?Math.cos(Math.PI*o.s)**2:1-ne(t,[n.spring[0],n.spring[0]+.06]);Kn(i,.22*a*r),fe(i,t),oe(i,{lean:6*r,nod:-6*r}),i.putAway(...Mt),xe(i,e,Object.keys(N));const[c,l,h]=ME,[u,d,f]=wE;for(const m of Object.keys(N)){const _=N[m];m==="r"&&s>r?At(i,m,s,new v(_*u,d,f),new v(1,.5,-.5)):At(i,m,r,new v(_*c,l,h),new v(1,-.2,-.4))}Ze(i,"amused",r)}const Aa={arm:.29,up:2.6,forward:-.1,above:.35},SE=[ie.rope_swing.ties*Gt/2-Aa.arm,Aa.forward,Aa.up];function EE(i,e,t){const n=_m(t),s=Ga(ie.rope_swing,t).held??0;i.kneesTogether(),i.lift("root",{z:Aa.above*xm(t)}),i.standProp("rope_swing",new v(0,0,_f.sit.drop*Gt).sub(i.carried(new v)).toArray()),fe(i,s),oe(i,{lean:-5*n,nod:-4}),i.putAway(...Mt);const[r,o,a]=SE;xe(i,e,Object.keys(N));for(const c of Object.keys(N))At(i,c,1,i.carried(new v(N[c]*r,o,a)),new v(1,0,-.4)),i.face(`hand_${c}`,{z:-N[c]*90});i.swing(1.2*n),Ze(i,"amused")}const TE=[1.25,0,2.95];function AE(i,e,t){const n=Te(t);fe(i,t),oe(i,{nod:-6,tilt:3*n}),i.putAway(...Mt);const[s,r,o]=TE;xe(i,e,Object.keys(N));for(const a of Object.keys(N))At(i,a,1,i.withinReach(a,i.carried(new v(N[a]*s,r,o)),.97),new v(1,0,-.4)),i.face(`hand_${a}`,{z:-N[a]*90});as(i,.05,6*n),Ze(i,"amused")}const ga={ahead:.95,below:.06,hands:.22,turn:35};function RE(i,e,t){const n=ie.binoculars,s=.4*br.sweep*Te(t,n.sweep),r=n.up+n.scan*Te(t,2);oe(i,{twist:s,nod:-r}),xe(i,e,["l","r"]);const o=i.rig.eyes.reduce((l,h)=>l.add(h),new v).divideScalar(i.rig.eyes.length).applyMatrix4(i.matrix("head")),a=new v(0,-Math.cos(Xe(r)),Math.sin(Xe(r))),c=o.clone().addScaledVector(a,ga.ahead).add(new v(0,0,-ga.below));i.standProp("binoculars",c.toArray(),{x:-r,z:s});for(const l of["l","r"]){const h=i.carried(c.clone().add(new v(N[l]*ga.hands,.1,-.16)));At(i,l,1,i.withinReach(l,h,.97),new v(...z.elbow))}Nr(i),i.posture==="stand"&&i.revolve(N[Ke(e)]*ga.turn)}const ai={crouch:.3,lean:48,nod:12,hands:[.3,-1.45,1.75],dig:.3,elbow:[1,-.4,-.6],turn:90,wiggle:6};function CE(i,e,t){const n=ie.rummage,s=yb(e,i.leanWay),r=ne(t,n.leans)*(1-ne(t,n.pops)),o=Te(t,n.digs);Kn(i,ai.crouch*r),fe(i,0),oe(i,{nod:ai.nod*r,tilt:ai.wiggle*o*r}),i.bendAbove("spine",{x:(ai.lean+ai.wiggle*o)*r}),xe(i,e);const[a,c,l]=ai.hands;for(const[h,u]of r?[["l",1],["r",-1]]:[]){const d=i.carried(new v(N[h]*a,c,l+u*ai.dig*o));os(i,h,r,i.withinReach(h,d,.97),void 0,ai.elbow)}vm.forEach((h,u)=>{const d=ym(u,t,i.throws??void 0);d&&i.standProp(h,[d.at[0],d.at[1],d.at[2]+ai.crouch*r],{x:d.turn,z:d.turn/3},1-d.landed)}),i.posture==="stand"&&i.revolve(N[s]*ai.turn*r)}function PE(i,e,t){const n=Ke(e),s=N[n],[r,o,a]=Ea;fe(i,t),oe(i,{lean:2,nod:gn.nod/2+2*Te(t),tilt:-s*gn.tilt*.7}),oc(i,e,1,[r,o,a+.03*Math.max(Te(t,2),0)]),Mp(i,n,1),i.holdLaptop(),i.glanceEyes(gn.glance[0],-s*gn.glance[1])}function LE(i,e,t){const{u:n,ready:s}=kn(t,z.greetingFrames),r=He(n,.3,.75),o=Ke(e),a=N[o];fe(i,0),oe(i,{lean:-4*s,nod:-10*s}),xe(i,e,s?[o]:[]),i.lift(`shoulder_${o}`,{y:-.32*s,z:.4*s}),Ro(i,o,s,B1([.6,-.93,3.35],[.15,-.93,3.35],r),{y:-a*110},new v(a*hn.grip,.148,0)),s&&Nr(i),i.shutEyes(1-.6*r)}function IE(i,e,t){const{back:n}=i.sky??{back:0};i.lift("root",{y:Ki.step*n,z:Ki.hop*Math.sin(Math.PI*n)}),fe(i,t),oe(i,{lean:-Ki.lean*n});const s=Ke(e);xe(i,e,[s]),yp(i,s,t),Nr(i),Ze(i,"amused")}const lf={sit:{under:Zh,over:Gb},lounge:{under:Bb,over:kb},composed:{under:zb,over:Hb},walk:{under:Yh,over:rc}},Ye=["stand","sit","lounge","composed","walk"],wt=["stand"],DE=["stand","sit","composed"],hf=["hang"],Zs=["sit","lounge"],NE=["stand","sit","walk"],uf=5,sA=[{name:"idle",head:se.free,frames:24,fps:8,loops:!0,leaves:8,postures:Ye,pose:sc},{name:"nod",head:se.gestures,frames:10,fps:12,loops:!1,postures:Ye,pose:Mb},{name:"hand_rub",head:se.gestures,frames:ie.hand_rub.frames,fps:ie.hand_rub.fps,loops:!1,postures:wt,pose:wb},{name:"ponder",head:se.holds,frames:ie.ponder.frames,fps:ie.ponder.fps,loops:!1,postures:Ye,pose:sl(ie.ponder)},{name:"think_cloud",head:se.holds,frames:ie.think_cloud.frames,fps:ie.think_cloud.fps,loops:!1,postures:Ye,pose:sl(ie.think_cloud)},{name:"got_it",head:se.holds,frames:ie.got_it.frames,fps:ie.got_it.fps,loops:!1,postures:Ye,pose:sl(ie.got_it)},{name:"shake",head:se.gestures,frames:12,fps:12,loops:!1,postures:Ye,pose:bb},{name:"wave",head:se.gestures,frames:12,fps:12,loops:!0,postures:Ye,pose:Sb},{name:"celebrate",head:se.gestures,frames:12,fps:10,loops:!0,postures:wt,pose:Rb},{name:"sleep",head:se.holds,frames:z.yawnFrames+ao,intro:z.yawnFrames,leaves:ao,fps:6,loops:!0,postures:Ye,marks:{mark:"Z",frames:[[z.yawnFrames,z.yawnFrames+ao]]},pose:Cb},{name:"walk",head:se.free,frames:12,fps:12,loops:!0,interruptible:!0,postures:wt,pose:Pb},{name:"walk_in",head:se.free,frames:40,fps:12,loops:!1,postures:wt,pose:jb},{name:"run_in",head:se.free,frames:28,fps:12,loops:!1,postures:wt,pose:Yb},{name:"pull_ups",head:se.holds,frames:24,fps:10,loops:!0,postures:wt,pose:Zb},{name:"ladder_climb",head:se.holds,frames:16,fps:8,loops:!0,interruptible:!0,postures:wt,pose:Kb},{name:"hang_l",head:se.holds,frames:24,fps:8,loops:!0,leaves:8,postures:hf,pose:Kd("l")},{name:"hang_r",head:se.holds,frames:24,fps:8,loops:!0,leaves:8,postures:hf,pose:Kd("r")},{name:"enter",head:se.gestures,frames:36,fps:12,loops:!1,postures:wt,pose:SS},{name:"exit",head:se.gestures,frames:28,fps:12,loops:!1,postures:wt,pose:ES},{name:"search",head:se.holds,frames:80,fps:10,loops:!0,postures:["stand"],pose:CS},{name:"glass_bubble",head:se.free,frames:48,fps:10,loops:!0,postures:["stand"],pose:IS},{name:"lean",head:se.free,frames:48,fps:8,loops:!0,leaves:24,postures:["stand"],pose:LS},{name:"read",head:se.holds,frames:ph,fps:Ct.fps,loops:!0,intro:Ct.intro,outro:Ct.outro,leaves:Ct.pageEvery,postures:Ye,pose:OS},{name:"write",head:se.holds,frames:Ba,intro:z.intro,outro:z.outro,leaves:z.hold,fps:z.fps,loops:!0,postures:Ye,pose:WS},{name:"waiting",head:se.free,frames:mh,intro:pn.intro,outro:pn.outro,leaves:pn.hold,fps:z.fps,loops:!0,postures:["stand","sit"],pose:FS},{name:"compacting",head:se.gestures,frames:Ba,intro:z.intro,outro:z.outro,leaves:z.hold,fps:z.compactFps,loops:!0,postures:Ye,pose:XS},{name:"yawn",head:se.gestures,frames:z.yawnFrames,fps:z.fps,loops:!1,postures:Ye,pose:zp},{name:"rest",head:se.free,frames:Bt.frames,fps:Bt.fps,loops:!1,postures:wt,marks:{mark:"♪",frames:Bt.tunes.map(i=>i.map(e=>e*Bt.frames))},pose:zS},{name:"whistle",head:se.gestures,frames:z.pastimeFrames,fps:z.fps,loops:!1,postures:Ye,voices:["coach"],pose:BS},{name:"phone_call",head:se.alone,frames:ie.phone_call.frames,fps:ie.phone_call.fps,loops:!1,postures:DE,pose:G1},{name:"sip",head:se.gestures,frames:z.pastimeFrames,fps:z.fps,loops:!1,postures:Ye,voices:["colleague"],pose:HS},{name:"groove",head:se.gestures,frames:z.pastimeFrames,fps:z.fps,loops:!1,postures:Ye,voices:["homie"],pose:GS},{name:"shield_polish",head:se.gestures,frames:z.pastimeFrames,fps:z.fps,loops:!1,postures:Ye,voices:["squire"],pose:VS},{name:"bow",head:se.gestures,frames:z.greetingFrames,fps:z.fps,loops:!1,postures:Ye,voices:["butler"],pose:qS},{name:"salute",head:se.gestures,frames:z.greetingFrames,fps:z.fps,loops:!1,postures:Ye,voices:["squire"],pose:$S},{name:"startled",head:se.gestures,frames:z.hopFrames,fps:z.fps,loops:!1,postures:Ye,pose:jS},{name:"stumble",head:se.gestures,frames:z.stumbleFrames,fps:z.fps,loops:!1,postures:["walk"],pose:YS},{name:"glance",head:se.holds,frames:z.greetingFrames,fps:z.fps,loops:!1,postures:Ye,pose:KS},{name:"work",head:se.free,frames:gt.blows*gt.blowFrames,fps:gt.fps,loops:!0,postures:["stand","sit"],pose:JS},{name:"inspect",head:se.holds,frames:Jt.frames,fps:Jt.fps,loops:!0,postures:["stand"],pose:t1},{name:"point",head:se.gestures,frames:12,fps:8,loops:!0,postures:Ye,pose:a1},{name:"watch",head:se.free,frames:8,fps:8,loops:!0,cuts:!0,postures:["stand","sit"],pose:s1},{name:"push",head:se.holds,frames:bn.intro+bn.stride,intro:bn.intro,fps:bn.fps,loops:!0,legs:!0,postures:["walk","stand"],pose:o1},{name:"jump",head:se.gestures,frames:16,fps:20,loops:!1,postures:wt,pose:c1},{name:"tickle_swat",head:se.free,frames:24,fps:16,loops:!1,cuts:!0,postures:Ye,pose:rE},{name:"disco",head:se.holds,frames:ie.disco.frames,fps:ie.disco.fps,loops:!1,postures:wt,pose:oE},{name:"bug_shot",head:se.holds,frames:ie.bug_shot.frames,fps:ie.bug_shot.fps,loops:!1,postures:wt,pose:pE},{name:"bug_smash",head:se.holds,frames:ie.bug_smash.frames,fps:ie.bug_smash.fps,loops:!1,postures:wt,pose:gE},{name:"halo",head:se.gestures,frames:ie.halo.frames,fps:ie.halo.fps,loops:!1,postures:wt,pose:_E},{name:"repent",head:se.holds,frames:ie.repent.frames,fps:ie.repent.fps,loops:!1,postures:wt,rises:!0,pose:yE},{name:"pogo",head:se.holds,frames:ie.pogo.frames,fps:ie.pogo.fps,loops:!1,postures:wt,pose:bE},{name:"fall",head:se.gestures,frames:12,fps:12,loops:!1,interruptible:!0,postures:wt,pose:d1},{name:"backflip",head:se.holds,frames:22,fps:20,loops:!1,postures:wt,pose:u1},{name:"land",head:se.gestures,frames:_h.frames,fps:_h.fps,loops:!1,postures:wt,pose:f1},{name:"type",head:se.holds,frames:24,fps:8,loops:!0,leaves:8,least:uf,aside:!0,postures:Zs,pose:Wb},{name:"joy",head:se.gestures,frames:ie.joy.frames,fps:ie.joy.fps,loops:!1,postures:Ye,pose:Xb},{name:"dismay",head:se.gestures,frames:28,fps:10,loops:!1,postures:Ye,pose:qb},{name:"stretch",head:se.gestures,frames:24,fps:8,loops:!1,postures:Ye,pose:$b},{name:"squire_chase",head:se.gestures,frames:24,fps:12,loops:!1,postures:wt,pose:p1},{name:"pointed",head:se.gestures,frames:20,fps:10,loops:!1,postures:wt,pose:y1},{name:"hat_tip",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,holds:!0,postures:Ye,voices:["butler"],pose:w1},{name:"monocle",head:se.holds,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["butler"],pose:S1},{name:"toast",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["butler"],pose:E1},{name:"shaka",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["homie"],pose:T1},{name:"shades",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["homie"],pose:A1},{name:"fire",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["homie"],pose:R1},{name:"thumbs_up",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["colleague"],pose:C1},{name:"peer",head:se.holds,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["colleague"],pose:P1},{name:"thanks",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,pose:L1},{name:"party_popper",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["coach"],pose:I1},{name:"flex",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["coach"],pose:D1},{name:"trophy",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["coach"],pose:N1},{name:"sword",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["squire"],pose:U1},{name:"shield_up",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["squire"],pose:O1},{name:"castle",head:se.gestures,frames:pe.frames,fps:pe.fps,loops:!1,postures:Ye,voices:["squire"],pose:F1},{name:"ask_sign",head:se.gestures,frames:ie.ask_sign.frames,fps:ie.ask_sign.fps,loops:!1,postures:Ye,pose:W1},{name:"scroll",head:se.holds,frames:ie.scroll.frames,fps:ie.scroll.fps,loops:!1,postures:Ye,pose:X1},{name:"file_card",head:se.gestures,frames:ie.file_card.frames,fps:ie.file_card.fps,loops:!1,postures:wt,pose:$1},{name:"pack_box",head:se.gestures,frames:ie.pack_box.intro+ie.pack_box.hold+ie.pack_box.outro,intro:ie.pack_box.intro,outro:ie.pack_box.outro,leaves:ie.pack_box.hold,fps:ie.pack_box.fps,loops:!0,postures:wt,pose:j1},{name:"press",head:se.gestures,frames:ie.press.intro+ie.press.hold+ie.press.outro,intro:ie.press.intro,outro:ie.press.outro,leaves:ie.press.hold,fps:ie.press.fps,loops:!0,postures:Ye,pose:Y1},{name:"vacuum",head:se.gestures,frames:ie.vacuum.intro+ie.vacuum.hold+ie.vacuum.outro,intro:ie.vacuum.intro,outro:ie.vacuum.outro,leaves:ie.vacuum.hold,fps:ie.vacuum.fps,loops:!0,postures:wt,pose:K1},{name:"eager",head:se.free,frames:$i.intro+$i.hold+$i.outro,intro:$i.intro,outro:$i.outro,leaves:$i.hold,fps:$i.fps,loops:!0,holds:!0,postures:wt,pose:Z1},{name:"fume",head:se.gestures,frames:ie.fume.frames,fps:ie.fume.fps,loops:!1,cuts:!0,postures:wt,pose:J1},{name:"look_left",head:se.holds,frames:li.frames,fps:li.fps,loops:!1,postures:Ye,pose:hl(-1,0)},{name:"look_right",head:se.holds,frames:li.frames,fps:li.fps,loops:!1,postures:Ye,pose:hl(1,0)},{name:"look_up",head:se.holds,frames:li.frames,fps:li.fps,loops:!1,postures:Ye,pose:hl(0,1)},{name:"tumble",head:se.holds,frames:Gn.frames,fps:Gn.fps,loops:!1,postures:wt,pose:Q1},{name:"ledge_sit",head:se.free,frames:32,fps:8,loops:!0,leaves:8,postures:Zs,pose:eE},{name:"pocket_watch",head:se.holds,frames:48,fps:10,loops:!0,postures:Zs,pose:tE},{name:"doze",head:se.holds,frames:48,fps:8,loops:!0,leaves:24,postures:Zs,pose:nE},{name:"hop_up",head:se.free,frames:8,fps:16,loops:!0,interruptible:!0,cuts:!0,postures:wt,pose:iE},{name:"rope_swing",head:se.gestures,frames:ie.rope_swing.intro+ie.rope_swing.hold+ie.rope_swing.outro,intro:ie.rope_swing.intro,outro:ie.rope_swing.outro,leaves:ie.rope_swing.hold,fps:ie.rope_swing.fps,loops:!0,postures:Zs,pose:EE},{name:"chute",head:se.holds,frames:ie.chute.frames,fps:ie.chute.fps,loops:!0,interruptible:!0,cuts:!0,postures:wt,pose:AE},{name:"binoculars",head:se.holds,frames:ie.binoculars.frames,fps:ie.binoculars.fps,loops:!0,postures:NE,pose:RE},{name:"rummage",head:se.holds,frames:ie.rummage.frames,fps:ie.rummage.fps,loops:!0,postures:wt,pose:CE},{name:"type_ponder",head:se.holds,frames:ie.type_ponder.frames,fps:ie.type_ponder.fps,loops:!0,leaves:8,least:uf,aside:!0,postures:Zs,pose:PE},{name:"wipe_brow",head:se.gestures,frames:z.greetingFrames,fps:z.fps,loops:!1,postures:Ye,pose:LE},{name:"wave_up",head:se.gestures,frames:12,fps:12,loops:!0,cuts:!0,postures:["stand","sit"],pose:IE}],im=`
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
`,UE=`
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
`,df=(i,e,t,n,s,r)=>{const o=i.getContext("2d");o.clearRect(0,0,i.width,i.height),o.filter="none",o.imageSmoothingEnabled=!0,o.imageSmoothingQuality="high",o.drawImage(e,t,n,s,r,0,0,i.width,i.height)},OE=["headphones"],ji={gap:.16,dark:.35,glass:[.006,.007,.01],shine:{lift:1,core:.55,tightness:6},framesBehind:6},FE=`
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
    uniform float dark;
    uniform vec3 glass;
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
        // the dark lines between the pixels, gap of each pixel wide, centred on the borders between
        // pixels, their edges blended over one drawn fragment so a screen drawn small shows no jagged steps or shimmer
        vec2 lines = clamp(vec2(gap), 0.0, 0.5);
        vec2 border = min(cell, 1.0 - cell);
        vec2 blend = fwidth(place) * 0.5;
        vec2 edges = smoothstep(lines * 0.5 - blend, lines * 0.5 + blend, border);
        float pixel = edges.x * edges.y;
        vec4 shown = pixelAt(floor(place));
        // the face: the glass alone, one plain colour, the lit pixels the only thing on it
        vec3 screen = glass;
        vec2 offMiddle = cell - 0.5;
        vec3 glowing = shown.rgb * (1.0 + shine.x) + shine.y * exp(-dot(offMiddle, offMiddle) * shine.z) * mix(shown.rgb, vec3(1.0), 0.5);
        vec3 drawn = mix(screen, glowing, shown.a * pixel);
        float centre = max(1.0 - length(from), 0.0);
        vec3 shine = glow * lit * mix(dark, 1.0, pixel);
        vec3 lighted = mix(shine + (vec3(1.0) - glow) * core * centre * centre * pixel, vec3(1.0), flash);
        gl_FragColor = vec4(mix(drawn * (1.0 - step(0.001, lit + flash) * 0.6), lighted, band * max(lit, flash)), 1.0);
        #include <colorspace_fragment>
    }
`;function BE(i){const e=nu(i);e.fragmentShader=FE;const t=new an().setFromBufferAttribute(i.geometry.attributes.position),n=t.getCenter(new v),s=t.getSize(new v).multiplyScalar(.5);return Object.assign(e.uniforms,{glow:{value:new v},lit:{value:0},across:{value:0},open:{value:0},flash:{value:0},core:{value:Em.core},middle:{value:new re(n.x,n.y)},extent:{value:new re(s.x,s.y)},pixels:{value:WE()},grid:{value:new re(Ss.columns,Ss.rows)},gap:{value:ji.gap},dark:{value:ji.dark},glass:{value:new v(...ji.glass)},shine:{value:new v(ji.shine.lift,ji.shine.core,ji.shine.tightness)}}),e}const fl={depth:.06,behind:fp+.014},kE=i=>i.name==="head_shell"||i.name.endsWith("__shell");function ff(i,e=.05){const t=i.attributes.position,n=a=>i.index?i.index.getX(a):a,s=i.index?i.index.count:t.count,r=(a,c)=>a*100003+c,o=new Map;for(let a=0;a<s;a+=3){const c=[0,1,2].map(g=>{const p=n(a+g);return{x:t.getX(p),y:t.getY(p),z:t.getZ(p)}}),[l,h,u]=c,[d,f]=[Math.floor(Math.min(l.x,h.x,u.x)/e),Math.floor(Math.max(l.x,h.x,u.x)/e)],[m,_]=[Math.floor(Math.min(l.y,h.y,u.y)/e),Math.floor(Math.max(l.y,h.y,u.y)/e)];for(let g=d;g<=f;g++)for(let p=m;p<=_;p++){const y=r(g,p);o.has(y)||o.set(y,[]),o.get(y).push(c)}}return(a,c)=>(o.get(r(Math.floor(a/e),Math.floor(c/e)))??[]).reduce((l,h)=>{const u=zE(h,a,c);return u===null||l!==null&&l>=u?l:u},null)}function zE([i,e,t],n,s){const r=(e.x-i.x)*(t.y-i.y)-(t.x-i.x)*(e.y-i.y);if(Math.abs(r)<1e-12)return null;const o=((e.x-n)*(t.y-s)-(t.x-n)*(e.y-s))/r,a=((t.x-n)*(i.y-s)-(i.x-n)*(t.y-s))/r,c=1-o-a;return o>=-1e-9&&a>=-1e-9&&c>=-1e-9?o*i.z+a*e.z+c*t.z:null}const HE=(i,e,t)=>i.map(n=>n(e,t)).reduce((n,s)=>s===null||n!==null&&n>=s?n:s,null);function GE(i,e){const t=e.map(o=>ff(o)),n=i.attributes.position;let s=-1/0;for(let o=0;o<n.count;o++)s=Math.max(s,n.getZ(o)-(HE(t,n.getX(o),n.getY(o))??1/0));i.translate(0,0,-(s+fl.depth));const r=ff(i);for(const o of e){const a=o.attributes.position;for(let c=0;c<a.count;c++){const l=r(a.getX(c),a.getY(c));l!==null&&a.getZ(c)>l-fl.behind&&a.setZ(c,l-fl.behind)}a.needsUpdate=!0}}function VE(i,e,t){var o,a;const n=(o=i.userData).waiting??(o.waiting=[]),s=e.map(({column:c,row:l,colour:h})=>`${c},${l},${h.join(",")}`).join(";");if(s!==(((a=n.at(-1))==null?void 0:a.key)??i.userData.shownKey)&&n.push({key:s,lit:e}),n.length>ji.framesBehind&&n.splice(0,n.length-ji.framesBehind),i.userData.frame===t||!n.length)return;const r=n.shift();XE(i.uniforms.pixels.value,r.lit),i.userData.shownKey=r.key,i.userData.frame=t}function WE(){const i=new Nh(new Uint8Array(Ss.columns*Ss.rows*4),Ss.columns,Ss.rows);return i.magFilter=i.minFilter=xn,i.needsUpdate=!0,i}function XE(i,e){const t=i.image.data;t.fill(0);for(const{column:n,row:s,colour:r}of e)t.set([...r.map(o=>Math.round(o*255)),255],(s*Ss.columns+n)*4);i.needsUpdate=!0}const qE=`
    uniform vec3 colour;

    void main() {
        gl_FragColor = vec4(colour, 1.0);
        #include <colorspace_fragment>
    }
`,sm=(i,e)=>({push:{value:e/i.getWorldScale(new v).x}});function nu(i){const{r:e,g:t,b:n}=i.material.color;return new di({vertexShader:im,fragmentShader:UE,side:Pn,uniforms:{...sm(i,0),colour:{value:new v(e,t,n)},light:{value:rb.clone().normalize().applyMatrix4(Pr)},shade:{value:dh},litFrom:{value:ob},bulbAt:{value:new v},bulbGlow:{value:new v},bulbFalloff:{value:hr.falloff}}})}function rm(i){return new di({vertexShader:im,fragmentShader:qE,side:Sn,defines:{HULL:""},uniforms:{...sm(i,fp),colour:{value:ab}}})}const $E=-.5;function iu(i){const e=i.attributes.position,t=Array.from({length:e.count},(o,a)=>new v().fromBufferAttribute(i.attributes.normal,a)),n=new Map,s=o=>`${e.getX(o).toFixed(5)},${e.getY(o).toFixed(5)},${e.getZ(o).toFixed(5)}`;for(let o=0;o<e.count;o++){const a=n.get(s(o))??[];a.push(o),n.set(s(o),a)}const r=new Float32Array(e.count*3);for(let o=0;o<e.count;o++){const a=new v;for(const c of n.get(s(o)).filter(l=>t[o].dot(t[l])>$E))a.add(t[c]);a.normalize().toArray(r,o*3)}i.setAttribute("hullNormal",new on(r,3))}function Kr(i,e){const t=new Set;for(const n of i.filter(s=>e.has(s.userData.item)))t.add(new an().setFromObject(n).getCenter(new v).x>=0?"l":"r");return t}function jE(i){const e=[];i.traverse(a=>a.isBone&&e.push(a));const t=new Map(e.map(a=>[a.name,a.parent.isBone?a.parent.name:""])),n=new Map(e.map(a=>[a.name,a.matrixWorld.clone()])),s=new Map(e.map(a=>[a.name,xo(new v().setFromMatrixPosition(a.matrixWorld))])),r=new Map(e.map(a=>[a.name,new v().setFromMatrixColumn(a.matrixWorld,1).transformDirection(ic)])),o=[];return i.traverse(a=>{!a.isSkinnedMesh||!a.name.startsWith("eye_")||!a.userData.hull||o.push(xo(new an().setFromBufferAttribute(a.geometry.attributes.position).getCenter(new v).applyMatrix4(a.matrixWorld)))}),{bones:e,order:e.map(a=>a.name),parents:t,rest:n,heads:s,along:r,eyes:o}}async function YE(i){const e=await xl.raw(i);if(e.ok)return e.arrayBuffer();const t=await xl.raw(`${i}.txt`).then(n=>n.text());return Uint8Array.from(atob(t),n=>n.charCodeAt(0)).buffer}async function rA(i,e,t){const[n,s]=await Promise.all([YE(i),xl.raw(e).then(a=>a.json())]),r=t==="bare",o=new Set((r?[]:s.outfits[t]).flatMap(a=>s.assets[a].hide_base_parts));return ZE(n,t,eb,a=>!o.has(a.name)&&!(r&&a.userData.item))}const KE={butler:mw};async function ZE(i,e,t,n=()=>!0){const r=(await new gw().setDRACOLoader(new Zw().setDecoderPath(t)).parseAsync(i,"")).scene;r.updateMatrixWorld(!0);const o=[];r.traverse(A=>A.isSkinnedMesh&&o.push(A));const a=(KE[e]??(A=>A))(o);GE(a.find(A=>A.name===_a).geometry,a.filter(kE).map(A=>A.geometry));const c=[],l=[];for(const A of a){A.visible=n(A)&&!db.has(A.userData.item)&&A.userData.item!==nl,iu(A.geometry);const E=new Dh(A.geometry,rm(A));E.bind(A.skeleton,A.bindMatrix),E.visible=A.visible,A.userData.hull=E,E.userData.item=A.userData.item,E.frustumCulled=A.frustumCulled=!1,A.material=A.name===_a?BE(A):nu(A),A.name===_a&&c.push(A.material),A.name===_a&&l.push(E),A.parent.add(E),E.position.copy(A.position),E.quaternion.copy(A.quaternion),E.scale.copy(A.scale),A.name.startsWith("eye_")&&(A.visible=E.visible=!1),OE.some(P=>A.name.startsWith(P))&&(A.visible=E.visible=!1)}const h=a.filter(A=>A.visible),u=Kr(h,nc),d=a.filter(A=>A.userData.item===nl&&n(A)),f={voice:e,level:Kr(h,xp),busy:u,carried:Kr(h,Mt),free:new Set(Object.keys(N).filter(A=>!u.has(A))),tablet:Kr(d,new Set([nl])),shield:Kr(h,new Set(["squire_shield"]))},m=QE(),_=PT(),g=oT();r.add(m,_,...g.values());const p={bulbAt:{value:new v},bulbGlow:{value:new v}};r.traverse(A=>{var E,P;return((P=(E=A.material)==null?void 0:E.uniforms)==null?void 0:P.bulbGlow)&&Object.assign(A.material.uniforms,p)});const y=A=>A.flatMap(E=>[E,E.userData.hull]),M=h.filter(A=>Mt.has(A.userData.item)),x=y(h.filter(A=>A.userData.item));return{scene:r,rig:jE(r),stance:f,screens:c,visorHulls:l,laptop:m,book:_,propByName:g,props:[...g.values()],stowable:x,tablet:y(d),inHand:y(M),bulbLight:p}}const JE={width:1.7,depth:.62,thickness:.1,open:105},Zr={base:4672082,lid:2829880,screen:1776932,edge:11120056,mark:6186185},rs=(i,e)=>{const t=new jt(i,new _n({color:e,side:Pn}));return t.frustumCulled=!1,t};function QE(){const{width:i,depth:e,thickness:t,open:n}=JE,s=(u,d,f,m)=>{const _=rs(new ut(d,f,m),u);return _.add(new wo(new Za(_.geometry),new Rs({color:Zr.edge}))),_},r=s(Zr.base,i,t,e);r.position.set(0,t/2,-e/2);const o=s(Zr.lid,i,e,t);o.position.set(0,e/2,t/2);const a=rs(new fi(i*.88,e*.82),Zr.screen);a.position.set(0,e/2,-.002);const c=rs(new Oi(e*.12,20),Zr.mark);c.position.set(0,e/2,t+.002);const l=new Ut;l.position.y=t,l.rotation.x=Xe(n-90),l.add(o,a,c);const h=new Ut;return h.matrixAutoUpdate=!1,h.visible=!1,h.add(r,l),h}const Qs={lights:[.144,.267,.389,.511],light:.047,vents:[.633,.711,.789,.867],vent:[.033,.49]},er={front:1842725,top:2895673,side:1184536,vent:329224,edge:4869724};function eT(i){const e=ls.width*i,t=Math.asin(ls.top/ls.width),n=(ls.height-ls.top)*i/Math.cos(t)/ls.units,[s,r,o]=[er.side,er.top,er.front].map(u=>new _n({color:u})),a=[],c=Array.from({length:ls.units},(u,d)=>{const f=new jt(new ut(e,n,e),[s,s,r,s,o,s]);f.add(new wo(new Za(f.geometry),new Rs({color:er.edge}))),f.position.set(0,n*(d+.5),-e/2);const m=(_,g)=>(_.position.set(e*(g-.5),0,e/2+.002),f.add(_),_);return a.push(...Qs.lights.map(_=>m(new jt(new Oi(e*Qs.light,12),new _n),_))),Qs.vents.forEach(_=>m(rs(new fi(e*Qs.vent[0],n*Qs.vent[1]),er.vent),_)),f}),l=new Ut;l.rotation.x=t,l.add(...c);const h=new ja;return h.add(l),h.updateMatrixWorld(!0),{scene:h,lights:a,bounds:new an().setFromObject(l)}}function tT(i,e,t){const n=new Ve(er.front);i.lights.forEach((s,r)=>{const o=new Ve().setRGB(...Cm[e],Yt);s.material.color.copy(n.clone().lerp(o,Pm(e,t,r%Qs.lights.length)))})}const Vt={hull:[[0,-.27],[.32,-.29],[.64,-.2],[.92,-.06],[1,0],[.93,.07],[.62,.15],[.38,.19],[0,.2]],band:.04,dome:.4,antenna:[.16,.05],lights:10,light:.075,lamp:.26,tilt:16,colours:{hull:12172744,band:6119792,dome:13625087,antenna:6119792,dark:3816778,lamp:16774056,lit:[15251530,6514417]}};function nT(i){const e=Ra.width/2*i,t=new Ut;t.name="saucer";const n=new Ar(Vt.hull.map(([h,u])=>new re(h*e,u*e)),48);Ae(t,"hull",n,Vt.colours.hull),Ae(t,"band",new jn(e*.985,e*Vt.band,8,64),Vt.colours.band).rotation.x=Math.PI/2;const s=Vt.hull.at(-1)[1]*e*.9;Ae(t,"dome",new En(e*Vt.dome,32,16,0,Math.PI*2,0,Math.PI/2),Vt.colours.dome,[0,s,0]);const[r,o]=Vt.antenna.map(h=>h*e);Ae(t,"antenna",new tt(o*.25,o*.25,r,8),Vt.colours.antenna,[0,s+e*Vt.dome+r/2,0]),Ae(t,"ball",new En(o,12,8),Vt.colours.lit[0],[0,s+e*Vt.dome+r,0]);const a=Array.from({length:Vt.lights},(h,u)=>{const d=u/Vt.lights*Math.PI*2;return Ae(t,`light_${u}`,new En(e*Vt.light,12,8),Vt.colours.dark,[Math.sin(d)*e,0,Math.cos(d)*e])}),c=-(Ra.belly*i)/Math.cos(Xe(Vt.tilt));Ae(t,"lamp",new tt(e*Vt.lamp,e*Vt.lamp*1.15,e*.07,24),Vt.colours.lamp,[0,c,0]),t.rotation.x=Xe(Vt.tilt),t.position.y=Fn;const l=new ja;return l.add(t),l.updateMatrixWorld(!0),{scene:l,lights:a,middle:new v(0,Fn,0),bounds:new an().setFromObject(t)}}function iT(i,e){i.lights.forEach((t,n)=>{const s=new Ve(n%Ra.blink===e?Vt.colours.lit[Math.floor(n/Ra.blink)%2]:Vt.colours.dark);t.material.uniforms.colour.value.set(s.r,s.g,s.b)})}const Rn={panels:8,reach:1.15,flat:.62,vent:.14,tilt:14,lines:[-.35,.35],colours:{gores:[14238011,16183779],vent:9382438}};function sT(i,e){const t=ie.chute.width*e/2/Math.sin(Rn.reach)*i,n=new Ut;n.name="canopy";const s=new Ut;s.name="canopy",s.scale.y=Rn.flat,n.add(s);for(let u=0;u<Rn.panels;u++){const d=new En(t,8,10,u/Rn.panels*Math.PI*2,Math.PI*2/Rn.panels,0,Rn.reach);Ae(s,`gore_${u}`,d,Rn.colours.gores[u%2])}Ae(s,"vent",new En(t*1.01,16,4,0,Math.PI*2,0,Rn.vent),Rn.colours.vent);const r=t*Math.sin(Rn.reach),o=t*Math.cos(Rn.reach)*Rn.flat,c=[-1,1].flatMap(u=>Rn.lines.map(d=>new v(u*r*Math.cos(d),o,r*Math.sin(d)))).map(u=>{const d=new kt;return d.position.copy(u),n.add(d),d});n.rotation.x=Xe(Rn.tilt),n.position.y=Fn-o;const l=new ja;l.add(n),l.updateMatrixWorld(!0);const h=new v(0,o,0).applyMatrix4(n.matrixWorld);return{scene:l,middle:h,ends:c.map(u=>new v().setFromMatrixPosition(u.matrixWorld)),bounds:new an().setFromObject(n)}}const yo={radius:.52,rim:.08,handle:.5,grip:.07},Jr={rim:2829880,lens:13625087,handle:4672082,edge:11120056,glint:16777215};function rT(i){const{radius:e,rim:t,handle:n,grip:s}=yo,r=(u,d,f={})=>{const m=new jt(u,new _n({color:d,side:Pn,...f}));return m.frustumCulled=!1,m},o=new Ut;i.add(o);const a=r(new jn(e,t,12,48),Jr.rim);a.position.y=n/2+e,a.add(new wo(new Za(new Oi(e+t,48)),new Rs({color:Jr.edge})));const c=r(new Oi(e,48),Jr.lens,{transparent:!0,opacity:.18,depthWrite:!1});c.position.y=n/2+e;const l=r(new Gh(e*.55,e*.72,24,1,Math.PI*.55,Math.PI*.4),Jr.glint);l.position.set(0,n/2+e,.008);const h=r(new tt(s,s*1.2,n,16),Jr.handle);o.add(h,a,c,l),i.userData.shape=({magnifies:u=0,size:d=1,roll:f=0})=>{o.scale.setScalar(u?d:1),l.rotation.z=Xe(f)}}const Ue={width:.82,height:1.2,cover:.055,pages:.06,spine:.18,inset:.035,open:160,tilt:8,gripHeight:.02,gripSide:.1,closedGrip:.2,gripBack:.6,leaf:.004,curl:2,pageSegments:12,pageBow:.24,lines:5,lineWidth:.004},vs={cover:6514417,spine:3487563,pages:15986399,paper:16776175,edge:2303282,rule:13024940},om=i=>Xe((180-Ue.open*i)/2);function vh(i,e){const t=N[i],n=i==="l"?1:e;return new v(t*Ue.width*n,Ue.gripHeight,Ue.cover/2).applyAxisAngle(new v(0,1,0),t*om(e)).add(new v(t*Ue.spine/2,0,0))}function am(i){const e=vh("l",i).sub(vh("r",i)).normalize(),t=new v(0,1,0);return new ge().makeBasis(e,t,e.clone().cross(t))}function cm(i){return new ge().makeRotationX(Xe(Ue.tilt)).multiply(am(i).invert())}function ts(i,e){const t=am(e),n=new v().setFromMatrixColumn(t,0),s=new v().setFromMatrixColumn(t,2);return vh(i,e).addScaledVector(n,N[i]*(Ue.gripSide+Ue.closedGrip*(1-e))).addScaledVector(s,-Ue.gripBack)}const sn={pen:{radius:.027,length:.58,tip:.08,sides:12,markerScale:1.8,pencilSides:6,bandScale:1.05,bandAt:1/3},feather:{at:1/4,points:[[0,0],[-.12,.18],[-.08,.42],[.03,.6],[.14,.34],[.1,.12]]},paper:{width:1.58,depth:.54,thickness:.012,count:4,spread:.04,tabletLayers:3,screenWidth:.91,screenDepth:.85,screenLift:2},whistle:{body:[.13,.1,.16],mouthpiece:[.08,.04,.15],mouthAt:[0,.01,-.12]},cloth:{width:.35,depth:.26,thickness:.02},hammer:{handleRadius:.06,handleLength:1.2,gripFrom:.15,head:[.55,.22,.22],sides:10,tilt:45},straw:{radius:.03,length:.7,head:[.045,.16]},colours:{ink:2566454,silver:11120056,paper:15986399,white:16052973,accent:6514417,pencil:14069867,handle:9067051,straw:15255146}};function oT(){const i=new Map,e=f=>{const m=new Ut;return m.name=f,m.visible=!1,m.matrixAutoUpdate=!1,i.set(f,m),m},t=(f,m,_,g,p=[0,0,0])=>{const y=rs(_,g);return y.name=`${f.name}_${m}`,y.position.set(...p),f.add(y),y},{pen:n,paper:s,cloth:r,colours:o}=sn;for(const f of Object.values(Np)){const m=e(f),_=f==="writing_marker",g=f==="writing_pencil",p=n.radius*(_?n.markerScale:1);t(m,"barrel",new tt(p,p,n.length,g?n.pencilSides:n.sides),g?o.pencil:o.ink);const y=t(m,"nib",new hi(p,n.tip,n.sides),o.silver,[0,-(n.length+n.tip)/2,0]);if(y.rotation.z=Math.PI,t(m,"band",new tt(p*n.bandScale,p*n.bandScale,n.tip/2,n.sides),o.accent,[0,n.length*n.bandAt,0]),f==="writing_quill"){const x=new Ls;x.moveTo(...sn.feather.points[0]);for(const A of sn.feather.points.slice(1))x.lineTo(...A);x.closePath(),t(m,"feather",new ec(x),o.white,[0,n.length*sn.feather.at,0])}const M=new kt;M.name="tip",M.position.y=-n.length/2-n.tip,m.add(M),m.userData.tip=M}for(const f of["papers","writing_paper","writing_tablet"]){const m=e(f),_=f==="writing_tablet",g=f==="papers"?s.count:1;m.userData.sheets=[];for(let p=0;p<g;p++){const y=t(m,`sheet_${p}`,new ut(s.width,s.thickness*(_?s.tabletLayers:1),s.depth),_?o.ink:o.paper,[0,p*s.thickness,0]);m.userData.sheets.push(y)}_&&t(m,"screen",new ut(s.width*s.screenWidth,s.thickness,s.depth*s.screenDepth),o.accent,[0,s.thickness*s.screenLift,0])}i.get("papers").userData.shape=({phase:f})=>{const m=Q(f,0,.3)*(1-Q(f,.8,1));i.get("papers").userData.sheets.forEach((_,g)=>{_.position.x=s.spread*g*(1-m),_.rotation.y=s.spread*g*(1-m)})};const a=e("hand_whistle");t(a,"body",new ut(...sn.whistle.body),o.accent),t(a,"mouthpiece",new ut(...sn.whistle.mouthpiece),o.silver,sn.whistle.mouthAt);const{hammer:c}=sn,l=e("work_hammer");t(l,"handle",new tt(c.handleRadius,c.handleRadius,c.handleLength,c.sides),o.handle,[0,c.handleLength/2-c.gripFrom,0]),t(l,"head",new ut(...c.head),o.silver,[0,c.handleLength-c.gripFrom,0]);const{straw:h}=sn,u=e("straw");t(u,"stalk",new tt(h.radius,h.radius,h.length,6),o.straw,[0,h.length/2,0]),t(u,"seeds",new hi(...h.head,6),o.pencil,[0,h.length+h.head[1]/2,0]),rT(e("magnifying_glass"));const d=e("polishing_cloth");return t(d,"fold",new ut(r.width,r.thickness,r.depth),o.white),TT(e,t),ST(e("telephone"),e("telephone_handset"),e("telephone_cord"),e("telephone_poof")),wT(e("light_bulb")),MT(e("report_scroll")),yT(e("binoculars")),hT(e("rifle")),uT(e("big_mallet")),dT(e("halo")),pT(e("crucifix")),gT(e("pocket_watch")),xT(e("rope_swing")),cT(e),i}const aT={papers:{sheet:[.9,.02,.66],count:3,fan:18},boot:{shaft:[.4,.72,.45],foot:[.4,.3,.84],sole:.07},bone:{spine:1.1,ribs:5,rib:.5,head:[.24,.18,.08],tail:[.2,.26],thick:.035},book:{cover:[.75,.15,.56],pages:[.7,.12,.53]},colours:{paper:16183779,leather:7029798,sole:2761760,bone:15525074,cover:11022906,pages:15985362}};function cT(i){const{papers:e,boot:t,bone:n,book:s,colours:r}=aT,o=[],a=_=>{const g=i(_),p=new Ut;return p.name=_,g.add(p),g.userData.shape=({size:y=1})=>p.scale.setScalar(Math.max(y,.001)),o.push(p),p},c=a("rummage_papers");for(let _=0;_<e.count;_++){const g=Ae(c,`sheet_${_}`,new ut(...e.sheet),r.paper,[0,_*e.sheet[1]*2,0]);g.rotation.y=Xe(e.fan*(_-(e.count-1)/2))}const l=a("rummage_boot");Ae(l,"shaft",new ut(...t.shaft),r.leather,[0,t.foot[1]+t.shaft[1]/2,0]),Ae(l,"foot",new ut(...t.foot),r.leather,[0,t.foot[1]/2,(t.foot[2]-t.shaft[2])/2]),Ae(l,"sole",new ut(t.foot[0]*1.05,t.sole,t.foot[2]*1.04),r.sole,[0,0,(t.foot[2]-t.shaft[2])/2]);const h=a("rummage_bone"),u=Ae(h,"spine",new tt(n.thick,n.thick,n.spine,6),r.bone);u.rotation.z=Math.PI/2;for(let _=0;_<n.ribs;_++){const g=(_/(n.ribs-1)-.5)*n.spine*.7,p=n.rib*(1-Math.abs(g)/n.spine);Ae(h,`rib_${_}`,new tt(n.thick*.7,n.thick*.7,p,5),r.bone,[g,0,0])}Ae(h,"head",new En(1,14,10),r.bone,[n.spine/2+n.head[0]*.8,0,0]).scale.set(...n.head);const f=Ae(h,"tail",new hi(n.tail[0],n.tail[1],3),r.bone,[-n.spine/2-n.tail[1]/2,0,0]);f.rotation.z=-Math.PI/2;const m=a("rummage_book");Ae(m,"cover",new ut(...s.cover),r.cover),Ae(m,"pages",new ut(...s.pages),r.pages,[(s.cover[0]-s.pages[0])/2+.03,0,0]);for(const _ of o){_.updateMatrixWorld(!0);const g=new an().setFromObject(_).getCenter(new v).sub(_.getWorldPosition(new v));for(const p of _.children)p.position.sub(g)}}const lT={barrel:.24,length:.6,apart:.54,rim:.045,eyepiece:[.15,.14],bridge:[.28,.13,.22],colours:{body:2763830,rim:10133677,eyepiece:1776674,lens:9356799}},ir={scale:1.4,stock:[[-.42,0,0],[.5,.09,.16]],receiver:[[.1,0,.04],[.46,.1,.14]],grip:[[-.03,0,-.1],[.08,.08,.2]],magazine:[[.2,0,-.15],[.1,.07,.26]],handguard:[[.55,0,.04],[.42,.1,.11]],sight:[[.24,0,.14],[.06,.04,.06]],front:[[1.17,0,.11],[.03,.03,.07]],barrel:{from:.76,to:1.24,radius:.03,up:.06},colours:{wood:9067051,metal:2829880,barrel:4672082,flash:16765530}},sr={barrel:ir.barrel.up*ir.scale,fore:.55*ir.scale,nearest:.38*ir.scale,under:.17,roll:90,low:.5};function Ur(i){const e=new Ut;return e.name=i.name,e.rotation.x=-Math.PI/2,i.add(e),e}function hT(i){const e=Ur(i),{colours:t,barrel:n,scale:s}=ir,r=d=>d.map(f=>f*s);for(const d of["stock","receiver","grip","magazine","handguard","sight","front"]){const[f,m]=ir[d];Ae(e,d,new ut(...r(m)),["stock","handguard"].includes(d)?t.wood:t.metal,r(f))}const[o,a,c,l]=r([n.from,n.to,n.radius,n.up]),h=Ae(e,"barrel",new tt(c,c,a-o,12),t.barrel,[(o+a)/2,0,l]);h.rotation.z=Math.PI/2;const u=Ae(e,"flash",new Hh(.12*s,0),t.flash,[a+.1*s,0,l]);u.scale.set(1.6,.6,1),i.userData.shape=({firing:d})=>u.visible=!!d}const no={handle:2,grip:.06,head:.42,width:.85,band:.04,colours:{handle:11565637,head:10185274,band:7040892}};function uT(i){const e=Ur(i),{handle:t,grip:n,head:s,width:r,band:o,colours:a}=no;Ae(e,"handle",new tt(n,n*1.2,t,12),a.handle,[t/2,0,0]).rotation.z=Math.PI/2,Ae(e,"head",new tt(s,s,r,20),a.head,[t,0,0]).rotation.x=Math.PI/2;for(const c of[-1,1])Ae(e,`band_${c}`,new tt(s*1.04,s*1.04,o,20),a.band,[t,0,c*(r/2-o)]).rotation.x=Math.PI/2}function dT(i){const e=Ae(Ur(i),"ring",new jn(lo.radius,lo.ring,10,40),15910987);e.rotation.x=Xe(lo.tip),i.userData.shape=({size:t})=>e.scale.setScalar(t??1)}const fT={long:.62,across:.32,bar:.075,at:.14,colours:{wood:14263361,gold:16180129}};function pT(i){const e=Ur(i),{long:t,across:n,bar:s,at:r,colours:o}=fT;Ae(e,"upright",new ut(s,s,t),o.wood,[0,0,t*.2]),Ae(e,"crossbar",new ut(n,s,s),o.wood,[0,0,t*.2+r]),Ae(e,"centre",new En(s*.7,10,8),o.gold,[0,-s*.5,t*.2+r])}const mT={radius:.2,depth:.08,bow:.06,colours:{gold:15251530,face:16183779,hands:2566454}};function gT(i){const e=Ur(i),{radius:t,depth:n,bow:s,colours:r}=mT,o=new cn(Math.PI/2,0,0);Ae(e,"case",new tt(t,t,n,24).applyMatrix4(new ge().makeRotationFromEuler(o)),r.gold,[0,0,0]),Ae(e,"face",new tt(t*.82,t*.82,n*.3,24).applyMatrix4(new ge().makeRotationFromEuler(o)),r.face,[0,-n*.45,0]),Ae(e,"hour_hand",new ut(t*.08,n*.2,t*.45),r.hands,[t*.1,-n*.62,t*.18]),Ae(e,"minute_hand",new ut(t*.6,n*.2,t*.06),r.hands,[t*.28,-n*.62,0]),Ae(e,"bow",new jn(s,s*.3,8,16).applyMatrix4(new ge().makeRotationFromEuler(o)),r.gold,[0,0,t+s*.8])}const _T={thick:.14,front:-.12,back:.4,cord:.035,knot:.08,colours:{wood:9067051,rope:13215082}};function xT(i){const e=Ur(i),[t,n,s,r]=["seat","ties","rope","under"].map(f=>ie.rope_swing[f]*Gt),{thick:o,front:a,back:c,cord:l,knot:h,colours:u}=_T,d=(a+c)/2;Ae(e,"seat",new ut(t,c-a,o),u.wood,[0,d,-r-o/2]);for(const[f,m]of Object.entries(N)){const _=new tt(l,l,s+r,8).rotateX(Math.PI/2);Ae(e,`rope_${f}`,_,u.rope,[m*n/2,d,(s-r)/2]),Ae(e,`knot_${f}`,new Qa(h,1),u.rope,[m*n/2,d,s])}}const Js={long:15,tilt:22,colours:{body:8016434,head:4861724,leg:2829880,shine:12094044}};function vT(i,e){const t=Js.long*i,n=new Ut;n.name="bug",Ae(n,"body",new En(t*.38,18,12),Js.colours.body,[t*.1,0,t*.3]).scale.set(1.3,.85,.75),Ae(n,"head",new En(t*.2,14,10),Js.colours.head,[-t*.42,0,t*.3]);for(const[o,a]of[-.18,.1,.38].entries())for(const c of[-1,1]){const l=Math.sin(Math.PI*(e+o/3+(c>0?.5:0))*2)*.12,h=Ae(n,`leg_${o}_${c}`,new tt(t*.035,t*.035,t*.42,6),Js.colours.leg,[t*(a+l),c*t*.28,t*.14]);h.rotation.x=c*.9}for(const o of[-1,1])Ae(n,`feeler_${o}`,new tt(t*.02,t*.02,t*.36,5),Js.colours.leg,[-t*.64,o*t*.08,t*.48]).rotation.set(o*.4,0,.9);n.rotation.x=Xe(Js.tilt),n.position.y=Fn;const r=new ja;return r.add(n),r.updateMatrixWorld(!0),{scene:r,foot:new v(0,Fn,0),bounds:new an().setFromObject(n)}}function yT(i){const{barrel:e,length:t,apart:n,rim:s,eyepiece:r,bridge:o,colours:a}=lT,c=l=>(l.rotation.x=Math.PI/2,l);for(const[l,h]of[-1,1].entries()){const u=h*n/2;c(Ae(i,`barrel_${l}`,new tt(e,e*.9,t,20),a.body,[u,0,t/2])),Ae(i,`rim_${l}`,new jn(e,s,10,28),a.rim,[u,0,t]),c(Ae(i,`eyepiece_${l}`,new tt(r[0],r[0],r[1],16),a.eyepiece,[u,0,-r[1]/2]));const d=new jt(new Oi(e*.85,24),new _n({color:a.lens,side:Pn}));d.name=`${i.name}_lens_${l}`,d.position.set(u,0,t+.004),d.frustumCulled=!1,i.add(d)}Ae(i,"bridge",new ut(...o),a.body,[0,0,t*.45])}const lm={roller:.045,length:1.25,knob:.075,wound:.11,unwound:.06,turns:1.5,width:1,bow:.06,curl:.08,rows:10,columns:16,rolled:.22,colours:{wood:9067051,knob:7029280,back:14469020,wound:15128238}};function MT(i){const{roller:e,length:t,knob:n,wound:s,unwound:r,turns:o,width:a,bow:c,curl:l,rows:h,columns:u,colours:d}=lm,f=["top","bottom"].map(p=>{const y=new Ut;y.name=`${i.name}_${p}`,i.add(y);const M=Ae(y,"roller",new tt(e,e,t,14),d.wood);M.rotation.z=Math.PI/2;for(const A of[-1,1])Ae(y,`knob_${A>0?"l":"r"}`,new En(n,14,10),d.knob,[A*t/2,0,0]);const x=Ae(y,"wound",new tt(1,1,a,18),d.wound);return x.rotation.z=Math.PI/2,{group:y,sleeve:x,rod:M}}),m=new fi(a,1,u,h),_=Ae(i,"parchment",m,d.back),g=p=>new v(p.x,p.z,-p.y);i.userData.shape=({top:p,bottom:y,open:M})=>{const[x,A]=[g(p),g(y)],E=nt(s,r,M);f.forEach(({group:R,sleeve:b,rod:w},L)=>{R.position.copy(L?A:x),b.scale.set(E,1,E),w.rotation.x=(L?-1:1)*o*2*Math.PI*M}),_.visible=M>.02;const P=m.attributes.position;for(let R=0;R<=h;R++){const b=R/h,w=x.clone().lerp(A,b);for(let L=0;L<=u;L++){const B=L/u-.5,F=c*Math.sin(Math.PI*b)*M-l*(2*B)**4;P.setXYZ(R*(u+1)+L,w.x+B*a,w.y,w.z+E+F)}}P.needsUpdate=!0,m.computeVertexNormals(),m.setAttribute("hullNormal",m.attributes.normal.clone())}}const hr={at:[.95,-.25,4.05],globe:.36,neck:.15,base:[.15,.22],threads:3,filament:.14,wire:.014,halo:1.7,strength:1.4,falloff:.6,colours:{glass:14937587,glassLit:16769658,base:12041414,contact:3816775,filament:5988203,filamentLit:16774338,warm:[1,.82,.42]}};function wT(i){const{globe:e,neck:t,base:n,threads:s,filament:r,wire:o,halo:a,colours:c}=hr,l=new Ut;l.name=i.name,i.add(l);const h=[[0,e*1.95],[e*.55,e*1.85],[e*.92,e*1.45],[e,e],[e*.88,e*.55],[t*1.2,e*.18],[t,0]].map(([A,E])=>new re(A,E)).reverse(),u=Ae(l,"glass",new Ar(h,28),c.glass);u.material.uniforms.shade={value:dh.clone()};const[d,f]=n;Ae(l,"base",new tt(d,d*.92,f,20),c.base,[0,-f/2,0]);for(let A=0;A<s;A++)Ae(l,`thread_${A}`,new jn(d*1.02,f/(s*4),6,20),c.base,[0,-f*((A+.6)/s),0]).rotation.x=Math.PI/2;Ae(l,"contact",new En(d*.45,12,8),c.contact,[0,-f,0]);const m=new Ya([[-r,e*.6],[-r*.5,e*1.15],[0,e*.95],[r*.5,e*1.15],[r,e*.6]].map(([A,E])=>new v(A,E,0))),_=new Ut;l.add(_);const p=[new vr(m,24,o*1.4,6),...[-1,1].map(A=>new vr(new ep(new v(A*r,.02,0),new v(A*r,e*.6,0)),1,o,6))].map(A=>{const E=new jt(A,new _n({color:c.filament,depthTest:!1}));return E.renderOrder=2,E.frustumCulled=!1,_.add(E),E}),y=new jt(new Oi(e*a,32),new _n({color:new Ve(...c.warm),transparent:!0,depthWrite:!1}));y.position.set(0,e,-e*1.2),y.frustumCulled=!1,l.add(y);const M=new Ve(c.glass),x=new Ve(c.glassLit);i.userData.shape=({size:A,lit:E})=>{l.scale.setScalar(Math.max(A,.001));const P=M.clone().lerp(x,E);u.material.uniforms.colour.value.set(P.r,P.g,P.b),u.material.uniforms.shade.value.copy(dh).lerp(new v(1.25,1.25,1.25),E);for(const R of p)R.material.color.set(c.filament).lerp(new Ve(c.filamentLit),E);y.visible=E>0,y.material.opacity=.35*E}}const xt={at:[0,-.92],tip:10,base:{width:1.2,narrow:.18,depth:.85,height:.88,brow:[.08,.8],round:.16,dome:.06},dial:{plate:.42,face:.045,marks:.37,radius:.31,holes:10,hole:.05,ring:.22,first:60,spread:290,label:.11},cradle:{at:-.14,apart:.3,post:.055,height:.13},handset:{length:1.4,grip:.085,drop:.15,end:[.2,.15],rest:.06,grille:1.52},cord:.022,coils:14,coil:.05,poof:{puffs:11,puff:.24,from:.5,to:.95},colours:{body:11022893,face:15853263,wheel:2829880,hole:16052973,mark:2829880,label:16052973,grille:2829880,smoke:15131630}},pl=new v(xt.at[0],xt.at[1],0);function Ae(i,e,t,n,s=[0,0,0]){const r=new jt(t,new _n({color:n}));iu(t),r.material=nu(r);const o=new jt(t,rm(r));return o.frustumCulled=r.frustumCulled=!1,r.add(o),r.name=`${i.name}_${e}`,r.position.set(...s),i.add(r),r}function bT(){const{width:i,narrow:e,depth:t,height:n,brow:s,round:r,dome:o}=xt.base,a=new Ls;a.moveTo(-t/2+r*.5,0),a.lineTo(t/2-r*.5,0),a.quadraticCurveTo(t/2,0,t/2-r*.2,r*.5),a.lineTo(s[0]+r*.3,s[1]-r*.4),a.quadraticCurveTo(s[0]-r*.2,n,s[0]-r*1.6,n),a.lineTo(-t/2+r*1.8,n),a.quadraticCurveTo(-t/2+r*.1,n,-t/2+r*.1,n-r*1.6),a.lineTo(-t/2,r*.5),a.quadraticCurveTo(-t/2,0,-t/2+r*.5,0);const c=i-2*r,l=new bo(a,{depth:c,bevelEnabled:!0,bevelThickness:r,bevelSize:eu(),bevelSegments:6,curveSegments:12});l.rotateY(-Math.PI/2).translate(c/2,0,0);const h=l.attributes.position;for(let u=0;u<h.count;u++){const[d,f]=[h.getX(u),Math.max(h.getY(u),0)];h.setX(u,d*(1-e*f/n)),h.setY(u,h.getY(u)+o*(f/n)**2*Math.max(1-(d/(i/2))**2,0))}return l.computeVertexNormals(),l}function ST(i,e,t,n){const{base:s,dial:r,cradle:o,colours:a}=xt,c=new Ut;c.name=i.name,i.add(c),Ae(c,"base",bT(),a.body);const l=new Ut;l.name=i.name,l.matrixAutoUpdate=!1,l.matrix.copy($p()),c.add(l),Ae(l,"dial_plate",new tt(r.plate,r.plate,r.face,40),a.face,[0,r.face/2,0]);for(let R=0;R<r.holes;R++){const b=Xe(r.first+r.spread*R/(r.holes-1));Ae(l,`number_${R}`,new ut(.03,r.face*.6,.045),a.mark,[Math.cos(b)*r.marks,r.face,-Math.sin(b)*r.marks])}const h=new Ut;h.name=i.name,h.position.y=r.face,l.add(h),Ae(h,"dial_wheel",new tt(r.radius,r.radius,r.face*.6,36),a.wheel,[0,r.face*.3,0]);for(let R=0;R<r.holes;R++){const b=Xe(r.first+r.spread*R/(r.holes-1));Ae(h,`hole_${R}`,new tt(r.hole,r.hole,r.face*.7,12),a.hole,[Math.cos(b)*r.ring,r.face*.4,-Math.sin(b)*r.ring])}Ae(l,"dial_label",new tt(r.label,r.label,r.face*1.6,24),a.label,[0,r.face,0]);const u=Xe(r.first+r.spread+22);Ae(l,"dial_stop",new ut(.04,r.face*2.2,.1),a.label,[Math.cos(u)*(r.radius+.02),r.face*1.2,-Math.sin(u)*(r.radius+.02)]);for(const R of[1,-1]){const b=jp(o.apart)+o.height;Ae(c,`prong_${R}`,new tt(o.post,o.post*1.4,o.height+.04,12),a.body,[R*o.apart,b-o.height/2-.02,o.at]),Ae(c,`saddle_${R}`,new jn(xt.handset.grip*1.1,o.post*.45,8,14,Math.PI),a.body,[R*o.apart,b+xt.handset.grip*.4,o.at]).rotation.set(0,Math.PI/2,Math.PI)}const d=new Ut;d.name=e.name,e.add(d);const{length:f,grip:m,drop:_,end:g}=xt.handset,p=new Ya([[-f/2,-_],[-f/2+.24,.02],[0,.06],[f/2-.24,.02],[f/2,-_]].map(([R,b])=>new v(R,b,0)));Ae(d,"handle",new vr(p,32,m,12),a.body);for(const[R,b]of[["ear",1],["mouth",-1]]){const w=new Ut;w.name=e.name,w.position.set(b*f/2,-_,0),w.rotation.z=b*.22,d.add(w),Ae(w,`${R}_piece`,new En(g[0],24,16),a.body,[0,-g[1]*.45,0]).scale.set(1,g[1]/g[0],1),Ae(w,`${R}_grille`,new tt(g[0]*.62,g[0]*.62,.025,20),a.grille,[0,-g[1]*xt.handset.grille,0])}i.userData.shape=({squash:R,dial:b})=>{c.scale.set(1+R/2,1-R,1+R/2),h.rotation.y=Xe(b)};const y=Ae(t,"cord",pf(new v,new v(1,0,0)),a.body);t.userData.shape=({from:R,to:b})=>{y.geometry.dispose(),y.geometry=y.children[0].geometry=pf(R,b),iu(y.geometry)};const{puffs:M,puff:x,from:A,to:E}=xt.poof,P=Array.from({length:M},(R,b)=>Ae(n,`puff_${b}`,new Qa(x*(.75+.5*(b*7%5)/4),1),a.smoke));n.userData.shape=({puff:R})=>{P.forEach((b,w)=>{const L=2*Math.PI*w/M,B=A+(E-A)*Math.sqrt(R);b.position.set(Math.cos(L)*B,Math.sin(L*2)*B*.35,Math.sin(L)*B*.6),b.scale.setScalar(Math.max(Math.sin(Math.PI*R),.001))})}}function pf(i,e){const{cord:t,coils:n,coil:s}=xt,r=u=>new v(u.x,u.z,-u.y),[o,a]=[r(i),r(e)],c=o.clone().lerp(a,.5).add(new v(0,-.35*o.distanceTo(a),0)),l=new kh(o,c,a),h=Array.from({length:n*8+1},(u,d)=>{const f=d/(n*8),m=l.getPoint(f),_=l.getTangent(f),g=new v(0,1,0).cross(_).normalize(),p=_.clone().cross(g).normalize(),y=2*Math.PI*n*f;return m.addScaledVector(g,Math.cos(y)*s).addScaledVector(p,Math.sin(y)*s)});return new vr(new Ya(h),n*16,t,6)}const ET={monocle:{radius:.2,tube:.028,chain:.55,chainWidth:.012},flute:{base:.13,baseDepth:.025,stem:.022,stemLength:.35,rim:.12,bottom:.05,bowl:.4,fill:.27},shades:{lens:[.56,.34,.05],apart:.37,bridge:[.2,.05,.05],temple:[.04,.04,.7],shine:[.2,.035,.01]},flame:{outer:[.17,.55],inner:[.09,.32],sides:12,flickers:7},finger:{radius:.09,length:.22,splay:.6},popper:{mouth:.14,length:.45,sides:12},confetti:{count:18,size:.08,reach:1.5,fall:.9,spin:9},trophy:{base:[.38,.12,.38],stem:[.05,.08,.22],rim:.3,bottom:.12,cup:.38,handle:.12,handleTube:.03},sword:{grip:[.035,.26],guard:[.42,.06,.07],blade:[.09,1.3,.025],point:.15,pommel:.06},castle:{wall:[.6,.3,.25],crenel:[.1,.08,.25],tower:[.11,.5],roof:[.15,.24],gate:[.14,.18],pole:.24,flag:.14},colours:{hat:2697787,band:16052973,gold:15251530,glass:14542574,champagne:15848058,lens:1316380,flame:16742938,fire:16765503,hand:16116959,wood:8014374,stone:13222580,confetti:[6514417,15251530,15681391,448160,1149618]}};function TT(i,e){const{monocle:t,flute:n,shades:s,flame:r,finger:o,popper:a,confetti:c,trophy:l,sword:h,castle:u,colours:d}=ET,f=sn.colours.ink,m=sn.colours.silver,_=sn.colours.accent,g=i("top_hat");e(g,"crown",lp(),d.hat),e(g,"band",hp(),new Ve(...wn.satin).getHex());const p=i("monocle");e(p,"ring",new jn(t.radius,t.tube,8,24),d.gold),e(p,"lens",new Oi(t.radius,24),d.glass),e(p,"chain",new tt(t.chainWidth,t.chainWidth,t.chain,6),d.gold,[t.radius*.7,-t.radius*.7-t.chain/2,0]);const y=i("champagne_flute");e(y,"base",new tt(n.base,n.base,n.baseDepth,16),d.glass,[0,-n.stemLength/2,0]),e(y,"stem",new tt(n.stem,n.stem,n.stemLength,8),d.glass),e(y,"bowl",new tt(n.rim,n.bottom,n.bowl,16,1,!0),d.glass,[0,(n.stemLength+n.bowl)/2,0]),e(y,"wine",new tt(n.rim*.9,n.bottom*.9,n.fill,16),d.champagne,[0,n.stemLength/2+n.fill/2+.01,0]);const M=i("sunglasses");for(const $ of[1,-1])e(M,`lens_${$}`,new ut(...s.lens),d.lens,[$*s.apart,0,0]),e(M,`temple_${$}`,new ut(...s.temple),f,[$*(s.apart+s.lens[0]/2),s.lens[1]/4,-s.temple[2]/2]),e(M,`shine_${$}`,new ut(...s.shine),sn.colours.white,[$*s.apart-s.lens[0]/5,s.lens[1]/4,s.lens[2]/2]).rotation.z=.5;e(M,"bridge",new ut(...s.bridge),f,[0,s.lens[1]/4,0]);const x=i("flame"),A=e(x,"outer",new hi(r.outer[0],r.outer[1],r.sides),d.flame,[0,r.outer[1]/2,0]),E=e(x,"inner",new hi(r.inner[0],r.inner[1],r.sides),d.fire,[0,r.inner[1]/2,.03]);x.userData.shape=({phase:$,size:W})=>{const ce=1+.18*Math.sin(2*Math.PI*r.flickers*$)+.08*Math.sin(2*Math.PI*2.3*r.flickers*$);x.scale.set(W*(2-ce),W*ce,W*(2-ce)),A.rotation.z=E.rotation.z=.12*Math.sin(2*Math.PI*1.7*r.flickers*$)};const P=()=>new zh(o.radius,o.length,4,8);e(i("thumb"),"thumb",P(),d.hand,[0,o.length/2+o.radius,0]);const R=i("shaka");for(const $ of[1,-1])e(R,`finger_${$}`,P(),d.hand,[$*o.length*.6,o.length/2,0]).rotation.z=-$*o.splay;const b=i("party_popper");e(b,"cone",new hi(a.mouth,a.length,a.sides,1,!0),_,[0,a.length/2,0]).rotation.x=Math.PI,e(b,"rim",new jn(a.mouth,.02,6,a.sides),d.gold,[0,a.length,0]).rotation.x=Math.PI/2;const w=Array.from({length:c.count},($,W)=>{const ce=e(b,`confetti_${W}`,new fi(c.size,c.size),d.confetti[W%d.confetti.length]),ve=W*2.39996,Re=.25+.5*(W*7%c.count)/c.count;return ce.userData.way=new v(Math.sin(Re)*Math.cos(ve),Math.cos(Re),Math.sin(Re)*Math.sin(ve)),ce});b.userData.shape=({burst:$})=>{for(const[W,ce]of w.entries()){ce.visible=$>0&&$<1;const ve=c.reach*Math.sqrt($);ce.position.set(ce.userData.way.x*ve,a.length+ce.userData.way.y*ve-c.fall*$*$,ce.userData.way.z*ve),ce.rotation.set(c.spin*$+W,c.spin*$*.7,W)}};const L=i("trophy");e(L,"base",new ut(...l.base),d.wood,[0,-l.stem[2]-l.base[1]/2,0]),e(L,"stem",new tt(l.stem[0],l.stem[1],l.stem[2],12),d.gold,[0,-l.stem[2]/2,0]),e(L,"cup",new tt(l.rim,l.bottom,l.cup,16),d.gold,[0,l.cup/2,0]);for(const $ of[1,-1])e(L,`handle_${$}`,new jn(l.handle,l.handleTube,6,12),d.gold,[$*l.rim,l.cup*.6,0]);const B=i("sword");e(B,"grip",new tt(h.grip[0],h.grip[0],h.grip[1],8),d.wood),e(B,"pommel",new En(h.pommel,8,6),d.gold,[0,-h.grip[1]/2-h.pommel/2,0]),e(B,"guard",new ut(...h.guard),d.gold,[0,h.grip[1]/2+h.guard[1]/2,0]),e(B,"blade",new ut(...h.blade),m,[0,h.grip[1]/2+h.guard[1]+h.blade[1]/2,0]);const F=e(B,"point",new hi(h.blade[0]/Math.SQRT2,h.point,4),m,[0,h.grip[1]/2+h.guard[1]+h.blade[1]+h.point/2,0]);F.rotation.y=Math.PI/4,F.scale.z=h.blade[2]/h.blade[0];const G=i("castle");e(G,"wall",new ut(...u.wall),d.stone,[0,u.wall[1]/2,0]);for(const $ of[-1,0,1])e(G,`crenel_${$}`,new ut(...u.crenel),d.stone,[$*u.wall[0]/3,u.wall[1]+u.crenel[1]/2,0]);for(const $ of[1,-1])e(G,`tower_${$}`,new tt(u.tower[0],u.tower[0],u.tower[1],12),d.stone,[$*u.wall[0]/2,u.tower[1]/2,0]),e(G,`roof_${$}`,new hi(...u.roof,12),_,[$*u.wall[0]/2,u.tower[1]+u.roof[1]/2,0]);e(G,"gate",new fi(...u.gate),f,[0,u.gate[1]/2,u.wall[2]/2+.005]);const Z=u.tower[1]+u.roof[1];e(G,"pole",new tt(.01,.01,u.pole,4),f,[u.wall[0]/2,Z+u.pole/2,0]);const X=new Ls;X.moveTo(0,0),X.lineTo(u.flag,-u.flag/3),X.lineTo(0,-u.flag*2/3),X.closePath(),e(G,"flag",new ec(X),d.gold,[u.wall[0]/2,Z+u.pole,0])}function AT(i,{bone:e,frame:t,at:n,turn:s}){const r=n.clone().applyMatrix4(i.get(e));return Pr.clone().multiply(Ln(r)).multiply(new ge().extractRotation(i.get(t))).multiply(On(s.x||0,s.y||0,s.z||0)).multiply(ic)}function RT(i,e){const{bulbAt:t,bulbGlow:n}=i.bulbLight;n.value.set(...hr.colours.warm).multiplyScalar(hr.strength*e.bulbLit),e.bulbLit&&t.value.setFromMatrixPosition(i.propByName.get("light_bulb").matrix).add(new v(0,hr.globe,0))}function CT(i,e,t){var n,s;for(const[r,o]of i.propByName){const a=e.props.get(r);o.visible=!!a,a&&(o.matrix.copy(AT(t,a)),o.matrixWorldNeedsUpdate=!0,(s=(n=o.userData).shape)==null||s.call(n,a))}}function PT(){const i=(l,h,u,d,f)=>{const m=rs(new ut(u,d,f),h);return m.name=l,m.add(new wo(new Za(m.geometry),new Rs({color:vs.edge}))),m},e=new Ut;e.name="reading_book",e.matrixAutoUpdate=!1,e.visible=!1;const t=i("book_spine",vs.spine,Ue.spine,Ue.height,Ue.cover);e.add(t);const n={},s={},r={},o={};for(const[l,h]of Object.entries(N)){const u=new Ut;u.name=`book_hinge_${l}`,u.position.x=h*Ue.spine/2;const d=i(`book_cover_${l}`,vs.cover,Ue.width,Ue.height,Ue.cover);d.position.set(h*Ue.width/2,0,Ue.cover/2);const f=i(`book_pages_${l}`,vs.pages,Ue.width-Ue.inset,Ue.height-Ue.inset*2,Ue.pages);f.position.set(h*(Ue.width-Ue.inset)/2,0,-Ue.pages/2);for(let _=1;_<=Ue.lines;_++){const g=rs(new ut(Ue.width-Ue.inset,Ue.lineWidth,Ue.lineWidth),vs.rule);g.position.set(f.position.x,-Ue.height/2+Ue.inset,-Ue.pages*_/(Ue.lines+1)),u.add(g)}u.add(d,f),e.add(u),n[l]=u,s[l]=d,r[l]=f;const m=new kt;m.name=`book_grip_${l}`,e.add(m),o[l]=m}const a=rs(new fi(Ue.width-Ue.inset,Ue.height-Ue.inset*2,Ue.pageSegments,1),vs.paper);a.geometry.translate(-(Ue.width-Ue.inset)/2,0,0),a.name="book_turning_page";const c=new Kf(new Xt,new Rs({color:vs.rule}));return c.frustumCulled=!1,a.add(c),a.userData.edge=c,e.add(a),e.userData={hinges:n,covers:s,pages:r,grips:o,leaf:a},e}function LT(i,e){const t=i.l.clone(),n=i.r.clone(),s=t.clone().sub(n).normalize(),r=new v(0,1,0).addScaledVector(s,-s.y).normalize(),o=s.clone().cross(r).normalize(),a=new ge().makeBasis(s,r,o).multiply(cm(e)),c=t.distanceTo(n)/ts("l",e).distanceTo(ts("r",e)),l=ts("l",e).add(ts("r",e)).multiplyScalar(.5).applyMatrix4(a).multiplyScalar(c);return a.scale(new v(c,c,c)).setPosition(t.add(n).multiplyScalar(.5).sub(l))}function IT(i,e,t){const n=om(e);for(const[h,u]of Object.entries(N))i.userData.hinges[h].rotation.y=u*n,i.userData.grips[h].position.copy(ts(h,e));const s=i.userData.leaf,r=Ue.pages+Ue.leaf;s.position.set(nt(-Ue.spine/2+r*Math.sin(n),Ue.spine/2-r*Math.sin(n),t),0,-r*Math.cos(n)),s.rotation.y=-n-Xe(Ue.open*e)*t,s.visible=e>0;const o=Ue.curl*Math.sin(Math.PI*t),a=Ue.width-Ue.inset,c=s.geometry.attributes.position;for(let h=0;h<2;h++)for(let u=0;u<=Ue.pageSegments;u++){const d=1-u/Ue.pageSegments,f=h*(Ue.pageSegments+1)+u,m=Ue.pageBow*Math.sin(Math.PI*t)*d*d;c.setX(f,(o?-a*Math.sin(o*d)/o:-a*d)-Math.sin(s.rotation.y)*m),c.setZ(f,(o?a*(1-Math.cos(o*d))/o:0)+Math.cos(s.rotation.y)*m)}c.needsUpdate=!0;const l=[];for(let h=0;h<=Ue.pageSegments;h++)l.push(new v().fromBufferAttribute(c,h));for(let h=Ue.pageSegments;h>=0;h--)l.push(new v().fromBufferAttribute(c,Ue.pageSegments+1+h));s.userData.edge.geometry.setFromPoints(l)}const DT=1.95,NT=.3;function UT(i){const e=a=>new v().setFromMatrixPosition(i.get(a)),t=e("thigh_l").add(e("thigh_r")).multiplyScalar(.5),n=e("shin_l").add(e("shin_r")).multiplyScalar(.5),s=n.clone().sub(t).setY(0).normalize(),r=new v(0,1,0),o=t.lerp(n,DT).addScaledVector(r,NT);return new ge().makeBasis(r.clone().cross(s),r,s).setPosition(o)}function OT(i,e){return Object.fromEntries(Object.keys(N).map(t=>[t,i.grip(t,[0,0,0]).applyMatrix4(e.get(`hand_${t}`)).applyMatrix4(Pr)]))}function FT(i,e,t,n){const s=e.moves(t);if(!n)return{moves:s,settled:!0};const r=dw(i,n.from,s,n.k,n.previous);if(!n.plant)return r;const o=c=>Math.min(...Object.keys(N).map(l=>e.head(`foot_${l}`,c.get(`foot_${l}`)).z)),a=new ge().makeTranslation(0,0,o(s)-o(r.moves));return{moves:new Map([...r.moves].map(([c,l])=>[c,a.clone().multiply(l)])),settled:r.settled}}function BT(i,e,t,n){var u;const s=FT(i.rig,e,t,n);n&&(n.settled=s.settled);const r=s.moves,o=new Map;for(const d of i.rig.bones){const f=Pr.clone().multiply(r.get(d.name)).multiply(ic).multiply(i.rig.rest.get(d.name));o.set(d.name,f),(d.parent.isBone?o.get(d.parent.name):d.parent.matrixWorld).clone().invert().multiply(f).decompose(d.position,d.quaternion,d.scale)}i.laptop.visible=e.laptop,i.book.visible=!!((u=e.book)!=null&&u.visible),i.book.visible&&(IT(i.book,e.book.open,e.book.page),i.book.matrix.copy(LT(OT(e,r),e.book.open)),i.book.matrixWorldNeedsUpdate=!0);for(const d of i.tablet)d.visible=e.tablet;const a=e.laptop||e.book||e.props.size>0;for(const d of i.stowable)d.visible=!e.stowed.has(d.userData.item);for(const d of i.inHand)d.visible=!e.stowed.has(d.userData.item)&&(!a||e.keep.has(d.userData.item));CT(i,e,r),RT(i,e),e.laptop&&(i.laptop.matrix.copy(UT(o)),i.laptop.matrixWorldNeedsUpdate=!0);const c=e.screen??$T,l=e.eyeShape&&{...e.eyeShape,colour:XT(e.screen)},h=Tm({eyed:c.eyes>qT,eyes:e.eyes,glance:e.eyeGlance,tint:e.eyeTint,hearts:e.hearts,stars:e.stars,squeezed:e.squeezed,dozing:e.dozing,whoa:e.whoa,sign:l,ticker:e.ticker});for(const d of i.screens)d.uniforms.lit.value=c.glow,d.uniforms.across.value=c.across,d.uniforms.open.value=c.open,d.uniforms.flash.value=c.flash,e.screen&&d.uniforms.glow.value.set(...e.screen.colour),VE(d,h,Math.floor(performance.now()*(e.ticker?Am.fps:Rm)/1e3));for(const d of i.visorHulls)d.visible=!e.screen||!!e.screen.sign;return r}function hm(i,e,t=1/0){if(i==="walk")return 0;if(!wm.has(i))return Math.min(Math.max(e,-t),t);const n=Math.max(...Lm.turns);return Math.min(Math.max(e,-n),n)}const mf=.8,gf={into:.35,out:.45},um=({seconds:i,lasts:e})=>ne(i,[0,gf.into])*(1-ne(i,[e-gf.out,e]));function kT(i){const e=i%mf/mf;return 1+.28*He(e,0,.3)+.14*He(e,.3,.55)}function zT(i){Ze(i,"startled"),i.whoa=!0}function HT(i,{mood:e,seconds:t,lasts:n}){const s=um({seconds:t,lasts:n});Sp[e].hearts?i.heartEyes(s*kT(t)):Ze(i,e,s)}const ml={share:.8,lean:.12,most:20},GT=.55,VT=(i,e)=>i==="sit"&&!e?GT:0;function gl(i,e){const t=new v(0,-1,0).transformDirection(i.matrix(e));return yt.radToDeg(Math.atan2(t.x,-t.y))}function WT(i,e,t){const n=Ci(e),s=()=>Ci(e+gl(i,"head")),r=ml.most,o=nt(s(),yt.clamp((1-ml.share)*n,-r,r),t);i.bendAbove("chest",{z:-ml.lean*n*t}),i.turn("neck",{z:-.3*Ci(s()-o)});const a=Ci(gl(i,"head")-gl(i,"chest")),c=a-yt.clamp(a-Ci(s()-o),-ka,ka);return i.turn("head",{z:-c}),hm(i.posture,-Ci(s()-o))}const XT=i=>{const e=i==null?void 0:i.sign;return e?i.colour.map(t=>(t+(1-t)*e.white)*e.lit):[1,1,1]},_a="face_screen",qT=.05,$T={eyes:1,across:0,open:0,flash:0,glow:0};function jT(i,e,t,n,s,{posture:r="stand",eyes:o=null,stride:a=0,sky:c=null,throws:l=null,leanWay:h=0,walkWay:u=0,at:d=null,target:f=null,open:m=1,screen:_=null,tilt:g=0,ticker:p=null,grabbed:y=!1,phoneWay:M=1}={}){var B,F;const x=new vb(i,r,a);Object.assign(x,{phoneWay:M,ticker:p,sky:c,throws:l,leanWay:h,walkWay:u,screen:_,at:d,target:f,facing:s}),t.legs||(B=lf[r])==null||B.under(x),t.pose(x,e,n/t.frames);const A=1-x.headContact;g&&A&&oe(x,{tilt:g*A}),t.legs||(F=lf[r])==null||F.over(x);const E=_l(r)&&t.head!==se.alone?Math.max(o?um(o):0,_?bm(_):0,y?1:0,x.eyesShown())*A:0,P=d&&A?{...d,amount:(d.amount??1)*(1-E)*A}:null,R=s+(P&&_l(r)?hm(r,n1(x,P,s),P.most):0);m<1&&x.shutEyes(Math.min(x.eyes,m)),_&&x.shutEyes(Math.min(x.eyes,_.eyes));const b=_l(r)&&!Sm(t)?VT(r,d)*A:0,w=x.gaze?E:Math.max(E,b),L=w?WT(x,R,w):0;return o&&HT(x,o),d!=null&&d.mood&&Ze(x,d.mood,d.amount),y&&zT(x),_!=null&&_.sign&&x.shapeEyes(_.sign.name,_.sign.strength),{pose:x,turned:R+L}}const _l=i=>i!=="lounge";class oA{constructor(){const e=Gt/2;this.camera=new qa(-e,e,e,-e,el-Wd,el+Wd),this.camera.position.set(0,Fn,el),this.camera.lookAt(0,Fn,0),this.renderer=new pd({antialias:!0,alpha:!0,preserveDrawingBuffer:!0}),this.renderer.setPixelRatio(1),this.renderer.setClearColor(0,0),this.screenRenderer=new pd({antialias:!0,alpha:!0,preserveDrawingBuffer:!0}),this.screenRenderer.setPixelRatio(1),this.screenRenderer.setClearColor(0,0)}headAt(e,t){if(!t)return{x:.5,y:.3};const n=e.rig.eyes.reduce((s,r)=>s.add(r),new v).divideScalar(e.rig.eyes.length);return this.pictured(n.applyMatrix4(t.get("head")))}handAt(e,t){const n=Ke(e.stance),s=n==="l"?"r":"l";return t?{...this.gripAt(e,t,n),out:N[n],other:this.gripAt(e,t,s)}:{x:.5+N[n]*.25,y:.6,out:N[n],other:{x:.5-N[n]*.25,y:.6}}}gripAt(e,t,n){const s=new v(N[n]*hn.grip,hn.forward,0).add(e.rig.heads.get(`hand_${n}`));return this.pictured(s.applyMatrix4(t.get(`hand_${n}`)))}pictured(e){const t=e.applyMatrix4(Pr).project(this.camera);return{x:(t.x+1)/2,y:(1-t.y)/2}}draw(e,t,n,s,r,{blend:o=null,...a}={}){const{pose:c,turned:l}=jT(e.rig,e.stance,t,n,s,a),h=BT(e,c,l,o);return this.drawBody(e,r),this.drawScreen(e,r),h}drawBody(e,t){const n=t.width*tb;this.renderer.domElement.width!==n&&this.renderer.setSize(n,n,!1);for(const r of e.screens)r.visible=!1;this.renderer.render(e.scene,this.camera);for(const r of e.screens)r.visible=!0;const s=t.getContext("2d");s.clearRect(0,0,t.width,t.height),s.imageSmoothingEnabled=!0,s.imageSmoothingQuality="high",s.filter=`blur(${sb(t)}px)`,s.drawImage(this.renderer.domElement,0,0,t.width,t.height),s.filter="none"}drawScreen(e,t){const n=t.width*Ti;this.screenRenderer.domElement.width!==n&&this.screenRenderer.setSize(n,n,!1);const s=new Set;e.scene.traverse(o=>{for(const a of[o.material??[]].flat())a.colorWrite&&!e.screens.includes(a)&&s.add(a)});for(const o of s)o.colorWrite=!1;const r=e.visorHulls.map(o=>o.visible);for(const o of e.visorHulls)o.visible=!1;this.screenRenderer.render(e.scene,this.camera),e.visorHulls.forEach((o,a)=>o.visible=r[a]);for(const o of s)o.colorWrite=!0;this.screenCanvas??(this.screenCanvas=document.createElement("canvas")),this.screenCanvas.width=t.width,this.screenCanvas.height=t.height,this.halvedOnto(this.screenRenderer.domElement,0,0,n,n,this.screenCanvas),t.getContext("2d").drawImage(this.screenCanvas,0,0)}halvedOnto(e,t,n,s,r,o){this.half??(this.half=document.createElement("canvas")),this.half.width=o.width*2,this.half.height=o.height*2,df(this.half,e,t,n,s,r),df(o,this.half,0,0,this.half.width,this.half.height)}drawBlock(e,t,n,s){this.blockFor!==n&&(this.block=eT(Gt/n)),this.blockFor=n,tT(this.block,e,t);const r=this.propPicture(this.block,new v(0,0,0),n,s);return{canvas:r.canvas,below:r.height-r.at.y}}drawSaucer(e,t,n){this.saucerFor!==t&&(this.saucer=nT(Gt/t)),this.saucerFor=t,iT(this.saucer,e);const s=this.propPicture(this.saucer,this.saucer.middle,t,n);return{canvas:s.canvas,at:s.at}}drawBug(e,t,n){const s=vT(Gt/t,e),r=this.propPicture(s,s.foot,t,n);return{canvas:r.canvas,at:r.at}}drawCanopy(e,t){const n=sT(Gt/e,e),s=this.propPicture(n,n.middle,e,t),r=n.middle.clone().project(this.camera),o=c=>(c+1)/2*e,a=n.ends.map(c=>{const l=c.clone().project(this.camera);return{x:s.at.x+o(l.x)-o(r.x),y:s.at.y-o(l.y)+o(r.y)}});return{canvas:s.canvas,at:s.at,ends:a}}propPicture({scene:e,bounds:t},n,s,r){const o=Math.round(s*r)*Ti;this.renderer.domElement.width!==o&&this.renderer.setSize(o,o,!1),this.renderer.render(e,this.camera);const{min:a,max:c}=t,l=[a.x,c.x].flatMap(y=>[a.y,c.y].flatMap(M=>[a.z,c.z].map(x=>new v(y,M,x).project(this.camera)))),h=y=>(y+1)/2*o,u=Math.floor(Math.min(...l.map(y=>h(y.x))))-Ti,d=Math.ceil(Math.max(...l.map(y=>h(y.x))))+Ti,f=Math.floor(Math.min(...l.map(y=>o-h(y.y))))-Ti,m=Math.ceil(Math.max(...l.map(y=>o-h(y.y))))+Ti,_=document.createElement("canvas");_.width=Math.round((d-u)/Ti),_.height=Math.round((m-f)/Ti),this.halvedOnto(this.renderer.domElement,u,f,d-u,m-f,_);const g=n.clone().project(this.camera),p=y=>y/Ti/r;return{canvas:_,height:p(m-f),at:{x:p(h(g.x)-u),y:p(o-h(g.y)-f)}}}}export{br as ACTED,z as ACTING,no as BIG_MALLET,lT as BINOCULARS,ga as BINOCULAR_HOLD,Ue as BOOK,Js as BUG,$t as CALL,Rn as CANOPY,Qw as CELL,TE as CHUTE_GRIP,sA as CLIPS,Kt as COMPOSED,fT as CRUCIFIX,dl as CRUCIFIX_HOLD,of as DOZE,$i as EAGERNESS,Sp as EYES,Yd as FIGHT_EYES,li as GLANCE,yo as GLASS,xs as GLASS_BUBBLE,QT as GROUND,lo as HALO_RING,hn as HAND,sf as HEAD_TIP,ka as HEAD_TURN,OE as HIDDEN_PARTS,Jt as INSPECTING,ol as LADDER_CLIMB,_h as LANDING,pa as LEDGE,db as LEFT_OUT,lf as LEGS,hr as LIGHT_BULB,za as LOOK_DEPTH,gf as LOOK_EASE,tA as LOOK_REACH,qn as LOUNGE,co as MALLET_SWING,mT as POCKET_WATCH,gn as PONDERING,vb as Posing,pe as REACTING,ET as REACTION_PROPS,Pi as REMORSE,lm as REPORT_SCROLL,Bt as REST,mn as RIFLE,sr as RIFLE_HOLD,ir as RIFLE_PARTS,Ks as RUB,ai as RUMMAGE,aT as RUMMAGE_THINGS,Vt as SAUCER,ji as SCREEN,fl as SCREEN_INSET,ii as SCROLL,fa as SEARCHING,GT as SEATED_TOWARD,Db as SEAT_SPREAD,bn as SHOVE,N as SIDES,Ki as SKY,_T as SWING,Aa as SWING_HOLD,oA as Stage,xt as TELEPHONE,sn as TOOLS,ml as TOWARD_VIEWER,Gn as TUMBLE,uf as TYPING_SECONDS,pn as WAIT,Yr as WATCH_CHECK,gt as WORK,Np as WRITING,uT as bigMalletOf,yT as binocularsOf,FT as blendedMoves,eA as blowsLandAt,hm as bodyTurnFor,QS as boxSeen,vT as bugOf,af as burstKick,sT as canopyOf,pT as crucifixOf,Yp as dialHole,jT as drawnPose,iA as eyesAboveOf,ZE as figureOf,ff as frontOf,rT as glassOf,e1 as glassSeen,dT as haloOf,nA as headPivotOf,kT as heartBeat,r1 as leanOf,tf as lensBefore,wT as lightBulbOf,RT as lightFromBulb,iT as lightSaucer,rA as loadFigure,um as lookStrength,n1 as lookToward,PS as lookedPoint,mE as malletAt,CT as moveProps,Sr as onPhoneAt,H1 as phoneArrival,WE as pixelTexture,gT as pocketWatchOf,oT as propsOf,yb as reachSide,MT as reportScrollOf,aE as rifleAim,xh as rifleLine,hT as rifleOf,xT as ropeSwingOf,nT as saucerOf,VE as screenFrame,BE as screenMaterial,VT as seatedTurn,GE as setScreenIn,XE as showPixels,XT as signColour,Fb as supportsClip,ST as telephoneOf,WT as turnToViewer,_l as turnsToViewer};

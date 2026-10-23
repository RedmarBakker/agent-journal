import{A as _e,p as Ge,h as fl,s as _d,g as xd,a as vd,P as Hi,L as yd,b as Md,V as Sd}from"./main-BdSpylUv.js";import"./tokens-D2Th-Z3L.js";import"./tip-CN_oYXIT.js";import"./preload-helper-Dp1pzeXC.js";/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const dl="170",Ed=0,$l=1,bd=2,Gh=1,wd=2,ni=3,ui=0,sn=1,mn=2,Ii=0,Ls=1,Kl=2,Zl=3,Jl=4,Td=5,Ji=100,Ad=101,Rd=102,Cd=103,Pd=104,Ld=200,Id=201,Dd=202,Nd=203,pc=204,mc=205,Ud=206,Od=207,Fd=208,Bd=209,kd=210,zd=211,Hd=212,Vd=213,Gd=214,gc=0,_c=1,xc=2,Fs=3,vc=4,yc=5,Mc=6,Sc=7,Wh=0,Wd=1,Xd=2,Di=0,qd=1,Yd=2,jd=3,$d=4,Kd=5,Zd=6,Jd=7,Ql="attached",Qd="detached",Xh=300,Bs=301,ks=302,Ec=303,bc=304,jo=306,zs=1e3,Ai=1001,Fo=1002,rn=1003,qh=1004,xr=1005,gn=1006,Ao=1007,oi=1008,hi=1009,Yh=1010,jh=1011,Tr=1012,pl=1013,es=1014,Dn=1015,Dr=1016,ml=1017,gl=1018,Hs=1020,$h=35902,Kh=1021,Zh=1022,bn=1023,Jh=1024,Qh=1025,Is=1026,Vs=1027,_l=1028,xl=1029,ef=1030,vl=1031,yl=1033,Ro=33776,Co=33777,Po=33778,Lo=33779,wc=35840,Tc=35841,Ac=35842,Rc=35843,Cc=36196,Pc=37492,Lc=37496,Ic=37808,Dc=37809,Nc=37810,Uc=37811,Oc=37812,Fc=37813,Bc=37814,kc=37815,zc=37816,Hc=37817,Vc=37818,Gc=37819,Wc=37820,Xc=37821,Io=36492,qc=36494,Yc=36495,tf=36283,jc=36284,$c=36285,Kc=36286,Ar=2300,Rr=2301,ha=2302,eu=2400,tu=2401,nu=2402,ep=2500,tp=0,nf=1,Zc=2,np=3200,ip=3201,sf=0,sp=1,wi="",Nt="srgb",en="srgb-linear",$o="linear",yt="srgb",us=7680,iu=519,rp=512,op=513,ap=514,rf=515,cp=516,lp=517,up=518,hp=519,Jc=35044,su="300 es",ai=2e3,Bo=2001;class $s{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const s=this._listeners[e];if(s!==void 0){const r=s.indexOf(t);r!==-1&&s.splice(r,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const s=n.slice(0);for(let r=0,o=s.length;r<o;r++)s[r].call(this,e);e.target=null}}}const Zt=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"];let ru=1234567;const Ds=Math.PI/180,Gs=180/Math.PI;function wn(){const i=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(Zt[i&255]+Zt[i>>8&255]+Zt[i>>16&255]+Zt[i>>24&255]+"-"+Zt[e&255]+Zt[e>>8&255]+"-"+Zt[e>>16&15|64]+Zt[e>>24&255]+"-"+Zt[t&63|128]+Zt[t>>8&255]+"-"+Zt[t>>16&255]+Zt[t>>24&255]+Zt[n&255]+Zt[n>>8&255]+Zt[n>>16&255]+Zt[n>>24&255]).toLowerCase()}function Bt(i,e,t){return Math.max(e,Math.min(t,i))}function Ml(i,e){return(i%e+e)%e}function fp(i,e,t,n,s){return n+(i-e)*(s-n)/(t-e)}function dp(i,e,t){return i!==e?(t-i)/(e-i):0}function Mr(i,e,t){return(1-t)*i+t*e}function pp(i,e,t,n){return Mr(i,e,1-Math.exp(-t*n))}function mp(i,e=1){return e-Math.abs(Ml(i,e*2)-e)}function gp(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*(3-2*i))}function _p(i,e,t){return i<=e?0:i>=t?1:(i=(i-e)/(t-e),i*i*i*(i*(i*6-15)+10))}function xp(i,e){return i+Math.floor(Math.random()*(e-i+1))}function vp(i,e){return i+Math.random()*(e-i)}function yp(i){return i*(.5-Math.random())}function Mp(i){i!==void 0&&(ru=i);let e=ru+=1831565813;return e=Math.imul(e^e>>>15,e|1),e^=e+Math.imul(e^e>>>7,e|61),((e^e>>>14)>>>0)/4294967296}function Sp(i){return i*Ds}function Ep(i){return i*Gs}function bp(i){return(i&i-1)===0&&i!==0}function wp(i){return Math.pow(2,Math.ceil(Math.log(i)/Math.LN2))}function Tp(i){return Math.pow(2,Math.floor(Math.log(i)/Math.LN2))}function Ap(i,e,t,n,s){const r=Math.cos,o=Math.sin,a=r(t/2),c=o(t/2),l=r((e+n)/2),u=o((e+n)/2),f=r((e-n)/2),h=o((e-n)/2),d=r((n-e)/2),m=o((n-e)/2);switch(s){case"XYX":i.set(a*u,c*f,c*h,a*l);break;case"YZY":i.set(c*h,a*u,c*f,a*l);break;case"ZXZ":i.set(c*f,c*h,a*u,a*l);break;case"XZX":i.set(a*u,c*m,c*d,a*l);break;case"YXY":i.set(c*d,a*u,c*m,a*l);break;case"ZYZ":i.set(c*m,c*d,a*u,a*l);break;default:console.warn("THREE.MathUtils: .setQuaternionFromProperEuler() encountered an unknown order: "+s)}}function In(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return i/4294967295;case Uint16Array:return i/65535;case Uint8Array:return i/255;case Int32Array:return Math.max(i/2147483647,-1);case Int16Array:return Math.max(i/32767,-1);case Int8Array:return Math.max(i/127,-1);default:throw new Error("Invalid component type.")}}function _t(i,e){switch(e.constructor){case Float32Array:return i;case Uint32Array:return Math.round(i*4294967295);case Uint16Array:return Math.round(i*65535);case Uint8Array:return Math.round(i*255);case Int32Array:return Math.round(i*2147483647);case Int16Array:return Math.round(i*32767);case Int8Array:return Math.round(i*127);default:throw new Error("Invalid component type.")}}const ci={DEG2RAD:Ds,RAD2DEG:Gs,generateUUID:wn,clamp:Bt,euclideanModulo:Ml,mapLinear:fp,inverseLerp:dp,lerp:Mr,damp:pp,pingpong:mp,smoothstep:gp,smootherstep:_p,randInt:xp,randFloat:vp,randFloatSpread:yp,seededRandom:Mp,degToRad:Sp,radToDeg:Ep,isPowerOfTwo:bp,ceilPowerOfTwo:wp,floorPowerOfTwo:Tp,setQuaternionFromProperEuler:Ap,normalize:_t,denormalize:In};class ie{constructor(e=0,t=0){ie.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6],this.y=s[1]*t+s[4]*n+s[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Bt(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),s=Math.sin(t),r=this.x-e.x,o=this.y-e.y;return this.x=r*n-o*s+e.x,this.y=r*s+o*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class et{constructor(e,t,n,s,r,o,a,c,l){et.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,o,a,c,l)}set(e,t,n,s,r,o,a,c,l){const u=this.elements;return u[0]=e,u[1]=s,u[2]=a,u[3]=t,u[4]=r,u[5]=c,u[6]=n,u[7]=o,u[8]=l,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,o=n[0],a=n[3],c=n[6],l=n[1],u=n[4],f=n[7],h=n[2],d=n[5],m=n[8],_=s[0],g=s[3],p=s[6],M=s[1],v=s[4],x=s[7],L=s[2],T=s[5],R=s[8];return r[0]=o*_+a*M+c*L,r[3]=o*g+a*v+c*T,r[6]=o*p+a*x+c*R,r[1]=l*_+u*M+f*L,r[4]=l*g+u*v+f*T,r[7]=l*p+u*x+f*R,r[2]=h*_+d*M+m*L,r[5]=h*g+d*v+m*T,r[8]=h*p+d*x+m*R,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],c=e[6],l=e[7],u=e[8];return t*o*u-t*a*l-n*r*u+n*a*c+s*r*l-s*o*c}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],c=e[6],l=e[7],u=e[8],f=u*o-a*l,h=a*c-u*r,d=l*r-o*c,m=t*f+n*h+s*d;if(m===0)return this.set(0,0,0,0,0,0,0,0,0);const _=1/m;return e[0]=f*_,e[1]=(s*l-u*n)*_,e[2]=(a*n-s*o)*_,e[3]=h*_,e[4]=(u*t-s*c)*_,e[5]=(s*r-a*t)*_,e[6]=d*_,e[7]=(n*c-l*t)*_,e[8]=(o*t-n*r)*_,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,s,r,o,a){const c=Math.cos(r),l=Math.sin(r);return this.set(n*c,n*l,-n*(c*o+l*a)+o+e,-s*l,s*c,-s*(-l*o+c*a)+a+t,0,0,1),this}scale(e,t){return this.premultiply(fa.makeScale(e,t)),this}rotate(e){return this.premultiply(fa.makeRotation(-e)),this}translate(e,t){return this.premultiply(fa.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<9;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const fa=new et;function of(i){for(let e=i.length-1;e>=0;--e)if(i[e]>=65535)return!0;return!1}function Cr(i){return document.createElementNS("http://www.w3.org/1999/xhtml",i)}function Rp(){const i=Cr("canvas");return i.style.display="block",i}const ou={};function vr(i){i in ou||(ou[i]=!0,console.warn(i))}function Cp(i,e,t){return new Promise(function(n,s){function r(){switch(i.clientWaitSync(e,i.SYNC_FLUSH_COMMANDS_BIT,0)){case i.WAIT_FAILED:s();break;case i.TIMEOUT_EXPIRED:setTimeout(r,t);break;default:n()}}setTimeout(r,t)})}function Pp(i){const e=i.elements;e[2]=.5*e[2]+.5*e[3],e[6]=.5*e[6]+.5*e[7],e[10]=.5*e[10]+.5*e[11],e[14]=.5*e[14]+.5*e[15]}function Lp(i){const e=i.elements;e[11]===-1?(e[10]=-e[10]-1,e[14]=-e[14]):(e[10]=-e[10],e[14]=-e[14]+1)}const ot={enabled:!0,workingColorSpace:en,spaces:{},convert:function(i,e,t){return this.enabled===!1||e===t||!e||!t||(this.spaces[e].transfer===yt&&(i.r=li(i.r),i.g=li(i.g),i.b=li(i.b)),this.spaces[e].primaries!==this.spaces[t].primaries&&(i.applyMatrix3(this.spaces[e].toXYZ),i.applyMatrix3(this.spaces[t].fromXYZ)),this.spaces[t].transfer===yt&&(i.r=Ns(i.r),i.g=Ns(i.g),i.b=Ns(i.b))),i},fromWorkingColorSpace:function(i,e){return this.convert(i,this.workingColorSpace,e)},toWorkingColorSpace:function(i,e){return this.convert(i,e,this.workingColorSpace)},getPrimaries:function(i){return this.spaces[i].primaries},getTransfer:function(i){return i===wi?$o:this.spaces[i].transfer},getLuminanceCoefficients:function(i,e=this.workingColorSpace){return i.fromArray(this.spaces[e].luminanceCoefficients)},define:function(i){Object.assign(this.spaces,i)},_getMatrix:function(i,e,t){return i.copy(this.spaces[e].toXYZ).multiply(this.spaces[t].fromXYZ)},_getDrawingBufferColorSpace:function(i){return this.spaces[i].outputColorSpaceConfig.drawingBufferColorSpace},_getUnpackColorSpace:function(i=this.workingColorSpace){return this.spaces[i].workingColorSpaceConfig.unpackColorSpace}};function li(i){return i<.04045?i*.0773993808:Math.pow(i*.9478672986+.0521327014,2.4)}function Ns(i){return i<.0031308?i*12.92:1.055*Math.pow(i,.41666)-.055}const au=[.64,.33,.3,.6,.15,.06],cu=[.2126,.7152,.0722],lu=[.3127,.329],uu=new et().set(.4123908,.3575843,.1804808,.212639,.7151687,.0721923,.0193308,.1191948,.9505322),hu=new et().set(3.2409699,-1.5373832,-.4986108,-.9692436,1.8759675,.0415551,.0556301,-.203977,1.0569715);ot.define({[en]:{primaries:au,whitePoint:lu,transfer:$o,toXYZ:uu,fromXYZ:hu,luminanceCoefficients:cu,workingColorSpaceConfig:{unpackColorSpace:Nt},outputColorSpaceConfig:{drawingBufferColorSpace:Nt}},[Nt]:{primaries:au,whitePoint:lu,transfer:yt,toXYZ:uu,fromXYZ:hu,luminanceCoefficients:cu,outputColorSpaceConfig:{drawingBufferColorSpace:Nt}}});let hs;class Ip{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{hs===void 0&&(hs=Cr("canvas")),hs.width=e.width,hs.height=e.height;const n=hs.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=hs}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=Cr("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const s=n.getImageData(0,0,e.width,e.height),r=s.data;for(let o=0;o<r.length;o++)r[o]=li(r[o]/255)*255;return n.putImageData(s,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(li(t[n]/255)*255):t[n]=li(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let Dp=0;class af{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:Dp++}),this.uuid=wn(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},s=this.data;if(s!==null){let r;if(Array.isArray(s)){r=[];for(let o=0,a=s.length;o<a;o++)s[o].isDataTexture?r.push(da(s[o].image)):r.push(da(s[o]))}else r=da(s);n.url=r}return t||(e.images[this.uuid]=n),n}}function da(i){return typeof HTMLImageElement<"u"&&i instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&i instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&i instanceof ImageBitmap?Ip.getDataURL(i):i.data?{data:Array.from(i.data),width:i.width,height:i.height,type:i.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let Np=0;class Wt extends $s{constructor(e=Wt.DEFAULT_IMAGE,t=Wt.DEFAULT_MAPPING,n=Ai,s=Ai,r=gn,o=oi,a=bn,c=hi,l=Wt.DEFAULT_ANISOTROPY,u=wi){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:Np++}),this.uuid=wn(),this.name="",this.source=new af(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=s,this.magFilter=r,this.minFilter=o,this.anisotropy=l,this.format=a,this.internalFormat=null,this.type=c,this.offset=new ie(0,0),this.repeat=new ie(1,1),this.center=new ie(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new et,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=u,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==Xh)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case zs:e.x=e.x-Math.floor(e.x);break;case Ai:e.x=e.x<0?0:1;break;case Fo:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case zs:e.y=e.y-Math.floor(e.y);break;case Ai:e.y=e.y<0?0:1;break;case Fo:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}Wt.DEFAULT_IMAGE=null;Wt.DEFAULT_MAPPING=Xh;Wt.DEFAULT_ANISOTROPY=1;class ht{constructor(e=0,t=0,n=0,s=1){ht.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=s}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,s){return this.x=e,this.y=t,this.z=n,this.w=s,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=this.w,o=e.elements;return this.x=o[0]*t+o[4]*n+o[8]*s+o[12]*r,this.y=o[1]*t+o[5]*n+o[9]*s+o[13]*r,this.z=o[2]*t+o[6]*n+o[10]*s+o[14]*r,this.w=o[3]*t+o[7]*n+o[11]*s+o[15]*r,this}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this.w/=e.w,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,s,r;const c=e.elements,l=c[0],u=c[4],f=c[8],h=c[1],d=c[5],m=c[9],_=c[2],g=c[6],p=c[10];if(Math.abs(u-h)<.01&&Math.abs(f-_)<.01&&Math.abs(m-g)<.01){if(Math.abs(u+h)<.1&&Math.abs(f+_)<.1&&Math.abs(m+g)<.1&&Math.abs(l+d+p-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const v=(l+1)/2,x=(d+1)/2,L=(p+1)/2,T=(u+h)/4,R=(f+_)/4,I=(m+g)/4;return v>x&&v>L?v<.01?(n=0,s=.707106781,r=.707106781):(n=Math.sqrt(v),s=T/n,r=R/n):x>L?x<.01?(n=.707106781,s=0,r=.707106781):(s=Math.sqrt(x),n=T/s,r=I/s):L<.01?(n=.707106781,s=.707106781,r=0):(r=Math.sqrt(L),n=R/r,s=I/r),this.set(n,s,r,t),this}let M=Math.sqrt((g-m)*(g-m)+(f-_)*(f-_)+(h-u)*(h-u));return Math.abs(M)<.001&&(M=1),this.x=(g-m)/M,this.y=(f-_)/M,this.z=(h-u)/M,this.w=Math.acos((l+d+p-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class Up extends $s{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new ht(0,0,e,t),this.scissorTest=!1,this.viewport=new ht(0,0,e,t);const s={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:gn,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const r=new Wt(s,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);r.flipY=!1,r.generateMipmaps=n.generateMipmaps,r.internalFormat=n.internalFormat,this.textures=[];const o=n.count;for(let a=0;a<o;a++)this.textures[a]=r.clone(),this.textures[a].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let s=0,r=this.textures.length;s<r;s++)this.textures[s].image.width=e,this.textures[s].image.height=t,this.textures[s].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,s=e.textures.length;n<s;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new af(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class ts extends Up{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class cf extends Wt{constructor(e=null,t=1,n=1,s=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=rn,this.minFilter=rn,this.wrapR=Ai,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class Op extends Wt{constructor(e=null,t=1,n=1,s=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:s},this.magFilter=rn,this.minFilter=rn,this.wrapR=Ai,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class On{constructor(e=0,t=0,n=0,s=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=s}static slerpFlat(e,t,n,s,r,o,a){let c=n[s+0],l=n[s+1],u=n[s+2],f=n[s+3];const h=r[o+0],d=r[o+1],m=r[o+2],_=r[o+3];if(a===0){e[t+0]=c,e[t+1]=l,e[t+2]=u,e[t+3]=f;return}if(a===1){e[t+0]=h,e[t+1]=d,e[t+2]=m,e[t+3]=_;return}if(f!==_||c!==h||l!==d||u!==m){let g=1-a;const p=c*h+l*d+u*m+f*_,M=p>=0?1:-1,v=1-p*p;if(v>Number.EPSILON){const L=Math.sqrt(v),T=Math.atan2(L,p*M);g=Math.sin(g*T)/L,a=Math.sin(a*T)/L}const x=a*M;if(c=c*g+h*x,l=l*g+d*x,u=u*g+m*x,f=f*g+_*x,g===1-a){const L=1/Math.sqrt(c*c+l*l+u*u+f*f);c*=L,l*=L,u*=L,f*=L}}e[t]=c,e[t+1]=l,e[t+2]=u,e[t+3]=f}static multiplyQuaternionsFlat(e,t,n,s,r,o){const a=n[s],c=n[s+1],l=n[s+2],u=n[s+3],f=r[o],h=r[o+1],d=r[o+2],m=r[o+3];return e[t]=a*m+u*f+c*d-l*h,e[t+1]=c*m+u*h+l*f-a*d,e[t+2]=l*m+u*d+a*h-c*f,e[t+3]=u*m-a*f-c*h-l*d,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,s){return this._x=e,this._y=t,this._z=n,this._w=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,s=e._y,r=e._z,o=e._order,a=Math.cos,c=Math.sin,l=a(n/2),u=a(s/2),f=a(r/2),h=c(n/2),d=c(s/2),m=c(r/2);switch(o){case"XYZ":this._x=h*u*f+l*d*m,this._y=l*d*f-h*u*m,this._z=l*u*m+h*d*f,this._w=l*u*f-h*d*m;break;case"YXZ":this._x=h*u*f+l*d*m,this._y=l*d*f-h*u*m,this._z=l*u*m-h*d*f,this._w=l*u*f+h*d*m;break;case"ZXY":this._x=h*u*f-l*d*m,this._y=l*d*f+h*u*m,this._z=l*u*m+h*d*f,this._w=l*u*f-h*d*m;break;case"ZYX":this._x=h*u*f-l*d*m,this._y=l*d*f+h*u*m,this._z=l*u*m-h*d*f,this._w=l*u*f+h*d*m;break;case"YZX":this._x=h*u*f+l*d*m,this._y=l*d*f+h*u*m,this._z=l*u*m-h*d*f,this._w=l*u*f-h*d*m;break;case"XZY":this._x=h*u*f-l*d*m,this._y=l*d*f-h*u*m,this._z=l*u*m+h*d*f,this._w=l*u*f+h*d*m;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+o)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,s=Math.sin(n);return this._x=e.x*s,this._y=e.y*s,this._z=e.z*s,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],s=t[4],r=t[8],o=t[1],a=t[5],c=t[9],l=t[2],u=t[6],f=t[10],h=n+a+f;if(h>0){const d=.5/Math.sqrt(h+1);this._w=.25/d,this._x=(u-c)*d,this._y=(r-l)*d,this._z=(o-s)*d}else if(n>a&&n>f){const d=2*Math.sqrt(1+n-a-f);this._w=(u-c)/d,this._x=.25*d,this._y=(s+o)/d,this._z=(r+l)/d}else if(a>f){const d=2*Math.sqrt(1+a-n-f);this._w=(r-l)/d,this._x=(s+o)/d,this._y=.25*d,this._z=(c+u)/d}else{const d=2*Math.sqrt(1+f-n-a);this._w=(o-s)/d,this._x=(r+l)/d,this._y=(c+u)/d,this._z=.25*d}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Bt(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const s=Math.min(1,t/n);return this.slerp(e,s),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,s=e._y,r=e._z,o=e._w,a=t._x,c=t._y,l=t._z,u=t._w;return this._x=n*u+o*a+s*l-r*c,this._y=s*u+o*c+r*a-n*l,this._z=r*u+o*l+n*c-s*a,this._w=o*u-n*a-s*c-r*l,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,s=this._y,r=this._z,o=this._w;let a=o*e._w+n*e._x+s*e._y+r*e._z;if(a<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,a=-a):this.copy(e),a>=1)return this._w=o,this._x=n,this._y=s,this._z=r,this;const c=1-a*a;if(c<=Number.EPSILON){const d=1-t;return this._w=d*o+t*this._w,this._x=d*n+t*this._x,this._y=d*s+t*this._y,this._z=d*r+t*this._z,this.normalize(),this}const l=Math.sqrt(c),u=Math.atan2(l,a),f=Math.sin((1-t)*u)/l,h=Math.sin(t*u)/l;return this._w=o*f+this._w*h,this._x=n*f+this._x*h,this._y=s*f+this._y*h,this._z=r*f+this._z*h,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),s=Math.sqrt(1-n),r=Math.sqrt(n);return this.set(s*Math.sin(e),s*Math.cos(e),r*Math.sin(t),r*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class b{constructor(e=0,t=0,n=0){b.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(fu.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(fu.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[3]*n+r[6]*s,this.y=r[1]*t+r[4]*n+r[7]*s,this.z=r[2]*t+r[5]*n+r[8]*s,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,s=this.z,r=e.elements,o=1/(r[3]*t+r[7]*n+r[11]*s+r[15]);return this.x=(r[0]*t+r[4]*n+r[8]*s+r[12])*o,this.y=(r[1]*t+r[5]*n+r[9]*s+r[13])*o,this.z=(r[2]*t+r[6]*n+r[10]*s+r[14])*o,this}applyQuaternion(e){const t=this.x,n=this.y,s=this.z,r=e.x,o=e.y,a=e.z,c=e.w,l=2*(o*s-a*n),u=2*(a*t-r*s),f=2*(r*n-o*t);return this.x=t+c*l+o*f-a*u,this.y=n+c*u+a*l-r*f,this.z=s+c*f+r*u-o*l,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,s=this.z,r=e.elements;return this.x=r[0]*t+r[4]*n+r[8]*s,this.y=r[1]*t+r[5]*n+r[9]*s,this.z=r[2]*t+r[6]*n+r[10]*s,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,s=e.y,r=e.z,o=t.x,a=t.y,c=t.z;return this.x=s*c-r*a,this.y=r*o-n*c,this.z=n*a-s*o,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return pa.copy(this).projectOnVector(e),this.sub(pa)}reflect(e){return this.sub(pa.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Bt(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,s=this.z-e.z;return t*t+n*n+s*s}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const s=Math.sin(t)*e;return this.x=s*Math.sin(n),this.y=Math.cos(t)*e,this.z=s*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),s=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=s,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const pa=new b,fu=new On;class on{constructor(e=new b(1/0,1/0,1/0),t=new b(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(Cn.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(Cn.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=Cn.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const r=n.getAttribute("position");if(t===!0&&r!==void 0&&e.isInstancedMesh!==!0)for(let o=0,a=r.count;o<a;o++)e.isMesh===!0?e.getVertexPosition(o,Cn):Cn.fromBufferAttribute(r,o),Cn.applyMatrix4(e.matrixWorld),this.expandByPoint(Cn);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),Vr.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),Vr.copy(n.boundingBox)),Vr.applyMatrix4(e.matrixWorld),this.union(Vr)}const s=e.children;for(let r=0,o=s.length;r<o;r++)this.expandByObject(s[r],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,Cn),Cn.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(sr),Gr.subVectors(this.max,sr),fs.subVectors(e.a,sr),ds.subVectors(e.b,sr),ps.subVectors(e.c,sr),_i.subVectors(ds,fs),xi.subVectors(ps,ds),Vi.subVectors(fs,ps);let t=[0,-_i.z,_i.y,0,-xi.z,xi.y,0,-Vi.z,Vi.y,_i.z,0,-_i.x,xi.z,0,-xi.x,Vi.z,0,-Vi.x,-_i.y,_i.x,0,-xi.y,xi.x,0,-Vi.y,Vi.x,0];return!ma(t,fs,ds,ps,Gr)||(t=[1,0,0,0,1,0,0,0,1],!ma(t,fs,ds,ps,Gr))?!1:(Wr.crossVectors(_i,xi),t=[Wr.x,Wr.y,Wr.z],ma(t,fs,ds,ps,Gr))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,Cn).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(Cn).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:($n[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),$n[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),$n[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),$n[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),$n[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),$n[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),$n[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),$n[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints($n),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const $n=[new b,new b,new b,new b,new b,new b,new b,new b],Cn=new b,Vr=new on,fs=new b,ds=new b,ps=new b,_i=new b,xi=new b,Vi=new b,sr=new b,Gr=new b,Wr=new b,Gi=new b;function ma(i,e,t,n,s){for(let r=0,o=i.length-3;r<=o;r+=3){Gi.fromArray(i,r);const a=s.x*Math.abs(Gi.x)+s.y*Math.abs(Gi.y)+s.z*Math.abs(Gi.z),c=e.dot(Gi),l=t.dot(Gi),u=n.dot(Gi);if(Math.max(-Math.max(c,l,u),Math.min(c,l,u))>a)return!1}return!0}const Fp=new on,rr=new b,ga=new b;class Gn{constructor(e=new b,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):Fp.setFromPoints(e).getCenter(n);let s=0;for(let r=0,o=e.length;r<o;r++)s=Math.max(s,n.distanceToSquared(e[r]));return this.radius=Math.sqrt(s),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;rr.subVectors(e,this.center);const t=rr.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),s=(n-this.radius)*.5;this.center.addScaledVector(rr,s/n),this.radius+=s}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(ga.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(rr.copy(e.center).add(ga)),this.expandByPoint(rr.copy(e.center).sub(ga))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Kn=new b,_a=new b,Xr=new b,vi=new b,xa=new b,qr=new b,va=new b;class Ko{constructor(e=new b,t=new b(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Kn)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Kn.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Kn.copy(this.origin).addScaledVector(this.direction,t),Kn.distanceToSquared(e))}distanceSqToSegment(e,t,n,s){_a.copy(e).add(t).multiplyScalar(.5),Xr.copy(t).sub(e).normalize(),vi.copy(this.origin).sub(_a);const r=e.distanceTo(t)*.5,o=-this.direction.dot(Xr),a=vi.dot(this.direction),c=-vi.dot(Xr),l=vi.lengthSq(),u=Math.abs(1-o*o);let f,h,d,m;if(u>0)if(f=o*c-a,h=o*a-c,m=r*u,f>=0)if(h>=-m)if(h<=m){const _=1/u;f*=_,h*=_,d=f*(f+o*h+2*a)+h*(o*f+h+2*c)+l}else h=r,f=Math.max(0,-(o*h+a)),d=-f*f+h*(h+2*c)+l;else h=-r,f=Math.max(0,-(o*h+a)),d=-f*f+h*(h+2*c)+l;else h<=-m?(f=Math.max(0,-(-o*r+a)),h=f>0?-r:Math.min(Math.max(-r,-c),r),d=-f*f+h*(h+2*c)+l):h<=m?(f=0,h=Math.min(Math.max(-r,-c),r),d=h*(h+2*c)+l):(f=Math.max(0,-(o*r+a)),h=f>0?r:Math.min(Math.max(-r,-c),r),d=-f*f+h*(h+2*c)+l);else h=o>0?-r:r,f=Math.max(0,-(o*h+a)),d=-f*f+h*(h+2*c)+l;return n&&n.copy(this.origin).addScaledVector(this.direction,f),s&&s.copy(_a).addScaledVector(Xr,h),d}intersectSphere(e,t){Kn.subVectors(e.center,this.origin);const n=Kn.dot(this.direction),s=Kn.dot(Kn)-n*n,r=e.radius*e.radius;if(s>r)return null;const o=Math.sqrt(r-s),a=n-o,c=n+o;return c<0?null:a<0?this.at(c,t):this.at(a,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,s,r,o,a,c;const l=1/this.direction.x,u=1/this.direction.y,f=1/this.direction.z,h=this.origin;return l>=0?(n=(e.min.x-h.x)*l,s=(e.max.x-h.x)*l):(n=(e.max.x-h.x)*l,s=(e.min.x-h.x)*l),u>=0?(r=(e.min.y-h.y)*u,o=(e.max.y-h.y)*u):(r=(e.max.y-h.y)*u,o=(e.min.y-h.y)*u),n>o||r>s||((r>n||isNaN(n))&&(n=r),(o<s||isNaN(s))&&(s=o),f>=0?(a=(e.min.z-h.z)*f,c=(e.max.z-h.z)*f):(a=(e.max.z-h.z)*f,c=(e.min.z-h.z)*f),n>c||a>s)||((a>n||n!==n)&&(n=a),(c<s||s!==s)&&(s=c),s<0)?null:this.at(n>=0?n:s,t)}intersectsBox(e){return this.intersectBox(e,Kn)!==null}intersectTriangle(e,t,n,s,r){xa.subVectors(t,e),qr.subVectors(n,e),va.crossVectors(xa,qr);let o=this.direction.dot(va),a;if(o>0){if(s)return null;a=1}else if(o<0)a=-1,o=-o;else return null;vi.subVectors(this.origin,e);const c=a*this.direction.dot(qr.crossVectors(vi,qr));if(c<0)return null;const l=a*this.direction.dot(xa.cross(vi));if(l<0||c+l>o)return null;const u=-a*vi.dot(va);return u<0?null:this.at(u/o,r)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class De{constructor(e,t,n,s,r,o,a,c,l,u,f,h,d,m,_,g){De.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,s,r,o,a,c,l,u,f,h,d,m,_,g)}set(e,t,n,s,r,o,a,c,l,u,f,h,d,m,_,g){const p=this.elements;return p[0]=e,p[4]=t,p[8]=n,p[12]=s,p[1]=r,p[5]=o,p[9]=a,p[13]=c,p[2]=l,p[6]=u,p[10]=f,p[14]=h,p[3]=d,p[7]=m,p[11]=_,p[15]=g,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new De().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,s=1/ms.setFromMatrixColumn(e,0).length(),r=1/ms.setFromMatrixColumn(e,1).length(),o=1/ms.setFromMatrixColumn(e,2).length();return t[0]=n[0]*s,t[1]=n[1]*s,t[2]=n[2]*s,t[3]=0,t[4]=n[4]*r,t[5]=n[5]*r,t[6]=n[6]*r,t[7]=0,t[8]=n[8]*o,t[9]=n[9]*o,t[10]=n[10]*o,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,s=e.y,r=e.z,o=Math.cos(n),a=Math.sin(n),c=Math.cos(s),l=Math.sin(s),u=Math.cos(r),f=Math.sin(r);if(e.order==="XYZ"){const h=o*u,d=o*f,m=a*u,_=a*f;t[0]=c*u,t[4]=-c*f,t[8]=l,t[1]=d+m*l,t[5]=h-_*l,t[9]=-a*c,t[2]=_-h*l,t[6]=m+d*l,t[10]=o*c}else if(e.order==="YXZ"){const h=c*u,d=c*f,m=l*u,_=l*f;t[0]=h+_*a,t[4]=m*a-d,t[8]=o*l,t[1]=o*f,t[5]=o*u,t[9]=-a,t[2]=d*a-m,t[6]=_+h*a,t[10]=o*c}else if(e.order==="ZXY"){const h=c*u,d=c*f,m=l*u,_=l*f;t[0]=h-_*a,t[4]=-o*f,t[8]=m+d*a,t[1]=d+m*a,t[5]=o*u,t[9]=_-h*a,t[2]=-o*l,t[6]=a,t[10]=o*c}else if(e.order==="ZYX"){const h=o*u,d=o*f,m=a*u,_=a*f;t[0]=c*u,t[4]=m*l-d,t[8]=h*l+_,t[1]=c*f,t[5]=_*l+h,t[9]=d*l-m,t[2]=-l,t[6]=a*c,t[10]=o*c}else if(e.order==="YZX"){const h=o*c,d=o*l,m=a*c,_=a*l;t[0]=c*u,t[4]=_-h*f,t[8]=m*f+d,t[1]=f,t[5]=o*u,t[9]=-a*u,t[2]=-l*u,t[6]=d*f+m,t[10]=h-_*f}else if(e.order==="XZY"){const h=o*c,d=o*l,m=a*c,_=a*l;t[0]=c*u,t[4]=-f,t[8]=l*u,t[1]=h*f+_,t[5]=o*u,t[9]=d*f-m,t[2]=m*f-d,t[6]=a*u,t[10]=_*f+h}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(Bp,e,kp)}lookAt(e,t,n){const s=this.elements;return dn.subVectors(e,t),dn.lengthSq()===0&&(dn.z=1),dn.normalize(),yi.crossVectors(n,dn),yi.lengthSq()===0&&(Math.abs(n.z)===1?dn.x+=1e-4:dn.z+=1e-4,dn.normalize(),yi.crossVectors(n,dn)),yi.normalize(),Yr.crossVectors(dn,yi),s[0]=yi.x,s[4]=Yr.x,s[8]=dn.x,s[1]=yi.y,s[5]=Yr.y,s[9]=dn.y,s[2]=yi.z,s[6]=Yr.z,s[10]=dn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,s=t.elements,r=this.elements,o=n[0],a=n[4],c=n[8],l=n[12],u=n[1],f=n[5],h=n[9],d=n[13],m=n[2],_=n[6],g=n[10],p=n[14],M=n[3],v=n[7],x=n[11],L=n[15],T=s[0],R=s[4],I=s[8],w=s[12],S=s[1],P=s[5],G=s[9],B=s[13],V=s[2],j=s[6],W=s[10],ee=s[14],O=s[3],re=s[7],ue=s[11],Me=s[15];return r[0]=o*T+a*S+c*V+l*O,r[4]=o*R+a*P+c*j+l*re,r[8]=o*I+a*G+c*W+l*ue,r[12]=o*w+a*B+c*ee+l*Me,r[1]=u*T+f*S+h*V+d*O,r[5]=u*R+f*P+h*j+d*re,r[9]=u*I+f*G+h*W+d*ue,r[13]=u*w+f*B+h*ee+d*Me,r[2]=m*T+_*S+g*V+p*O,r[6]=m*R+_*P+g*j+p*re,r[10]=m*I+_*G+g*W+p*ue,r[14]=m*w+_*B+g*ee+p*Me,r[3]=M*T+v*S+x*V+L*O,r[7]=M*R+v*P+x*j+L*re,r[11]=M*I+v*G+x*W+L*ue,r[15]=M*w+v*B+x*ee+L*Me,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],s=e[8],r=e[12],o=e[1],a=e[5],c=e[9],l=e[13],u=e[2],f=e[6],h=e[10],d=e[14],m=e[3],_=e[7],g=e[11],p=e[15];return m*(+r*c*f-s*l*f-r*a*h+n*l*h+s*a*d-n*c*d)+_*(+t*c*d-t*l*h+r*o*h-s*o*d+s*l*u-r*c*u)+g*(+t*l*f-t*a*d-r*o*f+n*o*d+r*a*u-n*l*u)+p*(-s*a*u-t*c*f+t*a*h+s*o*f-n*o*h+n*c*u)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const s=this.elements;return e.isVector3?(s[12]=e.x,s[13]=e.y,s[14]=e.z):(s[12]=e,s[13]=t,s[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],s=e[2],r=e[3],o=e[4],a=e[5],c=e[6],l=e[7],u=e[8],f=e[9],h=e[10],d=e[11],m=e[12],_=e[13],g=e[14],p=e[15],M=f*g*l-_*h*l+_*c*d-a*g*d-f*c*p+a*h*p,v=m*h*l-u*g*l-m*c*d+o*g*d+u*c*p-o*h*p,x=u*_*l-m*f*l+m*a*d-o*_*d-u*a*p+o*f*p,L=m*f*c-u*_*c-m*a*h+o*_*h+u*a*g-o*f*g,T=t*M+n*v+s*x+r*L;if(T===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const R=1/T;return e[0]=M*R,e[1]=(_*h*r-f*g*r-_*s*d+n*g*d+f*s*p-n*h*p)*R,e[2]=(a*g*r-_*c*r+_*s*l-n*g*l-a*s*p+n*c*p)*R,e[3]=(f*c*r-a*h*r-f*s*l+n*h*l+a*s*d-n*c*d)*R,e[4]=v*R,e[5]=(u*g*r-m*h*r+m*s*d-t*g*d-u*s*p+t*h*p)*R,e[6]=(m*c*r-o*g*r-m*s*l+t*g*l+o*s*p-t*c*p)*R,e[7]=(o*h*r-u*c*r+u*s*l-t*h*l-o*s*d+t*c*d)*R,e[8]=x*R,e[9]=(m*f*r-u*_*r-m*n*d+t*_*d+u*n*p-t*f*p)*R,e[10]=(o*_*r-m*a*r+m*n*l-t*_*l-o*n*p+t*a*p)*R,e[11]=(u*a*r-o*f*r-u*n*l+t*f*l+o*n*d-t*a*d)*R,e[12]=L*R,e[13]=(u*_*s-m*f*s+m*n*h-t*_*h-u*n*g+t*f*g)*R,e[14]=(m*a*s-o*_*s-m*n*c+t*_*c+o*n*g-t*a*g)*R,e[15]=(o*f*s-u*a*s+u*n*c-t*f*c-o*n*h+t*a*h)*R,this}scale(e){const t=this.elements,n=e.x,s=e.y,r=e.z;return t[0]*=n,t[4]*=s,t[8]*=r,t[1]*=n,t[5]*=s,t[9]*=r,t[2]*=n,t[6]*=s,t[10]*=r,t[3]*=n,t[7]*=s,t[11]*=r,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],s=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,s))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),s=Math.sin(t),r=1-n,o=e.x,a=e.y,c=e.z,l=r*o,u=r*a;return this.set(l*o+n,l*a-s*c,l*c+s*a,0,l*a+s*c,u*a+n,u*c-s*o,0,l*c-s*a,u*c+s*o,r*c*c+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,s,r,o){return this.set(1,n,r,0,e,1,o,0,t,s,1,0,0,0,0,1),this}compose(e,t,n){const s=this.elements,r=t._x,o=t._y,a=t._z,c=t._w,l=r+r,u=o+o,f=a+a,h=r*l,d=r*u,m=r*f,_=o*u,g=o*f,p=a*f,M=c*l,v=c*u,x=c*f,L=n.x,T=n.y,R=n.z;return s[0]=(1-(_+p))*L,s[1]=(d+x)*L,s[2]=(m-v)*L,s[3]=0,s[4]=(d-x)*T,s[5]=(1-(h+p))*T,s[6]=(g+M)*T,s[7]=0,s[8]=(m+v)*R,s[9]=(g-M)*R,s[10]=(1-(h+_))*R,s[11]=0,s[12]=e.x,s[13]=e.y,s[14]=e.z,s[15]=1,this}decompose(e,t,n){const s=this.elements;let r=ms.set(s[0],s[1],s[2]).length();const o=ms.set(s[4],s[5],s[6]).length(),a=ms.set(s[8],s[9],s[10]).length();this.determinant()<0&&(r=-r),e.x=s[12],e.y=s[13],e.z=s[14],Pn.copy(this);const l=1/r,u=1/o,f=1/a;return Pn.elements[0]*=l,Pn.elements[1]*=l,Pn.elements[2]*=l,Pn.elements[4]*=u,Pn.elements[5]*=u,Pn.elements[6]*=u,Pn.elements[8]*=f,Pn.elements[9]*=f,Pn.elements[10]*=f,t.setFromRotationMatrix(Pn),n.x=r,n.y=o,n.z=a,this}makePerspective(e,t,n,s,r,o,a=ai){const c=this.elements,l=2*r/(t-e),u=2*r/(n-s),f=(t+e)/(t-e),h=(n+s)/(n-s);let d,m;if(a===ai)d=-(o+r)/(o-r),m=-2*o*r/(o-r);else if(a===Bo)d=-o/(o-r),m=-o*r/(o-r);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+a);return c[0]=l,c[4]=0,c[8]=f,c[12]=0,c[1]=0,c[5]=u,c[9]=h,c[13]=0,c[2]=0,c[6]=0,c[10]=d,c[14]=m,c[3]=0,c[7]=0,c[11]=-1,c[15]=0,this}makeOrthographic(e,t,n,s,r,o,a=ai){const c=this.elements,l=1/(t-e),u=1/(n-s),f=1/(o-r),h=(t+e)*l,d=(n+s)*u;let m,_;if(a===ai)m=(o+r)*f,_=-2*f;else if(a===Bo)m=r*f,_=-1*f;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+a);return c[0]=2*l,c[4]=0,c[8]=0,c[12]=-h,c[1]=0,c[5]=2*u,c[9]=0,c[13]=-d,c[2]=0,c[6]=0,c[10]=_,c[14]=-m,c[3]=0,c[7]=0,c[11]=0,c[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let s=0;s<16;s++)if(t[s]!==n[s])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const ms=new b,Pn=new De,Bp=new b(0,0,0),kp=new b(1,1,1),yi=new b,Yr=new b,dn=new b,du=new De,pu=new On;class Un{constructor(e=0,t=0,n=0,s=Un.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=s}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,s=this._order){return this._x=e,this._y=t,this._z=n,this._order=s,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const s=e.elements,r=s[0],o=s[4],a=s[8],c=s[1],l=s[5],u=s[9],f=s[2],h=s[6],d=s[10];switch(t){case"XYZ":this._y=Math.asin(Bt(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(-u,d),this._z=Math.atan2(-o,r)):(this._x=Math.atan2(h,l),this._z=0);break;case"YXZ":this._x=Math.asin(-Bt(u,-1,1)),Math.abs(u)<.9999999?(this._y=Math.atan2(a,d),this._z=Math.atan2(c,l)):(this._y=Math.atan2(-f,r),this._z=0);break;case"ZXY":this._x=Math.asin(Bt(h,-1,1)),Math.abs(h)<.9999999?(this._y=Math.atan2(-f,d),this._z=Math.atan2(-o,l)):(this._y=0,this._z=Math.atan2(c,r));break;case"ZYX":this._y=Math.asin(-Bt(f,-1,1)),Math.abs(f)<.9999999?(this._x=Math.atan2(h,d),this._z=Math.atan2(c,r)):(this._x=0,this._z=Math.atan2(-o,l));break;case"YZX":this._z=Math.asin(Bt(c,-1,1)),Math.abs(c)<.9999999?(this._x=Math.atan2(-u,l),this._y=Math.atan2(-f,r)):(this._x=0,this._y=Math.atan2(a,d));break;case"XZY":this._z=Math.asin(-Bt(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(h,l),this._y=Math.atan2(a,r)):(this._x=Math.atan2(-u,d),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return du.makeRotationFromQuaternion(e),this.setFromRotationMatrix(du,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return pu.setFromEuler(this),this.setFromQuaternion(pu,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}Un.DEFAULT_ORDER="XYZ";class lf{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let zp=0;const mu=new b,gs=new On,Zn=new De,jr=new b,or=new b,Hp=new b,Vp=new On,gu=new b(1,0,0),_u=new b(0,1,0),xu=new b(0,0,1),vu={type:"added"},Gp={type:"removed"},_s={type:"childadded",child:null},ya={type:"childremoved",child:null};class At extends $s{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:zp++}),this.uuid=wn(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=At.DEFAULT_UP.clone();const e=new b,t=new Un,n=new On,s=new b(1,1,1);function r(){n.setFromEuler(t,!1)}function o(){t.setFromQuaternion(n,void 0,!1)}t._onChange(r),n._onChange(o),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:s},modelViewMatrix:{value:new De},normalMatrix:{value:new et}}),this.matrix=new De,this.matrixWorld=new De,this.matrixAutoUpdate=At.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=At.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new lf,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return gs.setFromAxisAngle(e,t),this.quaternion.multiply(gs),this}rotateOnWorldAxis(e,t){return gs.setFromAxisAngle(e,t),this.quaternion.premultiply(gs),this}rotateX(e){return this.rotateOnAxis(gu,e)}rotateY(e){return this.rotateOnAxis(_u,e)}rotateZ(e){return this.rotateOnAxis(xu,e)}translateOnAxis(e,t){return mu.copy(e).applyQuaternion(this.quaternion),this.position.add(mu.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(gu,e)}translateY(e){return this.translateOnAxis(_u,e)}translateZ(e){return this.translateOnAxis(xu,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(Zn.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?jr.copy(e):jr.set(e,t,n);const s=this.parent;this.updateWorldMatrix(!0,!1),or.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Zn.lookAt(or,jr,this.up):Zn.lookAt(jr,or,this.up),this.quaternion.setFromRotationMatrix(Zn),s&&(Zn.extractRotation(s.matrixWorld),gs.setFromRotationMatrix(Zn),this.quaternion.premultiply(gs.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(vu),_s.child=e,this.dispatchEvent(_s),_s.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(Gp),ya.child=e,this.dispatchEvent(ya),ya.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),Zn.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),Zn.multiply(e.parent.matrixWorld)),e.applyMatrix4(Zn),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(vu),_s.child=e,this.dispatchEvent(_s),_s.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,s=this.children.length;n<s;n++){const o=this.children[n].getObjectByProperty(e,t);if(o!==void 0)return o}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const s=this.children;for(let r=0,o=s.length;r<o;r++)s[r].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(or,e,Hp),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(or,Vp,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,s=t.length;n<s;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const s=this.children;for(let r=0,o=s.length;r<o;r++)s[r].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const s={};s.uuid=this.uuid,s.type=this.type,this.name!==""&&(s.name=this.name),this.castShadow===!0&&(s.castShadow=!0),this.receiveShadow===!0&&(s.receiveShadow=!0),this.visible===!1&&(s.visible=!1),this.frustumCulled===!1&&(s.frustumCulled=!1),this.renderOrder!==0&&(s.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(s.userData=this.userData),s.layers=this.layers.mask,s.matrix=this.matrix.toArray(),s.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(s.matrixAutoUpdate=!1),this.isInstancedMesh&&(s.type="InstancedMesh",s.count=this.count,s.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(s.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(s.type="BatchedMesh",s.perObjectFrustumCulled=this.perObjectFrustumCulled,s.sortObjects=this.sortObjects,s.drawRanges=this._drawRanges,s.reservedRanges=this._reservedRanges,s.visibility=this._visibility,s.active=this._active,s.bounds=this._bounds.map(a=>({boxInitialized:a.boxInitialized,boxMin:a.box.min.toArray(),boxMax:a.box.max.toArray(),sphereInitialized:a.sphereInitialized,sphereRadius:a.sphere.radius,sphereCenter:a.sphere.center.toArray()})),s.maxInstanceCount=this._maxInstanceCount,s.maxVertexCount=this._maxVertexCount,s.maxIndexCount=this._maxIndexCount,s.geometryInitialized=this._geometryInitialized,s.geometryCount=this._geometryCount,s.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(s.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(s.boundingSphere={center:s.boundingSphere.center.toArray(),radius:s.boundingSphere.radius}),this.boundingBox!==null&&(s.boundingBox={min:s.boundingBox.min.toArray(),max:s.boundingBox.max.toArray()}));function r(a,c){return a[c.uuid]===void 0&&(a[c.uuid]=c.toJSON(e)),c.uuid}if(this.isScene)this.background&&(this.background.isColor?s.background=this.background.toJSON():this.background.isTexture&&(s.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(s.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){s.geometry=r(e.geometries,this.geometry);const a=this.geometry.parameters;if(a!==void 0&&a.shapes!==void 0){const c=a.shapes;if(Array.isArray(c))for(let l=0,u=c.length;l<u;l++){const f=c[l];r(e.shapes,f)}else r(e.shapes,c)}}if(this.isSkinnedMesh&&(s.bindMode=this.bindMode,s.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(r(e.skeletons,this.skeleton),s.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const a=[];for(let c=0,l=this.material.length;c<l;c++)a.push(r(e.materials,this.material[c]));s.material=a}else s.material=r(e.materials,this.material);if(this.children.length>0){s.children=[];for(let a=0;a<this.children.length;a++)s.children.push(this.children[a].toJSON(e).object)}if(this.animations.length>0){s.animations=[];for(let a=0;a<this.animations.length;a++){const c=this.animations[a];s.animations.push(r(e.animations,c))}}if(t){const a=o(e.geometries),c=o(e.materials),l=o(e.textures),u=o(e.images),f=o(e.shapes),h=o(e.skeletons),d=o(e.animations),m=o(e.nodes);a.length>0&&(n.geometries=a),c.length>0&&(n.materials=c),l.length>0&&(n.textures=l),u.length>0&&(n.images=u),f.length>0&&(n.shapes=f),h.length>0&&(n.skeletons=h),d.length>0&&(n.animations=d),m.length>0&&(n.nodes=m)}return n.object=s,n;function o(a){const c=[];for(const l in a){const u=a[l];delete u.metadata,c.push(u)}return c}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const s=e.children[n];this.add(s.clone())}return this}}At.DEFAULT_UP=new b(0,1,0);At.DEFAULT_MATRIX_AUTO_UPDATE=!0;At.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const Ln=new b,Jn=new b,Ma=new b,Qn=new b,xs=new b,vs=new b,yu=new b,Sa=new b,Ea=new b,ba=new b,wa=new ht,Ta=new ht,Aa=new ht;class En{constructor(e=new b,t=new b,n=new b){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,s){s.subVectors(n,t),Ln.subVectors(e,t),s.cross(Ln);const r=s.lengthSq();return r>0?s.multiplyScalar(1/Math.sqrt(r)):s.set(0,0,0)}static getBarycoord(e,t,n,s,r){Ln.subVectors(s,t),Jn.subVectors(n,t),Ma.subVectors(e,t);const o=Ln.dot(Ln),a=Ln.dot(Jn),c=Ln.dot(Ma),l=Jn.dot(Jn),u=Jn.dot(Ma),f=o*l-a*a;if(f===0)return r.set(0,0,0),null;const h=1/f,d=(l*c-a*u)*h,m=(o*u-a*c)*h;return r.set(1-d-m,m,d)}static containsPoint(e,t,n,s){return this.getBarycoord(e,t,n,s,Qn)===null?!1:Qn.x>=0&&Qn.y>=0&&Qn.x+Qn.y<=1}static getInterpolation(e,t,n,s,r,o,a,c){return this.getBarycoord(e,t,n,s,Qn)===null?(c.x=0,c.y=0,"z"in c&&(c.z=0),"w"in c&&(c.w=0),null):(c.setScalar(0),c.addScaledVector(r,Qn.x),c.addScaledVector(o,Qn.y),c.addScaledVector(a,Qn.z),c)}static getInterpolatedAttribute(e,t,n,s,r,o){return wa.setScalar(0),Ta.setScalar(0),Aa.setScalar(0),wa.fromBufferAttribute(e,t),Ta.fromBufferAttribute(e,n),Aa.fromBufferAttribute(e,s),o.setScalar(0),o.addScaledVector(wa,r.x),o.addScaledVector(Ta,r.y),o.addScaledVector(Aa,r.z),o}static isFrontFacing(e,t,n,s){return Ln.subVectors(n,t),Jn.subVectors(e,t),Ln.cross(Jn).dot(s)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,s){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[s]),this}setFromAttributeAndIndices(e,t,n,s){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,s),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return Ln.subVectors(this.c,this.b),Jn.subVectors(this.a,this.b),Ln.cross(Jn).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return En.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return En.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,s,r){return En.getInterpolation(e,this.a,this.b,this.c,t,n,s,r)}containsPoint(e){return En.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return En.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,s=this.b,r=this.c;let o,a;xs.subVectors(s,n),vs.subVectors(r,n),Sa.subVectors(e,n);const c=xs.dot(Sa),l=vs.dot(Sa);if(c<=0&&l<=0)return t.copy(n);Ea.subVectors(e,s);const u=xs.dot(Ea),f=vs.dot(Ea);if(u>=0&&f<=u)return t.copy(s);const h=c*f-u*l;if(h<=0&&c>=0&&u<=0)return o=c/(c-u),t.copy(n).addScaledVector(xs,o);ba.subVectors(e,r);const d=xs.dot(ba),m=vs.dot(ba);if(m>=0&&d<=m)return t.copy(r);const _=d*l-c*m;if(_<=0&&l>=0&&m<=0)return a=l/(l-m),t.copy(n).addScaledVector(vs,a);const g=u*m-d*f;if(g<=0&&f-u>=0&&d-m>=0)return yu.subVectors(r,s),a=(f-u)/(f-u+(d-m)),t.copy(s).addScaledVector(yu,a);const p=1/(g+_+h);return o=_*p,a=h*p,t.copy(n).addScaledVector(xs,o).addScaledVector(vs,a)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const uf={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},Mi={h:0,s:0,l:0},$r={h:0,s:0,l:0};function Ra(i,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?i+(e-i)*6*t:t<1/2?e:t<2/3?i+(e-i)*6*(2/3-t):i}class Ve{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const s=e;s&&s.isColor?this.copy(s):typeof s=="number"?this.setHex(s):typeof s=="string"&&this.setStyle(s)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=Nt){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,ot.toWorkingColorSpace(this,t),this}setRGB(e,t,n,s=ot.workingColorSpace){return this.r=e,this.g=t,this.b=n,ot.toWorkingColorSpace(this,s),this}setHSL(e,t,n,s=ot.workingColorSpace){if(e=Ml(e,1),t=Bt(t,0,1),n=Bt(n,0,1),t===0)this.r=this.g=this.b=n;else{const r=n<=.5?n*(1+t):n+t-n*t,o=2*n-r;this.r=Ra(o,r,e+1/3),this.g=Ra(o,r,e),this.b=Ra(o,r,e-1/3)}return ot.toWorkingColorSpace(this,s),this}setStyle(e,t=Nt){function n(r){r!==void 0&&parseFloat(r)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let s;if(s=/^(\w+)\(([^\)]*)\)/.exec(e)){let r;const o=s[1],a=s[2];switch(o){case"rgb":case"rgba":if(r=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setRGB(Math.min(255,parseInt(r[1],10))/255,Math.min(255,parseInt(r[2],10))/255,Math.min(255,parseInt(r[3],10))/255,t);if(r=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setRGB(Math.min(100,parseInt(r[1],10))/100,Math.min(100,parseInt(r[2],10))/100,Math.min(100,parseInt(r[3],10))/100,t);break;case"hsl":case"hsla":if(r=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(r[4]),this.setHSL(parseFloat(r[1])/360,parseFloat(r[2])/100,parseFloat(r[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(s=/^\#([A-Fa-f\d]+)$/.exec(e)){const r=s[1],o=r.length;if(o===3)return this.setRGB(parseInt(r.charAt(0),16)/15,parseInt(r.charAt(1),16)/15,parseInt(r.charAt(2),16)/15,t);if(o===6)return this.setHex(parseInt(r,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=Nt){const n=uf[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=li(e.r),this.g=li(e.g),this.b=li(e.b),this}copyLinearToSRGB(e){return this.r=Ns(e.r),this.g=Ns(e.g),this.b=Ns(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=Nt){return ot.fromWorkingColorSpace(Jt.copy(this),e),Math.round(Bt(Jt.r*255,0,255))*65536+Math.round(Bt(Jt.g*255,0,255))*256+Math.round(Bt(Jt.b*255,0,255))}getHexString(e=Nt){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=ot.workingColorSpace){ot.fromWorkingColorSpace(Jt.copy(this),t);const n=Jt.r,s=Jt.g,r=Jt.b,o=Math.max(n,s,r),a=Math.min(n,s,r);let c,l;const u=(a+o)/2;if(a===o)c=0,l=0;else{const f=o-a;switch(l=u<=.5?f/(o+a):f/(2-o-a),o){case n:c=(s-r)/f+(s<r?6:0);break;case s:c=(r-n)/f+2;break;case r:c=(n-s)/f+4;break}c/=6}return e.h=c,e.s=l,e.l=u,e}getRGB(e,t=ot.workingColorSpace){return ot.fromWorkingColorSpace(Jt.copy(this),t),e.r=Jt.r,e.g=Jt.g,e.b=Jt.b,e}getStyle(e=Nt){ot.fromWorkingColorSpace(Jt.copy(this),e);const t=Jt.r,n=Jt.g,s=Jt.b;return e!==Nt?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${s.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(s*255)})`}offsetHSL(e,t,n){return this.getHSL(Mi),this.setHSL(Mi.h+e,Mi.s+t,Mi.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(Mi),e.getHSL($r);const n=Mr(Mi.h,$r.h,t),s=Mr(Mi.s,$r.s,t),r=Mr(Mi.l,$r.l,t);return this.setHSL(n,s,r),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,s=this.b,r=e.elements;return this.r=r[0]*t+r[3]*n+r[6]*s,this.g=r[1]*t+r[4]*n+r[7]*s,this.b=r[2]*t+r[5]*n+r[8]*s,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const Jt=new Ve;Ve.NAMES=uf;let Wp=0;class Hn extends $s{static get type(){return"Material"}get type(){return this.constructor.type}set type(e){}constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:Wp++}),this.uuid=wn(),this.name="",this.blending=Ls,this.side=ui,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=pc,this.blendDst=mc,this.blendEquation=Ji,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new Ve(0,0,0),this.blendAlpha=0,this.depthFunc=Fs,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=iu,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=us,this.stencilZFail=us,this.stencilZPass=us,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const s=this[t];if(s===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}s&&s.isColor?s.set(n):s&&s.isVector3&&n&&n.isVector3?s.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==Ls&&(n.blending=this.blending),this.side!==ui&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==pc&&(n.blendSrc=this.blendSrc),this.blendDst!==mc&&(n.blendDst=this.blendDst),this.blendEquation!==Ji&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Fs&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==iu&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==us&&(n.stencilFail=this.stencilFail),this.stencilZFail!==us&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==us&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function s(r){const o=[];for(const a in r){const c=r[a];delete c.metadata,o.push(c)}return o}if(t){const r=s(e.textures),o=s(e.images);r.length>0&&(n.textures=r),o.length>0&&(n.images=o)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const s=t.length;n=new Array(s);for(let r=0;r!==s;++r)n[r]=t[r].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class _n extends Hn{static get type(){return"MeshBasicMaterial"}constructor(e){super(),this.isMeshBasicMaterial=!0,this.color=new Ve(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Un,this.combine=Wh,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const Ot=new b,Kr=new ie;class Xt{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=Jc,this.updateRanges=[],this.gpuType=Dn,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let s=0,r=this.itemSize;s<r;s++)this.array[e+s]=t.array[n+s];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)Kr.fromBufferAttribute(this,t),Kr.applyMatrix3(e),this.setXY(t,Kr.x,Kr.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)Ot.fromBufferAttribute(this,t),Ot.applyMatrix3(e),this.setXYZ(t,Ot.x,Ot.y,Ot.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)Ot.fromBufferAttribute(this,t),Ot.applyMatrix4(e),this.setXYZ(t,Ot.x,Ot.y,Ot.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Ot.fromBufferAttribute(this,t),Ot.applyNormalMatrix(e),this.setXYZ(t,Ot.x,Ot.y,Ot.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Ot.fromBufferAttribute(this,t),Ot.transformDirection(e),this.setXYZ(t,Ot.x,Ot.y,Ot.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=In(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=_t(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=In(t,this.array)),t}setX(e,t){return this.normalized&&(t=_t(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=In(t,this.array)),t}setY(e,t){return this.normalized&&(t=_t(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=In(t,this.array)),t}setZ(e,t){return this.normalized&&(t=_t(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=In(t,this.array)),t}setW(e,t){return this.normalized&&(t=_t(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=_t(t,this.array),n=_t(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,s){return e*=this.itemSize,this.normalized&&(t=_t(t,this.array),n=_t(n,this.array),s=_t(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e*=this.itemSize,this.normalized&&(t=_t(t,this.array),n=_t(n,this.array),s=_t(s,this.array),r=_t(r,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=s,this.array[e+3]=r,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==Jc&&(e.usage=this.usage),e}}class Sl extends Xt{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class hf extends Xt{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class ft extends Xt{constructor(e,t,n){super(new Float32Array(e),t,n)}}let Xp=0;const yn=new De,Ca=new At,ys=new b,pn=new on,ar=new on,Vt=new b;class Ft extends $s{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:Xp++}),this.uuid=wn(),this.name="",this.type="BufferGeometry",this.index=null,this.indirect=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(of(e)?hf:Sl)(e,1):this.index=e,this}setIndirect(e){return this.indirect=e,this}getIndirect(){return this.indirect}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const r=new et().getNormalMatrix(e);n.applyNormalMatrix(r),n.needsUpdate=!0}const s=this.attributes.tangent;return s!==void 0&&(s.transformDirection(e),s.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return yn.makeRotationFromQuaternion(e),this.applyMatrix4(yn),this}rotateX(e){return yn.makeRotationX(e),this.applyMatrix4(yn),this}rotateY(e){return yn.makeRotationY(e),this.applyMatrix4(yn),this}rotateZ(e){return yn.makeRotationZ(e),this.applyMatrix4(yn),this}translate(e,t,n){return yn.makeTranslation(e,t,n),this.applyMatrix4(yn),this}scale(e,t,n){return yn.makeScale(e,t,n),this.applyMatrix4(yn),this}lookAt(e){return Ca.lookAt(e),Ca.updateMatrix(),this.applyMatrix4(Ca.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(ys).negate(),this.translate(ys.x,ys.y,ys.z),this}setFromPoints(e){const t=this.getAttribute("position");if(t===void 0){const n=[];for(let s=0,r=e.length;s<r;s++){const o=e[s];n.push(o.x,o.y,o.z||0)}this.setAttribute("position",new ft(n,3))}else{for(let n=0,s=t.count;n<s;n++){const r=e[n];t.setXYZ(n,r.x,r.y,r.z||0)}e.length>t.count&&console.warn("THREE.BufferGeometry: Buffer size too small for points data. Use .dispose() and create a new geometry."),t.needsUpdate=!0}return this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new on);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new b(-1/0,-1/0,-1/0),new b(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,s=t.length;n<s;n++){const r=t[n];pn.setFromBufferAttribute(r),this.morphTargetsRelative?(Vt.addVectors(this.boundingBox.min,pn.min),this.boundingBox.expandByPoint(Vt),Vt.addVectors(this.boundingBox.max,pn.max),this.boundingBox.expandByPoint(Vt)):(this.boundingBox.expandByPoint(pn.min),this.boundingBox.expandByPoint(pn.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new Gn);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new b,1/0);return}if(e){const n=this.boundingSphere.center;if(pn.setFromBufferAttribute(e),t)for(let r=0,o=t.length;r<o;r++){const a=t[r];ar.setFromBufferAttribute(a),this.morphTargetsRelative?(Vt.addVectors(pn.min,ar.min),pn.expandByPoint(Vt),Vt.addVectors(pn.max,ar.max),pn.expandByPoint(Vt)):(pn.expandByPoint(ar.min),pn.expandByPoint(ar.max))}pn.getCenter(n);let s=0;for(let r=0,o=e.count;r<o;r++)Vt.fromBufferAttribute(e,r),s=Math.max(s,n.distanceToSquared(Vt));if(t)for(let r=0,o=t.length;r<o;r++){const a=t[r],c=this.morphTargetsRelative;for(let l=0,u=a.count;l<u;l++)Vt.fromBufferAttribute(a,l),c&&(ys.fromBufferAttribute(e,l),Vt.add(ys)),s=Math.max(s,n.distanceToSquared(Vt))}this.boundingSphere.radius=Math.sqrt(s),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,s=t.normal,r=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new Xt(new Float32Array(4*n.count),4));const o=this.getAttribute("tangent"),a=[],c=[];for(let I=0;I<n.count;I++)a[I]=new b,c[I]=new b;const l=new b,u=new b,f=new b,h=new ie,d=new ie,m=new ie,_=new b,g=new b;function p(I,w,S){l.fromBufferAttribute(n,I),u.fromBufferAttribute(n,w),f.fromBufferAttribute(n,S),h.fromBufferAttribute(r,I),d.fromBufferAttribute(r,w),m.fromBufferAttribute(r,S),u.sub(l),f.sub(l),d.sub(h),m.sub(h);const P=1/(d.x*m.y-m.x*d.y);isFinite(P)&&(_.copy(u).multiplyScalar(m.y).addScaledVector(f,-d.y).multiplyScalar(P),g.copy(f).multiplyScalar(d.x).addScaledVector(u,-m.x).multiplyScalar(P),a[I].add(_),a[w].add(_),a[S].add(_),c[I].add(g),c[w].add(g),c[S].add(g))}let M=this.groups;M.length===0&&(M=[{start:0,count:e.count}]);for(let I=0,w=M.length;I<w;++I){const S=M[I],P=S.start,G=S.count;for(let B=P,V=P+G;B<V;B+=3)p(e.getX(B+0),e.getX(B+1),e.getX(B+2))}const v=new b,x=new b,L=new b,T=new b;function R(I){L.fromBufferAttribute(s,I),T.copy(L);const w=a[I];v.copy(w),v.sub(L.multiplyScalar(L.dot(w))).normalize(),x.crossVectors(T,w);const P=x.dot(c[I])<0?-1:1;o.setXYZW(I,v.x,v.y,v.z,P)}for(let I=0,w=M.length;I<w;++I){const S=M[I],P=S.start,G=S.count;for(let B=P,V=P+G;B<V;B+=3)R(e.getX(B+0)),R(e.getX(B+1)),R(e.getX(B+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new Xt(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let h=0,d=n.count;h<d;h++)n.setXYZ(h,0,0,0);const s=new b,r=new b,o=new b,a=new b,c=new b,l=new b,u=new b,f=new b;if(e)for(let h=0,d=e.count;h<d;h+=3){const m=e.getX(h+0),_=e.getX(h+1),g=e.getX(h+2);s.fromBufferAttribute(t,m),r.fromBufferAttribute(t,_),o.fromBufferAttribute(t,g),u.subVectors(o,r),f.subVectors(s,r),u.cross(f),a.fromBufferAttribute(n,m),c.fromBufferAttribute(n,_),l.fromBufferAttribute(n,g),a.add(u),c.add(u),l.add(u),n.setXYZ(m,a.x,a.y,a.z),n.setXYZ(_,c.x,c.y,c.z),n.setXYZ(g,l.x,l.y,l.z)}else for(let h=0,d=t.count;h<d;h+=3)s.fromBufferAttribute(t,h+0),r.fromBufferAttribute(t,h+1),o.fromBufferAttribute(t,h+2),u.subVectors(o,r),f.subVectors(s,r),u.cross(f),n.setXYZ(h+0,u.x,u.y,u.z),n.setXYZ(h+1,u.x,u.y,u.z),n.setXYZ(h+2,u.x,u.y,u.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)Vt.fromBufferAttribute(e,t),Vt.normalize(),e.setXYZ(t,Vt.x,Vt.y,Vt.z)}toNonIndexed(){function e(a,c){const l=a.array,u=a.itemSize,f=a.normalized,h=new l.constructor(c.length*u);let d=0,m=0;for(let _=0,g=c.length;_<g;_++){a.isInterleavedBufferAttribute?d=c[_]*a.data.stride+a.offset:d=c[_]*u;for(let p=0;p<u;p++)h[m++]=l[d++]}return new Xt(h,u,f)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new Ft,n=this.index.array,s=this.attributes;for(const a in s){const c=s[a],l=e(c,n);t.setAttribute(a,l)}const r=this.morphAttributes;for(const a in r){const c=[],l=r[a];for(let u=0,f=l.length;u<f;u++){const h=l[u],d=e(h,n);c.push(d)}t.morphAttributes[a]=c}t.morphTargetsRelative=this.morphTargetsRelative;const o=this.groups;for(let a=0,c=o.length;a<c;a++){const l=o[a];t.addGroup(l.start,l.count,l.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const c=this.parameters;for(const l in c)c[l]!==void 0&&(e[l]=c[l]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const c in n){const l=n[c];e.data.attributes[c]=l.toJSON(e.data)}const s={};let r=!1;for(const c in this.morphAttributes){const l=this.morphAttributes[c],u=[];for(let f=0,h=l.length;f<h;f++){const d=l[f];u.push(d.toJSON(e.data))}u.length>0&&(s[c]=u,r=!0)}r&&(e.data.morphAttributes=s,e.data.morphTargetsRelative=this.morphTargetsRelative);const o=this.groups;o.length>0&&(e.data.groups=JSON.parse(JSON.stringify(o)));const a=this.boundingSphere;return a!==null&&(e.data.boundingSphere={center:a.center.toArray(),radius:a.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const s=e.attributes;for(const l in s){const u=s[l];this.setAttribute(l,u.clone(t))}const r=e.morphAttributes;for(const l in r){const u=[],f=r[l];for(let h=0,d=f.length;h<d;h++)u.push(f[h].clone(t));this.morphAttributes[l]=u}this.morphTargetsRelative=e.morphTargetsRelative;const o=e.groups;for(let l=0,u=o.length;l<u;l++){const f=o[l];this.addGroup(f.start,f.count,f.materialIndex)}const a=e.boundingBox;a!==null&&(this.boundingBox=a.clone());const c=e.boundingSphere;return c!==null&&(this.boundingSphere=c.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const Mu=new De,Wi=new Ko,Zr=new Gn,Su=new b,Jr=new b,Qr=new b,eo=new b,Pa=new b,to=new b,Eu=new b,no=new b;class Gt extends At{constructor(e=new Ft,t=new _n){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}getVertexPosition(e,t){const n=this.geometry,s=n.attributes.position,r=n.morphAttributes.position,o=n.morphTargetsRelative;t.fromBufferAttribute(s,e);const a=this.morphTargetInfluences;if(r&&a){to.set(0,0,0);for(let c=0,l=r.length;c<l;c++){const u=a[c],f=r[c];u!==0&&(Pa.fromBufferAttribute(f,e),o?to.addScaledVector(Pa,u):to.addScaledVector(Pa.sub(t),u))}t.add(to)}return t}raycast(e,t){const n=this.geometry,s=this.material,r=this.matrixWorld;s!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),Zr.copy(n.boundingSphere),Zr.applyMatrix4(r),Wi.copy(e.ray).recast(e.near),!(Zr.containsPoint(Wi.origin)===!1&&(Wi.intersectSphere(Zr,Su)===null||Wi.origin.distanceToSquared(Su)>(e.far-e.near)**2))&&(Mu.copy(r).invert(),Wi.copy(e.ray).applyMatrix4(Mu),!(n.boundingBox!==null&&Wi.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,Wi)))}_computeIntersections(e,t,n){let s;const r=this.geometry,o=this.material,a=r.index,c=r.attributes.position,l=r.attributes.uv,u=r.attributes.uv1,f=r.attributes.normal,h=r.groups,d=r.drawRange;if(a!==null)if(Array.isArray(o))for(let m=0,_=h.length;m<_;m++){const g=h[m],p=o[g.materialIndex],M=Math.max(g.start,d.start),v=Math.min(a.count,Math.min(g.start+g.count,d.start+d.count));for(let x=M,L=v;x<L;x+=3){const T=a.getX(x),R=a.getX(x+1),I=a.getX(x+2);s=io(this,p,e,n,l,u,f,T,R,I),s&&(s.faceIndex=Math.floor(x/3),s.face.materialIndex=g.materialIndex,t.push(s))}}else{const m=Math.max(0,d.start),_=Math.min(a.count,d.start+d.count);for(let g=m,p=_;g<p;g+=3){const M=a.getX(g),v=a.getX(g+1),x=a.getX(g+2);s=io(this,o,e,n,l,u,f,M,v,x),s&&(s.faceIndex=Math.floor(g/3),t.push(s))}}else if(c!==void 0)if(Array.isArray(o))for(let m=0,_=h.length;m<_;m++){const g=h[m],p=o[g.materialIndex],M=Math.max(g.start,d.start),v=Math.min(c.count,Math.min(g.start+g.count,d.start+d.count));for(let x=M,L=v;x<L;x+=3){const T=x,R=x+1,I=x+2;s=io(this,p,e,n,l,u,f,T,R,I),s&&(s.faceIndex=Math.floor(x/3),s.face.materialIndex=g.materialIndex,t.push(s))}}else{const m=Math.max(0,d.start),_=Math.min(c.count,d.start+d.count);for(let g=m,p=_;g<p;g+=3){const M=g,v=g+1,x=g+2;s=io(this,o,e,n,l,u,f,M,v,x),s&&(s.faceIndex=Math.floor(g/3),t.push(s))}}}}function qp(i,e,t,n,s,r,o,a){let c;if(e.side===sn?c=n.intersectTriangle(o,r,s,!0,a):c=n.intersectTriangle(s,r,o,e.side===ui,a),c===null)return null;no.copy(a),no.applyMatrix4(i.matrixWorld);const l=t.ray.origin.distanceTo(no);return l<t.near||l>t.far?null:{distance:l,point:no.clone(),object:i}}function io(i,e,t,n,s,r,o,a,c,l){i.getVertexPosition(a,Jr),i.getVertexPosition(c,Qr),i.getVertexPosition(l,eo);const u=qp(i,e,t,n,Jr,Qr,eo,Eu);if(u){const f=new b;En.getBarycoord(Eu,Jr,Qr,eo,f),s&&(u.uv=En.getInterpolatedAttribute(s,a,c,l,f,new ie)),r&&(u.uv1=En.getInterpolatedAttribute(r,a,c,l,f,new ie)),o&&(u.normal=En.getInterpolatedAttribute(o,a,c,l,f,new b),u.normal.dot(n.direction)>0&&u.normal.multiplyScalar(-1));const h={a,b:c,c:l,normal:new b,materialIndex:0};En.getNormal(Jr,Qr,eo,h.normal),u.face=h,u.barycoord=f}return u}class Rt extends Ft{constructor(e=1,t=1,n=1,s=1,r=1,o=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:s,heightSegments:r,depthSegments:o};const a=this;s=Math.floor(s),r=Math.floor(r),o=Math.floor(o);const c=[],l=[],u=[],f=[];let h=0,d=0;m("z","y","x",-1,-1,n,t,e,o,r,0),m("z","y","x",1,-1,n,t,-e,o,r,1),m("x","z","y",1,1,e,n,t,s,o,2),m("x","z","y",1,-1,e,n,-t,s,o,3),m("x","y","z",1,-1,e,t,n,s,r,4),m("x","y","z",-1,-1,e,t,-n,s,r,5),this.setIndex(c),this.setAttribute("position",new ft(l,3)),this.setAttribute("normal",new ft(u,3)),this.setAttribute("uv",new ft(f,2));function m(_,g,p,M,v,x,L,T,R,I,w){const S=x/R,P=L/I,G=x/2,B=L/2,V=T/2,j=R+1,W=I+1;let ee=0,O=0;const re=new b;for(let ue=0;ue<W;ue++){const Me=ue*P-B;for(let Ye=0;Ye<j;Ye++){const dt=Ye*S-G;re[_]=dt*M,re[g]=Me*v,re[p]=V,l.push(re.x,re.y,re.z),re[_]=0,re[g]=0,re[p]=T>0?1:-1,u.push(re.x,re.y,re.z),f.push(Ye/R),f.push(1-ue/I),ee+=1}}for(let ue=0;ue<I;ue++)for(let Me=0;Me<R;Me++){const Ye=h+Me+j*ue,dt=h+Me+j*(ue+1),$=h+(Me+1)+j*(ue+1),ce=h+(Me+1)+j*ue;c.push(Ye,dt,ce),c.push(dt,$,ce),O+=6}a.addGroup(d,O,w),d+=O,h+=ee}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Rt(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function Ws(i){const e={};for(const t in i){e[t]={};for(const n in i[t]){const s=i[t][n];s&&(s.isColor||s.isMatrix3||s.isMatrix4||s.isVector2||s.isVector3||s.isVector4||s.isTexture||s.isQuaternion)?s.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=s.clone():Array.isArray(s)?e[t][n]=s.slice():e[t][n]=s}}return e}function nn(i){const e={};for(let t=0;t<i.length;t++){const n=Ws(i[t]);for(const s in n)e[s]=n[s]}return e}function Yp(i){const e=[];for(let t=0;t<i.length;t++)e.push(i[t].clone());return e}function ff(i){const e=i.getRenderTarget();return e===null?i.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:ot.workingColorSpace}const jp={clone:Ws,merge:nn};var $p=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,Kp=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class Vn extends Hn{static get type(){return"ShaderMaterial"}constructor(e){super(),this.isShaderMaterial=!0,this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=$p,this.fragmentShader=Kp,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=Ws(e.uniforms),this.uniformsGroups=Yp(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const s in this.uniforms){const o=this.uniforms[s].value;o&&o.isTexture?t.uniforms[s]={type:"t",value:o.toJSON(e).uuid}:o&&o.isColor?t.uniforms[s]={type:"c",value:o.getHex()}:o&&o.isVector2?t.uniforms[s]={type:"v2",value:o.toArray()}:o&&o.isVector3?t.uniforms[s]={type:"v3",value:o.toArray()}:o&&o.isVector4?t.uniforms[s]={type:"v4",value:o.toArray()}:o&&o.isMatrix3?t.uniforms[s]={type:"m3",value:o.toArray()}:o&&o.isMatrix4?t.uniforms[s]={type:"m4",value:o.toArray()}:t.uniforms[s]={value:o}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const s in this.extensions)this.extensions[s]===!0&&(n[s]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class df extends At{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new De,this.projectionMatrix=new De,this.projectionMatrixInverse=new De,this.coordinateSystem=ai}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const Si=new b,bu=new ie,wu=new ie;class ln extends df{constructor(e=50,t=1,n=.1,s=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=s,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=Gs*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Ds*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return Gs*2*Math.atan(Math.tan(Ds*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){Si.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set(Si.x,Si.y).multiplyScalar(-e/Si.z),Si.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set(Si.x,Si.y).multiplyScalar(-e/Si.z)}getViewSize(e,t){return this.getViewBounds(e,bu,wu),t.subVectors(wu,bu)}setViewOffset(e,t,n,s,r,o){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Ds*.5*this.fov)/this.zoom,n=2*t,s=this.aspect*n,r=-.5*s;const o=this.view;if(this.view!==null&&this.view.enabled){const c=o.fullWidth,l=o.fullHeight;r+=o.offsetX*s/c,t-=o.offsetY*n/l,s*=o.width/c,n*=o.height/l}const a=this.filmOffset;a!==0&&(r+=e*a/this.getFilmWidth()),this.projectionMatrix.makePerspective(r,r+s,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const Ms=-90,Ss=1;class Zp extends At{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const s=new ln(Ms,Ss,e,t);s.layers=this.layers,this.add(s);const r=new ln(Ms,Ss,e,t);r.layers=this.layers,this.add(r);const o=new ln(Ms,Ss,e,t);o.layers=this.layers,this.add(o);const a=new ln(Ms,Ss,e,t);a.layers=this.layers,this.add(a);const c=new ln(Ms,Ss,e,t);c.layers=this.layers,this.add(c);const l=new ln(Ms,Ss,e,t);l.layers=this.layers,this.add(l)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,s,r,o,a,c]=t;for(const l of t)this.remove(l);if(e===ai)n.up.set(0,1,0),n.lookAt(1,0,0),s.up.set(0,1,0),s.lookAt(-1,0,0),r.up.set(0,0,-1),r.lookAt(0,1,0),o.up.set(0,0,1),o.lookAt(0,-1,0),a.up.set(0,1,0),a.lookAt(0,0,1),c.up.set(0,1,0),c.lookAt(0,0,-1);else if(e===Bo)n.up.set(0,-1,0),n.lookAt(-1,0,0),s.up.set(0,-1,0),s.lookAt(1,0,0),r.up.set(0,0,1),r.lookAt(0,1,0),o.up.set(0,0,-1),o.lookAt(0,-1,0),a.up.set(0,-1,0),a.lookAt(0,0,1),c.up.set(0,-1,0),c.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const l of t)this.add(l),l.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:s}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[r,o,a,c,l,u]=this.children,f=e.getRenderTarget(),h=e.getActiveCubeFace(),d=e.getActiveMipmapLevel(),m=e.xr.enabled;e.xr.enabled=!1;const _=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,s),e.render(t,r),e.setRenderTarget(n,1,s),e.render(t,o),e.setRenderTarget(n,2,s),e.render(t,a),e.setRenderTarget(n,3,s),e.render(t,c),e.setRenderTarget(n,4,s),e.render(t,l),n.texture.generateMipmaps=_,e.setRenderTarget(n,5,s),e.render(t,u),e.setRenderTarget(f,h,d),e.xr.enabled=m,n.texture.needsPMREMUpdate=!0}}class pf extends Wt{constructor(e,t,n,s,r,o,a,c,l,u){e=e!==void 0?e:[],t=t!==void 0?t:Bs,super(e,t,n,s,r,o,a,c,l,u),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class Jp extends ts{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},s=[n,n,n,n,n,n];this.texture=new pf(s,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:gn}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

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
			`},s=new Rt(5,5,5),r=new Vn({name:"CubemapFromEquirect",uniforms:Ws(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:sn,blending:Ii});r.uniforms.tEquirect.value=t;const o=new Gt(s,r),a=t.minFilter;return t.minFilter===oi&&(t.minFilter=gn),new Zp(1,10,this).update(e,o),t.minFilter=a,o.geometry.dispose(),o.material.dispose(),this}clear(e,t,n,s){const r=e.getRenderTarget();for(let o=0;o<6;o++)e.setRenderTarget(this,o),e.clear(t,n,s);e.setRenderTarget(r)}}const La=new b,Qp=new b,em=new et;class Ki{constructor(e=new b(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,s){return this.normal.set(e,t,n),this.constant=s,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const s=La.subVectors(n,t).cross(Qp.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(s,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(La),s=this.normal.dot(n);if(s===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const r=-(e.start.dot(this.normal)+this.constant)/s;return r<0||r>1?null:t.copy(e.start).addScaledVector(n,r)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||em.getNormalMatrix(e),s=this.coplanarPoint(La).applyMatrix4(e),r=this.normal.applyMatrix3(n).normalize();return this.constant=-s.dot(r),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const Xi=new Gn,so=new b;class El{constructor(e=new Ki,t=new Ki,n=new Ki,s=new Ki,r=new Ki,o=new Ki){this.planes=[e,t,n,s,r,o]}set(e,t,n,s,r,o){const a=this.planes;return a[0].copy(e),a[1].copy(t),a[2].copy(n),a[3].copy(s),a[4].copy(r),a[5].copy(o),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=ai){const n=this.planes,s=e.elements,r=s[0],o=s[1],a=s[2],c=s[3],l=s[4],u=s[5],f=s[6],h=s[7],d=s[8],m=s[9],_=s[10],g=s[11],p=s[12],M=s[13],v=s[14],x=s[15];if(n[0].setComponents(c-r,h-l,g-d,x-p).normalize(),n[1].setComponents(c+r,h+l,g+d,x+p).normalize(),n[2].setComponents(c+o,h+u,g+m,x+M).normalize(),n[3].setComponents(c-o,h-u,g-m,x-M).normalize(),n[4].setComponents(c-a,h-f,g-_,x-v).normalize(),t===ai)n[5].setComponents(c+a,h+f,g+_,x+v).normalize();else if(t===Bo)n[5].setComponents(a,f,_,v).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),Xi.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),Xi.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(Xi)}intersectsSprite(e){return Xi.center.set(0,0,0),Xi.radius=.7071067811865476,Xi.applyMatrix4(e.matrixWorld),this.intersectsSphere(Xi)}intersectsSphere(e){const t=this.planes,n=e.center,s=-e.radius;for(let r=0;r<6;r++)if(t[r].distanceToPoint(n)<s)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const s=t[n];if(so.x=s.normal.x>0?e.max.x:e.min.x,so.y=s.normal.y>0?e.max.y:e.min.y,so.z=s.normal.z>0?e.max.z:e.min.z,s.distanceToPoint(so)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function mf(){let i=null,e=!1,t=null,n=null;function s(r,o){t(r,o),n=i.requestAnimationFrame(s)}return{start:function(){e!==!0&&t!==null&&(n=i.requestAnimationFrame(s),e=!0)},stop:function(){i.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(r){t=r},setContext:function(r){i=r}}}function tm(i){const e=new WeakMap;function t(a,c){const l=a.array,u=a.usage,f=l.byteLength,h=i.createBuffer();i.bindBuffer(c,h),i.bufferData(c,l,u),a.onUploadCallback();let d;if(l instanceof Float32Array)d=i.FLOAT;else if(l instanceof Uint16Array)a.isFloat16BufferAttribute?d=i.HALF_FLOAT:d=i.UNSIGNED_SHORT;else if(l instanceof Int16Array)d=i.SHORT;else if(l instanceof Uint32Array)d=i.UNSIGNED_INT;else if(l instanceof Int32Array)d=i.INT;else if(l instanceof Int8Array)d=i.BYTE;else if(l instanceof Uint8Array)d=i.UNSIGNED_BYTE;else if(l instanceof Uint8ClampedArray)d=i.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+l);return{buffer:h,type:d,bytesPerElement:l.BYTES_PER_ELEMENT,version:a.version,size:f}}function n(a,c,l){const u=c.array,f=c.updateRanges;if(i.bindBuffer(l,a),f.length===0)i.bufferSubData(l,0,u);else{f.sort((d,m)=>d.start-m.start);let h=0;for(let d=1;d<f.length;d++){const m=f[h],_=f[d];_.start<=m.start+m.count+1?m.count=Math.max(m.count,_.start+_.count-m.start):(++h,f[h]=_)}f.length=h+1;for(let d=0,m=f.length;d<m;d++){const _=f[d];i.bufferSubData(l,_.start*u.BYTES_PER_ELEMENT,u,_.start,_.count)}c.clearUpdateRanges()}c.onUploadCallback()}function s(a){return a.isInterleavedBufferAttribute&&(a=a.data),e.get(a)}function r(a){a.isInterleavedBufferAttribute&&(a=a.data);const c=e.get(a);c&&(i.deleteBuffer(c.buffer),e.delete(a))}function o(a,c){if(a.isInterleavedBufferAttribute&&(a=a.data),a.isGLBufferAttribute){const u=e.get(a);(!u||u.version<a.version)&&e.set(a,{buffer:a.buffer,type:a.type,bytesPerElement:a.elementSize,version:a.version});return}const l=e.get(a);if(l===void 0)e.set(a,t(a,c));else if(l.version<a.version){if(l.size!==a.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(l.buffer,a,c),l.version=a.version}}return{get:s,remove:r,update:o}}class fi extends Ft{constructor(e=1,t=1,n=1,s=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:s};const r=e/2,o=t/2,a=Math.floor(n),c=Math.floor(s),l=a+1,u=c+1,f=e/a,h=t/c,d=[],m=[],_=[],g=[];for(let p=0;p<u;p++){const M=p*h-o;for(let v=0;v<l;v++){const x=v*f-r;m.push(x,-M,0),_.push(0,0,1),g.push(v/a),g.push(1-p/c)}}for(let p=0;p<c;p++)for(let M=0;M<a;M++){const v=M+l*p,x=M+l*(p+1),L=M+1+l*(p+1),T=M+1+l*p;d.push(v,x,T),d.push(x,L,T)}this.setIndex(d),this.setAttribute("position",new ft(m,3)),this.setAttribute("normal",new ft(_,3)),this.setAttribute("uv",new ft(g,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new fi(e.width,e.height,e.widthSegments,e.heightSegments)}}var nm=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,im=`#ifdef USE_ALPHAHASH
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
#endif`,sm=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,rm=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,om=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,am=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,cm=`#ifdef USE_AOMAP
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
#endif`,lm=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,um=`#ifdef USE_BATCHING
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
#endif`,hm=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,fm=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,dm=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,pm=`float G_BlinnPhong_Implicit( ) {
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
} // validated`,mm=`#ifdef USE_IRIDESCENCE
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
#endif`,gm=`#ifdef USE_BUMPMAP
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
#endif`,_m=`#if NUM_CLIPPING_PLANES > 0
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
#endif`,xm=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,vm=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,ym=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,Mm=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,Sm=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,Em=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,bm=`#if defined( USE_COLOR_ALPHA )
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
#endif`,wm=`#define PI 3.141592653589793
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
} // validated`,Tm=`#ifdef ENVMAP_TYPE_CUBE_UV
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
#endif`,Am=`vec3 transformedNormal = objectNormal;
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
#endif`,Rm=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,Cm=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,Pm=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	#ifdef DECODE_VIDEO_TEXTURE_EMISSIVE
		emissiveColor = sRGBTransferEOTF( emissiveColor );
	#endif
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,Lm=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,Im="gl_FragColor = linearToOutputTexel( gl_FragColor );",Dm=`vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferEOTF( in vec4 value ) {
	return vec4( mix( pow( value.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), value.rgb * 0.0773993808, vec3( lessThanEqual( value.rgb, vec3( 0.04045 ) ) ) ), value.a );
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,Nm=`#ifdef USE_ENVMAP
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
#endif`,Um=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,Om=`#ifdef USE_ENVMAP
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
#endif`,Fm=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,Bm=`#ifdef USE_ENVMAP
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
#endif`,km=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,zm=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,Hm=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,Vm=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,Gm=`#ifdef USE_GRADIENTMAP
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
}`,Wm=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,Xm=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,qm=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,Ym=`uniform bool receiveShadow;
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
#endif`,jm=`#ifdef USE_ENVMAP
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
#endif`,$m=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,Km=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,Zm=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,Jm=`varying vec3 vViewPosition;
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
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,Qm=`PhysicalMaterial material;
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
#endif`,eg=`struct PhysicalMaterial {
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
}`,tg=`
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
#endif`,ng=`#if defined( RE_IndirectDiffuse )
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
#endif`,ig=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,sg=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,rg=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,og=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,ag=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,cg=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = sRGBTransferEOTF( sampledDiffuseColor );
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,lg=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,ug=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
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
#endif`,hg=`#if defined( USE_POINTS_UV )
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
#endif`,fg=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,dg=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,pg=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,mg=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,gg=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,_g=`#ifdef USE_MORPHTARGETS
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
#endif`,xg=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,vg=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
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
vec3 nonPerturbedNormal = normal;`,yg=`#ifdef USE_NORMALMAP_OBJECTSPACE
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
#endif`,Mg=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,Sg=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,Eg=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,bg=`#ifdef USE_NORMALMAP
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
#endif`,wg=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,Tg=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,Ag=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,Rg=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,Cg=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,Pg=`vec3 packNormalToRGB( const in vec3 normal ) {
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
}`,Lg=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,Ig=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,Dg=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,Ng=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,Ug=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,Og=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,Fg=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,Bg=`#if NUM_SPOT_LIGHT_COORDS > 0
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
#endif`,kg=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
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
#endif`,zg=`float getShadowMask() {
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
}`,Hg=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,Vg=`#ifdef USE_SKINNING
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
#endif`,Gg=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,Wg=`#ifdef USE_SKINNING
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
#endif`,Xg=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,qg=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,Yg=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,jg=`#ifndef saturate
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
vec3 CustomToneMapping( vec3 color ) { return color; }`,$g=`#ifdef USE_TRANSMISSION
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
#endif`,Kg=`#ifdef USE_TRANSMISSION
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
#endif`,Zg=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Jg=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,Qg=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
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
#endif`,e0=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const t0=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,n0=`uniform sampler2D t2D;
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
}`,i0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,s0=`#ifdef ENVMAP_TYPE_CUBE
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
}`,r0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,o0=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,a0=`#include <common>
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
}`,c0=`#if DEPTH_PACKING == 3200
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
}`,l0=`#define DISTANCE
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
}`,u0=`#define DISTANCE
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
}`,h0=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,f0=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,d0=`uniform float scale;
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
}`,p0=`uniform vec3 diffuse;
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
}`,m0=`#include <common>
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
}`,g0=`uniform vec3 diffuse;
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
}`,_0=`#define LAMBERT
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
}`,x0=`#define LAMBERT
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
}`,v0=`#define MATCAP
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
}`,y0=`#define MATCAP
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
}`,M0=`#define NORMAL
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
}`,S0=`#define NORMAL
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
}`,E0=`#define PHONG
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
}`,b0=`#define PHONG
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
}`,w0=`#define STANDARD
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
}`,T0=`#define STANDARD
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
}`,A0=`#define TOON
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
}`,R0=`#define TOON
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
}`,C0=`uniform float size;
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
}`,P0=`uniform vec3 diffuse;
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
}`,L0=`#include <common>
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
}`,I0=`uniform vec3 color;
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
}`,D0=`uniform float rotation;
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
}`,N0=`uniform vec3 diffuse;
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
}`,nt={alphahash_fragment:nm,alphahash_pars_fragment:im,alphamap_fragment:sm,alphamap_pars_fragment:rm,alphatest_fragment:om,alphatest_pars_fragment:am,aomap_fragment:cm,aomap_pars_fragment:lm,batching_pars_vertex:um,batching_vertex:hm,begin_vertex:fm,beginnormal_vertex:dm,bsdfs:pm,iridescence_fragment:mm,bumpmap_pars_fragment:gm,clipping_planes_fragment:_m,clipping_planes_pars_fragment:xm,clipping_planes_pars_vertex:vm,clipping_planes_vertex:ym,color_fragment:Mm,color_pars_fragment:Sm,color_pars_vertex:Em,color_vertex:bm,common:wm,cube_uv_reflection_fragment:Tm,defaultnormal_vertex:Am,displacementmap_pars_vertex:Rm,displacementmap_vertex:Cm,emissivemap_fragment:Pm,emissivemap_pars_fragment:Lm,colorspace_fragment:Im,colorspace_pars_fragment:Dm,envmap_fragment:Nm,envmap_common_pars_fragment:Um,envmap_pars_fragment:Om,envmap_pars_vertex:Fm,envmap_physical_pars_fragment:jm,envmap_vertex:Bm,fog_vertex:km,fog_pars_vertex:zm,fog_fragment:Hm,fog_pars_fragment:Vm,gradientmap_pars_fragment:Gm,lightmap_pars_fragment:Wm,lights_lambert_fragment:Xm,lights_lambert_pars_fragment:qm,lights_pars_begin:Ym,lights_toon_fragment:$m,lights_toon_pars_fragment:Km,lights_phong_fragment:Zm,lights_phong_pars_fragment:Jm,lights_physical_fragment:Qm,lights_physical_pars_fragment:eg,lights_fragment_begin:tg,lights_fragment_maps:ng,lights_fragment_end:ig,logdepthbuf_fragment:sg,logdepthbuf_pars_fragment:rg,logdepthbuf_pars_vertex:og,logdepthbuf_vertex:ag,map_fragment:cg,map_pars_fragment:lg,map_particle_fragment:ug,map_particle_pars_fragment:hg,metalnessmap_fragment:fg,metalnessmap_pars_fragment:dg,morphinstance_vertex:pg,morphcolor_vertex:mg,morphnormal_vertex:gg,morphtarget_pars_vertex:_g,morphtarget_vertex:xg,normal_fragment_begin:vg,normal_fragment_maps:yg,normal_pars_fragment:Mg,normal_pars_vertex:Sg,normal_vertex:Eg,normalmap_pars_fragment:bg,clearcoat_normal_fragment_begin:wg,clearcoat_normal_fragment_maps:Tg,clearcoat_pars_fragment:Ag,iridescence_pars_fragment:Rg,opaque_fragment:Cg,packing:Pg,premultiplied_alpha_fragment:Lg,project_vertex:Ig,dithering_fragment:Dg,dithering_pars_fragment:Ng,roughnessmap_fragment:Ug,roughnessmap_pars_fragment:Og,shadowmap_pars_fragment:Fg,shadowmap_pars_vertex:Bg,shadowmap_vertex:kg,shadowmask_pars_fragment:zg,skinbase_vertex:Hg,skinning_pars_vertex:Vg,skinning_vertex:Gg,skinnormal_vertex:Wg,specularmap_fragment:Xg,specularmap_pars_fragment:qg,tonemapping_fragment:Yg,tonemapping_pars_fragment:jg,transmission_fragment:$g,transmission_pars_fragment:Kg,uv_pars_fragment:Zg,uv_pars_vertex:Jg,uv_vertex:Qg,worldpos_vertex:e0,background_vert:t0,background_frag:n0,backgroundCube_vert:i0,backgroundCube_frag:s0,cube_vert:r0,cube_frag:o0,depth_vert:a0,depth_frag:c0,distanceRGBA_vert:l0,distanceRGBA_frag:u0,equirect_vert:h0,equirect_frag:f0,linedashed_vert:d0,linedashed_frag:p0,meshbasic_vert:m0,meshbasic_frag:g0,meshlambert_vert:_0,meshlambert_frag:x0,meshmatcap_vert:v0,meshmatcap_frag:y0,meshnormal_vert:M0,meshnormal_frag:S0,meshphong_vert:E0,meshphong_frag:b0,meshphysical_vert:w0,meshphysical_frag:T0,meshtoon_vert:A0,meshtoon_frag:R0,points_vert:C0,points_frag:P0,shadow_vert:L0,shadow_frag:I0,sprite_vert:D0,sprite_frag:N0},me={common:{diffuse:{value:new Ve(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new et},alphaMap:{value:null},alphaMapTransform:{value:new et},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new et}},envmap:{envMap:{value:null},envMapRotation:{value:new et},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new et}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new et}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new et},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new et},normalScale:{value:new ie(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new et},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new et}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new et}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new et}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new Ve(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new Ve(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new et},alphaTest:{value:0},uvTransform:{value:new et}},sprite:{diffuse:{value:new Ve(16777215)},opacity:{value:1},center:{value:new ie(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new et},alphaMap:{value:null},alphaMapTransform:{value:new et},alphaTest:{value:0}}},kn={basic:{uniforms:nn([me.common,me.specularmap,me.envmap,me.aomap,me.lightmap,me.fog]),vertexShader:nt.meshbasic_vert,fragmentShader:nt.meshbasic_frag},lambert:{uniforms:nn([me.common,me.specularmap,me.envmap,me.aomap,me.lightmap,me.emissivemap,me.bumpmap,me.normalmap,me.displacementmap,me.fog,me.lights,{emissive:{value:new Ve(0)}}]),vertexShader:nt.meshlambert_vert,fragmentShader:nt.meshlambert_frag},phong:{uniforms:nn([me.common,me.specularmap,me.envmap,me.aomap,me.lightmap,me.emissivemap,me.bumpmap,me.normalmap,me.displacementmap,me.fog,me.lights,{emissive:{value:new Ve(0)},specular:{value:new Ve(1118481)},shininess:{value:30}}]),vertexShader:nt.meshphong_vert,fragmentShader:nt.meshphong_frag},standard:{uniforms:nn([me.common,me.envmap,me.aomap,me.lightmap,me.emissivemap,me.bumpmap,me.normalmap,me.displacementmap,me.roughnessmap,me.metalnessmap,me.fog,me.lights,{emissive:{value:new Ve(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:nt.meshphysical_vert,fragmentShader:nt.meshphysical_frag},toon:{uniforms:nn([me.common,me.aomap,me.lightmap,me.emissivemap,me.bumpmap,me.normalmap,me.displacementmap,me.gradientmap,me.fog,me.lights,{emissive:{value:new Ve(0)}}]),vertexShader:nt.meshtoon_vert,fragmentShader:nt.meshtoon_frag},matcap:{uniforms:nn([me.common,me.bumpmap,me.normalmap,me.displacementmap,me.fog,{matcap:{value:null}}]),vertexShader:nt.meshmatcap_vert,fragmentShader:nt.meshmatcap_frag},points:{uniforms:nn([me.points,me.fog]),vertexShader:nt.points_vert,fragmentShader:nt.points_frag},dashed:{uniforms:nn([me.common,me.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:nt.linedashed_vert,fragmentShader:nt.linedashed_frag},depth:{uniforms:nn([me.common,me.displacementmap]),vertexShader:nt.depth_vert,fragmentShader:nt.depth_frag},normal:{uniforms:nn([me.common,me.bumpmap,me.normalmap,me.displacementmap,{opacity:{value:1}}]),vertexShader:nt.meshnormal_vert,fragmentShader:nt.meshnormal_frag},sprite:{uniforms:nn([me.sprite,me.fog]),vertexShader:nt.sprite_vert,fragmentShader:nt.sprite_frag},background:{uniforms:{uvTransform:{value:new et},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:nt.background_vert,fragmentShader:nt.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new et}},vertexShader:nt.backgroundCube_vert,fragmentShader:nt.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:nt.cube_vert,fragmentShader:nt.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:nt.equirect_vert,fragmentShader:nt.equirect_frag},distanceRGBA:{uniforms:nn([me.common,me.displacementmap,{referencePosition:{value:new b},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:nt.distanceRGBA_vert,fragmentShader:nt.distanceRGBA_frag},shadow:{uniforms:nn([me.lights,me.fog,{color:{value:new Ve(0)},opacity:{value:1}}]),vertexShader:nt.shadow_vert,fragmentShader:nt.shadow_frag}};kn.physical={uniforms:nn([kn.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new et},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new et},clearcoatNormalScale:{value:new ie(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new et},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new et},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new et},sheen:{value:0},sheenColor:{value:new Ve(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new et},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new et},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new et},transmissionSamplerSize:{value:new ie},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new et},attenuationDistance:{value:0},attenuationColor:{value:new Ve(0)},specularColor:{value:new Ve(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new et},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new et},anisotropyVector:{value:new ie},anisotropyMap:{value:null},anisotropyMapTransform:{value:new et}}]),vertexShader:nt.meshphysical_vert,fragmentShader:nt.meshphysical_frag};const ro={r:0,b:0,g:0},qi=new Un,U0=new De;function O0(i,e,t,n,s,r,o){const a=new Ve(0);let c=r===!0?0:1,l,u,f=null,h=0,d=null;function m(M){let v=M.isScene===!0?M.background:null;return v&&v.isTexture&&(v=(M.backgroundBlurriness>0?t:e).get(v)),v}function _(M){let v=!1;const x=m(M);x===null?p(a,c):x&&x.isColor&&(p(x,1),v=!0);const L=i.xr.getEnvironmentBlendMode();L==="additive"?n.buffers.color.setClear(0,0,0,1,o):L==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,o),(i.autoClear||v)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),i.clear(i.autoClearColor,i.autoClearDepth,i.autoClearStencil))}function g(M,v){const x=m(v);x&&(x.isCubeTexture||x.mapping===jo)?(u===void 0&&(u=new Gt(new Rt(1,1,1),new Vn({name:"BackgroundCubeMaterial",uniforms:Ws(kn.backgroundCube.uniforms),vertexShader:kn.backgroundCube.vertexShader,fragmentShader:kn.backgroundCube.fragmentShader,side:sn,depthTest:!1,depthWrite:!1,fog:!1})),u.geometry.deleteAttribute("normal"),u.geometry.deleteAttribute("uv"),u.onBeforeRender=function(L,T,R){this.matrixWorld.copyPosition(R.matrixWorld)},Object.defineProperty(u.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),s.update(u)),qi.copy(v.backgroundRotation),qi.x*=-1,qi.y*=-1,qi.z*=-1,x.isCubeTexture&&x.isRenderTargetTexture===!1&&(qi.y*=-1,qi.z*=-1),u.material.uniforms.envMap.value=x,u.material.uniforms.flipEnvMap.value=x.isCubeTexture&&x.isRenderTargetTexture===!1?-1:1,u.material.uniforms.backgroundBlurriness.value=v.backgroundBlurriness,u.material.uniforms.backgroundIntensity.value=v.backgroundIntensity,u.material.uniforms.backgroundRotation.value.setFromMatrix4(U0.makeRotationFromEuler(qi)),u.material.toneMapped=ot.getTransfer(x.colorSpace)!==yt,(f!==x||h!==x.version||d!==i.toneMapping)&&(u.material.needsUpdate=!0,f=x,h=x.version,d=i.toneMapping),u.layers.enableAll(),M.unshift(u,u.geometry,u.material,0,0,null)):x&&x.isTexture&&(l===void 0&&(l=new Gt(new fi(2,2),new Vn({name:"BackgroundMaterial",uniforms:Ws(kn.background.uniforms),vertexShader:kn.background.vertexShader,fragmentShader:kn.background.fragmentShader,side:ui,depthTest:!1,depthWrite:!1,fog:!1})),l.geometry.deleteAttribute("normal"),Object.defineProperty(l.material,"map",{get:function(){return this.uniforms.t2D.value}}),s.update(l)),l.material.uniforms.t2D.value=x,l.material.uniforms.backgroundIntensity.value=v.backgroundIntensity,l.material.toneMapped=ot.getTransfer(x.colorSpace)!==yt,x.matrixAutoUpdate===!0&&x.updateMatrix(),l.material.uniforms.uvTransform.value.copy(x.matrix),(f!==x||h!==x.version||d!==i.toneMapping)&&(l.material.needsUpdate=!0,f=x,h=x.version,d=i.toneMapping),l.layers.enableAll(),M.unshift(l,l.geometry,l.material,0,0,null))}function p(M,v){M.getRGB(ro,ff(i)),n.buffers.color.setClear(ro.r,ro.g,ro.b,v,o)}return{getClearColor:function(){return a},setClearColor:function(M,v=1){a.set(M),c=v,p(a,c)},getClearAlpha:function(){return c},setClearAlpha:function(M){c=M,p(a,c)},render:_,addToRenderList:g}}function F0(i,e){const t=i.getParameter(i.MAX_VERTEX_ATTRIBS),n={},s=h(null);let r=s,o=!1;function a(S,P,G,B,V){let j=!1;const W=f(B,G,P);r!==W&&(r=W,l(r.object)),j=d(S,B,G,V),j&&m(S,B,G,V),V!==null&&e.update(V,i.ELEMENT_ARRAY_BUFFER),(j||o)&&(o=!1,x(S,P,G,B),V!==null&&i.bindBuffer(i.ELEMENT_ARRAY_BUFFER,e.get(V).buffer))}function c(){return i.createVertexArray()}function l(S){return i.bindVertexArray(S)}function u(S){return i.deleteVertexArray(S)}function f(S,P,G){const B=G.wireframe===!0;let V=n[S.id];V===void 0&&(V={},n[S.id]=V);let j=V[P.id];j===void 0&&(j={},V[P.id]=j);let W=j[B];return W===void 0&&(W=h(c()),j[B]=W),W}function h(S){const P=[],G=[],B=[];for(let V=0;V<t;V++)P[V]=0,G[V]=0,B[V]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:P,enabledAttributes:G,attributeDivisors:B,object:S,attributes:{},index:null}}function d(S,P,G,B){const V=r.attributes,j=P.attributes;let W=0;const ee=G.getAttributes();for(const O in ee)if(ee[O].location>=0){const ue=V[O];let Me=j[O];if(Me===void 0&&(O==="instanceMatrix"&&S.instanceMatrix&&(Me=S.instanceMatrix),O==="instanceColor"&&S.instanceColor&&(Me=S.instanceColor)),ue===void 0||ue.attribute!==Me||Me&&ue.data!==Me.data)return!0;W++}return r.attributesNum!==W||r.index!==B}function m(S,P,G,B){const V={},j=P.attributes;let W=0;const ee=G.getAttributes();for(const O in ee)if(ee[O].location>=0){let ue=j[O];ue===void 0&&(O==="instanceMatrix"&&S.instanceMatrix&&(ue=S.instanceMatrix),O==="instanceColor"&&S.instanceColor&&(ue=S.instanceColor));const Me={};Me.attribute=ue,ue&&ue.data&&(Me.data=ue.data),V[O]=Me,W++}r.attributes=V,r.attributesNum=W,r.index=B}function _(){const S=r.newAttributes;for(let P=0,G=S.length;P<G;P++)S[P]=0}function g(S){p(S,0)}function p(S,P){const G=r.newAttributes,B=r.enabledAttributes,V=r.attributeDivisors;G[S]=1,B[S]===0&&(i.enableVertexAttribArray(S),B[S]=1),V[S]!==P&&(i.vertexAttribDivisor(S,P),V[S]=P)}function M(){const S=r.newAttributes,P=r.enabledAttributes;for(let G=0,B=P.length;G<B;G++)P[G]!==S[G]&&(i.disableVertexAttribArray(G),P[G]=0)}function v(S,P,G,B,V,j,W){W===!0?i.vertexAttribIPointer(S,P,G,V,j):i.vertexAttribPointer(S,P,G,B,V,j)}function x(S,P,G,B){_();const V=B.attributes,j=G.getAttributes(),W=P.defaultAttributeValues;for(const ee in j){const O=j[ee];if(O.location>=0){let re=V[ee];if(re===void 0&&(ee==="instanceMatrix"&&S.instanceMatrix&&(re=S.instanceMatrix),ee==="instanceColor"&&S.instanceColor&&(re=S.instanceColor)),re!==void 0){const ue=re.normalized,Me=re.itemSize,Ye=e.get(re);if(Ye===void 0)continue;const dt=Ye.buffer,$=Ye.type,ce=Ye.bytesPerElement,Pe=$===i.INT||$===i.UNSIGNED_INT||re.gpuType===pl;if(re.isInterleavedBufferAttribute){const fe=re.data,ze=fe.stride,$e=re.offset;if(fe.isInstancedInterleavedBuffer){for(let qe=0;qe<O.locationSize;qe++)p(O.location+qe,fe.meshPerAttribute);S.isInstancedMesh!==!0&&B._maxInstanceCount===void 0&&(B._maxInstanceCount=fe.meshPerAttribute*fe.count)}else for(let qe=0;qe<O.locationSize;qe++)g(O.location+qe);i.bindBuffer(i.ARRAY_BUFFER,dt);for(let qe=0;qe<O.locationSize;qe++)v(O.location+qe,Me/O.locationSize,$,ue,ze*ce,($e+Me/O.locationSize*qe)*ce,Pe)}else{if(re.isInstancedBufferAttribute){for(let fe=0;fe<O.locationSize;fe++)p(O.location+fe,re.meshPerAttribute);S.isInstancedMesh!==!0&&B._maxInstanceCount===void 0&&(B._maxInstanceCount=re.meshPerAttribute*re.count)}else for(let fe=0;fe<O.locationSize;fe++)g(O.location+fe);i.bindBuffer(i.ARRAY_BUFFER,dt);for(let fe=0;fe<O.locationSize;fe++)v(O.location+fe,Me/O.locationSize,$,ue,Me*ce,Me/O.locationSize*fe*ce,Pe)}}else if(W!==void 0){const ue=W[ee];if(ue!==void 0)switch(ue.length){case 2:i.vertexAttrib2fv(O.location,ue);break;case 3:i.vertexAttrib3fv(O.location,ue);break;case 4:i.vertexAttrib4fv(O.location,ue);break;default:i.vertexAttrib1fv(O.location,ue)}}}}M()}function L(){I();for(const S in n){const P=n[S];for(const G in P){const B=P[G];for(const V in B)u(B[V].object),delete B[V];delete P[G]}delete n[S]}}function T(S){if(n[S.id]===void 0)return;const P=n[S.id];for(const G in P){const B=P[G];for(const V in B)u(B[V].object),delete B[V];delete P[G]}delete n[S.id]}function R(S){for(const P in n){const G=n[P];if(G[S.id]===void 0)continue;const B=G[S.id];for(const V in B)u(B[V].object),delete B[V];delete G[S.id]}}function I(){w(),o=!0,r!==s&&(r=s,l(r.object))}function w(){s.geometry=null,s.program=null,s.wireframe=!1}return{setup:a,reset:I,resetDefaultState:w,dispose:L,releaseStatesOfGeometry:T,releaseStatesOfProgram:R,initAttributes:_,enableAttribute:g,disableUnusedAttributes:M}}function B0(i,e,t){let n;function s(l){n=l}function r(l,u){i.drawArrays(n,l,u),t.update(u,n,1)}function o(l,u,f){f!==0&&(i.drawArraysInstanced(n,l,u,f),t.update(u,n,f))}function a(l,u,f){if(f===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,l,0,u,0,f);let d=0;for(let m=0;m<f;m++)d+=u[m];t.update(d,n,1)}function c(l,u,f,h){if(f===0)return;const d=e.get("WEBGL_multi_draw");if(d===null)for(let m=0;m<l.length;m++)o(l[m],u[m],h[m]);else{d.multiDrawArraysInstancedWEBGL(n,l,0,u,0,h,0,f);let m=0;for(let _=0;_<f;_++)m+=u[_]*h[_];t.update(m,n,1)}}this.setMode=s,this.render=r,this.renderInstances=o,this.renderMultiDraw=a,this.renderMultiDrawInstances=c}function k0(i,e,t,n){let s;function r(){if(s!==void 0)return s;if(e.has("EXT_texture_filter_anisotropic")===!0){const R=e.get("EXT_texture_filter_anisotropic");s=i.getParameter(R.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else s=0;return s}function o(R){return!(R!==bn&&n.convert(R)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_FORMAT))}function a(R){const I=R===Dr&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(R!==hi&&n.convert(R)!==i.getParameter(i.IMPLEMENTATION_COLOR_READ_TYPE)&&R!==Dn&&!I)}function c(R){if(R==="highp"){if(i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.HIGH_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.HIGH_FLOAT).precision>0)return"highp";R="mediump"}return R==="mediump"&&i.getShaderPrecisionFormat(i.VERTEX_SHADER,i.MEDIUM_FLOAT).precision>0&&i.getShaderPrecisionFormat(i.FRAGMENT_SHADER,i.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let l=t.precision!==void 0?t.precision:"highp";const u=c(l);u!==l&&(console.warn("THREE.WebGLRenderer:",l,"not supported, using",u,"instead."),l=u);const f=t.logarithmicDepthBuffer===!0,h=t.reverseDepthBuffer===!0&&e.has("EXT_clip_control"),d=i.getParameter(i.MAX_TEXTURE_IMAGE_UNITS),m=i.getParameter(i.MAX_VERTEX_TEXTURE_IMAGE_UNITS),_=i.getParameter(i.MAX_TEXTURE_SIZE),g=i.getParameter(i.MAX_CUBE_MAP_TEXTURE_SIZE),p=i.getParameter(i.MAX_VERTEX_ATTRIBS),M=i.getParameter(i.MAX_VERTEX_UNIFORM_VECTORS),v=i.getParameter(i.MAX_VARYING_VECTORS),x=i.getParameter(i.MAX_FRAGMENT_UNIFORM_VECTORS),L=m>0,T=i.getParameter(i.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:r,getMaxPrecision:c,textureFormatReadable:o,textureTypeReadable:a,precision:l,logarithmicDepthBuffer:f,reverseDepthBuffer:h,maxTextures:d,maxVertexTextures:m,maxTextureSize:_,maxCubemapSize:g,maxAttributes:p,maxVertexUniforms:M,maxVaryings:v,maxFragmentUniforms:x,vertexTextures:L,maxSamples:T}}function z0(i){const e=this;let t=null,n=0,s=!1,r=!1;const o=new Ki,a=new et,c={value:null,needsUpdate:!1};this.uniform=c,this.numPlanes=0,this.numIntersection=0,this.init=function(f,h){const d=f.length!==0||h||n!==0||s;return s=h,n=f.length,d},this.beginShadows=function(){r=!0,u(null)},this.endShadows=function(){r=!1},this.setGlobalState=function(f,h){t=u(f,h,0)},this.setState=function(f,h,d){const m=f.clippingPlanes,_=f.clipIntersection,g=f.clipShadows,p=i.get(f);if(!s||m===null||m.length===0||r&&!g)r?u(null):l();else{const M=r?0:n,v=M*4;let x=p.clippingState||null;c.value=x,x=u(m,h,v,d);for(let L=0;L!==v;++L)x[L]=t[L];p.clippingState=x,this.numIntersection=_?this.numPlanes:0,this.numPlanes+=M}};function l(){c.value!==t&&(c.value=t,c.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function u(f,h,d,m){const _=f!==null?f.length:0;let g=null;if(_!==0){if(g=c.value,m!==!0||g===null){const p=d+_*4,M=h.matrixWorldInverse;a.getNormalMatrix(M),(g===null||g.length<p)&&(g=new Float32Array(p));for(let v=0,x=d;v!==_;++v,x+=4)o.copy(f[v]).applyMatrix4(M,a),o.normal.toArray(g,x),g[x+3]=o.constant}c.value=g,c.needsUpdate=!0}return e.numPlanes=_,e.numIntersection=0,g}}function H0(i){let e=new WeakMap;function t(o,a){return a===Ec?o.mapping=Bs:a===bc&&(o.mapping=ks),o}function n(o){if(o&&o.isTexture){const a=o.mapping;if(a===Ec||a===bc)if(e.has(o)){const c=e.get(o).texture;return t(c,o.mapping)}else{const c=o.image;if(c&&c.height>0){const l=new Jp(c.height);return l.fromEquirectangularTexture(i,o),e.set(o,l),o.addEventListener("dispose",s),t(l.texture,o.mapping)}else return null}}return o}function s(o){const a=o.target;a.removeEventListener("dispose",s);const c=e.get(a);c!==void 0&&(e.delete(a),c.dispose())}function r(){e=new WeakMap}return{get:n,dispose:r}}class Zo extends df{constructor(e=-1,t=1,n=1,s=-1,r=.1,o=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=s,this.near=r,this.far=o,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,s,r,o){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=s,this.view.width=r,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,s=(this.top+this.bottom)/2;let r=n-e,o=n+e,a=s+t,c=s-t;if(this.view!==null&&this.view.enabled){const l=(this.right-this.left)/this.view.fullWidth/this.zoom,u=(this.top-this.bottom)/this.view.fullHeight/this.zoom;r+=l*this.view.offsetX,o=r+l*this.view.width,a-=u*this.view.offsetY,c=a-u*this.view.height}this.projectionMatrix.makeOrthographic(r,o,a,c,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const Rs=4,Tu=[.125,.215,.35,.446,.526,.582],Qi=20,Ia=new Zo,Au=new Ve;let Da=null,Na=0,Ua=0,Oa=!1;const Zi=(1+Math.sqrt(5))/2,Es=1/Zi,Ru=[new b(-Zi,Es,0),new b(Zi,Es,0),new b(-Es,0,Zi),new b(Es,0,Zi),new b(0,Zi,-Es),new b(0,Zi,Es),new b(-1,1,-1),new b(1,1,-1),new b(-1,1,1),new b(1,1,1)];class Cu{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,s=100){Da=this._renderer.getRenderTarget(),Na=this._renderer.getActiveCubeFace(),Ua=this._renderer.getActiveMipmapLevel(),Oa=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const r=this._allocateTargets();return r.depthBuffer=!0,this._sceneToCubeUV(e,n,s,r),t>0&&this._blur(r,0,0,t),this._applyPMREM(r),this._cleanup(r),r}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=Iu(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=Lu(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(Da,Na,Ua),this._renderer.xr.enabled=Oa,e.scissorTest=!1,oo(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Bs||e.mapping===ks?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),Da=this._renderer.getRenderTarget(),Na=this._renderer.getActiveCubeFace(),Ua=this._renderer.getActiveMipmapLevel(),Oa=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:gn,minFilter:gn,generateMipmaps:!1,type:Dr,format:bn,colorSpace:en,depthBuffer:!1},s=Pu(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=Pu(e,t,n);const{_lodMax:r}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=V0(r)),this._blurMaterial=G0(r,e,t)}return s}_compileMaterial(e){const t=new Gt(this._lodPlanes[0],e);this._renderer.compile(t,Ia)}_sceneToCubeUV(e,t,n,s){const a=new ln(90,1,t,n),c=[1,-1,1,1,1,1],l=[1,1,1,-1,-1,-1],u=this._renderer,f=u.autoClear,h=u.toneMapping;u.getClearColor(Au),u.toneMapping=Di,u.autoClear=!1;const d=new _n({name:"PMREM.Background",side:sn,depthWrite:!1,depthTest:!1}),m=new Gt(new Rt,d);let _=!1;const g=e.background;g?g.isColor&&(d.color.copy(g),e.background=null,_=!0):(d.color.copy(Au),_=!0);for(let p=0;p<6;p++){const M=p%3;M===0?(a.up.set(0,c[p],0),a.lookAt(l[p],0,0)):M===1?(a.up.set(0,0,c[p]),a.lookAt(0,l[p],0)):(a.up.set(0,c[p],0),a.lookAt(0,0,l[p]));const v=this._cubeSize;oo(s,M*v,p>2?v:0,v,v),u.setRenderTarget(s),_&&u.render(m,a),u.render(e,a)}m.geometry.dispose(),m.material.dispose(),u.toneMapping=h,u.autoClear=f,e.background=g}_textureToCubeUV(e,t){const n=this._renderer,s=e.mapping===Bs||e.mapping===ks;s?(this._cubemapMaterial===null&&(this._cubemapMaterial=Iu()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=Lu());const r=s?this._cubemapMaterial:this._equirectMaterial,o=new Gt(this._lodPlanes[0],r),a=r.uniforms;a.envMap.value=e;const c=this._cubeSize;oo(t,0,0,3*c,2*c),n.setRenderTarget(t),n.render(o,Ia)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const s=this._lodPlanes.length;for(let r=1;r<s;r++){const o=Math.sqrt(this._sigmas[r]*this._sigmas[r]-this._sigmas[r-1]*this._sigmas[r-1]),a=Ru[(s-r-1)%Ru.length];this._blur(e,r-1,r,o,a)}t.autoClear=n}_blur(e,t,n,s,r){const o=this._pingPongRenderTarget;this._halfBlur(e,o,t,n,s,"latitudinal",r),this._halfBlur(o,e,n,n,s,"longitudinal",r)}_halfBlur(e,t,n,s,r,o,a){const c=this._renderer,l=this._blurMaterial;o!=="latitudinal"&&o!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const u=3,f=new Gt(this._lodPlanes[s],l),h=l.uniforms,d=this._sizeLods[n]-1,m=isFinite(r)?Math.PI/(2*d):2*Math.PI/(2*Qi-1),_=r/m,g=isFinite(r)?1+Math.floor(u*_):Qi;g>Qi&&console.warn(`sigmaRadians, ${r}, is too large and will clip, as it requested ${g} samples when the maximum is set to ${Qi}`);const p=[];let M=0;for(let R=0;R<Qi;++R){const I=R/_,w=Math.exp(-I*I/2);p.push(w),R===0?M+=w:R<g&&(M+=2*w)}for(let R=0;R<p.length;R++)p[R]=p[R]/M;h.envMap.value=e.texture,h.samples.value=g,h.weights.value=p,h.latitudinal.value=o==="latitudinal",a&&(h.poleAxis.value=a);const{_lodMax:v}=this;h.dTheta.value=m,h.mipInt.value=v-n;const x=this._sizeLods[s],L=3*x*(s>v-Rs?s-v+Rs:0),T=4*(this._cubeSize-x);oo(t,L,T,3*x,2*x),c.setRenderTarget(t),c.render(f,Ia)}}function V0(i){const e=[],t=[],n=[];let s=i;const r=i-Rs+1+Tu.length;for(let o=0;o<r;o++){const a=Math.pow(2,s);t.push(a);let c=1/a;o>i-Rs?c=Tu[o-i+Rs-1]:o===0&&(c=0),n.push(c);const l=1/(a-2),u=-l,f=1+l,h=[u,u,f,u,f,f,u,u,f,f,u,f],d=6,m=6,_=3,g=2,p=1,M=new Float32Array(_*m*d),v=new Float32Array(g*m*d),x=new Float32Array(p*m*d);for(let T=0;T<d;T++){const R=T%3*2/3-1,I=T>2?0:-1,w=[R,I,0,R+2/3,I,0,R+2/3,I+1,0,R,I,0,R+2/3,I+1,0,R,I+1,0];M.set(w,_*m*T),v.set(h,g*m*T);const S=[T,T,T,T,T,T];x.set(S,p*m*T)}const L=new Ft;L.setAttribute("position",new Xt(M,_)),L.setAttribute("uv",new Xt(v,g)),L.setAttribute("faceIndex",new Xt(x,p)),e.push(L),s>Rs&&s--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function Pu(i,e,t){const n=new ts(i,e,t);return n.texture.mapping=jo,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function oo(i,e,t,n,s){i.viewport.set(e,t,n,s),i.scissor.set(e,t,n,s)}function G0(i,e,t){const n=new Float32Array(Qi),s=new b(0,1,0);return new Vn({name:"SphericalGaussianBlur",defines:{n:Qi,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${i}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:s}},vertexShader:bl(),fragmentShader:`

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
		`,blending:Ii,depthTest:!1,depthWrite:!1})}function Lu(){return new Vn({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:bl(),fragmentShader:`

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
		`,blending:Ii,depthTest:!1,depthWrite:!1})}function Iu(){return new Vn({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:bl(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:Ii,depthTest:!1,depthWrite:!1})}function bl(){return`

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
	`}function W0(i){let e=new WeakMap,t=null;function n(a){if(a&&a.isTexture){const c=a.mapping,l=c===Ec||c===bc,u=c===Bs||c===ks;if(l||u){let f=e.get(a);const h=f!==void 0?f.texture.pmremVersion:0;if(a.isRenderTargetTexture&&a.pmremVersion!==h)return t===null&&(t=new Cu(i)),f=l?t.fromEquirectangular(a,f):t.fromCubemap(a,f),f.texture.pmremVersion=a.pmremVersion,e.set(a,f),f.texture;if(f!==void 0)return f.texture;{const d=a.image;return l&&d&&d.height>0||u&&d&&s(d)?(t===null&&(t=new Cu(i)),f=l?t.fromEquirectangular(a):t.fromCubemap(a),f.texture.pmremVersion=a.pmremVersion,e.set(a,f),a.addEventListener("dispose",r),f.texture):null}}}return a}function s(a){let c=0;const l=6;for(let u=0;u<l;u++)a[u]!==void 0&&c++;return c===l}function r(a){const c=a.target;c.removeEventListener("dispose",r);const l=e.get(c);l!==void 0&&(e.delete(c),l.dispose())}function o(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:o}}function X0(i){const e={};function t(n){if(e[n]!==void 0)return e[n];let s;switch(n){case"WEBGL_depth_texture":s=i.getExtension("WEBGL_depth_texture")||i.getExtension("MOZ_WEBGL_depth_texture")||i.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":s=i.getExtension("EXT_texture_filter_anisotropic")||i.getExtension("MOZ_EXT_texture_filter_anisotropic")||i.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":s=i.getExtension("WEBGL_compressed_texture_s3tc")||i.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":s=i.getExtension("WEBGL_compressed_texture_pvrtc")||i.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:s=i.getExtension(n)}return e[n]=s,s}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const s=t(n);return s===null&&vr("THREE.WebGLRenderer: "+n+" extension not supported."),s}}}function q0(i,e,t,n){const s={},r=new WeakMap;function o(f){const h=f.target;h.index!==null&&e.remove(h.index);for(const m in h.attributes)e.remove(h.attributes[m]);for(const m in h.morphAttributes){const _=h.morphAttributes[m];for(let g=0,p=_.length;g<p;g++)e.remove(_[g])}h.removeEventListener("dispose",o),delete s[h.id];const d=r.get(h);d&&(e.remove(d),r.delete(h)),n.releaseStatesOfGeometry(h),h.isInstancedBufferGeometry===!0&&delete h._maxInstanceCount,t.memory.geometries--}function a(f,h){return s[h.id]===!0||(h.addEventListener("dispose",o),s[h.id]=!0,t.memory.geometries++),h}function c(f){const h=f.attributes;for(const m in h)e.update(h[m],i.ARRAY_BUFFER);const d=f.morphAttributes;for(const m in d){const _=d[m];for(let g=0,p=_.length;g<p;g++)e.update(_[g],i.ARRAY_BUFFER)}}function l(f){const h=[],d=f.index,m=f.attributes.position;let _=0;if(d!==null){const M=d.array;_=d.version;for(let v=0,x=M.length;v<x;v+=3){const L=M[v+0],T=M[v+1],R=M[v+2];h.push(L,T,T,R,R,L)}}else if(m!==void 0){const M=m.array;_=m.version;for(let v=0,x=M.length/3-1;v<x;v+=3){const L=v+0,T=v+1,R=v+2;h.push(L,T,T,R,R,L)}}else return;const g=new(of(h)?hf:Sl)(h,1);g.version=_;const p=r.get(f);p&&e.remove(p),r.set(f,g)}function u(f){const h=r.get(f);if(h){const d=f.index;d!==null&&h.version<d.version&&l(f)}else l(f);return r.get(f)}return{get:a,update:c,getWireframeAttribute:u}}function Y0(i,e,t){let n;function s(h){n=h}let r,o;function a(h){r=h.type,o=h.bytesPerElement}function c(h,d){i.drawElements(n,d,r,h*o),t.update(d,n,1)}function l(h,d,m){m!==0&&(i.drawElementsInstanced(n,d,r,h*o,m),t.update(d,n,m))}function u(h,d,m){if(m===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,d,0,r,h,0,m);let g=0;for(let p=0;p<m;p++)g+=d[p];t.update(g,n,1)}function f(h,d,m,_){if(m===0)return;const g=e.get("WEBGL_multi_draw");if(g===null)for(let p=0;p<h.length;p++)l(h[p]/o,d[p],_[p]);else{g.multiDrawElementsInstancedWEBGL(n,d,0,r,h,0,_,0,m);let p=0;for(let M=0;M<m;M++)p+=d[M]*_[M];t.update(p,n,1)}}this.setMode=s,this.setIndex=a,this.render=c,this.renderInstances=l,this.renderMultiDraw=u,this.renderMultiDrawInstances=f}function j0(i){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(r,o,a){switch(t.calls++,o){case i.TRIANGLES:t.triangles+=a*(r/3);break;case i.LINES:t.lines+=a*(r/2);break;case i.LINE_STRIP:t.lines+=a*(r-1);break;case i.LINE_LOOP:t.lines+=a*r;break;case i.POINTS:t.points+=a*r;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",o);break}}function s(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:s,update:n}}function $0(i,e,t){const n=new WeakMap,s=new ht;function r(o,a,c){const l=o.morphTargetInfluences,u=a.morphAttributes.position||a.morphAttributes.normal||a.morphAttributes.color,f=u!==void 0?u.length:0;let h=n.get(a);if(h===void 0||h.count!==f){let w=function(){R.dispose(),n.delete(a),a.removeEventListener("dispose",w)};h!==void 0&&h.texture.dispose();const d=a.morphAttributes.position!==void 0,m=a.morphAttributes.normal!==void 0,_=a.morphAttributes.color!==void 0,g=a.morphAttributes.position||[],p=a.morphAttributes.normal||[],M=a.morphAttributes.color||[];let v=0;d===!0&&(v=1),m===!0&&(v=2),_===!0&&(v=3);let x=a.attributes.position.count*v,L=1;x>e.maxTextureSize&&(L=Math.ceil(x/e.maxTextureSize),x=e.maxTextureSize);const T=new Float32Array(x*L*4*f),R=new cf(T,x,L,f);R.type=Dn,R.needsUpdate=!0;const I=v*4;for(let S=0;S<f;S++){const P=g[S],G=p[S],B=M[S],V=x*L*4*S;for(let j=0;j<P.count;j++){const W=j*I;d===!0&&(s.fromBufferAttribute(P,j),T[V+W+0]=s.x,T[V+W+1]=s.y,T[V+W+2]=s.z,T[V+W+3]=0),m===!0&&(s.fromBufferAttribute(G,j),T[V+W+4]=s.x,T[V+W+5]=s.y,T[V+W+6]=s.z,T[V+W+7]=0),_===!0&&(s.fromBufferAttribute(B,j),T[V+W+8]=s.x,T[V+W+9]=s.y,T[V+W+10]=s.z,T[V+W+11]=B.itemSize===4?s.w:1)}}h={count:f,texture:R,size:new ie(x,L)},n.set(a,h),a.addEventListener("dispose",w)}if(o.isInstancedMesh===!0&&o.morphTexture!==null)c.getUniforms().setValue(i,"morphTexture",o.morphTexture,t);else{let d=0;for(let _=0;_<l.length;_++)d+=l[_];const m=a.morphTargetsRelative?1:1-d;c.getUniforms().setValue(i,"morphTargetBaseInfluence",m),c.getUniforms().setValue(i,"morphTargetInfluences",l)}c.getUniforms().setValue(i,"morphTargetsTexture",h.texture,t),c.getUniforms().setValue(i,"morphTargetsTextureSize",h.size)}return{update:r}}function K0(i,e,t,n){let s=new WeakMap;function r(c){const l=n.render.frame,u=c.geometry,f=e.get(c,u);if(s.get(f)!==l&&(e.update(f),s.set(f,l)),c.isInstancedMesh&&(c.hasEventListener("dispose",a)===!1&&c.addEventListener("dispose",a),s.get(c)!==l&&(t.update(c.instanceMatrix,i.ARRAY_BUFFER),c.instanceColor!==null&&t.update(c.instanceColor,i.ARRAY_BUFFER),s.set(c,l))),c.isSkinnedMesh){const h=c.skeleton;s.get(h)!==l&&(h.update(),s.set(h,l))}return f}function o(){s=new WeakMap}function a(c){const l=c.target;l.removeEventListener("dispose",a),t.remove(l.instanceMatrix),l.instanceColor!==null&&t.remove(l.instanceColor)}return{update:r,dispose:o}}class gf extends Wt{constructor(e,t,n,s,r,o,a,c,l,u=Is){if(u!==Is&&u!==Vs)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&u===Is&&(n=es),n===void 0&&u===Vs&&(n=Hs),super(null,s,r,o,a,c,u,n,l),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=a!==void 0?a:rn,this.minFilter=c!==void 0?c:rn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const _f=new Wt,Du=new gf(1,1),xf=new cf,vf=new Op,yf=new pf,Nu=[],Uu=[],Ou=new Float32Array(16),Fu=new Float32Array(9),Bu=new Float32Array(4);function Ks(i,e,t){const n=i[0];if(n<=0||n>0)return i;const s=e*t;let r=Nu[s];if(r===void 0&&(r=new Float32Array(s),Nu[s]=r),e!==0){n.toArray(r,0);for(let o=1,a=0;o!==e;++o)a+=t,i[o].toArray(r,a)}return r}function zt(i,e){if(i.length!==e.length)return!1;for(let t=0,n=i.length;t<n;t++)if(i[t]!==e[t])return!1;return!0}function Ht(i,e){for(let t=0,n=e.length;t<n;t++)i[t]=e[t]}function Jo(i,e){let t=Uu[e];t===void 0&&(t=new Int32Array(e),Uu[e]=t);for(let n=0;n!==e;++n)t[n]=i.allocateTextureUnit();return t}function Z0(i,e){const t=this.cache;t[0]!==e&&(i.uniform1f(this.addr,e),t[0]=e)}function J0(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(zt(t,e))return;i.uniform2fv(this.addr,e),Ht(t,e)}}function Q0(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(i.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(zt(t,e))return;i.uniform3fv(this.addr,e),Ht(t,e)}}function e_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(zt(t,e))return;i.uniform4fv(this.addr,e),Ht(t,e)}}function t_(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(zt(t,e))return;i.uniformMatrix2fv(this.addr,!1,e),Ht(t,e)}else{if(zt(t,n))return;Bu.set(n),i.uniformMatrix2fv(this.addr,!1,Bu),Ht(t,n)}}function n_(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(zt(t,e))return;i.uniformMatrix3fv(this.addr,!1,e),Ht(t,e)}else{if(zt(t,n))return;Fu.set(n),i.uniformMatrix3fv(this.addr,!1,Fu),Ht(t,n)}}function i_(i,e){const t=this.cache,n=e.elements;if(n===void 0){if(zt(t,e))return;i.uniformMatrix4fv(this.addr,!1,e),Ht(t,e)}else{if(zt(t,n))return;Ou.set(n),i.uniformMatrix4fv(this.addr,!1,Ou),Ht(t,n)}}function s_(i,e){const t=this.cache;t[0]!==e&&(i.uniform1i(this.addr,e),t[0]=e)}function r_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(zt(t,e))return;i.uniform2iv(this.addr,e),Ht(t,e)}}function o_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(zt(t,e))return;i.uniform3iv(this.addr,e),Ht(t,e)}}function a_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(zt(t,e))return;i.uniform4iv(this.addr,e),Ht(t,e)}}function c_(i,e){const t=this.cache;t[0]!==e&&(i.uniform1ui(this.addr,e),t[0]=e)}function l_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(i.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(zt(t,e))return;i.uniform2uiv(this.addr,e),Ht(t,e)}}function u_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(i.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(zt(t,e))return;i.uniform3uiv(this.addr,e),Ht(t,e)}}function h_(i,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(i.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(zt(t,e))return;i.uniform4uiv(this.addr,e),Ht(t,e)}}function f_(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s);let r;this.type===i.SAMPLER_2D_SHADOW?(Du.compareFunction=rf,r=Du):r=_f,t.setTexture2D(e||r,s)}function d_(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture3D(e||vf,s)}function p_(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTextureCube(e||yf,s)}function m_(i,e,t){const n=this.cache,s=t.allocateTextureUnit();n[0]!==s&&(i.uniform1i(this.addr,s),n[0]=s),t.setTexture2DArray(e||xf,s)}function g_(i){switch(i){case 5126:return Z0;case 35664:return J0;case 35665:return Q0;case 35666:return e_;case 35674:return t_;case 35675:return n_;case 35676:return i_;case 5124:case 35670:return s_;case 35667:case 35671:return r_;case 35668:case 35672:return o_;case 35669:case 35673:return a_;case 5125:return c_;case 36294:return l_;case 36295:return u_;case 36296:return h_;case 35678:case 36198:case 36298:case 36306:case 35682:return f_;case 35679:case 36299:case 36307:return d_;case 35680:case 36300:case 36308:case 36293:return p_;case 36289:case 36303:case 36311:case 36292:return m_}}function __(i,e){i.uniform1fv(this.addr,e)}function x_(i,e){const t=Ks(e,this.size,2);i.uniform2fv(this.addr,t)}function v_(i,e){const t=Ks(e,this.size,3);i.uniform3fv(this.addr,t)}function y_(i,e){const t=Ks(e,this.size,4);i.uniform4fv(this.addr,t)}function M_(i,e){const t=Ks(e,this.size,4);i.uniformMatrix2fv(this.addr,!1,t)}function S_(i,e){const t=Ks(e,this.size,9);i.uniformMatrix3fv(this.addr,!1,t)}function E_(i,e){const t=Ks(e,this.size,16);i.uniformMatrix4fv(this.addr,!1,t)}function b_(i,e){i.uniform1iv(this.addr,e)}function w_(i,e){i.uniform2iv(this.addr,e)}function T_(i,e){i.uniform3iv(this.addr,e)}function A_(i,e){i.uniform4iv(this.addr,e)}function R_(i,e){i.uniform1uiv(this.addr,e)}function C_(i,e){i.uniform2uiv(this.addr,e)}function P_(i,e){i.uniform3uiv(this.addr,e)}function L_(i,e){i.uniform4uiv(this.addr,e)}function I_(i,e,t){const n=this.cache,s=e.length,r=Jo(t,s);zt(n,r)||(i.uniform1iv(this.addr,r),Ht(n,r));for(let o=0;o!==s;++o)t.setTexture2D(e[o]||_f,r[o])}function D_(i,e,t){const n=this.cache,s=e.length,r=Jo(t,s);zt(n,r)||(i.uniform1iv(this.addr,r),Ht(n,r));for(let o=0;o!==s;++o)t.setTexture3D(e[o]||vf,r[o])}function N_(i,e,t){const n=this.cache,s=e.length,r=Jo(t,s);zt(n,r)||(i.uniform1iv(this.addr,r),Ht(n,r));for(let o=0;o!==s;++o)t.setTextureCube(e[o]||yf,r[o])}function U_(i,e,t){const n=this.cache,s=e.length,r=Jo(t,s);zt(n,r)||(i.uniform1iv(this.addr,r),Ht(n,r));for(let o=0;o!==s;++o)t.setTexture2DArray(e[o]||xf,r[o])}function O_(i){switch(i){case 5126:return __;case 35664:return x_;case 35665:return v_;case 35666:return y_;case 35674:return M_;case 35675:return S_;case 35676:return E_;case 5124:case 35670:return b_;case 35667:case 35671:return w_;case 35668:case 35672:return T_;case 35669:case 35673:return A_;case 5125:return R_;case 36294:return C_;case 36295:return P_;case 36296:return L_;case 35678:case 36198:case 36298:case 36306:case 35682:return I_;case 35679:case 36299:case 36307:return D_;case 35680:case 36300:case 36308:case 36293:return N_;case 36289:case 36303:case 36311:case 36292:return U_}}class F_{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=g_(t.type)}}class B_{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=O_(t.type)}}class k_{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const s=this.seq;for(let r=0,o=s.length;r!==o;++r){const a=s[r];a.setValue(e,t[a.id],n)}}}const Fa=/(\w+)(\])?(\[|\.)?/g;function ku(i,e){i.seq.push(e),i.map[e.id]=e}function z_(i,e,t){const n=i.name,s=n.length;for(Fa.lastIndex=0;;){const r=Fa.exec(n),o=Fa.lastIndex;let a=r[1];const c=r[2]==="]",l=r[3];if(c&&(a=a|0),l===void 0||l==="["&&o+2===s){ku(t,l===void 0?new F_(a,i,e):new B_(a,i,e));break}else{let f=t.map[a];f===void 0&&(f=new k_(a),ku(t,f)),t=f}}}class Do{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let s=0;s<n;++s){const r=e.getActiveUniform(t,s),o=e.getUniformLocation(t,r.name);z_(r,o,this)}}setValue(e,t,n,s){const r=this.map[t];r!==void 0&&r.setValue(e,n,s)}setOptional(e,t,n){const s=t[n];s!==void 0&&this.setValue(e,n,s)}static upload(e,t,n,s){for(let r=0,o=t.length;r!==o;++r){const a=t[r],c=n[a.id];c.needsUpdate!==!1&&a.setValue(e,c.value,s)}}static seqWithValue(e,t){const n=[];for(let s=0,r=e.length;s!==r;++s){const o=e[s];o.id in t&&n.push(o)}return n}}function zu(i,e,t){const n=i.createShader(e);return i.shaderSource(n,t),i.compileShader(n),n}const H_=37297;let V_=0;function G_(i,e){const t=i.split(`
`),n=[],s=Math.max(e-6,0),r=Math.min(e+6,t.length);for(let o=s;o<r;o++){const a=o+1;n.push(`${a===e?">":" "} ${a}: ${t[o]}`)}return n.join(`
`)}const Hu=new et;function W_(i){ot._getMatrix(Hu,ot.workingColorSpace,i);const e=`mat3( ${Hu.elements.map(t=>t.toFixed(4))} )`;switch(ot.getTransfer(i)){case $o:return[e,"LinearTransferOETF"];case yt:return[e,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space: ",i),[e,"LinearTransferOETF"]}}function Vu(i,e,t){const n=i.getShaderParameter(e,i.COMPILE_STATUS),s=i.getShaderInfoLog(e).trim();if(n&&s==="")return"";const r=/ERROR: 0:(\d+)/.exec(s);if(r){const o=parseInt(r[1]);return t.toUpperCase()+`

`+s+`

`+G_(i.getShaderSource(e),o)}else return s}function X_(i,e){const t=W_(e);return[`vec4 ${i}( vec4 value ) {`,`	return ${t[1]}( vec4( value.rgb * ${t[0]}, value.a ) );`,"}"].join(`
`)}function q_(i,e){let t;switch(e){case qd:t="Linear";break;case Yd:t="Reinhard";break;case jd:t="Cineon";break;case $d:t="ACESFilmic";break;case Zd:t="AgX";break;case Jd:t="Neutral";break;case Kd:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+i+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const ao=new b;function Y_(){ot.getLuminanceCoefficients(ao);const i=ao.x.toFixed(4),e=ao.y.toFixed(4),t=ao.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${i}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function j_(i){return[i.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",i.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(yr).join(`
`)}function $_(i){const e=[];for(const t in i){const n=i[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function K_(i,e){const t={},n=i.getProgramParameter(e,i.ACTIVE_ATTRIBUTES);for(let s=0;s<n;s++){const r=i.getActiveAttrib(e,s),o=r.name;let a=1;r.type===i.FLOAT_MAT2&&(a=2),r.type===i.FLOAT_MAT3&&(a=3),r.type===i.FLOAT_MAT4&&(a=4),t[o]={type:r.type,location:i.getAttribLocation(e,o),locationSize:a}}return t}function yr(i){return i!==""}function Gu(i,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return i.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function Wu(i,e){return i.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const Z_=/^[ \t]*#include +<([\w\d./]+)>/gm;function Qc(i){return i.replace(Z_,Q_)}const J_=new Map;function Q_(i,e){let t=nt[e];if(t===void 0){const n=J_.get(e);if(n!==void 0)t=nt[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return Qc(t)}const ex=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Xu(i){return i.replace(ex,tx)}function tx(i,e,t,n){let s="";for(let r=parseInt(e);r<parseInt(t);r++)s+=n.replace(/\[\s*i\s*\]/g,"[ "+r+" ]").replace(/UNROLLED_LOOP_INDEX/g,r);return s}function qu(i){let e=`precision ${i.precision} float;
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
#define LOW_PRECISION`),e}function nx(i){let e="SHADOWMAP_TYPE_BASIC";return i.shadowMapType===Gh?e="SHADOWMAP_TYPE_PCF":i.shadowMapType===wd?e="SHADOWMAP_TYPE_PCF_SOFT":i.shadowMapType===ni&&(e="SHADOWMAP_TYPE_VSM"),e}function ix(i){let e="ENVMAP_TYPE_CUBE";if(i.envMap)switch(i.envMapMode){case Bs:case ks:e="ENVMAP_TYPE_CUBE";break;case jo:e="ENVMAP_TYPE_CUBE_UV";break}return e}function sx(i){let e="ENVMAP_MODE_REFLECTION";if(i.envMap)switch(i.envMapMode){case ks:e="ENVMAP_MODE_REFRACTION";break}return e}function rx(i){let e="ENVMAP_BLENDING_NONE";if(i.envMap)switch(i.combine){case Wh:e="ENVMAP_BLENDING_MULTIPLY";break;case Wd:e="ENVMAP_BLENDING_MIX";break;case Xd:e="ENVMAP_BLENDING_ADD";break}return e}function ox(i){const e=i.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),112)),texelHeight:n,maxMip:t}}function ax(i,e,t,n){const s=i.getContext(),r=t.defines;let o=t.vertexShader,a=t.fragmentShader;const c=nx(t),l=ix(t),u=sx(t),f=rx(t),h=ox(t),d=j_(t),m=$_(r),_=s.createProgram();let g,p,M=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(g=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m].filter(yr).join(`
`),g.length>0&&(g+=`
`),p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m].filter(yr).join(`
`),p.length>0&&(p+=`
`)):(g=[qu(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+u:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+c:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(yr).join(`
`),p=[qu(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,m,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+l:"",t.envMap?"#define "+u:"",t.envMap?"#define "+f:"",h?"#define CUBEUV_TEXEL_WIDTH "+h.texelWidth:"",h?"#define CUBEUV_TEXEL_HEIGHT "+h.texelHeight:"",h?"#define CUBEUV_MAX_MIP "+h.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+c:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.decodeVideoTextureEmissive?"#define DECODE_VIDEO_TEXTURE_EMISSIVE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==Di?"#define TONE_MAPPING":"",t.toneMapping!==Di?nt.tonemapping_pars_fragment:"",t.toneMapping!==Di?q_("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",nt.colorspace_pars_fragment,X_("linearToOutputTexel",t.outputColorSpace),Y_(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(yr).join(`
`)),o=Qc(o),o=Gu(o,t),o=Wu(o,t),a=Qc(a),a=Gu(a,t),a=Wu(a,t),o=Xu(o),a=Xu(a),t.isRawShaderMaterial!==!0&&(M=`#version 300 es
`,g=[d,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+g,p=["#define varying in",t.glslVersion===su?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===su?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+p);const v=M+g+o,x=M+p+a,L=zu(s,s.VERTEX_SHADER,v),T=zu(s,s.FRAGMENT_SHADER,x);s.attachShader(_,L),s.attachShader(_,T),t.index0AttributeName!==void 0?s.bindAttribLocation(_,0,t.index0AttributeName):t.morphTargets===!0&&s.bindAttribLocation(_,0,"position"),s.linkProgram(_);function R(P){if(i.debug.checkShaderErrors){const G=s.getProgramInfoLog(_).trim(),B=s.getShaderInfoLog(L).trim(),V=s.getShaderInfoLog(T).trim();let j=!0,W=!0;if(s.getProgramParameter(_,s.LINK_STATUS)===!1)if(j=!1,typeof i.debug.onShaderError=="function")i.debug.onShaderError(s,_,L,T);else{const ee=Vu(s,L,"vertex"),O=Vu(s,T,"fragment");console.error("THREE.WebGLProgram: Shader Error "+s.getError()+" - VALIDATE_STATUS "+s.getProgramParameter(_,s.VALIDATE_STATUS)+`

Material Name: `+P.name+`
Material Type: `+P.type+`

Program Info Log: `+G+`
`+ee+`
`+O)}else G!==""?console.warn("THREE.WebGLProgram: Program Info Log:",G):(B===""||V==="")&&(W=!1);W&&(P.diagnostics={runnable:j,programLog:G,vertexShader:{log:B,prefix:g},fragmentShader:{log:V,prefix:p}})}s.deleteShader(L),s.deleteShader(T),I=new Do(s,_),w=K_(s,_)}let I;this.getUniforms=function(){return I===void 0&&R(this),I};let w;this.getAttributes=function(){return w===void 0&&R(this),w};let S=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return S===!1&&(S=s.getProgramParameter(_,H_)),S},this.destroy=function(){n.releaseStatesOfProgram(this),s.deleteProgram(_),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=V_++,this.cacheKey=e,this.usedTimes=1,this.program=_,this.vertexShader=L,this.fragmentShader=T,this}let cx=0;class lx{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,s=this._getShaderStage(t),r=this._getShaderStage(n),o=this._getShaderCacheForMaterial(e);return o.has(s)===!1&&(o.add(s),s.usedTimes++),o.has(r)===!1&&(o.add(r),r.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new ux(e),t.set(e,n)),n}}class ux{constructor(e){this.id=cx++,this.code=e,this.usedTimes=0}}function hx(i,e,t,n,s,r,o){const a=new lf,c=new lx,l=new Set,u=[],f=s.logarithmicDepthBuffer,h=s.vertexTextures;let d=s.precision;const m={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function _(w){return l.add(w),w===0?"uv":`uv${w}`}function g(w,S,P,G,B){const V=G.fog,j=B.geometry,W=w.isMeshStandardMaterial?G.environment:null,ee=(w.isMeshStandardMaterial?t:e).get(w.envMap||W),O=ee&&ee.mapping===jo?ee.image.height:null,re=m[w.type];w.precision!==null&&(d=s.getMaxPrecision(w.precision),d!==w.precision&&console.warn("THREE.WebGLProgram.getParameters:",w.precision,"not supported, using",d,"instead."));const ue=j.morphAttributes.position||j.morphAttributes.normal||j.morphAttributes.color,Me=ue!==void 0?ue.length:0;let Ye=0;j.morphAttributes.position!==void 0&&(Ye=1),j.morphAttributes.normal!==void 0&&(Ye=2),j.morphAttributes.color!==void 0&&(Ye=3);let dt,$,ce,Pe;if(re){const gt=kn[re];dt=gt.vertexShader,$=gt.fragmentShader}else dt=w.vertexShader,$=w.fragmentShader,c.update(w),ce=c.getVertexShaderID(w),Pe=c.getFragmentShaderID(w);const fe=i.getRenderTarget(),ze=i.state.buffers.depth.getReversed(),$e=B.isInstancedMesh===!0,qe=B.isBatchedMesh===!0,ct=!!w.map,J=!!w.matcap,oe=!!ee,C=!!w.aoMap,Fe=!!w.lightMap,ne=!!w.bumpMap,we=!!w.normalMap,de=!!w.displacementMap,We=!!w.emissiveMap,Ee=!!w.metalnessMap,A=!!w.roughnessMap,y=w.anisotropy>0,F=w.clearcoat>0,q=w.dispersion>0,Q=w.iridescence>0,Y=w.sheen>0,Ie=w.transmission>0,ge=y&&!!w.anisotropyMap,be=F&&!!w.clearcoatMap,rt=F&&!!w.clearcoatNormalMap,se=F&&!!w.clearcoatRoughnessMap,Ae=Q&&!!w.iridescenceMap,Xe=Q&&!!w.iridescenceThicknessMap,je=Y&&!!w.sheenColorMap,Re=Y&&!!w.sheenRoughnessMap,at=!!w.specularMap,tt=!!w.specularColorMap,St=!!w.specularIntensityMap,D=Ie&&!!w.transmissionMap,xe=Ie&&!!w.thicknessMap,X=!!w.gradientMap,K=!!w.alphaMap,Se=w.alphaTest>0,ve=!!w.alphaHash,Je=!!w.extensions;let Lt=Di;w.toneMapped&&(fe===null||fe.isXRRenderTarget===!0)&&(Lt=i.toneMapping);const Kt={shaderID:re,shaderType:w.type,shaderName:w.name,vertexShader:dt,fragmentShader:$,defines:w.defines,customVertexShaderID:ce,customFragmentShaderID:Pe,isRawShaderMaterial:w.isRawShaderMaterial===!0,glslVersion:w.glslVersion,precision:d,batching:qe,batchingColor:qe&&B._colorsTexture!==null,instancing:$e,instancingColor:$e&&B.instanceColor!==null,instancingMorph:$e&&B.morphTexture!==null,supportsVertexTextures:h,outputColorSpace:fe===null?i.outputColorSpace:fe.isXRRenderTarget===!0?fe.texture.colorSpace:en,alphaToCoverage:!!w.alphaToCoverage,map:ct,matcap:J,envMap:oe,envMapMode:oe&&ee.mapping,envMapCubeUVHeight:O,aoMap:C,lightMap:Fe,bumpMap:ne,normalMap:we,displacementMap:h&&de,emissiveMap:We,normalMapObjectSpace:we&&w.normalMapType===sp,normalMapTangentSpace:we&&w.normalMapType===sf,metalnessMap:Ee,roughnessMap:A,anisotropy:y,anisotropyMap:ge,clearcoat:F,clearcoatMap:be,clearcoatNormalMap:rt,clearcoatRoughnessMap:se,dispersion:q,iridescence:Q,iridescenceMap:Ae,iridescenceThicknessMap:Xe,sheen:Y,sheenColorMap:je,sheenRoughnessMap:Re,specularMap:at,specularColorMap:tt,specularIntensityMap:St,transmission:Ie,transmissionMap:D,thicknessMap:xe,gradientMap:X,opaque:w.transparent===!1&&w.blending===Ls&&w.alphaToCoverage===!1,alphaMap:K,alphaTest:Se,alphaHash:ve,combine:w.combine,mapUv:ct&&_(w.map.channel),aoMapUv:C&&_(w.aoMap.channel),lightMapUv:Fe&&_(w.lightMap.channel),bumpMapUv:ne&&_(w.bumpMap.channel),normalMapUv:we&&_(w.normalMap.channel),displacementMapUv:de&&_(w.displacementMap.channel),emissiveMapUv:We&&_(w.emissiveMap.channel),metalnessMapUv:Ee&&_(w.metalnessMap.channel),roughnessMapUv:A&&_(w.roughnessMap.channel),anisotropyMapUv:ge&&_(w.anisotropyMap.channel),clearcoatMapUv:be&&_(w.clearcoatMap.channel),clearcoatNormalMapUv:rt&&_(w.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:se&&_(w.clearcoatRoughnessMap.channel),iridescenceMapUv:Ae&&_(w.iridescenceMap.channel),iridescenceThicknessMapUv:Xe&&_(w.iridescenceThicknessMap.channel),sheenColorMapUv:je&&_(w.sheenColorMap.channel),sheenRoughnessMapUv:Re&&_(w.sheenRoughnessMap.channel),specularMapUv:at&&_(w.specularMap.channel),specularColorMapUv:tt&&_(w.specularColorMap.channel),specularIntensityMapUv:St&&_(w.specularIntensityMap.channel),transmissionMapUv:D&&_(w.transmissionMap.channel),thicknessMapUv:xe&&_(w.thicknessMap.channel),alphaMapUv:K&&_(w.alphaMap.channel),vertexTangents:!!j.attributes.tangent&&(we||y),vertexColors:w.vertexColors,vertexAlphas:w.vertexColors===!0&&!!j.attributes.color&&j.attributes.color.itemSize===4,pointsUvs:B.isPoints===!0&&!!j.attributes.uv&&(ct||K),fog:!!V,useFog:w.fog===!0,fogExp2:!!V&&V.isFogExp2,flatShading:w.flatShading===!0,sizeAttenuation:w.sizeAttenuation===!0,logarithmicDepthBuffer:f,reverseDepthBuffer:ze,skinning:B.isSkinnedMesh===!0,morphTargets:j.morphAttributes.position!==void 0,morphNormals:j.morphAttributes.normal!==void 0,morphColors:j.morphAttributes.color!==void 0,morphTargetsCount:Me,morphTextureStride:Ye,numDirLights:S.directional.length,numPointLights:S.point.length,numSpotLights:S.spot.length,numSpotLightMaps:S.spotLightMap.length,numRectAreaLights:S.rectArea.length,numHemiLights:S.hemi.length,numDirLightShadows:S.directionalShadowMap.length,numPointLightShadows:S.pointShadowMap.length,numSpotLightShadows:S.spotShadowMap.length,numSpotLightShadowsWithMaps:S.numSpotLightShadowsWithMaps,numLightProbes:S.numLightProbes,numClippingPlanes:o.numPlanes,numClipIntersection:o.numIntersection,dithering:w.dithering,shadowMapEnabled:i.shadowMap.enabled&&P.length>0,shadowMapType:i.shadowMap.type,toneMapping:Lt,decodeVideoTexture:ct&&w.map.isVideoTexture===!0&&ot.getTransfer(w.map.colorSpace)===yt,decodeVideoTextureEmissive:We&&w.emissiveMap.isVideoTexture===!0&&ot.getTransfer(w.emissiveMap.colorSpace)===yt,premultipliedAlpha:w.premultipliedAlpha,doubleSided:w.side===mn,flipSided:w.side===sn,useDepthPacking:w.depthPacking>=0,depthPacking:w.depthPacking||0,index0AttributeName:w.index0AttributeName,extensionClipCullDistance:Je&&w.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(Je&&w.extensions.multiDraw===!0||qe)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:w.customProgramCacheKey()};return Kt.vertexUv1s=l.has(1),Kt.vertexUv2s=l.has(2),Kt.vertexUv3s=l.has(3),l.clear(),Kt}function p(w){const S=[];if(w.shaderID?S.push(w.shaderID):(S.push(w.customVertexShaderID),S.push(w.customFragmentShaderID)),w.defines!==void 0)for(const P in w.defines)S.push(P),S.push(w.defines[P]);return w.isRawShaderMaterial===!1&&(M(S,w),v(S,w),S.push(i.outputColorSpace)),S.push(w.customProgramCacheKey),S.join()}function M(w,S){w.push(S.precision),w.push(S.outputColorSpace),w.push(S.envMapMode),w.push(S.envMapCubeUVHeight),w.push(S.mapUv),w.push(S.alphaMapUv),w.push(S.lightMapUv),w.push(S.aoMapUv),w.push(S.bumpMapUv),w.push(S.normalMapUv),w.push(S.displacementMapUv),w.push(S.emissiveMapUv),w.push(S.metalnessMapUv),w.push(S.roughnessMapUv),w.push(S.anisotropyMapUv),w.push(S.clearcoatMapUv),w.push(S.clearcoatNormalMapUv),w.push(S.clearcoatRoughnessMapUv),w.push(S.iridescenceMapUv),w.push(S.iridescenceThicknessMapUv),w.push(S.sheenColorMapUv),w.push(S.sheenRoughnessMapUv),w.push(S.specularMapUv),w.push(S.specularColorMapUv),w.push(S.specularIntensityMapUv),w.push(S.transmissionMapUv),w.push(S.thicknessMapUv),w.push(S.combine),w.push(S.fogExp2),w.push(S.sizeAttenuation),w.push(S.morphTargetsCount),w.push(S.morphAttributeCount),w.push(S.numDirLights),w.push(S.numPointLights),w.push(S.numSpotLights),w.push(S.numSpotLightMaps),w.push(S.numHemiLights),w.push(S.numRectAreaLights),w.push(S.numDirLightShadows),w.push(S.numPointLightShadows),w.push(S.numSpotLightShadows),w.push(S.numSpotLightShadowsWithMaps),w.push(S.numLightProbes),w.push(S.shadowMapType),w.push(S.toneMapping),w.push(S.numClippingPlanes),w.push(S.numClipIntersection),w.push(S.depthPacking)}function v(w,S){a.disableAll(),S.supportsVertexTextures&&a.enable(0),S.instancing&&a.enable(1),S.instancingColor&&a.enable(2),S.instancingMorph&&a.enable(3),S.matcap&&a.enable(4),S.envMap&&a.enable(5),S.normalMapObjectSpace&&a.enable(6),S.normalMapTangentSpace&&a.enable(7),S.clearcoat&&a.enable(8),S.iridescence&&a.enable(9),S.alphaTest&&a.enable(10),S.vertexColors&&a.enable(11),S.vertexAlphas&&a.enable(12),S.vertexUv1s&&a.enable(13),S.vertexUv2s&&a.enable(14),S.vertexUv3s&&a.enable(15),S.vertexTangents&&a.enable(16),S.anisotropy&&a.enable(17),S.alphaHash&&a.enable(18),S.batching&&a.enable(19),S.dispersion&&a.enable(20),S.batchingColor&&a.enable(21),w.push(a.mask),a.disableAll(),S.fog&&a.enable(0),S.useFog&&a.enable(1),S.flatShading&&a.enable(2),S.logarithmicDepthBuffer&&a.enable(3),S.reverseDepthBuffer&&a.enable(4),S.skinning&&a.enable(5),S.morphTargets&&a.enable(6),S.morphNormals&&a.enable(7),S.morphColors&&a.enable(8),S.premultipliedAlpha&&a.enable(9),S.shadowMapEnabled&&a.enable(10),S.doubleSided&&a.enable(11),S.flipSided&&a.enable(12),S.useDepthPacking&&a.enable(13),S.dithering&&a.enable(14),S.transmission&&a.enable(15),S.sheen&&a.enable(16),S.opaque&&a.enable(17),S.pointsUvs&&a.enable(18),S.decodeVideoTexture&&a.enable(19),S.decodeVideoTextureEmissive&&a.enable(20),S.alphaToCoverage&&a.enable(21),w.push(a.mask)}function x(w){const S=m[w.type];let P;if(S){const G=kn[S];P=jp.clone(G.uniforms)}else P=w.uniforms;return P}function L(w,S){let P;for(let G=0,B=u.length;G<B;G++){const V=u[G];if(V.cacheKey===S){P=V,++P.usedTimes;break}}return P===void 0&&(P=new ax(i,S,w,r),u.push(P)),P}function T(w){if(--w.usedTimes===0){const S=u.indexOf(w);u[S]=u[u.length-1],u.pop(),w.destroy()}}function R(w){c.remove(w)}function I(){c.dispose()}return{getParameters:g,getProgramCacheKey:p,getUniforms:x,acquireProgram:L,releaseProgram:T,releaseShaderCache:R,programs:u,dispose:I}}function fx(){let i=new WeakMap;function e(o){return i.has(o)}function t(o){let a=i.get(o);return a===void 0&&(a={},i.set(o,a)),a}function n(o){i.delete(o)}function s(o,a,c){i.get(o)[a]=c}function r(){i=new WeakMap}return{has:e,get:t,remove:n,update:s,dispose:r}}function dx(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.material.id!==e.material.id?i.material.id-e.material.id:i.z!==e.z?i.z-e.z:i.id-e.id}function Yu(i,e){return i.groupOrder!==e.groupOrder?i.groupOrder-e.groupOrder:i.renderOrder!==e.renderOrder?i.renderOrder-e.renderOrder:i.z!==e.z?e.z-i.z:i.id-e.id}function ju(){const i=[];let e=0;const t=[],n=[],s=[];function r(){e=0,t.length=0,n.length=0,s.length=0}function o(f,h,d,m,_,g){let p=i[e];return p===void 0?(p={id:f.id,object:f,geometry:h,material:d,groupOrder:m,renderOrder:f.renderOrder,z:_,group:g},i[e]=p):(p.id=f.id,p.object=f,p.geometry=h,p.material=d,p.groupOrder=m,p.renderOrder=f.renderOrder,p.z=_,p.group=g),e++,p}function a(f,h,d,m,_,g){const p=o(f,h,d,m,_,g);d.transmission>0?n.push(p):d.transparent===!0?s.push(p):t.push(p)}function c(f,h,d,m,_,g){const p=o(f,h,d,m,_,g);d.transmission>0?n.unshift(p):d.transparent===!0?s.unshift(p):t.unshift(p)}function l(f,h){t.length>1&&t.sort(f||dx),n.length>1&&n.sort(h||Yu),s.length>1&&s.sort(h||Yu)}function u(){for(let f=e,h=i.length;f<h;f++){const d=i[f];if(d.id===null)break;d.id=null,d.object=null,d.geometry=null,d.material=null,d.group=null}}return{opaque:t,transmissive:n,transparent:s,init:r,push:a,unshift:c,finish:u,sort:l}}function px(){let i=new WeakMap;function e(n,s){const r=i.get(n);let o;return r===void 0?(o=new ju,i.set(n,[o])):s>=r.length?(o=new ju,r.push(o)):o=r[s],o}function t(){i=new WeakMap}return{get:e,dispose:t}}function mx(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new b,color:new Ve};break;case"SpotLight":t={position:new b,direction:new b,color:new Ve,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new b,color:new Ve,distance:0,decay:0};break;case"HemisphereLight":t={direction:new b,skyColor:new Ve,groundColor:new Ve};break;case"RectAreaLight":t={color:new Ve,position:new b,halfWidth:new b,halfHeight:new b};break}return i[e.id]=t,t}}}function gx(){const i={};return{get:function(e){if(i[e.id]!==void 0)return i[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new ie};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new ie};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new ie,shadowCameraNear:1,shadowCameraFar:1e3};break}return i[e.id]=t,t}}}let _x=0;function xx(i,e){return(e.castShadow?2:0)-(i.castShadow?2:0)+(e.map?1:0)-(i.map?1:0)}function vx(i){const e=new mx,t=gx(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let l=0;l<9;l++)n.probe.push(new b);const s=new b,r=new De,o=new De;function a(l){let u=0,f=0,h=0;for(let w=0;w<9;w++)n.probe[w].set(0,0,0);let d=0,m=0,_=0,g=0,p=0,M=0,v=0,x=0,L=0,T=0,R=0;l.sort(xx);for(let w=0,S=l.length;w<S;w++){const P=l[w],G=P.color,B=P.intensity,V=P.distance,j=P.shadow&&P.shadow.map?P.shadow.map.texture:null;if(P.isAmbientLight)u+=G.r*B,f+=G.g*B,h+=G.b*B;else if(P.isLightProbe){for(let W=0;W<9;W++)n.probe[W].addScaledVector(P.sh.coefficients[W],B);R++}else if(P.isDirectionalLight){const W=e.get(P);if(W.color.copy(P.color).multiplyScalar(P.intensity),P.castShadow){const ee=P.shadow,O=t.get(P);O.shadowIntensity=ee.intensity,O.shadowBias=ee.bias,O.shadowNormalBias=ee.normalBias,O.shadowRadius=ee.radius,O.shadowMapSize=ee.mapSize,n.directionalShadow[d]=O,n.directionalShadowMap[d]=j,n.directionalShadowMatrix[d]=P.shadow.matrix,M++}n.directional[d]=W,d++}else if(P.isSpotLight){const W=e.get(P);W.position.setFromMatrixPosition(P.matrixWorld),W.color.copy(G).multiplyScalar(B),W.distance=V,W.coneCos=Math.cos(P.angle),W.penumbraCos=Math.cos(P.angle*(1-P.penumbra)),W.decay=P.decay,n.spot[_]=W;const ee=P.shadow;if(P.map&&(n.spotLightMap[L]=P.map,L++,ee.updateMatrices(P),P.castShadow&&T++),n.spotLightMatrix[_]=ee.matrix,P.castShadow){const O=t.get(P);O.shadowIntensity=ee.intensity,O.shadowBias=ee.bias,O.shadowNormalBias=ee.normalBias,O.shadowRadius=ee.radius,O.shadowMapSize=ee.mapSize,n.spotShadow[_]=O,n.spotShadowMap[_]=j,x++}_++}else if(P.isRectAreaLight){const W=e.get(P);W.color.copy(G).multiplyScalar(B),W.halfWidth.set(P.width*.5,0,0),W.halfHeight.set(0,P.height*.5,0),n.rectArea[g]=W,g++}else if(P.isPointLight){const W=e.get(P);if(W.color.copy(P.color).multiplyScalar(P.intensity),W.distance=P.distance,W.decay=P.decay,P.castShadow){const ee=P.shadow,O=t.get(P);O.shadowIntensity=ee.intensity,O.shadowBias=ee.bias,O.shadowNormalBias=ee.normalBias,O.shadowRadius=ee.radius,O.shadowMapSize=ee.mapSize,O.shadowCameraNear=ee.camera.near,O.shadowCameraFar=ee.camera.far,n.pointShadow[m]=O,n.pointShadowMap[m]=j,n.pointShadowMatrix[m]=P.shadow.matrix,v++}n.point[m]=W,m++}else if(P.isHemisphereLight){const W=e.get(P);W.skyColor.copy(P.color).multiplyScalar(B),W.groundColor.copy(P.groundColor).multiplyScalar(B),n.hemi[p]=W,p++}}g>0&&(i.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=me.LTC_FLOAT_1,n.rectAreaLTC2=me.LTC_FLOAT_2):(n.rectAreaLTC1=me.LTC_HALF_1,n.rectAreaLTC2=me.LTC_HALF_2)),n.ambient[0]=u,n.ambient[1]=f,n.ambient[2]=h;const I=n.hash;(I.directionalLength!==d||I.pointLength!==m||I.spotLength!==_||I.rectAreaLength!==g||I.hemiLength!==p||I.numDirectionalShadows!==M||I.numPointShadows!==v||I.numSpotShadows!==x||I.numSpotMaps!==L||I.numLightProbes!==R)&&(n.directional.length=d,n.spot.length=_,n.rectArea.length=g,n.point.length=m,n.hemi.length=p,n.directionalShadow.length=M,n.directionalShadowMap.length=M,n.pointShadow.length=v,n.pointShadowMap.length=v,n.spotShadow.length=x,n.spotShadowMap.length=x,n.directionalShadowMatrix.length=M,n.pointShadowMatrix.length=v,n.spotLightMatrix.length=x+L-T,n.spotLightMap.length=L,n.numSpotLightShadowsWithMaps=T,n.numLightProbes=R,I.directionalLength=d,I.pointLength=m,I.spotLength=_,I.rectAreaLength=g,I.hemiLength=p,I.numDirectionalShadows=M,I.numPointShadows=v,I.numSpotShadows=x,I.numSpotMaps=L,I.numLightProbes=R,n.version=_x++)}function c(l,u){let f=0,h=0,d=0,m=0,_=0;const g=u.matrixWorldInverse;for(let p=0,M=l.length;p<M;p++){const v=l[p];if(v.isDirectionalLight){const x=n.directional[f];x.direction.setFromMatrixPosition(v.matrixWorld),s.setFromMatrixPosition(v.target.matrixWorld),x.direction.sub(s),x.direction.transformDirection(g),f++}else if(v.isSpotLight){const x=n.spot[d];x.position.setFromMatrixPosition(v.matrixWorld),x.position.applyMatrix4(g),x.direction.setFromMatrixPosition(v.matrixWorld),s.setFromMatrixPosition(v.target.matrixWorld),x.direction.sub(s),x.direction.transformDirection(g),d++}else if(v.isRectAreaLight){const x=n.rectArea[m];x.position.setFromMatrixPosition(v.matrixWorld),x.position.applyMatrix4(g),o.identity(),r.copy(v.matrixWorld),r.premultiply(g),o.extractRotation(r),x.halfWidth.set(v.width*.5,0,0),x.halfHeight.set(0,v.height*.5,0),x.halfWidth.applyMatrix4(o),x.halfHeight.applyMatrix4(o),m++}else if(v.isPointLight){const x=n.point[h];x.position.setFromMatrixPosition(v.matrixWorld),x.position.applyMatrix4(g),h++}else if(v.isHemisphereLight){const x=n.hemi[_];x.direction.setFromMatrixPosition(v.matrixWorld),x.direction.transformDirection(g),_++}}}return{setup:a,setupView:c,state:n}}function $u(i){const e=new vx(i),t=[],n=[];function s(u){l.camera=u,t.length=0,n.length=0}function r(u){t.push(u)}function o(u){n.push(u)}function a(){e.setup(t)}function c(u){e.setupView(t,u)}const l={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:s,state:l,setupLights:a,setupLightsView:c,pushLight:r,pushShadow:o}}function yx(i){let e=new WeakMap;function t(s,r=0){const o=e.get(s);let a;return o===void 0?(a=new $u(i),e.set(s,[a])):r>=o.length?(a=new $u(i),o.push(a)):a=o[r],a}function n(){e=new WeakMap}return{get:t,dispose:n}}class Mx extends Hn{static get type(){return"MeshDepthMaterial"}constructor(e){super(),this.isMeshDepthMaterial=!0,this.depthPacking=np,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class Sx extends Hn{static get type(){return"MeshDistanceMaterial"}constructor(e){super(),this.isMeshDistanceMaterial=!0,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const Ex=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,bx=`uniform sampler2D shadow_pass;
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
}`;function wx(i,e,t){let n=new El;const s=new ie,r=new ie,o=new ht,a=new Mx({depthPacking:ip}),c=new Sx,l={},u=t.maxTextureSize,f={[ui]:sn,[sn]:ui,[mn]:mn},h=new Vn({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new ie},radius:{value:4}},vertexShader:Ex,fragmentShader:bx}),d=h.clone();d.defines.HORIZONTAL_PASS=1;const m=new Ft;m.setAttribute("position",new Xt(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const _=new Gt(m,h),g=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=Gh;let p=this.type;this.render=function(T,R,I){if(g.enabled===!1||g.autoUpdate===!1&&g.needsUpdate===!1||T.length===0)return;const w=i.getRenderTarget(),S=i.getActiveCubeFace(),P=i.getActiveMipmapLevel(),G=i.state;G.setBlending(Ii),G.buffers.color.setClear(1,1,1,1),G.buffers.depth.setTest(!0),G.setScissorTest(!1);const B=p!==ni&&this.type===ni,V=p===ni&&this.type!==ni;for(let j=0,W=T.length;j<W;j++){const ee=T[j],O=ee.shadow;if(O===void 0){console.warn("THREE.WebGLShadowMap:",ee,"has no shadow.");continue}if(O.autoUpdate===!1&&O.needsUpdate===!1)continue;s.copy(O.mapSize);const re=O.getFrameExtents();if(s.multiply(re),r.copy(O.mapSize),(s.x>u||s.y>u)&&(s.x>u&&(r.x=Math.floor(u/re.x),s.x=r.x*re.x,O.mapSize.x=r.x),s.y>u&&(r.y=Math.floor(u/re.y),s.y=r.y*re.y,O.mapSize.y=r.y)),O.map===null||B===!0||V===!0){const Me=this.type!==ni?{minFilter:rn,magFilter:rn}:{};O.map!==null&&O.map.dispose(),O.map=new ts(s.x,s.y,Me),O.map.texture.name=ee.name+".shadowMap",O.camera.updateProjectionMatrix()}i.setRenderTarget(O.map),i.clear();const ue=O.getViewportCount();for(let Me=0;Me<ue;Me++){const Ye=O.getViewport(Me);o.set(r.x*Ye.x,r.y*Ye.y,r.x*Ye.z,r.y*Ye.w),G.viewport(o),O.updateMatrices(ee,Me),n=O.getFrustum(),x(R,I,O.camera,ee,this.type)}O.isPointLightShadow!==!0&&this.type===ni&&M(O,I),O.needsUpdate=!1}p=this.type,g.needsUpdate=!1,i.setRenderTarget(w,S,P)};function M(T,R){const I=e.update(_);h.defines.VSM_SAMPLES!==T.blurSamples&&(h.defines.VSM_SAMPLES=T.blurSamples,d.defines.VSM_SAMPLES=T.blurSamples,h.needsUpdate=!0,d.needsUpdate=!0),T.mapPass===null&&(T.mapPass=new ts(s.x,s.y)),h.uniforms.shadow_pass.value=T.map.texture,h.uniforms.resolution.value=T.mapSize,h.uniforms.radius.value=T.radius,i.setRenderTarget(T.mapPass),i.clear(),i.renderBufferDirect(R,null,I,h,_,null),d.uniforms.shadow_pass.value=T.mapPass.texture,d.uniforms.resolution.value=T.mapSize,d.uniforms.radius.value=T.radius,i.setRenderTarget(T.map),i.clear(),i.renderBufferDirect(R,null,I,d,_,null)}function v(T,R,I,w){let S=null;const P=I.isPointLight===!0?T.customDistanceMaterial:T.customDepthMaterial;if(P!==void 0)S=P;else if(S=I.isPointLight===!0?c:a,i.localClippingEnabled&&R.clipShadows===!0&&Array.isArray(R.clippingPlanes)&&R.clippingPlanes.length!==0||R.displacementMap&&R.displacementScale!==0||R.alphaMap&&R.alphaTest>0||R.map&&R.alphaTest>0){const G=S.uuid,B=R.uuid;let V=l[G];V===void 0&&(V={},l[G]=V);let j=V[B];j===void 0&&(j=S.clone(),V[B]=j,R.addEventListener("dispose",L)),S=j}if(S.visible=R.visible,S.wireframe=R.wireframe,w===ni?S.side=R.shadowSide!==null?R.shadowSide:R.side:S.side=R.shadowSide!==null?R.shadowSide:f[R.side],S.alphaMap=R.alphaMap,S.alphaTest=R.alphaTest,S.map=R.map,S.clipShadows=R.clipShadows,S.clippingPlanes=R.clippingPlanes,S.clipIntersection=R.clipIntersection,S.displacementMap=R.displacementMap,S.displacementScale=R.displacementScale,S.displacementBias=R.displacementBias,S.wireframeLinewidth=R.wireframeLinewidth,S.linewidth=R.linewidth,I.isPointLight===!0&&S.isMeshDistanceMaterial===!0){const G=i.properties.get(S);G.light=I}return S}function x(T,R,I,w,S){if(T.visible===!1)return;if(T.layers.test(R.layers)&&(T.isMesh||T.isLine||T.isPoints)&&(T.castShadow||T.receiveShadow&&S===ni)&&(!T.frustumCulled||n.intersectsObject(T))){T.modelViewMatrix.multiplyMatrices(I.matrixWorldInverse,T.matrixWorld);const B=e.update(T),V=T.material;if(Array.isArray(V)){const j=B.groups;for(let W=0,ee=j.length;W<ee;W++){const O=j[W],re=V[O.materialIndex];if(re&&re.visible){const ue=v(T,re,w,S);T.onBeforeShadow(i,T,R,I,B,ue,O),i.renderBufferDirect(I,null,B,ue,T,O),T.onAfterShadow(i,T,R,I,B,ue,O)}}}else if(V.visible){const j=v(T,V,w,S);T.onBeforeShadow(i,T,R,I,B,j,null),i.renderBufferDirect(I,null,B,j,T,null),T.onAfterShadow(i,T,R,I,B,j,null)}}const G=T.children;for(let B=0,V=G.length;B<V;B++)x(G[B],R,I,w,S)}function L(T){T.target.removeEventListener("dispose",L);for(const I in l){const w=l[I],S=T.target.uuid;S in w&&(w[S].dispose(),delete w[S])}}}const Tx={[gc]:_c,[xc]:Mc,[vc]:Sc,[Fs]:yc,[_c]:gc,[Mc]:xc,[Sc]:vc,[yc]:Fs};function Ax(i,e){function t(){let D=!1;const xe=new ht;let X=null;const K=new ht(0,0,0,0);return{setMask:function(Se){X!==Se&&!D&&(i.colorMask(Se,Se,Se,Se),X=Se)},setLocked:function(Se){D=Se},setClear:function(Se,ve,Je,Lt,Kt){Kt===!0&&(Se*=Lt,ve*=Lt,Je*=Lt),xe.set(Se,ve,Je,Lt),K.equals(xe)===!1&&(i.clearColor(Se,ve,Je,Lt),K.copy(xe))},reset:function(){D=!1,X=null,K.set(-1,0,0,0)}}}function n(){let D=!1,xe=!1,X=null,K=null,Se=null;return{setReversed:function(ve){if(xe!==ve){const Je=e.get("EXT_clip_control");xe?Je.clipControlEXT(Je.LOWER_LEFT_EXT,Je.ZERO_TO_ONE_EXT):Je.clipControlEXT(Je.LOWER_LEFT_EXT,Je.NEGATIVE_ONE_TO_ONE_EXT);const Lt=Se;Se=null,this.setClear(Lt)}xe=ve},getReversed:function(){return xe},setTest:function(ve){ve?fe(i.DEPTH_TEST):ze(i.DEPTH_TEST)},setMask:function(ve){X!==ve&&!D&&(i.depthMask(ve),X=ve)},setFunc:function(ve){if(xe&&(ve=Tx[ve]),K!==ve){switch(ve){case gc:i.depthFunc(i.NEVER);break;case _c:i.depthFunc(i.ALWAYS);break;case xc:i.depthFunc(i.LESS);break;case Fs:i.depthFunc(i.LEQUAL);break;case vc:i.depthFunc(i.EQUAL);break;case yc:i.depthFunc(i.GEQUAL);break;case Mc:i.depthFunc(i.GREATER);break;case Sc:i.depthFunc(i.NOTEQUAL);break;default:i.depthFunc(i.LEQUAL)}K=ve}},setLocked:function(ve){D=ve},setClear:function(ve){Se!==ve&&(xe&&(ve=1-ve),i.clearDepth(ve),Se=ve)},reset:function(){D=!1,X=null,K=null,Se=null,xe=!1}}}function s(){let D=!1,xe=null,X=null,K=null,Se=null,ve=null,Je=null,Lt=null,Kt=null;return{setTest:function(gt){D||(gt?fe(i.STENCIL_TEST):ze(i.STENCIL_TEST))},setMask:function(gt){xe!==gt&&!D&&(i.stencilMask(gt),xe=gt)},setFunc:function(gt,An,Yn){(X!==gt||K!==An||Se!==Yn)&&(i.stencilFunc(gt,An,Yn),X=gt,K=An,Se=Yn)},setOp:function(gt,An,Yn){(ve!==gt||Je!==An||Lt!==Yn)&&(i.stencilOp(gt,An,Yn),ve=gt,Je=An,Lt=Yn)},setLocked:function(gt){D=gt},setClear:function(gt){Kt!==gt&&(i.clearStencil(gt),Kt=gt)},reset:function(){D=!1,xe=null,X=null,K=null,Se=null,ve=null,Je=null,Lt=null,Kt=null}}}const r=new t,o=new n,a=new s,c=new WeakMap,l=new WeakMap;let u={},f={},h=new WeakMap,d=[],m=null,_=!1,g=null,p=null,M=null,v=null,x=null,L=null,T=null,R=new Ve(0,0,0),I=0,w=!1,S=null,P=null,G=null,B=null,V=null;const j=i.getParameter(i.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let W=!1,ee=0;const O=i.getParameter(i.VERSION);O.indexOf("WebGL")!==-1?(ee=parseFloat(/^WebGL (\d)/.exec(O)[1]),W=ee>=1):O.indexOf("OpenGL ES")!==-1&&(ee=parseFloat(/^OpenGL ES (\d)/.exec(O)[1]),W=ee>=2);let re=null,ue={};const Me=i.getParameter(i.SCISSOR_BOX),Ye=i.getParameter(i.VIEWPORT),dt=new ht().fromArray(Me),$=new ht().fromArray(Ye);function ce(D,xe,X,K){const Se=new Uint8Array(4),ve=i.createTexture();i.bindTexture(D,ve),i.texParameteri(D,i.TEXTURE_MIN_FILTER,i.NEAREST),i.texParameteri(D,i.TEXTURE_MAG_FILTER,i.NEAREST);for(let Je=0;Je<X;Je++)D===i.TEXTURE_3D||D===i.TEXTURE_2D_ARRAY?i.texImage3D(xe,0,i.RGBA,1,1,K,0,i.RGBA,i.UNSIGNED_BYTE,Se):i.texImage2D(xe+Je,0,i.RGBA,1,1,0,i.RGBA,i.UNSIGNED_BYTE,Se);return ve}const Pe={};Pe[i.TEXTURE_2D]=ce(i.TEXTURE_2D,i.TEXTURE_2D,1),Pe[i.TEXTURE_CUBE_MAP]=ce(i.TEXTURE_CUBE_MAP,i.TEXTURE_CUBE_MAP_POSITIVE_X,6),Pe[i.TEXTURE_2D_ARRAY]=ce(i.TEXTURE_2D_ARRAY,i.TEXTURE_2D_ARRAY,1,1),Pe[i.TEXTURE_3D]=ce(i.TEXTURE_3D,i.TEXTURE_3D,1,1),r.setClear(0,0,0,1),o.setClear(1),a.setClear(0),fe(i.DEPTH_TEST),o.setFunc(Fs),ne(!1),we($l),fe(i.CULL_FACE),C(Ii);function fe(D){u[D]!==!0&&(i.enable(D),u[D]=!0)}function ze(D){u[D]!==!1&&(i.disable(D),u[D]=!1)}function $e(D,xe){return f[D]!==xe?(i.bindFramebuffer(D,xe),f[D]=xe,D===i.DRAW_FRAMEBUFFER&&(f[i.FRAMEBUFFER]=xe),D===i.FRAMEBUFFER&&(f[i.DRAW_FRAMEBUFFER]=xe),!0):!1}function qe(D,xe){let X=d,K=!1;if(D){X=h.get(xe),X===void 0&&(X=[],h.set(xe,X));const Se=D.textures;if(X.length!==Se.length||X[0]!==i.COLOR_ATTACHMENT0){for(let ve=0,Je=Se.length;ve<Je;ve++)X[ve]=i.COLOR_ATTACHMENT0+ve;X.length=Se.length,K=!0}}else X[0]!==i.BACK&&(X[0]=i.BACK,K=!0);K&&i.drawBuffers(X)}function ct(D){return m!==D?(i.useProgram(D),m=D,!0):!1}const J={[Ji]:i.FUNC_ADD,[Ad]:i.FUNC_SUBTRACT,[Rd]:i.FUNC_REVERSE_SUBTRACT};J[Cd]=i.MIN,J[Pd]=i.MAX;const oe={[Ld]:i.ZERO,[Id]:i.ONE,[Dd]:i.SRC_COLOR,[pc]:i.SRC_ALPHA,[kd]:i.SRC_ALPHA_SATURATE,[Fd]:i.DST_COLOR,[Ud]:i.DST_ALPHA,[Nd]:i.ONE_MINUS_SRC_COLOR,[mc]:i.ONE_MINUS_SRC_ALPHA,[Bd]:i.ONE_MINUS_DST_COLOR,[Od]:i.ONE_MINUS_DST_ALPHA,[zd]:i.CONSTANT_COLOR,[Hd]:i.ONE_MINUS_CONSTANT_COLOR,[Vd]:i.CONSTANT_ALPHA,[Gd]:i.ONE_MINUS_CONSTANT_ALPHA};function C(D,xe,X,K,Se,ve,Je,Lt,Kt,gt){if(D===Ii){_===!0&&(ze(i.BLEND),_=!1);return}if(_===!1&&(fe(i.BLEND),_=!0),D!==Td){if(D!==g||gt!==w){if((p!==Ji||x!==Ji)&&(i.blendEquation(i.FUNC_ADD),p=Ji,x=Ji),gt)switch(D){case Ls:i.blendFuncSeparate(i.ONE,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Kl:i.blendFunc(i.ONE,i.ONE);break;case Zl:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Jl:i.blendFuncSeparate(i.ZERO,i.SRC_COLOR,i.ZERO,i.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",D);break}else switch(D){case Ls:i.blendFuncSeparate(i.SRC_ALPHA,i.ONE_MINUS_SRC_ALPHA,i.ONE,i.ONE_MINUS_SRC_ALPHA);break;case Kl:i.blendFunc(i.SRC_ALPHA,i.ONE);break;case Zl:i.blendFuncSeparate(i.ZERO,i.ONE_MINUS_SRC_COLOR,i.ZERO,i.ONE);break;case Jl:i.blendFunc(i.ZERO,i.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",D);break}M=null,v=null,L=null,T=null,R.set(0,0,0),I=0,g=D,w=gt}return}Se=Se||xe,ve=ve||X,Je=Je||K,(xe!==p||Se!==x)&&(i.blendEquationSeparate(J[xe],J[Se]),p=xe,x=Se),(X!==M||K!==v||ve!==L||Je!==T)&&(i.blendFuncSeparate(oe[X],oe[K],oe[ve],oe[Je]),M=X,v=K,L=ve,T=Je),(Lt.equals(R)===!1||Kt!==I)&&(i.blendColor(Lt.r,Lt.g,Lt.b,Kt),R.copy(Lt),I=Kt),g=D,w=!1}function Fe(D,xe){D.side===mn?ze(i.CULL_FACE):fe(i.CULL_FACE);let X=D.side===sn;xe&&(X=!X),ne(X),D.blending===Ls&&D.transparent===!1?C(Ii):C(D.blending,D.blendEquation,D.blendSrc,D.blendDst,D.blendEquationAlpha,D.blendSrcAlpha,D.blendDstAlpha,D.blendColor,D.blendAlpha,D.premultipliedAlpha),o.setFunc(D.depthFunc),o.setTest(D.depthTest),o.setMask(D.depthWrite),r.setMask(D.colorWrite);const K=D.stencilWrite;a.setTest(K),K&&(a.setMask(D.stencilWriteMask),a.setFunc(D.stencilFunc,D.stencilRef,D.stencilFuncMask),a.setOp(D.stencilFail,D.stencilZFail,D.stencilZPass)),We(D.polygonOffset,D.polygonOffsetFactor,D.polygonOffsetUnits),D.alphaToCoverage===!0?fe(i.SAMPLE_ALPHA_TO_COVERAGE):ze(i.SAMPLE_ALPHA_TO_COVERAGE)}function ne(D){S!==D&&(D?i.frontFace(i.CW):i.frontFace(i.CCW),S=D)}function we(D){D!==Ed?(fe(i.CULL_FACE),D!==P&&(D===$l?i.cullFace(i.BACK):D===bd?i.cullFace(i.FRONT):i.cullFace(i.FRONT_AND_BACK))):ze(i.CULL_FACE),P=D}function de(D){D!==G&&(W&&i.lineWidth(D),G=D)}function We(D,xe,X){D?(fe(i.POLYGON_OFFSET_FILL),(B!==xe||V!==X)&&(i.polygonOffset(xe,X),B=xe,V=X)):ze(i.POLYGON_OFFSET_FILL)}function Ee(D){D?fe(i.SCISSOR_TEST):ze(i.SCISSOR_TEST)}function A(D){D===void 0&&(D=i.TEXTURE0+j-1),re!==D&&(i.activeTexture(D),re=D)}function y(D,xe,X){X===void 0&&(re===null?X=i.TEXTURE0+j-1:X=re);let K=ue[X];K===void 0&&(K={type:void 0,texture:void 0},ue[X]=K),(K.type!==D||K.texture!==xe)&&(re!==X&&(i.activeTexture(X),re=X),i.bindTexture(D,xe||Pe[D]),K.type=D,K.texture=xe)}function F(){const D=ue[re];D!==void 0&&D.type!==void 0&&(i.bindTexture(D.type,null),D.type=void 0,D.texture=void 0)}function q(){try{i.compressedTexImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Q(){try{i.compressedTexImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Y(){try{i.texSubImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Ie(){try{i.texSubImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function ge(){try{i.compressedTexSubImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function be(){try{i.compressedTexSubImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function rt(){try{i.texStorage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function se(){try{i.texStorage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Ae(){try{i.texImage2D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function Xe(){try{i.texImage3D.apply(i,arguments)}catch(D){console.error("THREE.WebGLState:",D)}}function je(D){dt.equals(D)===!1&&(i.scissor(D.x,D.y,D.z,D.w),dt.copy(D))}function Re(D){$.equals(D)===!1&&(i.viewport(D.x,D.y,D.z,D.w),$.copy(D))}function at(D,xe){let X=l.get(xe);X===void 0&&(X=new WeakMap,l.set(xe,X));let K=X.get(D);K===void 0&&(K=i.getUniformBlockIndex(xe,D.name),X.set(D,K))}function tt(D,xe){const K=l.get(xe).get(D);c.get(xe)!==K&&(i.uniformBlockBinding(xe,K,D.__bindingPointIndex),c.set(xe,K))}function St(){i.disable(i.BLEND),i.disable(i.CULL_FACE),i.disable(i.DEPTH_TEST),i.disable(i.POLYGON_OFFSET_FILL),i.disable(i.SCISSOR_TEST),i.disable(i.STENCIL_TEST),i.disable(i.SAMPLE_ALPHA_TO_COVERAGE),i.blendEquation(i.FUNC_ADD),i.blendFunc(i.ONE,i.ZERO),i.blendFuncSeparate(i.ONE,i.ZERO,i.ONE,i.ZERO),i.blendColor(0,0,0,0),i.colorMask(!0,!0,!0,!0),i.clearColor(0,0,0,0),i.depthMask(!0),i.depthFunc(i.LESS),o.setReversed(!1),i.clearDepth(1),i.stencilMask(4294967295),i.stencilFunc(i.ALWAYS,0,4294967295),i.stencilOp(i.KEEP,i.KEEP,i.KEEP),i.clearStencil(0),i.cullFace(i.BACK),i.frontFace(i.CCW),i.polygonOffset(0,0),i.activeTexture(i.TEXTURE0),i.bindFramebuffer(i.FRAMEBUFFER,null),i.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),i.bindFramebuffer(i.READ_FRAMEBUFFER,null),i.useProgram(null),i.lineWidth(1),i.scissor(0,0,i.canvas.width,i.canvas.height),i.viewport(0,0,i.canvas.width,i.canvas.height),u={},re=null,ue={},f={},h=new WeakMap,d=[],m=null,_=!1,g=null,p=null,M=null,v=null,x=null,L=null,T=null,R=new Ve(0,0,0),I=0,w=!1,S=null,P=null,G=null,B=null,V=null,dt.set(0,0,i.canvas.width,i.canvas.height),$.set(0,0,i.canvas.width,i.canvas.height),r.reset(),o.reset(),a.reset()}return{buffers:{color:r,depth:o,stencil:a},enable:fe,disable:ze,bindFramebuffer:$e,drawBuffers:qe,useProgram:ct,setBlending:C,setMaterial:Fe,setFlipSided:ne,setCullFace:we,setLineWidth:de,setPolygonOffset:We,setScissorTest:Ee,activeTexture:A,bindTexture:y,unbindTexture:F,compressedTexImage2D:q,compressedTexImage3D:Q,texImage2D:Ae,texImage3D:Xe,updateUBOMapping:at,uniformBlockBinding:tt,texStorage2D:rt,texStorage3D:se,texSubImage2D:Y,texSubImage3D:Ie,compressedTexSubImage2D:ge,compressedTexSubImage3D:be,scissor:je,viewport:Re,reset:St}}function Ku(i,e,t,n){const s=Rx(n);switch(t){case Kh:return i*e;case Jh:return i*e;case Qh:return i*e*2;case _l:return i*e/s.components*s.byteLength;case xl:return i*e/s.components*s.byteLength;case ef:return i*e*2/s.components*s.byteLength;case vl:return i*e*2/s.components*s.byteLength;case Zh:return i*e*3/s.components*s.byteLength;case bn:return i*e*4/s.components*s.byteLength;case yl:return i*e*4/s.components*s.byteLength;case Ro:case Co:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case Po:case Lo:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Tc:case Rc:return Math.max(i,16)*Math.max(e,8)/4;case wc:case Ac:return Math.max(i,8)*Math.max(e,8)/2;case Cc:case Pc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*8;case Lc:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Ic:return Math.floor((i+3)/4)*Math.floor((e+3)/4)*16;case Dc:return Math.floor((i+4)/5)*Math.floor((e+3)/4)*16;case Nc:return Math.floor((i+4)/5)*Math.floor((e+4)/5)*16;case Uc:return Math.floor((i+5)/6)*Math.floor((e+4)/5)*16;case Oc:return Math.floor((i+5)/6)*Math.floor((e+5)/6)*16;case Fc:return Math.floor((i+7)/8)*Math.floor((e+4)/5)*16;case Bc:return Math.floor((i+7)/8)*Math.floor((e+5)/6)*16;case kc:return Math.floor((i+7)/8)*Math.floor((e+7)/8)*16;case zc:return Math.floor((i+9)/10)*Math.floor((e+4)/5)*16;case Hc:return Math.floor((i+9)/10)*Math.floor((e+5)/6)*16;case Vc:return Math.floor((i+9)/10)*Math.floor((e+7)/8)*16;case Gc:return Math.floor((i+9)/10)*Math.floor((e+9)/10)*16;case Wc:return Math.floor((i+11)/12)*Math.floor((e+9)/10)*16;case Xc:return Math.floor((i+11)/12)*Math.floor((e+11)/12)*16;case Io:case qc:case Yc:return Math.ceil(i/4)*Math.ceil(e/4)*16;case tf:case jc:return Math.ceil(i/4)*Math.ceil(e/4)*8;case $c:case Kc:return Math.ceil(i/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function Rx(i){switch(i){case hi:case Yh:return{byteLength:1,components:1};case Tr:case jh:case Dr:return{byteLength:2,components:1};case ml:case gl:return{byteLength:2,components:4};case es:case pl:case Dn:return{byteLength:4,components:1};case $h:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${i}.`)}function Cx(i,e,t,n,s,r,o){const a=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,c=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),l=new ie,u=new WeakMap;let f;const h=new WeakMap;let d=!1;try{d=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function m(A,y){return d?new OffscreenCanvas(A,y):Cr("canvas")}function _(A,y,F){let q=1;const Q=Ee(A);if((Q.width>F||Q.height>F)&&(q=F/Math.max(Q.width,Q.height)),q<1)if(typeof HTMLImageElement<"u"&&A instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&A instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&A instanceof ImageBitmap||typeof VideoFrame<"u"&&A instanceof VideoFrame){const Y=Math.floor(q*Q.width),Ie=Math.floor(q*Q.height);f===void 0&&(f=m(Y,Ie));const ge=y?m(Y,Ie):f;return ge.width=Y,ge.height=Ie,ge.getContext("2d").drawImage(A,0,0,Y,Ie),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+Q.width+"x"+Q.height+") to ("+Y+"x"+Ie+")."),ge}else return"data"in A&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+Q.width+"x"+Q.height+")."),A;return A}function g(A){return A.generateMipmaps}function p(A){i.generateMipmap(A)}function M(A){return A.isWebGLCubeRenderTarget?i.TEXTURE_CUBE_MAP:A.isWebGL3DRenderTarget?i.TEXTURE_3D:A.isWebGLArrayRenderTarget||A.isCompressedArrayTexture?i.TEXTURE_2D_ARRAY:i.TEXTURE_2D}function v(A,y,F,q,Q=!1){if(A!==null){if(i[A]!==void 0)return i[A];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+A+"'")}let Y=y;if(y===i.RED&&(F===i.FLOAT&&(Y=i.R32F),F===i.HALF_FLOAT&&(Y=i.R16F),F===i.UNSIGNED_BYTE&&(Y=i.R8)),y===i.RED_INTEGER&&(F===i.UNSIGNED_BYTE&&(Y=i.R8UI),F===i.UNSIGNED_SHORT&&(Y=i.R16UI),F===i.UNSIGNED_INT&&(Y=i.R32UI),F===i.BYTE&&(Y=i.R8I),F===i.SHORT&&(Y=i.R16I),F===i.INT&&(Y=i.R32I)),y===i.RG&&(F===i.FLOAT&&(Y=i.RG32F),F===i.HALF_FLOAT&&(Y=i.RG16F),F===i.UNSIGNED_BYTE&&(Y=i.RG8)),y===i.RG_INTEGER&&(F===i.UNSIGNED_BYTE&&(Y=i.RG8UI),F===i.UNSIGNED_SHORT&&(Y=i.RG16UI),F===i.UNSIGNED_INT&&(Y=i.RG32UI),F===i.BYTE&&(Y=i.RG8I),F===i.SHORT&&(Y=i.RG16I),F===i.INT&&(Y=i.RG32I)),y===i.RGB_INTEGER&&(F===i.UNSIGNED_BYTE&&(Y=i.RGB8UI),F===i.UNSIGNED_SHORT&&(Y=i.RGB16UI),F===i.UNSIGNED_INT&&(Y=i.RGB32UI),F===i.BYTE&&(Y=i.RGB8I),F===i.SHORT&&(Y=i.RGB16I),F===i.INT&&(Y=i.RGB32I)),y===i.RGBA_INTEGER&&(F===i.UNSIGNED_BYTE&&(Y=i.RGBA8UI),F===i.UNSIGNED_SHORT&&(Y=i.RGBA16UI),F===i.UNSIGNED_INT&&(Y=i.RGBA32UI),F===i.BYTE&&(Y=i.RGBA8I),F===i.SHORT&&(Y=i.RGBA16I),F===i.INT&&(Y=i.RGBA32I)),y===i.RGB&&F===i.UNSIGNED_INT_5_9_9_9_REV&&(Y=i.RGB9_E5),y===i.RGBA){const Ie=Q?$o:ot.getTransfer(q);F===i.FLOAT&&(Y=i.RGBA32F),F===i.HALF_FLOAT&&(Y=i.RGBA16F),F===i.UNSIGNED_BYTE&&(Y=Ie===yt?i.SRGB8_ALPHA8:i.RGBA8),F===i.UNSIGNED_SHORT_4_4_4_4&&(Y=i.RGBA4),F===i.UNSIGNED_SHORT_5_5_5_1&&(Y=i.RGB5_A1)}return(Y===i.R16F||Y===i.R32F||Y===i.RG16F||Y===i.RG32F||Y===i.RGBA16F||Y===i.RGBA32F)&&e.get("EXT_color_buffer_float"),Y}function x(A,y){let F;return A?y===null||y===es||y===Hs?F=i.DEPTH24_STENCIL8:y===Dn?F=i.DEPTH32F_STENCIL8:y===Tr&&(F=i.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):y===null||y===es||y===Hs?F=i.DEPTH_COMPONENT24:y===Dn?F=i.DEPTH_COMPONENT32F:y===Tr&&(F=i.DEPTH_COMPONENT16),F}function L(A,y){return g(A)===!0||A.isFramebufferTexture&&A.minFilter!==rn&&A.minFilter!==gn?Math.log2(Math.max(y.width,y.height))+1:A.mipmaps!==void 0&&A.mipmaps.length>0?A.mipmaps.length:A.isCompressedTexture&&Array.isArray(A.image)?y.mipmaps.length:1}function T(A){const y=A.target;y.removeEventListener("dispose",T),I(y),y.isVideoTexture&&u.delete(y)}function R(A){const y=A.target;y.removeEventListener("dispose",R),S(y)}function I(A){const y=n.get(A);if(y.__webglInit===void 0)return;const F=A.source,q=h.get(F);if(q){const Q=q[y.__cacheKey];Q.usedTimes--,Q.usedTimes===0&&w(A),Object.keys(q).length===0&&h.delete(F)}n.remove(A)}function w(A){const y=n.get(A);i.deleteTexture(y.__webglTexture);const F=A.source,q=h.get(F);delete q[y.__cacheKey],o.memory.textures--}function S(A){const y=n.get(A);if(A.depthTexture&&(A.depthTexture.dispose(),n.remove(A.depthTexture)),A.isWebGLCubeRenderTarget)for(let q=0;q<6;q++){if(Array.isArray(y.__webglFramebuffer[q]))for(let Q=0;Q<y.__webglFramebuffer[q].length;Q++)i.deleteFramebuffer(y.__webglFramebuffer[q][Q]);else i.deleteFramebuffer(y.__webglFramebuffer[q]);y.__webglDepthbuffer&&i.deleteRenderbuffer(y.__webglDepthbuffer[q])}else{if(Array.isArray(y.__webglFramebuffer))for(let q=0;q<y.__webglFramebuffer.length;q++)i.deleteFramebuffer(y.__webglFramebuffer[q]);else i.deleteFramebuffer(y.__webglFramebuffer);if(y.__webglDepthbuffer&&i.deleteRenderbuffer(y.__webglDepthbuffer),y.__webglMultisampledFramebuffer&&i.deleteFramebuffer(y.__webglMultisampledFramebuffer),y.__webglColorRenderbuffer)for(let q=0;q<y.__webglColorRenderbuffer.length;q++)y.__webglColorRenderbuffer[q]&&i.deleteRenderbuffer(y.__webglColorRenderbuffer[q]);y.__webglDepthRenderbuffer&&i.deleteRenderbuffer(y.__webglDepthRenderbuffer)}const F=A.textures;for(let q=0,Q=F.length;q<Q;q++){const Y=n.get(F[q]);Y.__webglTexture&&(i.deleteTexture(Y.__webglTexture),o.memory.textures--),n.remove(F[q])}n.remove(A)}let P=0;function G(){P=0}function B(){const A=P;return A>=s.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+A+" texture units while this GPU supports only "+s.maxTextures),P+=1,A}function V(A){const y=[];return y.push(A.wrapS),y.push(A.wrapT),y.push(A.wrapR||0),y.push(A.magFilter),y.push(A.minFilter),y.push(A.anisotropy),y.push(A.internalFormat),y.push(A.format),y.push(A.type),y.push(A.generateMipmaps),y.push(A.premultiplyAlpha),y.push(A.flipY),y.push(A.unpackAlignment),y.push(A.colorSpace),y.join()}function j(A,y){const F=n.get(A);if(A.isVideoTexture&&de(A),A.isRenderTargetTexture===!1&&A.version>0&&F.__version!==A.version){const q=A.image;if(q===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(q.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{$(F,A,y);return}}t.bindTexture(i.TEXTURE_2D,F.__webglTexture,i.TEXTURE0+y)}function W(A,y){const F=n.get(A);if(A.version>0&&F.__version!==A.version){$(F,A,y);return}t.bindTexture(i.TEXTURE_2D_ARRAY,F.__webglTexture,i.TEXTURE0+y)}function ee(A,y){const F=n.get(A);if(A.version>0&&F.__version!==A.version){$(F,A,y);return}t.bindTexture(i.TEXTURE_3D,F.__webglTexture,i.TEXTURE0+y)}function O(A,y){const F=n.get(A);if(A.version>0&&F.__version!==A.version){ce(F,A,y);return}t.bindTexture(i.TEXTURE_CUBE_MAP,F.__webglTexture,i.TEXTURE0+y)}const re={[zs]:i.REPEAT,[Ai]:i.CLAMP_TO_EDGE,[Fo]:i.MIRRORED_REPEAT},ue={[rn]:i.NEAREST,[qh]:i.NEAREST_MIPMAP_NEAREST,[xr]:i.NEAREST_MIPMAP_LINEAR,[gn]:i.LINEAR,[Ao]:i.LINEAR_MIPMAP_NEAREST,[oi]:i.LINEAR_MIPMAP_LINEAR},Me={[rp]:i.NEVER,[hp]:i.ALWAYS,[op]:i.LESS,[rf]:i.LEQUAL,[ap]:i.EQUAL,[up]:i.GEQUAL,[cp]:i.GREATER,[lp]:i.NOTEQUAL};function Ye(A,y){if(y.type===Dn&&e.has("OES_texture_float_linear")===!1&&(y.magFilter===gn||y.magFilter===Ao||y.magFilter===xr||y.magFilter===oi||y.minFilter===gn||y.minFilter===Ao||y.minFilter===xr||y.minFilter===oi)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),i.texParameteri(A,i.TEXTURE_WRAP_S,re[y.wrapS]),i.texParameteri(A,i.TEXTURE_WRAP_T,re[y.wrapT]),(A===i.TEXTURE_3D||A===i.TEXTURE_2D_ARRAY)&&i.texParameteri(A,i.TEXTURE_WRAP_R,re[y.wrapR]),i.texParameteri(A,i.TEXTURE_MAG_FILTER,ue[y.magFilter]),i.texParameteri(A,i.TEXTURE_MIN_FILTER,ue[y.minFilter]),y.compareFunction&&(i.texParameteri(A,i.TEXTURE_COMPARE_MODE,i.COMPARE_REF_TO_TEXTURE),i.texParameteri(A,i.TEXTURE_COMPARE_FUNC,Me[y.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(y.magFilter===rn||y.minFilter!==xr&&y.minFilter!==oi||y.type===Dn&&e.has("OES_texture_float_linear")===!1)return;if(y.anisotropy>1||n.get(y).__currentAnisotropy){const F=e.get("EXT_texture_filter_anisotropic");i.texParameterf(A,F.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(y.anisotropy,s.getMaxAnisotropy())),n.get(y).__currentAnisotropy=y.anisotropy}}}function dt(A,y){let F=!1;A.__webglInit===void 0&&(A.__webglInit=!0,y.addEventListener("dispose",T));const q=y.source;let Q=h.get(q);Q===void 0&&(Q={},h.set(q,Q));const Y=V(y);if(Y!==A.__cacheKey){Q[Y]===void 0&&(Q[Y]={texture:i.createTexture(),usedTimes:0},o.memory.textures++,F=!0),Q[Y].usedTimes++;const Ie=Q[A.__cacheKey];Ie!==void 0&&(Q[A.__cacheKey].usedTimes--,Ie.usedTimes===0&&w(y)),A.__cacheKey=Y,A.__webglTexture=Q[Y].texture}return F}function $(A,y,F){let q=i.TEXTURE_2D;(y.isDataArrayTexture||y.isCompressedArrayTexture)&&(q=i.TEXTURE_2D_ARRAY),y.isData3DTexture&&(q=i.TEXTURE_3D);const Q=dt(A,y),Y=y.source;t.bindTexture(q,A.__webglTexture,i.TEXTURE0+F);const Ie=n.get(Y);if(Y.version!==Ie.__version||Q===!0){t.activeTexture(i.TEXTURE0+F);const ge=ot.getPrimaries(ot.workingColorSpace),be=y.colorSpace===wi?null:ot.getPrimaries(y.colorSpace),rt=y.colorSpace===wi||ge===be?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,y.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,y.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,y.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,rt);let se=_(y.image,!1,s.maxTextureSize);se=We(y,se);const Ae=r.convert(y.format,y.colorSpace),Xe=r.convert(y.type);let je=v(y.internalFormat,Ae,Xe,y.colorSpace,y.isVideoTexture);Ye(q,y);let Re;const at=y.mipmaps,tt=y.isVideoTexture!==!0,St=Ie.__version===void 0||Q===!0,D=Y.dataReady,xe=L(y,se);if(y.isDepthTexture)je=x(y.format===Vs,y.type),St&&(tt?t.texStorage2D(i.TEXTURE_2D,1,je,se.width,se.height):t.texImage2D(i.TEXTURE_2D,0,je,se.width,se.height,0,Ae,Xe,null));else if(y.isDataTexture)if(at.length>0){tt&&St&&t.texStorage2D(i.TEXTURE_2D,xe,je,at[0].width,at[0].height);for(let X=0,K=at.length;X<K;X++)Re=at[X],tt?D&&t.texSubImage2D(i.TEXTURE_2D,X,0,0,Re.width,Re.height,Ae,Xe,Re.data):t.texImage2D(i.TEXTURE_2D,X,je,Re.width,Re.height,0,Ae,Xe,Re.data);y.generateMipmaps=!1}else tt?(St&&t.texStorage2D(i.TEXTURE_2D,xe,je,se.width,se.height),D&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,se.width,se.height,Ae,Xe,se.data)):t.texImage2D(i.TEXTURE_2D,0,je,se.width,se.height,0,Ae,Xe,se.data);else if(y.isCompressedTexture)if(y.isCompressedArrayTexture){tt&&St&&t.texStorage3D(i.TEXTURE_2D_ARRAY,xe,je,at[0].width,at[0].height,se.depth);for(let X=0,K=at.length;X<K;X++)if(Re=at[X],y.format!==bn)if(Ae!==null)if(tt){if(D)if(y.layerUpdates.size>0){const Se=Ku(Re.width,Re.height,y.format,y.type);for(const ve of y.layerUpdates){const Je=Re.data.subarray(ve*Se/Re.data.BYTES_PER_ELEMENT,(ve+1)*Se/Re.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,X,0,0,ve,Re.width,Re.height,1,Ae,Je)}y.clearLayerUpdates()}else t.compressedTexSubImage3D(i.TEXTURE_2D_ARRAY,X,0,0,0,Re.width,Re.height,se.depth,Ae,Re.data)}else t.compressedTexImage3D(i.TEXTURE_2D_ARRAY,X,je,Re.width,Re.height,se.depth,0,Re.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else tt?D&&t.texSubImage3D(i.TEXTURE_2D_ARRAY,X,0,0,0,Re.width,Re.height,se.depth,Ae,Xe,Re.data):t.texImage3D(i.TEXTURE_2D_ARRAY,X,je,Re.width,Re.height,se.depth,0,Ae,Xe,Re.data)}else{tt&&St&&t.texStorage2D(i.TEXTURE_2D,xe,je,at[0].width,at[0].height);for(let X=0,K=at.length;X<K;X++)Re=at[X],y.format!==bn?Ae!==null?tt?D&&t.compressedTexSubImage2D(i.TEXTURE_2D,X,0,0,Re.width,Re.height,Ae,Re.data):t.compressedTexImage2D(i.TEXTURE_2D,X,je,Re.width,Re.height,0,Re.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):tt?D&&t.texSubImage2D(i.TEXTURE_2D,X,0,0,Re.width,Re.height,Ae,Xe,Re.data):t.texImage2D(i.TEXTURE_2D,X,je,Re.width,Re.height,0,Ae,Xe,Re.data)}else if(y.isDataArrayTexture)if(tt){if(St&&t.texStorage3D(i.TEXTURE_2D_ARRAY,xe,je,se.width,se.height,se.depth),D)if(y.layerUpdates.size>0){const X=Ku(se.width,se.height,y.format,y.type);for(const K of y.layerUpdates){const Se=se.data.subarray(K*X/se.data.BYTES_PER_ELEMENT,(K+1)*X/se.data.BYTES_PER_ELEMENT);t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,K,se.width,se.height,1,Ae,Xe,Se)}y.clearLayerUpdates()}else t.texSubImage3D(i.TEXTURE_2D_ARRAY,0,0,0,0,se.width,se.height,se.depth,Ae,Xe,se.data)}else t.texImage3D(i.TEXTURE_2D_ARRAY,0,je,se.width,se.height,se.depth,0,Ae,Xe,se.data);else if(y.isData3DTexture)tt?(St&&t.texStorage3D(i.TEXTURE_3D,xe,je,se.width,se.height,se.depth),D&&t.texSubImage3D(i.TEXTURE_3D,0,0,0,0,se.width,se.height,se.depth,Ae,Xe,se.data)):t.texImage3D(i.TEXTURE_3D,0,je,se.width,se.height,se.depth,0,Ae,Xe,se.data);else if(y.isFramebufferTexture){if(St)if(tt)t.texStorage2D(i.TEXTURE_2D,xe,je,se.width,se.height);else{let X=se.width,K=se.height;for(let Se=0;Se<xe;Se++)t.texImage2D(i.TEXTURE_2D,Se,je,X,K,0,Ae,Xe,null),X>>=1,K>>=1}}else if(at.length>0){if(tt&&St){const X=Ee(at[0]);t.texStorage2D(i.TEXTURE_2D,xe,je,X.width,X.height)}for(let X=0,K=at.length;X<K;X++)Re=at[X],tt?D&&t.texSubImage2D(i.TEXTURE_2D,X,0,0,Ae,Xe,Re):t.texImage2D(i.TEXTURE_2D,X,je,Ae,Xe,Re);y.generateMipmaps=!1}else if(tt){if(St){const X=Ee(se);t.texStorage2D(i.TEXTURE_2D,xe,je,X.width,X.height)}D&&t.texSubImage2D(i.TEXTURE_2D,0,0,0,Ae,Xe,se)}else t.texImage2D(i.TEXTURE_2D,0,je,Ae,Xe,se);g(y)&&p(q),Ie.__version=Y.version,y.onUpdate&&y.onUpdate(y)}A.__version=y.version}function ce(A,y,F){if(y.image.length!==6)return;const q=dt(A,y),Q=y.source;t.bindTexture(i.TEXTURE_CUBE_MAP,A.__webglTexture,i.TEXTURE0+F);const Y=n.get(Q);if(Q.version!==Y.__version||q===!0){t.activeTexture(i.TEXTURE0+F);const Ie=ot.getPrimaries(ot.workingColorSpace),ge=y.colorSpace===wi?null:ot.getPrimaries(y.colorSpace),be=y.colorSpace===wi||Ie===ge?i.NONE:i.BROWSER_DEFAULT_WEBGL;i.pixelStorei(i.UNPACK_FLIP_Y_WEBGL,y.flipY),i.pixelStorei(i.UNPACK_PREMULTIPLY_ALPHA_WEBGL,y.premultiplyAlpha),i.pixelStorei(i.UNPACK_ALIGNMENT,y.unpackAlignment),i.pixelStorei(i.UNPACK_COLORSPACE_CONVERSION_WEBGL,be);const rt=y.isCompressedTexture||y.image[0].isCompressedTexture,se=y.image[0]&&y.image[0].isDataTexture,Ae=[];for(let K=0;K<6;K++)!rt&&!se?Ae[K]=_(y.image[K],!0,s.maxCubemapSize):Ae[K]=se?y.image[K].image:y.image[K],Ae[K]=We(y,Ae[K]);const Xe=Ae[0],je=r.convert(y.format,y.colorSpace),Re=r.convert(y.type),at=v(y.internalFormat,je,Re,y.colorSpace),tt=y.isVideoTexture!==!0,St=Y.__version===void 0||q===!0,D=Q.dataReady;let xe=L(y,Xe);Ye(i.TEXTURE_CUBE_MAP,y);let X;if(rt){tt&&St&&t.texStorage2D(i.TEXTURE_CUBE_MAP,xe,at,Xe.width,Xe.height);for(let K=0;K<6;K++){X=Ae[K].mipmaps;for(let Se=0;Se<X.length;Se++){const ve=X[Se];y.format!==bn?je!==null?tt?D&&t.compressedTexSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+K,Se,0,0,ve.width,ve.height,je,ve.data):t.compressedTexImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+K,Se,at,ve.width,ve.height,0,ve.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):tt?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+K,Se,0,0,ve.width,ve.height,je,Re,ve.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+K,Se,at,ve.width,ve.height,0,je,Re,ve.data)}}}else{if(X=y.mipmaps,tt&&St){X.length>0&&xe++;const K=Ee(Ae[0]);t.texStorage2D(i.TEXTURE_CUBE_MAP,xe,at,K.width,K.height)}for(let K=0;K<6;K++)if(se){tt?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+K,0,0,0,Ae[K].width,Ae[K].height,je,Re,Ae[K].data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+K,0,at,Ae[K].width,Ae[K].height,0,je,Re,Ae[K].data);for(let Se=0;Se<X.length;Se++){const Je=X[Se].image[K].image;tt?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+K,Se+1,0,0,Je.width,Je.height,je,Re,Je.data):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+K,Se+1,at,Je.width,Je.height,0,je,Re,Je.data)}}else{tt?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+K,0,0,0,je,Re,Ae[K]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+K,0,at,je,Re,Ae[K]);for(let Se=0;Se<X.length;Se++){const ve=X[Se];tt?D&&t.texSubImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+K,Se+1,0,0,je,Re,ve.image[K]):t.texImage2D(i.TEXTURE_CUBE_MAP_POSITIVE_X+K,Se+1,at,je,Re,ve.image[K])}}}g(y)&&p(i.TEXTURE_CUBE_MAP),Y.__version=Q.version,y.onUpdate&&y.onUpdate(y)}A.__version=y.version}function Pe(A,y,F,q,Q,Y){const Ie=r.convert(F.format,F.colorSpace),ge=r.convert(F.type),be=v(F.internalFormat,Ie,ge,F.colorSpace),rt=n.get(y),se=n.get(F);if(se.__renderTarget=y,!rt.__hasExternalTextures){const Ae=Math.max(1,y.width>>Y),Xe=Math.max(1,y.height>>Y);Q===i.TEXTURE_3D||Q===i.TEXTURE_2D_ARRAY?t.texImage3D(Q,Y,be,Ae,Xe,y.depth,0,Ie,ge,null):t.texImage2D(Q,Y,be,Ae,Xe,0,Ie,ge,null)}t.bindFramebuffer(i.FRAMEBUFFER,A),we(y)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,q,Q,se.__webglTexture,0,ne(y)):(Q===i.TEXTURE_2D||Q>=i.TEXTURE_CUBE_MAP_POSITIVE_X&&Q<=i.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&i.framebufferTexture2D(i.FRAMEBUFFER,q,Q,se.__webglTexture,Y),t.bindFramebuffer(i.FRAMEBUFFER,null)}function fe(A,y,F){if(i.bindRenderbuffer(i.RENDERBUFFER,A),y.depthBuffer){const q=y.depthTexture,Q=q&&q.isDepthTexture?q.type:null,Y=x(y.stencilBuffer,Q),Ie=y.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,ge=ne(y);we(y)?a.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,ge,Y,y.width,y.height):F?i.renderbufferStorageMultisample(i.RENDERBUFFER,ge,Y,y.width,y.height):i.renderbufferStorage(i.RENDERBUFFER,Y,y.width,y.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,Ie,i.RENDERBUFFER,A)}else{const q=y.textures;for(let Q=0;Q<q.length;Q++){const Y=q[Q],Ie=r.convert(Y.format,Y.colorSpace),ge=r.convert(Y.type),be=v(Y.internalFormat,Ie,ge,Y.colorSpace),rt=ne(y);F&&we(y)===!1?i.renderbufferStorageMultisample(i.RENDERBUFFER,rt,be,y.width,y.height):we(y)?a.renderbufferStorageMultisampleEXT(i.RENDERBUFFER,rt,be,y.width,y.height):i.renderbufferStorage(i.RENDERBUFFER,be,y.width,y.height)}}i.bindRenderbuffer(i.RENDERBUFFER,null)}function ze(A,y){if(y&&y.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(i.FRAMEBUFFER,A),!(y.depthTexture&&y.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");const q=n.get(y.depthTexture);q.__renderTarget=y,(!q.__webglTexture||y.depthTexture.image.width!==y.width||y.depthTexture.image.height!==y.height)&&(y.depthTexture.image.width=y.width,y.depthTexture.image.height=y.height,y.depthTexture.needsUpdate=!0),j(y.depthTexture,0);const Q=q.__webglTexture,Y=ne(y);if(y.depthTexture.format===Is)we(y)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,Q,0,Y):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_ATTACHMENT,i.TEXTURE_2D,Q,0);else if(y.depthTexture.format===Vs)we(y)?a.framebufferTexture2DMultisampleEXT(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,Q,0,Y):i.framebufferTexture2D(i.FRAMEBUFFER,i.DEPTH_STENCIL_ATTACHMENT,i.TEXTURE_2D,Q,0);else throw new Error("Unknown depthTexture format")}function $e(A){const y=n.get(A),F=A.isWebGLCubeRenderTarget===!0;if(y.__boundDepthTexture!==A.depthTexture){const q=A.depthTexture;if(y.__depthDisposeCallback&&y.__depthDisposeCallback(),q){const Q=()=>{delete y.__boundDepthTexture,delete y.__depthDisposeCallback,q.removeEventListener("dispose",Q)};q.addEventListener("dispose",Q),y.__depthDisposeCallback=Q}y.__boundDepthTexture=q}if(A.depthTexture&&!y.__autoAllocateDepthBuffer){if(F)throw new Error("target.depthTexture not supported in Cube render targets");ze(y.__webglFramebuffer,A)}else if(F){y.__webglDepthbuffer=[];for(let q=0;q<6;q++)if(t.bindFramebuffer(i.FRAMEBUFFER,y.__webglFramebuffer[q]),y.__webglDepthbuffer[q]===void 0)y.__webglDepthbuffer[q]=i.createRenderbuffer(),fe(y.__webglDepthbuffer[q],A,!1);else{const Q=A.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Y=y.__webglDepthbuffer[q];i.bindRenderbuffer(i.RENDERBUFFER,Y),i.framebufferRenderbuffer(i.FRAMEBUFFER,Q,i.RENDERBUFFER,Y)}}else if(t.bindFramebuffer(i.FRAMEBUFFER,y.__webglFramebuffer),y.__webglDepthbuffer===void 0)y.__webglDepthbuffer=i.createRenderbuffer(),fe(y.__webglDepthbuffer,A,!1);else{const q=A.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Q=y.__webglDepthbuffer;i.bindRenderbuffer(i.RENDERBUFFER,Q),i.framebufferRenderbuffer(i.FRAMEBUFFER,q,i.RENDERBUFFER,Q)}t.bindFramebuffer(i.FRAMEBUFFER,null)}function qe(A,y,F){const q=n.get(A);y!==void 0&&Pe(q.__webglFramebuffer,A,A.texture,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,0),F!==void 0&&$e(A)}function ct(A){const y=A.texture,F=n.get(A),q=n.get(y);A.addEventListener("dispose",R);const Q=A.textures,Y=A.isWebGLCubeRenderTarget===!0,Ie=Q.length>1;if(Ie||(q.__webglTexture===void 0&&(q.__webglTexture=i.createTexture()),q.__version=y.version,o.memory.textures++),Y){F.__webglFramebuffer=[];for(let ge=0;ge<6;ge++)if(y.mipmaps&&y.mipmaps.length>0){F.__webglFramebuffer[ge]=[];for(let be=0;be<y.mipmaps.length;be++)F.__webglFramebuffer[ge][be]=i.createFramebuffer()}else F.__webglFramebuffer[ge]=i.createFramebuffer()}else{if(y.mipmaps&&y.mipmaps.length>0){F.__webglFramebuffer=[];for(let ge=0;ge<y.mipmaps.length;ge++)F.__webglFramebuffer[ge]=i.createFramebuffer()}else F.__webglFramebuffer=i.createFramebuffer();if(Ie)for(let ge=0,be=Q.length;ge<be;ge++){const rt=n.get(Q[ge]);rt.__webglTexture===void 0&&(rt.__webglTexture=i.createTexture(),o.memory.textures++)}if(A.samples>0&&we(A)===!1){F.__webglMultisampledFramebuffer=i.createFramebuffer(),F.__webglColorRenderbuffer=[],t.bindFramebuffer(i.FRAMEBUFFER,F.__webglMultisampledFramebuffer);for(let ge=0;ge<Q.length;ge++){const be=Q[ge];F.__webglColorRenderbuffer[ge]=i.createRenderbuffer(),i.bindRenderbuffer(i.RENDERBUFFER,F.__webglColorRenderbuffer[ge]);const rt=r.convert(be.format,be.colorSpace),se=r.convert(be.type),Ae=v(be.internalFormat,rt,se,be.colorSpace,A.isXRRenderTarget===!0),Xe=ne(A);i.renderbufferStorageMultisample(i.RENDERBUFFER,Xe,Ae,A.width,A.height),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+ge,i.RENDERBUFFER,F.__webglColorRenderbuffer[ge])}i.bindRenderbuffer(i.RENDERBUFFER,null),A.depthBuffer&&(F.__webglDepthRenderbuffer=i.createRenderbuffer(),fe(F.__webglDepthRenderbuffer,A,!0)),t.bindFramebuffer(i.FRAMEBUFFER,null)}}if(Y){t.bindTexture(i.TEXTURE_CUBE_MAP,q.__webglTexture),Ye(i.TEXTURE_CUBE_MAP,y);for(let ge=0;ge<6;ge++)if(y.mipmaps&&y.mipmaps.length>0)for(let be=0;be<y.mipmaps.length;be++)Pe(F.__webglFramebuffer[ge][be],A,y,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+ge,be);else Pe(F.__webglFramebuffer[ge],A,y,i.COLOR_ATTACHMENT0,i.TEXTURE_CUBE_MAP_POSITIVE_X+ge,0);g(y)&&p(i.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Ie){for(let ge=0,be=Q.length;ge<be;ge++){const rt=Q[ge],se=n.get(rt);t.bindTexture(i.TEXTURE_2D,se.__webglTexture),Ye(i.TEXTURE_2D,rt),Pe(F.__webglFramebuffer,A,rt,i.COLOR_ATTACHMENT0+ge,i.TEXTURE_2D,0),g(rt)&&p(i.TEXTURE_2D)}t.unbindTexture()}else{let ge=i.TEXTURE_2D;if((A.isWebGL3DRenderTarget||A.isWebGLArrayRenderTarget)&&(ge=A.isWebGL3DRenderTarget?i.TEXTURE_3D:i.TEXTURE_2D_ARRAY),t.bindTexture(ge,q.__webglTexture),Ye(ge,y),y.mipmaps&&y.mipmaps.length>0)for(let be=0;be<y.mipmaps.length;be++)Pe(F.__webglFramebuffer[be],A,y,i.COLOR_ATTACHMENT0,ge,be);else Pe(F.__webglFramebuffer,A,y,i.COLOR_ATTACHMENT0,ge,0);g(y)&&p(ge),t.unbindTexture()}A.depthBuffer&&$e(A)}function J(A){const y=A.textures;for(let F=0,q=y.length;F<q;F++){const Q=y[F];if(g(Q)){const Y=M(A),Ie=n.get(Q).__webglTexture;t.bindTexture(Y,Ie),p(Y),t.unbindTexture()}}}const oe=[],C=[];function Fe(A){if(A.samples>0){if(we(A)===!1){const y=A.textures,F=A.width,q=A.height;let Q=i.COLOR_BUFFER_BIT;const Y=A.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT,Ie=n.get(A),ge=y.length>1;if(ge)for(let be=0;be<y.length;be++)t.bindFramebuffer(i.FRAMEBUFFER,Ie.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+be,i.RENDERBUFFER,null),t.bindFramebuffer(i.FRAMEBUFFER,Ie.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+be,i.TEXTURE_2D,null,0);t.bindFramebuffer(i.READ_FRAMEBUFFER,Ie.__webglMultisampledFramebuffer),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ie.__webglFramebuffer);for(let be=0;be<y.length;be++){if(A.resolveDepthBuffer&&(A.depthBuffer&&(Q|=i.DEPTH_BUFFER_BIT),A.stencilBuffer&&A.resolveStencilBuffer&&(Q|=i.STENCIL_BUFFER_BIT)),ge){i.framebufferRenderbuffer(i.READ_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.RENDERBUFFER,Ie.__webglColorRenderbuffer[be]);const rt=n.get(y[be]).__webglTexture;i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0,i.TEXTURE_2D,rt,0)}i.blitFramebuffer(0,0,F,q,0,0,F,q,Q,i.NEAREST),c===!0&&(oe.length=0,C.length=0,oe.push(i.COLOR_ATTACHMENT0+be),A.depthBuffer&&A.resolveDepthBuffer===!1&&(oe.push(Y),C.push(Y),i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,C)),i.invalidateFramebuffer(i.READ_FRAMEBUFFER,oe))}if(t.bindFramebuffer(i.READ_FRAMEBUFFER,null),t.bindFramebuffer(i.DRAW_FRAMEBUFFER,null),ge)for(let be=0;be<y.length;be++){t.bindFramebuffer(i.FRAMEBUFFER,Ie.__webglMultisampledFramebuffer),i.framebufferRenderbuffer(i.FRAMEBUFFER,i.COLOR_ATTACHMENT0+be,i.RENDERBUFFER,Ie.__webglColorRenderbuffer[be]);const rt=n.get(y[be]).__webglTexture;t.bindFramebuffer(i.FRAMEBUFFER,Ie.__webglFramebuffer),i.framebufferTexture2D(i.DRAW_FRAMEBUFFER,i.COLOR_ATTACHMENT0+be,i.TEXTURE_2D,rt,0)}t.bindFramebuffer(i.DRAW_FRAMEBUFFER,Ie.__webglMultisampledFramebuffer)}else if(A.depthBuffer&&A.resolveDepthBuffer===!1&&c){const y=A.stencilBuffer?i.DEPTH_STENCIL_ATTACHMENT:i.DEPTH_ATTACHMENT;i.invalidateFramebuffer(i.DRAW_FRAMEBUFFER,[y])}}}function ne(A){return Math.min(s.maxSamples,A.samples)}function we(A){const y=n.get(A);return A.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&y.__useRenderToTexture!==!1}function de(A){const y=o.render.frame;u.get(A)!==y&&(u.set(A,y),A.update())}function We(A,y){const F=A.colorSpace,q=A.format,Q=A.type;return A.isCompressedTexture===!0||A.isVideoTexture===!0||F!==en&&F!==wi&&(ot.getTransfer(F)===yt?(q!==bn||Q!==hi)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",F)),y}function Ee(A){return typeof HTMLImageElement<"u"&&A instanceof HTMLImageElement?(l.width=A.naturalWidth||A.width,l.height=A.naturalHeight||A.height):typeof VideoFrame<"u"&&A instanceof VideoFrame?(l.width=A.displayWidth,l.height=A.displayHeight):(l.width=A.width,l.height=A.height),l}this.allocateTextureUnit=B,this.resetTextureUnits=G,this.setTexture2D=j,this.setTexture2DArray=W,this.setTexture3D=ee,this.setTextureCube=O,this.rebindTextures=qe,this.setupRenderTarget=ct,this.updateRenderTargetMipmap=J,this.updateMultisampleRenderTarget=Fe,this.setupDepthRenderbuffer=$e,this.setupFrameBufferTexture=Pe,this.useMultisampledRTT=we}function Px(i,e){function t(n,s=wi){let r;const o=ot.getTransfer(s);if(n===hi)return i.UNSIGNED_BYTE;if(n===ml)return i.UNSIGNED_SHORT_4_4_4_4;if(n===gl)return i.UNSIGNED_SHORT_5_5_5_1;if(n===$h)return i.UNSIGNED_INT_5_9_9_9_REV;if(n===Yh)return i.BYTE;if(n===jh)return i.SHORT;if(n===Tr)return i.UNSIGNED_SHORT;if(n===pl)return i.INT;if(n===es)return i.UNSIGNED_INT;if(n===Dn)return i.FLOAT;if(n===Dr)return i.HALF_FLOAT;if(n===Kh)return i.ALPHA;if(n===Zh)return i.RGB;if(n===bn)return i.RGBA;if(n===Jh)return i.LUMINANCE;if(n===Qh)return i.LUMINANCE_ALPHA;if(n===Is)return i.DEPTH_COMPONENT;if(n===Vs)return i.DEPTH_STENCIL;if(n===_l)return i.RED;if(n===xl)return i.RED_INTEGER;if(n===ef)return i.RG;if(n===vl)return i.RG_INTEGER;if(n===yl)return i.RGBA_INTEGER;if(n===Ro||n===Co||n===Po||n===Lo)if(o===yt)if(r=e.get("WEBGL_compressed_texture_s3tc_srgb"),r!==null){if(n===Ro)return r.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===Co)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Po)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===Lo)return r.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(r=e.get("WEBGL_compressed_texture_s3tc"),r!==null){if(n===Ro)return r.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===Co)return r.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Po)return r.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===Lo)return r.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===wc||n===Tc||n===Ac||n===Rc)if(r=e.get("WEBGL_compressed_texture_pvrtc"),r!==null){if(n===wc)return r.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Tc)return r.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Ac)return r.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===Rc)return r.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Cc||n===Pc||n===Lc)if(r=e.get("WEBGL_compressed_texture_etc"),r!==null){if(n===Cc||n===Pc)return o===yt?r.COMPRESSED_SRGB8_ETC2:r.COMPRESSED_RGB8_ETC2;if(n===Lc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:r.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===Ic||n===Dc||n===Nc||n===Uc||n===Oc||n===Fc||n===Bc||n===kc||n===zc||n===Hc||n===Vc||n===Gc||n===Wc||n===Xc)if(r=e.get("WEBGL_compressed_texture_astc"),r!==null){if(n===Ic)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:r.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===Dc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:r.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===Nc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:r.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===Uc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:r.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===Oc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:r.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===Fc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:r.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===Bc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:r.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===kc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:r.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===zc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:r.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===Hc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:r.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===Vc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:r.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===Gc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:r.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===Wc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:r.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===Xc)return o===yt?r.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:r.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===Io||n===qc||n===Yc)if(r=e.get("EXT_texture_compression_bptc"),r!==null){if(n===Io)return o===yt?r.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:r.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===qc)return r.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===Yc)return r.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===tf||n===jc||n===$c||n===Kc)if(r=e.get("EXT_texture_compression_rgtc"),r!==null){if(n===Io)return r.COMPRESSED_RED_RGTC1_EXT;if(n===jc)return r.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===$c)return r.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===Kc)return r.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===Hs?i.UNSIGNED_INT_24_8:i[n]!==void 0?i[n]:null}return{convert:t}}class Lx extends ln{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class un extends At{constructor(){super(),this.isGroup=!0,this.type="Group"}}const Ix={type:"move"};class Ba{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new un,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new un,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new b,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new b),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new un,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new b,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new b),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let s=null,r=null,o=null;const a=this._targetRay,c=this._grip,l=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(l&&e.hand){o=!0;for(const _ of e.hand.values()){const g=t.getJointPose(_,n),p=this._getHandJoint(l,_);g!==null&&(p.matrix.fromArray(g.transform.matrix),p.matrix.decompose(p.position,p.rotation,p.scale),p.matrixWorldNeedsUpdate=!0,p.jointRadius=g.radius),p.visible=g!==null}const u=l.joints["index-finger-tip"],f=l.joints["thumb-tip"],h=u.position.distanceTo(f.position),d=.02,m=.005;l.inputState.pinching&&h>d+m?(l.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!l.inputState.pinching&&h<=d-m&&(l.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else c!==null&&e.gripSpace&&(r=t.getPose(e.gripSpace,n),r!==null&&(c.matrix.fromArray(r.transform.matrix),c.matrix.decompose(c.position,c.rotation,c.scale),c.matrixWorldNeedsUpdate=!0,r.linearVelocity?(c.hasLinearVelocity=!0,c.linearVelocity.copy(r.linearVelocity)):c.hasLinearVelocity=!1,r.angularVelocity?(c.hasAngularVelocity=!0,c.angularVelocity.copy(r.angularVelocity)):c.hasAngularVelocity=!1));a!==null&&(s=t.getPose(e.targetRaySpace,n),s===null&&r!==null&&(s=r),s!==null&&(a.matrix.fromArray(s.transform.matrix),a.matrix.decompose(a.position,a.rotation,a.scale),a.matrixWorldNeedsUpdate=!0,s.linearVelocity?(a.hasLinearVelocity=!0,a.linearVelocity.copy(s.linearVelocity)):a.hasLinearVelocity=!1,s.angularVelocity?(a.hasAngularVelocity=!0,a.angularVelocity.copy(s.angularVelocity)):a.hasAngularVelocity=!1,this.dispatchEvent(Ix)))}return a!==null&&(a.visible=s!==null),c!==null&&(c.visible=r!==null),l!==null&&(l.visible=o!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new un;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const Dx=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,Nx=`
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

}`;class Ux{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const s=new Wt,r=e.properties.get(s);r.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=s}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new Vn({vertexShader:Dx,fragmentShader:Nx,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new Gt(new fi(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class Ox extends $s{constructor(e,t){super();const n=this;let s=null,r=1,o=null,a="local-floor",c=1,l=null,u=null,f=null,h=null,d=null,m=null;const _=new Ux,g=t.getContextAttributes();let p=null,M=null;const v=[],x=[],L=new ie;let T=null;const R=new ln;R.viewport=new ht;const I=new ln;I.viewport=new ht;const w=[R,I],S=new Lx;let P=null,G=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function($){let ce=v[$];return ce===void 0&&(ce=new Ba,v[$]=ce),ce.getTargetRaySpace()},this.getControllerGrip=function($){let ce=v[$];return ce===void 0&&(ce=new Ba,v[$]=ce),ce.getGripSpace()},this.getHand=function($){let ce=v[$];return ce===void 0&&(ce=new Ba,v[$]=ce),ce.getHandSpace()};function B($){const ce=x.indexOf($.inputSource);if(ce===-1)return;const Pe=v[ce];Pe!==void 0&&(Pe.update($.inputSource,$.frame,l||o),Pe.dispatchEvent({type:$.type,data:$.inputSource}))}function V(){s.removeEventListener("select",B),s.removeEventListener("selectstart",B),s.removeEventListener("selectend",B),s.removeEventListener("squeeze",B),s.removeEventListener("squeezestart",B),s.removeEventListener("squeezeend",B),s.removeEventListener("end",V),s.removeEventListener("inputsourceschange",j);for(let $=0;$<v.length;$++){const ce=x[$];ce!==null&&(x[$]=null,v[$].disconnect(ce))}P=null,G=null,_.reset(),e.setRenderTarget(p),d=null,h=null,f=null,s=null,M=null,dt.stop(),n.isPresenting=!1,e.setPixelRatio(T),e.setSize(L.width,L.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function($){r=$,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function($){a=$,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return l||o},this.setReferenceSpace=function($){l=$},this.getBaseLayer=function(){return h!==null?h:d},this.getBinding=function(){return f},this.getFrame=function(){return m},this.getSession=function(){return s},this.setSession=async function($){if(s=$,s!==null){if(p=e.getRenderTarget(),s.addEventListener("select",B),s.addEventListener("selectstart",B),s.addEventListener("selectend",B),s.addEventListener("squeeze",B),s.addEventListener("squeezestart",B),s.addEventListener("squeezeend",B),s.addEventListener("end",V),s.addEventListener("inputsourceschange",j),g.xrCompatible!==!0&&await t.makeXRCompatible(),T=e.getPixelRatio(),e.getSize(L),s.renderState.layers===void 0){const ce={antialias:g.antialias,alpha:!0,depth:g.depth,stencil:g.stencil,framebufferScaleFactor:r};d=new XRWebGLLayer(s,t,ce),s.updateRenderState({baseLayer:d}),e.setPixelRatio(1),e.setSize(d.framebufferWidth,d.framebufferHeight,!1),M=new ts(d.framebufferWidth,d.framebufferHeight,{format:bn,type:hi,colorSpace:e.outputColorSpace,stencilBuffer:g.stencil})}else{let ce=null,Pe=null,fe=null;g.depth&&(fe=g.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,ce=g.stencil?Vs:Is,Pe=g.stencil?Hs:es);const ze={colorFormat:t.RGBA8,depthFormat:fe,scaleFactor:r};f=new XRWebGLBinding(s,t),h=f.createProjectionLayer(ze),s.updateRenderState({layers:[h]}),e.setPixelRatio(1),e.setSize(h.textureWidth,h.textureHeight,!1),M=new ts(h.textureWidth,h.textureHeight,{format:bn,type:hi,depthTexture:new gf(h.textureWidth,h.textureHeight,Pe,void 0,void 0,void 0,void 0,void 0,void 0,ce),stencilBuffer:g.stencil,colorSpace:e.outputColorSpace,samples:g.antialias?4:0,resolveDepthBuffer:h.ignoreDepthValues===!1})}M.isXRRenderTarget=!0,this.setFoveation(c),l=null,o=await s.requestReferenceSpace(a),dt.setContext(s),dt.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(s!==null)return s.environmentBlendMode},this.getDepthTexture=function(){return _.getDepthTexture()};function j($){for(let ce=0;ce<$.removed.length;ce++){const Pe=$.removed[ce],fe=x.indexOf(Pe);fe>=0&&(x[fe]=null,v[fe].disconnect(Pe))}for(let ce=0;ce<$.added.length;ce++){const Pe=$.added[ce];let fe=x.indexOf(Pe);if(fe===-1){for(let $e=0;$e<v.length;$e++)if($e>=x.length){x.push(Pe),fe=$e;break}else if(x[$e]===null){x[$e]=Pe,fe=$e;break}if(fe===-1)break}const ze=v[fe];ze&&ze.connect(Pe)}}const W=new b,ee=new b;function O($,ce,Pe){W.setFromMatrixPosition(ce.matrixWorld),ee.setFromMatrixPosition(Pe.matrixWorld);const fe=W.distanceTo(ee),ze=ce.projectionMatrix.elements,$e=Pe.projectionMatrix.elements,qe=ze[14]/(ze[10]-1),ct=ze[14]/(ze[10]+1),J=(ze[9]+1)/ze[5],oe=(ze[9]-1)/ze[5],C=(ze[8]-1)/ze[0],Fe=($e[8]+1)/$e[0],ne=qe*C,we=qe*Fe,de=fe/(-C+Fe),We=de*-C;if(ce.matrixWorld.decompose($.position,$.quaternion,$.scale),$.translateX(We),$.translateZ(de),$.matrixWorld.compose($.position,$.quaternion,$.scale),$.matrixWorldInverse.copy($.matrixWorld).invert(),ze[10]===-1)$.projectionMatrix.copy(ce.projectionMatrix),$.projectionMatrixInverse.copy(ce.projectionMatrixInverse);else{const Ee=qe+de,A=ct+de,y=ne-We,F=we+(fe-We),q=J*ct/A*Ee,Q=oe*ct/A*Ee;$.projectionMatrix.makePerspective(y,F,q,Q,Ee,A),$.projectionMatrixInverse.copy($.projectionMatrix).invert()}}function re($,ce){ce===null?$.matrixWorld.copy($.matrix):$.matrixWorld.multiplyMatrices(ce.matrixWorld,$.matrix),$.matrixWorldInverse.copy($.matrixWorld).invert()}this.updateCamera=function($){if(s===null)return;let ce=$.near,Pe=$.far;_.texture!==null&&(_.depthNear>0&&(ce=_.depthNear),_.depthFar>0&&(Pe=_.depthFar)),S.near=I.near=R.near=ce,S.far=I.far=R.far=Pe,(P!==S.near||G!==S.far)&&(s.updateRenderState({depthNear:S.near,depthFar:S.far}),P=S.near,G=S.far),R.layers.mask=$.layers.mask|2,I.layers.mask=$.layers.mask|4,S.layers.mask=R.layers.mask|I.layers.mask;const fe=$.parent,ze=S.cameras;re(S,fe);for(let $e=0;$e<ze.length;$e++)re(ze[$e],fe);ze.length===2?O(S,R,I):S.projectionMatrix.copy(R.projectionMatrix),ue($,S,fe)};function ue($,ce,Pe){Pe===null?$.matrix.copy(ce.matrixWorld):($.matrix.copy(Pe.matrixWorld),$.matrix.invert(),$.matrix.multiply(ce.matrixWorld)),$.matrix.decompose($.position,$.quaternion,$.scale),$.updateMatrixWorld(!0),$.projectionMatrix.copy(ce.projectionMatrix),$.projectionMatrixInverse.copy(ce.projectionMatrixInverse),$.isPerspectiveCamera&&($.fov=Gs*2*Math.atan(1/$.projectionMatrix.elements[5]),$.zoom=1)}this.getCamera=function(){return S},this.getFoveation=function(){if(!(h===null&&d===null))return c},this.setFoveation=function($){c=$,h!==null&&(h.fixedFoveation=$),d!==null&&d.fixedFoveation!==void 0&&(d.fixedFoveation=$)},this.hasDepthSensing=function(){return _.texture!==null},this.getDepthSensingMesh=function(){return _.getMesh(S)};let Me=null;function Ye($,ce){if(u=ce.getViewerPose(l||o),m=ce,u!==null){const Pe=u.views;d!==null&&(e.setRenderTargetFramebuffer(M,d.framebuffer),e.setRenderTarget(M));let fe=!1;Pe.length!==S.cameras.length&&(S.cameras.length=0,fe=!0);for(let $e=0;$e<Pe.length;$e++){const qe=Pe[$e];let ct=null;if(d!==null)ct=d.getViewport(qe);else{const oe=f.getViewSubImage(h,qe);ct=oe.viewport,$e===0&&(e.setRenderTargetTextures(M,oe.colorTexture,h.ignoreDepthValues?void 0:oe.depthStencilTexture),e.setRenderTarget(M))}let J=w[$e];J===void 0&&(J=new ln,J.layers.enable($e),J.viewport=new ht,w[$e]=J),J.matrix.fromArray(qe.transform.matrix),J.matrix.decompose(J.position,J.quaternion,J.scale),J.projectionMatrix.fromArray(qe.projectionMatrix),J.projectionMatrixInverse.copy(J.projectionMatrix).invert(),J.viewport.set(ct.x,ct.y,ct.width,ct.height),$e===0&&(S.matrix.copy(J.matrix),S.matrix.decompose(S.position,S.quaternion,S.scale)),fe===!0&&S.cameras.push(J)}const ze=s.enabledFeatures;if(ze&&ze.includes("depth-sensing")){const $e=f.getDepthInformation(Pe[0]);$e&&$e.isValid&&$e.texture&&_.init(e,$e,s.renderState)}}for(let Pe=0;Pe<v.length;Pe++){const fe=x[Pe],ze=v[Pe];fe!==null&&ze!==void 0&&ze.update(fe,ce,l||o)}Me&&Me($,ce),ce.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:ce}),m=null}const dt=new mf;dt.setAnimationLoop(Ye),this.setAnimationLoop=function($){Me=$},this.dispose=function(){}}}const Yi=new Un,Fx=new De;function Bx(i,e){function t(g,p){g.matrixAutoUpdate===!0&&g.updateMatrix(),p.value.copy(g.matrix)}function n(g,p){p.color.getRGB(g.fogColor.value,ff(i)),p.isFog?(g.fogNear.value=p.near,g.fogFar.value=p.far):p.isFogExp2&&(g.fogDensity.value=p.density)}function s(g,p,M,v,x){p.isMeshBasicMaterial||p.isMeshLambertMaterial?r(g,p):p.isMeshToonMaterial?(r(g,p),f(g,p)):p.isMeshPhongMaterial?(r(g,p),u(g,p)):p.isMeshStandardMaterial?(r(g,p),h(g,p),p.isMeshPhysicalMaterial&&d(g,p,x)):p.isMeshMatcapMaterial?(r(g,p),m(g,p)):p.isMeshDepthMaterial?r(g,p):p.isMeshDistanceMaterial?(r(g,p),_(g,p)):p.isMeshNormalMaterial?r(g,p):p.isLineBasicMaterial?(o(g,p),p.isLineDashedMaterial&&a(g,p)):p.isPointsMaterial?c(g,p,M,v):p.isSpriteMaterial?l(g,p):p.isShadowMaterial?(g.color.value.copy(p.color),g.opacity.value=p.opacity):p.isShaderMaterial&&(p.uniformsNeedUpdate=!1)}function r(g,p){g.opacity.value=p.opacity,p.color&&g.diffuse.value.copy(p.color),p.emissive&&g.emissive.value.copy(p.emissive).multiplyScalar(p.emissiveIntensity),p.map&&(g.map.value=p.map,t(p.map,g.mapTransform)),p.alphaMap&&(g.alphaMap.value=p.alphaMap,t(p.alphaMap,g.alphaMapTransform)),p.bumpMap&&(g.bumpMap.value=p.bumpMap,t(p.bumpMap,g.bumpMapTransform),g.bumpScale.value=p.bumpScale,p.side===sn&&(g.bumpScale.value*=-1)),p.normalMap&&(g.normalMap.value=p.normalMap,t(p.normalMap,g.normalMapTransform),g.normalScale.value.copy(p.normalScale),p.side===sn&&g.normalScale.value.negate()),p.displacementMap&&(g.displacementMap.value=p.displacementMap,t(p.displacementMap,g.displacementMapTransform),g.displacementScale.value=p.displacementScale,g.displacementBias.value=p.displacementBias),p.emissiveMap&&(g.emissiveMap.value=p.emissiveMap,t(p.emissiveMap,g.emissiveMapTransform)),p.specularMap&&(g.specularMap.value=p.specularMap,t(p.specularMap,g.specularMapTransform)),p.alphaTest>0&&(g.alphaTest.value=p.alphaTest);const M=e.get(p),v=M.envMap,x=M.envMapRotation;v&&(g.envMap.value=v,Yi.copy(x),Yi.x*=-1,Yi.y*=-1,Yi.z*=-1,v.isCubeTexture&&v.isRenderTargetTexture===!1&&(Yi.y*=-1,Yi.z*=-1),g.envMapRotation.value.setFromMatrix4(Fx.makeRotationFromEuler(Yi)),g.flipEnvMap.value=v.isCubeTexture&&v.isRenderTargetTexture===!1?-1:1,g.reflectivity.value=p.reflectivity,g.ior.value=p.ior,g.refractionRatio.value=p.refractionRatio),p.lightMap&&(g.lightMap.value=p.lightMap,g.lightMapIntensity.value=p.lightMapIntensity,t(p.lightMap,g.lightMapTransform)),p.aoMap&&(g.aoMap.value=p.aoMap,g.aoMapIntensity.value=p.aoMapIntensity,t(p.aoMap,g.aoMapTransform))}function o(g,p){g.diffuse.value.copy(p.color),g.opacity.value=p.opacity,p.map&&(g.map.value=p.map,t(p.map,g.mapTransform))}function a(g,p){g.dashSize.value=p.dashSize,g.totalSize.value=p.dashSize+p.gapSize,g.scale.value=p.scale}function c(g,p,M,v){g.diffuse.value.copy(p.color),g.opacity.value=p.opacity,g.size.value=p.size*M,g.scale.value=v*.5,p.map&&(g.map.value=p.map,t(p.map,g.uvTransform)),p.alphaMap&&(g.alphaMap.value=p.alphaMap,t(p.alphaMap,g.alphaMapTransform)),p.alphaTest>0&&(g.alphaTest.value=p.alphaTest)}function l(g,p){g.diffuse.value.copy(p.color),g.opacity.value=p.opacity,g.rotation.value=p.rotation,p.map&&(g.map.value=p.map,t(p.map,g.mapTransform)),p.alphaMap&&(g.alphaMap.value=p.alphaMap,t(p.alphaMap,g.alphaMapTransform)),p.alphaTest>0&&(g.alphaTest.value=p.alphaTest)}function u(g,p){g.specular.value.copy(p.specular),g.shininess.value=Math.max(p.shininess,1e-4)}function f(g,p){p.gradientMap&&(g.gradientMap.value=p.gradientMap)}function h(g,p){g.metalness.value=p.metalness,p.metalnessMap&&(g.metalnessMap.value=p.metalnessMap,t(p.metalnessMap,g.metalnessMapTransform)),g.roughness.value=p.roughness,p.roughnessMap&&(g.roughnessMap.value=p.roughnessMap,t(p.roughnessMap,g.roughnessMapTransform)),p.envMap&&(g.envMapIntensity.value=p.envMapIntensity)}function d(g,p,M){g.ior.value=p.ior,p.sheen>0&&(g.sheenColor.value.copy(p.sheenColor).multiplyScalar(p.sheen),g.sheenRoughness.value=p.sheenRoughness,p.sheenColorMap&&(g.sheenColorMap.value=p.sheenColorMap,t(p.sheenColorMap,g.sheenColorMapTransform)),p.sheenRoughnessMap&&(g.sheenRoughnessMap.value=p.sheenRoughnessMap,t(p.sheenRoughnessMap,g.sheenRoughnessMapTransform))),p.clearcoat>0&&(g.clearcoat.value=p.clearcoat,g.clearcoatRoughness.value=p.clearcoatRoughness,p.clearcoatMap&&(g.clearcoatMap.value=p.clearcoatMap,t(p.clearcoatMap,g.clearcoatMapTransform)),p.clearcoatRoughnessMap&&(g.clearcoatRoughnessMap.value=p.clearcoatRoughnessMap,t(p.clearcoatRoughnessMap,g.clearcoatRoughnessMapTransform)),p.clearcoatNormalMap&&(g.clearcoatNormalMap.value=p.clearcoatNormalMap,t(p.clearcoatNormalMap,g.clearcoatNormalMapTransform),g.clearcoatNormalScale.value.copy(p.clearcoatNormalScale),p.side===sn&&g.clearcoatNormalScale.value.negate())),p.dispersion>0&&(g.dispersion.value=p.dispersion),p.iridescence>0&&(g.iridescence.value=p.iridescence,g.iridescenceIOR.value=p.iridescenceIOR,g.iridescenceThicknessMinimum.value=p.iridescenceThicknessRange[0],g.iridescenceThicknessMaximum.value=p.iridescenceThicknessRange[1],p.iridescenceMap&&(g.iridescenceMap.value=p.iridescenceMap,t(p.iridescenceMap,g.iridescenceMapTransform)),p.iridescenceThicknessMap&&(g.iridescenceThicknessMap.value=p.iridescenceThicknessMap,t(p.iridescenceThicknessMap,g.iridescenceThicknessMapTransform))),p.transmission>0&&(g.transmission.value=p.transmission,g.transmissionSamplerMap.value=M.texture,g.transmissionSamplerSize.value.set(M.width,M.height),p.transmissionMap&&(g.transmissionMap.value=p.transmissionMap,t(p.transmissionMap,g.transmissionMapTransform)),g.thickness.value=p.thickness,p.thicknessMap&&(g.thicknessMap.value=p.thicknessMap,t(p.thicknessMap,g.thicknessMapTransform)),g.attenuationDistance.value=p.attenuationDistance,g.attenuationColor.value.copy(p.attenuationColor)),p.anisotropy>0&&(g.anisotropyVector.value.set(p.anisotropy*Math.cos(p.anisotropyRotation),p.anisotropy*Math.sin(p.anisotropyRotation)),p.anisotropyMap&&(g.anisotropyMap.value=p.anisotropyMap,t(p.anisotropyMap,g.anisotropyMapTransform))),g.specularIntensity.value=p.specularIntensity,g.specularColor.value.copy(p.specularColor),p.specularColorMap&&(g.specularColorMap.value=p.specularColorMap,t(p.specularColorMap,g.specularColorMapTransform)),p.specularIntensityMap&&(g.specularIntensityMap.value=p.specularIntensityMap,t(p.specularIntensityMap,g.specularIntensityMapTransform))}function m(g,p){p.matcap&&(g.matcap.value=p.matcap)}function _(g,p){const M=e.get(p).light;g.referencePosition.value.setFromMatrixPosition(M.matrixWorld),g.nearDistance.value=M.shadow.camera.near,g.farDistance.value=M.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:s}}function kx(i,e,t,n){let s={},r={},o=[];const a=i.getParameter(i.MAX_UNIFORM_BUFFER_BINDINGS);function c(M,v){const x=v.program;n.uniformBlockBinding(M,x)}function l(M,v){let x=s[M.id];x===void 0&&(m(M),x=u(M),s[M.id]=x,M.addEventListener("dispose",g));const L=v.program;n.updateUBOMapping(M,L);const T=e.render.frame;r[M.id]!==T&&(h(M),r[M.id]=T)}function u(M){const v=f();M.__bindingPointIndex=v;const x=i.createBuffer(),L=M.__size,T=M.usage;return i.bindBuffer(i.UNIFORM_BUFFER,x),i.bufferData(i.UNIFORM_BUFFER,L,T),i.bindBuffer(i.UNIFORM_BUFFER,null),i.bindBufferBase(i.UNIFORM_BUFFER,v,x),x}function f(){for(let M=0;M<a;M++)if(o.indexOf(M)===-1)return o.push(M),M;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function h(M){const v=s[M.id],x=M.uniforms,L=M.__cache;i.bindBuffer(i.UNIFORM_BUFFER,v);for(let T=0,R=x.length;T<R;T++){const I=Array.isArray(x[T])?x[T]:[x[T]];for(let w=0,S=I.length;w<S;w++){const P=I[w];if(d(P,T,w,L)===!0){const G=P.__offset,B=Array.isArray(P.value)?P.value:[P.value];let V=0;for(let j=0;j<B.length;j++){const W=B[j],ee=_(W);typeof W=="number"||typeof W=="boolean"?(P.__data[0]=W,i.bufferSubData(i.UNIFORM_BUFFER,G+V,P.__data)):W.isMatrix3?(P.__data[0]=W.elements[0],P.__data[1]=W.elements[1],P.__data[2]=W.elements[2],P.__data[3]=0,P.__data[4]=W.elements[3],P.__data[5]=W.elements[4],P.__data[6]=W.elements[5],P.__data[7]=0,P.__data[8]=W.elements[6],P.__data[9]=W.elements[7],P.__data[10]=W.elements[8],P.__data[11]=0):(W.toArray(P.__data,V),V+=ee.storage/Float32Array.BYTES_PER_ELEMENT)}i.bufferSubData(i.UNIFORM_BUFFER,G,P.__data)}}}i.bindBuffer(i.UNIFORM_BUFFER,null)}function d(M,v,x,L){const T=M.value,R=v+"_"+x;if(L[R]===void 0)return typeof T=="number"||typeof T=="boolean"?L[R]=T:L[R]=T.clone(),!0;{const I=L[R];if(typeof T=="number"||typeof T=="boolean"){if(I!==T)return L[R]=T,!0}else if(I.equals(T)===!1)return I.copy(T),!0}return!1}function m(M){const v=M.uniforms;let x=0;const L=16;for(let R=0,I=v.length;R<I;R++){const w=Array.isArray(v[R])?v[R]:[v[R]];for(let S=0,P=w.length;S<P;S++){const G=w[S],B=Array.isArray(G.value)?G.value:[G.value];for(let V=0,j=B.length;V<j;V++){const W=B[V],ee=_(W),O=x%L,re=O%ee.boundary,ue=O+re;x+=re,ue!==0&&L-ue<ee.storage&&(x+=L-ue),G.__data=new Float32Array(ee.storage/Float32Array.BYTES_PER_ELEMENT),G.__offset=x,x+=ee.storage}}}const T=x%L;return T>0&&(x+=L-T),M.__size=x,M.__cache={},this}function _(M){const v={boundary:0,storage:0};return typeof M=="number"||typeof M=="boolean"?(v.boundary=4,v.storage=4):M.isVector2?(v.boundary=8,v.storage=8):M.isVector3||M.isColor?(v.boundary=16,v.storage=12):M.isVector4?(v.boundary=16,v.storage=16):M.isMatrix3?(v.boundary=48,v.storage=48):M.isMatrix4?(v.boundary=64,v.storage=64):M.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",M),v}function g(M){const v=M.target;v.removeEventListener("dispose",g);const x=o.indexOf(v.__bindingPointIndex);o.splice(x,1),i.deleteBuffer(s[v.id]),delete s[v.id],delete r[v.id]}function p(){for(const M in s)i.deleteBuffer(s[M]);o=[],s={},r={}}return{bind:c,update:l,dispose:p}}class zx{constructor(e={}){const{canvas:t=Rp(),context:n=null,depth:s=!0,stencil:r=!1,alpha:o=!1,antialias:a=!1,premultipliedAlpha:c=!0,preserveDrawingBuffer:l=!1,powerPreference:u="default",failIfMajorPerformanceCaveat:f=!1,reverseDepthBuffer:h=!1}=e;this.isWebGLRenderer=!0;let d;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");d=n.getContextAttributes().alpha}else d=o;const m=new Uint32Array(4),_=new Int32Array(4);let g=null,p=null;const M=[],v=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=Nt,this.toneMapping=Di,this.toneMappingExposure=1;const x=this;let L=!1,T=0,R=0,I=null,w=-1,S=null;const P=new ht,G=new ht;let B=null;const V=new Ve(0);let j=0,W=t.width,ee=t.height,O=1,re=null,ue=null;const Me=new ht(0,0,W,ee),Ye=new ht(0,0,W,ee);let dt=!1;const $=new El;let ce=!1,Pe=!1;const fe=new De,ze=new De,$e=new b,qe=new ht,ct={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let J=!1;function oe(){return I===null?O:1}let C=n;function Fe(E,N){return t.getContext(E,N)}try{const E={alpha:!0,depth:s,stencil:r,antialias:a,premultipliedAlpha:c,preserveDrawingBuffer:l,powerPreference:u,failIfMajorPerformanceCaveat:f};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${dl}`),t.addEventListener("webglcontextlost",K,!1),t.addEventListener("webglcontextrestored",Se,!1),t.addEventListener("webglcontextcreationerror",ve,!1),C===null){const N="webgl2";if(C=Fe(N,E),C===null)throw Fe(N)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(E){throw console.error("THREE.WebGLRenderer: "+E.message),E}let ne,we,de,We,Ee,A,y,F,q,Q,Y,Ie,ge,be,rt,se,Ae,Xe,je,Re,at,tt,St,D;function xe(){ne=new X0(C),ne.init(),tt=new Px(C,ne),we=new k0(C,ne,e,tt),de=new Ax(C,ne),we.reverseDepthBuffer&&h&&de.buffers.depth.setReversed(!0),We=new j0(C),Ee=new fx,A=new Cx(C,ne,de,Ee,we,tt,We),y=new H0(x),F=new W0(x),q=new tm(C),St=new F0(C,q),Q=new q0(C,q,We,St),Y=new K0(C,Q,q,We),je=new $0(C,we,A),se=new z0(Ee),Ie=new hx(x,y,F,ne,we,St,se),ge=new Bx(x,Ee),be=new px,rt=new yx(ne),Xe=new O0(x,y,F,de,Y,d,c),Ae=new wx(x,Y,we),D=new kx(C,We,we,de),Re=new B0(C,ne,We),at=new Y0(C,ne,We),We.programs=Ie.programs,x.capabilities=we,x.extensions=ne,x.properties=Ee,x.renderLists=be,x.shadowMap=Ae,x.state=de,x.info=We}xe();const X=new Ox(x,C);this.xr=X,this.getContext=function(){return C},this.getContextAttributes=function(){return C.getContextAttributes()},this.forceContextLoss=function(){const E=ne.get("WEBGL_lose_context");E&&E.loseContext()},this.forceContextRestore=function(){const E=ne.get("WEBGL_lose_context");E&&E.restoreContext()},this.getPixelRatio=function(){return O},this.setPixelRatio=function(E){E!==void 0&&(O=E,this.setSize(W,ee,!1))},this.getSize=function(E){return E.set(W,ee)},this.setSize=function(E,N,z=!0){if(X.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}W=E,ee=N,t.width=Math.floor(E*O),t.height=Math.floor(N*O),z===!0&&(t.style.width=E+"px",t.style.height=N+"px"),this.setViewport(0,0,E,N)},this.getDrawingBufferSize=function(E){return E.set(W*O,ee*O).floor()},this.setDrawingBufferSize=function(E,N,z){W=E,ee=N,O=z,t.width=Math.floor(E*z),t.height=Math.floor(N*z),this.setViewport(0,0,E,N)},this.getCurrentViewport=function(E){return E.copy(P)},this.getViewport=function(E){return E.copy(Me)},this.setViewport=function(E,N,z,H){E.isVector4?Me.set(E.x,E.y,E.z,E.w):Me.set(E,N,z,H),de.viewport(P.copy(Me).multiplyScalar(O).round())},this.getScissor=function(E){return E.copy(Ye)},this.setScissor=function(E,N,z,H){E.isVector4?Ye.set(E.x,E.y,E.z,E.w):Ye.set(E,N,z,H),de.scissor(G.copy(Ye).multiplyScalar(O).round())},this.getScissorTest=function(){return dt},this.setScissorTest=function(E){de.setScissorTest(dt=E)},this.setOpaqueSort=function(E){re=E},this.setTransparentSort=function(E){ue=E},this.getClearColor=function(E){return E.copy(Xe.getClearColor())},this.setClearColor=function(){Xe.setClearColor.apply(Xe,arguments)},this.getClearAlpha=function(){return Xe.getClearAlpha()},this.setClearAlpha=function(){Xe.setClearAlpha.apply(Xe,arguments)},this.clear=function(E=!0,N=!0,z=!0){let H=0;if(E){let U=!1;if(I!==null){const le=I.texture.format;U=le===yl||le===vl||le===xl}if(U){const le=I.texture.type,ye=le===hi||le===es||le===Tr||le===Hs||le===ml||le===gl,Ne=Xe.getClearColor(),Ue=Xe.getClearAlpha(),Ke=Ne.r,Qe=Ne.g,Oe=Ne.b;ye?(m[0]=Ke,m[1]=Qe,m[2]=Oe,m[3]=Ue,C.clearBufferuiv(C.COLOR,0,m)):(_[0]=Ke,_[1]=Qe,_[2]=Oe,_[3]=Ue,C.clearBufferiv(C.COLOR,0,_))}else H|=C.COLOR_BUFFER_BIT}N&&(H|=C.DEPTH_BUFFER_BIT),z&&(H|=C.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),C.clear(H)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",K,!1),t.removeEventListener("webglcontextrestored",Se,!1),t.removeEventListener("webglcontextcreationerror",ve,!1),be.dispose(),rt.dispose(),Ee.dispose(),y.dispose(),F.dispose(),Y.dispose(),St.dispose(),D.dispose(),Ie.dispose(),X.dispose(),X.removeEventListener("sessionstart",Hl),X.removeEventListener("sessionend",Vl),zi.stop()};function K(E){E.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),L=!0}function Se(){console.log("THREE.WebGLRenderer: Context Restored."),L=!1;const E=We.autoReset,N=Ae.enabled,z=Ae.autoUpdate,H=Ae.needsUpdate,U=Ae.type;xe(),We.autoReset=E,Ae.enabled=N,Ae.autoUpdate=z,Ae.needsUpdate=H,Ae.type=U}function ve(E){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",E.statusMessage)}function Je(E){const N=E.target;N.removeEventListener("dispose",Je),Lt(N)}function Lt(E){Kt(E),Ee.remove(E)}function Kt(E){const N=Ee.get(E).programs;N!==void 0&&(N.forEach(function(z){Ie.releaseProgram(z)}),E.isShaderMaterial&&Ie.releaseShaderCache(E))}this.renderBufferDirect=function(E,N,z,H,U,le){N===null&&(N=ct);const ye=U.isMesh&&U.matrixWorld.determinant()<0,Ne=pd(E,N,z,H,U);de.setMaterial(H,ye);let Ue=z.index,Ke=1;if(H.wireframe===!0){if(Ue=Q.getWireframeAttribute(z),Ue===void 0)return;Ke=2}const Qe=z.drawRange,Oe=z.attributes.position;let lt=Qe.start*Ke,Et=(Qe.start+Qe.count)*Ke;le!==null&&(lt=Math.max(lt,le.start*Ke),Et=Math.min(Et,(le.start+le.count)*Ke)),Ue!==null?(lt=Math.max(lt,0),Et=Math.min(Et,Ue.count)):Oe!=null&&(lt=Math.max(lt,0),Et=Math.min(Et,Oe.count));const wt=Et-lt;if(wt<0||wt===1/0)return;St.setup(U,H,Ne,z,Ue);let cn,pt=Re;if(Ue!==null&&(cn=q.get(Ue),pt=at,pt.setIndex(cn)),U.isMesh)H.wireframe===!0?(de.setLineWidth(H.wireframeLinewidth*oe()),pt.setMode(C.LINES)):pt.setMode(C.TRIANGLES);else if(U.isLine){let Be=H.linewidth;Be===void 0&&(Be=1),de.setLineWidth(Be*oe()),U.isLineSegments?pt.setMode(C.LINES):U.isLineLoop?pt.setMode(C.LINE_LOOP):pt.setMode(C.LINE_STRIP)}else U.isPoints?pt.setMode(C.POINTS):U.isSprite&&pt.setMode(C.TRIANGLES);if(U.isBatchedMesh)if(U._multiDrawInstances!==null)pt.renderMultiDrawInstances(U._multiDrawStarts,U._multiDrawCounts,U._multiDrawCount,U._multiDrawInstances);else if(ne.get("WEBGL_multi_draw"))pt.renderMultiDraw(U._multiDrawStarts,U._multiDrawCounts,U._multiDrawCount);else{const Be=U._multiDrawStarts,jn=U._multiDrawCounts,mt=U._multiDrawCount,Rn=Ue?q.get(Ue).bytesPerElement:1,ls=Ee.get(H).currentProgram.getUniforms();for(let fn=0;fn<mt;fn++)ls.setValue(C,"_gl_DrawID",fn),pt.render(Be[fn]/Rn,jn[fn])}else if(U.isInstancedMesh)pt.renderInstances(lt,wt,U.count);else if(z.isInstancedBufferGeometry){const Be=z._maxInstanceCount!==void 0?z._maxInstanceCount:1/0,jn=Math.min(z.instanceCount,Be);pt.renderInstances(lt,wt,jn)}else pt.render(lt,wt)};function gt(E,N,z){E.transparent===!0&&E.side===mn&&E.forceSinglePass===!1?(E.side=sn,E.needsUpdate=!0,Hr(E,N,z),E.side=ui,E.needsUpdate=!0,Hr(E,N,z),E.side=mn):Hr(E,N,z)}this.compile=function(E,N,z=null){z===null&&(z=E),p=rt.get(z),p.init(N),v.push(p),z.traverseVisible(function(U){U.isLight&&U.layers.test(N.layers)&&(p.pushLight(U),U.castShadow&&p.pushShadow(U))}),E!==z&&E.traverseVisible(function(U){U.isLight&&U.layers.test(N.layers)&&(p.pushLight(U),U.castShadow&&p.pushShadow(U))}),p.setupLights();const H=new Set;return E.traverse(function(U){if(!(U.isMesh||U.isPoints||U.isLine||U.isSprite))return;const le=U.material;if(le)if(Array.isArray(le))for(let ye=0;ye<le.length;ye++){const Ne=le[ye];gt(Ne,z,U),H.add(Ne)}else gt(le,z,U),H.add(le)}),v.pop(),p=null,H},this.compileAsync=function(E,N,z=null){const H=this.compile(E,N,z);return new Promise(U=>{function le(){if(H.forEach(function(ye){Ee.get(ye).currentProgram.isReady()&&H.delete(ye)}),H.size===0){U(E);return}setTimeout(le,10)}ne.get("KHR_parallel_shader_compile")!==null?le():setTimeout(le,10)})};let An=null;function Yn(E){An&&An(E)}function Hl(){zi.stop()}function Vl(){zi.start()}const zi=new mf;zi.setAnimationLoop(Yn),typeof self<"u"&&zi.setContext(self),this.setAnimationLoop=function(E){An=E,X.setAnimationLoop(E),E===null?zi.stop():zi.start()},X.addEventListener("sessionstart",Hl),X.addEventListener("sessionend",Vl),this.render=function(E,N){if(N!==void 0&&N.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(L===!0)return;if(E.matrixWorldAutoUpdate===!0&&E.updateMatrixWorld(),N.parent===null&&N.matrixWorldAutoUpdate===!0&&N.updateMatrixWorld(),X.enabled===!0&&X.isPresenting===!0&&(X.cameraAutoUpdate===!0&&X.updateCamera(N),N=X.getCamera()),E.isScene===!0&&E.onBeforeRender(x,E,N,I),p=rt.get(E,v.length),p.init(N),v.push(p),ze.multiplyMatrices(N.projectionMatrix,N.matrixWorldInverse),$.setFromProjectionMatrix(ze),Pe=this.localClippingEnabled,ce=se.init(this.clippingPlanes,Pe),g=be.get(E,M.length),g.init(),M.push(g),X.enabled===!0&&X.isPresenting===!0){const le=x.xr.getDepthSensingMesh();le!==null&&ua(le,N,-1/0,x.sortObjects)}ua(E,N,0,x.sortObjects),g.finish(),x.sortObjects===!0&&g.sort(re,ue),J=X.enabled===!1||X.isPresenting===!1||X.hasDepthSensing()===!1,J&&Xe.addToRenderList(g,E),this.info.render.frame++,ce===!0&&se.beginShadows();const z=p.state.shadowsArray;Ae.render(z,E,N),ce===!0&&se.endShadows(),this.info.autoReset===!0&&this.info.reset();const H=g.opaque,U=g.transmissive;if(p.setupLights(),N.isArrayCamera){const le=N.cameras;if(U.length>0)for(let ye=0,Ne=le.length;ye<Ne;ye++){const Ue=le[ye];Wl(H,U,E,Ue)}J&&Xe.render(E);for(let ye=0,Ne=le.length;ye<Ne;ye++){const Ue=le[ye];Gl(g,E,Ue,Ue.viewport)}}else U.length>0&&Wl(H,U,E,N),J&&Xe.render(E),Gl(g,E,N);I!==null&&(A.updateMultisampleRenderTarget(I),A.updateRenderTargetMipmap(I)),E.isScene===!0&&E.onAfterRender(x,E,N),St.resetDefaultState(),w=-1,S=null,v.pop(),v.length>0?(p=v[v.length-1],ce===!0&&se.setGlobalState(x.clippingPlanes,p.state.camera)):p=null,M.pop(),M.length>0?g=M[M.length-1]:g=null};function ua(E,N,z,H){if(E.visible===!1)return;if(E.layers.test(N.layers)){if(E.isGroup)z=E.renderOrder;else if(E.isLOD)E.autoUpdate===!0&&E.update(N);else if(E.isLight)p.pushLight(E),E.castShadow&&p.pushShadow(E);else if(E.isSprite){if(!E.frustumCulled||$.intersectsSprite(E)){H&&qe.setFromMatrixPosition(E.matrixWorld).applyMatrix4(ze);const ye=Y.update(E),Ne=E.material;Ne.visible&&g.push(E,ye,Ne,z,qe.z,null)}}else if((E.isMesh||E.isLine||E.isPoints)&&(!E.frustumCulled||$.intersectsObject(E))){const ye=Y.update(E),Ne=E.material;if(H&&(E.boundingSphere!==void 0?(E.boundingSphere===null&&E.computeBoundingSphere(),qe.copy(E.boundingSphere.center)):(ye.boundingSphere===null&&ye.computeBoundingSphere(),qe.copy(ye.boundingSphere.center)),qe.applyMatrix4(E.matrixWorld).applyMatrix4(ze)),Array.isArray(Ne)){const Ue=ye.groups;for(let Ke=0,Qe=Ue.length;Ke<Qe;Ke++){const Oe=Ue[Ke],lt=Ne[Oe.materialIndex];lt&&lt.visible&&g.push(E,ye,lt,z,qe.z,Oe)}}else Ne.visible&&g.push(E,ye,Ne,z,qe.z,null)}}const le=E.children;for(let ye=0,Ne=le.length;ye<Ne;ye++)ua(le[ye],N,z,H)}function Gl(E,N,z,H){const U=E.opaque,le=E.transmissive,ye=E.transparent;p.setupLightsView(z),ce===!0&&se.setGlobalState(x.clippingPlanes,z),H&&de.viewport(P.copy(H)),U.length>0&&zr(U,N,z),le.length>0&&zr(le,N,z),ye.length>0&&zr(ye,N,z),de.buffers.depth.setTest(!0),de.buffers.depth.setMask(!0),de.buffers.color.setMask(!0),de.setPolygonOffset(!1)}function Wl(E,N,z,H){if((z.isScene===!0?z.overrideMaterial:null)!==null)return;p.state.transmissionRenderTarget[H.id]===void 0&&(p.state.transmissionRenderTarget[H.id]=new ts(1,1,{generateMipmaps:!0,type:ne.has("EXT_color_buffer_half_float")||ne.has("EXT_color_buffer_float")?Dr:hi,minFilter:oi,samples:4,stencilBuffer:r,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:ot.workingColorSpace}));const le=p.state.transmissionRenderTarget[H.id],ye=H.viewport||P;le.setSize(ye.z,ye.w);const Ne=x.getRenderTarget();x.setRenderTarget(le),x.getClearColor(V),j=x.getClearAlpha(),j<1&&x.setClearColor(16777215,.5),x.clear(),J&&Xe.render(z);const Ue=x.toneMapping;x.toneMapping=Di;const Ke=H.viewport;if(H.viewport!==void 0&&(H.viewport=void 0),p.setupLightsView(H),ce===!0&&se.setGlobalState(x.clippingPlanes,H),zr(E,z,H),A.updateMultisampleRenderTarget(le),A.updateRenderTargetMipmap(le),ne.has("WEBGL_multisampled_render_to_texture")===!1){let Qe=!1;for(let Oe=0,lt=N.length;Oe<lt;Oe++){const Et=N[Oe],wt=Et.object,cn=Et.geometry,pt=Et.material,Be=Et.group;if(pt.side===mn&&wt.layers.test(H.layers)){const jn=pt.side;pt.side=sn,pt.needsUpdate=!0,Xl(wt,z,H,cn,pt,Be),pt.side=jn,pt.needsUpdate=!0,Qe=!0}}Qe===!0&&(A.updateMultisampleRenderTarget(le),A.updateRenderTargetMipmap(le))}x.setRenderTarget(Ne),x.setClearColor(V,j),Ke!==void 0&&(H.viewport=Ke),x.toneMapping=Ue}function zr(E,N,z){const H=N.isScene===!0?N.overrideMaterial:null;for(let U=0,le=E.length;U<le;U++){const ye=E[U],Ne=ye.object,Ue=ye.geometry,Ke=H===null?ye.material:H,Qe=ye.group;Ne.layers.test(z.layers)&&Xl(Ne,N,z,Ue,Ke,Qe)}}function Xl(E,N,z,H,U,le){E.onBeforeRender(x,N,z,H,U,le),E.modelViewMatrix.multiplyMatrices(z.matrixWorldInverse,E.matrixWorld),E.normalMatrix.getNormalMatrix(E.modelViewMatrix),U.onBeforeRender(x,N,z,H,E,le),U.transparent===!0&&U.side===mn&&U.forceSinglePass===!1?(U.side=sn,U.needsUpdate=!0,x.renderBufferDirect(z,N,H,U,E,le),U.side=ui,U.needsUpdate=!0,x.renderBufferDirect(z,N,H,U,E,le),U.side=mn):x.renderBufferDirect(z,N,H,U,E,le),E.onAfterRender(x,N,z,H,U,le)}function Hr(E,N,z){N.isScene!==!0&&(N=ct);const H=Ee.get(E),U=p.state.lights,le=p.state.shadowsArray,ye=U.state.version,Ne=Ie.getParameters(E,U.state,le,N,z),Ue=Ie.getProgramCacheKey(Ne);let Ke=H.programs;H.environment=E.isMeshStandardMaterial?N.environment:null,H.fog=N.fog,H.envMap=(E.isMeshStandardMaterial?F:y).get(E.envMap||H.environment),H.envMapRotation=H.environment!==null&&E.envMap===null?N.environmentRotation:E.envMapRotation,Ke===void 0&&(E.addEventListener("dispose",Je),Ke=new Map,H.programs=Ke);let Qe=Ke.get(Ue);if(Qe!==void 0){if(H.currentProgram===Qe&&H.lightsStateVersion===ye)return Yl(E,Ne),Qe}else Ne.uniforms=Ie.getUniforms(E),E.onBeforeCompile(Ne,x),Qe=Ie.acquireProgram(Ne,Ue),Ke.set(Ue,Qe),H.uniforms=Ne.uniforms;const Oe=H.uniforms;return(!E.isShaderMaterial&&!E.isRawShaderMaterial||E.clipping===!0)&&(Oe.clippingPlanes=se.uniform),Yl(E,Ne),H.needsLights=gd(E),H.lightsStateVersion=ye,H.needsLights&&(Oe.ambientLightColor.value=U.state.ambient,Oe.lightProbe.value=U.state.probe,Oe.directionalLights.value=U.state.directional,Oe.directionalLightShadows.value=U.state.directionalShadow,Oe.spotLights.value=U.state.spot,Oe.spotLightShadows.value=U.state.spotShadow,Oe.rectAreaLights.value=U.state.rectArea,Oe.ltc_1.value=U.state.rectAreaLTC1,Oe.ltc_2.value=U.state.rectAreaLTC2,Oe.pointLights.value=U.state.point,Oe.pointLightShadows.value=U.state.pointShadow,Oe.hemisphereLights.value=U.state.hemi,Oe.directionalShadowMap.value=U.state.directionalShadowMap,Oe.directionalShadowMatrix.value=U.state.directionalShadowMatrix,Oe.spotShadowMap.value=U.state.spotShadowMap,Oe.spotLightMatrix.value=U.state.spotLightMatrix,Oe.spotLightMap.value=U.state.spotLightMap,Oe.pointShadowMap.value=U.state.pointShadowMap,Oe.pointShadowMatrix.value=U.state.pointShadowMatrix),H.currentProgram=Qe,H.uniformsList=null,Qe}function ql(E){if(E.uniformsList===null){const N=E.currentProgram.getUniforms();E.uniformsList=Do.seqWithValue(N.seq,E.uniforms)}return E.uniformsList}function Yl(E,N){const z=Ee.get(E);z.outputColorSpace=N.outputColorSpace,z.batching=N.batching,z.batchingColor=N.batchingColor,z.instancing=N.instancing,z.instancingColor=N.instancingColor,z.instancingMorph=N.instancingMorph,z.skinning=N.skinning,z.morphTargets=N.morphTargets,z.morphNormals=N.morphNormals,z.morphColors=N.morphColors,z.morphTargetsCount=N.morphTargetsCount,z.numClippingPlanes=N.numClippingPlanes,z.numIntersection=N.numClipIntersection,z.vertexAlphas=N.vertexAlphas,z.vertexTangents=N.vertexTangents,z.toneMapping=N.toneMapping}function pd(E,N,z,H,U){N.isScene!==!0&&(N=ct),A.resetTextureUnits();const le=N.fog,ye=H.isMeshStandardMaterial?N.environment:null,Ne=I===null?x.outputColorSpace:I.isXRRenderTarget===!0?I.texture.colorSpace:en,Ue=(H.isMeshStandardMaterial?F:y).get(H.envMap||ye),Ke=H.vertexColors===!0&&!!z.attributes.color&&z.attributes.color.itemSize===4,Qe=!!z.attributes.tangent&&(!!H.normalMap||H.anisotropy>0),Oe=!!z.morphAttributes.position,lt=!!z.morphAttributes.normal,Et=!!z.morphAttributes.color;let wt=Di;H.toneMapped&&(I===null||I.isXRRenderTarget===!0)&&(wt=x.toneMapping);const cn=z.morphAttributes.position||z.morphAttributes.normal||z.morphAttributes.color,pt=cn!==void 0?cn.length:0,Be=Ee.get(H),jn=p.state.lights;if(ce===!0&&(Pe===!0||E!==S)){const vn=E===S&&H.id===w;se.setState(H,E,vn)}let mt=!1;H.version===Be.__version?(Be.needsLights&&Be.lightsStateVersion!==jn.state.version||Be.outputColorSpace!==Ne||U.isBatchedMesh&&Be.batching===!1||!U.isBatchedMesh&&Be.batching===!0||U.isBatchedMesh&&Be.batchingColor===!0&&U.colorTexture===null||U.isBatchedMesh&&Be.batchingColor===!1&&U.colorTexture!==null||U.isInstancedMesh&&Be.instancing===!1||!U.isInstancedMesh&&Be.instancing===!0||U.isSkinnedMesh&&Be.skinning===!1||!U.isSkinnedMesh&&Be.skinning===!0||U.isInstancedMesh&&Be.instancingColor===!0&&U.instanceColor===null||U.isInstancedMesh&&Be.instancingColor===!1&&U.instanceColor!==null||U.isInstancedMesh&&Be.instancingMorph===!0&&U.morphTexture===null||U.isInstancedMesh&&Be.instancingMorph===!1&&U.morphTexture!==null||Be.envMap!==Ue||H.fog===!0&&Be.fog!==le||Be.numClippingPlanes!==void 0&&(Be.numClippingPlanes!==se.numPlanes||Be.numIntersection!==se.numIntersection)||Be.vertexAlphas!==Ke||Be.vertexTangents!==Qe||Be.morphTargets!==Oe||Be.morphNormals!==lt||Be.morphColors!==Et||Be.toneMapping!==wt||Be.morphTargetsCount!==pt)&&(mt=!0):(mt=!0,Be.__version=H.version);let Rn=Be.currentProgram;mt===!0&&(Rn=Hr(H,N,U));let ls=!1,fn=!1,nr=!1;const Tt=Rn.getUniforms(),Bn=Be.uniforms;if(de.useProgram(Rn.program)&&(ls=!0,fn=!0,nr=!0),H.id!==w&&(w=H.id,fn=!0),ls||S!==E){de.buffers.depth.getReversed()?(fe.copy(E.projectionMatrix),Pp(fe),Lp(fe),Tt.setValue(C,"projectionMatrix",fe)):Tt.setValue(C,"projectionMatrix",E.projectionMatrix),Tt.setValue(C,"viewMatrix",E.matrixWorldInverse);const mi=Tt.map.cameraPosition;mi!==void 0&&mi.setValue(C,$e.setFromMatrixPosition(E.matrixWorld)),we.logarithmicDepthBuffer&&Tt.setValue(C,"logDepthBufFC",2/(Math.log(E.far+1)/Math.LN2)),(H.isMeshPhongMaterial||H.isMeshToonMaterial||H.isMeshLambertMaterial||H.isMeshBasicMaterial||H.isMeshStandardMaterial||H.isShaderMaterial)&&Tt.setValue(C,"isOrthographic",E.isOrthographicCamera===!0),S!==E&&(S=E,fn=!0,nr=!0)}if(U.isSkinnedMesh){Tt.setOptional(C,U,"bindMatrix"),Tt.setOptional(C,U,"bindMatrixInverse");const vn=U.skeleton;vn&&(vn.boneTexture===null&&vn.computeBoneTexture(),Tt.setValue(C,"boneTexture",vn.boneTexture,A))}U.isBatchedMesh&&(Tt.setOptional(C,U,"batchingTexture"),Tt.setValue(C,"batchingTexture",U._matricesTexture,A),Tt.setOptional(C,U,"batchingIdTexture"),Tt.setValue(C,"batchingIdTexture",U._indirectTexture,A),Tt.setOptional(C,U,"batchingColorTexture"),U._colorsTexture!==null&&Tt.setValue(C,"batchingColorTexture",U._colorsTexture,A));const ir=z.morphAttributes;if((ir.position!==void 0||ir.normal!==void 0||ir.color!==void 0)&&je.update(U,z,Rn),(fn||Be.receiveShadow!==U.receiveShadow)&&(Be.receiveShadow=U.receiveShadow,Tt.setValue(C,"receiveShadow",U.receiveShadow)),H.isMeshGouraudMaterial&&H.envMap!==null&&(Bn.envMap.value=Ue,Bn.flipEnvMap.value=Ue.isCubeTexture&&Ue.isRenderTargetTexture===!1?-1:1),H.isMeshStandardMaterial&&H.envMap===null&&N.environment!==null&&(Bn.envMapIntensity.value=N.environmentIntensity),fn&&(Tt.setValue(C,"toneMappingExposure",x.toneMappingExposure),Be.needsLights&&md(Bn,nr),le&&H.fog===!0&&ge.refreshFogUniforms(Bn,le),ge.refreshMaterialUniforms(Bn,H,O,ee,p.state.transmissionRenderTarget[E.id]),Do.upload(C,ql(Be),Bn,A)),H.isShaderMaterial&&H.uniformsNeedUpdate===!0&&(Do.upload(C,ql(Be),Bn,A),H.uniformsNeedUpdate=!1),H.isSpriteMaterial&&Tt.setValue(C,"center",U.center),Tt.setValue(C,"modelViewMatrix",U.modelViewMatrix),Tt.setValue(C,"normalMatrix",U.normalMatrix),Tt.setValue(C,"modelMatrix",U.matrixWorld),H.isShaderMaterial||H.isRawShaderMaterial){const vn=H.uniformsGroups;for(let mi=0,gi=vn.length;mi<gi;mi++){const jl=vn[mi];D.update(jl,Rn),D.bind(jl,Rn)}}return Rn}function md(E,N){E.ambientLightColor.needsUpdate=N,E.lightProbe.needsUpdate=N,E.directionalLights.needsUpdate=N,E.directionalLightShadows.needsUpdate=N,E.pointLights.needsUpdate=N,E.pointLightShadows.needsUpdate=N,E.spotLights.needsUpdate=N,E.spotLightShadows.needsUpdate=N,E.rectAreaLights.needsUpdate=N,E.hemisphereLights.needsUpdate=N}function gd(E){return E.isMeshLambertMaterial||E.isMeshToonMaterial||E.isMeshPhongMaterial||E.isMeshStandardMaterial||E.isShadowMaterial||E.isShaderMaterial&&E.lights===!0}this.getActiveCubeFace=function(){return T},this.getActiveMipmapLevel=function(){return R},this.getRenderTarget=function(){return I},this.setRenderTargetTextures=function(E,N,z){Ee.get(E.texture).__webglTexture=N,Ee.get(E.depthTexture).__webglTexture=z;const H=Ee.get(E);H.__hasExternalTextures=!0,H.__autoAllocateDepthBuffer=z===void 0,H.__autoAllocateDepthBuffer||ne.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),H.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(E,N){const z=Ee.get(E);z.__webglFramebuffer=N,z.__useDefaultFramebuffer=N===void 0},this.setRenderTarget=function(E,N=0,z=0){I=E,T=N,R=z;let H=!0,U=null,le=!1,ye=!1;if(E){const Ue=Ee.get(E);if(Ue.__useDefaultFramebuffer!==void 0)de.bindFramebuffer(C.FRAMEBUFFER,null),H=!1;else if(Ue.__webglFramebuffer===void 0)A.setupRenderTarget(E);else if(Ue.__hasExternalTextures)A.rebindTextures(E,Ee.get(E.texture).__webglTexture,Ee.get(E.depthTexture).__webglTexture);else if(E.depthBuffer){const Oe=E.depthTexture;if(Ue.__boundDepthTexture!==Oe){if(Oe!==null&&Ee.has(Oe)&&(E.width!==Oe.image.width||E.height!==Oe.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");A.setupDepthRenderbuffer(E)}}const Ke=E.texture;(Ke.isData3DTexture||Ke.isDataArrayTexture||Ke.isCompressedArrayTexture)&&(ye=!0);const Qe=Ee.get(E).__webglFramebuffer;E.isWebGLCubeRenderTarget?(Array.isArray(Qe[N])?U=Qe[N][z]:U=Qe[N],le=!0):E.samples>0&&A.useMultisampledRTT(E)===!1?U=Ee.get(E).__webglMultisampledFramebuffer:Array.isArray(Qe)?U=Qe[z]:U=Qe,P.copy(E.viewport),G.copy(E.scissor),B=E.scissorTest}else P.copy(Me).multiplyScalar(O).floor(),G.copy(Ye).multiplyScalar(O).floor(),B=dt;if(de.bindFramebuffer(C.FRAMEBUFFER,U)&&H&&de.drawBuffers(E,U),de.viewport(P),de.scissor(G),de.setScissorTest(B),le){const Ue=Ee.get(E.texture);C.framebufferTexture2D(C.FRAMEBUFFER,C.COLOR_ATTACHMENT0,C.TEXTURE_CUBE_MAP_POSITIVE_X+N,Ue.__webglTexture,z)}else if(ye){const Ue=Ee.get(E.texture),Ke=N||0;C.framebufferTextureLayer(C.FRAMEBUFFER,C.COLOR_ATTACHMENT0,Ue.__webglTexture,z||0,Ke)}w=-1},this.readRenderTargetPixels=function(E,N,z,H,U,le,ye){if(!(E&&E.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let Ne=Ee.get(E).__webglFramebuffer;if(E.isWebGLCubeRenderTarget&&ye!==void 0&&(Ne=Ne[ye]),Ne){de.bindFramebuffer(C.FRAMEBUFFER,Ne);try{const Ue=E.texture,Ke=Ue.format,Qe=Ue.type;if(!we.textureFormatReadable(Ke)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!we.textureTypeReadable(Qe)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}N>=0&&N<=E.width-H&&z>=0&&z<=E.height-U&&C.readPixels(N,z,H,U,tt.convert(Ke),tt.convert(Qe),le)}finally{const Ue=I!==null?Ee.get(I).__webglFramebuffer:null;de.bindFramebuffer(C.FRAMEBUFFER,Ue)}}},this.readRenderTargetPixelsAsync=async function(E,N,z,H,U,le,ye){if(!(E&&E.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let Ne=Ee.get(E).__webglFramebuffer;if(E.isWebGLCubeRenderTarget&&ye!==void 0&&(Ne=Ne[ye]),Ne){const Ue=E.texture,Ke=Ue.format,Qe=Ue.type;if(!we.textureFormatReadable(Ke))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!we.textureTypeReadable(Qe))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(N>=0&&N<=E.width-H&&z>=0&&z<=E.height-U){de.bindFramebuffer(C.FRAMEBUFFER,Ne);const Oe=C.createBuffer();C.bindBuffer(C.PIXEL_PACK_BUFFER,Oe),C.bufferData(C.PIXEL_PACK_BUFFER,le.byteLength,C.STREAM_READ),C.readPixels(N,z,H,U,tt.convert(Ke),tt.convert(Qe),0);const lt=I!==null?Ee.get(I).__webglFramebuffer:null;de.bindFramebuffer(C.FRAMEBUFFER,lt);const Et=C.fenceSync(C.SYNC_GPU_COMMANDS_COMPLETE,0);return C.flush(),await Cp(C,Et,4),C.bindBuffer(C.PIXEL_PACK_BUFFER,Oe),C.getBufferSubData(C.PIXEL_PACK_BUFFER,0,le),C.deleteBuffer(Oe),C.deleteSync(Et),le}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(E,N=null,z=0){E.isTexture!==!0&&(vr("WebGLRenderer: copyFramebufferToTexture function signature has changed."),N=arguments[0]||null,E=arguments[1]);const H=Math.pow(2,-z),U=Math.floor(E.image.width*H),le=Math.floor(E.image.height*H),ye=N!==null?N.x:0,Ne=N!==null?N.y:0;A.setTexture2D(E,0),C.copyTexSubImage2D(C.TEXTURE_2D,z,0,0,ye,Ne,U,le),de.unbindTexture()},this.copyTextureToTexture=function(E,N,z=null,H=null,U=0){E.isTexture!==!0&&(vr("WebGLRenderer: copyTextureToTexture function signature has changed."),H=arguments[0]||null,E=arguments[1],N=arguments[2],U=arguments[3]||0,z=null);let le,ye,Ne,Ue,Ke,Qe,Oe,lt,Et;const wt=E.isCompressedTexture?E.mipmaps[U]:E.image;z!==null?(le=z.max.x-z.min.x,ye=z.max.y-z.min.y,Ne=z.isBox3?z.max.z-z.min.z:1,Ue=z.min.x,Ke=z.min.y,Qe=z.isBox3?z.min.z:0):(le=wt.width,ye=wt.height,Ne=wt.depth||1,Ue=0,Ke=0,Qe=0),H!==null?(Oe=H.x,lt=H.y,Et=H.z):(Oe=0,lt=0,Et=0);const cn=tt.convert(N.format),pt=tt.convert(N.type);let Be;N.isData3DTexture?(A.setTexture3D(N,0),Be=C.TEXTURE_3D):N.isDataArrayTexture||N.isCompressedArrayTexture?(A.setTexture2DArray(N,0),Be=C.TEXTURE_2D_ARRAY):(A.setTexture2D(N,0),Be=C.TEXTURE_2D),C.pixelStorei(C.UNPACK_FLIP_Y_WEBGL,N.flipY),C.pixelStorei(C.UNPACK_PREMULTIPLY_ALPHA_WEBGL,N.premultiplyAlpha),C.pixelStorei(C.UNPACK_ALIGNMENT,N.unpackAlignment);const jn=C.getParameter(C.UNPACK_ROW_LENGTH),mt=C.getParameter(C.UNPACK_IMAGE_HEIGHT),Rn=C.getParameter(C.UNPACK_SKIP_PIXELS),ls=C.getParameter(C.UNPACK_SKIP_ROWS),fn=C.getParameter(C.UNPACK_SKIP_IMAGES);C.pixelStorei(C.UNPACK_ROW_LENGTH,wt.width),C.pixelStorei(C.UNPACK_IMAGE_HEIGHT,wt.height),C.pixelStorei(C.UNPACK_SKIP_PIXELS,Ue),C.pixelStorei(C.UNPACK_SKIP_ROWS,Ke),C.pixelStorei(C.UNPACK_SKIP_IMAGES,Qe);const nr=E.isDataArrayTexture||E.isData3DTexture,Tt=N.isDataArrayTexture||N.isData3DTexture;if(E.isRenderTargetTexture||E.isDepthTexture){const Bn=Ee.get(E),ir=Ee.get(N),vn=Ee.get(Bn.__renderTarget),mi=Ee.get(ir.__renderTarget);de.bindFramebuffer(C.READ_FRAMEBUFFER,vn.__webglFramebuffer),de.bindFramebuffer(C.DRAW_FRAMEBUFFER,mi.__webglFramebuffer);for(let gi=0;gi<Ne;gi++)nr&&C.framebufferTextureLayer(C.READ_FRAMEBUFFER,C.COLOR_ATTACHMENT0,Ee.get(E).__webglTexture,U,Qe+gi),E.isDepthTexture?(Tt&&C.framebufferTextureLayer(C.DRAW_FRAMEBUFFER,C.COLOR_ATTACHMENT0,Ee.get(N).__webglTexture,U,Et+gi),C.blitFramebuffer(Ue,Ke,le,ye,Oe,lt,le,ye,C.DEPTH_BUFFER_BIT,C.NEAREST)):Tt?C.copyTexSubImage3D(Be,U,Oe,lt,Et+gi,Ue,Ke,le,ye):C.copyTexSubImage2D(Be,U,Oe,lt,Et+gi,Ue,Ke,le,ye);de.bindFramebuffer(C.READ_FRAMEBUFFER,null),de.bindFramebuffer(C.DRAW_FRAMEBUFFER,null)}else Tt?E.isDataTexture||E.isData3DTexture?C.texSubImage3D(Be,U,Oe,lt,Et,le,ye,Ne,cn,pt,wt.data):N.isCompressedArrayTexture?C.compressedTexSubImage3D(Be,U,Oe,lt,Et,le,ye,Ne,cn,wt.data):C.texSubImage3D(Be,U,Oe,lt,Et,le,ye,Ne,cn,pt,wt):E.isDataTexture?C.texSubImage2D(C.TEXTURE_2D,U,Oe,lt,le,ye,cn,pt,wt.data):E.isCompressedTexture?C.compressedTexSubImage2D(C.TEXTURE_2D,U,Oe,lt,wt.width,wt.height,cn,wt.data):C.texSubImage2D(C.TEXTURE_2D,U,Oe,lt,le,ye,cn,pt,wt);C.pixelStorei(C.UNPACK_ROW_LENGTH,jn),C.pixelStorei(C.UNPACK_IMAGE_HEIGHT,mt),C.pixelStorei(C.UNPACK_SKIP_PIXELS,Rn),C.pixelStorei(C.UNPACK_SKIP_ROWS,ls),C.pixelStorei(C.UNPACK_SKIP_IMAGES,fn),U===0&&N.generateMipmaps&&C.generateMipmap(Be),de.unbindTexture()},this.copyTextureToTexture3D=function(E,N,z=null,H=null,U=0){return E.isTexture!==!0&&(vr("WebGLRenderer: copyTextureToTexture3D function signature has changed."),z=arguments[0]||null,H=arguments[1]||null,E=arguments[2],N=arguments[3],U=arguments[4]||0),vr('WebGLRenderer: copyTextureToTexture3D function has been deprecated. Use "copyTextureToTexture" instead.'),this.copyTextureToTexture(E,N,z,H,U)},this.initRenderTarget=function(E){Ee.get(E).__webglFramebuffer===void 0&&A.setupRenderTarget(E)},this.initTexture=function(E){E.isCubeTexture?A.setTextureCube(E,0):E.isData3DTexture?A.setTexture3D(E,0):E.isDataArrayTexture||E.isCompressedArrayTexture?A.setTexture2DArray(E,0):A.setTexture2D(E,0),de.unbindTexture()},this.resetState=function(){T=0,R=0,I=null,de.reset(),St.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return ai}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorspace=ot._getDrawingBufferColorSpace(e),t.unpackColorSpace=ot._getUnpackColorSpace()}}class Hx extends At{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new Un,this.environmentIntensity=1,this.environmentRotation=new Un,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class Vx{constructor(e,t){this.isInterleavedBuffer=!0,this.array=e,this.stride=t,this.count=e!==void 0?e.length/t:0,this.usage=Jc,this.updateRanges=[],this.version=0,this.uuid=wn()}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.array=new e.array.constructor(e.array),this.count=e.count,this.stride=e.stride,this.usage=e.usage,this}copyAt(e,t,n){e*=this.stride,n*=t.stride;for(let s=0,r=this.stride;s<r;s++)this.array[e+s]=t.array[n+s];return this}set(e,t=0){return this.array.set(e,t),this}clone(e){e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=wn()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=this.array.slice(0).buffer);const t=new this.array.constructor(e.arrayBuffers[this.array.buffer._uuid]),n=new this.constructor(t,this.stride);return n.setUsage(this.usage),n}onUpload(e){return this.onUploadCallback=e,this}toJSON(e){return e.arrayBuffers===void 0&&(e.arrayBuffers={}),this.array.buffer._uuid===void 0&&(this.array.buffer._uuid=wn()),e.arrayBuffers[this.array.buffer._uuid]===void 0&&(e.arrayBuffers[this.array.buffer._uuid]=Array.from(new Uint32Array(this.array.buffer))),{uuid:this.uuid,buffer:this.array.buffer._uuid,type:this.array.constructor.name,stride:this.stride}}}const tn=new b;class wl{constructor(e,t,n,s=!1){this.isInterleavedBufferAttribute=!0,this.name="",this.data=e,this.itemSize=t,this.offset=n,this.normalized=s}get count(){return this.data.count}get array(){return this.data.array}set needsUpdate(e){this.data.needsUpdate=e}applyMatrix4(e){for(let t=0,n=this.data.count;t<n;t++)tn.fromBufferAttribute(this,t),tn.applyMatrix4(e),this.setXYZ(t,tn.x,tn.y,tn.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)tn.fromBufferAttribute(this,t),tn.applyNormalMatrix(e),this.setXYZ(t,tn.x,tn.y,tn.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)tn.fromBufferAttribute(this,t),tn.transformDirection(e),this.setXYZ(t,tn.x,tn.y,tn.z);return this}getComponent(e,t){let n=this.array[e*this.data.stride+this.offset+t];return this.normalized&&(n=In(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=_t(n,this.array)),this.data.array[e*this.data.stride+this.offset+t]=n,this}setX(e,t){return this.normalized&&(t=_t(t,this.array)),this.data.array[e*this.data.stride+this.offset]=t,this}setY(e,t){return this.normalized&&(t=_t(t,this.array)),this.data.array[e*this.data.stride+this.offset+1]=t,this}setZ(e,t){return this.normalized&&(t=_t(t,this.array)),this.data.array[e*this.data.stride+this.offset+2]=t,this}setW(e,t){return this.normalized&&(t=_t(t,this.array)),this.data.array[e*this.data.stride+this.offset+3]=t,this}getX(e){let t=this.data.array[e*this.data.stride+this.offset];return this.normalized&&(t=In(t,this.array)),t}getY(e){let t=this.data.array[e*this.data.stride+this.offset+1];return this.normalized&&(t=In(t,this.array)),t}getZ(e){let t=this.data.array[e*this.data.stride+this.offset+2];return this.normalized&&(t=In(t,this.array)),t}getW(e){let t=this.data.array[e*this.data.stride+this.offset+3];return this.normalized&&(t=In(t,this.array)),t}setXY(e,t,n){return e=e*this.data.stride+this.offset,this.normalized&&(t=_t(t,this.array),n=_t(n,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this}setXYZ(e,t,n,s){return e=e*this.data.stride+this.offset,this.normalized&&(t=_t(t,this.array),n=_t(n,this.array),s=_t(s,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this}setXYZW(e,t,n,s,r){return e=e*this.data.stride+this.offset,this.normalized&&(t=_t(t,this.array),n=_t(n,this.array),s=_t(s,this.array),r=_t(r,this.array)),this.data.array[e+0]=t,this.data.array[e+1]=n,this.data.array[e+2]=s,this.data.array[e+3]=r,this}clone(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.clone(): Cloning an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return new Xt(new this.array.constructor(t),this.itemSize,this.normalized)}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.clone(e)),new wl(e.interleavedBuffers[this.data.uuid],this.itemSize,this.offset,this.normalized)}toJSON(e){if(e===void 0){console.log("THREE.InterleavedBufferAttribute.toJSON(): Serializing an interleaved buffer attribute will de-interleave buffer data.");const t=[];for(let n=0;n<this.count;n++){const s=n*this.data.stride+this.offset;for(let r=0;r<this.itemSize;r++)t.push(this.data.array[s+r])}return{itemSize:this.itemSize,type:this.array.constructor.name,array:t,normalized:this.normalized}}else return e.interleavedBuffers===void 0&&(e.interleavedBuffers={}),e.interleavedBuffers[this.data.uuid]===void 0&&(e.interleavedBuffers[this.data.uuid]=this.data.toJSON(e)),{isInterleavedBufferAttribute:!0,itemSize:this.itemSize,data:this.data.uuid,offset:this.offset,normalized:this.normalized}}}const Zu=new b,Ju=new ht,Qu=new ht,Gx=new b,eh=new De,co=new b,ka=new Gn,th=new De,za=new Ko;class Tl extends Gt{constructor(e,t){super(e,t),this.isSkinnedMesh=!0,this.type="SkinnedMesh",this.bindMode=Ql,this.bindMatrix=new De,this.bindMatrixInverse=new De,this.boundingBox=null,this.boundingSphere=null}computeBoundingBox(){const e=this.geometry;this.boundingBox===null&&(this.boundingBox=new on),this.boundingBox.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,co),this.boundingBox.expandByPoint(co)}computeBoundingSphere(){const e=this.geometry;this.boundingSphere===null&&(this.boundingSphere=new Gn),this.boundingSphere.makeEmpty();const t=e.getAttribute("position");for(let n=0;n<t.count;n++)this.getVertexPosition(n,co),this.boundingSphere.expandByPoint(co)}copy(e,t){return super.copy(e,t),this.bindMode=e.bindMode,this.bindMatrix.copy(e.bindMatrix),this.bindMatrixInverse.copy(e.bindMatrixInverse),this.skeleton=e.skeleton,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}raycast(e,t){const n=this.material,s=this.matrixWorld;n!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),ka.copy(this.boundingSphere),ka.applyMatrix4(s),e.ray.intersectsSphere(ka)!==!1&&(th.copy(s).invert(),za.copy(e.ray).applyMatrix4(th),!(this.boundingBox!==null&&za.intersectsBox(this.boundingBox)===!1)&&this._computeIntersections(e,t,za)))}getVertexPosition(e,t){return super.getVertexPosition(e,t),this.applyBoneTransform(e,t),t}bind(e,t){this.skeleton=e,t===void 0&&(this.updateMatrixWorld(!0),this.skeleton.calculateInverses(),t=this.matrixWorld),this.bindMatrix.copy(t),this.bindMatrixInverse.copy(t).invert()}pose(){this.skeleton.pose()}normalizeSkinWeights(){const e=new ht,t=this.geometry.attributes.skinWeight;for(let n=0,s=t.count;n<s;n++){e.fromBufferAttribute(t,n);const r=1/e.manhattanLength();r!==1/0?e.multiplyScalar(r):e.set(1,0,0,0),t.setXYZW(n,e.x,e.y,e.z,e.w)}}updateMatrixWorld(e){super.updateMatrixWorld(e),this.bindMode===Ql?this.bindMatrixInverse.copy(this.matrixWorld).invert():this.bindMode===Qd?this.bindMatrixInverse.copy(this.bindMatrix).invert():console.warn("THREE.SkinnedMesh: Unrecognized bindMode: "+this.bindMode)}applyBoneTransform(e,t){const n=this.skeleton,s=this.geometry;Ju.fromBufferAttribute(s.attributes.skinIndex,e),Qu.fromBufferAttribute(s.attributes.skinWeight,e),Zu.copy(t).applyMatrix4(this.bindMatrix),t.set(0,0,0);for(let r=0;r<4;r++){const o=Qu.getComponent(r);if(o!==0){const a=Ju.getComponent(r);eh.multiplyMatrices(n.bones[a].matrixWorld,n.boneInverses[a]),t.addScaledVector(Gx.copy(Zu).applyMatrix4(eh),o)}}return t.applyMatrix4(this.bindMatrixInverse)}}class Mf extends At{constructor(){super(),this.isBone=!0,this.type="Bone"}}class Sf extends Wt{constructor(e=null,t=1,n=1,s,r,o,a,c,l=rn,u=rn,f,h){super(null,o,a,c,l,u,s,r,f,h),this.isDataTexture=!0,this.image={data:e,width:t,height:n},this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}const nh=new De,Wx=new De;class Al{constructor(e=[],t=[]){this.uuid=wn(),this.bones=e.slice(0),this.boneInverses=t,this.boneMatrices=null,this.boneTexture=null,this.init()}init(){const e=this.bones,t=this.boneInverses;if(this.boneMatrices=new Float32Array(e.length*16),t.length===0)this.calculateInverses();else if(e.length!==t.length){console.warn("THREE.Skeleton: Number of inverse bone matrices does not match amount of bones."),this.boneInverses=[];for(let n=0,s=this.bones.length;n<s;n++)this.boneInverses.push(new De)}}calculateInverses(){this.boneInverses.length=0;for(let e=0,t=this.bones.length;e<t;e++){const n=new De;this.bones[e]&&n.copy(this.bones[e].matrixWorld).invert(),this.boneInverses.push(n)}}pose(){for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&n.matrixWorld.copy(this.boneInverses[e]).invert()}for(let e=0,t=this.bones.length;e<t;e++){const n=this.bones[e];n&&(n.parent&&n.parent.isBone?(n.matrix.copy(n.parent.matrixWorld).invert(),n.matrix.multiply(n.matrixWorld)):n.matrix.copy(n.matrixWorld),n.matrix.decompose(n.position,n.quaternion,n.scale))}}update(){const e=this.bones,t=this.boneInverses,n=this.boneMatrices,s=this.boneTexture;for(let r=0,o=e.length;r<o;r++){const a=e[r]?e[r].matrixWorld:Wx;nh.multiplyMatrices(a,t[r]),nh.toArray(n,r*16)}s!==null&&(s.needsUpdate=!0)}clone(){return new Al(this.bones,this.boneInverses)}computeBoneTexture(){let e=Math.sqrt(this.bones.length*4);e=Math.ceil(e/4)*4,e=Math.max(e,4);const t=new Float32Array(e*e*4);t.set(this.boneMatrices);const n=new Sf(t,e,e,bn,Dn);return n.needsUpdate=!0,this.boneMatrices=t,this.boneTexture=n,this}getBoneByName(e){for(let t=0,n=this.bones.length;t<n;t++){const s=this.bones[t];if(s.name===e)return s}}dispose(){this.boneTexture!==null&&(this.boneTexture.dispose(),this.boneTexture=null)}fromJSON(e,t){this.uuid=e.uuid;for(let n=0,s=e.bones.length;n<s;n++){const r=e.bones[n];let o=t[r];o===void 0&&(console.warn("THREE.Skeleton: No bone found with UUID:",r),o=new Mf),this.bones.push(o),this.boneInverses.push(new De().fromArray(e.boneInverses[n]))}return this.init(),this}toJSON(){const e={metadata:{version:4.6,type:"Skeleton",generator:"Skeleton.toJSON"},bones:[],boneInverses:[]};e.uuid=this.uuid;const t=this.bones,n=this.boneInverses;for(let s=0,r=t.length;s<r;s++){const o=t[s];e.bones.push(o.uuid);const a=n[s];e.boneInverses.push(a.toArray())}return e}}class el extends Xt{constructor(e,t,n,s=1){super(e,t,n),this.isInstancedBufferAttribute=!0,this.meshPerAttribute=s}copy(e){return super.copy(e),this.meshPerAttribute=e.meshPerAttribute,this}toJSON(){const e=super.toJSON();return e.meshPerAttribute=this.meshPerAttribute,e.isInstancedBufferAttribute=!0,e}}const bs=new De,ih=new De,lo=[],sh=new on,Xx=new De,cr=new Gt,lr=new Gn;class qx extends Gt{constructor(e,t,n){super(e,t),this.isInstancedMesh=!0,this.instanceMatrix=new el(new Float32Array(n*16),16),this.instanceColor=null,this.morphTexture=null,this.count=n,this.boundingBox=null,this.boundingSphere=null;for(let s=0;s<n;s++)this.setMatrixAt(s,Xx)}computeBoundingBox(){const e=this.geometry,t=this.count;this.boundingBox===null&&(this.boundingBox=new on),e.boundingBox===null&&e.computeBoundingBox(),this.boundingBox.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,bs),sh.copy(e.boundingBox).applyMatrix4(bs),this.boundingBox.union(sh)}computeBoundingSphere(){const e=this.geometry,t=this.count;this.boundingSphere===null&&(this.boundingSphere=new Gn),e.boundingSphere===null&&e.computeBoundingSphere(),this.boundingSphere.makeEmpty();for(let n=0;n<t;n++)this.getMatrixAt(n,bs),lr.copy(e.boundingSphere).applyMatrix4(bs),this.boundingSphere.union(lr)}copy(e,t){return super.copy(e,t),this.instanceMatrix.copy(e.instanceMatrix),e.morphTexture!==null&&(this.morphTexture=e.morphTexture.clone()),e.instanceColor!==null&&(this.instanceColor=e.instanceColor.clone()),this.count=e.count,e.boundingBox!==null&&(this.boundingBox=e.boundingBox.clone()),e.boundingSphere!==null&&(this.boundingSphere=e.boundingSphere.clone()),this}getColorAt(e,t){t.fromArray(this.instanceColor.array,e*3)}getMatrixAt(e,t){t.fromArray(this.instanceMatrix.array,e*16)}getMorphAt(e,t){const n=t.morphTargetInfluences,s=this.morphTexture.source.data.data,r=n.length+1,o=e*r+1;for(let a=0;a<n.length;a++)n[a]=s[o+a]}raycast(e,t){const n=this.matrixWorld,s=this.count;if(cr.geometry=this.geometry,cr.material=this.material,cr.material!==void 0&&(this.boundingSphere===null&&this.computeBoundingSphere(),lr.copy(this.boundingSphere),lr.applyMatrix4(n),e.ray.intersectsSphere(lr)!==!1))for(let r=0;r<s;r++){this.getMatrixAt(r,bs),ih.multiplyMatrices(n,bs),cr.matrixWorld=ih,cr.raycast(e,lo);for(let o=0,a=lo.length;o<a;o++){const c=lo[o];c.instanceId=r,c.object=this,t.push(c)}lo.length=0}}setColorAt(e,t){this.instanceColor===null&&(this.instanceColor=new el(new Float32Array(this.instanceMatrix.count*3).fill(1),3)),t.toArray(this.instanceColor.array,e*3)}setMatrixAt(e,t){t.toArray(this.instanceMatrix.array,e*16)}setMorphAt(e,t){const n=t.morphTargetInfluences,s=n.length+1;this.morphTexture===null&&(this.morphTexture=new Sf(new Float32Array(s*this.count),s,this.count,_l,Dn));const r=this.morphTexture.source.data.data;let o=0;for(let l=0;l<n.length;l++)o+=n[l];const a=this.geometry.morphTargetsRelative?1:1-o,c=s*e;r[c]=a,r.set(n,c+1)}updateMorphTargets(){}dispose(){return this.dispatchEvent({type:"dispose"}),this.morphTexture!==null&&(this.morphTexture.dispose(),this.morphTexture=null),this}}class ns extends Hn{static get type(){return"LineBasicMaterial"}constructor(e){super(),this.isLineBasicMaterial=!0,this.color=new Ve(16777215),this.map=null,this.linewidth=1,this.linecap="round",this.linejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.linewidth=e.linewidth,this.linecap=e.linecap,this.linejoin=e.linejoin,this.fog=e.fog,this}}const ko=new b,zo=new b,rh=new De,ur=new Ko,uo=new Gn,Ha=new b,oh=new b;class Rl extends At{constructor(e=new Ft,t=new ns){super(),this.isLine=!0,this.type="Line",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[0];for(let s=1,r=t.count;s<r;s++)ko.fromBufferAttribute(t,s-1),zo.fromBufferAttribute(t,s),n[s]=n[s-1],n[s]+=ko.distanceTo(zo);e.setAttribute("lineDistance",new ft(n,1))}else console.warn("THREE.Line.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Line.threshold,o=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),uo.copy(n.boundingSphere),uo.applyMatrix4(s),uo.radius+=r,e.ray.intersectsSphere(uo)===!1)return;rh.copy(s).invert(),ur.copy(e.ray).applyMatrix4(rh);const a=r/((this.scale.x+this.scale.y+this.scale.z)/3),c=a*a,l=this.isLineSegments?2:1,u=n.index,h=n.attributes.position;if(u!==null){const d=Math.max(0,o.start),m=Math.min(u.count,o.start+o.count);for(let _=d,g=m-1;_<g;_+=l){const p=u.getX(_),M=u.getX(_+1),v=ho(this,e,ur,c,p,M);v&&t.push(v)}if(this.isLineLoop){const _=u.getX(m-1),g=u.getX(d),p=ho(this,e,ur,c,_,g);p&&t.push(p)}}else{const d=Math.max(0,o.start),m=Math.min(h.count,o.start+o.count);for(let _=d,g=m-1;_<g;_+=l){const p=ho(this,e,ur,c,_,_+1);p&&t.push(p)}if(this.isLineLoop){const _=ho(this,e,ur,c,m-1,d);_&&t.push(_)}}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}}function ho(i,e,t,n,s,r){const o=i.geometry.attributes.position;if(ko.fromBufferAttribute(o,s),zo.fromBufferAttribute(o,r),t.distanceSqToSegment(ko,zo,Ha,oh)>n)return;Ha.applyMatrix4(i.matrixWorld);const c=e.ray.origin.distanceTo(Ha);if(!(c<e.near||c>e.far))return{distance:c,point:oh.clone().applyMatrix4(i.matrixWorld),index:s,face:null,faceIndex:null,barycoord:null,object:i}}const ah=new b,ch=new b;class Nr extends Rl{constructor(e,t){super(e,t),this.isLineSegments=!0,this.type="LineSegments"}computeLineDistances(){const e=this.geometry;if(e.index===null){const t=e.attributes.position,n=[];for(let s=0,r=t.count;s<r;s+=2)ah.fromBufferAttribute(t,s),ch.fromBufferAttribute(t,s+1),n[s]=s===0?0:n[s-1],n[s+1]=n[s]+ah.distanceTo(ch);e.setAttribute("lineDistance",new ft(n,1))}else console.warn("THREE.LineSegments.computeLineDistances(): Computation only possible with non-indexed BufferGeometry.");return this}}class Ef extends Rl{constructor(e,t){super(e,t),this.isLineLoop=!0,this.type="LineLoop"}}class bf extends Hn{static get type(){return"PointsMaterial"}constructor(e){super(),this.isPointsMaterial=!0,this.color=new Ve(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const lh=new De,tl=new Ko,fo=new Gn,po=new b;class Yx extends At{constructor(e=new Ft,t=new bf){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,s=this.matrixWorld,r=e.params.Points.threshold,o=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),fo.copy(n.boundingSphere),fo.applyMatrix4(s),fo.radius+=r,e.ray.intersectsSphere(fo)===!1)return;lh.copy(s).invert(),tl.copy(e.ray).applyMatrix4(lh);const a=r/((this.scale.x+this.scale.y+this.scale.z)/3),c=a*a,l=n.index,f=n.attributes.position;if(l!==null){const h=Math.max(0,o.start),d=Math.min(l.count,o.start+o.count);for(let m=h,_=d;m<_;m++){const g=l.getX(m);po.fromBufferAttribute(f,g),uh(po,g,c,s,e,t,this)}}else{const h=Math.max(0,o.start),d=Math.min(f.count,o.start+o.count);for(let m=h,_=d;m<_;m++)po.fromBufferAttribute(f,m),uh(po,m,c,s,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const s=t[n[0]];if(s!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let r=0,o=s.length;r<o;r++){const a=s[r].name||String(r);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=r}}}}}function uh(i,e,t,n,s,r,o){const a=tl.distanceSqToPoint(i);if(a<t){const c=new b;tl.closestPointToPoint(i,c),c.applyMatrix4(n);const l=s.ray.origin.distanceTo(c);if(l<s.near||l>s.far)return;r.push({distance:l,distanceToRay:Math.sqrt(a),point:c,index:e,face:null,faceIndex:null,barycoord:null,object:o})}}class Wn{constructor(){this.type="Curve",this.arcLengthDivisions=200}getPoint(){return console.warn("THREE.Curve: .getPoint() not implemented."),null}getPointAt(e,t){const n=this.getUtoTmapping(e);return this.getPoint(n,t)}getPoints(e=5){const t=[];for(let n=0;n<=e;n++)t.push(this.getPoint(n/e));return t}getSpacedPoints(e=5){const t=[];for(let n=0;n<=e;n++)t.push(this.getPointAt(n/e));return t}getLength(){const e=this.getLengths();return e[e.length-1]}getLengths(e=this.arcLengthDivisions){if(this.cacheArcLengths&&this.cacheArcLengths.length===e+1&&!this.needsUpdate)return this.cacheArcLengths;this.needsUpdate=!1;const t=[];let n,s=this.getPoint(0),r=0;t.push(0);for(let o=1;o<=e;o++)n=this.getPoint(o/e),r+=n.distanceTo(s),t.push(r),s=n;return this.cacheArcLengths=t,t}updateArcLengths(){this.needsUpdate=!0,this.getLengths()}getUtoTmapping(e,t){const n=this.getLengths();let s=0;const r=n.length;let o;t?o=t:o=e*n[r-1];let a=0,c=r-1,l;for(;a<=c;)if(s=Math.floor(a+(c-a)/2),l=n[s]-o,l<0)a=s+1;else if(l>0)c=s-1;else{c=s;break}if(s=c,n[s]===o)return s/(r-1);const u=n[s],h=n[s+1]-u,d=(o-u)/h;return(s+d)/(r-1)}getTangent(e,t){let s=e-1e-4,r=e+1e-4;s<0&&(s=0),r>1&&(r=1);const o=this.getPoint(s),a=this.getPoint(r),c=t||(o.isVector2?new ie:new b);return c.copy(a).sub(o).normalize(),c}getTangentAt(e,t){const n=this.getUtoTmapping(e);return this.getTangent(n,t)}computeFrenetFrames(e,t){const n=new b,s=[],r=[],o=[],a=new b,c=new De;for(let d=0;d<=e;d++){const m=d/e;s[d]=this.getTangentAt(m,new b)}r[0]=new b,o[0]=new b;let l=Number.MAX_VALUE;const u=Math.abs(s[0].x),f=Math.abs(s[0].y),h=Math.abs(s[0].z);u<=l&&(l=u,n.set(1,0,0)),f<=l&&(l=f,n.set(0,1,0)),h<=l&&n.set(0,0,1),a.crossVectors(s[0],n).normalize(),r[0].crossVectors(s[0],a),o[0].crossVectors(s[0],r[0]);for(let d=1;d<=e;d++){if(r[d]=r[d-1].clone(),o[d]=o[d-1].clone(),a.crossVectors(s[d-1],s[d]),a.length()>Number.EPSILON){a.normalize();const m=Math.acos(Bt(s[d-1].dot(s[d]),-1,1));r[d].applyMatrix4(c.makeRotationAxis(a,m))}o[d].crossVectors(s[d],r[d])}if(t===!0){let d=Math.acos(Bt(r[0].dot(r[e]),-1,1));d/=e,s[0].dot(a.crossVectors(r[0],r[e]))>0&&(d=-d);for(let m=1;m<=e;m++)r[m].applyMatrix4(c.makeRotationAxis(s[m],d*m)),o[m].crossVectors(s[m],r[m])}return{tangents:s,normals:r,binormals:o}}clone(){return new this.constructor().copy(this)}copy(e){return this.arcLengthDivisions=e.arcLengthDivisions,this}toJSON(){const e={metadata:{version:4.6,type:"Curve",generator:"Curve.toJSON"}};return e.arcLengthDivisions=this.arcLengthDivisions,e.type=this.type,e}fromJSON(e){return this.arcLengthDivisions=e.arcLengthDivisions,this}}class Cl extends Wn{constructor(e=0,t=0,n=1,s=1,r=0,o=Math.PI*2,a=!1,c=0){super(),this.isEllipseCurve=!0,this.type="EllipseCurve",this.aX=e,this.aY=t,this.xRadius=n,this.yRadius=s,this.aStartAngle=r,this.aEndAngle=o,this.aClockwise=a,this.aRotation=c}getPoint(e,t=new ie){const n=t,s=Math.PI*2;let r=this.aEndAngle-this.aStartAngle;const o=Math.abs(r)<Number.EPSILON;for(;r<0;)r+=s;for(;r>s;)r-=s;r<Number.EPSILON&&(o?r=0:r=s),this.aClockwise===!0&&!o&&(r===s?r=-s:r=r-s);const a=this.aStartAngle+e*r;let c=this.aX+this.xRadius*Math.cos(a),l=this.aY+this.yRadius*Math.sin(a);if(this.aRotation!==0){const u=Math.cos(this.aRotation),f=Math.sin(this.aRotation),h=c-this.aX,d=l-this.aY;c=h*u-d*f+this.aX,l=h*f+d*u+this.aY}return n.set(c,l)}copy(e){return super.copy(e),this.aX=e.aX,this.aY=e.aY,this.xRadius=e.xRadius,this.yRadius=e.yRadius,this.aStartAngle=e.aStartAngle,this.aEndAngle=e.aEndAngle,this.aClockwise=e.aClockwise,this.aRotation=e.aRotation,this}toJSON(){const e=super.toJSON();return e.aX=this.aX,e.aY=this.aY,e.xRadius=this.xRadius,e.yRadius=this.yRadius,e.aStartAngle=this.aStartAngle,e.aEndAngle=this.aEndAngle,e.aClockwise=this.aClockwise,e.aRotation=this.aRotation,e}fromJSON(e){return super.fromJSON(e),this.aX=e.aX,this.aY=e.aY,this.xRadius=e.xRadius,this.yRadius=e.yRadius,this.aStartAngle=e.aStartAngle,this.aEndAngle=e.aEndAngle,this.aClockwise=e.aClockwise,this.aRotation=e.aRotation,this}}class jx extends Cl{constructor(e,t,n,s,r,o){super(e,t,n,n,s,r,o),this.isArcCurve=!0,this.type="ArcCurve"}}function Pl(){let i=0,e=0,t=0,n=0;function s(r,o,a,c){i=r,e=a,t=-3*r+3*o-2*a-c,n=2*r-2*o+a+c}return{initCatmullRom:function(r,o,a,c,l){s(o,a,l*(a-r),l*(c-o))},initNonuniformCatmullRom:function(r,o,a,c,l,u,f){let h=(o-r)/l-(a-r)/(l+u)+(a-o)/u,d=(a-o)/u-(c-o)/(u+f)+(c-a)/f;h*=u,d*=u,s(o,a,h,d)},calc:function(r){const o=r*r,a=o*r;return i+e*r+t*o+n*a}}}const mo=new b,Va=new Pl,Ga=new Pl,Wa=new Pl;class $x extends Wn{constructor(e=[],t=!1,n="centripetal",s=.5){super(),this.isCatmullRomCurve3=!0,this.type="CatmullRomCurve3",this.points=e,this.closed=t,this.curveType=n,this.tension=s}getPoint(e,t=new b){const n=t,s=this.points,r=s.length,o=(r-(this.closed?0:1))*e;let a=Math.floor(o),c=o-a;this.closed?a+=a>0?0:(Math.floor(Math.abs(a)/r)+1)*r:c===0&&a===r-1&&(a=r-2,c=1);let l,u;this.closed||a>0?l=s[(a-1)%r]:(mo.subVectors(s[0],s[1]).add(s[0]),l=mo);const f=s[a%r],h=s[(a+1)%r];if(this.closed||a+2<r?u=s[(a+2)%r]:(mo.subVectors(s[r-1],s[r-2]).add(s[r-1]),u=mo),this.curveType==="centripetal"||this.curveType==="chordal"){const d=this.curveType==="chordal"?.5:.25;let m=Math.pow(l.distanceToSquared(f),d),_=Math.pow(f.distanceToSquared(h),d),g=Math.pow(h.distanceToSquared(u),d);_<1e-4&&(_=1),m<1e-4&&(m=_),g<1e-4&&(g=_),Va.initNonuniformCatmullRom(l.x,f.x,h.x,u.x,m,_,g),Ga.initNonuniformCatmullRom(l.y,f.y,h.y,u.y,m,_,g),Wa.initNonuniformCatmullRom(l.z,f.z,h.z,u.z,m,_,g)}else this.curveType==="catmullrom"&&(Va.initCatmullRom(l.x,f.x,h.x,u.x,this.tension),Ga.initCatmullRom(l.y,f.y,h.y,u.y,this.tension),Wa.initCatmullRom(l.z,f.z,h.z,u.z,this.tension));return n.set(Va.calc(c),Ga.calc(c),Wa.calc(c)),n}copy(e){super.copy(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(s.clone())}return this.closed=e.closed,this.curveType=e.curveType,this.tension=e.tension,this}toJSON(){const e=super.toJSON();e.points=[];for(let t=0,n=this.points.length;t<n;t++){const s=this.points[t];e.points.push(s.toArray())}return e.closed=this.closed,e.curveType=this.curveType,e.tension=this.tension,e}fromJSON(e){super.fromJSON(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(new b().fromArray(s))}return this.closed=e.closed,this.curveType=e.curveType,this.tension=e.tension,this}}function hh(i,e,t,n,s){const r=(n-e)*.5,o=(s-t)*.5,a=i*i,c=i*a;return(2*t-2*n+r+o)*c+(-3*t+3*n-2*r-o)*a+r*i+t}function Kx(i,e){const t=1-i;return t*t*e}function Zx(i,e){return 2*(1-i)*i*e}function Jx(i,e){return i*i*e}function Sr(i,e,t,n){return Kx(i,e)+Zx(i,t)+Jx(i,n)}function Qx(i,e){const t=1-i;return t*t*t*e}function ev(i,e){const t=1-i;return 3*t*t*i*e}function tv(i,e){return 3*(1-i)*i*i*e}function nv(i,e){return i*i*i*e}function Er(i,e,t,n,s){return Qx(i,e)+ev(i,t)+tv(i,n)+nv(i,s)}class wf extends Wn{constructor(e=new ie,t=new ie,n=new ie,s=new ie){super(),this.isCubicBezierCurve=!0,this.type="CubicBezierCurve",this.v0=e,this.v1=t,this.v2=n,this.v3=s}getPoint(e,t=new ie){const n=t,s=this.v0,r=this.v1,o=this.v2,a=this.v3;return n.set(Er(e,s.x,r.x,o.x,a.x),Er(e,s.y,r.y,o.y,a.y)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this.v3.copy(e.v3),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e.v3=this.v3.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this.v3.fromArray(e.v3),this}}class iv extends Wn{constructor(e=new b,t=new b,n=new b,s=new b){super(),this.isCubicBezierCurve3=!0,this.type="CubicBezierCurve3",this.v0=e,this.v1=t,this.v2=n,this.v3=s}getPoint(e,t=new b){const n=t,s=this.v0,r=this.v1,o=this.v2,a=this.v3;return n.set(Er(e,s.x,r.x,o.x,a.x),Er(e,s.y,r.y,o.y,a.y),Er(e,s.z,r.z,o.z,a.z)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this.v3.copy(e.v3),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e.v3=this.v3.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this.v3.fromArray(e.v3),this}}class Tf extends Wn{constructor(e=new ie,t=new ie){super(),this.isLineCurve=!0,this.type="LineCurve",this.v1=e,this.v2=t}getPoint(e,t=new ie){const n=t;return e===1?n.copy(this.v2):(n.copy(this.v2).sub(this.v1),n.multiplyScalar(e).add(this.v1)),n}getPointAt(e,t){return this.getPoint(e,t)}getTangent(e,t=new ie){return t.subVectors(this.v2,this.v1).normalize()}getTangentAt(e,t){return this.getTangent(e,t)}copy(e){return super.copy(e),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class sv extends Wn{constructor(e=new b,t=new b){super(),this.isLineCurve3=!0,this.type="LineCurve3",this.v1=e,this.v2=t}getPoint(e,t=new b){const n=t;return e===1?n.copy(this.v2):(n.copy(this.v2).sub(this.v1),n.multiplyScalar(e).add(this.v1)),n}getPointAt(e,t){return this.getPoint(e,t)}getTangent(e,t=new b){return t.subVectors(this.v2,this.v1).normalize()}getTangentAt(e,t){return this.getTangent(e,t)}copy(e){return super.copy(e),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class Af extends Wn{constructor(e=new ie,t=new ie,n=new ie){super(),this.isQuadraticBezierCurve=!0,this.type="QuadraticBezierCurve",this.v0=e,this.v1=t,this.v2=n}getPoint(e,t=new ie){const n=t,s=this.v0,r=this.v1,o=this.v2;return n.set(Sr(e,s.x,r.x,o.x),Sr(e,s.y,r.y,o.y)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class rv extends Wn{constructor(e=new b,t=new b,n=new b){super(),this.isQuadraticBezierCurve3=!0,this.type="QuadraticBezierCurve3",this.v0=e,this.v1=t,this.v2=n}getPoint(e,t=new b){const n=t,s=this.v0,r=this.v1,o=this.v2;return n.set(Sr(e,s.x,r.x,o.x),Sr(e,s.y,r.y,o.y),Sr(e,s.z,r.z,o.z)),n}copy(e){return super.copy(e),this.v0.copy(e.v0),this.v1.copy(e.v1),this.v2.copy(e.v2),this}toJSON(){const e=super.toJSON();return e.v0=this.v0.toArray(),e.v1=this.v1.toArray(),e.v2=this.v2.toArray(),e}fromJSON(e){return super.fromJSON(e),this.v0.fromArray(e.v0),this.v1.fromArray(e.v1),this.v2.fromArray(e.v2),this}}class Rf extends Wn{constructor(e=[]){super(),this.isSplineCurve=!0,this.type="SplineCurve",this.points=e}getPoint(e,t=new ie){const n=t,s=this.points,r=(s.length-1)*e,o=Math.floor(r),a=r-o,c=s[o===0?o:o-1],l=s[o],u=s[o>s.length-2?s.length-1:o+1],f=s[o>s.length-3?s.length-1:o+2];return n.set(hh(a,c.x,l.x,u.x,f.x),hh(a,c.y,l.y,u.y,f.y)),n}copy(e){super.copy(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(s.clone())}return this}toJSON(){const e=super.toJSON();e.points=[];for(let t=0,n=this.points.length;t<n;t++){const s=this.points[t];e.points.push(s.toArray())}return e}fromJSON(e){super.fromJSON(e),this.points=[];for(let t=0,n=e.points.length;t<n;t++){const s=e.points[t];this.points.push(new ie().fromArray(s))}return this}}var nl=Object.freeze({__proto__:null,ArcCurve:jx,CatmullRomCurve3:$x,CubicBezierCurve:wf,CubicBezierCurve3:iv,EllipseCurve:Cl,LineCurve:Tf,LineCurve3:sv,QuadraticBezierCurve:Af,QuadraticBezierCurve3:rv,SplineCurve:Rf});class ov extends Wn{constructor(){super(),this.type="CurvePath",this.curves=[],this.autoClose=!1}add(e){this.curves.push(e)}closePath(){const e=this.curves[0].getPoint(0),t=this.curves[this.curves.length-1].getPoint(1);if(!e.equals(t)){const n=e.isVector2===!0?"LineCurve":"LineCurve3";this.curves.push(new nl[n](t,e))}return this}getPoint(e,t){const n=e*this.getLength(),s=this.getCurveLengths();let r=0;for(;r<s.length;){if(s[r]>=n){const o=s[r]-n,a=this.curves[r],c=a.getLength(),l=c===0?0:1-o/c;return a.getPointAt(l,t)}r++}return null}getLength(){const e=this.getCurveLengths();return e[e.length-1]}updateArcLengths(){this.needsUpdate=!0,this.cacheLengths=null,this.getCurveLengths()}getCurveLengths(){if(this.cacheLengths&&this.cacheLengths.length===this.curves.length)return this.cacheLengths;const e=[];let t=0;for(let n=0,s=this.curves.length;n<s;n++)t+=this.curves[n].getLength(),e.push(t);return this.cacheLengths=e,e}getSpacedPoints(e=40){const t=[];for(let n=0;n<=e;n++)t.push(this.getPoint(n/e));return this.autoClose&&t.push(t[0]),t}getPoints(e=12){const t=[];let n;for(let s=0,r=this.curves;s<r.length;s++){const o=r[s],a=o.isEllipseCurve?e*2:o.isLineCurve||o.isLineCurve3?1:o.isSplineCurve?e*o.points.length:e,c=o.getPoints(a);for(let l=0;l<c.length;l++){const u=c[l];n&&n.equals(u)||(t.push(u),n=u)}}return this.autoClose&&t.length>1&&!t[t.length-1].equals(t[0])&&t.push(t[0]),t}copy(e){super.copy(e),this.curves=[];for(let t=0,n=e.curves.length;t<n;t++){const s=e.curves[t];this.curves.push(s.clone())}return this.autoClose=e.autoClose,this}toJSON(){const e=super.toJSON();e.autoClose=this.autoClose,e.curves=[];for(let t=0,n=this.curves.length;t<n;t++){const s=this.curves[t];e.curves.push(s.toJSON())}return e}fromJSON(e){super.fromJSON(e),this.autoClose=e.autoClose,this.curves=[];for(let t=0,n=e.curves.length;t<n;t++){const s=e.curves[t];this.curves.push(new nl[s.type]().fromJSON(s))}return this}}class il extends ov{constructor(e){super(),this.type="Path",this.currentPoint=new ie,e&&this.setFromPoints(e)}setFromPoints(e){this.moveTo(e[0].x,e[0].y);for(let t=1,n=e.length;t<n;t++)this.lineTo(e[t].x,e[t].y);return this}moveTo(e,t){return this.currentPoint.set(e,t),this}lineTo(e,t){const n=new Tf(this.currentPoint.clone(),new ie(e,t));return this.curves.push(n),this.currentPoint.set(e,t),this}quadraticCurveTo(e,t,n,s){const r=new Af(this.currentPoint.clone(),new ie(e,t),new ie(n,s));return this.curves.push(r),this.currentPoint.set(n,s),this}bezierCurveTo(e,t,n,s,r,o){const a=new wf(this.currentPoint.clone(),new ie(e,t),new ie(n,s),new ie(r,o));return this.curves.push(a),this.currentPoint.set(r,o),this}splineThru(e){const t=[this.currentPoint.clone()].concat(e),n=new Rf(t);return this.curves.push(n),this.currentPoint.copy(e[e.length-1]),this}arc(e,t,n,s,r,o){const a=this.currentPoint.x,c=this.currentPoint.y;return this.absarc(e+a,t+c,n,s,r,o),this}absarc(e,t,n,s,r,o){return this.absellipse(e,t,n,n,s,r,o),this}ellipse(e,t,n,s,r,o,a,c){const l=this.currentPoint.x,u=this.currentPoint.y;return this.absellipse(e+l,t+u,n,s,r,o,a,c),this}absellipse(e,t,n,s,r,o,a,c){const l=new Cl(e,t,n,s,r,o,a,c);if(this.curves.length>0){const f=l.getPoint(0);f.equals(this.currentPoint)||this.lineTo(f.x,f.y)}this.curves.push(l);const u=l.getPoint(1);return this.currentPoint.copy(u),this}copy(e){return super.copy(e),this.currentPoint.copy(e.currentPoint),this}toJSON(){const e=super.toJSON();return e.currentPoint=this.currentPoint.toArray(),e}fromJSON(e){return super.fromJSON(e),this.currentPoint.fromArray(e.currentPoint),this}}class Qo extends Ft{constructor(e=[new ie(0,-.5),new ie(.5,0),new ie(0,.5)],t=12,n=0,s=Math.PI*2){super(),this.type="LatheGeometry",this.parameters={points:e,segments:t,phiStart:n,phiLength:s},t=Math.floor(t),s=Bt(s,0,Math.PI*2);const r=[],o=[],a=[],c=[],l=[],u=1/t,f=new b,h=new ie,d=new b,m=new b,_=new b;let g=0,p=0;for(let M=0;M<=e.length-1;M++)switch(M){case 0:g=e[M+1].x-e[M].x,p=e[M+1].y-e[M].y,d.x=p*1,d.y=-g,d.z=p*0,_.copy(d),d.normalize(),c.push(d.x,d.y,d.z);break;case e.length-1:c.push(_.x,_.y,_.z);break;default:g=e[M+1].x-e[M].x,p=e[M+1].y-e[M].y,d.x=p*1,d.y=-g,d.z=p*0,m.copy(d),d.x+=_.x,d.y+=_.y,d.z+=_.z,d.normalize(),c.push(d.x,d.y,d.z),_.copy(m)}for(let M=0;M<=t;M++){const v=n+M*u*s,x=Math.sin(v),L=Math.cos(v);for(let T=0;T<=e.length-1;T++){f.x=e[T].x*x,f.y=e[T].y,f.z=e[T].x*L,o.push(f.x,f.y,f.z),h.x=M/t,h.y=T/(e.length-1),a.push(h.x,h.y);const R=c[3*T+0]*x,I=c[3*T+1],w=c[3*T+0]*L;l.push(R,I,w)}}for(let M=0;M<t;M++)for(let v=0;v<e.length-1;v++){const x=v+M*e.length,L=x,T=x+e.length,R=x+e.length+1,I=x+1;r.push(L,T,I),r.push(R,I,T)}this.setIndex(r),this.setAttribute("position",new ft(o,3)),this.setAttribute("uv",new ft(a,2)),this.setAttribute("normal",new ft(l,3))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Qo(e.points,e.segments,e.phiStart,e.phiLength)}}class Ll extends Qo{constructor(e=1,t=1,n=4,s=8){const r=new il;r.absarc(0,-t/2,e,Math.PI*1.5,0),r.absarc(0,t/2,e,0,Math.PI*.5),super(r.getPoints(n),s),this.type="CapsuleGeometry",this.parameters={radius:e,length:t,capSegments:n,radialSegments:s}}static fromJSON(e){return new Ll(e.radius,e.length,e.capSegments,e.radialSegments)}}class is extends Ft{constructor(e=1,t=32,n=0,s=Math.PI*2){super(),this.type="CircleGeometry",this.parameters={radius:e,segments:t,thetaStart:n,thetaLength:s},t=Math.max(3,t);const r=[],o=[],a=[],c=[],l=new b,u=new ie;o.push(0,0,0),a.push(0,0,1),c.push(.5,.5);for(let f=0,h=3;f<=t;f++,h+=3){const d=n+f/t*s;l.x=e*Math.cos(d),l.y=e*Math.sin(d),o.push(l.x,l.y,l.z),a.push(0,0,1),u.x=(o[h]/e+1)/2,u.y=(o[h+1]/e+1)/2,c.push(u.x,u.y)}for(let f=1;f<=t;f++)r.push(f,f+1,0);this.setIndex(r),this.setAttribute("position",new ft(o,3)),this.setAttribute("normal",new ft(a,3)),this.setAttribute("uv",new ft(c,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new is(e.radius,e.segments,e.thetaStart,e.thetaLength)}}class Dt extends Ft{constructor(e=1,t=1,n=1,s=32,r=1,o=!1,a=0,c=Math.PI*2){super(),this.type="CylinderGeometry",this.parameters={radiusTop:e,radiusBottom:t,height:n,radialSegments:s,heightSegments:r,openEnded:o,thetaStart:a,thetaLength:c};const l=this;s=Math.floor(s),r=Math.floor(r);const u=[],f=[],h=[],d=[];let m=0;const _=[],g=n/2;let p=0;M(),o===!1&&(e>0&&v(!0),t>0&&v(!1)),this.setIndex(u),this.setAttribute("position",new ft(f,3)),this.setAttribute("normal",new ft(h,3)),this.setAttribute("uv",new ft(d,2));function M(){const x=new b,L=new b;let T=0;const R=(t-e)/n;for(let I=0;I<=r;I++){const w=[],S=I/r,P=S*(t-e)+e;for(let G=0;G<=s;G++){const B=G/s,V=B*c+a,j=Math.sin(V),W=Math.cos(V);L.x=P*j,L.y=-S*n+g,L.z=P*W,f.push(L.x,L.y,L.z),x.set(j,R,W).normalize(),h.push(x.x,x.y,x.z),d.push(B,1-S),w.push(m++)}_.push(w)}for(let I=0;I<s;I++)for(let w=0;w<r;w++){const S=_[w][I],P=_[w+1][I],G=_[w+1][I+1],B=_[w][I+1];(e>0||w!==0)&&(u.push(S,P,B),T+=3),(t>0||w!==r-1)&&(u.push(P,G,B),T+=3)}l.addGroup(p,T,0),p+=T}function v(x){const L=m,T=new ie,R=new b;let I=0;const w=x===!0?e:t,S=x===!0?1:-1;for(let G=1;G<=s;G++)f.push(0,g*S,0),h.push(0,S,0),d.push(.5,.5),m++;const P=m;for(let G=0;G<=s;G++){const V=G/s*c+a,j=Math.cos(V),W=Math.sin(V);R.x=w*W,R.y=g*S,R.z=w*j,f.push(R.x,R.y,R.z),h.push(0,S,0),T.x=j*.5+.5,T.y=W*.5*S+.5,d.push(T.x,T.y),m++}for(let G=0;G<s;G++){const B=L+G,V=P+G;x===!0?u.push(V,V+1,B):u.push(V+1,V,B),I+=3}l.addGroup(p,I,x===!0?1:2),p+=I}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Dt(e.radiusTop,e.radiusBottom,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}class si extends Dt{constructor(e=1,t=1,n=32,s=1,r=!1,o=0,a=Math.PI*2){super(0,e,t,n,s,r,o,a),this.type="ConeGeometry",this.parameters={radius:e,height:t,radialSegments:n,heightSegments:s,openEnded:r,thetaStart:o,thetaLength:a}}static fromJSON(e){return new si(e.radius,e.height,e.radialSegments,e.heightSegments,e.openEnded,e.thetaStart,e.thetaLength)}}const go=new b,_o=new b,Xa=new b,xo=new En;class ea extends Ft{constructor(e=null,t=1){if(super(),this.type="EdgesGeometry",this.parameters={geometry:e,thresholdAngle:t},e!==null){const s=Math.pow(10,4),r=Math.cos(Ds*t),o=e.getIndex(),a=e.getAttribute("position"),c=o?o.count:a.count,l=[0,0,0],u=["a","b","c"],f=new Array(3),h={},d=[];for(let m=0;m<c;m+=3){o?(l[0]=o.getX(m),l[1]=o.getX(m+1),l[2]=o.getX(m+2)):(l[0]=m,l[1]=m+1,l[2]=m+2);const{a:_,b:g,c:p}=xo;if(_.fromBufferAttribute(a,l[0]),g.fromBufferAttribute(a,l[1]),p.fromBufferAttribute(a,l[2]),xo.getNormal(Xa),f[0]=`${Math.round(_.x*s)},${Math.round(_.y*s)},${Math.round(_.z*s)}`,f[1]=`${Math.round(g.x*s)},${Math.round(g.y*s)},${Math.round(g.z*s)}`,f[2]=`${Math.round(p.x*s)},${Math.round(p.y*s)},${Math.round(p.z*s)}`,!(f[0]===f[1]||f[1]===f[2]||f[2]===f[0]))for(let M=0;M<3;M++){const v=(M+1)%3,x=f[M],L=f[v],T=xo[u[M]],R=xo[u[v]],I=`${x}_${L}`,w=`${L}_${x}`;w in h&&h[w]?(Xa.dot(h[w].normal)<=r&&(d.push(T.x,T.y,T.z),d.push(R.x,R.y,R.z)),h[w]=null):I in h||(h[I]={index0:l[M],index1:l[v],normal:Xa.clone()})}}for(const m in h)if(h[m]){const{index0:_,index1:g}=h[m];go.fromBufferAttribute(a,_),_o.fromBufferAttribute(a,g),d.push(go.x,go.y,go.z),d.push(_o.x,_o.y,_o.z)}this.setAttribute("position",new ft(d,3))}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}}class di extends il{constructor(e){super(e),this.uuid=wn(),this.type="Shape",this.holes=[]}getPointsHoles(e){const t=[];for(let n=0,s=this.holes.length;n<s;n++)t[n]=this.holes[n].getPoints(e);return t}extractPoints(e){return{shape:this.getPoints(e),holes:this.getPointsHoles(e)}}copy(e){super.copy(e),this.holes=[];for(let t=0,n=e.holes.length;t<n;t++){const s=e.holes[t];this.holes.push(s.clone())}return this}toJSON(){const e=super.toJSON();e.uuid=this.uuid,e.holes=[];for(let t=0,n=this.holes.length;t<n;t++){const s=this.holes[t];e.holes.push(s.toJSON())}return e}fromJSON(e){super.fromJSON(e),this.uuid=e.uuid,this.holes=[];for(let t=0,n=e.holes.length;t<n;t++){const s=e.holes[t];this.holes.push(new il().fromJSON(s))}return this}}const av={triangulate:function(i,e,t=2){const n=e&&e.length,s=n?e[0]*t:i.length;let r=Cf(i,0,s,t,!0);const o=[];if(!r||r.next===r.prev)return o;let a,c,l,u,f,h,d;if(n&&(r=fv(i,e,r,t)),i.length>80*t){a=l=i[0],c=u=i[1];for(let m=t;m<s;m+=t)f=i[m],h=i[m+1],f<a&&(a=f),h<c&&(c=h),f>l&&(l=f),h>u&&(u=h);d=Math.max(l-a,u-c),d=d!==0?32767/d:0}return Pr(r,o,t,a,c,d,0),o}};function Cf(i,e,t,n,s){let r,o;if(s===Ev(i,e,t,n)>0)for(r=e;r<t;r+=n)o=fh(r,i[r],i[r+1],o);else for(r=t-n;r>=e;r-=n)o=fh(r,i[r],i[r+1],o);return o&&ta(o,o.next)&&(Ir(o),o=o.next),o}function ss(i,e){if(!i)return i;e||(e=i);let t=i,n;do if(n=!1,!t.steiner&&(ta(t,t.next)||Pt(t.prev,t,t.next)===0)){if(Ir(t),t=e=t.prev,t===t.next)break;n=!0}else t=t.next;while(n||t!==e);return e}function Pr(i,e,t,n,s,r,o){if(!i)return;!o&&r&&_v(i,n,s,r);let a=i,c,l;for(;i.prev!==i.next;){if(c=i.prev,l=i.next,r?lv(i,n,s,r):cv(i)){e.push(c.i/t|0),e.push(i.i/t|0),e.push(l.i/t|0),Ir(i),i=l.next,a=l.next;continue}if(i=l,i===a){o?o===1?(i=uv(ss(i),e,t),Pr(i,e,t,n,s,r,2)):o===2&&hv(i,e,t,n,s,r):Pr(ss(i),e,t,n,s,r,1);break}}}function cv(i){const e=i.prev,t=i,n=i.next;if(Pt(e,t,n)>=0)return!1;const s=e.x,r=t.x,o=n.x,a=e.y,c=t.y,l=n.y,u=s<r?s<o?s:o:r<o?r:o,f=a<c?a<l?a:l:c<l?c:l,h=s>r?s>o?s:o:r>o?r:o,d=a>c?a>l?a:l:c>l?c:l;let m=n.next;for(;m!==e;){if(m.x>=u&&m.x<=h&&m.y>=f&&m.y<=d&&Cs(s,a,r,c,o,l,m.x,m.y)&&Pt(m.prev,m,m.next)>=0)return!1;m=m.next}return!0}function lv(i,e,t,n){const s=i.prev,r=i,o=i.next;if(Pt(s,r,o)>=0)return!1;const a=s.x,c=r.x,l=o.x,u=s.y,f=r.y,h=o.y,d=a<c?a<l?a:l:c<l?c:l,m=u<f?u<h?u:h:f<h?f:h,_=a>c?a>l?a:l:c>l?c:l,g=u>f?u>h?u:h:f>h?f:h,p=sl(d,m,e,t,n),M=sl(_,g,e,t,n);let v=i.prevZ,x=i.nextZ;for(;v&&v.z>=p&&x&&x.z<=M;){if(v.x>=d&&v.x<=_&&v.y>=m&&v.y<=g&&v!==s&&v!==o&&Cs(a,u,c,f,l,h,v.x,v.y)&&Pt(v.prev,v,v.next)>=0||(v=v.prevZ,x.x>=d&&x.x<=_&&x.y>=m&&x.y<=g&&x!==s&&x!==o&&Cs(a,u,c,f,l,h,x.x,x.y)&&Pt(x.prev,x,x.next)>=0))return!1;x=x.nextZ}for(;v&&v.z>=p;){if(v.x>=d&&v.x<=_&&v.y>=m&&v.y<=g&&v!==s&&v!==o&&Cs(a,u,c,f,l,h,v.x,v.y)&&Pt(v.prev,v,v.next)>=0)return!1;v=v.prevZ}for(;x&&x.z<=M;){if(x.x>=d&&x.x<=_&&x.y>=m&&x.y<=g&&x!==s&&x!==o&&Cs(a,u,c,f,l,h,x.x,x.y)&&Pt(x.prev,x,x.next)>=0)return!1;x=x.nextZ}return!0}function uv(i,e,t){let n=i;do{const s=n.prev,r=n.next.next;!ta(s,r)&&Pf(s,n,n.next,r)&&Lr(s,r)&&Lr(r,s)&&(e.push(s.i/t|0),e.push(n.i/t|0),e.push(r.i/t|0),Ir(n),Ir(n.next),n=i=r),n=n.next}while(n!==i);return ss(n)}function hv(i,e,t,n,s,r){let o=i;do{let a=o.next.next;for(;a!==o.prev;){if(o.i!==a.i&&yv(o,a)){let c=Lf(o,a);o=ss(o,o.next),c=ss(c,c.next),Pr(o,e,t,n,s,r,0),Pr(c,e,t,n,s,r,0);return}a=a.next}o=o.next}while(o!==i)}function fv(i,e,t,n){const s=[];let r,o,a,c,l;for(r=0,o=e.length;r<o;r++)a=e[r]*n,c=r<o-1?e[r+1]*n:i.length,l=Cf(i,a,c,n,!1),l===l.next&&(l.steiner=!0),s.push(vv(l));for(s.sort(dv),r=0;r<s.length;r++)t=pv(s[r],t);return t}function dv(i,e){return i.x-e.x}function pv(i,e){const t=mv(i,e);if(!t)return e;const n=Lf(t,i);return ss(n,n.next),ss(t,t.next)}function mv(i,e){let t=e,n=-1/0,s;const r=i.x,o=i.y;do{if(o<=t.y&&o>=t.next.y&&t.next.y!==t.y){const h=t.x+(o-t.y)*(t.next.x-t.x)/(t.next.y-t.y);if(h<=r&&h>n&&(n=h,s=t.x<t.next.x?t:t.next,h===r))return s}t=t.next}while(t!==e);if(!s)return null;const a=s,c=s.x,l=s.y;let u=1/0,f;t=s;do r>=t.x&&t.x>=c&&r!==t.x&&Cs(o<l?r:n,o,c,l,o<l?n:r,o,t.x,t.y)&&(f=Math.abs(o-t.y)/(r-t.x),Lr(t,i)&&(f<u||f===u&&(t.x>s.x||t.x===s.x&&gv(s,t)))&&(s=t,u=f)),t=t.next;while(t!==a);return s}function gv(i,e){return Pt(i.prev,i,e.prev)<0&&Pt(e.next,i,i.next)<0}function _v(i,e,t,n){let s=i;do s.z===0&&(s.z=sl(s.x,s.y,e,t,n)),s.prevZ=s.prev,s.nextZ=s.next,s=s.next;while(s!==i);s.prevZ.nextZ=null,s.prevZ=null,xv(s)}function xv(i){let e,t,n,s,r,o,a,c,l=1;do{for(t=i,i=null,r=null,o=0;t;){for(o++,n=t,a=0,e=0;e<l&&(a++,n=n.nextZ,!!n);e++);for(c=l;a>0||c>0&&n;)a!==0&&(c===0||!n||t.z<=n.z)?(s=t,t=t.nextZ,a--):(s=n,n=n.nextZ,c--),r?r.nextZ=s:i=s,s.prevZ=r,r=s;t=n}r.nextZ=null,l*=2}while(o>1);return i}function sl(i,e,t,n,s){return i=(i-t)*s|0,e=(e-n)*s|0,i=(i|i<<8)&16711935,i=(i|i<<4)&252645135,i=(i|i<<2)&858993459,i=(i|i<<1)&1431655765,e=(e|e<<8)&16711935,e=(e|e<<4)&252645135,e=(e|e<<2)&858993459,e=(e|e<<1)&1431655765,i|e<<1}function vv(i){let e=i,t=i;do(e.x<t.x||e.x===t.x&&e.y<t.y)&&(t=e),e=e.next;while(e!==i);return t}function Cs(i,e,t,n,s,r,o,a){return(s-o)*(e-a)>=(i-o)*(r-a)&&(i-o)*(n-a)>=(t-o)*(e-a)&&(t-o)*(r-a)>=(s-o)*(n-a)}function yv(i,e){return i.next.i!==e.i&&i.prev.i!==e.i&&!Mv(i,e)&&(Lr(i,e)&&Lr(e,i)&&Sv(i,e)&&(Pt(i.prev,i,e.prev)||Pt(i,e.prev,e))||ta(i,e)&&Pt(i.prev,i,i.next)>0&&Pt(e.prev,e,e.next)>0)}function Pt(i,e,t){return(e.y-i.y)*(t.x-e.x)-(e.x-i.x)*(t.y-e.y)}function ta(i,e){return i.x===e.x&&i.y===e.y}function Pf(i,e,t,n){const s=yo(Pt(i,e,t)),r=yo(Pt(i,e,n)),o=yo(Pt(t,n,i)),a=yo(Pt(t,n,e));return!!(s!==r&&o!==a||s===0&&vo(i,t,e)||r===0&&vo(i,n,e)||o===0&&vo(t,i,n)||a===0&&vo(t,e,n))}function vo(i,e,t){return e.x<=Math.max(i.x,t.x)&&e.x>=Math.min(i.x,t.x)&&e.y<=Math.max(i.y,t.y)&&e.y>=Math.min(i.y,t.y)}function yo(i){return i>0?1:i<0?-1:0}function Mv(i,e){let t=i;do{if(t.i!==i.i&&t.next.i!==i.i&&t.i!==e.i&&t.next.i!==e.i&&Pf(t,t.next,i,e))return!0;t=t.next}while(t!==i);return!1}function Lr(i,e){return Pt(i.prev,i,i.next)<0?Pt(i,e,i.next)>=0&&Pt(i,i.prev,e)>=0:Pt(i,e,i.prev)<0||Pt(i,i.next,e)<0}function Sv(i,e){let t=i,n=!1;const s=(i.x+e.x)/2,r=(i.y+e.y)/2;do t.y>r!=t.next.y>r&&t.next.y!==t.y&&s<(t.next.x-t.x)*(r-t.y)/(t.next.y-t.y)+t.x&&(n=!n),t=t.next;while(t!==i);return n}function Lf(i,e){const t=new rl(i.i,i.x,i.y),n=new rl(e.i,e.x,e.y),s=i.next,r=e.prev;return i.next=e,e.prev=i,t.next=s,s.prev=t,n.next=t,t.prev=n,r.next=n,n.prev=r,n}function fh(i,e,t,n){const s=new rl(i,e,t);return n?(s.next=n.next,s.prev=n,n.next.prev=s,n.next=s):(s.prev=s,s.next=s),s}function Ir(i){i.next.prev=i.prev,i.prev.next=i.next,i.prevZ&&(i.prevZ.nextZ=i.nextZ),i.nextZ&&(i.nextZ.prevZ=i.prevZ)}function rl(i,e,t){this.i=i,this.x=e,this.y=t,this.prev=null,this.next=null,this.z=0,this.prevZ=null,this.nextZ=null,this.steiner=!1}function Ev(i,e,t,n){let s=0;for(let r=e,o=t-n;r<t;r+=n)s+=(i[o]-i[r])*(i[r+1]+i[o+1]),o=r;return s}class Ni{static area(e){const t=e.length;let n=0;for(let s=t-1,r=0;r<t;s=r++)n+=e[s].x*e[r].y-e[r].x*e[s].y;return n*.5}static isClockWise(e){return Ni.area(e)<0}static triangulateShape(e,t){const n=[],s=[],r=[];dh(e),ph(n,e);let o=e.length;t.forEach(dh);for(let c=0;c<t.length;c++)s.push(o),o+=t[c].length,ph(n,t[c]);const a=av.triangulate(n,s);for(let c=0;c<a.length;c+=3)r.push(a.slice(c,c+3));return r}}function dh(i){const e=i.length;e>2&&i[e-1].equals(i[0])&&i.pop()}function ph(i,e){for(let t=0;t<e.length;t++)i.push(e[t].x),i.push(e[t].y)}class na extends Ft{constructor(e=new di([new ie(.5,.5),new ie(-.5,.5),new ie(-.5,-.5),new ie(.5,-.5)]),t={}){super(),this.type="ExtrudeGeometry",this.parameters={shapes:e,options:t},e=Array.isArray(e)?e:[e];const n=this,s=[],r=[];for(let a=0,c=e.length;a<c;a++){const l=e[a];o(l)}this.setAttribute("position",new ft(s,3)),this.setAttribute("uv",new ft(r,2)),this.computeVertexNormals();function o(a){const c=[],l=t.curveSegments!==void 0?t.curveSegments:12,u=t.steps!==void 0?t.steps:1,f=t.depth!==void 0?t.depth:1;let h=t.bevelEnabled!==void 0?t.bevelEnabled:!0,d=t.bevelThickness!==void 0?t.bevelThickness:.2,m=t.bevelSize!==void 0?t.bevelSize:d-.1,_=t.bevelOffset!==void 0?t.bevelOffset:0,g=t.bevelSegments!==void 0?t.bevelSegments:3;const p=t.extrudePath,M=t.UVGenerator!==void 0?t.UVGenerator:bv;let v,x=!1,L,T,R,I;p&&(v=p.getSpacedPoints(u),x=!0,h=!1,L=p.computeFrenetFrames(u,!1),T=new b,R=new b,I=new b),h||(g=0,d=0,m=0,_=0);const w=a.extractPoints(l);let S=w.shape;const P=w.holes;if(!Ni.isClockWise(S)){S=S.reverse();for(let J=0,oe=P.length;J<oe;J++){const C=P[J];Ni.isClockWise(C)&&(P[J]=C.reverse())}}const B=Ni.triangulateShape(S,P),V=S;for(let J=0,oe=P.length;J<oe;J++){const C=P[J];S=S.concat(C)}function j(J,oe,C){return oe||console.error("THREE.ExtrudeGeometry: vec does not exist"),J.clone().addScaledVector(oe,C)}const W=S.length,ee=B.length;function O(J,oe,C){let Fe,ne,we;const de=J.x-oe.x,We=J.y-oe.y,Ee=C.x-J.x,A=C.y-J.y,y=de*de+We*We,F=de*A-We*Ee;if(Math.abs(F)>Number.EPSILON){const q=Math.sqrt(y),Q=Math.sqrt(Ee*Ee+A*A),Y=oe.x-We/q,Ie=oe.y+de/q,ge=C.x-A/Q,be=C.y+Ee/Q,rt=((ge-Y)*A-(be-Ie)*Ee)/(de*A-We*Ee);Fe=Y+de*rt-J.x,ne=Ie+We*rt-J.y;const se=Fe*Fe+ne*ne;if(se<=2)return new ie(Fe,ne);we=Math.sqrt(se/2)}else{let q=!1;de>Number.EPSILON?Ee>Number.EPSILON&&(q=!0):de<-Number.EPSILON?Ee<-Number.EPSILON&&(q=!0):Math.sign(We)===Math.sign(A)&&(q=!0),q?(Fe=-We,ne=de,we=Math.sqrt(y)):(Fe=de,ne=We,we=Math.sqrt(y/2))}return new ie(Fe/we,ne/we)}const re=[];for(let J=0,oe=V.length,C=oe-1,Fe=J+1;J<oe;J++,C++,Fe++)C===oe&&(C=0),Fe===oe&&(Fe=0),re[J]=O(V[J],V[C],V[Fe]);const ue=[];let Me,Ye=re.concat();for(let J=0,oe=P.length;J<oe;J++){const C=P[J];Me=[];for(let Fe=0,ne=C.length,we=ne-1,de=Fe+1;Fe<ne;Fe++,we++,de++)we===ne&&(we=0),de===ne&&(de=0),Me[Fe]=O(C[Fe],C[we],C[de]);ue.push(Me),Ye=Ye.concat(Me)}for(let J=0;J<g;J++){const oe=J/g,C=d*Math.cos(oe*Math.PI/2),Fe=m*Math.sin(oe*Math.PI/2)+_;for(let ne=0,we=V.length;ne<we;ne++){const de=j(V[ne],re[ne],Fe);fe(de.x,de.y,-C)}for(let ne=0,we=P.length;ne<we;ne++){const de=P[ne];Me=ue[ne];for(let We=0,Ee=de.length;We<Ee;We++){const A=j(de[We],Me[We],Fe);fe(A.x,A.y,-C)}}}const dt=m+_;for(let J=0;J<W;J++){const oe=h?j(S[J],Ye[J],dt):S[J];x?(R.copy(L.normals[0]).multiplyScalar(oe.x),T.copy(L.binormals[0]).multiplyScalar(oe.y),I.copy(v[0]).add(R).add(T),fe(I.x,I.y,I.z)):fe(oe.x,oe.y,0)}for(let J=1;J<=u;J++)for(let oe=0;oe<W;oe++){const C=h?j(S[oe],Ye[oe],dt):S[oe];x?(R.copy(L.normals[J]).multiplyScalar(C.x),T.copy(L.binormals[J]).multiplyScalar(C.y),I.copy(v[J]).add(R).add(T),fe(I.x,I.y,I.z)):fe(C.x,C.y,f/u*J)}for(let J=g-1;J>=0;J--){const oe=J/g,C=d*Math.cos(oe*Math.PI/2),Fe=m*Math.sin(oe*Math.PI/2)+_;for(let ne=0,we=V.length;ne<we;ne++){const de=j(V[ne],re[ne],Fe);fe(de.x,de.y,f+C)}for(let ne=0,we=P.length;ne<we;ne++){const de=P[ne];Me=ue[ne];for(let We=0,Ee=de.length;We<Ee;We++){const A=j(de[We],Me[We],Fe);x?fe(A.x,A.y+v[u-1].y,v[u-1].x+C):fe(A.x,A.y,f+C)}}}$(),ce();function $(){const J=s.length/3;if(h){let oe=0,C=W*oe;for(let Fe=0;Fe<ee;Fe++){const ne=B[Fe];ze(ne[2]+C,ne[1]+C,ne[0]+C)}oe=u+g*2,C=W*oe;for(let Fe=0;Fe<ee;Fe++){const ne=B[Fe];ze(ne[0]+C,ne[1]+C,ne[2]+C)}}else{for(let oe=0;oe<ee;oe++){const C=B[oe];ze(C[2],C[1],C[0])}for(let oe=0;oe<ee;oe++){const C=B[oe];ze(C[0]+W*u,C[1]+W*u,C[2]+W*u)}}n.addGroup(J,s.length/3-J,0)}function ce(){const J=s.length/3;let oe=0;Pe(V,oe),oe+=V.length;for(let C=0,Fe=P.length;C<Fe;C++){const ne=P[C];Pe(ne,oe),oe+=ne.length}n.addGroup(J,s.length/3-J,1)}function Pe(J,oe){let C=J.length;for(;--C>=0;){const Fe=C;let ne=C-1;ne<0&&(ne=J.length-1);for(let we=0,de=u+g*2;we<de;we++){const We=W*we,Ee=W*(we+1),A=oe+Fe+We,y=oe+ne+We,F=oe+ne+Ee,q=oe+Fe+Ee;$e(A,y,F,q)}}}function fe(J,oe,C){c.push(J),c.push(oe),c.push(C)}function ze(J,oe,C){qe(J),qe(oe),qe(C);const Fe=s.length/3,ne=M.generateTopUV(n,s,Fe-3,Fe-2,Fe-1);ct(ne[0]),ct(ne[1]),ct(ne[2])}function $e(J,oe,C,Fe){qe(J),qe(oe),qe(Fe),qe(oe),qe(C),qe(Fe);const ne=s.length/3,we=M.generateSideWallUV(n,s,ne-6,ne-3,ne-2,ne-1);ct(we[0]),ct(we[1]),ct(we[3]),ct(we[1]),ct(we[2]),ct(we[3])}function qe(J){s.push(c[J*3+0]),s.push(c[J*3+1]),s.push(c[J*3+2])}function ct(J){r.push(J.x),r.push(J.y)}}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}toJSON(){const e=super.toJSON(),t=this.parameters.shapes,n=this.parameters.options;return wv(t,n,e)}static fromJSON(e,t){const n=[];for(let r=0,o=e.shapes.length;r<o;r++){const a=t[e.shapes[r]];n.push(a)}const s=e.options.extrudePath;return s!==void 0&&(e.options.extrudePath=new nl[s.type]().fromJSON(s)),new na(n,e.options)}}const bv={generateTopUV:function(i,e,t,n,s){const r=e[t*3],o=e[t*3+1],a=e[n*3],c=e[n*3+1],l=e[s*3],u=e[s*3+1];return[new ie(r,o),new ie(a,c),new ie(l,u)]},generateSideWallUV:function(i,e,t,n,s,r){const o=e[t*3],a=e[t*3+1],c=e[t*3+2],l=e[n*3],u=e[n*3+1],f=e[n*3+2],h=e[s*3],d=e[s*3+1],m=e[s*3+2],_=e[r*3],g=e[r*3+1],p=e[r*3+2];return Math.abs(a-u)<Math.abs(o-l)?[new ie(o,1-c),new ie(l,1-f),new ie(h,1-m),new ie(_,1-p)]:[new ie(a,1-c),new ie(u,1-f),new ie(d,1-m),new ie(g,1-p)]}};function wv(i,e,t){if(t.shapes=[],Array.isArray(i))for(let n=0,s=i.length;n<s;n++){const r=i[n];t.shapes.push(r.uuid)}else t.shapes.push(i.uuid);return t.options=Object.assign({},e),e.extrudePath!==void 0&&(t.options.extrudePath=e.extrudePath.toJSON()),t}class os extends Ft{constructor(e=new di([new ie(0,.5),new ie(-.5,-.5),new ie(.5,-.5)]),t=12){super(),this.type="ShapeGeometry",this.parameters={shapes:e,curveSegments:t};const n=[],s=[],r=[],o=[];let a=0,c=0;if(Array.isArray(e)===!1)l(e);else for(let u=0;u<e.length;u++)l(e[u]),this.addGroup(a,c,u),a+=c,c=0;this.setIndex(n),this.setAttribute("position",new ft(s,3)),this.setAttribute("normal",new ft(r,3)),this.setAttribute("uv",new ft(o,2));function l(u){const f=s.length/3,h=u.extractPoints(t);let d=h.shape;const m=h.holes;Ni.isClockWise(d)===!1&&(d=d.reverse());for(let g=0,p=m.length;g<p;g++){const M=m[g];Ni.isClockWise(M)===!0&&(m[g]=M.reverse())}const _=Ni.triangulateShape(d,m);for(let g=0,p=m.length;g<p;g++){const M=m[g];d=d.concat(M)}for(let g=0,p=d.length;g<p;g++){const M=d[g];s.push(M.x,M.y,0),r.push(0,0,1),o.push(M.x,M.y)}for(let g=0,p=_.length;g<p;g++){const M=_[g],v=M[0]+f,x=M[1]+f,L=M[2]+f;n.push(v,x,L),c+=3}}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}toJSON(){const e=super.toJSON(),t=this.parameters.shapes;return Tv(t,e)}static fromJSON(e,t){const n=[];for(let s=0,r=e.shapes.length;s<r;s++){const o=t[e.shapes[s]];n.push(o)}return new os(n,e.curveSegments)}}function Tv(i,e){if(e.shapes=[],Array.isArray(i))for(let t=0,n=i.length;t<n;t++){const s=i[t];e.shapes.push(s.uuid)}else e.shapes.push(i.uuid);return e}class Ho extends Ft{constructor(e=1,t=32,n=16,s=0,r=Math.PI*2,o=0,a=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:n,phiStart:s,phiLength:r,thetaStart:o,thetaLength:a},t=Math.max(3,Math.floor(t)),n=Math.max(2,Math.floor(n));const c=Math.min(o+a,Math.PI);let l=0;const u=[],f=new b,h=new b,d=[],m=[],_=[],g=[];for(let p=0;p<=n;p++){const M=[],v=p/n;let x=0;p===0&&o===0?x=.5/t:p===n&&c===Math.PI&&(x=-.5/t);for(let L=0;L<=t;L++){const T=L/t;f.x=-e*Math.cos(s+T*r)*Math.sin(o+v*a),f.y=e*Math.cos(o+v*a),f.z=e*Math.sin(s+T*r)*Math.sin(o+v*a),m.push(f.x,f.y,f.z),h.copy(f).normalize(),_.push(h.x,h.y,h.z),g.push(T+x,1-v),M.push(l++)}u.push(M)}for(let p=0;p<n;p++)for(let M=0;M<t;M++){const v=u[p][M+1],x=u[p][M],L=u[p+1][M],T=u[p+1][M+1];(p!==0||o>0)&&d.push(v,x,T),(p!==n-1||c<Math.PI)&&d.push(x,L,T)}this.setIndex(d),this.setAttribute("position",new ft(m,3)),this.setAttribute("normal",new ft(_,3)),this.setAttribute("uv",new ft(g,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Ho(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}class Us extends Ft{constructor(e=1,t=.4,n=12,s=48,r=Math.PI*2){super(),this.type="TorusGeometry",this.parameters={radius:e,tube:t,radialSegments:n,tubularSegments:s,arc:r},n=Math.floor(n),s=Math.floor(s);const o=[],a=[],c=[],l=[],u=new b,f=new b,h=new b;for(let d=0;d<=n;d++)for(let m=0;m<=s;m++){const _=m/s*r,g=d/n*Math.PI*2;f.x=(e+t*Math.cos(g))*Math.cos(_),f.y=(e+t*Math.cos(g))*Math.sin(_),f.z=t*Math.sin(g),a.push(f.x,f.y,f.z),u.x=e*Math.cos(_),u.y=e*Math.sin(_),h.subVectors(f,u).normalize(),c.push(h.x,h.y,h.z),l.push(m/s),l.push(d/n)}for(let d=1;d<=n;d++)for(let m=1;m<=s;m++){const _=(s+1)*d+m-1,g=(s+1)*(d-1)+m-1,p=(s+1)*(d-1)+m,M=(s+1)*d+m;o.push(_,g,M),o.push(g,p,M)}this.setIndex(o),this.setAttribute("position",new ft(a,3)),this.setAttribute("normal",new ft(c,3)),this.setAttribute("uv",new ft(l,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Us(e.radius,e.tube,e.radialSegments,e.tubularSegments,e.arc)}}class Il extends Hn{static get type(){return"MeshStandardMaterial"}constructor(e){super(),this.isMeshStandardMaterial=!0,this.defines={STANDARD:""},this.color=new Ve(16777215),this.roughness=1,this.metalness=0,this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.emissive=new Ve(0),this.emissiveIntensity=1,this.emissiveMap=null,this.bumpMap=null,this.bumpScale=1,this.normalMap=null,this.normalMapType=sf,this.normalScale=new ie(1,1),this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.roughnessMap=null,this.metalnessMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new Un,this.envMapIntensity=1,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.flatShading=!1,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.defines={STANDARD:""},this.color.copy(e.color),this.roughness=e.roughness,this.metalness=e.metalness,this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.emissive.copy(e.emissive),this.emissiveMap=e.emissiveMap,this.emissiveIntensity=e.emissiveIntensity,this.bumpMap=e.bumpMap,this.bumpScale=e.bumpScale,this.normalMap=e.normalMap,this.normalMapType=e.normalMapType,this.normalScale.copy(e.normalScale),this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.roughnessMap=e.roughnessMap,this.metalnessMap=e.metalnessMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.envMapIntensity=e.envMapIntensity,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.flatShading=e.flatShading,this.fog=e.fog,this}}class Xn extends Il{static get type(){return"MeshPhysicalMaterial"}constructor(e){super(),this.isMeshPhysicalMaterial=!0,this.defines={STANDARD:"",PHYSICAL:""},this.anisotropyRotation=0,this.anisotropyMap=null,this.clearcoatMap=null,this.clearcoatRoughness=0,this.clearcoatRoughnessMap=null,this.clearcoatNormalScale=new ie(1,1),this.clearcoatNormalMap=null,this.ior=1.5,Object.defineProperty(this,"reflectivity",{get:function(){return Bt(2.5*(this.ior-1)/(this.ior+1),0,1)},set:function(t){this.ior=(1+.4*t)/(1-.4*t)}}),this.iridescenceMap=null,this.iridescenceIOR=1.3,this.iridescenceThicknessRange=[100,400],this.iridescenceThicknessMap=null,this.sheenColor=new Ve(0),this.sheenColorMap=null,this.sheenRoughness=1,this.sheenRoughnessMap=null,this.transmissionMap=null,this.thickness=0,this.thicknessMap=null,this.attenuationDistance=1/0,this.attenuationColor=new Ve(1,1,1),this.specularIntensity=1,this.specularIntensityMap=null,this.specularColor=new Ve(1,1,1),this.specularColorMap=null,this._anisotropy=0,this._clearcoat=0,this._dispersion=0,this._iridescence=0,this._sheen=0,this._transmission=0,this.setValues(e)}get anisotropy(){return this._anisotropy}set anisotropy(e){this._anisotropy>0!=e>0&&this.version++,this._anisotropy=e}get clearcoat(){return this._clearcoat}set clearcoat(e){this._clearcoat>0!=e>0&&this.version++,this._clearcoat=e}get iridescence(){return this._iridescence}set iridescence(e){this._iridescence>0!=e>0&&this.version++,this._iridescence=e}get dispersion(){return this._dispersion}set dispersion(e){this._dispersion>0!=e>0&&this.version++,this._dispersion=e}get sheen(){return this._sheen}set sheen(e){this._sheen>0!=e>0&&this.version++,this._sheen=e}get transmission(){return this._transmission}set transmission(e){this._transmission>0!=e>0&&this.version++,this._transmission=e}copy(e){return super.copy(e),this.defines={STANDARD:"",PHYSICAL:""},this.anisotropy=e.anisotropy,this.anisotropyRotation=e.anisotropyRotation,this.anisotropyMap=e.anisotropyMap,this.clearcoat=e.clearcoat,this.clearcoatMap=e.clearcoatMap,this.clearcoatRoughness=e.clearcoatRoughness,this.clearcoatRoughnessMap=e.clearcoatRoughnessMap,this.clearcoatNormalMap=e.clearcoatNormalMap,this.clearcoatNormalScale.copy(e.clearcoatNormalScale),this.dispersion=e.dispersion,this.ior=e.ior,this.iridescence=e.iridescence,this.iridescenceMap=e.iridescenceMap,this.iridescenceIOR=e.iridescenceIOR,this.iridescenceThicknessRange=[...e.iridescenceThicknessRange],this.iridescenceThicknessMap=e.iridescenceThicknessMap,this.sheen=e.sheen,this.sheenColor.copy(e.sheenColor),this.sheenColorMap=e.sheenColorMap,this.sheenRoughness=e.sheenRoughness,this.sheenRoughnessMap=e.sheenRoughnessMap,this.transmission=e.transmission,this.transmissionMap=e.transmissionMap,this.thickness=e.thickness,this.thicknessMap=e.thicknessMap,this.attenuationDistance=e.attenuationDistance,this.attenuationColor.copy(e.attenuationColor),this.specularIntensity=e.specularIntensity,this.specularIntensityMap=e.specularIntensityMap,this.specularColor.copy(e.specularColor),this.specularColorMap=e.specularColorMap,this}}function Mo(i,e,t){return!i||!t&&i.constructor===e?i:typeof e.BYTES_PER_ELEMENT=="number"?new e(i):Array.prototype.slice.call(i)}function Av(i){return ArrayBuffer.isView(i)&&!(i instanceof DataView)}function Rv(i){function e(s,r){return i[s]-i[r]}const t=i.length,n=new Array(t);for(let s=0;s!==t;++s)n[s]=s;return n.sort(e),n}function mh(i,e,t){const n=i.length,s=new i.constructor(n);for(let r=0,o=0;o!==n;++r){const a=t[r]*e;for(let c=0;c!==e;++c)s[o++]=i[a+c]}return s}function If(i,e,t,n){let s=1,r=i[0];for(;r!==void 0&&r[n]===void 0;)r=i[s++];if(r===void 0)return;let o=r[n];if(o!==void 0)if(Array.isArray(o))do o=r[n],o!==void 0&&(e.push(r.time),t.push.apply(t,o)),r=i[s++];while(r!==void 0);else if(o.toArray!==void 0)do o=r[n],o!==void 0&&(e.push(r.time),o.toArray(t,t.length)),r=i[s++];while(r!==void 0);else do o=r[n],o!==void 0&&(e.push(r.time),t.push(o)),r=i[s++];while(r!==void 0)}class Ur{constructor(e,t,n,s){this.parameterPositions=e,this._cachedIndex=0,this.resultBuffer=s!==void 0?s:new t.constructor(n),this.sampleValues=t,this.valueSize=n,this.settings=null,this.DefaultSettings_={}}evaluate(e){const t=this.parameterPositions;let n=this._cachedIndex,s=t[n],r=t[n-1];n:{e:{let o;t:{i:if(!(e<s)){for(let a=n+2;;){if(s===void 0){if(e<r)break i;return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}if(n===a)break;if(r=s,s=t[++n],e<s)break e}o=t.length;break t}if(!(e>=r)){const a=t[1];e<a&&(n=2,r=a);for(let c=n-2;;){if(r===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(n===c)break;if(s=r,r=t[--n-1],e>=r)break e}o=n,n=0;break t}break n}for(;n<o;){const a=n+o>>>1;e<t[a]?o=a:n=a+1}if(s=t[n],r=t[n-1],r===void 0)return this._cachedIndex=0,this.copySampleValue_(0);if(s===void 0)return n=t.length,this._cachedIndex=n,this.copySampleValue_(n-1)}this._cachedIndex=n,this.intervalChanged_(n,r,s)}return this.interpolate_(n,r,e,s)}getSettings_(){return this.settings||this.DefaultSettings_}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,s=this.valueSize,r=e*s;for(let o=0;o!==s;++o)t[o]=n[r+o];return t}interpolate_(){throw new Error("call to abstract method")}intervalChanged_(){}}class Cv extends Ur{constructor(e,t,n,s){super(e,t,n,s),this._weightPrev=-0,this._offsetPrev=-0,this._weightNext=-0,this._offsetNext=-0,this.DefaultSettings_={endingStart:eu,endingEnd:eu}}intervalChanged_(e,t,n){const s=this.parameterPositions;let r=e-2,o=e+1,a=s[r],c=s[o];if(a===void 0)switch(this.getSettings_().endingStart){case tu:r=e,a=2*t-n;break;case nu:r=s.length-2,a=t+s[r]-s[r+1];break;default:r=e,a=n}if(c===void 0)switch(this.getSettings_().endingEnd){case tu:o=e,c=2*n-t;break;case nu:o=1,c=n+s[1]-s[0];break;default:o=e-1,c=t}const l=(n-t)*.5,u=this.valueSize;this._weightPrev=l/(t-a),this._weightNext=l/(c-n),this._offsetPrev=r*u,this._offsetNext=o*u}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=e*a,l=c-a,u=this._offsetPrev,f=this._offsetNext,h=this._weightPrev,d=this._weightNext,m=(n-t)/(s-t),_=m*m,g=_*m,p=-h*g+2*h*_-h*m,M=(1+h)*g+(-1.5-2*h)*_+(-.5+h)*m+1,v=(-1-d)*g+(1.5+d)*_+.5*m,x=d*g-d*_;for(let L=0;L!==a;++L)r[L]=p*o[u+L]+M*o[l+L]+v*o[c+L]+x*o[f+L];return r}}class Pv extends Ur{constructor(e,t,n,s){super(e,t,n,s)}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=e*a,l=c-a,u=(n-t)/(s-t),f=1-u;for(let h=0;h!==a;++h)r[h]=o[l+h]*f+o[c+h]*u;return r}}class Lv extends Ur{constructor(e,t,n,s){super(e,t,n,s)}interpolate_(e){return this.copySampleValue_(e-1)}}class qn{constructor(e,t,n,s){if(e===void 0)throw new Error("THREE.KeyframeTrack: track name is undefined");if(t===void 0||t.length===0)throw new Error("THREE.KeyframeTrack: no keyframes in track named "+e);this.name=e,this.times=Mo(t,this.TimeBufferType),this.values=Mo(n,this.ValueBufferType),this.setInterpolation(s||this.DefaultInterpolation)}static toJSON(e){const t=e.constructor;let n;if(t.toJSON!==this.toJSON)n=t.toJSON(e);else{n={name:e.name,times:Mo(e.times,Array),values:Mo(e.values,Array)};const s=e.getInterpolation();s!==e.DefaultInterpolation&&(n.interpolation=s)}return n.type=e.ValueTypeName,n}InterpolantFactoryMethodDiscrete(e){return new Lv(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodLinear(e){return new Pv(this.times,this.values,this.getValueSize(),e)}InterpolantFactoryMethodSmooth(e){return new Cv(this.times,this.values,this.getValueSize(),e)}setInterpolation(e){let t;switch(e){case Ar:t=this.InterpolantFactoryMethodDiscrete;break;case Rr:t=this.InterpolantFactoryMethodLinear;break;case ha:t=this.InterpolantFactoryMethodSmooth;break}if(t===void 0){const n="unsupported interpolation for "+this.ValueTypeName+" keyframe track named "+this.name;if(this.createInterpolant===void 0)if(e!==this.DefaultInterpolation)this.setInterpolation(this.DefaultInterpolation);else throw new Error(n);return console.warn("THREE.KeyframeTrack:",n),this}return this.createInterpolant=t,this}getInterpolation(){switch(this.createInterpolant){case this.InterpolantFactoryMethodDiscrete:return Ar;case this.InterpolantFactoryMethodLinear:return Rr;case this.InterpolantFactoryMethodSmooth:return ha}}getValueSize(){return this.values.length/this.times.length}shift(e){if(e!==0){const t=this.times;for(let n=0,s=t.length;n!==s;++n)t[n]+=e}return this}scale(e){if(e!==1){const t=this.times;for(let n=0,s=t.length;n!==s;++n)t[n]*=e}return this}trim(e,t){const n=this.times,s=n.length;let r=0,o=s-1;for(;r!==s&&n[r]<e;)++r;for(;o!==-1&&n[o]>t;)--o;if(++o,r!==0||o!==s){r>=o&&(o=Math.max(o,1),r=o-1);const a=this.getValueSize();this.times=n.slice(r,o),this.values=this.values.slice(r*a,o*a)}return this}validate(){let e=!0;const t=this.getValueSize();t-Math.floor(t)!==0&&(console.error("THREE.KeyframeTrack: Invalid value size in track.",this),e=!1);const n=this.times,s=this.values,r=n.length;r===0&&(console.error("THREE.KeyframeTrack: Track is empty.",this),e=!1);let o=null;for(let a=0;a!==r;a++){const c=n[a];if(typeof c=="number"&&isNaN(c)){console.error("THREE.KeyframeTrack: Time is not a valid number.",this,a,c),e=!1;break}if(o!==null&&o>c){console.error("THREE.KeyframeTrack: Out of order keys.",this,a,c,o),e=!1;break}o=c}if(s!==void 0&&Av(s))for(let a=0,c=s.length;a!==c;++a){const l=s[a];if(isNaN(l)){console.error("THREE.KeyframeTrack: Value is not a valid number.",this,a,l),e=!1;break}}return e}optimize(){const e=this.times.slice(),t=this.values.slice(),n=this.getValueSize(),s=this.getInterpolation()===ha,r=e.length-1;let o=1;for(let a=1;a<r;++a){let c=!1;const l=e[a],u=e[a+1];if(l!==u&&(a!==1||l!==e[0]))if(s)c=!0;else{const f=a*n,h=f-n,d=f+n;for(let m=0;m!==n;++m){const _=t[f+m];if(_!==t[h+m]||_!==t[d+m]){c=!0;break}}}if(c){if(a!==o){e[o]=e[a];const f=a*n,h=o*n;for(let d=0;d!==n;++d)t[h+d]=t[f+d]}++o}}if(r>0){e[o]=e[r];for(let a=r*n,c=o*n,l=0;l!==n;++l)t[c+l]=t[a+l];++o}return o!==e.length?(this.times=e.slice(0,o),this.values=t.slice(0,o*n)):(this.times=e,this.values=t),this}clone(){const e=this.times.slice(),t=this.values.slice(),n=this.constructor,s=new n(this.name,e,t);return s.createInterpolant=this.createInterpolant,s}}qn.prototype.TimeBufferType=Float32Array;qn.prototype.ValueBufferType=Float32Array;qn.prototype.DefaultInterpolation=Rr;class Zs extends qn{constructor(e,t,n){super(e,t,n)}}Zs.prototype.ValueTypeName="bool";Zs.prototype.ValueBufferType=Array;Zs.prototype.DefaultInterpolation=Ar;Zs.prototype.InterpolantFactoryMethodLinear=void 0;Zs.prototype.InterpolantFactoryMethodSmooth=void 0;class Df extends qn{}Df.prototype.ValueTypeName="color";class Xs extends qn{}Xs.prototype.ValueTypeName="number";class Iv extends Ur{constructor(e,t,n,s){super(e,t,n,s)}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=(n-t)/(s-t);let l=e*a;for(let u=l+a;l!==u;l+=4)On.slerpFlat(r,0,o,l-a,o,l,c);return r}}class qs extends qn{InterpolantFactoryMethodLinear(e){return new Iv(this.times,this.values,this.getValueSize(),e)}}qs.prototype.ValueTypeName="quaternion";qs.prototype.InterpolantFactoryMethodSmooth=void 0;class Js extends qn{constructor(e,t,n){super(e,t,n)}}Js.prototype.ValueTypeName="string";Js.prototype.ValueBufferType=Array;Js.prototype.DefaultInterpolation=Ar;Js.prototype.InterpolantFactoryMethodLinear=void 0;Js.prototype.InterpolantFactoryMethodSmooth=void 0;class Ys extends qn{}Ys.prototype.ValueTypeName="vector";class Dv{constructor(e="",t=-1,n=[],s=ep){this.name=e,this.tracks=n,this.duration=t,this.blendMode=s,this.uuid=wn(),this.duration<0&&this.resetDuration()}static parse(e){const t=[],n=e.tracks,s=1/(e.fps||1);for(let o=0,a=n.length;o!==a;++o)t.push(Uv(n[o]).scale(s));const r=new this(e.name,e.duration,t,e.blendMode);return r.uuid=e.uuid,r}static toJSON(e){const t=[],n=e.tracks,s={name:e.name,duration:e.duration,tracks:t,uuid:e.uuid,blendMode:e.blendMode};for(let r=0,o=n.length;r!==o;++r)t.push(qn.toJSON(n[r]));return s}static CreateFromMorphTargetSequence(e,t,n,s){const r=t.length,o=[];for(let a=0;a<r;a++){let c=[],l=[];c.push((a+r-1)%r,a,(a+1)%r),l.push(0,1,0);const u=Rv(c);c=mh(c,1,u),l=mh(l,1,u),!s&&c[0]===0&&(c.push(r),l.push(l[0])),o.push(new Xs(".morphTargetInfluences["+t[a].name+"]",c,l).scale(1/n))}return new this(e,-1,o)}static findByName(e,t){let n=e;if(!Array.isArray(e)){const s=e;n=s.geometry&&s.geometry.animations||s.animations}for(let s=0;s<n.length;s++)if(n[s].name===t)return n[s];return null}static CreateClipsFromMorphTargetSequences(e,t,n){const s={},r=/^([\w-]*?)([\d]+)$/;for(let a=0,c=e.length;a<c;a++){const l=e[a],u=l.name.match(r);if(u&&u.length>1){const f=u[1];let h=s[f];h||(s[f]=h=[]),h.push(l)}}const o=[];for(const a in s)o.push(this.CreateFromMorphTargetSequence(a,s[a],t,n));return o}static parseAnimation(e,t){if(!e)return console.error("THREE.AnimationClip: No animation in JSONLoader data."),null;const n=function(f,h,d,m,_){if(d.length!==0){const g=[],p=[];If(d,g,p,m),g.length!==0&&_.push(new f(h,g,p))}},s=[],r=e.name||"default",o=e.fps||30,a=e.blendMode;let c=e.length||-1;const l=e.hierarchy||[];for(let f=0;f<l.length;f++){const h=l[f].keys;if(!(!h||h.length===0))if(h[0].morphTargets){const d={};let m;for(m=0;m<h.length;m++)if(h[m].morphTargets)for(let _=0;_<h[m].morphTargets.length;_++)d[h[m].morphTargets[_]]=-1;for(const _ in d){const g=[],p=[];for(let M=0;M!==h[m].morphTargets.length;++M){const v=h[m];g.push(v.time),p.push(v.morphTarget===_?1:0)}s.push(new Xs(".morphTargetInfluence["+_+"]",g,p))}c=d.length*o}else{const d=".bones["+t[f].name+"]";n(Ys,d+".position",h,"pos",s),n(qs,d+".quaternion",h,"rot",s),n(Ys,d+".scale",h,"scl",s)}}return s.length===0?null:new this(r,c,s,a)}resetDuration(){const e=this.tracks;let t=0;for(let n=0,s=e.length;n!==s;++n){const r=this.tracks[n];t=Math.max(t,r.times[r.times.length-1])}return this.duration=t,this}trim(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].trim(0,this.duration);return this}validate(){let e=!0;for(let t=0;t<this.tracks.length;t++)e=e&&this.tracks[t].validate();return e}optimize(){for(let e=0;e<this.tracks.length;e++)this.tracks[e].optimize();return this}clone(){const e=[];for(let t=0;t<this.tracks.length;t++)e.push(this.tracks[t].clone());return new this.constructor(this.name,this.duration,e,this.blendMode)}toJSON(){return this.constructor.toJSON(this)}}function Nv(i){switch(i.toLowerCase()){case"scalar":case"double":case"float":case"number":case"integer":return Xs;case"vector":case"vector2":case"vector3":case"vector4":return Ys;case"color":return Df;case"quaternion":return qs;case"bool":case"boolean":return Zs;case"string":return Js}throw new Error("THREE.KeyframeTrack: Unsupported typeName: "+i)}function Uv(i){if(i.type===void 0)throw new Error("THREE.KeyframeTrack: track type undefined, can not parse");const e=Nv(i.type);if(i.times===void 0){const t=[],n=[];If(i.keys,t,n,"value"),i.times=t,i.values=n}return e.parse!==void 0?e.parse(i):new e(i.name,i.times,i.values,i.interpolation)}const Ri={enabled:!1,files:{},add:function(i,e){this.enabled!==!1&&(this.files[i]=e)},get:function(i){if(this.enabled!==!1)return this.files[i]},remove:function(i){delete this.files[i]},clear:function(){this.files={}}};class Ov{constructor(e,t,n){const s=this;let r=!1,o=0,a=0,c;const l=[];this.onStart=void 0,this.onLoad=e,this.onProgress=t,this.onError=n,this.itemStart=function(u){a++,r===!1&&s.onStart!==void 0&&s.onStart(u,o,a),r=!0},this.itemEnd=function(u){o++,s.onProgress!==void 0&&s.onProgress(u,o,a),o===a&&(r=!1,s.onLoad!==void 0&&s.onLoad())},this.itemError=function(u){s.onError!==void 0&&s.onError(u)},this.resolveURL=function(u){return c?c(u):u},this.setURLModifier=function(u){return c=u,this},this.addHandler=function(u,f){return l.push(u,f),this},this.removeHandler=function(u){const f=l.indexOf(u);return f!==-1&&l.splice(f,2),this},this.getHandler=function(u){for(let f=0,h=l.length;f<h;f+=2){const d=l[f],m=l[f+1];if(d.global&&(d.lastIndex=0),d.test(u))return m}return null}}}const Fv=new Ov;class as{constructor(e){this.manager=e!==void 0?e:Fv,this.crossOrigin="anonymous",this.withCredentials=!1,this.path="",this.resourcePath="",this.requestHeader={}}load(){}loadAsync(e,t){const n=this;return new Promise(function(s,r){n.load(e,s,t,r)})}parse(){}setCrossOrigin(e){return this.crossOrigin=e,this}setWithCredentials(e){return this.withCredentials=e,this}setPath(e){return this.path=e,this}setResourcePath(e){return this.resourcePath=e,this}setRequestHeader(e){return this.requestHeader=e,this}}as.DEFAULT_MATERIAL_NAME="__DEFAULT";const ei={};class Bv extends Error{constructor(e,t){super(e),this.response=t}}class Vo extends as{constructor(e){super(e)}load(e,t,n,s){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const r=Ri.get(e);if(r!==void 0)return this.manager.itemStart(e),setTimeout(()=>{t&&t(r),this.manager.itemEnd(e)},0),r;if(ei[e]!==void 0){ei[e].push({onLoad:t,onProgress:n,onError:s});return}ei[e]=[],ei[e].push({onLoad:t,onProgress:n,onError:s});const o=new Request(e,{headers:new Headers(this.requestHeader),credentials:this.withCredentials?"include":"same-origin"}),a=this.mimeType,c=this.responseType;fetch(o).then(l=>{if(l.status===200||l.status===0){if(l.status===0&&console.warn("THREE.FileLoader: HTTP Status 0 received."),typeof ReadableStream>"u"||l.body===void 0||l.body.getReader===void 0)return l;const u=ei[e],f=l.body.getReader(),h=l.headers.get("X-File-Size")||l.headers.get("Content-Length"),d=h?parseInt(h):0,m=d!==0;let _=0;const g=new ReadableStream({start(p){M();function M(){f.read().then(({done:v,value:x})=>{if(v)p.close();else{_+=x.byteLength;const L=new ProgressEvent("progress",{lengthComputable:m,loaded:_,total:d});for(let T=0,R=u.length;T<R;T++){const I=u[T];I.onProgress&&I.onProgress(L)}p.enqueue(x),M()}},v=>{p.error(v)})}}});return new Response(g)}else throw new Bv(`fetch for "${l.url}" responded with ${l.status}: ${l.statusText}`,l)}).then(l=>{switch(c){case"arraybuffer":return l.arrayBuffer();case"blob":return l.blob();case"document":return l.text().then(u=>new DOMParser().parseFromString(u,a));case"json":return l.json();default:if(a===void 0)return l.text();{const f=/charset="?([^;"\s]*)"?/i.exec(a),h=f&&f[1]?f[1].toLowerCase():void 0,d=new TextDecoder(h);return l.arrayBuffer().then(m=>d.decode(m))}}}).then(l=>{Ri.add(e,l);const u=ei[e];delete ei[e];for(let f=0,h=u.length;f<h;f++){const d=u[f];d.onLoad&&d.onLoad(l)}}).catch(l=>{const u=ei[e];if(u===void 0)throw this.manager.itemError(e),l;delete ei[e];for(let f=0,h=u.length;f<h;f++){const d=u[f];d.onError&&d.onError(l)}this.manager.itemError(e)}).finally(()=>{this.manager.itemEnd(e)}),this.manager.itemStart(e)}setResponseType(e){return this.responseType=e,this}setMimeType(e){return this.mimeType=e,this}}class kv extends as{constructor(e){super(e)}load(e,t,n,s){this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const r=this,o=Ri.get(e);if(o!==void 0)return r.manager.itemStart(e),setTimeout(function(){t&&t(o),r.manager.itemEnd(e)},0),o;const a=Cr("img");function c(){u(),Ri.add(e,this),t&&t(this),r.manager.itemEnd(e)}function l(f){u(),s&&s(f),r.manager.itemError(e),r.manager.itemEnd(e)}function u(){a.removeEventListener("load",c,!1),a.removeEventListener("error",l,!1)}return a.addEventListener("load",c,!1),a.addEventListener("error",l,!1),e.slice(0,5)!=="data:"&&this.crossOrigin!==void 0&&(a.crossOrigin=this.crossOrigin),r.manager.itemStart(e),a.src=e,a}}class zv extends as{constructor(e){super(e)}load(e,t,n,s){const r=new Wt,o=new kv(this.manager);return o.setCrossOrigin(this.crossOrigin),o.setPath(this.path),o.load(e,function(a){r.image=a,r.needsUpdate=!0,t!==void 0&&t(r)},n,s),r}}class Dl extends At{constructor(e,t=1){super(),this.isLight=!0,this.type="Light",this.color=new Ve(e),this.intensity=t}dispose(){}copy(e,t){return super.copy(e,t),this.color.copy(e.color),this.intensity=e.intensity,this}toJSON(e){const t=super.toJSON(e);return t.object.color=this.color.getHex(),t.object.intensity=this.intensity,this.groundColor!==void 0&&(t.object.groundColor=this.groundColor.getHex()),this.distance!==void 0&&(t.object.distance=this.distance),this.angle!==void 0&&(t.object.angle=this.angle),this.decay!==void 0&&(t.object.decay=this.decay),this.penumbra!==void 0&&(t.object.penumbra=this.penumbra),this.shadow!==void 0&&(t.object.shadow=this.shadow.toJSON()),this.target!==void 0&&(t.object.target=this.target.uuid),t}}const qa=new De,gh=new b,_h=new b;class Nl{constructor(e){this.camera=e,this.intensity=1,this.bias=0,this.normalBias=0,this.radius=1,this.blurSamples=8,this.mapSize=new ie(512,512),this.map=null,this.mapPass=null,this.matrix=new De,this.autoUpdate=!0,this.needsUpdate=!1,this._frustum=new El,this._frameExtents=new ie(1,1),this._viewportCount=1,this._viewports=[new ht(0,0,1,1)]}getViewportCount(){return this._viewportCount}getFrustum(){return this._frustum}updateMatrices(e){const t=this.camera,n=this.matrix;gh.setFromMatrixPosition(e.matrixWorld),t.position.copy(gh),_h.setFromMatrixPosition(e.target.matrixWorld),t.lookAt(_h),t.updateMatrixWorld(),qa.multiplyMatrices(t.projectionMatrix,t.matrixWorldInverse),this._frustum.setFromProjectionMatrix(qa),n.set(.5,0,0,.5,0,.5,0,.5,0,0,.5,.5,0,0,0,1),n.multiply(qa)}getViewport(e){return this._viewports[e]}getFrameExtents(){return this._frameExtents}dispose(){this.map&&this.map.dispose(),this.mapPass&&this.mapPass.dispose()}copy(e){return this.camera=e.camera.clone(),this.intensity=e.intensity,this.bias=e.bias,this.radius=e.radius,this.mapSize.copy(e.mapSize),this}clone(){return new this.constructor().copy(this)}toJSON(){const e={};return this.intensity!==1&&(e.intensity=this.intensity),this.bias!==0&&(e.bias=this.bias),this.normalBias!==0&&(e.normalBias=this.normalBias),this.radius!==1&&(e.radius=this.radius),(this.mapSize.x!==512||this.mapSize.y!==512)&&(e.mapSize=this.mapSize.toArray()),e.camera=this.camera.toJSON(!1).object,delete e.camera.matrix,e}}class Hv extends Nl{constructor(){super(new ln(50,1,.5,500)),this.isSpotLightShadow=!0,this.focus=1}updateMatrices(e){const t=this.camera,n=Gs*2*e.angle*this.focus,s=this.mapSize.width/this.mapSize.height,r=e.distance||t.far;(n!==t.fov||s!==t.aspect||r!==t.far)&&(t.fov=n,t.aspect=s,t.far=r,t.updateProjectionMatrix()),super.updateMatrices(e)}copy(e){return super.copy(e),this.focus=e.focus,this}}class Vv extends Dl{constructor(e,t,n=0,s=Math.PI/3,r=0,o=2){super(e,t),this.isSpotLight=!0,this.type="SpotLight",this.position.copy(At.DEFAULT_UP),this.updateMatrix(),this.target=new At,this.distance=n,this.angle=s,this.penumbra=r,this.decay=o,this.map=null,this.shadow=new Hv}get power(){return this.intensity*Math.PI}set power(e){this.intensity=e/Math.PI}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.angle=e.angle,this.penumbra=e.penumbra,this.decay=e.decay,this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}const xh=new De,hr=new b,Ya=new b;class Gv extends Nl{constructor(){super(new ln(90,1,.5,500)),this.isPointLightShadow=!0,this._frameExtents=new ie(4,2),this._viewportCount=6,this._viewports=[new ht(2,1,1,1),new ht(0,1,1,1),new ht(3,1,1,1),new ht(1,1,1,1),new ht(3,0,1,1),new ht(1,0,1,1)],this._cubeDirections=[new b(1,0,0),new b(-1,0,0),new b(0,0,1),new b(0,0,-1),new b(0,1,0),new b(0,-1,0)],this._cubeUps=[new b(0,1,0),new b(0,1,0),new b(0,1,0),new b(0,1,0),new b(0,0,1),new b(0,0,-1)]}updateMatrices(e,t=0){const n=this.camera,s=this.matrix,r=e.distance||n.far;r!==n.far&&(n.far=r,n.updateProjectionMatrix()),hr.setFromMatrixPosition(e.matrixWorld),n.position.copy(hr),Ya.copy(n.position),Ya.add(this._cubeDirections[t]),n.up.copy(this._cubeUps[t]),n.lookAt(Ya),n.updateMatrixWorld(),s.makeTranslation(-hr.x,-hr.y,-hr.z),xh.multiplyMatrices(n.projectionMatrix,n.matrixWorldInverse),this._frustum.setFromProjectionMatrix(xh)}}class Wv extends Dl{constructor(e,t,n=0,s=2){super(e,t),this.isPointLight=!0,this.type="PointLight",this.distance=n,this.decay=s,this.shadow=new Gv}get power(){return this.intensity*4*Math.PI}set power(e){this.intensity=e/(4*Math.PI)}dispose(){this.shadow.dispose()}copy(e,t){return super.copy(e,t),this.distance=e.distance,this.decay=e.decay,this.shadow=e.shadow.clone(),this}}class Xv extends Nl{constructor(){super(new Zo(-5,5,5,-5,.5,500)),this.isDirectionalLightShadow=!0}}class qv extends Dl{constructor(e,t){super(e,t),this.isDirectionalLight=!0,this.type="DirectionalLight",this.position.copy(At.DEFAULT_UP),this.updateMatrix(),this.target=new At,this.shadow=new Xv}dispose(){this.shadow.dispose()}copy(e){return super.copy(e),this.target=e.target.clone(),this.shadow=e.shadow.clone(),this}}class br{static decodeText(e){if(console.warn("THREE.LoaderUtils: decodeText() has been deprecated with r165 and will be removed with r175. Use TextDecoder instead."),typeof TextDecoder<"u")return new TextDecoder().decode(e);let t="";for(let n=0,s=e.length;n<s;n++)t+=String.fromCharCode(e[n]);try{return decodeURIComponent(escape(t))}catch{return t}}static extractUrlBase(e){const t=e.lastIndexOf("/");return t===-1?"./":e.slice(0,t+1)}static resolveURL(e,t){return typeof e!="string"||e===""?"":(/^https?:\/\//i.test(t)&&/^\//.test(e)&&(t=t.replace(/(^https?:\/\/[^\/]+).*/i,"$1")),/^(https?:)?\/\//i.test(e)||/^data:.*,.*$/i.test(e)||/^blob:.*$/i.test(e)?e:t+e)}}class Yv extends as{constructor(e){super(e),this.isImageBitmapLoader=!0,typeof createImageBitmap>"u"&&console.warn("THREE.ImageBitmapLoader: createImageBitmap() not supported."),typeof fetch>"u"&&console.warn("THREE.ImageBitmapLoader: fetch() not supported."),this.options={premultiplyAlpha:"none"}}setOptions(e){return this.options=e,this}load(e,t,n,s){e===void 0&&(e=""),this.path!==void 0&&(e=this.path+e),e=this.manager.resolveURL(e);const r=this,o=Ri.get(e);if(o!==void 0){if(r.manager.itemStart(e),o.then){o.then(l=>{t&&t(l),r.manager.itemEnd(e)}).catch(l=>{s&&s(l)});return}return setTimeout(function(){t&&t(o),r.manager.itemEnd(e)},0),o}const a={};a.credentials=this.crossOrigin==="anonymous"?"same-origin":"include",a.headers=this.requestHeader;const c=fetch(e,a).then(function(l){return l.blob()}).then(function(l){return createImageBitmap(l,Object.assign(r.options,{colorSpaceConversion:"none"}))}).then(function(l){return Ri.add(e,l),t&&t(l),r.manager.itemEnd(e),l}).catch(function(l){s&&s(l),Ri.remove(e),r.manager.itemError(e),r.manager.itemEnd(e)});Ri.add(e,c),r.manager.itemStart(e)}}const Ul="\\[\\]\\.:\\/",jv=new RegExp("["+Ul+"]","g"),Ol="[^"+Ul+"]",$v="[^"+Ul.replace("\\.","")+"]",Kv=/((?:WC+[\/:])*)/.source.replace("WC",Ol),Zv=/(WCOD+)?/.source.replace("WCOD",$v),Jv=/(?:\.(WC+)(?:\[(.+)\])?)?/.source.replace("WC",Ol),Qv=/\.(WC+)(?:\[(.+)\])?/.source.replace("WC",Ol),ey=new RegExp("^"+Kv+Zv+Jv+Qv+"$"),ty=["material","materials","bones","map"];class ny{constructor(e,t,n){const s=n||xt.parseTrackName(t);this._targetGroup=e,this._bindings=e.subscribe_(t,s)}getValue(e,t){this.bind();const n=this._targetGroup.nCachedObjects_,s=this._bindings[n];s!==void 0&&s.getValue(e,t)}setValue(e,t){const n=this._bindings;for(let s=this._targetGroup.nCachedObjects_,r=n.length;s!==r;++s)n[s].setValue(e,t)}bind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].bind()}unbind(){const e=this._bindings;for(let t=this._targetGroup.nCachedObjects_,n=e.length;t!==n;++t)e[t].unbind()}}class xt{constructor(e,t,n){this.path=t,this.parsedPath=n||xt.parseTrackName(t),this.node=xt.findNode(e,this.parsedPath.nodeName),this.rootNode=e,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}static create(e,t,n){return e&&e.isAnimationObjectGroup?new xt.Composite(e,t,n):new xt(e,t,n)}static sanitizeNodeName(e){return e.replace(/\s/g,"_").replace(jv,"")}static parseTrackName(e){const t=ey.exec(e);if(t===null)throw new Error("PropertyBinding: Cannot parse trackName: "+e);const n={nodeName:t[2],objectName:t[3],objectIndex:t[4],propertyName:t[5],propertyIndex:t[6]},s=n.nodeName&&n.nodeName.lastIndexOf(".");if(s!==void 0&&s!==-1){const r=n.nodeName.substring(s+1);ty.indexOf(r)!==-1&&(n.nodeName=n.nodeName.substring(0,s),n.objectName=r)}if(n.propertyName===null||n.propertyName.length===0)throw new Error("PropertyBinding: can not parse propertyName from trackName: "+e);return n}static findNode(e,t){if(t===void 0||t===""||t==="."||t===-1||t===e.name||t===e.uuid)return e;if(e.skeleton){const n=e.skeleton.getBoneByName(t);if(n!==void 0)return n}if(e.children){const n=function(r){for(let o=0;o<r.length;o++){const a=r[o];if(a.name===t||a.uuid===t)return a;const c=n(a.children);if(c)return c}return null},s=n(e.children);if(s)return s}return null}_getValue_unavailable(){}_setValue_unavailable(){}_getValue_direct(e,t){e[t]=this.targetObject[this.propertyName]}_getValue_array(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)e[t++]=n[s]}_getValue_arrayElement(e,t){e[t]=this.resolvedProperty[this.propertyIndex]}_getValue_toArray(e,t){this.resolvedProperty.toArray(e,t)}_setValue_direct(e,t){this.targetObject[this.propertyName]=e[t]}_setValue_direct_setNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.needsUpdate=!0}_setValue_direct_setMatrixWorldNeedsUpdate(e,t){this.targetObject[this.propertyName]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_array(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)n[s]=e[t++]}_setValue_array_setNeedsUpdate(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)n[s]=e[t++];this.targetObject.needsUpdate=!0}_setValue_array_setMatrixWorldNeedsUpdate(e,t){const n=this.resolvedProperty;for(let s=0,r=n.length;s!==r;++s)n[s]=e[t++];this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_arrayElement(e,t){this.resolvedProperty[this.propertyIndex]=e[t]}_setValue_arrayElement_setNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.needsUpdate=!0}_setValue_arrayElement_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty[this.propertyIndex]=e[t],this.targetObject.matrixWorldNeedsUpdate=!0}_setValue_fromArray(e,t){this.resolvedProperty.fromArray(e,t)}_setValue_fromArray_setNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.needsUpdate=!0}_setValue_fromArray_setMatrixWorldNeedsUpdate(e,t){this.resolvedProperty.fromArray(e,t),this.targetObject.matrixWorldNeedsUpdate=!0}_getValue_unbound(e,t){this.bind(),this.getValue(e,t)}_setValue_unbound(e,t){this.bind(),this.setValue(e,t)}bind(){let e=this.node;const t=this.parsedPath,n=t.objectName,s=t.propertyName;let r=t.propertyIndex;if(e||(e=xt.findNode(this.rootNode,t.nodeName),this.node=e),this.getValue=this._getValue_unavailable,this.setValue=this._setValue_unavailable,!e){console.warn("THREE.PropertyBinding: No target node found for track: "+this.path+".");return}if(n){let l=t.objectIndex;switch(n){case"materials":if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.materials){console.error("THREE.PropertyBinding: Can not bind to material.materials as node.material does not have a materials array.",this);return}e=e.material.materials;break;case"bones":if(!e.skeleton){console.error("THREE.PropertyBinding: Can not bind to bones as node does not have a skeleton.",this);return}e=e.skeleton.bones;for(let u=0;u<e.length;u++)if(e[u].name===l){l=u;break}break;case"map":if("map"in e){e=e.map;break}if(!e.material){console.error("THREE.PropertyBinding: Can not bind to material as node does not have a material.",this);return}if(!e.material.map){console.error("THREE.PropertyBinding: Can not bind to material.map as node.material does not have a map.",this);return}e=e.material.map;break;default:if(e[n]===void 0){console.error("THREE.PropertyBinding: Can not bind to objectName of node undefined.",this);return}e=e[n]}if(l!==void 0){if(e[l]===void 0){console.error("THREE.PropertyBinding: Trying to bind to objectIndex of objectName, but is undefined.",this,e);return}e=e[l]}}const o=e[s];if(o===void 0){const l=t.nodeName;console.error("THREE.PropertyBinding: Trying to update property for track: "+l+"."+s+" but it wasn't found.",e);return}let a=this.Versioning.None;this.targetObject=e,e.needsUpdate!==void 0?a=this.Versioning.NeedsUpdate:e.matrixWorldNeedsUpdate!==void 0&&(a=this.Versioning.MatrixWorldNeedsUpdate);let c=this.BindingType.Direct;if(r!==void 0){if(s==="morphTargetInfluences"){if(!e.geometry){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.",this);return}if(!e.geometry.morphAttributes){console.error("THREE.PropertyBinding: Can not bind to morphTargetInfluences because node does not have a geometry.morphAttributes.",this);return}e.morphTargetDictionary[r]!==void 0&&(r=e.morphTargetDictionary[r])}c=this.BindingType.ArrayElement,this.resolvedProperty=o,this.propertyIndex=r}else o.fromArray!==void 0&&o.toArray!==void 0?(c=this.BindingType.HasFromToArray,this.resolvedProperty=o):Array.isArray(o)?(c=this.BindingType.EntireArray,this.resolvedProperty=o):this.propertyName=s;this.getValue=this.GetterByBindingType[c],this.setValue=this.SetterByBindingTypeAndVersioning[c][a]}unbind(){this.node=null,this.getValue=this._getValue_unbound,this.setValue=this._setValue_unbound}}xt.Composite=ny;xt.prototype.BindingType={Direct:0,EntireArray:1,ArrayElement:2,HasFromToArray:3};xt.prototype.Versioning={None:0,NeedsUpdate:1,MatrixWorldNeedsUpdate:2};xt.prototype.GetterByBindingType=[xt.prototype._getValue_direct,xt.prototype._getValue_array,xt.prototype._getValue_arrayElement,xt.prototype._getValue_toArray];xt.prototype.SetterByBindingTypeAndVersioning=[[xt.prototype._setValue_direct,xt.prototype._setValue_direct_setNeedsUpdate,xt.prototype._setValue_direct_setMatrixWorldNeedsUpdate],[xt.prototype._setValue_array,xt.prototype._setValue_array_setNeedsUpdate,xt.prototype._setValue_array_setMatrixWorldNeedsUpdate],[xt.prototype._setValue_arrayElement,xt.prototype._setValue_arrayElement_setNeedsUpdate,xt.prototype._setValue_arrayElement_setMatrixWorldNeedsUpdate],[xt.prototype._setValue_fromArray,xt.prototype._setValue_fromArray_setNeedsUpdate,xt.prototype._setValue_fromArray_setMatrixWorldNeedsUpdate]];typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:dl}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=dl);const iy=12,sy=ci.degToRad(iy),ry=1e-7,oy=1e-7,ay=new b(1,1,1),Nf=i=>new De().makeTranslation(i.x,i.y,i.z),vh=(i,e,t)=>e.get(t).clone().multiply(Nf(i.heads.get(t)));function ja(i,e,t){const n=i.parents.get(t),s=vh(i,e,t);return n?vh(i,e,n).invert().multiply(s):s}const $a=i=>{const e=new b,t=new On,n=new b;return i.decompose(e,t,n),{at:e,turn:t}};function cy(i,e,t,n,s=e,r=sy){const o=new Map,a=new Map;let c=n>=1;for(const l of i.order){const u=$a(ja(i,e,l)),f=$a(ja(i,t,l)),h=$a(ja(i,s,l)),d=u.at.lerp(f.at,n),m=u.turn.slerp(f.turn,n),_=h.turn.angleTo(m),g=h.turn.slerp(m,_>r?r/_:1),p=new De().compose(d,g,ay),M=i.parents.get(l),v=M?o.get(M).clone().multiply(p):p;o.set(l,v),a.set(l,v.clone().multiply(Nf(i.heads.get(l).clone().negate()))),c&&(c=g.angleTo(f.turn)<ry&&d.distanceTo(f.at)<oy)}return{moves:a,settled:c}}const ri={hat:{base:3.53,crown:.86,height:1,brim:.2,thick:.05,curl:.18,band:[.04,.24],bandOut:.015,sides:48},white:[.97,.97,.95],whites:["hand_shell_l","hand_shell_r","butler_bow_tie__knot","butler_bow_tie__loop_l","butler_bow_tie__loop_r","butler_shirt__collar_band","butler_shirt__collar_point_l","butler_shirt__collar_point_r"],wing:{points:[[.04,2.47],[.19,2.45],[.09,2.36]],z:.43,thick:.02},tails:{side:[[-.3,1.78],[-.47,1.78],[-.68,.72],[-.58,.72]],across:[.04,.36]},satin:[.15,.15,.24],removed:["butler_bowler_hat","butler_tailcoat__tail_l","butler_tailcoat__tail_r"]};function So(i,e,t,n){t.applyMatrix4(i.matrixWorld.clone().invert());const s=t.attributes.position.count,r=i.geometry.attributes.skinIndex.getX(0);t.setAttribute("skinIndex",new Sl(Array.from({length:s*4},(a,c)=>c%4?0:r),4)),t.setAttribute("skinWeight",new ft(Array.from({length:s*4},(a,c)=>c%4?0:1),4));const o=new Tl(t,new _n({color:new Ve(...n)}));return o.name=e,o.userData={item:e},o.position.copy(i.position),o.quaternion.copy(i.quaternion),o.scale.copy(i.scale),i.parent.add(o),o.bind(i.skeleton,i.bindMatrix),o.updateMatrixWorld(!0),o}function ly(i){const{base:e,crown:t,height:n,brim:s,thick:r,curl:o,sides:a}=ri.hat,c=t+s,l=[[.001,e],[c,e],[c,e+r],[t,e+r],[t,e+n],[.001,e+n]],u=new Qo(l.map(([h,d])=>new ie(h,d)),a),f=u.attributes.position;for(let h=0;h<f.count;h++){const[d,m,_]=[f.getX(h),f.getY(h),f.getZ(h)],g=Math.hypot(d,_);m<=e+r+1e-6&&g>t&&f.setY(h,m+o*((g-t)/s)**2*(d/g)**2)}return u.translate(i.x,0,i.z),u.computeVertexNormals(),u}function uy(i){const{base:e,crown:t,band:n,bandOut:s,sides:r}=ri.hat,o=new Dt(t+s,t+s,n[1]-n[0],r,1,!0);return o.translate(i.x,e+(n[0]+n[1])/2,i.z),o}function hy(i){const{points:e,z:t,thick:n}=ri.wing,s=new di(e.map(([o,a])=>new ie(i*o,a))),r=new na(s,{depth:n,bevelEnabled:!1});return r.translate(0,0,t),r}function fy(i){const{side:e,across:t}=ri.tails,n=new di(e.map(([r,o])=>new ie(r,o))),s=new na(n,{depth:t[1]-t[0],bevelEnabled:!1});return s.rotateY(-Math.PI/2),s.translate(i>0?t[1]:-.04,0,0),s.computeVertexNormals(),s}function dy(i){const e=u=>i.find(f=>f.name===u);for(const u of i.filter(f=>ri.whites.includes(f.name)))u.material=u.material.clone(),u.material.color.setRGB(...ri.white);const t=e("butler_bowler_hat__crown"),n=new on().setFromObject(t).getCenter(new b),s=t.material.color.toArray(),r=e("butler_tailcoat__body").material.color.toArray(),o=e("butler_bow_tie__knot"),a=e("butler_tailcoat__tail_l"),c=[So(t,"butler_top_hat",ly(n),s),So(t,"butler_top_hat_band",uy(n),ri.satin),...[1,-1].map(u=>So(o,`butler_wing_collar_${u>0?"l":"r"}`,hy(u),ri.white)),...[1,-1].map(u=>So(a,`butler_tail_${u>0?"l":"r"}`,fy(u),r))],l=i.filter(u=>ri.removed.some(f=>u.name.startsWith(f)));for(const u of l)u.parent.remove(u);return[...i.filter(u=>!l.includes(u)),...c]}function yh(i,e){if(e===tp)return console.warn("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Geometry already defined as triangles."),i;if(e===Zc||e===nf){let t=i.getIndex();if(t===null){const o=[],a=i.getAttribute("position");if(a!==void 0){for(let c=0;c<a.count;c++)o.push(c);i.setIndex(o),t=i.getIndex()}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Undefined position attribute. Processing not possible."),i}const n=t.count-2,s=[];if(e===Zc)for(let o=1;o<=n;o++)s.push(t.getX(0)),s.push(t.getX(o)),s.push(t.getX(o+1));else for(let o=0;o<n;o++)o%2===0?(s.push(t.getX(o)),s.push(t.getX(o+1)),s.push(t.getX(o+2))):(s.push(t.getX(o+2)),s.push(t.getX(o+1)),s.push(t.getX(o)));s.length/3!==n&&console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unable to generate correct amount of triangles.");const r=i.clone();return r.setIndex(s),r.clearGroups(),r}else return console.error("THREE.BufferGeometryUtils.toTrianglesDrawMode(): Unknown draw mode:",e),i}class py extends as{constructor(e){super(e),this.dracoLoader=null,this.ktx2Loader=null,this.meshoptDecoder=null,this.pluginCallbacks=[],this.register(function(t){return new vy(t)}),this.register(function(t){return new yy(t)}),this.register(function(t){return new Cy(t)}),this.register(function(t){return new Py(t)}),this.register(function(t){return new Ly(t)}),this.register(function(t){return new Sy(t)}),this.register(function(t){return new Ey(t)}),this.register(function(t){return new by(t)}),this.register(function(t){return new wy(t)}),this.register(function(t){return new xy(t)}),this.register(function(t){return new Ty(t)}),this.register(function(t){return new My(t)}),this.register(function(t){return new Ry(t)}),this.register(function(t){return new Ay(t)}),this.register(function(t){return new gy(t)}),this.register(function(t){return new Iy(t)}),this.register(function(t){return new Dy(t)})}load(e,t,n,s){const r=this;let o;if(this.resourcePath!=="")o=this.resourcePath;else if(this.path!==""){const l=br.extractUrlBase(e);o=br.resolveURL(l,this.path)}else o=br.extractUrlBase(e);this.manager.itemStart(e);const a=function(l){s?s(l):console.error(l),r.manager.itemError(e),r.manager.itemEnd(e)},c=new Vo(this.manager);c.setPath(this.path),c.setResponseType("arraybuffer"),c.setRequestHeader(this.requestHeader),c.setWithCredentials(this.withCredentials),c.load(e,function(l){try{r.parse(l,o,function(u){t(u),r.manager.itemEnd(e)},a)}catch(u){a(u)}},n,a)}setDRACOLoader(e){return this.dracoLoader=e,this}setKTX2Loader(e){return this.ktx2Loader=e,this}setMeshoptDecoder(e){return this.meshoptDecoder=e,this}register(e){return this.pluginCallbacks.indexOf(e)===-1&&this.pluginCallbacks.push(e),this}unregister(e){return this.pluginCallbacks.indexOf(e)!==-1&&this.pluginCallbacks.splice(this.pluginCallbacks.indexOf(e),1),this}parse(e,t,n,s){let r;const o={},a={},c=new TextDecoder;if(typeof e=="string")r=JSON.parse(e);else if(e instanceof ArrayBuffer)if(c.decode(new Uint8Array(e,0,4))===Uf){try{o[st.KHR_BINARY_GLTF]=new Ny(e)}catch(f){s&&s(f);return}r=JSON.parse(o[st.KHR_BINARY_GLTF].content)}else r=JSON.parse(c.decode(e));else r=e;if(r.asset===void 0||r.asset.version[0]<2){s&&s(new Error("THREE.GLTFLoader: Unsupported asset. glTF versions >=2.0 are supported."));return}const l=new Yy(r,{path:t||this.resourcePath||"",crossOrigin:this.crossOrigin,requestHeader:this.requestHeader,manager:this.manager,ktx2Loader:this.ktx2Loader,meshoptDecoder:this.meshoptDecoder});l.fileLoader.setRequestHeader(this.requestHeader);for(let u=0;u<this.pluginCallbacks.length;u++){const f=this.pluginCallbacks[u](l);f.name||console.error("THREE.GLTFLoader: Invalid plugin found: missing name"),a[f.name]=f,o[f.name]=!0}if(r.extensionsUsed)for(let u=0;u<r.extensionsUsed.length;++u){const f=r.extensionsUsed[u],h=r.extensionsRequired||[];switch(f){case st.KHR_MATERIALS_UNLIT:o[f]=new _y;break;case st.KHR_DRACO_MESH_COMPRESSION:o[f]=new Uy(r,this.dracoLoader);break;case st.KHR_TEXTURE_TRANSFORM:o[f]=new Oy;break;case st.KHR_MESH_QUANTIZATION:o[f]=new Fy;break;default:h.indexOf(f)>=0&&a[f]===void 0&&console.warn('THREE.GLTFLoader: Unknown extension "'+f+'".')}}l.setExtensions(o),l.setPlugins(a),l.parse(n,s)}parseAsync(e,t){const n=this;return new Promise(function(s,r){n.parse(e,t,s,r)})}}function my(){let i={};return{get:function(e){return i[e]},add:function(e,t){i[e]=t},remove:function(e){delete i[e]},removeAll:function(){i={}}}}const st={KHR_BINARY_GLTF:"KHR_binary_glTF",KHR_DRACO_MESH_COMPRESSION:"KHR_draco_mesh_compression",KHR_LIGHTS_PUNCTUAL:"KHR_lights_punctual",KHR_MATERIALS_CLEARCOAT:"KHR_materials_clearcoat",KHR_MATERIALS_DISPERSION:"KHR_materials_dispersion",KHR_MATERIALS_IOR:"KHR_materials_ior",KHR_MATERIALS_SHEEN:"KHR_materials_sheen",KHR_MATERIALS_SPECULAR:"KHR_materials_specular",KHR_MATERIALS_TRANSMISSION:"KHR_materials_transmission",KHR_MATERIALS_IRIDESCENCE:"KHR_materials_iridescence",KHR_MATERIALS_ANISOTROPY:"KHR_materials_anisotropy",KHR_MATERIALS_UNLIT:"KHR_materials_unlit",KHR_MATERIALS_VOLUME:"KHR_materials_volume",KHR_TEXTURE_BASISU:"KHR_texture_basisu",KHR_TEXTURE_TRANSFORM:"KHR_texture_transform",KHR_MESH_QUANTIZATION:"KHR_mesh_quantization",KHR_MATERIALS_EMISSIVE_STRENGTH:"KHR_materials_emissive_strength",EXT_MATERIALS_BUMP:"EXT_materials_bump",EXT_TEXTURE_WEBP:"EXT_texture_webp",EXT_TEXTURE_AVIF:"EXT_texture_avif",EXT_MESHOPT_COMPRESSION:"EXT_meshopt_compression",EXT_MESH_GPU_INSTANCING:"EXT_mesh_gpu_instancing"};class gy{constructor(e){this.parser=e,this.name=st.KHR_LIGHTS_PUNCTUAL,this.cache={refs:{},uses:{}}}_markDefs(){const e=this.parser,t=this.parser.json.nodes||[];for(let n=0,s=t.length;n<s;n++){const r=t[n];r.extensions&&r.extensions[this.name]&&r.extensions[this.name].light!==void 0&&e._addNodeRef(this.cache,r.extensions[this.name].light)}}_loadLight(e){const t=this.parser,n="light:"+e;let s=t.cache.get(n);if(s)return s;const r=t.json,c=((r.extensions&&r.extensions[this.name]||{}).lights||[])[e];let l;const u=new Ve(16777215);c.color!==void 0&&u.setRGB(c.color[0],c.color[1],c.color[2],en);const f=c.range!==void 0?c.range:0;switch(c.type){case"directional":l=new qv(u),l.target.position.set(0,0,-1),l.add(l.target);break;case"point":l=new Wv(u),l.distance=f;break;case"spot":l=new Vv(u),l.distance=f,c.spot=c.spot||{},c.spot.innerConeAngle=c.spot.innerConeAngle!==void 0?c.spot.innerConeAngle:0,c.spot.outerConeAngle=c.spot.outerConeAngle!==void 0?c.spot.outerConeAngle:Math.PI/4,l.angle=c.spot.outerConeAngle,l.penumbra=1-c.spot.innerConeAngle/c.spot.outerConeAngle,l.target.position.set(0,0,-1),l.add(l.target);break;default:throw new Error("THREE.GLTFLoader: Unexpected light type: "+c.type)}return l.position.set(0,0,0),l.decay=2,ii(l,c),c.intensity!==void 0&&(l.intensity=c.intensity),l.name=t.createUniqueName(c.name||"light_"+e),s=Promise.resolve(l),t.cache.add(n,s),s}getDependency(e,t){if(e==="light")return this._loadLight(t)}createNodeAttachment(e){const t=this,n=this.parser,r=n.json.nodes[e],a=(r.extensions&&r.extensions[this.name]||{}).light;return a===void 0?null:this._loadLight(a).then(function(c){return n._getNodeRef(t.cache,a,c)})}}class _y{constructor(){this.name=st.KHR_MATERIALS_UNLIT}getMaterialType(){return _n}extendParams(e,t,n){const s=[];e.color=new Ve(1,1,1),e.opacity=1;const r=t.pbrMetallicRoughness;if(r){if(Array.isArray(r.baseColorFactor)){const o=r.baseColorFactor;e.color.setRGB(o[0],o[1],o[2],en),e.opacity=o[3]}r.baseColorTexture!==void 0&&s.push(n.assignTexture(e,"map",r.baseColorTexture,Nt))}return Promise.all(s)}}class xy{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_EMISSIVE_STRENGTH}extendMaterialParams(e,t){const s=this.parser.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=s.extensions[this.name].emissiveStrength;return r!==void 0&&(t.emissiveIntensity=r),Promise.resolve()}}class vy{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_CLEARCOAT}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Xn}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];if(o.clearcoatFactor!==void 0&&(t.clearcoat=o.clearcoatFactor),o.clearcoatTexture!==void 0&&r.push(n.assignTexture(t,"clearcoatMap",o.clearcoatTexture)),o.clearcoatRoughnessFactor!==void 0&&(t.clearcoatRoughness=o.clearcoatRoughnessFactor),o.clearcoatRoughnessTexture!==void 0&&r.push(n.assignTexture(t,"clearcoatRoughnessMap",o.clearcoatRoughnessTexture)),o.clearcoatNormalTexture!==void 0&&(r.push(n.assignTexture(t,"clearcoatNormalMap",o.clearcoatNormalTexture)),o.clearcoatNormalTexture.scale!==void 0)){const a=o.clearcoatNormalTexture.scale;t.clearcoatNormalScale=new ie(a,a)}return Promise.all(r)}}class yy{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_DISPERSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Xn}extendMaterialParams(e,t){const s=this.parser.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=s.extensions[this.name];return t.dispersion=r.dispersion!==void 0?r.dispersion:0,Promise.resolve()}}class My{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_IRIDESCENCE}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Xn}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return o.iridescenceFactor!==void 0&&(t.iridescence=o.iridescenceFactor),o.iridescenceTexture!==void 0&&r.push(n.assignTexture(t,"iridescenceMap",o.iridescenceTexture)),o.iridescenceIor!==void 0&&(t.iridescenceIOR=o.iridescenceIor),t.iridescenceThicknessRange===void 0&&(t.iridescenceThicknessRange=[100,400]),o.iridescenceThicknessMinimum!==void 0&&(t.iridescenceThicknessRange[0]=o.iridescenceThicknessMinimum),o.iridescenceThicknessMaximum!==void 0&&(t.iridescenceThicknessRange[1]=o.iridescenceThicknessMaximum),o.iridescenceThicknessTexture!==void 0&&r.push(n.assignTexture(t,"iridescenceThicknessMap",o.iridescenceThicknessTexture)),Promise.all(r)}}class Sy{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_SHEEN}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Xn}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[];t.sheenColor=new Ve(0,0,0),t.sheenRoughness=0,t.sheen=1;const o=s.extensions[this.name];if(o.sheenColorFactor!==void 0){const a=o.sheenColorFactor;t.sheenColor.setRGB(a[0],a[1],a[2],en)}return o.sheenRoughnessFactor!==void 0&&(t.sheenRoughness=o.sheenRoughnessFactor),o.sheenColorTexture!==void 0&&r.push(n.assignTexture(t,"sheenColorMap",o.sheenColorTexture,Nt)),o.sheenRoughnessTexture!==void 0&&r.push(n.assignTexture(t,"sheenRoughnessMap",o.sheenRoughnessTexture)),Promise.all(r)}}class Ey{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_TRANSMISSION}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Xn}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return o.transmissionFactor!==void 0&&(t.transmission=o.transmissionFactor),o.transmissionTexture!==void 0&&r.push(n.assignTexture(t,"transmissionMap",o.transmissionTexture)),Promise.all(r)}}class by{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_VOLUME}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Xn}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];t.thickness=o.thicknessFactor!==void 0?o.thicknessFactor:0,o.thicknessTexture!==void 0&&r.push(n.assignTexture(t,"thicknessMap",o.thicknessTexture)),t.attenuationDistance=o.attenuationDistance||1/0;const a=o.attenuationColor||[1,1,1];return t.attenuationColor=new Ve().setRGB(a[0],a[1],a[2],en),Promise.all(r)}}class wy{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_IOR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Xn}extendMaterialParams(e,t){const s=this.parser.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=s.extensions[this.name];return t.ior=r.ior!==void 0?r.ior:1.5,Promise.resolve()}}class Ty{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_SPECULAR}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Xn}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];t.specularIntensity=o.specularFactor!==void 0?o.specularFactor:1,o.specularTexture!==void 0&&r.push(n.assignTexture(t,"specularIntensityMap",o.specularTexture));const a=o.specularColorFactor||[1,1,1];return t.specularColor=new Ve().setRGB(a[0],a[1],a[2],en),o.specularColorTexture!==void 0&&r.push(n.assignTexture(t,"specularColorMap",o.specularColorTexture,Nt)),Promise.all(r)}}class Ay{constructor(e){this.parser=e,this.name=st.EXT_MATERIALS_BUMP}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Xn}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return t.bumpScale=o.bumpFactor!==void 0?o.bumpFactor:1,o.bumpTexture!==void 0&&r.push(n.assignTexture(t,"bumpMap",o.bumpTexture)),Promise.all(r)}}class Ry{constructor(e){this.parser=e,this.name=st.KHR_MATERIALS_ANISOTROPY}getMaterialType(e){const n=this.parser.json.materials[e];return!n.extensions||!n.extensions[this.name]?null:Xn}extendMaterialParams(e,t){const n=this.parser,s=n.json.materials[e];if(!s.extensions||!s.extensions[this.name])return Promise.resolve();const r=[],o=s.extensions[this.name];return o.anisotropyStrength!==void 0&&(t.anisotropy=o.anisotropyStrength),o.anisotropyRotation!==void 0&&(t.anisotropyRotation=o.anisotropyRotation),o.anisotropyTexture!==void 0&&r.push(n.assignTexture(t,"anisotropyMap",o.anisotropyTexture)),Promise.all(r)}}class Cy{constructor(e){this.parser=e,this.name=st.KHR_TEXTURE_BASISU}loadTexture(e){const t=this.parser,n=t.json,s=n.textures[e];if(!s.extensions||!s.extensions[this.name])return null;const r=s.extensions[this.name],o=t.options.ktx2Loader;if(!o){if(n.extensionsRequired&&n.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setKTX2Loader must be called before loading KTX2 textures");return null}return t.loadTextureImage(e,r.source,o)}}class Py{constructor(e){this.parser=e,this.name=st.EXT_TEXTURE_WEBP,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,s=n.json,r=s.textures[e];if(!r.extensions||!r.extensions[t])return null;const o=r.extensions[t],a=s.images[o.source];let c=n.textureLoader;if(a.uri){const l=n.options.manager.getHandler(a.uri);l!==null&&(c=l)}return this.detectSupport().then(function(l){if(l)return n.loadTextureImage(e,o.source,c);if(s.extensionsRequired&&s.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: WebP required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/webp;base64,UklGRiIAAABXRUJQVlA4IBYAAAAwAQCdASoBAAEADsD+JaQAA3AAAAAA",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class Ly{constructor(e){this.parser=e,this.name=st.EXT_TEXTURE_AVIF,this.isSupported=null}loadTexture(e){const t=this.name,n=this.parser,s=n.json,r=s.textures[e];if(!r.extensions||!r.extensions[t])return null;const o=r.extensions[t],a=s.images[o.source];let c=n.textureLoader;if(a.uri){const l=n.options.manager.getHandler(a.uri);l!==null&&(c=l)}return this.detectSupport().then(function(l){if(l)return n.loadTextureImage(e,o.source,c);if(s.extensionsRequired&&s.extensionsRequired.indexOf(t)>=0)throw new Error("THREE.GLTFLoader: AVIF required by asset but unsupported.");return n.loadTexture(e)})}detectSupport(){return this.isSupported||(this.isSupported=new Promise(function(e){const t=new Image;t.src="data:image/avif;base64,AAAAIGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZk1BMUIAAADybWV0YQAAAAAAAAAoaGRscgAAAAAAAAAAcGljdAAAAAAAAAAAAAAAAGxpYmF2aWYAAAAADnBpdG0AAAAAAAEAAAAeaWxvYwAAAABEAAABAAEAAAABAAABGgAAABcAAAAoaWluZgAAAAAAAQAAABppbmZlAgAAAAABAABhdjAxQ29sb3IAAAAAamlwcnAAAABLaXBjbwAAABRpc3BlAAAAAAAAAAEAAAABAAAAEHBpeGkAAAAAAwgICAAAAAxhdjFDgQAMAAAAABNjb2xybmNseAACAAIABoAAAAAXaXBtYQAAAAAAAAABAAEEAQKDBAAAAB9tZGF0EgAKCBgABogQEDQgMgkQAAAAB8dSLfI=",t.onload=t.onerror=function(){e(t.height===1)}})),this.isSupported}}class Iy{constructor(e){this.name=st.EXT_MESHOPT_COMPRESSION,this.parser=e}loadBufferView(e){const t=this.parser.json,n=t.bufferViews[e];if(n.extensions&&n.extensions[this.name]){const s=n.extensions[this.name],r=this.parser.getDependency("buffer",s.buffer),o=this.parser.options.meshoptDecoder;if(!o||!o.supported){if(t.extensionsRequired&&t.extensionsRequired.indexOf(this.name)>=0)throw new Error("THREE.GLTFLoader: setMeshoptDecoder must be called before loading compressed files");return null}return r.then(function(a){const c=s.byteOffset||0,l=s.byteLength||0,u=s.count,f=s.byteStride,h=new Uint8Array(a,c,l);return o.decodeGltfBufferAsync?o.decodeGltfBufferAsync(u,f,h,s.mode,s.filter).then(function(d){return d.buffer}):o.ready.then(function(){const d=new ArrayBuffer(u*f);return o.decodeGltfBuffer(new Uint8Array(d),u,f,h,s.mode,s.filter),d})})}else return null}}class Dy{constructor(e){this.name=st.EXT_MESH_GPU_INSTANCING,this.parser=e}createNodeMesh(e){const t=this.parser.json,n=t.nodes[e];if(!n.extensions||!n.extensions[this.name]||n.mesh===void 0)return null;const s=t.meshes[n.mesh];for(const l of s.primitives)if(l.mode!==Sn.TRIANGLES&&l.mode!==Sn.TRIANGLE_STRIP&&l.mode!==Sn.TRIANGLE_FAN&&l.mode!==void 0)return null;const o=n.extensions[this.name].attributes,a=[],c={};for(const l in o)a.push(this.parser.getDependency("accessor",o[l]).then(u=>(c[l]=u,c[l])));return a.length<1?null:(a.push(this.parser.createNodeMesh(e)),Promise.all(a).then(l=>{const u=l.pop(),f=u.isGroup?u.children:[u],h=l[0].count,d=[];for(const m of f){const _=new De,g=new b,p=new On,M=new b(1,1,1),v=new qx(m.geometry,m.material,h);for(let x=0;x<h;x++)c.TRANSLATION&&g.fromBufferAttribute(c.TRANSLATION,x),c.ROTATION&&p.fromBufferAttribute(c.ROTATION,x),c.SCALE&&M.fromBufferAttribute(c.SCALE,x),v.setMatrixAt(x,_.compose(g,p,M));for(const x in c)if(x==="_COLOR_0"){const L=c[x];v.instanceColor=new el(L.array,L.itemSize,L.normalized)}else x!=="TRANSLATION"&&x!=="ROTATION"&&x!=="SCALE"&&m.geometry.setAttribute(x,c[x]);At.prototype.copy.call(v,m),this.parser.assignFinalMaterial(v),d.push(v)}return u.isGroup?(u.clear(),u.add(...d),u):d[0]}))}}const Uf="glTF",fr=12,Mh={JSON:1313821514,BIN:5130562};class Ny{constructor(e){this.name=st.KHR_BINARY_GLTF,this.content=null,this.body=null;const t=new DataView(e,0,fr),n=new TextDecoder;if(this.header={magic:n.decode(new Uint8Array(e.slice(0,4))),version:t.getUint32(4,!0),length:t.getUint32(8,!0)},this.header.magic!==Uf)throw new Error("THREE.GLTFLoader: Unsupported glTF-Binary header.");if(this.header.version<2)throw new Error("THREE.GLTFLoader: Legacy binary file detected.");const s=this.header.length-fr,r=new DataView(e,fr);let o=0;for(;o<s;){const a=r.getUint32(o,!0);o+=4;const c=r.getUint32(o,!0);if(o+=4,c===Mh.JSON){const l=new Uint8Array(e,fr+o,a);this.content=n.decode(l)}else if(c===Mh.BIN){const l=fr+o;this.body=e.slice(l,l+a)}o+=a}if(this.content===null)throw new Error("THREE.GLTFLoader: JSON content not found.")}}class Uy{constructor(e,t){if(!t)throw new Error("THREE.GLTFLoader: No DRACOLoader instance provided.");this.name=st.KHR_DRACO_MESH_COMPRESSION,this.json=e,this.dracoLoader=t,this.dracoLoader.preload()}decodePrimitive(e,t){const n=this.json,s=this.dracoLoader,r=e.extensions[this.name].bufferView,o=e.extensions[this.name].attributes,a={},c={},l={};for(const u in o){const f=ol[u]||u.toLowerCase();a[f]=o[u]}for(const u in e.attributes){const f=ol[u]||u.toLowerCase();if(o[u]!==void 0){const h=n.accessors[e.attributes[u]],d=Os[h.componentType];l[f]=d.name,c[f]=h.normalized===!0}}return t.getDependency("bufferView",r).then(function(u){return new Promise(function(f,h){s.decodeDracoFile(u,function(d){for(const m in d.attributes){const _=d.attributes[m],g=c[m];g!==void 0&&(_.normalized=g)}f(d)},a,l,en,h)})})}}class Oy{constructor(){this.name=st.KHR_TEXTURE_TRANSFORM}extendTexture(e,t){return(t.texCoord===void 0||t.texCoord===e.channel)&&t.offset===void 0&&t.rotation===void 0&&t.scale===void 0||(e=e.clone(),t.texCoord!==void 0&&(e.channel=t.texCoord),t.offset!==void 0&&e.offset.fromArray(t.offset),t.rotation!==void 0&&(e.rotation=t.rotation),t.scale!==void 0&&e.repeat.fromArray(t.scale),e.needsUpdate=!0),e}}class Fy{constructor(){this.name=st.KHR_MESH_QUANTIZATION}}class Of extends Ur{constructor(e,t,n,s){super(e,t,n,s)}copySampleValue_(e){const t=this.resultBuffer,n=this.sampleValues,s=this.valueSize,r=e*s*3+s;for(let o=0;o!==s;o++)t[o]=n[r+o];return t}interpolate_(e,t,n,s){const r=this.resultBuffer,o=this.sampleValues,a=this.valueSize,c=a*2,l=a*3,u=s-t,f=(n-t)/u,h=f*f,d=h*f,m=e*l,_=m-l,g=-2*d+3*h,p=d-h,M=1-g,v=p-h+f;for(let x=0;x!==a;x++){const L=o[_+x+a],T=o[_+x+c]*u,R=o[m+x+a],I=o[m+x]*u;r[x]=M*L+v*T+g*R+p*I}return r}}const By=new On;class ky extends Of{interpolate_(e,t,n,s){const r=super.interpolate_(e,t,n,s);return By.fromArray(r).normalize().toArray(r),r}}const Sn={POINTS:0,LINES:1,LINE_LOOP:2,LINE_STRIP:3,TRIANGLES:4,TRIANGLE_STRIP:5,TRIANGLE_FAN:6},Os={5120:Int8Array,5121:Uint8Array,5122:Int16Array,5123:Uint16Array,5125:Uint32Array,5126:Float32Array},Sh={9728:rn,9729:gn,9984:qh,9985:Ao,9986:xr,9987:oi},Eh={33071:Ai,33648:Fo,10497:zs},Ka={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT2:4,MAT3:9,MAT4:16},ol={POSITION:"position",NORMAL:"normal",TANGENT:"tangent",TEXCOORD_0:"uv",TEXCOORD_1:"uv1",TEXCOORD_2:"uv2",TEXCOORD_3:"uv3",COLOR_0:"color",WEIGHTS_0:"skinWeight",JOINTS_0:"skinIndex"},Ei={scale:"scale",translation:"position",rotation:"quaternion",weights:"morphTargetInfluences"},zy={CUBICSPLINE:void 0,LINEAR:Rr,STEP:Ar},Za={OPAQUE:"OPAQUE",MASK:"MASK",BLEND:"BLEND"};function Hy(i){return i.DefaultMaterial===void 0&&(i.DefaultMaterial=new Il({color:16777215,emissive:0,metalness:1,roughness:1,transparent:!1,depthTest:!0,side:ui})),i.DefaultMaterial}function ji(i,e,t){for(const n in t.extensions)i[n]===void 0&&(e.userData.gltfExtensions=e.userData.gltfExtensions||{},e.userData.gltfExtensions[n]=t.extensions[n])}function ii(i,e){e.extras!==void 0&&(typeof e.extras=="object"?Object.assign(i.userData,e.extras):console.warn("THREE.GLTFLoader: Ignoring primitive type .extras, "+e.extras))}function Vy(i,e,t){let n=!1,s=!1,r=!1;for(let l=0,u=e.length;l<u;l++){const f=e[l];if(f.POSITION!==void 0&&(n=!0),f.NORMAL!==void 0&&(s=!0),f.COLOR_0!==void 0&&(r=!0),n&&s&&r)break}if(!n&&!s&&!r)return Promise.resolve(i);const o=[],a=[],c=[];for(let l=0,u=e.length;l<u;l++){const f=e[l];if(n){const h=f.POSITION!==void 0?t.getDependency("accessor",f.POSITION):i.attributes.position;o.push(h)}if(s){const h=f.NORMAL!==void 0?t.getDependency("accessor",f.NORMAL):i.attributes.normal;a.push(h)}if(r){const h=f.COLOR_0!==void 0?t.getDependency("accessor",f.COLOR_0):i.attributes.color;c.push(h)}}return Promise.all([Promise.all(o),Promise.all(a),Promise.all(c)]).then(function(l){const u=l[0],f=l[1],h=l[2];return n&&(i.morphAttributes.position=u),s&&(i.morphAttributes.normal=f),r&&(i.morphAttributes.color=h),i.morphTargetsRelative=!0,i})}function Gy(i,e){if(i.updateMorphTargets(),e.weights!==void 0)for(let t=0,n=e.weights.length;t<n;t++)i.morphTargetInfluences[t]=e.weights[t];if(e.extras&&Array.isArray(e.extras.targetNames)){const t=e.extras.targetNames;if(i.morphTargetInfluences.length===t.length){i.morphTargetDictionary={};for(let n=0,s=t.length;n<s;n++)i.morphTargetDictionary[t[n]]=n}else console.warn("THREE.GLTFLoader: Invalid extras.targetNames length. Ignoring names.")}}function Wy(i){let e;const t=i.extensions&&i.extensions[st.KHR_DRACO_MESH_COMPRESSION];if(t?e="draco:"+t.bufferView+":"+t.indices+":"+Ja(t.attributes):e=i.indices+":"+Ja(i.attributes)+":"+i.mode,i.targets!==void 0)for(let n=0,s=i.targets.length;n<s;n++)e+=":"+Ja(i.targets[n]);return e}function Ja(i){let e="";const t=Object.keys(i).sort();for(let n=0,s=t.length;n<s;n++)e+=t[n]+":"+i[t[n]]+";";return e}function al(i){switch(i){case Int8Array:return 1/127;case Uint8Array:return 1/255;case Int16Array:return 1/32767;case Uint16Array:return 1/65535;default:throw new Error("THREE.GLTFLoader: Unsupported normalized accessor component type.")}}function Xy(i){return i.search(/\.jpe?g($|\?)/i)>0||i.search(/^data\:image\/jpeg/)===0?"image/jpeg":i.search(/\.webp($|\?)/i)>0||i.search(/^data\:image\/webp/)===0?"image/webp":i.search(/\.ktx2($|\?)/i)>0||i.search(/^data\:image\/ktx2/)===0?"image/ktx2":"image/png"}const qy=new De;class Yy{constructor(e={},t={}){this.json=e,this.extensions={},this.plugins={},this.options=t,this.cache=new my,this.associations=new Map,this.primitiveCache={},this.nodeCache={},this.meshCache={refs:{},uses:{}},this.cameraCache={refs:{},uses:{}},this.lightCache={refs:{},uses:{}},this.sourceCache={},this.textureCache={},this.nodeNamesUsed={};let n=!1,s=-1,r=!1,o=-1;if(typeof navigator<"u"){const a=navigator.userAgent;n=/^((?!chrome|android).)*safari/i.test(a)===!0;const c=a.match(/Version\/(\d+)/);s=n&&c?parseInt(c[1],10):-1,r=a.indexOf("Firefox")>-1,o=r?a.match(/Firefox\/([0-9]+)\./)[1]:-1}typeof createImageBitmap>"u"||n&&s<17||r&&o<98?this.textureLoader=new zv(this.options.manager):this.textureLoader=new Yv(this.options.manager),this.textureLoader.setCrossOrigin(this.options.crossOrigin),this.textureLoader.setRequestHeader(this.options.requestHeader),this.fileLoader=new Vo(this.options.manager),this.fileLoader.setResponseType("arraybuffer"),this.options.crossOrigin==="use-credentials"&&this.fileLoader.setWithCredentials(!0)}setExtensions(e){this.extensions=e}setPlugins(e){this.plugins=e}parse(e,t){const n=this,s=this.json,r=this.extensions;this.cache.removeAll(),this.nodeCache={},this._invokeAll(function(o){return o._markDefs&&o._markDefs()}),Promise.all(this._invokeAll(function(o){return o.beforeRoot&&o.beforeRoot()})).then(function(){return Promise.all([n.getDependencies("scene"),n.getDependencies("animation"),n.getDependencies("camera")])}).then(function(o){const a={scene:o[0][s.scene||0],scenes:o[0],animations:o[1],cameras:o[2],asset:s.asset,parser:n,userData:{}};return ji(r,a,s),ii(a,s),Promise.all(n._invokeAll(function(c){return c.afterRoot&&c.afterRoot(a)})).then(function(){for(const c of a.scenes)c.updateMatrixWorld();e(a)})}).catch(t)}_markDefs(){const e=this.json.nodes||[],t=this.json.skins||[],n=this.json.meshes||[];for(let s=0,r=t.length;s<r;s++){const o=t[s].joints;for(let a=0,c=o.length;a<c;a++)e[o[a]].isBone=!0}for(let s=0,r=e.length;s<r;s++){const o=e[s];o.mesh!==void 0&&(this._addNodeRef(this.meshCache,o.mesh),o.skin!==void 0&&(n[o.mesh].isSkinnedMesh=!0)),o.camera!==void 0&&this._addNodeRef(this.cameraCache,o.camera)}}_addNodeRef(e,t){t!==void 0&&(e.refs[t]===void 0&&(e.refs[t]=e.uses[t]=0),e.refs[t]++)}_getNodeRef(e,t,n){if(e.refs[t]<=1)return n;const s=n.clone(),r=(o,a)=>{const c=this.associations.get(o);c!=null&&this.associations.set(a,c);for(const[l,u]of o.children.entries())r(u,a.children[l])};return r(n,s),s.name+="_instance_"+e.uses[t]++,s}_invokeOne(e){const t=Object.values(this.plugins);t.push(this);for(let n=0;n<t.length;n++){const s=e(t[n]);if(s)return s}return null}_invokeAll(e){const t=Object.values(this.plugins);t.unshift(this);const n=[];for(let s=0;s<t.length;s++){const r=e(t[s]);r&&n.push(r)}return n}getDependency(e,t){const n=e+":"+t;let s=this.cache.get(n);if(!s){switch(e){case"scene":s=this.loadScene(t);break;case"node":s=this._invokeOne(function(r){return r.loadNode&&r.loadNode(t)});break;case"mesh":s=this._invokeOne(function(r){return r.loadMesh&&r.loadMesh(t)});break;case"accessor":s=this.loadAccessor(t);break;case"bufferView":s=this._invokeOne(function(r){return r.loadBufferView&&r.loadBufferView(t)});break;case"buffer":s=this.loadBuffer(t);break;case"material":s=this._invokeOne(function(r){return r.loadMaterial&&r.loadMaterial(t)});break;case"texture":s=this._invokeOne(function(r){return r.loadTexture&&r.loadTexture(t)});break;case"skin":s=this.loadSkin(t);break;case"animation":s=this._invokeOne(function(r){return r.loadAnimation&&r.loadAnimation(t)});break;case"camera":s=this.loadCamera(t);break;default:if(s=this._invokeOne(function(r){return r!=this&&r.getDependency&&r.getDependency(e,t)}),!s)throw new Error("Unknown type: "+e);break}this.cache.add(n,s)}return s}getDependencies(e){let t=this.cache.get(e);if(!t){const n=this,s=this.json[e+(e==="mesh"?"es":"s")]||[];t=Promise.all(s.map(function(r,o){return n.getDependency(e,o)})),this.cache.add(e,t)}return t}loadBuffer(e){const t=this.json.buffers[e],n=this.fileLoader;if(t.type&&t.type!=="arraybuffer")throw new Error("THREE.GLTFLoader: "+t.type+" buffer type is not supported.");if(t.uri===void 0&&e===0)return Promise.resolve(this.extensions[st.KHR_BINARY_GLTF].body);const s=this.options;return new Promise(function(r,o){n.load(br.resolveURL(t.uri,s.path),r,void 0,function(){o(new Error('THREE.GLTFLoader: Failed to load buffer "'+t.uri+'".'))})})}loadBufferView(e){const t=this.json.bufferViews[e];return this.getDependency("buffer",t.buffer).then(function(n){const s=t.byteLength||0,r=t.byteOffset||0;return n.slice(r,r+s)})}loadAccessor(e){const t=this,n=this.json,s=this.json.accessors[e];if(s.bufferView===void 0&&s.sparse===void 0){const o=Ka[s.type],a=Os[s.componentType],c=s.normalized===!0,l=new a(s.count*o);return Promise.resolve(new Xt(l,o,c))}const r=[];return s.bufferView!==void 0?r.push(this.getDependency("bufferView",s.bufferView)):r.push(null),s.sparse!==void 0&&(r.push(this.getDependency("bufferView",s.sparse.indices.bufferView)),r.push(this.getDependency("bufferView",s.sparse.values.bufferView))),Promise.all(r).then(function(o){const a=o[0],c=Ka[s.type],l=Os[s.componentType],u=l.BYTES_PER_ELEMENT,f=u*c,h=s.byteOffset||0,d=s.bufferView!==void 0?n.bufferViews[s.bufferView].byteStride:void 0,m=s.normalized===!0;let _,g;if(d&&d!==f){const p=Math.floor(h/d),M="InterleavedBuffer:"+s.bufferView+":"+s.componentType+":"+p+":"+s.count;let v=t.cache.get(M);v||(_=new l(a,p*d,s.count*d/u),v=new Vx(_,d/u),t.cache.add(M,v)),g=new wl(v,c,h%d/u,m)}else a===null?_=new l(s.count*c):_=new l(a,h,s.count*c),g=new Xt(_,c,m);if(s.sparse!==void 0){const p=Ka.SCALAR,M=Os[s.sparse.indices.componentType],v=s.sparse.indices.byteOffset||0,x=s.sparse.values.byteOffset||0,L=new M(o[1],v,s.sparse.count*p),T=new l(o[2],x,s.sparse.count*c);a!==null&&(g=new Xt(g.array.slice(),g.itemSize,g.normalized)),g.normalized=!1;for(let R=0,I=L.length;R<I;R++){const w=L[R];if(g.setX(w,T[R*c]),c>=2&&g.setY(w,T[R*c+1]),c>=3&&g.setZ(w,T[R*c+2]),c>=4&&g.setW(w,T[R*c+3]),c>=5)throw new Error("THREE.GLTFLoader: Unsupported itemSize in sparse BufferAttribute.")}g.normalized=m}return g})}loadTexture(e){const t=this.json,n=this.options,r=t.textures[e].source,o=t.images[r];let a=this.textureLoader;if(o.uri){const c=n.manager.getHandler(o.uri);c!==null&&(a=c)}return this.loadTextureImage(e,r,a)}loadTextureImage(e,t,n){const s=this,r=this.json,o=r.textures[e],a=r.images[t],c=(a.uri||a.bufferView)+":"+o.sampler;if(this.textureCache[c])return this.textureCache[c];const l=this.loadImageSource(t,n).then(function(u){u.flipY=!1,u.name=o.name||a.name||"",u.name===""&&typeof a.uri=="string"&&a.uri.startsWith("data:image/")===!1&&(u.name=a.uri);const h=(r.samplers||{})[o.sampler]||{};return u.magFilter=Sh[h.magFilter]||gn,u.minFilter=Sh[h.minFilter]||oi,u.wrapS=Eh[h.wrapS]||zs,u.wrapT=Eh[h.wrapT]||zs,u.generateMipmaps=!u.isCompressedTexture&&u.minFilter!==rn&&u.minFilter!==gn,s.associations.set(u,{textures:e}),u}).catch(function(){return null});return this.textureCache[c]=l,l}loadImageSource(e,t){const n=this,s=this.json,r=this.options;if(this.sourceCache[e]!==void 0)return this.sourceCache[e].then(f=>f.clone());const o=s.images[e],a=self.URL||self.webkitURL;let c=o.uri||"",l=!1;if(o.bufferView!==void 0)c=n.getDependency("bufferView",o.bufferView).then(function(f){l=!0;const h=new Blob([f],{type:o.mimeType});return c=a.createObjectURL(h),c});else if(o.uri===void 0)throw new Error("THREE.GLTFLoader: Image "+e+" is missing URI and bufferView");const u=Promise.resolve(c).then(function(f){return new Promise(function(h,d){let m=h;t.isImageBitmapLoader===!0&&(m=function(_){const g=new Wt(_);g.needsUpdate=!0,h(g)}),t.load(br.resolveURL(f,r.path),m,void 0,d)})}).then(function(f){return l===!0&&a.revokeObjectURL(c),ii(f,o),f.userData.mimeType=o.mimeType||Xy(o.uri),f}).catch(function(f){throw console.error("THREE.GLTFLoader: Couldn't load texture",c),f});return this.sourceCache[e]=u,u}assignTexture(e,t,n,s){const r=this;return this.getDependency("texture",n.index).then(function(o){if(!o)return null;if(n.texCoord!==void 0&&n.texCoord>0&&(o=o.clone(),o.channel=n.texCoord),r.extensions[st.KHR_TEXTURE_TRANSFORM]){const a=n.extensions!==void 0?n.extensions[st.KHR_TEXTURE_TRANSFORM]:void 0;if(a){const c=r.associations.get(o);o=r.extensions[st.KHR_TEXTURE_TRANSFORM].extendTexture(o,a),r.associations.set(o,c)}}return s!==void 0&&(o.colorSpace=s),e[t]=o,o})}assignFinalMaterial(e){const t=e.geometry;let n=e.material;const s=t.attributes.tangent===void 0,r=t.attributes.color!==void 0,o=t.attributes.normal===void 0;if(e.isPoints){const a="PointsMaterial:"+n.uuid;let c=this.cache.get(a);c||(c=new bf,Hn.prototype.copy.call(c,n),c.color.copy(n.color),c.map=n.map,c.sizeAttenuation=!1,this.cache.add(a,c)),n=c}else if(e.isLine){const a="LineBasicMaterial:"+n.uuid;let c=this.cache.get(a);c||(c=new ns,Hn.prototype.copy.call(c,n),c.color.copy(n.color),c.map=n.map,this.cache.add(a,c)),n=c}if(s||r||o){let a="ClonedMaterial:"+n.uuid+":";s&&(a+="derivative-tangents:"),r&&(a+="vertex-colors:"),o&&(a+="flat-shading:");let c=this.cache.get(a);c||(c=n.clone(),r&&(c.vertexColors=!0),o&&(c.flatShading=!0),s&&(c.normalScale&&(c.normalScale.y*=-1),c.clearcoatNormalScale&&(c.clearcoatNormalScale.y*=-1)),this.cache.add(a,c),this.associations.set(c,this.associations.get(n))),n=c}e.material=n}getMaterialType(){return Il}loadMaterial(e){const t=this,n=this.json,s=this.extensions,r=n.materials[e];let o;const a={},c=r.extensions||{},l=[];if(c[st.KHR_MATERIALS_UNLIT]){const f=s[st.KHR_MATERIALS_UNLIT];o=f.getMaterialType(),l.push(f.extendParams(a,r,t))}else{const f=r.pbrMetallicRoughness||{};if(a.color=new Ve(1,1,1),a.opacity=1,Array.isArray(f.baseColorFactor)){const h=f.baseColorFactor;a.color.setRGB(h[0],h[1],h[2],en),a.opacity=h[3]}f.baseColorTexture!==void 0&&l.push(t.assignTexture(a,"map",f.baseColorTexture,Nt)),a.metalness=f.metallicFactor!==void 0?f.metallicFactor:1,a.roughness=f.roughnessFactor!==void 0?f.roughnessFactor:1,f.metallicRoughnessTexture!==void 0&&(l.push(t.assignTexture(a,"metalnessMap",f.metallicRoughnessTexture)),l.push(t.assignTexture(a,"roughnessMap",f.metallicRoughnessTexture))),o=this._invokeOne(function(h){return h.getMaterialType&&h.getMaterialType(e)}),l.push(Promise.all(this._invokeAll(function(h){return h.extendMaterialParams&&h.extendMaterialParams(e,a)})))}r.doubleSided===!0&&(a.side=mn);const u=r.alphaMode||Za.OPAQUE;if(u===Za.BLEND?(a.transparent=!0,a.depthWrite=!1):(a.transparent=!1,u===Za.MASK&&(a.alphaTest=r.alphaCutoff!==void 0?r.alphaCutoff:.5)),r.normalTexture!==void 0&&o!==_n&&(l.push(t.assignTexture(a,"normalMap",r.normalTexture)),a.normalScale=new ie(1,1),r.normalTexture.scale!==void 0)){const f=r.normalTexture.scale;a.normalScale.set(f,f)}if(r.occlusionTexture!==void 0&&o!==_n&&(l.push(t.assignTexture(a,"aoMap",r.occlusionTexture)),r.occlusionTexture.strength!==void 0&&(a.aoMapIntensity=r.occlusionTexture.strength)),r.emissiveFactor!==void 0&&o!==_n){const f=r.emissiveFactor;a.emissive=new Ve().setRGB(f[0],f[1],f[2],en)}return r.emissiveTexture!==void 0&&o!==_n&&l.push(t.assignTexture(a,"emissiveMap",r.emissiveTexture,Nt)),Promise.all(l).then(function(){const f=new o(a);return r.name&&(f.name=r.name),ii(f,r),t.associations.set(f,{materials:e}),r.extensions&&ji(s,f,r),f})}createUniqueName(e){const t=xt.sanitizeNodeName(e||"");return t in this.nodeNamesUsed?t+"_"+ ++this.nodeNamesUsed[t]:(this.nodeNamesUsed[t]=0,t)}loadGeometries(e){const t=this,n=this.extensions,s=this.primitiveCache;function r(a){return n[st.KHR_DRACO_MESH_COMPRESSION].decodePrimitive(a,t).then(function(c){return bh(c,a,t)})}const o=[];for(let a=0,c=e.length;a<c;a++){const l=e[a],u=Wy(l),f=s[u];if(f)o.push(f.promise);else{let h;l.extensions&&l.extensions[st.KHR_DRACO_MESH_COMPRESSION]?h=r(l):h=bh(new Ft,l,t),s[u]={primitive:l,promise:h},o.push(h)}}return Promise.all(o)}loadMesh(e){const t=this,n=this.json,s=this.extensions,r=n.meshes[e],o=r.primitives,a=[];for(let c=0,l=o.length;c<l;c++){const u=o[c].material===void 0?Hy(this.cache):this.getDependency("material",o[c].material);a.push(u)}return a.push(t.loadGeometries(o)),Promise.all(a).then(function(c){const l=c.slice(0,c.length-1),u=c[c.length-1],f=[];for(let d=0,m=u.length;d<m;d++){const _=u[d],g=o[d];let p;const M=l[d];if(g.mode===Sn.TRIANGLES||g.mode===Sn.TRIANGLE_STRIP||g.mode===Sn.TRIANGLE_FAN||g.mode===void 0)p=r.isSkinnedMesh===!0?new Tl(_,M):new Gt(_,M),p.isSkinnedMesh===!0&&p.normalizeSkinWeights(),g.mode===Sn.TRIANGLE_STRIP?p.geometry=yh(p.geometry,nf):g.mode===Sn.TRIANGLE_FAN&&(p.geometry=yh(p.geometry,Zc));else if(g.mode===Sn.LINES)p=new Nr(_,M);else if(g.mode===Sn.LINE_STRIP)p=new Rl(_,M);else if(g.mode===Sn.LINE_LOOP)p=new Ef(_,M);else if(g.mode===Sn.POINTS)p=new Yx(_,M);else throw new Error("THREE.GLTFLoader: Primitive mode unsupported: "+g.mode);Object.keys(p.geometry.morphAttributes).length>0&&Gy(p,r),p.name=t.createUniqueName(r.name||"mesh_"+e),ii(p,r),g.extensions&&ji(s,p,g),t.assignFinalMaterial(p),f.push(p)}for(let d=0,m=f.length;d<m;d++)t.associations.set(f[d],{meshes:e,primitives:d});if(f.length===1)return r.extensions&&ji(s,f[0],r),f[0];const h=new un;r.extensions&&ji(s,h,r),t.associations.set(h,{meshes:e});for(let d=0,m=f.length;d<m;d++)h.add(f[d]);return h})}loadCamera(e){let t;const n=this.json.cameras[e],s=n[n.type];if(!s){console.warn("THREE.GLTFLoader: Missing camera parameters.");return}return n.type==="perspective"?t=new ln(ci.radToDeg(s.yfov),s.aspectRatio||1,s.znear||1,s.zfar||2e6):n.type==="orthographic"&&(t=new Zo(-s.xmag,s.xmag,s.ymag,-s.ymag,s.znear,s.zfar)),n.name&&(t.name=this.createUniqueName(n.name)),ii(t,n),Promise.resolve(t)}loadSkin(e){const t=this.json.skins[e],n=[];for(let s=0,r=t.joints.length;s<r;s++)n.push(this._loadNodeShallow(t.joints[s]));return t.inverseBindMatrices!==void 0?n.push(this.getDependency("accessor",t.inverseBindMatrices)):n.push(null),Promise.all(n).then(function(s){const r=s.pop(),o=s,a=[],c=[];for(let l=0,u=o.length;l<u;l++){const f=o[l];if(f){a.push(f);const h=new De;r!==null&&h.fromArray(r.array,l*16),c.push(h)}else console.warn('THREE.GLTFLoader: Joint "%s" could not be found.',t.joints[l])}return new Al(a,c)})}loadAnimation(e){const t=this.json,n=this,s=t.animations[e],r=s.name?s.name:"animation_"+e,o=[],a=[],c=[],l=[],u=[];for(let f=0,h=s.channels.length;f<h;f++){const d=s.channels[f],m=s.samplers[d.sampler],_=d.target,g=_.node,p=s.parameters!==void 0?s.parameters[m.input]:m.input,M=s.parameters!==void 0?s.parameters[m.output]:m.output;_.node!==void 0&&(o.push(this.getDependency("node",g)),a.push(this.getDependency("accessor",p)),c.push(this.getDependency("accessor",M)),l.push(m),u.push(_))}return Promise.all([Promise.all(o),Promise.all(a),Promise.all(c),Promise.all(l),Promise.all(u)]).then(function(f){const h=f[0],d=f[1],m=f[2],_=f[3],g=f[4],p=[];for(let M=0,v=h.length;M<v;M++){const x=h[M],L=d[M],T=m[M],R=_[M],I=g[M];if(x===void 0)continue;x.updateMatrix&&x.updateMatrix();const w=n._createAnimationTracks(x,L,T,R,I);if(w)for(let S=0;S<w.length;S++)p.push(w[S])}return new Dv(r,void 0,p)})}createNodeMesh(e){const t=this.json,n=this,s=t.nodes[e];return s.mesh===void 0?null:n.getDependency("mesh",s.mesh).then(function(r){const o=n._getNodeRef(n.meshCache,s.mesh,r);return s.weights!==void 0&&o.traverse(function(a){if(a.isMesh)for(let c=0,l=s.weights.length;c<l;c++)a.morphTargetInfluences[c]=s.weights[c]}),o})}loadNode(e){const t=this.json,n=this,s=t.nodes[e],r=n._loadNodeShallow(e),o=[],a=s.children||[];for(let l=0,u=a.length;l<u;l++)o.push(n.getDependency("node",a[l]));const c=s.skin===void 0?Promise.resolve(null):n.getDependency("skin",s.skin);return Promise.all([r,Promise.all(o),c]).then(function(l){const u=l[0],f=l[1],h=l[2];h!==null&&u.traverse(function(d){d.isSkinnedMesh&&d.bind(h,qy)});for(let d=0,m=f.length;d<m;d++)u.add(f[d]);return u})}_loadNodeShallow(e){const t=this.json,n=this.extensions,s=this;if(this.nodeCache[e]!==void 0)return this.nodeCache[e];const r=t.nodes[e],o=r.name?s.createUniqueName(r.name):"",a=[],c=s._invokeOne(function(l){return l.createNodeMesh&&l.createNodeMesh(e)});return c&&a.push(c),r.camera!==void 0&&a.push(s.getDependency("camera",r.camera).then(function(l){return s._getNodeRef(s.cameraCache,r.camera,l)})),s._invokeAll(function(l){return l.createNodeAttachment&&l.createNodeAttachment(e)}).forEach(function(l){a.push(l)}),this.nodeCache[e]=Promise.all(a).then(function(l){let u;if(r.isBone===!0?u=new Mf:l.length>1?u=new un:l.length===1?u=l[0]:u=new At,u!==l[0])for(let f=0,h=l.length;f<h;f++)u.add(l[f]);if(r.name&&(u.userData.name=r.name,u.name=o),ii(u,r),r.extensions&&ji(n,u,r),r.matrix!==void 0){const f=new De;f.fromArray(r.matrix),u.applyMatrix4(f)}else r.translation!==void 0&&u.position.fromArray(r.translation),r.rotation!==void 0&&u.quaternion.fromArray(r.rotation),r.scale!==void 0&&u.scale.fromArray(r.scale);return s.associations.has(u)||s.associations.set(u,{}),s.associations.get(u).nodes=e,u}),this.nodeCache[e]}loadScene(e){const t=this.extensions,n=this.json.scenes[e],s=this,r=new un;n.name&&(r.name=s.createUniqueName(n.name)),ii(r,n),n.extensions&&ji(t,r,n);const o=n.nodes||[],a=[];for(let c=0,l=o.length;c<l;c++)a.push(s.getDependency("node",o[c]));return Promise.all(a).then(function(c){for(let u=0,f=c.length;u<f;u++)r.add(c[u]);const l=u=>{const f=new Map;for(const[h,d]of s.associations)(h instanceof Hn||h instanceof Wt)&&f.set(h,d);return u.traverse(h=>{const d=s.associations.get(h);d!=null&&f.set(h,d)}),f};return s.associations=l(r),r})}_createAnimationTracks(e,t,n,s,r){const o=[],a=e.name?e.name:e.uuid,c=[];Ei[r.path]===Ei.weights?e.traverse(function(h){h.morphTargetInfluences&&c.push(h.name?h.name:h.uuid)}):c.push(a);let l;switch(Ei[r.path]){case Ei.weights:l=Xs;break;case Ei.rotation:l=qs;break;case Ei.position:case Ei.scale:l=Ys;break;default:switch(n.itemSize){case 1:l=Xs;break;case 2:case 3:default:l=Ys;break}break}const u=s.interpolation!==void 0?zy[s.interpolation]:Rr,f=this._getArrayFromAccessor(n);for(let h=0,d=c.length;h<d;h++){const m=new l(c[h]+"."+Ei[r.path],t.array,f,u);s.interpolation==="CUBICSPLINE"&&this._createCubicSplineTrackInterpolant(m),o.push(m)}return o}_getArrayFromAccessor(e){let t=e.array;if(e.normalized){const n=al(t.constructor),s=new Float32Array(t.length);for(let r=0,o=t.length;r<o;r++)s[r]=t[r]*n;t=s}return t}_createCubicSplineTrackInterpolant(e){e.createInterpolant=function(n){const s=this instanceof qs?ky:Of;return new s(this.times,this.values,this.getValueSize()/3,n)},e.createInterpolant.isInterpolantFactoryMethodGLTFCubicSpline=!0}}function jy(i,e,t){const n=e.attributes,s=new on;if(n.POSITION!==void 0){const a=t.json.accessors[n.POSITION],c=a.min,l=a.max;if(c!==void 0&&l!==void 0){if(s.set(new b(c[0],c[1],c[2]),new b(l[0],l[1],l[2])),a.normalized){const u=al(Os[a.componentType]);s.min.multiplyScalar(u),s.max.multiplyScalar(u)}}else{console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.");return}}else return;const r=e.targets;if(r!==void 0){const a=new b,c=new b;for(let l=0,u=r.length;l<u;l++){const f=r[l];if(f.POSITION!==void 0){const h=t.json.accessors[f.POSITION],d=h.min,m=h.max;if(d!==void 0&&m!==void 0){if(c.setX(Math.max(Math.abs(d[0]),Math.abs(m[0]))),c.setY(Math.max(Math.abs(d[1]),Math.abs(m[1]))),c.setZ(Math.max(Math.abs(d[2]),Math.abs(m[2]))),h.normalized){const _=al(Os[h.componentType]);c.multiplyScalar(_)}a.max(c)}else console.warn("THREE.GLTFLoader: Missing min/max properties for accessor POSITION.")}}s.expandByVector(a)}i.boundingBox=s;const o=new Gn;s.getCenter(o.center),o.radius=s.min.distanceTo(s.max)/2,i.boundingSphere=o}function bh(i,e,t){const n=e.attributes,s=[];function r(o,a){return t.getDependency("accessor",o).then(function(c){i.setAttribute(a,c)})}for(const o in n){const a=ol[o]||o.toLowerCase();a in i.attributes||s.push(r(n[o],a))}if(e.indices!==void 0&&!i.index){const o=t.getDependency("accessor",e.indices).then(function(a){i.setIndex(a)});s.push(o)}return ot.workingColorSpace!==en&&"COLOR_0"in n&&console.warn(`THREE.GLTFLoader: Converting vertex colors from "srgb-linear" to "${ot.workingColorSpace}" not supported.`),ii(i,e),jy(i,e,t),Promise.all(s).then(function(){return e.targets!==void 0?Vy(i,e.targets,t):i})}const Qa=new WeakMap;class $y extends as{constructor(e){super(e),this.decoderPath="",this.decoderConfig={},this.decoderBinary=null,this.decoderPending=null,this.workerLimit=4,this.workerPool=[],this.workerNextTaskID=1,this.workerSourceURL="",this.defaultAttributeIDs={position:"POSITION",normal:"NORMAL",color:"COLOR",uv:"TEX_COORD"},this.defaultAttributeTypes={position:"Float32Array",normal:"Float32Array",color:"Float32Array",uv:"Float32Array"}}setDecoderPath(e){return this.decoderPath=e,this}setDecoderConfig(e){return this.decoderConfig=e,this}setWorkerLimit(e){return this.workerLimit=e,this}load(e,t,n,s){const r=new Vo(this.manager);r.setPath(this.path),r.setResponseType("arraybuffer"),r.setRequestHeader(this.requestHeader),r.setWithCredentials(this.withCredentials),r.load(e,o=>{this.parse(o,t,s)},n,s)}parse(e,t,n=()=>{}){this.decodeDracoFile(e,t,null,null,Nt,n).catch(n)}decodeDracoFile(e,t,n,s,r=en,o=()=>{}){const a={attributeIDs:n||this.defaultAttributeIDs,attributeTypes:s||this.defaultAttributeTypes,useUniqueIDs:!!n,vertexColorSpace:r};return this.decodeGeometry(e,a).then(t).catch(o)}decodeGeometry(e,t){const n=JSON.stringify(t);if(Qa.has(e)){const c=Qa.get(e);if(c.key===n)return c.promise;if(e.byteLength===0)throw new Error("THREE.DRACOLoader: Unable to re-decode a buffer with different settings. Buffer has already been transferred.")}let s;const r=this.workerNextTaskID++,o=e.byteLength,a=this._getWorker(r,o).then(c=>(s=c,new Promise((l,u)=>{s._callbacks[r]={resolve:l,reject:u},s.postMessage({type:"decode",id:r,taskConfig:t,buffer:e},[e])}))).then(c=>this._createGeometry(c.geometry));return a.catch(()=>!0).then(()=>{s&&r&&this._releaseTask(s,r)}),Qa.set(e,{key:n,promise:a}),a}_createGeometry(e){const t=new Ft;e.index&&t.setIndex(new Xt(e.index.array,1));for(let n=0;n<e.attributes.length;n++){const s=e.attributes[n],r=s.name,o=s.array,a=s.itemSize,c=new Xt(o,a);r==="color"&&(this._assignVertexColorSpace(c,s.vertexColorSpace),c.normalized=!(o instanceof Float32Array)),t.setAttribute(r,c)}return t}_assignVertexColorSpace(e,t){if(t!==Nt)return;const n=new Ve;for(let s=0,r=e.count;s<r;s++)n.fromBufferAttribute(e,s),ot.toWorkingColorSpace(n,Nt),e.setXYZ(s,n.r,n.g,n.b)}_loadLibrary(e,t){const n=new Vo(this.manager);return n.setPath(this.decoderPath),n.setResponseType(t),n.setWithCredentials(this.withCredentials),new Promise((s,r)=>{n.load(e,s,void 0,r)})}preload(){return this._initDecoder(),this}_initDecoder(){if(this.decoderPending)return this.decoderPending;const e=typeof WebAssembly!="object"||this.decoderConfig.type==="js",t=[];return e?t.push(this._loadLibrary("draco_decoder.js","text")):(t.push(this._loadLibrary("draco_wasm_wrapper.js","text")),t.push(this._loadLibrary("draco_decoder.wasm","arraybuffer"))),this.decoderPending=Promise.all(t).then(n=>{const s=n[0];e||(this.decoderConfig.wasmBinary=n[1]);const r=Ky.toString(),o=["/* draco decoder */",s,"","/* worker */",r.substring(r.indexOf("{")+1,r.lastIndexOf("}"))].join(`
`);this.workerSourceURL=URL.createObjectURL(new Blob([o]))}),this.decoderPending}_getWorker(e,t){return this._initDecoder().then(()=>{if(this.workerPool.length<this.workerLimit){const s=new Worker(this.workerSourceURL);s._callbacks={},s._taskCosts={},s._taskLoad=0,s.postMessage({type:"init",decoderConfig:this.decoderConfig}),s.onmessage=function(r){const o=r.data;switch(o.type){case"decode":s._callbacks[o.id].resolve(o);break;case"error":s._callbacks[o.id].reject(o);break;default:console.error('THREE.DRACOLoader: Unexpected message, "'+o.type+'"')}},this.workerPool.push(s)}else this.workerPool.sort(function(s,r){return s._taskLoad>r._taskLoad?-1:1});const n=this.workerPool[this.workerPool.length-1];return n._taskCosts[e]=t,n._taskLoad+=t,n})}_releaseTask(e,t){e._taskLoad-=e._taskCosts[t],delete e._callbacks[t],delete e._taskCosts[t]}debug(){console.log("Task load: ",this.workerPool.map(e=>e._taskLoad))}dispose(){for(let e=0;e<this.workerPool.length;++e)this.workerPool[e].terminate();return this.workerPool.length=0,this.workerSourceURL!==""&&URL.revokeObjectURL(this.workerSourceURL),this}}function Ky(){let i,e;onmessage=function(o){const a=o.data;switch(a.type){case"init":i=a.decoderConfig,e=new Promise(function(u){i.onModuleLoaded=function(f){u({draco:f})},DracoDecoderModule(i)});break;case"decode":const c=a.buffer,l=a.taskConfig;e.then(u=>{const f=u.draco,h=new f.Decoder;try{const d=t(f,h,new Int8Array(c),l),m=d.attributes.map(_=>_.array.buffer);d.index&&m.push(d.index.array.buffer),self.postMessage({type:"decode",id:a.id,geometry:d},m)}catch(d){console.error(d),self.postMessage({type:"error",id:a.id,error:d.message})}finally{f.destroy(h)}});break}};function t(o,a,c,l){const u=l.attributeIDs,f=l.attributeTypes;let h,d;const m=a.GetEncodedGeometryType(c);if(m===o.TRIANGULAR_MESH)h=new o.Mesh,d=a.DecodeArrayToMesh(c,c.byteLength,h);else if(m===o.POINT_CLOUD)h=new o.PointCloud,d=a.DecodeArrayToPointCloud(c,c.byteLength,h);else throw new Error("THREE.DRACOLoader: Unexpected geometry type.");if(!d.ok()||h.ptr===0)throw new Error("THREE.DRACOLoader: Decoding failed: "+d.error_msg());const _={index:null,attributes:[]};for(const g in u){const p=self[f[g]];let M,v;if(l.useUniqueIDs)v=u[g],M=a.GetAttributeByUniqueId(h,v);else{if(v=a.GetAttributeId(h,o[u[g]]),v===-1)continue;M=a.GetAttribute(h,v)}const x=s(o,a,h,g,p,M);g==="color"&&(x.vertexColorSpace=l.vertexColorSpace),_.attributes.push(x)}return m===o.TRIANGULAR_MESH&&(_.index=n(o,a,h)),o.destroy(h),_}function n(o,a,c){const u=c.num_faces()*3,f=u*4,h=o._malloc(f);a.GetTrianglesUInt32Array(c,f,h);const d=new Uint32Array(o.HEAPF32.buffer,h,u).slice();return o._free(h),{array:d,itemSize:1}}function s(o,a,c,l,u,f){const h=f.num_components(),m=c.num_points()*h,_=m*u.BYTES_PER_ELEMENT,g=r(o,u),p=o._malloc(_);a.GetAttributeDataArrayForAllPoints(c,f,g,_,p);const M=new u(o.HEAPF32.buffer,p,m).slice();return o._free(p),{name:l,array:M,itemSize:h}}function r(o,a){switch(a){case Float32Array:return o.DT_FLOAT32;case Int8Array:return o.DT_INT8;case Int16Array:return o.DT_INT16;case Int32Array:return o.DT_INT32;case Uint8Array:return o.DT_UINT8;case Uint16Array:return o.DT_UINT16;case Uint32Array:return o.DT_UINT32}}}const Zy=224,Oi=5.4,Go=2.4,ec=8,wh=3,Jy="https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/libs/draco/gltf/",$b=(Oi/2-Go)/Oi,ti=2,Qy=.5,eM=new b(-.35,-.8,.5),tM=.6,nM=new b(.6,.6,.7),iM=new b(.02,.02,.05),sM=.036,Z={l:1,r:-1},rs=65,ia=25,rM=25,oM=-6,Th=95,aM=30,cM=20,Ff=40,Bf=25,kf=10,No=[.4,-.92,2.1],Fl=[.6,.3,-1],lM=[1,-.4,.35],uM=25,hM=4,wr=18,fM=new Set(["butler_tray"]),tc="butler_tablet",nc="butler_towel",zf=new Set(["colleague_mug"]),sa=new Set([...zf,"squire_shield","coach_clipboard"]),It=new Set([...sa,"squire_quill"]),dM=.06,pM={forearm:new b(0,0,-1),shin:new b(1,0,0)},Qs=new De().set(1,0,0,0,0,0,1,0,0,-1,0,0,0,0,0,1),ra=Qs.clone().invert(),Wo=i=>i.clone().applyMatrix4(ra),Ci=i=>new De().makeTranslation(i.x,i.y,i.z),hn=ci.degToRad,Ps=(i,e,t)=>new De().makeRotationFromEuler(new Un(hn(i),hn(e),hn(t),"ZYX"));function dr(i,e){return Ci(i).multiply(e).multiply(Ci(i.clone().negate()))}function mM(i){const e=i.match(/^(.*)_([lr])$/);return e?{base:e[1],side:e[2]}:{base:i,side:""}}function gM(i,e){const{x:t,y:n,z:s}=pM[i];return e==="l"?new b(t,n,s):new b(t,-n,-s)}class _M{constructor(e,t="stand",n=0){this.rig=e,this.final=new Map,this.eyes=1,this.eyeTint=null,this.hearts=0,this.stars=0,this.squeezed=0,this.laptop=!1,this.tablet=!1,this.cloth=!1,this.book=null,this.props=new Map,this.stowed=new Set,this.keep=new Set,this.tap=0,this.gaze=null,this.posture=t,this.sway=0,this.stride=n,this.sky=null,this.screen=null}standing(e){const t=this.rig.parents.get(e);return t?this.matrix(t):new De}matrix(e){return this.final.get(e)??this.standing(e)}head(e,t){return this.rig.heads.get(e).clone().applyMatrix4(t)}turn(e,{x:t=0,y:n=0,z:s=0}){const r=this.matrix(e);this.final.set(e,dr(this.head(e,r),Ps(t,n,s)).multiply(r))}face(e,{x:t=0,y:n=0,z:s=0}){const r=this.head(e,this.standing(e)),o=this.rig.heads.get(e).clone().negate();this.final.set(e,Ci(r).multiply(Ps(t,n,s)).multiply(Ci(o)))}lift(e,{x:t=0,y:n=0,z:s=0}){this.final.set(e,Ci(new b(t,n,s)).multiply(this.matrix(e)))}bend(e,t){const{base:n,side:s}=mM(e),r=this.standing(e),o=gM(n,s).transformDirection(r).normalize(),a=new De().makeRotationAxis(o,hn(t));this.final.set(e,dr(this.head(e,r),a).multiply(r))}aim(e,t){const n=this.standing(e),s=this.rig.along.get(e).clone().transformDirection(n),r=new De().makeRotationFromQuaternion(new On().setFromUnitVectors(s,t.clone().normalize()));this.final.set(e,dr(this.head(e,n),r).multiply(n))}reach(e,t,n){this.limbTo(e,["upper_arm","forearm","hand"],t,n)}step(e,t,n){this.limbTo(e,["thigh","shin","foot"],t,n)}limbTo(e,t,n,s){const[r,o,a]=t.map(p=>`${p}_${e}`),c=this.rig.heads.get(o).distanceTo(this.rig.heads.get(r)),l=this.rig.heads.get(a).distanceTo(this.rig.heads.get(o)),u=this.head(r,this.standing(r)),f=n.clone().sub(u),h=f.length();if(h<Math.abs(c-l)||h>c+l)throw new Error(`the ${r} cannot reach ${h.toFixed(3)}`);const d=f.clone().normalize(),m=(c*c-l*l+h*h)/(2*h),_=s.clone();e==="r"&&(_.x=-_.x),_.sub(d.clone().multiplyScalar(_.dot(d)));const g=u.clone().add(d.multiplyScalar(m)).add(_.normalize().multiplyScalar(Math.sqrt(Math.max(c*c-m*m,0))));this.aim(r,g.clone().sub(u)),this.aim(o,n.clone().sub(g))}turnAll({x:e=0,y:t=0,z:n=0},s=new b){const r=dr(s,Ps(e,t,n));this.final=new Map(this.rig.order.map(o=>[o,r.clone().multiply(this.matrix(o))]))}revolve(e){this.turnAll({z:e})}bendAbove(e,{x:t=0,y:n=0,z:s=0}){const r=dr(this.head(e,this.matrix(e)),Ps(t,n,s)),o=a=>a===e||!!a&&o(this.rig.parents.get(a));this.final=new Map(this.rig.order.map(a=>[a,o(a)?r.clone().multiply(this.matrix(a)):this.matrix(a)]))}shiftAll(e){const t=Ci(new b(...e));this.final=new Map(this.rig.order.map(n=>[n,t.clone().multiply(this.matrix(n))]))}carried(e){return e.clone().add(this.head("root",this.matrix("root")).sub(this.rig.heads.get("root")))}swing(e){this.sway=e}shutEyes(e){this.eyes=Math.max(e,dM)}tintEyes(e){this.eyeTint=e}heartEyes(e){this.hearts=e}starEyes(e){this.stars=e}squeezeEyes(e){this.squeezed=e}holdLaptop(){this.laptop=!0}holdTablet(){this.tablet=!0}holdCloth(){this.cloth=!0}holdBook(e,t,n){this.book={open:e,page:t,visible:n}}holdProp(e,t,n=[0,0,0],s={}){this.props.set(e,{bone:`hand_${t}`,frame:`hand_${t}`,at:this.grip(t,n),turn:s})}holdUpright(e,t,n=[0,0,0],s={}){this.props.set(e,{bone:`hand_${t}`,frame:"root",at:this.grip(t,n),turn:s})}wearProp(e,t,n={}){this.props.set(e,{bone:"head",frame:"head",at:this.rig.heads.get("head").clone().add(new b(...t)),turn:n})}grip(e,t){return this.rig.heads.get(`hand_${e}`).clone().add(new b(Z[e]*(js.grip+t[0]),js.forward+t[1],t[2]))}putAway(...e){e.forEach(t=>this.stowed.add(t))}moves(e){const t=new De().makeRotationZ(hn(e)),n=new Map;for(const s of this.rig.order){const r=this.rig.parents.get(s);n.set(s,this.final.get(s)??(r?n.get(r):new De))}return new Map([...n].map(([s,r])=>[s,t.clone().multiply(r)]))}}const Te=(i,e=1)=>Math.sin(2*Math.PI*e*i);function pe(i,e,t=1){i.turn("spine",{x:1*t*Te(e)}),i.turn("chest",{x:1.5*t*Te(e-.05)}),i.turn("neck",{x:-.8*t*Te(e-.1)}),i.turn("head",{x:-1.2*t*Te(e-.12)})}function ae(i,{lean:e=0,twist:t=0,nod:n=0,turn:s=0,tilt:r=0}){i.turn("spine",{x:e*.4,z:t*.4}),i.turn("chest",{x:e*.6,z:t*.6}),i.turn("neck",{x:n*.3,z:s*.3,y:r*.3}),i.turn("head",{x:n*.7,z:s*.7,y:r*.7})}function Hf(i,e,t=0,n=10){i.turn(`upper_arm_${e}`,{y:Z[e]*rs}),i.turn(`upper_arm_${e}`,{x:t}),i.bend(`forearm_${e}`,n)}function xM(i,e,t=oM,n=0,s=0){const r=Z[e];i.turn(`upper_arm_${e}`,{y:r*rs}),i.turn(`upper_arm_${e}`,{x:-n}),i.turn(`upper_arm_${e}`,{z:r*cM}),i.face(`forearm_${e}`,{y:-r*t,z:-r*Th}),i.face(`hand_${e}`,{x:s,z:-r*(Th-aM)})}function Ce(i,e,t=[],n={},s=e.level){var r;for(const o of Object.keys(Z))if(!t.includes(o)){if(s.has(o)){xM(i,o);continue}Hf(i,o,n[o]??0),(r=e.shield)!=null&&r.has(o)&&i.turn(`hand_${o}`,{y:-Z[o]*iS,z:Z[o]*nS})}}const it=i=>i.busy.has("r")?"l":"r";function oa(i,e,t){pe(i,t),Ce(i,e),i.swing(Te(t))}function vM(i,e,t){const n=Math.max(Te(t,2),0);ae(i,{lean:4*n,nod:26*n}),Ce(i,e)}function yM(i,e,t){ae(i,{turn:28*Te(t,2),tilt:4*Te(t,2)}),Ce(i,e)}function MM(i,e,t){const n=it(e),s=Z[n];ae(i,{twist:-s*4,turn:-s*8,tilt:-s*6}),Ce(i,e,[n]),Vf(i,n,t)}function Vf(i,e,t){i.turn(`upper_arm_${e}`,{x:-85}),i.turn(`upper_arm_${e}`,{z:Z[e]*Ff}),i.bend(`forearm_${e}`,Bf+kf*Te(t))}function SM(i,e,t){const n=Z[it(e)];ae(i,{nod:-6+3*Te(t),turn:-n*10+4*Te(t),tilt:-n*6}),Ce(i,e)}function EM(i,e){const t=Z[e],[n,s,r]=No;i.reach(e,i.carried(new b(t*n,s,r)),new b(...Fl));const[o,a,c]=lM;i.aim(`hand_${e}`,new b(-t*o,a,c)),i.turn(`hand_${e}`,{x:uM})}function bM(i,e,t){const n=Math.max(Math.sin(2*Math.PI*2*t),0);i.lift("root",{z:.28*n}),i.turn("hips",{z:6*Te(t,2)}),ae(i,{lean:-5,turn:-6*Te(t,2)});const s=Object.keys(Z).filter(r=>!e.busy.has(r));Ce(i,e,s);for(const r of s)Z[r],qt(i,r,1,{y:-ia,bend:10+6*Te(t,4)});for(const r of Object.keys(Z))i.turn(`thigh_${r}`,{x:-18*n}),i.turn(`shin_${r}`,{x:34*n}),i.turn(`foot_${r}`,{x:-10*n})}function wM(i,e,t){const n=t*(k.yawnFrames+wr);if(n<k.yawnFrames)return id(i,e,n/k.yawnFrames);const s=Te((n-k.yawnFrames)/wr);ae(i,{lean:4+1.5*s,nod:8+2*s,tilt:Z[it(e)]*hM}),Ce(i,e),i.shutEyes(0)}function TM(i,e,t){i.stride=t;const n=2*Math.PI*t;Gf(i),i.turn("hips",{z:5*Math.sin(n)}),ae(i,{lean:3,twist:-7*Math.sin(n),turn:3*Math.sin(n)}),Ce(i,e,[],{l:22*Math.sin(n),r:-22*Math.sin(n)}),Wf(i)}function Gf(i){i.lift("root",{z:.05*Math.cos(4*Math.PI*i.stride)})}function Wf(i){for(const[e,t]of[["l",0],["r",Math.PI]]){const n=2*Math.PI*i.stride+t,s=-30*Math.sin(n),r=42*Math.max(Math.cos(n),0);i.turn(`thigh_${e}`,{x:s}),i.turn(`shin_${e}`,{x:r}),i.turn(`foot_${e}`,{x:-.8*(s+r)+6})}}const Xo=4.4,Xf=.72,qf=.94,Bl=[1.84,.38,.2],kl=[1.36,.6,.16],Ah=.14,AM=.2,RM=66,CM=1.25,PM=2.91,ic={back:.58,up:.36,rise:.38},LM=new b(1,-1,-1);function Fi(i){return i=Math.min(Math.max(i,0),1),i*i*(3-2*i)}function Ct(i,e){return Math.min(Math.max(i*e/(e-1),0),1)}const Mt=(i,e,t)=>Math.min(Math.max((i-e)/(t-e),0),1),te=(i,e,t)=>Fi(Mt(i,e,t)),ke=(i,e,t)=>Math.sin(Math.PI*Mt(i,e,t)),kt=(i,e,t)=>i+(e-i)*t,Rh=(i,e,t)=>Math.exp(-t*i)*Math.sin(2*Math.PI*e*i)*(1-i);function IM(i,e){return i!=="pull_ups"||!(e.busy.size||e.level.size)}function DM(i){i.lift("root",{z:AM})}function NM(i){for(const[e,t]of Object.entries(Z))i.turn(`thigh_${e}`,{x:-88}),i.bend(`shin_${e}`,RM+t*9*i.sway),i.turn(`foot_${e}`,{x:-t*5*i.sway+(e==="r"?i.tap:0)})}function cs(i,e){i.posture==="stand"&&(i.lift("root",{z:-e}),Bi(i,e))}function zl(i,e,t,n,s=Fl){Ce(i,e,[...e.free]);for(const r of e.free)Ut(i,r,t,i.carried(new b(Z[r]*n[0],n[1],n[2])),new b(...s))}const Yf={hearts:{open:1,tint:null,hearts:!0},amused:{open:.3,tint:[1,.85,.4]},startled:{open:1.5,tint:[1,1,1]},worried:{open:.7,tint:[.6,.75,1]},angry:{open:.45,tint:[1,.35,.3]},reading:{open:.8,tint:null}};function Ze(i,e,t=1){const{open:n,tint:s}=Yf[e];i.shutEyes(kt(1,n,t)),s&&t>.5&&i.tintEyes(s)}const Uo=[.3,-.45,2],UM=[.46,-.82,2.04];function OM(i,e,t){const n=ke(t,.55,.75),s=(1-n)*Te(t,6);pe(i,0),ae(i,{lean:6,nod:20-4*n,turn:2*Te(t)}),zl(i,e,1,[Uo[0],Uo[1],Uo[2]+.035*s]),i.holdLaptop(),Ze(i,"reading")}function FM(i,e,t){const n=Ct(t,20),s=Math.max(Math.sin(2*Math.PI*2*Mt(n,.1,.9)),0)*(1-.3*n);i.lift("root",{z:.32*s}),pe(i,0),ae(i,{lean:-5*s,nod:-14+4*s}),xn(i,e,0,70+55*s,6*Te(t,4)),ki(i,.5*s)}function BM(i,e,t){const n=Ct(t,28),s=te(n,0,.2)*(1-te(n,.82,1)),r=ke(n,.28,.82);pe(i,0),ae(i,{lean:4*s,nod:10*s,turn:24*r*Te(Mt(n,.28,.82),1.5)}),zl(i,e,s,UM);for(const o of e.free)i.face(`hand_${o}`,{z:-Z[o]*90*s});Ze(i,"worried",s)}function kM(i,e,t){const n=Ct(t,24),s=ke(n,.05,.5)-ke(n,.5,.95);pe(i,0),ae(i,{turn:34*s,nod:-4*Math.abs(s),tilt:4*s}),Ce(i,e)}function zM(i,e,t){const n=Ct(t,24),s=ke(n,.05,.9);pe(i,0),ae(i,{lean:-10*s,nod:-10*s}),xn(i,e,0,100*s),i.shutEyes(1-.9*ke(n,.2,.75))}function HM(i,e,t,n){i=(i%1+1)%1;const s=e*t;if(i<t)return[-s/2+e*i,0];const r=(i-t)/(1-t);return[s/2-s*Fi(r),n*Math.sin(Math.PI*r)]}function aa(i,e,t,n,s,r=0){const o=i.rig.heads.get(`thigh_${e}`),a=i.rig.heads.get(`shin_${e}`),c=i.rig.heads.get(`foot_${e}`),l=o.z-a.z,u=a.z-c.z,f=l+u+s-n,h=(t*t+f*f-l*l-u*u)/(2*l*u);if(h<-1-1e-10||h>1+1e-10)throw new RangeError(`${e} stride target is outside the unchanged leg reach`);const d=Math.acos(Math.round(h*1e10)/1e10),m=Math.atan2(t,f)-Math.atan2(u*Math.sin(d),l+u*Math.cos(d));i.turn(`thigh_${e}`,{x:m*180/Math.PI}),i.bend(`shin_${e}`,d*180/Math.PI),i.face(`foot_${e}`,{x:r})}function ca(i,e,t,n,{running:s=!1,lean:r=s?10:3,clearance:o,apart:a=[],drop:c=0,bend:l={},behind:u=0}={}){const[f,h,d]=s?Bl:kl,m=t%.5,_=s&&m>h?Math.max(0,Math.sin(Math.PI*(m-h)/(.5-h))):0,g=n*(-(s?.075:.11)+(s?.055*_:0))-c;i.lift("root",{z:g}),pe(i,0),ae(i,{...l,lean:r*n+(l.lean??0),nod:(s?-6:-2)*n+(l.nod??0)});const p=(s?24:14)*Te(t)*n,M=e.carried??e.busy,v=Object.keys(Z).filter(x=>s&&!M.has(x)&&!e.level.has(x)&&!a.includes(x));Ce(i,e,[...v,...a],Object.fromEntries(Object.entries(Z).map(([x,L])=>[x,M.has(x)?0:L*p])));for(const x of v)Hf(i,x,Z[x]*p,10+40*n);if(n>0||c||u)for(const[x,L]of[["l",0],["r",.5]]){const[T,R]=HM(t+L,f,h,o??d),I=(t+L)%1,w=I>=h?(I-h)/(1-h):0,S=(s?14:11)*Math.sin(Math.PI*w)*n;aa(i,x,n*T+u,n*R,g,S)}}function er(i,e,t,n,s,r={}){const o=Mt(t,0,n),a=Fi(o);return i.lift("root",{y:Xo*(1-a)}),ca(i,e,Xo*a/(r.running?Bl:kl)[0],1-Fi((o-.76)/.24),r),90*(1-te(t,n,s))}function Or(i,e,t,n,s,r={}){const o=Mt(t,n+Ah/2,1),a=(o<.3?o*o/.6:o-.15)/.85;return i.lift("root",{y:-Xo*a}),ca(i,e,Xo*a/(r.running?Bl:kl)[0],Fi(o/.25),r),s*90*te(t,n,n+Ah)}function jf(i,e,t,n,s=!1){i.revolve(er(i,e,Ct(t,n),Xf,qf,{running:s}))}function VM(i,e,t){jf(i,e,t,40)}function GM(i,e,t){jf(i,e,t,28,!0)}function WM(i,e,t){if(!IM("pull_ups",e)){oa(i,e,t);return}$f(i,e,t,{pull:.5-.5*Math.cos(2*Math.PI*t),swing:0})}const Ch=i=>(e,t,n)=>$f(e,t,n,{pull:0,swing:Te(n),grips:[i]});function $f(i,e,t,{pull:n,swing:s,grips:r=Object.keys(Z)}){const o=r.filter(a=>e.free.has(a));i.lift("root",{y:ic.back,z:ic.up+ic.rise*n}),ae(i,{nod:-3*n,turn:2*s}),Ce(i,e,o);for(const[a,c]of Object.entries(Z))i.turn(`thigh_${a}`,{x:-8+7*s*c}),i.bend(`shin_${a}`,18+8*s*c),i.turn(`foot_${a}`,{x:-10}),o.includes(a)&&(i.reach(a,new b(c*CM,0,PM),LM),i.face(`hand_${a}`,{x:-90}))}const XM=36,qM=28,pr=.5,Ph=.36,YM=16,jM=7,Lh=-2.45,Ih=-1.54,sc=new b(1,-.6,.02),$M=new b(1,-1,-1),KM=new b(0,1,0),ZM={y:-15,z:-10,bend:15},JM=.97,Fr=new b(...Fl),Pi=.24,Kf=.1,QM=6.04,eS=10.36,Eo=.52,mr=.42,Dh=.6,tS={y:60,z:-10,bend:15},nS=60,iS=45,Zf={y:30,z:-25,bend:10},sS={y:0,z:-15,bend:0};function qt(i,e,t,{y:n=rs,x:s=0,z:r=0,bend:o=10}){const a=Z[e];i.turn(`upper_arm_${e}`,{y:a*kt(rs,n,t)}),i.turn(`upper_arm_${e}`,{x:s*t}),i.turn(`upper_arm_${e}`,{z:a*r*t}),i.bend(`forearm_${e}`,kt(10,o,t))}function Ut(i,e,t,n,s){const r=i.head(`upper_arm_${e}`,i.standing(`upper_arm_${e}`)),o=n.clone().sub(r),c=new b(Z[e]*Math.cos(hn(rs)),0,-Math.sin(hn(rs))).lerp(o.clone().normalize(),t).normalize();i.reach(e,r.clone().add(c.multiplyScalar(kt(JM,o.length(),t))),KM.clone().lerp(s,t))}const Br=i=>new b(Z[i]*No[0],No[1],No[2]);function Bi(i,e){for(const t of Object.keys(Z))aa(i,t,0,0,-e)}function rS(i,e,t){[...e.level].sort().forEach((n,s)=>{const r=Math.max(t-.05*s,0);i.turn(`hand_${n}`,{x:YM*Rh(r,3,2.5),y:Z[n]*jM*Rh(r,2.5,3)})})}const Jf=(i,e)=>e.reduce((t,n)=>t+ke(i,n,n+.05),0),tr=i=>[...i.carried].filter(e=>!i.busy.has(e));function oS(i,e,t){const n=ke(t,pr,pr+.22),s=er(i,e,t,pr,pr+.14,{running:!0,lean:15,drop:.12*n,bend:{lean:-7*n,nod:5*n}});rS(i,e,Mt(t,pr,1)),i.revolve(s)}function aS(i,e,t){const n=ke(t,0,Ph);i.revolve(Or(i,e,t,Ph,-1,{bend:{lean:30*n,nod:24*n}}))}function cS(i,e,t){const n=Mt(t,.55,.72),s=t<.72?0:Pi*(1-te(t,.84,1)),r=t<.55?kt(-4.4,Lh,te(t,0,.16))+(Ih-Lh)*te(t,.3,.55):t<.72?kt(Ih,-Pi,n)+1.2*Math.sin(Math.PI*n):-s;i.lift("root",{z:r}),pe(i,0),ae(i,{turn:25*Math.sin(2*Math.PI*Mt(t,.06,.2)),lean:14*(s/Pi)+8*te(t,.3,.55)*(1-n),nod:-10*ke(t,.86,1)});const o=t>=.2&&t<.55?te(t,.2,.27):0,a=ke(t,.55,.74);Ce(i,e,o||a?Object.keys(Z):[]);for(const c of Object.keys(Z))o?(Ut(i,c,o,new b(Z[c]*sc.x,sc.y,sc.z),$M),i.face(`hand_${c}`,{z:-Z[c]*90*o})):a&&qt(i,c,a,ZM);Bi(i,t<.72?kt(0,Pi,n)+Kf*Math.sin(Math.PI*n):s)}function lS(i,e,t){const n=Mt(t,.3,1),s=te(t,.05,.3),r=te(t,.3,.42);i.lift("root",{y:-2.4*n,z:t<.3?-Pi*s:-Pi+QM*n-eS*n*n}),pe(i,0),ae(i,{lean:15*s*(1-r),nod:18*s*(1-r)});for(const o of Object.keys(Z))qt(i,o,s,{y:kt(rs,-15,r),x:kt(40,0,r),z:-10*r,bend:10});Bi(i,t<.3?Pi*s:Pi*(1-r)+2*Kf*ke(t,.36,.62)),i.revolve(-35*te(t,0,.2))}function uS(i,e,t){const n=[...e.busy],s=tr(e),r=1-te(t,.7,.92),o=ke(t,Eo,Eo+.2),a=er(i,e,t,Eo,Eo+.14,{running:!0,lean:14,apart:[...n,...s],drop:.14*o,bend:{lean:-6*o}});n.forEach(c=>qt(i,c,r,tS)),s.forEach(c=>qt(i,c,r,Zf)),i.shutEyes(1-.45*r),i.revolve(a)}function hS(i,e,t){const n=tr(e),s=te(t,0,.12)*(1-te(t,.24,.34)),r=Or(i,e,t,.34,-1,{clearance:.18,lean:0,apart:s?n:[],bend:{nod:10*ke(t,.1,.26)}});s&&n.forEach(o=>Ut(i,o,s,Br(o),Fr)),i.revolve(r)}function fS(i,e,t){const n=it(e),s=te(t,mr,mr+.04)*(1-te(t,.62,.7)),r=6*Mt(t,mr,.7),o=-.05*s*Math.abs(Te(r)),a=te(t,.7,.76)*(1-te(t,.9,.98)),c=Jf(t,[.77,.83]);i.lift("root",{z:o});const l=er(i,e,t,mr,mr+.1,{running:!0,lean:6,apart:a?[n]:[],bend:{nod:7*c,lean:2*c}});if(a&&Ut(i,n,a,Br(n),Fr),s)for(const[u,f]of[["l",0],["r",.5]])aa(i,u,0,.22*s*Math.max(Te(r+f),0),o);i.shutEyes(1-.6*c),i.revolve(l)}function dS(i,e,t){const n=it(e),s=te(t,0,.06)*(1-te(t,.2,.26)),r=te(t,.26,.32)*(1-te(t,.42,.5)),o=Jf(t,[.07,.13]),a=Or(i,e,t,.4,Z[n],{running:!0,lean:6,apart:s||r?[n]:[],bend:{nod:7*o,lean:2*o}});s&&Ut(i,n,s,Br(n),Fr),r&&qt(i,n,r,sS),i.shutEyes(1-.6*o),i.revolve(a)}function pS(i,e,t){const n=te(t,.72,.8)*(1-te(t,.9,.98)),s=ke(t,.78,.92),r=[...e.level].sort(),o=er(i,e,t,Dh,Dh+.12,{apart:n?r:[],bend:{nod:-8*s}});n&&sd(i,e,n,s),i.shutEyes(1-.7*s),i.revolve(o)}function mS(i,e,t){const n=it(e),s=te(t,0,.08)*(1-te(t,.24,.32)),r=Or(i,e,t,.3,Z[n],{apart:s?[n]:[],bend:{tilt:-Z[n]*5*s}});s&&qt(i,n,s,{y:0,x:-85,z:Ff,bend:Bf+kf*Te(Mt(t,0,.32),2)}),i.revolve(r)}function gS(i,e,t){i.revolve(er(i,e,t,Xf,qf))}function _S(i,e,t){i.revolve(Or(i,e,t,0,-1))}const xS={bare:gS,butler:oS,homie:cS,squire:uS,coach:fS,colleague:pS},vS={bare:_S,butler:aS,homie:lS,squire:hS,coach:dS,colleague:mS};function yS(i,e,t){xS[e.voice](i,e,Ct(t,XM))}function MS(i,e,t){vS[e.voice](i,e,Ct(t,qM))}const SS=.2,ES=1.4,Nh=.13;function Qf(i){return te(i,0,.22)-2*te(i,.32,.62)+te(i,.7,.85)}function bS(i,e,t){const n=it(e),s=Qf(t);cs(i,SS),pe(i,0),ae(i,{lean:26,nod:20,turn:-Z[n]*28*s,twist:-Z[n]*10*s}),Ce(i,e,[n]),qt(i,n,1,{y:30,z:-60+25*s,bend:80}),i.holdUpright("magnifying_glass",n,[0,0,0],{x:vb}),Ze(i,"reading")}const ut={intro:12,hold:48,outro:12,fps:12,ready:3,opens:11,pageEvery:24,pageFrom:12,pageTo:20,lines:4,referenceArm:.985,forward:.68,drop:.3,drawDrop:.18,elbow:[1,-1,-1],wristTurn:90},cl=ut.intro+ut.hold+ut.outro,js={grip:.34,forward:.02},k={intro:8,hold:32,outro:8,fps:12,yawnFrames:28,pastimeFrames:40,greetingFrames:24,hopFrames:20,stumbleFrames:24,elbow:[1,-.15,-.35],wrist:[.72,-.72,1.76],supportLift:.22,whistleLift:.25,clothLift:.2,clothTurn:-90,compactFps:6,tap:10,rock:3,turn:12,nod:8,writeStroke:.035,writeHeight:.02,glance:22,hop:.18,stumble:12,writingWrist:[.38,-.76,2.1],yawnWrist:[.48,-.86,2.12],whistleWrist:[.48,-.82,2.2],sipWrist:[.7,-.63,2.17],shieldWrist:[.22,-.64,2.13],wipeWrist:[.1,-.7,1.9],saluteWrist:[1.28,-.32,2.59],gestureIn:.2,gestureOut:.8,yawnEyes:.94,yawnSpan:[.08,.92],pastimeSpan:[.3,.7],whistleEyes:.65,sipEyes:.5,sipTip:12,headphoneEyes:.4,beats:4,sways:2,wipes:3,wipeLift:.035,wipeAcross:.04,bowLean:18,bowNod:10,leapSpan:[.18,.78],catchSpan:[.15,.45],recoverSpan:[.45,.85],recover:.3},ed={butler:"writing_stylus",coach:"writing_pencil",colleague:"writing_pen",homie:"writing_marker",squire:"writing_quill"},qo=k.intro+k.hold+k.outro,Qt={intro:8,hold:144,outro:8,whistleSpan:[.7,.98],beats:12,sways:3},ll=Qt.intro+Qt.hold+Qt.outro,Oo={across:.04,top:.52,bottom:.44,forward:[0,-1,0]};function td(i){const e=i*qo,t=e>=k.intro&&e<k.intro+k.hold,n=e<k.intro?e:qo-1-e;return{frame:e,held:t,ready:t?1:te(n,0,k.intro-1),phase:t?(e-k.intro)/k.hold:0}}function wS(i){const e=i*ll,t=e>=Qt.intro&&e<Qt.intro+Qt.hold,n=e<Qt.intro?e:ll-1-e;return{ready:t?1:te(n,0,Qt.intro-1),phase:t?(e-Qt.intro)/Qt.hold:0}}function Tn(i,e){const t=Ct(i,e);return{u:t,ready:te(t,0,k.gestureIn)*(1-te(t,k.gestureOut,1))}}function TS(i,e,t=[0,0,0]){return i.rig.heads.get(`hand_${e}`).clone().add(new b(Z[e]*(js.grip+t[0]),js.forward+t[1],t[2])).applyMatrix4(i.matrix(`hand_${e}`))}function $t(i,e,t,n,s={}){t&&(Ut(i,e,t,i.carried(new b(Z[e]*n[0],n[1],n[2])),new b(...k.elbow)),i.face(`hand_${e}`,{z:-Z[e]*90*t,...s}))}const Yo=65;function nd(i,e,t=1){const n=i.rig.eyes.reduce((u,f)=>u.add(f),new b).divideScalar(i.rig.eyes.length),s=i.head("head",i.standing("head")),r=e.clone().sub(s),o=n.z-i.rig.heads.get("head").z,a=Math.asin(ci.clamp(o/r.length(),-1,1))-Math.atan2(r.z,Math.hypot(r.x,r.y)),c=ci.radToDeg(Math.atan2(r.x,-r.y)),l=ci.clamp(c,-Yo,Yo);return i.face("head",{x:ci.radToDeg(a)*t,z:l*t}),i.gaze={target:e.toArray(),forward:Oo.forward},(c-l)*t}function AS(i,e,t){const n=t*cl,s=n>=ut.intro&&n<ut.intro+ut.hold,r=n<ut.intro?n:cl-1-n,o=s?1:te(r,0,ut.ready),a=s?1:te(r,ut.ready,ut.opens),c=s?(n-ut.intro)%ut.pageEvery:0,l=s?te(c,ut.pageFrom,ut.pageTo):0;pe(i,0),Ce(i,e);const u=Math.min(...Object.keys(Z).map(x=>{const L=T=>i.rig.heads.get(`${T}_${x}`);return L("upper_arm").distanceTo(L("forearm"))+L("forearm").distanceTo(L("hand"))}))/ut.referenceArm,f=Object.keys(Z).map(x=>i.head(`upper_arm_${x}`,i.standing(`upper_arm_${x}`))),h=f[0].clone().add(f[1]).multiplyScalar(.5),d=hd(a),m=Li("l",a).add(Li("r",a)).multiplyScalar(.5).applyMatrix4(d),_=new b(h.x-m.x*u,h.z-(ut.drop+ut.drawDrop*(1-o))*u-m.y*u,-h.y+ut.forward*u-m.z*u),g=new De().makeTranslation(_.x,_.y,_.z).multiply(d).scale(new b(u,u,u));for(const[x,L]of Object.entries(Z)){const T=Wo(Li(x,a).applyMatrix4(g));if(!o)continue;Ut(i,x,o,T,new b(...ut.elbow));const R=ci.radToDeg(Math.atan2(Le.closedGrip*(1-a),Le.gripBack));i.face(`hand_${x}`,{z:-L*(ut.wristTurn+R)*o})}const p=Math.floor(c/(ut.pageEvery/ut.lines)),M=c%(ut.pageEvery/ut.lines)/(ut.pageEvery/ut.lines-1),v=new b(kt(-.04,Oo.across,M),kt(Oo.top,Oo.bottom,p/(ut.lines-1)),-Le.pages).applyMatrix4(g);nd(i,Wo(v),a),i.holdBook(a,l,s||r>=ut.ready),Ze(i,"reading",a)}const RS=[.55,-.35,1.35],CS=[.65,-.92,2.04],rc=[.7,.2,-1],Uh=.06;function PS(i,e,t){pe(i,t);const n=[...e.cloth];Ce(i,e,n);const s=te(t,.15,.3)*(1-te(t,.75,.9)),r=te(t,.08,.15)*(1-te(t,.88,.95)),o=te(t,.3,.35)*(1-te(t,.7,.75));ae(i,{nod:6*s,tilt:4*o*Math.sin(2*Math.PI*3*t)});for(const a of n){const c=Z[a],l=2*Math.PI*4*t,u=RS.map((h,d)=>h+(CS[d]-h)*s),f=new b(c*(u[0]+Uh*o*Math.cos(l)),u[1],u[2]+Uh*o*Math.sin(l));Ut(i,a,r,i.carried(f),new b(c*rc[0],rc[1],rc[2])),i.face(`hand_${a}`,{z:-c*90*r}),r>.5&&i.holdCloth()}Ze(i,o>.5?"amused":"reading")}function LS(i,e,t){const{ready:n,phase:s}=wS(t),r=e.voice==="butler",o=ke(s,...Qt.whistleSpan)*n;pe(i,0),ae(i,{turn:k.turn*n,nod:-k.nod*o/2,lean:k.rock*Te(s,Qt.sways)*(r?o:n)}),Ce(i,e),i.tap=k.tap*Math.max(Te(s,Qt.beats),0)*n,i.posture==="stand"&&i.turn("foot_r",{x:i.tap}),o&&i.shutEyes(1-k.whistleEyes*o)}function id(i,e,t){const{u:n,ready:s}=Tn(t,k.yawnFrames),r=it(e);pe(i,0),ae(i,{lean:-k.rock*s,nod:-k.nod*s}),Ce(i,e),$t(i,r,s,k.yawnWrist),s&&i.putAway(...It),i.shutEyes(1-k.yawnEyes*ke(n,...k.yawnSpan))}function Oh(i,e,t){const{u:n,ready:s}=Tn(t,k.pastimeFrames),r=ke(n,...k.pastimeSpan),o=it(e);pe(i,0),ae(i,{lean:-k.rock*r,nod:-k.nod*r}),Ce(i,e),$t(i,o,s,k.whistleWrist),s&&i.putAway(...It,"coach_whistle"),s>.5&&i.holdProp("hand_whistle",o,[0,0,k.whistleLift],{z:Z[o]*90}),i.shutEyes(1-k.whistleEyes*r)}const bt={frames:120,fps:8,down:[0,.1],up:[.9,1],tunes:[[.3,.45],[.62,.8]],beats:40,pillow:[0,1,3.2],tilt:72,across:-1.6,kneeUp:60,kneeBend:105,glance:40,ankle:[-.15,-.15,-.1],crossedKnee:[1,-.4,.6],footBob:18,wrist:[.6,.55,2.85],fingers:[-1,.4,.4],elbow:[1,-.3,.8],straw:[.14,-.9,.4],strawTip:115,strawWag:8,eyes:.45,whistleEyes:.2},IS=i=>bt.tunes.reduce((e,[t,n])=>e+ke(i,t,n),0);function DS(i,e,t){const n=Ct(t,bt.frames),s=te(n,...bt.down)*(1-te(n,...bt.up)),r=IS(n),o=Math.max(Te(n,bt.beats),0);if(pe(i,0),Ce(i,e,s?Object.keys(Z):[]),!s)return;i.putAway(...It),ae(i,{turn:-bt.glance*s});for(const[u,f]of Object.entries(Z)){const[h,d,m]=bt.wrist;Ut(i,u,s,new b(f*h,d,m),new b(...bt.elbow));const[_,g,p]=bt.fingers;i.aim(`hand_${u}`,new b(f*_,g,p))}i.turn("thigh_l",{x:-bt.kneeUp*s}),i.bend("shin_l",bt.kneeBend*s);const a=i.head("shin_l",i.matrix("shin_l")),c=i.head("foot_r",i.standing("foot_r"));i.step("r",c.lerp(a.add(new b(...bt.ankle)),s),new b(...bt.crossedKnee)),i.turn("foot_r",{x:-bt.footBob*r*o}),i.wearProp("straw",bt.straw,{x:bt.strawTip+bt.strawWag*(1+r)*Te(n,9)});const l=new b(...bt.pillow);i.turnAll({x:-bt.tilt*s},l),i.turnAll({z:90*s},l),i.shiftAll([bt.across*s,-l.y*s,-l.z*s]),i.shutEyes(kt(1,kt(bt.eyes,bt.whistleEyes,r),s))}function sd(i,e,t,n){for(const s of e.level)$t(i,s,t,k.sipWrist,{x:-k.sipTip*n})}function NS(i,e,t){const{u:n,ready:s}=Tn(t,k.pastimeFrames);pe(i,0),ae(i,{nod:-k.rock*s}),Ce(i,e),sd(i,e,s,ke(n,...k.pastimeSpan)),i.shutEyes(1-k.sipEyes*ke(n,...k.pastimeSpan))}function US(i,e,t){const{u:n,ready:s}=Tn(t,k.pastimeFrames);pe(i,0),ae(i,{nod:k.nod*Te(n,k.beats)*s,tilt:k.rock*Te(n,k.sways)*s}),Ce(i,e),i.swing(Te(n,k.sways)*s),i.shutEyes(1-k.headphoneEyes*s)}function OS(i,e,t){const{u:n,ready:s}=Tn(t,k.pastimeFrames),r=[...e.shield][0];if(!r)return oa(i,e,t);const o=r==="l"?"r":"l";pe(i,0),ae(i,{nod:k.nod*s}),Ce(i,e),$t(i,r,s,k.shieldWrist),$t(i,o,s,[k.wipeWrist[0],k.wipeWrist[1]+k.wipeAcross*Te(n,k.wipes),k.wipeWrist[2]+k.wipeLift*Te(n,k.wipes*2)]),s&&(i.putAway("squire_quill"),i.keep.add("squire_shield")),s>.5&&i.holdProp("polishing_cloth",o,[0,0,k.clothLift],{x:k.clothTurn})}function FS(i,e,t){const{ready:n,phase:s}=td(t),r=k.writeStroke*Te(s,k.beats);if(pe(i,0),ae(i,{nod:k.nod*n,lean:k.rock*n}),Ce(i,e),$t(i,"l",n,k.wrist),$t(i,"r",n,[k.writingWrist[0]+r,k.writingWrist[1],k.writingWrist[2]]),n&&i.putAway(...It),n>=1){const o=e.voice==="butler",a=Yt.paper.thickness*(o?2.5:.5),c=k.wrist[2]+k.supportLift+a+Yt.pen.length/2+Yt.pen.tip-k.writingWrist[2];i.holdProp(ed[e.voice]||"writing_pen","r",[0,0,c],{z:-90}),i.holdProp(e.voice==="butler"?"writing_tablet":"writing_paper","l",[0,-k.wrist[0],k.supportLift],{z:90})}Ze(i,"reading",n)}function BS(i,e,t){const{ready:n,phase:s}=td(t);pe(i,0),ae(i,{nod:k.nod*n}),Ce(i,e),$t(i,"l",n,k.wrist),$t(i,"r",n,[k.wrist[0]+k.writeStroke*Te(s,k.sways),k.wrist[1],k.wrist[2]+k.writeHeight*Math.max(Te(s,k.sways),0)]),n&&i.putAway(...It),n>=1&&(i.holdProp("papers","l",[0,-k.wrist[0],k.supportLift],{z:90}),i.props.get("papers").phase=s)}function kS(i,e,t){const{ready:n}=Tn(t,k.greetingFrames);pe(i,0),ae(i,{lean:k.bowLean*n,nod:k.bowNod*n}),Ce(i,e),n&&i.putAway(...It)}function zS(i,e,t){const{ready:n}=Tn(t,k.greetingFrames),s=it(e);pe(i,0),ae(i,{nod:-k.rock*n}),Ce(i,e),$t(i,s,n,k.saluteWrist),n&&i.putAway(...It)}function HS(i,e,t){const{u:n,ready:s}=Tn(t,k.hopFrames),r=ke(n,...k.leapSpan);cs(i,k.hop*ke(n,0,k.leapSpan[0])),i.lift("root",{z:k.hop*r}),pe(i,0),ae(i,{lean:-k.rock*r}),xn(i,e,0,ia*r),i.posture==="stand"&&ki(i,r),Ze(i,"startled",s)}function VS(i,e,t){const{u:n,ready:s}=Tn(t,k.stumbleFrames),r=ke(n,...k.catchSpan)-k.recover*ke(n,...k.recoverSpan);pe(i,0),ae(i,{lean:k.stumble*r,tilt:k.rock*r}),xn(i,e,0,ia*s),Ze(i,"startled",Math.max(r,0))}function GS(i,e,t){const{ready:n}=Tn(t,k.greetingFrames);pe(i,0),ae(i,{turn:k.glance*n,nod:-k.rock*n}),Ce(i,e)}const Nn={blows:1,blowFrames:8,fps:10,lands:.3,snap:50,turn:80,landsAt:[.74,-1.27]};function WS(i){const e=i*Nn.blows%1;return e<Nn.lands?1-(e/Nn.lands)**2:Fi(Mt(e,Nn.lands,1))}function Kb(i){const e=Z[it(i)],[t,n]=Nn.landsAt,s=hn(e*Nn.turn);return(e*t*Math.cos(s)-n*Math.sin(s))/Oi}function XS(i,e,t){const n=it(e),s=WS(t),r=1-s;cs(i,.04*r),pe(i,0),ae(i,{lean:8+6*r,nod:10}),Ce(i,e,[n]),qt(i,n,1,{y:kt(75,5,s),z:-35,bend:kt(15,70,s)}),i.holdProp("work_hammer",n,[0,0,0],{x:Nn.snap*r,z:Yt.hammer.tilt*Z[n]}),i.posture==="stand"&&i.revolve(Z[n]*Nn.turn)}const Ti={step:.6,hop:.12,lean:8,shadeWrist:[1.18,-.5,2.72],shadeHand:[-.35,-1,.2]},qS=-1.2;function YS(i,e,t=0){const n=new b((e.x-.5)*Oi,qS,Go+(.5-e.y)*Oi),s=i.matrix("head").clone(),r=nd(i,n.applyAxisAngle(new b(0,0,1),hn(-t))),o=e.amount??1;return o<1&&i.final.set("head",jS(s,i.matrix("head"),o)),r*o*o}function jS(i,e,t){const[n,s]=[i,e].map(r=>{const o={at:new b,turn:new On,size:new b};return r.decompose(o.at,o.turn,o.size),o});return new De().compose(n.at.lerp(s.at,t),n.turn.slerp(s.turn,t),n.size.lerp(s.size,t))}function $S(i,e,t){const{shade:n,back:s}=i.sky??{shade:0,back:0};i.lift("root",{y:Ti.step*s,z:Ti.hop*Math.sin(Math.PI*s)}),pe(i,t),ae(i,{lean:-Ti.lean*s});const r=it(e);if(Ce(i,e,n?[r]:[]),n){$t(i,r,n,Ti.shadeWrist);const[o,a,c]=Ti.shadeHand,l=`hand_${r}`,u=i.rig.along.get(l).clone().transformDirection(i.matrix(l));i.aim(l,u.lerp(new b(Z[r]*o,a,c),n)),i.putAway(...It)}}const gr={lean:60,nod:-12,drop:.3,behind:.25,hands:[.4,-.25,.8]};function KS(i,e,t){ca(i,e,i.stride,i.posture==="walk"?1:0,{lean:0,drop:gr.drop,behind:gr.behind,bend:{nod:gr.nod}}),i.bendAbove("spine",{x:gr.lean});const[n,s,r]=gr.hands;for(const[o,a]of Object.entries(Z))Ut(i,o,1,new b(a*n,s,r),new b(...k.elbow)),i.face(`hand_${o}`,{z:-a*90});i.putAway(...It)}function ZS(i,e,t){const n=it(e);pe(i,0),ae(i,{nod:-14,lean:-3,tilt:-Z[n]*5}),Ce(i,e,[n]),qt(i,n,1,{y:-12+3*Te(t),z:-15,bend:10}),Ze(i,"worried",.6)}function xn(i,e,t,n,s=0){Ce(i,e,[...e.free]);for(const r of e.free){const o=Z[r],a=Math.min(Math.max(n/rM,0),1);qt(i,r,a,{x:t+s*o,y:-Math.min(n,ia),bend:10})}}function ki(i,e,t=0){for(const[n,s]of Object.entries(Z))i.turn(`thigh_${n}`,{x:-24*e+t*s}),i.turn(`shin_${n}`,{x:44*e}),i.turn(`foot_${n}`,{x:-8*e})}function JS(i,e,t){const n=Ct(t,16),s=te(n,0,.26)*(1-te(n,.26,.36)),r=te(n,.3,.45);i.lift("root",{z:.1*r}),pe(i,0),ae(i,{lean:14*s-6*r,nod:-4*r}),xn(i,e,40*s,80*te(n,.26,.42)*(1-.4*te(n,.6,1))),Bi(i,.28*s),ki(i,r)}const QS=25,eE=360;function tE(i,e,t){const n=Ct(t,22),s=te(n,0,.26)*(1-te(n,.26,.34)),r=te(n,.3,.86),o=te(n,.28,.4)*(1-te(n,.86,.95));i.lift("root",{z:.1*o}),pe(i,0),ae(i,{lean:12*s}),xn(i,e,30*s,QS*o),Bi(i,.28*s),ki(i,1.2*o),i.turnAll({x:eE*r},i.head("hips",i.matrix("hips")))}function nE(i,e,t){const n=Ct(t,12),s=te(n,0,.2),r=ke(n,0,.3);i.lift("root",{z:.1*s}),pe(i,0),ae(i,{lean:-9*s-8*r,nod:-6*s-10*r,tilt:4*Te(t,3)*s}),xn(i,e,0,(70+8*Te(t,3))*s+25*r,14*Te(t,3)*s),Ze(i,"startled",Math.max(r,.6*s)),ki(i,.5*s,14*Te(t,3)*s)}function iE(i,e,t){const n=Ct(t,ul.frames),s=te(n,0,.2)*(1-te(n,.2,1));pe(i,0),ae(i,{lean:16*s,nod:8*s}),xn(i,e,0,38*s),Bi(i,.32*s)}function sE(i,e,t){const n=Ct(t,24),s=n<.5,r=ES*(s?Fi(Mt(n,0,.5)):1-Fi(Mt(n,.5,1))),o=Math.sqrt(Math.max(Math.sin(Math.PI*n),0)),a=tr(e);i.lift("root",{y:s?-r:r}),ca(i,e,4*n,o,{running:!0,lean:12,apart:a}),a.forEach(c=>qt(i,c,o,Zf)),i.revolve((s?90:-90)*Math.min(1,3*Math.sin(Math.PI*n)))}function Fh(i,e,t){const n=Nh*Math.max(Te(3*t),0)*ke(t,0,1);pe(i,0),ae(i,{tilt:8*ke(t,0,1),nod:6*ke(t,0,1),turn:10*ke(t,0,1)}),Ce(i,e),aa(i,"r",0,n,0,15*n/Nh)}function rE(i,e,t){const n=ke(t,0,1);pe(i,0),ae(i,{tilt:14*n,nod:-8*n});for(const s of Object.keys(Z))qt(i,s,n,{y:30,z:-15,bend:100})}function oE(i,e,t){const n=it(e),s=te(t,0,.15)*(1-te(t,.8,1)),r=ke(t,.2,.75);pe(i,0),ae(i,{lean:-4*r,nod:-6*r}),Ce(i,e,s?[n]:[]),s&&Ut(i,n,s,Br(n),Fr),i.shutEyes(1-.7*r)}function aE(i,e,t){const n=it(e),s=te(t,0,.2)*(1-te(t,.6,.85));pe(i,0),ae(i,{nod:18*s*(1-te(t,.35,.5)),turn:-Z[n]*8*s}),Ce(i,e,s?[n]:[]),s&&Ut(i,n,s,Br(n),Fr)}function cE(i,e,t){const n=tr(e),s=te(t,0,.2)*(1-te(t,.75,1));pe(i,0),ae(i,{tilt:-5*s,nod:4*s}),Ce(i,e,s?n:[]),s&&n.forEach(r=>qt(i,r,s,{y:30,z:-25+5*Te(3*t),bend:10}))}const lE={bare:Fh,butler:Fh,homie:rE,coach:oE,colleague:aE,squire:cE};function uE(i,e,t){lE[e.voice](i,e,Ct(t,20))}const he={frames:36,fps:12,hatOn:1.101,hatWrist:[1.05,-.2,2.85],hatRaised:[.95,-.5,2.85],hatTip:25,hatFingers:.25,hatBow:22,hatNod:14,monocleWrist:[.55,-.8,2.62],monocleWorn:[.354,-.95,.66],monoclePeer:8,monocleTilt:9,toastWrist:[.78,-.72,2.55],toastClink:.12,sipWrist:[.42,-.78,2.38],sipTip:20,shakaWrist:[1.22,-.25,2.72],shakaWaggle:28,shakaWaggles:3,shadesWrist:[.5,-.82,2.55],shadesWorn:[0,-.96,.66],shadesLean:7,shadesTilt:10,fireWrist:[.48,-.86,2.28],fireSize:2.4,thumbWrist:[.62,-.84,2.3],glassesWrist:[.32,-.8,2.47],peerLean:12,peerTurn:18,prayerWrist:[.12,-.62,2],prayerRoll:180,thanksBow:14,popperWrist:[.95,-.45,2.85],popAt:.4,popHop:.12,flex:{y:0,x:-85,z:15,bend:115},flexPump:15,trophy:{y:-55,x:15,z:0,bend:15},trophyHop:.1,sword:{y:-62,x:18,z:0,bend:12},swordThrust:12,shieldWrist:[.24,-.78,2.3],shieldCrouch:.08,shieldBump:.5,castleWrist:[.55,-.88,2.34]},kr=i=>sa.forEach(e=>i.keep.add(e)),an=i=>Tn(i,he.frames);function pi(i,e,t,n,s={}){$t(i,e,t,n,{x:-60*t,...s})}const hE=new b(0,0,1);function fE(i,e,t){const{u:n,ready:s}=an(t),r=it(e),o=te(n,.2,.3)*(1-te(n,.7,.8)),a=te(n,.3,.4)*(1-te(n,.6,.7)),c=ke(n,.32,.72);if(pe(i,0),ae(i,{lean:he.hatBow*c,nod:he.hatNod*c}),Ce(i,e,s?[r]:[]),pi(i,r,s,he.hatWrist.map((l,u)=>kt(l,he.hatRaised[u],a))),s&&i.aim(`hand_${r}`,i.rig.along.get(`hand_${r}`).clone().transformDirection(i.matrix(`hand_${r}`)).lerp(hE,s)),o){const l={y:Z[r]*he.hatTip*o};i.putAway("butler_bowler_hat"),i.wearProp("bowler_hat",dE(i,r,o,l).toArray(),l)}Ze(i,"amused",c)}function dE(i,e,t,n){const s=new b(Z[e]*fd.hat.brim,0,0).applyMatrix4(Ps(0,n.y,0)),o=TS(i,e,[he.hatFingers,0,0]).applyMatrix4(i.matrix("head").clone().invert()).sub(s).sub(i.rig.heads.get("head"));return new b(0,0,he.hatOn).lerp(o,t)}function pE(i,e,t){const{u:n}=an(t),s=it(e),r=Z[s],o=te(n,0,.2)*(1-te(n,.82,1)),a=te(n,.26,.36)*(1-te(n,.66,.76));pe(i,0),ae(i,{lean:he.monoclePeer*a,nod:he.monoclePeer*a,tilt:r*he.monocleTilt*a}),Ce(i,e,o?[s]:[]);const c=1-.35*a;pi(i,s,o,he.monocleWrist.map((h,d)=>d===2?h-.25*(1-c):h));const[l,u,f]=he.monocleWorn;n>.18&&n<.8?i.wearProp("monocle",[r*l,u,f]):o>.4&&i.holdUpright("monocle",s,[0,0,.2]),Ze(i,"startled",.6*a)}function mE(i,e,t){const{u:n,ready:s}=an(t),r=it(e),o=ke(n,.3,.42),a=ke(n,.5,.78);pe(i,0),ae(i,{lean:4*o,nod:-6*a}),Ce(i,e,s?[r]:[]);const c=he.toastWrist.map((l,u)=>kt(l,he.sipWrist[u],a)+(u===1?-he.toastClink*o:0));pi(i,r,s,c),s>.3&&i.holdUpright("champagne_flute",r,[0,0,.1],{x:he.sipTip*a,y:Z[r]*he.sipTip*a}),i.shutEyes(1-.7*a),o>.5&&Ze(i,"amused",o)}function gE(i,e,t){const{u:n,ready:s}=an(t),r=it(e),o=Z[r];pe(i,0),ae(i,{lean:-5*s,tilt:-o*8*s,turn:-o*6*s}),Ce(i,e,s?[r]:[]),pi(i,r,s,he.shakaWrist,{y:he.shakaWaggle*Te(Mt(n,.2,.8),he.shakaWaggles)*s}),s>.5&&i.holdUpright("shaka",r,[0,0,.32]),Ze(i,"amused",s)}function _E(i,e,t){const{u:n}=an(t),s=it(e),r=Z[s],o=te(n,0,.15)*(1-te(n,.15,.3)),a=te(n,.72,.86)*(1-te(n,.86,1)),c=n>.22&&n<.82,l=te(n,.28,.38)*(1-te(n,.66,.76));pe(i,0),ae(i,{lean:-he.shadesLean*l,tilt:r*he.shadesTilt*l,nod:6*l*Math.max(Te(Mt(n,.38,.66),2),0)});const u=Math.max(o,a);Ce(i,e,u?[s]:[]),pi(i,s,u,he.shadesWrist),c?i.wearProp("sunglasses",he.shadesWorn):u>.4&&i.holdUpright("sunglasses",s,[0,-.1,.25])}function xE(i,e,t){const{u:n,ready:s}=an(t),r=it(e),o=te(n,.18,.28)*(1-te(n,.66,.74)),a=ke(n,.66,.84);pe(i,0),ae(i,{nod:8*o*Math.max(Te(Mt(n,.28,.66),3),0)+6*a,tilt:Z[r]*5*o}),Ce(i,e,s?[r]:[]),pi(i,r,s,he.fireWrist,{y:25*a*Te(n,9)}),o>.02&&(i.holdUpright("flame",r,[0,0,.18]),Object.assign(i.props.get("flame"),{phase:n,size:he.fireSize*o})),Ze(i,a>.3?"startled":"amused",Math.max(o,a))}function vE(i,e,t){const{u:n,ready:s}=an(t),r=it(e),o=ke(n,.35,.6);pe(i,0),ae(i,{nod:14*o,lean:3*s}),Ce(i,e,s?[r]:[]),pi(i,r,s,he.thumbWrist,{y:0}),s>.5&&(i.holdUpright("thumb",r,[0,0,.3]),kr(i)),Ze(i,"amused",o)}function yE(i,e,t){const{u:n}=an(t),s=it(e),r=te(n,0,.14)*(1-te(n,.24,.36)),o=te(n,.26,.38)*(1-te(n,.8,.95)),a=ke(n,.38,.58)-ke(n,.58,.8);pe(i,0),ae(i,{lean:he.peerLean*o,nod:6*o,turn:he.peerTurn*a}),Ce(i,e,r?[s]:[]);const[c,l,u]=he.glassesWrist;pi(i,s,r,[c,l,u+.08*te(n,.12,.22)]),Ze(i,"reading",o)}function ME(i,e,t){const{u:n,ready:s}=an(t),r=ke(n,.25,.8);pe(i,0),ae(i,{lean:he.thanksBow*r,nod:10*r}),Ce(i,e,s?Object.keys(Z):[]),s&&i.putAway(...It);for(const[o,a]of Object.entries(Z))$t(i,o,s,he.prayerWrist,{x:he.prayerRoll*s,y:-a*90*s,z:0});i.shutEyes(1-.85*r)}function SE(i,e,t){const{u:n,ready:s}=an(t),r=it(e),o=ke(n,he.popAt,he.popAt+.2);i.lift("root",{z:he.popHop*o}),pe(i,0),ae(i,{lean:-4*o,nod:-8*o}),Ce(i,e,s?[r]:[]),pi(i,r,s,he.popperWrist),s>.4&&(i.holdUpright("party_popper",r,[0,0,.1],{y:Z[r]*25}),i.props.get("party_popper").burst=Mt(n,he.popAt,.95),kr(i)),Ze(i,"amused",o)}function EE(i,e,t){const{u:n,ready:s}=an(t),r=it(e),o=Math.max(Te(Mt(n,.25,.75),2),0);pe(i,0),ae(i,{lean:-5*s,twist:-Z[r]*10*s,tilt:Z[r]*4*s,nod:-4*s}),Ce(i,e,s?[r]:[]),s&&qt(i,r,s,{...he.flex,bend:he.flex.bend+he.flexPump*o}),Ze(i,"angry",.6*o)}function bE(i,e,t){const{u:n,ready:s}=an(t),r=it(e),o=Math.max(Te(Mt(n,.25,.75),2),0);i.lift("root",{z:he.trophyHop*o}),pe(i,0),ae(i,{nod:-12*s,lean:-4*s}),Ce(i,e,s?[r]:[]),s&&qt(i,r,s,he.trophy),s>.4&&(i.holdUpright("trophy",r,[0,0,.3]),kr(i)),Ze(i,"amused",s)}function wE(i,e,t){const{u:n,ready:s}=an(t),r=tr(e)[0]||it(e),o=Math.max(Te(Mt(n,.25,.75),2),0);pe(i,0),ae(i,{lean:-4*s,nod:-10*s}),Ce(i,e,s?[r]:[]),s&&qt(i,r,s,{...he.sword,y:he.sword.y-he.swordThrust*o}),s&&i.putAway("squire_quill"),s>.4&&(i.holdUpright("sword",r,[0,0,.15],{x:-15}),kr(i)),Ze(i,"angry",s)}function TE(i,e,t){const{u:n,ready:s}=an(t),r=[...e.shield][0];if(!r)return oa(i,e,t);const o=ke(n,he.shieldBump,he.shieldBump+.12);cs(i,he.shieldCrouch*s),pe(i,0),ae(i,{lean:8*s-8*o,nod:6*s}),Ce(i,e,s?[r]:[]);const[a,c,l]=he.shieldWrist;$t(i,r,s,[a,c+.08*o,l]),i.keep.add("squire_shield"),Ze(i,o>.3?"startled":"angry",s)}function AE(i,e,t){const{u:n,ready:s}=an(t),r=tr(e)[0]||it(e),o=ke(n,.35,.75);pe(i,0),ae(i,{nod:12*o,lean:4*o}),Ce(i,e,s?[r]:[]),$t(i,r,s,he.castleWrist,{x:-30*s}),s&&i.putAway("squire_quill"),s>.4&&(i.holdUpright("castle",r,[0,0,.12]),kr(i)),Ze(i,"amused",o)}const jt={high:[1,-.25,2.92],stampHigh:[1.1,-.42,2.7],stampDown:[1.18,-.46,1.72],sign:[.5,-.25,3],signWaggle:.1,scroll:[.3,-.84,2.28],drawer:[1.16,-.4,1.66],drop:.12,binoculars:[.24,-.8,2.36],sweep:30,torch:[1.1,-.55,1.88],torchSweep:.16,corner:[1,-.42,1.36],lift:.3,crouch:.6,peekLean:34},rd=(i,e,t)=>i.map((n,s)=>kt(n,e[s],t)),la=i=>i.putAway(...[...It].filter(e=>!sa.has(e)));function Fn(i,e,t,n,s={}){const r=it(e);Ce(i,e,t?[r]:[]),$t(i,r,t,n,s),t&&la(i)}function RE(i,e,t){const n=_e.post_dove,s=Ct(t,n.frames),r=Ge(s,n.raise)*(1-Ge(s,[.86,1]));pe(i,0),ae(i,{lean:-6*r,nod:-16*r}),Fn(i,e,Ge(s,n.raise)*(1-Ge(s,n.lower)),jt.high),Ze(i,"amused",Ge(s,[n.taken,n.taken+.1])*(1-Ge(s,[.86,1])))}function CE(i,e,t){const n=_e.stamp,s=Ct(t,n.frames),r=Ge(s,n.lift)*(1-Ge(s,[n.up[1],n.sinks[0]])),o=Ge(s,n.down)*(1-Ge(s,n.up));cs(i,.08*o),pe(i,0),ae(i,{lean:4+8*o,nod:10*r}),Fn(i,e,r,rd(jt.stampHigh,jt.stampDown,o),{x:-20*o}),Ze(i,"amused",Ge(s,[n.stamped,n.up[1]])*(1-Ge(s,n.sinks)))}function PE(i,e,t){const n=_e.ask_sign,s=Ct(t,n.frames),r=Ge(s,n.raise)*(1-Ge(s,n.lower)),o=Te(Mt(s,...n.waggle),n.waggles)*ke(s,...n.waggle),[a,c,l]=jt.sign;pe(i,0),ae(i,{nod:-10*r,tilt:4*o}),Fn(i,e,r,[a+jt.signWaggle*o,c,l]),Ze(i,"worried",r)}function LE(i,e,t){const n=_e.scroll,s=Ct(t,n.frames),r=Ge(s,n.unrolls)*(1-Ge(s,n.rolls));pe(i,0),ae(i,{nod:14*r,lean:3*r}),Fn(i,e,Ge(s,n.raise)*(1-Ge(s,n.lower)),jt.scroll,{x:-20}),Ze(i,"reading",r)}function IE(i,e,t){const n=_e.file_card,s=Ct(t,n.frames),r=Ge(s,n.reach)*(1-Ge(s,n.back)),[o,a,c]=jt.drawer;pe(i,0),ae(i,{lean:10*r,nod:14*r}),Fn(i,e,r,[o,a,c-jt.drop*Ge(s,n.filed)])}function DE(i,e,t){const n=_e.party_horn,s=Ct(t,n.frames),r=vd(s),o=Ge(s,n.turns)*(1-Ge(s,n.back));pe(i,0),ae(i,{turn:Z[it(e)]*n.turn*o}),Fn(i,e,Ge(s,n.raise)*(1-Ge(s,n.lower)),k.whistleWrist),i.shutEyes(1-.6*r)}const oc={sink:2.1,hop:.75,leap:1};function NE(i,e,t){const n=_e.pack_box,{into:s,out:r}=fl(n,t),o=ke(s,...n.hop),a=Ge(s,n.into)*(1-Ge(r,[n.pops,n.pops+.2])),c=ke(r,...n.leap);i.lift("root",{z:oc.hop*o-oc.sink*a+oc.leap*c}),pe(i,0),ae(i,{lean:6*o,nod:12*a-10*c}),xn(i,e,0,60*o+120*c),ki(i,.7*o+.6*c),i.putAway(...It),Ze(i,"amused",c)}function UE(i,e,t){const n=_e.press,{into:s,out:r}=fl(n,t),o=Ge(s,[.2,.55])*(1-Ge(r,[.2,.5]));pe(i,0),ae(i,{nod:-8*o}),xn(i,e,0,140*o),i.putAway(...It),i.shutEyes(1-.8*Ge(s,n.squashes)*(1-Ge(r,n.frees)))}function OE(i,e,t){const{held:n,into:s,out:r}=fl(_e.vacuum,t),[o,a,c]=jt.torch;pe(i,0),ae(i,{lean:8,nod:14,turn:-Z[it(e)]*14}),Fn(i,e,s*(1-r),[o,a,c-.12*Te(n??0,2)],{x:-10})}const bi={intro:18,hold:12,outro:6,fps:12,taps:6,tap:18,point:[1.25,-.45,1.75],bounce:.14,wiggle:7,sparkle:.25};function FE(i,e,t){const{intro:n,hold:s,outro:r,taps:o,tap:a,point:c,bounce:l,wiggle:u,sparkle:f}=bi,h=t*(n+s+r),d=h<n?Math.sin(Math.PI*h/n):0,m=h<n?te(h/n,.7,1):1-te((h-n-s)/r,0,1),_=h>=n&&h<n+s?(h-n)/s:null,g=_===null?0:Math.abs(Math.sin(2*Math.PI*_)),p=Te(h/n,o);i.lift("root",{z:l*g}),pe(i,0),ae(i,{lean:6*m,nod:14*m+4*g,twist:u*(_===null?d*p:Te(_,2))}),i.posture==="stand"&&(i.turn("foot_l",{x:a*d*Math.max(p,0)}),i.turn("foot_r",{x:a*d*Math.max(-p,0)})),Ce(i,e,m?[...e.free]:[]);for(const v of e.free)$t(i,v,m,[c[0],c[1],c[2]+.1*g*Z[v]],{x:40});m&&la(i);const M=Math.min(h/4,1)*(1-Mt(h,n+s,n+s+r));i.starEyes(M*(1+f*Math.abs(Te(h/6))))}function BE(i,e,t){const n=_e.fume,s=Ct(t,n.frames),r=ke(s,n.crushed[0],n.crushed[1]+.06),o=Ge(s,[n.mad[0],n.mad[0]+.06])*(1-Ge(s,[n.mad[1],1])),a=Te(Mt(s,...n.mad),n.stamps/2);cs(i,.14*r),i.lift("root",{z:.12*o*Math.abs(a)}),pe(i,0),ae(i,{lean:16*r+6*o,nod:28*r+10*o,tilt:5*o*Te(s,14)}),Ce(i,e,o?[...e.free]:[]);for(const c of e.free)qt(i,c,o,{y:40,z:-25,bend:95});if(i.posture==="stand")for(const[c,l]of[["l",1],["r",-1]]){const u=o*Math.max(l*a,0);i.turn(`thigh_${c}`,{x:-34*u,y:l*18*u}),i.turn(`shin_${c}`,{x:52*u})}r>o?Ze(i,"worried",r):Ze(i,"angry",o)}const zn={frames:24,fps:12,head:55,body:20,up:24},ac=(i,e)=>(t,n,s)=>{const r=Ct(s,zn.frames),o=te(r,.05,.3)*(1-te(r,.7,.95));ae(t,{twist:i*zn.body*o,turn:i*zn.head*o,nod:-e*zn.up*o}),Ce(t,n)},ul={frames:6,fps:20},Mn={frames:48,fps:12,trip:[0,.14],down:[.05,.11],bounce:[.11,.18],shake:[.3,.58],shakes:3,up:[.62,.8],hop:[.8,.96],drop:.74};function kE(i,e,t){const n=Ct(t,Mn.frames),s=te(n,...Mn.down)*(1-te(n,...Mn.up)),r=ke(n,...Mn.trip),o=Te(Mt(n,...Mn.shake),Mn.shakes)*ke(n,...Mn.shake),a=ke(n,...Mn.hop);if(i.lift("root",{z:-Mn.drop*s+.1*ke(n,...Mn.bounce)+.16*a}),i.posture==="stand")for(const c of Object.keys(Z))i.turn(`shin_${c}`,{x:90*s});ae(i,{lean:12*s+10*r*(1-s),nod:12*s,turn:26*o}),xn(i,e,0,100*r*(1-s)+60*a,8*r),i.putAway(...It),a>.1?Ze(i,"amused",a):Ze(i,s>.5?"worried":"startled",Math.max(s,r))}const cc={hands:[.8,.18,1.42],lean:-7,nod:-3};function zE(i,e,t){pe(i,t),ae(i,{lean:cc.lean,nod:cc.nod+2*Te(t)});const[n,s,r]=cc.hands;Ce(i,e,[...e.free]);for(const o of e.free)Ut(i,o,1,i.carried(new b(Z[o]*n,s,r)),new b(1,.6,.2)),i.face(`hand_${o}`,{z:-Z[o]*90,x:-70});e.free.size&&la(i),i.swing(.6*Te(t))}function HE(i,e,t){const n=Te(t);pe(i,0),ae(i,{lean:8,nod:-12}),xn(i,e,0,110+20*n),ki(i,.6+.2*n)}const lc={at:[.3,-.8,2.45],swats:4,giggle:4};function VE(i,e,t){const n=t*lc.swats,s=Math.floor(n)%2?"l":"r",r=Math.sin(Math.PI*(n%1));pe(i,t),ae(i,{tilt:lc.giggle*Math.sin(2*Math.PI*n*2),nod:-3}),i.putAway(...It),Ce(i,e,Object.keys(Z));for(const o of Object.keys(Z)){const[a,c,l]=lc.at;Ut(i,o,o===s?r:.25,new b(Z[o]*a,c,l),new b(1,-.4,-.3))}i.squeezeEyes(1)}const bo={up:[1.2,-.3,2.85],down:[.95,-.25,1.3],sway:12,bounce:.18};function GE(i,e,t){const{beats:n}=_e.disco,s=t*n,r=Math.floor(s)%2?1:-1,o=Math.sin(Math.PI*Math.min(s%1*3,1)*.5),a=Ge(t,[0,.06])*(1-Ge(t,[.94,1]));pe(i,t),ae(i,{tilt:r*bo.sway*o*a,nod:-4}),i.putAway(...It),Ce(i,e,Object.keys(Z));for(const c of Object.keys(Z)){const l=Z[c],[u,f,h]=l===r?bo.up:bo.down;Ut(i,c,a,new b(l*u,f,h),new b(1,-.3,l===r?.2:-.6))}Bi(i,bo.bounce*Math.abs(Math.sin(Math.PI*s))*a),Ze(i,"amused",a)}const uc={trigger:[.5,-.4,1.7],fore:[.12,-.45,1.85],behind:[.45,.45,1.45]};function WE(i,e,t){const n=_e.bug_shot,s=(n.draw[0]+n.draw[1])/2,r=Ge(t,[n.draw[0],s])*(1-Ge(t,[s,n.draw[1]])),o=Ge(t,[s,n.draw[1]])*(1-Ge(t,[n.drops[0]+.05,n.drops[0]+.2])),a=Math.min(Math.max((t-n.shots[0])/(n.shots[1]-n.shots[0]),0),1)*n.count,c=t>n.shots[0]&&t<n.shots[1]?Math.max(0,1-a%1*3):0,l=it(e),u=Z[l];pe(i,t),ae(i,{twist:-u*25*o,lean:4*o-5*c}),i.putAway(...It),Ce(i,e,Object.keys(Z));const f=(h,d=u)=>new b(d*h[0],h[1],h[2]);r>o?Ut(i,l,r,f(uc.behind),new b(1,.5,-.5)):Ut(i,l,o,f(uc.trigger),new b(1,-.2,-.4)),Ut(i,l==="l"?"r":"l",o,f(uc.fore),new b(-1,-.4,-.4)),Ze(i,"amused",o)}const XE=[.42,-.55,1.55],qE=[.45,.45,1.45];function YE(i,e,t){const n=_e.pogo,s=Ge(t,[n.draw[0],n.draw[1]*.5])*(1-Ge(t,[n.draw[1]*.5,n.draw[1]])),r=Ge(t,[n.draw[1]*.6,n.draw[1]])*(1-Ge(t,n.drop)),o=Math.min(Math.max((t-n.bounces[0])/(n.bounces[1]-n.bounces[0]),0),1)*n.count,a=t>n.bounces[0]&&t<n.bounces[1]?1-Math.sin(Math.PI*(o%1)):0;pe(i,t),ae(i,{lean:6*r,nod:-6*r}),i.putAway(...It),Ce(i,e,Object.keys(Z));const[c,l,u]=XE,[f,h,d]=qE;for(const m of Object.keys(Z)){const _=Z[m];m==="r"&&s>r?Ut(i,m,s,new b(_*f,h,d),new b(1,.5,-.5)):Ut(i,m,r,new b(_*c,l,u),new b(1,-.2,-.4))}Bi(i,.35*a*r),Ze(i,"amused",r)}const jE=[_e.rope_swing.ties*Oi/2,-.1,2.6];function $E(i,e,t){const n=_d(t)/_e.rope_swing.sway;pe(i,t),ae(i,{lean:-5*n,nod:-4}),i.putAway(...It);const[s,r,o]=jE;Ce(i,e,Object.keys(Z));for(const a of Object.keys(Z))Ut(i,a,1,i.carried(new b(Z[a]*s,r,o)),new b(1,0,-.4)),i.face(`hand_${a}`,{z:-Z[a]*90});i.swing(1.2*n),Ze(i,"amused")}function KE(i,e,t){const n=Te(t);pe(i,t),ae(i,{nod:-6,tilt:3*n}),xn(i,e,0,150),i.putAway(...It),ki(i,.15,6*n),Ze(i,"amused")}function ZE(i,e,t){const n=jt.sweep*Te(t,_e.binoculars.sweep);ae(i,{twist:n,nod:-4});const s=it(e),[r,o,a]=jt.binoculars,c=new b(Z[s]*r,o,a).applyAxisAngle(new b(0,0,1),hn(n));Fn(i,e,1,[Z[s]*c.x,c.y,c.z],{x:-60})}function JE(i,e,t){const n=Qf(t),[s,r,o]=jt.torch;pe(i,0),ae(i,{lean:10,nod:18,turn:-Z[it(e)]*20}),Fn(i,e,1,[s,r,o-jt.torchSweep*n],{x:-10}),Ze(i,"reading")}function QE(i,e,t){const n=_e.peek_under,s=Ge(t,[0,n.lift[0]+.1])*(1-Ge(t,[n.down[1],1])),r=Ge(t,n.lift)*(1-Ge(t,n.down)),o=Ge(t,n.peek)*(1-Ge(t,n.down));cs(i,jt.crouch*s),pe(i,0),ae(i,{lean:jt.peekLean*s,nod:14*s+10*o,turn:-Z[it(e)]*24*o,tilt:8*o});const[a,c,l]=jt.corner;Fn(i,e,s,[a,c,l+jt.lift*r]),Ze(i,"reading",o)}function eb(i,e,t){const n=it(e),s=Z[n],[r,o,a]=Uo;pe(i,t),ae(i,{lean:4,nod:14+3*Te(t),turn:-s*6,tilt:-s*4}),zl(i,e,1,[r,o,a+.03*Math.max(Te(t,2),0)]),EM(i,n),i.holdLaptop(),Ze(i,"reading")}function tb(i,e,t){const{u:n,ready:s}=Tn(t,k.greetingFrames),r=ke(n,.3,.75);pe(i,0),ae(i,{lean:-4*s,nod:-10*s}),Fn(i,e,s,rd([.7,-.62,2.34],[.3,-.84,2.38],r),{x:-40}),i.shutEyes(1-.6*r)}function nb(i,e,t){const{back:n}=i.sky??{back:0};i.lift("root",{y:Ti.step*n,z:Ti.hop*Math.sin(Math.PI*n)}),pe(i,t),ae(i,{lean:-Ti.lean*n});const s=it(e);Ce(i,e,[s]),Vf(i,s,t),la(i),Ze(i,"amused")}const Bh={sit:{under:DM,over:NM},walk:{under:Gf,over:Wf}},He=["stand","sit","walk"],vt=["stand"],kh=["hang"],wo=["sit"],Zb=[{name:"idle",frames:24,fps:8,loops:!0,leaves:8,postures:He,pose:oa},{name:"nod",frames:10,fps:12,loops:!1,postures:He,pose:vM},{name:"shake",frames:12,fps:12,loops:!1,postures:He,pose:yM},{name:"wave",frames:12,fps:12,loops:!0,postures:He,pose:MM},{name:"think",frames:12,fps:6,loops:!0,postures:He,pose:SM},{name:"celebrate",frames:12,fps:10,loops:!0,postures:vt,pose:bM},{name:"sleep",frames:k.yawnFrames+wr,intro:k.yawnFrames,leaves:wr,fps:6,loops:!0,postures:He,marks:{mark:"Z",frames:[[k.yawnFrames,k.yawnFrames+wr]]},pose:wM},{name:"walk",frames:12,fps:12,loops:!0,interruptible:!0,postures:vt,pose:TM},{name:"walk_in",frames:40,fps:12,loops:!1,postures:vt,pose:VM},{name:"run_in",frames:28,fps:12,loops:!1,postures:vt,pose:GM},{name:"pull_ups",frames:24,fps:10,loops:!0,postures:vt,pose:WM},{name:"hang_l",frames:24,fps:8,loops:!0,leaves:8,postures:kh,pose:Ch("l")},{name:"hang_r",frames:24,fps:8,loops:!0,leaves:8,postures:kh,pose:Ch("r")},{name:"enter",frames:36,fps:12,loops:!1,postures:vt,pose:yS},{name:"exit",frames:28,fps:12,loops:!1,postures:vt,pose:MS},{name:"search",frames:80,fps:10,loops:!0,postures:He,pose:bS},{name:"read",frames:cl,fps:ut.fps,loops:!0,intro:ut.intro,outro:ut.outro,leaves:ut.pageEvery,postures:He,pose:AS},{name:"write",frames:qo,intro:k.intro,outro:k.outro,leaves:k.hold,fps:k.fps,loops:!0,postures:He,pose:FS},{name:"waiting",frames:ll,intro:Qt.intro,outro:Qt.outro,leaves:Qt.hold,fps:k.fps,loops:!0,postures:["stand","sit"],pose:LS},{name:"compacting",frames:qo,intro:k.intro,outro:k.outro,leaves:k.hold,fps:k.compactFps,loops:!0,postures:He,pose:BS},{name:"yawn",frames:k.yawnFrames,fps:k.fps,loops:!1,postures:He,pose:id},{name:"rest",frames:bt.frames,fps:bt.fps,loops:!1,postures:vt,marks:{mark:"♪",frames:bt.tunes.map(i=>i.map(e=>e*bt.frames))},pose:DS},{name:"whistle",frames:k.pastimeFrames,fps:k.fps,loops:!1,postures:He,voices:["coach"],pose:Oh},{name:"sip",frames:k.pastimeFrames,fps:k.fps,loops:!1,postures:He,voices:["colleague"],pose:NS},{name:"headphones",frames:k.pastimeFrames,fps:k.fps,loops:!1,postures:He,voices:["homie"],pose:US},{name:"shield_polish",frames:k.pastimeFrames,fps:k.fps,loops:!1,postures:He,voices:["squire"],pose:OS},{name:"bow",frames:k.greetingFrames,fps:k.fps,loops:!1,postures:He,voices:["butler"],pose:kS},{name:"salute",frames:k.greetingFrames,fps:k.fps,loops:!1,postures:He,voices:["squire"],pose:zS},{name:"startled",frames:k.hopFrames,fps:k.fps,loops:!1,postures:He,pose:HS},{name:"stumble",frames:k.stumbleFrames,fps:k.fps,loops:!1,postures:["walk"],pose:VS},{name:"glance",frames:k.greetingFrames,fps:k.fps,loops:!1,postures:He,pose:GS},{name:"work",frames:Nn.blows*Nn.blowFrames,fps:Nn.fps,loops:!0,postures:["stand","sit"],pose:XS},{name:"point",frames:12,fps:8,loops:!0,postures:He,pose:ZS},{name:"watch",frames:8,fps:8,loops:!0,cuts:!0,postures:["stand","sit"],pose:$S},{name:"push",frames:6,fps:12,loops:!0,legs:!0,postures:["walk","stand"],pose:KS},{name:"jump",frames:16,fps:20,loops:!1,postures:vt,pose:JS},{name:"tickle_swat",frames:24,fps:16,loops:!1,cuts:!0,ownLook:!0,postures:He,pose:VE},{name:"disco",frames:_e.disco.frames,fps:_e.disco.fps,loops:!1,ownLook:!0,postures:vt,pose:GE},{name:"bug_shot",frames:_e.bug_shot.frames,fps:_e.bug_shot.fps,loops:!1,postures:He,pose:WE},{name:"pogo",frames:_e.pogo.frames,fps:_e.pogo.fps,loops:!1,postures:vt,pose:YE},{name:"fall",frames:12,fps:12,loops:!1,interruptible:!0,postures:vt,pose:nE},{name:"backflip",frames:22,fps:20,loops:!1,postures:vt,pose:tE},{name:"land",frames:ul.frames,fps:ul.fps,loops:!1,postures:vt,pose:iE},{name:"type",frames:24,fps:8,loops:!0,leaves:8,postures:wo,pose:OM},{name:"joy",frames:20,fps:14,loops:!1,postures:He,pose:FM},{name:"dismay",frames:28,fps:10,loops:!1,postures:He,pose:BM},{name:"look_around",frames:24,fps:10,loops:!1,postures:He,pose:kM},{name:"polish",frames:40,fps:12,loops:!1,postures:He,voices:["butler"],pose:PS},{name:"stretch",frames:24,fps:8,loops:!1,postures:He,pose:zM},{name:"squire_chase",frames:24,fps:12,loops:!1,postures:vt,pose:sE},{name:"pointed",frames:20,fps:10,loops:!1,postures:vt,pose:uE},{name:"hat_tip",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["butler"],pose:fE},{name:"monocle",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["butler"],pose:pE},{name:"toast",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["butler"],pose:mE},{name:"shaka",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["homie"],pose:gE},{name:"shades",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["homie"],pose:_E},{name:"fire",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["homie"],pose:xE},{name:"thumbs_up",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["colleague"],pose:vE},{name:"peer",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["colleague"],pose:yE},{name:"thanks",frames:he.frames,fps:he.fps,loops:!1,postures:He,pose:ME},{name:"party_popper",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["coach"],pose:SE},{name:"flex",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["coach"],pose:EE},{name:"trophy",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["coach"],pose:bE},{name:"sword",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["squire"],pose:wE},{name:"shield_up",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["squire"],pose:TE},{name:"castle",frames:he.frames,fps:he.fps,loops:!1,postures:He,voices:["squire"],pose:AE},{name:"post_dove",frames:_e.post_dove.frames,fps:_e.post_dove.fps,loops:!1,postures:He,pose:RE},{name:"stamp",frames:_e.stamp.frames,fps:_e.stamp.fps,loops:!1,postures:vt,pose:CE},{name:"ask_sign",frames:_e.ask_sign.frames,fps:_e.ask_sign.fps,loops:!1,postures:He,pose:PE},{name:"whistle_runner",frames:k.pastimeFrames,fps:k.fps,loops:!1,postures:vt,pose:Oh},{name:"scroll",frames:_e.scroll.frames,fps:_e.scroll.fps,loops:!1,postures:He,pose:LE},{name:"file_card",frames:_e.file_card.frames,fps:_e.file_card.fps,loops:!1,postures:vt,pose:IE},{name:"party_horn",frames:_e.party_horn.frames,fps:_e.party_horn.fps,loops:!1,postures:He,pose:DE},{name:"pack_box",frames:_e.pack_box.intro+_e.pack_box.hold+_e.pack_box.outro,intro:_e.pack_box.intro,outro:_e.pack_box.outro,leaves:_e.pack_box.hold,fps:_e.pack_box.fps,loops:!0,postures:vt,pose:NE},{name:"press",frames:_e.press.intro+_e.press.hold+_e.press.outro,intro:_e.press.intro,outro:_e.press.outro,leaves:_e.press.hold,fps:_e.press.fps,loops:!0,postures:He,pose:UE},{name:"vacuum",frames:_e.vacuum.intro+_e.vacuum.hold+_e.vacuum.outro,intro:_e.vacuum.intro,outro:_e.vacuum.outro,leaves:_e.vacuum.hold,fps:_e.vacuum.fps,loops:!0,postures:vt,pose:OE},{name:"eager",frames:bi.intro+bi.hold+bi.outro,intro:bi.intro,outro:bi.outro,leaves:bi.hold,fps:bi.fps,loops:!0,postures:vt,pose:FE},{name:"fume",frames:_e.fume.frames,fps:_e.fume.fps,loops:!1,postures:vt,pose:BE},{name:"look_left",frames:zn.frames,fps:zn.fps,loops:!1,postures:He,pose:ac(-1,0)},{name:"look_right",frames:zn.frames,fps:zn.fps,loops:!1,postures:He,pose:ac(1,0)},{name:"look_up",frames:zn.frames,fps:zn.fps,loops:!1,postures:He,pose:ac(0,1)},{name:"tumble",frames:Mn.frames,fps:Mn.fps,loops:!1,postures:vt,pose:kE},{name:"ledge_sit",frames:32,fps:8,loops:!0,leaves:8,postures:wo,pose:zE},{name:"hop_up",frames:8,fps:16,loops:!0,interruptible:!0,cuts:!0,postures:vt,pose:HE},{name:"rope_swing",frames:_e.rope_swing.intro+_e.rope_swing.hold+_e.rope_swing.outro,intro:_e.rope_swing.intro,outro:_e.rope_swing.outro,leaves:_e.rope_swing.hold,fps:_e.rope_swing.fps,loops:!0,postures:wo,pose:$E},{name:"chute",frames:_e.chute.frames,fps:_e.chute.fps,loops:!0,interruptible:!0,cuts:!0,postures:vt,pose:KE},{name:"binoculars",frames:_e.binoculars.frames,fps:_e.binoculars.fps,loops:!0,postures:He,pose:ZE},{name:"flashlight",frames:_e.flashlight.frames,fps:_e.flashlight.fps,loops:!0,postures:vt,pose:JE},{name:"peek_under",frames:_e.peek_under.frames,fps:_e.peek_under.fps,loops:!0,postures:vt,pose:QE},{name:"type_ponder",frames:24,fps:6,loops:!0,leaves:8,postures:wo,pose:eb},{name:"wipe_brow",frames:k.greetingFrames,fps:k.fps,loops:!1,postures:He,pose:tb},{name:"wave_up",frames:12,fps:12,loops:!0,cuts:!0,postures:["stand","sit"],pose:nb}],od=`
    #include <common>
    #include <skinning_pars_vertex>
    attribute vec3 hullNormal;
    uniform float push;
    uniform float openness;
    uniform float eyeMiddle;
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
        #include <skinning_vertex>
        transformed += normalize(objectNormal) * push;
        worldNormal = normalize(mat3(modelMatrix) * objectNormal);
        worldPosition = (modelMatrix * vec4(transformed, 1.0)).xyz;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(transformed, 1.0);
    }
`,ib=`
    uniform vec3 colour;
    uniform vec3 light;
    uniform vec3 shade;
    uniform float litFrom;
    varying vec3 worldNormal;

    void main() {
        vec3 normal = normalize(worldNormal);
        if (!gl_FrontFacing) {
            normal = -normal;
        }
        float lit = step(litFrom, dot(normal, light));
        gl_FragColor = vec4(colour * mix(shade, vec3(1.0), lit), 1.0);
        #include <colorspace_fragment>
    }
`,hc={pitch:.1,gap:.24,dark:.3},sb=`
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
`;function rb(i){const e=cd(i);e.fragmentShader=sb;const t=new on().setFromBufferAttribute(i.geometry.attributes.position),n=t.getCenter(new b),s=t.getSize(new b).multiplyScalar(.5);return Object.assign(e.uniforms,{glow:{value:new b},lit:{value:0},across:{value:0},open:{value:0},flash:{value:0},core:{value:Sd.core},middle:{value:new ie(n.x,n.y)},extent:{value:new ie(s.x,s.y)},pitch:{value:hc.pitch},gap:{value:hc.gap},dark:{value:hc.dark}}),e}const ob=`
    uniform vec3 colour;

    void main() {
        gl_FragColor = vec4(colour, 1.0);
        #include <colorspace_fragment>
    }
`;function ad(i,e){const t=i.geometry.attributes.position;let n=0;for(let s=0;s<t.count;s++)n+=t.getY(s)/t.count;return{push:{value:e/i.getWorldScale(new b).x},openness:{value:1},eyeMiddle:{value:n}}}function cd(i){const{r:e,g:t,b:n}=i.material.color;return new Vn({vertexShader:od,fragmentShader:ib,side:mn,uniforms:{...ad(i,0),colour:{value:new b(e,t,n)},light:{value:eM.clone().normalize().applyMatrix4(Qs)},shade:{value:nM},litFrom:{value:tM}}})}function ab(i){return new Vn({vertexShader:od,fragmentShader:ob,side:sn,defines:{HULL:""},uniforms:{...ad(i,sM),colour:{value:iM}}})}const cb=-.5;function lb(i){const e=i.attributes.position,t=Array.from({length:e.count},(o,a)=>new b().fromBufferAttribute(i.attributes.normal,a)),n=new Map,s=o=>`${e.getX(o).toFixed(5)},${e.getY(o).toFixed(5)},${e.getZ(o).toFixed(5)}`;for(let o=0;o<e.count;o++){const a=n.get(s(o))??[];a.push(o),n.set(s(o),a)}const r=new Float32Array(e.count*3);for(let o=0;o<e.count;o++){const a=new b;for(const c of n.get(s(o)).filter(l=>t[o].dot(t[l])>cb))a.add(t[c]);a.normalize().toArray(r,o*3)}i.setAttribute("hullNormal",new Xt(r,3))}function ws(i,e){const t=new Set;for(const n of i.filter(s=>e.has(s.userData.item)))t.add(new on().setFromObject(n).getCenter(new b).x>=0?"l":"r");return t}function ub(i){const e=[];i.traverse(a=>a.isBone&&e.push(a));const t=new Map(e.map(a=>[a.name,a.parent.isBone?a.parent.name:""])),n=new Map(e.map(a=>[a.name,a.matrixWorld.clone()])),s=new Map(e.map(a=>[a.name,Wo(new b().setFromMatrixPosition(a.matrixWorld))])),r=new Map(e.map(a=>[a.name,new b().setFromMatrixColumn(a.matrixWorld,1).transformDirection(ra)])),o=[];return i.traverse(a=>{!a.isSkinnedMesh||!a.name.startsWith("eye_")||!a.userData.hull||o.push(Wo(new on().setFromBufferAttribute(a.geometry.attributes.position).getCenter(new b).applyMatrix4(a.matrixWorld)))}),{bones:e,order:e.map(a=>a.name),parents:t,rest:n,heads:s,along:r,eyes:o}}async function hb(i){const e=await fetch(i);if(e.ok)return e.arrayBuffer();const t=await fetch(`${i}.txt`).then(n=>n.text());return Uint8Array.from(atob(t),n=>n.charCodeAt(0)).buffer}async function Jb(i,e,t){const[n,s]=await Promise.all([hb(i),fetch(e).then(a=>a.json())]),r=t==="bare",o=new Set((r?[]:s.outfits[t]).flatMap(a=>s.assets[a].hide_base_parts));return db(n,t,Jy,a=>!o.has(a.name)&&!(r&&a.userData.item))}const fb={butler:dy};async function db(i,e,t,n=()=>!0){const r=(await new py().setDRACOLoader(new $y().setDecoderPath(t)).parseAsync(i,"")).scene;r.updateMatrixWorld(!0);const o=[];r.traverse(T=>T.isSkinnedMesh&&o.push(T));const a=(fb[e]??(T=>T))(o),c={materials:[],shapes:[],hearts:[],stars:[],squeezed:[]},l=[],u=[];for(const T of a){T.visible=n(T)&&!fM.has(T.userData.item)&&T.userData.item!==tc&&T.userData.item!==nc,lb(T.geometry);const R=new Tl(T.geometry,ab(T));R.bind(T.skeleton,T.bindMatrix),R.visible=T.visible,T.userData.hull=R,R.userData.item=T.userData.item,R.frustumCulled=T.frustumCulled=!1,T.material=T.name===dc?rb(T):cd(T),T.name===dc&&l.push(T.material),T.name===dc&&u.push(R),T.parent.add(R),R.position.copy(T.position),R.quaternion.copy(T.quaternion),R.scale.copy(T.scale),T.name.startsWith("eye_")&&(T.material.userData.colour=T.material.uniforms.colour.value.toArray(),c.materials.push(T.material,R.material),c.shapes.push(T,R),c.hearts.push(fc(T,Lb,Db)),c.stars.push(fc(T,Nb,Ob)),c.squeezed.push(Object.assign(fc(T,Fb,Bb),{userData:{way:T.name==="eye_l"?-1:1}})))}const f=a.filter(T=>T.visible),h=ws(f,sa),d=a.filter(T=>T.userData.item===tc&&n(T)),m=a.filter(T=>T.userData.item===nc&&n(T)),_={voice:e,level:ws(f,zf),busy:h,carried:ws(f,It),free:new Set(Object.keys(Z).filter(T=>!h.has(T))),tablet:ws(d,new Set([tc])),cloth:ws(m,new Set([nc])),shield:ws(f,new Set(["squire_shield"]))},g=mb(),p=wb(),M=Mb();r.add(g,p,...M.values());const v=T=>T.flatMap(R=>[R,R.userData.hull]),x=f.filter(T=>It.has(T.userData.item)),L=v(f.filter(T=>T.userData.item));return{scene:r,rig:ub(r),stance:_,eyes:c,screens:l,visorHulls:u,laptop:g,book:p,propByName:M,props:[...M.values()],stowable:L,tablet:v(d),cloth:v(m),inHand:v(x)}}const pb={width:1.7,depth:.62,thickness:.1,open:105},_r={base:4672082,lid:2829880,screen:1776932,edge:11120056,mark:6186185},Ui=(i,e)=>{const t=new Gt(i,new _n({color:e,side:mn}));return t.frustumCulled=!1,t};function mb(){const{width:i,depth:e,thickness:t,open:n}=pb,s=(f,h,d,m)=>{const _=Ui(new Rt(h,d,m),f);return _.add(new Nr(new ea(_.geometry),new ns({color:_r.edge}))),_},r=s(_r.base,i,t,e);r.position.set(0,t/2,-e/2);const o=s(_r.lid,i,e,t);o.position.set(0,e/2,t/2);const a=Ui(new fi(i*.88,e*.82),_r.screen);a.position.set(0,e/2,-.002);const c=Ui(new is(e*.12,20),_r.mark);c.position.set(0,e/2,t+.002);const l=new un;l.position.y=t,l.rotation.x=hn(n-90),l.add(o,a,c);const u=new un;return u.matrixAutoUpdate=!1,u.visible=!1,u.add(r,l),u}const Ts={lights:[.144,.267,.389,.511],light:.047,vents:[.633,.711,.789,.867],vent:[.033,.49]},As={front:1842725,top:2895673,side:1184536,vent:329224,edge:4869724};function gb(i){const e=Hi.width*i,t=Math.asin(Hi.top/Hi.width),n=(Hi.height-Hi.top)*i/Math.cos(t)/Hi.units,[s,r,o]=[As.side,As.top,As.front].map(f=>new _n({color:f})),a=[],c=Array.from({length:Hi.units},(f,h)=>{const d=new Gt(new Rt(e,n,e),[s,s,r,s,o,s]);d.add(new Nr(new ea(d.geometry),new ns({color:As.edge}))),d.position.set(0,n*(h+.5),-e/2);const m=(_,g)=>(_.position.set(e*(g-.5),0,e/2+.002),d.add(_),_);return a.push(...Ts.lights.map(_=>m(new Gt(new is(e*Ts.light,12),new _n),_))),Ts.vents.forEach(_=>m(Ui(new fi(e*Ts.vent[0],n*Ts.vent[1]),As.vent),_)),d}),l=new un;l.rotation.x=t,l.add(...c);const u=new Hx;return u.add(l),u.updateMatrixWorld(!0),{scene:u,lights:a,bounds:new on().setFromObject(l)}}function _b(i,e,t){const n=new Ve(As.front);i.lights.forEach((s,r)=>{const o=new Ve().setRGB(...yd[e],Nt);s.material.color.copy(n.clone().lerp(o,Md(e,t,r%Ts.lights.length)))})}const xb={radius:.52,rim:.08,handle:.5,grip:.07},To={rim:2829880,lens:13625087,handle:4672082,edge:11120056},vb=40;function yb(i){const{radius:e,rim:t,handle:n,grip:s}=xb,r=(l,u,f={})=>{const h=new Gt(l,new _n({color:u,side:mn,...f}));return h.frustumCulled=!1,h},o=r(new Us(e,t,12,48),To.rim);o.position.y=n/2+e,o.add(new Nr(new ea(new is(e+t,48)),new ns({color:To.edge})));const a=r(new is(e,48),To.lens,{transparent:!0,opacity:.35,depthWrite:!1});a.position.y=n/2+e;const c=r(new Dt(s,s*1.2,n,16),To.handle);i.add(c,o,a)}const Le={width:.82,height:1.2,cover:.055,pages:.06,spine:.18,inset:.035,open:160,tilt:8,gripHeight:.02,gripSide:.1,closedGrip:.2,gripBack:.6,leaf:.004,curl:2,pageSegments:12,pageBow:.24,lines:5,lineWidth:.004},$i={cover:6514417,spine:3487563,pages:15986399,paper:16776175,edge:2303282,rule:13024940},ld=i=>hn((180-Le.open*i)/2);function hl(i,e){const t=Z[i],n=i==="l"?1:e;return new b(t*Le.width*n,Le.gripHeight,Le.cover/2).applyAxisAngle(new b(0,1,0),t*ld(e)).add(new b(t*Le.spine/2,0,0))}function ud(i){const e=hl("l",i).sub(hl("r",i)).normalize(),t=new b(0,1,0);return new De().makeBasis(e,t,e.clone().cross(t))}function hd(i){return new De().makeRotationX(hn(Le.tilt)).multiply(ud(i).invert())}function Li(i,e){const t=ud(e),n=new b().setFromMatrixColumn(t,0),s=new b().setFromMatrixColumn(t,2);return hl(i,e).addScaledVector(n,Z[i]*(Le.gripSide+Le.closedGrip*(1-e))).addScaledVector(s,-Le.gripBack)}const Yt={pen:{radius:.027,length:.58,tip:.08,sides:12,markerScale:1.8,pencilSides:6,bandScale:1.05,bandAt:1/3},feather:{at:1/4,points:[[0,0],[-.12,.18],[-.08,.42],[.03,.6],[.14,.34],[.1,.12]]},paper:{width:1.58,depth:.54,thickness:.012,count:4,spread:.04,tabletLayers:3,screenWidth:.91,screenDepth:.85,screenLift:2},whistle:{body:[.13,.1,.16],mouthpiece:[.08,.04,.15],mouthAt:[0,.01,-.12]},cloth:{width:.35,depth:.26,thickness:.02},hammer:{handleRadius:.06,handleLength:1.05,gripFrom:.15,head:[.55,.22,.22],sides:10,tilt:45},straw:{radius:.03,length:.7,head:[.045,.16]},colours:{ink:2566454,silver:11120056,paper:15986399,white:16052973,accent:6514417,pencil:14069867,handle:9067051,straw:15255146}};function Mb(){const i=new Map,e=d=>{const m=new un;return m.name=d,m.visible=!1,m.matrixAutoUpdate=!1,i.set(d,m),m},t=(d,m,_,g,p=[0,0,0])=>{const M=Ui(_,g);return M.name=`${d.name}_${m}`,M.position.set(...p),d.add(M),M},{pen:n,paper:s,cloth:r,colours:o}=Yt;for(const d of Object.values(ed)){const m=e(d),_=d==="writing_marker",g=d==="writing_pencil",p=n.radius*(_?n.markerScale:1);t(m,"barrel",new Dt(p,p,n.length,g?n.pencilSides:n.sides),g?o.pencil:o.ink);const M=t(m,"nib",new si(p,n.tip,n.sides),o.silver,[0,-(n.length+n.tip)/2,0]);if(M.rotation.z=Math.PI,t(m,"band",new Dt(p*n.bandScale,p*n.bandScale,n.tip/2,n.sides),o.accent,[0,n.length*n.bandAt,0]),d==="writing_quill"){const x=new di;x.moveTo(...Yt.feather.points[0]);for(const L of Yt.feather.points.slice(1))x.lineTo(...L);x.closePath(),t(m,"feather",new os(x),o.white,[0,n.length*Yt.feather.at,0])}const v=new At;v.name="tip",v.position.y=-n.length/2-n.tip,m.add(v),m.userData.tip=v}for(const d of["papers","writing_paper","writing_tablet"]){const m=e(d),_=d==="writing_tablet",g=d==="papers"?s.count:1;m.userData.sheets=[];for(let p=0;p<g;p++){const M=t(m,`sheet_${p}`,new Rt(s.width,s.thickness*(_?s.tabletLayers:1),s.depth),_?o.ink:o.paper,[0,p*s.thickness,0]);m.userData.sheets.push(M)}_&&t(m,"screen",new Rt(s.width*s.screenWidth,s.thickness,s.depth*s.screenDepth),o.accent,[0,s.thickness*s.screenLift,0])}i.get("papers").userData.shape=({phase:d})=>{const m=te(d,0,.3)*(1-te(d,.8,1));i.get("papers").userData.sheets.forEach((_,g)=>{_.position.x=s.spread*g*(1-m),_.rotation.y=s.spread*g*(1-m)})};const a=e("hand_whistle");t(a,"body",new Rt(...Yt.whistle.body),o.accent),t(a,"mouthpiece",new Rt(...Yt.whistle.mouthpiece),o.silver,Yt.whistle.mouthAt);const{hammer:c}=Yt,l=e("work_hammer");t(l,"handle",new Dt(c.handleRadius,c.handleRadius,c.handleLength,c.sides),o.handle,[0,c.handleLength/2-c.gripFrom,0]),t(l,"head",new Rt(...c.head),o.silver,[0,c.handleLength-c.gripFrom,0]);const{straw:u}=Yt,f=e("straw");t(f,"stalk",new Dt(u.radius,u.radius,u.length,6),o.straw,[0,u.length/2,0]),t(f,"seeds",new si(...u.head,6),o.pencil,[0,u.length+u.head[1]/2,0]),yb(e("magnifying_glass"));const h=e("polishing_cloth");return t(h,"fold",new Rt(r.width,r.thickness,r.depth),o.white),Sb(e,t),i}const fd={hat:{brim:1.084,brimDepth:.074,crown:.9,crownHeight:.787,band:.905,bandFrom:.104,bandDepth:.137,sides:32},monocle:{radius:.2,tube:.028,chain:.55,chainWidth:.012},flute:{base:.13,baseDepth:.025,stem:.022,stemLength:.35,rim:.12,bottom:.05,bowl:.4,fill:.27},shades:{lens:[.56,.34,.05],apart:.37,bridge:[.2,.05,.05],temple:[.04,.04,.7],shine:[.2,.035,.01]},flame:{outer:[.17,.55],inner:[.09,.32],sides:12,flickers:7},finger:{radius:.09,length:.22,splay:.6},popper:{mouth:.14,length:.45,sides:12},confetti:{count:18,size:.08,reach:1.5,fall:.9,spin:9},trophy:{base:[.38,.12,.38],stem:[.05,.08,.22],rim:.3,bottom:.12,cup:.38,handle:.12,handleTube:.03},sword:{grip:[.035,.26],guard:[.42,.06,.07],blade:[.09,1.3,.025],point:.15,pommel:.06},castle:{wall:[.6,.3,.25],crenel:[.1,.08,.25],tower:[.11,.5],roof:[.15,.24],gate:[.14,.18],pole:.24,flag:.14},colours:{hat:2697787,band:16052973,gold:15251530,glass:14542574,champagne:15848058,lens:1316380,flame:16742938,fire:16765503,hand:16116959,wood:8014374,stone:13222580,confetti:[6514417,15251530,15681391,448160,1149618]}};function Sb(i,e){const{hat:t,monocle:n,flute:s,shades:r,flame:o,finger:a,popper:c,confetti:l,trophy:u,sword:f,castle:h,colours:d}=fd,m=Yt.colours.ink,_=Yt.colours.silver,g=Yt.colours.accent,p=i("bowler_hat");e(p,"brim",new Dt(t.brim,t.brim,t.brimDepth,t.sides),d.hat,[0,t.brimDepth/2,0]),e(p,"crown",new Ho(t.crown,t.sides,12,0,2*Math.PI,0,Math.PI/2),d.hat).scale.y=t.crownHeight/t.crown,e(p,"band",new Dt(t.band,t.band,t.bandDepth,t.sides),d.band,[0,t.bandFrom+t.bandDepth/2,0]);const M=i("monocle");e(M,"ring",new Us(n.radius,n.tube,8,24),d.gold),e(M,"lens",new is(n.radius,24),d.glass),e(M,"chain",new Dt(n.chainWidth,n.chainWidth,n.chain,6),d.gold,[n.radius*.7,-n.radius*.7-n.chain/2,0]);const v=i("champagne_flute");e(v,"base",new Dt(s.base,s.base,s.baseDepth,16),d.glass,[0,-s.stemLength/2,0]),e(v,"stem",new Dt(s.stem,s.stem,s.stemLength,8),d.glass),e(v,"bowl",new Dt(s.rim,s.bottom,s.bowl,16,1,!0),d.glass,[0,(s.stemLength+s.bowl)/2,0]),e(v,"wine",new Dt(s.rim*.9,s.bottom*.9,s.fill,16),d.champagne,[0,s.stemLength/2+s.fill/2+.01,0]);const x=i("sunglasses");for(const O of[1,-1])e(x,`lens_${O}`,new Rt(...r.lens),d.lens,[O*r.apart,0,0]),e(x,`temple_${O}`,new Rt(...r.temple),m,[O*(r.apart+r.lens[0]/2),r.lens[1]/4,-r.temple[2]/2]),e(x,`shine_${O}`,new Rt(...r.shine),Yt.colours.white,[O*r.apart-r.lens[0]/5,r.lens[1]/4,r.lens[2]/2]).rotation.z=.5;e(x,"bridge",new Rt(...r.bridge),m,[0,r.lens[1]/4,0]);const L=i("flame"),T=e(L,"outer",new si(o.outer[0],o.outer[1],o.sides),d.flame,[0,o.outer[1]/2,0]),R=e(L,"inner",new si(o.inner[0],o.inner[1],o.sides),d.fire,[0,o.inner[1]/2,.03]);L.userData.shape=({phase:O,size:re})=>{const ue=1+.18*Math.sin(2*Math.PI*o.flickers*O)+.08*Math.sin(2*Math.PI*2.3*o.flickers*O);L.scale.set(re*(2-ue),re*ue,re*(2-ue)),T.rotation.z=R.rotation.z=.12*Math.sin(2*Math.PI*1.7*o.flickers*O)};const I=()=>new Ll(a.radius,a.length,4,8);e(i("thumb"),"thumb",I(),d.hand,[0,a.length/2+a.radius,0]);const w=i("shaka");for(const O of[1,-1])e(w,`finger_${O}`,I(),d.hand,[O*a.length*.6,a.length/2,0]).rotation.z=-O*a.splay;const S=i("party_popper");e(S,"cone",new si(c.mouth,c.length,c.sides,1,!0),g,[0,c.length/2,0]).rotation.x=Math.PI,e(S,"rim",new Us(c.mouth,.02,6,c.sides),d.gold,[0,c.length,0]).rotation.x=Math.PI/2;const P=Array.from({length:l.count},(O,re)=>{const ue=e(S,`confetti_${re}`,new fi(l.size,l.size),d.confetti[re%d.confetti.length]),Me=re*2.39996,Ye=.25+.5*(re*7%l.count)/l.count;return ue.userData.way=new b(Math.sin(Ye)*Math.cos(Me),Math.cos(Ye),Math.sin(Ye)*Math.sin(Me)),ue});S.userData.shape=({burst:O})=>{for(const[re,ue]of P.entries()){ue.visible=O>0&&O<1;const Me=l.reach*Math.sqrt(O);ue.position.set(ue.userData.way.x*Me,c.length+ue.userData.way.y*Me-l.fall*O*O,ue.userData.way.z*Me),ue.rotation.set(l.spin*O+re,l.spin*O*.7,re)}};const G=i("trophy");e(G,"base",new Rt(...u.base),d.wood,[0,-u.stem[2]-u.base[1]/2,0]),e(G,"stem",new Dt(u.stem[0],u.stem[1],u.stem[2],12),d.gold,[0,-u.stem[2]/2,0]),e(G,"cup",new Dt(u.rim,u.bottom,u.cup,16),d.gold,[0,u.cup/2,0]);for(const O of[1,-1])e(G,`handle_${O}`,new Us(u.handle,u.handleTube,6,12),d.gold,[O*u.rim,u.cup*.6,0]);const B=i("sword");e(B,"grip",new Dt(f.grip[0],f.grip[0],f.grip[1],8),d.wood),e(B,"pommel",new Ho(f.pommel,8,6),d.gold,[0,-f.grip[1]/2-f.pommel/2,0]),e(B,"guard",new Rt(...f.guard),d.gold,[0,f.grip[1]/2+f.guard[1]/2,0]),e(B,"blade",new Rt(...f.blade),_,[0,f.grip[1]/2+f.guard[1]+f.blade[1]/2,0]);const V=e(B,"point",new si(f.blade[0]/Math.SQRT2,f.point,4),_,[0,f.grip[1]/2+f.guard[1]+f.blade[1]+f.point/2,0]);V.rotation.y=Math.PI/4,V.scale.z=f.blade[2]/f.blade[0];const j=i("castle");e(j,"wall",new Rt(...h.wall),d.stone,[0,h.wall[1]/2,0]);for(const O of[-1,0,1])e(j,`crenel_${O}`,new Rt(...h.crenel),d.stone,[O*h.wall[0]/3,h.wall[1]+h.crenel[1]/2,0]);for(const O of[1,-1])e(j,`tower_${O}`,new Dt(h.tower[0],h.tower[0],h.tower[1],12),d.stone,[O*h.wall[0]/2,h.tower[1]/2,0]),e(j,`roof_${O}`,new si(...h.roof,12),g,[O*h.wall[0]/2,h.tower[1]+h.roof[1]/2,0]);e(j,"gate",new fi(...h.gate),m,[0,h.gate[1]/2,h.wall[2]/2+.005]);const W=h.tower[1]+h.roof[1];e(j,"pole",new Dt(.01,.01,h.pole,4),m,[h.wall[0]/2,W+h.pole/2,0]);const ee=new di;ee.moveTo(0,0),ee.lineTo(h.flag,-h.flag/3),ee.lineTo(0,-h.flag*2/3),ee.closePath(),e(j,"flag",new os(ee),d.gold,[h.wall[0]/2,W+h.pole,0])}function Eb(i,{bone:e,frame:t,at:n,turn:s}){const r=n.clone().applyMatrix4(i.get(e));return Qs.clone().multiply(Ci(r)).multiply(new De().extractRotation(i.get(t))).multiply(Ps(s.x||0,s.y||0,s.z||0)).multiply(ra)}function bb(i,e,t){var n,s;for(const[r,o]of i.propByName){const a=e.props.get(r);o.visible=!!a,a&&(o.matrix.copy(Eb(t,a)),o.matrixWorldNeedsUpdate=!0,(s=(n=o.userData).shape)==null||s.call(n,a))}}function wb(){const i=(l,u,f,h,d)=>{const m=Ui(new Rt(f,h,d),u);return m.name=l,m.add(new Nr(new ea(m.geometry),new ns({color:$i.edge}))),m},e=new un;e.name="reading_book",e.matrixAutoUpdate=!1,e.visible=!1;const t=i("book_spine",$i.spine,Le.spine,Le.height,Le.cover);e.add(t);const n={},s={},r={},o={};for(const[l,u]of Object.entries(Z)){const f=new un;f.name=`book_hinge_${l}`,f.position.x=u*Le.spine/2;const h=i(`book_cover_${l}`,$i.cover,Le.width,Le.height,Le.cover);h.position.set(u*Le.width/2,0,Le.cover/2);const d=i(`book_pages_${l}`,$i.pages,Le.width-Le.inset,Le.height-Le.inset*2,Le.pages);d.position.set(u*(Le.width-Le.inset)/2,0,-Le.pages/2);for(let _=1;_<=Le.lines;_++){const g=Ui(new Rt(Le.width-Le.inset,Le.lineWidth,Le.lineWidth),$i.rule);g.position.set(d.position.x,-Le.height/2+Le.inset,-Le.pages*_/(Le.lines+1)),f.add(g)}f.add(h,d),e.add(f),n[l]=f,s[l]=h,r[l]=d;const m=new At;m.name=`book_grip_${l}`,e.add(m),o[l]=m}const a=Ui(new fi(Le.width-Le.inset,Le.height-Le.inset*2,Le.pageSegments,1),$i.paper);a.geometry.translate(-(Le.width-Le.inset)/2,0,0),a.name="book_turning_page";const c=new Ef(new Ft,new ns({color:$i.rule}));return c.frustumCulled=!1,a.add(c),a.userData.edge=c,e.add(a),e.userData={hinges:n,covers:s,pages:r,grips:o,leaf:a},e}function Tb(i,e){const t=i.l.clone(),n=i.r.clone(),s=t.clone().sub(n).normalize(),r=new b(0,1,0).addScaledVector(s,-s.y).normalize(),o=s.clone().cross(r).normalize(),a=new De().makeBasis(s,r,o).multiply(hd(e)),c=t.distanceTo(n)/Li("l",e).distanceTo(Li("r",e)),l=Li("l",e).add(Li("r",e)).multiplyScalar(.5).applyMatrix4(a).multiplyScalar(c);return a.scale(new b(c,c,c)).setPosition(t.add(n).multiplyScalar(.5).sub(l))}function Ab(i,e,t){const n=ld(e);for(const[u,f]of Object.entries(Z))i.userData.hinges[u].rotation.y=f*n,i.userData.grips[u].position.copy(Li(u,e));const s=i.userData.leaf,r=Le.pages+Le.leaf;s.position.set(kt(-Le.spine/2+r*Math.sin(n),Le.spine/2-r*Math.sin(n),t),0,-r*Math.cos(n)),s.rotation.y=-n-hn(Le.open*e)*t,s.visible=e>0;const o=Le.curl*Math.sin(Math.PI*t),a=Le.width-Le.inset,c=s.geometry.attributes.position;for(let u=0;u<2;u++)for(let f=0;f<=Le.pageSegments;f++){const h=1-f/Le.pageSegments,d=u*(Le.pageSegments+1)+f,m=Le.pageBow*Math.sin(Math.PI*t)*h*h;c.setX(d,(o?-a*Math.sin(o*h)/o:-a*h)-Math.sin(s.rotation.y)*m),c.setZ(d,(o?a*(1-Math.cos(o*h))/o:0)+Math.cos(s.rotation.y)*m)}c.needsUpdate=!0;const l=[];for(let u=0;u<=Le.pageSegments;u++)l.push(new b().fromBufferAttribute(c,u));for(let u=Le.pageSegments;u>=0;u--)l.push(new b().fromBufferAttribute(c,Le.pageSegments+1+u));s.userData.edge.geometry.setFromPoints(l)}const Rb=1.95,Cb=.3;function Pb(i){const e=a=>new b().setFromMatrixPosition(i.get(a)),t=e("thigh_l").add(e("thigh_r")).multiplyScalar(.5),n=e("shin_l").add(e("shin_r")).multiplyScalar(.5),s=n.clone().sub(t).setY(0).normalize(),r=new b(0,1,0),o=t.lerp(n,Rb).addScaledVector(r,Cb);return new De().makeBasis(r.clone().cross(s),r,s).setPosition(o)}const Lb=(()=>{const i=new di;return i.moveTo(0,-.5),i.bezierCurveTo(-.16,-.3,-.5,-.16,-.5,.12),i.bezierCurveTo(-.5,.4,-.2,.5,0,.26),i.bezierCurveTo(.2,.5,.5,.4,.5,.12),i.bezierCurveTo(.5,-.16,.16,-.3,0,-.5),new os(i,12)})(),Ib=.42,Db=new Ve(1,.3,.5),Nb=(()=>{const i=new di;for(let e=0;e<10;e++){const t=e%2?.22:.55,n=Math.PI/2+e*Math.PI/5;i[e?"lineTo":"moveTo"](t*Math.cos(n),t*Math.sin(n))}return new os(i)})(),Ub=.46,Ob=new Ve(1,.86,.3),Fb=(()=>{const i=[[-.4,.42],[.42,0],[-.4,-.42],[-.4,-.2],[.04,0],[-.4,.2]];return new os(new di(i.map(([e,t])=>new ie(e,t))))})(),zh=.5,Bb=new Ve(1,.94,.81);function fc(i,e,t){const n=new on().setFromBufferAttribute(i.geometry.attributes.position).applyMatrix4(i.matrixWorld),s=n.getCenter(new b).setZ(n.max.z+.01),r=i.skeleton.getBoneByName("head"),o=new un;o.matrixAutoUpdate=!1,o.matrix.copy(r.matrixWorld).invert().multiply(Ci(s));const a=new Gt(e,new _n({color:t}));return a.frustumCulled=!1,a.visible=!1,o.add(a),r.add(o),a}function kb(i,e){return Object.fromEntries(Object.keys(Z).map(t=>[t,i.grip(t,[0,0,0]).applyMatrix4(e.get(`hand_${t}`)).applyMatrix4(Qs)]))}function zb(i,e,t,n){var f;const s=e.moves(t),r=n?cy(i.rig,n.from,s,n.k,n.previous):{moves:s,settled:!0};n&&(n.settled=r.settled);const o=r.moves,a=new Map;for(const h of i.rig.bones){const d=Qs.clone().multiply(o.get(h.name)).multiply(ra).multiply(i.rig.rest.get(h.name));a.set(h.name,d),(h.parent.isBone?a.get(h.parent.name):h.parent.matrixWorld).clone().invert().multiply(d).decompose(h.position,h.quaternion,h.scale)}for(const h of i.eyes.materials)h.uniforms.openness.value=e.eyes,h.uniforms.light&&h.uniforms.colour.value.set(...e.eyeTint??h.userData.colour);i.laptop.visible=e.laptop,i.book.visible=!!((f=e.book)!=null&&f.visible),i.book.visible&&(Ab(i.book,e.book.open,e.book.page),i.book.matrix.copy(Tb(kb(e,o),e.book.open)),i.book.matrixWorldNeedsUpdate=!0);for(const h of i.tablet)h.visible=e.tablet;const c=e.laptop||e.book||e.props.size>0;for(const h of i.stowable)h.visible=!e.stowed.has(h.userData.item);for(const h of i.inHand)h.visible=!e.stowed.has(h.userData.item)&&(!c||e.keep.has(h.userData.item));bb(i,e,o);for(const h of i.cloth)h.visible=e.cloth;e.laptop&&(i.laptop.matrix.copy(Pb(a)),i.laptop.matrixWorldNeedsUpdate=!0);const l=e.screen??Wb;for(const h of i.screens)h.uniforms.lit.value=l.glow,h.uniforms.across.value=l.across,h.uniforms.open.value=l.open,h.uniforms.flash.value=l.flash,e.screen&&h.uniforms.glow.value.set(...e.screen.colour);for(const h of i.visorHulls)h.visible=!e.screen;const u=l.eyes>Gb;for(const h of i.eyes.shapes)h.visible=u&&!e.hearts&&!e.stars&&!e.squeezed;for(const h of i.eyes.hearts)h.visible=u&&e.hearts>0,h.scale.setScalar(Ib*e.hearts);for(const h of i.eyes.stars)h.visible=u&&e.stars>0&&!e.hearts,h.scale.setScalar(Ub*e.stars),h.rotation.z=1.2*(e.stars-1);for(const h of i.eyes.squeezed)h.visible=u&&e.squeezed>0&&!e.hearts&&!e.stars,h.scale.set(zh*e.squeezed*h.userData.way,zh*e.squeezed,1);return o}const Hh=.8,dd=({seconds:i,lasts:e})=>Mt(i,0,.15)*(1-Mt(i,e-.3,e));function Hb(i,{mood:e,seconds:t,lasts:n}){const s=dd({seconds:t,lasts:n});if(Yf[e].hearts){const r=t%Hh/Hh;i.heartEyes(s*(1+.28*ke(r,0,.3)+.14*ke(r,.3,.55)))}else Ze(i,e,s)}const Vh={share:.8,lean:.12};function Vb(i,e,t){const n=((e+180)%360+360)%360-180,s=Vh.lean*n,r=ci.clamp(Vh.share*n-s,-Yo,Yo);i.bendAbove("chest",{z:-s*t}),i.turn("neck",{z:-.3*r*t}),i.turn("head",{z:-.7*r*t})}const dc="face_screen",Gb=.05,Wb={eyes:1,across:0,open:0,flash:0,glow:0};class Qb{constructor(){const e=Oi/2;this.camera=new Zo(-e,e,e,-e,ec-wh,ec+wh),this.camera.position.set(0,Go,ec),this.camera.lookAt(0,Go,0),this.renderer=new zx({antialias:!0,alpha:!0,preserveDrawingBuffer:!0}),this.renderer.setPixelRatio(1),this.renderer.setClearColor(0,0)}headAt(e,t){if(!t)return{x:.5,y:.3};const n=e.rig.eyes.reduce((s,r)=>s.add(r),new b).divideScalar(e.rig.eyes.length);return this.pictured(n.applyMatrix4(t.get("head")))}handAt(e,t){const n=it(e.stance);if(!t)return{x:.5+Z[n]*.25,y:.6,out:Z[n]};const s=new b(Z[n]*js.grip,js.forward,0).add(e.rig.heads.get(`hand_${n}`));return{...this.pictured(s.applyMatrix4(t.get(`hand_${n}`))),out:Z[n]}}pictured(e){const t=e.applyMatrix4(Qs).project(this.camera);return{x:(t.x+1)/2,y:(1-t.y)/2}}draw(e,t,n,s,r,{posture:o="stand",eyes:a=null,stride:c=0,blend:l=null,sky:u=null,at:f=null,open:h=1,screen:d=null}={}){var x,L;const m=new _M(e.rig,o,c);m.sky=u,m.screen=d,t.legs||(x=Bh[o])==null||x.under(m),t.pose(m,e.stance,n/t.frames),t.legs||(L=Bh[o])==null||L.over(m);const _=s+(f?YS(m,f,s):0);h<1&&m.shutEyes(Math.min(m.eyes,h)),d&&m.shutEyes(Math.min(m.eyes,d.eyes));const g=Math.max(a?dd(a):0,d?xd(d):0);g&&!m.gaze&&Vb(m,_,g),a&&Hb(m,a);const p=zb(e,m,_,l),M=r.width*ti;this.renderer.domElement.width!==M&&this.renderer.setSize(M,M,!1),this.renderer.render(e.scene,this.camera);const v=r.getContext("2d");return v.clearRect(0,0,r.width,r.height),v.imageSmoothingQuality="high",v.filter=`blur(${Qy*r.width/Zy}px)`,v.drawImage(this.renderer.domElement,0,0,r.width,r.height),p}drawBlock(e,t,n,s){this.blockFor!==n&&(this.block=gb(Oi/n)),this.blockFor=n,_b(this.block,e,t);const r=Math.round(n*s)*ti;this.renderer.domElement.width!==r&&this.renderer.setSize(r,r,!1),this.renderer.render(this.block.scene,this.camera);const{min:o,max:a}=this.block.bounds,c=[o.x,a.x].flatMap(p=>[o.y,a.y].flatMap(M=>[o.z,a.z].map(v=>new b(p,M,v).project(this.camera)))),l=p=>(p+1)/2*r,u=Math.floor(Math.min(...c.map(p=>l(p.x))))-ti,f=Math.ceil(Math.max(...c.map(p=>l(p.x))))+ti,h=Math.floor(Math.min(...c.map(p=>r-l(p.y))))-ti,d=Math.ceil(Math.max(...c.map(p=>r-l(p.y))))+ti,m=document.createElement("canvas");m.width=Math.round((f-u)/ti),m.height=Math.round((d-h)/ti);const _=m.getContext("2d");_.imageSmoothingQuality="high",_.drawImage(this.renderer.domElement,u,h,f-u,d-h,0,0,m.width,m.height);const g=r-l(new b(0,0,0).project(this.camera).y);return{canvas:m,below:(d-g)/ti/s}}}export{jt as ACTED,k as ACTING,Le as BOOK,Zy as CELL,Zb as CLIPS,bi as EAGERNESS,Yf as EYES,zn as GLANCE,$b as GROUND,js as HAND,Yo as HEAD_TURN,ul as LANDING,cc as LEDGE,_M as Posing,he as REACTING,fd as REACTION_PROPS,bt as REST,hc as SCREEN,gr as SHOVE,Z as SIDES,Ti as SKY,Qb as Stage,Yt as TOOLS,Vh as TOWARD_VIEWER,Mn as TUMBLE,Qt as WAIT,Nn as WORK,ed as WRITING,Kb as blowsLandAt,db as figureOf,Jb as loadFigure,YS as lookToward,IM as supportsClip,Vb as turnToViewer};

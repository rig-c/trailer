// Read real producer inputs before compiling/rendering them; no source mutation.
import {readRigInputs} from '../node_modules/@rig-c/parts/src/build.ts';
import {parseRigSpec} from '../node_modules/rig-c/src/rig.ts';
import {parseMotionSpec} from '../node_modules/rig-c/src/motion.ts';
import {existsSync,readFileSync,statSync} from 'node:fs';
import {join} from 'node:path';
const [kind,dir]=process.argv.slice(2);
function file(p:string){if(!existsSync(p)||!statSync(p).isFile())throw Error(`missing file ${p}`);}
if(kind==='parts'){
 const r=readRigInputs('inputs/config.json',dir);
 for(const p of r.parts.parts){file(join(dir,'parts',p.name+'.png'));if(p.depth)file(join(dir,'parts',p.depth.image));}
 if(r.parts.parts.some(p=>!p.depth))throw Error('all-sheet production input lost depth');
 console.log('PREFLIGHT parts:',r.parts.parts.length,'parts, all scalar-bound,',r.images.size,'images');
}else if(kind==='film'){
 const rig=parseRigSpec(JSON.parse(readFileSync(join(dir,'rig.json'),'utf8')),dir);
 const motion=parseMotionSpec(JSON.parse(readFileSync(join(dir,'motion.json'),'utf8')),dir);
 let timelines=0, keys=0;
 const timelineWalk=(value:any)=>{
   if(!value||typeof value!=="object")return;
   if(Array.isArray(value.keys)){
     const a=value.keys;timelines++;keys+=a.length;
     for(let i=1;i<a.length;i++)if(!(a[i].t>a[i-1].t))throw Error(`non-increasing timeline at ${a[i].t}`);
     const last=a.at(-1);if(last&&("ease" in last||"curve" in last))throw Error("terminal key carries easing/curve");
   }
   for(const child of Object.values(value))timelineWalk(child);
 };timelineWalk(motion);
 for(const name of ['rig.json','rig_black.json'])parseRigSpec(JSON.parse(readFileSync(join(dir,name),'utf8')),dir);
 console.log('PREFLIGHT timeline order and terminal keys:',timelines,'timelines,',keys,'keys');
 const walk=(v:any)=>{if(!v||typeof v!=='object')return;if(typeof v.image==='string')file(join(dir,'images',v.image));for(const x of Object.values(v))walk(x);};walk(rig);
 file('inputs/sky.png');console.log('PREFLIGHT film: actual rig/motion parsers, all image paths resolve');
}else throw Error('preflight parts|film <directory>');

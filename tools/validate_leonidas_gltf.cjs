// npm install gltf-validator (official Khronos validator). Set NODE_PATH if
// installed outside this checkout. Bounded regional files, not 151MB in RAM.
const fs=require('fs'), path=require('path'), crypto=require('crypto'), validator=require('gltf-validator');
const root=path.resolve(__dirname,'..'), dir=path.join(root,'exports/leonidas_ii/build/Roblox_Import_Kit');
(async()=>{
 const rows=[];
 for(const file of fs.readdirSync(dir).filter(x=>x.endsWith('.glb')).sort()){
  const bytes=fs.readFileSync(path.join(dir,file));
  const result=await validator.validateBytes(new Uint8Array(bytes),{uri:file,maxIssues:1000});
  rows.push({file,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),errors:result.issues.numErrors,warnings:result.issues.numWarnings,infos:result.issues.numInfos,truncated:result.issues.truncated,messages:result.issues.messages});
  console.log(file,'errors',result.issues.numErrors,'warnings',result.issues.numWarnings);
  if(global.gc)global.gc();
 }
 fs.writeFileSync(path.join(root,'docs/leonidas_ii/GLTF_VALIDATION.json'),JSON.stringify({validator:'Khronos glTF-Validator npm',scope:'Actual regional GLBs in import kit; structural format checks, not Studio upload/render or FPS certification',rows},null,2));
 process.exitCode=rows.some(r=>r.errors>0)?1:0;
})().catch(e=>{console.error(e);process.exitCode=1});

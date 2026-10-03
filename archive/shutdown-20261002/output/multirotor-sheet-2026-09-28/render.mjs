import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const dir='/Users/redhose/output/multirotor-sheet-2026-09-28';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(dir+'/verification.xlsx'));
const manifest=JSON.parse(await fs.readFile(dir+'/payload/manifest.json','utf8'));
await fs.mkdir(dir+'/previews',{recursive:true});
for(const t of manifest){
  const range=t.name==='Charts'?'A7:F27':t.name==='CS Dashboard'?'A4:D12':t.name==='Model Functions'?'A1:D5':t.name==='Calculation Notes'?'A1:C5':`A1:${t.width<4?'B':'D'}${Math.min(t.nrows,7)}`;
  try{
    const image=await wb.render({sheetName:t.name,range,scale:1,format:'png'});
    await fs.writeFile(dir+'/previews/'+t.id+'.png',new Uint8Array(await image.arrayBuffer()));
    console.log('rendered '+t.name);
  }catch(e){console.log('render error '+t.name+': '+e.message);}
}
for(const [name,range,file] of [['Study Charts','A5:G44','study-chart'],['Charts','A205:G235','scenario-chart']]){
 try{const image=await wb.render({sheetName:name,range,scale:1,format:'png'});await fs.writeFile(dir+'/previews/'+file+'.png',new Uint8Array(await image.arrayBuffer()));}catch(e){console.log('chart render error '+e.message);}
}

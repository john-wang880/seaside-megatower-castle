"""Exact rendered pixels in a labelled comparison; no rescale or retouch."""
from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw,ImageFont

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--font',type=Path,default=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'));a=p.parse_args();r=a.output.with_suffix('.json')
 if a.output.exists()or r.exists():raise RuntimeError('New outputs required')
 ims=[Image.open(x).convert('RGB')for x in[a.before,a.after]]
 if any(im.size!=(960,694)for im in ims):raise RuntimeError('Expected exact 960×694 inputs')
 border=24;gap=24;header=86;footer=88;size=(border*2+1920+gap,header+694+footer)
 canvas=Image.new('RGB',size,'#f2f1ed');draw=ImageDraw.Draw(canvas);title=ImageFont.truetype(str(a.font),34);small=ImageFont.truetype(str(a.font),26)
 rects=[]
 for im,x,label in zip(ims,[border,border+960+gap],['v027｜原通道','v028｜新增房间入口']):
  draw.text((x,22),label,font=title,fill='#24333b');canvas.paste(im,(x,header));rects.append([x,header,x+960,header+694])
 note='同一视角；原灯具/整体光照设置保留，房间内新增两盏暖灯'
 draw.text((border,header+694+23),note,font=small,fill='#46535a')
 canvas.save(a.output)
 decoded=Image.open(a.output).convert('RGB')
 for im,box in zip(ims,rects):
  if decoded.crop(box).tobytes()!=im.tobytes():raise RuntimeError('Embedded pixels changed')
 report={'purpose':'Same-camera entrance comparison; publication and final QA status not claimed','before':{'path':str(a.before),'sha256':sha(a.before),'label':'v027｜原通道'},'after':{'path':str(a.after),'sha256':sha(a.after),'label':'v028｜新增房间入口'},'note':note,'source_dimensions':[960,694],'output_dimensions':list(size),'source_rectangles':rects,'exact_decoded_rgb_pixels_verified':True,'rescale':False,'retouch':False,'font_sha256':sha(a.font),'script_sha256':sha(Path(__file__)),'output_sha256':sha(a.output)}
 r.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()

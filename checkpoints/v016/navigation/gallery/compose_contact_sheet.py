"""Compose seven actual renders without changing any rendered pixel.
Python3 + Pillow; --frames contains <view>/image.png. Supply a CJK font.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
VIEWS=[('hero','01  海边巨塔 · 全景'),('west_approach','02  林地与西侧接近'),('east_portal','03  桥端入口'),('bend','04  内廊转角'),('upper_stairs','05  回看上段楼梯'),('terminal','06  北侧终点地面 · 保留暗部'),('offshore_marker','07  离岸小塔 · 台阶承托')]
def frame_path(root,key):
 nested=root/key/'image.png'
 return nested if nested.exists() else root/(key+'.png')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--frames',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--font',type=Path,required=True);a=p.parse_args()
 assert not a.output.exists(),'Refuse existing output'
 titlefont=ImageFont.truetype(str(a.font),48);labelfont=ImageFont.truetype(str(a.font),32);bodyfont=ImageFont.truetype(str(a.font),30)
 W,H=1200,866;margin=20;gap=20;header=124;label=64;cellh=H+label
 canvas=Image.new('RGB',(2*W+2*margin+gap,header+4*cellh+3*gap+margin),(17,25,36));draw=ImageDraw.Draw(canvas)
 draw.text((margin,18),'海边巨塔城堡  /  v016 七视角',font=titlefont,fill=(244,241,230))
 draw.text((margin,80),'当前模型实渲 · 原有照明与曝光 · 不是连续行走动画',font=bodyfont,fill=(180,195,203))
 rows=[]
 for n,(key,labeltext) in enumerate(VIEWS):
  path=frame_path(a.frames,key);im=Image.open(path);im.load();assert im.mode=='RGB' and im.size==(W,H),(key,im.mode,im.size)
  x=margin+(n%2)*(W+gap);y=header+(n//2)*(cellh+gap)
  assert draw.textbbox((x,y),labeltext,font=labelfont)[2]<=x+W
  draw.text((x,y+10),labeltext,font=labelfont,fill=(244,241,230));canvas.paste(im,(x,y+label))
  assert canvas.crop((x,y+label,x+W,y+label+H)).tobytes()==im.tobytes()
  rows.append({'view':key,'source_png_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pixel_rectangle':[x,y+label,x+W,y+label+H],'source_pixels_preserved_exactly':True})
 x=margin+W+gap;y=header+3*(cellh+gap)
 lines=['看图说明','','七张均来自当前 v016 模型。','1200 × 866 / 80 采样 / Cycles CPU','未补光、去雾、提亮或修饰建筑。','','主路线：桥端入口 → 内廊转角 →','楼梯 → 北侧有顶露台附近。','相机可在路线之外，不是步行动画。','','离岸小塔是独立岛礁；','承托修复不代表已连接大陆。','','保留自然阴影，室内仍有暗处。','几何检查有明确范围，非全城通行认证。']
 for i,line in enumerate(lines):
  assert draw.textbbox((x,y),line,font=bodyfont)[2]<=x+W
  draw.text((x,y+24+i*46),line,font=bodyfont,fill=(200,211,216))
 a.output.parent.mkdir(parents=True,exist_ok=True);canvas.save(a.output)
 reread=Image.open(a.output).convert('RGB')
 for row in rows:
  im=Image.open(frame_path(a.frames,row['view'])).convert('RGB');assert reread.crop(row['pixel_rectangle']).tobytes()==im.tobytes()
 report={'source_model_sha256':'d44a4cdecd11dab152fd656c624755369e575a0f342e2eb0bc2460475c6f65eb','sheet_size':list(canvas.size),'sheet_sha256':hashlib.sha256(a.output.read_bytes()).hexdigest(),'font_sha256':hashlib.sha256(a.font.read_bytes()).hexdigest(),'compositing':'Exact unscaled RGB render pixels pasted on labeled sheet; no generative edits, recoloring, cropping, contrast or exposure adjustment.','views':rows}
 a.output.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()

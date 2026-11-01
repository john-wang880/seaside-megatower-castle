from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
r=Path(__file__).resolve().parent;repo=r.parents[2]
paths=[repo/'work/lateral_coverage_v025/actual/image.png',r/'lateral_after/image.png'];out=r/'lateral_pair_bilingual.png';assert not out.exists()
canvas=Image.new('RGB',(2448,1024),'#f1f1ed');d=ImageDraw.Draw(canvas);font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';f=ImageFont.truetype(font,30);small=ImageFont.truetype(font,24)
for i,(p,label)in enumerate(zip(paths,['v025 主塔重复黑带 / Before','v026 主塔表面修正 / After'])):
 im=Image.open(p).convert('RGB');assert im.size==(1200,866);x=16+i*1216;d.text((x,12),label,font=f,fill='#202626');canvas.paste(im,(x,56))
d.text((16,938),'同一相机、原始光照；图像像素原样保留 / Same camera and lighting; unchanged render pixels.',font=small,fill='#202626')
d.text((16,969),'仅清理重复表面；保留原有体积、石色与窗洞 / Duplicate skins removed; original mass, stone and openings retained.',font=small,fill='#202626');canvas.save(out)
(r/'lateral_pair_bilingual.json').write_text(json.dumps({'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'input_paths':[str(p)for p in paths],'input_sha256':[hashlib.sha256(p.read_bytes()).hexdigest()for p in paths],'uniform_scale':1,'resample':None,'labels_outside_images':True,'lighting_color_edits':False},indent=2)+'\n')

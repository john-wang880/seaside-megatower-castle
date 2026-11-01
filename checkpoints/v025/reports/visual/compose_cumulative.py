from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
r=Path(__file__).resolve().parent;repo=r.parents[2]
paths=[repo/'checkpoints/v024/previews/rear_before.png',r/'rear_after/image.png'];out=r/'rear_cumulative_v023_v025.png';assert not out.exists()
canvas=Image.new('RGB',(2448,1024),'#f1f1ed');d=ImageDraw.Draw(canvas);font='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc';f=ImageFont.truetype(font,30);small=ImageFont.truetype(font,24)
for i,(p,label)in enumerate(zip(paths,['v023 清理前 / Before','v025 已确认重复表面清理后 / After'])):
 im=Image.open(p).convert('RGB');assert im.size==(1200,866);x=16+i*1216;d.text((x,12),label,font=f,fill='#202626');canvas.paste(im,(x,56))
d.text((16,938),'同一相机、原始光照；图像像素原样保留 / Same camera and lighting; unchanged render pixels.',font=small,fill='#202626')
d.text((16,969),'一组阶梯体与四组回廊体；保留真实凹部 / Identified stepped and four return groups only.',font=small,fill='#202626');canvas.save(out)
(r/'rear_cumulative_v023_v025.json').write_text(json.dumps({'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'input_paths':[str(p)for p in paths],'input_sha256':[hashlib.sha256(p.read_bytes()).hexdigest()for p in paths],'uniform_scale':1,'resample':None,'labels_outside_images':True,'lighting_color_edits':False},indent=2)+'\n')

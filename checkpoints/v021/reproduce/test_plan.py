import json,unittest
from pathlib import Path
P=Path(__file__).with_name('plan.json')
def vol(lo,hi):
 r=1
 for a,b in zip(lo,hi):r*=max(0,b-a)
 return r
class Plan(unittest.TestCase):
 def test_exact_box_unions(self):
  for p in json.loads(P.read_text())['pairs']:
   a,b=p['components'];lo=[min(a['bounds'][0][i],b['bounds'][0][i])for i in range(3)];hi=[max(a['bounds'][1][i],b['bounds'][1][i])for i in range(3)];il=[max(a['bounds'][0][i],b['bounds'][0][i])for i in range(3)];ih=[min(a['bounds'][1][i],b['bounds'][1][i])for i in range(3)]
   self.assertEqual(a['bounds'][0][1:],b['bounds'][0][1:]);self.assertEqual(a['bounds'][1][1:],b['bounds'][1][1:]);self.assertGreater(vol(il,ih),0)
   self.assertAlmostEqual(vol(lo,hi),vol(*a['bounds'])+vol(*b['bounds'])-vol(il,ih),places=9)
   self.assertEqual(len(set(v['id']for c in[a,b]for v in c['vertices'])),16)
 def test_box_faces_outward_positive(self):
  v=[(x,y,z)for x in[0,1]for y in[0,1]for z in[0,1]];fs=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
  def sub(a,b):return tuple(x-y for x,y in zip(a,b))
  def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
  total=0
  for f in fs:
   n=cross(sub(v[f[1]],v[f[0]]),sub(v[f[2]],v[f[0]]));center=[sum(v[i][k]for i in f)/4-.5 for k in range(3)];self.assertGreater(sum(a*b for a,b in zip(n,center)),0)
   for i in[1,2]:total+=sum(a*b for a,b in zip(v[f[0]],cross(v[f[i]],v[f[i+1]])))/6
  self.assertAlmostEqual(total,1)
if __name__=='__main__':unittest.main()

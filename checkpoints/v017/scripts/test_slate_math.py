import dataclasses
import json
import math
import unittest
import slate_math as sm

class SlateMathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=sm.Parameters();cls.tiles,cls.discarded,cls.stats=sm.generate(cls.p);cls.frames={f['name']:f for f in sm.pitches()}

    def test_halfplane_clipping_known_area(self):
        p=sm.clip([(0,0),(2,0),(2,2),(0,2)],lambda q:1-q[0])
        self.assertAlmostEqual(sm.area(p),2)
        self.assertEqual(sm.clip(p,lambda q:-3-q[0]),[])

    def test_four_orthonormal_face_frames(self):
        self.assertEqual(set(self.frames),{'south','east','north','west'})
        for f in self.frames.values():
            for a in ('u','v','normal'):self.assertAlmostEqual(sm.dot(f[a],f[a]),1)
            self.assertAlmostEqual(sm.dot(f['u'],f['v']),0)
            self.assertGreater(f['normal'][2],0)

    def test_expected_budget_and_symmetry(self):
        self.assertEqual(len(self.tiles),6032)
        self.assertLess(sum(len(t['vertices']) for t in self.tiles),60000)
        counts={x['pitch']:x['tiles'] for x in self.stats}
        self.assertEqual(counts['south'],counts['north']);self.assertEqual(counts['east'],counts['west'])

    def test_closed_oriented_non_degenerate_solids(self):
        for t in self.tiles:
            self.assertTrue(sm.manifold(t));self.assertGreater(t['volume'],0)
            vs=t['vertices'];edges=set()
            for f in t['faces']:
                for a,b in zip(f,f[1:]+f[:1]):
                    self.assertGreater(math.dist(vs[a],vs[b]),1e-8);edges.add(tuple(sorted((a,b))))
            self.assertEqual(len(vs)-len(edges)+len(t['faces']),2)

    def test_independent_signed_volume(self):
        # Translation-local tetrahedral determinant; independent of analytical height integral.
        for t in self.tiles:
            origin=t['vertices'][0];v=[sm.sub(p,origin) for p in t['vertices']];volume=0
            for f in t['faces']:
                for k in range(1,len(f)-1):volume+=sm.dot(v[f[0]],sm.cross(v[f[k]],v[f[k+1]]))/6
            self.assertAlmostEqual(volume,t['volume'],places=9)

    def test_every_footprint_inside_all_inset_halfplanes(self):
        for t in self.tiles:
            fp=self.frames[t['pitch']]['polygon']
            for q in t['polygon']:
                for a,b in zip(fp,fp[1:]+fp[:1]):
                    ex,ey=b[0]-a[0],b[1]-a[1]
                    dist=(ex*(q[1]-a[1])-ey*(q[0]-a[0]))/math.hypot(ex,ey)
                    self.assertGreaterEqual(dist,self.p.inset-1e-8)

    def test_original_macro_plan_and_ridge_not_exceeded(self):
        r=sm.report(self.p,self.tiles,self.discarded,self.stats)
        self.assertTrue(r['macro_plan_and_height_preserved'])
        self.assertLess(r['bounds'][1][2],210.55)

    def test_slope_local_spacing_and_stagger(self):
        for t in self.tiles:
            self.assertAlmostEqual(t['row_start'],t['row']*.4)
            expected=t['col']*.6+(t['row']%2)*.3+.002
            self.assertAlmostEqual(t['column_start'],expected)
        # Equal .4 slope exposure deliberately gives unequal world-Z row pitch.
        self.assertNotAlmostEqual(.4*self.frames['south']['v'][2],.4*self.frames['east']['v'][2])

    def test_source_plane_embedding_and_positive_shallow_tops(self):
        for t in self.tiles:
            f=self.frames[t['pitch']];n=len(t['polygon'])
            for v in t['vertices'][:n]:self.assertAlmostEqual(sm.dot(sm.sub(v,f['origin']),f['normal']),-.015,places=10)
            for v in t['vertices'][n:]:
                z=sm.dot(sm.sub(v,f['origin']),f['normal']);self.assertGreaterEqual(z,.003-1e-9);self.assertLessEqual(z,.025+1e-9)

    def test_overlap_tops_are_not_coplanar(self):
        # Upper-row face is this much higher over the .2 overlap interval.
        delta=(self.p.lip-self.p.head)*self.p.exposure/self.p.length
        self.assertAlmostEqual(delta,.014666666666666668)
        self.assertGreater(delta,0)
        self.assertAlmostEqual(self.p.length-self.p.exposure,.2)

    def test_edge_slivers_bounded_and_not_silently_counted(self):
        self.assertEqual(len(self.discarded),40)
        self.assertLess(sum(t['area'] for t in self.discarded),.05)
        for t in self.discarded:self.assertTrue(t['area']<self.p.min_area or t['span']<self.p.min_span)

    def test_clipped_hip_ridge_edges_inside_existing_analytic_bronze(self):
        distances=[]
        for t in self.tiles:
            f=self.frames[t['pitch']];fp=f['polygon'];n=len(t['polygon'])
            for i,q in enumerate(t['polygon']):
                # Skip eave edge, which deliberately has no bronze hip beam.
                for a,b in list(zip(fp,fp[1:]+fp[:1]))[1:]:
                    ex,ey=b[0]-a[0],b[1]-a[1]
                    d=(ex*(q[1]-a[1])-ey*(q[0]-a[0]))/math.hypot(ex,ey)
                    if abs(d-self.p.inset)>1e-7:continue
                    def world(z):return sm.add(f['origin'],sm.add(sm.mul(f['u'],z[0]),sm.mul(f['v'],z[1])))
                    aa=sm.add(world(a),(0,0,.05));bb=sm.add(world(b),(0,0,.05));ab=sm.sub(bb,aa)
                    v=t['vertices'][i+n];delta=sm.sub(v,aa);param=sm.dot(delta,ab)/sm.dot(ab,ab)
                    self.assertGreaterEqual(param,0);self.assertLessEqual(param,1)
                    radial=math.dist(v,sm.add(aa,sm.mul(ab,param)))
                    # Inside inscribed cylinder => inside source's octagonal prism for any angular orientation.
                    self.assertLess(radial,.12*math.cos(math.pi/8));distances.append(radial)
        self.assertEqual(len(distances),1304)
        self.assertAlmostEqual(max(distances),.10113562875161221)

    def test_repeatability_and_invalid_parameters(self):
        t,d,s=sm.generate(self.p)
        self.assertEqual(t,self.tiles);self.assertEqual(d,self.discarded);self.assertEqual(s,self.stats)
        for k,v in [('exposure',.7),('bottom',.1),('width',float('nan')),('head',.04),('inset',0)]:
            with self.assertRaises(ValueError):dataclasses.replace(self.p,**{k:v}).validate()

if __name__=='__main__':unittest.main(verbosity=2)

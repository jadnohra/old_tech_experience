from ctypes import *
import math
import time
import copy
import random
import pickle
# conda install pyopengl
# conda install -c conda-forge freeglut
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
# conda install -c kne pybox2d
from Box2D import *
#
g_dbg = False
#
def sys_argv_has(keys):
	if (hasattr(sys, 'argv')):
	 return any(x in sys.argv for x in keys)
	return False
def sys_argv_has_key(keys):
	if ( hasattr(sys, 'argv')):
		for key in keys:
			ki = sys.argv.index(key) if key in sys.argv else -1
			if (ki >= 0 and ki+1 < len(sys.argv)):
				return True
	return False
def sys_argv_get(keys, dflt):
	if ( hasattr(sys, 'argv')):
		for key in keys:
			ki = sys.argv.index(key) if key in sys.argv else -1
			if (ki >= 0 and ki+1 < len(sys.argv)):
				return sys.argv[ki+1]
	return dflt
#
def m_min(v1, v2):
	return v1 if (v1 <= v2) else v2
def m_max(v1, v2):
	return v1 if (v1 >= v2) else v2
def m_interp(v1, v2, t):
	return v1*(1.0-t)+v2*(t)
def m_abs(v):
	return v if (v >= 0) else -v
def v2_p(x,y):
	return [x,y]
def v2_eq(x,y):
	return x[0] == y[0] and x[1] == y[1]
def v2_z():
	return [0.0,0.0]
def v2_sz(v):
	v[0] = 0.0
	v[1] = 0.0
def v2_add(v1, v2):
	return [v1[0]+v2[0], v1[1]+v2[1]]
def v2_sub(v1, v2):
	return [v1[0]-v2[0], v1[1]-v2[1]]
def v2_dot(v1, v2):
	return v1[0]*v2[0]+v1[1]*v2[1]
def v2_lenSq(v1):
	return v2_dot(v1, v1)
def v2_len(v1):
	return math.sqrt(v2_lenSq(v1))
def v2_distSq(p1, p2):
	vec = v2_sub(p2, p1)
	return v2_lenSq(vec)
def v2_dist(p1, p2):
	vec = v2_sub(p2, p1)
	return v2_len(vec)
def v2_muls(v1, s):
	return [v1[0]*s, v1[1]*s]
def v2_neg(v1):
	return [ -v1[0], -v1[1] ]
def v2_copy(v):
	return [v[0], v[1]]
def v2_interp(v1, v2, t):
	return [m_interp(v1[i], v2[i], t[i]) for i in range(2)]
def v2_normalize(v1):
	l = v2_len(v1)
	if l != 0.0:
		return v2_muls(v1, 1.0/l)
	return v1
def v2_v_angle(vec):
	return math.atan2(vec[1], vec[0])
def v2_p_angle(v1,v2):
	return v2_v_angle(v2_sub(v2, v1))
def v2_rot(v1,a):
	c = math.cos(a)
	s = math.sin(a)
	ret = [ v1[0]*c + v1[1]*(-s), v1[0]*s + v1[1]*(c) ]
	return ret
def v2_orth(v1):
	return [ -v1[1], v1[0] ]
def v2_rot90(v1):
	return [ -v1[1], v1[0] ]
def v2_rotm90(v1):
	return [ v1[1], -v1[0] ]
def v2_projs(v, a):
	return v2_dot(v, a) / v2_dot(a, a)
def v2_proj(v, a):
	return v2_muls(a, v2_projs(v, a))
def v2_points_proj(a, b, c):
	return v2_add(a, v2_proj(v2_sub(c, a), v2_sub(b, a)))
def v2_proj_rest(v, a):
	return v2_sub(v, v2_proj(v, a))
def v2_points_proj_rest(a, b, c):
	return v2_proj_rest(v2_sub(c, a), v2_sub(b, a))
def Matrix(r,c,v):
	return [[v]*c for x in xrange(r)]
def Eye(r,c):
	M = Matrix(r,c,0.0)
	for i in range(r):
		M[i][i] = 1.0
	return M
def m2_zero():
	return Matrix(3, 3, 0.0)
def m2_id():
	return Eye(3, 3)
def m2_rigid(off, a):
	m = Eye(3,3)
	m[0][2] = off[0]
	m[1][2] = off[1]
	c = math.cos(a); s = math.sin(a);
	m[0][0] = c; m[0][1] = -s; m[1][0] = s; m[1][1] = c;
	return m
def m2_mul(m1, m2):
	p = Eye(3, 3)
	for i in range(3):
		for j in range(3):
			p[i][j] = m1[i][0]*m2[0][j]+m1[i][1]*m2[1][j]+m1[i][2]*m2[2][j]
	return p
def m2_mulp(m, v):
	p = [0.0, 0.0]
	p[0] = m[0][0]*v[0]+m[0][1]*v[1]+m[0][2]
	p[1] = m[1][0]*v[0]+m[1][1]*v[1]+m[1][2]
	return p
def m2_mulp_a(m, va):
	return [m2_mulp(m, v) for v in va]
def m2_mulv(m, v):
	p = [0.0, 0.0]
	p[0] = m[0][0]*v[0]+m[0][1]*v[1]
	p[1] = m[1][0]*v[0]+m[1][1]*v[1]
	return p
def m2_inv(m):
	mi = Eye(3, 3)
	mi[0][0]=m[1][1]
	mi[0][1]=m[1][0]
	mi[0][2]=-m[0][2]*m[1][1]-m[1][2]*m[1][0]
	mi[1][0]=m[0][1]
	mi[1][1]=m[0][0]
	mi[1][2]=-m[0][2]*m[0][1]-m[1][2]*m[0][0]
	return mi
def m2_orth(m):
	orth = v2_orth([m[0][0], m[0][1]])
	m[1][0] = orth[0]
	m[1][1] = orth[1]
	return m
def m2_get_trans(m):
	return [m[0][2], m[1][2]]
def m2_get_dir1(m):
	return [m[0][0], m[1][0]]
def m2_set_trans(m, off):
	m[0][2] = off[0]
	m[1][2] = off[1]
def m2_get_angle(m):
	return v2_v_angle([m[0][0], m[1][0]])
def m2_set_angle(m, a):
	c = math.cos(a); s = math.sin(a);
	m[0][0] = c; m[0][1] = -s; m[1][0] = s; m[1][1] = c;
#
g_mouse = [None, None]
g_buttons = {}
g_drag = {}
g_keys = {}
g_special_keys = {}
g_track = True
g_mouseFocus = True
g_frames = 0
g_fps_frames = 0
g_fps_t0 = 0
g_wh = [1024, 768]; g_wh = [800,600];
def disp_aspect(wh = None):  wh = wh if wh is not None else g_wh; return float(wh[0])/float(wh[1]);
g_zoom = 1.0
g_offset = [0.0, 0.0]
#
def rgb_to_f(rgb):
	return [x/255.0 for x in rgb]
k_white = [1.0, 1.0, 1.0]; k_green = [0.0, 1.0, 0.0]; k_blue = [0.0, 0.0, 1.0];
k_red = [1.0, 0.0, 0.0]; k_lgray = [0.7, 0.7, 0.7]; k_dgray = [0.3, 0.3, 0.3];
k_pink = rgb_to_f([245, 183, 177]); k_bluish1 = rgb_to_f([30, 136, 229]);
k_orange = rgb_to_f([251, 140, 0]);
k_e_1 = [1.0, 0.0]; k_e_2 = [0.0, 1.0]; k_e2 = [k_e_1, k_e_2];
def style0_color3f(r,g,b):
	return (r, g, b)
def style1_color3f(r,g,b):
	return (1.0-r, 1.0-g, 1.0-b)
style_color3f = style0_color3f
def style_glColor3f(r,g,b):
	glColor3f(*style_color3f(r,g,b))
#
def screen_to_draw(pt, wh = None):
	x,y,z = gluUnProject(pt[0], (wh if wh else g_wh)[1] - pt[1], 0);
	return [x,y];
def size_to_draw(sz, wh = None):
	p0 = screen_to_draw(v2_z(), wh); p = screen_to_draw(sz, wh); return v2_sub(p, p0);
#
def draw_strings(strs, x0, y0, col, wh = None, anchor = 'lt', fill_col = None):
	def get_string_height(): return 13
	def get_string_size(str): return [len(str)*8, get_string_height()]
	wh = wh if wh is not None else g_wh
	if (anchor in ['cc', 'ct', 'lb']):
		bounds = [0, 0]
		for str in strs:
			sz = get_string_size(str)
			bounds[0] = m_max(bounds[0], sz[0]); bounds[1] = bounds[1] + sz[1]
		dbounds = size_to_draw(bounds, wh)
		if (anchor[0] == 'c'):
			x0 = x0 - 0.5*dbounds[0]
		if (anchor[1] == 'c'):
			y0 = y0 - 0.5*dbounds[1]
		elif (anchor[1] == 'b'):
			y0 = y0 - dbounds[1]
	style_glColor3f(col[0],col[1],col[2])
	h = size_to_draw([0.0, get_string_height()], wh)[1]
	glPushMatrix();
	glTranslatef(x0, y0+h, 0); glRasterPos2f(0, 0);
	si = 0
	for str in strs:
		for c in str:
			glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(c))
		sz = size_to_draw(get_string_size(str), wh)
		glTranslatef(0, h, 0); glRasterPos2f(0, 0);
		si = si+1
	glPopMatrix()
#
def draw_verts(verts, mode):
	glBegin(mode)
	for p in verts:
		glVertex2f(p[0], p[1])
	glEnd()
def trace_poly(poly, col = k_white):
	style_glColor3f(col[0],col[1],col[2])
	draw_verts(poly, GL_LINE_STRIP)
def fill_poly(poly, col = k_white):
	if len(poly) == 2:
		return trace_poly(poly, col)
	style_glColor3f(col[0],col[1],col[2])
	draw_verts(poly, GL_POLYGON)
def point_poly(poly, col = k_white):
	style_glColor3f(col[0],col[1],col[2])
	glPointSize(3)
	draw_verts(poly, GL_POINTS)
def draw_lines(lines, col = k_white):
	style_glColor3f(col[0],col[1],col[2])
	draw_verts(lines, GL_LINES)
def draw_poly_with_mode(mode, poly, col = k_white):
	if mode == 2:
		fill_poly(poly,col)
	elif mode == 1:
		trace_poly(poly,col)
	else:
		point_poly(poly,col)
#
def make_wh_poly(rwh):
	rw,rh = rwh[0], rwh[1]
	return [ v2_p(-rw, -rh), v2_p(-rw, rh), v2_p(rw, rh), v2_p(rw, -rh), v2_p(-rw, -rh) ]
def make_w_poly(rw):
		return [ v2_p(-rw, 0.0), v2_p(rw, 0.0) ]
def make_h_poly(rh):
		return [ v2_p(0.0, -rh), v2_p(0.0, rh) ]
def make_tri_poly(wh):
	return [v2_p(0,0), v2_p(wh[0], wh[1]), v2_p(wh[0], -wh[1]), v2_p(0,0)]
def make_body(poly, poly_type, xfm, col = k_white):
	return { 'poly':poly, 'poly_type': poly_type, 'xfm':xfm, 'col':col, 'fill':2, 'phys':None }
def make_col(r,g,b):
	return [r,g,b]
def draw_bodies(bodies):
	for b in bodies:
		poly = m2_mulp_a(b['xfm'], b['poly'])
		if b['fill'] == 2:
			fill_poly(poly, b['col'])
		elif b['fill'] == 1:
			trace_poly(poly, b['col'])
		else:
			point_poly(poly, b['col'])
def draw_stars(stars, col = k_white):
	if len(stars):
		style_glColor3f(col[0],col[1],col[2])
		glBegin(GL_LINES)
		for s in stars:
			for p in s:
				glVertex2f(p[0], p[1])
		glEnd()
def make_star(r, boxr = 0.0):
	star =  [ v2_p(-r, 0), v2_p(r, 0), v2_p(0, -r), v2_p(0, r) ]
	if boxr > 0.0:
		r = boxr
		star.extend( [v2_p(-r, -r), v2_p(-r, r), v2_p(-r, r), v2_p(r, r), v2_p(r, r), v2_p(r, -r), v2_p(r, -r), v2_p(-r, -r) ] )
	return star
#
def handleKeys(key, x, y):
	global g_keys
	g_keys[key] = {'wpt':[x,y] }
def handleSpecialKeys(key, x, y):
	global g_special_keys
	g_special_keys[str(key)] = {'wpt':[x,y] }
def handleMouseAct(button, mode, x, y):
	global g_buttons
	g_buttons[button] = {'button': button, 'mode':mode, 'wpt':[x,y] }
	if mode == 0:
		g_drag[button] = g_buttons[button]; g_drag[button]['wpts'] = [g_buttons[button]['wpt']]*3; g_drag[button]['active'] = True;
	elif mode == 1:
		if button in g_drag:
			g_drag[button]['active'] = False
def handleMousePassiveMove(x, y):
	global g_mouse
	if (g_mouseFocus):
		g_mouse = [x,y]
	for d in [xx for xx in g_drag.values() if xx['active']]:
		# wpts: src, curr, prev
		d['wpts'][2] = d['wpts'][1]
		d['wpts'][1] = [x,y]
def handleMouseMove(x, y):
	handleMousePassiveMove(x, y)
def handleMouseEntry(state):
	global g_mouseFocus
	g_mouseFocus = (state == GLUT_ENTERED)
def dbg_mouse():
	for d in [x for x in g_drag.values() if x['active']]:
		print '({},{}) -> ({},{})'.format(d['wpts'][0][0], d['wpts'][0][1], d['wpts'][1][0], d['wpts'][1][1])
def handleReshape(w, h):
	glutDisplayFunc(lambda: display(w, h))
	glutPostRedisplay()
def main_realtime():
	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
	glutInitWindowSize(g_wh[0], g_wh[1])
	glutCreateWindow('proto1')
	#
	glutReshapeFunc(handleReshape)
	glutIdleFunc(glutPostRedisplay)
	glutMouseFunc(handleMouseAct)
	glutPassiveMotionFunc(handleMousePassiveMove)
	glutMotionFunc(handleMouseMove)
	glutEntryFunc(handleMouseEntry)
	glutKeyboardFunc(handleKeys)
	glutSpecialFunc(handleSpecialKeys)
	glutMainLoop()
def start_display(w, h):
	global g_wh, g_frames
	g_wh = [w,h]
	aspect = disp_aspect(g_wh)
	glViewport(0, 0, w, h)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glOrtho(-1*aspect*g_zoom+g_offset[0], 1*aspect*g_zoom+g_offset[0], -1*g_zoom+g_offset[1], 1*g_zoom+g_offset[1], -1, 1)
	#
	glMatrixMode(GL_MODELVIEW);
	glLoadIdentity()
	#
	(r,g,b) = style_color3f(0,0,0)
	glClearColor(r,g,b, 0.0)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	#
	g_frames = g_frames+1
def end_display():
	global g_fps_frames, g_fps_t0
	glutSwapBuffers()
	t1 = glutGet(GLUT_ELAPSED_TIME)
	g_fps_frames = g_fps_frames+1
	if (g_fps_t0 <= 0) or (t1-g_fps_t0 >= 1000.0):
		g_fps = (1000.0 * float(g_fps_frames)) / float(t1-g_fps_t0)
		g_fps_t0 = t1; g_fps_frames = 0;
	#print (t1-t0)
def display(w, h):
	start_display(w, h)
	do_display()
	end_display()
def b2_raycast_all(physw, pts):
	coll_hits = []
	class RayCastCallback(b2RayCastCallback):
		 def ReportFixture(self, fixture, point, normal, fraction):
			 coll_hits.append([point, normal])
			 return 1.0
	if v2_distSq(*pts) > 0:
		physw.RayCast(RayCastCallback(), point1=pts[0], point2=pts[1])
	return coll_hits
def b2_raycast_closest(physw, pts):
	last_hit = [None]
	class RayCastCallback(b2RayCastCallback):
		 def ReportFixture(self, fixture, point, normal, fraction):
			 last_hit[0] = [point, normal]
			 return fraction
	if v2_distSq(*pts) > 0:
		physw.RayCast(RayCastCallback(), point1=pts[0], point2=pts[1])
	return last_hit[0]
def find_close_feature(pt, features, max_dist = None):
	best_dsq = 0; best_i = -1;
	max_dist_sq = max_dist*max_dist if max_dist is not None else None
	for i, feat in enumerate(features):
		dsq = v2_distSq(pt, m2_get_trans(feat['xfm']) )
		if max_dist_sq is not None and dsq <= max_dist_sq:
			return i
		if best_i == -1 or dsq < best_dsq:
			best_i = i; best_dsq = dsq;
	return best_i
g_app_mode = ''
g_app_scene = ''
g_design_allow_lines = False
g_raycast_test = False
def save_scene(scene, fpath):
	file = open(fpath, 'w+')
	fill_scene_phys(scene, True)
	scene['physw'] = None
	pickle.dump(scene, file)
	print 'saved to [{}]'.format(fpath)
def load_scene(fpath):
	file = open(fpath, 'r')
	scene = pickle.load(file)
	scene['physw'] = b2World()
	fill_scene_phys(scene)
	print 'loaded from [{}]'.format(fpath)
	return scene
def gen_empty_scene(settings):
	k_cm = 2.0 / g_wh[1]
	random.seed(0)
	static_bodies = []
	features = []
	objects = []
	physw = b2World()
	scene = {'static_bodies':static_bodies, 'features':features, 'objects':objects, 'physw':physw, 'settings':settings}
	return scene
def make_body_phys(physw, body):
	bd = physw.CreateStaticBody(position=m2_get_trans(body['xfm']), angle=m2_get_angle(body['xfm']))
	if len(body['poly']) == 2 or body['poly_type'] == 'line':
		bd.CreateEdgeFixture(vertices=body['poly'])
	else:
		bd.CreatePolygonFixture(vertices=body['poly'])
	return bd
def fill_scene_phys(scene, clear=False):
	physw = scene['physw']
	for coll in [ scene['static_bodies'] ]:
		for b in coll:
			b['phys'] = None if clear else make_body_phys(physw, b)
def fill_feature_btree(scene):
	print 'Filling feature tree...',
	btree = make_aabb_btree()
	features = scene['features']
	for i,feat in enumerate(features):
		feat['i'] = i; feat['processed'] = False;
	remaining = features[:]
	meter = scene['settings']['meter']
	while len(remaining) > 0:
		feat = remaining[0]
		box = aabb_inflate(point_to_aabb(m2_get_trans(feat['xfm'])), meter)
		box_feats = [feat]
		if len(remaining) > 1:
			for j,featj in enumerate(remaining[1:]):
				jbox = point_to_aabb(m2_get_trans(featj['xfm']))
				if aabb_equals(aabb_inter(box, jbox), jbox):
					box_feats.append(featj)
		for f in box_feats:
			f['processed'] = True
		btree_insert(btree, box, [x['i'] for x in box_feats])
		remaining = [x for x in features if x['processed'] == False]
	scene['feature_btree'] = btree
	print 'done. [features: {}] [tree size: {}]'.format(len(features), btree_size(btree))
def gen_scene_1(settings):
	k_cm = 2.0 / g_wh[1]
	random.seed(0)
	static_bodies = []
	static_col = k_green; feat_col = k_dgray; rig_col = k_blue; obj_col = k_blue;
	#
	static_bodies.append( make_body( make_w_poly(0.99+0.01), 'line', m2_rigid([0,-0.9], 0), static_col ) )
	static_bodies.append( make_body( make_h_poly(0.9+0.01), 'line', m2_rigid([-0.99, 0], 0), static_col ) )
	static_bodies.append( make_body( make_w_poly(0.99+0.01), 'line', m2_rigid([0,0.9], 0), static_col ) )
	static_bodies.append( make_body( make_h_poly(0.9+0.01), 'line', m2_rigid([0.99, 0], 0.0), static_col ) )
	#
	static_bodies.append( make_body( make_w_poly(0.46), 'line', m2_rigid([-0.2,-0.45], 0), static_col ) )
	static_bodies.append( make_body( make_w_poly(0.46), 'line', m2_rigid([-0.2, 0.25], 0), static_col ) )
	static_bodies.append( make_body( make_h_poly(0.45/2), 'line', m2_rigid([0.46-0.2-0.01,-0.25], 0), static_col ) )
	static_bodies.append( make_body( make_w_poly(0.46), 'line', m2_rigid([-1.0+0.46,-0.1], 0), static_col ) )
	#
	features = []
	feature_r = settings['feature_r']
	for i in range(settings['feature_count']):
		rpt = v2_p( 0.9 * (random.random()*2.0-1.0), 0.9 * (random.random()*2.0-1.0) )
		features.append( make_body( make_wh_poly([feature_r, feature_r]), 'convex', m2_rigid(rpt, 0), feat_col ) )
		features[-1]['xfm'] = m2_rigid(rpt, random.random() * math.pi)
	#
	objects = []
	objects.append( make_body( make_wh_poly([k_cm*80, k_cm*8]), 'convex', m2_rigid(v2_p(0.3, -0.8), 0), obj_col ) )
	if len(objects):
		obj = objects[-1]
		obj['fill'] = 1
		feat_i = find_close_feature( v2_add(m2_get_trans(objects[-1]['xfm']), [-0.3, 0.0]), features, k_cm*10 )
		obj['feat_i'] = feat_i
		obj['obj_feat'] = m2_mul( m2_inv( features[feat_i]['xfm'] ), obj['xfm'] )
	#
	scene = {'static_bodies':static_bodies, 'features':features, 'objects':objects, 'settings':settings}
	return scene
#
def aabb_inflate(vol, rad):
	return [vol[0]-rad, vol[1]-rad, vol[2]+rad, vol[3]+rad]
def aabb_size(vol):
	# min_1, min_2, max_1, max_2
	return  m_max(vol[2]-vol[0], 0.0) * m_max(vol[3]-vol[1], 0.0)
def aabb_radius(vol):
	return m_max(m_max(vol[2]-vol[0], 0.0), m_max(vol[3]-vol[1], 0.0))
def aabb_mM(vol):
	return [vol[:2], vol[2:]]
def aabb_equals(vol1, vol2):
	return all([vol1[i] == vol2[i] for i in range(4)])
def aabb_inter(vol1, vol2):
	return [ m_max(vol1[0], vol2[0]), m_max(vol1[1], vol2[1]), m_min(vol1[2], vol2[2]), m_min(vol1[3], vol2[3])  ]
def aabb_union(vol1, vol2):
	return [ m_min(vol1[0], vol2[0]), m_min(vol1[1], vol2[1]), m_max(vol1[2], vol2[2]), m_max(vol1[3], vol2[3])  ]
def make_aabb_btree():
	return {'func_vol_size':aabb_size, 'func_vol_inter':aabb_inter, 'func_vol_union':aabb_union, 'root':None}
def point_to_aabb(pt):
	return [pt[0], pt[1], pt[0], pt[1]]
def points_to_aabb(pts):
	return reduce(lambda x, y: aabb_union(x,y), [point_to_aabb(x) for x in pts])
def btree_intersecting_leaves(tree, volume):
	def btree_intersects(func_vol_size, func_vol_inter, node, vol, inter_leaves):
		if func_vol_size(func_vol_inter(node['vol'], vol)) > 0:
			if node['is_leaf']:
				inter_leaves.append(node)
			else:
				btree_intersects(func_vol_size, func_vol_inter, node['l'], vol, inter_leaves)
				btree_intersects(func_vol_size, func_vol_inter, node['r'], vol, inter_leaves)
		else:
			return
	inter_leaves = []
	if tree['root'] is not None:
		btree_intersects(tree['func_vol_size'], tree['func_vol_inter'], tree['root'], volume, inter_leaves)
	return inter_leaves
def btree_insert(tree, volume, data = None):
	if tree['root'] is None:
		tree['root'] = { 'is_leaf':True, 'vol':volume, 'data':data, 'p':None }
	else:
		inter_leaves = btree_intersecting_leaves(tree, volume)
		if len(inter_leaves) == 0:
			lr_vol = tree['func_vol_union']( tree['root']['vol'], volume )
			new_l = { 'is_leaf':True, 'vol':volume, 'data':data }
			new_r = tree['root'];
			new_root = { 'is_leaf':False, 'vol':lr_vol, 'l':new_l, 'r':new_r, 'p':None }
			new_l['p'] = new_root; new_r['p'] = new_root;
			tree['root'] = new_root
		else:
			func_vol_size = tree['func_vol_size']; func_vol_inter = tree['func_vol_inter'];
			vol_sizes = [ func_vol_size(func_vol_inter(x['vol'], volume)) for x in inter_leaves ]
			by_size = sorted( range(len(vol_sizes)), key = lambda x: vol_sizes[x] )
			split_leaf = inter_leaves[by_size[0]]
			lr_vol = tree['func_vol_union']( split_leaf['vol'], volume )
			new_l = { 'is_leaf':True, 'vol':volume, 'data':data, 'p':split_leaf }
			new_r = { 'is_leaf':True, 'vol':split_leaf['vol'], 'data':split_leaf['data'], 'p':split_leaf }
			split_leaf['is_leaf'] = False; split_leaf['vol'] = lr_vol;
			split_leaf['l'] = new_l; split_leaf['r'] = new_r;
			walk_c = split_leaf; func_vol_union = tree['func_vol_union'];
			while walk_c['p'] is not None:
				walk_c['p']['vol'] = func_vol_union(walk_c['p']['vol'], walk_c['vol'])
				walk_c = walk_c['p']
def btree_size(tree):
	def btree_node_size(node):
		return 1 + 0 if node['is_leaf'] else (btree_node_size(node['l']) + btree_node_size(node['r']))
	return btree_node_size(tree['root']) if tree['root'] is not None else 0
#
g_scene = None
def do_display():
	global g_scene
	k_cm = 2.0 / 600.0; k_meter = 100*k_cm;
	if g_scene is None:
		settings = { 'rand_pos_scl':(k_cm*3.0)*1.0, 'rand_ang_scl': ((0.5*math.pi)/40.0) * 1.0, 'rig_wh':v2_muls([300, 100], 2.0* k_cm* (g_wh[1]/800.0) ), 'feature_r':k_cm*2.0, 'feature_count':1000, 'map_set_sz':4,
					'sensor_fov':(15.0 / 180.0)*math.pi, 'sensor_rays':20, 'sensor_len':k_meter*3.0, 'meter':k_meter, 'unit':k_cm }
		if g_app_mode == 'design':
			if g_app_scene != '' and os.path.exists(g_app_scene):
				g_scene = load_scene(g_app_scene)
			else:
				g_scene = gen_empty_scene(settings)
		else:
			if g_app_scene != '' and os.path.exists(g_app_scene):
				g_scene = load_scene(g_app_scene)
			else:
				g_scene = gen_scene_1(settings)
		if g_scene.get('physw', None) is None:
			g_scene['physw'] = b2World()
			fill_scene_phys(g_scene)
		if g_scene.get('feature_btree', None) is None:
			fill_feature_btree(g_scene)
		g_scene['rig'] = {'path':[], 'max_path':140, 'pos': v2_z(), 'angle':0, 'poly':[]}
		g_scene['tracking'] = None
		g_scene['map'] = {'trackings':[], 'track_graph':[], 'roots':[]}
		g_scene['sensor_state'] = { 'shot_tree':make_aabb_btree() }
		g_scene['stats'] = { 'map_size':0, 'sensor_tree_size':0 }
		g_scene['scene_offset'] = { 'active':False }
		g_scene['mouse'] = { 'track_pts':[], 'max_track_pts':140, 'tracking':False }
		g_scene['design'] = { 'active_drag':False, 'active_drag_body_col':k_pink, 'static_col':k_blue }
		g_scene['show'] = { 'static':True, 'features':True, 'map':True, 'track_feat_path':True, 'track_map_path':False, 'rig_path':True, 'rig_sensor':True }
		g_scene['show_keys'] = { '1':'static', '2':'features', '3':'rig_path', '4':'map', '5':'track_feat_path', '6':'rig_sensor' }
		g_scene['on'] = { 'sensor_shot':True, 'cam_follow':True }
		g_scene['on_keys'] = { '9':'sensor_shot', '7':'cam_follow' }
		g_scene['once'] = { 'sensor_shot':False, 'design_save':False, 'design_gen_features':False }
		g_scene['once_keys'] = { '8':'sensor_shot', '12':'design_save', '11':'design_gen_features' }
		g_scene['scroll'] = { 'modes':['zoom', 'vision dist.', 'sensor dist.', 'sensor fov.', 'sensor rays', 'pos. error', 'ang. error'], 'mode':0 }
		g_scene['tracking_converge'] = { 'conv_pos':None, 'conv_max_time':4.0, 'conv_value':0.0 }
	scene = g_scene
	#
	if ('\x1b' in g_keys.keys()):
		glutLeaveMainLoop()
		sys.exit(0)
	if ('\t' in g_keys.keys()):
		scene['scroll']['mode'] = (scene['scroll']['mode']+1) % len(scene['scroll']['modes'])
	for coll, coll_keys in [['show', 'show_keys'], ['on', 'on_keys'], ['once', 'once_keys']]:
		for sk in g_special_keys.keys():
			name_key = g_scene[coll_keys].get(sk, '')
			if name_key != '':
				scene[coll][name_key] = not scene[coll][name_key]
	#
	def dbg_raycast():
		for d in [xx[1] for xx in g_drag.items() if xx[0] == 1 and xx[1]['active'] ]:
	 		pts = [screen_to_draw(x) for x in d['wpts'][:2]]
			trace_poly(pts, k_white)
			if True:
				hits = b2_raycast_all(scene['physw'], pts)
				if len(hits):
				#	print hits
					star = make_star(10*k_cm, 5*k_cm); hstars = [];
					for hit in hits:
						hstars.append(m2_mulp_a(m2_rigid(hit[0], v2_v_angle(hit[1]) + math.pi / 4.0), star))
					draw_stars(hstars, k_red)
	def track_mouse():
		if 't' in g_keys:
			scene['mouse']['tracking'] = not scene['mouse']['tracking']
		track =	scene['mouse']['track_pts']
		if scene['mouse']['tracking']:
			if g_mouseFocus and g_mouse[0] is not None:
				if v2_dist(scene.get('mouse_last', g_mouse), g_mouse) > 3.0 * k_cm:
					track.append(screen_to_draw(g_mouse))
				if len(track) > scene['mouse']['max_track_pts']:
					scene['mouse']['track_pts'] = track[1:]
				scene['mouse_last'] = g_mouse
				trace_poly( m2_mulp_a(m2_rigid(screen_to_draw(g_mouse), 0), make_wh_poly([k_cm*5, k_cm*5])) )
		else:
			if len(track) >= 2:
				scene['rig']['path'] = copy.copy(track)
				del track[:]
		if len(track) >= 2:
			trace_poly(track, [1.0, 1.0, 0.0])
	def handle_scene_zoom():
		global g_zoom
		zd = 3.0/4.0 if 3 in g_buttons else (4.0/3.0 if 4 in g_buttons else 1.0)
		g_zoom = m_min(m_max(g_zoom * zd, 0.05), 20)
	def handle_input_scroll():
		def do_generic_scroll(precision, zmin, zmax, scroll_key):
			zd = precision if 3 in g_buttons else (1.0/precision if 4 in g_buttons else 1.0)
			if scroll_key not in scene['scroll']:
				scene['scroll'][scroll_key] = 1.0
			zoom = scene['scroll'][scroll_key]; zoom = m_min(m_max(zoom * zd, zmin), zmax);
			scene['scroll'][scroll_key] = zoom; scene['scroll']['value'] = '{0:.0f}%'.format(zoom*100);
			return zoom
		scroll_mode = scene['scroll']['modes'][scene['scroll']['mode']]
		scene['scroll']['value'] = ''
		if scroll_mode == 'zoom':
			handle_scene_zoom()
			scene['scroll']['value'] = '{0:.0f}%'.format(1.0/g_zoom*100)
		elif scroll_mode == 'vision dist.':
			if 'base_rig_wh' not in scene['scroll']:
				scene['scroll']['base_rig_wh'] = copy.copy( scene['settings']['rig_wh'] )
			zoom = do_generic_scroll(1.2, 0.2, 5.0, 'zoom_rig_wh')
			scene['settings']['rig_wh'] = v2_muls(scene['scroll']['base_rig_wh'], zoom)
		elif scroll_mode == 'sensor dist.':
			if 'base_sensor_len' not in scene['scroll']:
				scene['scroll']['base_sensor_len'] = copy.copy( scene['settings']['sensor_len'] )
			zoom = do_generic_scroll(1.1, 0.2, 3.0, 'zoom_sensor_len')
			scene['settings']['sensor_len'] = scene['scroll']['base_sensor_len'] * zoom
		elif scroll_mode == 'sensor fov.':
			if 'base_sensor_fov' not in scene['scroll']:
				scene['scroll']['base_sensor_fov'] = copy.copy( scene['settings']['sensor_fov'] )
			zoom = do_generic_scroll(1.4, 0.4, 20.0, 'zoom_sensor_fov')
			scene['settings']['sensor_fov'] = scene['scroll']['base_sensor_fov'] * zoom
		elif scroll_mode == 'sensor rays':
			if 'base_sensor_rays' not in scene['scroll']:
				scene['scroll']['base_sensor_rays'] = copy.copy( scene['settings']['sensor_rays'] )
			zoom = do_generic_scroll(1.1, 0.4, 5.0, 'zoom_sensor_rays')
			scene['settings']['sensor_rays'] = int(scene['scroll']['base_sensor_rays'] * zoom)
			scene['scroll']['value'] = scene['settings']['sensor_rays']
		elif scroll_mode == 'pos. error':
			if 'base_pos_error' not in scene['scroll']:
				scene['scroll']['base_pos_error'] = copy.copy( scene['settings']['rand_pos_scl'] )
			zoom = do_generic_scroll(1.1, 0.0, 20.0, 'zoom_pos_error')
			scene['settings']['rand_pos_scl'] = scene['scroll']['base_pos_error'] * zoom
		elif scroll_mode == 'ang. error':
			if 'base_ang_error' not in scene['scroll']:
				scene['scroll']['base_ang_error'] = copy.copy( scene['settings']['rand_ang_scl'] )
			zoom = do_generic_scroll(1.4, 0.0, 20.0, 'zoom_ang_error')
			scene['settings']['rand_ang_scl'] = scene['scroll']['base_ang_error'] * zoom
	def handle_draw_strings():
		lines = []
		lines.append( '[map:{}] [sensor:{}]'.format(scene['stats']['map_size'], scene['stats']['sensor_tree_size']) )
		lines.append( 'scroll: [{}:{}]'.format(scene['scroll']['modes'][scene['scroll']['mode']], scene['scroll'].get('value','') ) )
		draw_strings(lines, -1.0*g_zoom*disp_aspect()+g_offset[0], 1.0*g_zoom+g_offset[1], k_white)
	def handle_scene_offset():
		global g_offset
		drag = g_drag.get(1, None)
		if drag is not None and drag['active']:
			if scene['scene_offset']['active'] == False:
				scene['scene_offset']['orig_offset'] = g_offset
				scene['scene_offset']['active'] = True
			pts = [screen_to_draw(x) for x in drag['wpts']]
			g_offset = v2_add(scene['scene_offset']['orig_offset'], v2_sub(pts[0], pts[1]))
		else:
			scene['scene_offset']['active'] = False
		if 'r' in g_keys:
			g_offset = v2_z()
	def make_rig_poly(xfm):
		def make_rig_shape(rwh):
			#return make_tri_poly(rwh)
			rw,rh = rwh[0]*0.5, rwh[1]
			return [ v2_p(0, -rh), v2_p(0, rh), v2_p(rw, rh), v2_p(rw, -rh), v2_p(0, -rh) ]
		return m2_mulp_a(xfm,  make_rig_shape(scene['settings']['rig_wh']))
		#return m2_mulp_a(xfm,  make_tri_poly(scene['settings']['rig_wh']))
	def make_rig_poly_pa(pos, angle):
		return make_rig_poly( m2_rigid(pos, angle) )
	def handle_rig():
		rig = scene['rig']
		def handle_track(rig_pt):
			if 0 in g_drag and g_drag[0]['active']:
				if g_mouseFocus and g_mouse[0] is not None:
					mpt = screen_to_draw(g_mouse)
					if (rig_pt is None) or (v2_dist(rig_pt, mpt) > 3.0 * k_cm):
						rig['path'].append(mpt)
						if scene['on']['cam_follow']:
							if len(rig['path']) > 7:
								angles = [ v2_v_angle(v2_sub(rig['path'][-x], rig['path'][-x-1])) for x in range(1,7)  ]
								#angles = [x if x >= 0 else x+2.0*math.pi for x in angles]
								angles = sorted([2.0*math.pi + x for x in angles])[:-2]
								rig['angle'] = angles[len(angles)/2]
					if len(rig['path']) > rig['max_path']:
						rig['path'] = rig['path'][1:]
		def handle_rig_xfm(rig_pt):
			changed = False
			if 2 in g_drag and g_drag[2]['active']:
				drag = g_drag[2]
				pts = [screen_to_draw(x) for x in drag['wpts']]
				if v2_dist(rig_pt, pts[1]) > 10 * k_cm:
					ca = v2_p_angle(rig_pt, pts[1])
					if ca != rig['angle']:
						rig['angle'] = ca; changed = True
				else:
					trace_poly([screen_to_draw(x) for x in drag['wpts']], k_blue)
			if rig['pos'] != rig_pt:
				rig['pos'] = rig_pt; changed = True
			return changed
		handle_track(rig['path'][-1] if len(rig['path']) else None)
		if len(rig['path']):
			if scene['show']['rig_path']:
				trace_poly(rig['path'], [1.0, 1.0, 1.0])
			xfm_changed = handle_rig_xfm(rig['path'][-1])
			if xfm_changed or len(rig['poly']) == 0:
				rig_verts = make_rig_poly_pa(rig['pos'], rig['angle'])
				rig['poly'] = rig_verts
				pshape = b2PolygonShape(vertices = rig_verts); pxfm = b2Transform(); pxfm.SetIdentity();
				vis = []; vis_pts = [];
				if True:
					vol_pts = []
					feature_btree = scene.get('feature_btree', None)
					if feature_btree is not None:
						rig_aabb = points_to_aabb(rig_verts)
						inter_leaves = btree_intersecting_leaves(feature_btree, rig_aabb)
						for leaf in inter_leaves:
							#trace_poly( [ v2_p(leaf['vol'][0], leaf['vol'][1]), v2_p(leaf['vol'][2], leaf['vol'][3]) ] )
							for feat_i in leaf['data']:
								feat = scene['features'][feat_i]; feat_pt = m2_get_trans(feat['xfm']);
								if pshape.TestPoint( pxfm, feat_pt ):
									vis_pt2 = v2_add(rig['pos'], v2_muls( v2_sub(feat_pt, rig['pos']), 0.98 ))
									obstacle = b2_raycast_closest(scene['physw'], [rig['pos'], vis_pt2])
									if obstacle is None:
										vis.append(feat_i); vis_pts.append(feat_pt)
					else:
						for i, feat in enumerate(scene['features']):
							feat_pt = m2_get_trans(feat['xfm'])
							if pshape.TestPoint( pxfm, feat_pt ):
								vol_pts.append((i, feat_pt))
					for feat_i, feat_pt in vol_pts:
						vis_pt2 = v2_add(rig['pos'], v2_muls( v2_sub(feat_pt, rig['pos']), 0.98 ))
						obstacle = b2_raycast_closest(scene['physw'], [rig['pos'], vis_pt2])
						if obstacle is None:
							vis.append(feat_i); vis_pts.append(feat_pt)
				rig['vis'] = vis; rig['vis_set'] = set(vis); rig['vis_pts'] = vis_pts;
			trace_poly(rig['poly'], k_blue )
			point_poly(rig['vis_pts'], k_red)
	def gen_tracking():
		rig = scene['rig']
		if len(rig['path']) == 0:
			return None
		tracking = { 'pos':rig['pos'], 'angle':rig['angle'], 'vis':rig['vis'], 'vis_set':rig['vis_set'], 'seed':time.time(), 'resolved':None }
		features = [scene['features'][x] for x in tracking['vis']]
		vis_pts = [m2_get_trans(x['xfm']) for x in features]
		vis_pts_trans = zip(*vis_pts)
		vis_pt_avg = [sum(xi)/float(len(xi)) for xi in vis_pts_trans]
		tracking['vis_pts'] = vis_pts; tracking['vis_pt_avg'] = vis_pt_avg;
		return tracking
	def vec_randomize(v, scl):
		return [x + (0.5*(-1.0 + 2.0*random.random()))*scl for x in v]
	def m2_rigid_randomize(pa, rand_settings):
		return m2_rigid(vec_randomize(pa[0], rand_settings[0]), vec_randomize([pa[1]], rand_settings[1])[0])
	def resolve_tracking(tracking, conv_value):
		if len(tracking['vis']) == 0:
			return None
		rand_settings = [x*(1.0-conv_value) for x in [g_scene['settings']['rand_pos_scl'], g_scene['settings']['rand_ang_scl']]]
		resolved = {}
		random.seed(tracking['seed'])
		features = [scene['features'][x] for x in tracking['vis']]
		vis_pts = [m2_get_trans(x['xfm']) for x in features]
		vis_pts_trans = zip(*vis_pts)
		vis_pt_avg = [sum(xi)/float(len(xi)) for xi in vis_pts_trans]
		map_frame = m2_rigid(vis_pt_avg, random.random()*math.pi)
		map_iframe = m2_inv(map_frame)
		resolved['map_frame'] = map_frame
		resolved['map_iframe'] = map_iframe
		rig_frame = m2_rigid_randomize([tracking['pos'], tracking['angle']], rand_settings)
		rig_local_xfm = m2_mul(map_iframe, rig_frame)
		rig_local_ixfm = m2_inv(rig_local_xfm)
		resolved['rig_frame'] = rig_frame
		resolved['rig_local_xfm'] = rig_local_xfm
		resolved['rig_local_ixfm'] = rig_local_ixfm
		feat_local_xfms = []; feat_rig_xfms = []; feat_frames = [];
		for feat in features:
			feat_pa = [m2_get_trans(feat['xfm']), m2_get_angle(feat['xfm'])]
			feat_frame = m2_rigid_randomize(feat_pa, rand_settings)
			feat_frames.append(feat_frame)
			feat_local_frame = m2_mul(map_iframe, feat_frame)
			feat_local_xfms.append( feat_local_frame )
			feat_rig_frame = m2_mul(rig_local_ixfm, feat_local_frame)
			feat_rig_xfms.append( feat_rig_frame )
		resolved['feat_local_xfms'] = feat_local_xfms
		resolved['feat_rig_xfms'] = feat_rig_xfms
		resolved['feat_frames'] = feat_frames
		resolved['feat_pts'] = [m2_get_trans(x) for x in feat_frames]
		return resolved
	def draw_tracking(tracking):
		resolved = tracking['resolved']
		if resolved is not None:
			rig_verts = make_rig_poly( resolved['rig_frame'] )
			trace_poly(rig_verts, k_pink )
			point_poly(resolved['feat_pts'], k_pink)
	def draw_object_tracking(tracking, objects):
		def try_index(ar, ar_el):
			try:
				return ar.index(ar_el)
			except ValueError:
				return -1
		resolved = tracking['resolved']
		for obj in objects:
			if obj['feat_i'] >= 0:
				trace_poly( [ m2_get_trans(obj['xfm']), m2_get_trans(scene['features'][obj['feat_i']]['xfm']) ], k_blue )
				if resolved is not None:
					vis_i = try_index(tracking['vis'], obj['feat_i'])
					if vis_i >= 0:
						#real_xfm = m2_mul( g_scene['features'][obj['feat_i']]['xfm'], obj['obj_feat'] )
						track_xfm = m2_mul( resolved['feat_frames'][vis_i] , obj['obj_feat'] )
						draw_poly_with_mode(obj['fill'], m2_mulp_a(track_xfm, obj['poly']), k_pink)
					else:
						path_jitter = obj.get('path_jitter', v2_z());  path_col = obj.get('path_col', k_orange);
						map_path = find_map_path_to_feature(tracking, obj['feat_i'])
						if map_path is not None:
							#print map_path
							if scene['show']['track_map_path']:
								trace_poly( [ v2_add(scene['map']['trackings'][x]['vis_pt_avg'], path_jitter) for x in map_path ],  path_col)
							feat_path, path_feat_rig_xfm = map_path_to_feature_path(tracking, obj['feat_i'], map_path, True)
							if scene['show']['track_feat_path']:
								trace_poly( [ v2_add( m2_get_trans(scene['features'][x]['xfm']), path_jitter ) for x in feat_path ],  path_col)
							track_xfm = m2_mul( resolved['rig_frame'],  m2_mul(path_feat_rig_xfm, obj['obj_feat']) )
							draw_poly_with_mode(obj['fill'], m2_mulp_a(track_xfm, obj['poly']), k_pink)
	def handle_tracking():
		def handle_tracking_converge(tracking):
			state = scene['tracking_converge']
			if state['conv_pos'] is not None and (v2_eq(state['conv_pos'], tracking['pos']) and state['conv_ang'] == tracking['angle']):
				state['conv_t'] = time.time()
				state['conv_value'] = m_max(0.0, m_min(1.0, (state['conv_t'] - state['conv_t0']) / state['conv_max_time']))
			else:
				state['conv_pos'] = tracking['pos']; state['conv_ang'] = tracking['angle']; state['conv_value'] = 0.0; state['conv_t0'] = time.time();
		tracking = gen_tracking()
		if tracking is None:
			return
		scene['tracking'] = tracking
		handle_tracking_converge(tracking)
		tracking['resolved'] = resolve_tracking(tracking, scene['tracking_converge']['conv_value'])
		draw_tracking(tracking)
		draw_object_tracking(tracking, scene['objects'])
	def handle_rig_sensor():
		def take_rig_sensor_shot():
			ray_fov = scene['settings']['sensor_fov']; n_rays = scene['settings']['sensor_rays']; ray_len = scene['settings']['sensor_len'];
			rig_xfm = m2_rigid(scene['rig']['pos'], scene['rig']['angle'])
			ray_src = m2_get_trans(rig_xfm)
			if scene['show']['rig_sensor']:
				extreme_pts = [ v2_add(ray_src,  v2_muls(m2_get_dir1( m2_mul(m2_rigid(v2_z(), (x*ray_fov)-(0.5*ray_fov) ) ,rig_xfm)), ray_len) ) for x in [0.0, 1.0] ]
				trace_poly( [ray_src, extreme_pts[0], extreme_pts[1], ray_src] )
			ray_dirs = []
			for i in range(n_rays):
				ray_dirs.append( m2_get_dir1( m2_mul(m2_rigid(v2_z(), (random.random()*ray_fov)-(0.5*ray_fov) ) ,rig_xfm)) )
			hits = [ b2_raycast_closest( scene['physw'], [ray_src, v2_add(ray_src, v2_muls(x, ray_len))] ) for x in ray_dirs ]
			hit_pts = [x[0] for x in hits if x is not None]
			sparse_hit_pts = []
			for hi in range(len(hit_pts)):
				has_nearby = False
				for hj in range(hi+1, len(hit_pts)):
					if has_nearby or v2_dist(hit_pts[hi], hit_pts[hj]) < 2.0*k_cm:
						has_nearby = True
				if has_nearby == False:
					sparse_hit_pts.append(hit_pts[hi])
			return sparse_hit_pts
		if len(scene['rig']['path']) <= 1 or len(scene['features']) == 0:
			return
		hit_pts = take_rig_sensor_shot()
		if len(hit_pts):
			take_object = False
			shot_vol = aabb_inflate(points_to_aabb(hit_pts), k_cm*1.0)
			#print len(hit_pts), shot_vol
			tree = scene['sensor_state']['shot_tree']
			inter_leaves = btree_intersecting_leaves(tree, shot_vol)
			#print inter_leaves
			if len(inter_leaves) == 0:
				btree_insert(tree, shot_vol)
				scene['stats']['sensor_tree_size'] = btree_size(tree)
				#print 'sensor tree size:', btree_size(tree)
				take_object = True
			if take_object:
				first_hit_pt = hit_pts[0]
				rel_hit_pts = [ v2_sub(x, first_hit_pt) for x in hit_pts if x is not None]
				if True:
					obj = make_body( rel_hit_pts, 'points', m2_rigid(first_hit_pt, 0.0), k_red )
					obj['fill'] = 0
					feat_i = find_close_feature( v2_add(m2_get_trans(obj['xfm']), [0.0, 0.0]), scene['features'], k_cm*10 )
					if feat_i >= 0:
						obj['feat_i'] = feat_i
						obj['obj_feat'] = m2_mul( m2_inv( scene['features'][feat_i]['xfm'] ), obj['xfm'] )
						#obj['path_col'] = [0.45 + random.random()*0.5, 0.25 + random.random()*0.5, 0.25 + random.random()*0.3]
						#obj['path_jitter'] = [ (-0.5+random.random()) *4.0*k_cm, (-0.5+random.random())*4.0*k_cm]
						scene['objects'].append(obj)
	def intersect_tracking_vis(tr1, tr2):
		return tr1['vis_set'].intersection(tr2['vis_set'])
	def map_path_to_feature_path(tracking, feat_i, map_path, calc_xfm):
		trk_path = [tracking] + [scene['map']['trackings'][x] for x in map_path]
		# feat_pt = m2_get_trans( scene['features'][feat_i]['xfm'] )
		feat_path = [ next(iter(intersect_tracking_vis(trk_path[x], trk_path[x+1]))) for x in range(len(trk_path)-1) ]
		feat_path.append(feat_i)
		#
		walk_feat_rig_xfm = None
		if calc_xfm:
			for walk_i in range(len(feat_path)):
				walk_feat_i = feat_path[walk_i]; walk_trk = trk_path[walk_i]; walk_trk_res = walk_trk['resolved'];
				feat_vis_i = walk_trk['vis'].index(walk_feat_i);
				feat_loc_xfm = walk_trk_res['feat_local_xfms'][ feat_vis_i ]
				if walk_i == 0:
					walk_feat_rig_xfm = walk_trk_res['feat_rig_xfms'][ feat_vis_i ]
				else:
					prev_feat_vis_i = walk_trk['vis'].index(feat_path[walk_i-1])
					prev_feat_loc_ixfm = m2_inv( walk_trk_res['feat_local_xfms'][ prev_feat_vis_i ] )
					feat_feat_xfm = m2_mul(prev_feat_loc_ixfm, feat_loc_xfm)
					walk_feat_rig_xfm = m2_mul(walk_feat_rig_xfm, feat_feat_xfm)
		return (feat_path, walk_feat_rig_xfm)
	def find_map_path_to_feature(tracking, feat_i):
		map_trackings = scene['map']['trackings']
		source_cands = set([xi for xi in range(len(map_trackings)) if (len(intersect_tracking_vis(tracking, map_trackings[xi]))>0) ])
		tgt_cands = set([xi for xi in range(len(map_trackings)) if feat_i in map_trackings[xi]['vis_set'] ])
		inter_cands = source_cands.intersection(tgt_cands)
		if len(inter_cands) > 0:
			return [next(iter(inter_cands))]
		min_path = None;
		for scand in source_cands:
			for tcand in tgt_cands:
				path = find_map_path(scand, tcand)
				if path is not None and (min_path is None or len(path) < len(min_path)):
					min_path = path
		return min_path
	def find_map_path(src_i, dest_i):
		def walk_node(args, node_i, visited):
			# args is trackings,edges,dest_i
			if node_i == args[2]:
				return [node_i]
			nvisi = copy.copy(visited); nvisi.add(node_i);
			for target_i in [x for x in args[1][node_i] if x not in nvisi]:
				ret = walk_node(args, target_i, nvisi)
				if ret is not None:
					return [node_i] + ret
			return None
		return walk_node((scene['map']['trackings'], scene['map']['track_graph'], dest_i), src_i, set())
	def walk_map(node_func, edge_func):
		def dummy_node_func(trackings, node_i):
			return
		def dummy_edge_func(trackings, src_i, tgt_i):
			return
		def walk_node(args, node_i, visited):
			# args is trackings,edges,node_func,edge_func
			args[2](args[0], node_i)
			nvisi = copy.copy(visited); nvisi.add(node_i);
			for target_i in [x for x in args[1][node_i] if x not in nvisi]:
				args[3](args[0], node_i, target_i)
				walk_node(args, target_i, nvisi)
		if len(scene['map']['trackings']):
			for root in scene['map']['roots']:
				walk_node((scene['map']['trackings'], scene['map']['track_graph'], node_func if node_func else dummy_node_func, edge_func if edge_func else dummy_edge_func), root, set())
	def show_mapping():
		if scene['show']['map']:
			def show_node_func(trackings, node_i):
				center = trackings[node_i]['vis_pt_avg']
				draw_lines( sum([[center,x] for x in trackings[node_i]['vis_pts'] ], []), k_dgray )
				return
			def show_edge_func(trackings, src_i, tgt_i):
				#print '{} -> {}'.format(src_i, tgt_i)
				trace_poly([ trackings[src_i]['vis_pt_avg'], trackings[tgt_i]['vis_pt_avg'] ], k_red )
				return
			walk_map(show_node_func, show_edge_func)
	def handle_mapping():
		def find_inter_tracking(tracking, exclude_subsets = True):
			max_inter = 0; max_inter_i = -1;
			for i, map_tr in enumerate(scene['map']['trackings']):
				inter = intersect_tracking_vis(tracking, map_tr)
				if exclude_subsets and (len(inter) == len(tracking['vis_set']) or len(inter) == len(map_tr['vis_set'])):
					return None
				if len(inter) > max_inter:
					max_inter = len(inter); max_inter_i = i;
			return (max_inter_i, max_inter)
		def prepare_map_tracking(tracking):
			return
		def add_tracking(tracking):
			new_i = len(scene['map']['trackings'])
			prepare_map_tracking(tracking)
			scene['map']['trackings'].append(tracking)
			scene['map']['track_graph'].append(set([]))
			if max_inter_i >= 0:
				scene['map']['track_graph'][max_inter_i].add(new_i)
				scene['map']['track_graph'][new_i].add(max_inter_i)
			else:
				scene['map']['roots'].append(new_i)
			#print max_inter_i, max_inter
			scene['stats']['map_size'] = len(scene['map']['trackings'])
			#print 'map size:', len(scene['map']['trackings'])
		save_useful_tracking = None
		if scene['tracking'] is not None and len(scene['tracking']['vis']) > 0:
			if len(scene['tracking']['vis']) > scene['settings']['map_set_sz']:
				out = find_inter_tracking(scene['tracking'])
				if out is not None:
					max_inter_i, max_inter = out
					if max_inter_i < 0 or max_inter < (len(scene['map']['trackings'][max_inter_i]['vis']) / 2):
						add_tracking(scene['tracking'])
					elif max_inter > 0:
						# We did not add this tracking, but keeping as a last-resource candidate in case the next tracking is disconnected
						save_useful_tracking = scene['tracking']
					elif max_inter == 0:
						if scene['map'].get('save_useful_tracking', None) is not None:
							add_tracking( scene['map']['save_useful_tracking'] )
							save_useful_tracking = None
		scene['map']['save_useful_tracking'] = save_useful_tracking
	#
	if g_app_mode == 'design':
		def draw_design_grid():
			draw_lines([v2_z(), v2_muls(k_e_1, k_meter), v2_z(), v2_muls(k_e_2, k_meter)], k_lgray)
		def handle_design_input_static_body():
			drag = g_drag.get(0, None)
			if drag is not None and drag['active']:
				scene['design']['active_drag'] = True
				#disc_wpts = [[round(x/8.0)*8.0 for x in pt] for pt in drag['wpts']]
				pts = [screen_to_draw(x) for x in drag['wpts']]
				pts = [[round(x*500.0/8.0)*8.0/500.0 for x in pt] for pt in pts]
				wh = v2_muls([ m_abs(pts[1][0]-pts[0][0]), m_abs(pts[1][1]-pts[0][1]) ], 0.5)
				poly = None; poly_type = None;
				if wh[0] == 0:
					poly = make_h_poly(wh[1]); poly_type = 'line';
				elif wh[1] == 0:
					poly = make_w_poly(wh[0]); poly_type = 'line';
				else:
					poly = make_wh_poly(wh); poly_type = 'convex';
				if poly_type == 'convex' or g_design_allow_lines:
					frame = m2_rigid(v2_muls(v2_add(pts[0], pts[1]), 0.5), 0.0)
					fill_poly(m2_mulp_a(frame, poly), scene['design']['active_drag_body_col'])
					scene['design']['active_drag_body'] = make_body( poly, 'convex', frame, scene['design']['static_col'] )
				else:
					scene['design']['active_drag_body'] = None
			else:
				if scene['design']['active_drag']:
					scene['design']['active_drag'] = False
					new_body = scene['design']['active_drag_body']; scene['design']['active_drag_body'] = None;
					if new_body is not None:
						new_body['phys'] = make_body_phys(scene['physw'], new_body)
						scene['static_bodies'].append(new_body)
		def gen_features():
			scene_aabb = reduce(lambda x, y: aabb_union(x,y), [ points_to_aabb( m2_mulp_a(x['xfm'], x['poly']) ) for x in scene['static_bodies'] ])
			scene_mM = aabb_mM(scene_aabb)
			scene_r = aabb_radius(scene_aabb)
			features = []
			feature_r = scene['settings']['feature_r']
			feat_col = k_dgray
			feature_count = m_max(10, int(0.25*scene['settings']['feature_count'] * aabb_size(scene_aabb)/4.0))
			for i in range(feature_count):
				rpt = v2_interp(scene_mM[0], scene_mM[1], [random.random(), random.random()])
				hits_e2 = [[b2_raycast_closest(scene['physw'], [rpt, v2_add(rpt, v2_muls(x, scene_r))]) for x in [dir, v2_neg(dir)]] for dir in k_e2]
				has_good_dir = any([all([hit is not None for hit in hits_e2[x]]) for x in range(2)])
				if has_good_dir:
					features.append( make_body( make_wh_poly([feature_r, feature_r]), 'convex', m2_rigid(rpt, 0), feat_col ) )
					features[-1]['xfm'] = m2_rigid(rpt, random.random() * math.pi)
			return features
		def handle_design_input():
			if scene['once']['design_save'] or ('q' in g_keys):
				save_scene(g_scene, g_app_scene)
			if scene['once']['design_gen_features']:
				features = gen_features()
				scene['features'] = features
			if 'q' in g_keys:
				glutLeaveMainLoop()
				sys.exit(0)
			handle_design_input_static_body()
		if g_raycast_test:
			dbg_raycast()
		handle_design_input()
		draw_design_grid()
		for coll in [scene['static_bodies'] if scene['show']['static'] else [], scene['features'] if scene['show']['features'] else [], scene['objects']]:
			draw_bodies(coll)
	else:
		if scene['once']['design_save'] and len(g_app_scene):
			save_scene(g_scene, g_app_scene)
		for coll in [scene['static_bodies'] if scene['show']['static'] else [], scene['features'] if scene['show']['features'] else [], scene['objects']]:
			draw_bodies(coll)
		#scene['physw'].Step(1.0/60.0, 1, 1)
		if g_raycast_test:
			dbg_raycast()
		#track_mouse()
		show_mapping()
		handle_rig()
		if scene['on']['sensor_shot'] or scene['once']['sensor_shot']:
			handle_rig_sensor()
		#
		handle_tracking()
		handle_mapping()
		if g_dbg:
			dbg_mouse()
		handle_draw_strings()
		#
	for once_k in scene['once'].keys():
		scene['once'][once_k] = False
	#
	handle_input_scroll()
	if not g_raycast_test:
		handle_scene_offset()
	g_keys.clear(); g_special_keys.clear(); g_buttons.clear();
def main():
	global g_dbg, g_app_mode, g_app_scene, g_design_allow_lines, g_raycast_test
	#if sys_argv_has(['-go']) == False:
	#	return
	g_dbg = sys_argv_has(['-dbg'])
	g_app_mode = 'design' if sys_argv_has(['-design']) else ''
	g_app_scene = sys_argv_get(['-file'], '')
	g_design_allow_lines = sys_argv_has(['-allow_lines'])
	g_raycast_test = sys_argv_has(['-raycast_test'])
	main_realtime()

main()

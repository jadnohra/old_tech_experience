from ctypes import *
import math
import time
import copy
import random
# conda install pyopengl
# conda install -c conda-forge freeglut
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
# conda install -c kne pybox2d
from Box2D import *

g_dbg = False

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
def rgb_to_f(rgb):
	return [x/255.0 for x in rgb]
k_white = [1.0, 1.0, 1.0]; k_green = [0.0, 1.0, 0.0]; k_blue = [0.0, 0.0, 1.0];
k_red = [1.0, 0.0, 0.0]; k_lgray = [0.7, 0.7, 0.7]; k_dgray = [0.3, 0.3, 0.3];
k_pink = rgb_to_f([245, 183, 177]); k_bluish1 = rgb_to_f([30, 136, 229]);
k_organe = rgb_to_f([251, 140, 0]);
k_e_1 = [1.0, 0.0]; k_e_2 = [0.0, 1.0]; k_e2 = [k_e_1, k_e_2];

def style0_color3f(r,g,b):
	return (r, g, b)
def style1_color3f(r,g,b):
	return (1.0-r, 1.0-g, 1.0-b)
style_color3f = style0_color3f
def style_glColor3f(r,g,b):
	glColor3f(*style_color3f(r,g,b))
def screen_to_draw(pt, wh = None):
	x,y,z = gluUnProject(pt[0], (wh if wh else g_wh[1]) - pt[1], 0);
	return [x,y];
def size_to_draw(sz, wh = None):
	p0 = screen_to_draw(v2_z(), wh); p = screen_to_draw(sz, wh); return v2_sub(p, p0);

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

def make_wh_poly(rwh):
	rw,rh = rwh[0], rwh[1]
	return [ v2_p(-rw, -rh), v2_p(-rw, rh), v2_p(rw, rh), v2_p(rw, -rh), v2_p(-rw, -rh) ]
def make_w_poly(rw):
		return [ v2_p(-rw, 0.0), v2_p(rw, 0.0) ]
def make_h_poly(rh):
		return [ v2_p(0.0, -rh), v2_p(0.0, rh) ]
def make_tri_poly(wh):
	return [v2_p(0,0), v2_p(wh[0], wh[1]), v2_p(wh[0], -wh[1]), v2_p(0,0)]
def make_body(poly, xfm, col = k_white):
	return { 'poly':poly, 'xfm':xfm, 'col':col, 'fill':2, 'phys':None }
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
		g_drag[button] = g_buttons[button]; g_drag[button]['wpts'] = [g_buttons[button]['wpt']]*2; g_drag[button]['active'] = True;
	elif mode == 1:
		g_drag[button]['active'] = False
def handleMousePassiveMove(x, y):
	global g_mouse
	if (g_mouseFocus):
		g_mouse = [x,y]
	for d in [xx for xx in g_drag.values() if xx['active']]:
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
	aspect = float(w)/float(h)
	glViewport(0, 0, w, h)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glOrtho(-1*aspect, 1*aspect, -1, 1, -1, 1)
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
def gen_scene_1(settings):
	k_unit = 2.0 / g_wh[1]
	static_bodies = []
	static_col = k_green; feat_col = k_dgray; rig_col = k_blue; obj_col = k_blue;
	#
	static_bodies.append( make_body( make_w_poly(0.99+0.01), m2_rigid([0,-0.9], 0), static_col ) )
	static_bodies.append( make_body( make_h_poly(0.9+0.01), m2_rigid([-0.99, 0], 0), static_col ) )
	static_bodies.append( make_body( make_w_poly(0.99+0.01), m2_rigid([0,0.9], 0), static_col ) )
	static_bodies.append( make_body( make_h_poly(0.9+0.01), m2_rigid([0.99, 0], 0.0), static_col ) )
	#
	static_bodies.append( make_body( make_w_poly(0.46), m2_rigid([-0.2,-0.45], 0), static_col ) )
	static_bodies.append( make_body( make_w_poly(0.46), m2_rigid([-0.2, 0.25], 0), static_col ) )
	static_bodies.append( make_body( make_h_poly(0.45/2), m2_rigid([0.46-0.2-0.01,-0.25], 0), static_col ) )
	static_bodies.append( make_body( make_w_poly(0.46), m2_rigid([-1.0+0.46,-0.1], 0), static_col ) )
	#
	features = []
	feature_r = settings['feature_r']
	for i in range(settings['feature_count']):
		rpt = v2_p( 0.9 * (random.random()*2.0-1.0), 0.9 * (random.random()*2.0-1.0) )
		features.append( make_body( make_wh_poly([feature_r, feature_r]), m2_rigid(rpt, 0), feat_col ) )
		features[-1]['xfm'] = m2_rigid(rpt, random.random() * math.pi)
	#
	objects = []
	objects.append( make_body( make_wh_poly([k_unit*80, k_unit*8]), m2_rigid(v2_p(0.3, -0.8), 0), obj_col ) )
	if len(objects):
		obj = objects[-1]
		obj['fill'] = 1
		feat_i = find_close_feature( v2_add(m2_get_trans(objects[-1]['xfm']), [-0.3, 0.0]), features, k_unit*10 )
		obj['feat_i'] = feat_i
		obj['obj_feat'] = m2_mul( m2_inv( features[feat_i]['xfm'] ), obj['xfm'] )
	#
	physw = b2World()
	#print dir(Box2D)
	#print dir(physw)
	for coll in [static_bodies]:
		for b in coll:
			bd = physw.CreateStaticBody(position=m2_get_trans(b['xfm']), angle=0)
			bd.CreateEdgeFixture(vertices=b['poly'])
			b['phys'] = bd
	#
	scene = {'static_bodies':static_bodies, 'features':features, 'objects':objects, 'physw':physw, 'settings':settings}
	return scene
g_scene = None
def do_display():
	global g_scene
	k_unit = 2.0 / g_wh[1]; k_meter = 100*k_unit;
	if g_scene is None:
		settings = { 'rand_pos_scl':(k_unit*3.0)*1.0, 'rand_ang_scl': ((0.5*math.pi)/40.0) * 1.0, 'rig_wh':v2_muls([300, 100], k_unit* (g_wh[1]/800.0) ), 'feature_r':k_unit*2.0, 'feature_count':600, 'map_set_sz':4,
					'sensor_fov':(90.0 / 180.0)*math.pi, 'sensor_rays':50, 'sensor_len':k_meter*3.0 }
		g_scene = gen_scene_1(settings)
		g_scene['rig'] = {'path':[], 'pos': v2_z(), 'angle':0, 'poly':[]}
		g_scene['tracking'] = None
		g_scene['map'] = {'trackings':[], 'track_graph':[], 'roots':[]}
		g_scene['show'] = { 'features':True, 'map':True, 'track_feat_path':True, 'track_map_path':False }
		g_scene['show_keys'] = {'1':'features', '2':'map', '3':'track_feat_path' }
	scene = g_scene
	#
	def dbg_raycast():
		for d in [xx[1] for xx in g_drag.items() if xx[0] == 1 and xx[1]['active'] ]:
	 		pts = [screen_to_draw(x) for x in d['wpts']]
			trace_poly(pts, k_white)
			if True:
				hits = b2_raycast_all(scene['physw'], pts)
				if len(hits):
				#	print hits
					star = make_star(10*k_unit, 5*k_unit); hstars = [];
					for hit in hits:
						hstars.append(m2_mulp_a(m2_rigid(hit[0], v2_v_angle(hit[1]) + math.pi / 4.0), star))
					draw_stars(hstars, k_red)
	def track_mouse():
		if 'mouse_track' not in scene:
			scene['mouse_track'] = []
			scene['mouse_tracking'] = False
		if 't' in g_keys:
			scene['mouse_tracking'] = not scene['mouse_tracking']
		track =	scene['mouse_track']
		if scene['mouse_tracking']:
			if g_mouseFocus and g_mouse[0] is not None:
				if v2_dist(scene.get('mouse_last', g_mouse), g_mouse) > 3.0 * k_unit:
					track.append(screen_to_draw(g_mouse))
				scene['mouse_last'] = g_mouse
				trace_poly( m2_mulp_a(m2_rigid(screen_to_draw(g_mouse), 0), make_wh_poly([k_unit*5, k_unit*5])) )
		else:
			if len(track) >= 2:
				scene['rig']['path'] = copy.copy(track)
				del track[:]
		if len(track) >= 2:
			trace_poly(track, [1.0, 1.0, 0.0])
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
					if (rig_pt is None) or (v2_dist(rig_pt, mpt) > 3.0 * k_unit):
						rig['path'].append(mpt)
		def handle_rig_xfm(rig_pt):
			changed = False
			if 2 in g_drag and g_drag[2]['active']:
				drag = g_drag[2]
				pts = [screen_to_draw(x) for x in drag['wpts']]
				if v2_dist(rig_pt, pts[1]) > 10 * k_unit:
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
			trace_poly(rig['path'], [1.0, 1.0, 1.0])
			xfm_changed = handle_rig_xfm(rig['path'][-1])
			if xfm_changed or len(rig['poly']) == 0:
				rig_verts = make_rig_poly_pa(rig['pos'], rig['angle'])
				rig['poly'] = rig_verts
				if True:
					pshape = b2PolygonShape(vertices = rig_verts)
					pxfm = b2Transform(); pxfm.SetIdentity();
					vis = []; vis_pts = [];
					for i, feat in enumerate(scene['features']):
						vis_pt = m2_get_trans(feat['xfm'])
						if pshape.TestPoint( pxfm, vis_pt ):
							vis_pt2 = v2_add(rig['pos'], v2_muls( v2_sub(vis_pt, rig['pos']), 0.95 ))
							obstacles = b2_raycast_all(scene['physw'], [rig['pos'], vis_pt2])
							if len(obstacles) == 0:
								vis.append(i); vis_pts.append(vis_pt)
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
		return m2_rigid(vec_randomize(pa[0], rand_settings['rand_pos_scl']), vec_randomize([pa[1]], rand_settings['rand_ang_scl'])[0])
	def resolve_tracking(tracking):
		if len(tracking['vis']) == 0:
			return None
		rand_settings =  g_scene['settings']
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
						map_path = find_map_path_to_feature(tracking, obj['feat_i'])
						if map_path is not None:
							#print map_path
							if scene['show']['track_map_path']:
								trace_poly( [ scene['map']['trackings'][x]['vis_pt_avg'] for x in map_path ],  k_organe)
							feat_path, path_feat_rig_xfm = map_path_to_feature_path(tracking, obj['feat_i'], map_path, True)
							if scene['show']['track_feat_path']:
								trace_poly( [ m2_get_trans(scene['features'][x]['xfm']) for x in feat_path ],  k_organe)
							track_xfm = m2_mul( resolved['rig_frame'],  m2_mul(path_feat_rig_xfm, obj['obj_feat']) )
							draw_poly_with_mode(obj['fill'], m2_mulp_a(track_xfm, obj['poly']), k_pink)
	def handle_tracking():
		tracking = gen_tracking()
		if tracking is None:
			return
		scene['tracking'] = tracking
		tracking['resolved'] = resolve_tracking(tracking)
		draw_tracking(tracking)
		draw_object_tracking(tracking, scene['objects'])
	def gen_rig_sensor_object():
		ray_fov = scene['settings']['sensor_fov']; n_rays = scene['settings']['sensor_rays']; ray_len = scene['settings']['sensor_len'];
		rig_xfm = m2_rigid(scene['rig']['pos'], scene['rig']['angle'])
		ray_dirs = []
		for i in range(n_rays):
			ray_dirs.append( m2_get_dir1( m2_mul(m2_rigid(v2_z(), (random.random()*ray_fov)-(0.5*ray_fov) ) ,rig_xfm)) )
		ray_src = m2_get_trans(rig_xfm)
		hits = [ b2_raycast_closest( scene['physw'], [ray_src, v2_add(ray_src, v2_muls(x, ray_len))] ) for x in ray_dirs ]
		hit_pts = [x[0] for x in hits if x is not None]
		if len(hit_pts):
			first_hit_pt = hit_pts[0]
			rel_hit_pts = [ v2_sub(x, first_hit_pt) for x in hit_pts if x is not None]
			if True:
				obj = make_body( rel_hit_pts, m2_rigid(first_hit_pt, 0.0), k_red )
				obj['fill'] = 0
				feat_i = find_close_feature( v2_add(m2_get_trans(obj['xfm']), [0.0, 0.0]), scene['features'], k_unit*10 )
				obj['feat_i'] = feat_i
				obj['obj_feat'] = m2_mul( m2_inv( scene['features'][feat_i]['xfm'] ), obj['xfm'] )
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
		if scene['tracking'] is not None and len(scene['tracking']['vis']) > scene['settings']['map_set_sz']:
			out = find_inter_tracking(scene['tracking'])
			if out is not None:
				max_inter_i, max_inter = out
				if max_inter_i < 0 or max_inter < (len(scene['map']['trackings'][max_inter_i]['vis']) / 2):
					new_i = len(scene['map']['trackings'])
					prepare_map_tracking(scene['tracking'])
					scene['map']['trackings'].append(scene['tracking'])
					scene['map']['track_graph'].append(set([]))
					if max_inter_i >= 0:
						scene['map']['track_graph'][max_inter_i].add(new_i)
						scene['map']['track_graph'][new_i].add(max_inter_i)
					else:
						scene['map']['roots'].append(new_i)
					#print max_inter_i, max_inter
					print 'map size:', len(scene['map']['trackings'])
	#
	for coll in [scene['static_bodies'], scene['features'] if scene['show']['features'] else [], scene['objects']]:
		draw_bodies(coll)
	#scene['physw'].Step(1.0/60.0, 1, 1)
	dbg_raycast()
	#track_mouse()
	show_mapping()
	handle_rig()
	if '5' in g_special_keys:
		gen_rig_sensor_object()
	#
	handle_tracking()
	handle_mapping()
	if g_dbg:
		dbg_mouse()
	#
	if ('\x1b' in g_keys.keys()):
		glutLeaveMainLoop()
		sys.exit(0)
	for sk in g_special_keys.keys():
		show_key = g_scene['show_keys'].get(sk, '')
		if show_key != '':
			scene['show'][show_key] = not scene['show'][show_key]
	g_keys.clear(); g_special_keys.clear(); g_buttons.clear();
def main():
	global g_dbg
	g_dbg = sys_argv_has(['-dbg'])
	main_realtime()

main()

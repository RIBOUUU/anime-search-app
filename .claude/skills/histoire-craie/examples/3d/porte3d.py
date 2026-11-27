# Blender 4.0 — « LA PORTE » en 3D (même découpage que la version craie, 18,2 s)
# blender -b -P porte3d.py -- OUTDIR [frame_start frame_end] [--test]
import bpy, math, random, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if argv else "/tmp/porte3d"
FPS, DUR = 30, 18.2
N = int(DUR * FPS)
random.seed(4)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS
sc.frame_start, sc.frame_end = 1, N
col = sc.collection


def F(t):
    return int(round(t * FPS)) + 1


# ------------------------------------------------------------------ matériaux
def mat(name, color, rough=0.55, emit=0.0, ecolor=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*(ecolor or color), 1)
        b.inputs["Emission Strength"].default_value = emit
    return m


def setmat(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True


def empty(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    col.objects.link(e)
    e.parent = parent
    e.location = loc
    e.rotation_mode = "XYZ"
    return e


def sphere(r, loc, m, parent=None, scale=(1, 1, 1), seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.active_object
    o.scale = scale
    setmat(o, m)
    smooth(o)
    if parent:
        o.parent = parent
        o.location = loc
    return o


def cyl(r, depth, loc, m, parent=None, rot=(0, 0, 0), r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=24)
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=depth, location=loc, rotation=rot, vertices=32)
    o = bpy.context.active_object
    setmat(o, m)
    smooth(o)
    if parent:
        o.parent = parent
        o.location = loc
        o.rotation_euler = rot
    return o


def cube(size, loc, m, parent=None, scale=(1, 1, 1), rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=size, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = scale
    setmat(o, m)
    if parent:
        o.parent = parent
        o.location = loc
        o.rotation_euler = rot
    bev = o.modifiers.new("bev", "BEVEL")
    bev.width, bev.segments = 0.02, 3
    return o


# ------------------------------------------------------------------ monde
w = bpy.data.worlds.new("nuit")
sc.world = w
w.use_nodes = True
nt = w.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputWorld")
bg = nt.nodes.new("ShaderNodeBackground")
tc = nt.nodes.new("ShaderNodeTexCoord")
vor = nt.nodes.new("ShaderNodeTexVoronoi")
vor.inputs["Scale"].default_value = 260
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (1, 1, 1, 1)
ramp.color_ramp.elements[1].position = 0.035
ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
grad = nt.nodes.new("ShaderNodeSeparateXYZ")
mix = nt.nodes.new("ShaderNodeMix")
mix.data_type = "RGBA"
mix.blend_type = "ADD"
mix.inputs["Factor"].default_value = 1.0
mix.inputs[6].default_value = (0.006, 0.01, 0.03, 1)  # A : bleu nuit
nt.links.new(tc.outputs["Generated"], vor.inputs["Vector"])
nt.links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
mul = nt.nodes.new("ShaderNodeMix")
mul.data_type = "RGBA"
mul.blend_type = "MULTIPLY"
mul.inputs["Factor"].default_value = 1.0
mul.inputs[7].default_value = (0.9, 0.9, 1.0, 1)
nt.links.new(ramp.outputs["Color"], mul.inputs[6])
nt.links.new(mul.outputs[2], mix.inputs[7])
nt.links.new(mix.outputs[2], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.0
nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

# sol : grande plaine douce
M_ground = mat("sol", (0.05, 0.09, 0.07), 0.9)
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
ground = bpy.context.active_object
setmat(ground, M_ground)
# petites touffes d'herbe autour
M_grass = mat("herbe", (0.1, 0.25, 0.12), 0.8)
for i in range(140):
    a = random.uniform(0, 6.28)
    r = random.uniform(1.2, 14)
    x, y = math.cos(a) * r, math.sin(a) * r
    for k in range(3):
        cyl(0.012, 0.18, (x + k * 0.03, y, 0.08), M_grass, rot=(random.uniform(-.4, .4), random.uniform(-.4, .4), 0), r2=0.0)

# lune
M_moon = mat("lune", (1, 0.95, 0.8), 0.5, emit=6.0)
sphere(1.6, (-25, 60, 22), M_moon)

# ------------------------------------------------------------------ porte (objet qui s'envolera)
M_wood = mat("bois", (0.42, 0.24, 0.12), 0.6)
M_wood2 = mat("bois2", (0.3, 0.16, 0.08), 0.6)
M_gold = mat("laiton", (0.9, 0.7, 0.3), 0.25)
door = empty("porte", loc=(0, 0, 0))
cube(1, (0, 0, 1.1), M_wood, door, scale=(1.0, 0.09, 2.15))
for i, z in enumerate((0.55, 1.65)):
    cube(1, (0, 0, z), M_wood2, door, scale=(0.75, 0.11, 0.8))
for x in (-0.55, 0.55):
    cube(1, (x, 0, 1.15), M_wood2, door, scale=(0.1, 0.16, 2.3))
cube(1, (0, 0, 2.3), M_wood2, door, scale=(1.2, 0.16, 0.1))
for sy in (-1, 1):
    sphere(0.045, (0.38, sy * 0.08, 1.05), M_gold, door)

# ------------------------------------------------------------------ personnages
M_skin = mat("peau", (0.95, 0.72, 0.55), 0.5)
M_white = mat("blanc", (1, 1, 1), 0.3)
M_black = mat("noir", (0.02, 0.02, 0.02), 0.3)


def character(name, body_rgb, hair_rgb, skirt=False, cap=False):
    root = empty(name)
    M_body = mat(name + "_corps", body_rgb, 0.6)
    M_hair = mat(name + "_cheveux", hair_rgb, 0.7)
    torso = empty(name + "_torse", root, (0, 0, 0.62))
    if skirt:
        cyl(0.3, 0.62, (0, 0, 0.18), M_body, torso, r2=0.15)
        sphere(0.17, (0, 0, 0.5), M_body, torso, scale=(1, 0.85, 0.9))
    else:
        sphere(0.2, (0, 0, 0.3), M_body, torso, scale=(1, 0.8, 1.75))
    neck = empty(name + "_cou", torso, (0, 0, 0.64))
    head = sphere(0.23, (0, 0, 0.2), M_skin, neck)
    face = {}
    for s in (-1, 1):
        sphere(0.06, (s * 0.085, 0.18, 0.25), M_white, neck)
        face["p%d" % s] = sphere(0.033, (s * 0.085, 0.233, 0.25), M_black, neck)
        face["b%d" % s] = cube(1, (s * 0.085, 0.2, 0.36), M_hair, neck, scale=(0.09, 0.02, 0.02))
    face["mouth"] = sphere(0.04, (0, 0.215, 0.12), M_black, neck, scale=(1.2, 0.5, 0.35))
    if cap:
        sphere(0.24, (0, 0, 0.26), M_hair, neck, scale=(1, 1, 0.6))
        cube(1, (0, 0.2, 0.3), M_hair, neck, scale=(0.32, 0.22, 0.03))
    else:
        sphere(0.245, (0, -0.02, 0.26), M_hair, neck, scale=(1, 1, 0.75))
        sphere(0.1, (0, -0.25, 0.22), M_hair, neck)
        cyl(0.06, 0.32, (0, -0.3, 0.02), M_hair, neck, rot=(0.3, 0, 0))
    sh = {}
    for s, side in ((-1, "L"), (1, "R")):
        e = empty(name + "_epaule" + side, torso, (s * 0.25, 0, 0.55))
        cyl(0.055, 0.46, (0, 0, -0.23), M_body, e)
        sphere(0.07, (0, 0, -0.49), M_skin, e)
        sh[side] = e
    hp = {}
    for s, side in ((-1, "L"), (1, "R")):
        e = empty(name + "_hanche" + side, root, (s * 0.1, 0, 0.62))
        cyl(0.07, 0.56, (0, 0, -0.28), mat(name + "_jambe", (0.12, 0.12, 0.16), 0.7), e)
        sphere(0.085, (0, 0.06, -0.6), M_black, e, scale=(1, 1.6, 0.6))
        hp[side] = e
    return dict(root=root, torso=torso, neck=neck, sh=sh, hp=hp, face=face)


lui = character("lui", (0.18, 0.4, 0.85), (0.15, 0.1, 0.08), cap=True)
elle = character("elle", (0.95, 0.45, 0.3), (0.35, 0.18, 0.08), skirt=True)

R = math.radians
POSES = {
    "stand": dict(lean=0, tilt=0, L=6, Rr=6, hL=0, hR=0, z=0),
    "knock": dict(lean=0, tilt=5, L=6, Rr=95, hL=0, hR=0, z=0),
    "knock_sad": dict(lean=-8, tilt=-18, L=4, Rr=80, hL=0, hR=0, z=0),
    "sad": dict(lean=-8, tilt=-22, L=4, Rr=4, hL=0, hR=0, z=0),
    "crouch": dict(lean=-40, tilt=-15, L=20, Rr=75, hL=55, hR=35, z=-0.22),
    "hug": dict(lean=-18, tilt=-24, L=75, Rr=75, hL=88, hR=88, z=-0.6),
    "look_up": dict(lean=4, tilt=22, L=20, Rr=20, hL=88, hR=88, z=-0.6),
    "cheer": dict(lean=4, tilt=12, L=160, Rr=165, hL=0, hR=0, z=0),
}


def key_rot(o, axis, deg, t):
    o.rotation_euler[axis] = R(deg)
    o.keyframe_insert("rotation_euler", index=axis, frame=F(t))


def pose(c, name, t):
    p = POSES[name]
    key_rot(c["torso"], 0, p["lean"], t)
    key_rot(c["neck"], 0, -p["tilt"], t)
    key_rot(c["sh"]["L"], 0, p["L"], t)
    key_rot(c["sh"]["R"], 0, p["Rr"], t)
    key_rot(c["hp"]["L"], 0, p["hL"], t)
    key_rot(c["hp"]["R"], 0, p["hR"], t)
    c["root"].location.z = p["z"]
    c["root"].keyframe_insert("location", index=2, frame=F(t))


def place(c, t, x=None, y=None, face=None):
    r = c["root"]
    if x is not None:
        r.location.x = x
        r.keyframe_insert("location", index=0, frame=F(t))
    if y is not None:
        r.location.y = y
        r.keyframe_insert("location", index=1, frame=F(t))
    if face is not None:
        r.rotation_euler[2] = face
        r.keyframe_insert("rotation_euler", index=2, frame=F(t))


def expr(c, kind, t):
    f = c["face"]
    m = f["mouth"]
    m.scale = {"smile": (1.4, 0.5, 0.3), "sad": (0.9, 0.5, 0.22), "laugh": (1.5, 0.6, 0.9),
               "surprised": (0.8, 0.6, 0.9), "neutral": (1.0, 0.5, 0.2)}[kind]
    m.keyframe_insert("scale", frame=F(t))
    for s in (-1, 1):
        b = f["b%d" % s]
        b.rotation_euler[1] = {"sad": -0.45 * s, "surprised": 0, "laugh": 0.15 * s}.get(kind, 0)
        b.location.z = 0.39 if kind == "surprised" else 0.36
        b.keyframe_insert("rotation_euler", index=1, frame=F(t))
        b.keyframe_insert("location", index=2, frame=F(t))


def walk(c, t0, t1, y0, y1, face=0.0):
    n = max(2, int((t1 - t0) / 0.12))
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        ph = math.sin(i * math.pi / 2)
        key_rot(c["hp"]["L"], 0, 28 * ph, t)
        key_rot(c["hp"]["R"], 0, -28 * ph, t)
        key_rot(c["sh"]["L"], 0, -24 * ph, t)
        key_rot(c["sh"]["R"], 0, 24 * ph, t)
    place(c, t0, y=y0, face=face)
    place(c, t1, y=y1)


def knock(c, t0, t1, amp=22):
    t = t0
    k = 0
    while t < t1:
        key_rot(c["sh"]["R"], 0, POSES["knock"]["Rr"] + (amp if k % 2 else -amp * 0.3), t)
        t += 0.1
        k += 1


def hold_cut(obj_list, t):
    """rend les clés juste avant t constantes (coupe franche)."""
    pass


# ---------------- timeline (identique à la version craie)
# lui
place(lui, 0, x=-0.05, y=-2.6, face=0)
pose(lui, "stand", 0)
expr(lui, "smile", 0)
walk(lui, 0.0, 0.8, -2.6, -0.85)
pose(lui, "stand", 0.85)
pose(lui, "knock", 0.95)
knock(lui, 1.0, 1.7)
pose(lui, "stand", 1.8)
pose(lui, "crouch", 2.15)
pose(lui, "stand", 2.55)
expr(lui, "neutral", 2.69)
pose(lui, "knock", 2.7)
knock(lui, 2.75, 3.55)
pose(lui, "stand", 3.65)
expr(lui, "sad", 4.49)
pose(lui, "knock_sad", 4.5)
knock(lui, 4.55, 5.35, amp=15)
pose(lui, "sad", 5.45)
pose(lui, "knock_sad", 6.3)
knock(lui, 6.35, 6.95, amp=10)
pose(lui, "sad", 7.05)
place(lui, 7.4, y=-0.85, face=0)
place(lui, 7.9, y=-0.42, face=math.pi)
pose(lui, "hug", 7.95)
pose(lui, "hug", 13.4)
expr(lui, "sad", 13.4)
pose(lui, "look_up", 13.7)
expr(lui, "surprised", 13.7)
pose(lui, "look_up", 14.1)
place(lui, 14.1, y=-0.42, face=math.pi)
pose(lui, "stand", 14.5)
place(lui, 14.5, y=-0.45, face=0.0)
expr(lui, "laugh", 14.9)
pose(lui, "cheer", 15.6)
pose(lui, "stand", 16.6)
expr(lui, "smile", 17.0)

# elle : de l'autre côté depuis le début
place(elle, 0, x=0.02, y=0.42, face=0)
pose(elle, "hug", 0)
expr(elle, "sad", 0)
pose(elle, "hug", 13.4)
pose(elle, "look_up", 13.7)
expr(elle, "surprised", 13.7)
pose(elle, "look_up", 14.1)
place(elle, 14.1, y=0.42, face=0)
pose(elle, "stand", 14.5)
place(elle, 14.5, y=0.45, face=math.pi)
expr(elle, "laugh", 15.0)
pose(elle, "cheer", 15.8)
pose(elle, "stand", 16.8)
expr(elle, "smile", 17.1)

# porte : reste, puis le vent l'emporte
door.location = (0, 0, 0)
door.keyframe_insert("location", frame=F(12.9))
door.rotation_euler = (0, 0, 0)
door.keyframe_insert("rotation_euler", frame=F(12.9))
door.location = (-4.5, 3.0, 9.0)
door.keyframe_insert("location", frame=F(14.5))
door.rotation_euler = (R(-80), R(220), R(140))
door.keyframe_insert("rotation_euler", frame=F(14.5))

# fleurs : son tas grandit, le sien est déjà là
M_stem = mat("tige", (0.15, 0.5, 0.2), 0.6)
PETALS = [mat("p%d" % i, c, 0.5) for i, c in
          enumerate([(1, 0.3, 0.35), (1, 0.8, 0.2), (0.9, 0.5, 1), (1, 1, 1), (1, 0.55, 0.2)])]


def flower(x, y, rotz, appear=None):
    root = empty("fleur", loc=(x, y, 0.02))
    root.rotation_euler = (R(90), 0, rotz)
    cyl(0.012, 0.36, (0, 0.18, 0), M_stem, root, rot=(R(90), 0, 0))
    pm = random.choice(PETALS)
    for k in range(5):
        a = k / 5 * 6.28
        sphere(0.04, (math.cos(a) * 0.045, 0.37, math.sin(a) * 0.045), pm, root, scale=(1, 0.4, 1), seg=12)
    sphere(0.03, (0, 0.37, 0), mat("coeur", (1, 0.85, 0.2), 0.5), root, seg=12)
    if appear is not None:
        root.scale = (0.001, 0.001, 0.001)
        root.keyframe_insert("scale", frame=max(1, F(appear) - 1))
        root.scale = (1, 1, 1)
        root.keyframe_insert("scale", frame=F(appear))
    return root


apps = [2.45] + [2.7] * 3 + [4.5] * 3 + [6.3] * 3
for i, ta in enumerate(apps):
    flower(random.uniform(-0.45, 0.45), -random.uniform(0.12, 0.55), random.uniform(-0.6, 0.6) + math.pi, ta)
for i in range(10):
    flower(random.uniform(-0.45, 0.45), random.uniform(0.12, 0.55), random.uniform(-0.6, 0.6))

# coupes franches : interpolation constante pour les sauts (positions/rotations de racine)
for o in bpy.data.objects:
    ad = o.animation_data
    if not ad or not ad.action:
        continue
    for fc in ad.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.easing = "AUTO"
for c, cut_times in ((lui, [7.9, 14.5]), (elle, [14.5])):
    ad = c["root"].animation_data
    for fc in ad.action.fcurves:
        if fc.data_path == "rotation_euler":
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"

# ------------------------------------------------------------------ lumières
bpy.ops.object.light_add(type="SUN", location=(0, 0, 10), rotation=(R(55), R(15), R(-35)))
moon = bpy.context.active_object
moon.data.energy = 0.55
moon.data.color = (0.6, 0.7, 1.0)
moon.data.angle = R(4)
bpy.ops.object.light_add(type="AREA", location=(-1.2, -2.2, 2.6))
lamp = bpy.context.active_object
lamp.data.energy = 160
lamp.data.size = 1.5
lamp.data.color = (1.0, 0.75, 0.45)
lamp.rotation_euler = (R(55), 0, R(-25))
bpy.ops.object.light_add(type="AREA", location=(1.5, 2.4, 2.4))
rim = bpy.context.active_object
rim.data.energy = 90
rim.data.size = 2
rim.data.color = (0.55, 0.65, 1.0)
rim.rotation_euler = (R(-55), 0, R(150))
# lumière chaude côté elle + toutes les lampes visent la porte
bpy.ops.object.light_add(type="AREA", location=(1.1, 2.6, 2.2))
side = bpy.context.active_object
side.data.energy = 140
side.data.size = 1.5
side.data.color = (1.0, 0.72, 0.5)
aim = empty("visee", loc=(0, 0, 0.8))
for L in (lamp, rim, side):
    cst = L.constraints.new("TRACK_TO")
    cst.target = aim
    cst.track_axis = "TRACK_NEGATIVE_Z"
    cst.up_axis = "UP_Y"
# chaleur qui monte au moment du retournement
bpy.ops.object.light_add(type="POINT", location=(0, 0, 1.6))
glow = bpy.context.active_object
glow.data.color = (1.0, 0.7, 0.4)
glow.data.shadow_soft_size = 1.0
glow.data.energy = 0
glow.data.keyframe_insert("energy", frame=F(13.4))
glow.data.energy = 70
glow.data.keyframe_insert("energy", frame=F(15.0))

# ------------------------------------------------------------------ caméra (même découpage)
bpy.ops.object.camera_add()
cam = bpy.context.active_object
cam.data.lens = 32
sc.camera = cam
target = empty("cible")
con = cam.constraints.new("TRACK_TO")
con.target = target
con.track_axis = "TRACK_NEGATIVE_Z"
con.up_axis = "UP_Y"

SHOTS = [  # (t, position caméra, cible, coupe?)
    (0.0, (-1.55, -3.6, 1.35), (-0.05, -0.7, 1.05), True),
    (2.65, (-1.4, -3.3, 1.3), (-0.05, -0.75, 1.0), False),
    (2.7, (-1.05, -2.7, 1.45), (0.0, -0.6, 1.15), True),
    (4.45, (-1.0, -2.6, 1.45), (0.0, -0.6, 1.15), False),
    (4.5, (-0.85, -2.3, 0.55), (0.0, -0.7, 1.3), True),
    (6.25, (-0.8, -2.2, 0.55), (0.0, -0.7, 1.3), False),
    (6.3, (-2.1, -1.9, 1.15), (0.0, -0.5, 0.95), True),
    (8.35, (-2.0, -1.9, 1.1), (0.0, -0.5, 0.8), False),
    (8.4, (-1.2, -2.5, 0.95), (0.0, -0.45, 0.6), True),
    (11.0, (-0.55, -1.55, 0.78), (0.0, -0.4, 0.6), False),
    (12.4, (4.2, -0.4, 3.1), (0.0, 0.0, 0.5), False),
    (13.3, (4.0, -0.3, 2.9), (0.0, 0.0, 0.7), False),
    (14.4, (3.2, -0.1, 1.9), (0.0, 0.0, 1.2), False),
    (16.0, (3.6, 0.0, 1.5), (0.0, 0.0, 1.25), False),
    (18.2, (3.4, 0.0, 1.45), (0.0, 0.0, 1.25), False),
]
for t, p, tg, cut in SHOTS:
    f = F(t)
    cam.location = p
    target.location = tg
    cam.keyframe_insert("location", frame=f)
    target.keyframe_insert("location", frame=f)
for o in (cam, target):
    for fc in o.animation_data.action.fcurves:
        kps = fc.keyframe_points
        for i, kp in enumerate(kps):
            t = (kp.co.x - 1) / FPS
            nxt = SHOTS[i + 1] if i + 1 < len(SHOTS) else None
            kp.interpolation = "CONSTANT" if (nxt and nxt[3]) else "BEZIER"
            if nxt and not nxt[3] and i >= 9:
                kp.interpolation = "BEZIER"
            elif nxt and not nxt[3]:
                kp.interpolation = "LINEAR"

# ------------------------------------------------------------------ rendu
r = sc.render
r.engine = "BLENDER_EEVEE"
ee = sc.eevee
ee.taa_render_samples = 24
ee.use_gtao = True
ee.use_bloom = True
ee.bloom_intensity = 0.04
ee.use_soft_shadows = True
ee.shadow_cube_size = "1024"
ee.shadow_cascade_size = "2048"
sc.cycles.device = "CPU"
sc.cycles.samples = 40
sc.cycles.use_denoising = False
try:
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
except Exception:
    pass
sc.cycles.max_bounces = 4
r.resolution_x, r.resolution_y = 720, 1280
r.resolution_percentage = 100
r.image_settings.file_format = "PNG"
r.filepath = OUT + "/f_"
sc.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
sc.view_settings.look = "None"
bpy.ops.wm.save_as_mainfile(filepath=OUT + "/porte3d.blend")
print("SCENE OK", N, "images")

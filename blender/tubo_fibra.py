"""
WaterFiberSim - modello 3D di un tubo risanato con fibra ottica a elica.

Scena in sezione "a cipolla": tubo ospite (tagliato corto), guaina in composito
semitrasparente, fibra a elica annegata nella guaina, fibra di riferimento
dritta, interrogatore a un capo. Spessori e fibra sono esagerati per vederli.

Uso:
  blender --python WaterFiberSim/blender/tubo_fibra.py
  blender -b --python WaterFiberSim/blender/tubo_fibra.py -- --render out.png [--save out.blend]
"""
import math
import sys

import bpy
from mathutils import Vector

# ---- parametri (unità di scena: metri, scala libera) ----------------------
ALFA_DEG = 70          # angolo dell'elica rispetto all'asse del tubo
L_GUAINA = 5.0         # lunghezza visibile della guaina (e della fibra)
L_OSPITE = 2.6         # lunghezza del tubo ospite (tagliato per vedere dentro)
R_OSPITE = 0.55        # raggio esterno tubo ospite
T_OSPITE = 0.07        # spessore tubo ospite
T_GUAINA = 0.06        # spessore guaina
R_FIBRA_TUBO = 0.012   # raggio del "filo" che disegna la fibra (esagerato)
PUNTI_PER_GIRO = 96

R_GUAINA = R_OSPITE - T_OSPITE              # raggio esterno guaina = interno ospite
R_ELICA = R_GUAINA - T_GUAINA / 2           # fibra a metà spessore della guaina
PASSO = 2 * math.pi * R_ELICA / math.tan(math.radians(ALFA_DEG))


# ---- utilità ---------------------------------------------------------------
def pulisci_scena():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for blocco in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for item in list(blocco):
            if item.users == 0:
                blocco.remove(item)


def imposta(bsdf, nomi, valore):
    """Imposta il primo input esistente tra `nomi` (i nomi cambiano tra versioni)."""
    for n in nomi:
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = valore
            return


def materiale(nome, colore, alpha=1.0, rough=0.5, metal=0.0, emissione=0.0, transm=0.0):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    imposta(bsdf, ["Base Color"], (*colore, 1.0))
    imposta(bsdf, ["Roughness"], rough)
    imposta(bsdf, ["Metallic"], metal)
    imposta(bsdf, ["Alpha"], alpha)
    imposta(bsdf, ["Transmission Weight", "Transmission"], transm)
    if emissione > 0:
        imposta(bsdf, ["Emission Color", "Emission"], (*colore, 1.0))
        imposta(bsdf, ["Emission Strength"], emissione)
    if alpha < 1.0:
        if hasattr(m, "surface_render_method"):      # Blender >= 4.2
            m.surface_render_method = "BLENDED"
        if hasattr(m, "blend_method"):              # Blender < 4.2
            try:
                m.blend_method = "BLEND"
            except TypeError:
                pass
    return m


def tubo(nome, r_est, spessore, x0, lunghezza, mat):
    """Cilindro cavo lungo l'asse X, da x0 a x0+lunghezza."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=160, radius=r_est, depth=lunghezza, end_fill_type="NOTHING",
        location=(x0 + lunghezza / 2, 0, 0), rotation=(0, math.pi / 2, 0))
    ob = bpy.context.active_object
    ob.name = nome
    mod = ob.modifiers.new("spessore", "SOLIDIFY")
    mod.thickness = spessore
    mod.offset = -1.0          # verso l'interno
    mod.use_even_offset = True
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(mat)
    return ob


def curva(nome, punti, raggio, mat):
    cu = bpy.data.curves.new(nome, type="CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = raggio
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new("POLY")
    sp.points.add(len(punti) - 1)
    for p, (x, y, z) in zip(sp.points, punti):
        p.co = (x, y, z, 1.0)
    ob = bpy.data.objects.new(nome, cu)
    bpy.context.collection.objects.link(ob)
    cu.materials.append(mat)
    return ob


def etichetta(testo, pos, camera, dim=0.16):
    bpy.ops.object.text_add(location=pos)
    ob = bpy.context.active_object
    ob.name = f"etichetta - {testo}"
    ob.data.body = testo
    ob.data.size = dim
    ob.data.align_x = "CENTER"
    ob.rotation_euler = camera.matrix_world.to_euler()   # parallelo all'immagine
    ob.data.materials.append(materiale(f"testo {testo}", (0.05, 0.05, 0.05), rough=0.9))
    return ob


# ---- scena -----------------------------------------------------------------
def costruisci():
    pulisci_scena()

    m_ospite = materiale("tubo ospite", (0.35, 0.36, 0.38), rough=0.7, metal=0.3)
    m_guaina = materiale("guaina composito", (0.93, 0.85, 0.62), alpha=0.35, rough=0.3, transm=0.3)
    m_fibra = materiale("fibra elica", (1.0, 0.35, 0.0), rough=0.2, emissione=1.5)
    m_rif = materiale("fibra riferimento", (0.05, 0.3, 1.0), rough=0.2, emissione=2.0)
    m_box = materiale("interrogatore", (0.12, 0.2, 0.35), rough=0.4)
    m_cavo = materiale("cavo", (0.08, 0.08, 0.08), rough=0.6)

    tubo("tubo ospite", R_OSPITE, T_OSPITE, 0.0, L_OSPITE, m_ospite)
    tubo("guaina", R_GUAINA, T_GUAINA, 0.0, L_GUAINA, m_guaina)

    # fibra a elica: x avanza di PASSO a ogni giro
    giri = L_GUAINA / PASSO
    n = max(2, int(giri * PUNTI_PER_GIRO))
    elica = []
    for i in range(n + 1):
        x = L_GUAINA * i / n
        th = 2 * math.pi * x / PASSO
        elica.append((x, R_ELICA * math.cos(th), R_ELICA * math.sin(th)))
    curva("fibra a elica", elica, R_FIBRA_TUBO, m_fibra)

    # fibra di riferimento dritta (in tubetto libero: sente solo la temperatura)
    ang = math.radians(-125)
    y_r, z_r = R_ELICA * math.cos(ang), R_ELICA * math.sin(ang)
    curva("fibra di riferimento", [(0, y_r, z_r), (L_GUAINA, y_r, z_r)], R_FIBRA_TUBO, m_rif)

    # interrogatore + cavi di collegamento
    box_pos = Vector((-1.5, -0.6, -0.3))
    bpy.ops.mesh.primitive_cube_add(size=1, location=box_pos)
    box = bpy.context.active_object
    box.name = "interrogatore"
    box.scale = (0.7, 0.5, 0.35)
    bpy.ops.object.modifier_add(type="BEVEL")
    box.modifiers["Bevel"].width = 0.03
    box.data.materials.append(m_box)
    uscita = box_pos + Vector((0.35, 0.0, 0.05))
    for inizio, nome in ((elica[0], "cavo elica"), ((0, y_r, z_r), "cavo riferimento")):
        a = Vector(inizio)
        punti = [uscita, uscita + Vector((0.5, 0, 0)), a + Vector((-0.5, 0, 0)), a]
        curva(nome, [tuple(p) for p in punti], R_FIBRA_TUBO * 1.4, m_cavo)

    # luci e camera
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 6), rotation=(math.radians(40), math.radians(10), math.radians(30)))
    bpy.context.active_object.data.energy = 1.5
    bpy.ops.object.light_add(type="AREA", location=(2.5, -4, 3))
    luce = bpy.context.active_object
    luce.data.energy = 120
    luce.data.size = 4

    bpy.ops.object.empty_add(location=(1.6, 0, -0.2))
    mira = bpy.context.active_object
    mira.name = "mira camera"
    bpy.ops.object.camera_add(location=(1.7, -8.2, 4.0))
    cam = bpy.context.active_object
    cam.data.lens = 35
    c = cam.constraints.new("TRACK_TO")
    c.target = mira
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    bpy.context.scene.camera = cam

    bpy.context.view_layer.update()          # risolve il constraint della camera
    # etichette
    etichetta("tubo ospite", (1.3, 0, R_OSPITE + 0.3), cam)
    etichetta("guaina (composito)", (3.9, 0, R_GUAINA + 0.3), cam)
    etichetta(f"fibra a elica, alfa = {ALFA_DEG} gradi", (3.8, -0.6, -1.0), cam)
    etichetta("fibra di riferimento (temperatura)", (3.8, -0.6, -1.3), cam, dim=0.13)
    etichetta("interrogatore", tuple(box_pos + Vector((0, 0, 0.5))), cam)

    # mondo e render
    sc = bpy.context.scene
    sc.world = sc.world or bpy.data.worlds.new("mondo")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.93, 0.94, 0.96, 1.0)
    bg.inputs["Strength"].default_value = 0.9
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    sc.view_settings.view_transform = "Standard"

    print(f"[WaterFiberSim] alfa = {ALFA_DEG} gradi, passo elica = {PASSO:.3f} m, "
          f"giri = {giri:.1f}, fibra per metro di tubo = {1 / math.cos(math.radians(ALFA_DEG)):.2f} m")


def render(percorso):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"           # funziona anche senza GPU / senza display
    sc.cycles.samples = 64
    sc.cycles.device = "CPU"
    sc.render.filepath = percorso
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    costruisci()
    if "--save" in argv:
        bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(argv[argv.index("--save") + 1]))
    if "--render" in argv:
        render(argv[argv.index("--render") + 1])

"""
WaterFiberSim - sezione 3D a gradini del tubo risanato (strati come in uno spaccato "a cavo spelato").

Strati dall'esterno: tubo ospite, guaina di risanamento (con la fibra a elica annegata e il tubicino con la fibra di
riferimento), acqua. Ogni strato è più corto di quello che contiene, così si vedono tutti; la faccia frontale mostra
gli anelli. Spessori non in scala. Le didascalie le aggiunge blender/sezione_tubo_figura.py.

    python blender/sezione_tubo.py -- --render blender/sezione_tubo_3d.png --save blender/sezione_tubo.blend
(apri blender/sezione_tubo.blend con Blender 4.2 per vederlo e modificarlo)
"""
import json
import math
import os
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tubo_fibra import cilindro_pieno, curva, materiale, pulisci_scena, taglia_quarto, tubo  # noqa: E402

R_OSPITE, T_OSPITE = 1.00, 0.13
R_GUAINA, T_GUAINA = R_OSPITE - T_OSPITE, 0.17
R_ACQUA = R_GUAINA - T_GUAINA
L_OSPITE, L_GUAINA, L_ACQUA = 2.0, 3.6, 3.6     # l'acqua resta dentro la guaina
R_ELICA = R_ACQUA + 0.06                 # elica annegata nella parte interna della guaina
ALFA = 70
PASSO = 2 * math.pi * R_ELICA / math.tan(math.radians(ALFA))
R_TUB, T_TUB = 0.045, 0.008
R_RIF = R_GUAINA - 0.065                 # tubicino nella parte esterna della guaina
TH_RIF = math.radians(120)


def elica(x0, x1, n=900):
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        th = math.radians(100) + 2 * math.pi * x / PASSO
        pts.append((x, R_ELICA * math.cos(th), R_ELICA * math.sin(th)))
    return pts


def costruisci():
    pulisci_scena()
    m_ospite = materiale("tubo ospite", (0.23, 0.24, 0.27), rough=0.55, metal=0.6)
    m_guaina = materiale("guaina", (0.86, 0.62, 0.30), alpha=0.32, rough=0.45)
    m_acqua = materiale("acqua", (0.45, 0.70, 0.95), alpha=0.6, rough=0.1)
    m_elica = materiale("fibra a elica", (0.95, 0.25, 0.0), rough=0.35, emissione=0.3)
    m_tub = materiale("tubicino", (0.97, 0.97, 1.0), alpha=0.1, rough=0.1)
    m_rif = materiale("fibra di riferimento", (0.02, 0.06, 0.35), rough=0.4)

    ospite = tubo("tubo ospite", R_OSPITE, T_OSPITE, 0.0, L_OSPITE, m_ospite)
    guaina = tubo("guaina", R_GUAINA, T_GUAINA, 0.0, L_GUAINA, m_guaina)
    taglia_quarto(ospite, -0.1, L_OSPITE + 0.1)          # spaccato: tolto il quarto verso chi guarda
    taglia_quarto(guaina, -0.1, L_GUAINA + 0.1)
    cilindro_pieno("acqua", R_ACQUA - 0.003, 0.0, L_ACQUA, m_acqua)
    curva("fibra a elica", elica(0.0, L_GUAINA), 0.03, m_elica)
    c = (R_RIF * math.cos(TH_RIF), R_RIF * math.sin(TH_RIF))
    tubo("tubicino", R_TUB, T_TUB, 0.0, L_GUAINA, m_tub, centro=c, vertici=48)
    curva("fibra di riferimento", [(0.0, c[0], c[1] - 0.008), (L_GUAINA, c[0], c[1] - 0.008)], 0.026, m_rif)

    # luci e camera
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 6),
                             rotation=(math.radians(40), math.radians(-15), math.radians(-30)))
    bpy.context.active_object.data.energy = 2.2
    bpy.ops.object.light_add(type="AREA", location=(-3.5, -4.0, 4.0))
    a = bpy.context.active_object
    a.data.energy = 600
    a.data.size = 6
    bpy.ops.object.empty_add(location=(2.0, 0, -0.15))
    mira = bpy.context.active_object
    bpy.ops.object.camera_add(location=(-3.6, -5.2, 3.0))
    cam = bpy.context.active_object
    cam.data.lens = 40
    t = cam.constraints.new("TRACK_TO")
    t.target = mira
    t.track_axis = "TRACK_NEGATIVE_Z"
    t.up_axis = "UP_Y"
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = 1800, 1100
    sc.world = sc.world or bpy.data.worlds.new("mondo")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bg.inputs["Strength"].default_value = 0.9
    sc.view_settings.view_transform = "Standard"
    sc.render.film_transparent = True            # sfondo trasparente: la figura lo mette su bianco
    bpy.context.view_layer.update()

    def sulla_superficie(x, r, th_deg):
        th = math.radians(th_deg)
        return Vector((x, r * math.cos(th), r * math.sin(th)))

    # punti indicati dalle didascalie: tutti su superfici VISIBILI (fuori dal quarto tolto: y < 0, z > 0)
    x_e = 2.0                                   # punto dell'elica nel quarto aperto, in basso (lontano dal tubicino)
    while x_e < L_GUAINA:
        th = math.radians(100) + 2 * math.pi * x_e / PASSO
        if math.cos(th) < -0.8 and 0.15 < math.sin(th) < 0.45:
            break
        x_e += 0.002
    punti = {
        "ospite": sulla_superficie(0.9, R_OSPITE, 205),            # faccia esterna grigia, davanti in basso
        "guaina": sulla_superficie(2.75, R_GUAINA, 205),           # guaina scoperta oltre il tubo ospite
        "elica": Vector((x_e, R_ELICA * math.cos(th), R_ELICA * math.sin(th))),
        "tubicino": Vector((1.6, c[0], c[1] + R_TUB)),
        "acqua": sulla_superficie(3.0, R_ACQUA * 0.98, 160),       # acqua vista dal quarto aperto
    }
    W, H = sc.render.resolution_x, sc.render.resolution_y
    pixel = {}
    for k, p in punti.items():
        u, v, _ = world_to_camera_view(sc, cam, p)
        pixel[k] = (round(u * W, 1), round((1 - v) * H, 1))
    return {"risoluzione": [W, H], "pixel": pixel, "alfa_deg": ALFA}


def render(percorso, info):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = int(os.environ.get("WFS_SAMPLES", 128))
    sc.cycles.device = "CPU"
    sc.render.filepath = str(Path(percorso).resolve())
    bpy.ops.render.render(write_still=True)
    Path(percorso).with_suffix(".json").write_text(json.dumps(info, indent=2))


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    info = costruisci()
    if "--save" in argv:
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(argv[argv.index("--save") + 1]).resolve()), compress=False)
    if "--render" in argv:
        render(argv[argv.index("--render") + 1], info)

"""
WaterFiberSim - spaccato 3D di un tubo risanato con il sensore in fibra ottica (BOTDA).

Cosa si vede:
  - tubo ospite tagliato per un quarto (spaccato), guaina in composito, acqua in pressione;
  - UNA SOLA fibra ad anello:
      porta A dell'interrogatore -> ANDATA a elica nella guaina (sente pressione + temperatura)
      -> giunzione in fondo al tratto -> RITORNO dritto in un tubetto libero (sente solo temperatura)
      -> porta B dello stesso interrogatore;
  - frecce lungo la fibra: verso in cui cresce la distanza z (z = 0 alla porta A); frecce rosse della pressione.
  La fibra ha un solo colore perché è una sola: andata e ritorno indicano solo dove passa.
Spessori e fibra sono esagerati per vederli.

Le spiegazioni testuali le aggiunge blender/schema_sensore.py sopra il render, usando le
posizioni dei punti notevoli che questo script scrive in un .json accanto al render.
In Blender le etichette 3D sono visibili nella vista ma escluse dal render.

Uso:
  blender --python blender/tubo_fibra.py
  blender -b --python blender/tubo_fibra.py -- --render blender/tubo_fibra_3d.png [--save blender/tubo_fibra.blend]
Testato con Blender 4.2 LTS e 5.0 (un .blend salvato con la 5.0 non si apre con la 4.2).
"""
import json
import math
import sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

# ---- parametri (unità di scena: metri, scala libera) ----------------------
ALFA_DEG = 70          # angolo dell'elica rispetto all'asse del tubo
L = 5.6                # lunghezza del tratto di tubo
R_OSPITE = 0.72        # raggio esterno tubo ospite
T_OSPITE = 0.08        # spessore tubo ospite
T_GUAINA = 0.11        # spessore guaina
R_FIBRA = 0.018        # raggio del "filo" che disegna la fibra (esagerato)
TAGLIO = (0.5, L - 0.5)  # tratto in cui il tubo ospite è tagliato per un quarto
FINESTRA = (1.0, 4.3)    # tratto in cui sono tagliate anche guaina e acqua (si vede dentro)
PUNTI_PER_GIRO = 96

R_GUAINA = R_OSPITE - T_OSPITE              # raggio esterno guaina = interno ospite
R_ACQUA = R_GUAINA - T_GUAINA               # raggio interno guaina
R_ELICA = R_ACQUA + 0.025                   # elica nella parte interna della guaina
R_TUBETTO, T_TUBETTO = 0.03, 0.006          # tubetto libero della fibra di riferimento
R_RIF = R_GUAINA - R_TUBETTO                # tubetto nella parte esterna della guaina
TH_RIF = math.radians(135)                  # posizione angolare del tubetto (nel quarto tagliato)
TH_ELICA0 = math.radians(90)                # l'elica parte dall'alto
PASSO = 2 * math.pi * R_ELICA / math.tan(math.radians(ALFA_DEG))

BOX = Vector((-1.9, -0.2, -0.1))           # interrogatore
PORTA_A = BOX + Vector((0.46, 0, 0.18))
PORTA_B = BOX + Vector((0.46, 0, -0.22))


# ---- utilità ---------------------------------------------------------------
def pulisci_scena():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
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
    m.diffuse_color = (*colore, alpha)               # colore nella vista "solid"
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


def tubo(nome, r_est, spessore, x0, lunghezza, mat, centro=(0.0, 0.0), vertici=160):
    """Cilindro cavo lungo l'asse X, da x0 a x0+lunghezza."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertici, radius=r_est, depth=lunghezza, end_fill_type="NOTHING",
        location=(x0 + lunghezza / 2, *centro), rotation=(0, math.pi / 2, 0))
    ob = bpy.context.active_object
    ob.name = nome
    mod = ob.modifiers.new("spessore", "SOLIDIFY")
    mod.thickness = spessore
    mod.offset = -1.0          # verso l'interno
    mod.use_even_offset = True
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(mat)
    return ob


def cilindro_pieno(nome, r, x0, lunghezza, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=r, depth=lunghezza,
                                        location=(x0 + lunghezza / 2, 0, 0), rotation=(0, math.pi / 2, 0))
    ob = bpy.context.active_object
    ob.name = nome
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(mat)
    return ob


def taglia_quarto(ob, x0, x1):
    """Spaccato: toglie il quarto rivolto verso la camera (y < 0, z > 0) tra x0 e x1."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, -1.0, 1.0))
    cutter = bpy.context.active_object
    cutter.name = f"taglio {ob.name}"
    cutter.scale = (x1 - x0, 2.0, 2.0)
    cutter.hide_render = True
    cutter.hide_viewport = True
    mod = ob.modifiers.new("spaccato", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.object = cutter


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


def liscia(ctrl, n=24):
    """Curva morbida (Catmull-Rom) che passa per i punti di controllo."""
    c = [Vector(p) for p in ctrl]
    c = [c[0]] + c + [c[-1]]
    out = []
    for i in range(1, len(c) - 2):
        p0, p1, p2, p3 = c[i - 1], c[i], c[i + 1], c[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(c[-2])
    return [tuple(p) for p in out]


def freccia(nome, base, direzione, lungo, raggio, mat, asta=0.0):
    """Cono (punta di freccia) con base in `base`, orientato lungo `direzione`; asta opzionale."""
    d = Vector(direzione).normalized()
    rot = d.to_track_quat("Z", "Y").to_euler()
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=raggio, radius2=0, depth=lungo,
                                    location=Vector(base) + d * (asta + lungo / 2), rotation=rot)
    cono = bpy.context.active_object
    cono.name = nome
    cono.data.materials.append(mat)
    if asta > 0:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=raggio * 0.4, depth=asta,
                                            location=Vector(base) + d * (asta / 2), rotation=rot)
        bpy.context.active_object.name = f"{nome} (asta)"
        bpy.context.active_object.data.materials.append(mat)
    return cono


def punto_elica(x):
    th = TH_ELICA0 + 2 * math.pi * x / PASSO
    return Vector((x, R_ELICA * math.cos(th), R_ELICA * math.sin(th)))


def tangente_elica(x, dx=1e-3):
    return (punto_elica(x + dx) - punto_elica(x - dx)).normalized()


# ---- scena -----------------------------------------------------------------
def costruisci():
    pulisci_scena()
    arancio = (1.0, 0.30, 0.0)

    m_ospite = materiale("tubo ospite", (0.42, 0.43, 0.46), rough=0.6, metal=0.3)
    m_guaina = materiale("guaina composito", (0.93, 0.83, 0.55), alpha=0.22, rough=0.3)
    m_acqua = materiale("acqua", (0.35, 0.65, 0.95), alpha=0.10, rough=0.1)
    m_tubetto = materiale("tubetto libero", (0.95, 0.95, 0.95), alpha=0.22, rough=0.2)
    # UNA sola fibra: stesso materiale dalla porta A alla porta B (andata e ritorno sono solo il percorso)
    m_andata = m_ritorno = materiale("fibra ottica", arancio, rough=0.3, emissione=0.7)
    m_pressione = materiale("pressione", (0.9, 0.0, 0.0), rough=0.4, emissione=1.2)
    m_box = materiale("interrogatore", (0.16, 0.22, 0.32), rough=0.4)
    m_giunto = materiale("giunzione", (0.25, 0.25, 0.25), rough=0.5, metal=0.4)

    # tubo ospite (spaccato), guaina, acqua
    ospite = tubo("tubo ospite", R_OSPITE, T_OSPITE, 0.0, L, m_ospite)
    taglia_quarto(ospite, *TAGLIO)
    guaina = tubo("guaina", R_GUAINA, T_GUAINA, 0.0, L, m_guaina)
    taglia_quarto(guaina, *FINESTRA)
    acqua = cilindro_pieno("acqua", R_ACQUA - 0.005, 0.0, L, m_acqua)
    taglia_quarto(acqua, *FINESTRA)

    # ANDATA: fibra a elica, x da 0 a L
    n = max(2, int(L / PASSO * PUNTI_PER_GIRO))
    elica = [tuple(punto_elica(L * i / n)) for i in range(n + 1)]
    curva("fibra ANDATA - elica (pressione + temperatura)", elica, R_FIBRA, m_andata)

    # RITORNO: fibra dritta in tubetto libero, leggermente ondulata (è libera, non tesa)
    y_r, z_r = R_RIF * math.cos(TH_RIF), R_RIF * math.sin(TH_RIF)
    tubo("tubetto libero", R_TUBETTO, T_TUBETTO, 0.0, L, m_tubetto, centro=(y_r, z_r), vertici=48)
    rif = [(L - x, y_r, z_r - 0.004 + 0.008 * math.sin(2 * math.pi * x / 0.9))
           for x in [L * i / 300 for i in range(301)]]
    curva("fibra RITORNO - dritta in tubetto libero (solo temperatura)", rif, R_FIBRA * 0.8, m_ritorno)

    # giunzione in fondo: l'elica esce dalla guaina, entra nella giunzione, torna nel tubetto
    giunto = Vector((L + 0.8, -0.55, 0.0))
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.15, depth=0.5, location=giunto,
                                        rotation=(0, math.pi / 2, 0))
    bpy.context.active_object.name = "giunzione (le due fibre sono saldate qui)"
    bpy.context.active_object.data.materials.append(m_giunto)
    fine_elica = punto_elica(L)
    curva("anello: elica -> giunzione",
          liscia([fine_elica, fine_elica + Vector((0.35, 0, 0)), giunto + Vector((-0.25, 0, 0))]),
          R_FIBRA, m_andata)
    curva("anello: giunzione -> tubetto",
          liscia([giunto + Vector((-0.25, 0, -0.06)), Vector((L + 0.3, y_r, z_r)), Vector((L, y_r, z_r))]),
          R_FIBRA * 0.8, m_ritorno)

    # interrogatore con due porte
    bpy.ops.mesh.primitive_cube_add(size=1, location=BOX)
    box = bpy.context.active_object
    box.name = "interrogatore BOTDA"
    box.scale = (0.9, 0.7, 0.8)
    bpy.ops.object.modifier_add(type="BEVEL")
    box.modifiers["Bevel"].width = 0.03
    box.data.materials.append(m_box)
    for porta, mat, nome in ((PORTA_A, m_andata, "porta A"), (PORTA_B, m_ritorno, "porta B")):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.07, depth=0.06, location=porta,
                                            rotation=(0, math.pi / 2, 0))
        bpy.context.active_object.name = nome
        bpy.context.active_object.data.materials.append(mat)

    # cavi di collegamento: stessa fibra, stesso colore del tratto che collegano
    ini_elica = punto_elica(0.0)
    cavo_a = liscia([PORTA_A, PORTA_A + Vector((0.5, 0, 0)), ini_elica + Vector((-0.6, 0, 0)), ini_elica])
    cavo_b = liscia([Vector((0, y_r, z_r)), Vector((-0.6, y_r, z_r)), PORTA_B + Vector((0.5, 0, 0)), PORTA_B])
    curva("cavo porta A -> inizio elica", cavo_a, R_FIBRA, m_andata)
    curva("cavo fine tubetto -> porta B", cavo_b, R_FIBRA * 0.8, m_ritorno)

    # frecce di verso
    for i, x in enumerate((0.9, 2.4, 3.9, 5.4)):
        freccia(f"verso andata {i}", punto_elica(x), tangente_elica(x), 0.24, 0.08, m_andata)
    for i, x in enumerate((4.9, 3.4, 1.9)):
        freccia(f"verso ritorno {i}", (x, y_r, z_r + 0.09), (-1, 0, 0), 0.24, 0.075, m_ritorno)
    k = len(cavo_a) // 2
    freccia("verso andata cavo", cavo_a[k], Vector(cavo_a[k + 1]) - Vector(cavo_a[k]), 0.24, 0.08, m_andata)
    k = len(cavo_b) // 2
    freccia("verso ritorno cavo", cavo_b[k], Vector(cavo_b[k + 1]) - Vector(cavo_b[k]), 0.24, 0.075, m_ritorno)

    # pressione dell'acqua: frecce radiali verso le pareti visibili attraverso la finestra
    for i, x in enumerate((1.6, 2.65, 3.7)):
        for th in (215, 270, 325, 30):
            d = Vector((0, math.cos(math.radians(th)), math.sin(math.radians(th))))
            freccia(f"pressione {i}-{th}", Vector((x, 0, 0)) + d * 0.06, d, 0.12, 0.06, m_pressione, asta=0.24)

    # luci e camera
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 6),
                             rotation=(math.radians(35), math.radians(10), math.radians(25)))
    bpy.context.active_object.data.energy = 2.0
    bpy.ops.object.light_add(type="AREA", location=(2.5, -5, 4))
    luce = bpy.context.active_object
    luce.data.energy = 250
    luce.data.size = 6

    bpy.ops.object.empty_add(location=(1.85, 0, -0.1))
    mira = bpy.context.active_object
    mira.name = "mira camera"
    bpy.ops.object.camera_add(location=(0.6, -6.6, 4.6))
    cam = bpy.context.active_object
    cam.data.lens = 26
    c = cam.constraints.new("TRACK_TO")
    c.target = mira
    c.track_axis = "TRACK_NEGATIVE_Z"
    c.up_axis = "UP_Y"
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = 1800, 1000
    bpy.context.view_layer.update()          # risolve il constraint della camera

    # punti notevoli (per le didascalie aggiunte fuori da Blender) e etichette 3D solo per la vista
    x_vis = 2.4
    while (punto_elica(x_vis).y > -0.1 or punto_elica(x_vis).z < 0.1) and x_vis < 3.4:
        x_vis += 0.01                        # un punto dell'elica ben visibile nel quarto aperto
    punti = {
        "interrogatore": BOX + Vector((0, -0.35, 0.4)),
        "porta_A": PORTA_A,
        "porta_B": PORTA_B,
        "elica": punto_elica(x_vis),
        "riferimento": Vector((2.6, y_r, z_r)),
        "giunzione": giunto,
        "ospite": Vector((L - 0.25, -R_OSPITE * 0.7, R_OSPITE * 0.7)),
        "guaina": Vector((4.8, R_GUAINA * math.cos(math.radians(120)), R_GUAINA * math.sin(math.radians(120)))),
        "acqua": Vector((2.65, 0, 0)) + Vector((0, math.cos(math.radians(270)), math.sin(math.radians(270)))) * 0.3,
    }
    nomi = {
        "interrogatore": "interrogatore BOTDA", "porta_A": "porta A", "porta_B": "porta B",
        "elica": "ANDATA: fibra a elica", "riferimento": "RITORNO: fibra dritta in tubetto libero",
        "giunzione": "giunzione", "ospite": "tubo ospite", "guaina": "guaina", "acqua": "acqua in pressione",
    }
    col = bpy.data.collections.new("etichette (solo vista, non nel render)")
    sc.collection.children.link(col)
    for k, p in punti.items():
        bpy.ops.object.text_add(location=p + Vector((0, -0.2, 0.35)))
        t = bpy.context.active_object
        t.name = f"etichetta - {nomi[k]}"
        t.data.body = nomi[k]
        t.data.size = 0.14
        t.data.align_x = "CENTER"
        t.rotation_euler = cam.matrix_world.to_euler()
        t.hide_render = True
        for c_ in list(t.users_collection):
            c_.objects.unlink(t)
        col.objects.link(t)

    W, H = sc.render.resolution_x, sc.render.resolution_y
    pixel = {}
    for k, p in punti.items():
        u, v, _ = world_to_camera_view(sc, cam, p)
        pixel[k] = (round(u * W, 1), round((1 - v) * H, 1))

    # mondo
    sc.world = sc.world or bpy.data.worlds.new("mondo")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bg.inputs["Strength"].default_value = 0.8
    sc.view_settings.view_transform = "Standard"

    info = {"alfa_deg": ALFA_DEG, "passo_scena": PASSO, "giri": L / PASSO,
            "fibra_per_metro_di_tubo": 1 / math.cos(math.radians(ALFA_DEG)),
            "risoluzione": [W, H], "pixel": pixel}
    print(f"[WaterFiberSim] alfa = {ALFA_DEG} gradi, giri = {L / PASSO:.1f}, "
          f"fibra per metro di tubo = {info['fibra_per_metro_di_tubo']:.2f} m")
    return info


def render(percorso, info):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"           # funziona anche senza GPU / senza display
    sc.cycles.samples = int(__import__("os").environ.get("WFS_SAMPLES", 96))
    sc.cycles.device = "CPU"
    sc.render.filepath = str(Path(percorso).resolve())
    bpy.ops.render.render(write_still=True)
    Path(percorso).with_suffix(".json").write_text(json.dumps(info, indent=2))


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    info = costruisci()
    if "--save" in argv:
        bpy.context.preferences.filepaths.save_version = 0   # niente copia di backup .blend1
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(argv[argv.index("--save") + 1]).resolve()),
                                    compress=False)
    if "--render" in argv:
        render(argv[argv.index("--render") + 1], info)

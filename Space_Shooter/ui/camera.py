from ursina import *
from ursina import raycast
from panda3d.core import PerspectiveLens, Camera, NodePath
from panda3d.core import Point3, Point2
from panda3d.core import BitMask32

def camera_creation(player, player2, CAM1_MASK, CAM2_MASK):
    # Créer un second DisplayRegion (vue droite)
    dr1 = base.win.make_display_region(0, 0.5, 0, 1)
    dr1.set_sort(0)
    dr2 = base.win.make_display_region(0.5, 1, 0, 1)
    dr2.set_sort(1)

    lens1 = PerspectiveLens()
    lens1.set_aspect_ratio(window.aspect_ratio / 2)
    cam_node1 = Camera('cam1', lens1)
    cam1 = NodePath(cam_node1)
    cam1.reparent_to(render)
    dr1.set_camera(cam1)

    lens2 = PerspectiveLens()
    lens2.set_aspect_ratio(window.aspect_ratio / 2)
    cam_node2 = Camera('cam2', lens2)
    cam2 = NodePath(cam_node2)
    cam2.reparent_to(render)
    dr2.set_camera(cam2)

    # Position caméras
    cam1.reparent_to(player)
    cam1.set_pos(0, 2.2, -20)
    cam1.node().get_lens().set_fov(40)  # champ de vision
    cam2.reparent_to(player2)
    cam2.node().get_lens().set_fov(40)  # champ de vision
    cam2.set_pos(0, 2.2, -20)
    cam1.node().set_camera_mask(CAM1_MASK)
    cam2.node().set_camera_mask(CAM2_MASK)
    return cam1, cam2, lens1, lens2
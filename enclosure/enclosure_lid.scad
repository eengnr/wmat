include <enclosure_config.scad>
use <enclosure_lib.scad>

finger_x0 = usb_plug_cut.x / 2 + tol;
// Stop clear of the header plastic so the finger bears on bare board, not on the header.
finger_x1 = pico_pin_x - pico_header_w / 2 - tol - 0.2;
finger_gusset_h = 3; // rib height above each finger

// 2D in the lid plane: x = world x, y = world z.
module lip_ring_2d() {
  difference() {
    translate([0, wall]) offset(delta=-tol) translate([-W_in / 2, 0]) rounded_rect_2d([W_in, H_in], inner_r);
    translate([0, wall]) offset(delta=-tol - lid_lip_t) translate([-W_in / 2, 0]) rounded_rect_2d([W_in, H_in], inner_r);
    translate([-lid_gap_x, 0]) square([2 * lid_gap_x, wall + tol + lid_lip_t + 1]);
  }
}

module sound_2d() {
  if (sound_style == "holes")
    hole_grid_2d(sound_area_r, sound_hole_d, sound_hole_pitch);
  else if (sound_style == "slots") slot_grid_2d(sound_slot_n, sound_slot_w, sound_slot_len, sound_slot_pitch, sound_slot_angle);
}

// Places 2D children (x, z) on the plane y = y0, extruded by h toward -y.
module on_lid_plane(y0, h) translate([0, y0, 0]) rotate([90, 0, 0]) linear_extrude(h) children();

// KY-006 slides in along +X until the end stop.
module piezo_rails() {
  len = ky_pcb.x + 2 * tol;
  x0 = ky_center.x - ky_pcb.x / 2 - tol;
  for (s = [-1, 1]) {
    e = ky_center.y + s * (ky_pcb.y / 2 + tol);
    // post
    translate([x0, D_out - ky_rail_h, s > 0 ? e : e - ky_rail_t]) cube([len + ky_rail_t, ky_rail_h + eps, ky_rail_t]);
    // lip
    translate([x0, D_out - ky_rail_h, s > 0 ? e - tol - ky_rail_lip : e - ky_rail_t])
      cube([len + ky_rail_t, ky_rail_lip_t, ky_rail_t + tol + ky_rail_lip]);
  }
  // end stop
  translate([x0 + len, D_out - ky_rail_h, ky_center.y - ky_pcb.y / 2 - tol - ky_rail_t])
    cube([ky_rail_t, ky_rail_h + eps, ky_pcb.y + 2 * (tol + ky_rail_t)]);
}

// Reaches just far enough onto the pcb to hold it down without reaching the mounting peg,
// whose clearance bore would otherwise pinch the finger to a third of its width.
finger_reach = 0.9; // along the pcb from its back edge

// The peg tops out below the gusset, so only the finger needs the clearance bore.
assert(finger_reach <= pico_hole_y_inset - pico_peg_d / 2 - tol,
    str("finger_reach ", finger_reach, " reaches the peg at y ",
        pico_y1 - pico_hole_y_inset, "; the clearance bore would thin the finger to ",
        finger_x1 - (pico_hole_pitch.x / 2 + pico_peg_d / 2 + 2 * tol),
        ". Keep it at or below ", pico_hole_y_inset - pico_peg_d / 2 - tol));

// Triangular rib standing on each finger, braced back against the lid's inner face. Without it
// the finger is a cantilever of 2 mm stock and the board can lever it up.
module finger_gusset() translate([finger_x0, 0, pico_pcb_z + pico_pcb.z + lid_t])
    rotate([90, 0, 90]) linear_extrude(finger_x1 - finger_x0)
      polygon([[D_out + eps, 0],
               [D_out + eps, finger_gusset_h],
               [pico_y1 - finger_reach, 0]]);

module pico_fingers() {
  z0 = pico_pcb_z + pico_pcb.z;
  for (side = [-1, 1])
    scale([side, 1, 1]) union() {
        difference() {
          translate([finger_x0, pico_y1 - finger_reach, z0])
            cube([finger_x1 - finger_x0, D_out - pico_y1 + finger_reach + eps, lid_t]);
          // clearance for the chassis pegs poking through the pcb
          translate([pico_hole_pitch.x / 2, pico_y1 - (pico_pcb.y - pico_hole_pitch.y) / 2, z0 - 1])
            cylinder(d=pico_peg_d + 2 * tol, h=lid_t + 2);
        }
        finger_gusset();
      }
}

module lid_snaps() {
  translate([0, lid_snap_y, H_out - wall - tol - eps]) snap_ridge(snap_len - 2 * tol, snap_bump);
  for (side = [-1, 1])
    scale([side, 1, 1])
      translate([W_in / 2 - tol - eps, lid_snap_y, H_out / 2]) rotate([0, 90, 0]) snap_ridge(snap_len - 2 * tol, snap_bump);
}

module lid() {
  difference() {
    union() {
      on_lid_plane(D_out + lid_t, lid_t) translate([-W_out / 2, 0]) rounded_rect_2d([W_out, H_out], edge_r);
      on_lid_plane(D_out + eps, lid_lip_d + eps) lip_ring_2d();
      lid_snaps();
      piezo_rails();
      pico_fingers();
    }
    on_lid_plane(D_out + lid_t + 1, lid_t + 2)
      translate([0, usb_center_z]) offset(r=1) offset(delta=-1) square(usb_plug_cut, center=true);
    on_lid_plane(D_out + lid_t + 1, lid_t + 2) translate(ky_center) sound_2d();
    if (sound_style != "none" && sound_wall_t > 0)
      on_lid_plane(D_out + lid_t - sound_wall_t, lid_t) translate(ky_center) circle(d=ky_disc_d - 2);
    // holes for the chassis pins
    for (s = [-1, 1])
      translate([s * (chassis_inner_w / 2 + chassis_t / 2), D_out - eps, chassis_pin_z])
        rotate([-90, 0, 0]) cylinder(d=chassis_pin_d + 2 * chassis_pin_fit, h=lid_t - 0.6 + eps);
    // pry slot for a coin or fingernail
    if (lid_grip) translate([-6, D_out - 1, -1]) cube([12, 2, 1 + wall]);
  }
}

// Outside face down on the bed.
module lid_print() translate([0, 0, D_out + lid_t]) rotate([-90, 0, 0]) lid();

lid_print();

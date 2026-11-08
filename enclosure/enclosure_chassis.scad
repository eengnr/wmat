include <enclosure_config.scad>
use <enclosure_lib.scad>

// Tray carries the Pico, side plates the switch shelf, pins press into the lid.
lip_w = 6;
lip_post_t = 1.5;
lip_gap = 2 * tol; // pcb is tilted under the lip, then lowered onto the pegs
z_tray = wall + tray_t;
plate_y0 = btn_y - switch_shelf_d / 2;
plate_x = chassis_inner_w / 2;
pin_inset = 1.5; // ledge under the switch body edge

module pico_mount() {
  for (sx = [-1, 1], front = [true, false]) {
    y = front ? pico_y0 + pico_hole_y_inset : pico_y1 - pico_hole_y_inset;
    translate([sx * pico_hole_pitch.x / 2, y, z_tray - eps]) {
      cylinder(d=so_d, h=pico_standoff_h + eps);
      if (!front)
        translate([0, 0, pico_standoff_h]) {
          cylinder(d=pico_peg_d, h=pico_pcb.z + 0.5);
          translate([0, 0, pico_pcb.z + 0.5]) cylinder(d1=pico_peg_d, d2=pico_peg_d - 0.6, h=0.3);
        }
    }
  }
  // antenna-end lip over the pcb edge
  translate([-lip_w / 2, pico_y0 - tol - lip_post_t, z_tray - eps])
    cube([lip_w, lip_post_t, pico_standoff_h + pico_pcb.z + lip_gap + lip_post_t + eps]);
  translate([-lip_w / 2, pico_y0 - tol - lip_post_t, pico_pcb_z + pico_pcb.z + lip_gap])
    cube([lip_w, lip_post_t + tol + pico_lip, lip_post_t]);
}

// Plates step down behind the shelf to clear the lid's piezo; see side_plate_* in the config.

module side_plates() {
  for (side = [-1, 1])
    scale([side, 1, 1]) difference() {
        translate([plate_x, plate_y0, wall]) cube([chassis_t, chassis_y1 - plate_y0, chassis_plate_top - wall]);
        translate([plate_x - 1, side_plate_step_y, side_plate_rear_top - eps])
          cube(
            [
              chassis_t + 2,
              chassis_y1 + 1 - side_plate_step_y,
              chassis_plate_top - side_plate_rear_top + 2 * eps,
            ]
          );
        // lightening window
        translate([plate_x - 1, btn_y + switch_shelf_d / 2 + 2, z_tray + 3])
          cube(
            [
              chassis_t + 2,
              max(side_plate_step_y - (btn_y + switch_shelf_d / 2 + 2), 0),
              max(chassis_plate_top - chassis_t - z_tray - 6, 0),
            ]
          );
      }
}

// Pedestal carrying the button, with the pocket in its top and two cuts in the front face
// for the pins and cables to escape forward into the open tray.
module button_pedestal() translate([-ped_w / 2, btn_y - ped_d / 2, chassis_plate_top])
    difference() {
      cube([ped_w, ped_d, ped_h]);
      translate([-(sw_body.x + tol) / 2 + ped_w / 2, (ped_d - sw_body.y - tol) / 2, ped_h - ped_pocket_d])
        cube([sw_body.x + tol, sw_body.y + tol, ped_pocket_d + eps]);
      for (s = [-1, 1])
        translate([s * ped_slot_off - ped_slot_w / 2 + ped_w / 2, -eps, -eps])
          cube([ped_slot_w, ped_slot_depth + eps, ped_h + 2 * eps]);
    }

module switch_shelf() {
  z_shelf = chassis_plate_top;
  difference() {
    translate([-plate_x - eps, plate_y0, z_shelf - chassis_t]) cube([2 * (plate_x + eps), switch_shelf_d, chassis_t]);
  }
  button_pedestal();
}

// Bores the tray straight down onto BOOTSEL. The housing floor gets the same bore, both
// derived from one position, so they cannot end up misaligned. The tray sits on top of the
// housing floor, so its bore starts at wall, not at 0.
module bootsel_bore() translate([bootsel_x, bootsel_y, wall - eps])
    cylinder(d=bootsel_d, h=tray_t + 2 * eps);

module chassis() {
  difference() {
    union() {
      translate([-chassis_w / 2, chassis_y0, wall]) cube([chassis_w, chassis_y1 - chassis_y0, tray_t]);
      pico_mount();
      side_plates();
      switch_shelf();
      for (s = [-1, 1])
        translate([s * (plate_x + chassis_t / 2), chassis_y1 - eps, chassis_pin_z])
          rotate([-90, 0, 0]) cylinder(d=chassis_pin_d, h=tol + lid_t - 0.6);
    }
    if (bootsel_enable) bootsel_bore();
  }
}

assert(so_d >= 2.5, "pico standoffs too thin next to the USB: check pico_hole_pitch / usb_size");

// Tray down on the bed; the shelf bridges between the side plates.
module chassis_print() translate([0, -chassis_y0, -wall]) chassis();

chassis_print();

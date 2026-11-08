include <enclosure_config.scad>
use <enclosure_lib.scad>

// Local frame: z = 0 is the housing top surface, button at rest (locked, lugs along ±X).
R = btn_body_d / 2;
z_seat = -(wall + btn_seat_depth);
z_lug_top = -wall + btn_lock_depth - btn_log_depth_cor; // lug top sits in the ceiling recess

module cap_2d(inset) {
  if (btn_shape == "square")
    offset(r=2) square(btn_cap_d - 4 - 2 * inset, center=true);
  else
    circle(d=btn_cap_d - 2 * inset, $fn=2 * $fn);
}

module cap() {
  h = btn_protrude - btn_stroke;
  c = min(0.6, h / 3);
  translate([0, 0, btn_stroke]) hull() {
      linear_extrude(h - c) cap_2d(0);
      linear_extrude(h) cap_2d(c);
    }
}

module button() {
  cap();
  translate([0, 0, z_seat]) cylinder(d=btn_body_d, h=btn_stroke - z_seat + eps);
  for (a = [0, 180])
    rotate(a)
      translate([R - 0.5, -btn_lug.x / 2, z_seat]) cube([btn_lug.y + 0.5, btn_lug.x, z_lug_top - z_seat]);
  // spring centering ring
  translate([0, 0, z_seat - 1]) difference() {
      cylinder(d=spring_id - 2 * tol, h=1 + eps);
      translate([0, 0, -1]) cylinder(d=spring_id - 2 * tol - 2, h=3);
    }
  // nub onto the switch plunger
  if (btn_nub_len > 0)
    translate([0, 0, z_seat - btn_nub_len]) cylinder(d=sw_act_d + 1, h=btn_nub_len + eps);
}

// Cap down on the bed.
module button_print() translate([0, 0, btn_protrude]) rotate([180, 0, 0]) button();

button_print();

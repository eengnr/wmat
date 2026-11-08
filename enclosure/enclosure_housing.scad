include <enclosure_config.scad>
use <enclosure_lib.scad>

// Local frame of the front face: y = into the housing, z = up along the face.
module front_frame() rotate([-front_tilt, 0, 0]) children();

cavity_y = wall * tan(front_tilt) + wall / cos(front_tilt);

module win_box(s, y0, y1) translate([-s.x / 2, y0, -s.y / 2]) cube([s.x, y1 - y0, s.y]);

module disp_holes_at() {
  for (sx = [-1, 1], sz = [-1, 1])
    translate([sx * disp_hole_pitch.x / 2, 0, sz * disp_hole_pitch.y / 2]) children();
}

module display_cuts() front_frame() translate([disp_x_off, 0, disp_face_c]) {
      translate([disp_win_c.x, 0, disp_win_c.y]) {
        win_box(disp_win, -1, wall + 1);
        c = disp_win_chamfer;
        hull() {
          win_box(disp_win + [2 * c, 2 * c], -1, 0);
          win_box(disp_win, -1, c);
        }
      }
      disp_holes_at() translate([0, -1, 0]) rotate([-90, 0, 0]) cylinder(d=disp_hole_d, h=wall + 2);
    }

// Lugs enter through the ±Y notches, a quarter turn locks them in the ±X recesses.
module button_hole() {
  translate([0, btn_y, H_out - wall / 2]) {
    cylinder(d=btn_hole_d, h=wall + 2, center=true);
    lug_cut = [2 * (btn_body_d / 2 + btn_lug.y + tol), btn_lug.x + 2 * tol];
    rotate(90) cube([lug_cut.x, lug_cut.y, wall + 2], center=true);
    translate([0, 0, -wall / 2 - eps]) linear_extrude(btn_lock_depth + eps)
        square(lug_cut, center=true);
  }
}

module lid_grooves() {
  g = snap_bump + tol;
  translate([0, lid_snap_y, H_out - wall - eps]) snap_ridge(snap_len, g);
  for (side = [-1, 1])
    scale([side, 1, 1])
      translate([W_in / 2 - eps, lid_snap_y, H_out / 2]) rotate([0, 90, 0]) snap_ridge(snap_len, g);
}

// Lands the chassis front face, so a cable pushing the Pico forward is reacted by the housing
// instead of levering the chassis pins out of the lid. Ramps up from front_stop_toe to the
// full front_stop_h, then flat for the last front_stop_nose.
module front_stop() rotate([90, 0, 90]) linear_extrude(front_stop_w, center=true)
      polygon(
        concat(
          [
            [front_stop_y0, wall],
            [front_stop_y1, wall],
            [front_stop_y1, wall + front_stop_h],
            [front_stop_y1 - front_stop_nose, wall + front_stop_h],
          ],
          front_stop_toe > 0 ? [[front_stop_y0, wall + front_stop_toe]] : []
        )
      );

// Straight down through the floor to BOOTSEL. Must match the chassis tray bore exactly;
// both are derived from bootsel_x / bootsel_y / bootsel_d in the config.
module bootsel_bore() translate([bootsel_x, bootsel_y, -eps])
    cylinder(d=bootsel_d, h=wall + 2 * eps);

// Bay for the chassis: the stop takes the forward push, these take the lateral play. The ramp at
// the front is the first layer in the print, so the rib grows out of the bed instead of starting
// on air. Same profile idiom as front_stop(): the polygon is in y/z, extruded sideways.
module chassis_rails() {
  x0 = chassis_w / 2 + rail_gap;
  for (side = [-1, 1])
    scale([side, 1, 1])
      translate([x0, 0, 0]) rotate([90, 0, 90]) linear_extrude(rail_t)
        polygon([
          [front_stop_y1, wall - eps],
          [rail_y1, wall - eps],
          [rail_y1, wall + rail_h],
          [front_stop_y1 + rail_ramp, wall + rail_h],
        ]);
}

module housing() {
  union() {
    difference() {
      rounded_body(W_out, H_out, D_out, edge_r, front_edge_r, front_edge_style, front_tilt);
      translate([0, cavity_y, wall])
        rounded_body(W_in, H_in, D_out - cavity_y + 1, inner_r, 0, "round", front_tilt);
      display_cuts();
      button_hole();
      lid_grooves();
      if (bootsel_enable) bootsel_bore();
    }
    front_stop();
    chassis_rails();
  }
}

// Front face down on the bed, open back up.
module housing_print() rotate([90, 0, 0]) rotate([front_tilt, 0, 0]) housing();

housing_print();

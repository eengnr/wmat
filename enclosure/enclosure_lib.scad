// Generic helpers for the enclosure. Independent of enclosure_config.scad.

_e = 0.01;

module rounded_rect_2d(size, r) {
  rr = max(min(r, size.x / 2 - _e, size.y / 2 - _e), 0);
  if (rr > 0)
    offset(r=rr) translate([rr, rr]) square([size.x - 2 * rr, size.y - 2 * rr]);
  else
    square(size);
}

// Rounded rectangle in the XZ plane (x centered, z 0..h), extruded along +Y (y 0..t).
module xz_slab(w, h, r, t) {
  translate([0, t, 0]) rotate([90, 0, 0])
      linear_extrude(t) translate([-w / 2, 0]) rounded_rect_2d([w, h], r);
}

// Box with rounded front->back edges, rounded/chamfered front rim and optional
// front tilt about the front-bottom edge. Back face stays flat. x centered, z 0..h, y 0..d.
module rounded_body(w, h, d, r, fr = 0, fstyle = "round", tilt = 0, steps = 6) {
  L = h / cos(tilt);
  // [depth behind face, inset]
  prof =
    fr <= 0 ? [[0, 0]]
    : fstyle == "chamfer" ? [[0, fr], [fr, 0]]
    : [for (i = [0:steps]) let (a = 90 * i / steps) [fr * (1 - cos(a)), fr * (1 - sin(a))]];
  // wolpertinger: clipping to z 0..h trims the front rounding at top/bottom when tilted; fine up to ~30 deg.
  intersection() {
    hull() {
      translate([0, d - _e, 0]) xz_slab(w, h, r, _e);
      for (p = prof)
        rotate([-tilt, 0, 0]) translate([0, p[0], p[1]])
            xz_slab(w - 2 * p[1], L - 2 * p[1], max(r - p[1], 0), _e);
    }
    translate([-w, -1, 0]) cube([2 * w, d + 2, h]);
  }
}

// 45 deg ridge along X, pointing +Z. Use with +tol as groove.
module snap_ridge(len, h) {
  rotate([90, 0, 90]) linear_extrude(len, center=true)
      polygon([[-h, 0], [h, 0], [0, h]]);
}

module stadium_2d(len, w) {
  hull()for (s = [-1, 1]) translate([s * (len - w) / 2, 0]) circle(d=w);
}

// Round holes on a square grid inside radius area_r.
module hole_grid_2d(area_r, d, pitch) {
  n = floor(area_r / pitch);
  for (i = [-n:n], j = [-n:n])
    if (norm([i, j]) * pitch <= area_r - d / 2)
      translate([i * pitch, j * pitch]) circle(d=d);
}

// n parallel slots, rotated by angle (0 = along Y).
module slot_grid_2d(n, w, len, pitch, angle = 0) {
  rotate(angle)for (i = [0:n - 1])
    translate([(i - (n - 1) / 2) * pitch, 0]) rotate(90) stadium_2d(len, w);
}

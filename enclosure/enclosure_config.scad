// Enclosure parameters: Pico W + Waveshare 1.5" RGB OLED + M03-03 micro switch + KY-006 piezo.
// Coordinates: X centered (left/right), Y = 0 front -> D_out back (open side), Z = 0 floor -> H_out top.
// Every dimension below was measured against the parts in hand.

/* [General] */
wall = 2;
tol = 0.2; // printing clearance per side
gap = 1; // free air around components
edge_r = 4; // radius of the edges running front->back
front_edge_r = 2; // radius/chamfer of the edges around the front face
front_edge_style = "round"; // [round, chamfer]
front_tilt = 5;
front_stop_h = 4; // full height where the stop meets the chassis front face
front_stop_len = 8; // length from the nose back to the chassis face
front_stop_nose = 1; // flat full-height length at the chassis end
front_stop_toe = 0; // height at the display end of the ramp
front_stop_w = 18; // stop width; narrower than the cavity, centred
rail_h = 5; // chassis guard rail height
rail_t = 4; // chassis guard rail thickness, measured in from the chassis side
rail_gap = 0.5; // clearance per side, so the chassis slides in without fighting
rail_len = 40; // chassis guard rail length, from the stop backwards
extra_w = 0;
extra_h = 0;
extra_d = 0;
force_cube = false; // grow all outer dimensions to the largest one
$fn = 48;

/* [Display: Waveshare OLED-15RGB-C] */
disp_pcb = [44.8, 37.0, 3.5]; // w, h, thickness incl. components behind the glass
disp_win = [27.0, 27.0]; // visible area incl. small margin
disp_win_off = [0, 2.0]; // window center relative to pcb center
// Measured correction to that centre, in the plane of the face: +x is right seen from the front,
// +z is up along the face. Kept apart from the nominal so the measurement stays readable.
disp_win_corr = [-0.2, 0.5];
disp_win_c = disp_win_off + disp_win_corr; // where the window is actually cut
disp_win_chamfer = 1; // outer chamfer of the window for viewing angle
disp_hole_pitch = [39.5, 32.0]; // mounting hole spacing x, y, measured on the board
disp_hole_d = 2.4; // M2 clearance
disp_glass_h = 2.0; // glass/panel height above pcb front
disp_rear_h = 5; // top of the connector above the pcb back
disp_cable_d = 4; // depth behind the display for the cable to leave and turn
// FPC connector on the right edge: the cable exits sideways, so it needs bend room beside
// the window. Reserved on both sides to keep the window centred; only the right one is used.
// disp_conn_side = false back-solders the cable, trading the side room for depth behind.
disp_conn_side = true; // cable leaves through the side connector
disp_conn_out = 2.6; // connector protrusion past the board edge
disp_cable_bend = 15; // bend room beside the window, per side
disp_z_off = 0; // shift display along the front face
spacer_len = 5.8; // your M2.5 spacers; they sit behind the board
spacer_d = 5; // spacer outside diameter

/* [Pico W] */
pico_pcb = [21, 51, 1]; // w, length, thickness
pico_hole_pitch = [11.4, 47];
pico_hole_d = 2.1;
pico_header_w = 2.54; // header plastic width
pico_header_above = 8.5; // pin header length above the pcb
pico_standoff_h = 4; // board above the tray; clears the USB and components underneath
pico_comp_h = 3.5; // tallest part below the pcb now, incl. USB and BOOTSEL
usb_size = [8, 5.5, 2.9]; // micro USB receptacle w, d, h
usb_overhang = 1.3; // receptacle sticking out past the pcb
usb_recess = 0.5; // receptacle face behind the lid inner face
usb_plug_cut = [12, 8]; // lid cutout for the plug overmold

/* [BOOTSEL access, through the tray and the housing floor] */
bootsel_enable = true; // drill both holes so a toothpick can press the button
bootsel_d = 3; // cap diameter
bootsel_x = 3; // from the board centreline, i.e. 7.5 from the right edge
bootsel_y_off = 11.5; // from the pcb's rear edge, NOT the usb tip (which is 1.8 mm further on)
bootsel_cap_h = 2; // how far the cap stands proud of the pcb: ESTIMATE, measure yours

/* [Chassis (carries Pico + switch, pinned to the lid)] */
tray_t = 2;
tray_front = 2; // tray length in front of the pico (lip post)
chassis_pin_d = 3;
chassis_pin_fit = 0.1; // hole radius allowance: negative = tighter, positive = looser
pico_standoff_d = 5;
pico_lip = 1; // front lip over the pcb edge (antenna end)

/* [Micro switch M03-03] */
sw_body = [6.1, 6.1, 6.3]; // w, d, h
sw_act_h = 0.8; // plunger above body
sw_act_d = 2.8; // plunger width
sw_travel = 0.25; // travel until click
sw_overtravel = 0.4; // allowed travel after click
sw_pin_len = 3.0; // pins below body
ped_w = 12; // pedestal footprint
ped_d = 12;
ped_h = 7; // pedestal height above the shelf
ped_pocket_d = ped_h - 4.5; // button pocket in the pedestal top
ped_slot_w = 1.5; // pin/cable cuts in the front face
ped_slot_off = 1.5; // ...offset from the centreline
ped_slot_depth = 5.5; // ...and how far they reach back

/* [Spring] */
spring_id = 9.5; // must fit over the switch body diagonal
spring_wire = 0.3;
spring_free = 25;
spring_solid = 1.6;
spring_preload = 1.5;

/* [Button + switch holder] */
btn_shape = "round"; // [round, square] cap shape; body and hole stay round
btn_seat_rim = 1; // spring seat beyond spring OD
btn_seat_depth = 1.0; // seat below the inner ceiling at rest
btn_log_depth_cor = 0.3; // correction to make the logs lower
btn_flange_w = 4; // cap overhang past the hole, also the travel stop
btn_protrude = 4; // cap top above the top surface at rest
btn_pretravel = 0.9; // air between nub and plunger at rest
btn_lug = [4, 1.2]; // bayonet lug width, radial overhang
btn_lock_depth = 0.5; // detent recess in the ceiling that stops the lugs from turning
btn_y_off = 0; // shift the button front/back from the top-surface centre
chassis_t = 2;

/* [Piezo KY-006 on lid] */
ky_pcb = [19, 15, 1.6]; // w, h, thickness, landscape with the pins sideways
ky_disc_d = 12.4; // disc diameter
ky_disc_h = 8; // disc depth
ky_solder_h = 2;
ky_rail_t = 1.2;
ky_rail_lip_t = 1.2; // rail lip thickness
ky_rail_lip = 1.5; // overlap over the pcb edge
ky_slot_d = ky_disc_h + ky_pcb.z + tol; // lid face to underside of the rail lips
ky_rail_h = ky_slot_d + ky_rail_lip_t; // how far the rails hang into the housing
ky_pos = [0, 0]; // shift on the lid (x, z) from its default spot

/* [Sound opening in lid] */
sound_style = "slots"; // [holes, slots, none]
sound_area_r = 6;
sound_hole_d = 1.5;
sound_hole_pitch = 3;
sound_slot_w = 1.5;
sound_slot_len = 10;
sound_slot_pitch = 3;
sound_slot_n = 4;
sound_slot_angle = 0; // 0 = slots along print Z (no bridges)
sound_wall_t = 1.2; // thinned wall in front of the disc, 0 = off

/* [Lid] */
lid_t = 2;
lid_lip_d = 5;
lid_lip_t = 1.5;
snap_bump = 0.6;
snap_len = 8;
lid_grip = true;

/* [Hidden] */
eps = 0.01;

spring_od = spring_id + 2 * spring_wire;
sw_diag = sqrt(sw_body.x ^ 2 + sw_body.y ^ 2);
pico_peg_d = pico_hole_d - 2 * tol;

// Bayonet button goes in from outside after the chassis.
btn_stroke = btn_pretravel + sw_travel + sw_overtravel;
btn_body_d = spring_od + 2 * btn_seat_rim;
btn_hole_d = btn_body_d + 2 * tol;
btn_cap_d = btn_hole_d + 2 * btn_flange_w;

piezo_mount_w = ky_pcb.x + 2 * (tol + ky_rail_t + gap);
chassis_inner_w = max(btn_body_d, spring_od, sw_body.x, pico_pcb.x, piezo_mount_w) + 2 * tol;
chassis_w = chassis_inner_w + 2 * chassis_t;
switch_shelf_d = spring_od + 2 * chassis_t;
sw_pocket_depth = min(1, chassis_t - 0.8);

// The button stands on a pedestal rather than directly on the shelf, so its pins and cables
// can leave forward where the tray is open. sw_pocket_depth is added back to the shelf gap
// because the button still has to end up where the old shelf pocket put it.
switch_shelf_gap = btn_seat_depth + sw_body.z + sw_act_h + sw_pocket_depth + ped_h - ped_pocket_d + sw_pocket_depth;
spring_inst = switch_shelf_gap - ped_h - btn_seat_depth;
switch_stack_h = ped_h + chassis_t + sw_pin_len;
btn_nub_len = switch_shelf_gap + ped_pocket_d - ped_h - btn_seat_depth - sw_body.z - sw_act_h - btn_pretravel;

// Glass front face rests against the inner front wall:
//   disp_front_gap - disp_glass_h = wall / cos(front_tilt)
disp_front_gap = wall / cos(front_tilt) + disp_glass_h + tol;
// The connector hangs off the right edge, outboard of the stop and the chassis, so the middle
// never has to clear it. Back-soldering puts it in the way.
disp_conn_mid_d = disp_conn_side ? 0 : disp_rear_h;
disp_stack_d = disp_front_gap + disp_pcb.z + disp_conn_mid_d + disp_cable_d;
// Reserved symmetrically so the window stays centred.
disp_bend_side = disp_conn_side ? disp_cable_bend : 0;

pico_hole_y_inset = (pico_pcb.y - pico_hole_pitch.y) / 2;
pico_pin_x = pico_pcb.x / 2 - pico_header_w / 2;
// Keep the standoffs clear of the USB, which is centred and now hangs below the pcb.
so_d = min(pico_standoff_d, 2 * (pico_hole_pitch.x / 2 - usb_size.x / 2 - tol));
pico_header_tip = pico_pcb.z + pico_header_above;
pico_top_z_in = pico_standoff_h + pico_header_tip;
pico_len = pico_pcb.y + usb_overhang + usb_recess;

piezo_stack_d = ky_disc_h + ky_pcb.z + ky_solder_h;

// Board centred, because the bend room is symmetric.
disp_x_off = 0;
// Bend room is measured outboard of the window, not the board.
disp_w_min = max(disp_win.x + 2 * disp_bend_side, disp_pcb.x + disp_conn_out + 2 * gap);
W_in_min = max(disp_w_min, ky_pcb.x, chassis_w) + 2 * gap;
// Tilting swings the board's bottom-rear corner below the flat floor, by this much.
disp_tilt_drop = (wall + disp_front_gap + disp_pcb.z) * sin(front_tilt) + disp_pcb.y / 2 * (1 - cos(front_tilt));
disp_h_in = disp_pcb.y + 2 * gap + disp_tilt_drop;
H_in_min = max(disp_h_in, pico_top_z_in + gap + switch_stack_h);
D_in_base = disp_stack_d + gap + tray_front + pico_len + extra_d;

W_raw = W_in_min + extra_w + 2 * wall;
H_raw = H_in_min + extra_h + 2 * wall;
// The tilt term allows the full height, which is conservative.
D_raw = D_in_base + wall + H_raw * tan(front_tilt);
cube_s = max(W_raw, H_raw, D_raw);

W_out = force_cube ? cube_s : W_raw;
H_out = force_cube ? cube_s : H_raw;
D_out = force_cube ? cube_s : D_raw;
W_in = W_out - 2 * wall;
H_in = H_out - 2 * wall;
inner_r = max(edge_r - wall, 0.5);

// Front face (tilted about the front-bottom edge).
tilt_dy = H_out * tan(front_tilt);
face_len = H_out / cos(front_tilt);
disp_face_c = face_len / 2 + disp_z_off; // display center along the face

// Pico: USB end flush with the lid inner face (y = D_out).
pico_y1 = D_out - usb_overhang - usb_recess;
pico_y0 = pico_y1 - pico_pcb.y;
pico_pcb_z = wall + tray_t + pico_standoff_h;
chassis_y0 = pico_y0 - tray_front;

// The stop's rear face sits where the chassis front face lands when fully inserted.
front_stop_y1 = chassis_y0;
front_stop_y0 = front_stop_y1 - front_stop_len;
chassis_y1 = D_out - tol;
// Guard rails run from the stop backwards and stop short of the lid's lip ring. The front ramp
// takes the stop's slope, so the rib starts on the bed instead of on air.
rail_y1 = front_stop_y1 + rail_len;
rail_ramp = rail_h * front_stop_len / front_stop_h;
bootsel_y = pico_y1 - bootsel_y_off;
usb_center_z = pico_pcb_z - usb_size.z / 2;

// Button centred on the top surface, so it follows front_tilt. btn_zone_* is the clear span
// it has to stay within; btn_y_off nudges it from the centre.
btn_zone_y0 = wall + tilt_dy + disp_stack_d;
btn_zone_y1 = D_out - max(lid_lip_d, piezo_stack_d);
btn_y = (tilt_dy + D_out) / 2 + btn_y_off;
switch_bottom_z = H_out - wall - switch_stack_h;

// Piezo: upper half of the lid, below the lid lip.
ky_center = [ky_pos.x, H_out - wall - tol - lid_lip_t - gap - ky_pcb.y / 2 + ky_pos.y];

lid_snap_y = D_out - lid_lip_d / 2;
lid_gap_x = chassis_w / 2 + tol; // bottom lip skips the chassis tray
chassis_plate_top = H_out - wall - switch_shelf_gap;

// The side plates stay full height under the shelf and step down behind it to clear the
// lid's piezo rails.
shelf_y1 = btn_y + switch_shelf_d / 2;
side_plate_step_y = shelf_y1 + 2;
lid_rear_y0 = min(D_out - ky_rail_h, D_out - ky_disc_h - ky_pcb.z);
lid_low_z = ky_center.y - ky_pcb.y / 2 - tol - ky_rail_t;
side_plate_rear_top = min(chassis_plate_top, lid_low_z);
chassis_pin_z = (wall + tray_t + chassis_plate_top) / 2;

assert(
  spring_id >= sw_diag + 2 * tol,
  str("spring_id too small: needs >= ", sw_diag + 2 * tol)
);
assert(spring_inst < spring_free, "the spring is slack: installed longer than its free length");
assert(btn_nub_len >= 0, "switch stack too tall for the configured button and shelf");
assert(
  spring_inst - btn_stroke >= spring_solid,
  str(
    "button stroke would compress the spring to block length: installed ",
    spring_inst, " minus stroke ", btn_stroke, " is below spring_solid ", spring_solid
  )
);
assert(btn_protrude > btn_stroke, "button would sink below the housing at full travel");
assert(btn_lock_depth > 0 && btn_lock_depth < wall, "btn_lock_depth must fit inside the top wall");
assert(btn_stroke >= btn_lock_depth + 0.3, "btn_stroke too short to lift the lugs out of the lock recess");
assert(btn_flange_w > btn_lug.y + tol, "btn_flange_w too small to hide the bayonet notches");
assert(spacer_len > 0 && spacer_d > 0, "the spacers behind the display need a positive size");
assert(pico_peg_d > 0, "tol too large for the Pico mounting holes");
assert(pico_standoff_h >= pico_comp_h + tol,
    str("the standoffs hold the board ", pico_standoff_h, " above the tray but its underside is ",
        pico_comp_h, " tall: raise pico_standoff_h"));
// Floor on the gap under the switch shelf, not the design target: a 14 mm housing needs more than
// this everywhere, so only some pins take one. See "Header wiring" in BUILD.md for which.
assert(pico_standoff_h + pico_header_tip + gap + 6 <= chassis_plate_top - chassis_t,
    str("header tips reach z ", pico_standoff_h + pico_header_tip, " leaving ",
        chassis_plate_top - chassis_t - pico_standoff_h - pico_header_tip,
        " under the shelf: not enough for a Dupont housing"));
if (bootsel_enable) {
    // The bore has to land on the button and stay clear of the mounting standoffs.
    assert(abs(bootsel_x) + bootsel_d / 2 < pico_pcb.x / 2,
        "the BOOTSEL bore runs off the side of the board");
    assert(bootsel_y - bootsel_d / 2 > chassis_y0 && bootsel_y + bootsel_d / 2 < chassis_y1,
        "the BOOTSEL bore falls outside the tray");
    assert(bootsel_y - bootsel_d / 2 > pico_y0 + pico_hole_y_inset + so_d / 2
            || bootsel_y + bootsel_d / 2 < pico_y1 - pico_hole_y_inset - so_d / 2,
        str("the BOOTSEL bore at y ", bootsel_y, " overlaps a Pico standoff"));
    // And the toothpick needs somewhere to go between the tray and the cap it is pressing.
    assert(pico_standoff_h - bootsel_cap_h >= 1,
        str("only ", pico_standoff_h - bootsel_cap_h, " mm between the tray and the BOOTSEL cap: raise pico_standoff_h or lower bootsel_cap_h"));
}
assert(chassis_pin_d + 2 * chassis_pin_fit > 0, "chassis pin holes must have a positive diameter");
assert(rail_ramp < rail_len, "the guard rail front ramp is longer than the rail");
assert(rail_y1 <= D_out - lid_lip_d,
    str("the guard rails reach y ", rail_y1, " and run into the lid lip ring at ", D_out - lid_lip_d,
        ": shorten rail_len"));
assert(sound_wall_t >= 0 && sound_wall_t <= lid_t, "sound_wall_t must be between 0 and lid_t");
assert(disp_pcb.x + 2 * tol <= W_in, "display wider than the inside");
// Lowest point of the tilted display board, and its clearance over the inner floor.
disp_low_z = H_out / 2 - disp_pcb.y / 2 * cos(front_tilt) - (wall + disp_front_gap + disp_pcb.z) * sin(front_tilt);
assert(
  disp_low_z >= wall,
  str(
    "display hits the floor: low point at ", disp_low_z, ", floor at ", wall,
    ". Raise extra_h or lower front_tilt."
  )
);
assert(
  abs(ky_center.x) + ky_pcb.x / 2 + tol + ky_rail_t + gap <= chassis_inner_w / 2,
  "piezo rails hit the chassis side plates: change ky_pos"
);
assert(
  btn_y - switch_shelf_d / 2 >= btn_zone_y0 && btn_y + switch_shelf_d / 2 <= btn_zone_y1,
  "switch shelf collides with display or lid piezo: increase extra_d"
);
assert(
  switch_bottom_z >= wall + pico_top_z_in + gap || btn_y + switch_shelf_d / 2 < pico_y0,
  "switch shelf collides with the pico: increase extra_h"
);
assert(
  ky_center.y - ky_pcb.y / 2 >= usb_center_z + usb_plug_cut.y / 2 || abs(ky_center.x) >= (ky_pcb.x + usb_plug_cut.x) / 2,
  "piezo overlaps the USB cutout: change ky_pos"
);
// The stepped section of the side plates must both clear the piezo and still support the shelf.
assert(
  side_plate_rear_top <= lid_low_z + eps,
  str(
    "side plates reach z ", side_plate_rear_top, " but the lid's piezo hangs to ",
    lid_low_z, ": lower chassis_plate_top or raise the piezo"
  )
);
assert(
  side_plate_step_y <= lid_rear_y0,
  str(
    "side plates only step down at y ", side_plate_step_y,
    " but the lid's piezo reaches forward to y ", lid_rear_y0,
    ": move side_plate_step_y earlier"
  )
);
assert(
  side_plate_step_y >= shelf_y1,
  str(
    "side plates step down at y ", side_plate_step_y,
    ", inside the switch shelf which ends at y ", shelf_y1,
    ": the shelf would lose its support"
  )
);
// The board leans back, so its rear edge sits at
//   y = (disp_front_gap + disp_pcb.z) / cos(front_tilt) + z * tan(front_tilt)
// The stop's ramp is shortest at its lowest point, which is where it is checked.
front_stop_ramp_y = front_stop_y1 - front_stop_nose - front_stop_y0;
disp_board_rear_y = (disp_front_gap + disp_pcb.z) / cos(front_tilt) + disp_low_z * tan(front_tilt);
disp_stop_y_at_low = front_stop_y0 + (disp_low_z - wall) / front_stop_h * front_stop_ramp_y;
assert(
  disp_stop_y_at_low > disp_board_rear_y,
  str(
    "the front stop reaches y ", disp_stop_y_at_low, " at the board's lowest point ",
    disp_low_z, ", but the board's rear edge is at ", disp_board_rear_y,
    ": shorten front_stop_len or drop disp_cable_d"
  )
);
// The stop clears the rest of the display only while the spacers and the board edge stay
// outboard of front_stop_w. The tilt rotates about x, so it moves the spacers back in y but
// never sideways: that margin is the same at 30 deg as at 0.
assert(
  disp_hole_pitch.x / 2 - spacer_d / 2 >= front_stop_w / 2,
  str(
    "a mounting-hole spacer spans the front stop: at x ", disp_hole_pitch.x / 2,
    " it reaches to ", disp_hole_pitch.x / 2 - spacer_d / 2,
    ", the stop covers to ", front_stop_w / 2, ": narrow front_stop_w"
  )
);
assert(
  disp_pcb.x / 2 >= front_stop_w / 2,
  str("front_stop_w ", front_stop_w, " is wider than the display", disp_pcb.x)
);
// Same reasoning for the chassis, which is only 2.9 mm clear of the spacers.
assert(
  disp_hole_pitch.x / 2 - spacer_d / 2 >= chassis_w / 2,
  str(
    "a mounting-hole spacer spans the chassis: it reaches to x ",
    disp_hole_pitch.x / 2 - spacer_d / 2, ", the chassis to ", chassis_w / 2
  )
);
// The spacers stand off along the board normal, so the tilt swings their far ends further
// back than the board itself reaches.
disp_spacer_y = (disp_front_gap + disp_pcb.z + spacer_len) * cos(front_tilt) + (disp_face_c + disp_hole_pitch.y / 2 + spacer_d / 2) * sin(front_tilt);
assert(
  disp_spacer_y < chassis_y0,
  str(
    "the spacers reach y ", disp_spacer_y, " but the chassis starts at ", chassis_y0,
    ": shorten spacer_len or add extra_d"
  )
);
assert(
  front_stop_nose > 0 && front_stop_nose < front_stop_len,
  "front_stop_nose must be positive and shorter than the stop"
);
assert(
  front_stop_toe >= 0 && front_stop_toe < front_stop_h,
  "front_stop_toe must be between 0 and front_stop_h"
);
assert(edge_r < min(W_out, H_out) / 2, "edge_r too large");
assert(front_edge_r < min(W_out, H_out) / 2, "front_edge_r too large");

if (front_tilt > 30) echo("WARNING: front_tilt > 30 deg needs supports when printed front-down");
echo(str("Outer size W x H x D: ", W_out, " x ", H_out, " x ", D_out, " mm"));

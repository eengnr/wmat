include <enclosure_config.scad>
use <enclosure_housing.scad>
use <enclosure_lid.scad>
use <enclosure_button.scad>
use <enclosure_chassis.scad>

part = "all"; // [all, housing, lid, button, chassis]
explode = 0; // [0:5:80]
show_dummies = true;
section = false; // cut away x > 0 to look inside
wire_service_loop = 60; // extra so the Pico can lie behind the open housing while soldered

// Stand-in components (not printed). Same frame as display_cuts(): local y = 0 is the outer
// front face.
module display_dummy() rotate([-front_tilt, 0, 0]) translate([disp_x_off, disp_front_gap, disp_face_c]) {
      color("DarkGreen") translate([-disp_pcb.x / 2, 0, -disp_pcb.y / 2]) cube([disp_pcb.x, disp_pcb.z, disp_pcb.y]);
      color("Black") translate([disp_win_c.x - disp_win.x / 2 - 2, -disp_glass_h, disp_win_c.y - disp_win.y / 2 - 2])
          cube([disp_win.x + 4, disp_glass_h, disp_win.y + 4]);
      if (disp_conn_side)
        color("Gray") translate([disp_pcb.x / 2, disp_rear_h - 1.5, -disp_win_off.y])
            cube([disp_conn_out, disp_rear_h, 6]);
    }

// Header up, USB and components down.
module pico_dummy() {
  color("Green") translate([-pico_pcb.x / 2, pico_y0, pico_pcb_z]) cube([pico_pcb.x, pico_pcb.y, pico_pcb.z]);
  color("Silver") translate([-usb_size.x / 2, pico_y1 + usb_overhang - usb_size.y, pico_pcb_z - usb_size.z])
      cube([usb_size.x, usb_size.y, usb_size.z]);
  color("DimGray") for (s = [-1, 1])
    translate([s * (pico_pcb.x / 2 - pico_header_w / 2) - pico_header_w / 2, pico_y0, pico_pcb_z + pico_pcb.z])
      cube([pico_header_w, pico_pcb.y, pico_header_above]);
}

// Referenced to the top of the button pedestal, with the body sunk into its pocket.
module switch_dummy() translate([0, btn_y, chassis_plate_top + ped_h]) {
    color("Black") translate([-sw_body.x / 2, -sw_body.y / 2, -ped_pocket_d]) cube(sw_body);
    color("Red") translate([0, 0, sw_body.z - ped_pocket_d]) cylinder(d=sw_act_d, h=sw_act_h);
    color("Silver", 0.6) difference() {
        cylinder(d=spring_od, h=spring_inst);
        translate([0, 0, -1]) cylinder(d=spring_id, h=spring_inst + 2);
      }
  }

module piezo_dummy() {
  color("Blue") translate([ky_center.x - ky_pcb.x / 2, D_out - ky_disc_h - ky_pcb.z, ky_center.y - ky_pcb.y / 2])
      cube([ky_pcb.x, ky_pcb.z, ky_pcb.y]);
  color("Black") translate([ky_center.x, D_out - ky_disc_h, ky_center.y]) rotate([-90, 0, 0])
        cylinder(d=ky_disc_d, h=ky_disc_h);
}

module assembled() {
  color("LightSteelBlue", 0.5) housing();
  translate([0, explode, 0]) {
    color("SteelBlue") lid();
    color("Tan") chassis();
    if (show_dummies) { piezo_dummy(); switch_dummy(); pico_dummy(); }
  }
  translate([0, 0, explode]) color("Orange") translate([0, btn_y, H_out]) button();
  if (show_dummies) display_dummy();
}

if (part == "housing")
  housing_print();
else if (part == "lid")
  lid_print();
else if (part == "button")
  button_print();
else if (part == "chassis")
  chassis_print();
else if (section)
  difference() { assembled(); translate([0, -50, -50]) cube([W_out, D_out + 200, H_out + 200]); }
else
  assembled();

// Wire lengths: axis-aligned path from each part to the middle of the Pico header + service loop.
pico_pin_pt = [pico_pcb.x / 2 - pico_header_w / 2, (pico_y0 + pico_y1) / 2, pico_pcb_z + pico_header_tip];
function route(p) = round(abs(p.x - pico_pin_pt.x) + abs(p.y - pico_pin_pt.y) + abs(p.z - pico_pin_pt.z) + wire_service_loop);
disp_wire_y = disp_front_gap + disp_pcb.z;
disp_back_pt = [
  0,
  disp_wire_y * cos(front_tilt) + disp_face_c * sin(front_tilt),
  disp_face_c * cos(front_tilt) - disp_wire_y * sin(front_tilt),
];
sw_pt = [0, btn_y, H_out - wall - switch_shelf_gap - chassis_t];
ky_pt = [ky_center.x - ky_pcb.x / 2, D_out - piezo_stack_d, ky_center.y];
echo(str("Wire lengths (mm): display ", route(disp_back_pt), ", switch ", route(sw_pt), ", piezo ", route(ky_pt)));

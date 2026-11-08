# Enclosure

Parametric OpenSCAD housing for the Weck Mich Am Tag bedside clock. Four printed parts hold the hardware
listed in the [bill of materials](../README.md#bill-of-materials): Raspberry Pi Pico W, Waveshare
1.5" RGB OLED, KY-006 piezo buzzer and an M03-03 momentary push button.

Everything is driven from [`enclosure_config.scad`](enclosure_config.scad). The part files contain
no hardcoded dimensions, so changing a value there changes all four parts consistently. Default
outer size **63 × 43.9 × 73.3 mm**, with the display leaning back 5°.

| File                    | Description                                                    | Print |
|-------------- ----------|----------------------------------------------------------------|-------|
| enclosure_config.scad   | all parameters, derived geometry, collision asserts            | no    |
| enclosure_lib.scad      | generic helpers (rounded bodies, snap ridges, hole/slot grids) | no    |
| enclosure_housing.scad  | shell: display window, button hole, lid snap grooves           | yes   |
| enclosure_lid.scad      | lip ring, snap ridges, piezo rails, Pico fingers               | yes   |
| enclosure_chassis.scad  | tray, Pico standoffs, side plates, button pedestal             | yes   |
| enclosure_button.scad   | bayonet cap with spring seat and switch nub                    | yes   |
| enclosure_assembly.scad | viewer: explodes/sections the model, echoes wire lengths       | no    |


## Requirements

[OpenSCAD](https://openscad.org/) 2021 or newer. The models use `assert()`, `offset()` and
`linear_extrude()`; no addons.

## Printing

Open a part file and render - each calls its own `*_print()` module, so the model is already in
print orientation with its base at z = 0. Export STL per file. All four fit a 100 mm bed and need
no supports: the sound slots run along print Z specifically so they need no bridging.

| File                     | Orientation                   |
| ------------------------ | ----------------------------- |
| `enclosure_housing.scad` | front face down, open back up |
| `enclosure_lid.scad`     | outside face down             |
| `enclosure_chassis.scad` | tray down                     |
| `enclosure_button.scad`  | cap down                      |

`enclosure_assembly.scad` is a viewer, not a print file. It takes `part`, `explode`, `section` and
`show_dummies`, draws coloured stand-ins for all four components, and echoes suggested wire
lengths. Render it once before printing to see both:

```
openscad -o out.stl enclosure_assembly.scad
```

Its STL export reports a non-manifold warning; that comes from the overlapping dummies and does
not affect the individual parts. Every render echoes the outer size.

## Assembly

1. **Soldering.** Solder every connection. Use at least 12 mm cable length. There is not enough room over the Pico header for Dupont
   housings, so nothing is fitted as a connector.
2. **Wiring.** Route the display, switch and piezo wires along the chassis. The Pico header row is
   the reference point for all wire lengths.
3. **Pico W onto the chassis tray.** Tilt the board up, slide the antenna end under the lip that
   overhangs the tray edge, then lower it onto the four standoffs. The lip captures the board.
4. **Switch onto the chassis pedestal.** The switch drops into the pocket in the top of the
   pedestal; its pins hang free below it and its wires exit forward through the pedestal cuts.
   The pins need to be bent to fit into the pedestal cuts.
5. **Speaker into the lid, then lid onto the chassis.** Slide the piezo into the rails along +X
   until it stops against the end stop, disc facing out. The two pins at the rear of the side
   plates press up into the lid and locate it. The lid's fingers clamp the USB end of the Pico
   down onto its pegs.
6. **Display into the housing.** Mount it on the front wall inside the housing.
7. **Chassis and lid into the housing.** Slide it in from the open back, tray down, between the
   two guard rails until its front face lands on the stop.
8. **Button in from outside.** Put the spring through the whole and press it down with the button.
   Drop the button cap through the hole with the spring on the switch body
   underneath, then turn it a quarter turn so the lugs lock into the recesses in the ceiling. The
   cap flange ends up under the top surface, so the button is captive.

## Configuration reference

Every parameter lives in [`enclosure_config.scad`](enclosure_config.scad) with a comment on the
same line. Only the values above the `/* [Hidden] */` marker are meant to be edited; everything
below it is derived and recomputed on each render.

If you substitute a component, re-measure it. The asserts will catch a fit that no longer works,
but not a dimension that is simply the wrong number.

### What the config derives, and why

**Display position.** The glass front face rests against the inner front wall, so the standoff
behind it is derived rather than entered:

```
disp_front_gap = wall / cos(front_tilt) + disp_glass_h + tol
```

The FPC connector is on the right edge seen from the front and its cable turns inward, so bend
room is reserved beside the window - on **both** sides so the window stays centred, though only
the right side carries a cable. `disp_conn_side = false` back-solders the cable and the housing
then narrows by 15 mm.

**Front stop.** A plugged-in USB cable pushes the Pico forward. The stop takes that force in the
housing rather than letting it lever the chassis pins out of the lid. It is a ramp, so nothing is
left hanging in the air when the housing prints front-down, and at 18 mm wide only its middle ever
touches the tray.

**Guard rails.** Two ribs alongside the chassis: the stop takes the forward push, the ribs take the
lateral play. Each ramps up from the stop at the stop's own slope, so the rib starts from the housing
rather than on air, then runs flat for `rail_len`. `rail_gap` is the clearance per side that lets
the chassis slide in.

**Button position.** The button is centred on the top surface, measured from the front-top edge to
the back of the housing, so it follows `front_tilt` instead of drifting rearward as the face leans
back. `btn_y_off` moves it in millimetres, negative toward the front. The clear span it must stay
within is set by the display stack at the front and the lid lip or piezo at the back.

**Pedestal.** The switch sits on a raised pedestal so its pins and cables leave through two cuts
in the front face, where the tray ahead of the side plates is open - that is what lets a switch
already soldered to the Pico drop in afterwards. `ped_pocket_d` is written as `ped_h` − 4.5 on
purpose: it fixes the button's absolute height however tall the pedestal is.

**Spring.** Not budgeted at its free length. It drops in vertically beside the switch body, the
button caps it, and the pair settles as the button turns into the bayonet - roughly the switch's
own height, 6.6 mm installed from 25 mm free. `spring_free` is documentation, not a geometry input.

**Piezo.** Mounted in landscape with the bent solder pins pointing sideways along the lid rather
than out of it, so they lengthen the footprint on that edge instead of adding to the depth budget.
The rails are anchored to the lid's rear edge.

**Standoffs.** `pico_standoff_d` is nominal; the config reduces it to whatever keeps the standoff
clear of the centred USB hanging below the board - 3.0 mm at the default hole pitch - and an
assert holds it at or above 2.5 mm.

**Front tilt** grows the depth and height rather than failing: 43.9 mm tall at 5°, 46.2 mm at 15°,
50.5 mm at 30°. Above 30° the front-face rounding is clipped by the tilt intersection and
`rounded_body()` prints a warning.

`eps` (0.01) is the modelling epsilon that avoids coincident-face artefacts. Leave it alone.

## Asserts

`enclosure_config.scad` ends with 34 `assert()` guards that catch collisions at compile time -
piezo rails against the chassis side plates, switch shelf against the Pico, button stroke against
the spring's solid height, display spacers against the front stop, and so on. A failing assertion
means the current parameter combination does not fit; the message names the parameter to change and
the two values in conflict.

OpenSCAD cannot intersect geometry inside an assertion, so collisions are checked as the
inequalities those intersections would violate. An assert only proves the model is self-consistent:
it cannot tell you a dimension is the wrong physical size, and it cannot tell you a cut landed on
material rather than in air.

## Known gaps

- The lid's top lip ring clearing the button lugs is not asserted. Both land on `H_out - 3.7`, so it
  fits, but with zero margin to absorb print variation.
- The spring is installed at roughly a quarter of its free length (6.6 mm from 25 mm). That is past
  the working range many compression springs are rated for, so the button may feel firm. If it does,
  it is a spring choice, not a modelling one.
- `bootsel_cap_h`, `spacer_d` and `usb_plug_cut` are not measured from a physical part. The asserts
  will catch a collision but not a dimension that is simply wrong.
- `spring_preload` is defined in the config but referenced by no geometry.

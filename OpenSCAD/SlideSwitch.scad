$fn = 100;

Slider =  [2.9, 2.9, 4.7];
Slide_Distance = 6.3;
Plate = [4.6, 19.5, 0.4];
Plate_Holes_Diameter = 2.5;
Body = [5.8, 10.7, 5.0];
Pins = [1.4, 0.4, 2.8];
Pins_Distance = 2.7;

e = 0.005;

Slide_Switch("#222", "#888");

module Slide_Switch(switch_color, metal_color, negative = false, backlash = 0.2) {
  b = negative ? backlash : 0;
  bc = negative ? backlash * 10 : 0;
  color(switch_color) {
    // Slider
    translate([-Slider[0] / 2, Slide_Distance / 2 - Slider[1], 0])
      cube(Slider);
    // Body and Plate
    difference() {
      union() {
        translate([-Plate[0] / 2, -Plate[1] / 2, 0])
          cube(Plate);
        translate([-(Body[0] + b) / 2, -(Body[1] + b) / 2, -Body[2] + Plate[2] - bc])
          cube([Body[0] + b, Body[1] + b, Body[2] + bc]);
      }
      if (!negative) {
        translate([-Slider[0] / 2, -Slide_Distance / 2, -e / 2])
          cube([Slider[0], Slide_Distance, Plate[2] + e]);
        for (i = [-1, 1])
          translate([0, i * (Plate[1] - Plate[0]) / 2, -e / 2])
            cylinder(Plate[2] + e, d = Plate_Holes_Diameter);
      }
    }
  }

  // Pins
  color(metal_color) {
    for (i = [-1, 0, 1])
      translate([-Pins[1] / 2, -Pins[0] / 2 + i * Pins_Distance, Plate[2] - Body[2] - Pins[2]])
        rotate([0, 0, 90])
          cube(Pins);
  }

  // Screw Holes in Case
  if (negative) {
      for (i = [-1, 1])
        translate([0, i * (Plate[1] - Plate[0]) / 2, -Body[2]])
          cylinder(Body[2] + e, d = Plate_Holes_Diameter);
  }
}

function Slide_Switch_Screw_Hole_Distance() = Plate[1] - Plate[0];
function Slide_Switch_Screw_Diameter() = Plate_Holes_Diameter;
function Slide_Switch_Plate_Thickness() = Plate[2];

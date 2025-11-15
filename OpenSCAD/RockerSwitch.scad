$fn = 200;

Cap_Height = 7.9;
Cap_Width = 9.3;
Cap_Length_2 = 8.5;
Cap_Angle = 40;
Cap_Elevation = 1.4;
Cap_Notch_Depth = 1.1;
Cap_Notch_Diameter = 9.0;

Mount_Thickness = 0.7;
Mount_Width = 7.0;
Mount_Length = 30.0;

Screw_Hole_Diameter = 3.25;
Screw_Hole_Distance = 23.5;

Holder_Base_Width = 8;
Holder_Base_Height = 5.5;
Holder_Base_Top_Diameter = 4.5;

Body_Size = [12.4, 6.7, 9.6];
Pin_Size = [0.8, 2.1, 4.0];
Pin_Distance = 4.2;

e = 0.001;

RockerSwitch("#333", "#888");

module RockerSwitch(cap_color, metal_color, negative = false, backlash = 0.2) {
  b = negative ? backlash : 0;
  // Cap
  if (!negative)
    color(cap_color) {
      difference() {
        translate([0, -Cap_Width / 2, Mount_Thickness + Cap_Elevation]) {
          cube([Cap_Length_2, Cap_Width, Cap_Height]);
            rotate([0, Cap_Angle, 0])
          translate([-Cap_Length_2, 0, 0])
              cube([Cap_Length_2, Cap_Width, Cap_Height]);
        }
        translate([0, 0, Mount_Thickness + Cap_Elevation])
          for (dir = [-1, 1]) {
            translate([0, dir * (Cap_Width / 2), 0])
              rotate([90, 0, 0])
                cylinder(Cap_Notch_Depth * 2, d = Cap_Notch_Diameter, center=true);
          }
      }
    }
  // Mount
  color(metal_color) {
    difference() {
      translate([-Mount_Length / 2, -Mount_Width / 2, 0])
        cube([Mount_Length, Mount_Width, Mount_Thickness]);
      for (dir = [-1, 1])
        translate([dir * (Screw_Hole_Distance / 2), 0, -e / 2])
          cylinder(Mount_Thickness + e, d = Screw_Hole_Diameter);
      }
    for (dir = [-1, 1]) {
      hull() {
        translate([0, dir * (Cap_Width / 2 - Mount_Thickness), Mount_Thickness / 2])
          cube([Holder_Base_Width, Mount_Thickness, Mount_Thickness], center=true);
        if (!negative)
          translate([0, dir * (Cap_Width / 2 - Mount_Thickness), Mount_Thickness])
            translate([0, 0, Mount_Thickness + Cap_Elevation])
              rotate([90, 0, 0])
                cylinder(Mount_Thickness, d = Holder_Base_Top_Diameter, center=true);
      }
    }
  }

  // Body
  color("#800") {
    translate([-(Body_Size[0] + b) / 2, -(Body_Size[1] + b) / 2, -Body_Size[2]])
      cube(Body_Size + [b, b, 0]);
  }

  // Pins
  color(metal_color) {
    for (i = [-1, 0, 1])
      translate([i * Pin_Distance - Pin_Size[0] / 2, -Pin_Size[1] / 2, -Pin_Size[2] - Body_Size[2]])
        cube(Pin_Size);
  }

  // Screw Holes in Case
  if (negative) {
    for (dir = [-1, 1])
      translate([dir * (Screw_Hole_Distance / 2), 0, -Body_Size[2]])
        cylinder(Body_Size[2] + e, d = Screw_Hole_Diameter);
  }
}

function Rocker_Switch_Screw_Hole_Distance() = Screw_Hole_Distance;
function Rocker_Switch_Screw_Diameter() = Screw_Hole_Diameter;
function Rocker_Switch_Plate_Thickness() = Mount_Thickness;

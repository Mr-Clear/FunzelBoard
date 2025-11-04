$fn = 100;

Knop_Length = 16;
Knop_Diameter = 14.5;

Thread_Diameter = 6.7;
Thread_Length = 15.2;
Circle_Diameter = 10.6;
Circle_Height = 1.1;

Body_Diameter = 17;
Metal_Base_Thickness = 0.8;

Metal_Pin_Size = [1.2, 2.7, 2.5];

Board_Thickness = 1.2;
Board_Extent = 3;

Body_Back_Height = 5.7;

Pin_Size = [1, 4.7, 0.4];
Pin_Distance = 2.54 * 2;

e = 0.001;

Poti("#A83");

module Poti(knop_color, metal_color = "#999", wall_thickness = 2) {
  // Knob
  color(knop_color)
    cylinder(h = Knop_Length, d = Knop_Diameter);

  translate([0, 0, -wall_thickness])
    color(metal_color) {
      cylinder(h = Thread_Length, d = Thread_Diameter);
      translate([0, 0, -Circle_Height]) {
        cylinder(h = Circle_Height, d = Circle_Diameter);
        translate([0, 0, -Metal_Base_Thickness]) {
          difference() {
            cylinder(h = Metal_Base_Thickness, d = Body_Diameter);
            for (x = [-1, 1])
              translate([0, x * ((Body_Diameter + Circle_Diameter) / 4 + e), Metal_Base_Thickness / 2])
                cube([Body_Diameter, (Body_Diameter - Circle_Diameter) / 2, Metal_Base_Thickness + e], center = true);
          }
          translate([Body_Diameter / 2 - Metal_Pin_Size[0], -Metal_Pin_Size[1] / 2, 0])
            cube(Metal_Pin_Size);
        }
      }
  }

  color("#8A4")
    translate([0, 0, -wall_thickness - Circle_Height - Metal_Base_Thickness - Board_Thickness]) {
      cylinder(h = Board_Thickness, d = Body_Diameter);
      translate([-Body_Diameter / 2, 0, 0])
        cube([Body_Diameter, Body_Diameter / 2 +Board_Extent, Board_Thickness]);
    }

  color("#AA4")
    translate([0, 0, -wall_thickness - Circle_Height - Metal_Base_Thickness - Board_Thickness - Body_Back_Height])
      cylinder(h = Body_Back_Height, d = Body_Diameter);

  color(metal_color)
  for (x = [-1, 0, 1]) {
    translate([x * (Pin_Distance + 0.5), Body_Diameter / 2 + Board_Extent + Pin_Size[1] / 2,
               -wall_thickness - Circle_Height - Metal_Base_Thickness - Board_Thickness])
      cube(Pin_Size, center = true);
  }
}

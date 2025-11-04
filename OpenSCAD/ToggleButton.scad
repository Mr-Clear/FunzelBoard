$fn = 100;

Base_Width = 13.6;
Base_Height_Outer = 1.1;
Base_Height_Inner = 2.0;
Base_Hole_Diameter = 9.3;
Button_Diameter = 9;
Button_Elevation = 1.8;
Thread_Diameter = 11;
Thread_Length = 18.1;
Extent_Height = 2.5;
Extent_Diameter = 9.6;
Pins_Distance = 6.5;
Pins_Width = 2.0;
Pins_Thickness = 0.5;
Pins_Length = 4.1;
Hex_Size = 13.7;
Hex_Thickness = 2.2;

e = 0.001;

ToggleButton("#999");

module ToggleButton(metal_color, wall_thickness = 1.5) {
  color(metal_color) {
      difference() {
        union() {
          cylinder(Base_Height_Outer, d = Base_Width);
          translate([0, 0, Base_Height_Outer])
            cylinder(Base_Height_Inner - Base_Height_Outer, d1 = Base_Width, d2 = Base_Hole_Diameter);
        }
        translate([0, 0, -e / 2])
        cylinder(Base_Height_Inner + e, d = Base_Hole_Diameter);
      }
      translate([0, 0, 0])
        cylinder(Base_Height_Inner + Button_Elevation, d = Button_Diameter);
    translate([0, 0, -Thread_Length])
      cylinder(Thread_Length, d = Thread_Diameter);
    translate([0, 0, -wall_thickness - Hex_Thickness])
      cylinder(Hex_Thickness, d = Hex_Size, $fn = 6);
  }
  color("#FFF")
    translate([0, 0, -Thread_Length - Extent_Height])
      cylinder(Extent_Height, d = Extent_Diameter);
  color("#A96")
    for (i = [-1, 1])
      translate([i * Pins_Distance / 2, 0, -Thread_Length - Extent_Height])
        rotate([0, 0, 90])
          cube([Pins_Width, Pins_Thickness, Pins_Length * 2], center = true);
}

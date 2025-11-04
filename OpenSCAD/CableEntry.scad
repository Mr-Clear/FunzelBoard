$fn = 100;

Cable_Diameter = 4.5;
Cable_In = 10;
Cable_Out = 10;
Dome_Radius = 14.4;
Hex_Diameter = 17.5;
Hex_Length = 14.8;
Nut_Thickness = 5;
Thread_Diameter = 12.2;
Thread_Length = 8.1;
Wall_Thickness = 1.5;

CableEntry("#222", Wall_Thickness);

module CableEntry(color, wall_thickness = 1.5) {
  color(color) {
    cylinder(Hex_Length, d = Hex_Diameter, $fn = 6);
    translate([0, 0, Hex_Length])
      sphere(d = Dome_Radius);
    translate([0, 0, -Thread_Length])
      cylinder(Thread_Length, d = Thread_Diameter);
    translate([0, 0, -wall_thickness - Nut_Thickness])
      cylinder(Nut_Thickness, d = Hex_Diameter, $fn = 6);
    translate([0, 0, -Thread_Length - Cable_In])
      cylinder(Cable_In + Thread_Length + Hex_Length + Dome_Radius / 2 + Cable_Out, d = Cable_Diameter);
  }
}

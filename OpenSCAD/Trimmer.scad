$fn = 100;

Body = [6.45, 6.8, 2.5];
Body_Cut_Diameter = 7.6;
Disk_Diameter = 6.2;
Disk_Height = 1.8;
Slit_Width = 0.8;
Slit_Length = 4.7;
Notch_Width = 2.6;
Notch_Depth = 1.0;
Pin_Thickness = 0.5;
Pin_Base_Height = 3.2;
Pin_Base_Width = 2.3;
Pin_Positions = [[-1, -1], [0, 1], [1, -1]];
Pin_Extent_Width = 0.75;
Pin_Extent_Height = 3.2;

e = 0.001;

Trimmer("#CCC", "#00F", "#999");

module Trimmer(disk_color, body_color, metal_color) {
  color(body_color) {
    intersection() {
      translate([-Body[0] / 2, -Body[1] / 2, Pin_Base_Height])
        cube(Body);
      translate([0, 0, Pin_Base_Height])
        cylinder(Body[2], d = Body_Cut_Diameter);
    }

    translate([-Body[0] / 2, -Body[1] / 2, Pin_Base_Height])
      cube([Body[0], Body[1] / 2, Body[2]]);
  }
  color(disk_color)
    translate([0, 0, Pin_Base_Height + Body[2]])
      difference() {
        cylinder(Disk_Height, d = Disk_Diameter);
        translate([-Slit_Length / 2, -Slit_Width / 2, -e / 2])
          cube([Slit_Length, Slit_Width, Disk_Height + e]);
        translate([-Slit_Width / 2, -Slit_Width * 1.5, Disk_Height / 2])
          cube([Slit_Width, Slit_Width * 3, Disk_Height / 2 + e]);
        translate([-Notch_Width / 2, Body[1] / 2 - Notch_Depth, -e / 2])
          cube([Notch_Width, Notch_Depth, Disk_Height + e]);
      }
  color(metal_color)
    for (pos = Pin_Positions) {
      translate([pos[0] * (Body[0] / 2 - Pin_Base_Width / 2),
                 pos[1] * (Body[1] / 2 - Pin_Thickness / 2),
                 Pin_Base_Height / 2])
        cube([Pin_Base_Width, Pin_Thickness, Pin_Base_Height], center = true);
      translate([pos[0] * (Body[0] / 2 - Pin_Base_Width / 2),
                 pos[1] * (Body[1] / 2 - Pin_Thickness / 2),
                 -Pin_Extent_Height / 2])
        cube([Pin_Extent_Width, Pin_Thickness, Pin_Extent_Height], center = true);
    }
}

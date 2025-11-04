$fn = 100;

Jacket = [14.8, 20.9];
Jacket_Height_Inner = 2.2;
Jacket_Height_Outer = 1.2;
Hole = [9.9, 15.6, 5.0];
Switch_Width = 9.5;
Switch_Diameter = 15.6;
Curvature_Height = 4.0;
Curvature_Radius = 15.0;
Joint_Pos = 1.0;
Body = [11.4, 18.1, 10.8];
Clip_Width = 4.7;
Clip_Extent = 19;
Pin = [5.0, 0.6, 8.1];
Pins_Distance = 5.9;

e = 0.01;

PowerSwitch("#222", "#888");

module PowerSwitch(switch_color, metal_color) {
  color(switch_color) {
    difference() {
      union() {
        translate([-Jacket[0] / 2, -Jacket[1] / 2, 0])
          cube([Jacket[0], Jacket[1], Jacket_Height_Inner]);
      }
      translate([-Hole[0] / 2, -Hole[1] / 2, Jacket_Height_Inner - Hole[2]])
        cube([Hole[0], Hole[1], Hole[2] + e]);
    }
    translate([0, 0, -Joint_Pos])
      rotate([18, 0, 0])
        difference() {
          rotate([0, 90, 0])
            cylinder(Switch_Width, d = Switch_Diameter, center = true);
          translate([0, 0, Curvature_Radius + Curvature_Height])
            rotate([0, 90, 0])
              cylinder(Switch_Width + e, r=Curvature_Radius, center = true);
          translate([-(Switch_Width + e) / 2, -(Switch_Diameter + e) / 2, -Curvature_Radius])
            cube([Switch_Width + e, Switch_Diameter + e, Curvature_Radius]);
        }
    translate([-Body[0] / 2, -Body[1] / 2, -Body[2]])
      cube(Body);
    translate([-Clip_Width / 2, -Clip_Extent / 2 , -Body[2]])
      cube([Clip_Width, Clip_Extent, Body[2]]);
  }
  color(metal_color) {
    for (i = [0, 1])
      translate([-Pin[0] / 2, i * Pins_Distance, -Body[2] - Pin[2]])
        cube(Pin);
  }
}

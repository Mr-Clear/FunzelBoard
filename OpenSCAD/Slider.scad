$fn = 100;

Cap_Width = 10;
Cap_Height = 8;
Cap_Thickness = 6;
Cap_Retract = 1;
Cap_Bottom_Fillet = .4;
Cap_Slit = [1.7, 3.2, 4];

Handle_Size = [1.3, 3, 5.7];
Handle_Base_Length = 6.3;
Slit_Width = 1.5;
Slit_Length = 13;

Metal_Thickness = 0.4;
Body_Size = [5.2, 18.3, 5];
Body_Metal_Height = 3;

Pin_Length = 2.5;
Hold_Pin_Width = 1.2;
Hold_Pin_Distance = 15.5;
Signal_Pin_Width = 0.8;
Signal_Pin_Thickness = 0.3;
Signal_Pin_Distance = 3.75;
Signal_Pin_Offsets = [0.6, -1.8, 0.6];

e = 0.001;

sphere_diameter = Cap_Thickness - Cap_Retract * 2;

Slider("#F00", position = $t < 0.5 ? $t * 2 : (1 - $t) * 2);

module Slider(cap_color, metal_color = "#999", black = "#222", wall_thickness = 2, position = 0.5, negative = false, backlash = 0.2) {
  b = negative ? backlash : 0;
  translate([0, (position - 0.5) * (Slit_Length - Handle_Size[1]), 0]) {
    // Cap
    if (!negative) {
      color(cap_color)
        translate([-Cap_Width / 2, -Cap_Thickness / 2])
          difference() {
            hull() {
              for (x = [sphere_diameter / 2 + Cap_Retract, Cap_Width - sphere_diameter / 2 - Cap_Retract])
                translate([x, Cap_Thickness / 2, Cap_Height - sphere_diameter / 2])
                  sphere(d = sphere_diameter);
              for (x = [Cap_Bottom_Fillet, Cap_Width - Cap_Bottom_Fillet])
                for (y = [Cap_Bottom_Fillet, Cap_Thickness - Cap_Bottom_Fillet])
                  translate([x, y, Cap_Bottom_Fillet])
                    sphere(r = Cap_Bottom_Fillet);
            }
            translate([Cap_Width / 2 - Cap_Slit[0] / 2, Cap_Thickness / 2 - Cap_Slit[1] / 2, -e])
              cube(Cap_Slit);
          }
      // Handle
      color(black) {
        translate([-Handle_Size[0] / 2, -Handle_Size[1] / 2, -wall_thickness - Metal_Thickness])
          cube([Handle_Size[0], Handle_Size[1], Handle_Size[2]]);
        translate([-Slit_Width / 2, -Handle_Base_Length / 2, -wall_thickness - Metal_Thickness - Body_Metal_Height])
          cube([Slit_Width, Handle_Base_Length, Body_Metal_Height]);
      }
    }
  }

  // Case Cutout
  if (negative) {
    translate([-(Slit_Width + b) / 2, -(Slit_Length + b) / 2, -Body_Metal_Height])
      cube([Slit_Width + b, Slit_Length + b, Body_Metal_Height]);
  }

  // Body
  difference() {
    color(metal_color)
      translate([-(Body_Size[0] + b) / 2, -(Body_Size[1] + b) / 2, -wall_thickness - Body_Metal_Height])
        cube([Body_Size[0] + b, Body_Size[1], Body_Metal_Height + b]);
    color(black)
      translate([-Slit_Width / 2, -Slit_Length / 2, -wall_thickness - Body_Metal_Height + e])
        cube([Slit_Width, Slit_Length, Body_Metal_Height]);
  }
  color("#2C2")
    translate([-(Body_Size[0] - e) / 2, -(Body_Size[1] - e) / 2, -wall_thickness - Body_Size[2]])
      cube([Body_Size[0] - e, Body_Size[1] - e, Body_Size[2] - Body_Metal_Height]);

  // Hold Pins
  base_d = (Body_Size[1] - Hold_Pin_Distance + Hold_Pin_Width) / 2;
  for(x = [-1, 1], y = [-1, 1]) {
    translate([x * Body_Size[0] / 2 - (x > 0 ? Metal_Thickness : 0),
               y * Hold_Pin_Distance / 2 - Hold_Pin_Width / 2 - (y < 0 ? (base_d - Hold_Pin_Width) : 0),
               -wall_thickness - Body_Size[2]])
      cube([Metal_Thickness, base_d, Body_Size[2] - Body_Metal_Height]);
    translate([x * Body_Size[0] / 2 - (x > 0 ? Metal_Thickness : 0),
               y * Hold_Pin_Distance / 2 - Hold_Pin_Width / 2,
               -wall_thickness - Body_Size[2] - Pin_Length])
      cube([Metal_Thickness, Hold_Pin_Width, Pin_Length]);
  }

  // Signal Pins
  for (i = [0 : 2]) {
    translate([Signal_Pin_Offsets[i] - (Signal_Pin_Thickness / 2),
               Signal_Pin_Distance * (i - 1) -Signal_Pin_Width / 2,
               -wall_thickness - Body_Size[2] - Pin_Length])
      cube([Signal_Pin_Thickness, Signal_Pin_Width, Pin_Length]);
  }
}

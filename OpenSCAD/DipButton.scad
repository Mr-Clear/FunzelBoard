$fn = 100;

Height = 8.5;
Diameter_Bottom = 3.4;
Diameter_Top = 3.0;

Base_Metal_Thickness = 0.4;
Base_Size = [6, 6.5, 3.8];

Pins_Size = [1, 0.7, 2.6];
Pins_Distance = 3.8;
Pins_Up = 1;

Dot_Diameter = 1.3;
Dot_Distance = [4.3, 4.8];

e = 0.001;

DipButton("#222", "#999");

module DipButton(button_color, metal_color, negative = false, backlash = 0.4) {
  b = negative ? backlash : 0;
  color(button_color)
    cylinder(Height, d1 = Diameter_Bottom + b, d2 = Diameter_Top + b);
  if (!negative) {
    color(metal_color)
      translate([-Base_Size[0] / 2, -Base_Size[1] / 2, -Base_Metal_Thickness])
        cube([Base_Size[0], Base_Size[1], Base_Metal_Thickness]);
    color(button_color)
      translate([-Base_Size[0] / 2, -Base_Size[1] / 2, -Base_Size[2]])
        cube([Base_Size[0], Base_Size[1], Base_Size[2] - Base_Metal_Thickness]);
    color(metal_color)
      for (x = [-1, 1], y = [-1, 1])
        translate([x * (Base_Size[0] / 2 - Pins_Size[0] / 2 + e),
                  y * (Pins_Distance / 2 + Pins_Size[1] / 2),
                  -Base_Size[2] - Pins_Size[2] / 2 + Pins_Up / 2])
          cube([Pins_Size[0], Pins_Size[1], Pins_Size[2] + Pins_Up], center = true);
    color(button_color)
      for (x = [-1, 1], y = [-1, 1])
        translate([x * Dot_Distance[0] / 2, y * Dot_Distance[1] / 2, 0])
          cylinder(e, d = Dot_Diameter);
  }
}

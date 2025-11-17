$fn = 200;

Diameter = 7;
Length = 24.4;
Cap_Length = 1.4;
Plastic_Length = 3.1;
Plastic_Cylinder_Length = 1.2;
Plastic_Small_Diameter = 4.3;
Wire_Diameter = 0.7;
Wire_Distance = 2.7;
Wire_Length = 1;

Vibrator();

function Vibrator_Size() = [Diameter, Length];
function Vibrator_Plastic_Length() = Plastic_Length;

module Vibrator(metal_color = "#888", plastic_color = "#FFF", wire_colors = ["#A00", "#028"]) {
  color(metal_color)
    translate([0, 0, Plastic_Length]) {
      cylinder(Length - Plastic_Length - Cap_Length, d = Diameter);
      intersection() {
        cylinder(Length - Plastic_Length, d = Diameter);
        r = ((Diameter / 2) ^ 2 + (Cap_Length) ^ 2) / (2 * Cap_Length); // Diameter² + (r - Cap_Length)² = r²
        translate([0, 0, Length - Plastic_Length - r])
          sphere(r);
        }
      }
  color(plastic_color)
    translate([0, 0, Plastic_Length - Plastic_Cylinder_Length])
      cylinder(Plastic_Cylinder_Length, d=Diameter);
    cylinder(Plastic_Length - Plastic_Cylinder_Length, d1 = Plastic_Small_Diameter, d2 = Diameter);

  for (i = [-1, 1]) {
    color(wire_colors[(i + 1) / 2])
      translate([i * Wire_Distance / 2, 0, -Wire_Length])
        rotate([0, 0, 0])
          cylinder(Wire_Length, d = Wire_Diameter);
  }
}

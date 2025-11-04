$fn = 100;

Cap_Diameter = 5.9;
Cap_Height = 3.6;
Cap_Foot_Diameter = 3.7;
Cap_Foot_Height = 2.0;

Thread_Diameter = 6.7;
Thread_Height = 6.2;

Metal_Base_Diameter = 9.5;
Metal_Base_Height = 2.9;

Plastic_Base_Diameter = 7.5;
Plastic_Base_Height = 6.1;

Pin_Size = [0.4, 2.2, 7.0];
Pin_Distance = 4.0;

SmallButton("#333");

module SmallButton(button_color, metal_color = "#AAA", black = "#222", negative = false) {
  color(button_color) {
    translate([0, 0, 0])
      cylinder(Cap_Foot_Height, d = Cap_Foot_Diameter);
    translate([0, 0, Cap_Foot_Height])
      cylinder(Cap_Height, d = Cap_Diameter);
  }
  color(metal_color) {
    translate([0, 0, -Thread_Height])
      cylinder(Thread_Height, d = Thread_Diameter);
    translate([0, 0, -Thread_Height - Metal_Base_Height])
      cylinder(Metal_Base_Height, d = Metal_Base_Diameter);
  }
  color(black) {
    translate([0, 0, -Thread_Height - Metal_Base_Height - Plastic_Base_Height])
      cylinder(Plastic_Base_Height, d = Plastic_Base_Diameter);
  }
  color(metal_color)
    for (x = [-1, 1]) {
      translate([x * Pin_Distance / 2, 0, -Thread_Height - Metal_Base_Height - Plastic_Base_Height - Pin_Size[2] / 2])
        cube(Pin_Size, center = true);
    }

}

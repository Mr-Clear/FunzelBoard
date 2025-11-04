$fn = 100;
Cap_Diameter = 11.4;
Cap_Height = 5.7;
Cap_Foot_Diameter = 12.8;
Cap_Foot_Height = 1.4;
Cap_Connector_Size = [5.5, 5.4, 2.4];

Press_Height = 0.35;

Base_Connector_Size = [3.7, 3.7, 3];
Base_Size = [12, 12, 3.5];

Grid_Spacing = 2.54;

Pin_Diameter = 0.8;
Pin_Length = 4.2;
Pin_Ascent = 1.0;

ColorButton("#F00");

module ColorButton(button_color, metal_color = "#999", black = "#222", negative = false) {
  // Cap
  translate([0, 0, Press_Height])
    color(button_color) {
      translate([-Cap_Connector_Size[0] / 2, -Cap_Connector_Size[1] / 2, -Cap_Connector_Size[2]])
        cube(Cap_Connector_Size);
      translate([0, 0, 0]) {
        cylinder(Cap_Height, d = Cap_Diameter);
        cylinder(Cap_Foot_Height, d = Cap_Foot_Diameter);
      }
    }

  // Base
  translate([-Base_Connector_Size[0] / 2, -Base_Connector_Size[1] / 2, -Cap_Connector_Size[2]])
    color("#FF0")
      cube(Base_Connector_Size);
  translate([-Base_Size[0] / 2, -Base_Size[1] / 2, -Cap_Connector_Size[2] - Base_Size[2]])
    color(black)
      cube(Base_Size);

  // Pins
  color(metal_color)
    for (x = [-1, 1])
      for (y = [-1, 1])
        translate([x * Grid_Spacing, 2.5 * y * Grid_Spacing, -Cap_Connector_Size[2] - Base_Size[2] - Pin_Length + Pin_Ascent])
          cylinder(Pin_Length, d = Pin_Diameter);
}

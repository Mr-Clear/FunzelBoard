$fn = 100;

Size = [20, 31.3, 6];

Bar_Width = 6.5;
Bar_Height = 3;
Bars_Bottom = 6.6;
Bars_Gap = 1.55;
Outline_Width = 1.4;
Outline_Bottom = 3.5;
Outline_Bottom_Gap = 3.4;
Outline_Top = 4.5;
Outline_Side = 4.4;
Cap_Size = [5, 2.6];
Board_Size = [16.4, 41.4, 1.2];
Board_Holes_Offset = 17.8;
Board_Holes_Diameter = 2;

Bar_Colors = ["#00F", "#00F", "#00F", "#999"];
Border_Color = "#F00";
Board_Color = "#040";

Pin_Grid = 2.54;
Pin_Size = 0.65;
Pin_Length = 7;

e = 0.01;

BatteryIndicator("#999");
function BatteryIndicator_Size() = Size;
function BatteryIndicator_Board_Size() = Board_Size;
function BatteryIndicator_Board_Holes_Offset() = Board_Holes_Offset;
function BatteryIndicator_Board_Holes_Diameter() = Board_Holes_Diameter;

module BatteryIndicator(metal_color, negative = false) {
  translate([-Size[0] / 2, -Size[1] / 2, -Size[2]]) {
    color("#000")
      difference() {
        cube(Size);
        if (!negative)
          bat();
      }
    bat();
    // Battery Board
    translate([(Size[0] - Board_Size[0]) / 2, (Size[1] - Board_Size[1]) / 2, -Board_Size[2]]) {
      difference() {
        color(Board_Color)
          cube(Board_Size);
        for (y = [-1, 1]) {
          translate([Board_Size[0] / 2, Board_Size[1] / 2 + y * Board_Holes_Offset, -e/2])
            cylinder(h = Board_Size[2] + e, d = Board_Holes_Diameter);
        }
      }
      color(metal_color) {
        // Pins
        for (i = [0 : 1]) {
          translate([Pin_Grid * (i + 0.5), Board_Size[1] - Pin_Grid, Board_Size[2] - Pin_Length + e])
            cube([Pin_Size, Pin_Size, Pin_Length]);
        }
      }
    }
  }
}

module bat() {
  translate([0, 0, e]) {
    // Bars
    for (i = [0 : 3]) {
      color(Bar_Colors[i])
        translate([(Size[0] - Bar_Width) / 2, Bars_Bottom + i * (Bar_Height + Bars_Gap), 0])
          cube([Bar_Width, Bar_Height, Size[2]]);
    }
    color(Border_Color) {
      // Outline Left/Right
      translate([Outline_Side, Outline_Bottom, 0])
        cube([Outline_Width, Size[1] - Outline_Top - Outline_Bottom, Size[2]]);
      translate([Size[0] - Outline_Side - Outline_Width, Outline_Bottom, 0])
        cube([Outline_Width, Size[1] - Outline_Top - Outline_Bottom, Size[2]]);
      // Outline Top
      translate([Outline_Side, Size[1] - Outline_Top - Outline_Width, 0])
        cube([Size[0] - Outline_Side * 2, Outline_Width, Size[2]]);
      // Outline Bottom
      translate([Outline_Side, Outline_Bottom, 0])
        cube([Size[0] / 2 - Outline_Side - Outline_Bottom_Gap / 2, Outline_Width, Size[2]]);
      translate([Size[0] / 2 + Outline_Bottom_Gap / 2, Outline_Bottom, 0])
        cube([Size[0] / 2 - Outline_Side - Outline_Bottom_Gap / 2, Outline_Width, Size[2]]);
      // Cap
      translate([(Size[0] - Cap_Size[0]) / 2, Size[1] - Outline_Top - Outline_Width, 0])
        cube([Cap_Size[0], Cap_Size[1], Size[2]]);
    }
  }
}

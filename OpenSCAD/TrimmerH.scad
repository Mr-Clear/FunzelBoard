use <Pipe.scad>;

$fn = 100;

Diameter = 10.3;
Thickness = 5.0;
Base_Thickness = 1.0;
Sunken = 0.3;
Dial_Diameter = 5.3;
Dial_Inner_Diameter = 2.8;
Dial_Sunken = 0.8;
Dial_Ring_Thickness = 0.9;
Gap_Width = 1.0;
Arrow_Width = 2.0;
Back_Dial_Diameter = 3.0;
Back_Sunken_Diameter = 5.5;
Front_Circle_Thickness = 1.0;
Front_Circle_H_Gaps = 3.0;
Pin_Thickness = 0.32;
Pin_Width = 1.1;
Pin_Length = 3.3;
Pin_Base_Width = 2.0;
Pin_Base_Length = 2.0;
Pin_Grid = 2.54;
Pins_Back_Ascent = 2.7;
Front_Circle_V_Gaps = Pin_Base_Width;
Pin_X_Offset = Pin_Grid - Thickness / 2;
Pin_Positions = [for(p = [[-1, -1], [0, 0], [-1, 1]])
  [p.x * Pin_Grid + Pin_X_Offset, p.y * Pin_Grid]];

e = 0.001;

TrimmerH("#CCC", "#222", "#999", $t * -360);

function TrimmerH_Center_Ascent() = Pin_Base_Length + Diameter / 2;
function TrimmerH_Size() = [Thickness, Diameter, Pin_Base_Length + Diameter];
function TrimmerH_Gap_Size() = Dial_Inner_Diameter;
function TrimmerH_Pin_X_Offset() = Pin_X_Offset;

module TrimmerH(disk_color, body_color, metal_color, orientation = 180) {
  // Body
  difference() {
    union() {
      color(body_color)
        translate([0, 0, TrimmerH_Center_Ascent()])
          rotate([0, 90, 0])
            difference() {
              union() {
                cylinder(Thickness, d = Diameter, center = true);
                translate([0, -Diameter / 2, -Thickness / 2 + Pin_Thickness])
                  cube([Diameter / 2, Diameter, Base_Thickness]);
              }
              translate([0, 0, -Thickness / 2 - e])
                Pipe(Pin_Thickness, Diameter, Back_Sunken_Diameter / 2);
              translate([0, 0, Thickness / 2 - Sunken - Pin_Thickness])
                cylinder(Sunken + Pin_Thickness + e, d = Diameter - Front_Circle_Thickness * 2);
              translate([-Front_Circle_H_Gaps / 2, -Diameter / 2, Thickness / 2 - Sunken - Pin_Thickness])
                cube([Front_Circle_H_Gaps, Diameter, Sunken + Pin_Thickness + e]);
              translate([-Diameter / 2, -Front_Circle_V_Gaps / 2, Thickness / 2 - Sunken - Pin_Thickness])
                cube([Diameter, Front_Circle_V_Gaps, Sunken + Pin_Thickness + e]);
            }

      color(metal_color) {
        translate([Thickness / 2 - Sunken - Pin_Thickness + e, 0, TrimmerH_Center_Ascent()])
          rotate([0, 90, 0])
            cylinder(Pin_Thickness, d=Diameter - e);
      }
    }
    translate([0, 0, TrimmerH_Center_Ascent()])
      rotate([0, 90, 0])
        cylinder(Thickness + e, d1 = Back_Dial_Diameter, d2 = Dial_Diameter, center = true);
  }

  // Dial
  color(disk_color) {
    translate([0, 0, TrimmerH_Center_Ascent()])
      rotate([0, 90, 0])
        difference() {
          cylinder(Thickness, d1 = Back_Dial_Diameter, d2 = Dial_Diameter, center = true);
          translate([0, 0, Thickness / 2 - Dial_Sunken + e])
            cylinder(Dial_Sunken + e, d1 = Dial_Inner_Diameter, d2 = Dial_Diameter - 2 * Dial_Ring_Thickness);
          rotate([0, 0, orientation]) {
            cube([Dial_Inner_Diameter, Gap_Width, Thickness + e], center = true);
            linear_extrude(Thickness + e, center = true)
              polygon([
                [Dial_Inner_Diameter / 2, 0],
                [0, Arrow_Width / 2],
                [0, -Arrow_Width / 2]
              ]);
          }
        }
  }

  // Pins
  color(metal_color) {
    for (pos = Pin_Positions) {
      translate([pos.x, pos.y - Pin_Width / 2, -Pin_Length + Pin_Width / 2])
        cube([Pin_Thickness, Pin_Width, Pin_Length - Pin_Width / 2]);
      translate([pos.x, pos.y, -Pin_Length])
        rotate([90, 0, 90])
        linear_extrude(height = Pin_Thickness)
          polygon([[0, 0], [Pin_Width / 2, Pin_Width / 2], [-Pin_Width / 2, Pin_Width / 2]]);
      translate([pos.x, pos.y - Pin_Base_Width / 2, 0])
        cube([Pin_Thickness, Pin_Base_Width, pos.x < 0 ? Pin_Base_Length + Pins_Back_Ascent : Pin_Base_Length]);
    }
  }
}

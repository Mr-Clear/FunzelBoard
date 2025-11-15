use <threadlib/threadlib.scad>

$fn = 100;
e = 0.001;
Hex_Relation = 2 / sqrt(3); // Relation between hex size and diameter

function metric_coarse_pitch(d) =
  d == 2   ? 0.4  :
  d == 2.5 ? 0.45 :
  d == 3   ? 0.5  :
  d == 4   ? 0.7  :
  d == 5   ? 0.8  :
  d == 6   ? 1.0  :
  d == 8   ? 1.25 :
  d == 10  ? 1.5  :
  1.0; // Fallback

function turns_from_length(len, d, overshoot=0) = (len + overshoot) / metric_coarse_pitch(d);

module Screw_Cylinder_Hex(diameter, length, head_diameter, head_height, hex_size, hex_depth, negative = false, always_simple = false) {
  translate([0, 0, -length])
  if ($preview || negative || always_simple)
    cylinder(length, d=diameter);
  else
    bolt(str("M", diameter), turns=turns_from_length(length, diameter), higbee_arc=30);

  difference() {
    cylinder(head_height, d=head_diameter);
    translate([0, 0, head_height - hex_depth])
      cylinder(hex_depth + e, d=hex_size * Hex_Relation, $fn=6);
  }
}

module Screw_Sunken_Hex(diameter, length, head_diameter, head_height, hex_size, hex_depth, negative = false, always_simple = false) {
  translate([0, 0, -head_height]) {
    translate([0, 0, -length])
    if ($preview || negative || always_simple)
      cylinder(length, d=diameter);
    else
      bolt(str("M", diameter), turns=turns_from_length(length, diameter), higbee_arc=30);

    difference() {
      cylinder(head_height, d1=diameter,d2=head_diameter);
      translate([0, 0, head_height - hex_depth])
        cylinder(hex_depth + e, d=hex_size * Hex_Relation, $fn=6);
    }
  }
}

module Screw_Insert(diameter, length, outer_diameter, riffle_height, riffle_diameter, negative = false, riffle_size = 0.3, always_simple = false) {
  translate([0, 0, -length])
  difference() {
    cylinder(length, d=riffle_diameter);
    translate([0, 0, -e / 2])
      if ($preview || negative || always_simple) {
        cylinder(length + e, d=diameter);
        translate([0, 0, riffle_height])
          difference() {
            cylinder(length - riffle_height * 2, d=riffle_diameter + e);
            cylinder(length - riffle_height * 2, d=outer_diameter);
          }
      } else {
        bolt(str("M", diameter), turns=turns_from_length(length, diameter), higbee_arc=30);
        riffles = floor(riffle_diameter * PI / riffle_size);
        for (a = [0 : riffles - 1]) {
          rotate([0, 0, a * 360 / riffles])
            translate([riffle_diameter / 2 - riffle_size / 4, 0, 0])
              rotate([0, 0, 180])
                cylinder(length + e, d = riffle_size, $fn=3);
        }
        translate([0, 0, riffle_height])
          difference() {
            cylinder(length - riffle_height * 2, d=riffle_diameter + e);
            cylinder(length - riffle_height * 2, d=outer_diameter);
          }
      }
  }
}

// diameter, length, head_diameter, head_height, hex_size, hex_depth
function Screw_Definition_Main() = [4, 25, 7.5, 1.1, 2.5, 1.6];
function Screw_Definition_Slide_Switch() = [2, 6, 3.7, 1.3, 1.5, 1.5];
function Screw_Definition_Rocker_Switch() = [3, 6, 5.4, 3, 2.5, 1.8];
function Screw_Definition_Battery() = [2.5, 3, 4.7, 1.6, 1.5, 1.2];
// diameter, length, outer_diameter, riffle_height, riffle_diameter
function Screw_Insert_Definition_Main() = [4, 4, 4.9, 1.1, 6];
function Screw_Insert_Definition_Slide_Switch() = [2, 2.9, 2.9, 1.0, 3.5];
function Screw_Insert_Definition_Rocker_Switch() = [3, 3.2, 3.5, 1.0, 4.1];
function Screw_Insert_Definition_Battery() = [2.5, 3, 3, 1.0, 3.5];

module Screw_Cylinder_Hex_From_Definition(definition, color, always_simple = false) {
  color(color)
    Screw_Cylinder_Hex(definition[0], definition[1], definition[2], definition[3], definition[4], definition[5], always_simple=always_simple);
}

module Screw_Sunken_Hex_From_Definition(definition, color, always_simple = false) {
  color(color)
    Screw_Sunken_Hex(definition[0], definition[1], definition[2], definition[3], definition[4], definition[5], always_simple=always_simple);
}

module Screw_Insert_From_Definition(definition, color, always_simple = false) {
  color(color)
    Screw_Insert(definition[0], definition[1], definition[2], definition[3], definition[4], always_simple=always_simple);
}

// Demo:
{
  insert_color = "#A85";
  metal_color = "#888";
  black = "#222";

  translate([0, 0, 0])
    Screw_Cylinder_Hex_From_Definition(Screw_Definition_Main(), black);

  translate([0, 0, -(25 - 4)])
    Screw_Insert_From_Definition(Screw_Insert_Definition_Main(), insert_color);

  translate([-10, 0, 0])
    Screw_Cylinder_Hex_From_Definition(Screw_Definition_Slide_Switch(), black);

  translate([-10, 0, -(6 - 2.9)])
    Screw_Insert_From_Definition(Screw_Insert_Definition_Slide_Switch(), insert_color);

  translate([10, 0, 0])
    Screw_Cylinder_Hex_From_Definition(Screw_Definition_Rocker_Switch(), metal_color);

  translate([10, 0, -(6 - 3.2)])
    Screw_Insert_From_Definition(Screw_Insert_Definition_Rocker_Switch(), insert_color);

  translate([0, 10, 0])
    Screw_Sunken_Hex_From_Definition(Screw_Definition_Battery(), black);

  translate([0, 10, -Screw_Definition_Battery()[3]])
    Screw_Insert_From_Definition(Screw_Insert_Definition_Battery(), insert_color);
}

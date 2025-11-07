$fn = 100;

Base_Size = [8.15, 13, 9.58];
Thread_Length = 8.66;
Thread_Size = "M6";
Thread_Diameter = 5.7;
Thread_Inner_Diameter = 4.4;
Thread_Notch = [1, 0.7];
Thread_Notch_Pos = 2.3;
Lever_Pivot = 15;
Lever_Length = 14;
Lever_Diameters = [2.4, 2.9];
Pin_Thickness = 0.7;
Pin_Width = 2;
Pin_Length = 4.1;
Pin_Distance = 4.4;
Jacket_Size = [9.8, 6.2];
Jacket_Thickness = 0.5;

Nut_Size = 9.2;
Nut_Thickness = 2;
Washer_Inner_Diameter = 6;
Washer_Outer_Diameter = 11.9;
Washer_Thickness = 0.52;
Washer_Notch = [2.1, 1.7];

Negative = false;

/* [Hidden] */
e = 0.001;
e2 = 2 * e;

use <threadlib/threadlib.scad>;

Switch("#00A", "#888", 12, 1.5, Negative);
ss = Switch_Size();
translate([-ss[0] / 2, -ss[1] / 2, 0])
  *cube(ss);

module Switch(base_color, metal_color, position, case_thickness, negative=false) {
  // Base
  color(base_color)
    translate([-Base_Size[0] / 2, -Base_Size[1] / 2, 0])
      cube(Base_Size);
  // Base Jacket
  color(metal_color) {
    translate([-Base_Size[0] / 2 - e, -Base_Size[1] / 2 - e, Base_Size[2] - Jacket_Thickness])
      cube([Base_Size[0] + e2, Base_Size[1] + e2, Jacket_Thickness + e]);
    for (x = [-1, 1]) {
      translate([x * (Base_Size[0] / 2 - Jacket_Thickness / 2), 0, Base_Size[2] - Jacket_Size[1] / 2])
        cube([Jacket_Thickness + e, Jacket_Size[0], Jacket_Size[1]], center=true);
    }
  }
  // Thread
  color(metal_color)
    translate([0, 0, Base_Size[2]])
      difference() {
        if (negative)
          cylinder(Thread_Length + Lever_Length, d = Thread_Diameter);
        else
          bolt(Thread_Size, Thread_Length, fn=$fn);
        if (!negative)
          translate([0, 0, Lever_Pivot - Base_Size[2]])
            cylinder(h = Thread_Length + e, d = Thread_Inner_Diameter);
        translate([-Thread_Notch[0] / 2, Thread_Notch_Pos, 0])
          cube([Thread_Notch[0], Thread_Notch[1], Thread_Length + e]);
      }

  // Lever
  color(metal_color) {
    translate([0, 0, Lever_Pivot])
      rotate([position, 0, 0]) {
        cylinder(h = Lever_Length - Lever_Diameters[1] / 2, d1 = Lever_Diameters[0], d2 = Lever_Diameters[1]);
        translate([0, 0, Lever_Length - Lever_Diameters[1] / 2])
          sphere(d = Lever_Diameters[1]);
      }
  }
  // Pins
  color(metal_color) {
    for (y = [-1, 0, 1]) {
      difference() {
        translate([0, y * Pin_Distance, -Pin_Length / 2])
          cube([Pin_Width, Pin_Thickness, Pin_Length], center=true);
        translate([0, y * Pin_Distance, -(Pin_Length - Pin_Width / 2)])
          rotate([90, 0, 0])
            cylinder(Pin_Thickness + e2, d = Pin_Width / 2, center=true);
      }
    }
  }
  // Wall mount
  if (!negative) {
    color(metal_color) {
      // Outer Nut
      translate([0, 0, Base_Size[2] + Thread_Length - Nut_Thickness])
        nut("M6", Nut_Thickness, Douter = Nut_Size, fn = $fn);
      // Outer Washer
      translate([0, 0, Base_Size[2] + Thread_Length - Nut_Thickness - Washer_Thickness]) {
        difference() {
          cylinder(Washer_Thickness, d = Washer_Outer_Diameter);
          translate([0, 0, -e])
            cylinder(Washer_Thickness + e2, d = Washer_Inner_Diameter);
        }
        translate([-Thread_Notch[0] / 2, Thread_Notch_Pos, 0])
          cube([Thread_Notch[0], Thread_Notch[1] + 0.1, Washer_Thickness]);
        translate([-Washer_Notch[0] / 2, Washer_Outer_Diameter / 2, Washer_Thickness - Washer_Notch[1]])
          cube([Washer_Notch[0], Washer_Thickness, Washer_Notch[1]]);
      }
      // Inner Washer
      translate([0, 0, Base_Size[2] + Thread_Length - Nut_Thickness - Washer_Thickness * 2 - case_thickness])
        difference() {
          cylinder(Washer_Thickness, d = Washer_Outer_Diameter);
          translate([0, 0, -e])
            cylinder(Washer_Thickness + e2, d = Washer_Inner_Diameter);
        }
      // Inner Nut
      translate([0, 0, Base_Size[2] + Thread_Length - Nut_Thickness * 2 - Washer_Thickness * 2 - case_thickness])
        nut("M6", Nut_Thickness, Douter = Nut_Size, fn = $fn);
    }
  } else {
    // Washer Notch
    translate([0, 0, Base_Size[2] + Thread_Length - Nut_Thickness - Washer_Thickness])
      translate([-Washer_Notch[0] / 2, Washer_Outer_Diameter / 2, Washer_Thickness - Washer_Notch[1]])
        cube([Washer_Notch[0], Washer_Thickness, Washer_Notch[1]]);
  }
}

function Switch_Back_Length() = Base_Size[2] + Thread_Length - Nut_Thickness - Washer_Thickness;
function Switch_Size() = [max(Base_Size[0], Washer_Outer_Diameter), max(Base_Size[1], Washer_Outer_Diameter), Lever_Pivot + Lever_Length];

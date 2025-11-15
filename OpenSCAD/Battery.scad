$fn = 200;

Case_Size = [86.0, 24.4, 23.0];
Case_Thickness_Sides = 1.5;
Case_Thickness_Ends = 2.1;
Case_Thickness_Bottom = 2.4;
Case_Top = 20.9;

Clip_Size = 15;
Clip_X = 10;
Clip_Z = 11;

Mount_Holes_Diameter = 3.1;
Mount_Holes_Distance = 55;
Power_Holes_Diameter = 8;

Battery_Size = [70, 21.3];

Negative = false;

/* [Hidden] */
e = 0.001;
e2 = 2 * e;

inner_box = [Case_Size[0] - Case_Thickness_Ends * 2, Case_Size[1] - Case_Thickness_Sides * 2, Case_Size[2] - Case_Thickness_Bottom];

Battery("#222", "#2D4", Negative);

module Battery(case_color, battery_color, negative=false) {
  // Case
  color(case_color)
    difference() {
      box(Case_Size);
      translate([0, 0, Case_Thickness_Bottom])
        box(inner_box);

      // Clips
      translate([0, 0, Clip_Z + Case_Size[2] / 2])
        cube([Clip_X * 2, Case_Size[1] + e2, Case_Size[2]], center=true);
      a = (Clip_X + Clip_Size + inner_box[0] / 2) / 2;
      for (x = [-1, 1]) {
        translate([x * a, 0, Clip_Z + Case_Size[2] / 2])
          cube([Clip_Size, Case_Size[1] + e2, Case_Size[2]], center=true);
      }
      translate([-Case_Size[0] / 2 + Case_Thickness_Ends, -Case_Size[1] / 2, Case_Top])
        cube([Case_Size[0] - Case_Thickness_Ends * 2, Case_Size[1], Case_Size[2] - Case_Top + e]);

      // Mount Holes
      for (x = [-1, 0, 1]) {
        translate([x * Mount_Holes_Distance / 2, 0, -e])
          cylinder(Case_Thickness_Bottom + e2, d = Mount_Holes_Diameter);
      }

      // Power Holes
      for (x = [-1, 1]) {
        translate([x * Case_Size[0] / 2 - e - (x > 0 ? Case_Thickness_Ends : 0), 0, Case_Thickness_Bottom + Battery_Size[1] / 2])
          rotate([0, 90, 0])
            cylinder(Case_Thickness_Bottom + e2, d = Power_Holes_Diameter);
      }
    }

  // Battery
  color(battery_color)
    translate([0, 0, Case_Thickness_Bottom + Battery_Size[1] / 2])
      rotate([0, 90, 0])
        cylinder(Battery_Size[0], d = Battery_Size[1], center=true);
}

module box(size) {
      translate([-size[0] / 2, -size[1] / 2, 0])
        cube([size[0], size[1], size[2] - size[1] / 2]);
      difference() {
        translate([-size[0] / 2, 0, size[2] - size[1] / 2])
          rotate([0, 90, 0])
            cylinder(size[0], d = size[1]);
        translate([-size[0] / 2 - e, -size[1] / 2, -size[2]])
          cube([size[0] + e2, size[1], size[2]]);
      }
}

function Battery_Size() = Battery_Size;
function Battery_Case_Size() = Case_Size;
function Battery_Case_Thickness_Bottom() = Case_Thickness_Bottom;
function Battery_Mount_Holes_Distance() = Mount_Holes_Distance;
function Battery_Power_Holes_Diameter() = Power_Holes_Diameter;

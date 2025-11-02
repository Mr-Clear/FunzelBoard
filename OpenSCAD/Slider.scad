$fn = 100;

width = 10;
height = 8;
thickness = 6;

retract = 1;
bottom_fillet = .4;

slit = [1.7, 3.2, 4];

e = 0.001;

sphere_diameter = thickness - retract * 2;
difference() {
  hull() {
    for (x = [sphere_diameter / 2 + retract, width - sphere_diameter / 2 - retract])
      translate([x, thickness / 2, height - sphere_diameter / 2])
        sphere(d = sphere_diameter);
    for (x = [bottom_fillet, width - bottom_fillet])
      for (y = [bottom_fillet, thickness - bottom_fillet])
        translate([x, y, bottom_fillet])
          sphere(r = bottom_fillet);
  }
  translate([width / 2 - slit[0] / 2, thickness / 2 - slit[1] / 2, -e])
    cube(slit);
}

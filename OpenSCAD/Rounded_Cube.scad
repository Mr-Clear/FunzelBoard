module Rounded_Cube(size, edges_default = 0, center = false, e = 0.01,
                    edges_left = 0, edges_right = 0,
                    edges_front = 0, edges_back = 0,
                    edges_top = 0, edges_bottom = 0) {
  translate(center ? -size/2 : [0,0,0])
      hull()
        for (x = [0, 1])
          for (y = [0, 1])
            for (z = [0, 1]) {
              r = max(edges_default, e,
                x ? edges_left : edges_right,
                y ? edges_front : edges_back,
                z ? edges_bottom : edges_top
              );
              intersection() {
                translate([x ? 0 : size.x / 2,
                           y ? 0 : size.y / 2,
                           z ? 0 : size.z / 2])
                  cube(size/2);
                translate([x ? r : size.x - r,
                          y ? r : size.y - r,
                          z ? r : size.z - r])
                  sphere(r = r);
              }
            }
}

// Demonstaration
$fn = 50;
Size = [100, 100, 50];
Edge_Size = 5;
Wall = 2;
intersection() {
  difference() {
    Rounded_Cube(Size, Edge_Size);
    translate([Wall, Wall, Wall])
      Rounded_Cube([Size[0] - 2 * Wall, Size[1] - 2 * Wall, Size[2] - 2 * Wall], Edge_Size - Wall);
  }
  translate([0, 0, 0])
    cube([Size[0], Size[1] / 2, Size[2] / 2]);
}
intersection() {
  difference() {
    cube(Size);
    translate([Wall, Wall, Wall])
      cube([Size[0] - 2 * Wall, Size[1] - 2 * Wall, Size[2] - 2 * Wall]);
  }
  translate([0, Size[1] / 2, 0])
    cube([Size[0], Size[1] / 2, Size[2] / 2]);
}

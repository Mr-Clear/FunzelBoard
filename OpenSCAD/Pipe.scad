e = 0.01;

module Pipe(h, r_out, r_in, $fn = $fn) {
  difference() {
    cylinder(h, r = r_out, $fn = $fn);
    translate([0, 0, -e])
      cylinder(h + e * 2, r = r_in, $fn = $fn);
  }
}

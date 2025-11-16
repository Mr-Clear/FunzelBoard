
use <Pipe.scad>;
e = 0.001;

module FilletCylinder(radius, size, always_render = false) {
  if (is_undef(global_disable_fillets) || global_disable_fillets == false || always_render)
    difference() {
      cylinder(size, r = radius + size);
      if (radius > 0)
        translate([0, 0, -e])
          cylinder(size + e * 2, r = radius);
      translate([0, 0, size])
        rotate_extrude()
          translate([radius + size, 0])
            circle(size);
    }
}

module FilletPipe(radius, size, always_render = false, $fn = $fn) {
  if (is_undef(global_disable_fillets) || global_disable_fillets == false || always_render)
    difference() {
      Pipe(size, radius, radius - size, $fn = $fn);
      translate([0, 0, size])
        rotate_extrude($fn = $fn)
          translate([radius - size, 0])
            circle(size);
    }
}

module FilletLinear(length, size, always_render = false) {
  if (is_undef(global_disable_fillets) || global_disable_fillets == false || always_render) {
    difference() {
      translate([0, 0, 0])
          cube([size, length, size]);
      translate([size, -e, size])
        rotate([-90, 0, 0])
          cylinder(length + e * 2, r = size);
    }
  }
}

module FilletCube(x, y, size, always_render = false) {
  if (is_undef(global_disable_fillets) || global_disable_fillets == false || always_render) {
    difference() {
      union() {
        translate([-size, 0, 0])
          cube([size, y, size]);
        translate([x, 0, 0])
          cube([size, y, size]);
        translate([0, -size, 0])
          cube([x, size, size]);
        translate([0, y, 0])
          cube([x, size, size]);
      }
      translate([0 - e, -size, size])
        rotate([0, 90, 0])
          cylinder(x + e * 2, r = size);
      translate([0 - e, y + size, size])
        rotate([0, 90, 0])
          cylinder(x + e * 2, r = size);
      translate([-size, y + e, size])
        rotate([90, 0, 0])
          cylinder(y + e * 2, r = size);
      translate([size + x, y + e, size])
        rotate([90, 0, 0])
          cylinder(y + e * 2, r = size);
    }
    intersection() {
      FilletCylinder(0, size, always_render);
      translate([-size, -size, 0])
        cube(size);
    }
    intersection() {
      translate([x, 0, 0])
        FilletCylinder(0, size, always_render);
      translate([x, -size, 0])
        cube(size);
    }
    intersection() {
      translate([0, y, 0])
        FilletCylinder(0, size, always_render);
      translate([-size, y, 0])
        cube(size);
    }
    intersection() {
      translate([x, y, 0])
        FilletCylinder(0, size, always_render);
      translate([x, y, 0])
        cube(size);
    }
  }
}

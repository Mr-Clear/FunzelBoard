$fn = 100;

LED_Size = [5.4, 5.4, 1.5];
Cap_Height = 10;
Cap_Diameter = 8;
Foot_Diameter = 9;
Foot_Height = 1;

Hollow_Height = 9;
Hollow_Diameter = 6.4;

Grid_Distance = 8.3;
Grid = [1, 3];
capa_size = [5, 2, 0.8];

e = 0.001;


for (y = [1:Grid[1]])
  difference() {
    for (x = [1:Grid[0]])
      translate([(x - 1) * Grid_Distance, (y - 1) * Grid_Distance, 0])
        led_cap(LED_Size,
                Cap_Height,
                Cap_Diameter,
                Foot_Diameter,
                Foot_Height,
                Hollow_Height,
                Hollow_Diameter);
    for (x = [0:Grid[0]])
      translate([(x - 0.5) * Grid_Distance - capa_size[0] / 2, (y - 1) * Grid_Distance - capa_size[1] / 2, -e])
        cube(capa_size);
  }

module led_cap(led_size = LED_Size,
               cap_height = Cap_Height,
               cap_diameter = Cap_Diameter,
               foot_diameter = Foot_Diameter,
               foot_height = Foot_Height,
               hollow_height = Hollow_Height,
               hollow_diameter = Hollow_Diameter) {
  difference() {
    union() {
      cylinder(cap_height - cap_diameter / 2, d = cap_diameter);
      translate([0, 0, cap_height - cap_diameter / 2])
        sphere(d = cap_diameter);
      cylinder(foot_height, d = foot_diameter);
    }
    translate([0, 0, -e]) {
      translate([-led_size[0] / 2, -led_size[1] / 2, ])
        cube(led_size);
      cylinder(hollow_height - hollow_diameter / 2, d = hollow_diameter);
      translate([0, 0, hollow_height - hollow_diameter / 2])
        sphere(d = hollow_diameter);
    }
    translate([0, 0, -Cap_Diameter / 2])
      cylinder(Cap_Diameter / 2 + e, d = Cap_Diameter);
  }
}


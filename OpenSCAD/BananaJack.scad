use <Pipe.scad>;

Plastic_Stick_Out_Length = 2.3;
Plastic_Stick_Out_Diameter = 10.7;

Plastic_Length = 4;
Plastic_Diameter = 7.9;

Plastic_Hole_Diameter = 6;

Plastic_Ring_Length = 4.7;

Metal_Stick_Out_Length = 1;
Metal_Stick_Out_Diameter = 7.7;
Metal_Hole_Diameter = 4;
Metal_Length = 15;
Metal_Diameter = 5.7;

Fin_Thickness = 0.5;
Fin_Length = 17.5;
Fin_Diameter_1 = 10;
Fin_Diameter_1_Inner = 6.3;
Fin_Hole_1_Diameter = 6.3;

Fin_Diameter_2 = 4.4;
Fin_Hole_2_Offset = Fin_Length - (Fin_Diameter_1 + Fin_Diameter_2) / 2;
Fin_Hole_2_Diameter = 1.6;

Nut_Thickness = 2;
Nut_Size = 11.1;
Nut_Hole_Diameter = 5.2;

Plug_Length = 20.4;
Plug_Diameter = 4;

e = 0.001;

BananaJack("#F00", "#888", 1.5, false);

module BananaJack(color, metal_color, case_thickness, negative = false) {
    if (negative) {
        color(color)
            translate([0, 0, Plastic_Stick_Out_Length + Metal_Stick_Out_Length - Plug_Length])
                cylinder(Plug_Length, d = Plastic_Diameter);
    } else {
        color(color) {
            difference() {
                union() {
                    cylinder(Plastic_Stick_Out_Length, d = Plastic_Stick_Out_Diameter);
                    translate([0, 0, -Plastic_Length]) {
                        cylinder(Plastic_Length, d = Plastic_Diameter);
                    }
                }
                translate([0, 0, -Plastic_Length - e / 2]) {
                    translate([0, 0, -Plastic_Stick_Out_Length])
                    cylinder(Plastic_Stick_Out_Length + Plastic_Stick_Out_Diameter + e, d = Plastic_Hole_Diameter);
                }
            }
        }

        color(metal_color) {
            translate([0, 0, Plastic_Stick_Out_Length])
                difference() {
                    union() {
                        cylinder(Metal_Stick_Out_Length, d = Metal_Stick_Out_Diameter);
                        translate([0, 0, -Metal_Length]) {
                            cylinder(Metal_Length, d = Metal_Diameter);
                        }
                    }
                    translate([0, 0, -Metal_Length - e / 2]) {
                        cylinder(Metal_Length  + Metal_Stick_Out_Length + e, d = Metal_Hole_Diameter);
                    }
                }
        }
        translate([0, 0, -case_thickness]) {
            translate([0, 0, -Plastic_Ring_Length]) {
                color(color)
                    Pipe(Plastic_Ring_Length, Plastic_Stick_Out_Diameter / 2, Plastic_Diameter / 2);
                color(metal_color) {
                    translate([0, 0, -Fin_Thickness]) {
                        difference() {
                            union() {
                                hull() {
                                    cylinder(Fin_Thickness, d = Fin_Diameter_1_Inner);
                                    translate([0, Fin_Hole_2_Offset, 0])
                                        cylinder(Fin_Thickness, d = Fin_Diameter_2);
                                }
                                cylinder(Fin_Thickness, d = Fin_Diameter_1);
                            }
                            translate([0, 0, -e / 2]) {
                                cylinder(Fin_Thickness + e, d = Fin_Hole_1_Diameter);
                                translate([0, Fin_Hole_2_Offset, 0])
                                    cylinder(Fin_Thickness + e, d = Fin_Hole_2_Diameter);
                            }
                        }
                        translate([0, 0, -Nut_Thickness]) {
                            difference() {
                                cylinder(Nut_Thickness, d = Nut_Size, $fn = 6);
                                translate([0, 0, -e / 2]) {
                                    cylinder(Nut_Thickness + e, d = Nut_Hole_Diameter);
                                }
                            }
                        }
                    }
                }
            }
        }

        color(metal_color, 0.4) {
            translate([0, 0, Plastic_Stick_Out_Length + Metal_Stick_Out_Length - Plug_Length + Plug_Diameter / 2]) {
                translate([0, 0, 0])
                    cylinder(Plug_Length - Plug_Diameter / 2 - e, d = Plug_Diameter);
                sphere(d = Plug_Diameter);
            }
        }
    }
}


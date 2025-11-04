Diameter = 4.9;
Height = 8.8;
Base_Diameter = 5.3;
Base_Height = 1.0;

Pin_Size = 0.5;
Pin_Length = [16.0, 17.5];
Pin_Distance = 2.54;

Led("#F00A", "#888");

module Led(color = "#F00", pin_color = "#888") {
    color(color) {
        cylinder(Height - Diameter / 2, d=Diameter);
        translate([0, 0, Height - Diameter / 2])
            sphere(d = Diameter);
        cylinder(Base_Height, d = Base_Diameter);
    }

    color(pin_color) {
        for (i = [0, 1]) {
            translate([Pin_Distance / 2 * (i == 0 ? -1 : 1), 0, -Pin_Length[i] / 2])
                cube([Pin_Size, Pin_Size, Pin_Length[i]], center=true);
        }
    }
}

# Desert Habitat
Software for the desert habitat IoT devices and monitoring.

![](./img/desert_habitat.png "Desert Habitat")

* [Summary](#summary)

FINISHED PHOTO HERE

## Summary
The desert habitat is a large-sized habitat housing a young bearded dragon, intended to serve as an enclosure for the duration of the dragon's long life. It contains a water feature allowing the dragon to drink from a very shallow pool or to lick the rocks for water when needed.  It contains one heat pad hidden under the substrate, two daytime heat lamps, one night time heat lamp, and two UVA/UVB lamps for the daytime.

Sensors in the habitat include temperature and humidity for the top right corner ("Basking"), and the lower left corner ("Cooling") as well as a water-level sensor.

These sensors are polled by a raspberry pi and upload data to Amazon Timestream. They are graphed by Grafana for AWS, accessible anywhere in the world with an internet connection. IFTTT provides push notifications if the sensors report abnormal values for an extended period.

## Structural Features
The physical features of the habitat are detailed below.

### Planning

The project began by first identifying a place in the house for the habitat. A suitable wall was found, far from windows so that the sun's rays wouldn't disturb the temperature regulation of the habitat, and close to where we spend time during the day, for maximal interaction. The dimentions that fit optimally were 48 inches by 44 inches.

I began drawing the enclosure, keeping several points in mind while doodling:
- The habitat needed to be cat proof.
- The floor level of the habitat needed to be high enough for a human to clean, or handle and feed the dragon.
- Storage would be ideal, for things like food and supplies.
- A ramp or stairs would be required, allowing the reptile to move about, thus regulating its body temperature.
- Water needed to be present, but not deep.
- A bearded dragon does not naturally encounter standing water, notices running water more easily, and prefers to lick rocks for moisture intake.
- Live plants would help the ambiance.
- Dragons like climbing branches, as their natural habitat is desert woodland, and they often sleep in trees.
- A cooling corner is required, with a cave or hiding place, away from the heat lamps.

Given these requirements, my designs included plans for structural elements as well as artistic choices. For instance, I settled on trying to recreate diagonal strata in the rock wall, lifting as a result of geologic activity, with flat desert rocks. I designed a natural cave, a rock cradling a shallow water pool, the placement of two plants.

![](./img/drawings.jpg "Brainstorming Drawings")

### Housing

Built from pine, due to cost, a mix of rough pine was used for the back, bottom, and generally for portions that won't be seen. Fine sanded pine was used for the main structure (the supports, the siding, the top, the drawers).  Plexiglass (clear acrylic) was used for the transparent sliding doors in front and on the side.  The top is made from an office light egg crate louver which proved _not_ to be cricket-proof (something that I wish had occurred to me much earlier) and is now therefore covered by fiberglass screen mesh.

### Interior

The interior began as styrofoam blocks both purchased from Michael's art store as well as salvaged from the garbage. These were held together with toothpicks. In retrospect, a glue should have been used to further secure them. The foam was shaped primarily by a heated foam cutter purchased from Michaels. The required features were worked in at this time, including places for two live plants, rocks for water to trickle down into a pool, a natural looking rock cave, a basking rock, and a ramp leading to the cooling corner.

![](./img/only_foam01.jpg "White styrofoam, just beginning")  ![](./img/only_foam02.jpg "White styrofoam, progressing")

The foam was then covered in a thick sanded grout mix, Charcoal Black in color. This was applied by hand, later with latex gloves (another late discovery - grout severly dries out one's skin).

![](./img/half_black.jpg "Black grout, just beginning")  ![](./img/all_black.jpg "Black grout, complete")

Once dry, the entirety of the habitat was then covered in another layer of grout, Navajo White in color.

![](./img/all_grey.jpg "Grey grout, complete")

During this process, I began purchasing items that I knew I would need, including heat lamps and substrate. The substrate is a sand from Australia that is orange and red in color. I attempted to match this color as best as I could using acrylic paints that I applied with a generous amount of water as a "wash" over the grout. I intended to keep the saturation relatively low.

![](./img/paint_ip.jpg "Paint color wash, just starting")

I mixed enough paint for about a square foot or two of the rocks at a time, and my pigment mixture varied from batch to batch, sometimes more red, sometimes more orage. I made sure to paint rocks diagonally along the back wall so that the pigment formed strata. The paint lightened as it dried, and I got a bit more aggressive with the amount of pigment that I used.

![](./img/paint_palette.jpg "Paint on palette, color choices")

To my chagrin, I was overly ambitious with the pigment, and many of my rocks were quite saturated, even after drying.  While I was dismayed, this proved to be a happy accident, as it actually looks pretty good in the end.

![](./img/color_done.jpg "Painting complete, all colored")

## Technical Features

## Technical Documentation

### Requirements

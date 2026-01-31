# 4.2 - Creating the World


## A bit of cleanup

- Rename TilemapFactory to TilemapLoader
- create an interface TilemapFactory
- Use the script to generate forest and make this a ForestTilemapFactory
- Create a TilemapTownFactory
- Reuse the TilemapForestFactory for the farm.

## Creating the World

- create world class
- create world factory
- use factory to create world with the 3 tilemaps

## Test each map by adding a temporary selection box in the GUI for each map

- notice that when we change the map the hero disappears, that's because the tilemap is being redrawn over top of the hero. So when we redraw the tilemap, we need to redraw the hero. Actually, the more robust solution is to make sure that if we need to redraw, we redraw everything.
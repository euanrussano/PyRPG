# Planning the game

Before you start coding you project, it is a good idea to plan:
- What the program have to do
- How the user interface will look

Since we are working on a very simple learning project, we don't need to get too deep into details. But still, we have to sketch a bit of a plan.

## Goals

What the program will do? In the following list I try to condense all the **minimum set of features** that I want the game to have. This makes the final version of this process a **Minimum Viable Product**, or **MVP**

### MVP
- User sees a map with a hero
- User can move the hero around the map 
  - Avoid moving over obstacles (walls, objects, etc.)
- The map might have a chest with items
  - The hero can open the chest
  - The chest gives items and/or gold to the hero
- The map might have a folk
  - The hero can talk to the folk
  - The folk can give quests to the hero
  - The hero can discuss with the folk
    - discussion spends energy
  - If hero wins the discussion, they get a loot (item/gold/xp)
- if the hero loses all energy, they return home (restore energy)
- Completing a quest requires turning in an item
- Item comes from chests or folks (discussion)
- If the hero has all the quest requirements, and it talks to the quest giver folk, the quest is completed, they receive:
  - experience points
  - gold
  - a reward item
- The location might have a trading shop with a trader
  - Player can buy/sell items
  - Player can save/load game


That set of features makes my **MVP**. Maybe you think it is too short or too long. The amount of features is up to each developer. But I think this is a good starting point for a learning project.

Now it comes the more fun part. We can think of more features to add to the game. These may not be so simple, but will surely enrich the game. Be careful not to overdo it! The more features you add, the longer it will take to write the code. You may end up with a complex program, that is hard to finish. So feet on the ground, and keep it simple.

As you will see, some of the features I placed a question mark, since I am not sure on how I will implement them. But we can decide on the details later.

## Future goals (Beta version)

- Internationalization
- Hero learns crafting skills to craft items
- Recipes to craft items
- Crafting skills? Crafting level?
- Add clothing
- Add jewelry
- Ability to enhance items
- Pets
  - Helps in discussion? crafting?
- Populate world from file(s) (data-driven design)
- RPG Maker app, to let users create their own maps/folks/items/quests/etc. without writing any code (the app creates the files or adds to the database)


## Sketching the game

With those goals in mind, is time to think on the look and feel of the game, i.e the screen. One simple way of doing that is by drawing it on paper. That is the fastest and simplest form of sketching. Or you can use a program like [Paint](https://www.paint.net/) or Canva (https://www.canva.com/), which is my case. So I made a simple sketch, as you can see below.

![Sketch of the game](img/02_01_sketch.png)

The upper left side shows some information about the hero. The middle upper side shows the game world. The lower left side shows the inventory, and the lower right side shows the controls. The upper right side shows some messages, so we can see if something happened (also helps when testing the game and finding bugs).


## The game world

We don't want to overcomplicate our first version so we will keep it simple and create a small world, with just few locations

![Game world](img/02_01_world.png)

There are only 3 locations in this world. We start in the (abandoned) farm, where we can find lost chests to get random items. From there we can go to the town to talk with folks and get quests. In the town we can also go to the trading shop to buy and sell items. Then we can move to the forest, to find more chests and some grumbling folks to discuss and win some experience and more items.

With this world, we are able to test all the features we want to add to the **Minimum Viable Product** version of the game.

With that basic planning in place, we can start coding!


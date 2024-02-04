purpy
=====

## Installation
* `pip3 install pygame`
* `pip3 install pyopengl`
* `pip3 install numpy`

## Running
* `python3 main.py`

## TODO
* Implement saving which stars you have.
* Implement better menus.
* Improve controls.

## Making Levels

Maps are edited using [Tiled](https://www.mapeditor.org/). In general, maps can be any size. The expected size of the screen is **`80x44` tiles**. Each tile should be **`8x8` pixels**.

Several different layer types are supported. `Background` and `Tile` layers are rendered bottom-to-top. `Object` layers are handled using separate logic.

*Map Properties*
* `bool dark` - If this is set to `true`, then the level will be dark, except where the player and stars are.
* `int gravity` - Custom gravity, in 1/32 pixels. Defaults to 64.

## Tile Layers

`Tile` layers are for grids of blocks. If there's more than one tile layer, one of them must be marked as the `player` layer. That is the layer where the player is rendered, and is the only layer the player can interact with directly.

*Properties*
* `bool player` - The tile layer marked with this property is the layer where the player interacts.

### Tile Properties

Each tile in a tile layer can have certain properities that affect its rendering and behavior.

*Properties*
* `bool solid` - If this is present and set to `false`, then the player can pass through the tile from any direction. Defaults to `true`.
* `int hitbox_top, hitbox_left, hitbox_right, hitbox_bottom` - How much to offset the hitbox for this tile from each side in pixels. Defaults to `0`.


### Animated Tiles

Tiles in a tileset (`.tsx` file) can be overridden with animated versions of some tiles. This is done by setting a path to a directory containing the animations. Each file in the directory should be a `.png` named with the tile id to replace. For example, `123.png` would replace the rendering for tile id `123`. The `.png` should have a single row of `8x8` images, with no padding.

*Properties*
* `string animations` - The path to the directory with the animations, relative to the `.tsx` file.

### Spikes

Spike blocks are blocks that kill the player when the player touches them from above.

*Properties*
* `bool deadly` - If this is present and set to `true`, then the block will be treated as a spike.

### One-way Walls

One-way walls are blocks that can be traversed from all but one direction.

*Properties*
* `string oneway` - If present and set to `'N'`, `'S'`, `'E'`, or `'W'`, will not allow the player to pass through the block in the opposite direction. For example, if the block is set to `N`, then the player cannot fall down through the block.

### Switch Blocks

Switch blocks are buttons that change other blocks when the player lands on them from above. Switched values are a set of strings that starts as empty.

*Properties*
* `string switch` - If this is set, then it is a string for the value that is added to the set. For example, this could be `"red"` to add the string `"red"` to the set of current switch values. The string can be prefixed with `~` or `!` to toggle or remove the value, respectively. For example, a switch with `"~red"` will toggle `"red"` every time it's pressed. A switch with `"!red"` will turn off `"red"`.
* `string condition` - If this is set, then the block will only be present if the value set is switched on. For example, if the `condition` is `"red"`, then the block will only be on if the `"red"` value is switched on. If the condition is prefixed with `!`, then the block is only on if the value is switched off.
* `int alternate` - If this is set, then it specified a tile id to replace this tile with when this tile is switched off.

## Object Layers

`Object` layers are used to add objects that don't neatly fit into the tile grid.

### Custom Spawn Points

A point can be added with properties to define where and how the player spawns. Only one spawn point should be added to a map.

*Properties*
* `bool spawn` - If true, this point is the spawn point.
* `bool facing_left` - If true, start the player facing left. Otherwise, the player will start facing right.
* `int dx` - The initial x velocity of the player, in pixels. Defaults to 0.
* `int dy` - The initial y velocity of the player, in pixels. Defaults to 0. Negative values mean up.

### Warp Zones

A rectangle that causes the player to be sent to another level, like a door.

*Properties*
* `string warp` - If present, this is the path of the map the player will be sent to. Similar to door's destination.

### Preferred Viewports

A rectangle can be added with properties that take effect when the player is in that area. For example, you can lock the camera to a certain location.

*Properties*
* `int preferred_x` - The x value of the map to use as the left side of the screen.
* `int preferred_y` - The y value of the map to use as the top of the screen.

### Platforms

Platforms are special tiles that can move. If the player is standing on a platform, they will be moved with it.

If the platform is `solid`, it can also push the player in other directions. The player will die if a `solid` platform pushes them into an impossible position, where they are crushed.

If the platform is _not_ `solid`, then the player can pass through it from the bottom or sides. If a player would be crushed by a non-solid platform moving up, then the player will fall through it.

*Properties*
* `bool platform` - If present and true, then this object will be a platform.
* `string direction` - The direction the platform should move from its starting point. Can be `'N'`, `'S'`, `'E'`, or `'W'`.
* `int distance` - The distance in blocks to move, before turning around and going back to the start.
* `int speed` - The speed of the movement, in 1/16 subpixels per frame. Defaults to `4`. Values above `16` may have odd behavior.
* `bool solid` - Whether the platform is `solid`, as described above. Defaults to `false`.
* `string condition` - Similar to the conditions for switched blocks. If the condition is set and turned off, then the platform will return to where it started and stop.
* `string overflow` - What to do when the platform reaches the end. Options are:
  * `"oscillate"` - Go back and forth.
  * `"clamp"` - Go to the end and stop.
  * `"wrap"` - Go to the end and then snap back to the beginning.

### Bagels

A platform that wiggles when you stand on it, and then falls after a short time. Does not obey other platform properties.

*Properties*
* `bool bagel` - If set to `true`, this object will be a bagel.

### Conveyor Belts

A platform that doesn't move itself, but does move the player when the player is standing on it.

*Properties*
* `string convey` - If set, makes this object into a conveyor belt. Can be `'E'` or `'W'`, which sets the direction the belt moves.
* `int speed` - The speed that the belt will move the player. Defaults to `24`.
* `bool solid` - Works the same as solid on other platforms.

### Buttons

Like a switch, but more flexible, and more aesthetic.

*Properties*
* `bool button` - If set, makes this object a button.
* `string color` - The color to toggle when the button is on.
* `string button_type` - The behavior of the button. Can be one of:
  * `"toggle"` - Switches between on and off when pressed.
  * `"momentary"` - Is on only while being pressed.
  * `"oneshot"` - Can only be turned on once.
  * `"smart"` - The `color` is treated as a condition and a command. The button is considered "on" if the condition is true. When the button is toggled on, the command is run. This is good for setting `color` values like`"red"` and `"!red"` as separate buttons.
* `bool solid` - Works the same as solid on other platforms.

### Stars

Stars are little doodads you can collect. They vibrate a little and light up.

*Properties*
* `bool star` - If set to true, this object will be a star.

### Doors

Doors let the player travel to other levels. A door object only specifies the upper left corner of the door. The door will always be a `32x32` pixel square.

*Properties*
* `bool door` - If set to true, this object will be a door.
* `int stars_needed` - If this is set to a non-zero value, then the door will be locked until the player collects this many stars on this level. Defaults to `0`.
* `string destination` - A path to the level to load when the player enters the door.

#### Background Layers

`Background` layers are images that are rendered behind all the tile layers.


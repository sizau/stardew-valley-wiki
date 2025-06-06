using Microsoft.Xna.Framework;
using StardewValley;

namespace WikiIngameTools.Framework;

internal static class Utilities
{
    public static Vector2 GetTile()
    {
        var tileX = (Game1.getMouseX() + Game1.viewport.X) / 64;
        var tileY = (Game1.getMouseY() + Game1.viewport.Y) / 64;

        return new Vector2(tileX, tileY);
    }
}

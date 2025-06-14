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
    
    public static void Reload(this IModule module)
    {
        var configStatus = module.Config.Enable;
        if (configStatus == module.IsActive) return;
        
        switch (configValue: configStatus, module.IsActive)
        {
            case (true, false):
                module.Activate();
                break;
            case (false, true):
                module.Deactivate();
                break;
        }
    }
}

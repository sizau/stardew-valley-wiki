using System.Collections.Generic;
using Microsoft.Xna.Framework;
using StardewValley;

namespace WikiIngameTools.Framework;

internal static class Utilities
{
    /// <summary>
    /// 获取当前鼠标指针下的地块坐标。
    /// </summary>
    /// <returns>当前鼠标指针下的地块坐标</returns>
    public static Vector2 GetTile()
    {
        var tileX = (Game1.getMouseX() + Game1.viewport.X) / 64;
        var tileY = (Game1.getMouseY() + Game1.viewport.Y) / 64;

        return new Vector2(tileX, tileY);
    }

    /// <summary>
    /// 重新载入模块配置
    /// </summary>
    /// <param name="module">需要重新载入配置的模块</param>
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

    /// <summary>
    /// 将字符串列表转化为字符串，可自定义分隔符。
    /// </summary>
    /// <param name="str">字符串列表</param>
    /// <param name="separator">分隔符</param>
    /// <returns></returns>
    public static string Tostring(this List<string> str, char separator=',')
    {
        return str == null || str.Count == 0 ? "" : string.Join(separator, str);
    }
}
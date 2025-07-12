import datetime
import os
from typing import override, Self

from PIL import Image, ImageDraw
from PIL.Image import Resampling


class Vector2:
    def __init__(self, x, y) -> None:
        self.x: int = x
        self.y: int = y

    @override
    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, Vector2):
            raise TypeError("not a Vector2!")
        return self.x == other.x and self.y == other.y

    def __mul__(self, other: int) -> Self:
        return Vector2(self.x * other, self.y * other)

    def __add__(self, other: int | Self) -> Self:
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        if isinstance(other, int):
            return Vector2(self.x + other, self.y + other)
        raise TypeError("not a supported type!")

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    @staticmethod
    def align(p1, p2) -> None:
        """
        调整两个 Vector2 的坐标，使得 p1 位于 p2 的左上方
        """
        if not (isinstance(p1, Vector2) and isinstance(p2, Vector2)):
            raise TypeError("not Vector2!")
        if p1.x > p2.x:
            p1.x, p2.x = p2.x, p1.x
        if p1.y > p2.y:
            p1.y, p2.y = p2.y, p1.y

    @staticmethod
    def parse(string: str, separator: str = ","):
        """
        将字符串解析为 Vector2 实例
        :param string: 需要解析的字符串
        :param separator: 坐标之间的分隔符，默认为 “,”
        :return: 解析得到的 Vector2
        """
        point = string.split(separator)
        if len(point) != 2:
            raise ValueError("cannot parse string!")
        return Vector2(int(point[0]), int(point[1]))


class PictureProcessor:
    def __init__(self, clearInputDir=False):
        self.pictures: list[str] = os.listdir("pics")
        self.output_dir = "output/" + datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        self.clear_input = clearInputDir
        os.makedirs(self.output_dir, exist_ok=True)

    def resize_pic(self, scale: float = 3.0, cover=False) -> None:
        """
        遍历 pic 文件夹内的所有图片，使用硬边缘缩放图片尺寸，使像素图片更适合用于显示，默认缩放比例为 3.0
        :param scale: 缩放比例
        :param cover: 是否覆盖原图片，若为 True 则会直接在原图上操作，否则输出至 output文件夹
        """
        for pic in self.pictures:
            image: Image = Image.open(f"pics/{pic}")
            original_size = image.size
            new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
            resized_image = image.resize(new_size, Resampling.NEAREST)
            if cover:
                resized_image.save(f"pics/{pic}")
                return
            self._save(resized_image, pic)

    def divide_pic(self, cutRange: tuple[int, int, int, int], cover=False) -> None:
        """
        遍历 pic 文件夹内的所有图片，裁剪出指定范围内的像素
        :param cutRange: 裁剪范围，格式为：[左上角 x, 左上角 y, 右下角 x, 右下角 y]
        :param cover: 是否覆盖原图片，若为 True 则会直接在原图上操作，否则输出至 output文件夹
        """
        for pic in self.pictures:
            image: Image = Image.open(f"pics/{pic}")
            roi = image.crop(cutRange)
            if cover:
                roi.save(f"pics/{pic}")
                return
            self._save(roi, pic)

    def divide_by_width(self, region_width: int) -> None:
        """
        按指定宽度从左至右依次裁剪图片为多个区域
        :param region_width: 每个区域的宽度（像素）
        """
        for pic in self.pictures:
            image: Image = Image.open(f"pics/{pic}")
            img_width, img_height = image.size
            count = 1
            for left in range(0, img_width, region_width):
                right = min(left + region_width, img_width)
                box = (left, 0, right, img_height)
                region = image.crop(box)
                # 输出到 output 文件夹，文件名加序号
                name, ext = os.path.splitext(pic)
                region_filename = f"{name} {count}{ext}"
                self._save(region, region_filename)
                count += 1

    def add_mask(self, region_lists: list[str], color, tile_width: int = 16, cover=False) -> None:
        """
        获取 pic 文件夹内的第一张图片，在其之上绘制图片遮罩
        :param region_lists: 遮罩的范围，格式为：["int,int;int,int", ...]
        :param color: 遮罩的 RGBA
        :param tile_width: 图块宽度，默认为 16
        :param cover: 是否覆盖原图片，若为 True 则会直接在原图上操作，否则输出至 output文件夹
        """
        regions: list[tuple[Vector2, Vector2]] = []
        for region in region_lists:
            # 先进行预处理，使用分号分隔前后两个坐标值，然后解析两个坐标
            point2 = region.split(";")
            point0 = Vector2.parse(point2[0])
            point1 = Vector2.parse(point2[1])
            # 使用 align 方法确保 point0 位于 point 1 的左上方
            Vector2.align(point0, point1)
            # 将地块坐标转化为像素坐标
            point0 = point0 * tile_width
            point1 = (point1 + 1) * tile_width
            regions.append((point0, point1))
        # 只读取一张图片进行操作
        pic = self.pictures[0]
        image = Image.open(f"pics/{pic}").convert("RGBA")
        # 新建一个透明图层
        mask_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(mask_layer)
        # 将范围遮罩绘制在透明图层上
        for region in regions:
            region = (region[0].x, region[0].y, region[1].x, region[1].y)
            draw.rectangle(region, fill=color)
        # 混合原图与遮罩图层
        image = Image.alpha_composite(image, mask_layer)
        if cover:
            image.save(f"pics/{pic}")
            return
        self._save(image, pic)

    def _save(self, image: Image, filename: str) -> None:
        """
        将图片保存至输出文件夹下
        :param image: 需要保存的图片
        :param filename: 保存的文件名
        """
        image.save(f"{self.output_dir}/{filename}", format="PNG")

    def clear(self) -> None:
        """
        清除空的导出文件夹和 pic 文件夹
        """
        # 如果 clear_input 为 True，删除 pics 文件夹下的所有图片
        if self.clear_input:
            for pic in self.pictures:
                os.remove(f"pics/{pic}")
        # 删除当前实例创建的空的导出文件夹
        if os.path.isdir(self.output_dir) and not os.listdir(self.output_dir):
            os.rmdir(self.output_dir)


if __name__ == "__main__":
    # 默认运行完成后不清除原始文件，如需调整，改为 True
    processor = PictureProcessor(clearInputDir=False)
    try:
        # 按需调用
        ...
    except Exception as error:
        print(error)
        raise
    finally:
        if 'error' not in locals():
            processor.clear()

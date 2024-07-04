import os
from PIL import ImageFilter
from typing import List, Union
from ..utils.convert import convert
from ..utils.directory import initialize_directory


class Luts:
    luts_directory = initialize_directory('luts')
    
    @classmethod
    def INPUT_TYPES(self):
        luts = [lut.split(".")[0] for lut in os.listdir(self.luts_directory) if lut.endswith(".cube")]

        return {
            "required": {
                "image": ("IMAGE",),
                "lut": (luts, {"default": 'Cinematic'}),
            },
        }

    CATEGORY = "Shibiko"

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    FUNCTION = "__call__"

    def apply_lut(self, image, lut):
        print("Applying LUT...")
        if not lut.endswith(".cube"):
            lut += ".cube"
        lut_file_name = lut
        lut_directory = initialize_directory('luts')
        lut_path = os.path.join(lut_directory, f"{lut_file_name}")
        lut = self.read_lut(lut_path)

        if isinstance(image, list):
            image = [img.filter(lut) for img in image]
        else:
            image = image.filter(lut)

        return image

    def read_lut(self, path_lut: Union[str, os.PathLike], num_channels: int = 3):
        """Read LUT from raw file. Assumes each line in a file is part of the lut table"""
        with open(path_lut) as f:
            lut_raw = f.read().splitlines()

        size = round(len(lut_raw) ** (1 / 3))
        lut_table = [
            self.row2val(row.split(" ")) for row in lut_raw if self.is_3dlut_row(row.split(" "))
        ]

        return ImageFilter.Color3DLUT(size, lut_table, num_channels)

    @staticmethod
    def is_3dlut_row(row: List) -> bool:
        """Check if one line in the file has exactly 3 values"""
        row_values = []
        for val in row:
            try:
                row_values.append(float(val))
            except:
                return False
        if len(row_values) == 3:
            return True
        return False

    @staticmethod
    def row2val(row):
        return tuple([float(val) for val in row])

    def __call__(self, image, lut, unique_id):
        image = convert(image)
        image = self.apply_lut(image, lut)
        image = convert(image)

        return (image,)


NODE_CLASS_MAPPINGS = {"Luts": Luts}
NODE_DISPLAY_NAME_MAPPINGS = {"Luts": "Shibiko AI - Luts"}

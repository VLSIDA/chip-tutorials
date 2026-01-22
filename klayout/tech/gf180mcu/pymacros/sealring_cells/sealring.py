# Copyright 2025 Leo Moser
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .draw_sealring import *

default_width = 100
default_height = 100

minimum_width = 3 * sealring_edge_width
minimum_height = 3 * sealring_edge_width


class sealring(pya.PCellDeclarationHelper):
    """
    Seal ring generator for GF180MCU
    """

    def __init__(self):

        # Initialize parent cell
        super(sealring, self).__init__()

        self.metal_handle = self.param(
            "metal_level", self.TypeList, "Metal level", default="Metal5"
        )
        self.metal_handle.add_choice("Metal3", "Metal3")
        self.metal_handle.add_choice("Metal4", "Metal4")
        self.metal_handle.add_choice("Metal5", "Metal5")
        self.metal_handle.add_choice("MetalTop", "MetalTop")

        self.type_handle = self.param(
            "sealring_type",
            self.TypeList,
            "Packaging type",
            default="bonding",
            tooltip="For flip-chip packaging, the sealring needs to be protected from chemical attack during solder bumping process with passivation.",
        )
        self.type_handle.add_choice("bonding", "bonding")
        self.type_handle.add_choice("flip-chip", "flip-chip")

        self.param("w", self.TypeDouble, "Width", default=default_width, unit="um")
        self.param("h", self.TypeDouble, "Height", default=default_height, unit="um")
        self.param("area", self.TypeDouble, "Area", readonly=True, unit="um²")
        self.param("perim", self.TypeDouble, "Perimeter", readonly=True, unit="um")

    def display_text_impl(self):
        # Description of the cell
        return "sealring(W=" + ("%.3f" % self.w) + ",H=" + ("%.3f" % self.h) + ")"

    def coerce_parameters_impl(self):
        # Limit length and width
        self.w = max(minimum_width, self.w)
        self.h = max(minimum_height, self.h)

        # Calculate area and perimeter
        self.area = self.w * self.h
        self.perim = 2 * (self.w + self.h)

    def can_create_from_shape_impl(self):
        # Any shape with a bounding box
        return self.shape.is_box() or self.shape.is_polygon() or self.shape.is_path()

    def parameters_from_shape_impl(self):
        # Get width and height
        self.w = self.shape.dbbox().width()
        self.h = self.shape.dbbox().height()

    def transformation_from_shape_impl(self):
        # Get the bottom left corner
        return pya.DTrans(self.shape.dbbox().left, self.shape.dbbox().bottom)

    def produce_impl(self):
        # Draw the sealring
        sealring_instance = draw_sealring(
            self.layout, self.w, self.h, self.metal_level, self.sealring_type
        )

        self.cell.insert(
            pya.CellInstArray(
                sealring_instance.cell_index(),
                pya.Trans(pya.Point(0, 0)),
            )
        )

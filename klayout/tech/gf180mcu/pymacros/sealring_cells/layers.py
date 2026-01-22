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

import pya


class Layers:

    def by_name(name):
        return Layers.__dict__[name]

    COMP = pya.LayerInfo(22, 0)
    Pplus = pya.LayerInfo(31, 0)
    Nplus = pya.LayerInfo(32, 0)
    DNWELL = pya.LayerInfo(12, 0)
    Nwell = pya.LayerInfo(21, 0)
    LVPWELL = pya.LayerInfo(204, 0)
    Dualgate = pya.LayerInfo(55, 0)
    Poly2 = pya.LayerInfo(30, 0)
    Nplus = pya.LayerInfo(32, 0)
    Pplus = pya.LayerInfo(31, 0)
    SAB = pya.LayerInfo(49, 0)
    ESD = pya.LayerInfo(24, 0)

    Metal1 = pya.LayerInfo(34, 0)
    Metal2 = pya.LayerInfo(36, 0)
    Metal3 = pya.LayerInfo(42, 0)
    Metal4 = pya.LayerInfo(46, 0)
    Metal5 = pya.LayerInfo(81, 0)
    MetalTop = pya.LayerInfo(53, 0)

    Contact = pya.LayerInfo(33, 0)
    Via1 = pya.LayerInfo(35, 0)
    Via2 = pya.LayerInfo(38, 0)
    Via3 = pya.LayerInfo(40, 0)
    Via4 = pya.LayerInfo(41, 0)
    Via5 = pya.LayerInfo(82, 0)

    PR_bndry = pya.LayerInfo(0, 0)

    GUARD_RING_MK = pya.LayerInfo(167, 5)

    Pad = pya.LayerInfo(37, 0)

require 'etc'

# No stdout buffering
$stdout.sync = true

puts "Reading layout…"

$ly = RBA::Layout::new()
$ly.read($input)

$micron2dbu = RBA::CplxTrans::new($ly.dbu).inverted

$top_cell = $ly.top_cell

# Layers

COMP   = $ly.layer(22, 0)
Poly2  = $ly.layer(30, 0)
Metal1 = $ly.layer(34, 0)
Metal2 = $ly.layer(36, 0)
Metal3 = $ly.layer(42, 0)
Metal4 = $ly.layer(46, 0)
Metal5 = $ly.layer(81, 0)

RES_MK = $ly.layer(110, 5)
IND_MK = $ly.layer(151, 5)

Nwell    = $ly.layer(21, 0)
DNWELL   = $ly.layer(12, 0)
LVPWELL  = $ly.layer(204, 0)
Dualgate = $ly.layer(55, 0)

Pad = $ly.layer(37, 0)

COMP_Dummy   = $ly.layer(22, 4)
Poly2_Dummy  = $ly.layer(30, 4)
Metal1_Dummy = $ly.layer(34, 4)
Metal2_Dummy = $ly.layer(36, 4)
Metal3_Dummy = $ly.layer(42, 4)
Metal4_Dummy = $ly.layer(46, 4)
Metal5_Dummy = $ly.layer(81, 4)

FuseTop       = $ly.layer(75, 0)
POLYFUSE      = $ly.layer(220, 0)
FUSEWINDOW_D  = $ly.layer(96, 1)
PMNDMY        = $ly.layer(152, 5)
MTPMK         = $ly.layer(122, 5)
OTP_MK        = $ly.layer(173, 5)
NDMY          = $ly.layer(111, 5)

# chip's bbox (boundary to fill)
$chip = $ly.top_cell().dbbox()

# threads
if not $threads
  $threads ||= Etc.nprocessors
end

$fill_cell_comp =	 $ly.create_cell("COMP_FILL")
$fill_cell_poly2 =	 $ly.create_cell("POLY2_FILL")
$fill_cell_metal1 =	 $ly.create_cell("METAL1_FILL")
$fill_cell_metal2 =	 $ly.create_cell("METAL2_FILL")
$fill_cell_metal3 =	 $ly.create_cell("METAL3_FILL")
$fill_cell_metal4 =	 $ly.create_cell("METAL4_FILL")
$fill_cell_metal5 =	 $ly.create_cell("METAL5_FILL")

# Insert fill cells into top level
$ly.start_changes()
$top_cell.insert(RBA::CellInstArray::new($fill_cell_comp, RBA::Trans::new(0,0)))
$top_cell.insert(RBA::CellInstArray::new($fill_cell_poly2, RBA::Trans::new(0,0)))
$top_cell.insert(RBA::CellInstArray::new($fill_cell_metal1, RBA::Trans::new(0,0)))
$top_cell.insert(RBA::CellInstArray::new($fill_cell_metal2, RBA::Trans::new(0,0)))
$top_cell.insert(RBA::CellInstArray::new($fill_cell_metal3, RBA::Trans::new(0,0)))
$top_cell.insert(RBA::CellInstArray::new($fill_cell_metal4, RBA::Trans::new(0,0)))
$top_cell.insert(RBA::CellInstArray::new($fill_cell_metal5, RBA::Trans::new(0,0)))
$ly.end_changes()

# This is an object which will receive the regions to tile
# It is driven single-threaded which is good since the tiling function
# isn't multi-threading safe
class TilingOperator < RBA::TileOutputReceiver
  def initialize(ly, fill_cell, *fill_args)
    @ly = ly
    @fill_cell = fill_cell
    @fill_args = fill_args
  end
  def put(ix, iy, tile, obj, dbu, clip)
    # This is the core function. It creates the fill.
    # For details see https://www.klayout.de/doc-qt4/code/class_Cell.html#k_63
    @fill_cell.fill_region(obj, *@fill_args)
  end
end

# I know, this is not the cleanest way to include scripts...

puts "Starting COMP fill…"
require_relative 'fill_comp.rb'

puts "Starting Poly2 fill…"
require_relative 'fill_poly2.rb'

puts "Starting Metal fill…"
require_relative 'fill_metal.rb'

puts "Done!"

$ly.write($output)

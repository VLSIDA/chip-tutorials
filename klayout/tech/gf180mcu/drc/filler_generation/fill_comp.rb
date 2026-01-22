# tile size in micron
tile_size = 400

# origin of the fill pattern
# For "enhanced fill use":
#   fc_origin = nil
fc_origin = RBA::DPoint::new(0.0, 0.0)

# creates a fill cell (DCF.1c 5x5 for COMP)
fc_box = RBA::DBox::new(-2.5, -2.5, 2.5, 2.5)

# define the fill cell's content
fill_shape = RBA::DBox::new(-2.5, -2.5, 2.5, 2.5)

# ----------------------------
# implementation

fill_layer = COMP_Dummy
fc_name = "COMP_fill_cell"

fill_cell = $ly.cell(fc_name)
if ! fill_cell
  fill_cell = $ly.create_cell(fc_name)
  fill_shape_in_dbu = $micron2dbu * fill_shape
  fill_cell.shapes(fill_layer).insert(fill_shape_in_dbu)
end

fc_box_in_dbu = $micron2dbu * fc_box
fc_origin_in_dbu = $micron2dbu * fc_origin

# DCF.2a
line_space = 3

# DCF.3
row_step = RBA::DVector::new(5 + line_space, 1.6)
column_step = RBA::DVector::new(1.6, 5 + line_space)

row_step_in_dbu    = $micron2dbu * row_step
column_step_in_dbu = $micron2dbu * column_step

# prepare a tiling processor to compute the parts to put into the tiling algorithm
# this can be tiled
tp = RBA::TilingProcessor::new
tp.frame = $chip
tp.dbu = $ly.dbu
tp.threads = $threads
tp.tile_size(tile_size, tile_size)
# Find optimal value?
tp.tile_border(30, 30)

tp.input("COMP", $ly, $top_cell.cell_index, COMP)
tp.input("Poly2", $ly, $top_cell.cell_index, Poly2)
tp.input("NDMY", $ly, $top_cell.cell_index, NDMY)

tp.input("Nwell", $ly, $top_cell.cell_index, Nwell)
tp.input("DNWELL", $ly, $top_cell.cell_index, DNWELL)
tp.input("LVPWELL", $ly, $top_cell.cell_index, LVPWELL)
tp.input("Dualgate", $ly, $top_cell.cell_index, Dualgate)

tp.input("RES_MK", $ly, $top_cell.cell_index, RES_MK)
tp.input("Pad", $ly, $top_cell.cell_index, Pad)
tp.input("IND_MK", $ly, $top_cell.cell_index, IND_MK)

tp.var("line_space", line_space / $ly.dbu)

# DPF.1
# Make sure to exclude some space at the tile border
# to ensure there will be no dummy poly2 without a
# dummy comp
tp.var("Poly2_extension", 0.3 / $ly.dbu)

# DCF.4
tp.var("space_to_COMP", 3.5 / $ly.dbu)
# DCF.5
tp.var("space_to_Poly2", 1.5 / $ly.dbu)

# DCF.6abcd
tp.var("space_to_Nwell", 1.3 / $ly.dbu)
tp.var("space_to_DNWELL", 4 / $ly.dbu)
tp.var("space_to_LVPWELL", 1.3 / $ly.dbu)
tp.var("space_to_Dualgate", 1.3 / $ly.dbu)

# DCF.7a
tp.var("space_to_scribe_line", 26 / $ly.dbu)

# DCF.8a
tp.var("space_to_RES_MK", 3.5 / $ly.dbu)

# DCF.9
tp.var("space_to_Pad", 7 / $ly.dbu)

# DCF.11a
tp.var("space_to_NDMY", 3.5 / $ly.dbu)

# DCF.12
tp.var("space_to_IND_MK", 3.0 / $ly.dbu)

tp.var("um1", 1 / $ly.dbu)
tp.var("um2", 2 / $ly.dbu)
tp.var("um20", 20 / $ly.dbu)
tp.var("um10", 10 / $ly.dbu)

tp.output("to_fill", TilingOperator::new($ly, $fill_cell_comp, fill_cell.cell_index, fc_box_in_dbu, row_step_in_dbu, column_step_in_dbu, fc_origin_in_dbu))

# perform the computations inside the tiling processor through "expression" syntax
# (see https://www.klayout.de/doc-qt4/about/expressions.html)
tp.queue("

# DCF.1a - use octagon_limit for sizing, do multiple steps for better performance
var COMP_20um_spacing = COMP.sized(um10, 0, mode=2).sized(0, um10, mode=2).sized(-um10, 0, mode=2).sized(0, -um10, mode=2);

# DCF.6abcd
var Nwell_ring    = Nwell.sized(space_to_Nwell)       - Nwell.sized(-space_to_Nwell);
var DNWELL_ring   = DNWELL.sized(space_to_DNWELL)     - DNWELL.sized(-space_to_DNWELL);
var LVPWELL_ring  = LVPWELL.sized(space_to_LVPWELL)   - LVPWELL.sized(-space_to_LVPWELL);
var Dualgate_ring = Dualgate.sized(space_to_Dualgate) - Dualgate.sized(-space_to_Dualgate);

# DCF.7a
# We expect the scribe line to be direct$ly outside of the die
var scribe_line_ring = _frame - _frame.sized(-space_to_scribe_line);

var fill_region = _tile & _frame
                  - _tile.not(_tile.sized(-Poly2_extension))
                  - COMP_20um_spacing.sized(space_to_COMP)
                  - Poly2.sized(space_to_Poly2)
                  - Nwell_ring
                  - DNWELL_ring
                  - LVPWELL_ring
                  - Dualgate_ring
                  - scribe_line_ring
                  - RES_MK.sized(space_to_RES_MK)
                  - Pad.sized(space_to_Pad)
                  - IND_MK.sized(space_to_IND_MK)
                  - NDMY.sized(space_to_NDMY);

_output(to_fill, fill_region)")

begin
  $ly.start_changes   # makes the layout handle many changes more efficiently
  tp.execute("Tiled fill")
ensure
  $ly.end_changes
end

# tile size in micron
tile_size = 500.0

# origin of the fill pattern
# For "enhanced fill use":
#   fc_origin = nil
#fc_origin = RBA::DPoint::new(0.0, 0.0)

# creates a fill cell with a shape on 
# DM.1
fc_box = RBA::DBox::new(-1.0, -1.0, 1.0, 1.0)

# define the fill cell's content
fill_shape = RBA::DBox::new(-1.0, -1.0, 1.0, 1.0)

# ----------------------------
# implementation

do_layers = ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5"]

metal_layers = {
  "Metal1" => Metal1,
  "Metal2" => Metal2,
  "Metal3" => Metal3,
  "Metal4" => Metal4,
  "Metal5" => Metal5
}

fill_layers = {
  "Metal1" => Metal1_Dummy,
  "Metal2" => Metal2_Dummy,
  "Metal3" => Metal3_Dummy,
  "Metal4" => Metal4_Dummy,
  "Metal5" => Metal5_Dummy
}

fc_names = {
  "Metal1" => "Metal1_fill_cell",
  "Metal2" => "Metal2_fill_cell",
  "Metal3" => "Metal3_fill_cell",
  "Metal4" => "Metal4_fill_cell",
  "Metal5" => "Metal5_fill_cell"
}

fill_cells = {
  "Metal1" => $fill_cell_metal1,
  "Metal2" => $fill_cell_metal2,
  "Metal3" => $fill_cell_metal3,
  "Metal4" => $fill_cell_metal4,
  "Metal5" => $fill_cell_metal5,
}

# DM.2a, DM.2c
line_spaces = {
  "Metal1" => 1.2,
  "Metal2" => 1.2,
  "Metal3" => 1.2,
  "Metal4" => 1.2,
  "Metal5" => 2
}

# DM.5_DM.7
previous_metals = {
  "Metal1" => Poly2,
  "Metal2" => Metal1,
  "Metal3" => Metal2,
  "Metal4" => Metal3,
  "Metal5" => Metal4
}

Empty_Layer = $ly.insert_layer(RBA::LayerInfo::new())

# DM.4_DM.6
subsequent_metals = {
  "Metal1" => Metal2,
  "Metal2" => Metal3,
  "Metal3" => Metal4,
  "Metal4" => Metal5,
  "Metal5" => Empty_Layer
}

# Insert dummy metal fill as active metal
# Ignore DM.5_DM.7 and DM.4_DM.6
metals_ignore_active = {
  "Metal1" => $Metal1_ignore_active,
  "Metal2" => $Metal2_ignore_active,
  "Metal3" => $Metal3_ignore_active,
  "Metal4" => $Metal4_ignore_active,
  "Metal5" => $Metal5_ignore_active
}

# DM.9
fc_origins = {
  "Metal1" => RBA::DPoint::new(0.0, 0.0),
  "Metal2" => RBA::DPoint::new(0.5, 0.5),
  "Metal3" => RBA::DPoint::new(1.0, 1.0),
  "Metal4" => RBA::DPoint::new(1.5, 1.5),
  "Metal5" => RBA::DPoint::new(2.0, 2.0)
}

for metal in do_layers

  fill_layer = fill_layers[metal]
  fc_name = fc_names[metal]

  fill_cell = $ly.cell(fc_name)
  if ! fill_cell
    fill_cell = $ly.create_cell(fc_name)
    fill_shape_in_dbu = $micron2dbu * fill_shape
    fill_cell.shapes(fill_layer).insert(fill_shape_in_dbu)
  end

  fc_box_in_dbu = $micron2dbu * fc_box
  fc_origin_in_dbu = $micron2dbu * fc_origins[metal]

  # DM.10
  row_step = RBA::DVector::new(2 + line_spaces[metal], 0.5)
  column_step = RBA::DVector::new(0.5, 2 + line_spaces[metal])

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
  
  tp.input("Metal", $ly, $top_cell.cell_index, metal_layers[metal])
  tp.input("subsequent_metal", $ly, $top_cell.cell_index, subsequent_metals[metal])
  tp.input("previous_metal", $ly, $top_cell.cell_index, previous_metals[metal])
  tp.input("FuseTop", $ly, $top_cell.cell_index, FuseTop)
  tp.input("POLYFUSE", $ly, $top_cell.cell_index, POLYFUSE)
  tp.input("FUSEWINDOW_D", $ly, $top_cell.cell_index, FUSEWINDOW_D)
  tp.input("PMNDMY", $ly, $top_cell.cell_index, PMNDMY)
  tp.input("MTPMK", $ly, $top_cell.cell_index, MTPMK)
  tp.input("OTP_MK", $ly, $top_cell.cell_index, OTP_MK)

  tp.input("Poly2", $ly, $top_cell.cell_index, Poly2)
  tp.input("Metal1", $ly, $top_cell.cell_index, Metal1)
  tp.input("Metal2", $ly, $top_cell.cell_index, Metal2)
  tp.input("Metal3", $ly, $top_cell.cell_index, Metal3)
  tp.input("Metal4", $ly, $top_cell.cell_index, Metal4)
  tp.input("Metal5", $ly, $top_cell.cell_index, Metal5)

  # DM.3
  tp.var("space_to_Metal", 2.0 / $ly.dbu)
  
  # DM.4_DM.6
  tp.var("space_to_subsequent_Metal", 2.0 / $ly.dbu)
  
  # DM.5_DM.7
  tp.var("space_to_previous_Metal", 2.0 / $ly.dbu)
  
  # DM.8
  tp.var("space_to_FuseTop",      6.0 / $ly.dbu)
  tp.var("space_to_POLYFUSE",     6.0 / $ly.dbu)
  tp.var("space_to_FUSEWINDOW_D", 6.0 / $ly.dbu)
  tp.var("space_to_PMNDMY",       6.0 / $ly.dbu)
  tp.var("space_to_MTPMK",        6.0 / $ly.dbu)
  tp.var("space_to_OTP_MK",       6.0 / $ly.dbu)
  
  tp.var("space_to_scribe_line", 26 / $ly.dbu)
  
  tp.var("um1", 1 / $ly.dbu)
  tp.var("um2", 2 / $ly.dbu)
  
  tp.output("to_fill", TilingOperator::new($ly, fill_cells[metal], fill_cell.cell_index, fc_box_in_dbu, row_step_in_dbu, column_step_in_dbu, fc_origin_in_dbu))

  if metals_ignore_active[metal]
      tp.queue("
# Not a dedicated rule, but it makes sense here as well
var scribe_line_ring = _frame - _frame.sized(-space_to_scribe_line);

var fill_region = _tile & _frame
                  - Metal.sized(space_to_Metal)
                  - FuseTop.sized(space_to_FuseTop)
                  - POLYFUSE.sized(space_to_POLYFUSE)
                  - FUSEWINDOW_D.sized(space_to_FUSEWINDOW_D)
                  - PMNDMY.sized(space_to_PMNDMY)
                  - MTPMK.sized(space_to_MTPMK)
                  - OTP_MK.sized(space_to_OTP_MK)
                  - scribe_line_ring;

_output(to_fill, fill_region)")
  else
      tp.queue("
# Not a dedicated rule, but it makes sense here as well
var scribe_line_ring = _frame - _frame.sized(-space_to_scribe_line);

var fill_region = _tile & _frame
                  - Metal.sized(space_to_Metal)
                  - previous_metal.sized(space_to_previous_Metal)
                  - subsequent_metal.sized(space_to_subsequent_Metal)
                  - FuseTop.sized(space_to_FuseTop)
                  - POLYFUSE.sized(space_to_POLYFUSE)
                  - FUSEWINDOW_D.sized(space_to_FUSEWINDOW_D)
                  - PMNDMY.sized(space_to_PMNDMY)
                  - MTPMK.sized(space_to_MTPMK)
                  - OTP_MK.sized(space_to_OTP_MK)
                  - scribe_line_ring;

_output(to_fill, fill_region)")

  end

  # perform the computations inside the tiling processor through "expression" syntax
  # (see https://www.klayout.de/doc-qt4/about/expressions.html)


  # Ignore DM.4 to DM.7 for now
  # With those it's almost impossible to fill a digital design...
  # - subsequent_metal.sized(um1) - previous_metal.sized(um1)

  begin
    $ly.start_changes   # makes the layout handle many changes more efficiently
    tp.execute("Tiled fill")
  ensure
    $ly.end_changes
  end

end

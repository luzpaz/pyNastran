More Information
----------------
If you like it/want to help leave some feedback:
 - [Dicussion Page](https://groups.google.com/forum/#!forum/pynastran-discuss)
 - [Developer Dicussion](https://groups.google.com/forum/#!forum/pynastran-dev)

If you have a bug/want a new feature or card, leave some feedback on the [Issue Tracker](https://github.com/SteveDoyle2/pyNastran/issues)

Release Notes
=============
v1.5.0 (2022/?/?)
-----------------
bdf:
 - faster mass checks
OP2:

op2_geom:
 - adding DVTREL1, DMNCON, GROUP
 - params: MDLPRM  (unreleased)

OP2 writer:
 - SET1
gui:
 - adding nastran_to_vtk

v1.4.0 (2021/8/??)
-----------------
Programmatics:
 - Supports Python 3.7-3.10
 - much improved MSC 2020/2021 and OptiStruct support
 - GUI is compatible with PyQt5 and PySide2
 - support for latest numpy/h5py

BDF:
 - new cards:
   - BGSET, BGADD, BCTPARM, BCBODY, TOPVAR, MATEV, PCOMPLS, TABDMP1
 - convert:
   - now supports A/acceleration, V/velocity
   - messages should be clearer (only the relevant conversions to your model are written)
 - mirror:
   - now supports solid elements (they have to be inverted); double check your loads
   - fixed bug where tolerance was ignored
   - adding punch flag
 - mass_properties:
   - CONM2 considers inertia
 - equivalence
   - now supports node sets as a list[list[int]], list[numpy array], list[set[int]]
 - quality:
   - added warping
 - renumber:
   - AUTOSPC support
 - new arguments:
   - adding validate flag (default=False) option to add_flutter method
   - adding extrap=0 flag (for NX) to TABLED* and TABLEM*
   - tref support in RBE2, RBE3, RBAR
   - ge_matrix support for MSC MAT2
   - added support for MSC 2021 PBUSH alpha, tref, coinl parameters
 - new features
   - read_bdf now supports Path objects
   - added node now has a get_position_wrt_coord_ref method
   - aero panels now have a 'plot' method, which will plot aero subpanels and points
   - FLUTTER card initialization now has a validate option (default=False)
   - MPC now has dependent_dofs, independent_dofs, independent_nodes, dependent_nodes properties
 - fixing:
   - fixed test_bdf bug that dropped the global subcase
     - it's not used unless there are no local subcases
   - deepcopying a card now supports comments
   - CAERO1, CAERO5, CAERO7 paneling bug (nodes and sub-elements should be defined chordwise)
   - adding more fields to add_* methods for CPLSTS*, CPLSTN*
   - better DEQATN python-builtin prevention (allows for executing Nastran equations)
   - better DTABLE handling
   - DRESP1 checks (with validate=True flag)
   - CBEAM.get_field now works
     - now uses nodes/nodes_ref instead of ga/ga_ref and gb/gb_ref
   - RBE3.get_field now works
   - better NLPARM checks
   - get_oml now clips the normal to [-1., -1.] to avoid out of bounds normal values
   - CBAR/CBEAM: A(), I1(), I2(), I12() methods all return floats
   - large field solid writing (forgot the *)
   - DVMREL2 support for MAT8
   - PLOAD2 can have 6 eids (not 5)
   - PBUSH1D parsing is more lax
   - test_bdf bug when subcase=0 was the only subcase
 - changes:
   - more use of warnings.warn instead of print when log doesn't exist
   - CONM2 positive semi-definite check is relaxed as it's the sum of masses on a node
     (not just due to one element) that has to be positive semi-definite
   - test_bdf now has volume > 0 requirement for solids

OP2:
 - reworked OES/OEF table reading to more robustly handle sort/format codes
 - grid point forces
   - fixed crash in GPFORCE shear_moment_diagram (shear/moment/torque plotter)
   - extract_interface_loads now returns force and moment
     - see _extract_interface_loads if you want the old behavior
 - vectorized real cbeam_stress/strain
 - improved NX 64-bit support
   - matrices should work much better in 64 bit
 - new results:
   - random sort2
     - CTRIA3/6
     - CQUAD4/8
   - model.op2_results.separation_initial
   - model.op2_results.separation_final
   - model.glue_forces
   - model.contact_tractions_and_pressures
   - model.contact_forces
   - model.op2_results.stress.chexa_compostite_stress/strain
   - model.op2_results.strain_energy.cbeam3_strain_energy
   - model.op2_results.strain_energy.cfast_strain_energy
   - model.op2_results.strain_energy.cseam_strain_energy
   - model.grid_point_surface_strains
   - model.grid_point_strains_volume_direct
   - model.grid_point_strains_volume_principal
   - model.grid_point_strain_discontinuities
   - model.op2_results.responses.normalized_mass_density
 - removed:
   - VU elements (MSC/NX recently removed these)
 - vectorized most op2 writing
 - bug fixes:
   - GPL bug
   - PARAM reading is much more robust
   - improved regex support for including/excluding results
   - GPDT/S and BGPDT/S tables bugs fixed
   - fixes for composite strength ratios and failure indices

OP2 Geom:
 - now works when no subcases are included :)
 - added many aero (EDT) and optimization (EDOM) cards
 - 32/64-bit modern MSC support
   - MSC 2020 is very different than MSC 2005
   - many cards changed (e.g., the CQUAD4) to simplify I/O
 - 64-bit NX support
 - improved:
   - MSC PCOMP ft support
   - MSC PSOLID fctn support
   - PSOLID isop=2
   - DSCREEN support
   - much better CBAR/CBEAM offt flag 
 - dual cards:
     - dual cards are cards that are different:
       - across different versions of Nastran (MSC vs NX) or (MSC 2020 vs. MSC 2021)
       - across different solutions (e.g., static vs. nonlinear)
     - new:
       - MAT2; (known issue: crashes if you have negative matrial ids)
       - DCONSTR, PBUSH
     - changed:
       - N/A
 - adding:
     - tables: TABLEH1, TABLEHT
     - loads: QVECT
     - aero: CAERO3, CAERO4, PAERO5, DIVERG, SET1, AELINK, MONPNT1, MONPNT2, MONPNT3, MONDSP1
     - mixed single/double precision for defining CORD2R/CORD2C
     - DTI,UNITS
 - bug fixes:
   - NLRSFD bug
   - SPLINE3 bug
   - PBUSH1D parsing bug (swapped equations for tables)
   - BSET1 and CSET1 were flipped

OP2 writer:
 - adding AELINK, MONPNT1, MONPNT2, MONPNT3, MONDSP1, SET1, CAEROx
 - fixed: 64-bit ints before writing ids (to avoid improperly sized arrays)
 
F06 Flutter Plotter:
 - supports --mach, --q, --alt on the x-axis
 - supports cm/s for velocities

GUI:
 - nastran:
   - transient/complex fringe only animations now supported
   - MOMENT card supported in gui
   - NX nonlinear solid element supported
   - added contact_forces & glue_forces
   - faster 3d bar visualization
   - added warping
   - minor speedups for loading geometry
   - CPYRAM13 fixed
   - xoffset finite bug
 - AVL support:
   - sine/cosine/equal spacing
   - proper classes
 - general gui support:
   - GUI now supports localization based on system configuration
     (e.g., 1,0 is 1.0 in some countries)
   - highlight point size option in settings
 - fixing:
   - fixed bug in gif writing for profile='0 to scale to -scale to 0'
   - better validation of floats

v1.3.3 (2020/6/28)
------------------
This is a bug fix only release outside of:
 - subcase.add_set_from_values(set_id, values)
which was overly complicated to do before.

Versions:
 - adding support for vtk 9 (GUI)
 - adding support for nptyping 1.1

BDF:
 - More TEMPRB defaults
 - DRESP2 now handles DTABLE properly when validate=True is used
 - TSTEPNL now handles KUPDATE (NX parameter)
 - fixing SET2 safe-xref
 - fixing SPLINE1 validate
 - fixing TRIM2 aeqr setting bug (was defaulted to 1.0)
 - fixing ACMODL for NX (didn't support writing)
 - fixed DCONADD bug (added the dconadd_id to the summation)
 - DEQATN now checks that the function name is not an argument
 - convert:
   - MAT8 now supports temperature scaling
   - fixed major PSHELL 12I/t^3 convert/scale bug
 - optimization checks:
   - DRESP1 DISP no longer limited to 1 node
   - DVMREL1/2 - MAT8 now supports E2, G12, G2Z, RHO, A1, A2
   - DVPREL1/2 - PLEAS now supports S1/5
   - DVPREL1/2 - PSHELL now supports Z1, Z2
   - DVPREL1/2 - PCOMP now supports NSM/4
   - DVPREL1/2 - PSHEAR now supports NSM/5

OP2:
 - auto-conversion to nx for some tables
 - added SixtyFourBitError, which is inherited from NotImplementedError
    - mainly used for op2 geometry and op2 writing
 - adding op2_results repr method
 - Convergence object has better repr

OP2 Writer:
 - fixed multiple PCOMP writing bug
 - added some 64 bit checks (64-bit writing is not supported)
 - turns out the CPYRAM (NX) has 14 node fields (even though it has 13 nodes)
 - fixed symmetric PCOMP writing

OP2 Geom:
 - fixed GRID, CORD2x reading from the GEOM1N table
 - fixed PSHELL reading bug that occurs when very large property ids exist
 - fixed MAT10 reading bug that occurs when very large material ids exist
 - fixing USET1 reading
 - PMASS were put in self.properties, not self.properties_mass
 - MATT2 tables properly handle table_ids=0 now
 - DEFORM and CLOAD are not the GEOM3/loads table
 - corrected SPC to NX bug
 - NX support (the card format is different than MSC)
   - PENTA (doesn't exist in MSC)
   - CTRIAX
   - TSTEPNL
   - TLOAD1 (also 64-bit)
   - TLOAD2 (also 64-bit)
 - multiple MATS1s now work
 - 64 bit:
   - multiple SEBULKs now work
   - SPOINTs work now
   - MAT10, MATT2, MATT3, MATT9
   - supporting alternate 64-bit PCOMP
   - PBARL
   - NLPARM

F06 Flutter Plotter
 - added check for mode id > 0
 - better parsing of modes; '1,3:' is now supported

minor:
 - removal of some prints
 - more docstrings
 - more typing
 - fixing Tecplot to Nastran converter

v1.3.2 (2020/4/8)
-----------------
With Python 2 now officially dead, it's time for a new feature to encourage people to switch.

There is now support for writing OP2 files!  They're difficult to create from scratch,
but modifying an existing is easy.  This also includes geometry support.

In addition, many new OP2 results have been added.  Modern NX Nastran should work much better.

Programmatics:
 - Supports Python 3.7 and 3.8
 - Dropping Python 2.7 and 3.6 support
 - GUI is compatible with PyQt5 and PySide2
 - improved testing of old versions of packages

BDF:
 - enhancements
   - 405 cards supported (up from 373)
   - improved mesh utilities
      - bdf mirror, bdf convert, bdf export_caero_mesh
      - additional `bdf scale`, which takes arbitrary mass, length, time, pressure, or velocity scale factors (3 of 5) to apply a scaling law
   - added deck guessing with punch=None
   - better parser for test_bdf
   - PCOMPG now supports DVPRELx
   - added get_position for SPOINT
   - added inertia for PBARL/L
   - bdf mirror:
     - added PLOTEL, RROD, RBAR, RBAR1, RBE1, AELIST, AESURF support
   - bdf_equivalence:
     - method='new' no longer requires neq_max
     - use method='old' for old behavior (deprecated)
 - bug fixes:
 - new cards:
   - DTI besides UNITS are now supported
   - PBEAM3, TEMPB3
 - minor enhancements:
   - handling ;; in DEQATN
   - support for SURF cid=None in _get_forces_moments_array
   - added check for number of loads = nscale factors for LOAD
   - more PARAM validation
- changes:
   - warning on RBAR dof check instead of RuntimeError

OP2:
 - enhancements:
   - OP2 write support
   - fixed most pandas deprecation warnings/added support for pandas 0.25
   - much improved NX 2019.2 support
 - minor enhancements:
   - more hdf5 results
   - a few more cards supported in the OP2 geometry reader
   - preliminary NX 64-bit support
   - more MSC versions supported
   - sped up R1TABRG (optimization) reading
   - various geometry cards added
   - supports more PARAM reading
 - new results:
    - composite failure indicies (OEFIT)
    - sensitivity support (DSCMCOL)
    - Cambpell diagrams (CDDATA)
    - eigenvectors (BOPHIGF)
    - grid point forces SORT2 (OGPFB2)
    - stress/strain/force
      - random stress/strain (OESVM1/2, OESVM1C, OSTRVM1/2, OSTRVM2, OESXRM1C, OESXNO1, OESXNO1C)
      - real/complex stress/strain/force output for centroidal CQUADR/CTRIAR
      - complex CBEAR forces
      - real CFAST, CWELD forces
      - nonlinear cbush stress/strain/force
    - other
      - XSOP2DIR
      - PSDs
      - optimization
        - convergence table
        - design variables
        - weight response
        - displacement response
        - stress response
        - strain response
        - force response
        - composite stress response
        - composite strain response
        - fractional mass response
    - SOL 401/402 results:
      - eigenvalue_fluid (LAMAF, LAMAS)
      - eigenvectors (BOPHIGF, BOPHIGS)
      - temperature (OTEMP1)
      - solution set
        - results: displacement, velocity, acceleration, eigenvectors:
        - tables: OUXY1, OUXY2, OPHSA
 - API:
   - reorganized output results to use op2_results object to simply interface
     - backwards compatibility for stress, strain, forces, strain energy
     - model.cbar_force -> model.op2_results.force.cbar_force
     - model.cbar_stress -> model.op2_results.stress.cbar_stress
     - model.cbar_strain -> model.op2_results.strain.cbar_strain
     - model.cbar_strain_energy -> model.op2_results.strain_energy.cbar_strain_energy
 - TODO: linear/nonlinear hyperelastic solids
 - TODO: stress transforms.  This is probably a bit of work.
 - TODO: preliminary NX 64-bit support
 - TODO: CD transforms for cylindrical/spherical displacement, velocity, acceleration, forces.  This shouldn't be terrible.

GUI:
 - enhancements:
    - Can now load custom fringe/displacement/force results with an incorrect
      number of nodes/elements.  It's assumed that the node/element id in the
      first column should be the same as the id for the model.  Thus, you just
      filter out extra nodes/elements or you set some blank nodes/elements.
       - For integer results, no masking is applied.
       - For float results, masking is applied and nan corresponds to no color.
   - animation now supports complex fringe
   - result case description now shows the min/max value as well as the location
   - result case description now shows the mode/time/frequency
   - map centroidal to nodal option
   - adding node/element highlight menu
   - adding node/element mark/label menu
   - result case description now shows the min/max value as well as the location
   - result case description now shows the mode/time/frequency
 - minor enhancements:
   - added export result option to right-click menu
   - legend supports unicode
   - more keyboard shortcuts
 - nastran:
   - geometry:
     - added preferences for geometry/results to speed up model loading
     - element & material coordinate systems
   - results
     - added acoustic displacements (OUG1F)
     - real/complex stress/strain/force results
       - plate by upper/lower, composite plates by ply, bars, rods, springs, cbush, cdamp
     - fractional mass response

F06:
 - KE support for plot_145

Bug fixes:
 - BDF:
   - fixing bug in set_param
   - PBARL & PBEAML DBOX now has defaults for DIM5-DIM10
   - added AECOMPL, DEFORM to bdf attributes
   - added RHO to MAT10 updater
   - Better case control SET parser (can now handle 1,THRU,10,EXCEPT,7,8,
     which doesn't have spaces that makes parsing easier).  It's also orders
     of magnitude faster on large problems.
   - Fixed NDDL bug in MONPNT2
   - Added check for DVPRELx to prevent referencing property fields when another
     similar property is used (e.g., a DVPRELx references a PCOMPG, but the PCOMP
     field id numbers are used to update the card).
   - added some missing hdf5 object support
   - fixing DEQATN bug caused by using python builtin
   - fixed missing variable in mass properties error message
   - aero
     - fixed issue where CAERO1 didn't set the xyz1 and xyz4 points to arrays
       when loading an HDF5 file
     - caero2 now sets box ids
   - elements/properties
     - added I12, J to PBEAM updater; fixed error message
     - fixed Area calculation for PBARL/CHAN, HAT1, DBOX
     - fixed PBAR optimization treating I12 as I1; added J
   - convert better handles:
     - T1-T4 in quad shells
     - fixed bug in CGAP x/g0
   - bdf mirror:
     - fixed bug where max element id is less than max rigid_element id
     - fixed bug with shells that have blanks (e.g., CTRIA6, CQUAD8)
     - plane is now case insensitive and auto-sorted
     - CAERO1 now supports lspan/lchord and Cp
     - CAERO1 handles xy plane properly now (doesn't assume it's xz)

OP2:
 - geom bug fixes:
    - fixed reading bugs for QHBDY and SPCOFF
    - better identifying duplicate property id (PBCOMP -> PBEAM)
    - fixed CONVM error (it can be 6 or 7 fields, not only 6)
    - fixed ACCEL key
 - bug fixes:
    - R1TABRG now stores response_types as strings
      (instead of bytes for Python 3)
    - f06 writer now writes CDAMP3/4 names correctly

GUI:
 - bug fixes:
   - better argument handling
   - fixed coordinate system scaling bug
   - added check on highlight menu for model existence
   - fixed import for new version download menu
   - improved command line error message
   - fixed support for CAEROx models without elements
   - export_cases now supports integers

v1.3.1 / v1.3.0 (2020/4/8)
--------------------------
 - This result has been superseded by 1.3.2.  No code changes, but the PyPi page was redone.

v1.2.1 (2019/5/24)
------------------
OP2:
 - fixed bug with OUGV1PAT table

v1.2.0 (2019/5/21)
------------------
Programmatics:
 - This is the last Python 2.7 release.
 - Dropping Python 3.5 support
 - Supports Python 2.7, 3.6-3.7
 - GUI is compatible with PyQt4/PyQt5 as well as PySide/PySide2
 - improved testing of old versions of packages

BDF:
 - 373 cards supported (up from 343)
 - added abiltity to write models to separate include files
     ```python
     >>> model = BDF()
     >>> model.read_bdf(bdf_filename, save_file_structure=True)

     out_filenames = {
         bdf_filename : bdf_filename_new,
         include_filename : include_filename_new,
     }
     >>> model.write_bdfs(out_filenames, relative_dirname=None, is_windows=None)
     >>> ifile = model.grids[1].ifile
     ```

 - HDF5 import/export
      ```python
     >>> model = read_bdf(bdf_filename)
     >>> model.export_hdf5_filename(hdf5_filename)
     >>> model_new = OP2()
     >>> model_new.load_hdf5_filename(hdf5_filename)
     ```

 - preliminary superelement support
     ```python
     >>> model.read_bdf(bdf_filename)
     >>> model.superelement_models[1].nodes
     ```


OP2:
 - reorganization of random op2 results into op2.results.psd (or ato, no, crm, rms) to aide in finding data
 - reorganization of op2 class to reduce number of functions in the object.  This affects any custom table reading.
 - improved optimzation response reading
 - limited SORT2 support
 - fixed CD transformation bug for BOUGV1 and BOPHIG1 tables
 - Improved HDF5 export/import support (e.g., matrices, random results)

 - Can optionally save directly to HDF5 instead of numpy (limited).
 - Loading OP2s to an HDF5 file to decrease memory usage
      ```python
     >>> op2_model = OP2()
     >>> op2_model.load_as_h5 = True
     >>> op2_model.read_op2(op2_filename)
     ```

OP2Geom:
 - HDF5 support
 - reading EQEXIN/S, GPT, GPDT, CSTM/S tables (recovery of nodes & coordinate with OP2Geom)
 - fixed theta/mcid reading for CTRIA3/CQUAD4
 - fixed CQUAD8 bug

GUI:
 - sped up HTML logging
 - much improved groups menu
 - options for Nastran in preferences menu to speed up loading/limit memory usage
 - pyNastran BDF pickle reading
 - pyNastran OP2 HDF5 reading (not MSC's format)
 - visualization when pickling nodes/elements
 - min/max labels
 - highlight menu
 - Patran-style colors
 - custom force vectors
 - AVL support


Known issues:
 - Transient Pandas Dataframes will fail for newer versions of numpy/pandas.  If anyone knows how to use a MultiIndex,
   this is probably pretty easy to fix.

v1.1.0 (2018/6/26)
------------------
Programmatics:
 - Added support for numpy 1.14
 - Dropping support for Python 3.4 (2.7, 3.5, 3.6 are supported)
 - Dropping support for VTK 5/6 (7/8 are supported)

BDF:
 - model may be pickled (model.save('model.obj') and model.load('model.obj')
 - simplified cross-referencing

OP2:
 - model may be pickled (model.save('model.obj') and model.load('model.obj')
 - Added support for exporting OP2 to HDF5 (uses pyNastran format, not MSC)
 - real sparse matrices take much less memory now; were being converted to dense matrices

GUI:
 - improved animations
 - improved labels

BDF (detailed):
  - New features:
    - model.get_reduced_loads(load_id)
    - model.get_reduced_dloads(dload_id)
    - card1 == card2 now supported
    - PBARL/PBEAML support the NX TUBE2 type
    - added FREQ3, FREQ5, CAERO5, PAERO5, MATT3, SPLINE3, RSSCON, OMIT1
    - more xref
    - added model.clear_attributes()
    - renumbering:
      - bdf_renumber now supports renumbers SETs and SPLINEx cards
      - SPOINTs/EPOINTs now use dictionaries to enable SPOINT/EPOINT renumbering
      - caero sub-panels ids are now renumbered
      - renumbering mapper object returned now
    - improved removed_unused card support
    - improved mirroring
    - read_bdf StringIO option now parses pyNastran header
    - subcase copying speedup (helps with SETs)
    - preliminary ZONA loading
    - added atmosphere2.make_flfacts_eas_sweep, make_flfacts_mach_sweep, and
      make_flfacts_alt_sweep with an EAS (equivalent airspeed) limiter
    - rotate_v_wa_wb for CBAR/CBEAM to determine element vectors

  - Bug fixes:
    - more add_card documentation (e.g., add_grid, add_ctria3)
    - fixed NSMADD card type (was SPCADD)
    - fixed CPLTSTN3 card type (was CTRIA3)
    - fixed CPLTSTS3 card type (was CTRIA3)
    - fixed shell MCIDs not renumbering
    - fixed FREQx renumbering crash
    - model may be pickled again (model.save('model.obj') and model.load('model.obj')
    - fixed PBARL/PBEAML DBOX error
    - fixed PositionWRT bug
    - fixed LOAD card messing up load ids after cross referencing
    - fixed TRIM default on aeqr (was 0.0/rigid; should be 1.0/elastic)
    - NLPCI now gets written when there are no other dynamic cards
    - fixed CBUSH cid=0 bug
    - fixed TABLED4/TABLEM4 stopping error

  - API changes:
    - model.Node(nid, allow_empty_nodes=False msg='') no longer supports
      allow_empty_nodes.  Use:
        model.EmptyNode(nid, msg='') instead for that
        model.Node(nid, msg='') is the new form
    - model.Nodes(nid, allow_empty_nodes=False msg='') no longer supports
      allow_empty_nodes.  Use:
        model.EmptyNodes(nid, msg='') instead for that
        model.Nodes(nid, msg='') is the new form
    - PCOMPG.validate() now checks that global ply ids are unique
    - xref_nodes_with_elements now creates a list instead of a set
      (fixes a Python 3.x bug)
    - get_MPCx_node_ids_c1 is now get_MPCx_node_ids_c1
      (was inconsistent with what it does)
    - get_MPCx_node_ids_c1 created
    - xref'd objects now use _ref globally
    - aestat.id is now aestat.aestat_id
    - aeparm.id is now aeparm.aeparm_id
    - model.add_aset1/aset (also bset/cset/qset/uset) now a consistent set of
      function arguments and call the same function.  The card will be created
      based on your data instead of necessarily what you asked for.
    - LOAD cards are now stored in model.load_combinations instead of model.loads

  - Known bugs:
    - dynamic loads cross-referencing is buggy;
      reject the cards if there is a problem
    - PBEAM defaults with ENDA are slightly incorrect.

OP2 (detailed):
  - New features:
    - added model.set_additional_generalized_tables_to_read(tables) to
      create custom OP2 readers
    - added complex/average strain energy
    - save/load hdf5 support
    - EIGRL support

  - Bug fixes:
    - improved table skipping
    - fixed RealCShearForceArray f06 writing
    - fixed CEN/3, CEN/4 writing for RealPlateBilinearForceArray
    - improved geometry table reading
    - real sparse matrices take much less memory now; were being converted to dense matrices
    - added RBAR on NX vs. MSC
    - fixed RBE2 with alpha bug
    - fixed CREEP bug
    - fixed RBE3 bug
    - fixed PBCOMP bug
  - API changes:
    - xlsx exporter removed
  - Known bugs:
    - pandas fails on some decks (numpy<1.13 is fine)
    - a large number of PSOLIDs will crash the read_op2/read_op2_geom;
      use PARAM,OGEOM,NO
    - transform_gpforce_to_global doesn't work properly with cylindrical
      or spherical coordinate systems

GUI (detailed):
  - New features:
    - control surfaces now get labels (label size doesn't resize properly)
    - in-gui animation
    - delete secondary actor support
    - delete result cases support
    - improved view buttons
    - preferences menu
    - right click support on results sidebar to apply fringe/displacement/veactor results

  - Bug fixes:
    - displays control surfaces again (aesurf)
    - changing secondary actor color works again
    - fixing random crash
    - "Show/Hide CAERO panels" updates the "Edit Geometry Properties" menu
    - "Toggle CAERO Subpanels" updates the "Edit Geometry Properties" menu
    - "Toggle CONM2s" updates the "Edit Geometry Properties" menu
    - fixing Windows taskbar icon bug
    - fixing first launch bug
    - qscintilla works in pyqt5

  - Known bugs:
    - after animating a model from within the GUI, the mouse behavior changes

OP4 bug fixes:
 - fixed Python 3 bytes bug

Applications:
 - removed due to excessively amount of unmaintained code

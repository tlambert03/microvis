# Thoughts

this folder is temporary
# TODO ... issues

- things that rely on data.  eg. contrast limits
    - when backend requests clims, it can use `image.clim_applied`
    - but when frontend data changes, DataNode also looks for DataField and calls `.apply()`
    - would be nice to unify that mechanism

## data slicing system...
- needs to be easy/make sense in general but extensible
  - which spaces should be unified?
    - nD or just 3D
    - ^3D is special
  - could unify nD and slice down to 3D with broadcasting rules (good) but lose
    the ability to modify how individual nD layer data is sliced... this is
    why we have to jump through hoops to get dynamic projections in napari
    - could regain individual slicing by replacing world slicing with an
      arbitrary callable... if present, an arbitrary callable on
      the data object - this feels nice!
    - this callable *could* be parametrised by some kind of nD world position

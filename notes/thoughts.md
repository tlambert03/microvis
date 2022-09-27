# features

- in place .data mutations
- ortho viewer
- browser support
- clear backend abstraction
- serialization
- state interpolation


# principles

- model is light
- always serializeable
- only on visualization do we connect backend
- no backend specific code in model


# TODO ... issues

- things that rely on data.  eg. contrast limits 
    - when backend requests clims, it can use `image.clim_applied`
    - but when frontend data changes, DataNode also looks for DataField and calls `.apply()`
    - would be nice to unify that mechanism

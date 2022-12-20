# Thoughts

this folder is temporary
# TODO ... issues

- things that rely on data.  eg. contrast limits
    - when backend requests clims, it can use `image.clim_applied`
    - but when frontend data changes, DataNode also looks for DataField and calls `.apply()`
    - would be nice to unify that mechanism

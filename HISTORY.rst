=======
History
=======

1.1.0 (Unreleased)
------------------

* Improve datetime utc now format on workflow and on timestamp mixin. (rudaporto)
* Changed address mixin to use new Point custom type with GeoJSON support. (ericof)
* Add unit tests to address mixin and improve workflow database unit tests. (ericof)
* Improve address mixin: metadata for colander alchemy and schema validators. (rudaporto)
* Change travis run flake8 on tests folder. (rudaporto)
* BODY-8: Add ImageMixin. (ericof)
* BODY-14: Add BaseMetadata mixin. (ericof)


0.1.0
-----
* overhauls workflow (jsbueno)
* Implements timeout_cache (jsbueno)
* Add helpers to deal with coordinates entry as a GeoJSON (ericof)
* Implements the Base Workflow (ericof)
* Implements the base class for a queue and the events queue (ericof)
* Implements the base class for a worker (ericof)

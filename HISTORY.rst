=======
History
=======

1.1.3 (Unreleased)
------------------

* Add python-logstash as requirement (ericof).
* BODY-60: Fix scale url generation (ericof).
* BODY-62: Add listing and summary serialization to objects (ericof).
* BODY-62: Implement permission checking on object listing (ericof).
* Add briefy.common.users.SystemUser (ericof).
* Add vocabulary with default groups (ericof).
* Fix identation of code examples in the Permission docstring (ericof).
* Add PhotoCategoryChoices and VideoCategoryChoices vocabularies (ericof).
* Add ThreeSixtyImage and Video mixins. Move Image mixin to assets module. (ericof).
* Add LocalRole support. (ericof).
* Improve Workflow documentation. (ericof).


1.1.2 (2016-10-04)
------------------

* BODY-53: Return additional metadata from Image (ericof).
* Add timeout to thumbor connection (ericof).


1.1.1 (2016-09-28)
------------------

* BODY-52: Quote filename for image signature (ericof).
* BODY-55: Improve briefy.common BaseEvent (sqs event dispatcher). (rudaporto)

1.1.0 (2016-09-27)
------------------

* Improve datetime utc now format on workflow and on timestamp mixin. (rudaporto)
* Changed address mixin to use new Point custom type with GeoJSON support. (ericof)
* Add unit tests to address mixin and improve workflow database unit tests. (ericof)
* Improve address mixin: metadata for colander alchemy and schema validators. (rudaporto)
* Change travis run flake8 on tests folder. (rudaporto)
* BODY-8: Add ImageMixin. (ericof)
* BODY-14: Add BaseMetadata mixin. (ericof)
* BODY-16: Add Categories enum to this package. (ericof)
* BODY-18: Add timezone to address mixin. (ericof)
* BODY-18: Add new SQLAlchemy time, AwareDateTime that always uses UTC. (ericof)
* BODY-20: Fix docstrings. (ericof)
* BODY-33: Improve Base model to_dict method to exclude default attributes and also receive a list of attributes do exclude.
* BODY-42: Add scale_with_filters method to Image mixin to generate scales using filters (ericof).
* BODY-42: Allow generation of internal urls available inside our cluster (ericof).
* BODY-40: Workflow history is not being persisted on database for models using worflow mixin. (rudaporto)
* BODY-48: Change workflow mixin init to receive workflow_context. (rudaporto)

0.1.0
-----
* overhauls workflow (jsbueno)
* Implements timeout_cache (jsbueno)
* Add helpers to deal with coordinates entry as a GeoJSON (ericof)
* Implements the Base Workflow (ericof)
* Implements the base class for a queue and the events queue (ericof)
* Implements the base class for a worker (ericof)


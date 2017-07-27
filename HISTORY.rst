=======
History
=======

2.0.7 (2017-07-27)
------------------
    * Added in setupy.py pylibmc and python-memcached as dependency (rudaporto).
    * Improve configuration to distinguish REDIS and MEMCACHED port numbers (rudaporto).

2.0.6 (2017-07-25)
------------------
    * Redis cache settings: socket_timeout=15, distributed_lock=False (rudaporto).

2.0.5 (2017-07-25)
------------------

    * Add a LoggingProxy class to make_region.configure to debug cache setting operations (rudaporto).

2.0.4 (2017-07-20)
------------------

    * Fix to_dict default serialization: now using sqlalchemy inspect function to list all attributes that should be serialized (rudaporto).

2.0.3 (2017-06-28)
------------------

    * New utility to resolve UserProfile info based on the user ID (rudaporto).
    * Serialize state_history only if explicitly set on to_dict includes parameter (ericof).

2.0.2 (2017-05-18)
------------------
    * Allows our Enum items to be pickled (fix caching issues) (jsbueno).

2.0.1 (2017-05-04)
------------------
    
    * When transition happens we also notify model updated event (if available) (rudaporto).
    * New cache manager utility based on dogpile.cache library with support to redis, memcached and memory backends (rudaporto).
    * Change WorkflowBase mixin to store request instance without a property (rudaporto).
    * Base model attribute serialization now make sure we do not return InstrumentedList instances (rudaporto).
    * Improve AddressMixin.coordinates setter (rudaporto).

2.0.0 (2017-04-21)
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
    * BODY-85: Auto generate workflow documentation. (ericof)
    * Include new serializer to sautils PhoneNumber instance (rudaporto).
    * Improve roles mixin with a new class BaseBriefyRoles to be reused in Leica (rudaporto).
    * Make sure new local roles add the LocalRolesChoice enun instance and not the simple string (rudaporto).
    * BODY-91: disable local_roles attribute "joined" load strategy and keep with the default lazy load (rudaporto).
    * Changing local role for professional to use professional_user attribute (rudaporto).
    * Fix entity_id value in the add_local_role method from LocalRolesMixin (rudaporto).
    * Update db person.NameMixin fullname attribute to be orm.column_property based on first and last name (rudaporto).
    * Move new method _summarize_relationships to base Model class and add new attribute  __summary_attributes_relations__ (rudaporto).
    * Add formatted_address attribute to Address Mixin. (ericof).
    * Fix briefy.common.utils.data.generate_contextual_slug to be used as default in the BaseMetadata._slug column argument (rudaporto).
    * Change briefy.common.db.mixins.identifiable.GUID.id column to be binary (default and less alocation space) (rudaporto).
    * New attributes in the local roles mixin: relationships and association proxies for easy access to the user permissions. (rudaporto).
    * New class method Base.__acl__ to map __raw_acl__ to the pyramid format (rudaporto).
    * Improve LocalRolesMixin.add_local_role to receive a new parameter permissions to be granted (rudaporto).
    * Add new mixin to hold contact information: company_name, email, mobile and additional_phone (rudaporto).
    * Change event name validator to accept names with _ (underscore) (rudaporto).
    * Fix bug in the workflow._perform_transition, it should use the name of the transition not the title (rudaporto).
    * New config.IMPORT_KNACK to be used by the import script: disable Timestamp.updated_at onupdate parameter (rudaporto).
    * Makefile improvements (rudaporto).
    * Added missing indexes on mixins (rudaporto).
    * Changed UUID type to native Postgres type (rudaporto).
    * Fix LocalRolesMixin._actors_info method (rudaporto).
    * Change to_dict, to_summary_dict and to_listing_dict to fix performance issues (rudaporto).
    * Fix: Added missing: colander.drop to AddressMixin._coordinates (rudaporto).
    * Add two new options to the Gender vocabulary (rudaporto).
    * Change ContactInfoMixin to drop value if nullable=True and make default=None explicity (rudaporto).
    * Added Objectify helper class to navigate JSON attributes (jsbueno).
    * Improve Objectify to allow defaults and get interation (jsbueno).
    * Added attribute traversal capability to Objectify (jsbueno).
    * Update transition message based on the result of a transition hook, if message key is returned (rudaporto).
    * Add TaskEvent (ericof).
 
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

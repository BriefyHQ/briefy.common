=======
History
=======

2.1.7 (2017-12-05)
------------------
    * Make sure mock_sqs uses SQS_IP and SQS_PORT configuration from the environment (rudaporto).

2.1.6 (2017-11-08)
------------------

    * Upgrade SQLAlchemy to version 1.2.0b3 (rudaporto).

2.1.5 (2017-11-01)
------------------

    * Fix config to support development ENV and setup proper queue suffix and AWS region (rudaporto).

2.1.4 (2017-10-09)
------------------

    * Fix query method from utilities.remote.RemoteRestEndpoint (rudaporto).

2.1.3 (2017-10-03)
------------------

    * Added new utilities to deal with rolleiflex authentication and remote rest items manipulation (rudaporto).
    * Fix: make sure briefy.common.db.model.Base.__colanderalchemy_config__ exists as class attribute with default value (rudaporto).
    * Fix: in briefy.common.event.BaseEvent.to_dict check for to_dict attr in the obj and only if it is not a dict instance already (rudaporto).
    * Added query method in briefy.common.utilities.remote.RemoteRestEndpoint to list items using a dict payload to pass filters (rudaporto).

2.1.2 (2017-09-06)
------------------

    * Change invalidate cache log from info to debug (rudaporto).

2.1.1 (2017-09-04)
------------------

    * Always include obj.state_history in the workflow transition event data payload (rudaporto).

2.1.0 (2017-08-31)
------------------

    * Change LocalRole model and LocalRoleMixin implementation (rudaporto).
    * Created Item model and table to be used as base class for all models that will have local role (rudaporto).
    * Make sure sqlalchemy_continuum is a dependency and that make_versioned function will be called before loading any model (rudaporto).
    * New mixin VersionMixin moved from briefy.leica to common (rudaporto).
    * Change Item model to use VersionMixin and BaseMetadata as base classes (rudaporto).
    * Allow BaseMetadata field to be null: title (rudaporto).
    * Change BaseMetadata to use use getter and setter to read and write attributes (rudaporto).
    * Added new item_type string column to the new local roles table (rudaporto).
    * Change create method of Base model class to look into the __parent_attr__ attribute to find the parent instance (rudaporto).
    * Create new function to manage a list local roles by obj and principal_id (rudaporto).
    * Use correct InstrumentedList api do update local roles attrs when creating new instances (rudaporto).
    * Added customized update method to Item class to deal with update of local role attributes (rudaporto).
    * Define new Model attribute to list all additional local roles to receive can_view permission when create a new instance (rudaporto).
    * Change create method of Item class to use new update method and compute can_view using payload, actors and additional local roles class attribute (rudaporto).
    * Change LocalRole.item_type to be class name lowercase (rudaporto).
    * Change workflow to user document.update method when updating valid_fields (rudaporto).
    * Added indexes to wokflow mixin (state) and items model (type and path) (rudaporto).
    * Upgrade depencie packages (rudaporto).
    * Increase usage of type hints (ericof).
    * Card #514: Refactor workflow package and make sure history is valid before persisting it (ericof).
    * Move ValidationError from briefy.ws to briefy.common.exceptions (ericof).
    * Card #504: Add Phone number validation to mobile and additional_phone attributes on ContactInfoMixin (ericof).
    * Added new Base model attribute to easy include property or association proxy fields in the to_dict payload (rudaporto).
    * Added new dynamic relationship on Item to return all local roles for one instance including from all parents (rudaporto).
    * Added Item.to_dict to append _roles key with all local roles and user ids (rudaporto).
    * Fix: obj.path instance shadowing from parent on LocalRole.create classmethod, now the attribute is copied (rudaporto).
    * Refactor local role mixin functions to avoid repetition and allow code reuse (rudaporto).
    * Fix a bug set_local_roles_by_principal function of model local roles mixin (rudaporto).
    * New base class to create custom comparators to change the query for some hybrid property columns (rudaporto).
    * Created a new comparator for local roles fields to filter items with principal_id the role_name of the local role atttribute (rudaporto).
    * Improve local roles attributes creation using hybrid_property init method (rudaporto).
    * Added a new to_dict method in the BaseEvent class to allow payload customization by subclasses (rudaporto).
    * Add "all" attributes to the list of possible attributes that can be summarized (rudaporto).

2.0.9 (2017-07-28)
------------------

    * Pin package iso8601 to version 0.1.11 (rudaporto).

2.0.8 (2017-07-27)
------------------

    * Add optional_fields to workflow transitions (ericof).

2.0.7 (2017-07-27)
------------------

    * Added in setupy.py pylibmc and python-memcached as dependency (rudaporto).
    * Improve configuration to distinguish REDIS and MEMCACHED port numbers (rudaporto).

2.0.6 (2017-07-27)
------------------

    * Redis cache settings: socket_timeout=15, distributed_lock=False (rudaporto).

2.0.5 (2017-07-25)
------------------

    * Add a LoggingProxy class to make_region.configure to debug cache setting operations (rudaporto).

2.0.4 (2017-07-20)
------------------

    * Enhancements to Objectify: "contains", equality, dottet attr retrieval and mapping interface (jsbueno).
    * Adds monkey-patch override for JSON serialization - JSON works for: uuid, datetime, Objectify (jsbueno).
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
    * Move new method _summarize_relationships to base Model class and add new attribute __summary_attributes_relations__ (rudaporto).
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

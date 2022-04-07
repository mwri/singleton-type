"""
Singleton module. Provides the `Singleton` meta class.

The `Singleton` meta class alters the normal class/object behaviour to make the
target class into a singleton, so that `__new__` and `__init__` will only be
called once, and it is thread safe.

The meta class can be used like this:

    class OneOfMe(metaclass=Singleton):
        pass

    assert id(OneOfMe()) == id(OneOfMe())

If a singleton class is inherited, all sub classes will be singletons (there
will be only one of each type), thus:

    class AnotherOfMe(OneOfMe, metaclass=Singleton):
        pass

    assert id(AnotherOfMe()) == id(AnotherOfMe())
    assert id(OneOfMe()) != id(AnotherOfMe())

When creating a singleton in this fashion, the target class's `__new__` and
`__init__` methods will be called only once, as you might expect. Any arguments
passed to the constructor will be passed as normal, again as you might expect.
Most design scenarios where a singleton would not see the possibility that
constructor arguments would vary, but if they do, then the second set of
arguments will obviously be ineffective. This is almost never a problem because
it would simply not be done when a singleton pattern is prescriptive. Some
cases may arise where it is desirable to do something more interesting, such
as a object/singleton per unique arguments... and this behaviour can be easily
implemented by providing some additional methods.

There are three such methods, and your target class must implement all or none
of them:

First `singleton_ref`, this class method is passed the constructor arguments
and must return the existing singleton object, or `None` if not instantiated
yet. The implementation need not be thread safe, the over all operation will
still be thread safe regardless.

Second `singleton_set_ref`, this class method is passed the object followed
by the constructor arguments, and must SET the singleton object to the object
given (such that `singleton_ref` will return it next time it is called). A
lock will be acquired before this class method is called in order to protect
thread safety.

Last `singleton_detach_ref`, this is an object class method rather than a class
method, passed no arguments beyond the mandatory `self`, and it must undo
`singleton_set_ref` such that there is no longer a singleton in effect (there
may still be references to the previous singleton object of course).
This is an object method rather than a class method so that the detach may
depend on state than the class itself.

It should be clear then why all or none of these methods must be implemented
by the target class, their operation must work in tandem and of necessity will
entirely depend on the differential required behaviour.

The default implementations of these methods will simply get, set and delete
an attribute on the class. Here's an example which provides for a different
object for different arguments (instead of the default different only for
different classes):

    class ObjectCache(metaclass=Singleton):
        _cache = {}

        def __init__(self, id):
            self._id = id

        def __new__(cls, id):
            return super().__new__(cls)

        @classmethod
        def singleton_ref(cls, id):
            return cls._cache[id] if id in cls._cache else None

        @classmethod
        def singleton_set_ref(cls, obj, id):
            cls._cache[id] = obj

        def singleton_detach_ref(self):
            del type(self)._cache[self._id]

Here a `_cache` class attribute is used to retain all instances, one for each
unique ID passed to the constructor, and the three singleton methods provide
the required implementation for this.

In this case then ObjectCache('foo') will always yield the same object, and
ObjectCache('bar') will always yield the same object, but the "foo" and "bar"
objects will be different to each other.

The intent here is that the mapping from the parameter domain (class being a
parameter of course) to the set of instances can governed in any
way desired. Although a less likely requirement, the number of instances can
be reduced as well as expanded, so for example the following would cause all
the instances of a class and any instances of any sub class, to be a singleton
together, so there would only ever be one instance for all the classes:

    class SuperClass(metaclass=Singleton):
        _singleton_ref = None

        @classmethod
        def singleton_ref(cls):
            return TestSingletonA._singleton_ref

        @classmethod
        def singleton_set_ref(cls, obj):
            TestSingletonA._singleton_ref = obj

        def singleton_detach_ref(self):
            TestSingletonA._singleton_ref = None

    class SubClass(SuperClass):
        pass

    assert id(SubClass()) == id(SuperClass())
"""

import threading


class Singleton(type):
    """Singleton meta class. Makes classes into singletons."""

    class ClsImplError(Exception):
        def __init__(self):
            return super().__init__("define all or none of singleton_ref, singleton_set_ref and singleton_detach_ref")

    def __new__(meta_cls, name, bases, dct):
        cls = super().__new__(meta_cls, name, bases, dct)

        if hasattr(cls, "singleton_ref") or hasattr(cls, "singleton_set_ref") or hasattr(cls, "singleton_detach_ref"):
            if not hasattr(cls, "singleton_ref"):
                raise Singleton.ClsImplError()
            if not hasattr(cls, "singleton_set_ref"):
                raise Singleton.ClsImplError()
            if not hasattr(cls, "singleton_detach_ref"):
                raise Singleton.ClsImplError()
        else:
            cls._singleton_ref = None

            @classmethod
            def singleton_ref(cls, *args, **kwargs):
                return cls._singleton_ref

            cls.singleton_ref = singleton_ref

            @classmethod
            def singleton_set_ref(cls, obj, *args, **kwargs):
                cls._singleton_ref = obj

            cls.singleton_set_ref = singleton_set_ref

            def singleton_detach_ref(self):
                type(self)._singleton_ref = None

            cls.singleton_detach_ref = singleton_detach_ref

        cls._singleton_ref_lock = threading.Lock()

        return cls

    def __call__(cls, *args, **kwargs):
        obj = cls.singleton_ref(*args, **kwargs)

        if obj is None:
            with cls._singleton_ref_lock:
                obj = cls.singleton_ref(*args, **kwargs)

                if obj is None:
                    obj = cls.__new__(cls, *args, **kwargs)
                    cls.__init__(obj, *args, **kwargs)

                    cls.singleton_set_ref(obj, *args, **kwargs)

        return obj

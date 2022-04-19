"""Tests for singleton_type module."""

import threading
from concurrent.futures import ThreadPoolExecutor
from random import random

import pytest

from singleton_type import Singleton


def test_singleton_classes_instantiate_same_obj():
    class TestSingleton(metaclass=Singleton):
        pass

    assert id(TestSingleton()) == id(TestSingleton())


def test_singleton_classes_new_once():
    count = 0

    class TestSingleton(metaclass=Singleton):
        def __new__(cls):
            nonlocal count
            count += 1
            return super().__new__(cls)

    assert count == 0
    TestSingleton()
    assert count == 1
    TestSingleton()
    assert count == 1


def test_singleton_classes_init_once():
    count = 0

    class TestSingleton(metaclass=Singleton):
        def __init__(self):
            nonlocal count
            count += 1

    assert count == 0
    TestSingleton()
    assert count == 1
    TestSingleton()
    assert count == 1


def test_singleton_classes_new_args_passed():
    class TestSingleton(metaclass=Singleton):
        def __new__(cls, *args, **kwargs):
            assert args == ("pos1", "pos2")
            assert kwargs == {"named1": "named1val"}
            return super().__new__(cls)

    TestSingleton("pos1", "pos2", named1="named1val")


def test_singleton_classes_init_args_passed():
    class TestSingleton(metaclass=Singleton):
        def __init__(self, *args, **kwargs):
            assert args == ("pos1", "pos2")
            assert kwargs == {"named1": "named1val"}

    TestSingleton("pos1", "pos2", named1="named1val")


def test_diff_singleton_classes_instantiate_diff_objs():
    class TestSingletonA(metaclass=Singleton):
        pass

    class TestSingletonB(metaclass=Singleton):
        pass

    assert id(TestSingletonA()) != id(TestSingletonB())


def test_singleton_subclasses_instantiate_same_obj():
    class TestSingletonA(metaclass=Singleton):
        pass

    class TestSingletonB(TestSingletonA):
        pass

    assert id(TestSingletonB()) == id(TestSingletonB())


def test_singleton_subclasses_instantiate_diff_objs_to_superclass_1():
    class TestSingletonA(metaclass=Singleton):
        pass

    class TestSingletonB(TestSingletonA):
        pass

    assert id(TestSingletonB()) != id(TestSingletonA())


def test_singleton_subclasses_instantiate_diff_objs_to_superclass_2():
    class TestSingletonA(metaclass=Singleton):
        pass

    class TestSingletonB(TestSingletonA):
        pass

    assert id(TestSingletonA()) != id(TestSingletonB())


def test_singleton_subclass_siblings_instantiate_diff_objs():
    class TestSingletonA(metaclass=Singleton):
        pass

    class TestSingletonB(TestSingletonA):
        pass

    class TestSingletonC(TestSingletonA):
        pass

    assert id(TestSingletonB()) != id(TestSingletonC())


def test_singleton_new_obj_after_detach():
    class TestSingleton(metaclass=Singleton):
        pass

    foo = TestSingleton()
    bar = TestSingleton()

    assert id(foo) == id(bar)

    bar.singleton_detach_ref()
    baz = TestSingleton()

    assert id(foo) != id(baz)


@pytest.mark.slow
@pytest.mark.soak
def test_thread_safe_soaktest():
    max_workers = 100
    work_count = 1000

    class TestSingletonA(metaclass=Singleton):
        pass

    class TestSingletonB(metaclass=Singleton):
        pass

    class TestSingletonC(TestSingletonA):
        pass

    class TestSingletonD(TestSingletonA):
        def __init__(self, *args, **kwargs):
            a = TestSingletonA()

    class TestSingletonE(TestSingletonA):
        def __init__(self, *args, **kwargs):
            b = TestSingletonB()

    last_a = None
    last_b = None
    last_c = None
    last_d = None
    last_e = None

    def assert_same_if_last(new_inst, prev_inst):
        if prev_inst is not None:
            assert id(prev_inst) == id(prev_inst)

    def cb(i):
        nonlocal last_a, last_b, last_c, last_d, last_e

        if int(random() * 6) == 0:
            a = TestSingletonA()
            assert_same_if_last(a, last_a)
            last_a = a
        elif int(random() * 6) == 1:
            b = TestSingletonB()
            assert_same_if_last(b, last_b)
            last_b = b
        elif int(random() * 6) == 2:
            c = TestSingletonC()
            assert_same_if_last(c, last_c)
            last_c = c
        elif int(random() * 6) == 3:
            d = TestSingletonD()
            assert_same_if_last(d, last_d)
            last_d = d
        elif int(random() * 6) == 4:
            e = TestSingletonE()
            assert_same_if_last(e, last_e)
            last_e = e
        elif int(random() * 6) == 5:
            if int(random() * 5) == 0:
                TestSingletonA().singleton_detach_ref()
            elif int(random() * 5) == 1:
                TestSingletonB().singleton_detach_ref()
            elif int(random() * 5) == 2:
                TestSingletonC().singleton_detach_ref()
            elif int(random() * 5) == 3:
                TestSingletonD().singleton_detach_ref()
            elif int(random() * 5) == 4:
                TestSingletonE().singleton_detach_ref()

    with ThreadPoolExecutor(max_workers=max_workers) as tp:
        futures = [tp.submit(cb, i) for i in range(0, work_count)]
        results = [f.result() for f in futures]


def test_singleton_raises_for_partial_ref_method_impl():
    with pytest.raises(Singleton.ClsImplError):

        class TestSingletonB(metaclass=Singleton):
            @classmethod
            def singleton_ref(_cls):
                pass

    with pytest.raises(Singleton.ClsImplError):

        class TestSingletonC(metaclass=Singleton):
            @classmethod
            def singleton_set_ref(_cls, _obj):
                pass

    with pytest.raises(Singleton.ClsImplError):

        class TestSingletonD(metaclass=Singleton):
            @classmethod
            def singleton_detach_ref(_cls):
                pass

    with pytest.raises(Singleton.ClsImplError):

        class TestSingletonB(metaclass=Singleton):
            @classmethod
            def singleton_ref(_cls):
                pass

            @classmethod
            def singleton_set_ref(_cls, _obj):
                pass

    with pytest.raises(Singleton.ClsImplError):

        class TestSingletonB(metaclass=Singleton):
            @classmethod
            def singleton_ref(_cls):
                pass

            @classmethod
            def singleton_detach_ref(_cls):
                pass

    with pytest.raises(Singleton.ClsImplError):

        class TestSingletonB(metaclass=Singleton):
            @classmethod
            def singleton_set_ref(_cls, _obj):
                pass

            @classmethod
            def singleton_detach_ref(_cls):
                pass

    class TestSingletonA(metaclass=Singleton):
        @classmethod
        def singleton_ref(_cls):
            pass

        @classmethod
        def singleton_set_ref(_cls, _obj):
            pass

        def singleton_detach_ref(_self):
            pass


def test_singleton_by_arg_more():
    class TestSingletonObjCache(metaclass=Singleton):
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

    foo1 = TestSingletonObjCache("foo")
    bar1 = TestSingletonObjCache("bar")
    baz1 = TestSingletonObjCache("baz")
    foo2 = TestSingletonObjCache("foo")
    bar2 = TestSingletonObjCache("bar")
    baz2 = TestSingletonObjCache("baz")

    assert id(foo1) == id(foo2)
    assert id(bar1) == id(bar2)
    assert id(baz1) == id(baz2)

    foo1.singleton_detach_ref()
    foo3 = TestSingletonObjCache("foo")

    assert id(foo1) != id(foo3)


def test_singleton_by_arg_less():
    class TestSingletonA(metaclass=Singleton):
        _singleton_ref = None

        @classmethod
        def singleton_ref(cls):
            return TestSingletonA._singleton_ref

        @classmethod
        def singleton_set_ref(cls, obj):
            TestSingletonA._singleton_ref = obj

        def singleton_detach_ref(self):
            TestSingletonA._singleton_ref = None

    class TestSingletonB(TestSingletonA):
        pass

    assert id(TestSingletonA()) == id(TestSingletonB())

# -*- coding: utf-8 -*-

"""
The free hypergraph category, i.e. diagrams with swaps and spiders.

Spiders are also known as dagger special commutative Frobenius algebras.

Summary
-------

.. autosummary::
    :template: class.rst
    :nosignatures:
    :toctree:

    Ob
    Ty
    Diagram
    Box
    Cup
    Cap
    Swap
    Spider
    Category
    Functor
"""

from __future__ import annotations
from collections.abc import Callable

from discopy import compact, pivotal
from discopy.cat import factory
from discopy.monoidal import assert_isatomic
from discopy.utils import factory_name


class Ob(pivotal.Ob):
    """
    A frobenius object is a self-dual pivotal object.

    Parameters:
        name : The name of the object.
    """
    def conjugate(self):
        return self

    l = r = property(conjugate)


@factory
class Ty(pivotal.Ty):
    """
    A frobenius type is a pivotal type with frobenius objects inside.

    Parameters:
        inside (frobenius.Ob) : The objects inside the type.
    """
    ob_factory = Ob


@factory
class Diagram(compact.Diagram):
    """
    A frobenius diagram is a compact diagram with :class:`Spider` boxes.

    Parameters:
        inside(Layer) : The layers of the diagram.
        dom (Ty) : The domain of the diagram, i.e. its input.
        cod (Ty) : The codomain of the diagram, i.e. its output.
    """
    ty_factory = Ty

    @classmethod
    def spiders(cls, n_legs_in: int, n_legs_out: int, typ: Ty, phase=None
            ) -> Diagram:
        """
        Returns a diagram of interleaving spiders.

        Parameters:
            n_legs_in : The number of legs in for each spider.
            n_legs_out : The number of legs out for each spider.
            typ : The type of the spiders.
            phase : The phase for each spider.
        """
        result = cls.id().tensor(*[
            cls.spider_factory(n_legs_in, n_legs_out, x, p) for x, p in zip(
                typ, len(typ) * [None] if phase is None else phase)])
        for i, t in enumerate(typ):
            for j in range(n_legs_in - 1):
                result <<= result.dom[:i * j + i + j] @ cls.swap(
                    t, result.dom[i * j + i + j:i * n_legs_in + j]
                ) @ result.dom[i * n_legs_in + j + 1:]
            for j in range(n_legs_out - 1):
                result >>= result.cod[:i * j + i + j] @ cls.swap(
                    result.cod[i * j + i + j:i * n_legs_out + j], t
                ) @ result.cod[i * n_legs_out + j + 1:]
        return result

    def unfuse(self) -> Diagram:
        """ Unfuse arbitrary spiders into three- and one-legged spiders. """
        return compact.Functor(ob=lambda x: x, ar=lambda f:
            f.unfuse() if isinstance(f, Spider) else f)(self)


class Box(compact.Box, Diagram):
    """
    A frobenius box is a compact box in a frobenius diagram.

    Parameters:
        name (str) : The name of the box.
        dom (Ty) : The domain of the box, i.e. its input.
        cod (Ty) : The codomain of the box, i.e. its output.
    """
    __ambiguous_inheritance__ = (compact.Box, )


class Cup(compact.Cup, Box):
    """
    A frobenius cup is a compact cup in a frobenius diagram.

    Parameters:
        left (Ty) : The atomic type.
        right (Ty) : Its adjoint.
    """
    __ambiguous_inheritance__ = (compact.Cup, )


class Cap(compact.Cap, Box):
    """
    A frobenius cap is a compact cap in a frobenius diagram.

    Parameters:
        left (Ty) : The atomic type.
        right (Ty) : Its adjoint.
    """
    __ambiguous_inheritance__ = (compact.Cap, )


class Swap(compact.Swap, Box):
    """
    A frobenius swap is a compact swap in a frobenius diagram.

    Parameters:
        left (Ty) : The type on the top left and bottom right.
        right (Ty) : The type on the top right and bottom left.
    """
    __ambiguous_inheritance__ = (compact.Swap, )


class Spider(Box):
    """
    The spider with :code:`n_legs_in` and :code:`n_legs_out`
    on a given atomic type, with some optional ``phase``.

    Parameters:
        n_legs_in : The number of legs in.
        n_legs_out : The number of legs out.
        typ : The type of the spider.
        phase : The phase of the spider.

    Examples
    --------
    >>> x = Ty('x')
    >>> spider = Spider(1, 2, x)
    >>> assert spider.dom == x and spider.cod == x @ x
    """
    def __init__(self, n_legs_in: int, n_legs_out: int, typ: Ty, phase=None,
                 **params):
        self.typ, self.phase = typ, phase
        assert_isatomic(typ)
        name = "Spider({}, {}, {}{})".format(
            n_legs_in, n_legs_out, typ, "" if phase is None else phase)
        dom, cod = typ ** n_legs_in, typ ** n_legs_out
        params = dict(dict(
            draw_as_spider=True, color="black", drawing_name=""), **params)
        Box.__init__(self, name, dom, cod, **params)

    def __repr__(self):
        return factory_name(type(self)) + "({}, {}, {}{})".format(
            len(self.dom), len(self.cod), repr(self.typ),
            "" if self.phase is None else repr(phase))

    def dagger(self):
        phase = None if self.phase is None else -self.phase
        return type(self)(len(self.cod), len(self.dom), self.typ, phase)

    def rotate(self, left=False):
        del left
        return type(self)(len(self.cod), len(self.dom), self.typ, self.phase)

    def unfuse(self, factory=None) -> Diagram:
        factory = factory or type(self)
        a, b, x = len(self.dom), len(self.cod), self.typ
        if self.phase is not None:  # Coherence for phase shifters.
            return factory(a, 1, x).unfuse()\
                >> factory(1, 1, x, self.phase)\
                >> factory(1, b, x).unfuse()
        if (a, b) in [(0, 1), (1, 0), (2, 1), (1, 2)]:
            return self
        if (a, b) == (1, 1):  # Speciality: one-to-one spiders are identity.
            return self.id(self.dom)
        if a < b:  # Cut the work in two.
            return self.dagger().unfuse().dagger()
        if b != 1:
            return factory(a, 1, x).unfuse() >> factory(1, b, x).unfuse()
        if a % 2:  # We can now assume a is odd and b == 1.
            return factory(a - 1, 1, x).unfuse() @ x\
                >> factory(2, 1, x).unfuse()
        # We can now assume a is even and b == 1.
        half_spiders = factory(a // 2, 1, x).unfuse()
        return half_spiders @ half_spiders >> factory(2, 1, x)


class Category(compact.Category):
    """
    A hypergraph category is a compact category with a method :code:`spiders`.

    Parameters:
        ob : The objects of the category, default is :class:`Ty`.
        ar : The arrows of the category, default is :class:`Diagram`.
    """
    ob, ar = Ty, Diagram


class Functor(compact.Functor):
    """
    A hypergraph functor is a compact functor that preserves spiders.

    Parameters:
        ob (Mapping[Ty, Ty]) : Map from atomic :class:`Ty` to :code:`cod.ob`.
        ar (Mapping[Box, Diagram]) : Map from :class:`Box` to :code:`cod.ar`.
        cod (Category) : The codomain of the functor.
    """
    dom = cod = Category()

    def __call__(self, other):
        if isinstance(other, Spider):
            return self.cod.ar.spiders(
                len(other.dom), len(other.cod), self(other.typ))
        return super().__call__(other)


Diagram.cup_factory, Diagram.cap_factory = Cup, Cap
Diagram.braid_factory, Diagram.spider_factory = Swap, Spider

Id = Diagram.id

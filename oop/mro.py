#!/usr/bin/env python
#-*-coding=utf-8-*-

#tabstop=4 softtabstop=4 shiftwidth=4

'''
MRO(Method Resolution Order)
In object-oriented programming languages with multiple inheritance, the diamond problem (sometimes referred to as the “deadly diamond of death”) is an ambiguity that arises when two classes B and C inherit from A, and class D inherits from both B and C. If D calls a method defined in A (and does not override the method), and B and C have overridden that method differently, then from which class does it inherit: B, or C?

'''

O = object
class A(O):pass
class B(O):pass
class X(A,B):pass
class Y(B,A):pass

#[<class '__main__.X'>, <class '__main__.A'>, <class '__main__.B'>, <type 'object'>]
print X.mro()
#[<class '__main__.Y'>, <class '__main__.B'>, <class '__main__.A'>, <type 'object'>]
print Y.mro()

'''
Traceback (most recent call last):
    File "mro.py", line 23, in <module>
        class Error(X,Y):pass
    TypeError: Error when calling the metaclass bases
        Cannot create a consistent method resolution
        order (MRO) for bases B, A
'''
class Error(X,Y):pass

# -*- coding: utf-8 -*-
"""
dcm - Direction Cosine Matric (DCM) class for Astrodynamic Toolkit

Copyright (c) 2017 - Michael Kessel (mailto: the.rocketredneck@gmail.com)
a.k.a. RocketRedNeck, RocketRedNeck.com, RocketRedNeck.net 

RocketRedNeck and MIT Licenses 

RocketRedNeck hereby grants license for others to copy and modify this source code for 
whatever purpose other's deem worthy as long as RocketRedNeck is given credit where 
where credit is due and you leave RocketRedNeck out of it for all other nefarious purposes. 

Permission is hereby granted, free of charge, to any person obtaining a copy 
of this software and associated documentation files (the "Software"), to deal 
in the Software without restriction, including without limitation the rights 
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions: 

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software. 

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
SOFTWARE. 
**************************************************************************************************** 
"""

import numpy as np
from Astro import Quaternion

class dcm(np.ndarray):
    '''
    % DCM       Direction Cosine Matrix (DCM) constructor
    %           Creates a dcm object which conforms to DCM mathematics and allows
    %           operations on a series of DCMs (N, used to represent a time varying
    %           DCM).
    %
    % Usage:    M = dcm;           % Template
    %           M = dcm(x);
    %           M = dcm(x,option);
    %
    % Inputs:   x     Any of the following forms:
    %                     (3x3)xN double
    %                     3x3 (assumes N=1)
    %                     9xN double (stacked DCM, see option)
    %                     4xN double (assumed quaternion)
    %                     quaternion
    %                     dcm
    %
    %           option   Either 'rows' (default) or 'columns' indicating the 9xN
    %                    form is to be interpreted as stack transposed rows, or
    %                    stacked columns, respectively.
    %
    % Outputs:  M     The dcm object.
    %
    % See also quaternion
    %
    %==============================================================================
    '''
    def __new__(cls,data=None, **kwargs):
        # Most common issue in here is the dimension of the inputs
        # Crease an exception we can just reference for convenience
        dimError = ValueError('Only Nx3x3, Nx1x4, Nx1x9, dcm, or quaternion allowed.')

        if data is None:
            data = np.zeros([1,3,3])
            data[:,0,0] = 1
            data[:,1,1] = 1
            data[:,2,2] = 1
            
        # If a quaternion was passed in, just return it at exit
        # All other type cases require more scrutiny

        inType = type(data)
        if (issubclass(inType,dcm)):
            d = data
        elif (issubclass(inType,list) or
              issubclass(inType,np.ndarray)):
            
           # TODO: If data has units, strip the units they are not required
                            
            d = np.array(data).view(cls)
            
            # Parse the dimensions to fiqure out what we have
            # t slices (in "time" or sequence)
            # r rows
            # c columns
            numDim = len(d.shape)
            
            if (numDim < 2):
                raise dimError
                
            if (numDim < 3):
                t = 1
                d = d[np.newaxis,...]
            else:
                t = d.shape[0]
                
            r = d.shape[1]
            c = d.shape[2]
            
            if ((r==3) and (c==3)):
                # The object already looks like a 3x3 DCM
                # we won't assess the normality, just pass it back
                pass
            elif ((r==1) and (c==4)):
                # Object looks like a tx1x4 stream of quaternions
                # We don't assess normality, we just convert element
                # by element
                q = d
                qsq = q ** 2
                q01 = q[:,0] * q[:,1]
                q02 = q[:,0] * q[:,2]
                q03 = q[:,0] * q[:,3]
                q12 = q[:,1] * q[:,2]
                q13 = q[:,1] * q[:,3]
                q23 = q[:,2] * q[:,3]
                
                d = np.ndarray([t, 3, 3]);
                d[:,0,0] = 1 - 2*(qsq[:,2]+qsq[:,3])
                d[:,0,1] = 2*(q12 - q03)
                d[:,0,2] = 2*(q13 + q02)
                d[:,1,0] = 2*(q12 + q03)
                d[:,1,1] = 1 - 2*(qsq[:,3]+qsq[:,1])
                d[:,1,2] = 2*(q23 - q01)
                d[:,2,0] = 2*(q13 - q02)
                d[:,2,1] = 2*(q23 + q01)
                d[:,2,2] = 1 - 2*(qsq[:,1]+qsq[:,2])
            elif ((r==1) and (c==9)):
                # Parse the keyword arguments, extracting what makes sense
                # and tossing what doesn't
                rowcol = None
                for key in kwargs:
                    if (key.lower() == 'direction'):
                        rowcol = kwargs[key]
                
                if (issubclass(type(rowcol),str)):
                    if (rowcol.lower() != 'columns'):
                        raise ValueError('direction must be either "rows" or "columns"')
                else:
                    rowcol = 'rows'
                
                if (rowcol == 'columns'):
                    d = d[:,:,(0, 3, 6, 1, 4, 7, 2, 5, 8)]
                
                d = d.reshape([t,3,3])             
                
            else:
                raise dimError
            
        else:
            raise TypeError('Input must be derived from list, np.array, dcm, or quaternion')
            
        return d

    def __repr__(self):
        s = repr(self.__array__()).replace('array', 'dcm')
        # now, 'dcm' has 3 letters, and 'array' 5, so the columns don't
        # line up anymore. We need to remove two spaces
        l = s.splitlines()
        for i in range(1, len(l)):
            if l[i]:
                l[i] = l[i][2:]
        return '\n'.join(l)
    
    '''
    transpose - a DCM transpose that follows our stacking rules
    
    NOTE: Can also use the ~ operator (inverse)
    '''
    def transpose(self):
        # If the user sliced off the t (sequence) axis we need to
        # only transpose the axes present in the correct order
        if (len(self.shape) < 3):
            return super(dcm,self).transpose().view(dcm)
        else:
            return super(dcm,self).transpose(0, 2, 1).view(dcm)

    '''
    det - determinant of dcm
    Necessary but not sufficient condition is that abs(det(dcm)) = 1
    [[a b c]
     [d e f]
     [g h i]]
    
    det = aei + bfg + cdh - ceg - bdi - afh
    '''
    def det(self):
        if (len(self.shape) < 3):
            return (self[0,0]*self[1,1]*self[2,2] +
                    self[0,1]*self[1,2]*self[2,0] +
                    self[0,2]*self[1,0]*self[2,1] -
                    self[0,2]*self[1,1]*self[2,0] -
                    self[0,1]*self[1,0]*self[2,2] -
                    self[0,0]*self[1,2]*self[2,1])
        else:              
            return (self[:,0,0]*self[:,1,1]*self[:,2,2].view(np.ndarray) +
                    self[:,0,1]*self[:,1,2]*self[:,2,0].view(np.ndarray) +
                    self[:,0,2]*self[:,1,0]*self[:,2,1].view(np.ndarray) -
                    self[:,0,2]*self[:,1,1]*self[:,2,0].view(np.ndarray) -
                    self[:,0,1]*self[:,1,0]*self[:,2,2].view(np.ndarray) -
                    self[:,0,0]*self[:,1,2]*self[:,2,1].view(np.ndarray))
    '''
        diagonal - return the diagonal of each DCM as an array
    '''
    def diagonal(self):
        if (len(self.shape) < 3):
            return np.array((self[0,0], self[1,1], self[2,2]))
        else:
            return np.array((self[:,0,0], self[:,1,1], self[:,2,2]))
    
    '''
        trace - sum of diagonal
    '''
    def trace(self):
        return sum(self.diagonal())
    
    '''
        orthonormal - returns True for each DCM in a stack that is sufficiently
        orthogonal and normal as determined by the rss of the associated quaternion
        being sufficiently close to 1.0
        Default tolerance is 1e-9
    '''
    
    def orthonormal(self,tolerance=1.0e-9):
        # The simplest thing to do is let the quaternion do the work
        # Not sure if this is the fastest way, but it is the easiest
        return Quaternion.quaternion(self).orthonormal()
    
    # -------------------------------------------------------------------
    # Operator Overloads
    # 
    # Returns NotImplemented for anything that does not make sense
    # -------------------------------------------------------------------
    '''
        object.__add__(self, other)                 +
    '''
    def __add__(self,b):
        return NotImplemented

    '''
        object.__sub__(self, other)                 -
    '''
    def __sub__(self,b):
        return NotImplemented

    '''
        object.__mul__(self, other)                 *
    '''
    def __mul__(self,b):
        return self.__matmul__(b)
    
    '''
        object.__matmul__(self, other)              @
    '''
    def __matmul__(self, b):
        inType = type(b)
        if (issubclass(inType,dcm)):
            return np.matmul(self,b).view(dcm)
        elif (issubclass(inType,list) or
              issubclass(inType,np.ndarray)):
            # TODO: Need to implement matric vector logic
            return NotImplemented
        else:
            raise TypeError('Target type must be a dcm')

    '''
        object.__truediv__(self, other)             /
    '''
    def __truediv__(self,b):
        return NotImplemented

    '''
        object.__floordiv__(self, other)            //
    '''
    def __floordiv__(self,b):
        return NotImplemented
    '''
        object.__mod__(self, other)                 %
    '''
    def __mod__(self,b):
        return NotImplemented
    '''
        object.__divmod__(self, other)              divmod()
    '''
    def __divmod__(self,b):
        return NotImplemented
    '''
        object.__pow__(self, other[, modulo])       pow(), **
    '''
    def __pow__(self,b,*args):
        return NotImplemented
    
    '''
        object.__lshift__(self, other)              <<
    '''
    def __lshift__(self,b):
        return NotImplemented
    
    '''
        object.__rshift__(self, other)              >>
    '''
    def __rshift__(self,b):
        return NotImplemented
    

    '''
        object.__and__(self, other)                 &
    '''
    def __and__(self,b):
        return NotImplemented
    

    '''
        object.__xor__(self, other)                 ^
    '''
    def __xor__(self,b):
        return NotImplemented
    

    '''
        object.__or__(self, other)                  |
    '''
    def __or__(self,b):
        return NotImplemented
    

    '''
        
        Backup functions when left side is not of the correct type
        object.__radd__(self, other)                +
    '''
    def __radd__(self,b):
        return NotImplemented
    

    '''
        object.__rsub__(self, other)                -
    '''
    def __rsub__(self,b):
        return NotImplemented
    

    '''
        object.__rmul__(self, other)                *
    '''
    def __rmul__(self,b):
        return NotImplemented
    

    '''
        object.__rmatmul__(self, other)             @
    '''
    def __rmatmul__(self,b):
        return NotImplemented
    

    '''
        object.__rtruediv__(self, other)            /
    '''
    def __rtruediv__(self,b):
        return NotImplemented
    

    '''
        object.__rfloordiv__(self, other)           //
    '''
    def __rfloordiv__(self,b):
        return NotImplemented
    

    '''
        object.__rmod__(self, other)                %
    '''
    def __rmod__(self,b):
        return NotImplemented
    

    '''
        object.__rdivmod__(self, other)             divmod()
    '''
    def __rdivmod__(self,b):
        return NotImplemented

    '''
        object.__rpow__(self, other)                pow(), **
    '''
    def __rpow__(self,b):
        return NotImplemented
    

    '''
        object.__rlshift__(self, other)             <<
    '''
    def __rlshift__(self,b):
        return NotImplemented
    

    '''
        object.__rrshift__(self, other)             >>
    '''
    def __rrshift__(self,b):
        return NotImplemented


    '''
        object.__rand__(self, other)                &
    '''
    def __rand__(self,b):
        return NotImplemented
    

    '''
        object.__rxor__(self, other)                ^
    '''
    def __rxor__(self,b):
        return NotImplemented
    

    '''
        object.__ror__(self, other)                 |        
    '''
    def __ror__(self,b):
        return NotImplemented
    

    '''
        object.__iadd__(self, other)                +=
    '''
    def __iadd__(self,b):
        return NotImplemented
    

    '''
        object.__isub__(self, other)                -=
    '''
    def __isub__(self,b):
        return NotImplemented
    

    '''
        object.__imul__(self, other)                *=
    '''
    def __imul__(self,b):
        return NotImplemented
    

    '''
        object.__imatmul__(self, other)             @=
    '''
    def __imatmul__(self,b):
        return NotImplemented
    

    '''
        object.__itruediv__(self, other)            /=
    '''
    def __itruediv__(self,b):
        return NotImplemented
    

    '''
        object.__ifloordiv__(self, other)           //=
    '''
    def __ifloordiv__(self,b):
        return NotImplemented
    

    '''
        object.__imod__(self, other)                %=
    '''
    def __imod__(self,b):
        return NotImplemented
    

    '''
        object.__ipow__(self, other[, modulo])      **=
    '''
    def __ipow__(self,b,*args):
        return NotImplemented
    

    '''
        object.__ilshift__(self, other)             <<=
    '''
    def __ilshift__(self,b):
        return NotImplemented
    

    '''
        object.__irshift__(self, other)             >>=
    '''
    def __irshift__(self,b):
        return NotImplemented
    

    '''
        object.__iand__(self, other)                &=
    '''
    def __iand__(self,b):
        return NotImplemented
    

    '''
        object.__ixor__(self, other)                ^=
    '''
    def __ixor__(self,b):
        return NotImplemented
    

    '''
        object.__ior__(self, other)                 |=        
    '''
    def __ior__(self,b):
        return NotImplemented
    

    '''
        object.__neg__(self)                        -
    '''
    # Use superclass

    '''
        object.__pos__(self)                        +
    '''
    # Use superclass

    '''
        object.__abs__(self)                        abs()
    '''
    def __abs__(self):
        return NotImplemented
    

    '''
        object.__invert__(self)                     ~
    '''
    def __invert__(self):
        return self.transpose()

    '''
        object.__complex__(self)                    complex()
    '''
    def __complex__(self):
        return NotImplemented
    

    '''
        object.__int__(self)                        int()
    '''
    def __int__(self):
        return NotImplemented
    

    '''
        object.__float__(self)                      float()
    '''
    def __float__(self):
        return NotImplemented
    

    '''
        object.__round__(self[, n])                 round()
    '''
    def __round__(self, *args):
        return NotImplemented
    

    '''
        object.__index__(self)                      operator.index()
    '''    
    # Use superclass                 
                    
                    
                    

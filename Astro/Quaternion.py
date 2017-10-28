# -*- coding: utf-8 -*-
"""
quaternion - Quaternion class for Astrodynamic Toolkit

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
from Astro import Dcm

class quaternion(np.ndarray):
    '''
    % QUATERNION Quaternion constructor.
    %           Creates a quaternion object which conforms to quaternion mathematics
    %           and allows operations on a series of quaternions (N, used to
    %           represent a time varying quaternion).
    %
    % Usage:    q = quaternion;        % Template
    %           q = quaternion(x);
    %           q = quaternion(x,option);
    %           [theta,lambda] = quaternion(x);
    %           [theta,lambda] = quaternion(x,option2);
    %           [theta,lambda] = quaternion(x,option,option2);
    %           [theta,lambda] = quaternion(x,option2,option);
    %
    % Inputs:   x     Any of the following forms:
    %                     3x3 (assumes N=1)
    %                     9xN double (stacked DCM, see option)
    %                     4xN double (assumed quaternion, see Notes)
    %                     quaternion
    %                     dcm
    %                     1xN double (eigenangle, see option)
    %
    %           direction Either 'rows' (default) or 'columns' indicating the 9xN
    %                     form is to be interpreted as stack transposed rows, or stacked
    %                     columns, respectively.
    %
    %                    or
    %
    %           eigenvector 3xN double when eigenangle specified as x
    %
    %           option2  Used to specify if theta should be dataunit. A string
    %                    corresponding to a valid angular unit (e.g., 'rad', 'deg').
    %
    % Outputs:  q        The quaternion object
    %
    %           theta    The eigenangle (1xN double (radians) or dataunit)
    %
    %           lambda   The eigenvector (3xN double)
    %
    % Notes:    The indexing of the quaternion is assumed be as follows:
    %           q(1) = cos(theta/2)
    %           q(2:4) = lambda*sin(theta/2)
    %
    % See also  dcm
    %
    %==============================================================================
    '''        
    def __new__(cls,data=None, **kwargs):
        # Most common issue in here is the dimension of the inputs
        # Crease an exception we can just reference for convenience
        dimError = ValueError('Only 3x3xN, 4xN, 9xN, dcm, or quaternion allowed.')
        
        if data is None:
           data = np.zeros([1,1,4])
           data[:,:,0] = 1
           data[:,:,1] = 0
           data[:,:,2] = 0 
           data[:,:,3] = 0
            
        # If a quaternion was passed in, just return it at exit
        # All other type cases require more scrutiny

        inType = type(data)
        if (issubclass(inType,quaternion)):
            q = data
        elif (issubclass(inType,list) or
              issubclass(inType,np.ndarray)):
                
            # TODO: If data has units, strip the units they are not required
                
            q = np.array(data).view(cls)
            
            # Parse the dimensions to fiqure out what we have
            # t slices (in "time" or sequence)
            # r rows
            # c columns
            numDim = len(q.shape)
            
            if (numDim < 2):
                raise dimError
                
            if (numDim < 3):
                t = 1
                q = q[np.newaxis,...]
            else:
                t = q.shape[0]
                
            r = q.shape[1]
            c = q.shape[2]
            
            # Things that look like DCM should be converted and processed
            # with Shepperd's method (c. 1978 Journal of Guidance, Control, and Dynamics) 
            # to reduce affects of singularities
            #
            # The following c-style code exemplifies the logic that will
            # be implemented using the index slicing in python
            #
            #float tr = m00 + m11 + m22
            #
            # if (tr > 0) 
            # { 
            #   float S = sqrt(tr+1.0) * 2; // S=4*qw 
            #   qw = 0.25 * S;
            #   qx = (m21 - m12) / S;
            #   qy = (m02 - m20) / S; 
            #   qz = (m10 - m01) / S; 
            # } 
            # else if ((m00 > m11)&(m00 > m22)) // m00 is max
            # { 
            #   float S = sqrt(1.0 + m00 - m11 - m22) * 2; // S=4*qx 
            #   qw = (m21 - m12) / S;
            #   qx = 0.25 * S;
            #   qy = (m01 + m10) / S; 
            #   qz = (m02 + m20) / S; 
            # } 
            # else if (m11 > m22) // m11 is max
            # { 
            #   float S = sqrt(1.0 + m11 - m00 - m22) * 2; // S=4*qy
            #   qw = (m02 - m20) / S;
            #   qx = (m01 + m10) / S; 
            #   qy = 0.25 * S;
            #   qz = (m12 + m21) / S; 
            # } 
            # else // m22 is max
            # { 
            #   float S = sqrt(1.0 + m22 - m00 - m11) * 2; // S=4*qz
            #   qw = (m10 - m01) / S;
            #   qx = (m02 + m20) / S;
            #   qy = (m12 + m21) / S;
            #   qz = 0.25 * S;
            # }            
            if ((r==1 and c==9) or (r==3 and c==3)):
                # Parse the keyword arguments, extracting what makes sense
                # and tossing what doesn't
                rowcol = None
                for key in kwargs:
                    if (key.lower() == 'direction'):
                        rowcol = kwargs[key]
                
                if (issubclass(type(rowcol),str)):
                    if (rowcol.lower() != 'columns'):
                        raise ValueError('direction must be either rows or columns')
                else:
                    rowcol = 'rows'
                    
                d = Dcm.dcm(data,direction=rowcol)
                
                diagonal = d.diagonal()

                trace = sum(diagonal)
                idx_trace_positive = np.where(trace > 0)[0]

                # Numpy does not provide a function that returns
                # both the index and the max value, but since we don't
                # really need to max values in this algorithm we can just
                # use the index function
                idx_diag_max = np.argmax(diagonal,axis=0)
                
                # Avoid duplication of trace positive with one of the
                # dominant diagonals
                idx0 = np.setdiff1d(np.where(idx_diag_max == 0)[0], idx_trace_positive)
                idx1 = np.setdiff1d(np.where(idx_diag_max == 1)[0], idx_trace_positive)
                idx2 = np.setdiff1d(np.where(idx_diag_max == 2)[0], idx_trace_positive)
                
                q = np.nan * np.zeros((t,1,4))
                
                if (idx_trace_positive.shape[0] != 0):      # Where the trace is dominant
 
                    m = d[idx_trace_positive].view(np.ndarray)

                    S = 2.0 * np.sqrt(trace[idx_trace_positive] + 1.0)
                                    
                    q[idx_trace_positive,0,0] = 0.25 * S
                    q[idx_trace_positive,0,1] = (m[:,2,1] - m[:,1,2]) / S
                    q[idx_trace_positive,0,2] = (m[:,0,2] - m[:,2,0]) / S
                    q[idx_trace_positive,0,3] = (m[:,1,0] - m[:,0,1]) / S
                    
                if (idx0.shape[0] != 0):                    # Where m00 is dominant
                    
                    m = d[idx0].view(np.ndarray)
                    
                    S = 2.0 * np.sqrt(1.0 + m[:,0,0] - m[:,1,1] - m[:,2,2])
                     
                    q[idx0,0,0] = (m[:,2,1] - m[:,1,2]) / S
                    q[idx0,0,1] = 0.25 * S
                    q[idx0,0,2] = (m[:,0,1] + m[:,1,0]) / S
                    q[idx0,0,3] = (m[:,0,2] + m[:,2,0]) / S
            
                if (idx1.shape[0] != 0):                    # Where m11 is dominant
                    
                    m = d[idx1].view(np.ndarray)
                    
                    S = 2.0 * np.sqrt(1.0 + m[:,1,1] - m[:,0,0] - m[:,2,2])
                    
                    q[idx1,0,0] = (m[:,0,2] - m[:,2,0]) / S
                    q[idx1,0,1] = (m[:,0,1] + m[:,1,0]) / S
                    q[idx1,0,2] = 0.25 * S
                    q[idx1,0,3] = (m[:,1,2] + m[:,2,1]) / S
                        
                if (idx2.shape[0] != 0):                    # Where m22 is dominant
                    
                    m = d[idx2].view(np.ndarray)
                    
                    S = 2.0 * np.sqrt(1.0 + m[:,2,2] - m[:,0,0] - m[:,1,1])
                    
                    q[idx2,0,0] = (m[:,1,0] - m[:,0,1]) / S
                    q[idx2,0,1] = (m[:,0,2] + m[:,2,0]) / S
                    q[idx2,0,2] = (m[:,1,2] + m[:,2,1]) / S
                    q[idx2,0,3] = 0.25 * S
                
                
        else:
            raise TypeError('Input must be derived from list, np.array, dcm, or quaternion')
            
        return q.view(quaternion)

    def eigenangle(self):
        return 2.0*np.arccos(self[:,0,0]).view(np.ndarray)
    
    def eigenaxis(self):
        lam = self[:,0,1:4].view(np.ndarray)
        div = np.sqrt(np.sum(lam * lam, axis=1))[...,np.newaxis]
        lam = lam / div
        return lam
    
    def __repr__(self):
        s = repr(self.__array__()).replace('array', 'quaternion')
        # now, 'quaternion' has 10 letters, and 'array' 5, so the columns don't
        # line up anymore. We need to add 5 spaces
        l = s.splitlines()
        for i in range(1, len(l)):
            if l[i]:
                l[i] = "     " + l[i]
        return '\n'.join(l)

    '''
    transpose - a quaternion transpose that follows our stacking rules
    
    NOTE: Can also use the ~ operator (inverse)
    '''
    def transpose(self):
        # If the user sliced off the t (sequence) axis we need to
        # only transpose the axes present in the correct order
        if (len(self.shape) < 3):
            return 
        else:
            return 
     
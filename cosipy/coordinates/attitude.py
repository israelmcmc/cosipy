from astropy.coordinates import (TimeAttribute, Attribute, EarthLocationAttribute,
                                 ICRS, CartesianRepresentation, SkyCoord, UnitSphericalRepresentation)
import astropy.units as u

import numpy as np

from abc import ABC, abstractmethod

from scipy.spatial.transform import Rotation

class Attitude:
    """
    Orientation of the spacecraft with respect to an inertial reference frame.

    Parameters
    ----------
    rot : :py:class:`scipy.spatial.transform.Rotation`
        Rotation transformation from a :py:class:`.SpacecraftFrame` to the reference inertial
        reference frame
    frame : :py:class:`astropy.coordinates.BaseCoordinateFrame`
        Inertial reference frame
    """
    
    def __init__(self, rot, frame = None):
        
        self._rot = rot

        if frame is None:
            self._frame = 'icrs'
        else:
            self._frame = frame

    @property
    def rot(self):
        """
        Rotation object.

        Returns
        -------
        :py:class:`scipy.spatial.transform.Rotation`
        """
        
        return self._rot
            
    @property
    def frame(self):
        """
        Intertial reference frame.

        Returns
        -------
        :py:class:`astropy.coordinates.BaseCoordinateFrame`
        """
        
        return self._frame
    
    @classmethod
    def from_quat(cls, quat, frame = None):
        """
        Construct rotation from an unit-norm quaternion.

        Parameters
        ----------
        quat : array-like shaped (N, 4) or (4,)
            Each row is a (possibly non-unit norm) quaternion in scalar-last (x, y, z, w)
            format. Each quaternion will be normalized to unit norm.
        frame : :py:class:`astropy.coordinates.BaseCoordinateFrame`
            Inertial reference frame

        Returns
        -------
        :py:class:`Attitude`
        """
        
        return cls(Rotation.from_quat(quat), frame)

    @classmethod
    def from_matrix(cls, matrix, frame = None):
        """
        Construct rotation from an rotation matrix.

        Parameters
        ----------
        matrix : array-like shaped shape (N, 3, 3) or (3, 3)
            A single matrix or a stack of matrices, where matrix[i] is the i-th matrix.
        frame : :py:class:`astropy.coordinates.BaseCoordinateFrame`
            Inertial reference frame

        Returns
        -------
        :py:class:`Attitude`
        """

        return cls(Rotation.from_matrix(matrix), frame)
        
    @classmethod
    def from_rotvec(cls, rotvec, frame = None):
        """
        Construct rotation from a 3 dimensional vector which is co-directional to the
        axis of rotation and whose norm gives the angle of rotation.

        Parameters
        ----------
        rotvec : :py:class:`astropy.units.Quantity` shape (N, 3) or (3,)
            A single vector or a stack of vectors, with angular units,
            where rotvec[i] gives the ith rotation vector.
        frame : :py:class:`astropy.coordinates.BaseCoordinateFrame`
            Inertial reference frame

        Returns
        -------
        :py:class:`Attitude`
        """

        return cls(Rotation.from_rotvec(rotvec.to_value(u.rad)), frame)

    @classmethod
    def from_axes(cls, x = None, y = None, z = None, frame = None):
        """
        Construct rotation based on the sky coordinates the :py:class:`.SpacecraftFrame`
        axes point to. 

        Specify at least 2 axes. The third axes is implicit based on the right-hand rule.
        
        Parameters
        ----------
        x : :py:class:`astropy.coordinates.BaseRepresentation`, optional
            Coordinate in the inertial reference frame that the spacecraft reference frame
            x-axis is pointing to.
        y : :py:class:`astropy.coordinates.BaseRepresentation`, optional
            Coordinate in the inertial reference frame that the spacecraft reference frame
            y-axis is pointing to.
        z : :py:class:`astropy.coordinates.BaseRepresentation`, optional
            Coordinate in the inertial reference frame that the spacecraft reference frame
            z-axis is pointing to.
        frame : :py:class:`astropy.coordinates.BaseCoordinateFrame`
            Inertial reference frame

        Returns
        -------
        :py:class:`Attitude`
        """

        if len([i for i in [x,y,z] if i is None]) > 1:
            raise ValueError("At least two axes are needed.")
        
        # Get the missing axis if needed
        if x is None:
            x = y.cross(x)
        elif y is None:
            y = z.cross(x)
        elif z is None:
            z = x.cross(y)

        # Get the rotation matrix. Each axis is a row. Transpose = inverted rot
        matrix = np.transpose([x.to_cartesian().xyz.value,
                               y.to_cartesian().xyz.value,
                               z.to_cartesian().xyz.value])

        return cls.from_matrix(matrix, frame = frame)

    @classmethod
    def identity(cls, frame = None):
        """
        Attitude that represents the spacecraft coordinate aligned with the internal frame

        Parameters
        ----------
        frame : :py:class:`astropy.coordinates.BaseCoordinateFrame`
            Inertial reference frame

        Returns
        -------        
        :py:class:`Attitude`
        """
        
        return cls(Rotation.identity(), frame = frame)

    def inv(self):
        """
        Inverse transformation.

        Returns
        -------        
        :py:class:`Attitude`
        """
        
        return Attitude(self.rot.inv(), frame = self.frame)
    
    def transform_to(self, frame):
        """
        Return the attitude with respect to different inertial reference frame.

        Parameters
        ----------
        frame : :py:class:`astropy.coordinates.BaseCoordinateFrame`
            Inertial reference frame

        Returns
        -------        
        :py:class:`Attitude`        
        """
        
        if self.frame == frame:
            return self
        
        # Each row of a rotation matrix is composed of the unit vector along
        # each axis on the new frame. We then convert each of this to the new frame,
        # resulting on a new rotation matrix
        
        old_rot = CartesianRepresentation(x = self.rot.as_matrix().transpose())
        
        new_rot = SkyCoord(old_rot, frame = self.frame).transform_to(frame)

        new_rot = new_rot.represent_as('cartesian').xyz.value.transpose()

        return self.from_matrix(new_rot, frame = frame)

    def as_matrix(self):
        """
        Represent as rotation matrix.

        Returns
        -------
            array, shape (3, 3) or (N, 3, 3)
        """
        
        return self.rot.as_matrix()

    def as_rotvec(self):
        """
        Represent as rotation vectors.

        Returns
        -------
            :py:class:`astropy.units.Quantity`, shape (3,) or (N, 3)        
        """
        return self.rot.as_rotvec()*u.rad

    def as_quat(self):
        """
        Represent as quaternion with a (x, y, z, w) format.

        Returns
        -------
            array, shape (4,) or (N, 4)        
        """
        
        return self.rot.as_quat()
    
    @property
    def shape(self):
        """
        Shape of the stack of rotations.

        Returns
        -------
        array
        """
        return np.asarray(self.rot).shape

    def __getitem__(self, key):
        return self.rot[key]

    def __setitem__(self, key, value):
        self.rot[key] = value.transform_to(self.frame)._rot

    def __str__(self):
        return f"<quat = {self.rot.as_quat()}, frame = {self.frame}>"

    
class AttitudeAttribute(Attribute):
    """
    Interface for attitude with astropy's custom :py:class:`.SpacecraftFrame`
    """
    
    def convert_input(self, value):

        if value is None:
            return None, False
        
        if not isinstance(value, Attitude):
            raise ValueError("Attitude is not an instance of Attitude.")
            
        converted = True
                        
        return value,converted
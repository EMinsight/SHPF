import numpy as np
from scipy.constants import c, mu_0, epsilon_0

class Structure:

    def __init__(self, name, space):
        
        """Define structure object.

        This script is not perfect because it cannot put dispersive materials.
        Only simple isotropic dielectric materials are possible.
        """
    
        self.name = name
        self.space = space

    def _get_local_x_loc(self, gxsrts, gxends):
        """Each node get the local x location of the structure.

        Parameters
        ----------
        gxsrts: float
            global x start point of the structure.

        gxends: float
            global x end point of the structure.

        Returns
        -------
        gxloc: tuple.
            global x location of the structure.
        lxloc: tuple.
            local x location of the structure in each node.
        """

        assert gxsrts >= 0
        assert gxends < self.space.Nx

        # Global x index of the border of each node.
        bxsrt = self.space.myNx_indice[self.space.MPIrank][0]
        bxend = self.space.myNx_indice[self.space.MPIrank][1]

        #print(self.space.MPIrank, bxsrt, bxend)

        # Initialize global and local x locations of the structure.
        gxloc = None # global x location.
        lxloc = None # local x location.

        # Front nodes that contains no structures.
        if gxsrts > bxend:
            gxloc = None
            lxloc = None

        # Rear nodes that contains no structures.
        if gxends <  bxsrt:
            gxloc = None
            lxloc = None

        # First part when the structure is small.
        if gxsrts >= bxsrt and gxsrts < bxend and gxends <= bxend:
            gxloc = (gxsrts      , gxends      )
            lxloc = (gxsrts-bxsrt, gxends-bxsrt)

        # First part when the structure is big.
        if gxsrts >= bxsrt and gxsrts < bxend and gxends > bxend:
            gxloc = (gxsrts      , bxend      )
            lxloc = (gxsrts-bxsrt, bxend-bxsrt)

        # Middle node but big.
        if gxsrts < bxsrt and gxends > bxend:
            gxloc = (bxsrt      , bxend      )
            lxloc = (bxsrt-bxsrt, bxend-bxsrt)

        # Last part.
        if gxsrts < bxsrt and gxends > bxsrt and gxends <= bxend:
            gxloc = (bxsrt      , gxends      )
            lxloc = (bxsrt-bxsrt, gxends-bxsrt)

        """
        # Global x index of each node.
        node_xsrt = self.space.myNx_indice[MPIrank][0]
        node_xend = self.space.myNx_indice[MPIrank][1]

        self.gloc = None 
        self.lloc = None 
    
        if xend <  node_xsrt:
            self.gloc = None 
            self.lloc = None 
        if xsrt <  node_xsrt and xend > node_xsrt and xend <= node_xend:
            self.gloc = ((node_xsrt          , ysrt, zsrt), (xend          , yend, zend))
            self.lloc = ((node_xsrt-node_xsrt, ysrt, zsrt), (xend-node_xsrt, yend, zend))
        if xsrt <  node_xsrt and xend > node_xend:
            self.gloc = ((node_xsrt          , ysrt, zsrt), (node_xend          , yend, zend))
            self.lloc = ((node_xsrt-node_xsrt, ysrt, zsrt), (node_xend-node_xsrt, yend, zend))
        if xsrt >= node_xsrt and xsrt < node_xend and xend <= node_xend:
            self.gloc = ((xsrt          , ysrt, zsrt), (xend          , yend, zend))
            self.lloc = ((xsrt-node_xsrt, ysrt, zsrt), (xend-node_xsrt, yend, zend))
        if xsrt >= node_xsrt and xsrt < node_xend and xend >  node_xend:
            self.gloc = ((xsrt          , ysrt, zsrt), (node_xend          , yend, zend))
            self.lloc = ((xsrt-node_xsrt, ysrt, zsrt), (node_xend-node_xsrt, yend, zend))
        if xsrt >  node_xend:
            self.gloc = None 
            self.lloc = None 
        """

        return gxloc, lxloc


class Box(Structure):

    def __init__(self, name, space, srt, end, eps_r, mu_r):
        """Set a rectangular box on a simulation space.
        
        PARAMETERS
        ----------
        name: str.
            A name of the object. Choose easy name which clearly represents this structure.
        space: space object.

        srt: tuple.

        end: tuple.

        eps_r : float
            Relative electric constant or permitivity.

        mu_ r : float
            Relative magnetic constant or permeability.
            
        Returns
        -------
        None
        """

        self.eps_r = eps_r
        self.mu_r = mu_r    

        Structure.__init__(self, name, space)

        assert len(srt) == 3, "Only 3D material is possible."
        assert len(end) == 3, "Only 3D material is possible."

        # Start index of the structure.
        xsrt = round(srt[0]/self.space.dx)
        ysrt = round(srt[1]/self.space.dy)
        zsrt = round(srt[2]/self.space.dz)

        # End index of the structure.
        xend = round(end[0]/self.space.dx)
        yend = round(end[1]/self.space.dy)
        zend = round(end[2]/self.space.dz)

        assert xsrt < xend
        assert ysrt < yend
        assert zsrt < zend

        um = 1e-6
        nm = 1e-9

        #if space.MPIrank == 0:
        #    print("Box size: x={:.4f} um, y={:.4f} um, z={:.4f} um" \
        #        .format((end[0]-srt[0])/um, (end[1]-srt[1])/um, (end[2]-srt[2])/um))

        self.gxloc, self.lxloc = Structure._get_local_x_loc(self, xsrt, xend)

        self.ysrt, self.yend = ysrt, yend
        self.zsrt, self.zend = zsrt, zend

        if self.gxloc != None:

            rank = self.space.MPIrank
            gxsrt = self.lxloc[0]
            gxend = self.lxloc[1]

            lxsrt = self.lxloc[0]
            lxend = self.lxloc[1]

            #print(f"rank {rank:>2}: \n\
#\tx idx >>> global {gxsrt:4d},{gxend:4d} and local {lxsrt:4d},{lxend:4d}\n\
#\ty idx >>> global {ysrt:4d},{yend:4d}\n\
#\tz idx >>> global {zsrt:4d},{zend:4d}")

            self.space.eps_Ex[lxsrt:lxend, ysrt:yend, zsrt:zend] = self.eps_r * epsilon_0
            self.space.eps_Ey[lxsrt:lxend, ysrt:yend, zsrt:zend] = self.eps_r * epsilon_0
            self.space.eps_Ez[lxsrt:lxend, ysrt:yend, zsrt:zend] = self.eps_r * epsilon_0

            self.space. mu_Hx[lxsrt:lxend, ysrt:yend, zsrt:zend] = self. mu_r * mu_0
            self.space. mu_Hy[lxsrt:lxend, ysrt:yend, zsrt:zend] = self. mu_r * mu_0
            self.space. mu_Hz[lxsrt:lxend, ysrt:yend, zsrt:zend] = self. mu_r * mu_0

        return


class Cone(Structure):
    def __init__(self, space, axis, height, radius, center, eps_r, mu_r):
        """Place a rectangle inside of a simulation space.
        
        Args:
            space : space object

            axis : string
                A coordinate axis parallel to the center axis of the cone. Choose 'x','y' or 'z'.

            height : int
                A height of the cone in terms of index.

            radius : int
                A radius of the bottom of a cone.

            center : tuple
                A coordinate of the center of the bottom.

            eps_r : float
                    Relative electric constant or permitivity.

            mu_ r : float
                    Relative magnetic constant or permeability.

        Returns:
            None

        """

        self.eps_r = eps_r
        self. mu_r =  mu_r

        Structure.__init__(self, space)

        assert self.space.dy == self.space.dz, "dy and dz must be the same. For the other case, it is not developed yet."
        assert axis == 'x', "Sorry, a cone parallel to the y and z axis are not developed yet."

        assert len(center)  == 3, "Please insert x,y,z coordinate of the center."

        assert type(eps_r) == float, "Only isotropic media is possible. eps_r must be a single float."  
        assert type( mu_r) == float, "Only isotropic media is possible.  mu_r must be a single float."  

        # Global srt index of the structure.
        gxsrt = center[0] - height

        # Global end index of the structure.
        gxend = center[0]

        assert gxsrt >= 0

        MPIrank = self.space.MPIrank
        MPIsize = self.space.MPIsize

        # Global x index of each node.
        node_xsrt = self.space.myNx_indice[MPIrank][0]
        node_xend = self.space.myNx_indice[MPIrank][1]

        if gxend <  node_xsrt:
            self.gxloc = None
            self.lxloc = None

            portion_srt  = None
            portion_end  = None
            self.portion = None

        # Last part
        if gxsrt <  node_xsrt and gxend >= node_xsrt and gxend <= node_xend:
            self.gxloc = (node_xsrt          , gxend          )
            self.lxloc = (node_xsrt-node_xsrt, gxend-node_xsrt)

            portion_srt  = height - (self.gxloc[1] - self.gxloc[0])
            portion_end  = height
            self.portion = (portion_srt, portion_end) 

            my_lxloc  = np.arange  (self.lxloc[0], self.lxloc[1] )
            my_height = np.linspace(portion_srt  , portion_end, len(my_lxloc))
            my_radius = (radius * my_height ) / height

            for i in range(len(my_radius)):
                for j in range(self.space.Ny):
                    for k in range(self.space.Nz):

                        if ((j-center[1])**2 + (k-center[2])**2) <= (my_radius[i]**2):

                            self.space.eps_Ex[my_lxloc[i], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ey[my_lxloc[i], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ez[my_lxloc[i], j, k] = self.eps_r * epsilon_0

                            self.space. mu_Hx[my_lxloc[i], j, k] = self. mu_r * mu_0
                            self.space. mu_Hy[my_lxloc[i], j, k] = self. mu_r * mu_0
                            self.space. mu_Hz[my_lxloc[i], j, k] = self. mu_r * mu_0

        # Middle part
        if gxsrt <= node_xsrt and gxend >= node_xend:
            self.gxloc = (node_xsrt          , node_xend          )
            self.lxloc = (node_xsrt-node_xsrt, node_xend-node_xsrt)

            portion_srt  = self.gxloc[0] - gxsrt
            portion_end  = portion_srt + (node_xend - node_xsrt)
            self.portion = (portion_srt, portion_end) 

            my_lxloc  = np.arange  (self.lxloc[0], self.lxloc[1] )
            my_height = np.linspace(portion_srt  , portion_end, len(my_lxloc))
            my_radius = (radius * my_height ) / height

            for i in range(len(my_radius)):
                for j in range(self.space.Ny):
                    for k in range(self.space.Nz):

                        if ((j-center[1])**2 + (k-center[2])**2) <= (my_radius[i]**2):

                            self.space.eps_Ex[my_lxloc[i], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ey[my_lxloc[i], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ez[my_lxloc[i], j, k] = self.eps_r * epsilon_0

                            self.space. mu_Hx[my_lxloc[i], j, k] = self. mu_r * mu_0
                            self.space. mu_Hy[my_lxloc[i], j, k] = self. mu_r * mu_0
                            self.space. mu_Hz[my_lxloc[i], j, k] = self. mu_r * mu_0


        # First part but small
        if gxsrt >= node_xsrt and gxsrt <= node_xend and gxend <=  node_xend:
            self.gxloc = (gxsrt          , gxend          )
            self.lxloc = (gxsrt-node_xsrt, gxend-node_xsrt)

            portion_srt  = self.lxloc[0]
            portion_end  = self.lxloc[1]
            self.portion = (portion_srt, portion_end) 

            my_lxloc  = np.arange  (self.lxloc[0], self.lxloc[1] )
            my_height = np.linspace(portion_srt  , portion_end, len(my_lxloc))
            my_radius = (radius * my_height ) / height

            for i in range(len(my_radius)):
                for j in range(self.space.Ny):
                    for k in range(self.space.Nz):

                        if ((j-center[1])**2 + (k-center[2])**2) <= (my_radius[i]**2):

                            self.space.eps_Ex[my_lxloc[i], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ey[my_lxloc[i], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ez[my_lxloc[i], j, k] = self.eps_r * epsilon_0

                            self.space. mu_Hx[my_lxloc[i], j, k] = self. mu_r * mu_0
                            self.space. mu_Hy[my_lxloc[i], j, k] = self. mu_r * mu_0
                            self.space. mu_Hz[my_lxloc[i], j, k] = self. mu_r * mu_0

        # First part but big
        if gxsrt >= node_xsrt and gxsrt <= node_xend and gxend >= node_xend:
            self.gxloc = (gxsrt          , node_xend          )
            self.lxloc = (gxsrt-node_xsrt, node_xend-node_xsrt)

            portion_srt  = 0
            portion_end  = self.gxloc[1] - self.gxloc[0]
            self.portion = (portion_srt, portion_end) 

            my_lxloc  = np.arange  (self.lxloc[0], self.lxloc[1] )
            my_height = np.linspace(portion_srt  , portion_end, len(my_lxloc))
            my_radius = (radius * my_height ) / height

            for i in range(len(my_radius)):
                for j in range(self.space.Ny):
                    for k in range(self.space.Nz):

                        if ((j-center[1])**2 + (k-center[2])**2) <= (my_radius[i]**2):

                            self.space.eps_Ex[my_lxloc[i], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ey[my_lxloc[i], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ez[my_lxloc[i], j, k] = self.eps_r * epsilon_0

                            self.space. mu_Hx[my_lxloc[i], j, k] = self. mu_r * mu_0
                            self.space. mu_Hy[my_lxloc[i], j, k] = self. mu_r * mu_0
                            self.space. mu_Hz[my_lxloc[i], j, k] = self. mu_r * mu_0

        if gxsrt >= node_xend:
                self.gxloc = None
                self.lxloc = None
            
                portion_srt  = None
                portion_end  = None
                self.portion = None

        #if self.gxloc != None:
        #   print('rank: ', MPIrank)
        #   print('Global loc: ', self.gxloc)
        #   print('Local loc: ', self.lxloc)
        #   print('height portion: ', self.portion)
        #   print('Local loc array: ', my_lxloc, len(my_lxloc))
        #   print('my height array: ', my_height, len(my_height))
        #   print('my radius array: ', my_radius, len(my_radius))

        #print(MPIrank, self.portion, self.gxloc, self.lxloc)
        self.space.MPIcomm.Barrier()

        return


class Sphere(Structure):

    def __init__(self, name, space, center, radius, eps_r, mu_r):
        """Dielectric sphere.

        Paramters
        ---------
            name: str
                the name of the object.

            space: space object.
                Choose which space object to put on.

            center: tuple
                the indices of the center of the sphere.

            radius: float
                the radius of the sphere in length unit, not indices.

            eps_r: float
                dielectric constant.

            mu_r: float
                magnetic constant.

        Returns
        -------
        None
        """

        Structure.__init__(self, name, space)

        assert len(center) == 3, "Please insert x,y,z coordinate of the center."

        assert type(eps_r) == float, "Only isotropic media is possible. eps_r must be a single float."  
        assert type( mu_r) == float, "Only isotropic media is possible.  mu_r must be a single float."  

        self.eps_r = eps_r
        self.mu_r =  mu_r
        self.radius = radius
        self.center_idx = center

        dx = self.space.dx
        dy = self.space.dy
        dz = self.space.dz

        gxsrt = center[0] - round(radius/dx) # Global srt index of the structure.
        gxend = center[0] + round(radius/dx) # Global end index of the structure.

        assert gxsrt >= 0
        assert gxend < self.space.Nx

        MPIrank = self.space.MPIrank
        MPIsize = self.space.MPIsize

        self.gxloc, self.lxloc = Structure._get_local_x_loc(self, gxsrt, gxend)

        if self.gxloc != None:      

            lxloc = np.arange(self.lxloc[0], self.lxloc[1])

            portion_srt  = self.gxloc[0] - center[0] + round(radius/dx)
            portion_end  = self.gxloc[1] - center[0] + round(radius/dx)
            self.portion = np.arange(portion_srt, portion_end)

            rx = abs(self.portion - round(radius/dx))
            rr = np.zeros_like(rx, dtype=np.float64)
            theta = np.zeros_like(rx, dtype=np.float64)

            for i in range(len(rx)):
                theta[i] = np.arccos(rx[i]*dx/radius)
                rr[i] = radius * np.sin(theta[i])

                for j in range(self.space.Ny):
                    for k in range(self.space.Nz):

                        if (((j-center[1])*dy)**2 + ((k-center[2])*dz)**2) <= (rr[i]**2):

                            self.space.eps_Ex[lxloc[i], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ey[lxloc[i], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ez[lxloc[i], j, k] = self.eps_r * epsilon_0

                            self.space. mu_Hx[lxloc[i], j, k] = self. mu_r * mu_0
                            self.space. mu_Hy[lxloc[i], j, k] = self. mu_r * mu_0
                            self.space. mu_Hz[lxloc[i], j, k] = self. mu_r * mu_0

            #print(MPIrank, self.gxloc, self.lxloc, rx, rr)

        return


class Sphere_percom(Structure):

    def __init__(self, name, space, center, radius, eps_r, mu_r):
        """Dielectric sphere.

        Paramters
        ---------
            name: str
                the name of the object.

            space: space object.
                Choose which space object to put on.

            center: tuple
                the coordinate of the center of the sphere in length unit, not indices.

            radius: float
                the radius of the sphere in length unit, not indices.

            eps_r: float
                dielectric constant.

            mu_r: float
                magnetic constant.

        Returns
        -------
        None
        """

        Structure.__init__(self, name, space)

        assert len(center) == 3, "Please insert x,y,z coordinate of the center."

        assert type(eps_r) == float, "Only isotropic media is possible. eps_r must be a single float."  
        assert type( mu_r) == float, "Only isotropic media is possible.  mu_r must be a single float."  

        dx = self.space.dx
        dy = self.space.dy
        dz = self.space.dz

        self.eps_r = eps_r
        self.mu_r =  mu_r
        self.radius = radius
        self.center_idx = (round(center[0]/dx)-1, round(center[1]/dy)-1, round(center[2]/dz)-1)
        #print(self.space.MPIrank, self.center_idx)

        # Start and End index of the sphere along x-axis.
        gxsrt = self.center_idx[0] - round(radius/dx) # Global srt index of the structure.
        gxend = self.center_idx[0] + round(radius/dx) # Global end index of the structure.

        assert gxsrt >= 0
        assert gxend < self.space.Nx

        MPIrank = self.space.MPIrank
        MPIsize = self.space.MPIsize

        # Global and Local x index of the sphere in each node.
        self.gxloc, self.lxloc = Structure._get_local_x_loc(self, gxsrt, gxend)

        if self.gxloc != None:      

            print(self.space.MPIrank, self.gxloc)
            print(self.space.MPIrank, self.lxloc)

            """
            lxloc = np.arange(self.lxloc[0], self.lxloc[1]+1)
            print(self.space.MPIrank, lxloc, len(lxloc))

            # Portion means the portion of a sphere that each node takes part in.
            portion_srt  = self.gxloc[0] - self.center_idx[0] + round(radius/dx)
            portion_end  = self.gxloc[1] - self.center_idx[0] + round(radius/dx)
            self.portion = np.arange(portion_srt, portion_end+1)

            rx = abs(self.portion - round(radius/dx))
            rrx = self.portion - round(radius/dx)

            #print(self.space.MPIrank,'rx:  ', rx)
            #print(self.space.MPIrank,'rrx: ', rrx)

            xdfcc = rrx      # x displacement from the center[0], for the centered grid point.
            xdfcs = (rrx+.5) # x displacement from the center[0], for the staggered grid point.

            #print(self.space.MPIrank,'xdfcc: ', xdfcc, len(xdfcc))
            print(self.space.MPIrank,'xdfcs: ', xdfcs, len(xdfcs))

            ydfcc = np.zeros_like(rx, dtype=np.float64)
            ydfcs = np.zeros_like(rx, dtype=np.float64)

            zdfcc = np.zeros_like(rx, dtype=np.float64)
            zdfcs = np.zeros_like(rx, dtype=np.float64)

            rr = np.zeros_like(rx, dtype=np.float64)
            theta = np.zeros_like(rx, dtype=np.float64)

            r_idx = round(radius/dx)
            #print(r_idx)

            # For Ex component.
            for i,xx in enumerate(xdfcs):

                dist = abs(xx)
                theta[i] = np.arccos(dist/radius)
                rr[i] = radius * np.sin(theta[i])

                if dist <= r_idx:

                    try: 
                        for j in range(self.space.Ny):
                            for k in range(self.space.Nz):

                                if (((j-self.center_idx[1])*dy)**2 + ((k-self.center_idx[2])*dz)**2) <= (rr[i]**2):

                                    self.space.eps_Ex[lxloc[i], j, k] = self.eps_r * epsilon_0

                    except Exception as e: 

                        pass
                        #print(self.space.MPIrank, i, xx)

                else: print(self.space.MPIrank, i, dist)

            for i in range(len(rx)):
                theta[i] = np.arccos(rx[i]*dx/radius)
                rr[i] = radius * np.sin(theta[i])

                for j in range(self.space.Ny):
                    for k in range(self.space.Nz):

                        if (((j-self.center_idx[1])*dy)**2 + ((k-self.center_idx[2])*dz)**2) <= (rr[i]**2):

                            self.space.eps_Ex[lxloc[i], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ey[lxloc[i], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ez[lxloc[i], j, k] = self.eps_r * epsilon_0

                            self.space. mu_Hx[lxloc[i], j, k] = self. mu_r * mu_0
                            self.space. mu_Hy[lxloc[i], j, k] = self. mu_r * mu_0
                            self.space. mu_Hz[lxloc[i], j, k] = self. mu_r * mu_0

            #print(MPIrank, self.gxloc, self.lxloc, rx, rr)
            """

        return


class Cylinder2D(Structure):

    def __init__(self, space, radius, center, eps_r, mu_r):
        """Cylinder object in Basic2D structure.

        Parameters
        ----------
        space: Basic2D object.
            Any two-dimensional space object.

        radius: float.

        center: tuple.
            a (x,z) or (y,z) coordinate of the center of the cylinder.

        eps_r: float.

        mu_r: float.

        Returns
        -------
        None.
   
        """

        Structure.__init__(self, space)
        assert space.dimension == 2

        self.eps_r = eps_r
        self. mu_r =  mu_r

        dx = self.space.dx
        dy = self.space.dy

        rx = center[0]/dx
        ry = center[1]/dy

        if space.mode == 'TM':

            for i in range(self.space.Nx):
                for j in range(self.space.Ny):

                    if (((i-rx)*dx)**2 + ((j-ry)*dy)**2) <= (radius**2):

                        self.space.eps_Ez[i, j] = self.eps_r * epsilon_0
                        self.space. mu_Hx[i, j] = self. mu_r * mu_0
                        self.space. mu_Hy[i, j] = self. mu_r * mu_0

        if space.mode == 'TE':

            for i in range(self.space.Nx):
                for j in range(self.space.Ny):

                    if (((i-rx)*dx)**2 + ((j-ry)*dy)**2) <= (radius**2):

                        self.space.eps_Ex[i, j] = self.eps_r * epsilon_0
                        self.space.eps_Ey[i, j] = self.eps_r * epsilon_0
                        self.space. mu_Hz[i, j] = self. mu_r * mu_0
        return


class Circle(Cylinder2D):

    def __init__(self, space, radius, center, eps_r, mu_r):
        """Circle object in Basic2D structure.
        This class inherits Cylinder2D object 
        which is effectively the same in 2D space.

        Parameters
        ----------
        space: Basic2D object.
            Any two-dimensional space object.

        radius: float.

        center: tuple.
            a (x,z) or (y,z) coordinate of the center of the cylinder.

        eps_r: float.

        mu_r: float.

        Returns
        -------
        None.
   
        """

        Cylinder2D.__init__(self, space, radius, center, eps_r, mu_r)


class Cylinder3D(Structure):

    def __init__(self, name, space, axis, radius, height, center, eps_r, mu_r):
        """Cylinder object in Basic3D structure.

        Parameters
        ----------
        name: str.

        space: space object.

        axis: string.
            An axis parallel to the cylinder.

        radius: float.

        height: float.
            a tuple with shape (xsrt,xend) showing the height of the cylinder such that (xsrt, xend).

        center: tuple.
            a (x,z) or (y,z) coordinate of the center of the cylinder.

        eps_r: float.

        mu_r: float.

        Returns
        -------
        None.
   
        """

        Structure.__init__(self, name, space)

        self.axis = axis
        self.radius = radius
        self.height = height
        self.center = center

        self.eps_r = eps_r
        self. mu_r =  mu_r

        dx = self.space.dx
        dy = self.space.dy
        dz = self.space.dz

        self.rx = None
        self.ry = None
        self.rz = None

        if axis == 'x':

            self.ry = center[0]/dy
            self.rz = center[1]/dz

            gxsrts = round(height[0]/dx)   # Global srt index of the structure.
            gxends = round(height[1]/dx) # Global end index of the structure.

            self.gxloc, self.lxloc = Structure._get_local_x_loc(self, gxsrts, gxends)

            if self.gxloc != None:      

                #print(f"Cylinder center index: (y0,z0)=({ry},{rz})")
                #print("rank {:>2}: x idx of a Cylinder >>> global \"{:4d},{:4d}\" and local \"{:4d},{:4d}\"" \
                #        .format(self.space.MPIrank, self.gxloc[0], self.gxloc[1], self.lxloc[0], self.lxloc[1]))

                for j in range(self.space.Ny):
                    for k in range(self.space.Nz):

                        if (((j-self.ry)*dy)**2 + ((k-self.rz)*dz)**2) <= (radius**2):

                            self.space.eps_Ex[self.lxloc[0]:self.lxloc[1], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ey[self.lxloc[0]:self.lxloc[1], j, k] = self.eps_r * epsilon_0
                            self.space.eps_Ez[self.lxloc[0]:self.lxloc[1], j, k] = self.eps_r * epsilon_0

                            self.space. mu_Hx[self.lxloc[0]:self.lxloc[1], j, k] = self. mu_r * mu_0
                            self.space. mu_Hy[self.lxloc[0]:self.lxloc[1], j, k] = self. mu_r * mu_0
                            self.space. mu_Hz[self.lxloc[0]:self.lxloc[1], j, k] = self. mu_r * mu_0

        elif axis == 'y':

            gxsrt = round(center[0]/dx) - round(radius/dx) # Global srt index of the structure.
            gxend = round(center[0]/dx) + round(radius/dx) # Global end index of the structure.

            if gxsrt < 0: gxsrt = 0
            if gxend >= self.space.Nx: gxend = self.space.Nx-1

            self.gxloc, self.lxloc = Structure._get_local_x_loc(self, gxsrt, gxend)

            if self.gxloc != None:      

                lxloc = np.arange(self.lxloc[0], self.lxloc[1])

                portion_srt  = self.gxloc[0] - round(center[0]/dx) + round(radius/dx)
                portion_end  = self.gxloc[1] - round(center[0]/dx) + round(radius/dx)
                self.portion = np.arange(portion_srt, portion_end)

                rx = abs(self.portion - round(radius/dx)) * dx
                rz = np.zeros_like(rx, dtype=np.float64)
                theta = np.zeros_like(rx, dtype=np.float64)

                #print(self.space.MPIrank, lxloc)

                for i in range(len(rx)):
                
                    theta[i] = np.arccos(rx[i]/radius)
                    rz[i] = radius * np.sin(theta[i])

                    for j in range(self.space.Ny):
                        for k in range(self.space.Nz):

                            if (k*dz-center[1])**2 <= rz[i]**2 and (j*dy) >= height[0] and (j*dy) <= height[1]:

                                #if i==3 and j==0: print(lxloc[i], k)

                                self.space.eps_Ex[lxloc[i], j, k] = self.eps_r * epsilon_0
                                self.space.eps_Ey[lxloc[i], j, k] = self.eps_r * epsilon_0
                                self.space.eps_Ez[lxloc[i], j, k] = self.eps_r * epsilon_0

                                self.space. mu_Hx[lxloc[i], j, k] = self. mu_r * mu_0
                                self.space. mu_Hy[lxloc[i], j, k] = self. mu_r * mu_0
                                self.space. mu_Hz[lxloc[i], j, k] = self. mu_r * mu_0

                #print(self.space.MPIrank, self.portion, self.gxloc, self.lxloc, lxloc, rx, rz, theta)

        elif axis == 'z': raise ValueError("Cylinder parallel to 'z' axis is not developed yet. Sorry.")

        return


class Cylinder3D_slab(Structure):

    def __init__(self, space, axis, radius, height, lcy, lcz, rot, rot_cen, eps_r, mu_r):
        """An array of the Cylinder3D object.

        Parameters
        ----------
        space: Space object.
            Space object to put cylinder slab.

        axis: string.
            An axis parallel to the cylinder.

        radius: float.
            a radius of the cylinders.

        height: float.
            a tuple with shape (xsrt,xend) showing the height of the cylinder such that (xsrt, xend).

        rot: float.
            a rotation angle in degree.

        rot_cen: ndarray.
            a coordinate of rotation axis.

        lcy: float.
            lattice constant along y axis.

        lcz: float.
            lattice constant along z axis.

        eps_r: float.

        mu_r: float.

        Returns
        -------
        None.
   
        """

        Structure.__init__(self, space)

        self.eps_r = eps_r
        self. mu_r =  mu_r

        dx = self.space.dx

        gxsrts = round(height[0]/dx) # Global srt index of the structure.
        gxends = round(height[1]/dx) # Global end index of the structure.

        self.gxloc, self.lxloc = Structure._get_local_x_loc(self, gxsrts, gxends)

        rot_cen = np.array(rot_cen)
        rot = np.radians(rot)
        cos, sin = np.cos(rot), np.sin(rot)
        R = np.array([[cos, -sin], [sin, cos]])

        center = np.array([self.space.Ly/2, self.space.Lz/2])

        if self.gxloc != None:      

            #Box(self.space, srt, end, eps_r, mu_r)

            j = 0
            k = 0

            #centers = []
            #cylinders = []

            numy = int(center[0]/lcy)
            numz = int(center[1]/lcz)

            for j in range(-numy, numy+1):
                for k in range(-numz, numz+1):

                    new_cen = np.array([center[0] + j*lcy, center[1] + k*lcz])
                    new_cen = R @ (new_cen - rot_cen) + rot_cen

                    Cylinder3D(self.space, axis, radius, height, new_cen, eps_r, mu_r)

                    #centers.append(center)
                    #cylinders.append(Cylinder3D(self.space, axis, radius, height, center, eps_r, mu_r))

        return


class Cylinder_slab_deprecated(Structure):

    def __init__(self, space, radius, height, llm, dc, eps_r, mu_r):
        """Cylinder object in Basic3D structure.

        Parameters
        ----------
        radius: float.

        height: float.
            a tuple with shape (xsrt,xend) showing the height of the cylinder such that (xsrt, xend).

        llm: tuple.
            (y,z) coordinate of the center of the left, lower most cylinder.

        dc: tuple.
            y,z distance between the center of each hole.

        eps_r: float.

        mu_r: float.

        Returns
        -------
        None.
   
        """

        Structure.__init__(self, space)

        self.eps_r = eps_r
        self. mu_r =  mu_r

        dx = self.space.dx
        dy = self.space.dy
        dz = self.space.dz

        gxsrts = round(height[0]/dx) # Global srt index of the structure.
        gxends = round(height[1]/dx) # Global end index of the structure.

        self.gxloc, self.lxloc = Structure._get_local_x_loc(self, gxsrts, gxends)

        if self.gxloc != None:      

            #Box(self.space, srt, end, eps_r, mu_r)

            Lx = self.space.Lx
            Ly = self.space.Ly
            Lz = self.space.Lz
            dy = self.space.dy
            dz = self.space.dz

            j = 0
            k = 0

            centers = []
            cylinders = []

            while (llm[0] + dc[0]*j) <= Ly:
                while (llm[1] + dc[1]*k) <= Lz:

                    center = (llm[0] + dc[0]*j, llm[1] + dc[1]*k)
                    centers.append(center)

                    cylinders.append(Cylinder(self.space, radius, height, center, eps_r, mu_r))

                    k += 1

                k = 0
                j += 1

        return

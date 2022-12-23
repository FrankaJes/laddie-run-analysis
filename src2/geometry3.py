import numpy as np
import xarray as xr
import pyproj

from constants import ModelConstants

class Geometry(ModelConstants):
    """Create geometry input"""
    def __init__(self,ds,name):

        self.ds = ds

        self.dx = self.ds.x[1]-self.ds.x[0]
        self.dy = self.ds.y[1]-self.ds.y[0]

        self.res = (self.ds.x[1]-self.ds.x[0]).values/1000

        if self.dx<0:
            print('inverting x-coordinates')
            self.ds = self.ds.reindex(x=list(reversed(self.ds.x)))
            self.dx = -self.dx
        if self.dy<0:
            print('inverting y-coordinates')
            self.ds = self.ds.reindex(y=list(reversed(self.ds.y)))
            self.dy = -self.dy

        #self.mask = self.ds.mask
        self.ds.mask[:] = xr.where(self.ds.mask==1,2,self.ds.mask)
        self.ds['draft'] = (self.ds.surface-self.ds.thickness).astype('float64')
        self.ds['thickness'] = self.ds.thickness.astype('float64')
        self.ds['surface'] = self.ds.surface.astype('float64')
        self.ds['bed'] = self.ds.bed.astype('float64')

        #Calving criterium
        ''' add if statement here or move to preprocess together with correctisf? '''
        self.ds['draft'][:] = np.where(np.logical_and(self.ds.mask==3,self.ds.draft>-90),0,self.ds.draft)
        self.ds['mask'][:] = np.where(np.logical_and(self.ds.mask==3,self.ds.draft>-90),0,self.ds.mask)

        self.name = name

        ModelConstants.__init__(self)
    
    def coarsen(self,N):
        """Coarsen grid resolution by a factor N"""
        self.ds['mask'] = xr.where(self.ds.mask==0,np.nan,self.ds.mask)
        self.ds['draft'] = xr.where(np.isnan(self.ds.mask),np.nan,self.ds.draft)
        self.ds = self.ds.coarsen(x=N,y=N,boundary='trim').mean()

        self.ds['mask'] = np.round(self.ds.mask)
        self.ds['mask'] = xr.where(np.isnan(self.ds.mask),0,self.ds.mask)
        self.ds['draft'] = xr.where(self.ds.mask==0,0,self.ds.draft)
        self.ds['draft'] = xr.where(np.isnan(self.ds.draft),0,self.ds.draft)
        self.res *= N
        print(f'Resolution set to {self.res} km')
        
    def smoothen(self,N):
        """Smoothen geometry"""
        for n in range(0,N):
            self.ds.draft = .5*self.ds.draft + .125*(np.roll(self.ds.draft,-1,axis=0)+np.roll(self.ds.draft,1,axis=0)+np.roll(self.ds.draft,-1,axis=1)+np.roll(self.ds.draft,1,axis=1))

    def create(self):
        """Create geometry"""
        geom = self.ds[['mask','draft','surface','thickness','bed']]
        geom['name_geo'] = f'{self.name}_{self.res:1.1f}'
        print('Geometry',geom.name_geo.values,'created')
        
        #Add lon lat
        project = pyproj.Proj("epsg:3031")
        xx, yy = np.meshgrid(geom.x, geom.y)
        lons, lats = project(xx, yy, inverse=True)
        dims = ['y','x']
        geom = geom.assign_coords({'lat':(dims,lats), 'lon':(dims,lons)})  
        return geom
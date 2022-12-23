import numpy as np
import copy

from geometry3 import Geometry
import preprocess as pp

### Nearest neighbour function
def compute_average_NN(object_variable, mask):
    """
    Compute the average of neighbouring cells masked as ice shelf. 

    INPUT:
        - object_variable: variable for which the NN average is to be computed, for example: object.T
        - mask: mask that corresponds to object_variable, for example: object.tmask
    """
    # Create nn_average array to store average nearest neighbour values
    nn_average = object_variable * 0

    for i in range(3):
        var = object_variable[i,:,:]

        # Only take values from cells within shelf mask
        vari = np.where(mask==1, var, 0)

        # Take the sum of the values in neighbouring cells for nt = 1 
        nn_total = np.roll(vari,-1,axis=0)+ np.roll(vari,1,axis=0) + np.roll(vari,-1,axis=1) + np.roll(vari,1,axis=1)

        # Compute the weight using the mask (the weight is the number of neighbouring cells which contain values within the shelf mask)
        weight = np.roll(mask,-1, axis=0)+ np.roll(mask,1, axis=0) + np.roll(mask,-1, axis=1) + np.roll(mask,1, axis=1)

        # Divide sum of neighbours by the weight and fill nn_average array
        nn_average[i,:,:] = nn_total / weight

    return nn_average

def update_geometry(object, geom_new):

    # Read in new geometry
    new_geom = Geometry(geom_new, object.geomname)
    new_geom.coarsen(N=object.N)
    new_geom = new_geom.create()
    
    # Copy object
    old_object = copy.deepcopy(object)

    # Overwrite mask, draft and zb with new geometry
    object.mask[:]     = new_geom.mask[:]
    object.ds.draft[:] = new_geom.draft[:]
    object.zb[:]       = new_geom.draft[:]
    
    # Create mask and initialize variables for new geometry
    pp.create_mask(object)
    pp.create_grid(object)
    pp.initialize_vars(object)
 
    # Inherit values for variables in grid cells that were already marked as iceshelf
    object.T[:] = np.where(np.logical_and(object.tmask==1, old_object.tmask==1), old_object.T[:], object.T[:])
    object.S[:] = np.where(np.logical_and(object.tmask==1, old_object.tmask==1), old_object.S[:], object.S[:])
    object.D[:] = np.where(np.logical_and(object.tmask==1, old_object.tmask==1), old_object.D[:], object.D[:])
    object.U[:] = np.where(np.logical_and(object.umask==1, old_object.umask==1), old_object.U[:], object.U[:])
    object.V[:] = np.where(np.logical_and(object.vmask==1, old_object.vmask==1), old_object.V[:], object.V[:]) 

    # Condition which marks cells that are newly ice shelfs to True
    conditiont = np.logical_and(object.tmask[:]==1, old_object.tmask[:]==0)
    conditionu = np.logical_and(object.umask[:]==1, old_object.umask[:]==0)
    conditionv = np.logical_and(object.vmask[:]==1, old_object.vmask[:]==0)

    # Fill new ice shelf grid cells with np.nan
    object.T[:] = np.where(conditiont, np.nan, object.T[:])
    object.S[:] = np.where(conditiont, np.nan, object.S[:])
    object.D[:] = np.where(conditiont, np.nan, object.D[:])
    object.U[:] = np.where(conditionu, np.nan, object.U[:])
    object.V[:] = np.where(conditionv, np.nan, object.V[:])    
   
    # Count empty cells
    N_empty_cells_tmask = np.sum(np.isnan(object.T[1]))
    N_empty_cells_umask = np.sum(np.isnan(object.U[1]))
    N_empty_cells_vmask = np.sum(np.isnan(object.V[1]))

    # Fill new cells with average of nearest neighbour, use a while loop to make sure every cell is filled
    print('empty tmask:', N_empty_cells_tmask)  # tmask, variables T, S, D
    while N_empty_cells_tmask > 0:
        object.T[:] = np.where(conditiont, compute_average_NN(object.T, old_object.tmask), object.T[:])
        object.S[:] = np.where(conditiont, compute_average_NN(object.S, old_object.tmask), object.S[:])
        object.D[:] = np.where(conditiont, compute_average_NN(object.D, old_object.tmask), object.D[:])
        # Update tmask
        old_object.tmask = np.where(np.logical_and(np.isnan(object.T[1])==False, old_object.tmask==0), 1, old_object.tmask)
        N_empty_cells_tmask = np.sum(np.isnan(object.T[1]))
        print('empty tmask:', N_empty_cells_tmask)
    
    print('empty umask:', N_empty_cells_umask)  # umask, variable U
    while N_empty_cells_umask > 0:
        object.U[:] = np.where(conditionu, object.nnUV * compute_average_NN(object.U, old_object.umask),object.U[:])
        # Update umask
        old_object.umask = np.where(np.logical_and(np.isnan(object.U[1])==False, old_object.umask==0), 1, old_object.umask)
        N_empty_cells_umask = np.sum(np.isnan(object.U[1]))
        print('empty umask:', N_empty_cells_umask)

    print('empty vmask:', N_empty_cells_vmask)  # vmask, variable V
    while N_empty_cells_vmask > 0:
        object.V[:] = np.where(conditionv, object.nnUV * compute_average_NN(object.V, old_object.vmask),object.V[:])
        # Update vmask
        old_object.vmask = np.where(np.logical_and(np.isnan(object.V[1])==False, old_object.vmask==0), 1, old_object.vmask)
        N_empty_cells_vmask = np.sum(np.isnan(object.V[1]))
        print('empty vmask:', N_empty_cells_vmask)
        
    return object
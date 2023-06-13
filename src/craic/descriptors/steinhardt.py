#!/usr/bin/env python3

import pyscal.core as pc
import numpy as np
import glob
import os
import os.path
import sys

from ._base import Descriptor


def computeQAll(input_file, qOrders, averageQ, neighborMethod, cutoffRadius=None):
    sysAll = pc.System()
    sysAll.read_inputfile(input_file)
    if neighborMethod == 'cutoff':
        if not cutoffRadius:
            print('Cutoff radius was not defined, necessary for cutoff neighbor method')
            exit()
        sysAll.find_neighbors(method=neighborMethod, cutoff=cutoffRadius)
    else:
        sysAll.find_neighbors(method=neighborMethod)
    sysAll.calculate_q(qOrders, averaged=averageQ)
    q = sysAll.get_qvals(qOrders, averaged=averageQ)
    return q


def computeQMono(input_file, qOrders, averageQ, neighborMethod, cutoffRadius=None):
    #Get number of atom types
    sysAll = pc.System()
    sysAll.read_inputfile(input_file)
    atomTypes = {i.type for i in sysAll.atoms}
    if len(atomTypes) == 1:
        print('There is only one available atom type, mono Steinhardt parameters will not be computed')
    else:
        qMono = dict()
        for atomtype in atomTypes:
            #Compute q values for system of same atom types
            selectedAtoms=[ i for i in sysAll.atoms if i.type==atomtype]
            sysMono=pc.System()
            sysMono.read_inputfile(input_file)
            sysMono.atoms=selectedAtoms
            if neighborMethod == 'cutoff':
                if not cutoffRadius:
                    print('Cutoff radius was not defined, necessary for cutoff neighbor method')
                    exit()
                sysMono.find_neighbors(method=neighborMethod, cutoff=cutoffRadius)
            else:
                sysMono.find_neighbors(method=neighborMethod)
            sysMono.calculate_q(qOrders, averaged=averageQ)
            qMono[atomtype]=sysMono.get_qvals(qOrders, averaged=averageQ)
    listTypes = [i.type for i in sysAll.atoms]
    q_mono = [[qMono[i][b][s] for i in listTypes for s in range(len(qMono[i][b]))] for b in range(len(qOrders))]
    return q_mono




class Steinhardt(Descriptor):
    """Steinhardt parameters"""

    def __init__(self, setupFile):
        super().__init__(setupDict=setupFile)
        self._read_setup(self.setupDict)
        #List of parameters for Steinhardt computation
        self.qOrders = [2,3,4,5,6,7,8]
        self.neighborMethod = 'voronoi'
        self.cutoffRadius = 4.0
        self.averageQ = True
        self.mono = False
        self.skipOld = False
    
    def _read_setup(self, setupDict: dict) -> None:
        """Read setup file and assign variables"""
        print('Reading setup from dictionary: ', setupDict)

    def _compute_descriptors(self):
        """Compute Steinhardt parameters using properties from setup file"""
        for input_file in self.list_files:
            #Check for sorting of qOrders
            qOrders = sorted(self.qOrders)

            #Compute q values for complete system
            self.qAll = computeQAll(input_file, qOrders, self.averageQ, self.neighborMethod, self.cutoffRadius)

            #Create mono type systems if desired
            if self.mono:
                self.qMono = computeQMono(input_file, qOrders, self.averageQ, self.neighborMethod, self.cutoffRadius)
            else:
                self.qMono = None
    
    def _write_to_file(self):
        """Save the computed descriptors to files in the 'Descriptors' directory"""
        for input_file in self.list_files:
            #Get name of output file and create the output directory if it doesn't exist
            output_file = input_file.replace('/Input/', '/Descriptors/')
            output_file = output_file.replace(".trj", ".Q.trj")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            #Skip file if it has already been computed before and skipOld is True
            if os.path.exists(output_file) and self.skipOld:
                print(input_file, '   Continued')
                return
            print(input_file)

            #Create system to write to file
            sysAll = pc.System()
            sysAll.read_inputfile(input_file)
            qVals = self.qAll
            #Get list of parameters to write
            if self.averageQ:
                listParams = ["aq"+str(order) for order in self.qOrders]
            else:
                listParams = ["q"+str(order) for order in self.qOrders]
            if self.qMono:
                qVals = self.qAll + self.qMono
                if self.averageQ:
                    listParams += ["aq"+str(order)+"_mono" for order in self.qOrders]
                else:
                    listParams += ["q"+str(order)+"_mono" for order in self.qOrders]
            
            #Transpose list
            transposedVals = [list(qVals[i][b] for i in range(len(qVals))) for b in range(len(qVals[0]))]
            #Write to file using the pyscal built-in function
            sysAll.to_file(output_file, customkeys=listParams, customvals=transposedVals)
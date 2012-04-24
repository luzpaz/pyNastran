from __future__ import print_function
import sys
from numpy import array,zeros,ones
from numpy.linalg import solve

from pyNastran.general.generalMath import printMatrix,annotatePrintMatrix
from pyNastran.bdf.bdf import BDF,SPC,SPC1

def partitionSparse(Is,Js,Vs):
    I2=[]
    J2=[]
    V2=[]
    for (i,j,v) in (Is,Js,Vs):
        if abs(v)>=1e-8:
            I2.append(i)
            J2.append(j)
            V2.append(v)
        ###
    ###
    return(I2,J2,V2)

def partitionDenseSymmetric(A,dofs):
    dofs.sort()
    n = len(dofs)
    A2 = zeros((n,n))
    for (i,dofI) in enumerate(dofs):
        for (j,dofJ) in enumerate(dofs):
            v = A[dofI,dofJ]
            if abs(v)>=1e-8:
                A2[i,j] = v
            ###
        ###
    ###
    return(A2)

def partitionSparseVector(F,dofs):
    dofs.sort()
    n = len(dofs)
    F2i = []
    F2v = []
    for (i,dofI) in enumerate(dofs):
            v = F2v[dofI]
            if abs(v)>=1e-8:
                F2i.append(i)
                F2v.append(v)
            ###
        ###
    ###
    return(F2i,F2v)

def partitionDenseVector(F,dofs):
    dofs.sort()
    n = len(dofs)
    F2 = zeros(n)
    for (i,dofI) in enumerate(dofs):
            v = F[dofI]
            if abs(v)>=1e-8:
                F2[i] = v
            ###
        ###
    ###
    return(F2)

def dePartitionDenseVector(n,IsVs):
    V = zeros(n)
    for IV in IVs:
        (Is,Vs) = IV
        for (i,v) in zip(Is,Vs):
            V[i] = v
        ###
    ###
    return(V)
    
def reverseDict(A):
    B = {}
    for key,value in A.iteritems():
        B[value] = key
    return B

class solver(object):
    def __init__(self):
        self.Title = ''
        self.Subtitle = ''
        self.Us = []
        self.Um = []
        self.iUs = []
        self.iUm = []

    def solve(K,F): # can be overwritten
        """solves [K]{x} = {F} for {x}"""
        return solve(K,F)

    def run(self,bdfName):
        model = BDF()
        model.cardsToRead = getCards()
        model.readBDF(bdfName)
        cc = model.caseControlDeck
        #print cc.subcases
        analysisCases = []
        for isub,subcase in sorted(cc.subcases.iteritems()):
            if subcase.hasParameter('LOAD'):
                analysisCases.append(subcase)

        #print analysisCases
        for case in analysisCases:
            print(case)
            (value,options) = case.getParameter('STRESS')
            print("STRESS value   = ",value)
            print("STRESS options = ",options)

            if case.hasParameter('TEMPERATURE(INITIAL)'):
                (value,options) = case.getParameter('TEMPERATURE(INITIAL)')
                print('value   = %s' %(value))
                print('options = %s' %(options))
                raise NotImplementedError('TEMPERATURE(INITIAL) not supported')
                #integrate(B.T*E*alpha*dt*Ads)
            #sys.exit('starting case')
            self.runCase(model,case)
        ###

    def runCase(self,model,case):
        sols = {101:self.runSOL101}
        
        if model.sol in sols:
            if case.hasParameter('TITLE'):
                (self.Title,options) = case.getParameter('TITLE')
            if case.hasParameter('SUBTITLE'):
                (self.Subtitle,options) = case.getParameter('SUBTITLE')
            sols[model.sol](model,case)
        else:
            raise NotImplementedError('model.sol=%s not in %s' %(model.sol,sols.keys()))
        ###

    def buildNidComponentToID(self,model):
        i=0
        nidComponentToID = {}
        for nid,node in sorted(model.nodes.iteritems()):  # GRIDs
            ps = node.ps
            #print ps
            for ips in ps:
                self.iUs.append(i+int(ips)-1)
                self.Us.append(0.0)
            ###
            if self.is3D:
                nidComponentToID[(nid,1)] = i
                nidComponentToID[(nid,2)] = i+1
                nidComponentToID[(nid,3)] = i+2
                nidComponentToID[(nid,4)] = i+3
                nidComponentToID[(nid,5)] = i+4
                nidComponentToID[(nid,6)] = i+5
                
                i+=6
            else:
                nidComponentToID[(nid,1)] = i
                nidComponentToID[(nid,2)] = i+1
                #nidComponentToID[(nid,4)] = i+2  # torsion???
                #nidComponentToID[(nid,5)] = i+2  # bending???
                i+=2
            ###
        ###
        if model.spoints:
            for nid in sorted(model.spoints.spoints): # SPOINTS
                nidComponentToID[(nid,1)] = i
                i+=1
            ###
        ###
        return(nidComponentToID,i)

    def runSOL101(self,model,case):
        assert model.sol==101,'model.sol=%s is not 101' %(model.sol)

        ## define IDs of grid point components in matrices

        self.is3D = False
        (nidComponentToID,i) = self.buildNidComponentToID(model) # the (GridID,componentID) -> internalID
        (isSPC) = self.applySPCs(model,case,nidComponentToID)
        (isMPC) = self.applyMPCs(model,case,nidComponentToID)

        #spcDOFs = self.iUs
        #mpcDOFs = self.iUm

        Ug  = ones(i)
        Fg  = zeros(i)

        Kgg = zeros((i,i))
        #Mgg = zeros((i,i))

        Kgg = self.assembleGlobalStiffness(model,Kgg,nidComponentToID)
        Fg  = self.assembleForces(model,Fg,nidComponentToID)
        
        (IDtoNidComponents) = reverseDict(nidComponentToID)
        print("Kgg = \n",annotatePrintMatrix(Kgg,IDtoNidComponents))
        print("iSize = ",i)
        sys.exit('verify Kgg')


        Kaa = partitionDenseSymmetric(Kgg,spcDOFs)
        Fa  = partitionDenseVector(Fg,spcDOFs)
        print("Kaa = \n%s" %(printMatrix(Kaa)))

        print("Fg = ",Fg)
        print("Fa = ",Fa)
        print("Us = ",self.Us)

        self.Us = array(self.Us)
        self.Um = array(self.Um)

        zero = array([])
        MPCgg = zero
        Ksa = Kas = Kss = Cam = Cma = Kma = Kam = Kmm = Kms = Ksm = zero
        Kaa1 = Kaa2 = zero
        Fm = Fs = zero

        Kaa = PartitionDenseMatrix(Kgg,iFree)
        Kaa0 = Kaa
        Fa0  = Fa

        if isSPC:
           #Fs  = PartitionDenseVector(Fg,self.iUs)
            Ksa = PartitionDenseMatrix(Kgg,self.iUs,iFree)
            Kas = Ksa.transpose()
            Kss = PartitionDenseMatrix(Kgg,self.iUs)

        if isMPC:
            Fm  = PartitionDenseVector(Fg,self.iUm)
            Cam = PartitionDenseMatrix(MPCgg,iFree)
            Cma = PartitionDenseMatrix(MPCgg,self.iUm)

            Kaa1 = Cam*Kmm*Cma
            Kaa2 = Cam*Kma + Kam*Cma
            assert Cam.transpose()==Cma

            Kma = PartitionDenseMatrix(Kgg,self.iUm,iFree)    
            Kam = Kma.transpose()
            Kmm = PartitionDenseMatrix(Kgg,self.iUm)
            if isSPC:
                Kms = PartitionDenseMatrix(Kgg,self.iUm,self.iUs)
                Ksm = Kms.transpose()
            ###
        ###
        Fa  = Fa0 + Cam*Fm
        Kaa = Kaa0+Kaa1+Kaa2

        Ua = self.solve(Kaa,Fa)
        self.Um = Kma*Ua

    def assembleGlobalStiffness(self,model,Kgg,Dofs):
        for eid,elem in sorted(model.elements.iteritems()):  # CROD
            K,nIJV = elem.Stiffness(model)  # nIJV is the position of the values of K in the dof
            print("K[%s] = \n%s" %(eid,K))
            (Ki,Kj) = K.shape
            ij = 0
            nij2 = []
            for ij in nIJV:
                nij2.append(Dofs[ij])
            print('nij2',nij2)

            for i in range(Ki):
                for j in range(Kj):
                    kij = K[i,j]
                    #if abs(kij)>1e-8:
                    #print('niJV = ',nIJV[ij])
                    ii = nij2[i]
                    jj = nij2[j]
                    #dof = Dofs[n]
                    Kgg[ii,jj] = kij

                    #ij += 1
                ###
            ###
        if 0:
            #(n,IJV) = elem.nIJV()  # n is (nid,componentID), IJV is the (ith,jth,value) in K
            for (ni,ijv) in zip(n,IJV):
                i = nidComponentToID(ni)
                j = nidComponentToID(ji)
                #(i,j,v) = ijv
                Kgg[i,j] = v
                #KggI.append(i)
                #KggJ.append(j)
                #KggV.append(v)
            ###
        ###
        return Kgg

    def applySPCs(self,model,case,nidComponentToID):
        isSPC = False
        if case.hasParameter('SPC'):
            isSPC = True
            spcs = model.spcObject2.constraints
            spcID = case.getParameter('SPC')[0]  # get the value, 1 is the options (SPC has no options)
            print("SPC = ",spcID)
            #print model.spcObject2.constraints
            spcset = spcs[spcID]

            for spc in spcset:
                print(spc)
                if isinstance(spc,SPC):
                    ps = spc.constraints
                    print("spc.constraints = ",spc.constraints)
                    print("spc.enforced    = ",spc.enforced)
                    raise NotImplementedError('no support for SPC...')
                    self.Us.append(self.enforced)
                    for ips in ps:
                        key = (nid,int(ips))
                        i = nidComponentToID(key)
                        self.iUs.append(i)
                        self.Us.append(0.0)
                    ###
                elif isinstance(spc,SPC1):
                    ps = spc.constraints
                    #print "ps = |%s|" %(ps)
                    nodes = spc.nodes
                    for nid in nodes:
                        for ips in ps:
                            ips = int(ips)
                            if not(self.is3D) and ips not in ['1','2','5']:
                                continue

                            key = (nid,ips)
                            i = nidComponentToID[key]
                            #print "i=%s Us=%s" %(i,0.0)
                            if i not in self.iUs:
                                self.iUs.append(i)
                                self.Us.append(0.0)
                            ###
                        ###
                    ###
                else:
                    raise NotImplementedError('Invalid SPC...spc=\n%s' %(spc))
                ###
            ###
            print("iUs = ",self.iUs)
            print("Us  = ",self.Us)
            sys.exit('stopping in applySPCs')
        ###
        return (isSPC)
    
    def applyMPCs(self,model,case,nidComponentToID):
        isMPC = False
        if case.hasParameter('MPC'):
            isMPC = True
            mpcs = model.mpcObject2.constraints
            mpcID = case.getParameter('MPC')[0]  # get the value, 1 is the options (MPC has no options)
            print("******")
            print(model.mpcObject2.constraints)
            print("mpcID = ",mpcID)
            mpcset = mpcs[mpcID]

            for mpc in mpcset:
                print(mpc,type(mpc))
            raise NotImplementedError('MPCs are not supported...stopping in applyMPCs')
        return (isMPC)

    def assembleForces(self,model,Fg,Dofs):
        print(model.loads)
        for loadSet,loads in model.loads.iteritems():
            ## @todo if loadset in required loadsets...
            #print loads
            for load in loads:
                if load.type=='FORCE':
                    loadDir = load.F()
                    #nid = load.nodeID()
                    for nid,F in loadDir.iteritems():
                        #print(nid,load.lid)
                        Fg[Dofs[(nid,1)]] = F[0]
                        Fg[Dofs[(nid,2)]] = F[1]
                        if self.is3D:
                            Fg[Dofs[(nid,3)]] = F[2]
                        #print("Fgi = ",Fg)
                    ###
                ###
            ###
        print("Fg  = ",Fg)
        return Fg

    def writeResults(self,case):
        Us = self.Us; iUs=self.iUs
        Um = self.Um; iUm=self.iUm
        Ua = self.Ua; iUa=self.iUa
        pageNum = 1

        if case.hasParameter('DISPLACEMENT'):
            (value,options) = case.getParameter('DISPLACEMENT')
            if options is not []:
                UgSeparate = [[Ua,iUa],[Us,iUs],[Um,iUm],]
                Ug = dePartitionDenseVector(UgSeparate)

                result = displacmentObject(dataCode,transient)
                result.addF06Data()

                if 'PRINT' in options:
                    f06.write(result.writeF06(header,pageStamp,pageNum))
                if 'PLOT' in options:
                    op2.write(result.writeOP2(self.Title,self.Subtitle))
                ###
            ###
        ###

        if case.hasParameter('SPCFORCES'):
            (value,options) = case.getParameter('SPCFORCES')
            if options is not []:
                SPCForces = Ksa*Ua + Kss*Us
                if isMPC:
                    SPCForces += Ksm*Um
                ###
                result = spcForcesObject(dataCode,transient)
                result.addF06Data()

                if 'PRINT' in options:
                    f06.write(result.writeF06(header,pageStamp,pageNum))
                if 'PLOT' in options:
                    op2.write(result.writeOP2(Title,Subtitle))
                ###
            ###
        ###

        if case.hasParameter('MPCFORCES'):
            if options is not []:
                (value,options) = case.getParameter('MPCFORCES')
                MPCForces = Kma*Ua + Kmm*Um
                if isSPC:
                    MPCForces += Kms*Us
                ###
                result = mpcForcesObject(dataCode,transient)
                result.addF06Data()

                if 'PRINT' in options:
                    f06.write(result.writeF06(header,pageStamp,pageNum))
                if 'PLOT' in options:
                    f06.write(result.writeOP2(Title,Subtitle))
                ###
            ###
        ###

        if case.hasParameter('GPFORCE'):
            if options is not []:
                (value,options) = case.getParameter('GPFORCE')
                AppliedLoads = Kaa*Ua
                if isSPC:
                    AppliedLoads += Kas*Us
                if isMPC:
                    AppliedLoads += Kam*Um
                ###
                result = xxxObject(dataCode,transient)
                result.addF06Data()

                if 'PRINT' in options:
                    f06.write(result.writeF06(header,pageStamp,pageNum))
                if 'PLOT' in options:
                    op2.write(result.writeOP2(Title,Subtitle))
                ###
            ###
        ###

        if case.hasParameter('STRAIN'):
            if options is not []:
                (value,options) = case.getParameter('STRAIN')

                for eid,elem in sorted(model.elements()):
                    pass
                ###
                result = xxxObject(dataCode,transient)
                result.addF06Data()

                if 'PRINT' in options:
                    f06.write(result.writeF06(header,pageStamp,pageNum))
                if 'PLOT' in options:
                    op2.write(result.writeOP2(Title,Subtitle))
                ###
            ###
        ###
    
def getCards():
        cardsToRead = set([
        'PARAM',
        'GRID','GRDSET',

        # elements
        'CONM1','CONM2','CMASS1','CMASS2','CMASS3','CMASS4',
        'CELAS1','CELAS2','CELAS3','CELAS4',
        
        'CBAR','CROD','CTUBE','CBEAM','CONROD','CBEND',
        'CTRIA3','CTRIA6',
        'CQUAD4','CQUAD8',
        'CTETRA','CPENTA','CHEXA',
        'CSHEAR',
        
        # rigid elements - represent as MPCs???
        #'RBAR','RBAR1','RBE1','RBE2','RBE3',

        # properties
        'PELAS',
        'PROD','PBAR','PBARL','PBEAM','PBEAML','PTUBE','PBEND',
        'PSHELL','PCOMP','PSHEAR', #'PCOMPG',
        'PSOLID',

        # materials
        'MAT1','MAT2','MAT8',

        # spc/mpc constraints
        'SPC','SPC1','SPCADD',
        #'MPC','MPCADD',

        # loads
        'LOAD',
        'FORCE','FORCE1','FORCE2',
        #'PLOAD','PLOAD1','PLOAD2','PLOAD4',
        'MOMENT','MOMENT1','MOMENT2',

        # coords
        'CORD1R','CORD1C','CORD1S',
        'CORD2R','CORD2C','CORD2S',
        
        # other
        'INCLUDE',
        'ENDDATA',
        ])
        return cardsToRead

if __name__=='__main__':
    bdfName = sys.argv[1]
    s = solver()
    s.run(bdfName)
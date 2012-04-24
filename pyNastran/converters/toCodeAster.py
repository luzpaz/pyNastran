language = 'english'
from pyNastran.bdf.bdf import BDF,PBAR,PBARL,PBEAM,PBEAML

class CodeAsterConverter(BDF):
    def __init__(self):
        BDF.__init__(self)
    
    def getElementsByPid(self):
        """builds a dictionary where the key is the property ID and the value is a list of element IDs"""
        props = {}
        for pid in self.properties:
            props[pid] = []
        for eid,element in self.elements.iteritems():
            pid = element.Pid()
            props[pid].append(eid)
        ###
        return mats

    def getElementsByMid(self):
        """builds a dictionary where the key is the material ID and the value is a list of element IDs"""
        mats = {0:[]}
        
        for mid in self.materials:
            mats[mid] = []
        for eid,element in self.elements.iteritems():
            try:
                mid = element.Mid()
                mats[mid].append(eid)
            except:
                mats[0].append(eid)
        ###
        return mats

    def getElementsByType(self):
        """builds a dictionary where the key is the element type and the value is a list of element IDs"""
        elems = {}
        #for eid,elements in self.elements:
            #elems[eid] = []
        for eid,element in self.elements.iteritems():
            Type = element.type
            if Type not in elems:
                elems[Type] = []

            elems[Type].append(eid)
            #mid = element.Mid()
            #mats[mid].append(eid)
        ###
        return elems

    def getPropertiesByMid(self):
        """builds a dictionary where the key is the material ID and the value is a list of property IDs"""
        mats = {0:[]}
        
        for mid in self.materials:
            mats[mid] = []
        for pid,property in self.properties.iteritems():
            try:
                mid = property.Mid()
                mats[mid].append(pid)
            except:
                mats[0].append(pid)
        ###
        return mats

    def CA_Executive(self):
        msg = ''
        if self.sol==101:
            #msg += 'MECA_STATIQUE % SOL 101 - linear statics\n'
            msg += 'stat(MECA_STATIQUE(MODELE=model,CHAM_MATER=material,CARA_ELEM=elemcar,\n'

            msg += 'ECIT=(_F(Charge=AllBoundaryConditions,),\n',
            msg += '      _F(Charge=AllLoads,),\n',
            msg += '      ),\n',

            msg += "TITRE='My Title'\n"
        return msg

    def CA_Nodes(self):
        if language=='english':
            msg = '# Grid Points\n'
        else:
            msg = ''

        msg += 'COORD_3D\n'
        form = '    grid%-'+str(self.maxNIDlen)+'s %8g %8g %8g\n'

        for nid,node in sorted(self.nodes.iteritems()):
            p = node.Position()
            msg += form %(nid,p[0],p[1],p[2])
        ###
        #msg += 'FINSF\n\n'
        msg += '\n'
        return ''
        return msg

    def CA_Elements(self):
        if language=='english':
            msg = '# Elements\n'
        else:
            msg = ''

        elems = self.getElementsByType()

        formE = '    elem%-'+str(self.maxEIDlen)+'s '
        formG =     'grid%-'+str(self.maxNIDlen)+'s '
        for Type,eids in sorted(elems.iteritems()):
            msg += '%s\n' %(Type)
            for eid in eids:
                msg += formE %(eid)
                element = self.elements[eid]
                for nid in element.nodeIDs():
                    msg += formG %(nid)
                msg += '\n'
            msg += 'FINSF\n\n'
        msg += self.breaker()
        return msg

    def CA_Properties(self):
        if language=='english':
            msg = '# Properties\n'
        else:
            msg = ''
        
        #p = []
        #for pid,prop in sorted(self.properties.iteritems()):
        #    p.append('%s_%s' %(prop.type,pid))
        #p = str(p)[1:-1] # chops the [] signs
        #msg += "MODEL=AFFE_MODELE(MAILLAGE=MESH,\n"
        #msg += "          AFFE=_F(GROUP_MA=(%s),\n" %(p)
        #msg += "                  PHENOMENE='MECANIQUE',\n"
        #msg += "                  MODELISATION=('POU_D_T'),),);\n\n"

        msg += "Prop = AFFE_CARA_ELEM(MODELE=FEMODL,\n"
        pyCA = ''
        iCut=0; iFace=0; iStart=0
        for pid,prop in sorted(self.properties.iteritems()):
            if isinstance(prop,PBARL) or isinstance(prop,PBEAML):
                (pyCAi,iCut,iFace,iStart) = prop.writeCodeAster(iCut,iFace,iStart)
                pyCA += pyCAi
            else:
                (msg) += prop.writeCodeAster()
            ###
        msg = msg[:-2]
        msg += ');\n'
        #msg += ');\nFINSF\n\n'
        msg += self.breaker()
        return msg,pyCA

    def CA_Loads(self):
        """writes the load cards sorted by ID"""
        if language=='english':
            msg = '# Loads\n'
        else:
            msg = ''
        if self.loads or self.gravs:
            msg += '# LOADS\n'
            for key,loadcase in sorted(self.loads.iteritems()):
                for load in loadcase:
                    try:
                        msg += load.writeCodeAster()
                    except:
                        print 'failed printing load...type=%s key=%s' %(load.type,key)
                        raise
                    ###
            for ID,grav in sorted(self.gravs.iteritems()):
                msg += grav.writeCodeAster()
            ###
        ###
        return msg

    def CA_Materials(self):
        """
        might need to make this byPid instead...
        steel=DEFI_MATERIAU(ELAS=_F(E=210000.,NU=0.3,RHO=8e-9),);
        """
        if language=='english':
            msg = '# Materials\n'
        else:
            msg = ''
        mats = self.getElementsByMid()
        for mid,material in sorted(self.materials.iteritems()):
            #msg += 'GROUP_MA name = %s_%s\n' %(material.type,mid)
            msg += material.writeCodeAster()

            eids = mats[mid]
            #msg += '    '
            #for eid in eids:
            #    msg += 'elem%s ' %(eid)
            #msg = msg[:-1]
            #msg += '\n'
        #msg = msg[:-2]
        #msg += '\n'
        #msg += ');\n'
        #msg += 'FINSF\n\n'
        msg += self.breaker()
        return msg

    def CA_MaterialField(self):
        """
        MtrlFld=AFFE_MATERIAU(MAILLAGE=MESH,
                              AFFE=(_F(GROUP_MA=('P32','P33','P42','P43','P46','P47','P48','P49','P61','P62','P63','P64','P65','P74',
                                                 'P75',),
                                       MATER=M3,),
                                    _F(GROUP_MA=('P11','P13','P14','P15','P55','P56','P59',),
                                       MATER=M6,),
        """
        msg = ''
        msg += 'MtrlFld=AFFE_MATERIAU(MAILLAGE=MESH,\n'
        msg += '                      AFFE=(\n'

        mat2Props = self.getPropertiesByMid()
        for mid,material in sorted(self.materials.iteritems()):
            msg += '                      _F(GROUP_MA=('
            pids = mat2Props[mid]
            #msg += "                      "
            for pid in pids:
                msg += "'P%s'," %(pid)
            msg = msg[:-1]+'),\n'
            msg += "                      MATER=M%s),\n" %(mid)
        ###
        msg = msg[:-1] + '));\n'
        
        msg += self.breaker()
        return msg

    def CA_SPCs(self):
        #for spcID,spcs in self.spcObject2.iteritems():
        pass

    def breaker(self):
        return '#-------------------------------------------------------------------------\n'

    def buildMaxs(self):
        self.maxNIDlen = len(str(max(self.nodes)))
        self.maxEIDlen = len(str(max(self.elements)))
        self.maxPIDlen = len(str(max(self.properties)))
        self.maxMIDlen = len(str(max(self.materials)))

    def writeAsCodeAster(self,fname='fem'):
        self.buildMaxs()

        msg = ''
        msg += '# BEGIN BULK\n'
        msg += 'DEBUT();\n\n'
        
        msg += "#'Read the mesh' - we use the 'med' file format here.\n"
        msg += 'mesh=LIRE_MAILLAGE(UNITE=20,\n'
        msg += "                   FORMAT='MED',\n"
        msg += '                   INFO_MED=2,);\n\n'
        
        msg += "# Assigning the model for which CA will calculate the results: 'Mecanique' - since we are dealing with a linear elastic beam and '3D' since it's a 3D model.\n"
        msg += 'Meca=AFFE_MODELE(MAILLAGE=mesh,\n'
        msg += "                 AFFE=_F(TOUT='OUI',\n"
        msg += "                         PHENOMENE='MECANIQUE',\n"
        msg += "                         MODELISATION='3D',),);\n\n"
        
        


        msg += self.CA_Nodes()
        #msg += self.CA_Elements()
        msg += self.CA_Materials()
        msg += self.CA_MaterialField()
        (msgi,pyCA) = self.CA_Properties()
        msg += msgi
        msg += self.CA_Loads()

        msg += 'FIN();\n'
        msg += '# ENDDATA\n'
        f = open(fname+'.comm','wb')
        f.write(msg)
        f.close()
        
        if pyCA:
            f = open(fname+'.py','wb')
            f.write(pyCA)
            f.close()
        ###

        

if __name__=='__main__':
    import sys
    ca = CodeAsterConverter()
    #model = 'solidBending'
    model = sys.argv[1]
    ca.readBDF(model+'.bdf')
    ca.writeAsCodeAster(model)  # comm, py
    
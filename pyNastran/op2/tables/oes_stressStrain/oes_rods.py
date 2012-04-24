import sys
from oes_objects import stressObject,strainObject #,array
from pyNastran.op2.op2Errors import *

class rodDamperObject(stressObject):
    def __init__(self,dataCode,iSubcase,dt=None):
        stressObject.__init__(self,dataCode,iSubcase)
        self.eType = 'CBUSH'
        
        self.code = [self.formatCode,self.sortCode,self.sCode]
        self.axial      = {}
        self.torsion    = {}


class rodStressObject(stressObject):
    """
    # formatCode=1 sortCode=0 stressCode=0
                                     S T R E S S E S   I N   R O D   E L E M E N T S      ( C R O D )
       ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY       ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY
         ID.        STRESS       MARGIN        STRESS      MARGIN         ID.        STRESS       MARGIN        STRESS      MARGIN
             1    5.000000E+03              0.0                               2    0.0                       0.0           

    # formatCode=1 sortCode=0 stressCode=0
                                     S T R E S S E S   I N   R O D   E L E M E N T S      ( C R O D )
      ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY       ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY
        ID.        STRESS       MARGIN        STRESS      MARGIN         ID.        STRESS       MARGIN        STRESS      MARGIN

    # formatCode=2 sortCode=1 stressCode=0
      COMPLEX EIGENVALUE = -3.575608E+04,  6.669431E+02
                             C O M P L E X   F O R C E S   I N   R O D   E L E M E N T S   ( C R O D )
                                                          (REAL/IMAGINARY)
                 ELEMENT                             AXIAL                                         TORQUE
                   ID.                               FORCE
    """
    def __init__(self,dataCode,iSubcase,dt=None):
        stressObject.__init__(self,dataCode,iSubcase)
        self.eType = 'CROD'
        
        self.code = [self.formatCode,self.sortCode,self.sCode]
        self.axial      = {}
        self.torsion    = {}
        
        if self.code in [[1,0,0],[1,0,1]]:
            self.MS_axial   = {}
            self.MS_torsion = {}
            self.getLength = self.getLength_format1_sort0
            self.isImaginary = False
            if dt is not None:
                self.addNewTransient = self.addNewTransient_format1_sort0
                self.addNewEid       = self.addNewEidTransient_format1_sort0
            else:
                self.addNewEid = self.addNewEid_format1_sort0
            ###
        elif self.code==[2,1,0]:
            self.getLength       = self.getLength_format1_sort0
            self.addNewTransient = self.addNewTransient_format2_sort1
            self.addNewEid       = self.addNewEidTransient_format2_sort1
            self.isImaginary = True
        else:
            raise InvalidCodeError('rodStress - get the format/sort/stressCode=%s' %(self.code))
        ###
        if dt is not None:
            self.isTransient = True
            self.dt = self.nonlinearFactor
            self.addNewTransient()
        ###

    def addF06Data(self,data,transient):
        if transient is None:
            for line in data:
                (eid,axial,MSa,torsion,MSt) = line
                if MSa==None: MSa = 0.
                if MSt==None: MSt = 0.
                self.axial[eid]      = axial
                self.MS_axial[eid]   = MSa
                self.torsion[eid]    = torsion
                self.MS_torsion[eid] = MSt
            ###
            return

        (dtName,dt) = transient
        self.dataCode['name'] = dtName
        if dt not in self.s1:
            self.updateDt(self.dataCode,dt)
            self.isTransient = True

        for line in data:
            (eid,axial,MSa,torsion,MSt) = line
            if MSa==None: MSa = 0.
            if MSt==None: MSt = 0.
            self.axial[dt][eid]      = axial
            self.MS_axial[dt][eid]   = MSa
            self.torsion[dt][eid]    = torsion
            self.MS_torsion[dt][eid] = MSt
        ###

    def getLength_format1_sort0(self):
        return (20,'iffff')

    def deleteTransient(self,dt):
        del self.axial[dt]
        del self.torsion[dt]
        del self.MS_axial[dt]
        del self.MS_torsion[dt]

    def getTransients(self):
        k = self.axial.keys()
        k.sort()
        return k

    def addNewTransient_format1_sort0(self):
        """
        initializes the transient variables
        @note make sure you set self.dt first
        """
        if self.dt not in self.axial:
            self.axial[self.dt]      = {}
            self.MS_axial[self.dt]   = {}
            self.torsion[self.dt]    = {}
            self.MS_torsion[self.dt] = {}

    def addNewTransient_format2_sort1(self):
        """
        initializes the transient variables
        @note make sure you set self.dt first
        """
        #print self.dataCode
        if self.dt not in self.axial:
            self.axial[self.dt]     = {}
            self.torsion[self.dt]   = {}

    def addNewEid_format1_sort0(self,out):
        #print "Rod Stress add..."
        (eid,axial,SMa,torsion,SMt) = out
        eid = (eid-self.deviceCode) // 10
        assert isinstance(eid,int)
        self.axial[eid]      = axial
        self.MS_axial[eid]   = SMa
        self.torsion[eid]    = torsion
        self.MS_torsion[eid] = SMt

    def addNewEid_format2_sort1(self,out):
        (eid,axialReal,axialImag,torsionReal,torsionImag) = out
        eid = (eid-self.deviceCode) // 10
        assert eid >= 0
        self.axial[eid]      = [axialReal,axialImag]
        self.torsion[eid]    = [torsionReal,torsionImag]

    def addNewEidTransient_format1_sort0(self,out):
        (eid,axial,SMa,torsion,SMt) = out
        eid = (eid-self.deviceCode) // 10
        dt = self.dt
        assert isinstance(eid,int)
        assert eid >= 0
        self.axial[dt][eid]      = axial
        self.MS_axial[dt][eid]   = SMa
        self.torsion[dt][eid]    = torsion
        self.MS_torsion[dt][eid] = SMt

    def addNewEidTransient_format2_sort1(self,out):
        (eid,axialReal,axialImag,torsionReal,torsionImag) = out
        eid = (eid-self.deviceCode) // 10
        dt = self.dt
        assert eid >= 0
        self.axial[dt][eid]      = [axialReal,axialImag]
        self.torsion[dt][eid]    = [torsionReal,torsionImag]

    def __reprTransient_format1_sort0__(self):
        msg = '---ROD STRESSES---\n'
        msg += '%-6s %6s ' %('EID','eType')
        headers = ['axial','torsion','MS_axial','MS_torsion']
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for dt,axial in sorted(self.axial.iteritems()):
            msg += '%s = %g\n' %(self.dataCode['name'],dt)
            for eid in sorted(axial):
                axial   = self.axial[dt][eid]
                torsion = self.torsion[dt][eid]
                SMa     = self.MS_axial[dt][eid]
                SMt     = self.MS_torsion[dt][eid]
                msg += '%-6i %6s ' %(eid,self.eType)
                vals = [axial,torsion,SMa,SMt]
                for val in vals:
                    if abs(val)<1e-6:
                        msg += '%10s ' %('0')
                    else:
                        msg += '%10i ' %(val)
                    ###
                msg += '\n'
                #msg += "eid=%-4s eType=%s axial=%-4i torsion=%-4i\n" %(eid,self.eType,axial,torsion)
            ###
        return msg

    def __reprTransient_format2_sort1__(self):
        msg = '---COMPLEX ROD STRESSES---\n'
        msg += '%-10s %10s ' %('EID','eType')
        headers = ['axialReal','axialImag','torsionReal','torsionImag']
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for dt,axial in sorted(self.axial.iteritems()):
            msg += '%s = %g\n' %(self.dataCode['name'],dt)
            for eid in sorted(axial):
                axial   = self.axial[dt][eid]
                torsion = self.torsion[dt][eid]
                msg += '%-6i %6s ' %(eid,self.eType)
                vals = axial + torsion # concatination
                for val in vals:
                    if abs(val)<1e-6:
                        msg += '%10s ' %('0')
                    else:
                        msg += '%10i ' %(val)
                    ###
                msg += '\n'
                #msg += "eid=%-4s eType=%s axial=%-4i torsion=%-4i\n" %(eid,self.eType,axial,torsion)
            ###
        return msg

    def writeF06(self,header,pageStamp,pageNum=1):
        if self.isTransient:
            return self.writeF06Transient(header,pageStamp,pageNum)

        msg = header+['                                     S T R E S S E S   I N   R O D   E L E M E N T S      ( C R O D )\n',
                 '       ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY       ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY\n',
                 '         ID.        STRESS       MARGIN        STRESS      MARGIN         ID.        STRESS       MARGIN        STRESS      MARGIN\n']
        out = []
        for eid in sorted(self.axial):
            axial   = self.axial[eid]
            MSa     = self.MS_axial[eid]
            torsion = self.torsion[eid]
            MSt     = self.MS_torsion[eid]
            (vals2,isAllZeros) = self.writeF06Floats13E([axial,torsion])
            (axial,torsion) = vals2
            out.append([eid,axial,MSa,torsion,MSt])
        
        nOut = len(out)
        nWrite = nOut
        if nOut%2==1:
            nWrite = nOut-1
        for i in range(0,nWrite,2):
            #print i,out[i:]
            outLine = '      %8i   %13s  %10.4E %13s  %10.4E   %8i   %13s  %10.4E %13s  %10.4E\n' %(tuple(out[i]+out[i+1]))
            msg.append(outLine)
        
        if nOut%2==1:
            outLine = '      %8i   %13s  %10.4E %13s  %10.4E\n' %(tuple(out[-1]))
            msg.append(outLine)
        msg.append(pageStamp+str(pageNum)+'\n')
        return(''.join(msg),pageNum)

    def writeF06Transient(self,header,pageStamp,pageNum=1):
        words = ['                                     S T R E S S E S   I N   R O D   E L E M E N T S      ( C R O D )\n',
                 '       ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY       ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY\n',
                 '         ID.        STRESS       MARGIN        STRESS      MARGIN         ID.        STRESS       MARGIN        STRESS      MARGIN\n']
        msg = []
        for dt,axials in sorted(self.axial.iteritems()):
            dtLine = '%14s = %12.5E\n'%(self.dataCode['name'],dt)
            header[2] = dtLine
            msg += header+words
            out = []
            for eid in sorted(axials):
                axial   = self.axial[dt][eid]
                MSa     = self.MS_axial[dt][eid]
                torsion = self.torsion[dt][eid]
                MSt     = self.MS_torsion[dt][eid]

                (vals2,isAllZeros) = self.writeF06Floats13E([axial,torsion])
                (axial,torsion) = vals2
                out.append([eid,axial,MSa,torsion,MSt])

            nOut = len(out)
            nWrite = nOut
            if nOut%2==1:
                nWrite = nOut-1
            for i in range(0,nWrite,2):
                outLine = '      %8i   %13s  %10.4E %13s  %10.4E   %8i   %13s  %10.4E %13s  %10.4E\n' %(tuple(out[i]+out[i+1]))
                msg.append(outLine)

            if nOut%2==1:
                outLine = '      %8i   %13s  %10.4E %13s  %10.4E\n' %(tuple(out[-1]))
                msg.append(outLine)
            msg.append(pageStamp+str(pageNum)+'\n')
            pageNum+=1
        return(''.join(msg),pageNum-1)

    def __repr__(self):
        if   self.isTransient and self.code in [[1,0,0],[1,0,1]]:
            return self.__reprTransient_format1_sort0__()
        elif self.code==[2,1,0]:
            return self.__reprTransient_format2_sort1__()
        #else:
        #    raise Exception('code=%s' %(self.code))
        msg = '---ROD STRESSES---\n'
        msg += '%-6s %6s ' %('EID','eType')
        headers = ['axial','torsion','MS_axial','MS_torsion']
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'
        #print "self.code = ",self.code
        for eid in sorted(self.axial):
            #print self.__dict__.keys()
            axial   = self.axial[eid]
            torsion = self.torsion[eid]
            SMa     = self.MS_axial[eid]
            SMt     = self.MS_torsion[eid]
            msg += '%-6i %6s ' %(eid,self.eType)
            vals = [axial,torsion,SMa,SMt]
            for val in vals:
                if abs(val)<1e-6:
                    msg += '%10s ' %('0')
                else:
                    msg += '%10i ' %(val)
                ###
            msg += '\n'
            #msg += "eid=%-4s eType=%s axial=%-4i torsion=%-4i\n" %(eid,self.eType,axial,torsion)
        return msg

class rodStrainObject(strainObject):
    """
    # sCode=1???
                                     S T R A I N S   I N   R O D   E L E M E N T S      ( C R O D )
    ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY
      ID.        STRAIN       MARGIN        STRAIN      MARGIN

    # sCode=10
                                       S T R A I N S   I N   R O D   E L E M E N T S      ( C O N R O D )
    ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY       ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY
      ID.        STRAIN       MARGIN        STRAIN      MARGIN         ID.        STRAIN       MARGIN        STRAIN      MARGIN
       1001    1.000000E+00   1.0E+00    1.250000E+00   3.0E+00         1007    1.000000E+00   1.0E+00    1.250000E+00   3.0E+00
    """
    def __init__(self,dataCode,iSubcase,dt=None):
        strainObject.__init__(self,dataCode,iSubcase)
        self.eType = 'CROD' #{} # 'CROD/CONROD/CTUBE'

        self.code = [self.formatCode,self.sortCode,self.sCode]
        
        self.axial      = {}
        self.torsion    = {}
        self.isTransient = False
        if self.code == [1,0,10]:
            self.getLength = self.getLength_format1_sort0
            self.MS_axial   = {}
            self.MS_torsion = {}
            self.isImaginary = False
            if dt is not None:
                self.addNewTransient = self.addNewTransient_format1_sort0
                self.addNewEid       = self.addNewEidTransient_format1_sort0
            ###
            else:
                self.addNewEid = self.addNewEid_format1_sort0
            ###

        elif self.code==[2,1,10]:
            self.getLength = self.getLength_format1_sort0
            self.addNewTransient = self.addNewTransient_format2_sort1
            self.addNewEid       = self.addNewEidTransient_format2_sort1
            self.isImaginary = True
        else:
            raise InvalidCodeError('rodStrain - get the format/sort/stressCode=%s' %(self.code))
        ###
        if dt is not None:
            self.dt = self.nonlinearFactor
            self.isTransient = True
            self.addNewTransient()
        ###

    def addF06Data(self,data,transient):
        if transient is None:
            for line in data:
                (eid,axial,MSa,torsion,MSt) = line
                if MSa==None: MSa = 0.
                if MSt==None: MSt = 0.
                self.axial[eid]      = axial
                self.MS_axial[eid]   = MSa
                self.torsion[eid]    = torsion
                self.MS_torsion[eid] = MSt
            ###
            return

        (dtName,dt) = transient
        self.dataCode['name'] = dtName
        if dt not in self.s1:
            self.updateDt(self.dataCode,dt)
            self.isTransient = True

        for line in data:
            (eid,axial,MSa,torsion,MSt) = line
            if MSa==None: MSa = 0.
            if MSt==None: MSt = 0.
            self.axial[dt][eid]      = axial
            self.MS_axial[dt][eid]   = MSa
            self.torsion[dt][eid]    = torsion
            self.MS_torsion[dt][eid] = MSt
        ###

    def getLength_format1_sort0(self):
        return (20,'iffff')

    def deleteTransient(self,dt):
        del self.axial[dt]
        del self.torsion[dt]
        del self.MS_axial[dt]
        del self.MS_torsion[dt]

    def getTransients(self):
        k = self.axial.keys()
        k.sort()
        return k

    def addNewTransient_format1_sort0(self):
        """
        initializes the transient variables
        @note make sure you set self.dt first
        """
        if self.dt not in self.axial:
            self.axial[self.dt]      = {}
            self.MS_axial[self.dt]   = {}
            self.torsion[self.dt]    = {}
            self.MS_torsion[self.dt] = {}

    def addNewTransient_format2_sort1(self):
        """
        initializes the transient variables
        @note make sure you set self.dt first
        """
        #print self.dataCode
        if self.dt not in self.axial:
            self.axial[self.dt]     = {}
            self.torsion[self.dt]   = {}

    def addNewEid_format1_sort0(self,out):
    
        (eid,axial,SMa,torsion,SMt) = out
        eid = (eid-self.deviceCode) // 10
        #print "Rod Strain add..."
        assert eid >= 0
        #self.eType = self.eType
        self.axial[eid]      = axial
        self.MS_axial[eid]   = SMa
        self.torsion[eid]    = torsion
        self.MS_torsion[eid] = SMt

    def addNewEid_format2_sort1(self,out):
        assert eid >= 0
        (eid,axialReal,axialImag,torsionReal,torsionImag) = out
        eid = (eid-self.deviceCode) // 10
        self.axial[eid]      = [axialReal,axialImag]
        self.torsion[eid]    = [torsionReal,torsionImag]

    def addNewEidTransient_format1_sort0(self,out):
        #print "Rod Strain add..."
        #print out
        (eid,axial,SMa,torsion,SMt) = out
        eid = (eid-self.deviceCode) // 10
        assert eid >= 0
        dt = self.dt

        #self.eType[eid] = self.elementType
        self.axial[dt][eid]      = axial
        self.MS_axial[dt][eid]   = SMa
        self.torsion[dt][eid]    = torsion
        self.MS_torsion[dt][eid] = SMt

    def addNewEidTransient_format2_sort1(self,out):
        (eid,axialReal,axialImag,torsionReal,torsionImag) = out
        eid = (eid-self.deviceCode) // 10
        assert eid >= 0
        dt = self.dt
        self.axial[dt][eid]      = [axialReal,axialImag]
        self.torsion[dt][eid]    = [torsionReal,torsionImag]

    def __reprTransient_format1_sort0__(self):
        msg = '---ROD STRAINS---\n'
        msg += '%-6s %6s ' %('EID','eType')
        headers = ['axial','torsion','MS_axial','MS_torsion']
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for dt,axial in sorted(self.axial.iteritems()):
            msg += '%s = %g\n' %(self.dataCode['name'],dt)
            for eid in sorted(axial):
                axial   = self.axial[dt][eid]
                torsion = self.torsion[dt][eid]
                SMa     = self.MS_axial[dt][eid]
                SMt     = self.MS_torsion[dt][eid]
                msg += '%-6i %6s ' %(eid,self.eType)
                vals = [axial,torsion,SMa,SMt]
                for val in vals:
                    if abs(val)<1e-6:
                        msg += '%10s ' %('0')
                    else:
                        msg += '%10g ' %(val)
                    ###
                msg += '\n'
                #msg += "eid=%-4s eType=%s axial=%-4i torsion=%-4i\n" %(eid,self.eType,axial,torsion)
            ###
        return msg

    def __reprTransient_format2_sort1__(self):
        msg = '---COMPLEX ROD STRAINS---\n'
        msg += '%-10s %10s ' %('EID','eType')
        headers = ['axialReal','axialImag','torsionReal','torsionImag']
        for header in headers:
            msg += '%10s ' %(header)
        msg += '\n'

        for dt,axial in sorted(self.axial.iteritems()):
            msg += '%s = %g\n' %(self.dataCode['name'],dt)
            for eid in sorted(axial):
                axial   = self.axial[dt][eid]
                torsion = self.torsion[dt][eid]
                msg += '%-6i %6s ' %(eid,self.eType)
                vals = axial + torsion # concatination
                for val in vals:
                    if abs(val)<1e-6:
                        msg += '%10s ' %('0')
                    else:
                        msg += '%10g ' %(val)
                    ###
                msg += '\n'
                #msg += "eid=%-4s eType=%s axial=%-4i torsion=%-4i\n" %(eid,self.eType,axial,torsion)
            ###
        return msg

    def writeF06(self,header,pageStamp,pageNum=1):
        if self.isTransient:
            return self.writeF06Transient(header,pageStamp,pageNum)

        msg = header+['                                       S T R A I N S   I N   R O D   E L E M E N T S      ( C R O D )\n',
                 '       ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY       ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY\n',
                 '         ID.        STRAIN       MARGIN        STRAIN      MARGIN         ID.        STRAIN       MARGIN        STRAIN      MARGIN\n']
        out = []
        for eid in sorted(self.axial):
            axial   = self.axial[eid]
            MSa     = self.MS_axial[eid]
            torsion = self.torsion[eid]
            MSt     = self.MS_torsion[eid]
            (vals2,isAllZeros) = self.writeF06Floats13E([axial,torsion])
            (axial,torsion) = vals2
            out.append([eid,axial,MSa,torsion,MSt])
        
        nOut = len(out)
        nWrite = nOut
        if nOut%2==1:
            nWrite = nOut-1
        for i in range(0,nWrite,2):
            outLine = '      %8i   %13s  %10.4E %13s  %10.4E   %8i   %13s  %10.4E %13s  %10.4E\n' %(tuple(out[i]+out[i+1]))
            msg.append(outLine)
        
        if nOut%2==1:
            outLine = '      %8i   %13s  %10.4E %13s  %10.4E\n' %(tuple(out[-1]))
            msg.append(outLine)
        msg.append(pageStamp+str(pageNum)+'\n')
        return(''.join(msg),pageNum)

    def writeF06Transient(self,header,pageStamp,pageNum=1):
        words = ['                                       S T R A I N S   I N   R O D   E L E M E N T S      ( C R O D )\n',
                 '       ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY       ELEMENT       AXIAL       SAFETY      TORSIONAL     SAFETY\n',
                 '         ID.        STRAIN       MARGIN        STRAIN      MARGIN         ID.        STRAIN       MARGIN        STRAIN      MARGIN\n']
        msg = []
        for dt,axials in sorted(self.axial.iteritems()):
            dtLine = '%14s = %12.5E\n'%(self.dataCode['name'],dt)
            header[2] = dtLine
            msg += header+words
            out = []
            for eid in sorted(axials):
                axial   = self.axial[dt][eid]
                MSa     = self.MS_axial[dt][eid]
                torsion = self.torsion[dt][eid]
                MSt     = self.MS_torsion[dt][eid]

                out.append([eid,axial,MSa,torsion,MSt])

            nOut = len(out)
            nWrite = nOut
            if nOut%2==1:
                nWrite = nOut-1
            for i in range(0,nWrite,2):
                outLine = '      %8i   %13.6E  %10.4E %13.6E  %10.4E   %8i   %13.6E  %10.4E %13.6E  %10.4E\n' %(tuple(out[i]+out[i+1]))
                msg.append(outLine)

            if nOut%2==1:
                outLine = '      %8i   %13.6E  %10.4E %13.6E  %10.4E\n' %(tuple(out[-1]))
                msg.append(outLine)
            msg.append(pageStamp+str(pageNum)+'\n')
            pageNum+=1
        return(''.join(msg),pageNum-1)

    def __repr__(self):
        if   self.isTransient and self.code==[1,0,10]:
            return self.__reprTransient_format1_sort0__()
        elif self.code==[2,1,10]:
            return self.__reprTransient_format2_sort1__()

        msg = '---ROD STRAINS---\n'
        msg += '%-6s %6s ' %('EID','eType')
        headers = ['axial','torsion','MS_tension','MS_compression']
        for header in headers:
            msg += '%8s ' %(header)
        msg += '\n'

        for eid in sorted(self.axial):
            axial   = self.axial[eid]
            torsion = self.torsion[eid]
            SMa     = self.MS_axial[eid]
            SMt     = self.MS_torsion[eid]
            msg += '%-6i %6s ' %(eid,self.eType)
            vals = [axial,torsion,SMa,SMt]
            for val in vals:
                if abs(val)<1e-7:
                    msg += '%8s ' %('0')
                else:
                    msg += '%8.3g ' %(val)
                ###
            msg += '\n'
        return msg

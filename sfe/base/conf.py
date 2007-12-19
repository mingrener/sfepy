import os.path as op
import re
import types
import sys

from base import Struct, IndexedStruct, dictToStruct, pause
from reader import Reader

##
# 20.06.2007, c
# 17.10.2007
def transform_toStruct_1( adict ):
    return dictToStruct( adict, flag = (1,) )
def transform_toIStruct_1( adict ):
    return dictToStruct( adict, flag = (1,), constructor = IndexedStruct )
def transform_toStruct_01( adict ):
    return dictToStruct( adict, flag = (0,1) )
def transform_toStruct_10( adict ):
    return dictToStruct( adict, flag = (1,0) )
def transform_fields( adict ):
    for key, val in adict.iteritems():
        adict[key] = dictToStruct( val, flag = (1,) )
    return adict
def transform_bc( adict ):
    if adict is None: return None
    for key, bcs in adict.iteritems():
        if type( bcs[0] ) == str:
            adict[key] = (bcs,)
    return adict

transforms = {
    'options'  : transform_toIStruct_1,
    'solvers'  : transform_toStruct_01,
    'integrals': transform_toStruct_01,
    'opt'      : transform_toStruct_1,
    'fe'       : transform_toStruct_1,
    'regions'  : transform_toStruct_01,
    'shapeOpt' : transform_toStruct_10,
    'fields'   : transform_fields,
    'ebc'      : transform_bc,
    'epbc'     : transform_bc,
    'nbc'      : transform_bc,
    'lcbc'     : transform_bc,
}

##
# 27.10.2005, c
class ProblemConf( Struct ):
    ##
    # 25.07.2006, c
    # 19.09.2006
    # 16.10.2006
    # 31.05.2007
    # 05.06.2007
    def fromFile( fileName, required = None, other = None ):
        sys.path.append( op.dirname( fileName ) )
        read = Reader( '.' )
        obj = read( ProblemConf, op.splitext( fileName )[0] )
        otherMissing = obj.validate( required = required, other = other )
        for name in otherMissing:
            setattr( obj, name, None )
        obj._fileName = fileName
        obj.transformInput()
        return obj
    fromFile = staticmethod( fromFile )

    ##
    # 20.06.2007, c
    def fromModule( module, required = None, other = None ):
        obj = ProblemConf()
        obj.__dict__.update( module.__dict__ )
        return obj
    fromModule = staticmethod( fromModule )

    ##
    # 27.10.2005, c
    # 19.09.2006
    # 05.06.2007
    def _validateHelper( self, items, butNots ):
        keys = self.__dict__.keys()
        leftOver = keys[:]
        if butNots is not None:
            for item in butNots:
                match = re.compile( '^' + item + '$' ).match
                for key in keys:
                    if match( key ):
                        leftOver.remove( key )

        missing = []
        if items is not None:
            for item in items:
                found = False
                match = re.compile( '^' + item + '$' ).match
                for key in keys:
                    if match( key ):
                        found = True
                        leftOver.remove( key )
                if not found:
                    missing.append( item )
        return leftOver, missing

    ##
    # 27.10.2005, c
    # 16.10.2006
    def validate( self, required = None, other = None ):
        requiredLeftOver, requiredMissing \
                          = self._validateHelper( required, other )
        otherLeftOver, otherMissing \
                       = self._validateHelper( other, required )

        assert requiredLeftOver == otherLeftOver

        err = False
        if requiredMissing:
            err = True
            print 'error: required missing:', requiredMissing

        if otherMissing:
            print 'warning: other missing:', otherMissing

        if otherLeftOver:
            print 'warning: left over:', otherLeftOver

        if err:
            raise ValueError

        return otherMissing

    ##
    # 31.10.2005, c
    # 01.11.2005
    # 02.11.2005
    # 14.11.2005
    # 14.12.2005
    # 21.12.2005
    # 20.01.2006
    # 29.01.2006
    # 17.02.2006
    # 14.04.2006
    # 19.04.2006
    # 25.07.2006
    # 12.02.2007
    # 14.02.2007
    # 31.05.2007
    # 20.06.2007
    # 23.10.2007
    def transformInput( self ):
        """Trivial input transformations."""

        ##
        # Unordered inputs.
        trList = ['([a-zA-Z0-9]+)_[0-9]+']
        # Keywords not in 'required', but needed even empty (e.g. for runTests).
        mustHave = {'regions' : {}, 'solvers' : {}, 'options' : {}}
        for key, val in mustHave.iteritems():
            if not self.__dict__.has_key( key ):
                self.__dict__[key] = val

        keys = self.__dict__.keys()
        for item in trList:
            match = re.compile( item ).match
            for key in keys:
                obj = match( key )
                if obj:
                    new = obj.group( 1 ) + 's'
                    result = {key : self.__dict__[key]}
                    try:
                        self.__dict__[new].update( result )
                    except:
                        self.__dict__[new] = result
                        
                    del self.__dict__[key]

        keys = self.__dict__.keys()
        for key, transform in transforms.iteritems():
            if not key in keys: continue
            self.__dict__[key] = transform( self.__dict__[key] )

        # Make module from the input file.
        name = op.splitext( op.basename( self._fileName ) )[0]
        self.funmod = __import__( name )

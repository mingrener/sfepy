from sfe.base.base import *
import extmods.terms as terms
from sfe.base.la import splitRange
#from sfe.base.ioutils import readCacheData, writeCacheData

_matchVar = re.compile( '^virtual$|^state(_[a-zA-Z0-9]+)?$'\
                        + '|^parameter(_[a-zA-Z0-9]+)?$' ).match
_matchState = re.compile( '^state(_[a-zA-Z0-9]+)?$' ).match
_matchParameter = re.compile( '^parameter(_[a-zA-Z0-9]+)?$' ).match
_matchMaterial = re.compile( '^material(_[a-zA-Z0-9]+)?$' ).match
_matchMaterialRoot = re.compile( '(.+)\.(.*)' ).match

##
# 21.11.2005, c
# 04.01.2006
# 08.01.2006
def vectorChunkGenerator( totalSize, chunkSize, shapeIn,
                          zero = False, setShape = True ):
    if not chunkSize:
        chunkSize = totalSize
    shape = list( shapeIn )

    sizes = splitRange( totalSize, chunkSize )
    ii = 0
    for size in sizes:
        chunk = nm.arange( size, dtype = nm.int32 ) + ii
        if setShape:
            shape[0] = size
        if zero:
            out = nm.zeros( shape, dtype = nm.float64 )
        else:
            out = nm.empty( shape, dtype = nm.float64 )
        yield out, chunk
        ii += size

##
# 22.01.2006, c
class CharacteristicFunction( Struct ):
    ##
    # 22.01.2006, c
    # 11.08.2006
    # 05.09.2006
    def __init__( self, region ):
        self.igs = region.igs
        self.region = region
        self.iCurrent = None
        self.localChunk = None

    ##
    # 22.01.2006, c
    # 11.08.2006
    # 05.09.2006
    def __call__( self, chunkSize, shapeIn, zero = False, setShape = True ):
        els = self.region.cells[self.ig]
        for out, chunk in vectorChunkGenerator( els.shape[0], chunkSize,
                                                shapeIn, zero, setShape ):
            self.localChunk = chunk
            yield out, els[chunk]

        self.localChunk = None

    ##
    # 11.08.2006, c
    # 27.02.2007
    def setCurrentGroup( self, ig ):
        self.ig = ig
        
    ##
    # 05.09.2006, c
    def getLocalChunk( self ):
        return self.localChunk

##
# 24.07.2006, c
class Terms( Container ):

    ##
    # 24.07.2006, c
    def classifyArgs( self ):
        for term in self:
            term.classifyArgs()
            
    ##
    # 24.07.2006, c
    # 02.08.2006
    def getVariableNames( self ):
        out = []
        for term in self:
            out.extend( term.getVariableNames() )
        return list( set( out ) )

    ##
    # 24.07.2006, c
    # 02.08.2006
    def getMaterialNames( self ):
        out = []
        for term in self:
            out.extend( term.getMaterialNames() )
        return list( set( out ) )

    ##
    # 24.07.2006, c
    # 02.08.2006
    def getUserNames( self ):
        out = []
        for term in self:
            out.extend( term.getUserNames() )
        return list( set( out ) )

    ##
    # 11.08.2006, c
    def setCurrentGroup( self, ig ):
        for term in self:
            term.charFun.setCurrentGroup( ig )

Volume = 'Volume'
Surface = 'Surface'
Edge = 'Edge'
Point = 'Point'
SurfaceExtra = 'SurfaceExtra'

##
# 21.07.2006, c
class Term( Struct ):
    name = ''
    argTypes = ()
    geometry = []

    ##
    # 24.07.2006, c
    # 25.07.2006
    # 11.08.2006
    # 24.08.2006
    # 11.10.2006
    # 29.11.2006
    def __init__( self, region, name, sign, function = None ):
        self.charFun  = CharacteristicFunction( region )
        self.region = region
        self.name = name
        self.sign = sign
        self.dofConnType = 'volume'
        self.function = function
        
        itype = None
        aux = re.compile( '([a-z]+)_.*' ).match( name )
        if aux:
            itype = aux.group( 1 )
        self.itype = itype
        self.ats = list( self.argTypes )

    ##
    # 02.08.2006, c
    def __call__( self, diffVar = None, chunkSize = None, **kwargs ):
        output( 'base class method called for %s' % self.__class__.__name__ )
        raise RuntimeError
        
    ##
    # 16.11.2005, c
    def getArgNames( self ):
        return self.__argNames

    def setArgNames( self, val ):
        if len( val ) != len( self.__class__.argTypes ):
            raise ValueError, 'equal shapes: %s, %s' \
                  % (val, self.__class__.argTypes)
        self.__argNames = val
    argNames = property( getArgNames, setArgNames )

    ##
    # 24.07.2006, c
    # 25.07.2006
    # 02.08.2006
    # 14.09.2006
    # 26.07.2007
    def classifyArgs( self ):
        self.names = Struct( name = 'arg_names',
                             material = [], variable = [], user = [],
                             state = [], virtual = [], parameter = [],
                             materialSplit = [] )
        for ii, argType in enumerate( self.argTypes ):
            name = self.__argNames[ii]
            if _matchVar( argType ):
                names = self.names.variable
                if _matchState( argType ):
                    self.names.state.append( name )
                elif argType == 'virtual':
                    self.names.virtual.append( name )
                elif _matchParameter( argType ):
                    self.names.parameter.append( name )
            elif _matchMaterial( argType ):
                names = self.names.material
                match = _matchMaterialRoot( name )
                if match:
                    self.names.materialSplit.append( (match.group( 1 ),
                                                      match.group( 2 )) )
                else:
                    self.names.materialSplit.append( (name, None) )
            else:
                names = self.names.user
            names.append( name )
        
    ##
    # 24.07.2006, c
    def getVariableNames( self ):
        return self.names.variable

    ##
    # 24.07.2006, c
    # 02.08.2006
    def getMaterialNames( self ):
        return [aux[0] for aux in self.names.materialSplit]

    ##
    # 24.07.2006, c
    def getUserNames( self ):
        return self.names.user

    ##
    # 24.07.2006, c
    # 25.07.2006
    def getVirtualName( self ):
        return self.names.virtual[0]

    ##
    # 24.07.2006, c
    # 25.07.2006
    def getStateNames( self ):
        return copy( self.names.state )

    ##
    # 26.07.2007, c
    def getParameterNames( self ):
        return copy( self.names.parameter )

    ##
    # 24.07.2006, c
    # 02.08.2006
    # 03.08.2006
    # 14.09.2006
    def getArgs( self, argTypes = None, **kwargs ):
        ats = self.ats
        if argTypes is None:
            argTypes = ats
        args = []

        iname, tregionName, aregionName, ig = self.getCurrentGroup()
        for at in argTypes:
            ii = ats.index( at )
            name = self.argNames[ii]
##             print at, ii, name
            if at[:8] == 'material':
##                 print self.names.material
                im = self.names.material.index( name )
                split = self.names.materialSplit[im]
                mat = kwargs[split[0]]
                args.append( mat.getData( tregionName, ig, split[1] ) )
            else:
                args.append( kwargs[name] )
        return args

    ##
    # 24.07.2006, c
    def getArgName( self, argType ):
        ii = self.ats.index( argType )
        return self.argNames[ii]

    ##
    #
    def describeGeometry( self, geometries, variables, integrals ):

        integral = integrals[self.integralName]
        integral.createQP()
        tgs = self.getGeometry()
        for varName in self.getVariableNames():
##             print '>>>>>', self.name, varName

            variable = variables[varName]
            field = variable.field
            assert field.region.contains( self.region )
            
##             print field.name, field.regionName
##             print field.bases

            if tgs.has_key( varName ):
##                 print tgs[varName]
                field.aps.describeGeometry( field, geometries,
                                            tgs[varName], integral )

            self.regionMap = {}
            for regionName, ig, ap in field.aps.iterAps( all = True ):
                self.regionMap.setdefault( ig, [] ).append( regionName )
##             print self.regionMap

    ##
    # 23.08.2006, c
    # 24.08.2006
    def getGeometry( self ):
        geom = self.__class__.geometry
        if geom:
            out = {}
            for (gtype, argType) in geom:
                argName = self.getArgName( argType )
                out[argName] = Struct( gtype = gtype,
                                       region = self.region )
            return out
        else:
            return None

    ##
    # 28.08.2006, c
    def getCurrentGroup( self ):
        return (self.integralName, self.region.name,
                self.charFun.currentRegionName, self.charFun.ig)

    ##
    # 11.10.2006, c
    def getDofConnType( self ):
        return self.dofConnType, self.region.name

    ##
    # 16.02.2007, c
    def setCurrentGroup( self, regionName, ig ):
        self.charFun.setCurrentGroup( ig )
        self.charFun.currentRegionName = regionName

    ##
    # 27.02.2007, c
    def getCache( self, baseName, ii ):
        args = self.__class__.useCaches[baseName][ii]
        ans = [self.getArgName( arg ) for arg in args]
        cname = '_'.join( [baseName] + ans )
        return self.caches[cname]

    ##
    # 02.03.2007, c
    def igs( self ):
        return self.charFun.igs

    ##
    #
    def iterGroups( self ):
        if self.dofConnType == 'point':
            igs = self.igs()[0:1]
        else:
            igs = self.igs()
        for ig in igs:
            regionNames = self.regionMap[ig]
            for regionName in regionNames:
                self.setCurrentGroup( regionName, ig )
                yield regionName, ig

from base import *
import inspect

##
# 30.05.2007, c
class TestCommon( Struct ):

    ##
    # 16.07.2007, c
    def getNumber( self ):
        methods = inspect.getmembers( self, inspect.ismethod )
        tests = [ii for ii in methods
                 if (len( ii[0] ) > 5) and ii[0][:5] == 'test_']
        return len( tests )

    ##
    # 30.05.2007, c
    # 16.07.2007
    def run( self, debug = False ):
        ok = True
        nFail = 0

        methods = inspect.getmembers( self, inspect.ismethod )
        tests = [ii for ii in methods
                 if (len( ii[0] ) > 5) and ii[0][:5] == 'test_']

        for testName, testMethod in tests:
            aux = ' %s: ' % testName

            try:
                ret = testMethod()
            except:
                if debug:
                    raise
                ret = False
                
            if not ret:
                aux = '---' + aux + 'failed!'
                nFail += 1
                ok = False
            else:
                aux = '+++' + aux + 'ok'

            print aux

        return ok, nFail, len( tests )

    ##
    # 31.05.2007, c
    def report( text ):
        """All tests should print via this function."""
        print '... ' + text
    report = staticmethod( report )

    ##
    # 30.05.2007, c
    def evalCoorExpression( expression, coor ):

        x = coor[:,0]
        y = coor[:,1]
        if coor.shape[1] == 3:
            z = coor[:,2]
        else:
            z = None

        coorDict = {'x' : x, 'y' : y, 'z' : z}
        out = eval( expression, globals(), coorDict )
        
        return out
    evalCoorExpression = staticmethod( evalCoorExpression )

    ##
    # 30.05.2007, c
    def compareVectors( vec1, vec2, allowedError = 1e-8,
                        label1 = 'vec1', label2 = 'vec2' ):

        diffNorm = nla.norm( vec1 - vec2 )
        TestCommon.report( '||%s - %s||: %e' % (label1, label2, diffNorm) )
        if diffNorm > allowedError:
            return False
        else:
            return True
    compareVectors = staticmethod( compareVectors )

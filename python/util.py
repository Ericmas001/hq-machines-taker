import sys

class Console:
    @staticmethod
    def Write(str, *args):
        sys.stdout.write(str.format(*args))
        sys.stdout.flush()

    @staticmethod
    def WriteLine(str, *args):
        print str.format(*args)
        
    @staticmethod
    def DebugLine(str, *args):
    #    print "DEBUG " + str.format(*args)    
        sys.stdout.flush()
from tests.test_server import ServerAllowedFileTest, ServerOtherTest, ServerImportShapefileShp2pgsql
from tests.test_util import UtilTest, Util1Test
import unittest


testServerList = [
    ServerAllowedFileTest,
    ServerOtherTest,
    ServerImportShapefileShp2pgsql
]
testUtilList = [UtilTest, Util1Test]

testList = []
testList.extend(testServerList)
# testList.extend(testUtilList)

testLoad = unittest.TestLoader()

caseList = []
for testCase in testList:
    testSuite = testLoad.loadTestsFromTestCase(testCase)
    caseList.append(testSuite)

newSuite = unittest.TestSuite(caseList)
unittest.TextTestRunner().run(newSuite)

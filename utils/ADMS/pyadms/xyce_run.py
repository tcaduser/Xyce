import pyadms.adms_loader
import pyadms.xyce_implicit as xyce_implicit

admst = pyadms.adms_loader.load_json('foo.json')
dv = xyce_implicit.dependency_visitor()
admst.get_module().visit(dv)

#from . import xyceVersion
import pyadms.xyceVersion as xyceVersion
xyceVersion.run()
print(admst.get_simulator().__dict__)

#import pyadms.xyceBasicTemplates as xyceBasicTemplates 
#xyceBasicTemplates.BasicData().run()

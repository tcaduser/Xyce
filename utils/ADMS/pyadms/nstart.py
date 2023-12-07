import pyadms.adms_loader
import pyadms.adms_implicit as adms_implicit

admst = pyadms.adms_loader.load_json('foo.json')
dv = adms_implicit.dependency_visitor()
admst.get_module().visit(dv)

#from . import xyceVersion
import pyadms.xyceVersion as xyceVersion
xyceVersion.run()
print(admst.get_simulator().__dict__)



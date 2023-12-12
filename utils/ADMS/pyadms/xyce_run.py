import pyadms.adms_loader
import pyadms.xyce_implicit as xyce_implicit
import sys


# Run the implicit rules
admst = pyadms.adms_loader.load_json(sys.argv[1])
dv = xyce_implicit.dependency_visitor()
admst.get_module().visit(dv)

# Set the simulator version information
import pyadms.xyceVersion as xyceVersion
xyceVersion.run()
print(admst.get_simulator().__dict__)

#import pyadms.xyceBasicTemplates as xyceBasicTemplates 
#xyceBasicTemplates.BasicData().run()

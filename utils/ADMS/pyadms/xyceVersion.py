from . import adms_loader

def run():
    simulator = adms_loader.admst.get_simulator()
    simulator.package_name="Xyce"
    simulator.package_tarname="Xyce"
    simulator.package_version="7.7.0"
    simulator.package_string="Xyce 7.7.0"
    simulator.package_bugreport="xyce@sandia.gov"


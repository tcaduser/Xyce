'''
  Purpose:  Provide a basic set of ADMST templates for working on Xyce
            mo
      Creator:   Tom Russo, SNL, Electrical and Microsystems Modeling
      Creation Date: 8 May 2008

     Copyright 2002-2023 National Technology & Engineering Solutions of
     Sandia, LLC (NTESS).  Under the terms of Contract DE-NA0003525 with
     NTESS, the U.S. Government retains certain rights in this software.

     This file is part of the Xyce(TM) Parallel Electrical Simulator.

     Xyce(TM) is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation, either version 3 of the License, or
     (at your option) any later version.

     Xyce(TM) is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.

     You should have received a copy of the GNU General Public License
     along with Xyce(TM).
     If not, see <http://www.gnu.org/licenses/>.


   =================================================================-
   =================================================================-
    simple templates for producing commonly-used information
   =================================================================-
   =================================================================-
'''
from .adms_loader import admst
#<!-- declare a global var used for collectAssignedVariables-->
class BasicData:
    def __init__(self):
        self.theGlobalAssignedVarsTarget = None
#<!-- some variables we'll use later -->
#<!-- This one will be set to the current probe with respect to which we're
#     differentiating -->
        self.derivProbe = None
        self.derivProbe2 = None
        self.initializeOnDeclare = False
        self.probeList =  []
        self.doSecondDerivs = False
        self.collapseFailure = False
        self.extraProbeBranches = []

    def run(self):
        module = admst.get_module()

        node = list(module.node.get_list())
        # TODO: fix optional
        for n in node:
            n.optional = False

        notgroundednode = [n for n in node if not n.grounded]

        self.xyceNumberNodes = len([n for n in node if not n.grounded])
        self.xyceNumberProbes = module.probe.size() + len(self.extraProbeBranches)
        self.xyceNumberInternalNodes = len([n for n in notgroundednode if ((n.location == 'internal'))])
        self.xyceNumberExternalNodes = len([n for n in notgroundednode if ((n.location == 'external'))])
        self.xyceNumberOptionalNodes = len([n for n in notgroundednode if ((n.location == 'external') and (n.optional))])
        self.xyceNumberRequiredNodes = len([n for n in notgroundednode if ((n.location == 'external') and (not n.optional))])
        if self.xyceNumberExternalNodes == 2:
            self.xyceNumberLeadCurrents = 1
        else:
            self.xyceNumberLeadCurrents = self.xyceNumberExternalNodes

        self.xyceDeviceNamespace = f'ADMS{module.name}'
        self.xyceClassBaseName = f'N_DEV_ADMS{module.name}'
        self.xyceInstanceClassName = f'N_DEV_ADMS{module.name}Instance'
        self.xyceModelClassName = f'N_DEV_ADMS{module.name}Model'
        self.xyceGuardSymbol =  f'Xyce_N_DEV_ADMS{module.name}_h'

    def xyceNodeConstantName(self, node):
        return f'admsNodeID_{node.name}'

    def xyceBranchConstantName(self, branch):
        return f'admsBRA_ID_{branch.pnode.name}_{branch.node.name}'
    
    def xyceProbeConstantName(self, probe):
        return f'admsProbeID_{probe.nature.name}_{probe.branch.pnode.name}_{probe.branch.nnode.name}'

    def xycePotentialProbeConstantName(self, branch):
        return f'admsProbeID_V_{probe.nature.name}_{branch.pnode.name}_{branch.nnode.name}'

    def xyceFlowProbeConstantName(self, branch):
        return f'admsProbeID_I_{probe.nature.name}_{branch.pnode.name}_{branch.nnode.name}'

#  <admst:template match="xyceJacobianOffsetName">
#    <admst:text format="A_%(row/name)_Equ_%(column/name)_NodeOffset"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xycedFdXPtrName
#    given a jacobian element, generate the name of the pointer var
#    used to identify its location
#   =================================================================-
#  -->
#  <admst:template match="xycedFdXPtrName">
#    <admst:text format="f_%(row/name)_Equ_%(column/name)_Node_Ptr"/>
#  </admst:template>
#  <!--
#   =================================================================-
#   xycedQdXPtrName
#    given a jacobian element, generate the name of the pointer var
#    used to identify its location
#   =================================================================-
#  -->
#  <admst:template match="xycedQdXPtrName">
#    <admst:text format="q_%(row/name)_Equ_%(column/name)_Node_Ptr"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#    xyceDeclareVariable
#    Given a variable, emit a C++ declaration for that variable
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareVariable">
#    <admst:assert test="adms[datatypename='variable' or datatypename='variableprototype']" format="xyceDeclareVariable expecting datatypename=variable or variableprototype, got %(adms/datatypename)"/>
#    <admst:choose>
#      <admst:when test="[type='real' and exists(probe) and not($globalCurrentScope='sensitivity')]">
#        <admst:text format="double"/>
#      </admst:when>
#      <!-- Bah.  Looks like "variable" dependency doesn't get propagated past
#           one level.
#
#           Tried having  and exists(variable[input='yes']) here, and it
#           seems to have missed some.  So we have to make ALL reals in
#           sensitivity be FADS
#      -->
#      <admst:when test="[type='real' and $globalCurrentScope='sensitivity' and exists(#Pdependent)]">
#        <admst:text format="double"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:apply-templates select="." match="verilog2CXXtype"/>
#      </admst:otherwise>
#    </admst:choose>
#    <admst:text format=" %(name)"/>
#    <admst:if test="[$initializeOnDeclare='yes']">
#      <admst:text format="=0.0"/>
#    </admst:if>
#    <admst:text format=";\n"/>
#    <admst:if test="[type='real' and $globalCurrentScope='sensitivity' and exists(#Pdependent)]">
#        <admst:text format="double d_%(name)_dX=0.0;\n"/>
#    </admst:if>
#    <admst:if test="[type='real' and exists(probe) and not($globalCurrentScope='sensitivity') and (insource='yes' or not(nilled(ddxprobe)))]">
#      <admst:variable name="myVar" path="."/>
#      <admst:for-each select="probe">
#        <admst:variable name="myprobe" path="."/>
#        <admst:text format="    "/>
#        <admst:text format=" double d_%($myVar/name)_d%(nature)_%(branch/pnode)_%(branch/nnode)"/>
#        <admst:if test="[$initializeOnDeclare='yes']">
#          <admst:text format="=0.0"/>
#        </admst:if>
#        <admst:text format=";\n"/>
#        <admst:if test="[../insource='yes' and $doSecondDerivs='yes']">
#          <!-- this looks fishy to me and presupposes that all ddxprobes are of form V(X,GND), 
#               and never V(X,Y) but the former is pretty much what all ddx() usage is in the wild.  -->
#          <admst:if test="[exists($myVar/ddxprobe/branch/pnode[.=$myprobe/branch/pnode or .=$myprobe/branch/nnode])]">
#            <admst:for-each select="$myVar/probe">
#              <admst:text format="    "/>
#              <admst:text format=" double d_%($myVar/name)_d%($myprobe/nature)_%($myprobe/branch/pnode)_%($myprobe/branch/nnode)_d%(./nature)_%(./branch/pnode)_%(./branch/nnode)"/>
#              <admst:if test="[$initializeOnDeclare='yes']">
#                <admst:text format="=0.0"/>
#              </admst:if>
#              <admst:text format=";\n"/>
#            </admst:for-each>
#          </admst:if>
#        </admst:if>
#      </admst:for-each>
#    </admst:if>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   =================================================================-
#    Specialized templates for dealing with guessing device model cards
#    and/or header files to include
#   =================================================================-
#   -->
#
#   <!--
#   =================================================================-
#   xyceIncludeModelBaseHeader
#   Given a module, this template generates an appropriate "#include"
#   for the base device IF the module has a "xyceModelGroup" attribute.
#   If the attribute doesn't exist, no include is generated.
#
#   Recognized groups:        Header included:
#      MOSFET                  N_DEV_MOSFET1.h
#      <anything else>         N_DEV_<that>.h
#   =================================================================-
#   -->
#   <admst:template match="xyceIncludeModelBaseHeader">
#     <admst:choose>
#       <admst:when test="[exists(attribute[name='xyceModelGroup'])]">
#         <admst:choose>
#           <admst:when test="[attribute[name='xyceModelGroup']/value='MOSFET']">
#             <admst:text format="#include &lt;N_DEV_MOSFET1.h&gt;\n"/>
#           </admst:when>
#           <admst:when test="[attribute[name='xyceModelGroup']/value='BJT' 
#                       or attribute[name='xyceModelGroup']/value='JFET'
#                       or attribute[name='xyceModelGroup']/value='Diode' 
#                       or attribute[name='xyceModelGroup']/value='Resistor' 
#                       or attribute[name='xyceModelGroup']/value='Capacitor']">
#             <admst:text format="#include &lt;N_DEV_%(attribute[name='xyceModelGroup']/value).h&gt;\n"/>
#           </admst:when>
#           <admst:otherwise>
#             <admst:fatal format="Xyce-specific module attribute xyceModelGroup given but has unknown value %(attribute[name='xyceModelGroup']/value).  Please remove this attribute.\n"/>
#           </admst:otherwise>
#         </admst:choose>
#       </admst:when>
#     </admst:choose>
#   </admst:template>
#
#   <!--
#   =================================================================-
#   xyceDeclareTraits
#   Given a module, this template generates an appropriate "typedef"
#   for the DeviceTraits.  IF the module has a "xyceModelGroup" attribute,
#   then this uses the base group instance as the group in the template.
#   If the attribute doesn't exist, no base group is used.
#
#   Recognized groups:        Base instance:
#      MOSFET                  MOSFET1
#      <anything else>         <verbatim>
#   =================================================================-
#   -->
#   <admst:template match="xyceDeclareTraits">
#struct Traits: public DeviceTraits&lt;Model, Instance
#     <admst:choose>
#       <admst:when test="[exists(attribute[name='xyceModelGroup'])]">
#         <admst:choose>
#           <admst:when test="[attribute[name='xyceModelGroup']/value='MOSFET']">
#             <admst:text format=", MOSFET1::Traits"/>
#           </admst:when>
#           <admst:otherwise>
#             <admst:text format=", %(attribute[name='xyceModelGroup']/value)::Traits"/>
#           </admst:otherwise>
#         </admst:choose>
#       </admst:when>
#     </admst:choose>&gt;
#{
#
#    <!-- Figure out a level number -->
#    <admst:choose>
#      <admst:when test="[exists(attribute[name='xyceLevelNumber'])]">
#        <admst:variable name="theLevelNumber" select="%(attribute[name='xyceLevelNumber']/value)"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:variable name="theLevelNumber" select="1"/>
#      </admst:otherwise>
#    </admst:choose>
#
#    <!-- Choose a device name -->
#    <admst:choose>
#      <admst:when test="[exists(attribute[name='xyceDeviceName'])]">
#        <admst:variable name="theDeviceName" select="%(attribute[name='xyceDeviceName']/value)"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:variable name="theDeviceName" select="ADMS %(name)"/>
#      </admst:otherwise>
#    </admst:choose>
#
#    <!-- Figure out what spice symbol we use -->
#    <admst:choose>
#      <admst:when test="[exists(attribute[name='xyceSpiceDeviceName'])]">
#        <admst:variable name="theSpiceDevice" select="%(attribute[name='xyceSpiceDeviceName']/value)"/>
#      </admst:when>
#      <admst:when test="[exists(attribute[name='xyceModelGroup'])]">
#        <admst:choose>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='MOSFET']">
#            <admst:variable name="theSpiceDevice" select="m"/>
#          </admst:when>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='JFET']">
#            <admst:variable name="theSpiceDevice" select="j"/>
#          </admst:when>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='BJT']">
#            <admst:variable name="theSpiceDevice" select="q"/>
#          </admst:when>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='Diode']">
#            <admst:variable name="theSpiceDevice" select="d"/>
#          </admst:when>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='Resistor']">
#            <admst:variable name="theSpiceDevice" select="r"/>
#          </admst:when>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='Capacitor']">
#            <admst:variable name="theSpiceDevice" select="c"/>
#          </admst:when>
#        </admst:choose>
#      </admst:when>
#      <admst:otherwise>
#        <admst:variable name="theSpiceDevice" select="%(.)"/>
#      </admst:otherwise>
#    </admst:choose>
#
#    <admst:text format="  static const char *name() {return &quot;%($theDeviceName)&quot;;}\n"/>
#    <admst:text format="  static const char *deviceTypeName() {return &quot;%(upper-case($theSpiceDevice)) level %($theLevelNumber)&quot;;}\n"/>
#  static int numNodes() {return <admst:text format="%(xyceNumberRequiredNodes(.))"/>;}
#
#  <admst:if test="[exists(@optnodes)]">
#  static int numOptionalNodes() {return %(xyceNumberOptionalNodes(.));};
#  </admst:if>
#
#  static bool modelRequired() {return 
#     <admst:choose>
#       <admst:when test="variable[parametertype='model' and input='yes']">
#         <admst:text format="true"/>
#       </admst:when>
#       <admst:otherwise>
#         <admst:text format="false"/>
#       </admst:otherwise>
#     </admst:choose>
#     <admst:text format=";}"/>
#  static bool isLinearDevice() {return false;}
#
#  static Device *factory(const Configuration &amp;configuration, const FactoryBlock &amp;factory_block);
#  static void loadModelParameters(ParametricData&lt;Model&gt; &amp;model_parameters);
#  static void loadInstanceParameters(ParametricData&lt;Instance&gt; &amp;instance_parameters);
#};
#   </admst:template>
#
#  <!--
#   =================================================================-
#   xyceDeviceFactoryandRegisterDevice
#
#   Given a module, this template generates appropriate code for a
#   device factory and registerDevice method.  If the attribute
#   xyceDeviceName exists, we use that as the name of the device.  If
#   not, we use "ADMS <module name>".  Other expected attributes are:
#
#      xyceSpiceDeviceName:   if not given, guess at one from xyceModelGroup.
#                             If that is not given, emit a "FIXME"
#      xyceLevelNumber:       If not given, "FIXME"
#
#   -->
#  <admst:template match="xyceDeviceFactoryandRegisterDevice">
#
#    <!-- Figure out what spice symbol we use -->
#    <admst:choose>
#      <admst:when test="[exists(attribute[name='xyceSpiceDeviceName'])]">
#        <admst:variable name="theSpiceDevice" select="%(attribute[name='xyceSpiceDeviceName']/value)"/>
#      </admst:when>
#      <admst:when test="[exists(attribute[name='xyceModelGroup'])]">
#        <admst:choose>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='MOSFET']">
#            <admst:variable name="theSpiceDevice" select="m"/>
#          </admst:when>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='JFET']">
#            <admst:variable name="theSpiceDevice" select="j"/>
#          </admst:when>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='BJT']">
#            <admst:variable name="theSpiceDevice" select="q"/>
#          </admst:when>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='Diode']">
#            <admst:variable name="theSpiceDevice" select="d"/>
#          </admst:when>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='Resistor']">
#            <admst:variable name="theSpiceDevice" select="r"/>
#          </admst:when>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='Capacitor']">
#            <admst:variable name="theSpiceDevice" select="c"/>
#          </admst:when>
#        </admst:choose>
#      </admst:when>
#      <admst:otherwise>
#        <admst:variable name="theSpiceDevice" select="%(.)"/>
#      </admst:otherwise>
#    </admst:choose>
#
#    <!-- Figure out a level number -->
#    <admst:choose>
#      <admst:when test="[exists(attribute[name='xyceLevelNumber'])]">
#        <admst:variable name="theLevelNumber" select="%(attribute[name='xyceLevelNumber']/value)"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:variable name="theLevelNumber" select="1"/>
#      </admst:otherwise>
#    </admst:choose>
#
#    <!-- Now emit the factory -->
#    <admst:text format="Device *Traits::factory(const Configuration &amp;configuration, const FactoryBlock &amp;factory_block)\n"/>
#    <admst:text format="{\n"/>
#    <admst:text format="  return new DeviceMaster&lt;Traits&gt;(configuration, factory_block, factory_block.solverState_, factory_block.deviceOptions_);\n"/>
#    <admst:text format="}\n\n"/>
#
#    <!-- and the registerDevice -->
#    <admst:text format="void\nregisterDevice(const DeviceCountMap&amp; deviceMap, const std::set&lt;int&gt;&amp; levelSet)\n"/>
#    <admst:text format="{\n"/>
#    <admst:text format="if (deviceMap.empty() ||\n((deviceMap.find(&quot;%(upper-case($theSpiceDevice))&quot;) != deviceMap.end() &amp;&amp; (levelSet.find(%($theLevelNumber))!=levelSet.end()))))\n{\n"/>
#     <admst:choose>
#       <admst:when test="[exists(attribute[name='xyceModelGroup'])]">
#         <admst:choose>
#           <admst:when test="[attribute[name='xyceModelGroup']/value='MOSFET']">
#             <admst:text format="MOSFET1::registerDevice();\n"/>
#           </admst:when>
#           <admst:otherwise>
#             <admst:text format="%(attribute[name='xyceModelGroup']/value)::registerDevice();\n\n"/>
#           </admst:otherwise>
#         </admst:choose>
#       </admst:when>
#     </admst:choose>
#    <admst:text format="  Config&lt;Traits&gt;::addConfiguration()\n"/>
#    <admst:text format="    .registerDevice(&quot;%($theSpiceDevice)&quot;, %($theLevelNumber))"/>
#
#    <!-- and all the registerModelTypes... -->
#    <admst:choose>
#      <admst:when test="[exists(attribute[name='xyceModelCardType'])]">
#        <admst:for-each select="attribute[name='xyceModelCardType']">
#          <admst:text format="\n    .registerModelType(&quot;%(./value)&quot;, %($theLevelNumber))"/>
#        </admst:for-each>
#      </admst:when>
#      <admst:otherwise>
#        <admst:choose>
#          <admst:when test="[exists(attribute[name='xyceModelGroup'])]">
#            <admst:choose>
#              <admst:when  test="[attribute[name='xyceModelGroup']/value='MOSFET']">
#                <admst:text format="\n    .registerModelType(&quot;nmos&quot;, %($theLevelNumber))"/>
#                <admst:text format="\n    .registerModelType(&quot;pmos&quot;, %($theLevelNumber))"/>
#              </admst:when>
#              <admst:when  test="[attribute[name='xyceModelGroup']/value='JFET']">
#                <admst:text format="\n    .registerModelType(&quot;njf&quot;, %($theLevelNumber))"/>
#                <admst:text format="\n    .registerModelType(&quot;pjf&quot;, %($theLevelNumber))"/>
#              </admst:when>
#              <admst:when test="[attribute[name='xyceModelGroup']/value='BJT']">
#                <admst:text format="\n    .registerModelType(&quot;npn&quot;, %($theLevelNumber))"/>
#                <admst:text format="\n    .registerModelType(&quot;pnp&quot;, %($theLevelNumber))"/>
#              </admst:when>
#              <admst:when test="[attribute[name='xyceModelGroup']/value='Diode']">
#                <admst:text format="\n    .registerModelType(&quot;d&quot;, %($theLevelNumber))"/>
#              </admst:when>
#              <admst:when test="[attribute[name='xyceModelGroup']/value='Resistor']">
#                <admst:text format="\n    .registerModelType(&quot;r&quot;, %($theLevelNumber))"/>
#              </admst:when>
#              <admst:when test="[attribute[name='xyceModelGroup']/value='Capacitor']">
#                <admst:text format="\n    .registerModelType(&quot;c&quot;, %($theLevelNumber))"/>
#              </admst:when>
#            </admst:choose>
#          </admst:when>
#          <admst:otherwise>
#            <!-- If the device requires a model (i.e. there are any
#                  parameters of type "model"), and no modely type has
#                  been given in attributes, emit comments to fix the issue -->
#            <admst:if test="variable[(parametertype='model' and input='yes') or (parametertype='instance' and exists(attribute/[name='xyceAlsoModel']) and input='yes')]">
#
#                <admst:text format="\n    .registerModelType(&quot;%($theSpiceDevice)&quot;, %($theLevelNumber))\n"/>
#            </admst:if>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:otherwise>
#    </admst:choose>
#
#    <admst:text format=";\n}\n}\n\n"/>
#
#  </admst:template>
#
#
#  <!--
#   =================================================================-
#   xyceSetTypeVariable
#
#   If the module defines a xyceModelGroup AND a non-null xyceTypeVariable,
#   emit the hackish code that sets the type variable based on the model
#   card type.
#
#   Input type is a module.
#   =================================================================-
#  -->
#  <admst:template match="xyceSetTypeVariable">
#    <admst:if test="[exists(attribute[name='xyceModelGroup']) and (attribute[name='xyceModelGroup']/value='MOSFET' or attribute[name='xyceModelGroup']/value='BJT' or attribute[name='xyceModelGroup']/value='JFET')]">
#      <admst:variable name="Ptype" value="-1"/>
#      <admst:if test="[exists(attribute[name='xycePTypeValue']) and attribute[name='xyceTypePtypeValue']/value != '']">
#        <admst:variable name="Ptype" value="%(attribute[name='xycePTypeValue']/value)"/>
#      </admst:if>
#      <admst:if test="[exists(attribute[name='xyceTypeVariable']) and attribute[name='xyceTypeVariable']/value != '']">
#        <admst:text format="\n// set internal model type based on model card type\n"/>
#        <admst:choose>
#          <admst:when  test="[attribute[name='xyceModelGroup']/value='MOSFET']">
#            <admst:text format="if (getType() == &quot;pmos&quot; || getType() == &quot;PMOS&quot;)\n"/>
#          </admst:when>
#          <admst:when  test="[attribute[name='xyceModelGroup']/value='JFET']">
#            <admst:text format="if (getType() == &quot;pjf&quot; || getType() == &quot;PJF&quot;)\n"/>
#          </admst:when>
#          <admst:when test="[attribute[name='xyceModelGroup']/value='BJT']">
#            <admst:text format="if (getType() == &quot;pnp&quot; || getType() == &quot;PNP&quot;)\n"/>
#          </admst:when>
#        </admst:choose>
#        <admst:text format="    %(attribute[name='xyceTypeVariable']/value) = %($Ptype);\n"/>
#      </admst:if>
#    </admst:if>
#  </admst:template>
#
#
#  <!--
#   =================================================================-
#   =================================================================-
#    Specialized templates for declaring and initializing Instance and
#    Model variables
#   =================================================================-
#
#   =================================================================-
#   xyceDeclareInstanceVariables
#   Extract all the variables that are either instance parameters or
#   instance variables (with "global_instance" scope) and declare them
#   Give the module for "select"
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareInstanceVariables">
#    <admst:text format="    // Begin verilog Instance Variables\n"/>
#    <admst:text format="    //   Instance Parameters\n"/>
#    <admst:for-each select="variable[parametertype='instance' and input='yes']">
#      <admst:text format="    "/>
#      <admst:apply-templates select="." match="verilog2CXXtype"/>
#      <admst:text format=" %(name);\n"/>
#    </admst:for-each>
#    <admst:text format="    //  Variables of global_instance scope\n"/>
#    <admst:for-each select="variable[scope='global_instance' and input='no']">
#      <admst:text format="    "/>
#      <admst:apply-templates select="." match="xyceDeclareVariable"/>
#    </admst:for-each>
#    <admst:text format="    // end verilog Instance Variables=====\n"/>
#  </admst:template>
#
#
#  <!--
#   =================================================================-
#   xyceDeclareNodeConstants
#    Declare const integers giving the node number of all named nodes
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareNodeConstants">
#    <admst:text format="   // node numbers\n"/>
#    <admst:for-each select="node[grounded='no' and location='external']">
#      <admst:text test="[exists(#optional)]" format="// optional node %(.):\n"/>
#      <admst:text format="    static const int %(xyceNodeConstantName(.)/[name='nodeConstant']/value) = %(position(.)-1);\n"/>
#    </admst:for-each>
#    <admst:variable name="numext" select="%(count(node[grounded='no' and location='external']))"/>
#    <admst:for-each select="node[grounded='no' and location='internal']">
#      <admst:text format="    static const int %(xyceNodeConstantName(.)/[name='nodeConstant']/value) = %(position(.)-1)+$numext;\n"/>
#    </admst:for-each>
#    <admst:text format="    static const int admsNodeID_GND = -1;\n"/>
#    <admst:text format="   // end node numbers\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceDeclareBranchConstants
#    Declare const integers giving the node number of all named nodes
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareBranchConstants">
#    <admst:text format="   // Additional IDs for branch equations\n"/>
#    <admst:for-each select="/module/@extraUnknowns">
#      <admst:text format="    static const int %(xyceBranchConstantName(.)/[name='branchConstant']/value) = %(position(.)-1 + count(/module/node[grounded='no']));\n"/>
#    </admst:for-each>
#    <admst:text format="   // end branch numbers\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceDeclareProbeConstants
#    Declare const integers giving the probe number of all used probes
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareProbeConstants">
#    <admst:text format="   // Probe numbers\n"/>
#    <admst:for-each select="$thisModule/probe">
#      <admst:text format="    static const int %(xyceProbeConstantName(.)/[name='probeConstant']/value) = %(position(.)-1);\n"/>
#    </admst:for-each>
#    <admst:for-each select="@extraProbeBranches">
#      <admst:text format="    static const int %(xyceFlowProbeConstantName(.)/[name='probeConstant']/value) = %(count($thisModule/probe)+position(.)-1);\n"/>
#    </admst:for-each>
#    <admst:text format="   // end probe numbers\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceDeclareLimitedProbeStoreLIDs
#    Declare integers for store LIDs of limited probes, given a module
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareLimitedProbeStoreLIDs">
#    <admst:text format="   // Store LIDs\n"/>
#    <admst:for-each select="@limitedProbes">
#      <admst:text format="    int %(xyceLimitedProbeStoreLIDVariable(.));\n"/>
#    </admst:for-each>
#    <admst:text format="   // end store LIDs\n"/>
#  </admst:template>
#  <!--
#   =================================================================-
#   xyceDeclareOutputStoreLIDs
#    Declare integers for store LIDs of output variables, given a module
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareOutputStoreLIDs">
#    <admst:text format="   // Store LIDs for output vars\n"/>
#    <admst:for-each select="variable[output='yes' and input!='yes']">
#      <admst:text format="    int li_store_%(name);\n"/>
#    </admst:for-each>
#    <admst:text format="   // end store LIDs for output vars\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceInstanceInitializers
#   Extract all the variables that are either instance parameters or
#   instance variables (with "global_instance" scope) and generate
#   an initializer list for the constructor.
#   Give the module for "select"
#   =================================================================-
#  -->
#  <admst:template match="xyceInstanceInitializers">
#    <admst:if test="[exists(variable[(parametertype='instance' and input='yes') or (scope='global_instance' and input='no')])]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="variable[(parametertype='instance' and input='yes') or (scope='global_instance' and input='no')]" separator=",\n    ">
#      <admst:text format="%(name)("/>
#      <admst:choose>
#        <admst:when test="[exists(default) and not exists(#dependent)]">
#          <admst:text format="%(printTerm(default))"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:choose>
#            <admst:when test="[type='real']">
#              <admst:text format="0.0"/>
#            </admst:when>
#            <admst:when test="[type='integer']">
#              <admst:text format="0"/>
#            </admst:when>
#            <admst:when test="[type='string']">
#              <admst:text format="&quot;&quot;"/>
#            </admst:when>
#          </admst:choose>
#        </admst:otherwise>
#      </admst:choose>
#      <admst:text format=")"/>
#      <admst:if test="[type='real' and exists(probe) and not($globalCurrentScope='sensitivity') and (insource='yes' or not(nilled(ddxprobe)))]">
#        <admst:text format=",\n"/>
#        <admst:join select="probe" separator=",\n">
#          <admst:text format="d_%(../name)_d%(nature)_%(branch/pnode)_%(branch/nnode)(0.0)"/>
#        </admst:join>
#    </admst:if>
#    </admst:join>
#    <!-- now initialize the LIDs: -->
#    <admst:if test="[exists(node[grounded='no'])]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="node[grounded='no']" separator=",\n    ">
#      <admst:text format="%(xyceNodeLIDVariable(.))(-1)"/>
#    </admst:join>
#    <admst:if test="[exists(@extraUnknowns)]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="@extraUnknowns" separator=",\n    ">
#      <admst:text format="%(xyceBranchLIDVariable(.))(-1)"/>
#    </admst:join>
#    <admst:text format=",\n    "/>
#    <admst:choose>
#      <admst:when test="[count($theModule/node[grounded='no' and location='external']) = 2 ]">
#        <admst:text format="%(xyceLeadBranchLIDVariable(node[2]))(-1)"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:join select="node[grounded='no' and location='external']" separator=",\n    ">
#          <admst:text format="%(xyceLeadBranchLIDVariable(.))(-1)"/>
#        </admst:join>
#      </admst:otherwise>
#    </admst:choose>
#    <!-- now initialize the jacobian pointers: -->
#    <admst:if test="[exists(jacobian)]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="jacobian" separator=",\n    ">
#      <admst:text format="%(xycedFdXPtrName(.))(0)"/>
#    </admst:join>
#    <!-- extra pointers from branch equations -->
#    <admst:for-each select="node/[not(nilled(@branchDeps))]">
#      <admst:text format=",\n    "/>
#      <admst:variable name="theNodeName" select="%(./name)"/>
#      <admst:join select="@branchDeps" separator=",\n    ">
#        <admst:text format="f_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Ptr(0)"/>
#      </admst:join>
#    </admst:for-each>
#    <admst:for-each select="@extraUnknowns">
#      <admst:variable name="thePnodeName" select="%(./pnode/name)"/>
#      <admst:variable name="theNnodeName" select="%(./nnode/name)"/>
#      <admst:if test="[not(nilled(@nodeDeps))]">
#        <admst:text format=",\n    "/>
#      </admst:if>
#      <admst:join select="@nodeDeps" separator=",\n    ">
#        <admst:text format="f_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Ptr(0)"/>
#      </admst:join>
#      <admst:if test="[not(nilled(@branchDeps))]">
#        <admst:text format=",\n    "/>
#      </admst:if>
#      <admst:join select="@branchDeps" separator=",\n    ">
#        <admst:text format="f_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Ptr(0)"/>
#      </admst:join>
#    </admst:for-each>
#    <!-- for the Q jacobian -->
#    <admst:if test="[exists(jacobian)]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="jacobian" separator=",\n    ">
#      <admst:text format="%(xycedQdXPtrName(.))(0)"/>
#    </admst:join>
#    <!-- extra pointers from branch equations -->
#    <admst:for-each select="node/[not(nilled(@branchDeps))]">
#      <admst:text format=",\n    "/>
#      <admst:variable name="theNodeName" select="%(./name)"/>
#      <admst:join select="@branchDeps" separator=",\n    ">
#        <admst:text format="q_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Ptr(0)"/>
#      </admst:join>
#    </admst:for-each>
#    <admst:for-each select="@extraUnknowns">
#      <admst:variable name="thePnodeName" select="%(./pnode/name)"/>
#      <admst:variable name="theNnodeName" select="%(./nnode/name)"/>
#      <admst:if test="[not(nilled(@nodeDeps))]">
#        <admst:text format=",\n    "/>
#      </admst:if>
#      <admst:join select="@nodeDeps" separator=",\n    ">
#        <admst:text format="q_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Ptr(0)"/>
#      </admst:join>
#      <admst:if test="[not(nilled(@branchDeps))]">
#        <admst:text format=",\n    "/>
#      </admst:if>
#      <admst:join select="@branchDeps" separator=",\n    ">
#        <admst:text format="q_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Ptr(0)"/>
#      </admst:join>
#    </admst:for-each>
#    <!-- now initialize the jacobian offsets: -->
#    <admst:if test="[exists(jacobian)]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="jacobian" separator=",\n    ">
#      <admst:text format="%(xyceJacobianOffsetName(.))(-1)"/>
#    </admst:join>
#    <!-- extra pointers from branch equations -->
#    <admst:for-each select="node/[not(nilled(@branchDeps))]">
#      <admst:text format=",\n    "/>
#      <admst:variable name="theNodeName" select="%(./name)"/>
#      <admst:join select="@branchDeps" separator=",\n    ">
#        <admst:text format="A_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Offset(-1)"/>
#      </admst:join>
#    </admst:for-each>
#    <admst:for-each select="@extraUnknowns">
#      <admst:variable name="thePnodeName" select="%(./pnode/name)"/>
#      <admst:variable name="theNnodeName" select="%(./nnode/name)"/>
#      <admst:if test="[not(nilled(@nodeDeps))]">
#        <admst:text format=",\n    "/>
#      </admst:if>
#      <admst:join select="@nodeDeps" separator=",\n    ">
#        <admst:text format="A_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Offset(-1)"/>
#      </admst:join>
#      <admst:if test="[not(nilled(@branchDeps))]">
#        <admst:text format=",\n    "/>
#      </admst:if>
#      <admst:join select="@branchDeps" separator=",\n    ">
#        <admst:text format="A_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Offset(-1)"/>
#      </admst:join>
#    </admst:for-each>
#    <!-- now initialize the store lids -->
#    <admst:if test="[count(@limitedProbes)>0]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="@limitedProbes" separator=",\n    ">
#      <admst:text format="%(xyceLimitedProbeStoreLIDVariable(.))(-1)"/>
#    </admst:join>
#    <admst:if test="[count(variable[output='yes' and input!='yes'])>0]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="variable[output='yes' and input!='yes']" separator=",\n    ">
#      <admst:text format="li_store_%(name)(-1)"/>
#    </admst:join>
#    <admst:if test="[count(node[#collapsible='yes'])>0]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="node[#collapsible='yes']" separator=",\n    ">
#      <admst:text format="collapseNode_%(name)(false)"/>
#    </admst:join>
#    <admst:if test="[count(callfunction[function/name='\$bound_step'])>0]">
#      <admst:text format=",\n  maxTimeStep_(getDeviceOptions().defaultMaxTimeStep)"/>
#    </admst:if>
#    <admst:text format=",\n    admsTemperature(getDeviceOptions().temp.getImmutableValue&lt;double&gt;())\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceModelInitializers
#   Extract all the variables that are either model parameters or
#   model variables (with "global_model" scope) and generate
#   an initializer list for the constructor.
#   Give the module for "select"
#   =================================================================-
#  -->
#  <admst:template match="xyceModelInitializers">
#    <admst:if test="[exists(variable[((parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and input='yes') or (scope='global_model' and input='no')])]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="variable[((parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and input='yes') or (scope='global_model' and input='no')]" separator=",\n    ">
#      <admst:text format="%(name)("/>
#      <admst:choose>
#        <admst:when test="[exists(default) and not exists(#dependent)]">
#          <admst:text format="%(printTerm(default))"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:choose>
#            <admst:when test="[type='real']">
#              <admst:text format="0.0"/>
#            </admst:when>
#            <admst:when test="[type='integer']">
#              <admst:text format="0"/>
#            </admst:when>
#            <admst:when test="[type='string']">
#              <admst:text format="&quot;&quot;"/>
#            </admst:when>
#          </admst:choose>
#        </admst:otherwise>
#      </admst:choose>
#      <admst:text format=")"/>
#    </admst:join>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceInstanceCopyInitializers
#   Extract all the variables that are either instance parameters or
#   instance variables (with "global_instance" scope) and generate
#   an initializer list for the copy constructor.
#   Give the module for "select"
#   =================================================================-
#  -->
#  <admst:template match="xyceInstanceCopyInitializers">
#    <admst:if test="[exists(variable[(parametertype='instance' and input='yes') or (scope='global_instance' and input='no')])]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="variable[(parametertype='instance' and input='yes') or (scope='global_instance' and input='no')]" separator=",\n    ">
#      <admst:text format="%(name)(right.%(name))"/>
#    </admst:join>
#    <!-- now initialize the LIDs: -->
#    <admst:if test="[exists(node[grounded='no'])]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="node[grounded='no']" separator=",\n    ">
#      <admst:text format="%(xyceNodeLIDVariable(.))(right.%(xyceNodeLIDVariable(.)))"/>
#    </admst:join>
#    <!-- now initialize the jacobian offsets: -->
#    <admst:if test="[exists(jacobian)]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="jacobian" separator=",\n    ">
#      <admst:text format="%(xycedFdXPtrName(.))(right.%(xycedFdXPtrName(.)))"/>
#    </admst:join>
#    <!-- extra pointers from branch equations -->
#    <admst:for-each select="node/[not(nilled(@branchDeps))]">
#      <admst:text format=",\n    "/>
#      <admst:variable name="theNodeName" select="%(./name)"/>
#      <admst:join select="@branchDeps" separator=",\n    ">
#        <admst:text format="f_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Ptr(right.f_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Ptr)"/>
#      </admst:join>
#    </admst:for-each>
#    <admst:for-each select="@extraUnknowns">
#      <admst:variable name="thePnodeName" select="%(./pnode/name)"/>
#      <admst:variable name="theNnodeName" select="%(./nnode/name)"/>
#      <admst:if test="[not(nilled(@nodeDeps))]">
#        <admst:text format=",\n    "/>
#      </admst:if>
#      <admst:join select="@nodeDeps" separator=",\n    ">
#        <admst:text format="f_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Ptr(right.f_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Ptr)"/>
#      </admst:join>
#      <admst:if test="[not(nilled(@branchDeps))]">
#        <admst:text format=",\n    "/>
#      </admst:if>
#      <admst:join select="@branchDeps" separator=",\n    ">
#        <admst:text format="f_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Ptr(right.f_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Ptr)"/>
#      </admst:join>
#    </admst:for-each>
#    <!-- same for Q -->
#    <admst:if test="[exists(jacobian)]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="jacobian" separator=",\n    ">
#      <admst:text format="%(xycedQdXPtrName(.))(right.%(xycedQdXPtrName(.)))"/>
#    </admst:join>
#    <!-- extra pointers from branch equations -->
#    <admst:for-each select="node/[not(nilled(@branchDeps))]">
#      <admst:text format=",\n    "/>
#      <admst:variable name="theNodeName" select="%(./name)"/>
#      <admst:join select="@branchDeps" separator=",\n    ">
#        <admst:text format="q_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Ptr(right.q_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Ptr)"/>
#      </admst:join>
#    </admst:for-each>
#    <admst:for-each select="@extraUnknowns">
#      <admst:variable name="thePnodeName" select="%(./pnode/name)"/>
#      <admst:variable name="theNnodeName" select="%(./nnode/name)"/>
#      <admst:if test="[not(nilled(@nodeDeps))]">
#        <admst:text format=",\n    "/>
#      </admst:if>
#      <admst:join select="@nodeDeps" separator=",\n    ">
#        <admst:text format="q_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Ptr(right.q_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Ptr)"/>
#      </admst:join>
#      <admst:if test="[not(nilled(@branchDeps))]">
#        <admst:text format=",\n    "/>
#      </admst:if>
#      <admst:join select="@branchDeps" separator=",\n    ">
#        <admst:text format="q_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Ptr(right.q_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Ptr)"/>
#      </admst:join>
#    </admst:for-each>
#    <admst:text format=",\n    admsTemperature(right.admsTemperature)\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceModelCopyInitializers
#   Extract all the variables that are either model parameters or
#   model variables (with "global_model" scope) and generate
#   an initializer list for the copy constructor.
#   Give the module for "select"
#   =================================================================-
#  -->
#  <admst:template match="xyceModelCopyInitializers">
#    <admst:if test="[exists(variable[((parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and input='yes') or (scope='global_model' and input='no')])]">
#      <admst:text format=",\n    "/>
#    </admst:if>
#    <admst:join select="variable[((parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and input='yes') or (scope='global_model' and input='no')]" separator=",\n    ">
#      <admst:text format="%(name)(right.%(name))"/>
#    </admst:join>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceDeclareModelVariables
#   Extract all the variables that are either model parameters or
#   model variables (with "global_model" scope) and declare them.
#   Give the module for "select"
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareModelVariables">
#    <admst:text format="// Begin verilog Model Variables\n"/>
#    <admst:text format="//   Model Parameters\n"/>
#    <admst:for-each select="variable[(parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and input='yes']">
#      <admst:text format="    "/>
#      <admst:apply-templates select="." match="verilog2CXXtype"/>
#      <admst:text format=" %(name);\n"/>
#    </admst:for-each>
#    <admst:text format="    //  Variables of global_model scope\n"/>
#    <admst:for-each select="variable[scope='global_model' and input='no']">
#      <admst:text format="    "/>
#      <admst:apply-templates select="." match="xyceDeclareVariable"/>
#      <admst:if test="[type='real' and exists(probe)]">
#        <admst:warning format="WARNING!  global model variable %(name) has probe dependence.  That smells like an error.\n"/>
#      </admst:if>
#    </admst:for-each>
#    <admst:text format="    // end verilog model variables====="/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceDeclareNodeLIDVariables
#   Generate a set of declarations for LID variables given module's
#   nodes.
#   Give the module for "select"
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareNodeLIDVariables">
#    <admst:text format="    // Nodal LID Variables\n"/>
#    <admst:for-each select="node[grounded='no']">
#      <admst:text format="    int %(xyceNodeLIDVariable(.));\n"/>
#    </admst:for-each>
#    <admst:text format="    // end Nodal LID Variables\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceDeclareBranchLIDVariables
#   Generate a set of declarations for LID variables given module's
#   branch equations.
#   Give the module for "select"
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareBranchLIDVariables">
#    <admst:text format="    // Branch LID Variables\n"/>
#    <admst:for-each select="@extraUnknowns">
#      <admst:text format="    int %(xyceBranchLIDVariable(.));\n"/>
#    </admst:for-each>
#    <admst:text format="    // end Branch LID Variables\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceDeclareLeadBranchLIDVariables
#   Generate a set of declarations for LID variables given module's
#   branch equations.
#   Give the module for "select"
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareLeadBranchLIDVariables">
#    <admst:text format="    // Lead (branch) LID Variables\n"/>
#
#    <!-- two-terminal devices are special, we only use one of the
#         two possible lead currents, the first one. -->
#    <admst:choose>
#      <admst:when test="[count(node[grounded='no' and location='external']) = 2 ]">
#        <!-- The first node is always GND -->
#        <admst:text format="    int %(xyceLeadBranchLIDVariable(node[2]));\n"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:for-each select="node[grounded='no' and location='external']">
#          <admst:text format="    int %(xyceLeadBranchLIDVariable(.));\n"/>
#        </admst:for-each>
#      </admst:otherwise>
#    </admst:choose>
#    <admst:text format="    // end Lead (branch) LID Variables\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceDeclareJacobianOffsets
#   given a module, declare the batch of Offset variables used when
#   accessing jacobian elements
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareJacobianOffsets">
#    <admst:text format="    // Jacobian  pointers\n"/>
#    <!-- normal jacobian pointers -->
#    <admst:for-each select="jacobian">
#      <admst:text format="    double * %(xycedFdXPtrName(.));\n"/>
#    </admst:for-each>
#    <!-- extra pointers for columns from branch equation dependencies -->
#    <admst:for-each select="node/[not(nilled(@branchDeps))]">
#      <admst:variable name="theNodeName" select="%(./name)"/>
#      <admst:for-each select="@branchDeps">
#        <admst:text format="    double * f_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Ptr;\n"/>
#      </admst:for-each>
#    </admst:for-each>
#    <!-- extra pointers for branch equation rows -->
#    <admst:for-each select="@extraUnknowns">
#      <admst:variable name="thePnodeName" select="%(./pnode/name)"/>
#      <admst:variable name="theNnodeName" select="%(./nnode/name)"/>
#      <admst:for-each select="@nodeDeps">
#        <admst:text format="    double * f_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Ptr;\n"/>
#      </admst:for-each>
#      <admst:for-each select="@branchDeps">
#        <admst:text format="    double * f_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Ptr;\n"/>
#      </admst:for-each>
#    </admst:for-each>
#
#    <!-- now the same thing for Q -->
#    <admst:for-each select="jacobian">
#      <admst:text format="    double * %(xycedQdXPtrName(.));\n"/>
#    </admst:for-each>
#    <admst:for-each select="node/[not(nilled(@branchDeps))]">
#      <admst:variable name="theNodeName" select="%(./name)"/>
#      <admst:for-each select="@branchDeps">
#        <admst:text format="    double * q_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Ptr;\n"/>
#      </admst:for-each>
#    </admst:for-each>
#    <admst:for-each select="@extraUnknowns">
#      <admst:variable name="thePnodeName" select="%(./pnode/name)"/>
#      <admst:variable name="theNnodeName" select="%(./nnode/name)"/>
#        <admst:for-each select="@nodeDeps">
#          <admst:text format="    double * q_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Ptr;\n"/>
#        </admst:for-each>
#        <admst:for-each select="@branchDeps">
#          <admst:text format="    double * q_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Ptr;\n"/>
#        </admst:for-each>
#    </admst:for-each>
#    <admst:text format="    // Jacobian offsets\n"/>
#    <!-- normal jacobian pointers -->
#    <admst:for-each select="jacobian">
#      <admst:text format="    int %(xyceJacobianOffsetName(.));\n"/>
#    </admst:for-each>
#    <!-- extra pointers for columns from branch equation dependencies -->
#    <admst:for-each select="node/[not(nilled(@branchDeps))]">
#      <admst:variable name="theNodeName" select="%(./name)"/>
#      <admst:for-each select="@branchDeps">
#        <admst:text format="    int A_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Offset;\n"/>
#      </admst:for-each>
#    </admst:for-each>
#    <!-- extra pointers for branch equation rows -->
#    <admst:for-each select="@extraUnknowns">
#      <admst:variable name="thePnodeName" select="%(./pnode/name)"/>
#      <admst:variable name="theNnodeName" select="%(./nnode/name)"/>
#      <admst:for-each select="@nodeDeps">
#        <admst:text format="    int A_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Offset;\n"/>
#      </admst:for-each>
#      <admst:for-each select="@branchDeps">
#        <admst:text format="    int A_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Offset;\n"/>
#      </admst:for-each>
#    </admst:for-each>
#
#    <admst:text format="    // end of Jacobian and pointers\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceDeclareFadArrays
#   Given a module, generate declaration of contribution arrays
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareFadArrays">
#    <admst:text format=" // Arrays to hold probes\n"/>
#    <admst:text format=" std::vector &lt; double &gt; probeVars;\n"/>
#    <admst:text format=" std::vector &lt; std::vector &lt; double &gt; &gt; d_probeVars;\n"/>
#    <admst:text format=" // Arrays to hold contributions\n"/>
#    <admst:text format=" // dynamic contributions are differentiated w.r.t time\n"/>
#    <admst:text format=" std::vector &lt; double &gt; staticContributions;\n"/>
#    <admst:text format=" std::vector &lt; std::vector &lt; double &gt; &gt; d_staticContributions;\n"/>
#    <admst:text format=" std::vector &lt; double &gt; dynamicContributions;\n"/>
#    <admst:text format=" std::vector &lt; std::vector &lt; double &gt; &gt; d_dynamicContributions;\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceDeclareLimitingTemporaries
#   Declare the various temporary variables that we need for limiting
#   in updateIntermediateVarsBlock.  Pass in the module.
#   =================================================================-
#  -->
#  <admst:template match="xyceDeclareLimitingTemporaries">
#    <admst:text format=" // temporary variables for limiting\n"/>
#    <admst:for-each select="@limiters">
#      <admst:text format=" double %(printTerm(lhs))_orig,%(printTerm(lhs))_limited,%(printTerm(lhs))_old;\n"/>
#    </admst:for-each>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceNodeLIDVariable
#   Given a node, return its associated LID variable
#   =================================================================-
#  -->
#  <admst:template match="xyceNodeLIDVariable">
#    <admst:text format="li_%(name)"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceBranchLIDVariable
#   Given a branch, return its associated LID variable
#   =================================================================-
#  -->
#  <admst:template match="xyceBranchLIDVariable">
#    <admst:text format="li_BRA_%(pnode)_%(nnode)"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceLeadBranchLIDVariable
#   Given a lead node, return its associated LID variable
#   =================================================================-
#  -->
#  <admst:template match="xyceLeadBranchLIDVariable">
#    <admst:text format="li_branch_i%(name)"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceLimitedProbeStoreLIDVariable
#   Given a probe, return its associated state LID variable for limiting
#   =================================================================-
#  -->
#  <admst:template match="xyceLimitedProbeStoreLIDVariable">
#    <admst:text format="li_store_%(xyceProbeConstantName(.)/[name='probeConstant']/value)"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceNoiseContributionName
#   Given a contribution that has either white or flicker noise
#   (and ONLY one term)
#   construct a name for the noise.
#   This noise name cannot just be the "name" argument of the noise
#   function, because that is not guaranteed unique to the device
#   (fbh has four terms named "thermal", for example)
#
#   We will use "<type>_<posnode>_<negnode>".  If there is a name
#   argument, we'll append "_<namearg" to the name.
#
#
#  -->
#  <admst:template match="xyceNoiseContributionName">
#    <!-- first sanity check.  In this implementation, we ONLY support
#         noise contributions that are simple "I(branch)<+ type_noise()"
#         and cannot work with more complex RHS expressions. -->
#    <admst:assert test="adms[datatypename='contribution']" format="xyceNoiseContribution called on something other than a contribution!\n"/>
#    <admst:assert test="[datatypename='contribution' and (whitenoise='yes' or flickernoise='yes')]" format="xyceNoiseContribution called on contribution %(.), with no noise function!\n"/>
#    <admst:assert test="[rhs/tree/datatypename='function']" format="xyceNoiseContribution called on contribution %(.) whose rhs is not a simple noise function!\n"/>
#    <admst:choose>
#      <admst:when test="[rhs/tree/name='white_noise']">
#        <admst:variable name="theReturnName" select="white"/>
#      </admst:when>
#      <admst:when test="[rhs/tree/name='flicker_noise']">
#        <admst:variable name="theReturnName" select="flicker"/>
#      </admst:when>
#    </admst:choose>
#    <admst:variable name="theReturnName" select="%($theReturnName)_%(lhs/branch/pnode)_%(lhs/branch/nnode)"/>
#    <admst:choose>
#      <admst:when test="[rhs/tree/name='white_noise' and count(rhs/tree/arguments)=2]">
#        <admst:return name="givenName" value="%(rhs/tree/arguments[2])"/>
#      </admst:when>
#      <admst:when test="[rhs/tree/name='flicker_noise' and count(rhs/tree/arguments)=3]">
#        <admst:return name="givenName" value="%(rhs/tree/arguments[3])"/>
#      </admst:when>
#    </admst:choose>
#    <admst:return name="noiseName" value="$theReturnName"/>
#  </admst:template>
#  <!--
#   =================================================================-
#   xyceAnalogFunctionDeclaration
#    Given an analog function, return a declaration for putting in
#    the header file.
#   =================================================================-
#  -->
#  <admst:template match="xyceAnalogFunctionDeclaration">
#    <admst:value-of select="name"/>
#    <admst:variable name="function" select="%s"/>
#    <admst:apply-templates
#       select="."
#       match="verilog2CXXtype"/>
#    <admst:text format=" $function("/>
#    <admst:join
#       select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]"
#       separator=", ">
#      <admst:apply-templates select="." match="verilog2CXXtype"/>
#      <admst:if test="[output='yes']">
#        <admst:text format="&amp; "/>
#      </admst:if>
#      <admst:text format=" %(name)"/>
#    </admst:join>
#    <admst:text format=");\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceAnalogFunctionDefinition
#   Given an analog function, return a non-templated definition of
#   the function (not just a declaration)
#   =================================================================-
#  -->
#  <admst:template match="xyceAnalogFunctionDefinition">
#    <admst:variable name="function" select="%(name)"/>
#    <!-- save the return type -->
#    <admst:variable name="returnType" select="%(type)"/>
#
#
#    <!-- must output variables defined as input, output, or inout, but not
#         the one that has the same name as the function -->
#    <admst:apply-templates
#       select="."
#       match="verilog2CXXtype"/>
#    <admst:text format=" $function("/>
#    <admst:join
#       select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]"
#       separator=", ">
#      <admst:apply-templates select="." match="verilog2CXXtype"/>
#      <!-- only pass by reference if it's an output variable. -->
#      <admst:if test="[output='yes']">
#        <admst:text format="&amp; "/>
#      </admst:if>
#      <admst:text format=" %(name)"/>
#    </admst:join>
#    <admst:text format=")\n"/>
#    <admst:text format="{\n"/>
#
#    <admst:apply-templates select="." match="verilog2CXXtype"/>
#    <admst:text format=" %($function);\n"/>
#
#    <admst:for-each select="variable[input='no' and output='no']">
#      <admst:text format="%(verilog2CXXtype(.)) "/>
#      <admst:text format="%(name);\n"/>
#    </admst:for-each>
#    <admst:apply-templates select="tree" match="%(adms/datatypename)"/>
#    <admst:text format="return(%(name));\n"/>
#    <admst:text format="}\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceCopyModelVars
#     given a module, generate code for assuring that instance vars
#     that override model vars get appropriate defaults
#   =================================================================-
#  -->
#  <admst:template match="xyceCopyModelVars">
#    <admst:for-each select="variable[parametertype='instance' and exists(attribute[name='xyceAlsoModel']) and input='yes']">
#      <admst:text format="   if (!(given(&quot;%(name)&quot;)))\n"/>
#      <admst:text format="   {\n"/>
#      <admst:text format="      %(name) = model_.%(name);\n"/>
#      <admst:text format="   }\n"/>
#    </admst:for-each>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceRegisterJacLIDs
#     given a module, generate code for initializing jacobian LIDs
#   =================================================================-
#  -->
#  <admst:template match="xyceRegisterJacLIDs">
#    <admst:variable name="theModule" select="%(.)"/>
#    <admst:text format="  IntPair jacLoc;\n"/>
#    <admst:for-each select="node[grounded='no']">
#      <admst:variable name="theEquation" select="%(.)"/>
#      <admst:variable name="theEquationNumber" select="%(position(.)-1)"/>
#      <admst:variable name="theEquationName" select="%(name)"/>
#      <admst:variable name="theEquationConstant" select="%(xyceNodeConstantName($theEquation)/[name='nodeConstant']/value)"/>
#      <admst:for-each select="$theModule/jacobian[row/name='$theEquationName']">
#        <admst:if test="[exists(row/#collapsible) and (row/@collapsesTo/name='GND')]">
#          <admst:text format="if (!collapseNode_%(row/name))\n"/>
#          <admst:text format="{\n"/>
#        </admst:if>
#        <admst:if test="[not(column=row) and exists(column/#collapsible) and (column/@collapsesTo/name='GND')]">
#          <admst:text format="if (!collapseNode_%(column/name))\n"/>
#          <admst:text format="{\n"/>
#        </admst:if>
#        <admst:text format="    jacLoc = pairToJacStampMap[IntPair(%(xyceNodeConstantName(row)/[name='nodeConstant']/value),%(xyceNodeConstantName(column)/[name='nodeConstant']/value))];\n"/>
#        <admst:text format="    %(xyceJacobianOffsetName(.)) = jacLIDVec[jacLoc.first][jacLoc.second];\n"/>
#        <admst:if test="[exists(row/#collapsible) and (row/@collapsesTo/name='GND')]">
#          <admst:text format="}\n"/>
#        </admst:if>
#        <admst:if test="[not(column=row) and exists(column/#collapsible) and (column/@collapsesTo/name='GND')]">
#          <admst:text format="}\n"/>
#        </admst:if>
#      </admst:for-each>
#
#      <!-- set up pointers for extra columns due to branches-->
#      <admst:variable name="theNodeName" select="%(./name)"/>
#      <admst:variable name="theNode" select="%(.)"/>
#      <admst:for-each select="@branchDeps">
#        <admst:if test="[exists($theNode/#collapsible) and ($theNode/@collapsesTo/name='GND')]">
#          <admst:text format="if (!collapseNode_%($theNodeName))\n"/>
#          <admst:text format="{\n"/>
#        </admst:if>
#        <admst:text format="    jacLoc=pairToJacStampMap[IntPair(%(xyceNodeConstantName($theNode)/[name='nodeConstant']/value),%(xyceBranchConstantName(.)/[name='branchConstant']/value))];\n"/>
#        <admst:text format="    A_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Offset = jacLIDVec[jacLoc.first][jacLoc.second];\n"/>
#        <admst:if test="[exists($theNode/#collapsible) and ($theNode/@collapsesTo/name='GND')]">
#          <admst:text format="}\n"/>
#        </admst:if>
#      </admst:for-each>
#
#    </admst:for-each>
#
#    <!-- Now we need to generate the pointers for the extra rows for branch
#         equations -->
#    <admst:for-each select="@extraUnknowns">
#      <admst:variable name="thePnodeName" select="%(./pnode/name)"/>
#      <admst:variable name="theNnodeName" select="%(./nnode/name)"/>
#      <admst:variable name="theBranch" select="%(.)"/>
#      <admst:for-each select="@nodeDeps">
#        <admst:if test="[exists(#collapsible) and (@collapsesTo/name='GND')]">
#          <admst:text format="if (!collapseNode_%(name))\n"/>
#          <admst:text format="{\n"/>
#        </admst:if>
#        <admst:text format="    jacLoc = pairToJacStampMap[IntPair(%(xyceBranchConstantName($theBranch)/[name='branchConstant']/value),%(xyceNodeConstantName(.)/[name='nodeConstant']/value))];\n"/>
#        <admst:text format="    A_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Offset = jacLIDVec[jacLoc.first][jacLoc.second];\n"/>
#        <admst:if test="[exists(#collapsible) and (@collapsesTo/name='GND')]">
#          <admst:text format="}\n"/>
#        </admst:if>
#
#      </admst:for-each>
#      <admst:for-each select="@branchDeps">
#        <admst:text format="    jacLoc = pairToJacStampMap[IntPair(%(xyceBranchConstantName($theBranch)/[name='branchConstant']/value),%(xyceBranchConstantName(.)/[name='branchConstant']/value))];\n"/>
#        <admst:text format="    A_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Offset=jacLIDVec[jacLoc.first][jacLoc.second];\n"/>
#      </admst:for-each>
#    </admst:for-each>
#  </admst:template>
#
#
#  <!--
#   =================================================================-
#   xyceSetupPointers
#     given a module, generate code for initializing jacobian LIDs
#   =================================================================-
#  -->
#  <admst:template match="xyceSetupPointers">
#    <admst:variable name="theModule" select="%(.)"/>
#    <admst:for-each select="node[grounded='no']">
#      <admst:variable name="theEquation" select="%(.)"/>
#      <admst:variable name="theEquationNumber" select="%(position(.)-1)"/>
#      <admst:variable name="theEquationName" select="%(name)"/>
#      <admst:variable name="theEquationConstant" select="%(xyceNodeConstantName($theEquation)/[name='nodeConstant']/value)"/>
#      <admst:for-each select="$theModule/jacobian[row/name='$theEquationName']">
#        <admst:if test="[exists(row/#collapsible) and (row/@collapsesTo/name='GND')]">
#          <admst:text format="if (!collapseNode_%(row/name))\n"/>
#          <admst:text format="{\n"/>
#        </admst:if>
#        <admst:if test="[not(column=row) and exists(column/#collapsible) and (column/@collapsesTo/name='GND')]">
#          <admst:text format="if (!collapseNode_%(column/name))\n"/>
#          <admst:text format="{\n"/>
#        </admst:if>
#        <admst:text format="    %(xycedFdXPtrName(.)) = &amp;(dFdx[%(xyceNodeLIDVariable(row))][%(xyceJacobianOffsetName(.))]);\n"/>
#        <admst:text format="    %(xycedQdXPtrName(.)) = &amp;(dQdx[%(xyceNodeLIDVariable(row))][%(xyceJacobianOffsetName(.))]);\n"/>
#        <admst:if test="[exists(row/#collapsible) and (row/@collapsesTo/name='GND')]">
#          <admst:text format="}\n"/>
#        </admst:if>
#        <admst:if test="[not(column=row) and exists(column/#collapsible) and (column/@collapsesTo/name='GND')]">
#          <admst:text format="}\n"/>
#        </admst:if>
#      </admst:for-each>
#
#      <!-- set up pointers for extra columns due to branches-->
#      <admst:variable name="theNodeName" select="%(./name)"/>
#      <admst:variable name="theNode" select="%(.)"/>
#      <admst:for-each select="@branchDeps">
#        <admst:if test="[exists($theNode/#collapsible) and ($theNode/@collapsesTo/name='GND')]">
#          <admst:text format="if (!collapseNode_%($theNodeName))\n"/>
#          <admst:text format="{\n"/>
#        </admst:if>
#        <admst:text format="    f_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Ptr = &amp;(dFdx[%(xyceNodeLIDVariable($theEquation))][A_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Offset]);\n"/>
#        <admst:text format="    q_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Ptr = &amp;(dQdx[%(xyceNodeLIDVariable($theEquation))][A_%($theNodeName)_Equ_BRA_%(pnode)_%(nnode)_Var_Offset]);\n"/>
#        <admst:if test="[exists($theNode/#collapsible) and ($theNode/@collapsesTo/name='GND')]">
#          <admst:text format="}\n"/>
#        </admst:if>
#      </admst:for-each>
#
#    </admst:for-each>
#
#    <!-- Now we need to generate the pointers for the extra rows for branch
#         equations -->
#    <admst:for-each select="@extraUnknowns">
#      <admst:variable name="thePnodeName" select="%(./pnode/name)"/>
#      <admst:variable name="theNnodeName" select="%(./nnode/name)"/>
#      <admst:variable name="theBranch" select="%(.)"/>
#      <admst:for-each select="@nodeDeps">
#        <admst:if test="[exists(#collapsible) and (@collapsesTo/name='GND')]">
#          <admst:text format="if (!collapseNode_%(name))\n"/>
#          <admst:text format="{\n"/>
#        </admst:if>
#        <admst:text format="    f_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Ptr = &amp;(dFdx[%(xyceBranchLIDVariable($theBranch))][A_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Offset]);\n"/>
#        <admst:text format="    q_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Ptr =  &amp;(dQdx[%(xyceBranchLIDVariable($theBranch))][A_BRA_%($thePnodeName)_%($theNnodeName)_Equ_%(name)_Node_Offset]);\n"/>
#        <admst:if test="[exists(#collapsible) and (@collapsesTo/name='GND')]">
#          <admst:text format="}\n"/>
#        </admst:if>
#
#      </admst:for-each>
#      <admst:for-each select="@branchDeps">
#        <admst:text format="    f_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Ptr=&amp;(dFdx[%(xyceBranchLIDVariable($theBranch))][A_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Offset]);\n"/>
#        <admst:text format="    q_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Ptr=&amp;(dQdx[%(xyceBranchLIDVariable($theBranch))][A_BRA_%($thePnodeName)_%($theNnodeName)_Equ_BRA_%(pnode/name)_%(nnode/name)_Var_Offset]);\n"/>
#      </admst:for-each>
#    </admst:for-each>
#
#  </admst:template>
#
#
#  <!--
#   =================================================================-
#   xyceGenerateJacStamp
#     given a module, generate code for initializing  jacobian stamp
#   =================================================================-
#  -->
#  <admst:template match="xyceGenerateJacStamp">
#    <admst:variable name="theModule" select="%(.)"/>
#    <admst:text format="    jacStamp.resize(%(count(node[grounded='no'])));\n"/>
#    <admst:for-each select="node[grounded='no']">
#      <admst:variable name="theEquation" select="%(.)"/>
#      <admst:variable name="theEquationName" select="%(name)"/>
#      <admst:variable name="theEquationConstant" select="%(xyceNodeConstantName($theEquation)/[name='nodeConstant']/value)"/>
#      <admst:text format="    jacStamp[$theEquationConstant].resize(%(count($theModule/jacobian[row/name='$theEquationName'])+count(@branchDeps)));\n"/>
#      <admst:for-each select="$theModule/jacobian[row/name='$theEquationName']">
#        <admst:text format="    jacStamp[$theEquationConstant][%(position(.)-1)] = %(xyceNodeConstantName(column)/[name='nodeConstant']/value);\n"/>
#      </admst:for-each>
#      <admst:if test="[not(nilled(@branchDeps))]">
#        <admst:text format="    // Extra columns for dependence on branches\n"/>
#        <admst:text format="    {\n      int tempOffset=0;\n"/>
#        <admst:for-each select="@branchDeps">
#        <admst:text format="    jacStamp[$theEquationConstant][%(count($theModule/jacobian[row/name='$theEquationName']))+(tempOffset++)] = %(xyceBranchConstantName(.)/[name='branchConstant']/value);\n"/>
#        </admst:for-each>
#        <admst:text format="    }\n\n"/>
#      </admst:if>
#
#    </admst:for-each>
#    <admst:apply-templates select="." match="xyceAugmentJacStamp"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceGenerateJacStamp2
#     given a module, generate code for initializing  jacobian stamp
#   =================================================================-
#  -->
#  <admst:template match="xyceGenerateJacStamp2">
#    <admst:variable name="theModule" select="%(.)"/>
#    <admst:text format="PairVector jacobianElements;\n"/>
#    <admst:for-each select="node[grounded='no']">
#      <admst:variable name="theEquation" select="%(.)"/>
#      <admst:variable name="theEquationName" select="%(name)"/>
#      <admst:variable name="theEquationConstant" select="%(xyceNodeConstantName($theEquation)/[name='nodeConstant']/value)"/>
#      <admst:for-each select="$theModule/jacobian[row/name='$theEquationName']">
#        <admst:text format="    jacobianElements.push_back(IntPair($theEquationConstant,%(xyceNodeConstantName(column)/[name='nodeConstant']/value)));\n"/>
#      </admst:for-each>
#      <admst:if test="[not(nilled(@branchDeps))]">
#        <admst:text format="    // Extra columns for dependence on branches\n"/>
#        <admst:for-each select="@branchDeps">
#        <admst:text format="    jacobianElements.push_back(IntPair($theEquationConstant,%(xyceBranchConstantName(.)/[name='branchConstant']/value)));\n"/>
#        </admst:for-each>
#      </admst:if>
#
#    </admst:for-each>
#
#    <admst:if test="[not(nilled(@extraUnknowns))]">
#      <admst:text format="    // Jacobian rows for branch equations\n"/>
#    </admst:if>
#    <admst:for-each select="@extraUnknowns">
#      <admst:variable name="theRow" select="%(xyceBranchConstantName(.)/[name='branchConstant']/value)"/>
#      <admst:variable name="theBranchName" select="%(.)"/>
#      <admst:for-each select="@nodeDeps">
#        <admst:text format="jacobianElements.push_back(IntPair($theRow,%(xyceNodeConstantName(.)/[name='nodeConstant']/value)));   // Branch eqn %($theBranchName) - node %(./name)\n"/>
#      </admst:for-each>
#      <admst:for-each select="@branchDeps">
#        <admst:text format="jacobianElements.push_back(IntPair($theRow,%(xyceBranchConstantName(.)/[name='branchConstant']/value))); // Branch eqn %($theBranchName) - branch var %(.)\n"/>
#      </admst:for-each>
#    </admst:for-each>
#
#  </admst:template>
#
#
#  <!--
#   =================================================================-
#   xyceAugmentJacStamp
#     given a module, generate code for adding branch equations/variables
#     to an existing  jacobian stamp
#   =================================================================-
#  -->
#  <admst:template match="xyceAugmentJacStamp">
#
#<!--
#    <admst:for-each select="@extraJac1">
#      <admst:variable name="theRow" select="%(xyceNodeConstantName(.)/[name='nodeConstant']/value)"/>
#      <admst:variable name="theRowName" select="%(name)"/>
#      //Augment jacobian row for %($theRowName)
#    {
#      int rowsize;
#      int tempColOffset=0;
#      rowsize=jacStamp[%($theRow)].size();
#      jacStamp[%($theRow)].resize(rowsize+%(count(@branchDeps)));
#      <admst:for-each select="@branchDeps">
#      jacStamp[%($theRow)][rowsize+(tempColOffset++)] = %(xyceBranchConstantName(.)/[name='branchConstant']/value); // eqn %($theRowName) - branch var %(.)
#      </admst:for-each>
#    }
#    </admst:for-each>
#-->
#    <admst:if test="[not(nilled(@extraUnknowns))]">
#      <admst:text format="    // Jacobian rows for branch equations\n"/>
#    </admst:if>
#    <admst:for-each select="@extraUnknowns">
#    {
#      int jacsize=jacStamp.size();
#      jacStamp.resize(jacsize+1);
#      <admst:variable name="theRow" select="%(xyceBranchConstantName(.)/[name='branchConstant']/value)"/>
#      <admst:variable name="theBranchName" select="%(.)"/>
#      jacStamp[$theRow].resize(%(count(@nodeDeps)+count(@branchDeps)));
#      int tempCol = 0;
#      <admst:for-each select="@nodeDeps">
#      jacStamp[$theRow][tempCol++] = %(xyceNodeConstantName(.)/[name='nodeConstant']/value);   // Branch eqn %($theBranchName) - node %(./name)
#      </admst:for-each>
#      <admst:for-each select="@branchDeps">
#      jacStamp[$theRow][tempCol++] = %(xyceBranchConstantName(.)/[name='branchConstant']/value); // Branch eqn %($theBranchName) - branch var %(.)
#      </admst:for-each>
#    }
#    </admst:for-each>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   xyceLabelNoiseContributions
#   Add a "#noiseContIndex" variable to each contribution that has
#   noise.  This will be used later to index into a vector of
#   contributions.
#   The thing passed in should be a module.
#   =================================================================-
#  -->
#  <admst:template match="xyceLabelNoiseContributions">
#    <admst:for-each select="contribution[whitenoise='yes' or flickernoise='yes']">
#      <admst:value-to select="#noiseContIndex" value="%(position(.)-1)"/>
#    </admst:for-each>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   collectBranchDepends
#   Given a branch (which is assumed to have an associated
#   branch variable due to use of flow probes and/or potential sources),
#   count up how many jacobian columns should be allocated for the
#   associated branch equation.  When returns, /module/@countNodes
#   will list all the nodes this branch equation depends on (through
#   potential probes) and /module/@countBranches will list the branch
#   flows it depends on (through flow probes).
#   =================================================================-
#   -->
#  <admst:template match="collectBranchDepends">
#    <admst:variable name="thePnode" select="%(pnode)"/>
#    <admst:variable name="theNnode" select="%(nnode)"/>
#    <admst:reset select="/module/@countNodes"/>
#    <admst:reset select="/module/@countBranches"/>
#    <admst:for-each select="/module/contribution[lhs/branch/pnode=$thePnode and lhs/branch/nnode=$theNnode]">
#      <admst:for-each select="rhs/probe">
#        <admst:choose>
#          <!-- potential probes on the RHS add nodal dependencies to
#               the branch equation-->
#          <admst:when test="[nature=discipline/potential]">
#            <admst:push into="/module/@countNodes" select="branch/pnode" onduplicate="ignore"/>
#            <admst:if test="[branch/nnode/grounded='no']">
#              <admst:push into="/module/@countNodes" select="branch/nnode" onduplicate="ignore"/>
#            </admst:if>
#          </admst:when>
#          <!-- flow probes on the RHS add branch dependencies to the
#               branch equation -->
#          <admst:otherwise>
#            <admst:push into="/module/@countBranches" select="branch" onduplicate="ignore"/>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:for-each>
#      <!-- Finally, if this is a potential source, the branch equation
#           also depends on the nodes of the lhs.  If it's a flow source,
#           the branch equation depends on the flow variable.
#      -->
#      <admst:choose>
#        <admst:when test="[lhs/nature=lhs/discipline/potential]">
#          <admst:push into="/module/@countNodes" select="lhs/branch/pnode" onduplicate="ignore"/>
#          <admst:if test="[lhs/branch/nnode/grounded='no']">
#            <admst:push into="/module/@countNodes" select="lhs/branch/nnode" onduplicate="ignore"/>
#            </admst:if>
#        </admst:when>
#        <admst:otherwise>
#          <admst:push into="/module/@countBranches" select="lhs/branch" onduplicate="ignore"/>
#        </admst:otherwise>
#      </admst:choose>
#
#    </admst:for-each>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   =================================================================-
#   Basic templates for processing verilog
#
#   =================================================================-
#   =================================================================-
#
#   =================================================================-
#   collectAssignedVariables
#   Given a node of the ADMS data tree, determine all variables that
#   appear on the left-hand side of assignments in that node and all
#   of its children.  This is done recursively.
#
#   The list of all those variables is deposited in the @assignedVars
#   array of the *PARENT* of the node passed in.  This is fishy, and
#   I wish I could figure out a way to do it without pushing the data
#   up above the node we start with.
#
#   Since we push data upward, it's probably best not to call this on
#   the top level "analog/code" node of the tree, but rather loop over
#   all of that node's children instead if one needs to process it.
#   =================================================================-
#  -->
#<admst:template match="collectAssignedVariables">
#  <admst:choose>
#    <!-- ASSIGNMENT -->
#    <admst:when test="adms[datatypename='assignment']">
#      <admst:push into="../@assignedVars" select="lhs" onduplicate="ignore"/>
#
#      <!-- now try to collect "assignments" that are just output vars
#           of analog function calls -->
#      <admst:value-of select=".."/>
#      <admst:variable name="theGlobalAssignedVarsTarget" select="%p"/>
#      <admst:apply-templates select="rhs" match="collectAssignedVariables"/>
#      <admst:variable name="theGlobalAssignedVarsTarget"/>
#
#    </admst:when>
#    <!-- BLOCK -->
#    <admst:when test="adms[datatypename='block']">
#      <!-- recurse -->
#      <admst:for-each select="item">
#        <admst:apply-templates select="." match="collectAssignedVariables"/>
#      </admst:for-each>
#      <!-- the result should be that our current node, which is a block,
#           has received all the variables of all its children listed in
#           @assignedVars -->
#    </admst:when>
#    <!-- CONDITIONAL -->
#    <admst:when test="adms[datatypename='conditional']">
#      <admst:apply-templates select="then" match="collectAssignedVariables"/>
#      <admst:apply-templates select="else" match="collectAssignedVariables"/>
#    </admst:when>
#    <!-- WHILELOOP -->
#    <admst:when test="adms[datatypename='whileloop']">
#      <admst:apply-templates select="whileblock" match="collectAssignedVariables"/>
#    </admst:when>
#    <!-- FORLOOP -->
#    <admst:when test="adms[datatypename='forloop']">
#      <admst:apply-templates select="initial" match="collectAssignedVariables"/>
#      <admst:apply-templates select="forblock" match="collectAssignedVariables"/>
#      <admst:apply-templates select="update" match="collectAssignedVariables"/>
#    </admst:when>
#    <!-- CASE -->
#    <admst:when test="adms[datatypename='case']">
#      <admst:apply-templates select="caseitem" match="collectAssignedVariables"/>
#    </admst:when>
#    <!-- caseitem -->
#    <admst:when test="adms[datatypename='caseitem']">
#      <admst:apply-templates select="code" match="collectAssignedVariables"/>
#    </admst:when>
#    <!-- CODE -->
#    <admst:when test="adms[datatypename='code']">
#      <admst:apply-templates select="item" match="collectAssignedVariables">
#      </admst:apply-templates>
#    </admst:when>
#    <!-- none of the following types can do assignment -->
#    <admst:when test="adms[datatypename='contribution']"/>
#    <admst:when test="adms[datatypename='callfunction']"/>
#    <admst:when test="adms[datatypename='nilled']"/>
#    <admst:when test="adms[datatypename='blockvariable']"/>
#
#    <!-- All of these things can happen only if we are being called on the
#         RHS of an assignment, and we're probing only for analog function
#         calls that have output vars (and therefore "assign" to those vars)
#    -->
#    <admst:when test="adms[datatypename='expression']">
#      <admst:apply-templates select="tree" match="collectAssignedVariables"/>
#    </admst:when>
#    <admst:when test="adms[datatypename='expression']">
#      <admst:apply-templates select="tree" match="collectAssignedVariables"/>
#    </admst:when>
#    <admst:when test="adms[datatypename='mapply_unary']">
#      <admst:apply-templates select="arg1" match="collectAssignedVariables"/>
#    </admst:when>
#    <admst:when test="adms[datatypename='mapply_binary']">
#      <admst:apply-templates select="arg1|arg2" match="collectAssignedVariables"/>
#    </admst:when>
#    <admst:when test="adms[datatypename='mapply_ternary']">
#      <admst:apply-templates select="arg1|arg2|arg3" match="collectAssignedVariables"/>
#    </admst:when>
#
#    <!-- Now, the real place where new assigned vars might exist -->
#    <admst:when test="adms[datatypename='function']">
#      <admst:apply-templates select="arguments" match="collectAssignedVariables"/>
#      <!-- Now, if we're an analog function, do some real work on the
#           output variables, if there are any -->
#      <admst:if test="[definition/datatypename='analogfunction']">
#        <admst:variable name="theFunction" select="%(.)"/>
#        <admst:for-each select="definition/variable">
#          <admst:if test="[(output='yes') and (name!=$theFunction/name)]">
#            <admst:variable name="thePosition" select="%(position(.)-1)"/>
#            <!-- <admst:message format="Found an output var %($theFunction/arguments[position(.)=$thePosition]/name) to mark as assigned\n"/> -->
#            <admst:push into="$theGlobalAssignedVarsTarget/@assignedVars" select="$theFunction/arguments[position(.)=$thePosition]" onduplicate="ignore"/>
#          </admst:if>
#        </admst:for-each>
#      </admst:if>
#    </admst:when>
#
#    <!-- these do nothing -->
#    <admst:when test="adms[datatypename='variable' or datatypename='number' or datatypename='string' or datatypename='probe']"/>
#
#    <admst:otherwise>
#      <admst:fatal format="'datatypename=%(adms/datatypename)':collectAssignedVariables cannot process this type, should not be reached.\n"/>
#    </admst:otherwise>
#  </admst:choose>
#  <!-- At this point, we have processed our own and our children's variables,
#       and our @assignedVars array contains all the variables we or our
#       children have assigned into.  Pass this information up to our parent
#       if we haven't already done it (because we're an assignment). -->
#  <admst:if test="adms[datatypename!='assignment']">
#    <admst:variable name="parent" select="%(..)"/>
#    <admst:variable name="this" select="%(.)"/>
#    <admst:for-each select="@assignedVars">
#      <!-- <admst:message format="Got something other than assignment (%($this/datatypename)), pushing %(.) into parent which is of type %($parent/datatypename)\n"/> -->
#      <admst:variable name="thisName" value="%(name)"/>
#      <!-- not enough to push with 'onduplicate="ignore"' because the actual
#           variable node has more info than just the name, and different
#           instances aren't actually duplicates just because the name is the
#           same. This would result in multiple declarations if we're not
#           careful. -->
#      <!-- <admst:message format="Want to push variable %(.) into parent.  This variable is defined in environment of type %(block/adms/datatypename) and scope is %(scope).\n"/> -->
#      <admst:variable name="pushUp" string="yes"/>
#      <admst:if test="[$this/adms/datatypename='block' and block=$this]">
#        <!-- <admst:message format="I think this should be local and we shouldn't push up\n"/> -->
#        <admst:variable name="pushUp" string="no"/>
#      </admst:if>
#      <admst:if test="[$pushUp = 'yes']">
#          <admst:push into="$parent/@assignedVars" select="." onduplicate="ignore"/>
#      </admst:if>
#    </admst:for-each>
#  </admst:if>
#</admst:template>
#
#<!--
# =================================================================-
# collectInterdependentParams
# Given a module, run through all the parameter variables it has and
# mark as "#dependent='yes'" any that have default values that depend
# on other variables in any way.
#
# These variables cannot have their defaults determined by their addPar
# calls, and must have their defaults set (if not given in the netlist)
# at constructor time instead.
#
# This template is intended to be called early in processing, like
# collectLimters and collectCollapsibles
# =================================================================-
# -->
# <admst:template match="collectInterdependentParams">
#   <admst:for-each select="variable[(parametertype='instance' or parametertype='model') and input='yes' and exists(default)]">
#     <admst:apply-templates select="default" match="recursiveDetectVariableDependence">
#       <admst:if test="[returned('isDependent')/value = 'yes']">
#         <admst:value-to select="../#dependent" string="yes"/>
#       </admst:if>
#     </admst:apply-templates>
#   </admst:for-each>
# </admst:template>
#
#<!--
# =================================================================-
# collectParamDependence
# Given a variable, run through everything it depends on, and check
# if it depends on any parameters
#
#This is necessary because ADMS only stores parameter dependence
#that is explicit.   Parameter dependence that is inherited from
#other variables does not get propagated into a variable's
#"variarable" structure
# =================================================================-
# -->
# <admst:template match="collectParamDependence">
#   <admst:variable name="isDependent" value="no"/>
#   <admst:apply-templates select="." match="recursiveDetectParameterDependence">
#     <admst:if test="[returned('isDependent')/value = 'yes']">
#       <admst:value-to select="#Pdependent" string="yes"/>
#     </admst:if>
#   </admst:apply-templates>
# </admst:template>
#
#<!--
# =================================================================-
# recursiveDetectVariableDependence
# Given a node, try to determine if the expression it represents has
# dependence on any variables
# =================================================================-
# -->
# <admst:template match="recursiveDetectVariableDependence">
# <admst:choose>
#   <admst:when test="[datatypename='number']">
#     <admst:return name="isDependent" value="no"/>
#   </admst:when>
#   <admst:when test="[datatypename='variable']">
#     <admst:return name="isDependent" value="yes"/>
#   </admst:when>
#   <admst:when test="[datatypename='expression']">
#     <admst:apply-templates select="tree" match="recursiveDetectVariableDependence">
#       <admst:return name="isDependent" value="%(returned('isDependent')/value)"/>
#     </admst:apply-templates>
#   </admst:when>
#   <admst:when test="[datatypename='mapply_unary']">
#     <admst:apply-templates select="arg1" match="recursiveDetectVariableDependence">
#       <admst:return name="isDependent" value="%(returned('isDependent')/value)"/>
#     </admst:apply-templates>
#   </admst:when>
#   <admst:when test="[datatypename='mapply_binary']">
#     <admst:apply-templates select="arg1" match="recursiveDetectVariableDependence">
#       <admst:variable name="isDependent1" value="%(returned('isDependent')/value)"/>
#     </admst:apply-templates>
#     <admst:apply-templates select="arg2" match="recursiveDetectVariableDependence">
#       <admst:variable name="isDependent2" value="%(returned('isDependent')/value)"/>
#     </admst:apply-templates>
#     <admst:choose>
#       <admst:when test="[$isDependent1='yes' or $isDependent2='yes']">
#         <admst:return name="isDependent" value="yes"/>
#       </admst:when>
#       <admst:otherwise>
#         <admst:return name="isDependent" value="no"/>
#       </admst:otherwise>
#     </admst:choose>
#   </admst:when>
#   <admst:when test="[datatypename='mapply_ternary']">
#     <admst:apply-templates select="arg1" match="recursiveDetectVariableDependence">
#       <admst:variable name="isDependent1" value="%(returned('isDependent')/value)"/>
#     </admst:apply-templates>
#     <admst:apply-templates select="arg2" match="recursiveDetectVariableDependence">
#       <admst:variable name="isDependent2" value="%(returned('isDependent')/value)"/>
#     </admst:apply-templates>
#     <admst:apply-templates select="arg3" match="recursiveDetectVariableDependence">
#       <admst:variable name="isDependent3" value="%(returned('isDependent')/value)"/>
#     </admst:apply-templates>
#     <admst:choose>
#       <admst:when test="[$isDependent1='yes' or $isDependent2='yes' or $isDependent3='yes']">
#         <admst:return name="isDependent" value="yes"/>
#       </admst:when>
#       <admst:otherwise>
#         <admst:return name="isDependent" value="no"/>
#       </admst:otherwise>
#     </admst:choose>
#   </admst:when>
#   <admst:when test="[datatypename='function']">
#     <admst:choose>
#       <admst:when test="[name='\$simparam']">
#         <admst:return name="isDependent" value="yes"/>
#       </admst:when>
#       <admst:otherwise>
#         <admst:variable name="isFuncDependent" value="no"/>
#         <admst:apply-templates select="arguments" match="recursiveDetectVariableDependence">
#           <admst:if test="[returned('isDependent')/value = 'yes']">
#             <admst:variable name="isFuncDependent" value="yes"/>
#           </admst:if>
#         </admst:apply-templates>
#         <admst:choose>
#           <admst:when test="[$isFuncDependent='yes']">
#             <admst:return name="isDependent" value="yes"/>
#           </admst:when>
#           <admst:otherwise>
#             <admst:return name="isDependent" value="no"/>
#           </admst:otherwise>
#         </admst:choose>
#       </admst:otherwise>
#     </admst:choose>
#   </admst:when>
#   <admst:otherwise>
#     <admst:return name="isDependent" value="no"/>
#   </admst:otherwise>
# </admst:choose>
# </admst:template>
#
#<!--
# =================================================================-
# recursiveDetectParameterDependence
# Given any node, try to determine if the expression it represents has
# dependence on any parameters
# =================================================================-
# -->
#<admst:template match="recursiveDetectParameterDependence">
#  <admst:variable name="isDependent" value="no"/>
#  <admst:choose>
#    <!-- if we've already been through this and already flagged as pdep, don't do again -->
#    <admst:when test="[exists(#Pdependent)]">
#      <admst:variable name="isDependent" value="yes"/>
#    </admst:when>
#    <admst:when test="[datatypename='number']">
#      <!-- no changie da value.  -->
#    </admst:when>
#    <admst:when test="[datatypename='string']">
#      <!-- no changie da value.  -->
#    </admst:when>
#    <admst:when test="[(datatypename='variable' or datatypename='variableprototype') and type='real']">
#      <admst:choose>
#        <!-- This variable is a real parameter or explicitly depends on one or more real parameters -->
#        <admst:when test="[exists(#Pdependent)]">
#          <admst:variable name="isDependent" value="yes"/>
#        </admst:when>
#        <admst:when test="[input='yes' or exists(variable[input='yes'])]">
#          <admst:variable name="isDependent" value="yes"/>
#          <admst:value-to select="#Pdependent" value="yes"/>
#        </admst:when>
#        <!-- This variable does not explicitly depend on one or more parameters,
#             but does depend on one or more non-parameter variables-->
#        <admst:when test="[count(variable) > 0]">
#          <admst:for-each select="variable">
#            <admst:if test="[not (name=../name or (exists(#DONOTLOOP) and #DONOTLOOP='yes'))]">
#              <!-- temporarily mark this variable as in process-->
#              <admst:value-to select="#DONOTLOOP" value="yes"/>
#              <admst:apply-templates select="." match="recursiveDetectParameterDependence">
#                <admst:variable name="isDependent1" value="%(returned('isDependent')/value)"/>
#                <admst:if test="[$isDependent1='yes']">
#                  <admst:variable name="isDependent" value="yes"/>
#                  <admst:value-to select="#Pdependent" value="yes"/>
#                </admst:if>
#              </admst:apply-templates>
#              <!--clear the donotloop flag, seems to be no way to delete
#                  a croixvar-->
#              <admst:value-to select="#DONOTLOOP" value="no"/>
#            </admst:if>
#          </admst:for-each>
#        </admst:when>
#        <!-- This variable does not explicitly depend on one or more parameters,
#             and does not depend other non-parameter variables-->
#        <admst:otherwise>
#          <!-- <admst:message format="recursiveDetectParameterDependence %(name) is independent of variables altogether\n"/>-->
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:when test="[datatypename='expression']">
#      <admst:apply-templates select="tree" match="recursiveDetectParameterDependence">
#        <admst:variable name="isDependent1" value="%(returned('isDependent')/value)"/>
#        <admst:if test="[$isDependent1='yes']">
#          <admst:variable name="isDependent" value="yes"/>
#        </admst:if>
#      </admst:apply-templates>
#    </admst:when>
#    <admst:when test="[datatypename='mapply_unary']">
#      <admst:apply-templates select="arg1" match="recursiveDetectParameterDependence">
#        <admst:variable name="isDependent1" value="%(returned('isDependent')/value)"/>
#        <admst:if test="[$isDependent1='yes']">
#          <admst:variable name="isDependent" value="yes"/>
#        </admst:if>
#      </admst:apply-templates>
#    </admst:when>
#    <admst:when test="[datatypename='mapply_binary']">
#      <admst:apply-templates select="arg1" match="recursiveDetectParameterDependence">
#        <admst:variable name="isDependent1" value="%(returned('isDependent')/value)"/>
#      </admst:apply-templates>
#      <admst:apply-templates select="arg2" match="recursiveDetectParameterDependence">
#        <admst:variable name="isDependent2" value="%(returned('isDependent')/value)"/>
#      </admst:apply-templates>
#      <admst:choose>
#        <admst:when test="[$isDependent1='yes' or $isDependent2='yes']">
#          <admst:variable name="isDependent" value="yes"/>
#        </admst:when>
#        <admst:otherwise>
#          <!-- no changie da value -->
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:when test="[datatypename='mapply_ternary']">
#      <admst:apply-templates select="arg1" match="recursiveDetectParameterDependence">
#        <admst:variable name="isDependent1" value="%(returned('isDependent')/value)"/>
#      </admst:apply-templates>
#      <admst:apply-templates select="arg2" match="recursiveDetectParameterDependence">
#        <admst:variable name="isDependent2" value="%(returned('isDependent')/value)"/>
#      </admst:apply-templates>
#      <admst:apply-templates select="arg3" match="recursiveDetectParameterDependence">
#        <admst:variable name="isDependent3" value="%(returned('isDependent')/value)"/>
#      </admst:apply-templates>
#      <admst:choose>
#        <admst:when test="[$isDependent1='yes' or $isDependent2='yes' or $isDependent3='yes']">
#          <admst:variable name="isDependent" value="yes"/>
#        </admst:when>
#        <admst:otherwise>
#          <!-- just leave isDependent where it is -->
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:when test="[datatypename='function']">
#      <admst:choose>
#        <admst:when test="[name='\$simparam']">
#          <admst:variable name="isDependent" value="yes"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:variable name="isFuncDependent" value="no"/>
#          <admst:apply-templates select="arguments" match="recursiveDetectParameterDependence">
#            <admst:if test="[returned('isDependent')/value = 'yes']">
#              <admst:variable name="isFuncDependent" value="yes"/>
#            </admst:if>
#          </admst:apply-templates>
#          <admst:if test="[$isFuncDependent='yes']">
#            <admst:variable name="isDependent" value="yes"/>
#          </admst:if>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:when test="[datatypename='probe']">
#      <!-- no changie da value -->
#    </admst:when>
#    <admst:when test="[(datatypename='variable' or datatypename='variableprototype') and type!='real']">
#      <!-- ignore it: sensitivity is never run on integer vars -->
#    </admst:when>
#    <admst:otherwise>
#      <admst:message format=" recursiveDetectParameterDependence on %(.) unimplemented datatype %(datatypename)\n"/>
#    </admst:otherwise>
#  </admst:choose>
#  <admst:if test="[$isDependent='yes']">
#    <admst:value-to select="#Pdependent" value="yes"/>
#  </admst:if>
#  <admst:return name="isDependent" value="$isDependent"/>
#</admst:template>
#
#<!--
# =================================================================-
# recursiveDetectProbeDependence
# Given any node, recursively populate $probeList (a path to an @
# var) with the probes it depends on.
# =================================================================-
# -->
#<admst:template match="recursiveDetectProbeDependence">
#  <admst:choose>
#    <!-- if this is one of the datatypes that has its own probe list stored by
#         ADMS itself, just copy that and be done-->
#    <admst:when test="[datatypename='variable' or datatypename='expression']">
#      <admst:if test="[not(nilled(probe))]">
#        <admst:push into="$probeList" select="probe" onduplicate="ignore"/>
#      </admst:if>
#    </admst:when>
#    <admst:when test="[datatypename='mapply_unary']">
#      <admst:apply-templates select="arg1" match="recursiveDetectProbeDependence"/>
#    </admst:when>
#    <admst:when test="[datatypename='mapply_binary']">
#      <admst:apply-templates select="arg1" match="recursiveDetectProbeDependence"/>
#      <admst:apply-templates select="arg2" match="recursiveDetectProbeDependence"/>
#    </admst:when>
#    <admst:when test="[datatypename='mapply_ternary']">
#      <admst:apply-templates select="arg1" match="recursiveDetectProbeDependence"/>
#      <admst:apply-templates select="arg2" match="recursiveDetectProbeDependence"/>
#      <admst:apply-templates select="arg3" match="recursiveDetectProbeDependence"/>
#    </admst:when>
#    <admst:when test="[datatypename='function']">
#      <admst:apply-templates select="arguments" match="recursiveDetectProbeDependence"/>
#    </admst:when>
#    <admst:otherwise>
#      <!-- do nothing -->
#    </admst:otherwise>
#  </admst:choose>
#</admst:template>
#
# <!--
# =================================================================-
# collectLimiters
# Given a module, create an "arobavar" (@limiters) containing all the
# assignments in which the verilog limiter function is called.
# Also, create another arobavar (@limitedProbes) containing just
# the probes that are limited by those assignments.
# This template is called early in processing, and the arrays it
# produces will be used to produce the various bits of code needed
# to implement voltage limiting in the device.
#
#  Example:  <admst:apply-templates select="/module" match="collectLimiters"/>
#
#  will result in there being a /module/@limiters and /module/@limitedProbes
# =================================================================-
#-->
#
#<admst:template match="collectLimiters">
#  <admst:variable name="thisModule" select="%(.)"/>
#  <admst:for-each select="assignment[rhs/function/name='\$limit']">
#    <admst:push into="../@limiters" select="." onduplicate="ignore"/>
#  </admst:for-each>
#  <admst:for-each select="@limiters">
#    <admst:for-each select="rhs/probe">
#      <admst:value-to select="#limited" string="yes"/>
#      <admst:if test="[../function/[name='\$limit']/arguments[2]/datatypename='string']">
#        <admst:if test="[../function/[name='\$limit']/arguments[2]/value='typedpnjlim' or ../function/[name='\$limit']/arguments[2]/value='typedpnjlim_new' or ../function/[name='\$limit']/arguments[2]/value='typeddummy' or ../function/[name='\$limit']/arguments[2]/value='typedfetlim' or (../function/[name='\$limit']/arguments[3]/datatypename='string' and ../function/[name='\$limit']/arguments[3]/value='typed')]">
#          <admst:value-to select="#typed" string="yes"/>
#        </admst:if>
#      </admst:if>
#      <admst:push into="$thisModule/@limitedProbes" select="." onduplicate="ignore"/>
#    </admst:for-each>
#  </admst:for-each>
#</admst:template>
#
#<!--
# =================================================================-
# collectCollapsibles
# This template is intended to be called very early in verilog processing.
# It runs through all contributions and tries to identify those that
# allow some node to be collapsed into another (i.e. contributions of the
# form "V(a,b) <+ 0;"
# If it locates such a collapsible, it adds a "#collapsible='yes'" variable
# to the node, and a "@collapsesTo" variable containing the node to which
# this one could collapse.
# In considering which node to collapse of a,b, if there's only one internal
# in the pair, that's the collapsible one.  If both are internal, it'll
# collapse the negative into the positive.
# =================================================================-
# -->
#<admst:template match="collectCollapsibles">
#  <admst:variable name="thisModule" select="%(.)"/>
#  <admst:if test="[not exists(#calledCollectCollapsibles)]">
#    <admst:for-each select="$thisModule/contribution[lhs/discipline/potential=lhs/nature]">
#      <admst:if test="[(rhs/datatypename='expression' and rhs/tree/datatypename='number' and (rhs/tree/value='0' or rhs/tree/value='0.0')) or (rhs/datatypename='number' and (rhs/value='0' or rhs/value='0.0'))]">
#        <admst:choose>
#          <admst:when test="lhs/branch[grounded='no']">
#            <admst:choose>
#              <admst:when test="lhs/branch/nnode[location='internal' or (location='external' and exists(#optional))]">
#                <!-- <admst:if test="[lhs/branch/nnode/location='internal']">
#                  <admst:warning format="collectCollapsibles found internal nnode %(lhs/branch/nnode/name) it wants to collapse into %(lhs/branch/pnode/name)\n"/>
#                </admst:if> -->
#                <admst:if test="[lhs/branch/nnode/location='external']">
#                   <admst:warning format="while processing collapse contributions %(.):  found optional external node %(lhs/branch/nnode/name) we want to collapse into %(lhs/branch/pnode/name).  This might be dangerous and should only work if the optional node is not given at run time.\n"/>
#                </admst:if>
#                <!-- nnode is internal, collapse it into pnode -->
#                <admst:if test="[exists(lhs/branch/nnode/#collapsible) and lhs/branch/nnode/#collapsible='yes']">
#                  <!-- nnode is already collapsible to something, so don't just
#                       blindly collapse it to pnode... check that pnode is
#                       not collapsible, and collapse p into n if not -->
#                  <!-- <admst:warning format="    %(lhs/branch/nnode/name) is already collapsible onto ...%(lhs/branch/nnode/@collapsesTo/name)\n"/> -->
#                  <admst:choose>
#                    <admst:when test="[not(exists(lhs/branch/pnode/#collapsible))]">
#                      <!-- <admst:warning format="    but %(lhs/branch/pnode/name) is not collapsible, so maybe we can collapse it onto %(lhs/branch/nnode/name) instead of the other way around...\n"/> -->
#                      <admst:choose>
#                        <admst:when test="[lhs/branch/pnode/name=lhs/branch/nnode/@collapsesTo/name]">
#                          <!-- <admst:warning format="But that is OK, because we were already going to do that collapsing!\n"/> -->
#                        </admst:when>
#                        <admst:when test="[lhs/branch/pnode/location='external' and not(exists(lhs/branch/pnode/#optional))]">
#                          <!-- <admst:warning format="     unfortunately, that is external... rearranging\n"/> -->
#                          <!-- <admst:warning format="     we would make %(lhs/branch/nnode/@collapsesTo/name) collapse to %(lhs/branch/nnode/name) instead, and make %(lhs/branch/nnode/name) collapse to %(lhs/branch/pnode/name) instead\n"/> -->
#                          <admst:if test="[lhs/branch/nnode/@collapsesTo/location='external']">
#                            <admst:fatal format="Fatal error with collapse contribution %(.) --- we would wind up collapsing an external node onto an internal!\n"/>
#                          </admst:if>
#                          <admst:variable name="saveCollapse" select="%(lhs/branch/nnode/@collapsesTo)"/>
#                          <admst:if test="[exists($saveCollapse/#collapsible)]">
#                            <admst:fatal format="fatal error with collapse contribution %(.) --- tried to rearrange collapsing of %(lhs/branch/nnode/name) and %($saveCollapse/name) but the latter is already collapsible.\n"/>
#                          </admst:if>
#                          <admst:value-to select="$saveCollapse/#collapsible" string="yes"/>
#                          <admst:push into="$saveCollapse/@collapsesTo" onduplicate="ignore" select="lhs/branch/nnode"/>
#                          <admst:reset select="lhs/branch/nnode/@collapsesTo"/>
#                          <admst:push into="lhs/branch/nnode/@collapsesTo" onduplicate="ignore" select="lhs/branch/pnode"/>
#                        </admst:when>
#                        <admst:otherwise>
#                          <admst:if test="[lhs/branch/pnode/location='external' and exists(lhs/branch/pnode/#optional)]">
#                            <admst:warning format="   Issue while processing %(.): trying to collapse optional external node %(lhs/branch/pnode/name) onto node %(lhs/branch/nnode/name).  This can only work at run time if the optional node is not given when collapse is needed.\n"/>
#                          </admst:if>
#                          <admst:value-to select="lhs/branch/pnode/#collapsible" string="yes"/>
#                          <admst:push into="lhs/branch/pnode/@collapsesTo" onduplicate="ignore" select="lhs/branch/nnode"/>
#                        </admst:otherwise>
#                      </admst:choose>
#                    </admst:when>
#                    <admst:otherwise>
#                      <!-- this is only an error if trying to collapse nnode
#                           into something OTHER than what it already collapses
#                           to.  -->
#                      <admst:if test="[(lhs/branch/pnode/name != lhs/branch/nnode/@collapsesTo/name) and (lhs/branch/nnode/name != lhs/branch/pnode/@collapsesTo/name)]">
#                        <admst:error format="Problem with contribution: %(.)\nNot yet supported: collapsing a node multiply... both %(lhs/branch/nnode/name) and %(lhs/branch/pnode/name) are already collapsible.  %(lhs/branch/nnode/name) collapses already into %(lhs/branch/nnode/@collapsesTo) and %(lhs/branch/pnode/name) collapses already into %(lhs/branch/pnode/@collapsesTo)\n"/>
#                      </admst:if>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:if>
#                <admst:if test="[not(exists(lhs/branch/nnode/#collapsible))]">
#                  <!-- nnode is not already collapsible, collapse it into p -->
#                  <admst:value-to select="lhs/branch/nnode/#collapsible" string="yes"/>
#                  <admst:push into="lhs/branch/nnode/@collapsesTo" onduplicate="ignore" select="lhs/branch/pnode"/>
#                </admst:if>
#              </admst:when>
#              <admst:when test="lhs/branch/pnode[location='internal']">
#                <!-- we only get here if nnode was external -->
#                <admst:choose>
#                  <admst:when test="[exists(lhs/branch/pnode/#collapsible)]">
#                    <admst:fatal format=" Collapse contribution '%(.)' requests collapse of internal node %(lhs/branch/pnode/name) onto external node %(lhs/branch/nnode/name), but %(lhs/branch/pnode/name) is already collapsible to %(lhs/branch/pnode/@collapsesTo) as a result of earlier collapses, and we cannot proceed!\n"/>
#                  </admst:when>
#                  <admst:otherwise>
#                    <admst:value-to select="lhs/branch/pnode/#collapsible" string="yes"/>
#                    <admst:push into="lhs/branch/pnode/@collapsesTo" onduplicate="ignore" select="lhs/branch/nnode"/>
#                  </admst:otherwise>
#                </admst:choose>
#              </admst:when>
#            </admst:choose>
#          </admst:when>
#          <admst:otherwise>
#            <admst:choose>
#              <admst:when test="lhs/branch/nnode/[grounded='yes']">
#                <admst:value-to select="lhs/branch/pnode/#collapsible" string="yes"/>
#                <admst:push into="lhs/branch/pnode/@collapsesTo" onduplicate="ignore" select="lhs/branch/nnode"/>
#              </admst:when>
#              <admst:when test="lhs/branch/pnode/[grounded='yes']">
#                <admst:value-to select="lhs/branch/nnode/#collapsible" string="yes"/>
#                <admst:push into="lhs/branch/nnode/@collapsesTo" onduplicate="ignore" select="lhs/branch/pnode"/>
#              </admst:when>
#            </admst:choose>
#
#          </admst:otherwise>
#        </admst:choose>
#      </admst:if>
#    </admst:for-each>
#    <admst:value-to select="$thisModule/#calledCollectCollapsibles" string="yes"/>
#  </admst:if>
#</admst:template>
#
#<!--
# =================================================================-
# declareCollapsibleBools
# For each node that may be collapsed, generate a declaration of a bool
# that will be used by Xyce to tell whether to collapse it or not.
# Pass the module in the select field of the apply-templates call.
# =================================================================-
# -->
#<admst:template match="declareCollapsibleBools">
#  <admst:if test="[count(node[#collapsible='yes'])>0]">
#    <admst:text format="     // bools for collapsing nodes\n"/>
#    <admst:for-each select="node[#collapsible='yes']">
#      <admst:text format="     bool collapseNode_%(name);\n"/>
#    </admst:for-each>
#  </admst:if>
#</admst:template>
#
#  <!--
#      recursiveFindContrib
#      This template is passed any item from the analog/code block,
#      and recurses downward until it finds a contribution of the form
#      V(branch) <+ 0;   (or 0.0)
#      When it finds one, it recurses upwards through the ADMS data tree
#      using the upwardRecurseCheckDepend template.
#  -->
#
#  <admst:template match="recursiveFindContrib">
#    <admst:choose>
#      <admst:when test="adms[datatypename='block']">
#        <admst:apply-templates select="item" match="recursiveFindContrib"/>
#      </admst:when>
#      <admst:when test="adms[datatypename='conditional']">
#        <admst:apply-templates select="then" match="recursiveFindContrib"/>
#        <admst:apply-templates select="else" match="recursiveFindContrib"/>
#      </admst:when>
#      <admst:when test="adms[datatypename='case']">
#        <admst:for-each select="caseitem">
#          <admst:apply-templates select="code" match="recursiveFindContrib"/>
#        </admst:for-each>
#      </admst:when>
#      <admst:when test="adms[datatypename='contribution']">
#        <admst:if test="[(lhs/discipline/potential=lhs/nature) and ((rhs/datatypename='expression' and rhs/tree/datatypename='number' and (rhs/tree/value='0' or rhs/tree/value='0.0')) or (rhs/datatypename='number' and (rhs/value='0' or rhs/value='0.0')))]">
#          <admst:apply-templates select="." match="upwardRecurseCheckDepend"/>
#        </admst:if>
#      </admst:when>
#    </admst:choose>
#  </admst:template>
#
#  <!--
#      upwardRecurseCheckDepend
#      Given any ADMS data tree item, recurse UPWARD through the ADMS data
#      tree.  Check that all conditionals depend only on variables of
#      global_instance or global_model scope, or are input parameters.
#
#      Flag a fatal error if any local variables are used in these
#      conditional expressions.  We just flag the error, we don't
#      abort, so the entire processing of the module can proceed and
#      report all errors.  The caller must check the "$collapseFailure"
#      variable and abort if it's "yes".
#
#      The starting point should be a contribution that collapses nodes, e.g.
#      V(branch) <+ 0;
#      -->
#  <admst:template match="upwardRecurseCheckDepend">
#    <admst:choose>
#      <admst:when test="adms[datatypename='expression']">
#        <admst:for-each select="variable">
#          <admst:if test="[not (input='yes' or (scope='global_instance' or scope='global_model'))]">
#            <admst:warning format="Collapse error:  Node collapse conditional depends on variable %(name), which is not an input parameter and which has scope of '%(scope)'.\n\n  Only variables of global_instance or global_model scope may be used in collapse conditionals in this version of Xyce/ADMS.\n\n  To clear this error, move bias-independent intialization of %(name) into an '@(initial_instance)' or '@(initial_model) block.\n"/>
#            <admst:variable name="collapseFailure" string="yes"/>
#          </admst:if>
#          <admst:if test="[OPdependent='yes']">
#            <admst:warning format="  Collapse error:  Node collapse conditional depends on variable %(name) that is bias-dependent.  Collapse conditionals must be bias-independent.\n"/>
#            <admst:variable name="collapseFailure" string="yes"/>
#          </admst:if>
#        </admst:for-each>
#      </admst:when>
#      <admst:when test="adms[datatypename='conditional']">
#        <admst:apply-templates select="if" match="upwardRecurseCheckDepend"/>
#      </admst:when>
#      <admst:when test="adms[datatypename='case']">
#        <admst:apply-templates select="case" match="upwardRecurseCheckDepend"/>
#      </admst:when>
#    </admst:choose>
#    <admst:if test="[not(../adms/datatypename = 'analog' or ./adms/datatypename='expression')]">
#      <admst:apply-templates select=".." match="upwardRecurseCheckDepend"/>
#    </admst:if>
#  </admst:template>
#
#
#  <!--
#      evaluateCollapse
#      Emit code for evaluating when to collapse nodes.
#      Only assignments that assign to variables that collapse depends on
#      are emitted.
#      Control structures that CONTAIN assignments that are emitted will also
#      be generated, e.g.
#
#      if (foo)
#        bar=baz;
#
#      will generate code if bar is a collapse-determining variable.
#
#      TODO:  If we find we need to generate FOR or WHILE loops, then we
#      should give up and report an error.  Handling these constructs correctly
#      is too difficult, and no rational model should ever have collapse
#      determination that requires it.  No currently known models do.
#
#  -->
#  <admst:template match="evaluateCollapse">
#    <admst:choose>
#
#      <!--IF/ELSE-->
#      <admst:when test="[datatypename='conditional']">
#        <admst:choose>
#          <admst:when test="if[nilled(variable[OPdependent='yes'])]">
#            <admst:choose>
#              <admst:when test="if/math[dependency='constant']">
#                <admst:variable name="thenOutputSomething" string="no"/>
#                <admst:variable name="thenOutput" string=""/>
#                <admst:variable name="elseOutputSomething" string="no"/>
#                <admst:variable name="elseOutput" string=""/>
#                <admst:apply-templates select="then" match="evaluateCollapse">
#                  <admst:value-of select="returned('outputSomething')/value"/>
#                  <admst:variable name="thenOutputSomething" select="%s"/>
#                  <admst:value-of select="returned('output')/value"/>
#                  <admst:variable name="thenOutput" select="%s"/>
#                </admst:apply-templates>
#                <admst:if test="[exists(else)]">
#                  <admst:apply-templates select="else" match="evaluateCollapse">
#                    <admst:value-of select="returned('outputSomething')/value"/>
#                    <admst:variable name="elseOutputSomething" select="%s"/>
#                    <admst:value-of select="returned('output')/value"/>
#                    <admst:variable name="elseOutput" select="%s"/>
#                  </admst:apply-templates>
#                </admst:if>
#
#                <admst:if test="[$thenOutputSomething='yes']">
#                  <admst:variable name="output" string="if (%(processTerm(if)/[name='returnedExpression']/value))"/>
#                  <admst:variable name="output" string="$output\n{\n$thenOutput\n}\n"/>
#                  <admst:if test="[$elseOutputSomething='yes']">
#                    <admst:variable name="output" string="$output\nelse\n{\n$elseOutput\n}\n"/>
#                  </admst:if>
#                  <admst:variable name="outputSomething" string="yes"/>
#                </admst:if>
#                <admst:if test="[$thenOutputSomething='no' and $elseOutputSomething='yes']">
#                  <admst:variable name="output" string="if (!(%(processTerm(if)/[name='returnedExpression']/value)))"/>
#                  <admst:variable name="output" string="$output\n{\n$elseOutput\n}\n"/>
#                </admst:if>
#
#                <admst:choose>
#                  <admst:when test="[$thenOutputSomething='yes' or $elseOutputSomething='yes']">
#                    <admst:return name="outputSomething" string="yes"/>
#                    <admst:return name="output" string="$output"/>
#                  </admst:when>
#                  <admst:otherwise>
#                    <admst:return name="outputSomething" string="no"/>
#                    <admst:return name="output" string=""/>
#                  </admst:otherwise>
#                </admst:choose>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="thenOutputSomething" string="no"/>
#                <admst:variable name="thenOutput" string=""/>
#                <admst:variable name="elseOutputSomething" string="no"/>
#                <admst:variable name="elseOutput" string=""/>
#                <admst:apply-templates select="then" match="evaluateCollapse">
#                  <admst:value-of select="returned('outputSomething')/value"/>
#                  <admst:variable name="thenOutputSomething" select="%s"/>
#                  <admst:value-of select="returned('output')/value"/>
#                  <admst:variable name="blockOutput" select="%s"/>
#                  <admst:if test="[$thenOutputSomething = 'yes']">
#                    <admst:variable name="thenOutput" string="%($blockOutput)\n"/>
#                  </admst:if>
#                </admst:apply-templates>
#                <admst:apply-templates select="else" match="evaluateCollapse">
#                  <admst:value-of select="returned('outputSomething')/value"/>
#                  <admst:variable name="elseOutputSomething" select="%s"/>
#                  <admst:value-of select="returned('output')/value"/>
#                  <admst:variable name="blockOutput" select="%s"/>
#                  <admst:if test="[$elseOutputSomething = 'yes']">
#                    <admst:variable name="outputSomething" string="yes"/>
#                    <admst:variable name="elseOutput" string="%($blockOutput)"/>
#                  </admst:if>
#                </admst:apply-templates>
#                <admst:variable name="output" string="%($thenOutput)%($elseOutput)"/>
#                <admst:choose>
#                  <admst:when test="[$thenOutputSomething='yes' or $elseOutputSomething='yes']">
#                    <admst:return name="outputSomething" string="yes"/>
#                    <admst:return name="output" string="$output"/>
#                  </admst:when>
#                  <admst:otherwise>
#                    <admst:return name="outputSomething" string="no"/>
#                    <admst:return name="output" string=""/>
#                  </admst:otherwise>
#                </admst:choose>
#
#              </admst:otherwise>
#            </admst:choose>
#          </admst:when>
#          <admst:otherwise>
#            <admst:return name="outputSomething" string="no"/>
#            <admst:return name="output" string=""/>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#
#      <!-- CASE -->
#      <admst:when test="[datatypename='case']">
#        <admst:choose>
#          <admst:when test="case[nilled(variable[OPdependent='yes'])]">
#            <admst:variable name="caseOutputSomething" string="no"/>
#            <admst:variable name="fullCaseOutput" string=""/>
#            <admst:variable name="haveDefault" string="no"/>
#            <admst:if test="[count(caseitem[defaultcase='yes'])>0]">
#              <admst:variable name="haveDefault" string="yes"/>
#            </admst:if>
#            <admst:choose>
#              <admst:when test="case/math[dependency='constant']">
#                <admst:variable name="caseConditionExpr" string="%(processTerm(case)/[name='returnedExpression']/value)"/>
#                <admst:for-each select="caseitem[defaultcase='no']">
#                  <admst:apply-templates select="code" match="evaluateCollapse">
#                    <admst:value-of select="returned('outputSomething')/value"/>
#                    <admst:variable name="caseItemOutputSomething" select="%s"/>
#                    <admst:value-of select="returned('output')/value"/>
#                    <admst:variable name="caseItemOutput" select="%s"/>
#                    <admst:if test="[$caseItemOutputSomething='yes']">
#                      <admst:variable name="caseOutputSomething" string="yes"/>
#                    </admst:if>
#                    <!-- now assemble the conditional for output -->
#                    <admst:variable name="oredCondition" string=""/>
#                    <admst:for-each select="../condition">
#                      <admst:apply-templates select="." match="%(datatypename)">
#                        <admst:if test="[$oredCondition != '']">
#                          <admst:variable name="oredCondition" string="$oredCondition || "/>
#                        </admst:if>
#                        <admst:variable name="oredCondition" string="$oredCondition ($caseConditionExpr == %(returned('returnedExpression')/value))"/>
#                      </admst:apply-templates>
#                    </admst:for-each>  <!-- condition -->
#                  </admst:apply-templates>
#                  <!-- add the conditional to the output -->
#                  <admst:variable name="fullCaseOutput" string="$fullCaseOutput if ( $oredCondition )\n"/>
#                  <admst:if test="[$caseItemOutputSomething = 'yes']">
#                    <admst:variable name="fullCaseOutput" string="$fullCaseOutput{\n$caseItemOutput\n}\nelse\n"/>
#                  </admst:if>
#                  <admst:if test="[$caseItemOutputSomething = 'no']">
#                    <admst:variable name="fullCaseOutput" string="$fullCaseOutput\n{\n // nothing to see here \n}\nelse\n"/>
#                  </admst:if>
#                </admst:for-each> <!-- non-default caseitem-->
#                <!-- now handle a default if we have one
#                     because we've been emitting all those "else" lines,
#                     we will emit an empty block just to keep syntax right -->
#                <admst:if test="[$haveDefault='no']">
#                  <admst:variable name="fullCaseOutput" string="$fullCaseOutput{\n // there is no default \n}\n"/>
#                </admst:if>
#                <admst:if test="[$haveDefault='yes']">
#                  <admst:for-each select="caseitem[defaultcase='yes']">
#                    <admst:apply-templates select="code" match="evaluateCollapse">
#                      <admst:value-of select="returned('outputSomething')/value"/>
#                      <admst:variable name="caseItemOutputSomething" select="%s"/>
#                      <admst:value-of select="returned('output')/value"/>
#                      <admst:variable name="caseItemOutput" select="%s"/>
#                      <admst:if test="[$caseItemOutputSomething='yes']">
#                        <admst:variable name="caseOutputSomething" string="yes"/>
#                    <admst:variable name="fullCaseOutput" string="$fullCaseOutput{\n$caseItemOutput\n}\n"/>
#                      </admst:if>
#                      <admst:if test="[$caseItemOutputSomething='no']">
#                        <admst:variable name="fullCaseOutput" string="$fullCaseOutput{\n//nothing to see here\n}\n"/>
#                      </admst:if>
#                    </admst:apply-templates>
#                  </admst:for-each> <!-- really just one default -->
#                </admst:if>
#                <admst:return name="outputSomething" string="$caseOutputSomething"/>
#                <admst:return name="output" string="$fullCaseOutput"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:error format="evaluateCollapse: case not constant, we can't handle that yet.\n"/>
#                <admst:return name="outputSomething" string="no"/>
#                <admst:return name="output" string=""/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:when>
#          <admst:otherwise>
#             <!-- do nothing -->
#            <admst:return name="outputSomething" string="no"/>
#            <admst:return name="output" string=""/>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#
#      <!--CONTRIBUTION-->
#      <admst:when test="[datatypename='contribution']">
#        <admst:choose>
#          <admst:when test="lhs[discipline/potential=nature]">
#            <admst:choose>
#              <admst:when test="[exists(lhs/branch/nnode/#collapsible) and lhs/branch/nnode/#collapsible='yes' and lhs/branch/nnode/@collapsesTo=lhs/branch/pnode]">
#                <admst:return name="output" string="collapseNode_%(lhs/branch/nnode/name) = true;\n"/>
#                <admst:return name="outputSomething" string="yes"/>
#              </admst:when>
#              <admst:when test="[exists(lhs/branch/pnode/#collapsible) and lhs/branch/pnode/#collapsible='yes' and lhs/branch/pnode/@collapsesTo=lhs/branch/nnode]">
#                <admst:return name="output" string="collapseNode_%(lhs/branch/pnode/name) = true;\n"/>
#                <admst:return name="outputSomething" string="yes"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:return name="output" string=""/>
#                <admst:return name="outputSomething" string="no"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:when>
#          <admst:otherwise>
#            <admst:return name="output" string=""/>
#            <admst:return name="outputSomething" string="no"/>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#
#      <!--BLOCK-->
#      <admst:when test="[datatypename='block']">
#        <admst:value-to select="./#tempOutput" value=""/>
#        <admst:value-to select="./#tempOutputSomething" value="no"/>
#        <admst:variable name="outputSomething" value="no"/>
#        <admst:if test="[name != '']">
#          <admst:value-to select="./#tempOutput" value="// begin block named %(name)\n"/>
#        </admst:if>
#        <admst:for-each select="variable[#collapseDepends='yes']">
#          <admst:value-to select="./#tempOutputSomething" value="yes"/>
#          <admst:variable name="outputSomething" value="yes"/>
#          <admst:if test="[type='integer']">
#            <admst:value-to select="../#tempOutput" value="%(../#tempOutput)int %(name);\n"/>
#          </admst:if>
#          <admst:if test="[type='real']">
#            <admst:value-to select="../#tempOutput" value="%(../#tempOutput)double %(name)\n"/>
#          </admst:if>
#          <admst:if test="[type='string']">
#            <admst:value-to select="../#tempOutput" value="%(../#tempOutput)char * %(name)\n"/>
#          </admst:if>
#        </admst:for-each>
#
#        <admst:apply-templates select="item" match="evaluateCollapse">
#          <admst:value-of select="returned('outputSomething')/value"/>
#          <admst:variable name="blockOutputSomething" select="%s"/>
#          <admst:value-of select="returned('output')/value"/>
#          <admst:variable name="blockOutput" select="%s"/>
#          <admst:if test="[$blockOutputSomething = 'yes']">
#            <admst:variable name="outputSomething" string="yes"/>
#            <admst:value-to select="../#tempOutputSomething" value="yes"/>
#            <admst:variable name="tempOutput" select="%(../#tempOutput)\n$blockOutput"/>
#            <admst:value-to select="../#tempOutput" value="$tempOutput"/>
#          </admst:if>
#        </admst:apply-templates>
#        <admst:variable name="output" select="%(./#tempOutput)"/>
#        <admst:if test="[name != '']">
#          <admst:variable name="output" select="%($output)\n// end block  named %(name)\n"/>
#        </admst:if>
#        <admst:choose>
#          <admst:when test="[./#tempOutputSomething='yes']">
#            <admst:return name="output" string="$output"/>
#            <admst:return name="outputSomething" string="yes"/>
#          </admst:when>
#          <admst:otherwise>
#            <admst:return name="output" string=""/>
#            <admst:return name="outputSomething" string="no"/>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#
#
#      <!--other stuff to ignore-->
#      <admst:when test="[datatypename='expression' or datatypename='probe' or datatypename='variable' or datatypename='mapply_unary' or datatypename='mapply_binary' or datatypename='mapply_ternary' or datatypename='function' or datatypename='number' or datatypename='string' or datatypename='nilled' or datatypename='blockvariable' or datatypename='callfunction' or datatypename='case' or datatypename='whileloop' or datatypename='forloop' or datatypename='assignment']">
#        <admst:return name="output" string=""/>
#        <admst:return name="outputSomething" string="no"/>
#      </admst:when>
#
#      <admst:otherwise>
#        <admst:fatal format="%(datatypename): adms element not implemented\n"/>
#      </admst:otherwise>
#    </admst:choose>
#
#    <!-- we have to clear this now, and it has to be after the return.
#         If we clear it before the return, somehow $output gets cleared.  Is
#         that because it's still tied to the memory location of #tempoutput?
#         And if we do NOT clear it, we consume all available memory and puke
#         on complex files. -->
#    <admst:value-to select="./#tempOutput" value=""/>
#  </admst:template>
#
#<!--
#   =================================================================-
#   collectExtraUnknowns
#   Another "execute early in the processing" deal.
#   Any use of "flow probes" requires an extra unknown (the flow through
#   the branch).
#   Any use of "potential sources" *also* requires an extra unknown (also
#   the flow through the branch).
#   These two cases also, naturally, require an additional equation.  There
#   are multiple possibilities:
#
#    A)  Flow probe used only in a flow source, without any associated
#        contribution:
#        I(b2) &lt;+ I(b1);
#        In this case, the extra unknown is I(b1), and the extra equation is
#          V(b1) = 0.
#
#    B)  Flow probe used in a flow source, with an associated contribution:
#        I(b1) &lt;+ expression;
#        I(b2) &lt;+ A*I(b1);
#        In this case, the extra unknown is I(b1), but the extra equation is:
#          sum(contributions into I(b1)) -I(b1) = 0
#
#    C)  Potential source
#        V(B1) &lt;+ expression_not_referencing_the_branch_B1;
#        Extra unknown is still I(B1), extra equation is:
#          sum (all contributions into V(B1)) - V(B1) = 0
#
#    D) Potential source referencing a flow probe:
#        V(b1) &lt;+ expression;
#        V(b2) &lt;+ A*I(B1)
#        Extra unknown is I(B1), extra equation same as C
#
#   Of course, each of these impacts the loads for the KCLs of the endpoints
#   of B1 and B2.
#
#      A) add/subtract I(B1) to endpoint nodes of B1
#      B) add/subtract I(B1) to endpoint nodes of B1
#      C) add/subtract I(B1) to endpoints of B1
#      D) add/subtract I(B1) to endpoints of B1, use unknown I(B1) in
#         equations for endpoints of B2.
#
#   There are other cases, too, but these are already handled elsewhere.
#
#   The purpose of this template is to figure out which new unknowns to
#   allocate for, which is pretty easy (look for flow probes in the module's
#   list of probes, and look for potential sources that aren't already flagged
#   as collapsible (zero RHS) in the module's list of sources: each one
#   means there has to be an associated current branch).
#
#   Determining what type of *equation* to do really depends on the contribution
#   involved.
#   -->
#<admst:template match="collectExtraUnknowns">
#  <admst:variable name="thisModule" select="%(.)"/>
#  <admst:reset select="$thisModule/@extraUnknowns"/>
#
#  <!-- First find the extra unknowns due to flow probes -->
#  <admst:for-each select="/module/probe[nature=discipline/flow]">
#    <admst:push into="$thisModule/@extraUnknowns" select="branch" onduplicate="ignore"/>
#    <admst:value-to select="#branchvar" string="yes" />
#  </admst:for-each>
#
#  <!-- Now find the extra unknowns due to potential sources -->
#  <admst:for-each select="$thisModule/source[not(exists(branch/nnode/#collapsible)) and not(exists(branch/pnode/#collapsible)) and nature=discipline/potential]">
#    <admst:push into="$thisModule/@extraUnknowns" select="branch" onduplicate="ignore"/>
#  </admst:for-each>
#
#  <!-- we now know the extra unknowns, which are all branches.  Unfortunately,
#       ADMS does not store any information about this stuff in its "jacobian"
#       structure, which makes life difficult for us.  So let us create our
#       own data.  -->
#  <!-- we'll make three arrays to help us figure out jacobian stuff
#
#       we need a list of nodes
#       that depend on branch variables.  We'll push the branch into the
#       node. We handle this by pushing the list of branch dependencies
#       into the actual node structure.
#
#       We need  a list of branches that depend on nodal vars.
#       This will let us create the jacobian row for the branch and fill it
#       with nodal dependencies.  These will simply be put in an array
#       inside the @extraUnknowns array called @nodeDeps.
#
#       We need a list of branches that depend on branch vars.
#       This will let us augment the branch equation rows.  This, too,
#       will be stored in the @branchDeps array under the @extraUnknowns.
#       -->
#    <admst:for-each select="$thisModule/@extraUnknowns">
#    <admst:variable name="thisBranch" select="%(.)"/>
#
#      <admst:push into="pnode/@branchDeps" select="." onduplicate="ignore"/>
#      <admst:if test="[nnode/grounded = 'no']">
#        <admst:push into="nnode/@branchDeps" select="." onduplicate="ignore"/>
#      </admst:if>
#
#      <admst:apply-templates match="collectBranchDepends" select="."/>
#      <admst:for-each select="/module/@countNodes">
#        <admst:push into="$thisBranch/@nodeDeps" select="." onduplicate="ignore"/>
#      </admst:for-each>
#      <admst:for-each select="/module/@countBranches">
#        <admst:push into="$thisBranch/@branchDeps" select="." onduplicate="ignore"/>
#      </admst:for-each>
#    </admst:for-each>
#
#    <!-- Finally, we have an issue:  if a voltage source is uses, but
#         the corresponding current probe is never used (such is done if
#         one has a pure voltage source), then our process so far will never
#         allocate a place for the current branch probe that we need to use in
#         updateIntermediateVars.  So here, we'll go through our list of
#         extra branch equations and make a list of branches for which there
#         is no probe in the tree.  This will be used later to allocate what's
#         missing. -->
#    <admst:reset select="$thisModule/@extraProbeBranches"/>
#    <admst:for-each select="$thisModule/@extraUnknowns">
#      <admst:variable name="thePnodeName" select="%(pnode/name)"/>
#      <admst:variable name="theNnodeName" select="%(nnode/name)"/>
#      <admst:if test="[not(exists($thisModule/probe[nature=discipline/flow and branch/pnode/name=$thePnodeName and branch/nnode/name=$theNnodeName]))]">
#        <admst:push into="$thisModule/@extraProbeBranches" select="." onduplicate="ignore"/>
#      </admst:if>
#    </admst:for-each>
#
#<!--   Debugging output commented out
#
#  <admst:for-each select="$thisModule/@extraUnknowns">
#    // branch %(.) depends on nodes %(@nodeDeps)
#    // branch %(.) depends on branches %(@branchDeps)
#
#  </admst:for-each>
#
#  <admst:for-each select="$thisModule/node[grounded='no']">
#    <admst:if test="[not(nilled(@branchDeps))]">
#      // Node %(.) depends on branches %(@branchDeps)
#
#    </admst:if>
#  </admst:for-each>
#-->
#</admst:template>
#
#<!--
#   =================================================================-
#   finishUpBranchEquations
#
#   Branch equations are of the form:
#     (sum of contributions into source) - (value of source) = 0
#
#   Our contribution template does the sum part, but we now need to do
#   the last bit.
#
#    . must be a module
#   =================================================================-
#   -->
#  <admst:template match="finishUpBranchEquations">
#
#    <admst:variable name="thisModule" select="%(.)"/>
#    <admst:for-each select="./contribution[lhs/nature=lhs/discipline/potential and not(rhs/tree/datatypename='number' and (rhs/tree/value='0' or rhs/tree/value='0.0'))]">
#      <!-- do nothing if a noise term -->
#      <admst:if test="[whitenoise='no' and flickernoise='no']">
#
#        <!-- The extra terms into the voltage nodes are only done once,
#             and only into the static contributions. -->
#        <admst:variable name="pnode" select="%(lhs/branch/pnode)"/>
#        <admst:variable name="pnodeConstant" select="%(xyceNodeConstantName($pnode)/[name='nodeConstant']/value)"/>
#        <admst:variable name="nnode" select="%(lhs/branch/nnode)"/>
#        <admst:if test="[rhs/static='yes' or (rhs/dynamic='yes' and not(exists($thisModule/contribution[lhs/nature=lhs/discipline/potential and lhs/branch/pnode=$pnode and lhs/branch/nnode=$nnode and rhs/static='yes'])))]">
#          // Additional term resulting from contributions into %(lhs)
#
#          <admst:text format="staticContributions[$pnodeConstant] += probeVars[%(xyceFlowProbeConstantName(lhs/branch)/[name='probeConstant']/value)];\n"/>
#          <admst:text format="d_staticContributions[$pnodeConstant][%(xyceFlowProbeConstantName(lhs/branch)/[name='probeConstant']/value)] += d_probeVars[%(xyceFlowProbeConstantName(lhs/branch)/[name='probeConstant']/value)][%(xyceFlowProbeConstantName(lhs/branch)/[name='probeConstant']/value)];\n"/>
#          <admst:if test="$nnode[grounded='no']">
#            <admst:variable name="nnodeConstant" select="%(xyceNodeConstantName($nnode)/[name='nodeConstant']/value)"/>
#            <admst:text format="staticContributions[$nnodeConstant] -= probeVars[%(xyceFlowProbeConstantName(lhs/branch)/[name='probeConstant']/value)];\n"/>
#            <admst:text format="d_staticContributions[$nnodeConstant][%(xyceFlowProbeConstantName(lhs/branch)/[name='probeConstant']/value)] -= d_probeVars[%(xyceFlowProbeConstantName(lhs/branch)/[name='probeConstant']/value)][%(xyceFlowProbeConstantName(lhs/branch)/[name='probeConstant']/value)];\n"/>
#          </admst:if>
#        </admst:if>
#      </admst:if>
#    </admst:for-each>
#
#    <admst:for-each select="./@extraUnknowns">
#      <!-- There is one special case:  a branch where the
#           flow probe is used AND there is a flow source for it.
#            In this case the branch equation is
#              (sum of contributions into I(branch)) - I(branch) =0
#
#            In all other cases, the branch equation will always be:
#              (sum of contributions into V(branch)) - V(branch) = 0
#       -->
#       <admst:text format="  // Final term for branch equation %(xyceBranchConstantName(.)/[name='branchConstant']/value) \n"/>
#  <admst:variable name="thePnodeName" select="%(pnode/name)"/>
#  <admst:variable name="theNnodeName" select="%(nnode/name)"/>
#       <admst:choose>
#         <admst:when test="[exists(/module/contribution[lhs/branch/pnode/name='$thePnodeName' and lhs/branch/nnode/name='$theNnodeName' and lhs/nature=lhs/discipline/flow]) and not exists(/module/contribution[lhs/branch/pnode/name='$thePnodeName' and lhs/branch/nnode/name='$theNnodeName' and lhs/nature=lhs/discipline/potential])]">
#           <admst:warning format="This module makes use of flow probe in branch ($thePnodeName,$theNnodeName) without any associated potential contribution to that branch, and with the use of flow contributions to that branch.  This particular use case is broken in Xyce/ADMS.\n"/>
#           <admst:text format="  staticContributions[%(xyceBranchConstantName(.)/[name='branchConstant']/value)] -= probeVars[%(xyceFlowProbeConstantName(.)/[name='probeConstant']/value)];\n"/>
#           <admst:text format="  d_staticContributions[%(xyceBranchConstantName(.)/[name='branchConstant']/value)][%(xyceFlowProbeConstantName(.)/[name='probeConstant']/value)] -= d_probeVars[%(xyceFlowProbeConstantName(.)/[name='probeConstant']/value)][%(xyceFlowProbeConstantName(.)/[name='probeConstant']/value)];\n"/>
#         </admst:when>
#         <admst:otherwise>
#           <!-- ICK.  In this case, we don't usually HAVE a probe variable,
#                and so we must calculate the drop V(branch) directly.
#                We don't rely on automatic differentiation to do derivatives
#                w.r.t. this, and will have to have a manual +/- dependence in
#                the
#                branch's static jacobian. -->
#           <admst:text format="// Derivative of this term with respect to node is +/-1\n"/>
#           <admst:text format="// Handling of that derivative is done explicitly in the loadDAEdFdX method\n"/>
#           <admst:text format="  staticContributions[%(xyceBranchConstantName(.)/[name='branchConstant']/value)] -= (*solVectorPtr)[%(xyceNodeLIDVariable(./pnode))]"/>
#           <admst:if test="[nnode/grounded='no']">
#             <admst:text format="-(*solVectorPtr)[%(xyceNodeLIDVariable(./nnode))]"/>
#           </admst:if>
#         <admst:text format=";\n"/>
#         </admst:otherwise>
#       </admst:choose>
#
#    </admst:for-each>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   functionPrecomputation
#     When evaluating assignments, we also need to evaluate (sometimes)
#     the derivatives of the variables.  If the RHS of an assignment
#     contains function calls, generating the assignment and its
#     derivative assignments becomes problematic.  To address this,
#     Xyce/ADMS will emit precomputation lines that evaluate the
#     function and store its result in a variable, and the variable
#     will be used in the actual expression instead.  This will also
#     enable us to deal with derivatives of functions in a similar manner
#     through functionDerivativePrecomputation.
#   =================================================================-
#  -->
#  <admst:template match="functionPrecomputation">
#    <!-- the index of this function call in the expression in which
#         it appears -->
#    <admst:variable name="functionIndex" select="%(index(../function,.))"/>
#    <!-- The name of the function being called, one simple for the
#         variable name, the other more complex for the call -->
#    <admst:variable name="functionNameS" select="%(funcnameSimple(.)/[name='fname']/value)"/>
#    <admst:variable name="functionName" select="%(funcname(.)/[name='fname']/value)"/>
#
#    <admst:choose>
#      <admst:when test="[class='analog']">
#        <admst:text format="%(analogFunctionEvaluatorConstruction(.)/[name='returnedExpression']/value);\n"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:text format="double value_%($functionNameS)_%($functionIndex) = %(functionCall(.)/[name='returnedExpression']/value);\n"/>
#      </admst:otherwise>
#    </admst:choose>
#  </admst:template>
#  <!--
#   =================================================================-
#   functionDerivativePrecomputation
#     When evaluating assignments, we also need to evaluate (sometimes)
#     the derivatives of the variables.  If the RHS of an assignment
#     contains function calls, generating the assignment and its
#     derivative assignments becomes problematic.  As with
#     functionPrecomputation, we go over the function in advance of
#     emitting the assignment, and compute as needed the derivatives of
#     function calls with respect to their arguments.  Note that to get
#     the actual derivative of the function call with respect to solution,
#     you still have to use the chain rule.
#
#     We will name these derivative variables:
#       deriv_<function name>_<index>_d<argnum>
#     where index is the unique index of this function call within
#     the expression, and the argnum is the number of the argument
#     starting at zero.
#
#   =================================================================-
#  -->
#  <admst:template match="functionDerivativePrecomputation">
#    <admst:if test="[hasVoltageDependentFunction='yes' or $globalCurrentScope='sensitivity']">
#      <admst:for-each select="function">
#        <admst:variable name="functionIndex" select="%(index(../function,.))"/>
#        <admst:variable name="functionNameS" select="%(funcnameSimple(.)/[name='fname']/value)"/>
#        <admst:variable name="functionName" select="%(funcname(.)/[name='fname']/value)"/>
#        <admst:variable name="varType" select="double "/>
#
#        <admst:choose>
#          <admst:when test="[name='exp' or name='ln' or name='log' or name='sqrt' or name='abs' or name='limexp' or name='cos' or name='sin' or name='tan' or name='acos' or name='asin' or name='atan' or name='cosh' or name='sinh' or name='tanh' or name='acosh' or name='asinh' or name='atanh']">
#            <admst:if test="[arguments/math/dependency!='constant' or ($globalCurrentScope='sensitivity' and exists(arguments[1]/#Pdependent))]">
#              <admst:choose>
#                <admst:when test="[name='exp']">
#                  <admst:text format="%($varType) deriv_exp_%($functionIndex)_d0 = value_exp_%($functionIndex);\n"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:apply-templates select="arguments[1]" match="processTerm">
#                    <admst:value-of select="returned('returnedExpression')/value"/>
#                    <admst:variable name="a1" select="%s"/>
#                  </admst:apply-templates>
#                  <admst:choose>
#                    <admst:when test="[name='ln']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (1.0/$a1);\n"/>
#                    </admst:when>
#                    <admst:when test="[name='log']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (1.0/(log(10.0)*$a1));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='sqrt']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (0.5/value_sqrt_%($functionIndex));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='abs']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = ((($a1)&gt;=0)?(+1.0):(-1.0));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='cos']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (-sin($a1));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='sin']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (cos($a1));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='tan']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (1.0/cos($a1)/cos($a1));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='acos']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (-1.0/sqrt(1.0-$a1*$a1));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='asin']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (+1.0/sqrt(1.0-$a1*$a1));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='atan']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (+1.0/(1+$a1*$a1));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='cosh']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (sinh($a1));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='sinh']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (cosh($a1));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='tanh']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (1.0/cosh($a1)/cosh($a1));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='acosh']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (1.0/(sqrt($a1-1.0)*sqrt($a1+1.0)));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='asinh']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (1.0/(sqrt($a1*$a1+1.0)));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='atanh']">
#                      <admst:text format="%($varType) deriv_%($functionNameS)_%($functionIndex)_d0 = (1.0/(1-$a1*$a1));\n"/>
#                    </admst:when>
#                    <admst:when test="[name='limexp']">
#                      <admst:text format="%($varType) deriv_limexp_%($functionIndex)_d0 = ((($a1)&lt;80)?(value_limexp_%($functionIndex)):exp(80.0));\n"/>
#                </admst:when>
#                  </admst:choose>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#          </admst:when>
#          <admst:when test="[name='pow' or name='min' or name='max' or name='hypot' or name='atan2']">
#            <admst:apply-templates select="arguments[1]" match="processTerm">
#              <admst:value-of select="returned('returnedExpression')/value"/>
#              <admst:variable name="a1" select="%s"/>
#            </admst:apply-templates>
#
#            <admst:apply-templates select="arguments[2]" match="processTerm">
#              <admst:value-of select="returned('returnedExpression')/value"/>
#              <admst:variable name="a2" select="%s"/>
#            </admst:apply-templates>
#            <admst:if test="[arguments[1]/math/dependency!='constant' or ($globalCurrentScope='sensitivity' and exists(arguments[1]/#Pdependent))]">
#              <admst:choose>
#                <admst:when test="[name='pow']">
#                  <admst:text format="%($varType) deriv_pow_%($functionIndex)_d0 = ((%($a1) == 0.0)?0.0:(value_pow_%($functionIndex)*%($a2)/%($a1)));\n"/>
#                </admst:when>
#                <admst:when test="[name='min']">
#                  <admst:text format="%($varType) deriv_min_%($functionIndex)_d0 = ((%($a1)&lt;=%($a2))?1.0:0.0);\n"/>
#                </admst:when>
#                <admst:when test="[name='max']">
#                  <admst:text format="%($varType) deriv_max_%($functionIndex)_d0 = ((%($a1)&gt;=%($a2))?1.0:0.0);\n"/>
#                </admst:when>
#                <admst:when test="[name='hypot']">
#                  <admst:text format="%($varType) deriv_hypot_%($functionIndex)_d0 = %($a1)/value_hypot_%($functionIndex);\n"/>
#                </admst:when>
#                <admst:when test="[name='atan2']">
#                  <admst:text format="%($varType) deriv_atan2_%($functionIndex)_d0 = %($a2)/(%($a2)*%($a2) + %($a1)*%($a1));\n"/>
#                </admst:when>
#              </admst:choose>
#            </admst:if>
#            <admst:if test="[arguments[2]/math/dependency!='constant' or ($globalCurrentScope='sensitivity' and exists(arguments[2]/#Pdependent))]">
#              <admst:choose>
#                <admst:when test="[name='pow']">
#                  <admst:text format="%($varType) deriv_pow_%($functionIndex)_d1 = (%($a1) == 0.0)?0.0:(log($a1)*value_pow_%($functionIndex));\n"/>
#                </admst:when>
#                <admst:when test="[name='min']">
#                  <admst:text format="%($varType) deriv_min_%($functionIndex)_d1 = ((%($a1)&lt;=%($a2))?0.0:1.0);\n"/>
#                </admst:when>
#                <admst:when test="[name='max']">
#                  <admst:text format="%($varType) deriv_max_%($functionIndex)_d1 = ((%($a1)&gt;=%($a2))?0.0:1.0);\n"/>
#                </admst:when>
#                <admst:when test="[name='hypot']">
#                  <admst:text format="%($varType) deriv_hypot_%($functionIndex)_d1 = %($a2)/value_hypot_%($functionIndex);\n"/>
#                </admst:when>
#                <admst:when test="[name='atan2']">
#                  <admst:text format="%($varType) deriv_atan2_%($functionIndex)_d1 = -%($a1)/(%($a2)*%($a2) + %($a1)*%($a1));\n"/>
#                </admst:when>
#              </admst:choose>
#            </admst:if>
#          </admst:when>
#          <admst:otherwise>
#            <admst:if test="[class !='analog' and name != '\$simparam' and name != 'floor']">
#              <admst:text format="//function deriv %(name) not implemented yet.\n"/>
#              <admst:warning format="function derivative for %(name) not implemented yet.\n"/>
#            </admst:if>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:for-each>
#    </admst:if>
#  </admst:template>
#  <!--
#   =================================================================-
#   verilog2CXXtype
#     given an admst data tree node, return the C++ datatype
#     corresponding to its type
#    The node passed in is usually a variable
#   =================================================================-
#  -->
#  <admst:template match="verilog2CXXtype">
#    <admst:choose>
#      <admst:when test="[type='integer']">
#        <admst:text format="int"/>
#      </admst:when>
#      <admst:when test="[type='real']">
#        <admst:text format="double"/>
#      </admst:when>
#      <admst:when test="[type='string']">
#        <admst:text format="string"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:fatal format="should not be reached\n"/>
#      </admst:otherwise>
#    </admst:choose>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   textUnit2XyceUnit
#   given an admst data tree element with a "units" attribute,
#   output the corresponding "U_" string
#   =================================================================-
#  -->
#  <admst:template match="textUnit2XyceUnit">
#    <admst:choose>
#      <!-- Simple units -->
#      <admst:when test="[attribute/[name='units']/value = 'm']">
#        <admst:text format="U_METER"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'm^2']">
#        <admst:text format="U_METER2"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'm^-3']">
#        <admst:text format="U_METERM3"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'F']">
#        <admst:text format="U_FARAD"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Ohm']">
#        <admst:text format="U_OHM"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'V']">
#        <admst:text format="U_VOLT"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = '/V' or attribute/[name='units']/value = 'V^-1']">
#        <admst:text format="U_VOLTM1"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'V^-0.5']">
#        <admst:text format="U_VOLTMH"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'A']">
#        <admst:text format="U_AMP"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'S' or attribute/[name='units']/value = '1/Ohm']">
#        <admst:text format="U_OHMM1"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 's']">
#        <admst:text format="U_SECOND"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'K']">
#        <admst:text format="U_DEGK"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'K^-1' or attribute/[name='units']/value = '1/K']">
#        <admst:text format="U_DEGKM1"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'degC']">
#        <admst:text format="U_DEGC"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = '/C' or attribute/[name='units']/value = '1/C' or attribute/[name='units']/value = 'degC^-1']">
#        <admst:text format="U_DEGCM1"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'C']">
#        <admst:text format="U_COULOMB"/>
#      </admst:when>
#      <!-- Complex units -->
#      <admst:when test="[attribute/[name='units']/value = 'V/K']">
#        <admst:text format="U_VKM1"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'm^2/V/s']">
#        <admst:text format="U_M2VM1SM1"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'm/V']">
#        <admst:text format="U_MVM1"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Vm']">
#        <admst:text format="U_VM"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Vm^-1']">
#        <admst:text format="U_VMM1"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'A/V^3' or attribute/[name='units']/value = 'AV^-3' ]">
#        <admst:text format="U_AMPVM3"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Am/V^3' or attribute/[name='units']/value = 'AV^-3m' ]">
#        <admst:text format="U_AMPVM3M"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Am^-1']">
#        <admst:text format="U_AMPMM1"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Am^-2']">
#        <admst:text format="U_AMPMM2"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Am^-3']">
#        <admst:text format="U_AMPMM3"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Ohm m^2']">
#        <admst:text format="U_OHMM2"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Ohm/sq']">
#        <admst:text format="U_OSQM1"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Fm^-1']">
#        <admst:text format="U_FARADMM1"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Fm^-2']">
#        <admst:text format="U_FARADMM2"/>
#      </admst:when>
#
#      <admst:otherwise>
#        <admst:text format="U_UNKNOWN"/>
#      </admst:otherwise>
#    </admst:choose>
#  </admst:template>
#
#    <!--
#   =================================================================-
#   textUnit2LaTeXUnit
#   given an admst data tree element with a "units" attribute,
#   output the corresponding LaTeX string
#   =================================================================-
#  -->
#  <admst:template match="textUnit2LaTeXUnit">
#    <admst:choose>
#      <!-- Simple units -->
#      <admst:when test="[attribute/[name='units']/value = 'm^-3']">
#        <admst:text format="m\$^{-3}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Ohm']">
#        <admst:text format="Ohm"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = '/V' or attribute/[name='units']/value = 'V^-1']">
#        <admst:text format="V\$^{-1}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'V^-0.5']">
#        <admst:text format="V\$^{-0.5}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'S' or attribute/[name='units']/value = '1/Ohm']">
#        <admst:text format="\$\\mathsf{\\Omega}^{-1}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'K^-1' or attribute/[name='units']/value = '1/K']">
#        <admst:text format="K\$^{-1}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = '/C' or attribute/[name='units']/value = '1/C' or attribute/[name='units']/value = 'degC^-1']">
#        <admst:text format="\$^\\circ\$C\$^{-1}\$"/>
#      </admst:when>
#      <!-- Complex units -->
#      <admst:when test="[attribute/[name='units']/value = 'm^2/V/s']">
#        <admst:text format="m\$^{2}\$/(Vs)"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Vm^-1']">
#        <admst:text format="Vm\$^{-1}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'A/V^3' or attribute/[name='units']/value = 'AV^-3' ]">
#        <admst:text format="A/V\$^{3}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'A/V^2' or attribute/[name='units']/value = 'AV^-2' ]">
#        <admst:text format="A/V\$^{2}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Am/V^3' or attribute/[name='units']/value = 'AV^-3m' ]">
#        <admst:text format="Am/V\$^{3}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Am^-1']">
#        <admst:text format="A/m"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Am^-2']">
#        <admst:text format="A/m\$^{2}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Am^-3']">
#        <admst:text format="A/m\$^{3}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Ohm m^2']">
#        <admst:text format="\$\\mathsf{\\Omega}\$ m\$^{2}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Ohm/sq']">
#        <admst:text format="\$\\mathsf{\\Omega}/\\Box\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Fm^-1']">
#        <admst:text format="F/m"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'Fm^-2']">
#        <admst:text format="F/m\$^{2}\$"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'A^2/Hz']">
#        <admst:text format="A\$^{2}\$/Hz"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = 'm^2/(V s)']">
#        <admst:text format="m\$^2\$/(V s)"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = '1/(V m^2)']">
#        <admst:text format="1/(V m\$^2\$)"/>
#      </admst:when>
#      <admst:when test="[attribute/[name='units']/value = '1/(V m^4)']">
#        <admst:text format="1/(V m\$^4\$)"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:text format="%(attribute/[name='units']/value)"/>
#      </admst:otherwise>
#    </admst:choose>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   processTerm
#   given any node, run the associated template over it
#   =================================================================-
#  -->
#  <admst:template match="processTerm" >
#    <admst:apply-templates select="." match="%(adms/datatypename)">
#      <admst:variable name="expression" select="%(returned('returnedExpression')/value)"/>
#      <admst:variable name="expressionDeriv" select="%(returned('returnedExpressionDeriv')/value)"/>
#      <admst:variable name="expressionDeriv2" select="%(returned('returnedExpressionDeriv2')/value)"/>
#      <admst:variable name="expressionDeriv12" select="%(returned('returnedExpressionDeriv12')/value)"/>
#      <admst:variable name="expressionDerivX" select="%(returned('returnedExpressionDerivX')/value)"/>
#    </admst:apply-templates>
#    <admst:return name="returnedExpression" value="$expression"/>
#    <admst:return name="returnedExpressionDeriv" value="$expressionDeriv"/>
#    <admst:return name="returnedExpressionDeriv2" value="$expressionDeriv2"/>
#    <admst:return name="returnedExpressionDeriv12" value="$expressionDeriv12"/>
#    <admst:return name="returnedExpressionDerivX" value="$expressionDerivX"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   printTerm
#   given any node, run the associated template over it and print
#   =================================================================-
#  -->
#  <admst:template match="printTerm" >
#    <admst:apply-templates select="." match="%(adms/datatypename)">
#      <admst:text format="%(returned('returnedExpression')/value)"/>
#    </admst:apply-templates>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   handling of expression
#   expression
#   This template returns the expression passed to it in the select
#   field
#   It processes each element of the tree using a template of the
#   same name as the datatype name.
#
#   To understand what it's doing, be aware that the datatypenames
#   that typically end up in the tree  are things like number,
#   mapply_binary, mapply_unary, expression (implying recursion back
#   into this template), ... (fill in, it would be good for this
#   comment to document all the templates we can call)
#
#   Each of the templates called does little more than return the C++
#   representation of that type of data, and when we return the entire
#   expression will be printed in C++
#   =================================================================-
#  -->
#  <admst:template match="expression">
#    <admst:apply-templates select="tree" match="%(adms/datatypename)" required="yes">
#      <admst:variable name="expression" select="%(returned('returnedExpression')/value)"/>
#      <admst:variable name="expressionDeriv" select="%(returned('returnedExpressionDeriv')/value)"/>
#      <admst:variable name="expressionDeriv2" select="%(returned('returnedExpressionDeriv2')/value)"/>
#      <admst:variable name="expressionDeriv12" select="%(returned('returnedExpressionDeriv12')/value)"/>
#      <admst:variable name="expressionDerivX" select="%(returned('returnedExpressionDerivX')/value)"/>
#    </admst:apply-templates>
#    <admst:return name="returnedExpression" value="$expression"/>
#    <admst:return name="returnedExpressionDeriv" value="$expressionDeriv"/>
#    <admst:return name="returnedExpressionDeriv2" value="$expressionDeriv2"/>
#    <admst:return name="returnedExpressionDeriv12" value="$expressionDeriv12"/>
#    <admst:return name="returnedExpressionDerivX" value="$expressionDerivX"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   number
#   Print out a number, properly accounting for scaling unit suffixes
#   =================================================================-
#  -->
#  <admst:template match="number">
#    <admst:value-of select="value"/>
#    <admst:choose>
#      <admst:when test="[scalingunit='1']"><admst:return name="returnedExpression" value="%s"/></admst:when>
#      <admst:when test="[scalingunit='E']"><admst:return name="returnedExpression" value="(%s*1.0e+18)"/></admst:when>
#      <admst:when test="[scalingunit='P']"><admst:return name="returnedExpression" value="%s*1.0e+15"/></admst:when>
#      <admst:when test="[scalingunit='T']"><admst:return name="returnedExpression" value="%s*1.0e+12"/></admst:when>
#      <admst:when test="[scalingunit='G']"><admst:return name="returnedExpression" value="%s*1.0e+9"/></admst:when>
#      <admst:when test="[scalingunit='M']"><admst:return name="returnedExpression" value="%s*1.0e+6"/></admst:when>
#      <admst:when test="[scalingunit='k']"><admst:return name="returnedExpression" value="%s*1.0e+3"/></admst:when>
#      <admst:when test="[scalingunit='h']"><admst:return name="returnedExpression" value="%s*1.0e+2"/></admst:when>
#      <admst:when test="[scalingunit='D']"><admst:return name="returnedExpression" value="%s*1.0e+1"/></admst:when>
#      <admst:when test="[scalingunit='d']"><admst:return name="returnedExpression" value="%s*1.0e-1"/></admst:when>
#      <admst:when test="[scalingunit='c']"><admst:return name="returnedExpression" value="%s*1.0e-2"/></admst:when>
#      <admst:when test="[scalingunit='m']"><admst:return name="returnedExpression" value="%s*1.0e-3"/></admst:when>
#      <admst:when test="[scalingunit='u']"><admst:return name="returnedExpression" value="%s*1.0e-6"/></admst:when>
#      <admst:when test="[scalingunit='n']"><admst:return name="returnedExpression" value="%s*1.0e-9"/></admst:when>
#      <admst:when test="[scalingunit='A']"><admst:return name="returnedExpression" value="%s*1.0e-10"/></admst:when>
#      <admst:when test="[scalingunit='p']"><admst:return name="returnedExpression" value="%s*1.0e-12"/></admst:when>
#      <admst:when test="[scalingunit='f']"><admst:return name="returnedExpression" value="%s*1.0e-15"/></admst:when>
#      <admst:when test="[scalingunit='a']"><admst:return name="returnedExpression" value="%s*1.0e-18"/></admst:when>
#      <admst:otherwise>
#        <admst:value-of select="scalingunit"/>
#        <admst:fatal format="%s%s: scaling unit not supported\n"/>
#      </admst:otherwise>
#    </admst:choose>
#    <admst:return name="returnedExpressionDeriv" value="0.0"/>
#    <admst:return name="returnedExpressionDeriv2" value="0.0"/>
#    <admst:return name="returnedExpressionDeriv12" value="0.0"/>
#    <admst:return name="returnedExpressionDerivX" value="0.0"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   mapply_unary
#   This template handles unary operators, printing out the result
#   surrounded by parentheses
#   =================================================================-
#  -->
#  <admst:template match="mapply_unary">
#    <admst:if test="[name='plus']"> <admst:variable name="op" select="+"/> </admst:if>
#    <admst:if test="[name='minus']"> <admst:variable name="op" select="-"/> </admst:if>
#    <admst:if test="[name='not']"> <admst:variable name="op" select="!"/> </admst:if>
#    <admst:if test="[name='bw_not']"> <admst:variable name="op" select="~"/> </admst:if>
#    <admst:variable name="expressionDeriv2" select="0.0"/>
#    <admst:variable name="expressionDeriv12" select="0.0"/>
#    <admst:variable name="expressionDerivX" select="0.0"/>
#    <admst:choose>
#      <admst:when test="[arg1/math/value=0.0]">
#        <admst:variable name="expression" select="0.0"/>
#        <admst:variable name="expressionDeriv" select="0.0"/>
#        <admst:variable name="expressionDeriv2" select="0.0"/>
#        <admst:variable name="expressionDeriv12" select="0.0"/>
#        <admst:variable name="expressionDerivX" select="0.0"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:value-of select="arg1/adms/datatypename"/>
#        <admst:apply-templates select="arg1" match="%s" required="yes">
#          <admst:value-of select="returned('returnedExpression')/value"/>
#          <admst:variable name="expression" select="($op%s)"/>
#          <admst:value-of select="returned('returnedExpressionDeriv')/value"/>
#          <admst:variable name="a1Deriv" select="%s"/>
#          <admst:if test="$derivProbe2">
#            <admst:value-of select="returned('returnedExpressionDeriv2')/value"/>
#            <admst:variable name="a1Deriv2" select="%s"/>
#            <admst:value-of select="returned('returnedExpressionDeriv12')/value"/>
#            <admst:variable name="a1Deriv12" select="%s"/>
#          </admst:if>
#          <admst:if test="[$globalCurrentScope='sensitivity' and exists(#Pdependent)]">
#            <admst:value-of  select="returned('returnedExpressionDerivX')/value"/>
#            <admst:variable name="a1DerivX" select="%s"/>
#          </admst:if>
#          <admst:choose>
#            <admst:when test="[$a1Deriv='0.0']">
#              <admst:variable name="expressionDeriv" select="0.0"/>
#            </admst:when>
#            <admst:otherwise>
#              <admst:variable name="expressionDeriv" select="($op$a1Deriv)"/>
#            </admst:otherwise>
#          </admst:choose>
#          <admst:if test="$derivProbe2">
#            <admst:choose>
#              <admst:when test="[$a1Deriv2='0.0']">
#                <admst:variable name="expressionDeriv2" select="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv2" select="($op$a1Deriv2)"/>
#              </admst:otherwise>
#            </admst:choose>
#            <admst:choose>
#              <admst:when test="[$a1Deriv12='0.0']">
#                <admst:variable name="expressionDeriv12" select="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv12" select="($op$a1Deriv12)"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:if>
#          <admst:if test="[$globalCurrentScope='sensitivity' and exists(#Pdependent)]">
#            <admst:choose>
#              <admst:when test="[$a1DerivX='0.0']">
#                <admst:variable name="expressionDerivX" select="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDerivX" select="($op$a1DerivX)"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:if>
#        </admst:apply-templates>
#      </admst:otherwise>
#    </admst:choose>
#    <admst:return name="returnedExpression" value="$expression"/>
#    <admst:return name="returnedExpressionDeriv" value="$expressionDeriv"/>
#    <admst:return name="returnedExpressionDeriv2" value="$expressionDeriv2"/>
#    <admst:return name="returnedExpressionDeriv12" value="$expressionDeriv12"/>
#    <admst:return name="returnedExpressionDerivX" value="$expressionDerivX"/>
#
#  </admst:template>
#
#  <!--
#   =================================================================-
#   mapply_binary
#   This template handles binary operators, printing out the C++
#   version surrounded by parentheses
#   =================================================================-
#  -->
#  <admst:template match="mapply_binary">
#    <admst:apply-templates select="arg1" match="processTerm">
#      <admst:value-of select="returned('returnedExpression')/value"/>
#      <admst:variable name="a1" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDeriv')/value"/>
#      <admst:variable name="a1Deriv" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDeriv2')/value"/>
#      <admst:variable name="a1Deriv2" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDeriv12')/value"/>
#      <admst:variable name="a1Deriv12" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDerivX')/value"/>
#      <admst:variable name="a1DerivX" select="%s"/>
#    </admst:apply-templates>
#    <admst:apply-templates select="arg2" match="processTerm">
#      <admst:value-of select="returned('returnedExpression')/value"/>
#      <admst:variable name="a2" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDeriv')/value"/>
#      <admst:variable name="a2Deriv" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDeriv2')/value"/>
#      <admst:variable name="a2Deriv2" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDeriv12')/value"/>
#      <admst:variable name="a2Deriv12" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDerivX')/value"/>
#      <admst:variable name="a2DerivX" select="%s"/>
#    </admst:apply-templates>
#    <admst:variable name="expressionDeriv2" select="0.0"/>
#    <admst:variable name="expressionDeriv12" select="0.0"/>
#    <admst:variable name="expressionDerivX" select="0.0"/>
#    <admst:choose>
#      <!-- addition -->
#      <admst:when test="[name='addp']">
#        <admst:choose>
#          <admst:when test="[(arg1/math/value=0.0)and(arg2/math/value=0.0)]">
#            <admst:variable name="expression" select="0.0"/>
#            <admst:variable name="expressionDeriv" select="0.0"/>
#            <admst:variable name="expressionDeriv2" select="0.0"/>
#            <admst:variable name="expressionDeriv12" select="0.0"/>
#            <admst:variable name="expressionDerivX" select="0.0"/>
#          </admst:when>
#          <admst:when test="[arg1/math/value=0.0 or $a1='0.0']">
#            <admst:variable name="expression" select="%($a2)"/>
#            <admst:choose>
#              <admst:when test="[$a2Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv" select="%($a2Deriv)"/>
#              </admst:otherwise>
#            </admst:choose>
#            <admst:if test="$derivProbe2">
#              <admst:choose>
#                <admst:when test="[$a2Deriv2 = '0.0']">
#                  <admst:variable name="expressionDeriv2" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv2" select="%($a2Deriv2)"/>
#                </admst:otherwise>
#              </admst:choose>
#              <admst:choose>
#                <admst:when test="[$a2Deriv12 = '0.0']">
#                  <admst:variable name="expressionDeriv12" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv12" select="%($a2Deriv12)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#            <admst:if test="[$globalCurrentScope='sensitivity' and (exists(arg1/#Pdependent)  or exists(arg2/#Pdependent))]">
#              <admst:choose>
#                <admst:when test="[$a2DerivX = '0.0']">
#                  <admst:variable name="expressionDerivX" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDerivX" select="%($a2DerivX)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#          </admst:when>
#          <admst:when test="[arg2/math/value=0.0 or $a2='0.0']">
#            <admst:variable name="expression" select="%($a1)"/>
#            <admst:choose>
#              <admst:when test="[$a1Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv" select="%($a1Deriv)"/>
#              </admst:otherwise>
#            </admst:choose>
#            <admst:if test="$derivProbe2">
#              <admst:choose>
#                <admst:when test="[$a1Deriv2 = '0.0']">
#                  <admst:variable name="expressionDeriv2" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv2" select="%($a1Deriv2)"/>
#                </admst:otherwise>
#              </admst:choose>
#              <admst:choose>
#                <admst:when test="[$a1Deriv12 = '0.0']">
#                  <admst:variable name="expressionDeriv12" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv12" select="%($a1Deriv12)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#            <admst:if test="[$globalCurrentScope='sensitivity' and (exists(arg1/#Pdependent) or exists(arg2/#Pdependent))]">
#              <admst:choose>
#                <admst:when test="[$a1DerivX = '0.0']">
#                  <admst:variable name="expressionDerivX" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDerivX" select="%($a1DerivX)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#          </admst:when>
#          <admst:otherwise>
#            <admst:variable name="expression" select="($a1+$a2)"/>
#            <admst:choose>
#              <admst:when test="[$a1Deriv = '0.0' and $a2Deriv ='0.0']">
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="$a2Deriv"/>
#              </admst:when>
#              <admst:when test="[$a2Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="$a1Deriv"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv" select="($a1Deriv+$a2Deriv)"/>
#              </admst:otherwise>
#            </admst:choose>
#            <admst:if test="$derivProbe2">
#              <admst:choose>
#                <admst:when test="[$a1Deriv2 = '0.0' and $a2Deriv2 ='0.0']">
#                  <admst:variable name="expressionDeriv2" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '0.0']">
#                  <admst:variable name="expressionDeriv2" select="$a2Deriv2"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv2 = '0.0']">
#                  <admst:variable name="expressionDeriv2" select="$a1Deriv2"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv2" select="($a1Deriv2+$a2Deriv2)"/>
#                </admst:otherwise>
#              </admst:choose>
#              <admst:choose>
#                <admst:when test="[$a1Deriv12 = '0.0' and $a2Deriv12 ='0.0']">
#                  <admst:variable name="expressionDeriv12" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv12 = '0.0']">
#                  <admst:variable name="expressionDeriv12" select="$a2Deriv12"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv12 = '0.0']">
#                  <admst:variable name="expressionDeriv12" select="$a1Deriv12"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv12" select="($a1Deriv12+$a2Deriv12)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#            <admst:if test="[$globalCurrentScope='sensitivity' and (exists(arg1/#Pdependent) or exists(arg2/#Pdependent)) ]">
#              <admst:choose>
#                <admst:when test="[$a1DerivX = '0.0' and $a2DerivX ='0.0']">
#                  <admst:variable name="expressionDerivX" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a1DerivX = '0.0']">
#                  <admst:variable name="expressionDerivX" select="$a2DerivX"/>
#                </admst:when>
#                <admst:when test="[$a2DerivX = '0.0']">
#                  <admst:variable name="expressionDerivX" select="$a1DerivX"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDerivX" select="($a1DerivX+$a2DerivX)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <!-- subtraction -->
#      <admst:when test="[name='addm']">
#        <admst:choose>
#          <admst:when test="[(arg1/math/value=0.0)and(arg2/math/value=0.0) or ($a1='0.0' and $a2='0.0')]">
#            <admst:variable name="expression" select="0.0"/>
#            <admst:variable name="expressionDeriv" select="0.0"/>
#            <admst:variable name="expressionDeriv2" select="0.0"/>
#            <admst:variable name="expressionDeriv12" select="0.0"/>
#            <admst:variable name="expressionDerivX" select="0.0"/>
#          </admst:when>
#          <admst:when test="[arg1/math/value=0.0 or $a1='0.0']">
#            <admst:variable name="expression" select="(-%($a2))"/>
#            <admst:choose>
#              <admst:when test="[$a2Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv" select="(-%($a2Deriv))"/>
#              </admst:otherwise>
#            </admst:choose>
#            <admst:if test="$derivProbe2">
#              <admst:choose>
#                <admst:when test="[$a2Deriv2 = '0.0']">
#                  <admst:variable name="expressionDeriv2" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv2" select="(-%($a2Deriv2))"/>
#                </admst:otherwise>
#              </admst:choose>
#              <admst:choose>
#                <admst:when test="[$a2Deriv12 = '0.0']">
#                  <admst:variable name="expressionDeriv12" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv12" select="(-%($a2Deriv12))"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#            <admst:if test="[$globalCurrentScope='sensitivity' and (exists(arg1/#Pdependent) or exists(arg2/#Pdependent)) ]">
#              <admst:choose>
#                <admst:when test="[$a2DerivX = '0.0']">
#                  <admst:variable name="expressionDerivX" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDerivX" select="(-%($a2DerivX))"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#          </admst:when>
#          <admst:when test="[arg2/math/value=0.0 or $a2='0.0']">
#            <admst:variable name="expression" select="(%($a1))"/>
#            <admst:choose>
#              <admst:when test="[$a1Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv" select="%($a1Deriv)"/>
#              </admst:otherwise>
#            </admst:choose>
#            <admst:if test="$derivProbe2">
#              <admst:choose>
#                <admst:when test="[$a1Deriv2 = '0.0']">
#                  <admst:variable name="expressionDeriv2" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv2" select="%($a1Deriv2)"/>
#                </admst:otherwise>
#              </admst:choose>
#              <admst:choose>
#                <admst:when test="[$a1Deriv12 = '0.0']">
#                  <admst:variable name="expressionDeriv12" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv12" select="%($a1Deriv12)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#            <admst:if test="[$globalCurrentScope='sensitivity' and (exists(arg1/#Pdependent) or exists(arg2/#Pdependent)) ]">
#              <admst:choose>
#                <admst:when test="[$a1DerivX = '0.0']">
#                  <admst:variable name="expressionDerivX" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDerivX" select="%($a1DerivX)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#          </admst:when>
#          <admst:otherwise>
#            <admst:variable name="expression" select="($a1-$a2)"/>
#            <admst:choose>
#              <admst:when test="[$a1Deriv = '0.0' and $a2Deriv ='0.0']">
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="(-$a2Deriv)"/>
#              </admst:when>
#              <admst:when test="[$a2Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="$a1Deriv"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv" select="($a1Deriv-$a2Deriv)"/>
#              </admst:otherwise>
#            </admst:choose>
#            <admst:if test="$derivProbe2">
#              <admst:choose>
#                <admst:when test="[$a1Deriv2 = '0.0' and $a2Deriv2 ='0.0']">
#                  <admst:variable name="expressionDeriv2" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '0.0']">
#                  <admst:variable name="expressionDeriv2" select="(-$a2Deriv2)"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv2 = '0.0']">
#                  <admst:variable name="expressionDeriv2" select="$a1Deriv2"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv2" select="($a1Deriv2-$a2Deriv2)"/>
#                </admst:otherwise>
#              </admst:choose>
#              <admst:choose>
#                <admst:when test="[$a1Deriv12 = '0.0' and $a2Deriv12 ='0.0']">
#                  <admst:variable name="expressionDeriv12" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv12 = '0.0']">
#                  <admst:variable name="expressionDeriv12" select="(-$a2Deriv12)"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv12 = '0.0']">
#                  <admst:variable name="expressionDeriv12" select="$a1Deriv12"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv12" select="($a1Deriv12-$a2Deriv12)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#            <admst:if test="[$globalCurrentScope='sensitivity' and (exists(arg1/#Pdependent) or exists(arg2/#Pdependent)) ]">
#              <admst:choose>
#                <admst:when test="[$a1DerivX = '0.0' and $a2DerivX ='0.0']">
#                  <admst:variable name="expressionDerivX" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a1DerivX = '0.0']">
#                  <admst:variable name="expressionDerivX" select="(-$a2DerivX)"/>
#                </admst:when>
#                <admst:when test="[$a2DerivX = '0.0']">
#                  <admst:variable name="expressionDerivX" select="$a1DerivX"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDerivX" select="($a1DerivX-$a2DerivX)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[name='multtime']">
#        <admst:choose>
#          <admst:when test="[(arg1/math/value=0.0)or(arg2/math/value=0.0) or $a1='0.0' or $a2='0.0']">
#            <admst:variable name="expression" select="0.0"/>
#            <admst:variable name="expressionDeriv" select="0.0"/>
#            <admst:variable name="expressionDeriv2" select="0.0"/>
#            <admst:variable name="expressionDeriv12" select="0.0"/>
#            <admst:variable name="expressionDerivX" select="0.0"/>
#          </admst:when>
#          <admst:when test="[((arg1/math/value=1.0) and (arg2/math/value=1.0)) or ($a1='1.0' and $a2='1.0')]">
#            <admst:variable name="expression" select="1.0"/>
#            <admst:variable name="expressionDeriv" select="0.0"/>
#            <admst:variable name="expressionDeriv2" select="0.0"/>
#            <admst:variable name="expressionDeriv12" select="0.0"/>
#            <admst:variable name="expressionDerivX" select="0.0"/>
#          </admst:when>
#          <admst:otherwise>
#            <admst:variable name="expression" select="($a1*$a2)"/>
#            <admst:choose>
#              <admst:when test="[$a1Deriv = '0.0' and $a2Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '0.0' and $a2Deriv = '1.0']">
#                <admst:variable name="expressionDeriv" select="$a1"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '1.0' and $a2Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="$a2"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '1.0' and $a2Deriv = '1.0']">
#                <admst:variable name="expressionDeriv" select="($a1+$a2)"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="$a1*$a2Deriv"/>
#              </admst:when>
#              <admst:when test="[$a2Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="$a1Deriv*$a2"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '1.0']">
#                <admst:variable name="expressionDeriv" select="($a1*$a2Deriv+$a2)"/>
#              </admst:when>
#              <admst:when test="[$a2Deriv = '1.0']">
#                <admst:variable name="expressionDeriv" select="($a1+$a2*$a1Deriv)"/>
#              </admst:when>
#              <admst:when test="[$a1 = '1.0']">
#                <admst:variable name="expressionDeriv" select="$a2Deriv"/>
#              </admst:when>
#              <admst:when test="[$a2 = '1.0']">
#                <admst:variable name="expressionDeriv" select="$a1Deriv"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv" select="($a1*$a2Deriv+$a1Deriv*$a2)"/>
#              </admst:otherwise>
#            </admst:choose>
#            <!-- now do derivative with respect to second probe, if it exists -->
#            <!-- and second derivs w.r.t. both probes -->
#            <admst:if test="$derivProbe2">
#              <admst:choose>
#                <admst:when test="[$a1Deriv2 = '0.0' and $a2Deriv2 = '0.0']">
#                  <admst:variable name="expressionDeriv2" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '0.0' and $a2Deriv2 = '1.0']">
#                  <admst:variable name="expressionDeriv2" select="$a1"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '1.0' and $a2Deriv2 = '0.0']">
#                  <admst:variable name="expressionDeriv2" select="$a2"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '1.0' and $a2Deriv2 = '1.0']">
#                  <admst:variable name="expressionDeriv2" select="($a1+$a2)"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '0.0']">
#                  <admst:variable name="expressionDeriv2" select="$a1*$a2Deriv2"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv2 = '0.0']">
#                  <admst:variable name="expressionDeriv2" select="$a1Deriv2*$a2"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '1.0']">
#                  <admst:variable name="expressionDeriv2" select="($a1*$a2Deriv2+$a2)"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv2 = '1.0']">
#                  <admst:variable name="expressionDeriv2" select="($a1+$a2*$a1Deriv2)"/>
#                </admst:when>
#                <admst:when test="[$a1 = '1.0']">
#                  <admst:variable name="expressionDeriv2" select="$a2Deriv2"/>
#                </admst:when>
#                <admst:when test="[$a2 = '1.0']">
#                  <admst:variable name="expressionDeriv2" select="($a1Deriv2)"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv2" select="($a1*$a2Deriv2+$a1Deriv2*$a2)"/>
#                </admst:otherwise>
#              </admst:choose>
#              <!-- Now we must do derivative w.r.t. 1 and 2, and all the special cases -->
#              <!-- first term is d2a1/dp2dp1*a2 -->
#              <admst:variable name="term1" select=""/>
#              <admst:variable name="term2" select=""/>
#              <admst:variable name="term3" select=""/>
#              <admst:variable name="term4" select=""/>
#              <admst:choose>
#                <admst:when test="[$a1Deriv12 = '0.0' or $a2 = '0.0']">
#                  <admst:variable name="term1" select=""/>
#                </admst:when>
#                <admst:when test="[$a1Deriv12 = '1.0' and $a2 = '1.0']">
#                  <admst:variable name="term1" select="1.0"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv12 = '1.0']">
#                  <admst:variable name="term1" select="$a2"/>
#                </admst:when>
#                <admst:when test="[$a2 = '1.0']">
#                  <admst:variable name="term1" select="$a1Deriv12"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="term1" select="$a1Deriv12*$a2"/>
#                </admst:otherwise>
#              </admst:choose>
#              <!-- second term, da1/dp1*da2/dp2 -->
#              <admst:choose>
#                <admst:when test="[$a1Deriv = '0.0' or $a2Deriv2 = '0.0']">
#                  <admst:variable name="term2" select=""/>
#                </admst:when>
#                <admst:when test="[$a1Deriv = '1.0' and $a2Deriv2 ='1.0']">
#                  <admst:variable name="term2" select="1.0"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv = '1.0']">
#                  <admst:variable name="term2" select="$a2Deriv2"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv2 = '1.0']">
#                  <admst:variable name="term2" select="$a1Deriv"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="term2" select="$a1Deriv*$a2Deriv2"/>
#                </admst:otherwise>
#              </admst:choose>
#              <!-- third term, da1/dp2*da2/dp1 -->
#              <admst:choose>
#                <admst:when test="[$a1Deriv2 = '0.0' or $a2Deriv = '0.0']">
#                  <admst:variable name="term3" select=""/>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '1.0' and $a2Deriv ='1.0']">
#                  <admst:variable name="term3" select="1.0"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '1.0']">
#                  <admst:variable name="term3" select="$a2Deriv"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv = '1.0']">
#                  <admst:variable name="term3" select="$a1Deriv2"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="term3" select="$a1Deriv2*$a2Deriv"/>
#                </admst:otherwise>
#              </admst:choose>
#              <!-- final term, a1*d2a2/dp2dp1 -->
#              <admst:choose>
#                <admst:when test="[$a2Deriv12 = '0.0' or $a1 = '0.0']">
#                  <admst:variable name="term4" select=""/>
#                </admst:when>
#                <admst:when test="[$a2Deriv12 = '1.0' and $a1 = '1.0']">
#                  <admst:variable name="term4" select="1.0"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv12 = '1.0']">
#                  <admst:variable name="term4" select="$a1"/>
#                </admst:when>
#                <admst:when test="[$a1 = '1.0']">
#                  <admst:variable name="term4" select="$a2Deriv12"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="term4" select="$a1*$a2Deriv12"/>
#                </admst:otherwise>
#              </admst:choose>
#              <!-- now assemble the smallest possible expression we can make of this -->
#              <admst:variable name="expressionDeriv12" select="$term1"/>
#              <admst:if test="[not($expressionDeriv12='') and not($term2='')]">
#                <admst:variable name="expressionDeriv12" select="$expressionDeriv12+"/>
#              </admst:if>
#              <admst:variable name="expressionDeriv12" select="$expressionDeriv12$term2"/>
#              <admst:if test="[not($expressionDeriv12='') and not($term3='')]">
#                <admst:variable name="expressionDeriv12" select="$expressionDeriv12+"/>
#              </admst:if>
#              <admst:variable name="expressionDeriv12" select="$expressionDeriv12$term3"/>
#              <admst:if test="[not($expressionDeriv12='') and not($term4='')]">
#                <admst:variable name="expressionDeriv12" select="$expressionDeriv12+"/>
#              </admst:if>
#              <admst:variable name="expressionDeriv12" select="$expressionDeriv12$term4"/>
#              <admst:choose>
#                <admst:when test="[$expressionDeriv12='']">
#                  <admst:variable name="expressionDeriv12" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv12" select="($expressionDeriv12)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#            <!-- now sensitivity deriv if needed -->
#            <admst:if test="[$globalCurrentScope='sensitivity' and (exists(arg1/#Pdependent) or exists(arg2/#Pdependent)) ]">
#              <admst:choose>
#                <admst:when test="[$a1DerivX = '0.0' and $a2DerivX = '0.0']">
#                  <admst:variable name="expressionDerivX" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a1DerivX = '0.0' and $a2DerivX = '1.0']">
#                  <admst:variable name="expressionDerivX" select="$a1"/>
#                </admst:when>
#                <admst:when test="[$a1DerivX = '1.0' and $a2DerivX = '0.0']">
#                  <admst:variable name="expressionDerivX" select="$a2"/>
#                </admst:when>
#                <admst:when test="[$a1DerivX = '1.0' and $a2DerivX = '1.0']">
#                  <admst:variable name="expressionDerivX" select="($a1+$a2)"/>
#                </admst:when>
#                <admst:when test="[$a1DerivX = '0.0']">
#                  <admst:variable name="expressionDerivX" select="$a1*$a2DerivX"/>
#                </admst:when>
#                <admst:when test="[$a2DerivX = '0.0']">
#                  <admst:variable name="expressionDerivX" select="$a1DerivX*$a2"/>
#                </admst:when>
#                <admst:when test="[$a1DerivX = '1.0']">
#                  <admst:variable name="expressionDerivX" select="($a1*$a2DerivX+$a2)"/>
#                </admst:when>
#                <admst:when test="[$a2DerivX = '1.0']">
#                  <admst:variable name="expressionDerivX" select="($a1+$a2*$a1DerivX)"/>
#                </admst:when>
#                <admst:when test="[$a1 = '1.0']">
#                  <admst:variable name="expressionDerivX" select="$a2DerivX"/>
#                </admst:when>
#                <admst:when test="[$a2 = '1.0']">
#                  <admst:variable name="expressionDerivX" select="$a1DerivX"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDerivX" select="($a1*$a2DerivX+$a1DerivX*$a2)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[name='multdiv']">
#        <admst:variable name="term1" select=""/>
#        <admst:variable name="term2" select=""/>
#        <admst:variable name="term2a" select=""/>
#        <admst:variable name="term2b" select=""/>
#        <admst:variable name="term2c" select=""/>
#        <admst:variable name="term3" select=""/>
#        <admst:choose>
#          <admst:when test="[arg1/math/value=0.0 or $a1='0.0']">
#            <admst:variable name="expression" select="0.0"/>
#            <admst:variable name="expressionDeriv" select="0.0"/>
#            <admst:variable name="expressionDeriv2" select="0.0"/>
#            <admst:variable name="expressionDeriv12" select="0.0"/>
#            <admst:variable name="expressionDerivX" select="0.0"/>
#          </admst:when>
#          <admst:when test="[((arg1/math/value=1.0)and(arg2/math/value=1.0)) or ($a1='1.0' and $a2='1.0')]">
#            <admst:variable name="expression" select="1.0"/>
#            <admst:variable name="expressionDeriv" select="0.0"/>
#            <admst:variable name="expressionDeriv2" select="0.0"/>
#            <admst:variable name="expressionDeriv12" select="0.0"/>
#            <admst:variable name="expressionDerivX" select="0.0"/>
#          </admst:when>
#          <admst:when test="[$a2='1.0']">
#            <admst:variable name="expression" select="$a1"/>
#            <admst:variable name="expressionDeriv" select="$a1Deriv"/>
#            <admst:variable name="expressionDeriv2" select="$a1Deriv2"/>
#            <admst:variable name="expressionDeriv12" select="$a1Deriv12"/>
#            <admst:variable name="expressionDerivX" select="$a1DerivX"/>
#          </admst:when>
#          <admst:otherwise>
#            <admst:variable name="expression" select="($a1/$a2)"/>
#            <admst:choose>
#              <admst:when test="[$a1Deriv='0.0' and $a2Deriv='0.0']">
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:when>
#              <admst:when test="[$a1 = '1.0']">
#                <admst:choose>
#                  <admst:when test="[$a2Deriv = '1.0']">
#                    <admst:variable name="expressionDeriv" select="(-1.0/$a2/$a2)"/>
#                  </admst:when>
#                  <admst:otherwise>
#                    <admst:variable name="expressionDeriv" select="(-$a2Deriv/$a2/$a2)"/>
#                  </admst:otherwise>
#                </admst:choose>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '0.0']">
#                <admst:choose>
#                  <admst:when test="[$a2Deriv = '1.0']">
#                    <admst:variable name="expressionDeriv" select="(-$a1/$a2/$a2)"/>
#                  </admst:when>
#                  <admst:otherwise>
#                    <admst:variable name="expressionDeriv" select="(-$a1*$a2Deriv/$a2/$a2)"/>
#                  </admst:otherwise>
#                </admst:choose>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '1.0']">
#                <admst:choose>
#                  <admst:when test="[$a2Deriv = '0.0']">
#                    <admst:variable name="expressionDeriv" select="(1.0/$a2)"/>
#                  </admst:when>
#                  <admst:when test="[$a2Deriv = '1.0']">
#                    <admst:variable name="expressionDeriv" select="(($a2-$a1)/$a2/$a2)"/>
#                  </admst:when>
#                  <admst:otherwise>
#                    <admst:variable name="expressionDeriv" select="(($a2-($a1*$a2Deriv))/$a2/$a2)"/>
#                  </admst:otherwise>
#                </admst:choose>
#              </admst:when>
#              <admst:otherwise>
#                <admst:choose>
#                  <admst:when test="[$a2 = '1.0']">
#                    <admst:variable name="expressionDeriv" select="$a1Deriv"/>
#                  </admst:when>
#                  <admst:when test="[$a2Deriv = '0.0']">
#                    <admst:variable name="expressionDeriv" select="($a1Deriv/$a2)"/>
#                  </admst:when>
#                  <admst:when test="[$a2Deriv = '1.0']">
#                    <admst:variable name="expressionDeriv" select="(($a2*$a1Deriv-$a1)/$a2/$a2)"/>
#                  </admst:when>
#                  <admst:otherwise>
#                    <admst:variable name="expressionDeriv" select="(($a2*$a1Deriv-$a1*$a2Deriv)/$a2/$a2)"/>
#                  </admst:otherwise>
#                </admst:choose>
#              </admst:otherwise>
#            </admst:choose>
#            <!-- derivative with respect to second probe if there is one -->
#            <admst:if test="$derivProbe2">
#              <admst:choose>
#                <admst:when test="[$a1Deriv2='0.0' and $a2Deriv2='0.0']">
#                  <admst:variable name="expressionDeriv2" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a1 = '1.0']">
#                  <admst:choose>
#                    <admst:when test="[$a2Deriv2 = '1.0']">
#                      <admst:variable name="expressionDeriv2" select="(-1.0/$a2/$a2)"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="expressionDeriv2" select="(-$a2Deriv2/$a2/$a2)"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '0.0']">
#                  <admst:choose>
#                    <admst:when test="[$a2Deriv2 = '1.0']">
#                      <admst:variable name="expressionDeriv2" select="(-$a1/$a2/$a2)"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="expressionDeriv2" select="(-$a1*$a2Deriv2/$a2/$a2)"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '1.0']">
#                  <admst:choose>
#                    <admst:when test="[$a2Deriv2 = '0.0']">
#                      <admst:variable name="expressionDeriv2" select="(1.0/$a2)"/>
#                    </admst:when>
#                    <admst:when test="[$a2Deriv2 = '1.0']">
#                      <admst:variable name="expressionDeriv2" select="(($a2-$a1)/$a2/$a2)"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="expressionDeriv2" select="(($a2-($a1*$a2Deriv2))/$a2/$a2)"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:choose>
#                    <admst:when test="[$a2 = '1.0']">
#                      <admst:variable name="expressionDeriv2" select="$a1Deriv2"/>
#                    </admst:when>
#                    <admst:when test="[$a2Deriv2 = '0.0']">
#                      <admst:variable name="expressionDeriv2" select="($a1Deriv2/$a2)"/>
#                    </admst:when>
#                    <admst:when test="[$a2Deriv2 = '1.0']">
#                      <admst:variable name="expressionDeriv2" select="(($a2*$a1Deriv2-$a1)/$a2/$a2)"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="expressionDeriv2" select="(($a2*$a1Deriv2-$a1*$a2Deriv2)/$a2/$a2)"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:otherwise>
#              </admst:choose>
#              <!-- now second derivatives... yuck -->
#              <!-- three big terms, second term has three sub-terms -->
#              <!-- First term is just $a1Deriv12/$a2 -->
#              <admst:choose>
#                <admst:when test="[$a1Deriv12 = '0.0' ]">
#                  <admst:variable name="term1" select=""/>
#                </admst:when>
#                <admst:when test="[$a1Deriv12 = '1.0' ]">
#                  <admst:variable name="term1" select="1.0/$a2"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="term1" select="$a1Deriv12/$a2"/>
#                </admst:otherwise>
#              </admst:choose>
#              <!-- term2 has three terms in numerator: a1Deriv*a2Deriv2+a1Deriv2*a2Deriv+a1*a2Deriv12 and denominator is $a2*$a2 -->
#              <!-- term2 is subtracted from term1 -->
#              <admst:choose>
#                <admst:when test="[$a1Deriv = '0.0' or $a2Deriv2 = '0.0']">
#                  <admst:variable name="term2a" select=""/>
#                </admst:when>
#                <admst:when test="[$a1Deriv = '1.0' and $a2Deriv2 = '1.0']">
#                  <admst:variable name="term2a" select="1.0"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv = '1.0']">
#                  <admst:variable name="term2a" select="$a2Deriv2"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv2 = '1.0']">
#                  <admst:variable name="term2a" select="$a1Deriv"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="term2a" select="$a1Deriv*$a2Deriv2"/>
#                </admst:otherwise>
#              </admst:choose>
#              <admst:choose>
#                <admst:when test="[$a1Deriv2 = '0.0' or $a2Deriv = '0.0']">
#                  <admst:variable name="term2b" select=""/>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '1.0' and $a2Deriv = '1.0']">
#                  <admst:variable name="term2b" select="1.0"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv2 = '1.0']">
#                  <admst:variable name="term2b" select="$a2Deriv"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv = '1.0']">
#                  <admst:variable name="term2b" select="$a1Deriv2"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="term2b" select="$a1Deriv2*$a2Deriv"/>
#                </admst:otherwise>
#              </admst:choose>
#              <admst:choose>
#                <admst:when test="[$a1 = '0.0' or $a2Deriv12 = '0.0']">
#                  <admst:variable name="term2c" select=""/>
#                </admst:when>
#                <admst:when test="[$a1 = '1.0' and $a2Deriv12 = '1.0']">
#                  <admst:variable name="term2c" select="1.0"/>
#                </admst:when>
#                <admst:when test="[$a1 = '1.0']">
#                  <admst:variable name="term2c" select="$a2Deriv12"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv12 = '1.0']">
#                  <admst:variable name="term2c" select="$a1"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="term2c" select="$a1*$a2Deriv12"/>
#                </admst:otherwise>
#              </admst:choose>
#              <admst:variable name="term2" select="$term2a"/>
#              <admst:if test="[not($term2='') and not($term2b='')]">
#                <admst:variable name="term2" select="$term2+"/>
#              </admst:if>
#              <admst:variable name="term2" select="$term2$term2b"/>
#              <admst:if test="[not($term2='') and not($term2c='')]">
#                <admst:variable name="term2" select="$term2+"/>
#              </admst:if>
#              <admst:variable name="term2" select="$term2$term2c"/>
#              <admst:if test="[not($term2='')]">
#                <admst:variable name="term2" select="-($term2/$a2/$a2)"/>
#              </admst:if>
#              <!-- term3 is just 2*a1*a2Deriv*a2Deriv2/a2/a2/a2 -->
#              <admst:choose>
#                <admst:when test="[$a1 = '0.0' or $a2Deriv='0.0' or $a2Deriv2='0.0']">
#                  <admst:variable name="term3" select=""/>
#                </admst:when>
#                <admst:when test="[$a1 = '1.0' and $a2Deriv='1.0' and $a2Deriv2='1.0']">
#                  <admst:variable name="term3" select="2.0/$a2/$a2/$a2"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:choose>
#                    <admst:when test="[$a1 = '1.0' and $a2Deriv='1.0']">
#                      <admst:variable name="factor1" select="1.0"/>
#                    </admst:when>
#                    <admst:when test="[$a1 = '1.0']">
#                      <admst:variable name="factor1" select="$a2Deriv"/>
#                    </admst:when>
#                    <admst:when test="[$a2Deriv='1.0']">
#                      <admst:variable name="factor1" select="$a1"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="factor1" select="$a1*$a2Deriv"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                  <admst:choose>
#                    <admst:when test="[$factor1 = '1.0']">
#                      <admst:variable name="term3" select="2*$a2Deriv2/$a2/$a2/$a2"/>
#                    </admst:when>
#                    <admst:when test="[$a2Deriv2 = '1.0']">
#                      <admst:variable name="term3" select="2*$factor1/$a2/$a2/$a2"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="term3" select="2*$factor1*$a2Deriv2/$a2/$a2/$a2"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:otherwise>
#              </admst:choose>
#              <admst:variable name="expressionDeriv12" select="$term1"/>
#              <admst:if test="[not($expressionDeriv12='') and not($term2='')]">
#                <admst:variable name="expressionDeriv12" select="$expressionDeriv12+"/>
#              </admst:if>
#              <admst:variable name="expressionDeriv12" select="$expressionDeriv12$term2"/>
#              <admst:if test="[not($expressionDeriv12='') and not($term3='')]">
#                <admst:variable name="expressionDeriv12" select="$expressionDeriv12+"/>
#              </admst:if>
#              <admst:variable name="expressionDeriv12" select="$expressionDeriv12$term3"/>
#              <admst:choose>
#                <admst:when test="[$expressionDeriv12='']">
#                  <admst:variable name="expressionDeriv12" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv12" select="($expressionDeriv12)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#            <!-- now sensitivity deriv if needed -->
#            <admst:if test="[$globalCurrentScope='sensitivity' and (exists(arg1/#Pdependent) or exists(arg2/#Pdependent)) ]">
#              <admst:choose>
#                <admst:when test="[$a1DerivX='0.0' and $a2DerivX='0.0']">
#                  <admst:variable name="expressionDerivX" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a1 = '1.0']">
#                  <admst:choose>
#                    <admst:when test="[$a2DerivX = '1.0']">
#                      <admst:variable name="expressionDerivX" select="(-1.0/$a2/$a2)"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="expressionDerivX" select="(-$a2DerivX/$a2/$a2)"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:when>
#                <admst:when test="[$a1DerivX = '0.0']">
#                  <admst:choose>
#                    <admst:when test="[$a2DerivX = '1.0']">
#                      <admst:variable name="expressionDerivX" select="(-$a1/$a2/$a2)"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="expressionDerivX" select="(-$a1*$a2DerivX/$a2/$a2)"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:when>
#                <admst:when test="[$a1DerivX = '1.0']">
#                  <admst:choose>
#                    <admst:when test="[$a2DerivX = '0.0']">
#                      <admst:variable name="expressionDerivX" select="(1.0/$a2)"/>
#                    </admst:when>
#                    <admst:when test="[$a2DerivX = '1.0']">
#                      <admst:variable name="expressionDerivX" select="(($a2-$a1)/$a2/$a2)"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="expressionDerivX" select="(($a2-($a1*$a2DerivX))/$a2/$a2)"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:choose>
#                    <admst:when test="[$a2 = '1.0']">
#                      <admst:variable name="expressionDerivX" select="$a1DerivX"/>
#                    </admst:when>
#                    <admst:when test="[$a2DerivX = '0.0']">
#                      <admst:variable name="expressionDerivX" select="($a1DerivX/$a2)"/>
#                    </admst:when>
#                    <admst:when test="[$a2DerivX = '1.0']">
#                      <admst:variable name="expressionDerivX" select="(($a2*$a1DerivX-$a1)/$a2/$a2)"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="expressionDerivX" select="(($a2*$a1DerivX-$a1*$a2DerivX)/$a2/$a2)"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <!-- We are assuming that no other binary ops have meaningful derivatives.  Not exactly
#           a safe assumption, but all the cool kids are doing it. -->
#      <admst:otherwise>
#        <admst:variable name="expression" select="($a1%(bname(.)/[name='bname']/value)$a2)"/>
#        <admst:variable name="expressionDeriv" select="0.0"/>
#        <admst:variable name="expressionDeriv2" select="0.0"/>
#        <admst:variable name="expressionDeriv12" select="0.0"/>
#        <admst:variable name="expressionDerivX" select="0.0"/>
#      </admst:otherwise>
#    </admst:choose>
#    <admst:return name="returnedExpression" value="$expression"/>
#    <admst:return name="returnedExpressionDeriv" value="$expressionDeriv"/>
#    <admst:return name="returnedExpressionDeriv2" value="$expressionDeriv2"/>
#    <admst:return name="returnedExpressionDeriv12" value="$expressionDeriv12"/>
#    <admst:return name="returnedExpressionDerivX" value="$expressionDerivX"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   mapply_ternary
#   Given a ternary operator (cond)?yes:no
#   format for C++
#   =================================================================-
#  -->
#  <admst:template match="mapply_ternary">
#    <admst:apply-templates select="arg1" match="processTerm">
#      <admst:value-of select="returned('returnedExpression')/value"/>
#      <admst:variable name="a1" select="%s"/>
#    </admst:apply-templates>
#    <admst:if test="[$globalCurrentScope='sensitivity']">
#      <admst:apply-templates select="arg2" match="recursiveDetectParameterDependence">
#        <admst:variable name="arg2Pdep" value="%(returned('isDependent')/value)"/>
#      </admst:apply-templates>
#      <admst:apply-templates select="arg3" match="recursiveDetectParameterDependence">
#        <admst:variable name="arg3Pdep" value="%(returned('isDependent')/value)"/>
#      </admst:apply-templates>
#    </admst:if>
#    <admst:apply-templates select="arg2" match="processTerm">
#      <admst:value-of select="returned('returnedExpression')/value"/>
#      <admst:variable name="a2" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDeriv')/value"/>
#      <admst:variable name="a2Deriv" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDeriv2')/value"/>
#      <admst:variable name="a2Deriv2" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDeriv12')/value"/>
#      <admst:variable name="a2Deriv12" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDerivX')/value"/>
#      <admst:variable name="a2DerivX" select="%s"/>
#    </admst:apply-templates>
#    <admst:apply-templates select="arg3" match="processTerm">
#      <admst:value-of select="returned('returnedExpression')/value"/>
#      <admst:variable name="a3" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDeriv')/value"/>
#      <admst:variable name="a3Deriv" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDeriv2')/value"/>
#      <admst:variable name="a3Deriv2" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDeriv12')/value"/>
#      <admst:variable name="a3Deriv12" select="%s"/>
#      <admst:value-of select="returned('returnedExpressionDerivX')/value"/>
#      <admst:variable name="a3DerivX" select="%s"/>
#    </admst:apply-templates>
#    <admst:variable name="expressionDeriv2" select="0.0"/>
#    <admst:variable name="expressionDeriv12" select="0.0"/>
#    <admst:variable name="expressionDerivX" select="0.0"/>
#    <admst:choose>
#      <admst:when test="[$globalCurrentScope='sensitivity']">
#        <admst:variable name="expression" select="($a1?$a2:$a3)"/>
#        <admst:choose>
#          <admst:when test="[$arg2Pdep = 'yes' or $arg3Pdep='yes']">
#            <admst:variable name="expressionDerivX" select="($a1?$a2DerivX:$a3DerivX)"/>
#          </admst:when>
#          <admst:otherwise>
#            <admst:variable name="expressionDerivX" select="0.0"/>
#          </admst:otherwise>
#        </admst:choose>
#        <admst:variable name="expressionDeriv" select=""/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:variable name="expression" select="($a1?$a2:$a3)"/>
#        <admst:variable name="expressionDeriv" select="($a1?$a2Deriv:$a3Deriv)"/>
#        <admst:variable name="expressionDeriv2" select="($a1?$a2Deriv2:$a3Deriv2)"/>
#        <admst:variable name="expressionDeriv12" select="($a1?$a2Deriv12:$a3Deriv12)"/>
#        <admst:variable name="expressionDerivX" select="($a1?$a2DerivX:$a3DerivX)"/>
#      </admst:otherwise>
#    </admst:choose>
#    <admst:return name="returnedExpression" value="$expression"/>
#    <admst:return name="returnedExpressionDeriv" value="$expressionDeriv"/>
#    <admst:return name="returnedExpressionDeriv2" value="$expressionDeriv2"/>
#    <admst:return name="returnedExpressionDeriv12" value="$expressionDeriv12"/>
#    <admst:return name="returnedExpressionDerivX" value="$expressionDerivX"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   assignment
#   Given an assignment, format it for C++
#
#   Special Case:  If the assignment happens to be one that uses
#   $limit, we don't emit anything.  Those special things are handled
#   differently.
#   =================================================================-
#  -->
#  <admst:template match="assignment">
#    <admst:assert test="adms[datatypename='assignment']" format="assignment template called with something that is not an assignment\n"/>
#    <!-- Try skipping assignments to output variables (only) in sensitivity context, and assignments where the RHS contains output variables -->
#    <admst:if test="[$globalCurrentScope != 'sensitivity' or ($globalCurrentScope='sensitivity' and not((lhs/insource='no' and lhs/output='yes') or (lhs/insource='no' and exists(rhs/variable[output='yes' and insource='no' and input='no']))))]">
#      <admst:choose>
#        <admst:when test="[nilled(rhs/function/[name='\$limit'])]">
#          <admst:variable name="saveTemplateUse" select="$globalMustUseTemplate"/>
#          <admst:variable name="saveScalarForce" select="$globalMustForceScalar"/>
#          <!-- if the lhs has any probe dependence recorded, then it's a Fad type -->
#          <admst:if test="[exists(lhs/probe) and $globalCurrentScope!='sensitivity']">
#            <admst:variable name="globalMustUseTemplate" select="yes"/>
#          </admst:if>
#          <!-- Make sure we check parameter dependence of rhs and lhs variables-->
#          <admst:if test="[$globalCurrentScope='sensitivity']">
#            <admst:apply-templates select="lhs" match="collectParamDependence"/>
#            <admst:if test="[exists(lhs/#Pdependent)]">
#              <admst:variable name="globalMustUseTemplate" select="yes"/>
#            </admst:if>
#          </admst:if>
#          <admst:if test="[$globalCurrentScope='sensitivity']">
#            <admst:apply-templates select="rhs" match="collectParamDependence"/>
#          </admst:if>
#          <!-- If RHS contains any function calls other than
#               $simparam, ddt, and ddx, precompute them -->
#          <admst:text test="rhs/function[name!='\$simparam' and name!='ddt' and name!='ddx' and $skipFunctionPrecomp='n']" format="{\n"/>
#          <admst:apply-templates select="rhs/function[name!='\$simparam' and name!='ddt' and name!='ddx' and $skipFunctionPrecomp='n']" match="functionPrecomputation"/>
#          <!-- Let's emit the derivatives of the assignment first -->
#          <admst:if test="[lhs/type='real']">
#            <admst:apply-templates select="rhs/[not(nilled(function[name!='\$simparam' and name!='ddt' and name!='ddx']))]" match="functionDerivativePrecomputation"/>
#            <admst:if test="[$globalCurrentScope!='sensitivity' and not(nilled(lhs/probe)) and $skipFunctionPrecomp='n'  and (lhs/insource='yes' or not(nilled(lhs/ddxprobe)))]">
#              <admst:text format="\n"/>
#              <admst:variable name="needinitialize" select="no"/>
#              <admst:for-each select="lhs/probe">
#                <admst:variable name="myVar" path=".."/>
#                <admst:variable name="myprobe" path="."/>
#                <admst:if test="[not(exists(../../rhs/probe[branch/pnode=$myprobe/branch/pnode and branch/nnode=$myprobe/branch/nnode]))]">
#                  <admst:text format="d_%($myVar/name)_d%(nature)_%($myprobe/branch/pnode)_%($myprobe/branch/nnode) = "/>
#                  <admst:if test="[../insource='yes' and $doSecondDerivs='yes']">
#                    <admst:if test="[exists(../ddxprobe/branch/pnode[.=$myprobe/branch/pnode or .=$myprobe/branch/nnode])]">
#                      <admst:for-each select="$myVar/probe">
#                        <admst:text format="d_%($myVar/name)_d%($myprobe/nature)_%($myprobe/branch/pnode)_%($myprobe/branch/nnode)_d%(nature)_%(branch/pnode)_%(branch/nnode) = "/>
#                      </admst:for-each>
#                    </admst:if>
#                  </admst:if>
#                  <admst:variable name="needinitialize" select="yes"/>
#                </admst:if>
#              </admst:for-each>
#              <admst:if test="[$needinitialize = 'yes']">
#                <admst:text format=" 0.0;\n"/>
#              </admst:if>
#            </admst:if>
#            <admst:if test="[$globalCurrentScope!='sensitivity' and not(nilled(rhs/probe)) and (lhs/insource='yes' or not(nilled(lhs/ddxprobe)))]">
#              <admst:variable name="theLHS" path="lhs"/>
#              <admst:variable name="theRHS" path="rhs"/>
#              <admst:for-each select="rhs/probe">
#                <admst:variable name="derivProbe" select="%(.)"/>
#                <admst:apply-templates select="$theRHS/tree" match="%(adms/datatypename)">
#                  <admst:variable name="rhsDeriv" value="%(returned('returnedExpressionDeriv')/value)"/>
#                </admst:apply-templates>
#                <admst:variable name="lhsname" select="d_%($theLHS/name)_d%(nature)_%(branch/pnode)_%(branch/nnode)"/>
#                <admst:if test="[$lhsname != $rhsDeriv]">
#                  <admst:text format="$lhsname = $rhsDeriv;\n"/>
#                </admst:if>
#              </admst:for-each>
#              <admst:if test="[lhs/insource='yes']">
#                <!-- now handle the second derivatives as needed if there are ddxprobes in the lhs
#                     It would probably be cleaner to do this in the loop above, but it is neither
#                     necessary (I think) nor particularly readable.  So we redo loops -->
#                <admst:if test="[$doSecondDerivs='yes']">
#                  <admst:for-each select="$theLHS/probe">
#                    <!-- skip any on which the RHS doesn't depend, because we've already
#                         handled those with explicit 0.0 initialization -->
#                    <admst:variable name="myprobe" path="."/>
#                    <admst:if test="[exists(../../rhs/probe[branch/pnode=$myprobe/branch/pnode and branch/nnode=$myprobe/branch/nnode])]">
#                      <admst:if test="$theLHS/ddxprobe/branch/pnode[.=$myprobe/branch/pnode or .=$myprobe/branch/nnode]">
#                        <admst:variable name="derivProbe" select="%(.)"/>
#                        <admst:for-each select="$theLHS/probe">
#                          <admst:variable name="derivProbe2" select="%(.)"/>
#                          <admst:apply-templates select="$theRHS/tree" match="%(adms/datatypename)">
#                            <admst:variable name="rhsDeriv12" value="%(returned('returnedExpressionDeriv12')/value)"/>
#                          </admst:apply-templates>
#                          <admst:variable name="lhsname" select="d_%($theLHS/name)_d%($derivProbe/nature)_%($derivProbe/branch/pnode)_%($derivProbe/branch/nnode)_d%($derivProbe2/nature)_%($derivProbe2/branch/pnode)_%($derivProbe2/branch/nnode)"/>
#                          <admst:if test="[$lhsname != $rhsDeriv12]">
#                            <admst:text format="$lhsname = $rhsDeriv12;\n"/>
#                          </admst:if>
#                        </admst:for-each>
#                      </admst:if>
#                    </admst:if>
#                  </admst:for-each>
#                </admst:if>
#              </admst:if>
#            </admst:if>
#            <!-- if we *ARE* in sensitivity context, emit the derivatives of the expression w.r.t. "X" -->
#            <admst:if test="[$globalCurrentScope='sensitivity' and exists(lhs/#Pdependent)]">
#              <admst:variable name="theLHS" path="lhs"/>
#              <admst:variable name="theRHS" path="rhs"/>
#              <admst:apply-templates select="$theLHS" match="%(adms/datatypename)">
#                <admst:variable name="lhsname" select="%(returned('returnedExpressionDerivX')/value)"/>
#              </admst:apply-templates>
#              <admst:apply-templates select="$theRHS/tree" match="%(adms/datatypename)">
#                <admst:variable name="rhsDerivX" value="%(returned('returnedExpressionDerivX')/value)"/>
#              </admst:apply-templates>
#              <admst:if test="[$lhsname != $rhsDerivX]">
#                <admst:text format="$lhsname = $rhsDerivX;\n"/>
#              </admst:if>
#            </admst:if>
#          </admst:if>
#          <admst:apply-templates select="lhs" match="processTerm">
#            <admst:variable name="lhsname" select="%(returned('returnedExpression')/value)"/>
#          </admst:apply-templates>
#          <admst:apply-templates select="rhs" match="processTerm">
#            <admst:variable name="rhsexpr" select="%(returned('returnedExpression')/value)"/>
#          </admst:apply-templates>
#          <admst:if test="[$lhsname != $rhsexpr]">
#            <admst:text format="$lhsname = $rhsexpr;\n"/>
#          </admst:if>
#
#          <admst:variable name="globalMustUseTemplate" select="$saveTemplateUse"/>
#          <admst:variable name="globalMustForceScalar" select="$saveScalarForce"/>
#          <admst:text test="rhs/function[name!='\$simparam' and name!='ddt' and name!='ddx' and $skipFunctionPrecomp='n']" format="}\n"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:apply-templates select="." match="limiterAssignment"/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:if>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   limiterAssignment
#   Handle special case output for assignments that involve limiters
#   These require lots of extra output, and it's only part of the deal.
#   =================================================================-
#  -->
#  <admst:template match="limiterAssignment">
#    <admst:choose>
#      <admst:when test="[$globalCurrentScope='sensitivity']">
#        <!-- The probeVars for "typed" limiters must be pre-multiplied by the
#             type variable anyway, so for sensitivity (which doesn't do
#             limiting) just do the assignment -->
#        <admst:text format="%(printTerm(lhs)) = probeVars[%(xyceProbeConstantName(rhs/function[name='\$limit']/arguments[1])/[name='probeConstant']/value)];\n\n"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:text format="\n\n//%(printTerm(lhs)) = %(rhs);\n"/>
#        <admst:text format="if (getDeviceOptions().voltageLimiterFlag)\n"/>
#        <admst:text format="{\n"/>
#        <admst:text format="  int icheck=0;\n"/>
#        <admst:choose>
#          <admst:when test="[rhs/function[name='\$limit']/arguments[2]/datatypename='string']">
#            <admst:choose>
#              <!-- the string could be "pnjlim" or "fetlim" -->
#              <admst:when test="[rhs/function[name='\$limit']/arguments[2]/value='pnjlim' or rhs/function[name='\$limit']/arguments[2]/value='typedpnjlim']">
#                <!-- handle "pnjlim" -->
#                <admst:text format="  %(printTerm(lhs))_limited = devSupport.pnjlim(%(printTerm(lhs))_limited,%(printTerm(lhs))_old,%(printTerm((rhs/function[name='\$limit']/arguments[3]))),%(printTerm((rhs/function[name='\$limit']/arguments[4]))),&amp;icheck);\n"/>
#              </admst:when>
#              <admst:when test="[rhs/function[name='\$limit']/arguments[2]/value='pnjlim_new' or rhs/function[name='\$limit']/arguments[2]/value='typedpnjlim_new']">
#                <!-- handle "pnjlim_new" -->
#                <admst:text format="  %(printTerm(lhs))_limited = devSupport.pnjlim_new(%(printTerm(lhs))_limited,%(printTerm(lhs))_old,%(printTerm((rhs/function[name='\$limit']/arguments[3]))),%(printTerm((rhs/function[name='\$limit']/arguments[4]))),&amp;icheck);\n"/>
#              </admst:when>
#              <!-- if "fetlim" we would do something else, but for now nothing... -->
#              <admst:when test="[rhs/function[name='\$limit']/arguments[2]/value='fetlim' or rhs/function[name='\$limit']/arguments[2]/value='typedfetlim']">
#                <admst:warning format="Warning: fetlim not implemented, ignoring."/>
#              </admst:when>
#              <admst:when test="[rhs/function[name='\$limit']/arguments[2]/value='dummy' or rhs/function[name='\$limit']/arguments[2]/value='typeddummy']">
#                <admst:text format="  // dummy limiting for initialization purposes\n"/>
#              </admst:when>
#              <!-- KLUDGE ALERT!  ADMS has a bug.  It does not properly allow us to
#                   pass the name of the analog function to the $limit function as it
#                   should, and pukes an error saying "identifier never declared."
#                   To get something usable, I am going to support passing a string
#                   other than pnjlim or fetlim, and treat it as an analog function
#                   name if so.  This is NOT standard verilog and needs fixing. -->
#
#              <admst:otherwise>
#                <admst:text format="  %(printTerm(lhs))_limited = AnalogFunctions::%(rhs/function[name='\$limit']/arguments[2]/value)(%(printTerm(lhs))_limited,%(printTerm(lhs))_old"/>
#                <admst:if test="[count(rhs/function[name='\$limit']/arguments)>2]">
#                  <admst:choose>
#                    <admst:when test="[rhs/function[name='\$limit']/arguments[3]/value = 'typed']">
#                      <admst:if test="[count(rhs/function[name='\$limit']/arguments)>4]">
#                        <admst:text format=","/>
#                        <admst:join select="rhs/function[name='\$limit']/arguments[position(.)>4]" separator=",">
#                          <admst:text format="%(printTerm(.))"/>
#                        </admst:join>
#                      </admst:if>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:text format=","/>
#                      <admst:join select="rhs/function[name='\$limit']/arguments[position(.)>2]" separator=",">
#                        <admst:text format="%(printTerm(.))"/>
#                      </admst:join>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:if>
#                <admst:text format=");\n"/>
#                <admst:text format="if (%(printTerm(lhs))_limited != %(printTerm(lhs))_orig)\n"/>
#                <admst:text  format="{\n"/>
#                <admst:text  format="icheck=1;\n"/>
#                <admst:text  format="}\n"/>
#              </admst:otherwise>
#
#            </admst:choose>
#          </admst:when>
#          <admst:otherwise>
#            <admst:text format="  %(printTerm(lhs))_limited = AnalogFunctions::%(rhs/function[name='\$limit']/arguments[2])((%(printTerm(lhs))_limited,%(printTerm(lhs))_old"/>
#            <admst:if test="[count(rhs/function[name='\$limit']/arguments)>2]">
#              <admst:text format=","/>
#              <admst:join select="rhs/function[name='\$limit']/arguments[position(.)>2]" separator=",">
#                <admst:text format="%(printTerm(.))"/>
#              </admst:join>
#            </admst:if>
#            <admst:text format=");\n"/>
#          </admst:otherwise>
#        </admst:choose>
#        <admst:text format="  if (icheck == 1)\n"/>
#        <admst:text format="     origFlag = false;\n"/>
#
#        <admst:text format="  if (!origFlag)\n  {\n"/>
#        <admst:text format="    probeDiffs[%(xyceProbeConstantName(rhs/function[name='\$limit']/arguments[1])/[name='probeConstant']/value)] = %(printTerm(lhs))_limited - %(printTerm(lhs))_orig;\n"/>
#        <admst:text format="    probeVars[%(xyceProbeConstantName(rhs/function[name='\$limit']/arguments[1])/[name='probeConstant']/value)] += probeDiffs[%(xyceProbeConstantName(rhs/function[name='\$limit']/arguments[1])/[name='probeConstant']/value)];\n"/>
#        <admst:text format="  }\n"/>
#        <admst:text format="}\n"/>
#        <admst:text format="%(printTerm(lhs)) = probeVars[%(xyceProbeConstantName(rhs/function[name='\$limit']/arguments[1])/[name='probeConstant']/value)];\n\n"/>
#        <admst:variable name="rhsprobe" select="%(rhs/function[name='\$limit']/arguments[1])"/>
#        <admst:text format="d_%(printTerm(lhs))_d%($rhsprobe/nature)_%($rhsprobe/branch/pnode)_%($rhsprobe/branch/nnode) = d_probeVars[%(xyceProbeConstantName(rhs/function[name='\$limit']/arguments[1])/[name='probeConstant']/value)][%(xyceProbeConstantName(rhs/function[name='\$limit']/arguments[1])/[name='probeConstant']/value)];\n\n"/>
#      </admst:otherwise>
#    </admst:choose>
#  </admst:template>
#<!--
#   =================================================================-
#   contribution
#   Given a contribution, format it for xyce's updateIntermediateVars
#
#   This template is complicated by the need to compute Jdxp terms
#   when we are working with any RHS that involves limited probes.
#   =================================================================-
#  -->
#  <admst:template match="contribution">
#    <!-- Do sanity check to make sure we're actually processing a contribution
#    -->
#    <admst:assert test="adms[datatypename='contribution']" format="contribution template called with something that is not a contribution\n"/>
#
#    <!-- force template functions used on rhs to be explicitly instantiated -->
#    <admst:variable name="saveTemplateUse" select="$globalMustUseTemplate"/>
#    <admst:variable name="globalMustUseTemplate" select="yes"/>
#
#    <!-- actual contribution processing done here -->
#    <admst:text format="// %(lhs) &lt;+ %(rhs)\n"/>
#
#    <!-- static and dynamic go to different places (F vs. Q) -->
#    <admst:choose>
#      <admst:when test="[dynamic='yes']">
#        <admst:variable name="mode" select="dynamic"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:variable name="mode" select="static"/>
#      </admst:otherwise>
#    </admst:choose>
#
#    <admst:if test="[$globalCurrentScope='sensitivity']">
#      <admst:apply-templates select="rhs" match="collectParamDependence"/>
#    </admst:if>
#
#    <admst:choose>
#
#      <!-- Contributions into potential sources with rhs 0 are only
#           used for node collapse in set-up, so do nothing -->
#      <admst:when test="[lhs/discipline/potential=lhs/nature and (rhs/tree/datatypename='number' and (rhs/tree/value='0' or rhs/tree/value='0.0'))]">
#        <admst:text format="// do nothing at all\n"/>
#      </admst:when>
#
#      <!-- Contributions into potential sources that are nonzero are
#           really different.  In this case, we add/subtract the
#           associated branch current from the pos and negative nodes,
#           and also add to the branch equation -->
#      <admst:when test="[lhs/discipline/potential=lhs/nature]">
#        <!-- do nothing if a noise term -->
#        <admst:if test="[whitenoise='no' and flickernoise='no']">
#          <!-- Positive and negative nodes get +/- the branch variable value -->
#          <!-- But this is not done once for every contribution to a source,
#               just once for each source!  So these terms will be done
#               in the same finish-up operation mentioned below -->
#          <admst:variable name="branchConstant" select="%(xyceBranchConstantName(lhs/branch)/[name='branchConstant']/value)"/>
#
#          <admst:choose>
#            <admst:when test="[count(module/@limitedProbes)>0 and not(nilled(rhs/probe/[#limited='yes'])) and not ($globalCurrenScope='sensitivity')]">
#              <!-- Special processing when RHS involves limited probes -->
#              <admst:text format="{\n"/>
#              <admst:text format="double contribTemp;\n"/>
#              <admst:for-each select="rhs/probe">
#                <admst:text format="double d_contribTemp_d%(nature)_%(branch/pnode)_%(branch/nnode);\n"/>
#              </admst:for-each>
#              <admst:text format="contribTemp = %(printTerm(rhs));\n"/>
#              <admst:for-each select="rhs/probe">
#                <admst:text format="d_contribTemp_d%(nature)_%(branch/pnode)_%(branch/nnode) = /*diff(%(printTerm(..)),%(nature)_%(branch/pnode)_%(branch/nnode))*/;\n"/>
#                <admst:warning format="Model uses nonzero contributions into voltage branch and RHS is probe-dependent.  This is not correctly handled yet.\n"/>
#              </admst:for-each>
#              <admst:text format="%($mode)Contributions[%($branchConstant)] += contribTemp;\n"/>
#              <admst:for-each select="rhs/probe">
#                <admst:text format="d_%($mode)Contributions[%($branchConstant)][%(xyceProbeConstantName(.)/[name='probeConstant']/value)] += d_contribTemp_d%(nature)_%(branch/pnode)_%(branch/nnode);\n"/>
#              </admst:for-each>
#              <admst:text format="Jdxp_%($mode)[$branchConstant] += "/>
#              <admst:join select="rhs/probe[#limited='yes']" separator="+">
#                <admst:text format="d_contribTemp_d%(nature)_%(branch/pnode)_%(branch/nnode)*probeDiffs[%(xyceProbeConstantName(.)/[name='probeConstant']/value)]*d_probeVars[%(xyceProbeConstantName(.)/[name='probeConstant']/value)][%(xyceProbeConstantName(.)/[name='probeConstant']/value)]"/>
#              </admst:join>
#              <admst:text format=";\n"/>
#
#            </admst:when>
#
#            <admst:otherwise>
#              <!-- this is the simple case, no limiting needed -->
#              <!-- Branch equation gets + the RHS -->
#              <admst:text test="rhs/function[name!='\$simparam' and name!='ddt' and name!='ddx']" format="{\n"/>
#              <admst:apply-templates select="rhs/function[name!='\$simparam' and name!='ddt' and name!='ddx']" match="functionPrecomputation"/>
#              <admst:apply-templates select="rhs/[not(nilled(function))]" match="functionDerivativePrecomputation"/>
#              <admst:if test="[not($globalCurrentScope='sensitivity')]">
#                <admst:for-each select="rhs/probe">
#                  <admst:variable name="derivProbe" select="%(.)"/>
#                  <admst:apply-templates select="../tree" match="%(adms/datatypename)">
#                    <admst:variable name="rhsDeriv" value="%(returned('returnedExpressionDeriv')/value)"/>
#                  </admst:apply-templates>
#
#                  <admst:text format="d_%($mode)Contributions[%($branchConstant)][%(xyceProbeConstantName(.)/[name='probeConstant']/value)] += %($rhsDeriv);\n"/>
#                </admst:for-each>
#              </admst:if>
#              <admst:if test="[$globalCurrentScope='sensitivity']">
#                <admst:apply-templates select="rhs/tree" match="%(adms/datatypename)">
#                  <admst:variable name="rhsDerivX" value="%(returned('returnedExpressionDerivX')/value)"/>
#                </admst:apply-templates>
#
#                <admst:text format="d_%($mode)Contributions_dX[%($branchConstant)] += %($rhsDerivX);\n"/>
#              </admst:if>
#              <!-- sensitivity doesn't actually need to store the value of the contribution, just deriv -->
#              <admst:if test="[$globalCurrentScope != 'sensitivity']">
#                <admst:text format="%($mode)Contributions[%($branchConstant)] += %(printTerm(rhs));\n"/>
#              </admst:if>
#              <admst:text test="rhs/function[name!='\$simparam' and name!='ddt' and name!='ddx']" format="}\n"/>
#            </admst:otherwise>
#          </admst:choose>
#
#          <!-- There is one last contribution necessary, but we don't do it here.
#               The branch equation also needs to get - the potential
#               from the solution, but it should only get this once, and there
#               could be multiple contributions to this potential.  We'll
#               have to do it in a finish-up loop later -->
#        </admst:if>
#      </admst:when>
#
#      <!-- Otherwise it's a contribution into flow source, which is
#           the most most straightforward case -->
#      <admst:otherwise>
#        <!-- do nothing if a noise term -->
#        <admst:if test="[whitenoise='no' and flickernoise='no']">
#          <admst:variable name="pnode" select="%(lhs/branch/pnode)"/>
#          <admst:variable name="pnodeConstant" select="%(xyceNodeConstantName($pnode)/[name='nodeConstant']/value)"/>
#          <admst:variable name="nnode" select="%(lhs/branch/nnode)"/>
#          <admst:text test="rhs/function[name!='\$simparam' and name!='ddt' and name!='ddx']" format="{\n"/>
#          <admst:apply-templates select="rhs/function[name!='\$simparam' and name!='ddt' and name!='ddx']" match="functionPrecomputation"/>
#          <admst:apply-templates select="rhs/[not(nilled(function))]" match="functionDerivativePrecomputation"/>
#          <!-- special processing when contribution RHS involves limited
#               probes.  We must compute the rhs of the contribution,
#               but also generate the Jdxp terms-->
#          <admst:choose>
#            <admst:when test="[count(module/@limitedProbes)>0 and not(nilled(rhs/probe/[#limited='yes'])) and not($globalCurrentScope='sensitivity')]">
#              <admst:text format="{\n"/>
#              <admst:text format="double contribTemp;\n"/>
#              <admst:for-each select="rhs/probe">
#                <admst:text format="double d_contribTemp_d%(nature)_%(branch/pnode)_%(branch/nnode);\n"/>
#              </admst:for-each>
#              <admst:text format="contribTemp= %(printTerm(rhs));\n"/>
#              <admst:for-each select="rhs/probe">
#                <admst:variable name="derivProbe" select="%(.)"/>
#                <admst:apply-templates select="../tree" match="%(adms/datatypename)">
#                  <admst:variable name="rhsDeriv" value="%(returned('returnedExpressionDeriv')/value)"/>
#                </admst:apply-templates>
#                <admst:text format="d_contribTemp_d%(nature)_%(branch/pnode)_%(branch/nnode) = %($rhsDeriv);\n"/>
#              </admst:for-each>
#              <admst:text format="%($mode)Contributions[$pnodeConstant] += contribTemp;\n"/>
#              <admst:for-each select="rhs/probe">
#                <admst:text format="d_%($mode)Contributions[%($pnodeConstant)][%(xyceProbeConstantName(.)/[name='probeConstant']/value)] += d_contribTemp_d%(nature)_%(branch/pnode)_%(branch/nnode);\n"/>
#              </admst:for-each>
#              <admst:if test="$nnode[grounded='no']">
#                <admst:variable name="nnodeConstant" select="%(xyceNodeConstantName($nnode)/[name='nodeConstant']/value)"/>
#                <admst:text format="%($mode)Contributions[$nnodeConstant] -= contribTemp;\n"/>
#                <admst:for-each select="rhs/probe">
#                  <admst:text format="d_%($mode)Contributions[%($nnodeConstant)][%(xyceProbeConstantName(.)/[name='probeConstant']/value)] -= d_contribTemp_d%(nature)_%(branch/pnode)_%(branch/nnode);\n"/>
#                </admst:for-each>
#              </admst:if>
#
#              <admst:text format="\n"/>
#
#              <!-- generate the Jdxp's:
#                   Jdxp[pnode]+= d(rhs)/d(probe)*deltaprobe*dlimitedprobe/dprobe
#
#                   The "dlimitedprobe/dprobe" thing is to handle cases
#                   where there could be a minus sign introduced by limiting,
#                   which can happen with PNP/PMOS vs. NPN/NMOS limiting hacks.
#
#                   Similar for Jdxp[nnode]
#                   -->
#              <admst:text format="Jdxp_%($mode)[$pnodeConstant] += "/>
#              <admst:join select="rhs/probe[#limited='yes']" separator="+">
#                <admst:text format="d_contribTemp_d%(nature)_%(branch/pnode)_%(branch/nnode)*probeDiffs[%(xyceProbeConstantName(.)/[name='probeConstant']/value)]*d_probeVars[%(xyceProbeConstantName(.)/[name='probeConstant']/value)][%(xyceProbeConstantName(.)/[name='probeConstant']/value)]"/>
#              </admst:join>
#              <admst:text format=";\n"/>
#              <admst:if test="$nnode[grounded='no']">
#                <admst:variable name="nnodeConstant" select="%(xyceNodeConstantName($nnode)/[name='nodeConstant']/value)"/>
#                <admst:text format="Jdxp_%($mode)[$nnodeConstant] -= "/>
#                <admst:join select="rhs/probe[#limited='yes']" separator="+">
#                <admst:text format="d_contribTemp_d%(nature)_%(branch/pnode)_%(branch/nnode)*probeDiffs[%(xyceProbeConstantName(.)/[name='probeConstant']/value)]*d_probeVars[%(xyceProbeConstantName(.)/[name='probeConstant']/value)][%(xyceProbeConstantName(.)/[name='probeConstant']/value)]"/>
#                </admst:join>
#                <admst:text format=";\n"/>
#              </admst:if>
#              <admst:text format="}\n"/>
#            </admst:when>
#
#            <!-- When no limiting, this is much simpler: Just output RHS -->
#            <admst:otherwise>
#              <admst:if test="[$globalCurrentScope!='sensitivity']">
#                <admst:text format="%($mode)Contributions[$pnodeConstant] += %(printTerm(rhs));\n"/>
#              </admst:if>
#              <admst:if test="[$globalCurrentScope='sensitivity']">
#                <admst:apply-templates select="rhs/tree" match="%(adms/datatypename)">
#                  <admst:variable name="rhsDerivX" value="%(returned('returnedExpressionDerivX')/value)"/>
#                </admst:apply-templates>
#                <admst:text format="d_%($mode)Contributions_dX[%($pnodeConstant)]+= %($rhsDerivX);\n"/>
#              </admst:if>
#              <admst:if test="[not($globalCurrentScope='sensitivity')]">
#                <admst:for-each select="rhs/probe">
#                <admst:variable name="derivProbe" select="%(.)"/>
#                <admst:apply-templates select="../tree" match="%(adms/datatypename)">
#                  <admst:variable name="rhsDeriv" value="%(returned('returnedExpressionDeriv')/value)"/>
#                </admst:apply-templates>
#                <admst:text format="d_%($mode)Contributions[%($pnodeConstant)][%(xyceProbeConstantName(.)/[name='probeConstant']/value)] += %($rhsDeriv);\n"/>
#                </admst:for-each>
#              </admst:if>
#              <admst:if test="$nnode[grounded='no']">
#                <admst:variable name="nnodeConstant" select="%(xyceNodeConstantName($nnode)/[name='nodeConstant']/value)"/>
#                <admst:if test="[$globalCurrentScope!='sensitivity']">
#                  <admst:text format="%($mode)Contributions[$nnodeConstant] -= %(printTerm(rhs));\n"/>
#                </admst:if>
#                <admst:if test="[$globalCurrentScope='sensitivity']">
#                  <admst:apply-templates select="rhs/tree" match="%(adms/datatypename)">
#                    <admst:variable name="rhsDerivX" value="%(returned('returnedExpressionDerivX')/value)"/>
#                  </admst:apply-templates>
#                  <admst:text format="d_%($mode)Contributions_dX[($nnodeConstant)]-= %($rhsDerivX);\n"/>
#                </admst:if>
#                <admst:if test="[not($globalCurrentScope='sensitivity')]">
#                  <admst:for-each select="rhs/probe">
#                    <admst:variable name="derivProbe" select="%(.)"/>
#                    <admst:apply-templates select="../tree" match="%(adms/datatypename)">
#                      <admst:variable name="rhsDeriv" value="%(returned('returnedExpressionDeriv')/value)"/>
#                    </admst:apply-templates>
#                    <admst:text format="d_%($mode)Contributions[%($nnodeConstant)][%(xyceProbeConstantName(.)/[name='probeConstant']/value)] -= %($rhsDeriv);\n"/>
#                  </admst:for-each>
#                </admst:if>
#              </admst:if>
#            </admst:otherwise>
#          </admst:choose>
#          <admst:text test="rhs/function[name!='\$simparam' and name!='ddt' and name!='ddx']" format="}\n"/>
#        </admst:if>
#          <!-- we will handle only very specific types of  noise contributions,
#               those whose RHS is strictly a single noise function.  This is
#               enforced by the assertions in xyceNoiseContributionName.  Get
#               its name -->
#        <admst:if test="[(whitenoise='yes' or flickernoise='yes') and not($globalCurrentScope='sensitivity')]">
#          <admst:variable name="theNoiseContributionName" select="%(xyceNoiseContributionName(.))"/>
#          <admst:text format="if (getSolverState().noiseFlag)\n{\n"/>
#          <!-- now force scalar, because we're assigning to a double value -->
#          <admst:variable name="saveForceScalar" select="$globalMustForceScalar"/>
#          <admst:variable name="globalMustForceScalar" select="yes"/>
#          <admst:apply-templates select="rhs/function[name!='\$simparam' and name!='ddt' and name!='ddx']" match="functionPrecomputation"/>
#          <admst:text format="  noiseContribsPower[%(#noiseContIndex)]="/>
#          <!-- extract the power argument, the first one-->
#          <admst:text format=" %(printTerm(rhs/tree/arguments[1]));\n"/>
#          <!-- flicker noise has an extra argument -->
#          <admst:if test="[rhs/tree/name='flicker_noise']">
#            <admst:text format="  noiseContribsExponent[%(#noiseContIndex)]="/>
#            <admst:text format=" %(printTerm(rhs/tree/arguments[2]));\n"/>
#          </admst:if>
#          <admst:text format="}\n"/>
#          <admst:variable name="globalMustForceScalar" select="$saveForceScalar"/>
#        </admst:if>
#
#      </admst:otherwise>
#    </admst:choose>
#    <admst:variable name="globalMustUseTemplate" select="$saveTemplateUse"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   probe
#   Given a probe, format it for xyce's updateIntermediateVars
#   =================================================================-
#  -->
#  <admst:template match="probe">
#    <admst:variable name="expression" select="(probeVars[%(xyceProbeConstantName(.)/[name='probeConstant']/value)])"/>
#    <admst:variable name="expressionDeriv2" select="0.0"/>
#    <admst:variable name="expressionDeriv12" select="0.0"/>
#    <admst:variable name="expressionDerivX" select="0.0"/>
#    <admst:choose>
#      <admst:when test="[.=$derivProbe]">
#        <admst:variable name="expressionDeriv" select="d_probeVars[%(xyceProbeConstantName(.)/[name='probeConstant']/value)][%(xyceProbeConstantName(.)/[name='probeConstant']/value)]"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:variable name="expressionDeriv" select="0.0"/>
#      </admst:otherwise>
#    </admst:choose>
#    <admst:if test="$derivProbe2">
#      <admst:choose>
#        <admst:when test="[.=$derivProbe2]">
#          <admst:variable name="expressionDeriv2" select="d_probeVars[%(xyceProbeConstantName(.)/[name='probeConstant']/value)][%(xyceProbeConstantName(.)/[name='probeConstant']/value)]"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:variable name="expressionDeriv2" select="0.0"/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:if>
#    <admst:return name="returnedExpression" value="$expression"/>
#    <admst:return name="returnedExpressionDeriv" value="$expressionDeriv"/>
#    <admst:return name="returnedExpressionDeriv2" value="$expressionDeriv2"/>
#    <admst:return name="returnedExpressionDeriv12" value="$expressionDeriv12"/>
#    <admst:return name="returnedExpressionDerivX" value="$expressionDerivX"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   variable
#   given a variable, emit C++ reference thereto
#   =================================================================-
#  -->
#  <admst:template match="variable">
#    <admst:assert test="adms[datatypename='variable']" format="variable template called on non-variable\n"/>
#    <admst:variable name="expressionDerivX" select="0.0"/>
#    <admst:choose>
#      <admst:when test="[scope='local']">
#        <admst:variable name="expression" select="%(name)"/>
#      </admst:when>
#      <admst:when test="[scope='global_instance']">
#        <admst:choose>
#          <admst:when test="[($globalCurrentScope='instance' or exists(attribute[name='xyceAlsoModel'])) and not($globalCurrentScope='sensitivity')]">
#            <admst:variable name="expression" select="%(name)"/>
#          </admst:when>
#          <admst:when test="[$globalCurrentScope='sensitivity']">
#            <admst:choose>
#              <admst:when test="[input='yes']">
#                <admst:choose>
#                  <admst:when test="[$globalSensitivityScope='model']">
#                    <admst:if test="[not exists(attribute[name='xyceAlsoModel'])]">
#                      <admst:fatal format="it is not legal to access instance variable %(name) in model context!  Our current scope is $globalCurrentScope, and we are generating $globalSensitivityScope code.\n"/>
#                    </admst:if>
#                    <admst:variable name="expression" select="modelStruct.modelPar_%(name)"/>
#                    <admst:if test="[exists(#Pdependent)]">
#                      <admst:variable name="expressionDerivX" select="modelStruct.d_modelPar_%(name)_dX"/>
#                    </admst:if>
#                  </admst:when>
#                  <admst:otherwise>
#                    <admst:variable name="expression" select="instanceStruct.instancePar_%(name)"/>
#                    <admst:if test="[exists(#Pdependent)]">
#                      <admst:variable name="expressionDerivX" select="instanceStruct.d_instancePar_%(name)_dX"/>
#                    </admst:if>
#                  </admst:otherwise>
#                </admst:choose>
#              </admst:when>
#              <admst:otherwise>
#                <!-- Ooof.  Sometimes one might put an output variable on the RHS of a local variable that is neither insource nor output -->
#                <!-- But we are explicitly skipping assignments and declarations of those variables, so we better not try to use them! -->
#                <admst:choose>
#                  <admst:when test="[insource='no' and output='yes']">
#                    <admst:variable name="expression" select="1.0"/>
#                    <admst:variable name="expressionDerivX" select="0.0"/>
#                  </admst:when>
#                  <admst:otherwise>
#                    <admst:variable name="expression" select="instanceStruct.instanceVar_%(name)"/>
#                    <admst:if test="[exists(#Pdependent)]">
#                      <admst:variable name="expressionDerivX" select="instanceStruct.d_instanceVar_%(name)_dX"/>
#                    </admst:if>
#                  </admst:otherwise>
#                </admst:choose>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:when>
#          <admst:otherwise>
#            <admst:fatal format="it is not legal to access instance variable %(name) outside of the instance class!  Our current scope is $globalCurrentScope\n"/>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[scope='global_model']">
#        <admst:choose>
#          <admst:when test="[$globalCurrentScope='model']">
#            <admst:variable name="expression" select="%(name)"/>
#          </admst:when>
#          <admst:when test="[$globalCurrentScope='sensitivity']">
#            <admst:choose>
#              <admst:when test="[input='yes']">
#                <admst:variable name="expression" select="modelStruct.modelPar_%(name)"/>
#                <admst:if test="[exists(#Pdependent)]">
#                  <admst:variable name="expressionDerivX" select="modelStruct.d_modelPar_%(name)_dX"/>
#                </admst:if>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expression" select="modelStruct.modelVar_%(name)"/>
#                <admst:if test="[exists(#Pdependent)]">
#                  <admst:variable name="expressionDerivX" select="modelStruct.d_modelVar_%(name)_dX"/>
#                </admst:if>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:when>
#          <admst:otherwise>
#            <admst:variable name="expression" select="(model_.%(name))"/>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <admst:otherwise>
#        <admst:fatal format="Unknown variable scope for %(name): %(scope)\n"/>
#      </admst:otherwise>
#    </admst:choose>
#
#    <!-- Now generate derivatives with respect to probes and "X" -->
#    <admst:variable name="expressionDeriv" select="0.0"/>
#    <admst:variable name="expressionDeriv2" select="0.0"/>
#    <admst:variable name="expressionDeriv12" select="0.0"/>
#    <!-- Only have derivatives if this variable is a real variable, not
#         an int or string -->
#    <admst:if test="[type='real']">
#      <admst:if test="[$globalCurrentScope='sensitivity' and exists(#Pdependent) and $expressionDerivX='0.0' and not(insource='no' and output='yes')]">
#        <admst:variable name="expressionDerivX" select="d_%($expression)_dX"/>
#      </admst:if>
#      <admst:if test="[insource='yes' or not(nilled(ddxprobe))]">
#        <admst:if-inside select="$derivProbe" list="%(probe)">
#          <admst:variable name="expressionDeriv" select="d_%(name)_d%($derivProbe/nature/access)_%($derivProbe/branch/pnode/name)_%($derivProbe/branch/nnode/name)"/>
#        </admst:if-inside>
#        <admst:if test="$derivProbe2">
#          <admst:if-inside select="$derivProbe2" list="%(probe)">
#            <admst:variable name="expressionDeriv2" select="d_%(name)_d%($derivProbe2/nature/access)_%($derivProbe2/branch/pnode/name)_%($derivProbe2/branch/nnode/name)"/>
#          </admst:if-inside>
#          <admst:if test="[insource='yes' and not(nilled(ddxprobe))]">
#            <admst:if-inside select="$derivProbe" list="%(probe)">
#              <!-- Note that if we are doing second derivatives, it's because
#                   we are differentiating something that has been ddx()ed.
#                   If so, derivProbe is supposed to be the ddx-related
#                   probe, and derivProbe2 is the regular derivative.
#                   If derivProbe is not associated with a ddxprobe in this
#                   variable, we should be returning ZERO.
#              -->
#              <admst:choose>
#                <admst:when test="[exists(ddxprobe/branch/pnode[.=$derivProbe/branch/pnode or .=$derivProbe/branch/nnode])]">
#                  <admst:if-inside select="$derivProbe2" list="%(probe)">
#                    <admst:variable name="expressionDeriv12" select="d_%(name)_d%($derivProbe/nature/access)_%($derivProbe/branch/pnode/name)_%($derivProbe/branch/nnode/name)_d%($derivProbe2/nature/access)_%($derivProbe2/branch/pnode/name)_%($derivProbe2/branch/nnode/name)"/>
#                  </admst:if-inside>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv12" select="0.0"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if-inside>
#          </admst:if>
#        </admst:if>
#      </admst:if>
#    </admst:if>
#
#    <admst:return name="returnedExpression" value="$expression"/>
#    <admst:return name="returnedExpressionDeriv" value="$expressionDeriv"/>
#    <admst:return name="returnedExpressionDeriv2" value="$expressionDeriv2"/>
#    <admst:return name="returnedExpressionDeriv12" value="$expressionDeriv12"/>
#    <admst:return name="returnedExpressionDerivX" value="$expressionDerivX"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   function
#     This template depends on there having been function precomputation
#     performed, with functions calls already having been evaluated
#     and stored into appropriately named variables.  We simply
#     emit the name of the variable instead of the call here.
#     The exception will be for ddt, which may only appear on the RHS of
#     a contribution, and which simply returns the argument of ddt
#     for stuffing into the Q vector.
#   =================================================================-
#  -->
#  <admst:template match="function">
#    <admst:variable name="expressionDeriv" select="0.0"/>
#    <admst:variable name="expressionDeriv2" select="0.0"/>
#    <admst:variable name="expressionDeriv12" select="0.0"/>
#    <admst:variable name="expressionDerivX" select="0.0"/>
#    <admst:choose>
#      <admst:when test="[name='\$port_connected']">
#        <admst:assert test="arguments[1]/adms[datatypename='node']" format="\$port_connected argument must be a node\n"/>
#        <admst:variable name="expression" select="portsConnected_[%(xyceNodeConstantName(arguments[1])/[name='nodeConstant']/value)]"/>
#      </admst:when>
#      <admst:when test="[(name='min' or name='max') and $skipFunctionPrecomp='y']">
#        <admst:variable name="expression" select="%(functionCall(.)/[name='returnedExpression']/value)"/>
#      </admst:when>
#      <admst:when test="[name='absdelay']">
#        <admst:apply-templates select="arguments[1]" match="processTerm">
#          <admst:variable name="expression" select="FIXMEabsdelay(%(returned('returnedExpression')/value))"/>
#        </admst:apply-templates>
#      </admst:when>
#      <!-- DDT is a null function in Xyce we'll load such things into
#           dynamic contributions, and those will be differentiated elsewhere -->
#      <admst:when test="[name='ddt']">
#        <admst:apply-templates select="arguments[1]" match="processTerm">
#          <admst:variable name="expression" select="(%(returned('returnedExpression')/value))"/>
#          <admst:variable name="expressionDeriv" select="(%(returned('returnedExpressionDeriv')/value))"/>
#          <admst:if test="$derivProbe2">
#            <admst:variable name="expressionDeriv2" select="(%(returned('returnedExpressionDeriv2')/value))"/>
#            <admst:variable name="expressionDeriv12" select="(%(returned('returnedExpressionDeriv12')/value))"/>
#          </admst:if>
#          <admst:if test="[$globalCurrentScope='sensitivity' and exists(#Pdependent)]">
#            <admst:variable name="expressionDerivX" select="(%(returned('returnedExpressionDerivX')/value))"/>
#          </admst:if>
#
#        </admst:apply-templates>
#      </admst:when>
#      <admst:when test="[name='\$given' or name='\$param_given']">
#        <admst:variable name="arg1" select="%(arguments[1])"/>
#        <admst:assert test="$arg1[datatypename='variable' and input='yes']" format="%(name): argument is not a parameter\n"/>
#        <admst:choose>
#          <admst:when test="$arg1/[parametertype='model']">
#            <admst:choose>
#              <admst:when test="[$globalCurrentScope = 'model']">
#                <admst:variable name="expression" select="given(&quot;$arg1&quot;)"/>
#              </admst:when>
#              <admst:when test="[$globalCurrentScope = 'instance']">
#                <admst:variable name="expression" select="(model_.given(&quot;$arg1&quot;))"/>
#              </admst:when>
#              <admst:when test="[$globalCurrentScope = 'sensitivity']">
#                <admst:variable name="expression" select="modelStruct.modelPar_given_$arg1"/>
#              </admst:when>
#            </admst:choose>
#          </admst:when>
#          <admst:when test="$arg1/[parametertype='instance']">
#            <admst:choose>
#              <admst:when test="[$globalCurrentScope = 'instance']">
#                <admst:variable name="expression" select="given(&quot;$arg1&quot;)"/>
#              </admst:when>
#              <admst:when test="[$globalCurrentScope = 'sensitivity']">
#                <admst:variable name="expression" select="instanceStruct.instancePar_given_$arg1"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:fatal format="Attempt to use \$given() on an instance variable outside of instance scope\n"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:when>
#          <admst:otherwise>
#            <admst:fatal format="%(name): should not be reached\n"/>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[name='\$temperature']">
#        <admst:assert test="[nilled(arguments)]" format="%(name): should not have arguments\n"/>
#        <admst:choose>
#          <admst:when test="[$globalCurrentScope='instance' or $globalCurrentScope='sensitivity']">
#            <admst:variable name="expression" select="admsTemperature"/>
#          </admst:when>
#          <!-- KLUDGE!!!!!! -->
#          <!-- Assumes that when at model scope, $temperature is taken as
#               the default temperature of the simulator. -->
#          <!-- At instance scope, we use whatever Xyce passed in to
#               updateTemperature for that instance. -->
#          <admst:when test="[$globalCurrentScope='model']">
#            <admst:variable name="expression" select="admsModTemp"/>
#          </admst:when>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[name='\$mfactor']">
#        <admst:assert test="[nilled(arguments)]" format="%(name): should not have arguments\n"/>
#        <admst:variable name="expression" select="FIXME_MFACTOR"/>
#      </admst:when>
#      <admst:when test="[name='\$vt']">
#        <admst:choose>
#          <admst:when test="[nilled(arguments)]">
#            <admst:variable name="expression" select="adms_vt_nom"/>
#          </admst:when>
#          <admst:when test="arguments[count(.)=1]">
#            <admst:apply-templates select="arguments[1]" match="processTerm">
#              <admst:choose>
#                <admst:when test="[$globalCurrentScope='AF']">
#                  <admst:variable name="expression" select="adms_vt(%(returned('returnedExpression')/value))"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expression" select="adms_vt(%(returned('returnedExpression')/value))"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:apply-templates>
#          </admst:when>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[name='\$scale']">
#        <admst:assert test="[nilled(arguments)]" format="%(name): should not have arguments\n"/>
#        <admst:variable name="expression" select="FIXME_scale"/>
#      </admst:when>
#      <admst:when test="[name='\$abstime' or name='\$realtime']">
#        <admst:assert test="[nilled(arguments)]" format="%(name): should not have arguments\n"/>
#          <admst:choose>
#            <admst:when test="[$globalCurrentScope='sensitivity']">
#              <admst:variable name="expression" select="theInstance.getSolverState().currTime_"/>
#            </admst:when>
#            <admst:otherwise>
#              <admst:variable name="expression" select="getSolverState().currTime_"/>
#            </admst:otherwise>
#          </admst:choose>
#      </admst:when>
#      <admst:when test="[name='ddx']">
#        <admst:assert test="arguments[count(.)=2]" format="%(name): should have two arguments exactly\n"/>
#        <admst:assert test="arguments[2]/adms[datatypename='probe']" format="%(name): second argument is not a probe\n"/>
#        <admst:assert test="arguments[2]/branch/nnode[grounded='yes']" format="%(name): probe argument has non-ground negative node [Xyce/ADMS limitation]\n"/>
#        <admst:choose>
#          <admst:when test="[$globalCurrentScope='sensitivity']">
#            <admst:variable name="expression" select="0.0 /*FIXME: ddx(%(arguments[1]),%(arguments[2])) not implemented in sensitivity context */"/>
#          </admst:when>
#          <admst:otherwise>
#            <!-- save any "derivProbe" value because we're monkeying with it -->
#            <admst:variable name="savedDerivProbe" path="$derivProbe" />
#            <admst:variable name="savedDerivProbe2" path="$derivProbe2" />
#            <admst:variable name="expressionToDDX" path="arguments[1]"/>
#            <admst:variable name="theDDXProbe" path="arguments[2]"/>
#            <admst:variable name="expression" select=""/>
#            <admst:variable name="expressionDeriv" select=""/>
#            <admst:reset select="$expressionToDDX/@probe"/>
#            <admst:variable name="probeList" path="$expressionToDDX/@probe"/>
#            <admst:apply-templates match="recursiveDetectProbeDependence" select="$expressionToDDX"/>
#            <admst:for-each select="$probeList">
#              <admst:variable name="derivProbe" path="."/>
#              <admst:variable name="derivProbe2" path="$savedDerivProbe"/>
#              <admst:choose>
#                <admst:when test="$derivProbe/branch/pnode[.=$theDDXProbe/branch/pnode]">
#                  <admst:apply-templates select="$expressionToDDX" match="processTerm">
#                    <admst:variable name="exprPartialDeriv" select="%(returned('returnedExpressionDeriv')/value)"/>
#                    <admst:variable name="exprPartialDeriv12" select="%(returned('returnedExpressionDeriv12')/value)"/>
#                  </admst:apply-templates>
#                  <admst:variable name="expression" select="$expression+$exprPartialDeriv"/>
#                  <admst:variable name="expressionDeriv" select="$expressionDeriv+$exprPartialDeriv12"/>
#                </admst:when>
#                <admst:when test="$derivProbe/branch/nnode[.=$theDDXProbe/branch/pnode]">
#                  <admst:apply-templates select="$expressionToDDX" match="processTerm">
#                    <admst:variable name="exprPartialDeriv" select="%(returned('returnedExpressionDeriv')/value)"/>
#                    <admst:variable name="exprPartialDeriv12" select="%(returned('returnedExpressionDeriv12')/value)"/>
#                  </admst:apply-templates>
#                  <admst:variable name="expression" select="$expression-$exprPartialDeriv"/>
#                  <admst:variable name="expressionDeriv" select="$expressionDeriv-$exprPartialDeriv12"/>
#                </admst:when>
#              </admst:choose>
#            </admst:for-each>
#            <admst:choose>
#              <admst:when test="[not($expression = '')]">
#                <admst:variable name="expression" select="($expression)"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expression" select="0.0"/>
#              </admst:otherwise>
#            </admst:choose>
#            <admst:choose>
#              <admst:when test="[not($expressionDeriv = '')]">
#                <admst:variable name="expressionDeriv" select="($expressionDeriv)"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:otherwise>
#            </admst:choose>
#            <!-- restore original "derivProbe"  -->
#            <admst:variable name="derivProbe" path="$savedDerivProbe" />
#            <admst:variable name="derivProbe2" path="$savedDerivProbe2" />
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[name='floor']">
#        <admst:assert test="arguments[count(.)=1]" format="%(name): should have one argument exactly\n"/>
#        <admst:apply-templates select="arguments[1]" match="processTerm">
#          <admst:variable name="expression" select="%(returned('returnedExpression')/value)"/>
#          <admst:variable name="expression" select="floor($expression)"/>
#          <!-- floor has all zero derivs -->
#        </admst:apply-templates>
#      </admst:when>
#      <admst:when test="[name='ceil']">
#        <admst:assert test="arguments[count(.)=1]" format="%(name): should have one argument exactly\n"/>
#        <admst:apply-templates select="arguments[1]" match="processTerm">
#          <admst:variable name="expression" select="%(returned('returnedExpression')/value)"/>
#          <admst:variable name="expression" select="ceil($expression)"/>
#          <!-- floor has all zero derivs -->
#        </admst:apply-templates>
#      </admst:when>
#      <admst:when test="[name='\$simparam']">
#        <admst:choose>
#          <admst:when test="[arguments[1]/datatypename='string' and arguments[1]/value='gmin']">
#            <admst:choose>
#              <admst:when test="[$globalCurrentScope='sensitivity']">
#                <admst:variable name="expression" select="ADMSgmin_arg"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expression" select="getDeviceOptions().gmin"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:when>
#          <admst:otherwise>
#            <admst:assert test="arguments[count(.)=2]" format="Unrecognized simparam %(arguments[1]) and no expression provided.\n"/>
#            <admst:apply-templates select="arguments[2]" match="processTerm">
#              <admst:variable name="expression" select="%(returned('returnedExpression')/value)"/>
#            </admst:apply-templates>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[$skipFunctionPrecomp='y']">
#        <!-- if we aren't caught by anything above, and this is set,
#             proceed as normal -->
#        <admst:choose>
#          <admst:when test="[name='ln' or name='log' or name='sqrt']">
#            <admst:variable name="expression" select="%(funcname(.)/[name='fname']/value)"/>
#            <admst:variable name="args" select=""/>
#            <admst:for-each select="arguments">
#              <admst:if test="[$args!='']">
#                <admst:variable name="args" select="$args,"/>
#              </admst:if>
#              <admst:apply-templates select="." match="realArgument">
#                <admst:variable name="args" select="$args%(returned('argval')/value)"/>
#              </admst:apply-templates>
#            </admst:for-each>
#            <admst:variable name="expression" select="$expression($args)"/>
#          </admst:when>
#          <admst:when test="[name='hypot']">
#            <admst:assert test="arguments[count(.)=2]" format="hypot function must take exactly two arguments.\n"/>
#            <admst:variable name="expression" value="sqrt"/>
#            <admst:variable name="args" select=""/>
#            <admst:for-each select="arguments">
#              <admst:if test="[$args!='']">
#                <admst:variable name="args" select="$args+"/>
#              </admst:if>
#              <admst:apply-templates select="." match="processTerm">
#                <admst:variable name="args" select="$args%(returned('returnedExpression')/value)*%(returned('returnedExpression')/value)"/>
#              </admst:apply-templates>
#            </admst:for-each>
#            <admst:variable name="expression" select="$expression($args)"/>
#          </admst:when>
#          <admst:otherwise>
#            <admst:variable name="expression" select="%(funcname(.)/[name='fname']/value)"/>
#            <admst:variable name="args" select=""/>
#            <admst:for-each select="arguments">
#              <admst:if test="[$args!='']">
#                <admst:variable name="args" select="$args,"/>
#              </admst:if>
#              <admst:apply-templates select="." match="processTerm">
#                <admst:variable name="args" select="$args%(returned('returnedExpression')/value)"/>
#              </admst:apply-templates>
#            </admst:for-each>
#            <admst:variable name="expression" select="$expression($args)"/>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <admst:otherwise>
#        <admst:choose>
#          <admst:when test="[name='exp' or name='ln' or name='log' or name='sqrt' or name='abs' or name='limexp' or name='cos' or name='sin' or name='tan' or name='acos' or name='asin' or name='atan' or name='cosh' or name='sinh' or name='tanh' or name='acosh' or name='asinh' or name='atanh' or name='pow' or name='min' or name='max' or name='hypot' or name='atan2']">
#            <!-- we must use precomputed function vars -->
#            <admst:variable name="expression" select="value_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))"/>
#          </admst:when>
#          <admst:otherwise>
#            <!-- <admst:message format="Falling back on direct function call instead of precomputation for function %(name) of class %(class).  May be a sign of incomplete back end.\n"/> -->
#            <admst:variable name="expression" select="%(functionCall(.)/[name='returnedExpression']/value)"/>
#          </admst:otherwise>
#        </admst:choose>
#        <!-- now try to deal with derivatives -->
#        <admst:choose>
#          <!-- Single-argument functions -->
#          <admst:when test="[name='exp' or name='ln' or name='log' or name='sqrt' or name='abs' or name='limexp' or name='cos' or name='sin' or name='tan' or name='acos' or name='asin' or name='atan' or name='cosh' or name='sinh' or name='tanh' or name='acosh' or name='asinh' or name='atanh' ]">
#            <admst:apply-templates select="arguments[1]" match="processTerm">
#              <admst:variable name="a1Deriv" select="%(returned('returnedExpressionDeriv')/value)"/>
#              <admst:variable name="a1Deriv2" select="%(returned('returnedExpressionDeriv2')/value)"/>
#              <admst:variable name="a1Deriv12" select="%(returned('returnedExpressionDeriv12')/value)"/>
#              <admst:variable name="a1DerivX" select="%(returned('returnedExpressionDerivX')/value)"/>
#            </admst:apply-templates>
#            <admst:choose>
#              <admst:when test="[$a1Deriv='0.0']">
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv" select="(deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0*($a1Deriv))"/>
#              </admst:otherwise>
#            </admst:choose>
#            <admst:if test="$derivProbe2">
#              <admst:choose>
#                <admst:when test="[$a1Deriv2='0.0']">
#                  <admst:variable name="expressionDeriv2" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv2" select="deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0*($a1Deriv2)"/>
#                </admst:otherwise>
#              </admst:choose>
#              <admst:choose>
#                <admst:when test="[($a1Deriv ='0.0' or $a1Deriv2='0.0') and $a1Deriv12='0.0']">
#                  <admst:variable name="expressionDeriv12" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv12='0.0']">
#                  <admst:apply-templates select="." match="oneArgSecondDeriv">
#                    <admst:variable name="d2fdx2" select="%(returned('d2fdx2')/value)"/>
#                  </admst:apply-templates>
#                  <admst:variable name="expressionDeriv12" select="$d2fdx2*$a1Deriv*$a1Deriv2"/>
#                </admst:when>
#                <admst:when test="[($a1Deriv='0.0' or $a1Deriv2='0.0')]">
#                  <admst:variable name="expressionDeriv12" select="deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0*($a1Deriv12)"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:apply-templates select="." match="oneArgSecondDeriv">
#                    <admst:variable name="d2fdx2" select="%(returned('d2fdx2')/value)"/>
#                  </admst:apply-templates>
#                  <admst:choose>
#                    <admst:when test="[$d2fdx2='0.0']">
#                      <!-- pretty much only for abs()-->
#                      <admst:variable name="expressionDeriv12" select="deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0*($a1Deriv12)"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="expressionDeriv12" select="($d2fdx2*$a1Deriv*$a1Deriv2+(deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0*($a1Deriv12)))"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#            <admst:if test="[$globalCurrentScope='sensitivity' and exists(arguments[1]/#Pdependent)]">
#              <admst:choose>
#                <admst:when test="[$a1DerivX='0.0']">
#                  <admst:variable name="expressionDerivX" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDerivX" select="deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0*($a1DerivX)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#          </admst:when>
#          <!-- two-argument functions -->
#          <admst:when test="[name='pow' or name='min' or name='max' or name='hypot' or name='atan2']">
#            <admst:apply-templates select="arguments[1]" match="processTerm">
#              <admst:variable name="a1" select="%(returned('returnedExpression')/value)"/>
#              <admst:variable name="a1Deriv" select="%(returned('returnedExpressionDeriv')/value)"/>
#              <admst:variable name="a1Deriv2" select="%(returned('returnedExpressionDeriv2')/value)"/>
#              <admst:variable name="a1Deriv12" select="%(returned('returnedExpressionDeriv12')/value)"/>
#              <admst:variable name="a1DerivX" select="%(returned('returnedExpressionDerivX')/value)"/>
#            </admst:apply-templates>
#            <admst:apply-templates select="arguments[2]" match="processTerm">
#              <admst:variable name="a2" select="%(returned('returnedExpression')/value)"/>
#              <admst:variable name="a2Deriv" select="%(returned('returnedExpressionDeriv')/value)"/>
#              <admst:variable name="a2Deriv2" select="%(returned('returnedExpressionDeriv2')/value)"/>
#              <admst:variable name="a2Deriv12" select="%(returned('returnedExpressionDeriv12')/value)"/>
#              <admst:variable name="a2DerivX" select="%(returned('returnedExpressionDerivX')/value)"/>
#            </admst:apply-templates>
#            <admst:choose>
#              <admst:when test="[$a1Deriv='0.0' and $a2Deriv='0.0']">
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:when>
#              <admst:when test="[$a2Deriv='0.0']">
#                <admst:variable name="expressionDeriv" select="(deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0*($a1Deriv))"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv='0.0']">
#                <admst:variable name="expressionDeriv" select="(deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d1*($a2Deriv))"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv" select="((deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0*($a1Deriv))+(deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d1*($a2Deriv)))"/>
#              </admst:otherwise>
#            </admst:choose>
#            <admst:if test="$derivProbe2">
#              <admst:choose>
#                <admst:when test="[$a1Deriv2='0.0' and $a2Deriv2='0.0']">
#                  <admst:variable name="expressionDeriv2" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a2Deriv2='0.0']">
#                  <admst:variable name="expressionDeriv2" select="(deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0*($a1Deriv2))"/>
#                </admst:when>
#                <admst:when test="[$a1Deriv2='0.0']">
#                  <admst:variable name="expressionDeriv2" select="(deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d1*($a2Deriv2))"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv2" select="((deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0*($a1Deriv2))+(deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d1*($a2Deriv2)))"/>
#                </admst:otherwise>
#              </admst:choose>
#              <!-- general case:  second deriv=
#                   (d2fdy2*a2Deriv + d2fdxdy*a1Deriv)*a2Deriv2
#                  +(d2fdxdy*a2Deriv+  d2fdx2*a1Deriv)*a1Deriv2
#                  +dfdy*a2Deriv12
#                  +dfdx*a1Deriv12
#                -->
#              <admst:choose>
#                <admst:when test="[$a1Deriv='0.0' and $a2Deriv='0.0' and $a1Deriv2='0.0' and $a2Deriv2='0.0' and $a1Deriv12='0.0' and $a2Deriv12='0.0']">
#                  <admst:variable name="expressionDeriv12" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:apply-templates select="." match="twoArgSecondDerivs">
#                    <admst:variable name="d2fdx2" select="%(returned('d2fdx2')/value)"/>
#                    <admst:variable name="d2fdxdy" select="%(returned('d2fdxdy')/value)"/>
#                    <admst:variable name="d2fdy2" select="%(returned('d2fdy2')/value)"/>
#                  </admst:apply-templates>
#                  <admst:variable name="term1" select=""/>
#                  <admst:variable name="term2" select=""/>
#                  <admst:variable name="term3" select=""/>
#                  <admst:variable name="term4" select=""/>
#                  <admst:if test="[not($a2Deriv2='0.0')]">
#                    <admst:if test="[not($a1Deriv='0.0' and $a2Deriv='0.0')]">
#                      <admst:choose>
#                        <admst:when test="[$a1Deriv='0.0']">
#                          <admst:variable name="term1" select="$d2fdy2*$a2Deriv*$a2Deriv2"/>
#                        </admst:when>
#                        <admst:when test="[$a2Deriv='0.0']">
#                          <admst:variable name="term1" select="$d2fdxdy*$a1Deriv*$a2Deriv2"/>
#                        </admst:when>
#                        <admst:otherwise>
#                          <admst:variable name="term1" select="($d2fdy2*$a2Deriv+$d2fdxdy*$a1Deriv)*$a2Deriv2"/>
#                        </admst:otherwise>
#                      </admst:choose>
#                    </admst:if>
#                  </admst:if>
#                  <admst:if test="[not($a1Deriv2='0.0')]">
#                    <admst:if test="[not($a1Deriv='0.0' and $a2Deriv='0.0')]">
#                      <admst:choose>
#                        <admst:when test="[$a1Deriv='0.0']">
#                          <admst:variable name="term2" select="$d2fdxdy*$a2Deriv*$a1Deriv2"/>
#                        </admst:when>
#                        <admst:when test="[$a2Deriv='0.0']">
#                          <admst:variable name="term2" select="$d2fdx2*$a1Deriv*$a1Deriv2"/>
#                        </admst:when>
#                        <admst:otherwise>
#                          <admst:variable name="term2" select="($d2fdxdy*$a2Deriv+$d2fdx2*$a1Deriv)*$a1Deriv2"/>
#                        </admst:otherwise>
#                      </admst:choose>
#                    </admst:if>
#                  </admst:if>
#                  <admst:if test="[not($a2Deriv12='0.0')]">
#                    <admst:variable name="term3" select="$a2Deriv12*deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d1"/>
#                  </admst:if>
#                  <admst:if test="[not($a1Deriv12='0.0')]">
#                    <admst:variable name="term4" select="$a1Deriv12*deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0"/>
#                  </admst:if>
#                  <admst:variable name="expressionDeriv12" select="$term1"/>
#                  <admst:if test="[not($expressionDeriv12='') and not($term2='')]">
#                    <admst:variable name="expressionDeriv12" select="$expressionDeriv12+"/>
#                  </admst:if>
#                  <admst:variable name="expressionDeriv12" select="$expressionDeriv12$term2"/>
#                  <admst:if test="[not($expressionDeriv12='') and not($term3='')]">
#                    <admst:variable name="expressionDeriv12" select="$expressionDeriv12+"/>
#                  </admst:if>
#                  <admst:variable name="expressionDeriv12" select="$expressionDeriv12$term3"/>
#                  <admst:if test="[not($expressionDeriv12='') and not($term4='')]">
#                    <admst:variable name="expressionDeriv12" select="$expressionDeriv12+"/>
#                  </admst:if>
#                  <admst:variable name="expressionDeriv12" select="$expressionDeriv12$term4"/>
#                  <admst:choose>
#                    <admst:when test="[$expressionDeriv12='']">
#                      <admst:variable name="expressionDeriv12" select="0.0"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="expressionDeriv12" select="($expressionDeriv12)"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#            <admst:if test="[$globalCurrentScope='sensitivity' and (exists(arguments[1]/#Pdependent) or exists(arguments[2]/#Pdependent))]">
#              <admst:choose>
#                <admst:when test="[$a1DerivX='0.0' and $a2DerivX='0.0']">
#                  <admst:variable name="expressionDerivX" select="0.0"/>
#                </admst:when>
#                <admst:when test="[$a2DerivX='0.0']">
#                  <admst:variable name="expressionDerivX" select="(deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0*($a1DerivX))"/>
#                </admst:when>
#                <admst:when test="[$a1DerivX='0.0']">
#                  <admst:variable name="expressionDerivX" select="(deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d1*($a2DerivX))"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDerivX" select="((deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d0*($a1DerivX))+(deriv_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.))_d1*($a2DerivX)))"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#          </admst:when>
#          <admst:otherwise>
#            <admst:variable name="thisFunctionCall" path="."/>
#            <admst:if test="[class!='analog']">
#              <admst:warning format="Do not know how to differentiate function %(name).  Code will be wrong!\n"/>
#              <admst:variable name="expressionDeriv" select="FIXME/*derivatives for %(name) not implemented*/"/>
#              <admst:variable name="expressionDeriv2" select="FIXME/*derivatives for %(name) not implemented*/"/>
#              <admst:variable name="expressionDeriv12" select="FIXME/*derivatives for %(name) not implemented*/"/>
#              <admst:variable name="expressionDerivX" select="FIXME/*derivatives for %(name) not implemented*/"/>
#            </admst:if>
#            <admst:variable name="argsDep" select="no"/>
#            <admst:variable name="argsDep2" select="no"/>
#            <admst:variable name="argsDepX" select="no"/>
#            <admst:if test="[definition/datatypename='analogfunction']">
#              <admst:if test="[exists(definition/variable[(output='yes') and (name!=$thisFunctionCall/name)])]">
#                <!-- <admst:message format="Called analog function has output variables other than return value, pretending args have dependencies.\n"/> -->
#                <admst:variable name="argsDep" value="yes"/>
#              </admst:if>
#            </admst:if>
#            <admst:variable name="args" value=""/>
#            <admst:variable name="dargs" value=""/>
#            <admst:variable name="dargs2" value=""/>
#            <admst:variable name="dargsX" value=""/>
#            <admst:for-each select="arguments">
#              <admst:if test="[not($args='')]">
#                <admst:variable name="args" value="$(args),"/>
#              </admst:if>
#              <admst:if test="[not($dargs='')]">
#                <admst:variable name="dargs" value="$(dargs),"/>
#              </admst:if>
#              <admst:if test="[not($dargs2='')]">
#                <admst:variable name="dargs2" value="$(dargs2),"/>
#              </admst:if>
#              <admst:if test="[not($dargsX='')]">
#                <admst:variable name="dargsX" value="$(dargsX),"/>
#              </admst:if>
#              <admst:apply-templates select="." match="processTerm">
#                <admst:variable name="args" select="$(args)%(returned('returnedExpression')/value)"/>
#                <admst:variable name="aDeriv" select="%(returned('returnedExpressionDeriv')/value)"/>
#                <admst:variable name="aDeriv2" select="%(returned('returnedExpressionDeriv2')/value)"/>
#                <admst:variable name="aDerivX" select="%(returned('returnedExpressionDerivX')/value)"/>
#                <admst:if test="[$aDeriv != '0.0']">
#                  <admst:variable name="argsDep" select="yes"/>
#                </admst:if>
#                <admst:if test="[$aDeriv2 != '0.0']">
#                  <admst:variable name="argsDep2" select="yes"/>
#                </admst:if>
#                <admst:if test="[$aDerivX != '0.0']">
#                  <admst:variable name="argsDepX" select="yes"/>
#                </admst:if>
#                <admst:variable name="dargs" select="$(dargs)$(aDeriv)"/>
#                <admst:variable name="dargs2" select="$(dargs2)$(aDeriv2)"/>
#                <admst:variable name="dargsX" select="$(dargsX)$(aDerivX)"/>
#              </admst:apply-templates>
#            </admst:for-each>
#            <admst:choose>
#              <admst:when test="[$argsDep = 'no']">
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv" select="evaluator_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.)).getDerivs($args,$dargs)"/>
#              </admst:otherwise>
#            </admst:choose>
#            <admst:if test="$derivProbe2">
#              <admst:choose>
#                <admst:when test="[$argsDep2 = 'no']">
#                  <admst:variable name="expressionDeriv2" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDeriv2" select="evaluator_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.)).getDerivs($args,$dargs2)"/>
#                </admst:otherwise>
#              </admst:choose>
#
#              <!-- It is not necessarily an error that we can't do
#                   these, it's only a problem if the derivatives are
#                   actually needed, and we don't know this yet -->
#              <admst:variable name="expressionDeriv12" select="0.0/*second derivatives of analog functions not implemented*/"/>
#            </admst:if>
#            <admst:if test="[$globalCurrentScope='sensitivity']">
#              <admst:choose>
#                <admst:when test="[$argsDepX = 'no']">
#                  <admst:variable name="expressionDerivX" select="0.0"/>
#                </admst:when>
#                <admst:otherwise>
#                  <admst:variable name="expressionDerivX" select="evaluator_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.)).getDerivs($args,$dargsX)"/>
#                </admst:otherwise>
#              </admst:choose>
#            </admst:if>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:otherwise>
#    </admst:choose>
#    <admst:return name="returnedExpression" value="$expression"/>
#
#    <admst:return name="returnedExpressionDeriv" value="$expressionDeriv"/>
#    <admst:return name="returnedExpressionDeriv2" value="$expressionDeriv2"/>
#    <admst:return name="returnedExpressionDeriv12" value="$expressionDeriv12"/>
#    <admst:return name="returnedExpressionDerivX" value="$expressionDerivX"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   functionCall
#     This template was what our old back-end called when a function
#     call was found, via the %(adms/datatype) template match.  Now
#     that we're doing precomputation of function evaluation, we have
#     do do something simpler in the "function" template, and
#     have this one for the real work
#   =================================================================-
#  -->
#  <admst:template match="functionCall">
#    <admst:choose>
#      <admst:when test="[name='min']">
#        <admst:variable name="expression" select="std::min"/>
#        <admst:variable name="args" select=""/>
#        <admst:for-each select="arguments">
#          <admst:if test="[$args!='']">
#            <admst:variable name="args" select="$args,"/>
#          </admst:if>
#          <admst:apply-templates select="." match="realArgument">
#            <admst:variable name="args" select="$args%(returned('argval')/value)"/>
#          </admst:apply-templates>
#        </admst:for-each>
#        <admst:variable name="expression" select="$expression($args)"/>
#      </admst:when>
#      <admst:when test="[name='max']">
#        <admst:variable name="expression" select="std::max"/>
#        <admst:variable name="args" select=""/>
#        <admst:for-each select="arguments">
#          <admst:if test="[$args!='']">
#            <admst:variable name="args" select="$args,"/>
#          </admst:if>
#          <admst:apply-templates select="." match="realArgument">
#            <admst:variable name="args" select="$args%(returned('argval')/value)"/>
#          </admst:apply-templates>
#        </admst:for-each>
#        <admst:variable name="expression" select="$expression($args)"/>
#      </admst:when>
#      <admst:when test="[name='absdelay']">
#        <admst:apply-templates select="arguments[1]" match="processTerm">
#          <admst:variable name="expression" select="FIXMEabsdelay(%(returned('returnedExpression')/value))"/>
#        </admst:apply-templates>
#      </admst:when>
#      <!-- DDT is a null function in Xyce we'll load such things into
#           dynamic contributions, and those will be differentiated elsewhere -->
#      <admst:when test="[name='ddt']">
#        <admst:apply-templates select="arguments[1]" match="processTerm">
#          <admst:variable name="expression" select="(%(returned('returnedExpression')/value))"/>
#        </admst:apply-templates>
#      </admst:when>
#      <admst:when test="[name='\$given' or name='\$param_given']">
#        <admst:variable name="arg1" select="%(arguments[1])"/>
#        <admst:assert test="$arg1[datatypename='variable' and input='yes']" format="%(name): argument is not a parameter\n"/>
#        <admst:choose>
#          <admst:when test="$arg1/[parametertype='model']">
#            <admst:choose>
#              <admst:when test="[$globalCurrentScope = 'model']">
#                <admst:variable name="expression" select="given(&quot;$arg1&quot;)"/>
#              </admst:when>
#              <admst:when test="[$globalCurrentScope = 'instance']">
#                <admst:variable name="expression" select="(model_.given(&quot;$arg1&quot;))"/>
#              </admst:when>
#              <admst:when test="[$globalCurrentScope = 'sensitivity']">
#                <admst:variable name="expression" select="modelStruct.modelPar_given_$arg1"/>
#              </admst:when>
#            </admst:choose>
#          </admst:when>
#          <admst:when test="$arg1/[parametertype='instance']">
#            <admst:choose>
#              <admst:when test="[$globalCurrentScope = 'instance']">
#                <admst:variable name="expression" select="given(&quot;$arg1&quot;)"/>
#              </admst:when>
#              <admst:when test="[$globalCurrentScope = 'sensitivity']">
#                <admst:variable name="expression" select="instanceStruct.instancePar_given_$arg1"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:fatal format="Attempt to use \$given() on an instance variable outside of instance scope\n"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:when>
#          <admst:otherwise>
#            <admst:fatal format="%(name): should not be reached\n"/>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[name='\$temperature']">
#        <admst:assert test="[nilled(arguments)]" format="%(name): should not have arguments\n"/>
#        <admst:choose>
#          <admst:when test="[$globalCurrentScope='instance' or $globalCurrentScope='sensitivity']">
#            <admst:variable name="expression" select="admsTemperature"/>
#          </admst:when>
#          <!-- KLUDGE!!!!!! -->
#          <!-- Assumes that when at model scope, $temperature is taken as
#               the default temperature of the simulator. -->
#          <!-- At instance scope, we use whatever Xyce passed in to
#               updateTemperature for that instance. -->
#          <admst:when test="[$globalCurrentScope='model']">
#            <admst:variable name="expression" select="admsModTemp"/>
#          </admst:when>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[name='\$mfactor']">
#        <admst:assert test="[nilled(arguments)]" format="%(name): should not have arguments\n"/>
#        <admst:variable name="expression" select="FIXME_MFACTOR"/>
#      </admst:when>
#      <admst:when test="[name='\$vt']">
#        <admst:choose>
#          <admst:when test="[nilled(arguments)]">
#            <admst:variable name="expression" select="adms_vt_nom"/>
#          </admst:when>
#          <admst:when test="arguments[count(.)=1]">
#            <admst:apply-templates select="arguments[1]" match="processTerm">
#              <admst:variable name="expression" select="adms_vt(%(returned('returnedExpression')/value))"/>
#            </admst:apply-templates>
#          </admst:when>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[name='\$scale']">
#        <admst:assert test="[nilled(arguments)]" format="%(name): should not have arguments\n"/>
#        <admst:variable name="expression" select="FIXME_scale"/>
#      </admst:when>
#      <admst:when test="[name='\$abstime' or name='\$realtime']">
#        <admst:assert test="[nilled(arguments)]" format="%(name): should not have arguments\n"/>
#          <admst:choose>
#            <admst:when test="[$globalCurrentScope='sensitivity']">
#              <admst:variable name="expression" select="theInstance.getSolverState().currTime_"/>
#            </admst:when>
#            <admst:otherwise>
#              <admst:variable name="expression" select="getSolverState().currTime_"/>
#            </admst:otherwise>
#          </admst:choose>
#      </admst:when>
#      <admst:when test="[name='ddx']">
#        <admst:assert test="arguments[count(.)=2]" format="%(name): should have two arguments exactly\n"/>
#        <admst:assert test="arguments[2]/adms[datatypename='probe']" format="%(name): second argument is not a probe\n"/>
#        <admst:variable name="expression" select="FIXME: ddx(%(arguments[1]),%(arguments[2]))"/>
#      </admst:when>
#      <admst:when test="[name='floor']">
#        <admst:assert test="arguments[count(.)=1]" format="%(name): should have one argument exactly\n"/>
#        <admst:apply-templates select="arguments[1]" match="processTerm">
#          <admst:variable name="expression" select="%(returned('returnedExpression')/value)"/>
#          <admst:variable name="expression" select="floor($expression)"/>
#        </admst:apply-templates>
#      </admst:when>
#      <admst:when test="[name='ceil']">
#        <admst:assert test="arguments[count(.)=1]" format="%(name): should have one argument exactly\n"/>
#        <admst:apply-templates select="arguments[1]" match="processTerm">
#          <admst:variable name="expression" select="%(returned('returnedExpression')/value)"/>
#          <admst:variable name="expression" select="ceil($expression)"/>
#        </admst:apply-templates>
#      </admst:when>
#      <admst:when test="[name='\$simparam']">
#        <admst:choose>
#          <admst:when test="[arguments[1]/datatypename='string' and arguments[1]/value='gmin']">
#            <admst:choose>
#              <admst:when test="[$globalCurrentScope='sensitivity']">
#                <admst:variable name="expression" select="ADMSgmin_arg"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expression" select="getDeviceOptions().gmin"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:when>
#          <admst:otherwise>
#            <admst:assert test="arguments[count(.)=2]" format="Unrecognized simparam %(arguments[1]) and no expression provided.\n"/>
#            <admst:apply-templates select="arguments[2]" match="processTerm">
#              <admst:variable name="expression" select="%(returned('returnedExpression')/value)"/>
#            </admst:apply-templates>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[name='hypot']">
#        <admst:assert test="arguments[count(.)=2]" format="hypot function must take exactly two arguments.\n"/>
#        <admst:variable name="expression" value="sqrt"/>
#        <admst:variable name="args" select=""/>
#        <admst:for-each select="arguments">
#          <admst:if test="[$args!='']">
#            <admst:variable name="args" select="$args+"/>
#          </admst:if>
#          <admst:apply-templates select="." match="processTerm">
#            <admst:variable name="args" select="$args%(returned('returnedExpression')/value)*%(returned('returnedExpression')/value)"/>
#          </admst:apply-templates>
#        </admst:for-each>
#        <admst:variable name="expression" select="$expression($args)"/>
#      </admst:when>
#      <admst:when test="[name='ln' or name='log' or name='sqrt']">
#        <admst:variable name="expression" select="%(funcname(.)/[name='fname']/value)"/>
#        <admst:variable name="args" select=""/>
#        <admst:for-each select="arguments">
#          <admst:if test="[$args!='']">
#            <admst:variable name="args" select="$args,"/>
#          </admst:if>
#          <admst:apply-templates select="." match="realArgument">
#            <admst:variable name="args" select="$args%(returned('argval')/value)"/>
#          </admst:apply-templates>
#        </admst:for-each>
#        <admst:variable name="expression" select="$expression($args)"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:variable name="expression" select="%(funcname(.)/[name='fname']/value)"/>
#        <admst:variable name="args" select=""/>
#        <admst:for-each select="arguments">
#          <admst:if test="[$args!='']">
#            <admst:variable name="args" select="$args,"/>
#          </admst:if>
#          <admst:apply-templates select="." match="processTerm">
#            <admst:variable name="args" select="$args%(returned('returnedExpression')/value)"/>
#          </admst:apply-templates>
#        </admst:for-each>
#        <admst:variable name="expression" select="$expression($args)"/>
#      </admst:otherwise>
#    </admst:choose>
#    <admst:return name="returnedExpression" value="$expression"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   analogFunctionEvaluatorConstruction
#     This is very much like functionCall, but is only used when
#     generating precomptation for analog functions, so it is simpler.
#   =================================================================-
#  -->
#  <admst:template match="analogFunctionEvaluatorConstruction">
#    <admst:variable name="expression" select="AnalogFunctions::%(funcnameSimple(.)/[name='fname']/value)Evaluator evaluator_%(funcnameSimple(.)/[name='fname']/value)_%(index(../function,.))"/>
#    <admst:variable name="args" select=""/>
#    <admst:for-each select="arguments">
#      <admst:if test="[$args!='']">
#        <admst:variable name="args" select="$args,"/>
#      </admst:if>
#      <admst:apply-templates select="." match="processTerm">
#        <admst:variable name="args" select="$args%(returned('returnedExpression')/value)"/>
#      </admst:apply-templates>
#    </admst:for-each>
#    <admst:variable name="expression" select="$expression($args)"/>
#    <admst:return name="returnedExpression" value="$expression"/>
#  </admst:template>
#  <!--
#   =================================================================-
#   string
#   format a string for output
#   =================================================================-
#  -->
#  <admst:template match="string">
#    <admst:return name="returnedExpression" value="&quot;%(value)&quot;"/>
#    <admst:return name="returnedExpressionDeriv" value="0.0"/>
#    <admst:return name="returnedExpressionDeriv2" value="0.0"/>
#    <admst:return name="returnedExpressionDeriv12" value="0.0"/>
#    <admst:return name="returnedExpressionDerivX" value="0.0"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   conditional
#   output if/then/else
#   =================================================================-
#  -->
#  <admst:template match="conditional">
#    <admst:assert test="adms[datatypename='conditional']" format="conditional template called on something other than conditional\n"/>
#
#    <admst:variable name="saveSkipFunctionPrecomp" select="$skipFunctionPrecomp"/>
#    <admst:variable name="skipFunctionPrecomp" select="y"/>
#    <admst:text format="if (%(printTerm(if)))\n"/>
#    <admst:variable name="skipFunctionPrecomp" select="$saveSkipFunctionPrecomp"/>
#    <!-- blocks will print their own braces, but we always want them -->
#    <admst:text select="then/adms[datatypename!='block']" format="{\n"/>
#    <admst:apply-templates select="then" match="%(adms/datatypename)"/>
#    <!-- blocks will print their own braces, but we always want them -->
#    <admst:text select="then/adms[datatypename!='block']"  format="}\n"/>
#    <admst:if test="else">
#      <admst:text format="else\n"/>
#      <admst:text select="else/adms[datatypename!='block']" format="{\n"/>
#      <admst:apply-templates select="else" match="%(adms/datatypename)"/>
#      <admst:text select="else/adms[datatypename!='block']"  format="}\n"/>
#    </admst:if>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   block
#   output block
#   =================================================================-
#  -->
#  <admst:template match="block">
#    <admst:assert test="adms[datatypename='block']" format="block template called on something other than block\n"/>
#    <admst:text select="[name!='']" format="//Begin block %(name)\n"/>
#    <admst:text format="{\n"/>
#    <admst:apply-templates select="item" match="%(adms/datatypename)"/>
#    <admst:text format="}\n"/>
#    <admst:text select="[name!='']" format="// End block %(name)\n"/>
#  </admst:template>
#
#
#  <!--
#   =================================================================-
#   blockvariable
#     declare block-local variables
#   =================================================================-
#  -->
#  <admst:template match="blockvariable">
#    <admst:text format="//Block-local variables for block %(block/name)\n"/>
#    <admst:for-each select="variable">
#      <admst:if test="[$globalCurrentScope='sensitivity']">
#        <admst:apply-templates select="." match="collectParamDependence"/>
#      </admst:if>
#      <admst:apply-templates select="." match="xyceDeclareVariable"/>
#    </admst:for-each>
#    <admst:text format="//End of Block-local variables\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   nilled
#   do nothing, when nothing is found
#   =================================================================-
#  -->
#  <admst:template match="nilled">
#  </admst:template>
#
#  <!--
#   =================================================================-
#   whileloop
#   output while loop
#   =================================================================-
#  -->
#  <admst:template match="whileloop">
#    <admst:variable name="saveSkipFunctionPrecomp" select="$skipFunctionPrecomp"/>
#    <admst:variable name="skipFunctionPrecomp" select="y"/>
#    <admst:text format="while (%(printTerm(while)))\n"/>
#    <admst:variable name="skipFunctionPrecomp" select="$saveSkipFunctionPrecomp"/>
#    <admst:text select="whileblock/adms[datatypename!='block']" format="{\n"/>
#    <admst:apply-templates select="whileblock" match="%(adms/datatypename)"/>
#    <admst:text select="whileblock/adms[datatypename!='block']" format="}\n"/>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   forloop
#   output for   loop
#   =================================================================-
#  -->
#  <admst:template match="forloop">
#    <admst:text format="for ("/>
#    <admst:text format="%(printTerm(initial/lhs))=%(printTerm(initial/rhs));"/>
#    <admst:text format="%(printTerm(condition));"/>
#    <admst:text format="%(printTerm(update/lhs))=%(printTerm(update/rhs)) )"/>
#    <admst:text select="forblock/adms[datatypename!='block']" format="{\n"/>
#    <admst:apply-templates select="forblock" match="%(adms/datatypename)"/>
#    <admst:text select="forblock/adms[datatypename!='block']" format="}\n"/>
#  </admst:template>
#  <!--
#   =================================================================-
#   case
#   output "case" statement
#   =================================================================-
#  -->
#  <admst:template match="case">
#    <admst:variable name="casecondition" path="case/tree"/>
#    <admst:variable name="havedefault" select="no"/>
#    <admst:if test="[count(caseitem[defaultcase='yes']) >0]">
#      <admst:variable name="havedefault" select="yes"/>
#    </admst:if>
#
#    <admst:for-each select="caseitem[defaultcase='no']">
#      <admst:text format="if ( "/>
#      <admst:join select="condition" separator="||">
#	<admst:apply-templates select="." match="%(datatypename)">
#	  <admst:text format="%(printTerm($casecondition)) == (%(returned('returnedExpression')/value))"/>
#	</admst:apply-templates>
#      </admst:join>
#      <admst:text format=")\n"/>
#      <admst:if test="[code/datatypename!='block']">
#        <admst:text format="{\n"/>
#      </admst:if>
#      <admst:apply-templates select="code" match="%(datatypename)" required="yes"/>
#      <admst:if test="[code/datatypename!='block']">
#        <admst:text format="}\n"/>
#      </admst:if>
#      <admst:text format="else\n"/>
#    </admst:for-each>
#    <admst:text select="[$havedefault='no']" format="{\n // no default\n}\n"/>
#    <admst:for-each select="caseitem[defaultcase='yes']">
#      <admst:apply-templates select="code" match="%(datatypename)" required="yes"/>
#    </admst:for-each>
#  </admst:template>
#
#
#  <!--
#   =================================================================-
#   formatted_range
#   Given a variable node, print out its range in a nicely formatted
#   way, with open or closed bounds indicated.
#   This is for pretty printing such as for HTML, not code generation.
#   =================================================================-
#  -->
#  <admst:template match="formatted_range">
#    <admst:choose>
#      <admst:when test="[nilled(range)]">
#        <admst:text format="No Range Specified"/>
#      </admst:when>
#      <admst:when test="[name!='pnp' and name!='npn']">
#        <admst:apply-templates select="range" match="formatted_range2"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:text format="Positive range"/>
#      </admst:otherwise>
#    </admst:choose>
#  </admst:template>
#
#  <!--
#   =================================================================-
#   formatted_range2
#   the actual guts of formatted range, but this one takes a single
#   range node of the tree, not a variable (which can have multiple
#   ranges
#   =================================================================-
#  -->
#<admst:template match="formatted_range2">
#  <admst:choose>
#    <admst:when test="infexpr[hasspecialnumber='YES']">
#      <admst:text format=" ] %(infexpr) "/>
#    </admst:when>
#    <admst:otherwise>
#      <admst:choose>
#        <admst:when test="[infboundtype='range_bound_include']">
#          <admst:text format="[ "/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:text format="] "/>
#        </admst:otherwise>
#      </admst:choose>
#      <admst:apply-templates select="infexpr" match="printTerm"/>
#      <admst:text format=", "/>
#    </admst:otherwise>
#  </admst:choose>
#  <admst:choose>
#    <admst:when test="supexpr[hasspecialnumber='YES']">
#      <admst:text format=" %(supexpr) ["/>
#    </admst:when>
#    <admst:otherwise>
#      <admst:apply-templates select="supexpr" match="printTerm"/>
#      <admst:choose>
#	<admst:when test="[supboundtype='range_bound_include']">
#	  <admst:text format=" ]"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:text format=" ["/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:otherwise>
#  </admst:choose>
#</admst:template>
#
#  <!--
#   =================================================================-
#   rangeCondition
#   Given a range, generate the C++ condition that checks if it's
#   exceeded/violated
#   =================================================================-
#  -->
#
#<admst:template match="rangeCondition">
#  <admst:choose>
#    <admst:when test="[infexpr/hasspecialnumber='YES' and supexpr/hasspecialnumber='YES']">
#      <admst:return name="doNothing" value="yes"/>
#    </admst:when>
#    <admst:otherwise>
#      <admst:variable name="returnCondition" select="("/>
#      <!-- Lower bound -->
#      <admst:if test="infexpr[hasspecialnumber!='YES']">
#        <admst:variable name="returnCondition" select="$returnCondition%(../name) &gt;"/>
#        <admst:if test="[infboundtype='range_bound_include']">
#          <admst:variable name="returnCondition" select="$returnCondition="/>
#        </admst:if>
#        <admst:variable name="returnCondition" select="$returnCondition%(processTerm(infexpr)/[name='returnedExpression']/value)"/>
#        <admst:if test="supexpr[hasspecialnumber!='YES']">
#          <admst:variable name="returnCondition" select="$returnCondition &amp;&amp; "/>
#        </admst:if>
#      </admst:if>
#
#      <!-- upper bound -->
#      <admst:if test="supexpr[hasspecialnumber!='YES']">
#        <admst:variable name="returnCondition" select="$returnCondition%(../name) &lt;"/>
#        <admst:if test="[supboundtype='range_bound_include']">
#          <admst:variable name="returnCondition" select="$returnCondition="/>
#        </admst:if>
#        <admst:variable name="returnCondition" select="$returnCondition%(processTerm(supexpr)/[name='returnedExpression']/value) "/>
#      </admst:if>
#      <admst:variable name="returnCondition" select="$returnCondition)"/>
#
#      <!-- now decide whether this is an include condition or exclude: -->
#      <admst:if test="[type='include']">
#        <admst:variable name="returnCondition" select="!($returnCondition)"/>
#      </admst:if>
#      <admst:return name="doNothing" value="no"/>
#      <admst:return name="returnCondition" value="$returnCondition"/>
#    </admst:otherwise>
#  </admst:choose>
#</admst:template>
#
#  <!--
#   =================================================================-
#   check_range
#   Given a variable node, generate code to check the variable against
#   the range.
#
#   The range of the variable is assumed non-nilled, so the caller
#   must check first before calling this.
#   =================================================================-
#  -->
#
#<admst:template match="check_range">
#  <admst:choose>
#    <!-- first special case: both upper and lower are special, meaning that
#         there really is no range to bother checking -->
#    <admst:when test="[range/infexpr/hasspecialnumber='YES' and range/supexpr/hasspecialnumber='YES']">
#      <!-- do nothing -->
#    </admst:when>
#    <admst:otherwise>
#      <!-- we have a range to check -->
#      <admst:text format="  if ( "/>
#      <admst:text format="("/>
#      <!-- there may be several ranges specified, some included, some excluded.
#           gotta be careful -->
#      <admst:join select="range[infexpr/hasspecialnumber!='YES' or supexpr/hasspecialnumber!='YES']" separator=" || ">
#        <admst:apply-templates select="." match="rangeCondition">
#          <admst:text format="%(returned('returnCondition')/value)"/>
#        </admst:apply-templates>
#      </admst:join>
#      <admst:text format=") )\n  {\n    UserWarning(*this) &lt;&lt; &quot;$nameSpace: Parameter %(name) value &quot; &lt;&lt; %(name) &lt;&lt; &quot; "/>
#      <admst:join select="range" separator=" or ">
#        <admst:text select="[type='include']" format="out of range"/>
#        <admst:text select="[type='exclude']" format="in excluded range"/>
#        <admst:text format=" %(formatted_range2(.))"/>
#      </admst:join>
#      <admst:text format="&quot;;\n  }\n"/>
#    </admst:otherwise>
#  </admst:choose>
#</admst:template>
#
#<!-- map binary operators onto C++ symbols -->
#<admst:template match="bname">
#  <admst:choose>
#    <admst:when test="[name='bw_equr']">
#      <admst:return name="bname" value="^~"/>
#    </admst:when>
#    <admst:when test="[name='bw_equl']">
#      <admst:return name="bname" value="~^"/>
#    </admst:when>
#    <admst:when test="[name='bw_xor']">
#      <admst:return name="bname" value="^"/>
#    </admst:when>
#    <admst:when test="[name='bw_or']">
#      <admst:return name="bname" value="|"/>
#    </admst:when>
#    <admst:when test="[name='bw_and']">
#      <admst:return name="bname" value="&amp;"/>
#    </admst:when>
#    <admst:when test="[name='or']">
#      <admst:return name="bname" value="||"/>
#    </admst:when>
#    <admst:when test="[name='and']">
#      <admst:return name="bname" value="&amp;&amp;"/>
#    </admst:when>
#    <admst:when test="[name='equ']">
#      <admst:return name="bname" value="=="/>
#    </admst:when>
#    <admst:when test="[name='notequ']">
#      <admst:return name="bname" value="!="/>
#    </admst:when>
#    <admst:when test="[name='lt']">
#      <admst:return name="bname" value="&lt;"/>
#    </admst:when>
#    <admst:when test="[name='lt_equ']">
#      <admst:return name="bname" value="&lt;="/>
#    </admst:when>
#    <admst:when test="[name='gt']">
#      <admst:return name="bname" value="&gt;"/>
#    </admst:when>
#    <admst:when test="[name='gt_equ']">
#      <admst:return name="bname" value="&gt;="/>
#    </admst:when>
#    <admst:when test="[name='shiftr']">
#      <admst:return name="bname" value="&gt;&gt;"/>
#    </admst:when>
#    <admst:when test="[name='shiftl']">
#      <admst:return name="bname" value="&lt;&lt;"/>
#    </admst:when>
#    <admst:when test="[name='multmod']">
#      <admst:return name="bname" value="%"/>
#    </admst:when>
#    <admst:otherwise>
#      <admst:fatal format="variable type %(name) unknown\n"/>
#    </admst:otherwise>
#  </admst:choose>
#</admst:template>
#
#<admst:template match="funcname">
#  <admst:choose>
#    <admst:when test="[name='abs']">
#      <admst:variable name="expression" select="fabs"/>
#    </admst:when>
#    <admst:when test="[name='\$shrinkl']">
#      <admst:variable name="expression" select="shrinkl"/>
#    </admst:when>
#    <admst:when test="[name='\$shrinka']">
#      <admst:variable name="expression" select="shrinka"/>
#    </admst:when>
#    <admst:when test="[name='log']">
#      <admst:variable name="expression" select="(1.0/log(10.0))*log"/>
#    </admst:when>
#    <admst:when test="[name='ln']">
#      <admst:variable name="expression" select="log"/>
#    </admst:when>
#    <admst:when test="[name='limexp']">
#      <admst:variable name="expression" select="limexp"/>
#    </admst:when>
#    <admst:when test="[name='\$limexp']">
#      <admst:variable name="expression" select="limexp"/>
#    </admst:when>
#    <admst:otherwise>
#      <admst:choose>
#        <admst:when test="[$globalMustUseTemplate='no' or class!='analog']">
#          <admst:choose>
#            <admst:when test="[class='analog']">
#              <admst:choose>
#                <admst:when test="[$globalCurrentScope!='AF']">
#                  <admst:choose>
#                    <admst:when test="[$skipFunctionPrecomp != 'y']">
#                      <admst:variable name="expression" select="evaluator_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.)).getValues"/>
#                    </admst:when>
#                    <admst:otherwise>
#                      <admst:variable name="expression" select="AnalogFunctions::%(name)"/>
#                    </admst:otherwise>
#                  </admst:choose>
#                </admst:when>
#                <admst:when test="[$globalCurrentScope='AF']">
#                  <admst:variable name="expression" select="%(name)"/>
#                </admst:when>
#              </admst:choose>
#            </admst:when>
#            <admst:otherwise>
#              <admst:variable name="expression" select="%(name)"/>
#            </admst:otherwise>
#          </admst:choose>
#        </admst:when>
#        <admst:otherwise>
#          <!-- globalMustUseTemplate=yes, apparently -->
#          <admst:choose>
#            <admst:when test="[class='analog']">
#              <!-- analog functions are in their own class, and the model
#                   class has an instance of that. -->
#              <admst:choose>
#                <!-- if we're in the AF class, these functions are accessible
#                     just by their names -->
#                <admst:when test="[$globalCurrentScope='AF']">
#                  <admst:variable name="expression" select="%(name)&lt;WRONG&gt;"/>
#                </admst:when>
#                <admst:when test="[$globalCurrentScope='model' or $globalCurrentScope='instance' or $globalCurrentScope='sensitivity']">
#                  <admst:variable name="expression" select="evaluator_%(funcnameSimple(.)/[name='fname']/value)_%(index(subexpression/expression/function,.)).getValues"/>
#                </admst:when>
#              </admst:choose>
#            </admst:when>
#            <admst:otherwise>
#              <admst:variable name="expression" select="%(name)"/>
#            </admst:otherwise>
#          </admst:choose>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:otherwise>
#  </admst:choose>
#  <admst:return name="fname" value="$expression"/>
#</admst:template>
#
#<!-- This template returns the second derivative of one-argument
#     builtin functions with respect to their argument -->
#<admst:template match="oneArgSecondDeriv">
#  <!-- set this to a complete bogon return value, so it becomes
#       a compilation error if we ever emerge from this function
#       without setting it properly -->
#  <admst:variable name="d2fdx2" select="fixme"/>
#  <admst:apply-templates select="arguments[1]" match="processTerm">
#    <admst:variable name="a1" select="%(returned('returnedExpression')/value)"/>
#  </admst:apply-templates>
#  <admst:choose>
#    <admst:when test="[name='exp']">
#      <admst:variable name="d2fdx2" select="exp($a1)"/>
#    </admst:when>
#    <admst:when test="[name='ln']">
#      <admst:variable name="d2fdx2" select="(-1.0/$a1/$a1)"/>
#    </admst:when>
#    <admst:when test="[name='log']">
#      <admst:variable name="d2fdx2" select="(-1.0/$a1/$a1/log(10.0))"/>
#    </admst:when>
#    <admst:when test="[name='sqrt']">
#      <admst:variable name="d2fdx2" select="(-0.25/$a1/sqrt($a1))"/>
#    </admst:when>
#    <admst:when test="[name='abs']">
#      <admst:variable name="d2fdx2" select="0.0"/>
#    </admst:when>
#    <admst:when test="[name='limexp']">
#      <admst:variable name="d2fdx2" select="((($a1)&lt;80)?exp($a1):0.0)"/>
#    </admst:when>
#    <admst:when test="[name='cos']">
#      <admst:variable name="d2fdx2" select="(-cos($a1))"/>
#    </admst:when>
#    <admst:when test="[name='sin']">
#      <admst:variable name="d2fdx2" select="(-sin($a1))"/>
#    </admst:when>
#    <admst:when test="[name='tan']">
#      <admst:variable name="d2fdx2" select="2.0*tan($a1)/cos($a1)/cos($a1)"/>
#    </admst:when>
#    <admst:when test="[name='acos']">
#      <admst:variable name="d2fdx2" select="(-$a1/(1-$a1*$a1)/sqrt(1-$a1*$a1))"/>
#    </admst:when>
#    <admst:when test="[name='asin']">
#      <admst:variable name="d2fdx2" select="($a1/(1-$a1*$a1)/sqrt(1-$a1*$a1))"/>
#    </admst:when>
#    <admst:when test="[name='atan']">
#      <admst:variable name="d2fdx2" select="(-2.0*$a1/($a1*$a1+1)/($a1*$a1+1))"/>
#    </admst:when>
#    <admst:when test="[name='cosh']">
#      <admst:variable name="d2fdx2" select="cosh($a1)"/>
#    </admst:when>
#    <admst:when test="[name='sinh']">
#      <admst:variable name="d2fdx2" select="sinh($a1)"/>
#    </admst:when>
#    <admst:when test="[name='tanh']">
#      <admst:variable name="d2fdx2" select="(-2*tanh($a1)/cosh($a1)/cosh($a1))"/>
#    </admst:when>
#    <admst:when test="[name='acosh']">
#      <admst:variable name="d2fdx2" select="(-$a1/($a1*$a1-1)/sqrt($a1*$a1-1))"/>
#    </admst:when>
#    <admst:when test="[name='asinh']">
#      <admst:variable name="d2fdx2" select="(-$a1/($a1*$a1+1)/sqrt($a1*$a1+1))"/>
#    </admst:when>
#    <admst:when test="[name='atanh']">
#      <admst:variable name="d2fdx2" select="2.0*$a1/(1-$a1*$a1)/(1-$a1*$a1)"/>
#    </admst:when>
#  </admst:choose>
#
#  <admst:return name="d2fdx2" value="$d2fdx2"/>
#</admst:template>
#
#<!-- This template returns the second derivatives of two-argument
#     builtin functions with respect to their arguments -->
#<admst:template match="twoArgSecondDerivs">
#  <admst:variable name="d2fdx2" select="0.0"/>
#  <admst:variable name="d2fdxdy" select="0.0"/>
#  <admst:variable name="d2fdy2" select="0.0"/>
#  <admst:choose>
#    <admst:when test="[name='pow']">
#      <admst:apply-templates select="arguments[1]" match="processTerm">
#        <admst:variable name="a1" select="%(returned('returnedExpression')/value)"/>
#      </admst:apply-templates>
#      <admst:apply-templates select="arguments[2]" match="processTerm">
#        <admst:variable name="a2" select="%(returned('returnedExpression')/value)"/>
#      </admst:apply-templates>
#      <admst:variable name="d2fdx2" select="(($a1==0.0)?0.0:$a2*($a2-1)*pow($a1,$a2)/$a1/$a1)"/>
#      <admst:variable name="d2fdxdy" select="(($a1==0.0)?0.0:(1+$a2*log($a1))*pow($a1,$a2)/$a1)"/>
#      <admst:variable name="d2fdy2" select="(($a1==0.0)?0.0:log($a1)*log($a1)*pow($a1,$a2))"/>
#    </admst:when>
#    <admst:when test="[name='min' or name='max']">
#      <admst:variable name="d2fdx2" select="0.0"/>
#      <admst:variable name="d2fdxdy" select="0.0"/>
#      <admst:variable name="d2fdy2" select="0.0"/>
#    </admst:when>
#    <admst:when test="[name='hypot']">
#      <admst:variable name="functionIndex" select="%(index(../function,.))"/>
#      <admst:variable name="hypotval" select="value_hypot_%($functionIndex)"/>
#      <admst:variable name="d2fdx2" select="(1.0/$hypotval - $a1*$a1/($a1*$a1+$a2*$a2)/$hypotval)"/>
#      <admst:variable name="d2fdxdy" select="( - $a1*$a2/($a1*$a1+$a2*$a2)/$hypotval)"/>
#      <admst:variable name="d2fdy2" select="(1.0/$hypotval - $a2*$a2/($a1*$a1+$a2*$a2)/$hypotval)"/>
#    </admst:when>
#    <admst:when test="[name='atan2']">
#      <admst:variable name="functionIndex" select="%(index(../function,.))"/>
#      <admst:variable name="dfda1" select="deriv_atan2_%($functionIndex)_d0"/>
#      <admst:variable name="dfda2" select="deriv_atan2_%($functionIndex)_d1"/>
#      <admst:apply-templates select="arguments[1]" match="processTerm">
#        <admst:variable name="a1" select="%(returned('returnedExpression')/value)"/>
#      </admst:apply-templates>
#      <admst:apply-templates select="arguments[2]" match="processTerm">
#        <admst:variable name="a2" select="%(returned('returnedExpression')/value)"/>
#      </admst:apply-templates>
#      <!-- Note, here, "x" and "y" refer to arguments one and two,
#           respectively, even though atan2() is usually called as "atan2(y,x)"
#           -->
#      <admst:variable name="dfdx2" select="2*$dfda1*$dfda2"/>
#      <admst:variable name="dfdxdy" select="(1.0/($a1*$a1+$a2*$a2) - 2*$dfda1*$dfda1)"/>
#      <admst:variable name="dfdy2" select="-2*$dfda1*$dfda2"/>
#    </admst:when>
#    <admst:otherwise>
#      <admst:variable name="d2fdx2" select="fixme/*second derivs of %(name) unimplemented*/"/>
#      <admst:variable name="d2fdxdy" select="fixme/*second derivs of %(name) unimplemented*/"/>
#      <admst:variable name="d2fdy2" select="fixme/*second derivs of %(name) unimplemented*/"/>
#    </admst:otherwise>
#  </admst:choose>
#  <admst:return name="d2fdx2" value="$d2fdx2"/>
#  <admst:return name="d2fdy2" value="$d2fdy2"/>
#  <admst:return name="d2fdxdy" value="$d2fdxdy"/>
#</admst:template>
#
#<!-- This variant doesn't try to return fancy names for functions in all
#     contexts, just makes certain Verilog-A to C++ mappings.  Used for
#     creation of variable names, not function calls -->
#<admst:template match="funcnameSimple">
#  <admst:choose>
#    <admst:when test="[name='abs']">
#      <admst:variable name="expression" select="fabs"/>
#    </admst:when>
#    <admst:when test="[name='\$shrinkl']">
#      <admst:variable name="expression" select="shrinkl"/>
#    </admst:when>
#    <admst:when test="[name='\$shrinka']">
#      <admst:variable name="expression" select="shrinka"/>
#    </admst:when>
#    <admst:when test="[name='log']">
#      <admst:variable name="expression" select="log"/>
#    </admst:when>
#    <admst:when test="[name='ln']">
#      <admst:variable name="expression" select="log"/>
#    </admst:when>
#    <admst:when test="[name='limexp']">
#      <admst:variable name="expression" select="limexp"/>
#    </admst:when>
#    <admst:when test="[name='\$limexp']">
#      <admst:variable name="expression" select="limexp"/>
#    </admst:when>
#    <admst:otherwise>
#      <admst:variable name="expression" select="%(name)"/>
#    </admst:otherwise>
#  </admst:choose>
#  <admst:return name="fname" value="$expression"/>
#</admst:template>
#
#<!-- callfunction: handle $strobe and $bound_step-->
#<admst:template match="callfunction">
#  <admst:choose>
#    <admst:when test="[$globalCurrentScope != 'AF']">
#      <admst:choose>
#        <admst:when test="function[name='\$strobe' or name='\$write'  or name='\$display']">
#          <admst:variable name="saveSkipFunctionPrecomp" select="$skipFunctionPrecomp"/>
#          <admst:variable name="skipFunctionPrecomp" select="y"/>
#          <admst:choose>
#            <admst:when test="[$globalCurrentScope ='sensitivity']">
#              <admst:text format="UserInfo(theInstance) "/>
#            </admst:when>
#            <admst:otherwise>
#              <admst:text format="UserInfo(*this) "/>
#            </admst:otherwise>
#          </admst:choose>
#          <admst:for-each select="function/arguments">
#            <admst:text format=" &lt;&lt; %(printTerm(.)) &lt;&lt; &quot; &quot;"/>
#          </admst:for-each>
#          <admst:if test="[function/name='\$strobe' or function/name='\$display']">
#            <admst:text format=" &lt;&lt;  std::endl"/>
#          </admst:if>
#          <admst:text format="; \n"/>
#          <admst:variable name="skipFunctionPrecomp" select="$saveSkipFunctionPrecomp"/>
#        </admst:when>
#        <admst:when test="function[name='\$finish']">
#          <admst:choose>
#            <admst:when test="[$globalCurrentScope ='sensitivity']">
#              <admst:text format=" UserError(theInstance) &lt;&lt; &quot;%(function/name) called.&quot; &lt;&lt; std::endl; \n"/>
#            </admst:when>
#            <admst:otherwise>
#              <admst:text format=" UserError(*this) &lt;&lt; &quot;%(function/name) called.&quot; &lt;&lt; std::endl; \n"/>
#            </admst:otherwise>
#          </admst:choose>
#        </admst:when>
#        <admst:when test="function[name='\$bound_step']">
#          <admst:choose>
#            <admst:when test="[$globalCurrentScope ='sensitivity']">
#              <!-- do absolutely nothing -->
#            </admst:when>
#            <admst:otherwise>
#              <admst:text format=" maxTimeStep_ = %(printTerm(function/arguments[1]));\n"/>
#            </admst:otherwise>
#          </admst:choose>
#        </admst:when>
#        <admst:otherwise>
#          <admst:value-of select="function/name"/>
#          <admst:text format="// %s: not supported by this interface\n"/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:otherwise>
#      <admst:text format="// %(function/name): not supported in analog functions\n"/>
#      <admst:warning format="%(function/name) not supported in analog functions, ignored.\n"/>
#    </admst:otherwise>
#  </admst:choose>
#</admst:template>
#
#
#
#  <!--
#   =================================================================-
#   realArgument
#   format a function argument to make sure that it is a real quantity
#   when emitted.
#
#   This is designed to be used such cases as
#   real foo;
#   integer bar;
#   foo=ln(bar);
#   which should wind up emitted as
#   double foo;
#   integer bar;
#   foo=log(static_cast<double>(bar));
#
#   This is especially important on systems like Windows.
#
#   This may also be used to handle things like this:
#   real foo;
#   real bar;
#   bar=max(foo,0);
#
#   C++ hates having the integer constant as the second argument of max
#   on most systems.
#
#   What we do here is check that if the argument is a constant or
#   integer variable.  If so, wrap the thing in a static cast first.
#   Otherwise, just emit as is.
#
#   When called, the current node is the argument.
#   =================================================================-
#  -->
#
#  <admst:template match="realArgument">
#    <admst:choose>
#      <admst:when test="[datatypename='number' or (datatypename='variable' and type='integer')]">
#        <admst:variable name="localArg" select="static_cast&lt;double&gt;(%(processTerm(.)/[name='returnedExpression']/value))" />
#      </admst:when>
#      <admst:otherwise>
#        <admst:variable name="localArg" select="%(processTerm(.)/[name='returnedExpression']/value)" />
#      </admst:otherwise>
#    </admst:choose>
#    <admst:return name="argval" value="$localArg"/>
#  </admst:template>
#
# <!--
#   =================================================================-
#   generateEvaluateModelEquationsArgs
#
#   to avoid doing all this mess over and over again, with possibility
#   of mismatch, collect up in one place If global variable
#   "globalDeclareEMEVars" is set, emit types with variable names (for
#   function definition/declaration).  If not, just generate variable
#   names (for function call)
#
#   In this version, we're very specifically emitting declarations JUST
#   for sensitivity, not for a general version.
#   =================================================================-
# -->
# <admst:template match="generateEvaluateModelEquationsArgs">
#   <!-- don't generate these if not declaring, because the caller
#        might need to add things like "in." or "mod." to them. -->
#   <admst:if test="[$globalDeclareVars='yes']">
#     <admst:text format="std::vector &lt;double&gt; &amp; probeVars,\n"/>
#     <admst:text format="// probe constants\n"/>
#
#     <admst:if test="[count(probe)>0]">
#       <admst:join select="probe" separator=",\n">
#         <admst:text format="const int "/>
#         <admst:text format="%(xyceProbeConstantName(.)/[name='probeConstant']/value)"/>
#       </admst:join>
#       <admst:text format=",\n"/>
#     </admst:if>
#     <admst:if test="[count(@extraProbeBranches)>0]">
#       <admst:join select="@extraProbeBranches" separator=",\n">
#         <admst:text format="const int "/>
#         <admst:text format="%(xyceFlowProbeConstantName(.)/[name='probeConstant']/value)"/>
#       </admst:join>
#       <admst:text format=",\n"/>
#     </admst:if>
#
#     <admst:text format="// node constants\n"/>
#
#     <admst:join select="node[grounded='no']" separator=",\n">
#       <admst:text format="const int "/>
#       <admst:text format="%(xyceNodeConstantName(.)/[name='nodeConstant']/value)"/>
#     </admst:join>
#     <admst:if test="[count(@extraUnknowns)>0]">
#       <admst:text format=",\n"/>
#       <admst:join select="@extraUnknowns" separator=",\n">
#         <admst:text format="const int "/>
#         <admst:text format="%(xyceBranchConstantName(.)/[name='branchConstant']/value)"/>
#       </admst:join>
#     </admst:if>
#   </admst:if>
#   <admst:text format=",\n"/>
#
#   <!-- now generate the instance and model parameters and variables -->
#   <admst:if test="[$globalDeclareVars='yes']">
#     <admst:text format="instanceSensStruct &amp; "/>
#   </admst:if>
#   <admst:text format="instanceStruct,\n"/>
#   <admst:if test="[$globalDeclareVars='yes']">
#     <admst:text format="modelSensStruct &amp; "/>
#   </admst:if>
#   <admst:text format="modelStruct,\n"/>
#
#   <!-- don't generate these if not declaring, because the caller
#        might need to add things like "in." or "mod." to them. -->
#   <admst:if test="[$globalDeclareVars='yes']">
#     <admst:if test="[exists(@optnodes)]">
#       <admst:text format="const std::vector&lt;bool&gt; &amp; portsConnected_,\n"/>
#     </admst:if>
#     <admst:text format="// basic variables\n"/>
#     <admst:text format=" double admsTemperature"/>
#     <admst:text format=", double adms_vt_nom"/>
#     <admst:text format=", double ADMSgmin_arg"/>
#     <admst:text format=", std::vector &lt;double&gt; &amp; d_staticContributions_dX"/>
#     <admst:text format=", std::vector &lt;double&gt; &amp; d_dynamicContributions_dX"/>
#     <!-- YUCK!  Went through all that trouble to duplicate the instance vars
#          and here we are passing an instance pointer!  Why?  Only because
#          UserError takes an instance as argument.  DO NOT EVER USE ANYTHING
#          FROM THE INSTANCE PASSED in evaluateModelEquations! -->
#     <admst:text format=", const Instance &amp; theInstance"/>
#   </admst:if>
#</admst:template>
#
#
# <!--
#   =================================================================-
#   generateInstanceStruct
#
#   Generate the declaration of a structure to hold instance pars and vars
#   to consolidate and simplify passing them to functions
#
#   In this version, we're very specifically emitting declarations JUST
#   for sensitivity, not for a general version.
#   =================================================================-
# -->
# <admst:template match="generateInstanceStruct">
#   <admst:text format="class instanceSensStruct\n{\npublic:\n"/>
#
#   <admst:if test="[exists( variable[parametertype='instance' and input='yes' and type='real']) or exists( variable[parametertype='instance' and input='no' and exists(attribute[name='hidden']) and type='real'] ) or exists( variable[parametertype='instance' and (input='yes' or input='no' and exists(attribute[name='hidden'])) and not(type='real')] )]">
#     <admst:text format="// instance parameters\n"/>
#   </admst:if>
#
#   <admst:if test="[exists( variable[parametertype='instance' and input='yes' and type='real'])]">
#     <admst:text format="// reals\n"/>
#     <admst:for-each select="variable[parametertype='instance' and input='yes' and type='real']">
#       <admst:text format="double instancePar_%(name);\n"/>
#       <admst:text format="double d_instancePar_%(name)_dX;\n"/>
#       <admst:text format="bool instancePar_given_%(name);\n"/>
#     </admst:for-each>
#   </admst:if>
#
#   <admst:if test="[exists( variable[parametertype='instance' and input='no' and exists(attribute[name='hidden']) and type='real'] )]">
#     <admst:text format="// real hiddens\n"/>
#     <admst:for-each select="variable[parametertype='instance' and input='no' and exists(attribute[name='hidden']) and type='real']">
#       <admst:text format="double instancePar_%(name);\n"/>
#       <admst:text format="double d_instancePar_%(name)_dX;\n"/>
#     </admst:for-each>
#   </admst:if>
#
#   <admst:if test="[exists( variable[parametertype='instance' and (input='yes' or input='no' and exists(attribute[name='hidden'])) and not(type='real')] )]">
#     <admst:text format="// non-reals(including hidden)\n"/>
#     <admst:for-each select="variable[parametertype='instance' and (input='yes' or input='no' and exists(attribute[name='hidden'])) and not(type='real')]">
#       <admst:apply-templates select="." match="verilog2CXXtype"/>
#       <admst:text format=" instancePar_%(name);\n"/>
#       <admst:if test="[not(exists(attribute[name='hidden']))]">
#         <admst:text format="bool instancePar_given_%(name);\n"/>
#       </admst:if>
#     </admst:for-each>
#   </admst:if>
#
#   <admst:if test="[exists( variable[(scope='global_instance') and input='no' and not (exists(attribute[name='hidden']) and type='real')]) or exists( variable[(scope='global_instance') and input='no' and not (exists(attribute[name='hidden'])) and not (type='real')])]">
#     <admst:text format="// instance variables\n"/>
#   </admst:if>
#   <admst:if test="[exists( variable[(scope='global_instance') and input='no' and not (exists(attribute[name='hidden']) and type='real' and not(insource='no' and output='yes'))])]">
#     <admst:text format="// reals\n"/>
#     <admst:for-each select="variable[(scope='global_instance') and input='no' and not (exists(attribute[name='hidden'])) and type='real' and not(insource='no' and output='yes')]">
#       <admst:apply-templates select="." match="collectParamDependence"/>
#       <admst:text format="double instanceVar_%(name);\n"/>
#       <admst:if test="[exists(#Pdependent)]">
#         <admst:text format="double d_instanceVar_%(name)_dX;\n"/>
#       </admst:if>
#     </admst:for-each>
#   </admst:if>
#
#   <admst:if test="[exists( variable[(scope='global_instance') and input='no' and not (exists(attribute[name='hidden'])) and not (type='real')])]">
#     <admst:text format="// non-reals\n"/>
#     <admst:for-each select="variable[(scope='global_instance') and input='no' and not (type='real')]">
#       <admst:apply-templates select="." match="verilog2CXXtype"/>
#       <admst:text format=" instanceVar_%(name);\n"/>
#     </admst:for-each>
#   </admst:if>
#
#   <admst:text format="};\n\n"/>
# </admst:template>
#
# <!--
#   =================================================================-
#   generateModelStruct
#
#   Generate the declaration of a structure to hold model pars and vars
#   to consolidate and simplify passing them to functions
# 
#   In this version, we're very specifically emitting declarations JUST
#   for sensitivity, not for a general version.
#   =================================================================-
# -->
# <admst:template match="generateModelStruct">
#   <admst:text format="class modelSensStruct\n{\npublic:\n"/>
#
#   <admst:if test="[exists( variable[(parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and input='yes' and type='real']) or exists( variable[(parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and input='no' and exists(attribute[name='hidden']) and type='real']) or exists( variable[(parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and (input='yes' or (input='no' and exists(attribute[name='hidden']))) and not (type='real')])]">
#     <admst:text format="// model parameters\n"/>
#   </admst:if>
#
#   <admst:if test="[exists( variable[(parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and input='yes' and type='real'])]">
#     <admst:text format="// reals\n"/>
#     <admst:for-each select="variable[(parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and input='yes' and type='real']">
#       <admst:text format="double modelPar_%(name);\n"/>
#       <admst:text format="double d_modelPar_%(name)_dX;\n"/>
#       <admst:text format="bool modelPar_given_%(name);\n"/>
#     </admst:for-each>
#   </admst:if>
#
#   <admst:if test="[exists( variable[(parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and input='no' and exists(attribute[name='hidden']) and type='real'])]">
#     <admst:text format="// real hiddens\n"/>
#     <admst:for-each select="variable[(parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and input='no' and exists(attribute[name='hidden']) and type='real']">
#       <admst:text format="double modelPar_%(name); \n"/>
#       <admst:text format="double d_modelPar_%(name)_dX;\n"/>
#     </admst:for-each>
#   </admst:if>
#
#   <admst:if test="[exists( variable[(parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and (input='yes' or (input='no' and exists(attribute[name='hidden']))) and not (type='real')])]">
#     <admst:text format="// non-reals (including hidden)\n"/>
#     <admst:for-each select="variable[(parametertype='model' or (parametertype='instance' and exists(attribute[name='xyceAlsoModel']))) and (input='yes' or (input='no' and exists(attribute[name='hidden']))) and not (type='real')]">
#       <admst:apply-templates select="." match="verilog2CXXtype"/>
#       <admst:text format=" modelPar_%(name);\n"/>
#       <admst:if test="[not(exists(attribute[name='hidden']))]">
#         <admst:text format="bool modelPar_given_%(name);\n"/>
#       </admst:if>
#     </admst:for-each>
#   </admst:if>
#
#   <admst:if test="[exists( variable[(scope='global_model') and input='no' and not (exists(attribute[name='hidden'])) and type='real']) or exists( variable[(scope='global_model') and input='no' and not (type='real')])]">
#     <admst:text format="// model variables\n"/>
#   </admst:if>
#   <admst:if test="[exists( variable[(scope='global_model') and input='no' and not (exists(attribute[name='hidden'])) and type='real'])]">
#     <admst:text format="// reals\n"/>
#     <admst:for-each select="variable[(scope='global_model') and input='no' and not (exists(attribute[name='hidden'])) and type='real']">
#       <admst:apply-templates select="." match="collectParamDependence"/>
#       <admst:text format="double modelVar_%(name);\n"/>
#       <admst:if test="[exists(#Pdependent)]">
#         <admst:text format="double d_modelVar_%(name)_dX;"/>
#       </admst:if>
#     </admst:for-each>
#   </admst:if>
#
#   <admst:if test="[exists( variable[(scope='global_model') and input='no' and not (type='real')])]">
#     <admst:text format="// non-reals\n"/>
#     <admst:for-each select="variable[(scope='global_model') and input='no' and not (type='real')]">
#       <admst:apply-templates select="." match="verilog2CXXtype"/>
#       <admst:text format=" modelVar_%(name);"/>
#     </admst:for-each>
#   </admst:if>
#   <admst:text format="};\n\n"/>
#
#</admst:template>
#
#</admst>

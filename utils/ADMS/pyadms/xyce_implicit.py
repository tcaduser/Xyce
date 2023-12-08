#<?xml version="1.0" encoding="ISO-8859-1"?>
#<!--
#  This file is part of adms - http://sourceforge.net/projects/mot-adms.
#
#  adms is a code generator for the Verilog-AMS language.
#
#  Copyright (C) 2002-2012 Laurent Lemaitre <r29173@users.sourceforge.net>
#  Copyright (C) 2015-2016 Guilherme Brondani Torri <guitorri@gmail.com>
#                2012 Ryan Fox <ryan.fox@upverter.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-->
#
#<!--  Version modified for use with Xyce to add dependency propagation
#      for analog function output variables
#      To make use of this, use the "-x" flag to admsXml in order to
#      disable its use of its own implicit rules, then put a "-e" flag followed
#      by this file's name first in your list of admsXml command-line options
#      to invoke it explicitly.
#-->
#
#<!-- built-in implicit transforms @GIT_VERSION=unknown@ -->
#<!-- this file is saved in local working directory, then downloaded prior any -e xml files -->
#<!-- unless flag '-x' is specified -->
#
#<!DOCTYPE admst SYSTEM "admst.dtd">
#<admst version="2.3.0" xmlns:admst="http://mot-adms.sourceforge.net/adms/admst.xml">

class dependency_visitor:
    def __init__(self):
        self.globalmodule = None
        self.globalassignment = None
        self.globalcontribution = None
        self.globalexpression = None
        self.globalopdependent = False
        self.globalpartitionning = None
        self.globaltreenode = None
        self.globalhandleafoutputs = False
        self.globalaf = None
        self.theDDXProbeToPush = None

    def visit_expression(self, expression):
        self.globalexpression = expression
        expression.probe = expression.create_reference_list()
        tree = expression.tree()
        tree.visit(self)
        self.globalexpression = None
        expression.dependency = tree.dependency

        if self.globalopdependent and (expression.dependency == 'constant'):
            expression.dependency = 'noprobe'


        partitionning_map = {
            None : lambda v : setattr(v, 'usedinevaluate', True),
            'initial_model' : lambda v : setattr(v, 'usedinmodel', True),
            'initial_instance' : lambda v : setattr(v, 'usedininstance', True),
            'initial_step' : lambda v : setattr(v, 'usedininitial_step', True),
            'noise' : lambda v : setattr(v, 'usedinnoise', True),
            'final_step' : lambda v : setattr(v, 'usedinfinal', True),
        }
        f = partionning_map[self.globalpartitionning]
        for v in expression.variable.get_list():
            f(v)

        expression.math = tree.math

    def visit_probe(self, probe):
        probe.dependency = 'linear'
        if probe.id not in self.globalexpression.probe:
            self.globalexpression.probe.append(probe.id, True)

        if self.globalhandleafoutputs:
            self.globalaf.probe.append(probe.id, True)

    def visit_array(self, array):
        array.visit(array.variable)
        array.dependency = array.variable().dependency

    def visit_variable(self, variable):
        self.globalexpression.probe.extend(variable.probe, True)
        self.globalexpression.variable.extend(variable, True)
        self.globaltreenode.variable.append(variable, True)
        variable.dependency = variable.prototype().dependency

        if self.globalhandleafoutputs:
            self.globalaf.probe.extend(variable.probe, True)
            self.globalaf.variable.extend(variable, True)

    def visit_mapply_unary(self, unary):
        arg = unary.args.get_head()
        arg.visit(self)
        unary.dependency = args.dependency
        unary.math = f'-({arg.math})'

    def visit_mapply_binary(self, binary):
        args = list(binary.args.get_list())
        for arg in args:
            arg.visit(self)
#      <!--
#        +:             -:            *:            /:
#          c  np l  nl    c  np l  nl   c  np l  nl   c  np nl nl
#          np np l  nl    np np l  nl   np np l  nl   np np nl nl
#          l  l  l  nl    l  l  l  nl   l  l  nl nl   l  l  nl nl
#          nl nl nl nl    nl nl nl nl   nl nl nl nl   nl nl nl nl
#      -->
        deps = [x.dependency for x in args]
        if binary.name == 'multdiv' and  deps[1] == 'linear':
            binary.dependency = 'nonlinear'
        elif 'nonlinear' in deps:
            binary.dependency = 'nonlinear'
        elif 'linear' in deps:
            binary.dependency = 'nonlinear'
        elif 'noprobe' in deps:
            binary.dependency = 'noprobe'
        else:
            binary.dependency = 'constant'

    def visit_mapply_ternary(self, ternary):
        args = list(ternary.args.get_list())
        for arg in args:
            arg.visit(self)
#      <!--
#          ?: - arg1=c -  - arg1!=c -
#             c  np l  nl np np l  nl
#             np np l  nl np np l  nl
#             l  l  l  nl l  l  l  nl
#             nl nl nl nl nl nl nl nl
#      -->
        if 'nonlinear' in deps[1:]:
            ternary.dependency = 'nonlinear'
        elif 'linear' in deps[1:]:
            ternary.dependency = 'linear'
        elif 'constant' != deps[0] or 'noprobe' in args[1:]:
            ternary.dependency = 'noprobe'
        else:
            ternary.dependency = 'constant'

    def visit_function(self, function):
        function.name = function.lexval().string
        name = function.name
        if name in ('ddx', '$ddx', '$derivate',):
            self.globalassignment.lhs().derivate = True
            arg1 = function.arguments.get_item(0)
            arg1.visit(self)
#          <!-- recursively push a ddxprobe into argument 1-->
#          <!-- call with argument 1 in select, set $theDDXProbeToPush to -->
#          <!-- the PATH to thing to push in -->

            def create_ddxprobe(arg):
                if arg.hasattr('ddxprobe'):
                    raise RuntimeError("Unexpected")
                else:
                    arg.ddxprobe = arg.create_reference_list()

            def pushDDXintoArg(x, theDDXProbeToPush):
                if x.datatypename == 'variable':
                    create_ddxprobe(x)
                    x.ddxprobe.append(theDDXProbeToPush)
                elif x.datatypename == 'expression':
                    create_ddxprobe(x.variable())
                    x.variable().ddxprobe.append(theDDXProbeToPush)
                elif x.datatypename == 'mapply_binary':
                    pushDDXintoArg(x.args.get_item(0))
                    pushDDXintoArg(x.args.get_item(1))
                elif x.datatypename == 'mapply_ternary':
                    pushDDXintoArg(x.args.get_item(1))
                    pushDDXintoArg(x.args.get_item(2))
                elif x.datatypename in ('constant', 'number',):
                    pass
                else:
                    raise RuntimeError(f"Xyce/ADMS got a ddx expression {x.uid} of type {x.datatypename} and cannot proceed.  We currently support only mapply_binary, mapply_ternary and variable.")
            arg2 = function.arguments.get_item(1)
            pushDDXintoArg(arg1, arg2)
            if arg1.dependency in ('constant', 'noprobe'):
                function.dependency = arg1.dependency
            else:
                function.dependency = 'nonlinear'
        elif name == '$port_connected':
            function.dependency = 'constant'
            arg1 = function.arguments.get_item(0)
            if arg1.datatypename != 'node':
                raise RuntimeError(f"Argument {arg1.uid} to $port_connected is not a node")
            else:
                nodename = arg1.name
                module = arg1.get_module()
                if not hasattr(module, 'optnodes'):
                    module.optnodes = module.create_reference_list()
                    module.optnodes.append(arg1, True)
            arg1.optional = True
        else:
            #
            # Analog functions
            #
            definition = function.definition()
            if (definition is not None) and (definition.datatypename == 'analogfunction'):
               for v in definition.variable.get_list():
                    if variable.output and variable.name == function.name:
                        self.globalhandleafoutputs = True
                        self.globalaf = function

            #
            # process arg dependencies
            #
            for arg in function.arguments.get_list():
                arg.visit(self)

            deps = [x.dependency for x in function.arguments.get_list()]

            if self.globalhandleafoutputs:
                self.globalhandleafoutputs = False
                self.globalaf = None

                if ('linear' in deps) or ('nonlinear' in deps):
                    dependency = 'nonlinear'
                elif 'noprobe' in deps:
                    dependency = 'noprobe'
                elif 'constant' in deps:
                    dependency = 'constant'

                for position, dv in enumerate(definition.variable.get_list()):
                    if not (dv.output and dv.name != function.name):
                        continue
                    elif dv.datatypename != 'variable':
                        raise RuntimeError(f"{function.name} output arg {position} is {dv.datatypename}, must be a variable")

                    # propagating probes and variables to output
                    dv.probe.extend(function.probe)
                    dv.variable.extend(function.variable)
                    dv.dependency = dependency
                    dv.prototype().dependency = dependency

                    if self.globalpartitioning == 'initial_model':
                        dv.setinmodel = True
                    elif self.globalpartitioning == 'initial_instance':
                        dv.setininstance = True
                    elif self.globalpartitioning == 'initial_step':
                        dv.setininitial_step = True
                    elif self.globalpartitioning == 'noise':
                        dv.setinnoise = True
                    elif self.globalpartitioning == 'final_step':
                        dv.setinfinal = True
                    else:
                        dv.setinevaluate = True

            function.probe = None
            function.variable = None

            if name in ('ddt', '$ddt', 'idt', '$idt',):
                function.dependency = 'nonlinear'
            elif ('linear' in deps) or ('nonlinear' in deps):
                function.dependency = 'nonlinear'
            elif 'noprobe' in deps:
                function.dependency = 'noprobe'
            else:
                function.dependency = 'constant'
        if function.dependency in ('linear', 'nonlinear'):
            self.globalexpression.hasVoltageDependentFunction = True

        function.subexpression = self.globalexpression
#      <!-- fixme: these flags should be set after all contribs are transformed to ...<+F(...); canonical form -->
        if name = 'ddt':
            self.globalcontribution.fixmedynamic = True
        elif name == 'white_noise':
            self.globalcontribution.fixmewhitenoise = True
        elif name == 'flicker_noise':
            self.globalcontribution.fixmeflickernoise = True
        elif name == '$temperature':
            self.globalassignment.lhs().TemperatureDependent = True

#      <admst:choose>
#        <admst:when
#          test="[
#          name='\$abstime' or
#          name='\$realtime' or
#          name='\$temperature' or
#          name='\$vt' or
#          name='idt' or
#          name='ddt' or
#          name='\$param_given' or
#          name='\$port_connected' or
#          name='\$given' or
#          name='ddx' or
#          name='flicker_noise' or
#          name='white_noise'
#          ]">
#        </admst:when>
#
#        <!-- Table 4-14 - Standard Functions -->
#        <!-- Table 4-15 - Trigonometric and Hyperbolic Functions-->
#        <admst:when
#          test="[name='analysis' or name='\$analysis' or name='\$simparam' or name='simparam' or
#          name='\$shrinka' or name='\$shrinkl' or name='\$limexp' or name='limexp' or name='\$limit' or
#          name='ln' or
#          name='log' or
#          name='exp' or
#          name='sqrt' or
#          name='min' or
#          name='max' or
#          name='abs' or
#          name='pow' or
#          name='floor' or
#          name='ceil' or
#          name='sin' or
#          name='cos' or
#          name='tan' or
#          name='asin' or
#          name='acos' or
#          name='atan' or
#          name='atan2' or
#          name='hypot' or
#          name='sinh' or
#          name='cosh' or
#          name='tanh' or
#          name='asinh' or
#          name='acosh' or
#          name='atanh'
#          ]">
#          <admst:push into="$globalexpression/function" select="."/>
#          <admst:value-to select="class" string="builtin"/>
#        </admst:when>
#        <admst:when test="[name='transition']">
#          <admst:push into="$globalexpression/function" select="."/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:assert test="[exists(definition)]" format="%(lexval/(f|':'|l|':'|c)): analog function '%(name)' is undefined\n"/>
#          <admst:push into="$globalexpression/function" select="."/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:when test="[datatypename='number']">
#      <admst:choose>
#        <admst:when test="[scalingunit='1']">
#          <admst:value-to select="math/value" path="value"/>
#        </admst:when>
#        <admst:when test="[scalingunit='E']">
#          <admst:warning format="%(lexval/(f|':'|l|':'|c)): non-standard scale factor: %(scalingunit)\n"/>
#          <admst:value-to select="math/value" string="%(value)e+18"/>
#        </admst:when>
#        <admst:when test="[scalingunit='P']">
#          <admst:warning format="%(lexval/(f|':'|l|':'|c)): non-standard scale factor: %(scalingunit)\n"/>
#          <admst:value-to select="math/value" string="%(value)e+15"/>
#        </admst:when>
#        <admst:when test="[scalingunit='T']">
#          <admst:value-to select="math/value" string="%(value)e+12"/>
#        </admst:when>
#        <admst:when test="[scalingunit='G']">
#          <admst:value-to select="math/value" string="%(value)e+9"/>
#        </admst:when>
#        <admst:when test="[scalingunit='M']">
#          <admst:value-to select="math/value" string="%(value)e+6"/>
#        </admst:when>
#        <admst:when test="[scalingunit='K']">
#          <admst:value-to select="math/value" string="%(value)e+3"/>
#        </admst:when>
#        <admst:when test="[scalingunit='k']">
#          <admst:value-to select="math/value" string="%(value)e+3"/>
#        </admst:when>
#        <admst:when test="[scalingunit='h']">
#          <admst:value-to select="math/value" string="%(value)e+2"/>
#          <admst:warning format="%(lexval/(f|':'|l|':'|c)): non-standard scale factor: %(scalingunit)\n"/>
#        </admst:when>
#        <admst:when test="[scalingunit='D']">
#          <admst:value-to select="math/value" string="%(value)e+1"/>
#          <admst:warning format="%(lexval/(f|':'|l|':'|c)): non-standard scale factor: %(scalingunit)\n"/>
#        </admst:when>
#        <admst:when test="[scalingunit='d']">
#          <admst:warning format="%(lexval/(f|':'|l|':'|c)): non-standard scale factor: %(scalingunit)\n"/>
#          <admst:value-to select="math/value" string="%(value)e-1"/>
#        </admst:when>
#        <admst:when test="[scalingunit='c']">
#          <admst:value-to select="math/value" string="%(value)e-2"/>
#        </admst:when>
#        <admst:when test="[scalingunit='m']">
#          <admst:value-to select="math/value" string="%(value)e-3"/>
#        </admst:when>
#        <admst:when test="[scalingunit='u']">
#          <admst:value-to select="math/value" string="%(value)e-6"/>
#        </admst:when>
#        <admst:when test="[scalingunit='n']">
#          <admst:value-to select="math/value" string="%(value)e-9"/>
#        </admst:when>
#        <admst:when test="[scalingunit='A']">
#          <admst:warning format="%(lexval/(f|':'|l|':'|c)): non-standard scale factor: %(scalingunit)\n"/>
#          <admst:value-to select="math/value" string="%(value)e-10"/>
#        </admst:when>
#        <admst:when test="[scalingunit='p']">
#          <admst:value-to select="math/value" string="%(value)e-12"/>
#        </admst:when>
#        <admst:when test="[scalingunit='f']">
#          <admst:value-to select="math/value" string="%(value)e-15"/>
#        </admst:when>
#        <admst:when test="[scalingunit='a']">
#          <admst:value-to select="math/value" string="%(value)e-18"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:error format="%(lexval/(f|':'|l|':'|c)): unit not supported: %(scalingunit)\n"/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:when test="[datatypename='string']"/>
#    <admst:otherwise>
#      <admst:fatal format="%(datatypename): case not handled\n"/>
#    </admst:otherwise>
#  </admst:choose>
#</admst:template>
#
#<admst:template match="dependency">
#  <admst:choose>
#    <admst:when test="[datatypename='callfunction']">
#      <admst:apply-templates select="function/arguments" match="e:dependency"/>
#      <admst:value-to select="dependency" path="function/dependency"/>
#    </admst:when>
#    <admst:when test="[datatypename='whileloop']">
#      <!--
#        w, logic(D,while.d)            , d=wb.d
#              c                 !c
#           c  wb,w,!c?(D,wb,!D) D,wb,!D
#           !c wb                wb
#      -->
#
#      <!-- This template, like forloop, had broken conditions that can
#           possibly cause dependency to be called twice on the block with
#           the consequence of reversing the block twice and polluting
#           the datastructure with duplicates.  Let's try to make it less
#           dangerous -->
#
#      <admst:apply-templates select="while" match="e:dependency"/>
#      <admst:choose>
#        <admst:when test="[$globalopdependent='no']">
#          <admst:variable name="globalopdependent" string="yes"/>
#          <admst:apply-templates select="whileblock" match="dependency"/>
#          <admst:variable name="globalopdependent" string="no"/>
#          <admst:apply-templates select="while[dependency='constant']" match="e:dependency"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:apply-templates select="whileblock" match="dependency"/>
#        </admst:otherwise>
#      </admst:choose>
#
#      <!--
#          wl:  w=c          w!=c
#               c  np l  nl  np np l  nl
#               np np l  nl  np np l  nl
#               l  l  l  nl  l  l  l  nl
#               nl nl nl nl  nl nl nl nl
#      -->
#      <admst:choose>
#        <admst:when test="[whileblock/dependency='nonlinear']">
#          <admst:value-to select="dependency" string="nonlinear"/>
#        </admst:when>
#        <admst:when test="[whileblock/dependency='linear']">
#          <admst:value-to select="dependency" string="linear"/>
#        </admst:when>
#        <admst:when test="[while/dependency!='constant' or whileblock/dependency='noprobe']">
#          <admst:value-to select="dependency" string="noprobe"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:value-to select="dependency" string="constant"/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:when test="[datatypename='forloop']">
#      <!-- Xyce:  The original code for this had broken conditionals that
#           could, in some cases, allow dependency to be called twice on
#           the "forblock".  This is catastrophic and should not happen.
#           Let's try to accomplish the dependency scanning without that
#           logical hole -->
#      <admst:apply-templates select="initial|update" match="dependency"/>
#      <admst:apply-templates select="condition" match="e:dependency"/>
#      <admst:choose>
#        <admst:when test="[$globalopdependent='no']">
#          <admst:variable name="globalopdependent" string="yes"/>
#          <admst:apply-templates select="forblock" match="dependency"/>
#          <admst:variable name="globalopdependent" string="no"/>
#          <admst:apply-templates select="(initial|update)/[dependency='constant']" match="dependency"/>
#          <admst:apply-templates select="condition[dependency='constant']" match="e:dependency"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:apply-templates select="forblock" match="dependency"/>
#          <admst:apply-templates select="(initial|update)/[dependency='constant']" match="dependency"/>
#          <admst:apply-templates select="condition[dependency='constant']" match="e:dependency"/>
#        </admst:otherwise>
#      </admst:choose>
#      <!-- Original code: -->
#      <!--
#      <admst:apply-templates select="initial|update" match="dependency"/>
#      <admst:apply-templates select="condition" match="e:dependency"/>
#      <admst:apply-templates select="[$globalopdependent='yes' or nilled((initial|condition|update)/[dependency!='constant'])]/forblock" match="dependency"/>
#      <admst:if test="[$globalopdependent='no']">
#        <admst:apply-templates select="(initial|update)/[dependency='constant']" match="dependency"/>
#        <admst:apply-templates select="condition[dependency='constant']" match="e:dependency"/>
#        <admst:if test="[condition/dependency!='constant' or initial/dependency!='constant' or update/dependency!='constant']">
#          <admst:variable name="globalopdependent" string="yes"/>
#          <admst:apply-templates select="forblock" match="dependency"/>
#          <admst:variable name="globalopdependent" string="no"/>
#        </admst:if>
#      </admst:if>
#      -->
#      <!--
#          fl:  f=c          f!=c
#               c  np l  nl  np np l  nl
#               np np l  nl  np np l  nl
#               l  l  l  nl  l  l  l  nl
#               nl nl nl nl  nl nl nl nl
#      -->
#      <admst:choose>
#        <admst:when test="[forblock/dependency='nonlinear']">
#          <admst:value-to select="dependency" string="nonlinear"/>
#        </admst:when>
#        <admst:when test="[forblock/dependency='linear']">
#          <admst:value-to select="dependency" string="linear"/>
#        </admst:when>
#        <admst:when test="[(condition!='constant' or initial!='constant' or update!='constant') or forblock/dependency='noprobe']">
#          <admst:value-to select="dependency" string="noprobe"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:value-to select="dependency" string="constant"/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:when test="[datatypename='case']">
#      <admst:variable name="globaltreenode" path="case"/>
#      <admst:apply-templates select="case" match="e:dependency"/>
#      <admst:variable name="globaltreenode"/>
#      <admst:for-each select="caseitem">
#        <admst:for-each select="condition">
#          <admst:variable name="globaltreenode" path="."/>
#          <admst:apply-templates select="." match="e:dependency"/>
#          <admst:variable name="globaltreenode"/>
#        </admst:for-each>
#        <admst:apply-templates select="code" match="dependency"/>
#      </admst:for-each>
#    </admst:when>
#    <admst:when test="[datatypename='conditional']">
#      <admst:push into="$globalmodule/conditional" select="."/>
#      <admst:apply-templates select="if" match="e:dependency"/>
#      <admst:choose>
#        <admst:when test="[$globalopdependent='no' and if/dependency!='constant']">
#          <admst:variable name="globalopdependent" string="yes"/>
#          <admst:apply-templates select="then|else" match="dependency"/>
#          <admst:variable name="globalopdependent" string="no"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:apply-templates select="then|else" match="dependency"/>
#        </admst:otherwise>
#      </admst:choose>
#      <!--
#          cd:  i=c          i!=c
#               c  np l  nl  np np l  nl
#               np np l  nl  np np l  nl
#               l  l  l  nl  l  l  l  nl
#               nl nl nl nl  nl nl nl nl
#      -->
#      <admst:choose>
#        <admst:when test="[then/dependency='nonlinear' or else/dependency='nonlinear']">
#          <admst:value-to select="dependency" string="nonlinear"/>
#        </admst:when>
#        <admst:when test="[then/dependency='linear' or else/dependency='linear']">
#          <admst:value-to select="dependency" string="linear"/>
#        </admst:when>
#        <admst:when test="[if/dependency!='constant' or then/dependency='noprobe' or else/dependency='noprobe']">
#          <admst:value-to select="dependency" string="noprobe"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:value-to select="dependency" string="constant"/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:when test="[datatypename='contribution']">
#      <admst:variable name="globalcontribution" path="."/>
#      <admst:apply-templates select="rhs" match="e:dependency"/>
#      <admst:variable name="globalcontribution"/>
#      <admst:push into="lhs/probe" select="rhs/probe" onduplicate="ignore"/>
#      <admst:value-to select="dependency" string="nonlinear"/>
#    </admst:when>
#    <admst:when test="[datatypename='assignment']">
#      <admst:choose>
#        <admst:when test="[lhs/datatypename='array']">
#          <admst:variable name="lhs" path="lhs/variable"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:variable name="lhs" path="lhs"/>
#        </admst:otherwise>
#      </admst:choose>
#      <admst:choose>
#        <admst:when test="[$globalpartitionning='initial_model']">
#          <admst:value-to select="$lhs/setinmodel" string="yes"/>
#        </admst:when>
#        <admst:when test="[$globalpartitionning='initial_instance']">
#          <admst:value-to select="$lhs/setininstance" string="yes"/>
#        </admst:when>
#        <admst:when test="[$globalpartitionning='initial_step']">
#          <admst:value-to select="$lhs/setininitial_step" string="yes"/>
#        </admst:when>
#        <admst:when test="[$globalpartitionning='noise']">
#          <admst:value-to select="$lhs/setinnoise" string="yes"/>
#        </admst:when>
#        <admst:when test="[$globalpartitionning='final_step']">
#          <admst:value-to select="$lhs/setinfinal" string="yes"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:value-to select="$lhs/setinevaluate" string="yes"/>
#        </admst:otherwise>
#      </admst:choose>
#      <admst:variable name="globalassignment" path="."/>
#      <admst:apply-templates select="rhs" match="e:dependency"/>
#      <admst:variable name="globalassignment"/>
#      <admst:push into="$lhs/variable" select="rhs/variable" onduplicate="ignore"/>
#      <admst:value-to test="rhs/variable[TemperatureDependent='yes']" select="$lhs/TemperatureDependent" string="yes"/>
#      <!--
#        d=rhs.d,d=(c and D)?np
#        l(l,r,$globalopdependent)
#        $globalopdependent='no'  $globalopdependent='yes'
#        c  np l  nl               np np l  nl
#        np np l  nl               np np l  nl
#        l  l  l  nl               l  l  l  nl
#        nl nl nl nl               nl nl nl nl
#      -->
#      <admst:value-to select="dependency" path="rhs/dependency"/>
#      <admst:choose>
#        <admst:when test="[$lhs/prototype/dependency='nonlinear' or rhs/dependency='nonlinear']">
#          <admst:value-to select="$lhs/(.|prototype)/dependency" string="nonlinear"/>
#        </admst:when>
#        <admst:when test="[$lhs/prototype/dependency='linear' or rhs/dependency='linear']">
#          <admst:value-to select="$lhs/(.|prototype)/dependency" string="linear"/>
#        </admst:when>
#        <admst:when test="[$globalopdependent='yes' or $lhs/prototype/dependency='noprobe' or rhs/dependency='noprobe']">
#          <admst:value-to select="$lhs/(.|prototype)/dependency" string="noprobe"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:value-to select="$lhs/(.|prototype)/dependency" string="constant"/>
#        </admst:otherwise>
#      </admst:choose>
#      <admst:push into="$lhs/probe" select="rhs/probe" onduplicate="ignore"/>
#    </admst:when>
#    <admst:when test="[datatypename='block']">
#      <admst:reverse select="item|variable"/>
#      <admst:variable name="forcepartitionning" string="yes"/>
#      <admst:choose>
#        <admst:when test="[name='initial_model']">
#          <admst:variable name="globalpartitionning" string="initial_model"/>
#        </admst:when>
#        <admst:when test="[name='initial_instance']">
#          <admst:variable name="globalpartitionning" string="initial_instance"/>
#        </admst:when>
#        <admst:when test="[name='initial_step']">
#          <admst:variable name="globalpartitionning" string="initial_step"/>
#        </admst:when>
#        <admst:when test="[name='noise']">
#          <admst:variable name="globalpartitionning" string="noise"/>
#        </admst:when>
#        <admst:when test="[name='final_step']">
#          <admst:variable name="globalpartitionning" string="final_step"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:variable name="forcepartitionning" string="no"/>
#        </admst:otherwise>
#      </admst:choose>
#      <admst:apply-templates select="item" match="dependency"/>
#      <admst:variable test="[$forcepartitionning='yes']" name="globalpartitionning"/>
#      <admst:choose>
#        <admst:when test="item[dependency='nonlinear']">
#          <admst:value-to select="dependency" string="nonlinear"/>
#        </admst:when>
#        <admst:when test="item[dependency='linear']">
#          <admst:value-to select="dependency" string="linear"/>
#        </admst:when>
#        <admst:when test="item[dependency='noprobe']">
#          <admst:value-to select="dependency" string="noprobe"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:value-to select="dependency" string="constant"/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:when test="[datatypename='nilled']"/>
#    <admst:when test="[datatypename='blockvariable']"/>
#    <admst:otherwise>
#      <admst:fatal format="%(datatypename): case not handled\n"/>
#    </admst:otherwise>
#  </admst:choose>
#</admst:template>
#
#<admst:template match="adms.implicit.xml.module">
#  <admst:variable name="globalmodule" path="."/>
#  <admst:reverse select="analogfunction|analogfunction/variable|node|variable
#                         |instance|instance/terminal|contribution|forloop|whileloop|case|callfunction"/>
#  <admst:value-to select="node[location='ground']/grounded" string="yes"/>
#  <admst:for-each select="branch">
#    <admst:value-to select="discipline" path="pnode/discipline"/>
#    <admst:value-to select="[nnode/grounded='yes']/grounded" string="yes"/>
#    <!-- FIXME: check that pnode/nnode have same discipline -->
#  </admst:for-each>
#  <admst:for-each select="source|probe">
#    <admst:value-to select="discipline" path="branch/discipline"/>
#    <admst:value-to select="[branch/grounded='yes']/grounded" string="yes"/>
#  </admst:for-each>
#  <admst:for-each select="instance">
#    <admst:push into="module/instantiator" select=".." onduplicate="ignore"/>
#    <admst:assert select="terminal" test="terminal[nodefrommodule/location='external']"
#                  format="%(../instantiator).%(nodefrommodule/name): is not terminal\n"/>
#    <admst:if test="[count(parameterset)!=0]">
#      <admst:assert select="parameterset" test="parameterset[parameter/input='yes']"
#                    format="%(../instantiator).%(parameter/name): is not input parameter\n"/>
#    </admst:if>
#  </admst:for-each>
#  <admst:apply-templates select="(analogfunction/tree)|(analog/code)" match="dependency"/>
#  <admst:for-each select="variable">
#    <admst:value-to select="[dependency!='constant']/OPdependent" string="yes"/>
#    <admst:value-to select="output" path="input"/>
#    <admst:for-each select="attribute">
#      <admst:value-to select="[name='type' and value='instance']/../parametertype" string="instance"/>
#      <admst:value-to select="[name='ask' and value='yes']/../output" string="yes"/>
#      <admst:value-to select="[name='ask' and value='no']/../output" string="no"/>
#      <!-- set output flag if desc or units attribute and we are a module-
#            scoped variable,  not an input parameter, and have
#            desc or units attribute, per Verilog-A LRM 2.4, section 3.2.1 -->
#      <admst:if test="[../input!='yes' and ../module/name=../block/name and name='desc' and value!='']">
#          <admst:value-to select="../output" string="yes"/>
#      </admst:if>
#     <admst:if test="[../input!='yes' and ../module/name=../block/name and name='units' and value!='']">
#          <admst:value-to select="../output" string="yes"/>
#      </admst:if>
#    </admst:for-each>
#    <admst:apply-templates select="default" match="e:dependency"/>
#    <admst:value-to
#       select="default[exists(tree[datatypename='mapply_unary' and name='minus' and arg1/datatypename='number' and arg1/value='1.0'])]/value"
#       string="is_neg_one"/>
#    <admst:value-to select="default[exists(tree[datatypename='number' and value='0.0'])]/value" string="is_zero"/>
#    <admst:value-to select="default[exists(tree[datatypename='number' and value='1.0'])]/value" string="is_one"/>
#    <admst:value-to select="scope"
#      test="[(input='yes' and parametertype='model') or (input='no' and (setinmodel='yes' or usedinmodel='yes')
#        and (setininstance='yes' or setininitial_step='yes' or setinevaluate='yes' or setinnoise='yes' or setinfinal='yes'
#        or usedininstance='yes' or usedininitial_step='yes' or usedinevaluate='yes' or usedinnoise='yes' or usedinfinal='yes' or output='yes'))]"
#      string="global_model"/>
#    <admst:value-to select="scope"
#      test="[(input='yes' and parametertype='instance') or
#      (input='no' and setinmodel='no' and usedinmodel='no' and
#        (((setininstance='yes' or usedininstance='yes') and (setininitial_step='yes' or setinevaluate='yes' or setinnoise='yes' or setinfinal='yes'
#        or usedininitial_step='yes' or usedinevaluate='yes' or usedinnoise='yes' or usedinfinal='yes' or output='yes'))
#        or ((setininitial_step='yes' or usedininitial_step='yes') and (setinevaluate='yes' or setinnoise='yes' or setinfinal='yes'
#        or usedinevaluate='yes' or usedinnoise='yes' or usedinfinal='yes' or output='yes'))
#        or ((setinevaluate='yes' or usedinevaluate='yes') and (setinnoise='yes' or setinfinal='yes'
#          or usedinnoise='yes' or usedinfinal='yes' or output='yes'))
#        or ((setinnoise='yes' or usedinnoise='yes') and (setinfinal='yes' or usedinfinal='yes' or output='yes'))
#        or ((setinfinal='yes' or usedinfinal='yes') and output='yes')
#        or (setinmodel='no' and setininstance='no' and setinevaluate='no' and setinnoise='no' and setinfinal='no' and
#            usedinmodel='no' and usedininstance='no' and usedinevaluate='no' and usedinnoise='no' and usedinfinal='no' and output='yes')
#      ))]"
#      string="global_instance"/>
#    <admst:value-to select="isstate"
#      test="[input='no' and scope='global_instance' and setininitial_step='yes' and (setinevaluate='yes' or usedinevaluate='yes')]"
#      string="yes"/>
#  </admst:for-each>
#  <admst:template match="modify">
#    <admst:choose>
#      <admst:when test="[datatypename='block']">
#        <admst:apply-templates select="reverse(item)" match="modify"/>
#        <admst:value-to test="item[#modifys=1]" select="#modifys" path="1"/>
#        <admst:value-to test="item[#modifyd=1]" select="#modifyd" path="1"/>
#        <admst:value-to test="item[#modifyn=1]" select="#modifyn" path="1"/>
#        <admst:value-to test="item[#modifyc=1]" select="#modifyc" path="1"/>
#      </admst:when>
#      <admst:when test="[datatypename='conditional']">
#        <admst:apply-templates select="else|then" match="modify"/>
#        <admst:value-to test="[then/#modifys=1 or else/#modifys=1]" select="#modifys|if/#modifys|if/variable/#modifys" path="1"/>
#        <admst:value-to test="[then/#modifyd=1 or else/#modifyd=1]" select="#modifyd|if/#modifyd|if/variable/#modifyd" path="1"/>
#        <admst:value-to test="[then/#modifyn=1 or else/#modifyn=1]" select="#modifyn|if/#modifyn|if/variable/#modifyn" path="1"/>
#        <admst:value-to test="[then/#modifyc=1 or else/#modifyc=1]" select="#modifyc|if/#modifyc|if/variable/#modifyc" path="1"/>
#      </admst:when>
#      <admst:when test="[datatypename='whileloop']">
#        <admst:apply-templates select="whileblock" match="modify"/>
#        <admst:value-to test="[whileblock/#modifys=1]" select="#modifys|while/#modifys|while/variable/#modifys" path="1"/>
#        <admst:value-to test="[whileblock/#modifyd=1]" select="#modifyd|while/#modifyd|while/variable/#modifyd" path="1"/>
#        <admst:value-to test="[whileblock/#modifyn=1]" select="#modifyn|while/#modifyn|while/variable/#modifyn" path="1"/>
#        <admst:value-to test="[whileblock/#modifyc=1]" select="#modifyc|while/#modifyc|while/variable/#modifyc" path="1"/>
#        <admst:apply-templates select="whileblock" match="modify"/>
#      </admst:when>
#      <admst:when test="[datatypename='forloop']">
#        <admst:choose>
#          <admst:when test="[update/lhs/datatypename='array']">
#            <admst:variable name="lhs" path="update/lhs/variable"/>
#          </admst:when>
#          <admst:otherwise>
#            <admst:variable name="lhs" path="update/lhs"/>
#          </admst:otherwise>
#        </admst:choose>
#        <admst:apply-templates select="forblock" match="modify"/>
#        <admst:value-to test="[forblock/#modifys=1]" select="#modifys|(condition|update)/#modifys|(condition|update/rhs)/($lhs|variable)/#modifys" path="1"/>
#        <admst:value-to test="[forblock/#modifyd=1]" select="#modifyd|(condition|update)/#modifyd|(condition|update/rhs)/($lhs|variable)/#modifyd" path="1"/>
#        <admst:value-to test="[forblock/#modifyn=1]" select="#modifyn|(condition|update)/#modifyn|(condition|update/rhs)/($lhs|variable)/#modifyn" path="1"/>
#        <admst:value-to test="[forblock/#modifyc=1]" select="#modifyc|(condition|update)/#modifyc|(condition|update/rhs)/($lhs|variable)/#modifyc" path="1"/>
#        <admst:apply-templates select="forblock" match="modify"/>
#      </admst:when>
#      <admst:when test="[datatypename='case']">
#        <admst:apply-templates select="caseitem/code" match="modify"/>
#        <admst:for-each select="caseitem">
#          <admst:value-to test="[code/#modifys=1 and defaultcase='no']" select="#modifys|condition/#modifys|condition/@variable/#modifys" path="1"/>
#          <admst:value-to test="[code/#modifyd=1 and defaultcase='no']" select="#modifyd|condition/#modifyd|condition/@variable/#modifyd" path="1"/>
#          <admst:value-to test="[code/#modifyn=1 and defaultcase='no']" select="#modifyn|condition/#modifyn|condition/@variable/#modifyn" path="1"/>
#          <admst:value-to test="[code/#modifyc=1 and defaultcase='no']" select="#modifyc|condition/#modifyc|condition/@variable/#modifyc" path="1"/>
#        </admst:for-each>
#        <admst:value-to test="caseitem[#modifys=1]" select="#modifys|case/@variable/#modifys" path="1"/>
#        <admst:value-to test="caseitem[#modifyd=1]" select="#modifyd|case/@variable/#modifyd" path="1"/>
#        <admst:value-to test="caseitem[#modifyn=1]" select="#modifyn|case/@variable/#modifyn" path="1"/>
#        <admst:value-to test="caseitem[#modifyc=1]" select="#modifyc|case/@variable/#modifyc" path="1"/>
#      </admst:when>
#      <admst:when test="[datatypename='assignment']">
#        <admst:choose>
#          <admst:when test="[lhs/datatypename='array']">
#            <admst:variable name="lhs" path="lhs/variable"/>
#          </admst:when>
#          <admst:otherwise>
#            <admst:variable name="lhs" path="lhs"/>
#          </admst:otherwise>
#        </admst:choose>
#        <admst:value-to test="$lhs[exists(prototype/instance[#modifys=1])]" select="#modifys|rhs/#modifys|rhs/variable/#modifys" path="1"/>
#        <admst:value-to test="$lhs[exists(prototype/instance[#modifyd=1])]" select="#modifyd|rhs/#modifys|rhs/variable/#modifyd" path="1"/>
#        <admst:value-to test="$lhs[exists(prototype/instance[#modifyn=1])]" select="#modifyn|rhs/#modifys|rhs/variable/#modifyn" path="1"/>
#        <admst:value-to test="$lhs[exists(prototype/instance[#modifyc=1])]" select="#modifyc|rhs/#modifys|rhs/variable/#modifyc" path="1"/>
#        <admst:value-to test="$lhs/ddxprobe" select="#ddxprobe" string="yes"/>
#        <admst:push into="rhs/variable/ddxprobe" select="$lhs/ddxprobe" onduplicate="ignore"/>
#      </admst:when>
#      <admst:when test="[datatypename='contribution']">
#        <admst:choose>
#          <admst:when test="[#fixmedynamic=1]">
#            <admst:value-to select="#modifyd|(lhs|rhs|rhs/variable)/#modifyd" path="1"/>
#          </admst:when>
#          <admst:when test="[#fixmeflickernoise=1]">
#            <admst:value-to select="flickernoise|lhs/flickernoise" string="yes"/>
#            <admst:value-to select="#modifyn|(lhs|rhs|rhs/variable)/#modifyn" path="1"/>
#          </admst:when>
#          <admst:when test="[#fixmewhitenoise=1]">
#            <admst:value-to select="whitenoise|lhs/whitenoise" string="yes"/>
#            <admst:value-to select="#modifyn|(lhs|rhs|rhs/variable)/#modifyn" path="1"/>
#          </admst:when>
#          <admst:otherwise>
#            <admst:value-to select="#modifys|(lhs|rhs|rhs/variable)/#modifys" path="1"/>
#          </admst:otherwise>
#        </admst:choose>
#      </admst:when>
#      <admst:when test="[datatypename='blockvariable']">
#      </admst:when>
#      <admst:when test="[datatypename='nilled']"/>
#      <admst:when test="[datatypename='callfunction']">
#        <admst:value-to select="#modifyc|function/arguments/variable/#modifyc" path="1"/>
#      </admst:when>
#      <admst:otherwise><admst:fatal format="%(datatypename): case not handled\n"/></admst:otherwise>
#    </admst:choose>
#  </admst:template>
#  <admst:apply-templates select="analog/code" match="modify"/>
#  <admst:push into="@analogitems" select="assignment|assignment/rhs|contribution|contribution/rhs|block|forloop|whileloop|case|callfunction|conditional|conditional/if"/>
#  <admst:value-to select="@analogitems[#modifys=1 or #modifyn=1 or #modifyc=1]/static" string="yes"/>
#  <admst:value-to select="@analogitems[#modifys!=1 and #modifyn!=1 and #modifyc!=1]/dynamic" string="yes"/>
#
#  <admst:value-to select="(.|blockvariable)/variable[exists(instance[#modifys=1])]/#modifys" path="1"/>
#  <admst:value-to select="(.|blockvariable)/variable[exists(instance[#modifyd=1])]/#modifyd" path="1"/>
#  <admst:value-to select="(.|blockvariable)/variable[exists(instance[#modifyn=1])]/#modifyn" path="1"/>
#  <admst:value-to select="(.|blockvariable)/variable[exists(instance[#modifyc=1])]/#modifyc" path="1"/>
#
#  <!-- let's try not counting noise source use as "insource", because Xyce
#       only uses "insource" to figure out if we need derivatives.  We don't
#       need derivatives for noise-only sources -->
#
#  <!-- <admst:value-to select="(.|blockvariable)/variable[exists(instance[#modifys=1 or #modifyd=1 or #modifyn=1])]/insource" string="yes"/> -->
#  <admst:value-to select="(.|blockvariable)/variable[exists(instance[#modifys=1 or #modifyd=1])]/insource" string="yes"/>
#  <admst:value-to select="(.|blockvariable)/variable[exists(instance[#modifys=1 or #modifyn=1 or #modifyc=1])]/static" string="yes"/>
#  <admst:value-to select="(.|blockvariable)/variable[exists(instance[#modifyd=1])]/dynamic" string="yes"/>
#  <admst:value-to select="source[#modifys=1 or #modifyn=1]/static" string="yes"/>
#  <admst:value-to select="source[#modifyd=1]/dynamic" string="yes"/>
#
#  <!-- jacobian -->
#  <admst:for-each select="contribution">
#    <admst:variable name="mycontribution" path="."/>
#    <admst:variable name="mysource" path="lhs"/>
#    <admst:push into="$mysource/attribute" select="attribute"/>
#    <!-- case I() <+ .V(). -->
#    <admst:for-each select="rhs/probe[(nature=discipline/potential)and($mysource/nature=$mysource/discipline/flow)]">
#      <admst:new datatype="jacobian" inputs="module,$mysource/branch/pnode,branch/pnode">
#        <admst:push into="/@jacobian" select="." onduplicate="ignore"/>
#      </admst:new>
#      <admst:new test="branch/nnode[grounded='no']" datatype="jacobian" inputs="module,$mysource/branch/pnode,branch/nnode">
#        <admst:push into="/@jacobian" select="." onduplicate="ignore"/>
#      </admst:new>
#      <admst:new test="$mysource/branch/nnode[grounded='no']" datatype="jacobian" inputs="module,$mysource/branch/nnode,branch/pnode">
#        <admst:push into="/@jacobian" select="." onduplicate="ignore"/>
#        <admst:new test="../branch/nnode[grounded='no']" datatype="jacobian" inputs="module,$mysource/branch/nnode,../branch/nnode">
#          <admst:push into="/@jacobian" select="." onduplicate="ignore"/>
#        </admst:new>
#      </admst:new>
#      <admst:for-each select="/reverse(@jacobian)">
#        <admst:choose>
#          <admst:when test="module/jacobian[row=../../row and column=../../column]">
#            <admst:variable name="jacobian" path="module/jacobian[row=../../row and column=../../column]"/>
#          </admst:when>
#          <admst:otherwise>
#            <admst:variable name="jacobian" path="."/>
#            <admst:value-to select="[row=column]/diagonal" string="yes"/>
#            <admst:push into="module/jacobian" select="."/>
#          </admst:otherwise>
#        </admst:choose>
#        <admst:value-to test="$mycontribution[dynamic='yes']" select="$jacobian/dynamic" string="yes"/>
#        <admst:value-to test="$mycontribution[dynamic='no']" select="$jacobian/static" string="yes"/>
#      </admst:for-each>
#      <admst:value-to select="/@jacobian"/>
#    </admst:for-each>
#  </admst:for-each>
#  <admst:reverse select="jacobian"/>
#</admst:template>
#
#<admst:template match="adms.implicit.xml.nature">
#  <admst:reverse select="/argv|/discipline|/nature"/>
#  <admst:for-each select="/nature">
#    <admst:value-to select="ddt_nature" path="/nature[name='%(../../ddt_name)']"/>
#    <admst:value-to select="idt_nature" path="/nature[name='%(../../idt_name)']"/>
#  </admst:for-each>
#</admst:template>
#
#<admst:template match="adms.implicit.xml">
#  <admst:apply-templates select="." match="adms.implicit.xml.nature"/>
#  <admst:apply-templates select="/module" match="adms.implicit.xml.module"/>
#</admst:template>
#
#<admst:apply-templates select="." match="adms.implicit.xml"/>
#
#<!--admst:sendmail>
#  <admst:subject>automatic mailing from %(/simulator/fullname)</admst:subject>
#  <admst:arguments recipient="%(/simulator/fullname)"/>
#  <admst:to recipient="r29173@freescale.com"/>
#  <admst:message>
#  </admst:message>
#</admst:sendmail-->
#
#
#</admst>

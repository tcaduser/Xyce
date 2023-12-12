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

    scalingunits = {
      '1' : '',
      'E' : 'e+18',
      'P' : 'e+15',
      'T' : 'e+12',
      'G' : 'e+9',
      'M' : 'e+6',
      'k' : 'e+3',
      'h' : 'e+2',
      'D' : 'e+1',
      'd' : 'e-1',
      'c' : 'e-2',
      'm' : 'e-3',
      'u' : 'e-6',
      'n' : 'e-9',
      'A' : 'e-10',
      'p' : 'e-12',
      'f' : 'e-15',
      'a' : 'e-18',
    }

    def visit_expression(self, expression):
        self.globalexpression = expression

        expression.variable = expression.create_reference_list()
        expression.probe = expression.create_reference_list()
        expression.function = expression.create_reference_list()

        tree = expression.tree()
        #if self.globalexpression is None:
        #    print(expression)
        #    raise RuntimeError("JJJJJ")
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
        f = partitionning_map[self.globalpartitionning]
        for v in expression.variable.get_list():
            f(v)
        if hasattr(tree, 'math'):
            expression.math = tree.math

    def visit_probe(self, probe):
        probe.dependency = 'linear'
        self.globalexpression.probe.append(probe, True)

        if self.globalhandleafoutputs:
            self.globalaf.probe.append(probe.id, True)

    def visit_array(self, array):
        array.visit(array.variable)
        array.dependency = array.variable().dependency

    def visit_variable(self, variable):
        if self.globalexpression is not None:
            self.globalexpression.probe.extend(variable.probe, True)
            self.globalexpression.variable.append(variable, True)
        if self.globaltreenode is not None:
            self.globaltreenode.variable.append(variable, True)
        variable.dependency = variable.prototype().dependency

        if self.globalhandleafoutputs:
            self.globalaf.probe.extend(variable.probe, True)
            self.globalaf.variable.extend(variable, True)

    def visit_mapply_unary(self, unary):
        arg = unary.args.get_head()
        arg.visit(self)
        unary.dependency = arg.dependency
        #unary.math = f'-({arg.math})'

    def visit_mapply_binary(self, binary):
        args = list(binary.args.get_list())
        for arg in args:
            arg.visit(self)
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
        deps = [x.dependency for x in args]
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
            definition = function.definition
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
        if (self.globalexpression is not None) and (function.dependency in ('linear', 'nonlinear')):
            self.globalexpression.hasVoltageDependentFunction = True

        function.subexpression = self.globalexpression
        if name == 'ddt':
            if self.globalcontribution is not None:
                self.globalcontribution.fixmedynamic = True
        elif name == 'white_noise':
            if self.globalcontribution is not None:
                self.globalcontribution.fixmewhitenoise = True
        elif name == 'flicker_noise':
            if self.globalcontribution is not None:
                self.globalcontribution.fixmeflickernoise = True
        elif name == '$temperature':
            self.globalassignment.lhs().TemperatureDependent = True

        if name in (
            '$abstime',
            '$realtime',
            '$temperature',
            '$vt',
            'idt',
            'ddt',
            '$param_given',
            '$port_connected',
            '$given',
            'ddx',
            'flicker_noise',
            'white_noise',
        ):
            pass
#        <!-- Table 4-14 - Standard Functions -->
#        <!-- Table 4-15 - Trigonometric and Hyperbolic Functions-->
        elif name in (
            'analysis',
            '$analysis',
            '$simparam',
            'simparam',
            '$shrinka',
            '$shrinkl',
            '$limexp',
            'limexp',
            '$limit',
            'ln',
            'log',
            'exp',
            'sqrt',
            'min',
            'max',
            'abs',
            'pow',
            'floor',
            'ceil',
            'sin',
            'cos',
            'tan',
            'asin',
            'acos',
            'atan',
            'atan2',
            'hypot',
            'sinh',
            'cosh',
            'tanh',
            'asinh',
            'acosh',
            'atanh',
        ):
            self.globalexpression.function.append(function)
        elif name == 'transition':
            self.globalexpression.function.append(function)
        else:
            if not hasattr(function, 'definition'):
                raise RuntimeError(f'analog function {name} is undefined')
            self.globalexpression.function = function

    def visit_number(self, number):
        number.dependency = 'constant'
        scalingunit = self.scalingunits[number.scalingunit]
        number.value = number.lexval().string + scalingunit

    def visit_string(self, string):
        string.dependency = 'constant'

#above is expression dependency

    def visit_callfunction(self, callfunction):
        for f in callfunction.function().arguments:
            f.visit(self)
        callfunction.dependency = callfunction.function().dependency
#
    def visit_whileloop(self, whileloop):
        While = whileloop.While()
        whileblock = whileloop.whileblock()
        While.visit(self)
        if self.globalopdependent or While.dependency == 'constant':
            whileblock.visit(self)
        if not self.globalopdependent:
            if While.dependency == 'constant':
                whileloop.While.visit(self)
            if While.dependency != 'constant':
                self.globalopdependent = True
                whileblock.visit(self)
                self.globalopdependent = False

        if whileblock.dependency == 'nonlinear':
            whileloop.dependency = 'nonlinear'
        elif whileblock.dependency == 'linear':
            whileloop.dependency = 'linear'
        elif (While.dependency != 'constant') or (whileblock.dependency == 'noprobe'):
            whileloop.dependency = 'noprobe'
        else:
            whileloop.dependency = 'constant'

    def visit_forloop(self, forloop):
#      <!-- Xyce:  The original code for this had broken conditionals that
#           could, in some cases, allow dependency to be called twice on
#           the "forblock".  This is catastrophic and should not happen.
#           Let's try to accomplish the dependency scanning without that
#           logical hole -->
        for i in(forloop.initial(), forloop.update(), forloop.condition()):
            i.visit(self)
        forblock = foorloop.forblock()
        if not self.globalopdependent:
            self.globalopdependent = True
            forblock.visit(self)
            self.globalopdependent = False
            for i in(forloop.initial(), forloop.update(), forloop.condition()):
                if i.dependency == 'constant':
                    i.visit(self)
        else:
            forblock.visit(self)
            for i in(forloop.initial(), forloop.update(), forloop.condition()):
                if i.dependency == 'constant':
                    i.visit(self)
            if forblock.dependency == 'nonlinear':
                forloop.dependency = 'nonlinear'
            elif forblock.dependency == 'linear':
                forloop.dependency = 'linear'
            elif (forloop.condition().dependency != 'constant' or forloop.initial().dependency() != 'constant') or forblock.dependency == 'noprobe':
                forloop.dependency = 'noprobe'
            else:
                forloop.dependency = 'constant'

    def visit_case(self, Case):
        self.globaltreenode = Case
        Case.visit(self)
        self.globaltreenode = None
        for ci in Case.caseitem.get_list():
            for co in ci.condition.get_list():
                self.globaltreenode = co
                co.visit(self)
                self.globaltreenode = None
            ci.visit(self)

    def visit_conditional(self, conditional):
        self.globalmodule.conditional.append(conditional.id)
        conditional.If().visit(self)
        if (not self.globalopdependent) and conditional.If().dependency != 'constant':
            self.globalopdependent = True
            conditional.Then().visit(self)
            if conditional.Else:
                conditional.Else().visit(self)
            self.globalopdependent = False
        else:
            conditional.Then().visit(self)
            if conditional.Else:
                conditional.Else().visit(self)
        if conditional.Else:
            deps = [conditional.Then().dependency, conditional.Else().dependency]
        else:
            deps = [conditional.Then().dependency,]
        conditional.dependency = 'constant'
        for d in ('nonlinear', 'linear', 'noprobe',):
            if d in deps:
                conditional.dependency = d
                break

    def visit_contribution(self, contribution):
        self.globalcontribution = contribution
        contribution.rhs().visit(self)
        self.globalcontribution = None
        contribution.lhs().probe
        for probe in contribution.rhs().probe.get_list():
            contribution.lhs().probe.append(probe, True)
        contribution.dependency = 'nonlinear'

    def visit_assignment(self, assignment):
        assignment.TemperatureDependent = False
        ldn = assignment.get_datatypename()
        if ldn == 'array':
            lhs = assignment.lhs().variable()
        else:
            lhs = assignment.lhs()

        if self.globalpartitionning == 'initial_model':
            lhs.prototype().setinmodel = True
        elif self.globalpartitionning == 'initial_instance':
            lhs.prototype().setininstance = True
        elif self.globalpartitionning == 'initial_step':
            lhs.prototype().setininitial_step = True
        elif self.globalpartitionning == 'noise':
            lhs.prototype().setinnoise = True
        elif self.globalpartitionning == 'final_step':
            lhs.prototype().setinfinal = True
        else:
            lhs.prototype().setinevaluate = True

        self.globalassignment = assignment
        rhs = assignment.rhs()
        rhs.visit(self)
        self.globalassignment = None

        if not hasattr(lhs, 'variable'):
            lhs.variable = []

        lhs.TemperatureDependent = False
        for x in rhs.variable.get_list():
            if x not in lhs.variable:
                lhs.variable.append(x)
                if hasattr(rhs, 'TemperatureDependent') and rhs.TemperatureDependent:
                    lhs.TemperatureDependent = rhs.TemperatureDependent
        assignment.dependency = rhs.dependency

        deps = [lhs.prototype().dependency, rhs.dependency]

        lhs.dependency = 'constant'
        lhs.prototype().dependency = 'constant'
        isset = False
        for d in ('nonlinear', 'linear', 'noprobe'):
            if d in deps:
                lhs.dependency = d
                lhs.prototype().dependency = d
                isset = True
                break

        if (not isset) and self.globalopdependent:
            lhs.dependency = 'noprobe'
            lhs.prototype().dependency = 'noprobe'
        for probe in rhs.probe.get_list():
            lhs.probe.append(probe, True)

    def visit_block(self, block):
        forcepartitionning = True
        name = block.lexval
        if name in  ('initial_model', 'initial_instance', 'initial_step', 'noise', 'final_step,'):
            self.globalpartitionning = name
            forcepartitionning = True
        else:
            forcepartitionning = False

        for item in block.item.get_list():
            item.visit(self)

        if forcepartitionning:
            self.globalpartitionning = ''

        deps = set([x.dependency for x in block.item.get_list()])
        block.dependency = 'constant'
        for d in ('nonlinear', 'linear', 'noprobe'):
            if d in deps:
                block.dependency = d
                break

    def visit_nilled(self, nilled):
        nilled.dependency = 'constant'

    def visit_blockvariable(self, blockvariable):
        deps = set([x.dependency for x in blockvariable.variable.get_list()])
        blockvariable.dependency = 'constant'
        for d in ('nonlinear', 'linear', 'noprobe'):
            if d in deps:
                blockvariable.dependency = d
                break

    def visit_module(self, module):
        self.globalmodule = module

        for node in module.node.get_list():
            if node.location == 'ground':
                node.grounded = True
            else:
                node.grounded = False

        for branch in module.branch.get_list():
            # need to check both nnode and pnode for this and next
            branch.discipline = branch.pnode().discipline
            branch.grounded = branch.nnode().grounded

        for source in module.source.get_list():
            source.discipline = source.branch().discipline
            source.grounded = source.branch().grounded

        for probe in module.probe.get_list():
            probe.discipline = probe.branch().discipline
            probe.grounded = probe.branch().grounded

        for instance in module.instance.get_list():
            module.instantiator.append(instance, True)
#  <admst:for-each select="instance">
#    <admst:assert select="terminal" test="nodefrommodule[location='external']"
#                  format="%(../instantiator).%(nodefrommodule/name): is not terminal\n"/>
#    <admst:assert select="parameterset" test="parameter[input='yes']"
#                  format="%(../instantiator).%(parameter/name): is not input parameter\n"/>
#  </admst:for-each>

        for analogfunction in module.analogfunction.get_list():
            analogfunction.tree().visit(self)
            analogfunction.code().visit(self)

        for analog in module.analog.get_list():
            analog.code().visit(self)

        # this looks like module variable is actually variable prototype
        for v in module.variable.get_list():
            if v.dependency != 'constant':
                v.OPdependent = True
            v.output = v.input

            if 'type' in v.attributes:
                if v.attributes['type'] == 'instance':
                    v.parametertype = 'instance'
            elif 'ask' in v.attributes:
                if v.attributes['ask'] == 'yes':
                    v.output == True
                elif v.attributes['ask'] == 'no':
                    v.output == False
                else:
                    raise RuntimeError('not valid type')

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

            if v.default is not None:
                default = v.default()
                default.visit(self)

#    <admst:value-to
#       select="default[exists(tree[datatypename='mapply_unary' and name='minus' and arg1/datatypename='number' and arg1/value='1.0'])]/value"
#       string="is_neg_one"/>
#    <admst:value-to select="default[exists(tree[datatypename='number' and value='0.0'])]/value" string="is_zero"/>
#    <admst:value-to select="default[exists(tree[datatypename='number' and value='1.0'])]/value" string="is_one"/>

            v.scope = None
            if (v.input and v.parametertype=='model') or ((not v.input) and (v.setinmodel or v.usedinmodel)
                and (v.setininstance or v.setininitial_step or v.setinevaluate or v.setinnoise or v.setinfinal
                or v.usedininstance or v.usedininitial_step or v.usedinevaluate or v.usedinnoise or v.usedinfinal or v.output)):
                v.scope = "global_model"
            elif ((not v.input) and (not v.setinmodel) and (not v.usedinmodel) and
                (((v.setininstance or v.usedininstance) and (v.setininitial_step or v.setinevaluate or v.setinnoise or v.setinfinal
                or v.usedininitial_step or v.usedinevaluate or v.usedinnoise or v.usedinfinal or v.output))
                or ((v.setininitial_step or v.usedininitial_step) and (v.setinevaluate or v.setinnoise or v.setinfinal
                or v.usedinevaluate or v.usedinnoise or v.usedinfinal or v.output))
                or ((v.setinevaluate or v.usedinevaluate) and (v.setinnoise or v.setinfinal
                  or v.usedinnoise or v.usedinfinal or v.output))
                or ((v.setinnoise or v.usedinnoise) and (v.setinfinal or v.usedinfinal or v.output))
                or ((v.setinfinal or v.usedinfinal) and v.output)
                or ((not v.setinmodel) and (not v.setininstance) and (not v.setinevaluate) and (not v.setinnoise) and (not v.setinfinal) and
                    (not v.usedinmodel) and (not v.usedininstance) and (not v.usedinevaluate) and (not v.usedinnoise) and (not v.usedinfinal) and v.output)
              )):
                v.scope = 'global_instance'

            if (not v.input) and v.scope=='global_instance' and v.setininitial_step and (v.setinevaluate or v.usedinevaluate):
                v.isstate = True
            else:
                v.isstate = False

# MODIFY template in module
#### TODO: FINISH HERE
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

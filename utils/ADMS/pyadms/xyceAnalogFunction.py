'''
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE admst SYSTEM "/users/tvrusso/src/QucsADMS/ADMS/admst.dtd">
<admst version="2.3.0" xmlns:admst="http://mot-adms.sourceforge.net/xml-files/admst">

<!--
  Purpose:  Provide a set of ADMST templates for
            producing analog function declarations and implementations that
            do not rely on Sacado.

            The primary need here is for functions that return the derivatives
            of analog functions, as the templated functions provided in all
            prior implementations of Xyce/ADMS are adequate for the
            implementations that return the function values themselves.

            At least in the current plan, these functions will only be
            used in the normal (DC, AC, Transient, HB) contexts where
            only derivatives with respect to probes are needed, not in
            sensitivity context.  Providing flexible derivative
            computation with respect to arbitrary model or instance
            parameters is beyond the scope of the current work.

      Creator:   Tom Russo, SNL, Electrical Models and Simulation
      Creation Date: 10 Aug 2019

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

-->

<!-- One will note that there are a lot of templates here that
       appear in xyceBasicTemplates in much more involved form.  We
       have simpler needs here, and therefore have pared down the
       basic templates to their minimum.  Further, there are some
       differences that make the templates in xyceBasicTemplates
       unsuitable, so we can't just use them.  To prevent conflict,
       all the templates here that have similar function to a template
       in xyceBasicTemplates will have the "xyceAnalogFunctions:"
       prefix in their names.
-->

<!-- This declares the variable global, but doesn't assign anything
     to it. -->
'''

'''
<!--
    xyceAnalogFunctions:processTerm

given a node (which must be a part of the analog function currently
being processed, i.e. the one pointed to by $globalAnalogFunction,
and which must be an expression or subexpression element),
return the C++ representation of this node and its derivatives with
respect to all input variables of the function.

This template does little more than farm out the real work to
templates specific to the datatype of the node passed in.

See "xyceAnalogFunctions:expression", "xyceAnalogFunctions:variable",
"xyceAnalogFunctions:wmapply_unary", etc. for specifics of what's
getting done at lower level.  Each level returns the value of the
expression and its derivatives with respect to its input variables in
"returned" variables such as returnedExpression and 'd_exp_d_X' for
each X that is an input variable of the function.

This template returns the same set of return variables that the
subordinate template returned.
-->
'''

from . import xyce_implicit

class af:
    def __init__(self):
        self.globalAnalogFunction = None

    def get_derivative_variables(self):
        for v in self.globalAnalogFunction.variable.get_list():
            if not v.input:
                continue
            yield v

    def get_expression_derivative_name(self, name):
        return f'd_exp_d_{name}'

    def get_zero_derivatives(self):
        afdict = {}
        for k in [self.get_expression_derivative_name(v.name) for v in self.get_derivative_variables()]:
            afdict[k] = '0.0'

    def processTerm(self, arg):
        afdict = {}
        returnedExpression, returnedDiff = arg.visit(self)
        for v in self.globalAnalogFunction.variable.get_list():
            if not v.input:
                continue
            k = f'd_exp_d_{v.name}'
            returnedDiff[k] = v.returnedDiff[k]
        arg.returnedExpression = returnedExpression
        arg.returnedDiff = returnedDiff
        return expression, returnedDiff

    def visit_expression(self, expression):
        tree = expression.tree()
        tree.visit(self)
        expression.returnedExpression = tree.returnedExpression
        expression.returnedDiff = tree.returnedDiff
        return self.returnedExpression, self.returnedDiff

    def visit_number(self, number):
        # set in xyce_implicit
        self.returnedExpression = number.value
        self.returnedDiff = self.get_zero_derivatives()
        return self.returnedExpression, self.returnedDiff

    def visit_string(self, string):
        self.returnedExpression = f'"{string.value}"'
        self.returnedDiff = self.get_zero_derivatives()
        return self.returnedExpression, self.returnedDiff

    def visit_variable(self, variable):
        self.returnedExpression = variable.name
        self.returnedDiff = self.get_zero_derivatives()
        # TODO: set derivative to 0 if no real
        self.returnedDiff[self.get_expression_derivative_name(variable.name)] = '1.0'
        return self.returnedExpression, self.returnedDiff

    def visit_unary(self, unary):
        ops = {
            'plus', '+',
            'minus', '-',
            'not', '!',
            'bw_not', '~',
        }
        op = ops[unary.name]

        arg1 = unary.args.get_item(0)
        #TODO: maybe get rid of premature optimization until later
        #if arg1.value = 0.0:
        #    self.returnedExpression = '0.0'
        #    self.returnedDiff = self.get_zero_derivatives()
        #else:
        returnedExpression, returnedDiff = arg1.visit(self)
        self.returnedExpression = f'({op} {returnedExpression})'
        for k, v in returnedDiff.items():
            self.returnedDiff[k] = f'({op} {v})'

        return self.returnedExpression, self.returnedDiff


#<!-- binary operators -->
#<admst:template match="xyceAnalogFunctions:mapply_binary">
#  <!-- process arguments and get their derivatives -->
#  <admst:apply-templates select="arg1" match="xyceAnalogFunctions:processTerm">
#    <admst:value-of select="returned('returnedExpression')/value"/>
#    <admst:variable name="a1" select="%s"/>
#    <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#      <admst:value-of select="name"/>
#      <admst:value-of select="returned('d_exp_d_%s')/value"/>
#      <admst:value-of select="name"/>
#      <admst:variable name="d_a1_d_%s" select="%s"/>
#    </admst:for-each>
#  </admst:apply-templates>
#  <admst:apply-templates select="arg2" match="xyceAnalogFunctions:processTerm">
#    <admst:value-of select="returned('returnedExpression')/value"/>
#    <admst:variable name="a2" select="%s"/>
#    <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#      <admst:value-of select="name"/>
#      <admst:value-of select="returned('d_exp_d_%s')/value"/>
#      <admst:value-of select="name"/>
#      <admst:variable name="d_a2_d_%s" select="%s"/>
#    </admst:for-each>
#  </admst:apply-templates>
#  <admst:choose>
#    <!-- addition -->
#    <admst:when test="[name='addp']">
#      <admst:choose>
#        <admst:when test="[(arg1/math/value=0.0)and(arg2/math/value=0.0)]">
#          <admst:variable name="expression" select="0.0"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="d_exp_d_%s" value="0.0"/>
#          </admst:for-each>
#        </admst:when>
#        <admst:when test="[arg1/math/value=0.0]">
#          <admst:variable name="expression" select="(+%($a2))"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="a2Deriv" select="$(d_a2_d_%s)"/>
#            <admst:choose>
#              <admst:when test="[$a2Deriv = '0.0']">
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="(+%($a2Deriv))"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:for-each>
#        </admst:when>
#        <admst:when test="[arg2/math/value=0.0]">
#          <admst:variable name="expression" select="(%($a1))"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="a1Deriv" select="$(d_a1_d_%s)"/>
#            <admst:choose>
#              <admst:when test="[$a1Deriv = '0.0']">
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="(%($a1Deriv))"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:for-each>
#        </admst:when>
#        <admst:otherwise>
#          <admst:variable name="expression" select="($a1+$a2)"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="a1Deriv" select="$(d_a1_d_%s)"/>
#            <admst:value-of select="name"/>
#            <admst:variable name="a2Deriv" select="$(d_a2_d_%s)"/>
#            <admst:choose>
#              <admst:when test="[$a1Deriv = '0.0' and $a2Deriv ='0.0']">
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="0.0"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '0.0']">
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="$a2Deriv"/>
#              </admst:when>
#              <admst:when test="[$a2Deriv = '0.0']">
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="$a1Deriv"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="($a1Deriv+$a2Deriv)"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:for-each>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#
#    <!-- subtraction -->
#    <admst:when test="[name='addm']">
#      <admst:choose>
#        <admst:when test="[(arg1/math/value=0.0)and(arg2/math/value=0.0)]">
#          <admst:variable name="expression" select="0.0"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="d_exp_d_%s" value="0.0"/>
#          </admst:for-each>
#        </admst:when>
#        <admst:when test="[arg1/math/value=0.0]">
#          <admst:variable name="expression" select="(-%($a2))"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="a2Deriv" select="$(d_a2_d_%s)"/>
#            <admst:choose>
#              <admst:when test="[$a2Deriv = '0.0']">
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="(-%($a2Deriv))"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:for-each>
#        </admst:when>
#        <admst:when test="[arg2/math/value=0.0]">
#          <admst:variable name="expression" select="(%($a1))"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="a1Deriv" select="$(d_a1_d_%s)"/>
#            <admst:choose>
#              <admst:when test="[$a1Deriv = '0.0']">
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" value="0.0"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="(%($a1Deriv))"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:for-each>
#        </admst:when>
#        <admst:otherwise>
#          <admst:variable name="expression" select="($a1-$a2)"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="a1Deriv" select="$(d_a1_d_%s)"/>
#            <admst:value-of select="name"/>
#            <admst:variable name="a2Deriv" select="$(d_a2_d_%s)"/>
#            <admst:choose>
#              <admst:when test="[$a1Deriv = '0.0' and $a2Deriv ='0.0']">
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" value="0.0"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '0.0']">
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="(-$a2Deriv)"/>
#              </admst:when>
#              <admst:when test="[$a2Deriv = '0.0']">
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="$a1Deriv"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:value-of select="name"/>
#                <admst:variable name="d_exp_d_%s" select="($a1Deriv-$a2Deriv)"/>
#              </admst:otherwise>
#            </admst:choose>
#          </admst:for-each>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#
#    <!-- multiplication -->
#    <admst:when test="[name='multtime']">
#      <admst:choose>
#        <admst:when test="[(arg1/math/value=0.0)or(arg2/math/value=0.0)]">
#          <admst:variable name="expression" select="0.0"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="d_exp_d_%s" value="0.0"/>
#          </admst:for-each>
#        </admst:when>
#        <admst:when test="[(arg1/math/value=1.0)and(arg2/math/value=1.0)]">
#          <admst:variable name="expression" select="1.0"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="d_exp_d_%s" value="0.0"/>
#          </admst:for-each>
#        </admst:when>
#        <admst:otherwise>
#          <admst:variable name="expression" select="($a1*$a2)"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="a1Deriv" select="$(d_a1_d_%s)"/>
#            <admst:value-of select="name"/>
#            <admst:variable name="a2Deriv" select="$(d_a2_d_%s)"/>
#            <admst:choose>
#              <admst:when test="[$a1Deriv = '0.0' and $a2Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="0.0"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '0.0' and $a2Deriv = '1.0']">
#                <admst:variable name="expressionDeriv" select="($a1)"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '1.0' and $a2Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="($a2)"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '1.0' and $a2Deriv = '1.0']">
#                <admst:variable name="expressionDeriv" select="($a1+$a2)"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="($a1*$a2Deriv)"/>
#              </admst:when>
#              <admst:when test="[$a2Deriv = '0.0']">
#                <admst:variable name="expressionDeriv" select="($a1Deriv*$a2)"/>
#              </admst:when>
#              <admst:when test="[$a1Deriv = '1.0']">
#                <admst:variable name="expressionDeriv" select="($a1*$a2Deriv+$a2)"/>
#              </admst:when>
#              <admst:when test="[$a2Deriv = '1.0']">
#                <admst:variable name="expressionDeriv" select="($a1+$a2*$a1Deriv)"/>
#              </admst:when>
#              <admst:when test="[$a1 = '1.0']">
#                <admst:variable name="expressionDeriv" select="($a2Deriv)"/>
#              </admst:when>
#              <admst:when test="[$a2 = '1.0']">
#                <admst:variable name="expressionDeriv" select="($a1Deriv)"/>
#              </admst:when>
#              <admst:otherwise>
#                <admst:variable name="expressionDeriv" select="(($a1*$a2Deriv)+($a1Deriv*$a2))"/>
#              </admst:otherwise>
#            </admst:choose>
#            <admst:value-of select="name"/>
#            <admst:variable name="d_exp_d_%s" select="$expressionDeriv"/>
#          </admst:for-each>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:when test="[name='multdiv']">
#      <admst:choose>
#        <admst:when test="[arg1/math/value=0.0]">
#          <admst:variable name="expression" select="0.0"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="d_exp_d_%s" value="0.0"/>
#          </admst:for-each>
#        </admst:when>
#        <admst:when test="[(arg1/math/value=1.0)and(arg2/math/value=1.0)]">
#          <admst:variable name="expression" select="1.0"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="d_exp_d_%s" value="0.0"/>
#          </admst:for-each>
#        </admst:when>
#        <admst:otherwise>
#          <admst:variable name="expression" select="($a1/$a2)"/>
#          <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#            <admst:value-of select="name"/>
#            <admst:variable name="a1Deriv" select="$(d_a1_d_%s)"/>
#            <admst:value-of select="name"/>
#            <admst:variable name="a2Deriv" select="$(d_a2_d_%s)"/>
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
#            <admst:value-of select="name"/>
#            <admst:variable name="d_exp_d_%s" select="$expressionDeriv"/>
#          </admst:for-each>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:otherwise>
#      <admst:variable name="expression" select="($a1%(bname(.)/[name='bname']/value)$a2)"/>
#      <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#        <admst:value-of select="name"/>
#        <admst:variable name="d_exp_d_%s" value="0.0"/>
#      </admst:for-each>
#    </admst:otherwise>
#  </admst:choose>
#
#  <admst:return name="returnedExpression" value="$expression"/>
#  <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#    <admst:value-of select="name"/>
#    <admst:value-of select="name"/>
#    <admst:return name="d_exp_d_%s" value="$(d_exp_d_%s)"/>
#  </admst:for-each>
#
#</admst:template>
#
#<!-- Ternary operator (condition)?iftrue:iffalse -->
#
#<admst:template match="xyceAnalogFunctions:mapply_ternary">
#  <!-- derivatives of conditional are not needed -->
#  <admst:apply-templates select="arg1" match="xyceAnalogFunctions:processTerm">
#    <admst:value-of select="returned('returnedExpression')/value"/>
#    <admst:variable name="a1" select="%s"/>
#  </admst:apply-templates>
#  <admst:apply-templates select="arg2" match="xyceAnalogFunctions:processTerm">
#    <admst:value-of select="returned('returnedExpression')/value"/>
#    <admst:variable name="a2" select="%s"/>
#    <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#      <admst:value-of select="name"/>
#      <admst:value-of select="returned('d_exp_d_%s')/value"/>
#      <admst:value-of select="name"/>
#      <admst:variable name="d_a2_d_%s" select="%s"/>
#    </admst:for-each>
#  </admst:apply-templates>
#  <admst:apply-templates select="arg3" match="xyceAnalogFunctions:processTerm">
#    <admst:value-of select="returned('returnedExpression')/value"/>
#    <admst:variable name="a3" select="%s"/>
#    <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#      <admst:value-of select="name"/>
#      <admst:value-of select="returned('d_exp_d_%s')/value"/>
#      <admst:value-of select="name"/>
#      <admst:variable name="d_a3_d_%s" select="%s"/>
#    </admst:for-each>
#  </admst:apply-templates>
#  <admst:variable name="expression" select="($a1?$a2:$a3)"/>
#  <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#    <admst:value-of select="name"/>
#    <admst:variable name="a2Deriv" select="$(d_a2_d_%s)"/>
#    <admst:value-of select="name"/>
#    <admst:variable name="a3Deriv" select="$(d_a3_d_%s)"/>
#    <admst:value-of select="name"/>
#    <admst:variable name="d_exp_d_%s" select="($a1?$a2Deriv:$a3Deriv)"/>
#  </admst:for-each>
#  <admst:return name="returnedExpression" value="$expression"/>
#  <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#    <admst:value-of select="name"/>
#    <admst:value-of select="name"/>
#    <admst:return name="d_exp_d_%s" value="$(d_exp_d_%s)"/>
#  </admst:for-each>
#</admst:template>
#
#<!-- Function call -->
#<admst:template match="xyceAnalogFunctions:function">
#  <admst:variable name="doingAnalogFunctionCall" value="no"/>
#  <admst:variable name="funcname" select="%(xyceAnalogFunctions:funcname(.)/[name='fname']/value)"/>
#  <admst:variable name="args" select=""/>
#  <admst:variable name="thisFunctionCall" path="."/>
#  <admst:if test="[$funcname='hypot']">
#    <admst:assert test="arguments[count(.)=2]" format="hypot function must take exactly two arguments.\n"/>
#  </admst:if>
#  <admst:for-each select="arguments">
#    <admst:if test="[not($args='')]">
#      <admst:variable name="args" select="$args,"/>
#    </admst:if>
#    <admst:value-of select="index(../arguments,.)"/>
#    <admst:variable name="index" select="%s"/>
#
#    <admst:apply-templates select="." match="xyceAnalogFunctions:processTerm">
#      <admst:variable name="arg$(index)" select="%(returned('returnedExpression')/value)"/>
#      <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#        <admst:value-of select="name"/>
#        <admst:value-of select="returned('d_exp_d_%s')/value"/>
#        <admst:value-of select="name"/>
#        <admst:variable name="d_arg$(index)_d_%s" select="%s"/>
#      </admst:for-each>
#      <admst:choose>
#        <admst:when test="[../name='min' or ../name='max']">
#          <!-- this is ridiculously over-conservative, and may be better done
#               by calling xyceAnalogFunctions:realArgument, but right now
#               I'm just going with the over-conservative -->
#          <admst:variable name="args" select="$args static_cast&lt;double&gt;($(arg$index))"/>
#        </admst:when>
#        <admst:when test="[(../definition/datatypename='analogfunction') and ((datatypename='number') or (datatypename='variable' and type='integer'))]">
#          <admst:variable name="argtype" select="huh?" />
#          <admst:for-each select="../definition/variable[input='yes' or (output='yes' and name !=$thisFunctionCall/name)]">
#            <admst:if test="[position(.)-1=$index]">
#              <admst:variable name="argtype" select="%(type)"/>
#            </admst:if>
#          </admst:for-each>
#          <admst:choose>
#            <admst:when test="[$argtype='real']">
#              <admst:variable name="args" select="$args static_cast&lt;double&gt;($(arg$index))"/>
#            </admst:when>
#            <admst:otherwise>
#                <admst:variable name="args" select="$args$(arg$index)"/>
#            </admst:otherwise>
#          </admst:choose>
#        </admst:when>
#        <admst:otherwise>
#          <admst:variable name="args" select="$args$(arg$index)"/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:apply-templates>
#  </admst:for-each>
#
#  <!-- We now have all our arguments collected up in "$args", each
#       individual argument in $arg#, and each argument's derivatives
#       in the $d_arg#_d_name variables.  Form the actual function call
#       and its derivatives.  Note:  "index" returns zero-based indices -->
#  <admst:choose>
#    <admst:when test="[$funcname='\$vt']">
#      <admst:choose>
#        <admst:when test="[$args='']">
#          <admst:fatal format="Illegal to use \$vt with no argument in analog function\n"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:variable name="expression" value="adms_vt($args)"/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <!-- this special case doesn't follow the same pattern as other
#         simple function calls.  We have also already handled misuse
#         of the call above, so just assume we have two args here -->
#    <admst:when test="[$funcname='hypot']">
#      <admst:variable name="expression" select="sqrt(%($arg0)*%($arg0)+%($arg1)*%($arg1))"/>
#    </admst:when>
#    <admst:otherwise>
#      <admst:variable name="expression" select="$funcname($args)"/>
#    </admst:otherwise>
#  </admst:choose>
#
#  <!-- Now let us construct expressions for the derivative of the function
#       with respect to its arguments. These will be stored in d_f_d#, where
#       # is the index (zero-based) of the argument -->
#  <admst:choose>
#    <admst:when test="[name='\$vt']">
#      <admst:variable name="d_f_d0" value="CONSTKoverQ"/>
#    </admst:when>
#    <admst:when test="[name='exp' or name='ln' or name='log' or name='sqrt' or name='abs' or name='limexp' or name='cos' or name='sin' or name='tan' or name='acos' or name='asin' or name='atan' or name='cosh' or name='sinh' or name='tanh' or name='acosh' or name='asinh' or name='atanh' or name='ceil' or name='floor']">
#      <!-- functions of one argument, set "d_f_d0" to the expression for
#           the derivative of f(x)/dx where x is the argument -->
#      <admst:choose>
#        <admst:when test="[name='exp']">
#          <admst:variable name="d_f_d0" select="exp(%($arg0))"/>
#        </admst:when>
#        <admst:when test="[name='ln']">
#          <admst:variable name="d_f_d0" select="(1.0/%($arg0))"/>
#        </admst:when>
#        <admst:when test="[name='log']">
#          <admst:variable name="d_f_d0" select="(1.0/(log(10.0)*%($arg0)))"/>
#        </admst:when>
#        <admst:when test="[name='sqrt']">
#          <admst:variable name="d_f_d0" select="(0.5/sqrt(%($arg0)))"/>
#        </admst:when>
#        <admst:when test="[name='abs']">
#          <admst:variable name="d_f_d0" select="(((%($arg0)&gt;=0)?(+1.0):(-1.0)))"/>
#        </admst:when>
#        <admst:when test="[name='cos']">
#          <admst:variable name="d_f_d0" select="(-sin(%($arg0)))"/>
#        </admst:when>
#        <admst:when test="[name='sin']">
#          <admst:variable name="d_f_d0" select="(cos(%($arg0)))"/>
#        </admst:when>
#        <admst:when test="[name='tan']">
#          <admst:variable name="d_f_d0" select="(1.0/cos(%($arg0))/cos(%($arg0)))"/>
#        </admst:when>
#        <admst:when test="[name='acos']">
#          <admst:variable name="d_f_d0" select="(-1.0/sqrt(1.0-%($arg0)*%($arg0)))"/>
#        </admst:when>
#        <admst:when test="[name='asin']">
#          <admst:variable name="d_f_d0" select="(+1.0/sqrt(1.0-%($arg0)*%($arg0)))"/>
#        </admst:when>
#        <admst:when test="[name='atan']">
#          <admst:variable name="d_f_d0" select="(+1.0/sqrt(1.0+%($arg0)*%($arg0)))"/>
#        </admst:when>
#        <admst:when test="[name='cosh']">
#          <admst:variable name="d_f_d0" select="(sinh(%($arg0)))"/>
#        </admst:when>
#        <admst:when test="[name='sinh']">
#          <admst:variable name="d_f_d0" select="(cosh(%($arg0)))"/>
#        </admst:when>
#        <admst:when test="[name='tanh']">
#          <admst:variable name="d_f_d0" select="(1.0/cosh(%($arg0))/cosh(%($arg0)))"/>
#        </admst:when>
#        <admst:when test="[name='acosh']">
#          <admst:variable name="d_f_d0" select="(1.0/(sqrt(%($arg0)-1)*sqrt(%($arg0)+1)))"/>
#        </admst:when>
#        <admst:when test="[name='asinh']">
#          <admst:variable name="d_f_d0" select="(1.0/(sqrt(%($arg0)*%($arg0)+1.0)))"/>
#        </admst:when>
#        <admst:when test="[name='atanh']">
#          <admst:variable name="d_f_d0" select="(1.0/(1.0-%($arg0)*%($arg0)))"/>
#        </admst:when>
#        <admst:when test="[name='limexp']">
#          <admst:variable name="d_f_d0" select="(((%($arg0))&lt;80)?(limexp(%($arg0))):exp(80.0))"/>
#        </admst:when>
#        <admst:when  test="[name='ceil' or name='floor']">
#          <admst:variable name="d_f_d0" select="0.0"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:variable name="d_f_d0" select="0.0"/>
#          <admst:warning format="function derivative for %(name) not implemented yet!\n"/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:when test="[name='pow' or name='min' or name='max' or name='hypot' or name='atan2']">
#      <!-- two-argument functions -->
#      <admst:choose>
#        <admst:when test="[name='pow']">
#          <admst:variable name="d_f_d0" select="((%($arg0)==0.0)?0.0:(pow(%($arg0),%($arg1))*%($arg1)/%($arg0)))"/>
#          <admst:variable name="d_f_d1" select="((%($arg0)==0.0)?0.0:(log(%($arg0)*pow(%($arg0),%($arg1)))))"/>
#        </admst:when>
#        <admst:when test="[name='min']">
#          <admst:variable name="d_f_d0" select="((%($arg0)&lt;=%($arg1))?1.0:0.0)"/>
#          <admst:variable name="d_f_d1" select="((%($arg0)&lt;=%($arg1))?0.0:1.0)"/>
#        </admst:when>
#        <admst:when test="[name='max']">
#          <admst:variable name="d_f_d0" select="((%($arg0)&gt;=%($arg1))?1.0:0.0)"/>
#          <admst:variable name="d_f_d1" select="((%($arg0)&gt;=%($arg1))?0.0:1.0)"/>
#        </admst:when>
#        <admst:when test="[name='hypot']">
#          <admst:variable name="d_f_d0" select="(%($arg0)/sqrt(%($arg0)*%($arg0)+%($arg1)*%($arg1)))"/>
#          <admst:variable name="d_f_d1" select="(%($arg1)/sqrt(%($arg0)*%($arg0)+%($arg1)*%($arg1)))"/>
#        </admst:when>
#        <admst:when test="[name='atan2']">
#          <admst:variable name="d_f_d0" select="%($arg1)/(%($arg0)*%($arg0)+%($arg1)*%($arg1))"/>
#          <admst:variable name="d_f_d1" select="-%($arg0)/(%($arg0)*%($arg0)+%($arg1)*%($arg1))"/>
#        </admst:when>
#        <admst:otherwise>
#          <admst:variable name="d_f_d0" select="0.0"/>
#          <admst:variable name="d_f_d1" select="0.0"/>
#          <admst:warning format="function derivative for %(name) not implemented yet!\n"/>
#        </admst:otherwise>
#      </admst:choose>
#    </admst:when>
#    <admst:otherwise>
#      <admst:if test="[class!='analog']">
#        <admst:fatal format="Unable to handle function %(name) of class %(class) at this time.  Bye."/>
#      </admst:if>
#      <!-- we are an analog function, and this is very different than everything
#           else -->
#      <admst:variable name="doingAnalogFunctionCall" value="yes"/>
#      <admst:variable name="defaultdontbother" value="yes"/>
#      <admst:variable name="expression" value="%(name)(%($args))"/>
#      <admst:return name="returnedExpression" value="$expression"/>
#      <admst:if test="[definition/datatypename='analogfunction']">
#        <!-- <admst:message format="Processing analog function call within analog function definition\n"/> -->
#        <admst:if test="[exists(definition/variable[(output='yes') and (name!=$thisFunctionCall/name)])]">
#          <!-- <admst:message format="Called analog function has output variables other than return value.\n"/>-->
#          <admst:variable name="defaultdontbother" value="no"/>
#        </admst:if>
#      </admst:if>
#      <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#        <admst:variable name="dontbother" value="$(defaultdontbother)"/>
#        <admst:variable name="dargs" value=""/>
#        <admst:variable name="wrt" value="%(name)"/>
#        <admst:for-each select="$thisFunctionCall/arguments">
#          <admst:value-of select="index($thisFunctionCall/arguments,.)"/>
#          <admst:variable name="index" select="%s"/>
#          <admst:if test="[($(d_arg$(index)_d_$(wrt)) != '0.0')]">
#            <admst:variable name="dontbother" value="no"/>
#          </admst:if>
#          <admst:if test="[not($dargs='')]">
#            <admst:variable name="dargs" select="$dargs,"/>
#          </admst:if>
#          <admst:variable name="dargs" select="$(dargs)$(d_arg$(index)_d_$(wrt))"/>
#        </admst:for-each>
#        <admst:choose>
#          <admst:when test="[$dontbother='yes']">
#            <admst:variable name="expressionDeriv" value="0.0"/>
#          </admst:when>
#          <admst:otherwise>
#            <admst:variable name="expressionDeriv" value="d_%($thisFunctionCall/name)($args,$dargs)"/>
#          </admst:otherwise>
#        </admst:choose>
#        <admst:return name="d_exp_d_$(wrt)" value="$expressionDeriv"/>
#      </admst:for-each>
#    </admst:otherwise>
#  </admst:choose>
#
#  <admst:if test="[$doingAnalogFunctionCall = 'no']">
#    <!-- we now have the function value and its derivatives with respect to
#         its arguments, and the derivatives of the arguments with respect to
#         all analog function dummy arguments.  Emit the total derivatives. -->
#
#    <admst:return name="returnedExpression" value="$expression"/>
#
#    <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#      <admst:variable name="expressionDeriv" select=""/>
#      <admst:variable name="wrt" value="%(name)"/>
#      <admst:for-each select="$thisFunctionCall/arguments">
#        <admst:value-of select="index($thisFunctionCall/arguments,.)"/>
#        <admst:variable name="index" select="%s"/>
#        <admst:if test="[($(d_arg$(index)_d_$(wrt)) != '0.0') and ($(d_f_d$(index)) != '0.0')]">
#          <admst:if test="[not($expressionDeriv='')]">
#            <admst:variable name="expressionDeriv" select="$(expressionDeriv)+"/>
#          </admst:if>
#          <admst:choose>
#            <admst:when test="[$(d_arg$(index)_d_$(wrt)) = '1.0']">
#              <admst:variable name="expressionDeriv" select="$(expressionDeriv)$(d_f_d$(index))"/>
#            </admst:when>
#            <admst:otherwise>
#              <admst:variable name="expressionDeriv" select="$(expressionDeriv)$(d_f_d$(index))*$(d_arg$(index)_d_$(wrt))"/>
#            </admst:otherwise>
#          </admst:choose>
#        </admst:if>
#      </admst:for-each>
#      <!-- handle the case where it turned out that all the derivs were zero -->
#      <admst:if test="[$expressionDeriv='']">
#        <admst:variable name="expressionDeriv" value="0.0"/>
#      </admst:if>
#      <admst:value-of select="name"/>
#      <admst:return name="d_exp_d_%s" value="$expressionDeriv"/>
#    </admst:for-each>
#  </admst:if>
#</admst:template>
#
#
#<!-- template to force an argument into a real (used only for min and max) -->
#<admst:template match="xyceAnalogFunctions:realArgument">
#  <admst:choose>
#    <admst:when test="[datatypename='number' or (datatypename='variable' and type='integer')]">
#        <admst:variable name="localArg" select="static_cast&lt;double&gt;(%(xyceAnalogFunctions:processTerm(.)/[name='returnedExpression']/value))" />
#      </admst:when>
#      <admst:otherwise>
#        <admst:variable name="localArg" select="%(xyceAnalogFunctions:processTerm(.)/[name='returnedExpression']/value)" />
#      </admst:otherwise>
#    </admst:choose>
#    <admst:return name="argval" value="$localArg"/>
#</admst:template>
#
#<!-- template to return the C++ name of a function given the Verilog name -->
#<!-- Very much like the one in xyceBasicTemplates, but stripped of all
#     context-dependent conditionals -->
#
#<admst:template match="xyceAnalogFunctions:funcname">
#  <admst:choose>
#    <admst:when test="[name='min']">
#      <admst:variable name="expression" select="std::min"/>
#    </admst:when>
#    <admst:when test="[name='max']">
#      <admst:variable name="expression" select="std::max"/>
#    </admst:when>
#    <admst:when test="[name='abs']">
#      <admst:variable name="expression" select="fabs"/>
#    </admst:when>
#    <admst:when test="[name='\$shrinkl']">
#      <admst:fatal format="\$shrinkl not supported in Xyce"/>
#    </admst:when>
#    <admst:when test="[name='\$shrinka']">
#      <admst:fatal format="\$shrinka not supported in Xyce"/>
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
#      <admst:variable name="expression" select="%(name)"/>
#    </admst:otherwise>
#  </admst:choose>
#  <admst:return name="fname" value="$expression"/>
#</admst:template>
#
#<!-- These templates are used in actual code generation -->
#<!-- each one returns a string that should simply be emitted in the
#     "returnedString" return slot. -->
#<!-- At the moment, we're ONLY emitting derivative functions, so we are
#     only providing templates that do differentiation.  That's because
#     we're already emitting a templated analog function, and it works just
#     fine when everything's "double", and does Sacado differentiation when
#     everything's a Sacado type.  Therefore we are not bothering to produce
#     a second set of templates that do no differentiation for analog functions,
#     as some other ADMS back-ends do.
#     If at some point in the future we need to do that, we can create a
#     second set of templates with a suffix in their names and use those
#     for that purpose. -->
#
#<!-- assignment -->
#<admst:template match="xyceAnalogFunctions:assignment">
#  <admst:variable name="lhsname" value="%(lhs/name)"/>
#  <admst:variable name="lhstype" value="%(lhs/type)"/>
#  <admst:apply-templates select="rhs" match="xyceAnalogFunctions:processTerm">
#    <admst:variable name="returnedString" select="" />
#
#    <admst:if test="[$lhstype = 'real']">
#      <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#        <admst:value-of select="name"/>
#        <admst:value-of select="returned('d_exp_d_%s')/value"/>
#        <admst:value-of select="name"/>
#        <admst:variable name="returnedString" select="$(returnedString)d_$(lhsname)_d_%s=%s;\n"/>
#      </admst:for-each>
#    </admst:if>
#    <admst:value-of select="returned('returnedExpression')/value"/>
#    <admst:variable name="returnedString" select="$(returnedString)$(lhsname)=%s;\n"/>
#  </admst:apply-templates>
#  <admst:return name="returnedString" value="$returnedString"/>
#</admst:template>
#
#<!-- if/then/else -->
#<admst:template match="xyceAnalogFunctions:conditional">
#  <admst:variable name="condition"/>
#  <admst:variable name="thenblock"/>
#  <admst:variable name="elseblock"/>
#  <admst:variable name="condition" select="%(xyceAnalogFunctions:processTerm(if)/[name='returnedExpression']/value)"/>
#  <admst:variable name="thenblock" value=""/>
#  <admst:apply-templates select="then" match="xyceAnalogFunctions:%(adms/datatypename)">
#    <admst:if test="[adms/datatypename != 'block']">
#      <admst:variable name="thenblock" value="{\n"/>
#    </admst:if>
#    <admst:value-of select="returned('returnedString')/value"/>
#    <admst:variable name="thenblock" select="$(thenblock)%s"/>
#    <admst:if test="[adms/datatypename != 'block']">
#      <admst:variable name="thenblock" value="$(thenblock)}\n"/>
#    </admst:if>
#  </admst:apply-templates>
#  <admst:variable name="returnedString" value="if($condition)\n$thenblock"/>
#  <admst:if test="else">
#    <admst:variable name="elseblock" value=""/>
#    <admst:apply-templates select="else" match="xyceAnalogFunctions:%(adms/datatypename)">
#      <admst:if test="[adms/datatypename != 'block']">
#        <admst:variable name="elseblock" value="{\n"/>
#      </admst:if>
#      <admst:value-of select="returned('returnedString')/value"/>
#      <admst:variable name="elseblock" select="$(elseblock)%s"/>
#      <admst:if test="[adms/datatypename != 'block']">
#        <admst:variable name="elseblock" value="$(elseblock)}\n"/>
#      </admst:if>
#    </admst:apply-templates>
#    <admst:variable name="returnedString" value="$(returnedString)else\n$elseblock"/>
#  </admst:if>
#  <admst:return name="returnedString" value="$returnedString"/>
#</admst:template>
#
#<!-- for loop -->
#<admst:template match="xyceAnalogFunctions:forloop">
#  <admst:variable name="returnedString" value="for ("/>
#  <admst:variable name="returnedString" select="$(returnedString)%(xyceAnalogFunctions:processTerm(initial/lhs)/[name='returnedExpression']/value)=%(xyceAnalogFunctions:processTerm(initial/rhs)/[name='returnedExpression']/value);"/>
#  <admst:variable name="returnedString" select="$(returnedString)%(xyceAnalogFunctions:processTerm(condition)/[name='returnedExpression']/value);"/>
#  <admst:variable name="returnedString" select="$(returnedString)%(xyceAnalogFunctions:processTerm(update/lhs)/[name='returnedExpression']/value)=%(xyceAnalogFunctions:processTerm(update/rhs)/[name='returnedExpression']/value) )\n"/>
#
#  <admst:if test="[forblock/adms[datatypename!='block']]">
#    <admst:variable name="returnedString" select="$(returnedString){\n"/>
#  </admst:if>
#  <admst:apply-templates select="forblock" match="xyceAnalogFunctions:%(adms/datatypename)">
#    <admst:value-of select="returned('returnedString')/value"/>
#    <admst:variable name="returnedString" select="$(returnedString)%s"/>
#  </admst:apply-templates>
#  <admst:if test="[forblock/adms[datatypename!='block']]">
#    <admst:variable name="returnedString" select="$(returnedString)}\n"/>
#  </admst:if>
#
#  <admst:return name="returnedString" value="$returnedString"/>
#</admst:template>
#
#<!-- while loop -->
#<admst:template match="xyceAnalogFunctions:whileloop">
#  <admst:variable name="returnedString" value="while (%(processTerm(while)[name='returnedExpression']/value))\n"/>
#  <admst:if test="[whileblock/adms[datatypename!='block']]">
#    <admst:variable name="returnedString" select="$(returnedString){\n"/>
#  </admst:if>
#  <admst:apply-templates select="whileblock" match="xyceAnalogFunctions:%(adms/datatypename)">
#    <admst:value-of select="returned('returnedString')/value"/>
#    <admst:variable name="returnedString" select="$(returnedString)%s"/>
#  </admst:apply-templates>
#  <admst:if test="[whileblock/adms[datatypename!='block']]">
#    <admst:variable name="returnedString" select="$(returnedString)}\n"/>
#  </admst:if>
#
#  <admst:return name="returnedString" value="$returnedString"/>
#</admst:template>
#
#<!-- case statement -->
#<admst:template match="xyceAnalogFunctions:case">
#  <admst:variable name="casecondition" path="case/tree"/>
#  <admst:variable name="havedefault" select="no"/>
#  <admst:if test="[count(caseitem[defaultcase='yes']) > 0]">
#    <admst:variable name="havedefault" select="yes"/>
#  </admst:if>
#  <admst:variable name="returnedString" value=""/>
#  <admst:variable name="conditionString" value=""/>
#  <admst:for-each select="caseitem[defaultcase='no']">
#    <admst:variable name="returnedString" select="$(returnedString)if( "/>
#    <admst:for-each select="condition">
#      <admst:if test="[$conditionString!='']">
#        <admst:variable name="conditionString" value="$(conditionString) || "/>
#      </admst:if>
#      <admst:apply-templates select="." match="xyceAnalogFunctions:%(datatypename)">
#        <admst:variable name="conditionString" select="%(xyceAnalogFunctions:processTerm($casecondition)[name='returnedExpression']/value) == %(returned('returnedExpression')/value)"/>
#      </admst:apply-templates>
#    </admst:for-each>
#
#    <admst:variable name="returnedString" select="$(returnedString)$(conditionString))\n"/>
#    <admst:apply-templates select="code" match="xyceAnalogFunctions:%(datatypename)" required="yes">
#      <admst:if test="[datatypename!='block']">
#        <admst:variable name="returnedString" select="$(returnedString){\n"/>
#      </admst:if>
#      <admst:variable name="returnedString" select="$(returnedString)%(returned('returnedString')/value)"/>
#      <admst:if test="[datatypename!='block']">
#        <admst:variable name="returnedString" select="$(returnedString)}\n"/>
#      </admst:if>
#      <admst:variable name="returnedString" select="$(returnedString)else\n"/>
#    </admst:apply-templates>
#    <admst:if test="[$havedefault='no']">
#      <admst:variable name="returnedString" select="$(returnedString){\n // no default\n}\n"/>
#    </admst:if>
#  </admst:for-each>
#  <admst:for-each select="caseitem[defaultcase='yes']">
#    <admst:apply-templates select="code" match="xyceAnalogFunctions:%(datatypename)" required="yes">
#      <admst:variable name="returnedString" select="$(returnedString)%(returned('returnedString')/value)"/>
#    </admst:apply-templates>
#  </admst:for-each>
#  <admst:return name="returnedString" value="$returnedString"/>
#</admst:template>
#
#<!-- block -->
#<admst:template match="xyceAnalogFunctions:block">
#  <admst:variable name="returnedString" value=""/>
#  <admst:if test="[name!='']">
#    <admst:variable name="returnedString" value="//Begin block %(name)\n"/>
#  </admst:if>
#  <admst:variable name="returnedString" value="$(returnedString){\n"/>
#  <admst:apply-templates select="item" match="xyceAnalogFunctions:%(adms/datatypename)">
#    <admst:value-of select="returned('returnedString')/value"/>
#    <admst:variable name="returnedString" select="$(returnedString)%s"/>
#  </admst:apply-templates>
#  <admst:variable name="returnedString" value="$(returnedString)}\n"/>
#  <admst:if test="[name!='']">
#    <admst:variable name="returnedString" value="//End block %(name)\n"/>
#  </admst:if>
#  <admst:return name="returnedString" value="$returnedString"/>
#</admst:template>
#
#<!-- Declare block-local variables -->
#<admst:template match="xyceAnalogFunctions:blockvariable">
#  <admst:variable name="returnedString" value="//block-local variables for block %(block/name)\n"/>
#  <admst:for-each select="variable">
#    <admst:choose>
#      <admst:when test="[type='real']">
#        <admst:variable name="returnedString" select="$(returnedString) double %(name);\n"/>
#        <admst:variable name="theName" select="%(name)"/>
#        <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#          <admst:variable name="wrt" select="%(name)"/>
#          <admst:variable name="returnedString" select="$(returnedString) double d_$(theName)_d_$(wrt);\n"/>
#        </admst:for-each>
#      </admst:when>
#      <admst:when test="[type='integer']">
#        <admst:variable name="returnedString" select="$(returnedString) int %(name);\n"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:fatal format="At the moment, Xyce/ADMS only supports real and integer block-local variables in analog functions\n"/>
#      </admst:otherwise>
#    </admst:choose>
#  </admst:for-each>
#  <admst:return name="returnedString" value="$returnedString"/>
#</admst:template>
#<!-- these should never get called, and if they do, it's a warning -->
#<admst:template match="xyceAnalogFunctions:callfunction">
#  <admst:warning format="callfunctions cannot be accessed inside analog functions, ignoring %(function/name)\n"/>
#  <admst:return name="returnedString" value=""/>
#</admst:template>
#
#<!-- these should never get called, and if they do, it's an error -->
#<admst:template match="xyceAnalogFunctions:probe">
#  <admst:fatal format="Probes cannot be accessed inside analog functions\n"/>
#</admst:template>
#<admst:template match="xyceAnalogFunctions:contribution">
#  <admst:fatal format="contributions cannot be used inside analog functions\n"/>
#</admst:template>
#<!-- end error types -->
#
#<!-- template to dump out the declaration/prototype of analog function
#     derivative function -->
#
#<admst:template match="xyceAnalogFunctions:Declaration">
#
#    <admst:variable name="function" select="%(name)"/>
#    <admst:variable name="globalAnalogFunction" path="."/>
#    <admst:text format="// Derivative of Analog Function %(name)\n"/>
#    <admst:text format="%(verilog2CXXtype(.)) d_%(name)("/>
#    <admst:join select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]" separator=", ">
#      <admst:text format="%(verilog2CXXtype(.)) "/>
#      <!-- irrespective of whether the argument is an output variable,
#           we always pass by value.  We are NOT returning the function
#           value and its output variable values, only the derivatives! -->
#      <admst:text format="%(name) "/>
#    </admst:join>
#    <admst:text format=" , "/>
#    <!-- now the derivatives of the args w.r.t. the desired variable -->
#    <admst:join select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]" separator=", ">
#      <admst:text format="%(verilog2CXXtype(.)) "/>
#      <admst:if test="[output='yes']">
#        <admst:text format="&amp; "/>
#      </admst:if>
#      <admst:text format="d_%(name)  "/>
#    </admst:join>
#    <admst:text format=");\n"/>
#</admst:template>
#
#<!-- template to dump out the declaration of the class needed to handle
#    analog functions in precomputation usage, i.e. outside of sensitivity
#    context.  This will ultimately completely replace the simple "d_"
#    derivative-calculating technique.
#    -->
#<admst:template match="xyceAnalogFunctions:ClassDeclaration">
#  <admst:variable name="function" select="%(name)"/>
#  <admst:variable name="globalAnalogFunction" path="."/>
#  <admst:text format="// Evaluator class for Analog Function %(name)\n"/>
#  <admst:text format="class $(function)Evaluator\n"/>
#  <admst:text format="{\n"/>
#  <admst:text format="  struct returnType\n"/>
#  <admst:text format="  {\n"/>
#  <admst:text format="     double value;\n"/>
#  <admst:for-each select="variable[input='yes']">
#    <admst:text format="     double deriv_WRT_%(name);\n"/>
#  </admst:for-each>
#  <admst:text format="  };\n"/>
#  <admst:text format="public:\n"/>
#  <admst:text format="  // constructor takes all same arguments as regular templated function,\n"/>
#  <admst:text format="  // even though it doesn't USE the output args\n"/>
#  <admst:text format="  $(function)Evaluator("/>
#  <admst:join select="variable[input='yes' or (input='no' and output='yes' and name!=$(function))]" separator=", ">
#    <admst:text format="%(verilog2CXXtype(.)) %(name)"/>
#  </admst:join>
#  <admst:text format=");\n"/>
#  <admst:text format="  // function that returns the precomputed values.  This, too, takes\n"/>
#  <admst:text format="  // all the same arguments as the regular function, though it ONLY\n"/>
#  <admst:text format="  // uses the output arguments\n"/>
#  <admst:text format="  %(verilog2CXXtype(.)) getValues("/>
#  <admst:join select="variable[input='yes' or (input='no' and output='yes' and name!=$(function))]" separator=", ">
#    <admst:text format="%(verilog2CXXtype(.)) "/>
#    <admst:if test="[output='yes']">
#      <admst:text format="&amp; "/>
#    </admst:if>
#    <admst:text format=" %(name)"/>
#  </admst:join>
#  <admst:text format=");\n"/>
#  <admst:text format="  // function that returns the total derivative of the function and its\n"/>
#  <admst:text format="  // output arguments with respect to some variable.  We pass in the\n"/>
#  <admst:text format="  // normal arguments(none of which are used) and the derivatives of those\n"/>
#  <admst:text format="  // arguments with respect to the desired variable.  We compute the\n"/>
#  <admst:text format="  // derivatives using the chain rule and our precomputed derivatives\n"/>
#  <admst:text format="  // with respect to input variables\n"/>
#  <admst:text format="%(verilog2CXXtype(.)) getDerivs("/>
#  <admst:join select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]" separator=", ">
#    <admst:text format="%(verilog2CXXtype(.)) "/>
#    <!-- irrespective of whether the argument is an output variable,
#         we always pass by value.  We are NOT returning the function
#         value and its output variable values, only the derivatives! -->
#    <admst:text format="%(name) "/>
#  </admst:join>
#  <admst:text format=" , "/>
#  <!-- now the derivatives of the args w.r.t. the desired variable -->
#  <admst:join select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]" separator=", ">
#    <admst:text format="%(verilog2CXXtype(.)) "/>
#    <admst:if test="[output='yes']">
#      <admst:text format="&amp; "/>
#    </admst:if>
#    <admst:text format="d_%(name)"/>
#  </admst:join>
#  <admst:text format=");\n"/>
#
#  <admst:text format="private:\n"/>
#  <admst:text format="  returnType $(function)Return_;\n"/>
#  <admst:for-each select="variable[output='yes' and name != $(function)]">
#    <admst:text format="  returnType %(name)Return_;\n"/>
#  </admst:for-each>
#  <!-- "evaluator_" is the actual function that evaluates the function,
#       but all outputs are actually of returnType -->
#  <admst:text format="  returnType evaluator_("/>
#  <admst:join
#      select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]"
#      separator=", ">
#    <admst:choose>
#      <admst:when test="[output='yes']">
#        <admst:text format="returnType &amp;"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:text format="%(verilog2CXXtype(.))"/>
#      </admst:otherwise>
#    </admst:choose>
#    <admst:text format=" %(name)"/>
#  </admst:join>
#  <admst:text format=");\n"/>
#  <admst:text format="};\n"/>
#</admst:template>
#
#<!-- Top level template to dump out an analog function implementation
#     These functions only return the TOTAL DERIVATIVE of the function
#     with respect to some (general) variable,
#     computed via the chain rule given the partial derivatives of its
#     arguments with respect to that variable (passed in to it) -->
#<admst:template match="xyceAnalogFunctions:Implementation">
#
#  <admst:variable name="function" select="%(name)"/>
#  <admst:variable name="globalAnalogFunction" path="."/>
#  <admst:text format="// Derivative of Analog Function %(name)\n"/>
#  <admst:text format="%(verilog2CXXtype(.)) d_%(name)("/>
#  <admst:join select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]" separator=", ">
#    <admst:text format="%(verilog2CXXtype(.)) "/>
#    <!-- irrespective of whether the argument is an output variable,
#         we always pass by value.  We are NOT returning the function
#         value and its output variable values, only the derivatives! -->
#    <admst:text format="%(name) "/>
#  </admst:join>
#  <admst:text format=" , "/>
#  <!-- now the derivatives of the args w.r.t. the desired variable -->
#  <admst:join select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]" separator=", ">
#    <admst:text format="%(verilog2CXXtype(.)) "/>
#    <admst:if test="[output='yes']">
#      <admst:text format="&amp; "/>
#    </admst:if>
#    <admst:text format="d_%(name) "/>
#  </admst:join>
#  <admst:text format=")\n"/>
#  <admst:text format="{\n"/>
#  <admst:text format="// Function return variable and total deriv\n"/>
#  <admst:text format="%(verilog2CXXtype(.)) %(name);\n"/>
#  <admst:text format="%(verilog2CXXtype(.)) d_%(name);\n"/>
#  <admst:text format="// Derivatives of return value w.r.t input vars\n"/>
#  <!-- derivatives of the return value w.r.t. all input vars -->
#  <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#    <admst:text format="%(verilog2CXXtype($globalAnalogFunction)) d_%($function)_d_%(name)=0;\n"/>
#  </admst:for-each>
#  <admst:if test="[exists($globalAnalogFunction/variable[output='yes' and name!='$function'])]">
#    <admst:text format="// Derivatives of additional output vars w.r.t input vars\n"/>
#  </admst:if>
#  <!-- derivatives of all output variables w.r.t. all input vars -->
#  <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#    <admst:variable name="wrt" select="%(name)"/>
#    <admst:for-each select="$globalAnalogFunction/variable[output='yes' and name!='$function']">
#      <admst:text format="%(verilog2CXXtype(.)) d_%(name)_d_$(wrt)=0;\n"/>
#    </admst:for-each>
#  </admst:for-each>
#  <admst:for-each select="variable[input='no' and output='no']">
#    <admst:variable name="theVar" path="."/>
#    <admst:variable name="varname" select="%(name)"/>
#    <admst:text format="%(verilog2CXXtype($theVar)) $varname;\n"/>
#    <admst:if test="[$theVar/type='real']">
#      <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#        <admst:text format="%(verilog2CXXtype($theVar)) d_$(varname)_d_%(name);\n"/>
#      </admst:for-each>
#    </admst:if>
#  </admst:for-each>
#
#  <admst:apply-templates select="tree" match="xyceAnalogFunctions:%(adms/datatypename)">
#    <admst:value-of select="returned('returnedString')/value"/>
#    <admst:variable name="returnedString" select="%s"/>
#    <admst:text format="$returnedString"/>
#  </admst:apply-templates>
#
#  <admst:for-each select="$globalAnalogFunction/variable[output='yes']">
#    <admst:variable name="outvar" value="%(name)"/>
#    <admst:variable name="expression" value=""/>
#    <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#      <admst:variable name="wrt" value="%(name)"/>
#      <admst:if test="[$expression != '']">
#        <admst:variable name="expression" value="$expression+"/>
#      </admst:if>
#      <admst:variable name="expression" value="$(expression)d_$(outvar)_d_$(wrt)*d_$(wrt)"/>
#    </admst:for-each>
#    <admst:text format="d_$(outvar) = $expression;\n"/>
#  </admst:for-each>
#  <admst:text format="return(d_%(name));\n"/>
#  <admst:text format="}\n\n"/>
#  <admst:variable name="globalAnalogFunction"/>
#</admst:template>
#
#<!-- Generate implementations of functions declared in the function evaluator
#     classes above
#     TODO:  eliminate unnecessary arguments.  Didn't do that at first
#     because it will simplify the problem of swapping these things into
#     where the functions are used (they all take the same arguments that
#     the old technique required).
#     -->
#<admst:template match="xyceAnalogFunctions:ClassImplementations">
#  <admst:variable name="function" select="%(name)"/>
#  <admst:variable name="globalAnalogFunction" path="."/>
#  <admst:text format="// Evaluator class implementations for Analog Function %(name)\n"/>
#  <admst:text format="  // Constructor\n"/>
#  <admst:text format="  $(function)Evaluator::$(function)Evaluator("/>
#  <admst:join select="variable[input='yes' or (input='no' and output='yes' and name!=$(function))]" separator=", ">
#    <admst:text format="%(verilog2CXXtype(.)) %(name)"/>
#  </admst:join>
#  <admst:text format=")\n"/>
#  <admst:text format="  {\n"/>
#
#  <admst:text format="    %(name)Return_ = evaluator_("/>
#  <admst:join
#      select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]"
#      separator=", ">
#    <admst:choose>
#      <admst:when test="[output='yes']">
#        <admst:text format="%(name)Return_"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:text format="%(name)"/>
#      </admst:otherwise>
#    </admst:choose>
#
#  </admst:join>
#  <admst:text format=");\n"/>
#  <admst:text format="  }\n"/>
#
#  <admst:text format="  // method to get precomputed values into double vars \n"/>
#  <admst:text format="  %(verilog2CXXtype(.)) %(name)Evaluator::getValues("/>
#  <admst:join select="variable[input='yes' or (input='no' and output='yes' and name!=$(function))]" separator=", ">
#    <admst:text format="%(verilog2CXXtype(.)) "/>
#    <admst:if test="[output='yes']">
#      <admst:text format="&amp; "/>
#    </admst:if>
#    <admst:text format=" %(name)"/>
#  </admst:join>
#  <admst:text format=")\n"/>
#  <admst:text format="  {\n"/>
#  <admst:text format="    // Silence unused argument warnings\n"/>
#  <admst:for-each select="variable[input='yes' and output='no']">
#    <admst:text format="    (void) %(name);\n"/>
#  </admst:for-each>
#  <admst:text format="    // Copy all precomputed values into corresponding output\n"/>
#  <admst:for-each select="variable[output='yes' and name!=$function]">
#    <admst:text format="    %(name) = %(name)Return_.value;\n"/>
#  </admst:for-each>
#  <admst:text format="    return(%(name)Return_.value);\n"/>
#  <admst:text format="  }\n"/>
#
#  <admst:text format="  // method to get total deriv w.r.t some variable via chain rule \n"/>
#  <admst:text format="  // given precomputed derivs of function w.r.t. args and derivs of args\n"/>
#  <admst:text format="  // w.r.t desired vars\n"/>
#  <admst:text format="  %(verilog2CXXtype(.)) %(name)Evaluator::getDerivs("/>
#  <admst:join select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]" separator=", ">
#    <admst:text format="%(verilog2CXXtype(.)) "/>
#    <!-- irrespective of whether the argument is an output variable,
#         we always pass by value.  We are NOT returning the function
#         value and its output variable values, only the derivatives! -->
#    <admst:text format="%(name) "/>
#  </admst:join>
#  <admst:text format=" , "/>
#  <!-- now the derivatives of the args w.r.t. the desired variable -->
#  <admst:join select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]" separator=", ">
#    <admst:text format="%(verilog2CXXtype(.)) "/>
#    <admst:if test="[output='yes']">
#      <admst:text format="&amp; "/>
#    </admst:if>
#    <admst:text format="d_%(name)"/>
#  </admst:join>
#  <admst:text format=")\n"/>
#  <admst:text format="  {\n"/>
#  <admst:text format="    // Function total deriv\n"/>
#  <admst:text format="    %(verilog2CXXtype(.)) d_%(name);\n"/>
#  <admst:text format="    // Silence unused argument warnings\n"/>
#  <admst:for-each select="variable[input='yes']">
#    <admst:text format="    (void) %(name);\n"/>
#  </admst:for-each>
#
#  <admst:for-each select="$globalAnalogFunction/variable[output='yes']">
#    <admst:variable name="outvar" value="%(name)"/>
#    <admst:variable name="expression" value=""/>
#    <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#      <admst:variable name="wrt" value="%(name)"/>
#      <admst:if test="[$expression != '']">
#        <admst:variable name="expression" value="$expression+"/>
#      </admst:if>
#      <admst:variable name="expression" value="$(expression)$(outvar)Return_.deriv_WRT_$(wrt)*d_$(wrt)"/>
#    </admst:for-each>
#    <admst:text format="    d_$(outvar) = $expression;\n"/>
#  </admst:for-each>
#  <admst:text format="    return(d_%(name));\n"/>
#  <admst:text format="  }\n"/>
#
#  <admst:text format="  // method that actually performs our computations.\n"/>
#  <admst:text format="  %(name)Evaluator::returnType %(name)Evaluator::evaluator_("/>
#  <admst:join
#      select="variable[input='yes' or (input='no' and output='yes' and name!=$function)]"
#      separator=", ">
#    <admst:choose>
#      <admst:when test="[output='yes']">
#        <admst:text format="$(function)Evaluator::returnType &amp; %(name)Return"/>
#      </admst:when>
#      <admst:otherwise>
#        <admst:text format="%(verilog2CXXtype(.)) %(name)"/>
#      </admst:otherwise>
#    </admst:choose>
#  </admst:join>
#  <admst:text format=")\n"/>
#  <admst:text format="  {\n"/>
#  <!-- This is almost the same as the contents of the d_(function) function,
#       modulo the chain rule thing at the end, and the storage of derivatives
#       in a returnType variable -->
#  <admst:text format="  // Function value and derivs variables, and a returnType to store everything\n"/>
#  <admst:text format="  %(verilog2CXXtype(.)) %(name);\n"/>
#  <admst:text format="  %(name)Evaluator::returnType %(name)Return;\n"/>
#  <admst:text format="  // Derivatives of return value w.r.t input vars\n"/>
#  <!-- derivatives of the return value w.r.t. all input vars -->
#  <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#    <admst:text format="  %(verilog2CXXtype($globalAnalogFunction)) d_%($function)_d_%(name)=0;\n"/>
#  </admst:for-each>
#  <admst:if test="[exists($globalAnalogFunction/variable[output='yes' and name!='$function'])]">
#    <admst:text format="  // additional output vars  and derivs w.r.t input vars\n"/>
#  </admst:if>
#  <!-- derivatives of all output variables w.r.t. all input vars -->
#  <admst:for-each select="$globalAnalogFunction/variable[output='yes' and name!='$function']">
#    <admst:variable name="ovar" select="%(name)"/>
#    <admst:text format="  %(verilog2CXXtype(.)) $(ovar);\n"/>
#    <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#      <admst:text format="  %(verilog2CXXtype(.)) d_$(ovar)_d_%(name)=0;\n"/>
#    </admst:for-each>
#  </admst:for-each>
#  <!-- and now the remaining local variables -->
#  <admst:text format="  // declared local variables\n"/>
#  <admst:for-each select="variable[input='no' and output='no']">
#    <admst:variable name="theVar" path="."/>
#    <admst:variable name="varname" select="%(name)"/>
#    <admst:text format="  %(verilog2CXXtype($theVar)) $varname;\n"/>
#    <admst:if test="[$theVar/type='real']">
#      <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#        <admst:text format="  %(verilog2CXXtype($theVar)) d_$(varname)_d_%(name)=0;\n"/>
#      </admst:for-each>
#    </admst:if>
#  </admst:for-each>
#
#  <!-- Generate the actual code -->
#  <admst:apply-templates select="tree" match="xyceAnalogFunctions:%(adms/datatypename)">
#    <admst:value-of select="returned('returnedString')/value"/>
#    <admst:variable name="returnedString" select="%s"/>
#    <admst:text format="$returnedString"/>
#  </admst:apply-templates>
#
#  <admst:text format="  // now save outputs and derivs into appropriate return vars\n"/>
#  <admst:text format="  %(name)Return.value=%(name);\n"/>
#  <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#    <admst:text format="  $(function)Return.deriv_WRT_%(name) = d_%($function)_d_%(name);\n"/>
#  </admst:for-each>
#
#  <admst:for-each select="$globalAnalogFunction/variable[output='yes' and name!='$function']">
#    <admst:variable name="ovar" select="%(name)"/>
#    <admst:text format="  $(ovar)Return.value = $(ovar);\n"/>
#    <admst:for-each select="$globalAnalogFunction/variable[input='yes']">
#      <admst:text format="  $(ovar)Return.deriv_WRT_%(name) = d_$(ovar)_d_%(name);\n"/>
#    </admst:for-each>
#  </admst:for-each>
#
#  <admst:text format="  return(%(name)Return);\n"/>
#  <admst:text format="  }\n\n"/>
#
#
#</admst:template>
#</admst>

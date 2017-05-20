import sympy
import antlr4
import io
from antlr4.error.ErrorListener import ErrorListener
from antlr4 import InputStream, CommonTokenStream

from parser.DOC import DOC as DOCParser
from parser.LEX import LEX as DOCLexer
from parser.DOCListener import DOCListener

from sympy.printing.str import StrPrinter

from latex2sympy import process_latex

def invert_dict(d):
    '''Inverts a dictionary that potentially contains duplicate values.'''

    inv_map = {}
    for k, v in d.iteritems():
        inv_map.setdefault(v, []).append(k)

    return inv_map

def pretty_print(result):
    print("Document class: {}".format(result.document_class))
    if len(result.packages) > 0: 
        for p in result.packages:
            print("\t{}".format(p))
    labels=invert_dict(result.equation_labels)
    for (i, e) in enumerate(result.equations):
        if i in labels:
            s="\t\t[{}]".format(', '.join(labels[i]))
        else:
            s=''
        print("[{}]:\t{}{}".format(i, e, s))
    print(result.equation_labels)

mathematical_environments=[u'align', u'equation', u'gather', u'align*', u'equation*', u'gather*']

class Parser(DOCParser):
    
    

    def math_test(self):
        print("math test.")
 
    def tagsMatch(self, x, y):
        x=x.text.strip()
        y=y.text.strip()
        #print("Checking to see if tag {} matches tag {}".format(x, y))
        predicate = (x == y)
        #print("Answer: {}".format(predicate))
  #      print("In addition:", self._input.LT(1).text)
        return predicate

    def isMathEnvironment(self):
        name=self._input.LT(3).text.strip()
        #print("Checking if {} is a math environment.".format(name))
        if name in mathematical_environments:
            predicate=True
        else:
            predicate=False
        #print("Answer: {}".format(predicate))
        return predicate

def process_doc(sympy):

    stream=antlr4.InputStream(sympy)
    lex = DOCLexer(stream)
    
    tokens=antlr4.CommonTokenStream(lex)
    parser=Parser(tokens)
 
    document = parser.document()

    return document

#def parse(s):
#    stream=antlr4.InputStream(s)
#    lex = DOCLexer(stream)
#    
#    tokens=antlr4.CommonTokenStream(lex)
#    parser=DOCParser(tokens)
#
#    return parser

def debug(s):
    print(s)

def parse(s, node):
    lexer = DOCLexer(InputStream(s))
    stream = CommonTokenStream(lexer)
    parser = Parser(stream)

#    print("extracted version {}". format(parser.extractVersion("4.7")))
#    print("checking version")
#    parser.checkVersion("4.7")
#    print("succeeded")

    tree = getattr(parser, node)()
    #print(type(tree), tree.__dict__)
    listener = documentListener()
    walker = antlr4.ParseTreeWalker()
    walker.walk(listener, tree)

    return listener

class MathListener(DOCListener):
    def __init__(self):
        self.equation_labels={}
        self.equations=[]
        self.math_fragment_stack=[]
        self.convert=True
        self.labels=[]
        self.fragment_stack=[]
        self.trace=False

    def ship_math(self):
        if len(self.math_fragment_stack) > 0:
            s=' '.join(self.math_fragment_stack)
            if self.convert:
                try:
                    m=process_latex.process_sympy(s)
                except:
                    print("**** sympy conversion failed on {}".format(s))
                    m=s.strip()
                separator=" === "
            else:
                m=s.strip()
                separator=":"
            if self.trace:
                print("Math{} {}".format(separator, m))
            pos=len(self.equations)
            self.equations.append(m)
            for l in self.labels:
                if l in self.equation_labels:
                    print("Warning: attempt to re-use label {}".format(l))
                else:
                    self.equation_labels[l]=pos
            self.labels=[]
            self.math_fragment_stack=[]

    def push_math_fragment(self, s):
        #print("Pushing math fragment {} on to {}".format(s, self.math_fragment_stack))
        self.math_fragment_stack.append(s)        

class documentListener(MathListener):
    def __init__(self):
        super(documentListener, self).__init__()
        #debug("Initialising listener")
        self.environment_stack=[]
        self.ignore=False
        self.packages=[]
        self.document_class=None
        #self.content_stack=[]

    def enterDocument_class(self, ctx):
        self.document_class=ctx.class_prop.text

    def enterPackage_decl(self, ctx):
        #print("Enter Package with context:", ctx)
        #print("Package prop", ctx.package_prop)
        self.packages.append(ctx.package_prop.text)

#    def enterStart_environment(self, ctx):
#        print("begin", ctx.name.text)
#        self.environment_stack.append(ctx.name)
#        #        print(ctx.children)
#        #        for (i, x) in enumerate(ctx.children):
#        #            print(i, x.getText())
#        #        #self.content_stack

    def enterDocument_body(self, ctx):
        pass # print("#### Document body")

    def enterContent(self, ctx):
        pass # print("Content: {}".format(ctx.getText()))
#        if self.ignore:
#            pass
#        else:
#            print("Non-mathematical content:", ctx.getText())

 #   def enterDisplay_math(self, ctx):
 #       if not self.math_mode:
 #           pass # self.ship_math()
 #           #print("Math: {}".format(process_latex.process_sympy(ctx.m.text)))
 #       else:
 #           print("Warning attempt to invoke display math in math environment")

    def enterEnvironment(self, ctx):
        name=ctx.startname.text
        #print("Begin", name)
        self.environment_stack.append(name)
#        if name==u"align":
#            self.ignore=True
#            #print("align:", ctx, type(ctx))
#            #print(ctx.content())
#            walker = antlr4.ParseTreeWalker()
#            listener=alignListener()
#            walker.walk(listener, ctx)
#            print("**** align listener returned", listener.equations)


    def exitEnvironment(self, ctx):
        name=ctx.endname.text
        #print("End", name)
        env=self.environment_stack.pop()
        if env != name:
            print("Warning attempted to end {} environment in {} environment".format(name, env))

    def enterMath_content(self, ctx):
        #print("#### Content {} {} ####".format(type(ctx), ctx.getText()))
        if ctx.ENDLINE():
            self.ship_math()
        elif ctx.TEXT() or ctx.COMMAND():
            #print("s is:", ctx, ctx.getText())
            s=ctx.getText()
            #print("all text:", s)
            self.push_math_fragment(s)

    def enterMath_brace(self, ctx):
        self.push_math_fragment("{")
    
    def exitMath_brace(self, ctx):
        self.push_math_fragment("}")


    def enterMath_body(self, ctx):
        self.fragment_stack.append(self.math_fragment_stack)
        self.math_fragment_stack=[]

    def exitMath_body(self, ctx):
        self.ship_math()
        self.math_fragment_stack=self.fragment_stack.pop()

    def enterMath_label(self, ctx):
        self.labels.append(ctx.label_prop.text)

    def enterText_element(self, ctx):
        if self.trace:
            print("Text: {}".format(ctx.text_prop.getText()))

# Lots of tests
if __name__ == "__main__":

 #   parse(r'''\begin{align}1\end{align}''', "document_body")

#    result=parse(r'''
#\begin{align}
#13=x*4y \text{starting somewhere}\\
#13/x=4y \label{second}
#\end{align}
#
#$$\frac{x}{y}=2$$
#$$x^2 + 2y =0$$''', "document_body")
#
# 

#    s=r'''45 \\ \foo \bar XXY {a \or b}'''
#    parse(s, "document_body")

#    s=r'''
#\begin{align}
#\frac{q_{\mathit{in}}^{2}}{m_{q}} + \frac{p_{\mathit{in}}^{2}}{m_{p}} &= \frac{q_{\mathit{out}}^{2}}{m_{q}} + \frac{p_{\mathit{out}}^{2}}{m_{p}}&&\text{conservation of energy}\\
#m_{p} q_{\mathit{in}}^{2} + m_{q} p_{\mathit{in}}^{2} &= m_{p} q_{\mathit{out}}^{2} + m_{q} p_{\mathit{out}}^{2}&&\text{eliminating denominators}\\
#p_{\mathit{in}} + q_{\mathit{in}} &= p_{\mathit{out}} + q_{\mathit{out}}&&\text{conservation of momentum}\\
#q_{\mathit{out}} &= p_{\mathit{in}} - p_{\mathit{out}} + q_{\mathit{in}}&&\text{making $q_{\mathit{out}}$ the subject of the equation.}\\
#m_{p} q_{\mathit{in}}^{2} + m_{q} p_{\mathit{in}}^{2} &= m_{p} \left(p_{\mathit{in}} - p_{\mathit{out}} + q_{\mathit{in}}\right)^{2} + m_{q} p_{\mathit{out}}^{2}&&\text{substituting}
#\end{align}'''
#    #result=parse(s, "document_body")
#    #pretty_print(result)
#
    s=r'''\documentclass[a4paper]{report}
\usepackage{mathtools}
\begin{document}
\begin{align}
\frac{q_{in}^{2}}{m_{q}} + \frac{p_{in}^{2}}{m_{p}} &= \frac{q_{\mathit{out}}^{2}}{m_{q}} + \frac{p_{out}^{2}}{m_{p}}&&\text{conservation of energy}\\
m_{p} q_{in}^{2} + m_{q} p_{in}^{2} &= m_{p} q_{out}^{2} + m_{q} p_{out}^{2}&&\text{eliminating denominators}\\
p_{in} + q_{in} &= p_{out} + q_{out}&&\text{conservation of momentum}\\
q_{out} &= p_{in} - p_{out} + q_{in}&&\text{making $q_{out}$ the subject of the equation.}\\
m_{p} q_{in}^{2} + m_{q} p_{in}^{2} &= m_{p} \left(p_{in} - p_{out} + q_{in}\right)^{2} + m_{q} p_{out}^{2}&&\text{substituting}
\end{align}
\end{document}'''
    node="document"
    #import newtest
    #newtest.test_parse(DOCLexer, Parser, documentListener, s, node)
    result=parse(s, node)
    pretty_print(result)
#
#    s=r'''\begin{document}
#    \begin{align}1\end{align}
#    \end{document}'''
#    node="document_body"
#    import newtest
#    print(newtest.test_parse(DOCLexer, Parser, documentListener, s, node))
#    result=parse(s, node)
#    pretty_print(result)
#
#    s=r'''\documentclass[a4paper]{report}
#\usepackage{mathtools}
#\begin{document}
#    \begin{align}1\end{align}
#    \end{document}'''
#    node="document"
#    import newtest
#    print(newtest.test_parse(DOCLexer, Parser, documentListener, s, node, show_text=['content', 'document_body', 'packages', 'header']))
#    result=parse(s, node)
#    pretty_print(result)

#    s=r'''
#\usepackage{amsmath}
#\usepackage{mathtools}
#'''
#    node="packages"
#    import newtest
#    print(newtest.tokens(DOCLexer, s))
#    print(newtest.test_parse(DOCLexer, Parser, documentListener, s, node, show_text=['content', 'document_body', 'packages', 'header']))
#    result=parse(s, node)
#    pretty_print(result)


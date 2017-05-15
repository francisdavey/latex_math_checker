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

class Parser(DOCParser):
    def tagsMatch(self, x, y):
        return x == y


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

class MathParser(DOCListener):
    def __init__(self):
        self.maths=[]
        self.labels={}

class documentListener(MathParser):
    def __init__(self):
        super(documentListener, self).__init__()
        debug("Initialising listener")
        self.environment_stack=[]
        self.math_mode=False
        self.ignore=False
        #self.content_stack=[]

    def enterStart_env(self, ctx):
        print("begin", ctx.name.text)
        self.environment_stack.append(ctx.name)
#        print(ctx.children)
#        for (i, x) in enumerate(ctx.children):
#            print(i, x.getText())
#        #self.content_stack

    def enterContent(self, ctx):
        if self.ignore:
            pass
        else:
            print("Non-mathematical content:", ctx.getText())

    def enterDisplay_math(self, ctx):
        if not self.math_mode:
            print("Equation: {}".format(process_latex.process_sympy(ctx.m.text)))
        else:
            print("Warning attempt to invoke display math in math environment")

    def enterEnvironment(self, ctx):
        name=ctx.startname.text
        print("Begin", name)
        self.environment_stack.append(name)
        if name==u"align":
            self.ignore=True
            #print("align:", ctx, type(ctx))
            #print(ctx.content())
            walker = antlr4.ParseTreeWalker()
            walker.walk(alignListener(), ctx)


    def exitEnvironment(self, ctx):
        name=ctx.endname.text
        print("End", name)
        env=self.environment_stack.pop()
        if env != name:
            print("Warning attempted to end {} environment in {} environment".format(name, env))

class alignListener(MathParser):
    def __init__(self):
        super(alignListener, self).__init__()
        self.general_stack=[]
        self.equations=[]
        #print("Initialising alignListener")

    def ship_equation(self):
        if len(self.general_stack) > 0:
            s=' '.join(self.general_stack)
            m=process_latex.process_sympy(s)
            print("Equation: {}".format(m))
            self.equations.append(m)
            self.general_stack=[]

    def enterContent(self, ctx):
        #print("#### Content {} {} ####".format(type(ctx), ctx.getText()))
        if ctx.TEXT():
            s=ctx.getText()
            #print("all text:", s)
            self.general_stack.append(s)
        elif ctx.ENDLINE():
            self.ship_equation()

    def exitContent(self, ctx):
        self.ship_equation()

# Lots of tests
if __name__ == "__main__":

    parse(r'''
\begin{align}
13=x*4y \\
13/x=4y
\end{align}

$$1+1=2$$
$$x^2 + 2y =0$$''', "document_body")
#    parse(r"\begin{align}\end{align}", "content")
    #print(parse(r"\begin{align}\end{align}$$3+8/2$$", "content").environment_stack)

    s=r'''
\documentclass[a4paper]{report}
\usepackage{mathtools}
\begin{document}
\begin{align}
\frac{q_{in}^{2}}{m_{q}} + \frac{p_{in}^{2}}{m_{p}} &= \frac{q_{out}^{2}}{m_{q}} + \frac{p_{out}^{2}}{m_{p}}&&\text{conservation of energy}\\
m_{p} q_{in}^{2} + m_{q} p_{in}^{2} &= m_{p} q_{out}^{2} + m_{q} p_{out}^{2}&&\text{eliminating denominators}\\
p_{in} + q_{in} &= p_{out} + q_{out}&&\text{conservation of momentum}\\
q_{out} &= p_{in} - p_{out} + q_{in}&&\text{making $q_{out}$ the subject of the equation.}\\
m_{p} q_{in}^{2} + m_{q} p_{in}^{2} &= m_{p} \left(p_{in} - p_{out} + q_{in}\right)^{2} + m_{q} p_{out}^{2}&&\text{substituting}
\end{align}
\end{document}'''
 

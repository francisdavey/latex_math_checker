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

def process_doc(sympy):
    
    stream=antlr4.InputStream(sympy)
    lex = DOCLexer(stream)
    
    tokens=antlr4.CommonTokenStream(lex)
    parser=DOCParser(tokens)

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
    parser = DOCParser(stream)
    tree = getattr(parser, node)()
    #print(type(tree), tree.__dict__)
    listener = LatexListener()
    walker = antlr4.ParseTreeWalker()
    walker.walk(listener, tree)

    return listener

class LatexListener(DOCListener):
    def __init__(self):
        debug("Initialising listener")
        self.environment_stack=[]

    def enterEnvironment(self, ctx):
        print("begin", ctx, ctx.__dict__)
        self.environment_stack.push(ctx.name)

    def enterContent(self, ctx):
        print("content:", ctx.getText())

    def enterDisplay_math(self, ctx):
        print("$$", process_latex.process_sympy(ctx.m.text))

# Lots of tests
if __name__ == "__main__":

    print(parse(r"$$3+8/2$$", "content").environment_stack)

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
 

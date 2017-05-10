import sympy
import antlr4
import io
from antlr4.error.ErrorListener import ErrorListener
from antlr4 import InputStream, CommonTokenStream

from parser.DOCParser import DOCParser
from parser.DOCLexer import DOCLexer
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
        print("Initialising Latex Listener")
        self.args=[]
        self.opts=[]
        self.arg_list=[]
        self.text_stack=[]
        self.equations=[]

    def enterDocument(self, ctx):
        print("Starting to parse document")

    def exitDocument(self, ctx):
        print("Reached the end of the document")

 #   def enterDocument_class(self, ctx):
 #       print("document class")
 #       self.output.write(u"Document class:")

    def exitDocument_class(self, ctx):
        print("Document")
        print("\tClass:\t{}".format(self.args.pop()))
        print("\tOptions:\t{}".format(", ".join(self.opts)))
        self.opts=[]

    def exitPackage_decl(self, ctx):
        print("Package")
        print("\tName:\t{}".format(self.args.pop()))
        print("\tOptions:\t{}".format(", ".join(self.opts)))
        self.opts=[]

    def enterLatex_arg(self, ctx):
        pass

    def exitLatex_arg(self, ctx):
        self.args=self.arg_list
        self.arg_list=[]

    def exitLatex_opts(self, ctx):
        self.opts=self.arg_list
        self.arg_list=[]

    def enterLatex_arg_list(self, ctx):

        self.arg_list=[x.getText() for x in ctx.children]
        #print("arg list", self.arg_list)

    def enterHeader(self, ctx):
        print("start header")

    def exitHeader(self, ctx):
        print("end header")

    def enterAlign(self, ctx):
        print("Aligned equations")

    def endAlign(self, ctx):
        print("End aligned equations")

    def enterText(self, ctx):
        self.text_stack.append(ctx.getText())

    def exitText_element(self, ctx):
        if len(self.text_stack)==0:
            print("Text empty.")
        else:
            print("Text:", self.text_stack.pop())

    def enterAlign_line(self, ctx):
        print("+++line element")
        r=ctx.math().relation()
        eq=process_latex.convert_relation(r)
        if r:
            print(eq)
            self.equations.append(eq)

    def exitAlign_line(self, ctx):
        print("+++line shipped")


if __name__ == "__main__":

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
    #parse(s, "document")

    #parse("a4paper", "latex_arg_list")
    #parse("[a4paper]", "latex_opt")

#    parse(r'''m_{p} q_{in}^{2} + m_{q} p_{in}^{2} &= m_{p} q_{out}^{2} + m_{q} p_{out}^{2}&&\text{eliminating denominators}''', "align_line")


#    parse(r'''
#\frac{q_{in}^{2}}{m_{q}} + \frac{p_{in}^{2}}{m_{p}} &= \frac{q_{out}^{2}}{m_{q}} + \frac{p_{out}^{2}}{m_{p}}&&\text{conservation of energy} \\
#m_{p} q_{in}^{2} + m_{q} p_{in}^{2} &= m_{p} q_{out}^{2} + m_{q} p_{out}^{2}&&\text{eliminating denominators}''', "align_body")
##

    s='''\\documentclass[a4paper]{report}'''
    #parse(s, "document_class")
    s1='''\\usepackage{mathtools}'''
    s2='''
\\documentclass[a4paper]{report}
\\usepackage{mathtools}'''

    #print(parse(r'''ab c3 hello there Mr go''', 'text').text_stack)
    parse(r'''a&=x ^ {2}& \text{axiomatic televisulisations}''', 'align_line')
    parse(r'''a&=x ^ {2}& \text{eliminating enominators}''', 'align_line')

#    parse(r'''a &=&1 & \text{first line} \\
#b=2\\
#m_{p} q_{in}^{2} + m_{q} p_{in}^{2} &= m_{p} q_{out}^{2} + m_{q} p_{out}^{2} \text{eliminating denominators}\\
#c=3''', "align_body")

    #parse(s2, "header")
#    parse(r'''
#\documentclass[a4paper]{report}
#\usepackage{mathtools}
#\begin{document}
#\begin{align}
#4 & 5 \\
#\end{align}
#\end{document}''', "document")



# \frac{q_{in}^{2}}{m_{q}} + \frac{p_{in}^{2}}{m_{p}} &= \frac{q_{out}^{2}}{m_{q}} + \frac{p_{out}^{2}}{m_{p}}&&\text{conservation of energy}\\

    #print(''.join(x.getText() for x in a.children))
#    print(parse('\\documentclass{report}').document_class())

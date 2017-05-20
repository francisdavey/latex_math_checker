parser grammar DOC;

options {
        language=Python2;
        tokenVocab = LEX;
}

text_element: X_TEXT L_BRACE text_prop=content* R_BRACE;

latex_math: LMATHL m=math_body LMATHR;
display_math: MATH MATH m=math_body MATH MATH;
inline_math: MATH m=math_body MATH;

// testing

// math_environment:X_BEGIN L_BRACE startname=TEXT R_BRACE body=math_environment_body X_END L_BRACE endname=TEXT R_BRACE {self.isMathEnvironment($startname) and self.tagsMatch($startname, $endname)}?;
math_environment: {self.isMathEnvironment()}? X_BEGIN L_BRACE startname=TEXT R_BRACE body=math_environment_body X_END L_BRACE endname=TEXT R_BRACE;

math_brace: L_BRACE math_content* R_BRACE;
math_label: X_LABEL L_BRACE label_prop=TEXT R_BRACE;
math_content: (TEXT | COMMAND | ENDLINE | math_brace | math_label | text_element);
math_body: math_content*;
math_environment_body: math_body;


// content: (environment | display_math | inline_math | latex_math | TEXT | COMMAND | ENDLINE | L_BRACE content R_BRACE);
content: (math_environment | environment | display_math | inline_math | latex_math | TEXT | COMMAND | ENDLINE | L_BRACE content R_BRACE);

environment: X_BEGIN L_BRACE startname=TEXT R_BRACE body=environment_body {self.tagsMatch($startname, self._input.LT(3))}? X_END L_BRACE endname=TEXT R_BRACE ;

environment_body: content*;

document_body: content+;

document_class:  X_DOCUMENTCLASS (L_BRACKET TEXT R_BRACKET)? L_BRACE class_prop=TEXT R_BRACE;
package_decl: X_USEPACKAGE (L_BRACKET TEXT R_BRACKET)? L_BRACE package_prop=TEXT R_BRACE;
// package_decl: X_USEPACKAGE L_BRACE package_prop=TEXT R_BRACE;
packages: package_decl*;
header : document_class packages;

document: header document_body;


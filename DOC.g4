parser grammar DOC;

options {
        language=Python2;
        tokenVocab = LEX;
}

latex_opt: L_BRACKET TEXT R_BRACKET;
latex_arg: L_BRACE TEXT R_BRACE;
latex_cmd_predicate: latex_arg | latex_opt latex_arg;

text_element: X_TEXT L_BRACE TEXT R_BRACE;

display_math: MATH MATH m=TEXT MATH MATH;
inline_math: MATH m=TEXT MATH;

document_class:  X_DOCUMENTCLASS latex_cmd_predicate;
package_decl: X_USEPACKAGE latex_cmd_predicate;
packages: package_decl | package_decl packages;
header : document_class packages | document_class;

environment: X_BEGIN L_BRACE startname=TEXT R_BRACE body=environment_body X_END L_BRACE endname=TEXT R_BRACE {self.tagsMatch($startname, $endname)};

content: (environment | display_math | inline_math | TEXT | COMMAND | ENDLINE | L_BRACE content R_BRACE);

environment_body: content*;
document_body: content*;

document: header document_body;


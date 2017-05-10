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

start_env: X_BEGIN L_BRACE name=TEXT R_BRACE;
end_env: X_END L_BRACE name=TEXT R_BRACE;

content: (start_env | end_env | display_math | inline_math | TEXT | COMMAND | ENDLINE | L_BRACE content R_BRACE)+;

document: header content;


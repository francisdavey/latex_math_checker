parser grammar DOC;

options {
        language=Python2;
        tokenVocab = LEX;
}

latex_opt: L_BRACKET TEXT R_BRACKET;
latex_arg: L_BRACE TEXT R_BRACE;
latex_cmd_predicate: latex_arg | latex_opt latex_arg;

text_element: X_TEXT L_BRACE TEXT R_BRACE;

inline_math: MATH TEXT MATH;
display_math: DMATH TEXT DMATH;

document_class:  X_DOCUMENTCLASS latex_cmd_predicate;
package_decl: X_USEPACKAGE latex_cmd_predicate;
packages: package_decl | package_decl packages;
header : document_class packages | document_class;

start_env: X_BEGIN L_BRACE TEXT R_BRACE;
end_env: X_END L_BRACE TEXT R_BRACE;

content: start_env | end_env | TEXT | COMMAND | ENDLINE | L_BRACE content R_BRACE;

document: header content;


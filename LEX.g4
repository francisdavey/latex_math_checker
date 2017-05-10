lexer grammar LEX;

options {
        language=Python2;
}

channels { whitespace }

X_BEGIN: '\\begin';
X_END: '\\end';
X_TEXT: '\\text';
X_LABEL: '\\label';
X_DOCUMENTCLASS: '\\documentclass';
X_USEPACKAGE: '\\usepackage';

DOLLAR: '\\$';
DMATH: '$$';
MATH: '$';

L_BRACKET: '[';
R_BRACKET: ']';
L_BRACE: '{';
R_BRACE: '}';

AMPER: '&' -> skip;

ENDLINE: '\\\\';
COMMAND: '\\' [a-zA-Z]+;
TEXT: ~[\\{}]+ ;

WS: ' \n\t' -> channel(whitespace);
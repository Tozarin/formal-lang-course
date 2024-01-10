grammar Lenguage;

programm : EOL* ((COMMENT EOL+)* statement COMMENT? EOL+ (COMMENT EOL+)*)* (statement COMMENT?)? EOF;

statement :
    | VAR EQ expr
    | PRINT expr
    ;

expr :
    | VAR
    | INT
    | STRING
    | BOOL
    | REGEX
    | CFG
    | LP expr COMMA expr RP
    | expr IN expr
    | NOT expr
    | expr OR expr
    | expr AND expr
    | LT RT
    | LT expr (COMMA expr)* RT
    | LT INT DOTS INT RT
    | expr STARTING
    | expr FINAL
    | expr NODES
    | expr EDGES
    | expr MARKS
    | expr REACHABLES
    | expr MAP LP pattern ARROW expr RP
    | expr FILTER LP pattern ARROW expr RP
    | expr SETSTARTING expr
    | expr SETFINAL expr
    | expr ADDSTARTING expr
    | expr ADDFINAL expr
    | LOADDOT VAR
    | LOADDOT STRING
    | LOADGRAPH VAR
    | LOADGRAPH STRING
    | expr INTER expr
    | expr UNION expr
    | expr CONCAT expr
    | expr STAR
    | LP expr RP
    ;

pattern :
    | UNDER
    | VAR
    | LP pattern COMMA pattern RP
    ;

PRINT : 'print';

SETSTARTING : 'set_starting';
SETFINAL : 'set_final';
ADDSTARTING : 'add_starting';
ADDFINAL : 'add_final';

STARTING : 'starting';
FINAL : 'final';
REACHABLES : 'reachables';
NODES : 'nodes';
EDGES : 'edges';
MARKS : 'marks';
MAP : 'map';
FILTER : 'filter';

LOADDOT : 'load_dot';
LOADGRAPH : 'load_graph';

OR : 'or';
AND : 'and';
NOT : 'not';
IN : 'in';

INTER : 'intersect';
UNION : 'union';
CONCAT : 'concat';
STAR : '*';

EQ : ':=';
COMMA : ',';
DOTS : '..';
ARROW : '=>';
LP : '(';
RP : ')';
LT : '<|';
RT : '|>';
UNDER : '_';

STRING : '"' ~[\n]* '"';
INT : '-'? [0-9]+;
BOOL : 'true' | 'false';
REGEX : 'r' STRING;
CFG : 'g' STRING;
VAR : [a-zA-Z_][a-zA-Z0-9_]*;

EOL : '\n';

COMMENT : '$' ~[\n]* -> skip;
WS : [ \t\r] -> skip;

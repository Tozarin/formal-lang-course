grammar Lenguage;

programm : EOL* ((COMMENT EOL+)* statement COMMENT? EOL+ (COMMENT EOL+)*)* (statement COMMENT?)? EOF;

statement :
      VAR EQ expr                               # bind
    | PRINT expr                                # print
    ;

expr :
      VAR                                       # var
    | INT                                       # int
    | STRING                                    # string
    | BOOL                                      # bool
    | REGEX                                     # regex
    | CFG                                       # cfg
    | LP expr COMMA expr RP                     # pair
    | LP expr COMMA expr COMMA expr RP          # triple
    | expr IN expr                              # in
    | NOT expr                                  # not
    | expr OR expr                              # or
    | expr AND expr                             # and
    | LT (expr (COMMA expr)*)? RT               # set
    | LT INT DOTS INT RT                        # range
    | expr STARTING                             # starting
    | expr FINAL                                # final
    | expr NODES                                # nodes
    | expr EDGES                                # edges
    | expr MARKS                                # marks
    | expr REACHABLES                           # reachables
    | expr MAP LP pattern ARROW expr RP         # map
    | expr FILTER LP pattern ARROW expr RP      # filter
    | expr SETSTARTING expr                     # set_starting
    | expr SETFINAL expr                        # set_final
    | expr ADDSTARTING expr                     # add_starting
    | expr ADDFINAL expr                        # add_final
    | LOADDOT STRING                            # load_dot
    | LOADGRAPH STRING                          # load_graph
    | expr INTER expr                           # inter
    | expr UNION expr                           # union
    | expr CONCAT expr                          # concat
    | expr STAR                                 # star
    | LP expr RP                                # parents
    ;

pattern :
      UNDER                                     # any
    | VAR                                       # unvar
    | LP pattern COMMA pattern RP               # unpair
    | LP pattern COMMA pattern COMMA pattern RP # untriple
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
STAR : 'star';

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

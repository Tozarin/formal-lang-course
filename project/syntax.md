# Описание синтаксиса языка запросов к графам

## Абстрактное синтаксичекое дерево

```
programm = List<statment>

statment =
    | Bind of var * expr            // привязка значения к имени
    | Print of expr                 // print

var = name
name = string

expr =
    | Var of var                    // переменные
    | Const of const                // константы
    | Set of List<expr>             // множество
    | Not of expr                   // логическое отрицание
    | And of expr * expr            // логическое и
    | Or of expr * expr             // логическо или
    | Map of lambda * expr          // map
    | Filter of lambda * expr       // выбор элементов из множества по условию
    | LoadDor of path               // загрузка графа из окржения
    | LoadGraph of name             // загрузка графа из базы данных по имени
    | Intersect of expr * expr      // пересечения зыков
    | Concat of expr * expr         // конкатенация языков
    | Union of expr * expr          // объединение языков
    | KleeStar of expr              // звёздочка Клини
    | Contain of expr * expr        // contain
    | AddStarting of expr * expr    // добавление состояния в множество стартовых
    | AddFinal of expr * expr       // добавление состояния в множество финальных
    | SetStarting of expr * expr    // задание множества стартовых состояний
    | SetFinal of expr * expr       // задание множества финальных состояний
    | GetStarting of expr           // получение множества стартовых состояний
    | GetFinal of expr              // получение множества финальных состояний
    | GetReachable of expr          // получение всех пар достижимых вершин
    | GetVertexes of expr           // получение всех вершин
    | GetEdges of expr              // получение всех граней
    | GetMarks of expr              // получение всех меток на гранях

const =
    | Regex of regex                // регулярное выражение, заданное регулярным выражением
    | Cfg of grammar                // контекстно свободная грамматика, зданная контекстно свободной грамматикой
    | String of string              // строчка
    | Int of int                    // целое
    | Bool of bool                  // логическое значние

lambda = pattern * expr

pattern =
    | Any                           // _
    | Name of name                  // именованное значение
    | Pair of pattern * pattern     // пары
```

## Грамматика

```
programm -> EOL* (comms* statement COMMENT? EOL+ comms*)*

comms -> (COMMENT EOL+)*

statement ->
    | var ':=' expr
    | 'print' expr

expr ->
    | var
    | const
    | bool
    | graph
    | set
    | '(' expr ',' expr ')'
    | '(' expr ')'

graph ->
    | var
    | REGEX
    | CFG
    | graph 'set_starting' set
    | graph 'set_final' set
    | graph 'add_starting' set
    | graph 'add_final' set
    | 'load_dot' var
    | 'load_dot' PATH
    | 'load_graph' var
    | 'load_graph' STRING
    | graph 'intersect' graph           // пересечение
    | graph 'union' graph               // объединение
    | graph 'concat' graph              // конкатенация
    | 'star' graph                      // звёздочка Клини
    | '(' graph ')'

bool ->
    | var
    | 'true'
    | 'false'
    | expr 'in' expr                    // одно выражение содержится в другом
    | 'not' bool
    | bool 'and' bool
    | bool 'or' bool
    | '(' bool ')'

set ->
    | var
    | '<|' (expr (','  expr)*)? '|>'    // множество из указанных элементов
    | '<|' INT '..' INT '|>'            // множество из промежутка
    | graph 'starting'
    | graph 'final'
    | grapn 'nodes'
    | graph 'edges'
    | graph 'marks'
    | graph 'reachables'
    | set 'map' '(' pattern '=>' expr ')'
    | set 'filter' '(' pattern '=>' bool ')'
    | '(' set ')'

petterin ->
    | '_'
    | var
    | '(' pattern ',' pattern ')'

var -> [a-zA-Z_][a-zA-Z0-9_]*

const ->
    | STRING
    | INT

STRING -> '"' ~[\n]* '"'
INT -> '-'? [1-9][0-9]*
REGEX -> 'r' STRING
CFG -> 'g' STRING
PATH -> ('/' STRING)+

COMMENT -> '@' ~[\n]*
EOL -> [\n]+
```

## Примеры

Получение достижимых вершин
```
graph := load_graph "skos" set_starting <|0 .. 9|>

result := graph reachables map ((_, f) => f)

print result
```

Получение пар вершин, между которым существуют путь, удовлетворяющий ограничениям контекстно свободной грамматики
```
grammar := g"S -> a S b | a b"
regex := r"a b"

result := grammar intersect regex reachables map (((u, _), (v, _)) => (u, v))

print result
```

Получение множества общих меток графов
```
wine := load_graph "wine"
skos := load_graph "skos"

ms := skos marks filter (mark => mark in (wine marks))

print ms
```

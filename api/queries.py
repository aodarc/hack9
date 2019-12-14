CREATE_CALLS_TABLE = """
create table if not exists calls
(
calling bigint not null,
called bigint not null,
start timestamp not null,
duration integer not null,
rounded integer not null,
price float not null,
cost double precision not null,
in_invoice boolean default false not null,

id serial not null
    constraint calls_pk
        primary key
);

alter table calls owner to hack9;

create index if not exists calls_start_index
on calls (start);

create index if not exists calls_calling_index
on calls (calling);
"""

CREATE_INVOICE_TABLE = """
create table if not exists invoice
(
id serial not null
    constraint invoice_pk
        primary key,
calling bigint not null,
start timestamp not null,
"end" timestamp not null,
sum double precision not null,
count bigint
);

alter table invoice owner to hack9;

create index if not exists invoice_start_index
on invoice (start);

create index if not exists invoice_end_index
on invoice ("end");
"""

#######################################################
##############  ADD/EDIT QUERIES  #####################
#######################################################


ADD_CALLS_RECORD = """
INSERT INTO calls (calling, called, start, duration, rounded, price, cost) 
VALUES ($1, $2, $3, $4, $5, $6, $7)
"""

ADD_INVOICE = """
INSERT INTO invoice (calling, start, "end", "sum", "count")
VALUES ($1, $2, $3, $4, $5)
"""

#######################################################
##############  GET QUERIES  #####################
#######################################################


GET_INVOICE_RECORD_BY_ID = """
SELECT * FROM invoice WHERE ID=$1
"""

LISTING = """
SELECT * FROM calls WHERE calling = $1 AND start >= $2 AND start <= $3
"""

GET_FINANCIAL_REPORTS_SUM = """
SELECT "sum", id FROM invoice
WHERE calling=$1;
"""

GET_FINANCIAL_REPORTS_REMAINING = """
SELECT sum(cost) FROM calls
WHERE in_invoice=FALSE and calling=$1
"""

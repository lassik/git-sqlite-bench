#! /usr/bin/env python3

import os
import random
import shutil
import sqlite3
from contextlib import contextmanager
from subprocess import check_call, check_output


WORKDIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'work')
DBFILE = os.path.join(WORKDIR, 'bench.db')
DUMPFILE = os.path.join(WORKDIR, 'bench.sql')


@contextmanager
def database():
    db = sqlite3.connect(DBFILE)
    yield db
    db.close()


def dump_db_into_git(msg):
    open(DUMPFILE, "wb").write(check_output(["sqlite3", DBFILE, ".dump"]))
    check_call(["git", "add", DUMPFILE])
    check_call(["git", "commit", "-m", msg])


def randval():
    return str(random.randrange(0, 2**24))


def create_table(t, nfield):
    return "create table table{} ({})".format(
        t, ",".join(["key integer primary key"] +
                    ["field{} integer".format(f)
                     for f in range(nfield)]))


def random_insert(table, nfield):
    return 'insert into table{} ({}) values ({})'.format(
        table,
        ",".join("field{}".format(f) for f in range(nfield)),
        ",".join([randval() for _ in range(nfield)]))


def random_update(table, nfield, nrow):
    fields = list(sorted(random.sample(range(nfield), 3)))
    return 'update table{} set {} where key={}'.format(
        table,
        ",".join('field{}={}'.format(f, randval())
                 for f in fields),
        random.randrange(nrow))


def bench(ntable, nfield, nop):
    nrow = {t: 0 for t in range(ntable)}
    if os.path.isdir(WORKDIR):
        shutil.rmtree(WORKDIR)
    os.mkdir(WORKDIR)
    os.chdir(WORKDIR)
    check_call(["git", "init"])
    with database() as db:
        cur = db.cursor()
        for t in range(ntable):
            cur.execute(create_table(t, nfield))
    dump_db_into_git("Commit empty database")
    for o in range(nop):
        t = random.randrange(ntable)
        op = random.choice(['insert', 'update']) \
             if nrow[t] else 'insert'
        opmsg = "Operation #{}: {} table #{}".format(o, op, t)
        print(opmsg)
        with database() as db:
            cur = db.cursor()
            if op == 'insert':
                cur.execute(random_insert(t, nfield))
                nrow[t] += 1
            elif op == 'update':
                cur.execute(random_update(t, nfield, nrow[t]))
            db.commit()
        dump_db_into_git(opmsg)


if __name__ == "__main__":
    bench(2, 10, 1000)

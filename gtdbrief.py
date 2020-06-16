#!/usr/bin/env python3

import logging
import argparse
from datetime import date, datetime, timedelta
import jinja2
import os
import re
from pybear import bear
from gtdclasses import Conventions, GtdNote, GtdList
from dataclasses import dataclass, field
from typing import List, Iterable, Dict, Set, Tuple,\
                   Optional, Callable


# --- args parsing ---
parser = argparse.ArgumentParser()
parser.add_argument("beardb", nargs='?', default="/notes/database.sqlite",
                    help="Bear.app SQLite DB file")
parser.add_argument("-v", "--verbosity", action='count', default=0,
                    help="increase output verbosity")
parser.add_argument("-D", "--output-dir", default="output",
                    help="name of the output directory")
parser.add_argument("-d", "--date",
                    help="Specify date (YYYY-MM-DD) for which to generate brief (default: today)")

parser.add_argument("--upcoming", default=7, type=int,
                    help="Number of days to include for upcoming tasks")

args = parser.parse_args()

# NOTE: Do not use logging above this line!
if args.verbosity == 1:
    loglevel = logging.INFO
elif args.verbosity >= 2:
    loglevel = logging.DEBUG
else:
    loglevel = logging.WARNING

logging.basicConfig(
    level=loglevel,
    format='%(message)s'
    )

day = date.today()
if args.date is not None:
    day = datetime.strptime (args.date, '%Y-%m-%d').date()
logging.info (f"target day: {day}")

upcoming_days = timedelta(days=(args.upcoming))

@dataclass
class GtdBrief:
    timestamp : datetime # when generated
    date : datetime # target date
    # Nexts, Somedays, etc 
    lists: List[GtdList] = field(default_factory=list) 

brief = GtdBrief (date=day, timestamp=datetime.now())

b = bear.Bear(path=args.beardb)
notes_all = [ GtdNote(bnote) for bnote in \
                b.tag_by_title (Conventions.gtd_prefix).notes()]

brief.lists.append (GtdList ("Nexts", from_list=notes_all,
            where=lambda n: n.is_tagged(Conventions.gtd_nexts),
            ctxs_func=lambda c: re.match (r"^(\d\d)-(\w)", c))
        )

brief.lists.append (GtdList ("Meetings", from_list=notes_all,
            where=lambda n: n.is_tagged(Conventions.gtd_meetings),
            ctxs_func=lambda c: re.match (f"^{Conventions.gtd_meetings.rsplit('/',1)}", c))
            )

brief.lists.append (GtdList ("Shopping", from_list=notes_all,
            where=lambda n: n.is_tagged(Conventions.gtd_shopping) and
                (n.is_tagged(Conventions.gtd_nexts) or \
                    n.is_tagged(Conventions.gtd_somedays)),
            ctxs_func=lambda c: re.match (f"^{Conventions.gtd_shopping.rsplit('/',1)}", c))
            )

brief.lists.append (GtdList ("Waitingons", from_list=notes_all,
            where=lambda n: n.is_tagged(Conventions.gtd_waitingons))
            )

brief.lists.append (GtdList ("Somedays", from_list=notes_all,
            where=lambda n: n.is_tagged(Conventions.gtd_somedays) and 
                not (n.is_tagged(Conventions.gtd_projects)),
            ctxs_func=lambda c: not (
                re.match (f"^{Conventions.gtd_shopping.rsplit('/',1)}", c) or
                re.match (f"^{Conventions.gtd_meetings.rsplit('/',1)}", c)
                )
            ))

brief.lists.append (GtdList ("Projects by ctx", from_list=notes_all,
            where=lambda n: n.is_tagged(Conventions.gtd_projects))
            )

# This Projects list is special, since it's not to be displayed by ctx
brief.projects  = GtdList ("Projects by prj", from_list=notes_all,
            where=lambda n: n.is_tagged(Conventions.gtd_projects)
            )
# The upcoming list is also special, as it is presented by due date
brief.upcoming = GtdList ("Upcoming", from_list=notes_all,
            where=lambda n: (n.is_timestamped() and
                    timedelta(0) <= n.due_date - day and
                    n.due_date - day <= upcoming_days))
                    
# Also check if there are any deferred tasks without a specific due date?
brief.deferred_nodue = GtdList ("Deferred (w/o due)", from_list=notes_all,
            where=lambda n: (n.is_tagged(Conventions.gtd_deferred) and
                                not n.is_timestamped()))

# --- Jinja2 templates and document generation
from jinja2_markdown import *
from jinja2_latex import *
templates = {
    'markdown': {
        'template': markdown_jinja_env.get_template('templates/gtd.md'),
        'filename': f"gtd-{day.year}-{day.month:02}-{day.day:02}.md"
    },
    'latex_a4': {
        'template': latex_jinja_env.get_template('templates/gtd-a4.tex'),
        'filename': f"gtd-{day.year}-{day.month:02}-{day.day:02}-a4.tex"
    }
}

# -- Generate documents for all formats
for format in templates.keys():
    logging.info (f"-> generating agenda using {format} template:")
    template = templates[format]['template']
    document = template.render(data=brief)
    try:
        os.makedirs (args.output_dir)
    except FileExistsError:
        pass

    with open (args.output_dir + '/' + templates[format]['filename'], "w") as f:
        f.write (document)

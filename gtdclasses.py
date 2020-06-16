from typing import List, Iterable, Dict, Set, Tuple,\
                   Optional, Callable
from datetime import date, datetime, timedelta
from pybear import bear
from conventions import Conventions
import pytest
import re
import logging

class GtdNote:
    def __init__ (self, bnote: bear.Note):
        assert self.is_gtd_note(bnote)
        self.bnote = bnote

    @property
    def uuid(self):
        return self.bnote.id

    @property
    def title(self):
        if self.bnote.title is not None:
            if self.prjs:
                return f"{self.prjs[0]}: {self.bnote.title}"
            else:
                return self.bnote.title
        else:
            return self.bnote.id
    
    @staticmethod
    def normalize_tag (tag: str) -> str:
        comps = tag.split (sep='/')
        normalized_tag = "" # tags do _not_ start with a leading '/' in Bear!
        for c in comps:
            if c:
                normalized_tag += c + '/'
        return normalized_tag.rstrip('/')
    
    @property
    def tags (self) -> List[str]:
        return [self.normalize_tag(t.title) for t in self.bnote.specific_tags()]
    
    def is_tagged(self, tag: str) -> bool:
        return any (t.startswith (tag) for t in self.tags)
    
    @staticmethod
    def is_gtd_note(bnote: bear.Note):
        # if bnote.tags is None:
        #     return False
        return any (t.title.startswith (Conventions.gtd_prefix)
                    for t in bnote.tags())

    def is_timestamped (self):
        return len(self.dates) > 0

    @property
    def dates (self) -> List[date]:
        dates = []
        for tag in self.tags:
            d = Conventions.tag_to_date(tag)
            if d:
                dates.append(d)
        return dates 

    @property
    def latest_date (self) -> date:
        return max (self.dates)

    @property
    def due_date (self) -> date:
        if not self.is_timestamped():
            return None
        return max (self.dates)

    def is_overdue(self, target_date: datetime):
        return self.is_timestamped() and self.due_date <= target_date

    @property
    def ctxs (self) -> List[str]:
        ctxs = [t[len(Conventions.gtd_ctx):].strip('/') \
                for t in self.tags \
                if t.startswith(Conventions.gtd_ctx)]
        if len (ctxs) == 0:
            ctxs = [Conventions.gtd_noctx_tag]
        return ctxs
    
    @property
    def prjs (self) -> List[str]:
        return [t[len(Conventions.gtd_projects):].strip('/') \
                for t in self.tags \
                if t.startswith(Conventions.gtd_projects)]

class MockupBearNote (bear.Note):
    '''
    A mockup class pretending a Bear.Note. For testing.
    '''
    def __init__ (self, *, tags: List[str], title: str = "test note"):
        self.id = hash(title)
        self.title = title
        self.mockup_tags = [
                bear.Tag(bear=None, id=None, title=t) \
                for t in tags]
    
    def tags(self):
        return self.mockup_tags

class TestGtdNote:
    
    def test_tags(self):
        note = GtdNote(MockupBearNote (
                tags=[
                    Conventions.gtd_nexts,
                    "tag1", "tag1/subtag1", "tag2", "tag3//subb"
                ]))
        assert  sorted(note.tags) == \
                sorted([Conventions.gtd_nexts,
                        "tag1/subtag1", "tag2", "tag3/subb"])
        
    def test_tags_gtd(self):
        note =  GtdNote(MockupBearNote (
            tags=[
            Conventions.gtd_nexts,
            ]))
        
        assert not note.is_timestamped()
        assert note.is_tagged(Conventions.gtd_nexts)
        assert not note.is_tagged(Conventions.gtd_projects)

    def test_timestamps(self):

        today = datetime.strptime ("2020-02-29", '%Y-%m-%d').date()

        past_days = [
            today - timedelta (days=7),
            today - timedelta (days=366),
            today - timedelta (days=1),           
        ]

        future_days = [
            today + timedelta (days=1),
            today + timedelta (days=7),
            today + timedelta (days=366),
        ]

        test_dates = past_days + future_days + [today]
        
        note =  GtdNote(MockupBearNote (
            tags=[Conventions.gtd_nexts] +
                 [Conventions.tag_date (d) for d in test_dates]
            ))

        assert note.is_timestamped()
        assert len(note.tags) == 1 + len(test_dates)
        assert sorted(note.dates) == sorted(test_dates)
        assert note.latest_date == max(test_dates)
        assert note.due_date == today + timedelta (days=366)
        assert note.is_overdue (target_date=max(future_days))

    def test_ctxs_prjs(self):
        note =  GtdNote(MockupBearNote (
            tags=[
                Conventions.gtd_nexts,
                ]))
        assert sorted(note.ctxs) == [Conventions.gtd_noctx_tag]
        assert sorted(note.prjs) == []

        note =  GtdNote(MockupBearNote (
            tags=[
                Conventions.gtd_nexts,
                Conventions.gtd_ctx + "/10-comp",
                Conventions.gtd_ctx + "/30-errand",
                ]
            ))
        assert sorted(note.ctxs) == ["10-comp", "30-errand"]

        note =  GtdNote(MockupBearNote (
            tags=[
                Conventions.gtd_nexts,
                Conventions.gtd_projects + "/prj1",
                Conventions.gtd_projects + "/prj2/subproj22",
                ]
            ))
        assert sorted(note.prjs) == ["prj1", "prj2/subproj22"]


class GtdList:
    '''A GTD list, such as Nexts, Waiting ons, Somedays, projects
    '''
    def __init__ (self, name: str, from_list: Iterable[GtdNote] = None, 
                    where: Callable [[GtdNote], bool] = None,
                    ctxs_func: Callable [[str], bool] = None,
                    ):
        logging.info (f"-> creating list {name}...")
        self.title = name
        self.by_ctx = {}
        self.by_prj = {}
        no_of_notes = 0

        if from_list is None:
            # A dummy empty list for making blank pages in brief documents
            return

        for n in from_list:
            if where (n):
                for c in n.ctxs:
                    if ctxs_func is None or ctxs_func(c):
                        if c not in self.by_ctx.keys():
                            self.by_ctx[c] = []
                        self.by_ctx[c].append (n)
                    no_of_notes += 1

                for p in n.prjs:
                    if p not in self.by_prj.keys():
                        self.by_prj[p] = []
                    self.by_prj[p].append (n)
                    no_of_notes += 1

        logging.info (f"`-> {no_of_notes} notes added ("
                      f"{len(self.by_ctx)} ctxs, "
                      f"{len(self.by_prj)} projects)")

    @property
    def ctxs(self):
        return sorted(self.by_ctx.keys())

    @property
    def prjs(self):
        return sorted(self.by_prj.keys())

    @property
    def list(self):
        uniqe_list = []
        for nlist in self.by_ctx.values():
            for n in nlist:
                if n not in uniqe_list:
                    uniqe_list.append(n)
                    yield n
    @property
    def nitems(self):
        return len(list(self.list))

class TestGtdList:
    @pytest.fixture
    def create_test_list(self):
        self.notes = [
            GtdNote(MockupBearNote (
                title="Apples",
                tags=[
                    Conventions.gtd_nexts,
                    Conventions.gtd_ctx + "/30-errand",
                    Conventions.gtd_ctx + "/shops/Warzywniak"
                ])),
            GtdNote(MockupBearNote (
                title="Write tests",
                tags=[
                    Conventions.gtd_nexts,
                    Conventions.gtd_ctx + "/20-comp/programming",
                    Conventions.gtd_projects + "gtdbrief",
                ])),
            ]
    
    def test_nexts (self, create_test_list):
        list = GtdList (name="test list",
            from_list=self.notes,
            where=lambda n: n.is_tagged(Conventions.gtd_nexts)
            )
        assert sorted(list.ctxs) == sorted([
                                "20-comp/programming",
                                "30-errand",
                                "shops/Warzywniak"
                                ])
        assert sorted(list.prjs) == sorted([
                                "gtdbrief",
                                ])

        assert sorted((n.title for n in list.list)) == \
                    sorted(["Apples", "gtdbrief: Write tests"])
        
        
    def test_ctxs (self, create_test_list):
        list = GtdList (name="test list",
            from_list=self.notes,
            where=lambda n: n.is_tagged(Conventions.gtd_nexts),
            ctxs_func=lambda c: re.match (r"^(\d\d)-(\w)", c)
            )
        assert sorted(list.ctxs) == sorted([
                                "20-comp/programming",
                                "30-errand",
                                ])

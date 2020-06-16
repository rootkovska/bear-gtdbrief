from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
from datetime import date, datetime, timedelta
import re

class Conventions:
    '''
    Tagging conventions as implemented by one's notebook
    '''
    gtd_prefix = "gtd"
    gtd_ctx = f"{gtd_prefix}/ctx"
    gtd_noctx_tag = '99-noctx'
    gtd_nexts = f"{gtd_prefix}/nexts"
    gtd_somedays = f"{gtd_prefix}/someday"
    gtd_deferred = f"{gtd_prefix}/deferred"
    gtd_waitingons = f"{gtd_prefix}/waiting"
    gtd_projects = f"{gtd_prefix}/projects"
    gtd_meetings = f"{gtd_ctx}/meetings"
    gtd_shopping = f"{gtd_ctx}/shops"

    gtd_timeline_prefix = "t"
    gtd_recurring_prefix = "r"

    @staticmethod
    def tag_date (day):
        return f"{Conventions.gtd_timeline_prefix}/" + \
               f"{day.year}/{day.month:02}/{day.day:02}"

    @staticmethod
    def tag_monthly (day):
        return f"{Conventions.gtd_recurring_prefix}/" + \
               f"monthly/{day.day:02}"
     
    @staticmethod
    def tag_yearly (day):
        return f"{Conventions.gtd_recurring_prefix}/" + \
               f"yearly/{day.year}/{day.month:02}"

    @staticmethod
    def tag_to_date (tag: str) -> date:
        match_regexp = f"^{Conventions.gtd_timeline_prefix}/" + \
                        r"(\d\d\d\d)/(\d\d)/(\d\d)"
        m = re.match (match_regexp, tag)
        if m and len(m.groups()) == 3: 
            # year, month, day -> 3 groups matched?
            year = int (m.group(1))
            month = int (m.group(2))
            day = int (m.group(3))
            try:
                return date (year, month, day)
            except ValueError:
                raise ValueError
        else:
            return None

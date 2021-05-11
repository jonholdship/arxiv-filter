import os
import time
import re
from datetime import datetime 
from pytz import timezone
import requests
import arxiv
import smtplib
from config import *

class Query(object):
    def __init__(self, query):
        # self.date = datetime(*query['updated_parsed'][:6], tzinfo=timezone('GMT'))
        self.title = query.title
        self.date = query.updated
        self.url =query.entry_id
        self.abstract=query.summary
        self.date_str = query.published
        self.id = 'v'.join(query.entry_id.split('v')[:-1])
        #self.categories = [tag['term'] for tag in query.tags]

    @property
    def is_recent(self):
        curr_time = datetime.now(timezone('GMT'))
        delta_time = curr_time - self.date
        assert delta_time.total_seconds() > 0
        return delta_time.days < 8

    def __hash__(self):
        return self.id

    def __str__(self):
        s = f"{self.title}\n{self.url}\n{self.date.ctime()} GMT\n"
        s += f"\n{self.abstract}\n"
        return s

class ArxivFilter(object):
    def __init__(self, categories, keywords):
        self._categories = categories
        self._keywords = keywords

    @property
    def _previous_arxivs_fname(self):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'previous_arxivs.txt')
        
    def _get_previously_sent_arxivs(self):
        if os.path.exists(self._previous_arxivs_fname):
            with open(self._previous_arxivs_fname, 'r') as f:
                return set(f.read().split('\n'))
        else:
            return set()

    def _save_previously_sent_arxivs(self, new_queries):
        prev_arxivs = list(self._get_previously_sent_arxivs())
        prev_arxivs += [q.id for q in new_queries]
        prev_arxivs = list(set(prev_arxivs))
        with open(self._previous_arxivs_fname, 'w') as f:
            f.write('\n'.join(prev_arxivs))
        
    def _get_queries_from_last_day(self, max_results=100):
        queries = []

        # get all queries in the categories in the last day
        for category in self._categories:
            num_category_added = 0
            new_queries = [Query(q) for q in arxiv.Search(query=category, sort_by=arxiv.SortCriterion.SubmittedDate, max_results=max_results).get()]
            num_category_added += len(new_queries)
            queries += [q for q in new_queries if q.is_recent]

        # get rid of duplicates
        queries_dict = {q.id: q for q in queries}
        unique_keys = set(queries_dict.keys())
        queries = [queries_dict[k] for k in unique_keys]

        # only keep queries that contain keywords
        queries = [q for q in queries if max([k.lower() in str(q).lower() for k in self._keywords])]

        # sort from most recent to least
        queries = sorted(queries, key=lambda q: (datetime.now(timezone('GMT')) - q.date).total_seconds())

        # filter if previously sent
        prev_arxivs = self._get_previously_sent_arxivs()
        queries = [q for q in queries if q.id not in prev_arxivs]
        self._save_previously_sent_arxivs(queries)
        
        return queries

    def _send_email(self, txt):
        message = 'Subject: {}\n\n{}'.format(SUBJECT, txt)
        server = smtplib.SMTP(SERVER)
        server.set_debuglevel(3)
        server.sendmail(FROM, TO, message)
        server.quit()

    def run(self):
        queries = self._get_queries_from_last_day()
        queries_str = '\n-----------------------------\n'.join([str(q) for q in queries])
        for keyword in self._keywords:
            queries_str_insensitive = re.compile(re.escape(keyword), re.IGNORECASE)
            queries_str = queries_str_insensitive.sub('**' + keyword + '**', queries_str)
        queries_str = 'Categories: ' + ', '.join(self._categories) + '\n' + \
                      'Keywords: ' + ', '.join(self._keywords) + '\n\n' + \
                      '\n-----------------------------\n' + \
                      queries_str
        self._send_email(queries_str)

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(FILE_DIR, 'categories.txt'), 'r') as f:
    categories = [line.strip() for line in f.read().split('\n') if len(line.strip()) > 0]

with open(os.path.join(FILE_DIR, 'keywords.txt'), 'r') as f:
    keywords = [line.strip() for line in f.read().split('\n') if len(line.strip()) > 0]


af = ArxivFilter(categories=categories,
                 keywords=keywords)
af.run()



